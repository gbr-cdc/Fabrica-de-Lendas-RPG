# Agent Context Configuration [AGENT.GLOBAL]

This document defines the operational rules and skills for AI agents. Adherence to these rules is MANDATORY.

## Skill: Reference Manager [AGENT.REF_MANAGER]
This is the ONLY valid interface for accessing [AGENT.ACCESS_RULES.FORBIDDEN_FILES].
It should be used for accessing agent_rules.md after initial read.
Agents must use `python3 utilities/ref_manager.py` for all documentation operations.

- **Fetch a tag:** Extract content and resolve dependencies. Use: `python3 utilities/ref_manager.py [TAG]`
- **Create a tag:** Append new content. Use: `python3 utilities/ref_manager.py --create [TAG_FOR_FILE] "Content" [--after TAG]`
    - *Smart Placement:* If `--after` is omitted, `ref_manager` will attempt to place it logically based on tag hierarchy.
- **Update a tag:** Replace existing section or line. Use: `python3 utilities/ref_manager.py --update [TAG] "New Content"`
- **Delete a tag:** Remove a section or line. Use: `python3 utilities/ref_manager.py --delete [TAG]`

### Reference Conventions [AGENT.REF_MANAGER.CONVENTIONS]
Considering filepath = module_name/FileName.py
- **File Documentation:** To access documentation for a specific file, use the pattern: `[ARCH.module_name.FileName]`
    - Example: `[ARCH.core.BaseClasses]`
- **Class Documentation:** To access documentation for a class, use: `[ARCH.module_name.FileName.CLASS:ClassName]`
    - Example: `[ARCH.core.BaseClasses.CLASS:GameAction]`
- **Function Documentation:** To access documentation for a standalone function, use: `[ARCH.module_name.FileName.FUNCTION:function_name]`
    - Example: `[ARCH.core.CharacterSystem.FUNCTION:take_damage]`
- **Method Documentation:** To access documentation for a class method, use: `[ARCH.module_name.FileName.METHOD:Class.method]`
    - Example: `[ARCH.battle.BattleManager.METHOD:BattleManager.emit]`

## File Access Rules [AGENT.ACCESS_RULES]

Files listed in [AGENT.ACCESS_RULES.FORBIDDEN_FILES] are NOT regular files. They are managed knowledge resources.

**Direct access is INVALID:**
- RESTRICTION: Never use view_file, grep_search, or run_command(cat/ls) on [AGENT.ACCESS_RULES.FORBIDDEN_FILES].
- Any direct access will result in corrupted or misleading context, leading to session termination and loss of work.

### Mandatory Access Protocol [AGENT.ACCESS_RULES.PROTOCOL]

Before accessing ANY file, the agent MUST:

1. Determine if the file belongs to [AGENT.ACCESS_RULES.FORBIDDEN_FILES]
2. If YES:
   - DO NOT access the file directly
   - MUST use [AGENT.REF_MANAGER]
3. If NO:
   - Direct access is allowed

Failure to follow this protocol invalidates the task result.

### Managed Files [AGENT.ACCESS_RULES.FORBIDDEN_FILES]
- `.forbidden/GDD.md` (Prefix: `GDD.`)
- `.forbidden/MISSION_LOG.md` (Prefix: `MISSION.`)
- `.forbidden/workflows.md` (Prefix: `WORKFLOWS.`)
- `.forbidden/architecture.md` (Prefix: `ARCH.`)

## Protocol: Workflow Execution [AGENT.PROTOCOL.WORKFLOW]
1. **Receive Workflow:** Agents must fetch the relevant workflow tag (e.g., `[WORKFLOWS.FEATURE_PLANNING]`) at the start of a task.
2. **Sequential Order:** Steps MUST be executed in the exact order they are numbered. Do not skip steps.
3. **Exclusivity:** Only ONE workflow can be active at a time.
4. **Completion:** A workflow must be fully completed (all steps checked or reported as done) before switching to another workflow.
5. **No Parallelism:** Do not attempt to execute multiple workflows simultaneously.
