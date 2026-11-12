# THE FOREMAN (11.11) leaves his Factory break room once Milo is beaten with the Peace Gun (flag void_unlocked) and
# waits in the Core, in one of its structures (a control desk if there is one - "all switches OFF, except one"): he
# gives the player the Old Note (foreman_core.json). Without the Peace Gun ending he never comes up.
# The Broken Bulb can be shown to him in both places (foreman_bulb.json).

from game.story.milo import _spot

MOVES_AFTER = "void_unlocked"
FACTORY_ID, CORE_ID = "foreman", "foreman_core"
CORE_ROOMS = ("core_control_desk", "core_generator_room", "core_storage_bay", "core_cooling_vents")  # preferred first
VOID_PORTAL = "void:entry"       # no structure at all: next to the way down


def foreman_npcs(level, world, flags, extra):
    """(extra NPC dicts for this level, ids of map NPCs to hide)."""
    if MOVES_AFTER not in flags:
        return extra, set()
    if level == "core":
        spot = core_spot(world, [tuple(n["pos"]) for n in extra])
        if spot:
            extra = extra + [{"pos": spot, "id": CORE_ID, "zone": None}]
    return extra, {FACTORY_ID}


def core_spot(world, taken):
    """Inside the first Core structure of the preferred kinds, off its items and gold."""
    taken = list(taken) + [tuple(p["pos"]) for p in getattr(world, "pickups", [])]
    rooms = [s for kind in CORE_ROOMS for s in getattr(world, "structures", []) if s["name"] == kind]
    if rooms:
        x, y, w, h = rooms[0]["rect"]
        return _spot(world, (x + w // 2, y + h // 2), taken, radius=(1, max(w, h) // 2), allow_path=True)
    portal = next((p for p in world.portals if p["leads_to"] == VOID_PORTAL), None)
    return _spot(world, portal["pos"], taken, (2, 4), allow_path=True) if portal else None
