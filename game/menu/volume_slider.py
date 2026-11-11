# VOLUME SLIDER (11.11): a value 0-1 (read with get(), changed with change(value)), drawn with the Settings
# screen's pictures (tools/make_menu_sprites.py): an icon, the track, the lit part (as far as the value goes) and a
# gem to drag. Also moved with the arrow keys (step()).

import pygame

from game.menu.sprite_button import load, scaled

GRAB = 30                         # px above / under the track that still grab it
STEP = 0.05                       # one arrow key press


class VolumeSlider:
    def __init__(self, get, change, icon, height):
        self.get, self.change = get, change
        self.icon = scaled(load("settings/icon_" + icon), height * 1.9) if icon else None
        self.track_img = load("settings/slider_track")
        self.fill_img = load("settings/slider_fill")
        self.knob = scaled(load("settings/slider_knob"), height * 1.7)
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.dragging = False
        self.track = self.fill = None

    def place(self, rect):
        """Where the track is (its pictures are scaled to this size)."""
        if rect.size != self.rect.size:
            self.track = pygame.transform.smoothscale(self.track_img, rect.size)
            self.fill = pygame.transform.smoothscale(self.fill_img, rect.size)
        self.rect = rect

    # --- input ------------------------------------------------------------------------------------------------
    def handle(self, event, pos):
        """True when it changed the value."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.inflate(0, GRAB).collidepoint(pos):
            self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        if self.dragging and event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
            self.change(self.value_at(pos[0]))
            return True
        return False

    def value_at(self, mouse_x):
        return max(0.0, min(1.0, (mouse_x - self.rect.x) / max(1, self.rect.width)))

    def step(self, direction):
        """An arrow key: a little up (+1) or down (-1)."""
        self.change(round(max(0.0, min(1.0, self.get() + STEP * direction)), 2))

    # --- drawing ----------------------------------------------------------------------------------------------
    def draw(self, screen):
        if self.icon:
            screen.blit(self.icon, self.icon.get_rect(midright=(self.rect.x - 24, self.rect.centery)))
        screen.blit(self.track, self.rect)
        lit = int(self.rect.width * self.get())
        if lit > 0:
            screen.blit(self.fill, self.rect, pygame.Rect(0, 0, lit, self.rect.height))
        screen.blit(self.knob, self.knob.get_rect(center=(self.rect.x + lit, self.rect.centery)))
