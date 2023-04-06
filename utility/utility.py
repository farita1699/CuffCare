from PyQt5.QtCore import QPropertyAnimation, QObject, pyqtProperty, QEasingCurve
from PyQt5.QtGui import QColor

class BlinkingLabelHelper(QObject):
    def __init__(self, label):
        super().__init__(label)
        self._label = label
        self._color = QColor(255, 255, 255)

    @pyqtProperty(QColor)
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self._label.setStyleSheet(f"color: rgba({value.red()}, {value.green()}, {value.blue()}, {value.alpha()})")

def startBlinkingAnimation(label):
    helper = BlinkingLabelHelper(label)
    
    start_color = QColor(255, 255, 255, 255)  # Start value (fully visible text)
    end_color = QColor(255, 255, 255, 50)  # End value (low-opacity text)

    fade_out = QPropertyAnimation(helper, b"color")
    fade_out.setDuration(1500)  # Animation duration in milliseconds
    fade_out.setStartValue(start_color)
    fade_out.setEndValue(end_color)
    fade_out.setEasingCurve(QEasingCurve.OutSine) 

    fade_in = QPropertyAnimation(helper, b"color")
    fade_in.setDuration(1500)  # Animation duration in milliseconds
    fade_in.setStartValue(end_color)
    fade_in.setEndValue(start_color)
    fade_in.setEasingCurve(QEasingCurve.InSine) 

    # Connect the animations
    fade_out.finished.connect(fade_in.start)
    fade_in.finished.connect(fade_out.start)

    fade_out.start()
    
    # Store the animation and helper objects as attributes of the label
    label.fade_out = fade_out
    label.fade_in = fade_in
    label.helper = helper

def stopBlinkingAnimation(label):
    if hasattr(label, 'fade_out') and label.fade_out is not None:
        label.fade_out.stop()
        label.fade_out = None

    if hasattr(label, 'fade_in') and label.fade_in is not None:
        label.fade_in.stop()
        label.fade_in = None

    if hasattr(label, 'helper') and label.helper is not None:
        label.helper.color = QColor(255, 255, 255)
        label.helper = None