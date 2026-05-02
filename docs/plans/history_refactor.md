# Implementation Plan: Data-Driven History Stream [PLAN.HISTORY_REFACTOR]

## 1. Goal
Transition the `history` field in `ActionLoad` and `AttackLoad` from unstructured narrative strings to a structured "Event Stream" protocol. This allows different Views (CLI, UI, Logs) to interpret and localize game events independently of the engine logic.

## 2. Technical Design

### 2.1 Event Format
We will use a pipe-delimited string format for simplicity and performance:
`TAG|PARAM1|PARAM2|...`

### 2.2 Core Event Dictionary
| Tag | Parameters | Description |
| :--- | :--- | :--- |
| `EXEC` | `action_id`, `actor_id` | Execution started. |
| `ROLL` | `type`, `value`, `die_size`, `actor_id` | A dice roll occurred. |
| `MOD` | `source_id`, `value`, `target_entity_id` | A value was modified by a passive/hook. |
| `HIT` | `target_id` | Attack hit target. |
| `MISS` | `target_id` | Attack missed target. |
| `DMG` | `target_id`, `amount`, `type` | Damage calculated. |
| `HP` | `entity_id`, `delta`, `current` | State change of health. |
| `FOCUS` | `entity_id`, `delta`, `current` | Focus generated or spent. |
| `MANA_F` | `entity_id`, `delta`, `current` | Floating Mana generated or spent. |
| `MANA_T` | `entity_id`, `delta`, `current` | Total/Daily Mana consumed during manifestation. |
| `MSG` | `message` | Legacy/Narrative fallback for untagged events. |

### 2.3 Implementation Strategy

#### Phase 1: Infrastructure
- Create `HistoryEmitter` utility in `core/Events.py` to standardize event string creation.
- Add `add_event(tag, *params)` helper to `ActionLoad`.

#### Phase 2: Engine Refactor
- Update `AttackAction.execute` to emit structured tags for:
    - Action Start (`EXEC`)
    - Attack/Defense Rolls (`ROLL`)
    - Hit/Miss check (`HIT`/`MISS`)
    - Damage application (`DMG`, `HP`)
- Update `GenerateFocusAction` and `GenerateManaAction` to emit `FOCUS`, `MANA_F`, and `MANA_T` tags.

#### Phase 3: Passives and Hooks Refactor
- Update `BattlePassives.py` (e.g., `Graça do Duelista`, `Força Bruta`) to use `MOD` instead of literal strings.
- Update `StatusEffects.py` to emit tags when applied/removed.

## 3. Proposed Changes

### core/Events.py
```python
class HistoryEmitter:
    @staticmethod
    def exec(action_id: str, actor_id: str) -> str:
        return f"EXEC|{action_id}|{actor_id}"
    # ... other tags
```

### battle/BattleActions.py
Replace:
`action_load.history.append(f"{self.actor.name} usou {self.name}!")`
With:
`action_load.history.append(HistoryEmitter.exec(self.name, self.actor.char_id))`

## 4. Verification Plan
- **Unit Tests:** Refactor existing tests in `test_BattleActions` to assert on the structured tags instead of narrative strings.
- **Integration:** Run a full battle simulation and verify the `BattleResult.history` contains only structured codes.

## 5. Architectural Alignment
- **[ARCH.RULES.CORE.MVC]:** Moves presentation logic out of the model.
- **[ARCH.RULES.CORE.DATA]:** Enhances automated verification of game mechanics.
