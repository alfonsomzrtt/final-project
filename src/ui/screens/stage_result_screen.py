
"""Minimal competitive dashboard for the Block Design Puzzle Game."""

import math

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtSvg import QSvgWidget


class StageResultScreen(QWidget):
    """Display stage winner, score comparison, and match progression."""

    COLORS = {
        "background": "#111827",
        "surface": "#1F2937",
        "surface_light": "#293548",
        "gold": "#F5C451",
        "p1": "#43C59E",
        "p2": "#F07878",
        "text": "#F3F4F6",
        "muted": "#9CA3AF",
        "inactive": "#374151",
    }

    def __init__(self, on_next):
        super().__init__()

        if not callable(on_next):
            raise TypeError("on_next harus callable")

        self.on_next = on_next
        self.current_stage = 1

        self.setObjectName("StageResultScreen")
        self.setStyleSheet(f"""
            QWidget#StageResultScreen {{
                background-color: {self.COLORS["background"]};
                color: {self.COLORS["text"]};
            }}

            QLabel {{
                background: transparent;
                border: none;
            }}

            QFrame#WinnerPanel,
            QFrame#ScoreCard {{
                background-color: {self.COLORS["surface"]};
                border: 1px solid {self.COLORS["surface_light"]};
                border-radius: 12px;
            }}

            QPushButton#NextButton {{
                background-color: {self.COLORS["gold"]};
                color: #172033;
                border: none;
                border-radius: 8px;
                font-size: 11pt;
                font-weight: bold;
                padding: 10px;
            }}

            QPushButton#NextButton:hover {{
                background-color: #FFD778;
            }}

            QPushButton#NextButton:pressed {{
                background-color: #D9A936;
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(10)

        # Header
        header = QHBoxLayout()

        self.title_label = QLabel("MATCH SUMMARY")
        self.title_label.setStyleSheet(
            f"font-size: 9pt; font-weight: bold; "
            f"letter-spacing: 1px; color: {self.COLORS['muted']};"
        )

        self.stage_label = QLabel("STAGE 01 COMPLETE")
        self.stage_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.stage_label.setStyleSheet(
            f"font-size: 9pt; font-weight: bold; "
            f"color: {self.COLORS['gold']};"
        )

        header.addWidget(self.title_label)
        header.addStretch()
        header.addWidget(self.stage_label)
        root.addLayout(header)

        # Winner panel
        self.winner_panel = QFrame()
        self.winner_panel.setObjectName("WinnerPanel")

        winner_layout = QVBoxLayout(self.winner_panel)
        winner_layout.setContentsMargins(14, 10, 14, 10)
        winner_layout.setSpacing(3)

        # Winner emblem
        self.winner_emblem = QSvgWidget(
            "src/assets/icons/winner_emblem2.svg"
        )
        self.winner_emblem.setFixedSize(54, 54)

        winner_layout.addWidget(
            self.winner_emblem,
            alignment=Qt.AlignCenter,
        )

        winner_caption = QLabel("STAGE WINNER")
        winner_caption.setAlignment(Qt.AlignCenter)
        winner_caption.setStyleSheet(
            f"font-size: 8pt; font-weight: bold; "
            f"color: {self.COLORS['muted']};"
        )

        self.winner_label = QLabel("—")
        self.winner_label.setAlignment(Qt.AlignCenter)
        self.winner_label.setStyleSheet(
            f"font-size: 21pt; font-weight: bold; "
            f"color: {self.COLORS['gold']};"
        )

        self.winner_bonus_label = QLabel("+1 STAGE WIN")
        self.winner_bonus_label.setAlignment(Qt.AlignCenter)
        self.winner_bonus_label.setStyleSheet(
            f"font-size: 8pt; font-weight: bold; "
            f"color: {self.COLORS['gold']};"
        )

        winner_layout.addWidget(winner_caption)
        winner_layout.addWidget(self.winner_label)
        winner_layout.addWidget(self.winner_bonus_label)

        root.addWidget(self.winner_panel)

        # Score comparison
        score_layout = QHBoxLayout()
        score_layout.setSpacing(10)

        self.p1_card, self.p1_score = self._create_score_card(
            "PLAYER 1", self.COLORS["p1"]
        )
        self.p2_card, self.p2_score = self._create_score_card(
            "PLAYER 2", self.COLORS["p2"]
        )

        score_layout.addWidget(self.p1_card)
        score_layout.addWidget(self.p2_card)

        root.addLayout(score_layout)

        # Stage wins
        wins_layout = QHBoxLayout()

        wins_caption = QLabel("STAGE WINS")
        wins_caption.setStyleSheet(
            f"font-size: 8pt; font-weight: bold; "
            f"color: {self.COLORS['muted']};"
        )

        self.wins_label = QLabel("P1 0  :  0 P2")
        self.wins_label.setAlignment(Qt.AlignRight)
        self.wins_label.setStyleSheet(
            "font-size: 9pt; font-weight: bold;"
        )

        wins_layout.addWidget(wins_caption)
        wins_layout.addStretch()
        wins_layout.addWidget(self.wins_label)

        root.addLayout(wins_layout)

        # Three-stage progress indicator
        self.progress_segments = []

        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(5)

        for _ in range(3):
            segment = QFrame()
            segment.setFixedHeight(5)
            segment.setStyleSheet(
                f"background-color: {self.COLORS['inactive']}; "
                "border-radius: 2px;"
            )
            self.progress_segments.append(segment)
            progress_layout.addWidget(segment)

        root.addLayout(progress_layout)

        self.progress_label = QLabel("1 / 3 STAGES")
        self.progress_label.setAlignment(Qt.AlignRight)
        self.progress_label.setStyleSheet(
            f"font-size: 8pt; color: {self.COLORS['muted']};"
        )
        root.addWidget(self.progress_label)

        # Primary action
        self.next_button = QPushButton("CONTINUE TO STAGE 2")
        self.next_button.setObjectName("NextButton")
        self.next_button.setFixedHeight(42)
        self.next_button.clicked.connect(self.on_next)

        root.addWidget(self.next_button)

    def _create_score_card(self, player_name, accent_color):
        """Create a compact player score card."""

        card = QFrame()
        card.setObjectName("ScoreCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 9, 12, 9)
        layout.setSpacing(4)

        name_label = QLabel(player_name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet(
            f"font-size: 8pt; font-weight: bold; "
            f"color: {accent_color};"
        )

        score_label = QLabel("0")
        score_label.setAlignment(Qt.AlignCenter)
        score_label.setStyleSheet(
            f"font-size: 19pt; font-weight: bold; "
            f"color: {self.COLORS['text']};"
        )

        layout.addWidget(name_label)
        layout.addWidget(score_label)

        return card, score_label

    @staticmethod
    def _format_score(value):
        """Format score without unnecessary decimal places."""

        if isinstance(value, float) and value.is_integer():
            value = int(value)

        return f"{value:,.0f}" if isinstance(value, int) else f"{value:,.2f}"

    def update(
        self,
        stage,
        winner,
        wins_p1,
        wins_p2,
        score_p1,
        score_p2,
        is_last,
    ):
        """Update the dashboard using the completed stage data."""

        if (
            not isinstance(stage, int)
            or isinstance(stage, bool)
            or not 1 <= stage <= 3
        ):
            raise ValueError("stage harus berupa integer 1 sampai 3")

        if not isinstance(winner, str) or not winner.strip():
            raise ValueError("winner tidak boleh kosong")

        for name, value in (
            ("wins_p1", wins_p1),
            ("wins_p2", wins_p2),
            ("score_p1", score_p1),
            ("score_p2", score_p2),
        ):
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not math.isfinite(value)
                or value < 0
            ):
                raise ValueError(f"{name} harus berupa angka non-negatif")

        if not isinstance(is_last, bool):
            raise TypeError("is_last harus boolean")

        self.current_stage = stage

        # Stage information
        self.stage_label.setText(f"STAGE {stage:02d} COMPLETE")
        self.progress_label.setText(f"{stage} / 3 STAGES")

        # Winner
        self.winner_label.setText(winner.strip().upper())

        # Score comparison
        self.p1_score.setText(self._format_score(score_p1))
        self.p2_score.setText(self._format_score(score_p2))

        # Stage wins
        self.wins_label.setText(
            f"P1 {wins_p1:g}  :  {wins_p2:g} P2"
        )

        # Progress segments
        for index, segment in enumerate(self.progress_segments):
            color = (
                self.COLORS["gold"]
                if index < stage
                else self.COLORS["inactive"]
            )

            segment.setStyleSheet(
                f"background-color: {color}; border-radius: 2px;"
            )

        # Next action
        self.next_button.setText(
            "VIEW FINAL RESULTS"
            if is_last
            else f"CONTINUE TO STAGE {stage + 1}"
        )
