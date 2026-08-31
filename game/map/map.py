import pygame

class Map:
    def __init__(self, screen):
        self.layout = ["1122111221","1111122111","2221121111","1211111121","1112221111","1111111111","1111111111","1111111111","1111111131","1111111111"]
        self.tile_size = 128
        self.player = None
        self.screen = screen
        self.collision_tiles = []
        self.boss_tiles = {}

    def draw(self, screen):
        self.boss_tiles = {}
        self.collision_tiles = []
        self.screen.fill((0, 0, 0))
        camera_x = self.player.x - screen.get_width() // 2
        camera_y = self.player.y - screen.get_height() // 2

        for y, row in enumerate(self.layout):
            for x, char in enumerate(row):
                world_x = x * self.tile_size
                world_y = y * self.tile_size

                screen_x = world_x - camera_x
                screen_y = world_y - camera_y

                if char == "1":
                    pygame.draw.rect(screen,(40, 210, 40),(screen_x, screen_y, self.tile_size, self.tile_size))
                elif char == "2":
                    self.collision_tiles.append(pygame.Rect(x*self.tile_size,y*self.tile_size,self.tile_size, self.tile_size))
                    pygame.draw.rect(screen,(210, 40, 40),(screen_x, screen_y, self.tile_size, self.tile_size))
                elif char == "3":
                    self.boss_tiles["boss1"] = pygame.Rect(x*self.tile_size,y*self.tile_size,self.tile_size, self.tile_size)
                    pygame.draw.rect(screen,(40, 40, 210),(screen_x, screen_y, self.tile_size, self.tile_size))

    def can_move_to(self, x, y):
        for tile in self.collision_tiles:
            if tile.collidepoint(x, y):
                return False
        for key, tile in self.boss_tiles.items():
            if tile.collidepoint(x, y):
                return key
        return True

