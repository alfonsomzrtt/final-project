"""
Game manager.

This module controls the game flow and updates the runtime game state.

The GameManager is responsible for game rules and state transitions.
It should not contain GUI code or computer vision processing.
"""

from core.enums import GamePhase, Difficulty, Player
from core.state import GameState
from core.results import PatternResult
# from config.constants import (
#     TOTAL_STAGES,
#     PATTERNS_PER_STAGE,
from game.level_manager import LevelManager
from game.puzzle_loader import PuzzleLoader
from game.scoring import Scoring
from game.timer import GameTimer




class GameManager:
    def __init__(self):
        self.state = GameState()

        self.level_manager = LevelManager()
        self.puzzle_loader = PuzzleLoader()
        self.scoring = Scoring()
        self.timer = GameTimer()

    def start_game(self, difficulty: Difficulty):
        """Start a new game with the selected difficulty."""

        self.state = GameState(
            phase=GamePhase.PLAYING,
            difficulty=difficulty,
            current_stage=1,
            current_pattern=1,
            active_player=Player.PLAYER_1,
         )
        
        self.puzzle_loader.reset()
        self.puzzle_loader.load_game_patterns(difficulty)

        self.timer.reset()
        self.timer.set_difficulty(difficulty)
    

    def start_pattern(self):
        """Start the current pattern."""

        self.state.phase = GamePhase.PLAYING
        self.timer.start()

    def complete_pattern(self, result: PatternResult):
        """ Handle the result of the current pattern """


        self.timer.stop()

        points = self.scoring.pattern_points(result.correct)

        if self.state.active_player == Player.PLAYER_1:
            self.state.score_player_1 += points
            self.state.stage_score_player_1 += points

        else:
            self.state.score_player_2 += points
            self.state.stage_score_player_2 += points

        has_next_pattern = self.level_manager.next_pattern(
            self.state
        )

        if not has_next_pattern:
            self.state.phase = GamePhase.STAGE_RESULT


    def next_stage(self):
        """Move to the next stage."""

        has_next_stage = self.level_manager.next_stage(
            self.state
        )

        if has_next_stage:
            self.state.phase = GamePhase.PLAYING
            self.timer.reset()
        else:
            self._complete_game()
            
    def _complete_game(self):
        """Handle completion of the entire game."""

        self.state.phase = GamePhase.GAME_RESULT

    def switch_player(self):
        """Switch the active player."""

        if self.state.active_player == Player.PLAYER_1:
            self.state.active_player = Player.PLAYER_2
        else:
            self.state.active_player = Player.PLAYER_1

    def get_current_pattern(self):
        """Return the pattern ID currently being played."""

        return self.puzzle_loader.get_pattern(
            self.state.current_stage,
            self.state.current_pattern,
        )

    def reset_game(self):
        """Reset the game to its initial state."""

        self.state = GameState()
        
        self.level_manager.reset(self.state)
        self.puzzle_loader.reset()
        self.timer.reset()