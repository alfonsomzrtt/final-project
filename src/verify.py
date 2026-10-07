# verify.py — jalankan dari root project: python verify.py

import sys
import os

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
    "load 15 Easy patterns",
    lambda: (
        lambda loader: assert_(
            len(
                loader.load_game_patterns(
                    __import__("core.enums", fromlist=["Difficulty"])
                    .Difficulty.EASY
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
                __import__("core.enums", fromlist=["Difficulty"])
                .Difficulty.EASY
            )[0].startswith("E")
        )
    )(
        __import__("game.puzzle_loader", fromlist=["PuzzleLoader"])
        .PuzzleLoader()
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
from core.enums import GamePhase, Difficulty, Player
from core.results import PatternResult

def pattern(correct=True, elapsed=10.0, time_left=20, score=200, accuracy=1.0):
    return PatternResult(
        correct=correct,
        accuracy=accuracy,
        elapsed_time=elapsed,
        time_left=time_left,
        score=score,
    )

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
            manager.start_game(Difficulty.EASY),
            assert_(manager.state.phase == GamePhase.PLAYING),
        )
    )(GameManager()),
)
check(
    "GameManager current pattern",
    lambda: (
        lambda manager: (
            manager.start_game(Difficulty.EASY),
            assert_(manager.get_current_pattern().startswith("E")),
        )
    )(GameManager()),
)
check(
    "Pattern result adds time-based score",
    lambda: (
        lambda manager: (
            manager.start_game(Difficulty.EASY),
            manager.complete_pattern(pattern(elapsed=15.0, time_left=15, score=150)),
            assert_(
                manager.state.score_player_1 == 150
                and manager.state.stage_score_player_1 == 150
                and manager.state.stage_time_player_1 == 15.0
                and manager.state.pattern_progress_player_1 == 1
                and manager.state.current_pattern == 2
            ),
        )
    )(GameManager()),
)
check(
    "Timeout result adds zero score",
    lambda: (
        lambda manager: (
            manager.start_game(Difficulty.EASY),
            manager.complete_pattern(
                pattern(correct=False, elapsed=30.0, time_left=0, score=0, accuracy=0.4)
            ),
            assert_(
                manager.state.score_player_1 == 0
                and manager.state.stage_score_player_1 == 0
                and manager.state.stage_time_player_1 == 30.0
                and manager.state.current_pattern == 2
            ),
        )
    )(GameManager()),
)
check(
    "Player 1 completes stage patterns then Player 2 starts",
    lambda: (
        lambda manager: (
            manager.start_game(Difficulty.EASY),
            [manager.complete_pattern(pattern()) for _ in range(5)],
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
    "Stage winner uses completion time first",
    lambda: (
        lambda manager: (
            manager.start_game(Difficulty.EASY),
            [manager.complete_pattern(pattern(elapsed=10.0, time_left=20, score=200)) for _ in range(5)],
            [manager.complete_pattern(pattern(elapsed=11.0, time_left=19, score=190)) for _ in range(5)],
            assert_(
                manager.state.stage_wins_player_1 == 1
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
            manager.start_game(Difficulty.EASY),
            [manager.complete_pattern(pattern()) for _ in range(5)],
            [manager.complete_pattern(pattern(elapsed=11.0, time_left=19, score=190)) for _ in range(5)],
            manager.next_stage(),
            assert_(
                manager.state.current_stage == 2
                and manager.state.current_pattern == 1
                and manager.state.stage_score_player_1 == 0
                and manager.state.stage_score_player_2 == 0
                and manager.state.stage_time_player_1 == 0.0
                and manager.state.stage_time_player_2 == 0.0
                and manager.state.stage_wins_player_1 == 1
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

from vision.pipeline import (
    VisionPipeline,
    VisionResult,
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
# ui.screens.lobby_screen
# ─────────────────────────────────────────────────────────────────────────────

print("\n── ui.screens.lobby_screen ──────────────")

from ui.screens.lobby_screen import LobbyScreen


def test_lobby_screen():
    started = []

    widget = LobbyScreen(on_start=lambda: started.append(True))

    # Initial state
    assert widget.start_button.isEnabled()
    assert "Player 1" in widget._player_labels[1].text()
    assert "Menunggu" in widget._player_labels[1].text()
    assert "Player 2" in widget._player_labels[2].text()
    assert "Menunggu" in widget._player_labels[2].text()

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
    assert started == [True]

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
    assert not widget.is_running
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

    assert widget.is_running
    assert widget.remaining_seconds == 20
    assert widget.time_bar.maximum() == 20
    assert widget.time_bar.value() == 20
    assert "Stage 1" in widget.stage_label.text()
    assert "Pattern 2/5" in widget.stage_label.text()
    assert widget.pattern_count_label.text() == "2 / 15"

    # Update scores and progress
    widget.set_scores(120, 95)
    assert "120" in widget.player1_score_label.text()
    assert "95" in widget.player2_score_label.text()

    widget.set_progress(3, 4)
    assert widget.artwork_count_label.text() == "3 / 15"
    assert widget.pattern_count_label.text() == "4 / 15"

    # Receive detection result
    widget.receive_detection(
        correct=True,
        accuracy=98.5,
    )

    assert not widget.is_running
    assert "MATCHED" in widget.detection_label.text()
    assert completed == [
        {"correct": True, "time_left": 20}
    ]

    # Ignore duplicate detection
    widget.receive_detection(
        correct=False,
        accuracy=50.0,
    )
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
        lambda: widget.receive_detection("yes", 95.0)
    )
    assert _raises_value_error(
        lambda: widget.receive_detection(True, 101)
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