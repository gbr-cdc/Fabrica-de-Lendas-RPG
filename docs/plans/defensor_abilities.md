# Plan: Defensor Abilities Implementation [PLAN.DEFENSOR_ABILITIES]

This plan outlines the implementation of "Bloquear" and "Golpe de Escudo" for the Defensor combat style, including structural improvements to `AttackAction`.

## 1. Decouple AttackAction Effect Hooks [PLAN.DECOUPLE_HOOKS]
- **Problem:** `AttackAction.get_hooks` currently uses hardcoded `if/elif` blocks for effects.
- **Solution:** Implement a registry of effect hook builders.
- **Implementation:**
    - Define a registry (dictionary) in `BattleActions.py`.
    - Map effect IDs to functions that return hook dictionaries.
    - Update `AttackAction.get_hooks` to iterate through template effects and use the registry.

## 2. Implement "Golpe de Escudo" [PLAN.GOLPE_ESCUDO]
- **Type:** `AttackAction`.
- **Mechanics:**
    - **Focus Cost:** 2 (via template).
    - **Attack Die:** Use `def_die` instead of `atk_die`.
    - **Damage Calculation:** GdA treated as 0.
    - **Effect:** If GdA > 3, apply `Atordoado`.
- **Implementation Details:**
    - Create new effect handlers in the registry:
        - `swap_atk_def_die`: Adds an `EphemeralModifier` to `atk_die` in `on_roll_modify` and removes it in `on_attack_end`.
        - `set_gda_zero_on_dmg`: Listens to `on_damage_calculation` and sets `attack_load.gda = 0`.
        - `apply_status_on_hit_threshold`: Listens to `on_hit_check` and applies status if `gda > threshold`.
    - Ensure `AttackAction` template is updated or used correctly.

## 3. Implement "Bloquear" [PLAN.BLOQUEAR]
- **Type:** `BattlePassive`.
- **Mechanics:**
    - **Reaction:** When targeted by an attack, can spend 2 Focus.
    - **Bonus:** Add 1d4 to defense (subtract from `attack_load.gda`).
    - **Counter-Bonus:** If `defense > attacker's roll` (GdA < 0) and `GdA < -3`, gain +1 Attack (BDA) against that opponent.
- **Implementation Details:**
    - Create `Bloquear` class in `BattlePassives.py`.
    - `on_defensive_reaction` hook:
        - Check owner target, focus, and controller choice.
        - Roll 1d4 and modify `gda`.
        - If `gda < -3`, store a bonus for the owner against the attacker.
    - `on_roll_modify` hook:
        - If attacking a tracked opponent, apply +1 BDA.
        - Clear the tracking after the roll or attack end.

## 4. Verification Plan [PLAN.VERIFICATION]
- **Unit Tests:**
    - Test `Bloquear` triggering and focus consumption.
    - Test `Bloquear` gda modification and counter-bonus application.
    - Test `Golpe de Escudo` using `def_die`.
    - Test `Golpe de Escudo` gda modification and `Atordoado` application.
- **Integration Tests:**
    - Run a simulated battle with a Defensor character.

## 5. Architectural Alignment
- Follows `[ARCH.RULES.CORE.IOC]` and `[ARCH.RULES.CORE.OBSERVER]`.
- Uses `[ARCH.RULES.BATTLE.EPHEMERAL_HOOKS]` for action-specific effects.
- Uses `HistoryEmitter` via `add_event` for all changes.
