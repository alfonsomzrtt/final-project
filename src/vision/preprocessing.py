"""
Image preprocessing.

This module prepares camera frames for further computer vision processing.
"""

import cv2
import numpy as np


class Preprocessor:
    def __init__(self):
        self.kernel = np.ones((5, 5), np.uint8)

    def to_hsv(self, frame):
        """Convert a BGR frame to HSV."""

        if frame is None:
            raise ValueError("Frame cannot be None.")

        return cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    def create_red_mask(self, hsv_frame):
        """Create a binary mask for red regions."""

        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])

        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])

        mask1 = cv2.inRange(
            hsv_frame,
            lower_red1,
            upper_red1,
        )

        mask2 = cv2.inRange(
            hsv_frame,
            lower_red2,
            upper_red2,
        )

        return mask1 + mask2

    def remove_noise(self, mask):
        """Remove small noise from a binary mask."""

        return cv2.morphologyEx(
            mask,
            cv2.MORPH_OPEN,
            self.kernel,
        )

    def process(self, frame):
        """Run the preprocessing pipeline."""

        hsv_frame = self.to_hsv(frame)
        red_mask = self.create_red_mask(hsv_frame)
        clean_mask = self.remove_noise(red_mask)

        return clean_mask