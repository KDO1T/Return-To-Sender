import json
import os

SETTINGS_PATH = os.path.join(os.getcwd(), "settings.json")

DEFAULT_SETTINGS = {
    "resolution_index": 1,
    "fullscreen": False,
    "brightness": 50,
    "master_volume": 100,
    "music_volume": 80,
    "sfx_volume": 100,
    "controls": {
        "up": "W",
        "left": "A",
        "down": "S",
        "right": "D",
        "jump": "Space"
    }
}

def load_settings():
    if not os.path.exists(SETTINGS_PATH):
        return DEFAULT_SETTINGS.copy()

    try:
        with open(SETTINGS_PATH, "r") as file:
            settings = json.load(file)
    except (OSError, json.JSONDecodeError):
        return DEFAULT_SETTINGS.copy()

    loaded = DEFAULT_SETTINGS.copy()
    loaded.update(settings)
    loaded["controls"] = DEFAULT_SETTINGS["controls"].copy()
    loaded["controls"].update(settings.get("controls", {}))
    return loaded

def save_settings(settings):
    with open(SETTINGS_PATH, "w") as file:
        json.dump(settings, file, indent=4)
