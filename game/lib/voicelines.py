# VOICE LINES (11.11): recorded lines, one file per line - assets/sfx/voicelines/<speaker>/<line id>.mp3 / .wav /
# .ogg. A missing file is fine: the line is then only text (with the speaker's talk sound in dialogues).
#   dialogues: every NPC line has an "id" (given by tools/voicelines.py, listed in VOICELINES.md);
#              the speaker is the line's "who" (milo, wren, ...)
#   the shop:  speaker "shopkeeper", the ids from game/shop/lines.json
#   Milo's fight in the Core: speaker "milo", ids core_battle_<moment> (core_fight.py)

import os

import pygame

ROOT = os.path.join("assets", "sfx", "voicelines")
EXTENSIONS = (".mp3", ".wav", ".ogg")


def path_of(speaker, line_id):
    """The recording's file, or None if there is none yet."""
    for ext in EXTENSIONS:
        path = os.path.join(ROOT, speaker, line_id + ext)
        if os.path.exists(path):
            return path
    return None


def load(speaker, line_id):
    """The recording as a Sound, or None (no id, no file, or a file pygame can't read)."""
    path = path_of(speaker, line_id) if line_id else None
    if not path:
        return None
    try:
        return pygame.mixer.Sound(path)
    except pygame.error:
        return None
