# Silverpine Tundra obstacles (pixel art 1:4): snowdrifts (thin walls), a wall of packed snow blocks (thick walls),
# snowman / ice block / snowy spruce (small / medium / large pillars, 3 kinds each). The floor is almost white, so
# snow gets blue shades and a very dark blue outline (outline = a very dark shade of the object's colour, 23.11).
import math, sys
import numpy as np
from PIL import Image

T, SH = (0, 0, 0, 0), (20, 40, 70, 70)              # shadow: dark blue, half-transparent (black looks dirty on snow)
def rgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) + (255,)
SW, S1, S2, S3, SO = rgb('#ffffff'), rgb('#e1edf8'), rgb('#b4cce2'), rgb('#86a6c6'), rgb('#0e1a2c')    # snow
IL, IM, ID, IO, IW = rgb('#a8e6fa'), rgb('#62c0e8'), rgb('#3a8cc4'), rgb('#06223a'), rgb('#f2fcff')    # ice
GL, GM, GD, GO = rgb('#4f9466'), rgb('#2f6b4a'), rgb('#1f4c35'), rgb('#06180e')                      # spruce
TL, TD, TO = rgb('#8a5a36'), rgb('#5e3b20'), rgb('#1e1006')                                          # trunk, sticks
CARROT, COAL = rgb('#f08a24'), rgb('#1a1a22')
SCARVES = [(rgb('#e2404a'), rgb('#9e2030')), (rgb('#4fb85a'), rgb('#2c7a36')), (rgb('#4a8ee2'), rgb('#2a5aa0'))]

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

def ball(cv, cx, cy, r, light=SW, mid=S1, dark=S2, deep=S3):
    """A snow ball, lit from the top left."""
    for y in range(cv.h):
        for x in range(cv.w):
            d = math.hypot(x - cx, y - cy)
            if d <= r:
                k = (x - cx) + (y - cy)
                cv.put(x, y, light if k < -r * 0.5 else (mid if k < r * 0.35 else (dark if k < r * 0.95 else deep)))

# --- small: snowmen ---------------------------------------------------------------------------------------
def snowman(kind):
    cv = Canvas(20, 20)
    ball(cv, 9.5, 13.5, 5.2)                                                # body
    ball(cv, 9.5, 6.5, 3.6)                                                 # head
    scarf, scarf_d = SCARVES[kind]
    for x in range(7, 13): cv.put(x, 10, scarf if x < 11 else scarf_d)      # scarf
    cv.put(11, 11, scarf); cv.put(11, 12, scarf_d)
    cv.put(8, 6, COAL); cv.put(11, 6, COAL)                                  # eyes
    cv.put(10, 7, CARROT); cv.put(11, 7, CARROT)                             # nose
    for y in (12, 14): cv.put(9, y, COAL)                                    # buttons
    if kind == 1:                                                            # a top hat
        cv.fill(7, 2, 12, 2, COAL); cv.fill(8, 0, 11, 1, COAL); cv.put(9, 1, rgb('#4a4a5a'))
    if kind == 2:                                                            # a bucket
        cv.fill(7, 2, 12, 3, rgb('#8a96a8')); cv.fill(8, 1, 11, 1, rgb('#b8c4d4'))
    for (x, y) in [(4, 11), (3, 10), (2, 9)] if kind != 1 else [(4, 12), (3, 12), (2, 11)]:   # stick arms
        cv.put(x, y, TD)
    for (x, y) in [(15, 11), (16, 10), (17, 9)]:
        cv.put(x, y, TD)
    cv.outline(SO); cv.shadow()
    return cv

# --- medium: ice blocks -----------------------------------------------------------------------------------
def ice_block(kind):
    cv = Canvas(28, 28)
    if kind == 0:                                                            # a cube: top face + front
        cv.fill(4, 4, 23, 10, IL); cv.fill(4, 11, 23, 23, IM); cv.fill(19, 11, 23, 23, ID)
        cv.fill(4, 11, 23, 11, IO)
    elif kind == 1:                                                          # a slanted chunk
        for y in range(3, 24):
            x0 = 6 - min(3, (y - 3) // 3); x1 = 20 + min(4, (y - 3) // 2)
            cv.fill(x0, y, x1, y, IL if y < 10 else (IM if y < 19 else ID))
        cv.fill(15, 10, 24, 23, ID)
    else:                                                                    # two stacked blocks
        cv.fill(3, 12, 24, 17, IL); cv.fill(3, 18, 24, 24, IM); cv.fill(20, 18, 24, 24, ID); cv.fill(3, 18, 24, 18, IO)
        cv.fill(8, 3, 19, 7, IL); cv.fill(8, 8, 19, 12, IM); cv.fill(16, 8, 19, 12, ID); cv.fill(8, 8, 19, 8, IO)
    for (x, y) in [(6, 6), (7, 6), (6, 7), (9, 14), (10, 15)]:              # shine
        if cv.get(x, y)[3]: cv.put(x, y, IW)
    for (x, y) in [(13, 15), (14, 16), (14, 17), (15, 18), (12, 19)]:        # a crack
        if cv.get(x, y)[3]: cv.put(x, y, ID)
    cv.outline(IO); cv.shadow()
    return cv

# --- large: snowy spruces ---------------------------------------------------------------------------------
def spruce(kind):
    """3 kinds: an ordinary spruce, a tall thin one, a low wide one. Each tier: needles shaded left-light /
    right-dark, a snow cap lying on its upper part (thicker on the lit side)."""
    cv = Canvas(36, 36)
    cx = 17.5
    shapes = {0: dict(tiers=5, top=3, step=5, height=7, half0=3, grow=2.1, trunk=(27, 32)),     # (23.11) narrower
              1: dict(tiers=6, top=1, step=4, height=6, half0=2.5, grow=1.55, trunk=(26, 32)),
              2: dict(tiers=4, top=7, step=5, height=7, half0=6, grow=3.6, trunk=(28, 32))}[kind]
    t0, t1 = shapes["trunk"]
    cv.fill(16, t0, 19, t1, TL); cv.fill(18, t0, 19, t1, TD)
    for i in range(shapes["tiers"]):
        top = shapes["top"] + i * shapes["step"]
        half = shapes["half0"] + i * shapes["grow"]
        for dy in range(shapes["height"]):
            y = top + dy
            w = max(1.0, half * (dy + 1) / shapes["height"])
            for x in range(int(round(cx - w)), int(round(cx + w)) + 1):
                k = x - cx
                band = GL if k < -w * 0.35 else (GM if k < w * 0.35 else GD)
                if (x * 7 + y * 13 + kind * 5) % 11 == 0 and w > 2:     # (23.11) dither like Filip's edits:
                    band = GM if band != GM else (GD if k > 0 else GL)   # a stray pixel of the next shade
                cv.put(x, y, band)
            snow_w = w * (0.85 if dy < 2 else 0.55)                          # the snow cap on top of the tier
            if dy < 3:
                for x in range(int(round(cx - snow_w)), int(round(cx + snow_w * (0.6 if dy == 2 else 1))) + 1):
                    cv.put(x, y, SW if x < cx else S1)
    cv.put(17, shapes["top"] - 1, SW); cv.put(18, shapes["top"] - 1, S1)      # snow on the tip
    cv.outline(GO)                                                            # (23.11) shadow: ground() casts it
    return cv


# --- thin walls: snowdrifts -----------------------------------------------------------------------------
TOP = [4, 3, 3, 2, 2, 3, 3, 4, 4, 3, 2, 2, 2, 3, 4, 4]       # the drift's top line per column (repeats every 16)

def drift_h():
    cv = Canvas(16, 12)
    for x in range(16):
        t = TOP[x]
        for y in range(t, 10):
            cv.put(x, y, SW if y < t + 2 else (S1 if y < 7 else (S2 if y < 9 else S3)))
    for x in range(16): cv.put(x, TOP[x] - 1, SO); cv.put(x, 10, SO); cv.put(x, 11, SH)
    return cv

def drift_h_end():
    """The left end: the drift slopes down to the ground."""
    cv = Canvas(8, 12)
    for x in range(8):
        t = max(TOP[0], 9 - x * 2) if x < 4 else TOP[0] if x > 5 else 5
        t = [9, 7, 6, 5, 5, 4, 4, 4][x]
        for y in range(t, 10):
            cv.put(x, y, SW if y < t + 2 else (S1 if y < 7 else (S2 if y < 9 else S3)))
        cv.put(x, t - 1, SO); cv.put(x, 10, SO); cv.put(x, 11, SH)
    cv.put(0, 9, SO)
    return cv

SIDE = [4, 4, 3, 3, 4, 5, 5, 4, 3, 3, 3, 4, 5, 4, 4, 4]       # the drift's left edge per row (repeats every 16)

def drift_v():
    cv = Canvas(12, 16)
    for y in range(16):
        x0, x1 = SIDE[y], 7 + (SIDE[(y + 5) % 16] - 3)
        for x in range(x0, x1 + 1): cv.put(x, y, SW if x < x0 + 2 else (S1 if x < x1 - 1 else S2))
        cv.put(x0 - 1, y, SO); cv.put(x1 + 1, y, SO); cv.put(x1 + 2, y, SH)
    return cv

def drift_v_cap(top_piece):
    cv = Canvas(12, 6)
    widths = [(5, 6), (4, 7), (4, 8), (4, 8), (4, 8), (4, 8)] if top_piece else [(4, 8), (4, 8), (4, 8), (4, 8), (5, 7), (6, 6)]
    for y, (x0, x1) in enumerate(widths):
        for x in range(x0, x1 + 1):
            front = not top_piece and y >= 3
            cv.put(x, y, (S2 if front else (SW if x < x0 + 2 else S1)))
        cv.put(x0 - 1, y, SO); cv.put(x1 + 1, y, SO); cv.put(x1 + 2, y, SH)
    if top_piece: cv.fill(5, 0, 6, 0, SO); cv.put(4, 0, T); cv.put(7, 0, T); cv.put(4, 1, SO); cv.put(7, 1, SO) if False else None
    else: cv.fill(5, 5, 7, 5, SO)
    return cv

# --- thick walls: packed snow blocks -----------------------------------------------------------------------
def blocks(cv, x0, y0, x1, y1, bw, bh, base, seam, shift=0):
    for y in range(y0, y1 + 1):
        row = (y - y0) // bh
        for x in range(x0, x1 + 1):
            off = (bw // 2) * (row % 2) + shift
            seam_here = (y - y0) % bh == bh - 1 or (x - x0 + off) % bw == bw - 1
            cv.put(x, y, seam if seam_here else base(x, y))

# (23.11) The thick horizontal wall drawn like Filip's thick_v: a big top seen from above (blocks, lit from the
# top-left), cut off from a LOW front face by a dark line - like the top of the ice blocks.
#   row 0 outline, 1-12 top, 13 outline (the edge), 14-19 front (as in thick_v_end), 20 outline, 21 shadow
SE, SG = rgb('#f4faff'), rgb('#86a6c6')                    # Filip's light edge and dark seam of the snow blocks
THICK_H_TOP = "bbbcccdcccde"                               # the top's rows: b white, c snow, d seam row, e light edge
THICK_H_FRONT = "cCgDDg"                                   # the front's rows (C = c with dark seams, D = d with dark seams)

def wall_h(variant=0):
    cv = Canvas(16, 22)
    shade = {"b": SW, "c": S1, "d": S2, "e": SE, "g": SG}
    seams = (7, 3) if variant == 0 else (3, 7)            # where the vertical seams are in the two rows of blocks
    cv.fill(0, 0, 15, 0, SO)
    for i, kind in enumerate(THICK_H_TOP):
        y, seam = 1 + i, seams[0] if i < 6 else seams[1]
        for x in range(16):
            cv.put(x, y, S2 if kind != "d" and x % 8 == seam else shade[kind])
    cv.fill(0, 13, 15, 13, SO)
    for i, kind in enumerate(THICK_H_FRONT):
        y, seam = 14 + i, seams[1] if i < 2 else seams[0]
        for x in range(16):
            at_seam = x % 8 == seam
            colour = {"c": S2 if at_seam else S1, "C": SG if at_seam else S1, "g": SG,
                      "D": SG if at_seam else S2}[kind]
            cv.put(x, y, colour)
    cv.fill(0, 20, 15, 20, SO); cv.fill(0, 21, 15, 21, SH)
    return cv

def wall_h_end():
    """The left end (the right one is mirrored): an outline column and a lit edge of the top."""
    mid = wall_h()
    cv = Canvas(6, 22)
    for y in range(22):
        for x in range(6): cv.put(x, y, mid.get(x, y))
    for y in range(1, 20): cv.put(0, y, SO)
    for y in range(1, 13): cv.put(1, y, SW)                  # the top's lit left edge
    for y in range(14, 20): cv.put(1, y, S2)                 # the front's left edge in shade
    cv.put(0, 0, T); cv.put(0, 20, T); cv.put(0, 21, T); cv.put(1, 1, SO)
    return cv

def wall_v(variant=0):
    cv = Canvas(22, 16)
    blocks(cv, 2, 0, 19, 15, 6, 8, lambda x, y: SW if x < 6 else (S1 if x < 16 else S2), S2, variant * 2)
    for y in range(16): cv.put(1, y, SO); cv.put(20, y, SO); cv.put(21, y, SH)
    return cv

def wall_v_top():
    cv = Canvas(22, 6)
    cv.fill(2, 0, 19, 0, SO)
    blocks(cv, 2, 1, 19, 5, 6, 8, lambda x, y: SW if x < 6 else (S1 if x < 16 else S2), S2)
    for y in range(1, 6): cv.put(1, y, SO); cv.put(20, y, SO); cv.put(21, y, SH)
    return cv

def wall_v_end():
    cv = Canvas(22, 12)
    blocks(cv, 2, 0, 19, 2, 6, 8, lambda x, y: SW if x < 6 else (S1 if x < 16 else S2), S2)
    cv.fill(1, 3, 20, 3, SO)
    blocks(cv, 2, 4, 19, 9, 6, 3, lambda x, y: S1 if y < 7 else S2, S3)
    for y in range(0, 10): cv.put(1, y, SO); cv.put(20, y, SO); cv.put(21, y, SH)
    cv.fill(1, 10, 20, 10, SO); cv.fill(2, 11, 21, 11, SH)
    return cv

# --- ground shadow for the pillars ------------------------------------------------------------------------
# GROUND (23.11): makes a pillar sit on the snow - a shadow the object casts on the ground (each pixel's shadow
# lands down-right, the further the higher the pixel is: a tree lays a long cone), a darker contact shadow right
# under its base, and a few snow crumbs at its foot. Only empty pixels are filled - the drawing stays as it is.
# The picture gets PAD empty columns on both sides and just enough rows below the base first, so the shadow fits (the game centres it anyway).

SHADOW = (20, 40, 70)
CAST_ALPHA, CONTACT_ALPHA = 50, 85    # (23.11) a bit lighter
LEAN_X, LEAN_Y = 0.38, 0.16        # a pixel h px above the ground: its shadow lands h*LEAN_X right, h*LEAN_Y down
CRUMB_LIGHT, CRUMB_SHADE = (225, 237, 248), (180, 204, 226)

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

SPRITES = {
    "silverpine_tundra_wall_h": drift_h, "silverpine_tundra_wall_h_end": drift_h_end,
    "silverpine_tundra_wall_v": drift_v, "silverpine_tundra_wall_v_top": lambda: drift_v_cap(True),
    "silverpine_tundra_wall_v_end": lambda: drift_v_cap(False),
    "silverpine_tundra_wall_thick_h": lambda: wall_h(0), "silverpine_tundra_wall_thick_h_2": lambda: wall_h(1),
    "silverpine_tundra_wall_thick_h_end": wall_h_end,
    "silverpine_tundra_wall_thick_v": lambda: wall_v(0), "silverpine_tundra_wall_thick_v_2": lambda: wall_v(1),
    "silverpine_tundra_wall_thick_v_top": wall_v_top, "silverpine_tundra_wall_thick_v_end": wall_v_end,
}
for i, suffix in enumerate(["", "_2", "_3"]):
    SPRITES[f"silverpine_tundra_pillar_small{suffix}"] = (lambda k: lambda: snowman(k))(i)
    SPRITES[f"silverpine_tundra_pillar_medium{suffix}"] = (lambda k: lambda: ice_block(k))(i)
    SPRITES[f"silverpine_tundra_pillar_large{suffix}"] = (lambda k: lambda: spruce(k))(i)
if __name__ == "__main__":
    for name, make in SPRITES.items():
        im = make().image()
        if "pillar" in name: im = ground(im)                                  # (23.11) sit on the snow
        im.save(f"{sys.argv[1]}/{name}.png"); print(name, im.size)
