import pygame, math, random, copy
from game.combat.projectile import projectile as prjt

CONTACT_KNOCKBACK = 35         # px the player is pushed away when an enemy touches them
TELEGRAPH_SPEED = 1.3          # a telegraphed (aimed) shot flies this much faster
AIM_LOCK_SHARE = 0.35          # the last 35% of the aiming time the line doesn't follow you any more
PULSE = [45, 15]               # pulsing ring: frames flying out, frames flying back ("3 steps forward, 1 back")
POISON_FIRST = 30               # frames from putting poison on to its first hit (then every 60)
PHASE_INVULN = 60               # frames a boss can't be hurt (and doesn't shoot) when it changes phase
FADING = {"line_soldier", "line_beetle", "scrap_beetle"}   # (8.11) the toys a machine makes fewer of late in a phase
SLIDE_GRIP = (0.5, 0.25)       # (10.11) wanderers: speed-up / slow-down share per frame (= the player's COMBAT_GRIP)
MINE_CREEP = 1.2               # px per frame a mine crawls towards the player (the player runs 8)

# ATTACK TYPES (the key in the enemy's attack dict decides what it does):
#   basic, shotgun, spiral, minigun, mine, throw, spawn, death_spiral, death_spawn  (the old ones)
#   split     {"split": {"after": frames, "bullets", "speed", "damage", "width"[, "start", "type", "effects"]}}
#   pulse     {"bullets", "pulse": [out, back]}  a pulsing ring (smooth; [45, 15] = 3 steps forward, 1 back)
#   wall      {"bullets", "spacing": px, "gap": bullets}  a row across the way to you with a hole
#   sprinkler {"streams", "duration": s, "every": frames, "turn": degrees}  spinning streams (stands still meanwhile)
#   line      {"bullets", "every": frames}  a quick row aimed once - looks like a laser
#   wave      {"bullets", "every", "amp": px, "period": frames[, "double": True]}  a wobbling line (double = DNA)
#   throw + "ring": {...children...}  the bomb throws out a full ring where it lands
#   dash      {"dashes", "windup": frames, "distance": px, "dash_frames", "spiral": {bullets, damage, speed, width, range}}
#             ["spiral_each": True - the ring at every stop, not only after the last dash; "spiral_on": [1, 2] - a ring
#              only after these dashes; "show": True - a landing ring while it winds up]
#   death_blast {"radius", "damage", "push": px}  on death: a blast that pushes everyone away, hurts only the player
#   burst     {"bullets", "speed": [min, max], "decay", "min_speed"}  spores in random directions and speeds that
#             slow down (Shroom Mother, like the mushroom in ETG)
#   leap      {"up": frames, "air": frames, "land_damage", "burst": {...}}  flies up off the screen (can't be hit), its
#             shadow grows where it will land (random spot), lands (hurts you if you stand there) and bursts there
#   spawn + "corners": True  the spawned ones stand in random corners; + "guards": True  the spawner can't be hurt
#             while one of them lives (a shield ring is drawn); "amount": [1, 2] = random; "after_death": s - new
#             guards only this long after the last one died; "chase": speed - while shielded it walks at you
#   wave + "bounce": n  the line bounces off the screen edges n times; + "opposite": True  a second one straight back
#   ice_walls {"count", "hits", "life": s, "long", "thick"}  walls of ice rise in random spots: they stop you, the
#             boss and every bullet; your shots break them (hits), or they melt after "life" s (Frost Golem)
#   ground_crack {"speed", "length", "every": px, "bullets": {...}}  a stomp: a crack runs along the ground at you and
#             throws bullets out to both sides every "every" px (Frost Golem; drawn like a zap)
#   spawn + "at": [[fx, fy], ...]  the spawned ones stand at these spots (share of the arena); "replace": True  the
#             old guards are taken away first; "enemy_name" can be a list (a random one each); "belt": True  they come
#             in at the start of a random conveyor belt (Combat places them) (8.11, Assembly Line)
#   spawn + "open_damage": share  when all its guards are broken it is open only until it took this share of its
#             max HP, then sealed (no guards) for "rebuild" s, then new guards; "no_drops": True  they drop nothing
#   vents     {"count", "warn", "pattern": "ring" / "line", "bullets", "every", "speed", "damage", "width", "type"}
#             vents in the bottom edge glow, then shoot a half ring up or a row at you (so you can't hide down there)
#   "kind": "spawn"  any attack can say which type it is - so a boss can have two spawns ("spawn" + "bombers")
#   spawn + "hard_only": [names]  those kinds only in hard mode (the boss's)
#   edge_rain {"warn": frames, "sides": ["left", "right", ...], "spacing": px, "gaps": n, "gap": px, "speed", "damage", "width", "type"}
#             rows of bullets come in from the arena's sides; `gaps` holes (gap px wide) in each side's row are the
#             only safe lanes (Night Bloom); "side_gaps": {"bottom": 4} = more holes on that side
#   decoys    {"copies": n, "copy": enemy name, "keep_away": px}  it vanishes and comes back somewhere else, with n
#             copies (the copies pop into a small ring when hit; the real one casts a shadow) (Night Bloom)
#   throw + "light": px  the bomb lights a circle round it while it flies / lies (dark arenas)
#   fuse      {"cooldown": s}  after this long the enemy blows up by itself (its death attack goes off) - bomb crates
#   nozzles   {"lanes": n, "warn": frames, "rows", "bullets", "every": frames, "speed", "damage", "width", "type"}
#             nozzles in the side walls light up for `warn` frames, then shoot a stream along n random belts
# Any attack can also have "repeat": [times, gap in s] - a series (the cooldown starts after the last one).
# ARENA (bosses, per phase: "arena": {...}): "ice": True = slippery floor; "blizzard": [on, every] frames = a snowstorm
#   (you only see a circle around you) for `on` frames out of every `every`; "belts": {"lanes": [[top, bottom, dir],
#   ...] (share of the height; dir 1 = to the right), "speed": px per frame, "reverse": [every, warn] frames} =
#   conveyor belts across the arena that carry you, the small enemies and the bullets (8.11). Combat reads enemy.arena.
#
# BOSS PHASES (7.11): EnemyDB.boss_info[name] = {"name": shown over the big HP bar, "phases": [{"at": 0.6, ...}]}.
# When the HP drops to "at" x max HP the boss gets that phase: new "attacks" (replace the old ones; "hard": more
# attacks added only in hard mode), and optionally
# "speed", "movement", "color", "contact". Meanwhile PHASE_INVULN frames: it blinks, takes no damage, doesn't shoot;
# Combat clears every enemy bullet, flashes the screen and plays a sound (phase_event).



class Enemy:
    def __init__(self, x, y, hp, width, type, speed, contact_dmg, money, defence, species, movement_type, attacks, sfx, bullet_type_info):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = self.hp
        self.width = width
        self.type = type
        self.bullet_type_info = bullet_type_info
        self.species = species

        self.speed = speed
        self.og_speed = speed
        self.movement_type = movement_type

        self.death_attacks = [1,1]

        self.movement_timer = 0    # for jump movement
        self.random_dx = 0            
        self.random_dy = 0            
        self.zigzag_phase = 0 

        self.is_jumping = False
        self.jump_dx = 0
        self.jump_dy = 0

        self.damage = 1.0
        self.og_damage = self.damage   
        self.contact_dmg = contact_dmg

        self.defence = defence
        self.og_defence = self.defence

        self.rate_of_fire = 1.0
        self.og_rate_of_fire = self.rate_of_fire

        self.attacks = attacks
        self.money = money
        self.color = (255,255,255)
        self.boss_name = None          # bosses: the name over the big HP bar
        self.phases = []               # bosses: the phases still to come (EnemyDB.boss_info), highest "at" first
        self.phase_marks = []          # where the phase lines are drawn on the HP bar
        self.phase_started = 0         # (8.11) attack_timer when this phase began
        self.owner = None              # (8.11) the boss that made this one (Assembly Line's machines)
        self.behind_wall = False       # (8.11) a wall stands between it and its target (Combat sets it)
        self.anchored = False          # (8.11) stays where it was put (Assembly Line's core and machines)
        self.anchor = None             # where that is (Combat notes it on the first frame)
        self.casts_shadow = False      # (8.11) Night Bloom: the real one has a shadow, its copies don't
        self.copies = []               # (8.11) its copies made by "split"
        self.invuln = 0                # frames left of a phase change (no damage, no shots, blinking)
        self.airborne = False          # a "leap": up in the air (off the screen, can't be hit)
        self.leap_shadow = None        # (x, y, 0..1) where it will land
        self.guards = []               # enemies that shield this one while alive ("guards" spawn)
        self.arena = {}                # boss: what the arena does in this phase (see the top)
        self.new_walls = []            # ice walls made this frame (Combat takes them)
        self.new_cracks = []           # ground cracks started this frame (Combat runs them)
        self.new_nozzles = []          # (8.11) wall nozzles started this frame (Combat runs them)
        self.open_left = None          # (8.11) guards with "open_damage": damage it can still take before it seals
        self.sealed_at = None          # (8.11) attack_timer when it sealed again (no guards yet - they come back soon)
        self.shape = None              # (8.11) "square" = drawn as a box (machines, crates, turrets)
        self.guards_gone_at = None     # attack_timer when the last guard died
        self.guard_chase = 0           # speed while shielded (walks at the player, hurts by touch)
        self.phase_event = False       # Combat: a phase just started (clear the bullets, flash, sound)
        self.effects = {}   
        self.poison_age = None          # frames since the poison was put on (None = not poisoned)
        self.attack_timer = 0 

        self.sfx = sfx
        self.name = ""   # database key, set by EnemyDB (used for item drops)
        self.aiming = None   # the attack being aimed right now (fast shots with a "telegraph" line)
        self.glow = 0        # frames of glowing before a dash (Firefly Queen)
        self.screen_size = None   # set in move() - a dash stays on the screen

    def draw(self, screen):
        if self.aiming:                                   # the aiming line of a fast shot
            a = self.aiming.get("aim_angle", 0)
            locked = self.aiming.get("aim_left", 0) <= self.aiming["telegraph"] * AIM_LOCK_SHARE
            end = (self.x + math.cos(a) * 2500, self.y + math.sin(a) * 2500)
            for wall in getattr(self, "_walls", []):           # (8.11) the line stops at a wall (so does the shot)
                hit = wall["rect"].clipline((self.x, self.y), end)
                if hit:
                    end = hit[0]
            pygame.draw.line(screen, (255, 40, 40) if locked else (255, 130, 130), (self.x, self.y), end, 3 if locked else 1)
        if getattr(self, "dash_preview", None):                   # a boss about to jump: where it lands
            a, dist, k = self.dash_preview
            lx, ly = self.x + math.cos(a) * dist, self.y + math.sin(a) * dist
            if self.screen_size:
                lx = min(self.screen_size[0] - self.width, max(self.width, lx))
                ly = min(self.screen_size[1] - self.width, max(self.width, ly))
            pygame.draw.circle(screen, (200, 60, 60), (lx, ly), self.width, 2 + int(k * 4))
        if self.leap_shadow:                                      # where a leaping boss will come down
            sx, sy, k = self.leap_shadow
            r = self.width * (0.35 + 0.65 * k)
            shade = pygame.Surface((int(r * 2), int(r * 1.2)), pygame.SRCALPHA)
            pygame.draw.ellipse(shade, (0, 0, 0, int(60 + 90 * k)), shade.get_rect())
            screen.blit(shade, shade.get_rect(center=(sx, sy + self.width * 0.3)))
        if self.shielded():                                       # shielded by its guards
            pygame.draw.circle(screen, (120, 200, 255), (self.x, self.y), self.width + 10, 4)
        if self.casts_shadow:                                     # (8.11) the tell of the real Night Bloom
            shade = pygame.Rect(0, 0, int(self.width * 1.8), int(self.width * 0.6))
            shade.center = (self.x, self.y + self.width * 0.95)
            pygame.draw.ellipse(screen, (12, 22, 16), shade)
        if not (self.invuln and (self.invuln // 5) % 2):          # blinking while changing phase
            if self.shape == "square":                            # (8.11) machines, crates, turrets
                box = pygame.Rect(0, 0, self.width * 2, self.width * 2)
                box.center = (self.x, self.y)
                pygame.draw.rect(screen, self.color, box, 0, 6)
                pygame.draw.rect(screen, (40, 40, 48), box, 4, 6)
            else:
                pygame.draw.circle(screen, self.color, (self.x, self.y), self.width)
        if not getattr(self, "bar_on_hud", False):              # (11.11) the Void: Combat draws it on the screen
            self.hp_bar(screen)
        die = self.handle_effects()[1]  
        self.draw_effects(screen)
        return die

    def handle_effects(self, check = False):
        effect_del = []
        text = []
        if self.effects:
            for effect_name, effect in self.effects.items():
                if effect_name == "slow":
                    self.speed = self.og_speed * (1-effect[1])
                elif effect_name == "poison":
                    # (7.11) the first poison hit comes POISON_FIRST frames after it is put on, then every 60
                    # (hit......hit......end); putting it on again only refreshes it, the rhythm goes on
                    if not check:
                        self.poison_age = 0 if self.poison_age is None else self.poison_age + 1
                        if self.poison_age % 60 == POISON_FIRST:
                            self.sfx.play("posion_effect")
                            self.hp -= effect[1]
                elif effect_name == "weakness":
                    self.damage = self.og_damage * (1-effect[1])
                elif effect_name == "glued":
                    self.rate_of_fire = self.og_rate_of_fire * (1-effect[1])
                elif effect_name == "burn" and effect[0] % 15 == 0:
                    self.sfx.play("burn_effect")
                    self.hp -= effect[1]
                elif effect_name == "acid":
                    self.defence = self.og_defence * (1-effect[1])
                elif effect_name == "confusion":
                    text.append("confusion")
                elif effect_name == "binded":
                    text.append("binded")
                

                if not check:
                    if effect[0] != "inf":
                        effect[0] -= 1

                if effect[0] != "inf" and effect[0] <= 0:
                    effect_del.append(effect_name)

            for name in effect_del:
                if name == "poison":
                    self.poison_age = None
                if name == "slow":
                    self.speed = self.og_speed
                elif name == "weakness":
                    self.damage = self.og_damage
                elif name == "glued":
                    self.rate_of_fire = self.og_rate_of_fire
                elif name == "acid":
                    self.defence = self.og_defence
                self.effects.pop(name)
        return text, self.hp <= 0
                

    def shielded(self):
        """Its guards still stand - or (open_damage guards) it sealed itself again and waits for new ones."""
        return any(g.hp > 0 and not getattr(g, "remove_me", False) for g in self.guards) or self.sealed_at is not None

    def take_damage(self, amount, effects = {}):
        if self.invuln > 0 or self.airborne or self.shielded():
            return [True]                     # changing phase / in the air / shielded: the bullet does nothing
        
             

        if effects:
            for effect_name, effect in effects.items():

                if effect_name in ("slow","poison","weakness","glued", "burn", "acid"):
                    self.effects[effect_name] = effect
                elif effect_name in ("binded","confusion"):        
                    rnd = random.random()
                    if rnd < effect[1] *(0.1 if self.type == "boss" else 1):
                        self.effects[effect_name] = effect
                elif effect_name == "dmg_to_undead" and self.species == "undead":
                    amount *= (1+effect[0])
                elif effect_name == "glued_vuln" and "glued" in self.effects:
                    amount *= (1+effect[0])                 # Tape
                elif effect_name == "slow_vuln" and "slow" in self.effects:
                    amount *= (1+effect[0])                 # Ice Mix
                elif effect_name == "bullseye" and self.hp <= self.max_hp*effect[0]:
                    self.hp = 0

        dealt = amount * 100 / (100 + max(0, self.defence))       # % defence: def 100 = half damage
        self.drop_copies()                                        # (8.11) found the real one: its copies vanish
        if self.open_left is not None:                            # (8.11) open only for so much damage, then sealed
            dealt = min(dealt, self.open_left)
            self.open_left -= dealt
            if self.open_left <= 0:
                self.open_left, self.sealed_at = None, self.attack_timer
        self.hp -= dealt
        if self.phases and self.hp < self.max_hp * self.phases[0]["at"]:
            self.hp = self.max_hp * self.phases[0]["at"]              # a phase is never skipped by one big hit
        if self.hp < 0:
                    self.hp = 0 
        if effects:
            for effect_name, effect in effects.items():
                if effect_name in ("zap","explosion","pierce","knockback"):
                    return [effect_name, effect]
            
        return [True]


    def move(self, target_x, target_y, screen):
        self.screen_size = screen.get_size()
        if self.guard_chase and self.shielded():
            d = math.hypot(target_x - self.x, target_y - self.y)       # shielded: walks straight at you
            if d > 1:
                self.x += (target_x - self.x) / d * self.guard_chase
                self.y += (target_y - self.y) / d * self.guard_chase
            return
        if self.aiming or self.airborne:
            return                                        # stands still while aiming a fast shot

        confusion = "confusion" in self.handle_effects(True)[0]
        direction_modifier = -1 if confusion else 1
        self.movement_timer += 1
        dx, dy = 0, 0

        if "to_player" in self.movement_type or "away_player" in self.movement_type:
            dx = target_x - self.x
            dy = target_y - self.y
            
            if "away_player" in self.movement_type:
                dx = -dx
                dy = -dy
        elif "random" in self.movement_type:
            if self.movement_timer % 60 == 0 or (self.random_dx == 0 and self.random_dy == 0):
                angle = random.uniform(0, 2 * math.pi)
                self.random_dx = math.cos(angle)
                self.random_dy = math.sin(angle)
            dx = self.random_dx
            dy = self.random_dy

        length = math.sqrt(dx*dx + dy*dy)
        if length != 0:
            dx /= length
            dy /= length
        current_speed = self.speed

        if "distance" in self.movement_type:
            keep_distance = 200 if "to_player" in self.movement_type else 900
            if ((length < keep_distance and "to_player" in self.movement_type) or (length > keep_distance and "away_player" in self.movement_type)) and "random" not in self.movement_type:
                current_speed = 0 

        if "jump" in self.movement_type:
            
            cycle_duration = 100  
            rest_duration = 60   
            jump_duration = cycle_duration - rest_duration  
            cycle = self.movement_timer % cycle_duration
            
            if cycle < rest_duration:
                current_speed = 0
            elif cycle == rest_duration:
                self.jump_dx = dx
                self.jump_dy = dy
            else:
                jump_progress = (cycle - rest_duration) / jump_duration
                smooth_modifier = math.sin(jump_progress * math.pi)
                max_jump_multiplier = 3.5
                current_speed = self.speed * smooth_modifier * max_jump_multiplier

        if self.is_stopped_by_attack():
            current_speed = 0

        if "zigzag" in self.movement_type and length != 0:
            self.zigzag_phase += 0.08

            perpendicular_x = -dy
            perpendicular_y = dx
            
            zigzag_strength = 1.25  
            dx += perpendicular_x * math.sin(self.zigzag_phase) * zigzag_strength
            dy += perpendicular_y * math.sin(self.zigzag_phase) * zigzag_strength
            
            new_len = math.sqrt(dx*dx + dy*dy)
            if new_len != 0:
                dx /= new_len
                dy /= new_len

        step_x = (dx if not "jump" in self.movement_type else self.jump_dx) * current_speed * direction_modifier
        step_y = (dy if not "jump" in self.movement_type else self.jump_dy) * current_speed * direction_modifier
        if "random" in self.movement_type and "jump" not in self.movement_type:
            step_x, step_y = self.slide(step_x, step_y)       # (10.11) wanderers slide like the player
        self.x += step_x
        self.y += step_y

        if self.x < 0 + self.width:
            self.x = 0 + self.width
        if self.x > screen.get_width() - self.width:
            self.x = screen.get_width() - self.width
        if self.y < 0 + self.width:
            self.y = 0 + self.width
        if self.y > screen.get_height() - self.width:
            self.y = screen.get_height() - self.width

    def slide(self, want_x, want_y):
        """Eases the step towards the wanted one (speeding up / slowing down like the player in a fight)."""
        grip = SLIDE_GRIP[0] if (want_x or want_y) else SLIDE_GRIP[1]
        self.vel_x = getattr(self, "vel_x", 0.0) + (want_x - getattr(self, "vel_x", 0.0)) * grip
        self.vel_y = getattr(self, "vel_y", 0.0) + (want_y - getattr(self, "vel_y", 0.0)) * grip
        return self.vel_x, self.vel_y

    def is_stopped_by_attack(self):
        # true while any attack is in its stop_move wait (before or after the shot), in a series, or spinning
        return any(info.get("stop_phase") or info.get("rep_left") or (info.get("is_bursting") and ("streams" in info or "dashes" in info))
                   for info in self.attacks.values())

    def attack_ready(self, attack_info, hard_mode, binded):
        """Returns True on the frame the attack should fire.

        stop_move: [frames BEFORE the shot, frames AFTER the shot] - the enemy stands still then.
        Order: cooldown (enemy moves) -> stand `before` frames -> SHOOT -> stand `after` frames -> cooldown starts.
        So the waiting time does NOT count towards the cooldown."""
        if attack_info.get("is_bursting"):
            return True
        cooldown_done = self.attack_timer - attack_info["last_used"] >= (attack_info["cooldown"] *(0.9 if hard_mode else 1.0)) * 60

        stop = attack_info.get("stop_move")
        if not stop:
            return cooldown_done

        phase = attack_info.get("stop_phase")
        if phase == "after":
            if not binded:
                attack_info["stop_timer"] -= 1
            if attack_info["stop_timer"] <= 0:
                attack_info["stop_phase"] = None
                attack_info["last_used"] = self.attack_timer   # cooldown starts only now
            return False

        if phase is None:
            if not cooldown_done:
                return False
            attack_info["stop_phase"] = "before"
            attack_info["stop_timer"] = stop[0]

        # phase "before"
        if not binded:
            attack_info["stop_timer"] -= 1
        if attack_info["stop_timer"] <= 0:
            attack_info["stop_phase"] = "after"
            attack_info["stop_timer"] = stop[1]
            return True
        return False

    def attack(self, timer, player = None, hard_mode = False, enemy_db = None, aim = None):
        # aim = what the shots go for (the player, or the Mascot Plush decoy while it lives); touching hurts only the player
        aim = aim or player

        binded = "binded" in self.handle_effects(True)[0]

        projectiles = []
        enemies = []
        self.check_phase()
        if self.invuln > 0:
            self.invuln -= 1
            return projectiles, enemies                    # changing phase: no shots for a moment
        if not binded:
            self.attack_timer +=1*self.rate_of_fire
        
        self._player = player
        for attack_name, attack_info in self.attacks.items():
            if self.airborne and attack_name != "leap":
                continue                                  # up in the air: only the leap goes on
            if attack_name == "death_spiral" and self.hp <= 0 and self.death_attacks[0] == 1:
                self.death_attacks[0] = 0
                bullets = attack_info.get("bullets", 12)
                for i in range(bullets):                          # a full ring (7.11: no gap - only "pulse" has one)

                    rad = math.radians(i * 360 / bullets)
                    proj_x = self.x + math.cos(rad) * self.width
                    proj_y = self.y + math.sin(rad) * self.width

                    target_x = self.x + math.cos(rad) * 1000
                    target_y = self.y + math.sin(rad) * 1000

                    projectile = prjt(proj_x, proj_y, target_x, target_y, self.attacks["death_spiral"]["speed"],
                                        self.attacks["death_spiral"]["damage"], "enemy",
                                        self.attacks["death_spiral"]["width"], self.attacks["death_spiral"]["range"],
                                        self.bullet_type_info, attack_info["type"], effects=attack_info["effects"])
                    projectiles.append(projectile)
            if attack_name == "death_spawn" and self.hp <= 0 and self.death_attacks[1] == 1:
                self.death_attacks[1] = 0
                for i in range(attack_info["amount"]):
                    enemy = enemy_db.get_enemy(attack_info["enemy_name"])
                    enemy.x = self.x + (-1)**i*20*i
                    enemy.y = self.y + (-1)**i*20*i
                    enemies.append(enemy)
            elif "death" not in attack_name and player:
                if attack_info.get("rep_left"):
                    # SERIES ("repeat": [times, gap in s]): the next shot of the series once its time comes
                    if self.attack_timer >= attack_info["rep_next"]:
                        new, spawned, done = self.fire(attack_name, attack_info, aim, enemy_db)
                        projectiles += new
                        enemies += spawned
                        if done:
                            attack_info["rep_left"] -= 1
                            attack_info["rep_next"] = self.attack_timer + attack_info["repeat"][1] * 60
                            attack_info["last_used"] = self.attack_timer       # the cooldown starts after the LAST one
                    continue
                if self.attack_ready(attack_info, hard_mode, binded):
                    new, spawned, done = self.fire(attack_name, attack_info, aim, enemy_db)
                    projectiles += new
                    enemies += spawned
                    if done and attack_info.get("repeat", [1])[0] > 1:
                        attack_info["rep_left"] = attack_info["repeat"][0] - 1
                        attack_info["rep_next"] = self.attack_timer + attack_info["repeat"][1] * 60

        if player and player.width + self.width > math.sqrt((self.x - player.x) ** 2 + (self.y - player.y) ** 2) and timer % 10 == 0 and "dmgless_contact" not in player.trinket_effect:
            hit = player.take_damage(self.contact_dmg, {})      # (Cotton Candy's speed boost: shooter.take_damage)
            if hit:
                self.sfx.play("hit")
                # touching = one hit (then the player's immunity frames) and a push away from the enemy
                d = math.dist((self.x, self.y), (player.x, player.y)) or 1
                player.x += (player.x - self.x) / d * CONTACT_KNOCKBACK
                player.y += (player.y - self.y) / d * CONTACT_KNOCKBACK
                
        return projectiles, enemies


    # --- one attack going off ------------------------------------------------------------------------------
    def shot(self, angle, info, x=None, y=None, speed=None, effects=None):
        """One bullet of an attack, flying at `angle` (radians) from the enemy's edge (or from x, y)."""
        if x is None:
            x, y = self.x + math.cos(angle) * self.width, self.y + math.sin(angle) * self.width
        return prjt(x, y, x + math.cos(angle) * 1000, y + math.sin(angle) * 1000, speed or info["speed"],
                    self.damage * info["damage"], "enemy", info["width"], info["range"],
                    self.bullet_type_info, info["type"], effects=info.get("effects", {}) if effects is None else effects)

    def children(self, info, key):
        """The spec of the smaller bullets a bullet bursts into (split / a thrown bomb's ring)."""
        c = info[key]
        effects = {k: v for k, v in info.get("effects", {}).items() if k != "homing"} if c.get("effects") is None else c["effects"]
        return {"bullets": c["bullets"], "speed": c["speed"], "damage": self.damage * c["damage"], "width": c["width"],
                "range": c.get("range", info.get("range", 3000)), "type": c.get("type", info["type"]),
                "effects": effects, "start": c.get("start", 0)}

    def spawnable(self, info):
        """The kinds a spawn may make now: "hard_only" ones only when its boss (owner) is in hard mode."""
        kinds = info["enemy_name"] if isinstance(info["enemy_name"], (list, tuple)) else [info["enemy_name"]]
        boss = self.owner or self
        if getattr(boss, "hard", False) or not info.get("hard_only"):
            return kinds
        return [k for k in kinds if k not in info["hard_only"]]

    def fire(self, name, info, aim, enemy_db):
        """Fires one attack. Returns (bullets, spawned enemies, done) - done = False while it is still going
        (aiming a fast shot, or a burst / spin / line that lasts a few frames)."""
        projectiles, enemies = [], []
        aim_angle = math.atan2(aim.y - self.y, aim.x - self.x)
        name = info.get("kind", name)                      # (8.11) e.g. a 2nd spawn: "bombers": {"kind": "spawn"}

        if name == "basic" and info.get("telegraph"):
            # FAST SHOT (6.11): a red aiming line first (follows you, then locks), then a faster bullet
            left = info.get("aim_left")
            if left is None and self.behind_wall:
                return [], [], True                        # (8.11) no aiming at a wall: it goes round first
            if left is None:
                left = info["telegraph"]
            left -= 1
            if left > info["telegraph"] * AIM_LOCK_SHARE:
                info["aim_angle"] = aim_angle
            if left > 0:
                info["aim_left"] = left
                self.aiming = info
                return [], [], False
            info["aim_left"] = None
            self.aiming = None
            projectiles.append(self.shot(info["aim_angle"], info, self.x, self.y, info["speed"] * TELEGRAPH_SPEED))
            info["last_used"] = self.attack_timer

        elif name == "basic":
            projectiles.append(prjt(self.x, self.y, aim.x, aim.y, info["speed"],
                                    self.damage*info["damage"], "enemy",
                                    info["width"], info["range"],
                                    self.bullet_type_info, info["type"], effects=info["effects"]))
            info["last_used"] = self.attack_timer

        elif name == "split":
            # SPLIT (7.11): one bullet (may home a bit) that bursts into a ring of smaller ones after "after" frames
            p = self.shot(aim_angle, info)
            p.motion = {"kind": "split", "after": info["split"]["after"], "children": self.children(info, "split")}
            projectiles.append(p)
            info["last_used"] = self.attack_timer

        elif name == "pulse":
            # PULSING RING (7.11): a full ring that goes "3 steps forward, 1 back" (smoothly)
            n = info["bullets"]
            start = random.uniform(0, math.tau)
            for i in range(n):                                 # a full ring (no gap - 7.11)
                p = self.shot(start + i * math.tau / n, info)
                p.motion = {"kind": "pulse", "pulse": info.get("pulse", PULSE)}
                projectiles.append(p)
            info["last_used"] = self.attack_timer

        elif name == "wall":
            # WALL (7.11): a row of bullets across the way to the target, with one gap to step into
            n, spacing, gap = info["bullets"], info["spacing"], info.get("gap", 3)
            hole = random.randint(1, max(1, n - gap - 1))
            px, py = -math.sin(aim_angle), math.cos(aim_angle)
            bx, by = self.x + math.cos(aim_angle) * self.width, self.y + math.sin(aim_angle) * self.width
            for i in range(n):
                if hole <= i < hole + gap:
                    continue
                off = (i - (n - 1) / 2) * spacing
                projectiles.append(self.shot(aim_angle, info, bx + px * off, by + py * off))
            info["last_used"] = self.attack_timer

        elif name in ("sprinkler", "line", "wave"):
            # attacks that last a few frames: SPRINKLER (spinning streams), LINE (a quick row of bullets that looks
            # like a laser, aimed once), WAVE (like a line, but the bullets wobble - "double": two mirrored = DNA)
            if not info.get("is_bursting"):
                info["is_bursting"] = True
                info["burst_t"] = 0
                info["burst_angle"] = random.uniform(0, math.tau) if name == "sprinkler" else aim_angle
                info["burst_dir"] = random.choice((-1, 1))
            t = info["burst_t"]
            if t % info["every"] == 0:
                a = info["burst_angle"]
                if name == "sprinkler":
                    streams = info["streams"]
                    projectiles += [self.shot(a + k * math.tau / streams, info) for k in range(streams)]
                    info["burst_angle"] += math.radians(info["turn"]) * info["burst_dir"]
                elif name == "line":
                    projectiles.append(self.shot(a, info))
                else:
                    for a, sign in [(d, s) for d in ((a, a + math.pi) if info.get("opposite") else (a,))
                                    for s in ((1, -1) if info.get("double") else (1,))]:
                        p = self.shot(a, info)
                        p.motion = {"kind": "wave", "amp": info["amp"], "period": info["period"], "sign": sign}
                        if info.get("bounce"):
                            p.motion.update(bounce=info["bounce"], bounds=self.screen_size or (1920, 1080))
                        projectiles.append(p)
            info["burst_t"] = t + 1
            length = info["duration"] * 60 if name == "sprinkler" else info["every"] * (info["bullets"] - 1) + 1
            if info["burst_t"] < length:
                return projectiles, enemies, False
            info["is_bursting"] = False
            info["last_used"] = self.attack_timer

        elif name == "dash":
            # SUN DASH (7.11, Firefly Queen - like the sun in ETG): "dashes" times: glow and aim ("windup" frames),
            # then a straight dash ("distance" px in "dash_frames"); after the last one a full "spiral" ring
            if not info.get("is_bursting"):
                info["is_bursting"] = True
                info["dash_left"] = info["dashes"]
                info["dash_t"] = 0
            t = info["dash_t"]
            info["dash_t"] = t + 1
            if t < info["windup"]:
                self.glow = info["windup"] - t                   # standing and glowing
                info["dash_angle"] = aim_angle
                if info.get("show"):                             # (bosses) where it will land: a ring on the floor
                    self.dash_preview = (aim_angle, info["distance"], t / info["windup"])
                return projectiles, enemies, False
            self.dash_preview = None
            if t < info["windup"] + info["dash_frames"]:
                self.glow = 0
                step = info["distance"] / info["dash_frames"]
                self.x += math.cos(info["dash_angle"]) * step
                self.y += math.sin(info["dash_angle"]) * step
                if self.screen_size:
                    self.x = min(self.screen_size[0] - self.width, max(self.width, self.x))
                    self.y = min(self.screen_size[1] - self.width, max(self.width, self.y))
                return projectiles, enemies, False
            info["dash_left"] -= 1
            info["dash_t"] = 0
            sp = info["spiral"]
            stop = info["dashes"] - info["dash_left"]          # which stop this is (1, 2, ...)
            if "spiral_on" in info:
                ring = stop in info["spiral_on"]                # a ring only after these dashes
            else:
                ring = info["dash_left"] == 0 or info.get("spiral_each")
            if ring:
                start = random.uniform(0, math.tau)
                for i in range(sp["bullets"]):
                    projectiles.append(self.shot(start + i * math.tau / sp["bullets"], {**sp, "type": sp.get("type", info["type"])}))
            if info["dash_left"] > 0:
                return projectiles, enemies, False
            info["is_bursting"] = False
            info["last_used"] = self.attack_timer

        elif name == "minigun":
            if not info["is_bursting"]:
                info["is_bursting"] = True
                info["burst_count"] = 0
                info["last_shot"] = self.attack_timer
                info["last_used"] = self.attack_timer
            if self.attack_timer - info["last_shot"] >= info["burst_delay"]*60:
                info["last_shot"] = self.attack_timer
                info["burst_count"] += 1
                spread = math.radians(info.get("spread", 0))   # degrees
                projectiles.append(self.shot(aim_angle + random.uniform(-spread, spread), info))
                if info["burst_count"] >= info["burst_max"]:
                    info["is_bursting"] = False
                    info["burst_count"] = 0
                    info["last_used"] = self.attack_timer
                    return projectiles, enemies, True
            return projectiles, enemies, False

        elif name == "spiral":
            rnd = random.randint(-5,5)
            angles = list(range(0+rnd*20, 360+rnd*20, 360//info["bullets"]))
            for angle in angles:                           # a full ring (7.11: no gap - only "pulse" has one)
                projectiles.append(self.shot(math.radians(angle), info))
            info["last_used"] = self.attack_timer

        elif name == "spawn":
            if info.get("guards"):
                if any(g.hp > 0 and not getattr(g, "remove_me", False) for g in self.guards):
                    info["last_used"] = self.attack_timer      # the old guards still stand: no new ones yet
                    return projectiles, enemies, True
                if self.guards and info.get("open_damage"):
                    # (8.11, Assembly Line) all broken: open for open_damage x max HP of damage, then sealed again
                    # (shielded, no guards) for "rebuild" s, then new guards
                    if self.sealed_at is not None:
                        if self.attack_timer - self.sealed_at < info.get("rebuild", 0) * 60:
                            return projectiles, enemies, True
                        self.sealed_at = None
                    else:
                        if self.open_left is None:
                            self.open_left = info["open_damage"] * self.max_hp
                            # (8.11) don't seal a hair before the next phase: if what would be left of the phase
                            # after this window is small, stay open until the phase changes
                            floor = self.max_hp * self.phases[0]["at"] if self.phases else 0
                            rest = self.hp - floor
                            if rest - self.open_left < self.open_left * 0.5:
                                self.open_left = rest + 1
                        return projectiles, enemies, True
                elif self.guards:                              # they all died: wait "after_death" s from then
                    if self.guards_gone_at is None:
                        self.guards_gone_at = self.attack_timer
                    if self.attack_timer - self.guards_gone_at < info.get("after_death", 0) * 60:
                        return projectiles, enemies, True
                self.guards_gone_at = None
                self.guard_chase = info.get("chase", 0)
            if info.get("replace"):
                for g in self.guards + getattr(self, "old_guards", []):   # (8.11) the old ones are taken away
                    g.remove_me = True
                self.old_guards = []
            corners = None
            if info.get("corners") and self.screen_size:
                w, h = self.screen_size
                m = info.get("margin", 130)
                corners = random.sample([(m, m + 60), (w - m, m + 60), (m, h - m), (w - m, h - m)], 4)
            amount = info["amount"]
            if isinstance(amount, (list, tuple)):
                amount = random.randint(*amount)               # e.g. [1, 2]: one or two
            for i in range(amount):
                kind = random.choice(self.spawnable(info))
                if info.get("fade") and self.owner and kind in FADING:
                    # (8.11) the boss's phase has lasted fade[0] s: fewer small toys (up to fade[2] skipped after
                    # another fade[1] s) - the fight can't drown you in them
                    age = (self.owner.attack_timer - self.owner.phase_started) / 60 - info["fade"][0]
                    if age > 0 and random.random() < min(info["fade"][2], age / info["fade"][1]):
                        continue
                enemy = enemy_db.get_enemy(kind)
                enemy.owner = self
                if info.get("at") and self.screen_size:
                    spot = info["at"][i % len(info["at"])]
                    enemy.x, enemy.y = spot[0] * self.screen_size[0], spot[1] * self.screen_size[1]
                elif info.get("belt"):
                    enemy.x, enemy.y = self.x, self.y
                    enemy.belt_entry = True                    # Combat puts it at the start of a belt
                elif corners:
                    enemy.x, enemy.y = corners[i % 4]
                else:
                    enemy.x = self.x + (-1)**i*20*i
                    enemy.y = self.y + (-1)**i*self.width
                if info.get("color"):
                    enemy.color = tuple(info["color"])
                if info.get("no_drops"):
                    enemy.no_drops = True                      # (8.11) a boss's helpers drop nothing
                enemies.append(enemy)
            if info.get("guards"):
                self.guards = list(enemies)
            info["last_used"] = self.attack_timer

        elif name == "ice_walls":
            # ICE WALLS (7.11, Frost Golem): a stomp - walls of ice rise in random spots (not on you, not on it)
            w, h = self.screen_size or (1920, 1080)
            lng, thick = info.get("long", 200), info.get("thick", 44)
            for _ in range(info["count"]):
                for _try in range(30):
                    ww, hh = (lng, thick) if random.random() < 0.5 else (thick, lng)
                    r = pygame.Rect(random.randint(80, w - 80 - ww), random.randint(120, h - 80 - hh), ww, hh)
                    p = getattr(self, "_player", None)
                    near_p = p is not None and r.inflate(p.width * 4, p.width * 4).collidepoint(p.x, p.y)
                    others = self.new_walls + list(getattr(self, "_walls", []))     # (8.11) also the walls still standing
                    apart = not any(r.inflate(60, 60).colliderect(o["rect"]) for o in others)
                    if apart and not near_p and not r.inflate(self.width * 2, self.width * 2).collidepoint(self.x, self.y):
                        self.new_walls.append({"rect": r, "hits": info["hits"], "max": info["hits"], "life": int(info["life"] * 60)})
                        break
            info["last_used"] = self.attack_timer

        elif name == "edge_rain":
            # (8.11) the rows wait at the walls for "warn" frames (Combat shows where they'll come from)
            self.new_nozzles.append({"rain": True, "warn": info.get("warn", 0), "bullets": self.edge_rain(info)})
            info["last_used"] = self.attack_timer

        elif name == "decoys":
            enemies += self.split(info, aim, enemy_db)
            info["last_used"] = self.attack_timer

        elif name == "fuse":
            # (8.11) a bomb crate: time's up - it blows (its death attack goes off when Combat sees hp <= 0)
            self.hp = 0
            info["last_used"] = self.attack_timer

        elif name == "vents":
            # (8.11, Assembly Line) vents in the floor at the bottom glow, then shoot (half ring up / a row at you)
            self.new_nozzles.append({k: v for k, v in info.items() if k not in ("cooldown", "last_used")}
                                    | {"damage": self.damage * info["damage"], "vent": True})
            info["last_used"] = self.attack_timer

        elif name == "nozzles":
            # (8.11, Assembly Line) wall nozzles light up, then shoot along random belts (Combat runs them)
            self.new_nozzles.append({k: v for k, v in info.items() if k not in ("cooldown", "last_used")}
                                    | {"damage": self.damage * info["damage"]})
            info["last_used"] = self.attack_timer

        elif name == "ground_crack":
            # GROUND CRACK (8.11, Frost Golem): a stomp - a crack runs from it towards you, bullets out to both sides
            self.new_cracks.append({"x": self.x, "y": self.y, "angle": aim_angle, "speed": info["speed"],
                                    "max": info["length"], "every": info["every"], "start": self.width,
                                    "bullets": {**info["bullets"], "damage": self.damage * info["bullets"]["damage"]}})
            info["last_used"] = self.attack_timer

        elif name == "burst":
            # SPORE BURST (7.11, Shroom Mother): bullets in random directions at random speeds, slowing down
            projectiles += self.burst(info)
            info["last_used"] = self.attack_timer

        elif name == "leap":
            # LEAP (7.11, like the pigeon in ETG): up (can't be hit), off the screen; its shadow grows on a random spot;
            # down there: hurts you if you stand under it, then a spore burst
            if not info.get("is_bursting"):
                info["is_bursting"] = True
                info["leap_t"] = 0
                w, h = self.screen_size or (1920, 1080)
                m = self.width + 80
                info["leap_to"] = (random.uniform(m, w - m), random.uniform(m + 60, h - m))
                info["leap_from"] = (self.x, self.y)
                self.airborne = True
            t = info["leap_t"]
            info["leap_t"] = t + 1
            up, air = info["up"], info["air"]
            if t < up:                                         # going up: rises off the screen
                fx, fy = info["leap_from"]
                self.x, self.y = fx, fy - (t / up) ** 2 * 1400
                return projectiles, enemies, False
            if t < up + air:                                   # in the air: only its shadow
                self.x, self.y = -5000, -5000
                tx, ty = info["leap_to"]
                self.leap_shadow = (tx, ty, (t - up) / air)
                return projectiles, enemies, False
            self.x, self.y = info["leap_to"]                   # down
            self.leap_shadow = None
            self.airborne = False
            p = getattr(self, "_player", None)
            if p is not None and math.dist((p.x, p.y), (self.x, self.y)) < self.width + p.width:
                if p.take_damage(self.damage * info["land_damage"], {}):
                    self.sfx.play("hit")
            if info.get("burst"):
                projectiles += self.burst(info["burst"])
            info["is_bursting"] = False
            info["last_used"] = self.attack_timer

        elif name == "shotgun":
            shots = info["bullets"]
            angle = aim_angle
            angle += math.radians(-info["recoil"]//2)
            angle += math.radians(-(info["recoil"]/shots)/2)
            proj_x = self.x + math.cos(angle) * self.width
            proj_y = self.y + math.sin(angle) * self.width
            for i in range(shots):
                angle += math.radians(info["recoil"]/shots)
                projectiles.append(self.shot(angle, info, proj_x, proj_y))
            info["last_used"] = self.attack_timer

        elif name == "mine":
            p = prjt(self.x, self.y, self.x, self.y, 0,
                     self.damage*info["damage"], "enemy",
                     info["width"], info["exp_time"]*1000,
                     self.bullet_type_info, info["type"], effects={**copy.deepcopy(info.get("effects", {})), "explosion":[info["radius"],1.0]})
            p.motion = {"kind": "creep", "speed": info.get("creep", MINE_CREEP)}     # mines crawl towards you (7.11)
            projectiles.append(p)
            info["last_used"] = self.attack_timer

        elif name == "throw":
            angle = random.uniform(0, math.tau)
            distance = math.sqrt(random.uniform(0, info["recoil"]**2))
            target_x = aim.x + math.cos(angle) * distance
            target_y = aim.y + math.sin(angle) * distance
            p = prjt(self.x, self.y, target_x, target_y, 0,
                     self.damage*info["damage"], "enemy",
                     info["width"], info["fly_time"]*1000,
                     self.bullet_type_info, info["type"], effects={**copy.deepcopy(info.get("effects", {})), "throw":[1], f"{info['exp_type']}explosion":[info["radius"],1.0]})
            if "ring" in info:                       # (7.11) where it lands: a full ring of bullets
                p.motion = {"kind": "land_ring", "children": self.children(info, "ring")}
            if info.get("light"):
                p.light = info["light"]               # (8.11) a lantern: lights the dark round it
            projectiles.append(p)
            info["last_used"] = self.attack_timer

        return projectiles, enemies, True

    # --- boss phases (7.11) --------------------------------------------------------------------------------
    def set_phases(self, info):
        self.boss_name = info.get("name")
        self.arena = dict(info.get("arena", {}))           # phase 1's arena
        self.phases = sorted((dict(p) for p in info.get("phases", [])), key=lambda p: -p["at"])
        self.phase_marks = [p["at"] for p in self.phases]

    def check_phase(self):
        if not self.phases or self.hp <= 0 or self.hp > self.max_hp * self.phases[0]["at"]:
            return
        phase = self.phases.pop(0)
        if "attacks" in phase:
            self.attacks = copy.deepcopy(phase["attacks"])
            if getattr(self, "hard", False):
                self.attacks.update(copy.deepcopy(phase.get("hard", {})))     # hard mode: extra attacks in this phase
            for info in self.attacks.values():
                info["last_used"] = self.attack_timer + info.get("last_used", 0)    # cooldowns start now
        if "speed" in phase:
            self.speed = self.og_speed = phase["speed"]
        if "movement" in phase:
            self.movement_type = phase["movement"]
        if "color" in phase:
            self.color = tuple(phase["color"])
        if "contact" in phase:
            self.contact_dmg = phase["contact"]
        self.arena = dict(phase.get("arena", {}))
        self.aiming = None
        self.glow = 0
        self.dash_preview = None
        for old in self.copies:                             # (8.11) Night Bloom's copies go; it splits again later
            old.remove_me = True
        self.copies = []
        self.old_guards = self.guards                       # ("replace" spawns can still take them away)
        self.guards = []                                    # a new phase: old guards don't shield any more
        self.open_left = self.sealed_at = None
        self.guard_chase = 0
        if self.airborne:                                   # (can't happen mid-air - no damage up there - but safe)
            self.airborne, self.leap_shadow = False, None
        self.invuln = PHASE_INVULN
        self.phase_started = self.attack_timer
        self.phase_event = True

    def edge_rain(self, info):
        """Rows of bullets from the arena's sides, each with a few holes - the only safe lanes."""
        w, h = self.screen_size or (1920, 1080)
        out = []
        for side in info["sides"]:
            across = h if side in ("left", "right") else w
            gaps = info.get("side_gaps", {}).get(side, info["gaps"])     # (8.11) e.g. more holes at the bottom
            holes = [random.uniform(info["gap"], across - info["gap"]) for _ in range(gaps)]
            for pos in range(info["spacing"] // 2, int(across), info["spacing"]):
                if any(abs(pos - hole) < info["gap"] / 2 for hole in holes):
                    continue
                start, angle = self.edge_start(side, pos, w, h)
                out.append(self.shot(angle, info, *start))
        return out

    @staticmethod
    def edge_start(side, pos, w, h):
        """Where a bullet of an edge row starts and which way it flies (into the arena)."""
        return {"left": ((2, pos), 0.0), "right": ((w - 2, pos), math.pi),
                "top": ((pos, 2), math.pi / 2), "bottom": ((pos, h - 2), -math.pi / 2)}[side]

    def drop_copies(self):
        """Night Bloom: once the real one is hit, its copies vanish quietly (no bursts)."""
        for copy_ in self.copies:
            copy_.remove_me = True
        self.copies = []

    def split(self, info, aim, enemy_db):
        """Vanishes and comes back at a random spot away from you, with copies at other spots."""
        for old in self.copies:
            old.remove_me = True
        spots = self.split_spots(info["copies"] + 1, aim, info.get("keep_away", 320))
        self.x, self.y = spots[0]
        self.copies = []
        for spot in spots[1:]:
            copy_ = enemy_db.get_enemy(info["copy"])
            copy_.x, copy_.y = spot
            copy_.color, copy_.width = self.color, self.width
            copy_.owner, copy_.no_drops = self, True
            self.copies.append(copy_)
        return list(self.copies)

    def split_spots(self, n, aim, keep_away):
        w, h = self.screen_size or (1920, 1080)
        spots = []
        for _ in range(200):
            p = (random.uniform(self.width + 60, w - self.width - 60), random.uniform(self.width + 120, h - self.width - 60))
            if math.dist(p, (aim.x, aim.y)) > keep_away and all(math.dist(p, q) > self.width * 3 for q in spots):
                spots.append(p)
                if len(spots) == n:
                    break
        return spots or [(self.x, self.y)]

    def burst(self, info):
        """Spores flying out in random directions at random speeds, each slowing down."""
        out = []
        lo, hi = info["speed"]
        for _ in range(info["bullets"]):
            p = self.shot(random.uniform(0, math.tau), info, speed=random.uniform(lo, hi))
            p.motion = {"kind": "slowdown", "decay": info.get("decay", 0.975), "min": info.get("min_speed", 1.5)}
            out.append(p)
        return out

    def hp_bar(self, screen):
        if self.type == "boss":
            bar_width = screen.get_width() // 1.5
            bar_height = screen.get_height() // 30
            x0 = screen.get_width() // 2 - bar_width // 2
            y0 = 20 if not self.boss_name else 20 + bar_height
            fill_width = int(bar_width * (self.hp/self.max_hp))
            pygame.draw.rect(screen, (255, 0, 0), (x0, y0, bar_width, bar_height))
            pygame.draw.rect(screen, (0, 255, 0), (x0, y0, fill_width, bar_height))
            for at in self.phase_marks:                        # where the next phases start
                mx = x0 + bar_width * at
                pygame.draw.line(screen, (20, 20, 25), (mx, y0 - 3), (mx, y0 + bar_height + 2), 4)
            if self.boss_name:
                if not hasattr(Enemy, "_name_font"):
                    Enemy._name_font = pygame.font.Font(None, int(bar_height * 1.3))
                dark = bool(getattr(self, "arena", {}).get("darkness")) or getattr(self, "light_label", False)   # (8.11) readable over the dark
                label = Enemy._name_font.render(self.boss_name, True, (225, 225, 230) if dark else (30, 30, 35))
                screen.blit(label, label.get_rect(midbottom=(screen.get_width() // 2, y0 - 2)))

    def draw_effects(self, screen):
        EFFECT_COLORS = {
            "slow":      (50, 110, 205),   # blue
            "weakness":  (190, 190, 190),  # light_gray
            "glued":     (255, 210, 40),   # yellow
            "confusion": (170, 80, 255),   # purple
            "binded":    (130, 80, 40),    # brown
            "acid":      (190, 190, 90),   # green/yellow ish
            "poison":    (70, 200, 80),    # green
            "burn":      (220,120,30),     # red
        }

        for i, effect in enumerate(self.effects.keys()):
            if effect in EFFECT_COLORS:
                radius = self.width + (i+1) * 6
                pygame.draw.circle(screen, EFFECT_COLORS[effect], (int(self.x), int(self.y)), radius, 3)
