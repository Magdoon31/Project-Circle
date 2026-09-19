import pygame, math

class BulletTypes:

    def __init__(self):
        self.img = {}
        self.bullet_types = [
            "normal_red", "normal_blue", "normal_yellow", "normal_green","mine_red",
            "bullet_red", "bullet_blue", "bullet_green", "bullet", "ghost_bullet", "acid",
            "laser_red", "laser_blue", "laser_purple", "laser_green", "laser_yellow", "grenade_red",
            "missile_red", "missile_blue", "nail", "water", "bubble", "arrow_blue", "arrow_red",
            "spore", "flower_green", "flower_orange", "flower_pink", "flower_blue", "bullet_gold"
            
        ]
        for b_type in self.bullet_types:
            img = pygame.image.load(f"assets/img/combat/projectiles/{b_type}.png").convert_alpha()
            self.img[b_type] = img