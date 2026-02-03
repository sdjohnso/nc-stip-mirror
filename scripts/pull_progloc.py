#!/usr/bin/env python3
"""
NCDOT ProgLoc Data Pull Script

Downloads the Progress Location (ProgLoc) Excel export containing
construction contract progress reports. Parses into structured JSON
for integration with STIP project files.

Output:
  - raw/progloc/progress_reports.xlsx  (original Excel from NCDOT)
  - raw/progloc/progress_reports.json  (parsed and structured)
  - raw/progloc/last_pull.json         (metadata with timestamps)
"""

import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

# Add scripts directory to path for config import
sys.path.insert(0, str(Path(__file__).parent))
from config import PROGLOC_EXPORT, REQUEST_DELAY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Output paths
RAW_DIR = Path(__file__).parent.parent / "raw" / "progloc"
EXCEL_OUTPUT = RAW_DIR / "progress_reports.xlsx"
JSON_OUTPUT = RAW_DIR / "progress_reports.json"
METADATA_OUTPUT = RAW_DIR / "last_pull.json"

# Retry configuration
MAX_RETRIES = 3
INITIAL_BACKOFF = 2
REQUEST_TIMEOUT = 120  # Excel download can be slow


def download_excel() -> bytes:
    """
    Download the ProgLoc Excel export from NCDOT.

    Returns:
        Raw bytes of the Excel file

    Raises:
        RuntimeError: If download fails after all retries
    """
    logger.info(f"Downloading ProgLoc Excel from: {PROGLOC_EXPORT}")

    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(PROGLOC_EXPORT, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            # Verify we got actual content
            content_length = len(response.content)
            if content_length < 1000:
                raise RuntimeError(f"Response too small ({content_length} bytes) - possible error page")

            logger.info(f"Downloaded {content_length:,} bytes")
            return response.content

        except (requests.RequestException, RuntimeError) as e:
            last_error = e
            if attempt < MAX_RETRIES - 1:
                backoff = INITIAL_BACKOFF * (2 ** attempt)
                logger.warning(f"Download failed: {e}. Retrying in {backoff}s...")
                time.sleep(backoff)
            else:
                raise RuntimeError(f"Failed to download ProgLoc after {MAX_RETRIES} attempts: {last_error}")


def parse_excel(excel_path: Path) -> list[dict]:
    """
    Parse the ProgLoc Excel file into structured records.

    Args:
        excel_path: Path to the downloaded Excel file

    Returns:
        List of contract dictionaries
    """
    logger.info(f"Parsing Excel: {excel_path}")

    # Read Excel - headers are in first row of data
    df = pd.read_excel(excel_path, engine='openpyxl', header=0)

    # The actual headers are in row 0, set them properly
    new_headers = df.iloc[0].tolist()
    df = df.iloc[1:].copy()
    df.columns = new_headers
    df = df.reset_index(drop=True)

    logger.info(f"Found {len(df)} contract records with {len(df.columns)} columns")

    # Convert to list of dicts with proper types
    contracts = []
    for _, row in df.iterrows():
        contract = {}
        for col in df.columns:
            val = row[col]

            # Handle NaN/None
            if pd.isna(val):
                contract[col] = None
            # Handle datetime
            elif isinstance(val, pd.Timestamp):
                contract[col] = val.isoformat()
            # Handle floats that are really ints (like division number)
            elif isinstance(val, float) and val.is_integer():
                contract[col] = int(val)
            else:
                contract[col] = val

        contracts.append(contract)

    return contracts


def build_tip_index(contracts: list[dict]) -> dict:
    """
    Build an index mapping TIP numbers to contract records.

    Handles multiple TIPs per contract (e.g., "U-2519BA, U-2519BB")

    Args:
        contracts: List of contract dictionaries

    Returns:
        Dict mapping TIP numbers to list of matching contracts
    """
    tip_index = {}

    for contract in contracts:
        tip_field = contract.get("TIP#")
        if not tip_field:
            continue

        # Split multiple TIPs (comma or space separated)
        tip_str = str(tip_field).strip()
        tips = [t.strip() for t in tip_str.replace(",", " ").split() if t.strip()]

        for tip in tips:
            if tip not in tip_index:
                tip_index[tip] = []
            tip_index[tip].append(contract)

    return tip_index


def main():
    """Pull ProgLoc data and save to files."""
    start_time = datetime.now(timezone.utc)
    logger.info("=" * 60)
    logger.info("NCDOT ProgLoc Data Pull Started")
    logger.info("=" * 60)

    # Ensure output directory exists
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    try:
        # Download Excel
        excel_bytes = download_excel()

        # Save raw Excel
        with open(EXCEL_OUTPUT, "wb") as f:
            f.write(excel_bytes)
        logger.info(f"Saved: {EXCEL_OUTPUT}")

        # Parse Excel
        contracts = parse_excel(EXCEL_OUTPUT)

    except Exception as e:
        logger.error(f"Pull failed: {e}")
        logger.error("Existing data files will NOT be overwritten")
        sys.exit(1)

    # Validate we got data
    if not contracts:
        logger.error("No contracts found in Excel - possible format change")
        logger.error("Existing data files will NOT be overwritten")
        sys.exit(1)

    # Build TIP index
    tip_index = build_tip_index(contracts)
    contracts_with_tip = len([c for c in contracts if c.get("TIP#")])

    # Save JSON output
    end_time = datetime.now(timezone.utc)

    output_data = {
        "source": "NCDOT ProgLoc (Construction Progress Report)",
        "source_url": PROGLOC_EXPORT,
        "pull_timestamp": start_time.isoformat(),
        "total_contracts": len(contracts),
        "contracts_with_tip": contracts_with_tip,
        "unique_tips": len(tip_index),
        "contracts": contracts,
        "tip_index": tip_index,
    }

    with open(JSON_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)
    logger.info(f"Saved: {JSON_OUTPUT}")

    # Save metadata
    metadata = {
        "last_pull_started": start_time.isoformat(),
        "last_pull_completed": end_time.isoformat(),
        "duration_seconds": (end_time - start_time).total_seconds(),
        "total_contracts": len(contracts),
        "contracts_with_tip": contracts_with_tip,
        "unique_tips": len(tip_index),
        "excel_size_bytes": EXCEL_OUTPUT.stat().st_size,
        "status": "success",
    }

    with open(METADATA_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Saved: {METADATA_OUTPUT}")

    # Summary
    logger.info("=" * 60)
    logger.info("Pull Complete!")
    logger.info(f"  Total contracts: {len(contracts)}")
    logger.info(f"  With TIP#: {contracts_with_tip}")
    logger.info(f"  Unique TIPs: {len(tip_index)}")
    logger.info(f"  Duration: {metadata['duration_seconds']:.1f} seconds")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
