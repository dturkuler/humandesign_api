# Project Architecture Blueprint

**Generated:** 2026-01-19
**Version:** 2.0.0
**Project:** Human Design API

## 1. Architecture Detection and Analysis

### Technology Stack
-   **Language:** Python 3.12+
-   **Web Framework:** FastAPI (Async)
-   **Server:** Uvicorn
-   **Astrology Engine:** `pyswisseph` (Swiss Ephemeris)
-   **Geospatial:** `geopy`, `timezonefinder`
-   **Visualization:** `matplotlib`, `svgpath2mpl`
-   **Containerization:** Docker, Docker Compose

### Architectural Pattern
**Layered / Modular Monolith**
The application is structured into distinct layers with clear separation of concerns, organized by domain function (Routers, Services, Features, Logic).

## 2. Architectural Overview

The **Human Design API** is designed as a stateless, high-performance calculation engine. It adheres to the **Sovereign Standard**, ensuring zero-hallucination, deterministic outputs for complex astrological and Human Design metrics.

**Guiding Principles:**
1.  **Statelessness:** No database persistence for calculations; strict Input-Process-Output.
2.  **Modularity:** Core logic (`features`) is decoupled from the HTTP layer (`routers`).
3.  **Precision:** Uses industry-standard Swiss Ephemeris for astronomical accuracy.
4.  **Semantic Richness:** Output is strictly typed and semantically mapped (Diamond/Sovereign standards) for ease of AI/Human interpretation.

## 3. Core Architectural Component Implementation

### A. API Layer (`src/humandesign/routers/`)
-   **Purpose:** Handles HTTP requests, input validation, and response formatting.
-   **Components:**
    -   `general.py`: Core endpoints (`/calculate`, `/bodygraph`, `/health`).
    -   `transits.py`: Temporal analysis (`/transits/daily`, `/transits/solar_return`).
    -   `composite.py`: Multi-person analysis (`/analyze/composite`, `/analyze/penta`).
-   **Pattern:** FastAPI Routers using Pydantic schemas for validation.

### B. Feature Engine (`src/humandesign/features/`)
-   **Purpose:** The "Brain" of the application. Contains pure functions for Human Design logic.
-   **Components:**
    -   `core.py`: Implementation of high-level algorithms (Penta, Composite).
    -   `mechanics.py`: Rules for Authority, Centers, and Definition.
    -   `attributes.py`: Static attributes (Gates, Lines, Channels).
-   **Pattern:** Functional programming; stateless functions receiving definitions and astronomical data.

### C. Data & Constants (`src/humandesign/hd_constants.py`)
-   **Purpose:** Single Source of Truth for Human Design knowledge.
-   **Content:**
    -   `PENTA_DEFINITIONS`: Channel maps for group dynamics.
    -   `FAMILY/BUSINESS_SKILLS_MAP`: Semantic context dictionaries.
    -   `PENTA_LINE_KEYWORD_MAP`: Operational style definitions.
-   **Pattern:** Constant lookup tables (dictionaries) for O(1) access.

### D. Service Layer (`src/humandesign/services/`)
-   **Purpose:** Utilities that orchestrate complex, non-domain specific tasks.
-   **Components:**
    -   `chart_renderer.py`: BodyGraph image generation logic.
    -   `geolocation.py`: Lat/Lon resolution.

## 4. Data Flow

1.  **Input:** User sends Birth Data (Date, Time, Location).
2.  **Validation:** Pydantic schemas enforce type and range correctness.
3.  **Geocoding:** `geolocation.py` converts "City, Country" -> (Lat, Lon) -> Timezone.
4.  **Ephemeris:** `pyswisseph` calculates planetary positions (Julian Day).
5.  **Feature Logic:** `features/core.py` transforms positions into Gate/Line/Tone activations.
6.  **Mechanics:** `mechanics.py` determines Centers, Channels, and Authority.
7.  **Semantic Mapping:** V2 logic applies `hd_constants` maps (Family vs Business) to enrich output.
8.  **Output:** Structured JSON is returned to the client.

## 5. Cross-Cutting Concerns

-   **Authentication:** Bearer Token middleware (`verify_token` dependency).
-   **Error Handling:** Global exception handlers return standardized HTTP 4xx/5xx responses.
-   **Health Checks:** `/health` endpoint monitors system and dependency status (e.g., SwissEph availability).
-   **Versioning:** Single source of truth in `pyproject.toml`, exposed via API metadata.

## 6. Implementation Patterns (Penta V2)

**Diamond/Sovereign Standard Implementation:**
-   **Context Switching:** Logic in `get_penta_v2` dynamically swaps lookup tables (`FAMILY_Skills` vs `BUSINESS_Skills`) based on `group_type`.
-   **Functional Roles:** Iterates active channels to map participants to functional outputs (`Implementation`, `Planning`).
-   **Line Semantics:** Applies specialized `PENTA_LINE_KEYWORD_MAP` to translate raw line numbers (1-6) into operational styles (e.g., "Authoritarian").

## 7. Deployment Architecture

-   **Docker:** Multi-stage build (Builder -> Runtime) to minimize image size (~450MB).
-   **Environment:** Configuration via `.env` file (API Token).
-   **Orchestration:** Docker Compose maps port 8000 and manages volume/network links.

## 8. Extension Guide

**Adding a New Analysis Type:**
1.  **Define Schema:** Add input/output models in `schemas/`.
2.  **Implement Logic:** Add calculation function in `features/` or `services/`.
3.  **Register Route:** Add endpoint in appropriate `routers/` file.
4.  **Map Constants:** If semantic mapping is needed, update `hd_constants.py`.
5.  **Test:** Add unit test in `tests/`.

**Modifying Penta Logic:**
-   Edit `src/humandesign/features/core.py`.
-   Maintain Sovereign Standard (V2) semantic mapping structure.

## 9. Governance

-   **Testing:** `pytest` suite ensuring parity across individual, composite, and group calculations.
-   **Linting:** `ruff` used for code quality enforcement.
-   **Documentation:** `API_DOCUMENTATION.md` and `OPENAPI.yaml` must be kept in sync with code changes.
