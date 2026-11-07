# WREN - the curious researcher (see STORY.md "Wren").
#   Separated Village (until the Garden is open)  ->  her camp in the Underground Garden (prefab wren_camp)
#   -> after her investigation (quest "wren") she stays at the camp.
#   ONLY if you give her the Cassette Tape (flag wren:moved) she goes off to search by herself (the camp is empty).
#   After the GARDEN BOSS she is at the way up to the Core with Milo - they ARGUE (starts by itself when you come
#   close: "auto"; you only listen). Then Wren leaves for good (flag wren:argued) and Milo stays: the same talk goes
#   straight on with his warning about the Core (milo_core_entrance).
#   No tape = no argument: only Milo and his warning, as before.
#
# The Garden is open once the boss of the chosen path is beaten (Factory or Tundra).

import math
from game.story.milo import _spot, _gate

ARGUMENT_RADIUS = 4          # tiles: coming this close to Wren + Milo starts the overheard argument


def garden_open(flags):
    return "boss:factory" in flags or "boss:tundra" in flags


def _zone_centre(world, zone):
    cells = [(x, y) for y in range(world.height) for x in range(world.width) if world.zones[y][x] == zone]
    if not cells:
        return None
    return (round(sum(x for x, _ in cells) / len(cells)), round(sum(y for _, y in cells) / len(cells)))


def wren_npcs(level, world, flags, milo_extra=()):
    """(all extra NPCs = Milo's ones changed if needed + Wren's, ids of map NPCs to hide)."""
    extra, hidden = list(milo_extra), set()
    if not garden_open(flags) or "wren:moved" in flags:
        hidden.add("wren")                               # her Garden camp is empty (not there yet / gone searching)
    if level == "surface" and not garden_open(flags):
        centre = _zone_centre(world, "separated")
        if centre:
            taken = [n["pos"] for n in extra]
            extra.append({"pos": _spot(world, centre, taken, (2, 9)), "id": "wren_village", "zone": "separated"})
    elif level == "cellar" and "wren:moved" in flags and "wren:argued" not in flags and "boss:garden" in flags:
        # Milo stands where he warns you about the Core - this time Wren is with him and they argue
        milo = next((n for n in extra if n["id"] == "milo_core_entrance"), None)
        if milo:
            extra = [n for n in extra if not n["id"].startswith("milo")]    # he's only here
            wren = _spot(world, milo["pos"], [milo["pos"]], (1, 4), allow_path=True)
            extra.append({"pos": milo["pos"], "id": "milo_argument", "zone": "garden", "auto": ARGUMENT_RADIUS})
            extra.append({"pos": wren, "id": "wren_moved", "zone": "garden"})
    return extra, hidden


def auto_npc_near(npcs, tile_of_player):
    """An NPC that starts talking by itself when the player comes close (e.g. the Wren x Milo argument)."""
    px, py = tile_of_player
    for npc in npcs:
        if npc.get("auto") and math.dist(npc["pos"], (px, py)) <= npc["auto"]:
            return npc
    return None
