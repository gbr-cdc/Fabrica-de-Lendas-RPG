# Mission Log

## RECENT HISTORY
- [2026-04-23 00:18: Area Attacks Implementation [PART 2]](MISSION_HISTORY.md#2026-04-23-0018-area-attacks-implementation-part-2)
- [2026-04-22 20:33: Area Attacks Implementation [PART 1]](MISSION_HISTORY.md#2026-04-22-2033-area-attacks-implementation-part-1)
- [2026-04-22 09:35: Targeting System Refactor](MISSION_HISTORY.md#2026-04-22-0935-targeting-system-refactor)

> [!TIP]
> **Token Economy:** Only **[ACTIVE]** missions are kept here. Completed entries are moved to [MISSION_HISTORY.md](file:///home/alice/Repositorios/RPG/MISSION_HISTORY.md).
> **Step Format:** `- [ ] Description | Files: path/to/file.py` → On completion: `- [x] Description | Files: ... | Note: 1-sentence state summary`.

## MISSION: Core Module Integrity (ACTIVE) [PART 1]
- **Summary**: Refactor foundational tests in the `core` module to eliminate mock abuse. Replace `MagicMock` with real object instances (`Character`, `StatModifier`, `GameRules`) to verify behavioral outcomes and system integrity.
- **Rule References**: ARCH.1.5, ARCH.1.8, ARCH.1.9
- **Plan**: [test_quality_improvement.md](docs/plans/test_quality_improvement.md)
- **Steps**:
    - [ ] [BLUE] [Implementation]: Refactor `test_Modifiers.py` to use real `Character` and `StatModifier` instances. Assert final stat totals instead of internal list modifications. | Files: tests/core/test_Modifiers.py
    - [ ] [BLUE] [Implementation]: Refactor `test_DataManager.py` to verify data loading from real `data/` JSONs, ensuring structural integrity between files and objects. | Files: tests/core/test_DataManager.py
    - [ ] [BLUE] [Implementation]: Refactor `test_DiceManager.py` to use deterministic roll scheduling for behavior verification without mocking the manager's logic. | Files: tests/core/test_DiceManager.py
    - [ ] [BLUE] [Implementation]: Update `test_BaseClasses.py` and `test_Structs.py` to ensure core data containers and interfaces are verified as behavior-driving entities. | Files: tests/core/test_BaseClasses.py, tests/core/test_Structs.py

## MISSION: Battle Orchestration & Logic (ACTIVE) [PART 1]
- **Summary**: Refactor `battle/` module tests to verify combat outcomes using real objects. Eliminate `MagicMock` for Characters, Actions, and Judges in favor of integration scenarios.
- **Rule References**: ARCH.1.2, ARCH.1.3, ARCH.2.1, ARCH.2.2
- **Plan**: [test_quality_improvement.md](docs/plans/test_quality_improvement.md)
- **Steps**:
    - [ ] [BLUE] [Implementation]: Refactor `test_BattleManager.py` to replace `MagicMock` characters with real `Character` instances and verify timeline/tick logic. | Files: tests/battle/test_BattleManager.py
    - [ ] [BLUE] [Implementation]: Refactor `test_BattleActions.py` to assert behavioral outcomes (damage, resource cost) instead of `execute()` call counts. | Files: tests/battle/test_BattleActions.py
    - [ ] [BLUE] [Implementation]: Refactor `test_BattlePassives.py` to verify event-driven triggers with real payloads and state modifications. | Files: tests/battle/test_BattlePassives.py
    - [ ] [BLUE] [Implementation]: Refactor `test_StatusEffects.py` and `test_Judges.py` to verify duration-based modifications and win/loss conditions with real entities. | Files: tests/battle/test_StatusEffects.py, tests/battle/test_Judges.py

## MISSION: Controllers, Entities & Data (ACTIVE) [PART 1]
- **Summary**: Grouped refactor for smaller modules. Ensure `CharacterController` decision loops and entity stat calculations are verified as system behaviors.
- **Rule References**: ARCH.1.1, ARCH.1.5, ARCH.1.9
- **Plan**: [test_quality_improvement.md](docs/plans/test_quality_improvement.md)
- **Steps**:
    - [ ] [BLUE] [Implementation]: Refactor `test_CharacterController.py` to verify `PvP1v1Controller` decisions in real scenarios without mocking internal logic. | Files: tests/controllers/test_CharacterController.py
    - [ ] [BLUE] [Implementation]: Refactor `test_Characters.py` to verify complex modifier stacks and `get_stat_total` accuracy with real data. | Files: tests/entities/test_Characters.py
    - [ ] [BLUE] [Implementation]: Implement a Data Integrity Test to validate all JSON files in `data/` against their Python struct definitions. | Files: tests/core/test_DataManager.py

## MISSION: System Integration & Regression (ACTIVE) [PART 1]
- **Summary**: Final verification of engine stability through full combat scenarios and invariant assertions.
- **Rule References**: ARCH.GLOBAL
- **Plan**: [test_quality_improvement.md](docs/plans/test_quality_improvement.md)
- **Steps**:
    - [ ] [BLUE] [Implementation]: Create high-level scenario tests (e.g., Duel Scenarios) that run battles from start to finish and assert final outcomes. | Files: tests/battle/test_EngineEdgeCases.py
    - [ ] [BLUE] [Implementation]: Implement invariant checks (e.g., non-negative HP, sorted timeline) to be run across all combat integration tests. | Files: tests/battle/test_BattleManager.py
