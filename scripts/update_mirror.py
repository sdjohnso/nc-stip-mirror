#!/usr/bin/env python3
"""
NCDOT STIP Mirror Orchestrator

Main entry point for updating the mirror. Coordinates calling appropriate
pull scripts based on update type, then regenerates markdown files and indexes.

Update Types:
  - daily:   Active construction only (HiCAMS updates nightly)
  - weekly:  STIP + ProgLoc + construction
  - monthly: All data (future: AADT and project URLs)
  - full:    Everything, used for initial population or recovery

Usage:
  python update_mirror.py [daily|weekly|monthly|full]
  python update_mirror.py --type weekly
"""

import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = Path(__file__).parent
LAST_UPDATED_FILE = PROJECT_ROOT / "LAST_UPDATED.md"
RUN_LOG_FILE = PROJECT_ROOT / "raw" / "run_log.json"

# Script paths
PULL_STIP = SCRIPTS_DIR / "pull_stip.py"
PULL_CONSTRUCTION = SCRIPTS_DIR / "pull_active_construction.py"
PULL_PROGLOC = SCRIPTS_DIR / "pull_progloc.py"
GENERATE_MARKDOWN = SCRIPTS_DIR / "generate_markdown.py"
BUILD_INDEXES = SCRIPTS_DIR / "build_indexes.py"
DETECT_REMOVED = SCRIPTS_DIR / "detect_removed_projects.py"

# Update type configurations
UPDATE_CONFIGS = {
    "daily": {
        "description": "Daily update - Active construction only",
        "pull_scripts": [
            (PULL_CONSTRUCTION, "Active Construction"),
        ],
        "regenerate_markdown": True,
        "detect_removed": False,  # No STIP pull, so no removal detection
    },
    "weekly": {
        "description": "Weekly update - STIP, ProgLoc, and construction",
        "pull_scripts": [
            (PULL_STIP, "STIP"),
            (PULL_CONSTRUCTION, "Active Construction"),
            (PULL_PROGLOC, "ProgLoc"),
        ],
        "regenerate_markdown": True,
        "detect_removed": True,
    },
    "monthly": {
        "description": "Monthly update - All data sources",
        "pull_scripts": [
            (PULL_STIP, "STIP"),
            (PULL_CONSTRUCTION, "Active Construction"),
            (PULL_PROGLOC, "ProgLoc"),
            # Future: AADT, project URLs
        ],
        "regenerate_markdown": True,
        "detect_removed": True,
    },
    "full": {
        "description": "Full update - All data sources (recovery/initial)",
        "pull_scripts": [
            (PULL_STIP, "STIP"),
            (PULL_CONSTRUCTION, "Active Construction"),
            (PULL_PROGLOC, "ProgLoc"),
        ],
        "regenerate_markdown": True,
        "detect_removed": True,
    },
}


def run_script(script_path: Path, name: str) -> tuple[bool, float]:
    """
    Run a Python script and capture result.

    Args:
        script_path: Path to the script to run
        name: Human-readable name for logging

    Returns:
        Tuple of (success: bool, duration_seconds: float)
    """
    logger.info(f"Running: {name}")
    start = time.time()

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout per script
        )

        duration = time.time() - start

        if result.returncode == 0:
            logger.info(f"  {name} completed in {duration:.1f}s")
            return True, duration
        else:
            logger.error(f"  {name} failed (exit code {result.returncode})")
            if result.stderr:
                logger.error(f"  stderr: {result.stderr[:500]}")
            return False, duration

    except subprocess.TimeoutExpired:
        duration = time.time() - start
        logger.error(f"  {name} timed out after {duration:.1f}s")
        return False, duration
    except Exception as e:
        duration = time.time() - start
        logger.error(f"  {name} raised exception: {e}")
        return False, duration


def load_run_log() -> list:
    """Load previous run log entries."""
    if not RUN_LOG_FILE.exists():
        return []
    try:
        with open(RUN_LOG_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_run_log(entries: list) -> None:
    """Save run log entries, keeping last 30."""
    RUN_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    # Keep only last 30 entries
    recent = entries[-30:]
    with open(RUN_LOG_FILE, "w") as f:
        json.dump(recent, f, indent=2)


def update_last_updated(run_entry: dict) -> None:
    """Update the LAST_UPDATED.md file with run status."""
    # Load recent history from run log
    run_log = load_run_log()
    recent_runs = run_log[-10:]  # Last 10 runs for display

    # Build history table
    history_rows = []
    for entry in reversed(recent_runs):
        date = entry.get("start_time", "")[:16].replace("T", " ")
        update_type = entry.get("update_type", "unknown")
        status = "Success" if entry.get("success") else "Failed"
        history_rows.append(f"| {date} | {update_type} | {status} |")

    history_table = "\n".join(history_rows) if history_rows else "| No history yet | | |"

    # Get counts from the run entry
    stip_count = run_entry.get("counts", {}).get("stip_projects", "N/A")
    construction_count = run_entry.get("counts", {}).get("construction_contracts", "N/A")
    progloc_count = run_entry.get("counts", {}).get("progloc_contracts", "N/A")

    # Format errors
    errors = run_entry.get("errors", [])
    error_text = "\n".join(f"- {e}" for e in errors) if errors else "None"

    content = f"""# Mirror Status

**Last Successful Update:** {run_entry.get("start_time", "Unknown")}
**Update Type:** {run_entry.get("update_type", "Unknown")}
**Duration:** {run_entry.get("total_duration", 0):.1f} seconds

## Data Counts

| Source | Records |
|--------|---------|
| STIP Projects | {stip_count} |
| Active Construction | {construction_count} |
| ProgLoc Contracts | {progloc_count} |

## Errors

{error_text}

## Recent History

| Date | Type | Status |
|------|------|--------|
{history_table}

---

*This file is automatically updated by the mirror sync process.*
*Data Source: [NCDOT](https://www.ncdot.gov/)*
"""

    LAST_UPDATED_FILE.write_text(content, encoding="utf-8")
    logger.info(f"Updated: {LAST_UPDATED_FILE}")


def get_data_counts() -> dict:
    """Get record counts from the raw data files."""
    counts = {}

    # STIP projects
    stip_meta = PROJECT_ROOT / "raw" / "stip" / "last_pull.json"
    if stip_meta.exists():
        with open(stip_meta) as f:
            data = json.load(f)
            counts["stip_projects"] = data.get("total_features", 0)

    # Construction contracts
    construction_meta = PROJECT_ROOT / "raw" / "active-construction" / "last_pull.json"
    if construction_meta.exists():
        with open(construction_meta) as f:
            data = json.load(f)
            counts["construction_contracts"] = data.get("table_count", 0)

    # ProgLoc contracts
    progloc_meta = PROJECT_ROOT / "raw" / "progloc" / "last_pull.json"
    if progloc_meta.exists():
        with open(progloc_meta) as f:
            data = json.load(f)
            counts["progloc_contracts"] = data.get("total_contracts", 0)

    return counts


def run_update(update_type: str) -> dict:
    """
    Execute the update process.

    Args:
        update_type: One of 'daily', 'weekly', 'monthly', 'full'

    Returns:
        Dict with run statistics
    """
    config = UPDATE_CONFIGS[update_type]
    start_time = datetime.now(timezone.utc)

    logger.info("=" * 60)
    logger.info(f"NCDOT Mirror Update: {update_type}")
    logger.info(f"{config['description']}")
    logger.info(f"Started: {start_time.isoformat()}")
    logger.info("=" * 60)

    run_entry = {
        "start_time": start_time.isoformat(),
        "update_type": update_type,
        "scripts_run": [],
        "errors": [],
        "success": True,
    }

    # Phase 1: Pull data from sources
    logger.info("\n--- Phase 1: Pull Data ---")
    for script_path, name in config["pull_scripts"]:
        if script_path.exists():
            success, duration = run_script(script_path, name)
            run_entry["scripts_run"].append({
                "name": name,
                "success": success,
                "duration": duration,
            })
            if not success:
                run_entry["errors"].append(f"{name} pull failed")
                # Continue with other scripts - partial update is better than none
        else:
            logger.warning(f"Script not found: {script_path}")
            run_entry["errors"].append(f"{name} script not found")

    # Phase 2: Detect removed projects (if STIP was pulled)
    if config["detect_removed"]:
        logger.info("\n--- Phase 2: Detect Removed Projects ---")
        success, duration = run_script(DETECT_REMOVED, "Detect Removed")
        run_entry["scripts_run"].append({
            "name": "Detect Removed",
            "success": success,
            "duration": duration,
        })
        if not success:
            run_entry["errors"].append("Removal detection had issues")

    # Phase 3: Regenerate markdown files
    if config["regenerate_markdown"]:
        logger.info("\n--- Phase 3: Generate Markdown ---")
        success, duration = run_script(GENERATE_MARKDOWN, "Generate Markdown")
        run_entry["scripts_run"].append({
            "name": "Generate Markdown",
            "success": success,
            "duration": duration,
        })
        if not success:
            run_entry["errors"].append("Markdown generation failed")
            run_entry["success"] = False  # This is critical

    # Phase 4: Build indexes
    logger.info("\n--- Phase 4: Build Indexes ---")
    success, duration = run_script(BUILD_INDEXES, "Build Indexes")
    run_entry["scripts_run"].append({
        "name": "Build Indexes",
        "success": success,
        "duration": duration,
    })
    if not success:
        run_entry["errors"].append("Index build failed")
        run_entry["success"] = False  # This is critical

    # Calculate totals
    end_time = datetime.now(timezone.utc)
    total_duration = (end_time - start_time).total_seconds()
    run_entry["end_time"] = end_time.isoformat()
    run_entry["total_duration"] = total_duration
    run_entry["counts"] = get_data_counts()

    # Update run log
    run_log = load_run_log()
    run_log.append(run_entry)
    save_run_log(run_log)

    # Update LAST_UPDATED.md
    update_last_updated(run_entry)

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Update Complete")
    logger.info(f"  Update Type: {update_type}")
    logger.info(f"  Duration: {total_duration:.1f}s")
    logger.info(f"  Scripts Run: {len(run_entry['scripts_run'])}")
    logger.info(f"  Errors: {len(run_entry['errors'])}")
    if run_entry["errors"]:
        for error in run_entry["errors"]:
            logger.warning(f"    - {error}")
    logger.info(f"  Overall Success: {run_entry['success']}")
    logger.info("=" * 60)

    return run_entry


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="NCDOT STIP Mirror Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Update Types:
  daily    Active construction only (HiCAMS updates nightly)
  weekly   STIP + ProgLoc + construction
  monthly  All data sources (future: AADT)
  full     Everything (recovery/initial population)

Examples:
  python update_mirror.py daily
  python update_mirror.py --type weekly
  python update_mirror.py full
        """,
    )
    parser.add_argument(
        "update_type",
        nargs="?",
        choices=["daily", "weekly", "monthly", "full"],
        help="Update type to run",
    )
    parser.add_argument(
        "--type", "-t",
        dest="update_type_flag",
        choices=["daily", "weekly", "monthly", "full"],
        help="Update type (alternative syntax)",
    )

    args = parser.parse_args()

    # Determine update type from args
    update_type = args.update_type or args.update_type_flag
    if not update_type:
        parser.print_help()
        print("\nError: Please specify an update type")
        sys.exit(1)

    # Run the update
    result = run_update(update_type)

    # Exit with appropriate code
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
