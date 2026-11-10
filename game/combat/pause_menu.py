# PAUSE MENU (10.11): ESC in a fight. The fight stands still (Game doesn't update it) and a menu shows over it:
#   Return / Settings (music and sound volume) / Stats / Main menu / Quit game   - like the map's menu, no Save.
# handle() says what the player chose: "resume", "main_menu", "quit" or None (still in the menu).
# Only the menu lives here - pausing the fight's clocks is Combat.pause / resume.

import pygame

OPTIONS = ["return", "settings", "stats", "main menu", "quit game"]
VEIL = (0, 0, 0, 160)
IDLE = (170, 170, 170)
HOVER = (255, 255, 255)
TRACK = (100, 100, 100)
KNOB_RADIUS = 15


class VolumeSlider:
    """A slider for a volume (0-1) that something keeps in `owner.<attr>` and applies with owner.update_volume()."""

    def __init__(self, owner, attr, label):
        self.owner, self.attr, self.label = owner, attr, label
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.dragging = False

    @property
    def value(self):
        return getattr(self.owner, self.attr)

    def set_from(self, mouse_x):
        share = (mouse_x - self.rect.x) / max(1, self.rect.width)
        setattr(self.owner, self.attr, max(0.0, min(1.0, share)))
        self.owner.update_volume()

    def handle(self, event, pos):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.inflate(0, 30).collidepoint(pos):
            self.dragging = True
            self.set_from(pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.set_from(pos[0])

    def draw(self, screen, font):
        pygame.draw.rect(screen, TRACK, self.rect)
        knob = (int(self.rect.x + self.rect.width * self.value), self.rect.centery)
        pygame.draw.circle(screen, HOVER, knob, KNOB_RADIUS)
        label = font.render(self.label, True, HOVER)
        screen.blit(label, label.get_rect(midright=(self.rect.x - 30, self.rect.centery)))


class PauseMenu:
    def __init__(self, screen, sfx, music, settings, font):
        self.screen = screen
        self.sfx = sfx
        self.settings = settings                    # SettingsManager: saves the volumes
        self.font = font
        self.sliders = [VolumeSlider(music, "music_volume", "Music"), VolumeSlider(sfx, "sfx_volume", "Sounds")]
        self.page = "menu"
        self.backdrop = None
        self.buttons = []

    def open(self, fight_picture):
        """The fight as it was when ESC was pressed (drawn behind the menu, darkened)."""
        self.page = "menu"
        self.backdrop = fight_picture.copy()
        veil = pygame.Surface(self.backdrop.get_size(), pygame.SRCALPHA)
        veil.fill(VEIL)
        self.backdrop.blit(veil, (0, 0))

    # --- input -----------------------------------------------------------------------------------------------
    def handle(self, events, pos):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.page == "menu":
                    return "resume"
                self.back_to_menu()
            elif self.page == "settings":
                for slider in self.sliders:
                    slider.handle(event, pos)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                choice = self.clicked(pos)
                if choice:
                    return choice
        return None

    def clicked(self, pos):
        hit = next((name for name, rect in self.buttons if rect.collidepoint(pos)), None)
        if hit is None:
            return None
        self.sfx.play("use")
        if hit == "back":
            self.back_to_menu()
        elif hit in ("settings", "stats"):
            self.page = hit
        else:
            return {"return": "resume", "main menu": "main_menu", "quit game": "quit"}[hit]
        return None

    def back_to_menu(self):
        if self.page == "settings":
            self.settings.settings_data_save()
        self.page = "menu"

    # --- drawing ---------------------------------------------------------------------------------------------
    def draw(self):
        self.screen.blit(self.backdrop, (0, 0))
        self.buttons = []
        if self.page == "menu":
            self.draw_options()
        else:
            if self.page == "settings":
                self.draw_sliders()
            self.draw_button("back", self.back_rect())

    def draw_options(self):
        w, h = self.screen.get_size()
        bw, bh = w // 3.9, h // 15
        for i, name in enumerate(OPTIONS):
            self.draw_button(name, pygame.Rect((w - bw) // 2, h // 2.6 + i * bh * 1.5, bw, bh), radius=10)

    def draw_sliders(self):
        w, h = self.screen.get_size()
        for i, slider in enumerate(self.sliders):
            slider.rect = pygame.Rect((w - w // 4) // 2, h // 3 + i * h // 8, w // 4, h // 60)
            slider.draw(self.screen, self.font)

    def back_rect(self):
        w, h = self.screen.get_size()
        return pygame.Rect(w - w // 6, h - h // 16, w // 6, h // 20)

    def draw_button(self, name, rect, radius=5):
        hover = rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(self.screen, HOVER if hover else IDLE, rect, 0, radius)
        text = self.font.render(name.capitalize(), True, (0, 0, 0))
        self.screen.blit(text, text.get_rect(center=rect.center))
        self.buttons.append((name, rect))
