import sys
import random
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QProgressBar, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, pyqtSignal, QEasingCurve

class SplashScreen(QWidget):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(600, 400)

        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Background Container for styling
        self.container = QWidget(self)
        self.container.setFixedSize(600, 400)
        self.container.setStyleSheet("""
            QWidget {
                background-color: rgba(11, 15, 25, 0.95);
                border: 2px solid #00f0ff;
                border-radius: 20px;
            }
        """)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.setSpacing(20)

        # Title Label
        self.title_label = QLabel("NEURAL BROWSER")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #00f0ff;
                font-size: 48px;
                font-weight: bold;
                font-family: 'Consolas', 'Courier New', monospace;
                letter-spacing: 5px;
                background: transparent;
                border: none;
            }
        """)
        
        # Subtitle
        self.subtitle_label = QLabel("V 2.0 Agentic Edition")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setStyleSheet("""
            QLabel {
                color: #b026ff;
                font-size: 18px;
                font-family: 'Consolas', 'Courier New', monospace;
                background: transparent;
                border: none;
            }
        """)

        # Loading Text
        self.loading_text = QLabel("Initializing Core Systems...")
        self.loading_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_text.setStyleSheet("""
            QLabel {
                color: #e0f2fe;
                font-size: 14px;
                font-family: 'Consolas', 'Courier New', monospace;
                background: transparent;
                border: none;
                margin-top: 20px;
            }
        """)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedSize(400, 10)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 5px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #b026ff, stop:1 #00f0ff);
                border-radius: 5px;
            }
        """)

        container_layout.addStretch()
        container_layout.addWidget(self.title_label)
        container_layout.addWidget(self.subtitle_label)
        container_layout.addWidget(self.loading_text)
        container_layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)
        container_layout.addStretch()

        self.layout.addWidget(self.container)

        # Opacity Effect for Fade In
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)

        # Fade In Animation
        self.fade_in_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_anim.setDuration(1000)
        self.fade_in_anim.setStartValue(0.0)
        self.fade_in_anim.setEndValue(1.0)
        self.fade_in_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Pulse Animation for Subtitle
        self.pulse_effect = QGraphicsOpacityEffect(self.subtitle_label)
        self.subtitle_label.setGraphicsEffect(self.pulse_effect)
        self.pulse_anim = QPropertyAnimation(self.pulse_effect, b"opacity")
        self.pulse_anim.setDuration(800)
        self.pulse_anim.setStartValue(0.4)
        self.pulse_anim.setEndValue(1.0)
        self.pulse_anim.setLoopCount(-1) # Infinite loop
        self.pulse_anim.setEasingCurve(QEasingCurve.Type.InOutSine)

        # Fake Loading State
        self.loading_messages = [
            "Booting Quantum Kernel...",
            "Loading Neural Engine...",
            "Connecting to Matrix...",
            "Bypassing Security Protocols...",
            "Establishing Secure Connection...",
            "Initializing UI Elements...",
            "Ready."
        ]
        self.progress = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)

    def start_animation(self):
        self.fade_in_anim.start()
        self.pulse_anim.start()
        self.timer.start(40) # Update every 40ms (total ~3-4 seconds)

    def update_progress(self):
        self.progress += random.randint(1, 3)
        if self.progress >= 100:
            self.progress = 100
            self.timer.stop()
            self.loading_text.setText("Ready.")
            self.progress_bar.setValue(self.progress)
            
            # Start Fade Out
            self.fade_out_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
            self.fade_out_anim.setDuration(800)
            self.fade_out_anim.setStartValue(1.0)
            self.fade_out_anim.setEndValue(0.0)
            self.fade_out_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.fade_out_anim.finished.connect(self.finish_loading)
            self.fade_out_anim.start()
        else:
            self.progress_bar.setValue(self.progress)
            
            # Change message based on progress
            idx = int((self.progress / 100) * (len(self.loading_messages) - 1))
            self.loading_text.setText(self.loading_messages[idx])

    def finish_loading(self):
        self.finished.emit()
        self.close()
