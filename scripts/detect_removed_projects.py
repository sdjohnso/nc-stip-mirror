#!/usr/bin/env python3
"""
NCDOT STIP Removed Project Detector

Compares current STIP data to the TIP inventory from the previous pull.
Projects that disappear from the API are marked as "No Longer in Active STIP"
rather than deleted - we never lose data.

Output:
  - Updates counties/{county}/{TIP}.md files with removal status
  - Updates raw/stip/tip_inventory.json with current TIP list
  - Returns list of removed TIPs for logging
"""

import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add scripts directory to path for config import
sys.path.insert(0, str(Path(__file__).parent))
from config import normalize_county

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "raw" / "stip"
COUNTIES_DIR = PROJECT_ROOT / "counties"
POINTS_FILE = RAW_DIR / "stip_points_full.json"
LINES_FILE = RAW_DIR / "stip_lines_full.json"
INVENTORY_FILE = RAW_DIR / "tip_inventory.json"


def load_json(filepath: Path) -> dict | list:
    """Load JSON file, return empty dict if file doesn't exist."""
    if not filepath.exists():
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: dict | list, output_path: Path) -> None:
    """Save data to JSON file with proper formatting."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved: {output_path}")


def get_current_tips() -> dict[str, dict]:
    """
    Extract all TIP numbers from current STIP data with their county info.

    Returns:
        Dict mapping TIP -> {county: str, description: str}
    """
    tips = {}

    # Load both point and line features
    for filepath in [POINTS_FILE, LINES_FILE]:
        if not filepath.exists():
            logger.warning(f"File not found: {filepath}")
            continue

        data = load_json(filepath)
        for feature in data.get("features", []):
            attrs = feature.get("attributes", {})
            tip = attrs.get("TIP")
            if tip and tip not in tips:
                # Store county info for locating the file later
                county_raw = attrs.get("Counties", "")
                # Take first county if multi-county (matching generate_markdown.py behavior)
                if county_raw:
                    first_county = county_raw.split(",")[0].strip()
                    county = normalize_county(first_county)
                else:
                    county = "unknown"

                tips[tip] = {
                    "county": county,
                    "description": attrs.get("Description", ""),
                }

    return tips


def load_previous_inventory() -> dict:
    """
    Load previous TIP inventory.

    Returns:
        Dict with 'tips' (dict of TIP -> info) and 'last_updated' timestamp
    """
    if not INVENTORY_FILE.exists():
        logger.info("No previous inventory found - this appears to be the first run")
        return {"tips": {}, "last_updated": None}

    return load_json(INVENTORY_FILE)


def find_project_file(tip: str, county: str) -> Path | None:
    """
    Find the markdown file for a project.

    Args:
        tip: TIP number
        county: Normalized county name (lowercase)

    Returns:
        Path to project file, or None if not found
    """
    # Try the expected location first
    expected_path = COUNTIES_DIR / county / f"{tip}.md"
    if expected_path.exists():
        return expected_path

    # Search all county directories (in case county changed or was wrong)
    for county_dir in COUNTIES_DIR.iterdir():
        if county_dir.is_dir():
            potential_path = county_dir / f"{tip}.md"
            if potential_path.exists():
                return potential_path

    return None


def mark_project_as_removed(project_file: Path, tip: str) -> bool:
    """
    Update project markdown file to indicate it's no longer in active STIP.

    Args:
        project_file: Path to the project's markdown file
        tip: TIP number for logging

    Returns:
        True if file was updated, False if already marked or error
    """
    try:
        content = project_file.read_text(encoding="utf-8")

        # Check if already marked as removed
        if "No Longer in Active STIP" in content:
            logger.debug(f"{tip} already marked as removed")
            return False

        # Add removal notice after the title line
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        removal_notice = f"""
> **Status: No Longer in Active STIP**
> *This project was removed from NCDOT's active STIP database as of {today}.*
> *The project may have been completed, cancelled, or consolidated with another project.*
"""

        # Insert after the first heading and description block
        # Find the first "## " section header
        match = re.search(r'\n## ', content)
        if match:
            insert_pos = match.start()
            new_content = content[:insert_pos] + removal_notice + content[insert_pos:]
        else:
            # Fallback: insert after the first line
            first_newline = content.find('\n')
            if first_newline > 0:
                new_content = content[:first_newline + 1] + removal_notice + content[first_newline + 1:]
            else:
                new_content = content + removal_notice

        # Update the mirror timestamp at the bottom
        new_content = re.sub(
            r'\*Mirror Updated: [^*]+\*',
            f'*Mirror Updated: {datetime.now(timezone.utc).isoformat()}*',
            new_content
        )

        project_file.write_text(new_content, encoding="utf-8")
        logger.info(f"Marked as removed: {tip}")
        return True

    except Exception as e:
        logger.error(f"Failed to update {project_file}: {e}")
        return False


def detect_removed_projects() -> dict:
    """
    Main function to detect and mark removed projects.

    Returns:
        Dict with statistics about the operation
    """
    logger.info("=" * 60)
    logger.info("Detecting Removed Projects")
    logger.info("=" * 60)

    # Load current and previous TIP lists
    current_tips = get_current_tips()
    previous_inventory = load_previous_inventory()
    previous_tips = previous_inventory.get("tips", {})

    logger.info(f"Current TIPs: {len(current_tips)}")
    logger.info(f"Previous TIPs: {len(previous_tips)}")

    # Find removed TIPs (in previous but not in current)
    current_tip_set = set(current_tips.keys())
    previous_tip_set = set(previous_tips.keys())

    removed_tips = previous_tip_set - current_tip_set
    new_tips = current_tip_set - previous_tip_set

    logger.info(f"Removed from STIP: {len(removed_tips)}")
    logger.info(f"New in STIP: {len(new_tips)}")

    # Mark removed projects
    marked_count = 0
    not_found_count = 0
    already_marked_count = 0

    for tip in sorted(removed_tips):
        info = previous_tips.get(tip, {})
        county = info.get("county", "unknown")

        project_file = find_project_file(tip, county)
        if project_file:
            if mark_project_as_removed(project_file, tip):
                marked_count += 1
            else:
                already_marked_count += 1
        else:
            logger.warning(f"Project file not found for removed TIP: {tip}")
            not_found_count += 1

    # Update inventory with current TIPs
    new_inventory = {
        "tips": current_tips,
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "tip_count": len(current_tips),
    }
    save_json(new_inventory, INVENTORY_FILE)

    # Summary
    stats = {
        "current_tip_count": len(current_tips),
        "previous_tip_count": len(previous_tips),
        "removed_count": len(removed_tips),
        "new_count": len(new_tips),
        "files_marked": marked_count,
        "already_marked": already_marked_count,
        "files_not_found": not_found_count,
        "removed_tips": sorted(removed_tips) if removed_tips else [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    logger.info("=" * 60)
    logger.info("Detection Complete")
    logger.info(f"  Removed TIPs: {len(removed_tips)}")
    logger.info(f"  Files marked: {marked_count}")
    logger.info(f"  Already marked: {already_marked_count}")
    logger.info(f"  Files not found: {not_found_count}")
    logger.info(f"  New TIPs: {len(new_tips)}")
    logger.info("=" * 60)

    return stats


def main():
    """Entry point for standalone execution."""
    stats = detect_removed_projects()

    # Print removed TIPs if any
    if stats["removed_tips"]:
        print("\nRemoved TIPs:")
        for tip in stats["removed_tips"]:
            print(f"  - {tip}")

    return 0 if stats["files_not_found"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
