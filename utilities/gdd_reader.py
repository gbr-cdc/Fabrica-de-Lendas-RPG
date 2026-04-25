import sys
import re
import os

def extract_section(tag, file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Clean tag for searching (remove brackets if present)
    search_tag = tag.strip('[]')
    
    found_idx = -1
    # First pass: look for header or definition (not in a DEPENDS line)
    for i, line in enumerate(lines):
        clean_line = line.strip()
        if search_tag in line and not clean_line.startswith('[DEPENDS:'):
            # Prefer headers or lines where tag is at the end or in brackets
            if clean_line.startswith('#') or f'[{search_tag}]' in line:
                found_idx = i
                break
    
    # Second pass: if not found, take any non-DEPENDS line
    if found_idx == -1:
        for i, line in enumerate(lines):
            if search_tag in line and not line.strip().startswith('[DEPENDS:'):
                found_idx = i
                break

    if found_idx == -1:
        return None

    target_line = lines[found_idx].strip()
    
    # Check if it's a header
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
        return "".join(content).strip()
    else:
        # Just a line
        return target_line

def resolve_gdd(tag, gdd_dir='docs/GDD', resolved_tags=None):
    if resolved_tags is None:
        resolved_tags = set()

    norm_tag = tag.strip('[]')
    if norm_tag in resolved_tags:
        return ""
    
    resolved_tags.add(norm_tag)
    
    content = ""
    found = False
    
    # Search in all .md files
    for root, dirs, files in os.walk(gdd_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                section = extract_section(norm_tag, file_path)
                if section:
                    content = section
                    found = True
                    break
        if found: break
            
    if not found:
        # Robustness for shorthands
        alt_tags = []
        if 'GDD.RES.' in norm_tag:
            alt_tags.append(norm_tag.replace('GDD.RES.', 'GDD.RESOURCES.'))
            alt_tags.append(norm_tag.replace('GDD.RES.', 'GDD.STATUS.'))
        if 'GDD.CORE.COMBAT' in norm_tag:
            alt_tags.append(norm_tag.replace('GDD.CORE.COMBAT', 'GDD.COMBAT'))
        if 'GDD.COMBAT' in norm_tag and 'GDD.CORE' not in norm_tag:
             alt_tags.append(norm_tag.replace('GDD.COMBAT', 'GDD.CORE.COMBAT'))
        
        for alt in alt_tags:
            for root, dirs, files in os.walk(gdd_dir):
                for file in files:
                    if file.endswith('.md'):
                        file_path = os.path.join(root, file)
                        section = extract_section(alt, file_path)
                        if section:
                            content = section
                            found = True
                            break
                if found: break
            if found: break

    if not found:
        return f"Error: Tag {tag} not found in {gdd_dir}."

    # Resolve dependencies
    dep_match = re.search(r'\[DEPENDS:\s*([^\]]+)\]', content)
    if dep_match:
        deps_str = dep_match.group(1)
        deps = [d.strip() for d in deps_str.split(',')]
        
        dep_contents = []
        for dep in deps:
            dep_content = resolve_gdd(dep, gdd_dir, resolved_tags)
            if dep_content and not dep_content.startswith("Error:"):
                dep_contents.append(dep_content)
        
        if dep_contents:
            content = "\n\n---\n\n".join(dep_contents) + "\n\n---\n\n" + content
            
    return content

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gdd_reader.py [TAG]")
        sys.exit(1)
    
    tag = sys.argv[1]
    gdd_dir = 'docs/GDD'
    
    print(resolve_gdd(tag, gdd_dir))
