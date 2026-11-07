from enum import Enum


class GameState(Enum):
    MENU = 1
    MAP = 2
    COMBAT = 3
    INVENTORY = 4
    