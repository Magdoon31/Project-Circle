# THE ACHIEVEMENT SOUND (13.11): a short bright chime - three bell notes going up (C6, E6, G6) and a soft C7 on
# top, each with a quick attack and a long fade, a little echo. Written to assets/sfx/UI/achievement.wav
# (the "Achievement unlocked" note plays it - game/achievements/popup.py). Needs numpy.
# Run from the game's folder:  python tools/make_achievement_sound.py

import os
import wave

import numpy as np

OUT = "assets/sfx/UI/achievement.wav"
RATE = 44100
LENGTH = 1.6                                  # seconds
NOTES = [(1046.5, 0.00, 0.55), (1318.5, 0.09, 0.50), (1568.0, 0.18, 0.50), (2093.0, 0.30, 0.30)]  # (Hz, start s, loud)
PARTIALS = [(1.0, 1.0), (2.0, 0.35), (3.01, 0.12), (4.2, 0.05)]   # a bell: (x the note, loudness)
DECAY = 3.2                                   # how fast a note fades (per second)
ECHO = (0.11, 0.25)                           # (s later, loudness)
VOLUME = 0.6


def bell(freq, start, loud, t):
    age = np.clip(t - start, 0, None)
    on = t >= start
    attack = np.minimum(1.0, age / 0.004)
    tone = sum(a * np.sin(2 * np.pi * freq * m * age) * np.exp(-DECAY * m ** 0.5 * age) for m, a in PARTIALS)
    return tone * attack * loud * on


def main():
    t = np.arange(int(RATE * LENGTH)) / RATE
    sound = sum(bell(f, s, l, t) for f, s, l in NOTES)
    delay = int(ECHO[0] * RATE)
    sound[delay:] += sound[:-delay] * ECHO[1]
    sound *= VOLUME / np.max(np.abs(sound))
    left = (sound * 32767).astype(np.int16)
    right = np.roll(left, 40)                                   # a touch of width
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with wave.open(OUT, "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes(np.column_stack([left, right]).tobytes())
    print("written", OUT)


if __name__ == "__main__":
    main()
