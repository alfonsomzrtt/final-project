"""Main application window and screen navigation."""

import math

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QStackedWidget

from config.constants import PATTERNS_PER_STAGE, TOTAL_STAGES
from core.enums import Difficulty, GamePhase, GridSize, Player
from game.game_manager import GameManager
from ui.screens.game_result_screen import GameResultScreen
from ui.screens.game_screen import GameScreen
from ui.screens.lobby_screen import LobbyScreen
from ui.screens.stage_result_screen import StageResultScreen
from ui.workers.camera_worker import CameraWorker, VISION_STABLE


class MainWindow(QMainWindow):
    """Orchestrate screen navigation around a single game manager."""

    def __init__(
        self,
        parent=None,
        vision_grid_bounds=None,
        vision_raw_frame_snapshot_dir=None,
    ):
        super().__init__(parent)

        self.game_manager = GameManager()
        self.camera_worker = None
        self.last_vision_result = None
        self._vision_target_generation = 0
        self._accepted_vision_key = None
        self._accepted_vision_accuracy = None
        self.vision_grid_bounds = vision_grid_bounds
        self.vision_raw_frame_snapshot_dir = (
            vision_raw_frame_snapshot_dir
        )
        self.timer_refresh = QTimer(self)
        self.timer_refresh.setInterval(100)
        self.timer_refresh.timeout.connect(self._refresh_timer_display)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.lobby_screen = LobbyScreen(on_start=self._on_lobby_start)
        self.game_screen = GameScreen(on_done=self._on_game_done)
        self.game_screen.camera_widget.adjustment_changed.connect(
            self._on_camera_adjustment_changed
        )
        self.stage_result_screen = StageResultScreen(
            on_next=self._on_stage_next
        )
        self.game_result_screen = GameResultScreen(
            on_rematch=self._on_rematch
        )

        self.stack.addWidget(self.lobby_screen)
        self.stack.addWidget(self.game_screen)
        self.stack.addWidget(self.stage_result_screen)
        self.stack.addWidget(self.game_result_screen)
        self.show_lobby()

    def show_lobby(self):
        """Show the lobby screen."""
        self.timer_refresh.stop()
        self.stack.setCurrentWidget(self.lobby_screen)

    def show_game(self):
        """Show the gameplay screen."""
        self.stack.setCurrentWidget(self.game_screen)

    def show_stage_result(self):
        """Show the stage result screen."""
        self.timer_refresh.stop()
        self.stack.setCurrentWidget(self.stage_result_screen)

    def show_game_result(self):
        """Show the final game result screen."""
        self.timer_refresh.stop()
        self.stack.setCurrentWidget(self.game_result_screen)

    def _on_lobby_start(self, grid_size: GridSize, difficulty: Difficulty):
        """Start the first pattern for the selected game configuration."""
        self.game_manager.start_game(grid_size, difficulty)
        self.game_manager.start_pattern()
        self._start_camera()
        self._show_current_pattern()
        self.timer_refresh.start()
        self.show_game()

    def _start_camera(self):
        """Start one camera worker for the current game session."""
        if self.camera_worker is not None and self.camera_worker.isRunning():
            return

        self.camera_worker = CameraWorker(
            self,
            grid_bounds=self.vision_grid_bounds,
            raw_frame_snapshot_dir=(
                self.vision_raw_frame_snapshot_dir
            ),
        )
        self.camera_worker.frame_ready.connect(self.game_screen.set_frame)
        self.camera_worker.vision_result.connect(
            self._on_vision_result
        )
        self.camera_worker.status_changed.connect(
            self.game_screen.set_camera_status
        )
        self.camera_worker.error.connect(self._on_camera_error)
        self._set_camera_target(self.game_manager.get_current_pattern_grid())
        self.camera_worker.start()

    def _set_camera_target(self, target_pattern):
        """Set the worker target and advance the UI-side result generation."""
        self._vision_target_generation += 1
        self._accepted_vision_key = None
        self._accepted_vision_accuracy = None
        self.camera_worker.set_vision_target(target_pattern)

    def _stop_camera(self):
        """Stop the worker and wait for its capture resource to release."""
        if self.camera_worker is None:
            return

        if self.camera_worker.isRunning():
            self.camera_worker.stop()
            if not self.camera_worker.wait(2000):
                raise RuntimeError("Camera worker did not stop cleanly")
        self.camera_worker = None

    def _on_camera_adjustment_changed(self, name, value):
        if self.camera_worker is not None and self.camera_worker.isRunning():
            self.camera_worker.set_adjustment(name, value)

    def _on_camera_error(self, message):
        self.game_screen.set_camera_status("error", message)

    def _on_vision_result(self, result):
        """Complete one pattern only for an accepted stable vision result."""
        self.last_vision_result = result
        if not self._accept_vision_result(result):
            return

        accuracy = result.stabilization.check_result.accuracy
        self.timer_refresh.stop()
        self.game_manager.complete_pattern(True, accuracy)
        self._handle_manager_phase()

    def _accept_vision_result(self, result):
        """Validate a stable result without advancing the game.

        This is the integration contract boundary. Automatic completion is
        intentionally not performed until physical-camera validation is done.
        """
        if result.status != VISION_STABLE:
            return False
        stabilization = result.stabilization
        if stabilization is None or not stabilization.success:
            return False
        if self.game_manager.state.phase != GamePhase.PLAYING:
            return False
        if not self.game_manager.timer.running:
            return False
        active_target = self.game_manager.get_current_pattern_grid()
        if result.target_pattern != active_target:
            return False
        if result.target_generation != self._vision_target_generation:
            return False
        check_result = stabilization.check_result
        accuracy = check_result.accuracy
        if accuracy is None:
            return False
        key = (
            result.target_generation,
            tuple(tuple(row) for row in active_target),
            tuple(tuple(row) for row in check_result.detected_pattern),
        )
        if key == self._accepted_vision_key:
            return False
        self._accepted_vision_key = key
        self._accepted_vision_accuracy = accuracy
        return True

    def _show_current_pattern(self):
        """Render the pattern currently owned by GameManager."""
        stage = self.game_manager.state.current_stage
        pattern_in_stage = self.game_manager.state.current_pattern
        global_pattern = (
            (stage - 1) * PATTERNS_PER_STAGE
            + pattern_in_stage
        )

        self.game_screen.start(
            stage=stage,
            pattern_in_stage=pattern_in_stage,
            global_pattern=global_pattern,
            grid=self.game_manager.get_current_pattern_grid(),
            seconds=self.game_manager.timer.time_limit,
        )
        self.game_screen.set_scores(
            self.game_manager.state.score_player_1,
            self.game_manager.state.score_player_2,
        )
        if self.camera_worker is not None:
            self._set_camera_target(
                self.game_manager.get_current_pattern_grid()
            )

    def _on_game_done(self, **event):
        """Forward a matched detection to GameManager."""
        correct = event.get("correct")
        accuracy = event.get("accuracy")

        if not isinstance(correct, bool) or not correct:
            return
        if isinstance(accuracy, bool) or not isinstance(accuracy, (int, float)):
            raise TypeError("accuracy event must be a number")

        self.timer_refresh.stop()
        self.game_manager.complete_pattern(correct, accuracy)
        self._handle_manager_phase()

    def _handle_manager_phase(self):
        """Render the screen selected by the GameManager phase."""
        if self.game_manager.state.phase == GamePhase.PLAYING:
            self.game_manager.start_pattern()
            self._show_current_pattern()
            self.timer_refresh.start()
            self.show_game()
        elif self.game_manager.state.phase == GamePhase.GAME_RESULT:
            self.show_game_result()
        elif self.game_manager.state.phase == GamePhase.STAGE_RESULT:
            state = self.game_manager.state
            winner_labels = {
                Player.PLAYER_1: "Player 1",
                Player.PLAYER_2: "Player 2",
            }
            self.stage_result_screen.update(
                stage=state.current_stage,
                winner=winner_labels.get(state.stage_winner, "Seri"),
                wins_p1=state.stage_wins_player_1,
                wins_p2=state.stage_wins_player_2,
                score_p1=state.stage_score_player_1,
                score_p2=state.stage_score_player_2,
                is_last=state.current_stage == TOTAL_STAGES,
            )
            self.show_stage_result()

    def _refresh_timer_display(self):
        """Refresh the display and delegate expiry to GameManager."""
        timer = self.game_manager.timer
        if not timer.running:
            self.timer_refresh.stop()
            return

        remaining = timer.remaining_time()
        self.game_screen.set_time_remaining(max(0, math.ceil(remaining)))

        if timer.is_expired():
            self.game_screen.show_timeout()
            self.timer_refresh.stop()
            self.game_manager.timeout_pattern()
            self._handle_manager_phase()

    def _on_stage_next(self):
        """Start the next stage through GameManager."""
        self.timer_refresh.stop()
        self.game_manager.next_stage()

        if self.game_manager.state.phase == GamePhase.PLAYING:
            self.game_manager.start_pattern()
            self._show_current_pattern()
            self.timer_refresh.start()
            self.show_game()
        elif self.game_manager.state.phase == GamePhase.GAME_RESULT:
            self.show_game_result()
        elif self.game_manager.state.phase == GamePhase.SUDDEN_DEATH:
            raise RuntimeError("SUDDEN_DEATH screen is not available")

    def _on_rematch(self):
        """Reset the manager and return to the lobby."""
        self.timer_refresh.stop()
        self._stop_camera()
        self.game_manager.reset_game()
        self.show_lobby()

    def closeEvent(self, event):
        self.timer_refresh.stop()
        self._stop_camera()
        super().closeEvent(event)
