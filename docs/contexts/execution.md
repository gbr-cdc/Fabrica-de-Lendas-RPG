# Context: [EXECUTION]
Implement approved plans via TDD. Focus on atomic steps.

## Mandatory Extraction
- [MISSION_LOG.md](../../MISSION_LOG.md): **Read entirely**.
- [architecture.md](../../architecture.md): Extract only the **ARCH rules** referenced in the active mission (e.g., `[ARCH.1.2]`, `[ARCH.1.5]`).
- [MISSION_HISTORY.md](../../MISSION_HISTORY.md): Extract only the entries linked in `MISSION_LOG.md`'s **RECENT HISTORY** section.

## Workflow
1. **Confirm**: Explicitly state target mission from `MISSION_LOG.md`.
2. **State Check**: Check last State Note in previous completed step for guidance(if exists).
3. **Execute (TDD Phases)**:
    - **RED (Test Objective)**: Pick a [RED] step -> Create/Update Integration/Scenario Test based on the detailed objective -> `pytest` (Must Fail).
    - **GREEN (Implementation)**: Pick the corresponding [GREEN] step -> Implement approved logic -> `pytest` (Must Pass).
4. **Execute (Non-TDD Phases)**:
    - **BLUE (Implementation)**: Pick the corresponding [BLUE] step -> Implement approved logic -> pytest (Regression: Full suite must pass)
5. **PhaseComplete ([RED/GREEN] or [BLUE])**:
    - Mark completed steps [ ] -> [x]
    - Append `| State: description of step results with all information summarized for the next step` to the [GREEN] or [BLUE] step.
        - **Source of truth**: Consider this state note is all next agent will have from previous context, so make sure it is descriptive and concise.
    - **Context Cleanup**: After completing a [RED/GREEN] or [BLUE] phase, suggest a commit message and call for a new session for context reset. 
6. **MissionComplete**:
    - **Fail Proof (Verification)**: 
        1. All tests MUST pass.
        2. 100% test coverage for the modified modules (`pytest --cov`).
        3. **DoD Check**: Explicitly verify each item in the mission's "Definition of Done".
        4. **Behavioral Audit**: Confirm the outcome matches the behavioral standards in "Test Quality Standards" (e.g., check final system state, not just mocks).
        - *If any check fails, STOP and ask for instructions.*
    - **Archive**: Move mission entry to `MISSION_HISTORY.md`. Update `RECENT HISTORY` in `MISSION_LOG.md` (Keep only the 3 most recent links with their **exact line ranges** e.g., `#L10-25`).
    - **History Format**: Standardize header in `MISSION_HISTORY.md` as `## YYYY-MM-DD HH:MM: [Title]`. Ensure the `#Lstart-end` reference in `MISSION_LOG.md` accurately covers the full entry.
    - **Git Message**: `task_name: brief_summary`.
    - **Sync**: Ask to commit changes

## Test Quality Standards
- **Behavior over Implementation**: Tests MUST verify the outcome (e.g., final HP, logs, state changes) rather than internal implementation details (e.g., checking specific list indices or private method calls).
- **Controlled Mocking**: Use real instances for domain logic (Entities, Systems). Mock ONLY system boundaries (I/O, UI) or to enforce determinism. Use `DiceManager.schedule_result()` for simulating dice rolls.
- **Standardized Setup**: Use `tests.utils.entity_factory` for dummies or `DataManager` for integration tests. Avoid manual instantiation of `Character`, `Weapon`, or `Armor` to ensure GDD compliance `[ARCH.1.5]`.
- **Decoupling**: Ensure tests do not break upon internal refactors if the public behavior remains unchanged.
- **Invariants**: Assert that system state remains valid according to ARCH rules (e.g., stats calculated via the Modifier Stack `[ARCH.1.8]`, no negative HP).

## Constraints
- **3-Strike**: After 2 failed fix attempts for the same test error, STOP and present logs to the USER.

