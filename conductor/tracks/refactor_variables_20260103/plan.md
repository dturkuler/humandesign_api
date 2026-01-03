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

## Phase 2: Project-Wide Key Refactoring [checkpoint: 6710ee2]
- [x] Task: specific key replacement in `hd_constants.py` and core logic.
    - **Description:** Replace `right_up` -> `top_right`, `left_up` -> `top_left`, etc. in the core calculation logic.
    - **Step 1:** detailed `grep` to find all occurrences.
    - **Step 2:** Update unit tests primarily to expect new keys.
    - **Step 3:** Update `hd_constants.py` and any calculation modules.
    - **Step 4:** Verify tests pass.
- [x] Task: Refactor API Models.
    - **Description:** Update schemas.py (or pydantic models) to use new keys.
    - **Step 1:** Update Pydantic models.
    - **Step 2:** Ensure any transformation logic in serialization.py or routers maps correctly.
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: API Response Transformation [checkpoint: 6710ee2]
- [x] Task: Update Router/Controller Logic.
    - **Description:** Ensure the API returns the new nested structure (value, name, aspect, def_type).
    - **Step 1:** Create test `test_variables_structure.py` to assert the nested structure.
    - **Step 2:** Modify `get_variables` in `attributes.py` to construct the full object.
    - **Step 3:** Run tests to confirm correct nesting and values.
- [x] Task: Final Cleanup.
    - **Description:** Delete `.docs/hddata/variables.json` if confirmed unused.
    - **Step 1:** Delete the file.
    - **Step 2:** Run all tests affecting variables.
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)
