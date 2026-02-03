# NCDOT Transportation Mirror - Roadmap

## Active Plans

### In Progress (WIP Limit: 2)
1. [ ] `plans/phase6-documentation.md` - README, llms.txt, LICENSE, final polish

### Completed
- [x] `plans/phase1-foundation.md` - Project infrastructure and API discovery
- [x] `plans/phase2-stip-core.md` - STIP data pull and markdown generation (2,356 projects)
- [x] `plans/phase3-construction.md` - Active construction data integration (90 projects with HiCAMS data)
- [x] `plans/phase4-supplementary.md` - ProgLoc integration (267 projects with progress reports)
- [x] `plans/phase5-automation.md` - GitHub Actions and change detection

### Queued (Priority Order)
_None - core implementation complete_

### Future Enhancements (Optional - After Core Is Stable)
- [ ] `plans/optional-aadt.md` - AADT traffic count stations (~48K stations, annual data)
- [ ] `plans/optional-project-urls.md` - High-profile project page URL mappings
- [ ] `plans/optional-tims.md` - Real-time traffic incidents (volatile data, different model)

---

## Phase Overview

### Phase 1: Foundation & API Discovery
- Create directory structure
- Set up Python environment and dependencies
- Build config.py with all API URLs and NC county list
- Query all API metadata endpoints to discover exact field names
- Document findings for parser development

### Phase 2: STIP Core (Primary Data Source)
- Build pull_stip.py with pagination and error handling
- Build generate_markdown.py for project file template
- Build build_indexes.py for county and statewide indexes
- Validate against Pitt County / U-5606

### Phase 3: Active Construction Integration
- Build pull_active_construction.py
- Cross-reference TIP numbers to merge construction status into project files
- Handle projects in construction but not in STIP (edge case)

### Phase 4: ProgLoc Integration (COMPLETE)
- ProgLoc Excel export works - direct URL download
- 774 contracts with 406 unique TIPs parsed
- 267 STIP projects enriched with contractor, amounts, completion %, dates

### Phase 5: Automation & Change Detection (COMPLETE)
- Built detect_removed_projects.py with TIP inventory tracking
- Created update_mirror.py orchestrator (daily/weekly/monthly/full modes)
- GitHub Actions workflow with 3 schedules + manual dispatch
- LAST_UPDATED.md status tracking with run history

### Phase 6: Documentation & Launch
- Write comprehensive README.md
- Create llms.txt for AI discoverability
- Add LICENSE file
- Final validation and first public push
