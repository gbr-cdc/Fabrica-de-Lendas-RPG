# Implementation Plan: Postura Defensiva (Destruidor)

**Feature:** `PosturaDefensiva` — toggle-state passive from the Destruidor Combat Style  
**Status:** Awaiting User Approval

---

## 1. Mechanic Summary (from GDD)

> *"Em postura defensiva os dados de ataque e defesa passam a ser d10/d10. Nesta postura, a habilidade Alcance passa a custar 1 de Foco. Toda vez que você acertar um oponente, aquele oponente ganha uma penalidade de Precisão contra você."*

Codified rules:
- **Toggle state**: `PosturaDefensiva` is always registered as a passive, but has an active/inactive internal state.
- **Dice change (ON)**: `atk_die` d12→d10 (modifier: -2), `def_die` d8→d10 (modifier: +2).
- **Dice change (OFF)**: modifiers are removed, reverting to base stats.
- **Hit hook**: Every time the owner lands a hit while in posture → the *attacker* (the hit target) gets a **-1 `pre` EphemeralModifier** tracked to the next time they attack the owner.
- **Penalty lifetime — success path**: Tracked target attacks the owner → `-1 pre` is applied before their roll → after their `on_attack_end` fires, the modifier is removed and **tracking ends** (passive fulfilled its purpose).
- **Penalty lifetime — miss path**: Tracked target's turn ends without attacking the owner → tracking is cleared, no modifier is ever applied.
- **One tracked target at a time**: For now, only one target is tracked. Multi-target tracking (needed for `Alcance`) is **Out of Scope** — to be revisited when `Alcance` is implemented.
- **Activation**: Via a `TogglePosturaDefensiva` `BattleAction` with `FREE_ACTION` cost. Free actions are resolved immediately at the start of a turn, without consuming the turn; the controller is re-prompted until it returns a non-free action.

---

## 2. Architectural Decisions

### 2.1 `FREE_ACTION` in `BattleActionType`
Add `FREE_ACTION = "free_action"` to the enum.  
`BattleManager.run_battle()` must loop on free actions: execute → re-prompt controller → repeat until the controller returns a non-free action. The tick is only advanced after a real action.

### 2.2 Modifier Stack Pattern for `atk_die` / `def_die`
`Character.atk_die` and `Character.def_die` are currently plain integers. To honor the **Modifier Stack Pattern** rule, they must become properties backed by `base_atk_die` / `base_def_die` and resolved through `get_stat_total()`.

- Dice values in the system are integers (the die face count: 8, 10, 12).
- The posture modifier adds **-2** to `atk_die` and **+2** to `def_die`.
- The modifier has `source="PosturaDefensiva"` so it can be identified and removed by source.
- **Note**: Enforcing `source` as a standard field on all modifiers is a desirable system improvement but is **Out of Scope** for this task.

### 2.3 `IBattleContext.get_active_passive()`
`BattleManager` already stores active passive instances in `self.active_passives[char_id]`. A new method `get_active_passive(char_id, passive_name)` will be added to both `BattleManager` and the `IBattleContext` Protocol, so the `TogglePosturaDefensiva` action can reach the passive instance cleanly without coupling to `BattleManager` directly.

### 2.4 Stateful Passive Design
`PosturaDefensiva` is a `BattlePassive` with internal mutable state:
- `is_active: bool` — current posture state.
- `_dice_modifiers: list[EphemeralModifier]` — owned modifiers applied to the owner's dice when active.
- `_tracked_target: Character | None` — the last hit target being watched.
- `_penalty_applied: bool` — guard flag for the tracking lifecycle.

No reference to the precision modifier is stored. Instead, cleanup uses `tracked_target.remove_modifiers_by_source("PosturaDefensiva_Penalidade")`. This requires adding `remove_modifiers_by_source(source: str)` to `Character` (already being modified in Step 2).

### 2.5 Hit Tracking Lifecycle (Hook Design)
All hooks are permanent (registered once at `add_character`):

| Hook | Trigger condition | Action |
|---|---|---|
| `on_gda_modify` | `attacker == owner` AND `hit == True` AND posture is active | Call `_start_tracking(target)` |
| `on_roll_modify` | `attacker == tracked_target` AND `target == owner` | Apply `EphemeralModifier('pre', -1, 'PosturaDefensiva_Penalidade')` to tracked_target; set `_penalty_applied = True` |
| `on_attack_end` | `attacker == tracked_target` | If `_penalty_applied`: call `tracked_target.remove_modifiers_by_source(...)` → **clear tracking** (success path, passive fulfilled) |
| `on_turn_end` | `actor == tracked_target` | If NOT `_penalty_applied`: clear tracking (miss path, target didn't attack owner) |

`_start_tracking(new_target)`:
1. Safety: if old tracked target still has `_penalty_applied = True`, call `old_target.remove_modifiers_by_source(...)` before replacing.
2. Set `_tracked_target = new_target`, `_penalty_applied = False`.

---

## 3. Files to Change

| File | Change |
|---|---|
| `core/Enums.py` | Add `FREE_ACTION = "free_action"` to `BattleActionType` |
| `entities/Characters.py` | Refactor `atk_die`/`def_die` → `base_atk_die`/`base_def_die` + properties; add `remove_modifiers_by_source(source)` |
| `core/BaseClasses.py` | Add `get_active_passive(char_id, name)` to `IBattleContext` Protocol |
| `battle/BattleManager.py` | Add `get_active_passive()` method; update `run_battle()` free-action loop |
| `battle/BattlePassives.py` | Add `PosturaDefensiva` class + register in `registry` |
| `battle/BattleActions.py` | Add `TogglePosturaDefensiva` class + register in `registry` |

---

## 4. Atomic Steps (Active Task)

1. **`core/Enums.py`**: Add `FREE_ACTION`.
2. **`entities/Characters.py`**: Rename `self.atk_die` → `self.base_atk_die`, `self.def_die` → `self.base_def_die`; add `atk_die`/`def_die` properties; add `remove_modifiers_by_source(source: str)`.
3. **`core/BaseClasses.py`**: Add `get_active_passive()` signature to `IBattleContext`.
4. **`battle/BattleManager.py`**: Add `get_active_passive()` implementation; refactor `run_battle()` to loop free actions.
5. **`battle/BattlePassives.py`**: Implement `PosturaDefensiva` + register.
6. **`battle/BattleActions.py`**: Implement `TogglePosturaDefensiva` + register.
7. **Tests**: Write `tests/battle/test_postura_defensiva.py` covering: toggle ON/OFF dice modifiers, penalty applied on success path, tracking cleared on miss path, `_start_tracking` safety cleanup.
8. **Run `pytest`** — green = done.

---

## 5. Out of Scope

- `Alcance` skill (Foco cost change while in posture) — separate ticket.
- **Multi-target tracking**: When `Alcance` is implemented, the tracking set will need to become a `set[char_id]` instead of a single target. Deferred.
- **Global modifier `source` enforcement**: Adding `source` as a mandatory field across all existing modifiers — deferred to a separate refactor task.
- Controller AI logic for *when* to toggle the posture — `PvP1v1Controller` will not be updated as part of this task.
