"""
Application enums.

This module defines finite sets of states and options used across
the game, vision, and user-interface components.
"""

from enum import Enum, auto


class GamePhase(Enum):
    LOBBY = auto()
    PLAYING = auto()
    STAGE_RESULT = auto()
    GAME_RESULT = auto()


class Difficulty(Enum):
    EASY = auto()
    NORMAL = auto()
    HARD = auto()


class Player(Enum):
    PLAYER_1 = auto()
    PLAYER_2 = auto()