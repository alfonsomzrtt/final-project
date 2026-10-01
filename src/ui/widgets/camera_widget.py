
"""
Camera preview and adjustment widget.

Responsibilities:
- Display OpenCV BGR frames.
- Display camera connection status.
- Provide brightness, contrast, and saturation controls.
- Map raw slider values to calibrated camera values.

Camera capture and image processing must be handled
outside this widget, preferably by a dedicated worker.
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QSlider,
    QPushButton,
    QGroupBox,
    QSizePolicy,
    QFormLayout,
)

from config.settings import (
    CAMERA_SLIDER_BOUNDS,
    CAMERA_SLIDER_MIN,
    CAMERA_SLIDER_MAX,
    CAMERA_SLIDER_DEFAULT,
)


class CameraWidget(QWidget):
    """
    Camera preview widget with calibrated adjustments.

    Signals:
        adjustment_changed(str, int):
            Emits the adjustment name and its mapped value.

    Public methods:
        set_frame(frame)
        clear_frame()
        set_camera_status(status, detail=None)
        set_adjustment(name, value)
        get_adjustments()
        get_raw_adjustments()
        reset_adjustments()
    """

    adjustment_changed = pyqtSignal(str, int)

    ADJUSTMENT_NAMES = (
        "brightness",
        "contrast",
        "saturation",
    )

    CAMERA_STATUSES = {
        "connected": ("Connected", "#2DC653"),
        "disconnected": ("Disconnected", "#E57373"),
        "error": ("Camera Error", "#F4A261"),
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        self._frame = None
        self._sliders = {}
        self._value_labels = {}
        self._adjustment_rows = {}

        self._build_ui()

    # ==================================================
    # UI CONSTRUCTION
    # ==================================================

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(10)

        self._build_video_display(main_layout)
        self._build_status(main_layout)
        self._build_adjustments(main_layout)

    def _build_video_display(self, parent_layout):
        self.video_label = QLabel("Camera feed unavailable")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(320, 180)

        self.video_label.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        self.video_label.setStyleSheet(
            """
            QLabel {
                background-color: #101820;
                color: #8899AA;
                border: 1px solid #344455;
                border-radius: 6px;
            }
            """
        )
       
        parent_layout.addWidget(self.video_label, stretch=1)

    
    def _build_status(self, parent_layout):
        self.status_label = QLabel()
        self.status_label.setAlignment(
            Qt.AlignLeft | Qt.AlignVCenter
        )

        self.set_camera_status("disconnected")
        parent_layout.addWidget(self.status_label)



    def _build_adjustments(self, parent_layout):
        self.adjustment_group = QGroupBox(
            "Camera Adjustments"
        )

        self.adjustment_group.setCheckable(True)
        self.adjustment_group.setChecked(True)

        group_layout = QVBoxLayout(
            self.adjustment_group
        )
        group_layout.setContentsMargins(10, 12, 10, 10)
        group_layout.setSpacing(8)

        # The body is separate so the controls can collapse.
        self.adjustment_body = QWidget()
        body_layout = QVBoxLayout(self.adjustment_body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(8)

        form_layout = QFormLayout()
        form_layout.setSpacing(8)

        for name in self.ADJUSTMENT_NAMES:
            row, slider, value_label = (
                self._create_adjustment_row(name)
            )

            self._adjustment_rows[name] = row
            self._sliders[name] = slider
            self._value_labels[name] = value_label

            form_layout.addRow(
                name.capitalize(),
                row,
            )

        body_layout.addLayout(form_layout)

        self.reset_button = QPushButton(
            "Reset to Default"
        )
        self.reset_button.clicked.connect(
            self.reset_adjustments
        )
        body_layout.addWidget(self.reset_button)

        group_layout.addWidget(self.adjustment_body)

        self.adjustment_group.toggled.connect(
            self._toggle_adjustment_visibility
        )

        parent_layout.addWidget(self.adjustment_group)

    def _create_adjustment_row(self, name):
        slider = QSlider(Qt.Horizontal)

        slider.setRange(
            CAMERA_SLIDER_MIN,
            CAMERA_SLIDER_MAX,
        )
        slider.setValue(CAMERA_SLIDER_DEFAULT)
        slider.setTickInterval(25)
        slider.setTickPosition(QSlider.TicksBelow)

        value_label = QLabel()
        value_label.setMinimumWidth(42)
        value_label.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )

        self._update_value_label(
            value_label,
            slider.value(),
        )

        slider.valueChanged.connect(
            lambda value, key=name:
                self._on_slider_changed(key, value)
        )

        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)

        row_layout.addWidget(slider, stretch=1)
        row_layout.addWidget(value_label)

        return row, slider, value_label

    # ==================================================
    # SLIDER MAPPING
    # ==================================================

    @staticmethod
    def remap_slider(value, attr):
        """
        Map raw slider value (0-255) to calibrated value.

        The GUI percentage is only a representation of
        the raw slider position. It is not the actual
        OpenCV parameter value.
        """
        minimum, maximum = CAMERA_SLIDER_BOUNDS.get(
            attr,
            (0, 255),
        )

        value = max(
            CAMERA_SLIDER_MIN,
            min(CAMERA_SLIDER_MAX, int(value)),
        )

        ratio = (
            (value - CAMERA_SLIDER_MIN)
            / (CAMERA_SLIDER_MAX - CAMERA_SLIDER_MIN)
        )

        return round(
            minimum + ratio * (maximum - minimum)
        )

    @staticmethod
    def _to_percentage(value):
        """Convert raw slider position to UI percentage."""
        return round(
            (value - CAMERA_SLIDER_MIN)
            / (CAMERA_SLIDER_MAX - CAMERA_SLIDER_MIN)
            * 100
        )

    def _update_value_label(self, label, raw_value):
        label.setText(
            f"{self._to_percentage(raw_value)}%"
        )

    def _on_slider_changed(self, name, raw_value):
        self._update_value_label(
            self._value_labels[name],
            raw_value,
        )

        actual_value = self.remap_slider(
            raw_value,
            name,
        )

        self.adjustment_changed.emit(
            name,
            actual_value,
        )

    def set_adjustment(self, name, value):
        """
        Set a raw slider value (0-255).

        The resulting adjustment_changed signal carries
        the mapped value, not the raw slider value.
        """
        if name not in self._sliders:
            raise ValueError(
                f"Unknown camera adjustment: {name}"
            )

        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(
                "Slider value must be an integer."
            )

        if not CAMERA_SLIDER_MIN <= value <= CAMERA_SLIDER_MAX:
            raise ValueError(
                "Slider value must be between 0 and 255."
            )

        self._sliders[name].setValue(value)

    def get_raw_adjustments(self):
        """Return raw slider values (0-255)."""
        return {
            name: slider.value()
            for name, slider in self._sliders.items()
        }

    def get_adjustments(self):
        """Return calibrated adjustment values."""
        return {
            name: self.remap_slider(
                slider.value(),
                name,
            )
            for name, slider in self._sliders.items()
        }

    def reset_adjustments(self):
        """Restore all sliders to their default position."""
        for slider in self._sliders.values():
            slider.setValue(CAMERA_SLIDER_DEFAULT)

    def _toggle_adjustment_visibility(self, checked):
        self.adjustment_body.setVisible(checked)

    # ==================================================
    # VIDEO FRAME
    # ==================================================

    def set_frame(self, frame):
        """
        Display an OpenCV BGR frame.

        This method must be invoked on the GUI thread.
        Use a queued signal when receiving frames from
        a worker thread.
        """
        if frame is None:
            self.clear_frame()
            return

        if (
            getattr(frame, "ndim", 0) != 3
            or frame.shape[2] != 3
        ):
            raise ValueError(
                "Expected a three-channel BGR frame."
            )

        height, width, _ = frame.shape

        if height <= 0 or width <= 0:
            raise ValueError("Frame dimensions are invalid.")

        # BGR -> RGB, with contiguous memory.
        rgb = frame[:, :, ::-1].copy()

        image = QImage(
            rgb.data,
            width,
            height,
            rgb.strides[0],
            QImage.Format_RGB888,
        ).copy()

        self._frame = image
        self._render_frame()

    def _render_frame(self):
        if self._frame is None:
            return

        pixmap = QPixmap.fromImage(self._frame)

        scaled = pixmap.scaled(
            self.video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        self.video_label.setText("")
        self.video_label.setPixmap(scaled)

    def clear_frame(self):
        """Clear the current camera preview."""
        self._frame = None
        self.video_label.clear()
        self.video_label.setText(
            "Camera feed unavailable"
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._render_frame()

    # ==================================================
    # CAMERA STATUS
    # ==================================================

    def set_camera_status(self, status, detail=None):
        """
        Update camera status.

        Supported values:
            connected
            disconnected
            error
        """
        key = str(status).lower()

        if key not in self.CAMERA_STATUSES:
            raise ValueError(
                f"Unknown camera status: {status}"
            )

        text, color = self.CAMERA_STATUSES[key]

        if detail:
            text = f"{text} | {detail}"

        self.status_label.setText(f"● {text}")
        self.status_label.setStyleSheet(
            f"color: {color}; font-weight: bold;"
        )

        if key != "connected":
            self.clear_frame()