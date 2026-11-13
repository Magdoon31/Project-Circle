# LOUDER SOUNDS (13.11): pygame can't play a sound above its file's own loudness (volume 1.0 at most), and the
# talk sounds and recorded voices were quiet next to the music. louder() makes a copy of a sound with every sample
# x gain (clipped), so the Dialogue slider has more room at the top. Only for the usual 16-bit mixer; with any
# other format the sound is given back as it is.

import array

import pygame

SIGNED_16 = -16
LIMIT = 32767


def louder(sound, gain):
    """A copy of `sound`, `gain` times louder (or the sound itself if that can't be done)."""
    if sound is None or gain == 1.0 or not mixer_is_16_bit():
        return sound
    try:
        samples = array.array("h", sound.get_raw())
        boosted = array.array("h", (max(-LIMIT, min(LIMIT, int(s * gain))) for s in samples))
        return pygame.mixer.Sound(buffer=boosted.tobytes())
    except (TypeError, ValueError, pygame.error):
        return sound                          # (not a normal Sound) - as it is


def mixer_is_16_bit():
    settings = pygame.mixer.get_init()
    return bool(settings) and settings[1] == SIGNED_16
