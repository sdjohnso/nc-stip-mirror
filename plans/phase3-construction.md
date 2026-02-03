# Phase 3: Active Construction Data Integration

## Objective
Pull active construction data and merge it into existing project files by TIP number.

**STATUS: COMPLETE** (2026-02-03)

---

## Step 1: Build pull_active_construction.py

### Tasks
- [x] Create API client similar to pull_stip.py
- [x] Pull Layer 0 (Points), Layer 1 (Lines), Layer 3 (HiCAMS Table)
- [x] Implement pagination and rate limiting
- [x] Save to raw/active-construction/
- [x] Save last_pull.json with timestamp and record counts

### Data Quality Considerations
- HiCAMS data updates nightly - timestamps matter
- Some contracts may not have TIP references (skip these - see orphan decision below)
- TipReference field may contain multiple TIPs (comma-separated?)

### Update Frequency (DECIDED)
- **Daily**: Pull active construction data (HiCAMS attributes like completion %)
- **Weekly**: Pull STIP, ProgLoc, and construction spatial data
- **Monthly**: Pull AADT and high-profile project URLs

### Notes/Lessons Learned
- Initial pull: 234 points, 164 lines, 61 HiCAMS table records
- Layer 3 (HiCAMS table) is non-spatial - don't request outSR parameter
- Script handles is_table parameter to skip spatial reference for tables

---

## Step 2: Cross-Reference TIP Numbers

### Tasks
- [x] Build mapping of TIP → construction contract details
- [x] Handle TipReference field format (may need parsing)
- [x] Handle contracts without TIP references (orphans)
- [x] Log any TIPs in construction that weren't in STIP data

### TIP Matching Logic
1. Parse TipReference field from construction data
2. Match to TIP field from STIP data (not SPOTID - that's internal)
3. One TIP may have multiple contracts
4. One contract may reference multiple TIPs

### Notes/Lessons Learned
- TipReference format: comma-separated, space-padded (e.g., " C-5606C   , C-5703    ")
- Need to split by comma and strip whitespace
- STIP has TIP field (human-readable like "R-5734A") and SPOTID (internal like "H090749-A")
- Construction TipReference matches STIP TIP field, not SPOTID
- Construction TIPs often have suffixes (A, B, C) for contract phases
- Match on both exact TIP and base TIP (strip trailing letter suffix)
- Results: 60 unique construction TIPs, 26 match STIP directly/via base, 34 orphans (BO- bond projects, etc.)

---

## Step 3: Update generate_markdown.py

### Tasks
- [x] Add construction status section to template
- [x] Merge construction data into project files during generation
- [x] Show contract number, status, completion %, contractor (if available)
- [x] Handle multiple contracts per project
- [x] Mark "Not Under Construction" for projects without active contracts

### Construction Section Fields
From Active Construction API:
- Contract Number → ContractNumber
- Contract Status → ContractStatus
- Completion % → CompletionPercent
- Contract Active Date → ContractActiveDate
- Contract Nickname → ContractNickname
- Contractor → Not available in HiCAMS table (would need ProgLoc)

### Notes/Lessons Learned
- Added `load_construction_data()` function to build TIP → contracts mapping
- Added `format_construction_section()` to generate markdown for construction status
- Uses HTML comment markers for machine-readable status (<!-- no-construction -->)
- 90 projects have construction data (more than direct matches due to base TIP matching)

---

## Step 4: Handle Orphan Construction Projects

### Tasks
- [x] Decide how to handle contracts with no TIP reference
- [x] Option B selected: Skip them (they're not in STIP scope)

### Decision: SKIP Orphan Projects
Construction projects without TIP numbers are outside STIP scope.
- This is a STIP mirror, not a general construction mirror
- Skip contracts with no TipReference
- Document in README that mirror covers STIP projects only
- Keeps the data model clean and consistent

### Notes/Lessons Learned
- 34 construction TIPs not in STIP (mostly BO- prefix = Build NC Bond projects)
- These are bond-funded projects tracked separately from STIP
- Correctly excluded per the "mirror, not transform" principle

---

## Step 5: Update Indexes

### Tasks
- [x] Update build_indexes.py to show construction status
- [x] Add "Active Construction" section to county indexes
- [x] Show completion percentage in index tables
- [x] Count active construction projects separately

### Notes/Lessons Learned
- Added new status: "Active Construction" (distinct from STIP's "Under Construction")
- "Active Construction" = has active HiCAMS contract with real-time tracking
- "Under Construction" = STIP says under construction but no HiCAMS contract
- Completion % shown in project table (e.g., "Active Construction (48%)")
- Statewide: 90 Active Construction, 601 Under Construction (from STIP comments)
- Top counties: Gaston (13), Cumberland (10), Durham (9) active construction projects

---

## Completion Criteria

Phase 3 is complete when:
1. [x] pull_active_construction.py works correctly
2. [x] TIP cross-referencing merges construction data
3. [x] Project files show construction status
4. [x] Indexes reflect construction status
5. [x] Orphan contract handling is decided and implemented

---

## Files Created/Modified

**New Files:**
- `scripts/pull_active_construction.py` - API client for construction data
- `raw/active-construction/construction_points.json`
- `raw/active-construction/construction_lines.json`
- `raw/active-construction/construction_table.json`
- `raw/active-construction/last_pull.json`

**Modified Files:**
- `scripts/generate_markdown.py` - Added construction section to project template
- `scripts/build_indexes.py` - Added Active Construction status tracking

---

## Next Phase

Phase 4: ProgLoc Integration

```
Review ROADMAP.md and plans/phase4-supplementary.md in ~/Documents/Python-Projects/ncdot-transportation-mirror.
Begin Phase 4: ProgLoc integration.
```
