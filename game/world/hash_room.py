# ### - THE HEART (13.11): the bottom of the Pale World maze (pale_world.HashMap). Under its floor the Core's heart
# is asleep: a very slow beat you hear (louder near the middle) and a soft red pulse of light on the floor.
# The words on the floor change every visit (HASH_LINES, then round again - a circle).
# No music, no NPC, no fights (the Pale World's rules). The way out is still only taking the Pale Orb off.

import math

import pygame

from game.menu import options as OPT

HEART_TILE = (15, 11)              # the middle of the room (the Peace Gun lies just above it)
TEXT_TILE = (15, 12)
BEAT_MS = 2600                     # one slow beat (a sleeping heart)
PULSE_FADE_MS = 900                # how long the light takes to fade after a beat
HEART_SOUND = "assets/sfx/combat/bosses/core/heart.ogg"
NEAR_TILES, FAR_TILES = 2.0, 11.0  # full loudness / light this close, the quietest this far
FAR_VOLUME = 0.12
GLOW_COLOUR = (150, 30, 45)
GLOW_TILES = 4.5                   # the light's radius
GLOW_ALPHA = 140
GLOW_RINGS = 14
HASH_LINES = ["Still asleep.", "Not off. Asleep.", "It heard you."]   # (14.11) "Not yet." taken out (Filip)
VISITS = "hash_visits"             # counters key: how many times you came down


def line_for(visit):
    """The words on the floor for this visit (1, 2, ...): HASH_LINES in turn, then from the start again."""
    return HASH_LINES[(visit - 1) % len(HASH_LINES)]


def beat_number(ms):
    return ms // BEAT_MS


def pulse(ms):
    """1 right on a beat, fading to 0 before the next one."""
    since = ms % BEAT_MS
    return max(0.0, 1 - since / PULSE_FADE_MS) ** 2


def closeness(tile_pos):
    """1 near the heart ... 0 far away (tiles)."""
    d = math.dist(tile_pos, HEART_TILE)
    return max(0.0, min(1.0, (FAR_TILES - d) / (FAR_TILES - NEAR_TILES)))


class Heart:
    """Plays the beat in time with the light (Game calls update each frame while you are in ###)."""

    def __init__(self):
        self.sound = None
        self.last_beat = None

    def update(self, tile_pos, ms):
        beat = beat_number(ms)
        if beat == self.last_beat:
            return
        self.last_beat = beat
        sound = self.load()
        if sound:
            sound.set_volume(OPT.volume("sfx") * (FAR_VOLUME + (1 - FAR_VOLUME) * closeness(tile_pos)))
            sound.play()

    def load(self):
        if self.sound is None:
            try:
                self.sound = pygame.mixer.Sound(HEART_SOUND)
            except (pygame.error, FileNotFoundError):
                self.sound = False
        return self.sound

    def leave(self):
        self.last_beat = None


def draw_glow(screen, centre, tile_size, ms, player_tile):
    """The soft red light on the floor round the heart, beating; brighter when you stand close."""
    strength = pulse(ms) * (0.35 + 0.65 * closeness(player_tile))
    if strength <= 0.01:
        return
    radius = int(GLOW_TILES * tile_size)
    glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for k in range(GLOW_RINGS, 0, -1):
        share = k / GLOW_RINGS
        alpha = int(GLOW_ALPHA * strength * (1 - share) ** 1.5)
        pygame.draw.circle(glow, GLOW_COLOUR + (alpha,), (radius, radius), int(radius * share))
    screen.blit(glow, glow.get_rect(center=(int(centre[0]), int(centre[1]))))
