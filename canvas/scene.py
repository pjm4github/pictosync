"""
canvas/scene.py

QGraphicsScene with drawing mode support for creating annotation items.
"""

from __future__ import annotations

from typing import Callable, List, Optional

from PyQt6.QtCore import Qt, QPointF, QRectF, QLineF
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsItem, QMenu

from models import Mode
from canvas.items import (
    MetaRectItem,
    MetaRoundedRectItem,
    MetaEllipseItem,
    MetaLineItem,
    MetaTextItem,
)

# Z-index constants
Z_INDEX_BASE = 1000  # Starting z-index for normal items
Z_INDEX_STEP = 10    # Gap between z-indices for room to insert


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
        self._on_z_order_changed: Optional[Callable[[], None]] = None  # For z-order changes

    def set_z_order_changed_callback(self, callback: Optional[Callable[[], None]]):
        """Set callback for when z-order changes (used to sync JSON)."""
        self._on_z_order_changed = callback

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
        # Right-click: show context menu if item is selected, otherwise exit sticky mode
        if event.button() == Qt.MouseButton.RightButton:
            item = self.itemAt(event.scenePos(), self.views()[0].transform() if self.views() else None)
            # Check if the item is one of our annotation items (not background)
            if item and self._is_annotation_item(item) and item.isSelected():
                self._show_context_menu(event.screenPos(), item)
                event.accept()
                return
            elif self._on_right_click:
                self._on_right_click()
                event.accept()
                return

        if event.button() == Qt.MouseButton.LeftButton:
            sp = event.scenePos()

            if self.mode in (Mode.RECT, Mode.ROUNDEDRECT, Mode.ELLIPSE, Mode.LINE):
                self._drag_start = sp
                ann_id = self._make_id() if self._make_id else "local"
                next_z = self._get_next_z_index()

                if self.mode == Mode.RECT:
                    self._temp_item = MetaRectItem(sp.x(), sp.y(), 0, 0, ann_id, self._on_item_changed)
                    self.addItem(self._temp_item)
                    self._temp_item.setZValue(next_z)
                elif self.mode == Mode.ROUNDEDRECT:
                    self._temp_item = MetaRoundedRectItem(sp.x(), sp.y(), 0, 0, 10, ann_id, self._on_item_changed)
                    self.addItem(self._temp_item)
                    self._temp_item.setZValue(next_z)
                elif self.mode == Mode.ELLIPSE:
                    self._temp_item = MetaEllipseItem(sp.x(), sp.y(), 0, 0, ann_id, self._on_item_changed)
                    self.addItem(self._temp_item)
                    self._temp_item.setZValue(next_z)
                elif self.mode == Mode.LINE:
                    self._temp_item = MetaLineItem(sp.x(), sp.y(), sp.x(), sp.y(), ann_id, self._on_item_changed)
                    self.addItem(self._temp_item)
                    self._temp_item.setZValue(next_z)

                event.accept()
                return

            elif self.mode == Mode.TEXT:
                ann_id = self._make_id() if self._make_id else "local"
                ti = MetaTextItem(sp.x(), sp.y(), "Double-click to edit", ann_id, self._on_item_changed)
                self.addItem(ti)
                ti.setZValue(self._get_next_z_index())
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

    def _is_annotation_item(self, item: QGraphicsItem) -> bool:
        """Check if an item is one of our annotation items."""
        return isinstance(item, (MetaRectItem, MetaRoundedRectItem, MetaEllipseItem, MetaLineItem, MetaTextItem))

    def _get_annotation_items(self) -> List[QGraphicsItem]:
        """Get all annotation items in the scene (excluding background, etc.)."""
        return [item for item in self.items() if self._is_annotation_item(item)]

    def _get_next_z_index(self) -> float:
        """Get the next z-index for a new item (higher than all existing items)."""
        items = self._get_annotation_items()
        if not items:
            return Z_INDEX_BASE
        max_z = max(i.zValue() for i in items)
        return max_z + Z_INDEX_STEP

    def _show_context_menu(self, screen_pos, item: QGraphicsItem):
        """Show context menu for the selected item."""
        menu = QMenu()

        bring_to_front = QAction("Bring to Front", menu)
        bring_to_front.triggered.connect(lambda: self._bring_to_front(item))
        menu.addAction(bring_to_front)

        send_to_back = QAction("Send to Back", menu)
        send_to_back.triggered.connect(lambda: self._send_to_back(item))
        menu.addAction(send_to_back)

        # screenPos() returns QPoint in PyQt6
        menu.exec(screen_pos)

    def _bring_to_front(self, item: QGraphicsItem):
        """
        Bring the item to the front of all other annotation items.

        Resets all z-indices to make room and puts this item at the top.
        """
        items = self._get_annotation_items()
        if len(items) <= 1:
            return

        # Remove the target item from the list
        items = [i for i in items if i is not item]

        # Sort remaining items by current zValue (lowest first)
        items.sort(key=lambda i: i.zValue())

        # Reassign z-indices with gaps, starting from base
        for idx, i in enumerate(items):
            new_z = Z_INDEX_BASE + (idx * Z_INDEX_STEP)
            i.setZValue(new_z)

        # Put target item at the front (highest z)
        front_z = Z_INDEX_BASE + (len(items) * Z_INDEX_STEP)
        item.setZValue(front_z)

        # Notify that z-order changed
        if self._on_z_order_changed:
            self._on_z_order_changed()

    def _send_to_back(self, item: QGraphicsItem):
        """
        Send the item to the back of all other annotation items.

        Finds the backmost item and places this one behind it.
        If no room, resets all z-indices.
        """
        items = self._get_annotation_items()
        if len(items) <= 1:
            return

        # Find the minimum z-value among all items
        min_z = min(i.zValue() for i in items)

        # Try to place behind the backmost item
        new_z = min_z - Z_INDEX_STEP

        # If we would go too low, reset all z-indices
        if new_z < 0:
            # Remove the target item from the list
            other_items = [i for i in items if i is not item]

            # Sort remaining items by current zValue (lowest first)
            other_items.sort(key=lambda i: i.zValue())

            # Put target item at the back (lowest z)
            item.setZValue(Z_INDEX_BASE)

            # Reassign z-indices for other items with gaps
            for idx, i in enumerate(other_items):
                new_z = Z_INDEX_BASE + ((idx + 1) * Z_INDEX_STEP)
                i.setZValue(new_z)
        else:
            # Just set the new z-value
            item.setZValue(new_z)

        # Notify that z-order changed
        if self._on_z_order_changed:
            self._on_z_order_changed()
