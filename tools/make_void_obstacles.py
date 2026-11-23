# The Void obstacles (pixel art 1:4, 23.11): planets (pillars, 2 kinds per size - mixed kinds, muted towards violet;
# SPINNING: 3 frames each),
# galaxies (thick walls: a flowing star band with a spinning spiral at each end - ANIMATED: 3 frames, <piece>,
# <piece>_frame2, <piece>_frame3, the game shows them in a loop; no dark outline) and asteroid belts (thin walls).
# Everything floats in space: no shadow, a faint half-transparent glow round it instead (not solid). The colours
# follow the_void.png (near-black with white, teal and green stars). In every frame the solid pixels are the same,
# only the colours inside move - so the collision mask of frame 1 holds for all of them.
# Run: py tools/make_void_obstacles.py <folder> - into another folder, then copy over what you need.
import math, sys
from PIL import Image

T = (0, 0, 0, 0)
def rgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) + (255,)
FRAMES = 3                                                    # animation frames of the galaxies
# galaxies: core -> arms -> dust
G_CORE, G_BRIGHT, G_ARM, G_ARM_DARK = rgb('#f4fff8'), rgb('#a8f0e0'), rgb('#4fb8a8'), rgb('#2f7a8a')
G_DUST, G_DEEP, G_OUT, STAR = rgb('#4a3a8a'), rgb('#241a52'), rgb('#07051a'), rgb('#ffffff')
GLOW_TEAL, GLOW_VIOLET = (90, 200, 190), (130, 100, 220)
# asteroids
A_LIGHT, A_MID, A_DARK, A_OUT = rgb('#8a8296'), rgb('#625a72'), rgb('#433c52'), rgb('#0e0b16')
# planets
P_OUT = rgb('#0a0716')
MOON = (rgb('#b4aec4'), rgb('#8a84a0'), rgb('#5e5878'), rgb('#3e3a56'))               # light .. deep
ICE = (rgb('#d6f6f4'), rgb('#8ad8d8'), rgb('#4aa0b0'), rgb('#2a6a80'))
GAS = (rgb('#e8b088'), rgb('#c07a78'), rgb('#8a5080'), rgb('#56306a'))                 # muted orange -> violet
OCEAN = (rgb('#8ae0b8'), rgb('#3a9a8e'), rgb('#2a6a7a'), rgb('#1a4058'))
GIANT = (rgb('#e0a8d8'), rgb('#b07ac8'), rgb('#7a4aa8'), rgb('#462a78'))
NIGHT = (rgb('#5a6ab8'), rgb('#3a4688'), rgb('#262e60'), rgb('#161a3e'))
RING, RING_DARK = rgb('#d8cce8'), rgb('#9a8cb4')
AURORA, CITY = rgb('#6ff2b0'), rgb('#ffe08a')

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


def glow(cv, colour, alpha=60, reach=1):
    """A faint glow round everything solid: half-transparent pixels on the empty ones (not solid)."""
    for step in range(reach):
        a = alpha // (step + 1)
        solid = [(x, y) for y in range(cv.h) for x in range(cv.w) if cv.px[y][x][3] >= (255 if step == 0 else 1)]
        add = set()
        for x, y in solid:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if cv.get(x + dx, y + dy) == T and 0 <= x + dx < cv.w and 0 <= y + dy < cv.h: add.add((x + dx, y + dy))
        for x, y in add: cv.put(x, y, (colour[0], colour[1], colour[2], a))

def hashed(x, y, seed=0):
    return (x * 374761393 + y * 668265263 + seed * 2654435761) % 1000003 % 100

# --- planets (23.11: spinning - 3 frames; the surface turns, the light, the outline and the rings stay) ------------
SPIN = 2 * math.pi / 3 / FRAMES     # how far the surface turns per frame: its pattern repeats 3x round the planet

def near(lon, lat, spots, size):
    """Is (lon, lat) within `size` of one of the spots? Spots repeat 3x round the planet (so the spin loops)."""
    for slon, slat in spots:
        d = (lon - slon) % (2 * math.pi / 3)
        d = min(d, 2 * math.pi / 3 - d)
        if d * d + (lat - slat) ** 2 < size * size: return True
    return False

def sphere(cv, cx, cy, r, pal, frame, surface=None, cap=False):
    """A spinning planet lit from the top-left: pal = (light, mid, dark, deep).
    surface(lon, lat) -> None (plain), "dark" (one shade darker), "light" or a colour."""
    light, mid, dark, deep = pal
    darker = {light: mid, mid: dark, dark: deep, deep: deep}
    lighter = {light: light, mid: light, dark: mid, deep: dark}
    for y in range(int(cy - r) - 1, int(cy + r) + 2):
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            dx, dy = (x - cx) / r, (y - cy) / r
            if dx * dx + dy * dy > 1: continue
            lit = -0.6 * dx - 0.7 * dy + 0.25
            c = light if lit > 0.75 else mid if lit > 0.05 else dark if lit > -0.55 else deep
            lat = math.asin(max(-1, min(1, dy)))
            lon = math.asin(max(-1, min(1, dx / max(0.05, math.cos(lat))))) + frame * SPIN
            mark = surface(lon, lat, lit) if surface else None
            if mark == "dark": c = darker[c]
            elif mark == "light": c = lighter[c]
            elif mark: c = mark
            if cap and dy < -0.62: c = rgb('#f4fffc') if lit > -0.3 else ICE[1]
            cv.put(x, y, c)

def ring(cv, cx, cy, rx, ry, front, planet_r):
    """A tilted ring: the back half (behind the planet) or the front half (over it)."""
    for t in range(0, 360, 2):
        a = math.radians(t)
        for k in (0, 1):
            x, y = cx + (rx - k) * math.cos(a), cy + (ry - k * 0.4) * math.sin(a)
            is_front = math.sin(a) > 0
            if is_front != front: continue
            inside = (x - cx) ** 2 + (y - cy) ** 2 < planet_r ** 2
            if not front and inside: continue
            cv.put(int(round(x)), int(round(y)), RING if k == 0 and math.cos(a) < 0.3 else RING_DARK)

def craters(lon, lat, lit):
    if near(lon, lat, [(0.3, -0.3), (1.2, 0.5)], 0.32): return "dark"
    if near(lon, lat, [(0.8, -0.6), (1.6, 0.0), (0.6, 0.7)], 0.18): return "dark"
    return None

def ice_clouds(lon, lat, lit):
    if abs(lat - (0.15 + 0.15 * math.sin(lon * 3))) < 0.1 or abs(lat - (0.6 + 0.1 * math.sin(lon * 3 + 1))) < 0.08:
        return rgb('#e8fff6')
    return None

def gas_bands(lon, lat, lit):
    if near(lon, lat, [(0.9, 0.35)], 0.22): return GAS[3]                   # the storm spot
    wave = 0.12 * math.sin(lon * 3 * 2)
    return "dark" if int((lat + wave + 2) / 0.32) % 2 == 0 else None

def ocean(lon, lat, lit):
    land = math.sin(lon * 3) * math.cos(lat * 2.2) + 0.5 * math.sin(lon * 6 + lat * 4) > 0.55
    cloud = abs(lat + 0.25 + 0.15 * math.sin(lon * 3 + 2)) < 0.08
    return rgb('#e8fff6') if cloud else (rgb('#6fbf6a') if land and lit > -0.2 else (rgb('#3f8a4a') if land else None))

def giant_bands(lon, lat, lit):
    if near(lon, lat, [(1.6, 0.25)], 0.2): return "light"
    wave = 0.08 * math.sin(lon * 3 * 2 + 1)
    band = int((lat + wave + 2) / 0.22) % 3
    return "dark" if band == 0 else None

def night_lights(lon, lat, lit):
    if lit < -0.1 and near(lon, lat, [(0.2, 0.2), (0.5, 0.45), (1.0, 0.1), (1.4, 0.55), (1.8, 0.3), (0.8, 0.7)], 0.09):
        return CITY
    return None

def planet(kind, size, frame=0):
    cv = Canvas(size, size)
    c = size / 2 - 0.5
    if size == 20:
        if kind == 0: sphere(cv, c, c, 7.5, MOON, frame, craters)
        else: sphere(cv, c, c, 7, ICE, frame, ice_clouds, cap=True)
        cv.outline(P_OUT); glow(cv, GLOW_TEAL, 55, 2)
    elif size == 28:
        if kind == 0:
            sphere(cv, c, c, 10.5, GAS, frame, gas_bands)
        else:
            ring(cv, c, c + 1, 13, 3.5, False, 9)
            sphere(cv, c, c, 9, OCEAN, frame, ocean)
            ring(cv, c, c + 1, 13, 3.5, True, 9)
        cv.outline(P_OUT); glow(cv, GLOW_VIOLET if kind == 0 else GLOW_TEAL, 55, 2)
    else:
        if kind == 0:                                                        # a ringed giant
            ring(cv, c, c + 1, 17, 4.5, False, 12)
            sphere(cv, c, c, 12, GIANT, frame, giant_bands)
            ring(cv, c, c + 1, 17, 4.5, True, 12)
        else:                                                                # a dark world with lights and an aurora
            sphere(cv, c, c, 12.5, NIGHT, frame, night_lights)
            for x in range(10, 26):                                         # the aurora round its pole (it doesn't spin)
                y = int(round(8 + 1.5 * math.sin(x / 2.2)))
                if cv.get(x, y)[3] == 255: cv.put(x, y, AURORA)
            sphere(cv, 29, 7, 2.5, MOON, frame)                              # a little moon
        cv.outline(P_OUT); glow(cv, GLOW_VIOLET, 55, 2)
    return cv

# --- galaxies (thick walls, animated) ---------------------------------------------------------------------------------
def galaxy_colour(bright):
    return G_CORE if bright > 0.92 else G_BRIGHT if bright > 0.72 else G_ARM if bright > 0.5 else \
        G_ARM_DARK if bright > 0.32 else G_DUST if bright > 0.15 else G_DEEP

def stars(cv, frame, seed):
    """Stars over the galaxy: most stay, a few twinkle (shown only in some frames)."""
    for y in range(cv.h):
        for x in range(cv.w):
            if cv.px[y][x][3] != 255: continue
            h = hashed(x, y, seed)
            if h < 3 or (h < 6 and (h + frame) % 3 == 0): cv.put(x, y, STAR)

def band(cv, frame, along_x, x0, x1, seed=1):
    """The star band of a galaxy between x0 and x1 (along the wall); its arms flow along it frame by frame.
    The pattern repeats every 16 px and every 3 frames, so the pieces and the loop fit."""
    phase = 2 * math.pi * frame / FRAMES
    length, across = (cv.w, cv.h) if along_x else (cv.h, cv.w)
    mid = (across - 1) / 2
    for u in range(x0, x1):
        half = 6.5 + 0.8 * math.sin(2 * math.pi * u / 16)                  # the band's thickness (the same in every frame)
        for v in range(across):
            k = (v - mid) / half
            if abs(k) > 1: continue
            arm = 0.5 + 0.5 * math.sin(2 * math.pi * u / 16 + k * 2.6 - phase)          # one slanted streak per 16 px
            bright = (1 - abs(k)) ** 1.4 * 0.62 + arm * 0.3 * (1 - abs(k) * 0.5) - 0.08
            cv.put(*((u, v) if along_x else (v, u)), galaxy_colour(bright))

def spiral(cv, cx, cy, r, frame, squash=0.8, spin=1):
    """A spinning two-armed spiral (its outline is the same in every frame; the arms turn by 1/3 of half a turn)."""
    phase = spin * math.pi * frame / FRAMES
    for y in range(cv.h):
        for x in range(cv.w):
            dx, dy = (x - cx), (y - cy) / squash
            d = math.hypot(dx, dy)
            if d > r: continue
            a = math.atan2(dy, dx)
            arm = 0.5 + 0.5 * math.cos(2 * (a - phase) - 3.2 * math.log(d + 1))
            bright = (1 - d / r) ** 1.6 * 1.25 + arm * 0.55 * min(1, d / (r * 0.4)) - 0.1
            cv.put(x, y, galaxy_colour(bright))

def finish_galaxy(cv, frame, seed):
    stars(cv, frame, seed)                                                   # (23.11, Filip) no dark outline
    glow(cv, GLOW_TEAL, 50, 2)
    return cv

def galaxy_h(frame):
    cv = Canvas(16, 22)
    band(cv, frame, True, 0, 16)
    return finish_galaxy(cv, frame, 1)

def galaxy_h_end(frame):
    """The left end (16 x 22): a spinning spiral the band comes out of (the right end is its mirror)."""
    cv = Canvas(16, 22)
    band(cv, frame, True, 8, 16)
    spiral(cv, 8, 10.5, 7.5, frame)
    return finish_galaxy(cv, frame, 2)

def galaxy_v(frame):
    cv = Canvas(22, 16)
    band(cv, frame, False, 0, 16)
    return finish_galaxy(cv, frame, 3)

def galaxy_v_cap(frame, top):
    """The top / bottom piece (22 x 16): a spiral the vertical band comes out of."""
    cv = Canvas(22, 16)
    band(cv, frame, False, 8, 16) if top else band(cv, frame, False, 0, 8)
    spiral(cv, 10.5, 7.5 if top else 8.5, 8, frame, squash=0.85, spin=1 if top else -1)
    return finish_galaxy(cv, frame, 4 if top else 5)

# --- thin walls: asteroid belts -------------------------------------------------------------------------------------
def rock(cv, cx, cy, r, seed):
    for y in range(int(cy - r) - 1, int(cy + r) + 2):
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            wob = 1 + 0.18 * math.sin(math.atan2(y - cy, x - cx) * 3 + seed)        # lumpy, not round
            d = math.hypot(x - cx, (y - cy) * 1.1) / (r * wob)
            if d > 1: continue
            lit = -(x - cx) - (y - cy)
            cv.put(x, y, A_LIGHT if lit > r * 0.6 else A_MID if lit > -r * 0.4 else A_DARK)
    if r >= 2: cv.put(int(cx + 0.5), int(cy + 0.5), A_DARK)                        # a pit

def belt(cv, rocks, dust):
    for x, y, r, s in rocks: rock(cv, x, y, r, s)
    cv.outline(A_OUT)
    for x, y in dust:
        if cv.get(x, y) == T: cv.put(x, y, A_MID)
    glow(cv, GLOW_VIOLET, 40, 1)
    return cv

def belt_h():
    return belt(Canvas(16, 12), [(3, 6, 2.6, 0), (8.5, 4.5, 1.4, 1), (12.5, 7, 2.2, 2), (8, 8.5, 0.9, 3)], [(6, 3), (15, 4), (10, 10), (1, 9)])

def belt_h_end():
    return belt(Canvas(8, 12), [(5, 6, 1.6, 4), (2, 7.5, 0.8, 5)], [(1, 4), (7, 9)])

def belt_v():
    return belt(Canvas(12, 16), [(6, 3, 2.6, 0), (4.5, 8.5, 1.4, 1), (7, 12.5, 2.2, 2), (8.5, 8, 0.9, 3)], [(3, 6), (4, 15), (10, 10), (9, 1)])

def belt_v_cap(top):
    return belt(Canvas(12, 6), [(6, 3.5 if top else 2.5, 1.6, 4), (8, 1.5 if top else 4, 0.8, 5)], [(4, 1), (3, 5)])

SPRITES = {
    "the_void_wall_h": belt_h, "the_void_wall_h_end": belt_h_end,
    "the_void_wall_v": belt_v, "the_void_wall_v_top": lambda: belt_v_cap(True), "the_void_wall_v_end": lambda: belt_v_cap(False),
}
for frame in range(FRAMES):
    tag = "" if frame == 0 else f"_frame{frame + 1}"
    SPRITES[f"the_void_wall_thick_h{tag}"] = (lambda f: lambda: galaxy_h(f))(frame)
    SPRITES[f"the_void_wall_thick_h_end{tag}"] = (lambda f: lambda: galaxy_h_end(f))(frame)
    SPRITES[f"the_void_wall_thick_v{tag}"] = (lambda f: lambda: galaxy_v(f))(frame)
    SPRITES[f"the_void_wall_thick_v_top{tag}"] = (lambda f: lambda: galaxy_v_cap(f, True))(frame)
    SPRITES[f"the_void_wall_thick_v_end{tag}"] = (lambda f: lambda: galaxy_v_cap(f, False))(frame)
for i, suffix in enumerate(["", "_2"]):
    for size, label in ((20, "small"), (28, "medium"), (36, "large")):
        for frame in range(FRAMES):                                          # (23.11) spinning planets
            tag = "" if frame == 0 else f"_frame{frame + 1}"
            SPRITES[f"the_void_pillar_{label}{suffix}{tag}"] = (lambda k, s, f: lambda: planet(k, s, f))(i, size, frame)

if __name__ == "__main__":
    for name, make in SPRITES.items():
        im = make().image(); im.save(f"{sys.argv[1]}/{name}.png"); print(name, im.size)
