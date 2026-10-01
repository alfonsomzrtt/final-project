"""Stage result screen for the Block Design Puzzle Game."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class StageResultScreen(QWidget):
    """Display the winner and scores after a stage."""

    def __init__(self, on_next):
        super().__init__()
        if not callable(on_next):
            raise TypeError("on_next harus callable")

        self.on_next = on_next

        root = QHBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        left = QVBoxLayout()
        left.setAlignment(Qt.AlignCenter)

        self.title_label = QLabel("🏆 STAGE RESULT")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(
            "font-size: 22pt; font-weight: bold; color: #FFD700;"
        )

        self.winner_label = QLabel("Pemenang: —")
        self.winner_label.setAlignment(Qt.AlignCenter)
        self.winner_label.setStyleSheet("font-size: 16pt; font-weight: bold;")

        self.wins_label = QLabel("Stage Win: P1 0 | P2 0")
        self.wins_label.setAlignment(Qt.AlignCenter)

        self.scores_label = QLabel("P1: 0  vs  P2: 0")
        self.scores_label.setAlignment(Qt.AlignCenter)

        self.next_button = QPushButton("Stage Berikutnya →")
        self.next_button.setFixedHeight(40)
        self.next_button.clicked.connect(self.on_next)

        for widget in (
            self.title_label,
            self.winner_label,
            self.wins_label,
            self.scores_label,
            self.next_button,
        ):
            left.addWidget(widget)

        root.addLayout(left, stretch=4)

        right = QVBoxLayout()
        self.summary_frame = QFrame()
        self.summary_frame.setStyleSheet(
            "QFrame { background: #243447; border-radius: 8px; }"
        )
        summary = QVBoxLayout(self.summary_frame)
        summary.setContentsMargins(18, 16, 18, 16)

        heading = QLabel("RINGKASAN STAGE")
        heading.setStyleSheet(
            "font-size: 10pt; font-weight: bold; color: #8899AA;"
        )
        self.stage_label = QLabel("Stage 1")
        self.stage_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        summary.addWidget(heading)
        summary.addWidget(self.stage_label)
        right.addWidget(self.summary_frame)
        root.addLayout(right, stretch=5)

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
        if not isinstance(stage, int) or isinstance(stage, bool) or not 1 <= stage <= 3:
            raise ValueError("stage harus berupa integer 1 sampai 3")
        if not isinstance(winner, str) or not winner.strip():
            raise ValueError("winner tidak boleh kosong")
        for name, value in (
            ("wins_p1", wins_p1),
            ("wins_p2", wins_p2),
            ("score_p1", score_p1),
            ("score_p2", score_p2),
        ):
            if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} harus berupa angka non-negatif")
        if not isinstance(is_last, bool):
            raise TypeError("is_last harus boolean")

        self.stage_label.setText(f"Stage {stage}")
        self.winner_label.setText(f"Pemenang: {winner}")
        self.wins_label.setText(f"Stage Win: P1 {wins_p1} | P2 {wins_p2}")
        self.scores_label.setText(f"P1: {score_p1}  vs  P2: {score_p2}")
        self.next_button.setText(
            "Lihat Hasil Akhir 🏆" if is_last else "Stage Berikutnya →"
        )
