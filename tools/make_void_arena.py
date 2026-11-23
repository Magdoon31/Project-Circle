# The Void's arena (pixel art 1:4, 23.11): the islands (middle - big and small - and outer), the bridges (glitch
# light) and F3's belts (the factory belt in the Void's colours), each also _pale (the Pale phase: whites and greys).
# Islands: purple rock with texture seen from above (the circle = the file's width, its top = the file's top), a
# light purple rim, a short rock side below. The middle one has a ring of runes, no cracks.
# (23.11) Under each island its rock falls apart into pixels - a SEPARATE picture, the same size as the island's
# (<island>_crumble, + _frame2 ... _frame10, pale: <island>_pale_crumble...), drawn under the bridges and islands.
# Run: py tools/make_void_arena.py <folder> - into another folder, then copy over what you need.
import math, random, sys
import numpy as np
from PIL import Image

def rgb(h): return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)] + [255], np.uint8)
FRAMES = 10                                                 # (23.11) 10 frames of the falling pixels
ROCK = [rgb('#2e2048'), rgb('#3a2858'), rgb('#46326a'), rgb('#54407c')]      # dark .. light (the old fill: #3a2858)
CRACK, PEBBLE = rgb('#21163a'), rgb('#6a5498')
RIM, RIM_LIGHT, RIM_DARK, OUT = rgb('#7d5faf'), rgb('#9c80cc'), rgb('#5e4690'), rgb('#120a20')   # the old edge: #7d5faf
SIDE, SIDE_DARK, SIDE_LINE = rgb('#2a1c44'), rgb('#1e1434'), rgb('#3a2a5a')
RUNE, RUNE_LIGHT = rgb('#7660b0'), rgb('#bba0ec')
GLITCH = [rgb('#6ff2e6'), rgb('#b48af5'), rgb('#ffffff')]
# bridges: glitch light (a little see-through)
B_TILE, B_TILE_LIGHT, B_SEAM, B_SIDE, B_GLOW = rgb('#5a3fa0'), rgb('#8a6ad8'), rgb('#2e1e5a'), rgb('#3a2878'), rgb('#6ff2e6')
BRIDGE_ALPHA = 225
# belts: the factory belt in the Void's colours
V_EDGE, V_EDGE_D, V_EDGE_DD, V_HAZ_A, V_HAZ_B = rgb('#7a6a9a'), rgb('#4a3c66'), rgb('#2e2444'), rgb('#6ff2e6'), rgb('#1e1630')
V_R_LIGHT, V_R_MID, V_R_DARK, V_R_EDGE, V_BOLT = rgb('#3e3256'), rgb('#2e2442'), rgb('#201a30'), rgb('#140f20'), rgb('#b4a8d0')

ISLANDS = {"void_island_middle": (210, True), "void_island_middle_small": (165, True), "void_island_outer": (110, False)}
BRIDGES = {"short": 72, "medium": 150, "long": 212}
BRIDGE_H, BELT_H = 30, 48

def put(a, x, y, c):
    if 0 <= y < a.shape[0] and 0 <= x < a.shape[1]: a[y, x] = c

# --- islands ------------------------------------------------------------------------------------------------------
def island(width, runes, frame, seed):
    rng = random.Random(seed)
    r = width / 2
    side = max(5, int(width * 0.05))                       # the rock side under the circle (3/4 view)
    fall = int(width * 0.45)                                # how far the falling pixels reach under it
    h = width + side + fall + 2
    a = np.zeros((h, width, 4), np.uint8)
    cx = cy = r - 0.5
    yy, xx = np.mgrid[0:h, 0:width]
    d = np.hypot(xx - cx, yy - cy)
    top = d <= r - 0.5
    # the side: under every column's lowest circle pixel, `side` px of rock
    for x in range(width):
        col = np.nonzero(top[:, x])[0]
        if not len(col): continue
        y0 = col.max() + 1
        for k in range(side):
            put(a, x, y0 + k, SIDE_LINE if k == side // 2 and (x // 5) % 3 else (SIDE if k < side - 2 else SIDE_DARK))
        put(a, x, y0 + side, OUT)
    # the top: blocky texture (lumps of 4 shades), cracks, pebbles
    lump = max(3, width // 30)
    for y, x in zip(*np.nonzero(top)):
        n = (((x + (y // lump) * 3) // lump) * 73856093 ^ (y // lump) * 19349663 ^ seed) % 9
        shade = 1 if n < 4 else 2 if n < 7 else 0 if n < 8 else 3
        light = (-(x - cx) - (y - cy)) / r + ((x * 374761393 ^ y * 668265263) % 97 - 48) / 160   # lighter to the top-left (noisy edge)
        if light > 0.9 and shade < 3: shade += 1
        if light < -0.9 and shade > 0: shade -= 1
        a[y, x] = ROCK[shade]
    for _crack in range(0 if runes else int(width / 14)):                  # cracks (not on the middle island)
        x, y = rng.uniform(cx - r * 0.7, cx + r * 0.7), rng.uniform(cy - r * 0.7, cy + r * 0.7)
        ang = rng.uniform(0, math.tau)
        for _ in range(rng.randint(4, int(width / 10) + 4)):
            ix, iy = int(x), int(y)
            if 0 <= iy < h and 0 <= ix < width and top[iy, ix]: a[iy, ix] = CRACK
            ang += rng.uniform(-0.7, 0.7); x += math.cos(ang); y += math.sin(ang)
    for _p in range(int(width / 5)):
        x, y = rng.randint(0, width - 1), rng.randint(0, width - 1)
        if top[y, x]: a[y, x] = PEBBLE; put(a, x + 1, y + 1, ROCK[0]) if top[min(h - 1, y + 1), min(width - 1, x + 1)] else None
    if runes: rune_ring(a, cx, cy, r, top, rng)
    # the rim: the outer 2 px of the circle, lit top-left; then the outline
    rim = top & (d > r - 2.5)
    for y, x in zip(*np.nonzero(rim)):
        light = -(x - cx) - (y - cy)
        a[y, x] = RIM_LIGHT if light > r * 0.5 else RIM_DARK if light < -r * 0.6 else RIM
    outline = top.copy()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        outline |= np.roll(np.roll(top, dy, 0), dx, 1)
    outline &= ~top & (a[:, :, 3] == 0)
    a[outline] = OUT
    for x in range(width):                                                 # the side's left and right outline
        col = np.nonzero(a[:, x, 3])[0]
        if len(col) and a[col.max(), x].tolist() != OUT.tolist(): put(a, x, col.max() + 1, OUT)
    bits = np.zeros_like(a)
    crumble(bits, a, width, side, fall, frame, seed)
    return a, bits

def rune_ring(a, cx, cy, r, top, rng):
    """(Filip: the boss arena) A ring of lighter stone with runes on it, and a thin inner ring."""
    R = r * 0.58
    for t in range(0, 3600):
        ang = math.radians(t / 10)
        for k, col in ((0, RUNE), (1, RUNE), (2, RUNE)):
            put(a, int(round(cx + (R - k) * math.cos(ang))), int(round(cy + (R - k) * math.sin(ang))), col)
        put(a, int(round(cx + R * 0.72 * math.cos(ang))), int(round(cy + R * 0.72 * math.sin(ang))), RUNE)
    glyphs = [[(0, 0), (1, 1), (2, 2), (0, 2), (2, 0)], [(1, 0), (1, 1), (1, 2), (0, 1), (2, 1)],
              [(0, 0), (1, 0), (2, 0), (1, 1), (1, 2)], [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1)],
              [(0, 1), (1, 0), (2, 1), (1, 2)], [(0, 0), (2, 0), (1, 1), (1, 2)]]
    count = 12
    for i in range(count):                                                 # the runes sit on the ring
        ang = math.tau * i / count
        gx, gy = cx + (R - 1) * math.cos(ang) - 1, cy + (R - 1) * math.sin(ang) - 1
        for dx, dy in glyphs[i % len(glyphs)]:
            put(a, int(round(gx + dx)), int(round(gy + dy)), RUNE_LIGHT)

def crumble(bits, a, width, side, fall, frame, seed):
    """Under the island (a) the rock falls apart into pixels, drawn into `bits`: each bit falls on its own track,
    1/FRAMES of its way per frame (so the frames loop), smaller and fewer further down."""
    rng = random.Random(seed * 7 + 1)
    h = a.shape[0]
    bottoms = {}
    for x in range(width):
        col = np.nonzero(a[:, x, 3])[0]
        if len(col): bottoms[x] = col.max()
    xs = sorted(bottoms)
    span = xs[-1] - xs[0]
    for _bit in range(int(width * 3)):
        # every random number of a bit is drawn up front, so it stays the same bit in every frame
        x = rng.choice(xs)
        reach_k, phase, size_k, fade_k, glitch_k, colour_k = (rng.random() for _ in range(6))
        edge = abs(x - width / 2) / (width / 2)                           # near the middle they fall further
        reach = fall * (1 - edge ** 2) * (0.4 + 0.6 * reach_k)
        k = (phase + frame / FRAMES) % 1.0                                # how far along its track it is now
        y = bottoms[x] + 1 + int(k * reach)
        size = 3 if k < 0.2 and size_k < 0.4 else 2 if k < 0.55 and size_k < 0.7 else 1
        if k > 0.8 and fade_k < 0.5: continue                             # the last bits fade away
        c = (GLITCH[int(colour_k * 3)] if glitch_k < 0.07 else
             (ROCK[1 + int(colour_k * 3)] if k < 0.45 else ROCK[int(colour_k * 2)] if k < 0.75 else SIDE))
        for dy in range(size):
            for dx in range(size):
                if 0 <= y + dy < h and a[y + dy, min(width - 1, x + dx), 3] == 0: bits[y + dy, min(width - 1, x + dx)] = c

# --- bridges: floating tiles of glitch light (23.11, Filip: irregular, no outline) -----------------------------------
TILE_SIZES = (4, 7)               # file px: a tile's side (each its own, a bit uneven)
TILE_GAP = (1, 3)                 # file px between neighbouring tiles (each gap its own)
TILE_DEPTH = 2                    # file px of a tile's side seen below it (3/4 view)

def bridge(length):
    """Square-ish tiles hovering one by one along the bridge: uneven sizes, uneven gaps, a little off the line;
    each tile lit along its top-left, its side below it, a few of them glowing or glitched."""
    a = np.zeros((BRIDGE_H, length, 4), np.uint8)
    rng = random.Random(length * 31)
    rows = [(1, 9), (10, 18), (19, BRIDGE_H - TILE_DEPTH - 1)]                 # 3 rows of tiles across the bridge
    for top, bottom in rows:
        x = rng.randint(-2, 2)
        while x < length:
            w = rng.randint(*TILE_SIZES)
            h = min(bottom - top, rng.randint(TILE_SIZES[0], TILE_SIZES[1] + 1))
            y = top + rng.randint(0, max(0, bottom - top - h)) + rng.choice((-1, 0, 0, 1))
            glowing, glitched = rng.random() < 0.12, rng.random() < 0.1
            for ty in range(h + TILE_DEPTH):
                for tx in range(w):
                    if (tx in (0, w - 1)) and (ty in (0, h - 1)) and rng.random() < 0.7: continue   # rough corners
                    if ty >= h: c = B_SIDE                                    # its side
                    elif glowing: c = B_GLOW if (tx + ty) % 3 else GLITCH[2]
                    elif tx == 0 or ty == 0: c = B_TILE_LIGHT                 # lit edge
                    else: c = B_TILE
                    if glitched and rng.random() < 0.15: c = GLITCH[rng.randrange(3)]
                    px, py = x + tx, y + ty
                    if 0 <= px < length and 0 <= py < BRIDGE_H and a[py, px, 3] == 0:
                        a[py, px] = c; a[py, px, 3] = BRIDGE_ALPHA
            x += w + rng.randint(*TILE_GAP)
    return a

# --- F3's belts: the factory belt in the Void's colours ------------------------------------------------------------
def belt(length):
    a = np.zeros((BELT_H, length, 4), np.uint8)
    for x in range(length):
        for y in range(BELT_H):
            if y < 6 or y >= BELT_H - 6:                                   # the edges with hazard stripes
                inner = 1 <= y <= 4 if y < 6 else BELT_H - 5 <= y <= BELT_H - 2
                stripe = V_HAZ_A if ((x + y) // 3) % 2 == 0 else V_HAZ_B
                c = stripe if inner else (V_EDGE if y == 0 else V_EDGE_D if y < 6 else V_EDGE_DD)
            else:
                rib = x % 5
                c = V_R_EDGE if y in (6, BELT_H - 7) else (V_R_LIGHT if rib == 0 else V_R_DARK if rib == 4 else V_R_MID)
            a[y, x] = c
        if x % 10 == 2: a[0, x] = V_BOLT; a[BELT_H - 1, x] = V_BOLT
    return a

# --- the Pale phase --------------------------------------------------------------------------------------------------
def pale(a):
    """Whites and greys: the brightness of each pixel mapped into a light range (no colour)."""
    out = a.copy()
    rgbv = a[:, :, :3].astype(float)
    lum = (0.3 * rgbv[:, :, 0] + 0.59 * rgbv[:, :, 1] + 0.11 * rgbv[:, :, 2]) / 255
    v = (240 + (lum - 0.18) * 70).clip(205, 255)              # the ground lighter than the pale abyss (226) ...
    v = np.where(lum < 0.09, 196, v).astype(np.uint8)          # ... the outline grey, as the old pale edge
    out[:, :, 0] = out[:, :, 1] = v; out[:, :, 2] = np.minimum(255, v.astype(int) + 4).astype(np.uint8)
    return out

if __name__ == "__main__":
    folder = sys.argv[1]
    def save(name, a):
        Image.fromarray(a).save(f"{folder}/{name}.png"); Image.fromarray(pale(a)).save(f"{folder}/{name}_pale.png")
        print(name, a.shape[1], a.shape[0])
    for seed, (name, (width, runes)) in enumerate(ISLANDS.items()):
        for frame in range(FRAMES):
            tag = "" if frame == 0 else f"_frame{frame + 1}"
            a, bits = island(width, runes, frame, seed + 3)
            if frame == 0:
                Image.fromarray(a).save(f"{folder}/{name}.png"); Image.fromarray(pale(a)).save(f"{folder}/{name}_pale.png")
            Image.fromarray(bits).save(f"{folder}/{name}_crumble{tag}.png")
            Image.fromarray(pale(bits)).save(f"{folder}/{name}_pale_crumble{tag}.png")
        print(name, a.shape[1], a.shape[0])
    for size, length in BRIDGES.items():
        save(f"void_bridge_{size}", bridge(length))
        save(f"void_belt_{size}", belt(length))
