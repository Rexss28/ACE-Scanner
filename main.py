import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import (
    QIcon,
    QFont,
)
from PySide6.QtCore import Qt

from core.data_access import DataAccess
from ui.main_window import MainWindow


def main():
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "RoundPreferFloor"
    
    app = QApplication(sys.argv)

    if os.path.exists("ui/assets/icons/ACE-LOGO.png"):
        app.setWindowIcon(QIcon("ui/assets/icons/ACE-LOGO.png"))

    global_font = QFont("Poppins", 12, QFont.Weight.Bold)
    QApplication.setFont(global_font)

    db = DataAccess()
    window = MainWindow(db)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()