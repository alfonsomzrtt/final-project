"""Score widget.
This widget is presentation-only: game logic owns the score values and
updates this widget through ``set_scores`` or ``set_score``.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class ScoreWidget(QFrame):
    """Compact scoreboard displaying the current scores of both players."""

    def __init__(
        self,
        player1_name="P1",
        player2_name="P2",
        parent=None,
    ):
        super().__init__(parent)

        self._player1_name = str(player1_name)
        self._player2_name = str(player2_name)
        self._score_p1 = 0
        self._score_p2 = 0

        self.setObjectName("scoreWidget")
        self.setMaximumHeight(68)
        self.setStyleSheet(
            """
            QFrame#scoreWidget {
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

        self.title_label = QLabel("SKOR SEMENTARA")
        self.title_label.setFont(QFont("Segoe UI", 7, QFont.Bold))
        self.title_label.setStyleSheet("color: #8899AA;")
        root.addWidget(self.title_label)

        scores_layout = QHBoxLayout()
        scores_layout.setContentsMargins(0, 0, 0, 0)
        scores_layout.setSpacing(8)

        self.player1_label = QLabel()
        self.player1_label.setAlignment(Qt.AlignCenter)
        self.player1_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.player1_label.setStyleSheet("color: #2DC653;")

        self.player2_label = QLabel()
        self.player2_label.setAlignment(Qt.AlignCenter)
        self.player2_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.player2_label.setStyleSheet("color: #E63946;")

        scores_layout.addWidget(self.player1_label, 1)
        scores_layout.addWidget(self.player2_label, 1)
        root.addLayout(scores_layout)

        self._refresh()

    @property
    def score_p1(self):
        """Return Player 1's currently displayed score."""
        return self._score_p1

    @property
    def score_p2(self):
        """Return Player 2's currently displayed score."""
        return self._score_p2

    def set_scores(self, score_p1, score_p2):
        """Set both player scores and refresh the display.

        Scores must be non-negative integers. Numeric strings and floats are
        rejected rather than silently converted.
        """
        self._validate_score(score_p1, "score_p1")
        self._validate_score(score_p2, "score_p2")

        self._score_p1 = score_p1
        self._score_p2 = score_p2
        self._refresh()

    def set_score(self, player, score):
        """Set one player's score. ``player`` accepts 1 or 2."""
        if player not in (1, 2):
            raise ValueError("player harus bernilai 1 atau 2")
        self._validate_score(score, "score")

        if player == 1:
            self._score_p1 = score
        else:
            self._score_p2 = score

        self._refresh()

    def reset_scores(self):
        """Reset both displayed scores to zero."""
        self.set_scores(0, 0)

    @staticmethod
    def _validate_score(value, name):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{name} harus berupa integer")
        if value < 0:
            raise ValueError(f"{name} tidak boleh negatif")

    def _refresh(self):
        self.player1_label.setText(
            f"🏅 {self._player1_name}   {self._score_p1}"
        )
        self.player2_label.setText(
            f"🏅 {self._player2_name}   {self._score_p2}"
        )
