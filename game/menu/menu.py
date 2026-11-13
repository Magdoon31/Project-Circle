import math

import pygame
from game.achievements.popup import AchievementPopup
from game.achievements.screen import AchievementsScreen
from game.menu import title_shadow as TITLE
from game.menu.save_screen import SaveScreen
from game.menu.sprite_button import SpriteButton

LAYERS = [("assets/img/menu/background/background_1.png", 30, False),     # (13.11) parallax: (file, px it moves,
          ("assets/img/menu/background/foreground_1.png", 70, True)]      #   has transparency) - back to front
BACK_DEPTH = 30
LAYER_SCALE = 1.1                 # a layer is this much bigger than the screen (room to move)
MENU_BLUR = 15                    # the other pages (saves, settings...): the background blurred
OLD_BACKGROUND = "assets/img/menu/main/background.png"
SHADOW_ALPHA = 200                # (13.11) the soft shadow right under the title's and buttons' letters: how dark,
SHADOW_BLUR = 0.006               #   how soft (share of the screen's height),
SHADOW_GROW = 0.004               #   how far past the letters,
SHADOW_DROP = 0.04                #   and how far down (share of the picture's height)
MAIN_BUTTON_H = 0.065             # (11.11) the main menu's buttons: share of the screen's height (the whole font height)

class Menu:
    def __init__(self, screen, sfx, music, save_manager, settings_screen):
        self.achievements = AchievementsScreen(screen, sfx)        # (13.11) no save open: no progress shown
        self.achievement_popup = AchievementPopup(sfx)           # (13.11) e.g. the ending's ones, after the credits
        self.sfx = sfx
        self.music = music
        self.screen = screen
        self.selected_btn = -1
        self.buttons = []

        self.font_light = {"small" : pygame.font.Font("assets/font/Nexa-ExtraLight.ttf",18),
                            "mid" : pygame.font.Font("assets/font/Nexa-ExtraLight.ttf",36),
                            "large" : pygame.font.Font("assets/font/Nexa-ExtraLight.ttf",64)}
        self.font_heavy = {"small" : pygame.font.Font("assets/font/Nexa-Heavy.ttf",18),
                            "mid" : pygame.font.Font("assets/font/Nexa-Heavy.ttf",36),
                            "big" : pygame.font.Font("assets/font/Nexa-Heavy.ttf",48),
                            "large" : pygame.font.Font("assets/font/Nexa-Heavy.ttf",64)}
        self.page = "main"
        self.img = {"title": load_title()}                         # (13.11) with its shadow baked in
        self.settings_screen = settings_screen      # (11.11) Settings (settings_screen.py) - the same one as under ESC
        self.title_timer = 0.0
        # (11.11) the same style as every other menu button (tools/make_menu_sprites.py)
        self.btn_img = {name: SpriteButton(name, self.screen.get_height() * MAIN_BUTTON_H, "main").img
                        for name in ("play", "achievements", "settings", "quit")}
        self.back_button = SpriteButton("back", self.screen.get_height() * 0.05)
        self.layers = self.load_layers()           # (13.11) the background and the foreground, a parallax
        self.btn_scales = [1.0, 1.0, 1.0, 1.0]
        h = self.screen.get_height()
        self.btn_shadows = {name: letter_shadow(img, h) for name, img in self.btn_img.items()}
        self.save_manager = save_manager

        self.difficulty = 0
        self.new_game = False
        self.save_selected = 0

        self.last_selected_btn = -1
        self.sfx.load_sfx("hover", "assets/sfx/UI/hover.mp3")
        self.save_screen = SaveScreen(screen, sfx, save_manager)     # (11.11) Play: the save slots
        

    def draw(self):
        self.buttons = []
        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen_width, screen_height = self.screen.get_size()
        
        blurred = self.page != "main"
        for sharp, blur, depth in self.layers:            # (13.11) the nearer the layer, the more it moves
            layer = blur if blurred else sharp
            shift_x = ((mouse_x / screen_width) - 0.5) * depth
            shift_y = ((mouse_y / screen_height) - 0.5) * depth
            self.screen.blit(layer, ((screen_width - layer.get_width()) / 2 - shift_x,
                                     (screen_height - layer.get_height()) / 2 - shift_y))
        if blurred:
            self.draw_blurred_overlay(self.screen)

        if self.page == "main":
    # title
            self.title_timer += 0.03

            target_w = self.screen.get_width() // 3
            target_h = self.screen.get_height() // 4

            pulse = 1.0 + (math.sin(self.title_timer) * 0.02) 
            current_w = int(target_w * pulse)
            current_h = int(target_h * pulse)

            angle = math.sin(self.title_timer * 0.7) * 0

            title, pad = self.img["title"]
            pad_x = int(pad * current_w / (title.get_width() - 2 * pad))            # the shadow's room round it
            pad_y = int(pad * current_h / (title.get_height() - 2 * pad))
            scaled_title = pygame.transform.smoothscale(title, (current_w + 2 * pad_x, current_h + 2 * pad_y))

            rotated_title = pygame.transform.rotate(scaled_title, angle)

            desired_x = self.screen.get_width() // 10
            desired_y = self.screen.get_height() // 11
            
            title_rect = rotated_title.get_rect()
            title_rect.topleft = (
                desired_x - (current_w - target_w) // 2,
                desired_y - (current_h - target_h) // 2
            )

            self.screen.blit(rotated_title, (title_rect.x - pad_x, title_rect.y - pad_y))

    # buttons
            
            button_y_start = self.screen.get_height() // 2.2
            options = ["play", "achievements", "settings", "quit"]
            GAP = self.screen.get_height()//60
            current_y = button_y_start
    
            for i, option in enumerate(options):
                base_img = self.btn_img[option]
                base_width = base_img.get_width()
                base_height = base_img.get_height()
                
                target_scale = 1.2 if i == self.selected_btn else 1.0
                self.btn_scales[i] += (target_scale - self.btn_scales[i]) * 0.15
                
                button_x = self.screen.get_width() // 11
                button_y = current_y
                
                scaled_w = int(base_width * self.btn_scales[i])
                scaled_h = int(base_height * self.btn_scales[i])
                
                offset_y = (scaled_h - base_height) // 2
                button_rect = pygame.Rect(button_x, button_y - offset_y, scaled_w, scaled_h)
                self.buttons.append(button_rect)
                
                animated_img = pygame.transform.smoothscale(base_img, (scaled_w, scaled_h))
                self.blit_shadow(self.btn_shadows[option], button_rect)
                self.screen.blit(animated_img, (button_x, button_y - offset_y))
                
                current_y += base_height + GAP



        elif self.page == "achievements":
            self.achievements.draw()                   # (13.11)

        elif self.page == "options":
            self.settings_screen.draw()

        elif self.page == "save_load":
            self.save_screen.draw()

        self.achievement_popup.update_and_draw(self.screen)

    def handle_click(self, pos, events):
        if self.page == "save_load":                     # (11.11) the save screen has its own input
            result = self.save_screen.handle(events, pos)
            if result == ("back",):
                self.page = "main"
            elif result:
                return result
            return "", 0, False
        if self.page == "options":
            if self.settings_screen.handle(events, pos) == "back":
                self.page = "main"
            return "", 0, False
        if self.page == "achievements":                  # (13.11) its own screen (Back / Esc)
            if self.achievements.handle(events, pos) == "back":
                self.page = "main"
            return "", 0, False
        for event in events:
            for i, btn in enumerate(self.buttons):
                if btn.collidepoint(pos):
                    if self.last_selected_btn != i:
                        self.sfx.play("hover")
                        self.last_selected_btn = i
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        page_on_click = self.page   # page changes below must not trigger the Back check
                        if self.page == "main":
                            if i == 0:
                                self.page = "save_load"
                                self.save_screen.open()
                            elif i == 1:
                                self.page = "achievements"
                            elif i == 2:
                                self.page = "options"
                                self.settings_screen.open()
                            elif i == 3:
                                return "quit", 0, False        
                                          
                    self.selected_btn = i
            if self.selected_btn in range(len(self.buttons)) and not self.buttons[self.selected_btn].collidepoint(pos):
                self.selected_btn = -1
                self.last_selected_btn = -1

        return "", 0, False

    def blit_shadow(self, shadow, rect):
        """The shadow (letter_shadow) scaled to where its picture is drawn now (it grows with the hover / pulse)."""
        picture, pad = shadow
        k = rect.width / (picture.get_width() - 2 * pad)
        if abs(k - 1) > 0.01:
            picture = pygame.transform.smoothscale_by(picture, k)
        offset = int(rect.height * SHADOW_DROP)
        self.screen.blit(picture, (rect.x - int(pad * k), rect.y - int(pad * k) + offset))

    def load_layers(self):
        """(13.11) [(picture, its blurred copy, how far it moves with the mouse)] - back to front. The pictures are
        assets/img/menu/background/background_1.png and foreground_1.png (the old single background if missing)."""
        w, h = self.screen.get_size()
        layers = []
        for path, depth, alpha in LAYERS:
            try:
                raw = pygame.image.load(path)
            except (pygame.error, FileNotFoundError):
                continue
            raw = raw.convert_alpha() if alpha else raw.convert()
            picture = pygame.transform.smoothscale(raw, (int(w * LAYER_SCALE), int(h * LAYER_SCALE)))
            layers.append((picture, pygame.transform.gaussian_blur(picture, MENU_BLUR), depth))
        if not layers:
            picture = pygame.transform.smoothscale(pygame.image.load(OLD_BACKGROUND).convert(),
                                                   (int(w * LAYER_SCALE), int(h * LAYER_SCALE)))
            layers.append((picture, pygame.transform.gaussian_blur(picture, MENU_BLUR), BACK_DEPTH))
        return layers

    def draw_blurred_overlay(self,screen):

        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))


def letter_shadow(img, screen_h):
    """(13.11) (a dark, soft copy of a picture's shape, its padding px) - drawn just under the picture."""
    blur, grow = max(1, int(screen_h * SHADOW_BLUR)), max(1, int(screen_h * SHADOW_GROW))
    pad = 2 * blur + grow
    shape = pygame.Surface((img.get_width() + 2 * pad, img.get_height() + 2 * pad), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(img, 40)
    dark = mask.to_surface(setcolor=(0, 0, 0, SHADOW_ALPHA), unsetcolor=(0, 0, 0, 0))
    for dx in range(-grow, grow + 1, max(1, grow)):
        for dy in range(-grow, grow + 1, max(1, grow)):
            shape.blit(dark, (pad + dx, pad + dy))
    return pygame.transform.gaussian_blur(shape, blur), pad


def load_title():
    """(13.11) (the title picture, its shadow's padding px): the one with the shadow if it is there."""
    try:
        return pygame.image.load(TITLE.OUT).convert_alpha(), TITLE.PAD
    except (pygame.error, FileNotFoundError):
        return pygame.image.load(TITLE.SOURCE).convert_alpha(), 0
