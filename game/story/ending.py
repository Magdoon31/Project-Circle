# ENDINGS (12.11): after the last fight of an ending the screen fades to a plain colour, the voice ??? speaks
# (a dialogue file with "auto": true - only the first line can be skipped, the rest goes on by itself), the screen
# goes black and the credits roll (credits.py) over end_credits.mp3. Then Game goes back to the main menu.
#   main   - Milo beaten without the Peace Gun   black, the ending hum
#   extra  - the Void beaten, lore items missing  black, the ending hum
#   secret - the Void beaten, all 3 lore items    white, silence, then ending_secret from its 8th line; after the
#            last line the music plays one more round of chords, fades, and a short silence comes before the credits
# PICTURES behind the lines (Slideshow): assets/img/endings/<name>_<n>.png, one for every 2 lines from the
# dialogue's "pictures": {"name", "from_line"} on, none on the last line; each slowly comes closer. A missing
# file = the plain colour.

import os

import pygame

from game.dialogue.dialogue import Dialogue, DialogueContext
from game.story.credits import Credits, FADE_MS as CREDITS_FADE_MS

DIALOGUES = {"main": "ending_main", "extra": "ending_extra", "secret": "ending_secret"}
LIGHT = {"secret"}                                       # a white ending
MUSIC = {"ending": "assets/music/ending.mp3", "ending_secret": "assets/music/ending_secret.mp3",
         "end_credits": "assets/music/end_credits.mp3"}
FADE_IN_FRAMES = 90                                      # the last picture of the fight fades to the ending's colour
MUSIC_TAIL_FRAMES = {"secret": 358}                      # the music goes on after the last line (~6 s)
SILENCE_FRAMES = {"secret": 120}                         # quiet between the monologue and the credits (default 45)
MUSIC_FADE_MS = 2000                                     # the monologue's music fades out this long
TO_BLACK_FRAMES = 60                                     # the ending's colour -> the credits' black

PICTURE_DIR = "assets/img/endings"
LINES_PER_PICTURE = 2
PICTURE_FADE = 45                                        # frames a new picture takes to come in
PICTURE_ZOOM = 0.06                                      # how much closer it comes ...
PICTURE_ZOOM_FRAMES = 900                                # ... over this long


class EndingScene:
    def __init__(self, screen, clock, music, dialogue_volume, kind):
        self.screen, self.clock, self.music, self.kind = screen, clock, music, kind
        self.colour = (255, 255, 255) if kind in LIGHT else (0, 0, 0)
        for name, path in MUSIC.items():
            music.load(name, path)
        context = DialogueContext(has_flag=lambda f: False, set_flag=lambda f: None, clear_flag=lambda f: None,
                                  has_item=lambda i: False, give_item=lambda i: None, take_item=lambda i: None,
                                  play_music=self.play)
        self.dialogue = Dialogue(screen, DIALOGUES[kind], context, dialogue_volume)
        self.slideshow = Slideshow(screen.get_size(), self.colour, self.dialogue.data.get("pictures"),
                                   len(self.dialogue.lines))

    def run(self):
        """The whole ending. False if the game was closed meanwhile."""
        self.music.stop()
        return (self.fade(self.screen.copy(), self.colour, FADE_IN_FRAMES) and self.monologue()
                and self.wind_down() and self.fade(self.plain(self.colour), (0, 0, 0), TO_BLACK_FRAMES)
                and self.credits())

    # --- the parts ------------------------------------------------------------------------------------------
    def monologue(self):
        self.play(self.dialogue.music)
        while not self.dialogue.finished:
            events = self.tick()
            if events is None:
                return False
            self.dialogue.handle_events(events)
            self.dialogue.update()
            self.dialogue.background = self.slideshow.frame(self.dialogue.line_index)
            self.dialogue.draw()
            pygame.display.flip()
        return True

    def wind_down(self):
        """After the last line: the music goes on a moment (secret), fades, then a short silence."""
        tail = MUSIC_TAIL_FRAMES.get(self.kind, 0)
        quiet = MUSIC_FADE_MS * 60 // 1000 + SILENCE_FRAMES.get(self.kind, 45)
        for frame in range(tail + quiet):
            if frame == tail:
                self.music.fade_out(MUSIC_FADE_MS)
            if self.tick() is None:
                return False
            self.screen.fill(self.colour)
            pygame.display.flip()
        return True

    def fade(self, start, colour, frames):
        """`start` (a picture) fades into a plain colour."""
        veil = self.plain(colour)
        for frame in range(frames):
            if self.tick() is None:
                return False
            self.screen.blit(start, (0, 0))
            veil.set_alpha(255 * (frame + 1) // frames)
            self.screen.blit(veil, (0, 0))
            pygame.display.flip()
        return True

    def credits(self):
        roll = Credits(self.screen)
        self.music.play_once("end_credits")
        music_fading = False
        while not roll.finished:
            if self.tick() is None:
                return False
            keys = pygame.key.get_pressed()
            roll.update(keys[pygame.K_SPACE] or keys[pygame.K_RETURN])
            if roll.fading_out and not music_fading:
                self.music.fade_out(CREDITS_FADE_MS)
                music_fading = True
            roll.draw()
            pygame.display.flip()
        return True

    # --- helpers --------------------------------------------------------------------------------------------
    def play(self, name):
        """A track from the start (or nothing: "silence" / a missing file)."""
        if self.music.has(name):
            self.music.stop()
            self.music.play(name)

    def plain(self, colour):
        surface = pygame.Surface(self.screen.get_size())
        surface.fill(colour)
        return surface

    def tick(self):
        """One frame: the events (a list), or None when the window is closed."""
        self.clock.tick(60)
        events = pygame.event.get()
        if any(e.type == pygame.QUIT for e in events):
            return None
        return events


class Slideshow:
    """The picture behind the monologue: one for every LINES_PER_PICTURE lines, slowly coming closer."""

    def __init__(self, size, colour, spec, line_count):
        self.size, self.colour = size, colour
        self.name = spec["name"] if spec else None
        self.first = spec.get("from_line", 2) if spec else 0     # counted from 1, like the Endings doc
        self.last = line_count                                    # the last line: no picture
        self.cache = {}
        self.current, self.since = None, 0
        self.plain = pygame.Surface(size)
        self.plain.fill(colour)

    def number_for(self, line_index):
        """The picture number (1, 2, ...) for a line (index from 0), or None."""
        line = line_index + 1
        if not self.name or not self.first <= line < self.last:
            return None
        return (line - self.first) // LINES_PER_PICTURE + 1

    def frame(self, line_index):
        """The background for this frame: the colour, with the picture (if there is one) over it."""
        number = self.number_for(line_index)
        if number != self.current:
            self.current, self.since = number, 0
        self.since += 1
        picture = self.picture(number)
        if picture is None:
            return self.plain
        zoomed = self.zoomed(picture)
        if self.since >= PICTURE_FADE:
            return zoomed
        background = self.plain.copy()
        zoomed.set_alpha(255 * self.since // PICTURE_FADE)
        background.blit(zoomed, (0, 0))
        return background

    def zoomed(self, picture):
        """The middle part of the picture, scaled up to the screen: it seems to come slowly closer."""
        scale = 1 + PICTURE_ZOOM * min(1.0, self.since / PICTURE_ZOOM_FRAMES)
        w, h = self.size
        part = pygame.Rect(0, 0, int(w / scale), int(h / scale))
        part.center = (w // 2, h // 2)
        return pygame.transform.smoothscale(picture.subsurface(part), self.size)

    def picture(self, number):
        if number is None:
            return None
        if number not in self.cache:
            path = os.path.join(PICTURE_DIR, f"{self.name}_{number}.png")
            try:
                raw = pygame.image.load(path).convert() if os.path.exists(path) else None
                self.cache[number] = pygame.transform.smoothscale(raw, self.size) if raw else None
            except pygame.error:
                self.cache[number] = None
        return self.cache[number]
