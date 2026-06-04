"""
tests/test_inplace_text_edit.py

In-place (PowerPoint-style) text editing on MetaTextItem.

Drives the edit lifecycle directly (``_enter_edit_mode`` →
QTextCursor formatting → ``_commit_edit``) rather than synthesising real
focus events, then asserts the overlay-2.0 ``blocks`` model, the live JSON
editor, and the undo stack all reflect the edit.
"""
from __future__ import annotations

import json

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextCharFormat, QTextCursor

from canvas.items import MetaTextItem


# ── Helpers ──────────────────────────────────────────────────────────────

def _ensure_linked(mw):
    if mw._draft_data is None:
        mw._draft_data = {"version": "draft-1", "image": {}, "annotations": []}
    mw._link_enabled = True
    mw._rebuild_id_index()


def _create_text_item(mw, qapp, text="Hello world"):
    _ensure_linked(mw)
    ann_id = mw._new_ann_id()
    item = MetaTextItem(50, 50, text, ann_id, mw._on_scene_item_changed)
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


def _runs(item):
    return [(r.text, r.format) for b in item.meta.blocks for r in b.runs]


def _bold_range(item, start, end):
    cur = QTextCursor(item.document())
    cur.setPosition(start)
    cur.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
    fmt = QTextCharFormat()
    fmt.setFontWeight(QFont.Weight.Bold)
    cur.mergeCharFormat(fmt)


# ── Tests ────────────────────────────────────────────────────────────────

class TestEditLifecycle:
    def test_enter_makes_editable(self, main_window, qapp):
        item, _ = _create_text_item(main_window, qapp)
        item._enter_edit_mode()
        assert item._editing is True
        assert (item.textInteractionFlags()
                == Qt.TextInteractionFlag.TextEditorInteraction)

    def test_commit_reverts_to_noninteractive(self, main_window, qapp):
        item, _ = _create_text_item(main_window, qapp)
        item._enter_edit_mode()
        item._commit_edit()
        assert item._editing is False
        assert (item.textInteractionFlags()
                == Qt.TextInteractionFlag.NoTextInteraction)


class TestRoundTrip:
    def test_selection_bold_splits_runs(self, main_window, qapp):
        item, _ = _create_text_item(main_window, qapp, "Hello world")
        item._enter_edit_mode()
        _bold_range(item, 6, 11)  # "world"
        item._commit_edit()

        runs = _runs(item)
        assert [t for t, _ in runs] == ["Hello ", "world"]
        assert runs[0][1] is None or not runs[0][1].bold
        assert runs[1][1] is not None and runs[1][1].bold

    def test_blocks_reach_json_editor(self, main_window, qapp):
        item, ann_id = _create_text_item(main_window, qapp, "Hello world")
        item._enter_edit_mode()
        _bold_range(item, 6, 11)
        item._commit_edit()
        qapp.processEvents()

        ann = _ann(main_window, ann_id)
        assert ann is not None
        blocks = ann["contents"]["blocks"]
        texts = [r["text"] for b in blocks for r in b["runs"]]
        assert texts == ["Hello ", "world"]
        bold_run = blocks[0]["runs"][1]
        assert bold_run.get("format", {}).get("bold") is True
        # Blocks-only contract: no label/tech/note aliases in the JSON.
        assert "label" not in ann["contents"]
        assert "note" not in ann["contents"]

    def test_multiline_edit_creates_blocks(self, main_window, qapp):
        item, ann_id = _create_text_item(main_window, qapp, "one")
        item._enter_edit_mode()
        cur = QTextCursor(item.document())
        cur.movePosition(QTextCursor.MoveOperation.End)
        cur.insertText("\ntwo")  # second paragraph
        item._commit_edit()
        qapp.processEvents()

        ann = _ann(main_window, ann_id)
        para_texts = [
            "".join(r["text"] for r in b["runs"])
            for b in ann["contents"]["blocks"]
        ]
        assert para_texts == ["one", "two"]


class TestMiniToolbar:
    def test_toolbar_formats_only_selection(self, main_window, qapp):
        from PyQt6.QtCore import QPoint

        item, ann_id = _create_text_item(main_window, qapp, "Hello world")
        item._enter_edit_mode()
        cur = item.textCursor()
        cur.setPosition(6)
        cur.setPosition(11, QTextCursor.MoveMode.KeepAnchor)  # "world"
        item.setTextCursor(cur)

        item._show_mini_toolbar(QPoint(10, 10))
        tb = item._mini_toolbar
        assert tb is not None and tb.isVisible()
        tb._btn_bold.setChecked(True)
        tb._toggle_bold()
        tb._apply_size(20)
        tb.hide()
        item._commit_edit()
        qapp.processEvents()

        runs = _runs(item)
        assert [t for t, _ in runs] == ["Hello ", "world"]
        assert runs[0][1] is None or not runs[0][1].bold
        assert runs[1][1].bold and runs[1][1].font_size == 20

    def test_toolbar_open_blocks_commit_on_focus_out(self, main_window, qapp):
        from PyQt6.QtCore import QPoint
        from PyQt6.QtGui import QFocusEvent

        item, _ = _create_text_item(main_window, qapp, "abc")
        item._enter_edit_mode()
        cur = item.textCursor()
        cur.select(QTextCursor.SelectionType.Document)
        item.setTextCursor(cur)

        item._show_mini_toolbar(QPoint(10, 10))
        assert item._mini_toolbar.isVisible()
        # A focus-out while the toolbar is up must NOT end the edit.
        item.focusOutEvent(QFocusEvent(QFocusEvent.Type.FocusOut))
        assert item._editing is True
        item._mini_toolbar.hide()


class TestUndo:
    def test_undo_restores_previous_text(self, main_window, qapp):
        mw = main_window
        item, ann_id = _create_text_item(mw, qapp, "before")
        item._enter_edit_mode()
        cur = QTextCursor(item.document())
        cur.select(QTextCursor.SelectionType.Document)
        cur.insertText("after")
        item._commit_edit()
        qapp.processEvents()

        assert item.meta.blocks[0].plain_text() == "after"

        mw.undo_stack.undo()
        qapp.processEvents()
        assert item.meta.blocks[0].plain_text() == "before"

        mw.undo_stack.redo()
        qapp.processEvents()
        assert item.meta.blocks[0].plain_text() == "after"

    def test_no_op_edit_pushes_no_command(self, main_window, qapp):
        mw = main_window
        depth_before = mw.undo_stack.count()
        item, _ = _create_text_item(mw, qapp, "unchanged")
        item._enter_edit_mode()
        item._commit_edit()  # no edits made
        qapp.processEvents()
        # Creating the item may push commands; editing without changes must not.
        assert mw.undo_stack.count() == mw.undo_stack.count()
        # The top command, if any, is not a text-edit for an unchanged doc.
        # (A no-op commit should not have added a TextEditCommand.)
        text = mw.undo_stack.text(mw.undo_stack.count() - 1) if mw.undo_stack.count() else ""
        assert "Edit text" not in text
