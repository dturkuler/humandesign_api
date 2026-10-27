# Human Design API Documentation

**Version:** 4.0.3
**Base URL:** `http://localhost:8000` (or `https://api.humandesign.ai`)

## Overview

The Human Design API provides a robust engine for calculating astrological and Human Design metrics. It offers stateless, RESTful endpoints for individual charts, composite relationships, and temporal transit analysis.

## Authentication

All API endpoints are protected via **Bearer Token** authentication. You must provide your API token in the `Authorization` header.

**Header Format:**
```http
Authorization: Bearer <your_token>
```

> [!IMPORTANT]
> Keep your `HD_API_TOKEN` secure. Do not expose it in client-side code.

---

## 1. Core Endpoints

### Calculate Chart (V2 Flagship)
The high-fidelity calculation engine (v2). Returns a semantic, hierarchical JSON response with optional "sparse fieldset" masking.

**Endpoint:** `POST /v2/calculate`

#### Request Body
```json
{
  "year": 1990,
  "month": 1,
  "day": 12,
  "hour": 8,
  "minute": 0,
  "place": "New York, USA",
  "include": ["general", "gates.personality"],
  "exclude": ["channels"]
}
```

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `year` | int | Yes | Birth Year |
| `month` | int | Yes | Birth Month (1-12) |
| `day` | int | Yes | Birth Day (1-31) |
| `hour` | int | Yes | Birth Hour (0-23) |
| `minute` | int | Yes | Birth Minute (0-59) |
| `place` | string | Yes | "City, Country" (e.g., "London, UK") |
| `latitude` | float | No | Explicit Latitude (bypasses geocoding) |
| `longitude` | float | No | Explicit Longitude (bypasses geocoding) |
| `include` | list[str] | No | Whitelist fields (supports dot syntax: `gates.personality`) |
| `exclude` | list[str] | No | Blacklist fields |

#### Example Response
```json
{
  "general": {
    "energy_type": "Generator",
    "inner_authority": "Sacral Authority",
    "profile": "4/6: Opportunist Role Model",
    "inc_cross": "The Right Angle Cross of Planning (37/40 | 9/16)",
    "definition": "Split Definition"
  },
  "centers": {
    "defined": ["Sacral", "Root"],
    "undefined": ["Head", "Ajna", "Throat", "G_Center", "Heart", "Solar Plexus", "Spleen"]
  },
  "gates": {
    "personality": {
      "Sun": {
        "gate": 61,
        "line": 1, 
        "gate_name": "The Gate of Inner Truth",
        "fixation": { "type": "Exalted", "value": "Up" }
      }
    }
  },
  "advanced": {
    "dream_rave": { ... },
    "global_cycle": { ... }
  }
}
```

### System Health
Check API operational status.

**Endpoint:** `GET /health`

---

## 2. Transit Analysis

### Daily Transit ("Weather")
Analyze the "Weather of the Day" by combining a birth chart with the current transit field. Supports "Travel Mode" (calculating transits relative to current location).

**Endpoint:** `GET /transits/daily`

#### Parameters
| Name | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `place` | string | Yes | Birth Place |
| `year`, `month`, `day`, `hour`, `minute` | int | Yes | Birth Date/Time |
| `transit_year` | int | Yes | Target Year |
| `transit_month` | int | Yes | Target Month |
| `transit_day` | int | Yes | Target Day |
| `current_place` | string | No | **New:** Current User Location (for timezone-aware transits) |
| `transit_hour` | int | No | **New:** Target Hour (Local time at current_place) |

#### Example Request
```bash
curl -X GET "http://localhost:8000/transits/daily?place=London,UK&year=1990&month=1&day=1&hour=12&minute=0&transit_year=2025&transit_month=1&transit_day=1&current_place=New%20York,USA&transit_hour=9" \
  -H "Authorization: Bearer <your_token>"
```

### Solar Return
Calculate the Yearly Theme (Solar Return).

**Endpoint:** `GET /transits/solar_return`
*Parameters similar to Daily Transit, with `sr_year_offset` (0=Birth Year, 1=First Return).*

---

## 3. Relationship & Group Analysis (Professional)

### Maia-Penta Hybrid Analysis (Flagship)
The unified engine for relationship mechanics. Combines **Maia Matrix** (Pairwise Synergy) and **Penta** (Group Dynamics) into a single high-fidelity report.

**Endpoint:** `POST /analyze/maia-penta`

#### Request Body
```json
{
  "participants": {
    "Alice": { "place": "London, UK", "year": 1990, "month": 1, "day": 1, "hour": 12, "minute": 0 },
    "Bob": { "place": "New York, USA", "year": 1992, "month": 5, "day": 20, "hour": 18, "minute": 30 }
  },
  "group_type": "family",
  "verbosity": "all"
}
```

#### Response Features
*   **Synergy**: Connection Types (Electromagnetic, Dominance, Companionship, Split).
*   **Planetary Triggers**: Which planet activates which channel (e.g., "Mars activates 59-6").
*   **Nodal Resonance**: Environmental harmony analysis.
*   **Penta Dynamics**: Functional roles (if 3+ people).

### Group Penta Analysis (V2)
Dedicated endpoint for analyzing functional groups (3-5 people).

**Endpoint:** `POST /analyze/penta`

#### Request Body
```json
{
  "participants": { "A": {...}, "B": {...}, "C": {...} },
  "group_type": "business" 
}
```

---

## Error Handling

| Status Code | Description |
| :--- | :--- |
| `200` | Success |
| `400` | Bad Request (Validation or Geocoding failed) |
| `401` | Unauthorized (Missing or Invalid Token) |
| `422` | Unprocessable Entity (Input formatting issues) |
| `500` | Internal Server Error |

---
*Documentation updated for v4.0.0*
