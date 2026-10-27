<div align="center">

<img src="logo.jpg" alt="Human Design API" width="256">

# Human Design API

🔮⚡ High-fidelity Human Design calculation engine — birth-chart analytics, BodyGraph visualization, and Group/Penta dynamics via a FastAPI service.

[![Version](https://img.shields.io/badge/version-4.0.3-blue.svg)](https://github.com/dturkuler/humandesign_api/releases/tag/v4.0.3)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE-AGPL)
[![Commercial License](https://img.shields.io/badge/License-Commercial-green.svg)](mailto:dogan.turkuler@gmail.com)
[![Docker](https://img.shields.io/badge/docker-dturkuler%2Fhumandesign__api-2496ED?logo=docker&logoColor=white)](https://hub.docker.com/r/dturkuler/humandesign_api)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org)
[![Docs](https://img.shields.io/badge/docs-API_DOCUMENTATION-md.svg)](docs/API_DOCUMENTATION.md)

[Documentation](docs/API_DOCUMENTATION.md) · [Changelog](CHANGELOG.md) · [Devaible](https://devaible.com)

</div>

---

## Overview

**Human Design API** is a high-performance Python service that powers modern Human Design applications. It serves as a comprehensive backend engine that:

1. **Calculates** core and deep Human Design metrics from birth data (Earth, Moon, Nodes, Planets, Gates, Lines, Color, Tone, Base).
2. **Resolves** birth locations to precise geocoordinates and timezones automatically.
3. **Visualizes** results by generating beautiful, high-quality BodyGraph images on-the-fly.

Whether you are building a mobile app, a professional dashboard, or a personal research tool, this API provides the rigorous astrological data and visual assets you need — all containerized for easy deployment.

## Features

*   **V2 Calculate API**: High-performance `POST /v2/calculate` with semantic enrichment, Dream Rave, and Global Cycle support.
*   **High-Fidelity Maia Matrix v2**: Advanced relational analysis with planetary triggers, nodal resonance, and sub-circuit details.
*   **Penta Analysis 2.0**: Enhanced Group Dynamics (3–5 people) via the `/analyze/penta` endpoint (Sovereign Standard).
*   **Maia-Penta Hybrid Analysis**: Flagship `POST /analyze/maia-penta` endpoint for professional composite + group dynamics in one request.
*   **Grounded 10x Interpretation**: Consultant-grade, psychology-grounded reports with zero-jargon semantic output.
*   **Global Performance (Sub-20ms)**: Integrated `TimezoneFinder` singleton and geocoding bypass for 100× lower latency.
*   **Coordinate Support**: All endpoints accept optional `latitude`/`longitude` to bypass geocoding for maximum precision and speed.
*   **FastAPI Backend**: High-performance, async-ready Python web framework.
*   **Precise Calculations**: `pyswisseph` for Swiss Ephemeris accuracy; `geopy`/`timezonefinder` for location and timezone resolution.
*   **BodyGraph Visualization**: High-fidelity BodyGraph charts in PNG, SVG, and JPG via `/bodygraph`.
*   **Comprehensive Chart Data**: Energy Type, Strategy, Authority, Profile, Incarnation Cross, Variables, Age, Western Zodiac, and full Planetary/Gate positions.

## API Versions: V1 vs V2

| Feature | Legacy V1 | Flagship V2 |
| :--- | :--- | :--- |
| **Request Type** | GET (Limited) | POST (Scalable JSON) |
| **Performance** | Standard | High (Coordinate Bypass) |
| **Output Control** | Fixed Response | Selective (Include/Exclude) |
| **Dream Rave** | ❌ No | ✅ Included |
| **Global Cycles** | ❌ No | ✅ Included |
| **Semantic Layer** | Basic | ✅ Deep Enrichment |
| **Variables/PHS** | Partial | ✅ Full Schema Support |

## 📦 Installation

### Prerequisites

*   **Docker**: Installed and running. Download from [Docker's official website](https://www.docker.com/products/docker-desktop).
*   **Docker Compose**: Usually bundled with Docker Desktop. Verify with `docker-compose --version`.

### Quick Start (Docker)

```bash
git clone https://github.com/dturkuler/humandesign_api.git
cd humandesign_api
cp .env_example .env   # then set HD_API_TOKEN
docker-compose up --build -d
```

The API is then accessible at `http://localhost:9021`. Verify with `docker ps` (look for the `humandesignapi` container).

### Quick Start (pip)

```bash
pip install -e .
uvicorn humandesign.api:app --host 0.0.0.0 --port 9021
```

> [!NOTE]
> The `.env` file stores your API token (`HD_API_TOKEN`). Keep it secret — it is gitignored.

## 🚀 Usage

The API exposes calculation, visualization, and analysis endpoints. A minimal V2 request:

```bash
curl -X POST "http://localhost:9021/v2/calculate" \
  -H "Authorization: Bearer your_secret_token_here" \
  -H "Content-Type: application/json" \
  -d '{"year": 1990, "month": 7, "day": 15, "hour": 14, "minute": 30, "place": "London, UK"}'
```

### Endpoint Reference

#### 1. `GET /calculate`

Calculates comprehensive Human Design features from birth information.

| Name | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `year` | `integer` | Birth year (e.g., `1990`) | Yes |
| `month` | `integer` | Birth month (e.g., `7`) | Yes |
| `day` | `integer` | Birth day (e.g., `15`) | Yes |
| `hour` | `integer` | Birth hour (24h, e.g., `14`) | Yes |
| `minute` | `integer` | Birth minute (e.g., `30`) | Yes |
| `second` | `integer` | Birth second (default `0`) | No |
| `place` | `string` | Birth place (e.g., `London, UK`) | Yes |

**Example Response (condensed):**
```json
{
  "general": {
    "birth_date": "1990-07-15T13:30:00Z",
    "age": 35,
    "energy_type": "Projector",
    "strategy": "Wait for the Invitation",
    "inner_authority": "Solar Plexus",
    "inc_cross": "The Right Angle Cross of the Maya (2)",
    "profile": "3/5: Martyr Heretic",
    "definition": "Split Definition"
  },
  "gates": { },
  "channels": { "Channels": [ { "channel": "30/41: The Channel of Recognition..." } ] }
}
```

---

#### 2. `GET /bodygraph`

Generates a visual BodyGraph chart image from birth information. Accepts the same birth parameters plus:

| Name | Type | Description | Default |
| :--- | :--- | :--- | :--- |
| `fmt` | `string` | Image format: `png`, `svg`, `jpg`, `jpeg` | `png` |

```bash
curl -X GET "http://localhost:9021/bodygraph?year=1990&month=7&day=15&hour=14&minute=30&place=London%2C%20UK&fmt=png" \
  -H "Authorization: Bearer your_secret_token_here" -o bodygraph.png
```

---

#### 3. `GET /transits/daily`

Calculates the "Weather of the Day" via a composite of birth data and current planetary transit. Requires birth data plus `transit_year`, `transit_month`, `transit_day`.

```bash
curl -X GET "http://localhost:9021/transits/daily?year=1990&month=7&day=15&hour=14&minute=30&place=London%2C%20UK&transit_year=2025&transit_month=12&transit_day=22" \
  -H "Authorization: Bearer your_secret_token_here"
```

---

#### 4. `GET /transits/solar_return`

Calculates the "Yearly Theme" (Solar Return). Requires birth data plus `sr_year_offset` (years after birth, default `0`).

```bash
curl -X GET "http://localhost:9021/transits/solar_return?year=1990&month=7&day=15&hour=14&minute=30&place=London%2C%20UK&sr_year_offset=0" \
  -H "Authorization: Bearer your_secret_token_here"
```

---

#### 5. `POST /analyze/composite`

Detailed pairwise composite analysis for exactly two people.

```json
{
  "person1": { "place": "Berlin, Germany", "year": 1985, "month": 6, "day": 15, "hour": 14, "minute": 30 },
  "person2": { "place": "Munich, Germany", "year": 1988, "month": 11, "day": 22, "hour": 9, "minute": 15 }
}
```

```bash
curl -X POST "http://localhost:9021/analyze/composite" \
  -H "Authorization: Bearer your_secret_token_here" \
  -H "Content-Type: application/json" -d @payload.json
```

**Response:**
```json
{
  "participants": ["person1", "person2"],
  "new_channels": [ { "gate": 59, "ch_gate": 6, "meaning": ["Mating", "A d. focused on reproduction"] } ],
  "duplicated_channels": [],
  "new_chakras": ["SolarPlexus"],
  "composite_chakras": ["Ajna", "Throat", "G_Center", "SolarPlexus", "Sacral", "Root"]
}
```

---

#### 6. `POST /analyze/compmatrix`

Composite Human Design matrix (Relationship Mechanics) for two or more people.

```bash
curl -X POST "http://localhost:9021/analyze/compmatrix" \
  -H "Authorization: Bearer your_secret_token_here" \
  -H "Content-Type: application/json" -d @payload.json
```

---

#### 7. `POST /analyze/penta`

**Group Dynamics (Penta)** using the Sovereign Standard (consultant-level interpretation).

```json
{
  "group_type": "family",
  "participants": {
    "Person A": { "place": "City, Country", "year": 1985, "month": 6, "day": 15, "hour": 14, "minute": 30 },
    "Person B": { }
  }
}
```

```bash
curl -X POST "http://localhost:9021/analyze/penta" \
  -H "Authorization: Bearer your_secret_token_here" \
  -H "Content-Type: application/json" -d @penta_v2_payload.json
```

## 📂 Folder Structure

```
.
├── .env_example
├── CHANGELOG.md
├── LICENSE
├── README.md
├── docker-compose.yml
├── Dockerfile
├── openapi.yaml
├── pyproject.toml
└── src/
    └── humandesign/
        ├── api.py           # FastAPI Application Entry
        ├── data/            # Static layout and hd data
        ├── features/        # Core Rave Engine logic
        ├── routers/         # API Route definitions
        ├── schemas/         # Pydantic validation models
        ├── services/        # Business logic services
        └── utils/           # Utilities (Astrology, Versioning, etc.)
```

## 📖 API Documentation

For comprehensive details, industrial-standard references, and runnable examples, see [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md).

The project ships an OpenAPI 3.0 specification (`openapi.yaml`) describing endpoints, parameters, responses, and schemas.

*   **Visualize**: Use a VS Code "Swagger Viewer" extension, or paste into the [Swagger Editor](https://editor.swagger.io/).
*   **Import into Postman**: `Import` → drag-drop `openapi.yaml`; a pre-configured collection is generated.
*   **Generate Clients**: Use `openapi-generator` for Python, JavaScript, Java, and more.

## 💼 License

This project is **dual-licensed**:

| Tier | Price | API Access | Credits / mo | Target Feature Set |
| :--- | :--- | :--- | :--- | :--- |
| **Hobbyist** | $0 | **V1 Only** | 50 | Legacy Calculations |
| **Startup** | $49/mo | **V1 + V2** | 20,000 | V2 Flagship + Interpretation |
| **Business** | $149/mo | **V1 + V2** | 150,000 | **Penta**, **Matrix**, White-Label |
| **Enterprise** | $499+/mo | **V1 + V2** | Custom | Unlimited Use, SLA, Support |

### Feature Locks & Premium Content

*   **V2 Flagship Engine**: Dream Rave, Global Cycles, and Selective Output Masking are restricted to paid tiers.
*   **Startup Tier**: Unlocks V2 access and the standard 10x Interpretation engine.
*   **Business Tier (Professional)**: Unlocks Group Penta Analysis, Maia-Matrix Relational Analytics, and White-Label BodyGraphs (no watermark).
*   **Enterprise Tier**: Full distribution rights for multiple domains, custom branding, and 99.9% uptime SLA.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE-AGPL)
[![Commercial License](https://img.shields.io/badge/License-Commercial-green.svg)](mailto:dogan.turkuler@gmail.com)

**Commercial self-hosted licenses start at $1,000/year.**
Contact: dogan.turkuler@gmail.com | https://devaible.com

## 🤝 Contributing

Contributions are welcome. Please open an issue or pull request on [GitHub](https://github.com/dturkuler/humandesign_api). For development setup, clone the repo, create a `.env` from `.env_example`, and run `docker-compose up --build -d`.

---

*Documentation generated for Human Design API v4.0.3*
