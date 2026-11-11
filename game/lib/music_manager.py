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

def play_at_full_volume(sound, loops=0, fade_ms=0):
    """(11.11) Plays `sound` on a free channel at the channel's full volume. A channel keeps the volume the last
    sound effect left on it (e.g. 0.2), and a fade-in ends at the volume the channel had when it started - setting
    the volume afterwards doesn't help (the fade puts the old one back). So: find the channel, set its volume, then
    play with the fade. -> the channel (None if none is free)"""
    channel = sound.play(loops)
    if channel:
        channel.stop()
        channel.set_volume(1.0)
        channel.play(sound, loops, fade_ms=fade_ms)
    return channel


_SILENCE = []


def silence():
    """A few ms of nothing (made once, when the mixer is up)."""
    if not _SILENCE:
        _SILENCE.append(pygame.mixer.Sound(buffer=bytes(256)))
    return _SILENCE[0]


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
        self.fixed_volume = {}       # (11.11) tracks that ignore the music slider: name -> volume (the Mascot's song)
        self.current = None          # name of the music playing now (biome / boss / menu ...)
        self.channel = None          # its channel (needed to pause it and come back at the same place)
        self.overlay = None          # music played OVER it for a while (the shop): see fade_to / fade_back
        self.fade = None             # [direction "in"/"out", frames done, frames total]
        self.loop_after = None       # (11.11) the loop that follows an intro (play_with_intro)

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
            self.music[name].set_volume(self.fixed_volume.get(name, self.music_volume))
        return True

    def set_fixed_volume(self, name, volume):
        """(11.11) This track always plays at `volume`, whatever the music slider says."""
        self.fixed_volume[name] = volume
        if name in self.music:
            self.music[name].set_volume(volume)

    def crossfade(self, name, ms=1500):
        """(8.11) The music playing now fades out while `name` fades in (boss phases)."""
        if name not in self.music or name == self.current:
            return
        self.drop_queued_loop()
        if self.current in self.music:
            self.music[self.current].fadeout(ms)
        self.channel = play_at_full_volume(self.music[name], -1, ms)
        self.current = name

    def play_once(self, name):
        """(10.11) Plays a track once, from the start (a song fight: the fight ends with the song)."""
        if name in self.music:
            self.drop_queued_loop()
            self.channel = play_at_full_volume(self.music[name], 0)
            self.current = name

    def play_with_intro(self, intro, loop):
        """(11.11) The intro once, then the loop round and round - joined exactly (the mixer queues the next one,
        no frame counting: before, the loop came in after a fixed number of frames and a slow frame broke it)."""
        if intro not in self.music or loop not in self.music:
            return
        self.channel = play_at_full_volume(self.music[intro], 0)
        self.current, self.loop_after = intro, loop
        if self.channel:
            self.channel.queue(self.music[loop])

    def drop_queued_loop(self):
        """(11.11) The intro's loop must not come in later. A queued sound starts even when its channel is STOPPED
        (that is how menu_loop got into the game), so the queue gets a tiny silence instead, then nothing follows."""
        if self.loop_after and self.channel:
            self.channel.queue(silence())
        self.loop_after = None

    def keep_looping(self):
        """Once the loop has begun it queues itself again, so it goes on without a gap."""
        if not self.loop_after or not self.channel:
            return
        loop = self.music[self.loop_after]
        if self.channel.get_sound() is loop:
            self.current = self.loop_after
            if self.channel.get_queue() is None:
                self.channel.queue(loop)

    def play(self, name):
        self.drop_queued_loop()
        if name not in self.music:
            name = MUSIC_FALLBACK.get(name, name)
        if name in self.music:
            self.channel = play_at_full_volume(self.music[name], -1)
            self.current = name

    # --- a second music OVER the current one (the shop) -----------------------------------------
    # fade_to: the current music fades out and PAUSES, the other one fades in.
    # fade_back: the other one fades out, the old one goes on from where it was (not from the start).
    def fade_to(self, name, ms=1000):
        if name not in self.music or self.overlay:
            return
        self.overlay = name
        play_at_full_volume(self.music[name], -1, ms)
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
        """Once per frame: moves the fade along (and keeps an intro's loop going)."""
        self.keep_looping()
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
        self.drop_queued_loop()
        if self.current in self.music:
            self.music[self.current].fadeout(ms)
        self.current = self.channel = None

    def stop(self, name=None):
        self.drop_queued_loop()
        if name in self.music:
            self.music[name].stop()
        else:
            for music in self.music.values():
                music.stop()
            self.overlay = self.fade = None
            self.current = self.channel = None
    def update_volume(self):
        for name, music in self.music.items():
            music.set_volume(self.fixed_volume.get(name, self.music_volume))
