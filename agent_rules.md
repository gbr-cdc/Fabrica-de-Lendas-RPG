# Agent Context Configuration [AGENT.GLOBAL]

This document defines the operational rules and skills for AI agents. Adherence to these rules is MANDATORY.

## Managed Documentation Files [AGENT.MANAGED_FILES]
The following files are the source of truth for the project and MUST be accessed and edited ONLY via `utilities/ref_manager.py`:
- `architecture.md` (Prefix: `ARCH.`)
- `docs/GDD/GDD.md` (Prefix: `GDD.`)
- `MISSION_LOG.md` (Prefix: `MISSION.`)
- `workflows.md` (Prefix: `WORKFLOWS.`)
- `agent_rules.md` (Prefix: `AGENT.`)

## Skill: Reference Manager [AGENT.SKILL.REF_MANAGER]
Agents must use `python3 utilities/ref_manager.py` for all documentation operations.

- **Fetch a tag:** Extract content and resolve dependencies. Use: `python3 utilities/ref_manager.py [TAG]`
- **Create a tag:** Append new content. Use: `python3 utilities/ref_manager.py --create [TAG_FOR_FILE] "Content" [--after TAG]`
    - *Smart Placement:* If `--after` is omitted, `ref_manager` will attempt to place it logically based on tag hierarchy.
- **Update a tag:** Replace existing section or line. Use: `python3 utilities/ref_manager.py --update [TAG] "New Content"`
- **Delete a tag:** Remove a section or line. Use: `python3 utilities/ref_manager.py --delete [TAG]`

## Protocol: Workflow Execution [AGENT.PROTOCOL.WORKFLOW]
1. **Receive Workflow:** Agents must fetch the relevant workflow tag from `workflows.md` (e.g., `[WORKFLOWS.FEATURE_PLANNING]`) at the start of a task.
2. **Sequential Order:** Steps MUST be executed in the exact order they are numbered. Do not skip steps.
3. **Exclusivity:** Only ONE workflow can be active at a time.
4. **Completion:** A workflow must be fully completed (all steps checked or reported as done) before switching to another workflow.
5. **No Parallelism:** Do not attempt to execute multiple workflows simultaneously.
