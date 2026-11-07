import math

import pygame
from game.menu.achivements import Achievements
from game.menu.save_manager import seed_from_text

SEED_MAX_LENGTH = 24

class Menu:
    def __init__(self, screen, sfx, music,save_manager):
        self.achievements = Achievements()
        self.sfx = sfx
        self.music = music
        self.screen = screen
        self.selected_btn = -1
        self.buttons = []
        self.dragging_music = False
        self.dragging_sfx = False

        self.font_light = {"small" : pygame.font.Font("assets/font/Nexa-ExtraLight.ttf",18),
                            "mid" : pygame.font.Font("assets/font/Nexa-ExtraLight.ttf",36),
                            "large" : pygame.font.Font("assets/font/Nexa-ExtraLight.ttf",64)}
        self.font_heavy = {"small" : pygame.font.Font("assets/font/Nexa-Heavy.ttf",18),
                            "mid" : pygame.font.Font("assets/font/Nexa-Heavy.ttf",36),
                            "big" : pygame.font.Font("assets/font/Nexa-Heavy.ttf",48),
                            "large" : pygame.font.Font("assets/font/Nexa-Heavy.ttf",64)}
        self.page = "main"
        self.img = {"music": pygame.transform.scale(pygame.image.load("assets/img/menu/music_icon.png"), (self.screen.get_height() // 10, self.screen.get_height() // 10)),
                    "sfx": pygame.transform.scale(pygame.image.load("assets/img/menu/sfx_icon.png"), (self.screen.get_height() // 10, self.screen.get_height() // 10)),
                    "title": pygame.image.load("assets/img/menu/game_title.png").convert_alpha()}
        self.title_timer = 0.0
        self.btn_img = {
            "play" : pygame.image.load("assets/img/menu/play_btn.png"),
            "achievements" : pygame.image.load("assets/img/menu/achievements_btn.png"),
            "settings" : pygame.image.load("assets/img/menu/settings_btn.png"),
            "quit" :pygame.image.load("assets/img/menu/quit_btn.png"),
        }
        self.background = pygame.transform.scale(pygame.image.load("assets/img/menu/background.png"),(self.screen.get_width()*1.1,self.screen.get_height()*1.1))
        self.blur_background = pygame.transform.gaussian_blur(self.background, 15)
        self.btn_scales = [1.0, 1.0, 1.0, 1.0]
        self.save_manager = save_manager

        self.difficulty = 0
        self.new_game = False
        self.save_selected = 0

        self.last_selected_btn = -1
        self.sfx.load_sfx("hover", "assets/sfx/UI/hover.mp3")
        self.seed_text = ""           # typed on the difficulty page (empty = random world)
        self.seed_rect = None
        

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
            GAP = self.screen.get_height()//20
            current_y = button_y_start
    
            for i, option in enumerate(options):
                base_img = self.btn_img[option]
                base_width = base_img.get_width()*0.4
                base_height = base_img.get_height()*0.4
                
                target_scale = 1.2 if i == self.selected_btn else 1.0
                self.btn_scales[i] += (target_scale - self.btn_scales[i]) * 0.15
                
                button_x = self.screen.get_width() // 11
                button_y = current_y
                
                scaled_w = int(base_width * self.btn_scales[i])
                scaled_h = int(base_height * self.btn_scales[i])
                
                offset_y = (scaled_h - base_height) // 2
                button_rect = pygame.Rect(button_x, button_y - offset_y, scaled_w, scaled_h)
                self.buttons.append(button_rect)
                
                animated_img = pygame.transform.scale(base_img, (scaled_w, scaled_h))
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
            slider_width = self.screen.get_width() // 4
            slider_height = self.screen.get_height() // 60
            slider_x = (self.screen.get_width() - slider_width) // 2
            slider_y_start = self.screen.get_height() // 4

    #music slider
            music_slider_rect = pygame.Rect(slider_x, slider_y_start*0.95, slider_width, slider_height*2.5)
            self.buttons.append(music_slider_rect)
            pygame.draw.rect(self.screen,(100, 100, 100),(slider_x, slider_y_start, slider_width, slider_height))
            music_circle_x = slider_x + slider_width * self.music.music_volume
            pygame.draw.circle(self.screen, (255, 255, 255), (int(music_circle_x), slider_y_start + slider_height // 2), 15)
            self.screen.blit(self.img["music"], (slider_x - self.img["music"].get_width()*1.2, slider_y_start + slider_height//2 - self.img["music"].get_height()//2))

    #sfx slider
            sfx_slider_rect = pygame.Rect(slider_x, slider_y_start*0.95 + slider_height*6, slider_width, slider_height*2.5)
            self.buttons.append(sfx_slider_rect)
            pygame.draw.rect(self.screen,(100, 100, 100),(slider_x, slider_y_start + slider_height*6, slider_width, slider_height))
            sfx_circle_x = slider_x + slider_width * self.sfx.sfx_volume
            pygame.draw.circle(self.screen, (255, 255, 255), (int(sfx_circle_x), slider_y_start + slider_height*6 + slider_height // 2), 15)
            self.screen.blit(self.img["sfx"], (slider_x - self.img["sfx"].get_width()*1.2, slider_y_start + slider_height*6 + slider_height//2 - self.img["sfx"].get_height()//2))

        elif self.page == "save_load":

            save_slot_width = self.screen.get_width() // 7.5
            save_slot_height = self.screen.get_height() // 4
            save_slot_x_start = self.screen.get_width() // 3.6
            save_slot_y = self.screen.get_height() // 3
            
            for i in range(3):

                save_text, hard_mode = self.save_manager.get_save_info(i+1)
                slot_x = save_slot_x_start + i * (save_slot_width*1.2)
                color = 1.5 if hard_mode else 1
                save_slot_rect = pygame.Rect(slot_x, save_slot_y, save_slot_width, save_slot_height)
                self.buttons.append(save_slot_rect)

                pygame.draw.rect(self.screen, (170, 170//color, 170//color) if self.selected_btn != i else (255,255//color,255//color), save_slot_rect, 0, 10)
                for i, text in enumerate(save_text):
                    slot_text = self.font_heavy["mid"].render(text,True,(0,0,0))
                    self.screen.blit(slot_text,(slot_x + (save_slot_width - slot_text.width)//2,save_slot_y+(i*save_slot_height)//5))

        elif self.page == "new_game":
            button_width = self.screen.get_width() // 3.9
            button_height = self.screen.get_height() // 11
            button_x = (self.screen.get_width() - button_width) // 2
            button_y_start = self.screen.get_height() // 2.4

            for i, text in enumerate(["New Game","Continue"]):

                button = pygame.Rect(button_x,button_y_start+(i*button_height*1.5),button_width,button_height)
                self.buttons.append(button)

                pygame.draw.rect(self.screen,(170,170,170) if self.selected_btn != i else (255,255,255),button,0,10)
                btn_text = self.font_heavy["mid"].render(text,True,(0,0,0))

                btn_text_rect = btn_text.get_rect(center=button.center)
                self.screen.blit(btn_text, btn_text_rect)

        elif self.page == "difficulty":

            button_width = self.screen.get_width() // 3.9
            button_height = self.screen.get_height() // 11
            button_x = (self.screen.get_width() - button_width) // 2
            button_y_start = self.screen.get_height() // 2.4

            for i, text in enumerate(["Normal","Hard Mode"]):

                button = pygame.Rect(button_x,button_y_start+(i*button_height*1.5),button_width,button_height)
                self.buttons.append(button)

                pygame.draw.rect(self.screen,(170,170,170) if self.selected_btn != i else (255,255,255),button,0,10)
                btn_text = self.font_heavy["mid"].render(text,True,(0,0,0))

                btn_text_rect = btn_text.get_rect(center=button.center)
                self.screen.blit(btn_text, btn_text_rect)
            self.draw_seed_field(button_x, button_y_start + 2 * button_height * 1.5 + button_height * 0.3, button_width, button_height)

        if self.page in ("achievements", "options", "save_load", "new_game", "difficulty"):

            back_btn_rect = pygame.Rect(self.screen.get_width() - self.screen.get_width()//6,
                                    self.screen.get_height() - self.screen.get_height()//16,
                                    self.screen.get_width() // 6,
                                    self.screen.get_height() // 20
                                    )
            self.buttons.append(back_btn_rect)
            pygame.draw.rect(self.screen,(255,255,255) if self.selected_btn == len(self.buttons) - 1 else (170, 170, 170),back_btn_rect,0,5)
            back_btn_text = self.font_heavy["mid"].render("Back",True,(0,0,0))
            self.screen.blit(back_btn_text,(back_btn_rect.x+back_btn_rect.width/2-back_btn_text.get_width()/2,back_btn_rect.y+back_btn_rect.height/2-back_btn_text.get_height()/2))
            

    def draw_seed_field(self, x, y, width, height):
        # text field for the world seed: just type (letters or numbers), empty = random
        label = self.font_heavy["small"].render("SEED  (empty = random world)", True, (230, 230, 230))
        self.screen.blit(label, (x, y))
        rect = pygame.Rect(x, y + label.get_height() + 6, width, height * 0.8)
        self.seed_rect = rect
        pygame.draw.rect(self.screen, (40, 40, 48), rect, 0, 10)
        pygame.draw.rect(self.screen, (170, 170, 170), rect, 2, 10)
        if self.seed_text:
            text = self.font_heavy["mid"].render(self.seed_text, True, (255, 255, 255))
        else:
            text = self.font_light["mid"].render("random", True, (120, 120, 130))
        text_rect = text.get_rect(midleft=(rect.x + 16, rect.centery))
        self.screen.blit(text, text_rect)
        if pygame.time.get_ticks() // 500 % 2 == 0:      # blinking cursor
            cursor_x = text_rect.right + 4 if self.seed_text else rect.x + 16
            pygame.draw.line(self.screen, (255, 255, 255), (cursor_x, rect.y + rect.height * 0.25), (cursor_x, rect.y + rect.height * 0.75), 2)

    def handle_seed_typing(self, event):
        if event.type == pygame.TEXTINPUT:
            for char in event.text:
                if char.isprintable() and len(self.seed_text) < SEED_MAX_LENGTH:
                    self.seed_text += char
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.seed_text = self.seed_text[:-1]
            elif event.key == pygame.K_DELETE:
                self.seed_text = ""

    def choose_seed(self):
        # called when a new game starts: the save manager uses it for the new world
        text = self.seed_text.strip()
        self.save_manager.pending_seed = (seed_from_text(text), text)
        self.seed_text = ""
        pygame.key.stop_text_input()

    def handle_click(self, pos, events):
        for event in events:
            if self.page == "difficulty":
                self.handle_seed_typing(event)
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
                            elif i == 1:
                                self.page = "achievements"
                            elif i == 2:
                                self.page = "options"
                            elif i == 3:
                                return "quit", 0, False        
                                          
                        elif self.page == "save_load":
                            if i in (0,1,2):  
                                self.save_selected = i+1
                                if self.save_manager.get_save_info(self.save_selected)[0][-1] == "EMPTY":
                                    self.page = "difficulty"
                                    pygame.key.start_text_input()
                                else:  
                                    self.page = "new_game"

                        elif self.page == "new_game":  
                            if i == 0:
                                self.page = "difficulty"
                                pygame.key.start_text_input()
                            elif i == 1:
                                return "start_game", self.save_selected, self.save_manager.get_save_info(self.save_selected)[1]
                            elif i == 2:
                                self.page = "save_load"
                                self.save_selected = 0
                        elif self.page == "difficulty":
                            if i == 0:
                                self.save_manager.reset_data(self.save_selected)
                                self.choose_seed()
                                return "start_game", self.save_selected, False
                            elif i == 1:
                                self.save_manager.reset_data(self.save_selected)
                                self.choose_seed()
                                return "start_game", self.save_selected, True
                            elif i == 2:
                                self.page = "save_load"
                                self.save_selected = 0
                        if page_on_click in ("achievements", "options", "save_load"):
                            if i == len(self.buttons) - 1:
                                self.page = "main"
                    self.selected_btn = i
            if self.selected_btn in range(len(self.buttons)) and not self.buttons[self.selected_btn].collidepoint(pos):
                self.selected_btn = -1
                self.last_selected_btn = -1

            if self.page == "options":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.buttons[0].collidepoint(pos):
                        self.dragging_music = True
                        mouse_x = pos[0]
                        self.music.music_volume = (mouse_x - self.buttons[0].x) / self.buttons[0].width
                        self.music.music_volume = max(0.0, min(1.0, self.music.music_volume))
                        self.music.update_volume()

                    elif self.buttons[1].collidepoint(pos):
                        self.dragging_sfx = True
                        mouse_x = pos[0]
                        self.sfx.sfx_volume = (mouse_x - self.buttons[1].x) / self.buttons[1].width
                        self.sfx.sfx_volume = max(0.0, min(1.0, self.sfx.sfx_volume))
                        self.sfx.update_volume()

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.dragging_music = False
                        self.dragging_sfx = False
            
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging_music:
            
                        mouse_x = pos[0]
                        self.music.music_volume = (mouse_x - self.buttons[0].x) / self.buttons[0].width
                        self.music.music_volume = max(0.0, min(1.0, self.music.music_volume))

                        self.music.update_volume()
            
            
                    elif self.dragging_sfx:
            
                        mouse_x = pos[0]
                        self.sfx.sfx_volume = (mouse_x - self.buttons[1].x) / self.buttons[1].width
                        self.sfx.sfx_volume = max(0.0, min(1.0, self.sfx.sfx_volume))

                        self.sfx.update_volume()

        return "", 0, False

    def draw_blurred_overlay(self,screen):

        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))