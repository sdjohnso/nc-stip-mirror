#!/usr/bin/env python3
"""
API Schema Discovery Script

Queries NCDOT ArcGIS API metadata endpoints to document field schemas.
Outputs results to docs/field_schemas.md.
"""

import json
import time
from datetime import datetime
from pathlib import Path

import requests

from config import (
    STIP_POINTS,
    STIP_LINES,
    CONSTRUCTION_POINTS,
    CONSTRUCTION_LINES,
    CONSTRUCTION_TABLE,
    AADT_STATIONS,
    REQUEST_DELAY,
    DEFAULT_OUT_SR,
)

# Output file
OUTPUT_FILE = Path(__file__).parent.parent / "docs" / "field_schemas.md"


def fetch_layer_metadata(url: str) -> dict:
    """Fetch layer metadata from ArcGIS REST endpoint."""
    response = requests.get(f"{url}?f=json", timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_sample_records(url: str, count: int = 2) -> list:
    """Fetch sample records from a layer."""
    params = {
        "where": "1=1",
        "outFields": "*",
        "outSR": DEFAULT_OUT_SR,
        "resultRecordCount": count,
        "f": "json",
    }
    response = requests.get(f"{url}/query", params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data.get("features", [])


def format_field_table(fields: list) -> str:
    """Format fields as a markdown table."""
    lines = [
        "| Field Name | Type | Alias | Length |",
        "|------------|------|-------|--------|",
    ]
    for field in fields:
        name = field.get("name", "")
        ftype = field.get("type", "").replace("esriFieldType", "")
        alias = field.get("alias", "")
        length = field.get("length", "")
        lines.append(f"| {name} | {ftype} | {alias} | {length} |")
    return "\n".join(lines)


def format_sample_record(feature: dict) -> str:
    """Format a sample record for display."""
    attrs = feature.get("attributes", {})
    lines = ["```json", json.dumps(attrs, indent=2, default=str), "```"]
    return "\n".join(lines)


def discover_layer(name: str, url: str) -> str:
    """Discover schema for a single layer."""
    print(f"  Querying {name}...")

    output = [f"### {name}\n"]
    output.append(f"**URL:** `{url}`\n")

    try:
        # Get metadata
        metadata = fetch_layer_metadata(url)

        # Layer info
        output.append(f"**Name:** {metadata.get('name', 'Unknown')}")
        output.append(f"**Type:** {metadata.get('type', 'Unknown')}")
        output.append(
            f"**Geometry Type:** {metadata.get('geometryType', 'None (Table)')}"
        )
        output.append(f"**Max Record Count:** {metadata.get('maxRecordCount', 'N/A')}")
        output.append("")

        # Fields table
        fields = metadata.get("fields", [])
        if fields:
            output.append("#### Fields\n")
            output.append(format_field_table(fields))
            output.append("")

        time.sleep(REQUEST_DELAY)

        # Sample records
        samples = fetch_sample_records(url)
        if samples:
            output.append("#### Sample Record\n")
            output.append(format_sample_record(samples[0]))
            output.append("")

    except requests.RequestException as e:
        output.append(f"**ERROR:** Failed to fetch - {e}\n")
    except Exception as e:
        output.append(f"**ERROR:** {e}\n")

    return "\n".join(output)


def main():
    """Main discovery routine."""
    print("NCDOT API Schema Discovery")
    print("=" * 40)

    layers = [
        ("STIP Points (Layer 0)", STIP_POINTS),
        ("STIP Lines (Layer 1)", STIP_LINES),
        ("Active Construction Points (Layer 0)", CONSTRUCTION_POINTS),
        ("Active Construction Lines (Layer 1)", CONSTRUCTION_LINES),
        ("Active Construction Table (Layer 3)", CONSTRUCTION_TABLE),
        ("AADT Stations", AADT_STATIONS),
    ]

    output = [
        "# NCDOT API Field Schemas",
        "",
        f"*Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        "",
        "This document contains field definitions and sample data from all NCDOT APIs",
        "used by this mirror project.",
        "",
        "---",
        "",
        "## Table of Contents",
        "",
    ]

    # TOC
    for name, _ in layers:
        anchor = name.lower().replace(" ", "-").replace("(", "").replace(")", "")
        output.append(f"- [{name}](#{anchor})")

    output.append("")
    output.append("---")
    output.append("")

    # Process each layer
    for name, url in layers:
        output.append(discover_layer(name, url))
        output.append("---")
        output.append("")
        time.sleep(REQUEST_DELAY)

    # Write output
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(output))
    print(f"\nOutput written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
