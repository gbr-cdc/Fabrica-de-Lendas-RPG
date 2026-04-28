# WORKFLOWS [WORKFLOWS.GLOBAL]

## FEATURE PLANNING [WORKFLOWS.FEATURE_PLANNING]
1. **Check Architectural Rules:** Fetch [ARCH.RULES]
2. **Understand:** Problem statement and User's desired outcome/technical preference. Challange user directions if you have better solutions to the problem.
3. **Analyze:** Validate against ARCH.RULES and common gaming design patterns.
4. **Propose:** Create `docs/plans/[task].md`.
5. **Iterate:** Wait for the user to approve the plan.
6. **Check Mission Format:** Fetch [ARCH.DOC_STANDARDS.MISSION]
7. **Mission:** Translate the approved Plan into a mission. Create new mission with tag [MISSION.ACTIVE.(mission_name)].

## ARCHITECTURAL ANALYSIS [WORKFLOWS.ARCH_ANALYSIS]
1. **Receive:** Fetch [ARCH.(...)] tags user wants to discuss. If you didn't received any, aks for tags.
2. **Discuss**: Discuss architectural problems and needed changes based on the information received.
3. **Apply**: Updated, create or delete [ARCH.(...)] tags according with desired changes.
4. **Impact Analysis**: Determine if existing code needs a migration mission.

## INDEPENDENT EXECUTION [WORKFLOWS.INDEPENDENT_EXECUTION]
1. **Understand:** Problem statement and user's desired outcome/technical preference. Challange user directions if you have better solutions to the problem.
2. **Propose:** Create/edit `docs/plans/[IE_task_description].md` with a execution plan.
3. **Iterate:** Wait for User approval.
4. **Implement:** Execute the plan.
5. **Test:** Test if implementation have correctly achieved the desired outcome.
6. **Document:** Go to [WORKFLOWS.DOC_MODULES] workflow.

## FLASH EXECUTION [WORKFLOWS.FLASH_EXECUTION]
1. **Understand:** Undestand the objective of the execution and what needs to be done.
2. **Execute:** Follow the instructions given by the user.
3. **Verify:** Check if all objectives were achieved and if implementations done works as intended.

## OPERATIONAL CHANGES [WORKFLOWS.OPERATIONAL_CHANGES]
1. **Receive:** Fetch [WORKFLOWS.GLOBAL]
2. **Identify**: Pinpoint specific workflow and steps that caused confusion or inefficiency, or new elements that need to be implemented.
3. **Propose**: Propose the updates tha should be applied to specifc [WORKFLOWS.(...)] or [AGENT.(...)] tags.
4. **Iterate**: Wait for user approval.
5. **Update**: Applay updates.
6. **Report & Sync**:
    - Generate a reunion report in `docs/reports/reunion_YYYY-MM-DD_HH:MM.md` summarizing: problems identified, changes made, files modified.
    - Ask USER to commit changes and suggest message: `reunion: description_of_change`.

## MISSION EXECUTION [WORKFLOWS.MISSION_EXECUTION]
1. **Receive:** Fetch a [MISSION.ACITVE.(...)] tag. If you didn't received one, ask for one. If mission have no steps to complete, stop and inform the problem.
2. **State Check:** Check last `State: (...)` notes in previous completed steps if available for context.
3. **Phase Execution:** Select a project phase to execute.

### Phase execution
- **TDD Phases:**
    1. **RED (Test Objective)**: Pick a [RED] step -> Create/Update Integration/Scenario Test based on the detailed objective -> `pytest` (Must Fail).
    2. **GREEN (Implementation)**: Pick the corresponding [GREEN] step -> Implement approved logic -> `pytest` (Must Pass).
- **Non-TDD Phases**:
    - **BLUE (Implementation)**: Pick the corresponding [BLUE] step -> Implement approved logic -> pytest (Regression: Full suite must pass)
- **PhaseComplete ([RED/GREEN] or [BLUE])**:
    1. Update [MISSION.(...)] with:
        - Mark completed steps [ ] -> [x]
        - Append `| State: description of step results with all information summarized for the next step` to the [GREEN] or [BLUE] step.
            - **Source of truth**: Consider this state note is all next agent will have from previous context, so make sure it is descriptive and concise.
    2. **Context Cleanup**: After completing a [RED/GREEN] or [BLUE] phase, suggest a commit message and call for a new session for context reset.

### Mission Completion
1. All tests MUST pass.
2. 100% test coverage for the modified modules (`pytest --cov`).
3. **DoD Check**: Explicitly verify each item in the mission's "Definition of Done".
4. **Archive**: Fetch [ARCH.DOC_STANDARDS.MISSION.ARCHIVED]. Delete [MISSION.(...)]. Create [MISSION.ARCHIVE.(...)] following [ARCH.DOC_STANDARDS.MISSION.ARCHIVED].
5. **Document**: Go to [WORKFLOWS.DOC_MODULES] workflow.

## DOCUMENT MODULES [WORKFLOWS.DOC_MODULES]
1. **Get template**: Fetch [ARCH.DOC_STANDARDS.MODULE] for documentation template.
2. **Filter**: Identify modified implementation files. For completed missions, check all files referenced in completed steps. Exclude `tests/`, root files, and `docs/`. 
3. **Identify**: Use [AGENT.REF_MANAGER.CONVENTIONS] to create the tags for modified files documentations. 
4. **Evaluate**: Fetch each file documentation. Check for missing elements or discrepancies vs [ARCH.DOC_STANDARDS.MODULE] based on recent changes (public APIs, state transitions, or core logic).
5. **Sync**: Use `ref_manager.py --update` or `--create` to align the module documentation with the code.
    - If `--create` fails with `"Error: Parent tag [ARCH.module_name] not found."`, default to creating the missing module documentation (`[ARCH.module_name]`) with file documentation (`[ARCH.module_name.FileName]) inside, following [ARCH.DOC_STANDARDS.MODULE].
