import json
import os

def load_level_map(filepath):
    """
    Reads a file.
    If .txt, parses as single layer (legacy).
    If .json, parses as multi-layer.
    Returns a dict with layers: {'bg': [], 'main': [], 'fg': []}
    """
    if not os.path.exists(filepath):
        print(f"Level file not found: {filepath}")
        return {'main': []} # Empty default

    if filepath.endswith('.txt'):
        # Legacy support
        with open(filepath, 'r') as f:
            lines = [line.rstrip('\r\n') for line in f.readlines()]
            lines = [line for line in lines if line]
            return {'main': lines, 'bg': [], 'fg': []}

    elif filepath.endswith('.json'):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                return data # Expected {'bg': [], 'main': [], 'fg': []}
        except json.JSONDecodeError:
            print(f"Error decoding JSON {filepath}")
            return {'main': []}

    return {'main': []}

def save_level_map(filepath, data):
    """
    Saves level data to JSON.
    data format: {'bg': [], 'main': [], 'fg': []}
    """
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Saved level to {filepath}")
