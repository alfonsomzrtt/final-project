"""
Puzzle loader.

This module manages puzzle selection from the pattern bank.

The loader is responsible for selecting patterns for a game session.
It does not handle GUI rendering, computer vision, or gameplay scoring.
"""

import random

from config.constants import (
    TOTAL_STAGES,
    PATTERNS_PER_STAGE,
)
from core.enums import Difficulty


class PuzzleLoader:
    def __init__(self):
        self.pattern_bank = self._create_pattern_bank()
        self.selected_patterns = []

    def _create_pattern_bank(self):
        """Create the available pattern identifiers."""

        return {
            Difficulty.EASY: [
                f"E{i:02d}" for i in range(1, 21)
            ],
            Difficulty.NORMAL: [
                f"M{i:02d}" for i in range(1, 21)
            ],
            Difficulty.HARD: [
                f"H{i:02d}" for i in range(1, 21)
            ],
        }

    def load_game_patterns(self, difficulty: Difficulty):
        """
        Select patterns for a new game session.

        A game session contains 15 unique patterns:
        3 stages × 5 patterns.
        """

        available_patterns = self.pattern_bank[difficulty]
        total_patterns = TOTAL_STAGES * PATTERNS_PER_STAGE

        self.selected_patterns = random.sample(
            available_patterns,
            total_patterns,
        )

        return self.selected_patterns

    def get_pattern(self, stage: int, pattern: int):
        """
        Get a pattern identifier based on stage and pattern number.
        """

        if not self.selected_patterns:
            raise RuntimeError("Game patterns have not been loaded.")

        index = (
            (stage - 1) * PATTERNS_PER_STAGE
            + (pattern - 1)
        )

        if index >= len(self.selected_patterns):
            raise IndexError(
                f"Invalid stage/pattern: {stage}/{pattern}"
            )

        return self.selected_patterns[index]

    def reset(self):
        """Clear the currently selected patterns."""

        self.selected_patterns = []