import pygame
from game.game import Game

pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(64)

game = Game()
game.run()
