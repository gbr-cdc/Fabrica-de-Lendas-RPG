# Project Documentation & Architectural Guardrails

This document serves as the primary technical reference for the **Fábrica de Lendas** RPG Engine. It combines high-level architectural rules with detailed module documentation to guide both human developers and AI agents.

---

## 1. Project Vision
**Fábrica de Lendas** is a data-driven, modular RPG engine designed for tactical combat simulation. It follows a strict **Game-MVC** pattern, where rules and logic are decoupled from presentation. The engine uses an **Event-Driven** architecture to handle complex interactions (Passives, Effects) through an Event Bus.

---

## 2. Architectural Guardrails [ARCH.GLOBAL]

These rules are context-exclusive and MUST be referenced in `MISSION_LOG.md` when relevant to the task.

### 2.1 Core Patterns
*   **Game-MVC [ARCH.1.1]**: Strict separation. 
    *   **Models**: Rules, State, and Logic in `core/`, `battle/`, `entities/`, `data/`.
    *   **Controllers**: "Brains" (Decision Flow) in `controllers/`.
    *   **Views**: Presentation layer (Logs/UI) is decoupled from the engine.
*   **Command Pattern [ARCH.1.2]**: All actions (Skills, Basic Attacks, Movements) MUST inherit from `GameAction`/`BattleAction` and implement `can_execute()` and `execute()`.
*   **Observer/EventBus [ARCH.1.3]**: Decouple reactive logic (Effects/Passives) via an EventBus. Orchestrators (e.g., `BattleManager`) manage subscriptions.
*   **IoC (Inversion of Control) [ARCH.1.4]**: Implementations (Passives/Actions) using hooks MUST expose them via `get_hooks()`. Only the Orchestrator (BattleManager) handles event registration.
*   **Data-Driven [ARCH.1.5]**: GameAction templates, CombatStyles, and GameRules MUST be defined in JSON files (`data/`). Use `DataManager` for loading.
*   **Lifecycle Safety [ARCH.1.6]**: Ephemeral hooks (valid for 1 action cycle) MUST be wrapped in `try...finally` within the Orchestrator to guarantee unsubscription.
*   **CQRS [ARCH.1.7]**: Use Methods for direct state changes (e.g., `take_damage`); use Events for notification/modification ONLY.
*   **Modifier Stack Pattern [ARCH.1.8]**: Stats are immutable. All dynamic changes (buffs/debuffs) MUST be implemented as `StatModifier` objects in the character's `modifiers` list.
*   **Anemic Entities [ARCH.1.9]**: Classes in `entities/` are data containers. All complex logic resides in Systems (e.g., `CharacterSystem`) or Actions.
*   **Protocols & Typing [ARCH.1.10]**: Use `typing.Protocol` for Dependency Injection. Use `from __future__ import annotations`. Keep typing imports in `TYPE_CHECKING` blocks to avoid circular dependencies.

### 2.2 Engine Mechanics
*   **Timeline Execution [ARCH.2.1]**: The turn order is managed by a Min-Heap timeline. Characters are re-scheduled based on `action_cost` after every non-free action.
*   **Event Payload Modification [ARCH.2.2]**: Listeners in the EventBus receive payload objects (e.g., `AttackLoad`) passed by reference. They MUST modify the object directly to influence calculations.
*   **Tick-Based Simulation [ARCH.2.3]**: The engine does not use rounds. It uses "Ticks" (discrete units of time). Logic relying on "duration" should count turns or specific events, not wall-clock time.
*   **Error Handling (Decision Loop) [ARCH.2.4]**: Controllers MUST NOT enter an infinite loop when an action fails `can_execute()`. The Orchestrator MUST implement a safety break (Max Attempts).
*   **Targeting Cardinality [ARCH.2.5]**: All `BattleAction` subclasses MUST support a `targets: List[Character]` interface. Single-target actions should use a list with one element.
*   **Area Attack Resolution (Master Roll) [ARCH.2.6]**: For `AttackType.AREA`, the attacker’s roll MUST be performed once (Master Roll) with `target=None` in the `AttackLoad`. This ensures only target-agnostic passives influence the shared roll, followed by individual resolution phases for each target.
*   **Defensive Payload Auditing [ARCH.2.7]**: Any hook that accesses `AttackLoad.target` MUST perform a null-check if the event it listens to could potentially be emitted during a Master Roll phase or a targetless context.

---

## 3. Project Structure [STRUCT.MAP]

```text
.
├── core/                # Fundamental logic, Base Classes, and Systems
├── battle/              # Combat resolution, Passives, and Battle Orchestration
├── entities/            # Data containers (Character, Items)
├── controllers/         # Decision making (AI/Player input)
├── data/                # JSON definitions (Rules, Styles, Actions)
├── utilities/           # Helper scripts and standalone tools
├── tests/               # Pytest suite (Red/Green TDD)
└── pvp_simulator/       # Main entry point for simulation
```

---

## 4. Module: Core [MODULE.core]
The `core` module contains the fundamental building blocks of the engine.

### Enums [FILE:core/Enums.py]
Centralized enumerations to ensure type safety and consistency.
- `RollState`: `ADVANTAGE`, `DISADVANTAGE`, `NEUTRAL`.
- `AttributeType`: `FIS`, `HAB`, `MEN`.
- `AttackType`: `BASIC_ATTACK`, `SKILL`, `AREA`, `EXTRA_ATTACK`.
- `BattleActionType`: `MOVE_ACTION`, `STANDARD_ACTION`, `FREE_ACTION`.

### Structs [FILE:core/Structs.py]
Data containers for passing structured information.
- `GameRules`: Progression tables (HP/MP/Cost) and resource limits.
- `RollResult`: Detailed dice roll info (final value, individual dice, state).
- `CombatStyle`: Blueprint for a character's fighting style (dice used, main stat).
- `AttackActionTemplate`: Data-driven blueprint for actions loaded from JSON.

### Events [FILE:core/Events.py]
Payload objects for the Event Bus and results transmission.
- `ActionLoad [CLASS:ActionLoad]`: Base payload containing character and history.
- `AttackLoad [CLASS:AttackLoad]`: Specialized payload for attack resolution. Carries `target`, `gda`, `damage`, and roll states.

### Base Classes [FILE:core/BaseClasses.py]
The foundational interfaces of the engine.
- `GameAction [CLASS:GameAction]`: Abstract base for the Command Pattern. `[ARCH.1.2]`
- `BattleAction [CLASS:BattleAction]`: specialized `GameAction` for combat. Manages `targets` and `IBattleContext`. `[ARCH.2.5]`
- `BattlePassive [CLASS:BattlePassive]`: Base for reactive logic. Hooks are exposed via `get_hooks()`. `[ARCH.1.4]`
- `IBattleContext [CLASS:IBattleContext]`: Protocol defining the interface for battle interaction (emit events, subscribe, delay characters). `[ARCH.1.10]`

### Character System [FILE:core/CharacterSystem.py]
Stateless logic for manipulating `Character` entities. `[ARCH.1.9]`
- `take_damage()`: Direct HP modification. `[ARCH.1.7]`
- `generate_focus() / generate_mana()`: Resource replenishment logic.
- `equip_weapon() / equip_armor()`: Equipment application and base stat calculation.

### Dice Manager [FILE:core/DiceManager.py]
Random number generation and deterministic roll scheduling.
- `roll_dice()`: Core rolling logic with support for Advantage/Disadvantage.
- `schedule_result()`: Used in tests to force specific outcomes.

### Data Manager [FILE:core/DataManager.py]
Central registry for loading and accessing data-driven templates. `[ARCH.1.5]`
- `load_combat_styles()`, `load_game_rules()`, `load_characters()`.
- `get_action_template()`: Accesses `AttackActionTemplate` by ID.

### Modifiers [FILE:core/Modifiers.py]
Implementation of the Modifier Stack Pattern. `[ARCH.1.8]`
- `StatModifier [CLASS:StatModifier]`: Base for all stat changes.
- `EphemeralModifier`: Changes cleared after combat.
- `PersistentModifier`: Permanent changes (Equipment, Traits).
