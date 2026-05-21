"""
Bookmarks Bar component for Nova Browser.
Sits horizontally under the address bar, offering quick double-click navigation.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QMenu
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QUrl
from PyQt6.QtGui import QIcon, QPixmap

from src.ui.icons import ICON_GLOBE, ICON_BOOKMARK, icon_to_pixmap, icon_to_qicon
from src.ui.theme import BACKGROUND_SECONDARY, BACKGROUND_ELEVATED, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_TERTIARY

class BookmarkBarItem(QPushButton):
    """Sleek interactive button representing a single bookmark link."""
    
    def __init__(self, title: str, url: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.url = url
        
        self.setFixedHeight(24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Elide title
        display_title = title if len(title) <= 15 else title[:12] + "..."
        self.setText(f"  {display_title}")
        
        # Default icon
        self.setIcon(icon_to_qicon(ICON_GLOBE, 12))
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 0 8px;
                color: {TEXT_SECONDARY};
                font-size: 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {BACKGROUND_ELEVATED};
                color: {TEXT_PRIMARY};
            }}
            QPushButton:pressed {{
                transform: scale(0.96);
            }}
        """)

class NovaBookmarksBar(QWidget):
    """Horizontal bookmarks manager bar with overflow handling."""
    
    bookmark_clicked = pyqtSignal(str)
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setFixedHeight(32)
        self.setStyleSheet(f"background-color: {BACKGROUND_SECONDARY}; border-bottom: 1px solid rgba(255,255,255,0.06);")
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(12, 0, 12, 0)
        self.layout.setSpacing(8)
        
        self.refresh()
        
    def refresh(self):
        """Rebuild the bar dynamically from the global bookmarks list."""
        # Clean current layout items
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        bookmarks = []
        try:
            bookmarks = self.main_window.bookmarks_manager.get_bookmarks()
        except Exception:
            pass
            
        if not bookmarks:
            empty_lbl = QLabel("Add bookmarks here for quick access ✦")
            empty_lbl.setStyleSheet(f"color: {TEXT_TERTIARY}; font-size: 11px; font-style: italic;")
            self.layout.addWidget(empty_lbl)
            self.layout.addStretch()
            return
            
        # Add up to 8 items, overflow to menu
        max_visible = 8
        for bm in bookmarks[:max_visible]:
            btn = BookmarkBarItem(bm.title, bm.url)
            btn.clicked.connect(lambda _, u=bm.url: self.bookmark_clicked.emit(u))
            self.layout.addWidget(btn)
            
        if len(bookmarks) > max_visible:
            # Add overflow button (»)
            overflow_btn = QPushButton("»")
            overflow_btn.setFixedSize(24, 24)
            overflow_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            overflow_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    border-radius: 6px;
                    color: {TEXT_SECONDARY};
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {BACKGROUND_ELEVATED};
                    color: {TEXT_PRIMARY};
                }}
            """)
            
            # Setup popup menu
            menu = QMenu(self)
            menu.setStyleSheet("QMenu { background: #1A1D2E; border: 1px solid rgba(255,255,255,0.06); }")
            for bm in bookmarks[max_visible:]:
                act = menu.addAction(bm.title)
                act.triggered.connect(lambda _, u=bm.url: self.bookmark_clicked.emit(u))
            overflow_btn.clicked.connect(lambda: menu.exec(overflow_btn.mapToGlobal(overflow_btn.rect().bottomLeft())))
            self.layout.addWidget(overflow_btn)
            
        self.layout.addStretch()
