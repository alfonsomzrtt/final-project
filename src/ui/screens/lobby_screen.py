"""Lobby screen for the Block Design Puzzle Game."""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


BG_DARK = "#0D1B2A"
BG_CARD = "#243447"
ACCENT = "#E63946"
TEXT_MAIN = "#FFFFFF"
TEXT_DIM = "#8899AA"
GREEN = "#2DC653"
ORANGE = "#F4A261"


class LobbyScreen(QWidget):
    """Initial screen that displays player status and starts a game.

    Args:
        on_start: Callback invoked when the start button is clicked.
    """

    def __init__(self, on_start):
        super().__init__()

        self._player_labels = {}

        self.setObjectName("LobbyScreen")
        self.setStyleSheet(
            f"""
            QWidget#LobbyScreen {{
                background: {BG_DARK};
                color: {TEXT_MAIN};
                font-family: 'Segoe UI';
            }}
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(14)
        root.setAlignment(Qt.AlignCenter)

        title = QLabel("🧩  Block Design Puzzle Game")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        root.addWidget(title)

        subtitle = QLabel("Vision-based Automated Pattern Detection")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet(f"color: {TEXT_DIM}; background: transparent;")
        subtitle.setAlignment(Qt.AlignCenter)
        root.addWidget(subtitle)

        root.addSpacing(12)

        player_card = QFrame()
        player_card.setObjectName("PlayerCard")
        player_card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        player_card.setStyleSheet(
            f"""
            QFrame#PlayerCard {{
                background: {BG_CARD};
                border: none;
                border-radius: 8px;
            }}
            """
        )

        card_layout = QVBoxLayout(player_card)
        card_layout.setContentsMargins(18, 14, 18, 14)
        card_layout.setSpacing(10)

        heading = QLabel("STATUS PEMAIN")
        heading.setFont(QFont("Segoe UI", 9, QFont.Bold))
        heading.setStyleSheet(f"color: {TEXT_DIM}; background: transparent;")
        card_layout.addWidget(heading)

        for player_id, player_name in ((1, "Player 1"), (2, "Player 2")):
            label = QLabel(f"🟡  {player_name} — Menunggu...")
            label.setFont(QFont("Segoe UI", 11))
            label.setStyleSheet(
                f"color: {ORANGE}; background: transparent;"
            )
            label.setWordWrap(True)
            self._player_labels[player_id] = label
            card_layout.addWidget(label)

        root.addWidget(player_card)

        summary = QLabel(
            "1 Game = 3 Stage  |  5 Pattern/Stage  |  15 Pattern/Match"
        )
        summary.setFont(QFont("Segoe UI", 9))
        summary.setStyleSheet(f"color: {TEXT_DIM}; background: transparent;")
        summary.setAlignment(Qt.AlignCenter)
        summary.setWordWrap(True)
        root.addWidget(summary)

        self.start_button = QPushButton("▶  Mulai Game")
        self.start_button.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.start_button.setFixedSize(200, 40)
        self.start_button.setCursor(Qt.PointingHandCursor)
        self.start_button.setStyleSheet(
            f"""
            QPushButton {{
                background: {ACCENT};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0 18px;
            }}
            QPushButton:hover {{
                background: #D92F3D;
            }}
            QPushButton:pressed {{
                background: #B92532;
            }}
            QPushButton:disabled {{
                background: #59636F;
                color: #B8C0C8;
            }}
            """
        )
        self.start_button.clicked.connect(on_start)
        root.addWidget(self.start_button, alignment=Qt.AlignCenter)

    def set_player_status(self, player_id, status, message=None):
        """Update one player's status.

        Args:
            player_id: Player number, either 1 or 2.
            status: One of ``waiting``, ``ready``, ``disconnected``, or
                ``error``.
            message: Optional text appended to the status.
        """
        if player_id not in self._player_labels:
            raise ValueError("player_id harus 1 atau 2")

        status_config = {
            "waiting": ("🟡", "Menunggu...", ORANGE),
            "ready": ("🟢", "Ready", GREEN),
            "disconnected": ("⚪", "Disconnected", TEXT_DIM),
            "error": ("🔴", "Error", ACCENT),
        }

        if status not in status_config:
            raise ValueError(
                "status harus waiting, ready, disconnected, atau error"
            )
        if message is not None and not isinstance(message, str):
            raise TypeError("message harus berupa str atau None")

        icon, label_text, color = status_config[status]
        player_name = f"Player {player_id}"
        suffix = f" — {message}" if message else ""
        label = self._player_labels[player_id]
        label.setText(f"{icon}  {player_name} — {label_text}{suffix}")
        label.setStyleSheet(f"color: {color}; background: transparent;")

    def set_start_enabled(self, enabled):
        """Enable or disable the start button."""
        self.start_button.setEnabled(bool(enabled))
