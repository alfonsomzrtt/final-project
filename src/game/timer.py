"""
Game timer.

This module manages gameplay timing.
It does not contain GUI code or display logic.
"""

import time

from config.constants import (
    EASY_TIME_LIMIT,
    NORMAL_TIME_LIMIT,
    HARD_TIME_LIMIT,
)
from core.enums import Difficulty


class GameTimer:
    def __init__(self):
        self.time_limit = 0
        self.start_time = None
        self.running = False

    def set_difficulty(self, difficulty: Difficulty):
        """Set the time limit based on the selected difficulty."""

        time_limits = {
            Difficulty.EASY: EASY_TIME_LIMIT,
            Difficulty.NORMAL: NORMAL_TIME_LIMIT,
            Difficulty.HARD: HARD_TIME_LIMIT,
        }

        self.time_limit = time_limits[difficulty]

    def start(self):
        """Start the timer."""

        self.start_time = time.monotonic()
        self.running = True

    def stop(self):
        """Stop the timer."""

        self.running = False

    def reset(self):
        """Reset the timer."""

        self.start_time = None
        self.running = False

    def elapsed_time(self) -> float:
        """Return elapsed time in seconds."""

        if self.start_time is None:
            return 0.0

        return time.monotonic() - self.start_time

    def remaining_time(self) -> float:
        """Return remaining time in seconds."""

        remaining = self.time_limit - self.elapsed_time()

        return max(0.0, remaining)

    def is_expired(self) -> bool:
        """Return True if the time limit has been reached."""

        return self.elapsed_time() >= self.time_limit