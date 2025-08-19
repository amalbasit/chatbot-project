import json
from typing import Any

from api.constants import JSON_FILE

# FIX METHOD
def load_data() -> dict[str, Any]:
    try:
        with open(JSON_FILE, 'r') as file:
            return json.load(file)
    except:
        return {}

# FIX METHOD
def save_data(data: dict) -> None:
    with open(JSON_FILE, 'w') as file:
        json.dump(data, file, indent=4)