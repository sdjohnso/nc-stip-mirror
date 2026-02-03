# Phase 1: Foundation & API Discovery

## Objective
Set up project infrastructure and discover exact API field schemas before building parsers.

---

## Step 1: Project Structure & Environment

### Tasks
- [x] Create full directory structure per spec
- [x] Initialize Python virtual environment
- [x] Create requirements.txt with dependencies
- [x] Initialize git repository

### Directory Structure to Create
```
ncdot-transportation-mirror/
├── raw/stip/
├── raw/active-construction/
├── raw/aadt/
├── raw/progloc/
├── counties/
├── traffic-counts/
├── scripts/
└── .github/workflows/
```

### Dependencies Needed
Keep lightweight for GitHub Actions:
- `requests` - API calls (simple, well-supported)
- `openpyxl` - Excel file reading (for ProgLoc if needed)
- No pandas - use built-in json/csv modules where possible

### Environment
- Python 3.11+
- Standard venv (not poetry/uv/conda)
- GitHub Actions runner: ubuntu-latest

### Notes/Lessons Learned
- Plan files moved to `plans/` directory for organization
- Using Python 3.14 (latest available on system)
- Added docs/ directory (not in original spec) for field_schemas.md
- .gitignore created; raw/ is tracked as source-of-truth

---

## Step 2: Config Module

### Tasks
- [x] Create scripts/config.py
- [x] Add all API URLs as constants
- [x] Add complete list of all 100 NC counties (lowercase for folders, Title Case for display)
- [x] Add field mapping placeholders (to be filled after API discovery)

### NC Counties Reference
Complete - all 100 NC counties verified.

### Notes/Lessons Learned
- "New Hanover" handled as two words (key: "new hanover")
- "McDowell" needs proper capitalization in display
- Field mapping placeholders ready for API discovery step

---

## Step 3: API Metadata Discovery

### Tasks
- [x] Query STIP MapServer/0 metadata (points layer)
- [x] Query STIP MapServer/1 metadata (lines layer)
- [x] Query Active Construction MapServer/0 metadata (points)
- [x] Query Active Construction MapServer/1 metadata (lines)
- [x] Query Active Construction MapServer/3 metadata (HiCAMS table)
- [x] Query AADT FeatureServer/0 metadata
- [x] Document all field names, types, and sample values
- [x] Create field_schemas.md with complete documentation

### API Metadata Endpoints
- STIP Points: `https://gis11.services.ncdot.gov/arcgis/rest/services/NCDOT_STIP/MapServer/0?f=json`
- STIP Lines: `https://gis11.services.ncdot.gov/arcgis/rest/services/NCDOT_STIP/MapServer/1?f=json`
- Construction Points: `https://gis11.services.ncdot.gov/arcgis/rest/services/NCDOT_RoadProjects/NCDOT_ActiveConstructionProjects/MapServer/0?f=json`
- Construction Lines: `https://gis11.services.ncdot.gov/arcgis/rest/services/NCDOT_RoadProjects/NCDOT_ActiveConstructionProjects/MapServer/1?f=json`
- Construction Table: `https://gis11.services.ncdot.gov/arcgis/rest/services/NCDOT_RoadProjects/NCDOT_ActiveConstructionProjects/MapServer/3?f=json`
- AADT: `https://services.arcgis.com/NuWFvHYDMVmmxMeM/ArcGIS/rest/services/NCDOT_AADT_Stations/FeatureServer/0?f=json`

### Discovery Script
Created `scripts/discover_api_schemas.py` - auto-generates docs/field_schemas.md

### Notes/Lessons Learned
- **STIP API**: Simple field names (`TIP`, `Counties`, `Description`). Counties is Title Case.
- **Construction API**: Fully qualified field names (`GdbGisuPub.HICAMS.ActiveContractsMap.TIP`). Uses `CountyNumber` (integer) instead of name.
- **Layer 3 (Unmapped)**: Contains construction projects without geographic coordinates - need special handling
- **AADT**: Has yearly columns (AADT_2002 through AADT_2022). Blank years stored as " " (space)
- Max record count is 1000 for all APIs - pagination required

---

## Step 4: Validate API Access & Test Queries

### Tasks
- [x] Test STIP query with Pitt County filter
- [x] Test pagination (verify we can get all records)
- [x] Test coordinate transformation (outSR=4326)
- [x] Find U-5606 in results to validate data quality
- [x] Test Active Construction API similarly
- [x] Document any API quirks or issues discovered

### Test Queries
```
# STIP Pitt County
https://gis11.services.ncdot.gov/arcgis/rest/services/NCDOT_STIP/MapServer/0/query?where=COUNTY%3D%27PITT%27&outFields=*&outSR=4326&f=json

# STIP Pagination Test
https://gis11.services.ncdot.gov/arcgis/rest/services/NCDOT_STIP/MapServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json&resultOffset=0&resultRecordCount=1000
```

### Notes/Lessons Learned
- **U-5606 validation**: Found in STIP Lines (not points) and Active Construction
  - STIP: "UNDER CONSTRUCTION", Pitt County
  - Construction: Contract C204070, 85.22% complete
- **County field**: STIP uses "Counties" (Title Case name), Construction uses CountyNumber (74 = Pitt)
- **Pagination**: 1119 points + 1243 lines total. `exceededTransferLimit: true` when >1000
- **Geometry**: Must query BOTH points and lines layers to get all projects
- **Coordinates**: WGS84 working correctly (outSR=4326)

---

## Step 5: ProgLoc Excel Export Test

### Tasks
- [x] Attempt Excel export from ProgLoc
- [x] If successful, examine structure and fields
- [x] If blocked, research alternative approaches (scraping?)
- [x] Document findings

### Test URL
`https://apps.ncdot.gov/traffictravel/progloc/ExportProgLocToExcel.aspx`

### Notes/Lessons Learned
- **Export works!** No authentication required, returns XLSX file
- **778 active construction projects** (as of 2026-02-03)
- **22 columns** of rich data:
  1. Contract Number, Division, County, TIP#, Tier
  2. Route, Location Description, Contract Amount
  3. Contractor info, Federal Aid Number
  4. NCDOT Contact info
  5. Letting Date, Work Began Date, Completion Date, Revised Completion Date
  6. Construction Progress, Completion Percent
  7. Latest Payment info
- **Headers in row 2** (row 1 is empty)
- **U-5606 found**: Contract C204070, Pitt County, SR-1598 (Dickinson Ave), $15.7M contract

---

## Completion Criteria

Phase 1 is complete when:
1. Directory structure exists
2. Python environment is set up with dependencies
3. config.py has all API URLs and county list
4. All API field schemas are documented in field_schemas.md
5. Test queries confirm APIs are accessible and data is valid
6. ProgLoc approach is determined

---

## Next Session Prompt

```
Review ROADMAP.md and plans/phase2-stip-core.md in ~/Documents/Python-Projects/ncdot-transportation-mirror.
Phase 1 is complete. Begin Phase 2 (STIP Core), starting from Step 1.
```
