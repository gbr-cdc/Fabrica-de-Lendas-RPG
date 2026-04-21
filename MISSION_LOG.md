# Mission Log

> [!TIP]
> **Token Economy:** Only the active task and the last 3 completed entries are kept here. Older entries are archived in [MISSION_HISTORY.md](file:///home/alice/Repositorios/RPG/MISSION_HISTORY.md).
> **Step Format:** `- [ ] Description | Files: path/to/file.py` → On completion: `- [x] Description | Files: ... | Note: 1-sentence state summary`.

## MISSION: Postura Defensiva ([COMPLETE])
**Plan:** [postura_defensiva.md](docs/plans/postura_defensiva.md)

**Description:**
Lay the infrastructure for "Postura Defensiva": add the FREE_ACTION enum, refactor `atk_die`/`def_die` to modifier-stack properties on `Character`, extend `IBattleContext`, and refactor `BattleManager.run_battle()` for the free-action loop.

**Context & Constraints:**
- `ARCH.1.8` (Modifier Stack Pattern): `atk_die`/`def_die` must become properties backed by modifiers.
- `ARCH.1.3` (Observer Pattern): Passive hooks subscribed via `BattleManager`.
- Free actions must loop at the start of the turn without advancing the tick.

**Steps:**
- [x] Add `FREE_ACTION` to `BattleActionType`. | Files: `core/Enums.py` | Note: Added FREE_ACTION to BattleActionType enum.
- [x] Refactor `atk_die`/`def_die` to properties; add `remove_modifiers_by_source(source: str)`. | Files: `entities/Characters.py` | Note: Dice are now properties backed by modifiers.
- [x] Add `get_active_passive()` to `IBattleContext`. | Files: `core/BaseClasses.py` | Note: Added get_active_passive to IBattleContext protocol.
- [x] Add `get_active_passive()` impl and refactor `run_battle()` for free-action loop. | Files: `battle/BattleManager.py` | Note: Implemented get_active_passive and free action turn loop.

---

---

## MISSION: Postura Defensiva — Part 2 ([COMPLETE])
**Plan:** [postura_defensiva.md](docs/plans/postura_defensiva.md)

**Description:**
Build the `PosturaDefensiva` passive and its toggle action, then validate with a full TDD pass.

**Context & Constraints:**
- `ARCH.1.3` (Observer Pattern): Hooks subscribed via EventBus in BattleManager.
- `OP.1.2` (TDD): Tests must be green before finalizing.
- Tracking penalty must be ephemeral and clear if the target doesn't attack the owner.
- *(Part 1 Handover: FREE_ACTION logic and dice properties are ready. BattleManager supports turn-start free actions.)*

**Steps:**
- [x] Implement `PosturaDefensiva` class and register it. | Files: `battle/BattlePassives.py` | Note: Stateful passive with hit-tracking and penalty hooks.
- [x] Implement `TogglePosturaDefensiva` action and register it. | Files: `battle/BattleActions.py` | Note: Free action to toggle posture state.
- [x] Create tests for toggle logic, dice modifiers, and penalty lifecycle. | Files: `tests/battle/test_postura_defensiva.py` | Note: Full coverage for posture mechanics.
- [x] Verify implementation with pytest. | Files: `tests/battle/test_postura_defensiva.py` | Note: 92 tests passed (5 new).


---

## RECENT HISTORY

## 2026-04-20: Project Reorganization
**Plan:** [project_reorganization.md](docs/plans/project_reorganization.md)

**Overall Idea:**
Structural cleanup — rename/move files and folders with no logic changes. Renamed `combat/` → `battle/`, moved docs to `docs/`, removed stale tracked files, renamed `core/Bases.py` → `core/BaseClasses.py`, moved `DiceCalculator.py` to `utilities/`.

**Steps:**
- [x] `git rm test_output.txt` | Status: Done.
- [x] `git mv "GDD Sistema de Batalha.md" docs/` | Status: Done.
- [x] `mv Sistema_RPG_Regras.txt docs/` | Status: Done.
- [x] `git mv DiceCalculator.py utilities/DiceCalculator.py` + created `utilities/__init__.py` | Status: Done.
- [x] `git mv core/Bases.py core/BaseClasses.py` + updated all imports | Status: Done.
- [x] `git mv tests/core/test_Bases.py tests/core/test_BaseClasses.py` | Status: Done.
- [x] `git mv combat battle` | Status: Done.
- [x] `git mv tests/combat tests/battle` | Status: Done.
- [x] Grep-replaced all `from combat.` / `patch('combat.` strings across all Python files | Status: Done.
- [x] Updated `agent_rules.md` Section 1 (`battle`, `utilities/`, `docs/`) | Status: Done.
- [x] README checked — no stale links | Status: Done.
- [x] `python3 -m pytest` — 87 passed (matches baseline) | Status: Done.

## 2026-04-20: PvP Simulator Path Fix

**Overall Idea:**
Fix `ModuleNotFoundError` when running `Main.py` directly from the project root by adding the root directory to `sys.path`.

**Steps:**
- [x] Update `pvp_simulator/Main.py` to inject project root into `sys.path`. | Status: Done.
- [x] Verify simulation execution from terminal. | Status: Done.

## 2026-04-20: Timeline Tie-Breaking Logic
**Plan:** [timeline_tie_breaking.md](docs/plans/timeline_tie_breaking.md)

**Overall Idea:**
Implement game-compliant tie-breaking in the combat timeline where higher HAB and d10 rolls determine turn order on tied ticks. Delegate logic from Controller (Simulator) to Model (BattleManager).

**Steps:**
- [x] Create `tests/battle/test_timeline_logic.py` with tie-break scenarios. | Status: Done.
- [x] Modify `BattleManager.add_character` to support 5-element tuple and roll d10. | Status: Done.
- [x] Modify `BattleManager.schedule_next_action` to roll d10. | Status: Done.
- [x] Update `BattleManager.get_next_actor` and `delay_character` for new tuple structure. | Status: Done.
- [x] Cleanup `pvp_simulator/Simulator.py`: Remove manual tie-break logic. | Status: Done.
- [x] Verify with tests and simulation. | Status: Done.
