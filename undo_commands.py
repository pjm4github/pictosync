"""
undo_commands.py

QUndoCommand implementations for undo/redo support in PictoSync.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

from PyQt6.QtCore import QPointF, QRectF, QLineF
from PyQt6.QtGui import QUndoCommand
from PyQt6.QtWidgets import QGraphicsItem

if TYPE_CHECKING:
    from canvas.scene import AnnotatorScene


# ---------------------------------------------------------------------------
# Geometry snapshot helpers
# ---------------------------------------------------------------------------

def capture_geometry(item) -> dict:
    """Capture a duck-typed geometry snapshot of an item.

    Returns a dict that can be passed to apply_geometry() to restore
    the item's position and shape.
    """
    pos = QPointF(item.pos())

    # MetaGroupItem — snapshot children
    if hasattr(item, '_capture_child_states'):
        return {"children": item._capture_child_states()}

    # Rect/Ellipse (have both setRect and rect)
    if hasattr(item, 'setRect') and hasattr(item, 'rect') and not hasattr(item, '_update_path'):
        return {"pos": pos, "rect": QRectF(item.rect())}

    # Path-based items with _width/_height (RoundedRect, Hexagon, Cylinder, BlockArrow, Polygon)
    if hasattr(item, '_width') and hasattr(item, '_update_path'):
        state = {"pos": pos, "width": item._width, "height": item._height}
        if hasattr(item, '_adjust1'):
            state["adjust1"] = item._adjust1
        if hasattr(item, '_adjust2'):
            state["adjust2"] = item._adjust2
        if hasattr(item, '_rel_points'):
            state["rel_points"] = [list(p) for p in item._rel_points]
        return state

    # Line (has setLine and line)
    if hasattr(item, 'setLine') and hasattr(item, 'line'):
        return {"pos": pos, "line": QLineF(item.line())}

    # Text/unknown — position only
    return {"pos": pos}


def apply_geometry(item, state: dict) -> None:
    """Restore an item's geometry from a snapshot dict.

    Sets geometry properties FIRST, then setPos() LAST so that
    itemChange(ItemPositionHasChanged) triggers _notify_changed()
    once at the end.
    """
    # Group — restore children
    if "children" in state:
        item._restore_child_states(state["children"])
        item._notify_changed()
        return

    # Rect/Ellipse
    if "rect" in state:
        item.setRect(state["rect"])
        item.setPos(state["pos"])
        return

    # Path-based items
    if "width" in state:
        item._width = state["width"]
        item._height = state["height"]
        if "adjust1" in state and hasattr(item, '_adjust1'):
            item._adjust1 = state["adjust1"]
        if "adjust2" in state and hasattr(item, '_adjust2'):
            item._adjust2 = state["adjust2"]
        if "rel_points" in state and hasattr(item, '_rel_points'):
            item._rel_points = [list(p) for p in state["rel_points"]]
        item._update_path()
        if hasattr(item, '_update_label_position'):
            item._update_label_position()
        item.setPos(state["pos"])
        return

    # Line
    if "line" in state:
        item.setLine(state["line"])
        item.setPos(state["pos"])
        return

    # Fallback — position only
    if "pos" in state:
        item.setPos(state["pos"])


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

class MoveItemCommand(QUndoCommand):
    """Command for moving an item."""

    def __init__(self, item: QGraphicsItem, old_pos: QPointF, new_pos: QPointF, parent=None):
        super().__init__(parent)
        self.item = item
        self.old_pos = old_pos
        self.new_pos = new_pos
        ann_id = getattr(item, 'ann_id', 'item')
        self.setText(f"Move {ann_id}")
        self._first_redo = True

    def undo(self):
        self.item.setPos(self.old_pos)

    def redo(self):
        if self._first_redo:
            self._first_redo = False
            return
        self.item.setPos(self.new_pos)


class ItemGeometryCommand(QUndoCommand):
    """Generic command for resize/endpoint-drag undo for all item types."""

    def __init__(self, item: QGraphicsItem, old_state: dict, new_state: dict, parent=None):
        super().__init__(parent)
        self.item = item
        self.old_state = old_state
        self.new_state = new_state
        ann_id = getattr(item, 'ann_id', 'item')
        self.setText(f"Resize {ann_id}")
        self._first_redo = True

    def undo(self):
        apply_geometry(self.item, self.old_state)

    def redo(self):
        if self._first_redo:
            self._first_redo = False
            return
        apply_geometry(self.item, self.new_state)


class TextEditCommand(QUndoCommand):
    """Command for text editing undo on MetaTextItem."""

    def __init__(self, item, old_text: str, new_text: str, parent=None):
        super().__init__(parent)
        self.item = item
        self.old_text = old_text
        self.new_text = new_text
        ann_id = getattr(item, 'ann_id', 'item')
        self.setText(f"Edit text {ann_id}")
        self._first_redo = True

    def undo(self):
        self.item.document().blockSignals(True)
        self.item.setPlainText(self.old_text)
        self.item.document().blockSignals(False)
        self.item.meta.note = self.old_text
        self.item._notify_changed()

    def redo(self):
        if self._first_redo:
            self._first_redo = False
            return
        self.item.document().blockSignals(True)
        self.item.setPlainText(self.new_text)
        self.item.document().blockSignals(False)
        self.item.meta.note = self.new_text
        self.item._notify_changed()


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
        self._first_redo = True

    def undo(self):
        setattr(self.item, self.property_name, self.old_value)
        if self.apply_func:
            self.apply_func()
        if hasattr(self.item, '_notify_changed'):
            self.item._notify_changed()

    def redo(self):
        if self._first_redo:
            self._first_redo = False
            return
        setattr(self.item, self.property_name, self.new_value)
        if self.apply_func:
            self.apply_func()
        if hasattr(self.item, '_notify_changed'):
            self.item._notify_changed()


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
        self._first_redo = True

    def undo(self):
        if hasattr(self.item, 'meta'):
            for key, value in self.old_meta.items():
                setattr(self.item.meta, key, value)
        if self.update_func:
            self.update_func()
        if hasattr(self.item, '_notify_changed'):
            self.item._notify_changed()

    def redo(self):
        if self._first_redo:
            self._first_redo = False
            return
        if hasattr(self.item, 'meta'):
            for key, value in self.new_meta.items():
                setattr(self.item.meta, key, value)
        if self.update_func:
            self.update_func()
        if hasattr(self.item, '_notify_changed'):
            self.item._notify_changed()


class GroupItemsCommand(QUndoCommand):
    """Command for grouping items together."""

    def __init__(self, scene: "AnnotatorScene", group_item, child_items: list,
                 on_grouped_callback=None, on_ungrouped_callback=None, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.group_item = group_item
        self.child_items = list(child_items)
        self.on_grouped_callback = on_grouped_callback
        self.on_ungrouped_callback = on_ungrouped_callback
        self.child_z_values = {item: item.zValue() for item in self.child_items}
        self.setText(f"Group {len(self.child_items)} items")
        self._first_redo = True

    def undo(self):
        # Remove children from group and restore flags
        for child in self.child_items:
            self.group_item.remove_member(child)
            child.setZValue(self.child_z_values.get(child, 0))
        self.scene.removeItem(self.group_item)
        if self.on_ungrouped_callback:
            self.on_ungrouped_callback(self.group_item, self.child_items)

    def redo(self):
        if self._first_redo:
            self._first_redo = False
            return
        self.scene.addItem(self.group_item)
        for child in self.child_items:
            self.group_item.add_member(child)
        if self.on_grouped_callback:
            self.on_grouped_callback(self.group_item, self.child_items)


class UngroupItemsCommand(QUndoCommand):
    """Command for ungrouping a group item."""

    def __init__(self, scene: "AnnotatorScene", group_item, child_items: list,
                 on_grouped_callback=None, on_ungrouped_callback=None, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.group_item = group_item
        self.child_items = list(child_items)
        self.on_grouped_callback = on_grouped_callback
        self.on_ungrouped_callback = on_ungrouped_callback
        self.group_z = group_item.zValue()
        self.setText(f"Ungroup {len(self.child_items)} items")
        self._first_redo = True

    def undo(self):
        # Re-group: add group back to scene and add children
        self.scene.addItem(self.group_item)
        self.group_item.setZValue(self.group_z)
        for child in self.child_items:
            self.group_item.add_member(child)
        if self.on_grouped_callback:
            self.on_grouped_callback(self.group_item, self.child_items)

    def redo(self):
        if self._first_redo:
            self._first_redo = False
            return
        # Remove children from group
        for child in self.child_items:
            self.group_item.remove_member(child)
        self.scene.removeItem(self.group_item)
        if self.on_ungrouped_callback:
            self.on_ungrouped_callback(self.group_item, self.child_items)
