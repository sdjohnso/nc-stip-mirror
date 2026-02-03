#!/usr/bin/env python3
"""
NCDOT STIP Markdown Generator

Reads raw STIP JSON data and generates individual markdown files for each project.
Handles multi-county projects by placing the file in the first listed county.
Merges active construction data when available.

Output:
  - counties/{county-name}/{TIP}.md for each project
  - raw/stip/cross_references.json for multi-county tracking
"""

import json
import logging
import re
import sys
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
CONSTRUCTION_METADATA_FILE = CONSTRUCTION_DIR / "last_pull.json"
PROGLOC_DIR = PROJECT_ROOT / "raw" / "progloc"
PROGLOC_FILE = PROGLOC_DIR / "progress_reports.json"

# Markdown template for project files
PROJECT_TEMPLATE = '''# {tip}

> **{description}**

## Project Details

| Field | Value |
|-------|-------|
| **TIP Number** | {tip} |
| **SPOT ID** | {spot_id} |
| **Route** | {route} |
| **County** | {counties} |
| **Division** | {divisions} |
| **MPO/RPO** | {mpo_rpo} |

## Project Information

- **Category:** {category}
- **Mode:** {mode}
- **Project Cost:** {project_cost}
- **Right of Way Year:** {row_year}
- **Construction Year:** {construction_year}

## Status

{comment}

## Construction Status

{construction_section}

## Progress Report

{progloc_section}

## Location

- **Coordinates:** {coordinates}
- **Geometry Type:** {geometry_type}

---

*Data Source: [NCDOT STIP](https://connect.ncdot.gov/projects/planning/Pages/STIP.aspx)*
*Last NCDOT Update: {ncdot_update}*
*Mirror Updated: {mirror_update}*
'''


def load_json(filepath: Path) -> dict:
    """Load JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: dict | list, filepath: Path) -> None:
    """Save data to JSON file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def calculate_centroid_point(geometry: dict) -> tuple[float, float] | None:
    """Calculate centroid from point geometry."""
    points = geometry.get("points", [])
    if not points:
        return None
    # Use first point (usually only one)
    return (points[0][0], points[0][1])  # (lon, lat)


def calculate_centroid_line(geometry: dict) -> tuple[float, float] | None:
    """Calculate centroid from line geometry (average of all vertices)."""
    paths = geometry.get("paths", [])
    if not paths:
        return None

    all_points = []
    for path in paths:
        all_points.extend(path)

    if not all_points:
        return None

    avg_lon = sum(p[0] for p in all_points) / len(all_points)
    avg_lat = sum(p[1] for p in all_points) / len(all_points)
    return (avg_lon, avg_lat)


def format_value(value, null_marker: bool = True) -> str:
    """
    Format a value for markdown display.

    Args:
        value: The value to format
        null_marker: If True, add <!-- null --> comment for None/empty values

    Returns:
        Formatted string
    """
    if value is None or value == "" or (isinstance(value, str) and value.strip() == ""):
        if null_marker:
            return "Not Available <!-- null -->"
        return "Not Available"
    return str(value)


def format_cost(value) -> str:
    """Format project cost in thousands (value is in $1000s)."""
    if value is None:
        return "Not Available <!-- null -->"
    try:
        # API returns cost in thousands
        cost = float(value) * 1000
        return f"${cost:,.0f}"
    except (ValueError, TypeError):
        return "Not Available <!-- null -->"


def format_coordinates(lon: float | None, lat: float | None) -> str:
    """Format coordinates to 5 decimal places."""
    if lon is None or lat is None:
        return "Not Available <!-- null -->"
    return f"{lat:.5f}, {lon:.5f}"


def parse_counties(counties_str: str) -> list[str]:
    """
    Parse county string into list of normalized county names.

    Args:
        counties_str: Comma-separated county names (e.g., "Pitt, Greene")

    Returns:
        List of normalized county folder names
    """
    if not counties_str:
        return []

    counties = []
    for county in counties_str.split(","):
        county = county.strip()
        if county:
            normalized = normalize_county(county)
            # Validate against known counties
            if normalized in NC_COUNTIES:
                counties.append(normalized)
            else:
                logger.warning(f"Unknown county: {county}")
                counties.append(normalized)

    return counties


def sanitize_filename(tip: str) -> str:
    """Sanitize TIP number for use as filename."""
    # Replace any characters that might be problematic in filenames
    return re.sub(r'[<>:"/\\|?*]', '_', tip.strip())


def get_base_tip(tip: str) -> str:
    """
    Extract base TIP number (without suffix letter).

    Examples:
        'R-5734A' -> 'R-5734'
        'C-5606C' -> 'C-5606'
        'U-5606' -> 'U-5606'
    """
    match = re.match(r'^([A-Z]+-\d+)([A-Z]*)$', tip.strip())
    if match:
        return match.group(1)
    return tip.strip()


def load_construction_data() -> dict[str, list[dict]]:
    """
    Load construction data and build TIP -> contracts mapping.

    Returns dict where keys are base TIP numbers and values are lists
    of contract records. Handles comma-separated TipReferences.
    """
    tip_to_contracts = {}

    if not CONSTRUCTION_TABLE_FILE.exists():
        logger.warning(f"Construction data not found: {CONSTRUCTION_TABLE_FILE}")
        return tip_to_contracts

    try:
        data = load_json(CONSTRUCTION_TABLE_FILE)
        features = data.get("features", [])
        logger.info(f"Loading construction data: {len(features)} contracts")

        for feat in features:
            attrs = feat.get("attributes", {})
            tip_ref = attrs.get("TipReference", "")

            if not tip_ref:
                continue

            # Parse comma-separated TIPs
            tips = [t.strip() for t in tip_ref.split(",") if t.strip()]

            # Build contract record
            contract = {
                "contract_number": attrs.get("ContractNumber", ""),
                "contract_type": attrs.get("ContractType", ""),
                "contract_status": attrs.get("ContractStatus", ""),
                "completion_percent": attrs.get("CompletionPercent"),
                "contract_active_date": attrs.get("ContractActiveDate"),
                "contract_nickname": attrs.get("ContractNickname", ""),
                "location_description": attrs.get("LocationsDescription", ""),
                "route": attrs.get("Route", ""),
            }

            # Link to all TIPs (both direct and base)
            for tip in tips:
                # Add under exact TIP
                if tip not in tip_to_contracts:
                    tip_to_contracts[tip] = []
                tip_to_contracts[tip].append(contract)

                # Also add under base TIP for matching
                base = get_base_tip(tip)
                if base != tip:
                    if base not in tip_to_contracts:
                        tip_to_contracts[base] = []
                    # Avoid duplicates
                    if contract not in tip_to_contracts[base]:
                        tip_to_contracts[base].append(contract)

        logger.info(f"Mapped construction data to {len(tip_to_contracts)} TIP variations")

    except Exception as e:
        logger.error(f"Error loading construction data: {e}")

    return tip_to_contracts


def format_epoch_date(epoch_ms: int | None) -> str:
    """Convert epoch milliseconds to readable date."""
    if epoch_ms is None:
        return "Unknown"
    try:
        dt = datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError, OSError):
        return "Unknown"


def format_construction_section(
    tip: str, tip_to_contracts: dict[str, list[dict]]
) -> str:
    """
    Format the construction section for a project.

    Looks up contracts by exact TIP match first, then base TIP match.
    """
    contracts = []

    # Try exact match first
    if tip in tip_to_contracts:
        contracts = tip_to_contracts[tip]
    else:
        # Try base TIP match
        base = get_base_tip(tip)
        if base in tip_to_contracts:
            contracts = tip_to_contracts[base]

    if not contracts:
        return "Not currently under construction. <!-- no-construction -->"

    # Build markdown for each contract
    lines = []
    for i, contract in enumerate(contracts, 1):
        completion = contract.get("completion_percent")
        completion_str = f"{completion:.1f}%" if completion is not None else "Unknown"

        active_date = format_epoch_date(contract.get("contract_active_date"))
        status = contract.get("contract_status", "Unknown")
        contract_num = contract.get("contract_number", "Unknown")
        nickname = contract.get("contract_nickname", "")

        if len(contracts) > 1:
            lines.append(f"### Contract {i}: {contract_num}")
        else:
            lines.append(f"**Contract:** {contract_num}")

        if nickname:
            lines.append(f"- **Nickname:** {nickname}")
        lines.append(f"- **Status:** {status}")
        lines.append(f"- **Completion:** {completion_str}")
        lines.append(f"- **Active Since:** {active_date}")
        lines.append("")

    return "\n".join(lines).strip()


def load_progloc_data() -> dict[str, list[dict]]:
    """
    Load ProgLoc progress report data and build TIP -> contracts mapping.

    Returns dict where keys are TIP numbers and values are lists of
    contract records from ProgLoc.
    """
    tip_to_progloc = {}

    if not PROGLOC_FILE.exists():
        logger.warning(f"ProgLoc data not found: {PROGLOC_FILE}")
        return tip_to_progloc

    try:
        data = load_json(PROGLOC_FILE)
        tip_index = data.get("tip_index", {})
        logger.info(f"Loading ProgLoc data: {len(tip_index)} TIP entries")
        return tip_index

    except Exception as e:
        logger.error(f"Error loading ProgLoc data: {e}")
        return tip_to_progloc


def format_progloc_section(
    tip: str, tip_to_progloc: dict[str, list[dict]]
) -> str:
    """
    Format the progress report section from ProgLoc data.

    Looks up contracts by exact TIP match first, then base TIP match.
    """
    contracts = []

    # Try exact match first
    if tip in tip_to_progloc:
        contracts = tip_to_progloc[tip]
    else:
        # Try base TIP match
        base = get_base_tip(tip)
        if base in tip_to_progloc:
            contracts = tip_to_progloc[base]

    if not contracts:
        return "No progress report available. <!-- no-progloc -->"

    # Build markdown for each contract
    lines = []
    for i, contract in enumerate(contracts, 1):
        contract_num = contract.get("Contract Number", "Unknown")
        contractor = contract.get("Contractor", "Unknown")
        contract_amt = contract.get("Contract Amount")
        completion = contract.get("Completion Percent")
        county = contract.get("County", "")
        route = contract.get("Route", "")
        location = contract.get("Location Description", "")

        # Format dates - they come as ISO strings
        work_began = contract.get("Work Began Date", "")
        if work_began:
            work_began = work_began[:10]  # Just the date part
        original_completion = contract.get("Completion Date", "")
        if original_completion:
            original_completion = original_completion[:10]
        revised_completion = contract.get("Revised Completion Date", "")
        if revised_completion:
            revised_completion = revised_completion[:10]
        latest_payment = contract.get("Latest Payment Date", "")
        if latest_payment:
            latest_payment = latest_payment[:10]

        # Format amounts
        if contract_amt:
            try:
                contract_amt_str = f"${float(contract_amt):,.2f}"
            except (ValueError, TypeError):
                contract_amt_str = str(contract_amt)
        else:
            contract_amt_str = "Unknown"

        # Format completion
        if completion is not None:
            try:
                completion_str = f"{float(completion) * 100:.1f}%"
            except (ValueError, TypeError):
                completion_str = str(completion)
        else:
            completion_str = "Unknown"

        if len(contracts) > 1:
            lines.append(f"### Contract {i}: {contract_num}")
        else:
            lines.append(f"**Contract:** {contract_num}")

        lines.append(f"- **Contractor:** {contractor}")
        lines.append(f"- **Contract Amount:** {contract_amt_str}")
        lines.append(f"- **Completion:** {completion_str}")

        if work_began:
            lines.append(f"- **Work Began:** {work_began}")
        if original_completion:
            lines.append(f"- **Original Completion:** {original_completion}")
        if revised_completion and revised_completion != original_completion:
            lines.append(f"- **Revised Completion:** {revised_completion}")
        if latest_payment:
            lines.append(f"- **Latest Payment:** {latest_payment}")

        lines.append("")

    return "\n".join(lines).strip()


def merge_projects(points_data: dict, lines_data: dict) -> dict[str, dict]:
    """
    Merge point and line features by TIP number.

    Returns dict keyed by TIP number with merged project data.
    """
    projects = {}

    # Process points first
    for feat in points_data.get("features", []):
        attrs = feat.get("attributes", {})
        tip = attrs.get("TIP", "").strip()
        if not tip:
            continue

        geom = feat.get("geometry", {})
        centroid = calculate_centroid_point(geom)

        projects[tip] = {
            "tip": tip,
            "attributes": attrs,
            "centroid": centroid,
            "geometry_type": "Point",
            "has_line": False,
        }

    # Process lines (may override or supplement points)
    for feat in lines_data.get("features", []):
        attrs = feat.get("attributes", {})
        tip = attrs.get("TIP", "").strip()
        if not tip:
            continue

        geom = feat.get("geometry", {})
        centroid = calculate_centroid_line(geom)

        if tip in projects:
            # Project exists from points - prefer line geometry if available
            if centroid:
                projects[tip]["centroid"] = centroid
                projects[tip]["geometry_type"] = "Line"
                projects[tip]["has_line"] = True
            # Merge any missing attributes (points might have data lines don't)
            for key, value in attrs.items():
                if key not in projects[tip]["attributes"] or not projects[tip]["attributes"][key]:
                    projects[tip]["attributes"][key] = value
        else:
            # New project only in lines
            projects[tip] = {
                "tip": tip,
                "attributes": attrs,
                "centroid": centroid,
                "geometry_type": "Line",
                "has_line": True,
            }

    return projects


def generate_project_markdown(
    project: dict,
    pull_timestamp: str,
    tip_to_contracts: dict[str, list[dict]],
    tip_to_progloc: dict[str, list[dict]],
) -> str:
    """Generate markdown content for a single project."""
    attrs = project["attributes"]
    centroid = project.get("centroid")

    # Extract and format fields
    tip = project["tip"]
    description = format_value(attrs.get("Description"))
    spot_id = format_value(attrs.get("SPOTID"))
    route = format_value(attrs.get("Route"))
    counties = format_value(attrs.get("Counties"))
    divisions = format_value(attrs.get("Divisions"))
    mpo_rpo = format_value(attrs.get("MPOsRPOs"))
    category = format_value(attrs.get("Category"))
    mode = format_value(attrs.get("Mode"))
    project_cost = format_cost(attrs.get("ProjectCost"))
    row_year = format_value(attrs.get("RightOfWayYear"))
    construction_year = format_value(attrs.get("ConstructionYear"))

    # Status/comment
    comment_raw = attrs.get("COMMENT", "")
    if comment_raw:
        comment = comment_raw
    else:
        comment = "No status information available. <!-- null -->"

    # Construction status
    construction_section = format_construction_section(tip, tip_to_contracts)

    # Progress report (ProgLoc)
    progloc_section = format_progloc_section(tip, tip_to_progloc)

    # Coordinates
    if centroid:
        coordinates = format_coordinates(centroid[0], centroid[1])
    else:
        coordinates = "Not Available <!-- null -->"

    geometry_type = project.get("geometry_type", "Unknown")

    # Timestamps
    mirror_update = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    return PROJECT_TEMPLATE.format(
        tip=tip,
        description=description.replace(" <!-- null -->", ""),  # Clean for header
        spot_id=spot_id,
        route=route,
        counties=counties,
        divisions=divisions,
        mpo_rpo=mpo_rpo,
        category=category,
        mode=mode,
        project_cost=project_cost,
        row_year=row_year,
        construction_year=construction_year,
        comment=comment,
        construction_section=construction_section,
        progloc_section=progloc_section,
        coordinates=coordinates,
        geometry_type=geometry_type,
        ncdot_update=pull_timestamp[:10] if pull_timestamp else "Unknown",
        mirror_update=mirror_update,
    )


def main():
    """Generate markdown files for all STIP projects."""
    logger.info("=" * 60)
    logger.info("STIP Markdown Generation Started")
    logger.info("=" * 60)

    # Load raw data
    logger.info("Loading raw JSON data...")
    points_data = load_json(POINTS_FILE)
    lines_data = load_json(LINES_FILE)
    metadata = load_json(METADATA_FILE)

    pull_timestamp = metadata.get("last_pull_completed", "")
    logger.info(f"Data from pull: {pull_timestamp[:19] if pull_timestamp else 'Unknown'}")

    # Load construction data
    tip_to_contracts = load_construction_data()

    # Load ProgLoc progress report data
    tip_to_progloc = load_progloc_data()

    # Merge projects
    logger.info("Merging points and lines by TIP number...")
    projects = merge_projects(points_data, lines_data)
    logger.info(f"Found {len(projects)} unique projects")

    # Track cross-references for multi-county projects
    cross_references = {}  # county -> list of (TIP, primary_county)

    # Track statistics
    stats = {
        "total_projects": len(projects),
        "files_created": 0,
        "multi_county_projects": 0,
        "cross_references_created": 0,
        "counties_with_projects": set(),
        "projects_with_construction": 0,
        "projects_with_progloc": 0,
        "errors": 0,
    }

    # Generate markdown files
    logger.info("Generating markdown files...")

    for tip, project in sorted(projects.items()):
        attrs = project["attributes"]
        counties_str = attrs.get("Counties", "")
        counties = parse_counties(counties_str)

        if not counties:
            logger.warning(f"No valid county for {tip}, skipping")
            stats["errors"] += 1
            continue

        # Primary county is the first one listed
        primary_county = counties[0]
        stats["counties_with_projects"].add(primary_county)

        # Track multi-county projects
        if len(counties) > 1:
            stats["multi_county_projects"] += 1
            # Add cross-references for secondary counties
            for secondary_county in counties[1:]:
                if secondary_county not in cross_references:
                    cross_references[secondary_county] = []
                cross_references[secondary_county].append({
                    "tip": tip,
                    "primary_county": primary_county,
                    "description": attrs.get("Description", ""),
                    "route": attrs.get("Route", ""),
                })
                stats["cross_references_created"] += 1
                stats["counties_with_projects"].add(secondary_county)

        # Generate markdown
        try:
            markdown = generate_project_markdown(
                project, pull_timestamp, tip_to_contracts, tip_to_progloc
            )

            # Track construction status
            if "<!-- no-construction -->" not in markdown:
                stats["projects_with_construction"] += 1
            if "<!-- no-progloc -->" not in markdown:
                stats["projects_with_progloc"] += 1

            # Write to file
            county_dir = COUNTIES_DIR / primary_county
            county_dir.mkdir(parents=True, exist_ok=True)

            filename = sanitize_filename(tip) + ".md"
            filepath = county_dir / filename

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(markdown)

            stats["files_created"] += 1

        except Exception as e:
            logger.error(f"Error generating {tip}: {e}")
            stats["errors"] += 1

    # Save cross-references for build_indexes.py to use
    save_json(cross_references, CROSS_REF_FILE)
    logger.info(f"Saved cross-references to {CROSS_REF_FILE}")

    # Summary
    logger.info("=" * 60)
    logger.info("Generation Complete!")
    logger.info(f"  Total projects: {stats['total_projects']}")
    logger.info(f"  Files created: {stats['files_created']}")
    logger.info(f"  Multi-county projects: {stats['multi_county_projects']}")
    logger.info(f"  Cross-references: {stats['cross_references_created']}")
    logger.info(f"  Counties with projects: {len(stats['counties_with_projects'])}")
    logger.info(f"  Projects with construction data: {stats['projects_with_construction']}")
    logger.info(f"  Projects with ProgLoc data: {stats['projects_with_progloc']}")
    logger.info(f"  Errors: {stats['errors']}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
