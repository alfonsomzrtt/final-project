"""
Block detector.

This module detects the region containing block-design pieces
from a binary mask.
"""

import cv2


class BlockDetector:
    def __init__(self, min_contour_area: int = 500):
        self.min_contour_area = min_contour_area

    def find_valid_contours(self, mask):
        """Find contours that are large enough to be considered blocks."""

        if mask is None:
            raise ValueError("Mask cannot be None.")

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        return [
            contour
            for contour in contours
            if cv2.contourArea(contour) > self.min_contour_area
        ]

    def get_bounding_box(self, contours):
        """
        Calculate the global bounding box containing all valid contours.

        Returns:
            tuple[int, int, int, int] | None:
                (x, y, width, height), or None if no valid contours exist.
        """

        if not contours:
            return None

        min_x = float("inf")
        min_y = float("inf")
        max_x = 0
        max_y = 0

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x + w)
            max_y = max(max_y, y + h)

        x = int(min_x)
        y = int(min_y)
        width = int(max_x - min_x)
        height = int(max_y - min_y)

        return x, y, width, height

    def is_valid_region(
        self,
        bounding_box,
        min_width: int = 150,
        min_height: int = 150,
    ):
        """Check whether the detected region is large enough."""

        if bounding_box is None:
            return False

        _, _, width, height = bounding_box

        return (
            width > min_width
            and height > min_height
        )

    def detect(self, mask):
        """
        Detect the block region from a binary mask.

        Returns:
            tuple[int, int, int, int] | None:
                Valid bounding box, or None if no region is detected.
        """

        contours = self.find_valid_contours(mask)

        bounding_box = self.get_bounding_box(contours)

        if not self.is_valid_region(bounding_box):
            return None

        return bounding_box