
from PyQt5.QtCore import QPoint, QRect, Qt
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QPainter,
    QPen,
    QPolygon,
)
from PyQt5.QtWidgets import QWidget

from config.constants import (
    BLOCK_CLASS_RED,
    BLOCK_CLASS_WHITE,
    BLOCK_CLASS_RED_TOP_LEFT,
    BLOCK_CLASS_RED_TOP_RIGHT,
    BLOCK_CLASS_RED_BOTTOM_LEFT,
    BLOCK_CLASS_RED_BOTTOM_RIGHT,
    SUPPORTED_GRID_SIZES,
)


class PatternGrid(QWidget):
    """
    Widget untuk merender pola Block Design 2x2 dan 3x3.

    Setiap sel menggunakan salah satu dari enam kelas blok:
        0: Merah penuh
        1: Putih penuh
        2: Merah segitiga kiri atas
        3: Merah segitiga kanan atas
        4: Merah segitiga kiri bawah
        5: Merah segitiga kanan bawah
    """

    RED = QColor("#C0392B")
    WHITE = QColor("#F0F0F0")
    BORDER = QColor("#444444")

    DEFAULT_GRID = [
        [BLOCK_CLASS_RED, BLOCK_CLASS_WHITE],
        [BLOCK_CLASS_WHITE, BLOCK_CLASS_RED],
    ]

    def __init__(self, grid=None, cell_size=72, parent=None):
        super().__init__(parent)

        if not isinstance(cell_size, int) or cell_size < 10:
            raise ValueError("cell_size harus berupa integer >= 10.")

        self.cell_size = cell_size
        self.grid = self._validate_grid(
            grid if grid is not None else self.DEFAULT_GRID
        )

        self._update_size()

    @staticmethod
    def _validate_grid(grid):
        """Validasi dimensi dan kelas setiap sel."""
        if not isinstance(grid, (list, tuple)):
            raise TypeError("Grid harus berupa list atau tuple.")

        if len(grid) not in SUPPORTED_GRID_SIZES:
            raise ValueError("Grid hanya mendukung ukuran 2x2 atau 3x3.")

        size = len(grid)

        if any(
            not isinstance(row, (list, tuple)) or len(row) != size
            for row in grid
        ):
            raise ValueError("Grid harus berbentuk matriks persegi.")

        valid_classes = {
            BLOCK_CLASS_RED,
            BLOCK_CLASS_WHITE,
            BLOCK_CLASS_RED_TOP_LEFT,
            BLOCK_CLASS_RED_TOP_RIGHT,
            BLOCK_CLASS_RED_BOTTOM_LEFT,
            BLOCK_CLASS_RED_BOTTOM_RIGHT,
        }

        for row in grid:
            for cell in row:
                if cell not in valid_classes:
                    raise ValueError(
                        f"Kelas blok tidak valid: {cell}"
                    )

        return [list(row) for row in grid]

    def set_grid(self, grid):
        """Memperbarui pola yang ditampilkan."""
        self.grid = self._validate_grid(grid)
        self._update_size()
        self.update()

    def set_cell_size(self, cell_size):
        """Mengubah ukuran setiap sel."""
        if not isinstance(cell_size, int) or cell_size < 10:
            raise ValueError("cell_size harus berupa integer >= 10.")

        if cell_size == self.cell_size:
            return

        self.cell_size = cell_size
        self._update_size()
        self.update()

    def _update_size(self):
        size = len(self.grid)
        total_size = size * self.cell_size + 4

        self.setFixedSize(total_size, total_size)

    def _draw_cell(self, painter, x, y, cell_class):
        """Menggambar satu sel berdasarkan kelas blok."""
        size = self.cell_size
        rect = QRect(x, y, size - 2, size - 2)

        painter.setPen(Qt.NoPen)

        if cell_class == BLOCK_CLASS_RED:
            painter.fillRect(rect, self.RED)

        elif cell_class == BLOCK_CLASS_WHITE:
            painter.fillRect(rect, self.WHITE)

        else:
            painter.fillRect(rect, self.WHITE)

            w = rect.width()
            h = rect.height()

            triangles = {
                BLOCK_CLASS_RED_TOP_LEFT: [
                    QPoint(x, y),
                    QPoint(x + w, y),
                    QPoint(x, y + h),
                ],
                BLOCK_CLASS_RED_TOP_RIGHT: [
                    QPoint(x + w, y),
                    QPoint(x + w, y + h),
                    QPoint(x, y),
                ],
                BLOCK_CLASS_RED_BOTTOM_LEFT: [
                    QPoint(x, y),
                    QPoint(x, y + h),
                    QPoint(x + w, y + h),
                ],
                BLOCK_CLASS_RED_BOTTOM_RIGHT: [
                    QPoint(x + w, y),
                    QPoint(x, y + h),
                    QPoint(x + w, y + h),
                ],
            }

            painter.setBrush(QBrush(self.RED))
            painter.drawPolygon(QPolygon(triangles[cell_class]))

        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(self.BORDER, 1))
        painter.drawRect(rect)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for row_index, row in enumerate(self.grid):
            for col_index, cell_class in enumerate(row):
                x = col_index * self.cell_size + 2
                y = row_index * self.cell_size + 2

                self._draw_cell(
                    painter,
                    x,
                    y,
                    cell_class,
                )

        painter.end()