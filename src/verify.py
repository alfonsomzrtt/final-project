# verify.py — jalankan dari root project: python verify.py

import sys
import os
import time
import tempfile

# Gunakan Qt tanpa display fisik saat pengujian
os.environ["QT_QPA_PLATFORM"] = "offscreen"

# Hindari penggunaan plugin Qt bawaan OpenCV
os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH", None)

import cv2
import numpy as np

errors = []


# helpers
def assert_(value):
    assert value
    return value

def _raises(exception, func):
    try: 
        func()
    except exception:
        return True
    return False


def check(label, fn):
    try:
        fn()
        print(f"  ✓  {label}")
    except Exception as e:
        print(f"  ✗  {label}: {e}")
        errors.append(label)

def _raises_value_error(func):
    try:
        func()
    except ValueError:
        return True
    return False


# ─────────────────────────────────────────────────────────────────────────────
# config
# ─────────────────────────────────────────────────────────────────────────────

print("\n── config ───────────────────────────────")

check(
    "import config.constants",
    lambda: __import__("config.constants"),
)

check(
    "import config.settings",
    lambda: __import__("config.settings"),
)

check(
    "constants game values",
    lambda: assert_(
        __import__("config.constants", fromlist=["TOTAL_STAGES"])
        .TOTAL_STAGES == 3
    ),
)

check(
    "constants pattern values",
    lambda: assert_(
        __import__("config.constants", fromlist=["PATTERNS_PER_STAGE"])
        .PATTERNS_PER_STAGE == 5
    ),
)

check(
    "constants block classes",
    lambda: assert_(
        __import__("config.constants", fromlist=["TOTAL_BLOCK_CLASSES"])
        .TOTAL_BLOCK_CLASSES == 6
    ),
)


# ─────────────────────────────────────────────────────────────────────────────
# core.enums
# ─────────────────────────────────────────────────────────────────────────────

print("\n── core.enums ───────────────────────────")

check(
    "import core.enums",
    lambda: __import__("core.enums"),
)

check(
    "GamePhase enum",
    lambda: assert_(
        __import__("core.enums", fromlist=["GamePhase"]).GamePhase
    ),
)

check(
    "Difficulty enum",
    lambda: assert_(
        __import__("core.enums", fromlist=["Difficulty"]).Difficulty
    ),
)

check(
    "GridSize enum",
    lambda: assert_(
        __import__("core.enums", fromlist=["GridSize"]).GridSize
    ),
)

check(
    "Player enum",
    lambda: assert_(
        __import__("core.enums", fromlist=["Player"]).Player
    ),
)


# ─────────────────────────────────────────────────────────────────────────────
# core.state
# ─────────────────────────────────────────────────────────────────────────────

print("\n── core.state ───────────────────────────")

check(
    "import core.state",
    lambda: __import__("core.state"),
)

check(
    "GameState instance",
    lambda: assert_(
        __import__("core.state", fromlist=["GameState"]).GameState()
    ),
)

check(
    "GameState default phase",
    lambda: assert_(
        __import__("core.state", fromlist=["GameState"])
        .GameState()
        .phase
        == __import__("core.enums", fromlist=["GamePhase"])
        .GamePhase.LOBBY
    ),
)

check(
    "GameState default stage",
    lambda: assert_(
        __import__("core.state", fromlist=["GameState"])
        .GameState()
        .current_stage == 1
    ),
)

check(
    "GameState default pattern",
    lambda: assert_(
        __import__("core.state", fromlist=["GameState"])
        .GameState()
        .current_pattern == 1
    ),
)

check(
    "GameState default total scores",
    lambda: assert_(
        __import__("core.state", fromlist=["GameState"])
        .GameState()
        .score_player_1 == 0
        and
        __import__("core.state", fromlist=["GameState"])
        .GameState()
        .score_player_2 == 0
    ),
)

check(
    "GameState default stage scores",
    lambda: assert_(
        __import__("core.state", fromlist=["GameState"])
        .GameState()
        .stage_score_player_1 == 0
        and
        __import__("core.state", fromlist=["GameState"])
        .GameState()
        .stage_score_player_2 == 0
    ),
)

# ─────────────────────────────────────────────────────────────────────────────
# core.results
# ─────────────────────────────────────────────────────────────────────────────

print("\n── core.results ─────────────────────────")

from core.results import PatternResult


check(
    "import core.results",
    lambda: __import__("core.results"),
)

check(
    "PatternResult instance",
    lambda: assert_(
        PatternResult(
            correct=True,
            accuracy=0.96,
            elapsed_time=18.0,
            time_left=12,
            score=120,
        )
    ),
)

check(
    "PatternResult values",
    lambda: (
        lambda result: (
            assert_(result.correct is True),
            assert_(result.accuracy == 0.96),
            assert_(result.elapsed_time == 18.0),
            assert_(result.time_left == 12),
            assert_(result.score == 120),
        )
    )(
        PatternResult(
            correct=True,
            accuracy=0.96,
            elapsed_time=18.0,
            time_left=12,
            score=120,
        )
    ),
)

check(
    "PatternResult rejects accuracy > 1",
    lambda: assert_(
        _raises_value_error(
            lambda: PatternResult(
                correct=True,
                accuracy=1.1,
                elapsed_time=18.0,
                time_left=12,
                score=120,
            )
        )
    ),
)

check(
    "PatternResult rejects accuracy < 0",
    lambda: assert_(
        _raises_value_error(
            lambda: PatternResult(
                correct=True,
                accuracy=-0.1,
                elapsed_time=18.0,
                time_left=12,
                score=120,
            )
        )
    ),
)

check(
    "PatternResult rejects negative time",
    lambda: assert_(
        _raises_value_error(
            lambda: PatternResult(
                correct=True,
                accuracy=0.96,
                elapsed_time=31.0,
                time_left=-1,
                score=0,
            )
        )
    ),
)


# ─────────────────────────────────────────────────────────────────────────────
# game.level_manager
# ─────────────────────────────────────────────────────────────────────────────

print("\n── game.level_manager ──────────────────")

check(
    "import game.level_manager",
    lambda: __import__("game.level_manager"),
)

check(
    "LevelManager instance",
    lambda: assert_(
        __import__("game.level_manager", fromlist=["LevelManager"])
        .LevelManager()
    ),
)

check(
    "next_pattern()",
    lambda: (
        lambda state, manager: (
            manager.next_pattern(state),
            assert_(state.current_pattern == 2),
        )
    )(
        __import__("core.state", fromlist=["GameState"]).GameState(),
        __import__("game.level_manager", fromlist=["LevelManager"])
        .LevelManager(),
    ),
)


# ─────────────────────────────────────────────────────────────────────────────
# game.puzzle_loader
# ─────────────────────────────────────────────────────────────────────────────

print("\n── game.puzzle_loader ──────────────────")

check(
    "import game.puzzle_loader",
    lambda: __import__("game.puzzle_loader"),
)

check(
    "PuzzleLoader instance",
    lambda: assert_(
        __import__("game.puzzle_loader", fromlist=["PuzzleLoader"])
        .PuzzleLoader()
    ),
)

check(
    "supported grid sizes",
    lambda: (
        lambda loader: assert_(
            __import__("core.enums", fromlist=["GridSize"])
            .GridSize.TWO_BY_TWO in loader.supported_grid_sizes
            and __import__("core.enums", fromlist=["GridSize"])
            .GridSize.THREE_BY_THREE not in loader.supported_grid_sizes
        )
    )(
        __import__("game.puzzle_loader", fromlist=["PuzzleLoader"])
        .PuzzleLoader()
    ),
)

check(
    "load 15 Easy 2x2 patterns",
    lambda: (
        lambda loader: assert_(
            len(
                loader.load_game_patterns(
                    __import__("core.enums", fromlist=["GridSize"])
                    .GridSize.TWO_BY_TWO,
                    __import__("core.enums", fromlist=["Difficulty"])
                    .Difficulty.EASY,
                )
            ) == 15
        )
    )(
        __import__("game.puzzle_loader", fromlist=["PuzzleLoader"])
        .PuzzleLoader()
    ),
)

check(
    "load Normal and Hard 2x2 patterns",
    lambda: (
        lambda loader: assert_(
            len(
                loader.load_game_patterns(
                    __import__("core.enums", fromlist=["GridSize"])
                    .GridSize.TWO_BY_TWO,
                    __import__("core.enums", fromlist=["Difficulty"])
                    .Difficulty.NORMAL,
                )
            ) == 15
            and len(
                loader.load_game_patterns(
                    __import__("core.enums", fromlist=["GridSize"])
                    .GridSize.TWO_BY_TWO,
                    __import__("core.enums", fromlist=["Difficulty"])
                    .Difficulty.HARD,
                )
            ) == 15
        )
    )(
        __import__("game.puzzle_loader", fromlist=["PuzzleLoader"])
        .PuzzleLoader()
    ),
)

check(
    "Easy pattern ID format",
    lambda: (
        lambda loader: assert_(
            loader.load_game_patterns(
                __import__("core.enums", fromlist=["GridSize"])
                .GridSize.TWO_BY_TWO,
                __import__("core.enums", fromlist=["Difficulty"])
                .Difficulty.EASY,
            )[0].startswith("E")
        )
    )(
        __import__("game.puzzle_loader", fromlist=["PuzzleLoader"])
        .PuzzleLoader()
    ),
)

check(
    "pattern matrix resolves to 2x2 grid",
    lambda: (
        lambda loader: (
            lambda matrix: assert_(
                len(matrix) == 2
                and all(len(row) == 2 for row in matrix)
                and all(
                    cell in range(6)
                    for row in matrix
                    for cell in row
                )
            )
        )(
            loader.get_pattern_matrix(
                "E01",
                __import__("core.enums", fromlist=["GridSize"])
                .GridSize.TWO_BY_TWO,
            )
        )
    )(
        __import__("game.puzzle_loader", fromlist=["PuzzleLoader"])
        .PuzzleLoader()
    ),
)

check(
    "pattern bank IDs are unique",
    lambda: (
        lambda loader: (
            lambda ids: assert_(len(ids) == len(set(ids)) == 60)
        )(
            [
                pattern_id
                for difficulty_map in loader.pattern_bank.values()
                for patterns in difficulty_map.values()
                for pattern_id in patterns
            ]
        )
    )(
        __import__("game.puzzle_loader", fromlist=["PuzzleLoader"])
        .PuzzleLoader()
    ),
)

check(
    "3x3 pattern bank gap is explicit",
    lambda: assert_(
        _raises(
            NotImplementedError,
            lambda: __import__("game.puzzle_loader", fromlist=["PuzzleLoader"])
            .PuzzleLoader()
            .load_game_patterns(
                __import__("core.enums", fromlist=["GridSize"])
                .GridSize.THREE_BY_THREE,
                __import__("core.enums", fromlist=["Difficulty"])
                .Difficulty.EASY,
            ),
        )
    ),
)


# ─────────────────────────────────────────────────────────────────────────────
# game.scoring
# ─────────────────────────────────────────────────────────────────────────────

print("\n── game.scoring ─────────────────────────")

from game.scoring import Scoring
from core.enums import Player

check(
    "import game.scoring",
    lambda: __import__("game.scoring"),
)

check(
    "Scoring instance",
    lambda: assert_(Scoring()),
)

check(
    "correct pattern points",
    lambda: assert_(Scoring.pattern_points(True, 12) == 120),
)

check(
    "incorrect pattern points",
    lambda: assert_(Scoring.pattern_points(False, 12) == 0),
)

check(
    "stage winner by completion time",
    lambda: assert_(
        Scoring.determine_stage_winner(40.0, 45.0, 300, 500)
        == Player.PLAYER_1
    ),
)

check(
    "stage winner by score tie-breaker",
    lambda: assert_(
        Scoring.determine_stage_winner(40.0, 40.0, 300, 250)
        == Player.PLAYER_1
    ),
)

check(
    "stage tie when time and score equal",
    lambda: assert_(
        Scoring.determine_stage_winner(40.0, 40.0, 300, 300) is None
    ),
)

check("game winner threshold", lambda: assert_(Scoring.is_game_winner(2)))
check("not game winner below threshold", lambda: assert_(not Scoring.is_game_winner(1)))


# game.timer
# ─────────────────────────────────────────────────────────────────────────────

print("\n── game.timer ───────────────────────────")

check(
    "import game.timer",
    lambda: __import__("game.timer"),
)

check(
    "GameTimer instance",
    lambda: assert_(
        __import__("game.timer", fromlist=["GameTimer"]).GameTimer()
    ),
)

check(
    "set EASY time limit",
    lambda: (
        lambda timer: (
            timer.set_difficulty(
                __import__("core.enums", fromlist=["Difficulty"])
                .Difficulty.EASY
            ),
            assert_(timer.time_limit == 30),
        )
    )(
        __import__("game.timer", fromlist=["GameTimer"]).GameTimer()
    ),
)

check(
    "timer initially not expired",
    lambda: (
        lambda timer: (
            timer.set_difficulty(
                __import__("core.enums", fromlist=["Difficulty"])
                .Difficulty.EASY
            ),
            assert_(not timer.is_expired()),
        )
    )(
        __import__("game.timer", fromlist=["GameTimer"]).GameTimer()
    ),
)


# ─────────────────────────────────────────────────────────────────────────────
# vision.camera
# ─────────────────────────────────────────────────────────────────────────────

print("\n── vision.camera ────────────────────────")

check(
    "import vision.camera",
    lambda: __import__("vision.camera"),
)

check(
    "Camera instance",
    lambda: assert_(
        __import__("vision.camera", fromlist=["Camera"]).Camera()
    ),
)

check(
    "Camera initially closed",
    lambda: (
        lambda camera: assert_(not camera.is_opened())
    )(
        __import__("vision.camera", fromlist=["Camera"]).Camera()
    ),
)


# ─────────────────────────────────────────────────────────────────────────────
# game.game_manager
# ─────────────────────────────────────────────────────────────────────────────

print("\n── game.game_manager ───────────────────")

from game.game_manager import GameManager
from core.enums import GamePhase, Difficulty, GridSize, Player
from inspect import signature
from unittest.mock import patch


def complete_after(manager, elapsed, correct=True, accuracy=1.0):
    manager.start_pattern()
    start_time = manager.timer.start_time
    with patch(
        "game.timer.time.monotonic",
        return_value=start_time + elapsed,
    ):
        return manager.complete_pattern(correct, accuracy)


def timeout_after(manager, elapsed):
    manager.start_pattern()
    start_time = manager.timer.start_time
    with patch(
        "game.timer.time.monotonic",
        return_value=start_time + elapsed,
    ):
        return manager.timeout_pattern()


check("import game.game_manager", lambda: __import__("game.game_manager"))
check("GameManager instance", lambda: assert_(GameManager()))
check(
    "GameManager starts in LOBBY",
    lambda: assert_(GameManager().state.phase == GamePhase.LOBBY),
)
check(
    "GameManager.start_game()",
    lambda: (
        lambda manager: (
            manager.start_game(GridSize.TWO_BY_TWO, Difficulty.EASY),
            assert_(manager.state.phase == GamePhase.PLAYING),
        )
    )(GameManager()),
)
check(
    "GameManager current pattern",
    lambda: (
        lambda manager: (
            manager.start_game(GridSize.TWO_BY_TWO, Difficulty.EASY),
            assert_(manager.get_current_pattern().startswith("E")),
        )
    )(GameManager()),
)
check(
    "GameState stores grid size",
    lambda: (
        lambda manager: (
            manager.start_game(GridSize.TWO_BY_TWO, Difficulty.NORMAL),
            assert_(
                manager.state.grid_size == GridSize.TWO_BY_TWO
                and manager.state.difficulty == Difficulty.NORMAL
            ),
        )
    )(GameManager()),
)
check(
    "GameManager resolves current 2x2 grid",
    lambda: (
        lambda manager: (
            manager.start_game(GridSize.TWO_BY_TWO, Difficulty.HARD),
            (
                lambda grid: assert_(
                    len(grid) == 2
                    and all(len(row) == 2 for row in grid)
                    and all(
                        cell in range(6)
                        for row in grid
                        for cell in row
                    )
                )
            )(manager.get_current_pattern_grid()),
        )
    )(GameManager()),
)
check(
    "GameManager supports all 2x2 difficulties",
    lambda: (
        lambda difficulty: (
            lambda manager: (
                manager.start_game(GridSize.TWO_BY_TWO, difficulty),
                assert_(
                    manager.state.grid_size == GridSize.TWO_BY_TWO
                    and manager.state.difficulty == difficulty
                    and manager.get_current_pattern_grid()
                ),
            )
        )(GameManager())
    )(
        Difficulty.EASY
    )
    and (
        lambda manager: (
            manager.start_game(GridSize.TWO_BY_TWO, Difficulty.NORMAL),
            assert_(manager.get_current_pattern_grid()),
        )
    )(GameManager())
    and (
        lambda manager: (
            manager.start_game(GridSize.TWO_BY_TWO, Difficulty.HARD),
            assert_(manager.get_current_pattern_grid()),
        )
    )(GameManager()),
)
check(
    "GameManager rejects unsupported 3x3",
    lambda: (
        lambda manager: assert_(
            _raises(
                NotImplementedError,
                lambda: manager.start_game(
                    GridSize.THREE_BY_THREE,
                    Difficulty.EASY,
                ),
            )
            and manager.state.phase == GamePhase.LOBBY
        )
    )(GameManager()),
)
check(
    "MATCHED result uses timer and scoring authority",
    lambda: (
        lambda manager: (
            manager.start_game(GridSize.TWO_BY_TWO, Difficulty.EASY),
            (
                lambda result: assert_(
                    result.correct is True
                    and result.accuracy == 0.985
                    and result.elapsed_time == 4.75
                    and result.time_left == 25
                    and result.score == 250
                    and manager.state.score_player_1 == 250
                    and manager.state.stage_score_player_1 == 250
                    and manager.state.stage_time_player_1 == 4.75
                    and manager.state.pattern_progress_player_1 == 1
                    and manager.state.current_pattern == 2
                    and not manager.timer.running
                    and manager.timer.elapsed_time() == 4.75
                )
            )(complete_after(manager, elapsed=4.75, accuracy=0.985)),
        )
    )(GameManager()),
)
check(
    "NOT MATCHED completion records no score",
    lambda: (
        lambda manager: (
            manager.start_game(GridSize.TWO_BY_TWO, Difficulty.EASY),
            complete_after(
                manager,
                elapsed=2.0,
                correct=False,
                accuracy=0.4,
            ),
            assert_(
                manager.state.score_player_1 == 0
                and manager.state.stage_score_player_1 == 0
                and manager.state.stage_time_player_1 == 2.0
                and manager.state.current_pattern == 2
                and manager.state.pattern_progress_player_1 == 1
            ),
        )
    )(GameManager()),
)
check(
    "timeout before expiry leaves pattern active",
    lambda: (
        lambda manager: (
            manager.start_game(GridSize.TWO_BY_TWO, Difficulty.EASY),
            assert_(timeout_after(manager, 1.0) is None),
            assert_(
                manager.timer.running
                and manager.state.current_pattern == 1
                and manager.state.pattern_progress_player_1 == 0
            ),
        )
    )(GameManager()),
)
check(
    "expired timeout creates zero-score result and advances pattern",
    lambda: (
        lambda manager: (
            manager.start_game(GridSize.TWO_BY_TWO, Difficulty.EASY),
            (
                lambda result: assert_(
                    result is not None
                    and result.correct is False
                    and result.accuracy == 0.0
                    and result.elapsed_time == manager.timer.time_limit
                    and result.time_left == 0
                    and result.score == 0
                    and manager.state.score_player_1 == 0
                    and manager.state.stage_time_player_1
                    == manager.timer.time_limit
                    and manager.state.current_pattern == 2
                    and manager.state.pattern_progress_player_1 == 1
                    and not manager.timer.running
                )
            )(timeout_after(manager, manager.timer.time_limit)),
        )
    )(GameManager()),
)
check(
    "complete_pattern requires an active timer",
    lambda: (
        lambda manager: (
            manager.start_game(GridSize.TWO_BY_TWO, Difficulty.EASY),
            assert_(
                _raises(
                    RuntimeError,
                    lambda: manager.complete_pattern(True, 1.0),
                )
            ),
            assert_(manager.state.current_pattern == 1),
        )
    )(GameManager()),
)
check(
    "complete_pattern rejects injected result values",
    lambda: assert_(
        tuple(signature(GameManager.complete_pattern).parameters)
        == ("self", "correct", "accuracy")
    ),
)
check(
    "complete_pattern validates detection values",
    lambda: (
        lambda manager: (
            manager.start_game(GridSize.TWO_BY_TWO, Difficulty.EASY),
            manager.start_pattern(),
            assert_(
                _raises(
                    TypeError,
                    lambda: getattr(manager, "complete_pattern")(
                        "yes",
                        1.0,
                    ),
                )
                and _raises(
                    TypeError,
                    lambda: getattr(manager, "complete_pattern")(
                        True,
                        True,
                    ),
                )
                and _raises_value_error(
                    lambda: manager.complete_pattern(True, 1.01)
                )
            ),
            manager.timer.reset(),
        )
    )(GameManager()),
)
check(
    "Player 1 completes stage patterns then Player 2 starts",
    lambda: (
        lambda manager: (
            manager.start_game(GridSize.TWO_BY_TWO, Difficulty.EASY),
            [complete_after(manager, elapsed=1.0) for _ in range(5)],
            assert_(
                manager.state.active_player == Player.PLAYER_2
                and manager.state.current_pattern == 1
                and manager.state.pattern_progress_player_1 == 5
                and manager.state.phase == GamePhase.PLAYING
            ),
        )
    )(GameManager()),
)
check(
    "Stage winner uses completion time first and is exposed",
    lambda: (
        lambda manager: (
            manager.start_game(GridSize.TWO_BY_TWO, Difficulty.EASY),
            [complete_after(manager, elapsed=10.0) for _ in range(5)],
            [complete_after(manager, elapsed=11.0) for _ in range(5)],
            assert_(
                manager.state.stage_wins_player_1 == 1
                and manager.state.stage_wins_player_2 == 0
                and manager.state.stage_winner == Player.PLAYER_1
                and manager.state.phase == GamePhase.STAGE_RESULT
            ),
        )
    )(GameManager()),
)
check(
    "Stage winner can be Player 2",
    lambda: (
        lambda manager: (
            manager.start_game(GridSize.TWO_BY_TWO, Difficulty.EASY),
            [complete_after(manager, elapsed=11.0) for _ in range(5)],
            [complete_after(manager, elapsed=10.0) for _ in range(5)],
            assert_(
                manager.state.stage_winner == Player.PLAYER_2
                and manager.state.stage_wins_player_1 == 0
                and manager.state.stage_wins_player_2 == 1
                and manager.state.phase == GamePhase.STAGE_RESULT
            ),
        )
    )(GameManager()),
)
check(
    "Stage tie exposes no winner or stage win",
    lambda: (
        lambda manager: (
            manager.start_game(GridSize.TWO_BY_TWO, Difficulty.EASY),
            [complete_after(manager, elapsed=10.0) for _ in range(5)],
            [complete_after(manager, elapsed=10.0) for _ in range(5)],
            assert_(
                manager.state.stage_winner is None
                and manager.state.stage_wins_player_1 == 0
                and manager.state.stage_wins_player_2 == 0
                and manager.state.phase == GamePhase.STAGE_RESULT
            ),
        )
    )(GameManager()),
)
check(
    "Next stage resets stage-specific state",
    lambda: (
        lambda manager: (
            manager.start_game(GridSize.TWO_BY_TWO, Difficulty.EASY),
            [complete_after(manager, elapsed=10.0) for _ in range(5)],
            [complete_after(manager, elapsed=11.0) for _ in range(5)],
            (
                lambda total_score_p1, total_score_p2: (
                    manager.next_stage(),
                    assert_(
                        manager.state.current_stage == 2
                        and manager.state.current_pattern == 1
                        and manager.state.active_player == Player.PLAYER_1
                        and manager.state.phase == GamePhase.PLAYING
                        and manager.state.stage_winner is None
                        and manager.state.stage_score_player_1 == 0
                        and manager.state.stage_score_player_2 == 0
                        and manager.state.stage_time_player_1 == 0.0
                        and manager.state.stage_time_player_2 == 0.0
                        and manager.state.stage_wins_player_1 == 1
                        and manager.state.stage_wins_player_2 == 0
                        and manager.state.score_player_1 == total_score_p1
                        and manager.state.score_player_2 == total_score_p2
                    ),
                )
            )(
                manager.state.score_player_1,
                manager.state.score_player_2,
            ),
        )
    )(GameManager()),
)
check(
    "Sudden death phase exists",
    lambda: assert_(GamePhase.SUDDEN_DEATH),
)


# vision.preprocessing
# ─────────────────────────────────────────────────────────────────────────────

print("\n── vision.preprocessing ─────────────────")

check(
    "import vision.preprocessing",
    lambda: __import__("vision.preprocessing"),
)

check(
    "Preprocessor instance",
    lambda: assert_(
        __import__(
            "vision.preprocessing",
            fromlist=["Preprocessor"]
        ).Preprocessor()
    ),
)

check(
    "BGR to HSV",
    lambda: (
        lambda preprocessor: (
            assert_(
                preprocessor.to_hsv(
                    __import__("numpy").zeros((100, 100, 3), dtype="uint8")
                ).shape == (100, 100, 3)
            )
        )
    )(
        __import__(
            "vision.preprocessing",
            fromlist=["Preprocessor"]
        ).Preprocessor()
    ),
)

check(
    "red mask",
    lambda: (
        lambda preprocessor: (
            assert_(
                preprocessor.create_red_mask(
                    __import__("numpy").zeros(
                        (100, 100, 3),
                        dtype="uint8"
                    )
                ).shape == (100, 100)
            )
        )
    )(
        __import__(
            "vision.preprocessing",
            fromlist=["Preprocessor"]
        ).Preprocessor()
    ),
)

check(
    "noise removal",
    lambda: (
        lambda preprocessor: (
            assert_(
                preprocessor.remove_noise(
                    __import__("numpy").zeros(
                        (100, 100),
                        dtype="uint8"
                    )
                ).shape == (100, 100)
            )
        )
    )(
        __import__(
            "vision.preprocessing",
            fromlist=["Preprocessor"]
        ).Preprocessor()
    ),
)

check(
    "preprocessing pipeline",
    lambda: (
        lambda preprocessor: (
            assert_(
                preprocessor.process(
                    __import__("numpy").zeros(
                        (100, 100, 3),
                        dtype="uint8"
                    )
                ).shape == (100, 100)
            )
        )
    )(
        __import__(
            "vision.preprocessing",
            fromlist=["Preprocessor"]
        ).Preprocessor()
    ),
)

print("\n── vision.detector ─────────────────────")

check(
    "import vision.detector",
    lambda: __import__("vision.detector"),
)

check(
    "BlockDetector instance",
    lambda: assert_(
        __import__(
            "vision.detector",
            fromlist=["BlockDetector"]
        ).BlockDetector()
    ),
)

check(
    "find valid contours",
    lambda: (
        lambda detector, np: (
            assert_(
                len(
                    detector.find_valid_contours(
                        cv2.rectangle(
                            np.zeros(
                                (400, 400),
                                dtype="uint8"
                            ),
                            (50, 50),
                            (350, 350),
                            255,
                            -1,
                        )
                    )
                ) == 1
            )
        )
    )(
        __import__(
            "vision.detector",
            fromlist=["BlockDetector"]
        ).BlockDetector(),
        __import__("numpy"),
    ),
)

print("\n── vision.grid_mapper ─────────────────")

from vision.grid_mapper import GridMapper


check(
    "import vision.grid_mapper",
    lambda: __import__("vision.grid_mapper"),
)

check(
    "GridMapper 2x2",
    lambda: assert_(
        GridMapper(2)
    ),
)

check(
    "GridMapper 3x3",
    lambda: assert_(
        GridMapper(3)
    ),
)

check(
    "resize region",
    lambda: (
        lambda mapper: assert_(
            mapper.resize_region(
                np.zeros(
                    (300, 300),
                    dtype=np.uint8
                )
            ).shape == (600, 600)
        )
    )(GridMapper(2)),
)

check(
    "split 2x2 grid",
    lambda: (
        lambda mapper: (
            lambda cells: assert_(
                len(cells) == 2
                and len(cells[0]) == 2
                and cells[0][0].shape == (300, 300)
            )
        )(
            mapper.map(
                np.zeros(
                    (300, 300),
                    dtype=np.uint8
                )
            )
        )
    )(GridMapper(2)),
)

check(
    "split 3x3 grid",
    lambda: (
        lambda mapper: (
            lambda cells: assert_(
                len(cells) == 3
                and len(cells[0]) == 3
                and cells[0][0].shape == (200, 200)
            )
        )(
            mapper.map(
                np.zeros(
                    (300, 300),
                    dtype=np.uint8
                )
            )
        )
    )(GridMapper(3)),
)

from config.constants import (
    BLOCK_CLASS_RED,
    BLOCK_CLASS_WHITE,
)

print("\n── vision.orientation ──────────────────")

from vision.orientation import OrientationClassifier


check(
    "import vision.orientation",
    lambda: __import__("vision.orientation"),
)

check(
    "OrientationClassifier instance",
    lambda: assert_(
        OrientationClassifier()
    ),
)

check(
    "red ratio",
    lambda: (
        lambda classifier: assert_(
            abs(
                classifier.calculate_red_ratio(
                    np.ones(
                        (100, 100),
                        dtype=np.uint8
                    ) * 255
                ) - 1.0
            ) < 0.001
        )
    )(OrientationClassifier()),
)

check(
    "classify full red",
    lambda: (
        lambda classifier: assert_(
            classifier.classify_cell(
                np.ones(
                    (100, 100),
                    dtype=np.uint8
                ) * 255
            ) == BLOCK_CLASS_RED
        )
    )(OrientationClassifier()),
)

check(
    "classify white",
    lambda: (
        lambda classifier: assert_(
            classifier.classify_cell(
                np.zeros(
                    (100, 100),
                    dtype=np.uint8
                )
            ) == BLOCK_CLASS_WHITE
        )
    )(OrientationClassifier()),
)

print("\n── vision.pattern_matcher ──────────────")

from vision.pattern_matcher import PatternMatcher


check(
    "import vision.pattern_matcher",
    lambda: __import__("vision.pattern_matcher"),
)

check(
    "PatternMatcher instance",
    lambda: assert_(
        PatternMatcher()
    ),
)

check(
    "exact pattern accuracy",
    lambda: (
        lambda matcher: assert_(
            matcher.calculate_accuracy(
                [
                    [2, 0],
                    [1, 5],
                ],
                [
                    [2, 0],
                    [1, 5],
                ],
            ) == 1.0
        )
    )(PatternMatcher()),
)

check(
    "partial pattern accuracy",
    lambda: (
        lambda matcher: assert_(
            matcher.calculate_accuracy(
                [
                    [2, 0],
                    [1, 4],
                ],
                [
                    [2, 0],
                    [1, 5],
                ],
            ) == 0.75
        )
    )(PatternMatcher()),
)

check(
    "exact pattern match",
    lambda: (
        lambda matcher: assert_(
            matcher.is_match(
                [
                    [2, 0],
                    [1, 5],
                ],
                [
                    [2, 0],
                    [1, 5],
                ]
            )
        )
    )(PatternMatcher()),
)

check(
    "non-matching pattern",
    lambda: (
        lambda matcher: assert_(
            not matcher.is_match(
                [
                    [2, 0],
                    [1, 4],
                ],
                [
                    [2, 0],
                    [1, 5],
                ]
            )
        )
    )(PatternMatcher()),
)

print("\n── vision.pipeline ─────────────────────")

from vision.yolo_detector import CLASS_NAMES, Detection, YoloDetector
from vision.grid_reconstruction import (
    GridReconstructor,
    GridReconstructionResult,
    map_detection_class,
)
from vision.grid_pattern_checker import (
    GridPatternCheckResult,
    GridPatternChecker,
    STATUS_INVALID_RECONSTRUCTION,
    STATUS_MATCH,
    STATUS_MISMATCH,
)
from vision.pattern_stabilizer import (
    PatternStabilizationResult,
    PatternStabilizer,
    STATUS_PENDING,
    STATUS_REJECTED,
    STATUS_STABLE,
)
from vision.pipeline import (
    VisionPipeline,
    VisionResult,
)


def test_yolo_detector_adapter():
    class FakeNet:
        def __init__(self):
            self.input = None

        def setInput(self, blob, name):
            self.input = (blob, name)

        def forward(self, name):
            assert name == "output0"
            output = np.zeros((1, 10, 8400), dtype=np.float32)
            output[0, 0:4, 0] = [320, 320, 200, 100]
            output[0, 4, 0] = 0.95
            output[0, 0:4, 1] = [320, 320, 200, 100]
            output[0, 4, 1] = 0.80
            output[0, 0:4, 2] = [320, 320, 200, 100]
            output[0, 5, 2] = 0.90
            return output

    with patch("vision.yolo_detector.cv2.dnn.readNetFromONNX", return_value=FakeNet()):
        detector = YoloDetector(
            model_path="mock.onnx",
            confidence_threshold=0.25,
        )
        detections = detector.detect(np.zeros((640, 640, 3), dtype=np.uint8))

    assert (
        len(detections) == 2
        and isinstance(detections[0], Detection)
        and detections[0].class_id == 0
        and detections[0].class_name == "red_bottom_right"
        and abs(detections[0].confidence - 0.95) < 1e-6
        and detections[0].bbox_xyxy == (220, 270, 420, 370)
        and detections[1].class_id == 1
        and detector.net.input[0].shape == (1, 3, 640, 640)
        and detector.net.input[0].dtype == np.float32
        and detector.net.input[1] == "images"
    )


def test_yolo_decoder_matches_reference():
    detector = YoloDetector.__new__(YoloDetector)
    detector.confidence_threshold = 0.25
    detector.nms_threshold = 0.45
    rng = np.random.default_rng(42)
    output = np.zeros((1, 10, 8400), dtype=np.float32)
    output[0, :4] = rng.uniform(0, 640, (4, 8400))
    output[0, 2:4] = rng.uniform(1, 180, (2, 8400))
    output[0, 4:] = rng.uniform(0, 0.2, (6, 8400))

    cases = [
        (0.25, 640, 640, 1.0, 0.0, 0.0),
        (0.5, 1280, 720, 0.5, 0.0, 140.0),
        (0.9, 300, 900, 0.711, 213.0, 0.0),
    ]
    output[0, 0:4, 0:8] = np.array(
        [
            [320, 320, 200, 100],
            [320, 320, 200, 100],
            [320, 320, 200, 100],
            [0, 0, 20, 20],
            [640, 640, 40, 40],
            [320, 320, 50, 50],
            [320, 320, 50, 50],
            [320, 320, 50, 50],
        ],
        dtype=np.float32,
    ).T
    output[0, 4:, 0:8] = 0.0
    output[0, 4, 0] = 0.9
    output[0, 5, 1] = 0.8
    output[0, 4, 2] = 0.7
    output[0, 4, 3] = 0.9
    output[0, 4, 4] = 0.9
    output[0, 4, 5] = 0.8
    output[0, 5, 6] = 0.8
    output[0, 4, 7] = 0.8

    def reference(values, width, height, scale, pad_x, pad_y, threshold):
        values = values[0].T
        candidates = []
        for row in values:
            class_id = int(np.argmax(row[4:]))
            confidence = float(row[4 + class_id])
            if confidence < threshold:
                continue
            center_x, center_y, box_width, box_height = map(float, row[:4])
            box = (
                max(0, min(width, round(
                    (center_x - box_width / 2 - pad_x) / scale
                ))),
                max(0, min(height, round(
                    (center_y - box_height / 2 - pad_y) / scale
                ))),
                max(0, min(width, round(
                    (center_x + box_width / 2 - pad_x) / scale
                ))),
                max(0, min(height, round(
                    (center_y + box_height / 2 - pad_y) / scale
                ))),
            )
            if box[2] > box[0] and box[3] > box[1]:
                candidates.append(
                    Detection(
                        class_id=class_id,
                        class_name=CLASS_NAMES[class_id],
                        confidence=confidence,
                        bbox_xyxy=box,
                    )
                )
        return candidates

    for threshold, width, height, scale, pad_x, pad_y in cases:
        detector.confidence_threshold = threshold
        actual = detector._decode_output(
            output,
            width=width,
            height=height,
            scale=scale,
            pad_x=pad_x,
            pad_y=pad_y,
        )
        expected = reference(
            output, width, height, scale, pad_x, pad_y, threshold
        )
        actual = detector._class_aware_nms(actual)
        expected = detector._class_aware_nms(expected)
        assert len(actual) == len(expected)
        for got, want in zip(actual, expected):
            assert got.class_id == want.class_id
            assert got.class_name == want.class_name
            assert abs(got.confidence - want.confidence) < 1e-6
            assert np.allclose(got.bbox_xyxy, want.bbox_xyxy, atol=1)

    detector.confidence_threshold = 0.95
    assert detector._decode_output(
        output,
        width=640,
        height=640,
        scale=1.0,
        pad_x=0,
        pad_y=0,
    ) == []
    assert_(_raises(
        ValueError,
        lambda: detector.detect(np.zeros((0, 640, 3), dtype=np.uint8)),
    ))


check("YOLO vectorized decoder reference equivalence", test_yolo_decoder_matches_reference)


check("YOLO ONNX adapter", test_yolo_detector_adapter)

print("\n── vision.grid_reconstruction ──────────")


def test_yolo_class_mapping():
    expected = {
        "red_bottom_right": 5,
        "red_bottom_left": 4,
        "red_top_right": 3,
        "red_top_left": 2,
        "red": 0,
        "white": 1,
    }
    for class_name, pattern_class in expected.items():
        detection = Detection(
            class_id={
                "red_bottom_right": 0,
                "red_bottom_left": 1,
                "red_top_right": 2,
                "red_top_left": 3,
                "red": 4,
                "white": 5,
            }[class_name],
            class_name=class_name,
            confidence=0.9,
            bbox_xyxy=(10, 10, 20, 20),
        )
        assert map_detection_class(detection) == pattern_class


def test_grid_reconstruction():
    detections = [
        Detection(4, "red", 0.9, (10, 10, 40, 40)),
        Detection(5, "white", 0.9, (60, 10, 90, 40)),
        Detection(2, "red_top_right", 0.9, (10, 60, 40, 90)),
        Detection(0, "red_bottom_right", 0.9, (60, 60, 90, 90)),
    ]
    result = GridReconstructor((0, 0, 100, 100)).reconstruct(
        list(reversed(detections)),
        frame_size=(100, 100),
    )
    assert isinstance(result, GridReconstructionResult)
    assert result.valid
    assert result.matrix == [[0, 1], [3, 5]]


def test_grid_reconstruction_invalid_cases():
    reconstructor = GridReconstructor((0, 0, 100, 100))
    valid = Detection(4, "red", 0.9, (10, 10, 40, 40))

    empty = reconstructor.reconstruct([])
    assert not empty.valid and empty.matrix == [[None, None], [None, None]]

    missing = reconstructor.reconstruct([valid])
    assert not missing.valid and "missing cell [1][1]" in missing.errors

    duplicate = reconstructor.reconstruct([
        valid,
        Detection(5, "white", 0.9, (20, 20, 30, 30)),
    ])
    assert not duplicate.valid
    assert any("multiple detections" in error for error in duplicate.errors)

    outside = reconstructor.reconstruct([
        Detection(4, "red", 0.9, (120, 120, 130, 130)),
    ])
    assert not outside.valid
    assert "detection outside grid bounds" in outside.errors
    assert _raises(
        ValueError,
        lambda: reconstructor.reconstruct([], frame_size=(80, 100)),
    )
    assert _raises(
        ValueError,
        lambda: GridReconstructor((-1, 0, 100, 100)),
    )

    assert _raises(
        ValueError,
        lambda: reconstructor.reconstruct([
            Detection(4, "red", 0.9, (20, 20, 20, 30)),
        ]),
    )
    assert _raises(
        ValueError,
        lambda: map_detection_class(
            Detection(99, "unknown", 0.9, (10, 10, 20, 20))
        ),
    )


def test_grid_reconstruction_adaptive_geometry():
    detections = [
        Detection(0, "red_bottom_right", 0.9, (810, 130, 850, 170)),
        Detection(4, "red", 0.9, (600, 120, 640, 160)),
        Detection(5, "white", 0.9, (610, 360, 650, 400)),
        Detection(2, "red_top_right", 0.9, (820, 370, 860, 410)),
    ]
    result = GridReconstructor((42, 100, 300, 250)).reconstruct(
        detections,
        frame_size=(1280, 720),
    )
    assert result.valid
    assert result.matrix == [[0, 5], [1, 3]]

    shifted = [
        Detection(4, "red", 0.9, (605, 125, 650, 170)),
        Detection(5, "white", 0.9, (815, 130, 860, 175)),
        Detection(2, "red_top_right", 0.9, (610, 365, 655, 410)),
        Detection(0, "red_bottom_right", 0.9, (820, 370, 865, 415)),
    ]
    shifted_result = GridReconstructor((42, 100, 300, 250)).reconstruct(
        shifted,
        frame_size=(1280, 720),
    )
    assert shifted_result.valid
    assert shifted_result.matrix == [[0, 1], [3, 5]]

    extra = detections + [
        Detection(4, "red", 0.9, (1000, 500, 1040, 540)),
    ]
    extra_result = GridReconstructor((42, 100, 300, 250)).reconstruct(
        extra,
        frame_size=(1280, 720),
    )
    assert extra_result.valid
    assert extra_result.matrix == [[0, 5], [1, 3]]

    ambiguous = detections + [
        Detection(5, "white", 0.95, (605, 125, 645, 165)),
    ]
    ambiguous_result = GridReconstructor((42, 100, 300, 250)).reconstruct(
        ambiguous,
        frame_size=(1280, 720),
    )
    assert not ambiguous_result.valid
    assert _raises(
        ValueError,
        lambda: map_detection_class(
            Detection(0, "red", 0.9, (10, 10, 20, 20))
        ),
    )


def test_grid_match():
    from vision.pattern_matcher import PatternMatcher

    detections = [
        Detection(4, "red", 0.9, (10, 10, 40, 40)),
        Detection(5, "white", 0.9, (60, 10, 90, 40)),
        Detection(2, "red_top_right", 0.9, (10, 60, 40, 90)),
        Detection(0, "red_bottom_right", 0.9, (60, 60, 90, 90)),
    ]
    result = GridReconstructor((0, 0, 100, 100)).reconstruct(detections)
    assert PatternMatcher().match(
        result.matrix,
        [[0, 1], [3, 5]],
    ) == {"accuracy": 1.0, "is_match": True}


check("YOLO class mapping", test_yolo_class_mapping)
check("2x2 grid reconstruction", test_grid_reconstruction)
check("grid reconstruction invalid cases", test_grid_reconstruction_invalid_cases)
check(
    "adaptive grid reconstruction and extra detection rejection",
    test_grid_reconstruction_adaptive_geometry,
)
check("grid reconstruction pattern match", test_grid_match)

print("\n── vision.grid_pattern_checker ─────────")


def _checker_detections():
    return [
        Detection(4, "red", 0.9, (10, 10, 40, 40)),
        Detection(5, "white", 0.9, (60, 10, 90, 40)),
        Detection(2, "red_top_right", 0.9, (10, 60, 40, 90)),
        Detection(0, "red_bottom_right", 0.9, (60, 60, 90, 90)),
    ]


def test_grid_pattern_checker():
    checker = GridPatternChecker((0, 0, 100, 100))
    target = [[0, 1], [3, 5]]

    matched = checker.check(
        list(reversed(_checker_detections())),
        target,
        frame_size=(100, 100),
    )
    assert isinstance(matched, GridPatternCheckResult)
    assert (
        matched.status == STATUS_MATCH
        and matched.is_match
        and matched.detected_pattern == target
        and matched.accuracy == 1.0
        and matched.errors == ()
    )

    mismatched = checker.check(
        _checker_detections(),
        [[0, 1], [2, 5]],
    )
    assert (
        mismatched.status == STATUS_MISMATCH
        and not mismatched.is_match
        and mismatched.detected_pattern == [[0, 1], [3, 5]]
        and mismatched.accuracy == 0.75
    )


def test_grid_pattern_checker_invalid_reconstruction():
    checker = GridPatternChecker((0, 0, 100, 100))

    invalid = checker.check(
        _checker_detections()[:-1],
        [[0, 1], [3, 5]],
    )
    assert (
        invalid.status == STATUS_INVALID_RECONSTRUCTION
        and not invalid.is_match
        and invalid.accuracy is None
        and invalid.detected_pattern == [[0, 1], [3, None]]
        and invalid.errors
    )

    invalid_detection = checker.check(
        [Detection(99, "unknown", 0.9, (10, 10, 40, 40))],
        [[0, 1], [3, 5]],
    )
    assert (
        invalid_detection.status == STATUS_INVALID_RECONSTRUCTION
        and not invalid_detection.is_match
        and invalid_detection.accuracy is None
    )


def test_grid_pattern_checker_validates_target():
    checker = GridPatternChecker((0, 0, 100, 100))
    detections = _checker_detections()

    assert _raises(
        ValueError,
        lambda: checker.check(detections, [[0, 1, 2], [3, 5, 0]]),
    )
    assert _raises(
        ValueError,
        lambda: checker.check(detections, [[0, 1], [3, 6]]),
    )
    assert _raises(
        TypeError,
        lambda: checker.check(detections, None),
    )


def test_grid_pattern_checker_matches_pattern_matcher():
    from vision.pattern_matcher import PatternMatcher

    checker = GridPatternChecker((0, 0, 100, 100))
    target = [[0, 1], [3, 5]]
    result = checker.check(_checker_detections(), target)
    expected = PatternMatcher().match(result.detected_pattern, target)
    assert result.accuracy == expected["accuracy"]
    assert result.is_match == expected["is_match"]


check("grid pattern checker match and mismatch", test_grid_pattern_checker)
check(
    "grid pattern checker invalid reconstruction",
    test_grid_pattern_checker_invalid_reconstruction,
)
check(
    "grid pattern checker target validation",
    test_grid_pattern_checker_validates_target,
)
check(
    "grid pattern checker uses PatternMatcher",
    test_grid_pattern_checker_matches_pattern_matcher,
)

print("\n── vision.pattern_stabilizer ───────────")


def _stable_match_result(matrix=None):
    if matrix is None:
        matrix = [[0, 1], [3, 5]]
    return GridPatternCheckResult(
        status=STATUS_MATCH,
        detected_pattern=matrix,
        accuracy=1.0,
        is_match=True,
    )


def _stable_mismatch_result():
    return GridPatternCheckResult(
        status=STATUS_MISMATCH,
        detected_pattern=[[0, 1], [3, 5]],
        accuracy=0.75,
        is_match=False,
    )


def _stable_invalid_result():
    return GridPatternCheckResult(
        status=STATUS_INVALID_RECONSTRUCTION,
        detected_pattern=[[0, 1], [3, None]],
        accuracy=None,
        is_match=False,
        errors=("missing cell [1][1]",),
    )


def test_pattern_stabilizer_sequence():
    stabilizer = PatternStabilizer()
    target = [[0, 1], [3, 5]]

    first = stabilizer.update(_stable_match_result(), target)
    second = stabilizer.update(_stable_match_result(), target)
    third = stabilizer.update(_stable_match_result(), target)
    fourth = stabilizer.update(_stable_match_result(), target)

    assert (
        isinstance(first, PatternStabilizationResult)
        and first.status == STATUS_PENDING
        and not first.success
        and first.consecutive_matches == 1
        and second.consecutive_matches == 2
        and third.status == STATUS_STABLE
        and third.success
        and third.consecutive_matches == 3
        and fourth.status == STATUS_STABLE
        and not fourth.success
        and fourth.consecutive_matches == 4
    )


def test_pattern_stabilizer_resets_on_nonmatch_and_matrix_change():
    stabilizer = PatternStabilizer()
    target = [[0, 1], [3, 5]]
    stabilizer.update(_stable_match_result(), target)
    stabilizer.update(_stable_match_result(), target)

    mismatch = stabilizer.update(_stable_mismatch_result(), target)
    invalid = stabilizer.update(_stable_invalid_result(), target)
    changed = stabilizer.update(
        _stable_match_result([[0, 1], [5, 3]]),
        target,
    )
    assert (
        mismatch.status == STATUS_REJECTED
        and mismatch.consecutive_matches == 0
        and invalid.status == STATUS_REJECTED
        and invalid.consecutive_matches == 0
        and changed.status == STATUS_PENDING
        and changed.consecutive_matches == 1
        and not changed.success
    )


def test_pattern_stabilizer_target_change_and_explicit_reset():
    stabilizer = PatternStabilizer(minimum_matches=2)
    target_one = [[0, 1], [3, 5]]
    target_two = [[1, 0], [5, 3]]

    stabilizer.update(_stable_match_result(), target_one)
    stable_one = stabilizer.update(_stable_match_result(), target_one)
    changed_target = stabilizer.update(
        _stable_match_result([[1, 0], [5, 3]]),
        target_two,
    )
    assert stable_one.success
    assert (
        changed_target.status == STATUS_PENDING
        and changed_target.consecutive_matches == 1
        and not changed_target.success
    )

    stabilizer.reset()
    reset_first = stabilizer.update(
        _stable_match_result([[1, 0], [5, 3]]),
        target_two,
    )
    reset_second = stabilizer.update(
        _stable_match_result([[1, 0], [5, 3]]),
        target_two,
    )
    assert not reset_first.success and reset_second.success


def test_pattern_stabilizer_validates_threshold_and_results():
    assert _raises(ValueError, lambda: PatternStabilizer(0))
    assert _raises(ValueError, lambda: PatternStabilizer(-1))
    assert _raises(TypeError, lambda: PatternStabilizer(3.0))

    stabilizer = PatternStabilizer()
    assert _raises(
        TypeError,
        lambda: stabilizer.update(object(), [[0, 1], [3, 5]]),
    )
    assert _raises(
        ValueError,
        lambda: stabilizer.update(
            _stable_match_result(),
            [[0, 1, 2], [3, 5, 0]],
        ),
    )


check("pattern stabilizer consecutive matches", test_pattern_stabilizer_sequence)
check(
    "pattern stabilizer nonmatch and matrix reset",
    test_pattern_stabilizer_resets_on_nonmatch_and_matrix_change,
)
check(
    "pattern stabilizer target and explicit reset",
    test_pattern_stabilizer_target_change_and_explicit_reset,
)
check(
    "pattern stabilizer validation",
    test_pattern_stabilizer_validates_threshold_and_results,
)


check(
    "import vision.pipeline",
    lambda: __import__("vision.pipeline"),
)

check(
    "VisionPipeline instance",
    lambda: assert_(
        VisionPipeline()
    ),
)

check(
    "VisionResult",
    lambda: assert_(
        VisionResult(
            detected_pattern=None,
            accuracy=0.0,
            is_match=False,
            bounding_box=None,
        )
    ),
)

check(
    "pipeline no detection",
    lambda: (
        lambda pipeline: (
            lambda result: assert_(
                isinstance(result, VisionResult)
                and result.detected_pattern is None
                and result.accuracy == 0.0
                and result.is_match is False
                and result.bounding_box is None
            )
        )(
            pipeline.process(
                np.zeros(
                    (480, 640, 3),
                    dtype=np.uint8,
                ),
                [
                    [0, 1],
                    [1, 0],
                ],
            )
        )
    )(VisionPipeline()),
)

print("\n── api.messages ───────────────────────")

from api.messages import Message, MessageType


check(
    "import api.messages",
    lambda: __import__("api.messages"),
)

check(
    "MessageType",
    lambda: assert_(
        MessageType.SCORE_UPDATE.value
        == "score_update"
    ),
)

check(
    "Message creation",
    lambda: assert_(
        Message(
            type=MessageType.SCORE_UPDATE,
            data={
                "score": 5,
            },
        )
    ),
)

check(
    "Message to_dict",
    lambda: (
        lambda message: assert_(
            message.to_dict()
            == {
                "type": "score_update",
                "data": {
                    "score": 5,
                },
            }
        )
    )(
        Message(
            type=MessageType.SCORE_UPDATE,
            data={
                "score": 5,
            },
        )
    ),
)

check(
    "Message from_dict",
    lambda: (
        lambda message: assert_(
            message.type == MessageType.SCORE_UPDATE
            and message.data["score"] == 5
        )
    )(
        Message.from_dict(
            {
                "type": "score_update",
                "data": {
                    "score": 5,
                },
            }
        )
    ),
)

print("\n── api.session ────────────────────────")

from api.session import Session, SessionManager, SessionStatus


check(
    "import api.session",
    lambda: __import__("api.session"),
)

check(
    "SessionStatus",
    lambda: assert_(
        SessionStatus.WAITING.value == "waiting"
        and SessionStatus.READY.value == "ready"
        and SessionStatus.PLAYING.value == "playing"
        and SessionStatus.FINISHED.value == "finished"
    ),
)

check(
    "Session creation",
    lambda: assert_(
        Session(
            session_id="TEST001",
            host_id="P1",
            grid_size=2,
            difficulty="easy",
        )
    ),
)

check(
    "SessionManager instance",
    lambda: assert_(
        not SessionManager().is_active
    ),
)

check(
    "Set session",
    lambda: (
        lambda manager: (
            manager.set_session(
                Session(
                    session_id="TEST001",
                    host_id="P1",
                    grid_size=2,
                    difficulty="easy",
                )
            ),
            assert_(
                manager.is_active
                and manager.session is not None
                and manager.session.session_id == "TEST001"
            ),
        )
    )(SessionManager()),
)

check(
    "Add player",
    lambda: (
        lambda manager: (
            manager.set_session(
                Session(
                    session_id="TEST001",
                    host_id="P1",
                    grid_size=2,
                    difficulty="easy",
                )
            ),
            manager.add_player("P2"),
            assert_(
                manager.session is not None
                and manager.session.players == ["P1", "P2"]
            ),
        )
    )(SessionManager()),
)

check(
    "Update session status",
    lambda: (
        lambda manager: (
            manager.set_session(
                Session(
                    session_id="TEST001",
                    host_id="P1",
                    grid_size=2,
                    difficulty="easy",
                )
            ),
            manager.update_status(SessionStatus.READY),
            assert_(
                manager.session is not None
                and manager.session.status == SessionStatus.READY
            ),
        )
    )(SessionManager()),
)

check(
    "Clear session",
    lambda: (
        lambda manager: (
            manager.set_session(
                Session(
                    session_id="TEST001",
                    host_id="P1",
                    grid_size=2,
                    difficulty="easy",
                )
            ),
            manager.clear_session(),
            assert_(not manager.is_active),
        )
    )(SessionManager()),
)

print("\n── api.http_client ────────────────────")

from api.http_client import (
    HTTPClient,
    APIError,
    HTTPStatusError,
    APIConnectionError,
    APIResponseError,
)


check(
    "import api.http_client",
    lambda: __import__("api.http_client"),
)

check(
    "HTTPClient instance",
    lambda: assert_(
        isinstance(
            HTTPClient("http://localhost:8000"),
            HTTPClient,
        )
    ),
)

check(
    "Base URL",
    lambda: assert_(
        HTTPClient("http://localhost:8000/").base_url
        == "http://localhost:8000"
    ),
)

check(
    "Build URL",
    lambda: assert_(
        HTTPClient("http://localhost:8000")._build_url(
            "/api/sessions"
        )
        == "http://localhost:8000/api/sessions"
    ),
)

check(
    "Initial connection state",
    lambda: assert_(
        HTTPClient("http://localhost:8000").is_closed
    ),
)

check(
    "Async HTTP methods",
    lambda: assert_(
        all(
            __import__("inspect").iscoroutinefunction(method)
            for method in (
                HTTPClient.request,
                HTTPClient.get,
                HTTPClient.post,
                HTTPClient.put,
                HTTPClient.patch,
                HTTPClient.delete,
                HTTPClient.close,
            )
        )
    ),
)

check(
    "API exception hierarchy",
    lambda: assert_(
        issubclass(HTTPStatusError, APIError)
        and issubclass(APIConnectionError, APIError)
        and issubclass(APIResponseError, APIError)
    ),
)

check(
    "HTTPStatusError",
    lambda: assert_(
        HTTPStatusError(
            404,
            "Not Found",
            {"detail": "Session not found"},
        ).status == 404
    ),
)

print("\n── api.websocket_client ───────────────")

from api.websocket_client import (
    WebSocketClient,
    WebSocketError,
    WebSocketConnectionError,
    WebSocketMessageError,
)


check(
    "import api.websocket_client",
    lambda: __import__("api.websocket_client"),
)

check(
    "WebSocketClient instance",
    lambda: assert_(
        isinstance(
            WebSocketClient("ws://localhost:8000/ws"),
            WebSocketClient,
        )
    ),
)

check(
    "WebSocket URL validation",
    lambda: assert_(
        WebSocketClient("ws://localhost:8000/ws")._url
        == "ws://localhost:8000/ws"
    ),
)

check(
    "Initial connection state",
    lambda: assert_(
        not WebSocketClient(
            "ws://localhost:8000/ws"
        ).is_connected
    ),
)

check(
    "Async WebSocket methods",
    lambda: assert_(
        all(
            __import__("inspect").iscoroutinefunction(method)
            for method in (
                WebSocketClient.connect,
                WebSocketClient.send,
                WebSocketClient.receive,
                WebSocketClient.disconnect,
            )
        )
    ),
)

check(
    "WebSocket exception hierarchy",
    lambda: assert_(
        issubclass(WebSocketConnectionError, WebSocketError)
        and issubclass(WebSocketMessageError, WebSocketError)
    ),
)

check(
    "Invalid WebSocket URL",
    lambda: assert_(
        _raises_value_error(
            lambda: WebSocketClient("http://localhost:8000/ws")
        )
    ),
)

print("\n── config.settings (API) ─────────────")

from config.settings import (
    API_BASE_URL,
    WEBSOCKET_URL,
    API_TIMEOUT,
)

check("API base URL", lambda: assert_(
    isinstance(API_BASE_URL, str)
    and API_BASE_URL.startswith(("http://", "https://"))
))

check("WebSocket URL", lambda: assert_(
    isinstance(WEBSOCKET_URL, str)
    and WEBSOCKET_URL.startswith(("ws://", "wss://"))
))

check("API timeout", lambda: assert_(
    API_TIMEOUT > 0
))

print("\n── api.client ────────────────────────")

from api.client import APIClient

check("import api.client", lambda: __import__("api.client"))

check("APIClient instance", lambda: assert_(
    isinstance(APIClient(), APIClient)
))

check("HTTP and WebSocket integration", lambda: assert_(
    isinstance(APIClient().http, HTTPClient)
    and isinstance(APIClient().websocket, WebSocketClient)
))

check("Initial WebSocket state", lambda: assert_(
    not APIClient().is_websocket_connected
))

check("HTTP methods", lambda: assert_(
    all(
        __import__("inspect").iscoroutinefunction(method)
        for method in (
            APIClient.get,
            APIClient.post,
            APIClient.put,
            APIClient.patch,
            APIClient.delete,
        )
    )
))

check("WebSocket methods", lambda: assert_(
    all(
        __import__("inspect").iscoroutinefunction(method)
        for method in (
            APIClient.connect_websocket,
            APIClient.disconnect_websocket,
            APIClient.send,
            APIClient.receive,
            APIClient.close,
        )
    )
))


print("\n── ui.workers.api_worker ─────────────")

from ui.workers.api_worker import APIWorker, _APIThread

check("import ui.workers.api_worker", lambda: __import__(
    "ui.workers.api_worker"
))

check("APIWorker instance", lambda: assert_(
    isinstance(APIWorker(), APIWorker)
))

check("API thread", lambda: assert_(
    isinstance(APIWorker()._thread, _APIThread)
))

check("Initial worker state", lambda: assert_(
    not APIWorker().is_running
))

check("Worker signals", lambda: assert_(
    all(
        hasattr(APIWorker, name)
        for name in (
            "ready",
            "stopped",
            "connected",
            "disconnected",
            "message_received",
            "request_succeeded",
            "request_failed",
            "error",
        )
    )
))

check("HTTP worker methods", lambda: assert_(
    all(
        callable(getattr(APIWorker, name))
        for name in ("get", "post", "put", "patch", "delete")
    )
))

check("WebSocket worker methods", lambda: assert_(
    all(
        callable(getattr(APIWorker, name))
        for name in (
            "connect_websocket",
            "send",
            # "receive",
            "disconnect_websocket",
            "stop",
        )
    )
))

print("\n── ui.widgets.pattern_widget ─────────────")

from PyQt5.QtWidgets import QApplication 
from ui.widgets.pattern_widget import PatternGrid

app = QApplication.instance()
if app is None: 
    app = QApplication(sys.argv)

check(
    "pattern widget default grid",
    lambda: assert_(
        len(PatternGrid().grid) == 2
    ),
)

check(
    "pattern widget 3x3",
    lambda: assert_(
        len(PatternGrid(
            [[0, 1, 2], [3, 4, 5], [1, 0, 2]]
        ).grid) == 3
    ),
)

check(
    "pattern widget invalid grid",
    lambda: assert_(
        _raises(
            ValueError,
            lambda: PatternGrid([[0, 1], [2, 6]])
        )
    ),
)

check(
    "pattern widget non-square grid",
    lambda: assert_(
        _raises(
            ValueError,
            lambda: PatternGrid([[0, 1, 2], [3, 4, 5]])
        )
    ),
)

print("\n── ui.widgets.camera_widget ─────────────")
from ui.widgets.camera_widget import CameraWidget
from ui.workers.camera_worker import (
    CameraWorker,
    VISION_ERROR,
    VISION_GEOMETRY_UNCONFIGURED,
    VISION_INVALID_RECONSTRUCTION,
    VISION_PENDING,
    VISION_STABLE,
    VISION_TARGET_UNAVAILABLE,
    VisionFrameResult,
)
from vision.yolo_detector import Detection
from PyQt5.QtCore import Qt


def test_camera_widget():
    widget = CameraWidget()

    # Initial raw and mapped values
    assert widget.get_raw_adjustments() == {
        "brightness": 128,
        "contrast": 128,
        "saturation": 128,
    }

    assert widget.get_adjustments() == {
        "brightness": 128,
        "contrast": 134,
        "saturation": 122,
    }

    # Verify endpoints
    assert CameraWidget.remap_slider(0, "brightness") == 64
    assert CameraWidget.remap_slider(255, "brightness") == 191

    assert CameraWidget.remap_slider(0, "contrast") == 77
    assert CameraWidget.remap_slider(255, "contrast") == 191

    assert CameraWidget.remap_slider(0, "saturation") == 77
    assert CameraWidget.remap_slider(255, "saturation") == 166

    # Verify signal carries mapped value
    received = []
    widget.adjustment_changed.connect(
        lambda name, value: received.append((name, value))
    )

    widget.set_adjustment("brightness", 255)
    assert received[-1] == ("brightness", 191)

    # Verify reset
    widget.reset_adjustments()
    assert widget.get_raw_adjustments() == {
        "brightness": 128,
        "contrast": 128,
        "saturation": 128,
    }

    # Verify camera status
    widget.set_camera_status("connected")
    assert "Connected" in widget.status_label.text()

    widget.set_camera_status("error", "Device unavailable")
    assert "Camera Error" in widget.status_label.text()
    assert widget._frame is None

    # Verify invalid inputs
    try:
        widget.set_adjustment("unknown", 100)
    except ValueError:
        pass
    else:
        raise AssertionError("Unknown adjustment was accepted")

    widget.close()


check("camera widget", test_camera_widget)


def test_camera_worker_failure():
    class UnavailableCamera:
        def __init__(self):
            self.released = False

        def open(self):
            return False

        def release(self):
            self.released = True

    with patch("ui.workers.camera_worker.Camera", UnavailableCamera):
        worker = CameraWorker()
        statuses = []
        worker.status_changed.connect(
            lambda status, detail: statuses.append((status, detail)),
            Qt.DirectConnection,
        )
        worker.start()
        assert worker.wait(2000)

    assert statuses and statuses[0][0] == "error"


def test_camera_worker_frame_delivery():
    class FakeCamera:
        instances = []

        def __init__(self):
            self.released = False
            FakeCamera.instances.append(self)

        def open(self):
            return True

        def read(self):
            return np.zeros((2, 2, 3), dtype=np.uint8)

        def release(self):
            self.released = True

    with patch("ui.workers.camera_worker.Camera", FakeCamera):
        worker = CameraWorker()
        frames = []

        def receive(frame):
            frames.append(frame)
            worker.stop()

        worker.frame_ready.connect(receive, Qt.DirectConnection)
        worker.start()
        assert worker.wait(2000)

    assert (
        len(frames) == 1
        and frames[0].shape == (2, 2, 3)
        and FakeCamera.instances[0].released
    )


def test_camera_worker_yolo_overlay():
    class FakeCamera:
        instances = []

        def __init__(self):
            self.released = False
            self.read_count = 0
            FakeCamera.instances.append(self)

        def open(self):
            return True

        def read(self):
            self.read_count += 1
            frame = np.zeros((80, 120, 3), dtype=np.uint8)
            time.sleep(0.01)
            if self.read_count >= 20:
                worker.stop()
            return frame

        def release(self):
            self.released = True

    class FakeDetection:
        class_name = "red"
        confidence = 0.9
        bbox_xyxy = (10, 20, 50, 60)

    class FakeDetector:
        instances = []

        def __init__(self):
            self.calls = 0
            FakeDetector.instances.append(self)

        def detect(self, frame):
            self.calls += 1
            return [FakeDetection()]

    with patch("ui.workers.camera_worker.Camera", FakeCamera):
        worker = CameraWorker(detector_factory=FakeDetector)
        frames = []
        worker.frame_ready.connect(
            lambda frame: frames.append(frame),
            Qt.DirectConnection,
        )
        worker.start()
        assert worker.wait(2000)

    assert FakeCamera.instances[0].released
    assert FakeDetector.instances[0].calls >= 1
    assert any(np.any(frame[:, :, 1] > 0) for frame in frames)


def test_camera_worker_vision_pipeline():
    target = [[0, 1], [3, 5]]
    detections = [
        Detection(4, "red", 0.9, (10, 10, 40, 40)),
        Detection(5, "white", 0.9, (60, 10, 90, 40)),
        Detection(2, "red_top_right", 0.9, (10, 60, 40, 90)),
        Detection(0, "red_bottom_right", 0.9, (60, 60, 90, 90)),
    ]

    worker = CameraWorker(grid_bounds=(0, 0, 100, 100))
    target_missing = worker._process_vision_result(
        1,
        detections,
        (100, 100),
    )
    assert target_missing.status == VISION_TARGET_UNAVAILABLE

    worker.set_vision_target(target)
    geometry_worker = CameraWorker()
    geometry_worker.set_vision_target(target)
    geometry_missing = geometry_worker._process_vision_result(
        1,
        detections,
        (100, 100),
    )
    assert geometry_missing.status == VISION_GEOMETRY_UNCONFIGURED

    results = [
        worker._process_vision_result(frame_id, detections, (100, 100))
        for frame_id in (1, 2, 3)
    ]
    assert (
        [item.status for item in results]
        == [VISION_PENDING, VISION_PENDING, VISION_STABLE]
        and results[-1].stabilization.success
    )
    assert worker._process_vision_result(
        4,
        [],
        (100, 100),
    ).status == VISION_INVALID_RECONSTRUCTION

    worker.set_vision_target([[1, 0], [5, 3]])
    reset_result = worker._process_vision_result(
        5,
        detections,
        (100, 100),
    )
    assert reset_result.status == "mismatch"


def test_camera_worker_frame_id_deduplication_and_errors():
    from queue import Queue

    class FakeDetector:
        def detect(self, frame):
            return []

    worker = CameraWorker(grid_bounds=(0, 0, 100, 100))
    worker.set_vision_target([[0, 1], [3, 5]])
    results = []
    worker.vision_result.connect(
        lambda result: results.append(result),
        Qt.DirectConnection,
    )
    worker._inference_queue = Queue()
    worker._inference_queue.put((7, np.zeros((10, 10, 3), dtype=np.uint8)))
    worker._inference_queue.put((7, np.zeros((10, 10, 3), dtype=np.uint8)))
    worker._stop_event.set()
    worker._inference_loop(FakeDetector())
    assert len(results) == 1 and results[0].frame_id == 7

    class FailingDetector:
        def detect(self, frame):
            raise RuntimeError("synthetic inference failure")

    failing_worker = CameraWorker()
    failures = []
    failing_worker.vision_result.connect(
        lambda result: failures.append(result),
        Qt.DirectConnection,
    )
    failing_worker._inference_queue.put(
        (1, np.zeros((10, 10, 3), dtype=np.uint8))
    )
    failing_worker._stop_event.set()
    failing_worker._inference_loop(FailingDetector())
    assert len(failures) == 1 and failures[0].status == VISION_ERROR


check("camera worker failure", test_camera_worker_failure)
check("camera worker frame delivery", test_camera_worker_frame_delivery)
check("camera worker YOLO overlay", test_camera_worker_yolo_overlay)
check("camera worker vision pipeline", test_camera_worker_vision_pipeline)
check(
    "camera worker frame identity and errors",
    test_camera_worker_frame_id_deduplication_and_errors,
)


def test_camera_worker_raw_frame_snapshot():
    with tempfile.TemporaryDirectory() as directory:
        worker = CameraWorker(raw_frame_snapshot_dir=directory)
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        assert not worker._save_raw_frame(16, frame)
        assert worker._raw_frame_snapshot_path is None

        frame[100:200, 100:200] = (10, 80, 200)
        assert worker._save_raw_frame(17, frame)
        first_path = worker._raw_frame_snapshot_path
        worker._save_raw_frame(18, frame)

        assert first_path is not None
        saved = cv2.imread(str(first_path))
        assert saved is not None and saved.shape == (720, 1280, 3)
        assert worker._raw_frame_snapshot_path == first_path


check(
    "camera worker raw frame snapshot",
    test_camera_worker_raw_frame_snapshot,
)


def test_camera_worker_raw_frame_snapshot_retries_write_failure():
    with tempfile.TemporaryDirectory() as directory:
        worker = CameraWorker(raw_frame_snapshot_dir=directory)
        frame = np.full((20, 30, 3), 80, dtype=np.uint8)
        original_imwrite = cv2.imwrite
        try:
            cv2.imwrite = lambda path, value: False
            assert not worker._save_raw_frame(1, frame)
            assert worker._raw_frame_snapshot_path is None
            cv2.imwrite = original_imwrite
            assert worker._save_raw_frame(2, frame)
        finally:
            cv2.imwrite = original_imwrite
        assert worker._raw_frame_snapshot_path is not None


check(
    "camera worker raw frame snapshot write retry",
    test_camera_worker_raw_frame_snapshot_retries_write_failure,
)

# ─────────────────────────────────────────────────────────────────────────────
# ui.widgets.score_widget
# ─────────────────────────────────────────────────────────────────────────────

print("\n── ui.widgets.score_widget ─────────────")

from ui.widgets.score_widget import ScoreWidget



def test_score_widget():
    widget = ScoreWidget()

    # Initial scores
    assert widget.score_p1 == 0
    assert widget.score_p2 == 0
    assert "0" in widget.player1_label.text()
    assert "0" in widget.player2_label.text()

    # Set both scores
    widget.set_scores(120, 95)
    assert widget.score_p1 == 120
    assert widget.score_p2 == 95
    assert "120" in widget.player1_label.text()
    assert "95" in widget.player2_label.text()

    # Update individual scores
    widget.set_score(1, 35)
    assert widget.score_p1 == 35
    assert widget.score_p2 == 95
    assert "35" in widget.player1_label.text()

    widget.set_score(2, 45)
    assert widget.score_p1 == 35
    assert widget.score_p2 == 45
    assert "45" in widget.player2_label.text()

    # Reset scores
    widget.reset_scores()
    assert widget.score_p1 == 0
    assert widget.score_p2 == 0
    assert "0" in widget.player1_label.text()
    assert "0" in widget.player2_label.text()

    # Reject negative scores
    assert _raises_value_error(lambda: widget.set_scores(-1, 10))
    assert _raises_value_error(lambda: widget.set_score(1, -1))

    # Reject invalid score types
    assert _raises(TypeError, lambda: widget.set_scores(1.5, 10))
    assert _raises(TypeError, lambda: widget.set_scores("10", 10))
    assert _raises(TypeError, lambda: widget.set_scores(True, 10))

    # Reject invalid player identifiers
    assert _raises_value_error(lambda: widget.set_score(0, 10))
    assert _raises_value_error(lambda: widget.set_score(3, 10))
    assert _raises_value_error(lambda: widget.set_score("1", 10))

    # Invalid inputs must not alter the current scores
    assert widget.score_p1 == 0
    assert widget.score_p2 == 0

    widget.close()


check("score widget", test_score_widget)

print("\n── ui.widgets.status_widget ─────────────")
from ui.widgets.status_widget import StatusWidget


def test_status_widget():
    widget = StatusWidget()
    assert widget.status == "idle"
    assert widget.message is None
    assert widget.status_label.text() == "—"

    widget.set_status("ready")
    assert widget.status == "ready"
    assert widget.status_label.text() == "READY"

    widget.set_status("scanning", "Mendeteksi pola...")
    assert widget.status == "scanning"
    assert widget.message == "Mendeteksi pola..."
    assert widget.status_label.text() == "Mendeteksi pola..."

    widget.set_status("error")
    assert widget.status == "error"
    assert widget.status_label.text() == "ERROR"

    widget.reset()
    assert widget.status == "idle"
    assert widget.message is None
    assert widget.status_label.text() == "—"

    assert _raises(ValueError, lambda: widget.set_status("unknown"))
    assert _raises(TypeError, lambda: widget.set_status(123))
    assert _raises(TypeError, lambda: widget.set_status("ready", 123))
    widget.close()


check("status widget", test_status_widget)


print("\n── ui.widgets.timer_widget ─────────────")
from ui.widgets.timer_widget import TimerWidget


def test_timer_widget():
    widget = TimerWidget()
    assert widget.duration == 30
    assert widget.remaining_seconds == 30
    assert not widget.is_running
    assert widget.progress_bar.value() == 30

    widget.set_duration(10)
    assert widget.duration == 10
    assert widget.remaining_seconds == 10
    assert widget.progress_bar.maximum() == 10

    widget.set_remaining(6)
    assert widget.remaining_seconds == 6
    assert widget.progress_bar.value() == 6

    # Invoke one tick directly so the smoke test does not sleep.
    ticks = []
    timeouts = []
    widget.tick.connect(ticks.append)
    widget.timeout.connect(lambda: timeouts.append(True))

    widget._tick()
    assert widget.remaining_seconds == 5
    assert widget.progress_bar.value() == 5
    assert ticks == [5]
    assert timeouts == []

    widget.set_remaining(1)
    widget._tick()
    assert widget.remaining_seconds == 0
    assert ticks[-1] == 0
    assert timeouts == [True]
    assert not widget.is_running

    widget.reset()
    assert widget.remaining_seconds == 10
    assert widget.progress_bar.value() == 10

    widget.start()
    assert widget.is_running
    widget.stop()
    assert not widget.is_running
    assert widget.remaining_seconds == 10

    widget.reset(5)
    assert widget.duration == 5
    assert widget.remaining_seconds == 5

    assert _raises(ValueError, lambda: TimerWidget(0))
    assert _raises(TypeError, lambda: TimerWidget(1.5),  # type: ignore[arg-type] 
                   )
    assert _raises(ValueError, lambda: widget.set_duration(-1))
    assert _raises(TypeError, lambda: widget.set_duration(True))
    assert _raises(ValueError, lambda: widget.set_remaining(6))
    widget.close()


check("timer widget", test_timer_widget)

# ─────────────────────────────────────────────────────────────────────────────
# ui.main_window
# ─────────────────────────────────────────────────────────────────────────────

print("\n── ui.main_window ───────────────────────")

from ui.main_window import MainWindow


def test_main_window():
    window = MainWindow()

    assert window.game_manager is not None
    assert window.lobby_screen is not None
    assert window.game_screen is not None
    assert window.stage_result_screen is not None
    assert window.game_result_screen is not None
    assert window.stack.currentWidget() is window.lobby_screen

    window._on_lobby_start(GridSize.TWO_BY_TWO, Difficulty.EASY)
    assert window.stack.currentWidget() is window.game_screen

    window.show_stage_result()
    assert window.stack.currentWidget() is window.stage_result_screen

    window.game_manager.state.phase = GamePhase.STAGE_RESULT
    window.stage_result_screen.next_button.click()
    assert (
        window.stack.currentWidget() is window.game_screen
        and window.game_manager.state.phase == GamePhase.PLAYING
    )

    window.game_manager.state.phase = GamePhase.GAME_RESULT
    window.stage_result_screen.next_button.click()
    assert window.stack.currentWidget() is window.game_result_screen

    window.game_result_screen.rematch_button.click()
    assert window.stack.currentWidget() is window.lobby_screen

    window.close()


def test_main_window_runtime_start():
    configurations = (
        (GridSize.TWO_BY_TWO, Difficulty.EASY, 30),
        (GridSize.TWO_BY_TWO, Difficulty.NORMAL, 25),
        (GridSize.TWO_BY_TWO, Difficulty.HARD, 20),
    )

    for grid_size, difficulty, seconds in configurations:
        window = MainWindow()
        window._on_lobby_start(grid_size, difficulty)

        assert window.stack.currentWidget() is window.game_screen
        assert window.game_manager.state.grid_size == grid_size
        assert window.game_manager.state.difficulty == difficulty
        assert window.game_manager.state.phase == GamePhase.PLAYING
        assert window.game_manager.state.current_stage == 1
        assert window.game_manager.state.current_pattern == 1
        assert window.game_manager.timer.running
        assert window.game_manager.state.pattern_progress_player_1 == 0
        assert window.game_manager.state.pattern_progress_player_2 == 0
        assert window.game_manager.state.score_player_1 == 0
        assert window.game_manager.state.score_player_2 == 0
        assert not window.game_screen.is_resolved
        assert window.game_screen.remaining_seconds == seconds
        assert len(window.game_screen.pattern_grid.grid) == 2
        assert all(
            len(row) == 2
            for row in window.game_screen.pattern_grid.grid
        )
        assert window.stage_result_screen is not window.stack.currentWidget()
        assert window.game_result_screen is not window.stack.currentWidget()

        window.game_manager.timer.stop()
        window.close()


def test_main_window_rejects_unsupported_grid():
    window = MainWindow()

    assert _raises(
        NotImplementedError,
        lambda: window._on_lobby_start(
            GridSize.THREE_BY_THREE,
            Difficulty.EASY,
        ),
    )
    assert window.stack.currentWidget() is window.lobby_screen
    assert window.game_manager.state.phase == GamePhase.LOBBY
    assert not window.game_manager.timer.running

    window.close()


check("main window", test_main_window)


def test_main_window_pattern_completion():
    window = MainWindow()
    window._on_lobby_start(GridSize.TWO_BY_TWO, Difficulty.EASY)

    initial_pattern = window.game_manager.get_current_pattern()
    initial_score = window.game_manager.state.score_player_1

    window._on_game_done(correct=False, accuracy=0.25)
    assert (
        window.game_manager.get_current_pattern() == initial_pattern
        and window.game_manager.state.score_player_1 == initial_score
        and window.game_manager.timer.running
        and not window.game_screen.is_resolved
    )

    received = []
    original_complete = window.game_manager.complete_pattern

    def capture_completion(correct, accuracy):
        received.append((correct, accuracy))
        return original_complete(correct, accuracy)

    window.game_manager.complete_pattern = capture_completion
    window._on_game_done(correct=True, accuracy=0.875)

    assert received == [(True, 0.875)]
    assert window.game_manager.state.current_pattern == 2
    assert window.game_manager.state.pattern_progress_player_1 == 1
    assert window.game_manager.state.score_player_1 > 0
    assert window.game_manager.timer.running
    assert window.game_screen.pattern_count_label.text() == "2 / 15"
    assert window.game_screen.remaining_seconds == 30
    assert not window.game_screen.is_resolved
    assert window.stack.currentWidget() is window.game_screen

    window.game_manager.timer.stop()
    window.close()


check(
    "main window pattern completion",
    test_main_window_pattern_completion,
)


def test_main_window_vision_integration_contract():
    window = MainWindow()
    window.game_manager.start_game(GridSize.TWO_BY_TWO, Difficulty.EASY)
    window.game_manager.start_pattern()
    target = window.game_manager.get_current_pattern_grid()
    window._vision_target_generation = 1

    worker = CameraWorker(grid_bounds=(0, 0, 100, 100))
    worker.set_vision_target(target)
    class_by_pattern = {
        0: (4, "red"),
        1: (5, "white"),
        2: (3, "red_top_left"),
        3: (2, "red_top_right"),
        4: (1, "red_bottom_left"),
        5: (0, "red_bottom_right"),
    }
    detections = []
    for row, values in enumerate(target):
        for column, pattern_class in enumerate(values):
            class_id, class_name = class_by_pattern[pattern_class]
            x1 = 10 + column * 50
            y1 = 10 + row * 50
            detections.append(
                Detection(
                    class_id,
                    class_name,
                    0.9,
                    (x1, y1, x1 + 30, y1 + 30),
                )
            )
    results = [
        worker._process_vision_result(frame_id, detections, (100, 100))
        for frame_id in (1, 2, 3)
    ]
    stable = results[-1]
    assert stable.status == VISION_STABLE
    received = []
    original_complete = window.game_manager.complete_pattern

    def capture_completion(correct, accuracy):
        received.append((correct, accuracy))
        return original_complete(correct, accuracy)

    window.game_manager.complete_pattern = capture_completion
    window._on_vision_result(stable)
    assert received == [(True, 1.0)]
    assert window._accepted_vision_accuracy == 1.0
    assert window.game_manager.state.current_pattern == 2
    assert window.game_manager.state.pattern_progress_player_1 == 1

    # The old stable result must not complete the next pattern.
    window._on_vision_result(stable)
    assert received == [(True, 1.0)]
    assert window.game_manager.state.current_pattern == 2

    for status in (
        VISION_PENDING,
        "mismatch",
        VISION_INVALID_RECONSTRUCTION,
        VISION_ERROR,
    ):
        rejected = VisionFrameResult(
            frame_id=10,
            status=status,
            stabilization=stable.stabilization,
            target_pattern=target,
            target_generation=1,
        )
        assert not window._accept_vision_result(rejected)

    stale = VisionFrameResult(
        frame_id=11,
        status=VISION_STABLE,
        stabilization=stable.stabilization,
        target_pattern=target,
        target_generation=0,
    )
    assert not window._accept_vision_result(stale)

    old_target = VisionFrameResult(
        frame_id=12,
        status=VISION_STABLE,
        stabilization=stable.stabilization,
        target_pattern=[[1, 0], [1, 1]],
        target_generation=2,
    )
    assert not window._accept_vision_result(old_target)

    window.game_manager.state.phase = GamePhase.STAGE_RESULT
    assert not window._accept_vision_result(stable)
    window.game_manager.state.phase = GamePhase.PLAYING
    window.game_manager.timer.stop()
    assert not window._accept_vision_result(stable)
    window.close()


check(
    "main window vision integration contract",
    test_main_window_vision_integration_contract,
)


def test_main_window_timer_refresh():
    window = MainWindow()
    window._on_lobby_start(GridSize.TWO_BY_TWO, Difficulty.EASY)

    start_time = window.game_manager.timer.start_time
    with patch(
        "game.timer.time.monotonic",
        return_value=start_time + 1.25,
    ):
        window._refresh_timer_display()

    assert (
        window.game_screen.remaining_seconds == 29
        and window.game_manager.timer.running
        and window.timer_refresh.isActive()
    )

    window.timer_refresh.stop()
    window.close()


def test_main_window_timeout_refresh():
    window = MainWindow()
    window._on_lobby_start(GridSize.TWO_BY_TWO, Difficulty.EASY)
    timeout_calls = []
    original_timeout = window.game_manager.timeout_pattern

    def capture_timeout():
        timeout_calls.append(True)
        return original_timeout()

    window.game_manager.timeout_pattern = capture_timeout
    start_time = window.game_manager.timer.start_time
    with patch(
        "game.timer.time.monotonic",
        return_value=start_time + window.game_manager.timer.time_limit,
    ):
        window._refresh_timer_display()
        window._refresh_timer_display()

    assert (
        timeout_calls == [True]
        and window.game_screen.remaining_seconds == 30
        and window.game_manager.state.pattern_progress_player_1 == 1
        and window.game_manager.state.current_pattern == 2
        and window.game_manager.timer.running
        and window.timer_refresh.isActive()
    )

    window.timer_refresh.stop()
    window.close()


check("main window timer refresh", test_main_window_timer_refresh)
check("main window timeout refresh", test_main_window_timeout_refresh)


def test_main_window_stage_result_wiring():
    window = MainWindow()
    window._on_lobby_start(GridSize.TWO_BY_TWO, Difficulty.EASY)

    def complete_window_pattern(elapsed):
        window.game_manager.start_pattern()
        start_time = window.game_manager.timer.start_time
        with patch(
            "game.timer.time.monotonic",
            return_value=start_time + elapsed,
        ):
            window._on_game_done(correct=True, accuracy=1.0)

    for elapsed in (10.0,) * 5:
        complete_window_pattern(elapsed)
    for elapsed in (11.0,) * 5:
        complete_window_pattern(elapsed)

    state = window.game_manager.state
    assert (
        state.phase == GamePhase.STAGE_RESULT
        and state.pattern_progress_player_1 == 5
        and state.pattern_progress_player_2 == 5
        and state.current_stage == 1
        and state.stage_winner == Player.PLAYER_1
        and state.stage_wins_player_1 == 1
        and state.stage_wins_player_2 == 0
        and state.stage_score_player_1 == 1000
        and state.stage_score_player_2 == 950
        and window.stack.currentWidget() is window.stage_result_screen
        and "Player 1" in window.stage_result_screen.winner_label.text()
        and "1000" in window.stage_result_screen.scores_label.text()
    )

    window.stage_result_screen.next_button.click()
    assert (
        state.phase == GamePhase.PLAYING
        and state.current_stage == 2
        and state.current_pattern == 1
        and state.active_player == Player.PLAYER_1
        and state.stage_winner is None
        and state.stage_wins_player_1 == 1
        and state.stage_wins_player_2 == 0
        and state.score_player_1 == 1000
        and state.score_player_2 == 950
        and state.stage_score_player_1 == 0
        and state.stage_score_player_2 == 0
        and state.stage_time_player_1 == 0.0
        and state.stage_time_player_2 == 0.0
        and window.game_screen.stage_label.text() == "Stage 2 — Pattern 1/5"
        and window.game_screen.pattern_count_label.text() == "6 / 15"
        and window.game_manager.timer.running
    )

    window.game_manager.timer.stop()
    window.close()


check("main window stage result wiring", test_main_window_stage_result_wiring)


def test_main_window_stage_progression_and_game_result():
    window = MainWindow()
    window._on_lobby_start(GridSize.TWO_BY_TWO, Difficulty.EASY)

    def complete_player(elapsed):
        for _ in range(5):
            window.game_manager.start_pattern()
            start_time = window.game_manager.timer.start_time
            with patch(
                "game.timer.time.monotonic",
                return_value=start_time + elapsed,
            ):
                window._on_game_done(correct=True, accuracy=1.0)

    complete_player(10.0)
    complete_player(11.0)
    window.stage_result_screen.next_button.click()
    complete_player(11.0)
    complete_player(10.0)

    state = window.game_manager.state
    assert (
        state.current_stage == 2
        and state.stage_winner == Player.PLAYER_2
        and state.stage_wins_player_1 == 1
        and state.stage_wins_player_2 == 1
        and window.stack.currentWidget() is window.stage_result_screen
        and "Player 2" in window.stage_result_screen.winner_label.text()
        and "Stage 2" == window.stage_result_screen.stage_label.text()
    )

    window.stage_result_screen.next_button.click()
    assert (
        state.current_stage == 3
        and state.current_pattern == 1
        and state.active_player == Player.PLAYER_1
        and state.phase == GamePhase.PLAYING
        and state.stage_wins_player_1 == 1
        and state.stage_wins_player_2 == 1
        and window.game_screen.stage_label.text() == "Stage 3 — Pattern 1/5"
    )

    complete_player(10.0)
    complete_player(11.0)
    assert (
        state.phase == GamePhase.GAME_RESULT
        and window.stack.currentWidget() is window.game_result_screen
    )

    window.game_manager.timer.stop()
    window.close()


check(
    "main window stage progression and game result",
    test_main_window_stage_progression_and_game_result,
)
check("main window runtime start", test_main_window_runtime_start)
check(
    "main window rejects unsupported grid",
    test_main_window_rejects_unsupported_grid,
)

# ─────────────────────────────────────────────────────────────────────────────
# ui.screens.lobby_screen
# ─────────────────────────────────────────────────────────────────────────────

print("\n── ui.screens.lobby_screen ──────────────")

from ui.screens.lobby_screen import LobbyScreen


def test_lobby_screen():
    started = []

    widget = LobbyScreen(
        on_start=lambda grid_size, difficulty: started.append(
            (grid_size, difficulty)
        )
    )

    # Initial state
    assert widget.start_button.isEnabled()
    assert "Player 1" in widget._player_labels[1].text()
    assert "Menunggu" in widget._player_labels[1].text()
    assert "Player 2" in widget._player_labels[2].text()
    assert "Menunggu" in widget._player_labels[2].text()
    assert (
        widget.selected_grid_size()
        == __import__("core.enums", fromlist=["GridSize"]).GridSize.TWO_BY_TWO
    )
    assert (
        widget.selected_difficulty()
        == __import__("core.enums", fromlist=["Difficulty"]).Difficulty.EASY
    )

    widget.set_grid_size(
        __import__("core.enums", fromlist=["GridSize"])
        .GridSize.THREE_BY_THREE
    )
    widget.set_difficulty(
        __import__("core.enums", fromlist=["Difficulty"])
        .Difficulty.HARD
    )
    assert (
        widget.selected_grid_size()
        == __import__("core.enums", fromlist=["GridSize"]).GridSize.THREE_BY_THREE
    )
    assert (
        widget.selected_difficulty()
        == __import__("core.enums", fromlist=["Difficulty"]).Difficulty.HARD
    )

    # Player status updates
    widget.set_player_status(1, "ready")
    assert "Ready" in widget._player_labels[1].text()

    widget.set_player_status(2, "disconnected", "Koneksi terputus")
    assert "Disconnected" in widget._player_labels[2].text()
    assert "Koneksi terputus" in widget._player_labels[2].text()

    widget.set_player_status(2, "error", "Perangkat tidak tersedia")
    assert "Error" in widget._player_labels[2].text()
    assert "Perangkat tidak tersedia" in widget._player_labels[2].text()

    # Start button state and callback
    widget.set_start_enabled(False)
    assert not widget.start_button.isEnabled()

    widget.set_start_enabled(True)
    assert widget.start_button.isEnabled()
    widget.start_button.click()
    assert started == [
        (
            __import__("core.enums", fromlist=["GridSize"])
            .GridSize.THREE_BY_THREE,
            __import__("core.enums", fromlist=["Difficulty"])
            .Difficulty.HARD,
        )
    ]

    # Reject invalid player IDs, statuses, and messages
    assert _raises_value_error(
        lambda: widget.set_player_status(3, "ready")
    )
    assert _raises_value_error(
        lambda: widget.set_player_status(1, "unknown")
    )
    assert _raises(
        TypeError,
        lambda: widget.set_player_status(1, "ready", 123)
    )

    assert _raises(
        TypeError,
        lambda: widget.set_grid_size(2),
    )
    assert _raises(
        TypeError,
        lambda: widget.set_difficulty("easy"),
    )

    widget.close()


check("lobby screen", test_lobby_screen)

# ─────────────────────────────────────────────────────────────────────────────
# ui.screens.game_screen
# ─────────────────────────────────────────────────────────────────────────────

print("\n── ui.screens.game_screen ───────────────")

from ui.screens.game_screen import GameScreen


def test_game_screen():
    completed = []

    widget = GameScreen(
        on_done=lambda **kwargs: completed.append(kwargs)
    )

    # Initial state
    assert widget.remaining_seconds == 30
    assert widget.is_resolved
    assert not hasattr(widget, "_timer")
    assert widget.time_bar.value() == 30
    assert widget.player1_score_label.text().endswith("0")
    assert widget.player2_score_label.text().endswith("0")

    # Start a pattern
    grid = [
        [0, 1],
        [2, 3],
    ]

    widget.start(
        stage=1,
        pattern_in_stage=2,
        global_pattern=2,
        grid=grid,
        seconds=20,
    )

    assert not widget.is_resolved
    assert widget.remaining_seconds == 20
    assert widget.time_bar.maximum() == 20
    assert widget.time_bar.value() == 20
    assert "Stage 1" in widget.stage_label.text()
    assert "Pattern 2/5" in widget.stage_label.text()
    assert widget.pattern_count_label.text() == "2 / 15"

    # The controller supplies timer display updates; the screen does not tick.
    widget.set_time_remaining(17)
    assert widget.remaining_seconds == 17
    assert widget.timer_label.text().endswith("17s")
    assert widget.time_bar.value() == 17

    # Update scores and progress
    widget.set_scores(120, 95)
    assert "120" in widget.player1_score_label.text()
    assert "95" in widget.player2_score_label.text()

    widget.set_progress(3, 4)
    assert widget.artwork_count_label.text() == "3 / 15"
    assert widget.pattern_count_label.text() == "4 / 15"

    # A mismatch updates presentation and leaves scanning active.
    widget.receive_detection(
        correct=False,
        accuracy=0.5,
    )
    assert not widget.is_resolved
    assert "NOT MATCHED" in widget.detection_label.text()
    assert "50.0%" in widget.detection_label.text()
    assert completed == []

    # A match resolves the pattern and reports normalized accuracy.
    widget.receive_detection(
        correct=True,
        accuracy=0.985,
    )
    assert widget.is_resolved
    assert "MATCHED" in widget.detection_label.text()
    assert completed == [
        {"correct": True, "accuracy": 0.985}
    ]

    # Ignore duplicate detection
    widget.receive_detection(
        correct=False,
        accuracy=0.5,
    )
    assert len(completed) == 1

    # A controller-reported timeout is presentation only.
    widget.start(1, 2, 2, grid, 20)
    widget.show_timeout()
    assert widget.is_resolved
    assert widget.remaining_seconds == 0
    assert widget.time_bar.value() == 0
    assert "TIMEOUT" in widget.detection_label.text()
    assert len(completed) == 1

    # Reject invalid inputs
    assert _raises_value_error(
        lambda: widget.start(4, 1, 1, grid, 30)
    )
    assert _raises_value_error(
        lambda: widget.start(1, 6, 1, grid, 30)
    )
    assert _raises_value_error(
        lambda: widget.start(1, 1, 1, grid, 0)
    )
    assert _raises(
        TypeError,
        lambda: widget.receive_detection("yes", 0.95)
    )
    assert _raises_value_error(
        lambda: widget.receive_detection(True, 1.01)
    )
    assert _raises_value_error(
        lambda: widget.set_time_remaining(-1)
    )
    assert _raises_value_error(
        lambda: widget.set_scores(-1, 10)
    )

    widget.stop()
    widget.close()


check("game screen", test_game_screen)

print("\n── ui.screens.stage_result_screen ─────────")

from ui.screens.stage_result_screen import StageResultScreen


def test_stage_result_screen():
    received = []
    screen = StageResultScreen(
        on_next=lambda: received.append(True)
    )

    assert screen.winner_label.text() == "Pemenang: —"

    screen.update(
        stage=1,
        winner="Player 1",
        wins_p1=1,
        wins_p2=0,
        score_p1=150,
        score_p2=100,
        is_last=False,
    )

    assert screen.stage_label.text() == "Stage 1"
    assert "Player 1" in screen.winner_label.text()
    assert "P1 1" in screen.wins_label.text()
    assert "150" in screen.scores_label.text()
    assert screen.next_button.text() == "Stage Berikutnya →"

    screen.next_button.click()
    assert received == [True]

    screen.update(
        stage=3,
        winner="Player 2",
        wins_p1=1,
        wins_p2=2,
        score_p1=300,
        score_p2=400,
        is_last=True,
    )

    assert screen.stage_label.text() == "Stage 3"
    assert "Player 2" in screen.winner_label.text()
    assert screen.next_button.text() == "Lihat Hasil Akhir 🏆"

    assert _raises_value_error(
        lambda: screen.update(
            4, "Player 1", 1, 0, 100, 50, False
        )
    )

    screen.close()


check("stage result screen", test_stage_result_screen)


print("\n── ui.screens.game_result_screen ───────")

from ui.screens.game_result_screen import GameResultScreen


def test_game_result_screen():
    calls = []
    screen = GameResultScreen(
        on_rematch=lambda: calls.append("rematch")
    )

    # Default state
    assert screen.nlbl.text() == "Belum ada pemenang"
    assert screen.wlbl.text() == "Stage Win: 0–0"
    assert screen.leaderboard.count() == 0

    # Update result
    screen.set_result(
        winner="Player 1",
        wins_p1=2,
        wins_p2=1,
        leaderboard=[
            ("Player 1", 1250),
            ("Player 2", 980),
            ("Player 3", 870),
        ],
        accuracy=93.5,
        completion_time=18.2,
        correct_placements=14,
        wrong_placements=1,
        artwork_revealed=15,
    )

    assert screen.nlbl.text() == "Player 1"
    assert screen.wlbl.text() == "Stage Win: 2–1"

    # Leaderboard
    assert screen.leaderboard.count() == 3
    item = screen.leaderboard.item(0)

    assert item is not None
    assert "Player 1" in item.text()
    assert "1250" in item.text()

    # Result details
    assert screen.details["accuracy"].text() == "93.5%"
    assert screen.details["completion_time"].text() == "18.2s"
    assert screen.details["correct_placements"].text() == "14"
    assert screen.details["wrong_placements"].text() == "1"
    assert screen.details["artwork_revealed"].text() == "15"

    # Rematch callback
    screen.rematch_button.click()
    assert calls == ["rematch"]

    # Invalid winner
    try:
        screen.set_result(
            "", 2, 1, [], 90, 10, 5, 1, 5
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Empty winner accepted")

    # Invalid accuracy
    try:
        screen.set_result(
            "Player 1", 2, 1, [], 101, 10, 5, 1, 5
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid accuracy accepted")

    # Invalid score
    try:
        screen.set_result(
            "Player 1", -1, 1, [], 90, 10, 5, 1, 5
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Negative stage win accepted")

    screen.close()


check("game result screen", test_game_result_screen)




# ─────────────────────────────────────────────────────────────────────────────
# Result
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 50)

if errors:
    print(f"✗  {len(errors)} check gagal:")
    for error in errors:
        print(f"   - {error}")

    sys.exit(1)

else:
    print("✓  Semua check passed")
    sys.exit(0)
