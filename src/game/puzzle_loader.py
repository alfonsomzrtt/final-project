"""Puzzle loader.

This module manages puzzle selection from the pattern bank.

The loader is responsible for selecting patterns for a game session.
It does not handle GUI rendering, computer vision, or gameplay scoring.
"""

import json
import random
from pathlib import Path

from config.constants import (
    PATTERNS_PER_STAGE,
    TOTAL_STAGES,
)
from core.enums import Difficulty, GridSize


class PuzzleLoader:
    DATA_PATH = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "pattern_bank.json"
    )

    def __init__(self):
        self.pattern_bank = self._load_pattern_bank()
        self.selected_patterns = []
        self._selected_grid_size = GridSize.TWO_BY_TWO

    @property
    def supported_grid_sizes(self):
        """Return the grid sizes that are available in the pattern bank."""
        return tuple(sorted(self.pattern_bank.keys(), key=int))

    def _load_pattern_bank(self):
        """Load and validate the pattern bank data file."""
        if not self.DATA_PATH.exists():
            raise FileNotFoundError(
                f"Pattern bank data file not found: {self.DATA_PATH}"
            )

        with self.DATA_PATH.open("r", encoding="utf-8") as handle:
            raw_bank = json.load(handle)

        if not isinstance(raw_bank, dict):
            raise TypeError("pattern_bank.json harus berupa object JSON")

        bank = {}
        for grid_key, difficulty_map in raw_bank.items():
            grid_size = self._parse_grid_size(grid_key)

            if not isinstance(difficulty_map, dict):
                raise TypeError(
                    f"Bank untuk grid size {grid_key} harus berupa object"
                )

            bank[grid_size] = {}
            for difficulty_key, patterns in difficulty_map.items():
                difficulty = self._parse_difficulty(difficulty_key)

                if not isinstance(patterns, dict):
                    raise TypeError(
                        f"Bank untuk difficulty {difficulty_key} harus "
                        "berupa object"
                    )

                bank[grid_size][difficulty] = {}
                for pattern_id, matrix in patterns.items():
                    bank[grid_size][difficulty][pattern_id] = (
                        self._validate_matrix(matrix, grid_size)
                    )

        return bank

    @staticmethod
    def _parse_grid_size(grid_key):
        if grid_key == "2x2":
            return GridSize.TWO_BY_TWO
        if grid_key == "3x3":
            return GridSize.THREE_BY_THREE
        raise ValueError(f"Unsupported grid size key: {grid_key}")

    @staticmethod
    def _parse_difficulty(difficulty_key):
        difficulty_map = {
            "easy": Difficulty.EASY,
            "normal": Difficulty.NORMAL,
            "hard": Difficulty.HARD,
        }

        if difficulty_key not in difficulty_map:
            raise ValueError(
                f"Unsupported difficulty key: {difficulty_key}"
            )
        return difficulty_map[difficulty_key]

    @staticmethod
    def _validate_matrix(matrix, grid_size):
        if not isinstance(matrix, (list, tuple)):
            raise TypeError("Pattern matrix harus berupa list atau tuple")

        if len(matrix) != int(grid_size):
            raise ValueError(
                f"Pattern matrix untuk {grid_size} harus berukuran "
                f"{int(grid_size)}x{int(grid_size)}"
            )

        validated = []
        for row in matrix:
            if not isinstance(row, (list, tuple)) or len(row) != int(grid_size):
                raise ValueError("Pattern matrix harus berbentuk persegi")

            validated_row = []
            for cell in row:
                if not isinstance(cell, int) or not 0 <= cell <= 5:
                    raise ValueError(
                        f"Block class tidak valid pada pattern bank: {cell}"
                    )
                validated_row.append(cell)

            validated.append(validated_row)

        return validated

    def _normalize_grid_size(self, grid_size):
        if isinstance(grid_size, GridSize):
            return grid_size
        return GridSize(grid_size)

    def load_game_patterns(
        self,
        grid_size: GridSize,
        difficulty: Difficulty,
    ):
        """
        Select patterns for a new game session.

        A game session contains 15 unique patterns:
        3 stages × 5 patterns.
        """

        if not isinstance(difficulty, Difficulty):
            raise TypeError("difficulty harus berupa Difficulty")

        grid_size = self._normalize_grid_size(grid_size)

        if grid_size not in self.pattern_bank:
            raise NotImplementedError(
                f"Pattern bank untuk grid size {grid_size.value}x"
                f"{grid_size.value} belum tersedia."
            )

        available_patterns = list(self.pattern_bank[grid_size][difficulty])
        total_patterns = TOTAL_STAGES * PATTERNS_PER_STAGE

        self.selected_patterns = random.sample(
            available_patterns,
            total_patterns,
        )
        self._selected_grid_size = grid_size

        return self.selected_patterns

    def get_pattern(self, stage: int, pattern: int):
        """
        Get a pattern identifier based on stage and pattern number.
        """

        if not self.selected_patterns:
            raise RuntimeError("Game patterns have not been loaded.")

        index = (
            (stage - 1) * PATTERNS_PER_STAGE
            + (pattern - 1)
        )

        if index >= len(self.selected_patterns):
            raise IndexError(
                f"Invalid stage/pattern: {stage}/{pattern}"
            )

        return self.selected_patterns[index]

    def get_pattern_matrix(self, pattern_id: str, grid_size=None):
        """Resolve a pattern identifier to its matrix."""
        if not isinstance(pattern_id, str) or not pattern_id:
            raise TypeError("pattern_id harus berupa string non-kosong")

        search_grid_sizes = []
        if grid_size is None:
            search_grid_sizes.append(self._selected_grid_size)
            search_grid_sizes.extend(
                size
                for size in self.supported_grid_sizes
                if size != self._selected_grid_size
            )
        else:
            grid_size = self._normalize_grid_size(grid_size)
            if grid_size not in self.pattern_bank:
                raise NotImplementedError(
                    f"Pattern bank untuk grid size {grid_size.value}x"
                    f"{grid_size.value} belum tersedia."
                )
            search_grid_sizes.append(grid_size)

        for current_grid_size in search_grid_sizes:
            for patterns in self.pattern_bank[current_grid_size].values():
                if pattern_id in patterns:
                    return [
                        list(row)
                        for row in patterns[pattern_id]
                    ]

        raise KeyError(f"Pattern tidak ditemukan: {pattern_id}")

    def reset(self):
        """Clear the currently selected patterns."""

        self.selected_patterns = []
        self._selected_grid_size = GridSize.TWO_BY_TWO
