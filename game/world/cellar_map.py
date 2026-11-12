# CELLAR map (underground): a huge UNDERGROUND GARDEN cave with the FACTORY as a square block inside it.
#
#   surface: separated village --portal--> factory (a random hall, far from the boss hall)
#   factory: halls + corridors ... boss hall --gate "||" (factory boss) on a RANDOM side--> tunnel --> garden
#   surface: area behind the tundra boss --portal--> garden (random place)
#   garden:  ... garden boss --gate--> walled chamber with the portal up to the Core (random place, not near entrances)
#
# Same interface as SurfaceMap (tiles, zones, gates, portals, pickups, npcs, biome_at ...) so the game can use both.

import math, random
from collections import deque
from game.world import loot
from game.world.noise import ValueNoise, coarse_field
from game.world.prefab import all_structures, boss_building, rotate
from game.world.tiles import TILES, EMPTY
from game.world.terrain import _astar

WIDTH, HEIGHT = 320, 240

ZONES = {"factory": "toy_factory", "garden": "underground_garden"}

# the garden: a big blob made of circles (x, y, radius) in tiles - about 3x the Tundra
GARDEN_ANCHORS = [(95, 60, 62), (185, 52, 62), (262, 82, 52), (272, 160, 58), (185, 185, 66),
                  (85, 185, 56), (40, 120, 40), (165, 118, 62)]
FACTORY_RECT = (34, 72, 92, 100)        # x, y, w, h - square block inside the garden (west), ~Tundra size

ROOM_COUNT = 24
ROOM_SIZE = (11, 22)
CORRIDOR_WIDTH = 3
FACTORY_LOOT_ROOMS = 4                  # halls with gold piles (items are only in structures)
REQUIRED_FACTORY_STRUCTURES = ["factory_break_room",     # the Foreman's room - always tried first
                               "factory_control_room"]   # (11.11) its secret room has the Broken Bulb
FACTORY_STRUCTURES = 5                  # rooms with walls + entrance inside halls (prefabs with @biomes toy_factory)

# always placed first in the Garden: Wren's camp + the 3 places of her investigation (quest "wren")
# + the Gardener, his pier, the mushroom ring (whisper) and the pale altar (Pale Orb) - game/story/garden.py
REQUIRED_GARDEN_STRUCTURES = ["wren_camp", "stone_rows", "buried_playground", "collapsed_lab",
                              "gardener_hut", "sunken_pier", "mushroom_ring", "pale_altar"]
QUEST_SPROUTS = 2                      # Glowing Sprouts on the floor of far parts of the Garden (quest "gardener")
GARDEN_STRUCTURES = 12                  # atmosphere structures (prefabs with @biomes underground_garden)
GARDEN_ITEMS = 0                        # loose items in the cave: none - items are only in structures
GARDEN_GOLD = 10                        # loose gold piles in the cave
SHRINES = ["vigor", "swift", "might"]   # sigil shrines hidden in the Garden (dead ends, far from everything)
SHRINE_DISTANCE = 60                    # shrines at least this far from each other
HIDDEN_HALL = (9, 7)                    # the Factory's secret hall (Lucky Charm): inside size, no doors
EXIT_MIN_DISTANCE = 45                  # the Core exit is random, but at least this far from both entrances

CUTTABLE = {"T", "r", "~", "m", "k", "x", "*"}   # removable when something must be made reachable


class CellarMap:
    def __init__(self, seed):
        self.seed = seed
        self.used_seed = seed
        self.width, self.height = WIDTH, HEIGHT
        self.rnd = random.Random(f"cellar-{seed}")
        self.zones = [[None] * WIDTH for _ in range(HEIGHT)]
        self.tiles = [["M"] * WIDTH for _ in range(HEIGHT)]
        self.gates, self.portals, self.pickups, self.npcs, self.structures = [], [], [], [], []
        self.exits = []
        self.protected = set()
        self.structure_cells = set()       # hand-made walls that must never be cut
        self.prefab_cells = set()          # tiles of stamped prefabs (structures, boss buildings)
        self.arrivals = {}                 # where the player appears when coming through a portal: leads_from -> tile
        self.hidden = {}                   # secret id -> cells drawn as wall until the player steps in (Map)
        self.secret_ways = {}              # (11.11) secret id -> its ways in (a crack shows on them up close)
        self.wiggle = coarse_field(ValueNoise(seed * 11 + 9), 9, WIDTH, HEIGHT)   # makes tunnels bend

        self._make_garden_cave()
        self._make_factory()
        self._factory_exit()
        self._make_tundra_entrance()
        self._make_garden_exit()
        self._place_garden_structures()
        self._decorate_garden()
        self._place_garden_loot()
        self._garden_secrets()
        self.paths_cut = self._ensure_reachable()
        self.player_start = self.arrivals["surface:separated"]
        self._sigil_secrets()

    def biome_at(self, x, y):
        zone = self.zones[y][x]
        return ZONES[zone] if zone else None

    def walkable(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height and not TILES[self.tiles[y][x]]["solid"]

    def in_factory_block(self, x, y, margin=0):
        fx, fy, fw, fh = FACTORY_RECT
        return fx - margin <= x < fx + fw + margin and fy - margin <= y < fy + fh + margin

    # --- tunnels: wide and bending ----------------------------------------------------------
    def _tunnel(self, a, b, floor, zone, radius=1.8, allow=None):
        """Carves a natural-looking tunnel from a to b (bends with noise, ~4 tiles wide)."""
        def cost(x, y):
            if (x, y) in self.structure_cells:
                return 1 if self.walkable(x, y) else None     # through a structure's floor, never its walls
            if (allow is None and self.in_factory_block(x, y, 2)) or (allow is not None and not allow(x, y)):
                return None
            if self.walkable(x, y):
                return 1
            return 2 + max(0.0, self.wiggle[y][x] + 0.5) * 14
        path = _astar(self, a, b, cost)
        if not path:
            return []
        r = int(math.ceil(radius))
        for i, (x, y) in enumerate(path):
            rr = radius + 0.6 * math.sin(i / 5.0)          # width breathes a bit along the tunnel
            for dx in range(-r - 1, r + 2):
                for dy in range(-r - 1, r + 2):
                    nx, ny = x + dx, y + dy
                    if dx * dx + dy * dy > rr * rr or not (1 <= nx < WIDTH - 1 and 1 <= ny < HEIGHT - 1):
                        continue
                    if (nx, ny) in self.structure_cells or (allow is None and self.in_factory_block(nx, ny, 1)):
                        continue
                    if allow is not None and not allow(nx, ny):
                        continue
                    if not self.walkable(nx, ny):
                        self.tiles[ny][nx] = floor
                    if self.zones[ny][nx] is None:
                        self.zones[ny][nx] = zone
        return path

    # --- garden cave ----------------------------------------------------------------------
    def _make_garden_cave(self):
        s = self.seed
        warp_x = coarse_field(ValueNoise(s * 11 + 1), 35, WIDTH, HEIGHT)
        warp_y = coarse_field(ValueNoise(s * 11 + 2), 35, WIDTH, HEIGHT)
        cave = coarse_field(ValueNoise(s * 11 + 3), 13, WIDTH, HEIGHT)
        for y in range(HEIGHT):
            for x in range(WIDTH):
                wx, wy = x + warp_x[y][x] * 18, y + warp_y[y][x] * 18
                d = min(math.hypot(wx - cx, wy - cy) / r for cx, cy, r in GARDEN_ANCHORS)
                if d < 1.0 and 2 <= x < WIDTH - 2 and 2 <= y < HEIGHT - 2:
                    self.zones[y][x] = "garden"
                    edge = max(0.0, (d - 0.75) / 0.25)        # closes up near the outer edge
                    self.tiles[y][x] = "." if cave[y][x] > -0.10 + edge * 0.6 else "#"
        # the factory block is solid rock in the cave; the factory is built into it next
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if self.in_factory_block(x, y, 3):
                    self.zones[y][x] = "garden" if not self.in_factory_block(x, y) else None
                    self.tiles[y][x] = "#"
        self._keep_main_cave()

    def _components(self, zone, open_tiles):
        seen, comps = set(), []
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if (x, y) in seen or self.zones[y][x] != zone or self.tiles[y][x] not in open_tiles:
                    continue
                comp, queue = [], deque([(x, y)])
                seen.add((x, y))
                while queue:
                    cx, cy = queue.popleft()
                    comp.append((cx, cy))
                    for n in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if n not in seen and 0 <= n[0] < WIDTH and 0 <= n[1] < HEIGHT and \
                                self.zones[n[1]][n[0]] == zone and self.tiles[n[1]][n[0]] in open_tiles:
                            seen.add(n)
                            queue.append(n)
                comps.append(comp)
        return sorted(comps, key=len, reverse=True)

    def _keep_main_cave(self):
        # big side caves get a bending tunnel to the main cave, tiny pockets are filled with rock
        comps = self._components("garden", {"."})
        main = set(comps[0])
        inside = lambda x, y: self.zones[y][x] == "garden" and not self.in_factory_block(x, y, 2)
        for comp in comps[1:]:
            if len(comp) < 60:
                for x, y in comp:
                    self.tiles[y][x] = "#"
                continue
            start = comp[len(comp) // 2]
            target = min(main, key=lambda c: abs(c[0] - start[0]) + abs(c[1] - start[1]))
            self._tunnel(start, target, ".", "garden", allow=inside)
            main |= set(comp)

    # --- factory --------------------------------------------------------------------------
    def _make_factory(self):
        fx, fy, fw, fh = FACTORY_RECT
        for y in range(fy, fy + fh):
            for x in range(fx, fx + fw):
                self.zones[y][x] = "factory"
                self.tiles[y][x] = "#"
                self.structure_cells.add((x, y))      # factory walls are never cut by tunnels
        rooms = []
        for _ in range(2500):
            if len(rooms) >= ROOM_COUNT:
                break
            w, h = self.rnd.randint(*ROOM_SIZE), self.rnd.randint(*ROOM_SIZE)
            x, y = self.rnd.randint(fx + 3, fx + fw - w - 3), self.rnd.randint(fy + 3, fy + fh - h - 3)
            if all(x + w + 3 <= rx or rx + rw + 3 <= x or y + h + 3 <= ry or ry + rh + 3 <= y for rx, ry, rw, rh in rooms):
                rooms.append((x, y, w, h))
        self.rooms = rooms
        for x, y, w, h in rooms:
            for ty in range(y, y + h):
                for tx in range(x, x + w):
                    self.tiles[ty][tx] = "g"
        centres = [(x + w // 2, y + h // 2) for x, y, w, h in rooms]
        self.room_centres = centres
        connected, edges = {0}, []
        while len(connected) < len(rooms):
            a, b = min(((i, j) for i in connected for j in range(len(rooms)) if j not in connected),
                       key=lambda e: math.dist(centres[e[0]], centres[e[1]]))
            edges.append((a, b))
            connected.add(b)
        others = sorted(((i, j) for i in range(len(rooms)) for j in range(i + 1, len(rooms)) if (i, j) not in edges and (j, i) not in edges),
                        key=lambda e: math.dist(centres[e[0]], centres[e[1]]))
        edges += others[:max(2, len(rooms) // 5)]
        for a, b in edges:
            self._corridor(centres[a], centres[b])
        for y in range(fy, fy + fh):
            for x in range(fx, fx + fw):
                if self.tiles[y][x] != "#":
                    self.structure_cells.discard((x, y))

    def _corridor(self, a, b):
        half = CORRIDOR_WIDTH // 2
        (x1, y1), (x2, y2) = a, b
        corner = (x2, y1) if self.rnd.random() < 0.5 else (x1, y2)
        for (sx, sy), (tx, ty) in ((a, corner), (corner, b)):
            for x in range(min(sx, tx), max(sx, tx) + 1):
                for y in range(min(sy, ty), max(sy, ty) + 1):
                    for d in range(-half, half + 1):
                        for cx, cy in ((x + d, y), (x, y + d)):
                            if self.zones[cy][cx] == "factory":
                                self.tiles[cy][cx] = "g"
                                self.protected.add((cx, cy))

    def _protect(self, centre, r):
        cx, cy = centre
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                    self.protected.add((x, y))

    def _factory_exit(self):
        """Boss hall on a random side of the factory, gate through the factory wall, bending tunnel into the cave."""
        fx, fy, fw, fh = FACTORY_RECT
        centres = self.room_centres
        side = self.rnd.choice(["north", "east", "south", "west"])
        score = {"north": lambda c: c[1], "south": lambda c: -c[1], "west": lambda c: c[0], "east": lambda c: -c[0]}[side]
        self.boss_room = min(range(len(centres)), key=lambda i: score(centres[i]))
        bx, by = centres[self.boss_room]
        # corridor from the boss hall straight to the wall, then 3 tiles of gate through the wall
        step = {"north": (0, -1), "south": (0, 1), "west": (-1, 0), "east": (1, 0)}[side]
        x, y = bx, by
        gate_cells = []
        while self.in_factory_block(x, y):
            for d in (-1, 0, 1):
                cx, cy = (x + d, y) if step[0] == 0 else (x, y + d)
                if self.tiles[cy][cx] == "#":
                    # last 2 tiles of the factory wall become the gate
                    on_edge = not self.in_factory_block(cx + step[0] * 2, cy + step[1] * 2)
                    self.tiles[cy][cx] = "|" if on_edge else "g"
                    self.structure_cells.discard((cx, cy))
                    if on_edge:
                        gate_cells.append((cx, cy))
            x, y = x + step[0], y + step[1]
        outside = (x + step[0] * 2, y + step[1] * 2)
        # bending tunnel from just outside the factory to the nearest open cave
        floor = [c for c in self._garden_floor() if not self.in_factory_block(*c, 6)]
        target = min(floor, key=lambda c: math.dist(c, outside))
        for d in range(-1, 2):
            for k in range(0, 3):
                cx, cy = (x + d + step[0] * k, y + step[1] * k) if step[0] == 0 else (x + step[0] * k, y + d + step[1] * k)
                self.tiles[cy][cx] = "."
                self.zones[cy][cx] = "garden"
        self._tunnel(outside, target, ".", "garden")
        self.gates.append({"from": "factory", "to": "garden", "pos": gate_cells[len(gate_cells) // 2], "cells": gate_cells,
                           "boss": (bx, by), "entry": outside})
        self._protect((bx, by), 3)
        self._protect(outside, 3)
        # entry hall from the surface: random hall, but not close to the boss hall
        far = sorted(range(len(centres)), key=lambda i: -math.dist(centres[i], (bx, by)))
        self.entry_room = self.rnd.choice(far[:max(1, len(far) // 2)])
        ex, ey = centres[self.entry_room]
        self.portals.append({"zone": "factory", "pos": (ex, ey), "leads_to": "surface:separated"})
        self.arrivals["surface:separated"] = (ex, ey + 2)
        self._protect((ex, ey), 3)
        self._place_factory_structures()
        self._decorate_factory()
        self._factory_loot()

    def _place_factory_structures(self):
        """Special rooms (walls + entrance) built into the solid factory walls between the halls.
        The room is rotated so its door FACES a hall, and a straight 3-wide corridor joins them
        (no corridors wrapping around the room)."""
        prefabs = [p for p in all_structures() if "toy_factory" in p.list_setting("biomes")]
        fx, fy, fw, fh = FACTORY_RECT
        uses, placed = {}, 0
        for _ in range(1500):
            if placed >= FACTORY_STRUCTURES or not prefabs:
                break
            required = [p for name in REQUIRED_FACTORY_STRUCTURES for p in prefabs if p.name == name and not uses.get(name)]
            base = required[0] if required else self.rnd.choice(prefabs)
            if uses.get(base.name, 0) >= self._factory_structure_limit(base):
                continue
            ox0 = self.rnd.randint(fx + 2, fx + fw - 4)
            oy0 = self.rnd.randint(fy + 2, fy + fh - 4)
            best = None
            for turns in range(4):
                prefab = rotate(base, turns)
                ox, oy = ox0, oy0
                if ox + prefab.width > fx + fw - 2 or oy + prefab.height > fy + fh - 2:
                    continue
                ring = [(ox + dx, oy + dy) for dy in range(-1, prefab.height + 1) for dx in range(-1, prefab.width + 1)]
                if not all(self.tiles[y][x] == "#" and (x, y) not in self.protected for x, y in ring):
                    continue
                for door, direction in self._doors(prefab, ox, oy):
                    corridor = self._straight_corridor(door, direction)
                    if corridor is not None and (best is None or len(corridor) < len(best[3])):
                        best = (prefab, ox, oy, corridor)
            if not best:
                continue
            prefab, ox, oy, corridor = best
            self._stamp(prefab, ox, oy, "factory")
            for cx, cy in corridor:
                self.tiles[cy][cx] = "g"
                self.structure_cells.discard((cx, cy))
                self.protected.add((cx, cy))
            self.structures.append({"name": prefab.name, "zone": "factory", "rect": (ox, oy, prefab.width, prefab.height)})
            uses[base.name] = uses.get(base.name, 0) + 1
            placed += 1

    @staticmethod
    def _factory_structure_limit(prefab):
        """How many of this room a Factory may have: NPC rooms and the required (story) ones once, others twice."""
        once = prefab.list_setting("npcs") or prefab.name in REQUIRED_FACTORY_STRUCTURES
        return 1 if once else 2

    def _doors(self, prefab, ox, oy):
        """Walkable tiles on the edge of a prefab + the direction pointing out of the room."""
        doors = []
        for y in range(prefab.height):
            for x in range(prefab.width):
                if prefab.rows[y][x] == EMPTY or TILES[prefab.tile_at(x, y)]["solid"]:
                    continue
                if y == 0:
                    doors.append(((ox + x, oy + y), (0, -1)))
                elif y == prefab.height - 1:
                    doors.append(((ox + x, oy + y), (0, 1)))
                elif x == 0:
                    doors.append(((ox + x, oy + y), (-1, 0)))
                elif x == prefab.width - 1:
                    doors.append(((ox + x, oy + y), (1, 0)))
        return doors

    def _straight_corridor(self, door, direction, max_length=14):
        """Tiles of a straight 3-wide corridor from the door outwards until it meets a hall ("g").
        None if it would hit the outer factory wall, another structure, or is too long."""
        dx, dy = direction
        px, py = -dy, dx                                   # across the corridor
        cells = []
        x, y = door
        for step in range(1, max_length + 1):
            cx, cy = x + dx * step, y + dy * step
            row = [(cx + px * k, cy + py * k) for k in (-1, 0, 1)]
            if not all(self.in_factory_block(a, b, -1) for a, b in row):
                return None
            if any((a, b) in self.prefab_cells for a, b in row):
                return None
            if self.tiles[cy][cx] == "g":                  # reached a hall / corridor
                return cells if step > 1 else None         # a door glued to a hall isn't a corridor
            cells += row
        return None

    def _decorate_factory(self):
        centres = self.room_centres
        for i, (x, y, w, h) in enumerate(self.rooms):
            if i in (self.boss_room, self.entry_room):
                continue
            free = lambda tx, ty: self.tiles[ty][tx] == "g" and (tx, ty) not in self.protected
            # conveyor belt along the hall: moves the player ("<" ">" or "A" "v")
            if self.rnd.random() < 0.7:
                if w >= h:
                    row, belt = y + self.rnd.choice([2, h - 3]), self.rnd.choice([">", "<"])
                    cells = [(tx, row) for tx in range(x + 2, x + w - 2)]
                else:
                    col, belt = x + self.rnd.choice([2, w - 3]), self.rnd.choice(["A", "v"])
                    cells = [(col, ty) for ty in range(y + 2, y + h - 2)]
                for tx, ty in cells:
                    if free(tx, ty):
                        self.tiles[ty][tx] = belt
            for _ in range(w * h // 55):
                mx, my = self.rnd.randint(x + 2, x + w - 4), self.rnd.randint(y + 2, y + h - 4)
                cells = [(mx + dx, my + dy) for dx in (0, 1) for dy in (0, 1)]
                if all(free(*c) for c in cells) and math.dist((mx, my), centres[i]) > 2:
                    for cx, cy in cells:
                        self.tiles[cy][cx] = "m"
            for _ in range(w * h // 45):
                kx, ky = self.rnd.choice([(self.rnd.randint(x, x + w - 1), self.rnd.choice([y, y + h - 1])),
                                          (self.rnd.choice([x, x + w - 1]), self.rnd.randint(y, y + h - 1))])
                if free(kx, ky):
                    self.tiles[ky][kx] = "k"

    def _factory_loot(self):
        centres = self.room_centres
        candidates = [i for i in range(len(self.rooms)) if i not in (self.boss_room, self.entry_room)]
        self.rnd.shuffle(candidates)
        placed = set()
        for i in candidates[:FACTORY_LOOT_ROOMS]:
            x, y, w, h = self.rooms[i]
            for _ in range(2):
                gx, gy = self.rnd.randint(x + 1, x + w - 2), self.rnd.randint(y + 1, y + h - 2)
                if self.tiles[gy][gx] == "g" and (gx, gy) not in self.protected:
                    self.pickups.append({"pos": (gx, gy), "type": "gold", "amount": loot.roll_gold("toy_factory", self.rnd)})
        self._quest_gear()

    def _quest_gear(self):
        """The Foreman's Gear (quest "foreman"): on the floor of a far hall, only shown while the quest is active.
        Own random generator, so the rest of the cellar stays the same for a seed."""
        rnd = random.Random(f"gear-{self.seed}")
        ex, ey = self.room_centres[self.entry_room] if self.entry_room is not None else (0, 0)
        rooms = [i for i in range(len(self.rooms)) if i not in (self.boss_room, self.entry_room)]
        rooms.sort(key=lambda i: -math.dist(self.room_centres[i], (ex, ey)))
        taken = {p["pos"] for p in self.pickups}
        for i in rooms[:max(1, len(rooms) // 3)] + rooms:          # preferably one of the farthest halls
            x, y, w, h = self.rooms[i]
            spots = [(gx, gy) for gy in range(y + 1, y + h - 1) for gx in range(x + 1, x + w - 1)
                     if self.tiles[gy][gx] == "g" and (gx, gy) not in self.protected and (gx, gy) not in taken]
            if spots:
                self.pickups.append({"pos": rnd.choice(spots), "type": "item", "item": "Gear", "quest": "foreman"})
                return

    # --- garden entrance / exit ---------------------------------------------------------------
    def _garden_floor(self):
        return [(x, y) for y in range(HEIGHT) for x in range(WIDTH)
                if self.zones[y][x] == "garden" and self.tiles[y][x] == "." and not self.in_factory_block(x, y, 3)]

    def _garden_boss_building(self, chamber, dx, dy):
        """Temple around the garden boss (prefabs/bosses/underground_garden.txt), back door facing the exit chamber."""
        prefab = boss_building("underground_garden")
        if not prefab:
            return None
        gx, gy = -dx, -dy                                  # from the boss towards the chamber
        if abs(gx) > abs(gy):
            turns = 1 if gx > 0 else 3
        else:
            turns = 2 if gy > 0 else 0
        building = rotate(prefab, turns)
        bx, by = building.markers["boss"][0]
        cx, cy = chamber
        spots = [(dist, side) for dist in range(16, 46) for side in (0, -4, 4, -8, 8, -12, 12, -16, 16)]
        spots.sort(key=lambda d: d[0] + abs(d[1]) * 1.5)
        for dist, side in spots:
            px = round(cx + dx * dist - dy * side)
            py = round(cy + dy * dist + dx * side)
            ox, oy = px - bx, py - by
            area = [(ox + x, oy + y) for y in range(-2, building.height + 2) for x in range(-2, building.width + 2)]
            if all(2 <= x < WIDTH - 2 and 2 <= y < HEIGHT - 2 and self.zones[y][x] == "garden" and (x, y) not in self.structure_cells
                   and not self.in_factory_block(x, y, 3) for x, y in area):
                for x, y in area:                          # carve the cave open around the temple
                    self.tiles[y][x] = "."
                self._stamp(building, ox, oy, "garden")
                self.structures.append({"name": building.name, "zone": "garden", "rect": (ox, oy, building.width, building.height)})
                for x, y in area:
                    self.protected.add((x, y))
                return (px, py)
        return None

    def _depth(self, c):
        # rough distance from the solid rock around the garden
        x, y = c
        for r in range(1, 12):
            for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r)):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < WIDTH and 0 <= ny < HEIGHT) or self.zones[ny][nx] != "garden":
                    return r
        return 12

    def _clear_circle(self, centre, r, floor):
        cx, cy = centre
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if 1 < x < WIDTH - 2 and 1 < y < HEIGHT - 2 and math.hypot(x - cx, y - cy) <= r + 0.3 \
                        and (x, y) not in self.structure_cells and not self.in_factory_block(x, y):
                    self.tiles[y][x] = floor
                    self.zones[y][x] = self.zones[y][x] or "garden"

    def _make_tundra_entrance(self):
        # random place in the cave (not right next to the factory)
        floor = [c for c in self._garden_floor() if self._depth(c) >= 5 and not self.in_factory_block(*c, 12)]
        pos = self.rnd.choice(floor)
        self._clear_circle(pos, 3, ".")
        self.portals.append({"zone": "garden", "pos": pos, "leads_to": "surface:tundra_pass"})
        self.arrivals["surface:tundra_pass"] = (pos[0], pos[1] + 2)
        self._protect(pos, 4)

    def _make_garden_exit(self):
        # random place, deep in the cave, at least EXIT_MIN_DISTANCE from both entrances
        entrances = [g["entry"] for g in self.gates] + [p["pos"] for p in self.portals if p["zone"] == "garden"]
        floor = [c for c in self._garden_floor() if self._depth(c) >= 9 and not self.in_factory_block(*c, 15)
                 and min(math.dist(c, e) for e in entrances) >= EXIT_MIN_DISTANCE]
        pos = self.rnd.choice(floor)
        cx, cy = pos
        # the chamber door faces the biggest open direction
        best, dx, dy = -1, 1, 0
        for a in range(0, 360, 30):
            ddx, ddy = math.cos(math.radians(a)), math.sin(math.radians(a))
            open_count = sum(1 for k in range(9, 18) if self.walkable(round(cx + ddx * k), round(cy + ddy * k)))
            if open_count > best:
                best, dx, dy = open_count, ddx, ddy
        self._clear_circle(pos, 5, ",")
        gate_cells = []
        for y in range(cy - 8, cy + 9):
            for x in range(cx - 8, cx + 9):
                if not (5.5 < math.hypot(x - cx, y - cy) <= 7.5):
                    continue
                along = (x - cx) * dx + (y - cy) * dy
                across = abs(-(x - cx) * dy + (y - cy) * dx)
                if along > 0 and across <= 1.6:
                    self.tiles[y][x] = "|"
                    gate_cells.append((x, y))
                else:
                    self.tiles[y][x] = "#"
                    self.structure_cells.add((x, y))
                self.zones[y][x] = "garden"
        boss = (round(cx + dx * 12), round(cy + dy * 12))
        building_boss = self._garden_boss_building(pos, dx, dy)
        if building_boss:
            boss = building_boss
        else:
            self._clear_circle(boss, 3, ".")
        self._tunnel(boss, (round(cx + dx * 8), round(cy + dy * 8)), ".", "garden", radius=1.5)
        self.portals.append({"zone": "garden", "pos": pos, "leads_to": "core:entry"})
        self.arrivals["core:core"] = (round(cx + dx * 3), round(cy + dy * 3))    # coming back from the Core
        self.gates.append({"from": "garden", "to": "garden", "pos": gate_cells[len(gate_cells) // 2], "cells": gate_cells,
                           "boss": boss, "entry": (round(cx + dx * 3), round(cy + dy * 3))})
        self._protect(pos, 8)
        self._protect(boss, 4)

    # --- garden structures (atmosphere) --------------------------------------------------------
    def _place_garden_structures(self):
        prefabs = [p for p in all_structures() if "underground_garden" in p.list_setting("biomes")]
        if not prefabs:
            return
        floor = self._garden_floor()
        uses, centres = {}, [p["pos"] for p in self.portals] + [g["boss"] for g in self.gates]
        pending = [p for name in REQUIRED_GARDEN_STRUCTURES for p in prefabs if p.name == name]
        tries = 0
        for _ in range(4000):
            if sum(1 for st in self.structures if st["zone"] == "garden" and not st["name"].startswith("boss_")) >= GARDEN_STRUCTURES:
                break
            if pending and tries > 800:
                pending.pop(0)                                       # doesn't fit anywhere (very unlikely)
                tries = 0
            prefab = pending[0] if pending else self.rnd.choice(prefabs)
            tries += 1
            # NPC structures and the story ones (e.g. the pale altar) once, others max twice
            limit = 1 if prefab.list_setting("npcs") or prefab.name in REQUIRED_GARDEN_STRUCTURES else 2
            if uses.get(prefab.name, 0) >= limit:
                continue
            cx, cy = self.rnd.choice(floor)
            ox, oy = cx - prefab.width // 2, cy - prefab.height // 2
            if any(math.dist((cx, cy), c) < 24 for c in centres):
                continue
            cells = [(ox + x, oy + y) for y in range(prefab.height) for x in range(prefab.width) if prefab.rows[y][x] != EMPTY]
            if not all(2 <= x < WIDTH - 2 and 2 <= y < HEIGHT - 2 and self.zones[y][x] == "garden" and (x, y) not in self.protected
                       and (x, y) not in self.structure_cells and not self.in_factory_block(x, y, 3) for x, y in cells):
                continue
            # mostly open ground there (structures sit in the cave, they don't fill rock walls)
            if sum(1 for x, y in cells if self.tiles[y][x] == ".") < len(cells) * 0.75:
                continue
            self._stamp(prefab, ox, oy, "garden")
            for x, y in cells:   # a free ring around it
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        n = (x + dx, y + dy)
                        if n not in self.structure_cells and self.zones[n[1]][n[0]] == "garden" and TILES[self.tiles[n[1]][n[0]]]["solid"]:
                            self.tiles[n[1]][n[0]] = "."
                        self.protected.add(n)
            self.structures.append({"name": prefab.name, "zone": "garden", "rect": (ox, oy, prefab.width, prefab.height)})
            uses[prefab.name] = uses.get(prefab.name, 0) + 1
            centres.append((cx, cy))
            if pending and prefab is pending[0]:
                pending.pop(0)
                tries = 0

    def _stamp(self, prefab, ox, oy, zone):
        biome = ZONES[zone]
        for y in range(prefab.height):
            for x in range(prefab.width):
                tile = prefab.tile_at(x, y)
                if tile != EMPTY:
                    self.tiles[oy + y][ox + x] = tile
                    self.structure_cells.add((ox + x, oy + y))
                    self.prefab_cells.add((ox + x, oy + y))
                    self.protected.add((ox + x, oy + y))
        for (x, y) in prefab.markers_in_order("gold"):
            self.pickups.append({"pos": (ox + x, oy + y), "type": "gold", "amount": loot.roll_gold(biome, self.rnd)})
        placed = {p["item"] for p in self.pickups if p["type"] == "item"}
        for (x, y), entry in zip(prefab.markers_in_order("item"), prefab.list_setting("items")):
            item = loot.roll_item(biome, self.rnd, placed) if entry == "random" else entry
            self.pickups.append({"pos": (ox + x, oy + y), "type": "item", "item": item})
        for (x, y), npc_id in zip(prefab.markers_in_order("npc"), prefab.list_setting("npcs")):
            self.npcs.append({"pos": (ox + x, oy + y), "id": npc_id, "zone": zone})
        self._stamp_secret(prefab, ox, oy)

    def _stamp_secret(self, prefab, ox, oy):
        """(11.11) A prefab's secret part ("h" marker): wall-looking until found (Map.hidden_cells)."""
        ways, part = prefab.secret()
        if part:
            self.hidden[prefab.name] = {(ox + x, oy + y) for x, y in part}
            self.secret_ways[prefab.name] = {(ox + x, oy + y) for x, y in ways}

    def _garden_secrets(self):
        """Quest / secret pickups in the Garden (own random generator, the rest of the cellar stays the same):
        - the Pale Orb on the pale altar exists only after flag "pale_orb:revealed" (game/story/garden.py)
        - 2 Glowing Sprouts far away, only while the Gardener's quest is active."""
        for p in self.pickups:
            if p.get("item") == "Pale Orb":
                p["flag"] = "pale_orb:revealed"
        rnd = random.Random(f"sprouts-{self.seed}")
        hut = next((n["pos"] for n in self.npcs if n["id"] == "gardener"), None)
        taken = {p["pos"] for p in self.pickups}
        floor = [c for c in self._garden_floor() if c not in self.protected and c not in taken]
        if not floor or hut is None:
            return
        chosen = []
        for _ in range(QUEST_SPROUTS):
            sample = [rnd.choice(floor) for _ in range(400)]
            best = max(sample, key=lambda c: min(math.dist(c, o) for o in [hut] + chosen))   # far from the hut + each other
            chosen.append(best)
            self.pickups.append({"pos": best, "type": "item", "item": "Glowing Sprout", "quest": "gardener"})

    # --- sigils (7.11) - own random generator and AFTER the reachability fix, so the rest of the cellar
    # stays exactly the same for a seed (old saves too) ---------------------------------------------
    def _sigil_secrets(self):
        rnd = random.Random(f"sigils-{self.seed}")
        self._sigil_shrines(rnd)
        self._hidden_hall(rnd)

    def _sigil_shrines(self, rnd):
        """3 shrines (a pedestal with a sigil) in enclosed dead ends of the Garden, far from paths and each other."""
        reach = self.flood(self.arrivals["surface:separated"])
        busy = self.important_points() + list(self.prefab_cells)[::7]
        def open_around(c):
            x, y = c
            return sum(1 for dy in range(-4, 5) for dx in range(-4, 5)
                       if 0 <= x + dx < WIDTH and 0 <= y + dy < HEIGHT and not TILES[self.tiles[y + dy][x + dx]]["solid"])
        floor = [c for c in reach if self.zones[c[1]][c[0]] == "garden" and self.tiles[c[1]][c[0]] == "."
                 and not self.in_factory_block(c[0], c[1], 3)]
        if not floor:
            return
        chosen = []
        for sigil in SHRINES:
            sample = [rnd.choice(floor) for _ in range(900)]
            sample = [c for c in sample if all(math.dist(c, o) >= SHRINE_DISTANCE for o in chosen)
                      and all(math.dist(c, b) >= 18 for b in busy)]
            if not sample:
                continue
            best = min(sample, key=open_around)            # the most closed-in spot = a dead end
            chosen.append(best)
            self.pickups.append({"pos": best, "type": "sigil", "sigil": sigil})

    def _hidden_hall(self, rnd):
        """Lucky Charm: a hall inside the Factory's walls with no door. A short conveyor in a hall runs into the
        wall and carries you through it; the passage and the hall look like wall until you step in."""
        iw, ih = HIDDEN_HALL
        fx, fy, fw, fh = FACTORY_RECT
        wall = lambda x, y: fx < x < fx + fw - 1 and fy < y < fy + fh - 1 and self.tiles[y][x] == "#" \
            and (x, y) not in self.prefab_cells
        rooms = [i for i in range(len(self.rooms)) if i not in (self.boss_room, self.entry_room)]
        rnd.shuffle(rooms)
        sides = [(1, 0, ">"), (-1, 0, "<"), (0, 1, "v"), (0, -1, "A")]
        for i in rooms:
            x, y, w, h = self.rooms[i]
            rnd.shuffle(sides)
            for dx, dy, belt in sides:
                # floor tiles along this side of the hall, the belt starts 3 tiles inside
                if dx:
                    edge_x = x + w - 1 if dx > 0 else x
                    starts = [(edge_x, ty) for ty in range(y + 2, y + h - 2)]
                else:
                    edge_y = y + h - 1 if dy > 0 else y
                    starts = [(tx, edge_y) for tx in range(x + 2, x + w - 2)]
                rnd.shuffle(starts)
                for sx, sy in starts:
                    for length in (2, 3, 4):            # wall tiles the belt goes through
                        passage = [(sx + dx * k, sy + dy * k) for k in range(1, length + 1)]
                        if not all(wall(*c) for c in passage):
                            break
                        ex, ey = passage[-1][0] + dx, passage[-1][1] + dy          # first tile of the hall
                        if dx:
                            hx, hy = (ex if dx > 0 else ex - iw + 1), ey - ih // 2
                        else:
                            hx, hy = ex - iw // 2, (ey if dy > 0 else ey - ih + 1)
                        ring = [(tx, ty) for ty in range(hy - 1, hy + ih + 1) for tx in range(hx - 1, hx + iw + 1)]
                        if not all(wall(*c) or (c in passage[-1:]) for c in ring if c not in passage):
                            continue
                        inside = [(tx, ty) for ty in range(hy, hy + ih) for tx in range(hx, hx + iw)]
                        visible_belt = [(sx - dx * k, sy - dy * k) for k in range(0, 3)]
                        if not all(self.tiles[cy][cx] == "g" for cx, cy in visible_belt):
                            continue
                        for cx, cy in inside:
                            self.tiles[cy][cx] = "g"
                        for cx, cy in visible_belt + passage:
                            self.tiles[cy][cx] = belt
                        self.hidden["factory_hall"] = set(passage) | set(inside)
                        self.pickups.append({"pos": (hx + iw // 2, hy + ih // 2), "type": "sigil", "sigil": "lucky_charm"})
                        return

    # --- garden decoration + loose loot ---------------------------------------------------------
    def _decorate_garden(self):
        s = self.seed
        water = coarse_field(ValueNoise(s * 11 + 4), 20, WIDTH, HEIGHT)
        plants = coarse_field(ValueNoise(s * 11 + 5), 11, WIDTH, HEIGHT)
        shrooms = coarse_field(ValueNoise(s * 11 + 6), 8, WIDTH, HEIGHT)
        near = set()
        for x, y in self.protected:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    near.add((x + dx, y + dy))
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if self.zones[y][x] != "garden" or self.tiles[y][x] != "." or (x, y) in near:
                    continue
                if water[y][x] > 0.32:
                    self.tiles[y][x] = "~"
                elif plants[y][x] > 0.22 or self.rnd.random() < 0.025:
                    self.tiles[y][x] = "T"
                elif shrooms[y][x] > 0.30:
                    self.tiles[y][x] = "*"
                elif self.rnd.random() < 0.012:
                    self.tiles[y][x] = "x"
                elif self.rnd.random() < 0.01:
                    self.tiles[y][x] = "r"

    def _place_garden_loot(self):
        floor = [c for c in self._garden_floor() if c not in self.protected]
        taken = [p["pos"] for p in self.pickups]
        spots = []
        for _ in range(4000):
            if len(spots) >= GARDEN_ITEMS + GARDEN_GOLD:
                break
            c = self.rnd.choice(floor)
            if all(math.dist(c, o) >= 14 for o in spots + taken):
                spots.append(c)
        placed = {p["item"] for p in self.pickups if p["type"] == "item"}
        for i, pos in enumerate(spots):
            if i < GARDEN_ITEMS:
                item = loot.roll_item("underground_garden", self.rnd, placed)
                placed.add(item)
                self.pickups.append({"pos": pos, "type": "item", "item": item})
            else:
                self.pickups.append({"pos": pos, "type": "gold", "amount": loot.roll_gold("underground_garden", self.rnd)})

    # --- reachability -----------------------------------------------------------------------
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
        """Anything important the player can't reach gets a bending tunnel (cave) or a cut (factory clutter)."""
        fixed = 0
        for _ in range(80):
            reach = self.flood(self.arrivals["surface:separated"])
            missing = [p for p in self.important_points() if p not in reach]
            if not missing:
                return fixed
            target = missing[0]
            in_factory = self.zones[target[1]][target[0]] == "factory"
            # start from the nearest reachable tile of the same area (a cave tunnel can't start inside the factory)
            options = [c for c in reach if in_factory == (self.zones[c[1]][c[0]] == "factory")
                       and (in_factory or not self.in_factory_block(c[0], c[1], 1))]
            start = min(options or reach, key=lambda c: abs(c[0] - target[0]) + abs(c[1] - target[1]))
            if in_factory:
                def cost(x, y):
                    t = self.tiles[y][x]
                    if not TILES[t]["solid"]:
                        return 1
                    return 6 if t in CUTTABLE else None
                for x, y in _astar(self, start, target, cost) or []:
                    if TILES[self.tiles[y][x]]["solid"]:
                        self.tiles[y][x] = "g"
            else:
                garden = lambda x, y: self.zones[y][x] in ("garden", None) and not self.in_factory_block(x, y, 1)
                if not self._tunnel(start, target, ".", "garden", radius=1.6, allow=garden):
                    raise RuntimeError(f"cellar: cannot reach {target}")
            fixed += 1
        raise RuntimeError("cellar: reachability fix did not finish")
