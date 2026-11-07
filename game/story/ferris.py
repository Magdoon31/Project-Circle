# FERRIS - the courier in the Village (7.11). He shows up after the Rainbow Fields boss, right next to the start,
# and sells SHORTCUTS (like the warp buttons in FNaF World): bought once, then they work for good from the world
# map (M) - click one, "Travel to ...?" Yes, and you are there. Talking to him opens the same map, where the
# places you have been to but don't have yet show a price (SHORTCUT_FIGHTS x one fight's gold in that biome).
# Only places the player has really been to (the "need" flags).

from game.story.milo import _spot
from game.shop.stock import FIGHT_GOLD, round10

APPEARS_AFTER = "boss:rainbow_fields"
SHORTCUT_FIGHTS = 15
SHORTCUTS = [
    # id, name on the map, level, where (("gate", from, to) = just behind that gate | ("arrival", key)), biome (price), need
    {"id": "candy", "name": "Candy Entrance", "level": "surface", "at": ("gate", "rainbow_fields", "candy"),
     "biome": "sugarwood_grove", "need": ["visited:candy"]},
    {"id": "factory", "name": "Toy Factory", "level": "cellar", "at": ("arrival", "surface:separated"),
     "biome": "toy_factory", "need": ["visited:factory"]},
    {"id": "garden_tundra", "name": "Garden (Tundra side)", "level": "cellar", "at": ("arrival", "surface:tundra_pass"),
     "biome": "underground_garden", "need": ["arrived:garden_tundra"]},
    {"id": "garden_factory", "name": "Garden (Factory side)", "level": "cellar", "at": ("gate", "factory", "garden"),
     "biome": "underground_garden", "need": ["boss:factory", "visited:garden"]},
    {"id": "core", "name": "The Core", "level": "core", "at": ("arrival", "cellar:garden"),
     "biome": "the_core", "need": ["visited:core"]},
]
BY_ID = {s["id"]: s for s in SHORTCUTS}


def price(shortcut):
    return round10(FIGHT_GOLD[shortcut["biome"]] * SHORTCUT_FIGHTS)


def tile_of(shortcut, world):
    """The tile a shortcut leads to in that level's world (None if it isn't there)."""
    kind, *rest = shortcut["at"]
    if kind == "arrival":
        return getattr(world, "arrivals", {}).get(rest[0])
    gate = next((g for g in world.gates if g["from"] == rest[0] and g["to"] == rest[1]), None)
    return tuple(gate["entry"]) if gate else None


def available(flags, owned):
    """Shortcuts the player has been to: [(shortcut, owned?)]."""
    return [(s, s["id"] in owned) for s in SHORTCUTS if all(f in flags for f in s["need"])]


def ferris_npcs(level, world, flags, extra):
    """Adds Ferris next to the Village start once the Rainbow Fields boss is beaten."""
    if level != "surface" or APPEARS_AFTER not in flags or not hasattr(world, "player_start"):
        return extra, set()
    sx, sy = world.player_start
    spot = _spot(world, (sx + 3, sy - 2), taken=[tuple(n["pos"]) for n in extra], radius=(0, 4), allow_path=True)
    return extra + [{"id": "ferris", "pos": spot}], set()
