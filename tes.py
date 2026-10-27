import cv2
import time
from ultralytics import YOLO

MODEL_PATH = "models/baseline-52-4rd.onnx"

model = YOLO(MODEL_PATH, task="detect")

print("Predictor sebelum prediksi:", model.predictor)

cap = cv2.VideoCapture(2)
if not cap.isOpened():
    raise RuntimeError("Kamera index 2 tidak dapat dibuka")

try:
    # Warm-up dan inisialisasi predictor
    ret, frame = cap.read()
    if not ret:
        raise RuntimeError("Gagal membaca frame kamera")

    model.predict(frame, imgsz=640, conf=0.5, verbose=False)

    predictor = model.predictor
    backend_model = predictor.model

    print("\n=== BACKEND AUDIT ===")
    print("Predictor type:", type(predictor))
    print("Model backend type:", type(backend_model))
    print("Backend attributes:", {
        name: getattr(backend_model, name, None)
        for name in ("pt", "onnx", "engine", "device", "format")
        if hasattr(backend_model, name)
    })

    session = getattr(backend_model, "session", None)
    print("ONNX session:", type(session) if session is not None else None)

    if session is not None and hasattr(session, "get_providers"):
        print("Session providers:", session.get_providers())

    # Ukur latensi predict secara terpisah dari pembacaan kamera.
    latencies = []
    for _ in range(50):
        ret, frame = cap.read()
        if not ret:
            continue

        start = time.perf_counter()
        model.predict(frame, imgsz=640, conf=0.5, verbose=False)
        latencies.append((time.perf_counter() - start) * 1000)

    if latencies:
        latencies.sort()
        n = len(latencies)
        print("\n=== PREDICT LATENCY ===")
        print("Samples:", n)
        print(f"Mean: {sum(latencies) / n:.2f} ms")
        print(f"Median: {latencies[n // 2]:.2f} ms")
        print(f"P95: {latencies[min(int(n * 0.95), n - 1)]:.2f} ms")
        print(f"Approximate predict throughput: {1000 / (sum(latencies) / n):.2f} FPS")

finally:
    cap.release()
