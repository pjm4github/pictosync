"""Test bench for undo/redo commands.

Tests all 11 QUndoCommand implementations:
  - MoveItemCommand: move and undo restores position
  - ItemGeometryCommand: resize/reshape via capture/apply geometry
  - TextEditCommand: text change and undo restores old text
  - ResizeItemCommand: rect resize and undo restores old rect
  - AddItemCommand: add item, undo removes, redo re-adds
  - DeleteItemCommand: delete item, undo re-adds with z-value
  - DeleteMultipleItemsCommand: multi-delete and undo re-adds all
  - ChangeStyleCommand: style property change and undo restores
  - ChangeMetaCommand: metadata change and undo restores
  - GroupItemsCommand: group, undo ungroups
  - UngroupItemsCommand: ungroup, undo re-groups
  - capture_geometry / apply_geometry for multiple item types
  - First-redo skip behavior
  - Callback firing on add/delete/group/ungroup
"""
from __future__ import annotations

import pytest

from PyQt6.QtCore import QPointF, QRectF, QLineF
from PyQt6.QtGui import QColor, QUndoStack

from canvas.items import (
    MetaRectItem, MetaEllipseItem, MetaLineItem,
    MetaTextItem, MetaPolygonItem, MetaGroupItem,
    MetaRoundedRectItem,
)
from canvas.scene import AnnotatorScene
from undo_commands import (
    MoveItemCommand,
    ItemGeometryCommand,
    ResizeItemCommand,
    TextEditCommand,
    AddItemCommand,
    DeleteItemCommand,
    DeleteMultipleItemsCommand,
    ChangeStyleCommand,
    ChangeMetaCommand,
    GroupItemsCommand,
    UngroupItemsCommand,
    capture_geometry,
    apply_geometry,
)


# ── Helpers ──────────────────────────────────────────────────────────────

def _scene_with(*items):
    s = AnnotatorScene()
    for it in items:
        s.addItem(it)
    return s


# ── capture_geometry / apply_geometry ────────────────────────────────────

class TestCaptureApplyGeometry:

    def test_rect_capture(self):
        item = MetaRectItem(10, 20, 100, 50, "r1", None)
        state = capture_geometry(item)
        assert "pos" in state
        assert "rect" in state
        assert state["pos"].x() == 10
        assert state["rect"].width() == 100

    def test_rect_apply_restores(self):
        item = MetaRectItem(10, 20, 100, 50, "r1", None)
        state = capture_geometry(item)
        item.setPos(QPointF(999, 999))
        item.setRect(QRectF(0, 0, 1, 1))
        apply_geometry(item, state)
        assert abs(item.pos().x() - 10) < 0.1
        assert abs(item.rect().width() - 100) < 0.1

    def test_line_capture(self):
        item = MetaLineItem(10, 20, 200, 150, "l1", None)
        state = capture_geometry(item)
        assert "line" in state

    def test_line_apply_restores(self):
        item = MetaLineItem(10, 20, 200, 150, "l1", None)
        state = capture_geometry(item)
        old_line = QLineF(state["line"])
        item.setLine(QLineF(0, 0, 1, 1))
        apply_geometry(item, state)
        assert abs(item.line().x2() - old_line.x2()) < 0.1

    def test_path_item_capture(self):
        item = MetaRoundedRectItem(10, 20, 100, 50, 12, "rr1", None)
        state = capture_geometry(item)
        assert "width" in state
        assert "height" in state
        assert "adjust1" in state

    def test_polygon_capture_preserves_points(self):
        pts = [[0, 0], [1, 0], [0.5, 1]]
        item = MetaPolygonItem(10, 20, 100, 100, pts, "p1", None)
        state = capture_geometry(item)
        assert "rel_points" in state
        assert len(state["rel_points"]) == 3

    def test_text_capture_position_only(self):
        item = MetaTextItem(10, 20, "hello", "t1", None)
        state = capture_geometry(item)
        assert "pos" in state
        assert "rect" not in state
        assert "width" not in state


# ── MoveItemCommand ──────────────────────────────────────────────────────

class TestMoveItemCommand:

    def test_undo_restores_position(self):
        item = MetaRectItem(100, 200, 50, 30, "r1", None)
        old_pos = QPointF(100, 200)
        new_pos = QPointF(300, 400)
        item.setPos(new_pos)
        cmd = MoveItemCommand(item, old_pos, new_pos)
        cmd.undo()
        assert abs(item.pos().x() - 100) < 0.1
        assert abs(item.pos().y() - 200) < 0.1

    def test_redo_moves_again(self):
        item = MetaRectItem(100, 200, 50, 30, "r1", None)
        old_pos = QPointF(100, 200)
        new_pos = QPointF(300, 400)
        item.setPos(new_pos)
        cmd = MoveItemCommand(item, old_pos, new_pos)
        cmd.redo()  # first redo skipped
        cmd.undo()
        cmd.redo()  # second redo applies
        assert abs(item.pos().x() - 300) < 0.1

    def test_first_redo_skipped(self):
        item = MetaRectItem(100, 200, 50, 30, "r1", None)
        old_pos = QPointF(100, 200)
        new_pos = QPointF(300, 400)
        item.setPos(new_pos)
        cmd = MoveItemCommand(item, old_pos, new_pos)
        # First redo should be a no-op (item already moved)
        cmd.redo()
        assert abs(item.pos().x() - 300) < 0.1  # still at new_pos

    def test_command_text(self):
        item = MetaRectItem(0, 0, 50, 30, "r1", None)
        cmd = MoveItemCommand(item, QPointF(0, 0), QPointF(10, 10))
        assert "r1" in cmd.text()


# ── ItemGeometryCommand ──────────────────────────────────────────────────

class TestItemGeometryCommand:

    def test_undo_restores_rect_geometry(self):
        item = MetaRectItem(10, 20, 100, 50, "r1", None)
        old_state = capture_geometry(item)
        item.setRect(QRectF(0, 0, 200, 100))
        item.setPos(QPointF(50, 60))
        new_state = capture_geometry(item)
        cmd = ItemGeometryCommand(item, old_state, new_state)
        cmd.undo()
        assert abs(item.pos().x() - 10) < 0.1
        assert abs(item.rect().width() - 100) < 0.1

    def test_redo_reapplies_geometry(self):
        item = MetaRectItem(10, 20, 100, 50, "r1", None)
        old_state = capture_geometry(item)
        item.setRect(QRectF(0, 0, 200, 100))
        item.setPos(QPointF(50, 60))
        new_state = capture_geometry(item)
        cmd = ItemGeometryCommand(item, old_state, new_state)
        cmd.redo()  # first skip
        cmd.undo()
        cmd.redo()  # actual redo
        assert abs(item.pos().x() - 50) < 0.1


# ── ResizeItemCommand ────────────────────────────────────────────────────

class TestResizeItemCommand:

    def test_undo_restores_size(self):
        item = MetaRectItem(10, 20, 100, 50, "r1", None)
        old_pos = QPointF(10, 20)
        old_rect = QRectF(0, 0, 100, 50)
        new_pos = QPointF(5, 10)
        new_rect = QRectF(0, 0, 200, 80)
        item.setPos(new_pos)
        item.setRect(new_rect)
        cmd = ResizeItemCommand(item, old_pos, old_rect, new_pos, new_rect)
        cmd.undo()
        assert abs(item.rect().width() - 100) < 0.1
        assert abs(item.rect().height() - 50) < 0.1


# ── TextEditCommand ──────────────────────────────────────────────────────

class TestTextEditCommand:

    def test_undo_restores_text(self):
        item = MetaTextItem(10, 20, "old text", "t1", None)
        cmd = TextEditCommand(item, "old text", "new text")
        # Simulate the edit
        item.setPlainText("new text")
        item.meta.note = "new text"
        cmd.undo()
        assert item.toPlainText() == "old text"
        assert item.meta.note == "old text"


# ── AddItemCommand ───────────────────────────────────────────────────────

class TestAddItemCommand:

    def test_undo_removes_from_scene(self):
        item = MetaRectItem(10, 20, 100, 50, "r1", None)
        scene = _scene_with(item)
        assert item.scene() is scene
        cmd = AddItemCommand(scene, item)
        cmd.undo()
        assert item.scene() is None

    def test_redo_re_adds_to_scene(self):
        item = MetaRectItem(10, 20, 100, 50, "r1", None)
        scene = _scene_with(item)
        cmd = AddItemCommand(scene, item)
        cmd.redo()  # first skip
        cmd.undo()
        assert item.scene() is None
        cmd.redo()
        assert item.scene() is scene

    def test_callbacks_fired(self):
        added = []
        removed = []
        item = MetaRectItem(10, 20, 100, 50, "r1", None)
        scene = _scene_with(item)
        cmd = AddItemCommand(scene, item,
                             on_add_callback=lambda i: added.append(i),
                             on_remove_callback=lambda i: removed.append(i))
        cmd.redo()  # first redo skipped (item already added)
        cmd.undo()
        assert len(removed) == 1
        cmd.redo()  # second redo fires callback
        assert len(added) == 1


# ── DeleteItemCommand ────────────────────────────────────────────────────

class TestDeleteItemCommand:

    def test_redo_removes_from_scene(self):
        item = MetaRectItem(10, 20, 100, 50, "r1", None)
        scene = _scene_with(item)
        cmd = DeleteItemCommand(scene, item)
        cmd.redo()  # actually deletes
        assert item.scene() is None

    def test_undo_re_adds_to_scene(self):
        item = MetaRectItem(10, 20, 100, 50, "r1", None)
        item.setZValue(42)
        scene = _scene_with(item)
        cmd = DeleteItemCommand(scene, item)
        cmd.redo()
        cmd.undo()
        assert item.scene() is scene
        assert item.zValue() == 42

    def test_callbacks_fired(self):
        added = []
        removed = []
        item = MetaRectItem(10, 20, 100, 50, "r1", None)
        scene = _scene_with(item)
        cmd = DeleteItemCommand(scene, item,
                                on_add_callback=lambda i: added.append(i),
                                on_remove_callback=lambda i: removed.append(i))
        cmd.redo()
        assert len(removed) == 1
        cmd.undo()
        assert len(added) == 1


# ── DeleteMultipleItemsCommand ───────────────────────────────────────────

class TestDeleteMultipleItemsCommand:

    def test_redo_removes_all(self):
        r1 = MetaRectItem(10, 10, 50, 30, "r1", None)
        r2 = MetaRectItem(100, 10, 50, 30, "r2", None)
        scene = _scene_with(r1, r2)
        cmd = DeleteMultipleItemsCommand(scene, [r1, r2])
        cmd.redo()
        assert r1.scene() is None
        assert r2.scene() is None

    def test_undo_re_adds_all(self):
        r1 = MetaRectItem(10, 10, 50, 30, "r1", None)
        r1.setZValue(10)
        r2 = MetaRectItem(100, 10, 50, 30, "r2", None)
        r2.setZValue(20)
        scene = _scene_with(r1, r2)
        cmd = DeleteMultipleItemsCommand(scene, [r1, r2])
        cmd.redo()
        cmd.undo()
        assert r1.scene() is scene
        assert r2.scene() is scene
        assert r1.zValue() == 10
        assert r2.zValue() == 20


# ── ChangeStyleCommand ───────────────────────────────────────────────────

class TestChangeStyleCommand:

    def test_undo_restores_color(self):
        item = MetaRectItem(10, 20, 100, 50, "r1", None)
        old_color = QColor(item.pen_color)
        new_color = QColor(0, 255, 0)
        item.pen_color = new_color
        cmd = ChangeStyleCommand(item, "pen_color", old_color, new_color)
        cmd.undo()
        assert item.pen_color.red() == old_color.red()

    def test_redo_reapplies_color(self):
        item = MetaRectItem(10, 20, 100, 50, "r1", None)
        old_color = QColor(item.pen_color)
        new_color = QColor(0, 255, 0)
        item.pen_color = new_color
        cmd = ChangeStyleCommand(item, "pen_color", old_color, new_color)
        cmd.redo()  # first skip
        cmd.undo()
        cmd.redo()  # actual redo
        assert item.pen_color.green() == 255

    def test_apply_func_called(self):
        calls = []
        item = MetaRectItem(10, 20, 100, 50, "r1", None)
        cmd = ChangeStyleCommand(item, "pen_width", 1, 3,
                                  apply_func=lambda: calls.append(1))
        cmd.undo()
        assert len(calls) == 1


# ── ChangeMetaCommand ────────────────────────────────────────────────────

class TestChangeMetaCommand:

    def test_undo_restores_meta(self):
        item = MetaRectItem(10, 20, 100, 50, "r1", None)
        item.meta.halign = "left"
        cmd = ChangeMetaCommand(item, {"halign": "center"}, {"halign": "left"})
        cmd.undo()
        assert item.meta.halign == "center"

    def test_redo_reapplies_meta(self):
        item = MetaRectItem(10, 20, 100, 50, "r1", None)
        item.meta.halign = "left"
        cmd = ChangeMetaCommand(item, {"halign": "center"}, {"halign": "left"})
        cmd.redo()  # first skip
        cmd.undo()
        cmd.redo()  # actual redo
        assert item.meta.halign == "left"

    def test_update_func_called(self):
        calls = []
        item = MetaRectItem(10, 20, 100, 50, "r1", None)
        cmd = ChangeMetaCommand(item, {"wrap": True}, {"wrap": False},
                                 update_func=lambda: calls.append(1))
        cmd.undo()
        assert len(calls) == 1


# ── GroupItemsCommand ────────────────────────────────────────────────────

class TestGroupItemsCommand:

    def test_undo_ungroups(self):
        r1 = MetaRectItem(10, 10, 50, 30, "r1", None)
        r2 = MetaRectItem(100, 10, 50, 30, "r2", None)
        scene = _scene_with(r1, r2)
        group = MetaGroupItem("g1", None)
        scene.addItem(group)
        group.add_member(r1)
        group.add_member(r2)
        cmd = GroupItemsCommand(scene, group, [r1, r2])
        cmd.undo()
        assert group.scene() is None
        # Children should be back on scene as independent items
        assert r1.parentItem() is None
        assert r2.parentItem() is None

    def test_callbacks_fired(self):
        grouped = []
        ungrouped = []
        r1 = MetaRectItem(10, 10, 50, 30, "r1", None)
        scene = _scene_with(r1)
        group = MetaGroupItem("g1", None)
        scene.addItem(group)
        group.add_member(r1)
        cmd = GroupItemsCommand(scene, group, [r1],
                                 on_grouped_callback=lambda g, c: grouped.append(g),
                                 on_ungrouped_callback=lambda g, c: ungrouped.append(g))
        cmd.undo()
        assert len(ungrouped) == 1


# ── UngroupItemsCommand ─────────────────────────────────────────────────

class TestUngroupItemsCommand:

    def test_undo_regroups(self):
        r1 = MetaRectItem(10, 10, 50, 30, "r1", None)
        r2 = MetaRectItem(100, 10, 50, 30, "r2", None)
        scene = _scene_with(r1, r2)
        group = MetaGroupItem("g1", None)
        scene.addItem(group)
        group.add_member(r1)
        group.add_member(r2)
        # Simulate ungroup
        cmd = UngroupItemsCommand(scene, group, [r1, r2])
        cmd.redo()  # first skip
        # Manually ungroup for second redo test
        for c in [r1, r2]:
            group.remove_member(c)
        scene.removeItem(group)
        cmd.undo()
        # Group should be back
        assert group.scene() is scene


# ── QUndoStack integration ──────────────────────────────────────────────

class TestUndoStackIntegration:

    def test_push_and_undo(self):
        stack = QUndoStack()
        item = MetaRectItem(10, 20, 100, 50, "r1", None)
        old_pos = QPointF(10, 20)
        new_pos = QPointF(50, 60)
        item.setPos(new_pos)
        stack.push(MoveItemCommand(item, old_pos, new_pos))
        assert stack.canUndo()
        stack.undo()
        assert abs(item.pos().x() - 10) < 0.1

    def test_push_undo_redo(self):
        stack = QUndoStack()
        item = MetaRectItem(10, 20, 100, 50, "r1", None)
        old_pos = QPointF(10, 20)
        new_pos = QPointF(50, 60)
        item.setPos(new_pos)
        stack.push(MoveItemCommand(item, old_pos, new_pos))
        stack.undo()
        assert abs(item.pos().x() - 10) < 0.1
        stack.redo()
        assert abs(item.pos().x() - 50) < 0.1

    def test_multiple_commands(self):
        stack = QUndoStack()
        item = MetaRectItem(10, 20, 100, 50, "r1", None)
        # Move 1
        p0 = QPointF(10, 20)
        p1 = QPointF(50, 60)
        item.setPos(p1)
        stack.push(MoveItemCommand(item, p0, p1))
        # Move 2
        p2 = QPointF(200, 300)
        item.setPos(p2)
        stack.push(MoveItemCommand(item, p1, p2))
        # Undo both
        stack.undo()
        assert abs(item.pos().x() - 50) < 0.1
        stack.undo()
        assert abs(item.pos().x() - 10) < 0.1
        # Redo both
        stack.redo()
        assert abs(item.pos().x() - 50) < 0.1
        stack.redo()
        assert abs(item.pos().x() - 200) < 0.1
