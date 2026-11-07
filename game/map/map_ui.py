import pygame

# bright biomes: the text on the map (money, biome, quests) is drawn black there so it stays readable
BRIGHT_BIOMES = {"silverpine_tundra", "lunapark"}

class MapUI:
    def __init__(self, screen, sfx):
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
        self.sfx = sfx
        self.message = ""        # short info on the map, e.g. "Inventory full - item sold"
        self.message_timer = 0
        self.quests = None       # Game's QuestLog - short list under the Menu button
        self.font_quest = (pygame.font.Font("assets/font/Nexa-Heavy.ttf", max(14, screen.get_height() // 52)),
                           pygame.font.Font("assets/font/Nexa-ExtraLight.ttf", max(13, screen.get_height() // 58)))
        self.quest_note = ""     # "New Quest: ..." at the bottom of the screen
        self.quest_timer = 0
        self.saved_text = ""     # small autosave note in the bottom-left corner
        self.saved_timer = 0
        

        

    def draw(self):
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

            menu_btn_rect = pygame.Rect(self.screen.get_width() - self.screen.get_width()//10,
                            self.screen.get_height()//25,
                            self.screen.get_width()//14,
                            self.screen.get_height()//22
                            )
            self.buttons.append(menu_btn_rect)
            pygame.draw.rect(self.screen,(255,255,255),menu_btn_rect,0,5)
            menu_btn_text = self.font_heavy["mid"].render("Menu",True,(0,0,0))
            self.screen.blit(menu_btn_text,(menu_btn_rect.x+menu_btn_rect.width/2-menu_btn_text.get_width()/2,menu_btn_rect.y+menu_btn_rect.height/2-menu_btn_text.get_height()/2))

            # the shop (game/shop): left of the Inventory button (key B does the same)
            shop_btn_rect = pygame.Rect(inventory_btn_rect.x - self.screen.get_width()//10 - self.screen.get_width()//80,
                            inventory_btn_rect.y, self.screen.get_width()//10, inventory_btn_rect.height)
            self.buttons.append(shop_btn_rect)
            pygame.draw.rect(self.screen,(255,255,255),shop_btn_rect,0,5)
            shop_btn_text = self.font_heavy["mid"].render("Shop",True,(0,0,0))
            self.screen.blit(shop_btn_text,(shop_btn_rect.x+shop_btn_rect.width/2-shop_btn_text.get_width()/2,shop_btn_rect.y+shop_btn_rect.height/2-shop_btn_text.get_height()/2))

            text_color = (0, 0, 0) if self.player.biome in BRIGHT_BIOMES else (255, 255, 255)
            money_text = self.font_heavy["large"].render(f"{self.player.money}$", True, text_color)
            self.screen.blit(money_text, (self.screen.get_width()//50,self.screen.get_height()//50))
            biome_text = self.font_heavy["mid"].render(self.player.biome.replace("_", " ").title(), True, text_color)
            self.screen.blit(biome_text, (self.screen.get_width()//50, self.screen.get_height()//50 + money_text.get_height()))

            self.draw_quest_list(menu_btn_rect, text_color)

            if self.message_timer > 0:
                self.message_timer -= 1
                message_text = self.font_heavy["mid"].render(self.message, True, (255,255,255))
                message_text.set_alpha(min(255, self.message_timer * 6))   # fades out at the end
                self.screen.blit(message_text, (self.screen.get_width()//2 - message_text.get_width()//2, self.screen.get_height()//1.25))

            if self.quest_timer > 0:
                self.quest_timer -= 1
                note = self.font_heavy["mid"].render(self.quest_note, True, (255, 230, 60))
                plate = pygame.Rect(0, 0, note.get_width() + 40, note.get_height() + 16)
                plate.midbottom = (self.screen.get_width() // 2, self.screen.get_height() - self.screen.get_height() // 40)
                panel = pygame.Surface(plate.size, pygame.SRCALPHA)
                panel.fill((0, 0, 0, 170))
                panel.set_alpha(min(255, self.quest_timer * 6))
                note.set_alpha(min(255, self.quest_timer * 6))
                self.screen.blit(panel, plate.topleft)
                self.screen.blit(note, note.get_rect(center=plate.center))

            if self.saved_timer > 0:
                self.saved_timer -= 1
                saved = self.font_light["mid"].render(self.saved_text, True, (230, 230, 230))
                saved.set_alpha(min(255, self.saved_timer * 6))
                self.screen.blit(saved, (self.screen.get_width()//50, self.screen.get_height() - saved.get_height() - self.screen.get_height()//40))

        if self.page == "menu":
            button_width = self.screen.get_width() // 3.9
            button_height = self.screen.get_height() // 15
            button_x = (self.screen.get_width() - button_width) // 2
            button_y_start = self.screen.get_height() // 2.6

            for i in range(5):
                option = ["return", "save", "stats", "main menu", "quit game"][i]
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


    def draw_quest_list(self, below, color):
        # active quests, small, without a background, right under the Menu button (right-aligned)
        if not self.quests or not self.quests.active:
            return
        title_font, text_font = self.font_quest
        right = below.right
        y = below.bottom + self.screen.get_height() // 60
        accent = (150, 110, 0) if color == (0, 0, 0) else (255, 230, 60)
        max_width = self.screen.get_width() // 7
        for name, step in self.quests.entries():
            img = title_font.render(name, True, accent)
            self.screen.blit(img, (right - img.get_width(), y))
            y += img.get_height() + 2
            # every sentence starts on a new row, long sentences are wrapped
            sentences = [p.strip() + ("." if not p.strip().endswith((".", "!", "?")) else "") for p in step.split(". ") if p.strip()]
            for line in (row for sentence in sentences for row in self._wrap(sentence, text_font, max_width)):
                img = text_font.render(line, True, color)
                self.screen.blit(img, (right - img.get_width(), y))
                y += img.get_height()
            y += self.screen.get_height() // 90

    def _wrap(self, text, font, width):
        lines, current = [], ""
        for word in text.split(" "):
            test = word if not current else current + " " + word
            if font.size(test)[0] <= width or not current:
                current = test
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def show_quest_note(self, text, frames=240):
        self.quest_note = text
        self.quest_timer = frames

    def show_saved(self, text="Saving...", frames=100):
        self.saved_text = text
        self.saved_timer = frames

    def show_message(self, text, frames=180):
        self.message = text
        self.message_timer = frames

    def handle_click(self,pos,events):
        for event in events:
            for i, btn in enumerate(self.buttons):
                if btn.collidepoint(pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.sfx.play("use")
                        if self.page == "map":
                            if i == 0:
                                return "inventory"
                            elif i == 1:
                                self.page = "menu"
                            elif i == 2:
                                return "shop"
                        elif self.page == "menu":
                            if i == 0:
                                self.page = "map"
                            elif i == 1:
                                return "save"
                            elif i == 2:
                                self.page = "stats"
                            elif i == 3:
                                return "menu"
                            elif i == 4:
                                return "quit"
                        elif self.page == "stats":
                            if i == 0:
                                self.page = "menu"
                    self.selected_btn = i
            if self.selected_btn in range(len(self.buttons)) and not self.buttons[self.selected_btn].collidepoint(pos):
                self.selected_btn = -1
                            
                        



