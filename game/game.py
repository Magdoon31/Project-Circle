import pygame
from game.states import GameState
from game.combat import Combat


class Game:

    def __init__(self):
        self.combat = Combat(self.screen, "easy")
        self.state = GameState.COMBAT
        self.running = True

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()

    def run(self):
        while self.running:

            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            if self.state == GameState.MENU:
                self.update_menu(events)

            elif self.state == GameState.WORLD:
                self.update_world(events)

            elif self.state == GameState.COMBAT:
                self.update_combat(events)

            elif self.state == GameState.INVENTORY:
                self.update_inventory(events)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def update_menu(self, events):
        pass

    def update_world(self, events):
        pass

    def update_combat(self, events):
        self.combat.handle_events(events)
        self.combat.update()
        self.combat.draw()

        if self.combat.finished:
            self.running = False

    def update_inventory(self, events):
        pass