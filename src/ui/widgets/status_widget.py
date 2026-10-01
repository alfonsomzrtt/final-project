"""Status widget for the Block Design Puzzle Game.

The widget only presents a status. The controller or worker owns the
underlying application state and updates this widget through ``set_status``.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QLabel, QHBoxLayout, QVBoxLayout


class StatusWidget(QFrame):
    """Compact status indicator with a title and color-coded state."""

    _STATUS_CONFIG = {
        "idle": ("—", "#8899AA"),
        "waiting": ("WAITING", "#F4A261"),
        "ready": ("READY", "#2DC653"),
        "scanning": ("SCANNING...", "#42E8E0"),
        "matched": ("MATCHED", "#2DC653"),
        "not_matched": ("NOT MATCHED", "#E63946"),
        "connected": ("CONNECTED", "#2DC653"),
        "disconnected": ("DISCONNECTED", "#F4A261"),
        "error": ("ERROR", "#E63946"),
        "completed": ("COMPLETED", "#2DC653"),
    }

    def __init__(self, title="STATUS", parent=None):
        super().__init__(parent)

        self._title = str(title)
        self._status = "idle"
        self._message = None

        self.setObjectName("statusWidget")
        self.setMaximumHeight(58)
        self.setStyleSheet(
            """
            QFrame#statusWidget {
                background: #243447;
                border: none;
                border-radius: 8px;
            }
            QLabel {
                background: transparent;
                border: none;
            }
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 5, 12, 5)
        root.setSpacing(2)

        self.title_label = QLabel(self._title)
        self.title_label.setFont(QFont("Segoe UI", 7, QFont.Bold))
        self.title_label.setStyleSheet("color: #8899AA;")
        root.addWidget(self.title_label)

        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(4)

        self.status_label = QLabel()
        self.status_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        status_layout.addWidget(self.status_label, 1)

        root.addLayout(status_layout)
        self._refresh()

    @property
    def status(self):
        """Return the current normalized status key."""
        return self._status

    @property
    def message(self):
        """Return the optional custom status message."""
        return self._message

    def set_status(self, status, message=None):
        """Update the displayed status.

        ``status`` must be one of the supported status keys. A custom
        ``message`` replaces the default text while retaining the status color.
        """
        if not isinstance(status, str):
            raise TypeError("status harus berupa string")

        status = status.strip().lower()
        if status not in self._STATUS_CONFIG:
            raise ValueError(
                f"status tidak dikenal: {status!r}; "
                f"pilihan: {', '.join(self._STATUS_CONFIG)}"
            )

        if message is not None and not isinstance(message, str):
            raise TypeError("message harus berupa string atau None")

        self._status = status
        self._message = message
        self._refresh()

    def reset(self):
        """Return the widget to its initial idle state."""
        self.set_status("idle")

    def _refresh(self):
        default_text, color = self._STATUS_CONFIG[self._status]
        text = self._message if self._message else default_text
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color};")
