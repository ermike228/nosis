# nosis/desktop_gui/widgets/dropdowns.py
# Enterprise-grade Dropdown / Combo widgets for NOSIS Desktop GUI (PyQt6)
# Used across Create / Studio / Chat / Inspector / Settings
# License: Commercial

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QLabel, QComboBox, QVBoxLayout, QHBoxLayout,
    QSizePolicy
)


class DropdownAction:
    """
    Semantic dropdown actions.
    """
    SELECT = "select"
    CHANGE = "change"
    CLEAR = "clear"


class BaseDropdown(QWidget):
    """
    Base enterprise dropdown widget.

    Features:
    - semantic value binding
    - dynamic population
    - clean separation UI <-> logic
    """
    valueChangedSemantic = pyqtSignal(str, object)

    def __init__(self, label: str | None = None, dropdown_id: str | None = None):
        super().__init__()
        self.dropdown_id = dropdown_id or label or "dropdown"

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)

        if label:
            lbl = QLabel(label)
            lbl.setObjectName("DropdownLabel")
            self.layout.addWidget(lbl)

        self.combo = QComboBox()
        self.combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.combo.currentIndexChanged.connect(self._emit_change)

        self.layout.addWidget(self.combo)

    def set_items(self, items: list[tuple[str, object]]):
        """
        items: list of (display_text, value)
        """
        self.combo.clear()
        for text, value in items:
            self.combo.addItem(text, value)

    def value(self):
        return self.combo.currentData()

    def _emit_change(self):
        self.valueChangedSemantic.emit(self.dropdown_id, self.value())

    def clear(self):
        self.combo.setCurrentIndex(-1)
        self.valueChangedSemantic.emit(self.dropdown_id, None)


class SearchableDropdown(BaseDropdown):
    """
    Dropdown with built-in search.
    Used for:
    - models
    - genres (700-10000)
    - voices
    """
    def __init__(self, label: str | None = None, dropdown_id: str | None = None):
        super().__init__(label, dropdown_id)
        self.combo.setEditable(True)
        self.combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.combo.completer().setCompletionMode(
            self.combo.completer().CompletionMode.PopupCompletion
        )


class MultiSelectDropdown(BaseDropdown):
    """
    Multi-select dropdown using checkable items.
    Used for:
    - multi-genre blending
    - mood selection
    """
    valuesChanged = pyqtSignal(str, list)

    def __init__(self, label: str | None = None, dropdown_id: str | None = None):
        super().__init__(label, dropdown_id)
        self.combo.setEditable(True)
        self.combo.lineEdit().setReadOnly(True)
        self.combo.model().dataChanged.connect(self._update_values)

        self._values = []

    def set_items(self, items: list[tuple[str, object]]):
        self.combo.clear()
        model = self.combo.model()
        for text, value in items:
            self.combo.addItem(text)
            index = self.combo.model().index(self.combo.count() - 1, 0)
            model.setData(index, Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
            model.setData(index, value, Qt.ItemDataRole.UserRole)

    def _update_values(self):
        values = []
        labels = []
        model = self.combo.model()
        for i in range(self.combo.count()):
            idx = model.index(i, 0)
            if model.data(idx, Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Checked:
                values.append(model.data(idx, Qt.ItemDataRole.UserRole))
                labels.append(self.combo.itemText(i))

        self._values = values
        self.combo.lineEdit().setText(", ".join(labels))
        self.valuesChanged.emit(self.dropdown_id, values)

    def values(self):
        return self._values


# Factory helpers

def make_model_selector():
    return SearchableDropdown(label="Model", dropdown_id="model_selector")

def make_voice_selector():
    return SearchableDropdown(label="Voice", dropdown_id="voice_selector")

def make_genre_selector():
    return MultiSelectDropdown(label="Genres", dropdown_id="genre_selector")
