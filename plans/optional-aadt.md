# Optional: AADT Traffic Count Stations

## Status: Future Enhancement

Add after core mirror (STIP + Active Construction) is stable and working.

---

## What This Would Add

- ~48,687 traffic count stations statewide
- Historical AADT (Annual Average Daily Traffic) back to 2002
- Location descriptions and functional class
- Organized by county in `traffic-counts/{county}.md`

## Data Source

- **API**: `https://services.arcgis.com/NuWFvHYDMVmmxMeM/ArcGIS/rest/services/NCDOT_AADT_Stations/FeatureServer/0/query`
- **Format**: GeoJSON with coordinates
- **Update frequency**: Annually

## Implementation Tasks

1. Build `pull_aadt.py` with pagination
2. Create `traffic-counts/` folder structure
3. Generate county markdown files with station tables
4. Add to monthly GitHub Actions schedule
5. Update README to document traffic count data

## Value Assessment

**Pros:**
- Useful for understanding road usage
- Historical trends available
- Clean API, easy to pull

**Cons:**
- Separate from STIP projects (different data model)
- Large dataset (~48K records)
- Updates only annually (low urgency)

## Decision

Deferred until core mirror is stable. Revisit after 1-2 months of successful operation.
