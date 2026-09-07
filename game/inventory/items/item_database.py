import pygame
from game.inventory.items.weapon import Weapon
from game.inventory.items.armor import Armor
from game.inventory.items.trinket import Trinket

class ItemDatabase:
    def __init__(self,height):
        self.img_size = (height // 10, height // 10)
        self.weapons = {

            "Simple Pistol": Weapon("Simple Pistol",
                                    "Starter weapon\nmade by the starter itself,\nmaybe he started this",
                                    "weapon",4,0.23,{},"None",7200,9,18,"normal_red",
                                    self.load_img("weapon/simple_pistol.png")),
            "Simple Blaster": Weapon("Simple Blaster",
                                    "Starter weapon\nmade by the starter itself,\nmaybe he doesn't know about this",
                                    "weapon",30,0.5,{"confusion" : [30], "zap":[2,0.5]},"None",20000,10,25,"laser_blue",
                                    self.load_img("weapon/simple_blaster.png")),
            "Minigun": Weapon("Minigun",
                                    "Shoot really fast\nbut uncontrollably, like everything around",
                                    "weapon",1,0.05,{"zap":[3,1.0]},"Automatic",10000,5,12,"normal_red",
                                    self.load_img("weapon/minigun.png"),True,20),
            "Shotgun R6": Weapon("Shotgun R6",
                                    "Shoots 6 bullets\nin a random pattern at once",
                                    "weapon",10,1.4,{"shotgun_r6" : 1},"None",7200,7,20,"normal_red",
                                    self.load_img("weapon/shotgun_r6.png"),recoil=30),
            "Shotgun S4": Weapon("Shotgun S4",
                                    "Shoots 4 bullets at once",
                                    "weapon",3,0.5,{"shotgun_s4" : 1},"None",9600,6,20,"normal_red",
                                    self.load_img("weapon/shotgun_s4.png"),recoil=20),
            "Bubble Gun": Weapon("Bubble Gun",
                                    "Shoots bubbles that slow down over time.\nRange is short, as is life",
                                    "weapon",5,0.15,{"bubble" : 1, "slow": [30,0.3]},"Slows enemies, Automatic",14000,9,10,"bubble",
                                    self.load_img("weapon/bubble_gun.png"),True,5),
        }
        

        self.armors = {

        # --- VILLAGE ---

            "Leather Chestplate": Armor(
                "Leather Chestplate",
                "A simple chestplate.\nIt's a little dusty, but it gets the job done.",
                "armor", 1, 8,
                {}, "None",
                self.load_img("armor/chestplate1.png")
            ),
            "Vest": Armor(
                "Vest",
                "Better than wearing nothing.\nProbably.",
                "armor", 0, 5,
                {"speed": ["inf", 0.07]}, "Lightweight I\n+7% movement speed",
                self.load_img("armor/vest1.png")
            ),

        # --- RAINBOW FIELDS ---

            "Gladiator's Chestplate": Armor(
                "Gladiator's Chestplate",
                "A sturdier version of the old chestplate.\nLost by the last fallen.",
                "armor", 1, 16,
                {"guard": [1.0, 0.25]}, "Guard I\nAt 100% health, next dmg -25%",
                self.load_img("armor/chestplate2.png")
            ),
            "Medieval Armor I": Armor(
                "Medieval Armor",
                "Old-fashioned armor\n from an old-fashioned world.",
                "armor", 1, 18,
                {}, "None",
                self.load_img("armor/medieval1.png")
            ),
            "Apprentice Armor": Armor(
                "Knight Armor",
                "A small suit of armor.\nProbably made for training.",
                "armor", 2, 10,
                {"berserk": [0.3, 0.15]}, "Berserk I\nIf below 30% health, dmg +15%",
                self.load_img("armor/knight1.png")
            ),

        # --- SUGARWOOD GROVE ---

            "Reinforced Vest": Armor(
                "Reinforced Vest",
                "Almost feels like wearing nothing.",
                "armor", 3, 15,
                {"speed": ["inf", 0.15]}, "Lightweight II\n+15% movement speed",
                self.load_img("armor/vest2.png")
            ),
            "Living Plate": Armor(
                "Living Plate",
                "Soft. Warm. Slightly breathing.",
                "armor", 3, 30,
                {"regen": [0.3, 1]}, "Regen I\nRegenerate up to 30% hp by 1/s",
                self.load_img("armor/living1.png")
            ),
            "Samurai Jacket": Armor(
                "Samurai Jacket",
                "Sweet in touch.\nDon't you think this world is too sweet?",
                "armor", 0, 20,
                {"focus": [120, 0.1, 0.1, 0]}, "Focus I\nAfter 2s without dmg +10% speed and dmg",
                self.load_img("armor/samurai1.png")
            ),

        # --- TOY FACTORY ---

            "Knight Armor": Armor(
                "Knight Armor",
                "Several pieces have been replaced\nby parts that don't seem to\nbelong here.",
                "armor", 4, 45,
                {"berserk": [0.4, 0.2]}, "Berserk II\nIf below 40% health, dmg +20%",
                self.load_img("armor/knight2.png")
            ),
            "Medieval Armor II": Armor(
                "Medieval Armor II",
                "The Core makes the difference\nThe Core of the armor i mean",
                "armor", 5, 40,
                {"poison_imm": []}, "Immune to poison",
                self.load_img("armor/medieval2.png")
            ),
            "Samurai Plating": Armor(
                "Samurai Plating",
                "The material doesn't match anything\nelse found in the factory, wierd...",
                "armor", 0, 40,
                {"focus": [90, 0.1, 0.2, 0]}, "Focus II\nAfter 1.5s without dmg: +10% speed, +20% dmg",
                self.load_img("armor/samurai2.png")
            ),
            "Cyber Suit": Armor(
                "Cyber Suit",
                "Bad idea, worse execution.\nIt reminds me of this world",
                "armor", 10, 0,
                {"bullseye": [0.1]}, "Bullseye I\nimmediately kills an enemy below 10% hp",
                self.load_img("armor/cyber1.png")
            ),
            "Scrap Armor": Armor(
                "Scrap Armor",
                "These pieces are from the core.",
                "armor", 6, 25,
                {"rnd_effect": [480, 0]}, "Randomiser I\nEach 8s gain a random effect",
                self.load_img("armor/scrap.png")
            ),

        # --- SILVERPINE TUNDRA ---

            "Old-World Vest": Armor(
                "Reinforced Vest",
                "Whoever made this cared more\nabout movement than protection.",
                "armor", 2, 40,
                {"speed": ["inf", 0.21]}, "Lightweight III\n+21% movement speed",
                self.load_img("armor/vest3.png")
            ),
            "Golden Chestplate": Armor(
                "Golden Chestplate",
                "It is much heavier than the original.\nThe metal is strangely warm,\ndespite where it was found.",
                "armor", 6, 35,
                {"guard": [0.8, 0.5]}, "Guard II\nIf above 80% health, all dmg -50%",
                self.load_img("armor/chestplate3.png")
            ),
            "Living Armor": Armor(
                "Living Armor",
                "It changes shape when nobody is looking.\nAlmost like this world",
                "armor", 4, 30,
                {"regen": [0.3, 1], "slow_imm": []}, "Regen I\nRegenerate up to 30% hp by 1/s\nImmune to slowness",
                self.load_img("armor/living2.png")
            ),
            "Frost Armor": Armor(
                "Frost Armor",
                "That frost is an attempt to\ndestroy everything before it was too late",
                "armor", 6, 25,
                {"frost": []}, "Frost Aura\nSlows nearby bullets",
                self.load_img("armor/frost.png")
            ),

        # --- UNDERGROUND GARDEN ---

            "Medieval Armor III": Armor(
                "Medieval Armor III",
                "The Core makes the difference\nThe Core of the armor i mean",
                "armor", 8, 65,
                {"poison_imm": [], "glued_imm": [], "weakness_imm": []}, "Immune to poison, glued and weakness",
                self.load_img("armor/medieval3.png")
            ),
            "Plate Armor": Armor(
                "Plate Armor",
                "Probably the most tanky armor in the game",
                "armor", 10, 80,
                {"guard": [0.5, 0.6], "slow": ["inf", 0.25]}, "Guard III\nIf above 50% health, all dmg -60%\nSlowness\n-25% speed",
                self.load_img("armor/knight3.png")
            ),
            "Tribe Armor": Armor(
                "Tribe Armor",
                "It isn't armor.\nYou are wearing it because it allows you to.",
                "armor", 4, 80,
                {"regen": [0.5, 1], "slow_imm": [], "poison_imm": []}, "Regen II\nRegenerate up to 50% hp by 2/s\nImmune to slowness and poison",
                self.load_img("armor/living3.png")
            ),
            "Samurai Armor": Armor(
                "Samurai Armor",
                "Did you ever thought it was meant to last?\nStupid world analogy",
                "armor", 0, 80,
                {"focus": [60, 0.15, 0.3, 0.1]}, "Focus III\nAfter 1s without dmg:\n+15% speed, +30% dmg, +10% fire rate\nImmune to slowness and binded",
                self.load_img("armor/samurai3.png")
            ),
            "Cyber Armor": Armor(
                "Cyber Armor",
                "There is no serial number. There is no manufacturer.",
                "armor", 14, 20,
                {"overclock": [600, 120, 0.4]}, "Overclock I\nEvery 10s gain a fire rate boost for 2s",
                self.load_img("armor/cyber2.png")
            ),

        # --- THE CORE ---

            "Mecha Armor": Armor(
                "Mecha Armor",
                "Is it me or it looks like a lifejacket?",
                "armor", 28, 40,
                {"overclock": [480, 180, 0.4]}, "Overclock II\nEvery 8s gain a fire rate boost for 3s",
                self.load_img("armor/cyber3.png")
            ),
            "Viking Armor": Armor(
                "Viking Armor",
                "Nobody remembers where this armor came from.\nNobody remembers anything honestly",
                "armor", 5, 120,
                {"bullseye": [0.3]}, "Bullseye II\nImmediately kills an enemy below 30% hp",
                self.load_img("armor/viking.png")
            ),
            "Heroic Armor": Armor(
                "Heroic Armor",
                "A costume made for heroes.",
                "armor", 12, 115,
                {"rnd_effect": [480, 1]}, "Randomiser II\nEach 8s gain a random buff",
                self.load_img("armor/heroic.png")
            ),
            "Electro Armor": Armor(
                "Electro Armor",
                "Something inside is still receiving a signal.",
                "armor", 22, 80,
                {"static": [0.25]}, "Static Shock I\nEach time you get hit, deal dmg to all enemies\nequivalent to quater the dmg dealt",
                self.load_img("armor/electro.png")
            ),

        # --- THE VOID ---

            "Mecha-King Armor": Armor(
                "Mecha-King Armor",
                "Milo's best buddy had it\nnow he's dead...",
                "armor", 45, 250,
                {"emergnecy":[1], "confusion_imm": []}, "Emergency Protocol\nIf you die, you do not\nImmune to confusion",
                self.load_img("armor/cyber4.png")
            ),
            "Fallen knight armor": Armor(
                "Armor of the fallen Knight",
                "That's the fallen one\nhe certainly died here",
                "armor", 35, 200,
                {"berserk": [0.6, 0.7], "binded_imm": [], "burn_imm": []}, "Berserk III\nIf below 60% health, dmg +70%\nImmune to binded and burn",
                self.load_img("armor/knight4.png")
            ),

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

    def load_img(self, path):
        img = pygame.image.load(f"assets/img/inventory/{path}").convert_alpha()
        return pygame.transform.scale(img, self.img_size)