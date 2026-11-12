# FANCY TEXT (11.11): words drawn while the game runs (a save's name, its biome...) in the style of the menu's
# pictures (tools/make_save_sprites.py): Cinzel, cream fading into lavender, a dark purple outline. Made once per
# (text, size, style) and kept.

import pygame

FONT = "assets/font/Cinzel-Bold.ttf"          # SIL Open Font License 1.1
STYLES = {
    "cream": [(250, 246, 222), (250, 246, 222), (184, 150, 220), (118, 78, 170)],
    "red": [(255, 232, 222), (236, 130, 140), (170, 50, 70)],
    "green": [(196, 240, 186), (104, 190, 118), (34, 112, 62)],     # (12.11) an "I Have a Job" (easy) save
    "pale": [(214, 204, 232), (150, 130, 180)],
}
OUTLINE = (36, 16, 56)

_fonts = {}
_made = {}


def font(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.Font(FONT, size)
    return _fonts[size]


def fancy(text, size, style="cream"):
    """The text as a picture (kept: the same words are only made once)."""
    key = (text, size, style)
    if key not in _made:
        _made[key] = make(text, size, STYLES[style])
    return _made[key]


def make(text, size, colours):
    letters = font(size).render(text, True, (255, 255, 255))
    edge = max(2, size // 16)
    w, h = letters.get_width() + edge * 2, letters.get_height() + edge * 2
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    dark = font(size).render(text, True, OUTLINE)
    for dx in range(-edge, edge + 1):
        for dy in range(-edge, edge + 1):
            if dx * dx + dy * dy <= edge * edge:
                out.blit(dark, (edge + dx, edge + dy))
    fill = vertical_gradient(letters.get_size(), colours)
    fill.blit(letters, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    out.blit(fill, (edge, edge))
    return out


def vertical_gradient(size, colours):
    w, h = size
    surf = pygame.Surface(size, pygame.SRCALPHA)
    for y in range(h):
        t = y / max(1, h - 1) * (len(colours) - 1)
        i = min(int(t), len(colours) - 2)
        k = t - i
        c = [int(colours[i][j] + (colours[i + 1][j] - colours[i][j]) * k) for j in range(3)]
        pygame.draw.line(surf, c + [255], (0, y), (w - 1, y))
    return surf
