# Sugarwood Grove obstacles (pixel art 1:4): candy-cane fence (thin walls), gingerbread (thick walls), lollipops
# (small / large pillars). Outline = a very dark shade of the object's own colour (Filip, 23.11).
import math, sys
from PIL import Image

T = (0, 0, 0, 0)
SHADOW = (0, 0, 0, 70)
# candy cane
CW, CWs, CR, CRs, CO = (255, 250, 246, 255), (238, 214, 220, 255), (226, 48, 60, 255), (170, 28, 42, 255), (46, 8, 14, 255)
# gingerbread
GL, GM, GD, GO = (214, 146, 80, 255), (184, 115, 58, 255), (138, 82, 40, 255), (40, 18, 6, 255)
IC, ICs = (255, 250, 242, 255), (226, 214, 204, 255)                  # icing
GUM = [(232, 52, 64, 255), (92, 200, 96, 255), (90, 160, 240, 255), (255, 214, 40, 255)]

class Canvas:
    def __init__(s, w, h): s.w, s.h, s.px = w, h, [[T] * w for _ in range(h)]
    def put(s, x, y, c):
        if 0 <= x < s.w and 0 <= y < s.h: s.px[y][x] = c
    def get(s, x, y): return s.px[y][x] if 0 <= x < s.w and 0 <= y < s.h else T
    def fill(s, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): s.put(x, y, c)
    def image(s):
        im = Image.new('RGBA', (s.w, s.h))
        for y in range(s.h):
            for x in range(s.w): im.putpixel((x, y), s.px[y][x])
        return im

def stripe(x, y, shade=False):
    """Candy-cane colour of an inside pixel: diagonal red/white bands, the right side darker."""
    red = (x + y) % 4 in (0, 1)
    return (CRs if shade else CR) if red else (CWs if shade else CW)

# --- candy-cane fence (the Rainbow Fields fence shape, canes with hooks) ---------------------------------------
def cane_picket(cv, x, top=0, bottom=10):
    """A candy cane: stem x+1..x+2 inside (outline x, x+3), a round hook over to x+4 going 2 rows down.
    Stripes run along the cane: 2 px red, 2 px white, slanted on the stem."""
    for y in range(top + 2, bottom):
        cv.put(x, y, CO); cv.put(x + 3, y, CO)
        for c in (0, 1):
            red = ((y + c) // 2) % 2 == 0
            cv.put(x + 1 + c, y, (CRs if c else CR) if red else (CWs if c else CW))
    cv.fill(x + 1, top, x + 4, top, CO)                                   # the hook: outline round it
    cv.put(x, top + 1, CO); cv.put(x + 5, top + 1, CO); cv.put(x + 5, top + 2, CO); cv.put(x + 5, top + 3, CO)
    cv.put(x + 3, top + 2, CO); cv.put(x + 3, top + 3, CO); cv.put(x + 4, top + 4, CO)
    hook = [(x + 1, top + 1, CW), (x + 2, top + 1, CR), (x + 3, top + 1, CR), (x + 4, top + 1, CW),
            (x + 4, top + 2, CWs), (x + 4, top + 3, CRs)]
    for hx, hy, c in hook: cv.put(hx, hy, c)
    cv.fill(x, bottom, x + 3, bottom, CO)

def cane_rail(cv, x0, x1, y):
    """A rail: outline, a striped line, outline."""
    for x in range(x0, x1 + 1):
        if cv.get(x, y + 1) in (T,) or True:
            if cv.get(x, y) == T: cv.put(x, y, CO)
            if cv.get(x, y + 2) == T: cv.put(x, y + 2, CO)
            if cv.get(x, y + 1) == T: cv.put(x, y + 1, CWs)                # (plain cream, so the canes stand out)

RAILS = (4, 8)                                     # each rail: outline, colour, outline (rows y..y+2)

def fence_h():
    cv = Canvas(16, 12)
    for x in (1, 9): cane_picket(cv, x)
    for y in RAILS: cane_rail(cv, 0, 15, y)
    for x in (2, 10): cv.fill(x, 11, x + 3, 11, SHADOW)
    return cv

def fence_h_end():
    cv = Canvas(8, 12)
    cv.fill(0, 0, 5, 0, CO); cv.fill(0, 10, 5, 10, CO)
    for y in range(1, 10):
        cv.put(0, y, CO); cv.put(5, y, CO)
        for x in range(1, 5): cv.put(x, y, stripe(x, y, x == 4))
    for x in range(1, 5): cv.put(x, 1, CW if x < 4 else CWs)               # the post's top, seen from above
    cv.fill(0, 2, 5, 2, CO)
    for y in RAILS: cane_rail(cv, 6, 7, y)
    cv.fill(1, 11, 6, 11, SHADOW)
    return cv

def fence_v():
    cv = Canvas(12, 16)
    for y in range(16):
        cv.put(4, y, CO); cv.put(7, y, CO); cv.put(8, y, SHADOW)
        cv.put(5, y, stripe(5, y)); cv.put(6, y, stripe(6, y, True))
    return cv

def fence_post(top_piece):
    cv = Canvas(12, 6)
    rows = range(0, 5) if top_piece else range(1, 6)
    r0 = rows[0]
    cv.fill(3, r0, 8, r0, CO); cv.fill(3, r0 + 4, 8, r0 + 4, CO)
    for y in range(r0 + 1, r0 + 4):
        cv.put(3, y, CO); cv.put(8, y, CO); cv.put(9, y, SHADOW)
        for x in range(4, 8): cv.put(x, y, stripe(x, y, x == 7))
    for x in range(4, 8): cv.put(x, r0 + 1, CW if x < 7 else CWs)
    if top_piece:                                                        # the band goes on below the top post
        cv.put(4, 5, CO); cv.put(7, 5, CO); cv.put(8, 5, SHADOW); cv.put(5, 5, stripe(5, 5)); cv.put(6, 5, stripe(6, 5, True))
    else:                                                                # ... and comes from above into the bottom one
        cv.put(4, 0, CO); cv.put(7, 0, CO); cv.put(8, 0, SHADOW); cv.put(5, 0, stripe(5, 0)); cv.put(6, 0, stripe(6, 0, True))
    cv.put(9, r0 + 4, SHADOW)
    return cv

# --- gingerbread wall ------------------------------------------------------------------------------------
DRIPS = [2, 0, 1, 3, 1, 0, 2, 4, 1, 0, 1, 2, 0, 3, 1, 0]     # icing drip length per column (repeats every 16)

def ginger_front(cv, x, y, light, shift=0):
    """A front-face pixel: plain gingerbread, a few baked holes (shift moves the holes in a variant)."""
    hole = ((x + shift) * 7 + y * 3) % 23 == 0
    cv.put(x, y, GD if hole else (GM if not light else GL))

def ginger_h(variant=0):
    cv = Canvas(16, 22)
    cv.fill(0, 0, 15, 0, GO)
    cv.fill(0, 1, 15, 5, GL)                                             # top face
    for x in range(16): cv.put(x, 1, (236, 170, 104, 255) if x % 5 else GL)     # lit edge
    for x in range(16):                                                  # icing along the front edge + drips
        cv.put(x, 6, IC); cv.put(x, 7, IC if x % 3 else ICs)
        for d in range(DRIPS[(x + variant * 5) % 16]):
            cv.put(x, 8 + d, IC if d == 0 else ICs)
    for y in range(8, 20):
        for x in range(16):
            if cv.get(x, y) == T: ginger_front(cv, x, y, False, variant * 3)
    for y in range(8, 20):                                               # re-put the drips over the face
        for x in range(16):
            if 8 <= y < 8 + DRIPS[(x + variant * 5) % 16]: cv.put(x, y, IC if y == 8 else ICs)
    for x in range(16): cv.put(x, 19, GD)
    cv.fill(0, 20, 15, 20, GO)
    cv.fill(0, 21, 15, 21, SHADOW)
    candies = [(4, 3, 0), (11, 4, 1)] if variant == 0 else [(7, 3, 2), (13, 2, 3)]
    for cx, cy, k in candies:                                            # gumdrops on the top
        cv.put(cx, cy, GUM[k]); cv.put(cx + 1, cy, GUM[k]); cv.put(cx, cy - 1, (255, 255, 255, 255))
    return cv

def ginger_h_end():
    mid = ginger_h()
    cv = Canvas(6, 22)
    for y in range(22):
        for x in range(6): cv.put(x, y, mid.get(x + 3, y))
    for y in range(1, 20): cv.put(0, y, GO)
    for y in range(8, 19): cv.put(1, y, GD)                              # the corner in shade
    cv.put(0, 0, T); cv.put(1, 0, GO); cv.put(1, 1, GO); cv.put(0, 20, T); cv.put(0, 21, T)
    cv.put(1, 6, IC); cv.put(1, 7, IC); cv.put(1, 8, IC); cv.put(1, 9, ICs); cv.put(1, 10, ICs)   # icing over the corner
    return cv

def ginger_v(variant=0):
    cv = Canvas(22, 16)
    for y in range(16):
        cv.put(1, y, GO); cv.put(20, y, GO); cv.put(21, y, SHADOW)
        for x in range(2, 20): cv.put(x, y, GL)
        for x in (2, 3, 18, 19): cv.put(x, y, IC if (y + x) % 3 else ICs)   # icing along both sides
        cv.put(4 if (y + variant) % 4 == 0 else 3, y, IC)
        cv.put(17 if (y + variant + 2) % 4 == 0 else 18, y, IC)
    for (cx, cy, k) in ([(8, 3, 0), (13, 9, 1), (9, 13, 3)] if variant == 0 else [(12, 2, 2), (7, 8, 3), (13, 13, 0)]):
        cv.put(cx, cy, GUM[k]); cv.put(cx + 1, cy, GUM[k]); cv.put(cx, cy - 1, (255, 255, 255, 255))
    for y in range(16):
        for x in range(5, 17):
            if (x * 5 + y * 7) % 29 == 0: cv.put(x, y, GM)              # baked texture
    return cv

def ginger_v_top():
    cv = Canvas(22, 6)
    cv.fill(2, 0, 19, 0, GO)
    for y in range(1, 6):
        cv.put(1, y, GO); cv.put(20, y, GO); cv.put(21, y, SHADOW)
        for x in range(2, 20): cv.put(x, y, GL)
    for x in range(2, 20): cv.put(x, 1, IC); cv.put(x, 2, IC if x % 3 else ICs)   # icing over the top end
    for y in range(3, 6):
        for x in (2, 3, 18, 19): cv.put(x, y, IC if (y + x) % 3 else ICs)
    cv.put(1, 0, T); cv.put(20, 0, T); cv.put(2, 1, GO); cv.put(19, 1, GO)
    return cv

def ginger_v_end():
    cv = Canvas(22, 12)
    for y in range(0, 3):                                                # the top face ends
        cv.put(1, y, GO); cv.put(20, y, GO); cv.put(21, y, SHADOW)
        for x in range(2, 20): cv.put(x, y, GL)
        for x in (2, 3, 18, 19): cv.put(x, y, IC)
    for x in range(1, 21): cv.put(x, 3, IC); cv.put(x, 4, IC if x % 3 else ICs)      # icing on the front edge
    for y in range(5, 10):
        cv.put(1, y, GO); cv.put(20, y, GO); cv.put(21, y, SHADOW)
        for x in range(2, 20):
            d = DRIPS[x % 16]
            cv.put(x, y, (IC if y == 5 else ICs) if y < 5 + d else (GD if (x * 7 + y * 3) % 23 == 0 else GM))
    for x in range(2, 20): cv.put(x, 9, GD)
    cv.fill(1, 10, 20, 10, GO); cv.put(1, 3, GO); cv.put(20, 3, GO); cv.put(1, 4, GO); cv.put(20, 4, GO)
    cv.fill(2, 11, 21, 11, SHADOW)
    return cv

# --- lollipops -----------------------------------------------------------------------------------------
def shade(c, k):
    return tuple(max(0, min(255, round(v * k))) for v in c[:3]) + (255,)

def lollipop(size, disc, colours, outline):
    """A lollipop stuck in the ground: a spiral disc of `disc` px across on a stick; size = the file (square)."""
    cv = Canvas(size, size)
    r = disc / 2 - 0.5
    cx, cy = (size - 1) / 2, disc / 2 + 0.5
    stick_top, stick_bottom = int(cy + r) - 1, size - 3
    sx = int(cx) - (1 if disc < 16 else 1)
    stick_w = 2 if disc < 16 else 3
    cv.fill(sx + 1, size - 2, sx + stick_w + 3, size - 1, SHADOW)          # its shadow on the ground
    for y in range(stick_top, stick_bottom + 1):                          # the stick
        cv.put(sx - 1, y, (60, 40, 28, 255)); cv.put(sx + stick_w, y, (60, 40, 28, 255))
        for i in range(stick_w): cv.put(sx + i, y, (246, 236, 214, 255) if i == 0 else (206, 190, 164, 255))
    cv.fill(sx - 1, stick_bottom + 1, sx + stick_w, stick_bottom + 1, (60, 40, 28, 255))
    arms = len(colours)
    for y in range(size):
        for x in range(size):
            d = math.hypot(x - cx, y - cy)
            if d > r + 1.0: continue
            if d > r: cv.put(x, y, outline); continue
            a = (math.atan2(y - cy, x - cx) / math.tau) % 1
            k = int((a * arms + d / (disc / 5.5)) % arms)
            col = colours[k]
            light = 1.12 if (x - cx) + (y - cy) < -r * 0.6 else (0.82 if (x - cx) + (y - cy) > r * 0.9 else 1.0)
            cv.put(x, y, shade(col, light))
    hx, hy = int(cx - r * 0.45), int(cy - r * 0.5)                        # the shine
    cv.put(hx, hy, (255, 255, 255, 255))
    if disc >= 16: cv.put(hx + 1, hy, (255, 255, 255, 255)); cv.put(hx, hy + 1, (255, 255, 255, 255))
    return cv

def pillar_small():
    return lollipop(20, 13, [(80, 205, 190, 255), (255, 250, 246, 255)], (8, 40, 38, 255))

def pillar_large():
    rainbow = [(232, 52, 64, 255), (255, 150, 40, 255), (255, 214, 40, 255), (92, 200, 96, 255), (90, 160, 240, 255), (160, 90, 220, 255)]
    return lollipop(36, 29, rainbow, (30, 12, 36, 255))

SPRITES = {
    "sugarwood_grove_wall_h": fence_h, "sugarwood_grove_wall_h_end": fence_h_end,
    "sugarwood_grove_wall_v": fence_v, "sugarwood_grove_wall_v_top": lambda: fence_post(True),
    "sugarwood_grove_wall_v_end": lambda: fence_post(False),
    "sugarwood_grove_wall_thick_h": lambda: ginger_h(0), "sugarwood_grove_wall_thick_h_2": lambda: ginger_h(1),
    "sugarwood_grove_wall_thick_h_end": ginger_h_end,
    "sugarwood_grove_wall_thick_v": lambda: ginger_v(0), "sugarwood_grove_wall_thick_v_2": lambda: ginger_v(1),
    "sugarwood_grove_wall_thick_v_top": ginger_v_top, "sugarwood_grove_wall_thick_v_end": ginger_v_end,
    "sugarwood_grove_pillar_small": pillar_small, "sugarwood_grove_pillar_large": pillar_large,
}
if __name__ == "__main__":
    out = sys.argv[1]
    for name, make in SPRITES.items():
        im = make().image(); im.save(f"{out}/{name}.png"); print(name, im.size)
