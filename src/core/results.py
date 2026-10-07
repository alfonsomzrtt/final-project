from dataclasses import dataclass


@dataclass(frozen=True)
class PatternResult:
    correct: bool
    accuracy: float
    time_left: int

    def __post_init__(self):
        if not 0.0 <= self.accuracy <= 1.0:
            raise ValueError("accuracy must be between 0.0 and 1.0")

        if self.time_left < 0:
            raise ValueError("time_left cannot be negative")

        