import pygame, math, random
from game import controls as KEYS

ENCOUNTER_CHANCE = 0.0015   # per frame of walking on grass (~1 fight every 15 s of walking)

CONVEYOR_SPEED = 0.55   # how strongly conveyor belts push the player (x player speed)

# smooth movement: the velocity eases towards the wanted one instead of jumping to it
ACCELERATION = 0.25   # 0..1 per frame, how fast the player speeds up / turns (lower = more slide)
FRICTION = 0.1       # 0..1 per frame, how fast the player stops after releasing the keys


class Player:
    def __init__(self, x, y, map):
        self.x = x                 # world pixels (centre of the player)
        self.y = y
        self.map = map
        self.speed = max(4, map.tile_size // 14)
        self.radius = map.tile_size * 0.3
        self.encounter_grace = 0   # frames without random fights (e.g. after running away)
        self.vx = 0.0              # current velocity (pixels / frame)
        self.vy = 0.0
        self.money = 0
        self.biome = "village"
        self.play_time = 0

    def draw(self, screen):
        pygame.draw.circle(screen, (200, 200, 50), (screen.get_width() // 2, screen.get_height() // 2), self.radius)
        pygame.draw.circle(screen, (90, 80, 20), (screen.get_width() // 2, screen.get_height() // 2), self.radius, 2)
        self.play_time += 1/60

    def move(self, keys):
        """Moves the player. Returns "fight" when a random fight starts, otherwise None."""
        vx = 0
        vy = 0
        vy = KEYS.held(keys, "down") - KEYS.held(keys, "up")      # (11.11) the keys come from Settings (controls.py)
        vx = KEYS.held(keys, "right") - KEYS.held(keys, "left")

        # biome = biome of the tile under the player (also right after a teleport / load)
        biome = self.map.biome_at(self.x, self.y)
        if biome:
            self.biome = biome

        length = math.sqrt(vx*vx + vy*vy)
        if length != 0:
            vx /= length
            vy /= length
            ease = ACCELERATION
        else:
            ease = FRICTION
        # move the velocity a part of the way towards the wanted velocity -> smooth start, turn, stop
        self.vx += (vx * self.speed - self.vx) * ease
        self.vy += (vy * self.speed - self.vy) * ease
        if abs(self.vx) < 0.05:
            self.vx = 0.0
        if abs(self.vy) < 0.05:
            self.vy = 0.0
        # conveyor belt under the player pushes in its direction (on top of walking)
        push = self.map.conveyor_push(self.x, self.y)
        px, py = (push[0] * self.speed * CONVEYOR_SPEED, push[1] * self.speed * CONVEYOR_SPEED) if push else (0.0, 0.0)
        if self.vx == 0 and self.vy == 0 and not push:
            return None

        old = (self.x, self.y)
        # x and y separately -> the player slides along walls instead of sticking
        new_x = self.x + self.vx + px
        if self.map.can_stand(new_x, self.y, self.radius):
            self.x = new_x
        else:
            self.vx = 0.0
        new_y = self.y + self.vy + py
        if self.map.can_stand(self.x, new_y, self.radius):
            self.y = new_y
        else:
            self.vy = 0.0

        moved = (self.x, self.y) != old
        biome = self.map.biome_at(self.x, self.y)
        if biome:
            self.biome = biome
        if self.encounter_grace > 0:
            self.encounter_grace -= 1
        elif moved and self.map.encounter_allowed(self.x, self.y) and random.random() < ENCOUNTER_CHANCE:
            return "fight"
        return None

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.vx = self.vy = 0.0   # teleport / respawn: no leftover sliding
