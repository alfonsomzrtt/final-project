"""Matched OpenCV DNN versus ONNX Runtime benchmark.

Run from the repository root:

    PYTHONPATH=src /home/alfonsomzrt/.venvs/bdt-312/bin/python \
        benchmarks/benchmark_backend_comparison.py

Each backend/configuration/repeat runs in a fresh subprocess. Production
source and backend selection are not modified.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
MODEL_PATH = ROOT / "models" / "baseline-52-4rd.onnx"
FRAME_SHAPE = (720, 1280, 3)
WARMUP = 10
MEASURED = 100
REPEATS = 3


def deterministic_frame() -> np.ndarray:
    height, width, _ = FRAME_SHAPE
    y, x = np.indices((height, width), dtype=np.uint16)
    frame = np.empty(FRAME_SHAPE, dtype=np.uint8)
    frame[:, :, 0] = (x * 3 + y) % 256
    frame[:, :, 1] = (x + y * 2) % 256
    frame[:, :, 2] = (x * 2 + y * 3) % 256
    return frame


def summary(values: list[float]) -> dict[str, float]:
    mean = statistics.mean(values)
    return {
        "mean_ms": mean,
        "median_ms": statistics.median(values),
        "p95_ms": float(np.percentile(values, 95)),
        "min_ms": min(values),
        "max_ms": max(values),
        "throughput_fps": 1000 / mean,
    }


def build_session_options(intra: int | None) -> ort.SessionOptions | None:
    if intra is None:
        return None
    options = ort.SessionOptions()
    options.intra_op_num_threads = intra
    options.inter_op_num_threads = 0
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    return options


def session_info(session: ort.InferenceSession) -> dict[str, object]:
    options = session.get_session_options()
    return {
        "providers": session.get_providers(),
        "intra_op_num_threads": options.intra_op_num_threads,
        "inter_op_num_threads": options.inter_op_num_threads,
        "execution_mode": str(options.execution_mode),
        "graph_optimization_level": str(options.graph_optimization_level),
    }


def run_backend(backend: str, thread_count: int | None) -> dict[str, object]:
    from vision.yolo_detector import MODEL_INPUT_NAME, MODEL_OUTPUT_NAME, YoloDetector

    frame = deterministic_frame()
    detector = YoloDetector.__new__(YoloDetector)
    detector.confidence_threshold = 0.25
    detector.nms_threshold = 0.45
    blob, scale, pad_x, pad_y = detector._preprocess(frame)

    if backend == "opencv":
        cv2.setNumThreads(thread_count or 1)
        detector.net = cv2.dnn.readNetFromONNX(str(MODEL_PATH))
        input_name = MODEL_INPUT_NAME
        output_name = MODEL_OUTPUT_NAME
        session_details = {
            "opencv_threads_effective": cv2.getNumThreads(),
            "backend": "OpenCV DNN default",
            "target": "OpenCV DNN default",
        }

        def infer():
            detector.net.setInput(blob, input_name)
            return detector.net.forward(output_name)
    else:
        session = ort.InferenceSession(
            str(MODEL_PATH),
            sess_options=build_session_options(thread_count),
            providers=["CPUExecutionProvider"],
        )
        input_name = session.get_inputs()[0].name
        output_name = session.get_outputs()[0].name
        session_details = session_info(session)

        def infer():
            return session.run([output_name], {input_name: blob})[0]

    for _ in range(WARMUP):
        infer()

    raw_output = infer()
    timings = {"backend": [], "decode": [], "nms": [], "total": []}
    last_detections = 0
    for _ in range(MEASURED):
        total_start = time.perf_counter()
        backend_start = total_start
        output = infer()
        backend_end = time.perf_counter()
        candidates = detector._decode_output(
            output,
            width=frame.shape[1],
            height=frame.shape[0],
            scale=scale,
            pad_x=pad_x,
            pad_y=pad_y,
        )
        decode_end = time.perf_counter()
        result = detector._class_aware_nms(candidates)
        end = time.perf_counter()
        timings["backend"].append((backend_end - backend_start) * 1000)
        timings["decode"].append((decode_end - backend_end) * 1000)
        timings["nms"].append((end - decode_end) * 1000)
        timings["total"].append((end - total_start) * 1000)
        last_detections = len(result)

    return {
        "backend": backend,
        "thread_count": thread_count,
        "session": session_details,
        "input_shape": list(blob.shape),
        "input_dtype": str(blob.dtype),
        "output_shape": list(np.asarray(raw_output).shape),
        "output_dtype": str(np.asarray(raw_output).dtype),
        "last_detection_count": last_detections,
        "timings": {name: summary(values) for name, values in timings.items()},
        "raw_output": np.asarray(raw_output),
    }


def raw_comparison(opencv_output: np.ndarray, ort_output: np.ndarray) -> dict[str, object]:
    opencv_values = np.asarray(opencv_output, dtype=np.float32)
    ort_values = np.asarray(ort_output, dtype=np.float32)
    if opencv_values.shape != ort_values.shape:
        return {
            "shape_equal": False,
            "opencv_shape": list(opencv_values.shape),
            "onnxruntime_shape": list(ort_values.shape),
        }
    difference = np.abs(opencv_values - ort_values)
    return {
        "shape_equal": True,
        "shape": list(opencv_values.shape),
        "max_abs": float(np.max(difference)),
        "mean_abs": float(np.mean(difference)),
        "allclose_1e-4": bool(np.allclose(opencv_values, ort_values, atol=1e-4, rtol=1e-4)),
        "allclose_1e-3": bool(np.allclose(opencv_values, ort_values, atol=1e-3, rtol=1e-3)),
    }


def child(backend: str, thread_count: int | None) -> int:
    result = run_backend(backend, thread_count)
    result["raw_output"] = result["raw_output"].tolist()
    print("BENCHMARK_RESULT " + json.dumps(result, sort_keys=True))
    return 0


def run_child(backend: str, thread_count: int | None) -> dict[str, object]:
    command = [sys.executable, str(Path(__file__).resolve()), "--child", backend]
    if thread_count is not None:
        command += ["--threads", str(thread_count)]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    line = next(
        item for item in completed.stdout.splitlines()
        if item.startswith("BENCHMARK_RESULT ")
    )
    result = json.loads(line.removeprefix("BENCHMARK_RESULT "))
    result["raw_output"] = np.asarray(result["raw_output"], dtype=np.float32)
    return result


def print_timing(result: dict[str, object]) -> None:
    timing = result["timings"]
    label = f"{result['backend']} threads={result['thread_count']}"
    print(
        f"{label}: backend mean={timing['backend']['mean_ms']:.2f} ms "
        f"P95={timing['backend']['p95_ms']:.2f} ms; "
        f"decode={timing['decode']['mean_ms']:.2f} ms; "
        f"NMS={timing['nms']['mean_ms']:.2f} ms; "
        f"total mean={timing['total']['mean_ms']:.2f} ms "
        f"P95={timing['total']['p95_ms']:.2f} ms "
        f"throughput={timing['total']['throughput_fps']:.2f} FPS"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", choices=("opencv", "onnxruntime"), help=argparse.SUPPRESS)
    parser.add_argument("--threads", type=int, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.child:
        return child(args.child, args.threads)

    print(f"Model: {MODEL_PATH}")
    print(f"Frame: {FRAME_SHAPE}; warm-up={WARMUP}; measured={MEASURED}; repeats={REPEATS}")
    print({
        "python": platform.python_version(),
        "opencv": cv2.__version__,
        "onnxruntime": ort.__version__,
        "logical_cpus": os.cpu_count(),
        "platform": platform.platform(),
    })

    configurations = [
        ("opencv", 1),
        ("opencv", 2),
        ("opencv", 4),
        ("onnxruntime", None),
        ("onnxruntime", 1),
        ("onnxruntime", 2),
        ("onnxruntime", 4),
    ]
    baseline_outputs = None
    for backend, thread_count in configurations:
        print(f"\n=== {backend} threads={thread_count} ===")
        for repeat in range(1, REPEATS + 1):
            result = run_child(backend, thread_count)
            print(f"repeat {repeat}: ", end="")
            print_timing(result)
            if baseline_outputs is None:
                baseline_outputs = (backend, result["raw_output"])
            elif repeat == 1:
                comparison = raw_comparison(baseline_outputs[1], result["raw_output"])
                print(f"raw output compatibility vs {baseline_outputs[0]}: {comparison}")
            if repeat == 1:
                print(f"input={result['input_shape']} {result['input_dtype']}; "
                      f"output={result['output_shape']} {result['output_dtype']}")
                print(f"session={result['session']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
