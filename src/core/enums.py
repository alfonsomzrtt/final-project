"""Application enums."""

from enum import Enum, auto


class GamePhase(Enum):
    LOBBY = auto()
    PLAYING = auto()
    STAGE_RESULT = auto()
    GAME_RESULT = auto()
    SUDDEN_DEATH = auto()


class Difficulty(Enum):
    EASY = auto()
    NORMAL = auto()
    HARD = auto()


class Player(Enum):
    PLAYER_1 = auto()
    PLAYER_2 = auto()
