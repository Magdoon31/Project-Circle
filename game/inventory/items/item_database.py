import pygame, copy
from game.inventory.items.weapon import Weapon
from game.inventory.items.armor import Armor
from game.inventory.items.trinket import Trinket

# EFFECTS: (time in frames)
# slow : [time,-speed%], poison : [time,dmg] /s, weakness : [time,-dmg%], glued : [time,-rate_of_fire%],
# confusion : [time,%chance] (reverse controls), binded : [time,%chance] (can't attack), burn : [time,dmg]/0.25s, acid : [time,-def%]
# PROJECTILE:
# bubble : [slow_rate] (slows overtime), homing : [turn_speed], explosion : [radius,%dmg], 
# zap : [e_zapped-e_hit,%dmg], pierce : [e_pirced-e_hit]

class ItemDatabase:
    def __init__(self,height):
        self.img_size = (height // 10, height // 10)
        self.weapons = {
        # BALANCE (6.11, see the project's BALANCE.md): only the DAMAGE (and poison/burn dmg) was changed.
        # Base DPS grows x3 per biome level (village 12, rainbow 36, sugarwood 108, factory/tundra 324, garden 972,
        # core 2916, void 8748); each weapon = base x its multiplier (0.7 weakest ... 1.45 best, factory up to 1.5).
        # The weakest weapon of a biome is ~6% better than the best one of the biome before.
        # (the "NN DPS ... | Np" notes under each weapon are the author's old values / points;
        #  "weight" = the new value of the weapon = its target DPS (base x multiplier) - shop prices will be based on it)

        # --- VILLAGE ---   3

            "Simple Pistol": Weapon("Simple Pistol",
                                    "Starter weapon made by the starter itself,\nI think he knows",
                                    "weapon",2.4,0.25,{},"Short range, more damage",5500,10,10,["normal_red"],
                                    self.load_img("weapon/simple_pistol.png"),recoil=5),
                                    # 12 DPS -1R              |   11p   |   weight 10
            "Simple Blaster": Weapon("Simple Blaster",
                                    "Starter weapon made by the starter itself,\nmaybe he doesn't know about this",
                                    "weapon",4.2,0.5,{},"Long range, easier to use",13000,12,18,["laser_red"],
                                    self.load_img("weapon/simple_blaster.png")),
                                    # 10 DPS +6R                |   16p   |   weight 8
            "Flintlock": Weapon("Flintlock",
                                    "An ancient-looking weapon that\nsomehow hasn't fallen apart yet.",
                                    "weapon",14.7,1.05,{"burn":[30,1.8]},"Small Burn",10500,14,16,["normal_red"],
                                    self.load_img("weapon/flintlock.png")),
                                    # 8 DPS + 3Burn + 5R        |   16p   |   weight 17
            "Toy Rifle": Weapon("Toy Rifle",
                                    "It looks like a toy. It doesn't behave like one.",
                                    "weapon",3.5,0.2,{},"Automatic",9200,12,16,["laser_blue","laser_green","laser_red","laser_purple"],
                                    self.load_img("weapon/toy_rifle.png"),True,8),
                                    # 15 DPS +2Auto +2.4R       |   19p   |   weight 17
            "Old Pistol": Weapon("Old Pistol",
                                    "It's so old that even Milo doesn't remember it",
                                    "weapon",9.2,1.0,{"poison":[60,3.4]},"Small Poison",9400,13,13,["bullet_green"],
                                    self.load_img("weapon/old_pistol.png")),
                                    # 8 DPS + 3Poison + 2.8R    |   14p   |   weight 13

        # --- RAINBOW FIELDS ---    6

            "Water Hose": Weapon("Water Hose",
                                    "It's just a hose. Right?",
                                    "weapon",1.0,0.04,{"bubble" : [0.4]},"Automatic",8800,16,16,["water"],
                                    self.load_img("weapon/hose1.png"),True,10),
                                    # 25 DPS +2Auto             |   27p   |   weight 25
            "Rifle A2": Weapon("Rifle A2",
                                    "A sturdy little rifle.\nThe markings suggest it was mass-produced.",
                                    "weapon",17.2,0.33,{"burst":[3,0.06]},"Automatic\n3-round bursts",10200,10,16,["bullet_red"],
                                    self.load_img("weapon/rifle_a2.png"),True),
                                    # 30 DPS +2Auto +4.4R       |   36p   |   weight 52
            "Normal Blaster": Weapon("Normal Blaster",
                                    "A colorful blaster with a surprisingly serious design.",
                                    "weapon",24,0.45,{"pierce" : [1]},"Pierces one enemy",12200,16,22,["laser_blue"],
                                    self.load_img("weapon/blaster1.png")),
                                    # 22 DPS +6Pierce +8.4R    |   36p   |   weight 52
            "Finger Gun": Weapon("Finger Gun",
                                    "You point. It shoots. Nobody knows why.",
                                    "weapon",38,1.0,{},"None",10200,16,20,["normal_red"],
                                    self.load_img("weapon/finger_gun.png")),
                                    # 30 DPS +4.4R              |   34p   |   weight 38

        # --- SUGARWOOD GROVE ---   9

            "Glue Gun": Weapon("Glue Gun",
                                    "The label says 'NOT FOR TREES'.\nSomeone has ignored that warning many times.",
                                    "weapon",78,0.5,{"glued" : [90,0.33]},"Glue: -33% fire rate to hit enemies",9600,18,12,["normal_yellow"],
                                    self.load_img("weapon/glue_gun.png")),
                                    # 40 DPS + 6Glued +3.2R     |   49p   |   weight 157
            "Shotgun S4": Weapon("Shotgun S4",
                                    "Four Barrels...\nThey're all loaded and ready to go.",
                                    "weapon",13.5,0.5,{"shotgun" : ["s",4]},"None",8000,15,18,["normal_red"],
                                    self.load_img("weapon/shotgun_s4.png"),recoil=30),
                                    # 44 DPS *0.8Recoil         |   35p   |   weight 76
            "Laser SMG": Weapon("Laser SMG",
                                    "Military weapon for god knows what.",
                                    "weapon",39,0.3,{"pierce" : [1], "burst":[3,0.06]},"Pierces one enemy\n3-round bursts",10600,16,22,["laser_blue"],
                                    self.load_img("weapon/laser_smg1.png"),True),
                                    # 33 DPS +9Pierce +5.2R     |   47p   |   weight 130
            "Bubble Gun": Weapon("Bubble Gun",
                                    "Cute bubbles. Cute colors.\nSomething about them feels strangely familiar.",
                                    "weapon",31,0.2,{"bubble":[0.25],"slow":[60,0.3]},"Slows enemies",10200,17,11,["bubble"],
                                    self.load_img("weapon/bubble_gun.png"),True,10),
                                    # 40 DPS +5Slow +2.2R       |   47p   |   weight 157
            "Hand Cannon": Weapon("Hand Cannon",
                                    "Ridiculously large and heavy.\nAlmost completely impractical.",
                                    "weapon",150,1.5,{},"None",10000,25,8,["normal_red"],
                                    self.load_img("weapon/hand_cannon.png")),
                                    # 33 DPS +4R                |   37p   |   weight 103

        # --- TOY FACTORY ---   12

            "Laser Cannon": Weapon("Laser Cannon",
                                    "The casing says it was manufactured as a toy.\nThe power requirements suggest otherwise.",
                                    "weapon",530,1.5,{"pierce":[2]},"Pierces 2 enemies",15000,27,8,["normal_blue"],
                                    self.load_img("weapon/laser_cannon1.png")),
                                    # 47 DPS +24Pierce +14R         |   85p   |   weight 356
            "Poison Gun": Weapon("Poison Gun",
                                    "The green liquid inside\nis not listed in the factory inventory.",
                                    "weapon",130,0.55,{"poison":[130,21]},"Poisons enemies",10000,14,18,["spore","normal_green","flower_green"],
                                    self.load_img("weapon/poison_gun.png")),
                                    # 48 DPS +12Poison +4R          |   64p   |   weight 259
            "Rifle A4": Weapon("Rifle A4",
                                    "An updated model.\nThe original design has been\nmodified more times than the label admits.",
                                    "weapon",120,0.25,{"burst":[3,0.06]},"Automatic\n3-round bursts",12300,10,18,["bullet_red"],
                                    self.load_img("weapon/rifle_a4.png"),True,4),
                                    # 76 DPS +8.6R                  |   85p   |   weight 486
            "Taser": Weapon("Taser",
                                    "The instructions say:\n'DO NOT CONNECT TO CORE SYSTEM'.",
                                    "weapon",130,0.45,{"zap":[2,0.5]},"Zaps 2 additional enemies for 50% dmg",9200,12,20,["normal_blue"],
                                    self.load_img("weapon/taser.png")),
                                    # 53 DPS +12Zap +2.4R           |   67p   |   weight 292
            "Hunter's Sniper": Weapon("Hunter's Sniper",
                                    "Made for targets that want to stay still.\nThe scope has marks engraved around it.",
                                    "weapon",740,1.9,{},"None",22000,18,36,["bullet"],
                                    self.load_img("weapon/sniper1.png")),
                                    # 47 DPS +28R                   |   75p   |   weight 389
            "Nail Gun": Weapon("Nail Gun",
                                    "Definitely a construction tool.\nMaybe it was used for the project...",
                                    "weapon",150,0.35,{"binded":[108,0.20]},"20% chance to bind an enemy",8800,16,14,["nail"],
                                    self.load_img("weapon/nail_gun.png"),recoil=20),
                                    # 77 DPS *0.9Recoil +1.6R + 8Bind   |   79p     |   weight 421
            "G-Launcher": Weapon("G-Launcher",
                                    "KABOOM... KABLAOW...",
                                    "weapon",490,1.0,{"explosion":[65,0.8], "bubble":[0.1]},"Explodes on impact",11000,22,10,["grenade_red"],
                                    self.load_img("weapon/grenade_launcher.png")),
                                    # 50 DPS + 20Boom +3R           |   73p   |   weight 486

        # --- SILVERPINE TUNDRA --- 12

            "Living Pistol": Weapon("Living Pistol",
                                    "The trigger isn't connected to anything.\nIt fires anyway.",
                                    "weapon",120,0.45,{"homing":[0.75]},"Homing bullets",10000,16,16,["bullet"],
                                    self.load_img("weapon/living_pistol.png")),
                                    # 66 DPS  +10Homing +4R         |   80p   |   weight 275
            "Liquidator Hose": Weapon("Liquidator Hose",
                                    "The liquid dissolves almost everything.",
                                    "weapon",21,0.05,{"acid":[100,0.5],"bubble":[0.1]},"Acid: -50% def to hit enemy",9000,16,16,["acid"],
                                    self.load_img("weapon/hose2.png"),True,10),
                                    # 80 DPS + 8Acid                |   88p   |   weight 421
            "Shotgun R6": Weapon("Shotgun R6",
                                    "The sixth revision was supposed to be the final one.",
                                    "weapon",43,0.8,{"shotgun":["r",6]},"None",8800,14,16,["normal_red"],
                                    self.load_img("weapon/shotgun_r6.png"),recoil=30),
                                    # 90 DPS *0.8Recoil +1.6R       |   74p   |   weight 227
            "Living Hose": Weapon("Living Hose",
                                    "It moves before you point it.",
                                    "weapon",26,0.08,{"homing":[0.6]},"Homing projectiles",9800,14,16,["water"],
                                    self.load_img("weapon/living_hose.png"),True,16),
                                    # 75 DPS + 1R +8Homing         |   84p   |   weight 324
            "Blaster 2.0": Weapon("Blaster 2.0",
                                    "The paint is peeling.\nUnderneath it is a number you don't recognize.",
                                    "weapon",630,1.3,{"zap":[3,0.4],"slow":[90,0.2]},"Zaps and slows enemies",11000,18,18,["laser_blue"],
                                    self.load_img("weapon/blaster2.png")),
                                    # 61 DPS +20Zap + 5Slow         |   86p   |   weight 486
            "Minigun": Weapon("Minigun",
                                    "Too much firepower for such a small world.",
                                    "weapon",36,0.11,{},"None",9500,12,20,["bullet"],
                                    self.load_img("weapon/minigun.png"),True,20),
                                    # 73 DPS *0.9Recoil +3R         |   69p   |   weight 324
            "Flare Gun": Weapon("Flare Gun",
                                    "It was designed to call for help.\nThe signal was never answered.",
                                    "weapon",300,0.85,{"explosion":[60,0.4],"burn":[50,17.9]},"Explodes and burns enemies",9100,18,14,["bullet_red"],
                                    self.load_img("weapon/flare_gun.png")),
                                    # 59 DPS + 12Burn +16Boom        |   87p   |   weight 421

        # --- UNDERGROUND GARDEN ---    20

            "RPG": Weapon("RPG",
                                    "The garden has no reason to need weapons like this.",
                                    "weapon",1970,1.4,{"explosion":[90,0.7]},"Big explosion",9100,24,13,["missile_red"],
                                    self.load_img("weapon/rpg1.png")),
                                    # 85 DPS + 60Boom +2.2R         |   147p   |   weight 1409
            "Living Rifle": Weapon("Living Rifle",
                                    "It doesn't aim at enemies.\nIt seems to know where they are going to be.",
                                    "weapon",260,0.3,{"homing":[0.85]},"Homing bullets, Automatic",10100,14,18,["bullet"],
                                    self.load_img("weapon/living_rifle.png"),True),
                                    # 100 DPS +16Homing +4.2R +2Auto        |   122p   |   weight 875
            "Flower Gun": Weapon("Flower Gun",
                                    "It smells so nice.\nThat is probably the worst part.",
                                    "weapon",700,0.7,{"bubble":[0.1],"poison":[200,70],"acid":[120,0.5]},"Poisons and acidizes enemies",9600,18,16,["flower_green","flower_blue","flower_orange","flower_pink"],
                                    self.load_img("weapon/flower_gun.png")),
                                    # 71 DPS +20Poison + 40Acid     |   131p   |   weight 1069
            "Laser Cannon 2.0": Weapon("Laser Cannon 2.0",
                                    "Version 2.0 exists.\nVersion 1.0 is still running somewhere below.",
                                    "weapon",1410,1.0,{"pierce":[4]},"Pierces 4 enemies",11100,28,8,["normal_blue"],
                                    self.load_img("weapon/laser_cannon2.png")),
                                    # 105 DPS + 50Pierce +6.2R      |   173p   |   weight 1409
            "Shotgun S8": Weapon("Shotgun S8",
                                    "More barrels were added because\nnobody knew how else to improve it.",
                                    "weapon",130,0.58,{"shotgun":["s",8]},"Automatic",9100,14,18,["normal_red"],
                                    self.load_img("weapon/shotgun_s8.png"),True,18),
                                    # 138 DPS *0.92Recoil +2.2R +2Auto      |   131p   |   weight 1215
            "Shotgun R15": Weapon("Shotgun R15",
                                    "15th... It's never enough",
                                    "weapon",58,0.89,{"shotgun":["r",15]},"None",9400,16,18,["normal_red"],
                                    self.load_img("weapon/shotgun_r15.png"),recoil=25),
                                    # 135 DPS *0.85Recoil 2.8R      |   118p   |   weight 680
            "Ultra Blaster": Weapon("Ultra Blaster",
                                    "There is a tiny crack in the casing.\nSomething underneath is glowing.",
                                    "weapon",740,0.55,{"zap":[2,0.3],"poison":[180,57],"weakness":[180,0.1]},"Zaps, poisons and weakens enemies",10200,18,20,["laser_green"],
                                    self.load_img("weapon/blaster3.png")),
                                    # 118 DPS +12Zap +20Poison +16Weakness  |   166p   |   weight 1409

        # --- THE CORE ---  26

            "AK-47": Weapon("AK-47",
                                    "A weapon from a world that shouldn't exist here.",
                                    "weapon",840,0.22,{"weakness":[30,0.15]},"Apply -15% dmg to enemies hit",11100,15,18,["bullet"],
                                    self.load_img("weapon/ak_47.png"),True),
                                    # 264 DPS +10Weakness + 14R +2Auto      |   290p   |   weight 3791
            "Laser Arrow": Weapon("Laser Arrow",
                                    "THE weapon from THE future",
                                    "weapon",1480,0.35,{"zap":[2,0.8],"slow":[30,0.5]},"Zaps and slows",14200,18,26,["arrow_blue"],
                                    self.load_img("weapon/laser_arrow.png")),
                                    # 228 DPS +42Zap +10Slow +30R           |   310p   |   weight 4228
            "Acid Gun": Weapon("Acid Gun",
                                    "The container was empty when you found it.\nSomehow, now it's full.",
                                    "weapon",1670,0.52,{"acid":[180,1.0],"slow":[100,0.3]},"Destroys enemies defence",11300,20,20,["laser_yellow"],
                                    self.load_img("weapon/acid_gun.png")),
                                    # 169 DPS +60Acid +20Slow +14R          |   263p   |   weight 3208
            "Peace Gun": Weapon("Peace Gun",
                                    "The name is handwritten.\nThe rumors say that this gun is\nMilo's worst enemy, no one tried it yet.",
                                    "weapon",1900,0.82,{"binded":[100,0.33]},"33% chance to bind",10200,12,20,["flower_green"],
                                    self.load_img("weapon/peace_gun.png")),
                                    # 106 DPS +80Bind +10R                  |   196p   |   weight 2041
            "Combat Sniper": Weapon("Combat Sniper",
                                    "Someone used this long after\nthe factory shut down.",
                                    "weapon",3200,1.22,{"pierce":[1],"weakness":[90,0.3]},"Pierces and weakens enemies",27000,18,30,["nail"],
                                    self.load_img("weapon/sniper2.png")),
                                    # 172 DPS +26Pierce +14Weakness + 40Range   |  252p    |   weight 2624
            "Ghost USP": Weapon("Ghost USP",
                                    "There is no record of this weapon.\nThere is no record of you finding it.",
                                    "weapon",1800,0.42,{"pierce":[1],"confusion":[30,0.9],"weakness":[120,0.25],"glued":[120,0.25]},"Pierces one enemy, confuses, weakens\nand glues enemies (ghost bullets)",9800,16,18,["ghost_bullet"],
                                    self.load_img("weapon/ghost_usp.png")),
                                    # 226 DPS +26Pierce +20Confusion +20Weakness +20Glued   |   312p   |   weight 4228

        # --- THE VOID ---  32

            "Ghost Rifle": Weapon("Ghost Rifle",
                                    "The ectoplasma is really wierd in touch\nYou are holding it anyway.",
                                    "weapon",2800,0.24,{"pierce":[1],"confusion":[40,0.8],"weakness":[100,0.3],"glued":[100,0.3]},"Pierces one enemy, confuses, weakens\nand glues enemies (ghost bullets)",10800,16,18,["ghost_bullet"],
                                    self.load_img("weapon/ghost_rifle.png"),True),
                                    # 521 DPS +32Pierce +80Ghost            |   633p   |   weight 11372

            "Pocket AK": Weapon("Pocket AK",
                                    "This weapon should be a meme,\nmaybe it's an explanation why it's here",
                                    "weapon",1100,0.18,{"glued":[150,0.25]},"Glues enemies, Automatic",10000,13,18,["bullet_gold"],
                                    self.load_img("weapon/pocket_ak.png"),True,15),
                                    # 567 DPS *0.95Recoil + 50Glued         |   589p   |   weight 6124
            "Ghost Shotgun": Weapon("Ghost Shotgun",
                                    "The ectoplasma is really wierd in touch\nYou are holding it anyway.",
                                    "weapon",1980,0.8,{"pierce":[2],"confusion":[40,0.85],"weakness":[120,0.2],"glued":[120,0.2],"shotgun":["s",7]},"Pierces one enemy, confuses, weakens\nand glues enemies (ghost bullets)",8800,16,18,["ghost_bullet"],
                                    self.load_img("weapon/ghost_shotgun.png"),recoil=15),
                                    # 578 DPS *0.95Recoil +80Ghost          |  629p    |   weight 11372
            "Missile-3000": Weapon("Missile-3000",
                                    "The number isn't a model number.\nIt's a count...",
                                    "weapon",11800,1.18,{"explosion":[100,0.88],"burn":[60,200],"slow":[90,0.33],"homing":[0.35]},"Homing missiles, big explosion\nthat slows and burns enemies",11100,26,14,["missile_blue"],
                                    self.load_img("weapon/rpg2.png")),
                                    # 286 DPS + 288Explosion + 40Burn +20Slow   |   634p   |   weight 11372
            "Laser SMG v2": Weapon("Laser SMG v2",
                                    "Don't you think it's too much DPS\nYeah i know the answer...",
                                    "weapon",2450,0.21,{"pierce":[1],"binded":[60,0.2], "burst":[3,0.06]},"Pierces and has a small\nchance to bind an enemy\n3-round bursts",12200,14,26,["laser_red"],
                                    self.load_img("weapon/laser_smg2.png"),True),
                                    # 690 DPS +42Pierce +10Binded           |   742p   |   weight 11372

            
        }  

# ARMORS

        self.armors = {
        # BALANCE (6.11, see BALANCE.md): an armour x1.0 lets you take ~6 normal hits from enemies of its biome
        # (hits x multiplier: 0.7 weakest ... 1.45 best, Tundra up to 1.5). Defence stays FLAT (dmg - def, min 1):
        # ~1/8 of a normal hit of its biome, so bullets from ~2-3 levels lower do almost nothing.
        # Regeneration: regen [up to this share of HP, % of max HP every 0.5 s] - only after 3 s without a hit (10.11).

        # --- VILLAGE ---

            "Leather Chestplate": Armor(
                "Leather Chestplate",
                "A simple chestplate.\nIt's a little dusty, but it gets the job done.",
                "armor", 1.8,0,
                {}, "None",
                self.load_img("armor/chestplate1.png")
            ),
            "Vest": Armor(
                "Vest",
                "Better than wearing nothing.\nProbably.",
                "armor", 0.5,0,
                {"speed": ["inf", 0.07]}, "Lightweight I\n+7% movement speed",
                self.load_img("armor/vest1.png")
            ),

        # --- RAINBOW FIELDS ---

            "Gladiator's Chestplate": Armor(
                "Gladiator's Chestplate",
                "A sturdier version of the old chestplate.\nLost by the last fallen.",
                "armor", 4.0,110,
                {"guard": [1.0, 0.25]}, "Guard I\nAt 100% health, next dmg -25%",
                self.load_img("armor/chestplate2.png")
            ),
            "Medieval Armor I": Armor(
                "Medieval Armor I",
                "Old-fashioned armor\n from an old-fashioned world.",
                "armor", 3.6,61,
                {}, "None",
                self.load_img("armor/medieval1.png")
            ),
            "Apprentice Armor": Armor(
                "Apprentice Armor",
                "A small suit of armor.\nProbably made for training.",
                "armor", 6.5,150,
                {"berserk": [0.3, 0.15]}, "Berserk I\nIf below 30% health, dmg +15%",
                self.load_img("armor/knight1.png")
            ),

        # --- SUGARWOOD GROVE ---

            "Reinforced Vest": Armor(
                "Reinforced Vest",
                "Almost feels like wearing nothing.",
                "armor", 18,250,
                {"speed": ["inf", 0.15]}, "Lightweight II\n+15% movement speed",
                self.load_img("armor/vest2.png")
            ),
            "Living Plate": Armor(
                "Living Plate",
                "Soft. Warm. Slightly breathing.",
                "armor", 14,600,
                {"regen": [0.3, 1.2]}, "Regen I\nRegenerate up to 30% hp (1.2% every 0.5 s)\nafter 3 s without a hit",
                self.load_img("armor/living1.png")
            ),
            "Samurai Jacket": Armor(
                "Samurai Jacket",
                "Sweet in touch.\nDon't you think this world is too sweet?",
                "armor", 0,460,
                {"focus": [120, 0.1, 0.1, 0]}, "Focus I\nAfter 2s without dmg +10% speed and dmg",
                self.load_img("armor/samurai1.png")
            ),

        # --- TOY FACTORY ---

            "Knight Armor": Armor(
                "Knight Armor",
                "Several pieces have been replaced\nby parts that don't seem to\nbelong here.",
                "armor", 42,1530,
                {"berserk": [0.33, 0.2]}, "Berserk II\nIf below 33% health, dmg +20%",
                self.load_img("armor/knight2.png")
            ),
            "Medieval Armor II": Armor(
                "Medieval Armor II",
                "The Core makes the difference\nThe Core of the armor i mean",
                "armor", 47,1490,
                {"poison_imm": [1]}, "Immune to poison",
                self.load_img("armor/medieval2.png")
            ),
            "Samurai Plating": Armor(
                "Samurai Plating",
                "The material doesn't match anything\nelse found in the factory, wierd...",
                "armor", 14,1490,
                {"focus": [90, 0.1, 0.2, 0]}, "Focus II\nAfter 1.5s without dmg: +10% speed, +20% dmg",
                self.load_img("armor/samurai2.png")
            ),
            "Cyber Suit": Armor(
                "Cyber Suit",
                "Bad idea, worse execution.\nIt reminds me of this world",
                "armor", 81,1080,
                {"bullseye": [0.1]}, "Bullseye I\nimmediately kills an enemy below 10% hp",
                self.load_img("armor/cyber1.png")
            ),
            "Scrap Armor": Armor(
                "Scrap Armor",
                "These pieces are from the core.",
                "armor", 58,1220,
                {"rnd_effect": [480, 1]}, "Randomiser I\nEach 8s gain a random effect",
                self.load_img("armor/scrap.png")
            ),

        # --- SILVERPINE TUNDRA ---

            "Old-World Vest": Armor(
                "Old-World Vest",
                "Whoever made this cared more\nabout movement than protection.",
                "armor", 33,1090,
                {"speed": ["inf", 0.21]}, "Lightweight III\n+21% movement speed",
                self.load_img("armor/vest3.png")
            ),
            "Golden Chestplate": Armor(
                "Golden Chestplate",
                "It is much heavier than the original.\nThe metal is strangely warm,\ndespite where it was found.",
                "armor", 53,1910,
                {"guard": [0.8, 0.5]}, "Guard II\nIf above 80% health, all dmg -50%",
                self.load_img("armor/chestplate3.png")
            ),
            "Living Armor": Armor(
                "Living Armor",
                "It changes shape when nobody is looking.\nAlmost like this world",
                "armor", 48,1280,
                {"regen": [0.3, 1.2], "slow_imm": [1]}, "Regen I\nRegenerate up to 30% hp (1.2% every 0.5 s)\nafter 3 s without a hit\nImmune to slowness",
                self.load_img("armor/living2.png")
            ),
            "Frost Armor": Armor(
                "Frost Armor",
                "That frost is an attempt to\ndestroy everything before it was too late",
                "armor", 58,1860,
                {"frost": [60]}, "Frost Aura\nSlows nearby bullets",
                self.load_img("armor/frost.png")
            ),

        # --- UNDERGROUND GARDEN ---

            "Medieval Armor III": Armor(
                "Medieval Armor III",
                "How the hell an armor can make you\nimmune to poison or weakness?",
                "armor", 140,4570,
                {"poison_imm": [1], "glued_imm": [1], "weakness_imm": [1],"poison_up":[60,1]}, "Immune to poison, glued and weakness\nAlso your poison lasts one additional second",
                self.load_img("armor/medieval3.png")
            ),
            "Plate Armor": Armor(
                "Plate Armor",
                "Probably the most tanky armor in the game",
                "armor", 140,5750,
                {"guard": [0.5, 0.6], "slow": ["inf", 0.25]}, "Guard III\nIf above 50% health, all dmg -60%\nSlowness - -25% speed",
                self.load_img("armor/knight3.png")
            ),
            "Saper Armor": Armor(
                "Saper Armor",
                "You like KABOOM...?",
                "armor", 120,2850,
                {"explosion_up": [20, 0.1]}, "Buffs Explosions",
                self.load_img("armor/saper.png")
            ),
            "Tribe Armor": Armor(
                "Tribe Armor",
                "It isn't armor.\nYou are wearing it because it allows you to.",
                "armor", 60,6250,
                {"regen": [0.5, 1.5], "slow_imm": [1], "poison_imm": [1]}, "Regen II\nRegenerate up to 50% hp (1.5% every 0.5 s)\nafter 3 s without a hit\nImmune to slowness and poison",
                self.load_img("armor/living3.png")
            ),
            "Samurai Armor": Armor(
                "Samurai Armor",
                "Did you ever thought it was meant to last?\nStupid world analogy",
                "armor", 40,5250,
                {"focus": [60, 0.15, 0.3, 0.1], "slow_imm": [1], "bind_chance": [0]}, "Focus III\nAfter 1s without dmg:\n+15% speed, +30% dmg, +10% fire rate\nImmune to slowness and binded",
                self.load_img("armor/samurai3.png")
            ),
            "Cyber Armor": Armor(
                "Cyber Armor",
                "There is no serial number. There is no manufacturer.",
                "armor", 210,3150,
                {"overclock": [600, 120, 0.5]}, "Overclock I\nEvery 10s gain a fire rate boost for 2s",
                self.load_img("armor/cyber2.png")
            ),

        # --- THE CORE ---

            "Mecha Armor": Armor(
                "Mecha Armor",
                "Is it me or it looks like a lifejacket?",
                "armor", 620,15660,
                {"overclock": [480, 180, 0.5]}, "Overclock II\nEvery 8s gain a fire rate boost for 3s",
                self.load_img("armor/cyber3.png")
            ),
            "Viking Armor": Armor(
                "Viking Armor",
                "Nobody remembers where this armor came from.\nNobody remembers anything honestly",
                "armor", 300,8920,
                {"bullseye": [0.3]}, "Bullseye II\nImmediately kills an enemy below 30% hp",
                self.load_img("armor/viking.png")
            ),
            "Heroic Armor": Armor(
                "Heroic Armor",
                "A costume made for heroes.",
                "armor", 400,12140,
                {"rnd_effect": [480, 2]}, "Randomiser II\nEach 8s gain a random buff",
                self.load_img("armor/heroic.png")
            ),
            "Electro Armor": Armor(
                "Electro Armor",
                "Something inside is still receiving a signal.",
                "armor", 470,13460,
                {"static": [0.25],"zap_up":[1,0.5]}, "Each time you get hit(not contact),\ndeal dmg to all enemies equivalent to quater\nthe dmg dealt, also buffs zap bullets",
                self.load_img("armor/electro.png")
            ),
            "Samurai God": Armor(
                "Samurai God",
                "You belived in him and you became him.",
                "armor", 0,20000,
                {"dodge": [0.25],"hitbox":[0.80]},"Chance to dodge bullets, smaller hitbox",
                self.load_img("armor/samurai4.png")
            ),

        # --- THE VOID ---

            "Mecha-King Armor": Armor(
                "Mecha-King Armor",
                "Milo's best buddy had it\nnow he's dead...",
                "armor", 1410,45850,
                {"emergency":[1], "confusion_chance": [0]}, "Emergency Protocol\nOnce per fight, survive death with 15% hp\nImmune to confusion",
                self.load_img("armor/cyber4.png")
            ),
            "Fallen knight armor": Armor(
                "Armor of the fallen Knight",
                "That's the fallen one\nhe certainly died here",
                "armor", 1430,45680,
                {"berserk": [0.3, 0.5], "bind_chance": [0], "burn_imm": [1]}, "Berserk III\nIf below 30% health, dmg +50%\nImmune to binded and burn",
                self.load_img("armor/knight4.png")
            ),
            "Ghost Armor": Armor(
                "Ghost Armor",
                "You cover yourself in ghost, you may become a ghost",
                "armor", 1580,44490,
                {"ghost_up": [1,0.1]}, "Buffs ghost bullets",
                self.load_img("armor/ghost.png")
            ),

        }
# TRINKETS
        self.trinkets = {
        # --- Village ---   

            "Hook": Trinket("Hook",
                "A heavy, rust-covered iron anchor that was dragged\nfrom the depths of a nameless lake. Its jagged edge\nlooks like it was designed to catch something big",
                "trinket",
                {"angler":[1]}, "Bring this to the angler",
                self.load_img("trinket/hook.png")
            ),
            "Shrooms": Trinket("Shrooms",
                "A cluster of pale, pulsing fungi\nharvested from the corners of the village woods.",
                "trinket",
                {"poison_up":[60,2]}, "Poison +1s and +2 dmg",
                self.load_img("trinket/shrooms.png")
            ),
            "Shoe": Trinket("Shoe",
                "A well-worn, lightweight sneaker with strange,\nglowing runes roughly stitched into the sole.",
                "trinket",
                {"speed":["inf",0.07]}, "+7% movement speed",
                self.load_img("trinket/shoe.png")
            ),

        # --- RAINBOW FIELDS ---  

            "D20": Trinket("D20",
                "20-sided die carved from a ruby crystal.\nAs you turn it over, the numbers on its faces\nseem to constantly shift and blur.",
                "trinket",
                {"double_shot":[3]}, "Every 3 s your next shot is doubled.",
                self.load_img("trinket/d20.png")
            ),
            "Martini": Trinket("Martini",
                "An elegant, crystal glass filled with a shimmering\nneon fluid that vibrates to an unseen rhythm.",
                "trinket",
                {"strength":["inf",0.2], "recoil":[15], "shotgun_up":[1]}, "+20% dmg, +15 recoil.\nShotguns fire +1 pellet.",
                self.load_img("trinket/martini.png")
            ),
            "Rose": Trinket("Rose",
                "A remarkably beautiful crimson flower.\nIt seems like this belonged to the previous world.",
                "trinket",
                {"thorns":[8, 20]}, "When you get hit, 8 thorns fly out (20 dmg each).",
                self.load_img("trinket/rose.png")
            ),
        
        # --- SUGARWOOD GROVE ---  

            "Book": Trinket("Book",
                "Money, Money, Money...",
                "trinket",
                {"enemy_gold":[0.2]}, "+20% money from defeated enemies.",
                self.load_img("trinket/book.png")
            ),
            "Bra": Trinket("Bra",
                "You'll look insanely pretty with this on.",
                "trinket",
                {"dmgless_contact":[1]}, "Contact with enemies doesn't deal dmg.",
                self.load_img("trinket/bra.png")
            ),
            "Cotton Candy": Trinket("Cotton Candy",
                "You're too sweat for this world.",
                "trinket",
                {"speed_on_hit":[0.33]}, "Getting hurt gives you a speed boost.",
                self.load_img("trinket/cotton_candy.png")
            ),
            "Sugar Crystal": Trinket("Sugar Crystal",
                "A sharp, glittering lump of pure sugar.\nIt hums faintly when you hold it to your ear.",
                "trinket",
                {"gus":[1]}, "Bring this to Gus",
                self.load_img("trinket/sugar_crystal.png")
            ),
            "Firefly Jar": Trinket("Firefly Jar",
                "A jar of fireflies from the Night Bloom.\nThey don't like the dark either.",
                "trinket",
                {"fireflies": [180, 0.5], "light": [1]}, "Every 3 s a firefly flies at an enemy\n(50% of your shot). Less dark around you.",
                self.load_img("trinket/firefly_jar.png")
            ),
            "Flavoured Candy": Trinket("Flavoured Candy",
                "A sweet from the Shroom Mother.\nEvery bite tastes different. Some bite back.",
                "trinket",
                {"flavour":[600]}, "Start of every fight: a random effect for 10 s (good or bad)",
                self.load_img("trinket/flavoured_candy.png")
            ),
            "Coupon": Trinket("Coupon",
                "A golden coupon for Lucky's wheel.\nThe print is pale, as if copied from somewhere else.",
                "trinket",
                {"coupon":[1]}, "Bring this to Lucky",
                self.load_img("trinket/coupons.png")
            ),
            "Mascot Plush": Trinket("Mascot Plush",
                "A plush prize from the lunapark.\nIt's still warm. It has a sticker: WINNER.",
                "trinket",
                {"decoy":[2.5]}, "Lures enemies away in every fight",
                self.load_img("trinket/plushie.png")
            ),
            "Tape": Trinket("Tape",
                "Your enemies won't speak a world when\nyou'll use it, literally.",
                "trinket",
                {"slow_on_glue":[0.2], "glued_vuln":[0.1]}, "Glued enemies are also slowed (-20% speed)\nand take +10% dmg. (Glue weapons only)",
                self.load_img("trinket/tape.png")
            ),
                    
        # --- TOY FACTORY ---  

            "Broken Bulb": Trinket("Broken Bulb",
                "The bulb shattered when the system went dark.\nThe system never came back on.",
                "trinket",
                {"lore_item_bulb":[1]}, "None",
                self.load_img("trinket/bulb.png")
            ),
            "Dices": Trinket("Dices",
                "If they made you loose a lot of money,\nnow's the time for a payback.",
                "trinket",
                {"luck":[1]}, "Increased luck.",
                self.load_img("trinket/dices.png")
            ),
            "Fire Ring": Trinket("Fire Ring",
                "Ring from the lord of rings?\nNah, but it's still powerfull.",
                "trinket",
                {"glued_imm":[1], "less_burn":[30, 0], "burn_burst":[220, 0.5]}, "Immune to glue, shorter burns.\nBurning enemies burst into flames when they die\n(sets the enemies around on fire).",
                self.load_img("trinket/fire_ring.png")
            ),
            "Holy Orb": Trinket("Holy Orb",
                "It hums with a righteous power designed\nto cleanse the world of ancient evils.",
                "trinket",
                {"dmg_to_undead":[0.2], "homing_light":[0.6, 1.5]}, "Your bullets gently home in (more on undead).\n+20% dmg to undead.",
                self.load_img("trinket/holy_orb.png")
            ),
            # the Foreman's 3 parts for Line Bloodbath (quest "foreman")
            "Gear": Trinket("Gear",
                "A heavy gear with a few teeth missing.\nIt still turns, if you ask it nicely.",
                "trinket",
                {"foreman":[1]}, "Bring this to the Foreman",
                self.load_img("trinket/gear.png")
            ),
            "Meter": Trinket("Meter",
                "A little meter. The needle never stops shaking,\neven when it's not plugged into anything.",
                "trinket",
                {"foreman":[1]}, "Bring this to the Foreman",
                self.load_img("trinket/meter.png")
            ),
            "Fuse": Trinket("Fuse",
                "A spare fuse from a tesla robot.\nStill warm.",
                "trinket",
                {"foreman":[1]}, "Bring this to the Foreman",
                self.load_img("trinket/fuse.png")
            ),

        # --- SILVERPINE TUNDRA ---  

            "Cassette Tape": Trinket("Cassette Tape",
                "Someone keeps repeating the same sentence.\n“We need to turn it off.”",
                "trinket",
                {"lore_item_tape":[1]}, "None",
                self.load_img("trinket/cassette_tape.png")
            ),
            "Frozen Ring": Trinket("Frozen Ring",
                "Doesn't freeze anything, it's quite the opposite actually.",
                "trinket",
                {"weakness_imm":[1], "slow_imm":[1]}, "Immune to weakness and slow.",
                self.load_img("trinket/frozen_ring.png")
            ),
            "Ice Mix": Trinket("Ice Mix",
                "Used it on yourself a lot.\nNow you will use it on enemies.",
                "trinket",
                {"slow_up":[10, 0.1], "slow_vuln":[0.15]}, "Slows enemies 10% (stacks with normal slow).\nSlowed enemies take +15% dmg.",
                self.load_img("trinket/ice_mix.png")
            ),
            "Eyeballs": Trinket("Eyeballs",
                "Where did you even get this from?\nBut at least it's really usefull.",
                "trinket",
                {"reveal_secret":[1], "map_memory":[900]}, "Remembers more than you do",
                self.load_img("trinket/eyeball.png")
            ),

        # --- UNDERGROUND GARDEN ---  

            "Atom": Trinket("Atom",
                "A physical atom that you can hold in your hand.",
                "trinket",
                {"cluster":[3, 0.20]}, "Your explosions throw out 3 smaller ones\n(20% dmg each).",
                self.load_img("trinket/atom.png")
            ),
            "Pale Orb": Trinket("Pale Orb",
                "It comes from the pale world.\nEquipping this makes you vanish.",
                "trinket",
                {"pale_world":[1]}, "You'll see.",
                self.load_img("trinket/pale_orb.png")
            ),
            "Toxic Ring": Trinket("Toxic Ring",
                "The poison has eaten through the metal.\nIt hasn't eaten through the ring.",
                "trinket",
                {"poison_imm":[1], "less_acid":[20, 0.35], "poison_spread":[600, 2]}, "Immune to poison, lowers acid effect.\nWhen a poisoned enemy dies, the poison\njumps to the 2 nearest enemies (fresh).",
                self.load_img("trinket/toxic_ring.png")
            ),
            "Magic Ring": Trinket("Magic Ring",
                "The symbol inside the ring isn't magic.\nAt least, that's what the old books say.",
                "trinket",
                {"confusion_imm":[1], "binded_imm":[1], "friendly_fire":[1]}, "Immune to binding and confusion.\nConfused enemies' shots also hurt other enemies.",
                self.load_img("trinket/magic_ring.png")
            ),
            "Magic Dust": Trinket("Magic Dust",
                "It doesn't fall normally.\nSome of it floats upward.",
                "trinket",
                {"imm_frames":[80]}, "Gives 80 immunity frames.",
                self.load_img("trinket/magic_dust.png")
            ),
            # the Gardener's quest (3 needed: 2 on the floor of the Garden, 1 from a toxic flower)
            "Glowing Sprout": Trinket("Glowing Sprout",
                "A tiny sprout that glows like a lamp.\nIt's warm, as if it remembered the sun.",
                "trinket",
                {"gardener":[1]}, "Bring 3 of these to the Gardener",
                self.load_img("trinket/sprout.png")
            ),
            # the Gardener's reward
            "Toxic Gas": Trinket("Toxic Gas",
                "Bottled from the toxic flowers of the Garden.\nDon't open it indoors.",
                "trinket",
                {"toxic_gas":[3, 180, 3]}, "Poison from your weapon never wears off.\nWeapons without poison: small poison (3 s).",
                self.load_img("trinket/toxic_gas.png")
            ),

        # --- THE CORE ---  

            "Hourglass": Trinket("Hourglass",
                "An old hourglass. The sand flows surprisingly slowly.",
                "trinket",
                {"debuff_time":[0.75],"buff_time":[1.25]}, "All debuffs last 25% shorter\nand buffs 25% longer.",
                self.load_img("trinket/hourglass.png")
            ),
            "Old Note": Trinket("Old Note",
                "“It was meant to last but something happend”\n“We thought we were shutting it down.”\n“We were only putting it to sleep.”",
                "trinket",
                {"lore_item_note":[1]}, "None",
                self.load_img("trinket/old_note.png")
            ),
            "Power Bank": Trinket("Power Bank",
                "The battery indicator hasn't changed in years.\nOf course you can plug it to any weapon.",
                "trinket",
                {"zap_up":[1, 0.25], "electric_up":[0.15]}, "Electric weapons: +15% dmg,\nzaps 1 more enemy, zap dmg +25%.",
                self.load_img("trinket/power_bank.png")
            ),

        # --- THE VOID ---  

            "Crown": Trinket("Crown",
                "It warps the space directly around your body,\nmaking your physical presence look strangely small.",
                "trinket",
                {"hitbox":[0.75]}, "Makes you smaller",
                self.load_img("trinket/crown.png")
            ),

        }


        # every item knows its database key -> saves store keys, not display names
        for db in (self.weapons, self.armors, self.trinkets):
            for key, item in db.items():
                item.id = key

    def get_item(self, name):
        # returns a fresh copy, so two copies of one item are separate objects in the inventory
        item = self.find_item(name)
        if item is None:
            return None
        new_item = copy.copy(item)
        new_item.effect = copy.deepcopy(item.effect)
        return new_item

    def find_item(self, name):
        for db in (self.weapons, self.armors, self.trinkets):
            if name in db:
                return db[name]
        # old saves stored display names; this one no longer matches anything
        legacy_names = {"Medieval Armor": "Medieval Armor I"}
        if name in legacy_names:
            return self.find_item(legacy_names[name])
        # fallback for old saves (stored display names) and renamed keys, case-insensitive
        for db in (self.weapons, self.armors, self.trinkets):
            for key, item in db.items():
                if item.name.lower() == name.lower() or key.lower() == name.lower():
                    return item
        return None

    def load_img(self, path):
        try:
            img = pygame.image.load(f"assets/img/inventory/{path}").convert_alpha()
        except (FileNotFoundError, pygame.error):
            # PLACEHOLDER: no picture yet (e.g. a new quest item) -> a plain square with a "?"
            img = pygame.Surface((64, 64), pygame.SRCALPHA)
            img.fill((200, 200, 210))
            pygame.draw.rect(img, (60, 60, 70), img.get_rect(), 4)
            mark = pygame.font.Font(None, 56).render("?", True, (60, 60, 70))
            img.blit(mark, mark.get_rect(center=(32, 34)))
        return pygame.transform.scale(img, self.img_size)
