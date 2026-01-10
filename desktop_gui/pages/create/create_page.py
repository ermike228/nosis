"""
NOSIS Desktop GUI – Create Page
===============================

Enterprise-grade music generation workspace (2025–2026).

Layout (horizontal split):
------------------------------------------------------------
| Generator Panel | Generated Library | Inspector Panel |
------------------------------------------------------------

Responsibilities:
- Primary generation workflow
- Prompt / style / controls
- Generated items preview
- Selection-driven inspection
- Bridge-layer orchestration

NO ML logic
NO backend logic
ALL actions via signals & bridge
"""

from __future__ import annotations

import logging
from typing import Optional, Dict, Any, List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QSlider,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QFrame,
    QSizePolicy,
    QSplitter,
    QLineEdit,
)

from desktop_gui.core.signals import get_signals
from desktop_gui.core.app_state import get_app_state
from desktop_gui.core.permissions import get_permissions

logger = logging.getLogger("nosis.create_page")


# =============================================================================
# CREATE PAGE
# =============================================================================

class CreatePage(QWidget):
    """
    Main music generation workspace.

    This page is the HEART of the product.
    """

    ROUTE = "create"

    def __init__(self):
        super().__init__()

        self._signals = get_signals()
        self._state = get_app_state()
        self._permissions = get_permissions()

        self.setObjectName("CreatePage")

        self._init_ui()
        self._connect_signals()

        logger.info("CreatePage initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.generator = GeneratorPanel()
        self.library = GeneratedLibraryPanel()
        self.inspector = InspectorPanel()

        splitter.addWidget(self.generator)
        splitter.addWidget(self.library)
        splitter.addWidget(self.inspector)

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 2)

        layout.addWidget(splitter)

    # ------------------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:
        self._signals.generated_item_selected.connect(
            self.inspector.display_item
        )


# =============================================================================
# GENERATOR PANEL
# =============================================================================

class GeneratorPanel(QFrame):
    """
    Left panel: prompt, style, controls.
    """

    def __init__(self):
        super().__init__()

        self._signals = get_signals()
        self._permissions = get_permissions()

        self.setObjectName("CreateGenerator")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setMinimumWidth(420)

        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Lyrics
        layout.addWidget(SectionLabel("Lyrics"))
        self.lyrics = ExpandableText("Enter lyrics or leave empty")
        layout.addWidget(self.lyrics)

        # Style
        layout.addWidget(SectionLabel("Style"))
        self.style = ExpandableText("Describe genre, mood, style (up to 10k chars)")
        layout.addWidget(self.style)

        # Sliders
        layout.addWidget(SectionLabel("Controls"))

        self.prompt_accuracy = LabeledSlider("Prompt Accuracy")
        self.reference_similarity = LabeledSlider("Reference Similarity")
        self.creativity = LabeledSlider("Creativity / Strangeness")

        layout.addWidget(self.prompt_accuracy)
        layout.addWidget(self.reference_similarity)
        layout.addWidget(self.creativity)

        # Negative prompt
        layout.addWidget(SectionLabel("Negative Prompt"))
        self.negative = QLineEdit()
        self.negative.setPlaceholderText("What should be avoided")
        layout.addWidget(self.negative)

        # Title
        layout.addWidget(SectionLabel("Track Title"))
        self.title = QLineEdit()
        layout.addWidget(self.title)

        # Generate
        self.generate_btn = QPushButton("Generate")
        self.generate_btn.setObjectName("CreateGenerateButton")
        self.generate_btn.setEnabled(self._permissions.can_generate())
        self.generate_btn.clicked.connect(self._on_generate)

        layout.addWidget(self.generate_btn)

        layout.addStretch()

    def _on_generate(self):
        payload = {
            "lyrics": self.lyrics.toPlainText(),
            "style": self.style.toPlainText(),
            "negative": self.negative.text(),
            "title": self.title.text(),
            "controls": {
                "prompt_accuracy": self.prompt_accuracy.value(),
                "reference_similarity": self.reference_similarity.value(),
                "creativity": self.creativity.value(),
            },
        }
        self._signals.generate_requested.emit(payload)


# =============================================================================
# GENERATED LIBRARY PANEL
# =============================================================================

class GeneratedLibraryPanel(QFrame):
    """
    Middle panel: generated tracks.
    """

    def __init__(self):
        super().__init__()

        self._signals = get_signals()
        self.setObjectName("CreateLibrary")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setMinimumWidth(320)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        header = QLabel("Generated Tracks")
        header.setObjectName("CreateLibraryHeader")
        layout.addWidget(header)

        self.list = QListWidget()
        self.list.itemClicked.connect(self._on_item_selected)
        layout.addWidget(self.list)

        # Example placeholder items (real ones come from backend)
        for i in range(4):
            item = QListWidgetItem(f"Track #{i+1}")
            item.setData(Qt.ItemDataRole.UserRole, {"id": i})
            self.list.addItem(item)

    def _on_item_selected(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole)
        self._signals.generated_item_selected.emit(data)


# =============================================================================
# INSPECTOR PANEL
# =============================================================================

class InspectorPanel(QFrame):
    """
    Right panel: detailed info about selected generation.
    """

    def __init__(self):
        super().__init__()

        self.setObjectName("CreateInspector")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setMinimumWidth(360)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        self.title = QLabel("Inspector")
        self.title.setObjectName("InspectorTitle")
        layout.addWidget(self.title)

        self.content = QTextEdit()
        self.content.setReadOnly(True)
        layout.addWidget(self.content)

        layout.addStretch()

    def display_item(self, data: Optional[Dict[str, Any]]):
        if not data:
            self.content.setText("No selection")
            return
        self.content.setText(str(data))


# =============================================================================
# UI COMPONENTS
# =============================================================================

class SectionLabel(QLabel):
    def __init__(self, text: str):
        super().__init__(text)
        self.setObjectName("CreateSectionLabel")


class ExpandableText(QTextEdit):
    def __init__(self, placeholder: str):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(80)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )


class LabeledSlider(QFrame):
    def __init__(self, label: str):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(label)
        layout.addWidget(self.label)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        layout.addWidget(self.slider)

    def value(self) -> int:
        return self.slider.value()
