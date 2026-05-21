"""
Custom Find In Page Bar component for Nova Browser.
Triggered by Ctrl+F. Sits above status bar, offering dynamic highlighted text search.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QIcon, QKeySequence

from src.ui.icons import ICON_SEARCH, ICON_CLOSE, icon_to_qicon, icon_to_pixmap
from src.ui.theme import BACKGROUND_TERTIARY, BACKGROUND_ELEVATED, ACCENT_DANGER, ACCENT_PRIMARY, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_TERTIARY
from src.ui.animations import slide_in_from_bottom

class NovaFindBar(QWidget):
    """Clean sliding widget for Ctrl+F in-page highlighting and matches iteration."""
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setFixedHeight(42)
        self.setStyleSheet(f"background-color: {BACKGROUND_TERTIARY}; border-top: 1px solid rgba(255,255,255,0.08);")
        
        self.is_case_sensitive = False
        self.is_regex = False
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(10)
        
        # Search Pill Container
        self.pill = QFrame()
        self.pill.setStyleSheet(f"background-color: {BACKGROUND_ELEVATED}; border: 1px solid rgba(255,255,255,0.06); border-radius: 16px;")
        self.pill.setFixedSize(280, 28)
        pill_layout = QHBoxLayout(self.pill)
        pill_layout.setContentsMargins(8, 0, 8, 0)
        pill_layout.setSpacing(6)
        
        # Search Magnifier Label
        self.search_icon = QLabel()
        self.search_icon.setPixmap(icon_to_pixmap(ICON_SEARCH, 12, "#8B8FA8"))
        self.search_icon.setFixedSize(12, 12)
        pill_layout.addWidget(self.search_icon)
        
        # Input Field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Find in page...")
        self.input_field.setStyleSheet("background: transparent; border: none; font-size: 13px; color: #FFFFFF;")
        self.input_field.textChanged.connect(self._on_text_changed)
        self.input_field.returnPressed.connect(self.navigate_next)
        pill_layout.addWidget(self.input_field)
        
        # Results counter
        self.counter_lbl = QLabel("0/0")
        self.counter_lbl.setStyleSheet(f"color: {TEXT_TERTIARY}; font-size: 11px;")
        pill_layout.addWidget(self.counter_lbl)
        
        layout.addWidget(self.pill)
        
        # Next / Prev controls
        self.prev_btn = QPushButton("↑")
        self.prev_btn.setFixedSize(28, 28)
        self.prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_btn.setStyleSheet(f"QPushButton {{ background: transparent; border: none; border-radius: 6px; color: {TEXT_SECONDARY}; font-weight: bold; font-size: 14px; }} QPushButton:hover {{ background-color: {BACKGROUND_ELEVATED}; color: #FFFFFF; }}")
        self.prev_btn.clicked.connect(self.navigate_prev)
        layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton("↓")
        self.next_btn.setFixedSize(28, 28)
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.setStyleSheet(f"QPushButton {{ background: transparent; border: none; border-radius: 6px; color: {TEXT_SECONDARY}; font-weight: bold; font-size: 14px; }} QPushButton:hover {{ background-color: {BACKGROUND_ELEVATED}; color: #FFFFFF; }}")
        self.next_btn.clicked.connect(self.navigate_next)
        layout.addWidget(self.next_btn)
        
        # Filter Buttons (Aa & Regex)
        self.case_btn = QPushButton("Aa")
        self.case_btn.setCheckable(True)
        self.case_btn.setFixedSize(28, 28)
        self.case_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.case_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 6px;
                color: {TEXT_SECONDARY};
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {BACKGROUND_ELEVATED};
            }}
            QPushButton:checked {{
                background-color: {ACCENT_PRIMARY};
                color: #FFFFFF;
            }}
        """)
        self.case_btn.clicked.connect(self._toggle_case)
        layout.addWidget(self.case_btn)
        
        layout.addStretch()
        
        # Close Button
        self.close_btn = QPushButton()
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setIcon(icon_to_qicon(ICON_CLOSE, 14))
        self.close_btn.setStyleSheet(f"QPushButton {{ background: transparent; border: none; border-radius: 6px; }} QPushButton:hover {{ background-color: {ACCENT_DANGER}; }}")
        self.close_btn.clicked.connect(self.hide_bar)
        layout.addWidget(self.close_btn)
        
        self.hide()
        
    def show_bar(self):
        """Display finding tray with smooth slide animations and focus input."""
        self.show()
        slide_in_from_bottom(self, 15, 120)
        self.input_field.setFocus()
        self.input_field.selectAll()
        
    def hide_bar(self):
        """Dismiss search and clear page highlight tags."""
        browser = self.main_window.tabs.current_browser()
        if browser:
            # Passing empty string clears highlights
            browser.findText("")
        self.hide()
        
    def _on_text_changed(self, text: str):
        self._find_on_page(text)
        
    def _toggle_case(self):
        self.is_case_sensitive = self.case_btn.isChecked()
        self._find_on_page(self.input_field.text())
        
    def _find_on_page(self, text: str, forward: bool = True):
        browser = self.main_window.tabs.current_browser()
        if not browser:
            return
            
        from PyQt6.QtWebEngineCore import QWebEnginePage
        flags = QWebEnginePage.FindFlag(0)
        
        if not forward:
            flags |= QWebEnginePage.FindFlag.FindBackward
        if self.is_case_sensitive:
            flags |= QWebEnginePage.FindFlag.FindCaseSensitively
            
        # Execute search and fetch total match sizes
        def _on_find_done(result):
            # result is a QWebEngineFindTextResult (on newer QtWebEngine versions)
            # or a boolean depending on standard API
            try:
                # We can show indicator
                if text:
                    self.counter_lbl.setText(f"{result.activeMatchIndex()}/{result.numberOfMatches()}")
                else:
                    self.counter_lbl.setText("0/0")
            except Exception:
                # Fallback if result doesn't have details
                pass
                
        browser.page().findText(text, flags, _on_find_done)
        
    def navigate_next(self):
        self._find_on_page(self.input_field.text(), forward=True)
        
    def navigate_prev(self):
        self._find_on_page(self.input_field.text(), forward=False)
