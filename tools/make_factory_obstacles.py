# Toy Factory obstacles (pixel art 1:4): copper pipes (thin walls), a stopped conveyor belt with boxes (thick walls),
# a barrel / a crate / a stack of crates (pillars). Outline = a very dark shade of the object's colour (23.11).
import sys
from PIL import Image

T, SH = (0, 0, 0, 0), (0, 0, 0, 70)
def rgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) + (255,)
# copper pipe
PL, PM, PD, PO, PB = rgb('#eaa56a'), rgb('#c8763c'), rgb('#8e4c22'), rgb('#2a1206'), rgb('#f6cfa0')
# wooden crate
WL, WM, WD, WO = rgb('#cf9a5c'), rgb('#a8763f'), rgb('#7c5326'), rgb('#2a1606')
ML, MD = rgb('#b7bec8'), rgb('#7d8592')                                 # metal corners
# blue barrel
BL, BM, BD, BO, BR = rgb('#5aa2e2'), rgb('#3c7cc0'), rgb('#2a5690'), rgb('#0a1a30'), rgb('#8fc4f0')
# belt + machine side
RB, RBd, RBl, RO = rgb('#47474f'), rgb('#36363c'), rgb('#5c5c66'), rgb('#121216')
YL, YM, YD, YO = rgb('#f2c443'), rgb('#d9a227'), rgb('#a8761a'), rgb('#2e1e04')
CL, CM, CD, CT, CO = rgb('#e6bd7d'), rgb('#c8995a'), rgb('#9c7238'), rgb('#efe0b0'), rgb('#2c1c08')
TOY_R, TOY_B, WHITE = rgb('#e2404a'), rgb('#4a90e2'), rgb('#ffffff')

class Canvas:
    def __init__(s, w, h): s.w, s.h, s.px = w, h, [[T] * w for _ in range(h)]
    def put(s, x, y, c):
        if 0 <= x < s.w and 0 <= y < s.h: s.px[y][x] = c
    def get(s, x, y): return s.px[y][x] if 0 <= x < s.w and 0 <= y < s.h else T
    def fill(s, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): s.put(x, y, c)
    def box(s, x0, y0, x1, y1, fill, outline):
        s.fill(x0, y0, x1, y1, outline); s.fill(x0 + 1, y0 + 1, x1 - 1, y1 - 1, fill)
    def image(s):
        im = Image.new('RGBA', (s.w, s.h))
        for y in range(s.h):
            for x in range(s.w): im.putpixel((x, y), s.px[y][x])
        return im

# --- copper pipes --------------------------------------------------------------------------------------------
PIPE_ROWS = [PO, PB, PL, PM, PM, PD, PO]          # a horizontal pipe seen from the side (top to bottom), 7 rows

def pipe_h(flange=True):
    cv = Canvas(16, 12)
    top = 3
    for x in range(16):
        for i, c in enumerate(PIPE_ROWS): cv.put(x, top + i, c)
    if not flange:                                                        # (a plain piece: the joints come unevenly)
        cv.fill(0, 10, 15, 10, SH); cv.fill(0, 11, 15, 11, SH) if False else None
        for x in range(16): cv.put(x, 10, SH)
        return cv
    for x in (6, 7):                                                      # a flange (joint ring) with bolts
        cv.fill(x, top - 1, x, top + 7, PO)
    cv.fill(5, top - 1, 8, top - 1, PO); cv.fill(5, top + 7, 8, top + 7, PO)
    for y in range(top, top + 7): cv.put(5, y, PD if y > top + 3 else PM); cv.put(8, y, PD if y > top + 3 else PM)
    cv.put(6, top + 1, PL); cv.put(7, top + 1, PL)
    for y in range(top, top + 7): cv.put(6, y, PO if y in (top, top + 6) else (PL if y < top + 3 else PM)); cv.put(7, y, PO if y in (top, top + 6) else (PM if y < top + 3 else PD))
    cv.fill(0, 11, 15, 11, SH)
    cv.fill(0, 10, 15, 10, T)
    for x in range(16): cv.put(x, 10, SH)
    return cv

def pipe_h_end():
    """The pipe goes down into the floor: an elbow with a big flange on the ground."""
    cv = Canvas(8, 12)
    top = 3
    for x in range(4, 8):
        for i, c in enumerate(PIPE_ROWS): cv.put(x, top + i, c)
    cv.fill(0, 1, 6, 10, PO)                                              # the floor flange / box the pipe comes from
    cv.fill(1, 2, 5, 2, PB); cv.fill(1, 3, 5, 4, PL); cv.fill(1, 5, 5, 7, PM); cv.fill(1, 8, 5, 9, PD)
    for (x, y) in [(1, 3), (5, 3), (1, 8), (5, 8)]: cv.put(x, y, PO)        # bolts
    cv.fill(1, 11, 7, 11, SH); cv.put(7, 10, SH)
    return cv

PIPE_COLS = [PO, PB, PL, PM, PD, PO]               # a vertical pipe seen from above (left to right), 6 columns

def pipe_v(flange=True):
    cv = Canvas(12, 16)
    for y in range(16):
        for i, c in enumerate(PIPE_COLS): cv.put(3 + i, y, c)
        cv.put(9, y, SH)
    if flange:
        y0 = 6                                                            # a flange
        cv.fill(2, y0, 9, y0 + 2, PO)
        for x in range(3, 9): cv.put(x, y0 + 1, PL if x < 6 else PD)
    return cv

def pipe_v_cap(top_piece):
    cv = Canvas(12, 6)
    rows = range(1, 6) if top_piece else range(0, 5)
    for y in rows:
        for i, c in enumerate(PIPE_COLS): cv.put(3 + i, y, c)
        cv.put(9, y, SH)
    y0 = 0 if top_piece else 2                                            # the end: a wide flange with bolts
    cv.fill(1, y0, 10, y0 + 3, PO); cv.fill(2, y0 + 1, 9, y0 + 1, PL); cv.fill(2, y0 + 2, 9, y0 + 2, PD)
    cv.put(2, y0 + 1, PO); cv.put(9, y0 + 1, PO)
    cv.fill(2, y0 + 4, 11, y0 + 4, SH) if not top_piece else None
    return cv

# --- conveyor belt with boxes -------------------------------------------------------------------------------
def cardboard(cv, x, y, w, h, top_h):
    """A box in 3/4 view: its lid (top_h rows), then its front."""
    cv.box(x, y, x + w - 1, y + h - 1, CM, CO)
    cv.fill(x + 1, y + 1, x + w - 2, y + top_h, CL)
    cv.fill(x + 1, y + top_h + 1, x + w - 2, y + top_h + 1, CO)
    cv.fill(x + w // 2, y + 1, x + w // 2, y + top_h, CT)                  # tape over the lid
    cv.fill(x + w - 2, y + top_h + 2, x + w - 2, y + h - 2, CD)           # its right side in shade

def ball(cv, x, y, c, dark):
    """A round toy ball (5x5 inside an outline), shine top-left, shade bottom-right."""
    shape = ["  ooo  ", " occco ", "occcddo", "occcddo", "occddd o"[:7], " odddo ", "  ooo  "]
    shape = ["  ooo  ", " oWcco ", "ocWccdo", "occccdo", "occcddo", " oddo  ", "  ooo  "]
    for dy, row in enumerate(shape):
        for dx, ch in enumerate(row):
            col = {"o": dark, "c": c, "d": tuple(max(0, int(v * 0.72)) for v in c[:3]) + (255,), "W": WHITE}.get(ch)
            if col: cv.put(x + dx - 1, y + dy - 1, col)

def belt_h(variant=0):
    cv = Canvas(16, 22)
    cv.fill(0, 0, 15, 0, RO)
    cv.fill(0, 1, 15, 1, YL)                                              # the back rail
    cv.fill(0, 2, 15, 2, RO)
    for y in range(3, 11):                                               # the belt, ribs across
        for x in range(16): cv.put(x, y, RBd if x % 4 == 0 else (RBl if y == 3 else RB))
    cv.fill(0, 11, 15, 11, RO)
    cv.fill(0, 12, 15, 12, YL)                                            # the front edge (lit)
    for y in range(13, 19):                                              # the yellow machine side
        for x in range(16): cv.put(x, y, YM if y < 17 else YD)
    for x in (2, 10): cv.put(x, 14, YO); cv.put(x, 17, YO)                # rivets
    for x in range(16):                                                  # a hazard stripe at the bottom
        cv.put(x, 18, RO if (x // 2) % 2 == 0 else YL)
    cv.fill(0, 19, 15, 19, YD); cv.fill(0, 20, 15, 20, YO); cv.fill(0, 21, 15, 21, SH)
    if variant == 0:
        cardboard(cv, 1, 2, 8, 8, 3); ball(cv, 11, 5, TOY_R, rgb('#4a0a10'))
    else:
        cardboard(cv, 7, 3, 7, 7, 2); ball(cv, 2, 5, TOY_B, rgb('#0c1e40'))
    return cv

def belt_h_end():
    """The belt's end: the big roller drum in a yellow frame."""
    cv = Canvas(6, 22)
    cv.fill(0, 0, 5, 20, YO)
    cv.fill(1, 1, 4, 1, YL); cv.fill(1, 2, 4, 11, YM)
    for y in range(3, 11): cv.put(2, y, YL)                              # the frame's lit edge
    cv.fill(1, 12, 4, 12, YL); cv.fill(1, 13, 4, 17, YM); cv.fill(1, 18, 4, 19, YD)
    cv.box(1, 4, 4, 9, RB, RO); cv.put(2, 6, RBl); cv.put(2, 7, RBl)        # the roller's axle cap
    cv.put(2, 15, YO)
    cv.fill(1, 21, 5, 21, SH)
    return cv

def belt_v(variant=0):
    cv = Canvas(22, 16)
    for y in range(16):
        cv.put(1, y, RO); cv.put(2, y, YL); cv.put(3, y, YM); cv.put(4, y, RO)     # left rail
        cv.put(17, y, RO); cv.put(18, y, YL); cv.put(19, y, YD); cv.put(20, y, RO) # right rail
        cv.put(21, y, SH)
        for x in range(5, 17): cv.put(x, y, RBd if y % 4 == 0 else RB)
    if variant == 0:
        cardboard(cv, 6, 1, 8, 8, 3); ball(cv, 11, 11, TOY_R, rgb('#4a0a10'))
    else:
        cardboard(cv, 8, 7, 7, 7, 2); ball(cv, 7, 1, TOY_B, rgb('#0c1e40'))
    return cv

def belt_v_top():
    cv = Canvas(22, 6)
    cv.fill(1, 0, 20, 5, YO)
    cv.fill(2, 1, 19, 1, YL); cv.fill(2, 2, 19, 4, YM)
    cv.box(6, 1, 15, 4, RB, RO); cv.fill(7, 2, 14, 2, RBl)                    # the roller
    for y in range(4, 6): cv.put(21, y, SH)
    return cv

def belt_v_end():
    cv = Canvas(22, 12)
    for y in range(0, 3):
        cv.put(1, y, RO); cv.put(2, y, YL); cv.put(3, y, YM); cv.put(4, y, RO)
        cv.put(17, y, RO); cv.put(18, y, YL); cv.put(19, y, YD); cv.put(20, y, RO); cv.put(21, y, SH)
        for x in range(5, 17): cv.put(x, y, RB)
    cv.fill(1, 3, 20, 3, RO); cv.fill(1, 4, 20, 4, YL)
    cv.fill(1, 5, 20, 9, YM); cv.put(1, 5, RO)
    for y in range(5, 10): cv.put(1, y, RO); cv.put(20, y, RO); cv.put(21, y, SH)
    for x in range(2, 20): cv.put(x, 9, RO if (x // 2) % 2 == 0 else YL)
    cv.put(4, 6, YO); cv.put(17, 6, YO)
    cv.fill(1, 10, 20, 10, YO); cv.fill(2, 11, 21, 11, SH)
    return cv

# --- pillars ---------------------------------------------------------------------------------------------
def crate(cv, x, y, s, top_h):
    """A wooden crate in 3/4 view: s px wide, its top (top_h rows) and its front with planks + metal corners."""
    cv.box(x, y, x + s - 1, y + s - 1, WM, WO)
    cv.fill(x + 1, y + 1, x + s - 2, y + top_h, WL)                       # the top
    cv.fill(x + 1, y + top_h + 1, x + s - 2, y + top_h + 1, WO)
    for py in range(y + top_h + 2 + 3, y + s - 1, 4): cv.fill(x + 1, py, x + s - 2, py, WD)   # planks
    cv.fill(x + s - 2, y + top_h + 2, x + s - 2, y + s - 2, WD)           # right side in shade
    for cx, cy in [(x + 1, y + top_h + 2), (x + s - 3, y + top_h + 2), (x + 1, y + s - 3), (x + s - 3, y + s - 3)]:
        cv.fill(cx, cy, cx + 1, cy + 1, ML); cv.put(cx + 1, cy + 1, MD)     # metal corners
    for gx in range(x + 3, x + s - 3, 4): cv.put(gx, y + 1 + top_h // 2, WM)   # the top's boards

def barrel():
    cv = Canvas(20, 20)
    x0, x1, top, bottom = 4, 15, 2, 17
    for y in range(top + 3, bottom):                                     # the body
        cv.put(x0, y, BO); cv.put(x1, y, BO)
        for x in range(x0 + 1, x1):
            cv.put(x, y, BL if x < x0 + 4 else (BM if x < x1 - 3 else BD))
    for y in (top + 6, bottom - 4):                                      # rims round it
        for x in range(x0 + 1, x1): cv.put(x, y, BR if x < x0 + 4 else BD)
    for x in range(x0 + 1, x1): cv.put(x, top + 3, BO)
    cv.fill(x0 + 1, top, x1 - 1, top, BO); cv.put(x0, top + 1, BO); cv.put(x1, top + 1, BO); cv.put(x0, top + 2, BO); cv.put(x1, top + 2, BO)
    cv.fill(x0 + 1, top + 1, x1 - 1, top + 2, BR)                         # the lid seen from above
    cv.fill(x0 + 7, top + 1, x0 + 8, top + 1, BO)                         # its cap
    cv.fill(x0 + 1, bottom, x1 - 1, bottom, BO)
    for y in range(top + 8, top + 12):                                   # a white hazard label
        for x in range(x0 + 4, x0 + 8): cv.put(x, y, WHITE if not (y == top + 9 and x in (x0 + 5, x0 + 6)) else BO)
    cv.fill(x0 + 2, bottom + 1, x1 + 1, bottom + 1, SH); cv.fill(x1 + 1, top + 4, x1 + 1, bottom, SH)
    return cv

def crate_medium():
    cv = Canvas(28, 28)
    crate(cv, 2, 3, 23, 7)
    cv.fill(4, 26, 26, 26, SH); cv.fill(25, 5, 25, 25, SH)
    return cv

def crate_stack():
    cv = Canvas(36, 36)
    crate(cv, 1, 13, 21, 6)                                               # bottom left
    crate(cv, 14, 15, 20, 6)                                              # bottom right (a bit in front)
    crate(cv, 7, 1, 18, 5)                                                # on top
    cv.fill(3, 34, 35, 34, SH); cv.fill(34, 17, 34, 33, SH)
    return cv

SPRITES = {
    "toy_factory_wall_h": lambda: pipe_h(True), "toy_factory_wall_h_2": lambda: pipe_h(False),
    "toy_factory_wall_h_end": pipe_h_end,
    "toy_factory_wall_v": lambda: pipe_v(True), "toy_factory_wall_v_2": lambda: pipe_v(False),
    "toy_factory_wall_v_top": lambda: pipe_v_cap(True), "toy_factory_wall_v_end": lambda: pipe_v_cap(False),
    "toy_factory_wall_thick_h": lambda: belt_h(0), "toy_factory_wall_thick_h_2": lambda: belt_h(1),
    "toy_factory_wall_thick_h_end": belt_h_end,
    "toy_factory_wall_thick_v": lambda: belt_v(0), "toy_factory_wall_thick_v_2": lambda: belt_v(1),
    "toy_factory_wall_thick_v_top": belt_v_top, "toy_factory_wall_thick_v_end": belt_v_end,
    "toy_factory_pillar_small": barrel, "toy_factory_pillar_medium": crate_medium, "toy_factory_pillar_large": crate_stack,
}
if __name__ == "__main__":
    for name, make in SPRITES.items():
        im = make().image(); im.save(f"{sys.argv[1]}/{name}.png"); print(name, im.size)
