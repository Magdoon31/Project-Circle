# THE VOID (11.11): the last boss. Combat runs this script next to the boss (EnemyDB "void_boss"); Game gives it
# the arena (void_arena.py, 2 x 2 screens), the music (lib/music_sequence.py: "Fire and Thunder" by Cjbeards,
# CC BY 3.0 - goes into the end credits) and a way to make the boss again (checkpoints).
#   silence (5 s, nothing happens) -> the boss comes in (the music starts) -> F1-F5 (the boss's own phases: what the
#   system cut away - Slime King / Prism, Shroom Mother / Frost Golem, the Factory, Night Bloom in the Pale World,
#   everything) -> the interlude (no fighting: its few words) -> the end (only dodging, not on the HP bar; at the
#   peak of the music YOU shoot by yourself and it is over) -> it falls apart -> Game: the ending.
# - the music: every part loops; a new phase's part comes in on the next 8-beat line (lib/music_sequence.py)
# - off the islands = the abyss (only when all of you is off, and never while you can't be hurt): you sink for a
#   moment, then a hit (FALL_HIT of your max HP), back onto the nearest island and twice your usual immunity
# - the boss never goes out past the ring of the outer islands (it would be too hard to hit there)
# - F3: the bridges are conveyor belts - they carry you and the bullets on them; Scrap Beetles and Toy Soldiers
#   come up on the outer islands now and then (void_helpers.py)
# - F3-F4: a big slow shot (it follows you a little) knocks your weapon to a far island (you can't shoot, you're
#   faster); walk onto it
# - Milo's memory (F1-F4): when ready (he glows) he catches the bullets coming close to you; goes to your lost
#   weapon; not in F5
# - F4 is in the Pale World: bullets are only outlines; the boss and 3 copies round you (void_copies.py)
# - F5: the outer islands blink and fall away (you too, if you're there), the middle grows; turrets come up out of
#   the far islands for one shot (void_turrets.py); the boss flies round the middle island
# - the interlude: it stands still and says its few words, then it breaks up (glitches) into its new form
# - the end: the camera zooms and turns a little (void_camera.py); the boss jumps about and you may shoot it - it
#   does nothing; after your shot it dies to the rest of the music (void_finale.py); 2 s after the music the screen
#   goes black - white if you used the lore items (Game says which)
# - 3 lives: dying shows "Game Over"; a click goes back to the last checkpoint (the start, F4 - marked on the
#   boss's bar - the interlude); the 3rd death = lost (Game). Emergency Protocol works first, every life.

import math
import random

import pygame

from game.combat import void_parts as PARTS
from game.combat.song.emitters import Ring, Spinner, Walls
from game.combat.void_camera import VoidCamera
from game.combat.void_copies import VoidCopies
from game.combat.void_helpers import VoidHelpers
from game.combat import void_finale as FINALE
from game.combat.void_turrets import Turrets

SILENCE_FRAMES = 5 * 60
ENTER_FRAMES = 2 * 60
LIVES = 3
FALL_HIT = 0.25                   # share of your max HP a fall into the abyss costs
FALL_FRAMES = 30                  # you sink into the abyss this long before you come back
FALL_IMMUNITY_TIMES = 2           # ... then twice your usual immunity after a hit (Magic Dust counts)
CHECKPOINT_MARK = (255, 228, 150)
PALE_PHASE = 3                    # F4
DISARM_PHASES = (2, 3)            # F3, F4
DISARM_EVERY = 11 * 60
MILO_PHASES = (0, 1, 2, 3)        # gone in F5
HELPERS_PHASE = 2                 # F3: the Factory's toys on the outer islands
COPIES_PHASE = 3                  # F4: the boss and its copies round you
TURRETS_PHASE = 4                 # F5: turrets on the far islands; the boss flies round the middle island
FLIGHT = (560, 130, 0.006)        # F5: px from the middle, going in and out by, turns a frame (radians)
RING_PHASES = (0, 1, 2)           # the boss is kept inside the ring of the outer islands (later: Void moves it)
CHECKPOINTS = {0: "start", 3: "phase4"}       # phase -> its checkpoint (and "interlude")
PHASE_MUSIC = ["void_phase1", "void_phase2", "void_phase3", "void_phase4", "void_phase5"]   # (MusicSequence parts)
MONOLOGUE = [(4000, "I am every day that was taken away."),
             (12500, "every quiet night. every name no one says anymore."),     # (11.11: a proposal - to confirm)
             (21000, "and you came to take one more.")]
INTERLUDE_ZOOM = 1.18             # the camera comes slowly this close over the interlude
FINAL_FIRST_BEAT_MS = 75          # final_scene: where its first beat is
FINAL_SHOT_MS = 28770             # (11.11) ... the peak (beat 66, 28.7 s): your shot hits it right then
SHOT_FLIGHT_MS = 500
FINAL_DAMAGE = 6500
JUMP = (420, 560)                 # the end: the boss jumps to somewhere this far from you (px)
JUMP_FLASH = 18                   # frames a jump's flash shows
SHOT_ZOOM = 1.4                   # the camera on the boss as your shot hits
INTERLUDE_MS = 31190              # the interlude's length (its glitching ends with it)
DROP_WARNING = "The islands are falling!"
BEAT_MS = 60_000 / 138
PLAYER_START = (0, 230)           # px from the middle of the arena
BOSS_SPOT = (0, -170)
SHOT_COLOUR = (255, 245, 200)
BOSS_COLOUR = (175, 150, 235)


class VoidFight:
    def __init__(self, boss, make_boss, arena, music, bullet_info, font, now, light_ending=False, make_enemy=None):
        self.boss = boss
        self.make_boss = make_boss                # () -> a new boss (Enemy) for a checkpoint
        self.make_enemy = make_enemy              # name -> a new Enemy (F3's helpers)
        self.arena = arena                        # VoidArena
        self.music = music                        # MusicSequence
        self.bullet_info = bullet_info
        self.name = PARTS.GlitchName()
        self.words = PARTS.BrokenWords(font)
        self.font = font
        self.lives = LIVES
        self.checkpoint = "start"
        self.timer = 0
        self.state = "silence"
        self.phase = -1
        self.disarm_shots, self.weapon, self.milo = [], None, None
        self.copies, self.turrets, self.helpers = None, None, None
        self.camera = VoidCamera()
        self.flashes = []                         # the end: where the boss just jumped from / to: [x, y, frames left]
        self.glitch = self.dying = None           # the interlude's glitching, its dying after your shot
        self.fade = FINALE.FadeOut(light_ending)  # black - white with the lore items used
        self.final_beat, self.spinner, self.emitters = -1, None, []
        self.shot = None                          # your last shot in the end: (x, y, start tick)
        self.said = 0
        self.finished = False
        self.dead = False                         # "Game Over" on the screen, waiting for a click
        self.falling = None                       # (where, frames left) while you sink into the abyss
        self.prepare_boss(boss)
        self.hide_boss()

    # --- what Combat asks ------------------------------------------------------------------------------------
    @property
    def allows_shooting(self):
        """In the end too - your bullets fly through it (nothing you do hurts it there)."""
        return (self.state == "fight" and self.weapon is None) or self.state == "final"

    @property
    def holds_world(self):
        """While "Game Over" waits for a click, nothing in the fight moves."""
        return self.dead

    @property
    def freezes_boss(self):
        return self.state != "fight"

    @property
    def pale(self):
        return self.state == "fight" and self.phase == PALE_PHASE

    @property
    def shows_boss_bar(self):
        return self.state in ("enter", "fight")

    # --- the boss ---------------------------------------------------------------------------------------------
    def prepare_boss(self, boss):
        boss.color = BOSS_COLOUR
        boss.base_width = boss.width
        boss.undying = True                       # it never "dies" in Combat: it goes on to the interlude
        boss.bar_on_hud = True                    # (a big arena: its bar is drawn on the screen, not the world)
        boss.boss_name = self.name.update(0)

    def hide_boss(self):
        self.boss.x, self.boss.y = self.arena.centre[0], -400
        self.boss.anchor = None

    def boss_spot(self):
        return self.arena.centre[0] + BOSS_SPOT[0], self.arena.centre[1] + BOSS_SPOT[1]

    # --- every frame -----------------------------------------------------------------------------------------
    def update(self, combat, now):
        if self.dead:
            return
        self.timer += 1
        self.boss.boss_name = self.name.update(self.timer)
        self.boss.light_label = not self.pale                # (its name readable over the dark abyss)
        self.arena.update()
        self.camera.update()
        self.flashes = [[x, y, left - 1] for x, y, left in self.flashes if left > 1]
        {"silence": self.update_silence, "enter": self.update_enter, "fight": self.update_fight,
         "interlude": self.update_interlude, "final": self.update_final,
         "falling_apart": self.update_falling_apart}[self.state](combat, now)
        if self.state == "fight" and self.phase in RING_PHASES:
            self.arena.keep_inside_ring(self.boss)
        if self.state in ("fight", "interlude", "final"):
            self.check_fall(combat)
        self.arena.push_bullets(combat.enemy_projectiles)

    def start_state(self, state):
        self.state, self.timer = state, 0

    def update_silence(self, combat, now):
        if self.timer >= SILENCE_FRAMES:
            self.start_state("enter")
            self.music.start(PHASE_MUSIC[0], now)

    def update_enter(self, combat, now):
        """It comes down onto the middle island."""
        gx, gy = self.boss_spot()
        k = min(1.0, self.timer / ENTER_FRAMES)
        k = k * k * (3 - 2 * k)
        self.boss.x, self.boss.y = gx, -400 + (gy + 400) * k
        if self.timer >= ENTER_FRAMES:
            self.start_state("fight")

    def update_fight(self, combat, now):
        if self.boss.hp <= 0:
            self.start_interlude(combat, now)
            return
        self.check_phase(combat, now)
        self.update_weapon(combat)
        if self.milo:
            self.milo.update(combat.player, self.weapon.pos if self.weapon else None, combat.enemy_projectiles)
        player = (combat.player.x, combat.player.y)
        if self.helpers:
            self.helpers.update(self.arena, combat.player, combat.enemies)
        if self.copies:
            combat.enemy_projectiles.extend(self.copies.update(player))
            self.boss.x, self.boss.y = self.copies.real
            self.boss.untouchable = not self.copies.solid            # (faded away: your bullets fly through)
        if self.phase == TURRETS_PHASE:
            self.fly_round_middle()
            if self.turrets and not self.arena.outer_solid and not self.arena.drop:
                combat.enemy_projectiles.extend(self.turrets.update(self.arena.outer_islands(), player))

    def fly_round_middle(self):
        """F5: round and round the middle island, a little in and out (not a perfect circle)."""
        reach, breath, turn = FLIGHT
        a = self.timer * turn
        r = reach + breath * math.sin(self.timer * 0.011)
        gx, gy = self.arena.centre[0] + math.cos(a) * r, self.arena.centre[1] + math.sin(a) * r * 0.8
        self.boss.x += (gx - self.boss.x) * 0.05
        self.boss.y += (gy - self.boss.y) * 0.05

    def check_phase(self, combat, now):
        phase = len(self.boss.phase_marks) - len(self.boss.phases)
        if phase == self.phase:
            return
        first = self.phase == -1
        self.phase = phase
        self.arena.set_layout(phase, instant=first)
        if not first:
            self.music.switch_to(PHASE_MUSIC[phase], now)
        if phase in CHECKPOINTS:
            self.checkpoint = CHECKPOINTS[phase]
        if phase in MILO_PHASES and self.milo is None:
            self.milo = PARTS.MiloMemory((combat.player.x, combat.player.y))
        elif phase not in MILO_PHASES:
            self.milo = None
        if phase not in DISARM_PHASES:
            self.give_weapon_back(combat.player)
            self.disarm_shots = []
        if phase != 2:
            combat.last_belts = None                       # the Factory's belts are gone with its phase
        self.copies = VoidCopies((self.boss.x, self.boss.y), (combat.player.x, combat.player.y), self.bullet_info,
                                 self.arena.size) if phase == COPIES_PHASE else None
        self.boss.hidden = self.copies is not None                   # (the copies draw it - fading, with its shadow)
        self.boss.untouchable = False
        self.turrets = Turrets(self.bullet_info, self.arena.size) if phase == TURRETS_PHASE else None
        if self.helpers:
            self.helpers.leave()
        self.helpers = VoidHelpers(self.make_enemy) if phase == HELPERS_PHASE and self.make_enemy else None

    # --- the weapon -----------------------------------------------------------------------------------------------
    def update_weapon(self, combat):
        player = combat.player
        if self.phase in DISARM_PHASES and self.weapon is None and self.timer % DISARM_EVERY == DISARM_EVERY - 1:
            self.disarm_shots.append(PARTS.DisarmShot((self.boss.x, self.boss.y), (player.x, player.y)))
        for shot in self.disarm_shots[:]:
            shot.update((player.x, player.y))
            if shot.hits(player) and self.weapon is None and player.imm_frames <= 0:
                self.disarm_shots.remove(shot)
                self.weapon = PARTS.LostWeapon(self.arena.far_island(player.x, player.y, 900))
                combat.sfx.play("hit")
            elif shot.life <= 0:
                self.disarm_shots.remove(shot)
        if self.weapon:
            player.effects["speed"] = [2, 0.3]             # without a weapon you are faster
            if self.weapon.picked_up(player):
                self.give_weapon_back(player)
                combat.sfx.play("gain_effect")

    def give_weapon_back(self, player):
        self.weapon = None

    # --- falling into the abyss -------------------------------------------------------------------------------
    def check_fall(self, combat):
        p = combat.player
        if self.falling:
            self.sink(combat)
            return
        push = self.arena.belt_push(p.x, p.y)              # F3: the bridges are conveyor belts
        p.x, p.y = p.x + push[0], p.y + push[1]
        if self.arena.on_ground(p.x, p.y, margin=p.width):
            return                                         # (only when ALL of you is off the ground)
        if p.imm_frames > 0 and not self.arena.collapsing:
            return                                         # (an island falling away takes you with it, always)
        self.falling = ((p.x, p.y), FALL_FRAMES)
        p.base_width = p.width

    def sink(self, combat):
        """You get smaller and smaller where you fell; then a hit and back onto the nearest island."""
        p = combat.player
        (x, y), left = self.falling
        p.x, p.y = x, y
        p.slide_x = p.slide_y = 0.0
        p.width = max(1, int(p.base_width * left / FALL_FRAMES))
        if left > 1:
            self.falling = ((x, y), left - 1)
            return
        self.falling = None
        p.width = p.base_width
        p.x, p.y = self.arena.nearest_island(x, y)
        p.hp -= p.max_hp * FALL_HIT
        p.imm_frames = max(p.imm_frames, FALL_IMMUNITY_TIMES * immunity_after_hit(p))
        combat.sfx.play("player_hit")

    # --- the interlude ------------------------------------------------------------------------------------------
    def start_interlude(self, combat, now):
        self.start_state("interlude")
        self.checkpoint = "interlude"
        self.clear_fight(combat)
        self.boss.hp = 0
        self.music.switch_to("void_interlude", now)
        self.music.then("void_final")
        self.said = 0

    def clear_fight(self, combat):
        combat.enemy_projectiles.clear()
        combat.player_projectiles.clear()
        combat.pending_bullets.clear()
        combat.cracks = []
        combat.last_belts = None
        combat.enemies[:] = [e for e in combat.enemies if e is self.boss]
        self.disarm_shots, self.weapon, self.milo, self.spinner, self.emitters = [], None, None, None, []
        self.copies = self.turrets = self.helpers = None
        self.boss.hidden = self.boss.untouchable = False
        self.flashes = []
        self.glitch = self.dying = None
        self.arena.set_layout(len(PHASE_MUSIC) - 1, instant=True)

    def update_interlude(self, combat, now):
        """It stands still and says its few words (the camera comes slowly closer, between you and it); when all is
        said, it breaks up into its new form."""
        spot = self.boss_spot()
        self.camera.zoom_to(INTERLUDE_ZOOM)
        self.camera.look(((combat.player.x + spot[0]) / 2, (combat.player.y + spot[1]) / 2))
        if self.glitch:
            self.glitch.update(self.boss)
        else:
            self.move_boss_to(spot)
        if self.music.current and self.music.current.name == "void_interlude":
            t = self.music.song_ms(now)
            if self.said < len(MONOLOGUE) and t >= MONOLOGUE[self.said][0]:
                self.words.say(MONOLOGUE[self.said][1])
                self.said += 1
            if self.glitch is None and self.said == len(MONOLOGUE) and self.words.done:
                self.glitch = FINALE.Glitch(spot, (INTERLUDE_MS - t) * 60 / 1000)
        if self.music.current and self.music.current.name == "void_final":
            self.start_final()

    def start_final(self):
        FINALE.settle_in_form(self.boss, (self.boss_spot()))
        self.glitch = None
        self.start_state("final")
        self.final_beat = -1
        self.boss.untouchable = True                       # your bullets fly through it
        self.camera.zoom_to(1.0)
        self.camera.look(None)

    def move_boss_to(self, goal, k=0.05):
        self.boss.x += (goal[0] - self.boss.x) * k
        self.boss.y += (goal[1] - self.boss.y) * k

    # --- the end: only dodging, then your shot --------------------------------------------------------------------
    def update_final(self, combat, now):
        self.boss.hp = 0                                   # (your bullets fly through it anyway)
        t = self.music.song_ms(now)
        beat = (t - FINAL_FIRST_BEAT_MS) / BEAT_MS
        while self.final_beat < math.floor(beat) and t < FINAL_SHOT_MS - BEAT_MS:
            self.final_beat += 1
            self.on_final_beat(self.final_beat, combat)
        origin = (self.boss.x, self.boss.y)
        for e in self.emitters + ([self.spinner] if self.spinner else []):
            combat.enemy_projectiles.extend(e.update(beat, origin))
        self.emitters = [e for e in self.emitters if not e.done(beat)]
        if self.shot is None and t >= FINAL_SHOT_MS - SHOT_FLIGHT_MS:
            self.shot = (combat.player.x, combat.player.y, now)
            self.spinner, self.emitters = None, []
            combat.sfx.play("shoot")
            self.camera.look((self.boss.x, self.boss.y))
            self.camera.zoom_to(SHOT_ZOOM)
        if self.shot and t >= FINAL_SHOT_MS:
            combat.enemy_projectiles.clear()
            combat.sfx.play("explosion")
            self.camera.kick(zoom=0.08, turn=2.5)
            self.dying = FINALE.Dying(self.boss, self.camera)
            self.start_state("falling_apart")

    def on_final_beat(self, b, combat):
        """The end's attacks, on the music's beats (a quiet bar at 13 s, a big hit at 13.9 s, silence at 27.8 s,
        then the peak - your shot). The boss jumps about (every 4 beats, then every 2), the camera kicks on the bars."""
        spec = {"width": 12, "kind": "normal_red", "damage": FINAL_DAMAGE, "reach": None}
        self.final_camera(b)
        if b in (30, 31, 62, 63, 64, 65):
            self.spinner = None                            # the music holds its breath
            if b in (30, 62):
                self.jump_boss(combat.player, above=True)
            return
        if b % (2 if b > 32 else 4) == 0:
            self.jump_boss(combat.player)
        if b < 30 and b % 2 == 0:
            self.emitters.append(Ring(b, dict(spec, bullets=12, speed=5, start=b * 11), self.bullet_info, self.arena.size))
        if b < 30 and b % 8 == 4:
            side = "left" if (b // 8) % 2 == 0 else "right"
            self.emitters.append(Walls(b, side, combat.player.y, dict(spec, gap=200, speed=7), self.bullet_info,
                                       self.arena.size))
        if b in (32, 66):                                  # the big hits
            self.emitters.append(Ring(b, dict(spec, bullets=36, speed=6), self.bullet_info, self.arena.size))
            self.spinner = Spinner(b, 10 ** 6, dict(spec, arms=3, rate=2, turn=40 if b == 32 else -45, speed=6),
                                   self.bullet_info, self.arena.size)
        if b > 32 and b % 4 == 0:
            self.emitters.append(Ring(b, dict(spec, bullets=14, speed=5, start=b * 7), self.bullet_info, self.arena.size))

    def final_camera(self, b):
        if b == 32:
            self.camera.kick(zoom=0.12, turn=2.5)          # the big hit
        elif b % 8 == 0:
            self.camera.kick(zoom=0.05, turn=1.2 if (b // 8) % 2 else -1.2)
        elif b > 32 and b % 4 == 0:                        # (11.11) the later part: a kick every 4 beats ...
            self.camera.kick(zoom=0.04, turn=0.9 if (b // 4) % 2 else -0.9)
        elif b > 48 and b % 2 == 0:                        # ... and the last stretch every 2 (only a little zoom)
            self.camera.kick(zoom=0.025)
        if b == 62:                                        # the silence before the peak: slowly closer
                self.camera.zoom_to(1.12)

    def jump_boss(self, player, above=False):
        """It's gone from where it was and is somewhere else round you (a flash at both places)."""
        a = -math.pi / 2 if above else random.uniform(0, math.tau)
        r = random.uniform(*JUMP)
        self.flashes.append([self.boss.x, self.boss.y, JUMP_FLASH])
        self.boss.x, self.boss.y = player.x + math.cos(a) * r, player.y + math.sin(a) * r
        self.arena.keep_inside_ring(self.boss)
        self.flashes.append([self.boss.x, self.boss.y, JUMP_FLASH])

    def update_falling_apart(self, combat, now):
        """Your shot hit it: it dies to the rest of the music; 2 s of quiet; the screen fades; the ending."""
        t = self.music.song_ms(now)
        self.dying.update(t)
        self.fade.update(t - self.dying.fade_starts_ms)
        if self.fade.done:
            self.finished = True

    # --- dying: the checkpoints -------------------------------------------------------------------------------------
    def catch_death(self, combat, now):
        """The player died. True = "Game Over", then (a click) back to the last checkpoint; False = no lives left."""
        if self.dead:
            return True                                    # (11.11) asked again while "Game Over" waits: same death
        self.lives -= 1
        self.music.stop()
        if self.lives <= 0:
            return False
        self.dead = True
        combat.sfx.play("death")
        return True

    def click(self, combat, now):
        if self.dead:
            self.dead = False
            self.back_to_checkpoint(combat, now)

    def back_to_checkpoint(self, combat, now):
        self.clear_fight(combat)
        p = combat.player
        p.hp = p.max_hp
        p.emergency_used = 1 if "emergency" in p.armor_effect else 0     # a new life: Emergency Protocol again
        if self.falling:
            p.width, self.falling = p.base_width, None
        p.x, p.y = self.arena.centre[0] + PLAYER_START[0], self.arena.centre[1] + PLAYER_START[1]
        p.slide_x = p.slide_y = 0.0
        p.imm_frames = 120
        boss = self.make_boss()
        self.prepare_boss(boss)
        combat.enemies[:] = [boss]
        self.boss = boss
        self.shot, self.final_beat = None, -1
        self.camera.reset()
        self.fade.share = 0.0
        if self.checkpoint == "interlude":
            boss.hp = 0
            boss.x, boss.y = self.boss_spot()
            self.start_state("interlude")
            self.said = 0
            self.music.start("void_interlude", now)
            self.music.then("void_final")
            return
        to_phase = 3 if self.checkpoint == "phase4" else 0
        for _ in range(to_phase):                          # straight to the checkpoint's phase
            boss.hp = boss.max_hp * boss.phases[0]["at"]
            boss.check_phase()
            boss.invuln = 0
        boss.x, boss.y = self.boss_spot()
        self.phase = -1
        self.start_state("fight")
        self.check_phase(combat, now)
        self.music.start(PHASE_MUSIC[to_phase], now)

    # --- drawing ------------------------------------------------------------------------------------------------
    def draw_world(self, screen):
        """The islands and bridges (instead of a floor)."""
        self.arena.draw(screen, self.pale, self.timer)

    def draw_over(self, screen, player, now):
        """Over the fight, in the world: the copies, the turrets, the weapon, the weapon-shots, Milo, the boss's
        jumps, your last shot, the falling apart."""
        if self.copies:
            self.copies.draw(screen, self.boss)
        if self.turrets:
            self.turrets.draw(screen)
        for x, y, left in self.flashes:
            r = int(self.boss.base_width * (1.6 - 0.6 * left / JUMP_FLASH))
            pygame.draw.circle(screen, (230, 210, 255), (int(x), int(y)), r, max(1, left // 3))
        if self.weapon:
            self.weapon.draw(screen, self.timer)
        for shot in self.disarm_shots:
            shot.draw(screen, self.timer)
        if self.milo:
            self.milo.draw(screen, player, self.weapon.pos if self.weapon else None)
        if self.shot and self.state == "final":
            sx, sy, t0 = self.shot
            k = min(1.0, (now - t0) / SHOT_FLIGHT_MS)
            x, y = sx + (self.boss.x - sx) * k, sy + (self.boss.y - sy) * k
            pygame.draw.circle(screen, SHOT_COLOUR, (int(x), int(y)), 16)
        if self.glitch:
            self.glitch.draw(screen, self.boss)
        if self.state in ("final", "falling_apart"):
            FINALE.draw_form_edge(screen, self.boss, self.timer)
        if self.dying:
            self.dying.draw(screen)

    def draw_checkpoint_mark(self, screen):
        """A light mark on the boss's bar where F4's checkpoint is (the bar's look: Enemy.hp_bar)."""
        marks = self.boss.phase_marks
        if len(marks) < 3:
            return
        w, h = screen.get_size()
        bar_w, bar_h = w // 1.5, h // 30
        x = w // 2 - bar_w // 2 + bar_w * marks[2]
        y = 20 + bar_h
        pygame.draw.polygon(screen, CHECKPOINT_MARK, [(x - 9, y - 16), (x + 9, y - 16), (x, y - 4)])
        pygame.draw.line(screen, CHECKPOINT_MARK, (x, y), (x, y + bar_h), 2)

    def draw_dead(self, screen, font):
        """ "Game Over" and a click to go back to the checkpoint (a life is gone)."""
        w, h = screen.get_size()
        veil = pygame.Surface((w, h), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 120))
        screen.blit(veil, (0, 0))
        text = font.render("Game Over", True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=(w // 2, h // 2 - 40)))
        small = self.font.render(f"Click - back to the checkpoint ({self.lives} {'life' if self.lives == 1 else 'lives'} left)",
                                 True, (230, 220, 255))
        screen.blit(small, small.get_rect(center=(w // 2, h // 2 + 60)))

    @staticmethod
    def draw_bullet_outline(screen, p):
        """F4 (the Pale World): you only see a bullet's outline."""
        pygame.draw.circle(screen, (150, 150, 160), (int(p.x), int(p.y)), max(4, int(p.width)), 1)

    def draw_hud(self, screen):
        if self.shows_boss_bar:
            self.draw_checkpoint_mark(screen)
        self.words.draw(screen)
        w = screen.get_width()
        for i in range(LIVES):                             # the lives, in the top right corner
            colour = (235, 70, 90) if i < self.lives else (70, 60, 80)
            pygame.draw.circle(screen, colour, (w - 22 - i * 30, 22), 10)
        if self.weapon:
            label = self.font.render("Your weapon is gone - find it", True, (235, 220, 255))
            screen.blit(label, label.get_rect(midtop=(w // 2, screen.get_height() - 90)))
        if self.state == "fight" and self.arena.warning and (self.timer // 15) % 2 == 0:
            label = self.font.render(DROP_WARNING, True, (255, 120, 140))
            screen.blit(label, label.get_rect(midtop=(w // 2, 110)))
        self.fade.draw(screen)


def immunity_after_hit(player):
    """How long you can't be hurt after a hit (Magic Dust: longer) - as shooter.take_damage does it."""
    from game.combat.player.shooter import IMM_AFTER_HIT
    return player.trinket_effect.get("imm_frames", [IMM_AFTER_HIT])[0]
