# Plan: Add Update Capabilities to Reference Manager

I will extend `utilities/ref_manager.py` to support updating documentation sections based on tags.

## Proposed Changes

### 1. New function: `update_section(tag, new_content)`
This function will:
- Identify the target file using `get_path_for_tag`.
- Read the entire file.
- Locate the tagged section (header-based session or individual line).
- Replace the identified range with `new_content`.
- Write the modified content back to the file.

### 2. Enhanced CLI
The CLI will be updated to handle an `--update` (or `-u`) flag.
- **Usage:** `python utilities/ref_manager.py --update [TAG] "New Content"`
- It will also support reading from a file if the content is too large: `python utilities/ref_manager.py --update [TAG] --from-file path/to/content.txt` (Optional, but good for robustness).
- Actually, for now, I'll implement the simple string argument as requested.

## Implementation Details

- **Session Updates:** If the tag is found in a markdown header, the entire section (until the next header of equal or higher level) will be replaced.
- **Line Updates:** If the tag is found in a regular line, only that line will be replaced.
- **Safety:** It will perform a basic check to ensure the file exists and the tag is found before attempting to write.

## Definition of Done
1. `ref_manager.py` has an `update_section` function.
2. CLI supports `--update [TAG] content`.
3. Test updating a session tag in a dummy file.
4. Test updating a line tag in a dummy file.
