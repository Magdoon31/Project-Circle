# UNDERGROUND GARDEN secrets (see STORY.md "Gardener" / "Mushroom ring + Pale Orb").
#
# MUSHROOM RING: the first time you step inside, a whisper starts by itself (dialogue ring_voice, flag ring:heard).
# It is a riddle about the PALE ORB:
#   "Only the innocent may see what is true. Find the stone that has no colour. Come with nothing to hurt with.
#    Stand. Be still. Wait until the light forgets you."
# PALE ALTAR: the Pale Orb shows up there (flag pale_orb:revealed) only if ALL of these are true:
#   - you heard the whisper (ring:heard)
#   - you stand on the pale stone (tile "q")
#   - NO weapon is equipped ("nothing to hurt with" / "the innocent")
#   - you don't move for PALE_WAIT_SECONDS ("until the light forgets you")


PALE_WAIT_SECONDS = 5                 # (10.11, was 10)
RING_RADIUS = 3              # tiles from the middle of the ring: you are inside


def garden_npcs(level, world, flags, extra=()):
    """(extra NPCs, ids to hide): before the whisper the ring's middle starts talking by itself."""
    extra, hidden = list(extra), set()
    if level == "cellar" and "ring:heard" not in flags:
        ring = next((n for n in world.npcs if n["id"] == "ring_voice"), None)
        if ring:
            hidden.add("ring_voice")
            extra.append(dict(ring, auto=RING_RADIUS))
    return extra, hidden


class PaleAltar:
    """Counts how long the player stands still on the pale stone, unarmed (after hearing the whisper)."""
    def __init__(self):
        self.frames = 0

    def update(self, game):
        m = game.map
        if m.level != "cellar" or "ring:heard" not in m.flags or "pale_orb:revealed" in m.flags:
            self.frames = 0
            return False
        tx, ty = m.tile_at(game.player.x, game.player.y)
        on_stone = 0 <= ty < m.world.height and 0 <= tx < m.world.width and m.world.tiles[ty][tx] == "q"
        unarmed = game.inventory.active_items.get("weapon") is None
        still = abs(game.player.vx) < 0.05 and abs(game.player.vy) < 0.05
        self.frames = self.frames + 1 if (on_stone and unarmed and still) else 0
        if self.frames >= PALE_WAIT_SECONDS * 60:
            m.flags.add("pale_orb:revealed")
            self.frames = 0
            return True
        return False
