import pygame

from game.combat.boss.boss import Boss


class Combat:

    def __init__(self, screen, player, enemy, difficulty="easy", sfx=None):
        self.screen = screen
        self.difficulty = difficulty
        self.player = player
        self.boss = Boss(900, 800, difficulty)
        self.player_projectiles = []
        self.boss_projectiles = []

        self.timer = pygame.time.get_ticks()
        self.enemy = enemy
        self.win = False
        self.finished = False

        self.sfx = sfx
        
        self.sfx.load_sfx("shoot", "assets/sfx/combat/player_shoot.mp3")
        self.sfx.load_sfx("explosion", "assets/sfx/combat/explosion.mp3")
        self.sfx.load_sfx("hit", "assets/sfx/combat/player_hit.mp3")

        self.player.hp = 100

    def handle_events(self, events, mouse_btn_pressed):

        

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.finished = True
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

            if projectile.deal_damage(self.boss):
                self.player_projectiles.remove(projectile)
                self.sfx.play("hit")
                if self.boss.health <= 0:
                    self.win = True
                    self.finished = True


        for projectile in self.boss_projectiles[:]:
            projectile.update()

            if not projectile.check_duration():
                self.boss_projectiles.remove(projectile)

            if projectile.deal_damage(self.player):
                self.boss_projectiles.remove(projectile)
                self.sfx.play("hit")
                if self.player.hp <= 0:

                    self.win = False
                    self.finished = True

        self.boss.move(self.player.x, self.player.y, self.screen)

        self.boss_projectiles.extend(self.boss.attack(self.player))

    def draw(self):

        self.screen.fill((0, 0, 0))
        for projectile in self.player_projectiles:
            projectile.draw(self.screen)
        for projectile in self.boss_projectiles:
            projectile.draw(self.screen)
        self.player.draw(self.screen, self.difficulty)
        self.boss.draw(self.screen)

        pygame.display.flip()