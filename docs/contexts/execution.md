# Context: [EXECUTION]
Implement approved plans via TDD. Focus on atomic steps.

## Mandatory Extraction
- [MISSION_LOG.md](../../MISSION_LOG.md): **Read entirely**.
- [architecture.md](../../architecture.md): Extract only the **ARCH rules** referenced in the active mission (e.g., `ARCH.1.2`, `ARCH.1.5`).
- [MISSION_HISTORY.md](../../MISSION_HISTORY.md): Extract only the entries linked in `MISSION_LOG.md`'s **RECENT HISTORY** section.

## Workflow
1. **Confirm**: Explicitly state target mission from `MISSION_LOG.md`.
2. **Execute (TDD Phases)**:
    - **RED (Test Objective)**: Pick a [RED] step -> Create/Update Integration/Scenario Test based on the detailed objective -> `pytest` (Must Fail).
    - **GREEN (Implementation)**: Pick the corresponding [GREEN] step -> Implement approved logic -> `pytest` (Must Pass).
3. **Execute (Non-TDD Phases)**:
    - **BLUE (Implementation)**: Pick the corresponding [BLUE] step -> Implement approved logic -> pytest (Regression: Full suite must pass)
4. **StepComplete ([RED/GREEN] or [BLUE])**:
    - Append `| State: description of step results with all information summarized for the next step` to the mission step.
        - **Source of truth**: Consider this state note is all next agent will have from previous context, so make sure it is descriptive and concise.
    - **Context Cleanup**: After completing a [RED/GREEN] or [BLUE] step, suggest a commit message and call for a new session for context reset. 
5. **MissionComplete**:
    - **Fail Proof**: Ensure all tests pass and 100% test coverage with `pytest --cov`. If not, stop and ask for instructions.
    - **Archive**: Move mission entry to `MISSION_HISTORY.md`. Update `RECENT HISTORY` in `MISSION_LOG.md` (Keep only the 3 most recent links).
    - **History Format**: Standardize header in `MISSION_HISTORY.md` as `## YYYY-MM-DD HH:MM: [Title]`.
    - **Git Message**: `task_name: brief_summary`.
    - **Sync**: Ask to commit changes

## Test Quality Standards
- **Behavior over Implementation**: Tests MUST verify the outcome (e.g., final HP, logs, state changes) rather than internal implementation details (e.g., checking specific list indices or private method calls).
- **Controlled Mocking**: Prefer real object instances (`Character`, `StatModifier`) initialized via `DataManager` over `MagicMock` for core logic. Use Mocks only for external dependencies (Controllers, I/O).
- **Decoupling**: Ensure tests do not break upon internal refactors if the public behavior remains unchanged.
- **Invariants**: When possible, assert that the system state remains valid according to ARCH rules (e.g., no negative HP, sorted timeline).

## Constraints
- **3-Strike**: After 2 failed fix attempts for the same test error, STOP and present logs to the USER.

