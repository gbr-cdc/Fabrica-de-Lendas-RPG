# Implementation Plan: Targeting System Refactor

**Feature:** Support for 0-N targets in `BattleAction` and multi-target tracking in `PosturaDefensiva`.  
**Status:** [PLANNING]  
**Objective:** Refactor the action system to allow multiple targets, preparing for AOE skills and map-based targeting.

---

## 1. Architectural Changes

### 1.1 `BattleAction` Target Refactor
Currently, `BattleAction` and its subclasses receive a single `target: Character`. This will be changed to `targets: List[Character]`.

- **Impact**: All controllers and actions must be updated to handle a list of characters.
- **Backward Compatibility**: For single-target actions, the list will contain one element. For self-actions (like `Gerar Foco`), the list can be empty or contain the actor.

### 1.2 `AttackAction` Multi-Target Execution
The `execute()` method in `AttackAction` will be updated to loop over `self.targets`.
- **Logic**: For each target, it will create a dedicated `AttackLoad`, run the roll/hit/damage logic, and emit the corresponding events.
- **Aggregated History**: The `ActionLoad` returned by `execute()` will aggregate the history logs from all attack resolutions.
- **Resource Cost**: Focus cost is paid once per action, regardless of the number of targets (this is standard for AOE).

### 1.3 `PosturaDefensiva` Multi-Target Tracking
The current implementation tracks a single target. It will be refactored to use a dictionary for tracking.
- **State**: `_tracked_targets: Dict[str, bool]` (Map of `char_id` to `penalty_applied`).
- **Tracking Hook**: When the owner hits *any* target, that target is added to the tracking map.
- **Penalty Hook**: When *any* character attacks the owner, the passive checks if the attacker is in the tracking map.
- **Cleanup**: Tracking for a specific character is removed when they successfully attack the owner or when their turn ends.

---

## 2. Files to Change

| File | Change |
|---|---|
| `core/BaseClasses.py` | Change `BattleAction.__init__` signature: `target` -> `targets: List[Character]`. |
| `battle/BattleActions.py` | Update all actions to use `targets`. Refactor `AttackAction.execute()` to loop over targets. |
| `battle/BattlePassives.py` | Refactor `PosturaDefensiva` to use `_tracked_targets` map. Update `Combo` to use `targets[0]`. |
| `controllers/CharacterController.py` | Update `PvP1v1Controller` to pass `[target]` instead of `target`. |
| `tests/battle/test_postura_defensiva.py` | Update tests to support multiple targets and verify multi-tracking. |

---

## 3. Atomic Steps (Phase 1: Independent Rolls)

### Step 1: Core Interface Update
- [ ] Modify `core/BaseClasses.py`: Update `BattleAction` to accept `targets: List[Character]`.

### Step 2: Controller Update
- [ ] Modify `controllers/CharacterController.py`: Update `choose_action` to provide targets as a list.

### Step 3: Action Implementation Update
- [ ] Modify `battle/BattleActions.py`:
    - Update `AttackAction.__init__` and `execute()`.
    - **Logic**: For this phase, `execute()` will loop over targets and perform a standard attack resolution (including a new roll) for each.
    - Update `GenerateManaAction`, `GenerateFocusAction`, `TogglePosturaDefensiva`.

### Step 4: Passive Update (Postura Defensiva)
- [ ] Modify `battle/BattlePassives.py`:
    - Update `PosturaDefensiva` internal state to `_tracked_targets`.
    - Update `hit_hook`, `penalty_hook`, `cleanup_hook`, and `turn_end_hook`.
    - Update `Combo` and any other passives relying on `target`.

### Step 5: Verification
- [ ] Update and run tests in `tests/battle/test_postura_defensiva.py`.
- [ ] Create a new test case for multi-target `AttackAction` to ensure logs and damage are correctly distributed.

---

## 4. Phase 2: Unified Rolls (Future)
- **Goal**: Support "Area Attacks" (shockwaves, explosions) where the attacker rolls once for the whole zone.
- **Advantage Logic**: Advantage/Disadvantage against specific creatures should NOT apply to area attacks, as the attacker is targeting the ground/space, not a specific oponent.
- **Refactor**: Will require a flag in `AttackActionTemplate` to toggle between Independent and Unified modes.

---

## 5. Future Considerations (Map Module)
- The list of targets in `choose_action` is currently determined by the controller's logic (e.g., "closest enemy").
- Once a map module is available, the controller will use map-queries (e.g., `map.get_characters_in_range(actor, range)`) to populate the `targets` list.
- `Alcance` will specifically use this to target all adjacent enemies.
