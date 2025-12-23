# Project Architecture Blueprint

**Generated:** 2025-12-23 for Version 1.5.0
**Project Type:** Python (FastAPI)
**Architecture Pattern:** Modular Layered Architecture

## 1. Architectural Overview

The Human Design API utilizes a **Modular Layered Architecture** built on top of the **FastAPI** framework. The primary goal is to provide a clean separation of concerns between HTTP handling (Routers), business logic (Services), and core domain calculations (Features/Utils).

### Guiding Principles
- **Separation of Concerns**: distinctive boundaries between entry points, logic, and data processing.
- **Statelessness**: The API is fully stateless, relying on Bearer tokens for auth.
- **Single Source of Truth**: Configuration and versioning are centralized in `pyproject.toml`.
- **Reproducibility**: Builds are standardized via `pip install .` and Docker.
- **Package-Oriented**: Uses `src` layout and `importlib` for robust resource loading across environments (Local vs Docker).

## 2. Component Relationships

### Subsystem Boundaries
- **Entry Points (`routers/`)**: Handle HTTP requests, parsing, and validation.
- **Service Layer (`services/`)**: Orchestrates complex logic (e.g., Geocoding + SwissEph).
- **Core Domain (`hd_features.py`, `hd_constants.py`)**: Pure functions containing the "physics" of Human Design.
- **Utilities (`utils/`)**: Shared helpers for date handling, math, and serialization.
- **Data (`data/`)**: Static assets (SVG layouts) loaded via `importlib.resources`.

### Data Flow
1.  **Request**: Client sends encoded birth data.
2.  **Router**: Validates input using Pydantic schemas (`schemas/`).
3.  **Service**:
    - Resolves location (via `geolocation.py`).
    - Calculates mechanics (via `hd_features.py`).
    - Renders visual assets (via `chart_renderer.py`) loading `layout_data.json` from package resources.
4.  **Response**: JSON or Image data returned to client.

## 3. Core Architectural Components

### `api.py` (Application Root)
- **Responsibility**: Bootstraps the FastAPI app, configures middleware, and includes routers.
- **Implementation**: Uses `importlib.metadata` to retrieve version at runtime.

### `routers/` (Interface Adapters)
- **Components**: `general.py`, `transits.py`, `composite.py`.
- **Responsibility**: Map HTTP verbs to service calls.

### `services/` (Application Business Rules)
- **Components**:
    - `geolocation.py`: Adapter for `geopy`/`timezonefinder`.
    - `chart_renderer.py`: Logic for generating BodyGraphs. Uses `importlib.resources` to read `data/layout_data.json` safely.
    - `composite.py`: Orchestrator for multi-person analysis.

### `src/humandesign/features/` (Domain Core)
- **Components**:
    - `core.py`: Main `hd_features` class and core calculation entry points.
    - `attributes.py`: Helper functions for attributes (Profile, Incarnation Cross).
    - `mechanics.py`: Logic for Centers, Channels, and Definition mechanics.
- **Responsibility**: The "Engine". Contains all calculation formulas for Gates, Lines, Tones, Bases, and Centers. Using a modular package structure.

## 4. Cross-Cutting Concerns

### Authentication
- **Pattern**: Bearer Token via `dependencies.verify_token` against `HD_API_TOKEN`.

### Configuration
- **Source**: `.env` file or Environment Variables.
- **Access**: `dependencies.py` resolves `.env` path dynamically relative to the package location.

- **Deployment Architecture**:
  - **Structure**: Installed as a standard Python package (`pip install .`) in `/usr/local/lib/python3.12/site-packages/humandesign`.
  - **Cleanup**: Build artifacts (`*.egg-info`) are excluded from source control and regenerated during install.

## 6. Extension Patterns

### Adding New Endpoints
1.  Create validation model in `schemas/`.
2.  Implement logic in `services/`.
3.  Add route in `routers/` and register in `api.py`.

## 7. Architectural Decisions (ADRs)

### ADR-005: Modularization of Core Logic (v1.5.0)
- **Decision**: Split monolithic `hd_features.py` into `humandesign.features` package.
- **Reason**: The file grew too large (>1000 lines) making maintenance difficult. Modularization respects separation of concerns (Mechanics vs Attributes) and improves testability.

### ADR-004: Resource Loading via Importlib (v1.4.0)
- **Decision**: Use `importlib.resources` and `importlib.metadata`.
- **Reason**: Standard file paths (e.g. `../data`) fail when the package is installed in Docker. `importlib` ensures correct resolution in all environments.

### ADR-001: Src Layout (v1.4.0)
- **Decision**: Move all code to `src/humandesign`.
- **Reason**: Avoid import ambiguities, cleaner root directory, standard Python packaging practice.
