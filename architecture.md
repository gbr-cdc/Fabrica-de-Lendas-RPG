# Architectural Guardrails (Technical Reference)

These rules are context-exclusive and should be referenced in `MISSION_LOG.md` when relevant to the task. They MUST be read during the `[PLANNING]` context.

## ARCH.1: Core Patterns

*   **1.1 Game-MVC**: Strict separation. 
    *   **Models**: Rules, State, and Logic in `core/`, `battle/`, `entities/`, `data/`.
    *   **Controllers**: "Brains" (Decision Flow) in `controllers/`.
    *   **Views**: Presentation layer (Logs/UI) is decoupled from the engine.
*   **1.2 Command Pattern**: All actions (Skills, Basic Attacks, Movements) MUST inherit from `GameAction`/`BattleAction` and implement `can_execute()` and `execute()`.
*   **1.3 Observer/EventBus**: Decouple reactive logic (Effects/Passives) via an EventBus. Orchestrators (e.g., `BattleManager`) manage subscriptions.
*   **1.4 IoC (Inversion of Control)**: Implementations (Passives/Actions) using hooks MUST expose them via `get_hooks()`. Only the Orchestrator (BattleManager) handles event registration.
*   **1.5 Data-Driven**: GameAction templates, CombatStyles, and GameRules MUST be defined in JSON files (`data/`). Use `DataManager` for loading.
*   **1.6 Lifecycle Safety**: Ephemeral hooks (valid for 1 action cycle) MUST be wrapped in `try...finally` within the Orchestrator to guarantee unsubscription.
*   **1.7 CQRS**: Use Methods for direct state changes (e.g., `take_damage`); use Events for notification/modification ONLY.
*   **1.8 Modifier Stack Pattern**: Stats are immutable. All dynamic changes (buffs/debuffs) MUST be implemented as `StatModifier` objects in the character's `modifiers` list.
*   **1.9 Anemic Entities**: Classes in `entities/` are data containers. All complex logic resides in Systems (e.g., `CharacterSystem`) or Actions.
*   **1.10 Protocols & Typing**: Use `typing.Protocol` for Dependency Injection. Use `from __future__ import annotations`. Keep typing imports in `TYPE_CHECKING` blocks to avoid circular dependencies.

## ARCH.2: Engine Mechanics

*   **2.1 Timeline Execution**: The turn order is managed by a Min-Heap timeline. Characters are re-scheduled based on `action_cost` after every non-free action.
*   **2.2 Event Payload Modification**: Listeners in the EventBus receive payload objects (e.g., `AttackLoad`) passed by reference. They MUST modify the object directly to influence calculations.
*   **2.3 Tick-Based Simulation**: The engine does not use rounds. It uses "Ticks" (discrete units of time). Logic relying on "duration" should count turns or specific events, not wall-clock time.
*   **2.4 Error Handling (Decision Loop)**: Controllers MUST NOT enter an infinite loop when an action fails `can_execute()`. The Orchestrator MUST implement a safety break (Max Attempts).
