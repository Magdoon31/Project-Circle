# The achievements' icons (13.11): assets/img/menu/achievements/<id>.png (tools/make_achievement_icons.py),
# "locked.png" for a hidden one not reached yet. Loaded once per size; a missing file = a plain placeholder.

import os

import pygame

FOLDER = os.path.join("assets", "img", "menu", "achievements")
_raw, _sized = {}, {}


def icon(name, size, dim=False):
    """The icon `name` at `size` px; dim = greyed out (not reached yet)."""
    key = (name, size, dim)
    if key not in _sized:
        picture = pygame.transform.smoothscale(raw(name), (size, size))
        if dim:
            picture = pygame.transform.grayscale(picture)
            picture.fill((90, 90, 90, 255), special_flags=pygame.BLEND_RGBA_MULT)
        _sized[key] = picture
    return _sized[key]


def raw(name):
    if name not in _raw:
        path = os.path.join(FOLDER, name + ".png")
        try:
            _raw[name] = pygame.image.load(path).convert_alpha()
        except (pygame.error, FileNotFoundError):
            _raw[name] = placeholder()
    return _raw[name]


def placeholder():
    surface = pygame.Surface((96, 96), pygame.SRCALPHA)
    pygame.draw.rect(surface, (60, 50, 80), surface.get_rect(), 0, 18)
    pygame.draw.rect(surface, (160, 140, 200), surface.get_rect(), 4, 18)
    return surface
