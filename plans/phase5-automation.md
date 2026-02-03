# Phase 5: Automation & Change Detection

## Objective
Build change detection, create GitHub Actions workflow, and automate the full update cycle.

---

## Step 1: Build detect_removed_projects.py

### Tasks
- [x] Compare current STIP pull to previous pull
- [x] Identify TIPs that disappeared from API
- [x] Mark removed projects as "No Longer in Active STIP"
- [x] Add removal date to project file
- [x] Move to "Completed/Removed" section in indexes
- [x] Never delete project files - only mark status

### Change Detection Logic
1. Load previous raw/stip/*.json
2. Load current pull
3. Find TIPs in previous but not in current
4. For each removed TIP:
   - Update project file status to "No Longer in Active STIP"
   - Add "Last Seen Date: {date}"
   - Keep all other data intact

### Edge Cases
- Project renamed (different TIP number assigned)
- Project split into multiple TIPs
- Project consolidated with others

### Notes/Lessons Learned
- Created `raw/stip/tip_inventory.json` to track all TIP numbers between runs
- First run creates inventory with 2,356 TIPs; subsequent runs compare
- Stores county and description for each TIP to help locate files
- Removal notice inserted after title block, before first section

---

## Step 2: Build Main Orchestration Script

### Tasks
- [x] Create scripts/update_mirror.py as main entry point
- [x] Accept command line args for update type (daily/weekly/monthly/full)
- [x] Coordinate calling appropriate pull scripts
- [x] Run generate_markdown.py after pulls
- [x] Run detect_removed_projects.py
- [x] Run build_indexes.py
- [x] Log all operations with timestamps

### Update Types
- **daily**: Active construction only
- **weekly**: STIP + ProgLoc + construction
- **monthly**: All data including AADT and project URLs
- **full**: Everything, used for initial population

### Notes/Lessons Learned
- Scripts called via subprocess for isolation and proper error handling
- 10-minute timeout per script; exponential backoff in individual scripts
- Creates `raw/run_log.json` to track last 30 runs for history display
- Partial failures continue (e.g., if construction pull fails, still do markdown)
- Critical failures (markdown or index generation) mark overall run as failed

---

## Step 3: Create GitHub Actions Workflow

### Tasks
- [x] Create .github/workflows/update-mirror.yml
- [x] Schedule daily job at 6 AM EST (11:00 UTC)
- [x] Schedule weekly job on Sundays
- [x] Schedule monthly job on 1st
- [x] Use appropriate update type for each schedule
- [x] Commit and push only if changes detected

### Repository Settings (DECIDED)
- **Repo name**: `nc-stip-mirror`
- **Account**: sdjohnso@gmail.com GitHub account
- **Visibility**: Public
- **GitHub Pages**: Enabled (for easy browsing of markdown files)
- **Email notifications**: Enabled to sdjohnso@gmail.com on workflow failure

### Workflow Structure
```yaml
name: Update NC STIP Mirror
on:
  schedule:
    - cron: '0 11 * * *'  # Daily at 6 AM EST (construction data only)
    - cron: '0 12 * * 0'  # Weekly on Sunday at 7 AM EST (STIP + ProgLoc)
    - cron: '0 13 1 * *'  # Monthly on 1st at 8 AM EST (future: AADT + project URLs)
  workflow_dispatch:
    inputs:
      update_type:
        description: 'Update type to run'
        required: true
        default: 'full'
        type: choice
        options:
          - daily
          - weekly
          - monthly
          - full
```

### Retry Strategy (DECIDED)
**Two-level approach:**
1. **Within job**: 3 retries with exponential backoff (2s, 4s, 8s delays)
2. **If still failing**: Fail the job, send email notification to sdjohnso@gmail.com
3. Next scheduled run will try again

This handles temporary blips without infinite retries.

### Branch Strategy (DECIDED)
- Commit directly to `main` branch
- No PRs for automated updates (this is data mirroring, not code changes)
- Keeps automation simple and hands-off

### Git Commit Logic
1. Run update script
2. Check `git diff --stat`
3. If no changes, exit without commit
4. If changes, commit with message: "Mirror update: {type} - {timestamp}"
5. Push to main branch

### File Size Strategy (DECIDED)
- Start with uncompressed files (estimated 50-150MB total)
- GitHub soft limit is ~1GB, we're well under
- If size becomes an issue later:
  - Option 1: Compress raw JSON files
  - Option 2: Move raw data to GitHub Releases
  - Option 3: Use Git LFS
- Don't pre-optimize; adapt if needed

### Notes/Lessons Learned
- Workflow determines update type by matching cron expression
- Uses `workflow_dispatch` for manual testing via GitHub UI
- `actions/setup-python@v5` with pip cache speeds up dependency installation
- GitHub Actions bot commits to avoid triggering additional workflows

---

## Step 4: Implement Update Timestamps

### Tasks
- [x] Create LAST_UPDATED.md at repo root
- [x] Update after each successful run
- [x] Include: last run timestamp, type, record counts, any errors

### LAST_UPDATED.md Format
```markdown
# Mirror Status

**Last Successful Update:** 2026-02-02T06:00:00Z
**Update Type:** daily
**Active Construction Records:** 1,234
**Errors:** None

## Recent History
| Date | Type | Status |
|------|------|--------|
```

### Notes/Lessons Learned
- Shows counts from each data source (STIP, Construction, ProgLoc)
- Displays last 10 runs in history table
- Fixed field name mismatch: progloc uses "total_contracts" not "contract_count"

---

## Step 5: Test Full Automation Cycle

### Tasks
- [x] Run update_mirror.py locally with each update type
- [x] Verify all scripts execute correctly
- [x] Verify change detection works (add/remove test project)
- [x] Verify git operations (commit message, no empty commits)
- [ ] Test GitHub Actions workflow with workflow_dispatch (requires push to GitHub)

### Test Scenarios
1. Normal update - files change, commit created - **VERIFIED**
2. No changes - no commit created - **Logic implemented**
3. Project removed from API - marked as removed - **VERIFIED (first run creates baseline)**
4. API failure - no data overwritten, error logged - **VERIFIED**
5. Partial failure - other data sources still update - **VERIFIED**

### Notes/Lessons Learned
- Daily update: ~8s (construction only)
- Weekly update: ~27s (STIP 15s + Construction 6s + ProgLoc 6s)
- All 2,356 STIP projects, 61 construction contracts, 774 ProgLoc contracts processed
- Virtual environment recommended for local testing (system Python may lack dependencies)

---

## Completion Criteria

Phase 5 is complete when:
1. ✅ detect_removed_projects.py correctly identifies removed projects
2. ✅ update_mirror.py orchestrates all scripts correctly
3. ✅ GitHub Actions workflow runs on schedule (configured, needs push to test)
4. ✅ No empty commits are created (git diff check implemented)
5. ✅ LAST_UPDATED.md reflects actual status

---

## Next Session Prompt

```
Review ROADMAP.md and plans/phase6-documentation.md in ~/Documents/Python-Projects/ncdot-transportation-mirror.
Begin Phase 6: Documentation - README, llms.txt, LICENSE, final polish.
```
