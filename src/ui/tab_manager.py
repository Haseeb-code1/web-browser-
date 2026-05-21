from PyQt6.QtWidgets import QTabWidget, QVBoxLayout, QWidget, QMenu, QInputDialog
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PyQt6.QtCore import QUrl, pyqtSignal, Qt
import os

from src.ui.downloader import DownloadManager
from src.core.ad_blocker import AdBlockerInterceptor
from src.core.extension_manager import ExtensionManager
from src.utils.exception_logger import log_exception

class CustomWebPage(QWebEnginePage):
    """Custom web page to handle errors and specific behaviors."""
    
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        # We can ignore console messages to keep the terminal clean
        pass

class TabManager(QTabWidget):
    """Manages browser tabs and web views."""
    
    url_changed = pyqtSignal(QUrl)
    load_progress = pyqtSignal(int)
    
    def __init__(self, main_window, is_private=False):
        super().__init__(main_window)
        self.main_window = main_window
        self.is_private = is_private
        self.setDocumentMode(True)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.currentChanged.connect(self._current_tab_changed)
        
        self.download_manager = DownloadManager(self)
        
        # AdBlocker (Ad Guard)
        self.ad_blocker = AdBlockerInterceptor(self)

        # Extension Manager — loads extensions and injects content scripts
        self.extension_manager = ExtensionManager()
        
        # Standard Profile
        self.standard_profile = QWebEngineProfile.defaultProfile()
        self.standard_profile.downloadRequested.connect(self.download_manager.handle_download)
        self.standard_profile.setUrlRequestInterceptor(self.ad_blocker)
        
        # Incognito Profile (Off-the-record)
        self.incognito_profile = QWebEngineProfile("Incognito", self)
        self.incognito_profile.downloadRequested.connect(self.download_manager.handle_download)
        self.incognito_profile.setUrlRequestInterceptor(self.ad_blocker)

        # Inject extension scripts into both profiles
        self._inject_extensions()

    def _inject_extensions(self):
        """(Re-)inject all enabled extension scripts into both profiles."""
        self.extension_manager.inject_into_profile(self.standard_profile)
        self.extension_manager.inject_into_profile(self.incognito_profile)

    def add_new_tab(self, qurl: QUrl = None, label: str = "New Tab", incognito: bool = False) -> None:
        """
        Adds a new tab to the browser.
        
        Args:
            qurl: The initial URL to load.
            label: The tab title.
            incognito: Whether to use the incognito profile.
        """
        incognito = incognito or self.is_private
        try:
            browser = QWebEngineView()
            
            # Setup profile
            profile = self.incognito_profile if incognito else self.standard_profile
            page = CustomWebPage(profile, browser)
            browser.setPage(page)
            
            # Setup tab widget
            tab_widget = QWidget()
            layout = QVBoxLayout(tab_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(browser)
            
            # Set properties before adding tab to avoid AttributeError on signal fire
            tab_widget.browser = browser
            tab_widget.is_incognito = incognito
            
            # Add to TabWidget
            i = self.addTab(tab_widget, label)
            self.setCurrentIndex(i)
            
            # Connect signals
            browser.urlChanged.connect(lambda qurl, browser=browser: self._update_urlbar(qurl, browser))
            browser.loadFinished.connect(lambda _, i=i, browser=browser: self._update_title(i, browser))
            browser.loadProgress.connect(self.load_progress.emit)
            browser.iconChanged.connect(lambda _, i=i, browser=browser: self._update_icon(i, browser))
            
            # Handle Load Errors
            browser.page().loadFinished.connect(lambda ok, browser=browser: self._handle_load_finished(ok, browser))
            
            # Custom Context Menu
            browser.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            browser.customContextMenuRequested.connect(lambda pos, b=browser: self._show_context_menu(pos, b))
            
            if qurl:
                browser.setUrl(qurl)
            
        except Exception as e:
            log_exception(e)

    def close_tab(self, index: int) -> None:
        """Closes a tab by index."""
        if self.count() < 2:
            return
        self.removeTab(index)

    def close_current_tab(self) -> None:
        """Closes the currently active tab."""
        self.close_tab(self.currentIndex())

    def current_browser(self) -> QWebEngineView:
        """Returns the currently active web view."""
        widget = self.currentWidget()
        if widget and hasattr(widget, 'browser'):
            return widget.browser
        return None

    def _update_urlbar(self, q, browser: QWebEngineView = None) -> None:
        """Emits signal if the changed URL belongs to the current tab."""
        if browser == self.current_browser():
            self.url_changed.emit(q)

    def _current_tab_changed(self, i: int) -> None:
        """Handles tab switching."""
        browser = self.current_browser()
        if browser:
            qurl = browser.url()
            self._update_urlbar(qurl, browser)

    def _update_title(self, index: int, browser: QWebEngineView) -> None:
        """Updates tab title after load."""
        try:
            if index < self.count():
                title = browser.page().title()
                if not title:
                    title = "New Tab"
                # Truncate title
                if len(title) > 20:
                    title = title[:17] + "..."
                self.setTabText(index, title)
                
                # Log history if not incognito
                current_widget = self.widget(index)
                if current_widget and not current_widget.is_incognito:
                    self.main_window.history_manager.log_entry(browser.url().toString(), title)
        except Exception as e:
            log_exception(e)

    def _update_icon(self, index: int, browser: QWebEngineView) -> None:
        """Updates tab icon."""
        if index < self.count():
            self.setTabIcon(index, browser.icon())

    def _handle_load_finished(self, ok: bool, browser: QWebEngineView) -> None:
        """Handles page load completion/failure."""
        if not ok:
            url = browser.url().toString()
            # We no longer inject an error HTML here because it destroys the current page
            # when a user clicks a direct download link. Chromium provides its own error pages.
            self.main_window.status.showMessage(f"Load interrupted or failed: {url}", 5000)

    def _show_context_menu(self, pos, browser):
        """Displays a custom right-click context menu."""
        from src.ui.components.nova_context_menu import NovaContextMenu
        menu = NovaContextMenu(self.main_window)
        menu.populate_for_web_view(browser, pos)
        menu.exec(browser.mapToGlobal(pos))

