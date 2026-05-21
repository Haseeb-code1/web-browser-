import re
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer

class ResponseRenderer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        self.current_label = None

    def render(self, text: str) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        lines = text.split('\n')
        in_code_block = False
        code_text = []

        for line in lines:
            if line.startswith("```"):
                if in_code_block:
                    in_code_block = False
                    lbl = QLabel("\n".join(code_text))
                    lbl.setStyleSheet("background-color: #1a1a2e; color: #00f0ff; padding: 10px; border-radius: 5px; font-family: monospace;")
                    lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                    lbl.setWordWrap(True)
                    layout.addWidget(lbl)
                    code_text = []
                else:
                    in_code_block = True
                    code_text = []
                continue

            if in_code_block:
                code_text.append(line)
                continue

            if line.startswith("#"):
                lbl = QLabel(line.lstrip("#").strip())
                lbl.setStyleSheet("font-weight: bold; font-size: 16px; color: #4F8EF7;")
                lbl.setWordWrap(True)
                layout.addWidget(lbl)
            elif line.startswith("-") or line.startswith("*"):
                lbl = QLabel(f"• {line.lstrip('-*').strip()}")
                lbl.setStyleSheet("color: white; font-size: 13px;")
                lbl.setWordWrap(True)
                layout.addWidget(lbl)
            else:
                # Basic markdown bold
                formatted = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
                # URLs
                urls = re.findall(r'(https?://[^\s]+)', formatted)
                for url in urls:
                    formatted = formatted.replace(url, f'<a href="{url}" style="color: #4F8EF7;">{url}</a>')
                
                if formatted.strip():
                    lbl = QLabel(formatted)
                    lbl.setStyleSheet("color: white; font-size: 13px;")
                    lbl.setWordWrap(True)
                    lbl.setOpenExternalLinks(True)
                    layout.addWidget(lbl)

        # Action links at the bottom
        all_urls = re.findall(r'(https?://[^\s)\]]+)', text)
        if all_urls:
            for url in set(all_urls):
                clean_url = url.strip(".,)'\"")
                link_lbl = QLabel(f'┌─────────────────────────────┐\n│ 🔗 Link\n│    <a href="{clean_url}" style="color: #4F8EF7;">{clean_url}</a>\n└─────────────────────────────┘')
                link_lbl.setStyleSheet("color: #e0f2fe; font-family: monospace;")
                link_lbl.setOpenExternalLinks(True)
                layout.addWidget(link_lbl)

        return container

    def stream_render(self, container: QWidget, layout: QVBoxLayout, word_generator):
        # A simple timer-based word-by-word streaming effect on a single label
        # In a real app, this should parse markdown on the fly, but for simplicity
        # we append text to a QLabel.
        
        self.stream_label = QLabel()
        self.stream_label.setStyleSheet("color: white; font-size: 13px;")
        self.stream_label.setWordWrap(True)
        layout.addWidget(self.stream_label)
        
        self.full_text = ""
        self.word_queue = []
        
        # Load words from generator
        for chunk in word_generator:
            self.word_queue.extend(chunk.split(" "))
            
        self.timer = QTimer(self)
        def append_word():
            if self.word_queue:
                word = self.word_queue.pop(0)
                self.full_text += word + " "
                self.stream_label.setText(self.full_text)
            else:
                self.timer.stop()
                
        self.timer.timeout.connect(append_word)
        self.timer.start(30)
