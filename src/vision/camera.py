"""
Camera interface.

This module handles camera initialization and frame acquisition.
It does not perform image processing, object detection,
or GUI operations.
"""

import cv2
import subprocess

from config.settings import (
    CAMERA_INDEX,
    CAMERA_WIDTH,
    CAMERA_HEIGHT,
    CAMERA_FPS,
)


class Camera:
    def __init__(
        self,
        camera_index: int = CAMERA_INDEX,
        width: int = CAMERA_WIDTH,
        height: int = CAMERA_HEIGHT,
        fps: int = CAMERA_FPS,
    ):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.fps = fps

        self.capture = None

    def open(self) -> bool:
        """Open the camera."""

        self.capture = cv2.VideoCapture(self.camera_index)

        if not self.capture.isOpened():
            self.capture = None
            return False

        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.capture.set(cv2.CAP_PROP_FPS, self.fps)

        return True

    def read(self):
        """Read one frame from the camera."""

        if self.capture is None:
            raise RuntimeError("Camera is not open.")

        success, frame = self.capture.read()

        if not success:
            return None

        return frame


    def set_adjustment(self, name: str, value: int) -> bool:
        """Set camera controls through V4L2."""

        if name not in {"brightness", "contrast", "saturation"}:
            raise ValueError(f"Unsupported adjustment: {name}")

        if not 0 <= value <= 255:
            raise ValueError("Value must be between 0 and 255.")

        if not self.is_opened():
            raise RuntimeError("Camera is not open.")

        result = subprocess.run(
            [
                "v4l2-ctl",
                "-d", "/dev/video2",
                f"--set-ctrl={name}={value}",
            ],
            capture_output=True,
            text=True,
            timeout=2,
        )

        if result.returncode != 0:
            raise RuntimeError(
                result.stderr.strip() or
                f"Failed to set {name}={value}"
            )

        return True


    def is_opened(self) -> bool:
        """Return True if the camera is currently open."""

        return (
            self.capture is not None
            and self.capture.isOpened()
        )

    def release(self):
        """Release the camera resource."""

        if self.capture is not None:
            self.capture.release()
            self.capture = None

