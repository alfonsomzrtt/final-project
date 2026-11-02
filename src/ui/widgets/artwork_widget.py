"""Mystery Artwork widget with deterministic spatial reveals."""

from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QPixmap
from PyQt5.QtWidgets import QWidget


class ArtworkWidget(QWidget):
    """Reveal a 5x3 partition of an artwork as puzzle milestones are reached."""

    COLUMNS = 5
    ROWS = 3
    REGION_COUNT = COLUMNS * ROWS

    # Spatially distributed order; region IDs remain row-major (0..14).
    REVEAL_ORDER = (7, 1, 13, 4, 10, 2, 14, 6, 0, 11, 3, 8, 12, 5, 9)

    def __init__(self, image_path=None, parent=None):
        super().__init__(parent)
        self.setMinimumSize(180, 120)
        self._revealed = set()
        if image_path is None:
            image_path = (
                Path(__file__).resolve().parents[2]
                / "assets" / "images" / "Vincent_van_Gogh_Starry_Night.jpg"
            )
        self._pixmap = QPixmap(str(image_path))
        if self._pixmap.isNull():
            raise FileNotFoundError(f"Artwork tidak dapat dimuat: {image_path}")

    @property
    def revealed_count(self):
        return len(self._revealed)

    def reset(self):
        self._revealed.clear()
        self.update()

    def reveal_next(self):
        if self.revealed_count >= self.REGION_COUNT:
            return None
        region_id = self.REVEAL_ORDER[self.revealed_count]
        self._revealed.add(region_id)
        self.update()
        return region_id

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        target = self.rect().adjusted(2, 2, -2, -2)
        scaled = self._pixmap.scaled(
            target.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        x = target.x() + (target.width() - scaled.width()) // 2
        y = target.y() + (target.height() - scaled.height()) // 2
        from PyQt5.QtCore import QRect
        destination = QRect(x, y, scaled.width(), scaled.height())
        painter.fillRect(target, QColor("#111820"))
        painter.drawPixmap(destination, scaled)

        cell_w = destination.width() / self.COLUMNS
        cell_h = destination.height() / self.ROWS
        for region_id in range(self.REGION_COUNT):
            if region_id in self._revealed:
                continue
            row, col = divmod(region_id, self.COLUMNS)
            left = round(destination.x() + col * cell_w)
            top = round(destination.y() + row * cell_h)
            right = round(destination.x() + (col + 1) * cell_w)
            bottom = round(destination.y() + (row + 1) * cell_h)
            painter.fillRect(
                left, top, right - left, bottom - top,
                QColor(8, 14, 22, 238),
            )
        painter.setPen(QColor("#526170"))
        painter.drawRect(destination.adjusted(0, 0, -1, -1))
        painter.end()
