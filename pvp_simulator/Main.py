

import sys
import os

# Add project root to sys.path to allow absolute imports from 'entities', 'core', etc.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Simulator import mono, multy


def main():
    if len(sys.argv) != 4:
        print("Usage: python BattleManager.py <mono|multi> <character1_id> <character2_id>")
        return
    mode = sys.argv[1]
    char1_id = sys.argv[2]
    char2_id = sys.argv[3]
    if mode == "mono":
        mono(char1_id, char2_id)
    elif mode == "multi":
        multy(char1_id, char2_id)
    else:
        print("Invalid mode. Use 'mono' or 'multi'")

if __name__ == "__main__":
    main()