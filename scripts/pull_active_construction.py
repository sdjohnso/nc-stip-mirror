#!/usr/bin/env python3
"""
NCDOT Active Construction Data Pull Script

Pulls all active construction project data from NCDOT's ArcGIS REST API.
This data comes from HiCAMS and is updated nightly.

Layers pulled:
  - Layer 0: Point features (construction project locations)
  - Layer 1: Line features (construction project routes)
  - Layer 3: HiCAMS attributes table (detailed contract/project info)

Output:
  - raw/active-construction/construction_points.json
  - raw/active-construction/construction_lines.json
  - raw/active-construction/construction_table.json  (HiCAMS attributes)
  - raw/active-construction/last_pull.json
"""

import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

# Add scripts directory to path for config import
sys.path.insert(0, str(Path(__file__).parent))
from config import (
    CONSTRUCTION_POINTS,
    CONSTRUCTION_LINES,
    CONSTRUCTION_TABLE,
    DEFAULT_OUT_SR,
    MAX_RECORD_COUNT,
    REQUEST_DELAY,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Output paths
RAW_DIR = Path(__file__).parent.parent / "raw" / "active-construction"
POINTS_OUTPUT = RAW_DIR / "construction_points.json"
LINES_OUTPUT = RAW_DIR / "construction_lines.json"
TABLE_OUTPUT = RAW_DIR / "construction_table.json"
METADATA_OUTPUT = RAW_DIR / "last_pull.json"

# Retry configuration
MAX_RETRIES = 3
INITIAL_BACKOFF = 2  # seconds


def query_layer(layer_url: str, layer_name: str, is_table: bool = False) -> list[dict]:
    """
    Query all features from an ArcGIS layer or table with pagination.

    Args:
        layer_url: Base URL for the layer (without /query)
        layer_name: Human-readable name for logging
        is_table: If True, this is a non-spatial table (no geometry)

    Returns:
        List of all feature dictionaries

    Raises:
        RuntimeError: If query fails after all retries
    """
    all_features = []
    offset = 0
    query_url = f"{layer_url}/query"

    logger.info(f"Starting pull for {layer_name}")

    while True:
        params = {
            "where": "1=1",  # All records
            "outFields": "*",
            "f": "json",
            "resultOffset": offset,
            "resultRecordCount": MAX_RECORD_COUNT,
        }

        # Only request spatial reference for layers with geometry
        if not is_table:
            params["outSR"] = DEFAULT_OUT_SR

        # Attempt query with retries
        response_data = None
        last_error = None

        for attempt in range(MAX_RETRIES):
            try:
                logger.debug(f"Query offset={offset}, attempt {attempt + 1}/{MAX_RETRIES}")
                response = requests.get(query_url, params=params, timeout=60)
                response.raise_for_status()
                response_data = response.json()

                # Check for ArcGIS error response
                if "error" in response_data:
                    error_msg = response_data["error"].get("message", "Unknown API error")
                    raise RuntimeError(f"API error: {error_msg}")

                break  # Success

            except (requests.RequestException, RuntimeError) as e:
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    backoff = INITIAL_BACKOFF * (2 ** attempt)
                    logger.warning(f"Request failed: {e}. Retrying in {backoff}s...")
                    time.sleep(backoff)
                else:
                    logger.error(f"All {MAX_RETRIES} retries failed for {layer_name}")
                    raise RuntimeError(f"Failed to query {layer_name} after {MAX_RETRIES} attempts: {last_error}")

        # Extract features
        features = response_data.get("features", [])
        all_features.extend(features)

        batch_count = len(features)
        logger.info(f"  Retrieved {batch_count} features (total: {len(all_features)}, offset: {offset})")

        # Check if we've retrieved all records
        exceeded_limit = response_data.get("exceededTransferLimit", False)

        if batch_count < MAX_RECORD_COUNT and not exceeded_limit:
            logger.info(f"Completed {layer_name}: {len(all_features)} total features")
            break

        # Prepare for next batch
        offset += MAX_RECORD_COUNT
        time.sleep(REQUEST_DELAY)

    return all_features


def save_json(data: dict | list, output_path: Path) -> None:
    """Save data to JSON file with proper formatting."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved: {output_path}")


def main():
    """Pull all active construction data and save to files."""
    start_time = datetime.now(timezone.utc)
    logger.info("=" * 60)
    logger.info("NCDOT Active Construction Data Pull Started")
    logger.info("=" * 60)

    try:
        # Pull all three layers/tables
        points_features = query_layer(CONSTRUCTION_POINTS, "Construction Points (Layer 0)")
        time.sleep(REQUEST_DELAY)

        lines_features = query_layer(CONSTRUCTION_LINES, "Construction Lines (Layer 1)")
        time.sleep(REQUEST_DELAY)

        # Layer 3 is a table (non-spatial HiCAMS attributes)
        table_features = query_layer(CONSTRUCTION_TABLE, "HiCAMS Table (Layer 3)", is_table=True)

    except RuntimeError as e:
        logger.error(f"Pull failed: {e}")
        logger.error("Existing data files will NOT be overwritten")
        sys.exit(1)

    # Validate we got data (sanity check)
    if not points_features and not lines_features and not table_features:
        logger.error("All layers returned 0 features - possible API issue")
        logger.error("Existing data files will NOT be overwritten")
        sys.exit(1)

    # Save the raw feature lists with metadata
    end_time = datetime.now(timezone.utc)

    points_output = {
        "layer": "Active Construction Points (Layer 0)",
        "source_url": CONSTRUCTION_POINTS,
        "pull_timestamp": start_time.isoformat(),
        "feature_count": len(points_features),
        "features": points_features,
    }

    lines_output = {
        "layer": "Active Construction Lines (Layer 1)",
        "source_url": CONSTRUCTION_LINES,
        "pull_timestamp": start_time.isoformat(),
        "feature_count": len(lines_features),
        "features": lines_features,
    }

    table_output = {
        "layer": "HiCAMS Attributes Table (Layer 3)",
        "source_url": CONSTRUCTION_TABLE,
        "pull_timestamp": start_time.isoformat(),
        "feature_count": len(table_features),
        "features": table_features,
    }

    save_json(points_output, POINTS_OUTPUT)
    save_json(lines_output, LINES_OUTPUT)
    save_json(table_output, TABLE_OUTPUT)

    # Save metadata
    metadata = {
        "last_pull_started": start_time.isoformat(),
        "last_pull_completed": end_time.isoformat(),
        "duration_seconds": (end_time - start_time).total_seconds(),
        "points_count": len(points_features),
        "lines_count": len(lines_features),
        "table_count": len(table_features),
        "total_features": len(points_features) + len(lines_features) + len(table_features),
        "status": "success",
    }
    save_json(metadata, METADATA_OUTPUT)

    # Summary
    logger.info("=" * 60)
    logger.info("Pull Complete!")
    logger.info(f"  Points: {len(points_features)}")
    logger.info(f"  Lines:  {len(lines_features)}")
    logger.info(f"  Table:  {len(table_features)} (HiCAMS attributes)")
    logger.info(f"  Total:  {metadata['total_features']}")
    logger.info(f"  Duration: {metadata['duration_seconds']:.1f} seconds")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
