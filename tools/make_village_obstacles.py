# Village stones (23.11): run py tools/make_village_obstacles.py <folder with Filip's original stones> <output folder>.
# Filip: keep the old stone shapes, use the new texture - so his silhouette, outline and shadow pixels stay
# where they are; inside, each face (top / lit left / shaded right, told apart by his colours) gets the boulders'
# shading in lumps, cracks, moss tufts on the top, and the outline turns very dark brown (not black).
import numpy as np
from PIL import Image

def rgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) + (255,)
S_HI, S_LIGHT, S_MID, S_DARK, S_DEEP = rgb('#c2a39b'), rgb('#a4857e'), rgb('#8f736d'), rgb('#6c5a56'), rgb('#443432')
S_SHADE, S_OUT, CRACK = rgb('#7e6864'), rgb('#1e1412'), rgb('#3a2c2a')
MOSS_HI, MOSS, MOSS_LO = rgb('#8ccf5a'), rgb('#5f9a3c'), rgb('#3f7028')
TOP = {'#b29089', '#ad8c85', '#a4857e', '#9b7d77', '#8f736d', '#86716d'}
LEFT = {'#7e6864', '#6c5a56', '#60504d'}
RIGHT = {'#543e39', '#443432', '#352927', '#281f1e', '#2b2120'}
FACE_TONES = {"top": (S_HI, S_LIGHT, S_MID), "left": (S_MID, S_SHADE, S_DARK), "right": (S_DARK, rgb("#54403b"), S_DEEP)}
LUMP = 3                                    # px: the size of the light / dark lumps on a face

def lumps(x, y, seed):
    """-1 / 0 / 1: a darker, plain or lighter lump at this pixel (blocky noise, the same every run)."""
    cx, cy = (x + (y // LUMP) * 2) // LUMP, y // LUMP
    h = (cx * 73856093 ^ cy * 19349663 ^ seed * 83492791) % 7
    return 1 if h == 0 else (-1 if h in (1, 2) else 0)

def retexture(path, cracks, moss, seed):
    a = np.array(Image.open(path).convert('RGBA'))
    out = a.copy()
    h, w = a.shape[:2]
    face = np.full((h, w), '', object)
    for y in range(h):
        for x in range(w):
            if a[y, x, 3] != 255: continue
            c = '#%02x%02x%02x' % tuple(a[y, x, :3])
            face[y, x] = 'top' if c in TOP else 'left' if c in LEFT else 'right' if c in RIGHT else 'out'
    for y in range(h):
        for x in range(w):
            f = face[y, x]
            if f == 'out': out[y, x] = S_OUT; continue
            if not f: continue
            hi, mid, lo = FACE_TONES[f]
            edge_up = y > 0 and face[y - 1, x] == 'out'                    # the rim along the top: lit
            tone = lumps(x, y, seed)
            out[y, x] = hi if (edge_up and f != 'right') or tone > 0 else lo if tone < 0 else mid
    for crack in cracks:
        for x, y in crack:
            if face[y, x] in ('top', 'left', 'right'): out[y, x] = CRACK
    for x, y, r in moss:                                                     # moss tufts on the top face
        for yy in range(y - 1, y + 2):
            for xx in range(x - r, x + r + 1):
                if 0 <= yy < h and 0 <= xx < w and face[yy, xx] == 'top' and abs(xx - x) + abs(yy - y) * 2 <= r + 1:
                    out[yy, xx] = MOSS_HI if yy < y else (MOSS if yy == y else MOSS_LO)
    return Image.fromarray(out)

STONES = {
    "village_pillar_small": dict(cracks=[[(5, 10), (5, 11), (6, 12)], [(14, 11), (14, 12)]], moss=[(8, 3, 2)], seed=1),
    "village_pillar_medium": dict(cracks=[[(5, 12), (6, 13), (6, 14), (7, 15)], [(18, 14), (18, 15), (19, 16)]],
                                  moss=[(11, 3, 3), (18, 4, 2)], seed=2),
    "village_pillar_large": dict(cracks=[[(6, 14), (7, 15), (7, 16), (8, 17), (8, 18)], [(23, 15), (23, 16), (24, 17)],
                                         [(12, 22), (13, 23)]], moss=[(12, 4, 3), (19, 3, 2), (24, 6, 2)], seed=3),
}
if __name__ == "__main__":
    import sys, os
    for name, kw in STONES.items():
        retexture(os.path.join(sys.argv[1], name + ".png"), **kw).save(os.path.join(sys.argv[2], name + ".png"))
