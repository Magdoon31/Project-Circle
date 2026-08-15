import pygame, math
from lib.player.projectile import projectile as prjt

class Shooter :
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 25
        self.hp = 100
        self.speed = 10
        self.rate_of_fire = 0.5
        self.last_shot_time = 0
        self.damage = 8
        self.type = "player"

    def draw(self, screen, difficulty):
        pygame.draw.circle(screen, (200, 50, 50), (self.x, self.y), self.width)
        self.hp_bar(screen, difficulty)
    def move(self, keys, screen):
        vx = 0
        vy = 0

        if keys[pygame.K_w]:
            vy -= 1
        if keys[pygame.K_s]:
            vy += 1
        if keys[pygame.K_a]:
            vx -= 1
        if keys[pygame.K_d]:
            vx += 1

        length = math.sqrt(vx*vx + vy*vy)

        if length != 0:
            vx /= length
            vy /= length

        self.x += vx * self.speed
        self.y += vy * self.speed
        if self.x < 0 + self.width:
            self.x = 0 + self.width
        if self.x > screen.get_width()-self.width:
            self.x = screen.get_width()-self.width
        if self.y < 0 + self.width:
            self.y = 0 + self.width
        if self.y > screen.get_height()-self.width:
            self.y = screen.get_height()-self.width
    def shoot(self,type):
        if type == "basic":
            if pygame.time.get_ticks() - self.last_shot_time >= self.rate_of_fire * 1000:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                projectile = prjt(self.x, self.y, mouse_x, mouse_y, 15, self.damage, "player",10)
                self.last_shot_time = pygame.time.get_ticks()
                return projectile
        elif type == "shotgun":
            if pygame.time.get_ticks() - self.last_shot_time >= self.rate_of_fire * 1200:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                projectiles = []
                for angle in range(-90, 90, 35):
                    rad = math.radians(angle)
                    cos_a = math.cos(rad)
                    sin_a = math.sin(rad)
                    target_x = mouse_x + cos_a * 100
                    target_y = mouse_y + sin_a * 100
                    projectile = prjt(self.x, self.y, target_x, target_y, 8, self.damage//2.2, "player",5,pygame.time.get_ticks())
                    projectiles.append(projectile)
                self.last_shot_time = pygame.time.get_ticks()
                return projectiles
        return None
    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            return True
        return False
    def hp_bar(self, screen,difficulty):
        bar_width = 50
        bar_height = 5
        fill_width = int(bar_width * self.hp / (100 if difficulty == "hard" else 125 if difficulty == "medium" else 150))
        pygame.draw.rect(screen, (255, 0, 0), (self.x - bar_width // 2, self.y - self.width - 10, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (self.x - bar_width // 2, self.y - self.width - 10, fill_width, bar_height))
    

        