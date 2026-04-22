# Context: [DEBUG]
Resolve bugs and system failures.

## Workflow
1. **Reproduce**: Create a minimal test case or use `pytest` to confirm the failure.
2. **Analyze**: Isolate the failure point using logs, debugger tools, or print statements.
3. **Hypothesize**: Present the findings and the proposed fix to the USER.
4. **Fix**: Minor -> Direct. Complex -> Transition to `[PLANNING]`.
5. **Verify**: Test fix and check for regressions.

## Constraints
- **Minimalism**: Do not modify working code outside the bug's immediate scope.
- **TDD**: A failing test must precede the fix.
