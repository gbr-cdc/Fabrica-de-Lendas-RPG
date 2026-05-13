# WORKFLOWS [WORKFLOWS.GLOBAL]

## FEATURE PLANNING [WORKFLOWS.FEATURE_PLANNING]
1. **Check Architectural Rules:** Fetch [ARCH.RULES]
2. **Understand:** Problem statement and User's desired outcome/technical preference. Challenge user directions if you have better solutions to the problem.
3. **Analyze:** Validate against ARCH.RULES and common gaming design patterns.
4. **Propose:** Create `docs/plans/[task].md`.
5. **HALT EXECUTION:** Present the plan to the user and ask for approval. **YOU MUST STOP GENERATING TEXT HERE.** Do not proceed to Step 6 under any circumstances until the user explicitly replies with approval.
6. **Check Mission Format:** Fetch [ARCH.DOC_STANDARDS.MISSION]
7. **Mission:** Translate the approved Plan into a mission. Create new mission with tag [MISSION.ACTIVE.(mission_name)].
  **Note:** Do not try to check MISSION_LOG.md to confirm file state or active missions, just use **Skill: Reference Manager** to *create a tag* with the new mission. If ref_manager fails informing tag already exists, change mission name and tag.
8. **Git Protocol**: STOP and ask USER to commit changes. Suggest message: `planning: create mission for ...`.


## ARCHITECTURAL ANALYSIS [WORKFLOWS.ARCH_ANALYSIS]
1. **Receive:** Fetch [ARCH.(...)] tags user wants to discuss. If you didn't received any, aks for tags.
2. **Discuss**: Discuss architectural problems and needed changes based on the information received.
3. **Apply**: Updated, create or delete [ARCH.(...)] tags according with desired changes.
4. **Impact Analysis**: Determine if existing code needs a migration mission.

## INDEPENDENT EXECUTION [WORKFLOWS.INDEPENDENT_EXECUTION]
1. **Understand:** Analyze the problem statement and the desired outcome. Challenge the instructions if you have a structurally better solution.
2. **Propose:** Create/edit `docs/plans/"IE_task_description".md` with an execution plan.
3. **HALT EXECUTION:** Present the plan to the user and ask for approval. **YOU MUST STOP GENERATING TEXT HERE.** Do not proceed to Step 4 under any circumstances until the user explicitly replies with approval.
4. **Implement:** Execute the approved plan.
5. **Test:** Write or update tests within the `tests/` module to cover your implementation. Do not create temporary or disposable test files outside of the `tests/` directory. Run the project test suite using `pytest`. All tests must pass at the end of execution to ensure system integrity.
6. **Evaluate:** Check if the project documentation need to be updated.
    - **Filter:** From the list of files you modified this session. Exclude `tests/` and root files.
    - **Document:** If there are any modified files left after filtering, transition to the [WORKFLOWS.DOC_MODULES] workflow. Then, go to next step.
    - **Report:** Create a report in `docs/reports` as `IE_YYYY-MM-DD_HH:MM.md` with everything done during this workflow.
    - **Git Protocol:** Stop and ask user to commit with message `IE: execution description`.

## FLASH EXECUTION [WORKFLOWS.FLASH_EXECUTION]
Note: This workflow is designed to work across multiple rapid interactions. Follow the execution loop precisely and be concise and direct in your responses.
- **Execution Loop:**
    1. **Understand:** Undestand the objective of the execution and what needs to be done. STOP and ask if the objective isn't clear.
    2. **Execute:** Follow the instructions given by the user. Do exactly what is asked; this workflow is used for simple and quick tasks. Avoid major refactoring. If the task requires significant refactoring, STOP and provide a report.
    3. **Verify:** Check if all objectives were achieved and if implementations done works as intended.

## OPERATIONAL CHANGES [WORKFLOWS.OPERATIONAL_CHANGES]
1. **Receive:** Fetch [WORKFLOWS.GLOBAL]
2. **Identify**: Pinpoint specific workflow and steps that caused confusion or inefficiency, or new elements that need to be implemented.
3. **Propose**: Propose the updates that should be applied to specifc [WORKFLOWS.(...)] or [AGENT.(...)] tags.
4. **HALT EXECUTION:** Wait for user to appove updates. **YOU MUST STOP GENERATING TEXT HERE.** Do not proceed to Step 5 under any circumstances until the user explicitly replies with approval.
5. **Update**: Applay updates using `ref_manager` tool.
6. **Report & Sync**:
    - Generate a reunion report in `docs/reports/reunion_YYYY-MM-DD_HH:MM.md` summarizing: problems identified and changes made.
    - Ask USER to commit changes and suggest message: `reunion: description_of_change`.

## MISSION EXECUTION [WORKFLOWS.MISSION_EXECUTION]
1. **Receive:** You MUST receive a [MISSION.ACTIVE.(...)] tag in the SAME prompt as the workflow trigger. Do NOT search MISSION_LOG or conversation history for it. If missing, STOP and ask: "Please provide the active mission tag to proceed."
2. **State Check:** Fetch all tags in the mission's "Rule References" and "Documentation References". Read the mission's plan.
3. **Execution Loop:** Read all steps in the mission. Execute them sequentially:
    - **If `[RED]`:** Create/Update Test based on objective -> `pytest` (Must Fail). Testes must follow quality standards in [ARCH.TEST_QUALITY].
    - **If `[GREEN]`:** Implement logic -> `pytest` (Must Pass).
    - **If `[BLUE]`:** Implement logic -> `pytest` (Regression: Full suite must pass).
4. **Mission Completion:** Once all steps are executed:
    - **Verification**: All tests MUST pass.
    - **Coverage**: At least 80% test coverage for modified modules (`pytest --cov`).
    - **DoD Check**: Explicitly verify each item in the mission's "Definition of Done".
5. **Evaluate Documentation**: 
    - **Filter**: List files modified this session. Exclude `tests/` and root files.
    - **Document**: If there are files left, transition to [WORKFLOWS.DOC_MODULES]. Return here when done.
6. **Archive**: Fetch [ARCH.DOC_STANDARDS.MISSION.ARCHIVED]. Delete [MISSION.ACTIVE.(...)]. Create [MISSION.ARCHIVE.(...)] following the standard.
7. **Git Protocol:** STOP and ask user to commit with message "[MISSION_TAG]: Completed".

## DOCUMENT MODULES [WORKFLOWS.DOC_MODULES]
1. **Get template**: Fetch [ARCH.DOC_STANDARDS.MODULE] for documentation template. 
2. **Identify**: Use [AGENT.REF_MANAGER.CONVENTIONS] to determine the tags for the modified files' documentation. 
3. **Evaluate**: Fetch all required file documentation tags in a single batched `ref_manager.py` call. Check for missing elements or discrepancies vs [ARCH.DOC_STANDARDS.MODULE] based on recent changes (e.g., public APIs, state transitions, or core logic).
4. **Sync**: Use `ref_manager.py --update` or `--create` to align the module documentation with the code.
    - If `--create` fails with `"Error: Parent tag [ARCH.module_name] not found."`, default to creating the missing module documentation (`[ARCH.module_name]`) with the file documentation (`[ARCH.module_name.FileName]`) inside, strictly following [ARCH.DOC_STANDARDS.MODULE].

## PROJECT INITIALIZATION [WORKFLOWS.PROJECT_INIT]
1. **Understand & Scope:** Ask the user for the project's high-level objective, target tech stack, and preferred architectural paradigm (e.g., MVC, Hexagonal, Data-Driven, ECS). If the user hasn't provided this information, STOP and ask for it.
2. **Analyze:** Evaluate the project requirements and map out the necessary technical foundations. Identify what core guardrails will be needed to keep the code clean and scalable.
3. **Propose Structure & Modules:** Draft a base directory tree for the project. Based on the directory tree, explicitly list the high-level Modules that will make up the system (e.g., `core`, `database`, `api`).
    - Ensure the Python script `ref_manager.py` is logically placed (e.g., in `utilities/` or `tools/`).
    - Ensure framework tracking files (`agent_rules.md`, `workflows.md`, `architecture.md`) are placed in their designated secure locations (e.g., `.forbidden/`).
4. **Propose Architecture:** Draft the initial text for `[ARCH.VISION]` (the "why" of the project) and define 3 to 5 strict rules for `[ARCH.RULES.CORE]` (the "how" of the project) based on the stack and paradigm discussed.
5. **HALT EXECUTION:** Present the proposed directory structure, the list of initial modules, `[ARCH.VISION]`, and `[ARCH.RULES.CORE]` to the user for approval. **YOU MUST STOP GENERATING TEXT HERE.** Do not proceed under any circumstances until the user explicitly replies with approval.
6. **Scaffold:** Execute shell commands to create the approved directories and move the boilerplate framework files to their final locations.
7. **Document Vision & Rules:** Use the `ref_manager.py` tool to inject the approved `[ARCH.VISION]` and `[ARCH.RULES.CORE]` into the newly placed `architecture.md`.
8. **Document Modules:** Use the `ref_manager.py` tool with `--create` to instantiate the base `[ARCH.DOC]` section if missing, and then inject the headers and brief descriptions for each of the approved modules (e.g., `[ARCH.DOC.module_name]`) into `architecture.md`.
9. **Git Protocol:** STOP and ask the user to commit changes. Suggest message: `chore: initialize project structure, agent framework, and base architecture`.