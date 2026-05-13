# Implementation Plan - Standardizing Battle History Logging

The goal is to enhance combat transparency by including detailed breakdowns of attack and damage calculations in the battle history stream.

## Proposed Changes

### 1. Core: `core/Events.py`
- Add `atk_calc` static method to `HistoryEmitter`.
- Add `dmg_calc` static method to `HistoryEmitter`.

### 2. Battle: `battle/BattleActions.py`
- Modify `AttackAction.execute` to record the attack calculation after `current_mod_atk` is computed.
- Modify `AttackAction.execute` to record the damage calculation during damage resolution.

### 3. View: `views/BattleView.py`
- Update `_parse_entry` to handle `ATK_CALC` and `DMG_CALC` tags.
- Format them as `[CALC] ...` to distinguish from standard rolls and damage events.

## Verification Plan

### Automated Tests
- Create `tests/battle/test_HistoryCalculations.py`.
- Mock a basic attack and verify that the `ActionLoad.history` contains the expected `ATK_CALC` and `DMG_CALC` tags with correct values.
- Verify `BattleView` parses them correctly.

### Manual Verification
- None required if automated tests pass.
