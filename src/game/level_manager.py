"""
Level manager.

This module manages stages and puzzle progression
within a game session.
"""

from config.constants import (
    TOTAL_STAGES,
    PATTERNS_PER_STAGE,
)
from core.state import GameState


class LevelManager:

    def reset(self, state: GameState):
        """Reset progression to the first pattern of the first stage."""

        state.current_stage = 1
        state.current_pattern = 1

    def start_stage(self, state: GameState, stage: int):
        """Start a specific stage."""

        if not 1 <= stage <= TOTAL_STAGES:
            raise ValueError(f"Invalid stage: {stage}")

        state.current_stage = stage
        state.current_pattern = 1

    def start_pattern(self, state: GameState, pattern: int):
        """Start a specific pattern within the current stage."""

        if not 1 <= pattern <= PATTERNS_PER_STAGE:
            raise ValueError(f"Invalid pattern: {pattern}")

        state.current_pattern = pattern

    def next_pattern(self, state: GameState) -> bool:
        """
        Move to the next pattern.

        Returns:
            True if progression moved to another pattern.
            False if the current stage has been completed.
        """

        if state.current_pattern < PATTERNS_PER_STAGE:
            state.current_pattern += 1
            return True

        return False

    def next_stage(self, state: GameState) -> bool:
        """
        Move to the next stage.

        Returns:
            True if another stage exists.
            False if the entire game has been completed.
        """

        if state.current_stage < TOTAL_STAGES:
            state.current_stage += 1
            state.current_pattern = 1
            return True

        return False

    def is_last_pattern(self, state: GameState) -> bool:
        """Return True if the current pattern is the last pattern."""

        return state.current_pattern == PATTERNS_PER_STAGE

    def is_last_stage(self, state: GameState) -> bool:
        """Return True if the current stage is the last stage."""

        return state.current_stage == TOTAL_STAGES