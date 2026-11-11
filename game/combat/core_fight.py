# THE CORE FIGHT (10.11): Milo, the last boss of the normal game. Combat runs this script next to the two enemies
# (Milo and the heart of the Core, both from EnemyDB). Everything happens on the heart's beats; the heart beats
# faster the less HP Milo has (60 -> 140 BPM). The heart stands in the middle: it blocks your shots and is shielded
# while Milo stands (it is "guarded" by him); touching it burns.
#   F1 "Guard"     (100-75%)  rings from the heart, Milo shoots 3 at a time
#   F2 "Cracks"    (75-50%)   3 cracks at once run from the heart in random directions (they hurt to touch);
#                             the arena BREATHES (the heart pulls you in, hardest on the beat);
#                             every ~12 s Milo REWINDS TIME 3 s (everything goes back, only HP stays) - see time_rewind.py
#   F3 "Overheat"  (50-25%)   the heart spins out streams of bullets; Milo slowly hides behind it, but every 4 beats
#                             steps out (and glows) to drop a mine - that's when you hit him; rings with gaps
#   F4 "Despair"   (25-0%)    everything but the cracks (the breathing weaker, the rewinds rarer); he circles steadily
#   Milo falls -> the heart stops, silence, a strange ~2 s ... then a (fake) "Win! CLICK".
#   F5 (after the click) - a fight you can't lose: Milo lies there, the heart has lost its shield and races.
#     without the Peace Gun: break the heart -> "See you soon." -> white -> Main ending (Game)
#     with the Peace Gun:    shoot the heart once -> it stops; Milo talks about the Void (Game: a talk, Void opens)
# Milo says a line at the start and at every phase (subtitles now, recorded lines later - core_parts.Subtitles).

import math
import random

import pygame

from game.combat import core_parts as PARTS
from game.combat.song.emitters import Spinner, bullet
from game.combat.time_rewind import TimeRewind
from game.menu import options as OPT

LINES = {"enter": "Every beat of this heart is a day nobody gets hurt.",
         "phase2": "Hear it speeding up? That's you. You're doing that.",
         "phase3": "Stop! You don't know what's down there!",
         "phase4": "I've done this before. I'll do it again. As many times as it takes.",
         "fall": "...no.",
         "dont": "Don't... please...",
         "goodbye": "See you soon."}

DAMAGE = {"ring": 2200, "burst": 2400, "crack": 2400, "wave": 2400, "mine": 2200, "stream": 2000}
BULLET_KIND = {"ring": "normal_red", "burst": "bullet_red", "mine": "normal_yellow", "stream": "normal_red",
               "wave": "normal_red"}
ORBIT = 320                       # px: Milo walks round the heart about this far from it
WANDER_RADIUS = (270, 370)        # (11.11) F1, F2: he wanders round the heart - not like a planet: now one way,
WANDER_TURN = (0.5, 2.0)          #   now the other (a new goal this many radians round), a bit nearer / further,
WANDER_FRAMES = (60, 150)         #   a new goal every this many frames
WANDER_SPEED = 0.012              # radians per frame at most
ORBIT_TURN = (0.006, 0.0067)      # radians per frame: walking round / going (slowly) to hide (F3)
PEEK_EVERY, PEEK_BEATS = 4, 1.5   # F3: every 4 beats he steps out from behind the heart for 1.5 beats
PEEK_SIDE = math.radians(75)      # ... this far round from "right behind it" (the heart isn't between you then)
PEEK_TURN = 0.045                 # radians per frame while stepping out (quick)
PEEK_GLOW = (255, 240, 170)
PEEK_ORBIT = 190                  # px from the heart while stepping out (closer than his usual walk)
CRACK = {"speed": 12, "every": 10 ** 6, "bullets": None}   # (no bullets: the crack itself hurts - Combat)
CRACKS_AT_ONCE = {1: 3}           # F2 (none in F4)
BREATH = {1: 2.0, 3: 1.2}         # px per frame the heart pulls you in (F2, F4), at most (on the beat)
BREATH_NEAR = (0.5, 1.4)          # ... weaker far from the heart, stronger close to it
REWIND_EVERY = {1: 12 * 60, 3: 20 * 60}   # frames between rewinds (F2, F4)
REWIND_WARN_BEATS = 1             # the ghost (where you'll end up) shows this long before
GHOST = (170, 210, 255)
WAVE_BULLETS, WAVE_GAP, WAVE_SPEED = 40, math.radians(16), 4.5   # a ring from the heart with 2 gaps (each this wide)
FALL_SILENCE = 140                # frames between Milo falling and the (fake) "Win!" - a bit too long, on purpose
WHITE_FRAMES = 120                # the heart breaks: the screen goes white this long
MILO_COLOUR = (255, 196, 96)      # warm amber (redder every phase: EnemyDB.boss_info)
HEART_COLOUR = (200, 30, 60)


class CoreFight:
    def __init__(self, milo, heart_enemy, arena, bullet_info, font, peace_gun):
        self.milo = milo
        self.heart_enemy = heart_enemy
        self.arena = arena
        self.centre = (arena[0] / 2, arena[1] / 2)
        self.bullet_info = bullet_info
        self.peace_gun = peace_gun                # the Peace Gun in hand: F5 ends with a talk about the Void
        self.heart = PARTS.Heart()
        self.subtitles = PARTS.Subtitles(font, OPT.volume("dialogue"))     # (11.11) Settings: dialogue volume
        self.state = "fight"                      # fight -> fall -> fake_win -> broken -> white -> (finished)
        self.phase = -1
        self.count = 0                            # beats since the phase started
        self.angle = math.pi / 2                  # where Milo is round the heart
        self.radius = ORBIT                       # ... and how far from it
        self.wander = None                        # (goal angle, goal radius, frames left)
        self.peek_until = -1.0                    # F3: he is out from behind the heart until this beat
        self.mines = []
        self.spinner = None
        self.rewind = TimeRewind()
        self.rewind_at = None                     # frame (of the phase) of the next rewind; its warning comes first
        self.rewind_warned = None                 # the beat the warning started on
        self.phase_frames = 0
        self.timer = 0                            # frames in the current state
        self.finished = False
        self.outcome = None                       # "main" / "void"
        self.music_cue = None                     # "stop" -> Game stops the boss music
        self.sounds = []                          # (name, volume) to play this frame
        self.begged = False
        milo.undying = True                       # Combat never removes him; he "falls" here
        heart_enemy.guards = [milo]               # the heart is shielded while he stands
        heart_enemy.base_width = heart_enemy.width
        heart_enemy.color = HEART_COLOUR
        milo.color = MILO_COLOUR
        self.place_milo()

    # --- what Combat asks ------------------------------------------------------------------------------------
    @property
    def holds_time(self):
        """While time runs backwards the rest of the fight stands still (Combat only calls update())."""
        return self.rewind.playing

    @property
    def allows_shooting(self):
        return self.state in ("fight", "broken")

    @property
    def shows_fake_win(self):
        return self.state == "fake_win"

    def click(self):
        if self.state == "fake_win":
            self.start_state("broken")

    # --- every frame -----------------------------------------------------------------------------------------
    def update(self, combat):
        self.sounds = []
        self.timer += 1
        if self.timer == 1 and self.state == "fight" and self.phase == -1:
            self.say("enter")
        if self.state == "fight":
            self.update_fight(combat)
        elif self.state == "fall":
            self.update_fall(combat)
        elif self.state == "broken":
            self.update_broken(combat)
        elif self.state == "white" and self.timer >= WHITE_FRAMES:
            self.finish("main")

    def start_state(self, state):
        self.state, self.timer = state, 0

    def finish(self, outcome):
        self.finished, self.outcome = True, outcome

    def say(self, key):
        self.subtitles.say(key, LINES[key])

    # --- F1-F4 -----------------------------------------------------------------------------------------------
    def update_fight(self, combat):
        if self.rewind.playing:
            self.play_rewind(combat)
            return
        if self.milo.hp <= 0:
            self.fall(combat)
            return
        self.check_phase()
        self.phase_frames += 1
        self.heart.set_pace(self.milo.hp / self.milo.max_hp)
        self.move_milo(combat.player)
        self.breathe(combat.player)
        if self.heart.tick():
            self.on_beat(combat)
            self.count += 1
            self.time_rewind_on_beat(combat)
        new = self.spinner.update(self.heart.beat, self.centre) if self.spinner else []
        combat.enemy_projectiles.extend(new)
        self.update_mines(combat)
        self.drop_far_bullets(combat.enemy_projectiles)
        if self.phase in REWIND_EVERY:
            self.rewind.remember(self.moment(combat))

    def check_phase(self):
        phase = len(self.milo.phase_marks) - len(self.milo.phases)
        if phase == self.phase:
            return
        self.phase, self.count, self.phase_frames = phase, 0, 0
        self.spinner = None
        self.rewind.forget()
        self.rewind_at = REWIND_EVERY.get(phase)
        self.rewind_warned = None
        if phase >= 1:
            self.say(f"phase{phase + 1}")
        spin = {2: dict(arms=3, rate=1.5, turn=25), 3: dict(arms=2, rate=1.5, turn=-30)}.get(phase)
        if spin:
            spec = dict(spin, speed=6, width=12, kind=BULLET_KIND["stream"], damage=DAMAGE["stream"], reach=None)
            self.spinner = Spinner(self.heart.beat, 10 ** 6, spec, self.bullet_info, self.arena)

    def on_beat(self, combat):
        self.sounds.append(("core_heart", self.heart.volume()))
        k, player = self.count, combat.player
        plan = {0: self.beat_guard, 1: self.beat_cracks, 2: self.beat_overheat, 3: self.beat_despair}[self.phase]
        plan(k, player, combat)

    def beat_guard(self, k, player, combat):
        if k % 2 == 0:
            self.ring(combat, self.centre, 8, 5, k * 11)
        else:
            self.burst(combat, player)

    def beat_cracks(self, k, player, combat):
        if k % 2 == 0:
            self.cracks(combat)
        elif k % 4 == 1:
            self.ring(combat, self.centre, 8, 5, k * 7)

    def beat_overheat(self, k, player, combat):
        if k % PEEK_EVERY == 0:
            self.peek_until = self.heart.beat + PEEK_BEATS
        if k % PEEK_EVERY == 1:                            # (out in the open by now)
            self.mines.append(PARTS.Mine((self.milo.x, self.milo.y), self.heart.beat + 4))
        if k % 8 == 6:
            self.wave(combat, k)

    def beat_despair(self, k, player, combat):
        if k % 2 == 1:
            self.burst(combat, player)
        if k % 8 == 2:
            self.wave(combat, k)
        if k % 8 == 6:
            self.mines.append(PARTS.Mine((self.milo.x, self.milo.y), self.heart.beat + 4))

    # --- attacks -----------------------------------------------------------------------------------------------
    def shot(self, origin, angle, speed, kind):
        return bullet(*origin, angle, speed, 12, BULLET_KIND[kind], self.bullet_info, self.arena,
                      DAMAGE[kind], None)

    def ring(self, combat, origin, count, speed, turn_deg, kind="ring"):
        start = math.radians(turn_deg)
        combat.enemy_projectiles += [self.shot(origin, start + i * math.tau / count, speed, kind)
                                     for i in range(count)]

    def burst(self, combat, player):
        """3 shots at you in a row (one behind the other)."""
        a = math.atan2(player.y - self.milo.y, player.x - self.milo.x)
        combat.enemy_projectiles += [self.shot((self.milo.x, self.milo.y), a, speed, "burst") for speed in (9, 10.5, 12)]

    def cracks(self, combat):
        """A few cracks run from the heart in random directions at once (they hurt to touch, no bullets)."""
        for n in range(CRACKS_AT_ONCE[self.phase]):
            combat.add_crack(dict(CRACK, damage=DAMAGE["crack"], x=self.centre[0], y=self.centre[1],
                                  angle=random.uniform(0, math.tau), max=self.arena[0] + self.arena[1],
                                  start=self.heart_enemy.base_width), sound=n == 0)

    def wave(self, combat, k):
        """A ring of bullets from the heart with 2 gaps (opposite each other) to slip through."""
        first = math.radians(k * 37 % 360)
        for i in range(WAVE_BULLETS):
            a = first + i * math.tau / WAVE_BULLETS
            if min(abs((a - g + math.pi) % math.tau - math.pi) for g in (first, first + math.pi)) < WAVE_GAP:
                continue
            combat.enemy_projectiles.append(self.shot(self.centre, a, WAVE_SPEED, "wave"))

    # --- Milo's walk -----------------------------------------------------------------------------------------
    def place_milo(self):
        pos = (self.centre[0] + math.cos(self.angle) * self.radius, self.centre[1] + math.sin(self.angle) * self.radius)
        self.set_milo(pos)

    def set_milo(self, pos):
        self.milo.x, self.milo.y = pos
        self.milo.anchor = pos

    def move_milo(self, player):
        if self.phase == 2:                                # hides behind the heart (the heart between you) ...
            goal = math.atan2(player.y - self.centre[1], player.x - self.centre[0]) + math.pi
            if self.peeking:                               # ... but now and then steps out to the side
                goal += PEEK_SIDE
            turn = (goal - self.angle + math.pi) % math.tau - math.pi
            rate = PEEK_TURN if self.peeking else ORBIT_TURN[1]
            self.angle += max(-rate, min(rate, turn))
        elif self.phase == 3:                              # (11.11) F4: steady round and round, like a planet
            self.angle += ORBIT_TURN[0]
        else:
            self.wander_step()
        radius = PEEK_ORBIT if self.peeking else (self.radius if self.phase in (0, 1) else ORBIT)
        goal = (self.centre[0] + math.cos(self.angle) * radius, self.centre[1] + math.sin(self.angle) * radius)
        here = (self.milo.x, self.milo.y)
        self.set_milo((here[0] + (goal[0] - here[0]) * 0.08, here[1] + (goal[1] - here[1]) * 0.08))

    def wander_step(self):
        """Round the heart towards a goal that changes now and then (either way, a bit nearer or further)."""
        if self.wander is None or self.wander[2] <= 0:
            turn = random.choice((-1, 1)) * random.uniform(*WANDER_TURN)
            self.wander = (self.angle + turn, random.uniform(*WANDER_RADIUS), random.randint(*WANDER_FRAMES))
        goal, radius, left = self.wander
        self.angle += max(-WANDER_SPEED, min(WANDER_SPEED, goal - self.angle))
        self.radius += (radius - self.radius) * 0.02
        self.wander = (goal, radius, left - 1)

    def face_player(self, player):
        """(11.11) At the start he stands on the other side of the heart from you."""
        self.angle = math.atan2(player.y - self.centre[1], player.x - self.centre[0]) + math.pi
        self.place_milo()

    # --- the breathing heart (F2, F4) -----------------------------------------------------------------------------
    def breathe(self, player):
        """The heart pulls you in - hardest on the beat, hardly between beats (stronger close to it)."""
        strength = BREATH.get(self.phase)
        if not strength:
            return
        dx, dy = self.centre[0] - player.x, self.centre[1] - player.y
        d = math.hypot(dx, dy) or 1
        near = max(BREATH_NEAR[0], min(BREATH_NEAR[1], BREATH_NEAR[1] - d / (self.arena[0] / 2)))
        pull = (1 + math.cos(math.tau * (self.heart.beat % 1))) / 2 * strength * near   # strongest on the beat
        player.x += dx / d * pull
        player.y += dy / d * pull

    # --- the time rewind (F2, F4) -------------------------------------------------------------------------------
    def time_rewind_on_beat(self, combat):
        """A beat: the warning starts (the ghost shows where you'll end up); a beat later time runs back."""
        if self.rewind_at is None or self.phase_frames < self.rewind_at or self.rewind.oldest() is None:
            return
        if self.rewind_warned is None:
            self.rewind_warned = self.heart.beat
        elif self.heart.beat - self.rewind_warned >= REWIND_WARN_BEATS:
            self.rewind.start()
            self.rewind_warned = None
            self.rewind_at = self.phase_frames + REWIND_EVERY[self.phase]

    def moment(self, combat):
        """Everything the rewind puts back (not HP)."""
        p = combat.player
        return {"tick": pygame.time.get_ticks(),
                "player": (p.x, p.y, p.slide_x, p.slide_y),
                "enemy_bullets": [(b, dict(b.__dict__)) for b in combat.enemy_projectiles],
                "player_bullets": [(b, dict(b.__dict__)) for b in combat.player_projectiles],
                "cracks": [dict(c, segs=list(c.get("segs", []))) for c in getattr(combat, "cracks", [])],
                "milo": (self.milo.x, self.milo.y, self.angle),
                "heart": self.heart.beat, "count": self.count, "peek_until": self.peek_until,
                "mines": list(self.mines), "spinner": self.spinner.next_shot if self.spinner else None}

    def put_back(self, combat, m):
        p = combat.player
        p.x, p.y, p.slide_x, p.slide_y = m["player"]
        waited = pygame.time.get_ticks() - m["tick"]           # bullets' range runs on real time
        for key, bullets in (("enemy_bullets", combat.enemy_projectiles), ("player_bullets", combat.player_projectiles)):
            for b, state in m[key]:
                b.__dict__.update(state)
                b.shot_time = state["shot_time"] + waited
            bullets[:] = [b for b, _ in m[key]]
        combat.cracks = [dict(c, segs=list(c["segs"])) for c in m["cracks"]]
        self.milo.x, self.milo.y, self.angle = m["milo"]
        self.set_milo((self.milo.x, self.milo.y))
        self.heart.beat, self.count, self.peek_until = m["heart"], m["count"], m["peek_until"]
        self.mines = list(m["mines"])
        if self.spinner and m["spinner"] is not None:
            self.spinner.next_shot = m["spinner"]

    def play_rewind(self, combat):
        moment = self.rewind.next_moment()
        if moment is not None:
            self.put_back(combat, moment)
        combat.player.imm_frames = max(combat.player.imm_frames, 20)    # nothing hurts while time runs back

    @property
    def ghost(self):
        """Where you'll be after the rewind (shown during its warning and while it plays), or None."""
        if self.rewind.playing:
            return self.rewind.playback[-1]["player"][:2]
        if self.rewind_warned is not None and self.rewind.oldest():
            return self.rewind.oldest()["player"][:2]
        return None

    def drop_far_bullets(self, bullets):
        """Bullets that left the arena are gone (they'd only fly on unseen)."""
        w, h = self.arena
        bullets[:] = [b for b in bullets if -60 < b.x < w + 60 and -60 < b.y < h + 60]

    # --- mines ---------------------------------------------------------------------------------------------------
    def update_mines(self, combat):
        for mine in [m for m in self.mines if m.due(self.heart.beat)]:
            self.mines.remove(mine)
            self.ring(combat, mine.pos, 10, 5, 0, kind="mine")

    # --- Milo falls, the fake win ------------------------------------------------------------------------------
    def fall(self, combat):
        """The heart stops, everything goes quiet - and stays quiet a little too long."""
        self.say("fall")
        self.start_state("fall")
        self.heart.stopped = True
        self.music_cue = "stop"
        self.milo.color = (110, 110, 110)
        combat.enemy_projectiles.clear()
        self.mines, self.spinner = [], None
        self.rewind = TimeRewind()
        self.rewind_at = self.rewind_warned = None
        combat.cracks = []

    def update_fall(self, combat):
        combat.enemy_projectiles.clear()
        if self.timer >= FALL_SILENCE:
            self.start_state("fake_win")

    # --- F5: the heart, a fight you can't lose -----------------------------------------------------------------
    def update_broken(self, combat):
        if self.timer == 1:
            self.heart.stopped, self.heart.broken = False, True
        self.heart.set_pace(0)
        if self.heart.tick():
            self.sounds.append(("core_heart", 1.0))
        hurt = self.heart_enemy.hp < self.heart_enemy.max_hp
        if hurt and self.peace_gun:
            self.heart.stopped = True
            self.finish("void")
        elif hurt and not self.begged:
            self.begged = True
            self.say("dont")
        if self.heart_enemy.hp <= 0 or self.heart_enemy not in combat.enemies:
            self.say("goodbye")
            self.heart.stopped = True
            self.start_state("white")

    # --- drawing -------------------------------------------------------------------------------------------------
    @property
    def peeking(self):
        return self.state == "fight" and self.phase == 2 and self.heart.beat < self.peek_until

    def draw_world(self, screen, layer):
        """Under the bullets: the mines, Milo's glow when he steps out (F3), your ghost before / during a rewind."""
        layer.fill((0, 0, 0, 0))
        ghost = self.ghost
        if ghost:
            alpha = 120 if self.rewind.playing else 55                  # a subtle warning, clear while it plays
            pygame.draw.circle(layer, GHOST + (alpha,), (int(ghost[0]), int(ghost[1])), 25, 3)
        if self.peeking:
            pygame.draw.circle(layer, PEEK_GLOW + (110,), (int(self.milo.x), int(self.milo.y)), self.milo.width + 18)
        screen.blit(layer, (0, 0))
        for mine in self.mines:
            mine.draw(screen, self.heart.beat)
        self.heart_enemy.width = int(self.heart_enemy.base_width * self.heart.pulse())

    def draw_hud(self, screen):
        if self.rewind.playing:
            self.draw_rewind_look(screen)
        self.subtitles.draw(screen)
        if self.state == "white":
            veil = pygame.Surface(screen.get_size())
            veil.fill((255, 255, 255))
            veil.set_alpha(min(255, int(255 * self.timer / (WHITE_FRAMES * 0.7))))
            screen.blit(veil, (0, 0))

    @staticmethod
    def draw_rewind_look(screen):
        """While time runs back: a cold tint and lines like an old tape."""
        w, h = screen.get_size()
        veil = pygame.Surface((w, h), pygame.SRCALPHA)
        veil.fill((80, 120, 200, 45))
        for y in range(0, h, 6):
            pygame.draw.line(veil, (255, 255, 255, 22), (0, y), (w, y))
        screen.blit(veil, (0, 0))
