# MISSION LOG [MISSION.GLOBAL]

## ACTIVE MISSIONS [MISSION.ACTIVE]

### MISSION: Core Module Integrity [MISSION.ACTIVE.CORE_MODULE_INTEGRITY]
- **Summary**: Refactor foundational tests in the `core` module to eliminate mock abuse. Replace `MagicMock` with real object instances (`Character`, `StatModifier`, `GameRules`) to verify behavioral outcomes and system integrity.
- **Rule References**: [ARCH.RULES.CORE.DATA_DRIVEN], [ARCH.RULES.CORE.MODIFIER], [ARCH.RULES.CORE.ENTITIES]
- **Definition of Done**: Core tests pass using real object instances instead of mocks. Internal logic is verified via state assertions.
- **Plan**: [test_quality_improvement.md](docs/plans/test_quality_improvement.md)
- **Steps**:
    - [x] [BLUE] [Implementation]: Refactor `test_Modifiers.py` to use real `Character` and `StatModifier` instances. Assert final stat totals instead of internal list modifications. | Files: tests/core/test_Modifiers.py | State: Modifiers verified with real Character objects loaded via DataManager. Behavioral assertions replaced mock-based logic. All 6 tests passing.
    - [x] [BLUE] [Implementation]: Implement `create_dummy_entity` utility to generate valid random entities (Characters, Weapons, Armor) for testing based on [GDD.CORE.ATTR], [GDD.CORE.PROG], and [GDD.EQUIP.TIERS]. | Files: tests/utils/entity_factory.py | State: Utility implemented and verified. Successfully generates Characters, Weapons, and Armor with GDD-compliant stats scaled by attributes and tiers.
    - [x] [BLUE] [Implementation]: Correct modifications made in the first mission step in tests/core/test_Modifiers.py to use the create_dummy_entity utility instead of DataManager to create characters. | Files: tests/core/test_Modifiers.py tests/utils/entity_factory.py | State: Refactor verified. DataManager dependency removed from test_Modifiers.py; characters now created via create_dummy_character. All 6 tests passing.
    - [x] [BLUE] [Implementation]: Refactor `test_DataManager.py` to verify data loading from real `data/` JSONs, ensuring structural integrity between files and objects. | Files: tests/core/test_DataManager.py | State: DataManager tests refactored to use real data/ JSONs for happy paths, ensuring integration with actual project data. 11 tests passing.
    - [ ] [BLUE] [Implementation]: Update `test_BaseClasses.py` and `test_Structs.py` to ensure core data containers and interfaces are verified as behavior-driving entities. | Files: tests/core/test_BaseClasses.py, tests/core/test_Structs.py

### MISSION: Battle Orchestration & Logic [MISSION.ACTIVE.BATTLE_ORCHESTRATION_AND_LOGIC]
- **Summary**: Refactor `battle/` module tests to verify combat outcomes using real objects. Eliminate `MagicMock` for Characters, Actions, and Judges in favor of integration scenarios.
- **Rule References**: [ARCH.RULES.CORE.COMMAND], [ARCH.RULES.CORE.OBSERVER], [ARCH.ENGINE.TIMELINE], [ARCH.ENGINE.PAYLOAD]
- **Definition of Done**: Combat outcomes (damage, timeline, status) are verified via integration tests with real entities.
- **Plan**: [test_quality_improvement.md](docs/plans/test_quality_improvement.md)
- **Steps**:
    - [ ] [BLUE] [Implementation]: Refactor `test_BattleManager.py` to replace `MagicMock` characters with real `Character` instances and verify timeline/tick logic. | Files: tests/battle/test_BattleManager.py
    - [ ] [BLUE] [Implementation]: Refactor `test_BattleActions.py` to assert behavioral outcomes (damage, resource cost) instead of `execute()` call counts. | Files: tests/battle/test_BattleActions.py
    - [ ] [BLUE] [Implementation]: Refactor `test_BattlePassives.py` to verify event-driven triggers with real payloads and state modifications. | Files: tests/battle/test_BattlePassives.py
    - [ ] [BLUE] [Implementation]: Refactor `test_StatusEffects.py` and `test_Judges.py` to verify duration-based modifications and win/loss conditions with real entities. | Files: tests/battle/test_StatusEffects.py, tests/battle/test_Judges.py

### MISSION: Controllers, Entities & Data [MISSION.ACTIVE.CONTROLLERS_ENTITIES_DATA]
- **Summary**: Grouped refactor for smaller modules. Ensure `CharacterController` decision loops and entity stat calculations are verified as system behaviors.
- **Rule References**: [ARCH.RULES.CORE.MVC], [ARCH.RULES.CORE.DATA], [ARCH.RULES.CORE.ENTITIES]
- **Definition of Done**: AI controllers and entity stats are verified through behavior tests. JSON definitions are validated against Python structs.
- **Plan**: [test_quality_improvement.md](docs/plans/test_quality_improvement.md)
- **Steps**:
    - [ ] [BLUE] [Implementation]: Refactor `test_CharacterController.py` to verify `PvP1v1Controller` decisions in real scenarios without mocking internal logic. | Files: tests/controllers/test_CharacterController.py
    - [ ] [BLUE] [Implementation]: Refactor `test_Characters.py` to verify complex modifier stacks and `get_stat_total` accuracy with real data. | Files: tests/entities/test_Characters.py
    - [ ] [BLUE] [Implementation]: Implement a Data Integrity Test to validate all JSON files in `data/` against their Python struct definitions. | Files: tests/core/test_DataManager.py

### MISSION: System Integration & Regression (ACTIVE) [MISSION.ACTIVE.SYSTEM_INTEGRATION_AND_REGRESSION]
- **Summary**: Final verification of engine stability through full combat scenarios and invariant assertions.
- **Rule References**: [ARCH.GLOBAL]
- **Definition of Done**: Engine stability is confirmed via end-to-end battle scenarios and continuous invariant assertions.
- **Plan**: [test_quality_improvement.md](docs/plans/test_quality_improvement.md)
- **Steps**:
    - [ ] [BLUE] [Implementation]: Create high-level scenario tests (e.g., Duel Scenarios) that run battles from start to finish and assert final outcomes. | Files: tests/battle/test_EngineEdgeCases.py
    - [ ] [BLUE] [Implementation]: Implement invariant checks (e.g., non-negative HP, sorted timeline) to be run across all combat integration tests. | Files: tests/battle/test_BattleManager.py

## ARCHIVED MISSIONS [MISSION.ARCHIVE]

### 2026-04-23 00:18: Area Attacks Implementation [PART 2] [MISSION.ARCHIVE.AREA_ATTACKS_IMPLEMENTATION_PART_2]
**Plan:** [area_attacks.md](docs/plans/area_attacks.md)

**Overall Idea:**
Completed the core logic for area-effect attacks in the battle engine. Refactored `AttackAction.execute` to implement a "Master Roll" phase where a single attack roll is performed and then shared across all targets. Individual defense rolls and damage resolution are maintained for each target. Added comprehensive tests to verify single-roll distribution and ensure passive safety.

**Steps:**
- [x] Refactor `AttackAction.execute` to trigger a single attack roll when `self.attack_type == AttackType.AREA` | Files: battle/BattleActions.py | Note: Implemented Master Roll logic that shares one roll across all targets.
- [x] Implement iterative loop for target defense/damage using the shared attack roll result | Files: battle/BattleActions.py | Note: Targets now resolve individual defense and damage using the shared Master Roll.
- [x] Create tests validating one attack roll vs multiple defense rolls in area scenarios | Files: tests/battle/test_area_attacks.py | Note: Verified single-roll distribution and safety for passives like Postura Defensiva.

### 2026-04-22 20:33: Area Attacks Implementation [PART 1] [MISSION.ARCHIVE.AREA_ATTACKS_IMPLEMENTATION_PART_1]
**Plan:** [area_attacks.md](docs/plans/area_attacks.md)

**Overall Idea:**
Updated core event infrastructure and passive safety to support area-effect attacks. This included adding the `AREA` attack type, making the `target` field optional in `AttackLoad` (for shared master rolls), and implementing safety checks in `PosturaDefensiva` to prevent crashes when a target is missing. Fixed pre-existing test suite breakages caused by the recent multi-target refactor.

**Steps:**
- [x] Add `AREA = "area"` to `AttackType` enum | Files: `core/Enums.py` | Note: Added AREA to AttackType enum.
- [x] Update `AttackLoad` dataclass to allow `target: Character | None = None` (required for shared rolls) | Files: `core/Events.py` | Note: Made target optional in AttackLoad.
- [x] Audit all `on_roll_modify` hooks. Wrap any logic that accesses `attack_load.target` in an `if attack_load.target is not None:` check. | Files: `battle/BattlePassives.py` | Note: Added safety check to PosturaDefensiva.penalty_hook.
- [x] Add unit test verifying `AttackLoad` supports optional targets | Files: `tests/core/test_Events.py` | Note: Verified AttackLoad flexibility with new tests.


### 2026-04-22 09:35: Targeting System Refactor [MISSION.ARCHIVE.TARGETING_SYSTEM_REFACTOR]
**Plan:** [targeting_system.md](docs/plans/targeting_system.md)

**Overall Idea:**
Refactor the RPG battle engine to support multi-target actions, enabling future integration of AOE mechanics and map-based targeting. Updated `BattleAction` interface and subclasses to accept a list of targets. Updated `AttackAction` to iteratively resolve attacks against all targets. Refactored `PosturaDefensiva` to track multiple hit targets simultaneously using a dictionary-based state.

**Steps:**
- [x] Update `BattleAction` interface to accept `targets: List[Character]` | Files: `core/BaseClasses.py` | Note: Changed target to targets list and added backward-compatible property.
- [x] Update `PvP1v1Controller` to provide targets as a list | Files: `controllers/CharacterController.py` | Note: All AttackAction calls now pass targets as a single-element list.
- [x] Refactor `AttackAction` and other actions to handle multi-targeting | Files: `battle/BattleActions.py` | Note: AttackAction now loops over targets and aggregates history.
- [x] Update `PosturaDefensiva` tracking logic for multiple targets | Files: `battle/BattlePassives.py` | Note: Replaced single tracking with a dict and updated all hooks.
- [x] Update and verify tests for multi-target mechanics | Files: `tests/battle/test_postura_defensiva.py` | Note: Verified with existing tests and a new multi-target test suite.


### 2026-04-21 17:37: Postura Defensiva [MISSION.ARCHIVE.POSTURA_DEFENSIVA]
**Plan:** [postura_defensiva.md](docs/plans/postura_defensiva.md)

**Overall Idea:**
Implement the "Postura Defensiva" toggleable passive for the Destruidor combat style. This included adding infrastructure for free actions in the battle timeline, refactoring character dice to a modifier-stack pattern, and implementing hit-tracking logic with ephemeral precision penalties.

**Steps:**
- [x] Add `FREE_ACTION` to `BattleActionType`. | Files: `core/Enums.py`.
- [x] Refactor `atk_die`/`def_die` to properties; add `remove_modifiers_by_source(source: str)`. | Files: `entities/Characters.py`.
- [x] Add `get_active_passive()` to `IBattleContext`. | Files: `core/BaseClasses.py`.
- [x] Add `get_active_passive()` impl and refactor `run_battle()` for free-action loop. | Files: `battle/BattleManager.py`.
- [x] Implement `PosturaDefensiva` class and register it. | Files: `battle/BattlePassives.py`.
- [x] Implement `TogglePosturaDefensiva` action and register it. | Files: `battle/BattleActions.py`.
- [x] Create and verify tests for posture mechanics. | Files: `tests/battle/test_postura_defensiva.py`.


### 2026-04-20: Project Reorganization [MISSION.ARCHIVE.PROJECT_REORGANIZATION]
**Plan:** [project_reorganization.md](docs/plans/project_reorganization.md)

**Overall Idea:**
Structural cleanup — rename/move files and folders with no logic changes. Renamed `combat/` → `battle/`, moved docs to `docs/`, removed stale tracked files, renamed `core/Bases.py` → `core/BaseClasses.py`, moved `DiceCalculator.py` to `utilities/`.

**Steps:**
- [x] Remove stale tracked files. | Files: `test_output.txt`.
- [x] Move design documents to `docs/`. | Files: `GDD Sistema de Batalha.md`, `Sistema_RPG_Regras.txt`.
- [x] Move utility script to `utilities/`. | Files: `DiceCalculator.py`.
- [x] Rename core base classes and update imports. | Files: `core/BaseClasses.py`, `tests/core/test_BaseClasses.py`.
- [x] Rename combat module to battle and update imports. | Files: `battle/`, `tests/battle/`.

### 2026-04-20: PvP Simulator Path Fix [MISSION.ARCHIVE.PVP_SIMULATOR_PATH_FIX]

**Overall Idea:**
Fix `ModuleNotFoundError` when running `Main.py` directly from the project root by adding the root directory to `sys.path`.

**Steps:**
- [x] Inject project root into `sys.path` in simulator entry point. | Files: `pvp_simulator/Main.py`.
- [x] Verify execution from terminal. | Files: `pvp_simulator/`.

### 2026-04-20: Timeline Tie-Breaking Logic [MISSION.ARCHIVE.TIMELINE_TIE_BREAKING_LOGIC]
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

### 2026-04-20: PvP Simulator Refactor [MISSION.ARCHIVE.PVP_SIMULATOR_REFACTOR]
**Plan:** [update_pvp_simulator.md](docs/plans/update_pvp_simulator.md)

**Overall Idea:**
Update `pvp_simulator/Simulator.py` to delegate turn logic to `BattleManager.run_battle()`, resolving architectural debt and ensuring compatibility with the current data-driven engine.

**Steps:**
- [x] Refactor `PvPSimulator` initialization to use `DataManager` and `BattleJudge`. | Files: `pvp_simulator/Simulator.py`.
- [x] Replace `single_battle_verbose` manual loop with `battle_manager.run_battle()`. | Files: `pvp_simulator/Simulator.py`.
- [x] Replace `single_battle_summary` manual loop with `battle_manager.run_battle()`. | Files: `pvp_simulator/Simulator.py`.
- [x] Verify compatibility with `simulate_multiple_battles` and `Main.py`. | Files: `pvp_simulator/Simulator.py`, `pvp_simulator/Main.py`.
- [x] Fixed missing `weapon_type` in `CombatStyles.json`. | Files: `data/CombatStyles.json`.

### 2026-04-20: Decouple Combat Logic from Character Entity [MISSION.ARCHIVE.DECOUPLE_COMBAT_LOGIC_FROM_CHARACTER_ENTITY]
**Plan:** [combat_decoupling.md](docs/plans/combat_decoupling.md)

**Overall Idea:**
Remove logic dependencies from the `Character` entity by redirecting lifecycle and resource method calls to the `CharacterSystem` utility class, fulfilling Rule 1.13.

**Steps:**
- [x] Add `team: int = 0` data attribute to `Character`. | Files: `entities/Characters.py`.
- [x] Refactor `Judges.py` (replace `is_alive`). | Files: `combat/Judges.py`.
- [x] Refactor `BattleActions.py` (replace all resource/lifecycle calls). | Files: `combat/BattleActions.py`.
- [x] Verify fix with `pvp_simulator/Main.py`. | Files: `pvp_simulator/`.

### 2026-04-20: Orchestration Rule Refinement [MISSION.ARCHIVE.ORCHESTRATION_RULE_REFINEMENT]

**Overall Idea:**
Fix inconsistencies in agent rules regarding atomic tasks, planning workflow, and logging synchronization.

**Steps:**
- [x] Refactor `agent_rules.md`: Optimize for size and clarity. | Files: `agent_rules.md`.
- [x] Sync `MISSION_LOG.md`: Update status of orchestration tasks. | Files: `MISSION_LOG.md`.

### 2026-04-20: Character Data Container Refactor [MISSION.ARCHIVE.CHARACTER_DATA_CONTAINER_REFACTOR]

**Overall Idea:** 
Refactor the `Character` class to strictly act as a data container (anemic domain model) per the "Plain Character Sheet" architectural rule. All domain logic must be stripped from the entity and moved into a dedicated stateless system. The combat engine must be updated to track character "brains" (controllers) externally rather than injecting them into the data object.

**Steps Completed:**
- [x] Create `core/CharacterSystem.py` for isolated domain logic. | Files: `core/CharacterSystem.py`.
- [x] Strip verb methods and `controller` from `Character`. | Files: `entities/Characters.py`.
- [x] Refactor `BattleManager` to track controllers. | Files: `battle/BattleManager.py`.
- [x] Update character tests. | Files: `tests/entities/test_Characters.py`.
- [x] Update engine and simulator for external controllers. | Files: `battle/BattleManager.py`, `pvp_simulator/Simulator.py`.
- [x] Verify all 47 tests pass. | Files: `tests/`.

### 2026-04-20: Graça do Duelista Bugfix and Test Coverage [MISSION.ARCHIVE.GRACA_DO_DUELISTA_BUGFIX_AND_TEST_COVERAGE]

**Overall Idea:**
Add unit tests for the `GraçaDoDuelista` BattlePassive to ensure it properly modifies Attack Load (GdA) and handles evasion reactions. Also, fix a regression in `GracaDoDuelista` introduced by the Character Refactor, where the passive attempted to directly access `self.owner.controller` and `self.owner.spend_focus` which are no longer available on the plain data container.

**Steps Completed:**
- [x] Extend `IBattleContext` for controller access. | Files: `core/BaseClasses.py`, `battle/BattleManager.py`.
- [x] Refactor `GracaDoDuelista` for new systems. | Files: `battle/BattlePassives.py`.
- [x] Add unit tests for hit/reaction scenarios. | Files: `tests/battle/test_BattlePassives.py`.
- [x] Verify tests pass with `pytest`. | Files: `tests/`.

### 2026-04-20: DEVLOG and Agent Rules Optimization [MISSION.ARCHIVE.DEVLOG_AND_AGENT_RULES_OPTIMIZATION]

**Overall Idea:**
Reduce token usage by implementing an archiving system for `MISSION_LOG.md`.

**Steps Completed:**
- [x] Archive legacy tasks to `MISSION_HISTORY.md`. | Files: `MISSION_LOG.md`, `MISSION_HISTORY.md`.
- [x] Implement Log Archiving policy in `agent_rules.md`. | Files: `agent_rules.md`.
