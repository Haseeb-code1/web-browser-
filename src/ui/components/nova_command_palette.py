"""
Floating Command Palette component for Nova Browser.
Triggered by Ctrl+K or Ctrl+P. Provides searchable hotkey access to browser actions,
bookmarks, history, and active tabs.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QKeyEvent

from src.ui.icons import ICON_AI, ICON_GLOBE, ICON_BOOKMARK, ICON_HISTORY, icon_to_qicon
from src.ui.theme import BACKGROUND_TERTIARY, BACKGROUND_ELEVATED, ACCENT_PRIMARY, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_TERTIARY

class CommandPaletteItem(QListWidgetItem):
    """Specific formatted item representing a searchable command action."""
    
    def __init__(self, title: str, category: str, icon_svg: str, callback, parent=None):
        super().__init__(parent)
        self.title = title
        self.category = category
        self.callback = callback
        
        self.setText(f"  {title}")
        self.setToolTip(f"Category: {category}")
        self.setIcon(icon_to_qicon(icon_svg, 14))

class NovaCommandPalette(QDialog):
    """Frameless command launcher search bar float-overlay."""
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent or main_window)
        self.main_window = main_window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setModal(True)
        self.setFixedSize(520, 360)
        
        # Space-dark border dialog stylings
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {BACKGROUND_TERTIARY};
                border: 1px solid rgba(108, 99, 255, 0.4);
                border-radius: 16px;
            }}
            QLineEdit {{
                background-color: transparent;
                border: none;
                font-size: 15px;
                color: #FFFFFF;
                padding: 12px;
            }}
            QListWidget {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                padding: 8px 12px;
                border-radius: 8px;
                color: {TEXT_SECONDARY};
                font-size: 13px;
            }}
            QListWidget::item:hover, QListWidget::item:selected {{
                background-color: {BACKGROUND_ELEVATED};
                color: #FFFFFF;
            }}
        """)
        
        # Soft outer shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(32)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 12)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Search Input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type a command or search...")
        self.search_input.textChanged.connect(self._on_search)
        layout.addWidget(self.search_input)
        
        # Separator line
        sep = QFrame = QLabel()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: rgba(255,255,255,0.06);")
        layout.addWidget(sep)
        
        # List Widget
        self.list_widget = QListWidget()
        self.list_widget.itemActivated.connect(self._on_item_activated)
        self.list_widget.itemClicked.connect(self._on_item_activated)
        layout.addWidget(self.list_widget)
        
        # Bottom hint bar
        hint_lbl = QLabel("↑↓ to navigate  •  Enter to select  •  Esc to close")
        hint_lbl.setStyleSheet(f"color: {TEXT_TERTIARY}; font-size: 10px; margin-left: 8px;")
        layout.addWidget(hint_lbl)
        
        self._all_commands = []
        self._build_commands_list()
        self._on_search("")
        
    def showEvent(self, event):
        """Center palette perfectly in viewport geometry of parent window."""
        if self.parentWidget():
            p_geom = self.parentWidget().geometry()
            self.move(
                p_geom.x() + (p_geom.width() - self.width()) // 2,
                p_geom.y() + (p_geom.height() - self.height()) // 2
            )
        super().showEvent(event)
        self.search_input.setFocus()
        
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        elif event.key() == Qt.Key.Key_Down:
            self.list_widget.setCurrentRow((self.list_widget.currentRow() + 1) % self.list_widget.count())
        elif event.key() == Qt.Key.Key_Up:
            self.list_widget.setCurrentRow((self.list_widget.currentRow() - 1 + self.list_widget.count()) % self.list_widget.count())
        elif event.key() == Qt.Key.Key_Return:
            item = self.list_widget.currentItem()
            if item:
                self._on_item_activated(item)
        else:
            super().keyPressEvent(event)
            
    def _build_commands_list(self):
        """Pre-populate static system commands."""
        m = self.main_window
        self._all_commands = [
            ("⚡ Open New Tab", "COMMANDS", ICON_GLOBE, lambda: m.tabs.add_new_tab()),
            ("⚡ Open Private Incognito Tab", "COMMANDS", ICON_GLOBE, lambda: m.tabs.add_new_tab(incognito=True)),
            ("⚡ Open Preferences settings", "COMMANDS", ICON_AI, lambda: m.show_settings_dialog()),
            ("⚡ Toggle Left Sidebar Menu", "COMMANDS", ICON_AI, lambda: m.sidebar.toggle_sidebar()),
            ("⚡ Toggle Bookmarks Bar Display", "COMMANDS", ICON_BOOKMARK, lambda: m.toggle_bookmarks_bar()),
            ("⚡ Clear Browser History Logs", "COMMANDS", ICON_HISTORY, lambda: m.history_manager.clear()),
            ("⚡ Close Active Current Tab", "COMMANDS", ICON_GLOBE, lambda: m.tabs.close_current_tab()),
        ]
        
    def _on_search(self, text: str):
        self.list_widget.clear()
        
        # 1. Filter default commands
        for title, cat, icon, cb in self._all_commands:
            if not text or text.lower() in title.lower():
                item = CommandPaletteItem(title, cat, icon, cb)
                self.list_widget.addItem(item)
                
        # 2. Filter bookmarks
        try:
            for bm in self.main_window.bookmarks_manager.get_bookmarks():
                if text and (text.lower() in bm.title.lower() or text.lower() in bm.url.lower()):
                    item = CommandPaletteItem(f"⭐ Bookmark: {bm.title}", "BOOKMARKS", ICON_BOOKMARK, lambda u=bm.url: self.main_window.tabs.current_browser().setUrl(QUrl(u)))
                    self.list_widget.addItem(item)
        except Exception:
            pass
            
        # Select first item as active cursor default
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)
            
    def _on_item_activated(self, item: CommandPaletteItem):
        if hasattr(item, 'callback') and item.callback:
            item.callback()
        self.accept()
