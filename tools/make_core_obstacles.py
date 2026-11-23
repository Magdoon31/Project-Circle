# The Core obstacles (pixel art 1:4, 23.11): a mechanical heart - organic and mechanical at once.
# Pillars (2 kinds each): pipe-veins (small), heart chambers in metal (medium), columns of cables like muscles
# (large). Thin walls: bundles of cables on the floor. Thick walls: dark metal panels with vent grilles and red lamps
# (laid out like Filip's tundra thick walls: a big top, a dark edge line, a low front).
# Red glowing accents (veins, lamps, sparks) with a faint half-transparent glow round them. The floor is dark grey
# metal: the shadow is near-black, half-transparent; outline = a very dark shade of the object's own colour.
# Run: py tools/make_core_obstacles.py <folder> - into another folder, then copy over what you need (Filip touches
# the files up by hand: his files in assets/ are the real ones).
import math, sys
import numpy as np
from PIL import Image

T, SH = (0, 0, 0, 0), (8, 4, 6, 100)               # shadow: near-black, half-transparent
def rgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) + (255,)
M_LIGHT, M_MID, M_DARK, M_DEEP, M_OUT = rgb('#8a8f9c'), rgb('#5e6270'), rgb('#3e414c'), rgb('#2a2c34'), rgb('#0c0d12')
RIVET, HOLE = rgb('#b4b8c4'), rgb('#120a0c')
FLESH_LIGHT, FLESH, FLESH_DARK = rgb('#d0566a'), rgb('#a8344a'), rgb('#6e1c2e')
VEIN, VEIN_CORE = rgb('#ff3a50'), rgb('#ffb0b8')                            # glowing red
LAMP, LAMP_DARK = rgb('#ff4058'), rgb('#a01c2c')
CABLE_LIGHT, CABLE, CABLE_RED, CABLE_RED_DARK, CABLE_OUT = rgb('#55515c'), rgb('#2e2c34'), rgb('#b0283c'), rgb('#701828'), rgb('#0a090c')
P_LIGHT, P_MID, P_DARK, P_SEAM, VENT = rgb('#6a6e7a'), rgb('#50535e'), rgb('#3a3c45'), rgb('#2c2e36'), rgb('#16171c')
P_FRONT, P_FRONT_DARK, P_OUT = rgb('#454852'), rgb('#363840'), rgb('#0b0c10')

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
# under its base, and a few crumbs (here: metal bits) at its foot. Only empty pixels are filled - the drawing stays as it is.
# The picture gets PAD empty columns on both sides and just enough rows below the base first, so the shadow fits (the game centres it anyway).

SHADOW = (8, 4, 6)
CAST_ALPHA, CONTACT_ALPHA = 75, 115
LEAN_X, LEAN_Y = 0.38, 0.16        # a pixel h px above the ground: its shadow lands h*LEAN_X right, h*LEAN_Y down
CRUMB_LIGHT, CRUMB_SHADE = (94, 98, 112), (62, 65, 76)       # metal bits

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
    """A faint glow round glowing pixels: half-transparent, only on empty pixels (not solid for collision)."""
    halo = (colour[0], colour[1], colour[2], alpha)
    for x, y in cells:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if cv.get(x + dx, y + dy)[3] == 0: cv.put(x + dx, y + dy, halo)

def blob(cv, cx, cy, rx, ry, colour):
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1: cv.put(x, y, colour)

def shade3(k, half, light, mid, dark):
    """Lit from the left: light / mid / dark across a round thing (k = offset from its middle)."""
    return light if k < -half * 0.35 else (mid if k < half * 0.4 else dark)

def cylinder(cv, cx, top, bottom, half, light, mid, dark):
    for y in range(top, bottom + 1):
        for x in range(int(cx - half), int(cx + half) + 1): cv.put(x, y, shade3(x - cx, half, light, mid, dark))

def collar(cv, cx, y, half, rows=2):
    """A metal ring round a pipe / column, with a rivet."""
    for yy in range(y, y + rows):
        for x in range(int(cx - half - 1), int(cx + half + 1) + 1):
            cv.put(x, yy, shade3(x - cx, half + 1, M_LIGHT, M_MID, M_DARK))
    cv.put(int(cx - half + 1), y, RIVET)

def vein(cv, cells, lit):
    """A glowing red vein along these pixels (every other one brighter)."""
    for i, (x, y) in enumerate(cells):
        cv.put(x, y, VEIN if i % 3 else VEIN_CORE); lit.append((x, y))

# --- small pillars: pipe-veins ----------------------------------------------------------------------------------
def pipe_vein(kind):
    cv = Canvas(20, 20)
    lit = []
    if kind == 0:                                                           # a pipe stub out of the floor
        cylinder(cv, 9.5, 5, 16, 3.5, M_LIGHT, M_MID, M_DARK)
        blob(cv, 9.5, 5, 3.5, 1.4, M_DEEP); blob(cv, 9.5, 5.3, 2.2, 0.8, HOLE)    # its open top
        collar(cv, 9.5, 8, 3.5); collar(cv, 9.5, 15, 3.5)
        vein(cv, [(7, 10), (8, 11), (9, 11), (10, 12), (11, 12), (12, 13), (11, 14), (8, 13), (7, 14)], lit)
    else:                                                                   # a pipe bend: out of the floor and back in
        for t in range(0, 33):
            a = math.pi * t / 32
            x, y = 9.5 - 5 * math.cos(a), 14 - 9 * math.sin(a)
            blob(cv, x, y, 2.2, 2.2, M_MID)
        for t in range(0, 33):
            a = math.pi * t / 32
            x, y = 9.5 - 5 * math.cos(a), 14 - 9 * math.sin(a)
            cv.put(int(round(x - 1)), int(round(y - 1)), M_LIGHT)
        collar(cv, 4.5, 15, 2); collar(cv, 14.5, 15, 2)
        vein(cv, [(int(round(9.5 - 5 * math.cos(math.pi * t / 10))), int(round(14 - 9 * math.sin(math.pi * t / 10))) + 1)
                  for t in range(1, 10)], lit)
    cv.outline(M_OUT)
    glow(cv, lit, VEIN, 60)
    return cv

# --- medium pillars: heart chambers in metal ------------------------------------------------------------------------
def heart_chamber(kind):
    cv = Canvas(28, 28)
    lit = []
    if kind == 0:                                                           # a beating chamber in a metal cage
        blob(cv, 13.5, 13, 8, 8.5, FLESH_DARK); blob(cv, 12.5, 12, 6.8, 7.2, FLESH); blob(cv, 10.5, 9.5, 2.6, 2.2, FLESH_LIGHT)
        for x in (5, 22):                                                   # the cage's posts
            cylinder(cv, x, 3, 23, 1.2, M_LIGHT, M_MID, M_DARK)
        for y in (3, 13, 22):                                               # and bands
            for x in range(5, 23): cv.put(x, y, M_MID if y != 22 else M_DARK)
            cv.put(5, y, RIVET); cv.put(22, y, RIVET)
        vein(cv, [(9, 15), (10, 16), (11, 17), (12, 17), (13, 18), (15, 8), (16, 9), (16, 10), (17, 11), (18, 11)], lit)
        cylinder(cv, 13.5, 23, 24, 10, M_LIGHT, M_MID, M_DARK)              # the base plate
    else:                                                                   # a round tank with a window onto the heart
        cylinder(cv, 13.5, 6, 23, 8.5, M_LIGHT, M_MID, M_DARK)
        blob(cv, 13.5, 6, 8.5, 2.6, M_LIGHT); blob(cv, 13.5, 6, 6, 1.6, M_MID)       # the lid
        blob(cv, 13.5, 14, 5, 5, M_DEEP); blob(cv, 13.5, 14, 4, 4, FLESH); blob(cv, 12.5, 12.5, 1.6, 1.4, FLESH_LIGHT)
        vein(cv, [(12, 16), (13, 16), (14, 15), (15, 15), (15, 13)], lit)
        collar(cv, 13.5, 21, 8.5)
        for x in (8, 19): cv.put(x, 9, LAMP); lit.append((x, 9))
        cv.put(13, 3, M_MID); cv.put(13, 2, M_MID); cv.put(13, 1, LAMP); lit.append((13, 1))   # a little antenna
    cv.outline(M_OUT)
    glow(cv, lit, VEIN, 60)
    return cv

# --- large pillars: columns of cables like muscles ------------------------------------------------------------------
def muscle_column(kind):
    cv = Canvas(36, 36)
    lit = []
    if kind == 0:                                                           # twisted cables
        for strand in range(4):
            for y in range(5, 31):
                x = 17.5 + math.sin(y / 3.2 + strand * math.pi / 2) * 3.4
                front = math.cos(y / 3.2 + strand * math.pi / 2) > 0
                c = (CABLE_RED, CABLE_RED_DARK) if strand % 2 else (CABLE_LIGHT, CABLE)
                for dx in (-1, 0, 1):
                    if front or cv.get(int(round(x)) + dx, y)[3] == 0:
                        cv.put(int(round(x)) + dx, y, c[0] if dx < 1 else c[1])
        for y in range(30, 33):                                             # spreading at the foot
            for dx in range(-7 - (y - 30) * 2, 8 + (y - 30) * 2):
                if abs(dx) > 4 and (dx + y) % 3 == 0: cv.put(17 + dx, y, CABLE)
        collar(cv, 17.5, 3, 6, 3); collar(cv, 17.5, 17, 5.5)
        blob(cv, 17.5, 3, 6, 1.6, M_LIGHT)
        for y in range(7, 30, 4): cv.put(17 + (y % 3) - 1, y, VEIN_CORE); lit.append((17 + (y % 3) - 1, y))
        cv.put(17, 1, LAMP); cv.put(18, 1, LAMP); lit += [(17, 1), (18, 1)]
    else:                                                                   # muscle bundles held by metal bands
        for y in range(4, 31):
            half = 5.5 + 1.3 * math.sin(y / 2.6) ** 2
            for x in range(int(17.5 - half), int(17.5 + half) + 1):
                k = x - 17.5
                fibre = (int(x - 17.5 + y * 0.35) % 3 == 0)                    # slanted fibres
                c = shade3(k, half, FLESH_LIGHT, FLESH, FLESH_DARK)
                cv.put(x, y, FLESH_DARK if fibre and c != FLESH_DARK else c)
        for by in (4, 13, 22, 29): collar(cv, 17.5, by, 6.5, 2)
        blob(cv, 17.5, 4, 7, 1.8, M_LIGHT); blob(cv, 17.5, 3.6, 4, 1, M_MID)
        vein(cv, [(15, 8), (16, 9), (16, 10), (19, 17), (20, 18), (20, 19), (14, 25), (15, 26)], lit)
        cv.put(17, 2, LAMP); lit.append((17, 2))
    cv.outline(M_OUT)
    glow(cv, lit, VEIN, 60)
    return cv

# --- thin walls: cable bundles ----------------------------------------------------------------------------------------
CABLES = [(3, 0.6, 0.0, (CABLE_LIGHT, CABLE)), (5, 0.6, 2.0, (CABLE_RED, CABLE_RED_DARK)), (7, 0.6, 4.0, (CABLE_LIGHT, CABLE))]   # (base, wave, phase)

def cables_h():
    cv = Canvas(16, 12)
    for base, amp, phase, (light, dark) in CABLES:                          # 3 cables lying side by side
        for x in range(16):
            y = int(round(base + amp * math.sin(x / 16 * 2 * math.pi + phase)))
            cv.put(x, y, light); cv.put(x, y + 1, dark)
    spark = (4, int(round(5 + 0.6 * math.sin(4 / 16 * 2 * math.pi + 2.0))))
    cv.put(*spark, VEIN_CORE)                                               # a spark on the red cable
    cv.outline(CABLE_OUT); cv.shadow()
    glow(cv, [spark], VEIN, 60)
    return cv

def cables_h_end():
    """The left end: the cables go into a socket on the floor."""
    mid = cables_h()
    cv = Canvas(8, 12)
    for x in range(2, 8):
        for y in range(12):
            c = mid.get(x + 2, y)
            if c[3] == 255 and c not in (CABLE_OUT, M_MID, M_DARK, RIVET): cv.put(x, y, c)
    for y in range(1, 11):                                                  # the socket
        for x in range(0, 3): cv.put(x, y, M_LIGHT if x == 0 else (M_MID if x == 1 else M_DARK))
    cv.put(1, 2, LAMP); cv.put(1, 9, RIVET)
    cv.outline(CABLE_OUT); cv.shadow()
    glow(cv, [(1, 2)], VEIN, 60)
    return cv

def cables_v():
    cv = Canvas(12, 16)
    for base, amp, phase, (light, dark) in CABLES:
        for y in range(16):
            x = int(round(base + amp * math.sin(y / 16 * 2 * math.pi + phase)))
            cv.put(x, y, light); cv.put(x + 1, y, dark)
    spark = (int(round(5 + 0.6 * math.sin(4 / 16 * 2 * math.pi + 2.0))), 4)
    cv.put(*spark, VEIN_CORE)
    cv.outline(CABLE_OUT); cv.shadow()
    glow(cv, [spark], VEIN, 60)
    return cv

def cables_v_cap(top_piece):
    mid = cables_v()
    cv = Canvas(12, 6)
    for y in range(6):
        for x in range(12):
            c = mid.get(x, (y + 2) if top_piece else y)
            if c[3] == 255 and c not in (CABLE_OUT, M_MID, M_DARK, RIVET) and (y >= 3 if top_piece else y <= 2): cv.put(x, y, c)
    sy = 0 if top_piece else 3                                              # the socket the cables go into
    for y in range(sy, sy + 3):
        for x in range(1, 11): cv.put(x, y, M_LIGHT if y == sy else (M_MID if y == sy + 1 else M_DARK))
    cv.put(9, sy + 1, LAMP)
    cv.outline(CABLE_OUT); cv.shadow()
    glow(cv, [(9, sy + 1)], VEIN, 60)
    return cv

# --- thick walls: metal panels with vents (laid out like Filip's tundra thick walls) --------------------------------
def panel_top(x, y, i, variant):
    """The top face, seen from above: plates with seams, rivets in the corners, a vent grille."""
    px, py = (x + variant * 4) % 16, i
    if px in (0, 15) or py in (0, 11): return P_SEAM
    if (px, py) in ((1, 1), (14, 1), (1, 10), (14, 10)): return RIVET
    if 4 <= px <= 11 and 3 <= py <= 8: return VENT if py % 2 == 0 else P_DARK        # the grille
    return P_LIGHT if py < 3 else P_MID

def wall_thick_h(variant=0):
    cv = Canvas(16, 22)
    cv.fill(0, 0, 15, 0, P_OUT)
    for i in range(12):
        for x in range(16): cv.put(x, 1 + i, panel_top(x, 1 + i, i, variant))
    cv.fill(0, 13, 15, 13, P_OUT)
    for i in range(6):                                                      # the low front: a vent strip and a lamp
        y = 14 + i
        for x in range(16):
            c = P_FRONT if i in (0, 5) else (VENT if i in (2, 4) and 2 <= (x + variant * 6) % 16 <= 9 else P_FRONT_DARK)
            cv.put(x, y, c)
    lamp_x = (12 + variant * 6) % 16
    cv.put(lamp_x, 16, LAMP); cv.put(lamp_x, 17, LAMP_DARK)
    cv.fill(0, 20, 15, 20, P_OUT); cv.fill(0, 21, 15, 21, SH)
    glow(cv, [(lamp_x, 16)], VEIN, 50)
    return cv

def wall_thick_h_end():
    mid = wall_thick_h()
    cv = Canvas(6, 22)
    for y in range(22):
        for x in range(6): cv.put(x, y, mid.get(x, y))
    for y in range(1, 20): cv.put(0, y, P_OUT)
    for y in range(1, 13): cv.put(1, y, P_LIGHT)
    for y in range(14, 20): cv.put(1, y, P_FRONT)
    cv.put(0, 0, T); cv.put(0, 20, T); cv.put(0, 21, T); cv.put(1, 1, P_OUT)
    return cv

def thick_v_face(cv, y0, y1, variant=0):
    for y in range(y0, y1 + 1):
        for x in range(2, 20):
            i, along = x - 2, y                                             # across 0..17, along the wall
            py = (along + variant * 5) % 16
            if i in (0, 17) or py == 15: c = P_SEAM
            elif (i, py) in ((1, 1), (16, 1), (1, 13), (16, 13)): c = RIVET
            elif 5 <= i <= 12 and 4 <= py <= 10: c = VENT if i % 2 == 0 else P_DARK
            else: c = P_LIGHT if i < 3 else P_MID
            cv.put(x, y, c)

def wall_thick_v(variant=0):
    cv = Canvas(22, 16)
    thick_v_face(cv, 0, 15, variant)
    for y in range(16): cv.put(1, y, P_OUT); cv.put(20, y, P_OUT); cv.put(21, y, SH)
    return cv

def wall_thick_v_top():
    cv = Canvas(22, 6)
    thick_v_face(cv, 1, 5)
    cv.fill(2, 0, 19, 0, P_OUT)
    for y in range(1, 6): cv.put(1, y, P_OUT); cv.put(20, y, P_OUT); cv.put(21, y, SH)
    return cv

def wall_thick_v_end():
    cv = Canvas(22, 12)
    thick_v_face(cv, 0, 2)
    cv.fill(1, 3, 20, 3, P_OUT)
    for i in range(6):
        y = 4 + i
        for x in range(2, 20):
            c = P_FRONT if i in (0, 5) else (VENT if i in (2, 4) and 5 <= x <= 14 else P_FRONT_DARK)
            cv.put(x, y, c)
    cv.put(17, 6, LAMP); cv.put(17, 7, LAMP_DARK)
    for y in range(0, 10): cv.put(1, y, P_OUT); cv.put(20, y, P_OUT); cv.put(21, y, SH)
    cv.fill(1, 10, 20, 10, P_OUT); cv.fill(2, 11, 21, 11, SH)
    glow(cv, [(17, 6)], VEIN, 50)
    return cv

SPRITES = {
    "the_core_wall_h": cables_h, "the_core_wall_h_end": cables_h_end,
    "the_core_wall_v": cables_v, "the_core_wall_v_top": lambda: cables_v_cap(True),
    "the_core_wall_v_end": lambda: cables_v_cap(False),
    "the_core_wall_thick_h": lambda: wall_thick_h(0), "the_core_wall_thick_h_2": lambda: wall_thick_h(1),
    "the_core_wall_thick_h_end": wall_thick_h_end,
    "the_core_wall_thick_v": lambda: wall_thick_v(0), "the_core_wall_thick_v_2": lambda: wall_thick_v(1),
    "the_core_wall_thick_v_top": wall_thick_v_top, "the_core_wall_thick_v_end": wall_thick_v_end,
}
for i, suffix in enumerate(["", "_2"]):
    SPRITES[f"the_core_pillar_small{suffix}"] = (lambda k: lambda: pipe_vein(k))(i)
    SPRITES[f"the_core_pillar_medium{suffix}"] = (lambda k: lambda: heart_chamber(k))(i)
    SPRITES[f"the_core_pillar_large{suffix}"] = (lambda k: lambda: muscle_column(k))(i)

if __name__ == "__main__":
    for name, make in SPRITES.items():
        im = make().image()
        if "pillar" in name: im = ground(im)
        im.save(f"{sys.argv[1]}/{name}.png"); print(name, im.size)
