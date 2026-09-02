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
        self.player = None
    def draw(self):
        back_btn_rect = pygame.Rect(self.screen.get_width() - self.screen.get_width()//6,
                        self.screen.get_height() - self.screen.get_height()//16,
                        self.screen.get_width()//7,
                        self.screen.get_height()//20
                        )
        self.buttons.append(back_btn_rect)
        pygame.draw.rect(self.screen,(255,255,255),back_btn_rect,0,5)
        back_btn_text = self.font_heavy["mid"].render("Inventory",True,(0,0,0))
        self.screen.blit(back_btn_text,(back_btn_rect.x+back_btn_rect.width/2-back_btn_text.get_width()/2,back_btn_rect.y+back_btn_rect.height/2-back_btn_text.get_height()/2))
        money_text = self.font_heavy["large"].render(f"{self.player.money}$", True, (255,255,255))
        self.screen.blit(money_text, (self.screen.get_width()//50,self.screen.get_height()//50))

    def handle_click(self,pos,events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, btn in enumerate(self.buttons):
                    if btn.collidepoint(pos):
                        if i == 0:
                            return "inventory"

