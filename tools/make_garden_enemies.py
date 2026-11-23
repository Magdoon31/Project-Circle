# Underground Garden enemies (pixel art 1:4, 23.11). Outline = a very dark shade of each part's colour; a black
# half-transparent shadow under them (fliers float: their shadow lies apart); they face RIGHT (the game mirrors).
# Poses (sprites.py): pixie (27 x 21) / rainbow_pixie (33 x 21) _idle1.._idle4 (a glowing ball like Terraria's pixie, its wing
# flapping; the rainbow one changes colour), inferno / frost / toxic_flower _shoot (mouth / petals open) + _walk1/_walk2 (root steps), poison_skeleton
# _aim (bow drawn, a red arrow) + _shoot (string let go), firefly_queen _idle1.._idle4 (wings, the glow pulsing).
# Run: py tools/make_garden_enemies.py <folder>
import sys
from PIL import Image

def rgb(h, a=255): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) + (a,)
SHADOW = (0, 0, 0, 90)
FLY_SHADOW = (0, 0, 0, 70)

def draw(rows, colours, size=None):
    h, w = len(rows), len(rows[0])
    im = Image.new('RGBA', size or (w, h))
    for y, row in enumerate(rows):
        assert len(row) == w, (y, row, len(row), w)
        for x, ch in enumerate(row):
            if ch != ".": im.putpixel((x, y), colours[ch])
    return im

def glow_round(im, colour):
    """A soft glow: every empty pixel touching the picture (shadow aside) gets `colour`, under the picture."""
    w, h = im.size
    out = Image.new('RGBA', im.size)
    for y in range(h):
        for x in range(w):
            if im.getpixel((x, y))[3]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and im.getpixel((nx, ny))[3] == 255:
                    out.putpixel((x, y), colour)
                    break
    return Image.alpha_composite(out, im)

def overlay(base, rows, colours):
    return Image.alpha_composite(base, draw(rows, colours))

# --- Pixie (27 x 21) / Rainbow Pixie (33 x 21) (23.11 Filip: like Terraria's pixie): a glowing ball with a little wing behind ----
# Drawn from Filip's picture (it faced left - here mirrored to face right). The ball: a glow ring round an orange ball
# with a white cross in the middle; the wing flaps (sheared up / down). Rainbow Pixie: bigger wing, the ball changes
# colour every frame (orange, pink, blue, green).
PIXIE_BALL = [                   # 15 x 15, symmetric; a / b = the glow rings
    "....aaaaaaa....",
    "...aabbbbbaa...",
    "..aab.....baa..",
    ".abb.eeeee.bba.",
    ".ab.eehhhee.ba.",
    "ab.eehiiihee.ba",
    "ab.ehiijiihe.ba",
    "ab.ehijjjihe.ba",
    "ab.ehiijiihe.ba",
    "ab.eehiiihee.ba",
    ".ab.eehhhee.ba.",
    ".abb.eeeee.bba.",
    "..aab.....baa..",
    "...aabbbbbaa...",
    "....aaaaaaa....",
]
PIXIE_WING = [                   # Filip's wing, mirrored: rows 1..7 of the ball, x 0..9 (its root over the ball's edge)
    ".....ccc..",
    ".cccccddc.",
    "cgffddccdc",
    "cgffffddcf",
    ".cgggffff.",
    "..cccgggg.",
    ".....cccc.",
]
RAINBOW_STRETCH = 13 / 10        # the Rainbow Pixie's wing is this much longer ...
RAINBOW_TINT = {3: {"f": "r"}, 4: {"f": "V"}, 5: {"f": "B", "g": "n"}, 6: {"g": "n"}}   # ... and tinted (wing row: swaps)
PIXIE_COLOURS = {"a": (255, 214, 120, 70), "b": (255, 170, 90, 120),       # glow (Filip's rings were dark - on the dark
                 "c": rgb('#303030', 212), "d": rgb('#c5d4d4', 212),       # floor they vanished, so they glow here)
                 "f": rgb('#a6b6cb', 212), "g": rgb('#8c9bbf', 212), "r": (255, 150, 180, 212), "V": (200, 150, 255, 212),
                 "B": (120, 200, 255, 212), "n": (140, 230, 130, 212),
                 "e": rgb('#fd8f4d'), "h": rgb('#fdc621'), "i": rgb('#fedd7c'), "j": rgb('#fffaeb'), "#": FLY_SHADOW}
RAINBOW_BALLS = [                # e / h / i per frame (j stays white)
    (rgb('#fd8f4d'), rgb('#fdc621'), rgb('#fedd7c')),
    (rgb('#f04a9a'), rgb('#ff8ad0'), rgb('#ffc8ec')),
    (rgb('#3a8af0'), rgb('#6ac8ff'), rgb('#c0ecff')),
    (rgb('#3ac84a'), rgb('#8af06a'), rgb('#d0ffb8')),
]
PIXIE_TOP = 3                    # room above for the raised wing
WING_ROOT = 9                    # the wing's root column (over the ball's edge)
WING_SHEAR = (-0.45, 0.0, 0.4, 0.0)   # per frame: up, middle, down, middle (rows moved per px away from the root)

def rainbow_wing():
    width = round(len(PIXIE_WING[0]) * RAINBOW_STRETCH)
    rows = []
    for y, row in enumerate(PIXIE_WING):
        line = "".join(row[min(len(row) - 1, int(n / RAINBOW_STRETCH))] for n in range(width))
        rows.append("".join(RAINBOW_TINT.get(y + 1, {}).get(ch, ch) for ch in line))
    return rows

def pixie(frame, rainbow=False):
    colours = dict(PIXIE_COLOURS)
    wing_rows = PIXIE_WING
    if rainbow:
        colours["e"], colours["h"], colours["i"] = RAINBOW_BALLS[frame]
        wing_rows = rainbow_wing()
    extra = len(wing_rows[0]) - len(PIXIE_WING[0])             # a longer wing moves the ball right
    ball_x = 6 + extra
    size = (2 * ball_x + len(PIXIE_BALL[0]), 2 * PIXIE_TOP + len(PIXIE_BALL))   # (23.11) the ball in the middle:
    # the game draws pixies round their middle, so the ball sits on the hitbox (sprites.CENTRED)
    root = WING_ROOT + extra
    im = Image.new('RGBA', size)
    for x in range(ball_x + 2, ball_x + 13):                   # its shadow (it floats)
        im.putpixel((x, size[1] - 1), colours["#"])
    im.alpha_composite(draw(PIXIE_BALL, colours), (ball_x, PIXIE_TOP))
    wing = Image.new('RGBA', size)
    for y, row in enumerate(wing_rows):
        for x, ch in enumerate(row):
            if ch == ".": continue
            wy = PIXIE_TOP + 1 + y + round((root - x) * WING_SHEAR[frame])
            if 0 <= wy < size[1]:
                wing.putpixel((x, wy), colours[ch])
    return Image.alpha_composite(im, wing)

WING_ORDER = (0, 1, 2, 1)        # one flap = up, middle, down, middle (the Firefly Queen)


# --- the three flowers (15 x 15): each its own head on a stem with leaves, walking on roots -----------------------------
STEM = {"o": rgb('#0e1a0a'), "G": rgb('#6ad84a'), "L": rgb('#3a9a2a'), "R": rgb('#6a4a2a'), "#": SHADOW}
STEM_ROWS = [
    "..oo..oGo..oo..",
    ".oLLo.oGo.oLLo.",
    "..oLLooGooLLo..",
    "....oRRRRRo....",
]
ROOTS = {"": "....oRo.oRo....", "_walk1": "...oRo...oRo...", "_walk2": ".....oRoRo....."}
FLOWER_SHADOW = "...#########..."

INFERNO = dict(STEM, o=rgb('#3a0a06'), r=rgb('#d8281a'), O=rgb('#ff7a1a'), Y=rgb('#ffd23a'), m=rgb('#2a0606'),
               W=rgb('#fff6d0'))
INFERNO_HEAD = [                 # petals like flames round a face with a mouth
    "..o....o....o..",
    ".oYo..oYo..oYo.",
    ".oOYooOYOooYOo.",
    "oOrOrooooorOrOo",
    "orOroOYYYOorOro",
    "orOroYmmmYorOro",
    "orOroOYYYOorOro",
    ".orOrooooorOro.",
    "..oorrrrrrroo..",
]
INFERNO_SHOT = list(INFERNO_HEAD)
INFERNO_SHOT[0:2] = [".oYo..oYo..oYo.", "oYOYooYOYooYOYo"]
INFERNO_SHOT[4:7] = ["orOroOmmmOorOro", "orOromYWYmorOro", "orOroOmmmOorOro"]

FROST = dict(STEM, o=rgb('#0c2a3a'), W=rgb('#f4fcff'), C=rgb('#a8e6fa'), B=rgb('#4aa6d4'), E=rgb('#6ff2ff'))
FROST_HEAD = [                   # a star of icy pointed petals round a glowing blue heart
    ".......o.......",
    "......oWo......",
    "..o...oWo...o..",
    "..oWo.oCo.oWo..",
    "...oWCoCoCWo...",
    ".oooCCBBBCCooo.",
    "oWWCCBEEEBCCWWo",
    ".oooCCBBBCCooo.",
    "...oWCoCoCWo...",
]
FROST_SHOT = list(FROST_HEAD)
FROST_SHOT[0:4] = ["..o....o....o..", "..oWo.oWo.oWo..", "...oWooWooWo...", "....oCoCoCo...."]
FROST_SHOT[5:8] = [".oooCCEEECCooo.", "oWWCCEWWWECCWWo", ".oooCCEEECCooo."]

TOXIC = dict(STEM, o=rgb('#1a0810'), P=rgb('#8a2a4a'), p=rgb('#5a1a32'), S=rgb('#d8e85a'), A=rgb('#a8ff3a'),
             a=rgb('#4aa82a'), W=rgb('#f0ffd0'))
TOXIC_HEAD = [                   # (23.11, v2) a rafflesia: fat dark-red spotted petals round a pool of bubbling acid
    "....ooooooo....",
    "..ooPPSPPPPoo..",
    ".oPPPoooooPPSo.",
    "oPSPoaAAAaoPPPo",
    "oPPoaAAWAAaoPSo",
    "oPPoaAAAAAaoPPo",
    "oSPPoaaaaaoPSPo",
    ".oPPPoooooPPPo.",
    "..ooPSPoPPSoo..",
]
TOXIC_SHOT = list(TOXIC_HEAD)    # the acid spurts up out of the middle
TOXIC_SHOT[0:2] = ["....oAoAoAo....", "..ooPAPAPAPoo.."]
TOXIC_SHOT[3:5] = ["oPSPoaAWAaoPPPo", "oPPoaAWAWAaoPSo"]

def flower(head, colours, roots=""):
    return draw(head + STEM_ROWS + [ROOTS[roots], FLOWER_SHADOW], colours)

# --- Poison Skeleton (17 x 16): a dark skeleton with glowing poison stains and a bow ----------------------------------------------
SKELETON = {"o": rgb('#060a06'), "B": rgb('#6e7564'), "b": rgb('#454a3e'), "e": rgb('#0a0a0a'), "E": rgb('#7aff4a'),   # (23.11, v2) dark bones
            "P": rgb('#7aff4a'), "p": rgb('#3ac82a'), "K": rgb('#7a4a22'), "k": rgb('#3a2010'), "s": rgb('#d8d8d0'),
            "R": rgb('#e0342a'), "r": rgb('#ff8a7a'), "#": SHADOW}
SKELETON_BODY = [
    "....oooooo.......",
    "...oBBBBBBo......",
    "..oBBPBBBBBo.....",
    "..oBeEBBBeEo.....",
    "..oBBBBbBBBo.....",
    "...oBoBoBoo......",
    "....oooooo.......",
    "..oBBBBBBBo......",
    ".oBoBoPoBoBo.....",
    ".oBoBpBoBoBBBBo..",
    ".oBoPoBoBoo......",
    "..oBBPBBBo.......",
    "...oBo.oBo.......",
    "...oPo.oBo.......",
    "..obbo.obbo......",
    "..#########......",
]
BOW_X = {4: 13, 5: 14, 6: 14, 7: 15, 8: 15, 9: 15, 10: 15, 11: 15, 12: 14, 13: 14, 14: 13}   # the bow's curve
BOW_GRIP = 9                     # the row the hand holds it at
DRAW_BACK = 10                   # where the drawn string's middle goes (aiming)

def skeleton(pose=""):
    im = Image.new('RGBA', (17, 16))
    string = {}                  # row -> x of the string
    for row in BOW_X:
        if pose == "_aim":       # pulled back to DRAW_BACK in the middle, straight to the tips
            t = abs(row - BOW_GRIP) / (max(BOW_X) - BOW_GRIP)
            string[row] = round(DRAW_BACK + (13 - DRAW_BACK) * t)
        elif pose == "_shoot":   # let go: it still shakes forward a bit
            string[row] = 14 if abs(row - BOW_GRIP) <= 1 else 13
        else:
            string[row] = 13
    for row, x in string.items():
        im.putpixel((x, row), SKELETON["s"])
    for row, x in BOW_X.items():
        im.putpixel((x, row), SKELETON["K"])
        if row in (min(BOW_X), max(BOW_X)):
            im.putpixel((x, row), SKELETON["k"])
    body = draw(SKELETON_BODY, SKELETON)
    im = Image.alpha_composite(im, body)
    im.putpixel((15, BOW_GRIP), SKELETON["k"])                 # the grip under the hand
    if pose == "_aim":                                          # a red arrow on the string
        for x in range(DRAW_BACK, 16):
            im.putpixel((x, BOW_GRIP), SKELETON["R"])
        im.putpixel((16, BOW_GRIP), SKELETON["r"])
        im.putpixel((DRAW_BACK, BOW_GRIP - 1), SKELETON["R"])  # the fletching
        im.putpixel((DRAW_BACK, BOW_GRIP + 1), SKELETON["R"])
    return im

# --- Firefly Queen (15 x 15): a big firefly with a crown and a glowing tail, floating ----------------------------------
FIREFLY = {"o": rgb('#140c10'), "D": rgb('#4a3a5a'), "d": rgb('#2a2036'), "Y": rgb('#fff27a'), "y": rgb('#ffc83a'),
           "H": rgb('#ffffff'), "C": rgb('#ffd23a'), "R": rgb('#e0342a'), "E": rgb('#ff6a3a'),
           "W": (220, 240, 255, 140), "w": (255, 255, 255, 210), "#": FLY_SHADOW}
FIREFLY_GLOW = (255, 240, 120, 90)
FIREFLY_BODY = [
    "...............",
    "...............",
    "...............",
    "...............",
    "..........C.C..",
    ".........oCRCo.",
    "..oooo..ooDDDDo",
    ".oYYYYoodDDDEDo",
    "oYYyYYYodDDDDo.",
    "oYyYYyYodDDDoo.",
    ".oYYYYoo.oddo..",
    "..oooo..o.o.o..",
    "...............",
    "...............",
    "....#######....",
]
FIREFLY_WINGS = [                # up, middle, down (then middle again)
    ["....ww.........", "...wWWw........", "...wWWWw.......", "....wWWWw......", ".....wWWw......",
     "......wWw......"],
    ["...............", "...............", "...............", "..wwwwww.......", ".wWWWWWWw......",
     "..wWWWWWw......"],
    ["...............", "...............", "...............", "...............", "...wwwww.......",
     ".wWWWWWw.......", "wWWWWWw........", ".wwww.........."],
]
BRIGHT_FRAMES = (0, 2)           # the tail glows brighter (white heart + a glow) every other frame

def firefly(frame):
    rows = list(FIREFLY_BODY)
    if frame in BRIGHT_FRAMES:
        rows[8] = rows[8][:3] + "H" + rows[8][4:]
        rows[9] = rows[9][:3] + "HH" + rows[9][5:]
    body = draw(rows, FIREFLY)
    if frame in BRIGHT_FRAMES:   # the glow only round the tail
        tail = body.crop((0, 0, 7, 15))
        tail = glow_round(tail, FIREFLY_GLOW)
        body.paste(tail, (0, 0))
    wings = FIREFLY_WINGS[WING_ORDER[frame]]
    wings = wings + ["." * 15] * (15 - len(wings))
    return overlay(body, wings, FIREFLY)

SPRITES = {}
for k in range(4):
    SPRITES[f"pixie_idle{k + 1}"] = (lambda f: lambda: pixie(f))(k)
    SPRITES[f"rainbow_pixie_idle{k + 1}"] = (lambda f: lambda: pixie(f, True))(k)
    SPRITES[f"firefly_queen_idle{k + 1}"] = (lambda f: lambda: firefly(f))(k)
SPRITES["pixie"] = lambda: pixie(1)
SPRITES["rainbow_pixie"] = lambda: pixie(1, True)
SPRITES["firefly_queen"] = lambda: firefly(1)
for name, head, shot, colours in (("inferno_flower", INFERNO_HEAD, INFERNO_SHOT, INFERNO),
                                  ("frost_flower", FROST_HEAD, FROST_SHOT, FROST),
                                  ("toxic_flower", TOXIC_HEAD, TOXIC_SHOT, TOXIC)):
    for tag in ROOTS:
        SPRITES[f"{name}{tag}"] = (lambda h, c, t: lambda: flower(h, c, t))(head, colours, tag)
    SPRITES[f"{name}_shoot"] = (lambda h, c: lambda: flower(h, c))(shot, colours)
for tag in ("", "_aim", "_shoot"):
    SPRITES[f"poison_skeleton{tag}"] = (lambda t: lambda: skeleton(t))(tag)

if __name__ == "__main__":
    for name, make in SPRITES.items():
        im = make(); im.save(f"{sys.argv[1]}/{name}.png"); print(name, im.size)
