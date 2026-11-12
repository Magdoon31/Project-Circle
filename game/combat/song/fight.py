# SONG FIGHT (10.11, the Mascot in the lunapark): Combat runs one of these instead of enemies.
#   - the attacks come from the chart (chart.py) on the beats of the song; you can't shoot, only dodge
#   - you can't die: a hit only counts (and gives SONG_IMMUNITY frames to get out of the way)
#   - the song ends -> the fight is won; the grade depends on the hits: A (at most 1) .. D
#     A = the Mascot Plush (the first time), B / C = a little gold, D = nothing
# Combat calls update() every frame, draw_world() into the arena, draw_hud() / draw_result() onto the display,
# and plays the sounds in `sounds` (lasers / shapes, only when they land - on the beat).

import math

import pygame

from game.combat.song import chart as CHART
from game.combat.song.clock import SongClock, load_beat_map, steady_beats
from game.combat.song.emitters import BULLET_DAMAGE, Ring, Spinner, Walls
from game.combat.song.hazards import PINK, Laser, Shape

FLOOR = (24, 20, 40)              # the arena: dark, so the pink shapes stand out
SONG_IMMUNITY = 60                # frames you can't be hit again after a hit (1 s)
HIT_RADIUS_SHARE = 0.6            # lasers / shapes hurt this share of your size (a fair, small hitbox)
GRADES = (("A", 3), ("B", 6), ("C", 9))          # (grade, most hits for it); more = D
GRADE_GOLD = {"A": 150, "B": 200, "C": 60, "D": 0}  # (A: only when the plush was already won)
GRADE_COLOURS = {"A": (255, 210, 60), "B": (120, 220, 140), "C": (130, 170, 240), "D": (190, 190, 190)}
BULLET = {"width": 11, "kind": "normal_red", "speed": 7}
MASCOT_START = (0.5, -0.15)       # share of the arena: it comes in from above
MASCOT_RADIUS = 46
MASCOT_COLOUR = (255, 196, 64)     # a round boss like the others
PROGRESS_HEIGHT = 4               # px: the thin song progress bar at the top
FLASH_ALPHA = 46                  # climax: the arena flashes pink on every beat
PLAYER_START = (0.5, 0.8)
MUSIC_HINT = "Music recommended"   # (11.11) shown at the start when the music is (almost) off - the fight is a song
MUSIC_HINT_FRAMES = 300           # 5 s, the last second fades


class SongFight:
    def __init__(self, arena, bullet_info, now_ms, prize_name, prize_available, cues=None, music_hint=False):
        self.arena = arena                                  # (w, h) px
        self.bullet_info = bullet_info
        self.clock = SongClock(self.beat_times(), now_ms)
        self.cues = cues if cues is not None else CHART.mascot_chart()
        self.next_cue = 0
        self.end_beat = max(c[0] for c in self.cues)
        self.hazards = []
        self.emitters = []
        self.mascot = self.to_px(MASCOT_START)
        self.mascot_move = None                             # (from, to, start beat, end beat)
        self.dark = 0.0
        self.flash = False
        self.beat = -1.0
        self.hits = 0
        self.finished = False
        self.prize_name = prize_name                        # what grade A gives (only once)
        self.prize_available = prize_available
        self.layer = pygame.Surface(arena, pygame.SRCALPHA)
        self.sounds = []                                    # what landed this frame (Combat plays it)
        self.music_hint_left = MUSIC_HINT_FRAMES if music_hint else 0

    # --- helpers ---------------------------------------------------------------------------------------------
    def to_px(self, share):
        return share[0] * self.arena[0], share[1] * self.arena[1]

    @staticmethod
    def beat_times():
        """The song's beat map, or a steady tempo if the file is missing."""
        return load_beat_map(CHART.BEAT_MAP) or steady_beats(CHART.BPM, CHART.FIRST_BEAT_MS, 400)

    def spot(self, at, player):
        """A spot of the chart: a share of the arena, or \"player\" = where you are when its warning starts."""
        return (player.x, player.y) if at == "player" else self.to_px(at)

    def place_player(self, player):
        player.x, player.y = self.to_px(PLAYER_START)

    # --- every frame -----------------------------------------------------------------------------------------
    def update(self, now_ms, player, bullets):
        """Moves the song on; returns the new bullets. Removes the bullets that left the arena from `bullets`."""
        self.beat = self.clock.beat(now_ms)
        self.start_due_cues(player)
        self.move_mascot()
        new = []
        for emitter in self.emitters:
            new += emitter.update(self.beat, self.mascot)
        self.emitters = [e for e in self.emitters if not e.done(self.beat)]
        self.hazards = [h for h in self.hazards if not h.gone(self.beat)]
        self.sounds = sorted({h.sound for h in self.hazards if h.lands_now(self.beat)})
        self.drop_far_bullets(bullets)
        if self.touches_player(player):
            player.take_damage(BULLET_DAMAGE, {})
        return new

    def start_due_cues(self, player):
        while self.next_cue < len(self.cues):
            at, kind, settings = self.cues[self.next_cue]
            if self.beat < at - settings.get("warn", 0):
                return
            self.start(at, kind, settings, player)
            self.next_cue += 1

    def start(self, at, kind, s, player):
        warn_from = at - s.get("warn", 0)
        if kind == "laser":
            self.hazards.append(Laser(*self.spot(s["at"], player), s["angle"], s["width"], warn_from, at, s["hold"]))
        elif kind == "grid":
            self.hazards += self.grid(at, s, warn_from)
        elif kind == "shape":
            self.hazards.append(Shape(*self.spot(s["at"], player), s["form"], s["size"], warn_from, at, s["hold"]))
        elif kind == "spin":
            self.emitters.append(Spinner(at, at + s["beats"], {**BULLET, **s}, self.bullet_info, self.arena))
        elif kind == "ring":
            self.emitters.append(Ring(at, {**BULLET, **s}, self.bullet_info, self.arena))
        elif kind == "walls":
            self.emitters.append(Walls(at, s["side"], self.gap_spot(s), {**BULLET, **s},
                                       self.bullet_info, self.arena))
        elif kind == "move":
            self.mascot_move = (self.mascot, self.to_px(s["to"]), at, at + s["beats"])
        elif kind == "mood":
            self.dark, self.flash = s["dark"], s["flash"]
        elif kind == "end":
            self.finished = True

    def grid(self, at, s, warn_from):
        """Parallel lasers right across the arena, evenly spread (gaps between them to stand in)."""
        a = math.radians(s["angle"])
        normal = (-math.sin(a), math.cos(a))
        w, h = self.arena
        across = [x * normal[0] + y * normal[1] for x, y in ((0, 0), (w, 0), (0, h), (w, h))]
        low, high = min(across), max(across)
        step = (high - low) / s["count"]
        out = []
        for i in range(s["count"]):
            d = low + step * (i + 0.5 + s["shift"])
            if d > high:
                d -= high - low
            out.append(Laser(normal[0] * d, normal[1] * d, s["angle"], s["width"], warn_from, at, s["hold"]))
        return out

    def gap_spot(self, s):
        along_y = s["side"] in ("left", "right")
        return s["gap_at"] * (self.arena[1] if along_y else self.arena[0])

    def move_mascot(self):
        if not self.mascot_move:
            return
        start, goal, b0, b1 = self.mascot_move
        k = min(1.0, max(0.0, (self.beat - b0) / max(1e-6, b1 - b0)))
        k = k * k * (3 - 2 * k)                             # eases in and out
        self.mascot = (start[0] + (goal[0] - start[0]) * k, start[1] + (goal[1] - start[1]) * k)
        if k >= 1.0:
            self.mascot_move = None

    def drop_far_bullets(self, bullets):
        w, h = self.arena
        margin = 60
        bullets[:] = [b for b in bullets if -margin < b.x < w + margin and -margin < b.y < h + margin]

    def touches_player(self, player):
        r = player.width * HIT_RADIUS_SHARE
        if math.dist(self.mascot, (player.x, player.y)) < MASCOT_RADIUS + r:
            return True
        return any(h.touches(player.x, player.y, r, self.beat) for h in self.hazards)

    def count_hit(self, player):
        """After the frame: a lost bit of HP = one hit; the HP comes back (you can't die here)."""
        if player.hp < player.max_hp:
            self.hits += 1
            player.hp = player.max_hp
            player.imm_frames = max(player.imm_frames, SONG_IMMUNITY)

    # --- the result ------------------------------------------------------------------------------------------
    @property
    def grade(self):
        return next((g for g, most in GRADES if self.hits <= most), "D")

    @property
    def prize_won(self):
        return self.grade == "A" and self.prize_available

    @property
    def gold(self):
        return 0 if self.prize_won else GRADE_GOLD[self.grade]

    def reward_text(self):
        if self.prize_won:
            return f"New item: {self.prize_name}"
        return f"{self.gold}$" if self.gold else "No reward"

    # --- drawing ---------------------------------------------------------------------------------------------
    def draw_world(self, screen):
        if self.dark > 0:
            veil = pygame.Surface(self.arena, pygame.SRCALPHA)
            veil.fill((0, 0, 0, int(255 * self.dark)))
            screen.blit(veil, (0, 0))
        self.layer.fill((0, 0, 0, 0))
        for hazard in self.hazards:
            hazard.draw(self.layer, self.beat)
        for emitter in self.emitters:
            emitter.draw(self.layer, self.beat)
        screen.blit(self.layer, (0, 0))
        self.draw_mascot(screen)

    def draw_flash(self, screen):
        """Climax: a pink flash on every beat (drawn over the bullets)."""
        if not self.flash or self.beat < 0:
            return
        fade = 1 - (self.beat % 1)
        veil = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        veil.fill(PINK + (int(FLASH_ALPHA * fade * fade),))
        screen.blit(veil, (0, 0))

    def draw_mascot(self, screen):
        x, y = int(self.mascot[0]), int(self.mascot[1])
        pygame.draw.circle(screen, MASCOT_COLOUR, (x, y), MASCOT_RADIUS)

    def draw_hud(self, screen, font):
        """Only a thin bar: how far the song is (no HP, no hits - you see how you did at the end)."""
        w = screen.get_width()
        bar = pygame.Rect(0, 0, int(w * 0.5), PROGRESS_HEIGHT)
        bar.midtop = (w // 2, 40)
        share = min(1.0, max(0.0, self.beat / self.end_beat))
        pygame.draw.rect(screen, (60, 50, 80), bar)
        pygame.draw.rect(screen, PINK, (bar.x, bar.y, int(bar.width * share), bar.height))
        name = font.render("Mascot", True, (240, 230, 245))
        screen.blit(name, name.get_rect(midbottom=(w // 2, bar.top - 6)))
        self.draw_music_hint(screen, font, bar.bottom + 14)

    def draw_music_hint(self, screen, font, top):
        """(11.11) "Music recommended" under the bar for a few seconds, when the music is (almost) off."""
        if self.music_hint_left <= 0:
            return
        self.music_hint_left -= 1
        hint = font.render(MUSIC_HINT, True, PINK)
        hint.set_alpha(min(255, self.music_hint_left * 255 // 60))
        screen.blit(hint, hint.get_rect(midtop=(screen.get_width() // 2, top)))

    def draw_result(self, screen, fonts):
        w, h = screen.get_size()
        panel = pygame.Rect(0, 0, w // 4, int(h / 2.4))
        panel.center = (w // 2, h // 2)
        pygame.draw.rect(screen, (36, 30, 54), panel, 0, 12)
        pygame.draw.rect(screen, PINK, panel, 3, 12)
        lines = [(fonts["mid"], "Rank:", (240, 230, 245), 0.12),
                 (fonts["giant"], self.grade, GRADE_COLOURS[self.grade], 0.38),
                 (fonts["small"], f"Hits: {self.hits}", (220, 210, 230), 0.62),
                 (fonts["small"], self.reward_text(), (255, 210, 120), 0.8)]
        for font, text, colour, y in lines:
            img = font.render(text, True, colour)
            screen.blit(img, img.get_rect(center=(panel.centerx, panel.top + panel.height * y)))
        click = fonts["giant"].render("CLICK", True, (255, 255, 255))
        screen.blit(click, click.get_rect(center=(w // 2, int(h / 1.3) + click.get_height() // 2)))
