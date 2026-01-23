# Project Architecture Blueprint

**Generated:** 2026-01-23
**Version:** 3.4.1
**Project:** Human Design API

## 1. Architecture Detection and Analysis

### Technology Stack
-   **Language:** Python 3.12+
-   **Web Framework:** FastAPI (Async)
-   **Server:** Uvicorn
-   **Astrology Engine:** `pyswisseph` (Swiss Ephemeris)
-   **Geospatial:** `geopy`, `timezonefinder` (Singleton)
-   **Semantic Engine:** SQLite (`hd_data.sqlite`)
-   **Visualization:** `matplotlib`, `svgpath2mpl`
-   **Containerization:** Docker, Docker Compose

### Architectural Pattern
**Layered / Modular Monolith**
The application is structured into distinct layers with clear separation of concerns, organized by domain function (Routers, Services, Features, Logic).

## 2. Architectural Overview

The **Human Design API** is a high-performance calculation engine. v3.4.1 features the stable **Recursive Masking** upgrade, allowing granular control over nested response fields for both `include` and `exclude` parameters.

**Guiding Principles:**
1.  **Statelessness:** Strict Input-Process-Output workflow.
2.  **Modularity:** Decoupled calculation core (`features`) from transport layer (`routers`).
3.  **Precision:** Industry-standard accuracy via Swiss Ephemeris.
4.  **Efficiency:** Payload reduction via recursive dot-notation masking.

## 3. Core Architectural Component Implementation

### A. API Layer (`src/humandesign/routers/`)
-   **Purpose:** HTTP Interface, validation, and orchestration.
-   **Key Components:**
    -   `general.py`: Root endpoints (`/calculate`, `/bodygraph`, `/health`). 
    -   `transits.py`: Temporal logic (`/daily`, `/solar_return`).
    -   `composite.py`: Multi-person track. Features the `/analyze/maia-penta` flagship.

### B. Feature Engine (`src/humandesign/features/`)
-   **Purpose:** Domain logic implementation.
-   **Key Components:**
    -   `core.py`: Complex algorithms (Hybrid, Penta, Relational).
    -   `mechanics.py`: System rules (Authority, Centers).
    -   `attributes.py`: Static data (Gates, Channels).
    -   `v2/calculate`: The high-fidelity endpoint with nested hierarchy.

### C. Service Layer (`src/humandesign/services/`)
-   **Purpose:** Cross-cutting technical utilities.
-   **Key Components:**
    -   `chart_renderer.py`: Visual generation.
    -   `composite.py`: Orchestration for multi-participant jobs.
    -   `masking.py`: **v3.4.1 stable:** Recursive masking logic with dot-notation tree parsing for `include` and `exclude`.
    -   `enrichment.py`: Semantic enrichment using SQLite.
    -   `dream_rave.py` & `global_cycles.py`: Advanced mechanics engines.

## 4. Data Flow (v3.4.0 optimized)

1.  **Ingress:** Pydantic validation of birth/transit parameters.
2.  **Bio-Resolution:** Conversion of city names to (Lat/Lon) with optional bypass support.
3.  **Astro-Calculation:** Swiss Ephemeris calculates planetary longitudes (base data).
4.  **Rave Transformation:** Base data mapped to Gates/Lines/Tones.
5.  **Relational Synthesis:** Hybrid engine correlates participants' planetary triggers and nodal environmental resonance.
6.  **Semantic Enrichment:** SQLite layer resolves gates and incarnation crosses to human-readable strings.
7.  **Output Masking (v3.4.1):** Dot-notation tree filtering applied to the final dictionary (supporting nested exclusions).
8.  **Egress:** High-fidelity JSON response returned (all V2 fields are `Optional` for sparse output).

## 5. Cross-Cutting Concerns

-   **Security:** Bearer Token middleware.
-   **Performance:** Singleton `TimezoneFinder`, geocoding bypass, and efficient masking.
-   **Observability:** `/health` monitoring.
-   **Versioning:** PEP 621 compliant metadata managed via `pyproject.toml`.

## 6. Implementation Patterns (v3 Flagship)

**Recursive Masking (v3.4.1):**
-   **Tree-Based Filtering:** Dot-notation paths are parsed into a tree structure for efficient recursive traversal.
-   **Full Parity:** Supports both `include` (whitelisting) and `exclude` (blacklisting) up to 3+ levels.
-   **Payload Control:** Enables clients to request only specific sub-fields (e.g., `gates.personality.Sun`).

**Maia-Penta Hybrid Orchestration:**
-   **Relational Precision:** Uses `date_to_gate_dict` to find planetary weights behind relational connections.
-   **Group Vitality:** Deduce functional roles and "Vital Sign" gaps in group structures.

## 7. Deployment Architecture

-   **Docker:** Optimized multi-stage build (~447MB).
-   **Registry:** Publicly available at `dturkuler/humandesign_api:3.4.1`.
-   **Configuration:** 12-Factor app principles via environment variables.

## 8. Development Blueprint

**Implementing New Features:**
1.  **Define Schema:** `schemas/input_models.py` or `response_models.py`.
2.  **Core Logic:** Add pure functions to `features/core.py`.
3.  **Router Registration:** Extend existing modules in `routers/`.
4.  **Verification:** Assert parity with snapshots and new TDD requirements.

---
*Blueprint automatically updated for Version 3.4.1 Release Cycle.*
