import copy

import pygame, math

class projectile:
    def __init__(self, x, y, target_x, target_y, speed, damage, player, width, range, bullet_type_info, bullet_type , effects = {}):
        self.x = x
        self.y = y

        self.speed = speed
        self.damage = damage
        self.type = player
        self.width = width
        self.range = range

        self.shot_time = pygame.time.get_ticks()
        self.effects = effects

        self.target_x = target_x
        self.target_y = target_y
        self.targets_hit = []

        self.vx = 0
        self.vy = 0
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        self.angle = math.degrees(math.atan2(-dy, dx))

        self.bullet_type = bullet_type
        self.bullet_type_info = bullet_type_info

        self.base_image = pygame.transform.scale(self.bullet_type_info.img.get(self.bullet_type),(self.width*2,self.width*2))

        self.set_velocity()

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
            return True
        return False
        
    def update(self,enemies):
        if self.effects:
            for effect_name, effect in self.effects.items():
                if effect_name == "bubble":
                    self.speed -= 0.25
                    if self.speed < 0:
                        self.speed = 0
                    self.set_velocity()
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

                    
                    turn_speed = effect[0]                    
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

        angle = math.degrees(math.atan2(-self.vy, self.vx))
        rotated_image = pygame.transform.rotate(self.base_image, angle)

        rect = rotated_image.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(rotated_image, rect.topleft)

    def check_collision(self, target):
        distance = math.sqrt((self.x - target.x) ** 2 + (self.y - target.y) ** 2)
        if "pierce" in self.effects:
            if target in self.targets_hit:
                return False
            elif distance < target.width:
                self.targets_hit.append(target)
        return distance < target.width
    
    def deal_damage(self, target):
        if self.check_collision(target) and target.type != self.type:
            effect = target.take_damage(self.damage,copy.deepcopy(self.effects))
            # ["pierce",[10]] or ["explosion",[20,0.5]]
            print(effect)
            if effect not in (True,False,None,[True]):
                if effect[0] == "pierce":
                    return [effect[0],effect[1][0]<len(self.targets_hit)]
                effect[1].append(self.damage)
            return effect
        return False