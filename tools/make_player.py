# The player in fights (pixel art 1:4, 16 x 19, 8 directions, 23.11): Filip's pink ball and its TOP HAT (as on the
# menu picture) - a grey-black hat with a brim, its crown leaning the way the player looks, so every direction reads.
# Colours of the ball and its outline are Filip's. Run: py tools/make_player.py <folder>
import math, sys
from PIL import Image

def rgb(h, a=255): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) + (a,)
T = (0, 0, 0, 0)
B_OUT, B_DARK, B_MID, B_LIGHT, B_RIM = rgb('#1e0814'), rgb('#8e295d'), rgb('#cc287d'), rgb('#ff0183'), rgb('#6b1f46')
H_OUT, H_DARK, H_MID, H_LIGHT, H_BAND = rgb('#050507'), rgb('#1c1c22'), rgb('#2e2e36'), rgb('#55555f'), rgb('#101014')
SHADOW = (0, 0, 0, 51)
DIRS = {"n": (0, -1), "ne": (1, -1), "e": (1, 0), "se": (1, 1), "s": (0, 1), "sw": (-1, 1), "w": (-1, 0), "nw": (-1, -1)}
SIZE = (16, 19)                     # px of the file: the hat stands over the ball
BALL = (7.5, 11.0, 6.6, 6.2)          # centre x, y, radius across, radius down

def player(dx, dy):
    W, H = SIZE
    px = [[T] * W for _ in range(H)]
    owner = [[None] * W for _ in range(H)]
    cx, cy, rx, ry = BALL
    for y in range(H):                                          # the ball, lit from the top-left
        for x in range(W):
            u, v = (x - cx) / rx, (y - cy) / ry
            d = u * u + v * v
            if d > 1: continue
            lit = -0.45 * u - 0.75 * v
            c = B_LIGHT if lit > 0.62 and d > 0.25 else B_MID if lit > -0.35 else B_DARK
            if v > 0.82: c = B_RIM                                # the bottom edge in shade
            px[y][x], owner[y][x] = c, "ball"
    # the hat: a brim (a flat oval) and a crown leaning towards where it looks
    bx, by = 7.5 + dx * 1.3, 6.2 + dy * 0.7                      # the brim's middle (on the ball's top)
    brim_rx, brim_ry = 3.9, 1.2
    lean_x, lean_y = dx * 1.8, -dy * 0.3
    crown_h = 5.5 if dy <= 0 else 4.5                            # looking down (at you) the crown is foreshortened
    for y in range(H):
        for x in range(W):
            u, v = (x - bx) / brim_rx, (y - by) / brim_ry
            if u * u + v * v <= 1:
                px[y][x], owner[y][x] = (H_LIGHT if v < -0.3 and u < 0.2 else H_MID), "hat"
    for i in range(int(crown_h * 4) + 1):                       # the crown: slices from the brim up
        t = i / (crown_h * 4)
        y = by - 0.5 - t * crown_h + lean_y * t
        mid = bx + lean_x * t
        half = 2.2 - 0.15 * t
        for x in range(int(round(mid - half)), int(round(mid + half)) + 1):
            k = (x - mid) / half
            c = H_LIGHT if k < -0.45 else H_DARK if k > 0.45 else H_MID
            if t < 0.22: c = H_BAND                              # the hat band just over the brim
            yy = int(round(y))
            if 0 <= yy < H and 0 <= x < W: px[yy][x], owner[yy][x] = c, "hat"
    top_y = int(round(by - 0.5 - crown_h + lean_y))             # the crown's flat top, a lit line
    for x in range(int(round(bx + lean_x - 1.6)), int(round(bx + lean_x + 1.6)) + 1):
        if 0 <= top_y < H and owner[top_y][x] == "hat": px[top_y][x] = H_LIGHT
    # outlines: each part its own very dark shade
    add = []
    for y in range(H):
        for x in range(W):
            if owner[y][x]: continue
            near = [owner[y + j][x + i] for i, j in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= x + i < W and 0 <= y + j < H]
            if "hat" in near: add.append((x, y, H_OUT))
            elif "ball" in near: add.append((x, y, B_OUT))
    for x, y, c in add: px[y][x], owner[y][x] = c, "out"
    for y in range(H - 1, 0, -1):                               # the shadow: down-right, under the ball
        for x in range(W - 1, 0, -1):
            if owner[y][x] is None and owner[y - 1][x - 1] in ("out", "ball") and y >= H - 3: px[y][x] = SHADOW
    im = Image.new('RGBA', (W, H))
    for y in range(H):
        for x in range(W): im.putpixel((x, y), px[y][x])
    return im

if __name__ == "__main__":
    for name, (dx, dy) in DIRS.items():
        player(dx, dy).save(f"{sys.argv[1]}/{name}.png")
    print("ok")
