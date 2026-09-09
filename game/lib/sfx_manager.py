import pygame

class SFXManager:
    def __init__(self):
        self.sfx = {}
        self.sfx_volume = 1.0
    def load_sfx(self, name, path):
        self.sfx[name] = pygame.mixer.Sound(path)
    def play(self, name):
        channel = pygame.mixer.find_channel()
        if name in self.sfx:
            if channel:
                channel.play(self.sfx[name])
            else:
                print("Too many SFX to play!!")
        else:
            print("No SFX found")
    def stop(self, name=None):
        if name in self.sfx:
            self.sfx[name].stop()
        else:
            for sfx in self.sfx.values():
                sfx.stop()
    def update_volume(self):
        for sfx in self.sfx.values():
            sfx.set_volume(self.sfx_volume)
