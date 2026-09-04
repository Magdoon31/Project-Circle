import pygame

class MapUI:
    def __init__(self, screen):
        self.screen = screen
        self.font_light = {"small" : pygame.font.Font("assets/font/Nexa-ExtraLight.ttf",18),
                            "mid" : pygame.font.Font("assets/font/Nexa-ExtraLight.ttf",36),
                            "large" : pygame.font.Font("assets/font/Nexa-ExtraLight.ttf",64)}
        self.font_heavy = {"small" : pygame.font.Font("assets/font/Nexa-Heavy.ttf",18),
                            "mid" : pygame.font.Font("assets/font/Nexa-Heavy.ttf",36),
                            "large" : pygame.font.Font("assets/font/Nexa-Heavy.ttf",64)}
        self.buttons = []
        self.selected_btn = -1
        self.player = None
        self.page = "map"

        

    def draw(self):
        print(self.selected_btn)
        if self.page != "map":
            self.screen.fill((0, 0, 0))
        self.buttons = []
        if self.page == "map":
            inventory_btn_rect = pygame.Rect(self.screen.get_width() - self.screen.get_width()//6,
                            self.screen.get_height() - self.screen.get_height()//16,
                            self.screen.get_width()//7,
                            self.screen.get_height()//20
                            )
            self.buttons.append(inventory_btn_rect)
            pygame.draw.rect(self.screen,(255,255,255),inventory_btn_rect,0,5)
            inventory_btn_text = self.font_heavy["mid"].render("Inventory",True,(0,0,0))
            self.screen.blit(inventory_btn_text,(inventory_btn_rect.x+inventory_btn_rect.width/2-inventory_btn_text.get_width()/2,inventory_btn_rect.y+inventory_btn_rect.height/2-inventory_btn_text.get_height()/2))

            menu_btn_rect = pygame.Rect(self.screen.get_width() - self.screen.get_width()//6,
                            self.screen.get_height()//16,
                            self.screen.get_width()//14,
                            self.screen.get_height()//22
                            )
            self.buttons.append(menu_btn_rect)
            pygame.draw.rect(self.screen,(255,255,255),menu_btn_rect,0,5)
            menu_btn_text = self.font_heavy["mid"].render("Menu",True,(0,0,0))
            self.screen.blit(menu_btn_text,(menu_btn_rect.x+menu_btn_rect.width/2-menu_btn_text.get_width()/2,menu_btn_rect.y+menu_btn_rect.height/2-menu_btn_text.get_height()/2))

            money_text = self.font_heavy["large"].render(f"{self.player.money}$", True, (255,255,255))
            self.screen.blit(money_text, (self.screen.get_width()//50,self.screen.get_height()//50))

        if self.page == "menu":
            button_width = self.screen.get_width() // 3.9
            button_height = self.screen.get_height() // 15
            button_x = (self.screen.get_width() - button_width) // 2
            button_y_start = self.screen.get_height() // 2.4

            for i in range(4):
                option = ["return", "save", "stats", "quit game"][i]
                button_y = button_y_start + i * (button_height*1.5)
                button_rect = pygame.Rect(button_x, button_y, button_width, button_height,)
                self.buttons.append(button_rect)

                if i == self.selected_btn:
                    pygame.draw.rect(self.screen, (255, 255, 255), button_rect, 0, 10)
                else:
                    pygame.draw.rect(self.screen, (170, 170, 170), button_rect, 0, 10)

                text_surface = self.font_heavy["mid"].render(option.capitalize(), True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=button_rect.center)
                self.screen.blit(text_surface, text_rect)
        elif self.page == "stats":

            back_btn_rect = pygame.Rect(self.screen.get_width() - self.screen.get_width()//6,
                                    self.screen.get_height() - self.screen.get_height()//16,
                                    self.screen.get_width() // 6,
                                    self.screen.get_height() // 20
                                    )
            self.buttons.append(back_btn_rect)
            pygame.draw.rect(self.screen,(255,255,255) if self.selected_btn == len(self.buttons) - 1 else (170, 170, 170),back_btn_rect,0,5)
            back_btn_text = self.font_heavy["mid"].render("Back",True,(0,0,0))
            self.screen.blit(back_btn_text,(back_btn_rect.x+back_btn_rect.width/2-back_btn_text.get_width()/2,back_btn_rect.y+back_btn_rect.height/2-back_btn_text.get_height()/2))


    def handle_click(self,pos,events):
        for event in events:
            for i, btn in enumerate(self.buttons):
                if btn.collidepoint(pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.page == "map":
                            if i == 0:
                                return "inventory"
                            elif i == 1:
                                self.page = "menu"
                        elif self.page == "menu":
                            if i == 0:
                                self.page = "map"
                            elif i == 1:
                                return "save"
                            elif i == 2:
                                self.page = "stats"
                            elif i == 3:
                                return "quit"
                        elif self.page == "stats":
                            if i == 0:
                                self.page = "menu"
                    self.selected_btn = i
            if self.selected_btn in range(len(self.buttons)) and not self.buttons[self.selected_btn].collidepoint(pos):
                self.selected_btn = -1
                            
                        



