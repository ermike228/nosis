# desktop_gui/core/router.py

from typing import Dict, Type, Optional, List
from PyQt6.QtWidgets import QStackedWidget, QWidget
from PyQt6.QtCore import QObject, pyqtSignal

from desktop_gui.core.permissions import PermissionManager
from desktop_gui.core.config import UIConfig


class Router(QObject):
    """
    Central GUI router based on QStackedWidget.

    Responsibilities:
    - Page registration
    - Navigation
    - Permission checks
    - Navigation history
    """

    page_changed = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._stack = QStackedWidget(parent)
        self._pages: Dict[str, QWidget] = {}
        self._page_classes: Dict[str, Type[QWidget]] = {}
        self._history: List[str] = []

        self._permissions = PermissionManager()
        self._config = UIConfig()

    # ---------- PUBLIC API ----------

    @property
    def widget(self) -> QStackedWidget:
        """Returns QStackedWidget to be embedded into layouts."""
        return self._stack

    def register_page(self, name: str, widget_cls: Type[QWidget]) -> None:
        """
        Register page class for lazy initialization.

        Example:
            router.register_page("create", CreatePage)
        """
        if name in self._page_classes:
            raise ValueError(f"Page '{name}' already registered")

        self._page_classes[name] = widget_cls

    def preload_pages(self) -> None:
        """
        Preload pages marked as preloadable in UIConfig.
        """
        for name in self._config.preload_pages:
            if name in self._page_classes:
                self._ensure_page(name)

    def navigate(self, name: str) -> None:
        """
        Navigate to page by name.
        """
        if not self.can_access(name):
            raise PermissionError(f"Access denied for page '{name}'")

        widget = self._ensure_page(name)

        self._stack.setCurrentWidget(widget)
        self._history.append(name)

        self.page_changed.emit(name)

    def back(self) -> None:
        """
        Navigate back in history.
        """
        if len(self._history) < 2:
            return

        self._history.pop()
        previous = self._history[-1]
        self._stack.setCurrentWidget(self._pages[previous])
        self.page_changed.emit(previous)

    # ---------- INTERNAL ----------

    def _ensure_page(self, name: str) -> QWidget:
        """
        Lazily create page if not exists.
        """
        if name in self._pages:
            return self._pages[name]

        if name not in self._page_classes:
            raise KeyError(f"Page '{name}' is not registered")

        page = self._page_classes[name]()
        self._pages[name] = page
        self._stack.addWidget(page)

        return page

    def can_access(self, name: str) -> bool:
        """
        Permission + feature flag check.
        """
        if not self._config.is_page_enabled(name):
            return False

        return self._permissions.can_access_page(name)

    def clear(self) -> None:
        """
        Destroy all pages (used for logout / user switch).
        """
        self._stack.clear()
        self._pages.clear()
        self._history.clear()
