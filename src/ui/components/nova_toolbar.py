"""
Custom Title Bar and Toolbar widgets for Nova Browser.
NovaTitleBar implements a draggable custom frame with macOS style traffic lights.
NovaToolbar implements a clean space-dark navigation bar with long-press history dropdowns,
pulsing AI glow actions, and spinning reloading arcs.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QMenu, QToolBar, QToolButton
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect, pyqtSignal, QSize
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QIcon, QMouseEvent, QAction

from src.ui.icons import ICON_BACK, ICON_FORWARD, ICON_RELOAD, ICON_STOP, ICON_HOME, ICON_UNDO, ICON_REDO, ICON_STAR_OUTLINE, ICON_STAR_FILLED, ICON_PUZZLE, ICON_AI, ICON_MORE_VERTICAL, icon_to_pixmap, icon_to_qicon
from src.ui.components.nova_address_bar import NovaAddressBar
from src.ui.theme import BACKGROUND_PRIMARY, BACKGROUND_SECONDARY, BACKGROUND_TERTIARY, BACKGROUND_ELEVATED, ACCENT_PRIMARY, ACCENT_SECONDARY, ACCENT_DANGER, ACCENT_SUCCESS, ACCENT_WARNING

class NovaTitleBar(QWidget):
    """Custom frameless draggable title bar featuring macOS styling."""
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setFixedHeight(32)
        self.drag_position = QPoint()
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)
        
        # Logo + Text
        self.logo_label = QLabel()
        self.logo_label.setPixmap(icon_to_pixmap(ICON_AI, 14, ACCENT_PRIMARY))
        self.logo_label.setFixedSize(14, 14)
        
        self.title_label = QLabel("Nova")
        self.title_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: 600;")
        
        self.badge_label = QLabel("v2.0")
        self.badge_label.setStyleSheet(f"""
            background-color: {ACCENT_PRIMARY};
            color: #FFFFFF;
            font-size: 9px;
            font-weight: bold;
            padding: 1px 6px;
            border-radius: 6px;
        """)
        
        layout.addWidget(self.logo_label)
        layout.addWidget(self.title_label)
        layout.addWidget(self.badge_label)
        layout.addStretch()
        
        # Traffic Lights Window Controls
        self.min_btn = QPushButton()
        self.min_btn.setFixedSize(12, 12)
        self.min_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.min_btn.setStyleSheet(f"background-color: {ACCENT_WARNING}; border-radius: 6px; border: none;")
        self.min_btn.clicked.connect(self.main_window.showMinimized)
        
        self.max_btn = QPushButton()
        self.max_btn.setFixedSize(12, 12)
        self.max_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.max_btn.setStyleSheet(f"background-color: {ACCENT_SUCCESS}; border-radius: 6px; border: none;")
        self.max_btn.clicked.connect(self._toggle_maximize)
        
        self.close_btn = QPushButton()
        self.close_btn.setFixedSize(12, 12)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet(f"background-color: {ACCENT_DANGER}; border-radius: 6px; border: none;")
        self.close_btn.clicked.connect(self.main_window.close)
        
        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)
        
    def _toggle_maximize(self):
        if self.main_window.isMaximized():
            self.main_window.showNormal()
        else:
            self.main_window.showMaximized()
            
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.main_window.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.main_window.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
            
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self._toggle_maximize()

class SpinningReloadButton(QPushButton):
    """Custom QPushButton with standard reload state and highly premium spinning circular arc stop loading state."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(36, 36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.is_loading = False
        self.angle = 0
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)
        
    def set_loading(self, loading: bool):
        self.is_loading = loading
        if loading:
            self.timer.start(16) # ~60fps
        else:
            self.timer.stop()
        self.update()
        
    def _on_tick(self):
        self.angle = (self.angle + 6) % 360
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Hover/Press backgrounds
        if self.isDown():
            painter.fillRect(self.rect(), QColor(BACKGROUND_ELEVATED))
        elif self.underMouse():
            painter.fillRect(self.rect(), QColor(BACKGROUND_TERTIARY))
            
        if self.is_loading:
            # Draw spinning arc
            arc_rect = QRect(10, 10, 16, 16)
            pen = QPen(QColor(ACCENT_PRIMARY), 2)
            painter.setPen(pen)
            painter.drawArc(arc_rect, self.angle * 16, 120 * 16)
            
            # Draw stop icon in center
            stop_pixmap = icon_to_pixmap(ICON_STOP, 8, ACCENT_DANGER)
            painter.drawPixmap(14, 14, stop_pixmap)
        else:
            # Draw reload icon
            reload_pixmap = icon_to_pixmap(ICON_RELOAD, 16, "#8B8FA8" if not self.underMouse() else "#E8E9F3")
            painter.drawPixmap(10, 10, reload_pixmap)
        painter.end()

class LongPressToolButton(QToolButton):
    """QToolButton executing action on click and showing history dropdown on 500ms long-press."""
    
    long_pressed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(36, 36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.press_timer = QTimer(self)
        self.press_timer.setSingleShot(True)
        self.press_timer.timeout.connect(self._on_long_press)
        self.did_long_press = False
        
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.did_long_press = False
            self.press_timer.start(500)
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event: QMouseEvent):
        self.press_timer.stop()
        if self.did_long_press:
            # Consume event, don't trigger click action
            self.setDown(False)
            return
        super().mouseReleaseEvent(event)
        
    def _on_long_press(self):
        self.did_long_press = True
        self.long_pressed.emit()

class NovaToolbar(QWidget):
    """Modern toolbar containing address bar, undo/redo buttons, page controls, extensions, and AI agent buttons."""
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setFixedHeight(52)
        self.setStyleSheet(f"background-color: {BACKGROUND_SECONDARY}; border-bottom: 1px solid rgba(255,255,255,0.06);")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(6)
        
        # 1. Back Button (Long-Press History)
        self.back_btn = LongPressToolButton()
        self.back_btn.setIcon(icon_to_qicon(ICON_BACK, 16))
        self.back_btn.setToolTip("Go back (Alt+Left)")
        self.back_btn.clicked.connect(self.main_window.navigate_back)
        self.back_btn.long_pressed.connect(self._show_back_history)
        layout.addWidget(self.back_btn)
        
        # 2. Forward Button
        self.forward_btn = LongPressToolButton()
        self.forward_btn.setIcon(icon_to_qicon(ICON_FORWARD, 16))
        self.forward_btn.setToolTip("Go forward (Alt+Right)")
        self.forward_btn.clicked.connect(self.main_window.navigate_forward)
        self.forward_btn.long_pressed.connect(self._show_forward_history)
        layout.addWidget(self.forward_btn)
        
        # 3. Reload Spinning Button
        self.reload_btn = SpinningReloadButton()
        self.reload_btn.setToolTip("Reload page (F5)")
        self.reload_btn.clicked.connect(self.main_window.navigate_reload)
        layout.addWidget(self.reload_btn)
        
        # 4. Home Button
        self.home_btn = QPushButton()
        self.home_btn.setFixedSize(36, 36)
        self.home_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.home_btn.setIcon(icon_to_qicon(ICON_HOME, 16))
        self.home_btn.setToolTip("Go to homepage")
        self.home_btn.clicked.connect(self.main_window.navigate_home)
        layout.addWidget(self.home_btn)
        
        # 5. Undo / Redo Buttons
        self.undo_btn = QPushButton()
        self.undo_btn.setFixedSize(36, 36)
        self.undo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.undo_btn.setIcon(icon_to_qicon(ICON_UNDO, 16))
        self.undo_btn.setToolTip("Undo last action (Ctrl+Z)")
        self.undo_btn.clicked.connect(self._trigger_undo)
        layout.addWidget(self.undo_btn)
        
        self.redo_btn = QPushButton()
        self.redo_btn.setFixedSize(36, 36)
        self.redo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.redo_btn.setIcon(icon_to_qicon(ICON_REDO, 16))
        self.redo_btn.setToolTip("Redo action (Ctrl+Y)")
        self.redo_btn.clicked.connect(self._trigger_redo)
        layout.addWidget(self.redo_btn)
        
        # Spacer
        self.sep = QFrame()
        self.sep.setFrameShape(QFrame.Shape.VLine)
        self.sep.setFrameShadow(QFrame.Shadow.Sunken)
        self.sep.setStyleSheet("color: rgba(255,255,255,0.08); max-height: 20px; margin: 0 4px;")
        layout.addWidget(self.sep)
        
        # 6. Center Address Bar
        self.address_bar = NovaAddressBar(self.main_window, self)
        layout.addWidget(self.address_bar, 1) # Expand center
        
        # 7. Action Buttons (Right)
        self.bookmark_btn = QPushButton()
        self.bookmark_btn.setFixedSize(36, 36)
        self.bookmark_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bookmark_btn.setIcon(icon_to_qicon(ICON_STAR_OUTLINE, 16))
        self.bookmark_btn.setToolTip("Bookmark this page")
        self.bookmark_btn.clicked.connect(self.main_window.add_bookmark)
        layout.addWidget(self.bookmark_btn)
        
        self.ext_btn = QPushButton()
        self.ext_btn.setFixedSize(36, 36)
        self.ext_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ext_btn.setIcon(icon_to_qicon(ICON_PUZZLE, 16))
        self.ext_btn.setToolTip("Extensions Manager (Ctrl+Shift+E)")
        self.ext_btn.clicked.connect(self.main_window.show_extensions_dialog)
        layout.addWidget(self.ext_btn)
        
        self.ai_btn = QPushButton()
        self.ai_btn.setFixedSize(36, 36)
        self.ai_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ai_btn.setIcon(icon_to_qicon(ICON_AI, 16))
        self.ai_btn.setToolTip("Toggle AI Panel (Ctrl+Shift+A)")
        self.ai_btn.clicked.connect(self._toggle_ai_dock)
        layout.addWidget(self.ai_btn)
        
        self.menu_btn = QPushButton()
        self.menu_btn.setFixedSize(36, 36)
        self.menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.menu_btn.setIcon(icon_to_qicon(ICON_MORE_VERTICAL, 16))
        self.menu_btn.setToolTip("Menu")
        self.menu_btn.clicked.connect(self._show_overflow_menu)
        layout.addWidget(self.menu_btn)
        
    def _trigger_undo(self):
        browser = self.main_window.tabs.current_browser()
        if browser:
            from PyQt6.QtWebEngineCore import QWebEnginePage
            browser.page().triggerAction(QWebEnginePage.WebAction.Undo)
            
    def _trigger_redo(self):
        browser = self.main_window.tabs.current_browser()
        if browser:
            from PyQt6.QtWebEngineCore import QWebEnginePage
            browser.page().triggerAction(QWebEnginePage.WebAction.Redo)
            
    def _toggle_ai_dock(self):
        dock = self.main_window.side_panel_dock
        if not dock.isVisible():
            dock.setVisible(True)
            self.main_window.side_panel_tabs.setCurrentIndex(3) # AI Assistant tab index
        else:
            if self.main_window.side_panel_tabs.currentIndex() == 3:
                dock.hide()
            else:
                self.main_window.side_panel_tabs.setCurrentIndex(3)
                
    def _show_overflow_menu(self):
        # We trigger menu display below the ⋮ button
        global_pos = self.menu_btn.mapToGlobal(QPoint(0, self.menu_btn.height()))
        self.main_window.settings_menu.exec(global_pos)
        
    def _show_back_history(self):
        browser = self.main_window.tabs.current_browser()
        if not browser:
            return
        history = browser.history()
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background: #1A1D2E; border: 1px solid rgba(255,255,255,0.06); }")
        for i in reversed(range(history.backItemsCount())):
            item = history.backItemAt(-i-1)
            act = menu.addAction(item.title())
            act.triggered.connect(lambda _, it=item: history.goToItem(it))
        menu.exec(self.back_btn.mapToGlobal(QPoint(0, self.back_btn.height())))
        
    def _show_forward_history(self):
        browser = self.main_window.tabs.current_browser()
        if not browser:
            return
        history = browser.history()
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background: #1A1D2E; border: 1px solid rgba(255,255,255,0.06); }")
        for i in range(history.forwardItemsCount()):
            item = history.forwardItemAt(i+1)
            act = menu.addAction(item.title())
            act.triggered.connect(lambda _, it=item: history.goToItem(it))
        menu.exec(self.forward_btn.mapToGlobal(QPoint(0, self.forward_btn.height())))
        
# For backward compatibility mapping
TEXT_PRIMARY = "#E8E9F3"
