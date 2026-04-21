# Implementation Plan: Workflow & Token Optimization

## 1. Problem Statement
The current workflow requires reading the full `agent_rules.md` at the start of every session. As tasks in `DEVLOG.md` grow, context saturation leads to high token costs and reduced precision. We need a way to maintain atomic precision without the overhead of redundant reading.

## 2. Proposed Solutions

### 2.1. Block-Based Execution (Sizing)
- **Constraint**: Active Tasks in `DEVLOG.md` should be scoped to logical sub-modules or checkpoints.
- **Guideline**: An `[EXECUTION]` session should ideally target 3–5 atomic steps. If a task exceeds 7 steps, it MUST be split into "Part 1", "Part 2", etc., to force a context reset and prevent saturation.

### 2.2. Handover Notes (State Persistence)
- **Feature**: Add a `| Note: ...` field to the `DEVLOG.md` step format.
- **Purpose**: When a step is marked `[x]`, the agent provides a 1-sentence technical summary (e.g., "Interface X now requires param Y"). This allows the next agent to understand changes without re-reading the modified file.

### 2.3. Targeted Rule Mapping
- **Feature**: Update `agent_rules.md` to use a consistent indexing system (e.g., R1.1, R4.2).
- **Protocol**: The `Context & Constraints` field in `DEVLOG.md` must link to these indices.
- **Benefit**: Agents can use `view_file` with line ranges to read *only* the relevant rules for that specific task.

### 2.4. File Closure Protocol
- **Behavior**: Once a file's associated steps are completed and verified (tests green), the agent should explicitly mention it is "closing" the context for that file.

## 3. Implementation Steps

### 3.1. Update `agent_rules.md`
- Refactor Section 4.1 (Command Post) to include "Sizing Guidelines".
- Update Section 4.2 (Task Content) to include the `Note` field and "Rule Mapping" requirement.
- Add Section 4.6 (Context Cleanup) to formalize the "File Closure" behavior.

### 3.2. Update `DEVLOG.md` Template
- Add a comment/tip about the new step format.

## 4. Verification
- The next `[EXECUTION]` session (for Postura Defensiva) will be the first "stress test" of the block-based approach.
