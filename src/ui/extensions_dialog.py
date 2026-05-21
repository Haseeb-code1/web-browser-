"""
Extensions Manager Dialog  —  Premium Modern UI v2
====================================================
Design: Glassmorphism dark · Indigo/Violet accents · Smooth card layout
"""
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QPushButton, QFrame, QScrollArea, QMessageBox,
    QFileDialog, QCheckBox, QSizePolicy, QGraphicsDropShadowEffect,
    QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QColor, QPalette, QLinearGradient

from src.core.extension_manager import ExtensionManager, CATALOGUE

# ── Design tokens (mirror browser_window.py palette) ─────────────────────────
_BG       = "#05000a"
_SURFACE  = "#0a0118"
_CARD     = "#12022b"
_CARD_HI  = "#1a033c"
_BORDER   = "rgba(0, 240, 255, 0.15)"
_ACCENT   = "#00f0ff"
_ACCENT2  = "#ff007f"
_TEXT     = "#ffffff"
_MUTED    = "#8e7cc3"
_GREEN    = "#00ff9d"
_RED      = "#ff003c"
_INDIGO   = "#00f0ff"

# ── Global stylesheet for the dialog ─────────────────────────────────────────
_STYLE = f"""
QDialog {{
    background: {_BG};
    font-family: "Segoe UI", "Inter", sans-serif;
    color: {_TEXT};
}}

/* ── Tab widget ── */
QTabWidget::pane {{
    border: none;
    background: {_BG};
}}
QTabBar {{
    background: transparent;
}}
QTabBar::tab {{
    background: rgba(255,255,255,0.02);
    color: {_MUTED};
    padding: 10px 22px;
    font-size: 13px;
    font-weight: 700;
    border: none;
    border-bottom: 2px solid transparent;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    color: {_ACCENT};
    border-bottom: 2px solid {_ACCENT2};
    background: rgba(255, 0, 127, 0.15);
}}
QTabBar::tab:hover:!selected {{
    color: {_TEXT};
    background: rgba(0, 240, 255, 0.08);
}}

/* ── Scroll area ── */
QScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{
    background: rgba(255,255,255,0.01);
    width: 6px; border-radius: 3px; margin: 0;
}}
QScrollBar::handle:vertical {{
    background: rgba(0, 240, 255, 0.50);
    border-radius: 3px; min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{ background: {_ACCENT2}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

/* ── Generic labels ── */
QLabel {{ color: {_TEXT}; background: transparent; }}

/* ── Generic buttons (overridden per button) ── */
QPushButton {{
    background: rgba(0, 240, 255, 0.1);
    color: {_ACCENT};
    border: 1px solid rgba(0, 240, 255, 0.5);
    border-radius: 10px;
    padding: 8px 18px;
    font-weight: 700;
    font-size: 13px;
    min-height: 32px;
    text-transform: uppercase;
    letter-spacing: 1px;
}}
QPushButton:hover {{
    background: rgba(255, 0, 127, 0.2);
    border-color: {_ACCENT2};
    color: #ffffff;
}}
QPushButton:pressed {{
    background: rgba(255, 0, 127, 0.4);
    border-color: #ffffff;
}}
QPushButton:disabled {{
    color: {_MUTED};
    background: rgba(255,255,255,0.02);
    border-color: rgba(255,255,255,0.05);
}}

QCheckBox {{
    color: {_ACCENT};
    spacing: 10px;
    font-size: 13px;
    font-weight: 700;
}}
QCheckBox::indicator {{
    width: 20px; height: 20px;
    border: 2px solid rgba(0, 240, 255, 0.6);
    border-radius: 6px;
    background: rgba(0,0,0,0.5);
}}
QCheckBox::indicator:checked {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 {_ACCENT}, stop:1 {_ACCENT2});
    border-color: #ffffff;
}}
"""

# ── Pill badge ────────────────────────────────────────────────────────────────
def _perm_badge(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(f"""
        QLabel {{
            background: rgba(0, 240, 255, 0.15);
            color: {_ACCENT};
            border: 1px solid rgba(0, 240, 255, 0.4);
            border-radius: 6px;
            padding: 2px 8px;
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
        }}
    """)
    lbl.setFixedHeight(20)
    return lbl


# ══════════════════════════════════════════════════════════════════════════════
class ExtensionCard(QFrame):
    """Premium glassmorphism card for a single extension."""

    install_requested   = pyqtSignal(str)
    uninstall_requested = pyqtSignal(str)
    toggle_requested    = pyqtSignal(str, bool)

    def __init__(self, data: dict, mode: str = "store", parent=None):
        super().__init__(parent)
        self.ext_id = data["id"]
        self.mode = mode
        self._build(data)

    def _build(self, data: dict):
        self.setObjectName("ExtCard")
        self.setStyleSheet(f"""
            QFrame#ExtCard {{
                background: {_CARD};
                border: 1px solid rgba(0, 240, 255, 0.15);
                border-radius: 14px;
            }}
            QFrame#ExtCard:hover {{
                background: {_CARD_HI};
                border: 1px solid {_ACCENT2};
                box-shadow: 0 0 15px rgba(255, 0, 127, 0.3);
            }}
        """)
        self.setMinimumHeight(100)

        root = QHBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(16)

        # ── Left: icon bubble ────────────────────────────────────────────────
        icon_frame = QFrame()
        icon_frame.setFixedSize(54, 54)
        icon_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 rgba(0, 240, 255, 0.25),
                    stop:1 rgba(255, 0, 127, 0.25));
                border: 2px solid rgba(0, 240, 255, 0.5);
                border-radius: 16px;
            }}
        """)
        icon_lbl = QLabel(data.get("icon", "🧩"), icon_frame)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 20))
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setGeometry(0, 0, 54, 54)
        root.addWidget(icon_frame)

        # ── Middle: info ──────────────────────────────────────────────────────
        info = QVBoxLayout()
        info.setSpacing(5)

        # Name + version row
        name_row = QHBoxLayout()
        name_row.setSpacing(8)
        name_lbl = QLabel(data["name"])
        name_lbl.setStyleSheet(f"color: {_TEXT}; font-size: 15px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px;")
        ver_lbl  = QLabel(f"v{data['version']}")
        ver_lbl.setStyleSheet(f"color: {_ACCENT}; font-size: 11px; font-weight: 700;")
        name_row.addWidget(name_lbl)
        name_row.addWidget(ver_lbl)
        name_row.addStretch()
        info.addLayout(name_row)

        # Description
        desc = QLabel(data.get("description", ""))
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {_MUTED}; font-size: 13px; line-height: 1.5;")
        info.addWidget(desc)

        # Permission badges
        perms = [p for p in data.get("permissions", []) if not p.startswith("http")][:5]
        if perms:
            badge_row = QHBoxLayout()
            badge_row.setSpacing(6)
            badge_row.setContentsMargins(0, 4, 0, 0)
            for p in perms:
                badge_row.addWidget(_perm_badge(p))
            badge_row.addStretch()
            info.addLayout(badge_row)

        root.addLayout(info)
        root.addStretch()

        # ── Right: actions ────────────────────────────────────────────────────
        action_col = QVBoxLayout()
        action_col.setSpacing(8)
        action_col.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        if self.mode == "store":
            installed = data.get("installed", False)
            if installed:
                btn = QPushButton("✓  Installed")
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: rgba(0, 255, 157, 0.15);
                        color: {_GREEN};
                        border: 2px solid rgba(0, 255, 157, 0.5);
                        border-radius: 10px;
                        padding: 8px 18px;
                        font-weight: 800;
                        min-width: 120px;
                    }}
                """)
                btn.setEnabled(False)
            else:
                btn = QPushButton("＋  Install")
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                            stop:0 rgba(0, 240, 255, 0.3),
                            stop:1 rgba(255, 0, 127, 0.3));
                        color: #ffffff;
                        border: 2px solid rgba(0, 240, 255, 0.6);
                        border-radius: 10px;
                        padding: 8px 18px;
                        font-weight: 800;
                        min-width: 120px;
                        letter-spacing: 1px;
                        text-transform: uppercase;
                    }}
                    QPushButton:hover {{
                        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                            stop:0 rgba(0, 240, 255, 0.5),
                            stop:1 rgba(255, 0, 127, 0.5));
                        border-color: {_ACCENT2};
                        color: #ffffff;
                    }}
                """)
                btn.clicked.connect(lambda: self.install_requested.emit(self.ext_id))
            action_col.addWidget(btn)

        elif self.mode == "installed":
            self.toggle_cb = QCheckBox("Enabled")
            self.toggle_cb.setChecked(data.get("enabled", True))
            self.toggle_cb.toggled.connect(
                lambda c: self.toggle_requested.emit(self.ext_id, c)
            )
            remove_btn = QPushButton("🗑  Remove")
            remove_btn.setStyleSheet(f"""
                QPushButton {{
                    background: rgba(255, 0, 60, 0.15);
                    color: #ff6688;
                    border: 1px solid rgba(255, 0, 60, 0.5);
                    border-radius: 8px;
                    padding: 6px 16px;
                    font-weight: 700;
                    font-size: 12px;
                    min-width: 100px;
                    letter-spacing: 0.5px;
                }}
                QPushButton:hover {{
                    background: rgba(255, 0, 60, 0.3);
                    border-color: {_RED};
                    color: #ffffff;
                }}
            """)
            remove_btn.clicked.connect(lambda: self.uninstall_requested.emit(self.ext_id))
            action_col.addWidget(self.toggle_cb)
            action_col.addWidget(remove_btn)

        root.addLayout(action_col)


# ══════════════════════════════════════════════════════════════════════════════
class ExtensionsDialog(QDialog):
    """Full-featured, premium Chrome-style Extensions Manager dialog."""

    extensions_changed = pyqtSignal()

    def __init__(self, extension_manager: ExtensionManager, parent=None):
        super().__init__(parent)
        self.mgr = extension_manager
        self.setWindowTitle("Extensions")
        self.resize(820, 620)
        self.setMinimumSize(680, 500)
        self.setStyleSheet(_STYLE)
        self._build_ui()

    # ── Layout ─────────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header bar ───────────────────────────────────────────────────────
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {_SURFACE},
                    stop:1 rgba(18,2,43,1));
                border-bottom: 2px solid rgba(0, 240, 255, 0.4);
            }}
        """)
        h = QHBoxLayout(header)
        h.setContentsMargins(24, 0, 20, 0)

        title_row = QHBoxLayout()
        title_row.setSpacing(12)
        puzzle_lbl = QLabel("🔌")
        puzzle_lbl.setFont(QFont("Segoe UI Emoji", 22))
        title_lbl = QLabel("CYBER EXTENSIONS")
        title_lbl.setStyleSheet(f"color: #ffffff; font-size: 20px; font-weight: 800; letter-spacing: 1px;")
        title_row.addWidget(puzzle_lbl)
        title_row.addWidget(title_lbl)
        h.addLayout(title_row)

        # Count badge
        self._count_badge = QLabel("")
        self._count_badge.setStyleSheet(f"""
            QLabel {{
                background: rgba(255, 0, 127, 0.25);
                color: #ffffff;
                border: 2px solid rgba(255, 0, 127, 0.6);
                border-radius: 12px;
                padding: 3px 12px;
                font-size: 12px;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
        """)
        h.addWidget(self._count_badge)
        h.addStretch()

        # Action buttons
        load_folder_btn = self._header_btn("📁  Load Unpacked")
        load_zip_btn    = self._header_btn("📦  Load .zip / .crx")
        load_folder_btn.clicked.connect(self._load_folder)
        load_zip_btn.clicked.connect(self._load_zip)
        h.addWidget(load_folder_btn)
        h.addWidget(load_zip_btn)
        root.addWidget(header)

        # ── Tab widget ────────────────────────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        root.addWidget(self.tabs)

        self.store_tab     = self._build_store_tab()
        self.installed_tab = self._build_installed_tab()
        self.tabs.addTab(self.store_tab,     "  🏪  Store  ")
        self.tabs.addTab(self.installed_tab, "  🧩  Installed  ")

        self._refresh_count_badge()

    def _header_btn(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(0, 240, 255, 0.05);
                color: {_ACCENT};
                border: 2px solid rgba(0, 240, 255, 0.3);
                border-radius: 12px;
                padding: 8px 16px;
                font-weight: 800;
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background: rgba(255, 0, 127, 0.25);
                border-color: {_ACCENT2};
                color: #ffffff;
            }}
        """)
        return btn

    # ── Store Tab ──────────────────────────────────────────────────────────────
    def _build_store_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        # Sub-header
        sub = QLabel("Curated extensions — click Install to add them to your browser.")
        sub.setStyleSheet(f"color: {_MUTED}; font-size: 12px;")
        layout.addWidget(sub)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        inner_l = QVBoxLayout(inner)
        inner_l.setSpacing(10)
        inner_l.setContentsMargins(2, 4, 6, 4)

        for entry in self.mgr.catalogue_entries():
            card = ExtensionCard(entry, mode="store")
            card.install_requested.connect(self._install_from_catalogue)
            inner_l.addWidget(card)

        inner_l.addStretch()
        scroll.setWidget(inner)
        layout.addWidget(scroll)
        return w

    # ── Installed Tab ──────────────────────────────────────────────────────────
    def _build_installed_tab(self) -> QWidget:
        self._installed_root = QWidget()
        layout = QVBoxLayout(self._installed_root)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        sub = QLabel("Toggle or remove installed extensions. Changes apply on the next page load.")
        sub.setStyleSheet(f"color: {_MUTED}; font-size: 12px;")
        layout.addWidget(sub)

        self._installed_scroll = QScrollArea()
        self._installed_scroll.setWidgetResizable(True)
        layout.addWidget(self._installed_scroll)

        self._refresh_installed_list()
        return self._installed_root

    def _refresh_installed_list(self):
        inner = QWidget()
        inner_l = QVBoxLayout(inner)
        inner_l.setSpacing(10)
        inner_l.setContentsMargins(2, 4, 6, 4)

        exts = self.mgr.extensions
        if not exts:
            # Empty state
            empty_frame = QFrame()
            empty_frame.setStyleSheet(f"""
                QFrame {{
                    background: rgba(255,255,255,0.02);
                    border: 1px dashed rgba(255,255,255,0.10);
                    border-radius: 14px;
                }}
            """)
            ef_layout = QVBoxLayout(empty_frame)
            ef_layout.setContentsMargins(30, 40, 30, 40)
            ef_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            icon_lbl = QLabel("🧩")
            icon_lbl.setFont(QFont("Segoe UI Emoji", 36))
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            head = QLabel("No extensions installed")
            head.setStyleSheet(f"color: {_TEXT}; font-size: 15px; font-weight: 700;")
            head.setAlignment(Qt.AlignmentFlag.AlignCenter)
            body = QLabel("Visit the Store tab to add your first extension.")
            body.setStyleSheet(f"color: {_MUTED}; font-size: 12px;")
            body.setAlignment(Qt.AlignmentFlag.AlignCenter)

            go_btn = QPushButton("  Browse Store  ")
            go_btn.setFixedWidth(160)
            go_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(0))

            ef_layout.addWidget(icon_lbl)
            ef_layout.addWidget(head)
            ef_layout.addWidget(body)
            ef_layout.addSpacing(12)
            ef_layout.addWidget(go_btn, alignment=Qt.AlignmentFlag.AlignCenter)

            inner_l.addWidget(empty_frame)
        else:
            for ext in exts:
                card = ExtensionCard(ext.to_dict(), mode="installed")
                card.toggle_requested.connect(self._toggle_extension)
                card.uninstall_requested.connect(self._uninstall_extension)
                inner_l.addWidget(card)

        inner_l.addStretch()
        self._installed_scroll.setWidget(inner)
        self._refresh_count_badge()

    def _refresh_count_badge(self):
        n = len(self.mgr.extensions)
        self._count_badge.setText(f"  {n} installed  ")
        # Update tab text
        if hasattr(self, 'tabs') and hasattr(self, 'installed_tab'):
            idx = self.tabs.indexOf(self.installed_tab)
            if idx >= 0:
                self.tabs.setTabText(idx, f"  🧩  Installed ({n})  " if n else "  🧩  Installed  ")

    # ── Actions ────────────────────────────────────────────────────────────────
    def _install_from_catalogue(self, ext_id: str):
        try:
            ext = self.mgr.install_from_catalogue(ext_id)
            self._notify(f"✅  '{ext.name}' installed!", success=True)
            self.extensions_changed.emit()
            # Rebuild store so Install button turns to ✓
            idx = self.tabs.indexOf(self.store_tab)
            self.store_tab = self._build_store_tab()
            self.tabs.removeTab(idx)
            self.tabs.insertTab(idx, self.store_tab, "  🏪  Store  ")
            self.tabs.setCurrentIndex(idx)
            self._refresh_installed_list()
        except Exception as e:
            self._notify(str(e), success=False)

    def _toggle_extension(self, ext_id: str, enabled: bool):
        if enabled:
            self.mgr.enable(ext_id)
        else:
            self.mgr.disable(ext_id)
        self.extensions_changed.emit()

    def _uninstall_extension(self, ext_id: str):
        ext = self.mgr.get(ext_id)
        name = ext.name if ext else ext_id
        reply = QMessageBox.question(
            self, "Remove Extension",
            f"Remove '{name}'?\n\nThis will permanently delete its files.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.mgr.uninstall(ext_id)
            self.extensions_changed.emit()
            self._refresh_installed_list()
            idx = self.tabs.indexOf(self.store_tab)
            self.store_tab = self._build_store_tab()
            self.tabs.removeTab(idx)
            self.tabs.insertTab(idx, self.store_tab, "  🏪  Store  ")

    def _load_zip(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Extension Archive", "",
            "Chrome Extension (*.zip *.crx);;All Files (*)"
        )
        if not path:
            return
        try:
            ext = self.mgr.install_from_zip(path)
            self._notify(f"✅  '{ext.name}' loaded from zip!", success=True)
            self.extensions_changed.emit()
            self._refresh_installed_list()
        except Exception as e:
            self._notify(f"Failed: {e}", success=False)

    def _load_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Unpacked Extension Folder")
        if not folder:
            return
        try:
            ext = self.mgr.install_from_folder(folder)
            self._notify(f"✅  '{ext.name}' loaded from folder!", success=True)
            self.extensions_changed.emit()
            self._refresh_installed_list()
        except Exception as e:
            self._notify(f"Failed: {e}", success=False)

    # ── Notification toast ─────────────────────────────────────────────────────
    def _notify(self, message: str, success: bool = True):
        color = _GREEN if success else _RED
        bg    = "rgba(16,185,129,0.15)" if success else "rgba(239,68,68,0.15)"
        border= "rgba(16,185,129,0.45)" if success else "rgba(239,68,68,0.45)"
        QMessageBox.information(self, "Extensions", message)
