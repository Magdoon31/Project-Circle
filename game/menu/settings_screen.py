# THE SETTINGS SCREEN (11.11): the same one from the main menu (Settings) and from ESC (on the map, in a fight).
#   tabs: Audio / Video / Controls / Gameplay (click, or Tab); a list of settings under them:
#     slider - drag it, or the arrow keys            choice / on-off - the arrows (click, or Left / Right)
#     key    - click (or Enter), then press a key (Backspace: no key, Esc: keep the old one)
#   Up / Down choose a row. Defaults - this tab's settings back to their defaults. Back / Esc - leave.
#   Point at a row: a short description comes up at the bottom.
#   Full screen restarts the game (in a game: press it twice - what isn't saved is lost).
# The values live in options.py; on_change(name) tells the game a setting changed (e.g. a volume).

import pygame

from game.menu import fancy_text as FANCY
from game.menu import options as OPT
from game import controls as KEYS
from game.lib import restart as RESTART
from game.menu.sprite_button import SpriteButton, load, scaled
from game.menu.volume_slider import VolumeSlider

TABS = ["audio", "video", "controls", "gameplay"]
TAB_GAP = 0.045                   # space between two tabs (part of the screen's width)
ON_OFF = {True: "On", False: "Off"}
VALUE_NAMES = {
    "shadow_quality": {"low": "Low", "medium": "Medium", "high": "High"},
    "motion_blur": {"off": "Off", "light": "Light", "strong": "Strong"},
    "blur_where": {"map": "Map", "fight": "Fights", "both": "Map and fights"},
    "move_keys": {"wasd": "W A S D", "ijkl": "I J K L", "arrows": "Arrows"},
    "text_speed": {"slow": "Slow", "normal": "Normal", "fast": "Fast", "instant": "Instant"},
    "autosave": {"off": "Off", "bosses": "After bosses", "often": "+ every 5 min"},
}
ROWS = {          # tab -> [(option, label, kind, icon / -, description)]
    "audio": [
        ("master_volume", "Master", "slider", "master", "All of the game's sound at once."),
        ("music_volume", "Music", "slider", "music", "The music."),
        ("sfx_volume", "Sounds", "slider", "sounds", "Shots, hits, coins, menus..."),
        ("dialogue_volume", "Dialogue", "slider", "dialogue", "The talking sounds and recorded voices in talks."),
    ],
    "video": [
        ("fullscreen", "Full screen", "toggle", None, "Full screen or a window. The game restarts to change it."),
        ("flashes", "Flashes", "toggle", None, "The white flash when a boss changes phase, the song fight's flashes."),
        ("weather", "Weather", "toggle", None,
         "Snow on the map and the blizzard in fights. Better turned on for nicer atmosphere."),
        ("shadow_quality", "Shadows", "choice", None, "How soft the light's edges are in dark fights. Lower = faster."),
        ("motion_blur", "Motion blur", "choice", None, "Movement leaves a short trail."),
        ("blur_where", "Blur where", "choice", None, "Where the motion blur is used."),
    ],
    "controls": [
        ("move_keys", "Move", "choice", None, "The keys you move with (also to choose an answer in talks)."),
        ("key_map", "World map", "key", None, "Opens the world map."),
        ("key_shop", "Shop", "key", None, "Opens the shop."),
        ("key_shoot", "Shoot", "key", None, "Shoots, like the left mouse button."),
        ("key_equip", "Equip", "key", None, "Equips or takes off the item you selected."),
        ("key_delete", "Remove item", "key", None, "Removes the item you selected (it asks first)."),
        ("key_tab", "Next page", "key", None, "Changes the page: Items / Sigils, Buy / Sell."),
    ],
    "gameplay": [
        ("damage_numbers", "Damage numbers", "toggle", None, "Numbers over enemies show how much you hit them for."),
        ("text_speed", "Text speed", "choice", None, "How fast the words appear in talks."),
        ("autosave", "Autosave", "choice", None, "When the game saves by itself."),
        ("pause_on_phase", "Pause on boss phase", "toggle", None, "The fight pauses when a boss changes phase."),
        ("short_tooltips", "Short tooltips", "toggle", None, "The shop shows only an item's name, DPS and range."),
    ],
}
KEY_HINT = "Press a key  (Backspace: none, Esc: cancel)"
RESTART_IN_GAME_NOTE = "Press again to restart the game - what isn't saved is lost"
ROW_H, LABEL_SIZE, VALUE_SIZE = 0.074, 0.032, 0.03            # shares of the screen's height
LEFT, MIDDLE, RIGHT = 0.27, 0.62, 0.74                         # shares of the screen's width
BAND = (40, 24, 64, 110)
DESCRIPTION_COLOUR = (214, 204, 232)
WARNING_COLOUR = (255, 160, 170)


class SettingsScreen:
    def __init__(self, screen, sfx, on_change):
        self.screen, self.sfx, self.on_change = screen, sfx, on_change
        w, h = screen.get_size()
        self.title = scaled(load("settings/title_settings"), h * 0.09)
        self.tab_imgs = {tab: scaled(load("settings/tab_" + tab), h * 0.05) for tab in TABS}
        self.arrows = [scaled(load("settings/icon_arrow_" + side), h * 0.035) for side in ("left", "right")]
        self.back = SpriteButton("back", h * 0.05)
        self.defaults = SpriteButton("defaults", h * 0.05, "settings")
        self.sliders = {option: VolumeSlider(lambda o=option: OPT.get(o), lambda v, o=option: self.change(o, v),
                                             icon, h * 0.028)
                        for rows in ROWS.values() for option, _, kind, icon, _ in rows if kind == "slider"}
        self.open()

    def open(self, tab="audio", in_game=False):
        self.tab, self.row = tab, 0
        self.in_game = in_game                    # from ESC (a restart loses what isn't saved)
        self.waiting = None                       # the key option waiting for a key press
        self.note = ""                            # e.g. "That key moves you"
        self.restart_asked = False                # Full screen pressed once in a game: once more restarts
        self.pointed = None
        self.tab_rects, self.row_rects, self.arrow_rects = {}, [], []

    @property
    def rows(self):
        return ROWS[self.tab]

    # --- changing values ---------------------------------------------------------------------------------------
    def change(self, option, value):
        OPT.set(option, value)
        self.on_change(option)

    def cycle(self, i, direction):
        option, _, kind, _, _ = self.rows[i]
        if kind == "slider":
            self.sliders[option].step(direction)
        elif option == "fullscreen":
            self.switch_screen_mode()
        elif kind == "toggle":
            self.change(option, not OPT.get(option))
        elif kind == "choice":
            values = OPT.CHOICES[option]
            self.change(option, values[(values.index(OPT.get(option)) + direction) % len(values)])
        elif kind == "key":
            self.waiting, self.note = option, ""
            return
        self.sfx.play("hover")

    def switch_screen_mode(self):
        """Full screen <-> window: saved, then the game restarts (in a game only when you press it again)."""
        if self.in_game and not self.restart_asked:
            self.restart_asked = True
            return
        OPT.set("fullscreen", not OPT.get("fullscreen"))
        OPT.save()
        RESTART.restart_game()

    def set_key(self, option, key):
        """A key for an action; the same key taken from any other action; not the movement keys or Esc."""
        if key in KEYS.MOVES[OPT.get("move_keys")]:
            self.note = "That key moves you"
            return
        if key == pygame.K_e:
            self.note = "E talks to people"
            return
        for other in OPT.DEFAULTS:
            if other.startswith("key_") and other != option and OPT.get(other) == key:
                self.change(other, None)
        self.change(option, key)

    def reset_tab(self):
        OPT.reset([row[0] for row in self.rows])
        for row in self.rows:
            self.on_change(row[0])

    # --- input ------------------------------------------------------------------------------------------------
    def handle(self, events, pos):
        """-> "back" when you leave, else None."""
        self.point_at(pos)
        for event in events:
            if self.waiting:
                self.wait_for_key(event)
                continue
            result = self.key_press(event) if event.type == pygame.KEYDOWN else self.mouse(event, pos)
            if result:
                return result
        if self.rows[self.row][0] != "fullscreen":
            self.restart_asked = False
        return None

    def wait_for_key(self, event):
        if event.type != pygame.KEYDOWN:
            return
        option, self.waiting = self.waiting, None
        if event.key == pygame.K_ESCAPE:
            return
        self.set_key(option, None if event.key in (pygame.K_BACKSPACE, pygame.K_DELETE) else event.key)

    def key_press(self, event):
        key = event.key
        self.note = ""
        if key == pygame.K_ESCAPE:
            return "back"
        if key == pygame.K_TAB or KEYS.pressed(event, "tab"):
            self.switch_tab(1)
        elif key in (pygame.K_UP, KEYS.move_key("up")):
            self.row = (self.row - 1) % len(self.rows)
        elif key in (pygame.K_DOWN, KEYS.move_key("down")):
            self.row = (self.row + 1) % len(self.rows)
        elif key in (pygame.K_LEFT, KEYS.move_key("left")):
            self.cycle(self.row, -1)
        elif key in (pygame.K_RIGHT, KEYS.move_key("right"), pygame.K_RETURN, pygame.K_KP_ENTER):
            self.cycle(self.row, 1)
        return None

    def mouse(self, event, pos):
        for option, slider in self.sliders.items():
            if self.tab_of(option) == self.tab and slider.handle(event, pos):
                return None
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None
        if self.back.rect.collidepoint(pos):
            return "back"
        if self.defaults.rect.collidepoint(pos):
            self.reset_tab()
            return None
        for tab, rect in self.tab_rects.items():
            if rect.collidepoint(pos) and tab != self.tab:
                self.tab, self.row = tab, 0
                self.sfx.play("hover")
                return None
        for i, (left, right) in enumerate(self.arrow_rects):
            if left and left.collidepoint(pos):
                self.row = i
                self.cycle(i, -1)
                return None
            if right and right.collidepoint(pos):
                self.row = i
                self.cycle(i, 1)
                return None
        for i, rect in enumerate(self.row_rects):
            if rect.collidepoint(pos):
                self.row = i
                if self.rows[i][2] != "slider":
                    self.cycle(i, 1)
        return None

    def switch_tab(self, direction):
        self.tab = TABS[(TABS.index(self.tab) + direction) % len(TABS)]
        self.row = 0
        self.sfx.play("hover")

    def point_at(self, pos):
        """Which row the mouse is on (its description shows)."""
        self.pointed = next((i for i, rect in enumerate(self.row_rects) if rect.collidepoint(pos)), None)

    @staticmethod
    def tab_of(option):
        return next(tab for tab, rows in ROWS.items() if any(r[0] == option for r in rows))

    # --- drawing ------------------------------------------------------------------------------------------------
    def draw(self):
        w, h = self.screen.get_size()
        self.screen.blit(self.title, self.title.get_rect(center=(w // 2, int(h * 0.1))))
        self.draw_tabs()
        self.draw_rows()
        self.draw_description()
        self.defaults.draw(self.screen, (w // 10, h - h // 14))
        self.back.draw(self.screen, (w - w // 10, h - h // 14))

    def draw_tabs(self):
        w, h = self.screen.get_size()
        self.tab_rects = {}
        gap = w * TAB_GAP
        total = sum(img.get_width() for img in self.tab_imgs.values()) + gap * (len(TABS) - 1)
        x = w / 2 - total / 2
        for tab in TABS:
            img = self.tab_imgs[tab]
            rect = img.get_rect(midleft=(int(x), int(h * 0.2)))
            x += img.get_width() + gap
            self.tab_rects[tab] = rect
            if tab == self.tab:
                self.screen.blit(img, rect)
                pygame.draw.line(self.screen, FANCY.STYLES["cream"][2], (rect.left + 10, rect.bottom + 4),
                                 (rect.right - 10, rect.bottom + 4), 3)
            else:
                dim = img.copy()
                dim.set_alpha(110 if not rect.collidepoint(pygame.mouse.get_pos()) else 190)
                self.screen.blit(dim, rect)

    def draw_rows(self):
        w, h = self.screen.get_size()
        self.row_rects, self.arrow_rects = [], []
        for i, (option, label, kind, _, _) in enumerate(self.rows):
            cy = int(h * (0.3 + i * ROW_H))
            band = pygame.Rect(int(w * (LEFT - 0.02)), cy - int(h * ROW_H / 2) + 2, int(w * (RIGHT - LEFT + 0.07)),
                               int(h * ROW_H) - 4)
            self.row_rects.append(band)
            if i == self.row:
                shade = pygame.Surface(band.size, pygame.SRCALPHA)
                shade.fill(BAND)
                self.screen.blit(shade, band)
            text = FANCY.fancy(label, int(h * LABEL_SIZE), "cream" if i == self.row else "pale")
            self.screen.blit(text, text.get_rect(midleft=(int(w * LEFT), cy)))
            self.arrow_rects.append(self.draw_value(option, kind, cy))

    def draw_value(self, option, kind, cy):
        """The control on the right of a row. -> (left arrow rect, right arrow rect) or (None, None)."""
        w, h = self.screen.get_size()
        if kind == "slider":
            slider = self.sliders[option]
            slider.place(pygame.Rect(int(w * 0.53), cy - int(h * 0.014), int(w * 0.21), int(h * 0.028)))
            slider.draw(self.screen)
            return None, None
        if kind == "key":
            return self.draw_key(option, cy)
        value = OPT.get(option)
        words = ON_OFF[value] if kind == "toggle" else VALUE_NAMES[option][value]
        self.blit_center(FANCY.fancy(words, int(h * VALUE_SIZE)), int(w * MIDDLE), cy)
        left = self.arrows[0].get_rect(center=(int(w * (MIDDLE - 0.1)), cy))
        right = self.arrows[1].get_rect(center=(int(w * (MIDDLE + 0.1)), cy))
        self.screen.blit(self.arrows[0], left)
        self.screen.blit(self.arrows[1], right)
        return left.inflate(16, 16), right.inflate(16, 16)

    def draw_key(self, option, cy):
        w, h = self.screen.get_size()
        box = pygame.Rect(0, 0, int(w * 0.12), int(h * 0.05))
        box.center = (int(w * MIDDLE), cy)
        waiting = self.waiting == option
        pygame.draw.rect(self.screen, (24, 16, 38), box, 0, 10)
        pygame.draw.rect(self.screen, FANCY.STYLES["cream"][0] if waiting else (120, 96, 160), box, 2, 10)
        words = "..." if waiting else KEYS.key_name(OPT.get(option))
        self.blit_center(FANCY.fancy(words, int(h * VALUE_SIZE), "cream" if OPT.get(option) else "pale"), *box.center)
        return None, None

    def draw_description(self):
        w, h = self.screen.get_size()
        if self.waiting:
            words, colour = KEY_HINT, DESCRIPTION_COLOUR
        elif self.restart_asked:
            words, colour = RESTART_IN_GAME_NOTE, WARNING_COLOUR
        elif self.note:
            words, colour = self.note, WARNING_COLOUR
        elif self.pointed is not None and self.pointed < len(self.rows):
            words, colour = self.rows[self.pointed][4], DESCRIPTION_COLOUR
        else:
            return
        img = FANCY.font(int(h * 0.026)).render(words, True, colour)
        self.blit_center(img, w // 2, int(h * 0.84))

    def blit_center(self, img, cx, cy):
        self.screen.blit(img, img.get_rect(center=(cx, cy)))
