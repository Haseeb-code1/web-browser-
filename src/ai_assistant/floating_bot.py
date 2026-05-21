from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox,
    QScrollArea, QPushButton, QLabel
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QThread
from src.ai_assistant.response_renderer import ResponseRenderer
from src.ai_assistant.model_router import ModelRouter
from src.ai_assistant.groq_client import GroqClient
from src.ai_assistant.ollama_client import OllamaClient
import os, json


from src.utils.paths import get_data_file_path

def _load_config() -> dict:
    """Always read fresh config from disk."""
    try:
        with open(get_data_file_path("config.json"), "r") as f:
            return json.load(f)
    except Exception:
        return {}


class WorkerThread(QThread):
    response_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, router, prompt, context):
        super().__init__()
        self.router = router
        self.prompt = prompt
        self.context = context

    def run(self):
        try:
            chunks = list(self.router.ask(self.prompt, self.context))
            self.response_ready.emit(chunks)
        except Exception as e:
            self.error_occurred.emit(str(e))


class FloatingBot(QWidget):
    command_issued = pyqtSignal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(500)
        self.hide()

        # Build router — key always re-read from config before each query
        self._build_router()
        self.renderer = ResponseRenderer()
        self.init_ui()

    def _build_router(self):
        cfg = _load_config()
        key = cfg.get("groq_api_key", "") or os.environ.get("GROQ_API_KEY", "")
        ollama_url = cfg.get("ollama_url", "http://localhost:11434")
        self.router = ModelRouter(
            GroqClient(api_key=key),
            OllamaClient(ollama_url=ollama_url)
        )
        # Apply saved default model
        default = cfg.get("default_model", "auto")
        self.router.set_model(default)
        return default

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)

        self.container = QWidget()
        self.container.setStyleSheet("""
            QWidget {
                background-color: rgba(15, 17, 27, 0.97);
                border: 1px solid #4F8EF7;
                border-radius: 16px;
            }
        """)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(6)
        self.container_layout.setContentsMargins(12, 10, 12, 10)

        # ── Header Row ──────────────────────────────────────────
        header_layout = QHBoxLayout()

        icon = QLabel("✦")
        icon.setStyleSheet("color: #4F8EF7; font-weight: bold; font-size: 16px; border: none; background: transparent;")
        icon.setFixedWidth(22)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Ask AI or give a command...")
        self.search_bar.setStyleSheet("background: transparent; color: white; border: none; font-size: 14px;")
        self.search_bar.returnPressed.connect(self.submit_query)

        self.model_combo = QComboBox()
        self.model_combo.addItems(["🔀 Auto", "⚡ Groq Llama 3", "🧠 Phi-3 Mini"])
        self.model_combo.setFixedWidth(145)
        self.model_combo.setStyleSheet(
            "background-color: rgba(79,142,247,0.15); color: white; border-radius: 6px; padding: 2px 4px;"
        )
        self.model_combo.currentTextChanged.connect(self.on_model_change)

        close_btn = QPushButton("×")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("background: transparent; color: #aaa; font-weight: bold; font-size: 18px; border: none;")
        close_btn.clicked.connect(self.close_animate)

        header_layout.addWidget(icon)
        header_layout.addWidget(self.search_bar)
        header_layout.addWidget(self.model_combo)
        header_layout.addWidget(close_btn)

        # ── Status / Thinking label ──────────────────────────────
        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet("color: #4F8EF7; font-size: 12px; background: transparent; border: none;")
        self.status_lbl.hide()

        # ── Quick Action Chips ───────────────────────────────────
        chips_layout = QHBoxLayout()
        chips_layout.setSpacing(4)
        chips = [
            ("🌐 Open", "Open "),
            ("🔍 Search", "Search for "),
            ("❌ Close Tab", "Close current tab"),
            ("📋 Links", "Get all links on this page"),
            ("📄 Summarize", "Summarize this page"),
        ]
        for text, prompt in chips:
            btn = QPushButton(text)
            btn.setStyleSheet(
                "background-color: rgba(79,142,247,0.15); color: #4F8EF7; "
                "border-radius: 10px; padding: 3px 8px; font-size: 11px; border: none;"
            )
            btn.clicked.connect(lambda checked, p=prompt: self.set_query(p))
            chips_layout.addWidget(btn)

        # ── Response Area ────────────────────────────────────────
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMaximumHeight(400)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")

        self.response_content = QWidget()
        self.response_layout = QVBoxLayout(self.response_content)
        self.response_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.response_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setWidget(self.response_content)
        self.scroll_area.hide()

        self.container_layout.addLayout(header_layout)
        self.container_layout.addWidget(self.status_lbl)
        self.container_layout.addLayout(chips_layout)
        self.container_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.container)

        # ── Opacity Animation ────────────────────────────────────
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(150)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Sync combo to saved default
        self._sync_combo_to_model()

    def _sync_combo_to_model(self):
        model = self.router.selected_model
        mapping = {"auto": "🔀 Auto", "groq": "⚡ Groq Llama 3", "phi3": "🧠 Phi-3 Mini"}
        label = mapping.get(model, "🔀 Auto")
        self.model_combo.blockSignals(True)
        self.model_combo.setCurrentText(label)
        self.model_combo.blockSignals(False)

    def on_model_change(self, text):
        if "Groq" in text:
            self.router.set_model("groq")
        elif "Phi-3" in text:
            self.router.set_model("phi3")
        else:
            self.router.set_model("auto")

    def open_animate(self, selected_text=""):
        # Always re-read config so a freshly saved key is picked up
        saved_default = self._build_router()
        self._sync_combo_to_model()

        if self.parent():
            pr = self.parent().geometry()
            self.move(pr.x() + (pr.width() - self.width()) // 2, pr.y() + 80)

        # Prevent immediate close if opened while previously closing
        try:
            self.anim.finished.disconnect()
        except TypeError:
            pass

        self.setWindowOpacity(0.0)
        self.show()
        if selected_text:
            self.set_query(selected_text)
        self.search_bar.setFocus()
        self.anim.setStartValue(self.windowOpacity())
        self.anim.setEndValue(1.0)
        self.anim.start()

    def close_animate(self):
        self.anim.setStartValue(self.windowOpacity())
        self.anim.setEndValue(0.0)
        try:
            self.anim.finished.disconnect()
        except TypeError:
            pass
        self.anim.finished.connect(self.hide)
        self.anim.start()

    # Allow dragging of the floating window
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, '_drag_pos'):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def set_query(self, text):
        if not self.isVisible():
            self.open_animate()
        self.search_bar.setText(text)
        self.search_bar.selectAll()
        self.search_bar.setFocus()

    def _clear_response(self):
        for i in reversed(range(self.response_layout.count())):
            w = self.response_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

    def submit_query(self):
        query = self.search_bar.text().strip()
        if not query:
            return

        self._clear_response()
        self.scroll_area.show()
        self.status_lbl.setText("⏳ Thinking...")
        self.status_lbl.show()

        context = ""
        if self.parent() and hasattr(self.parent(), "browser_controller"):
            ctx = self.parent().browser_controller.get_page_context()
            context = f"URL: {ctx['url']}\nTitle: {ctx['title']}\n"

        # Re-read key from config each time so a hot-saved key always works
        cfg = _load_config()
        fresh_key = cfg.get("groq_api_key", "").strip()
        if fresh_key:
            self.router.groq_client.api_key = fresh_key

        self.worker = WorkerThread(self.router, query, context)
        self.worker.response_ready.connect(self.render_response)
        self.worker.error_occurred.connect(self.show_error)
        self.worker.start()

    def show_error(self, msg):
        self.status_lbl.hide()
        err_lbl = QLabel(f"⚠️ Error: {msg}")
        err_lbl.setStyleSheet("color: #ff6b6b; font-size: 13px; background: transparent; border: none;")
        err_lbl.setWordWrap(True)
        self.response_layout.addWidget(err_lbl)

    def render_response(self, chunks):
        self.status_lbl.hide()
        full_text = "".join(chunks).strip() if chunks else ""

        if not full_text:
            self.show_error("No response received. Check your API key in Settings → 🤖 AI Settings.")
            return

        rendered = self.renderer.render(full_text)
        self.response_layout.addWidget(rendered)

        # Execute any embedded action tags
        if self.parent() and hasattr(self.parent(), "browser_controller"):
            bc = self.parent().browser_controller
            bc.execute_ai_tags(full_text)
