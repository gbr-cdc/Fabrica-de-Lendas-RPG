# Plan: Documentation Creation via Tags

I will extend `utilities/ref_manager.py` to support creating new documentation entries (sessions and lines) using tags, providing a structured way to grow the documentation.

## Proposed Changes

### 1. New function: `create_section(tag, content, file_path, position=None)`
This function will handle the insertion of new content into a file.
- **Parameters:**
    - `tag`: The new tag to be created.
    - `content`: The text content for the new entry.
    - `file_path`: Target file (determined by prefix).
    - `position`: A dictionary defining where to insert:
        - `{"after": "[TAG]"}`: Inserts after the specified tag (or after the session if the tag is a header).
        - `{"in": "[TAG]"}`: Inserts at the end of the specified session.
        - `None`: Appends to the end of the file.

### 2. Logic for Insertion
- **After Tag**: 
    - If the target tag is a header, find the end of its section and insert.
    - If the target tag is a line, insert immediately after it.
- **In Session**:
    - Find the session header.
    - Find the end of that session (before the next header of same/higher level).
    - Insert before the next header.
- **Separators**: Automatically add `---` separators when creating new top-level sessions if needed.

### 3. CLI Expansion
New flags to support creation:
- `--create` or `-c`: Triggers creation mode.
- `--after [TAG]`: Specifies the tag to follow.
- `--in [TAG]`: Specifies the session to join.
- **Usage Examples:**
    - `python ref_manager.py --create "[ARCH.NEW]" "Content" --after "[ARCH.EXISTING]"`
    - `python ref_manager.py -c "[ARCH.FILE:new.py]" "- Description [TAG]" --in "[ARCH.MODULE.core]"`

## Implementation Steps

1.  **Refactor `extract_section`**: Extract the logic for finding section boundaries into a helper function (e.g., `find_section_range`) to be shared with `update_section` and `create_section`.
2.  **Implement `create_section`**: Handle the different positioning modes.
3.  **Update CLI**: Parse the new flags and coordinate with `create_section`.
4.  **Documentation**: Update `architecture.md` with the creation protocol.

## Definition of Done
1. `ref_manager.py` supports creating new entries.
2. CLI supports `--after` and `--in` positioning.
3. Successfully created a new module section in a test file.
4. Successfully added a new file line to an existing module section in a test file.
