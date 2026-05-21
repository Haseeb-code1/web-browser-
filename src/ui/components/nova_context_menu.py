"""
Custom styled Context Menu for Nova Browser.
Replaces the standard QMenu with a space-dark rounded, animated context menu.
"""

from PyQt6.QtWidgets import QMenu
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QAction

from src.ui.icons import ICON_BACK, ICON_FORWARD, ICON_RELOAD, ICON_COPY, ICON_AI, icon_to_qicon
from src.ui.animations import fade_in

class NovaContextMenu(QMenu):
    """Custom painted context menu featuring smooth fade-in transitions and styling."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("NovaContextMenu")
        self.setStyleSheet("""
            QMenu#NovaContextMenu {
                background-color: #1A1D2E;
                border: 1px solid rgba(108, 99, 255, 0.3);
                border-radius: 12px;
                padding: 6px;
            }
            QMenu#NovaContextMenu::item {
                background-color: transparent;
                border-radius: 8px;
                padding: 8px 28px;
                color: #E8E9F3;
                font-size: 13px;
                min-width: 150px;
            }
            QMenu#NovaContextMenu::item:selected {
                background-color: #1F2235;
                color: #E8E9F3;
            }
            QMenu#NovaContextMenu::item:disabled {
                color: #555870;
            }
            QMenu#NovaContextMenu::separator {
                height: 1px;
                background: rgba(255,255,255,0.06);
                margin: 4px 8px;
            }
        """)
        
    def showEvent(self, event):
        """Execute smooth micro-opacity fade-in when popup appears."""
        fade_in(self, 120)
        super().showEvent(event)
        
    def populate_for_web_view(self, browser, pos: QPoint):
        """Add standard back, forward, reload, copy, and AI actions based on page contents."""
        self.clear()
        
        has_selection = browser.hasSelection()
        
        if has_selection:
            # Selection menu
            copy_act = self.addAction(icon_to_qicon(ICON_COPY, 14), "Copy")
            from PyQt6.QtWebEngineCore import QWebEnginePage
            copy_act.triggered.connect(lambda: browser.page().triggerAction(QWebEnginePage.WebAction.Copy))
            copy_act.setShortcut("Ctrl+C")
            
            self.addSeparator()
            
            ai_act = self.addAction(icon_to_qicon(ICON_AI, 14), "Ask AI about this text")
            # Trigger floating AI bot with selection
            ai_act.triggered.connect(lambda: self.parentWidget().toggle_floating_bot())
        else:
            # Page default menu
            back_act = self.addAction(icon_to_qicon(ICON_BACK, 14), "Back")
            back_act.setEnabled(browser.history().canGoBack())
            back_act.triggered.connect(browser.back)
            back_act.setShortcut("Alt+Left")
            
            fwd_act = self.addAction(icon_to_qicon(ICON_FORWARD, 14), "Forward")
            fwd_act.setEnabled(browser.history().canGoForward())
            fwd_act.triggered.connect(browser.forward)
            fwd_act.setShortcut("Alt+Right")
            
            reload_act = self.addAction(icon_to_qicon(ICON_RELOAD, 14), "Reload")
            reload_act.triggered.connect(browser.reload)
            reload_act.setShortcut("F5")
            
            self.addSeparator()
            
            source_act = self.addAction("View Page Source")
            # We can connect this to viewing source
            def _view_source():
                url = browser.url().toString()
                self.parentWidget().tabs.add_new_tab(url="view-source:" + url)
            source_act.triggered.connect(_view_source)
            source_act.setShortcut("Ctrl+U")
            
            self.addSeparator()
            
            ai_page_act = self.addAction(icon_to_qicon(ICON_AI, 14), "Summarize this page with AI")
            ai_page_act.triggered.connect(lambda: self.parentWidget().ai_summarize_current_page())
