# Human Design API Documentation

**Version:** 1.6.1  
**Base URL:** `http://localhost:8000` (or your deployment URL)

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

## 1. General Endpoints

### Calculate Chart
Get comprehensive Human Design calculations for a single person.

**Endpoint:** `GET /calculate`

#### Parameters
| Name | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `place` | string | Yes | "City, Country" (e.g., "London, UK") |
| `year` | int | Yes | Birth Year |
| `month` | int | Yes | Birth Month (1-12) |
| `day` | int | Yes | Birth Day (1-31) |
| `hour` | int | Yes | Birth Hour (0-23) |
| `minute` | int | Yes | Birth Minute (0-59) |
| `second` | int | No | Birth Second (Default: 0) |
| `gender` | string | No | Gender (None, male, female, etc. Default: male) |
| `islive` | bool | No | Whether the person is alive (true) or deceased (false). (Default: true) |

#### Example Request
```bash
curl -X GET "http://localhost:8000/calculate?place=Kirikkale,Turkey&year=1968&month=2&day=21&hour=11&minute=0" \
  -H "Authorization: Bearer <your_token>"
```

#### Example Response
```json
{
  "general": {
    "birth_date": "1990-01-01T12:00:00Z",
    "energy_type": "Generator",
    "inner_authority": "Sacral",
    "profile": "2/4: Hermit Opportunist",
    "definition": "Single Definition",
    "active_chakras": ["Sacral", "Root"],
    "age": 35,
    "zodiac_sign": "Capricorn",
    "gender": "male",
    "islive": true,
    ...
  },
  "gates": { ... },
  "channels": { ... }
}
```

### Get BodyGraph Image
Render a visual bodygraph chart.

**Endpoint:** `GET /bodygraph`

#### Parameters
Same as `/calculate`, plus:
| Name | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `fmt` | string | `png` | Image format (`png`, `svg`, `jpg`) |

#### Example Request
```bash
curl -X GET "http://localhost:8000/bodygraph?place=London,UK&year=1990&month=1&day=1&hour=12&minute=0&fmt=png" \
  -H "Authorization: Bearer <your_token>" \
  --output chart.png
```

<img src="../src/humandesign/static/bodygraph_sample.png" alt="alt text" width="50%" />

---

## 2. Transit Analysis

### Daily Transit ("Weather")
Analyze the "Weather of the Day" by combining a birth chart with the current transit field.

**Endpoint:** `GET /transits/daily`

#### Parameters
Requires Birth Data (year...place) plus:
| Name | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `transit_year` | int | Yes | Transit Year |
| `transit_month` | int | Yes | Transit Month |
| `transit_day` | int | Yes | Transit Day |

#### Example Request
```bash
curl -X GET "http://localhost:8000/transits/daily?place=London,UK&year=1990&month=1&day=1&hour=12&minute=0&transit_year=2025&transit_month=1&transit_day=1" \
  -H "Authorization: Bearer <your_token>"
```

#### Example Response
```json
{
  "transit_date": "2025-01-01",
  "analysis": {
    "composite_type": "Manifesting Generator",
    "new_defined_centers": ["Throat", "SolarPlexus"],
    ...
  }
}
```

### Solar Return
Calculate the Yearly Theme for a specific year.

**Endpoint:** `GET /transits/solar_return`

#### Additional Parameters
| Name | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `sr_year_offset` | int | 0 | 0 = Current SR, 1 = Next Year's SR |

#### Example Request
```bash
curl -X GET "http://localhost:8000/transits/solar_return?place=London,UK&year=1990&month=1&day=1&hour=12&minute=0&sr_year_offset=0" \
  -H "Authorization: Bearer <your_token>"
```

---

## 3. Relationship & Group Analysis

### Pairwise Composite Analysis
Detailed mechanics for exactly two people. Returns new channels and centers formed by the connection.

**Endpoint:** `POST /analyze/composite`

#### Request Body
```json
{
  "person1": { "place": "London, UK", "year": 1990, "month": 1, "day": 1, "hour": 12, "minute": 0 },
  "person2": { "place": "New York, USA", "year": 1992, "month": 5, "day": 20, "hour": 18, "minute": 30 }
}
```

#### Example Request
```bash
curl -X POST "http://localhost:8000/analyze/composite" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "person1": { "place": "London, UK", "year": 1990, "month": 1, "day": 1, "hour": 12, "minute": 0 },
    "person2": { "place": "New York, USA", "year": 1992, "month": 5, "day": 20, "hour": 18, "minute": 30 }
  }'
```

#### Example Response (v1.3.0 Standard)
```json
{
  "participants": ["person1", "person2"],
  "new_channels": [
    { "gate": 59, "ch_gate": 6, "meaning": ["Mating", "A d. focused on reproduction"] }
  ],
  "new_chakras": ["SolarPlexus", "Throat"],
  "composite_chakras": ["Sacral", "Root", "SolarPlexus", "Throat", "Ajna"]
}
```

### Group Penta Analysis
Calculate group dynamics for 3-5 people.

**Endpoint:** `POST /analyze/penta`

#### Request Body
Accepts dictionary of 3 to 5 people (similar structure to Composite).

#### Example Request
```bash
curl -X POST "http://localhost:8000/analyze/penta" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "person1": { "place": "London, UK", "year": 1990, "month": 1, "day": 1, "hour": 12, "minute": 0 },
    "person2": { "place": "New York, USA", "year": 1992, "month": 5, "day": 20, "hour": 18, "minute": 30 },
    "person3": { "place": "Berlin, DE", "year": 1985, "month": 3, "day": 15, "hour": 9, "minute": 15 }
  }'
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
*Documentation generated for Human Design API v1.6.1*
