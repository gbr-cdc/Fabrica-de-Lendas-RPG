# Development Log History

## 2026-04-20: Project Reorganization
**Plan:** [project_reorganization.md](docs/plans/project_reorganization.md)

**Overall Idea:**
Structural cleanup — rename/move files and folders with no logic changes. Renamed `combat/` → `battle/`, moved docs to `docs/`, removed stale tracked files, renamed `core/Bases.py` → `core/BaseClasses.py`, moved `DiceCalculator.py` to `utilities/`.

**Steps:**
- [x] Remove stale tracked files. | Files: `test_output.txt`.
- [x] Move design documents to `docs/`. | Files: `GDD Sistema de Batalha.md`, `Sistema_RPG_Regras.txt`.
- [x] Move utility script to `utilities/`. | Files: `DiceCalculator.py`.
- [x] Rename core base classes and update imports. | Files: `core/BaseClasses.py`, `tests/core/test_BaseClasses.py`.
- [x] Rename combat module to battle and update imports. | Files: `battle/`, `tests/battle/`.

## 2026-04-20: PvP Simulator Path Fix

**Overall Idea:**
Fix `ModuleNotFoundError` when running `Main.py` directly from the project root by adding the root directory to `sys.path`.

**Steps:**
- [x] Inject project root into `sys.path` in simulator entry point. | Files: `pvp_simulator/Main.py`.
- [x] Verify execution from terminal. | Files: `pvp_simulator/`.

## 2026-04-20: Timeline Tie-Breaking Logic
**Plan:** [timeline_tie_breaking.md](docs/plans/timeline_tie_breaking.md)

**Overall Idea:**
Implement game-compliant tie-breaking in the combat timeline where higher HAB and d10 rolls determine turn order on tied ticks. Delegate logic from Controller (Simulator) to Model (BattleManager).

**Steps:**
- [x] Create `tests/combat/test_timeline_logic.py` with tie-break scenarios. | Files: `tests/combat/test_timeline_logic.py`.
- [x] Modify `BattleManager.add_character` to support 5-element tuple and roll d10. | Files: `combat/BattleManager.py`.
- [x] Modify `BattleManager.schedule_next_action` to roll d10. | Files: `combat/BattleManager.py`.
- [x] Update `BattleManager.get_next_actor` and `delay_character` for new tuple structure. | Files: `combat/BattleManager.py`.
- [x] Cleanup `pvp_simulator/Simulator.py`: Remove manual tie-break logic. | Files: `pvp_simulator/Simulator.py`.
- [x] Verify with tests and simulation. | Files: `tests/combat/`, `pvp_simulator/`.

## 2026-04-20: PvP Simulator Refactor
**Plan:** [update_pvp_simulator.md](docs/plans/update_pvp_simulator.md)

**Overall Idea:**
Update `pvp_simulator/Simulator.py` to delegate turn logic to `BattleManager.run_battle()`, resolving architectural debt and ensuring compatibility with the current data-driven engine.

**Steps:**
- [x] Refactor `PvPSimulator` initialization to use `DataManager` and `BattleJudge`. | Files: `pvp_simulator/Simulator.py`.
- [x] Replace `single_battle_verbose` manual loop with `battle_manager.run_battle()`. | Files: `pvp_simulator/Simulator.py`.
- [x] Replace `single_battle_summary` manual loop with `battle_manager.run_battle()`. | Files: `pvp_simulator/Simulator.py`.
- [x] Verify compatibility with `simulate_multiple_battles` and `Main.py`. | Files: `pvp_simulator/Simulator.py`, `pvp_simulator/Main.py`.
- [x] Fixed missing `weapon_type` in `CombatStyles.json`. | Files: `data/CombatStyles.json`.

## 2026-04-20: Decouple Combat Logic from Character Entity
**Plan:** [combat_decoupling.md](docs/plans/combat_decoupling.md)

**Overall Idea:**
Remove logic dependencies from the `Character` entity by redirecting lifecycle and resource method calls to the `CharacterSystem` utility class, fulfilling Rule 1.13.

**Steps:**
- [x] Add `team: int = 0` data attribute to `Character`. | Files: `entities/Characters.py`.
- [x] Refactor `Judges.py` (replace `is_alive`). | Files: `combat/Judges.py`.
- [x] Refactor `BattleActions.py` (replace all resource/lifecycle calls). | Files: `combat/BattleActions.py`.
- [x] Verify fix with `pvp_simulator/Main.py`. | Files: `pvp_simulator/`.

## 2026-04-20: Orchestration Rule Refinement

**Overall Idea:**
Fix inconsistencies in agent rules regarding atomic tasks, planning workflow, and logging synchronization.

**Steps:**
- [x] Refactor `agent_rules.md`: Optimize for size and clarity. | Files: `agent_rules.md`.
- [x] Sync `DEVLOG.md`: Update status of orchestration tasks. | Files: `DEVLOG.md`.

## 2026-04-20: Character Data Container Refactor

**Overall Idea:** 
Refactor the `Character` class to strictly act as a data container (anemic domain model) per the "Plain Character Sheet" architectural rule. All domain logic must be stripped from the entity and moved into a dedicated stateless system. The combat engine must be updated to track character "brains" (controllers) externally rather than injecting them into the data object.

**Steps Completed:**
- [x] Create `core/CharacterSystem.py` for isolated domain logic. | Files: `core/CharacterSystem.py`.
- [x] Strip verb methods and `controller` from `Character`. | Files: `entities/Characters.py`.
- [x] Refactor `BattleManager` to track controllers. | Files: `battle/BattleManager.py`.
- [x] Update character tests. | Files: `tests/entities/test_Characters.py`.
- [x] Update engine and simulator for external controllers. | Files: `battle/BattleManager.py`, `pvp_simulator/Simulator.py`.
- [x] Verify all 47 tests pass. | Files: `tests/`.

## 2026-04-20: Graça do Duelista Bugfix and Test Coverage

**Overall Idea:**
Add unit tests for the `GraçaDoDuelista` BattlePassive to ensure it properly modifies Attack Load (GdA) and handles evasion reactions. Also, fix a regression in `GracaDoDuelista` introduced by the Character Refactor, where the passive attempted to directly access `self.owner.controller` and `self.owner.spend_focus` which are no longer available on the plain data container.

**Steps Completed:**
- [x] Extend `IBattleContext` for controller access. | Files: `core/BaseClasses.py`, `battle/BattleManager.py`.
- [x] Refactor `GracaDoDuelista` for new systems. | Files: `battle/BattlePassives.py`.
- [x] Add unit tests for hit/reaction scenarios. | Files: `tests/battle/test_BattlePassives.py`.
- [x] Verify tests pass with `pytest`. | Files: `tests/`.

## 2026-04-20: DEVLOG and Agent Rules Optimization

**Overall Idea:**
Reduce token usage by implementing an archiving system for `DEVLOG.md`.

**Steps Completed:**
- [x] Archive legacy tasks to `DEVLOG_HISTORY.md`. | Files: `DEVLOG.md`, `DEVLOG_HISTORY.md`.
- [x] Implement Log Archiving policy in `agent_rules.md`. | Files: `agent_rules.md`.
