# Utilities

This directory (`src/humandesign/utils`) contains shared helper functions and utilities used across the application.

## Modules

- **[`calculations.py`](calculations.py)**: General calculation helpers.
    - `calc_single_hd_features`: Wrapper for running the full analysis pipeline for a single person.
    - `process_transit_data`: Utility to merge natal and transit data.
- **[`date_utils.py`](date_utils.py)**: Datetime manipulation.
    - `parse_datetime`: Standardizes ISO string parsing.
    - `calculate_utc_offset`: Computes offset based on timezone strings.
- **[`serialization.py`](serialization.py)**: JSON Handling.
    - `NumpyEncoder`: Custom encoder to handle `numpy.int64` and other non-standard types returned by `swisseph`, preventing JSON serialization errors.
