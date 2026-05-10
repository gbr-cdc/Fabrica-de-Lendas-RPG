# Implementation Plan: Interface Segregation & Context Decoupling

## Overview
This plan addresses the "God Interface" anti-pattern in the battle engine. By breaking down `IBattleContext`, removing context leaks from event payloads, and decoupling basic attacks from data templates, we achieve strict Interface Segregation (ISP) without changing the dynamic instantiation flow.

## Phase 1: Core Interface Segregation (`core/BaseClasses.py`)
1. **Define Segregated Protocols:**
   Break `IBattleContext` into smaller, responsibility-focused protocols:
   *   `IEventContext(Protocol)`: `emit`
   *   `IEffectContext(Protocol)`: `add_status_effect`, `remove_status_effect`, `get_active_passive`
   *   `ITimelineContext(Protocol)`: `delay_character`, `set_tick`
   *   `IRegistryContext(Protocol)`: `get_characters`, `get_graveyard`, `get_controller`
   *   `IDataContext(Protocol)`: `get_template`

2. **Define Role-Based Contexts:**
   Group the smaller protocols into strictly typed contexts for specific base classes:
   *   `IPassiveContext(IEventContext, IEffectContext, ITimelineContext, Protocol)`
   *   `IActionContext(IEventContext, Protocol)`
   *   `IControllerContext(IRegistryContext, ITimelineContext, Protocol)`

3. **Update Base Class Signatures:**
   Update the type hints in base classes to use these new restricted contexts:
   *   `BattlePassive.__init__(..., context: IPassiveContext)`
   *   `StatusEffect.__init__(..., context: IPassiveContext)`
   *   `BattleAction.__init__(..., context: IActionContext)`

## Phase 2: Plug the "God Context Leak"
1. **Update `core/Events.py`:**
   *   Remove `battle_context: 'IBattleContext'` from the `AttackLoad` dataclass. Both `ActionLoad` and `AttackLoad` must be pure DTOs.
2. **Update `battle/BattleActions.py`:**
   *   Remove the `battle_context=self.context` argument wherever `ActionLoad` or `AttackLoad` is instantiated.
3. **Update `battle/BattlePassives.py`:**
   *   Fix `Combo` (line 199): Change `attack_load.battle_context.add_status_effect` to `self.context.add_status_effect`.

## Phase 3: Decouple `AttackAction` from `IDataContext`
1. **Update `data/AttackActions.json`:**
   *   Remove the `"BasicAttack"` entry completely.
2. **Update `battle/BattleActions.py`:**
   *   Refactor `AttackAction` constructor to make the `template` argument optional (or allow it to handle `None`).
   *   If no template is provided, `AttackAction` should generate a default "Basic Attack" configuration internally (Focus Cost 0, standard action, basic attack type, no effects).
3. **Update `battle/BattlePassives.py` (Combo):**
   *   Remove `self.context.get_template("BasicAttack")`.
   *   Instantiate `AttackAction` directly without passing a template. This ensures `Combo` doesn't need `IDataContext` to function.

## Phase 4: Documentation Updates
1. **Update Architecture Documentation via `ref_manager`:**
   *   Update `[ARCH.DOC.core.BaseClasses.IBattleContext]` to reflect the removal of the monolithic interface and the addition of the new segregated interfaces (`IEventContext`, `IPassiveContext`, etc.).
   *   Update their `[DEPENDS: ...]` tags. Since the interfaces are now small, their dependencies will be minimal (e.g., `IEventContext` only depends on `ActionLoad`).

---
**Execution Note for AI:** When executing this plan, rely heavily on structural subtyping (`Protocol`). The actual runtime instantiation in `BattleManager` (`registry[passive](character, self)`) does **not** need to change, as `BattleManager` naturally implements all the required protocols.
