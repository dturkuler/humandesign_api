# Application Services

This directory (`src/humandesign/services`) contains the business logic layer and service orchestrators. It bridges the gap between raw calculations (`features/`) and the API layer (`routers/`).

## Modules

- **[`chart_renderer.py`](chart_renderer.py)**: Generates BodyGraph images.
    - Uses `matplotlib` and `svgpath2mpl` to render the chart.
    - Loads geometry from `data/layout_data.json`.
- **[`geolocation.py`](geolocation.py)**: Resolves location strings to coordinates.
    - Uses `geopy` and `timezonefinder` to determine Latitude, Longitude, and Timezone.
- **[`composite.py`](composite.py)**: Logic for composite charts.
    - `CompositeHandler`: Processes multiple `PersonInput` objects to find connections and shared definitions.
