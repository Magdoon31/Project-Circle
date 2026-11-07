# STEP 2: layout of zones on the SURFACE map (from the author's sketch).
#
# A ZONE is a piece of the map; every zone has a BIOME (the biome of its tiles).
# Each zone is made of a few circles ("anchors") roughly copying the sketch.
# The seed bends the borders with noise, but the order and neighbours never change:
# the result is checked against REQUIRED / FORBIDDEN neighbours and regenerated if wrong.

import math, random
from collections import deque
from game.world.noise import ValueNoise

WIDTH, HEIGHT = 220, 260          # surface size in tiles

# zone -> biome
ZONES = {
    "village":        "village",
    "rainbow_fields": "rainbow_fields",
    "candy":          "sugarwood_grove",
    "separated":      "village",            # village biome, link between candy and tundra/factory
    "tundra":         "silverpine_tundra",
    "tundra_pass":    "silverpine_tundra",  # small area behind the tundra boss, portal to the garden
}

# anchors: (x, y, radius) in sketch pixels (sketch ~ 800x600, surface part x 30-460, y 50-580)
ANCHORS = {
    "village":        [(215, 160, 92), (165, 205, 55)],
    "rainbow_fields": [(100, 288, 68), (105, 390, 60), (120, 490, 45)],
    "candy":          [(225, 400, 70), (185, 500, 55), (238, 335, 42)],
    "separated":      [(222, 272, 42)],
    "tundra":         [(352, 290, 105), (330, 380, 55)],
    "tundra_pass":    [(392, 188, 28)],
}
SKETCH_X0, SKETCH_Y0, SKETCH_SCALE = 25, 40, 0.5    # sketch px -> tiles

# borders that must exist (walkable later through a gate or plain wall - step 3 decides)
REQUIRED_NEIGHBOURS = {
    ("village", "rainbow_fields"), ("rainbow_fields", "candy"), ("candy", "separated"),
    ("separated", "tundra"), ("tundra", "tundra_pass"),
}
# borders that must NOT exist (would create a shortcut around the progression)
FORBIDDEN_NEIGHBOURS = {
    ("rainbow_fields", "tundra"), ("rainbow_fields", "tundra_pass"), ("candy", "tundra_pass"),
    ("separated", "tundra_pass"), ("candy", "village"),
}

OUTSIDE = None    # tile outside every zone (will be impassable terrain)

# the fixed village centre (prefab village_start, 48x25) is placed with its middle here
VILLAGE_CENTRE = (95, 50)
VILLAGE_PREFAB_SIZE = (48, 25)


def village_prefab_rect():
    w, h = VILLAGE_PREFAB_SIZE
    return VILLAGE_CENTRE[0] - w // 2, VILLAGE_CENTRE[1] - h // 2, w, h


def _anchors_in_tiles():
    result = {}
    for zone, anchors in ANCHORS.items():
        result[zone] = [((x - SKETCH_X0) * SKETCH_SCALE, (y - SKETCH_Y0) * SKETCH_SCALE, r * SKETCH_SCALE) for x, y, r in anchors]
    return result


def generate_zones(seed, warp=14.0):
    """Returns (grid, used_seed): grid[y][x] = zone name or OUTSIDE."""
    attempt = 0
    while True:
        # retry with a seed derived from the original one (seed+1 would just copy the next seed's world)
        used_seed = seed if attempt == 0 else random.Random(f"{seed}-{attempt}").randrange(1, 2**31)
        grid = _try_generate(used_seed, warp)
        if validate(grid) is None:
            return grid, used_seed
        attempt += 1
        if attempt > 50:
            raise RuntimeError("could not generate a valid layout")


def _coarse_field(noise, scale, step=4):
    # noise sampled every `step` tiles and smoothly interpolated - same look, ~15x faster
    cw, ch = WIDTH // step + 2, HEIGHT // step + 2
    coarse = [[noise.fractal(cx * step / scale, cy * step / scale) for cx in range(cw)] for cy in range(ch)]
    field = [[0.0] * WIDTH for _ in range(HEIGHT)]
    for y in range(HEIGHT):
        cy, fy = divmod(y, step)
        ty = fy / step
        row0, row1 = coarse[cy], coarse[cy + 1]
        out = field[y]
        for x in range(WIDTH):
            cx, fx = divmod(x, step)
            tx = fx / step
            a = row0[cx] + (row0[cx + 1] - row0[cx]) * tx
            b = row1[cx] + (row1[cx + 1] - row1[cx]) * tx
            out[x] = a + (b - a) * ty
    return field


def _try_generate(seed, warp):
    warp_x = _coarse_field(ValueNoise(seed * 3 + 1), 40)
    warp_y = _coarse_field(ValueNoise(seed * 3 + 2), 40)
    edge = _coarse_field(ValueNoise(seed * 3 + 3), 25)
    circles = [(zone, cx, cy, 1.0 / r) for zone, anchors in _anchors_in_tiles().items() for cx, cy, r in anchors]
    grid = [[OUTSIDE] * WIDTH for _ in range(HEIGHT)]
    for y in range(HEIGHT):
        for x in range(WIDTH):
            # domain warp: look up a slightly moved point -> wavy borders
            wx = x + warp_x[y][x] * warp
            wy = y + warp_y[y][x] * warp
            best_zone, best = OUTSIDE, 1e18
            for zone, cx, cy, inv_r in circles:
                d = ((wx - cx) ** 2 + (wy - cy) ** 2) * inv_r * inv_r     # squared, no sqrt needed
                if d < best:
                    best, best_zone = d, zone
            # outer edge of the world is also wavy
            limit = 1.0 + edge[y][x] * 0.25
            if best < limit * limit:
                grid[y][x] = best_zone
    _remove_islands(grid)
    return grid


def _remove_islands(grid):
    # every zone must be ONE connected piece: smaller pieces are given to the neighbouring zone
    seen = [[False] * WIDTH for _ in range(HEIGHT)]
    pieces = {}
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if grid[y][x] is OUTSIDE or seen[y][x]:
                continue
            zone = grid[y][x]
            cells, queue = [], deque([(x, y)])
            seen[y][x] = True
            while queue:
                cx, cy = queue.popleft()
                cells.append((cx, cy))
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and not seen[ny][nx] and grid[ny][nx] == zone:
                        seen[ny][nx] = True
                        queue.append((nx, ny))
            pieces.setdefault(zone, []).append(cells)
    for zone, zone_pieces in pieces.items():
        zone_pieces.sort(key=len, reverse=True)
        for small in zone_pieces[1:]:
            replacement = OUTSIDE
            for cx, cy in small:
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and grid[ny][nx] not in (zone, OUTSIDE):
                        replacement = grid[ny][nx]
                        break
                if replacement is not OUTSIDE:
                    break
            for cx, cy in small:
                grid[cy][cx] = replacement


def neighbours(grid):
    pairs = {}
    for y in range(HEIGHT - 1):
        for x in range(WIDTH - 1):
            a = grid[y][x]
            for b in (grid[y][x + 1], grid[y + 1][x]):
                if a is not OUTSIDE and b is not OUTSIDE and a != b:
                    key = tuple(sorted((a, b)))
                    pairs[key] = pairs.get(key, 0) + 1
    return pairs   # (zone_a, zone_b) -> length of the shared border


def gate_spots(grid, a, b, clearance):
    """Tiles of zone a touching zone b with only zones a/b within `clearance` tiles
    (a gate there won't touch a third zone or the edge of the world)."""
    cells = []
    r = clearance
    for y in range(r, HEIGHT - r):
        for x in range(r, WIDTH - r):
            if grid[y][x] != a:
                continue
            if not any(grid[y + dy][x + dx] == b for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                continue
            if all(grid[y + dy][x + dx] in (a, b) for dx in range(-r, r + 1) for dy in range(-r, r + 1)):
                cells.append((x, y))
    return cells


GATE_MIN_CLEARANCE = 3


def validate(grid, min_border=6):
    """None if OK, otherwise a text with the problem."""
    # fixed village centre (+3 tiles of forest around it) must lie fully in the village zone
    px, py, pw, ph = village_prefab_rect()
    for y in range(py - 3, py + ph + 3):
        for x in range(px - 3, px + pw + 3):
            if grid[y][x] != "village":
                return "village centre does not fit"
    pairs = neighbours(grid)
    for a, b in REQUIRED_NEIGHBOURS:
        if pairs.get(tuple(sorted((a, b))), 0) < min_border:
            return f"missing border {a}-{b}"
    # every required border needs room for a gate
    for a, b in REQUIRED_NEIGHBOURS:
        if len(gate_spots(grid, a, b, GATE_MIN_CLEARANCE)) < 3:
            return f"no room for a gate {a}-{b}"
    for a, b in FORBIDDEN_NEIGHBOURS:
        if tuple(sorted((a, b))) in pairs:
            return f"forbidden border {a}-{b}"
    return None
