import os

def load_level_map(filepath):
    """
    Reads a text file and returns a list of strings representing the map.
    """
    if not os.path.exists(filepath):
        print(f"Level file not found: {filepath}")
        # Return a safe default empty map or raise error
        return [
            "....................",
            "....................",
            "....................",
            ".........P..........",
            "XXXXXXXXXXXXXXXXXXXX"
        ]

    with open(filepath, 'r') as f:
        # Read lines and strip newlines, but preserve spaces if any
        map_data = [line.rstrip('\r\n') for line in f.readlines()]

    # Filter out empty lines just in case
    map_data = [line for line in map_data if line]
    return map_data
