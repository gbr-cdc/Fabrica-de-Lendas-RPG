# Context: [PLANNING]
Architectural design and technical rationale. No implementation.

## Mandatory Reading
- [architecture.md](../../architecture.md): Entire file (guardrails).
- Relevant code: Current state/compatibility.

## GDD References (Conditional)
Reading the **Modular GDD** (`docs/GDD/`) is NOT mandatory. Only read if:
1.  Explicitly prompted by the USER.
2.  Implementing a mechanic that requires rule translation into technical steps.
*   **Targeted Reading**: Use `grep` to find specific `[GDD.X.Y]` tags. Never read the entire directory.
*   **Dependency Resolution**: If a mechanic has `[DEPENDS: GDD.X.Y]`, you MUST resolve those dependencies to ensure the resulting `MISSION_LOG.md` steps are technically sound and architecturally compliant.

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
- **NO IMPLEMENTATION**: Do not modify any code in `core/`, `battle/`, `entities/`, etc. Implementations MUST wait for the `[EXECUTION]` context.

## Documentation Standards (MISSION_LOG.md)
*   **Header Format**: `## MISSION: [Title] ([Status]) [PART X]`.
*   **Sizing**: 3-5 steps per part. Max 7 steps (split if larger).
*   **Entry Format**:
    - **Summary**: Concise technical overview of the goal. Provide enough context to guide execution.
    - **Acceptance Criteria (AC)**: Mandatory section. Define the behavior-based scenarios that MUST pass (e.g., "Warrior must reduce damage by X when in Postura Defensiva"). This serves as the blueprint for the [EXECUTION] RED phase.
    - **Rule References**: Comma-separated list of ARCH rules from `architecture.md` (e.g., `ARCH.1.2, ARCH.1.5`).
    - **Plan**: Link to the approved `docs/plans/[task].md`.
    - **Steps**: Atomic TDD steps, distinguishing between RED (Test) and GREEN (Implementation) when necessary.
*   **Step Format**: `- [ ] [RED/GREEN] Description | Files: path/to/file.py`.
    - **Self-Sufficiency**: Steps MUST be descriptive enough to allow an [EXECUTION] agent to work without reading the approved `docs/plans/`.

