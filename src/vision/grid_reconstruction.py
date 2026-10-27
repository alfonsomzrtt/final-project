"""Reconstruct a 2x2 pattern from YOLO detections."""

from dataclasses import dataclass
from itertools import combinations
import math

from config.constants import (
    BLOCK_CLASS_RED,
    BLOCK_CLASS_WHITE,
    BLOCK_CLASS_RED_TOP_LEFT,
    BLOCK_CLASS_RED_TOP_RIGHT,
    BLOCK_CLASS_RED_BOTTOM_LEFT,
    BLOCK_CLASS_RED_BOTTOM_RIGHT,
)
from vision.yolo_detector import Detection


YOLO_CLASS_TO_PATTERN_CLASS = {
    "red_bottom_right": BLOCK_CLASS_RED_BOTTOM_RIGHT,
    "red_bottom_left": BLOCK_CLASS_RED_BOTTOM_LEFT,
    "red_top_right": BLOCK_CLASS_RED_TOP_RIGHT,
    "red_top_left": BLOCK_CLASS_RED_TOP_LEFT,
    "red": BLOCK_CLASS_RED,
    "white": BLOCK_CLASS_WHITE,
}

YOLO_CLASS_IDS = {
    "red_bottom_right": 0,
    "red_bottom_left": 1,
    "red_top_right": 2,
    "red_top_left": 3,
    "red": 4,
    "white": 5,
}


@dataclass(frozen=True)
class GridReconstructionResult:
    """Reconstructed grid and explicit validity information."""

    matrix: list[list[int | None]]
    valid: bool
    errors: tuple[str, ...] = ()


def map_detection_class(detection: Detection) -> int:
    """Map one YOLO detection to a pattern-bank class ID."""
    if not isinstance(detection, Detection):
        raise TypeError("detection must be a Detection")

    expected_id = YOLO_CLASS_IDS.get(detection.class_name)
    if expected_id is None:
        raise ValueError(
            f"Unknown YOLO class name: {detection.class_name}"
        )
    if detection.class_id != expected_id:
        raise ValueError(
            f"YOLO class ID does not match class name: "
            f"{detection.class_id} != {expected_id}"
        )
    return YOLO_CLASS_TO_PATTERN_CLASS[detection.class_name]


class GridReconstructor:
    """Map detections into an explicitly supplied 2x2 board geometry."""

    def __init__(self, grid_bounds: tuple[int, int, int, int]):
        if (
            not isinstance(grid_bounds, tuple)
            or len(grid_bounds) != 4
            or any(type(value) is not int for value in grid_bounds)
        ):
            raise TypeError(
                "grid_bounds must be a tuple[int, int, int, int]"
            )

        x, y, width, height = grid_bounds
        if x < 0 or y < 0:
            raise ValueError("grid_bounds origin must be nonnegative")
        if width <= 0 or height <= 0:
            raise ValueError("grid_bounds dimensions must be positive")
        self.grid_bounds = grid_bounds

    def reconstruct(
        self,
        detections: list[Detection],
        frame_size: tuple[int, int] | None = None,
    ) -> GridReconstructionResult:
        """Return a 2x2 matrix using detection centers and board geometry."""
        if not isinstance(detections, list):
            raise TypeError("detections must be a list")
        if frame_size is not None:
            self._validate_frame_size(frame_size)
            self._validate_grid_bounds_against_frame(frame_size)

        matrix = [[None, None], [None, None]]
        errors = []
        occupied = {}

        for detection in detections:
            pattern_class = map_detection_class(detection)
            self._validate_bbox(detection.bbox_xyxy, frame_size)
            row, column = self._cell_for_detection(detection)
            if row is None:
                errors.append("detection outside grid bounds")
                continue

            cell = (row, column)
            if cell in occupied:
                errors.append(
                    f"multiple detections in cell [{row}][{column}]"
                )
                continue
            occupied[cell] = True
            matrix[row][column] = pattern_class

        for row in range(2):
            for column in range(2):
                if matrix[row][column] is None:
                    errors.append(f"missing cell [{row}][{column}]")

        fixed_result = GridReconstructionResult(
            matrix=matrix,
            valid=not errors,
            errors=tuple(errors),
        )
        if fixed_result.valid:
            return fixed_result

        adaptive_candidates = []
        if len(detections) >= 4:
            for candidate in combinations(detections, 4):
                adaptive = self._reconstruct_from_centers(list(candidate))
                if adaptive is not None:
                    confidence = sum(
                        detection.confidence for detection in candidate
                    )
                    adaptive_candidates.append((confidence, adaptive))
        if adaptive_candidates:
            adaptive_candidates.sort(key=lambda item: item[0], reverse=True)
            if (
                len(adaptive_candidates) > 1
                and adaptive_candidates[0][0]
                - adaptive_candidates[1][0]
                <= 0.1
            ):
                return GridReconstructionResult(
                    matrix=matrix,
                    valid=False,
                    errors=tuple(errors) + (
                        "adaptive 2x2 geometry is ambiguous",
                    ),
                )
            return adaptive_candidates[0][1]
        return GridReconstructionResult(
            matrix=matrix,
            valid=False,
            errors=tuple(errors) + (
                "adaptive 2x2 geometry is inconsistent",
            ),
        )

    def _reconstruct_from_centers(self, detections):
        """Infer four cells from centers when fixed ROI mapping fails.

        This adapts OAMP's positional ordering while retaining the project's
        explicit four-cell contract. It is deliberately limited to exactly
        four detections and never fills a missing cell.
        """
        centers = []
        for detection in detections:
            x1, y1, x2, y2 = detection.bbox_xyxy
            centers.append(((x1 + x2) / 2, (y1 + y2) / 2))

        x_labels, x_gap = self._axis_groups(
            [center[0] for center in centers]
        )
        y_labels, y_gap = self._axis_groups(
            [center[1] for center in centers]
        )
        if x_labels is None or y_labels is None:
            return None

        matrix = [[None, None], [None, None]]
        occupied = set()
        for index, detection in enumerate(detections):
            cell = (y_labels[index], x_labels[index])
            if cell in occupied:
                return None
            occupied.add(cell)
            matrix[cell[0]][cell[1]] = map_detection_class(detection)

        if len(occupied) != 4:
            return None

        # The two rows and columns must have comparable orientation. This
        # rejects collinear or near-duplicate center layouts without adding a
        # camera-specific pixel threshold.
        if min(x_gap, y_gap) <= 0 or not math.isfinite(x_gap + y_gap):
            return None
        return GridReconstructionResult(
            matrix=matrix,
            valid=True,
            errors=(),
        )

    @staticmethod
    def _axis_groups(values):
        """Split four coordinates into two stable low/high groups."""
        ordered = sorted((value, index) for index, value in enumerate(values))
        first = ordered[:2]
        second = ordered[2:]
        first_center = sum(value for value, _ in first) / 2
        second_center = sum(value for value, _ in second) / 2
        gap = second_center - first_center
        tolerance = gap * 0.45
        if gap <= 0:
            return None, gap
        if (
            abs(first[0][0] - first[1][0]) > tolerance
            or abs(second[0][0] - second[1][0]) > tolerance
        ):
            return None, gap
        labels = [None] * 4
        for _, index in first:
            labels[index] = 0
        for _, index in second:
            labels[index] = 1
        return labels, gap

    @staticmethod
    def _validate_frame_size(frame_size):
        if (
            not isinstance(frame_size, tuple)
            or len(frame_size) != 2
            or any(type(value) is not int for value in frame_size)
        ):
            raise TypeError("frame_size must be a tuple[int, int]")
        if any(value <= 0 for value in frame_size):
            raise ValueError("frame_size dimensions must be positive")

    @staticmethod
    def _validate_bbox(bbox, frame_size):
        if (
            not isinstance(bbox, tuple)
            or len(bbox) != 4
            or any(type(value) is not int for value in bbox)
        ):
            raise ValueError("detection bbox must be tuple[int, int, int, int]")
        x1, y1, x2, y2 = bbox
        if x2 <= x1 or y2 <= y1:
            raise ValueError("detection bbox must have positive area")
        if frame_size is not None:
            frame_width, frame_height = frame_size
            if x1 < 0 or y1 < 0 or x2 > frame_width or y2 > frame_height:
                raise ValueError("detection bbox is outside frame bounds")

    def _validate_grid_bounds_against_frame(self, frame_size):
        frame_width, frame_height = frame_size
        x, y, width, height = self.grid_bounds
        if x + width > frame_width or y + height > frame_height:
            raise ValueError(
                "grid_bounds must fit within frame_size"
            )

    def _cell_for_detection(self, detection):
        x, y, width, height = self.grid_bounds
        x1, y1, x2, y2 = detection.bbox_xyxy
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        if not (x <= center_x < x + width and y <= center_y < y + height):
            return None, None

        column = int((center_x - x) * 2 / width)
        row = int((center_y - y) * 2 / height)
        return row, column
