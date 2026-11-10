# TIME REWIND (10.11, Milo's F2 and F4): the fight remembers its last few seconds, frame by frame; a rewind plays
# them back BACKWARDS (quickly), so everything goes back to where it was - you, Milo, every bullet, the cracks,
# the mines, the heart. Only HP is never taken back. Here: the memory and the playback; what a "moment" holds and
# how it is put back is CoreFight's (it knows the fight).

from collections import deque

REMEMBER_FRAMES = 180            # 3 s back
PLAYBACK_FRAMES = 30             # ... played back in 0.5 s


class TimeRewind:
    def __init__(self):
        self.memory = deque(maxlen=REMEMBER_FRAMES)
        self.playback = []                       # the moments still to show, newest first

    @property
    def playing(self):
        return bool(self.playback)

    def remember(self, moment):
        self.memory.append(moment)

    def forget(self):
        self.memory.clear()

    def oldest(self):
        """Where the rewind will end (None = nothing remembered yet)."""
        return self.memory[0] if self.memory else None

    def start(self):
        moments = list(self.memory)[::-1]
        step = max(1, len(moments) // PLAYBACK_FRAMES)
        self.playback = moments[step - 1::step]
        if self.playback and self.playback[-1] is not moments[-1]:
            self.playback.append(moments[-1])     # it always ends exactly on the oldest moment
        self.memory.clear()

    def next_moment(self):
        """The moment to show this frame (None when the playback is over)."""
        return self.playback.pop(0) if self.playback else None
