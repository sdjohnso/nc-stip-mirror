#!/usr/bin/env python3
"""
NCDOT STIP Index Builder

Generates index files for counties and statewide summary.
Reads raw STIP data, cross-references, and construction data to build navigable indexes.

Output:
  - counties/{county-name}/index.md for each county with projects
  - index.md (statewide summary at project root)
"""

import json
import logging
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# Add scripts directory to path for config import
sys.path.insert(0, str(Path(__file__).parent))
from config import NC_COUNTIES, normalize_county, display_county

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
CONSTRUCTION_DIR = PROJECT_ROOT / "raw" / "active-construction"
COUNTIES_DIR = PROJECT_ROOT / "counties"
POINTS_FILE = RAW_DIR / "stip_points_full.json"
LINES_FILE = RAW_DIR / "stip_lines_full.json"
METADATA_FILE = RAW_DIR / "last_pull.json"
CROSS_REF_FILE = RAW_DIR / "cross_references.json"
CONSTRUCTION_TABLE_FILE = CONSTRUCTION_DIR / "construction_table.json"
STATEWIDE_INDEX = PROJECT_ROOT / "index.md"


def load_json(filepath: Path) -> dict | list:
    """Load JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def get_base_tip(tip: str) -> str:
    """Extract base TIP number (without suffix letter)."""
    match = re.match(r'^([A-Z]+-\d+)([A-Z]*)$', tip.strip())
    if match:
        return match.group(1)
    return tip.strip()


def load_construction_data() -> dict[str, dict]:
    """
    Load construction data and build TIP -> best contract info mapping.

    Returns dict where keys are TIPs (both exact and base) and values are
    dicts with: status, completion_percent, contract_count
    """
    tip_to_construction = {}

    if not CONSTRUCTION_TABLE_FILE.exists():
        logger.warning(f"Construction data not found: {CONSTRUCTION_TABLE_FILE}")
        return tip_to_construction

    try:
        data = load_json(CONSTRUCTION_TABLE_FILE)
        features = data.get("features", [])

        # Group contracts by TIP
        tip_contracts = defaultdict(list)
        for feat in features:
            attrs = feat.get("attributes", {})
            tip_ref = attrs.get("TipReference", "")
            if not tip_ref:
                continue

            tips = [t.strip() for t in tip_ref.split(",") if t.strip()]
            contract_info = {
                "status": attrs.get("ContractStatus", ""),
                "completion_percent": attrs.get("CompletionPercent"),
            }

            for tip in tips:
                tip_contracts[tip].append(contract_info)
                base = get_base_tip(tip)
                if base != tip:
                    tip_contracts[base].append(contract_info)

        # Build summary for each TIP
        for tip, contracts in tip_contracts.items():
            # Find best status (prefer ACTIVE)
            active_contracts = [c for c in contracts if c["status"] == "ACTIVE"]
            if active_contracts:
                # Average completion of active contracts
                completions = [c["completion_percent"] for c in active_contracts if c["completion_percent"] is not None]
                avg_completion = sum(completions) / len(completions) if completions else None
                tip_to_construction[tip] = {
                    "status": "ACTIVE",
                    "completion_percent": avg_completion,
                    "contract_count": len(active_contracts),
                }
            else:
                # Use first contract status
                tip_to_construction[tip] = {
                    "status": contracts[0]["status"],
                    "completion_percent": contracts[0]["completion_percent"],
                    "contract_count": len(contracts),
                }

        logger.info(f"Loaded construction data for {len(tip_to_construction)} TIP variations")

    except Exception as e:
        logger.error(f"Error loading construction data: {e}")

    return tip_to_construction


def determine_status(comment: str) -> str:
    """
    Determine project status from COMMENT field.

    Returns one of: 'Under Construction', 'Right-of-Way', 'Completed', 'Planned'
    """
    if not comment:
        return "Planned"

    comment_upper = comment.upper()

    if "UNDER CONSTRUCTION" in comment_upper:
        return "Under Construction"
    elif "COMPLETE" in comment_upper:
        return "Completed"
    elif "RIGHT-OF-WAY" in comment_upper or "RIGHT OF WAY" in comment_upper:
        return "Right-of-Way"
    else:
        return "Planned"


def get_status_emoji(status: str) -> str:
    """Get emoji indicator for status."""
    return {
        "Active Construction": "🏗️",
        "Under Construction": "🚧",
        "Right-of-Way": "📋",
        "Completed": "✅",
        "Planned": "📅",
    }.get(status, "")


def sanitize_filename(tip: str) -> str:
    """Sanitize TIP number for use as filename."""
    return re.sub(r'[<>:"/\\|?*]', '_', tip.strip())


def truncate(text: str, max_len: int = 60) -> str:
    """Truncate text with ellipsis if too long."""
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def build_project_index(
    points_data: dict, lines_data: dict, construction_data: dict[str, dict]
) -> dict[str, list[dict]]:
    """
    Build index of projects grouped by county.

    Returns dict: county_name -> list of project info dicts
    """
    projects_by_county = defaultdict(list)
    seen_tips = {}  # Track TIPs to avoid duplicates

    # Process all features
    for feat in points_data.get("features", []) + lines_data.get("features", []):
        attrs = feat.get("attributes", {})
        tip = attrs.get("TIP", "").strip()
        if not tip:
            continue

        # Skip if we've already processed this TIP
        if tip in seen_tips:
            continue
        seen_tips[tip] = True

        counties_str = attrs.get("Counties", "")
        if not counties_str:
            continue

        # Parse counties - project goes in first county
        counties = [c.strip() for c in counties_str.split(",") if c.strip()]
        if not counties:
            continue

        primary_county = normalize_county(counties[0])

        # Determine status - check construction data first
        base_tip = get_base_tip(tip)
        const_info = construction_data.get(tip) or construction_data.get(base_tip)

        if const_info and const_info.get("status") == "ACTIVE":
            status = "Active Construction"
            completion = const_info.get("completion_percent")
        else:
            status = determine_status(attrs.get("COMMENT", ""))
            completion = None

        # Build project info
        project_info = {
            "tip": tip,
            "description": attrs.get("Description", "") or "",
            "route": attrs.get("Route", "") or "",
            "mode": attrs.get("Mode", "") or "",
            "status": status,
            "completion_percent": completion,
            "counties": counties_str,
            "is_multi_county": len(counties) > 1,
        }

        projects_by_county[primary_county].append(project_info)

    return dict(projects_by_county)


def generate_county_index(
    county: str,
    projects: list[dict],
    cross_refs: list[dict],
    pull_timestamp: str,
) -> str:
    """Generate markdown index for a county."""

    display_name = display_county(county)
    mirror_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    ncdot_date = pull_timestamp[:10] if pull_timestamp else "Unknown"

    # Sort projects by TIP
    projects_sorted = sorted(projects, key=lambda p: p["tip"])

    # Group by status for summary
    by_status = defaultdict(list)
    for p in projects_sorted:
        by_status[p["status"]].append(p)

    # Build markdown
    lines = [
        f"# {display_name} County - STIP Projects",
        "",
        f"> **{len(projects)} projects** in the State Transportation Improvement Program",
        "",
        "## Summary",
        "",
        "| Status | Count |",
        "|--------|-------|",
    ]

    # Status summary in order
    status_order = ["Active Construction", "Under Construction", "Right-of-Way", "Planned", "Completed"]
    for status in status_order:
        count = len(by_status.get(status, []))
        if count > 0:
            emoji = get_status_emoji(status)
            lines.append(f"| {emoji} {status} | {count} |")

    lines.extend([
        "",
        "## All Projects",
        "",
        "| TIP | Description | Route | Status |",
        "|-----|-------------|-------|--------|",
    ])

    # Project table
    for p in projects_sorted:
        tip = p["tip"]
        filename = sanitize_filename(tip)
        desc = truncate(p["description"], 50)
        route = truncate(p["route"], 25)
        status = p["status"]
        emoji = get_status_emoji(status)

        # Multi-county indicator
        if p["is_multi_county"]:
            desc = f"🗺️ {desc}"

        # Add completion % for active construction
        status_display = status
        if status == "Active Construction" and p.get("completion_percent") is not None:
            status_display = f"{status} ({p['completion_percent']:.0f}%)"

        lines.append(f"| [{tip}]({filename}.md) | {desc} | {route} | {emoji} {status_display} |")

    # Cross-references section (projects from other counties that span this one)
    if cross_refs:
        lines.extend([
            "",
            "## Projects Spanning This County",
            "",
            "*These projects are primarily located in another county but include " + display_name + " County.*",
            "",
            "| TIP | Description | Route | Primary County |",
            "|-----|-------------|-------|----------------|",
        ])

        for ref in sorted(cross_refs, key=lambda r: r["tip"]):
            tip = ref["tip"]
            primary = ref["primary_county"]
            primary_display = display_county(primary)
            filename = sanitize_filename(tip)
            desc = truncate(ref.get("description", ""), 40)
            route = truncate(ref.get("route", ""), 20)

            lines.append(
                f"| [{tip}](../{primary}/{filename}.md) | {desc} | {route} | {primary_display} |"
            )

    # Footer
    lines.extend([
        "",
        "---",
        "",
        f"*Data Source: [NCDOT STIP](https://connect.ncdot.gov/projects/planning/Pages/STIP.aspx)*  ",
        f"*Last NCDOT Update: {ncdot_date}*  ",
        f"*Mirror Updated: {mirror_date}*",
    ])

    return "\n".join(lines)


def generate_statewide_index(
    projects_by_county: dict[str, list[dict]],
    cross_refs: dict[str, list[dict]],
    pull_timestamp: str,
) -> str:
    """Generate statewide index markdown."""

    mirror_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    ncdot_date = pull_timestamp[:10] if pull_timestamp else "Unknown"

    # Calculate totals
    total_projects = sum(len(p) for p in projects_by_county.values())

    # Count by status across all projects
    status_totals = defaultdict(int)
    for projects in projects_by_county.values():
        for p in projects:
            status_totals[p["status"]] += 1

    # Build markdown
    lines = [
        "# North Carolina STIP Projects",
        "",
        "> A mirror of the NC Department of Transportation State Transportation Improvement Program",
        "",
        "## Overview",
        "",
        f"This mirror contains **{total_projects:,} transportation projects** across all 100 North Carolina counties.",
        "",
        "### Project Status Summary",
        "",
        "| Status | Count |",
        "|--------|-------|",
    ]

    status_order = ["Active Construction", "Under Construction", "Right-of-Way", "Planned", "Completed"]
    for status in status_order:
        count = status_totals.get(status, 0)
        if count > 0:
            emoji = get_status_emoji(status)
            lines.append(f"| {emoji} {status} | {count:,} |")

    lines.extend([
        "",
        "## Counties",
        "",
        "| County | Projects | Active Construction | Planned |",
        "|--------|----------|---------------------|---------|",
    ])

    # County table - sorted alphabetically
    for county_key in sorted(NC_COUNTIES.keys()):
        projects = projects_by_county.get(county_key, [])
        cross_ref_count = len(cross_refs.get(county_key, []))

        total = len(projects)
        if total == 0 and cross_ref_count == 0:
            continue  # Skip counties with no projects at all

        display_name = display_county(county_key)

        # Count by status
        active_construction = sum(1 for p in projects if p["status"] == "Active Construction")
        planned = sum(1 for p in projects if p["status"] == "Planned")

        # Include cross-ref indicator if applicable
        total_display = str(total)
        if cross_ref_count > 0:
            total_display = f"{total} (+{cross_ref_count})"

        lines.append(
            f"| [{display_name}](counties/{county_key}/index.md) | {total_display} | {active_construction} | {planned} |"
        )

    lines.extend([
        "",
        "## About This Mirror",
        "",
        "This is an automated mirror of public NCDOT transportation project data. ",
        "It is designed to provide easy access to project information for residents, ",
        "researchers, and AI assistants.",
        "",
        "### Data Sources",
        "",
        "- **STIP Data**: [NCDOT STIP ArcGIS Service](https://gis11.services.ncdot.gov/arcgis/rest/services/NCDOT_STIP/MapServer)",
        "",
        "### Update Schedule",
        "",
        "- STIP data is refreshed weekly",
        "",
        "---",
        "",
        f"*Data Source: [NCDOT STIP](https://connect.ncdot.gov/projects/planning/Pages/STIP.aspx)*  ",
        f"*Last NCDOT Update: {ncdot_date}*  ",
        f"*Mirror Updated: {mirror_date}*",
    ])

    return "\n".join(lines)


def main():
    """Build all index files."""
    logger.info("=" * 60)
    logger.info("STIP Index Builder Started")
    logger.info("=" * 60)

    # Load data
    logger.info("Loading raw JSON data...")
    points_data = load_json(POINTS_FILE)
    lines_data = load_json(LINES_FILE)
    metadata = load_json(METADATA_FILE)

    pull_timestamp = metadata.get("last_pull_completed", "")

    # Load construction data
    construction_data = load_construction_data()

    # Load cross-references
    cross_refs = {}
    if CROSS_REF_FILE.exists():
        cross_refs = load_json(CROSS_REF_FILE)
        logger.info(f"Loaded cross-references for {len(cross_refs)} counties")

    # Build project index
    logger.info("Building project index...")
    projects_by_county = build_project_index(points_data, lines_data, construction_data)
    logger.info(f"Found projects in {len(projects_by_county)} counties")

    # Generate county indexes
    logger.info("Generating county indexes...")
    county_count = 0

    for county, projects in projects_by_county.items():
        county_cross_refs = cross_refs.get(county, [])

        index_content = generate_county_index(
            county, projects, county_cross_refs, pull_timestamp
        )

        county_dir = COUNTIES_DIR / county
        county_dir.mkdir(parents=True, exist_ok=True)

        index_path = county_dir / "index.md"
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(index_content)

        county_count += 1

    # Also create indexes for counties that only have cross-references
    for county, refs in cross_refs.items():
        if county not in projects_by_county and refs:
            # County has no primary projects but has cross-references
            index_content = generate_county_index(county, [], refs, pull_timestamp)

            county_dir = COUNTIES_DIR / county
            county_dir.mkdir(parents=True, exist_ok=True)

            index_path = county_dir / "index.md"
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(index_content)

            county_count += 1

    logger.info(f"Created {county_count} county indexes")

    # Generate statewide index
    logger.info("Generating statewide index...")
    statewide_content = generate_statewide_index(
        projects_by_county, cross_refs, pull_timestamp
    )

    with open(STATEWIDE_INDEX, "w", encoding="utf-8") as f:
        f.write(statewide_content)

    logger.info(f"Created statewide index at {STATEWIDE_INDEX}")

    # Summary
    total_projects = sum(len(p) for p in projects_by_county.values())
    logger.info("=" * 60)
    logger.info("Index Generation Complete!")
    logger.info(f"  Total projects indexed: {total_projects}")
    logger.info(f"  County indexes created: {county_count}")
    logger.info(f"  Statewide index: {STATEWIDE_INDEX}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
