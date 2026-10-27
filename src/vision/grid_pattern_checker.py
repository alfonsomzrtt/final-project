"""Match a reconstructed YOLO grid against a 2x2 target pattern."""

from dataclasses import dataclass

from vision.grid_reconstruction import (
    GridReconstructionResult,
    GridReconstructor,
)
from vision.pattern_matcher import PatternMatcher


STATUS_INVALID_RECONSTRUCTION = "invalid_reconstruction"
STATUS_MISMATCH = "mismatch"
STATUS_MATCH = "match"


@dataclass(frozen=True)
class GridPatternCheckResult:
    """Explicit result of reconstruction followed by pattern matching."""

    status: str
    detected_pattern: list[list[int | None]] | None
    accuracy: float | None
    is_match: bool
    errors: tuple[str, ...] = ()


class GridPatternChecker:
    """Reconstruct and compare a 2x2 detection grid without game logic."""

    def __init__(
        self,
        grid_bounds: tuple[int, int, int, int],
        matcher: PatternMatcher | None = None,
    ):
        self.reconstructor = GridReconstructor(grid_bounds)
        self.matcher = matcher or PatternMatcher()

    def check(
        self,
        detections,
        target_pattern,
        frame_size: tuple[int, int] | None = None,
    ) -> GridPatternCheckResult:
        """Return an explicit reconstruction and matching result."""
        self._validate_target_pattern(target_pattern)

        try:
            reconstruction = self.reconstructor.reconstruct(
                detections,
                frame_size=frame_size,
            )
        except (TypeError, ValueError) as exc:
            return GridPatternCheckResult(
                status=STATUS_INVALID_RECONSTRUCTION,
                detected_pattern=None,
                accuracy=None,
                is_match=False,
                errors=(str(exc),),
            )

        if not reconstruction.valid:
            return GridPatternCheckResult(
                status=STATUS_INVALID_RECONSTRUCTION,
                detected_pattern=reconstruction.matrix,
                accuracy=None,
                is_match=False,
                errors=reconstruction.errors,
            )

        match_result = self.matcher.match(
            reconstruction.matrix,
            target_pattern,
        )
        is_match = match_result["is_match"]
        return GridPatternCheckResult(
            status=STATUS_MATCH if is_match else STATUS_MISMATCH,
            detected_pattern=reconstruction.matrix,
            accuracy=match_result["accuracy"],
            is_match=is_match,
        )

    @staticmethod
    def _validate_target_pattern(target_pattern):
        if not isinstance(target_pattern, (list, tuple)):
            raise TypeError("target_pattern must be a 2x2 matrix")
        if len(target_pattern) != 2:
            raise ValueError("target_pattern must have exactly 2 rows")

        for row in target_pattern:
            if not isinstance(row, (list, tuple)) or len(row) != 2:
                raise ValueError("target_pattern must be a 2x2 matrix")
            for cell in row:
                if (
                    type(cell) is not int
                    or not 0 <= cell <= 5
                ):
                    raise ValueError(
                        "target_pattern cells must be integer classes 0 to 5"
                    )
