# Silverpine Tundra enemies (pixel art 1:4, 23.11). Outline = a very dark shade of each part's colour; a black
# half-transparent shadow under them (the orb floats: its shadow lies apart); they face RIGHT (the game mirrors).
# Poses (sprites.py): frost_wolf (15 x 15) _walk1.._walk3 (a gallop), ice_shooter _aim (crossbow up, the bolt glowing, while
# it aims) + _shoot, frozen_orb _idle1.._idle5 (crystals circling it), tundra_watcher _walk1/_walk2 (steps).
# Run: py tools/make_tundra_enemies.py <folder>
import math, sys
from PIL import Image

def rgb(h, a=255): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) + (a,)
SHADOW = (0, 0, 0, 90)

def draw(rows, colours):
    h, w = len(rows), len(rows[0])
    im = Image.new('RGBA', (w, h))
    for y, row in enumerate(rows):
        assert len(row) == w, (y, row, len(row), w)
        for x, ch in enumerate(row):
            if ch != ".": im.putpixel((x, y), colours[ch])
    return im

# --- Frost Wolf (15 x 15, bigger for a face - 23.11): a white wolf with frost in its fur, ice-blue eye ------------
WOLF = {"o": rgb('#0e1a2c'), "W": rgb('#f4f8fc'), "S": rgb('#c8d8e8'), "D": rgb('#8aa4c0'), "f": rgb('#a8e6fa'),
        "e": rgb('#2ad8f0'), "n": rgb('#1a2a3a'), "m": rgb('#6a2a3a'), "t": rgb('#ffffff'), "#": SHADOW}
WOLF_BODY = [
    "...............",
    "..........oo.o.",
    ".........oWWoWo",
    "........oWWWWWo",
    "o......oWWWeWWo",
    "Wo.....oWWWWSWn",
    "oWooooooWWWmtmo",
    ".oWWfWWWWWWWoo.",
    ".oSWWWWWfWWSo..",
    "..oSSSSSSSSSo..",
]
WOLF_LEGS = {
    "": ["..oWo...oWo....", "..oDo...oDo....", "..oo....oo.....", "..##########..."],
    "_walk1": [".oWo.....oWo...", "oDo.......oDo..", "oo.........oo..", "#############.."],
    "_walk2": ["....oWooWo.....", "....oDooDo.....", "....oo.oo......", "...########...."],
    "_walk3": ["..oWo..oWo.....", ".oDo....oDo....", ".oo......oo....", ".##########...."],
}
def wolf(tag):
    body = WOLF_BODY if tag != "_walk2" else WOLF_BODY[1:] + [WOLF_BODY[-1]]   # the gathered step: body a bit up
    rows = body[:11] + WOLF_LEGS[tag]
    return draw(rows, WOLF)

# --- Ice Shooter (13 x 13): someone in a fur parka with an ice crossbow -----------------------------------------------
SHOOTER = {"o": rgb('#1a1008'), "P": rgb('#8a5a36'), "p": rgb('#5e3a20'), "F": rgb('#f2ece0'), "S": rgb('#f2c8a0'),
           "e": rgb('#1a1008'), "K": rgb('#6a4a2a'), "I": rgb('#8ad8f0'), "G": rgb('#e8fcff'), "B": rgb('#4fb8e8'),
           "x": rgb('#0c2a3a'), "#": SHADOW}
SHOOTER_BASE = [
    "....oooo.....",
    "...oFFFFo....",
    "..oFPPPPFo...",
    "..oFeSeSFo...",
    "..oFSSSSFo...",
    "...oFFFFo....",
    "..oPPPPPPo...",
    "..oPpPPPKKIx.",
    "..oPpPPPoxx..",
    "..oPPPPPPo...",
    "..oFFFFFFo...",
    "...op..po....",
    "..########...",
]
SHOOTER_AIM = [
    "....oooo.....",
    "...oFFFFo....",
    "..oFPPPPFo...",
    "..oFeSeKKKBGx",
    "..oFSSSSFxxx.",
    "...oFFFFo....",
    "..oPPPPPPo...",
    "..oPpPPPPo...",
    "..oPpPPPPo...",
    "..oPPPPPPo...",
    "..oFFFFFFo...",
    "...op..po....",
    "..########...",
]
SHOOTER_SHOT = [r for r in SHOOTER_AIM]
SHOOTER_SHOT[3] = "..oFeSeKKKx.G"
SHOOTER_SHOT[2] = "..oFPPPPFo.G."

# --- Frozen Orb (14 x 14): a ball of ice with crystals circling it, floating ---------------------------------------
ORB_LIGHT, ORB_MID, ORB_DARK, ORB_CORE, ORB_OUT = rgb('#d6f6fc'), rgb('#8ad8f0'), rgb('#4aa6d4'), rgb('#ffffff'), rgb('#06223a')
CRYSTAL, CRYSTAL_DARK = rgb('#4aa6d4'), rgb('#1e5a86')       # darker than the orb: they show on the snow
ORB_SHADOW = (0, 0, 0, 70)
ORB_FRAMES = 5                   # (23.11) frames of the crystals' circle (a third of a turn = the next crystal)

def orb(frame):
    im = Image.new('RGBA', (14, 14))
    cx, cy, r = 6.5, 6.0, 3.9
    crystals = []
    for k in range(3):                                         # 3 crystals on a tilted ring, a third of a turn apart
        a = 2 * math.pi * (k / 3 + frame / (3 * ORB_FRAMES))
        crystals.append((cx + 5.6 * math.cos(a), cy + 3.2 * math.sin(a), math.sin(a) > 0))
    def crystal(x, y):
        """A little diamond of ice: white middle, lit top-left, dark bottom-right, a dark outline round it."""
        x, y = int(round(x)), int(round(y))
        shape = {(0, 0): ORB_CORE, (0, -1): ORB_LIGHT, (-1, 0): ORB_LIGHT, (1, 0): CRYSTAL, (0, 1): CRYSTAL_DARK}
        for (dx, dy) in ((0, -2), (-1, -1), (1, -1), (-2, 0), (2, 0), (-1, 1), (1, 1), (0, 2)):
            if 0 <= x + dx < 14 and 0 <= y + dy < 14 and (dx, dy) not in shape: im.putpixel((x + dx, y + dy), ORB_OUT)
        for (dx, dy), c in shape.items():
            if 0 <= x + dx < 14 and 0 <= y + dy < 14: im.putpixel((x + dx, y + dy), c)
    for x, y, front in crystals:
        if not front: crystal(x, y)                            # behind the orb
    for y in range(14):
        for x in range(14):
            d = math.hypot(x - cx, y - cy)
            if d <= r:
                lit = -(x - cx) - (y - cy)
                c = ORB_LIGHT if lit > 2.5 else ORB_MID if lit > -2 else ORB_DARK
                if d < 1.3: c = ORB_CORE
                im.putpixel((x, y), c)
            elif d <= r + 1:
                im.putpixel((x, y), ORB_OUT)
    for x, y, front in crystals:
        if front: crystal(x, y)                                # in front of it
    for x in range(4, 10):                                     # its shadow on the ground (it floats)
        im.putpixel((x, 13), ORB_SHADOW)
    return im

# --- Tundra Watcher (18 x 18): a hooded watcher - shoulders, sleeves, an ice staff, one big eye in the hood ------------
WATCHER = {"o": rgb('#0c1220'), "R": rgb('#3a4a6a'), "r": rgb('#2a3650'), "L": rgb('#56688c'), "F": rgb('#e8f2fa'),
           "h": rgb('#141a28'), "E": rgb('#6ff2ff'), "W": rgb('#e8fcff'), "p": rgb('#0c2a3a'), "s": rgb('#7a5a3a'),
           "C": rgb('#a8e6fa'), "c": rgb('#4aa6d4'), "H": rgb('#c8d8e8'), "b": rgb('#2a2030'), "#": SHADOW}
WATCHER_TOP = [
    "...............oo.",
    "......oooo....oCco",
    ".....oLRRRo...oCco",
    "....oLRRRRRo...oo.",
    "....oLhhhhRo...os.",
    "...oLhhEEEhRo..os.",
    "...oLhEWpEhRo..os.",
    "...oLhhEEEhRo..os.",
    "..ooRRhhhhRRoo.os.",
    ".oLRRFFFFFFRRRooHo",
    "oLRRRRRRRRRRRRRoHo",
    "oLRoLRRrRRRRoRRRos",
    "oLo.oLRrRRRRo.ooos",
    "oo..oLRrRRRro...os",
]
WATCHER_HEM = {                  # the robe's hem and feet: still / stepping
    "": ["....oLRrRRRro...os", "....oFFFFFFFo...os", "....obo..obo....oo", "...##########....."],
    "_walk1": ["....oLRrRRRRo...os", "....oFFFFFFFFo..os", "...obo....obo...oo", "...##########....."],
    "_walk2": ["....oLRrRRRro...os", "....oFFFFFFFo...os", ".....oboobo.....oo", "...##########....."],
}

SPRITES = {}
for tag in ("", "_walk1", "_walk2", "_walk3"):
    SPRITES[f"frost_wolf{tag}"] = (lambda t: lambda: wolf(t))(tag)
SPRITES["ice_shooter"] = lambda: draw(SHOOTER_BASE, SHOOTER)
SPRITES["ice_shooter_aim"] = lambda: draw(SHOOTER_AIM, SHOOTER)
SPRITES["ice_shooter_shoot"] = lambda: draw(SHOOTER_SHOT, SHOOTER)
SPRITES["frozen_orb"] = lambda: orb(0)
for k in range(ORB_FRAMES):
    SPRITES[f"frozen_orb_idle{k + 1}"] = (lambda f: lambda: orb(f))(k)
for tag, hem in WATCHER_HEM.items():
    SPRITES[f"tundra_watcher{tag}"] = (lambda h: lambda: draw(WATCHER_TOP + h, WATCHER))(hem)

if __name__ == "__main__":
    for name, make in SPRITES.items():
        im = make(); im.save(f"{sys.argv[1]}/{name}.png"); print(name, im.size)
