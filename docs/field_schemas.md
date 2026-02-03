# NCDOT API Field Schemas

*Auto-generated on 2026-02-03 13:13:02*

This document contains field definitions and sample data from all NCDOT APIs
used by this mirror project.

---

## Table of Contents

- [STIP Points (Layer 0)](#stip-points-layer-0)
- [STIP Lines (Layer 1)](#stip-lines-layer-1)
- [Active Construction Points (Layer 0)](#active-construction-points-layer-0)
- [Active Construction Lines (Layer 1)](#active-construction-lines-layer-1)
- [Active Construction Table (Layer 3)](#active-construction-table-layer-3)
- [AADT Stations](#aadt-stations)

---

### STIP Points (Layer 0)

**URL:** `https://gis11.services.ncdot.gov/arcgis/rest/services/NCDOT_STIP/MapServer/0`

**Name:** 2026-2035 STIP Points
**Type:** Feature Layer
**Geometry Type:** esriGeometryMultipoint
**Max Record Count:** 1000

#### Fields

| Field Name | Type | Alias | Length |
|------------|------|-------|--------|
| OBJECTID | OID | OBJECTID |  |
| TIP | String | TIP | 10 |
| SPOTID | String | SPOTID | 255 |
| Route | String | Route | 255 |
| Description | String | Description | 500 |
| Category | String | Category | 255 |
| Mode | String | Mode | 255 |
| RightOfWayYear | String | Right Of Way Year | 255 |
| ConstructionYear | String | ConstructionYear | 255 |
| COMMENT | String | COMMENT | 255 |
| ProjectCost | Double | Project Cost |  |
| Symbology | String | Symbology | 100 |
| Counties | String | Counties | 255 |
| Divisions | String | Divisions | 255 |
| MPOsRPOs | String | MPOsRPOs | 255 |
| SHAPE | Geometry | SHAPE |  |

#### Sample Record

```json
{
  "OBJECTID": 1,
  "TIP": "AO-0001",
  "SPOTID": "",
  "Route": "AVL",
  "Description": "Asheville Regional Airport. Modernize building.",
  "Category": "EX",
  "Mode": "AVIATION",
  "RightOfWayYear": "",
  "ConstructionYear": "2022",
  "COMMENT": "UNDER CONSTRUCTION. \"FED\" FUNDS ARE FAA FUNDS; \"HF\" FUNDS ARE A STATE APPROPRIATION FROM THE HIGHWAY FUND; \"L\" FUNDS PROVIDED BY ASHEVILLE REGIONAL AIRPORT",
  "ProjectCost": 153808.0,
  "Symbology": "Ex Aviation",
  "Counties": "Buncombe",
  "Divisions": "13",
  "MPOsRPOs": "French Broad River MPO"
}
```

---

### STIP Lines (Layer 1)

**URL:** `https://gis11.services.ncdot.gov/arcgis/rest/services/NCDOT_STIP/MapServer/1`

**Name:** 2026-2035 STIP Lines
**Type:** Feature Layer
**Geometry Type:** esriGeometryPolyline
**Max Record Count:** 1000

#### Fields

| Field Name | Type | Alias | Length |
|------------|------|-------|--------|
| OBJECTID | OID | OBJECTID |  |
| TIP | String | TIP | 10 |
| SPOTID | String | SPOTID | 255 |
| Route | String | Route | 255 |
| Description | String | Description | 500 |
| Category | String | Category | 255 |
| Mode | String | Mode | 255 |
| RightOfWayYear | String | Right Of Way Year | 255 |
| ConstructionYear | String | ConstructionYear | 255 |
| COMMENT | String | COMMENT | 255 |
| ProjectCost | Double | Project Cost |  |
| Symbology | String | Symbology | 100 |
| Counties | String | Counties | 255 |
| Divisions | String | Divisions | 255 |
| MPOsRPOs | String | MPOsRPOs | 255 |
| SHAPE | Geometry | SHAPE |  |
| SHAPE.STLength() | Double | SHAPE.STLength() |  |

#### Sample Record

```json
{
  "OBJECTID": 1,
  "TIP": "A-0009CA",
  "SPOTID": "",
  "Route": "US 129; NC 143",
  "Description": "South of SR 1275 (Five Point Road) to NC 143; US 129 to SR 1223 (Beech Creek Road). Upgrade roadway.",
  "Category": "EX",
  "Mode": "HIGHWAY",
  "RightOfWayYear": "2021",
  "ConstructionYear": "2022",
  "COMMENT": "UNDER CONSTRUCTION.",
  "ProjectCost": 58554.0,
  "Symbology": "Ex Highway",
  "Counties": "Graham",
  "Divisions": "14",
  "MPOsRPOs": "Southwestern RPO",
  "SHAPE.STLength()": 21866.116425158267
}
```

---

### Active Construction Points (Layer 0)

**URL:** `https://gis11.services.ncdot.gov/arcgis/rest/services/NCDOT_RoadProjects/NCDOT_ActiveConstructionProjects/MapServer/0`

**Name:** NCDOT Construction Projects (Points)
**Type:** Feature Layer
**Geometry Type:** esriGeometryMultipoint
**Max Record Count:** 1000

#### Fields

| Field Name | Type | Alias | Length |
|------------|------|-------|--------|
| GdbGisuPub.HICAMS.ActiveProjectPoint.OBJECTID | OID | OBJECTID |  |
| GdbGisuPub.HICAMS.ActiveProjectPoint.ContractNumber | String | ContractNumber | 255 |
| GdbGisuPub.HICAMS.ActiveProjectPoint.Shape | Geometry | Shape |  |
| GdbGisuPub.HICAMS.ActiveContractsMap.ContractType | String | ContractType | 60 |
| GdbGisuPub.HICAMS.ActiveContractsMap.TipReference | String | TipReference | 150 |
| GdbGisuPub.HICAMS.ActiveContractsMap.TIP | String | TIP | 10 |
| GdbGisuPub.HICAMS.ActiveContractsMap.CountyNumber | Integer | CountyNumber |  |
| GdbGisuPub.HICAMS.ActiveContractsMap.LocationsDescription | String | LocationsDescription | 240 |
| GdbGisuPub.HICAMS.ActiveContractsMap.ContractNickname | String | ContractNickname | 40 |
| GdbGisuPub.HICAMS.ActiveContractsMap.ContractStatus | String | ContractStatus | 6 |
| GdbGisuPub.HICAMS.ActiveContractsMap.CompletionPercent | Double | CompletionPercent |  |
| GdbGisuPub.HICAMS.ActiveContractsMap.Route | String | Route | 12 |
| GdbGisuPub.HICAMS.ActiveContractsMap.PhysicalDivisionNumber | Integer | PhysicalDivisionNumber |  |
| GdbGisuPub.HICAMS.ActiveContractsMap.ContractActiveDate | Date | ContractActiveDate | 8 |

#### Sample Record

```json
{
  "GdbGisuPub.HICAMS.ActiveProjectPoint.OBJECTID": 53,
  "GdbGisuPub.HICAMS.ActiveProjectPoint.ContractNumber": "C204130",
  "GdbGisuPub.HICAMS.ActiveContractsMap.ContractType": "Other",
  "GdbGisuPub.HICAMS.ActiveContractsMap.TipReference": " R-5734A   ",
  "GdbGisuPub.HICAMS.ActiveContractsMap.TIP": "R-5734A   ",
  "GdbGisuPub.HICAMS.ActiveContractsMap.CountyNumber": 56,
  "GdbGisuPub.HICAMS.ActiveContractsMap.LocationsDescription": "US-23/441 FROM US-64 TO SR-1652 (WIDE HORIZON DR)/SR-1152 (BELDEN CIR) & BRIDGE NO. 314 OVER CARTOOGECHAYE CREEK.",
  "GdbGisuPub.HICAMS.ActiveContractsMap.ContractNickname": "US 23-441/BELDEN CIRCLE",
  "GdbGisuPub.HICAMS.ActiveContractsMap.ContractStatus": "ACTIVE",
  "GdbGisuPub.HICAMS.ActiveContractsMap.CompletionPercent": 88.31,
  "GdbGisuPub.HICAMS.ActiveContractsMap.Route": "US-23",
  "GdbGisuPub.HICAMS.ActiveContractsMap.PhysicalDivisionNumber": 14,
  "GdbGisuPub.HICAMS.ActiveContractsMap.ContractActiveDate": 1546960920000
}
```

---

### Active Construction Lines (Layer 1)

**URL:** `https://gis11.services.ncdot.gov/arcgis/rest/services/NCDOT_RoadProjects/NCDOT_ActiveConstructionProjects/MapServer/1`

**Name:** NCDOT Construction Projects (Lines)
**Type:** Feature Layer
**Geometry Type:** esriGeometryPolyline
**Max Record Count:** 1000

#### Fields

| Field Name | Type | Alias | Length |
|------------|------|-------|--------|
| GdbGisuPub.HICAMS.ActiveProjectLine.OBJECTID | OID | OBJECTID |  |
| GdbGisuPub.HICAMS.ActiveProjectLine.ContractNumber | String | ContractNumber | 255 |
| GdbGisuPub.HICAMS.ActiveProjectLine.Shape | Geometry | Shape |  |
| GdbGisuPub.HICAMS.ActiveContractsMap.ContractType | String | ContractType | 60 |
| GdbGisuPub.HICAMS.ActiveContractsMap.TipReference | String | TipReference | 150 |
| GdbGisuPub.HICAMS.ActiveContractsMap.TIP | String | TIP | 10 |
| GdbGisuPub.HICAMS.ActiveContractsMap.CountyNumber | Integer | CountyNumber |  |
| GdbGisuPub.HICAMS.ActiveContractsMap.LocationsDescription | String | LocationsDescription | 240 |
| GdbGisuPub.HICAMS.ActiveContractsMap.ContractNickname | String | ContractNickname | 40 |
| GdbGisuPub.HICAMS.ActiveContractsMap.ContractStatus | String | ContractStatus | 6 |
| GdbGisuPub.HICAMS.ActiveContractsMap.CompletionPercent | Double | CompletionPercent |  |
| GdbGisuPub.HICAMS.ActiveContractsMap.Route | String | Route | 12 |
| GdbGisuPub.HICAMS.ActiveContractsMap.PhysicalDivisionNumber | Integer | PhysicalDivisionNumber |  |
| GdbGisuPub.HICAMS.ActiveContractsMap.ContractActiveDate | Date | ContractActiveDate | 8 |

#### Sample Record

```json
{
  "GdbGisuPub.HICAMS.ActiveProjectLine.OBJECTID": 11,
  "GdbGisuPub.HICAMS.ActiveProjectLine.ContractNumber": "C203567",
  "GdbGisuPub.HICAMS.ActiveContractsMap.ContractType": "Other",
  "GdbGisuPub.HICAMS.ActiveContractsMap.TipReference": " U-3308    ",
  "GdbGisuPub.HICAMS.ActiveContractsMap.TIP": "U-3308    ",
  "GdbGisuPub.HICAMS.ActiveContractsMap.CountyNumber": 32,
  "GdbGisuPub.HICAMS.ActiveContractsMap.LocationsDescription": "NC-55 (ALSTON AVE) FROM NC-147 (BUCK DEAN FREEWAY) TO NORTH OF US-70BUS/NC-98 (HOLLOWAY ST).",
  "GdbGisuPub.HICAMS.ActiveContractsMap.ContractNickname": "NC 55 (Alston Avenue) Widening in Durham",
  "GdbGisuPub.HICAMS.ActiveContractsMap.ContractStatus": "ACTIVE",
  "GdbGisuPub.HICAMS.ActiveContractsMap.CompletionPercent": 94.67,
  "GdbGisuPub.HICAMS.ActiveContractsMap.Route": "NC-55",
  "GdbGisuPub.HICAMS.ActiveContractsMap.PhysicalDivisionNumber": 5,
  "GdbGisuPub.HICAMS.ActiveContractsMap.ContractActiveDate": 1472045100000
}
```

---

### Active Construction Table (Layer 3)

**URL:** `https://gis11.services.ncdot.gov/arcgis/rest/services/NCDOT_RoadProjects/NCDOT_ActiveConstructionProjects/MapServer/3`

**Name:** Unmapped HiCAMS Contracts
**Type:** Table
**Geometry Type:** None (Table)
**Max Record Count:** 1000

#### Fields

| Field Name | Type | Alias | Length |
|------------|------|-------|--------|
| OBJECTID | OID | OBJECTID |  |
| ContractNumber | String | ContractNumber | 20 |
| ContractType | String | ContractType | 60 |
| TipReference | String | TipReference | 150 |
| TIP | String | TIP | 10 |
| CountyNumber | Integer | CountyNumber |  |
| LocationsDescription | String | LocationsDescription | 240 |
| ContractNickname | String | ContractNickname | 40 |
| ContractStatus | String | ContractStatus | 6 |
| CompletionPercent | Double | CompletionPercent |  |
| Route | String | Route | 12 |
| PhysicalDivisionNumber | Integer | PhysicalDivisionNumber |  |
| ContractActiveDate | Date | ContractActiveDate | 8 |

#### Sample Record

```json
{
  "OBJECTID": 68,
  "ContractNumber": "C204702",
  "ContractType": "CMGC",
  "TipReference": null,
  "TIP": null,
  "CountyNumber": 76,
  "LocationsDescription": "GREENSBORO RANDOLPH MEGASITE NORTH OF US-421 AND EAST OF JULIAN AIRPORT ROAD.",
  "ContractNickname": "Megasite Grading",
  "ContractStatus": "ACTIVE",
  "CompletionPercent": 69.44,
  "Route": "US-421",
  "PhysicalDivisionNumber": 8,
  "ContractActiveDate": 1643100840000
}
```

---

### AADT Stations

**URL:** `https://services.arcgis.com/NuWFvHYDMVmmxMeM/ArcGIS/rest/services/NCDOT_AADT_Stations/FeatureServer/0`

**Name:** NCDOT_AADT_Stations
**Type:** Feature Layer
**Geometry Type:** esriGeometryPoint
**Max Record Count:** 1000

#### Fields

| Field Name | Type | Alias | Length |
|------------|------|-------|--------|
| FID | OID | FID |  |
| LocationID | String | LocationID | 254 |
| COUNTY | String | COUNTY | 254 |
| RTE_CLS | Double | RTE_CLS |  |
| ROUTE | String | ROUTE | 254 |
| LOCATION | String | LOCATION | 254 |
| AADT_2002 | String | AADT_2002 | 254 |
| AADT_2003 | String | AADT_2003 | 254 |
| AADT_2004 | String | AADT_2004 | 254 |
| AADT_2005 | String | AADT_2005 | 254 |
| AADT_2006 | String | AADT_2006 | 254 |
| AADT_2007 | String | AADT_2007 | 254 |
| AADT_2008 | String | AADT_2008 | 254 |
| AADT_2009 | String | AADT_2009 | 254 |
| AADT_2010 | String | AADT_2010 | 254 |
| AADT_2011 | String | AADT_2011 | 254 |
| AADT_2012 | String | AADT_2012 | 254 |
| AADT_2013 | String | AADT_2013 | 254 |
| AADT_2014 | String | AADT_2014 | 254 |
| AADT_2015 | String | AADT_2015 | 254 |
| AADT_2016 | String | AADT_2016 | 254 |
| AADT_2017 | String | AADT_2017 | 254 |
| AADT_2018 | String | AADT_2018 | 254 |
| AADT_2019 | String | AADT_2019 | 254 |
| AADT_2020 | String | AADT_2020 | 254 |
| AADT_2021 | String | AADT_2021 | 254 |
| AADT_2022 | String | AADT_2022 | 254 |

#### Sample Record

```json
{
  "FID": 1,
  "LocationID": "0010000002",
  "COUNTY": "ALAMANCE",
  "RTE_CLS": 4,
  "ROUTE": "SR 1103",
  "LOCATION": "WEST OF NC 49",
  "AADT_2002": " ",
  "AADT_2003": "220",
  "AADT_2004": " ",
  "AADT_2005": "260",
  "AADT_2006": " ",
  "AADT_2007": "210",
  "AADT_2008": " ",
  "AADT_2009": "230",
  "AADT_2010": " ",
  "AADT_2011": "220",
  "AADT_2012": " ",
  "AADT_2013": "220",
  "AADT_2014": " ",
  "AADT_2015": "250",
  "AADT_2016": " ",
  "AADT_2017": "180",
  "AADT_2018": " ",
  "AADT_2019": "200",
  "AADT_2020": " ",
  "AADT_2021": "200",
  "AADT_2022": " "
}
```

---
