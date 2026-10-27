"""Lobby screen for the Block Design Puzzle Game."""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.enums import Difficulty, GridSize


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

        self._on_start = on_start
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

        config_card = QFrame()
        config_card.setObjectName("ConfigCard")
        config_card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        config_card.setStyleSheet(
            f"""
            QFrame#ConfigCard {{
                background: {BG_CARD};
                border: none;
                border-radius: 8px;
            }}
            """
        )

        config_layout = QVBoxLayout(config_card)
        config_layout.setContentsMargins(18, 14, 18, 14)
        config_layout.setSpacing(10)

        config_heading = QLabel("KONFIGURASI PERMAINAN")
        config_heading.setFont(QFont("Segoe UI", 9, QFont.Bold))
        config_heading.setStyleSheet(
            f"color: {TEXT_DIM}; background: transparent;"
        )
        config_layout.addWidget(config_heading)

        self.grid_size_combo = QComboBox()
        self.grid_size_combo.addItem("2x2", GridSize.TWO_BY_TWO)
        self.grid_size_combo.addItem("3x3", GridSize.THREE_BY_THREE)

        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItem("Easy", Difficulty.EASY)
        self.difficulty_combo.addItem("Normal", Difficulty.NORMAL)
        self.difficulty_combo.addItem("Hard", Difficulty.HARD)

        grid_row = QHBoxLayout()
        grid_row.setContentsMargins(0, 0, 0, 0)
        grid_row.setSpacing(12)

        grid_label = QLabel("Grid Size")
        grid_label.setFont(QFont("Segoe UI", 10))
        grid_label.setStyleSheet(f"color: {TEXT_MAIN}; background: transparent;")
        grid_row.addWidget(grid_label)
        grid_row.addWidget(self.grid_size_combo, stretch=1)
        config_layout.addLayout(grid_row)

        difficulty_row = QHBoxLayout()
        difficulty_row.setContentsMargins(0, 0, 0, 0)
        difficulty_row.setSpacing(12)

        difficulty_label = QLabel("Difficulty")
        difficulty_label.setFont(QFont("Segoe UI", 10))
        difficulty_label.setStyleSheet(
            f"color: {TEXT_MAIN}; background: transparent;"
        )
        difficulty_row.addWidget(difficulty_label)
        difficulty_row.addWidget(self.difficulty_combo, stretch=1)
        config_layout.addLayout(difficulty_row)

        root.addWidget(config_card)

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
        self.start_button.clicked.connect(self._emit_start)
        root.addWidget(self.start_button, alignment=Qt.AlignCenter)

    def _emit_start(self, checked=False):
        """Emit the selected game configuration to the controller."""
        del checked
        self._on_start(
            self.selected_grid_size(),
            self.selected_difficulty(),
        )

    def selected_grid_size(self):
        """Return the currently selected grid size."""
        return GridSize(self.grid_size_combo.currentData())

    def selected_difficulty(self):
        """Return the currently selected difficulty."""
        return Difficulty(self.difficulty_combo.currentData())

    def set_grid_size(self, grid_size):
        """Select a grid size in the lobby UI."""
        if not isinstance(grid_size, GridSize):
            raise TypeError("grid_size harus berupa GridSize")

        index = self.grid_size_combo.findData(grid_size)
        if index < 0:
            raise ValueError(f"Grid size tidak tersedia: {grid_size}")

        self.grid_size_combo.setCurrentIndex(index)

    def set_difficulty(self, difficulty):
        """Select a difficulty in the lobby UI."""
        if not isinstance(difficulty, Difficulty):
            raise TypeError("difficulty harus berupa Difficulty")

        index = self.difficulty_combo.findData(difficulty)
        if index < 0:
            raise ValueError(f"Difficulty tidak tersedia: {difficulty}")

        self.difficulty_combo.setCurrentIndex(index)

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
