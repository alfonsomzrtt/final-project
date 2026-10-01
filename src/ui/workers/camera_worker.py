
from queue import Queue, Empty
from threading import Event

from PyQt5.QtCore import QThread, pyqtSignal
from vision.camera import Camera

class CameraWorker(QThread):
    """Capture camera frames outside the GUI thread."""

    frame_ready = pyqtSignal(object)
    status_changed = pyqtSignal(str, str)
    error = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stop_event = Event()
        self._adjustments = Queue()

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
    


    def run(self):
        camera = Camera()
        connected = False

        try:
            if not camera.open():
                message = "Unable to open camera."
                self.status_changed.emit("error", message)
                self.error.emit(message)
                return

            connected = True
            self.status_changed.emit("connected", "")

            while not self._stop_event.is_set():
                self._apply_adjustments(camera)

                frame = camera.read()
                if frame is None:
                    message = "Failed to read camera frame."
                    self.status_changed.emit("error", message)
                    self.error.emit(message)
                    break

                self.frame_ready.emit(frame)

        except Exception as exc:
            message = str(exc)
            self.status_changed.emit("error", message)
            self.error.emit(message)

        finally:
            camera.release()

            if connected and self._stop_event.is_set():
                self.status_changed.emit("disconnected", "")

    def stop(self):
        self._stop_event.set()