# Combat objects (pixel art 1:4, 23.11): Frost Golem's ice wall tile (+ cracked), the Assembly Line's conveyor belt
# (factory style: dark rubber with ribs, metal edges with yellow-black hazard stripes, yellow arrows), its nozzles
# and vents (+ hot), Night Bloom's golden light seed, the Void's crystal turret with an eye (+ its pupil, moved by
# the game) and Milo's metal mine with a red lamp (+ blink). Outline = a very dark shade of the object's colour.
# Run: py tools/make_combat_objects.py <folder> - into another folder, then copy over what you need.
import sys
from PIL import Image

T = (0, 0, 0, 0)
def rgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) + (255,)
I_SHINE, I_TOP, I_EDGE, I_MID, I_FRONT, I_DEEP = rgb('#f2fcff'), rgb('#a8e6fa'), rgb('#9fd9ea'), rgb('#7fd0f0'), rgb('#62c0e8'), rgb('#4aa6d4')
I_CRACK = rgb('#1c5a86')                                       # Filip's tundra ice colours + a crack
M_LIGHT, M_MID, M_DARK, M_DEEP, M_OUT, BOLT = rgb('#9a9ca8'), rgb('#6c6e7a'), rgb('#4a4c56'), rgb('#33343c'), rgb('#101116'), rgb('#c8cad4')
Y_HAZ, K_HAZ = rgb('#f2c230'), rgb('#26252a')
R_LIGHT, R_MID, R_DARK, R_EDGE = rgb('#4a4850'), rgb('#38363e'), rgb('#26252b'), rgb('#1a191e')
ARROW, ARROW_DARK, ARROW_OUT = rgb('#ffd23a'), rgb('#c8961a'), rgb('#2a1e04')
WARN, WARN_DARK = rgb('#ff8a2a'), rgb('#c0500e')
HOT, HOT_CORE = rgb('#ff7a3a'), rgb('#ffe0a0')
SEED_WHITE, SEED_HI, SEED_MID, SEED_DARK, SEED_OUT, SEED_SPROUT = rgb('#fffbe6'), rgb('#ffe48a'), rgb('#ffc63a'), rgb('#d08a1a'), rgb('#3a2204'), rgb('#7ac85a')
C_SHINE, C_LIGHT, C_MID, C_DARK, C_OUT = rgb('#e6dcff'), rgb('#a88ae8'), rgb('#6e52c0'), rgb('#3e2a80'), rgb('#0c0624')
EYE_WHITE, EYE_RIM, PUPIL, PUPIL_GLINT = rgb('#c8fff4'), rgb('#4fb8a8'), rgb('#0c1a2a'), rgb('#6ff2e6')
MM_LIGHT, MM_MID, MM_DARK, MM_SPIKE, MM_OUT = rgb('#8a8f9c'), rgb('#5e6270'), rgb('#3e414c'), rgb('#b4b8c4'), rgb('#0c0d12')
LAMP_ON, LAMP_CORE, LAMP_DIM, LAMP_OFF = rgb('#ff4058'), rgb('#ffd0d4'), rgb('#a01c2c'), rgb('#4a1a20')

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


def glow(cv, colour, alpha=60):
    add = set()
    for y in range(cv.h):
        for x in range(cv.w):
            if cv.px[y][x][3] != 255: continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if 0 <= x + dx < cv.w and 0 <= y + dy < cv.h and cv.get(x + dx, y + dy) == T: add.add((x + dx, y + dy))
    for x, y in add: cv.put(x, y, (colour[0], colour[1], colour[2], alpha))

def hashed(x, y, seed=0):
    return (x * 374761393 + y * 668265263 + seed * 2654435761) % 1000003 % 100

# --- Frost Golem's ice wall: a seamless 16 x 16 tile (no outline - it repeats on every side) --------------------------
def ice_wall(cracked=False):
    cv = Canvas(16, 16)
    for y in range(16):
        for x in range(16):
            # big slanted facets: the colour follows bands running down-right, repeating every 16 px both ways
            band = ((x + y * 2) % 16) / 16
            c = I_TOP if band < 0.3 else I_MID if band < 0.65 else I_FRONT if band < 0.9 else I_EDGE
            if (x - y) % 16 in (0, 8) and band < 0.65: c = I_DEEP                     # facet edges
            cv.put(x, y, c)
    for x, y in ((3, 2), (4, 2), (4, 3), (11, 9), (12, 9), (12, 10), (7, 13)):             # shine
        cv.put(x, y, I_SHINE)
    if cracked:
        for x, y in ((2, 5), (3, 6), (4, 6), (5, 7), (6, 8), (6, 9), (7, 10), (5, 9), (4, 10), (9, 3), (10, 4), (10, 5),
                     (11, 6), (12, 6), (13, 7), (8, 11), (9, 12), (10, 12)):
            cv.put(x, y, I_CRACK)
        for x, y in ((3, 5), (5, 6), (7, 9), (11, 5), (13, 6)): cv.put(x, y, I_SHINE)          # the lit edge of a crack
    return cv

# --- the conveyor belt (Assembly Line): 20 x 27, repeats sideways; the game scrolls it -----------------------------------
def belt():
    cv = Canvas(20, 27)
    for x in range(20):
        hazard = Y_HAZ if (x // 3) % 2 == 0 else K_HAZ                                    # yellow-black stripes, slanted
        for y in range(0, 5):                                                              # the top edge (metal + stripes)
            stripe = Y_HAZ if ((x + y) // 3) % 2 == 0 else K_HAZ
            cv.put(x, y, M_LIGHT if y == 0 else stripe if y in (1, 2, 3) else M_DARK)
        for y in range(5, 22):                                                             # the rubber with ribs
            rib = x % 5
            cv.put(x, y, R_LIGHT if rib == 0 else R_DARK if rib == 4 else R_MID)
        cv.put(x, 5, R_EDGE); cv.put(x, 21, R_EDGE)
        for y in range(22, 27):                                                            # the bottom edge
            stripe = Y_HAZ if ((x + y) // 3) % 2 == 0 else K_HAZ
            cv.put(x, y, M_DARK if y == 22 else stripe if y in (23, 24, 25) else M_DEEP)
    for x in (2, 12):                                                                      # bolts on the edges
        cv.put(x, 0, BOLT); cv.put(x + 5, 26, BOLT)
    return cv

def arrow(colour, dark):
    """A chevron pointing right (8 x 12)."""
    cv = Canvas(8, 12)
    for i in range(6):
        for t in range(3):
            cv.put(1 + i + t - 1, i, colour if t else dark); cv.put(1 + i + t - 1, 11 - i, colour if t else dark)
    cv.outline(ARROW_OUT)
    return cv

def nozzle(hot):
    """The nozzle in the left side wall, its mouth to the right (7 x 11)."""
    cv = Canvas(7, 11)
    cv.fill(0, 0, 3, 10, M_MID); cv.fill(0, 0, 0, 10, M_LIGHT)                             # the plate in the wall
    for y in (1, 9): cv.put(1, y, BOLT)
    cv.fill(4, 3, 6, 7, M_LIGHT); cv.fill(4, 6, 6, 7, M_DARK)                              # the pipe
    mouth = (HOT_CORE, HOT) if hot else (M_DEEP, M_DEEP)
    cv.put(6, 4, mouth[1]); cv.put(6, 5, mouth[0]); cv.put(6, 6, mouth[1])
    cv.outline(M_OUT)
    if hot: glow(cv, HOT[:3], 90)
    return cv

def vent(hot):
    """A grille in the belt's bottom edge (13 x 6)."""
    cv = Canvas(13, 6)
    cv.fill(0, 0, 12, 5, M_MID); cv.fill(0, 0, 12, 0, M_LIGHT)
    for x in range(2, 11, 2):
        for y in range(1, 5): cv.put(x, y, (HOT if y > 1 else HOT_CORE) if hot else M_DEEP)
    cv.outline(M_OUT)
    if hot: glow(cv, HOT[:3], 80)
    return cv

# --- Night Bloom's light seed: a golden glowing seed (8 x 8; the game draws the pulsing ring) -----------------------------
def light_seed():
    cv = Canvas(8, 8)
    for y in range(8):
        for x in range(8):
            dx, dy = (x - 3.5) / 2.6, (y - 3.8) / 3.4                                   # a seed: taller than wide
            if dx * dx + dy * dy > 1: continue
            lit = -dx - dy
            cv.put(x, y, SEED_HI if lit > 0.7 else SEED_MID if lit > -0.4 else SEED_DARK)
    cv.put(3, 2, SEED_WHITE); cv.put(3, 3, SEED_HI)
    cv.put(4, 0, SEED_SPROUT); cv.put(5, 0, SEED_SPROUT)                                   # a little sprout on top
    cv.outline(SEED_OUT)
    glow(cv, (255, 210, 90), 90)
    return cv

# --- the Void's turret: a crystal with an eye (13 x 13); the game moves the pupil towards where it shoots ---------------
def void_turret():
    cv = Canvas(13, 13)
    shape = [(6, 0), (5, 1), (4, 3), (3, 5), (3, 8), (4, 10), (5, 11), (6, 12)]          # the crystal's left edge (x, y)
    for y in range(13):
        half = {0: 0.5, 1: 1.5, 2: 2.5, 3: 3, 4: 3.5, 5: 4.5, 6: 5, 7: 5, 8: 5, 9: 4.5, 10: 3.5, 11: 2, 12: 1}[y]
        for x in range(13):
            k = x - 6
            if abs(k) > half: continue
            cv.put(x, y, C_LIGHT if k < -half * 0.3 and y < 9 else C_DARK if k > half * 0.4 else C_MID)
    for x, y in ((5, 2), (4, 4), (4, 5)): cv.put(x, y, C_SHINE)
    for y in range(5, 9):                                                                 # the eye (white, no pupil)
        for x in range(4, 9):
            if ((x - 6) / 2.4) ** 2 + ((y - 6.5) / 1.7) ** 2 <= 1: cv.put(x, y, EYE_WHITE)
    cv.put(4, 6, EYE_RIM); cv.put(8, 6, EYE_RIM); cv.put(4, 7, EYE_RIM); cv.put(8, 7, EYE_RIM)
    cv.outline(C_OUT)
    glow(cv, (90, 200, 190), 60)
    return cv

def void_turret_pupil():
    cv = Canvas(2, 2)
    cv.fill(0, 0, 1, 1, PUPIL); cv.put(0, 0, PUPIL_GLINT)
    return cv

# --- Milo's mine: a round metal mine with spikes and a lamp (8 x 8); _blink = the lamp lit -------------------------------
def milo_mine(lit):
    cv = Canvas(8, 8)
    for y in range(8):
        for x in range(8):
            dx, dy = (x - 3.5) / 2.8, (y - 3.8) / 2.6
            if dx * dx + dy * dy > 1: continue
            lit_side = -dx - dy
            cv.put(x, y, MM_LIGHT if lit_side > 0.6 else MM_MID if lit_side > -0.5 else MM_DARK)
    for x, y in ((3, 0), (4, 0), (0, 3), (7, 4), (3, 7), (4, 7)): cv.put(x, y, MM_SPIKE)    # spikes
    cv.put(3, 3, LAMP_ON if lit else LAMP_OFF); cv.put(4, 3, LAMP_ON if lit else LAMP_OFF)  # the lamp
    cv.put(3, 4, LAMP_DIM if lit else LAMP_OFF); cv.put(4, 4, LAMP_DIM if lit else LAMP_OFF)
    if lit: cv.put(3, 3, LAMP_CORE)
    cv.outline(MM_OUT)
    if lit: glow(cv, (255, 64, 88), 80)
    return cv

SPRITES = {
    "ice_wall": lambda: ice_wall(False), "ice_wall_cracked": lambda: ice_wall(True),
    "belt": belt, "belt_arrow": lambda: arrow(ARROW, ARROW_DARK), "belt_arrow_warn": lambda: arrow(WARN, WARN_DARK),
    "belt_nozzle": lambda: nozzle(False), "belt_nozzle_hot": lambda: nozzle(True),
    "belt_vent": lambda: vent(False), "belt_vent_hot": lambda: vent(True),
    "light_seed": light_seed, "void_turret": void_turret, "void_turret_pupil": void_turret_pupil,
    "milo_mine": lambda: milo_mine(False), "milo_mine_blink": lambda: milo_mine(True),
}
if __name__ == "__main__":
    for name, make in SPRITES.items():
        im = make().image(); im.save(f"{sys.argv[1]}/{name}.png"); print(name, im.size)
