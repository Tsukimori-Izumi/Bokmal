"""Bokmål - Project Management Application

Entry point for the application.
Python 3.13 + PySide6
"""

import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ui.main_window import MainWindow
from ui.theme import get_theme_stylesheet
from config import APP_TITLE


def main():
    """Initialize and run the application."""
    # High DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)
    app.setOrganizationName("Bokmål")
    app.setOrganizationDomain("bokmal.local")

    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Apply dark theme
    app.setStyleSheet(get_theme_stylesheet())

    # Create and show main window
    window = MainWindow()
    window.showMaximized()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
