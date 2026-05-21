"""
Smart Address Bar for Nova Browser.
Simplifies URLs to show bold domain + muted path when unfocused,
reveals full URL on focus, and handles inline lock/bookmark icons.
Includes a modern dropdown suggestions menu overlay.
"""

from PyQt6.QtWidgets import QLineEdit, QWidget, QLabel, QPushButton, QFrame, QVBoxLayout, QListWidget, QListWidgetItem, QHBoxLayout
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap, QFocusEvent, QResizeEvent, QMouseEvent, QColor
from urllib.parse import urlparse
import sys

from src.ui.icons import ICON_LOCK, ICON_GLOBE, ICON_STAR_OUTLINE, ICON_STAR_FILLED, ICON_CLOSE, ICON_SHARE, icon_to_pixmap, icon_to_qicon
from src.ui.theme import BACKGROUND_TERTIARY, BACKGROUND_ELEVATED, ACCENT_PRIMARY, ACCENT_SUCCESS, ACCENT_WARNING, TEXT_PRIMARY, TEXT_SECONDARY

class AddressDropdown(QFrame):
    """Floating dropdown menu positioned below the address bar to show suggestions."""
    
    suggestion_selected = pyqtSignal(str)
    
    def __init__(self, parent_window):
        super().__init__(parent_window, Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setObjectName("AddressDropdown")
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setStyleSheet(f"""
            QFrame#AddressDropdown {{
                background-color: {BACKGROUND_TERTIARY};
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
            }}
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: none;
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 8px 12px;
                border-radius: 8px;
                color: {TEXT_PRIMARY};
            }}
            QListWidget::item:hover {{
                background-color: {BACKGROUND_ELEVATED};
                color: #ffffff;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget)
        
    def populate(self, text: str, bookmarks_mgr, history_mgr):
        """Fill items based on currently typed text."""
        self.list_widget.clear()
        if not text:
            self.hide()
            return
            
        # 1. Search Google Suggestion
        search_item = QListWidgetItem(f"🔍 Search Google for '{text}'")
        search_item.setData(Qt.ItemDataRole.UserRole, f"https://www.google.com/search?q={text}")
        self.list_widget.addItem(search_item)
        
        # 2. Bookmarks Match
        try:
            for bm in bookmarks_mgr.get_bookmarks():
                if text.lower() in bm.title.lower() or text.lower() in bm.url.lower():
                    bm_item = QListWidgetItem(f"⭐ Bookmark: {bm.title} - {bm.url}")
                    bm_item.setData(Qt.ItemDataRole.UserRole, bm.url)
                    self.list_widget.addItem(bm_item)
        except Exception:
            pass
            
        # 3. History Match
        try:
            for entry in history_mgr.get_history():
                if text.lower() in entry['title'].lower() or text.lower() in entry['url'].lower():
                    hist_item = QListWidgetItem(f"📜 History: {entry['title']} - {entry['url']}")
                    hist_item.setData(Qt.ItemDataRole.UserRole, entry['url'])
                    self.list_widget.addItem(hist_item)
        except Exception:
            pass
            
        # Show or hide
        if self.list_widget.count() > 0:
            self.show()
        else:
            self.hide()
            
    def _on_item_clicked(self, item):
        url = item.data(Qt.ItemDataRole.UserRole)
        if url:
            self.suggestion_selected.emit(url)
        self.hide()

class NovaAddressBar(QLineEdit):
    """Custom QLineEdit displaying dynamic icons and elided domain rendering."""
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.real_url_text = ""
        self.is_focused = False
        
        # Add internal icons spacing
        self.setTextMargins(28, 0, 68, 0)
        self.setFixedHeight(36)
        
        # Initialize internal icons
        self.left_icon_label = QLabel(self)
        self.left_icon_label.setScaledContents(True)
        self.left_icon_label.setPixmap(icon_to_pixmap(ICON_GLOBE, 16, "#8B8FA8"))
        
        self.clear_button = QPushButton(self)
        self.clear_button.setIcon(icon_to_qicon(ICON_CLOSE, 12, "#8B8FA8"))
        self.clear_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_button.setStyleSheet("background: transparent; border: none;")
        self.clear_button.hide()
        self.clear_button.clicked.connect(self.clear)
        
        self.star_button = QPushButton(self)
        self.star_button.setIcon(icon_to_qicon(ICON_STAR_OUTLINE, 14, "#8B8FA8", "#FFB830"))
        self.star_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.star_button.setStyleSheet("background: transparent; border: none;")
        self.star_button.clicked.connect(self.main_window.add_bookmark)
        
        self.share_button = QPushButton(self)
        self.share_button.setIcon(icon_to_qicon(ICON_SHARE, 14, "#8B8FA8"))
        self.share_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.share_button.setStyleSheet("background: transparent; border: none;")
        self.share_button.clicked.connect(self._share_current_url)
        
        # Dropdown popup
        self.dropdown = AddressDropdown(self.window())
        self.dropdown.suggestion_selected.connect(self._on_suggestion_selected)
        
        # Connect text changed for suggestions
        self.textChanged.connect(self._on_text_changed)
        
    def set_address(self, url_str: str):
        """Set URL from application code without losing selection if focused."""
        self.real_url_text = url_str
        if not self.is_focused:
            self._display_simplified_address()
        else:
            self.setText(url_str)
            
        self._update_security_icon()
        
    def _display_simplified_address(self):
        """Format elided bold domain and muted path when unfocused."""
        url_str = self.real_url_text
        if not url_str or url_str.startswith("chrome:") or url_str.startswith("about:"):
            self.setText(url_str)
            return
            
        try:
            parsed = urlparse(url_str)
            domain = parsed.netloc
            path = parsed.path + (f"?{parsed.query}" if parsed.query else "")
            
            if domain:
                self.setText(f"{domain}{path}")
            else:
                self.setText(url_str)
        except Exception:
            self.setText(url_str)
            
    def _update_security_icon(self):
        """Change lock color/icon dynamically."""
        url_str = self.real_url_text.lower()
        if url_str.startswith("https:"):
            self.left_icon_label.setPixmap(icon_to_pixmap(ICON_LOCK, 16, ACCENT_SUCCESS))
        elif url_str.startswith("http:"):
            self.left_icon_label.setPixmap(icon_to_pixmap(ICON_LOCK, 16, ACCENT_WARNING))
        else:
            self.left_icon_label.setPixmap(icon_to_pixmap(ICON_GLOBE, 16, "#8B8FA8"))
            
    def focusInEvent(self, event: QFocusEvent):
        self.is_focused = True
        self.setText(self.real_url_text)
        self.clear_button.show()
        # Select all text on click
        self.selectAll()
        
        # Reposition dropdown and show if populated
        self._reposition_dropdown()
        
        super().focusInEvent(event)
        
    def focusOutEvent(self, event: QFocusEvent):
        self.is_focused = False
        self.clear_button.hide()
        # Wait a tiny fraction to allow dropdown click to register
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(150, self.dropdown.hide)
        self._display_simplified_address()
        super().focusOutEvent(event)
        
    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        # Position left icon
        self.left_icon_label.setGeometry(8, (self.height() - 16) // 2, 16, 16)
        
        # Position right buttons
        r_width = self.width()
        self.share_button.setGeometry(r_width - 24, (self.height() - 16) // 2, 16, 16)
        self.star_button.setGeometry(r_width - 44, (self.height() - 16) // 2, 16, 16)
        self.clear_button.setGeometry(r_width - 64, (self.height() - 16) // 2, 16, 16)
        
        self._reposition_dropdown()
        
    def _reposition_dropdown(self):
        """Anchor suggestions dropdown perfectly beneath the address bar."""
        if hasattr(self, 'dropdown') and self.dropdown:
            global_pos = self.mapToGlobal(QPoint(0, self.height() + 4))
            self.dropdown.setGeometry(global_pos.x(), global_pos.y(), self.width(), 240)
            
    def _on_text_changed(self, text: str):
        if self.is_focused:
            self.dropdown.populate(text, self.main_window.bookmarks_manager, self.main_window.history_manager)
            
    def _on_suggestion_selected(self, url: str):
        self.setText(url)
        self.real_url_text = url
        self.main_window.navigate_to_url()
        
    def _share_current_url(self):
        """Copy current URL to clipboard with status message feedback."""
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(self.real_url_text)
        self.main_window.status.showMessage("URL Copied to Clipboard! ✓", 2000)
