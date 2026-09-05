from game.combat.enemy.enemy import Enemy
import copy, random, math

class EnemyDB:
    def __init__(self):
        self.enemies = {
            "circle" : [0,0,70,30,"enemy",3,10,{"basic" : {"damage": 20, "cooldown": 500, "last_used": 0, "width": 10, "speed": 12, "range": 1500}}],
            "fast" : [0,0,30,25,"enemy",6.5,10,{"death_spiral": {"damage": 20, "cooldown": 0, "last_used": 0, "width": 15, "speed": 5, "range": 3500}}],
            "turret" : [0,0,150,40,"enemy",0,20,{"basic": {"damage": 40, "cooldown": 800, "last_used": 0, "width": 15, "speed": 16, "range": 3500},
                                              "spinner": {"damage": 10, "cooldown": 1800, "last_used": 0, "width": 5, "speed": 5, "range": 4000, "bullets": 18}}]
            }
        self.bosses = {
            "boss1": [900, 900,500,40,"boss",5,200,{"basic" : {"damage": 30, "cooldown": 2000, "last_used": 2000, "width": 30, "speed": 9, "range": 2000}, 
                                                "spinner" : {"damage": 20, "cooldown": 3200, "last_used": 3200, "width": 24, "speed": 6, "range": 2000, "bullets": 12},
                                                "spinner" : {"damage": 10, "cooldown": 2800, "last_used": 2800, "width": 8, "speed": 7, "range": 2000, "bullets": 36},
                                                "minigun": {"damage": 10,"cooldown": 2500,"last_used": 2500,"width": 8,"speed": 10,"burst_count": 0,"burst_max": 30,"burst_delay": 30,"last_shot": 2500,"is_bursting": False, "range": 2000}}]
        }

    def get_enemy(self, name):
        e = self.enemies[name]
        return Enemy(*e[:-1],copy.deepcopy(e[-1]))
    def get_boss(self, name):
        b = self.bosses[name]
        return Enemy(*b[:-1],copy.deepcopy(b[-1]))

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
            "village": [[8,9],["circle", "fast"]],
            "rainbow_fields": [[1,3],[]],
            "sugarwood_grove": [[1,3],[]],
            "toy_factory": [[3,4],[]],
            "silverpine_tundra": [[2,4],[]],
            "underground_garden": [[2,5],[]],
            "the_core": [[2,3],[]],
            "the_void": [[3,4],[]],
            "pale_world": [[6,8],[]],
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
