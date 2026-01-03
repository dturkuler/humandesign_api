# Implementation Plan - Refactor Variables Output

## Phase 1: Data Migration & Internal Structure [checkpoint: cc1e63c]
- [x] Task: Create `VARIABLES_METADATA` constant in `src/humandesign/hd_constants.py`.
    - **Description:** Migrate key data from `.docs/hddata/variables.json` to a Python dictionary. Structure it to support the new response format (name, aspect, def_type logic).
    - **Step 1:** Create `test_refactor_constants.py` to verify the new constant exists and contains correct data for all 4 positions.
    - **Step 2:** Implement `VARIABLES_METADATA` in `hd_constants.py`.
    - **Step 3:** Run tests to confirm.
- [x] Task: Remove `variables.json` dependency.
    - **Description:** Identify where `variables.json` is currently loaded (likely in `utils.py` or a data loader) and refactor to use `VARIABLES_METADATA`.
    - **Step 1:** Search for usages of `variables.json`.
    - **Step 2:** Update code to use the imported constant.
    - **Step 3:** Verify no file I/O errors occur.
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Project-Wide Key Refactoring
- [ ] Task: specific key replacement in `hd_constants.py` and core logic.
    - **Description:** Replace `right_up` -> `top_right`, `left_up` -> `top_left`, etc. in the core calculation logic.
    - **Step 1:** detailed `grep` to find all occurrences.
    - **Step 2:** Update unit tests primarily to expect new keys.
    - **Step 3:** Update `hd_constants.py` and any calculation modules.
    - **Step 4:** Verify tests pass.
- [ ] Task: Refactor API Models.
    - **Description:** Update Pydantic models to use the new naming convention.
    - **Step 1:** Update `schemas.py` (or equivalent).
    - **Step 2:** Ensure Pydantic validation passes with new keys.
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: API Response Transformation
- [ ] Task: Update Router/Controller Logic.
    - **Description:** specific logic to construct the nested `variables` object in the API response using `VARIABLES_METADATA`.
    - **Step 1:** Create `test_variables_response.py` asserting the complex nested structure.
    - **Step 2:** Modify the route handler (e.g., `routers/general.py`) to build the dictionary dynamically.
    - **Step 3:** Run tests to confirm correct nesting and values.
- [ ] Task: Final Cleanup.
    - **Description:** Delete `.docs/hddata/variables.json` if confirmed unused.
    - **Step 1:** Delete file.
    - **Step 2:** Run full test suite.
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)
