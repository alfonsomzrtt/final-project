"""Gameplay screen for the Block Design Puzzle Game."""

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ui.widgets.camera_widget import CameraWidget
from ui.widgets.pattern_widget import PatternGrid


BG_DARK = "#0D1B2A"
BG_CARD = "#243447"
ACCENT = "#E63946"
TEXT_MAIN = "#FFFFFF"
TEXT_DIM = "#8899AA"
GREEN = "#2DC653"
GOLD = "#F4C95D"
TEAL = "#2C7A7B"


class GameScreen(QWidget):
    """Display the target pattern, camera feed, timer, and game progress.

    The screen does not own game state or perform pattern detection.
    Those responsibilities remain with the controller and vision worker.

    Args:
        on_done: Callback called once when a pattern is resolved. It receives
            ``correct`` and ``time_left`` keyword arguments.
    """

    def __init__(self, on_done):
        super().__init__()

        if not callable(on_done):
            raise TypeError("on_done harus berupa callable")

        self.on_done = on_done
        self._remaining = 30
        self._duration = 30
        self._resolved = True

        self.setObjectName("GameScreen")
        self.setStyleSheet(
            f"""
            QWidget#GameScreen {{
                background: {BG_DARK};
                color: {TEXT_MAIN};
                font-family: 'Segoe UI';
            }}
            """
        )

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(6)
        splitter.setStyleSheet(
            "QSplitter::handle { background: #0D1B2A; }"
        )

        # Left column: target pattern and camera.
        left_widget = QWidget()
        left = QVBoxLayout(left_widget)
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(8)

        self.stage_label = QLabel("Stage 1 — Pattern 1/5")
        self.stage_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.stage_label.setWordWrap(True)

        self.timer_label = QLabel("⏱  30s")
        self.timer_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.timer_label.setStyleSheet(f"color: {GOLD};")
        self.timer_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        header.addWidget(self.stage_label, 1)
        header.addWidget(self.timer_label)
        left.addLayout(header)

        self.time_bar = QProgressBar()
        self.time_bar.setRange(0, 30)
        self.time_bar.setValue(30)
        self.time_bar.setTextVisible(False)
        self.time_bar.setFixedHeight(8)
        left.addWidget(self.time_bar)

        target_frame = self._make_card()
        target_layout = QVBoxLayout(target_frame)
        target_layout.setContentsMargins(12, 8, 12, 8)
        target_layout.setSpacing(6)

        target_title = QLabel("TARGET PATTERN")
        target_title.setFont(QFont("Segoe UI", 9, QFont.Bold))
        target_title.setStyleSheet(f"color: {TEXT_DIM};")
        target_layout.addWidget(target_title)

        self.pattern_grid = PatternGrid()
        target_layout.addWidget(self.pattern_grid, 1, Qt.AlignCenter)
        left.addWidget(target_frame, 3)

        camera_frame = self._make_card()
        camera_layout = QVBoxLayout(camera_frame)
        camera_layout.setContentsMargins(12, 7, 12, 7)
        camera_layout.setSpacing(5)

        camera_header = QHBoxLayout()
        camera_title = QLabel("LIVE CAMERA FEED")
        camera_title.setFont(QFont("Segoe UI", 8, QFont.Bold))
        camera_title.setStyleSheet(f"color: {TEXT_DIM};")
        camera_header.addWidget(camera_title, 1)

        self.detection_label = QLabel("Pattern Detection: —")
        self.detection_label.setFont(QFont("Segoe UI", 8))
        self.detection_label.setStyleSheet(f"color: {GREEN};")
        self.detection_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        camera_header.addWidget(self.detection_label)
        camera_layout.addLayout(camera_header)

        self.camera_widget = CameraWidget()
        self.camera_widget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        camera_layout.addWidget(self.camera_widget, 1)
        left.addWidget(camera_frame, 2)

        # Right column: score, artwork placeholder, and progress/log.
        right_widget = QWidget()
        right = QVBoxLayout(right_widget)
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(8)

        score_frame = self._make_card()
        score_frame.setMaximumHeight(68)
        score_layout = QVBoxLayout(score_frame)
        score_layout.setContentsMargins(12, 5, 12, 5)
        score_layout.setSpacing(2)

        score_title = QLabel("SKOR SEMENTARA")
        score_title.setFont(QFont("Segoe UI", 7, QFont.Bold))
        score_title.setStyleSheet(f"color: {TEXT_DIM};")
        score_layout.addWidget(score_title)

        score_row = QHBoxLayout()
        self.player1_score_label = QLabel("🏅 P1   0")
        self.player1_score_label.setStyleSheet(f"color: {GREEN};")
        self.player1_score_label.setAlignment(Qt.AlignCenter)
        self.player2_score_label = QLabel("🏅 P2   0")
        self.player2_score_label.setStyleSheet(f"color: {ACCENT};")
        self.player2_score_label.setAlignment(Qt.AlignCenter)
        score_row.addWidget(self.player1_score_label, 1)
        score_row.addWidget(self.player2_score_label, 1)
        score_layout.addLayout(score_row)
        right.addWidget(score_frame)

        artwork_frame = self._make_card()
        artwork_layout = QVBoxLayout(artwork_frame)
        artwork_layout.setContentsMargins(12, 8, 12, 8)
        artwork_layout.setSpacing(6)

        artwork_header = QHBoxLayout()
        artwork_title = QLabel("MYSTERY ARTWORK")
        artwork_title.setFont(QFont("Segoe UI", 9, QFont.Bold))
        artwork_title.setStyleSheet(f"color: {TEXT_DIM};")
        artwork_header.addWidget(artwork_title, 1)

        self.artwork_count_label = QLabel("0 / 15")
        self.artwork_count_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.artwork_count_label.setStyleSheet(f"color: {GOLD};")
        self.artwork_count_label.setAlignment(Qt.AlignRight)
        artwork_header.addWidget(self.artwork_count_label)
        artwork_layout.addLayout(artwork_header)

        self.artwork_placeholder = QLabel("Artwork akan ditampilkan di sini")
        self.artwork_placeholder.setAlignment(Qt.AlignCenter)
        self.artwork_placeholder.setMinimumHeight(100)
        self.artwork_placeholder.setStyleSheet(
            f"background: #111820; color: {TEXT_DIM}; border-radius: 5px;"
        )
        artwork_layout.addWidget(self.artwork_placeholder, 1)
        right.addWidget(artwork_frame, 7)

        lower_frame = self._make_card()
        lower_layout = QVBoxLayout(lower_frame)
        lower_layout.setContentsMargins(9, 7, 9, 7)
        lower_layout.setSpacing(5)

        bank_header = QHBoxLayout()
        bank_title = QLabel("PATTERN BANK")
        bank_title.setFont(QFont("Segoe UI", 7, QFont.Bold))
        bank_title.setStyleSheet(f"color: {TEXT_DIM};")
        bank_header.addWidget(bank_title, 1)
        self.pattern_count_label = QLabel("1 / 15")
        self.pattern_count_label.setStyleSheet(f"color: {TEXT_DIM};")
        bank_header.addWidget(self.pattern_count_label)
        lower_layout.addLayout(bank_header)

        self.pattern_bank_labels = []
        bank_grid = QHBoxLayout()
        bank_grid.setSpacing(3)
        for index in range(1, 16):
            item = QLabel(f"{index:02d}")
            item.setAlignment(Qt.AlignCenter)
            item.setFixedSize(25, 22)
            item.setStyleSheet(
                "background: #111820; color: #6B7280; border-radius: 3px;"
            )
            self.pattern_bank_labels.append(item)
            bank_grid.addWidget(item)
        lower_layout.addLayout(bank_grid)

        self.log = QListWidget()
        self.log.setFixedHeight(38)
        self.log.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.log.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.log.setStyleSheet(
            f"QListWidget {{ background: transparent; border: none; "
            f"color: {TEXT_DIM}; font-family: Consolas; font-size: 8pt; }}"
        )
        lower_layout.addWidget(self.log)

        self.demo_button = QPushButton("⚡ Simulasi Deteksi Benar")
        self.demo_button.setCursor(Qt.PointingHandCursor)
        self.demo_button.setFixedHeight(34)
        self.demo_button.setStyleSheet(
            f"QPushButton {{ background: {TEAL}; color: white; "
            "border: none; border-radius: 5px; padding: 4px 10px; }"
            "QPushButton:hover { background: #24696A; }"
        )
        self.demo_button.clicked.connect(self._sim_correct)
        lower_layout.addWidget(self.demo_button)
        right.addWidget(lower_frame, 3)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([500, 720])
        left_widget.setMinimumWidth(300)
        right_widget.setMinimumWidth(300)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.addWidget(splitter)

    @staticmethod
    def _make_card():
        frame = QFrame()
        frame.setStyleSheet(
            f"QFrame {{ background: {BG_CARD}; border: none; "
            "border-radius: 8px; }"
        )
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return frame

    @property
    def remaining_seconds(self):
        return self._remaining

    @property
    def is_running(self):
        return self._timer.isActive()

    def start(
        self,
        stage,
        pattern_in_stage,
        global_pattern,
        grid,
        seconds,
    ):
        """Load a pattern and start its countdown."""
        if type(stage) is not int or not 1 <= stage <= 3:
            raise ValueError("stage harus integer antara 1 dan 3")
        if type(pattern_in_stage) is not int or not 1 <= pattern_in_stage <= 5:
            raise ValueError("pattern_in_stage harus integer antara 1 dan 5")
        if type(global_pattern) is not int or not 1 <= global_pattern <= 15:
            raise ValueError("global_pattern harus integer antara 1 dan 15")
        if type(seconds) is not int or seconds <= 0:
            raise ValueError("seconds harus integer positif")

        self._timer.stop()
        self._remaining = seconds
        self._duration = seconds
        self._resolved = False

        self.stage_label.setText(
            f"Stage {stage} — Pattern {pattern_in_stage}/5"
        )
        self.timer_label.setText(f"⏱  {seconds}s")
        self.time_bar.setRange(0, seconds)
        self.time_bar.setValue(seconds)
        self.pattern_grid.set_grid(grid)
        self.detection_label.setText("Pattern Detection: SCANNING...")
        self.log.clear()

        self.artwork_count_label.setText(f"{global_pattern - 1} / 15")
        self.pattern_count_label.setText(f"{global_pattern} / 15")
        self._update_pattern_bank(global_pattern - 1, global_pattern)

        self._log(f"Pattern {global_pattern} ditampilkan", TEXT_DIM)
        self._timer.start()

    def set_scores(self, player1, player2):
        """Update the displayed scores."""
        for value in (player1, player2):
            if type(value) is not int or value < 0:
                raise ValueError("skor harus integer nonnegatif")
        self.player1_score_label.setText(f"🏅 P1   {player1}")
        self.player2_score_label.setText(f"🏅 P2   {player2}")

    def set_camera_status(self, status, message=None):
        """Forward camera status updates to the camera widget."""
        self.camera_widget.set_camera_status(status, message)

    def set_frame(self, frame):
        """Forward a camera frame to the camera widget."""
        self.camera_widget.set_frame(frame)

    def set_progress(self, completed, current=None):
        """Update the artwork counter and pattern bank progress."""
        if type(completed) is not int or not 0 <= completed <= 15:
            raise ValueError("completed harus integer antara 0 dan 15")
        if current is not None and (
            type(current) is not int or not 1 <= current <= 15
        ):
            raise ValueError("current harus integer antara 1 dan 15")

        self.artwork_count_label.setText(f"{completed} / 15")
        if current is not None:
            self.pattern_count_label.setText(f"{current} / 15")
        self._update_pattern_bank(completed, current)

    def _update_pattern_bank(self, completed, current):
        for index, item in enumerate(self.pattern_bank_labels, start=1):
            if index <= completed:
                item.setText("✓")
                item.setStyleSheet(
                    f"background: {GREEN}; color: #06110A; "
                    "border-radius: 3px; font-weight: bold;"
                )
            elif index == current:
                item.setText(f"{index:02d}")
                item.setStyleSheet(
                    f"background: {ACCENT}; color: white; "
                    "border-radius: 3px; font-weight: bold;"
                )
            else:
                item.setText(f"{index:02d}")
                item.setStyleSheet(
                    "background: #111820; color: #6B7280; "
                    "border: 1px solid #27313B; border-radius: 3px;"
                )

    def _tick(self):
        if self._remaining > 0:
            self._remaining -= 1

        self.timer_label.setText(f"⏱  {self._remaining}s")
        self.time_bar.setValue(self._remaining)

        if self._remaining <= 0:
            self._timer.stop()
            self._log("Waktu habis!", "#F4A261")
            self._finish(correct=False, time_left=0)

    def _sim_correct(self):
        if not self._timer.isActive() or self._resolved:
            return
        self.detection_label.setText("Pattern Detection: MATCHED")
        self._log(f"Pattern benar! Sisa {self._remaining}s", GREEN)
        self._timer.stop()
        self._finish(correct=True, time_left=self._remaining)

    def receive_detection(self, correct, accuracy):
        """Receive a result from the vision pipeline."""
        if not isinstance(correct, bool):
            raise TypeError("correct harus bool")
        if isinstance(accuracy, bool) or not isinstance(accuracy, (int, float)):
            raise TypeError("accuracy harus berupa angka")
        if not 0 <= accuracy <= 100:
            raise ValueError("accuracy harus berada pada rentang 0–100")
        if self._resolved:
            return

        self._timer.stop()
        label = "MATCHED" if correct else "NOT MATCHED"
        color = GREEN if correct else ACCENT
        self.detection_label.setText(
            f"Pattern Detection: {label} • {accuracy:.1f}%"
        )
        self._log(f"{'OK' if correct else 'MISS'} {accuracy:.1f}%", color)
        self._finish(correct=correct, time_left=self._remaining)

    def _finish(self, correct, time_left):
        if self._resolved:
            return
        self._resolved = True
        self.on_done(correct=correct, time_left=time_left)

    def _log(self, message, color=TEXT_MAIN):
        item = QListWidgetItem(message)
        item.setForeground(QColor(color))
        self.log.insertItem(0, item)
        while self.log.count() > 1:
            self.log.takeItem(self.log.count() - 1)

    def stop(self):
        """Stop the countdown without resolving the current pattern."""
        self._timer.stop()
