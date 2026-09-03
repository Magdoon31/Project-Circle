import pygame, math


class Player:
    def __init__(self, x, y, map):
        self.x = x
        self.y = y
        self.speed = 8
        self.map = map
        self.money = 0
        self.biome = "toy_factory"

    def draw(self, screen):
        pygame.draw.circle(screen, (200, 200, 50), ((screen.get_width()//2) - 5, (screen.get_height()//2) - 5), 10)
    def move(self, keys):
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
        new_x = self.x + vx * self.speed
        new_y = self.y + vy * self.speed
        if self.map.can_move_to(new_x,new_y) == True:

            self.set_position(new_x,new_y)
        if self.map.can_move_to(new_x,new_y) not in (True,False):
            return self.map.can_move_to(new_x,new_y)

    def set_position(self, x, y):
        self.x = x
        self.y = y
