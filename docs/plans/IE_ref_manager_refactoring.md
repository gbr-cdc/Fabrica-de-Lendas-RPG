# Implementation Plan - Refactoring Reference Manager Creation Logic

The `ref_manager.py` utility will be refactored to simplify the document creation protocol. The core focus is to streamline the `create_section` function, removing redundant positioning logic and automated formatting, and delegating tag responsibility entirely to the agent.

## User Requirements
- `create_section` signature: `(content, file_path, position)`.
- Script should not handle tag creation/validation for the new content.
- Unify `after` and `in` positioning (use `after` for both).
- Remove automated `---` separators.

## Proposed Changes

### 1. Refactor `create_section` in `utilities/ref_manager.py`
- Change signature to `def create_section(content, file_path, after_tag=None):`.
- Logic:
    - If `after_tag` is provided:
        - Find range of `after_tag` using `find_tag_range`.
        - Insert `content` at the `end_idx` of the found range.
    - If `after_tag` is `None`:
        - Append `content` to the end of the file.
- Remove "smart spacing" (`---` logic).
- Return `(True, success_message)` or `(False, error_message)`.

### 2. Update CLI Interface
- Remove `--in` flag.
- Update `--create` (or `-c`) to handle content as the primary argument.
- Usage: `python utilities/ref_manager.py --create "Full Content with Tags" --after [EXISTING_TAG]`
- The `file_path` will be resolved from `after_tag`.
- If `--after` is not provided, the CLI should support a way to specify the target file (e.g., `--file path` or derived from a prefix).
- Actually, I'll allow `python utilities/ref_manager.py --create "Content" [TARGET_TAG_TO_FIND_FILE]`.
- To avoid breaking too much, I'll keep the logic where if no `--after` is provided, we use the first argument after `--create` to find the file and then append to it.

### 3. Verification Plan
- **Test Case 1: Create after a line tag.**
    - Insert a new line after an existing `[ARCH.FILE:...]` line.
- **Test Case 2: Create after a header tag (session).**
    - Insert a new session after an existing `[ARCH.MODULE:...]` session.
- **Test Case 3: Create at end of file.**
    - Append content without specifying `--after`.
- **Test Case 4: Verify NO automated `---` are added.**
