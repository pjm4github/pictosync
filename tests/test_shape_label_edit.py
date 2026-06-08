"""
tests/test_shape_label_edit.py

In-place editing of shape labels via the shared EditableLabelItem /
InPlaceTextEditMixin.  A double-click on an enclosed shape routes editing to
its child label; the edit commits back into the owner shape's overlay-2.0
``meta.blocks`` and flows to the JSON editor and undo stack.
"""
from __future__ import annotations

import json

import pytest
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QFont, QTextCharFormat, QTextCursor

from canvas.items import (
    MetaRectItem,
    MetaRoundedRectItem,
    MetaEllipseItem,
    MetaHexagonItem,
    MetaCylinderItem,
    MetaBlockArrowItem,
    MetaPolygonItem,
    MetaIsoCubeItem,
)
from canvas.text_edit import EditableLabelItem


# (cls, ctor-args-before ann_id) for each enclosed shape.
SHAPES = {
    "rect":        (MetaRectItem,        (10, 10, 200, 100)),
    "roundedrect": (MetaRoundedRectItem, (10, 10, 200, 100, 0.2)),
    "ellipse":     (MetaEllipseItem,     (10, 10, 200, 100)),
    "hexagon":     (MetaHexagonItem,     (10, 10, 200, 100, 0.25)),
    "cylinder":    (MetaCylinderItem,    (10, 10, 200, 100, 0.15)),
    "blockarrow":  (MetaBlockArrowItem,  (10, 10, 200, 100, 0.3, 0.5)),
    "polygon":     (MetaPolygonItem,     (10, 10, 200, 100, [[0, 0], [1, 0], [0.5, 1]])),
    "isocube":     (MetaIsoCubeItem,     (10, 10, 200, 100, 0.2, 0.2)),
}


def _make(mw, qapp, kind):
    if mw._draft_data is None:
        mw._draft_data = {"version": "draft-1", "image": {}, "annotations": []}
    mw._link_enabled = True
    mw._rebuild_id_index()
    ann_id = mw._new_ann_id()
    cls, args = SHAPES[kind]
    item = cls(*args, ann_id, mw._on_scene_item_changed)
    mw.scene.addItem(item)
    qapp.processEvents()
    mw._on_new_scene_item(item)
    qapp.processEvents()
    return item, ann_id


def _ann(mw, ann_id):
    data = json.loads(mw.draft.get_json_text())
    for a in data.get("annotations", []):
        if isinstance(a, dict) and a.get("id") == ann_id:
            return a
    return None


@pytest.mark.parametrize("kind", list(SHAPES))
class TestShapeLabelEditing:
    def test_label_is_editable_item(self, main_window, qapp, kind):
        item, _ = _make(main_window, qapp, kind)
        assert isinstance(item._label_item, EditableLabelItem)

    def test_double_click_enters_edit(self, main_window, qapp, kind):
        item, _ = _make(main_window, qapp, kind)
        item._label_item._begin_edit_at(QPointF(20, 20))
        assert item._label_item._editing is True
        # Owner movement is frozen during text editing.
        assert not (item.flags() & item.GraphicsItemFlag.ItemIsMovable)

    def test_edit_commits_to_owner_blocks_and_json(self, main_window, qapp, kind):
        item, ann_id = _make(main_window, qapp, kind)
        lbl = item._label_item
        lbl._begin_edit_at(QPointF(20, 20))

        cur = lbl.textCursor()
        cur.select(QTextCursor.SelectionType.Document)
        cur.insertText("Service")
        # bold the whole word
        cur2 = lbl.textCursor()
        cur2.setPosition(0)
        cur2.setPosition(7, QTextCursor.MoveMode.KeepAnchor)
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Weight.Bold)
        cur2.mergeCharFormat(fmt)
        lbl.setTextCursor(cur2)

        lbl._commit_edit()
        qapp.processEvents()

        assert lbl._editing is False
        assert item.flags() & item.GraphicsItemFlag.ItemIsMovable  # restored
        assert item.meta.blocks[0].plain_text() == "Service"
        assert item.meta.blocks[0].runs[0].format.bold is True

        ann = _ann(main_window, ann_id)
        blocks = ann["contents"]["blocks"]
        assert "".join(r["text"] for b in blocks for r in b["runs"]) == "Service"
        assert blocks[0]["runs"][0]["format"]["bold"] is True
        assert "label" not in ann["contents"]  # blocks-only contract

    def test_undo_restores_label(self, main_window, qapp, kind):
        mw = main_window
        item, _ = _make(mw, qapp, kind)
        item.meta.label = "Before"
        item._update_label_text()

        lbl = item._label_item
        lbl._begin_edit_at(QPointF(20, 20))
        cur = lbl.textCursor()
        cur.select(QTextCursor.SelectionType.Document)
        cur.insertText("After")
        lbl._commit_edit()
        qapp.processEvents()
        assert item.meta.blocks[0].plain_text() == "After"

        mw.undo_stack.undo()
        qapp.processEvents()
        assert item.meta.blocks[0].plain_text() == "Before"

        mw.undo_stack.redo()
        qapp.processEvents()
        assert item.meta.blocks[0].plain_text() == "After"


class TestMiniToolbarOnShape:
    def test_toolbar_formats_shape_label(self, main_window, qapp):
        from PyQt6.QtCore import QPoint

        item, _ = _make(main_window, qapp, "rect")
        lbl = item._label_item
        lbl._begin_edit_at(QPointF(20, 20))
        cur = lbl.textCursor()
        cur.select(QTextCursor.SelectionType.Document)
        cur.insertText("Hello world")
        # select "world"
        cur = lbl.textCursor()
        cur.setPosition(6)
        cur.setPosition(11, QTextCursor.MoveMode.KeepAnchor)
        lbl.setTextCursor(cur)

        lbl._show_mini_toolbar(QPoint(10, 10))
        tb = lbl._mini_toolbar
        assert tb is not None and tb.isVisible()
        tb._btn_bold.setChecked(True)
        tb._toggle_bold()
        tb.hide()
        lbl._commit_edit()
        qapp.processEvents()

        runs = [(r.text, r.format) for b in item.meta.blocks for r in b.runs]
        assert [t for t, _ in runs] == ["Hello ", "world"]
        assert runs[1][1].bold


class TestPanelFormattingOnSelection:
    """Panel format controls drive the in-place canvas selection (the panel no
    longer hosts its own QTextEdit)."""

    def test_panel_bold_applies_to_selection_only_and_keeps_it(self, main_window, qapp):
        mw = main_window
        item, _ = _make(mw, qapp, "rect")
        mw.scene.clearSelection()
        item.setSelected(True)
        mw.props.set_item(item)
        qapp.processEvents()

        lbl = item._label_item
        lbl._begin_edit_at(QPointF(20, 20))
        cur = lbl.textCursor()
        cur.select(QTextCursor.SelectionType.Document)
        cur.insertText("Hello world")
        lbl.setTextCursor(cur)
        # select "world"
        cur = lbl.textCursor()
        cur.setPosition(6)
        cur.setPosition(11, QTextCursor.MoveMode.KeepAnchor)
        lbl.setTextCursor(cur)

        mw.props._on_bold_changed(True)
        qapp.processEvents()

        runs = [(r.text, bool(r.format and r.format.bold))
                for b in item.meta.blocks for r in b.runs]
        assert runs == [("Hello ", False), ("world", True)]   # only selection
        assert lbl.textCursor().selectedText() == "world"      # still selected
        assert lbl._editing is True                            # still editing

    def test_focusout_to_popup_keeps_editing(self, main_window, qapp):
        from PyQt6.QtGui import QFocusEvent
        mw = main_window
        item, _ = _make(mw, qapp, "rect")
        lbl = item._label_item
        lbl._begin_edit_at(QPointF(20, 20))
        # A combo dropdown / colour dialog opening must not end the edit.
        lbl.focusOutEvent(QFocusEvent(QFocusEvent.Type.FocusOut,
                                      Qt.FocusReason.PopupFocusReason))
        assert lbl._editing is True


class TestKeyboardDuringEdit:
    """While editing a label, keys belong to the document; Escape exits."""

    def test_arrow_moves_caret_not_shape(self, main_window, qapp):
        from PyQt6.QtGui import QKeyEvent
        from PyQt6.QtCore import QEvent
        mw = main_window
        item, _ = _make(mw, qapp, "rect")
        mw.scene.clearSelection(); item.setSelected(True)
        mw.props.set_item(item); qapp.processEvents()
        lbl = item._label_item
        lbl._begin_edit_at(QPointF(20, 20))
        cur = lbl.textCursor()
        cur.select(QTextCursor.SelectionType.Document)
        cur.insertText("Hello world")
        cur = lbl.textCursor(); cur.setPosition(11); lbl.setTextCursor(cur)
        pos_before = (item.pos().x(), item.pos().y())
        ev = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Left,
                       Qt.KeyboardModifier.NoModifier)
        mw.scene.keyPressEvent(ev)
        assert (item.pos().x(), item.pos().y()) == pos_before   # shape didn't move
        assert lbl.textCursor().position() == 10                 # caret moved left

    def test_escape_commits_and_selects_shape(self, main_window, qapp):
        from PyQt6.QtGui import QKeyEvent
        from PyQt6.QtCore import QEvent
        mw = main_window
        item, _ = _make(mw, qapp, "rect")
        lbl = item._label_item
        lbl._begin_edit_at(QPointF(20, 20))
        cur = lbl.textCursor(); cur.insertText("hi"); lbl.setTextCursor(cur)
        ev = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Escape,
                       Qt.KeyboardModifier.NoModifier)
        lbl.keyPressEvent(ev)
        assert lbl._editing is False
        assert item.isSelected() is True
        assert item.meta.blocks[0].plain_text() == "hi"   # committed
