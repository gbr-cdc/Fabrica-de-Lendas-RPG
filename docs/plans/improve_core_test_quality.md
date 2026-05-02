# Plan: Improve Core Test Quality [IE.improve_core_test_quality]

This plan aims to align the `core` module test suite with the standards defined in `[ARCH.TEST_QUALITY]`, specifically reducing excessive mocking and adopting the `entity_factory`.

## Proposed Changes

### 1. `tests/core/test_BaseClasses.py`
- Replace `MagicMock` for `actor` with real `Character` instances using `create_dummy_character`.
- Replace `MagicMock` for `context` with a minimal real context if possible, or a structured dummy.

### 2. `tests/core/test_Events.py`
- Replace `MagicMock` for `character` and `target` with real `Character` instances using `create_dummy_character`.

### 3. `tests/core/test_DiceManager.py`
- Refactor to use seeds instead of mocking `random.randint` where possible to ensure determinism while using the real implementation.

### 4. `tests/entities/test_Characters.py` (Core Logic)
- This file tests `CharacterSystem` (which is in `core/`). 
- Replace manual fixture creation with `create_dummy_character` and other `entity_factory` utilities.
- Ensure behavior-based assertions (e.g., checking HP values) are preserved but using standard starting states.

### 5. `tests/core/test_Modifiers.py` & `test_Structs.py`
- Review to ensure they are fully compliant (already seem to be in good shape).

## Verification Plan

- Run `pytest tests/core` to ensure all improved tests pass.
- Run `pytest tests/entities/test_Characters.py` to ensure character system tests pass.
- Verify that `MagicMock` usage is minimized in the targeted files.
