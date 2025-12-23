# Human Design Source Package

This directory (`src/humandesign`) contains the core application source code.

## Key Files

- **`api.py`**: The application entry point. Initializes the `FastAPI` app, includes routers, and handles global exception handlers.
- **`dependencies.py`**: Dependency injection provider. Handles authentication (Bearer token) and configuration (`.env` loading).
- **`hd_constants.py`**: Domain constants, including center names, gate definitions, and mapping dictionaries.
- **`__init__.py`**: Exposes the package version.

## Submodules

- **[`routers/`](routers/README.md)**: API route handlers (endpoints).
- **[`services/`](services/README.md)**: Business logic and orchestrators.
- **[`features/`](features/README.md)**: Core Human Design calculation engine.
- **[`schemas/`](schemas/README.md)**: Pydantic input/output models.
- **[`utils/`](utils/README.md)**: Helper functions (math, dates, serialization).
- **[`data/`](data/README.md)**: Static data assets.
