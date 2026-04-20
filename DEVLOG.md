# Development Log

## 2026-04-20: Character Data Container Refactor

**Overall Idea:** 
Refactor the `Character` class to strictly act as a data container (anemic domain model) per the "Plain Character Sheet" architectural rule. All domain logic must be stripped from the entity and moved into a dedicated stateless system. The combat engine must be updated to track character "brains" (controllers) externally rather than injecting them into the data object.

**Steps Completed:**
- [x] Create `core/CharacterSystem.py` to hold isolated domain logic (mana, focus, damage, equipment).
- [x] Strip verb methods and `controller` dependency from `entities/Characters.py`.
- [x] Refactor `combat/BattleManager.py` to track character controllers internally via `add_character`.
- [x] Update `tests/entities/test_Characters.py` to test against `CharacterSystem`.
- [x] Update `tests/combat/test_BattleManager.py` and `pvp_simulator/Simulator.py` to pass controllers into the engine.
- [x] Verify all 47 tests pass.

## 2026-04-20: Graça do Duelista Bugfix and Test Coverage

**Overall Idea:**
Add unit tests for the `GraçaDoDuelista` BattlePassive to ensure it properly modifies Attack Load (GdA) and handles evasion reactions. Also, fix a regression in `GracaDoDuelista` introduced by the Character Refactor, where the passive attempted to directly access `self.owner.controller` and `self.owner.spend_focus` which are no longer available on the plain data container.

**Steps Completed:**
- [x] Extend `IBattleContext` and `BattleManager` to expose a `get_controller(char_id)` method.
- [x] Refactor `GracaDoDuelista` to use `self.context.get_controller()` and `CharacterSystem.spend_focus()`.
- [x] Add `test_graca_do_duelista_acerto` and `test_graca_do_duelista_reacao` in `tests/combat/test_BattlePassives.py`.
- [x] Verify tests pass with `pytest`.

## 2026-04-20: Achieving 100% Test Coverage for RPG Combat Engine

**Overall Idea:**
Systematically expand the test suite to cover all remaining branches and edge cases in the combat engine, ensuring 100% code coverage across all core modules. This includes testing anemic data loading, complex passive interactions, battle manager error states, and logic clamping.

**Steps Completed:**
- [x] Configure `.coveragerc` to exclude non-testable blocks (TYPE_CHECKING, NotImplementedError).
- [x] Implement comprehensive tests for `core/DataManager.py`, `core/DiceManager.py`, and `core/Modifiers.py`.
- [x] Expand `entities/Characters.py` coverage to 100% (stat getters, equipment validation).
- [x] Target logic edge cases in `combat/BattleActions.py` (GdA clamping, focus/mana validation).
- [x] Create `tests/combat/test_EngineEdgeCases.py` for `BattleManager` (decision loops, death resolution, timeline empty errors).
- [x] Achieve 100% coverage on `BattlePassives.py`, `StatusEffects.py`, `Judges.py`, and `CharacterController.py`.
- [x] Verify final 100% total coverage with `pytest-cov`.

