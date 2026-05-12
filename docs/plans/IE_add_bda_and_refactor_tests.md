# Plan: Implement add_bda hook and refactor AttackAction tests

The goal is to implement a new `add_bda` hook for `AttackAction` effects and modernize the test suite to use programmatic test actions instead of relying on external JSON data for unit testing individual effects.

## Phase 1: Implementation
1.  **Modify `battle/BattleActions.py`**:
    *   Implement `_build_add_bda(effect, action: AttackAction) -> Dict[str, Callable]`.
    *   Register `add_bda` in `EFFECT_HOOK_BUILDERS`.
    *   The hook should listen to `on_roll_modify` and increment `attack_load.bda`.

## Phase 2: Documentation
1.  **Update `[ARCH.TEST_QUALITY]`**:
    *   Add `[ARCH.TEST_QUALITY.EFFECT_HOOKS]` instructing to test effects using programmatic templates rather than real skills.

## Phase 3: Testing & Refactoring
1.  **Refactor `tests/test_BattleActions.py`**:
    *   Update `TestAttackAction` to use a `AttackActionTemplate` created in the test for each effect scenario.
    *   Remove dependency on `data/AttackActions.json` for these specific tests.
    *   Ensure all tests pass and verify the new `add_bda` hook.

## Phase 4: Evaluation
1.  Update module documentation for `BattleActions`.
2.  Create implementation report.
