import os
import pygame

# OPTIONAL music: loaded only if the file exists (placeholders for music that isn't made yet)
# a list = the first file that exists
OPTIONAL_MUSIC = {"dialogue": "assets/music/dialogue/dialogue.mp3",
                  "minigame": ["assets/music/minigame.mp3", "assets/music/minigames/minigame.mp3"],   # while playing a minigame
                  "lunapark": "assets/music/biomes/lunapark.mp3",
                  "nowhere": "assets/music/biomes/nowhere.mp3"}      # below the pale Garden (pale_world.py)
# PLACEHOLDER: music that isn't there yet -> this one plays instead
MUSIC_FALLBACK = {"lunapark": "sugarwood_grove"}

class MusicManager:
    def __init__(self):
        self.music = {"menu_intro": pygame.mixer.Sound("assets/music/menu/menu_intro.mp3"),
                      "menu_loop": pygame.mixer.Sound("assets/music/menu/menu_loop.mp3"),
                      "rainbow_fields": pygame.mixer.Sound("assets/music/biomes/rainbow_fields.mp3"),
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
        for name, paths in OPTIONAL_MUSIC.items():
            path = next((p for p in ([paths] if isinstance(paths, str) else paths) if os.path.exists(p)), None)
            if path:
                self.music[name] = pygame.mixer.Sound(path)
        self.music_volume = 1.0
        self.current = None          # name of the music playing now (biome / boss / menu ...)
        self.channel = None          # its channel (needed to pause it and come back at the same place)
        self.overlay = None          # music played OVER it for a while (the shop): see fade_to / fade_back
        self.fade = None             # [direction "in"/"out", frames done, frames total]

    def mute(self, on):
        # horror moments in dialogues: the music goes silent, then comes back at the same place
        for music in self.music.values():
            music.set_volume(0.0 if on else self.music_volume)

    def has(self, name):
        return name in self.music

    def load(self, name, path):
        """(8.11) Loads a track on demand (big boss tracks: only when the fight starts). False if the file isn't there."""
        if name not in self.music:
            if not os.path.exists(path):
                return False
            self.music[name] = pygame.mixer.Sound(path)
            self.music[name].set_volume(self.music_volume)
        return True

    def crossfade(self, name, ms=1500):
        """(8.11) The music playing now fades out while `name` fades in (boss phases)."""
        if name not in self.music or name == self.current:
            return
        if self.current in self.music:
            self.music[self.current].fadeout(ms)
        self.channel = self.music[name].play(-1, fade_ms=ms)
        self.current = name

    def play_once(self, name):
        """(10.11) Plays a track once, from the start (a song fight: the fight ends with the song)."""
        if name in self.music:
            self.channel = self.music[name].play(0)
            self.current = name
            if self.channel:
                self.channel.set_volume(1.0)

    def play(self, name):
        if name not in self.music:
            name = MUSIC_FALLBACK.get(name, name)
        if name in self.music:
            self.channel = self.music[name].play(-1)
            self.current = name
            if self.channel:
                self.channel.set_volume(1.0)

    # --- a second music OVER the current one (the shop) -----------------------------------------
    # fade_to: the current music fades out and PAUSES, the other one fades in.
    # fade_back: the other one fades out, the old one goes on from where it was (not from the start).
    def fade_to(self, name, ms=1000):
        if name not in self.music or self.overlay:
            return
        self.overlay = name
        self.music[name].play(-1, fade_ms=ms)
        self.fade = ["in", 0, max(1, ms * 60 // 1000)]

    def fade_back(self, ms=1000):
        if not self.overlay:
            return
        self.music[self.overlay].fadeout(ms)
        self.overlay = None
        if self.channel:
            self.channel.unpause()
        self.fade = ["out", 0, max(1, ms * 60 // 1000)]

    def update(self):
        """Once per frame: moves the fade along."""
        if not self.fade:
            return
        direction, done, total = self.fade
        done += 1
        p = min(1.0, done / total)
        if self.channel:
            self.channel.set_volume(1.0 - p if direction == "in" else p)
            if direction == "in" and p >= 1.0:
                self.channel.pause()                 # waits here until fade_back
        self.fade = None if p >= 1.0 else [direction, done, total]
    def fade_out(self, ms):
        """The music playing now goes quiet over `ms` and stops (e.g. before a minigame's countdown)."""
        if self.current in self.music:
            self.music[self.current].fadeout(ms)
        self.current = self.channel = None

    def stop(self, name=None):
        if name in self.music:
            self.music[name].stop()
        else:
            for music in self.music.values():
                music.stop()
            self.overlay = self.fade = None
            self.current = self.channel = None
    def update_volume(self):
        for music in self.music.values():
            music.set_volume(self.music_volume)
