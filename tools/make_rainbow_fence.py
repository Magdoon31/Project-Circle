# Rainbow Fields fence (v1, chosen 23.11) + thick wall = a fenced flower bed. Pixel art 1:4.
import sys
from PIL import Image
PAL = {'.': (0,0,0,0), 'o': (53,39,46,255), 'L': (253,246,240,255), 'M': (227,211,219,255),
       'D': (179,156,174,255), 's': (0,0,0,70),
       'g': (106,153,65,255), 'G': (138,198,85,255), 'k': (75,131,64,255),          # bed: grass, light, leaf
       'r': (211,99,99,255), 'p': (200,89,165,255), 'y': (255,216,0,255), 'b': (127,178,232,255),
       'v': (179,82,148,255), 'w': (253,246,240,255), 'c': (255,216,0,255)}
V1 = {
 "wall_h": [
  "..oo......oo....",
  ".oLMo....oLMo...",
  ".oLMo....oLMo...",
  "ooLMooooooLMoooo",
  "MoLMoMMMMoLMoMMM",
  "ooLMooooooLMoooo",
  ".oLDo....oLDo...",
  "ooLDooooooLDoooo",
  "DoLDoDDDDoLDoDDD",
  "ooLDooooooLDoooo",
  ".oooo....oooo...",
  "..ssss....ssss..",
 ],
 "wall_h_end": [
  "oooooo..",
  "oLLLMo..",
  "oMMMDo..",
  "oLMMDooo",
  "oLMMDoMM",
  "oLMMDooo",
  "oLMMDo..",
  "oLMMDooo",
  "oLMMDoDD",
  "oLMMDooo",
  "oooooo..",
  ".ssssss.",
 ],
 "wall_v": ["....oLMos...", "....oLMos...", "....oLDos...", "....oDDos..."] * 4,
 "wall_v_top": [
  "...oooooo...",
  "...oLLLMo...",
  "...oMMMDos..",
  "...oMMMDos..",
  "...oooooos..",
  "....oLMos...",
 ],
 "wall_v_end": [
  "....oLMos...",
  "...oooooo...",
  "...oLLLMos..",
  "...oMMMDos..",
  "...oMMMDos..",
  "...oooooos..",
 ],
}

class Canvas:
    def __init__(self, w, h): self.w, self.h, self.px = w, h, [['.'] * w for _ in range(h)]
    def put(self, x, y, ch):
        if 0 <= x < self.w and 0 <= y < self.h: self.px[y][x] = ch
    def rows(self, x, y, block):
        for dy, row in enumerate(block):
            for dx, ch in enumerate(row):
                if ch != ' ': self.put(x + dx, y + dy, ch)
    def fill(self, x0, y0, x1, y1, ch):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): self.put(x, y, ch)
    def lines(self): return [''.join(r) for r in self.px]

FLOWER = {"r": ["  r  ", " rcr ", "  r  "]}
def flower(cv, x, y, petal):                    # a 3x3 plus: petals round a yellow middle (a white one in a yellow flower)
    mid = 'w' if petal == 'y' else 'c'
    cv.put(x, y - 1, petal); cv.put(x - 1, y, petal); cv.put(x + 1, y, petal); cv.put(x, y + 1, petal); cv.put(x, y, mid)

def bed(cv, x0, y0, x1, y1, flowers, dots):
    """Grass with leaves and flowers, seen from above."""
    cv.fill(x0, y0, x1, y1, 'g')
    for (x, y) in [(x0 + 1, y0 + 1), (x0 + 6, y0 + 4), (x0 + 11, y0 + 2), (x0 + 14, y0 + 5)]:
        cv.put(x, y, 'k')
    for (x, y) in [(x0 + 4, y0), (x0 + 9, y0 + 5), (x0 + 13, y0 + 1)]:
        cv.put(x, y, 'G')
    for (x, y, c) in flowers: flower(cv, x0 + x, y0 + y, c)
    for (x, y, c) in dots: cv.put(x0 + x, y0 + y, c)

# --- thick horizontal: back rail, flower bed, the v1 fence in front --------------------------------
def thick_h(flowers=((3, 2, 'r'), (11, 4, 'b'), (7, 6, 'y')), dots=((14, 1, 'p'), (1, 6, 'v'), (9, 1, 'w'))):
    cv = Canvas(16, 22)
    cv.fill(0, 0, 15, 0, 'o'); cv.fill(0, 1, 15, 1, 'M'); cv.fill(0, 2, 15, 2, 'o')     # the back rail
    bed(cv, 0, 3, 15, 10, flowers=list(flowers), dots=list(dots))
    cv.rows(0, 10, V1["wall_h"])                                                    # front fence + its shadow
    return cv.lines()

def thick_h_end():
    cv = Canvas(6, 22)
    cv.rows(0, 0, ["oooooo", "oLLLMo", "oMMMDo"])                                   # back corner post
    for y in range(3, 10): cv.rows(0, y, [".oLMog"])                                # side fence edge-on, the bed
    cv.rows(0, 10, ["oooooo", "oLLLMo", "oMMMDo"] + ["oLMMDo"] * 7 + ["oooooo", ".sssss"])   # front corner post
    return cv.lines()

# --- thick vertical: two fences edge-on with the bed between -------------------------------------
BAND = ["oLMo", "oLMo", "oLDo", "oDDo"]
def thick_v(flowers=((3, 2, 'p'), (8, 7, 'r'), (4, 12, 'y')), dots=((10, 3, 'b'), (1, 9, 'w'), (9, 13, 'v'))):
    cv = Canvas(22, 16)
    bed(cv, 5, 0, 16, 15, flowers=list(flowers), dots=list(dots))
    for y in range(16):
        cv.rows(1, y, [BAND[y % 4]]); cv.rows(17, y, [BAND[y % 4]]); cv.put(21, y, 's')
    return cv.lines()

def thick_v_top():
    cv = Canvas(22, 6)
    cv.rows(1, 0, ["oooooo" + "o" * 10 + "oooooo"])
    cv.rows(1, 1, ["oLLLMo" + "M" * 10 + "oLLLMo"])
    cv.rows(1, 2, ["oMMMDo" + "o" * 10 + "oMMMDo"]); cv.put(21, 2, 's')
    bed(cv, 5, 3, 16, 5, flowers=[], dots=[(3, 1, 'r'), (9, 0, 'y')])
    for y in range(3, 6):
        cv.rows(1, y, [BAND[y % 4]]); cv.rows(17, y, [BAND[y % 4]]); cv.put(21, y, 's')
    return cv.lines()

def thick_v_end():
    cv = Canvas(22, 12)
    for x in (7, 12):                                                               # 2 pickets between the corner posts
        cv.rows(x, 0, [" oo ", "oLMo", "oLMo", "oLMo", "oLMo", "oLMo", "oLDo", "oLDo", "oLDo", "oLDo", "oooo", " ssss"])
    for y in (3, 5, 7, 9): cv.fill(5, y, 16, y, 'o') if False else None
    for y0 in (3, 7):                                                               # the rails between them
        for x in list(range(5, 7)) + list(range(11, 12)) + list(range(16, 17)):
            cv.put(x, y0, 'o'); cv.put(x, y0 + 1, 'M' if y0 == 3 else 'D'); cv.put(x, y0 + 2, 'o')
    for x in (0, 16):                                                               # the corner posts
        cv.rows(x + 1 if x == 0 else x + 1, 0, ["oooooo"[:4] + "", ])
    cv.rows(1, 0, ["oooo", "oLMo", "oLMo"] + ["oLMo"] * 7 + ["oooo", " sss"])
    cv.rows(17, 0, ["oooo", "oLMo", "oLMo"] + ["oLMo"] * 7 + ["oooo", " sss"])
    return cv.lines()

out = sys.argv[1]
SPRITES = {f"rainbow_fields_{k}": v for k, v in V1.items()}
SPRITES.update({"rainbow_fields_wall_thick_h": thick_h(), "rainbow_fields_wall_thick_h_end": thick_h_end(),
                "rainbow_fields_wall_thick_h_2": thick_h(((5, 4, 'p'), (12, 2, 'y')), ((2, 1, 'b'), (9, 6, 'r'), (14, 5, 'w'))),
                "rainbow_fields_wall_thick_v": thick_v(),
                "rainbow_fields_wall_thick_v_2": thick_v(((8, 3, 'b'), (3, 9, 'y'), (8, 13, 'p')), ((2, 1, 'r'), (10, 7, 'w'), (2, 14, 'v'))), "rainbow_fields_wall_thick_v_top": thick_v_top(),
                "rainbow_fields_wall_thick_v_end": thick_v_end()})
for name, rows in SPRITES.items():
    w = len(rows[0]); assert all(len(r) == w for r in rows), name
    im = Image.new('RGBA', (w, len(rows)))
    for y, r in enumerate(rows):
        for x, ch in enumerate(r): im.putpixel((x, y), PAL[ch])
    im.save(f"{out}/{name}.png"); print(name, im.size)
