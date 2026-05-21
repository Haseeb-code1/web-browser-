import os
from PyQt6.QtWidgets import (
    QMainWindow, QToolBar, QLineEdit, QStatusBar,
    QMessageBox, QDialog, QVBoxLayout, QListWidget, QListWidgetItem,
    QDockWidget, QWidget, QTextEdit, QPushButton, QHBoxLayout,
    QTabWidget, QMenu, QInputDialog, QToolButton, QLabel,
    QStackedWidget, QFormLayout, QComboBox, QCheckBox, QApplication
)
from PyQt6.QtGui import QIcon, QKeySequence, QActionGroup, QAction, QGuiApplication
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtNetwork import QNetworkProxy

from src.ui.tab_manager import TabManager
from src.core.settings_manager import SettingsManager
from src.core.bookmarks import BookmarksManager
from src.core.history import HistoryManager
from src.utils import url_utils
from src.utils.exception_logger import log_exception
from src.utils.paths import get_data_file_path

# --- Nova Browser Theme & Stylesheet imports ---
from src.ui.theme import *
from src.ui.stylesheet import NOVA_STYLESHEET
from src.ui.cursor import get_arrow_cursor, get_pointer_cursor, get_ibeam_cursor, get_wait_cursor
from src.ui.new_tab_page import get_new_tab_html

# --- Nova Browser Dialogs & Components ---
from src.ui.dialogs.nova_settings import NovaSettingsDialog
from src.ui.dialogs.nova_history import NovaHistoryDialog
from src.ui.dialogs.nova_downloads import NovaDownloadsDialog

from src.ui.components.nova_tab_bar import NovaTabBar
from src.ui.components.nova_address_bar import NovaAddressBar
from src.ui.components.nova_toolbar import NovaTitleBar, NovaToolbar
from src.ui.components.nova_sidebar import NovaSidebar
from src.ui.components.nova_bookmarks_bar import NovaBookmarksBar
from src.ui.components.nova_status_bar import NovaStatusBar
from src.ui.components.nova_context_menu import NovaContextMenu
from src.ui.components.nova_find_bar import NovaFindBar
from src.ui.components.nova_command_palette import NovaCommandPalette



class BrowserWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, is_private=False):
        super().__init__()
        self.is_private = is_private
        self.settings = SettingsManager()
        self.bookmarks_manager = BookmarksManager()
        self.history_manager = HistoryManager()
        
        self.init_ui()

    def init_ui(self) -> None:
        """Initializes the GUI with Nova Browser premium design system."""
        icon_path = get_data_file_path("app_icon.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setMinimumSize(900, 600)
        
        # Apply Nova Space-Dark stylesheet universally
        self.setStyleSheet(NOVA_STYLESHEET)
        
        if self.is_private:
            self.setWindowTitle("Nova Browser (Private)")
        else:
            self.setWindowTitle("Nova Browser")
        
        # Setup Tabs
        self.tabs = TabManager(self, self.is_private)
        self.setCentralWidget(self.tabs)
        self.tabs.url_changed.connect(self.update_urlbar)
        self.tabs.load_progress.connect(self.update_progress)
        
        # AI Assistant Setup
        from src.ai_assistant.floating_bot import FloatingBot
        from src.ai_assistant.selection_watcher import SelectionWatcher
        from src.ai_assistant.browser_controller import BrowserController
        from PyQt6.QtGui import QShortcut, QKeySequence
        
        self.browser_controller = BrowserController(self)
        self.floating_bot = FloatingBot(parent=self)
        self.selection_watcher = SelectionWatcher()
        
        shortcut_bot = QShortcut(QKeySequence("Ctrl+5"), self)
        shortcut_bot.activated.connect(self.toggle_floating_bot)
        
        self.floating_bot.command_issued.connect(
            self.browser_controller.parse_and_execute
        )
        
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # ── Nova Navigation Toolbar ──
        self.navbar = QToolBar("Navigation")
        self.navbar.setMovable(False)
        self.addToolBar(self.navbar)
        
        # Nav Buttons
        self._add_nav_action("Back", "⮜", self.navigate_back)
        self._add_nav_action("Forward", "⮞", self.navigate_forward)
        self._add_nav_action("Reload", "⟳", self.navigate_reload)
        self._add_nav_action("Home", "🏠", self.navigate_home)
        
        # URL Bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search the web or enter a URL...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.navbar.addWidget(self.url_bar)
        
        # Actions
        self._add_nav_action("Bookmark", "⭐", self.add_bookmark)
        
        # 3-Dots Settings Menu (Chrome-like)
        self.settings_btn = QToolButton()
        self.settings_btn.setText("⋮")
        self.settings_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.settings_menu = QMenu(self)
        self.settings_btn.setMenu(self.settings_menu)
        self.navbar.addWidget(self.settings_btn)

        # Extensions Quick-Access Button
        self.ext_btn = QToolButton()
        self.ext_btn.setText("🧩")
        self.ext_btn.setToolTip("Extensions Manager  (Ctrl+Shift+E)")
        self.ext_btn.clicked.connect(self.show_extensions_dialog)
        self.navbar.addWidget(self.ext_btn)
        
        # ── Status Bar ──
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        
        # ── Unified Side Panel (Dock) ──
        self.side_panel_dock = QDockWidget("Side Panel", self)
        self.side_panel_tabs = QTabWidget()
        
        # 1. Bookmarks Tab
        self.bookmarks_list = QListWidget()
        self.bookmarks_list.itemDoubleClicked.connect(self.load_bookmark)
        self.side_panel_tabs.addTab(self.bookmarks_list, "Bookmarks")
        self.refresh_bookmarks_list()
        
        # 2. History Tab
        self.history_widget = QWidget()
        self.history_layout = QVBoxLayout(self.history_widget)
        
        self.history_list = QListWidget()
        self.history_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.history_list.customContextMenuRequested.connect(self.show_history_context_menu)
        self.history_list.itemDoubleClicked.connect(self.load_history_item)
        
        self.history_del_btn = QPushButton("Delete Selected")
        self.history_del_btn.clicked.connect(self.delete_history_entry)
        
        self.history_clear_btn = QPushButton("Clear All History")
        self.history_clear_btn.clicked.connect(self.clear_all_history)
        
        btn_layout_h = QHBoxLayout()
        btn_layout_h.addWidget(self.history_del_btn)
        btn_layout_h.addWidget(self.history_clear_btn)
        
        self.history_layout.addWidget(self.history_list)
        self.history_layout.addLayout(btn_layout_h)
        
        self.side_panel_tabs.addTab(self.history_widget, "History")
        self.refresh_history_list()
        
        # 3. Downloads Tab
        self.downloads_list = QListWidget()
        self.side_panel_tabs.addTab(self.downloads_list, "Downloads")
        
        # 4. AI Assistant Tab
        self.ai_widget = QWidget()
        self.ai_layout = QVBoxLayout(self.ai_widget)
        
        self.ai_model_combo = QComboBox()
        self.ai_model_combo.addItems(["🔀 Auto", "⚡ Groq Llama 3", "🧠 Phi-3 Mini"])
        self.ai_model_combo.setStyleSheet("margin-bottom: 5px;")
        import json as _json2
        try:
            with open(get_data_file_path("config.json"), "r") as f:
                _cfg = _json2.load(f)
                _def = _cfg.get("default_model", "auto")
                if _def == "groq": self.ai_model_combo.setCurrentText("⚡ Groq Llama 3")
                elif _def == "phi3": self.ai_model_combo.setCurrentText("🧠 Phi-3 Mini")
        except:
            pass
        self.ai_layout.addWidget(self.ai_model_combo)
        
        self.ai_chat_display = QTextEdit()
        self.ai_chat_display.setReadOnly(True)
        self.ai_chat_display.setHtml(f"<b style='color:{ACCENT_PRIMARY};'>Nova AI:</b> Hello! How can I help you today?")
        
        self.ai_input = QLineEdit()
        self.ai_input.setPlaceholderText("Ask the AI something...")
        self.ai_input.returnPressed.connect(self.send_ai_message)
        
        btn_layout = QHBoxLayout()
        self.ai_send_btn = QPushButton("Send")
        self.ai_send_btn.clicked.connect(self.send_ai_message)
        
        self.ai_summarize_btn = QPushButton("Summarize Page")
        self.ai_summarize_btn.clicked.connect(self.ai_summarize_current_page)
        
        btn_layout.addWidget(self.ai_send_btn)
        btn_layout.addWidget(self.ai_summarize_btn)
        
        self.ai_layout.addWidget(self.ai_chat_display)
        self.ai_layout.addWidget(self.ai_input)
        self.ai_layout.addLayout(btn_layout)
        self.side_panel_tabs.addTab(self.ai_widget, "AI Assistant")
        
        self.side_panel_dock.setWidget(self.side_panel_tabs)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.side_panel_dock)
        self.side_panel_dock.hide()
        
        # ── Status Bar & Floating AI Button ──
        self.status = self.statusBar()
        self.floating_ai_btn = QPushButton("✦  NOVA A.I.  ✦")
        self.floating_ai_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.floating_ai_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0,y1:0,x2:1,y2:0,
                    stop:0 rgba(108, 99, 255, 0.25),
                    stop:1 rgba(0, 212, 255, 0.25));
                color: #ffffff;
                border: 2px solid rgba(108, 99, 255, 0.7);
                border-radius: 12px;
                padding: 4px 18px;
                font-weight: 800;
                font-size: 11px;
                letter-spacing: 1px;
                margin-bottom: 2px;
                margin-right: 8px;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0,y1:0,x2:1,y2:0,
                    stop:0 rgba(108, 99, 255, 0.5),
                    stop:1 rgba(0, 212, 255, 0.5));
                border-color: rgba(0, 212, 255, 0.9);
                color: #ffffff;
            }}
        """)
        
        def _toggle_ai_panel():
            if not self.side_panel_dock.isVisible():
                self.side_panel_dock.setVisible(True)
            for i in range(self.side_panel_tabs.count()):
                if self.side_panel_tabs.tabText(i) == "AI Assistant":
                    self.side_panel_tabs.setCurrentIndex(i)
                    break
                    
        self.floating_ai_btn.clicked.connect(_toggle_ai_panel)
        self.status.addPermanentWidget(self.floating_ai_btn)
        
        # ── Nova Keyboard Shortcuts ──
        from PyQt6.QtGui import QShortcut
        
        # Ctrl+K / Ctrl+P: Command Palette
        shortcut_cmd_k = QShortcut(QKeySequence("Ctrl+K"), self)
        shortcut_cmd_k.activated.connect(self.show_command_palette)
        shortcut_cmd_p = QShortcut(QKeySequence("Ctrl+P"), self)
        shortcut_cmd_p.activated.connect(self.show_command_palette)
        
        # Ctrl+F: Find Bar (uses browser's built-in find)
        shortcut_find = QShortcut(QKeySequence("Ctrl+F"), self)
        shortcut_find.activated.connect(self._toggle_find_bar)
        
        # Ctrl+/: Toggle Side Panel
        shortcut_panel = QShortcut(QKeySequence("Ctrl+/"), self)
        shortcut_panel.activated.connect(lambda: self.side_panel_dock.setVisible(not self.side_panel_dock.isVisible()))
        
        # Menus
        self._populate_settings_menu()
        
        # Load Homepage
        homepage = self.settings.get_setting("homepage")
        self.tabs.add_new_tab(QUrl(homepage), "Homepage")


    def _add_nav_action(self, name: str, text: str, callback) -> None:
        """Adds an action to the navbar."""
        action = QAction(text, self)
        action.setToolTip(name)
        action.triggered.connect(callback)
        self.navbar.addAction(action)

    def _populate_settings_menu(self) -> None:
        """Populates the 3-dots Chrome-style settings menu."""
        
        new_tab_act = QAction("New Tab", self)
        new_tab_act.setShortcut(QKeySequence("Ctrl+T"))
        new_tab_act.triggered.connect(lambda: self.tabs.add_new_tab(QUrl(self.settings.get_setting("homepage")), "New Tab"))
        self.settings_menu.addAction(new_tab_act)
        
        incognito_act = QAction("New Incognito Tab", self)
        incognito_act.setShortcut(QKeySequence("Ctrl+Shift+N"))
        incognito_act.triggered.connect(lambda: self.tabs.add_new_tab(QUrl(self.settings.get_setting("homepage")), "Incognito", True))
        self.settings_menu.addAction(incognito_act)
        
        private_win_act = QAction("New Private Window", self)
        private_win_act.setShortcut(QKeySequence("Ctrl+Shift+P"))
        private_win_act.triggered.connect(self.open_private_window)
        self.settings_menu.addAction(private_win_act)
        
        self.settings_menu.addSeparator()
        
        zoom_in_act = QAction("Zoom In", self)
        zoom_in_act.setShortcut(QKeySequence("Ctrl+="))
        zoom_in_act.triggered.connect(self.zoom_in)
        self.settings_menu.addAction(zoom_in_act)
        
        zoom_out_act = QAction("Zoom Out", self)
        zoom_out_act.setShortcut(QKeySequence("Ctrl+-"))
        zoom_out_act.triggered.connect(self.zoom_out)
        self.settings_menu.addAction(zoom_out_act)
        
        self.settings_menu.addSeparator()
        
        hist_act = QAction("Show Full History Dialog", self)
        hist_act.triggered.connect(self.show_history_dialog)
        self.settings_menu.addAction(hist_act)
        
        panel_act = QAction("Toggle Side Panel", self)
        panel_act.triggered.connect(lambda: self.side_panel_dock.setVisible(not self.side_panel_dock.isVisible()))
        self.settings_menu.addAction(panel_act)
        
        dl_act = QAction("Show Full Downloads Dialog", self)
        dl_act.triggered.connect(self.show_downloads_dialog)
        self.settings_menu.addAction(dl_act)
        
        self.settings_menu.addSeparator()
        
        vpn_act = QAction("Toggle Built-in VPN (Proxy)", self)
        vpn_act.triggered.connect(self.toggle_vpn)
        self.settings_menu.addAction(vpn_act)
        
        ad_act = QAction("Toggle AdGuard (Ad Blocker)", self)
        ad_act.triggered.connect(self.toggle_adblocker)
        self.settings_menu.addAction(ad_act)
        
        ext_act = QAction("Extensions Manager", self)
        ext_act.setShortcut(QKeySequence("Ctrl+Shift+E"))
        ext_act.triggered.connect(self.show_extensions_dialog)
        self.settings_menu.addAction(ext_act)
        
        self.settings_menu.addSeparator()
        
        settings_act = QAction("Settings", self)
        settings_act.triggered.connect(self.show_settings_dialog)
        self.settings_menu.addAction(settings_act)

    def navigate_to_url(self) -> None:
        """Navigates to the URL in the address bar."""
        try:
            url_str = self.url_bar.text()
            if not url_utils.is_valid_url(url_str):
                search_engine = self.settings.get_setting("search_engine")
                url_str = url_utils.get_search_url(url_str, search_engine)
            else:
                url_str = url_utils.format_url(url_str)
                
            self.tabs.current_browser().setUrl(QUrl(url_str))
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Navigation Error", str(e))

    def update_urlbar(self, q: QUrl) -> None:
        """Updates the URL bar text."""
        self.url_bar.setText(q.toString())
        self.url_bar.setCursorPosition(0)

    def update_progress(self, p: int) -> None:
        """Updates status bar with loading progress."""
        if p < 100:
            self.status.showMessage(f"Loading {p}%")
        else:
            self.status.clearMessage()

    # AI Assistant Methods
    def toggle_floating_bot(self):
        if self.floating_bot.isVisible():
            self.floating_bot.close_animate()
        else:
            selected = QApplication.clipboard().text()
            self.floating_bot.open_animate(selected_text=selected)

    def on_tab_changed(self, index):
        widget = self.tabs.widget(index)
        if widget and hasattr(widget, 'browser'):
            web_view = widget.browser
            self.selection_watcher.start_watching(web_view)
            try:
                self.selection_watcher.selection_changed.disconnect()
            except TypeError:
                pass
            self.selection_watcher.selection_changed.connect(
                self.floating_bot.set_query
            )
            # Make sure to inject script on load finished as well, or at least try here
            self.selection_watcher.inject_selection_script(web_view)
            try:
                web_view.loadFinished.disconnect(lambda _: self.selection_watcher.inject_selection_script(web_view))
            except TypeError:
                pass
            web_view.loadFinished.connect(lambda _: self.selection_watcher.inject_selection_script(web_view))

    # Navigation Wrappers
    def navigate_home(self):
        self.tabs.current_browser().setUrl(QUrl(self.settings.get_setting("homepage")))
    def navigate_back(self):
        self.tabs.current_browser().back()
    def navigate_forward(self):
        self.tabs.current_browser().forward()
    def navigate_reload(self):
        self.tabs.current_browser().reload()
    def navigate_stop(self):
        self.tabs.current_browser().stop()

    # Zoom
    def zoom_in(self):
        browser = self.tabs.current_browser()
        browser.setZoomFactor(browser.zoomFactor() + 0.1)
    def zoom_out(self):
        browser = self.tabs.current_browser()
        browser.setZoomFactor(browser.zoomFactor() - 0.1)

    # Dark Mode
    def toggle_dark_mode(self):
        current = self.settings.get_setting("theme")
        new_theme = "light" if current == "dark" else "dark"
        self.settings.set_setting("theme", new_theme)
        if new_theme == "dark":
            self.setStyleSheet(NOVA_STYLESHEET)
        else:
            self.setStyleSheet("")

    # ── Nova Command Palette & Find Bar ──
    def show_command_palette(self):
        """Opens the floating Ctrl+K command launcher."""
        palette = NovaCommandPalette(self)
        palette.exec()

    def _toggle_find_bar(self):
        """Opens the browser's native find-text dialog."""
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, "Find on Page", "Search text:")
        if ok and text:
            self.tabs.current_browser().findText(text)

    # Bookmarks
    def add_bookmark(self):
        url = self.tabs.current_browser().url().toString()
        title = self.tabs.tabText(self.tabs.currentIndex())
        self.bookmarks_manager.add_bookmark(url, title)
        self.refresh_bookmarks_list()
        self.status.showMessage("Bookmark added!", 2000)

    def refresh_bookmarks_list(self):
        self.bookmarks_list.clear()
        for bm in self.bookmarks_manager.get_bookmarks():
            self.bookmarks_list.addItem(f"{bm.title} ({bm.url})")

    def load_bookmark(self, item):
        url = item.text().split('(')[-1].strip(')')
        self.tabs.current_browser().setUrl(QUrl(url))

    # History
    def refresh_history_list(self):
        self.history_list.clear()
        for entry in self.history_manager.get_history()[:50]: # Show last 50
            self.history_list.addItem(f"{entry.timestamp[:16]} | {entry.title} ({entry.url})")

    def load_history_item(self, item):
        url = item.text().split('(')[-1].strip(')')
        self.tabs.current_browser().setUrl(QUrl(url))

    def show_history_context_menu(self, position):
        menu = QMenu()
        item = self.history_list.itemAt(position)
        
        if item:
            self.history_list.setCurrentItem(item)
            
            open_act = QAction("Open Link", self)
            open_act.triggered.connect(lambda: self.load_history_item(item))
            menu.addAction(open_act)
            
            copy_act = QAction("Copy Link", self)
            url = item.text().split('(')[-1].strip(')')
            copy_act.triggered.connect(lambda _, u=url: QApplication.clipboard().setText(u))
            menu.addAction(copy_act)
            
            menu.addSeparator()
            
            del_act = QAction("Delete Selected Entry", self)
            del_act.triggered.connect(self.delete_history_entry)
            menu.addAction(del_act)
            
        clear_act = QAction("Clear All History", self)
        clear_act.triggered.connect(self.clear_all_history)
        menu.addAction(clear_act)
        
        menu.exec(self.history_list.viewport().mapToGlobal(position))

    def delete_history_entry(self):
        row = self.history_list.currentRow()
        if row >= 0:
            self.history_manager.remove_entry(row)
            self.refresh_history_list()
            self.status.showMessage("History entry deleted.", 2000)

    def clear_all_history(self):
        self.history_manager.clear_history()
        self.refresh_history_list()
        self.status.showMessage("All history cleared.", 2000)

    def show_history_dialog(self):
        """Opens the Nova History Manager dialog."""
        dialog = NovaHistoryDialog(self)
        dialog.exec()

    # AI Integration
    def send_ai_message(self):
        query = self.ai_input.text().strip()
        if not query: return
        self.ai_input.clear()
        
        def ui_callback(html_text):
            self.ai_chat_display.append(html_text)
            self.status.showMessage("Agent active...")
            scroll = self.ai_chat_display.verticalScrollBar()
            scroll.setValue(scroll.maximum())
            
        from src.ai_agent.agent_brain import AgentBrain
        browser = self.tabs.current_browser()
        
        sel_text = self.ai_model_combo.currentText()
        if "Groq" in sel_text: model_choice = "groq"
        elif "Phi-3" in sel_text: model_choice = "phi3"
        else: model_choice = "auto"
        
        if not hasattr(self, 'current_agent'):
            self.current_agent = AgentBrain(browser, ui_callback, model_choice)
        else:
            self.current_agent.model_choice = model_choice
            self.current_agent.executor.web_view = browser
            
        self.current_agent.start_task(query)
        self.status.clearMessage()

    def ai_summarize_current_page(self):
        query = "Read the current page and give me a brief summary of what it's about."
        self.ai_input.setText(query)
        self.send_ai_message()

    def open_private_window(self):
        """Opens a new completely private browser window."""
        self.private_win = BrowserWindow(is_private=True)
        self.private_win.show()

    def refresh_downloads_list(self):
        """Updates the downloads tab from the download manager."""
        self.downloads_list.clear()
        
        active = self.tabs.download_manager.active_downloads
        if active:
            self.downloads_list.addItem("--- ACTIVE ---")
            for dl_id, info in active.items():
                speed_mb = info.get("speed_bps", 0) / (1024 * 1024)
                self.downloads_list.addItem(f"⏳ {info['filename']} ({speed_mb:.2f} MB/s)")
            self.downloads_list.addItem("")
            
        self.downloads_list.addItem("--- HISTORY ---")
        for dl in reversed(self.tabs.download_manager.downloads_history):
            self.downloads_list.addItem(f"✓ {dl}")
            
    def show_downloads_dialog(self):
        """Opens the Nova Downloads Manager dialog."""
        dialog = NovaDownloadsDialog(self)
        dialog.exec()
            
    def toggle_vpn(self):
        if not hasattr(self, 'vpn_enabled') or not self.vpn_enabled:
            # Prompt user for proxy details
            proxy_addr, ok = QInputDialog.getText(
                self, 
                "VPN / Proxy Setup", 
                "Enter Proxy Server (Format: IP:PORT)\n(Public proxies are often slow or offline):",
                QLineEdit.EchoMode.Normal,
                "185.199.229.156:8080"
            )
            
            if not ok:
                return # User cancelled
                
            try:
                host, port_str = proxy_addr.split(":")
                port = int(port_str)
                
                proxy = QNetworkProxy()
                proxy.setType(QNetworkProxy.ProxyType.HttpProxy)
                proxy.setHostName(host.strip())
                proxy.setPort(port)
                QNetworkProxy.setApplicationProxy(proxy)
                
                self.vpn_enabled = True
                self.status.showMessage(f"VPN Enabled ({host})", 3000)
                QMessageBox.information(self, "VPN Activated", f"Traffic is now routed through {host}:{port}.\n\nNOTE: If pages fail to load, the proxy server you entered is offline or blocking traffic. Disable the VPN to restore internet access.")
            except ValueError:
                QMessageBox.warning(self, "Invalid Format", "Please enter the proxy in IP:PORT format (e.g., 12.34.56.78:8080).")
        else:
            QNetworkProxy.setApplicationProxy(QNetworkProxy(QNetworkProxy.ProxyType.NoProxy))
            self.vpn_enabled = False
            self.status.showMessage("VPN Disabled", 3000)

    def toggle_adblocker(self):
        ad_blocker = self.tabs.ad_blocker
        ad_blocker.is_enabled = not ad_blocker.is_enabled
        state_str = "ON" if ad_blocker.is_enabled else "OFF"
        self.status.showMessage(f"AdGuard is now {state_str}", 3000)

    def show_extensions_dialog(self):
        """Opens the Chrome-style Extensions Manager dialog."""
        from src.ui.extensions_dialog import ExtensionsDialog

        def _on_extensions_changed():
            """Re-inject scripts into all profiles when user changes anything."""
            self.tabs._inject_extensions()
            self.status.showMessage("Extensions updated — reload a tab to apply changes.", 3000)

        dialog = ExtensionsDialog(self.tabs.extension_manager, parent=self)
        dialog.extensions_changed.connect(_on_extensions_changed)
        dialog.exec()

    def show_settings_dialog(self):
        """Opens the Nova Settings dialog."""
        dialog = NovaSettingsDialog(self)
        dialog.exec()

