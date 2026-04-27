import sys
import re
import os

# Configuration: Tag prefixes mapped to their respective files
# This makes it easy to update the documentation structure.
PATH_MAPPING = {
    "ARCH.": "architecture.md",
    "GDD.": "docs/GDD/GDD.md",
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

def extract_section(tag, file_path):
    """
    Extracts a specific section from a markdown file based on a [TAG].
    """
    if not os.path.isfile(file_path):
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    search_tag = tag.strip('[]')
    found_idx = -1
    
    # PASS 1: Look for the tag in a header or explicit bracketed usage.
    for i, line in enumerate(lines):
        clean_line = line.strip()
        # Skip lines that are just declaring dependencies
        if search_tag in line and 'DEPENDS:' not in clean_line:
            if clean_line.startswith('#'):
                found_idx = i
                break
    
    # PASS 2: Fallback to any line containing the tag if no header was found.
    if found_idx == -1:
        for i, line in enumerate(lines):
            if search_tag in line and 'DEPENDS:' not in line.strip():
                found_idx = i
                break

    if found_idx == -1:
        return None

    target_line = lines[found_idx].strip()
    header_match = re.match(r'^(#+)', target_line)
    if header_match:
        level = len(header_match.group(1))
        content = [lines[found_idx]]
        for i in range(found_idx + 1, len(lines)):
            next_line = lines[i].strip()
            if next_line.startswith('#'):
                next_header_match = re.match(r'^(#+)', next_line)
                next_level = len(next_header_match.group(1))
                if next_level <= level:
                    break
            content.append(lines[i])
        
        section_text = "".join(content).strip()
        section_text = re.sub(r'\n+---+\s*$', '', section_text)
        return section_text.strip()
    else:
        return target_line

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
        print("Usage: python ref_manager.py [TAG1] [TAG2] ...")
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
