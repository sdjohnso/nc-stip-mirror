# Optional: TIMS Traffic Incidents Integration

## Status: Future Enhancement

This is **not part of the core mirror**. Implement only if there's demand after the main mirror is stable.

---

## Why This Is Separate

The TIMS Traffic Incidents API provides **real-time, volatile data** that doesn't fit the static mirror model:

- Incidents appear and disappear within hours
- Data changes constantly (not daily/weekly/monthly like other sources)
- Historical value is questionable (incidents are resolved and gone)
- Would require fundamentally different update cadence

## If Implemented

### Approach Options

**Option A: Snapshot File (Simplest)**
- Single file: `incidents/current.json`
- Overwritten on each update (no history)
- Update frequency: Every 15-30 minutes via GitHub Actions
- Simple but loses historical data

**Option B: Rolling Archive**
- Append incidents to daily files: `incidents/2026-02-02.json`
- Keep 7-30 days of history
- Allows trend analysis over short periods
- More storage, more complexity

**Option C: Don't Store, Just Document**
- Don't mirror the data at all
- Just document the API endpoint in README
- Let consumers call TIMS directly for real-time needs

### API Endpoints
- Base: `https://eapps.ncdot.gov/services/traffic-prod/v1/`
- `/incidents` - All incidents
- `/incidents?active=true` - Active only
- `/counties/{id}/incidents` - By county

### Recommendation
Start with **Option C** (document only). Real-time traffic data has limited value as a static mirror. Users needing live incident data should query the API directly.

---

## Decision: Deferred

Revisit this after the main mirror has been running for 1-2 months and there's clarity on whether users want incident data.
