# Plan: Add DEF_CALC History Entry

## Objective
Mirror the `ATK_CALC` history entry for the defense roll. After each defense roll, emit a `DEF_CALC` tag showing the full formula: `final = roll + rank + bdd`.

## Changes

### 1. `core/Events.py`
- Add `HistoryEmitter.def_calc(target_id, roll, rank, bdd, final) -> str`
  - Returns `DEF_CALC|{target_id}|{roll}|{rank}|{bdd}|{final}`

### 2. `battle/BattleActions.py`
- After the defense roll and `mod_def_roll` calculation, append:
  `HistoryEmitter.def_calc(target.char_id, roll_result.final_roll, target.rank, attack_load.bdd, mod_def_roll)`

### 3. `views/BattleView.py`
- Add `DEF_CALC` case to `_parse_entry`:
  `[CALC] {target} Final Defense: {final} = {roll} (Roll) + {rank} (Rank) + {bdd} (BdD)`

### 4. Tests (`tests/battle/test_HistoryCalculations.py`)
- Add `TestDefCalcHistory` class:
  - Verifies `DEF_CALC` tag is present after every attack resolution (hit or miss).
  - Verifies formula values: `final == roll + rank + bdd`.
  - Verifies ordering: appears after `ROLL|DEF` and before `HIT/MISS`.
- Add `TestBattleViewDefCalcParsing` to existing `TestBattleViewCalcParsing`:
  - Verifies `_parse_entry` correctly translates `DEF_CALC` tag.

### 5. Documentation
- Add `[ARCH.DOC.core.Events.HistoryEmitter.def_calc]`
- Update `[ARCH.DOC.battle.BattleActions.AttackAction.execute]` to mention `DEF_CALC`.
- Update `[ARCH.DOC.views.BattleView.BattleView._parse_entry]` to list `DEF_CALC`.
