"""
tests/test_seqblock_label_edit.py

In-place editing of MetaSeqBlockItem region labels.

A sequence block's regions are plain-text segments of the pipe-separated
``meta.tech`` field (rendered as italic ``[text]``), so each region uses the
lightweight EditableSectionItem editor: double-click a region, edit its raw
text, and the segment commits back into ``meta.tech``.
"""
from __future__ import annotations

import json

import pytest
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QTextCursor

from canvas.items import MetaSeqBlockItem
from canvas.text_edit import EditableSectionItem


def _make(mw, qapp, block_type="alt"):
    if mw._draft_data is None:
        mw._draft_data = {"version": "draft-1", "image": {}, "annotations": []}
    mw._link_enabled = True
    mw._rebuild_id_index()
    aid = mw._new_ann_id()
    it = MetaSeqBlockItem(0, 0, 200, 160, block_type, aid, mw._on_scene_item_changed)
    mw.scene.addItem(it)
    qapp.processEvents()
    mw._on_new_scene_item(it)
    qapp.processEvents()
    return it, aid


def _ann(mw, aid):
    data = json.loads(mw.draft.get_json_text())
    for a in data.get("annotations", []):
        if isinstance(a, dict) and a.get("id") == aid:
            return a
    return None


class _DblClick:
    def __init__(self, pos):
        self._pos = pos

    def button(self):
        return Qt.MouseButton.LeftButton

    def pos(self):
        return self._pos

    def accept(self):
        pass


class TestSeqBlockSectionEditing:
    def test_sections_are_editable_items(self, main_window, qapp):
        it, _ = _make(main_window, qapp)
        assert all(isinstance(s, EditableSectionItem) for s in it._section_items)

    def test_region_index_by_y(self, main_window, qapp):
        it, _ = _make(main_window, qapp)  # alt → 1 divider at adjust1*h = 0.5*160 = 80
        assert it._divider_count == 1
        assert it._section_index_at(30) == 0
        assert it._section_index_at(120) == 1

    def test_double_click_edits_region_to_tech(self, main_window, qapp):
        it, aid = _make(main_window, qapp)
        it.meta.tech = "cond|else"
        it._update_label_text()
        qapp.processEvents()

        # double-click the lower region (below the divider) → region index 1
        it.mouseDoubleClickEvent(_DblClick(QPointF(50, 120)))
        sec = it._section_items[1]
        assert sec._editing is True
        # owner movement frozen during edit
        assert not (it.flags() & it.GraphicsItemFlag.ItemIsMovable)

        cur = sec.textCursor()
        cur.select(QTextCursor.SelectionType.Document)
        cur.insertText("otherwise")
        sec._commit()
        qapp.processEvents()

        assert sec._editing is False
        assert it.flags() & it.GraphicsItemFlag.ItemIsMovable  # restored
        assert it._sections() == ["cond", "otherwise"]
        # tech round-trips to JSON (blocks-only contract; tech is block 1 text)
        ann = _ann(main_window, aid)
        from models import AnnotationContents
        assert AnnotationContents.from_dict(ann["contents"]).tech == "cond|otherwise"

    def test_edit_first_region(self, main_window, qapp):
        it, _ = _make(main_window, qapp)
        it.meta.tech = "a|b"
        it._update_label_text()
        it.mouseDoubleClickEvent(_DblClick(QPointF(50, 20)))  # region 0
        sec = it._section_items[0]
        cur = sec.textCursor()
        cur.select(QTextCursor.SelectionType.Document)
        cur.insertText("x>0")
        sec._commit()
        qapp.processEvents()
        assert it._sections() == ["x>0", "b"]

    def test_undo_restores_section(self, main_window, qapp):
        mw = main_window
        it, _ = _make(mw, qapp)
        it.meta.tech = "before|keep"
        it._update_label_text()

        it.mouseDoubleClickEvent(_DblClick(QPointF(50, 20)))
        sec = it._section_items[0]
        cur = sec.textCursor()
        cur.select(QTextCursor.SelectionType.Document)
        cur.insertText("after")
        sec._commit()
        qapp.processEvents()
        assert it._sections() == ["after", "keep"]

        mw.undo_stack.undo()
        qapp.processEvents()
        assert it._sections() == ["before", "keep"]

        mw.undo_stack.redo()
        qapp.processEvents()
        assert it._sections() == ["after", "keep"]

    def test_noop_edit_pushes_no_command(self, main_window, qapp):
        mw = main_window
        it, _ = _make(mw, qapp)
        it.meta.tech = "same|two"
        it._update_label_text()
        before = mw.undo_stack.count()
        it.mouseDoubleClickEvent(_DblClick(QPointF(50, 20)))
        sec = it._section_items[0]
        # commit without changing the text
        sec._commit()
        qapp.processEvents()
        assert mw.undo_stack.count() == before
        # region returns to its bracketed display
        assert it._sections() == ["same", "two"]
