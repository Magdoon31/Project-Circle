import pygame

class sfx_manager:
    def __init__(self):
        self.sfx = {}
    def load_sfx(self, name, path):
        self.sfx[name] = pygame.mixer.Sound(path)
    def play_sfx(self, name):
        if name in self.sfx:
            self.sfx[name].play()