"""Temporal stabilization for 2x2 grid pattern check results."""

from dataclasses import dataclass

from vision.grid_pattern_checker import (
    GridPatternCheckResult,
    STATUS_INVALID_RECONSTRUCTION,
    STATUS_MATCH,
    STATUS_MISMATCH,
)


STATUS_PENDING = "pending"
STATUS_STABLE = "stable"
STATUS_REJECTED = "rejected"


@dataclass(frozen=True)
class PatternStabilizationResult:
    """State produced after consuming one sequential frame result."""

    status: str
    target_pattern: tuple[tuple[int, int], tuple[int, int]]
    consecutive_matches: int
    success: bool
    check_result: GridPatternCheckResult


class PatternStabilizer:
    """Require consecutive identical matches before emitting one success."""

    def __init__(self, minimum_matches: int = 3):
        if type(minimum_matches) is not int:
            raise TypeError("minimum_matches must be an integer")
        if minimum_matches <= 0:
            raise ValueError("minimum_matches must be a positive integer")
        self.minimum_matches = minimum_matches
        self.reset()

    def reset(self):
        """Clear all accumulated temporal state."""
        self._target = None
        self._last_matrix = None
        self._consecutive_matches = 0
        self._success_key = None

    def update(
        self,
        check_result: GridPatternCheckResult,
        target_pattern,
    ) -> PatternStabilizationResult:
        """Consume one frame result and return the current stable state."""
        if not isinstance(check_result, GridPatternCheckResult):
            raise TypeError(
                "check_result must be a GridPatternCheckResult"
            )
        target = self._validate_target(target_pattern)

        if self._target != target:
            self._target = target
            self._last_matrix = None
            self._consecutive_matches = 0
            self._success_key = None

        if check_result.status != STATUS_MATCH:
            if check_result.status not in {
                STATUS_MISMATCH,
                STATUS_INVALID_RECONSTRUCTION,
            }:
                raise ValueError(
                    f"Unknown grid pattern status: {check_result.status}"
                )
            self._last_matrix = None
            self._consecutive_matches = 0
            return PatternStabilizationResult(
                status=STATUS_REJECTED,
                target_pattern=target,
                consecutive_matches=0,
                success=False,
                check_result=check_result,
            )

        matrix = self._validate_match_matrix(check_result)
        if matrix != self._last_matrix:
            self._consecutive_matches = 0
            self._last_matrix = matrix
            self._success_key = None

        self._consecutive_matches += 1
        key = (target, matrix)
        stable = self._consecutive_matches >= self.minimum_matches
        success = stable and self._success_key != key
        if success:
            self._success_key = key

        return PatternStabilizationResult(
            status=STATUS_STABLE if stable else STATUS_PENDING,
            target_pattern=target,
            consecutive_matches=self._consecutive_matches,
            success=success,
            check_result=check_result,
        )

    @staticmethod
    def _validate_target(target_pattern):
        if not isinstance(target_pattern, (list, tuple)):
            raise TypeError("target_pattern must be a 2x2 matrix")
        if len(target_pattern) != 2:
            raise ValueError("target_pattern must have exactly 2 rows")

        rows = []
        for row in target_pattern:
            if not isinstance(row, (list, tuple)) or len(row) != 2:
                raise ValueError("target_pattern must be a 2x2 matrix")
            values = []
            for cell in row:
                if type(cell) is not int or not 0 <= cell <= 5:
                    raise ValueError(
                        "target_pattern cells must be integer classes 0 to 5"
                    )
                values.append(cell)
            rows.append(tuple(values))
        return tuple(rows)

    @staticmethod
    def _validate_match_matrix(check_result):
        if not check_result.is_match:
            raise ValueError("match result must have is_match=True")
        matrix = check_result.detected_pattern
        if not isinstance(matrix, list) or len(matrix) != 2:
            raise ValueError("match result must contain a 2x2 matrix")

        rows = []
        for row in matrix:
            if (
                not isinstance(row, list)
                or len(row) != 2
                or any(type(cell) is not int for cell in row)
            ):
                raise ValueError("match result must contain a valid 2x2 matrix")
            rows.append(tuple(row))
        return tuple(rows)
