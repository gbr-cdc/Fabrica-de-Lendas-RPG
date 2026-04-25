# Context: [REUNION]
Evolution of **Operational Rules** and workflow protocols.

## Workflow
1. **Initialize**: Read `agent_rules.md` followed IMMEDIATELY by this context file.
2. **Identify**: Pinpoint specific rules or workflow steps that caused confusion or inefficiency.

2. **Propose**: Draft `agent_rules.md` or `docs/contexts/` changes.
3. **Formalize**: Implement upon USER approval.
4. **Report & Sync**:
    - Generate a reunion report in `docs/reports/reunion_YYYY-MM-DD_HH:MM.md` summarizing: problems identified, changes made, files modified.
    - Ask USER to commit changes and suggest message: `reunion: description_of_change`.

## Constraints
- **Meta-Focus**: Edit only `agent_rules.md`, `docs/contexts/`, or standard templates.
- **Exclusion**: Technical architecture belongs in `[PLANNING]`.
- **NO IMPLEMENTATION**: Do not modify any code in `core/`, `battle/`, `entities/`, etc.
