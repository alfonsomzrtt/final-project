"""
Block orientation and cell classification.

This module classifies individual grid cells based on
their red-pixel distribution.
"""

import cv2

from config.constants import (
    BLOCK_CLASS_RED,
    BLOCK_CLASS_WHITE,
    BLOCK_CLASS_RED_TOP_LEFT,
    BLOCK_CLASS_RED_TOP_RIGHT,
    BLOCK_CLASS_RED_BOTTOM_LEFT,
    BLOCK_CLASS_RED_BOTTOM_RIGHT,
)


class OrientationClassifier:
    def __init__(
        self,
        full_red_threshold: float = 0.80,
        white_threshold: float = 0.20,
    ):
        self.full_red_threshold = full_red_threshold
        self.white_threshold = white_threshold

    def calculate_red_ratio(self, cell):
        """Calculate the ratio of red pixels in a cell."""

        if cell is None:
            raise ValueError("Cell cannot be None.")

        total_pixels = cell.shape[0] * cell.shape[1]

        if total_pixels == 0:
            raise ValueError("Cell cannot be empty.")

        red_pixels = cv2.countNonZero(cell)

        return red_pixels / total_pixels

    def classify_full_or_empty(self, red_ratio: float):
        """Classify cells that are fully red or mostly white."""

        if red_ratio >= self.full_red_threshold:
            return BLOCK_CLASS_RED

        if red_ratio <= self.white_threshold:
            return BLOCK_CLASS_WHITE

        return None

    def classify_diagonal(self, cell):
        """
        Classify a partially red cell based on the distribution
        of red pixels across its four quadrants.
        """

        height, width = cell.shape[:2]

        mid_y = height // 2
        mid_x = width // 2

        top_left = cell[:mid_y, :mid_x]
        top_right = cell[:mid_y, mid_x:]
        bottom_left = cell[mid_y:, :mid_x]
        bottom_right = cell[mid_y:, mid_x:]

        ratios = {
            "top_left": self.calculate_red_ratio(top_left),
            "top_right": self.calculate_red_ratio(top_right),
            "bottom_left": self.calculate_red_ratio(bottom_left),
            "bottom_right": self.calculate_red_ratio(bottom_right),
        }

        quadrant = max(
            ratios,
            key=lambda key: ratios[key],
        )

        class_map = {
            "top_left": BLOCK_CLASS_RED_TOP_LEFT,
            "top_right": BLOCK_CLASS_RED_TOP_RIGHT,
            "bottom_left": BLOCK_CLASS_RED_BOTTOM_LEFT,
            "bottom_right": BLOCK_CLASS_RED_BOTTOM_RIGHT,
        }

        return class_map[quadrant]

    def classify_cell(self, cell):
        """Classify one grid cell."""

        red_ratio = self.calculate_red_ratio(cell)

        full_or_empty = self.classify_full_or_empty(
            red_ratio
        )

        if full_or_empty is not None:
            return full_or_empty

        return self.classify_diagonal(cell)

    def classify_grid(self, cells):
        """Classify every cell in a grid."""

        return [
            [
                self.classify_cell(cell)
                for cell in row
            ]
            for row in cells
        ]