import math

import pygame
from game.menu.achivements import Achievements
from game.menu.save_screen import SaveScreen
from game.menu.sprite_button import SpriteButton

MAIN_BUTTON_H = 0.065             # (11.11) the main menu's buttons: share of the screen's height (the whole font height)

class Menu:
    def __init__(self, screen, sfx, music, save_manager, settings_screen):
        self.achievements = Achievements()
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
        self.img = {"title": pygame.image.load("assets/img/menu/main/game_title.png").convert_alpha()}
        self.settings_screen = settings_screen      # (11.11) Settings (settings_screen.py) - the same one as under ESC
        self.title_timer = 0.0
        # (11.11) the same style as every other menu button (tools/make_menu_sprites.py)
        self.btn_img = {name: SpriteButton(name, self.screen.get_height() * MAIN_BUTTON_H, "main").img
                        for name in ("play", "achievements", "settings", "quit")}
        self.back_button = SpriteButton("back", self.screen.get_height() * 0.05)
        self.background = pygame.transform.scale(pygame.image.load("assets/img/menu/main/background.png"),(self.screen.get_width()*1.1,self.screen.get_height()*1.1))
        self.blur_background = pygame.transform.gaussian_blur(self.background, 15)
        self.btn_scales = [1.0, 1.0, 1.0, 1.0]
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
        
        intensity = 30 
        
        shift_x = ((mouse_x / screen_width) - 0.5) * intensity
        shift_y = ((mouse_y / screen_height) - 0.5) * intensity

        pos_x = -shift_x - (self.background.get_width() - screen_width) / 2 - 50
        pos_y = -shift_y - (self.background.get_height() - screen_height) / 2 - 50

        if self.page != "main": 
            self.screen.blit(self.blur_background, (pos_x, pos_y))
            self.draw_blurred_overlay(self.screen)
        else:
            self.screen.blit(self.background, (pos_x, pos_y))

        if self.page == "main":
    # title
            self.title_timer += 0.03

            target_w = self.screen.get_width() // 3
            target_h = self.screen.get_height() // 4

            pulse = 1.0 + (math.sin(self.title_timer) * 0.02) 
            current_w = int(target_w * pulse)
            current_h = int(target_h * pulse)

            angle = math.sin(self.title_timer * 0.7) * 0

            scaled_title = pygame.transform.smoothscale(self.img["title"], (current_w, current_h))

            rotated_title = pygame.transform.rotate(scaled_title, angle)

            desired_x = self.screen.get_width() // 10
            desired_y = self.screen.get_height() // 11
            
            title_rect = rotated_title.get_rect()
            title_rect.topleft = (
                desired_x - (current_w - target_w) // 2,
                desired_y - (current_h - target_h) // 2
            )

            self.screen.blit(rotated_title, title_rect.topleft)

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
                self.screen.blit(animated_img, (button_x, button_y - offset_y))
                
                current_y += base_height + GAP



        elif self.page == "achievements":

            slot_width = self.screen.get_height() // 6
            slot_height = self.screen.get_height() // 6
            slot_x_start = self.screen.get_width() // 9
            slot_y_start = self.screen.get_height() // 6

            for i, achievement in enumerate(self.achievements.achievements.values()):
                slot_x = slot_x_start + (i % 7) * (slot_width*1.2)
                slot_y = slot_y_start + (i // 7) * (slot_height*1.2)
                slot_rect = pygame.Rect(slot_x, slot_y, slot_width, slot_height)
                self.buttons.append(slot_rect)
                if achievement["completed"]:
                    pygame.draw.rect(self.screen, (0, 255, 0), slot_rect, 0, 10)
                else:
                    pygame.draw.rect(self.screen, (170, 170, 170), slot_rect, 0, 10)

        elif self.page == "options":
            self.settings_screen.draw()

        elif self.page == "save_load":
            self.save_screen.draw()

        if self.page == "achievements":

            w, h = self.screen.get_size()
            self.back_button.draw(self.screen, (w - w // 10, h - h // 14))      # (11.11) as on the save screen
            self.buttons.append(self.back_button.rect)
            

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
                                          
                        if page_on_click == "achievements":
                            if i == len(self.buttons) - 1:
                                self.page = "main"
                    self.selected_btn = i
            if self.selected_btn in range(len(self.buttons)) and not self.buttons[self.selected_btn].collidepoint(pos):
                self.selected_btn = -1
                self.last_selected_btn = -1

        return "", 0, False

    def draw_blurred_overlay(self,screen):

        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))