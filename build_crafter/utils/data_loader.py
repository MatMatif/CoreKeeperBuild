# utils/data_loader.py
import json
import os

def load_data_from_file(filepath):
    """Charge une liste de dictionnaires depuis un fichier JSON."""
    data = []
    print(f"Attempting to load data from: {filepath}") # <<< Print 1
    if not os.path.exists(filepath):
        print(f"Error: Data file '{filepath}' does not exist.") # <<< Print 2
        return data
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list):
                print(f"Error: Content of '{filepath}' is not a valid JSON list. Type found: {type(data)}") # <<< Print 3
                return []
        print(f"Successfully loaded {len(data)} entries from {filepath}") # <<< Print 4
        if data: # Check if list is not empty
            print(f"Type of first element from {filepath}: {type(data[0])}") # <<< Print 5
            if isinstance(data[0], dict):
                 print(f"Keys of first dictionary element: {list(data[0].keys())}") # <<< Print 6 (show keys)
        return data
    except json.JSONDecodeError:
        print(f"Error: JSON file '{filepath}' is malformed.") # <<< Print 7
        return []
    except Exception as e:
        print(f"Unexpected error loading {filepath}: {e}") # <<< Print 8
        return []