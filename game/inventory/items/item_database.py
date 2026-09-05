import pygame
from game.inventory.items.weapon import Weapon
from game.inventory.items.armor import Armor
from game.inventory.items.trinket import Trinket

class ItemDatabase:
    def __init__(self,height):
        self.weapons = {

            "Simple Pistol": Weapon("Simple Pistol",
                                    "Starter weapon\nmade by the starter itself,\nmaybe he started this",
                                    "weapon",4,0.23,{},"None",7200,9,18,(255,255,255),
                        pygame.transform.scale(pygame.image.load("assets/img/inventory/simple_pistol.png"),(height//10,height//10)).convert_alpha()),
            "Simple Blaster": Weapon("Simple Blaster",
                                    "Starter weapon\nmade by the starter itself,\nmaybe he doesn't know about this",
                                    "weapon",80,0.5,{},"None",20000,10,25,(120,60,200),
                        pygame.transform.scale(pygame.image.load("assets/img/inventory/simple_blaster.png"),(height//10,height//10)).convert_alpha()),
            "Minigun": Weapon("Minigun",
                                    "Shoot really fast\nbut uncontrollably, like everything around",
                                    "weapon",1,0.05,{},"Automatic",10000,5,12,(200,50,50),
                        pygame.transform.scale(pygame.image.load("assets/img/inventory/minigun.png"),(height//10,height//10)).convert_alpha(),True,20),
            "Shotgun R6": Weapon("Shotgun R6",
                                    "Shoots 6 bullets\nin a random pattern at once",
                                    "weapon",10,1.4,{"shotgun_r6" : 1},"None",7200,7,20,(255,255,255),
                        pygame.transform.scale(pygame.image.load("assets/img/inventory/shotgun_r6.png"),(height//10,height//10)).convert_alpha(),recoil=40),
            "Shotgun S4": Weapon("Shotgun S4",
                                    "Shoots 4 bullets at once",
                                    "weapon",3,0.5,{"shotgun_s4" : 1},"None",9600,6,20,(255,255,255),
                        pygame.transform.scale(pygame.image.load("assets/img/inventory/shotgun_s4.png"),(height//10,height//10)).convert_alpha(),recoil=20),
            "Bubble Gun": Weapon("Bubble Gun",
                                    "Shoots bubbles that slow down over time.\nRange is short, as is life",
                                    "weapon",5,0.15,{"bubble" : 1, "slow": [0.5,0.3]},"Slows enemies, Automatic",14000,9,10,(20,100,200),
                        pygame.transform.scale(pygame.image.load("assets/img/inventory/bubble_gun.png"),(height//10,height//10)).convert_alpha(),True,10),
        }
        self.armors = {
            # "Simple Armor": Armor("Simple Armor",
            #                         "",
            #                         "armor",2,20,None,"None",
            #             pygame.transform.scale(pygame.image.load("assets/img/inventory/simple_armor.png"),(height//10,height//10)).convert_alpha())
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