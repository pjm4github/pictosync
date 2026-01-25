"""
canvas/scene.py

QGraphicsScene with drawing mode support for creating annotation items.
"""

from __future__ import annotations

from typing import Callable, Optional

from PyQt6.QtCore import Qt, QPointF, QRectF, QLineF
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsItem

from models import Mode
from canvas.items import (
    MetaRectItem,
    MetaRoundedRectItem,
    MetaEllipseItem,
    MetaLineItem,
    MetaTextItem,
)


class AnnotatorScene(QGraphicsScene):
    """
    Graphics scene with drawing mode support.

    Supports creating shapes (rect, rounded rect, ellipse, line, text)
    by clicking and dragging in the appropriate mode.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode = Mode.SELECT
        self._drag_start: Optional[QPointF] = None
        self._temp_item: Optional[QGraphicsItem] = None
        self._make_id: Optional[Callable[[], str]] = None
        self._on_new_item: Optional[Callable[[QGraphicsItem], None]] = None
        self._on_item_changed: Optional[Callable[[QGraphicsItem], None]] = None
        self._on_right_click: Optional[Callable[[], None]] = None  # For exiting sticky mode
        self._on_escape_key: Optional[Callable[[], None]] = None  # For exiting sticky mode

    def set_mode(self, mode: str) -> None:
        """Set the current drawing mode."""
        self.mode = mode

    def configure_linkage(
        self,
        make_id: Callable[[], str],
        on_new_item: Callable[[QGraphicsItem], None],
        on_item_changed: Callable[[QGraphicsItem], None],
    ):
        """
        Configure callbacks for JSON<->Scene linkage.

        Args:
            make_id: Function to generate new annotation IDs
            on_new_item: Callback when a new item is created
            on_item_changed: Callback when an item's geometry/style changes
        """
        self._make_id = make_id
        self._on_new_item = on_new_item
        self._on_item_changed = on_item_changed

    def set_right_click_callback(self, callback: Optional[Callable[[], None]]):
        """Set callback for right-click (used to exit sticky tool mode)."""
        self._on_right_click = callback

    def set_escape_key_callback(self, callback: Optional[Callable[[], None]]):
        """Set callback for Escape key (used to exit sticky tool mode)."""
        self._on_escape_key = callback

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Escape:
            if self._on_escape_key:
                self._on_escape_key()
                event.accept()
                return
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        # Right-click exits sticky mode
        if event.button() == Qt.MouseButton.RightButton:
            if self._on_right_click:
                self._on_right_click()
                event.accept()
                return

        if event.button() == Qt.MouseButton.LeftButton:
            sp = event.scenePos()

            if self.mode in (Mode.RECT, Mode.ROUNDEDRECT, Mode.ELLIPSE, Mode.LINE):
                self._drag_start = sp
                ann_id = self._make_id() if self._make_id else "local"

                if self.mode == Mode.RECT:
                    self._temp_item = MetaRectItem(sp.x(), sp.y(), 0, 0, ann_id, self._on_item_changed)
                    self.addItem(self._temp_item)
                elif self.mode == Mode.ROUNDEDRECT:
                    self._temp_item = MetaRoundedRectItem(sp.x(), sp.y(), 0, 0, 10, ann_id, self._on_item_changed)
                    self.addItem(self._temp_item)
                elif self.mode == Mode.ELLIPSE:
                    self._temp_item = MetaEllipseItem(sp.x(), sp.y(), 0, 0, ann_id, self._on_item_changed)
                    self.addItem(self._temp_item)
                elif self.mode == Mode.LINE:
                    self._temp_item = MetaLineItem(sp.x(), sp.y(), sp.x(), sp.y(), ann_id, self._on_item_changed)
                    self.addItem(self._temp_item)

                event.accept()
                return

            elif self.mode == Mode.TEXT:
                ann_id = self._make_id() if self._make_id else "local"
                ti = MetaTextItem(sp.x(), sp.y(), "Double-click to edit", ann_id, self._on_item_changed)
                self.addItem(ti)
                ti.setSelected(True)
                if self._on_new_item:
                    self._on_new_item(ti)
                event.accept()
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_start is not None and self._temp_item is not None:
            cur = event.scenePos()
            sx, sy = self._drag_start.x(), self._drag_start.y()
            cx, cy = cur.x(), cur.y()

            if isinstance(self._temp_item, (MetaRectItem, MetaEllipseItem, MetaRoundedRectItem)):
                x = min(sx, cx)
                y = min(sy, cy)
                w = abs(cx - sx)
                h = abs(cy - sy)
                self._temp_item.setPos(QPointF(x, y))
                self._temp_item.setRect(QRectF(0, 0, w, h))
            elif isinstance(self._temp_item, MetaLineItem):
                x1, y1 = sx, sy
                x2, y2 = cx, cy
                self._temp_item.setPos(QPointF(x1, y1))
                self._temp_item.setLine(QLineF(0, 0, x2 - x1, y2 - y1))

            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._drag_start is not None and self._temp_item is not None:
            if self._on_new_item:
                self._on_new_item(self._temp_item)

            self._drag_start = None
            self._temp_item = None
            event.accept()
            return

        super().mouseReleaseEvent(event)
