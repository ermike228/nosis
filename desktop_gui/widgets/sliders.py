# nosis/desktop_gui/widgets/sliders.py
# Enterprise-grade slider widgets for NOSIS Desktop GUI (PyQt6)
# Author: NOSIS
# License: Commercial

from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtWidgets import (
    QWidget, QSlider, QLabel, QHBoxLayout, QVBoxLayout,
    QStyleOptionSlider, QStyle, QSizePolicy
)
from PyQt6.QtGui import QPainter, QColor


class SliderBinding(QObject):
    """
    Reactive binding object to connect sliders to application state,
    backend parameters, or automation lanes.
    """
    valueChanged = pyqtSignal(str, float)

    def __init__(self, param_id: str):
        super().__init__()
        self.param_id = param_id

    def emit(self, value: float):
        self.valueChanged.emit(self.param_id, value)


class BaseSlider(QWidget):
    """
    Base slider with value normalization, precision handling,
    and signal abstraction.
    """
    changed = pyqtSignal(float)

    def __init__(self, minimum=0.0, maximum=1.0, step=0.01, value=0.0, orientation=Qt.Orientation.Horizontal):
        super().__init__()
        self._min = minimum
        self._max = maximum
        self._step = step

        self.slider = QSlider(orientation)
        self.slider.setMinimum(0)
        self.slider.setMaximum(int((self._max - self._min) / self._step))
        self.slider.setValue(int((value - self._min) / self._step))

        self.slider.valueChanged.connect(self._emit_value)

        layout = QHBoxLayout(self)
        layout.addWidget(self.slider)
        layout.setContentsMargins(0, 0, 0, 0)

    def _emit_value(self, raw):
        value = self._min + raw * self._step
        self.changed.emit(value)

    def set_value(self, value: float):
        self.slider.setValue(int((value - self._min) / self._step))

    def value(self) -> float:
        return self._min + self.slider.value() * self._step


class LabeledSlider(BaseSlider):
    """
    Slider with dynamic label displaying current value.
    """
    def __init__(self, label: str, unit: str = "", **kwargs):
        self.label_text = label
        self.unit = unit
        super().__init__(**kwargs)

        self.label = QLabel(self._format(self.value()))
        self.changed.connect(lambda v: self.label.setText(self._format(v)))

        layout = QHBoxLayout(self)
        layout.addWidget(QLabel(self.label_text))
        layout.addWidget(self.slider)
        layout.addWidget(self.label)

    def _format(self, value: float) -> str:
        return f"{value:.2f}{self.unit}"


class LogSlider(BaseSlider):
    """
    Logarithmic slider for perceptual parameters (gain, frequency).
    """
    def __init__(self, minimum=0.01, maximum=1.0, **kwargs):
        super().__init__(minimum=0, maximum=1000, step=1, **kwargs)
        self.log_min = minimum
        self.log_max = maximum

    def value(self):
        t = self.slider.value() / 1000.0
        return self.log_min * (self.log_max / self.log_min) ** t

    def set_value(self, value: float):
        import math
        t = math.log(value / self.log_min, self.log_max / self.log_min)
        self.slider.setValue(int(t * 1000))


class RangeSlider(QWidget):
    """
    Dual-handle slider implemented with two synchronized sliders.
    Used for filters, frequency bands, randomness windows.
    """
    rangeChanged = pyqtSignal(float, float)

    def __init__(self, minimum=0.0, maximum=1.0, step=0.01, low=0.2, high=0.8):
        super().__init__()
        self.min = minimum
        self.max = maximum
        self.step = step

        self.low_slider = BaseSlider(minimum, maximum, step, low)
        self.high_slider = BaseSlider(minimum, maximum, step, high)

        self.low_slider.changed.connect(self._update)
        self.high_slider.changed.connect(self._update)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Min"))
        layout.addWidget(self.low_slider)
        layout.addWidget(QLabel("Max"))
        layout.addWidget(self.high_slider)

    def _update(self, _):
        low = min(self.low_slider.value(), self.high_slider.value())
        high = max(self.low_slider.value(), self.high_slider.value())
        self.rangeChanged.emit(low, high)


class PresetSlider(LabeledSlider):
    """
    Slider with predefined semantic presets (used in AI controls).
    """
    presetChanged = pyqtSignal(str)

    def __init__(self, label: str, presets: dict, **kwargs):
        self.presets = presets
        super().__init__(label=label, **kwargs)

        self.changed.connect(self._check_preset)

    def _check_preset(self, value: float):
        for name, (low, high) in self.presets.items():
            if low <= value <= high:
                self.presetChanged.emit(name)
                break


# Utility factory for common NOSIS sliders
def make_creativity_slider():
    return PresetSlider(
        label="Creativity",
        presets={
            "Conservative": (0.0, 0.3),
            "Balanced": (0.3, 0.7),
            "Experimental": (0.7, 1.0)
        },
        minimum=0.0,
        maximum=1.0,
        step=0.01,
        value=0.5
    )
