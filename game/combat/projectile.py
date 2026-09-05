import copy

import pygame, math

class projectile:
    def __init__(self, x, y, target_x, target_y, speed, damage, player, width, range, color = (180,180,0), effects = {}):
        self.x = x
        self.y = y
        self.speed = speed
        self.damage = damage
        self.type = player
        self.width = width
        self.color = color
        self.range = range
        self.shot_time = pygame.time.get_ticks()
        self.effects = effects
        self.target_x = target_x
        self.target_y = target_y
        self.vx = 0
        self.vy = 0

        self.set_velocity()

    def set_velocity(self):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        length = math.sqrt(dx**2 + dy**2)

        if length != 0:
            self.vx = dx / length * self.speed
            self.vy = dy / length * self.speed
        else:
            self.vx = 0
            self.vy = 0

    def check_duration(self):
        if pygame.time.get_ticks() - self.shot_time < self.range and self.shot_time != 0:
            return True
        return False
        
    def update(self):
        if self.effects:
            for effect in self.effects:
                if effect == "bubble":
                    self.speed -= 0.25
                    if self.speed < 0:
                        self.speed = 0
                    self.set_velocity()

        
        self.x += self.vx
        self.y += self.vy

    def draw(self,screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.width)

    def check_collision(self, target):
        distance = math.sqrt((self.x - target.x) ** 2 + (self.y - target.y) ** 2)
        return distance < target.width
    
    def deal_damage(self, target):
        if self.check_collision(target) and target.type != self.type:
            target.take_damage(self.damage,copy.deepcopy(self.effects))
            return True
        return False