import pygame
from game.menu.achivements import Achievements

class Menu:
    def __init__(self, screen, sfx, music):
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
                    "sfx": pygame.transform.scale(pygame.image.load("assets/img/menu/sfx_icon.png"), (self.screen.get_height() // 10, self.screen.get_height() // 10))}
        
        

    def draw(self):
        self.buttons = []
        self.screen.fill((0, 0, 0))
        if self.page == "main":
            button_width = self.screen.get_width() // 3.9
            button_height = self.screen.get_height() // 11
            button_x = (self.screen.get_width() - button_width) // 2
            button_y_start = self.screen.get_height() // 2.4

            for i in range(4):
                option = ["start game", "achievements", "options", "quit"][i]
                button_y = button_y_start + i * (button_height*1.2)
                button_rect = pygame.Rect(button_x, button_y, button_width, button_height,)
                self.buttons.append(button_rect)

                if i == self.selected_btn:
                    pygame.draw.rect(self.screen, (255, 255, 255), button_rect, 0, 10)
                else:
                    pygame.draw.rect(self.screen, (170, 170, 170), button_rect, 0, 10)

                text_surface = self.font_heavy["big"].render(option.capitalize(), True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=button_rect.center)
                self.screen.blit(text_surface, text_rect)


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
                print(achievement)
                if achievement["completed"]:
                    pygame.draw.rect(self.screen, (0, 255, 0), slot_rect, 0, 10)
                else:
                    pygame.draw.rect(self.screen, (170, 170, 170), slot_rect, 0, 10)
            back_btn_rect = pygame.Rect(self.screen.get_width() - self.screen.get_width()//6,
                        self.screen.get_height() - self.screen.get_height()//16,
                        self.screen.get_width() // 6,
                        self.screen.get_height() // 20
                        )
            self.buttons.append(back_btn_rect)
            pygame.draw.rect(self.screen,(255,255,255) if self.selected_btn == len(self.buttons) - 1 else (170, 170, 170),back_btn_rect,0,5)
            back_btn_text = self.font_heavy["mid"].render("Back",True,(0,0,0))
            self.screen.blit(back_btn_text,(back_btn_rect.x+back_btn_rect.width/2-back_btn_text.get_width()/2,back_btn_rect.y+back_btn_rect.height/2-back_btn_text.get_height()/2))

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

            back_btn_rect = pygame.Rect(self.screen.get_width() - self.screen.get_width()//6,
                                    self.screen.get_height() - self.screen.get_height()//16,
                                    self.screen.get_width() // 6,
                                    self.screen.get_height() // 20
                                    )
            self.buttons.append(back_btn_rect)
            pygame.draw.rect(self.screen,(255,255,255) if self.selected_btn == len(self.buttons) - 1 else (170, 170, 170),back_btn_rect,0,5)
            back_btn_text = self.font_heavy["mid"].render("Back",True,(0,0,0))
            self.screen.blit(back_btn_text,(back_btn_rect.x+back_btn_rect.width/2-back_btn_text.get_width()/2,back_btn_rect.y+back_btn_rect.height/2-back_btn_text.get_height()/2))

    def handle_click(self, pos, events):
        for event in events:
            for i, btn in enumerate(self.buttons):
                if btn.collidepoint(pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.page == "main":
                            if i == 0:
                                return "start_game"
                            elif i == 1:
                                return "achievements"
                            elif i == 2:
                                return "options"
                            elif i == 3:
                                return "quit"
                        elif self.page == "achievements":
                            if i == len(self.buttons) - 1:
                                return "main"
                        elif self.page == "options":
                            if i == len(self.buttons) - 1:
                                return "main"
                    self.selected_btn = i
            if self.selected_btn in range(len(self.buttons)) and not self.buttons[self.selected_btn].collidepoint(pos):
                self.selected_btn = -1

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
        