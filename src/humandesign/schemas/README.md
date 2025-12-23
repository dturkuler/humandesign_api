# Data Schemas

This directory (`src/humandesign/schemas`) contains `Pydantic` models used for request validation and response serialization.

## Modules

- **[`input_models.py`](input_models.py)**: Defines input contracts.
    - `PersonInput`: Standardizes birth data input (Year, Month, Day, Hour, Minute, Place).
    - Validates ranges (e.g., Month 1-12) and types.
