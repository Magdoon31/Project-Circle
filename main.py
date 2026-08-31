import pygame
from game.game import Game

pygame.init()
pygame.mixer.init()

game = Game()
game.run()
