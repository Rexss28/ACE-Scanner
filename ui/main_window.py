from PySide6.QtCore import Qt, QPointF
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget, 
    QVBoxLayout, 
    QHBoxLayout, 
    QLineEdit,
    QLabel, 
    QListWidget, 
    QListWidgetItem, 
    QApplication, 
    QWidget,
)
from PySide6.QtGui import ( 
    QColor, 
    QPalette, 
    QPainter, 
    QRadialGradient, 
    QBrush, 
    )

from core.data_access import DataAccess


# # --- Style Constants ---
# STYLE_CONSTANTS = {
#     "background_color": "#1E1E1E",
#     "form_container_color": "#1F2937",
#     "input_field_color": "#374151",
#     "input_border_color": "#4B5563",
#     "input_error_color": "#BA0000",  # Red for errors
#     "success_color": "#008C2C",      # Green for success
#     "error_bg_color": "rgba(239, 68, 68, 0.1)",
#     "success_bg_color": "rgba(16, 185, 129, 0.1)",
#     "primary_button_color": "#6366F1",
#     "primary_button_hover_color": "#4F46E5",
#     "secondary_button_color": "#374151",
#     "secondary_button_hover_color": "#4B5563",
#     "text_color": "#E5E7EB",
#     "text_secondary_color": "#9CA3AF",
#     "link_color": "#6366F1",
#     "separator_color": "#6B7280",
#     "font_family": "Inter, sans-serif",
# }

class GradientBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

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

        gradient.setColorAt(0.0, QColor("#4F46E5"))
        gradient.setColorAt(0.35, QColor("#312E81"))
        gradient.setColorAt(0.75, QColor("#1E1B4B"))
        gradient.setColorAt(1.0, QColor("#111827"))

        painter.fillRect(
            self.rect(),
            QBrush(gradient)
        )

        painter.end()

class MainWindow(QMainWindow):
    def __init__(self, db: DataAccess):
        super().__init__()
        self.db = db

        self.setWindowTitle("ACE Christmas Party 2026 | Attendance Scanner")
        self.resize(700, 900)

        # Central widget
        central = GradientBackground()
        self.setCentralWidget(central)

        main_container = QVBoxLayout(central)
        header_container = QHBoxLayout()
        main_container.addLayout(header_container)

        # Title
        title = QLabel("Welcome to the 2026 ACE Christmas Party!")
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        header_container.addWidget(title)
        