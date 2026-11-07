# PALE WORLD (7.11, see the project's PALE_WORLD.md) - the evil reflection under the normal world.
#
# GLITCH STONES (tile "Q"): with the Pale Orb equipped you push into one for GLITCH_PUSH_FRAMES. Going through
# a stone never moves you: you stand on the same tile, only the world changes (normal <-> pale). Stones that
# exist only below (in the pale pockets, Nowhere) have their own "target" (level, tile).
#
# LINKS - every way in has a purpose:
#   ENTRANCE: a rock next to a normal path.
#   ENCLAVE: a small clearing deep inside a forest, or an island in a lake, in the NORMAL world - you can see it,
#            you can't walk there (nothing artificial gives it away). Its own stone stands in the clearing.
#   The PALE level is closed: solid rock except a pale pocket around a long winding path from the entrance to the
#   enclave (a washed-out, slightly wrong copy of the terrain there). Sometimes two pockets run into each other.
#   surface: village - Milo's island (a "second" Milo, there from the start) | tundra - gold (Garden-level piles) |
#            the Coupon (bring it to Lucky: the Golden Wheel - stakes 50/100/500, ~104% back)
#   cellar:  garden  - next to the Pale Orb altar (gold) | Headstart (4th shrine) | Spare Pocket (near the Garden
#            boss building; its stone in the pocket lets you through only after the Garden boss) | a rare item
#            + THE MAZE (like the glitch chains in FNaF World, no hints):
#              garden: ultra stone -> pale pocket A -> NOWHERE (a level below) -> up into pale pocket B ->
#              GARDEN* (a long hidden clearing in the forest; you arrive next to its stone) -> back up into B ->
#              B also leads out to the normal Garden (looks like a dead end).
#              But GARDEN* has a second stone at its far end, off the screen -> pale pocket D -> NOWHERE 2 ->
#              the only stone down: ### (no music, "Not yet.", the Peace Gun). Out of ###: take the Orb off.
#              Nowhere also has stones back up into other pockets (loops).
# Everything here uses its own random generators, so the rest of a seed's world doesn't change (old saves too).

import math, random
from collections import deque
from game.world import loot
from game.world.tiles import TILES

PALE_PREFIX = "pale_"
NOWHERE, NOWHERE2, HASH = "pale_nowhere", "pale_nowhere2", "pale_hash"    # the levels below the pale Garden
DEEP_LEVELS = (NOWHERE, NOWHERE2, HASH)
PALE_ZONES = {"surface": {"village", "tundra"}, "cellar": {"garden"}}
LINKS = {"surface": [("village", "milo"), ("tundra", "gold"), ("tundra", "coupon")],
         "cellar": [("garden", "altar"), ("garden", "backroom"), ("garden", "headstart"), ("garden", "item"),
                    ("garden", "maze")]}
STONE_CHARS = {"r", "M", "#", "^", "T"}       # what an entrance stone can be made of (rock first, trees if nothing else)
HIDE_CHARS = ("T", "~")                       # enclaves only inside forests and lakes
ENTRANCE_SPACING = 12                         # entrance stones at least this far apart
FLOOR = {"village": ".", "tundra": ".", "garden": "."}
ZONE_BIOMES = {"village": "village", "tundra": "silverpine_tundra", "garden": "underground_garden"}
OPEN_R = 2.0                                  # enclave clearing / island radius
ENCLAVE_DEPTH = 5                             # its centre: this deep inside the forest / lake (= 2+ tiles of it all round)
SEEN_FROM = 10                                # ...and a walkable tile at most this far (you can see it)
ENCLAVE_DIST = {"milo": (10, 26), "altar": (6, 20)}    # from the anchor (start / altar)
ENTRANCE_DIST = (14, 30)                      # entrance stone <-> enclave (the pale path is longer: it winds)
JOIN_CHANCE = 0.4                             # a pocket runs into an earlier one (one pocket, more stones)
JOIN_MAX = 26
MAZE_OFFSCREEN = (16, 10)                     # garden*: the hidden stone this far (x or y) from the arrival
OPEN = "open"                                 # pocket group of the ordinary links (they may run into each other)
MAZE_GAP = 6                                  # maze paths at least this far from every other path
POCKET_R = 3.6                                # the pale pocket: how far around its path the terrain is kept
DECOR = {"T", "r", "*", "x", "k", "m", "p", "e"}
NEW_DECOR = {"village": "T", "tundra": "T", "garden": "T"}
BACKROOM_FLAG = "open:garden_backroom"        # Game sets it once the Garden boss is beaten
LOOT_LEVEL = {"village": "underground_garden", "tundra": "underground_garden"}   # surface secrets pay like the Garden
GOLD_PILES = 3                                # piles on a "gold" enclave
MUSIC = {NOWHERE: "nowhere", NOWHERE2: "nowhere", HASH: "silence"}     # "silence" = no such music; other pale levels: "pale_world"

_SWAP = {"a": "4", "e": "3", "i": "1", "o": "0", "s": "5", "A": "4", "E": "3", "I": "1", "O": "0", "S": "5"}
_SPECS = {}                                   # seed -> the cellar's stones down there (so Nowhere needn't rebuild it)


def distort(text):
    """A name the Pale World got a little wrong ("Village" -> "V1ll4ge"): every other swappable letter."""
    out, k = [], 0
    for ch in text:
        if ch in _SWAP:
            k += 1
            if k % 2:
                ch = _SWAP[ch]
        out.append(ch)
    return "".join(out)


def is_pale(level):
    return level.startswith(PALE_PREFIX)


def base_level(level):
    return "cellar" if level in DEEP_LEVELS else level[len(PALE_PREFIX):] if is_pale(level) else level


def music_for(level, biome):
    if level in MUSIC:
        return MUSIC[level]
    return "pale_world" if is_pale(level) else biome


def _inside(world, x, y, margin=0):
    return margin <= x < world.width - margin and margin <= y < world.height - margin


def _walk(world, x, y):
    return _inside(world, x, y) and not TILES[world.tiles[y][x]]["solid"]


def _flood(world, starts):
    seen = set(starts)
    queue = deque(starts)
    while queue:
        x, y = queue.popleft()
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if n not in seen and _walk(world, *n):
                seen.add(n)
                queue.append(n)
    return seen


def _sign(v):
    return (v > 0) - (v < 0)


def _cardinal(dx, dy):
    return (_sign(dx), 0) if abs(dx) >= abs(dy) else (0, _sign(dy))


def _add(a, b, k=1):
    return (a[0] + b[0] * k, a[1] + b[1] * k)


def with_glitches(level, world):
    add_glitches(level, world)
    return world


def _stone(sid, tile, stand, role, zone, pale_only=False, target=None, **extra):
    s = {"id": sid, "tile": tuple(tile), "stand": tuple(stand), "role": role, "zone": zone, "pale_only": pale_only}
    if target:
        s["target"] = target
    s.update(extra)
    return s


# --- the normal world -----------------------------------------------------------------------------------
class _Builder:
    def __init__(self, level, world):
        self.level, self.w = level, world
        self.rnd = random.Random(f"glitch3-{level}-{world.seed}")
        w = world
        starts = [tuple(w.player_start)] + [tuple(a) for a in getattr(w, "arrivals", {}).values()]
        self.reach = _flood(w, [s for s in starts if _walk(w, *s)])
        busy = set(getattr(w, "prefab_cells", set())) | set(getattr(w, "structure_cells", set()))
        for g in w.gates:
            busy |= {tuple(c) for c in g.get("cells", [])}
        for s in getattr(w, "structures", []):
            x0, y0, sw, sh = s["rect"]
            busy |= {(x, y) for y in range(y0 - 1, y0 + sh + 1) for x in range(x0 - 1, x0 + sw + 1)}
        for cells in list(getattr(w, "hidden", {}).values()) + list(getattr(w, "locked", {}).values()):
            busy |= {tuple(c) for c in cells}
        for p in [tuple(p["pos"]) for p in w.pickups] + [tuple(n["pos"]) for n in w.npcs] + \
                 [tuple(p["pos"]) for p in w.portals] + starts:
            busy |= {(p[0] + dx, p[1] + dy) for dx in range(-3, 4) for dy in range(-3, 4)}
        fence = getattr(w, "start_fence", None)
        if fence:
            busy |= {(x, y) for y in range(fence[1] - 2, fence[1] + fence[3] + 2) for x in range(fence[0] - 2, fence[0] + fence[2] + 2)}
        self.busy, self.carved, self.entrances = busy, set(), []
        self.depth, self.stones = {}, {}
        self.paths = []                     # every pale path of this level so far (for joining)

    # how deep every forest / lake cell lies inside its forest / lake (1 = at the edge), per zone
    def depth_map(self, zone):
        if zone in self.depth:
            return self.depth[zone]
        w, reach = self.w, self.reach
        ok = lambda x, y: _inside(w, x, y, 1) and w.tiles[y][x] in HIDE_CHARS and (x, y) not in reach \
            and w.zones[y][x] == zone
        D, queue = {}, deque()
        for y in range(1, w.height - 1):
            for x in range(1, w.width - 1):
                if ok(x, y) and any(not ok(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                    D[(x, y)] = 1
                    queue.append((x, y))
        while queue:
            x, y = queue.popleft()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    n = (x + dx, y + dy)
                    if n not in D and ok(*n):
                        D[n] = D[(x, y)] + 1
                        queue.append(n)
        self.depth[zone] = D
        return D

    def free(self, cells):
        return not any(c in self.busy or c in self.carved for c in cells)

    def seen(self, c, zone):
        r = SEEN_FROM
        return any((c[0] + dx, c[1] + dy) in self.reach and self.w.zones[c[1] + dy][c[0] + dx] == zone
                   for dy in range(-r, r + 1) for dx in range(-r, r + 1) if dx * dx + dy * dy <= r * r)

    def enclave_spot(self, zone, anchor=None, dist=None, prefer_lake=False):
        """(centre, small) - a clearing / island deep enough in a forest or lake; a smaller one if there is none."""
        for depth in (ENCLAVE_DEPTH, ENCLAVE_DEPTH - 1):
            c = self._spot(zone, depth, anchor, dist, prefer_lake)
            if c:
                return c, depth < ENCLAVE_DEPTH
        return None, False

    def _spot(self, zone, depth, anchor, dist, prefer_lake):
        D = self.depth_map(zone)
        cands = sorted(c for c, d in D.items() if d >= depth)
        if anchor:
            cands = [c for c in cands if dist[0] <= math.dist(c, anchor) <= dist[1]]
        self.rnd.shuffle(cands)
        if prefer_lake:
            cands.sort(key=lambda c: self.w.tiles[c[1]][c[0]] != "~")
        if anchor and not prefer_lake:
            cands.sort(key=lambda c: math.dist(c, anchor))
        for c in cands[:400]:
            area = [(c[0] + dx, c[1] + dy) for dx in range(-4, 5) for dy in range(-4, 5)]
            if self.free(area) and self.seen(c, zone):
                return c
        return None

    def entrance_stone(self, zone, near, dist=ENTRANCE_DIST, avoid=(), away=None, commit=True):
        w = self.w
        if zone not in self.stones:
            out = []
            for (x, y) in self.reach:
                if w.zones[y][x] != zone:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    s = (x + dx, y + dy)
                    if _inside(w, *s, 2) and w.tiles[s[1]][s[0]] in STONE_CHARS:
                        out.append((s, (x, y)))
            self.stones[zone] = sorted(out)
        out = [o for o in self.stones[zone] if w.tiles[o[0][1]][o[0][0]] in STONE_CHARS
               and not ({o[0], o[1]} & self.busy) and not ({o[0], o[1]} & self.carved)]
        for lo, hi in (dist, (dist[0] - 6, dist[1] + 15), (4, 60)):
            c = [o for o in out if lo <= math.dist(o[0], near) <= hi and o[0] not in avoid
                 and all(math.dist(o[0], e) >= ENTRANCE_SPACING for e in self.entrances)
                 and (away is None or math.dist(o[0], away) > math.dist(o[0], near) + 6)]
            if c:
                rocks = [o for o in c if w.tiles[o[0][1]][o[0][0]] != "T"] or c
                pick = self.rnd.choice(rocks)
                if not commit:
                    return pick
                self.entrances.append(pick[0])
                w.tiles[pick[0][1]][pick[0][0]] = "Q"
                self.busy.add(pick[0])
                return pick
        return None

    def rock_point(self, near, dist, away=None):
        """A spot somewhere in the rock (only the pale pocket will be there); `away`: roughly away from that point."""
        w = self.w
        base = math.atan2(near[1] - away[1], near[0] - away[0]) if away else None
        for _ in range(500):
            a = base + self.rnd.uniform(-0.9, 0.9) if away else self.rnd.random() * math.tau
            d = self.rnd.uniform(*dist)
            p = (round(near[0] + math.cos(a) * d), round(near[1] + math.sin(a) * d))
            if _inside(w, *p, 6):
                return p
        return (min(max(near[0], 6), w.width - 7), min(max(near[1], 6), w.height - 7))

    def path(self, a, b, wander=5):
        """A long winding 4-connected path from a to b."""
        rnd, w = self.rnd, self.w
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy) or 1
        nx, ny = -dy / length, dx / length
        n = max(2, int(length / 5))
        points = [a]
        detour = rnd.random() < 0.5
        for i in range(1, n):
            t = i / n
            off = rnd.uniform(-wander, wander) + (math.sin(t * math.pi) * rnd.choice((-1, 1)) * 8 if detour else 0)
            points.append((round(a[0] + dx * t + nx * off), round(a[1] + dy * t + ny * off)))
        points.append(b)
        cells = [tuple(a)]
        for p in points[1:]:
            x, y = cells[-1]
            p = (min(max(p[0], 2), w.width - 3), min(max(p[1], 2), w.height - 3))
            while (x, y) != p:
                if x != p[0] and (y == p[1] or rnd.random() < 0.5):
                    x += _sign(p[0] - x)
                else:
                    y += _sign(p[1] - y)
                cells.append((x, y))
        if cells[-1] != tuple(b):
            cells.append(tuple(b))
        return cells

    def join(self, cells):
        """Sometimes a new pocket runs into an earlier one: a short path between their nearest points."""
        if not self.paths or self.rnd.random() > JOIN_CHANCE:
            return None
        best = None
        for other in self.paths:
            for c in cells[::3]:
                for o in other[::3]:
                    d = math.dist(c, o)
                    if best is None or d < best[0]:
                        best = (d, c, o)
        if best and 4 < best[0] <= JOIN_MAX:
            return self.path(best[1], best[2], wander=3)
        return None


def add_glitches(level, world):
    """Carves the enclaves into a NORMAL level, puts the glitch stones there and lists everything in
    world.glitches (normal stones) / world.glitch_links (+ pale paths and pale-only stones)."""
    if hasattr(world, "glitches"):
        return
    world.glitches, world.glitch_links = [], []
    if level not in LINKS:
        return
    b = _Builder(level, world)
    present = {world.zones[y][x] for (x, y) in b.reach}
    for zone, role in LINKS[level]:
        if zone not in present:
            continue
        link = _maze(b, zone) if role == "maze" else _enclave_link(b, zone, role)
        if link:
            world.glitch_links.append(link)
    world.glitches = [s for l in world.glitch_links for s in l["stones"] if not s["pale_only"]]
    if level == "cellar":
        _SPECS[world.seed] = world.deep_stones = _deep_stones(world)


def _carve_clearing(b, centre, zone, floor, small=False):
    r = 1.5 if small else OPEN_R
    open_ = [(centre[0] + dx, centre[1] + dy) for dx in range(-2, 3) for dy in range(-2, 3) if math.hypot(dx, dy) <= r]
    for (x, y) in open_:
        b.w.tiles[y][x] = floor
        b.w.zones[y][x] = zone
    b.carved |= {(centre[0] + dx, centre[1] + dy) for dx in range(-4, 5) for dy in range(-4, 5)}


def _enclave_link(b, zone, role):
    w = b.w
    centre, small = None, False
    if role == "milo":
        centre, small = b.enclave_spot(zone, tuple(w.player_start), ENCLAVE_DIST["milo"], prefer_lake=True)
    elif role == "altar":
        altar = sorted((x, y) for y in range(w.height) for x in range(w.width) if w.tiles[y][x] == "q")
        if altar:
            centre, small = b.enclave_spot(zone, altar[len(altar) // 2], ENCLAVE_DIST["altar"])
    elif role == "backroom":
        gate = next((g for g in w.gates if g.get("from") == "garden" and g.get("boss")), None)
        if gate:
            centre, small = b.enclave_spot(zone, tuple(gate["boss"]), (0, 40))    # the nearest hidden clearing
    if centre is None:
        centre, small = b.enclave_spot(zone)
    if centre is None:
        return None
    pick = b.entrance_stone(zone, centre)
    if not pick:
        return None
    stone, stand = pick
    _carve_clearing(b, centre, zone, FLOOR.get(zone, "."), small)
    d = _cardinal(stand[0] - centre[0], stand[1] - centre[1])      # the enclave's own stone faces the entrance
    k = 1 if small else 2
    e_stone, e_stand, back = _add(centre, d, k), _add(centre, d, k - 1), _add(centre, d, -1)
    w.tiles[e_stone[1]][e_stone[0]] = "Q"
    side = (d[1], d[0])
    biome = w.biome_at(*centre)
    lrnd = random.Random(f"glitch-loot-{b.level}-{w.seed}-{role}")
    if role == "milo":
        w.npcs.append({"pos": _add(centre, d, -k), "id": "milo_island", "zone": zone})
    elif role in ("gold", "altar"):
        biome = LOOT_LEVEL.get(zone, biome)                 # worth it for someone who already reached the Garden
        piles = [back, _add(back, side), _add(back, side, -1)] if not small else [back, _add(centre, side), _add(centre, side, -1)]
        for p in piles[:GOLD_PILES if role == "gold" else 1]:
            w.pickups.append({"pos": p, "type": "gold", "amount": loot.roll_gold(biome, lrnd) * (2 if role == "gold" else 1),
                              "glitch": True})
    elif role == "item":
        pool = loot.random_pool(biome)
        if pool:
            low = min(loot.weight(n) for n in pool)
            w.pickups.append({"pos": back, "type": "item", "item": lrnd.choice([n for n in pool if loot.weight(n) == low]),
                              "glitch": True})
    elif role == "coupon":
        w.pickups.append({"pos": back, "type": "item", "item": "Coupon", "glitch": True})   # -> Lucky's Golden Wheel
    elif role == "headstart":
        w.pickups.append({"pos": back, "type": "sigil", "sigil": "headstart"})
    elif role == "backroom":
        w.pickups.append({"pos": back, "type": "sigil", "sigil": "spare_pocket"})
    gid = f"{b.level}_{role}"
    far = _stone(gid + "_far", e_stone, e_stand, role + "_far", zone)
    if role == "backroom":
        far.update(needs=BACKROOM_FLAG, hint="garden_backroom")     # (checked only on the way IN, from the pale side)
    main = b.path(stand, e_stand)
    paths = [main]
    joined = b.join(main)
    if joined:
        paths.append(joined)
    b.paths.append(main)
    return {"role": role, "zone": zone, "centre": centre, "paths": paths,
            "stones": [_stone(gid, stone, stand, role, zone), far]}


# --- the maze to ### --------------------------------------------------------------------------------------
def _corridors(b, zone):
    """GARDEN* candidates: long narrow clearings deep in the forest (cell lists) - the two ends far enough apart
    that one is off the screen when you stand at the other."""
    D = b.depth_map(zone)
    deep = {c for c, d in D.items() if d >= 3 and c not in b.busy and c not in b.carved}
    starts = sorted(c for c in deep if D[c] >= 4 and b.seen(c, zone))
    b.rnd.shuffle(starts)
    for s in starts[:80]:
        prev, queue = {s: None}, deque([s])
        while queue:
            x, y = queue.popleft()
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if n in deep and n not in prev:
                    prev[n] = (x, y)
                    queue.append(n)
        far = [c for c in prev if abs(c[0] - s[0]) >= MAZE_OFFSCREEN[0] or abs(c[1] - s[1]) >= MAZE_OFFSCREEN[1]]
        if not far:
            continue
        f = min(far, key=lambda c: (abs(c[0] - s[0]) + abs(c[1] - s[1]), c))
        cells, c = [], f
        while c:
            cells.append(c)
            c = prev[c]
        cells.reverse()
        if len(cells) <= 40:
            yield cells


def _maze(b, zone):
    """The maze to ### (see the top of this file). Tries garden* spots until everything fits."""
    for corridor in _corridors(b, zone):
        plan = _maze_plan(b, zone, corridor)
        if plan:
            return _maze_build(b, zone, corridor, *plan)
    return None


def _maze_plan(b, zone, corridor):
    g_stand, h_stand = corridor[1], corridor[-2]
    corr = set(corridor)
    ultra = b.entrance_stone(zone, g_stand, (20, 40), away=h_stand, avoid=corr, commit=False)
    out = b.entrance_stone(zone, g_stand, (12, 30), away=h_stand, avoid=corr | {ultra and ultra[0]}, commit=False)
    if not ultra or not out or math.dist(ultra[0], out[0]) < ENTRANCE_SPACING:
        return None

    def apart(path, others, gap=MAZE_GAP):
        return all(math.dist(c, o) >= gap for c in path[::2] for other in others for o in other[::2])
    for _ in range(25):
        a0 = b.rock_point(ultra[1], (22, 30), g_stand)     # pocket A: ends at the stone down to Nowhere
        b0 = b.rock_point(g_stand, (16, 24), h_stand)      # pocket B: starts at the stone from Nowhere
        d0 = b.rock_point(h_stand, (18, 26), g_stand)      # pocket D: ends at the stone down to Nowhere 2 (other side)
        path_a = b.path(ultra[1], a0)
        path_b = b.path(b0, g_stand)
        path_b2 = b.path(path_b[len(path_b) // 2], out[1], wander=4)
        path_d = b.path(h_stand, d0)
        if apart(path_a, [path_b, path_b2, path_d]) and apart(path_b + path_b2, [path_d]) \
                and apart(path_a + path_b + path_b2 + path_d, b.paths, 4):
            return ultra, out, path_a, path_b, path_b2, path_d
    return None


def _maze_build(b, zone, corridor, ultra, out, path_a, path_b, path_b2, path_d):
    w = b.w
    D = b.depth_map(zone)
    for (x, y) in corridor:
        w.tiles[y][x] = "."
        w.zones[y][x] = zone
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if D.get(n, 0) >= 4 and n not in b.busy:
                w.tiles[n[1]][n[0]] = "."                   # a little wider where the forest is thick
                w.zones[n[1]][n[0]] = zone
    for (x, y) in corridor:
        b.carved |= {(x + dx, y + dy) for dx in range(-3, 4) for dy in range(-3, 4)}
    g_tile, g_stand = corridor[0], corridor[1]            # garden*: the stone you arrive by
    h_tile, h_stand = corridor[-1], corridor[-2]          # ...and the one far away, off the screen
    for t in (g_tile, h_tile, ultra[0], out[0]):
        w.tiles[t[1]][t[0]] = "Q"
    for t in (ultra[0], out[0]):
        b.entrances.append(t)
        b.busy.add(t)
    a0, b0, d0 = path_a[-1], path_b[0], path_d[-1]
    up = lambda p: (p[0], p[1] - 1)                        # a pale-only stone: just above its spot
    s = [_stone("maze_ultra", ultra[0], ultra[1], "ultra", zone),
         _stone("maze_out", out[0], out[1], "maze_out", zone),
         _stone("maze_garden_star", g_tile, g_stand, "garden_star", zone),
         _stone("maze_hidden", h_tile, h_stand, "garden_star_hidden", zone),
         _stone("maze_a_down", up(a0), a0, "a_down", zone, True, (NOWHERE, NOWHERE_SLOTS[NOWHERE][0][1])),
         _stone("maze_b_down", up(b0), b0, "b_down", zone, True, (NOWHERE, NOWHERE_SLOTS[NOWHERE][1][1])),
         _stone("maze_d_down", up(d0), d0, "d_down", zone, True, (NOWHERE2, NOWHERE_SLOTS[NOWHERE2][0][1]))]
    # loops: Nowhere's third stones lead back up into the middle of other pockets
    mid_a = path_a[len(path_a) // 2]
    s.append(_stone("maze_a_mid", _add(mid_a, (0, -2)), _add(mid_a, (0, -1)), "a_mid", zone, True,
                    (NOWHERE2, NOWHERE_SLOTS[NOWHERE2][2][1])))
    b.paths += [path_a, path_b, path_d]
    return {"role": "maze", "zone": zone, "centre": g_stand, "paths": [path_a, path_b, path_b2, path_d],
            "groups": ["A", "B", "B", "D"], "stones": s}


def _deep_stones(world):
    """Where the stones in Nowhere / Nowhere 2 lead (slot index -> target), from the cellar's maze."""
    maze = next((l for l in world.glitch_links if l["role"] == "maze"), None)
    if not maze:
        return {}
    st = {s["role"]: s for s in maze["stones"]}
    other = next((l for l in world.glitch_links if l["role"] == "item"), None) or \
        next((l for l in world.glitch_links if l["role"] != "maze"), None)
    loop = other["paths"][0][len(other["paths"][0]) // 3] if other else st["a_down"]["stand"]
    cellar = PALE_PREFIX + "cellar"
    return {NOWHERE: [(cellar, st["a_down"]["stand"]), (cellar, st["b_down"]["stand"]), (cellar, loop)],
            NOWHERE2: [(cellar, st["d_down"]["stand"]), (HASH, HashMap.ARRIVAL), (cellar, st["a_mid"]["stand"])],
            "loop": loop}


# --- the pale level: closed pockets ------------------------------------------------------------------------
class PaleWorld:
    """The pale version of a level: solid rock with a small pale pocket around every glitch path (same seed, same
    coordinates as the normal level)."""

    def __init__(self, level, base):
        self.level, self.base_level_name = PALE_PREFIX + level, level
        self.pale = True
        self.seed = base.seed
        self.width, self.height = base.width, base.height
        self._base_biome_at = base.biome_at
        self.tiles = [["M"] * self.width for _ in range(self.height)]
        self.zones = [[None] * self.width for _ in range(self.height)]
        self.gates, self.portals, self.npcs, self.pickups, self.structures = [], [], [], [], []
        self.hidden, self.locked, self.arrivals = {}, {}, {}
        self.glitches = []
        rnd = random.Random(f"pale3-{level}-{self.seed}")
        links = getattr(base, "glitch_links", [])
        pockets, self.owner = [], {}
        for link in links:                                             # 1. the pockets (terrain copied once)
            for path, group in zip(link["paths"], link.get("groups", [OPEN] * len(link["paths"]))):
                pockets.append((link, path, self._pocket(base, path, link["zone"], group)))
        stands = {tuple(s["stand"]) for l in links for s in l["stones"]}
        for link, path, pocket in pockets:                             # 2. a little wrong
            self._distort(rnd, pocket, stands, link["zone"])
        for link, path, pocket in pockets:                             # 3. the way through is always open
            for (x, y) in path:
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        c = (x + dx, y + dy)
                        if c in pocket and TILES[self.tiles[c[1]][c[0]]]["solid"]:
                            self.tiles[c[1]][c[0]] = FLOOR.get(link["zone"], ".")
        self._separate(pockets)                                        # the maze's pockets never touch each other
        deep = getattr(base, "deep_stones", {})
        for link in links:                                             # 4. the glitch stones
            for s in link["stones"]:
                self._put(s, link["zone"])
        if deep.get("loop"):                                           # Nowhere's loop stone comes up here
            p = deep["loop"]
            self._put(_stone("maze_loop", (p[0], p[1] - 1), p, "loop", "garden", True, (NOWHERE, NOWHERE_SLOTS[NOWHERE][2][1])),
                      "garden")
        st = [g["stand"] for g in self.glitches]
        self.player_start = st[0] if st else base.player_start

    def _put(self, s, zone):
        tx, ty = s["tile"]
        self.tiles[ty][tx] = "Q"
        self.zones[ty][tx] = zone
        sx, sy = s["stand"]
        if TILES[self.tiles[sy][sx]]["solid"] or not self.zones[sy][sx]:
            self.tiles[sy][sx] = FLOOR.get(zone, ".")
            self.zones[sy][sx] = zone
        self.glitches.append(dict(s))

    def biome_at(self, x, y):
        if not self.zones[y][x]:
            return None
        return self._base_biome_at(x, y) or ZONE_BIOMES.get(self.zones[y][x])     # (a pocket also runs through plain rock)

    def _separate(self, pockets):
        """A wall between pockets of different groups when one of them is a maze pocket (A / B / D): those are
        only joined by glitch stones, never by walking."""
        keep = set()
        for link, path, pocket in pockets:
            keep |= {(x + dx, y + dy) for (x, y) in path for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
        for c, g in list(self.owner.items()):
            if c in keep:
                continue
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    o = self.owner.get((c[0] + dx, c[1] + dy))
                    if o and o != g and (o != OPEN or g != OPEN):
                        self.tiles[c[1]][c[0]] = "M"
                        break
                else:
                    continue
                break

    def _pocket(self, base, path, zone, group=None):
        """Copies the normal terrain around the path (normal glitch stones become rock) and returns its cells."""
        cells = set()
        r = int(POCKET_R) + 1
        for (x, y) in path[::2] + [path[-1]]:
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    c = (x + dx, y + dy)
                    if c not in cells and math.hypot(dx, dy) <= POCKET_R and _inside(self, *c, 1):
                        cells.add(c)
        for (x, y) in cells:
            if self.zones[y][x]:
                continue                                                       # already part of another pocket
            self.owner[(x, y)] = group or OPEN
            ch = base.tiles[y][x]
            self.tiles[y][x] = "r" if ch == "Q" else "M" if ch == "|" else ch
            self.zones[y][x] = base.zones[y][x] or zone
        return cells

    def _distort(self, rnd, cells, protect, zone):
        """The slightly wrong terrain: decoration moved / gone / new."""
        for (x, y) in sorted(cells):
            if (x, y) in protect:
                continue
            ch = self.tiles[y][x]
            floor = FLOOR.get(self.zones[y][x], ".")
            if ch in DECOR:
                r = rnd.random()
                if r < 0.2:
                    self.tiles[y][x] = floor                                   # gone
                elif r < 0.35:
                    nx, ny = x + rnd.randint(-2, 2), y + rnd.randint(-2, 2)
                    if (nx, ny) in cells and (nx, ny) not in protect and self.tiles[ny][nx] in (".", "g", ",", "_"):
                        self.tiles[ny][nx], self.tiles[y][x] = ch, floor       # moved a little
            elif ch in (".", "g") and rnd.random() < 0.02:
                self.tiles[y][x] = NEW_DECOR.get(zone, "T")                    # something that wasn't there


# --- below: Nowhere, Nowhere 2, ### -------------------------------------------------------------------------
# Nowhere: a pale nothing of three lobes far apart (one stone in each, you can't see the others from one).
# slot = (stone tile, stand); the stones lead to the targets in the cellar's world.deep_stones.
# Nowhere 2 is one wide hall instead: you arrive at its left side and see the way out straight ahead (slot 2, a
# loop back up); the hall is bigger than the screen, and far away in its top right corner, out of sight, is the
# only stone down to ### (slot 1). Rock pillars break it up a little - open, but not a place to wander.
NOWHERE_SHAPES = {NOWHERE: (64, 46, [(14, 12), (50, 14), (30, 36)]),
                  NOWHERE2: (50, 36, [(10, 19), (43, 5), (20, 19)])}
HALL = (4, 3, 46, 32)                         # Nowhere 2: the hall's rough box (x0, y0, x1, y1)
HALL_PILLARS = 14
NOWHERE_SLOTS = {name: [((cx, cy - 1), (cx, cy)) for cx, cy in shape[2]] for name, shape in NOWHERE_SHAPES.items()}


def deep_targets(seed, build_cellar):
    if seed not in _SPECS:
        add_glitches("cellar", build_cellar(seed))
    return _SPECS.get(seed, {})


class NowhereMap:
    def __init__(self, seed, name, targets):
        self.level, self.pale, self.seed = name, True, seed
        w, h, lobes = NOWHERE_SHAPES[name]
        self.width, self.height = w, h
        self.tiles = [["M"] * w for _ in range(h)]
        self.zones = [[None] * w for _ in range(h)]
        rnd = random.Random(f"{name}-{seed}")
        def blob(cx, cy, r):
            for y in range(max(2, int(cy - r - 2)), min(h - 2, int(cy + r + 3))):
                for x in range(max(2, int(cx - r - 2)), min(w - 2, int(cx + r + 3))):
                    if math.hypot(x - cx, y - cy) + rnd.uniform(-0.9, 0.9) < r:
                        self.tiles[y][x], self.zones[y][x] = "_", "nowhere"
        if name == NOWHERE2:
            self._hall(rnd, lobes)
        for i, (cx, cy) in enumerate(lobes if name != NOWHERE2 else []):   # three lobes joined by thin winding ways
            blob(cx, cy, 6.5)
            nx, ny = lobes[(i + 1) % len(lobes)]
            steps = int(math.dist((cx, cy), (nx, ny)))
            bend = rnd.uniform(-6, 6)
            for k in range(steps + 1):
                t = k / steps
                px = cx + (nx - cx) * t + math.sin(t * math.pi) * bend * (ny - cy) / steps
                py = cy + (ny - cy) * t - math.sin(t * math.pi) * bend * (nx - cx) / steps
                blob(px, py, 1.6)
        self.gates, self.portals, self.npcs, self.pickups, self.structures = [], [], [], [], []
        self.hidden, self.locked, self.arrivals = {}, {}, {}
        self.glitches = []
        for i, ((tile, stand), target) in enumerate(zip(NOWHERE_SLOTS[name], targets or [])):
            self.tiles[tile[1]][tile[0]] = "Q"
            self.tiles[stand[1]][stand[0]] = "_"
            self.glitches.append(_stone(f"{name}_{i}", tile, stand, "down" if target[0] == HASH else "up", "nowhere",
                                        True, target))
        self.player_start = NOWHERE_SLOTS[name][0][1]

    def _hall(self, rnd, slots):
        x0, y0, x1, y1 = HALL
        for y in range(y0, y1):
            for x in range(x0, x1):
                edge = min(x - x0, x1 - 1 - x, y - y0, y1 - 1 - y)
                if edge >= 2 or rnd.random() < 0.35 + edge * 0.3:           # ragged walls
                    self.tiles[y][x], self.zones[y][x] = "_", "nowhere"
        stands = [(cx, cy) for cx, cy in slots]
        keep = {(x, y) for (sx, sy) in stands for x in range(sx - 2, sx + 3) for y in range(sy - 3, sy + 3)}
        keep |= {(x, y) for x in range(slots[0][0], slots[2][0] + 1) for y in range(slots[0][1] - 2, slots[0][1] + 3)}
        placed = 0
        for _ in range(200):                                   # pillars, but every stone stays reachable
            if placed >= HALL_PILLARS:
                break
            pw, ph = rnd.randint(2, 4), rnd.randint(2, 3)
            px, py = rnd.randint(x0 + 3, x1 - 3 - pw), rnd.randint(y0 + 3, y1 - 3 - ph)
            cells = [(x, y) for x in range(px, px + pw) for y in range(py, py + ph)]
            if any(c in keep or self.tiles[c[1]][c[0]] != "_" for c in cells):
                continue
            for x, y in cells:
                self.tiles[y][x] = "M"
            seen = _flood(self, [stands[0]])
            if all(st in seen for st in stands):
                placed += 1
            else:
                for x, y in cells:
                    self.tiles[y][x] = "_"

    def biome_at(self, x, y):
        return "nowhere" if self.zones[y][x] else None


class HashMap:
    """### - the bottom. No music, nearly black, "Not yet." on the floor and the Peace Gun. No stone back:
    taking the Pale Orb off is the only way out."""
    W, H = 30, 22
    ARRIVAL = (15, 15)

    def __init__(self, seed):
        self.level, self.pale, self.seed = HASH, False, seed
        self.width, self.height = self.W, self.H
        self.tiles = [["M"] * self.W for _ in range(self.H)]
        self.zones = [[None] * self.W for _ in range(self.H)]
        for y in range(self.H):
            for x in range(self.W):
                if math.hypot((x - 15) / 1.4, y - 11) < 7.5:
                    self.tiles[y][x], self.zones[y][x] = "_", "hash"
        self.gates, self.portals, self.npcs, self.structures = [], [], [], []
        self.pickups = [{"pos": (15, 9), "type": "item", "item": "Peace Gun"}]
        self.hidden, self.locked, self.arrivals, self.glitches = {}, {}, {}, []
        self.floor_text = [((15, 12), "Not yet.")]
        self.player_start = self.ARRIVAL

    def biome_at(self, x, y):
        return "###"                                     # (the rock around it too: all black)
