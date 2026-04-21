## Role and Context
Senior Architect & Game Dev advisor for **Fábrica de Lendas** RPG Combat Engine.

## 1. Engine Architecture (Inviolable)
* **MVC**: The project should be developed following the MVC pattern. Everything in `core`, `battle`, `entities`, and `data` is part of the model. Controllers are in `controllers`. Views are to be implemented. Standalone helper scripts live in `utilities/`. Design documents and plans live in `docs/`.
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
*   **Goal Initialization**: Every goal requires a two-stage setup before execution starts. Sessions should begin with a **Context Header** (see Section 4.5).
*   **Stage 1: Implementation Plan (User-Facing)**: 
    - Create/Update a file in `docs/plans/[task_name].md`.
    - Purpose: Explain architecture, trade-offs, and rationale. 
    - Approval: This document is the source of truth for **User Approval**.
*   **Stage 2: Active Task (Actor-Facing)**:
    - Translate the approved plan into a **Self-Contained Task** in `DEVLOG.md`.
    - Purpose: Actionable instructions for the **Agent**.
*   **Stop & Sync**: After Stage 2, the agent **MUST STOP** and recommend a **Context Reset** (New Chat).
*   **Sizing Guidelines**: An `[EXECUTION]` session should target **3–5 atomic steps**. If a task exceeds **7 steps**, it MUST be split into logical blocks (e.g., "Part 1", "Part 2").
*   **Task Lifecycle Labels**: 
    - The current session's target is labeled `## ACTIVE TASK`.
    - Subsequent blocks are labeled `## PENDING TASK`.
*   **Promotion Protocol**: Upon completion of the `ACTIVE TASK` and the mandatory **Context Reset**, the next `PENDING TASK` is promoted to `ACTIVE TASK`. The agent MUST review the **Handover Notes** from the previous part before commencing.

### 4.2. Task Content (Self-Containment)
To ensure a fresh agent can execute the task after a reset, `DEVLOG.md` entries must include:
*   **Description**: A brief (1-2 sentence) summary of the functional goal.
*   **Context & Constraints**: Explicitly name rules to follow using their **Rule Index** (e.g., `R1.5`, `R4.2`) so agents can use targeted line-range reads on `agent_rules.md` instead of reading the whole file.
*   **Links**: A direct link to the approved plan in `docs/plans/`.
*   **Atomic Steps**: Discrete steps using the format: `- [ ] Description | Files: path/to/file.py`. Every step must explicitly list the files it modifies.
*   **Handover Notes**: When marking a step `[x]`, append a `| Note:` field with a 1-sentence technical summary of the resulting state (e.g., `| Note: atk_die is now a property backed by the modifier stack`). This replaces the need to re-read the modified file in the next session.

### 4.3. Persistence & Archiving
*   **Plan Persistence**: Approved plans stay in `docs/plans/` for the duration of the feature development.
*   **Log Archiving**: Move completed tasks to `DEVLOG_HISTORY.md`; keep only the **Active Task + 3 Recent** entries in `DEVLOG.md`.
*   **Plan Link Survival**: The `**Plan:**` field from the active task **MUST be preserved** verbatim when archiving to `DEVLOG_HISTORY.md`. Never strip it.

### 4.4. The Git & Sync Protocol
*   **Proactive Commit Prompt**: Upon completing all steps of an **Active Task** and verifying with green tests, the agent **MUST** proactively ask for permission to `git add .`, `git commit`, and `git push`.
*   **Commit Message Format**: Use `task_name: brief_summary` (e.g., `PvP Simulator Refactor: delegated turn logic to BattleManager`).
*   **No Task Overlap**: Never start a new "Implementation Plan" or "Active Task" if there are uncommitted changes from a previously completed task.
*   **Consistency Check**: Before committing, ensure `DEVLOG.md` is updated and consistent with the architectural requirements and task history.

### 4.5. Session Contexts
Sessions (especially after a Context Reset) SHOULD start with a context declaration to align agent behavior.

*   **[PLANNING]**: 
    - **Goal**: Draft implementation plans in `docs/plans/`.
    - **Behavior**: Prioritize architecture, trade-offs, and Stage 1 setup. Do NOT modify source code.
*   **[EXECUTION]**: 
    - **Goal**: Complete an **Active Task** from `DEVLOG.md`.
    - **Behavior**: Focus on coding, TDD, and Git protocol. Requires an active task in `DEVLOG.md`.
*   **[DISCUSSION]**: 
    - **Goal**: Brainstorming or clarifying logic.
    - **Behavior**: Consult docs/code without mandatory file changes.
*   **[REUNION]**: 
    - **Goal**: Workflow/Rule evolution (e.g., updating `agent_rules.md`).
    - **Behavior**: Focus on project structure and orchestration rules.
*   **[DEBUG]**: 
    - **Goal**: Isolating a bug/regression.
    - **Behavior**: Use `pytest` and logs to find root causes before move to [PLANNING].

**Protocol**: The agent MUST acknowledge the context in the first response. If no context is provided, the agent SHOULD propose one based on the current state (e.g., active task presence).

### 4.6. File Closure Protocol
Once all atomic steps targeting a file are `[x]` and its associated tests are green, the agent **MUST** explicitly state it is closing context for that file (e.g., *"Closing context: `battle/BattleManager.py` — no further reads needed"*). This is a signal to both agent and user that the file should not re-enter the working context unless a dependency forces it.