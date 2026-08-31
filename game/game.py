import pygame
from game.states import GameState
from game.combat.combat import Combat
from game.combat.player.shooter import Shooter
from lib.sfx_manager import sfx_manager as sfx
from game.map.map import Map
from game.map.player import Player


class Game:

    def __init__(self):
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.font = pygame.font.SysFont(None, 60)
        self.state = GameState.MAP
        self.running = True
        self.clock = pygame.time.Clock()
        self.map = Map(self.screen)
        self.player = Player(128,128,self.map)
        self.map.player = self.player

        self.player_in_combat = Shooter(400, 300)
        self.combat = None
        

    def run(self):
        while self.running:
            keys = pygame.key.get_pressed()
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            if self.state == GameState.MENU:
                self.update_menu(events, keys)

            elif self.state == GameState.MAP:
                self.update_world(events, keys)

            elif self.state == GameState.COMBAT:
                self.update_combat(events, keys)

            elif self.state == GameState.INVENTORY:
                self.update_inventory(events, keys)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def update_menu(self, events, keys):
        pass

    def update_world(self, events, keys):
        self.map.draw(self.screen)
        self.player.draw(self.screen)
        fight = self.player.move(keys)
        if fight == "boss1":
            self.state = GameState.COMBAT
            self.combat = Combat(self.screen, self.player_in_combat,"boss1", "easy")


    def update_combat(self, events, keys):
        self.combat.handle_events(events)
        self.combat.update()
        self.combat.draw()

        if self.combat.finished:
            self.state = GameState.MAP
            if self.combat.win:
                if self.combat.enemy == "boss1":
                    self.map.layout[8] = self.map.layout[8][:8] + "1" + self.map.layout[8][8 + 1:]
            else:
                self.player.set_position(128,128)
            

    def update_inventory(self, events, keys):
        pass
