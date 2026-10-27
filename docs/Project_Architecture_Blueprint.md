# Project Architecture Blueprint

**Generated:** 2026-10-27
**Version:** 4.0.3 "Sovereign"
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
-   **Containerization:** Docker (Multi-stage), Docker Compose
-   **Licensing Headers:** Unified SPDX identifiers (AGPL-3.0-or-later OR LicenseRef-DevAIble-Commercial)

### Architectural Pattern
**Layered / Service-Oriented (Dual-License Enforced)**
The application is structured into distinct layers with clear separation of concerns. v4.0.0 formalizes the transition from a collection of scripts to a professional-grade "Sovereign" knowledge engine.

## 2. Architectural Overview

The **Human Design API (v4.0.0)** is a high-fidelity calculation and interpretation engine. This release marks the transition to a **Dual-Licensing Strategy** and the stabilization of the **Sovereign Standard**—a zero-hallucination benchmark for professional Human Design analytics.

**Guiding Principles:**
1.  **Legal Integrity:** Clear licensing boundaries (AGPL-3.0 vs. Commercial).
2.  **Stateless Reliability:** Deterministic calculations using coordinates and cached solar ephemerides.
3.  **Semantic Depth:** Deep technical enrichment via local relational databases.
4.  **Forensic Accuracy:** Multi-stage validation of planetary positions and mechanical logic.

## 3. Core Architectural Component Implementation

### A. API Layer (`src/humandesign/routers/`)
-   **Purpose:** HTTP Interface, security enforcement, and request orchestration.
-   **Key Components:**
    -   `general.py`: V1 core endpoints (`/calculate`, `/bodygraph`).
    -   `v2/general.py`: Flagship V2 endpoint (`/v2/calculate`) with field masking.
    -   `transits.py`: Forecasting logic (`/daily`, `/solar_return`).
    -   `composite.py`: Relational and Group track (`/analyze/maia-penta`, `/analyze/penta`).

### B. Feature Engine (`src/humandesign/features/`)
-   **Purpose:** Domain logic and heavy Rave calculations.
-   **Key Components:**
    -   `core.py`: Orchestrates complex multi-participant analysis.
    -   `mechanics.py`: Standard HD rules hierarchy (Authority, Centers, Definition, 13 motor-to-throat pathways for Energy Type classification).
    -   `attributes.py`: Static mappings for Gates, Channels, and Variables.

### C. Service Layer (`src/humandesign/services/`)
-   **Purpose:** Technical service abstraction.
-   **Key Components:**
    -   `masking.py`: **Recursive Pattern Matching:** Dot-notation tree filtering for sparse fieldsets.
    -   `enrichment.py`: **Semantic Layer:** Resolves raw Gate/Line data into human-readable professional descriptors.
    -   `global_cycles.py`: Calculates Era/Epoch transitions (e.g., 2027 Bridge).
    -   `chart_renderer.py`: Optimized vector-to-raster BodyGraph generation.

## 4. Data Flow (v4.0.0 Sovereign Standard)

1.  **Validation:** Pydantic V2 schemas enforce strict input types and ranges.
2.  **Geopositioning:** Dual-mode resolution (Auto-Geocoding or Explicit Coordinate Bypass).
3.  **Swiss Ephemeris:** Deterministic calculation of planetary longitudes.
4.  **Rave Logic:** Coordinates transformed into Gates, Lines, Fixed/Undefined status.
5.  **Relational Synthesis:** Hybrid engine detects synergy types and planetary triggers.
6.  **Semantic Enrichment:** SQLite lookups for Incarnation Crosses and Gate semantics.
7.  **Final Masking:** Recursive filtering of the JSON response based on client-defined `include`/`exclude`.
8.  **Egress:** Signed/Validated response returned via async FastAPI pipeline.

## 5. Dual-Licensing Implementation

v4.0.0 introduces a strict dual-licensing implementation:
-   **LICENSE-AGPL**: Governs open-source community usage.
-   **LICENSE-COMMERCIAL**: Governs proprietary, hosted, and closed-source commercial deployments.
-   **SPDX Compliance**: Every file in `src/` contains unified headers indicating dual-licensing terms.

## 6. Implementation Patterns

**Sovereign Standard Verification:**
-   **TDD Snapshot Testing:** Core calculations are verified against a permanent regression suite.
-   **Forensic Validation:** Cross-checking mechanics (e.g., specific gate fixations) against verified HD reference charts.

**Recursive Payload Filtering:**
-   **Pattern:** Tree-based recursive traversal of the response dictionary.
-   **Impact:** Reduces average payload size by 70% while maintaining deep field access.

## 7. Deployment Architecture

-   **Docker:** High-performance multi-stage build (~447MB) using `python:3.12-slim`.
-   **Registry:** Managed at `dturkuler/humandesign_api:v4.0.0`.
-   **CI/CD:** Automated testing and release tagging via `release_manager` protocol.

## 8. Development Blueprint

**Adding a New Analysis Module:**
1.  Extend `schemas/input_models.py` with the new request parameters.
2.  Implement the mechanical logic in a dedicated service in `services/`.
3.  Integrate the service into the `maia-penta` or `v2/calculate` orchestration flow.
4.  Update `docs/API_DOCUMENTATION.md` and regenerate this blueprint.

---
*Blueprint automatically updated for Version 4.0.3 "Sovereign" Release.*
