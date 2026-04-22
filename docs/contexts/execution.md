# Context: [EXECUTION]
Implement approved plans via TDD. Focus on atomic steps.

## Mandatory Extraction
- [MISSION_LOG.md](../../MISSION_LOG.md): Read ONLY the active mission and its steps.
- [architecture.md](../../architecture.md): Targeted extraction of relevant rules/patterns only.
- [MISSION_HISTORY.md](../../MISSION_HISTORY.md): Targeted extraction of referenced history entries only.

## Workflow
1. **Confirm**: Explicitly state target mission from `MISSION_LOG.md`.
2. **Execute**:
    - Pick step -> Implement -> `pytest` (TDD mandatory).
    - Check off in `MISSION_LOG.md` + 1-sentence summary.
3. **Track**: Keep `MISSION_LOG.md` updated as progress is made.
4. **StepComplete**:
    - Append `| Note: 1-sentence technical summary` to the mission step.
    - **Context Cleanup**: Close files from this step that are **not** in scope of the next step. Closing strips file content from the active memory window — the step note becomes its memory replacement.
5. **MissionComplete**:
    - **Archive**: Move mission entry to `MISSION_HISTORY.md`. Update `RECENT HISTORY` in `MISSION_LOG.md`.
    - **Sync**: Ask to commit changes

## Constraints
- **Scope Lock**: Only modify files listed in the mission step. Fix "Code Smells" only if blocking the task.
- **Fail Fast**: STOP if a step lacks file paths/logic or has missing dependencies. Never assume; ask.
- **3-Strike**: After 2 failed fix attempts for the same test error, STOP and present logs to the USER.

## Completion & Sync Protocols
*   **Archiving**: Keep **ONLY [ACTIVE] Missions** in `MISSION_LOG.md`.
*   **History Format**: Standardize header in `MISSION_HISTORY.md` as `## YYYY-MM-DD HH:MM: [Title]`.
*   **Git Message**: `task_name: brief_summary`.
*   **Constraint**: No task overlap. Sync completed work before starting new implementation plans.
