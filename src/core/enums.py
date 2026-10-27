"""Application enums."""

from enum import Enum, IntEnum, auto


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


class GridSize(IntEnum):
    TWO_BY_TWO = 2
    THREE_BY_THREE = 3


class Player(Enum):
    PLAYER_1 = auto()
    PLAYER_2 = auto()
