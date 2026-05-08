# Plan: Audit Battle Module Test Quality

## Objective
Verify if tests in `tests/battle` follow the standards defined in `[ARCH.TEST_QUALITY]` and evaluate the organization of the test suite.

## Steps
1. **Inventory and Initial Scan:**
    - Examine the file list in `tests/battle`.
    - Identify the primary focus of each test file (Unit, Integration, Edge Case).

2. **Quality Audit (Rule by Rule):**
    - **[ARCH.TEST_QUALITY.TEST_BEHAVIOR]:** Check if assertions focus on final state (HP, status) instead of internals.
    - **[ARCH.TEST_QUALITY.MOCKING]:** Ensure `DiceManager` is used instead of manual random mocks.
    - **[ARCH.TEST_QUALITY.ENTITY_FACTORY]:** Check for `tests.utils.entity_factory`.
    - **[ARCH.TEST_QUALITY.ATTACK_ACTION_DATA]:** specifically check `test_GolpeDeEscudo.py` and action tests for `DataManager` usage.
    - **[ARCH.TEST_QUALITY.LIFECYCLE]:** Check for EventBus baseline assertions.
    - **[ARCH.TEST_QUALITY.STRUCTURED_HISTORY]:** Ensure `TAG|...` assertions are used.

3. **Organizational Review:**
    - Evaluate if the distribution of files (e.g., `test_BattleActions.py` vs `test_GolpeDeEscudo.py`) is consistent.
    - Check for redundancy.

4. **Reporting:**
    - Document findings and propose specific refactorings to align with standards.

## Execution
- Use `view_file` to inspect the content of the tests.
- Compare patterns across files.
