# STEP 3: from the zone layout (surface_layout.py) to a real tile map:
#   - cliffs ("^") between neighbouring zones, mountains ("M") outside the world
#   - "||" gates ("|") cut through the cliffs only where progression allows
#   - a boss spot in front of every gate (on the side you come from), except where no boss is needed
#   - portals to the cellar map
# Terrain inside the zones is plain grass for now - step 4 adds forests etc.

import math, os, random
from game.world import surface_layout as L
from game.world import loot
from game.world.prefab import load_prefab, PREFAB_DIR, all_structures, boss_building, rotate
from game.world.tiles import EMPTY
from game.world import terrain

TEST_DIALOGUE_NPC = False    # TEST ONLY: extra Milo with the test dialogue (game/dialogue/data/test_milo.json)
REQUIRED_STRUCTURES = {"village": ["angler_shack"], "rainbow_fields": ["flower_tower"], "candy": ["gingerbread_hut"],
                       "tundra": ["radio_hut", "antenna_a", "antenna_b", "antenna_c", "ice_fishing_camp"]}   # always placed (first) in that zone

# progression gates: (from_zone, to_zone, boss before the gate?, preferred side of the border)
# preferred side: "bottom"/"top"/"left"/"right" picks the gate position on that part of the border, None = middle
GATES = [
    ("village",        "rainbow_fields", True,  None),
    ("rainbow_fields", "candy",          True,  "bottom"),   # sketch: gate at the bottom-left of Candy
    ("candy",          "separated",      True,  None),
    ("separated",      "tundra",         False, None),       # no boss between separated village and tundra
    ("tundra",         "tundra_pass",    True,  None),
]

# portals: zone -> where it leads
PORTALS = {
    "separated":   "cellar:factory",
    "tundra_pass": "cellar:underground_garden",
    "candy":       "lunapark:entry",          # the lunapark gate - open after the Candy boss
}
# portals closed until a story flag is set: zone -> (flag, message when you walk into it)
SEALED_PORTALS = {"candy": ("boss:candy", "CLOSED. Come back when the forest is safe.")}
# portals put somewhere near the EDGE of their zone (not in the middle): the lunapark gate is off to the side
PORTALS_AT_SIDE = {"candy"}
SIDE_CLEARANCE = 4        # tiles of free zone ground all around the portal (away from the cliffs)
SIDE_AWAY_FROM_GATES = 16 # tiles from every gate and boss spot

GATE_WIDTH = 3        # tiles
BOSS_DISTANCE = 9     # tiles in front of the gate

# how many small structures (prefabs from game/world/prefabs/structures) each zone gets
STRUCTURES_PER_ZONE = {"village": 3, "rainbow_fields": 3, "candy": 3, "tundra": 4}
STRUCTURE_MIN_DISTANCE = 22   # tiles between structure centres


class SurfaceMap:
    def __init__(self, seed):
        self.seed = seed
        self.zones, self.used_seed = L.generate_zones(seed)
        self.width, self.height = L.WIDTH, L.HEIGHT
        self.rnd = random.Random(f"gates-{self.used_seed}")
        self.tiles = [["." if z is not L.OUTSIDE else "M" for z in row] for row in self.zones]
        self.gates = []      # dicts: from, to, pos, cells, boss (pos or None)
        self.portals = []    # dicts: zone, pos, leads_to
        self.structures = [] # dicts: name, zone, rect (x, y, w, h)
        self.pickups = []    # dicts: pos, type ("gold"/"item"), amount or item - picked up by walking over
        self.npcs = []       # dicts: pos, id, zone
        self.player_start = None
        self.exits = []      # exits of the fixed village centre (roads start there)
        self.protected = set()        # tiles terrain must not cover (roads, gates, bosses, portals, structures)
        self.structure_cells = set()  # tiles belonging to stamped prefabs
        self.boss_building_cells = set()   # roads may go through these (boss building doors)
        self._make_cliffs()
        for from_zone, to_zone, has_boss, side in GATES:
            self._make_gate(from_zone, to_zone, has_boss, side)
        for zone, target in PORTALS.items():
            pos = self._zone_side(zone) if zone in PORTALS_AT_SIDE else self._zone_centre(zone)
            portal = {"zone": zone, "pos": pos, "leads_to": target}
            if zone in SEALED_PORTALS:
                portal["sealed"], portal["sealed_text"] = SEALED_PORTALS[zone]
            self.portals.append(portal)
        self._place_boss_buildings()
        px, py, _, _ = L.village_prefab_rect()
        village = load_prefab("village_start")
        self._stamp(village, px, py, "village")
        # the fenced square around the start (fence included): the player can't leave it before talking to Milo
        fence = [(x, y) for y in range(village.height) for x in range(village.width) if village.rows[y][x] == "f"]
        fx0, fy0 = min(x for x, _ in fence), min(y for _, y in fence)
        fx1, fy1 = max(x for x, _ in fence), max(y for _, y in fence)
        self.start_fence = (px + fx0, py + fy0, fx1 - fx0 + 1, fy1 - fy0 + 1)
        self._place_structures()
        self._protect_special_places()
        terrain.carve_roads(self)
        terrain.fill_terrain(self)
        self.paths_cut = terrain.ensure_reachable(self)

    def biome_at(self, x, y):
        zone = self.zones[y][x]
        return L.ZONES[zone] if zone is not L.OUTSIDE else None

    # --- cliffs -------------------------------------------------------------------------
    def _make_cliffs(self):
        # every tile touching (8 directions) another zone becomes a cliff -> 2 tiles thick border
        for y in range(self.height):
            for x in range(self.width):
                zone = self.zones[y][x]
                if zone is L.OUTSIDE:
                    continue
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            other = self.zones[ny][nx]
                            if other is not L.OUTSIDE and other != zone:
                                self.tiles[y][x] = "^"

    # --- gates --------------------------------------------------------------------------
    def _make_gate(self, a, b, has_boss, side):
        cells = []
        for clearance in (5, 4, L.GATE_MIN_CLEARANCE):   # small zones (separated village) may need a tighter fit
            cells = L.gate_spots(self.zones, a, b, clearance)
            if cells:
                break
        if not cells:
            raise RuntimeError(f"no place for a gate {a}-{b}")
        if side == "bottom":
            cells.sort(key=lambda c: -c[1])
        elif side == "top":
            cells.sort(key=lambda c: c[1])
        elif side == "left":
            cells.sort(key=lambda c: c[0])
        elif side == "right":
            cells.sort(key=lambda c: -c[0])
        else:
            # middle part of the border, random within it
            cx = sum(c[0] for c in cells) / len(cells)
            cy = sum(c[1] for c in cells) / len(cells)
            cells.sort(key=lambda c: math.hypot(c[0] - cx, c[1] - cy))
        pick = cells[self.rnd.randrange(max(1, len(cells) // 4))]

        # direction from b into a (average of nearby a tiles minus nearby b tiles)
        ax = ay = bx = by = na = nb = 0
        for dx in range(-6, 7):
            for dy in range(-6, 7):
                z = self.zones[pick[1] + dy][pick[0] + dx]
                if z == a:
                    ax += dx; ay += dy; na += 1
                elif z == b:
                    bx += dx; by += dy; nb += 1
        nx, ny = ax / na - bx / nb, ay / na - by / nb
        length = math.hypot(nx, ny) or 1
        nx, ny = nx / length, ny / length       # unit vector pointing into zone a
        px, py = -ny, nx                        # along the border

        # cut the passage through the cliffs: a corridor GATE_WIDTH wide, crossing the border
        gate_cells = []
        half = GATE_WIDTH // 2
        for step in range(-5, 6):
            for w in range(-half, half + 1):
                x = round(pick[0] + nx * step * 0.5 + px * w)
                y = round(pick[1] + ny * step * 0.5 + py * w)
                if self.tiles[y][x] == "^":
                    self.tiles[y][x] = "|"
                    gate_cells.append((x, y))

        boss = None
        if has_boss:
            for dist in range(BOSS_DISTANCE, 3, -1):
                bx_, by_ = round(pick[0] + nx * dist), round(pick[1] + ny * dist)
                if self.zones[by_][bx_] == a and self.tiles[by_][bx_] == ".":
                    boss = (bx_, by_)
                    break
        # first free tile on the far side (zone b) - where the player arrives
        entry = pick
        for dist in range(3, 9):
            ex, ey = round(pick[0] - nx * dist), round(pick[1] - ny * dist)
            if self.zones[ey][ex] == b and self.tiles[ey][ex] == ".":
                entry = (ex, ey)
                break
        self.gates.append({"from": a, "to": b, "pos": pick, "cells": gate_cells, "boss": boss, "entry": entry,
                           "normal": (nx, ny)})

    def _protect_special_places(self):
        # free space around gates, bosses (room for the boss) and portals - terrain never goes there
        def protect_circle(cx, cy, r):
            for y in range(cy - r, cy + r + 1):
                for x in range(cx - r, cx + r + 1):
                    if 0 <= x < self.width and 0 <= y < self.height and math.hypot(x - cx, y - cy) <= r:
                        self.protected.add((x, y))
        for gate in self.gates:
            for cx, cy in gate["cells"]:
                protect_circle(cx, cy, 2)
            protect_circle(*gate["entry"], 2)
            if gate["boss"]:
                protect_circle(*gate["boss"], 4)
        for portal in self.portals:
            protect_circle(*portal["pos"], 3)

    # --- helpers ------------------------------------------------------------------------
    def _zone_centre(self, zone):
        cells = [(x, y) for y in range(self.height) for x in range(self.width)
                 if self.zones[y][x] == zone and self.tiles[y][x] == "."]
        cx = sum(c[0] for c in cells) / len(cells)
        cy = sum(c[1] for c in cells) / len(cells)
        return min(cells, key=lambda c: math.hypot(c[0] - cx, c[1] - cy))

    def _zone_side(self, zone):
        """A spot near the edge of the zone (far from its middle), with free ground around it and not next to
        a gate or a boss. Falls back to the middle if the zone is too small."""
        centre = self._zone_centre(zone)
        avoid = [g["pos"] for g in self.gates] + [g["boss"] for g in self.gates if g["boss"]]
        r = SIDE_CLEARANCE
        def free(x, y):
            return all(0 <= x + dx < self.width and 0 <= y + dy < self.height and
                       self.zones[y + dy][x + dx] == zone and self.tiles[y + dy][x + dx] == "."
                       for dx in range(-r, r + 1) for dy in range(-r, r + 1))
        cells = [(x, y) for y in range(self.height) for x in range(self.width)
                 if self.zones[y][x] == zone and self.tiles[y][x] == "."
                 and all(math.dist((x, y), a) >= SIDE_AWAY_FROM_GATES for a in avoid) and free(x, y)]
        if not cells:
            return centre
        cells.sort(key=lambda c: -math.dist(c, centre))
        far = cells[:max(1, len(cells) // 10)]               # the 10% farthest from the middle
        return random.Random(f"portal-{zone}-{self.used_seed}").choice(far)

    # --- prefabs / structures -------------------------------------------------------------
    def _stamp(self, prefab, ox, oy, zone):
        """Copies a prefab into the map at (ox, oy) and records its markers (gold, items, npcs, start)."""
        biome = L.ZONES[zone]
        for y in range(prefab.height):
            for x in range(prefab.width):
                tile = prefab.tile_at(x, y)
                if tile != EMPTY:
                    self.tiles[oy + y][ox + x] = tile
        gold_range = None
        if prefab.settings.get("gold"):
            low, _, high = prefab.settings["gold"].partition("-")
            gold_range = (int(low), int(high or low))
        for (x, y) in prefab.markers_in_order("gold"):
            self.pickups.append({"pos": (ox + x, oy + y), "type": "gold", "amount": loot.roll_gold(biome, self.rnd, gold_range)})
        placed = {p["item"] for p in self.pickups if p["type"] == "item"}
        for (x, y), entry in zip(prefab.markers_in_order("item"), prefab.list_setting("items")):
            item = loot.roll_item(biome, self.rnd, placed) if entry == "random" else entry
            placed.add(item)
            self.pickups.append({"pos": (ox + x, oy + y), "type": "item", "item": item})
        for (x, y), npc_id in zip(prefab.markers_in_order("npc"), prefab.list_setting("npcs")):
            self.npcs.append({"pos": (ox + x, oy + y), "id": npc_id, "zone": zone})
        for (x, y) in prefab.markers.get("exit", []):
            self.exits.append((ox + x, oy + y))
        for y in range(prefab.height):
            for x in range(prefab.width):
                if prefab.rows[y][x] != EMPTY:
                    self.structure_cells.add((ox + x, oy + y))
                    self.protected.add((ox + x, oy + y))
        if prefab.markers.get("player_start"):
            x, y = prefab.markers["player_start"][0]
            self.player_start = (ox + x, oy + y)
            if TEST_DIALOGUE_NPC:
                # TEST: Milo just north of the start, outside the fence (visible at once, but you have to walk to him)
                self.npcs.append({"pos": (ox + x - 2, oy + y - 6), "id": "milo_test", "zone": zone})

    def _place_boss_buildings(self):
        """Every boss gets a building of its biome (prefabs/bosses/<biome>.txt), back door facing the passage."""
        vx, vy, vw, vh = L.village_prefab_rect()
        for gate in self.gates:
            if not gate["boss"]:
                continue
            zone = gate["from"]
            prefab = boss_building(L.ZONES[zone])
            if not prefab:
                continue
            nx, ny = gate["normal"]                     # points from the gate into the boss's zone
            gx, gy = -nx, -ny                           # direction from the boss towards the gate
            if abs(gx) > abs(gy):
                turns = 1 if gx > 0 else 3              # building's top (back door) must face the gate
            else:
                turns = 2 if gy > 0 else 0
            building = rotate(prefab, turns)
            bx, by = building.markers["boss"][0]
            # straight in front of the passage first, then a bit to the side / further away
            spots = [(dist, side) for dist in range(11, 34) for side in (0, -3, 3, -6, 6, -9, 9)]
            spots.sort(key=lambda d: d[0] + abs(d[1]) * 1.5)
            for dist, side in spots:
                cx = round(gate["pos"][0] + nx * dist - ny * side)
                cy = round(gate["pos"][1] + ny * dist + nx * side)
                ox, oy = cx - bx, cy - by
                if self._building_fits(building, ox, oy, zone, (vx - 3, vy - 3, vw + 6, vh + 6)):
                    self._stamp(building, ox, oy, zone)
                    for y in range(building.height):
                        for x in range(building.width):
                            if building.rows[y][x] != EMPTY:
                                self.boss_building_cells.add((ox + x, oy + y))
                    gate["boss"] = (cx, cy)
                    self.structures.append({"name": building.name, "zone": zone, "rect": (ox, oy, building.width, building.height)})
                    break

    def _building_fits(self, prefab, ox, oy, zone, avoid_rect):
        ax, ay, aw, ah = avoid_rect
        for y in range(-1, prefab.height + 1):
            for x in range(-1, prefab.width + 1):
                tx, ty = ox + x, oy + y
                if not (0 <= tx < self.width and 0 <= ty < self.height):
                    return False
                inside = 0 <= x < prefab.width and 0 <= y < prefab.height and prefab.rows[y][x] != EMPTY
                ring = not inside
                if inside or ring:
                    if self.zones[ty][tx] != zone or self.tiles[ty][tx] != ".":
                        return False
                    if ax <= tx < ax + aw and ay <= ty < ay + ah:
                        return False
        return True

    def _reserved(self):
        # places structures must stay away from: (x, y, radius)
        spots = []
        for gate in self.gates:
            spots.append((gate["pos"][0], gate["pos"][1], 8))
            if gate["boss"]:
                spots.append((gate["boss"][0], gate["boss"][1], 10))
        for portal in self.portals:
            spots.append((portal["pos"][0], portal["pos"][1], 8))
        px, py, pw, ph = L.village_prefab_rect()
        spots.append((px + pw // 2, py + ph // 2, max(pw, ph) // 2 + 6))
        return spots

    def _fits(self, prefab, ox, oy, zone, margin=2):
        if ox - margin < 0 or oy - margin < 0 or ox + prefab.width + margin >= self.width or oy + prefab.height + margin >= self.height:
            return False
        for y in range(oy - margin, oy + prefab.height + margin):
            for x in range(ox - margin, ox + prefab.width + margin):
                if self.zones[y][x] != zone or self.tiles[y][x] != ".":
                    return False
        return True

    def _place_structures(self):
        all_prefabs = all_structures()      # game structures + mods/structures
        reserved = self._reserved()
        centres = []
        used_unique = set()   # structures with NPCs appear at most once per map (an NPC is one person)
        for zone, count in STRUCTURES_PER_ZONE.items():
            biome = L.ZONES[zone]
            required = [p for p in all_prefabs if p.name in REQUIRED_STRUCTURES.get(zone, [])]
            count += len(required)
            candidates = [p for p in all_prefabs if biome in p.list_setting("biomes") and p.name not in used_unique
                          and not any(p.name in names for names in REQUIRED_STRUCTURES.values())]
            # biome-specific structures first, then the "anywhere" ones; no repeats inside a zone
            specific = [p for p in candidates if len(p.list_setting("biomes")) == 1]
            generic = [p for p in candidates if len(p.list_setting("biomes")) > 1]
            self.rnd.shuffle(specific)
            self.rnd.shuffle(generic)
            queue = required + specific + generic       # required ones first (e.g. the Angler's shack)
            cells = [(x, y) for y in range(self.height) for x in range(self.width) if self.zones[y][x] == zone]
            placed = 0
            for prefab in queue:
                if placed >= count:
                    break
                if prefab.name in used_unique:
                    continue
                for _ in range(4000 if prefab in required else 400):
                    cx, cy = self.rnd.choice(cells)
                    ox, oy = cx - prefab.width // 2, cy - prefab.height // 2
                    centre = (cx, cy)
                    if any(math.hypot(cx - rx, cy - ry) < rr + max(prefab.width, prefab.height) / 2 for rx, ry, rr in reserved):
                        continue
                    if any(math.hypot(cx - ox2, cy - oy2) < STRUCTURE_MIN_DISTANCE for ox2, oy2 in centres):
                        continue
                    if not self._fits(prefab, ox, oy, zone):
                        continue
                    self._stamp(prefab, ox, oy, zone)
                    self.structures.append({"name": prefab.name, "zone": zone, "rect": (ox, oy, prefab.width, prefab.height)})
                    centres.append(centre)
                    if prefab.list_setting("npcs"):
                        used_unique.add(prefab.name)
                    placed += 1
                    break
