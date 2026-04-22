# Plan: Area Attacks Support

## Architectural Guardrails
- **Roll Differentiator**: Use `AttackType.AREA` in the `AttackLoad` to distinguish area-effect rolls from targeted ones.
- **Safety**: Passives must never assume `target` is present if `attack_type` is `AREA` during the Master Roll phase of an execution.
- **Resolution**: Reactions (`on_defensive_reaction`) and individual resolution hooks (`on_hit_check`, `on_damage_taken`) remain per-target and will always have a valid `target` reference.

## Implementation Steps

### PART 1: Infrastructure & Safety
1. **`core/Enums.py`**: Add `AREA = "area"` to `AttackType` enum.
2. **`core/Events.py`**: Modify `AttackLoad` dataclass to allow `target: Character | None = None`. This is crucial for the "Master Roll" phase where a single roll is made before applying it to multiple targets.
3. **`battle/BattlePassives.py`**: Audit all `on_roll_modify` hooks. Wrap any logic that accesses `attack_load.target` in an `if attack_load.target is not None:` check. This prevents `AttributeError` when the Master Roll (which has no specific target yet) is processed by passives.
4. **Verification**: Add a unit test in `tests/core/test_Events.py` ensuring `AttackLoad` can be instantiated with `target=None`.

### PART 2: Logic Implementation
1. **`battle/BattleActions.py`**:
    - Refactor `AttackAction.execute` to handle the "Master Roll" dual-path logic:
        - **If `self.attack_type == AttackType.AREA`**:
            - Perform one shared attack roll (emit `on_roll_modify` with `target=None`, then call `dice_service.roll_dice`).
            - Store this "Master Roll" result.
            - Iterate through `self.targets`:
                - For each target, resolve hits/damage using the shared Master Roll but individual target defense rolls.
        - **Else (Standard)**:
            - Maintain existing iterative logic (individual attack and defense rolls per target).
3. **`tests/battle/test_area_attacks.py`**: 
    - Test that an area attack only calls `roll_dice` for the attacker once, regardless of the number of targets.
    - Test that defense rolls and damage are still calculated individually for each target.
    - Test that passives like *Postura Defensiva* (which modify attack rolls) do not crash during the Master Roll.

## Verification Plan
1. **Infrastructure**: Run `pytest tests/core/test_Events.py` to confirm `AttackLoad` flexibility.
2. **Safety**: Run all existing battle tests to ensure no regressions in passives.
3. **Feature**: Run `pytest tests/battle/test_area_attacks.py` to validate single-roll distribution.
