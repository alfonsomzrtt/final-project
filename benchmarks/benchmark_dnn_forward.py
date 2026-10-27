"""Isolated OpenCV DNN benchmark for the project's YOLO ONNX model.

Run from the repository root:

    python benchmarks/benchmark_dnn_forward.py

Each thread configuration runs in a fresh subprocess so OpenCV global thread
state and allocator history do not contaminate another configuration.
"""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
MODEL_PATH = ROOT / "models" / "baseline-52-4rd.onnx"
FRAME_SHAPE = (720, 1280, 3)
WARMUP_ITERATIONS = 10
MEASURED_ITERATIONS = 50


def _stats(values: list[float]) -> dict[str, float]:
    return {
        "mean_ms": statistics.mean(values),
        "median_ms": statistics.median(values),
        "p95_ms": float(np.percentile(values, 95)),
        "min_ms": min(values),
        "max_ms": max(values),
    }


def _deterministic_frame() -> np.ndarray:
    height, width, _ = FRAME_SHAPE
    y, x = np.indices((height, width), dtype=np.uint16)
    frame = np.empty(FRAME_SHAPE, dtype=np.uint8)
    frame[:, :, 0] = (x * 3 + y) % 256
    frame[:, :, 1] = (x + y * 2) % 256
    frame[:, :, 2] = (x * 2 + y * 3) % 256
    return frame


def _available_dnn_options() -> dict[str, object]:
    backends = {
        name: getattr(cv2.dnn, name)
        for name in (
            "DNN_BACKEND_DEFAULT",
            "DNN_BACKEND_OPENCV",
            "DNN_BACKEND_CUDA",
            "DNN_BACKEND_INFERENCE_ENGINE",
            "DNN_BACKEND_HALIDE",
            "DNN_BACKEND_TIMVX",
            "DNN_BACKEND_WEBNN",
        )
        if hasattr(cv2.dnn, name)
    }
    targets = {
        name: getattr(cv2.dnn, name)
        for name in (
            "DNN_TARGET_CPU",
            "DNN_TARGET_CUDA",
            "DNN_TARGET_CUDA_FP16",
            "DNN_TARGET_OPENCL",
            "DNN_TARGET_OPENCL_FP16",
            "DNN_TARGET_MYRIAD",
            "DNN_TARGET_FPGA",
            "DNN_TARGET_HDDL",
        )
        if hasattr(cv2.dnn, name)
    }
    return {"backends": backends, "targets": targets}


def _run_child(thread_count: int) -> dict[str, object]:
    cv2.setNumThreads(thread_count)
    frame = _deterministic_frame()

    from vision.yolo_detector import MODEL_INPUT_NAME, MODEL_OUTPUT_NAME, YoloDetector

    detector = YoloDetector(model_path=MODEL_PATH)
    for _ in range(WARMUP_ITERATIONS):
        blob, scale, pad_x, pad_y = detector._preprocess(frame)
        detector.net.setInput(blob, MODEL_INPUT_NAME)
        output = detector.net.forward(MODEL_OUTPUT_NAME)
        candidates = detector._decode_output(
            output,
            width=frame.shape[1],
            height=frame.shape[0],
            scale=scale,
            pad_x=pad_x,
            pad_y=pad_y,
        )
        detector._class_aware_nms(candidates)

    timings = {
        "preprocess": [],
        "forward": [],
        "decode": [],
        "nms": [],
        "total": [],
    }
    detections = 0
    for _ in range(MEASURED_ITERATIONS):
        total_start = time.perf_counter()
        stage_start = total_start
        blob, scale, pad_x, pad_y = detector._preprocess(frame)
        stage_end = time.perf_counter()
        timings["preprocess"].append((stage_end - stage_start) * 1000)

        detector.net.setInput(blob, MODEL_INPUT_NAME)
        stage_start = time.perf_counter()
        output = detector.net.forward(MODEL_OUTPUT_NAME)
        stage_end = time.perf_counter()
        timings["forward"].append((stage_end - stage_start) * 1000)

        stage_start = time.perf_counter()
        candidates = detector._decode_output(
            output,
            width=frame.shape[1],
            height=frame.shape[0],
            scale=scale,
            pad_x=pad_x,
            pad_y=pad_y,
        )
        stage_end = time.perf_counter()
        timings["decode"].append((stage_end - stage_start) * 1000)

        stage_start = time.perf_counter()
        result = detector._class_aware_nms(candidates)
        stage_end = time.perf_counter()
        timings["nms"].append((stage_end - stage_start) * 1000)
        timings["total"].append((stage_end - total_start) * 1000)
        detections = len(result)

    return {
        "threads_requested": thread_count,
        "threads_effective": cv2.getNumThreads(),
        "opencv_version": cv2.__version__,
        "python_version": platform.python_version(),
        "model": str(MODEL_PATH),
        "frame_shape": list(FRAME_SHAPE),
        "warmup_iterations": WARMUP_ITERATIONS,
        "measured_iterations": MEASURED_ITERATIONS,
        "last_detection_count": detections,
        "timings": {name: _stats(values) for name, values in timings.items()},
        "dnn_options": _available_dnn_options(),
    }


def _child_main(thread_count: int) -> int:
    print(json.dumps(_run_child(thread_count), sort_keys=True))
    return 0


def _run_all(thread_counts: list[int]) -> None:
    print(f"Model: {MODEL_PATH}")
    print(f"Frame: {FRAME_SHAPE}, warm-up={WARMUP_ITERATIONS}, "
          f"measured={MEASURED_ITERATIONS}")
    for thread_count in thread_counts:
        command = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--child",
            str(thread_count),
        ]
        completed = subprocess.run(
            command,
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)
        print(f"\nOpenCV threads={result['threads_requested']} "
              f"(effective={result['threads_effective']})")
        print(
            "  forward: "
            f"{result['timings']['forward']}"
        )
        print(
            "  total:   "
            f"{result['timings']['total']}"
        )
        print(
            "  stages:  "
            f"preprocess={result['timings']['preprocess']['mean_ms']:.3f} ms, "
            f"decode={result['timings']['decode']['mean_ms']:.3f} ms, "
            f"nms={result['timings']['nms']['mean_ms']:.3f} ms"
        )
        print(
            f"  last detection count: {result['last_detection_count']}"
        )
        if thread_count == thread_counts[0]:
            print(f"  OpenCV DNN options: {result['dnn_options']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", type=int, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.child is not None:
        return _child_main(args.child)
    _run_all([1, 2, 4, 0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
