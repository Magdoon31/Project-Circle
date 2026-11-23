# Sugarwood Grove enemies (pixel art 1:4, 23.11), from character maps; outline = a very dark shade of each part's
# colour, a black half-transparent shadow under them; they face RIGHT (the game mirrors). Poses (sprites.py):
#   gum_goblin   + _walk1, _walk2, _shoot (the gum balloon pops)
#   candy_shroom + _walk1, _walk2, _spin1.._spin3 (the cap turns while it sprays spores)
#   toffee_runner + _walk1, _walk2 (running)
#   sugar_caster + _shoot (throwing its sugar bomb)
#   shroom_guard + _shoot (its cap lifts as it sprays)
# Run: py tools/make_sugarwood_enemies.py <folder>
import sys
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

# --- Gum Goblin (13 x 13): pink chewing gum, a gum balloon at its mouth -----------------------------------------
GOBLIN = {"o": rgb('#3a0624'), "P": rgb('#ff4fae'), "L": rgb('#ff9ad0'), "d": rgb('#c02a7c'), "e": rgb('#2a0614'),
          "m": rgb('#7a1040'), "b": rgb('#ffc8e4'), "W": rgb('#ffffff'), "#": SHADOW}
GOBLIN_TOP = [
    ".............",
    "...o....o....",
    "...odo.odo...",
    "...oPPPPo....",
    "..oPLPPPPooo.",
    "..oPLPePeobbo",
    "..oPPPPPmbWbo",
    "..odPPPPmbbbo",
    "...oPdPPoooo.",
    "...oPPPPo....",
]
GOBLIN_SHOOT_TOP = [
    ".............",
    "...o....o....",
    "...odo.odo...",
    "...oPPPPo....",
    "..oPLPPPPo...",
    "..oPLPePeo.o.",
    "..oPPPPPmmobo",
    "..odPPPPmo.o.",
    "...oPdPPo....",
    "...oPPPPo....",
]
GOBLIN_LEGS = {"": ["...oPooPo....", "...oo..oo....", "..########..."],
               "_walk1": ["..oPo..oPo...", "..oo....oo...", ".##########.."],
               "_walk2": ["....oPPo.....", "....oooo.....", "..########..."]}

# --- Candy Shroom (12 x 12): a red candy cap with icing dots on a cream stem (red: stands out on the pink floor) ------------------------------------------
SHROOM = {"o": rgb('#3a0410'), "C": rgb('#f2304e'), "L": rgb('#ff7088'), "d": rgb('#b0182f'), "D": rgb('#fff6fb'),
          "q": rgb('#3a2a14'), "S": rgb('#fff0d8'), "s": rgb('#e0c8a8'), "e": rgb('#2a1a10'), "#": SHADOW}
CAP = [
    "....oooo....",
    "..ooLLCCoo..",
    ".oLLCCCCCCo.",
    "oLCCCCCCCCdo",
    "oCCCCCCCCCdo",
    "oCCCCCCCCddo",
    ".oddddddddo.",
]
def cap(shift):
    """The cap with its icing dots; shift moves the dots right (the cap turning): a pattern every 6 px."""
    rows = [list(r) for r in CAP]
    for y in range(1, 6):
        for x in range(12):
            if rows[y][x] in "CL" and (x + 3 * y + shift) % 6 == 0: rows[y][x] = "D"
    return ["".join(r) for r in rows]
SHROOM_STEM = ["...qSSSSq...", "...qSeSeq...", "...qsSSsq..."]
SHROOM_LEGS = {"": ["...qSqqSq...", "..########.."],
               "_walk1": ["..qSq..qSq..", ".##########."],
               "_walk2": ["....qSSq....", "..########.."]}

# --- Toffee Runner (9 x 9): a slim brown toffee critter, running ---------------------------------------------------
TOFFEE = {"o": rgb('#2a1404'), "T": rgb('#c8803a'), "L": rgb('#e8a85a'), "d": rgb('#8a5020'), "e": rgb('#1a0a02'),
          "w": rgb('#fff4e0'), "B": rgb('#c8803a', 120), "#": SHADOW}
TOFFEE_TOP = [
    "...ooo...",
    "..oLTTo..",
    "..oTwew..",
    "..oTTTo..",
    "..oLTTdo.",
    "..oTTTdo.",
]
TOFFEE_LEGS = {"": ["...o.o...", "...o.o...", "..#####.."],
               "_walk1": ["..o...o..", ".BoB.oB..", ".#######."],
               "_walk2": ["...oo....", "..BooB...", "..#####.."]}

# --- Sugar Caster (13 x 13): a mage in a white-and-light-blue icing robe with a sugar bomb -------------------------
CASTER = {"o": rgb('#14243a'), "W": rgb('#f8fbff'), "B": rgb('#a8d8f8'), "b": rgb('#6aa8d8'), "f": rgb('#2a3a5a'),
          "e": rgb('#8ff4ff'), "x": rgb('#3a1430'), "s": rgb('#ffffff'), "p": rgb('#ff8fc8'), "#": SHADOW}
CASTER_ROWS = [
    ".....ooo.....",
    "....oWWWo....",
    "...oWBBBWo...",
    "...oWfefeo...",
    "...oWffffo...",
    "...oBWWWBo...",
    "..oBWWBWWBox.",
    "..oBWWBWWoxsx",
    "..oBWWBWWoxpx",
    "..obWWBWWbox.",
    "..obbbbbbbo..",
    "...ooooooo...",
    "..#########..",
]
CASTER_THROW = [                 # its arm up, the bomb over its head
    ".....ooo.xxx.",
    "....oWWWoxspx",
    "...oWBBBWoxx.",
    "...oWfefeoo..",
    "...oWffffoWo.",
    "...oBWWWBWo..",
    "..oBWWBWWBo..",
    "..oBWWBWWBo..",
    "..oBWWBWWBo..",
    "..obWWBWWbo..",
    "..obbbbbbbo..",
    "...ooooooo...",
    "..#########..",
]

# --- Shroom Guard (15 x 15): Shroom Mother's big pink guard with a candy shield --------------------------------------
GUARD = {"o": rgb('#3a0410'), "C": rgb('#f2304e'), "L": rgb('#ff7088'), "d": rgb('#b0182f'), "D": rgb('#fff6fb'),
         "q": rgb('#3a2a14'), "S": rgb('#fff0d8'), "s": rgb('#e0c8a8'), "e": rgb('#2a1a10'),
         "h": rgb('#7a4a2a'), "H": rgb('#c8a060'), "R": rgb('#ff4d6d'), "w": rgb('#ffffff'), "g": rgb('#d8f0c8', 200),
         "#": SHADOW}
GUARD_CAP = [
    ".....ooooo.....",
    "...ooLLDCCoo...",
    "..oLLCCCCDCCo..",
    ".oLCDCCCCCCCdo.",
    "oLCCCCCDCCCCCdo",
    "oCCCDCCCCCDCddo",
    ".oddddddddddoo.",
]
GUARD_BODY = [
    "....qSSSSSqoo..",
    "....qSeSSeohRo.",
    "....qSSSSSohwRo",
    "...qsSSSSSohRwo",
    "...qSSSSSSqohRo",
    "...qssSSssq.oo.",
    "...qSq...qSq...",
    "..###########..",
]
GUARD_PUFFS = ["..g.........g..", "g.............g"]          # spores puffing as it sprays

SPRITES = {}
for tag, legs in GOBLIN_LEGS.items():
    SPRITES[f"gum_goblin{tag}"] = (lambda l: lambda: draw(GOBLIN_TOP + l, GOBLIN))(legs)
SPRITES["gum_goblin_shoot"] = lambda: draw(GOBLIN_SHOOT_TOP + GOBLIN_LEGS[""], GOBLIN)
for tag, legs in SHROOM_LEGS.items():
    SPRITES[f"candy_shroom{tag}"] = (lambda l: lambda: draw(cap(0) + SHROOM_STEM + l, SHROOM))(legs)
for k in range(3):
    SPRITES[f"candy_shroom_spin{k + 1}"] = (lambda s: lambda: draw(cap(s) + SHROOM_STEM + SHROOM_LEGS[""], SHROOM))(2 * k + 2)
for tag, legs in TOFFEE_LEGS.items():
    SPRITES[f"toffee_runner{tag}"] = (lambda l: lambda: draw(TOFFEE_TOP + l, TOFFEE))(legs)
SPRITES["sugar_caster"] = lambda: draw(CASTER_ROWS, CASTER)
SPRITES["sugar_caster_shoot"] = lambda: draw(CASTER_THROW, CASTER)
SPRITES["shroom_guard"] = lambda: draw(GUARD_CAP + GUARD_BODY, GUARD)
SPRITES["shroom_guard_shoot"] = lambda: draw(GUARD_PUFFS[:1] + GUARD_CAP + GUARD_BODY[:-2] + GUARD_BODY[-1:], GUARD)

if __name__ == "__main__":
    for name, make in SPRITES.items():
        im = make(); im.save(f"{sys.argv[1]}/{name}.png"); print(name, im.size)
