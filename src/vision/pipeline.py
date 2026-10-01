"""
Vision pipeline.

This module coordinates the complete computer vision
processing pipeline for Block Design pattern detection.
"""

from dataclasses import dataclass

from vision.preprocessing import Preprocessor
from vision.detector import BlockDetector
from vision.grid_mapper import GridMapper
from vision.orientation import OrientationClassifier
from vision.pattern_matcher import PatternMatcher


@dataclass
class VisionResult:
    """Result produced by the vision pipeline."""

    detected_pattern: list | None
    accuracy: float
    is_match: bool
    bounding_box: tuple | None


class VisionPipeline:
    def __init__(self):
        self.preprocessor = Preprocessor()
        self.detector = BlockDetector()
        self.orientation_classifier = OrientationClassifier()
        self.pattern_matcher = PatternMatcher()

    def process(self, frame, target_pattern):
        """
        Process one camera frame against a target pattern.

        Returns:
            VisionResult:
                Detection result, accuracy, match status,
                and detected bounding box.
        """

        # STEP 1: PREPROCESSING
        mask = self.preprocessor.process(frame)

        # STEP 2: OBJECT / REGION DETECTION
        bounding_box = self.detector.detect(mask)

        if bounding_box is None:
            return VisionResult(
                detected_pattern=None,
                accuracy=0.0,
                is_match=False,
                bounding_box=None,
            )

        # STEP 3: CROP DETECTED REGION
        x, y, width, height = bounding_box

        roi = mask[
            y:y + height,
            x:x + width,
        ]

        # STEP 4: GRID MAPPING
        target_rows = len(target_pattern)

        grid_mapper = GridMapper(
            grid_size=target_rows
        )

        cells = grid_mapper.map(roi)

        # STEP 5: CELL CLASSIFICATION
        detected_pattern = (
            self.orientation_classifier.classify_grid(
                cells
            )
        )

        # STEP 6: PATTERN MATCHING
        match_result = self.pattern_matcher.match(
            detected_pattern,
            target_pattern,
        )

        return VisionResult(
            detected_pattern=detected_pattern,
            accuracy=match_result["accuracy"],
            is_match=match_result["is_match"],
            bounding_box=bounding_box,
        )