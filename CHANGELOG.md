# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).



## [Unreleased]

## [1.2.6] - 2025-12-23

### Added
- **New Endpoint**: `POST /analyze/composite` for detailed pairwise composite analysis.
- **Enhanced Output**: Returns `new_channels`, `duplicated_channels`, `new_chakras`, and `composite_chakras` with full descriptive names.
- **Core Logic**: Exposed `hd.composite_chakras_channels` logic directly via API for granular relationship mechanics.

### Changed
- **Documentation**: Updated `hd_constants.py` to ensure all output fields use human-readable names mapped from `CHAKRA_NAMES_MAP`.

### Added
- **Penta Analysis**: Added `POST /analyze/penta` endpoint to calculate group dynamics (Penta) for 3-5 people. Returns match percentage and active gates breakdown per person.
- **Core Logic**: Refactored `hd_features.get_penta` to return detailed data `(percentage, details_dict)` without side effects or reliance on global state.

### Changed

- **API Response**: Renamed the output field `split` to `definition` across all endpoints (`/calculate`, `/bodygraph`, `/transits`, etc.) to better align with Human Design terminology.
- **API Response**: Standardized all date outputs to ISO 8601 UTC format (`YYYY-MM-DDTHH:MM:SSZ`) across all endpoints.
- **API Response**: Added `birth_place` field to `/calculate` and `/transits` output.
- **API Response**: Standardized all longitude outputs to 3 decimal places for cleaner JSON responses.
- **Documentation**: Updated `README.md` and Knowledgebase to reflect the new `definition` field and ISO date formats.

### Fixed
- **Calculation Logic**: Resolved a `TypeError` in `hd_features.py` where the recursive function `definition` was incorrectly shadowing the imported function name. `get_definition` is now correctly called.

## [1.2.1] - 2025-12-22

### Changed
- **Version Management**: Switched to `pyproject.toml` for version management, replacing `version.py`.
- **API**: Updated `api.py` to read version dynamically from `pyproject.toml`.

## [1.2.0] - 2025-12-21

### Added
- **New Endpoint**: `POST /compmatrix` for composite chart analysis with robust validation.
- **Enriched Composite Analysis**: `run_composite_combinations.py` now outputs comprehensive Human Design profiles (Type, Strategy, Aura, Channels) for each person involved.
- **Input Validation**: `api.py` now implements strict Pydantic validation (ranges, dates) and supports flexible string inputs (e.g., `minute="00"`) for numeric fields.
- **Structured JSON Output**: Composite analysis results are now normalized with separate `persons` dictionaries and `combinations` lists.
- **Geocoding & Timezone**: Integrated automatic location-to-coordinates and timezone resolution for input data.
- **Descriptive Mappings**: Output now utilizes full descriptive names for Centers, Authorities, and Incarnation Crosses instead of internal codes.

### Fixed
- **JSON Serialization**: Implemented custom `NumpyEncoder` to resolve `TypeError: Object of type int64 is not JSON serializable` when handling HD calculation results.

## [1.1.0] - 2025-12-19

### Added
- **AuraCycle Module**: Implemented new functionality for strategic timing and planning based on planetary transits.
- **Daily Transit Analysis**: Added `GET /transits/daily` endpoint to calculate the "Weather of the Day" (Composite Chart of User + Current Transit).
- **Solar Return Analysis**: Added `GET /transits/solar_return` endpoint to calculate the "Yearly Theme" (Solar Return Chart).
- **Core Logic**: Enhanced `hd_features.py` with `calc_solar_return_jd` and `get_solar_return_date` methods using `swisseph` for precise astronomical return calculations.

## [1.0.5] - 2025-12-12

### Added
- **BodyGraph Visualization**: New `chart.py` module to generate high-fidelity Human Design BodyGraph charts based on extracted vector geometry.
- **New API Endpoint**: Added `GET /bodygraph` endpoint to `api.py` that returns the generated chart image directly.
- **Image Formats**: Support for `png` (transparent background), `svg` (vector), and `jpg`/`jpeg` (white background) output formats.
- **Dependencies**: Added `matplotlib`, `svgpath2mpl`, and `Pillow` to `requirements.txt`.
- **Layout Data**: Added `layout_data.json` containing precise SVG paths and coordinates for centers, channels, and gates, extracted from XAML reference.
- **Versioning**: Implemented centralized version tracking via `version.py` and exposed it in the API info.

### Changed
- **API Response**: `api.py` updated to include `Response` and `image/*` media types handling.
- **Documentation**: Updated `README.md` to include usage instructions for the new `/bodygraph` endpoint.
- **Geocode**: Updated `geocode.py` to conditionally run sample code only when executed directly, cleaning up logs during import.

### Fixed
- **G Center Rendering**: Corrected the parsing logic to properly handle XAML MatrixTransforms, ensuring the G Center is drawn as a diamond (rotated 45 degrees) instead of a square.
- **Channel Rendering**: Implemented correct logic to draw inactive channels as gray background lines and active channels (Design/Personality) as colored overlays (Red/Black/Striped).
