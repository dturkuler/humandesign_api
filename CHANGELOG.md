# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
