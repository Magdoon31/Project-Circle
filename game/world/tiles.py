# TILE TYPES of the world map.
# A tile = terrain char (this table, the SAME in every biome) + biome (stored per tile in the map).
# "." is always grass - only its sprite (for now: color) depends on the biome.
#   name      - readable name
#   solid     - True = player can't walk through
#   encounter - random fights can start on this tile
# Colors: DEFAULT_COLORS + per-biome overrides in BIOME_COLORS -> use tile_color(char, biome).

TILES = {
    ".": {"name": "grass",       "solid": False, "encounter": True},
    ",": {"name": "path",        "solid": False, "encounter": False},
    "_": {"name": "floor",       "solid": False, "encounter": False},   # inside buildings / camps
    "*": {"name": "flowers",     "solid": False, "encounter": True},
    "x": {"name": "dead_flowers","solid": False, "encounter": True},
    "=": {"name": "bridge",      "solid": False, "encounter": False},
    "|": {"name": "gate",        "solid": False, "encounter": False},   # "||" passage, closed until its boss is beaten
    "T": {"name": "tree",        "solid": True,  "encounter": False},
    "r": {"name": "rock",        "solid": True,  "encounter": False},
    "#": {"name": "wall",        "solid": True,  "encounter": False},
    "f": {"name": "fence",       "solid": True,  "encounter": False},
    "H": {"name": "house",       "solid": True,  "encounter": False},
    "D": {"name": "door",        "solid": True,  "encounter": False},
    "~": {"name": "water",       "solid": True,  "encounter": False},
    "o": {"name": "well",        "solid": True,  "encounter": False},
    "c": {"name": "campfire",    "solid": True,  "encounter": False},
    "^": {"name": "cliff",       "solid": True,  "encounter": False},   # border between biomes
    "M": {"name": "mountain",    "solid": True,  "encounter": False},   # outside every biome / solid rock in the cellar
    "F": {"name": "flower_heap", "solid": True,  "encounter": False},   # Sunny's tower of flowers (Rainbow Fields)
    "a": {"name": "antenna",     "solid": True,  "encounter": False},   # Hal's radio masts (Tundra)
    "q": {"name": "pale_stone",  "solid": False, "encounter": False},   # the colourless altar in the Garden (Pale Orb)
    # cellar
    "g": {"name": "metal_floor", "solid": False, "encounter": True},    # factory floor (fights can start)
    # conveyor belts move the player in their direction ("push" = direction)
    ">": {"name": "conveyor_right", "solid": False, "encounter": False, "push": (1, 0)},
    "<": {"name": "conveyor_left",  "solid": False, "encounter": False, "push": (-1, 0)},
    "A": {"name": "conveyor_up",    "solid": False, "encounter": False, "push": (0, -1)},
    "v": {"name": "conveyor_down",  "solid": False, "encounter": False, "push": (0, 1)},
    "m": {"name": "machine",     "solid": True,  "encounter": False},
    # core / void
    "e": {"name": "cable",       "solid": False, "encounter": True},    # glowing cables on the floor (core)
    "E": {"name": "gold_cable",  "solid": False, "encounter": True},    # the golden cable to the Core's secret room
    "p": {"name": "pipe",        "solid": True,  "encounter": False},
    "O": {"name": "core",        "solid": True,  "encounter": False},   # THE core object
    "k": {"name": "crate",       "solid": True,  "encounter": False},
}

DEFAULT_COLORS = {
    ".": (90, 170, 80),   ",": (190, 160, 110), "_": (150, 115, 80),  "*": (230, 150, 200),
    "x": (130, 120, 115), "=": (160, 120, 70),  "|": (240, 240, 240), "T": (40, 110, 50),
    "r": (120, 115, 110), "#": (110, 100, 95),  "f": (150, 110, 70),  "H": (180, 80, 70),
    "D": (100, 50, 30),   "~": (60, 120, 210),  "o": (120, 120, 140), "c": (240, 120, 40),
    "^": (95, 90, 85),    "M": (40, 38, 45),    "F": (255, 205, 90),   "a": (150, 155, 170), "q": (228, 228, 232),
    "g": (95, 95, 105),   "v": (70, 70, 78),    "m": (170, 130, 60),  "k": (140, 100, 60),
    ">": (70, 70, 78),    "<": (70, 70, 78),    "A": (70, 70, 78),
    "e": (200, 60, 90),   "E": (235, 190, 70),   "p": (105, 105, 125), "O": (255, 80, 110),
}

# only what differs from DEFAULT_COLORS
BIOME_COLORS = {
    "village": {},
    "lunapark": {          # pastel amusement park (its own small level)
        ".": (240, 214, 232), ",": (255, 240, 205), "_": (230, 180, 120), "f": (255, 255, 255), "H": (225, 75, 95),
        "m": (110, 180, 240), "o": (250, 215, 90), "T": (120, 200, 150), "*": (255, 160, 220), "k": (200, 140, 90),
        "~": (120, 180, 240), "=": (200, 150, 100), "c": (255, 150, 60), "M": (40, 25, 45),
    },
    "rainbow_fields": {
        ".": (150, 215, 110), "*": (255, 140, 220), "T": (80, 170, 90), ",": (225, 200, 150),
    },
    "sugarwood_grove": {   # candy forest
        ".": (215, 150, 170), "T": (230, 70, 90), ",": (240, 225, 200), "*": (255, 255, 160),
        "f": (255, 240, 240), "H": (170, 100, 60), "~": (150, 90, 60), "r": (250, 200, 220),
        "^": (140, 90, 70),
    },
    "silverpine_tundra": {
        ".": (225, 235, 245), "T": (40, 80, 70), ",": (190, 200, 210), "~": (160, 210, 240),
        "r": (150, 160, 175), "*": (200, 230, 255), "^": (120, 130, 145), "H": (120, 90, 80),
    },
}


BIOME_COLORS["toy_factory"] = {
    "#": (50, 50, 62), "_": (115, 115, 125), ",": (125, 125, 135), "M": (28, 28, 34),
}
BIOME_COLORS["underground_garden"] = {
    ".": (40, 95, 75), "T": (25, 150, 95), "~": (40, 110, 150), "*": (130, 255, 210),   # glowing mushrooms
    "x": (95, 70, 120), "#": (30, 48, 42), ",": (75, 110, 90), "r": (60, 75, 70), "M": (18, 26, 24),
}


BIOME_COLORS["the_core"] = {
    "g": (72, 60, 78), "#": (36, 27, 42), "_": (84, 72, 90), ",": (92, 80, 98), "m": (118, 112, 132), "k": (96, 78, 70), "M": (18, 12, 22),
}
BIOME_COLORS["the_void"] = {
    ".": (44, 32, 64), "#": (10, 7, 16), "_": (56, 44, 76), ",": (52, 40, 72), "*": (96, 66, 160), "x": (64, 54, 84),
    "r": (70, 58, 92), "T": (150, 100, 230), "M": (4, 3, 8), "~": (12, 8, 24), "=": (98, 82, 130),
}


def tile_color(char, biome):
    return BIOME_COLORS.get(biome, {}).get(char, DEFAULT_COLORS[char])


# MARKERS - special points in prefabs. On the map they become a normal tile, the game remembers them separately.
# "becomes": None = take the tile next to the marker (so gold on a floor lies on floor, on grass on grass)
MARKERS = {
    "S": {"name": "player_start", "becomes": ","},
    "N": {"name": "npc",          "becomes": None},
    "E": {"name": "exit",         "becomes": ","},   # generator must connect a path to this point
    "B": {"name": "boss",         "becomes": "."},
    "P": {"name": "portal",       "becomes": ","},   # entry to another map (surface <-> cellar)
    "$": {"name": "gold",         "becomes": None},  # gold on the ground, picked up by walking over it
    "I": {"name": "item",         "becomes": None},  # item on the ground (fixed or random - see prefab @items)
}

# " " (space) in a prefab = empty: the generator fills it
EMPTY = " "


def is_solid(char):
    tile = TILES.get(char)
    return tile["solid"] if tile else True
