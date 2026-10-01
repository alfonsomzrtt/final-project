"""
Pattern matching.

This module compares a detected block-design pattern
with a target pattern.
"""

import numpy as np


class PatternMatcher:
    def __init__(self, match_threshold: float = 1.0):
        self.match_threshold = match_threshold

    def _validate_patterns(
        self,
        detected_pattern,
        target_pattern,
    ):
        """Validate the input patterns."""

        if detected_pattern is None:
            raise ValueError(
                "Detected pattern cannot be None."
            )

        if target_pattern is None:
            raise ValueError(
                "Target pattern cannot be None."
            )

        detected = np.asarray(detected_pattern)
        target = np.asarray(target_pattern)

        if detected.shape != target.shape:
            raise ValueError(
                "Detected pattern and target pattern "
                "must have the same shape."
            )

        return detected, target

    def calculate_accuracy(
        self,
        detected_pattern,
        target_pattern,
    ):
        """
        Calculate cell-based pattern accuracy.

        Returns:
            float:
                Accuracy between 0.0 and 1.0.
        """

        detected, target = self._validate_patterns(
            detected_pattern,
            target_pattern,
        )

        total_cells = detected.size

        if total_cells == 0:
            raise ValueError(
                "Pattern cannot be empty."
            )

        matching_cells = np.sum(
            detected == target
        )

        return float(
            matching_cells / total_cells
        )

    def is_match(
        self,
        detected_pattern,
        target_pattern,
    ):
        """Return True if the pattern meets the match threshold."""

        accuracy = self.calculate_accuracy(
            detected_pattern,
            target_pattern,
        )

        return accuracy >= self.match_threshold

    def match(
        self,
        detected_pattern,
        target_pattern,
    ):
        """
        Compare a detected pattern with a target pattern.

        Returns:
            dict:
                Matching result and accuracy.
        """

        accuracy = self.calculate_accuracy(
            detected_pattern,
            target_pattern,
        )

        return {
            "accuracy": accuracy,
            "is_match": accuracy >= self.match_threshold,
        }