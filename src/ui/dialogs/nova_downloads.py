"""
Premium Downloads Dialog for Nova Browser.
Offers progress tracking, speed stats, and direct action triggers.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QTimer

from src.ui.theme import BACKGROUND_SECONDARY, BACKGROUND_TERTIARY, BACKGROUND_ELEVATED, TEXT_PRIMARY, TEXT_SECONDARY
from src.ui.icons import ICON_DOWNLOAD, icon_to_qicon

class NovaDownloadsDialog(QDialog):
    """Real-time active downloads progress tracking dialog widget."""
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent or main_window)
        self.main_window = main_window
        self.setWindowTitle("Downloads Manager")
        self.setFixedSize(580, 420)
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
            QListWidget {{
                background-color: {BACKGROUND_TERTIARY};
                border: none;
                border-radius: 10px;
                outline: none;
                padding: 6px;
            }}
            QListWidget::item {{
                padding: 10px;
                border-radius: 8px;
                color: {TEXT_SECONDARY};
            }}
            QListWidget::item:hover, QListWidget::item:selected {{
                background-color: {BACKGROUND_ELEVATED};
                color: #FFFFFF;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Header
        title_lbl = QLabel("⬇ Downloads Manager")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_lbl)
        
        # List Widget
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        # Action Buttons Layout
        btn_layout = QHBoxLayout()
        
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pause_btn.clicked.connect(lambda: self._action("pause"))
        
        self.resume_btn = QPushButton("Resume")
        self.resume_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.resume_btn.clicked.connect(lambda: self._action("resume"))
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.clicked.connect(lambda: self._action("cancel"))
        
        self.del_btn = QPushButton("Delete Record")
        self.del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.del_btn.clicked.connect(lambda: self._action("delete"))
        
        self.close_btn = QPushButton("Close")
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.resume_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.del_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.close_btn)
        
        layout.addLayout(btn_layout)
        
        # Auto refresh timer (1s interval)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_list)
        self.timer.start(1000)
        
        self.update_list()
        
    def update_list(self):
        """Re-draw items lists matching active downloads statuses and history."""
        curr_row = self.list_widget.currentRow()
        self.list_widget.clear()
        
        dl_mgr = self.main_window.tabs.download_manager
        
        # 1. Active Downloads
        active = dl_mgr.active_downloads
        if active:
            header_item = QListWidgetItem("--- ACTIVE DOWNLOADS ---")
            header_item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.list_widget.addItem(header_item)
            
            for dl_id, info in active.items():
                speed_mb = info.get("speed_bps", 0) / (1024 * 1024)
                received_mb = info.get("received", 0) / (1024 * 1024)
                total_mb = info.get("total", 0) / (1024 * 1024)
                is_paused = info["request"].isPaused()
                
                status_icon = "⏸" if is_paused else "⏳"
                text = f"{status_icon} {info['filename']} - {received_mb:.1f}/{total_mb:.1f} MB ({speed_mb:.2f} MB/s)"
                
                item = QListWidgetItem(text)
                item.setData(Qt.ItemDataRole.UserRole, f"active:{dl_id}")
                self.list_widget.addItem(item)
                
            sep = QListWidgetItem("")
            sep.setFlags(Qt.ItemFlag.NoItemFlags)
            self.list_widget.addItem(sep)
            
        # 2. History
        history = dl_mgr.downloads_history
        header_history = QListWidgetItem("--- DOWNLOADS HISTORY ---")
        header_history.setFlags(Qt.ItemFlag.NoItemFlags)
        self.list_widget.addItem(header_history)
        
        for idx, entry in enumerate(reversed(history)):
            original_idx = len(history) - 1 - idx
            item = QListWidgetItem(f"✓ {entry}")
            item.setData(Qt.ItemDataRole.UserRole, f"history:{original_idx}")
            self.list_widget.addItem(item)
            
        if curr_row >= 0 and curr_row < self.list_widget.count():
            self.list_widget.setCurrentRow(curr_row)
            
    def _action(self, action_type: str):
        item = self.list_widget.currentItem()
        if not item:
            return
            
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return
            
        kind, ref = data.split(":", 1)
        dl_mgr = self.main_window.tabs.download_manager
        
        if kind == "active":
            dl_id = int(ref)
            if action_type == "pause":
                dl_mgr.pause_download(dl_id)
            elif action_type == "resume":
                dl_mgr.resume_download(dl_id)
            elif action_type == "cancel":
                dl_mgr.cancel_download(dl_id)
        elif kind == "history" and action_type == "delete":
            idx = int(ref)
            dl_mgr.delete_history(idx)
            
        self.update_list()
        
    def closeEvent(self, event):
        self.timer.stop()
        super().closeEvent(event)
