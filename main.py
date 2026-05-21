"""
This project follows the Incremental Process Model. Each increment added a working 
feature set: navigation -> tabs -> bookmarks -> history -> downloads -> testing -> refactoring.
This allowed solo development with continuous testing at each stage.
"""

import sys
from PyQt6.QtWidgets import QApplication

from src.ui.browser_window import BrowserWindow
from src.utils.exception_logger import log_exception
from src.ui.splash_screen import SplashScreen
from PyQt6.QtCore import Qt

# Keep a global reference so the window doesn't get garbage collected
_main_window = None

def main():
    """Entry point for the application."""
    global _main_window
    try:
        # Enable Hardware Acceleration and High DPI
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
        
        app = QApplication(sys.argv)
        app.setApplicationName("Python Web Browser")
        app.setOrganizationName("Student Project")
        
        splash = SplashScreen()
        
        def on_splash_finished():
            global _main_window
            _main_window = BrowserWindow()
            _main_window.show()
            
        splash.finished.connect(on_splash_finished)
        splash.show()
        splash.start_animation()
        
        sys.exit(app.exec())
    except Exception as e:
        log_exception(e)
        print("Fatal error. Check data/logs/error.log")

if __name__ == "__main__":
    main()
