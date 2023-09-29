import os
import json


def save_to_json(data, filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            existing_data = json.load(f)
    else:
        existing_data = {}

    existing_data.update(data)
    with open(filename, 'w') as f:
        json.dump(existing_data, f)
