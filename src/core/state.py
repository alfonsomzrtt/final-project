"""
Runtime game state.

This module stores the current state of the game during execution.

State should contain information that can change while the game is running.
It should not contain GUI objects, camera objects, detection logic,
or other heavy runtime components.
"""

from dataclasses import dataclass

from core.enums import GamePhase, Difficulty, Player


@dataclass
class GameState:
    # GAME FLOW
    phase: GamePhase = GamePhase.LOBBY
    difficulty: Difficulty = Difficulty.EASY

    # STAGE & PATTERN
    current_stage: int = 1
    current_pattern: int = 1

    # PLAYERS
    score_player_1: int = 0
    score_player_2: int = 0

    stage_score_player_1: int = 0
    stage_score_player_2: int = 0

    # STAGE WINS
    stage_wins_player_1: int = 0
    stage_wins_player_2: int = 0

    # ACTIVE PLAYER
    active_player: Player = Player.PLAYER_1

