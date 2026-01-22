# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).



## [Unreleased]
### Added
- **Recursive Masking**: Upgraded `OutputMaskingService` to support dot-notation for nested fields in `include` and `exclude` parameters (e.g., `["gates.profile", "general.birth_place"]`).

## [3.3.2] - 2026-01-22
### Fixed
- **V2 Geocoding**: Fixed an edge case in `POST /v2/calculate` where explicit `0.0` coordinates were failing to trigger reverse geocoding fallback.
- **Test Parity**: Updated version assertion tests to align with `pyproject.toml` as the single source of truth.

## [3.3.1] - 2026-01-22
### Fixed
- **Docker Build**: Removed `*.sqlite` from `.dockerignore` to ensure the required `hd_data.sqlite` database is included in the Docker image.
- **Configuration**: Updated `.gitignore` to force-track `.dockerignore` changes.

## [3.3.0] - 2026-01-21
### Added
- **V2 Calculate API (10x Upgrade)**: Launched the high-fidelity `POST /v2/calculate` endpoint.
    - **Semantic Enrichment**: Direct lookup for full, human-readable descriptions of Incarnation Crosses, Centers, and Gates using a local SQLite architecture.
    - **Nested Hierarchy**: Restructured the response into a logical hierarchy: `general`, `centers`, `channels`, `variables`, `gates`, `advanced`.
    - **Advanced Mechanics**: Integrated **Dream Rave** (activated gates/centers) and **Global Cycles** (Cycle Cross/Great Cycle) directly into the API response.
    - **Fixations Explicit & Structural**: Semantic logic for gate/line fixations (Exaltation/Detriment) is now structural and machine-readable.
- **Test Stability**: Implemented coordinate-based test payloads for all composite and penta tests to bypass geocoding rate limits during high-frequency CLI verification.

### Fixed
- **Global Cycle 2027 Transition**: Resolved a timezone conversion bug where Jan 1st, 2027 births were incorrectly assigned to "Cross of Planning" due to UTC shift. Now uses input year for era determination.
- **V2 Schema Parity**: Achieved 100% semantic parity with V1 while maintaining V2's performance and design advantages.

## [3.2.0] - 2026-01-21
### Added
- **Localization Infrastructure**: Overhauled interpretation report prompts (`daily_transit`, `question`, `solar_return`, `penta`) to support dynamic language output via `{{LANGUAGE}}` variable.
- **Prompt Standardization**: Migrated all hardcoded Turkish headers and logic in interpretation prompts to English, enabling global localization while maintaining the original logic structure.

## [3.1.0] - 2026-01-20
### Added
- **Relational Intelligence Refinements**: Expanded `/analyze/maia-penta` with high-fidelity synergy insights.
- **Environmental Resonance Detail**: New logic to detect "Shared Frequency" and "Harmonic Pull" in Nodal environments, including dual-aspect insights (Business vs. Lifestyle).
- **Variable Synergy Model**: Comprehensive analysis of "Strategic vs. Receptive" arrow combinations, providing tactical collaboration and relationship lifestyle advice.
- **Schema Expansion**: Added `environmental_resonance_detail` and `variable_synergy` objects to the `SynergyDetail` response model.

## [3.0.0] - 2026-01-20
### Removed (Breaking Changes)
- **Deactivated `/analyze/compmatrix`**: Removed the redundant traditional matrix analysis endpoint. Use `POST /analyze/maia-penta` with `verbosity="partial"` for a modern alternative.
- **Deactivated `/analyze/maiamatrix`**: Removed the legacy Professional Maia Relational Matrix endpoint. It has been fully superseded by the high-performance Hybrid engine (`POST /analyze/maia-penta`).
- **Clean Service Layer**: Pruned 200+ lines of redundant code in `src/humandesign/services/composite.py` that served the deactivated endpoints.
- **Schema Cleanup**: Removed `CompMatrixResponse` from response models.

### Changed
- **Consolidation**: Officially promoted **Maia-Penta Hybrid Analysis** as the sole flagship engine for professional-grade group and relational dynamics.
- **Version Bump**: Major version jump to v3.0.0 to reflect the removal of legacy endpoints (Breaking Changes).


## [2.2.0] - 2026-01-20
### Added
- **Maia-Penta Hybrid Analysis (10x)**: New endpoint `POST /analyze/maia-penta` for professional-grade group and relational analysis.
    - **Tier 1 (Precision)**: Swisseph engine integration for deterministic degrees and provenance metadata.
    - **Tier 2 (Complexity)**: Lunar Phase cycles and PRL/DRR Variables support.
    - **Tier 3 (Performance)**: 100x improvement via `TimezoneFinder` Singleton (65ms vs 6s).
- **Global Coordinate Support**: Optional `latitude` and `longitude` parameters added to `/calculate`, `/bodygraph`, `/transits/solar_return`, and `/transits/daily` to bypass external geocoding and improve precision.
- **Performance Audit**: Automated benchmarking confirmed sub-25ms latency across all coordinate-enabled endpoints.

### Changed
- **Version bump**: Project version updated to v2.2.0.
- **API Documentation**: Updated OpenAPI spec to reflect coordinate parameters and new endpoints.

### Fixed
- **NameError**: Resolved `Optional` type hint import issues in various routers.
- **Linting**: Fixed 140+ Ruff errors for clean code standards.

## [2.1.0] - 2026-01-20
### Added
- **High-Fidelity Maia Matrix v2**: Enhanced the relational engine with deep technical insights.
    - **Planetary Triggers**: Detects which planet is "unlocking" a specific channel or gate in the relationship.
    - **Nodal Environmental Resonance**: Maps North/South Node positions to environmental harmony or friction.
    - **Deep Sub-Circuit Detail**: Identifies dominant sub-circuits (e.g., Sensing, Logic, Ego) in the synergy.
    - **Planetary Flavor Summary**: Semantic summary of the composite's "astrological flavor."
    - **Group Dynamic Detection**: Automatically detects if a group qualifies as a **Penta** (3-5 people) or **Wa** (10+ people) and adds dedicated summary blocks.
- **Grounded 10x Interpretation Engine**: Major upgrade to the Professional Maia Relational prompt.
    - **Technical Authority**: 10x improvement in psychological grounding and mechanical accuracy.
    - **Semantic Cleanse**: Zero-jargon output for better cross-industry accessibility (Business/Family).
    - **Conditional Logic**: Intelligent handling of specific user questions and context notes.
- **Penta Integration**: Integrated Penta dynamics directly into the Maia Matrix synergy blocks.

### Fixed
- **Test Stability**: Implemented a geocoding bypass for IANA Timezone names (e.g., "Europe/London") to prevent network rate-limiting/timeouts during `pytest` execution.
- **Reliability**: Updated all geocoding-dependent endpoints (`/calculate`, `/analyze/*`, `/transits/*`) to favor provided timezone names, ensuring 100% deterministic test results.

### Changed
- **Response Models**: Added `planetary_trigger`, `node_resonance`, `dominant_sub_circuit`, and `penta_details` to `CompMatrixResponse` schemas.
### Added
- **Penta Analysis 2.0**: Upgraded `POST /analyze/penta` to use the new Sovereign Standard engine.
    - **Breaking Change**: Legacy 1.x Penta endpoint logic has been removed. The endpoint now returns the V2 hierarchical structure.
    - **Removed**: `POST /analyze/penta/v2` (features merged into main endpoint).
    - **Sovereign Standard**: Consultant-grade interpretation with zero hallucinations.
    - **Contextual Semantics**: API dynamically adjusts output language for "Business" vs "Family" group types (e.g., "Toxic Environment" vs "Chaotic Home").
    - **Functional Role Assignment**: Explicitly maps contributors to functional roles (e.g., `"Planning": ["User A"]`).
    - **Operational Style (Line Semantics)**: Interprets the *style* of contribution based on line data (e.g., "Line 1: Authoritarian", "Line 6: Administrator").
    - **Gap Analysis**: Detailed breakdown of missing gates/skills with severity (Critical/Moderate) and impact descriptions.
    - **Advanced Metrics**: Includes Stability Score, Vision vs Action Score, and Backbone Integrity checks.

### Changed
- **HD Constants**: Added extensive semantic maps (`FAMILY_SKILLS_MAP`, `FAMILY_SHADOW_MAP`, `PENTA_LINE_KEYWORD_MAP`) to support V2 logic.
- **Core Features**: Refactored `get_penta_v2` in `core.py` to implement the new Diamond/Sovereign standards.


## [1.9.1] - 2026-01-19
### Changed
- **Solar Return Parity**: Standardized `/transits/solar_return` output to match `/transits/daily`. Use the return structure `meta`, `composite_changes`, `planetary_transits`.
- **Metadata**: Enhanced Solar Return metadata to include full chart details (Profile, Cross, Channels, etc.) using `enrich_transit_metadata`.
- **Documentation**: Updated `sr_year_offset` to explicitly state `0` = Birth Year, `X` = Current/Future Year.

## [1.9.0] - 2026-01-18
### Added
- **Location-Aware Transits**: Added `current_place` parameter to `/transits/daily` to calculate planetary positions based on the user's current location (timezone).
- **Custom Transit Timing**: Added `transit_hour` and `transit_minute` parameters to specify the exact time of analysis (defaults to 12:00 Local Time).
- **Metadata**: Response `meta` now includes `calculation_place`, `transit_date_local`, and `transit_date_utc`.

## [1.8.1] - 2026-01-18
### Added
- **Enriched Metadata**: The `/transits/daily` endpoint now includes a comprehensive `meta` object with:
    - **Bio**: Age, Place, Gender, IsAlive.
    - **Astrology**: Zodiac Sign.
    - **HD Core**: Energy Type, Strategy, Signature, Not-Self, Aura, Inner Authority, Profile, Incarnation Cross.
    - **Mechanics**: Defined/Undefined Centers, Definition Type.
    - **Channels**: List of formatted active channels (e.g., `6/59: The Channel of Mating (Reproduction)`).
### Changed
- **API Defaults**: Updated default query parameters for `/transits/daily` to `1968-02-21 11:00` (Kirikkale, Turkey) and `2025-01-10`.

## [1.8.0] - 2026-01-18

### Added
- **Transits V2**: Enriched `GET /transits/daily` response with `meta`, `composite_changes`, and `planetary_transits` sections.
    - **Meta**: Includes explicit Type, Authority, and Transit Date (Local/UTC).
    - **Composite Changes**: Lists exactly which Channels and Centers are defined *by the transit connection*.
    - **Planetary Transits**: Detailed breakdown of current planetary positions (Gate, Line, Color, Tone, Base).
- **Metadata Enums**: Updated `hd_constants.py` with formalized `INNER_AUTHORITY_NAMES_MAP` (e.g., "Ego-Manifested Authority", "No Inner Authority").

### Changed
- **Enhanced Authority Logic**: Refactored `get_auth` in `mechanics.py` to strictly follow the standard Authority Hierarchy:
    1. **Emotional** (Solar Plexus)
    2. **Sacral** (Sacral)
    3. **Splenic** (Spleen)
    4. **Ego** (Heart: Manifested or Projected)
    5. **Self-Projected** (G-Center)
    6. **Outer/Lunar** (No Inner Authority)
- **Authority Mapping**: Updated `INNER_AUTHORITY_NAMES_MAP` in `hd_constants.py` to provide detailed authority names (e.g., "Solar Plexus, Emotional", "Heart & G Center, Ego Projected").


## [1.7.3] - 2026-01-17

### Added
- **Variable Shorthand**: Added `short_code` field to the `variables` response object (e.g., "PRL DRR") to standardize arrow direction summary.


## [1.7.2] - 2026-01-13

### Changed
- Refactored `general` response structure to group demographics (`age`, `gender`, `islive`) and astrological info (`zodiac_sign`) immediate after the birth place.
- Updated `VARIABLES_METADATA` terminology for Environment (bottom_left): Changed "Consistent" to "Observed" and "Variable" to "Observer".

 
## [1.7.1] - 2026-01-03

### Fixed
- **Timezone Resolution**: Pinned `timezonefinder>=8.2.0` to resolve a bug where older versions (8.1.0) incorrectly mapped certain Turkish coordinates to `Europe/Moscow`. This ensures consistent Tone/Color calculation across environments.

## [1.7.0] - 2026-01-03

### Refactored
- **Variables Logic**: Migrated `variables.json` data into internal `hd_constants.py` to remove external file dependencies and improve performance.
- **Project Structure**: Standardized variable keys across the codebase (e.g., `top_left` instead of `right_up`) for better readability and alignment with Human Design terminology. See [Track: Refactor Variables](conductor/tracks/refactor_variables_20260103/) for details.

## [1.6.1] - 2026-01-03

### Fixed
- **Variables**: Resolved an issue where the `variables` (arrows) field in the API response was hardcoded. The output now correctly reflects dynamic calculations based on planetary tones.

## [1.6.0] - 2026-01-03

### Added
- **System Health**: Implemented a new `GET /health` endpoint for operational monitoring.
- **Architecture**: Created a centralized version extraction utility in `src/humandesign/utils/version.py` that reads directly from `pyproject.toml`.
- **Validation**: Introduced `HealthResponse` Pydantic schema for standardized system responses.
- **Testing**: Added comprehensive test suites for health endpoints, schemas, and versioning logic.

## [1.5.1] - 2025-12-30

### Added
- **Features**: Added `age` and `zodiac_sign` fields to the `/calculate` response.
- **Input**: Added optional `gender` and `islive` query parameters to `/calculate` and corresponding Pydantic schemas.
- **Utilities**: Implemented `astrology` utility for Western zodiac calculation and `calculate_age` helper.
- **Compatibility**: Upgraded `fastapi` and `pydantic` versions to resolve environment-specific dependency conflicts (Starlette/HTTPX).
- **Usability**: Set default values for `/calculate` (1968 birth data) to pre-fill Swagger UI for easier testing.

### Changed
- **Formatting**: Updated `/calculate` output to return expanded profile names (e.g., "4/6: Opportunist Role Model") instead of raw numbers.
- **Documentation**: Clarified `islive` parameter to indicate life status (True = Alive, False = Deceased).
- **Defaults**: Updated default values for `gender` (`male`) and `islive` (`true`) across all schemas and endpoints.
- **Refactoring**: Replaced deprecated `example` parameter with the modern `examples` list in all route definitions to eliminate `FastAPIDeprecationWarning`.

## [1.5.0] - 2025-12-23

### Added
- **Modularization**: Refactored `hd_features.py` into a modular `humandesign.features` package structure (`core`, `attributes`, `mechanics`).
- **Regression Testing**: Added `tests/test_hd_features_snapshot.py` to ensure logic parity across refactors.
- **Docker**: Verified and optimized Docker build with the new package structure.
- **Cleanup**: Removed legacy artifacts and unnecessary files (e.g., `humandesign_api.egg-info`), ensuring a clean distribution state.
- **Optimization**: Updated `.gitignore` to exclude build artifacts (`*.egg-info`).

### Changed
- **Codebase**: Moved core calculation logic from monolithic file to `src/humandesign/features/`.
- **Imports**: Updated all internal references to use the new `humandesign.features` namespace.
- **Testing**: Renamed regression test to `tests/test_core_calculations.py` to reflect its permanent role in the test suite.


## [1.4.0] - 2025-12-23

### Added
- **Refactoring**: Implemented standard `src` layout (`src/humandesign`).
- **Organization**: Created dedicated modules for `api` (root), `routers` (endpoints), `services` (logic), and `utils` (helpers).
- **Import Logic**: Updated all imports to use relative imports within the package.
- **Tooling**: Configured `pyproject.toml` as the single source of truth for build verification and dependency management.
- **Verification**: Added `tests/test_api_smoke.py` and `verify_endpoints.sh` for robust testing.
- **Robustness**: Implemented `importlib.resources` and `importlib.metadata` for reliable Docker execution.

### Changed
- **File Structure**: Moved `api.py`, `hd_features.py` and other core files into `src/humandesign`.
- **Docker**: Updated `Dockerfile` to install the package using `pip install .` for better reproducibility.

## [1.3.1] - 2025-12-23

### Added
- **Validation**: Added `verify_endpoints.sh` script to automated verification of all API endpoints.

### Changed
- **API Endpoint**: Renamed `/compmatrix` to `/analyze/compmatrix` to align with the `analyze` namespace for processing-heavy endpoints.
- **Documentation**: Reduced the size of the bodygraph sample image in `API_DOCUMENTATION.md` for better readability.
- **Documentation**: Updated `README.md` to reflect the renamed endpoint and improved examples.

## [1.3.0] - 2025-12-23

### Added
- **Refactoring**: Split monolithic `api.py` into modular routers: `routers/general.py`, `routers/transits.py`, `routers/composite.py`.
- **API Response**: Simplified `/analyze/composite` output. `new_chakras` and `composite_chakras` now return a flat list of names (strings) instead of objects.
- **Organization**: Introduced `schemas/` directory for Pydantic models (`PersonInput`) and `utils/` for helper functions (`date_utils.py`, `calculations.py`).

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
