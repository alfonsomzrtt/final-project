from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel,
    QPushButton, QListWidget, QListWidgetItem
)


class GameResultScreen(QWidget):
    """Layar hasil akhir pertandingan."""

    def __init__(self, on_rematch):
        super().__init__()

        if not callable(on_rematch):
            raise TypeError("on_rematch harus callable")

        self.on_rematch = on_rematch

        self.setStyleSheet("""
            QWidget {
                background: #081421;
                color: #E8EEF5;
                font-family: Segoe UI;
            }
            QFrame {
                background: #132235;
                border: 1px solid #22364D;
                border-radius: 8px;
            }
            QListWidget {
                background: #0D1B2A;
                color: #E8EEF5;
                border: none;
                border-radius: 5px;
                padding: 6px;
                font-size: 10pt;
            }
            QPushButton {
                background: #276749;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 9px 18px;
                font-weight: bold;
            }
            QPushButton:hover { background: #31815C; }
        """)

        root = QHBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        left_frame = QFrame()
        left = QVBoxLayout(left_frame)
        left.setContentsMargins(18, 18, 18, 18)
        left.setSpacing(10)
        left.setAlignment(Qt.AlignCenter)

        self.clbl = QLabel("🏆 JUARA")
        self.clbl.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self.clbl.setStyleSheet("color: #F4C542;")
        self.clbl.setAlignment(Qt.AlignCenter)

        self.nlbl = QLabel("Belum ada pemenang")
        self.nlbl.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.nlbl.setAlignment(Qt.AlignCenter)

        self.wlbl = QLabel("Stage Win: 0–0")
        self.wlbl.setStyleSheet("color: #9BAABD;")
        self.wlbl.setAlignment(Qt.AlignCenter)

        left.addWidget(self.clbl)
        left.addWidget(self.nlbl)
        left.addWidget(self.wlbl)
        left.addSpacing(20)

        self.rematch_button = QPushButton("🔄 Main Lagi")
        self.rematch_button.setFixedWidth(160)
        self.rematch_button.clicked.connect(self.on_rematch)
        left.addWidget(self.rematch_button, alignment=Qt.AlignCenter)
        root.addWidget(left_frame, stretch=4)

        right = QVBoxLayout()
        right.setSpacing(10)

        leaderboard_frame = QFrame()
        leaderboard_layout = QVBoxLayout(leaderboard_frame)
        leaderboard_layout.setContentsMargins(14, 12, 14, 12)
        leaderboard_layout.setSpacing(8)

        heading = QLabel("LEADERBOARD")
        heading.setFont(QFont("Segoe UI", 11, QFont.Bold))
        heading.setStyleSheet("color: #9BAABD;")
        leaderboard_layout.addWidget(heading)

        self.leaderboard = QListWidget()
        leaderboard_layout.addWidget(self.leaderboard)
        right.addWidget(leaderboard_frame, stretch=3)

        details_frame = QFrame()
        details_layout = QVBoxLayout(details_frame)
        details_layout.setContentsMargins(14, 12, 14, 12)
        details_layout.setSpacing(8)

        details_heading = QLabel("RESULT DETAILS")
        details_heading.setFont(QFont("Segoe UI", 9, QFont.Bold))
        details_heading.setStyleSheet("color: #9BAABD;")
        details_layout.addWidget(details_heading)

        self.details = {}
        for key, label in (
            ("accuracy", "Pattern Accuracy"),
            ("completion_time", "Completion Time"),
            ("correct_placements", "Correct Placements"),
            ("wrong_placements", "Wrong Placements"),
            ("artwork_revealed", "Artwork Revealed"),
        ):
            row = QHBoxLayout()
            name = QLabel(f"• {label}")
            value = QLabel("—")
            value.setFont(QFont("Segoe UI", 9, QFont.Bold))
            value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row.addWidget(name)
            row.addWidget(value)
            details_layout.addLayout(row)
            self.details[key] = value

        right.addWidget(details_frame, stretch=2)
        root.addLayout(right, stretch=5)

    def set_result(
        self,
        winner,
        wins_p1,
        wins_p2,
        leaderboard,
        accuracy,
        completion_time,
        correct_placements,
        wrong_placements,
        artwork_revealed,
    ):
        """Memperbarui hasil; leaderboard berupa iterable (nama, skor)."""
        if not isinstance(winner, str) or not winner.strip():
            raise ValueError("winner harus berupa string nonblank")

        for name, value in (
            ("wins_p1", wins_p1),
            ("wins_p2", wins_p2),
            ("correct_placements", correct_placements),
            ("wrong_placements", wrong_placements),
            ("artwork_revealed", artwork_revealed),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} harus integer nonnegatif")

        if isinstance(accuracy, bool) or not isinstance(accuracy, (int, float)) or not 0 <= accuracy <= 100:
            raise ValueError("accuracy harus berada pada rentang 0–100")

        if isinstance(completion_time, bool) or not isinstance(completion_time, (int, float)) or completion_time < 0:
            raise ValueError("completion_time harus numerik nonnegatif")

        try:
            rows = list(leaderboard)
        except TypeError as exc:
            raise ValueError("leaderboard harus iterable") from exc

        for item in rows:
            if (
                not isinstance(item, (tuple, list))
                or len(item) != 2
                or not isinstance(item[0], str)
                or not item[0].strip()
                or isinstance(item[1], bool)
                or not isinstance(item[1], (int, float))
                or item[1] < 0
            ):
                raise ValueError("setiap leaderboard item harus berupa (nama, skor) valid")

        self.nlbl.setText(winner)
        self.wlbl.setText(f"Stage Win: {wins_p1}–{wins_p2}")

        self.leaderboard.clear()
        for rank, (name, score) in enumerate(
            sorted(rows, key=lambda item: item[1], reverse=True), start=1
        ):
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"{rank}.")
            self.leaderboard.addItem(f"{medal}  {name}    {score:g} pts")

        self.details["accuracy"].setText(f"{accuracy:g}%")
        self.details["completion_time"].setText(f"{completion_time:g}s")
        self.details["correct_placements"].setText(str(correct_placements))
        self.details["wrong_placements"].setText(str(wrong_placements))
        self.details["artwork_revealed"].setText(str(artwork_revealed))
