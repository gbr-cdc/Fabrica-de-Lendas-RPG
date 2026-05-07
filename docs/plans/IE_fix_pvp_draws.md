# IE Task: Fix PvP Simulator Drawing Every Battle (v3 - Team-based Judge)

## Problem
All battles in the multi-battle simulation end in a draw because `BattleResult.winners` and `BattleResult.losers` are never populated. The `BattleJudge` will be responsible for populating these lists based on team outcomes.

## Proposed Changes

### `core/BaseClasses.py`
- Add `IBattleJudge` Protocol:
  ```python
  class IBattleJudge(Protocol):
      def rule(self, context: 'IBattleContext', result: 'BattleResult') -> 'BattleState': ...
  ```
- Update `IBattleContext` to include `get_graveyard()` method:
  ```python
  def get_graveyard(self) -> List[Character]: ...
  ```

### `battle/Judges.py`
- Update `BattleJudge.rule` signature to accept `result: 'BattleResult'`.
- Implement logic to populate `result.winners` and `result.losers`:
    1. Determine battle state (RUNNING, VICTORY, DEFEAT, DRAW) as before.
    2. If state is terminal (not RUNNING):
        - Clear `result.winners` and `result.losers` (to ensure idempotency if called multiple times).
        - Collect all participants by merging `context.get_characters()` and `context.get_graveyard()`.
        - If `VICTORY`: All Team 1 characters -> `winners`, all Team 2 -> `losers`.
        - If `DEFEAT`: All Team 2 characters -> `winners`, all Team 1 -> `losers`.
        - If `DRAW`: All characters -> `losers` (or keep both lists empty, depending on definition of draw).
    3. Return the state.

### `battle/BattleManager.py`
- Implement `get_graveyard()`:
  ```python
  def get_graveyard(self) -> List[Character]:
      return list(self.graveyard.values())
  ```
- Update calls to `self.judge.rule(self)` to `self.judge.rule(self, self.battle_result)`.

### `tests/`
- Update `tests/battle/test_Judges.py` to verify that `winners` and `losers` are populated correctly for each state, including characters from the graveyard.
- Update `tests/pvp_simulator/test_Simulator.py` if needed.

## Verification Plan

### Automated Tests
- `pytest tests/battle/test_Judges.py`
- `pytest tests/pvp_simulator/test_Simulator.py`

### Manual Verification
- Run `python3 pvp_simulator/Main.py mono "Destruidor" "Duelista"`
- Run `python3 pvp_simulator/Main.py multi "Destruidor" "Duelista"`
