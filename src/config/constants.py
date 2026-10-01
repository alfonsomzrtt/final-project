"""
Application-wide constants.

This module contains immutable values that define the rules and
fixed characteristics of the Block Design Puzzle Game.

Do not put runtime configuration, mutable state, GUI settings,
camera settings, or model paths in this module.
"""


# ============================================================
# GAME
# ============================================================

TOTAL_STAGES = 3
PATTERNS_PER_STAGE = 5

TOTAL_PATTERNS_PER_GAME = TOTAL_STAGES * PATTERNS_PER_STAGE


# ============================================================
# DIFFICULTY
# ============================================================

EASY_TIME_LIMIT = 30
NORMAL_TIME_LIMIT = 25
HARD_TIME_LIMIT = 20


# ============================================================
# BLOCK DESIGN
# ============================================================

MIN_GRID_SIZE = 2
MAX_GRID_SIZE = 3

SUPPORTED_GRID_SIZES = (2, 3)


# ============================================================
# BLOCK CLASSES
# ============================================================

BLOCK_CLASS_RED = 0
BLOCK_CLASS_WHITE = 1
BLOCK_CLASS_RED_TOP_LEFT = 2
BLOCK_CLASS_RED_TOP_RIGHT = 3
BLOCK_CLASS_RED_BOTTOM_LEFT = 4
BLOCK_CLASS_RED_BOTTOM_RIGHT = 5

TOTAL_BLOCK_CLASSES = 6


# ============================================================
# PLAYERS
# ============================================================

PLAYER_1 = 1
PLAYER_2 = 2

STAGES_REQUIRED_TO_WIN = 2