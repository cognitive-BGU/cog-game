import os
import json
import datetime

BASE_DIR = "Patient Data"

def save_to_json(data, patient_id, filename):
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)

    patient_dir = os.path.join(BASE_DIR, patient_id)
    if not os.path.exists(patient_dir):
        os.makedirs(patient_dir)

    json_name = os.path.join(patient_dir, filename)

    if os.path.exists(json_name):
        with open(json_name, 'r') as f:
            existing_data = json.load(f)
    else:
        existing_data = {}

    if "stages" not in existing_data:
        existing_data["stages"] = {}

    for key, value in data.items():
        if key == "config" or key == "task_start_time" or key == "end game":
            if key in existing_data:
                if isinstance(existing_data[key], list):
                    existing_data[key].append(value)
                else:
                    existing_data[key] = [existing_data[key], value]
            else:
                existing_data[key] = value
        else:
            if key in existing_data["stages"]:
                if isinstance(existing_data["stages"][key], list):
                    existing_data["stages"][key].append(value)
                else:
                    existing_data["stages"][key] = [existing_data["stages"][key], value]
            else:
                existing_data["stages"][key] = [value]

    # שליטה בסדר המפתחות בעת כתיבת JSON
    ordered_data = {
        "config": existing_data.get("config", {}),
        "task_start_time": existing_data.get("task_start_time", None),
        "stages": existing_data.get("stages", {}),
        "end game": existing_data.get("end game", None)
    }

    with open(json_name, 'w') as f:
        json.dump(ordered_data, f, indent=4)



'''
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

'''