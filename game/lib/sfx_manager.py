import pygame

import pygame
import time

class SFXManager:
    def __init__(self):
        self.sfx = {}
        self.sfx_volume = 1.0
        self.last_played_time = {} 
        
    def load_sfx(self, name, path):
        self.sfx[name] = pygame.mixer.Sound(path)
        self.last_played_time[name] = 0.0

    def play(self, name, volume=1.0):
        if name not in self.sfx:
            print("No SFX found")
            return

        # NOT pygame.mixer.find_channel(): it ignores reserved channels, so a sound could land on channel 0
        # (dialogue talk sounds) and get cut off by the next typed letter = only a short click.
        # Sound.play() only uses free, NOT reserved channels.
        channel = self.sfx[name].play()
        if channel:
            current_time = time.time()
            time_passed = current_time - self.last_played_time[name]

            if time_passed < 0.125:
                volume_modifier = max(0.20, time_passed * 8.0)
            else:
                volume_modifier = 1.0 
            
            final_volume = self.sfx_volume * volume_modifier * volume
            
            channel.set_volume(final_volume)
            
            self.last_played_time[name] = current_time
        else:

            pygame.mixer.Channel(0).set_volume(self.sfx_volume * 0.05)
            pygame.mixer.Channel(0).play(self.sfx[name])

    def stop(self, name=None):
        if name in self.sfx:
            self.sfx[name].stop()
        else:
            for sfx in self.sfx.values():
                sfx.stop()

    def update_volume(self):
        for sfx in self.sfx.values():
            sfx.set_volume(self.sfx_volume)
