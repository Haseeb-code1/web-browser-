"""
Smooth UI micro-animations and transition helpers using QPropertyAnimation.
Designed to run on the GUI thread without blocking browser execution.
"""

from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QRect, QObject, pyqtProperty
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QWidget

def fade_in(widget: QWidget, duration: int = 150) -> QPropertyAnimation:
    """Fade widget opacity from 0.0 to 1.0."""
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    
    anim = QPropertyAnimation(effect, b"opacity")
    anim.setDuration(duration)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.start(QPropertyAnimation.DeletionPolicy.KeepWhenStopped)
    return anim

def slide_in_from_bottom(widget: QWidget, distance: int = 20, duration: int = 180) -> QPropertyAnimation:
    """Slide widget up from a offset below its final position."""
    start_pos = widget.pos() + QPoint(0, distance)
    end_pos = widget.pos()
    
    anim = QPropertyAnimation(widget, b"pos")
    anim.setDuration(duration)
    anim.setStartValue(start_pos)
    anim.setEndValue(end_pos)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.start(QPropertyAnimation.DeletionPolicy.KeepWhenStopped)
    return anim

def scale_bounce(widget: QWidget, duration: int = 200) -> QPropertyAnimation:
    """Quick visual bounce scale effect (e.g. on bookmark confirmation)."""
    geom = widget.geometry()
    center = geom.center()
    w, h = geom.width(), geom.height()
    
    anim = QPropertyAnimation(widget, b"geometry")
    anim.setDuration(duration)
    anim.setStartValue(geom)
    anim.setKeyValueAt(0.5, QRect(center.x() - int(w*1.08/2), center.y() - int(h*1.08/2), int(w*1.08), int(h*1.08)))
    anim.setEndValue(geom)
    anim.setEasingCurve(QEasingCurve.Type.OutBack)
    anim.start(QPropertyAnimation.DeletionPolicy.KeepWhenStopped)
    return anim

def width_slide(widget: QWidget, start_w: int, end_w: int, duration: int = 200) -> QPropertyAnimation:
    """Animate maximumWidth property (essential for sidebar collapse/expand)."""
    anim = QPropertyAnimation(widget, b"maximumWidth")
    anim.setDuration(duration)
    anim.setStartValue(start_w)
    anim.setEndValue(end_w)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.start(QPropertyAnimation.DeletionPolicy.KeepWhenStopped)
    return anim
