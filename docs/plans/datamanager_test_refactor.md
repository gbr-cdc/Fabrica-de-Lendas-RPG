# Execution Plan: DataManager Test Refactoring

## Problem Statement
The current `tests/core/test_DataManager.py` relies heavily on hardcoded JSON values (e.g., checking if "Destruidor" has a specific stat). This violates the `[ARCH.TEST_QUALITY.TEST_BEHAVIOR]` standard because balance changes in JSON data break logic tests.

## Goal
Decouple testing from specific JSON values. The tests should focus on ensuring that the `DataManager` correctly reads from files, extracts keys, and hydrates Python objects (including Enums) properly. 

## Steps
1. **Create Utility**: 
   - Create `tests/utils/json_integrity_checker.py`.
   - Implement `get_json_keys(filepath: str) -> list[str]` to dynamically fetch keys from the JSON files.

2. **Refactor `tests/core/test_DataManager.py`**:
   - Refactor `test_load_combat_styles` to dynamically iterate through all loaded styles and verify their properties are initialized with the correct types (e.g., `isinstance(style.main_stat, AttributeType)`), instead of hardcoding expected values.
   - Refactor `test_load_action_templates` similarly, ensuring `len(dm._action_templates) > 0` and that loaded items have valid `BattleActionType` and `AttackType` enums.
   - Refactor `test_load_game_rules` to just check that `dm._game_rules` is properly populated without relying on specific hardcoded level/HP values.
   - Refactor `test_load_characters_success` to dynamically load all characters from JSON and ensure all fields (weapon, armor, abilities) are instantiated correctly.

3. **Validation**: 
   - Run `python3 -m pytest tests/core/test_DataManager.py` to ensure all tests pass and effectively validate the integrity of the JSON schema and the DataManager's logic.

4. **Documentation**:
   - Document the newly created `tests/utils/json_integrity_checker.py` using `utilities/ref_manager.py` following the existing `[AGENT.REF_MANAGER.CONVENTIONS]`.
