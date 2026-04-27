import sys
import re
import os

# Configuration: Tag prefixes mapped to their respective files
# This makes it easy to update the documentation structure.
PATH_MAPPING = {
    "ARCH.": "architecture.md",
    "GDD.": "docs/GDD/GDD.md",
    "WORKFLOWS.": "workflows.md",
}

def get_path_for_tag(tag):
    """
    Determines the correct file path for a given tag based on its prefix.
    """
    norm_tag = tag.strip('[]')
    for prefix, path in PATH_MAPPING.items():
        if norm_tag.startswith(prefix):
            return path
    return None

def find_tag_range(tag, lines):
    """
    Returns (start_idx, end_idx, is_header) for a given tag in the lines.
    Returns (None, None, None) if not found.
    """
    search_tag = tag.strip('[]')
    found_idx = -1
    
    # PASS 1: Look for the tag in a header
    for i, line in enumerate(lines):
        clean_line = line.strip()
        if search_tag in line and 'DEPENDS:' not in clean_line:
            if clean_line.startswith('#'):
                found_idx = i
                break
    
    if found_idx == -1:
        # PASS 2: Fallback to any line
        for i, line in enumerate(lines):
            if search_tag in line and 'DEPENDS:' not in line.strip():
                found_idx = i
                break

    if found_idx == -1:
        return None, None, None

    target_line = lines[found_idx].strip()
    header_match = re.match(r'^(#+)', target_line)
    
    if header_match:
        level = len(header_match.group(1))
        end_idx = found_idx + 1
        for i in range(found_idx + 1, len(lines)):
            next_line = lines[i].strip()
            if next_line.startswith('#'):
                next_header_match = re.match(r'^(#+)', next_line)
                next_level = len(next_header_match.group(1))
                if next_level <= level:
                    break
            end_idx = i + 1
        return found_idx, end_idx, True
    else:
        return found_idx, found_idx + 1, False

def extract_section(tag, file_path):
    """
    Extracts a specific section from a markdown file based on a [TAG].
    """
    if not os.path.isfile(file_path):
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    start, end, is_header = find_tag_range(tag, lines)
    if start is None:
        return None

    if is_header:
        section_text = "".join(lines[start:end]).strip()
        section_text = re.sub(r'\n+---+\s*$', '', section_text)
        return section_text.strip()
    else:
        return lines[start].strip()

def update_section(tag, new_content, file_path):
    """
    Updates a specific section or line in a markdown file based on a [TAG].
    """
    if not os.path.isfile(file_path):
        return False, f"Error: File {file_path} not found."

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    start, end, is_header = find_tag_range(tag, lines)
    if start is None:
        return False, f"Error: Tag [{tag}] not found in {file_path}."

    new_lines = lines[:start] + [new_content.strip() + '\n'] + lines[end:]

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    return True, f"Successfully updated tag [{tag}] in {file_path}."

def create_section(content, file_path, after_tag=None):
    """
    Creates a new section or line in a markdown file.
    """
    if not os.path.isfile(file_path):
        return False, f"Error: File {file_path} not found."

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    insert_idx = len(lines)
    
    if after_tag:
        start, end, is_header = find_tag_range(after_tag, lines)
        if start is not None:
            insert_idx = end
        else:
            return False, f"Error: Position tag [{after_tag}] not found."

    content_to_insert = content.strip() + '\n'
    
    new_lines = lines[:insert_idx] + [content_to_insert] + lines[insert_idx:]

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    return True, f"Successfully created content in {file_path}."

def resolve_tag(tag, resolved_tags=None, parent_file=None):
    """
    Recursively resolves a tag and all its [DEPENDS: ...] references.
    The file path is automatically determined by the tag's prefix.
    """
    if resolved_tags is None:
        resolved_tags = set()

    norm_tag = tag.strip('[]')
    
    # Determine which file this tag belongs to
    file_path = get_path_for_tag(norm_tag)
    if not file_path:
        return f"Error: No path mapping found for tag [{norm_tag}]."

    # Prevent duplicate extraction
    tag_id = f"{file_path}:{norm_tag}"
    if tag_id in resolved_tags:
        return ""
    
    resolved_tags.add(tag_id)
    
    # Check if the file exists
    if not os.path.isfile(file_path):
        return f"Error: Mapped file '{file_path}' for tag [{norm_tag}] not found."

    # Attempt to find the tag content
    content = extract_section(norm_tag, file_path)

    if not content:
        return f"Error: Tag [{norm_tag}] not found in {file_path}."

    # If the tag is in a session (line starts with #), mark all tags in the session as resolved
    if content.startswith('#'):
        for itag in re.findall(r'\[([A-Z0-9._]+)\]', content):
            if itag not in ("DEPENDS", "FROM"):
                ipath = get_path_for_tag(itag)
                if ipath:
                    resolved_tags.add(f"{ipath}:{itag}")

    # Look for dependency lines: [DEPENDS: tag1, tag2]
    dep_match = re.search(r'\[DEPENDS:\s*([^\]]+)\]', content)

    content = content.strip()
    if dep_match:
        deps = [d.strip() for d in dep_match.group(1).split(',')]
        dep_contents = []
        for dep in deps:
            # Recursively resolve each dependency
            dep_content = resolve_tag(dep, resolved_tags, parent_file=file_path)
            # If a dependency fails, fail fast and inform which tag triggered the failure
            if dep_content.startswith("Error:"):
                return f"Error: Failed to resolve dependency '{dep}' for tag [{norm_tag}]. {dep_content}"
            
            if dep_content.strip():
                dep_contents.append(dep_content)
        
        if dep_contents:
            valid_deps = [c for c in dep_contents if c.strip()]
            if valid_deps:
                content = "\n\n---\n\n".join(valid_deps) + "\n\n---\n\n" + content

    # CROSS-FILE TRACKING: If this section comes from a different file than its parent
    if parent_file and file_path != parent_file:
        origin_name = os.path.basename(file_path)
        if not content.startswith("> [FROM:"):
            content = f"> [FROM: {origin_name}]\n\n" + content
            
    return content

if __name__ == "__main__":
    # COMMAND LINE INTERFACE:
    # Usage: python ref_manager.py [TAG1] [TAG2] ...
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Extraction: python ref_manager.py [TAG1] [TAG2] ...")
        print("  Update:     python ref_manager.py --update [TAG] \"New Content\" [--from-file path]")
        print("  Creation:   python ref_manager.py --create [TAG_TO_FIND_FILE] \"New Content\" [--after TAG]")
        sys.exit(1)
    
    # Handle Update/Creation Modes
    if any(arg in sys.argv for arg in ("--update", "-u", "--create", "-c")):
        try:
            mode = "update" if any(arg in sys.argv for arg in ("--update", "-u")) else "create"
            flag = next(arg for arg in sys.argv if arg in ("--update", "-u", "--create", "-c"))
            flag_idx = sys.argv.index(flag)
            
            if len(sys.argv) < flag_idx + 2:
                print(f"Error: Missing tag for {mode}.")
                sys.exit(1)
            
            target_tag = sys.argv[flag_idx + 1]
            
            # Content source
            new_content = ""
            if "--from-file" in sys.argv:
                ff_idx = sys.argv.index("--from-file")
                if len(sys.argv) < ff_idx + 2:
                    print("Error: Missing file path for --from-file.")
                    sys.exit(1)
                ff_path = sys.argv[ff_idx + 1]
                if not os.path.isfile(ff_path):
                    print(f"Error: Content file '{ff_path}' not found.")
                    sys.exit(1)
                with open(ff_path, 'r', encoding='utf-8') as f:
                    new_content = f.read()
            else:
                if len(sys.argv) < flag_idx + 3:
                    print(f"Error: Missing content for {mode}.")
                    sys.exit(1)
                new_content = sys.argv[flag_idx + 2]
            
            if not target_tag.startswith('['):
                print(f"Error: '{target_tag}' is not a valid tag.")
                sys.exit(1)
            
            path = get_path_for_tag(target_tag)
            if not path:
                print(f"Error: No path mapping found for tag {target_tag}.")
                sys.exit(1)
            
            if mode == "update":
                success, message = update_section(target_tag, new_content, path)
            else:
                after_tag = None
                if "--after" in sys.argv:
                    after_tag = sys.argv[sys.argv.index("--after") + 1]
                
                success, message = create_section(new_content, path, after_tag)
            
            print(message)
            sys.exit(0 if success else 1)
        except (ValueError, IndexError):
            print("Error: Invalid arguments for update/creation.")
            sys.exit(1)

    tags = sys.argv[1:]
    
    # Validate that all arguments are tags
    for tag in tags:
        if not tag.startswith('['):
            print(f"Error: '{tag}' is not a valid tag. Tags must start with '['.")
            sys.exit(1)

    # Process and print each requested tag
    for i, tag in enumerate(tags):
        result = resolve_tag(tag)
        print(result)
        # Add a visual separator between different top-level tags
        if i < len(tags) - 1:
            print("\n" + "="*40 + "\n")
