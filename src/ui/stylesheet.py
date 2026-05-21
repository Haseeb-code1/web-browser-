"""
Global QSS Stylesheet for the Nova Browser.
Defines clean space-dark themes, modern typography, glassmorphism scrollbars,
rounded cards, and sleek input fields.
"""

NOVA_STYLESHEET = """
/* === GLOBAL === */
* {
    font-family: "Segoe UI Variable", "Inter", "SF Pro Display", system-ui;
    color: #E8E9F3;
    selection-background-color: #6C63FF;
    selection-color: #FFFFFF;
}

QMainWindow {
    background-color: #0D0F1A;
}

QWidget {
    background-color: transparent;
}

/* === SCROLLBARS === */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(108, 99, 255, 0.5);
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background: transparent;
    height: 6px;
}
QScrollBar::handle:horizontal {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 3px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover {
    background: rgba(108, 99, 255, 0.5);
}

/* === TOOLTIPS === */
QToolTip {
    background-color: #1F2235;
    color: #E8E9F3;
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}

/* === PUSH BUTTONS === */
QPushButton {
    background-color: transparent;
    border: none;
    border-radius: 8px;
    padding: 6px 12px;
    color: #8B8FA8;
    font-size: 13px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #1A1D2E;
    color: #E8E9F3;
}
QPushButton:pressed {
    background-color: #1F2235;
}
QPushButton[accent="true"] {
    background-color: #6C63FF;
    color: #FFFFFF;
    border-radius: 8px;
    padding: 8px 16px;
}
QPushButton[accent="true"]:hover {
    background-color: #7B73FF;
}

/* === LINE EDIT (inputs) === */
QLineEdit {
    background-color: #1A1D2E;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 999px;
    padding: 6px 14px;
    color: #E8E9F3;
    font-size: 14px;
    selection-background-color: #6C63FF;
}
QLineEdit:focus {
    border: 1px solid #6C63FF;
    background-color: #1F2235;
}
QLineEdit::placeholder {
    color: #555870;
}

/* === COMBO BOX === */
QComboBox {
    background-color: #1A1D2E;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 6px 12px;
    color: #E8E9F3;
    font-size: 13px;
}
QComboBox:hover {
    border-color: rgba(255,255,255,0.15);
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox::down-arrow {
    image: none;
    width: 0;
}
QComboBox QAbstractItemView {
    background-color: #1A1D2E;
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 10px;
    padding: 4px;
    selection-background-color: #1F2235;
    outline: none;
}

/* === MENU (QMenu) === */
QMenu {
    background-color: #1A1D2E;
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 12px;
    padding: 6px;
}
QMenu::item {
    background-color: transparent;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    color: #E8E9F3;
}
QMenu::item:selected {
    background-color: #1F2235;
}
QMenu::item:disabled {
    color: #555870;
}
QMenu::separator {
    height: 1px;
    background: rgba(255,255,255,0.06);
    margin: 4px 8px;
}

/* === DIALOG === */
QDialog {
    background-color: #13151F;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
}

/* === TAB WIDGET (settings only, not browser tabs) === */
QTabWidget::pane {
    background-color: #13151F;
    border: none;
}
QTabBar::tab {
    background-color: transparent;
    padding: 8px 16px;
    color: #8B8FA8;
    font-size: 13px;
    font-weight: 500;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:selected {
    color: #6C63FF;
    border-bottom: 2px solid #6C63FF;
}
QTabBar::tab:hover {
    color: #E8E9F3;
}

/* === SLIDER === */
QSlider::groove:horizontal {
    background: rgba(255,255,255,0.10);
    height: 4px;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #6C63FF;
    width: 14px;
    height: 14px;
    border-radius: 7px;
    margin-top: -5px;
}
QSlider::sub-page:horizontal {
    background: #6C63FF;
    border-radius: 2px;
}

/* === PROGRESS BAR === */
QProgressBar {
    background: rgba(255,255,255,0.08);
    border: none;
    border-radius: 2px;
    height: 2px;
}
QProgressBar::chunk {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #6C63FF, stop:1 #00D4FF
    );
    border-radius: 2px;
}

/* === SPLITTER === */
QSplitter::handle {
    background: rgba(255,255,255,0.06);
    width: 1px;
}

/* === TREE/LIST WIDGET === */
QListWidget, QTreeWidget {
    background-color: transparent;
    border: none;
    outline: none;
}
QListWidget::item, QTreeWidget::item {
    padding: 8px 12px;
    border-radius: 8px;
    color: #E8E9F3;
}
QListWidget::item:hover, QTreeWidget::item:hover {
    background-color: #1A1D2E;
}
QListWidget::item:selected, QTreeWidget::item:selected {
    background-color: #1F2235;
    color: #6C63FF;
}

/* === CHECK BOX === */
QCheckBox {
    color: #E8E9F3;
    font-size: 13px;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1.5px solid rgba(255,255,255,0.20);
    background: transparent;
}
QCheckBox::indicator:checked {
    background: #6C63FF;
    border-color: #6C63FF;
}

/* === SPIN BOX === */
QSpinBox {
    background: #1A1D2E;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 6px 10px;
    color: #E8E9F3;
    font-size: 13px;
}
QSpinBox::up-button, QSpinBox::down-button {
    background: transparent;
    border: none;
    width: 18px;
}
"""
