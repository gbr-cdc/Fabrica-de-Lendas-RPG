# Ref Manager Improvement Plan

Improve `utilities/ref_manager.py` to handle hierarchical documentation more robustly and provide better feedback when parent sections are missing.

## User Review Required

> [!IMPORTANT]
> The new "Fail-Fast" logic will prevent creating a child tag (e.g., `[ARCH.mod.file]`) if its parent (`[ARCH.mod]`) does not exist in the target file. This ensures documentation remains structured and discoverable.

## Proposed Changes

### Utilities

#### [MODIFY] [ref_manager.py](file:///home/alice/Repositorios/RPG/utilities/ref_manager.py)
- **Implement Existence & Hierarchy Logic**:
    - Extract all current tags from the file.
    - **Existence Check**: If `target_tag` exists, return error: `"Error: Tag [TAG] already exists."`
    - **Hierarchy Search**:
        - Split the tag into components (e.g., `[A.B.C]` -> prefix `A.B`).
        - Search for the **last** tag `m` such that `m == prefix` OR `m.startswith(prefix + ".")`.
    - **Fail-Fast Validation**:
        - If **no match** is found:
            - If the tag has 3+ components (e.g., `[A.B.C]`), return error: `"Error: Parent tag [A.B] not found."`
            - If it has 2 components (e.g., `[A.B]`), return error: `"Error: File identifier [A] not found. The target file is missing its root documentation tag."`
        - If **match** is found:
            - Set `insert_idx` to the end of that tag's section (using `find_tag_range`).

### Tests

#### [MODIFY] [test_ref_manager.py](file:///home/alice/Repositorios/RPG/tests/utilities/test_ref_manager.py)
- Add `test_create_section_fail_fast`: Verify that creating a child without a parent fails.
- Add `test_smart_placement_no_siblings`: Verify that creating the first child of a parent places it immediately after the parent.
- Add `test_smart_placement_deep_hierarchy`: Verify placement in a 3+ level hierarchy.

## Verification Plan

### Automated Tests
- Run `pytest tests/utilities/test_ref_manager.py` to ensure all existing and new tests pass.

### Manual Verification
- Manually run `python3 utilities/ref_manager.py --create "[TESTE.NEW_PARENT.CHILD]" "Content"` on a file where `[TESTE.NEW_PARENT]` is missing to confirm the error message.
- Manually run the same command after creating `[TESTE.NEW_PARENT]` to confirm successful placement.
