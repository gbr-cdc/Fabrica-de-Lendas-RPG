# Implementation Plan - Timeline Tie-Breaking

## Problem Description
The `BattleManager` currently manages the combat timeline using a simple `(tick, char_id, character)` tuple in a min-heap. This leads to arbitrary turn order when two characters have the same tick (alphabetical by `char_id`).

Game rules specify:
1. Characters with higher **HAB** (Habilidade) act first on tied ticks.
2. If **HAB** is tied, each character rolls a **d10**; the higher roll acts first.
3. **Continuous Draw Resolution**: If the rolls are also tied, they must re-roll until a winner is determined.

## Proposed Changes

### 1. BattleManager.py
Update the timeline management to ensure unique priority for every entry.

*   **New State**: `self.timeline_slots = set()` to track `(tick, hab, roll)` combinations currently in the heap.
*   **Unique Roll Logic**: Implement a helper to roll d10 until a unique `(tick, hab, roll)` is found.
*   **Update Tuple Structure**: `(tick, neg_hab, neg_roll, char_id, character)`.
    *   Even though `char_id` is present for identification, it will **never** be used for sorting because `(tick, neg_hab, neg_roll)` will be guaranteed unique.
*   **`add_character` & `schedule_next_action`**:
    *   Use the unique roll logic.
    *   Add the tuple to `self.timeline_slots`.
*   **`get_next_actor`**:
    *   Unpack the 5-element tuple.
    *   Remove the corresponding `(tick, hab, roll)` from `self.timeline_slots`.
*   **`delay_character`**:
    *   Remove the old slot from `self.timeline_slots`.
    *   Calculate the new tick and get a new unique roll.
    *   Add the new slot to `self.timeline_slots` and update the heap.

### 2. Simulator.py (Cleanup)
Remove the manual tie-break logic in `_setup_battle`. The simulator should simply add characters at their base `action_cost_base` (or 0) and let the `BattleManager` handle the collisions.

## Rationale
*   **MVC Adherence**: Combat logic belongs in the `BattleManager` (Model), not the `Simulator` (Controller).
*   **Robustness**: Using `char_id` as the final tie-breaker prevents comparison errors between `Character` objects while ensuring a deterministic (though secondary) order.
*   **TDD**: A new test case in `tests/combat/test_timeline_logic.py` will be created to verify that on tied ticks, HAB and Rolls are respected.

## Verification Plan
1.  **Unit Test**: Create `tests/combat/test_timeline_logic.py`.
    *   Case A: Two characters, same tick, different HAB.
    *   Case B: Two characters, same tick, same HAB, different d10 rolls (mocked).
2.  **Simulation Check**: Run a mono-battle simulation and verify the history/order for initial turns.
