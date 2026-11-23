# Underground Garden obstacles (pixel art 1:4, 23.11): glowing cave flowers / big mushrooms / cave trees (small /
# medium / large pillars, 2 kinds each), tangled roots (thin walls) and an old garden wall with moss and vines
# (thick walls, laid out like Filip's tundra thick walls: a big top, a dark edge line, a low front).
# The cave is dark, so there are glowing accents (cyan / violet) with a faint half-transparent glow round them.
# The floor is mossy green: the shadow is a very dark green, half-transparent; outline = a very dark shade of the
# object's own colour. Run: py tools/make_garden_obstacles.py <folder>
# (23.11) Filip touched up all 6 pillars by hand afterwards - his files in assets/ are the real ones: run this
# into another folder and copy over only what you need, never straight onto assets/img/combat/obstacles.
import math, sys
import numpy as np
from PIL import Image

T, SH = (0, 0, 0, 0), (6, 16, 6, 90)              # shadow: very dark green, half-transparent
def rgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) + (255,)
GLOW, GLOW_DARK, CORE = rgb('#6ff2e6'), rgb('#36b8b0'), rgb('#e8fffb')            # cyan glow
BELL, BELL_DARK = rgb('#c58af5'), rgb('#8a52c4')                                   # violet glow
SPOT = rgb('#9ff8ef')                                                              # glowing spots
LEAF_LIGHT, LEAF, LEAF_DARK, STEM, PLANT_OUT = rgb('#6fbf6a'), rgb('#3f8a4a'), rgb('#2a6236'), rgb('#4f9a4a'), rgb('#0a1e0e')
CAP_LIGHT, CAP, CAP_DARK, MUSH_OUT = rgb('#b67ae6'), rgb('#8a4ac0'), rgb('#5e2c8e'), rgb('#1a0a28')
TEAL_LIGHT, TEAL, TEAL_DARK = rgb('#5fd0c4'), rgb('#2f9a94'), rgb('#1e6a68')
STALK, STALK_DARK = rgb('#e6dcc4'), rgb('#b8aa8c')
MOSS_LIGHT, MOSS, MOSS_DARK = rgb('#8ccf5a'), rgb('#5f9a3c'), rgb('#3f7028')
BARK_LIGHT, BARK, BARK_DARK, TREE_OUT = rgb('#7a5a3e'), rgb('#5a3f2a'), rgb('#3c2818'), rgb('#140a04')
PALE_LIGHT, PALE, PALE_DARK = rgb('#d8d0bc'), rgb('#b0a68e'), rgb('#857b64')
VINE = rgb('#3e8a3a')
CROWN_LIGHT, CROWN, CROWN_DARK = rgb('#5fb08a'), rgb('#2f7a5e'), rgb('#1d5242')       # teal-green cave leaves
GREY_LIGHT, GREY, GREY_DARK = rgb('#8a8496'), rgb('#68627a'), rgb('#4a4558')        # the willow's grey-violet bark
ROOT_LIGHT, ROOT, ROOT_DARK, ROOT_OUT = rgb('#a07a52'), rgb('#7a5636'), rgb('#553a22'), rgb('#1c1008')
THIN_ROOT, THIN_ROOT_DARK = rgb('#c49e70'), rgb('#94704a')
DIRT, DIRT_DARK = rgb('#4a3a28'), rgb('#33281a')
STONE_LIGHT, STONE_TOP, STONE_TOP2, STONE_TOP3 = rgb('#c4bca6'), rgb('#a39a86'), rgb('#968d78'), rgb('#ada490')
STONE_SEAM, BRICK, BRICK_DARK, BRICK_SEAM, WALL_OUT = rgb('#6b6453'), rgb('#8b7f6a'), rgb('#746a57'), rgb('#4f4839'), rgb('#1a170f')

class Canvas:
    def __init__(s, w, h): s.w, s.h, s.px = w, h, [[T] * w for _ in range(h)]
    def put(s, x, y, c):
        if 0 <= x < s.w and 0 <= y < s.h: s.px[y][x] = c
    def get(s, x, y): return s.px[y][x] if 0 <= x < s.w and 0 <= y < s.h else T
    def fill(s, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): s.put(x, y, c)
    def outline(s, col, solid=None):
        """A 1 px outline round everything drawn (but the shadow)."""
        solid = solid or (lambda c: c[3] == 255)
        add = []
        for y in range(s.h):
            for x in range(s.w):
                if solid(s.px[y][x]): continue
                if any(solid(s.get(x + dx, y + dy)) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))): add.append((x, y))
        for x, y in add: s.put(x, y, col)
    def shadow(s, dx=1, dy=1):
        """The shadow: the shape moved down-right, under it."""
        cells = [(x, y) for y in range(s.h) for x in range(s.w) if s.px[y][x][3] == 255]
        for x, y in cells:
            if s.get(x + dx, y + dy) == T: s.put(x + dx, y + dy, SH)
    def image(s):
        im = Image.new('RGBA', (s.w, s.h))
        for y in range(s.h):
            for x in range(s.w): im.putpixel((x, y), s.px[y][x])
        return im


# GROUND (23.11): makes a pillar sit on the ground - a shadow the object casts on the ground (each pixel's shadow
# lands down-right, the further the higher the pixel is: a tree lays a long cone), a darker contact shadow right
# under its base, and a few crumbs (here: moss) at its foot. Only empty pixels are filled - the drawing stays as it is.
# The picture gets PAD empty columns on both sides and just enough rows below the base first, so the shadow fits (the game centres it anyway).

SHADOW = (6, 16, 6)
CAST_ALPHA, CONTACT_ALPHA = 70, 110
LEAN_X, LEAN_Y = 0.38, 0.16        # a pixel h px above the ground: its shadow lands h*LEAN_X right, h*LEAN_Y down
CRUMB_LIGHT, CRUMB_SHADE = (95, 154, 60), (63, 112, 40)      # moss crumbs

def ground(im, pad=4, crumbs=True):
    src = np.array(im.convert('RGBA'))
    sh, w = src.shape[:2]
    rows = np.nonzero((src[:, :, 3] == 255).any(axis=1))[0]
    below = 3 + int((rows.max() - rows.min()) * LEAN_Y) if len(rows) else 0   # room under the base for the shadow
    h = rows.max() + 1 + below if len(rows) else sh
    out = np.zeros((h, w + 2 * pad, 4), np.uint8)
    out[:min(sh, h), pad:pad + w] = src[:min(sh, h)]
    solid = out[:, :, 3] == 255
    ys, xs = np.nonzero(solid)
    if not len(ys): return Image.fromarray(out)
    base = ys.max()                                           # the ground line = the lowest drawn row
    empty = lambda x, y: 0 <= y < h and 0 <= x < out.shape[1] and out[y, x, 3] == 0
    def shade(x, y, a):
        if 0 <= y < h and 0 <= x < out.shape[1] and out[y, x, 3] < 255:
            out[y, x, :3] = SHADOW
            out[y, x, 3] = max(out[y, x, 3], a)
    for y, x in zip(ys, xs):                                  # the cast shadow
        lift = base - y
        sx, sy = x + lift * LEAN_X, base + 1 + lift * LEAN_Y
        for dx in (0, 1):
            shade(int(round(sx)) + dx, int(round(sy)), CAST_ALPHA)
    foot = xs[ys >= base - 1]                                 # the contact shadow under the base
    left, right = foot.min(), foot.max()
    for x in range(left - 1, right + 3):
        shade(x, base + 1, CONTACT_ALPHA)
        if left <= x <= right + 1: shade(x, base + 2, CAST_ALPHA)
    if not crumbs: return Image.fromarray(out)                # (23.11) the drawing has its own crumbs
    for x, col in ((left - 1, CRUMB_LIGHT), (left - 2, CRUMB_SHADE), (right + 1, CRUMB_SHADE)):   # snow crumbs at the foot
        if empty(x, base) or out[base, x, 3] < 255:
            out[base, x, :3] = col; out[base, x, 3] = 255
    if 0 <= left - 1 and (out[base - 1, left - 1, 3] < 255): out[base - 1, left - 1, :3] = CRUMB_LIGHT; out[base - 1, left - 1, 3] = 255
    return Image.fromarray(out)


def glow(cv, cells, colour, alpha=70):
    """(23.11) A faint glow round glowing pixels: half-transparent, only on empty pixels (not solid for collision)."""
    halo = (colour[0], colour[1], colour[2], alpha)
    for x, y in cells:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if cv.get(x + dx, y + dy)[3] == 0: cv.put(x + dx, y + dy, halo)

def blob(cv, cx, cy, rx, ry, colour):
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1: cv.put(x, y, colour)

def noise(x, y, seed=0):
    """A fixed pseudo-random number 0..99 for a pixel (the same every run)."""
    return (x * 374761393 + y * 668265263 + seed * 2654435761) % 1000003 % 100

# --- small pillars: glowing cave flowers ---------------------------------------------------------------------
def flowers(kind):
    cv = Canvas(20, 20)
    petal, petal_dark = (GLOW, GLOW_DARK) if kind == 0 else (BELL, BELL_DARK)
    for x0, x1, y0 in ((4, 9, 13), (10, 16, 12), (7, 12, 15)):            # leaves round the foot
        for x in range(x0, x1 + 1):
            top = y0 + abs(x - (x0 + x1) / 2) * 0.5
            for y in range(int(top), 18): cv.put(x, y, LEAF if x < (x0 + x1) / 2 else LEAF_DARK)
    stems = [(6, 6), (10, 3), (14, 5)] if kind == 0 else [(5, 7), (9, 4), (13, 3), (15, 8)]
    lit = []
    for sx, top in stems:
        for y in range(top + 2, 15): cv.put(sx, y, STEM)
        if kind == 0:                                                       # a round glowing flower
            for dx, dy in ((0, 0), (-1, 1), (1, 1), (0, 2), (-1, 0), (1, 0), (0, 1)):
                cv.put(sx + dx, top + dy, petal if dy < 2 else petal_dark)
            cv.put(sx, top + 1, CORE); lit += [(sx + dx, top + dy) for dx in (-1, 0, 1) for dy in (0, 1, 2)]
        else:                                                               # a hanging glowing bell
            cv.put(sx, top + 1, STEM); cv.put(sx + 1, top + 2, petal); cv.put(sx + 1, top + 3, petal)
            cv.put(sx + 2, top + 3, petal_dark); cv.put(sx, top + 3, petal); cv.put(sx + 1, top + 4, CORE)
            lit += [(sx + 1, top + 2), (sx, top + 3), (sx + 1, top + 3), (sx + 2, top + 3), (sx + 1, top + 4)]
    cv.outline(PLANT_OUT)
    glow(cv, lit, petal)
    return cv

# --- medium pillars: big mushrooms ------------------------------------------------------------------------------
def mushroom(cv, cx, cap_y, rx, ry, stem_w, stem_bottom, cap, cap_dark, cap_light, spots):
    for y in range(cap_y + ry - 1, stem_bottom + 1):                     # the stem
        for x in range(cx - stem_w, cx + stem_w + 1):
            cv.put(x, y, STALK if x < cx + stem_w - 1 else STALK_DARK)
    for y in range(cap_y - ry, cap_y + ry + 1):                          # the cap (a half dome)
        for x in range(cx - rx - 1, cx + rx + 2):
            k = ((x - cx) / (rx + 0.5)) ** 2 + ((y - cap_y) / ry) ** 2
            if k <= 1 and y <= cap_y + ry // 3:
                c = cap_light if (x - cx) < -rx * 0.4 and y < cap_y else (cap if x - cx < rx * 0.45 else cap_dark)
                cv.put(x, y, c)
    for x in range(cx - rx, cx + rx + 1): cv.put(x, cap_y + ry // 3 + 1, cap_dark)   # the cap's rim
    lit = []
    for dx, dy in spots:
        cv.put(cx + dx, cap_y + dy, SPOT); lit.append((cx + dx, cap_y + dy))
    return lit

def big_mushroom(kind):
    cv = Canvas(28, 28)
    if kind == 0:
        lit = mushroom(cv, 13, 10, 10, 7, 2, 24, CAP, CAP_DARK, CAP_LIGHT, [(-5, -3), (-1, -5), (3, -2), (6, -4), (0, 0), (-6, 1)])
    else:                                                                   # three mushrooms together
        lit = mushroom(cv, 18, 13, 6, 5, 1, 24, TEAL, TEAL_DARK, TEAL_LIGHT, [(-2, -3), (2, -1)])
        lit += mushroom(cv, 9, 8, 7, 5, 2, 24, CAP, CAP_DARK, CAP_LIGHT, [(-3, -2), (1, -4), (3, -1)])
        lit += mushroom(cv, 13, 19, 4, 3, 1, 24, TEAL, TEAL_DARK, TEAL_LIGHT, [(-1, -1)])
    for x in range(5, 23):                                                  # moss at the foot
        if noise(x, 0, kind) < 70: cv.put(x, 24 - (noise(x, 1, kind) < 30), MOSS)
    cv.outline(MUSH_OUT)
    glow(cv, lit, SPOT, 55)
    return cv

# --- large pillars: cave trees ------------------------------------------------------------------------------------
def canopy(cv, blobs, dark, mid, light):
    """A leafy crown of clumps: each clump dark, a lit part up-left, a small highlight."""
    for cx, cy, rx, ry in blobs: blob(cv, cx, cy, rx, ry, dark)
    for cx, cy, rx, ry in blobs: blob(cv, cx - 1, cy - 1, rx - 1.2, ry - 1, mid)
    for cx, cy, rx, ry in blobs: blob(cv, cx - rx * 0.4, cy - ry * 0.45, max(1, rx * 0.35), max(0.8, ry * 0.3), light)

def trunk(cv, top, bottom, half, colours, sway=1.0, prongs=True):
    light, mid, dark = colours
    for y in range(top, bottom + 1):
        c = 18 + int(round(math.sin(y / 4) * sway))
        for x in range(int(c - half), int(c + half) + 1):
            k = x - c
            cv.put(x, y, light if k < -half * 0.35 else (mid if k < half * 0.4 else dark))
        if noise(c, y, 3) < 30: cv.put(c, y, dark)                             # bark grooves
    if prongs:                                                                 # roots spreading at the foot
        for i in range(4):
            y = bottom - 3 + i
            for x in (18 - half - 1 - i, 18 - half - 2 - i): cv.put(int(x), y, light if i < 2 else mid)
            for x in (18 + half + 1 + i, 18 + half + 2 + i): cv.put(int(x), y, dark)

def cave_tree(kind):
    cv = Canvas(36, 36)
    lit = []
    if kind == 0:                                                           # a gnarled cave tree, leafy crown
        trunk(cv, 12, 30, 2, (BARK_LIGHT, BARK, BARK_DARK))
        canopy(cv, [(18, 12, 9, 4), (10, 13, 5, 3.5), (26, 13, 5, 3.5), (13, 7, 6, 4), (23, 7, 6, 4), (18, 4, 5, 3)],
               CROWN_DARK, CROWN, CROWN_LIGHT)
        for fx, fy in ((10, 15), (17, 15), (25, 15), (14, 10), (22, 9)):    # glowing fruit
            cv.put(fx, fy, GLOW); lit.append((fx, fy))
        for sx, sy in ((19, 21), (16, 25)):                                  # glowing shelf fungi on the trunk
            cv.put(sx, sy, SPOT); cv.put(sx + 1, sy, SPOT); lit += [(sx, sy), (sx + 1, sy)]
    else:                                                                   # a cave willow
        trunk(cv, 14, 30, 1.6, (GREY_LIGHT, GREY, GREY_DARK), sway=1.5)
        canopy(cv, [(18, 9, 11, 4), (12, 7, 6, 3), (24, 7, 6, 3), (18, 5, 6, 3)], LEAF_DARK, LEAF, LEAF_LIGHT)
        for vx in range(8, 30, 2):                                          # drooping strands, glowing tips
            length = 6 + noise(vx, 2) % 8
            for y in range(12, 12 + length): cv.put(vx, y, LEAF if (vx // 2) % 2 else LEAF_DARK)
            if noise(vx, 5) < 45: cv.put(vx, 12 + length, BELL); lit.append((vx, 12 + length))
    cv.outline(TREE_OUT)
    glow(cv, lit, GLOW if kind == 0 else BELL, 55)
    return cv

# --- thin walls: tangled roots -------------------------------------------------------------------------------------
def root_colour(k, half):
    return ROOT_LIGHT if k < -half * 0.3 else (ROOT if k < half * 0.4 else ROOT_DARK)

def roots_h():
    cv = Canvas(16, 12)
    for x in range(16):                                                     # the thick root (behind)
        a = 6.5 + 1.2 * math.sin(x / 16 * 2 * math.pi)
        for y in range(int(round(a - 2)), int(round(a + 1.5)) + 1): cv.put(x, y, root_colour(y - a, 2))
    for x in range(16):                                                     # a thin pale root winding round it
        b = 6.5 - 3 * math.sin(x / 16 * 2 * math.pi + 1.2)
        front = math.cos(x / 16 * 2 * math.pi + 1.2) > -0.2                 # in front of the thick one or behind it
        y = int(round(b))
        for yy, c in ((y, THIN_ROOT), (y + 1, THIN_ROOT_DARK)):
            if front or cv.get(x, yy)[3] == 0: cv.put(x, yy, c)
    cv.put(9, 9, ROOT_DARK); cv.put(10, 10, ROOT_DARK)                      # a rootlet going into the ground
    cv.outline(ROOT_OUT); cv.shadow()
    return cv

def roots_h_end():
    """The left end: the roots dive into the ground."""
    mid = roots_h()
    cv = Canvas(8, 12)
    for x in range(8):
        keep = x / 7                                                         # less root the further left
        for y in range(12):
            c = mid.get(x, y)
            if c[3] == 255 and c != ROOT_OUT and y < 9 - keep * 6: continue
            if c[3] == 255 and c != ROOT_OUT: cv.put(x, y, c)
    cv.outline(ROOT_OUT); cv.shadow()
    cv.put(1, 9, DIRT); cv.put(2, 9, DIRT); cv.put(0, 9, DIRT_DARK)          # the soil it comes out of
    return cv

def roots_v():
    cv = Canvas(12, 16)
    for y in range(16):
        a = 6 + 1.2 * math.sin(y / 16 * 2 * math.pi)
        for x in range(int(round(a - 2)), int(round(a + 1.5)) + 1): cv.put(x, y, root_colour(x - a, 2))
    for y in range(16):
        b = 6 - 3 * math.sin(y / 16 * 2 * math.pi + 1.2)
        front = math.cos(y / 16 * 2 * math.pi + 1.2) > -0.2
        x = int(round(b))
        for xx, c in ((x, THIN_ROOT), (x + 1, THIN_ROOT_DARK)):
            if front or cv.get(xx, y)[3] == 0: cv.put(xx, y, c)
    cv.outline(ROOT_OUT); cv.shadow()
    return cv

def roots_v_cap(top_piece):
    mid = roots_v()
    cv = Canvas(12, 6)
    for y in range(6):
        cut = (5 - y) if top_piece else y                                   # how far it narrows (rounded end)
        for x in range(12):
            c = mid.get(x, y if top_piece else y + 10)
            if c[3] == 255 and c != ROOT_OUT and abs(x - 6) <= 4 - max(0, cut - 2) * 1.5: cv.put(x, y, c)
    cv.outline(ROOT_OUT); cv.shadow()
    if not top_piece: cv.put(3, 5, DIRT); cv.put(8, 5, DIRT); cv.put(9, 5, DIRT_DARK)
    return cv

# --- thick walls: the old garden wall (laid out like Filip's tundra thick walls) ----------------------------------
def stone(x, y, row):
    """A stone's colour by which stone it is (they differ a little: an old wall)."""
    pick = noise(x // 8, row, 7) % 3
    return (STONE_TOP, STONE_TOP2, STONE_TOP3)[pick]

MOSS_PATCHES = {                         # (x, y, rx, ry) moss patches on the wall's top, in one 16 px tile
    1: [(2, 3, 3, 1.6), (11, 9, 3.5, 2), (7, 12, 2.5, 1.2), (15, 1, 2, 1)],
    6: [(5, 2, 2.5, 1.4), (13, 6, 3, 2), (2, 10, 3, 1.8), (9, 12, 2, 1)],
    2: [(5, 2, 2, 3), (12, 9, 2.5, 3.5), (8, 14, 1.5, 2), (16, 5, 1.5, 2)],
    9: [(14, 3, 2, 2.5), (6, 8, 2.5, 3), (11, 14, 1.8, 2)],
}

def mossy(x, y, seed):
    """Is (x, y) under a moss patch? The patches repeat every 16 px (along the wall), so the pieces fit."""
    return any(((x % 16 - px + dx) / rx) ** 2 + ((y - py) / ry) ** 2 <= 1
               for px, py, rx, ry in MOSS_PATCHES[seed] for dx in (-16, 0, 16))

def wall_thick_h(variant=0):
    cv = Canvas(16, 22)
    cv.fill(0, 0, 15, 0, WALL_OUT)
    for i in range(12):                                                     # the top: stones seen from above
        y = 1 + i
        row, off = (0, 0) if i < 6 else (1, 4)
        off += variant * 3
        for x in range(16):
            if i == 5 or (x + off) % 8 == 7: c = STONE_SEAM
            else: c = STONE_LIGHT if i == 0 else stone(x + off, y, row + variant * 2)
            if mossy(x, y, 6 if variant else 1): c = MOSS_LIGHT if mossy(x + 1, y + 1, 6 if variant else 1) and i < 4 else (MOSS if i < 11 else MOSS_DARK)
            cv.put(x, y, c)
    cv.fill(0, 13, 15, 13, WALL_OUT)
    for i in range(6):                                                      # the low front: bricks
        y = 14 + i
        off = (0 if i < 3 else 4) + variant * 5
        for x in range(16):
            seam = i == 2 or i == 5 or (x + off) % 8 == 7
            cv.put(x, y, BRICK_SEAM if seam else (BRICK if i in (0, 3) else BRICK_DARK))
    vines = (3, 11) if variant == 0 else (6, 14)
    for n, vx in enumerate(vines):                                           # vines hanging down the front
        for y in range(14, 14 + 3 + n * 2): cv.put(vx, y, VINE)
        if n == 0: cv.put(vx, 14 + 3, GLOW)
    cv.fill(0, 20, 15, 20, WALL_OUT); cv.fill(0, 21, 15, 21, SH)
    return cv

def wall_thick_h_end():
    mid = wall_thick_h()
    cv = Canvas(6, 22)
    for y in range(22):
        for x in range(6): cv.put(x, y, mid.get(x + 8, y))
    for y in range(1, 20): cv.put(0, y, WALL_OUT)
    for y in range(1, 13): cv.put(1, y, STONE_LIGHT)
    for y in range(14, 20): cv.put(1, y, BRICK_SEAM)
    cv.put(0, 0, T); cv.put(0, 20, T); cv.put(0, 21, T); cv.put(1, 1, WALL_OUT)
    return cv

def thick_v_top_face(cv, y0, y1, variant=0):
    for y in range(y0, y1 + 1):
        row = y // 8
        for x in range(2, 20):
            off = (0 if row % 2 == 0 else 3) + variant * 2
            if y % 8 == 7 or (x + off) % 6 == 5: c = STONE_SEAM
            else: c = STONE_LIGHT if x < 4 else stone(x * 2 + off, y, row + variant * 3)
            if mossy(y, x, 9 if variant else 2) and x > 2: c = MOSS if x < 17 else MOSS_DARK
            cv.put(x, y, c)

def wall_thick_v(variant=0):
    cv = Canvas(22, 16)
    thick_v_top_face(cv, 0, 15, variant)
    for y in range(16): cv.put(1, y, WALL_OUT); cv.put(20, y, WALL_OUT); cv.put(21, y, SH)
    return cv

def wall_thick_v_top():
    cv = Canvas(22, 6)
    thick_v_top_face(cv, 1, 5)
    cv.fill(2, 0, 19, 0, WALL_OUT)
    for y in range(1, 6): cv.put(1, y, WALL_OUT); cv.put(20, y, WALL_OUT); cv.put(21, y, SH)
    return cv

def wall_thick_v_end():
    cv = Canvas(22, 12)
    thick_v_top_face(cv, 0, 2)
    cv.fill(1, 3, 20, 3, WALL_OUT)
    for i in range(6):
        y = 4 + i
        off = 0 if i < 3 else 3
        for x in range(2, 20):
            seam = i == 2 or i == 5 or (x + off) % 6 == 5
            cv.put(x, y, BRICK_SEAM if seam else (BRICK if i in (0, 3) else BRICK_DARK))
    for y in range(4, 7): cv.put(7, y, VINE)
    cv.put(7, 7, GLOW)
    for y in range(0, 10): cv.put(1, y, WALL_OUT); cv.put(20, y, WALL_OUT); cv.put(21, y, SH)
    cv.fill(1, 10, 20, 10, WALL_OUT); cv.fill(2, 11, 21, 11, SH)
    return cv

SPRITES = {
    "underground_garden_wall_h": roots_h, "underground_garden_wall_h_end": roots_h_end,
    "underground_garden_wall_v": roots_v, "underground_garden_wall_v_top": lambda: roots_v_cap(True),
    "underground_garden_wall_v_end": lambda: roots_v_cap(False),
    "underground_garden_wall_thick_h": lambda: wall_thick_h(0), "underground_garden_wall_thick_h_2": lambda: wall_thick_h(1),
    "underground_garden_wall_thick_h_end": wall_thick_h_end,
    "underground_garden_wall_thick_v": lambda: wall_thick_v(0), "underground_garden_wall_thick_v_2": lambda: wall_thick_v(1),
    "underground_garden_wall_thick_v_top": wall_thick_v_top, "underground_garden_wall_thick_v_end": wall_thick_v_end,
}
for i, suffix in enumerate(["", "_2"]):
    SPRITES[f"underground_garden_pillar_small{suffix}"] = (lambda k: lambda: flowers(k))(i)
    SPRITES[f"underground_garden_pillar_medium{suffix}"] = (lambda k: lambda: big_mushroom(k))(i)
    SPRITES[f"underground_garden_pillar_large{suffix}"] = (lambda k: lambda: cave_tree(k))(i)

if __name__ == "__main__":
    for name, make in SPRITES.items():
        im = make().image()
        if "pillar" in name: im = ground(im)
        im.save(f"{sys.argv[1]}/{name}.png"); print(name, im.size)
