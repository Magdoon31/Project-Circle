from game.combat.enemy.enemy import Enemy
from game.combat.bullet_types import BulletTypes
import copy, random, math

class EnemyDB:
    def __init__(self, sfx):
        self.enemies = {
             # --- VILLAGE ---

            "slime_small": [0,0,12,18,"enemy",3.4,6,4,0,"mystical","to_player_normal",{"mine":{"damage": 10, "radius": 120, "cooldown": 2.1, "last_used": 0, "width": 15, "exp_time": 4.2, "effects": {}, "type": ["mine_red"]}}],

            "slime_big": [0,0,60,36,"enemy",2.0,12,12,0,"mystical","to_player_jump",{"death_spawn":{"amount":2,"enemy_name":"slime_small"}}],

            "shooter": [0,0,40,22,"enemy",3.2,5,10,0,"human","away_player_distance",
                {"shotgun": {"damage": 12, "cooldown": 2.2, "last_used": 0, "width": 14, "speed": 16, "range": 3200,"bullets":6,"recoil":40, "effects": {}, "type":["arrow_red"]}}],


            # --- RAINBOW FIELDS ---

            "rainbow_slime": [0,0,80,24,"enemy",3.8,8,12,1,"mystical","to_player_jump",
                {"death_spiral": {"bullets":4,"damage": 18, "width": 13, "speed": 6, "range": 4000, "effects": {}, "type":["normal_yellow","normal_red","normal_green","nromal_blue"]}}],

            "flower_spitter": [0,0,140,23,"enemy",1.0,6,10,0,"animal","away_player_normal",
                {"basic": {"damage": 22, "cooldown": 2.2, "last_used": 0, "width": 12, "speed": 8, "range": 3600, "effects": {"slow":[45,0.15],"homing":[0.2]}, "type":["flower_pink"]}}],

            "rainbow_guard": [0,0,140,30,"enemy",1.5,14,14,4,"human","to_player_normal",
                {"basic": {"damage": 12, "cooldown": 1.0, "last_used": 0, "width": 16, "speed": 14, "range": 750, "effects": {}, "type":["nail"]}}],


            # --- SUGARWOOD GROVE ---

            "gum_goblin": [0,0,200,28,"enemy",4.8,4,16,0,"animal","to_player_distance",
                {"basic": {"damage": 16, "cooldown": 1.6, "last_used": 0, "width": 13, "speed": 16, "range": 1800, "effects": {"glued":[60,0.25]}, "type":["normal_green"]}}],

            "candy_shroom": [0,0,280,24,"enemy",0.8,8,20,1,"plant","random_normal",
                {"spiral": {"damage": 6, "cooldown": 2.1, "last_used": 0, "width": 9, "speed": 8, "range": 3500, "bullets": 12, "effects": {"poison":[185,2]}, "type":["spore"], "stop_move":[60,32]}}],

            "toffee_runner": [0,0,120,18,"enemy",3.5,12,10,4,"animal","to_player_zigzag",{}],

            "sugar_caster": [0,0,100,25,"enemy",2.3,10,22,2,"mystical","away_player_normal",
                {"throw": {"radius": 75, "damage": 30, "cooldown": 2.8, "last_used": 0, "fly_time": 1.0, "effects": {"speed":[60,0.25]},"stop_move":[48,12], "type":["flower_white"]}}],


            # --- TOY FACTORY ---

            "toy_soldier": [0,0,380,23,"enemy",1.8,10,25,4,"mechanical","to_player_normal",
                {"basic": {"damage": 30, "cooldown": 1.4, "last_used": 0, "width": 16, "speed": 14, "range": 3500, "effects": {}, "type":["bullet_red"]}}],

            "portable_factory": [0,0,800,40,"enemy",0,1,50,2,"mechanical","random_normal",
                {"spawn": {"enemy_name":"toy_soldier","amount" : 1,"cooldown": 7.5, "last_used": 0},
                "spiral": {"damage": 16, "cooldown": 3.5, "last_used": 0, "width": 12, "speed": 6, "range": 3800, "bullets": 14, "effects": {}, "type":["normal_red"]}}],

            "robo-tesla": [0,0,310,23,"enemy",1.8,10,30,4,"mechanical","random_normal",
                           {"spiral": {"damage": 22, "cooldown": 1.2, "last_used": 0, "width": 5, "speed": 4, "range": 1600, "bullets": 18, "effects": {"weakness":[120,0.2]}, "type":["normal_blue"]}}],

            "robo-bomber": [0,0,310,23,"enemy",1.8,10,30,4,"mechanical","random_normal",
                            {"throw": {"radius": 100, "damage": 35, "cooldown": 3.2, "last_used": 0, "fly_time": 0.8, "effects": {"burn":[60,2]}, "type":["grenade_red"]}}],
                           
            "scrap_beetle": [0,0,50,14,"enemy",5.2,20,20,5,"mechanical","to_player_normal",
                {"mine": {"damage": 45, "radius": 55, "cooldown": 1.5, "last_used": 0, "width": 15, "exp_time": 2500, "effects": {}, "type": ["mine_red"]}}],


            # --- SILVERPINE TUNDRA ---

            "frost_wolf": [0,0,250,26,"enemy",3.4,30,30,4,"animal","to_player_normal",{}],

            "ice_shooter": [0,0,400,26,"enemy",1.1,15,32,0,"human","away_player_normal",
                {"basic": {"damage": 16, "cooldown": 1.4, "last_used": 0, "width": 12, "speed": 22, "range": 4500, "effects": {"slow":[45,0.55]}, "type":["arrow_blue"]}}],

            "frozen_orb": [0,0,290,28,"enemy",0.8,12,30,10,"mystical","random_normal",
                {"spiral": {"damage": 22, "cooldown": 2.4, "last_used": 0, "width": 14, "speed": 8, "range": 4000, "bullets": 8, "effects": {"slow":[60,0.55],"homing":[0.12]}, "type":["normal_blue"]},
                 "death_spiral": {"damage": 22, "cooldown": 0, "last_used": 0, "width": 14, "speed": 8, "range": 4000, "bullets": 16, "effects": {"slow":[60,0.55],"homing":[0.12]}, "type":["normal_blue"]}}],

            "tundra_watcher": [0,0,900,35,"enemy",1.2,20,45,6,"human","random_normal",
                {"shotgun":{"damage": 20, "cooldown": 2.4, "last_used": 0, "width": 16, "speed": 20, "range": 4000, "recoil": 60, "bullets": 5, "effects": {"slow":[50,0.3]}, "type":["laser_blue"]},
                "basic": {"damage": 35, "cooldown": 1.4, "last_used": 0, "width": 20, "speed": 20, "range": 4000, "effects": {}, "type":["laser_blue"]}}],


            # --- UNDERGROUND GARDEN ---

            "pixie": [0,0,800,24,"enemy",2.5,40,70,4,"mystical","random_jump",
                {"minigun": {"damage": 25,"cooldown": 2.5,"last_used": 0,"width": 18,"speed": 9,"burst_count": 0,"burst_max": 10,"burst_delay": 0.05,"last_shot": 0,"is_bursting": False, "spread": 360, "range": 3000, "effects" : {"confusion":[120,0.75],"slow":[180,0.25]},"type":["normal_yellow"]}}],

            "rainbow_pixie": [0,0,60,24,"enemy",1.5,40,200,0,"mystical","random_jump",
                              {"death_spiral": {"damage": 40, "cooldown": 0, "last_used": 0, "width": 18, "speed": 9, "range": 3000, "bullets": 18, "effects": {"confusion":[120,0.75],"slow":[180,0.25]}, "type":["normal_yellow","normal_green","normal_blue","normal_red"]},
                              "death_spawn": {"amount": 2, "enemy_name":"pixie"}}],

            "poison_skeleton": [0,0,1100,28,"enemy",3.1,40,85,6,"undead","away_player_normal",
                                {"basic": {"damage": 40, "cooldown": 1.8, "last_used": 0, "width": 22, "speed": 20, "range": 3800, "effects": {"poison":[240,6]}, "type":["arrow_red"]}}],

            "inferno_flower": [0,0,900,26,"enemy",0.6,40,85,5,"mystical","random_normal",
                               {"shotgun":{"damage": 25, "cooldown": 2.5, "last_used": 0, "width": 12, "speed": 12, "range": 2100, "spread": 40, "bullets": 7, "effects": {"burn":[120,3]}, "type":["flower_orange"]},
                                "basic": {"damage": 30, "cooldown": 1.9, "last_used": 0, "width": 12, "speed": 12, "range": 2100, "effects": {"homing":[0.8],"burn":[120,3]}, "type":["flower_orange"]}}],

            "frost_flower": [0,0,900,26,"enemy",0.6,40,85,5,"mystical","random_normal",
                               {"shotgun":{"damage": 25, "cooldown": 2.5, "last_used": 0, "width": 12, "speed": 12, "range": 2100, "spread": 40, "bullets": 7, "effects": {"slow":[120,0.33],"weakness":[160,0.5]}, "type":["flower_blue"]},
                                "basic": {"damage": 30, "cooldown": 1.9, "last_used": 0, "width": 12, "speed": 12, "range": 2100, "effects": {"homing":[0.8],"slow":[120,0.33],"weakness":[160,0.5]}, "type":["flower_blue"]}}],

            "toxic_flower": [0,0,900,26,"enemy",0.6,40,85,5,"mystical","random_normal",
                               {"shotgun":{"damage": 25, "cooldown": 2.5, "last_used": 0, "width": 12, "speed": 12, "range": 2100, "spread": 40, "bullets": 7, "effects": {"acid":[120,0.33],"poison":[180,8]}, "type":["flower_green"]},
                                "basic": {"damage": 30, "cooldown": 1.9, "last_used": 0, "width": 12, "speed": 12, "range": 2100, "effects": {"homing":[0.8],"acid":[120,0.33],"poison":[180,8]}, "type":["flower_green"]}}],


            # --- THE CORE ---

            "liche": [0,0,900,26,"enemy",2.5,10,120,13,"undead","away_player_normal",
                {"basic": {"damage": 50, "cooldown": 1.0, "last_used": 0, "width": 18, "speed": 12, "range": 3400, "effects": {"poison":[300,6],"confusion":[80,0.5]}, "type":["ghost_bullet"]},
                "spiral": {"damage": 30, "cooldown": 1.9, "last_used": 0, "width": 14, "speed": 10, "range": 2100, "bullets": 12, "effects": {"weakness":[300,0.3],"confusion":[80,0.5]}, "type":["ghost_bullet"]},
                "shotgun":{"damage": 30, "cooldown": 2.6, "last_used": 0, "width": 14, "speed": 10, "range": 2200, "recoil": 30, "bullets": 4, "effects": {"glued":[300,0.3],"confusion":[80,0.5]}, "type":["ghost_bullet"]}}],

            "skeleton": [0,0,300,21,"enemy",4.2,30,30,5,"undead","to_player_normal",
                      {}],

            "mecha-skeleton": [0,0,3000,35,"boss",2.5,100,400,8,"undead","random_normal",
                      {"basic": {"damage": 40, "cooldown": 2.6, "last_used": 0, "width": 28, "speed": 10, "range": 2000, "effects": {"homing":[1],"burn":[120,4]}, "type":["missile_red"]},
                       "mine": {"damage": 50, "radius": 50, "cooldown": 1.7, "last_used": 0, "width": 25, "exp_time": 5.0, "effects": {"bind":[90,0.75]}, "type": ["mine_red"]},
                       "spawn": {"enemy_name":"skeleton","amount" : 2,"cooldown": 4.9, "last_used": 0},
                       "shotgun":{"damage": 25, "cooldown": 0.8, "last_used": 0, "width": 10, "speed": 8, "range": 2000, "recoil": 60, "bullets": 4, "effects": {"burn":[120,4]}, "type":["normal_red"]}}],

            "guard": [0,0,600,22,"enemy",2.2,40,90,20,"human","to_player_normal",
                      {}],

            "fly": [0,0,100,18,"enemy",4.8,30,30,10,"animal","to_player_normal",
                      {"death_spiral": {"damage": 20, "cooldown": 0, "last_used": 0, "width": 15, "speed": 12, "range": 1600, "bullets": 8, "effects": {"poison":[180,10]}, "type":["spore"]}}],

            "generator": [0,0,600,26,"enemy",0,10,120,16,"mechanical","random_normal",
                      {"spiral": {"damage": 35, "cooldown": 1.0, "last_used": 0, "width": 13, "speed": 8, "range": 4000, "bullets": 12, "effects": {"glued":[100,0.33]}, "type":["normal_yellow"]},
                       "death_spiral": {"damage": 35, "cooldown": 0, "last_used": 0, "width": 13, "speed": 8, "range": 4000, "bullets": 24, "effects": {"glued":[160,0.33]}, "type":["normal_yellow"]}}],


            # --- THE VOID ---

            "voidling": [0,0,800,14,"enemy",2.4,70,80,15,"void","to_player_normal",
                {"spawn": {"enemy_name":"voidling","amount" : 1,"cooldown": 3.0, "last_used": 0},
                 "death_spiral": {"damage": 50, "cooldown": 0, "last_used": 0, "width": 12, "speed": 12, "range": 3000, "bullets": 3, "effects": {"confusion":[30,0.5]}, "type":["flower_pink"]}}],

            "red_crystal": [0,0,2400,25,"enemy",1.5,50,200,10,"void","away_player_normal",
                {"shotgun":{"damage": 80, "cooldown": 2.1, "last_used": 0, "width": 16, "speed": 12, "range": 3500, "recoil": 40, "bullets": 8, "effects": {"burn":[180,3]}, "type":["flower_orange"]},
                 "basic": {"damage": 110, "cooldown": 1.7, "last_used": 0, "width": 24, "speed": 18, "range": 3600, "effects": {"burn":[180,3]}, "type":["flower_orange"]}}],

            "purple_crystal": [0,0,3200,25,"enemy",1.8,50,250,12,"mechanical","random_normal",
                {"death_spawn": {"amount": 1, "enemy_name": "voidling"},
                "spiral": {"damage": 50, "cooldown": 2.2, "last_used": 0, "width": 10, "speed": 8, "range": 4000, "bullets": 32, "effects": {"confusion":[30,1.0]}, "type":["flower_pink"]}}],

            "blue_crystal": [0,0,4000,30,"enemy",1.1,90,300,25,"void","to_player_normal",
                {"death_spiral": {"damage": 50, "cooldown": 0, "last_used": 0, "width": 16, "speed": 14, "range": 3200, "bullets": 12, "effects": {"slow":[120,0.8]}, "type":["flower_blue"]}}]
        }
            
        self.bosses = {
            "boss1": [900, 900,8000,40,"boss",4.2,5,200,20,"undead","to_player",{"basic" : {"damage": 3, "cooldown": 2.0, "last_used": 0, "width": 30, "speed": 9, "range": 2000, "effects" : {"homing":[2],"slow":[180,0.1]}, "type":["missile_blue"]}, 
                                                "spinner1" : {"damage": 2, "cooldown": 3.2, "last_used": 0, "width": 24, "speed": 6, "range": 2000, "bullets": 12, "effects" : {"poison" : [600,2]}, "type":["normal_green"]},
                                                "spinner2" : {"damage": 1, "cooldown": 2.8, "last_used": 0, "width": 8, "speed": 7, "range": 2000, "bullets": 36, "effects" : {"glued" : [60,0.5]}, "type":["normal_yellow"]},
                                                "minigun": {"damage": 1,"cooldown": 2.5,"last_used": 0,"width": 8,"speed": 10,"burst_count": 0,"burst_max": 30,"burst_delay": 0.03,"last_shot": 2500,"is_bursting": False, "range": 2000, "effects" : {"confusion" : [180,0.5]},"type":["bullet_blue"]}}]
        }
        self.bullet_type_info = BulletTypes()
        self.sfx = sfx

    def get_enemy(self, name):
        e = self.enemies[name]
        return Enemy(*e[:-1],copy.deepcopy(e[-1]),self.sfx, self.bullet_type_info)
    def get_boss(self, name):
        b = self.bosses[name]
        return Enemy(*b[:-1],copy.deepcopy(b[-1]),self.sfx, self.bullet_type_info)

    def provoke_enemies(self, biome, hard_mode, screen):
        money = 0
        w = screen.get_width()
        h = screen.get_height()
        spawnpoints = []
        for i in range(1,4):
            for j in range(1,4):
                spawn_x = w//2 + j * w//6
                spawn_y = i * h//4
                spawnpoints.append((spawn_x, spawn_y))

        provoked_enemies = []
        # lower point of spawn amount should be at least 1 lower than upper point (it is chosen at random({lower},{upper}))
        # biome : [[{lower spawn amount},{upper spawn amount}, [enemies]]]
        biomes = {
            "village": [[3,6],["slime_small","slime_big","shooter"]],
            "rainbow_fields": [[1,3],["rainbow_slime","flower_spitter","rainbow_guard"]],
            "sugarwood_grove": [[1,3],["gum_goblin","candy_shroom","toffee_runner","sugar_caster"]],
            "toy_factory": [[3,4],["toy_soldier","portable_factory","robo-tesla","robo-bomber","scrap_beetle"]],
            "silverpine_tundra": [[2,4],["frost_wolf","ice_shooter","frozen_orb"]],
            "underground_garden": [[3,5],["pixie","rainbow_pixie","poison_skeleton","inferno_flower","frost_flower","toxic_flower"]],
            "the_core": [[2,3],["liche","skeleton","guard","fly","generator"]],
            "the_void": [[3,4],["voidling","red_crystal","purple_crystal","blue_crystal"]],
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
