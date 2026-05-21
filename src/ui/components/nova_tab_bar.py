"""
Custom QTabBar subclass for Nova Browser.
Implements custom paintEvent for glassmorphism active/inactive tabs,
tab close hover areas, and context menu support.
"""

from PyQt6.QtWidgets import QTabBar, QMenu, QWidget
from PyQt6.QtCore import Qt, QSize, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QPen, QBrush, QFont, QMouseEvent

class NovaTabBar(QTabBar):
    """Custom painted QTabBar with deep space aesthetic and micro-interactions."""
    
    tab_close_clicked = pyqtSignal(int)
    new_tab_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.hovered_index = -1
        self.setDrawBase(False)
        self.setMovable(True)
        
    def tabSizeHint(self, index: int) -> QSize:
        """Dynamically compute tab sizes with compression."""
        count = self.count() or 1
        parent_width = self.parentWidget().width() if self.parentWidget() else 800
        
        # Deduct space for new tab button
        available_width = parent_width - 120
        calculated_width = available_width // count
        
        width = max(120, min(220, calculated_width))
        return QSize(width, 38)
        
    def minimumTabSizeHint(self, index: int) -> QSize:
        return QSize(100, 38)
        
    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.position().toPoint()
        hovered = -1
        for i in range(self.count()):
            if self.tabRect(i).contains(pos):
                hovered = i
                break
        if hovered != self.hovered_index:
            self.hovered_index = hovered
            self.update()
        super().mouseMoveEvent(event)
        
    def leaveEvent(self, event):
        self.hovered_index = -1
        self.update()
        super().leaveEvent(event)
        
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            for i in range(self.count()):
                tab_rect = self.tabRect(i)
                if tab_rect.contains(pos):
                    # Check if close button is clicked (rightmost 24px of the tab)
                    close_btn_rect = QRect(tab_rect.right() - 24, tab_rect.top(), 24, tab_rect.height())
                    if close_btn_rect.contains(pos):
                        self.tab_close_clicked.emit(i)
                        return
                    break
        elif event.button() == Qt.MouseButton.RightButton:
            pos = event.position().toPoint()
            for i in range(self.count()):
                if self.tabRect(i).contains(pos):
                    self.setCurrentIndex(i)
                    self._show_tab_context_menu(event.globalPosition().toPoint(), i)
                    return
            # Clicked empty area
            self._show_tab_context_menu(event.globalPosition().toPoint(), -1)
            return
            
        super().mousePressEvent(event)
        
    def paintEvent(self, event):
        """Manually paint every pixel of each tab."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Base background fill
        painter.fillRect(self.rect(), QColor("#0D0F1A")) # BACKGROUND_PRIMARY
        
        for i in range(self.count()):
            tab_rect = self.tabRect(i)
            is_active = (i == self.currentIndex())
            is_hover = (i == self.hovered_index)
            
            # --- 1. Background Fill ---
            if is_active:
                painter.fillRect(tab_rect, QColor("#1F2235")) # BACKGROUND_ELEVATED
                
                # Top accent gradient line
                gradient = QLinearGradient(tab_rect.topLeft(), tab_rect.topRight())
                gradient.setColorAt(0.0, QColor("#6C63FF")) # ACCENT_PRIMARY
                gradient.setColorAt(1.0, QColor("#00D4FF")) # ACCENT_SECONDARY
                pen = QPen(QBrush(gradient), 2)
                painter.setPen(pen)
                painter.drawLine(tab_rect.topLeft(), tab_rect.topRight())
            elif is_hover:
                painter.fillRect(tab_rect, QColor("#1A1D2E")) # BACKGROUND_TERTIARY
            else:
                # Subtly border tab right to separate them
                painter.setPen(QColor("rgba(255,255,255,0.03)"))
                painter.drawLine(tab_rect.topRight() - QPoint(0, 4), tab_rect.bottomRight() - QPoint(0, 4))
                
            # --- 2. Icon (Favicon) ---
            icon = self.tabIcon(i)
            icon_rect = QRect(tab_rect.left() + 10, tab_rect.top() + (tab_rect.height() - 16) // 2, 16, 16)
            if not icon.isNull():
                icon.paint(painter, icon_rect)
            else:
                # Default globe icon
                from src.ui.icons import ICON_GLOBE, icon_to_pixmap
                globe_pixmap = icon_to_pixmap(ICON_GLOBE, 16, "#8B8FA8")
                painter.drawPixmap(icon_rect.topLeft(), globe_pixmap)
                
            # --- 3. Label Text ---
            text = self.tabText(i)
            font = QFont("Segoe UI Variable", 10)
            font.setWeight(QFont.Weight.Medium if is_active else QFont.Weight.Normal)
            painter.setFont(font)
            
            text_color = QColor("#E8E9F3") if is_active else QColor("#8B8FA8")
            painter.setPen(text_color)
            
            # Available text width
            close_width = 24 if (is_active or is_hover) else 0
            avail_w = tab_rect.width() - 10 - 16 - 8 - close_width - 8
            metrics = painter.fontMetrics()
            elided_text = metrics.elidedText(text, Qt.TextElideMode.ElideRight, avail_w)
            
            text_rect = QRect(icon_rect.right() + 8, tab_rect.top(), avail_w, tab_rect.height())
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, elided_text)
            
            # --- 4. Close Button (×) ---
            if is_active or is_hover:
                close_rect = QRect(tab_rect.right() - 20, tab_rect.top() + (tab_rect.height() - 16) // 2, 16, 16)
                painter.setPen(QColor("#FF4757") if is_hover and self.underMouse() and QRect(tab_rect.right() - 24, tab_rect.top(), 24, tab_rect.height()).contains(self.mapFromGlobal(self.cursor().pos())) else QColor("#8B8FA8"))
                
                close_font = QFont("Segoe UI Variable", 11)
                close_font.setBold(True)
                painter.setFont(close_font)
                painter.drawText(close_rect, Qt.AlignmentFlag.AlignCenter, "×")
                
        painter.end()

    def _show_tab_context_menu(self, global_pos: QPoint, tab_index: int):
        """Displays custom context menu for tab operations."""
        menu = QMenu(self)
        # Custom stylesheet applied to this specific popup QMenu
        menu.setStyleSheet("""
            QMenu {
                background-color: #1A1D2E;
                border: 1px solid rgba(108, 99, 255, 0.3);
                border-radius: 10px;
                padding: 4px;
            }
            QMenu::item {
                background-color: transparent;
                border-radius: 6px;
                padding: 6px 20px;
                font-size: 13px;
                color: #E8E9F3;
            }
            QMenu::item:selected {
                background-color: #1F2235;
                color: #6C63FF;
            }
            QMenu::separator {
                height: 1px;
                background: rgba(255,255,255,0.06);
                margin: 4px 8px;
            }
        """)
        
        tab_manager = self.parentWidget()
        
        if tab_index >= 0:
            reload_act = menu.addAction("Reload Tab")
            reload_act.triggered.connect(lambda: tab_manager.widget(tab_index).browser.reload())
            
            dup_act = menu.addAction("Duplicate Tab")
            dup_act.triggered.connect(lambda: tab_manager.add_new_tab(tab_manager.widget(tab_index).browser.url()))
            
            menu.addSeparator()
            
            close_act = menu.addAction("Close Tab")
            close_act.triggered.connect(lambda: tab_manager.close_tab(tab_index))
            
            close_others_act = menu.addAction("Close Other Tabs")
            def _close_others():
                for idx in reversed(range(tab_manager.count())):
                    if idx != tab_index:
                        tab_manager.close_tab(idx)
            close_others_act.triggered.connect(_close_others)
            
            menu.addSeparator()
            
        new_tab_act = menu.addAction("New Tab")
        new_tab_act.triggered.connect(self.new_tab_requested.emit)
        
        menu.exec(global_pos)
