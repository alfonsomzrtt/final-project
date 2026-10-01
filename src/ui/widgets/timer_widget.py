"""Timer widget for the Block Design Puzzle Game.

This widget owns only its visual countdown. Game rules and scoring remain
outside the widget; consumers can react to ``timeout`` and ``tick`` signals.
"""

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QLabel, QProgressBar, QVBoxLayout


class TimerWidget(QFrame):
    """Countdown timer with a text label and a progress bar."""

    timeout = pyqtSignal()
    tick = pyqtSignal(int)

    def __init__(self, duration=30, parent=None):
        super().__init__(parent)

        self._validate_seconds(duration, "duration", allow_zero=False)
        self._duration = duration
        self._remaining = duration

        self.setObjectName("timerWidget")
        self.setMaximumHeight(64)
        self.setStyleSheet(
            """
            QFrame#timerWidget {
                background: #243447;
                border: none;
                border-radius: 8px;
            }
            QLabel {
                background: transparent;
                border: none;
            }
            QProgressBar {
                background: #1B2A3B;
                border: none;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background: #E63946;
                border-radius: 4px;
            }
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 5, 12, 5)
        root.setSpacing(3)

        self.time_label = QLabel()
        self.time_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("color: #FFD700;")
        root.addWidget(self.time_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        root.addWidget(self.progress_bar)

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

        self._refresh()

    @property
    def duration(self):
        """Return the configured countdown duration in seconds."""
        return self._duration

    @property
    def remaining_seconds(self):
        """Return the currently displayed remaining time in seconds."""
        return self._remaining

    @property
    def is_running(self):
        """Return whether the countdown is active."""
        return self._timer.isActive()

    def set_duration(self, seconds):
        """Set a new positive duration and reset the countdown."""
        self._validate_seconds(seconds, "duration", allow_zero=False)
        self._timer.stop()
        self._duration = seconds
        self._remaining = seconds
        self._refresh()

    def set_remaining(self, seconds):
        """Set the remaining time without starting or stopping the timer."""
        self._validate_seconds(seconds, "seconds", allow_zero=True)
        if seconds > self._duration:
            raise ValueError("seconds tidak boleh melebihi duration")

        self._remaining = seconds
        self._refresh()

        if seconds == 0:
            self._timer.stop()

    def start(self, seconds=None):
        """Start the countdown, optionally replacing its duration.

        Starting an already active timer has no effect unless a new duration
        is supplied.
        """
        if seconds is not None:
            self.set_duration(seconds)

        if self._remaining == 0:
            self._remaining = self._duration
            self._refresh()

        if not self._timer.isActive():
            self._timer.start()

    def stop(self):
        """Pause the countdown while preserving the remaining time."""
        self._timer.stop()

    def reset(self, seconds=None):
        """Stop and reset the countdown to its configured or supplied duration."""
        if seconds is not None:
            self._validate_seconds(seconds, "duration", allow_zero=False)
            self._duration = seconds

        self._timer.stop()
        self._remaining = self._duration
        self._refresh()

    @staticmethod
    def _validate_seconds(value, name, allow_zero):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{name} harus berupa integer")

        minimum = 0 if allow_zero else 1
        if value < minimum:
            qualifier = "tidak boleh negatif" if allow_zero else "harus lebih dari 0"
            raise ValueError(f"{name} {qualifier}")

    def _tick(self):
        if self._remaining <= 0:
            self._timer.stop()
            return

        self._remaining -= 1
        self._refresh()
        self.tick.emit(self._remaining)

        if self._remaining == 0:
            self._timer.stop()
            self.timeout.emit()

    def _refresh(self):
        self.time_label.setText(f"⏱  {self._remaining}s")
        self.progress_bar.setRange(0, self._duration)
        self.progress_bar.setValue(self._remaining)
