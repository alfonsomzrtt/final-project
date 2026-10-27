
import time
import logging
from datetime import datetime
from pathlib import Path
from queue import Empty, Full, Queue
from threading import Event, Lock, Thread

import cv2
import numpy as np

from PyQt5.QtCore import QThread, pyqtSignal
from config.settings import DETECTION_FPS
from vision.camera import Camera
from vision.grid_pattern_checker import GridPatternChecker
from vision.pattern_stabilizer import PatternStabilizer
from vision.yolo_detector import YoloDetector


VISION_TARGET_UNAVAILABLE = "target_unavailable"
VISION_GEOMETRY_UNCONFIGURED = "geometry_unconfigured"
VISION_PENDING = "pending"
VISION_STABLE = "stable"
VISION_MISMATCH = "mismatch"
VISION_INVALID_RECONSTRUCTION = "invalid_reconstruction"
VISION_ERROR = "vision_error"

logger = logging.getLogger(__name__)


class VisionFrameResult:
    """Result emitted for one processed inference frame."""

    def __init__(
        self,
        frame_id,
        status,
        stabilization=None,
        error=None,
        target_pattern=None,
        target_generation=None,
    ):
        self.frame_id = frame_id
        self.status = status
        self.stabilization = stabilization
        self.error = error
        self.target_pattern = target_pattern
        self.target_generation = target_generation


class CameraWorker(QThread):
    """Capture camera frames outside the GUI thread."""

    frame_ready = pyqtSignal(object)
    vision_result = pyqtSignal(object)
    status_changed = pyqtSignal(str, str)
    error = pyqtSignal(str)

    def __init__(
        self,
        parent=None,
        detector_factory=YoloDetector,
        grid_bounds=None,
        minimum_matches=3,
        raw_frame_snapshot_dir=None,
    ):
        super().__init__(parent)
        self._stop_event = Event()
        self._adjustments = Queue()
        self._detector_factory = detector_factory
        self._inference_queue = Queue(maxsize=1)
        self._frame_id = 0
        self._last_processed_frame_id = 0
        self._vision_lock = Lock()
        self._grid_bounds = grid_bounds
        self._target_pattern = None
        self._vision_target_generation = 0
        self._grid_checker = (
            GridPatternChecker(grid_bounds)
            if grid_bounds is not None
            else None
        )
        self._pattern_stabilizer = PatternStabilizer(minimum_matches)
        self._inference_thread = None
        self._annotated_frame = None
        self._annotated_lock = Lock()
        self._last_inference_error = None
        self._last_vision_log_key = None
        self._raw_frame_snapshot_dir = (
            Path(raw_frame_snapshot_dir)
            if raw_frame_snapshot_dir is not None
            else None
        )
        self._raw_frame_snapshot_path = None

    def set_vision_target(self, target_pattern):
        """Set the active target and reset temporal vision state."""
        with self._vision_lock:
            self._target_pattern = target_pattern
            self._vision_target_generation += 1
            self._pattern_stabilizer.reset()

    def set_grid_bounds(self, grid_bounds):
        """Set explicit board geometry and reset temporal vision state."""
        checker = (
            GridPatternChecker(grid_bounds)
            if grid_bounds is not None
            else None
        )
        with self._vision_lock:
            self._grid_bounds = grid_bounds
            self._grid_checker = checker
            self._pattern_stabilizer.reset()

    def set_adjustment(self, name: str, value: int):
        self._adjustments.put((name, value))

    def _apply_adjustments(self, camera):
        while True:
            try:
                name, value = self._adjustments.get_nowait()
            except Empty:
                break

            try:
                success = camera.set_adjustment(name, value)
                if not success:
                    self.error.emit(
                        f"Camera rejected {name}={value}"
                    )
            except Exception as exc:
                self.error.emit(f"{name}: {exc}")

    def _start_inference(self):
        """Start model loading and inference outside the capture loop."""
        try:
            detector = self._detector_factory()
        except Exception as exc:
            self.error.emit(f"YOLO model unavailable: {exc}")
            return

        self._inference_thread = Thread(
            target=self._inference_loop,
            args=(detector,),
            name="yolo-inference",
            daemon=True,
        )
        self._inference_thread.start()

    def _inference_loop(self, detector):
        while not self._stop_event.is_set() or not self._inference_queue.empty():
            try:
                frame_id, frame = self._inference_queue.get(timeout=0.1)
            except Empty:
                continue

            if frame_id <= self._last_processed_frame_id:
                continue
            self._last_processed_frame_id = frame_id

            try:
                detections = detector.detect(frame)
                vision_result = self._process_vision_result(
                    frame_id,
                    detections,
                    frame.shape[1::-1],
                )
                self.vision_result.emit(vision_result)
                annotated = self._annotate_frame(frame, detections)
                with self._annotated_lock:
                    self._annotated_frame = annotated
                self._last_inference_error = None
            except Exception as exc:
                message = f"YOLO inference failed: {exc}"
                if message != self._last_inference_error:
                    self._last_inference_error = message
                    self.error.emit(message)
                self.vision_result.emit(
                    VisionFrameResult(
                        frame_id=frame_id,
                        status=VISION_ERROR,
                        error=str(exc),
                    )
                )

    def _save_raw_frame(self, frame_id, frame):
        """Save one original capture frame for board-bound calibration."""
        if (
            self._raw_frame_snapshot_dir is None
            or self._raw_frame_snapshot_path is not None
        ):
            return False

        if not isinstance(frame, np.ndarray):
            logger.warning(
                "raw vision frame rejected frame_id=%s: not an ndarray",
                frame_id,
            )
            return False
        if (
            frame.ndim not in (2, 3)
            or frame.shape[0] <= 0
            or frame.shape[1] <= 0
            or frame.dtype != np.uint8
            or (frame.ndim == 3 and frame.shape[2] not in (1, 3, 4))
        ):
            logger.warning(
                "raw vision frame rejected frame_id=%s shape=%s dtype=%s",
                frame_id,
                frame.shape,
                frame.dtype,
            )
            return False

        raw_frame = frame.copy()
        mean, standard_deviation = cv2.meanStdDev(raw_frame)
        mean_value = float(np.mean(mean))
        standard_deviation_value = float(np.mean(standard_deviation))
        if not np.any(raw_frame):
            logger.warning(
                "raw vision frame rejected frame_id=%s shape=%s "
                "mean=%.3f std=%.3f: all pixels are zero",
                frame_id,
                raw_frame.shape,
                mean_value,
                standard_deviation_value,
            )
            return False

        snapshot_dir = self._raw_frame_snapshot_dir
        try:
            snapshot_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = snapshot_dir.resolve() / (
                f"vision_raw_frame_{timestamp}_frame_{frame_id}.png"
            )
            if not cv2.imwrite(str(path), raw_frame):
                logger.warning(
                    "raw vision frame write failed path=%s resolution=%sx%s "
                    "mean=%.3f std=%.3f",
                    path,
                    raw_frame.shape[1],
                    raw_frame.shape[0],
                    mean_value,
                    standard_deviation_value,
                )
                return False
        except Exception as exc:
            logger.warning(
                "raw vision frame write failed frame_id=%s error=%s",
                frame_id,
                exc,
            )
            return False

        self._raw_frame_snapshot_path = path
        logger.warning(
            "saved raw vision frame path=%s resolution=%sx%s "
            "mean=%.3f std=%.3f",
            path,
            raw_frame.shape[1],
            raw_frame.shape[0],
            mean_value,
            standard_deviation_value,
        )
        return True

    def _process_vision_result(self, frame_id, detections, frame_size):
        with self._vision_lock:
            target_pattern = self._target_pattern
            target_generation = self._vision_target_generation
            checker = self._grid_checker
            stabilizer = self._pattern_stabilizer

        if target_pattern is None:
            result = VisionFrameResult(
                frame_id,
                VISION_TARGET_UNAVAILABLE,
                error="vision target pattern is not configured",
                target_generation=target_generation,
            )
            self._log_vision_diagnostic(
                result,
                detections,
                frame_size,
                checker,
                target_pattern,
            )
            return result
        if checker is None:
            result = VisionFrameResult(
                frame_id,
                VISION_GEOMETRY_UNCONFIGURED,
                error="vision grid bounds are not configured",
                target_pattern=target_pattern,
                target_generation=target_generation,
            )
            self._log_vision_diagnostic(
                result,
                detections,
                frame_size,
                checker,
                target_pattern,
            )
            return result

        with self._vision_lock:
            if target_generation != self._vision_target_generation:
                result = VisionFrameResult(
                    frame_id,
                    VISION_TARGET_UNAVAILABLE,
                    error="vision target changed while frame was processing",
                    target_pattern=target_pattern,
                    target_generation=target_generation,
                )
                self._log_vision_diagnostic(
                    result,
                    detections,
                    frame_size,
                    checker,
                    target_pattern,
                )
                return result
            check_result = checker.check(
                detections,
                target_pattern,
                frame_size=frame_size,
            )
            stabilization = stabilizer.update(
                check_result,
                target_pattern,
            )
        if check_result.status == "mismatch":
            status = VISION_MISMATCH
        elif check_result.status == "invalid_reconstruction":
            status = VISION_INVALID_RECONSTRUCTION
        else:
            status = stabilization.status
        result = VisionFrameResult(
            frame_id,
            status,
            stabilization=stabilization,
            target_pattern=target_pattern,
            target_generation=target_generation,
        )
        self._log_vision_diagnostic(
            result,
            detections,
            frame_size,
            checker,
            target_pattern,
            check_result,
        )
        return result

    def _log_vision_diagnostic(
        self,
        result,
        detections,
        frame_size,
        checker,
        target_pattern,
        check_result=None,
    ):
        """Log one compact diagnostic record when the observable state changes."""
        matrix = (
            check_result.detected_pattern
            if check_result is not None
            else None
        )
        errors = (
            check_result.errors
            if check_result is not None
            else (result.error,) if result.error else ()
        )
        consecutive = (
            result.stabilization.consecutive_matches
            if result.stabilization is not None
            else 0
        )
        detection_diagnostics = self._describe_detections(
            detections,
            checker,
            frame_size,
        )
        key = (
            result.status,
            tuple(
                tuple(row) for row in matrix
            ) if matrix is not None else None,
            tuple(tuple(row) for row in target_pattern)
            if target_pattern is not None else None,
            tuple(errors),
            repr(detection_diagnostics),
        )
        if key == self._last_vision_log_key:
            return
        self._last_vision_log_key = key
        inside_count = sum(
            item["inside_roi"] for item in detection_diagnostics
        )
        outside_count = len(detection_diagnostics) - inside_count
        classes = [
            f"{item.class_name}#{getattr(item, 'class_id', '?')}"
            for item in detections
        ]
        logger.warning(
            "vision frame_id=%s frame_size=%s detections=%d classes=%s "
            "grid_bounds=%s target=%s matrix=%s errors=%s status=%s "
            "consecutive_matches=%d inside_roi=%d outside_roi=%d "
            "detection_diagnostics=%s",
            result.frame_id,
            frame_size,
            len(detections),
            classes,
            checker.reconstructor.grid_bounds if checker else None,
            target_pattern,
            matrix,
            errors,
            result.status,
            consecutive,
            inside_count,
            outside_count,
            detection_diagnostics,
        )

    @staticmethod
    def _describe_detections(detections, checker, frame_size):
        """Describe ROI membership and cell mapping without changing results."""
        descriptions = []
        reconstructor = checker.reconstructor if checker else None
        for detection in detections:
            x1, y1, x2, y2 = detection.bbox_xyxy
            center = ((x1 + x2) / 2, (y1 + y2) / 2)
            item = {
                "class": (
                    f"{detection.class_name}#"
                    f"{getattr(detection, 'class_id', '?')}"
                ),
                "confidence": round(detection.confidence, 4),
                "bbox": detection.bbox_xyxy,
                "center": tuple(round(value, 1) for value in center),
                "inside_roi": False,
                "cell": None,
                "reason": None,
            }
            if reconstructor is None:
                item["reason"] = "grid bounds are not configured"
            else:
                row, column = reconstructor._cell_for_detection(detection)
                item["inside_roi"] = row is not None
                if item["inside_roi"]:
                    item["cell"] = (row, column)
                else:
                    item["reason"] = "detection center outside grid bounds"
            descriptions.append(item)
        return descriptions

    def _annotate_frame(self, frame, detections):
        """Draw detector output on a display-only copy."""
        annotated = frame.copy()
        for detection in detections:
            x1, y1, x2, y2 = detection.bbox_xyxy
            center_x = int(round((x1 + x2) / 2))
            center_y = int(round((y1 + y2) / 2))
            label = f"{detection.class_name} {detection.confidence:.2f}"
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.circle(
                annotated,
                (center_x, center_y),
                5,
                (255, 0, 255),
                -1,
            )
            cv2.putText(
                annotated,
                label,
                (x1, max(20, y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )
        return annotated

    def _submit_for_inference(self, frame):
        self._frame_id += 1
        item = (self._frame_id, frame.copy())
        try:
            self._inference_queue.put_nowait(item)
        except Full:
            try:
                self._inference_queue.get_nowait()
            except Empty:
                pass
            try:
                self._inference_queue.put_nowait(item)
            except Full:
                pass

    def run(self):
        camera = Camera()
        connected = False
        inference_interval = 1.0 / max(1, DETECTION_FPS)
        next_inference = 0.0

        try:
            if not camera.open():
                message = "Unable to open camera."
                self.status_changed.emit("error", message)
                self.error.emit(message)
                return

            connected = True
            self.status_changed.emit("connected", "")
            self._start_inference()

            while not self._stop_event.is_set():
                self._apply_adjustments(camera)

                frame = camera.read()
                if frame is None:
                    message = "Failed to read camera frame."
                    self.status_changed.emit("error", message)
                    self.error.emit(message)
                    break

                # Snapshot the exact capture buffer before it can be queued,
                # replaced, annotated, or otherwise delayed by inference.
                # _save_raw_frame deliberately leaves the path unset when a
                # frame is invalid or writing fails, so the next capture is
                # tried automatically.
                if self._raw_frame_snapshot_path is None:
                    self._save_raw_frame(self._frame_id + 1, frame)

                now = time.monotonic()
                if (
                    self._inference_thread is not None
                    and now >= next_inference
                ):
                    self._submit_for_inference(frame)
                    next_inference = now + inference_interval

                with self._annotated_lock:
                    display_frame = (
                        self._annotated_frame
                        if self._annotated_frame is not None
                        else frame
                    )
                self.frame_ready.emit(display_frame)

        except Exception as exc:
            message = str(exc)
            self.status_changed.emit("error", message)
            self.error.emit(message)

        finally:
            self._stop_event.set()
            if self._inference_thread is not None:
                self._inference_thread.join(timeout=2.0)
                self._inference_thread = None
            camera.release()

            if connected and self._stop_event.is_set():
                self.status_changed.emit("disconnected", "")

    def stop(self):
        self._stop_event.set()
