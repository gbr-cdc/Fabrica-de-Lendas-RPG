import sys
import re
import os

def extract_reference(tag, file_path='architecture.md'):
    if not os.path.exists(file_path):
        return f"Error: {file_path} not found."

    with open(file_path, 'r') as f:
        lines = f.readlines()

    found_idx = -1
    for i, line in enumerate(lines):
        if tag in line:
            found_idx = i
            break

    if found_idx == -1:
        return f"Error: Tag {tag} not found in {file_path}."

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
        # Just a line (like ARCH.X.X)
        return target_line

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ref_extractor.py [TAG] [FILE_PATH]")
        sys.exit(1)
    
    tag = sys.argv[1]
    file_path = sys.argv[2] if len(sys.argv) > 2 else 'architecture.md'
    
    print(extract_reference(tag, file_path))
