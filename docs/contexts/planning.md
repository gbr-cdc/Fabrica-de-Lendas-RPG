# Context: [PLANNING]
Architectural design and technical rationale. No implementation.

## Mandatory Reading
- [architecture.md](../../architecture.md): Entire file (guardrails).
- Relevant code: Current state/compatibility.

## Workflow
1. **Understand**: Problem statement and User's desired outcome/technical preference.
2. **Analyze**: Validate against architecture.md guardrails and common gaming design patterns.
3. **Propose**: Create/edit `docs/plans/[task].md`. (Challenge User direction if justified).
4. **Iterate**: Refine via feedback.
5. **Finalize**: Approved plan leads to `[TASK SETUP]`.
6. **[TASK SETUP]**: Translate the approved Plan into a specific `MISSION_LOG.md` entry with atomic steps.

## Constraints
- **No Source Edits**: Edit only `docs/plans/`.
- **Focus**: High-level structure, interface definitions, and state management logic.

## Documentation Standards (MISSION_LOG.md)
*   **Header Format**: `## MISSION: [Title] ([Status]) [PART X]`.
*   **Sizing**: 3-5 steps per part. Max 7 steps (split if larger).
*   **Entry Format**: Summary, Rule References (e.g., `ARCH.1.5`), Plan Link, and Atomic Steps.
*   **Step Format**: `- [ ] Description | Files: path/to/file.py`.
