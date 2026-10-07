"""Runtime game state."""

from dataclasses import dataclass
from typing import Optional

from core.enums import GamePhase, Difficulty, Player


@dataclass
class GameState:
    phase: GamePhase = GamePhase.LOBBY
    difficulty: Difficulty = Difficulty.EASY
    current_stage: int = 1
    current_pattern: int = 1

    score_player_1: int = 0
    score_player_2: int = 0

    stage_score_player_1: int = 0
    stage_score_player_2: int = 0

    stage_time_player_1: float = 0.0
    stage_time_player_2: float = 0.0

    stage_wins_player_1: int = 0
    stage_wins_player_2: int = 0

    pattern_progress_player_1: int = 0
    pattern_progress_player_2: int = 0

    active_player: Player = Player.PLAYER_1
    game_winner: Optional[Player] = None
    sudden_death_round: int = 0
