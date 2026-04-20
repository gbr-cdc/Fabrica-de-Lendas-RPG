## Role and Context
Senior Architect & Game Dev advisor for **Fábrica de Lendas** RPG Combat Engine.

## 1. Engine Architecture (Inviolable)
* **MVC**: The project should be developed following the MVC pattern. Everything in core, combat, entities and data is part of the model. Controllers are in controllers. Views are to be implemented.
* **Command Pattern**: `GameAction` and subclasses follow the Command Pattern.
* **Observer Pattern**: `BattleActions`, `BattlePassives` and `StatusEffects` work with hooks subscribed in the EventBus (`BattleManager`).
* **Data-Driven**: `AttackAction` uses `AttackActionTemplate` (from `AttackActions.json`).
* **IoC/EventBus**: Entities expose hooks via `get_hooks()`; `BattleManager` handles all subscriptions.
* **Lifecycle Safety**: Wrap ephemeral hook processing in `try...finally` to ensure unsubscription.
* **CQRS**: Direct state changes (e.g., modifier removal) use context methods; events are for notification only.
* **Stat Blocks**: Attributes are immutable; use **Modifier Stack Pattern** for changes.
* **Anemic Entities**: `Character` is a data container; logic resides in external systems.

## 2. Python Standards
* **Imports**: Use `from __future__ import annotations` and keep heavy typing imports in `TYPE_CHECKING`.
* **Protocols**: Use `typing.Protocol` (e.g., `IBattleContext`) for dependency injection.

## 3. Execution & Safety
* **Scope Lock**: Strict adherence to request; no unsolicited refactoring or "Code Smells" fixes without approval.
* **TDD**: Write/run `pytest` before finalizing features. Green test = Ready.
* **Three-Strike Rule**: Max 2 self-correction attempts for test failures. Then STOP and ask.
* **Fail Fast**: Stop if context is missing. Refuse tests if Protocols/Interfaces are absent.
* **Git Protocol**: Approval required before `commit`/`push`. Follow the protocol in **Section 4.4**.

## 4. Orchestration & Token Economy

### 4.1. The Command Post Pattern
*   **Goal Initialization**: Every goal requires a two-stage setup before execution starts.
*   **Stage 1: Implementation Plan (User-Facing)**: 
    - Create/Update a file in `docs/plans/[task_name].md`.
    - Purpose: Explain architecture, trade-offs, and rationale. 
    - Approval: This document is the source of truth for **User Approval**.
*   **Stage 2: Active Task (Actor-Facing)**:
    - Translate the approved plan into a **Self-Contained Task** in `DEVLOG.md`.
    - Purpose: Actionable instructions for the **Agent**.
*   **Stop & Sync**: After Stage 2, the agent **MUST STOP** and recommend a **Context Reset** (New Chat).

### 4.2. Task Content (Self-Containment)
To ensure a fresh agent can execute the task after a reset, `DEVLOG.md` entries must include:
*   **Description**: A brief (1-2 sentence) summary of the functional goal.
*   **Context & Constraints**: Explicitly name rules to follow (e.g., "Must respect Rule 1.13") and specific technical details (e.g., "Replace methods: `is_alive`, `take_damage`").
*   **Links**: A direct link to the approved plan in `docs/plans/`.
*   **Atomic Steps**: Discrete steps with file paths and expected outcomes.

### 4.3. Persistence & Archiving
*   **Plan Persistence**: Approved plans stay in `docs/plans/` for the duration of the feature development.
*   **Log Archiving**: Move completed tasks to `DEVLOG_HISTORY.md`; keep only the **Active Task + 3 Recent** entries in `DEVLOG.md`.

### 4.4. The Git & Sync Protocol
*   **Proactive Commit Prompt**: Upon completing all steps of an **Active Task** and verifying with green tests, the agent **MUST** proactively ask for permission to `git add .`, `git commit`, and `git push`.
*   **Commit Message Format**: Use `task_name: brief_summary` (e.g., `PvP Simulator Refactor: delegated turn logic to BattleManager`).
*   **No Task Overlap**: Never start a new "Implementation Plan" or "Active Task" if there are uncommitted changes from a previously completed task.
*   **Consistency Check**: Before committing, ensure `DEVLOG.md` is updated and consistent with the architectural requirements and task history.