"""Isolated ONNX Runtime CPU audit for the project's YOLO ONNX model.

Run from the repository root with the project environment, for example:

    PYTHONPATH=src /home/alfonsomzrt/.venvs/bdt-312/bin/python \
        benchmarks/benchmark_onnxruntime_cpu.py

Each configuration is measured in a fresh subprocess. Production files and
the OpenCV DNN backend are not modified.
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
MEASURED = 50


def stats(values: list[float]) -> dict[str, float]:
    mean = statistics.mean(values)
    return {
        "mean_ms": mean,
        "median_ms": statistics.median(values),
        "p95_ms": float(np.percentile(values, 95)),
        "min_ms": min(values),
        "max_ms": max(values),
        "throughput_fps": 1000.0 / mean,
    }


def deterministic_frame() -> np.ndarray:
    height, width, _ = FRAME_SHAPE
    y, x = np.indices((height, width), dtype=np.uint16)
    frame = np.empty(FRAME_SHAPE, dtype=np.uint8)
    frame[:, :, 0] = (x * 3 + y) % 256
    frame[:, :, 1] = (x + y * 2) % 256
    frame[:, :, 2] = (x * 2 + y * 3) % 256
    return frame


def production_input(frame: np.ndarray) -> np.ndarray:
    from vision.yolo_detector import YoloDetector

    blob, _, _, _ = YoloDetector._preprocess(frame)
    return blob


def session_summary(session: ort.InferenceSession) -> dict[str, object]:
    options = session.get_session_options()
    return {
        "providers": session.get_providers(),
        "provider_options": session.get_provider_options(),
        "intra_op_num_threads": options.intra_op_num_threads,
        "inter_op_num_threads": options.inter_op_num_threads,
        "execution_mode": str(options.execution_mode),
        "graph_optimization_level": str(options.graph_optimization_level),
        "enable_mem_pattern": options.enable_mem_pattern,
        "enable_cpu_mem_arena": options.enable_cpu_mem_arena,
    }


def make_options(intra_op: int | None) -> ort.SessionOptions | None:
    if intra_op is None:
        return None
    options = ort.SessionOptions()
    options.intra_op_num_threads = intra_op
    # Keep the default sequential execution and graph optimization behavior.
    options.inter_op_num_threads = 0
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    return options


def direct_benchmark(intra_op: int | None) -> dict[str, object]:
    frame = deterministic_frame()
    input_tensor = production_input(frame)
    session = ort.InferenceSession(
        str(MODEL_PATH),
        sess_options=make_options(intra_op),
        providers=["CPUExecutionProvider"],
    )
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name

    for _ in range(WARMUP):
        session.run([output_name], {input_name: input_tensor})

    values = []
    output_shape = None
    for _ in range(MEASURED):
        started = time.perf_counter()
        output = session.run([output_name], {input_name: input_tensor})
        values.append((time.perf_counter() - started) * 1000)
        output_shape = list(output[0].shape)

    return {
        "configuration": "default" if intra_op is None else f"intra={intra_op}",
        "requested_intra_op": intra_op,
        "effective": session_summary(session),
        "output_shape": output_shape,
        "stats": stats(values),
    }


def ultralytics_benchmark() -> dict[str, object]:
    from ultralytics import YOLO

    frame = deterministic_frame()
    model = YOLO(str(MODEL_PATH))
    for _ in range(WARMUP):
        model.predict(frame, imgsz=640, conf=0.5, verbose=False)

    values = []
    result_count = 0
    for _ in range(MEASURED):
        started = time.perf_counter()
        results = model.predict(frame, imgsz=640, conf=0.5, verbose=False)
        values.append((time.perf_counter() - started) * 1000)
        result_count = len(results[0].boxes)

    session = model.predictor.model.session
    return {
        "stats": stats(values),
        "result_count": result_count,
        "session": session_summary(session),
    }


def environment() -> dict[str, object]:
    return {
        "python": platform.python_version(),
        "opencv": cv2.__version__,
        "onnxruntime": ort.__version__,
        "ultralytics": __import__("ultralytics").__version__,
        "available_ort_providers": ort.get_available_providers(),
        "logical_cpus": os.cpu_count(),
        "platform": platform.platform(),
    }


def child(intra_op: int | None, include_ultralytics: bool) -> int:
    result = {
        "environment": environment(),
        "direct": direct_benchmark(intra_op),
    }
    if include_ultralytics:
        result["ultralytics"] = ultralytics_benchmark()
    print("BENCHMARK_RESULT " + json.dumps(result, sort_keys=True))
    return 0


def run_child(intra_op: int | None, include_ultralytics: bool) -> dict[str, object]:
    command = [sys.executable, str(Path(__file__).resolve()), "--child"]
    if intra_op is not None:
        command += ["--intra", str(intra_op)]
    if include_ultralytics:
        command.append("--ultralytics")
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    result_line = next(
        line for line in completed.stdout.splitlines()
        if line.startswith("BENCHMARK_RESULT ")
    )
    return json.loads(result_line.removeprefix("BENCHMARK_RESULT "))


def print_stats(label: str, measured: dict[str, object]) -> None:
    values = measured["stats"]
    print(
        f"{label}: mean={values['mean_ms']:.2f} ms, "
        f"median={values['median_ms']:.2f} ms, "
        f"p95={values['p95_ms']:.2f} ms, "
        f"min={values['min_ms']:.2f} ms, "
        f"max={values['max_ms']:.2f} ms, "
        f"throughput={values['throughput_fps']:.2f} FPS"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--intra", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--ultralytics", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.child:
        return child(args.intra, args.ultralytics)

    print(f"Model: {MODEL_PATH}")
    print(f"Frame: {FRAME_SHAPE}; warm-up={WARMUP}; measured={MEASURED}")
    print(f"Environment: {environment()}")

    for repeat in range(3):
        result = run_child(None, include_ultralytics=(repeat == 0))
        print(f"\nDefault session repeat {repeat + 1}")
        print_stats("  direct", result["direct"])
        if "ultralytics" in result:
            print_stats("  ultralytics.predict", result["ultralytics"])
            print(f"  observed prediction/direct mean ratio: "
                  f"{result['ultralytics']['stats']['mean_ms'] / result['direct']['stats']['mean_ms']:.2f}x")
        if repeat == 0:
            print(f"  direct session: {result['direct']['effective']}")
            if "ultralytics" in result:
                print(f"  ultralytics session: {result['ultralytics']['session']}")

    hardware_threads = min(8, os.cpu_count() or 1)
    print("\nThread configuration comparison")
    for intra in (1, 2, 4, hardware_threads):
        result = run_child(intra, include_ultralytics=False)
        print(f"\n  intra_op_num_threads={intra}")
        print_stats("    direct", result["direct"])
        print(f"    effective session: {result['direct']['effective']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
