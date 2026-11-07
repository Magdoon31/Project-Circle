# STEP 4b: terrain inside the biomes + roads + reachability guarantee.
#
# Order (called by SurfaceMap after structures are placed):
#   1. carve_roads     - main roads ("," 2 tiles wide) along the progression: start -> boss -> gate -> next zone ...
#                        plus a few short trails from the village exits into the forest
#   2. fill_terrain    - forests, ponds, rocks, flowers from noise; different per biome (BIOME_TERRAIN)
#                        never on roads, structures, gates, bosses, portals (protected tiles)
#   3. ensure_reachable - flood fill from the player start; anything important that got closed in
#                        (by trees / water / rocks) gets a path cut to it.

import heapq, math, random
from collections import deque
from game.world import surface_layout as L
from game.world.noise import ValueNoise
from game.world.tiles import TILES

# Per biome terrain. Noise values are roughly -0.6..0.6.
#   forest:  tree where forest noise > value      (lower = more forest)
#   water:   water where water noise > value      (None = no water)
#   flowers: flower patches where flower noise > value (None = none)
#   rocks:   chance of a single rock on a free tile
#   scatter: chance of a single tree on a free tile (outside forests)
#   flower_tile: which tile flowers use
BIOME_TERRAIN = {
    "village":           {"forest": 0.02, "water": 0.42, "flowers": 0.38, "rocks": 0.004, "scatter": 0.03, "flower_tile": "*"},
    "rainbow_fields":    {"forest": 0.30, "water": 0.48, "flowers": 0.16, "rocks": 0.006, "scatter": 0.01, "flower_tile": "*"},
    "sugarwood_grove":   {"forest": -0.06, "water": 0.40, "flowers": 0.35, "rocks": 0.006, "scatter": 0.05, "flower_tile": "*"},
    "silverpine_tundra": {"forest": 0.18, "water": 0.33, "flowers": None, "rocks": 0.018, "scatter": 0.02, "flower_tile": "*"},
}
# zone-specific overrides (small zones stay open)
ZONE_TERRAIN = {
    "separated":   {"forest": 0.32, "water": None, "flowers": 0.40, "rocks": 0.004, "scatter": 0.02, "flower_tile": "*"},
    "tundra_pass": {"forest": 0.38, "water": None, "flowers": None, "rocks": 0.03, "scatter": 0.01, "flower_tile": "*"},
}

WALKABLE = {char for char, tile in TILES.items() if not tile["solid"]}
OBSTACLES = {"T", "r", "~"}          # terrain the reachability fix may remove (never walls, cliffs, houses)


# --- helpers -------------------------------------------------------------------------------
def _field(seed, scale):
    return L._coarse_field(ValueNoise(seed), scale)


def _astar(world, start, goal, cost_fn):
    """Shortest path by cost; cost_fn(x, y) -> cost or None (blocked)."""
    open_heap = [(0, start)]
    came, best = {start: None}, {start: 0}
    while open_heap:
        _, cur = heapq.heappop(open_heap)
        if cur == goal:
            path = []
            while cur:
                path.append(cur)
                cur = came[cur]
            return path[::-1]
        x, y = cur
        for nxt in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            nx, ny = nxt
            if not (0 <= nx < world.width and 0 <= ny < world.height):
                continue
            c = cost_fn(nx, ny) if nxt != goal else 1
            if c is None:
                continue
            new = best[cur] + c
            if new < best.get(nxt, 1e18):
                best[nxt] = new
                came[nxt] = cur
                heapq.heappush(open_heap, (new + abs(nx - goal[0]) + abs(ny - goal[1]), nxt))
    return None


def _flood(world, start):
    passable = WALKABLE
    seen = {start}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            nx, ny = n
            if n not in seen and 0 <= nx < world.width and 0 <= ny < world.height and world.tiles[ny][nx] in passable:
                seen.add(n)
                queue.append(n)
    return seen


# --- 1. roads ------------------------------------------------------------------------------
def carve_roads(world):
    wiggle = _field(world.used_seed * 7 + 11, 12)

    def road_cost(x, y):
        tile = world.tiles[y][x]
        if (x, y) in world.structure_cells:
            # roads go around structures, but through the doors of boss buildings
            if (x, y) in getattr(world, "boss_building_cells", ()) and not TILES[tile]["solid"]:
                return 1
            return None
        if tile in (",", "|"):
            return 1                         # reuse existing roads / gates
        if tile == ".":
            return 1 + max(0.0, wiggle[y][x] + 0.6) ** 2 * 30   # noise cost -> roads bend around "hills"
        return None

    def road(a, b, width=2):
        path = _astar(world, a, b, road_cost)
        if not path:
            return
        for x, y in path:
            for dx, dy in ((0, 0), (1, 0), (0, 1))[:width + 1 if width > 1 else 1]:
                nx, ny = x + dx, y + dy
                if world.tiles[ny][nx] == ".":
                    world.tiles[ny][nx] = ","
                world.protected.add((nx, ny))

    gates = {(g["from"], g["to"]): g for g in world.gates}

    def entry(gate):     # first free tile on the far side of a gate
        return gate["entry"]

    # village: nearest exit of the fixed centre -> boss -> gate to rainbow
    g = gates[("village", "rainbow_fields")]
    exit_main = min(world.exits, key=lambda e: math.hypot(e[0] - g["boss"][0], e[1] - g["boss"][1]))
    road(exit_main, g["boss"])
    road(g["boss"], g["pos"])
    # rainbow: gate -> boss -> gate to candy
    g2 = gates[("rainbow_fields", "candy")]
    road(entry(g), g2["boss"]); road(g2["boss"], g2["pos"])
    # candy: gate -> boss -> gate to separated
    g3 = gates[("candy", "separated")]
    road(entry(g2), g3["boss"]); road(g3["boss"], g3["pos"])
    # separated: gate -> portal (factory) and -> gate to tundra
    g4 = gates[("separated", "tundra")]
    portal_sep = next(p for p in world.portals if p["zone"] == "separated")
    road(entry(g3), portal_sep["pos"]); road(portal_sep["pos"], g4["pos"])
    # tundra: gate -> boss -> gate to the pass -> portal (garden)
    g5 = gates[("tundra", "tundra_pass")]
    portal_pass = next(p for p in world.portals if p["zone"] == "tundra_pass")
    road(entry(g4), g5["boss"]); road(g5["boss"], g5["pos"]); road(entry(g5), portal_pass["pos"])

    # short trails (1 wide) from the other village exits into the forest - invitation to explore
    rnd = random.Random(f"trails-{world.used_seed}")
    village_cells = [(x, y) for y in range(world.height) for x in range(world.width)
                     if world.zones[y][x] == "village" and world.tiles[y][x] == "."]
    for ex in world.exits:
        if ex == exit_main:
            continue
        far = [c for c in village_cells if 18 < math.hypot(c[0] - ex[0], c[1] - ex[1]) < 30]
        if far:
            road(ex, rnd.choice(far), width=1)


# --- 2. terrain ----------------------------------------------------------------------------
def fill_terrain(world):
    seed = world.used_seed
    forest = _field(seed * 7 + 1, 14)
    water = _field(seed * 7 + 2, 22)
    flowers = _field(seed * 7 + 3, 9)
    rnd = random.Random(f"terrain-{seed}")
    # keep a free ring next to roads/protected spots so they never feel walled in
    near_protected = set()
    for x, y in world.protected:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                near_protected.add((x + dx, y + dy))

    for y in range(world.height):
        for x in range(world.width):
            if world.tiles[y][x] != "." or (x, y) in near_protected:
                continue
            zone = world.zones[y][x]
            rules = ZONE_TERRAIN.get(zone) or BIOME_TERRAIN.get(L.ZONES.get(zone))
            if not rules:
                continue
            if rules["water"] is not None and water[y][x] > rules["water"]:
                world.tiles[y][x] = "~"
            elif forest[y][x] > rules["forest"] or rnd.random() < rules["scatter"]:
                world.tiles[y][x] = "T"
            elif rnd.random() < rules["rocks"]:
                world.tiles[y][x] = "r"
            elif rules["flowers"] is not None and flowers[y][x] > rules["flowers"]:
                world.tiles[y][x] = rules["flower_tile"]


# --- 3. reachability -----------------------------------------------------------------------
def important_points(world):
    points = [p["pos"] for p in world.pickups] + [n["pos"] for n in world.npcs] + [p["pos"] for p in world.portals]
    points += [g["boss"] for g in world.gates if g["boss"]] + [g["entry"] for g in world.gates] + list(world.exits)
    return points


def ensure_reachable(world):
    """Cuts paths (through trees / rocks / water only) to everything important the player can't reach."""
    fixed = 0
    for _ in range(40):
        reach = _flood(world, world.player_start)
        missing = [p for p in important_points(world) if p not in reach]
        if not missing:
            return fixed
        target = missing[0]

        def cut_cost(x, y):
            tile = world.tiles[y][x]
            if tile in WALKABLE:
                return 1
            if tile in OBSTACLES and (x, y) not in world.structure_cells:
                return 6                      # prefer few cuts
            return None
        # path from the target to the nearest reachable tile
        start = min(reach, key=lambda c: abs(c[0] - target[0]) + abs(c[1] - target[1]))
        path = _astar(world, start, target, cut_cost)
        if not path:
            raise RuntimeError(f"cannot reach {target}")
        for x, y in path:
            if world.tiles[y][x] in OBSTACLES:
                world.tiles[y][x] = "."
        fixed += 1
    raise RuntimeError("reachability fix did not finish")
