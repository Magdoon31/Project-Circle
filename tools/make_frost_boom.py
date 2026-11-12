# FROST BOOM (12.11): Frost Golem's winter blasts (hard mode, F2) - the normal explosion (boom1-6.png) recoloured
# light blue, frame by frame: each pixel keeps its brightness and transparency, dark = deep ice blue, bright = white.
# Run from the game's folder:  python tools/make_frost_boom.py

import os

import pygame

FOLDER = "assets/img/combat/projectiles"
FRAMES = range(1, 7)
DARK = (40, 120, 230)             # the darkest parts of the blast ...
LIGHT = (230, 248, 255)           # ... to the brightest


def brightness(r, g, b):
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255


def ice(colour):
    r, g, b, a = colour
    k = brightness(r, g, b)
    return tuple(round(d + (l - d) * k) for d, l in zip(DARK, LIGHT)) + (a,)


def recolour(path_in, path_out):
    picture = pygame.image.load(path_in).convert_alpha()      # (a colour key -> transparency)
    out = pygame.Surface(picture.get_size(), pygame.SRCALPHA)
    for y in range(picture.get_height()):
        for x in range(picture.get_width()):
            out.set_at((x, y), ice(picture.get_at((x, y))))
    pygame.image.save(out, path_out)


def main():
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.HIDDEN)            # convert_alpha needs a window
    for nr in FRAMES:
        recolour(os.path.join(FOLDER, f"boom{nr}.png"), os.path.join(FOLDER, f"frost_boom{nr}.png"))
    print(f"frost_boom1-{FRAMES[-1]}.png written to {FOLDER}")


if __name__ == "__main__":
    main()
