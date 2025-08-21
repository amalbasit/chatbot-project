import json
from typing import Any

from constants import JSON_FILE

def load_data() -> dict[str, Any]:
    try:
        with open(JSON_FILE, 'r') as file:
            return json.load(file)
    except:
        return {}

def save_data(data: dict) -> None:
    with open(JSON_FILE, 'w') as file:
        json.dump(data, file, indent=4)