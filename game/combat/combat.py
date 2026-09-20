import copy
import math
import random

import pygame



class Combat:

    def __init__(self, screen, player, enemies, enemy_db, hard_mode, sfx=None, boss=None):
        self.screen = screen
        self.player = player
        self.boss = boss
        self.player_projectiles = []
        self.enemy_projectiles = []
        self.enemy_db = enemy_db

        self.enemies = enemies
        self.win = False
        self.finished = False
        self.money_boost_applied = False

        self.font_light = {"small" : pygame.font.Font("assets/font/Nexa-ExtraLight.ttf",18),
                            "mid" : pygame.font.Font("assets/font/Nexa-ExtraLight.ttf",36),}
        self.font_heavy = {"small" : pygame.font.Font("assets/font/Nexa-Heavy.ttf",18),
                            "mid" : pygame.font.Font("assets/font/Nexa-Heavy.ttf",36),
                            "giant" : pygame.font.Font("assets/font/Nexa-Heavy.ttf",128),}
        
        self.sfx = sfx
        
        self.sfx.load_sfx("shoot", "assets/sfx/combat/player_shoot.mp3")
        self.sfx.load_sfx("explosion", "assets/sfx/combat/explosion.wav")
        self.sfx.load_sfx("hit", "assets/sfx/combat/hit.wav")
        self.sfx.load_sfx("laser1", "assets/sfx/combat/laser1.mp3")
        self.sfx.load_sfx("laser2", "assets/sfx/combat/laser2.wav")
        self.sfx.load_sfx("laser3", "assets/sfx/combat/laser3.wav")
        self.sfx.load_sfx("run", "assets/sfx/combat/run.wav")
        self.sfx.load_sfx("death", "assets/sfx/combat/death.wav")
        self.sfx.load_sfx("enemy_death", "assets/sfx/combat/enemy_death.wav")
        self.sfx.load_sfx("player_hit", "assets/sfx/combat/player_hit.wav")
        self.sfx.load_sfx("bullet_burst", "assets/sfx/combat/bullet_burst.mp3")
        self.sfx.load_sfx("posion_effect", "assets/sfx/combat/posion_effect.mp3")
        self.sfx.load_sfx("burn_effect", "assets/sfx/combat/burn_effect.mp3")
        self.sfx.load_sfx("zap1", "assets/sfx/combat/zap_sfx1.mp3")
        self.sfx.load_sfx("zap2", "assets/sfx/combat/zap_sfx2.mp3")
        self.sfx.load_sfx("zap3", "assets/sfx/combat/zap_sfx3.mp3")
        self.sfx.load_sfx("overclock","assets/sfx/combat/overclock.mp3")
        self.sfx.load_sfx("gain_effect","assets/sfx/combat/effect_gain.wav")
        self.sfx.load_sfx("emergency","assets/sfx/combat/emergency.mp3")

        self.money = 0
        self.money_mult = random.randint(10,40)*0.05
        self.money_mult_og = self.money_mult

        self.hard_mode = hard_mode
        self.timer = 0

        self.segments = [pygame.transform.scale(pygame.image.load(f"assets/img/combat/zap/zap{nr}.png"),(64,64)) for nr in range(1,5)]
        self.zapped_enemies = []
        self.explosion_img = [pygame.image.load(f"assets/img/combat/projectiles/boom{nr}.png") for nr in range(1,7)]
        self.nova_explosion_img = [pygame.image.load(f"assets/img/combat/projectiles/nova_boom{nr}.png") for nr in range(1,7)]
        self.explosions = []

    def handle_events(self, events, mouse_btn_pressed):


        for event in events:
                
            if event.type == pygame.MOUSEBUTTONDOWN and not self.player.automatic_weapon:
                if event.button == 1:
                    multiple, new_projectile = self.player.shoot()      
                    if new_projectile is not None:
                        self.sfx.play("shoot")
                        if multiple:
                            self.player_projectiles.extend(new_projectile)
                        else:
                            self.player_projectiles.append(new_projectile)

        if mouse_btn_pressed[0] and self.player.automatic_weapon:
            multiple, new_projectile = self.player.shoot()      
            if new_projectile is not None:
                self.sfx.play("shoot")
                if multiple:
                    self.player_projectiles.extend(new_projectile)
                else:
                    self.player_projectiles.append(new_projectile)

    def update(self):
        self.timer += 1
        keys = pygame.key.get_pressed()
        self.player.move(keys, self.screen)
        if len(self.enemies) > 32:
            for i in range(len(self.enemies)-32):
                self.enemies[-1].hp = 0

        for projectile in self.player_projectiles[:]:
            projectile.update(self.enemies)
            if (
                projectile.x < 0
                or projectile.x > self.screen.get_width()
                or projectile.y < 0
                or projectile.y > self.screen.get_height()
            ):
                self.player_projectiles.remove(projectile)
                continue

            proj_expire, effect = projectile.check_duration()
            if not proj_expire:
                
                if "explosion" in effect:
                    effect["explosion"].append(projectile.damage)
                    self.explosion((projectile.x,projectile.y), effect["explosion"],None)
                    self.sfx.play("explosion") 
                self.player_projectiles.remove(projectile)
                continue
           
            for enemy in self.enemies:

                special_effect = projectile.deal_damage(enemy)
                #special_effect -> [name,effect] (and also (T/F) if it hit an enemy) name in (zap, pierce, explosion) effect = []

                if special_effect:
                    if special_effect[0] != "pierce":
                        self.player_projectiles.remove(projectile)
                    else:
                        if special_effect[1]:
                            self.player_projectiles.remove(projectile)


                    if special_effect[0] == "zap":
                        self.zap(special_effect[1], enemy)
                        self.sfx.play(f"zap{random.randint(1,3)}")
                    elif special_effect[0] == "explosion":
                        self.explosion((projectile.x,projectile.y), special_effect[1],enemy)
                        self.sfx.play("explosion")     
                    else:
                        self.sfx.play("hit")
                    break
        if len(self.enemies) == 0:
            self.win = True
            self.finished = True


        for projectile in self.enemy_projectiles[:]:
            if "frost" in self.player.armor_effect:

                dx = self.player.x - projectile.x
                dy = self.player.y - projectile.y

                dist = math.sqrt(dx**2 + dy**2)
                current_speed = math.sqrt(projectile.vx**2 + projectile.vy**2)

                if current_speed > 0:
                    dir_x = projectile.vx / current_speed
                    dir_y = projectile.vy / current_speed

                    if dist < self.player.armor_effect["frost"][0]:
                        projectile.speed = projectile.og_speed / 2
                    else:
                        projectile.speed = projectile.og_speed

                    projectile.vx = dir_x * projectile.speed
                    projectile.vy = dir_y * projectile.speed
    
            projectile.update([self.player])
            proj_expire, effect = projectile.check_duration()
            if not proj_expire:
                if "explosion" in effect:
                    effect["explosion"].append(projectile.damage)
                    self.explosion((projectile.x,projectile.y), effect["explosion"],"player")
                    self.sfx.play("explosion") 
                elif "nova_explosion" in effect:
                    effect["nova_explosion"].append(projectile.damage)
                    self.explosion((projectile.x,projectile.y), effect["nova_explosion"],"player",type="nova_")
                    self.sfx.play("explosion") 
                self.enemy_projectiles.remove(projectile)

            player_hit = projectile.deal_damage(self.player)

            if player_hit:

                if player_hit[0] == "static":

                    self.zap([999,1.0,player_hit[1]],self.player)

                if player_hit[0] == "explosion":

                    self.explosions.append([player_hit[1][0],(projectile.x,projectile.y),24,None])
                    self.sfx.play("explosion")

                self.enemy_projectiles.remove(projectile)
                self.sfx.play("player_hit")

                if self.player.hp <= 0:
                    if self.player.emergency_used == 1:

                        self.enemy_projectiles = []
                        self.sfx.play("emergency")
                        self.player.emergency_used = 0
                        self.player.effects["speed"] = [180,0.33]
                        self.player.hp = self.player.max_hp*0.15

                    else:
                        self.win = False
                        self.finished = True

        for enemy in self.enemies:
            enemy.move(self.player.x, self.player.y, self.screen)
            proj,enemies = enemy.attack(self.timer, self.player, self.hard_mode, self.enemy_db)
            self.enemy_projectiles.extend(proj)
            self.enemies.extend(enemies)
            if enemy.hp <= 0:    
                self.sfx.play("enemy_death")
                projectiles,enemies_spawn = enemy.attack(self.timer, enemy_db=self.enemy_db)
                self.enemy_projectiles.extend(projectiles)
                self.enemies.extend(enemies_spawn)
                self.enemies.remove(enemy)

    # enemy collision
        for i, enemy1 in enumerate(self.enemies):
            for enemy2 in self.enemies[i + 1:]:
                dx = enemy2.x - enemy1.x
                dy = enemy2.y - enemy1.y

                distance = math.sqrt(dx**2 + dy**2)
                min_distance = enemy1.width + enemy2.width

                if distance < min_distance:
                    if distance == 0:
                        distance = 0.1
                        dx = random.choice([-1, 1])
                        dy = random.choice([-1, 1])

                    overlap = min_distance - distance

                    move_x = (dx / distance) * overlap * 0.5
                    move_y = (dy / distance) * overlap * 0.5
                    enemy1.x -= move_x
                    enemy1.y -= move_y
                    enemy2.x += move_x
                    enemy2.y += move_y

        for enemy in self.enemies:
            dx = enemy.x - self.player.x
            dy = enemy.y - self.player.y

            distance = math.sqrt(dx**2 + dy**2)
            min_distance = enemy.width + self.player.width*0.66

            if distance < min_distance:
                if distance == 0:
                    distance = 0.1
                    dx = random.choice([-1, 1])
                    dy = random.choice([-1, 1])

                overlap = min_distance - distance

                # Wektor przesunięcia
                move_x = (dx / distance) * overlap
                move_y = (dy / distance) * overlap

                enemy.x += move_x * 0.5
                enemy.y += move_y * 0.5
                self.player.x -= move_x * 0.5
                self.player.y -= move_y * 0.5
           
    def draw(self):

        self.screen.fill((230, 250, 200))
        for projectile in self.player_projectiles:
            projectile.draw(self.screen)
        for projectile in self.enemy_projectiles:
            projectile.draw(self.screen)
        if "frost" in self.player.armor_effect:
            pygame.draw.circle(self.screen,(40,120,220),(self.player.x,self.player.y),self.player.armor_effect["frost"][0],8)
        if self.player.draw(self.screen):
            self.win = False
            self.finished = True
        for enemy in self.enemies:
            if enemy.draw(self.screen):
                self.sfx.play("enemy_death")
                projectiles,enemies_spawn = enemy.attack(self.timer, enemy_db=self.enemy_db)
                self.enemy_projectiles.extend(projectiles)
                self.enemies.extend(enemies_spawn)
                self.enemies.remove(enemy)
        

        for zap_data in self.zapped_enemies[:]:
            if zap_data["duration"] > 0:

                if zap_data["start_enemy"] in self.enemies:
                    start_pos = (zap_data["start_enemy"].x, zap_data["start_enemy"].y)
                    zap_data["last_start_pos"] = start_pos
                else:
                    start_pos = zap_data["last_start_pos"]

                if zap_data["end_enemy"] in self.enemies:
                    end_pos = (zap_data["end_enemy"].x, zap_data["end_enemy"].y)
                    zap_data["last_end_pos"] = end_pos
                else:
                    end_pos = zap_data["last_end_pos"]

                self.ZapEffect(start_pos, end_pos)
                zap_data["duration"] -= 1
                if zap_data["duration"] <= 0:
                    self.zapped_enemies.remove(zap_data)

        self.ExplosionEffect()

        if self.win:

            pygame.draw.rect(self.screen,(200,200,200),(self.screen.get_width()/2 - self.screen.get_width()/12, self.screen.get_height()/3, self.screen.get_width()/6,self.screen.get_height()/2.9),0,10)
            end_title = self.font_heavy["mid"].render("Win!", True, (0,0,0))

            flawless_text = self.font_heavy["mid"].render("Flawless!!", True, (255,255,255))
            is_flawless = self.player.hp == self.player.max_hp
            money_base = self.money*self.money_mult if not self.boss else self.money     
            if not self.money_boost_applied and not self.boss:
                if not self.hard_mode and is_flawless:
                    self.money_mult *= 1.5      
                if "enemy_gold" in self.player.trinket_effect:
                    self.money_mult *= 1+self.player.trinket_effect["enemy_gold"][0]
                self.money_boost_applied = True
            if round(self.money_mult/self.money_mult_og,1) != 1.0:
                end_text = self.font_light["mid"].render(f"{int(money_base)}$ X {round(self.money_mult/self.money_mult_og,2)}!", True, (0,0,0))
            else:
                end_text = self.font_light["mid"].render(f"{int(money_base)}$", True, (0,0,0))
  
                
            self.screen.blit(end_title, (self.screen.get_width()/2 - end_title.get_width()/2, self.screen.get_height()/2 - end_title.get_height()*3))
            self.screen.blit(end_text, (self.screen.get_width()/2 - end_text.get_width()/2, self.screen.get_height()/2 - end_text.get_height()/2))

            if is_flawless:      
                self.screen.blit(flawless_text, (self.screen.get_width()/2 - flawless_text.get_width()/2, self.screen.get_height()/2 + end_text.get_height()*2))

            end_text = self.font_heavy["giant"].render("CLICK", True, (255,255,255))
            self.screen.blit(end_text, (self.screen.get_width()/2 - end_text.get_width()/2, self.screen.get_height()/1.3))

        elif self.finished:

            end_text = self.font_heavy["giant"].render("CLICK", True, (255,255,255))
            self.screen.blit(end_text, (self.screen.get_width()/2 - end_text.get_width()/2, self.screen.get_height()/2 - end_text.get_height()/2))

        pygame.display.flip()

    def zap(self, effect, enemy_hit):

        e = self.enemies.copy()

        if len(e) > 1:

            if enemy_hit in e:
                e.remove(enemy_hit)
                next_enemy = enemy_hit
            else:
                next_enemy = None

            last_enemy = enemy_hit
            pos = (enemy_hit.x,enemy_hit.y)

            for i in range(effect[0]):
                if len(e) > 0:
                    dist = 0
                    nearest = 9999
                    for enemy in e:

                        dx = pos[0] - enemy.x
                        dy = pos[1] - enemy.y
                        dist = math.sqrt(dx*dx+dy*dy)
                        if dist < nearest:
                            nearest = dist
                            next_enemy = enemy
                        
                    if next_enemy and next_enemy in self.enemies:
                        self.enemies[self.enemies.index(next_enemy)].take_damage(effect[2]*effect[1])

                    self.zapped_enemies.append({
                        "start_enemy": last_enemy,
                        "end_enemy": next_enemy,
                        "last_start_pos": (last_enemy.x, last_enemy.y),
                        "last_end_pos": (next_enemy.x, next_enemy.y),
                        "duration": 8
                    })

                    last_enemy = next_enemy
                    next_enemy = None
                    e.remove(last_enemy)

    def explosion(self, pos, exp_effect, enemy_hit, type=None):
        # effect -> [width,dmg_mult,dmg]

        

        if enemy_hit != "player":
            e = self.enemies[:]
            if enemy_hit:
                e.remove(enemy_hit)
        
        self.explosions.append([exp_effect[0],pos,24,type])
        w = exp_effect[0]
        
        if enemy_hit != "player" and len(e) > 1:
            
            for enemy in e:

                dx = enemy.x - pos[0]
                dy = enemy.y - pos[1]
                dist = math.sqrt(dx*dx + dy*dy)

                if dist <= w + enemy.width*0.5:
                    self.enemies[self.enemies.index(enemy)].take_damage(exp_effect[2]*exp_effect[1],copy.deepcopy(self.player.weapon_effect))

                    if self.enemies[self.enemies.index(enemy)].hp <= 0:
                        self.sfx.play("enemy_death")
                        projectiles,enemies_spawn = enemy.attack(self.timer, enemy_db=self.enemy_db)
                        self.enemy_projectiles.extend(projectiles)
                        self.enemies.extend(enemies_spawn)
                        self.enemies.pop(self.enemies.index(enemy))

        elif enemy_hit == "player":
            dx = self.player.x - pos[0]
            dy = self.player.y - pos[1]
            dist = math.sqrt(dx*dx + dy*dy)

            if dist <= w + self.player.width*0.5:
                self.player.take_damage(exp_effect[2]*exp_effect[1],copy.deepcopy(self.player.weapon_effect))
                    


    
    def ZapEffect(self, start_pos, end_pos):

        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        dist = math.sqrt(dx*dx + dy*dy)

        if dist == 0:
            return

        zap_length = 64
        amount = max(1,math.ceil(dist / zap_length))

        angle = math.degrees(math.atan2(-dy, dx))

        for i in range(amount):
            progress = (i + 0.5) / amount

            x = start_pos[0] + dx * progress
            y = start_pos[1] + dy * progress

            zap_img = random.choice(self.segments)
            
            zap_img = pygame.transform.rotate(zap_img, angle)

            rect = zap_img.get_rect(center=(x, y))

            self.screen.blit(zap_img, rect)

    def ExplosionEffect(self): 
        # exp -> [width,pos,time,nova]
        for exp in self.explosions:

            w = exp[0]
            pos = exp[1]

            if exp[2] > 0:

                stage = math.ceil(exp[2]/4)
                if exp[3]:
                    img = pygame.transform.scale(self.nova_explosion_img[6-stage],(w*2,w*2))
                else:
                    img = pygame.transform.scale(self.explosion_img[6-stage],(w*2,w*2))
                rect = img.get_rect(center=pos)

                if exp[2]>8:

                    pygame.draw.circle(self.screen,(240,170,160),pos,w,w//15)

                self.screen.blit(img, rect)
                exp[2] -= 1

            else:

                self.explosions.remove(exp)