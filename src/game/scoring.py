"""
Game scoring.

This module contains scoring rules for the Block Design puzzle game.
It does not handle GUI, camera, or computer vision processing.
"""

from config.constants import STAGES_REQUIRED_TO_WIN
from core.enums import Player


class Scoring:
    def __init__(self):
        self.score_player_1 = 0
        self.score_player_2 = 0

        self.stage_wins_player_1 = 0
        self.stage_wins_player_2 = 0

    def reset(self):
        """Reset all scores and stage wins."""

        self.score_player_1 = 0
        self.score_player_2 = 0

        self.stage_wins_player_1 = 0
        self.stage_wins_player_2 = 0

    def add_pattern_point(self, player: Player):
        """Award one point for successfully completing a pattern."""

        if player == Player.PLAYER_1:
            self.score_player_1 += 1

        elif player == Player.PLAYER_2:
            self.score_player_2 += 1

    def award_stage_win(self, player: Player):
        """Award a stage win to a player."""

        if player == Player.PLAYER_1:
            self.stage_wins_player_1 += 1

        elif player == Player.PLAYER_2:
            self.stage_wins_player_2 += 1

    def has_game_winner(self) -> bool:
        """Return True if a player has won enough stages."""
        return (
            self.stage_wins_player_1 >= STAGES_REQUIRED_TO_WIN
            or
            self.stage_wins_player_2 >= STAGES_REQUIRED_TO_WIN
        )

    def get_game_winner(self):
        """Return the player who has won the required number of stages."""

        if self.stage_wins_player_1 >= STAGES_REQUIRED_TO_WIN:
            return Player.PLAYER_1

        if self.stage_wins_player_2 >= STAGES_REQUIRED_TO_WIN:
            return Player.PLAYER_2

        return None