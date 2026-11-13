# THE TITLE'S SHADOW (13.11): a soft dark copy of the title's letters, a little lower, baked into its own picture -
# assets/img/menu/main/game_title_shadowed.png (made by tools/make_title_shadow.py from game_title.png) - so it grows
# and shrinks with the title's pulse. The picture is PAD px bigger than the title on every side.

import pygame

SOURCE = "assets/img/menu/main/game_title.png"
OUT = "assets/img/menu/main/game_title_shadowed.png"
PAD = 48                          # px (in the title picture's own size) of room round it for the shadow
ALPHA = 140                       # how dark
BLUR = 18                         # px, how soft
GROW = 8                          # px past the letters
DROP = 14                         # px down


def shadowed(title):
    """The title with its shadow under it (PAD px bigger on every side)."""
    w, h = title.get_size()
    out = pygame.Surface((w + 2 * PAD, h + 2 * PAD), pygame.SRCALPHA)
    dark = pygame.mask.from_surface(title, 40).to_surface(setcolor=(0, 0, 0, ALPHA), unsetcolor=(0, 0, 0, 0))
    for dx in (-GROW, 0, GROW):
        for dy in (-GROW, 0, GROW):
            out.blit(dark, (PAD + dx, PAD + dy + DROP))
    out = pygame.transform.gaussian_blur(out, BLUR)
    out.blit(title, (PAD, PAD))
    return out
