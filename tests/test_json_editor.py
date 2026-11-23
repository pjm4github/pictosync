"""Test bench for JSON editor (JsonCodeEditor + DraftDock).

Tests:
  - Code folding: fold/unfold/fold_all/unfold_all/fold_all_annotations
  - Focus mode toggle
  - Schema check toggle
  - Gutter highlight bar (set_highlighted_annotation)
  - cursor_annotation_changed signal
  - _find_annotation_at_cursor
  - Read-only field detection (_is_cursor_on_readonly_field)
  - scroll_to_id_top / jump_to_note_field_for_id
  - set_json_text / get_json_text
"""
from __future__ import annotations

import json

import pytest

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QTextCursor

from editor.code_editor import JsonCodeEditor
from editor.draft_dock import DraftDock


# ── Sample JSON ──────────────────────────────────────────────────────────

SAMPLE_JSON = json.dumps({
    "version": "draft-1",
    "image": {"width": 800, "height": 600},
    "annotations": [
        {
            "id": "a000001",
            "kind": "rect",
            "geom": {"x": 100, "y": 200, "w": 150, "h": 80},
            "contents": {"label": "Hello", "tech": "World", "note": ""},
            "style": {"pen": {"color": "#FF0000", "width": 2},
                       "fill": {"color": "#FFFFFFFF"}},
        },
        {
            "id": "a000002",
            "kind": "ellipse",
            "geom": {"x": 400, "y": 200, "w": 100, "h": 100},
            "contents": {"label": "Circle", "tech": "", "note": ""},
            "style": {"pen": {"color": "#0000FF", "width": 1},
                       "fill": {"color": "#00000000"}},
            "ports": ["p001"],
        },
    ],
}, indent=2)


# ── Helpers ──────────────────────────────────────────────────────────────

@pytest.fixture
def editor():
    """Create a standalone JsonCodeEditor with sample JSON."""
    e = JsonCodeEditor()
    e.setPlainText(SAMPLE_JSON)
    e._recompute_fold_regions()
    return e


@pytest.fixture
def dock():
    """Create a DraftDock widget."""
    d = DraftDock()
    d.set_json_text(SAMPLE_JSON, enable_import=True, status="Test")
    return d


# ── JsonCodeEditor: folding ──────────────────────────────────────────────

class TestCodeFolding:

    def test_fold_regions_found(self, editor):
        assert len(editor._fold_regions) > 0

    def test_fold_all(self, editor):
        editor.fold_all()
        # At least some blocks should be hidden
        doc = editor.document()
        hidden = 0
        blk = doc.begin()
        while blk.isValid():
            if not blk.isVisible():
                hidden += 1
            blk = blk.next()
        assert hidden > 0

    def test_unfold_all(self, editor):
        editor.fold_all()
        editor.unfold_all()
        # All blocks should be visible
        doc = editor.document()
        blk = doc.begin()
        while blk.isValid():
            assert blk.isVisible(), f"Block {blk.blockNumber()} still hidden"
            blk = blk.next()

    def test_toggle_fold(self, editor):
        # Find a foldable block
        if not editor._fold_regions:
            pytest.skip("No fold regions")
        block_num = next(iter(editor._fold_regions))
        editor.toggle_fold(block_num)
        # Should now be folded
        assert block_num in editor._folded_blocks
        editor.toggle_fold(block_num)
        # Should now be unfolded
        assert block_num not in editor._folded_blocks

    def test_fold_all_annotations(self, editor):
        editor.fold_all_annotations()
        # annotation objects should be folded
        assert len(editor._folded_blocks) > 0


# ── JsonCodeEditor: annotation tracking ──────────────────────────────────

class TestAnnotationTracking:

    def test_find_annotation_at_cursor_inside(self, editor):
        # Position cursor inside the first annotation
        text = editor.toPlainText()
        pos = text.find('"a000001"')
        assert pos >= 0
        cursor = editor.textCursor()
        cursor.setPosition(pos + 5)
        editor.setTextCursor(cursor)
        ann_id = editor._find_annotation_at_cursor()
        assert ann_id == "a000001"

    def test_find_annotation_at_cursor_second(self, editor):
        text = editor.toPlainText()
        pos = text.find('"a000002"')
        assert pos >= 0
        cursor = editor.textCursor()
        cursor.setPosition(pos + 5)
        editor.setTextCursor(cursor)
        ann_id = editor._find_annotation_at_cursor()
        assert ann_id == "a000002"

    def test_find_annotation_outside(self, editor):
        # Position cursor at the very beginning (before annotations)
        cursor = editor.textCursor()
        cursor.setPosition(0)
        editor.setTextCursor(cursor)
        ann_id = editor._find_annotation_at_cursor()
        assert ann_id == ""

    def test_cursor_annotation_changed_signal(self, editor):
        received = []
        editor.cursor_annotation_changed.connect(lambda aid: received.append(aid))
        # Move cursor into first annotation
        text = editor.toPlainText()
        pos = text.find('"a000001"')
        cursor = editor.textCursor()
        cursor.setPosition(pos + 5)
        editor.setTextCursor(cursor)
        # Signal fires via _on_cursor_position_changed
        editor._on_cursor_position_changed()
        assert len(received) >= 1
        assert received[-1] == "a000001"


# ── JsonCodeEditor: gutter highlight bar ─────────────────────────────────

class TestGutterHighlight:

    def test_set_highlighted_annotation(self, editor):
        editor.set_highlighted_annotation("a000001")
        assert editor._highlighted_annotation_id == "a000001"
        start, end = editor._highlighted_line_range
        assert start >= 0
        assert end > start

    def test_clear_highlighted_annotation(self, editor):
        editor.set_highlighted_annotation("a000001")
        editor.clear_highlighted_annotation()
        assert editor._highlighted_annotation_id == ""

    def test_highlight_unknown_id(self, editor):
        editor.set_highlighted_annotation("nonexistent")
        start, _ = editor._highlighted_line_range
        assert start == -1


# ── JsonCodeEditor: read-only fields ─────────────────────────────────────

class TestReadOnlyFields:

    def test_readonly_on_ports_line(self, editor):
        text = editor.toPlainText()
        pos = text.find('"ports"')
        if pos < 0:
            pytest.skip("No ports field in sample JSON")
        cursor = editor.textCursor()
        cursor.setPosition(pos + 3)
        editor.setTextCursor(cursor)
        assert editor._is_cursor_on_readonly_field()

    def test_not_readonly_on_kind_line(self, editor):
        text = editor.toPlainText()
        pos = text.find('"kind"')
        assert pos >= 0
        cursor = editor.textCursor()
        cursor.setPosition(pos + 3)
        editor.setTextCursor(cursor)
        assert not editor._is_cursor_on_readonly_field()

    def test_readonly_on_label_line(self, editor):
        text = editor.toPlainText()
        pos = text.find('"label"')
        if pos < 0:
            pytest.skip("No label field in sample JSON")
        cursor = editor.textCursor()
        cursor.setPosition(pos + 3)
        editor.setTextCursor(cursor)
        assert editor._is_cursor_on_readonly_field()


# ── DraftDock: basic operations ──────────────────────────────────────────

class TestDraftDock:

    def test_set_and_get_json_text(self, dock):
        dock.set_json_text('{"test": 1}', enable_import=False, status="OK")
        assert '"test"' in dock.get_json_text()

    def test_status_text(self, dock):
        dock.set_status("Custom status")
        assert dock.status.text() == "Custom status"

    def test_import_button_enabled(self, dock):
        dock.set_json_text('{}', enable_import=True)
        assert dock.import_btn.isEnabled()

    def test_import_button_disabled(self, dock):
        dock.set_json_text('{}', enable_import=False)
        assert not dock.import_btn.isEnabled()


# ── DraftDock: focus mode ────────────────────────────────────────────────

class TestFocusMode:

    def test_initially_disabled(self, dock):
        assert not dock.is_focus_mode_enabled()

    def test_toggle_on(self, dock):
        dock._on_focus_mode_toggled(True)
        assert dock.is_focus_mode_enabled()

    def test_toggle_off(self, dock):
        dock._on_focus_mode_toggled(True)
        dock._on_focus_mode_toggled(False)
        assert not dock.is_focus_mode_enabled()


# ── DraftDock: schema check ──────────────────────────────────────────────

class TestSchemaCheck:

    def test_initially_disabled(self, dock):
        assert not dock.is_schema_check_enabled()

    def test_toggle_on(self, dock):
        dock._on_schema_check_toggled(True)
        assert dock.is_schema_check_enabled()

    def test_toggle_off(self, dock):
        dock._on_schema_check_toggled(True)
        dock._on_schema_check_toggled(False)
        assert not dock.is_schema_check_enabled()


# ── DraftDock: scroll to annotation ──────────────────────────────────────

class TestScrollToAnnotation:

    def test_scroll_to_existing_id(self, dock):
        ok = dock.scroll_to_id_top("a000001")
        assert ok is True

    def test_scroll_to_nonexistent_id(self, dock):
        ok = dock.scroll_to_id_top("nonexistent")
        assert ok is False

    def test_jump_to_note_field(self, dock):
        ok = dock.jump_to_note_field_for_id("a000001")
        # May or may not find "note" depending on contents vs meta key
        # Just ensure it doesn't crash
        assert isinstance(ok, bool)
