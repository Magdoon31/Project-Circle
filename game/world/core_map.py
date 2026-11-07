# CORE map: the "mechanical heart" - metal halls and chaotic corridors full of pipes, cables and machines.
#
#   cellar: garden exit --portal "core:entry"--> arrival hall (random place at the top)
#   random part: ~20 halls of different shapes, connected by bending corridors of different widths (many loops)
#   FIXED last section (prefabs/core_chamber.txt, at the bottom): the core, Milo in front of it,
#   behind it the portal down to the Void - sealed until Milo is beaten with the Peace Gun (game.py checks it).
#
# Not connected to the rest of the world by walking - only through the portals.
# Same interface as SurfaceMap / CellarMap (tiles, zones, gates, portals, pickups, npcs, arrivals, biome_at ...).

import math, random
from collections import deque
from game.world import loot
from game.world.noise import ValueNoise, coarse_field
from game.world.prefab import load_prefab, all_structures, rotate
from game.world.tiles import TILES, EMPTY
from game.world.terrain import _astar

WIDTH, HEIGHT = 130, 140

ZONES = {"core": "the_core"}

HALL_COUNT = 34
HALL_SIZE = (7, 15)                 # width / height range of one hall piece
BIG_HALL_SIZE = (14, 19)            # the first STRUCTURES halls are big enough for a structure
EXTRA_CORRIDORS = 0.45              # share of extra loops on top of the minimum (bigger = more chaotic)
STRUCTURES = 6                      # rooms inside the halls (prefabs with @biomes the_core) - they hold the items
GOLD_PILES = 18                     # loose gold in the halls (items only in structures - none in the Core yet)
CHAMBER = "core_chamber"            # the fixed last section
VOID_SEAL = "void_unlocked"         # flag (saved) that opens the portal to the Void
CUTTABLE = {"m", "k", "p"}          # clutter that may be removed when something must be made reachable
MARGIN = 3


class CoreMap:
    def __init__(self, seed):
        self.seed = seed
        self.used_seed = seed
        self.width, self.height = WIDTH, HEIGHT
        self.rnd = random.Random(f"core-{seed}")
        self.zones = [[None] * WIDTH for _ in range(HEIGHT)]
        self.tiles = [["#"] * WIDTH for _ in range(HEIGHT)]
        self.gates, self.portals, self.pickups, self.npcs, self.structures = [], [], [], [], []
        self.protected = set()
        self.structure_cells = set()       # walls of the fixed chamber - never cut
        self.prefab_cells = set()
        self.arrivals = {}
        self.wiggle = coarse_field(ValueNoise(seed * 13 + 1), 7, WIDTH, HEIGHT)
        self._place_chamber()
        self._make_halls()
        self._connect_halls()
        self._make_arrival()
        self._place_structures()
        self._decorate()
        self._place_gold()
        self._set_zones()
        self.paths_cut = self._ensure_reachable()
        self.player_start = self.arrivals["cellar:garden"]

    def biome_at(self, x, y):
        zone = self.zones[y][x]
        return ZONES[zone] if zone else None

    def walkable(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height and not TILES[self.tiles[y][x]]["solid"]

    def inside(self, x, y, margin=MARGIN):
        return margin <= x < WIDTH - margin and margin <= y < HEIGHT - margin

    # --- the fixed last section ------------------------------------------------------------
    def _place_chamber(self):
        prefab = load_prefab(CHAMBER)
        ox = WIDTH // 2 - prefab.width // 2 + self.rnd.randint(-8, 8)
        oy = HEIGHT - prefab.height - MARGIN
        self.chamber_rect = (ox, oy, prefab.width, prefab.height)
        for y in range(prefab.height):
            for x in range(prefab.width):
                tile = prefab.tile_at(x, y)
                if tile != EMPTY:
                    self.tiles[oy + y][ox + x] = tile
                    self.structure_cells.add((ox + x, oy + y))
                    self.prefab_cells.add((ox + x, oy + y))
                    self.protected.add((ox + x, oy + y))
        (ex, ey), = prefab.markers_in_order("exit")
        (bx, by), = prefab.markers_in_order("boss")
        (px, py), = prefab.markers_in_order("portal")
        self.chamber_door = (ox + ex, oy + ey)
        boss = (ox + bx, oy + by)
        # Milo: no gate to open - beating him (with the Peace Gun) unseals the Void portal instead
        self.gates.append({"from": "core", "to": "core", "pos": boss, "cells": [], "boss": boss,
                           "entry": (ox + ex, oy + ey + 2), "name": "Milo"})
        self.portals.append({"zone": "core", "pos": (ox + px, oy + py), "leads_to": "void:entry", "sealed": VOID_SEAL})
        self.arrivals["void:void"] = (ox + px, oy + py - 2)          # coming back up from the Void
        # a small hall in front of the door, so the corridors meet there
        self.door_hall = (ox + ex - 4, oy - 7, 9, 6)
        self._carve_rect(self.door_hall, "_")
        for y in range(oy - 1, oy + 1):
            for dx in (-1, 0, 1):
                self.tiles[y][ox + ex + dx] = "_"
        self._protect_rect(self.door_hall)

    def _in_chamber(self, x, y, margin=0):
        cx, cy, cw, ch = self.chamber_rect
        return cx - margin <= x < cx + cw + margin and cy - margin <= y < cy + ch + margin

    # --- halls ------------------------------------------------------------------------------
    def _carve_rect(self, rect, floor):
        x0, y0, w, h = rect
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                if self.inside(x, y) and (x, y) not in self.structure_cells:
                    self.tiles[y][x] = floor

    def _carve_circle(self, cx, cy, r, floor):
        for y in range(int(cy - r) - 1, int(cy + r) + 2):
            for x in range(int(cx - r) - 1, int(cx + r) + 2):
                if self.inside(x, y) and (x, y) not in self.structure_cells and math.hypot(x - cx, y - cy) <= r:
                    self.tiles[y][x] = floor

    def _protect_rect(self, rect):
        x0, y0, w, h = rect
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                self.protected.add((x, y))

    def _make_halls(self):
        """Halls of mixed shapes: plain, L / cross (two rects), round, and pillared. They may touch each other."""
        halls = []
        for _ in range(3000):
            if len(halls) >= HALL_COUNT:
                break
            size = BIG_HALL_SIZE if len(halls) < STRUCTURES else HALL_SIZE     # some big halls for the structures
            w, h = self.rnd.randint(*size), self.rnd.randint(*size)
            x = self.rnd.randint(MARGIN + 1, WIDTH - w - MARGIN - 1)
            y = self.rnd.randint(MARGIN + 1, HEIGHT - h - MARGIN - 1)
            rect = (x, y, w, h)
            if self._rect_hits_chamber(rect, 4):
                continue
            if all(x + w + 2 <= hx or hx + hw + 2 <= x or y + h + 2 <= hy or hy + hh + 2 <= y for hx, hy, hw, hh in halls):
                halls.append(rect)
        self.halls = halls
        for rect in halls:
            x, y, w, h = rect
            floor = self.rnd.choice(["g"] * 5 + ["_"])     # "_" = metal plates, no random fights there
            shape = self.rnd.choice(["rect", "rect", "L", "cross", "round", "pillars"])
            if shape == "round":
                self._carve_circle(x + w / 2, y + h / 2, min(w, h) / 2, floor)
            elif shape == "L":
                self._carve_rect((x, y, w, max(3, h // 2)), floor)
                side = x if self.rnd.random() < 0.5 else x + w - max(3, w // 2)
                self._carve_rect((side, y, max(3, w // 2), h), floor)
            elif shape == "cross":
                self._carve_rect((x, y + h // 3, w, max(3, h // 3)), floor)
                self._carve_rect((x + w // 3, y, max(3, w // 3), h), floor)
            else:
                self._carve_rect(rect, floor)
                if shape == "pillars" and w >= 9 and h >= 9:
                    for py in range(y + 2, y + h - 2, 3):
                        for px in range(x + 2, x + w - 2, 3):
                            self.tiles[py][px] = "#"
        self.hall_centres = [self._hall_centre(r) for r in halls]

    def _hall_centre(self, rect):
        x, y, w, h = rect
        cx, cy = x + w // 2, y + h // 2
        # the centre of an L / cross / pillared hall may be a wall: take the nearest floor tile
        if self.walkable(cx, cy):
            return cx, cy
        floor = [(tx, ty) for ty in range(y, y + h) for tx in range(x, x + w) if self.walkable(tx, ty)]
        return min(floor, key=lambda c: math.dist(c, (cx, cy)))

    def _rect_hits_chamber(self, rect, margin):
        x, y, w, h = rect
        cx, cy, cw, ch = self.chamber_rect
        dx, dy, dw, dh = self.door_hall if hasattr(self, "door_hall") else (cx, cy, cw, ch)
        cy, ch = min(cy, dy), max(cy + ch, dy + dh) - min(cy, dy)
        return not (x + w + margin <= cx or cx + cw + margin <= x or y + h + margin <= cy or cy + ch + margin <= y)

    # --- corridors ----------------------------------------------------------------------------
    def _corridor(self, a, b, radius):
        """Bending corridor (noise makes the path wander), radius 0.6 .. 2 = 1 .. 4 tiles wide."""
        def cost(x, y):
            if not self.inside(x, y, 2) or (x, y) in self.structure_cells:
                return None
            if self.walkable(x, y):
                return 1
            return 2 + max(0.0, self.wiggle[y][x] + 0.4) * 10
        path = _astar(self, a, b, cost) or []
        r = int(math.ceil(radius))
        for x, y in path:
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    nx, ny = x + dx, y + dy
                    if dx * dx + dy * dy <= radius * radius + 0.01 and self.inside(nx, ny) \
                            and (nx, ny) not in self.structure_cells and not self.walkable(nx, ny):
                        self.tiles[ny][nx] = "g"
        return path

    def _connect_halls(self):
        nodes = self.hall_centres + [self._door_hall_centre()]
        connected, edges = {0}, []
        while len(connected) < len(nodes):
            a, b = min(((i, j) for i in connected for j in range(len(nodes)) if j not in connected),
                       key=lambda e: math.dist(nodes[e[0]], nodes[e[1]]))
            edges.append((a, b))
            connected.add(b)
        others = sorted(((i, j) for i in range(len(nodes)) for j in range(i + 1, len(nodes))
                         if (i, j) not in edges and (j, i) not in edges),
                        key=lambda e: math.dist(nodes[e[0]], nodes[e[1]]))
        edges += others[:int(len(nodes) * EXTRA_CORRIDORS)]
        for a, b in edges:
            self._corridor(nodes[a], nodes[b], self.rnd.choice([0.6, 1.0, 1.0, 1.5, 2.0]))

    def _door_hall_centre(self):
        x, y, w, h = self.door_hall
        return x + w // 2, y + h // 2

    # --- arrival from the Garden -----------------------------------------------------------
    def _make_arrival(self):
        # the hall farthest from the core chamber (random among the far ones)
        far = sorted(range(len(self.halls)), key=lambda i: -math.dist(self.hall_centres[i], self.chamber_door))
        i = self.rnd.choice(far[:4])
        pos = self.hall_centres[i]
        self.portals.append({"zone": "core", "pos": pos, "leads_to": "cellar:garden"})
        arrival = next(((pos[0] + dx, pos[1] + dy) for dx, dy in ((0, 2), (0, -2), (2, 0), (-2, 0))
                        if self.walkable(pos[0] + dx, pos[1] + dy)), (pos[0], pos[1] + 2))
        self.tiles[arrival[1]][arrival[0]] = "g" if not self.walkable(*arrival) else self.tiles[arrival[1]][arrival[0]]
        self.arrivals["cellar:garden"] = arrival
        for y in range(pos[1] - 3, pos[1] + 4):
            for x in range(pos[0] - 3, pos[0] + 4):
                self.protected.add((x, y))

    # --- structures: small rooms standing inside the halls ------------------------------------
    def _place_structures(self):
        prefabs = [p for p in all_structures() if "the_core" in p.list_setting("biomes")]
        if not prefabs:
            return
        uses = {}
        for _ in range(4000):
            if len(self.structures) >= STRUCTURES:
                break
            prefab = rotate(self.rnd.choice(prefabs), self.rnd.randrange(4))     # any side can face the hall
            limit = 1 if prefab.list_setting("npcs") else 2
            if uses.get(prefab.name, 0) >= limit:
                continue
            hx, hy, hw, hh = self.rnd.choice(self.halls)
            if hw < prefab.width + 2 or hh < prefab.height + 2:
                continue
            ox = self.rnd.randint(hx + 1, hx + hw - prefab.width - 1)
            oy = self.rnd.randint(hy + 1, hy + hh - prefab.height - 1)
            # the room + a free ring of 1 tile around it must be open floor (not touching walls or other rooms)
            ring = [(ox + x, oy + y) for y in range(-1, prefab.height + 1) for x in range(-1, prefab.width + 1)]
            if not all(self.walkable(x, y) and (x, y) not in self.protected and (x, y) not in self.structure_cells for x, y in ring):
                continue
            self._stamp(prefab, ox, oy)
            self.protected.update(ring)
            self.structures.append({"name": prefab.name, "zone": "core", "rect": (ox, oy, prefab.width, prefab.height)})
            uses[prefab.name] = uses.get(prefab.name, 0) + 1

    def _stamp(self, prefab, ox, oy):
        for y in range(prefab.height):
            for x in range(prefab.width):
                tile = prefab.tile_at(x, y)
                if tile != EMPTY:
                    self.tiles[oy + y][ox + x] = tile
                    self.structure_cells.add((ox + x, oy + y))
                    self.prefab_cells.add((ox + x, oy + y))
                    self.protected.add((ox + x, oy + y))
        gold = prefab.list_setting("gold")
        for (x, y) in prefab.markers_in_order("gold"):
            if gold:
                lo, hi = (int(v) for v in gold[0].split("-"))
                amount = self.rnd.randint(lo, hi)
            else:
                amount = loot.roll_gold("the_core", self.rnd)
            self.pickups.append({"pos": (ox + x, oy + y), "type": "gold", "amount": amount})
        placed = {p["item"] for p in self.pickups if p["type"] == "item"}
        for (x, y), entry in zip(prefab.markers_in_order("item"), prefab.list_setting("items")):
            item = loot.roll_item("the_core", self.rnd, placed) if entry == "random" else entry
            placed.add(item)
            self.pickups.append({"pos": (ox + x, oy + y), "type": "item", "item": item})
        for (x, y), npc_id in zip(prefab.markers_in_order("npc"), prefab.list_setting("npcs")):
            self.npcs.append({"pos": (ox + x, oy + y), "id": npc_id, "zone": "core"})

    # --- decoration ----------------------------------------------------------------------------
    def _decorate(self):
        s = self.seed
        cables = coarse_field(ValueNoise(s * 13 + 2), 9, WIDTH, HEIGHT)
        pipes = coarse_field(ValueNoise(s * 13 + 3), 6, WIDTH, HEIGHT)
        machines = coarse_field(ValueNoise(s * 13 + 4), 5, WIDTH, HEIGHT)
        near = set()
        for x, y in self.protected:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    near.add((x + dx, y + dy))
        for y in range(HEIGHT):
            for x in range(WIDTH):
                t = self.tiles[y][x]
                if (x, y) in self.structure_cells or (x, y) in near or TILES[t]["solid"]:
                    continue
                walls = sum(1 for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)) if self.tiles[ny][nx] == "#")
                open8 = sum(1 for dx in (-1, 0, 1) for dy in (-1, 0, 1) if self.walkable(x + dx, y + dy))
                if walls == 1 and open8 >= 6 and pipes[y][x] > 0.05:
                    self.tiles[y][x] = "p"                       # pipes along the walls of the halls
                elif abs(cables[y][x]) < 0.035:
                    self.tiles[y][x] = "e"                       # glowing cable lines across the floor
                elif open8 == 9 and machines[y][x] > 0.38:
                    self.tiles[y][x] = "m"                       # machine blocks in the middle of halls
                elif open8 == 9 and self.rnd.random() < 0.012:
                    self.tiles[y][x] = "k"

    # --- gold -------------------------------------------------------------------------------
    def _place_gold(self):
        floor = [(x, y) for y in range(HEIGHT) for x in range(WIDTH)
                 if self.walkable(x, y) and (x, y) not in self.protected and not self._in_chamber(x, y, 2)]
        spots = []
        for _ in range(3000):
            if len(spots) >= GOLD_PILES or not floor:
                break
            c = self.rnd.choice(floor)
            if all(math.dist(c, o) >= 14 for o in spots):
                spots.append(c)
        for pos in spots:
            self.pickups.append({"pos": pos, "type": "gold", "amount": loot.roll_gold("the_core", self.rnd)})

    # --- zones: floor + the walls around it ---------------------------------------------------
    def _set_zones(self):
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if self.walkable(x, y) or (x, y) in self.prefab_cells or self.tiles[y][x] in ("p", "m", "k"):
                    for dy in (-2, -1, 0, 1, 2):
                        for dx in (-2, -1, 0, 1, 2):
                            if 0 <= x + dx < WIDTH and 0 <= y + dy < HEIGHT:
                                self.zones[y + dy][x + dx] = "core"
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if self.zones[y][x] is None:
                    self.tiles[y][x] = "M"                       # nothing out there

    # --- reachability -------------------------------------------------------------------------
    def important_points(self):
        pts = [p["pos"] for p in self.pickups] + [p["pos"] for p in self.portals] + list(self.arrivals.values())
        pts += [g["boss"] for g in self.gates] + [g["entry"] for g in self.gates] + [n["pos"] for n in self.npcs]
        return pts

    def flood(self, start, gates_open=True):
        seen, queue = {start}, deque([start])
        while queue:
            x, y = queue.popleft()
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                nx, ny = n
                if n in seen or not (0 <= nx < WIDTH and 0 <= ny < HEIGHT):
                    continue
                t = self.tiles[ny][nx]
                if (t == "|" and gates_open) or (t != "|" and not TILES[t]["solid"]):
                    seen.add(n)
                    queue.append(n)
        return seen

    def _ensure_reachable(self):
        """Something important can't be reached -> cut a path through the clutter (or the rock between halls)."""
        fixed = 0
        for _ in range(60):
            reach = self.flood(self.arrivals["cellar:garden"])
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
                    return None
                return 4 if t in CUTTABLE else (12 if t == "#" and self.inside(x, y) else None)
            path = _astar(self, start, target, cost)
            if not path:
                raise RuntimeError(f"core: cannot reach {target}")
            for x, y in path:
                if TILES[self.tiles[y][x]]["solid"] and (x, y) not in self.structure_cells:
                    self.tiles[y][x] = "g"
                    self.zones[y][x] = "core"
            fixed += 1
        raise RuntimeError("core: reachability fix did not finish")
