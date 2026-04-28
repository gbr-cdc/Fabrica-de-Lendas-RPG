# Centralizing Documentation & Improving Ref Manager

This plan aims to make `ref_manager.py` smarter about where it places new content when intermediate documentation is missing.

## Proposed Change

### Utilities
#### [MODIFY] [ref_manager.py](file:///home/alice/Repositorios/RPG/utilities/ref_manager.py)
- Update `create_section` to implement **Fail-Fast Hierarchy Validation**:
    - When creating a child tag (e.g., `[ARCH.mod.file]`), the tool must verify that the parent tag (`[ARCH.mod]`) exists in the file.
    - If the parent is missing, return an error: `"Error: Parent tag [ARCH.mod] not found. Please create the parent documentation before adding children."`
    - Module-level tags (e.g., `[ARCH.mod]`) will continue to use the prefix (`ARCH.`) to find their place after existing modules.