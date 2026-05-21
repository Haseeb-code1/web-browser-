"""
Sleek, modular History Dialog for Nova Browser.
Provides searchable history logs, custom context actions, and clear routines.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QPushButton, QLabel, QApplication, QMenu
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QAction

from src.ui.theme import BACKGROUND_SECONDARY, BACKGROUND_TERTIARY, BACKGROUND_ELEVATED, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT_DANGER
from src.ui.icons import ICON_HISTORY, ICON_CLOSE, icon_to_qicon

class NovaHistoryDialog(QDialog):
    """Modern history manager dialog matching space-dark palette constraints."""
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent or main_window)
        self.main_window = main_window
        self.setWindowTitle("History Manager")
        self.setFixedSize(560, 420)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {BACKGROUND_SECONDARY};
                border: 1px solid rgba(108, 99, 255, 0.4);
                border-radius: 12px;
            }}
            QLabel {{
                color: {TEXT_PRIMARY};
            }}
            QLineEdit {{
                background-color: {BACKGROUND_TERTIARY};
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 16px;
                padding: 6px 12px;
                color: #FFFFFF;
            }}
            QListWidget {{
                background-color: {BACKGROUND_TERTIARY};
                border: none;
                border-radius: 10px;
                outline: none;
                padding: 6px;
            }}
            QListWidget::item {{
                padding: 8px 12px;
                border-radius: 8px;
                color: {TEXT_SECONDARY};
            }}
            QListWidget::item:hover {{
                background-color: {BACKGROUND_ELEVATED};
                color: #FFFFFF;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Header
        hdr = QHBoxLayout()
        title_lbl = QLabel("📜 Navigation History")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold;")
        hdr.addWidget(title_lbl)
        
        # Search input
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search history logs...")
        self.search_box.textChanged.connect(self._on_search)
        hdr.addWidget(self.search_box, 1)
        
        layout.addLayout(hdr)
        
        # List Widget
        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.list_widget)
        
        # Actions Layout
        btn_layout = QHBoxLayout()
        
        self.del_btn = QPushButton("Delete Selected")
        self.del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.del_btn.clicked.connect(self._delete_selected)
        
        self.clear_btn = QPushButton("Clear All History")
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.clicked.connect(self._clear_all)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.del_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.close_btn)
        
        layout.addLayout(btn_layout)
        
        self.refresh()
        
    def refresh(self):
        """Reload logs list."""
        self.list_widget.clear()
        entries = self.main_window.history_manager.get_history()
        search_text = self.search_box.text().lower()
        
        for idx, entry in enumerate(entries):
            if not search_text or search_text in entry.title.lower() or search_text in entry.url.lower():
                # Formatted item
                time_str = entry.timestamp[:16] if hasattr(entry, 'timestamp') else "Recent"
                item = QListWidgetItem(f"[{time_str}] {entry.title} - {entry.url}")
                item.setData(Qt.ItemDataRole.UserRole, (idx, entry.url))
                self.list_widget.addItem(item)
                
    def _on_search(self, text):
        self.refresh()
        
    def _delete_selected(self):
        item = self.list_widget.currentItem()
        if item:
            idx, url = item.data(Qt.ItemDataRole.UserRole)
            self.main_window.history_manager.remove_entry(idx)
            self.main_window.refresh_history_list()
            self.refresh()
            
    def _clear_all(self):
        self.main_window.history_manager.clear_history()
        self.main_window.refresh_history_list()
        self.refresh()
        
    def _on_item_double_clicked(self, item):
        idx, url = item.data(Qt.ItemDataRole.UserRole)
        self.main_window.tabs.add_new_tab(QUrl(url), "History")
        self.accept()
        
    def _show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item:
            return
            
        idx, url = item.data(Qt.ItemDataRole.UserRole)
        
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background: #1A1D2E; border: 1px solid rgba(255,255,255,0.06); }")
        
        open_act = menu.addAction("Open in New Tab")
        open_act.triggered.connect(lambda: self._on_item_double_clicked(item))
        
        copy_act = menu.addAction("Copy Link")
        copy_act.triggered.connect(lambda: QApplication.clipboard().setText(url))
        
        menu.addSeparator()
        
        del_act = menu.addAction("Delete Entry")
        del_act.triggered.connect(self._delete_selected)
        
        menu.exec(self.list_widget.viewport().mapToGlobal(pos))
