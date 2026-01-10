# nosis/desktop_gui/widgets/buttons.py
# Enterprise-grade button system for NOSIS Desktop GUI (PyQt6)
# Designed for Create / Studio / Chat / DAW / AI workflows
# License: Commercial

from PyQt6.QtCore import Qt, pyqtSignal, QSize, QObject
from PyQt6.QtWidgets import (
    QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QSizePolicy, QMenu
)
from PyQt6.QtGui import QIcon, QColor


class ButtonAction(QObject):
    """
    Declarative action object.
    Allows buttons to be bound to commands, backend actions,
    shortcuts, permissions, and analytics.
    """
    triggered = pyqtSignal(str)

    def __init__(self, action_id: str, description: str = ""):
        super().__init__()
        self.action_id = action_id
        self.description = description

    def fire(self):
        self.triggered.emit(self.action_id)


class BaseButton(QPushButton):
    """
    Base enterprise button with:
    - semantic role
    - loading / disabled states
    - consistent styling hooks
    """
    clickedSemantic = pyqtSignal(str)

    def __init__(
        self,
        text: str,
        action_id: str = "",
        icon: QIcon | None = None,
        checkable: bool = False
    ):
        super().__init__(text)
        self.action_id = action_id
        self.setCheckable(checkable)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        if icon:
            self.setIcon(icon)
            self.setIconSize(QSize(18, 18))

        self.clicked.connect(self._emit_semantic)

    def _emit_semantic(self):
        if self.action_id:
            self.clickedSemantic.emit(self.action_id)

    def set_loading(self, loading: bool):
        self.setEnabled(not loading)
        self.setText("Processing…" if loading else self.text())


class PrimaryButton(BaseButton):
    """
    Primary call-to-action button.
    Used for:
    - Generate
    - Render
    - Export
    - Apply
    """
    def __init__(self, text: str, action_id: str = "", icon: QIcon | None = None):
        super().__init__(text, action_id, icon)
        self.setProperty("role", "primary")


class SecondaryButton(BaseButton):
    """
    Secondary action button.
    Used for:
    - Preview
    - Regenerate
    - Duplicate
    """
    def __init__(self, text: str, action_id: str = "", icon: QIcon | None = None):
        super().__init__(text, action_id, icon)
        self.setProperty("role", "secondary")


class DangerButton(BaseButton):
    """
    Destructive action button.
    Used for:
    - Delete
    - Reset
    - Clear
    """
    def __init__(self, text: str, action_id: str = "", icon: QIcon | None = None):
        super().__init__(text, action_id, icon)
        self.setProperty("role", "danger")


class ToggleButton(BaseButton):
    """
    Toggleable button with semantic states.
    Used for:
    - Solo / Mute
    - AI locks
    - Enable / Disable modules
    """
    toggledSemantic = pyqtSignal(str, bool)

    def __init__(self, text: str, action_id: str = "", icon: QIcon | None = None):
        super().__init__(text, action_id, icon, checkable=True)
        self.toggled.connect(self._emit_toggle)

    def _emit_toggle(self, state: bool):
        self.toggledSemantic.emit(self.action_id, state)


class IconButton(BaseButton):
    """
    Minimal icon-only button.
    Used in toolbars, mixers, timelines.
    """
    def __init__(self, icon: QIcon, tooltip: str, action_id: str = ""):
        super().__init__("", action_id, icon)
        self.setToolTip(tooltip)
        self.setFixedSize(32, 32)


class DropdownButton(BaseButton):
    """
    Button with attached menu.
    Used for:
    - Export formats
    - Model selection
    - Presets
    """
    optionSelected = pyqtSignal(str, str)

    def __init__(self, text: str, action_id: str = "", options: dict | None = None):
        super().__init__(text, action_id)
        self.menu = QMenu(self)
        self.options = options or {}

        for key, label in self.options.items():
            act = self.menu.addAction(label)
            act.triggered.connect(lambda _, k=key: self.optionSelected.emit(action_id, k))

        self.setMenu(self.menu)


class ButtonGroup(QWidget):
    """
    Horizontal or vertical button group with shared semantics.
    """
    actionTriggered = pyqtSignal(str)

    def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Horizontal):
        super().__init__()
        self.layout = QHBoxLayout() if orientation == Qt.Orientation.Horizontal else QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    def add_button(self, button: BaseButton):
        button.clickedSemantic.connect(self.actionTriggered.emit)
        self.layout.addWidget(button)


# Factory helpers for common NOSIS actions

def make_generate_button():
    return PrimaryButton("Generate", action_id="generate_music")

def make_regenerate_button():
    return SecondaryButton("Regenerate", action_id="regenerate_music")

def make_delete_button():
    return DangerButton("Delete", action_id="delete_item")
