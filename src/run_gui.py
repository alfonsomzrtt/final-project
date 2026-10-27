
import os
from pathlib import Path

from ui.main_window import MainWindow
from PyQt5.QtCore import QLibraryInfo
from PyQt5.QtWidgets import QApplication

os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = (
    QLibraryInfo.location(QLibraryInfo.PluginsPath)
)



app = QApplication([])
# Calibrate these bounds in original camera-frame pixels before enabling.
VISION_GRID_BOUNDS = (42, 100, 636, 604)
VISION_RAW_FRAME_SNAPSHOT_DIR = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "logs"
    / "vision_snapshots"
)
window = MainWindow(
    vision_grid_bounds=VISION_GRID_BOUNDS,
    vision_raw_frame_snapshot_dir=VISION_RAW_FRAME_SNAPSHOT_DIR,
)
window.show()
app.exec_()
