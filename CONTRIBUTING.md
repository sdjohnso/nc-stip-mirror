# Contributing to NC STIP Mirror

Thank you for your interest in contributing! This guide will help you understand how to contribute effectively.

## Project Philosophy

Before contributing, please understand our core principle: **this is a mirror, not a transformation**. We reflect NCDOT data faithfully without adding analysis, commentary, or derived insights.

## What We Accept

### Bug Fixes
- Script errors or crashes
- Incorrect data parsing
- Missing error handling
- API endpoint changes

### Data Corrections
- If you notice a project file has incorrect data compared to NCDOT's source
- Missing fields that should be populated
- Coordinate errors

### Documentation
- Typos and clarity improvements
- Better examples
- Additional usage guidance

### Improvements
- Better error handling
- Performance optimizations
- New NCDOT data source integrations (must be public data)
- Accessibility improvements

## What We Don't Accept

### Analysis or Commentary
- Rankings, scores, or ratings
- Editorial commentary on projects
- Predictions or projections
- "Insights" derived from the data

### Non-NCDOT Data
- Data from other states
- Private or proprietary data sources
- Third-party analysis overlays

### Breaking Changes
- Changes that would break AI consumption patterns
- Removing fields from project files
- Changing the directory structure

## How to Contribute

### 1. Fork the Repository

Click "Fork" on GitHub to create your own copy.

### 2. Create a Branch

```bash
git checkout -b fix/description-of-change
```

Use prefixes:
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `feat/` - New features or data sources
- `refactor/` - Code improvements

### 3. Make Your Changes

- Follow existing code style
- Add comments for complex logic
- Test your changes locally

### 4. Test Locally

```bash
# Set up environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run a test update
python scripts/update_mirror.py --mode daily --dry-run
```

### 5. Submit a Pull Request

- Describe what you changed and why
- Reference any related issues
- Keep PRs focused (one fix/feature per PR)

## Code Style

- Python 3.8+
- Use type hints where helpful
- Follow existing patterns in the codebase
- Prefer clarity over cleverness

## Testing

Before submitting:
1. Run the scripts without errors
2. Verify generated markdown looks correct
3. Check that raw JSON is valid
4. Test against Pitt County / TIP U-5606 (our validation baseline)

## Questions?

Open an issue with the "question" label if you're unsure about something.

## License

By contributing, you agree that your contributions will be released under the CC0 1.0 Universal public domain dedication.

---

Thank you for helping maintain this public resource!
