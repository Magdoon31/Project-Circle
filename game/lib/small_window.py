# SMALL WINDOW (11.11, Settings -> Video -> Full screen off): a fixed 960 x 540 window with the system's title bar
# (move it, minimise it). The game is still drawn at the screen's full size (every layout stays the same) on a
# "canvas"; each shown frame is scaled down into the window, and the mouse is scaled back up - so the rest of the
# game never knows. It does that by standing in for a few pygame calls:
#   display.flip / update  - scale the canvas into the window first
#   display.get_surface    - the canvas
#   mouse.get_pos / set_pos, event.get - mouse positions in the canvas's size

import os

import pygame

WINDOW_SIZE = (960, 540)
BARS = (0, 0, 0)                  # the window's sides if the screen isn't 16:9

MOUSE_EVENTS = (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP)


class SmallWindow:
    def __init__(self, full_size):
        os.environ.setdefault("SDL_VIDEO_CENTERED", "1")
        self.window = pygame.display.set_mode(WINDOW_SIZE)
        self.canvas = pygame.Surface(full_size).convert()
        self.scale = min(WINDOW_SIZE[0] / full_size[0], WINDOW_SIZE[1] / full_size[1])
        self.area = pygame.Rect(0, 0, round(full_size[0] * self.scale), round(full_size[1] * self.scale))
        self.area.center = (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2)
        self.stand_in()

    def stand_in(self):
        """Put this window's versions of the pygame calls in place (the originals are kept to call)."""
        self.real = {"flip": pygame.display.flip, "get_pos": pygame.mouse.get_pos,
                     "set_pos": pygame.mouse.set_pos, "get": pygame.event.get}
        pygame.display.flip = self.flip
        pygame.display.update = lambda *rects: self.flip()
        pygame.display.get_surface = lambda: self.canvas
        pygame.mouse.get_pos = self.mouse_pos
        pygame.mouse.set_pos = self.set_mouse_pos
        pygame.event.get = self.events

    # --- the picture ------------------------------------------------------------------------------------------
    def flip(self):
        self.window.fill(BARS)
        pygame.transform.smoothscale(self.canvas, self.area.size, self.window.subsurface(self.area))
        self.real["flip"]()

    # --- the mouse ----------------------------------------------------------------------------------------------
    def to_canvas(self, pos):
        x = (pos[0] - self.area.x) / self.scale
        y = (pos[1] - self.area.y) / self.scale
        w, h = self.canvas.get_size()
        return int(max(0, min(w - 1, x))), int(max(0, min(h - 1, y)))

    def mouse_pos(self):
        return self.to_canvas(self.real["get_pos"]())

    def set_mouse_pos(self, *pos):
        x, y = pos[0] if len(pos) == 1 else pos
        self.real["set_pos"](self.area.x + x * self.scale, self.area.y + y * self.scale)

    def events(self, *args, **kwargs):
        events = self.real["get"](*args, **kwargs)
        for event in events:
            if event.type in MOUSE_EVENTS:
                event.pos = self.to_canvas(event.pos)
                if event.type == pygame.MOUSEMOTION:
                    event.rel = (round(event.rel[0] / self.scale), round(event.rel[1] / self.scale))
        return events
