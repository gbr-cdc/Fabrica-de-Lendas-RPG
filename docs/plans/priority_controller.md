# Implementation Plan - Data-Driven Priority Controller

The objective is to implement a `CharacterController` that uses a priority-based system of decision nodes, configurable via JSON. This allows for complex AI behavior without hardcoding logic for every enemy type.

## Proposed Changes

### 1. `core/Structs.py`
Add `DecisionNode` and `AIBehavior` data structures.

```python
@dataclass(frozen=True)
class DecisionNode:
    priority: int
    required_state: str
    target_selector: str
    filters: List[str]
    action_id: str | None
    next_state: str | None
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class AIBehavior:
    id: str
    initial_state: str
    nodes: List[DecisionNode]
```

### 2. `core/DataManager.py`
Add methods to load and retrieve AI behaviors.

- `_ai_behaviors: Dict[str, AIBehavior]`
- `load_ai_behaviors(filepath: str)`
- `get_ai_behavior(behavior_id: str) -> AIBehavior`

### 3. `controllers/CharacterController.py`
Implement `AIPriorityController`.

#### Key Features:
- **Behavior State**: The controller maintains a `current_state` (string), initialized from `AIBehavior.initial_state`.
- **Decision Loop**:
    1.  Start a loop (with a safety break) to process decisions.
    2.  Find all nodes where `required_state` matches `current_state` (or "any").
    3.  Sort nodes by `priority` (descending).
    4.  For each node:
        -   **Targeting Resolution**:
            a. Select base group (`self`, `any_ally`, `all_ally`, `any_enemy`, `all_enemy`, `anyone`, `everyone`).
            b. Apply filters sequentially (`hp_lt_50`, `lowest_hp`, `highest_atk`, etc.).
            c. If the resulting list is empty, the node fails; move to next node.
        -   **Action/State Transition**:
            a. If `action_id` is present, instantiate the `BattleAction`.
            b. If `next_state` is present, update `current_state`.
            c. If `next_state` was updated AND `action_id` was `None` (or a special "ChangeState" meta-action), **restart the loop** from step 1.
            d. If an action was instantiated and `can_execute()` is True, return it.
    5.  If no node is successful, return a fallback `WaitAction`.

#### Targeting System:
- **Base Groups**:
    - `self`: `[actor]`
    - `any_ally`: First ally meeting filters.
    - `all_ally`: All allies meeting filters.
    - `any_enemy`: First enemy meeting filters.
    - `all_enemy`: All enemies meeting filters.
    - `anyone`: Any character meeting filters.
    - `everyone`: All characters meeting filters.
- **Filter Registry**:
    - `hp_lt_X`: Filters characters with HP percentage below X.
    - `lowest_hp`: Reduces the group to the single character with the lowest absolute HP.
    - `is_dead`: Filters dead characters (mostly for rez skills).

#### Fallback State Change (Answering User Question):
To change state when no target is found for a specific condition:
Implement a **lower priority node** within the same state that acts as a "catch-all".
*Example:*
- **Node A (Priority 10, State: Neutral)**: Target `any_ally` with `hp_lt_50`. Action: `None`, Next State: `Healing`.
- **Node B (Priority 5, State: Neutral)**: Target `self`. Action: `Attack`, Next State: `Aggressive`.

If Node A fails (no ally has < 50% HP), the controller moves to Node B. If Node B is intended to be the "failure state" of the healing check, it can transition the state to something else.

### 4. Data Configuration
Create `data/ai_behaviors.json` with initial behaviors.

## Verification Plan

### Automated Tests
1.  **Unit Tests for `AIPriorityController`**:
    -   Test that it respects priority.
    -   Test that it switches behavior when HP is low.
    -   Test that it handles "no targets found" gracefully.
2.  **Integration Tests**:
    -   Battle simulation with an AI-controlled character using a specific behavior JSON.

### Manual Verification
-   Run a sample battle and observe the logs to ensure the AI is choosing actions according to the JSON definition.
