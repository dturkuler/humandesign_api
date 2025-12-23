# Tests

This directory contains the automated test suite for the Human Design API.

## Test Files

- **[`test_core_calculations.py`](test_core_calculations.py)**: **Regression Test Suite**.
    - Uses a canonical snapshot of a known chart (Jan 1, 2024, 12:00 UTC, London) to verify that `hd_features` logic remains consistent.
    - Checks Type, Authority, Profile, Channels, Gates, and Centers against hardcoded expected values.
    - **Critical**: This test safeguards the core astrological logic during refactoring.
- **[`test_api_smoke.py`](test_api_smoke.py)**: **Smoke Test**.
    - Verifies that the FastAPI app initializes correctly and the `/docs` endpoint is reachable (`200 OK`).
    - Basic health check for the web server layer.

## Running Tests

Run the full suite using `pytest` from the project root:

```bash
pytest
```
