"""
NCDOT Transportation Mirror - Configuration

Contains all API URLs, NC county list, and field mappings.
"""

# =============================================================================
# API Base URLs
# =============================================================================

# STIP (State Transportation Improvement Program)
STIP_BASE = "https://gis11.services.ncdot.gov/arcgis/rest/services/NCDOT_STIP/MapServer"
STIP_POINTS = f"{STIP_BASE}/0"  # Point features
STIP_LINES = f"{STIP_BASE}/1"   # Line features

# Active Construction Projects (HiCAMS data, updated nightly)
CONSTRUCTION_BASE = "https://gis11.services.ncdot.gov/arcgis/rest/services/NCDOT_RoadProjects/NCDOT_ActiveConstructionProjects/MapServer"
CONSTRUCTION_POINTS = f"{CONSTRUCTION_BASE}/0"  # Point features
CONSTRUCTION_LINES = f"{CONSTRUCTION_BASE}/1"   # Line features
CONSTRUCTION_TABLE = f"{CONSTRUCTION_BASE}/3"   # HiCAMS attributes table

# AADT (Annual Average Daily Traffic) Stations
AADT_BASE = "https://services.arcgis.com/NuWFvHYDMVmmxMeM/ArcGIS/rest/services/NCDOT_AADT_Stations/FeatureServer"
AADT_STATIONS = f"{AADT_BASE}/0"

# ProgLoc (Progress Location Reports)
PROGLOC_EXPORT = "https://apps.ncdot.gov/traffictravel/progloc/ExportProgLocToExcel.aspx"

# =============================================================================
# API Query Parameters
# =============================================================================

# Always request WGS84 coordinates, not NC State Plane
DEFAULT_OUT_SR = 4326

# ArcGIS API pagination limit
MAX_RECORD_COUNT = 1000

# Rate limiting (seconds between requests)
REQUEST_DELAY = 1.5

# =============================================================================
# NC Counties (100 total)
# =============================================================================

# All 100 North Carolina counties
# Key: lowercase (for folder names)
# Value: Title Case (for display)
NC_COUNTIES = {
    "alamance": "Alamance",
    "alexander": "Alexander",
    "alleghany": "Alleghany",
    "anson": "Anson",
    "ashe": "Ashe",
    "avery": "Avery",
    "beaufort": "Beaufort",
    "bertie": "Bertie",
    "bladen": "Bladen",
    "brunswick": "Brunswick",
    "buncombe": "Buncombe",
    "burke": "Burke",
    "cabarrus": "Cabarrus",
    "caldwell": "Caldwell",
    "camden": "Camden",
    "carteret": "Carteret",
    "caswell": "Caswell",
    "catawba": "Catawba",
    "chatham": "Chatham",
    "cherokee": "Cherokee",
    "chowan": "Chowan",
    "clay": "Clay",
    "cleveland": "Cleveland",
    "columbus": "Columbus",
    "craven": "Craven",
    "cumberland": "Cumberland",
    "currituck": "Currituck",
    "dare": "Dare",
    "davidson": "Davidson",
    "davie": "Davie",
    "duplin": "Duplin",
    "durham": "Durham",
    "edgecombe": "Edgecombe",
    "forsyth": "Forsyth",
    "franklin": "Franklin",
    "gaston": "Gaston",
    "gates": "Gates",
    "graham": "Graham",
    "granville": "Granville",
    "greene": "Greene",
    "guilford": "Guilford",
    "halifax": "Halifax",
    "harnett": "Harnett",
    "haywood": "Haywood",
    "henderson": "Henderson",
    "hertford": "Hertford",
    "hoke": "Hoke",
    "hyde": "Hyde",
    "iredell": "Iredell",
    "jackson": "Jackson",
    "johnston": "Johnston",
    "jones": "Jones",
    "lee": "Lee",
    "lenoir": "Lenoir",
    "lincoln": "Lincoln",
    "macon": "Macon",
    "madison": "Madison",
    "martin": "Martin",
    "mcdowell": "McDowell",
    "mecklenburg": "Mecklenburg",
    "mitchell": "Mitchell",
    "montgomery": "Montgomery",
    "moore": "Moore",
    "nash": "Nash",
    "new hanover": "New Hanover",
    "northampton": "Northampton",
    "onslow": "Onslow",
    "orange": "Orange",
    "pamlico": "Pamlico",
    "pasquotank": "Pasquotank",
    "pender": "Pender",
    "perquimans": "Perquimans",
    "person": "Person",
    "pitt": "Pitt",
    "polk": "Polk",
    "randolph": "Randolph",
    "richmond": "Richmond",
    "robeson": "Robeson",
    "rockingham": "Rockingham",
    "rowan": "Rowan",
    "rutherford": "Rutherford",
    "sampson": "Sampson",
    "scotland": "Scotland",
    "stanly": "Stanly",
    "stokes": "Stokes",
    "surry": "Surry",
    "swain": "Swain",
    "transylvania": "Transylvania",
    "tyrrell": "Tyrrell",
    "union": "Union",
    "vance": "Vance",
    "wake": "Wake",
    "warren": "Warren",
    "washington": "Washington",
    "watauga": "Watauga",
    "wayne": "Wayne",
    "wilkes": "Wilkes",
    "wilson": "Wilson",
    "yadkin": "Yadkin",
    "yancey": "Yancey",
}

# =============================================================================
# Field Mappings (to be populated after API discovery)
# =============================================================================

# STIP field mappings
# These will map API field names to our standardized field names
STIP_FIELDS = {
    # TIP number field (primary identifier)
    "tip_number": None,  # Discover actual field name
    "county": None,
    "description": None,
    "project_type": None,
    "funding_source": None,
    "let_date": None,
    "completion_date": None,
    # ... more to be added after discovery
}

# Construction field mappings
CONSTRUCTION_FIELDS = {
    "tip_number": None,
    "contract_id": None,
    "contractor": None,
    "percent_complete": None,
    "status": None,
    # ... more to be added after discovery
}

# AADT field mappings
AADT_FIELDS = {
    "station_id": None,
    "route": None,
    "county": None,
    "aadt_count": None,
    "year": None,
    # ... more to be added after discovery
}


def normalize_county(county_name: str) -> str:
    """
    Normalize county name to lowercase folder format.

    Args:
        county_name: County name in any format (e.g., "PITT", "Pitt", "pitt")

    Returns:
        Lowercase county name for folder naming (e.g., "pitt")
    """
    return county_name.lower().strip()


def display_county(county_folder: str) -> str:
    """
    Get display name for a county folder.

    Args:
        county_folder: Lowercase folder name (e.g., "pitt")

    Returns:
        Title Case display name (e.g., "Pitt")
    """
    return NC_COUNTIES.get(county_folder, county_folder.title())
