# Implementation Plan - Update Battle View for Standardized History Tags

The goal is to update `views/BattleView.py` to support the new structured history tags introduced in the recent engine standardization refactor.

## Proposed Changes

### 1. Update `BattleView._parse_entry`
Add support for the following tags:
- `PASSIVE`: Display as `[PASSIVE] {owner_id} triggers {passive_name}`.
- `ACTION_HOOK`: Display as `[HOOK] {actor_id} triggers {action_name} effect`.
- `STATUS_HOOK`: Display as `[HOOK] {status_name} effect triggered on {target_id}`.
- `ATK_LOAD`: Display as `[ATK_LOAD] {attribute} modified: {current} ({delta})`.

## Verification Plan

### Automated Tests
Run existing integration tests to ensure that the view no longer outputs raw pipe-delimited tags for these events.
- `pytest tests/battle/test_BattleActions.py`
- `pytest tests/battle/test_Bloquear.py`
- `pytest tests/battle/test_ForcaBruta.py`
- `pytest tests/battle/test_GracaDoDuelista.py`
- `pytest tests/battle/test_MestreArmas.py`
- `pytest tests/battle/test_PosturaDefensiva.py`

### Manual Verification
I will verify the output of `BattleView.parse()` with a sample of the new tags to ensure correct formatting.
