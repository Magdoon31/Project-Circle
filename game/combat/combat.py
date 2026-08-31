import pygame

from game.combat.projectile import projectile as Projectile
from game.combat.boss.boss import Boss
from lib.sfx_manager import sfx_manager as sfx


class Combat:

    def __init__(self, screen, player, enemy, difficulty="easy", ):
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

        self.sfx = sfx()
        
        self.sfx.load_sfx("shoot", "assets/sfx/player_shoot.mp3")
        self.sfx.load_sfx("explosion", "assets/sfx/explosion.mp3")
        self.sfx.load_sfx("hit", "assets/sfx/player_hit.mp3")

        if difficulty == "easy":
            self.player.hp = 150
        elif difficulty == "medium":
            self.player.hp = 125
        else:
            self.player.hp = 100

    def handle_events(self, events):

        for event in events:

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.finished = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    new_projectile = self.player.shoot("basic")      
                    if new_projectile is not None:
                        self.sfx.play_sfx("shoot")
                        self.player_projectiles.append(new_projectile)

    def update(self):

        keys = pygame.key.get_pressed()
        self.player.move(keys, self.screen)

        for projectile in self.player_projectiles[:]:
            Projectile.update(projectile)
            if (
                projectile.x < 0
                or projectile.x > self.screen.get_width()
                or projectile.y < 0
                or projectile.y > self.screen.get_height()
            ):
                self.player_projectiles.remove(projectile)
                continue

            if Projectile.deal_damage(projectile, self.boss):
                self.player_projectiles.remove(projectile)
                self.sfx.play_sfx("hit")
                if self.boss.health <= 0:
                    self.win = True
                    self.finished = True


        for projectile in self.boss_projectiles[:]:
            Projectile.update(projectile)
            if Projectile.deal_damage(projectile, self.player):
                self.boss_projectiles.remove(projectile)
                self.sfx.play_sfx("hit")
                if self.player.hp <= 0:
                    self.win = False
                    self.finished = True

        self.boss.move(self.player.x, self.player.y, self.screen)

        self.boss_projectiles.extend(self.boss.attack(self.player))

    def draw(self):

        self.screen.fill((0, 0, 0))
        for projectile in self.player_projectiles:
            Projectile.draw(projectile, self.screen)
        for projectile in self.boss_projectiles:
            Projectile.draw(projectile, self.screen)
        self.player.draw(self.screen, self.difficulty)
        self.boss.draw(self.screen)

        pygame.display.flip()