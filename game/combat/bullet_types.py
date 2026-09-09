import pygame, math

class BulletTypes:

    def __init__(self):
        self.img = {}
        self.bullet_types = [
            "normal_red", "normal_blue", "normal_yellow", "normal_green", "ghost_bullet",
            "laser_red", "laser_blue", "laser_purple", "laser_green",
            "missile_red", "missile_blue", "nail", "water", "bubble","spore"
        ]
        for b_type in self.bullet_types:
            img = pygame.image.load(f"assets/img/combat/projectiles/{b_type}.png").convert_alpha()
            self.img[b_type] = img