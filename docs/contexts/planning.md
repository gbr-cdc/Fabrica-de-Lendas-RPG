# Context: [PLANNING]
Architectural design and technical rationale. No implementation.

## Mandatory Reading
- [architecture.md](../../architecture.md): Entire file (guardrails).
- Relevant code: Current state/compatibility.

## Workflow (Feature Planning)
1. **Understand**: Problem statement and User's desired outcome/technical preference.
2. **Analyze**: Validate against architecture.md guardrails and common gaming design patterns.
3. **Propose**: Create/edit `docs/plans/[task].md`. (Challenge User direction if justified).
4. **Iterate**: Refine via feedback.
5. **Finalize**: Approved plan leads to `[TASK SETUP]`.
6. **[TASK SETUP]**: Translate the approved Plan into a specific `MISSION_LOG.md` entry with atomic steps.

## Workflow (Systemic Planning)
1. **Discuss**: High-level architectural changes or new patterns.
2. **Refine**: Validate against existing guardrails (check for breaking changes).
3. **Apply**: Edit `architecture.md` with new/updated ARCH rules.
4. **Impact Analysis**: Determine if existing code needs a migration mission.
5. **Finalize**: Approved changes lead to a **New Chat** or a **Feature Planning** session if migration is needed.

## Constraints
- **Scope**: Edit only `docs/plans/` (Feature) or `architecture.md` (Systemic).
- **Focus**: High-level structure, interface definitions, and state management logic.

## Documentation Standards (MISSION_LOG.md)
*   **Header Format**: `## MISSION: [Title] ([Status]) [PART X]`.
*   **Sizing**: 3-5 steps per part. Max 7 steps (split if larger).
*   **Entry Format**:
    - **Summary**: 1-2 sentences on technical goal.
    - **Rule References**: Comma-separated list of ARCH rules from `architecture.md` (e.g., `ARCH.1.2, ARCH.1.5`).
    - **Plan**: Link to the approved `docs/plans/[task].md`.
    - **Steps**: Atomic TDD steps.
*   **Step Format**: `- [ ] Description | Files: path/to/file.py`.
