# DARKER OUTLINE (13.11): in a picture with a chalky dark outline (e.g. the menu's foreground_1.png) half of the
# light grey specks in the outline - the band along the picture's transparent edge - are made dark.
# Run from the game's folder:  python tools/darken_outline.py assets/img/menu/background/foreground_1.png
# (it overwrites the file - keep a copy if you want the old one). Needs Pillow and numpy.

import sys

import numpy as np
from PIL import Image, ImageFilter

BAND = 31                         # px: the outline band = this wide a filter from the transparent edge (~15 px in)
LIGHT = 80                        # a speck: every channel above this ...
GREY = 30                         # ... and the channels this close together (grey, not a colour)
SHARE = 0.5                       # how many of the specks become dark
DARK = (28, 26, 30)
SEED = 7


def darken(path):
    a = np.array(Image.open(path).convert("RGBA")).astype(np.int16)
    opaque = a[..., 3] > 0
    inside = np.array(Image.fromarray((opaque * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(BAND))) > 0
    rgb = a[..., :3]
    specks = opaque & ~inside & (rgb.min(axis=2) > LIGHT) & (rgb.max(axis=2) - rgb.min(axis=2) < GREY)
    rng = np.random.default_rng(SEED)
    pick = specks & (rng.random(specks.shape) < SHARE)
    rgb[pick] = np.array(DARK) + rng.integers(-8, 9, size=(pick.sum(), 1))
    Image.fromarray(a.astype(np.uint8), "RGBA").save(path)
    print(f"{pick.sum()} of {specks.sum()} light outline pixels made dark in {path}")


if __name__ == "__main__":
    darken(sys.argv[1])
