import pygame, math, random


class Player:
    def __init__(self, x, y, map):
        self.x = x
        self.y = y
        self.speed = 6
        self.map = map
        self.money = 0
        self.biome = "village"
        self.play_time = 0

    def draw(self, screen):
        pygame.draw.circle(screen, (200, 200, 50), ((screen.get_width()//2) - 5, (screen.get_height()//2) - 5), 10)
        self.play_time += 1/60
    def move(self, keys):
        interaction = None
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

        x = self.x + vx * self.speed
        y = self.y + vy * self.speed
        new_x = self.x
        new_y = self.y

        move_x = self.map.can_move_to(x, self.y)
        if move_x == True:
            new_x = x
        elif move_x not in (True, False):
            interaction = move_x

        move_y = self.map.can_move_to(self.x, y)
        if move_y == True:
            new_y = y
        elif move_y not in (True, False):
            interaction = move_y

        if new_x != self.x or new_y != self.y:
            rnd = random.random()
            print(rnd)
            if rnd < 0.0015:
                return "fight"

        self.set_position(new_x,new_y)

        if interaction:
            return interaction

    def set_position(self, x, y):
        self.x = x
        self.y = y
