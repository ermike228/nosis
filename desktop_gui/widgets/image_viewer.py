
"""
NOSIS Image Viewer Widget
Enterprise-level image viewer for AI-generated cover art, references,
and inspector previews.

Author: NOSIS
Level: Lead Enterprise 2026
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QFileDialog
)
from PyQt6.QtGui import QPixmap, QWheelEvent
from PyQt6.QtCore import Qt, pyqtSignal, QRectF


class ImageViewer(QWidget):
    """
    High-performance image viewer with zoom, pan, and signal hooks.
    Used across:
    - Create → Inspector (cover preview)
    - Library → Track card
    - Studio → Visual timeline
    - Chat Assistant → inline image reasoning
    """

    imageLoaded = pyqtSignal(str)
    zoomChanged = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._zoom = 1.0
        self._min_zoom = 0.1
        self._max_zoom = 10.0

        self._scene = QGraphicsScene(self)
        self._view = QGraphicsView(self._scene, self)
        self._view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self._view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self._view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self._view.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

        self._pixmap_item = QGraphicsPixmapItem()
        self._scene.addItem(self._pixmap_item)

        self._load_button = QPushButton("Load Image")
        self._load_button.clicked.connect(self.load_image_dialog)

        layout = QVBoxLayout(self)
        layout.addWidget(self._view)
        layout.addWidget(self._load_button)
        self.setLayout(layout)

    def load_image_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Image",
            "",
            "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if path:
            self.load_image(path)

    def load_image(self, path: str):
        pixmap = QPixmap(path)
        if pixmap.isNull():
            return

        self._pixmap_item.setPixmap(pixmap)
        self._scene.setSceneRect(QRectF(pixmap.rect()))
        self._reset_view()
        self.imageLoaded.emit(path)

    def _reset_view(self):
        self._zoom = 1.0
        self._view.resetTransform()
        self._view.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        factor = 1.15 if delta > 0 else 0.85
        new_zoom = self._zoom * factor

        if self._min_zoom <= new_zoom <= self._max_zoom:
            self._zoom = new_zoom
            self._view.scale(factor, factor)
            self.zoomChanged.emit(self._zoom)

    def clear(self):
        self._pixmap_item.setPixmap(QPixmap())
        self._scene.clear()

    def get_zoom(self) -> float:
        return self._zoom
