# SONG CLOCK: where we are in the song, counted in beats (bar 1 beat 1 = beat 0).
# The time comes from the real clock (ms since the music started), so a slow frame never puts the attacks
# out of step with the music.
# (10.11) A song's tempo isn't always steady (the Mascot's track slows from ~165.5 to ~163 BPM), so a song can
# have a BEAT MAP: the time of every beat, measured from the track (a text file, one ms value per line).
# Between two beats the clock goes evenly; before the first / after the last it goes on at the nearest pace.

import bisect
import os

BEATS_PER_BAR = 4


def steady_beats(bpm, first_beat_ms, count):
    """The beat times of a song with a steady tempo."""
    step = 60_000 / bpm
    return [first_beat_ms + i * step for i in range(count)]


def load_beat_map(path):
    """The beat times (ms) from a beat map file, or None if there is no such file."""
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return [float(line) for line in f if line.strip()]


class SongClock:
    def __init__(self, beat_times_ms, start_ms):
        self.times = beat_times_ms              # where every beat is in the track (at least 2)
        self.start_ms = start_ms                # the real time the music started

    def song_ms(self, now_ms):
        return now_ms - self.start_ms

    def beat(self, now_ms):
        """The beat we are on now (a float; 0 = bar 1 beat 1, negative before it)."""
        t = self.song_ms(now_ms)
        i = min(max(bisect.bisect_right(self.times, t) - 1, 0), len(self.times) - 2)
        a, b = self.times[i], self.times[i + 1]
        return i + (t - a) / (b - a)

    def ms_of(self, beat):
        """The real time a beat falls on."""
        i = min(max(int(beat), 0), len(self.times) - 2)
        a, b = self.times[i], self.times[i + 1]
        return self.start_ms + a + (beat - i) * (b - a)


def beat_of(bar, beat=1):
    """Bar and beat as the musicians count them (both from 1) -> the beat number (from 0)."""
    return (bar - 1) * BEATS_PER_BAR + (beat - 1)
