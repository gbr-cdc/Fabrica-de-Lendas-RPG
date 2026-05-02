# Implementation Plan - Improve Battle Test Quality [PLAN.BATTLE_TEST_QUALITY]

The goal is to refactor the test suite for the `battle` module to adhere to `[ARCH.TEST_QUALITY]` standards, reducing mocking and focusing on behavioral verification.

## 1. Refactor `tests/battle/test_BattleManager.py`
- **Replace Mocks with Entities:** Use `create_dummy_character` from `tests.utils.entity_factory` for all actors.
- **Real Services:** Use real `BattleManager` and `BattleJudge`.
- **Scheduled Dice:** Use `DiceManager.schedule_result()` instead of mocking `roll_dice`.
- **Event Auditing:** Ensure `test_battle_manager_try_finally_hooks` correctly verifies EventBus cleanup.

## 2. Refactor `tests/battle/test_BattleActions.py`
- **Behavioral Verification:** Focus on final HP and state changes rather than verifying specific method calls.
- **Remove Patches:** Avoid `unittest.mock.patch` for `CharacterSystem` logic; use the real system with the dummy characters.
- **Deterministic Rolls:** Use `DiceManager.schedule_result()` to control outcomes in `AttackAction` tests.

## 3. Refactor `tests/battle/test_StatusEffects.py` and `tests/battle/test_BattlePassives.py`
- **Invariant Checks:** Add assertions to verify that attributes are correctly modified and restored.
- **Decoupling:** Remove dependencies on internal list structures or private state if possible.

## 4. Verification
- Run the refactored tests using `pytest`.
- Ensure all tests pass and are more robust to internal changes.
- Verify `EventBus` subscriber count returns to baseline where applicable.

## Execution Order
1.  `test_BattleManager.py`
2.  `test_BattleActions.py`
3.  Other battle tests...
