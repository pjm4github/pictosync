"""Test that the JSON editor scroll position stays frozen during canvas drag.

Requires a GUI environment (not headless).  Run with:
    .venv/Scripts/python -m pytest tests/test_scroll_preservation.py -v
"""
from __future__ import annotations

import json
import os
import sys

import pytest
from PyQt6.QtCore import QPointF, QTimer
from PyQt6.QtWidgets import QApplication

# Ensure project root is on sys.path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from settings import SettingsManager


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def qapp():
    """Provide a single QApplication for the entire test session."""
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


@pytest.fixture()
def main_window(qapp):
    """Create a fresh MainWindow for each test."""
    from main import MainWindow
    sm = SettingsManager()
    mw = MainWindow(sm)
    mw.show()
    qapp.processEvents()
    yield mw
    mw.close()


@pytest.fixture()
def linked_scene(main_window, qapp):
    """Import a PUML file and link items, returning (main_window, items)."""
    puml_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "test_data", "PUML", "test_seq1.puml")
    )
    if not os.path.exists(puml_path):
        pytest.skip(f"Test fixture not found: {puml_path}")

    main_window._import_puml(puml_path)
    main_window.import_draft_and_link()
    qapp.processEvents()

    items = [i for i in main_window.scene.items() if hasattr(i, "ann_id")]
    assert len(items) > 0, "No linked items after import"
    return main_window, items


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_annotation(data: dict, ann_id: str) -> dict | None:
    """Find an annotation by ID, including inside groups."""
    for a in data.get("annotations", []):
        if a.get("id") == ann_id:
            return a
        for c in a.get("children", []):
            if c.get("id") == ann_id:
                return c
    return None


def _select_and_scroll(mw, item, qapp):
    """Select an item and let the deferred scroll settle."""
    item.setSelected(True)
    qapp.processEvents()
    ann_id = item.ann_id
    mw._scroll_draft_to_id_top(ann_id)
    # Let QTimer.singleShot(0) deferred scrolls complete
    qapp.processEvents()
    qapp.processEvents()
    return ann_id


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestScrollPreservationDuringDrag:
    """Scroll position must not change while the user drags a canvas item."""

    def test_scroll_frozen_during_simulated_drag(self, linked_scene, qapp):
        """Dragging an item 5px should not change the editor scroll position."""
        mw, items = linked_scene

        # Pick a middle item so the editor has to scroll
        item = items[len(items) // 2]
        ann_id = _select_and_scroll(mw, item, qapp)

        sb = mw.draft.text.verticalScrollBar()
        scroll_before = sb.value()
        assert scroll_before > 0, "Item should be far enough to require scrolling"

        # Simulate mouse-down + drag
        mw.scene._mouse_down_in_select = True
        mw.scene._move_start_positions = {item: (QPointF(item.pos()), 0)}

        for _ in range(5):
            old = item.pos()
            item.setPos(old.x() + 1, old.y())
            qapp.processEvents()

        scroll_after = sb.value()
        assert scroll_after == scroll_before, (
            f"Scroll drifted during drag: {scroll_before} -> {scroll_after}"
        )

        # Clean up simulated interaction
        mw.scene._mouse_down_in_select = False
        mw.scene._move_start_positions = {}
        mw.draft.unlock_scroll()

    def test_json_values_update_live_during_drag(self, linked_scene, qapp):
        """Geometry values in the JSON editor must update while dragging."""
        mw, items = linked_scene

        item = items[len(items) // 2]
        ann_id = _select_and_scroll(mw, item, qapp)

        # Read geometry before drag
        text_before = mw.draft.get_json_text()
        data_before = json.loads(text_before)
        ann_before = _find_annotation(data_before, ann_id)
        assert ann_before is not None, f"Annotation {ann_id} not found"

        # Simulate mouse-down + drag
        mw.scene._mouse_down_in_select = True
        mw.scene._move_start_positions = {item: (QPointF(item.pos()), 0)}

        for _ in range(5):
            old = item.pos()
            item.setPos(old.x() + 1, old.y())
            qapp.processEvents()

        # Read geometry after drag
        text_after = mw.draft.get_json_text()
        data_after = json.loads(text_after)
        ann_after = _find_annotation(data_after, ann_id)
        assert ann_after is not None, f"Annotation {ann_id} not found after drag"
        assert ann_after["geom"] != ann_before["geom"], (
            "Geometry should have changed during drag"
        )

        # Clean up
        mw.scene._mouse_down_in_select = False
        mw.scene._move_start_positions = {}
        mw.draft.unlock_scroll()

    def test_scroll_on_click_then_freeze(self, linked_scene, qapp):
        """Selecting an item with mouse-down should scroll once, then freeze."""
        mw, items = linked_scene

        item = items[len(items) // 2]
        ann_id = item.ann_id

        # Simulate mouse-down in SELECT mode (before selection)
        mw.scene._mouse_down_in_select = True
        mw.scene._move_start_positions = {}

        # Select the item — this triggers _do_selection_changed which should
        # scroll to the annotation AND set _lock_after_scroll.
        item.setSelected(True)
        qapp.processEvents()
        qapp.processEvents()  # let deferred _scroll_cursor_to_top run

        sb = mw.draft.text.verticalScrollBar()
        scroll_after_click = sb.value()
        assert scroll_after_click > 0, "Should have scrolled to the item"
        assert mw.draft._locked_scroll is not None, (
            "Scroll should be locked after click-select"
        )

        # Now simulate drag — scroll must not change
        for _ in range(5):
            old = item.pos()
            item.setPos(old.x() + 1, old.y())
            qapp.processEvents()

        scroll_after_drag = sb.value()
        assert scroll_after_drag == scroll_after_click, (
            f"Scroll drifted during drag: {scroll_after_click} -> {scroll_after_drag}"
        )

        # Simulate mouse release
        mw.scene._mouse_down_in_select = False
        mw.scene._move_start_positions = {}
        mw.draft.unlock_scroll()


class TestPumlImport:
    """PUML import must still work correctly with scroll-lock changes."""

    def test_line_meta_has_formatting_defaults(self, linked_scene, qapp):
        """Line annotations from PUML import should have full meta formatting fields."""
        mw, items = linked_scene
        text = mw.draft.get_json_text()
        data = json.loads(text)
        lines = [a for a in data["annotations"] if a.get("kind") == "line"]
        assert len(lines) > 0, "Should have at least one line annotation"
        expected_keys = {
            "kind", "label", "tech", "note",
            "label_align", "label_size",
            "tech_align", "tech_size",
            "note_align", "note_size",
            "text_valign", "text_spacing",
            "text_box_width", "text_box_height",
        }
        for line in lines:
            meta = line["meta"]
            missing = expected_keys - set(meta.keys())
            assert not missing, (
                f"Line {line['id']} meta missing keys: {missing}"
            )

    def test_shape_meta_has_formatting_defaults(self, linked_scene, qapp):
        """Shape annotations from PUML import should have full meta formatting fields."""
        mw, items = linked_scene
        text = mw.draft.get_json_text()
        data = json.loads(text)
        shapes = [a for a in data["annotations"] if a.get("kind") not in ("line", "group")]
        assert len(shapes) > 0, "Should have at least one shape annotation"
        expected_keys = {
            "kind", "label", "tech", "note",
            "label_align", "label_size",
            "tech_align", "tech_size",
            "note_align", "note_size",
            "text_valign", "text_spacing",
            "text_box_width", "text_box_height",
        }
        for shape in shapes:
            meta = shape["meta"]
            missing = expected_keys - set(meta.keys())
            assert not missing, (
                f"Shape {shape['id']} ({shape.get('kind')}) meta missing keys: {missing}"
            )

    def test_import_produces_annotations(self, linked_scene, qapp):
        """Importing a PUML file should produce annotations in the JSON."""
        mw, items = linked_scene
        text = mw.draft.get_json_text()
        data = json.loads(text)
        anns = data.get("annotations", [])
        assert len(anns) > 0, "Import should produce annotations"
        assert len(anns) == len(items), (
            f"Annotation count ({len(anns)}) should match item count ({len(items)})"
        )

    def test_reimport_after_drag(self, linked_scene, qapp):
        """Re-importing a PUML after a simulated drag should work."""
        mw, items = linked_scene
        puml_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "test_data", "PUML", "test_seq1.puml")
        )

        # Simulate a drag
        item = items[0]
        mw.scene._mouse_down_in_select = True
        mw.scene._move_start_positions = {item: (QPointF(item.pos()), 0)}
        item.setPos(item.pos().x() + 10, item.pos().y())
        qapp.processEvents()
        mw.scene._mouse_down_in_select = False
        mw.scene._move_start_positions = {}
        mw.draft.unlock_scroll()

        # Re-import
        mw._import_puml(puml_path)
        qapp.processEvents()
        data = json.loads(mw.draft.get_json_text())
        assert len(data.get("annotations", [])) > 0, "Re-import should produce annotations"
