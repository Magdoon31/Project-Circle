# SPRITE BUTTONS (11.11): the menus' buttons are word pictures (assets/img/menu/<where it's used>/btn_*.png, made
# by tools/make_menu_sprites.py) that grow a little under the mouse. Used by the main menu, the save screen, the map's
# menu (ESC) and the fight's pause menu.

import pygame

MENU_IMG = "assets/img/menu/"
GROW = 1.12                       # a button under the mouse is this much bigger
EASE = 0.2

_loaded = {}


def load(path):
    """A menu picture, e.g. "main/btn_play" (loaded once)."""
    if path not in _loaded:
        _loaded[path] = pygame.image.load(MENU_IMG + path + ".png").convert_alpha()
    return _loaded[path]


def scaled(img, height):
    return pygame.transform.smoothscale(img, (max(1, int(img.get_width() * height / img.get_height())), int(height)))


class SpriteButton:
    """One word picture as a button. rect = where it can be clicked (its size without the hover growth)."""

    def __init__(self, name, height, folder="", file=None):
        """name: what it says (also its file: btn_<name>.png, spaces as _), in assets/img/menu/<folder>."""
        self.name = name
        file = file or "btn_" + name.replace(" ", "_")
        self.img = scaled(load(f"{folder}/{file}" if folder else file), height)
        self.scale = 1.0
        self.rect = self.img.get_rect()

    def draw(self, screen, center=None, hovered=None, topleft=None):
        if topleft is not None:
            self.rect = self.img.get_rect(topleft=topleft)
        else:
            self.rect = self.img.get_rect(center=center)
        if hovered is None:
            hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        self.scale += ((GROW if hovered else 1.0) - self.scale) * EASE
        size = (int(self.img.get_width() * self.scale), int(self.img.get_height() * self.scale))
        img = pygame.transform.smoothscale(self.img, size)
        screen.blit(img, img.get_rect(center=self.rect.center))


class ButtonColumn:
    """Buttons one under another in the middle of the screen; hover sound when the mouse comes onto one."""

    def __init__(self, names, height, sfx=None, gap=1.1, folder="", files=None):
        files = files or {}
        self.buttons = [SpriteButton(name, height, folder, files.get(name)) for name in names]
        self.height, self.sfx, self.gap = height, sfx, gap
        self.under = None

    def draw(self, screen, top):
        cx = screen.get_width() // 2
        for i, button in enumerate(self.buttons):
            button.draw(screen, (cx, int(top + i * self.height * self.gap + self.height / 2)))
        self.hover_sound()

    def hover_sound(self):
        under = self.clicked(pygame.mouse.get_pos())
        if under and under != self.under and self.sfx:
            self.sfx.play("hover")
        self.under = under

    def clicked(self, pos):
        """The name of the button at pos (None = none)."""
        return next((b.name for b in self.buttons if b.rect.collidepoint(pos)), None)
