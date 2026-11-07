# VOID map: a labyrinth that does not look like one.
#
# The Void looks like wide, open, dark-violet land. In reality it is split into ISLANDS by thin
# chasms (cracks of nothing). You can see across a chasm, but you can't cross it - only narrow
# bridges connect the islands, and they form a MAZE (a spanning tree = many dead ends, few loops).
#
#   core: behind the core --portal "void:entry"--> entrance island (portal back up to the Core)
#   Void boss: on the island FARTHEST from the entrance (counted along the bridges, not in a straight line)
#
# Same interface as SurfaceMap / CellarMap / CoreMap.

import math, random
from collections import deque
from game.world import loot
from game.world.noise import ValueNoise, coarse_field
from game.world.tiles import TILES, EMPTY
from game.world.prefab import all_structures
from game.world.terrain import _astar

WIDTH, HEIGHT = 156, 150

ZONES = {"void": "the_void"}

ANCHORS = [(52, 50, 38), (104, 46, 36), (78, 78, 40), (46, 108, 35), (108, 106, 36)]   # x, y, r - overall shape
ISLANDS = 62                  # number of islands (more = smaller islands, longer maze)
CHASM_WIDTH = (0.9, 2.4)      # how wide the cracks between islands are (varies along the crack)
EXTRA_BRIDGES = 0.06          # share of extra bridges on top of the maze (loops); small = more dead ends
GOLD_PILES = 16               # gold - mostly at dead ends (a small reward for getting lost)
BOSS_NAME_TAG = "Void"        # gate "name" -> game.py knows which ending to show
BRANCHING = 0.6              # 1.0 = one long path with few branches, lower = more side branches / dead ends
CUTTABLE = {"T", "r"}
SHRINE = "void_shrine"        # ONE structure about halfway along the way to the boss (2 items + Milo)


class VoidMap:
    def __init__(self, seed):
        self.seed = seed
        self.used_seed = seed
        self.width, self.height = WIDTH, HEIGHT
        self.rnd = random.Random(f"void-{seed}")
        self.zones = [["void"] * WIDTH for _ in range(HEIGHT)]   # all of it is the Void - outside the land is the abyss "M"
        self.tiles = [["M"] * WIDTH for _ in range(HEIGHT)]
        self.gates, self.portals, self.pickups, self.npcs, self.structures = [], [], [], [], []
        self.protected = set()
        self.structure_cells = set()
        self.prefab_cells = set()
        self.arrivals = {}
        self._make_shape()
        self._make_islands()
        self._make_maze()
        self._place_entrance_and_boss()
        self._place_shrine()
        self._decorate()
        self._place_gold()
        self.paths_cut = self._ensure_reachable()
        self.player_start = self.arrivals["core:core"]

    def biome_at(self, x, y):
        zone = self.zones[y][x]
        return ZONES[zone] if zone else None

    def walkable(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height and not TILES[self.tiles[y][x]]["solid"]

    # --- overall shape ------------------------------------------------------------------------
    def _make_shape(self):
        s = self.seed
        warp_x = coarse_field(ValueNoise(s * 17 + 1), 30, WIDTH, HEIGHT)
        warp_y = coarse_field(ValueNoise(s * 17 + 2), 30, WIDTH, HEIGHT)
        self.region = set()
        for y in range(3, HEIGHT - 3):
            for x in range(3, WIDTH - 3):
                wx, wy = x + warp_x[y][x] * 16, y + warp_y[y][x] * 16
                if min(math.hypot(wx - cx, wy - cy) / r for cx, cy, r in ANCHORS) < 1.0:
                    self.region.add((x, y))

    # --- islands (warped Voronoi cells) -----------------------------------------------------------
    def _make_islands(self):
        s = self.seed
        region = sorted(self.region)
        centres = []
        for _ in range(20000):
            if len(centres) >= ISLANDS:
                break
            c = self.rnd.choice(region)
            if all(math.dist(c, o) >= 11 for o in centres):
                centres.append(c)
        self.centres = centres
        warp_x = coarse_field(ValueNoise(s * 17 + 3), 9, WIDTH, HEIGHT)
        warp_y = coarse_field(ValueNoise(s * 17 + 4), 9, WIDTH, HEIGHT)
        width = coarse_field(ValueNoise(s * 17 + 5), 6, WIDTH, HEIGHT)
        self.owner = {}                 # tile -> island index (floor tiles only)
        self.neighbours = [set() for _ in centres]
        border_pairs = {}               # (a, b) -> chasm tiles between islands a and b
        for x, y in region:
            wx, wy = x + warp_x[y][x] * 4, y + warp_y[y][x] * 4       # wobbly borders = natural cracks
            d = sorted((math.hypot(wx - cx, wy - cy), i) for i, (cx, cy) in enumerate(centres))[:2]
            (d1, a), (d2, b) = d
            self.zones[y][x] = "void"
            gap = CHASM_WIDTH[0] + (CHASM_WIDTH[1] - CHASM_WIDTH[0]) * (width[y][x] * 0.5 + 0.5)
            if d2 - d1 < gap:
                self.tiles[y][x] = "~"          # chasm: a crack of nothing (solid)
                key = (min(a, b), max(a, b))
                border_pairs.setdefault(key, []).append((x, y))
            else:
                self.tiles[y][x] = "."
                self.owner[(x, y)] = a
        # two islands touching directly (the crack got too thin there) -> close the gap
        for (x, y), a in list(self.owner.items()):
            for n in ((x + 1, y), (x, y + 1), (x + 1, y + 1), (x + 1, y - 1)):
                b = self.owner.get(n)
                if b is not None and b != a and (x, y) in self.owner:
                    self.tiles[y][x] = "~"
                    del self.owner[(x, y)]
                    border_pairs.setdefault((min(a, b), max(a, b)), []).append((x, y))
        # islands are neighbours only if they share a long enough crack (a corner touch doesn't count)
        self.borders = {k: v for k, v in border_pairs.items() if len(v) >= 6}
        for a, b in self.borders:
            self.neighbours[a].add(b)
            self.neighbours[b].add(a)
        # edge of the whole Void: the abyss itself (darker than the cracks)
        for x, y in region:
            if any((x + dx, y + dy) not in self.region for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                self.tiles[y][x] = "M"
                self.owner.pop((x, y), None)

    # --- the maze: bridges between islands -----------------------------------------------------
    def _make_maze(self):
        n = len(self.centres)
        start = min(range(n), key=lambda i: self.centres[i][1])       # top island (any island works)
        seen, stack, tree = {start}, [start], []
        # "growing tree" maze: mostly continues the newest path (long winding ways),
        # sometimes branches off an older island (side branches = dead ends to get lost in)
        while stack:
            k = len(stack) - 1 if self.rnd.random() < BRANCHING else self.rnd.randrange(len(stack))
            cur = stack[k]
            options = [b for b in self.neighbours[cur] if b not in seen]
            if not options:
                stack.pop(k)
                continue
            nxt = self.rnd.choice(options)
            seen.add(nxt)
            tree.append((cur, nxt))
            stack.append(nxt)
        self.reached_islands = seen
        edges = set((min(a, b), max(a, b)) for a, b in tree)
        others = [k for k in self.borders if k not in edges and k[0] in seen and k[1] in seen]
        self.rnd.shuffle(others)
        edges |= set(others[:int(len(edges) * EXTRA_BRIDGES)])
        self.bridges = edges
        self.graph = [set() for _ in range(n)]
        for a, b in edges:
            self.graph[a].add(b)
            self.graph[b].add(a)
            self._bridge(a, b)
        # islands the maze could not reach (cut off by the shape) are turned into abyss
        for (x, y), i in list(self.owner.items()):
            if i not in seen:
                self.tiles[y][x] = "M"
                del self.owner[(x, y)]

    def _bridge(self, a, b):
        """A narrow bridge across the crack between islands a and b (1-2 tiles wide)."""
        crack = self.borders[(min(a, b), max(a, b))]
        mid = crack[len(crack) // 2] if len(crack) < 3 else self.rnd.choice(crack[len(crack) // 4: 3 * len(crack) // 4 + 1])
        def floor_of(i):
            return min((c for c, o in self.owner.items() if o == i and math.dist(c, mid) < 8),
                       key=lambda c: math.dist(c, mid), default=self.centres[i])
        pa, pb = floor_of(a), floor_of(b)
        crack_set = set(crack)
        def safe(x, y):
            # a bridge tile may only touch islands a and b - otherwise it would open a shortcut to a third island
            return (x, y) in crack_set and all(self.owner.get(n) in (None, a, b)
                                               for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
        def cost(x, y):
            if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
                return None
            o = self.owner.get((x, y))
            if o is not None:
                return 1 if o in (a, b) else None
            return 3 if safe(x, y) else None
        path = _astar(self, pa, pb, cost) or []
        if not path:
            self.failed_bridges = getattr(self, "failed_bridges", 0) + 1
        wide = self.rnd.random() < 0.3
        for x, y in path:
            for dx, dy in ((0, 0), (1, 0), (0, 1)) if wide else ((0, 0),):
                if self.tiles[y + dy][x + dx] == "~" and safe(x + dx, y + dy):
                    self.tiles[y + dy][x + dx] = "="
        self.protected.update(path)

    # --- entrance + boss -----------------------------------------------------------------------
    def _island_tiles(self, i):
        return [c for c, o in self.owner.items() if o == i]

    def _island_core(self, i):
        # the tile of the island farthest from its cracks (the middle of the island)
        tiles = set(self._island_tiles(i))
        best, best_d = None, -1
        cx, cy = self.centres[i]
        for c in tiles:
            d = 0
            while d < 6 and all((c[0] + dx, c[1] + dy) in tiles for dx in range(-d - 1, d + 2) for dy in (-d - 1, d + 1)) \
                    and all((c[0] + dx, c[1] + dy) in tiles for dy in range(-d - 1, d + 2) for dx in (-d - 1, d + 1)):
                d += 1
            if d > best_d or (d == best_d and math.dist(c, (cx, cy)) < math.dist(best, (cx, cy))):
                best, best_d = c, d
        return best

    def _place_entrance_and_boss(self):
        islands = sorted(self.reached_islands)
        # entrance: an island on the edge of the maze (a random one of the outer ones)
        mid = (WIDTH / 2, HEIGHT / 2)
        outer = sorted(islands, key=lambda i: -math.dist(self.centres[i], mid))
        self.entrance_island = self.rnd.choice(outer[:8])
        pos = self._island_core(self.entrance_island)
        self.portals.append({"zone": "void", "pos": pos, "leads_to": "core:void"})
        arrival = next((p for p in ((pos[0], pos[1] + 2), (pos[0], pos[1] - 2), (pos[0] + 2, pos[1]), (pos[0] - 2, pos[1]))
                        if self.owner.get(p) == self.entrance_island), pos)
        self.arrivals["core:core"] = arrival
        self._protect(pos, 3)
        # boss: the island farthest from the entrance ALONG THE BRIDGES
        dist = {self.entrance_island: 0}
        queue = deque([self.entrance_island])
        while queue:
            cur = queue.popleft()
            for nxt in self.graph[cur]:
                if nxt not in dist:
                    dist[nxt] = dist[cur] + 1
                    queue.append(nxt)
        self.island_depth = dist
        self.boss_island = max(dist, key=lambda i: (dist[i], len(self._island_tiles(i))))
        boss = self._island_core(self.boss_island)
        # a ring of crystals around the boss (decoration, open on all sides)
        for a in range(0, 360, 30):
            x, y = round(boss[0] + math.cos(math.radians(a)) * 4), round(boss[1] + math.sin(math.radians(a)) * 4)
            if self.owner.get((x, y)) == self.boss_island and (a // 30) % 3 != 0:
                self.tiles[y][x] = "T"
        self.gates.append({"from": "void", "to": "void", "pos": boss, "cells": [], "boss": boss,
                           "entry": boss, "name": BOSS_NAME_TAG})
        self._protect(boss, 2)

    # --- the shrine halfway to the boss -----------------------------------------------------------
    def _place_shrine(self):
        prefab = next((p for p in all_structures() if p.name == SHRINE), None)
        if prefab is None:
            return
        # the islands on the way from the entrance to the boss (along the bridges)
        parent = {self.entrance_island: None}
        queue = deque([self.entrance_island])
        while queue:
            cur = queue.popleft()
            for nxt in self.graph[cur]:
                if nxt not in parent:
                    parent[nxt] = cur
                    queue.append(nxt)
        way, cur = [], self.boss_island
        while cur is not None:
            way.append(cur)
            cur = parent[cur]
        way.reverse()
        half = len(way) // 2
        # the middle island first, then its neighbours on the way (an island must be big enough)
        for i in sorted(range(1, len(way) - 1), key=lambda k: abs(k - half)):
            island = way[i]
            tiles = set(self._island_tiles(island))
            cx, cy = self._island_core(island)
            spots = sorted(tiles, key=lambda c: math.dist(c, (cx, cy)))[:60]
            for sx, sy in spots:
                ox, oy = sx - prefab.width // 2, sy - prefab.height // 2
                cells = [(ox + x, oy + y) for y in range(prefab.height) for x in range(prefab.width) if prefab.rows[y][x] != EMPTY]
                ring = {(x + dx, y + dy) for x, y in cells for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
                if all(c in tiles and c not in self.protected for c in ring):
                    self._stamp_shrine(prefab, ox, oy)
                    self.protected.update(ring)
                    self.shrine_island = island
                    self.shrine_step = (i, len(way) - 1)          # bridges from the entrance / to the boss island
                    return
        raise RuntimeError("void: no island on the way to the boss fits the shrine")

    def _stamp_shrine(self, prefab, ox, oy):
        for y in range(prefab.height):
            for x in range(prefab.width):
                tile = prefab.tile_at(x, y)
                if tile != EMPTY:
                    self.tiles[oy + y][ox + x] = tile
                    self.structure_cells.add((ox + x, oy + y))
                    self.prefab_cells.add((ox + x, oy + y))
        placed = set()
        for (x, y), entry in zip(prefab.markers_in_order("item"), prefab.list_setting("items")):
            item = loot.roll_item("the_void", self.rnd, placed) if entry == "random" else entry
            placed.add(item)
            self.pickups.append({"pos": (ox + x, oy + y), "type": "item", "item": item})
        for (x, y), npc_id in zip(prefab.markers_in_order("npc"), prefab.list_setting("npcs")):
            self.npcs.append({"pos": (ox + x, oy + y), "id": npc_id, "zone": "void"})
        self.structures.append({"name": prefab.name, "zone": "void", "rect": (ox, oy, prefab.width, prefab.height)})

    def _protect(self, centre, r):
        for y in range(centre[1] - r, centre[1] + r + 1):
            for x in range(centre[0] - r, centre[0] + r + 1):
                self.protected.add((x, y))

    # --- decoration ----------------------------------------------------------------------------
    def _decorate(self):
        s = self.seed
        glow = coarse_field(ValueNoise(s * 17 + 6), 7, WIDTH, HEIGHT)
        crystals = coarse_field(ValueNoise(s * 17 + 7), 5, WIDTH, HEIGHT)
        ash = coarse_field(ValueNoise(s * 17 + 8), 11, WIDTH, HEIGHT)
        for (x, y) in self.owner:
            if (x, y) in self.protected or self.tiles[y][x] != ".":
                continue
            near_crack = any(self.tiles[y + dy][x + dx] in ("~", "M", "=") for dx in (-1, 0, 1) for dy in (-1, 0, 1))
            if not near_crack and crystals[y][x] > 0.42:
                self.tiles[y][x] = "T"          # crystal clusters (solid)
            elif glow[y][x] > 0.30:
                self.tiles[y][x] = "*"          # glowing violet patches
            elif ash[y][x] > 0.25:
                self.tiles[y][x] = "x"
            elif not near_crack and self.rnd.random() < 0.008:
                self.tiles[y][x] = "r"

    # --- gold: mostly at dead ends -------------------------------------------------------------
    def _place_gold(self):
        dead_ends = [i for i in self.reached_islands if len(self.graph[i]) == 1
                     and i not in (self.entrance_island, self.boss_island)]
        self.rnd.shuffle(dead_ends)
        others = [i for i in self.reached_islands if i not in dead_ends and i not in (self.entrance_island, self.boss_island)]
        self.rnd.shuffle(others)
        skip = getattr(self, "shrine_island", None)
        for i in [i for i in dead_ends + others if i != skip][:GOLD_PILES]:
            spot = self._island_core(i)
            if spot and self.walkable(*spot):
                self.pickups.append({"pos": spot, "type": "gold", "amount": loot.roll_gold("the_void", self.rnd)})

    # --- reachability -------------------------------------------------------------------------
    def important_points(self):
        pts = [p["pos"] for p in self.pickups] + [p["pos"] for p in self.portals] + list(self.arrivals.values())
        pts += [g["boss"] for g in self.gates] + [n["pos"] for n in self.npcs]
        return pts

    def flood(self, start, gates_open=True):
        seen, queue = {start}, deque([start])
        while queue:
            x, y = queue.popleft()
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                nx, ny = n
                if n in seen or not (0 <= nx < WIDTH and 0 <= ny < HEIGHT):
                    continue
                if not TILES[self.tiles[ny][nx]]["solid"]:
                    seen.add(n)
                    queue.append(n)
        return seen

    def _ensure_reachable(self):
        """Something can't be reached (crystals in the way on an island) -> cut them. Never adds bridges."""
        fixed = 0
        for _ in range(60):
            reach = self.flood(self.arrivals["core:core"])
            missing = [p for p in self.important_points() if p not in reach]
            if not missing:
                return fixed
            target = missing[0]
            start = min(reach, key=lambda c: abs(c[0] - target[0]) + abs(c[1] - target[1]))
            def cost(x, y):
                t = self.tiles[y][x]
                if not TILES[t]["solid"] or (x, y) == target:
                    return 1
                if (x, y) in self.structure_cells:
                    return None                  # never through the shrine's walls
                return 3 if t in CUTTABLE else (40 if t == "~" else None)
            path = _astar(self, start, target, cost)
            if not path:
                raise RuntimeError(f"void: cannot reach {target}")
            for x, y in path:
                t = self.tiles[y][x]
                if t in CUTTABLE:
                    self.tiles[y][x] = "."
                elif t == "~":
                    self.tiles[y][x] = "="       # last resort: an extra bridge
            fixed += 1
        raise RuntimeError("void: reachability fix did not finish")
