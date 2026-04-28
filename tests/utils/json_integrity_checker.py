import json
from typing import List

def get_json_keys(filepath: str) -> List[str]:
    """
    Automatically reads the top-level keys from a JSON file.
    Used for providing a list of valid IDs to the test runner dynamically.
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    if isinstance(data, dict):
        return list(data.keys())
    return []
