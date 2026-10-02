from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtSvgWidgets import QSvgWidget
from core.data_access import DataAccess

from ui.common.py_button import PyButton

class GradientBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

# background ni
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        # Place the brightest point near the upper center
        center = QPointF(width * 0.5, height * 0.2)

        # Large enough to cover the entire widget
        radius = max(width, height) * 0.9

        gradient = QRadialGradient(center, radius)

        gradient.setColorAt(0.0, QColor("#E5E5D4"))
        gradient.setColorAt(0.35, QColor("#E5E5D4"))
        gradient.setColorAt(0.75, QColor("#B8AB89"))
        gradient.setColorAt(1.0, QColor("#646448"))

        painter.fillRect(
            self.rect(),
            QBrush(gradient)
        )

        painter.end()


class MainWindow(QMainWindow):
    # button to scanner window
    def scanner(self):
        self.recent_scan = "Test click!"

    def __init__(self, db: DataAccess):
        super().__init__()
        self.db = db

        self.setWindowTitle("ACE Christmas Party 2026 | Attendance Scanner")
        self.resize(500, 500)

        # Central widget
        central = GradientBackground()
        self.setCentralWidget(central)

        main_container = QVBoxLayout(central)
        main_container.setSpacing(10)

        # Title
        title = QLabel("Welcome!")
        title.setStyleSheet("font-size: 100px; color: black")

        scan_row = QHBoxLayout()
        scan_row.setSpacing(20)
        scan_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # scan button
        self.scan_button = PyButton(
            label="Start Scanning",
        )
        self.scan_button.clicked.connect(self.scanner)
        
        main_container.addWidget(
            title,
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        main_container.addWidget(
            self.scan_button,
            alignment=Qt.AlignmentFlag.AlignCenter
        )