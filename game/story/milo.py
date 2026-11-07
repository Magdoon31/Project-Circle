# STORY STATE on the map: where Milo stands right now, and which ways are closed by the story.
#
# MILO moves after bosses (he is always one step ahead - nobody ever explains how):
#   Village fence (start) -> entrance of Rainbow Fields -> entrance of Candy -> Separated Village
#   -> entrances of the Underground Garden (Factory side and/or Tundra side, wherever the player came through)
#   -> the Core (boss) -> the Void (shrine, a memory)
#
# PATH CHOICE (like Crimson / Corruption in Terraria): from the Separated Village the player picks the Factory
# (portal down) or the Tundra (passage). The first one entered is the chosen path (flag "path:factory" /
# "path:tundra"); the OTHER way stays closed until the chosen path's boss is beaten. The chosen way is always open.

import math
from game.world.tiles import TILES

PATH_ZONES = {"tundra": ("surface", {"tundra", "tundra_pass"}), "factory": ("cellar", {"factory"})}


def _spot(world, near, taken=(), radius=(2, 5), allow_path=False):
    """A walkable tile near `near`, not on a path / gate / portal, so Milo doesn't block the way."""
    bad = {tuple(p["pos"]) for p in world.portals} | {tuple(c) for g in world.gates for c in g["cells"]} | set(taken)
    best = None
    nx, ny = near
    for r in range(radius[0], radius[1] + 1):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                x, y = nx + dx, ny + dy
                if max(abs(dx), abs(dy)) != r or not (0 < x < world.width - 1 and 0 < y < world.height - 1):
                    continue
                t = world.tiles[y][x]
                if TILES[t]["solid"] or t in ("=", "|") or (t == "," and not allow_path) or (x, y) in bad:
                    continue
                # keep a free tile around him (he must never close a narrow way)
                if sum(1 for ax in (-1, 0, 1) for ay in (-1, 0, 1) if not TILES[world.tiles[y + ay][x + ax]]["solid"]) < 8:
                    continue
                d = math.hypot(dx, dy)
                if best is None or d < best[0]:
                    best = (d, (x, y))
        if best:
            return best[1]
    return near


def _gate(world, a, b):
    return next((g for g in world.gates if g["from"] == a and g["to"] == b), None)


def milo_npcs(level, world, flags):
    """(extra NPC dicts for this level, ids of map NPCs to hide)."""
    beaten = lambda zone: f"boss:{zone}" in flags
    extra, hidden = [], set()
    if beaten("village"):
        hidden.add("milo")                                   # he left the Village fence
    if level == "surface":
        place = None
        if beaten("village") and not beaten("rainbow_fields"):
            place = ("milo_rainbow", _gate(world, "village", "rainbow_fields"))
        elif beaten("rainbow_fields") and not beaten("candy"):
            place = ("milo_candy", _gate(world, "rainbow_fields", "candy"))
        elif beaten("candy") and not (beaten("factory") or beaten("tundra")):
            place = ("milo_separated", _gate(world, "candy", "separated"))
        if place and place[1]:
            extra.append({"pos": _spot(world, place[1]["entry"], radius=(3, 7) if place[0] == "milo_separated" else (2, 5)),
                          "id": place[0], "zone": None})
    elif level == "cellar" and beaten("garden"):
        # before the way up to the Core: a warning about what's waiting there
        portal = next((p for p in world.portals if p["leads_to"] == "core:entry"), None)
        if portal:
            extra.append({"pos": _spot(world, portal["pos"], [world.arrivals.get("core:core")], (2, 4), allow_path=True),
                          "id": "milo_core_entrance", "zone": "garden"})
    elif level == "cellar":
        if beaten("factory"):
            g = _gate(world, "factory", "garden")
            if g:
                extra.append({"pos": _spot(world, g["entry"]), "id": "milo_garden_factory", "zone": "garden"})
        if beaten("tundra") and "surface:tundra_pass" in world.arrivals:
            extra.append({"pos": _spot(world, world.arrivals["surface:tundra_pass"], [n["pos"] for n in extra]),
                          "id": "milo_garden_tundra", "zone": "garden"})
    return extra, hidden


def choose_path(level, flags, player_zone):
    """The first of the two ways the player walks into becomes the chosen path (returns the new flag or None)."""
    if "path:factory" in flags or "path:tundra" in flags:
        return None
    for path, (lvl, zones) in PATH_ZONES.items():
        if level == lvl and player_zone in zones:
            return f"path:{path}"
    return None


def path_locks(level, world, flags, player_zone):
    """(locked gate positions, locked portal positions): the way NOT chosen, until the chosen path's boss is beaten."""
    gates, portals = set(), set()
    if level != "surface":
        return gates, portals
    if "path:tundra" in flags and "boss:tundra" not in flags:
        for p in world.portals:                          # the portal down to the Factory
            if p["zone"] == "separated":
                portals.add(tuple(p["pos"]))
    if "path:factory" in flags and "boss:factory" not in flags:
        g = _gate(world, "separated", "tundra")          # the passage to the Tundra
        if g:
            gates.add(tuple(g["pos"]))
    return gates, portals
