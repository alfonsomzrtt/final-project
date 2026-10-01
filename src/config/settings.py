"""
Application settings.

This module contains runtime and environment-related configuration
used by the application.

Unlike constants.py, values in this module may be changed depending
on the deployment environment, hardware, or development setup.
"""


# ============================================================
# APPLICATION
# ============================================================

import os 
APP_NAME = "Block Design Puzzle Game"

DEBUG = True


# ============================================================
# CAMERA
# ============================================================

CAMERA_INDEX = 1

CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

CAMERA_FPS = 30

# Camera adjustment configuration

CAMERA_SLIDER_BOUNDS = {
    "brightness": (64, 191),
    "contrast": (77, 191),
    "saturation": (77, 166),
}

CAMERA_SLIDER_MIN = 0
CAMERA_SLIDER_MAX = 255
CAMERA_SLIDER_DEFAULT = 128


# ============================================================
# VISION
# ============================================================

DETECTION_FPS = 10


# ============================================================
# GAME
# ============================================================

DEFAULT_DIFFICULTY = "easy"

#API Configuration
API_BASE_URL = os.getenv(
    "BDT_API_BASE_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

WEBSOCKET_URL = os.getenv(
    "BDT_WEBSOCKET_URL",
    "ws://127.0.0.1:8000/ws",
)

API_TIMEOUT = float(os.getenv("BDT_API_TIMEOUT", "10"))