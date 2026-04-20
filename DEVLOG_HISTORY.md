# Development Log History

## 2026-04-20: Timeline Tie-Breaking Logic

**Overall Idea:**
Implement game-compliant tie-breaking in the combat timeline where higher HAB and d10 rolls determine turn order on tied ticks. Delegate logic from Controller (Simulator) to Model (BattleManager).

**Steps:**
- [x] Create `tests/combat/test_timeline_logic.py` with tie-break scenarios. | Files: `tests/combat/test_timeline_logic.py` | Status: Done.
- [x] Modify `BattleManager.add_character` to support 5-element tuple and roll d10. | Files: `combat/BattleManager.py` | Status: Done.
- [x] Modify `BattleManager.schedule_next_action` to roll d10. | Files: `combat/BattleManager.py` | Status: Done.
- [x] Update `BattleManager.get_next_actor` and `delay_character` for new tuple structure. | Files: `combat/BattleManager.py` | Status: Done.
- [x] Cleanup `pvp_simulator/Simulator.py`: Remove manual tie-break logic. | Files: `pvp_simulator/Simulator.py` | Status: Done.
- [x] Verify with tests and simulation. | Files: `tests/combat/`, `pvp_simulator/` | Status: Done.

## 2026-04-20: PvP Simulator Refactor

**Overall Idea:**
Update `pvp_simulator/Simulator.py` to delegate turn logic to `BattleManager.run_battle()`, resolving architectural debt and ensuring compatibility with the current data-driven engine.

**Steps:**
- [x] Refactor `PvPSimulator` initialization to use `DataManager` and `BattleJudge`. | Files: `pvp_simulator/Simulator.py` | Status: Done.
- [x] Replace `single_battle_verbose` manual loop with `battle_manager.run_battle()`. | Files: `pvp_simulator/Simulator.py` | Status: Done.
- [x] Replace `single_battle_summary` manual loop with `battle_manager.run_battle()`. | Files: `pvp_simulator/Simulator.py` | Status: Done.
- [x] Verify compatibility with `simulate_multiple_battles` and `Main.py`. | Files: `pvp_simulator/Simulator.py`, `pvp_simulator/Main.py` | Status: Done.
- [x] Fixed missing `weapon_type` in `CombatStyles.json`. | Files: `data/CombatStyles.json` | Status: Done.

## 2026-04-20: Decouple Combat Logic from Character Entity

**Overall Idea:**
Remove logic dependencies from the `Character` entity by redirecting lifecycle and resource method calls to the `CharacterSystem` utility class, fulfilling Rule 1.13.

**Steps:**
- [x] Add `team: int = 0` data attribute to `Character`. | Files: `entities/Characters.py` | Status: Done.
- [x] Refactor `Judges.py` (replace `is_alive`). | Files: `combat/Judges.py` | Status: Done.
- [x] Refactor `BattleActions.py` (replace all resource/lifecycle calls). | Files: `combat/BattleActions.py` | Status: Done.
- [x] Verify fix with `pvp_simulator/Main.py`. | Files: `pvp_simulator/` | Status: Done.

## 2026-04-20: Orchestration Rule Refinement

**Overall Idea:**
Fix inconsistencies in agent rules regarding atomic tasks, planning workflow, and logging synchronization.

**Steps:**
- [x] Refactor `agent_rules.md`: Optimize for size and clarity. | Files: `agent_rules.md` | Status: Done.
- [x] Sync `DEVLOG.md`: Update status of orchestration tasks. | Files: `DEVLOG.md` | Status: Done.

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

## 2026-04-20: DEVLOG and Agent Rules Optimization

**Overall Idea:**
Reduce token usage by implementing an archiving system for `DEVLOG.md`.

**Steps Completed:**
- [x] Archive legacy tasks to `DEVLOG_HISTORY.md`. | Files: `DEVLOG.md`, `DEVLOG_HISTORY.md` | Status: Done.
- [x] Implement Log Archiving policy in `agent_rules.md`. | Files: `agent_rules.md` | Status: Done.
