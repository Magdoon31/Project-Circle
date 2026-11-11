# RESTART (11.11): the game closes and starts again by itself - Settings -> Video -> Full screen needs it (every
# screen of the game takes its size when it is made). The new game opens straight on Settings -> Video.

import os
import subprocess
import sys

import pygame

SETTINGS_FLAG = "--open-video-settings"


def restart_game():
    """Start a new copy of the game and close this one (the settings must be saved before)."""
    subprocess.Popen(new_command())
    pygame.quit()
    sys.exit()


def new_command():
    others = [arg for arg in sys.argv[1:] if arg != SETTINGS_FLAG]
    if getattr(sys, "frozen", False):                       # the built .exe
        start = [sys.executable]
    else:                                                    # python main.py
        start = [sys.executable, os.path.abspath(sys.argv[0])]
    return start + others + [SETTINGS_FLAG]


def opens_on_settings():
    """Was this game started by restart_game()?"""
    return SETTINGS_FLAG in sys.argv
