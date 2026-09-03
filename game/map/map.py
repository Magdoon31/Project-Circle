import pygame

class Map:
    def __init__(self, screen):
        self.layout = []
        self.tile_size = screen.get_height()//9
        self.player = None
        self.screen = screen
        self.collision_tiles = []
        self.boss_tiles = {}

    def draw(self):
        self.boss_tiles = {}
        self.collision_tiles = []
        self.screen.fill((0, 0, 0))
        camera_x = self.player.x - self.screen.get_width() // 2
        camera_y = self.player.y - self.screen.get_height() // 2

        for y, row in enumerate(self.layout):
            for x, char in enumerate(row):
                world_x = x * self.tile_size
                world_y = y * self.tile_size

                screen_x = world_x - camera_x
                screen_y = world_y - camera_y

                if char == "1":
                    pygame.draw.rect(self.screen,(40, 210, 40),(screen_x, screen_y, self.tile_size, self.tile_size))
                elif char == "2":
                    self.collision_tiles.append(pygame.Rect(x*self.tile_size,y*self.tile_size,self.tile_size, self.tile_size))
                    pygame.draw.rect(self.screen,(210, 40, 40),(screen_x, screen_y, self.tile_size, self.tile_size))
                elif char == "3":
                    self.boss_tiles["boss1"] = pygame.Rect(x*self.tile_size,y*self.tile_size,self.tile_size, self.tile_size)
                    pygame.draw.rect(self.screen,(40, 40, 210),(screen_x, screen_y, self.tile_size, self.tile_size))
        

    def can_move_to(self, x, y):
        for tile in self.collision_tiles:
            if tile.collidepoint(x, y):
                return False
        for key, tile in self.boss_tiles.items():
            if tile.collidepoint(x, y):
                return key
        return True

