# Context: [EXECUTION]
Implement approved plans via TDD. Focus on atomic steps.

## Mandatory Extraction
- [MISSION_LOG.md](../../MISSION_LOG.md): **Read entirely**.
- [architecture.md](../../architecture.md): Extract only the **ARCH rules** referenced in the active mission (e.g., `ARCH.1.2`, `ARCH.1.5`).
- [MISSION_HISTORY.md](../../MISSION_HISTORY.md): Extract only the entries linked in `MISSION_LOG.md`'s **RECENT HISTORY** section.

## Workflow
1. **Confirm**: Explicitly state target mission from `MISSION_LOG.md`.
2. **Execute**:
    - Pick step -> Implement -> `pytest` (TDD mandatory).
3. **StepComplete**:
    - Append `| Note: 1-sentence technical summary` to the mission step.
    - **Context Cleanup**: Close files opened in this step that are **not** in scope of the next step. Use last step notes as memory.
4. **MissionComplete**:
    - **Fail Proof**: Ensure all tests pass and 100% test coverage with `pytest --cov`. If not, stop and ask for instructions.
    - **Archive**: Move mission entry to `MISSION_HISTORY.md`. Update `RECENT HISTORY` in `MISSION_LOG.md`.
    - **History Format**: Standardize header in `MISSION_HISTORY.md` as `## YYYY-MM-DD HH:MM: [Title]`.
    - **Git Message**: `task_name: brief_summary`.
    - **Sync**: Ask to commit changes

## Constraints
- **3-Strike**: After 2 failed fix attempts for the same test error, STOP and present logs to the USER.
