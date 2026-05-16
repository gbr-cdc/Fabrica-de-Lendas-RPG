# Implementation Plan - Nerf Combo Passive

The `Combo` passive currently allows up to three attacks and a stun. This plan outlines the steps to nerf it by limiting it to a maximum of two attacks, removing the stun, and adding a configurable attack roll threshold for the second attack.

## Proposed Changes

### 1. Configuration Update
- **File:** `data/BattlePassives.json`
- **Change:** Add `min_roll_for_second` (default: 5) to the `Combo` parameters.

### 2. Logic Refactoring
- **File:** `battle/BattlePassives.py`
- **Class:** `Combo`
- **Changes:**
    - Simplify `on_attack_end` hook.
    - Remove `stage` and `hit` tracking (no longer needed for multi-hit chains).
    - Check if `attack_load.hit` and `attack_load.attack_roll >= min_roll_for_second`.
    - Trigger a single `AttackAction` without `EXTRA_ATTACK` (allowing focus generation).
    - Ensure it doesn't trigger recursively.

### 3. Documentation Sync
- **Files:** `.forbidden/GDD.md`, `.forbidden/architecture.md`
- **Change:** Update descriptions of the `Combo` passive to reflect the new mechanics.

### 4. Test Updates
- **File:** `tests/battle/test_Combo.py`
- **Changes:**
    - Update tests to verify the two-attack limit.
    - Verify the roll threshold requirement.
    - Verify focus generation for the second attack.
    - Ensure no stun is applied.

## Detailed Logic for `Combo.on_attack_end`

```python
def checar_ataque_bonus(attack_load: AttackLoad):
    if attack_load.target is None or attack_load.character.char_id != self.owner.char_id:
        return
    
    if self._executing_combo:
        return

    params = self.template.parameters if self.template else {}
    min_roll = params.get("min_roll_for_second", 5)

    if attack_load.hit and attack_load.attack_roll >= min_roll:
        self._executing_combo = True
        try:
            # Use default AttackAction (BASIC_ATTACK) to allow focus generation
            response = AttackAction(None, attack_load.character, [attack_load.target], self.context).execute_if_possible()
            if response.success:
                attack_load.history.append(HistoryEmitter.passive(self.name, self.owner.char_id))
                attack_load.add_event("COMBO", self.owner.char_id, 1)
                attack_load.history.extend(response.history)
        finally:
            self._executing_combo = False
```

## Verification Plan
1. Run `pytest tests/battle/test_Combo.py` to see initial failures (after logic change).
2. Fix tests and re-run.
3. Verify that the second attack generates focus (inspect history).
4. Verify that a third attack is never triggered.
