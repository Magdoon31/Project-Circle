import copy

import pygame, math, random

# ENEMY BULLET PATTERNS (7.11) - a bullet can get a "motion" (set by Enemy.fire, not by the data):
#   {"kind": "pulse", "pulse": [out, back]}  flies outwards `out` frames, back `back` frames, again... (smooth, 3 forward 1 back)
#   {"kind": "wave", "amp": px, "period": frames, "sign": 1/-1}  wobbles sideways (two with opposite signs = DNA)
#   {"kind": "creep", "speed": px}  a mine that slowly crawls towards its target
#   {"kind": "split", "after": frames, "children": spec}  bursts into smaller bullets after a while
#   {"kind": "land_ring", "children": spec}  a thrown bomb that throws out a ring of bullets where it lands
#   {"kind": "slowdown", "decay": 0.97, "min": px}  starts fast, slows down every frame (Shroom Mother's spores)
#     + "return": {"after": frames, "home": () -> (x, y)}  (12.11) then flies back to its owner and is gone there
#   wave + "bounce": n, "bounds": (w, h)  the wobbling line bounces off the screen edges n times
# spec (children) = {"bullets", "speed", "damage" (final), "width", "range", "type", "effects", "start" (degrees)}


OFF_VIEW_MARGIN = 160            # px round the drawn area where a bullet is still drawn (its picture's size)
RETURN_SPEED = (0.25, 11)        # (12.11) a returning spore: px a frame more every frame, at most


def ring_of(x, y, spec, base_angle, bullet_type_info):
    """A full ring of bullets around (x, y); the first one at base_angle + spec["start"] (radians / degrees)."""
    out = []
    n = max(1, spec["bullets"])
    for i in range(n):
        a = base_angle + math.radians(spec.get("start", 0)) + i * math.tau / n
        out.append(projectile(x, y, x + math.cos(a) * 1000, y + math.sin(a) * 1000, spec["speed"], spec["damage"],
                              "enemy", spec["width"], spec["range"], bullet_type_info, spec["type"],
                              effects=copy.deepcopy(spec.get("effects", {}))))
    return out


class projectile:
    def __init__(self, x, y, target_x, target_y, speed, damage, type, width, range, bullet_type_info, bullet_type , effects = None):
        self.x = x
        self.y = y
        self.start_x = self.x
        self.start_y = self.y

        self.speed = speed
        self.og_speed = speed
        self.damage = damage
        self.type = type
        self.width = width
        self.range = range

        self.shot_time = pygame.time.get_ticks()
        self.effects = effects if effects is not None else {}

        self.target_x = target_x
        self.target_y = target_y
        self.targets_hit = []

        self.vx = 0
        self.vy = 0
        dx = self.target_x - self.x
        dy = self.target_y - self.y

        self.angle = math.degrees(math.atan2(-dy, dx))
        self.progress = 0

        self.bullet_type = bullet_type
        self.bullet_type_info = bullet_type_info
        img = random.choice(self.bullet_type)

        self.base_image = pygame.transform.scale(self.bullet_type_info.img.get(img),(self.width*2,self.width*2))

        self.age = 0                # frames since it was fired (bullet patterns)
        self.motion = None          # see the top of this file
        self.set_velocity()
        length = math.hypot(self.target_x - self.x, self.target_y - self.y) or 1
        self.dir_x, self.dir_y = (self.target_x - self.x) / length, (self.target_y - self.y) / length
        self.base_x, self.base_y = self.x, self.y

    def bounce_off(self, rect):
        """(8.11) Off a wall (Frozen Orb's bullets): back to where it was, the side it hit turns it around."""
        px, py = self.x - self.vx, self.y - self.vy
        if not rect.left <= px <= rect.right:               # came from the left / right
            self.vx, self.dir_x, self.target_x = -self.vx, -self.dir_x, 2 * self.x - self.target_x
        else:                                               # from above / below
            self.vy, self.dir_y, self.target_y = -self.vy, -self.dir_y, 2 * self.y - self.target_y
        self.x, self.y = px, py
        m = self.motion
        if m and m.get("kind") == "wave":                    # a wave line turns its middle line too
            self.base_x, self.base_y = px, py

    def set_velocity(self):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        length = math.sqrt(dx**2 + dy**2)

        if length != 0:
            self.vx = dx / length * self.speed
            self.vy = dy / length * self.speed
        else:
            self.vx = 0
            self.vy = 0

    def check_duration(self):
        if pygame.time.get_ticks() - self.shot_time < self.range and self.shot_time != 0:
            return True, {}
        # copy: callers append dmg to the explosion list, it must not grow on the weapon itself
        return False, copy.deepcopy(self.effects)
        
    def split_now(self):
        """The bullets it bursts into right now (split), or None."""
        m = self.motion
        if m and m["kind"] == "split" and self.age >= m["after"]:
            return ring_of(self.x, self.y, m["children"], math.atan2(self.vy, self.vx), self.bullet_type_info)
        return None

    def land_children(self):
        """The ring a thrown bomb throws out where it lands ([] for other bullets)."""
        m = self.motion
        if m and m["kind"] == "land_ring":
            return ring_of(self.x, self.y, m["children"], random.uniform(0, math.tau), self.bullet_type_info)
        return []

    def move_pattern(self, enemies):
        """Bullet patterns: sets vx / vy for this frame. True if it moved by a pattern."""
        m = self.motion
        kind = m["kind"]
        if kind == "pulse":
            # smooth: speeds up and slows down (sine) - out for `out` frames, then back for `back` frames;
            # the distance goes with the time, so [45, 15] = 3 steps forward, 1 back
            out, back = m["pulse"]
            t = self.age % (out + back)
            v = math.sin(math.pi * t / out) if t < out else -math.sin(math.pi * (t - out) / back)
            self.vx, self.vy = self.dir_x * self.speed * v, self.dir_y * self.speed * v
            return True
        if kind == "slowdown":
            if m.get("return") and self.age >= m["return"]["after"]:
                self.fly_home(m["return"]["home"]())
                return True
            self.speed = max(m["min"], self.speed * m["decay"])
            self.vx, self.vy = self.dir_x * self.speed, self.dir_y * self.speed
            return True
        if kind == "wave":
            self.base_x += self.dir_x * self.speed
            self.base_y += self.dir_y * self.speed
            if m.get("bounce", 0) > 0 and m.get("bounds"):           # off a wall: the line turns back
                w, h = m["bounds"]
                if not 0 <= self.base_x <= w:
                    self.dir_x = -self.dir_x
                    self.base_x = min(w, max(0, self.base_x))
                    m["bounce"] -= 1
                elif not 0 <= self.base_y <= h:
                    self.dir_y = -self.dir_y
                    self.base_y = min(h, max(0, self.base_y))
                    m["bounce"] -= 1
            off = m["amp"] * math.sin(math.tau * self.age / m["period"]) * m["sign"]
            self.vx = self.base_x - self.dir_y * off - self.x
            self.vy = self.base_y + self.dir_x * off - self.y
            return True
        if kind == "creep" and enemies:
            t = enemies[0]
            d = math.hypot(t.x - self.x, t.y - self.y)
            if d > 1:
                self.vx, self.vy = (t.x - self.x) / d * m["speed"], (t.y - self.y) / d * m["speed"]
            return True
        return False

    def fly_home(self, home):
        """A returning spore: speeds up towards its owner; there it is gone (its life ends)."""
        dx, dy = home[0] - self.x, home[1] - self.y
        d = math.hypot(dx, dy)
        if d <= max(RETURN_SPEED[1], self.width):
            self.range = 0
            self.vx = self.vy = 0
            return
        self.speed = min(RETURN_SPEED[1], self.speed + RETURN_SPEED[0])
        self.vx, self.vy = dx / d * self.speed, dy / d * self.speed

    def update(self,enemies):
        self.age += 1
        if self.motion and self.move_pattern(enemies):
            self.x += self.vx
            self.y += self.vy
            return

        if self.effects:
            for effect_name, effect in self.effects.items():

                if effect_name == "bubble":

                    self.speed -= effect[0]
                    if self.speed < 1.0:
                        self.speed = 1.0
                    self.set_velocity()

                elif effect_name == "throw":
                    old_progress = self.progress

                    elapsed = pygame.time.get_ticks() - self.shot_time
                    progress = min(elapsed / self.range, 1)

                    progress = 1 - (1 - progress) ** 3

                    self.vx = (self.target_x - self.start_x) * (progress - old_progress)
                    self.vy = (self.target_y - self.start_y) * (progress - old_progress)

                    self.progress = progress

                elif effect_name == "homing":
            # effect -> [turn_speed]
                    target = None
                    dist = 0
                    nearest = 9999

                    for enemy in enemies:
                        dx = self.x - enemy.x
                        dy = self.y - enemy.y
                        dist = math.sqrt(dx*dx+dy*dy)
                        if dist < nearest:
                            nearest = dist
                            target = enemy

                    
                    # [turn speed] or [turn speed, turn speed at undead] (Holy Orb)
                    turn_speed = effect[1] if len(effect) > 1 and target is not None and \
                        getattr(target, "species", None) == "undead" else effect[0]                    
                    if target:
                        target_dx = target.x - self.x
                        target_dy = target.y - self.y
                        target_angle = math.degrees(math.atan2(-target_dy, target_dx))
                        
                        angle_diff = (target_angle - self.angle + 180) % 360 - 180
                                        
                        if abs(angle_diff) <= turn_speed:
                            self.angle = target_angle
                        else:
                            if angle_diff > 0:
                                self.angle += turn_speed
                            else:
                                self.angle -= turn_speed
                        
                        self.angle = (self.angle + 180) % 360 - 180
                        
                        rad = math.radians(self.angle)
                        self.vx = math.cos(rad) * self.speed
                        self.vy = -math.sin(rad) * self.speed                   

        
        self.x += self.vx
        self.y += self.vy

    def draw(self,screen):
        
        if not self.base_image:
            return
        if not screen.get_clip().inflate(OFF_VIEW_MARGIN, OFF_VIEW_MARGIN).collidepoint(self.x, self.y):
            return                                  # (11.11) off the camera in a big room: nothing to draw

        angle = round(math.degrees(math.atan2(-self.vy, self.vx)))
        if getattr(self, "_turned", None) is None or self._turned[0] != angle:
            self._turned = (angle, pygame.transform.rotate(self.base_image, angle))   # (11.11) only when it turns
        rotated_image = self._turned[1]

        rect = rotated_image.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(rotated_image, rect.topleft)

    def hit_reach(self, target):
        """How close the centres must be for a hit. (10.11) The player's bullets also count their own size, so big
        ones (Hand Cannon, Laser Cannon) hit with their whole body; enemy bullets keep the old reach (dodging)."""
        if getattr(self, "fixed_reach", None):              # (10.11) song fights: a smaller, fixed hitbox
            return self.fixed_reach
        reach = target.width * 1.3
        return reach + self.width / 2 if self.type == "player" else reach

    def check_collision(self, target):
        distance = math.sqrt((self.x - target.x) ** 2 + (self.y - target.y) ** 2)
        reach = self.hit_reach(target)
        if "pierce" in self.effects or "throw" in self.effects:
            if target in self.targets_hit or "throw" in self.effects:
                return False
            elif distance < reach:
                self.targets_hit.append(target)
        return distance < reach
    
    def deal_damage(self, target):
        if self.check_collision(target) and target.type != self.type:
            effect = target.take_damage(self.damage,copy.deepcopy(self.effects))
            # ["pierce",[10]] or ["explosion",[20,0.5]] or [static dmg]
            if effect not in (True,False,None,[True]):
                if effect[0] == "pierce":
                    return [effect[0],effect[1][0]<len(self.targets_hit)]
                if effect[0] != "static":
                    effect[1].append(self.damage)
            return effect
        return False