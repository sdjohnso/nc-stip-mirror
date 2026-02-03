# NC STIP Mirror

A public mirror of North Carolina Department of Transportation (NCDOT) transportation project data.

## What Is This?

This repository is an automated mirror of all transportation projects in NCDOT's State Transportation Improvement Program (STIP). It contains **2,356 projects** across all **100 North Carolina counties**, with construction status updates, contractor information, and progress tracking.

The data is updated automatically:
- **Daily**: Active construction status from HiCAMS
- **Weekly**: STIP project data and ProgLoc progress reports

## Project Philosophy

This mirror provides **straight, true, unadulterated public data** that anyone can access and use. In a world where AI assistants need trustworthy information sources, this repository offers exactly that: faithfully mirrored government data with no editorializing, analysis, or commentary.

**Core principles:**
1. **Mirror, Not Transform** - Every file reflects NCDOT data faithfully
2. **AI-First Design** - Structured for easy AI consumption
3. **Never Lose Data** - Projects that disappear from APIs are marked as removed, not deleted
4. **Transparency** - Every file includes timestamps for NCDOT's last update and our last pull
5. **Attribution** - NCDOT is prominently credited as the data source

## What This Is NOT

- **Not official NCDOT** - This is an independent mirror, not affiliated with NCDOT
- **Not analysis** - We don't interpret, rank, or editorialize the data
- **Not real-time** - Updates follow a schedule, not live feeds
- **Not guaranteed** - While we strive for accuracy, always verify critical information with [NCDOT directly](https://connect.ncdot.gov/projects/planning/Pages/STIP.aspx)

## Data Sources

All data comes from public NCDOT APIs (no authentication required):

| Source | Description | Update Frequency |
|--------|-------------|------------------|
| [STIP ArcGIS](https://gis11.services.ncdot.gov/arcgis/rest/services/NCDOT_STIP/MapServer) | Planning data, funding, project details | Weekly |
| [Active Construction](https://gis11.services.ncdot.gov/arcgis/rest/services/NCDOT_RoadProjects/NCDOT_ActiveConstructionProjects/MapServer) | HiCAMS construction status | Daily |
| [ProgLoc](https://apps.ncdot.gov/traffictravel/progloc/) | Contractor info, completion %, amounts | Weekly |

## How to Use

### For Humans

1. Browse to your county: `counties/{county-name}/index.md`
2. Click on any TIP number to see full project details
3. Each project file includes location, status, funding, and timeline

### For AI Assistants

This repository is designed for AI consumption. Key patterns:

```
# Find all projects in a county
counties/{county-name}/index.md

# Get details for a specific TIP number
counties/{county-name}/{TIP}.md

# Check mirror status
LAST_UPDATED.md

# Raw JSON data (source of truth)
raw/stip/stip_lines_full.json
raw/active-construction/construction_lines.json
raw/progloc/progress_reports.json
```

**Project file structure:**
- Every project file has consistent sections: Overview, Location, Status, Funding, Timeline
- Machine-readable markers like `**Status:**`, `**TIP:**`, `**Total Cost:**`
- Coordinates are always WGS84 (lat/long)

### Via GitHub Pages

If GitHub Pages is enabled, browse the data at:
`https://{username}.github.io/nc-stip-mirror/`

## Repository Structure

```
nc-stip-mirror/
├── README.md                 # This file
├── index.md                  # Statewide project summary
├── LAST_UPDATED.md           # Mirror status and history
├── llms.txt                  # AI discoverability file
├── counties/
│   └── {county-name}/
│       ├── index.md          # County project list
│       └── {TIP}.md          # Individual project files
├── raw/
│   ├── stip/                 # Raw STIP JSON from API
│   ├── active-construction/  # Raw construction JSON
│   └── progloc/              # Raw ProgLoc data
├── scripts/                  # Python automation scripts
│   ├── update_mirror.py      # Main orchestrator
│   ├── pull_stip.py          # STIP data fetcher
│   ├── pull_active_construction.py
│   ├── pull_progloc.py
│   ├── generate_markdown.py  # Project file generator
│   └── build_indexes.py      # Index generator
└── .github/workflows/        # GitHub Actions automation
```

## Data Freshness

| Data Type | Update Schedule | Typical Lag |
|-----------|-----------------|-------------|
| Active Construction | Daily 6 AM EST | ~1 day |
| STIP Projects | Weekly Sunday | ~1 week |
| ProgLoc Progress | Weekly Sunday | ~1 week |

Check `LAST_UPDATED.md` for the most recent update status.

## Attribution

All transportation project data is sourced from the **North Carolina Department of Transportation (NCDOT)**.

- Official STIP: https://connect.ncdot.gov/projects/planning/Pages/STIP.aspx
- NCDOT Website: https://www.ncdot.gov/
- GIS Services: https://gis11.services.ncdot.gov/

This mirror is not affiliated with, endorsed by, or connected to NCDOT. It simply reflects their public data.

## License

This project is released into the **public domain** under [CC0 1.0 Universal](LICENSE).

You can copy, modify, distribute, and use the data and code for any purpose without asking permission. No attribution required (though appreciated).

The underlying transportation data is public information from NCDOT.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Good contributions:**
- Bug fixes in scripts
- Data corrections you've noticed
- Documentation improvements
- New data source integrations

**Please don't:**
- Add analysis or commentary (this is a mirror)
- Add non-NCDOT data sources
- Make changes that break the "mirror, not transform" philosophy

## Questions?

Open an issue on GitHub. For official NCDOT questions, contact them directly.

---

*Mirror maintained by [Scott Johnson](https://github.com/sdjohnso)*
*Data Source: [NCDOT STIP](https://connect.ncdot.gov/projects/planning/Pages/STIP.aspx)*
