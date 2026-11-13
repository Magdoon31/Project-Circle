# Bakes the main menu title's soft shadow into its picture (13.11): game_title.png -> game_title_shadowed.png
# (game/menu/title_shadow.py says how). Run from the game's folder after changing the title:
#   python tools/make_title_shadow.py

import os
import sys

import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game.menu import title_shadow as TS                                          # noqa: E402


def main():
    pygame.init()
    pygame.image.save(TS.shadowed(pygame.image.load(TS.SOURCE)), TS.OUT)
    print("written", TS.OUT)


if __name__ == "__main__":
    main()
