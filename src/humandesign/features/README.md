# Human Design Features Engine

This package (`src/humandesign/features`) contains the core astrological and Human Design calculation logic. It was refactored in v1.5.0 from a monolithic file into modular components.

## Modules

- **[`core.py`](core.py)**: The main entry point `hd_features` class. Orchestrates calculations by calling specialized functions in submodule and aggregating results.
- **[`mechanics.py`](mechanics.py)**: Handles the "mechanics" of the chart:
    - **Center Activation**: Determining defined vs. undefined centers.
    - **Channel Definition**: Identifying active channels based on gate activation.
    - **Definition Type**: Calculating Split, Single, Triple, or Quadruple definition.
    - **Aura Type & Authority**: Deriving Energy Type (Generator, Projector, etc.) and Authority.
- **[`attributes.py`](attributes.py)**: specialized lookups for high-level attributes:
    - **Profiles**: (e.g., 1/3, 4/6).
    - **Incarnation Crosses**: Determining the life theme based on Sun/Earth gates.
    - **Variables**: Left/Right orientation of digestion etc.
