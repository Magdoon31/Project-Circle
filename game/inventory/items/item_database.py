import pygame
from game.inventory.items.weapon import Weapon
from game.inventory.items.armor import Armor
from game.inventory.items.trinket import Trinket

class ItemDatabase:
    def __init__(self,height):
        self.weapons = {

            "Simple Pistol": Weapon("Simple Pistol",
                                    "Simple Pistol to kompaktowe i łatwe w obsłudze\n"
                                    "urządzenie do piaskowania, zaprojektowane z myślą\n"
                                    "o szybkich pracach warsztatowych lub renowacyjnych",
                                    "weapon",4,0.25,None,"None",100,10,25,
                        pygame.transform.scale(pygame.image.load("assets/img/inventory/simple_pistol.png"),(height//10,height//10)).convert_alpha()),
            "Simple Blaster": Weapon("Simple Blaster",
                                    "Simple Blaster to kompaktowe i łatwe w obsłudze\n"
                                    "urządzenie do piaskowania, zaprojektowane z myślą\n"
                                    "o szybkich pracach warsztatowych lub renowacyjnych",
                                    "weapon",8,0.5,None,"None",110,10,20,
                        pygame.transform.scale(pygame.image.load("assets/img/inventory/simple_blaster.png"),(height//10,height//10)).convert_alpha())
        }
        self.armors = {
            "Simple Armor": Armor("Simple Armor",
                                    "Simple Armor to kompaktowe i łatwe w obsłudze\n"
                                    "urządzenie do piaskowania, zaprojektowane z myślą\n"
                                    "o szybkich pracach warsztatowych lub renowacyjnych",
                                    "armor",2,20,None,"None",
                        pygame.transform.scale(pygame.image.load("assets/img/inventory/simple_armor.png"),(height//10,height//10)).convert_alpha())
        }
        self.trinkets = {}


    def get_item(self, name):
        if name in self.weapons:
            return self.weapons[name]
        elif name in self.armors:
            return self.armors[name]
        elif name in self.trinkets:
            return self.trinkets[name]
        else:
            return None