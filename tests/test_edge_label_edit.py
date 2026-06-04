"""
tests/test_edge_label_edit.py

In-place editing of edge labels on lines and curves.

Lines have no competing double-click action, so they use the parent
``LabelEditableMixin`` routing.  Curves and polygons already bind
double-click to node/vertex editing, so they hit-test the label region
(``label_hit_at``) inside their existing handler and only edit the label
when the double-click lands on it — otherwise the node/vertex toggle wins.
"""
from __future__ import annotations

import json

import pytest
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QFont, QTextCharFormat, QTextCursor

from canvas.items import (
    MetaLineItem,
    MetaCurveItem,
    MetaOrthoCurveItem,
    MetaPolygonItem,
)
from canvas.text_edit import EditableLabelItem, label_hit_at


def _link(mw):
    if mw._draft_data is None:
        mw._draft_data = {"version": "draft-1", "image": {}, "annotations": []}
    mw._link_enabled = True
    mw._rebuild_id_index()


def _add(mw, qapp, item):
    mw.scene.addItem(item)
    qapp.processEvents()
    mw._on_new_scene_item(item)
    qapp.processEvents()


def _ann(mw, ann_id):
    data = json.loads(mw.draft.get_json_text())
    for a in data.get("annotations", []):
        if isinstance(a, dict) and a.get("id") == ann_id:
            return a
    return None


def _make_line(mw, qapp):
    _link(mw)
    aid = mw._new_ann_id()
    it = MetaLineItem(0, 0, 200, 0, aid, mw._on_scene_item_changed)
    _add(mw, qapp, it)
    return it, aid


def _make_curve(mw, qapp, cls=MetaCurveItem):
    _link(mw)
    aid = mw._new_ann_id()
    nodes = [{"cmd": "M", "x": 0, "y": 0}, {"cmd": "L", "x": 1, "y": 1}]
    if cls is MetaOrthoCurveItem:
        nodes = [{"cmd": "M", "x": 0, "y": 0}, {"cmd": "H", "x": 1},
                 {"cmd": "V", "y": 1}]
    it = cls(0, 0, 200, 100, nodes, aid, mw._on_scene_item_changed)
    _add(mw, qapp, it)
    return it, aid


class TestLineLabel:
    def test_label_is_editable(self, main_window, qapp):
        it, _ = _make_line(main_window, qapp)
        assert isinstance(it._label_item, EditableLabelItem)

    def test_double_click_edits_label(self, main_window, qapp):
        # Lines route double-click via the parent mixin (no conflict).
        it, aid = _make_line(main_window, qapp)
        it.mouseDoubleClickEvent(_DummyDblClick(QPointF(100, 0)))
        assert it._label_item._editing is True
        cur = it._label_item.textCursor()
        cur.insertText("CT/VT sec")
        it._label_item._commit_edit()
        qapp.processEvents()
        assert it.meta.blocks[0].plain_text() == "CT/VT sec"
        ann = _ann(main_window, aid)
        blocks = ann["contents"]["blocks"]
        assert "".join(r["text"] for b in blocks for r in b["runs"]) == "CT/VT sec"


@pytest.mark.parametrize("cls", [MetaCurveItem, MetaOrthoCurveItem])
class TestCurveLabel:
    def test_label_is_editable(self, main_window, qapp, cls):
        it, _ = _make_curve(main_window, qapp, cls)
        assert isinstance(it._label_item, EditableLabelItem)

    def test_node_toggle_preserved_off_label(self, main_window, qapp, cls):
        it, _ = _make_curve(main_window, qapp, cls)
        assert it._node_editing is False
        # Double-click far from the label toggles node editing, not text.
        it.mouseDoubleClickEvent(_DummyDblClick(QPointF(1000, 1000)))
        assert it._node_editing is True
        assert it._label_item._editing is False

    def test_double_click_on_label_edits(self, main_window, qapp, cls):
        it, aid = _make_curve(main_window, qapp, cls)
        it.meta.label = "flow"
        it._update_label_text()
        qapp.processEvents()
        pos = it._label_item.pos()
        assert label_hit_at(it._label_item, pos)
        it.mouseDoubleClickEvent(_DummyDblClick(pos))
        assert it._label_item._editing is True
        assert it._node_editing is False
        cur = it._label_item.textCursor()
        cur.select(QTextCursor.SelectionType.Document)
        cur.insertText("GOOSE trip")
        it._label_item._commit_edit()
        qapp.processEvents()
        assert it.meta.blocks[0].plain_text() == "GOOSE trip"


class TestPolygonLabel:
    def test_double_click_on_label_edits_not_vertex(self, main_window, qapp):
        _link(main_window)
        aid = main_window._new_ann_id()
        it = MetaPolygonItem(0, 0, 200, 100, [[0, 0], [1, 0], [0.5, 1]],
                             aid, main_window._on_scene_item_changed)
        _add(main_window, qapp, it)
        it.meta.label = "poly"
        it._update_label_text()
        qapp.processEvents()
        pos = it._label_item.pos()
        it.mouseDoubleClickEvent(_DummyDblClick(pos))
        assert it._label_item._editing is True
        assert it._vertex_editing is False


class _DummyDblClick:
    """Minimal stand-in for QGraphicsSceneMouseEvent double-click."""

    def __init__(self, pos: QPointF):
        self._pos = pos
        self._accepted = False

    def button(self):
        return Qt.MouseButton.LeftButton

    def pos(self):
        return self._pos

    def scenePos(self):
        return QPointF(99999, 99999)  # never near vertices/nodes

    def accept(self):
        self._accepted = True

    def ignore(self):
        self._accepted = False
