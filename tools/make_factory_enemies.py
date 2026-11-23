# Toy Factory enemies + the Assembly Line's 3 machines (pixel art 1:4, 23.11). Outline = a very dark shade of each
# part's colour; a black half-transparent shadow under the walkers; they face RIGHT (the game mirrors).
# Poses (sprites.py): toy_soldier _walk1/_walk2/_shoot, scrap_beetle _walk1/_walk2 (flying: its wings flap),
# robo-tesla / robo-bomber / portable_factory _shoot, bomb_crate _idle1.._idle3 (its fuse flickers, always).
# Run: py tools/make_factory_enemies.py <folder>
import sys
from PIL import Image

def rgb(h, a=255): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) + (a,)
SHADOW = (0, 0, 0, 90)
METAL = {"m": rgb('#8a8f9c'), "M": rgb('#5e6270'), "n": rgb('#3e414c'), "q": rgb('#121318'), "w": rgb('#b4b8c4')}

def draw(rows, colours):
    h, w = len(rows), len(rows[0])
    im = Image.new('RGBA', (w, h))
    for y, row in enumerate(rows):
        assert len(row) == w, (y, row, len(row), w)
        for x, ch in enumerate(row):
            if ch != ".": im.putpixel((x, y), colours[ch])
    return im

# --- Toy Soldier (10 x 10): a tin soldier, a wind-up key on its back, a rifle ---------------------------------------
SOLDIER = {"o": rgb('#1a0c10'), "H": rgb('#2a3a8a'), "G": rgb('#e8c040'), "S": rgb('#f2c8a0'), "e": rgb('#1a0c10'),
           "R": rgb('#c8302a'), "W": rgb('#f4f0e8'), "B": rgb('#2a3a8a'), "k": rgb('#e8c040'), "K": rgb('#6a6e78'),
           "Y": rgb('#fff27a'), "#": SHADOW}
SOLDIER_TOP = ["...oooo...", "...oHHo...", "...oHGo...", "...oSeo...", "kk.oRWRo..", "kkkoRRWoKK", "kk.oRRRo..",
               "...oBBBo.."]
SOLDIER_FLASH = ["...oooo...", "...oHHo...", "...oHGo...", "...oSeo...", "kk.oRWRo.Y", "kkkoRRWoKY", "kk.oRRRo.Y",
                 "...oBBBo.."]
SOLDIER_LEGS = {"": ["...oBoBo..", "..######.."], "_walk1": ["..oBo.oBo.", ".########."],
                "_walk2": ["....oBo...", "..######.."]}

# --- Scrap Beetle (7 x 7): a beetle of scrap metal and bolts; flying: its wings flap ---------------------------------
BEETLE = dict(METAL, o=rgb('#121318'), r=rgb('#a0602a'), B=rgb('#e0e4ec'), L=rgb('#3e414c'),
              v=rgb('#c8d8f0', 190), **{"#": SHADOW})
BEETLE_ROWS = {"": [".......", "..ooo..", ".omrmo.", "omMBMMo", "omrMMMo", ".oLoLo.", ".#####."],
               "_walk1": ["v.....v", "vvooovv", ".omrmo.", "omMBMMo", "omrMMMo", ".o...o.", "..###.."],
               "_walk2": [".......", "..ooo..", "vomrmov", "vmMBMMv", "vmrMMMv", ".o...o.", "..###.."]}

# --- Line Soldier (8 x 8) / Line Beetle (6 x 6): fresh from the belt - shiny red / unfinished --------------------------
LINE_SOLDIER = {"o": rgb('#2a0606'), "H": rgb('#c8202a'), "S": rgb('#f2c8a0'), "e": rgb('#2a0606'),
                "R": rgb('#e8302a'), "L": rgb('#ff9a90'), "W": rgb('#ffffff'), "B": rgb('#8a1818'), "K": rgb('#6a6e78'),
                "#": SHADOW}
LINE_SOLDIER_ROWS = ["..ooo...", "..oHLo..", "..oSeo..", ".oRWLo..", ".oRRRoKK", ".oRLRo..", "..oBoBo.", ".######."]
LINE_BEETLE = dict(METAL, o=rgb('#121318'), r=rgb('#e83a3a'), g=rgb('#5fd35f'), y=rgb('#ffe14d'), **{"#": SHADOW})
LINE_BEETLE_ROWS = ["......", ".ooo..", "omy.o.", "oMMrgo", ".o.o..", ".####."]

# --- Belt Turret (12 x 12, a box): dark grey turret on a base ----------------------------------------------------------
TURRET = dict(METAL, o=rgb('#0e0f14'), d=rgb('#3a3c44'), D=rgb('#2a2c32'), L=rgb('#6a6e78'), r=rgb('#ff4058'))
TURRET_ROWS = ["............", "............", "....oooo....", "...oLddDo...", "..oLddddDo..", "..oLdrddDoooo",
               "..oddddDDoKKK", "..oddddDDoooo", ".ooooooooooo.", ".oMmmmmmmmMo.", ".oMMMMMMMMMo.", ".ooooooooooo."]
TURRET["K"] = rgb('#5a5e68')
TURRET_ROWS = [r[:12] for r in TURRET_ROWS]

# --- Bomb Crate (11 x 11, a box): a wooden crate with FRAGILE marks and a burning fuse ---------------------------------
CRATE = {"o": rgb('#2a1606'), "W": rgb('#c8904a'), "w": rgb('#a06a30'), "d": rgb('#7a4a1e'), "R": rgb('#d8282a'),
         "f": rgb('#2a2a2a'), "F": rgb('#ffe14d'), "E": rgb('#ff7a2a'), "Z": rgb('#ffffff')}
CRATE_BASE = ["...........", "...........", "oooooooooo.", "oWWWWWWWWdo", "owRRwRRwwdo", "oWWWWWWWWdo",
              "owwwwwwwwdo", "oWRWRWRWWdo", "owwwwwwwwdo", "oddddddddoo", "oooooooooo."]
SPARKS = [["......F....", ".....fE...."], [".....E.F...", ".....fF...."], ["......Z....", ".....fEF..."]]

# --- Robo-Tesla (12 x 12): a robot with a Tesla coil on its head -------------------------------------------------------
TESLA = dict(METAL, o=rgb('#0e1018'), c=rgb('#c87a3a'), C=rgb('#8a4a1e'), b=rgb('#4fb8e8'), B=rgb('#a8f0ff'),
             e=rgb('#4fb8e8'), Y=rgb('#e8f8ff'), **{"#": SHADOW})
TESLA_ROWS = ["....ooo.....", "....obo.....", "...ocCco....", "....oco.....", "..oooooooo..", "..ommmmmMo..",
              "..omeMmeMo..", "..oMMMMMMo..", ".ommMMMMMMo.", ".omoMMMMoMo.", "..oMo..oMo..", "..########.."]
TESLA_SHOOT = ["..B.oBo.B...", "...oBYBo....", "..BocCcoB...", "....oco.....", "..oooooooo..", "..ommmmmMo..",
               "..omBMmBMo..", "..oMMMMMMo..", ".ommMMMMMMo.", ".omoMMMMoMo.", "..oMo..oMo..", "..########.."]

# --- Robo-Bomber (12 x 12): a robot with a mortar on its back -----------------------------------------------------------
BOMBER = dict(METAL, o=rgb('#0e1018'), t=rgb('#4a5a3a'), T=rgb('#2e3a24'), e=rgb('#ff4058'), s=rgb('#d8d8d8', 210),
              K=rgb('#2a2a2a'), **{"#": SHADOW})
BOMBER_ROWS = ["............", ".oo.........", "otTo........", "otTo........", ".otToooooo..", "..otommmMo..",
               "..oommeMeo..", "..oMMMMMMo..", ".ommMMMMMMo.", ".omoMMMMoMo.", "..oMo..oMo..", "..########.."]
BOMBER_SHOOT = ["ss.K........", "sooK........", "otTo........", "otTo........", ".otToooooo..", "..otommmMo..",
                "..oommeMeo..", "..oMMMMMMo..", ".ommMMMMMMo.", ".omoMMMMoMo.", "..oMo..oMo..", "..########.."]

# --- Portable Factory (20 x 20): a little factory on legs - chimney, saw-tooth roof, a belt hatch with a toy -----------
FACTORY = dict(METAL, o=rgb('#140c0a'), b=rgb('#a8483a'), B=rgb('#7a3028'), r=rgb('#5a6a8a'), R=rgb('#3a4a6a'),
               y=rgb('#ffd23a'), g=rgb('#2a2a30'), t=rgb('#e83a3a'), l=rgb('#5fd35f'), s=rgb('#c8c8c8', 200),
               S=rgb('#e8e8e8', 220), **{"#": SHADOW})
FACTORY_ROWS = [
    "....................",
    "....................",
    ".ooo................",
    ".oMo................",
    ".oMo.o...o...o......",
    ".oMoorooorooorooo...",
    ".oMorrRorrRorrRRo...",
    "oooooooooooooooooo..",
    "obbBbbbBbbbBbbbbBo..",
    "obBbbbBbbbBbbbBbbo..",
    "obbbyyybbbbbbbbbBo..",
    "obbbyyybbbogggggoo..",
    "obbBbbbBbbogtlgtgo..",
    "obbbbbbbbbogggggoo..",
    "oBBBBBBBBBoMmMmMmo..",
    "oooooooooooooooooo..",
    "..oMo..oMo..oMo.....",
    "..ono..ono..ono.....",
    "..ooo..ooo..ooo.....",
    ".################...",
]
FACTORY_SMOKE = [".Ss.................", "sSSs................"]   # the 2 top rows when it works

# --- the Assembly Line's machines (21 x 21, boxes) -------------------------------------------------------------------------
MACHINE = dict(METAL, o=rgb('#0e0f14'), y=rgb('#ffd23a'), k=rgb('#26252a'), r=rgb('#ff4058'), g=rgb('#5fd35f'),
               h=rgb('#ff7a2a'), H=rgb('#ffc85a'), t=rgb('#e83a3a'), b=rgb('#4da6ff'))
def machine(kind):
    """1: a small press (a piston over a plate), 2: a bigger one with a turret-and-crate hatch, 3: the fastest, hot."""
    w = 21
    rows = [["."] * w for _ in range(w)]
    def box(x0, y0, x1, y1, fill, edge="o"):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                rows[y][x] = edge if x in (x0, x1) or y in (y0, y1) else fill
    box(1, 6, 19, 19, "M")                                                 # the body
    for x in range(2, 19): rows[7][x] = "m"; rows[18][x] = "n"
    for x in range(2, 19):                                                 # hazard stripes along the bottom
        rows[16][x] = "y" if (x // 2) % 2 == 0 else "k"
    if kind == 1:
        box(7, 0, 13, 5, "m"); box(9, 6, 11, 11, "w")                        # the press head and its piston
        box(5, 12, 15, 14, "n")                                              # the plate it presses on
        rows[2][10] = "r"
    elif kind == 2:
        box(3, 1, 17, 6, "m"); box(6, 9, 14, 15, "k")                        # a bigger head, a dark hatch
        rows[3][6] = rows[3][10] = rows[3][14] = "g"                        # status lights
        for x in range(7, 14): rows[12][x] = "n"
        rows[11][9] = rows[11][10] = "M"; rows[11][11] = "t"                 # a crate / turret coming out
    else:
        box(4, 1, 16, 6, "h"); box(6, 9, 14, 15, "k")                        # hot: orange head, glowing hatch
        for x in range(7, 14):
            for y in range(10, 15): rows[y][x] = "h" if (x + y) % 3 else "H"
        rows[3][7] = rows[3][13] = "r"; rows[2][10] = "H"
    for y in (8, 12): rows[y][2] = rows[y][18] = "w"                         # bolts
    return ["".join(r) for r in rows]

SPRITES = {}
for tag, legs in SOLDIER_LEGS.items():
    SPRITES[f"toy_soldier{tag}"] = (lambda l: lambda: draw(SOLDIER_TOP + l, SOLDIER))(legs)
SPRITES["toy_soldier_shoot"] = lambda: draw(SOLDIER_FLASH + SOLDIER_LEGS[""], SOLDIER)
for tag, rows in BEETLE_ROWS.items():
    SPRITES[f"scrap_beetle{tag}"] = (lambda r: lambda: draw(r, BEETLE))(rows)
SPRITES["line_soldier"] = lambda: draw(LINE_SOLDIER_ROWS, LINE_SOLDIER)
SPRITES["line_beetle"] = lambda: draw(LINE_BEETLE_ROWS, LINE_BEETLE)
SPRITES["belt_turret"] = lambda: draw(TURRET_ROWS, TURRET)
SPRITES["bomb_crate"] = lambda: draw(SPARKS[0] + CRATE_BASE[2:], CRATE)
for k in range(3):
    SPRITES[f"bomb_crate_idle{k + 1}"] = (lambda s: lambda: draw(s + CRATE_BASE[2:], CRATE))(SPARKS[k])
SPRITES["robo-tesla"] = lambda: draw(TESLA_ROWS, TESLA)
SPRITES["robo-tesla_shoot"] = lambda: draw(TESLA_SHOOT, TESLA)
SPRITES["robo-bomber"] = lambda: draw(BOMBER_ROWS, BOMBER)
SPRITES["robo-bomber_shoot"] = lambda: draw(BOMBER_SHOOT, BOMBER)
SPRITES["portable_factory"] = lambda: draw(FACTORY_ROWS, FACTORY)
SPRITES["portable_factory_shoot"] = lambda: draw(FACTORY_SMOKE + FACTORY_ROWS[2:], FACTORY)
for k in (1, 2, 3):
    SPRITES[f"assembly_machine_{k}"] = (lambda n: lambda: draw(machine(n), MACHINE))(k)

if __name__ == "__main__":
    for name, make in SPRITES.items():
        im = make(); im.save(f"{sys.argv[1]}/{name}.png"); print(name, im.size)
