# Phase 2: STIP Core Data Pull & Markdown Generation

## Objective
Build the core data pipeline: pull STIP data, generate project markdown files, and create indexes.

---

## Step 1: Build pull_stip.py

### Tasks
- [x] Create pull_stip.py with API client
- [x] Implement pagination (loop until < 1000 results)
- [x] Add 1-2 second delay between requests
- [x] Implement error handling (log failures, don't overwrite on error)
- [x] Pull both points (Layer 0) and lines (Layer 1)
- [x] Save to raw/stip/stip_points_full.json and stip_lines_full.json
- [x] Save metadata to raw/stip/last_pull.json (timestamp, record counts)
- [x] Test with full statewide pull

### Error Handling Requirements
- Retry failed requests up to 3 times with exponential backoff
- If all retries fail, log error and abort (don't save partial data)
- Never overwrite existing raw JSON with empty/partial results

### Notes/Lessons Learned
- **Completed 2026-02-03**: Full statewide pull successful
- **Results**: 1119 points + 1243 lines = 2362 total features
- **Duration**: ~13 seconds (pagination handled 2 batches per layer)
- **Validation**: U-5606 confirmed in stip_lines_full.json
- **File sizes**: Lines ~22MB, Points ~850KB (lines have geometry data)
- **Key decision**: Wrapped features in metadata dict for traceability (source URL, timestamp)

---

## Step 2: Build generate_markdown.py

### Tasks
- [x] Create project file template as Python string
- [x] Parse raw JSON and extract required fields
- [x] Handle missing fields gracefully (show "Not Available")
- [x] Generate one markdown file per TIP number
- [x] Organize into counties/{county-name}/ folders
- [x] Handle multi-county projects (TBD: which county folder?)
- [x] Add mirror metadata (timestamps, source, status)

### Template Fields to Map
From STIP data:
- TIP/SPOT ID → SPOTID
- Description → DESCRIPTION
- County → COUNTY (may be comma-separated for multi-county)
- Route → ROUTE
- Division → (TBD from field discovery)
- Planning Org → (TBD from field discovery)
- STI Category → (TBD from field discovery)
- Coordinates → geometry.x, geometry.y (with outSR=4326)
- Funding phases → (TBD from field discovery)

### Geometry Handling (DECIDED)
- Merge Points (Layer 0) and Lines (Layer 1) by TIP number
- Store centroid coordinates (5 decimal places = ~1m precision)
- If line geometry exists, calculate centroid from line
- If only point exists, use point coordinates

### Null Field Handling (DECIDED)
Use HTML comments for machine-readable null markers:
```markdown
- **Contractor:** Not Available <!-- null -->
```
This helps AI parsers distinguish missing data from actual "Not Available" values

### Multi-County Handling (DECIDED)
**Decision: Option A** - Single source of truth
- Project file lives in the FIRST listed county
- Project file lists ALL counties it spans
- Other county indexes include a cross-reference row:
  ```
  | R-2500 | Highway widening | US-264 | → See [Pitt County](../pitt/R-2500.md) |
  ```
- Ensures congruent experience across all counties

### Notes/Lessons Learned
- **Completed 2026-02-03**: All 2,356 projects generated successfully
- **Merging**: 2,362 features → 2,356 unique TIPs (some in both points & lines)
- **Multi-county**: 119 projects span multiple counties, generating 166 cross-refs
- **Coverage**: All 100 NC counties have at least one project
- **Cross-refs**: Saved to `raw/stip/cross_references.json` for build_indexes.py
- **U-5606 validated**: Pitt County, Dickinson Ave, coordinates 35.60547, -77.38344
- **Cost field**: API returns thousands (18365 = $18,365,000)

---

## Step 3: Build build_indexes.py

### Tasks
- [x] Generate counties/{county}/index.md for each county
- [x] Generate top-level index.md with statewide summary
- [x] Calculate project counts per county
- [x] Link to individual project files
- [x] Group projects by status (Active Construction, Planned, Completed/Removed)

### Index Generation Requirements
- Sort counties alphabetically in statewide index
- Sort projects by TIP number within county indexes
- Include last updated timestamp in each index

### Notes/Lessons Learned
- **Completed 2026-02-03**: All 100 county indexes + statewide index generated
- **Status categories**: Under Construction (646), Right-of-Way (296), Planned (1,276), Completed (138)
- **Status derived from COMMENT field**: Pattern matching for "UNDER CONSTRUCTION", "COMPLETE", "RIGHT-OF-WAY"
- **Cross-references**: 64 counties have cross-ref sections showing multi-county projects
- **Visual indicators**: Emojis for status (🚧/📋/📅/✅) and multi-county (🗺️)
- **Statewide index**: Shows (+N) for cross-reference counts per county

---

## Step 4: Validate Pitt County Data

### Tasks
- [x] Run full pipeline for Pitt County specifically
- [x] Locate U-5606 in generated files
- [x] Verify all fields populated correctly
- [x] Spot-check coordinates on a map
- [x] Compare against NCDOT's STIP map for accuracy
- [x] Fix any issues found

### Validation Checklist
- [x] U-5606 file exists at counties/pitt/U-5606.md
- [x] Description matches NCDOT records ("NC 11 to Reade Circle. Improve roadway.")
- [x] Coordinates plot to correct location (35.60547, -77.38344 = Dickinson Ave, Greenville)
- [x] Funding data present (or marked N/A if not in API) - Cost: $18,365,000
- [x] Index includes U-5606 with correct link

### Notes/Lessons Learned
- **Completed 2026-02-03**: All validation checks passed
- **U-5606 verified**: File at counties/pitt/U-5606.md with all expected fields
- **Coordinates correct**: 35.60547, -77.38344 plots to Dickinson Avenue in Greenville
- **All 36 Pitt County links valid**: Every project in index links to existing file
- **Status shown correctly**: "🚧 Under Construction" in index, "UNDER CONSTRUCTION." in detail

---

## Completion Criteria

Phase 2 is complete when:
1. pull_stip.py successfully pulls all statewide STIP data
2. generate_markdown.py creates individual project files
3. build_indexes.py creates county and statewide indexes
4. Pitt County / U-5606 validation passes

---

## Next Session Prompt

```
Review ROADMAP.md and plan-phase2-stip-core.md in ~/Documents/Python-Projects/ncdot-transportation-mirror.
Continue with Phase 2, starting from the first unchecked task.
```
