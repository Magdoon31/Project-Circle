import pygame

class MusicManager:
    def __init__(self):
        self.music = {"menu": pygame.mixer.Sound("assets/music/menu/menu.mp3"),
                      "rainbow_hills": pygame.mixer.Sound("assets/music/biomes/rainbow_fields.mp3"),
                      "village": pygame.mixer.Sound("assets/music/biomes/village.mp3"),
                      "sugarwood_grove": pygame.mixer.Sound("assets/music/biomes/sugarwood_grove.mp3"),
                      "toy_factory": pygame.mixer.Sound("assets/music/biomes/toy_factory.mp3"),
                      "silverpine_tundra": pygame.mixer.Sound("assets/music/biomes/silverpine_tundra.mp3"),
                      "underground_garden": pygame.mixer.Sound("assets/music/biomes/underground_garden.mp3"),
                      "the_core": pygame.mixer.Sound("assets/music/biomes/the_core.mp3"),
                      "the_void": pygame.mixer.Sound("assets/music/biomes/the_void.mp3"),
                      "pale_world": pygame.mixer.Sound("assets/music/biomes/pale_world.mp3"),
                      "shop": pygame.mixer.Sound("assets/music/biomes/shop.mp3"),
                      "boss_fight1": pygame.mixer.Sound("assets/music/combat/boss_fight1.mp3"),
                      "boss_fight2": pygame.mixer.Sound("assets/music/combat/boss_fight2.mp3"),
                      "final_boss_fight": pygame.mixer.Sound("assets/music/combat/final_boss_fight.mp3")}
        self.music_volume = 1.0

    def play(self, name):
        if name in self.music:
            self.music[name].play(-1)
    def stop(self, name=None):
        if name in self.music:
            self.music[name].stop()
        else:
            for music in self.music.values():
                music.stop()
    def update_volume(self):
        for music in self.music.values():
            music.set_volume(self.music_volume)