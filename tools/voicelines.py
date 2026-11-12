# VOICE LINES (11.11): gives every NPC line in the dialogues an "id" (the lines that have one keep it) and writes
# VOICELINES.md - every line to record, by speaker, with the file it goes to:
#   assets/sfx/voicelines/<speaker>/<id>.mp3 (or .wav / .ogg)
# Run it again after writing new dialogue lines:  python tools/voicelines.py   (from the game's folder)
#
# Not given ids: the player, narration ("look" - examining a place, "antenna" - Hal's antennas) and the test talk.
# The same line said by the same speaker in several places gets ONE id (one recording for all of them).
# Also listed: the shopkeeper and the buyer (game/shop/lines.json) and Milo in his fight in the Core (core_fight.py).

import ast
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game.dialogue.speakers import SPEAKERS                                       # noqa: E402

DATA_DIR = "game/dialogue/data"
SHOP_LINES = "game/shop/lines.json"
CORE_FIGHT = "game/combat/core_fight.py"
CORE_VOICE_ID = "core_battle_{}"                 # the same as VOICE_ID in core_fight.py
OUT = "VOICELINES.md"
VOICE_ROOT = "assets/sfx/voicelines"
NOT_VOICED = {"player", "look", "antenna"}
SKIPPED_FILES = {"test_milo"}
FIRST_SPEAKERS = ["milo", "shopkeeper", "buyer"]   # listed first, the rest by name
EXTRA_NAMES = {"shopkeeper": "Shopkeeper", "buyer": "Buyer (the Sell page)"}


# --- the dialogue files -------------------------------------------------------------------------------------------
def dialogue_files():
    """[(name, data)] in name order, without the test talk."""
    files = []
    for path in sorted(glob.glob(os.path.join(DATA_DIR, "*.json"))):
        name = os.path.splitext(os.path.basename(path))[0]
        if name not in SKIPPED_FILES:
            with open(path, encoding="utf-8") as f:
                files.append((name, json.load(f)))
    return files


def voiced_lines(data):
    """[(node name, line)] of the lines an NPC says, in the file's order."""
    return [(node_name, line) for node_name, node in data["nodes"].items() for line in node.get("lines", [])
            if line.get("who", "player") not in NOT_VOICED]


def give_ids(files):
    """Lines without an id get one: the id of the same line said before, or <file>_<number>. -> changed files"""
    known = {(line["who"], line["text"]): line["id"]
             for _, data in files for _, line in voiced_lines(data) if "id" in line}
    changed = set()
    for name, data in files:
        number = highest_number(name, data)
        for _, line in voiced_lines(data):
            if "id" in line:
                continue
            key = (line["who"], line["text"])
            if key not in known:
                number += 1
                known[key] = f"{name}_{number:02d}"
            put_id_first(line, known[key])
            changed.add(name)
    return changed


def highest_number(name, data):
    pattern = re.compile(re.escape(name) + r"_(\d+)$")
    numbers = [int(m.group(1)) for _, line in voiced_lines(data) if (m := pattern.match(line.get("id", "")))]
    return max(numbers, default=0)


def put_id_first(line, line_id):
    rest = dict(line)
    line.clear()
    line["id"] = line_id
    line.update(rest)


def save_dialogue(name, data):
    text = json.dumps(data, indent=4, ensure_ascii=False).replace("\n", "\r\n") + "\r\n"
    with open(os.path.join(DATA_DIR, name + ".json"), "w", encoding="utf-8", newline="") as f:
        f.write(text)


# --- everything to record, by speaker -----------------------------------------------------------------------------
def all_lines(files):
    """speaker -> {id: {"text", "notes", "where": [places]}}"""
    lines = {}
    for name, data in files:
        for node_name, line in voiced_lines(data):
            add(lines, line["who"], line["id"], line["text"], notes_of(line), f"{name} → {node_name}")
    for line in shop_lines():
        speaker = "buyer" if line["kind"].startswith("sell_") else "shopkeeper"
        add(lines, speaker, line["id"], line["text"], shop_notes(line), f"shop: {line['kind']}")
    for key, text in core_fight_lines().items():
        add(lines, "milo", CORE_VOICE_ID.format(key), text, [], f"Core fight ({key})")
    return lines


def add(lines, speaker, line_id, text, notes, where):
    entry = lines.setdefault(speaker, {}).setdefault(line_id, {"text": text, "notes": notes, "where": []})
    entry["where"].append(where)


def notes_of(line):
    notes = []
    if line.get("voice"):
        notes.append(f"{line['voice']} voice")
    if line.get("horror"):
        notes.append("horror (black screen)")
    if line.get("speed"):
        notes.append(f"speed {line['speed']}")
    return notes


def shop_notes(line):
    return [f"mood: {', '.join(line['moods'])}"] if line.get("moods") else []


def shop_lines():
    with open(SHOP_LINES, encoding="utf-8") as f:
        return json.load(f)["lines"]


def core_fight_lines():
    """LINES from core_fight.py, read without running the game."""
    with open(CORE_FIGHT, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "LINES" for t in node.targets):
            return ast.literal_eval(node.value)
    return {}


# --- VOICELINES.md --------------------------------------------------------------------------------------------
def write_list(lines):
    speakers = speaker_order(lines)
    rows = header(lines, speakers)
    for speaker in speakers:
        rows += section(speaker, lines[speaker])
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(rows) + "\r\n")


def speaker_order(lines):
    first = [s for s in FIRST_SPEAKERS if s in lines]
    return first + sorted(s for s in lines if s not in first)


def display_name(speaker):
    name = EXTRA_NAMES.get(speaker) or SPEAKERS.get(speaker, {}).get("name", speaker)
    return name if name not in ("...", "???") else f"{speaker} ({name})"


def header(lines, speakers):
    total = sum(len(entries) for entries in lines.values())
    rows = ["# Voice lines", "",
            "Every line an NPC says, to record. A file goes to `assets/sfx/voicelines/<folder>/<ID>.mp3`",
            "(or `.wav` / `.ogg`). A missing file is fine - the line is only text (with the talk sound).",
            "Without the player, the answers and narration. Made by `python tools/voicelines.py` - run it again",
            "after writing new lines (new lines get IDs, old ones keep theirs).", "",
            "**×N** = the same line is said in N places - one recording is used for all of them.", "",
            f"Total: {total} lines.", "", "| Who | Folder | Lines |", "|---|---|---|"]
    rows += [f"| {display_name(s)} | `{VOICE_ROOT}/{s}/` | {len(lines[s])} |" for s in speakers]
    return rows + [""]


def section(speaker, entries):
    rows = ["", f"## {display_name(speaker)} — `{VOICE_ROOT}/{speaker}/`", "",
            "| ID | Line | Where | Notes |", "|---|---|---|---|"]
    for line_id, entry in entries.items():
        where = entry["where"]
        repeat = f"**×{len(where)}** " if len(where) > 1 else ""
        rows.append(f"| {line_id} | {cell(entry['text'])} | {repeat}{cell('; '.join(where))} | "
                    f"{cell(', '.join(entry['notes']))} |")
    return rows


def cell(text):
    return text.replace("\n", " ").replace("|", "\\|")


def main():
    files = dialogue_files()
    changed = give_ids(files)
    for name, data in files:
        if name in changed:
            save_dialogue(name, data)
    lines = all_lines(files)
    write_list(lines)
    print(f"ids given in {len(changed)} files; {sum(map(len, lines.values()))} lines listed in {OUT}")


if __name__ == "__main__":
    main()
