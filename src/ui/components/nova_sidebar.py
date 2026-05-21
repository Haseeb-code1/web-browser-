"""
Collapsible left Sidebar widget for Nova Browser.
Switches between collapsed (48px, icons only) and expanded (220px, icons + labels + stats).
Includes smooth animation transitions.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QFont

from src.ui.icons import ICON_GLOBE, ICON_BOOKMARK, ICON_HISTORY, ICON_DOWNLOAD, ICON_AI, ICON_SETTINGS, ICON_MOON, ICON_SUN, ICON_SIDEBAR, icon_to_qicon, icon_to_pixmap
from src.ui.theme import BACKGROUND_SECONDARY, BACKGROUND_TERTIARY, BACKGROUND_ELEVATED, ACCENT_PRIMARY, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_TERTIARY
from src.ui.animations import width_slide

class SidebarItem(QPushButton):
    """Interactive button in Sidebar with dynamic hover and left status indicator."""
    
    def __init__(self, svg_icon: str, label: str, is_collapsed: bool = True, parent=None):
        super().__init__(parent)
        self.svg_icon = svg_icon
        self.label = label
        self.is_collapsed = is_collapsed
        self.is_active = False
        
        self.setFixedSize(40, 40) if is_collapsed else self.setFixedHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_style()
        
    def set_collapsed(self, collapsed: bool):
        self.is_collapsed = collapsed
        if collapsed:
            self.setFixedSize(40, 40)
            self.setText("")
        else:
            self.setMinimumWidth(196)
            self.setMaximumWidth(196)
            self.setFixedHeight(40)
            self.setText(f"  {self.label}")
            
        self._update_style()
        
    def set_active(self, active: bool):
        self.is_active = active
        self._update_style()
        
    def _update_style(self):
        # We handle normal/active/hover styling using QSS
        icon_color = ACCENT_PRIMARY if self.is_active else "#8B8FA8"
        self.setIcon(icon_to_qicon(self.svg_icon, 16, icon_color, "#E8E9F3"))
        
        border_left = f"2px solid {ACCENT_PRIMARY}" if self.is_active else "none"
        bg_color = BACKGROUND_ELEVATED if self.is_active else "transparent"
        
        # Align left if expanded
        align = "align-left" if not self.is_collapsed else "align-center"
        padding = "padding-left: 12px;" if not self.is_collapsed else "padding: 0;"
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                border: none;
                border-left: {border_left};
                border-radius: 8px;
                color: {TEXT_PRIMARY if self.is_active else TEXT_SECONDARY};
                font-size: 13px;
                font-weight: 500;
                text-align: left;
                {padding}
            }}
            QPushButton:hover {{
                background-color: {BACKGROUND_TERTIARY};
                color: #FFFFFF;
            }}
        """)

class NovaSidebar(QWidget):
    """Custom sidebar with dynamic states, system summary cards, and collapse control."""
    
    state_changed = pyqtSignal(bool) # Emits True if expanded, False if collapsed
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.is_expanded = False
        
        self.setMinimumWidth(48)
        self.setMaximumWidth(48)
        self.setStyleSheet(f"background-color: {BACKGROUND_SECONDARY}; border-right: 1px solid rgba(255,255,255,0.06);")
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(4, 12, 4, 12)
        self.main_layout.setSpacing(12)
        
        # --- 1. Top Section (Logo + Toggle) ---
        self.top_widget = QWidget()
        self.top_layout = QHBoxLayout(self.top_widget)
        self.top_layout.setContentsMargins(4, 0, 4, 0)
        
        self.logo_label = QLabel()
        self.logo_label.setPixmap(icon_to_pixmap(ICON_AI, 20, ACCENT_PRIMARY))
        self.logo_label.setFixedSize(20, 20)
        self.logo_label.hide() # Hidden when collapsed
        
        self.toggle_btn = QPushButton()
        self.toggle_btn.setFixedSize(36, 36)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setIcon(icon_to_qicon(ICON_SIDEBAR, 16))
        self.toggle_btn.setStyleSheet("background: transparent; border: none; border-radius: 8px;")
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        self.toggle_btn.setToolTip("Toggle Sidebar (Ctrl+/)")
        
        self.top_layout.addWidget(self.logo_label)
        self.top_layout.addStretch()
        self.top_layout.addWidget(self.toggle_btn)
        self.main_layout.addWidget(self.top_widget)
        
        # --- 2. Middle Navigation Items ---
        self.nav_widget = QWidget()
        self.nav_layout = QVBoxLayout(self.nav_widget)
        self.nav_layout.setContentsMargins(0, 0, 0, 0)
        self.nav_layout.setSpacing(6)
        
        self.section_label = QLabel("NAVIGATION")
        self.section_label.setStyleSheet(f"color: {TEXT_TERTIARY}; font-size: 9px; font-weight: bold; margin-left: 8px; margin-top: 8px;")
        self.section_label.hide()
        self.nav_layout.addWidget(self.section_label)
        
        # Home
        self.item_new_tab = SidebarItem(ICON_GLOBE, "New Tab", is_collapsed=True)
        self.item_new_tab.clicked.connect(lambda: self.main_window.tabs.add_new_tab(label="New Tab"))
        self.nav_layout.addWidget(self.item_new_tab)
        
        # Bookmarks
        self.item_bookmarks = SidebarItem(ICON_BOOKMARK, "Bookmarks", is_collapsed=True)
        self.item_bookmarks.clicked.connect(self._toggle_bookmarks_panel)
        self.nav_layout.addWidget(self.item_bookmarks)
        
        # History
        self.item_history = SidebarItem(ICON_HISTORY, "History", is_collapsed=True)
        self.item_history.clicked.connect(self._toggle_history_panel)
        self.nav_layout.addWidget(self.item_history)
        
        # Downloads
        self.item_downloads = SidebarItem(ICON_DOWNLOAD, "Downloads", is_collapsed=True)
        self.item_downloads.clicked.connect(self._toggle_downloads_panel)
        self.nav_layout.addWidget(self.item_downloads)
        
        # AI Agent
        self.item_ai = SidebarItem(ICON_AI, "AI Assistant", is_collapsed=True)
        self.item_ai.clicked.connect(self._toggle_ai_panel)
        self.nav_layout.addWidget(self.item_ai)
        
        self.main_layout.addWidget(self.nav_widget)
        
        # --- 3. Stats Section (Expanded Only) ---
        self.stats_card = QFrame()
        self.stats_card.setStyleSheet(f"""
            QFrame {{
                background-color: {BACKGROUND_TERTIARY};
                border: 1px solid rgba(255,255,255,0.04);
                border-radius: 10px;
                margin: 4px;
            }}
            QLabel {{
                border: none;
                background: transparent;
            }}
        """)
        stats_layout = QVBoxLayout(self.stats_card)
        stats_layout.setContentsMargins(10, 10, 10, 10)
        
        self.stats_header = QLabel("SYSTEM STATISTICS")
        self.stats_header.setStyleSheet(f"color: {TEXT_TERTIARY}; font-size: 9px; font-weight: bold;")
        stats_layout.addWidget(self.stats_header)
        
        self.stats_tabs = QLabel("• 3 Tabs Active")
        self.stats_tabs.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
        stats_layout.addWidget(self.stats_tabs)
        
        self.stats_bms = QLabel("• 24 Bookmarks Saved")
        self.stats_bms.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
        stats_layout.addWidget(self.stats_bms)
        
        self.stats_card.hide()
        self.main_layout.addWidget(self.stats_card)
        
        self.main_layout.addStretch()
        
        # --- 4. Bottom Actions ---
        self.bottom_widget = QWidget()
        self.bottom_layout = QVBoxLayout(self.bottom_widget)
        self.bottom_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_layout.setSpacing(6)
        
        # Theme Toggle
        self.item_theme = SidebarItem(ICON_MOON, "Dark Mode", is_collapsed=True)
        self.item_theme.clicked.connect(self.main_window.toggle_dark_mode)
        self.bottom_layout.addWidget(self.item_theme)
        
        # Settings
        self.item_settings = SidebarItem(ICON_SETTINGS, "Settings", is_collapsed=True)
        self.item_settings.clicked.connect(self.main_window.show_settings_dialog)
        self.bottom_layout.addWidget(self.item_settings)
        
        self.main_layout.addWidget(self.bottom_widget)
        
        # Single shot timer to update stats live
        self.stats_timer = QTimer(self)
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(5000)
        
    def toggle_sidebar(self):
        """Perform slide animation transition on sidebar toggle."""
        self.is_expanded = not self.is_expanded
        
        start_w = 220 if not self.is_expanded else 48
        end_w = 48 if not self.is_expanded else 220
        
        # Hide labels instantly on collapsing to avoid layout overflows
        if not self.is_expanded:
            self.logo_label.hide()
            self.section_label.hide()
            self.stats_card.hide()
            self.item_new_tab.set_collapsed(True)
            self.item_bookmarks.set_collapsed(True)
            self.item_history.set_collapsed(True)
            self.item_downloads.set_collapsed(True)
            self.item_ai.set_collapsed(True)
            self.item_theme.set_collapsed(True)
            self.item_settings.set_collapsed(True)
            self.main_layout.setContentsMargins(4, 12, 4, 12)
        else:
            self.main_layout.setContentsMargins(12, 12, 12, 12)
            
        # Trigger dynamic QPropertyAnimation width slider
        self.anim = width_slide(self, start_w, end_w, 200)
        self.anim.finished.connect(self._on_slide_finished)
        
        self.state_changed.emit(self.is_expanded)
        
    def _on_slide_finished(self):
        if self.is_expanded:
            self.logo_label.show()
            self.section_label.show()
            self.stats_card.show()
            self.item_new_tab.set_collapsed(False)
            self.item_bookmarks.set_collapsed(False)
            self.item_history.set_collapsed(False)
            self.item_downloads.set_collapsed(False)
            self.item_ai.set_collapsed(False)
            self.item_theme.set_collapsed(False)
            self.item_settings.set_collapsed(False)
            self.update_stats()
            
        # Standardize size properties after animation terminates
        target_w = 220 if self.is_expanded else 48
        self.setMinimumWidth(target_w)
        self.setMaximumWidth(target_w)
        
    def update_stats(self):
        if self.is_expanded:
            try:
                tab_count = self.main_window.tabs.count()
                bm_count = len(self.main_window.bookmarks_manager.get_bookmarks())
                self.stats_tabs.setText(f"• {tab_count} Tabs Active")
                self.stats_bms.setText(f"• {bm_count} Bookmarks Saved")
            except Exception:
                pass
                
    def _toggle_bookmarks_panel(self):
        self._show_panel_tab("Bookmarks")
        
    def _toggle_history_panel(self):
        self._show_panel_tab("History")
        
    def _toggle_downloads_panel(self):
        self._show_panel_tab("Downloads")
        
    def _toggle_ai_panel(self):
        self._show_panel_tab("AI Assistant")
        
    def _show_panel_tab(self, tab_label: str):
        dock = self.main_window.side_panel_dock
        if not dock.isVisible():
            dock.setVisible(True)
        
        tabs = self.main_window.side_panel_tabs
        for i in range(tabs.count()):
            if tabs.tabText(i) == tab_label:
                tabs.setCurrentIndex(i)
                break
