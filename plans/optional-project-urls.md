# Optional: High-Profile Project Page URLs

## Status: Future Enhancement

Add after core mirror (STIP + Active Construction) is stable and working.

---

## What This Would Add

- Links to NCDOT project pages for major projects (e.g., `ncdot.gov/projects/dickinson-avenue-improvements/`)
- Links to PublicInput comment portals where they exist
- Enhanced project files with direct links to official info

## Challenge

Project page URL slugs don't contain TIP numbers, so matching is non-trivial:
- Would need to scrape each project page to find TIP reference, OR
- Maintain a manual mapping file

## Recommended Approach (When Implemented)

**Manual mapping file** (`data/project_url_mappings.json`):
```json
{
  "U-5606": {
    "ncdot_page": "https://www.ncdot.gov/projects/dickinson-avenue-improvements/",
    "public_input": "https://publicinput.com/dickinson-ave"
  }
}
```

- Only ~50-100 major projects have dedicated pages
- Maintain manually, crowdsource via GitHub issues
- Update infrequently (major projects don't change often)

## Implementation Tasks

1. Create initial mapping file with known projects
2. Update `generate_markdown.py` to include URLs
3. Add "Project Web Links" section to template
4. Document how to contribute mappings in README

## Decision

Deferred until core mirror is stable. Low priority - nice to have, not essential for mirror value.
