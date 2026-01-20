# Project Architecture Blueprint

**Generated:** 2026-01-20
**Version:** 3.0.0
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

The **Human Design API** is a stateless, high-performance calculation engine. Reaching **v3.0.0**, it has completed a significant architectural consolidation, retiring legacy endpoints to focus on the **Maia-Penta Hybrid Analysis**—a professional-grade engine for complex relational and group dynamics.

**Guiding Principles:**
1.  **Statelessness:** Strict Input-Process-Output workflow.
2.  **Modularity:** Decoupled calculation core (`features`) from transport layer (`routers`).
3.  **Precision:** Industry-standard accuracy via Swiss Ephemeris.
4.  **Consolidation:** Unified analysis flagship to prevent model-drift and redundant logic.

## 3. Core Architectural Component Implementation

### A. API Layer (`src/humandesign/routers/`)
-   **Purpose:** HTTP Interface, validation, and orchestration.
-   **Key Components:**
    -   `general.py`: Root endpoints (`/calculate`, `/bodygraph`, `/health`).
    -   `transits.py`: Temporal logic (`/daily`, `/solar_return`).
    -   `composite.py`: Multi-person track. **V3 Update:** Retired `/compmatrix` and `/maiamatrix`. Features the `/analyze/maia-penta` flagship.

### B. Feature Engine (`src/humandesign/features/`)
-   **Purpose:** Domain logic implementation.
-   **Key Components:**
    -   `core.py`: Complex algorithms (Hybrid, Penta, Relational).
    -   `mechanics.py`: System rules (Authority, Centers).
    -   `attributes.py`: Static data (Gates, Channels).

### C. Service Layer (`src/humandesign/services/`)
-   **Purpose:** Cross-cutting technical utilities.
-   **Key Components:**
    -   `chart_renderer.py`: Visual generation.
    -   `composite.py`: Orchestration for multi-participant jobs. **V3 Update:** Pruned redundant legacy matrix logic.

## 4. Data Flow (v3.0.0 optimized)

1.  **Ingress:** Pydantic validation of birth/transit parameters.
2.  **Bio-Resolution:** Conversion of city names to (Lat/Lon) with optional bypass support.
3.  **Astro-Calculation:** Swiss Ephemeris calculates planetary longitudes (base data).
4.  **Rave Transformation:** Base data mapped to Gates/Lines/Tones.
5.  **Relational Synthesis:** Hybrid engine correlates participants' planetary triggers and nodal environmental resonance.
6.  **Penta Projection:** Functional group gaps calculated based on unified group mechanics.
7.  **Egress:** High-fidelity JSON response returned.

## 5. Cross-Cutting Concerns

-   **Security:** Bearer Token middleware.
-   **Performance:** Singleton `TimezoneFinder` and geocoding bypass.
-   **Observability:** `/health` monitoring.
-   **Versioning:** PEP 621 compliant metadata managed via `pyproject.toml`.

## 6. Implementation Patterns (v3 Flagship)

**Maia-Penta Hybrid Orchestration:**
-   **Relational Precision:** Uses `date_to_gate_dict` to find planetary weights behind relational connections.
-   **Group Vitality:** Deduce functional roles and "Vital Sign" gaps in group structures.
-   **Semantic Cleanse:** Dynamically maps esoteric terminology to professional psychological language in output.

## 7. Deployment Architecture

-   **Docker:** Optimized multi-stage build (~520MB).
-   **Registry:** Publicly available at `dturkuler/humandesign_api:3.0.0`.
-   **Configuration:** 12-Factor app principles via environment variables.

## 8. Development Blueprint

**Implementing New Features:**
1.  **Define Schema:** `schemas/input_models.py` or `response_models.py`.
2.  **Core Logic:** Add pure functions to `features/core.py`.
3.  **Router Registration:** Extend existing modules in `routers/`.
4.  **Verification:** Assert parity with snapshots and new TDD requirements.

---
*Blueprint automatically updated for Version 3.0.0 Release Cycle.*
