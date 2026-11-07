# Base for minigames played from dialogues (memory, sudoku ...).
# Game runs one like this:  handle_events(events) -> update() -> draw()  until  .finished;  then reads .won

import os, random
import pygame

RESULT_DELAY = 40           # frames the "You win / Time's up" text stays before a key closes it
COUNTDOWN_STEP = 54         # frames per "3", "2", "1", "GO!" (4 x 0.9 s = the 3.6 s countdown.mp3)

# sounds: the minigame file if it exists (assets/sfx/minigames/), otherwise an existing game sound
SOUND_DIR = "assets/sfx/minigames"
# a list of own files = one of them at random (e.g. win1 / win2)
SOUNDS = {
    "countdown": (["countdown.mp3"],          "assets/sfx/UI/click1.wav"),   # the whole "3, 2, 1, GO!" in one file
    "go":        (["go.wav"],                 "assets/sfx/UI/use.wav"),      # only used without countdown.mp3
    "flip":      (["flip.wav"],               "assets/sfx/UI/click1.wav"),
    "match":     (["match.wav"],              "assets/sfx/UI/use.wav"),
    "wrong":     (["wrong.wav"],              "assets/sfx/combat/player_hit.wav"),
    "write":     (["write.wav"],              "assets/sfx/UI/click1.wav"),
    "win":       (["win1.wav", "win2.wav"],   "assets/sfx/UI/new_item.wav"),
    "lose":      (["fail.mp3"],               "assets/sfx/minigames/finish.mp3"),
    "jackpot":   (["wheel_jackpot.mp3"],      "assets/sfx/UI/new_item.wav"),  # Lucky's wheel stops on x6
}
_sound_cache = {}


def _load(path):
    try:
        return pygame.mixer.Sound(path) if os.path.exists(path) else None
    except pygame.error:
        return None


def _sounds(name):
    """([sounds], True if they are the minigame's own files)"""
    if name not in _sound_cache:
        own, fallback = SOUNDS[name]
        sounds = [s for s in (_load(os.path.join(SOUND_DIR, f)) for f in own) if s]
        if sounds:
            _sound_cache[name] = (sounds, True)
        else:
            fb = _load(fallback)
            _sound_cache[name] = ([fb] if fb else [], False)
    return _sound_cache[name]


def has_own_sound(name):
    return _sounds(name)[1]


class Minigame:
    title = "Minigame"

    hide_board_in_countdown = False
    use_countdown = True            # False = starts right away (no 3-2-1)
    keep_music = False              # True = the biome music keeps playing (no minigame music)

    def __init__(self, screen, background, volume=1.0):
        self.screen = screen
        self.background = background          # the dimmed map from the dialogue
        sh = screen.get_height()
        self.font = pygame.font.Font("assets/font/Nexa-Heavy.ttf", max(18, sh // 26))
        self.font_big = pygame.font.Font("assets/font/Nexa-Heavy.ttf", max(28, sh // 14))
        self.font_small = pygame.font.Font("assets/font/Nexa-ExtraLight.ttf", max(12, sh // 45))
        self.finished = False
        self.won = False
        self.result = None                    # "win" / "lose" while the result text is shown
        self.result_timer = 0
        self.timer = 0
        self.volume = volume
        self.countdown = COUNTDOWN_STEP * 4 if self.use_countdown else 0      # 3, 2, 1, GO!
        self.countdown_started = False            # the sound starts on the first frame (after e.g. a sudoku is made)

    def play(self, name):
        sounds = _sounds(name)[0]
        sound = random.choice(sounds) if sounds else None
        if sound:
            channel = sound.play()            # (not find_channel: that one may pick the reserved talk channel 0)
            if channel:
                channel.set_volume(self.volume)

    @property
    def counting_down(self):
        return self.countdown > 0

    def end(self, won, sound=None):
        """sound = a special sound instead of the usual win / lose one (e.g. "jackpot")."""
        if self.result is None:
            self.result = "win" if won else "lose"
            self.won = won
            self.result_timer = 0
            self.play(sound or ("win" if won else "lose"))

    def handle_events(self, events):
        if self.result is not None:
            if self.result_timer >= RESULT_DELAY and any(e.type == pygame.KEYDOWN or
                                                         (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1) for e in events):
                self.finished = True
            return
        if self.counting_down:
            return
        self.on_events(events)

    def update(self):
        self.timer += 1
        if self.result is not None:
            self.result_timer += 1
            return
        if self.counting_down:
            if not self.countdown_started:
                self.countdown_started = True
                self.play("countdown")
                return
            self.countdown -= 1
            # with the old single-beep fallback: a beep on every number (countdown.mp3 already has them all)
            if not has_own_sound("countdown") and self.countdown > 0 and self.countdown % COUNTDOWN_STEP == 0:
                self.play("go" if self.countdown == COUNTDOWN_STEP else "countdown")
            return
        self.on_update()

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        if self.counting_down and self.hide_board_in_countdown:
            self.draw_header("Get ready...")
        else:
            self.on_draw()
        if self.counting_down:
            sw, sh = self.screen.get_size()
            step = (self.countdown - 1) // COUNTDOWN_STEP          # 3, 2, 1, 0 (= GO!)
            text = "GO!" if step == 0 else str(step)
            img = self.font_big.render(text, True, (255, 230, 60))
            frac = (self.countdown - 1) % COUNTDOWN_STEP / COUNTDOWN_STEP
            img = pygame.transform.rotozoom(img, 0, 1.0 + frac * 0.8)          # each number "pops"
            plate = img.get_rect(center=(sw // 2, sh // 2)).inflate(60, 30)
            pygame.draw.rect(self.screen, (0, 0, 0), plate, 0, 14)
            pygame.draw.rect(self.screen, (255, 255, 255), plate, 4, 14)
            self.screen.blit(img, img.get_rect(center=plate.center))
        if self.result is not None:
            sw, sh = self.screen.get_size()
            text = self.win_text() if self.result == "win" else self.lose_text()
            img = self.font_big.render(text, True, (255, 230, 60) if self.result == "win" else (255, 110, 110))
            plate = pygame.Rect(0, 0, img.get_width() + 80, img.get_height() + 40)
            plate.center = (sw // 2, sh // 2)
            pygame.draw.rect(self.screen, (0, 0, 0), plate, 0, 14)
            pygame.draw.rect(self.screen, (255, 255, 255), plate, 4, 14)
            self.screen.blit(img, img.get_rect(center=plate.center))
            if self.result_timer >= RESULT_DELAY:
                hint = self.font_small.render("press any key", True, (200, 200, 200))
                self.screen.blit(hint, hint.get_rect(midtop=(sw // 2, plate.bottom + 10)))

    def win_text(self):
        return "You win!"

    def lose_text(self):
        return "Time's up!"

    def draw_header(self, subtitle, seconds_left=None, total=None):
        sw, sh = self.screen.get_size()
        title = self.font.render(self.title, True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(midtop=(sw // 2, sh // 40)))
        sub = self.font_small.render(subtitle, True, (200, 200, 200))
        self.screen.blit(sub, sub.get_rect(midtop=(sw // 2, sh // 40 + title.get_height() + 4)))
        if seconds_left is not None:
            bar = pygame.Rect(sw // 4, sh // 40 + title.get_height() + sub.get_height() + 14, sw // 2, max(8, sh // 90))
            pygame.draw.rect(self.screen, (60, 60, 70), bar, 0, 6)
            part = bar.copy()
            part.width = int(bar.width * max(0.0, seconds_left / total))
            pygame.draw.rect(self.screen, (255, 110, 110) if seconds_left < 10 else (120, 220, 140), part, 0, 6)
            t = self.font_small.render(f"{max(0, int(seconds_left + 0.99))} s", True, (255, 255, 255))
            self.screen.blit(t, (bar.right + 12, bar.centery - t.get_height() // 2))
