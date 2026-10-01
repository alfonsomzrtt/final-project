"""
Grid mapping.

This module divides the detected block region into
a regular grid of cells.
"""

import cv2

from config.constants import SUPPORTED_GRID_SIZES


class GridMapper:
    def __init__(self, grid_size: int = 2):
        self.grid_size = grid_size
        self._validate_grid_size()

    def _validate_grid_size(self):
        """Validate the configured grid size."""

        if self.grid_size not in SUPPORTED_GRID_SIZES:
            raise ValueError(
                f"Unsupported grid size: {self.grid_size}"
            )

    def resize_region(self, mask, size: int = 600):
        """Resize the detected region to a square image."""

        if mask is None:
            raise ValueError("Mask cannot be None.")

        return cv2.resize(
            mask,
            (size, size),
        )

    def split_cells(self, region):
        """
        Split the region into equally sized grid cells.

        Returns:
            list[list]:
                Two-dimensional list containing the grid cells.
        """

        if region is None:
            raise ValueError("Region cannot be None.")

        height, width = region.shape[:2]

        cell_height = height // self.grid_size
        cell_width = width // self.grid_size

        cells = []

        for row in range(self.grid_size):
            row_cells = []

            for column in range(self.grid_size):
                y_start = row * cell_height
                y_end = (
                    (row + 1) * cell_height
                    if row < self.grid_size - 1
                    else height
                )

                x_start = column * cell_width
                x_end = (
                    (column + 1) * cell_width
                    if column < self.grid_size - 1
                    else width
                )

                cell = region[
                    y_start:y_end,
                    x_start:x_end,
                ]

                row_cells.append(cell)

            cells.append(row_cells)

        return cells

    def map(self, mask, size: int = 600):
        """
        Resize the detected region and divide it into grid cells.

        Returns:
            list[list]:
                Two-dimensional grid of image cells.
        """

        resized_region = self.resize_region(
            mask,
            size,
        )

        return self.split_cells(resized_region)