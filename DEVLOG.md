# Development Log

> [!TIP]
> **Token Economy:** Only the active task and the last 3 completed entries are kept here. Older entries are archived in [DEVLOG_HISTORY.md](file:///home/alice/Repositorios/RPG/DEVLOG_HISTORY.md).

## ACTIVE TASK: [None]

---

## RECENT HISTORY

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
