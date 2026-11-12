# SPEAKERS - who can talk in dialogues.
#   name   - shown above the text box
#   sound  - "talk sound" played while the text is typed (assets/sfx/dialogue/)
#   voices - other sounds for the same speaker, chosen per line with "voice": "<name>" in the dialogue file
#   color  - name tag + placeholder figure colour
#
# Only the person you talk to is drawn (never the player). Its picture depends on the POSE of each line:
#   assets/img/dialogue/<speaker id>/<pose>.png      e.g. assets/img/dialogue/milo/neutral.png
# Without the picture a placeholder figure with the file name on it is drawn.

SOUND_DIR = "assets/sfx/dialogue"
IMAGE_DIR = "assets/img/dialogue"
DEFAULT_POSE = "neutral"

# music while talking (a name in MusicManager). PLACEHOLDER: there is no file yet -> the biome music keeps playing.
# Put a file at assets/music/dialogue/dialogue.mp3 and it is used automatically. A dialogue can pick its own: "music": "..."
DEFAULT_DIALOGUE_MUSIC = "dialogue"

SPEAKERS = {
    "player": {"name": "You", "sound": "talksound_player.wav", "color": (255, 230, 60)},
    "milo":   {"name": "Milo", "sound": "talksound_milo.wav", "voices": {"scary": "talksound_milo_scary.wav"},
               "color": (150, 120, 230)},
    "angler": {"name": "Angler", "sound": "talksound_NPC2.ogg", "color": (110, 150, 190)},
    "bramble": {"name": "Mayor Bramble", "sound": "talksound_NPC1.ogg", "color": (210, 170, 90)},
    "dot":    {"name": "Dot", "sound": "talksound_woman.ogg", "color": (230, 150, 120)},
    "wanderer": {"name": "Wanderer", "sound": "talksound_NPC1.ogg", "color": (160, 140, 110)},
    "sunny":  {"name": "Sunny", "sound": "talks_sound_girl2.ogg", "color": (255, 200, 80)},
    "gus":    {"name": "Gus", "sound": "talksound_NPC1.ogg", "color": (200, 120, 90)},
    "hal":    {"name": "Hal", "sound": "talksound_NPC2.ogg", "color": (110, 170, 200)},
    "antenna": {"name": "Antenna", "sound": "talksound_player.wav", "color": (150, 155, 170)},
    "radio":  {"name": "Radio", "sound": "talksound_NPC1.ogg", "color": (60, 60, 70)},   # the voice on channel nine
    "foreman": {"name": "Foreman", "sound": "talksound_NPC1.ogg", "color": (200, 160, 60)},
    "oliver": {"name": "Oliver", "sound": "talksound_NPC2.ogg", "color": (140, 180, 210)},
    "wren":   {"name": "Wren", "sound": "talksound_girl1.wav", "color": (190, 140, 230)},
    "look":   {"name": "...", "sound": "talksound_player.wav", "color": (120, 140, 130)},   # examining a place
    "gardener": {"name": "Gardener", "sound": "talksound_NPC2.ogg", "color": (120, 170, 110)},
    "whisper": {"name": "...", "sound": "talksound_player.wav", "color": (230, 230, 235)},   # the voice in the mushroom ring
    "lucky":  {"name": "Lucky", "sound": "talksound_NPC1.ogg", "color": (240, 80, 120)},
    "ferris": {"name": "Ferris", "sound": "talksound_NPC2.ogg", "color": (200, 165, 110)},   # the courier (shortcuts)
    "npc1":   {"name": "???", "sound": "talksound_NPC1.ogg", "color": (120, 200, 140)},
    "npc2":   {"name": "???", "sound": "talksound_NPC2.ogg", "color": (200, 140, 110)},
    "girl":   {"name": "???", "sound": "talksound_girl1.wav", "color": (240, 140, 190)},
    "narrator": {"name": "???", "color": (225, 225, 232)},     # (12.11) the voice in the endings (no talk sound)
}

# which dialogue an NPC on the map starts (NPC id from the prefab @npcs / the map -> file in game/dialogue/data/)
NPC_DIALOGUES = {
    "milo_test": "test_milo",
    "milo": "milo_village",          # Milo moves after bosses (game/story/milo.py) - one dialogue per place:
    "milo_rainbow": "milo_rainbow",
    "milo_candy": "milo_candy",
    "milo_separated": "milo_separated",
    "milo_garden_factory": "milo_garden_factory",
    "milo_garden_tundra": "milo_garden_tundra",
    "milo_core_entrance": "milo_core_entrance",
    "milo_island": "milo_island",    # the "second" Milo on the Village island (Pale World link, 4th wall)
    "angler": "angler",
    "bramble": "bramble",
    "dot": "dot",
    "wanderer": "wanderer",
    "sunny": "sunny",
    "gus": "gus",
    "hal": "hal",
    "foreman": "foreman",
    "foreman_core": "foreman_core",     # (11.11) in the Core after Milo's Peace Gun ending: gives the Old Note
    "milo_void": "milo_void",           # (11.11) Milo in the Void Shrine, a memory (takes the Old Note)
    "ice_fisher": "oliver",          # Oliver at the ice fishing camp (Tundra)
    "wren_village": "wren_village",  # Wren moves: Separated Village -> Garden camp -> near the Core way (story/wren.py)
    "wren": "wren",
    "wren_moved": "wren_moved",
    "milo_argument": "wren_argument",   # the overheard argument (starts by itself)
    "clue_stones": "clue_stones",       # the 3 places of Wren's investigation
    "clue_playground": "clue_playground",
    "clue_lab": "clue_lab",
    "gardener": "gardener",
    "lucky": "lucky",                   # the lunapark barker (wheel of fortune)
    "ferris": "ferris",                 # the courier in the Village: shortcuts (game/story/ferris.py)
    "pier_water": "pier_water",         # the end of the sunken pier (Gardener's quest)
    "ring_voice": "ring_voice",         # the whisper in the mushroom ring (riddle about the Pale Orb)
    "antenna_1": "antenna_1",        # Hal's three antennas (prefabs antenna_a / _b / _c)
    "antenna_2": "antenna_2",
    "antenna_3": "antenna_3",
}
