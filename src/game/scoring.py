"""Pure scoring rules for the Block Design Puzzle Game."""

from config.constants import STAGES_REQUIRED_TO_WIN
from core.enums import Player


class Scoring:
    @staticmethod
    def pattern_points(correct: bool, time_left: int) -> int:
        return time_left * 10 if correct else 0

    @staticmethod
    def determine_stage_winner(
        player_1_time: float,
        player_2_time: float,
        player_1_score: int,
        player_2_score: int,
    ):
        if player_1_time < player_2_time:
            return Player.PLAYER_1
        if player_2_time < player_1_time:
            return Player.PLAYER_2
        if player_1_score > player_2_score:
            return Player.PLAYER_1
        if player_2_score > player_1_score:
            return Player.PLAYER_2
        return None

    @staticmethod
    def is_game_winner(stage_wins: int) -> bool:
        return stage_wins >= STAGES_REQUIRED_TO_WIN
