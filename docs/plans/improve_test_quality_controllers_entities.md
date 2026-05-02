# Test Quality Improvement Plan [ARCH.TEST_QUALITY.PLAN]

This plan aims to modernize the test suite for `controllers` and `entities` modules, adhering to `[ARCH.TEST_QUALITY]` standards.

## Objectives
- **Reduce Mocking:** Replace `unittest.mock` with real domain objects (`Character`, `Weapon`, `Armor`) and a concrete `TestContext`.
- **Behavioral Testing:** Ensure tests verify outcomes (HP changes, action choices) rather than implementation details.
- **Remove Redundancy:** Eliminate "coverage-only" tests for dataclasses that don't provide behavioral value.
- **Standardize Instantiation:** Use `tests.utils.entity_factory` for all entity creation.

## Proposed Changes

### 1. `tests/entities/test_Items.py`
- **Action:** Delete file.
- **Rationale:** `Weapon` and `Armor` are pure data containers (dataclasses). Their initialization is implicitly tested by `CharacterSystem` equipment tests and `entity_factory` usage. They currently offer no behavior to test independently.

### 2. `tests/entities/test_Characters.py`
- **Action:** 
    - Replace `MagicMock` in `test_character_status_effects` with a lightweight concrete `StatusEffect` or a generic implementation.
    - Review all tests to ensure they use `entity_factory` exclusively.
    - Ensure `CharacterSystem` interactions are verifying the side effects on the `Character` entity.

### 3. `tests/controllers/test_CharacterController.py`
- **Action:** 
    - Replace all `MagicMock` (actor, target, context) with real `Character` instances and `TestContext`.
    - Remove `patch('battle.BattleActions.registry')`. Instead, rely on the real registry or ensure the `TestContext` handles action resolution if needed. (Note: `PvP1v1Controller` imports from `battle.BattleActions`, so we should ensure the environment is set up correctly).
    - Verify that `choose_action` returns the expected `BattleAction` instance type with correct targets.

### 4. `tests/utils/test_context.py` (Created)
- **Action:** Already created `TestContext` to provide a non-mocked implementation of `IBattleContext`.

## Verification Plan
- Run `pytest tests/controllers/test_CharacterController.py`
- Run `pytest tests/entities/test_Characters.py`
- Run the full test suite to ensure no regressions: `pytest`
