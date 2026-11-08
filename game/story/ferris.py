# FERRIS - the courier in the Village (7.11). He shows up after the Rainbow Fields boss, right next to the start,
# and sells SHORTCUTS (like the warp buttons in FNaF World): bought once, then they work for good from the world
# map (M) - click one, "Travel to ...?" Yes, and you are there. Talking to him opens the same map, where the
# places you have been to but don't have yet show a price (SHORTCUT_FIGHTS x one fight's gold in that biome).
# Only places the player has really been to (the "need" flags).

import math
from collections import deque
from game.story.milo import _spot
from game.shop.stock import FIGHT_GOLD, round10
from game.world.tiles import TILES

APPEARS_AFTER = "boss:rainbow_fields"
SHORTCUT_FIGHTS = 15
SHORTCUTS = [
    # id, name on the map, level, where (("gate", from, to) = just behind that gate | ("arrival", key) |
    # ("centre", zone, (from, to)) = the middle of the zone, reachable from that gate | ("before_boss",) = the factory
    # hall next to the boss hall), biome (price), need
    {"id": "candy", "name": "Sugarwood Grove", "level": "surface", "at": ("centre", "candy", ("rainbow_fields", "candy")),
     "biome": "sugarwood_grove", "need": ["visited:candy"]},
    {"id": "factory", "name": "Toy Factory", "level": "cellar", "at": ("before_boss",),
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


def _walkable(world, x, y):
    return 0 <= x < world.width and 0 <= y < world.height and not TILES[world.tiles[y][x]]["solid"]


def _zone_centre(world, zone, gate_ends):
    """(8.11) The walkable tile nearest the middle of a zone that you can walk to from that zone's gate."""
    cells = [(x, y) for y in range(world.height) for x in range(world.width) if world.zones[y][x] == zone]
    gate = next((g for g in world.gates if (g["from"], g["to"]) == tuple(gate_ends)), None)
    if not cells or not gate:
        return None
    cx, cy = sum(c[0] for c in cells) / len(cells), sum(c[1] for c in cells) / len(cells)
    start = tuple(gate["entry"])
    seen, todo = {start}, deque([start])
    while todo:                                          # every tile of the zone you can walk to from the gate
        x, y = todo.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in seen and _walkable(world, nx, ny) and world.zones[ny][nx] == zone:
                seen.add((nx, ny))
                todo.append((nx, ny))
    # not right next to a wall / tree: all 8 neighbours walkable too
    roomy = [c for c in seen if all(_walkable(world, c[0] + dx, c[1] + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1))]
    return min(roomy or seen, key=lambda c: math.dist(c, (cx, cy)))


def tile_of(shortcut, world):
    """The tile a shortcut leads to in that level's world (None if it isn't there)."""
    kind, *rest = shortcut["at"]
    if kind == "centre":
        cache = world.__dict__.setdefault("_shortcut_tiles", {})
        if shortcut["id"] not in cache:
            cache[shortcut["id"]] = _zone_centre(world, rest[0], rest[1])
        return cache[shortcut["id"]]
    if kind == "before_boss":                            # (8.11) the factory hall nearest to the boss hall
        centres, boss = getattr(world, "room_centres", None), getattr(world, "boss_room", None)
        if not centres or boss is None:
            return None
        near = min((c for i, c in enumerate(centres) if i != boss), key=lambda c: math.dist(c, centres[boss]))
        return (near[0], near[1] + 1)
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
