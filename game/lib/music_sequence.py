# MUSIC SEQUENCE (11.11, the Void's boss): one song cut into parts that follow each other in time.
#   - a looping part plays round and round;
#   - switch_to(part): the next part starts on the next 8-beat line of the one playing (at most ~3.5 s at 138 BPM),
#     so that ITS first beat falls exactly on that line; the old part fades out over one beat (no sudden cut);
#   - then(part): the next part starts the moment this one (a one-off part) ends.
# Times are real ms (pygame ticks), so a slow frame never moves the music; pause() / resume() keep the places.
# The tracks themselves are MusicManager's (loaded once, by name).

from game.lib.music_manager import play_at_full_volume

SWITCH_EVERY_BEATS = 8
FADE_IN_MS = 80                  # the new part comes in very quickly (its first beat stays sharp)


class Part:
    def __init__(self, name, path, first_beat_ms, length_ms, loop):
        self.name, self.path = name, path
        self.first_beat_ms = first_beat_ms      # where its first beat is in the file
        self.length_ms = length_ms              # one time through (a loop: exactly a whole number of beats)
        self.loop = loop


class MusicSequence:
    def __init__(self, music, parts, bpm):
        self.music = music                      # MusicManager
        self.parts = {p.name: p for p in parts}
        self.beat_ms = 60_000 / bpm
        self.current = None                     # the part playing now
        self.started_at = 0                     # tick its file started
        self.channel = None
        self.pending = None                     # (part, tick it starts at)
        self.after = None                       # a part that starts when the current one ends
        self.paused_at = None
        for p in parts:
            music.load(p.name, p.path)

    # --- asking -----------------------------------------------------------------------------------------------
    def position_ms(self, now):
        """How far into the current part's file we are (a loop: within the current time round)."""
        if self.current is None:
            return 0
        t = now - self.started_at
        return t % self.current.length_ms if self.current.loop else t

    def song_ms(self, now):
        """ms since the current part started (not wrapped)."""
        return now - self.started_at if self.current else 0

    @property
    def target(self):
        """The part playing or about to (what the fight asked for last)."""
        if self.pending:
            return self.pending[0].name
        if self.after:
            return self.after.name
        return self.current.name if self.current else None

    # --- doing ------------------------------------------------------------------------------------------------
    def start(self, name, now):
        """Starts a part right now (the fight's start, a checkpoint)."""
        self.stop()
        self._play(self.parts[name], now)

    def switch_to(self, name, now):
        """The next part, on the next 8-beat line of the one playing (see the top)."""
        part = self.parts[name]
        if self.current is None:
            self._play(part, now)
            return
        self.pending = (part, self._next_line(now, part) - part.first_beat_ms)

    def then(self, name):
        """This part starts the moment the current one ends."""
        self.after = self.parts[name]

    def update(self, now):
        if self.paused_at is not None:
            return
        if self.pending and now >= self.pending[1]:
            part, at = self.pending
            self.pending = None
            self._fade_current_out()
            self._play(part, at)
        if self.after and self.current and not self.current.loop and now - self.started_at >= self.current.length_ms:
            part, self.after = self.after, None
            self._play(part, self.started_at + self.current.length_ms)

    def fade_out(self, ms):
        """(11.11) The part playing fades away (nothing comes after it)."""
        self.pending = self.after = None
        self._fade_current_out(ms)

    def stop(self):
        for p in self.parts.values():
            self.music.music[p.name].stop()
        self.current = self.channel = self.pending = self.after = None

    def pause(self, now):
        self.paused_at = now
        if self.channel:
            self.channel.pause()

    def resume(self, now):
        if self.paused_at is None:
            return
        waited = now - self.paused_at
        self.started_at += waited
        if self.pending:
            self.pending = (self.pending[0], self.pending[1] + waited)
        self.paused_at = None
        if self.channel:
            self.channel.unpause()

    # --- inside -----------------------------------------------------------------------------------------------
    def _play(self, part, at):
        sound = self.music.music[part.name]
        self.channel = play_at_full_volume(sound, -1 if part.loop else 0, FADE_IN_MS)
        self.current, self.started_at = part, at
        self.music.current, self.music.channel = part.name, self.channel

    def _fade_current_out(self, ms=None):
        if self.current:
            self.music.music[self.current.name].fadeout(int(ms or self.beat_ms))

    def _next_line(self, now, coming):
        """The tick of the next 8-beat line of the current part (counted from its first beat), far enough ahead to
        start the coming part early by its own lead-in (its first beat lands on the line)."""
        part = self.current
        lead = coming.first_beat_ms + 20
        line = SWITCH_EVERY_BEATS * self.beat_ms
        pos = self.position_ms(now)
        round_start = now - pos                                   # this time round of the loop started here
        k = 0
        while True:
            at = part.first_beat_ms + k * line
            if at >= part.length_ms:                              # the loop's end is a line too
                at = part.length_ms + part.first_beat_ms
            if round_start + at - now >= lead:
                return round_start + at
            if at >= part.length_ms:
                round_start += part.length_ms
                k = 0
                continue
            k += 1
