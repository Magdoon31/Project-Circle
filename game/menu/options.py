# OPTIONS (11.11): every setting of the game in one place - what it is called, its default, what values it can
# take. Read anywhere with get("name"); the Settings screen (settings_screen.py) changes them with set(); kept in
# game/text/settings.json (the old settings.txt with the two volumes is read once if there's no json yet).

import json
import os

FILE = "game/text/settings.json"
OLD_FILE = "game/text/settings.txt"

DEFAULTS = {
    # Audio (0-1)
    "master_volume": 1.0,
    "music_volume": 0.65,
    "sfx_volume": 0.65,
    "dialogue_volume": 0.8,
    # Video
    "fullscreen": True,                   # (changing it restarts the game)
    "flashes": True,                      # the white flash when a boss changes phase, a song's beat flashes
    "weather": True,                      # snow on the map, the blizzard in a fight
    "shadow_quality": "high",             # Night Bloom's darkness: how soft the lights' edges are
    "motion_blur": "off",                 # off / light / strong
    "blur_where": "both",                 # map / fight / both
    # Controls (pygame key codes; None = not set)
    "move_keys": "wasd",                  # wasd / ijkl / arrows
    "key_map": 109,                       # M
    "key_shop": 98,                       # B
    "key_shoot": None,
    "key_equip": None,
    "key_delete": None,
    "key_tab": None,
    # Gameplay
    "damage_numbers": False,
    "text_speed": "normal",               # slow / normal / fast / instant
    "autosave": "bosses",                 # off / bosses / often (bosses + every 5 min)
    "pause_on_phase": False,              # a boss's new phase pauses the fight
    "short_tooltips": False,              # the shop shows only the name, DPS and range
}
CHOICES = {
    "shadow_quality": ["low", "medium", "high"],
    "motion_blur": ["off", "light", "strong"],
    "blur_where": ["map", "fight", "both"],
    "move_keys": ["wasd", "ijkl", "arrows"],
    "text_speed": ["slow", "normal", "fast", "instant"],
    "autosave": ["off", "bosses", "often"],
}

_values = dict(DEFAULTS)


def get(name):
    return _values[name]


def set(name, value):
    _values[name] = value


def reset(names):
    for name in names:
        _values[name] = DEFAULTS[name]


def load():
    """From the file (anything missing or broken: its default)."""
    _values.update(DEFAULTS)
    data = from_old_blur(read_json() or read_old_file())
    for name, value in data.items():
        if name in DEFAULTS and valid(name, value):
            _values[name] = value


def save():
    try:
        with open(FILE, "w") as f:
            json.dump(_values, f, indent=4)
    except OSError:
        pass


def valid(name, value):
    default = DEFAULTS[name]
    if name in CHOICES:
        return value in CHOICES[name]
    if name.startswith("key_"):
        return value is None or isinstance(value, int)
    if isinstance(default, bool):
        return isinstance(value, bool)
    if isinstance(default, float):
        return isinstance(value, (int, float)) and 0.0 <= value <= 1.0
    return True


def read_json():
    try:
        with open(FILE) as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def from_old_blur(data):
    """Before, motion_blur was none / map / fight / both (always as strong as "strong" now)."""
    old = data.get("motion_blur")
    if old == "none":
        data["motion_blur"] = "off"
    elif old in CHOICES["blur_where"]:
        data["motion_blur"], data["blur_where"] = "strong", old
    return data


def read_old_file():
    """The settings.txt from before (two lines: music_volume, its value, sfx_volume, its value)."""
    if not os.path.exists(OLD_FILE):
        return {}
    try:
        with open(OLD_FILE) as f:
            lines = f.read().splitlines()
        return {"music_volume": float(lines[1]), "sfx_volume": float(lines[3])}
    except (OSError, IndexError, ValueError):
        return {}


# --- what other parts of the game ask -------------------------------------------------------------------------
def volume(kind):
    """The volume a sound really plays at: kind = music / sfx / dialogue, times the master volume."""
    return get("master_volume") * get(kind + "_volume")


def blur_strength(where):
    """How strong the motion blur is on the map / in a fight: off / light / strong."""
    return get("motion_blur") if get("blur_where") in (where, "both") else "off"
