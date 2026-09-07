import math
import random

import pygame



class Combat:

    def __init__(self, screen, player, enemies, hard_mode, sfx=None, boss=None):
        self.screen = screen
        self.player = player
        self.boss = boss
        self.player_projectiles = []
        self.enemy_projectiles = []

        self.timer = pygame.time.get_ticks()
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
        self.sfx.load_sfx("explosion", "assets/sfx/combat/explosion.mp3")
        self.sfx.load_sfx("hit", "assets/sfx/combat/hit.wav")
        self.sfx.load_sfx("laser1", "assets/sfx/combat/laser1.mp3")
        self.sfx.load_sfx("laser2", "assets/sfx/combat/laser2.wav")
        self.sfx.load_sfx("laser3", "assets/sfx/combat/laser3.wav")
        self.sfx.load_sfx("run", "assets/sfx/combat/run.wav")
        self.sfx.load_sfx("death", "assets/sfx/combat/death.wav")
        self.sfx.load_sfx("enemy_death", "assets/sfx/combat/enemy_death.wav")
        self.sfx.load_sfx("player_hit", "assets/sfx/combat/player_hit.wav")
        self.sfx.load_sfx("bullet_burst", "assets/sfx/combat/bullet_burst.mp3")
        self.sfx.load_sfx("dmg_effect", "assets/sfx/combat/dmg_effect.wav")
        self.sfx.load_sfx("zap1", "assets/sfx/combat/zap_sfx1.mp3")
        self.sfx.load_sfx("zap2", "assets/sfx/combat/zap_sfx2.mp3")
        self.sfx.load_sfx("zap3", "assets/sfx/combat/zap_sfx3.mp3")

        self.money = 0
        self.money_mult = random.randint(10,40)

        self.hard_mode = hard_mode
        self.timer = 0

        self.segments = [pygame.transform.scale(pygame.image.load(f"assets/img/combat/zap/zap{nr}.png"),(64,64)) for nr in range(1,5)]
        self.zapped_enemies = []
        self.explosion_img = [pygame.image.load(f"assets/img/combat/projectiles/boom{nr}.png") for nr in range(1,7)]
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

        for projectile in self.player_projectiles[:]:
            projectile.update()
            if (
                projectile.x < 0
                or projectile.x > self.screen.get_width()
                or projectile.y < 0
                or projectile.y > self.screen.get_height()
            ):
                self.player_projectiles.remove(projectile)
                continue

            if not projectile.check_duration():
                self.player_projectiles.remove(projectile)
                continue
            for enemy in self.enemies:

                special_effect = projectile.deal_damage(enemy)
                #special_effect -> [name,weapon_effect]

                if special_effect:
                    if special_effect[0] != "pierce":
                        self.player_projectiles.remove(projectile)

                    if special_effect[0] == "zap":
                        self.zap(special_effect[1], enemy)
                        self.sfx.play(f"zap{random.randint(1,3)}")
                    elif special_effect[0] == "explosion":
                        self.explosion((projectile.x,projectile.y), special_effect[1],enemy)
                        self.sfx.play("explosion")
                        
                    if enemy.hp <= 0:    
                        self.sfx.play("enemy_death")
                        projectiles = enemy.attack(self.timer)
                        self.enemy_projectiles.extend(projectiles)
                        self.enemies.remove(enemy)
                        
                    else:
                        self.sfx.play("hit")
                    break
            if len(self.enemies) == 0:
                self.win = True
                self.finished = True


        for projectile in self.enemy_projectiles[:]:
            projectile.update()

            if not projectile.check_duration():
                self.enemy_projectiles.remove(projectile)
                continue 

            if projectile.deal_damage(self.player):
                self.enemy_projectiles.remove(projectile)
                self.sfx.play("player_hit")
                if self.player.hp <= 0:
                    self.win = False
                    self.finished = True

        for enemy in self.enemies:
            enemy.move(self.player.x, self.player.y, self.screen)
            proj = enemy.attack(self.timer, self.player, self.hard_mode)
            self.enemy_projectiles.extend(proj)

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

           
    def draw(self):

        self.screen.fill((0, 0, 0))
        for projectile in self.player_projectiles:
            projectile.draw(self.screen)
        for projectile in self.enemy_projectiles:
            projectile.draw(self.screen)
        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        for enemy in self.zapped_enemies:
            if enemy[2] > 0:
                self.ZapEffect(enemy[0],enemy[1])
                enemy[2] -= 1
                if enemy[2] <= 0:
                    self.zapped_enemies.remove(enemy)
        self.ExplosionEffect()

        if self.win:

            pygame.draw.rect(self.screen,(200,200,200),(self.screen.get_width()/2 - self.screen.get_width()/12, self.screen.get_height()/3, self.screen.get_width()/6,self.screen.get_height()/2.9),0,10)
            end_title = self.font_heavy["mid"].render("Win!", True, (0,0,0))

            flawless_text = self.font_heavy["mid"].render("Flawless!!", True, (255,255,255))
            is_flawless = self.player.hp == self.player.max_hp
            money_base = self.money*self.money_mult*0.05 if not self.boss else self.money
            if is_flawless and not self.hard_mode and not self.boss:

                end_text = self.font_light["mid"].render(f"{money_base}$ X 1.5!", True, (0,0,0))

                if not self.money_boost_applied:
                    self.money_mult *= 1.5
                    self.money_boost_applied = True

            else:
                end_text = self.font_light["mid"].render(f"{money_base}$", True, (0,0,0))
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
            
            e.remove(enemy_hit)
            pos = (enemy_hit.x,enemy_hit.y)

            next_enemy = enemy_hit
            last_enemy = enemy_hit
        
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
                        
                    
                    self.enemies[self.enemies.index(next_enemy)].take_damage(effect[2]*effect[1])

                    if self.enemies[self.enemies.index(next_enemy)].hp <= 0:
                        self.sfx.play("enemy_death")
                        self.enemies.pop(self.enemies.index(next_enemy))

                    self.zapped_enemies.append([(last_enemy.x,last_enemy.y),(next_enemy.x,next_enemy.y),8])

                    last_enemy = next_enemy
                    next_enemy = None
                    e.remove(last_enemy)

    def explosion(self, pos, effect, enemy_hit):
        # effect -> [width,dmg_mult,dmg]

        e = self.enemies.copy()

        self.explosions.append([effect[0],pos,18])
        
        if len(e) > 1:

            e.remove(enemy_hit)
            w = effect[0]

            for enemy in e:

                dx = enemy.x - pos[0]
                dy = enemy.y - pos[1]
                dist = math.sqrt(dx*dx + dy*dy)

                if dist <= w:
                    self.enemies[self.enemies.index(enemy)].take_damage(effect[2]*effect[1])

                    if self.enemies[self.enemies.index(enemy)].hp <= 0:
                        self.sfx.play("enemy_death")
                        self.enemies.pop(self.enemies.index(enemy))
                    


    
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
        # exp -> [width,pos,time]
        for exp in self.explosions:

            w = exp[0]
            pos = exp[1]

            if exp[2] > 0:

                stage = math.ceil(exp[2]/6)
                img = pygame.transform.scale(self.explosion_img[stage],(w*2,w*2))
                rect = img.get_rect(center=pos)

                if exp[2]>8:

                    pygame.draw.circle(self.screen,(240,170,160),pos,w,w//15)

                self.screen.blit(img, rect)
                exp[2] -= 1

            else:

                self.explosions.remove(exp)