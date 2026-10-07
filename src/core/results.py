"""Immutable result objects produced by gameplay/vision."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PatternResult:
    correct: bool
    accuracy: float
    elapsed_time: float
    time_left: int
    score: int

    def __post_init__(self):
        if not isinstance(self.correct, bool):
            raise TypeError("correct must be bool")
        if not 0.0 <= self.accuracy <= 1.0:
            raise ValueError("accuracy must be between 0.0 and 1.0")
        if self.elapsed_time < 0:
            raise ValueError("elapsed_time cannot be negative")
        if self.time_left < 0:
            raise ValueError("time_left cannot be negative")
        if self.score < 0:
            raise ValueError("score cannot be negative")
