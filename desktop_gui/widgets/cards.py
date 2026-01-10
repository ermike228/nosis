# nosis/desktop_gui/widgets/cards.py
# Enterprise-grade Card components for NOSIS Desktop GUI (PyQt6)
# Used in Library, Create, Studio, Inspector, Chat, Presets
# License: Commercial

from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QSizePolicy, QFrame
)
from PyQt6.QtGui import QPixmap


class CardAction:
    """
    Semantic card actions used across the app.
    """
    OPEN = "open"
    SELECT = "select"
    PLAY = "play"
    PREVIEW = "preview"
    EDIT = "edit"
    DELETE = "delete"
    EXPORT = "export"
    FAVORITE = "favorite"


class BaseCard(QFrame):
    """
    Base enterprise card widget.
    Provides:
    - unified visual container
    - hover / selection state
    - semantic action dispatch
    """
    actionTriggered = pyqtSignal(str, dict)

    def __init__(self, card_id: str, selectable: bool = True):
        super().__init__()
        self.card_id = card_id
        self.selectable = selectable
        self.selected = False

        self.setObjectName("BaseCard")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(12, 12, 12, 12)
        self.root_layout.setSpacing(8)

    def mousePressEvent(self, event):
        if self.selectable:
            self.selected = not self.selected
            self.setProperty("selected", self.selected)
            self.style().polish(self)

        self.actionTriggered.emit(CardAction.SELECT, {"id": self.card_id})
        super().mousePressEvent(event)


class MediaCard(BaseCard):
    """
    Card representing media content:
    - track
    - stem
    - preset
    """
    def __init__(
        self,
        card_id: str,
        title: str,
        subtitle: str = "",
        image_path: str | None = None
    ):
        super().__init__(card_id)

        self.cover = QLabel()
        self.cover.setFixedSize(QSize(96, 96))
        self.cover.setObjectName("CardCover")

        if image_path:
            pix = QPixmap(image_path).scaled(
                96, 96, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            self.cover.setPixmap(pix)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("CardTitle")

        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("CardSubtitle")

        text_layout = QVBoxLayout()
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.subtitle_label)

        top = QHBoxLayout()
        top.addWidget(self.cover)
        top.addLayout(text_layout, 1)

        self.root_layout.addLayout(top)

        self._build_actions()

    def _build_actions(self):
        actions = QHBoxLayout()
        actions.addStretch()

        btn_play = QPushButton("▶")
        btn_play.clicked.connect(
            lambda: self.actionTriggered.emit(CardAction.PLAY, {"id": self.card_id})
        )

        btn_more = QPushButton("⋯")
        btn_more.clicked.connect(
            lambda: self.actionTriggered.emit(CardAction.OPEN, {"id": self.card_id})
        )

        actions.addWidget(btn_play)
        actions.addWidget(btn_more)
        self.root_layout.addLayout(actions)


class InfoCard(BaseCard):
    """
    Card for informational blocks:
    - tips
    - onboarding
    - AI suggestions
    """
    def __init__(self, card_id: str, title: str, description: str):
        super().__init__(card_id, selectable=False)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("CardTitle")

        desc_lbl = QLabel(description)
        desc_lbl.setWordWrap(True)
        desc_lbl.setObjectName("CardDescription")

        self.root_layout.addWidget(title_lbl)
        self.root_layout.addWidget(desc_lbl)


class PresetCard(BaseCard):
    """
    Card representing a preset (style, model, genre bundle).
    """
    def __init__(self, card_id: str, name: str, meta: dict):
        super().__init__(card_id)

        name_lbl = QLabel(name)
        name_lbl.setObjectName("CardTitle")

        meta_lbl = QLabel(", ".join(f"{k}: {v}" for k, v in meta.items()))
        meta_lbl.setObjectName("CardSubtitle")

        self.root_layout.addWidget(name_lbl)
        self.root_layout.addWidget(meta_lbl)

        btn_apply = QPushButton("Apply")
        btn_apply.clicked.connect(
            lambda: self.actionTriggered.emit(CardAction.APPLY, {"id": self.card_id})
        )
        self.root_layout.addWidget(btn_apply)


class CardGrid(QWidget):
    """
    Grid-like container for cards.
    Used in Library, Presets, Browser.
    """
    cardAction = pyqtSignal(str, dict)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)

    def add_card(self, card: BaseCard):
        card.actionTriggered.connect(self.cardAction.emit)
        self.layout.addWidget(card)

    def clear(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
