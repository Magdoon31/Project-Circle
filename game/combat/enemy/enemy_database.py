from game.combat.enemy.enemy import Enemy
from game.world.loot import LUCK_DROP
from game.combat.bullet_types import BulletTypes
import copy, random, math

class EnemyDB:
    def __init__(self, sfx, bullet_type_info=None):
        self.enemies = {
            # BALANCE (6.11, see BALANCE.md): HP so that a NORMAL enemy dies in ~2.5 s to a 1.0x weapon of its biome
            # (small ~1 s, tank ~5.6 s), x3 per biome level. Defence is now a % : damage x 100 / (100 + def)
            # (def 25 = -20%, 50 = -33%, 100 = -50%).
            # DAMAGE (6.11): every attack + touching scaled so the biome's average hit = 10 x 3^(level-1)
            # (village 10, rainbow 30, sugarwood 90, factory/tundra 270, garden 810, core 2430, void 7290); minigun bursts
            # x0.5 per bullet. "telegraph": frames of the aiming line before a fast shot (the shot is then x1.3 faster).
             # --- VILLAGE ---

            "slime_small": [0,0,12,18,"enemy",3.4,6.9,4,0,"mystical","to_player_jump",{}],

            "slime_big": [0,0,68,36,"enemy",2.0,14,12,0,"mystical","to_player_jump",{"death_spawn":{"amount":2,"enemy_name":"slime_small"}}],

            "shooter": [0,0,30,22,"enemy",3.2,5.7,10,0,"human","away_player_distance",
                {"basic": {"damage": 14, "cooldown": 2.2, "last_used": 0, "width": 14, "speed": 16, "range": 3200, "effects": {}, "type":["arrow_red"]}}],


            # --- RAINBOW FIELDS ---

            "rainbow_slime": [0,0,72,24,"enemy",3.8,18,12,25,"mystical","to_player_jump",
                {"death_spiral": {"bullets":4,"damage": 40, "width": 13, "speed": 6, "range": 4000, "effects": {}, "type":["normal_yellow","normal_red","normal_green","normal_blue"]}}],

            "flower_spitter": [0,0,90,23,"enemy",1.0,14,10,0,"animal","away_player_normal",
                {"basic": {"damage": 50, "cooldown": 2.2, "last_used": 0, "width": 12, "speed": 8, "range": 3600, "effects": {"slow":[45,0.15],"homing":[0.4]}, "type":["flower_pink"]}}],

            "rainbow_guard": [0,0,162,30,"enemy",2.1,32,14,25,"human","to_player_normal",
                {"basic": {"damage": 27, "cooldown": 1.0, "last_used": 0, "width": 16, "speed": 14, "range": 750, "effects": {}, "type":["nail"]}}],


            # --- SUGARWOOD GROVE ---

            "gum_goblin": [0,0,270,26,"enemy",4.8,29,16,0,"animal","to_player_distance",
                {"basic": {"damage": 117, "cooldown": 1.6, "last_used": 0, "width": 13, "speed": 16, "range": 1800, "effects": {"glued":[60,0.25]}, "type":["normal_green"]}}],

            "candy_shroom": [0,0,490,24,"enemy",0.8,59,20,25,"plant","random_normal",
                {"spiral": {"damage": 44, "cooldown": 1.2, "last_used": 0, "width": 12, "speed": 8, "range": 3500, "bullets": 12, "effects": {"poison":[185,15]}, "type":["spore"], "stop_move":[30,15]}}],

            "toffee_runner": [0,0,86,18,"enemy",3.8,88,10,25,"animal","to_player_zigzag",{}],

            "sugar_caster": [0,0,220,25,"enemy",2.3,73,22,25,"mystical","away_player_normal",
                {"throw": {"radius": 90, "recoil":150, "damage": 220, "width":15, "exp_type":"nova_", "cooldown": 0.75, "last_used": 0, "fly_time": 1.5, "effects": {"speed":[60,0.25]},"stop_move":[48,12], "type":["flower_white"]}}],


            # --- TOY FACTORY ---

            "toy_soldier": [0,0,810,20,"enemy",1.8,136,25,0,"mechanical","to_player_normal",
                {"basic": {"damage": 407, "cooldown": 1.4, "last_used": 0, "width": 16, "speed": 14, "range": 3500, "effects": {}, "type":["bullet_red"]}}],

            "portable_factory": [0,0,1820,40,"enemy",0,14,50,0,"mechanical","random_normal",
                {"spawn": {"enemy_name":"toy_soldier","amount" : 1,"cooldown": 7.5, "last_used": 0},
                "spiral": {"damage": 217, "cooldown": 3.5, "last_used": 0, "width": 12, "speed": 6, "range": 3800, "bullets": 14, "effects": {}, "type":["normal_red"]}}],

            "robo-tesla": [0,0,650,23,"enemy",1.8,136,30,25,"mechanical","random_normal",
                           {"spiral": {"damage": 298, "cooldown": 1.0, "last_used": 0, "width": 5, "speed": 11, "range": 1800, "bullets": 18, "effects": {"weakness":[120,0.2]}, "type":["normal_blue"]}}],

            "robo-bomber": [0,0,650,23,"enemy",1.8,136,30,25,"mechanical","random_normal",
                            {"throw": {"radius": 180, "recoil":250, "damage": 475, "width":15, "exp_type":"", "cooldown": 3.2, "last_used": 0, "fly_time": 0.8, "effects": {"burn":[60,27]}, "type":["grenade_red"]}}],
                           
            "scrap_beetle": [0,0,260,14,"enemy",5.2,271,20,25,"mechanical","to_player_normal",
                {"mine": {"damage": 611, "radius": 80, "cooldown": 1.0, "last_used": 0, "width": 18, "exp_time": 3.5, "effects": {}, "type": ["mine_red"]}}],


            # --- SILVERPINE TUNDRA ---

            "frost_wolf": [0,0,650,26,"enemy",3.4,415,30,25,"animal","to_player_normal",{}],

            "ice_shooter": [0,0,810,26,"enemy",1.1,208,32,0,"human","away_player_normal",
                {"basic": {"telegraph": 30, "damage": 222, "cooldown": 1.4, "last_used": 0, "width": 12, "speed": 24, "range": 4500, "effects": {"slow":[45,0.55]}, "type":["arrow_blue"]}}],

            "frozen_orb": [0,0,1220,28,"enemy",0.8,166,30,50,"mystical","random_normal",
                {"spiral": {"damage": 305, "cooldown": 2.4, "last_used": 0, "width": 14, "speed": 8, "range": 4000, "bullets": 8, "effects": {"slow":[60,0.55],"homing":[0.34]}, "type":["normal_blue"]},
                 "death_spiral": {"damage": 305, "cooldown": 0, "last_used": 0, "width": 14, "speed": 8, "range": 4000, "bullets": 16, "effects": {"slow":[60,0.55],"homing":[0.34]}, "type":["normal_blue"]}}],

            "tundra_watcher": [0,0,900,35,"enemy",1.2,20,45,4,"human","random_normal",
                {"shotgun":{"damage": 20, "cooldown": 2.4, "last_used": 0, "width": 16, "speed": 20, "range": 4000, "recoil": 60, "bullets": 5, "effects": {"slow":[50,0.3]}, "type":["laser_blue"]},
                "basic": {"damage": 35, "cooldown": 1.4, "last_used": 0, "width": 20, "speed": 20, "range": 4000, "effects": {}, "type":["laser_blue"]}}],


            # --- UNDERGROUND GARDEN ---

            "pixie": [0,0,1940,20,"enemy",2.8,953,70,25,"mystical","random_jump",
                {"minigun": {"damage": 298,"cooldown": 1.5,"last_used": 0,"width": 18,"speed": 10,"burst_count": 0,"burst_max": 10,"burst_delay": 0.05,"last_shot": 0,"is_bursting": False, "spread": 360, "range": 3000, "effects" : {"confusion":[120,0.75],"slow":[180,0.25]},"type":["normal_yellow"]}}],

            "rainbow_pixie": [0,0,970,20,"enemy",1.5,953,200,0,"mystical","random_jump",
                              {"death_spiral": {"damage": 953, "cooldown": 0, "last_used": 0, "width": 18, "speed": 10, "range": 3000, "bullets": 18, "effects": {"confusion":[120,0.75],"slow":[180,0.25]}, "type":["normal_yellow","normal_green","normal_blue","normal_red"]},
                              "death_spawn": {"amount": 2, "enemy_name":"pixie"}}],

            "poison_skeleton": [0,0,5470,28,"enemy",3.1,953,85,0,"undead","away_player_normal",
                                {"basic": {"telegraph": 30, "damage": 953, "cooldown": 1.8, "last_used": 0, "width": 22, "speed": 24, "range": 3800, "effects": {"poison":[240,143]}, "type":["arrow_red"]}}],

            "inferno_flower": [0,0,1940,26,"enemy",0.6,953,85,25,"mystical","random_normal",
                               {"shotgun":{"damage": 596, "cooldown": 2.5, "last_used": 0, "width": 12, "speed": 12, "range": 2100, "recoil": 40, "bullets": 7, "effects": {"burn":[120,71]}, "type":["flower_orange"]},
                                "basic": {"damage": 715, "cooldown": 1.9, "last_used": 0, "width": 12, "speed": 12, "range": 2100, "effects": {"homing":[0.8],"burn":[120,71]}, "type":["flower_orange"]}}],

            "frost_flower": [0,0,1940,26,"enemy",0.6,953,85,25,"mystical","random_normal",
                               {"shotgun":{"damage": 596, "cooldown": 2.5, "last_used": 0, "width": 12, "speed": 12, "range": 2100, "recoil": 40, "bullets": 7, "effects": {"slow":[120,0.33],"weakness":[160,0.5]}, "type":["flower_blue"]},
                                "basic": {"damage": 715, "cooldown": 1.9, "last_used": 0, "width": 12, "speed": 12, "range": 2100, "effects": {"homing":[0.8],"slow":[120,0.33],"weakness":[160,0.5]}, "type":["flower_blue"]}}],

            "toxic_flower": [0,0,1940,26,"enemy",0.6,953,85,25,"mystical","random_normal",
                               {"shotgun":{"damage": 596, "cooldown": 2.5, "last_used": 0, "width": 12, "speed": 12, "range": 2100, "recoil": 40, "bullets": 7, "effects": {"acid":[120,0.33],"poison":[180,191]}, "type":["flower_green"]},
                                "basic": {"damage": 715, "cooldown": 1.9, "last_used": 0, "width": 12, "speed": 12, "range": 2100, "effects": {"homing":[0.8],"acid":[120,0.33],"poison":[180,191]}, "type":["flower_green"]}}],


            # --- THE CORE ---

            "liche": [0,0,10940,26,"enemy",2.5,835,120,50,"undead","random_normal",
                {"basic": {"damage": 4177, "cooldown": 1.0, "last_used": 0, "width": 18, "speed": 12, "range": 3400, "effects": {"poison":[300,501],"confusion":[80,0.5]}, "type":["ghost_bullet"]},
                "spiral": {"damage": 2506, "cooldown": 1.9, "last_used": 0, "width": 14, "speed": 10, "range": 2100, "bullets": 16, "effects": {"weakness":[300,0.3],"confusion":[80,0.5]}, "type":["ghost_bullet"]},
                "shotgun":{"damage": 2506, "cooldown": 2.6, "last_used": 0, "width": 14, "speed": 10, "range": 2200, "recoil": 30, "bullets": 5, "effects": {"glued":[300,0.3],"confusion":[80,0.5]}, "type":["ghost_bullet"]}}],

            "skeleton": [0,0,2330,21,"enemy",4.2,2506,30,25,"undead","to_player_normal",
                      {}],

            "mecha-skeleton": [0,0,3000,35,"boss",2.5,100,400,8,"undead","random_normal",
                      {"basic": {"damage": 40, "cooldown": 2.6, "last_used": 0, "width": 28, "speed": 10, "range": 2000, "effects": {"homing":[1],"burn":[120,4]}, "type":["missile_red"]},
                       "mine": {"damage": 50, "radius": 50, "cooldown": 1.7, "last_used": 0, "width": 25, "exp_time": 5.0, "effects": {"binded":[90,0.75]}, "type": ["mine_red"]},
                       "spawn": {"enemy_name":"skeleton","amount" : 2,"cooldown": 4.9, "last_used": 0},
                       "shotgun":{"damage": 25, "cooldown": 0.8, "last_used": 0, "width": 10, "speed": 8, "range": 2000, "recoil": 60, "bullets": 4, "effects": {"burn":[120,4]}, "type":["normal_red"]}}],

            "guard": [0,0,8200,22,"enemy",2.2,3341,90,100,"human","to_player_normal",
                      {}],

            "fly": [0,0,1940,18,"enemy",4.8,2506,30,50,"animal","to_player_normal",
                      {"death_spiral": {"damage": 1671, "cooldown": 0, "last_used": 0, "width": 15, "speed": 12, "range": 1600, "bullets": 8, "effects": {"poison":[180,835]}, "type":["spore"]}}],

            "generator": [0,0,4860,26,"enemy",0,835,120,50,"mechanical","random_normal",
                      {"spiral": {"damage": 2924, "cooldown": 1.0, "last_used": 0, "width": 13, "speed": 8, "range": 4000, "bullets": 14, "effects": {"glued":[100,0.33]}, "type":["normal_yellow"]},
                       "death_spiral": {"damage": 2924, "cooldown": 0, "last_used": 0, "width": 13, "speed": 8, "range": 4000, "bullets": 24, "effects": {"glued":[160,0.33]}, "type":["normal_yellow"]}}],


            # --- THE VOID ---

            "voidling": [0,0,10940,14,"enemy",2.4,7851,80,100,"void","to_player_normal",
                {"spawn": {"enemy_name":"voidling","amount" : 1,"cooldown": 3.0, "last_used": 0},
                 "death_spiral": {"damage": 5608, "cooldown": 0, "last_used": 0, "width": 12, "speed": 12, "range": 3000, "bullets": 3, "effects": {"confusion":[30,0.5]}, "type":["flower_pink"]}}],

            "red_crystal": [0,0,32800,25,"enemy",1.5,5608,200,50,"void","away_player_normal",
                {"shotgun":{"damage": 8972, "cooldown": 2.1, "last_used": 0, "width": 16, "speed": 12, "range": 3500, "recoil": 40, "bullets": 8, "effects": {"burn":[180,336]}, "type":["flower_orange"]},
                 "basic": {"telegraph": 30, "damage": 12337, "cooldown": 1.7, "last_used": 0, "width": 24, "speed": 18, "range": 3600, "effects": {"burn":[180,336]}, "type":["flower_orange"]}}],

            "purple_crystal": [0,0,32800,25,"enemy",1.8,5608,250,50,"void","random_normal",
                {"death_spawn": {"amount": 1, "enemy_name": "voidling"},
                "spiral": {"damage": 5608, "cooldown": 2.2, "last_used": 0, "width": 10, "speed": 8, "range": 4000, "bullets": 32, "effects": {"confusion":[30,1.0]}, "type":["flower_pink"]}}],

            "blue_crystal": [0,0,24600,30,"enemy",1.1,10094,300,100,"void","to_player_normal",
                {"death_spiral": {"damage": 5608, "cooldown": 0, "last_used": 0, "width": 16, "speed": 14, "range": 3200, "bullets": 12, "effects": {"slow":[120,0.8]}, "type":["flower_blue"]},
                "basic": {"damage": 5608, "cooldown": 2.5, "last_used": 0, "width": 18, "speed": 12, "range": 3400, "effects": {"confusion":[80,0.5]}, "type":["arrow_blue"]}}]
        }
            
        self.bosses = {
            "boss1": [900, 900,10,40,"boss",4.2,5,200,0,"undead","to_player",{"basic" : {"damage": 3, "cooldown": 2.0, "last_used": 0, "width": 30, "speed": 9, "range": 2000, "effects" : {"homing":[2],"slow":[180,0.1]}, "type":["missile_blue"]}, 
                                                "spiral1" : {"damage": 2, "cooldown": 3.2, "last_used": 0, "width": 24, "speed": 6, "range": 2000, "bullets": 12, "effects" : {"poison" : [600,2]}, "type":["normal_green"]},
                                                "spiral2" : {"damage": 1, "cooldown": 2.8, "last_used": 0, "width": 8, "speed": 7, "range": 2000, "bullets": 36, "effects" : {"glued" : [60,0.5]}, "type":["normal_yellow"]},
                                                "minigun": {"damage": 1,"cooldown": 2.5,"last_used": 0,"width": 8,"speed": 10,"burst_count": 0,"burst_max": 30,"burst_delay": 0.03,"last_shot": 2500,"is_bursting": False, "range": 2000, "effects" : {"confusion" : [180,0.5]},"type":["bullet_blue"]}}]
        }
        # shared with the rest of the game when passed in (projectile images loaded once)
        self.bullet_type_info = bullet_type_info if bullet_type_info is not None else BulletTypes()

        # ITEM DROPS: enemy name -> [(item name, chance 0-1), ...]
        # rolled once per killed enemy; items are given only if the fight is won
        # (6.11 distribution, see BALANCE.md) - some of the best items come ONLY from here (loot weight 0).
        # An item you already have isn't dropped again. Luck: +25% chance per point (loot.LUCK_DROP).
        self.drops = {
            "slime_small": [("Toy Rifle", 0.04)],
            "slime_big": [("Toy Rifle", 0.04)],
            "rainbow_guard": [("Rifle A2", 0.02)],
            "rainbow_slime": [("Normal Blaster", 0.02)],
            "flower_spitter": [("Rose", 0.10)],
            "candy_shroom": [("Bubble Gun", 0.02)],
            "gum_goblin": [("Tape", 0.04)],
            "toy_soldier": [("Rifle A4", 0.04)],
            "robo-bomber": [("G-Launcher", 0.04)],
            "portable_factory": [("Blaster 2.0", 0.04)],
            "frozen_orb": [("Liquidator Hose", 0.04), ("Frost Armor", 0.04)],
            "ice_shooter": [("Frozen Ring", 0.05), ("Ice Mix", 0.05), ("Golden Chestplate", 0.04)],
            "inferno_flower": [("RPG", 0.04)],
            "frost_flower": [("Ultra Blaster", 0.04)],
            "poison_skeleton": [("Laser Cannon 2.0", 0.04), ("Plate Armor", 0.04)],
            "pixie": [("Magic Dust", 0.04)],
            "toxic_flower": [("Tribe Armor", 0.04)],
            "skeleton": [("Samurai God", 0.04)],
            "generator": [("Laser Arrow", 0.04), ("Mecha Armor", 0.04)],
            "liche": [("Ghost USP", 0.04)],
            "voidling": [("Ghost Rifle", 0.02), ("Ghost Armor", 0.02)],
            "purple_crystal": [("Ghost Shotgun", 0.02)],
            "red_crystal": [("Missile-3000", 0.02), ("Fallen knight armor", 0.02)],
            "blue_crystal": [("Laser SMG v2", 0.02), ("Mecha-King Armor", 0.02)],
        }
        self.luck = 0                   # set by Game before each fight (Game.luck())
        # QUEST DROPS: enemy name -> [(item name, chance, quest id[, max owned]), ...]
        # only while that quest is active and the player has fewer than "max owned" (default 1) - at most one per fight
        self.quest_drops = {
            "sugar_caster": [("Sugar Crystal", 0.05, "gus")],
            "robo-tesla": [("Fuse", 0.25, "foreman")],
            "toxic_flower": [("Glowing Sprout", 0.25, "gardener", 3)],      # (.., max you may own: 3 sprouts)
        }
        self.active_quests = set()      # set by Game before each fight
        self.skip_items = set()         # items the player already has (set by Game before each fight)
        self.dropped_now = set()        # quest items already dropped in this fight (one per fight)
        self.owned_counts = {}          # how many of each item the player has (set by Game before each fight)
        self.sfx = sfx

    def get_enemy(self, name):
        e = self.enemies[name]
        enemy = Enemy(*e[:-1],copy.deepcopy(e[-1]),self.sfx, self.bullet_type_info)
        enemy.name = name   # needed for drops
        return enemy
    def get_boss(self, name):
        b = self.bosses[name]
        enemy = Enemy(*b[:-1],copy.deepcopy(b[-1]),self.sfx, self.bullet_type_info)
        enemy.name = name
        return enemy

    def roll_drops(self, enemy):
        dropped = []
        for item_name, chance in self.drops.get(enemy.name, []):
            if item_name in self.skip_items or item_name in self.dropped_now:
                continue                # you have it already / it dropped in this fight
            if random.random() < chance * (1 + LUCK_DROP * self.luck):
                dropped.append(item_name)
                self.dropped_now.add(item_name)
        for item_name, chance, quest, *limit in self.quest_drops.get(enemy.name, []):
            enough = self.owned_counts.get(item_name, 1 if item_name in self.skip_items else 0) >= (limit[0] if limit else 1)
            if quest in self.active_quests and not enough and item_name not in self.dropped_now and random.random() < chance:
                dropped.append(item_name)
                self.dropped_now.add(item_name)
        return dropped

    def provoke_enemies(self, biome, hard_mode, screen):
        money = 0
        w = screen.get_width()
        h = screen.get_height()
        spawnpoints = []
        for i in range(3):  
            for j in range(3):
                
                if i == 1 and j == 1:
                    continue
                    
                spawn_x = min(w-90,max(90, j * (w // 2)))
                spawn_y = min(h-90,max(90, i * (h // 2)))
                
                spawnpoints.append((spawn_x, spawn_y))

        provoked_enemies = []
        # lower end_point of spawn amount should be at least 1 lower than upper end_point (it is chosen at random({lower},{upper}))
        # biome : [[{lower spawn amount},{upper spawn amount}, [enemies]]]
        biomes = {
            "village": [[1,3],["slime_small","slime_big","shooter"]],
            "rainbow_fields": [[1,4],["rainbow_slime","flower_spitter","rainbow_guard"]],
            "sugarwood_grove": [[2,4],["gum_goblin","candy_shroom","toffee_runner","sugar_caster"]],
            "toy_factory": [[3,5],["toy_soldier","portable_factory","robo-tesla","robo-bomber","scrap_beetle"]],
            "silverpine_tundra": [[3,5],["frost_wolf","ice_shooter","frozen_orb"]],
            "underground_garden": [[3,6],["pixie","rainbow_pixie","poison_skeleton","inferno_flower","frost_flower","toxic_flower"]],
            "the_core": [[3,6],["liche","skeleton","guard","fly","generator"]],
            "the_void": [[4,6],["voidling","red_crystal","purple_crystal","blue_crystal"]],
        }

        rnd = random.randint(biomes[biome][0][0]+(1 if hard_mode else 0),biomes[biome][0][1])
        for i in range(rnd):

            rnd_enemy_name = random.choice(biomes[biome][1])
            enemy = self.get_enemy(rnd_enemy_name)

            point = random.choice(spawnpoints)
            spawnpoints.remove(point)

            enemy.x = point[0]
            enemy.y = point[1]

            enemy.color = (random.randint(100,200),random.randint(100,200),random.randint(100,200))
            provoked_enemies.append(enemy)

            money += enemy.money

        return provoked_enemies, money
