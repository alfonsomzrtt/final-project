"""Game lifecycle authority."""

from config.constants import PATTERNS_PER_STAGE, TOTAL_STAGES
from core.enums import GamePhase, Difficulty, Player
from core.results import PatternResult
from core.state import GameState
from game.puzzle_loader import PuzzleLoader
from game.scoring import Scoring
from game.timer import GameTimer


SUDDEN_DEATH_TIME_LIMIT = 15


class GameManager:
    def __init__(self):
        self.state = GameState()
        self.puzzle_loader = PuzzleLoader()
        self.scoring = Scoring()
        self.timer = GameTimer()

    def start_game(self, difficulty: Difficulty):
        self.state = GameState(
            phase=GamePhase.PLAYING,
            difficulty=difficulty,
            active_player=Player.PLAYER_1,
        )
        self.puzzle_loader.reset()
        self.puzzle_loader.load_game_patterns(difficulty)
        self.timer.reset()
        self.timer.set_difficulty(difficulty)

    def start_pattern(self):
        self.state.phase = GamePhase.PLAYING
        self.timer.start()

    def complete_pattern(self, result: PatternResult):
        self.timer.stop()
        player = self.state.active_player
        points = result.score

        if player == Player.PLAYER_1:
            self.state.score_player_1 += points
            self.state.stage_score_player_1 += points
            self.state.stage_time_player_1 += result.elapsed_time
            self.state.pattern_progress_player_1 += 1
        else:
            self.state.score_player_2 += points
            self.state.stage_score_player_2 += points
            self.state.stage_time_player_2 += result.elapsed_time
            self.state.pattern_progress_player_2 += 1

        if self.state.current_pattern < PATTERNS_PER_STAGE:
            self.state.current_pattern += 1
            return

        if player == Player.PLAYER_1:
            self.state.active_player = Player.PLAYER_2
            self.state.current_pattern = 1
            self.timer.reset()
            return

        self._complete_stage()

    def _complete_stage(self):
        winner = self.scoring.determine_stage_winner(
            self.state.stage_time_player_1,
            self.state.stage_time_player_2,
            self.state.stage_score_player_1,
            self.state.stage_score_player_2,
        )

        if winner == Player.PLAYER_1:
            self.state.stage_wins_player_1 += 1
        elif winner == Player.PLAYER_2:
            self.state.stage_wins_player_2 += 1

        if self.scoring.is_game_winner(self.state.stage_wins_player_1):
            self._complete_game(Player.PLAYER_1)
            return
        if self.scoring.is_game_winner(self.state.stage_wins_player_2):
            self._complete_game(Player.PLAYER_2)
            return

        self.state.phase = GamePhase.STAGE_RESULT

    def next_stage(self):
        if self.state.phase != GamePhase.STAGE_RESULT:
            return

        if self.state.current_stage >= TOTAL_STAGES:
            self._resolve_final_tie()
            return

        self.state.current_stage += 1
        self.state.current_pattern = 1
        self.state.active_player = Player.PLAYER_1
        self.state.stage_score_player_1 = 0
        self.state.stage_score_player_2 = 0
        self.state.stage_time_player_1 = 0.0
        self.state.stage_time_player_2 = 0.0
        self.state.pattern_progress_player_1 = 0
        self.state.pattern_progress_player_2 = 0
        self.timer.reset()
        self.state.phase = GamePhase.PLAYING

    def _resolve_final_tie(self):
        if self.state.stage_wins_player_1 != 1 or self.state.stage_wins_player_2 != 1:
            self.state.phase = GamePhase.GAME_RESULT
            return

        if self.state.score_player_1 > self.state.score_player_2:
            self._complete_game(Player.PLAYER_1)
        elif self.state.score_player_2 > self.state.score_player_1:
            self._complete_game(Player.PLAYER_2)
        else:
            self._start_sudden_death()

    def _start_sudden_death(self):
        self.state.phase = GamePhase.SUDDEN_DEATH
        self.state.sudden_death_round += 1
        self.state.active_player = Player.PLAYER_1
        self.timer.reset()
        self.timer.time_limit = SUDDEN_DEATH_TIME_LIMIT
        self.timer.start()

    def complete_sudden_death(self, player: Player, result: PatternResult):
        if self.state.phase != GamePhase.SUDDEN_DEATH:
            return

        self.timer.stop()

        if result.correct:
            self._complete_game(player)
        elif result.time_left == 0:
            self._start_sudden_death()

    def _complete_game(self, winner: Player):
        self.state.game_winner = winner
        self.state.phase = GamePhase.GAME_RESULT
        self.timer.stop()

    def switch_player(self):
        self.state.active_player = (
            Player.PLAYER_2
            if self.state.active_player == Player.PLAYER_1
            else Player.PLAYER_1
        )

    def get_current_pattern(self):
        return self.puzzle_loader.get_pattern(
            self.state.current_stage,
            self.state.current_pattern,
        )

    def reset_game(self):
        self.state = GameState()
        self.puzzle_loader.reset()
        self.timer.reset()
