# API Routers

This directory (`src/humandesign/routers`) contains the `FastAPI` router modules that define the application's HTTP endpoints.

## Modules

- **[`general.py`](general.py)**: Handles the primary calculation endpoints:
    - `GET /calculate`: Full chart analysis.
    - `GET /bodygraph`: Image generation (proxies to `services.chart_renderer`).
- **[`transits.py`](transits.py)**: Handles prognostic endpoints:
    - `GET /transits/daily`: Current transit weather.
    - `GET /transits/solar_return`: Yearly Solar Return charts.
- **[`composite.py`](composite.py)**: Handles relationship analysis:
    - `POST /analyze/composite`: Detailed pairwise analysis (channels, centers).
    - `POST /analyze/compmatrix`: Multi-person matrix.
    - `POST /analyze/penta`: Group dynamics (Penta) analysis.
