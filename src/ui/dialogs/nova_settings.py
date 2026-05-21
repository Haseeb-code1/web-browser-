"""
Premium multi-page Preferences dialog for Nova Browser.
Uses left vertical sidebar menu cards to switch between:
General, Appearance, Search, Privacy, AI Keys, and Shortcuts.
"""

from PyQt6.QtWidgets import QDialog, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QStackedWidget, QLabel, QLineEdit, QComboBox, QCheckBox, QPushButton, QFormLayout
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

from src.ui.theme import BACKGROUND_SECONDARY, BACKGROUND_TERTIARY, BACKGROUND_ELEVATED, ACCENT_PRIMARY, TEXT_PRIMARY, TEXT_SECONDARY, RADIUS_MEDIUM
from src.ui.icons import ICON_SETTINGS, ICON_AI, ICON_GLOBE, ICON_BOOKMARK, ICON_HISTORY, icon_to_qicon

class NovaSettingsDialog(QDialog):
    """Sleek vertical sidebar preference dialog matching space-dark theme constraints."""
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent or main_window)
        self.main_window = main_window
        self.setWindowTitle("Preferences")
        self.setFixedSize(640, 480)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        
        # Dialog Style
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
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 10px 14px;
                border-radius: 8px;
                color: {TEXT_SECONDARY};
                font-size: 13px;
            }}
            QListWidget::item:selected {{
                background-color: {BACKGROUND_ELEVATED};
                color: {ACCENT_PRIMARY};
                font-weight: bold;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Top title
        title_lbl = QLabel("Nova Browser Settings")
        title_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(title_lbl)
        
        # Body section
        body_widget = QWidget()
        body_layout = QHBoxLayout(body_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(16)
        
        # Sidebar Menu list
        self.sidebar_menu = QListWidget()
        self.sidebar_menu.setFixedWidth(160)
        self.sidebar_menu.setIconSize(QSize(16, 16))
        self.sidebar_menu.addItem(QListWidgetItem(icon_to_qicon(ICON_GLOBE, 14), "General"))
        self.sidebar_menu.addItem(QListWidgetItem(icon_to_qicon(ICON_SETTINGS, 14), "Appearance"))
        self.sidebar_menu.addItem(QListWidgetItem(icon_to_qicon(ICON_GLOBE, 14), "Search Engine"))
        self.sidebar_menu.addItem(QListWidgetItem(icon_to_qicon(ICON_BOOKMARK, 14), "Privacy"))
        self.sidebar_menu.addItem(QListWidgetItem(icon_to_qicon(ICON_AI, 14), "AI Keys"))
        self.sidebar_menu.addItem(QListWidgetItem(icon_to_qicon(ICON_SETTINGS, 14), "Shortcuts"))
        self.sidebar_menu.currentRowChanged.connect(self._on_row_changed)
        body_layout.addWidget(self.sidebar_menu)
        
        # Stacked widgets
        self.stacked_pages = QStackedWidget()
        self.stacked_pages.setStyleSheet(f"background-color: {BACKGROUND_TERTIARY}; border-radius: 10px; padding: 12px;")
        body_layout.addWidget(self.stacked_pages)
        
        self._init_pages()
        layout.addWidget(body_widget)
        
        # Bottom Buttons
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        
        save_btn = QPushButton("Save Settings")
        save_btn.setProperty("accent", True)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._save_settings)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        
        bottom_layout.addStretch()
        bottom_layout.addWidget(cancel_btn)
        bottom_layout.addWidget(save_btn)
        layout.addWidget(bottom_widget)
        
        self.sidebar_menu.setCurrentRow(0)
        
    def _init_pages(self):
        """Build form controls inside pages stacked lists."""
        # Page 1: General
        p1 = QWidget()
        l1 = QFormLayout(p1)
        self.home_url_input = QLineEdit("https://www.google.com")
        self.home_url_input.setPlaceholderText("Homepage URL link")
        l1.addRow("Homepage:", self.home_url_input)
        
        self.startup_combo = QComboBox()
        self.startup_combo.addItems(["Show New Tab", "Continue last session", "Show homepage"])
        l1.addRow("On Startup:", self.startup_combo)
        self.stacked_pages.addWidget(p1)
        
        # Page 2: Appearance
        p2 = QWidget()
        l2 = QFormLayout(p2)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Nova Dark Space (default)", "Light Solarized"])
        l2.addRow("UI Theme:", self.theme_combo)
        
        self.tabs_position = QComboBox()
        self.tabs_position.addItems(["Top Toolbar Tabs", "Left Sidebar vertical"])
        l2.addRow("Tab Layout:", self.tabs_position)
        self.stacked_pages.addWidget(p2)
        
        # Page 3: Search
        p3 = QWidget()
        l3 = QFormLayout(p3)
        self.search_combo = QComboBox()
        self.search_combo.addItems(["Google Search", "DuckDuckGo", "Bing", "Brave Search"])
        l3.addRow("Search Engine:", self.search_combo)
        self.stacked_pages.addWidget(p3)
        
        # Page 4: Privacy
        p4 = QWidget()
        l4 = QVBoxLayout(p4)
        l4.setSpacing(10)
        self.track_chk = QCheckBox("Send 'Do Not Track' header blocks")
        self.track_chk.setChecked(True)
        l4.addWidget(self.track_chk)
        
        self.cookies_chk = QCheckBox("Block third-party cookies tracking")
        self.cookies_chk.setChecked(True)
        l4.addWidget(self.cookies_chk)
        
        self.history_chk = QCheckBox("Persist history navigation logs locally")
        self.history_chk.setChecked(True)
        l4.addWidget(self.history_chk)
        self.stacked_pages.addWidget(p4)
        
        # Page 5: AI Keys
        p5 = QWidget()
        l5 = QFormLayout(p5)
        
        import json
        from src.utils.paths import get_data_file_path
        
        cfg = {}
        try:
            with open(get_data_file_path("config.json"), "r") as f:
                cfg = json.load(f)
        except Exception:
            pass
            
        self.ollama_url = QLineEdit(cfg.get("ollama_base_url", "http://localhost:11434"))
        l5.addRow("Local Ollama Server:", self.ollama_url)
        
        self.ollama_model = QLineEdit(cfg.get("ollama_model", "phi3"))
        l5.addRow("Ollama Model:", self.ollama_model)
        
        self.groq_key = QLineEdit(cfg.get("groq_api_key", ""))
        self.groq_key.setEchoMode(QLineEdit.EchoMode.Password)
        l5.addRow("Groq API Key:", self.groq_key)
        
        self.groq_link = QLabel('<a href="https://console.groq.com/keys" style="color:#4F8EF7;">Get your Groq API Key here</a>')
        self.groq_link.setOpenExternalLinks(True)
        l5.addRow("", self.groq_link)
        
        self.groq_model = QLineEdit(cfg.get("groq_model", "llama-3.1-8b-instant"))
        l5.addRow("Groq Model:", self.groq_model)
        
        self.stacked_pages.addWidget(p5)
        
        # Page 6: Shortcuts
        p6 = QWidget()
        l6 = QVBoxLayout(p6)
        l6.setSpacing(6)
        l6.addWidget(QLabel("⌨ Nova Browser Keyboard maps:"))
        l6.addWidget(QLabel("  • Ctrl+K / Ctrl+P  -  Floating Command Palette"))
        l6.addWidget(QLabel("  • Ctrl+F  -  Find text highlight on page"))
        l6.addWidget(QLabel("  • Ctrl+T  -  Create new browser tab"))
        l6.addWidget(QLabel("  • Ctrl+W  -  Close current browser tab"))
        l6.addWidget(QLabel("  • Ctrl+B  -  Toggle horizontal Bookmarks Bar"))
        l6.addWidget(QLabel("  • Ctrl+/  -  Collapse/Expand Left Sidebar menu"))
        self.stacked_pages.addWidget(p6)
        
    def _on_row_changed(self, index: int):
        self.stacked_pages.setCurrentIndex(index)
        
    def _save_settings(self):
        """Persist settings values (e.g. settings parameters) back to main_window."""
        import json
        from src.utils.paths import get_data_file_path
        
        cfg = {}
        cfg_path = get_data_file_path("config.json")
        try:
            with open(cfg_path, "r") as f:
                cfg = json.load(f)
        except Exception:
            pass
            
        cfg["ollama_base_url"] = self.ollama_url.text()
        cfg["ollama_model"] = self.ollama_model.text()
        cfg["groq_api_key"] = self.groq_key.text()
        cfg["groq_model"] = self.groq_model.text()
        
        try:
            with open(cfg_path, "w") as f:
                json.dump(cfg, f, indent=4)
        except Exception:
            pass
            
        try:
            # We hook these values into main_window
            self.main_window.homepage_url = self.home_url_input.text()
            self.main_window.ai_assistant.ollama_base_url = self.ollama_url.text()
            self.main_window.ai_assistant.ollama_model = self.ollama_model.text()
        except Exception:
            pass
            
        try:
            # Apply Theme
            if self.theme_combo.currentIndex() == 1:
                self.main_window.settings.set_setting("theme", "light")
                self.main_window.setStyleSheet("")
            else:
                self.main_window.settings.set_setting("theme", "dark")
                from src.ui.stylesheet import NOVA_STYLESHEET
                self.main_window.setStyleSheet(NOVA_STYLESHEET)
                
            # Apply Tabs Position
            from PyQt6.QtWidgets import QTabWidget
            if self.tabs_position.currentIndex() == 1:
                self.main_window.tabs.setTabPosition(QTabWidget.TabPosition.West)
            else:
                self.main_window.tabs.setTabPosition(QTabWidget.TabPosition.North)
        except Exception as e:
            pass
            
        self.accept()
