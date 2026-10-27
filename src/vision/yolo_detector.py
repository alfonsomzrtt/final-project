"""Standalone YOLO ONNX adapter for OpenCV BGR frames."""

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


MODEL_INPUT_SIZE = (640, 640)
MODEL_INPUT_NAME = "images"
MODEL_OUTPUT_NAME = "output0"
CLASS_NAMES = (
    "red_bottom_right",
    "red_bottom_left",
    "red_top_right",
    "red_top_left",
    "red",
    "white",
)


@dataclass(frozen=True)
class Detection:
    """One decoded YOLO detection in original-frame coordinates."""

    class_id: int
    class_name: str
    confidence: float
    bbox_xyxy: tuple[int, int, int, int]


class YoloDetector:
    """Load and run the project's fixed-shape YOLO ONNX model."""

    def __init__(
        self,
        model_path: str | Path | None = None,
        confidence_threshold: float = 0.25,
        nms_threshold: float = 0.45,
    ):
        if not 0.0 <= confidence_threshold <= 1.0:
            raise ValueError("confidence_threshold must be between 0 and 1")
        if not 0.0 <= nms_threshold <= 1.0:
            raise ValueError("nms_threshold must be between 0 and 1")

        if model_path is None:
            model_path = (
                Path(__file__).resolve().parents[2]
                / "models"
                / "baseline-52-4rd.onnx"
            )
        self.model_path = Path(model_path).resolve()
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold

        try:
            self.net = cv2.dnn.readNetFromONNX(str(self.model_path))
        except Exception as exc:
            raise RuntimeError(
                f"Unable to load YOLO ONNX model: {self.model_path}"
            ) from exc

    def detect(self, frame) -> list[Detection]:
        """Run inference on one OpenCV BGR frame."""
        self._validate_frame(frame)
        height, width = frame.shape[:2]
        blob, scale, pad_x, pad_y = self._preprocess(frame)

        try:
            self.net.setInput(blob, MODEL_INPUT_NAME)
            output = self.net.forward(MODEL_OUTPUT_NAME)
        except Exception as exc:
            raise RuntimeError("YOLO ONNX inference failed") from exc

        candidates = self._decode_output(
            output,
            width=width,
            height=height,
            scale=scale,
            pad_x=pad_x,
            pad_y=pad_y,
        )
        return self._class_aware_nms(candidates)

    @staticmethod
    def _validate_frame(frame):
        if not isinstance(frame, np.ndarray):
            raise ValueError("frame must be a numpy array")
        if frame.ndim != 3 or frame.shape[2] != 3:
            raise ValueError("frame must be a three-channel BGR image")
        if frame.shape[0] <= 0 or frame.shape[1] <= 0:
            raise ValueError("frame dimensions must be positive")

    @staticmethod
    def _preprocess(frame):
        height, width = frame.shape[:2]
        input_width, input_height = MODEL_INPUT_SIZE
        scale = min(input_width / width, input_height / height)
        resized_width = max(1, round(width * scale))
        resized_height = max(1, round(height * scale))
        resized = cv2.resize(
            frame,
            (resized_width, resized_height),
            interpolation=cv2.INTER_LINEAR,
        )

        pad_x = (input_width - resized_width) / 2
        pad_y = (input_height - resized_height) / 2
        canvas = np.full(
            (input_height, input_width, 3),
            114,
            dtype=np.uint8,
        )
        left = int(np.floor(pad_x))
        top = int(np.floor(pad_y))
        pad_x = left
        pad_y = top
        canvas[
            top:top + resized_height,
            left:left + resized_width,
        ] = resized

        rgb = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
        blob = rgb.astype(np.float32) / 255.0
        blob = np.transpose(blob, (2, 0, 1))[None, ...]
        return np.ascontiguousarray(blob), scale, pad_x, pad_y

    def _decode_output(
        self,
        output,
        *,
        width,
        height,
        scale,
        pad_x,
        pad_y,
    ):
        values = np.asarray(output)
        if values.shape == (1, 10, 8400):
            values = values[0].T
        elif values.shape == (10, 8400):
            values = values.T
        elif values.shape == (1, 8400, 10):
            values = values[0]
        elif values.shape != (8400, 10):
            raise ValueError(
                f"unexpected YOLO output shape: {tuple(values.shape)}"
            )
        if values.shape[1] != 4 + len(CLASS_NAMES):
            raise ValueError(
                f"unexpected YOLO attribute count: {values.shape[1]}"
            )

        class_scores = values[:, 4:]
        class_ids = np.argmax(class_scores, axis=1)
        confidences = class_scores[
            np.arange(class_scores.shape[0]),
            class_ids,
        ]
        # Promote the scalar threshold so float32 scores retain the old
        # per-row Python-float comparison semantics at boundary values.
        selected = confidences >= np.float64(self.confidence_threshold)
        if not np.any(selected):
            return []

        selected_ids = class_ids[selected]
        selected_confidences = confidences[selected]
        coordinates = values[selected, :4].astype(np.float64, copy=False)
        centers = coordinates[:, :2]
        half_sizes = coordinates[:, 2:] / 2.0
        top_left = (centers - half_sizes - (pad_x, pad_y)) / scale
        bottom_right = (centers + half_sizes - (pad_x, pad_y)) / scale
        boxes = np.concatenate((top_left, bottom_right), axis=1)
        boxes = np.rint(boxes)
        boxes[:, [0, 2]] = np.clip(boxes[:, [0, 2]], 0, width)
        boxes[:, [1, 3]] = np.clip(boxes[:, [1, 3]], 0, height)
        boxes = boxes.astype(np.int64, copy=False)
        valid = (
            (boxes[:, 2] > boxes[:, 0])
            & (boxes[:, 3] > boxes[:, 1])
        )

        detections = []
        for class_id, confidence, box in zip(
            selected_ids[valid],
            selected_confidences[valid],
            boxes[valid],
        ):
            bbox_xyxy: tuple[int, int, int, int] = (
                int(box[0]),
                int(box[1]),
                int(box[2]),
                int(box[3]),
            )
            detections.append(
                Detection(
                    class_id=int(class_id),
                    class_name=CLASS_NAMES[int(class_id)],
                    confidence=float(confidence),
                    bbox_xyxy=bbox_xyxy,
                )
            )
        return detections

    def _class_aware_nms(self, detections):
        kept = []
        for class_id in range(len(CLASS_NAMES)):
            class_detections = sorted(
                (item for item in detections if item.class_id == class_id),
                key=lambda item: item.confidence,
                reverse=True,
            )
            while class_detections:
                current = class_detections.pop(0)
                kept.append(current)
                class_detections = [
                    item
                    for item in class_detections
                    if self._iou(current.bbox_xyxy, item.bbox_xyxy)
                    <= self.nms_threshold
                ]
        return sorted(kept, key=lambda item: item.confidence, reverse=True)

    @staticmethod
    def _iou(first, second):
        left = max(first[0], second[0])
        top = max(first[1], second[1])
        right = min(first[2], second[2])
        bottom = min(first[3], second[3])
        intersection = max(0, right - left) * max(0, bottom - top)
        first_area = (first[2] - first[0]) * (first[3] - first[1])
        second_area = (second[2] - second[0]) * (second[3] - second[1])
        union = first_area + second_area - intersection
        return intersection / union if union else 0.0