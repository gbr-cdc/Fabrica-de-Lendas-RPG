# Context: [EXECUTION]
Implement approved plans via TDD. Focus on atomic steps.

## Mandatory Reading
- [MISSION_LOG.md](../../MISSION_LOG.md): Active mission/steps.
- [architecture.md](../../architecture.md): Referenced rules.
- [MISSION_HISTORY.md](../../MISSION_HISTORY.md): Referenced history.

## Workflow
1. **Confirm**: Explicitly state target mission from `MISSION_LOG.md`.
2. **Execute**:
    - Pick step -> Implement -> `pytest` (TDD mandatory).
    - Check off in `MISSION_LOG.md` + 1-sentence summary.
3. **Track**: Keep `MISSION_LOG.md` updated as progress is made.
4. **StepComplete**: Append `| Note: 1-sentence technical summary` to the step.
5. **Archive**: Move completed missions to `MISSION_HISTORY.md` + update `RECENT HISTORY` in `MISSION_LOG.md`.
6. **Sync**: Ask to commit/sync after mission goal.

## Constraints
- **Scope Lock**: Only modify files listed in the mission step. Fix "Code Smells" only if blocking the task.
- **Fail Fast**: STOP if a step lacks file paths/logic or has missing dependencies. Never assume; ask.
- **3-Strike**: After 2 failed fix attempts for the same test error, STOP and present logs to the USER.

## Completion & Sync Protocols
*   **Archiving**: Keep **ONLY [ACTIVE] Missions** in `MISSION_LOG.md`.
*   **History Format**: Standardize header in `MISSION_HISTORY.md` as `## YYYY-MM-DD HH:MM: [Title]`.
*   **Git Message**: `task_name: brief_summary`.
*   **Constraint**: No task overlap. Sync completed work before starting new implementation plans.
