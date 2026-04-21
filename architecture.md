# Architectural Guardrails (Technical Reference)

These rules are context-exclusive and should be referenced in `MISSION_LOG.md` when relevant to the task. They MUST be read during the `[PLANNING]` context.

## ARCH.1: Core Patterns
*   **1.1 Game-MVC**: Strict separation. **Models** (Rules/State in `core/`, `battle/`, `entities/`, `data/`); **Controllers** (Flow/Commands in `controllers/`); **Views** (Logs/UI are TBD).
*   **1.2 Command Pattern**: All actions must inherit from `GameAction` and follow the command pattern.
*   **1.3 Observer/EventBus**: Decouple reactive logic (Effects/Passives) via an EventBus. Orchestrators (e.g., `BattleManager`) manage subscriptions.
*   **1.4 IoC**: Implementations using hooks expose them via `get_hooks()`. Only the Orchestrator handles event registration.
*   **1.5 Data-Driven**: GameAction logic should be defined in JSON files when possible (e.g., defining abilities and effects).
*   **1.6 Lifecycle Safety**: Wrap ephemeral hooks (1 action cycle) in `try...finally` for guaranteed unsubscription.
*   **1.7 CQRS**: Methods for direct state changes; Events for notification ONLY.
*   **1.8 Modifier Stack**: Stats are immutable; use the Modifier Stack Pattern for dynamic attributes.
*   **1.9 Anemic Entities**: All classes in `entities/` are data containers; logic resides in external systems.
*   **1.10 Protocols & Typing**: Use `typing.Protocol` for DI. Use `from __future__ import annotations`. Keep typing imports in `TYPE_CHECKING`.
