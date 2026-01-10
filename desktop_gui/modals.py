# nosis/desktop_gui/widgets/modals.py
# Enterprise-grade modal & dialog system for NOSIS Desktop GUI (PyQt6)
# Covers Create / Studio / Chat / Library / System dialogs
# License: Commercial

from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtWidgets import (
    QDialog, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QSizePolicy, QFrame
)


class ModalResult:
    """Standardized modal result constants."""
    ACCEPT = "accept"
    REJECT = "reject"
    APPLY = "apply"
    CANCEL = "cancel"
    CUSTOM = "custom"


class BaseModal(QDialog):
    """
    Base enterprise modal window.
    Provides:
    - unified layout
    - semantic result handling
    - keyboard shortcuts
    - extensible content area
    """
    resultSemantic = pyqtSignal(str)

    def __init__(self, title: str, width: int = 520, height: int = 360):
        super().__init__()
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(QSize(width, height))
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(20, 20, 20, 20)
        self.root_layout.setSpacing(16)

        self._build_header(title)
        self._build_body()
        self._build_footer()
        self._bind_shortcuts()

    def _build_header(self, title: str):
        header = QLabel(title)
        header.setObjectName("ModalTitle")
        header.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.root_layout.addWidget(header)

    def _build_body(self):
        self.body = QFrame()
        self.body.setObjectName("ModalBody")
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(12)
        self.root_layout.addWidget(self.body, 1)

    def _build_footer(self):
        self.footer = QFrame()
        self.footer.setObjectName("ModalFooter")
        footer_layout = QHBoxLayout(self.footer)
        footer_layout.setContentsMargins(0, 12, 0, 0)
        footer_layout.setSpacing(8)
        footer_layout.addStretch()

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self._on_cancel)

        self.btn_ok = QPushButton("OK")
        self.btn_ok.setDefault(True)
        self.btn_ok.clicked.connect(self._on_accept)

        footer_layout.addWidget(self.btn_cancel)
        footer_layout.addWidget(self.btn_ok)

        self.root_layout.addWidget(self.footer)

    def _bind_shortcuts(self):
        self.btn_cancel.setShortcut(Qt.Key.Key_Escape)
        self.btn_ok.setShortcut(Qt.Key.Key_Return)

    def add_content(self, widget: QWidget):
        self.body_layout.addWidget(widget)

    def _on_accept(self):
        self.resultSemantic.emit(ModalResult.ACCEPT)
        self.accept()

    def _on_cancel(self):
        self.resultSemantic.emit(ModalResult.CANCEL)
        self.reject()


class ConfirmModal(BaseModal):
    """Confirmation dialog for destructive or critical actions."""
    def __init__(self, title: str, message: str):
        super().__init__(title, width=480, height=220)
        label = QLabel(message)
        label.setWordWrap(True)
        self.add_content(label)


class FormModal(BaseModal):
    """Modal with form-like content (settings, export, AI options)."""
    def __init__(self, title: str):
        super().__init__(title)
        self.form_layout = QVBoxLayout()
        self.body_layout.addLayout(self.form_layout)

    def add_field(self, label: str, widget: QWidget):
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setFixedWidth(140)
        row.addWidget(lbl)
        row.addWidget(widget, 1)
        self.form_layout.addLayout(row)


class InfoModal(BaseModal):
    """Read-only informational dialog."""
    def __init__(self, title: str, message: str):
        super().__init__(title, width=500, height=260)
        label = QLabel(message)
        label.setWordWrap(True)
        self.add_content(label)
        self.btn_ok.setText("Close")


class ProgressModal(BaseModal):
    """
    Modal for long-running operations:
    generation, rendering, exporting.
    """
    cancelled = pyqtSignal()

    def __init__(self, title: str, message: str):
        super().__init__(title, width=520, height=240)
        label = QLabel(message)
        label.setWordWrap(True)
        self.add_content(label)

        self.btn_ok.hide()
        self.btn_cancel.setText("Cancel")
        self.btn_cancel.clicked.connect(self.cancelled.emit)


class CustomActionModal(BaseModal):
    """Modal with custom footer actions."""
    def __init__(self, title: str, actions: dict[str, str]):
        super().__init__(title)

        # Remove default buttons
        for btn in self.footer.findChildren(QPushButton):
            btn.setParent(None)

        footer_layout = self.footer.layout()
        footer_layout.addStretch()

        for action_id, label in actions.items():
            btn = QPushButton(label)
            btn.clicked.connect(lambda _, a=action_id: self._emit_custom(a))
            footer_layout.addWidget(btn)

    def _emit_custom(self, action_id: str):
        self.resultSemantic.emit(action_id)
        self.accept()
