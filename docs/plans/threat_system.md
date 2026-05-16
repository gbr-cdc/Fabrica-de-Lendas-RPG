# Threat System Implementation Plan

## Problem Statement
The user wants to implement Threat logic (engagement) in combat. The system needs to track who is threatening whom, restrict targeting for threatened characters, and enforce Disengage Tests when a character attempts to attack an unengaged target. The user correctly identified that putting this logic directly into `BattleManager` would bloat it.

## Architectural Analysis & Solution
Instead of placing the threat tracking and disengage logic inside `BattleManager`, we will create a dedicated **`ThreatManager`** component. This adheres to the single responsibility principle and keeps `BattleManager` focused on orchestration, timeline management, and event dispatching.

### 1. `ThreatManager` Component
Create a new file `battle/ThreatManager.py` defining the `ThreatManager` class.
- **State:** Keep track of who threatens whom. This can be stored as a dictionary mapping a character ID to a set of character IDs they are currently threatening, and vice-versa.
- **Event Listening:** `ThreatManager` will subscribe to `BattleManager`'s event bus (e.g., `on_attack_end` or `on_hit_check`). When a character performs a melee attack against a target, the `ThreatManager` updates its state to establish threat [GDD.COMBAT.THREAT.ESTABLISH].

### 2. Validating Actions & Disengaging
- **Pre-execution Hook/Check:** `ThreatManager` will expose a method (e.g., `validate_action(action)` or `process_intent(action)`) that `BattleManager` calls before fully committing to `run_action`. 
- **Targeting Restrictions [GDD.COMBAT.THREAT.RESTRICTION]:** If the action's target is already threatening the actor, or if the actor was already threatening the target, the action proceeds normally.
- **Disengage Test [GDD.COMBAT.THREAT.DISENGAGE]:** If the actor is threatened by enemies but tries to attack someone else, `ThreatManager` will initiate the Disengage Test (1d10 + Attribute vs 1d10 + Attribute of all threatening enemies, including Ally Assistance logic [GDD.COMBAT.THREAT.ASSIST]).
- **Failure Handling [GDD.COMBAT.THREAT.FAILURE]:** If the test fails, `ThreatManager` will inform `BattleManager`. The original action is aborted, and the character is instead charged half a standard action's cost (Movement Action cost).

### 3. Integration with `BattleManager`
- `BattleManager` will instantiate `ThreatManager` during its `__init__`.
- `ThreatManager` will register its hooks via the Event Bus.
- `BattleManager`'s `run_action` (or the controller loop) will be updated to consult `ThreatManager` when a character attempts a targeted action.
- When characters die or are removed (`resolve_deaths` / `remove_character`), `ThreatManager` will clean up their threat presence.

## Proposed Steps
1. **Implement `ThreatManager`**: Track relationships, write the Disengage Test logic, and handle Ally Assistance.
2. **Update `BattleManager`**: Inject/instantiate `ThreatManager`, add the pre-action validation step in `run_action` or the decision loop.
3. **Event Hooks**: Add `ThreatManager`'s hooks to establish and remove threat automatically on attacks and character deaths.
4. **Unit Tests**: Add tests verifying targeting restrictions, disengage success/failure, and action cost changes.
