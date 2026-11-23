# The player's HP bar in fights (pixel art, shown x2 - smaller pixels than the rest, 23.11): a frame (no heart, Filip),
# the fill in 3 colours (green / yellow under 50% / red under 25%) and the "lost" part (light: the HP you just lost,
# it shrinks after a hit). The fills are as big as the frame; the game cuts them to the HP left.
# Run: py tools/make_hp_bar.py <folder>
import sys
from PIL import Image

def rgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) + (255,)
W, H = 23, 5
FILL_X = (1, 22)                 # file px: where the fill goes (from, to) - the same numbers as in sprites.py
FILL_Y = (1, 4)
OUT, BACK = rgb('#1a0a12'), rgb('#3a2030')
FILLS = {"hp_bar_fill": (rgb('#8ef06a'), rgb('#4fcf3a'), rgb('#2f9a2a')),
         "hp_bar_fill_mid": (rgb('#ffe36a'), rgb('#f2c230'), rgb('#c8901a')),
         "hp_bar_fill_low": (rgb('#ff8a8a'), rgb('#e83a3a'), rgb('#a01c1c')),
         "hp_bar_lost": (rgb('#ffffff'), rgb('#ffe0e0'), rgb('#e8b8b8'))}

def frame():
    im = Image.new('RGBA', (W, H))
    for x in range(FILL_X[0] - 1, FILL_X[1] + 1):
        for y in range(FILL_Y[0] - 1, FILL_Y[1] + 1):
            edge = x in (FILL_X[0] - 1, FILL_X[1]) or y in (FILL_Y[0] - 1, FILL_Y[1])
            im.putpixel((x, y), OUT if edge else BACK)
    return im

def fill(colours):
    im = Image.new('RGBA', (W, H))
    for x in range(*FILL_X):
        for k, y in enumerate(range(*FILL_Y)):
            im.putpixel((x, y), colours[k])
    return im

# --- (23.11) the effects on the player: small icons over its HP bar (7 x 7, shown x2 like the bar) ----------------
ICON_OUT = rgb('#140c14')
EFFECT_ICONS = {                 # effect: (badge colour, symbol), symbol rows 5 x 5 (# = the symbol, light)
    "slow":      ('#3268c8', ["#...#", ".#.#.", "..#..", "#...#", ".#.#."]),       # down chevrons
    "weakness":  ('#8a8a8a', ["..#..", "..#..", "#.#.#", ".###.", "..#.."]),       # arrow down
    "glued":     ('#e8b820', ["..#..", ".###.", "#####", "#####", ".###."]),       # a drop of glue
    "confusion": ('#8a40e0', [".###.", "#...#", "...#.", "..#..", "..#.."]),       # ?
    "binded":    ('#7a4a24', ["#...#", ".#.#.", "..#..", ".#.#.", "#...#"]),       # X (tied)
    "acid":      ('#a8a83a', ["..#..", ".#.#.", "#...#", "#...#", ".###."]),       # an empty drop
    "poison":    ('#2f9a3a', [".###.", "#.#.#", "#####", ".#.#.", ".#.#."]),       # a skull
    "burn":      ('#e0601c', ["..#..", ".##..", ".###.", "#####", ".###."]),       # a flame
    "speed":     ('#3aa0e8', ["#..#.", ".#..#", "..#..", ".#..#", "#..#."]),       # right chevrons
    "strength":  ('#d8281a', ["..#..", ".###.", "#.#.#", "..#..", "..#.."]),       # arrow up
    "boost":     ('#c8a028', ["..#..", "#####", ".###.", ".#.#.", "#...#"]),       # a star
    "focus":     ('#4a4a5a', ["..#..", ".#.#.", "##.##", ".#.#.", "..#.."]),       # a crosshair
}
SYMBOL = rgb('#ffffff')

def icon(colour, symbol):
    im = Image.new('RGBA', (7, 7))
    base = rgb(colour)
    for y in range(7):
        for x in range(7):
            corner = x in (0, 6) and y in (0, 6)
            if corner: continue
            edge = x in (0, 6) or y in (0, 6)
            im.putpixel((x, y), ICON_OUT if edge else base)
    for y, row in enumerate(symbol):
        for x, ch in enumerate(row):
            if ch == "#": im.putpixel((x + 1, y + 1), SYMBOL)
    return im

if __name__ == "__main__":
    frame().save(f"{sys.argv[1]}/hp_bar.png")
    for name, colours in FILLS.items():
        fill(colours).save(f"{sys.argv[1]}/{name}.png")
    for name, (colour, symbol) in EFFECT_ICONS.items():
        icon(colour, symbol).save(f"{sys.argv[1]}/effect_{name}.png")
    print("ok")
