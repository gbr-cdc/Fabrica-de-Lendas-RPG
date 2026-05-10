# Implementation Plan - Ref Manager Depth Resolution [PLAN]

The objective is to modify `utilities/ref_manager.py` to allow users to specify a maximum depth for recursive dependency resolution. By default, the tool will now use a depth of 1 (immediate dependencies only).

## Proposed Changes

### 1. Update `resolve_tag` Function
Modify the `resolve_tag` function to track current recursion depth and compare it against a maximum allowed depth.

```python
def resolve_tag(tag, resolved_tags=None, parent_file=None, current_depth=0, max_depth=1):
    # ...
    # 1. Track depth
    # 2. Only process [DEPENDS:] if current_depth < max_depth
    # 3. Pass current_depth + 1 to recursive calls
```

### 2. Update CLI Parsing
Modify the `if __name__ == "__main__":` block to detect and parse `--depth` or `-D` arguments.

- Extract the depth value if provided.
- Remove the depth arguments from the list of tags to process.
- Pass the depth value to `resolve_tag`.

### 3. Documentation Update
Update the usage printout to include the new depth option.

## Verification Plan

### Automated Tests
1. Create a temporary markdown file with 3 levels of dependencies: `A -> B -> C`.
2. Run `ref_manager.py [A] --depth 0`: Should only return content of `A`.
3. Run `ref_manager.py [A] --depth 1`: Should return content of `B` and `A`. (Default behavior)
4. Run `ref_manager.py [A] --depth 2`: Should return content of `C`, `B`, and `A`.

### Manual Verification
- Test with existing tags in `architecture.md` to ensure default behavior (depth 1) is sane.
- Test with `-D 99` to simulate previous "infinite" behavior.
