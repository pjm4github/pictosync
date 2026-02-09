"""
undo_commands.py

QUndoCommand implementations for undo/redo support in PictoSync.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QUndoCommand
from PyQt6.QtWidgets import QGraphicsItem

if TYPE_CHECKING:
    from canvas.scene import AnnotatorScene


class MoveItemCommand(QUndoCommand):
    """Command for moving an item."""

    def __init__(self, item: QGraphicsItem, old_pos: QPointF, new_pos: QPointF, parent=None):
        super().__init__(parent)
        self.item = item
        self.old_pos = old_pos
        self.new_pos = new_pos
        ann_id = getattr(item, 'ann_id', 'item')
        self.setText(f"Move {ann_id}")

    def undo(self):
        self.item.setPos(self.old_pos)

    def redo(self):
        self.item.setPos(self.new_pos)


class ResizeItemCommand(QUndoCommand):
    """Command for resizing a rect/ellipse item."""

    def __init__(self, item: QGraphicsItem, old_pos: QPointF, old_rect: QRectF,
                 new_pos: QPointF, new_rect: QRectF, parent=None):
        super().__init__(parent)
        self.item = item
        self.old_pos = old_pos
        self.old_rect = old_rect
        self.new_pos = new_pos
        self.new_rect = new_rect
        ann_id = getattr(item, 'ann_id', 'item')
        self.setText(f"Resize {ann_id}")

    def undo(self):
        self.item.setPos(self.old_pos)
        if hasattr(self.item, 'setRect'):
            self.item.setRect(self.old_rect)

    def redo(self):
        self.item.setPos(self.new_pos)
        if hasattr(self.item, 'setRect'):
            self.item.setRect(self.new_rect)


class AddItemCommand(QUndoCommand):
    """Command for adding an item to the scene."""

    def __init__(self, scene: "AnnotatorScene", item: QGraphicsItem,
                 on_add_callback=None, on_remove_callback=None, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.item = item
        self.on_add_callback = on_add_callback
        self.on_remove_callback = on_remove_callback
        ann_id = getattr(item, 'ann_id', 'item')
        kind = getattr(getattr(item, 'meta', None), 'kind', 'item')
        self.setText(f"Add {kind} {ann_id}")
        self._first_redo = True

    def undo(self):
        self.scene.removeItem(self.item)
        if self.on_remove_callback:
            self.on_remove_callback(self.item)

    def redo(self):
        if self._first_redo:
            # Item was already added when command was created
            self._first_redo = False
            return
        self.scene.addItem(self.item)
        if self.on_add_callback:
            self.on_add_callback(self.item)


class DeleteItemCommand(QUndoCommand):
    """Command for deleting an item from the scene."""

    def __init__(self, scene: "AnnotatorScene", item: QGraphicsItem,
                 on_add_callback=None, on_remove_callback=None, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.item = item
        self.on_add_callback = on_add_callback
        self.on_remove_callback = on_remove_callback
        self.z_value = item.zValue()
        ann_id = getattr(item, 'ann_id', 'item')
        kind = getattr(getattr(item, 'meta', None), 'kind', 'item')
        self.setText(f"Delete {kind} {ann_id}")

    def undo(self):
        self.scene.addItem(self.item)
        self.item.setZValue(self.z_value)
        if self.on_add_callback:
            self.on_add_callback(self.item)

    def redo(self):
        self.scene.removeItem(self.item)
        if self.on_remove_callback:
            self.on_remove_callback(self.item)


class DeleteMultipleItemsCommand(QUndoCommand):
    """Command for deleting multiple items from the scene."""

    def __init__(self, scene: "AnnotatorScene", items: list,
                 on_add_callback=None, on_remove_callback=None, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.items = list(items)  # Copy the list
        self.on_add_callback = on_add_callback
        self.on_remove_callback = on_remove_callback
        # Store z-values for restoration
        self.z_values = {item: item.zValue() for item in self.items}
        self.setText(f"Delete {len(self.items)} items")

    def undo(self):
        for item in self.items:
            self.scene.addItem(item)
            item.setZValue(self.z_values[item])
            if self.on_add_callback:
                self.on_add_callback(item)

    def redo(self):
        for item in self.items:
            self.scene.removeItem(item)
            if self.on_remove_callback:
                self.on_remove_callback(item)


class ChangeStyleCommand(QUndoCommand):
    """Command for changing item style properties."""

    def __init__(self, item: QGraphicsItem, property_name: str,
                 old_value: Any, new_value: Any, apply_func=None, parent=None):
        super().__init__(parent)
        self.item = item
        self.property_name = property_name
        self.old_value = old_value
        self.new_value = new_value
        self.apply_func = apply_func
        ann_id = getattr(item, 'ann_id', 'item')
        self.setText(f"Change {property_name} of {ann_id}")

    def undo(self):
        setattr(self.item, self.property_name, self.old_value)
        if self.apply_func:
            self.apply_func()

    def redo(self):
        setattr(self.item, self.property_name, self.new_value)
        if self.apply_func:
            self.apply_func()


class ChangeMetaCommand(QUndoCommand):
    """Command for changing item metadata."""

    def __init__(self, item: QGraphicsItem, old_meta: Dict[str, Any],
                 new_meta: Dict[str, Any], update_func=None, parent=None):
        super().__init__(parent)
        self.item = item
        self.old_meta = old_meta
        self.new_meta = new_meta
        self.update_func = update_func
        ann_id = getattr(item, 'ann_id', 'item')
        self.setText(f"Change metadata of {ann_id}")

    def undo(self):
        if hasattr(self.item, 'meta'):
            for key, value in self.old_meta.items():
                setattr(self.item.meta, key, value)
        if self.update_func:
            self.update_func()

    def redo(self):
        if hasattr(self.item, 'meta'):
            for key, value in self.new_meta.items():
                setattr(self.item.meta, key, value)
        if self.update_func:
            self.update_func()
