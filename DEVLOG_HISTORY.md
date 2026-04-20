# Development Log History

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
Systematically expand the test suite to cover all remaining branches and edge cases.

**Steps Completed:**

## 2026-04-20: DEVLOG and Agent Rules Optimization

**Overall Idea:**
Reduce token usage by implementing an archiving system for `DEVLOG.md`.

**Steps Completed:**
- [x] Archive legacy tasks to `DEVLOG_HISTORY.md`. | Files: `DEVLOG.md`, `DEVLOG_HISTORY.md` | Status: Done.
- [x] Implement Log Archiving policy in `agent_rules.md`. | Files: `agent_rules.md` | Status: Done.
