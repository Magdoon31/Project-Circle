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
                                    "weapon",4,0.23,[None],"None",7200,9,18,
                        pygame.transform.scale(pygame.image.load("assets/img/inventory/simple_pistol.png"),(height//10,height//10)).convert_alpha()),
            "Simple Blaster": Weapon("Simple Blaster",
                                    "Simple Blaster to kompaktowe i łatwe w obsłudze\n"
                                    "urządzenie do piaskowania, zaprojektowane z myślą\n"
                                    "o szybkich pracach warsztatowych lub renowacyjnych",
                                    "weapon",8,0.5,[None],"None",20000,10,25,
                        pygame.transform.scale(pygame.image.load("assets/img/inventory/simple_blaster.png"),(height//10,height//10)).convert_alpha()),
            "Minigun": Weapon("Minigun",
                                    "Shoot really fast\nbut uncontrollably",
                                    "weapon",1,0.05,[None],"Automatic",10000,5,12,
                        pygame.transform.scale(pygame.image.load("assets/img/inventory/minigun.png"),(height//10,height//10)).convert_alpha(),True,20),
            "Shotgun R6": Weapon("Shotgun R6",
                                    "Shoots 6 bullets\nin a random pattern at once",
                                    "weapon",10,1.2,["shotgun_r6"],"None",7200,7,20,
                        pygame.transform.scale(pygame.image.load("assets/img/inventory/shotgun_r6.png"),(height//10,height//10)).convert_alpha(),recoil=40),
            "Shotgun S4": Weapon("Shotgun S4",
                                    "Shoots 4 bullets at once",
                                    "weapon",3,0.5,["shotgun_s4"],"None",9600,6,20,
                        pygame.transform.scale(pygame.image.load("assets/img/inventory/shotgun_s4.png"),(height//10,height//10)).convert_alpha(),recoil=20),
            "Bubble Gun": Weapon("Bubble Gun",
                                    "Shoots bubbles that slow down over time",
                                    "weapon",12,0.3,["bubble"],"None",9600,6,10,
                        pygame.transform.scale(pygame.image.load("assets/img/inventory/shotgun_s4.png"),(height//10,height//10)).convert_alpha(),recoil=10),
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