import os
import json

import datetime

json_name = f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"

def save_to_json(data):
    if os.path.exists(json_name):
        with open(json_name, 'r') as f:
            existing_data = json.load(f)
    else:
        existing_data = {}

    existing_data.update(data)
    with open(json_name, 'w') as f:
        json.dump(existing_data, f)
