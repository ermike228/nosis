# nosis/desktop_gui/widgets/chips.py
# Enterprise-grade Chip / Tag / Token widgets for NOSIS Desktop GUI (PyQt6)
# Used across Create / Studio / Chat / Library / Inspector
# License: Commercial

from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout,
    QSizePolicy, QScrollArea, QFrame
)
from PyQt6.QtGui import QColor


class Chip(QFrame):
    """
    Single semantic chip (tag/token).
    Examples:
    - Genre: Ambient
    - Mood: Dark
    - Language: English
    - AI Lock: Melody
    """
    removed = pyqtSignal(str)
    clickedSemantic = pyqtSignal(str)

    def __init__(self, text: str, chip_id: str | None = None, removable: bool = True):
        super().__init__()
        self.chip_id = chip_id or text
        self.setObjectName("Chip")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.label = QLabel(text)
        self.label.setObjectName("ChipLabel")

        self.close_btn = None
        if removable:
            self.close_btn = QPushButton("×")
            self.close_btn.setObjectName("ChipClose")
            self.close_btn.setFixedSize(QSize(14, 14))
            self.close_btn.clicked.connect(self._on_remove)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 6, 2)
        layout.setSpacing(6)
        layout.addWidget(self.label)

        if self.close_btn:
            layout.addWidget(self.close_btn)

    def mousePressEvent(self, event):
        self.clickedSemantic.emit(self.chip_id)
        super().mousePressEvent(event)

    def _on_remove(self):
        self.removed.emit(self.chip_id)
        self.setParent(None)
        self.deleteLater()


class ChipGroup(QWidget):
    """
    Container for multiple chips with flow-like behavior.
    """
    chipAdded = pyqtSignal(str)
    chipRemoved = pyqtSignal(str)
    chipClicked = pyqtSignal(str)

    def __init__(self, title: str | None = None):
        super().__init__()
        self.setObjectName("ChipGroup")

        self.layout = QHBoxLayout()
        self.layout.setSpacing(6)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.container = QWidget()
        self.container.setLayout(self.layout)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setWidget(self.container)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        if title:
            lbl = QLabel(title)
            lbl.setObjectName("ChipGroupTitle")
            root.addWidget(lbl)

        root.addWidget(self.scroll)

    def add_chip(self, text: str, chip_id: str | None = None, removable: bool = True):
        chip = Chip(text, chip_id, removable)
        chip.removed.connect(self._on_removed)
        chip.clickedSemantic.connect(self.chipClicked.emit)
        self.layout.addWidget(chip)
        self.chipAdded.emit(chip.chip_id)

    def _on_removed(self, chip_id: str):
        self.chipRemoved.emit(chip_id)

    def clear(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


class SelectableChip(Chip):
    """
    Chip with selectable (toggle) state.
    Used for:
    - multi-genre selection
    - moods
    - filters
    """
    toggled = pyqtSignal(str, bool)

    def __init__(self, text: str, chip_id: str | None = None):
        super().__init__(text, chip_id, removable=False)
        self.setCheckable(True)
        self._selected = False
        self.update_style()

    def mousePressEvent(self, event):
        self._selected = not self._selected
        self.update_style()
        self.toggled.emit(self.chip_id, self._selected)
        super().mousePressEvent(event)

    def update_style(self):
        self.setProperty("selected", self._selected)
        self.style().polish(self)


class ChipCloud(QWidget):
    """
    High-level widget for large-scale semantic selections.
    Can handle hundreds or thousands of chips efficiently.
    """
    selectionChanged = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.chips = {}

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def load(self, items: list[str]):
        self.clear()
        for item in items:
            chip = SelectableChip(item)
            chip.toggled.connect(self._on_toggle)
            self.layout.addWidget(chip)
            self.chips[item] = chip

    def _on_toggle(self, chip_id: str, state: bool):
        selected = [k for k, v in self.chips.items() if v._selected]
        self.selectionChanged.emit(selected)

    def clear(self):
        for chip in self.chips.values():
            chip.deleteLater()
        self.chips.clear()
