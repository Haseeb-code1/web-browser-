"""
Custom SVG Cursors for Nova Browser.
Loads stroke-drawn modern vectors and generates QCursor definitions.
"""

from PyQt6.QtGui import QCursor, QPixmap, QPainter
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtSvg import QSvgRenderer

def _svg_to_cursor(svg_string: str, size: int, hot_x: int, hot_y: int) -> QCursor:
    """Helper converting raw SVG vector content to standard QCursor instance."""
    renderer = QSvgRenderer(svg_string.encode('utf-8'))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    
    return QCursor(pixmap, hot_x, hot_y)

# 1. Sleek dark arrow pointer with white borders and glowing violet accent
ARROW_SVG = """<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M4 2v22.5l6.5-6.5h9.5L4 2z" fill="#0D0F1A" stroke="#E8E9F3" stroke-width="1.5" stroke-linejoin="miter"/>
  <circle cx="4" cy="2" r="3" fill="#6C63FF"/>
</svg>"""

# 2. Sleek pointing hand pointer with electric cyan fingertip dot
POINTER_SVG = """<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M14 12V4a2 2 0 1 1 4 0v8h2.5V8.5a1.5 1.5 0 0 1 3 0V12h2v4a8 8 0 0 1-16 0v-4h2.5v2" fill="#0D0F1A" stroke="#E8E9F3" stroke-width="1.5" stroke-linejoin="round"/>
  <circle cx="16" cy="2" r="2.5" fill="#00D4FF"/>
</svg>"""

# 3. Violet thin I-beam text insertion cursor
IBEAM_SVG = """<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
  <line x1="16" y1="6" x2="16" y2="26" stroke="#6C63FF" stroke-width="2" stroke-linecap="round"/>
  <line x1="10" y1="6" x2="22" y2="6" stroke="#E8E9F3" stroke-width="1.5" stroke-linecap="round"/>
  <line x1="10" y1="26" x2="22" y2="26" stroke="#E8E9F3" stroke-width="1.5" stroke-linecap="round"/>
</svg>"""

# 4. Electric cyan circular rotating loading wait indicator
WAIT_SVG = """<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="16" cy="16" r="8" stroke="rgba(255,255,255,0.1)" stroke-width="2.5"/>
  <path d="M16 8a8 8 0 0 1 8 8" stroke="#00D4FF" stroke-width="2.5" stroke-linecap="round"/>
</svg>"""

def get_arrow_cursor() -> QCursor:
    return _svg_to_cursor(ARROW_SVG, 32, 4, 2)

def get_pointer_cursor() -> QCursor:
    return _svg_to_cursor(POINTER_SVG, 32, 16, 2)

def get_ibeam_cursor() -> QCursor:
    return _svg_to_cursor(IBEAM_SVG, 32, 16, 16)

def get_wait_cursor() -> QCursor:
    return _svg_to_cursor(WAIT_SVG, 32, 16, 16)
