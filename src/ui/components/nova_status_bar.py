"""
Custom Status Bar component for Nova Browser.
Features status indicators, live page load times, a sliding link-hover text display,
micro-zoom increments, and encoding readouts.
"""

from PyQt6.QtWidgets import QStatusBar, QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor

from src.ui.icons import ICON_LOCK, icon_to_pixmap
from src.ui.theme import BACKGROUND_PRIMARY, ACCENT_SUCCESS, ACCENT_WARNING, ACCENT_DANGER, TEXT_SECONDARY

class NovaStatusBar(QStatusBar):
    """Bottom status bar widget containing dynamic site statistics and zoom micro-adjustments."""
    
    zoom_changed = pyqtSignal(int) # Emits +1 for zoom-in, -1 for zoom-out
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(24)
        self.setStyleSheet(f"background-color: {BACKGROUND_PRIMARY}; border-top: 1px solid rgba(255,255,255,0.06);")
        
        # Central horizontal widget layout
        self.container = QWidget()
        layout = QHBoxLayout(self.container)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(12)
        
        # --- Left: Connection dot and stats ---
        self.dot_lbl = QLabel("●")
        self.dot_lbl.setStyleSheet(f"color: {ACCENT_SUCCESS}; font-size: 11px;")
        
        self.status_lbl = QLabel("Connected")
        self.status_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
        
        layout.addWidget(self.dot_lbl)
        layout.addWidget(self.status_lbl)
        
        # --- Center: Hovered link ---
        self.hover_lbl = QLabel("")
        self.hover_lbl.setStyleSheet(f"color: #00D4FF; font-size: 11px; font-weight: 500;")
        layout.addWidget(self.hover_lbl, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # --- Right: Zoom, Security, Encoding ---
        # Zoom controls
        self.zoom_out_btn = QPushButton("-")
        self.zoom_out_btn.setFixedSize(14, 14)
        self.zoom_out_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.zoom_out_btn.setStyleSheet("QPushButton { background: rgba(255,255,255,0.05); border: none; border-radius: 3px; color: #FFFFFF; font-size: 10px; font-weight: bold; } QPushButton:hover { background: rgba(255,255,255,0.15); }")
        self.zoom_out_btn.clicked.connect(lambda: self.zoom_changed.emit(-1))
        
        self.zoom_lbl = QLabel("100%")
        self.zoom_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
        
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setFixedSize(14, 14)
        self.zoom_in_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.zoom_in_btn.setStyleSheet("QPushButton { background: rgba(255,255,255,0.05); border: none; border-radius: 3px; color: #FFFFFF; font-size: 10px; font-weight: bold; } QPushButton:hover { background: rgba(255,255,255,0.15); }")
        self.zoom_in_btn.clicked.connect(lambda: self.zoom_changed.emit(1))
        
        layout.addWidget(self.zoom_out_btn)
        layout.addWidget(self.zoom_lbl)
        layout.addWidget(self.zoom_in_btn)
        
        # Security icon + label
        self.sec_icon = QLabel()
        self.sec_icon.setPixmap(icon_to_pixmap(ICON_LOCK, 11, ACCENT_SUCCESS))
        self.sec_icon.setFixedSize(11, 11)
        
        self.sec_lbl = QLabel("Secure")
        self.sec_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
        
        layout.addWidget(self.sec_icon)
        layout.addWidget(self.sec_lbl)
        
        # Encoding
        self.enc_lbl = QLabel("UTF-8")
        self.enc_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
        layout.addWidget(self.enc_lbl)
        
        self.addWidget(self.container, 1)
        
    def set_loading(self, loading: bool):
        """Toggle connection dot loading/ready statuses."""
        if loading:
            self.dot_lbl.setText("●")
            self.dot_lbl.setStyleSheet(f"color: {ACCENT_WARNING}; font-size: 11px;")
            self.status_lbl.setText("Loading...")
        else:
            self.dot_lbl.setText("●")
            self.dot_lbl.setStyleSheet(f"color: {ACCENT_SUCCESS}; font-size: 11px;")
            self.status_lbl.setText("Connected")
            
    def set_load_time(self, seconds: float):
        """Displays formatted page render time."""
        self.status_lbl.setText(f"Loaded in {seconds:.2f}s")
        # Fade back to "Connected" after 5s
        QTimer.singleShot(5000, lambda: self.status_lbl.setText("Connected"))
        
    def set_hover_url(self, url: str):
        """Set or clear center elided url showing on hyperlink hover."""
        if url:
            if len(url) > 60:
                url = url[:57] + "..."
            self.hover_lbl.setText(url)
        else:
            self.hover_lbl.setText("")
            
    def set_zoom(self, factor: float):
        """Update inline zoom factor percentage label."""
        self.zoom_lbl.setText(f"{int(factor * 100)}%")
        
    def set_security(self, secure: bool):
        """Modify lock graphic color based on active HTTPS state."""
        if secure:
            self.sec_icon.setPixmap(icon_to_pixmap(ICON_LOCK, 11, ACCENT_SUCCESS))
            self.sec_lbl.setText("Secure")
        else:
            self.sec_icon.setPixmap(icon_to_pixmap(ICON_LOCK, 11, ACCENT_WARNING))
            self.sec_lbl.setText("Unsecured")
