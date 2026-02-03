# NC STIP Mirror - Project Instructions

**Repository**: `nc-stip-mirror` (public, GitHub Pages enabled)

## Project Overview

This is a GitHub-hosted mirror of all North Carolina Department of Transportation (NCDOT) transportation projects statewide. It's a **MIRROR**, not an analytics product - we reflect existing public data without adding analysis or commentary.

## Project Philosophy

This mirror exists to provide **straight, true, unadulterated public data** that anyone - especially AI assistants - can easily access and use. In a future where AI needs trustworthy information sources, this channel provides exactly that: faithfully mirrored government data with no editorializing.

## Core Principles

1. **Mirror, Not Transform** - Every file reflects NCDOT data faithfully. No analysis, no derived insights.
2. **AI-First Design** - Structured for easy AI consumption (consistent templates, machine-readable markers).
3. **Never Lose Data** - Projects that disappear from APIs get marked as removed, not deleted.
4. **Transparency** - Every file includes timestamps for NCDOT's last update AND our last pull.
5. **Attribution** - NCDOT is prominently credited as the data source everywhere.

## Data Sources

All public, no authentication required:

| Source | URL Base | Update Frequency | Purpose |
|--------|----------|------------------|---------|
| STIP ArcGIS | `gis11.services.ncdot.gov/arcgis/rest/services/NCDOT_STIP/MapServer` | Monthly | Planning & funding |
| Active Construction | `gis11.services.ncdot.gov/arcgis/rest/services/NCDOT_RoadProjects/NCDOT_ActiveConstructionProjects/MapServer` | Nightly (HiCAMS) | Construction status |
| AADT Stations | `services.arcgis.com/.../NCDOT_AADT_Stations/FeatureServer` | Annually | Traffic counts |
| ProgLoc | `apps.ncdot.gov/traffictravel/progloc/` | Varies | Progress reports |
| TIMS | `eapps.ncdot.gov/services/traffic-prod/v1/` | Real-time | Incidents (optional) |

## Critical Technical Notes

- **Pagination Required**: MaxRecordCount=1000 on ArcGIS APIs. Must loop with `resultOffset`.
- **Coordinate System**: ALWAYS use `outSR=4326` for WGS84 lat/long. Never store NC State Plane.
- **Rate Limiting**: 1-2 second delay between API requests. These are government servers.
- **Error Handling**: Never overwrite existing data with empty data on API failure.
- **County Names**: Normalize to lowercase for folders, Title Case for display.

## File Structure Conventions

```
counties/{county-name}/index.md     # County project list
counties/{county-name}/{TIP}.md     # Individual project files
traffic-counts/{county-name}.md     # AADT data by county
raw/{source}/                       # Raw JSON from APIs (source of truth)
scripts/                            # Python automation scripts
```

## Testing & Validation

- Use Pitt County and TIP U-5606 as the validation baseline
- Verify coordinates render correctly on a map
- Cross-reference TIP numbers across data sources

## GitHub Actions Schedule

- **Daily 6 AM EST**: Active construction (HiCAMS nightly refresh)
- **Weekly Sunday**: STIP and ProgLoc data
- **Monthly 1st**: AADT and high-profile project URLs

## Do NOT

- Add analysis or commentary
- Create summary statistics beyond simple counts
- Delete projects that disappear (mark as removed instead)
- Store NC State Plane coordinates
- Commit empty data on API failures
