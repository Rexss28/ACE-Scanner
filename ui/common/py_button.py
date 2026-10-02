from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *

class PyButton(QPushButton):
    def __init__(
            self,
            width = 150,
            bg_color = "#0b0c0d",
            text_color = "white",
            label = ""
    ):
        QPushButton.__init__(self)
        self.setText(label)
        self.setFixedSize(width, 40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Apply styles
        self._bg_color = bg_color
        self._text_color = text_color
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {self._bg_color};
                color: {self._text_color};
                border: none;
                border-radius: 15px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: #1e1e1e;
            }}
            """
        )
        