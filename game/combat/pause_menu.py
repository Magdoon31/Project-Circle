# PAUSE MENU (10.11): ESC in a fight. The fight stands still (Game doesn't update it) and a menu shows over it:
#   Return / Settings / Stats / Main menu / Quit game   - like the map's menu, no Save.
#   (11.11) Settings = the same Settings screen as in the main menu (game/menu/settings_screen.py).
# handle() says what the player chose: "resume", "main_menu", "quit" or None (still in the menu).
# Only the menu lives here - pausing the fight's clocks is Combat.pause / resume.

import pygame

from game.menu.sprite_button import ButtonColumn, SpriteButton, load, scaled

OPTIONS = ["return", "settings", "stats", "main menu", "quit game"]
VEIL = (0, 0, 0, 160)
BUTTON_H = 0.055                  # (11.11) the buttons are word pictures (game/menu/sprite_button.py), all as tall
TITLES = {"menu": "esc/title_paused", "stats": "esc/title_stats"}


class PauseMenu:
    def __init__(self, screen, sfx, music, settings, font, settings_screen):
        self.screen = screen
        self.sfx = sfx
        self.settings = settings                    # SettingsManager: saves the settings
        self.settings_screen = settings_screen
        self.font = font
        self.page = "menu"
        self.backdrop = None
        h = screen.get_height()
        self.column = ButtonColumn(OPTIONS, h * BUTTON_H, sfx, folder="esc", files={"settings": "btn_settings_esc"})
        self.back = SpriteButton("back", h * 0.05)
        self.titles = {page: scaled(load(name), h * 0.1) for page, name in TITLES.items()}

    def open(self, fight_picture):
        """The fight as it was when ESC was pressed (drawn behind the menu, darkened)."""
        self.page = "menu"
        self.backdrop = fight_picture.copy()
        veil = pygame.Surface(self.backdrop.get_size(), pygame.SRCALPHA)
        veil.fill(VEIL)
        self.backdrop.blit(veil, (0, 0))

    # --- input -----------------------------------------------------------------------------------------------
    def handle(self, events, pos):
        if self.page == "settings":
            if self.settings_screen.handle(events, pos) == "back":
                self.back_to_menu()
            return None
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.page == "menu":
                    return "resume"
                self.back_to_menu()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                choice = self.clicked(pos)
                if choice:
                    return choice
        return None

    def clicked(self, pos):
        if self.page != "menu":
            hit = "back" if self.back.rect.collidepoint(pos) else None
        else:
            hit = self.column.clicked(pos)
        if hit is None:
            return None
        self.sfx.play("use")
        if hit == "back":
            self.back_to_menu()
        elif hit in ("settings", "stats"):
            self.page = hit
            if hit == "settings":
                self.settings_screen.open(in_game=True)
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
        w, h = self.screen.get_size()
        if self.page == "settings":
            self.settings_screen.draw()
            return
        title = self.titles[self.page]
        self.screen.blit(title, title.get_rect(center=(w // 2, int(h * 0.2))))
        if self.page == "menu":
            self.column.draw(self.screen, h * 0.33)
        else:
            self.back.draw(self.screen, (w - w // 10, h - h // 14))
