# Agent Context Configuration [AGENT.GLOBAL]

This document defines the operational rules and skills for AI agents. Adherence to these rules is MANDATORY.

## Behavioral Constraints [AGENT.BEHAVIOR]
- **Communication:** Be highly succinct. Do not output conversational filler. Acknowledge commands briefly.
- **Code Modifications:** Make ONLY the changes requested. Avoid large, unnecessary refactorings unless explicitly commanded.
- **Scope:** Never touch or alter files, functions, or variables unrelated to the immediate task.
- **Workflow:** Do not do anything if you don't have an active workflow as explained in [AGENT.PROTOCOL.WORKFLOW].

## Skill: Reference Manager [AGENT.REF_MANAGER]
This is the ONLY valid interface for accessing [AGENT.ACCESS_RULES.FORBIDDEN_FILES].
It should be used for editing agent_rules.md after initial read.
Agents must use `python3 utilities/ref_manager.py` for all documentation operations.

- **Tag content:** 
    - Line Tag: A tag placed inside a standard line of text (e.g., Timeout rule [TAG_TIME]: Set timeout to 30s). It references and modifies ONLY that specific single line.
    - Section Tag: A tag placed inside a Markdown header (e.g., ### Database Rules [TAG_DB]). It references the header and all content below it, stopping immediately before the next header of equal or higher level.
- **Fetch a tag:** Get referenced content with the tag. Use: `python3 utilities/ref_manager.py [TAG]`
- **Create a tag:** Append new content. Use: `python3 utilities/ref_manager.py --create [TAG_FOR_FILE] "Content"`
    - *Smart Placement:* `ref_manager` will automatically place the new tag logically based on tag hierarchy.
- **Update a tag:** Replace existing section or line. Use: `python3 utilities/ref_manager.py --update [TAG] "New Content" [--from-file path]`
    - Single-Line Constraint: If updating a line tag, the "New Content" MUST be exactly one line. Do not pass multi-line strings. 
    - Line Tag Preservation: When updating a line, you MUST include the exact original line tag within your "New Content".
    - Section Tag Preservation: When updating a section, your "New Content" MUST start with the original Markdown header containing the tag (e.g., ## Section Name [TAG]). Do not strip the header away.
- **Delete a tag:** Remove a section or line. Use: `python3 utilities/ref_manager.py --delete [TAG]`

### Efficiency Rules [AGENT.REF_MANAGER.EFFICIENCY]
To minimize redundant operations and maximize context utility:
- **Avoid Redundant Fetches:** Do not fetch a tag if you already have its content in your current context.
- **Batch Requests:** Optimize `ref_manager` usage by determining all necessary tags beforehand. Execute a single call with multiple tags: `python3 utilities/ref_manager.py [TAG1] [TAG2] [TAG3]...`

### Reference Conventions [AGENT.REF_MANAGER.CONVENTIONS]
Considering filepath = module_name/FileName.py
- **Module Documentation:** To access documentation for a specific module, use the pattern: `[ARCH.module_name]`
    - Example: `[ARCH.core]`
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

### Raw Project File Policy [AGENT.ACCESS_RULES.RAW_FILES]
Reading raw project files (e.g., source code, scripts) is a costly operation. Agents MUST prefer fetching a file's documentation via `ref_manager` rather than opening the raw file directly.

**ONLY read a raw file if at least one of the following is true:**
- The user explicitly asked you to read the raw file.
- The file's documentation does not exist.
- You have already fetched and read the file's documentation, and it lacks the specific information needed for your task.

## Protocol: Workflow Execution [AGENT.PROTOCOL.WORKFLOW]
1. **Receive Workflow:** You should receive a [WORKFLOWS.(...)] tag in the frist prompt. Fetch the tag and make ir your active workflow. If you don't have one, ask for it. Refuse to do anything without an active workflow.
2. **Sequential Order:** Steps MUST be executed in the exact order they are numbered. Do not skip steps.
3. **Exclusivity:** Only ONE workflow can be active at a time.
4. **Completion:** A workflow must be fully completed (all steps checked or reported as done) before switching to another workflow.
5. **No Parallelism:** Do not attempt to execute multiple workflows simultaneously.
