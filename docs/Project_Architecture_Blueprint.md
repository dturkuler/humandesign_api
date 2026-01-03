# Project Architecture Blueprint: Human Design API

This document provides a comprehensive analysis of the architectural patterns, components, and implementation strategies used in the Human Design API. It serves as a definitive reference for maintaining architectural consistency and guiding future development.

## 1. Architectural Overview

The Human Design API is built as a **Modular Monolith** using the **FastAPI** framework. It follows a layered approach that separates concerns between request handling, core business logic, and utility functions.

### Guiding Principles
- **Separation of Concerns**: Use of `routers`, `services`, and `utils` to decouple HTTP logic from astrological calculations.
- **Consistency**: Standardized JSON outputs (ISO dates, 3-decimal longitudes) and error handling.
- **Extensibility**: Modular structure in `src/humandesign/features` allows adding new Human Design metrics without impacting existing logic.
- **Portability**: Containerized with Docker, using standard Python packaging (`pyproject.toml`).

---

## 2. Architecture Visualization

### 2.1 Component Interaction
1. **API Layer (Routers)**: Receives HTTP requests, validates input using Pydantic schemas.
2. **Service Layer**: Handles complex multi-step processes like geocoding (Nominatim), timezone resolution (TimezoneFinder), and composite orchestration.
3. **Core Engine (Features)**: Performs precise astrological calculations using `pyswisseph` (Swiss Ephemeris).
4. **Utility Layer**: Provides specialized helpers for date formatting, Western astrology, and JSON serialization.

### 2.2 Data Flow
`Client Request` -> `FastAPI Router` -> `Pydantic Validation` -> `Service/Utility (Preprocessing)` -> `Core Engine (Calculation)` -> `Serialization Helper` -> `JSON Response`

---

## 3. Core Architectural Components

### 3.1 API Routers (`src/humandesign/routers/`)
- **General**: Handles `/calculate` and `/bodygraph`.
- **Composite**: Handles relationships (`/analyze/composite`, `/analyze/compmatrix`, `/analyze/penta`).
- **Transits**: Handles `/transits/daily` and `/transits/solar_return`.

### 3.2 Core Calculation Engine (`src/humandesign/features/`)
- **`core.py`**: The `hd_features` class managing planet positions and gate mappings.
- **`attributes.py`**: Calculation of Type, Strategy, Authority, and Profile.
- **`mechanics.py`**: Logic for Splits/Definitions and Penta group dynamics.

### 3.3 Services (`src/humandesign/services/`)
- **`geolocation.py`**: Integration with Nominatim for latitude/longitude resolution.
- **`chart_renderer.py`**: SVG/PNG rendering logic for the BodyGraph.

### 3.4 Utilities (`src/humandesign/utils/`)
- **`astrology.py`**: Western zodiac calculations.
- **`date_utils.py`**: ISO formatting and age calculation.
- **`health_utils.py`**: Live dependency verification (Swiss Ephemeris).
- **`version.py`**: Centralized version retrieval from `pyproject.toml`.
- **`serialization.py`**: Custom JSON encoders for NumPy compatibility.

---

## 4. Cross-Cutting Concerns

### 4.1 Monitoring & Health
- **System Health**: A dedicated `/health` endpoint in `routers/general.py` provides real-time status of the API and its data dependencies (Swiss Ephemeris).
- **Version Synchronization**: The system enforces a single-source-of-truth for versioning using `pyproject.toml`, retrieved via `utils/version.py`.

### 4.2 Authentication
- Implemented via `dependencies.py` using a Bearer token verification system.
- Enforced at the router level using FastAPI's `Depends(verify_token)`.

### 4.3 Error Handling
- Use of `fastapi.HTTPException` for consistent error responses (400 for bad input, 500 for calculation errors).
- Geocoding and timezone resolution include fallback logic (e.g., defaulting to UTC).

### 4.4 Validation
- Input validation is handled strictly by Pydantic models in `schemas/input_models.py`.
- Includes custom validators for year ranges (1800-2100) and day-of-month logic (leap years).

---

## 5. Technology-Specific Patterns (Python/FastAPI)

- **Asynchronous Programming**: FastAPI routes are designed for high-concurrency request handling.
- **Dependency Enrichment**: Routing logic leverages common dependencies for clean code and shared state.

---

## 6. Testing Architecture

- **Core Tests**: Snapshot-based testing for astrological accuracy in `tests/test_core_calculations.py`.
- **Integration Tests**: Verification of API endpoints and serialization in `tests/test_calculate_updates.py`.
- **Data Validation Tests**: Boundary condition testing for Pydantic schemas in `tests/test_schemas.py`.

---

## 7. Blueprint for New Development

### Adding a New Endpoint
1. Define the input/output schemas in `src/humandesign/schemas/`.
2. Implement the business logic in `services/` or a new module in `features/`.
3. Create a new route in the appropriate router (or a new router file).
4. Register the router in `src/humandesign/api.py`.
5. Update `openapi.yaml` and `docs/API_DOCUMENTATION.md`.

### Adding a New HD Metric
1. Locate the relevant sub-module in `src/humandesign/features/`.
2. Update the `hd_features` class or helper functions.
3. Update `serialization.py` to include the new data in the JSON output.
4. Add a regression test in `tests/`.

---

*Blueprint generated for Version 1.5.1 on 2025-12-30*
