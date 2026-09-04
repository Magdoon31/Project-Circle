from game.combat.enemy.enemy import Enemy

class EnemyDB:
    def __init__(self):
        self.enemies = {
            "circle" : Enemy(0,0,100,40,"enemy",5,10,{"basic" : {"damage": 20, "cooldown": 1000, "last_used": 1000, "width": 10, "speed": 10, "range": 1000}}),
            "fast" : Enemy(0,0,60,30,"enemy",5,10,{})
            }
    def get_enemy(self, name):
        return self.enemies[name]