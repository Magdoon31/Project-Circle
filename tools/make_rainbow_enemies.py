# Rainbow Fields enemies (pixel art 1:4, 23.11): Flower Spitter (+ _shoot: its mouth wide open as it spits) and
# Rainbow Guard (+ _walk1, _walk2: steps). Drawn from character maps; outline = a very dark shade of each part's
# colour; the shadow under them is black, half-transparent (like Filip's slimes). They face RIGHT (the game mirrors).
# (rainbow_slime is Filip's.) Run: py tools/make_rainbow_enemies.py <folder>
import sys
from PIL import Image

def rgb(h, a=255): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) + (a,)
SHADOW = (0, 0, 0, 90)

SPITTER_COLOURS = {
    "o": rgb('#3a0a22'), "P": rgb('#ff7fbf'), "L": rgb('#ffb3d9'), "d": rgb('#d14d8f'),        # petals (pink)
    "m": rgb('#4a0a1e'), "t": rgb('#fff4f8'), "s": rgb('#ff7fbf'),                             # mouth, teeth, seed
    "G": rgb('#4f9a4a'), "l": rgb('#7cc86a'), "e": rgb('#2f6b38'), "q": rgb('#0a240e'),        # stem, leaves
    "#": SHADOW,
}
SPITTER = [
    "...oo..oo...",
    "..oLPooLPo..",
    ".oLPPddPPdo.",
    "oLPdttttdPdo",
    "oPPmmmmmmPdo",
    "oLPdmmmmdPdo",
    ".oPPddddPdo.",
    "..oPdoodPo..",
    ".....qGq....",
    "..qq.qGq.qq.",
    ".qellGGGlleq",
    "..########..",
]
SPITTER_SHOOT = [                 # the mouth wide open, a seed in it, the petals pushed out
    "..oo....oo..",
    ".oLPoooLPPo.",
    "oLPdttttdPdo",
    "oPmmmmmmmmdo",
    "oPmmmssmmmdo",
    "oPmmmssmmmdo",
    "oLPdmmmmdPdo",
    ".oPPdoodPdo.",
    ".....qGq....",
    "..qq.qGq.qq.",
    ".qellGGGlleq",
    "..########..",
]

GUARD_COLOURS = {
    "o": rgb('#1c1f2c'), "W": rgb('#f4f6fa'), "S": rgb('#c4c8d4'), "D": rgb('#8a90a0'),        # armour
    "V": rgb('#2a2e3e'), "v": rgb('#6fd8ff'),                                                  # visor + its glint
    "r": rgb('#ff4d4d'), "n": rgb('#ff9a3c'), "y": rgb('#ffe14d'), "g": rgb('#5fd35f'),
    "b": rgb('#4da6ff'), "p": rgb('#a86bff'),                                                  # the rainbow
    "K": rgb('#6a6e78'), "k": rgb('#3a3c44'), "B": rgb('#8a5a36'), "x": rgb('#1a120a'),        # the shotgun
    "#": SHADOW,
}
GUARD_TOP = [
    "......rnygb....",
    ".....oWWWWWo...",
    "....oWSSSSSWo..",
    "....oSVvVVVSo..",
    "....oSSSSSSDo..",
    ".....oDDDDDo...",
    "...oWWWWWWWWo..",
    "...oWrnygbpWWo.",
    "...oSWWSSoBBKKK",
    "...oDSSSDoxkkkx",
    "....oDDDDo.....",
]
GUARD_LEGS = {
    "": ["....oSo.oSo....", "....oSo.oSo....", "....ooo.ooo....", "...#########..."],
    "_walk1": ["...oSo..oSo....", "...oSo...oSo...", "...ooo...ooo...", "..##########..."],
    "_walk2": ["....oSooSo.....", ".....oSSo......", ".....oooo......", "...#########..."],
}

def draw(rows, colours):
    h, w = len(rows), len(rows[0])
    im = Image.new('RGBA', (w, h))
    for y, row in enumerate(rows):
        assert len(row) == w, (y, row)
        for x, ch in enumerate(row):
            if ch != ".": im.putpixel((x, y), colours[ch])
    return im

SPRITES = {
    "flower_spitter": lambda: draw(SPITTER, SPITTER_COLOURS),
    "flower_spitter_shoot": lambda: draw(SPITTER_SHOOT, SPITTER_COLOURS),
}
for tag, legs in GUARD_LEGS.items():
    SPRITES[f"rainbow_guard{tag}"] = (lambda l: lambda: draw(GUARD_TOP + l, GUARD_COLOURS))(legs)

if __name__ == "__main__":
    for name, make in SPRITES.items():
        im = make(); im.save(f"{sys.argv[1]}/{name}.png"); print(name, im.size)
