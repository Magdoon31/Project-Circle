# CONTROLS (11.11): which keys do what (set in Settings -> Controls, kept by options.py).
#   movement - one of three sets: W A S D / I J K L / the arrows (on the map, in a fight, choosing an answer)
#   map, shop - one key each (M, B by default)
#   shoot, equip, delete, tab - not set by default: a key that shoots (like the mouse), equips / takes off the
#     selected item, removes it (asks first), changes the page (Items / Sigils, Buy / Sell)
# ESC and the dialogue keys stay as they are.

import pygame

from game.menu import options as OPT

MOVES = {   # set -> (up, left, down, right)
    "wasd": (pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d),
    "ijkl": (pygame.K_i, pygame.K_j, pygame.K_k, pygame.K_l),
    "arrows": (pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT),
}
DIRECTIONS = ("up", "left", "down", "right")
ACTIONS = ("map", "shop", "shoot", "equip", "delete", "tab")      # the keys you can set one by one


def move_key(direction):
    return MOVES[OPT.get("move_keys")][DIRECTIONS.index(direction)]


def held(keys, direction):
    """Is the key for this direction ("up" / "left" / "down" / "right") held down now?"""
    return keys[move_key(direction)]


def key_of(action):
    return OPT.get("key_" + action)


def pressed(event, action):
    """Was this action's key just pressed (in this event)?"""
    key = key_of(action)
    return key is not None and event.type == pygame.KEYDOWN and event.key == key


def pressed_in(events, action):
    return any(pressed(e, action) for e in events)


def holding(keys, action):
    key = key_of(action)
    return key is not None and keys[key]


def key_name(key):
    """How a key is written in Settings ("-" = not set)."""
    return "-" if key is None else pygame.key.name(key).upper()
