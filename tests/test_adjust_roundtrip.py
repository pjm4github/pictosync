"""Test round-trip between property-panel adjust controls and JSON editor.

For each adjustable item kind (roundedrect, hexagon, cylinder, blockarrow):
  1. Create the item on the canvas and register it in draft JSON.
  2. Select it so the property panel populates.
  3. Change adjust1 (and adjust2 for blockarrow) via the spinbox.
  4. Verify the JSON editor reflects the new value.
  5. Verify no duplicate annotation IDs are created.

Requires a GUI environment (not headless).  Run with:
    .venv/Scripts/python -m pytest tests/test_adjust_roundtrip.py -v
"""
from __future__ import annotations

import json
import os
import sys

import pytest
from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QApplication

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from settings import SettingsManager
from properties.dock import ADJUST_CONFIG


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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ensure_linked(mw):
    """Make sure draft data and linking are initialised."""
    if mw._draft_data is None:
        mw._draft_data = {"version": "draft-1", "image": {}, "annotations": []}
    mw._link_enabled = True
    mw._rebuild_id_index()


def _create_item(mw, kind, qapp):
    """Create an adjustable item on the scene and register it in draft JSON.

    Returns (item, ann_id).
    """
    from canvas.items import (
        MetaRoundedRectItem,
        MetaHexagonItem,
        MetaCylinderItem,
        MetaBlockArrowItem,
    )

    _ensure_linked(mw)

    ann_id = mw._new_ann_id()
    on_change = mw._on_scene_item_changed

    if kind == "roundedrect":
        item = MetaRoundedRectItem(50, 50, 120, 80, 10, ann_id, on_change)
    elif kind == "hexagon":
        item = MetaHexagonItem(50, 50, 120, 80, 0.25, ann_id, on_change)
    elif kind == "cylinder":
        item = MetaCylinderItem(50, 50, 120, 100, 0.15, ann_id, on_change)
    elif kind == "blockarrow":
        item = MetaBlockArrowItem(50, 50, 160, 80, 40, 0.5, ann_id, on_change)
    else:
        raise ValueError(f"Unknown kind: {kind}")

    mw.scene.addItem(item)
    qapp.processEvents()

    # Register via _on_new_scene_item (mimics the drawing-finished callback)
    mw._on_new_scene_item(item)
    qapp.processEvents()

    return item, ann_id


def _select_item(mw, item, qapp):
    """Select an item so the property panel populates."""
    mw.scene.clearSelection()
    item.setSelected(True)
    qapp.processEvents()
    mw.props.set_item(item)
    qapp.processEvents()


def _json_geom(mw, ann_id):
    """Read the geom dict for *ann_id* from the live JSON editor text."""
    text = mw.draft.get_json_text()
    data = json.loads(text)
    for a in data.get("annotations", []):
        if a.get("id") == ann_id:
            return a.get("geom", {})
    return None


def _all_ids(mw):
    """Return all annotation IDs from the live editor JSON."""
    text = mw.draft.get_json_text()
    data = json.loads(text)
    return [a.get("id") for a in data.get("annotations", []) if isinstance(a, dict)]


# ---------------------------------------------------------------------------
# Tests — ADJUST_CONFIG labels and suffixes
# ---------------------------------------------------------------------------

class TestAdjustConfig:
    """ADJUST_CONFIG should drive the property panel labels and suffixes."""

    @pytest.mark.parametrize("kind", list(ADJUST_CONFIG.keys()))
    def test_adjust1_label_and_suffix(self, main_window, qapp, kind):
        """Selecting an item should set the correct adjust1 label and suffix."""
        mw = main_window
        item, _ = _create_item(mw, kind, qapp)
        _select_item(mw, item, qapp)

        cfg = ADJUST_CONFIG[kind]["adjust1"]
        assert mw.props.adjust1_label.text() == cfg["label"]
        assert mw.props.adjust1_spin.suffix() == cfg["suffix"]
        assert mw.props.adjust1_spin.minimum() == cfg["min"]
        assert mw.props.adjust1_spin.maximum() == cfg["max"]

    def test_blockarrow_adjust2_label_and_suffix(self, main_window, qapp):
        """Block arrow adjust2 should have the correct label and suffix."""
        mw = main_window
        item, _ = _create_item(mw, "blockarrow", qapp)
        _select_item(mw, item, qapp)

        cfg = ADJUST_CONFIG["blockarrow"]["adjust2"]
        assert mw.props.adjust2_label.text() == cfg["label"]
        assert mw.props.adjust2_spin.suffix() == cfg["suffix"]
        assert mw.props.adjust2_spin.minimum() == cfg["min"]
        assert mw.props.adjust2_spin.maximum() == cfg["max"]

    @pytest.mark.parametrize("kind", ["roundedrect", "hexagon", "cylinder"])
    def test_adjust2_hidden_for_single_adjust(self, main_window, qapp, kind):
        """Items with only adjust1 should hide the adjust2 controls."""
        mw = main_window
        item, _ = _create_item(mw, kind, qapp)
        _select_item(mw, item, qapp)

        assert mw.props.adjust2_spin.isVisible() is False
        assert mw.props.adjust2_label.isVisible() is False

    def test_adjust2_visible_for_blockarrow(self, main_window, qapp):
        """Block arrow should show the adjust2 controls."""
        mw = main_window
        item, _ = _create_item(mw, "blockarrow", qapp)
        _select_item(mw, item, qapp)

        assert mw.props.adjust2_spin.isVisible() is True
        assert mw.props.adjust2_label.isVisible() is True


# ---------------------------------------------------------------------------
# Tests — Round-trip: property panel → JSON editor
# ---------------------------------------------------------------------------

class TestAdjustRoundTrip:
    """Changing adjust spinboxes should update JSON, and vice-versa."""

    def test_roundedrect_adjust1_roundtrip(self, main_window, qapp):
        """Changing rounded-rect radius spinbox should update JSON adjust1."""
        mw = main_window
        item, ann_id = _create_item(mw, "roundedrect", qapp)
        _select_item(mw, item, qapp)

        # Change radius to 25 px (stored as raw pixels in JSON)
        mw.props.adjust1_spin.setValue(25)
        qapp.processEvents()

        geom = _json_geom(mw, ann_id)
        assert geom is not None, f"{ann_id} not found in editor JSON"
        assert geom["adjust1"] == 25.0

    def test_hexagon_adjust1_roundtrip(self, main_window, qapp):
        """Changing hexagon indent spinbox should update JSON adjust1."""
        mw = main_window
        item, ann_id = _create_item(mw, "hexagon", qapp)
        _select_item(mw, item, qapp)

        # Spinbox shows %, JSON stores ratio (30% → 0.3)
        mw.props.adjust1_spin.setValue(30)
        qapp.processEvents()

        geom = _json_geom(mw, ann_id)
        assert geom is not None, f"{ann_id} not found in editor JSON"
        assert geom["adjust1"] == 0.3

    def test_cylinder_adjust1_roundtrip(self, main_window, qapp):
        """Changing cylinder cap spinbox should update JSON adjust1."""
        mw = main_window
        item, ann_id = _create_item(mw, "cylinder", qapp)
        _select_item(mw, item, qapp)

        # Spinbox shows %, JSON stores ratio (20% → 0.2)
        mw.props.adjust1_spin.setValue(20)
        qapp.processEvents()

        geom = _json_geom(mw, ann_id)
        assert geom is not None, f"{ann_id} not found in editor JSON"
        assert geom["adjust1"] == 0.2

    def test_blockarrow_adjust1_roundtrip(self, main_window, qapp):
        """Changing block arrow shaft spinbox should update JSON adjust1."""
        mw = main_window
        item, ann_id = _create_item(mw, "blockarrow", qapp)
        _select_item(mw, item, qapp)

        # Spinbox shows %, JSON stores ratio (70% → 0.7)
        mw.props.adjust1_spin.setValue(70)
        qapp.processEvents()

        geom = _json_geom(mw, ann_id)
        assert geom is not None, f"{ann_id} not found in editor JSON"
        assert geom["adjust1"] == 0.7

    def test_blockarrow_adjust2_roundtrip(self, main_window, qapp):
        """Changing block arrow head spinbox should update JSON adjust2."""
        mw = main_window
        item, ann_id = _create_item(mw, "blockarrow", qapp)
        _select_item(mw, item, qapp)

        # Head length in px (stored directly)
        mw.props.adjust2_spin.setValue(60)
        qapp.processEvents()

        geom = _json_geom(mw, ann_id)
        assert geom is not None, f"{ann_id} not found in editor JSON"
        assert geom["adjust2"] == 60.0


# ---------------------------------------------------------------------------
# Tests — No duplicate annotation IDs
# ---------------------------------------------------------------------------

class TestNoDuplicates:
    """Adjusting items should never create duplicate annotation entries."""

    @pytest.mark.parametrize("kind", list(ADJUST_CONFIG.keys()))
    def test_no_duplicate_ids_after_adjust(self, main_window, qapp, kind):
        """Changing adjust values should not create duplicate IDs."""
        mw = main_window
        item, ann_id = _create_item(mw, kind, qapp)
        _select_item(mw, item, qapp)

        # Change adjust1 a few times
        for v in [mw.props.adjust1_spin.minimum() + 1,
                   (mw.props.adjust1_spin.minimum() + mw.props.adjust1_spin.maximum()) // 2,
                   mw.props.adjust1_spin.maximum() - 1]:
            mw.props.adjust1_spin.setValue(v)
            qapp.processEvents()

        ids = _all_ids(mw)
        dupes = [x for x in ids if ids.count(x) > 1]
        assert len(dupes) == 0, f"Duplicate IDs after adjusting {kind}: {dupes}"

    def test_no_duplicate_ids_after_blockarrow_adjust2(self, main_window, qapp):
        """Changing block arrow adjust2 should not create duplicate IDs."""
        mw = main_window
        item, ann_id = _create_item(mw, "blockarrow", qapp)
        _select_item(mw, item, qapp)

        for v in [20, 50, 80]:
            mw.props.adjust2_spin.setValue(v)
            qapp.processEvents()

        ids = _all_ids(mw)
        dupes = [x for x in ids if ids.count(x) > 1]
        assert len(dupes) == 0, f"Duplicate IDs after adjust2: {dupes}"


# ---------------------------------------------------------------------------
# Tests — Canvas handle → property panel display
# ---------------------------------------------------------------------------

class TestCanvasHandleUpdatesPanel:
    """Dragging adjust handles on canvas should update property panel spinboxes."""

    def test_roundedrect_canvas_to_panel(self, main_window, qapp):
        """Programmatic set_adjust1 + callback should update the spinbox."""
        mw = main_window
        item, _ = _create_item(mw, "roundedrect", qapp)
        _select_item(mw, item, qapp)

        # Simulate what the canvas handle drag does
        item.set_adjust1(30.0)
        item._notify_changed()
        from canvas.items import MetaRoundedRectItem
        if MetaRoundedRectItem.on_adjust1_changed:
            MetaRoundedRectItem.on_adjust1_changed(item, 30.0)
        qapp.processEvents()

        assert mw.props.adjust1_spin.value() == 30

    def test_hexagon_canvas_to_panel(self, main_window, qapp):
        """Programmatic set_adjust1 + callback should update the spinbox."""
        mw = main_window
        item, _ = _create_item(mw, "hexagon", qapp)
        _select_item(mw, item, qapp)

        item.set_adjust1(0.35)
        item._notify_changed()
        from canvas.items import MetaHexagonItem
        if MetaHexagonItem.on_adjust1_changed:
            MetaHexagonItem.on_adjust1_changed(item, 0.35)
        qapp.processEvents()

        assert mw.props.adjust1_spin.value() == 35  # 0.35 → 35%

    def test_cylinder_canvas_to_panel(self, main_window, qapp):
        """Programmatic set_adjust1 + callback should update the spinbox."""
        mw = main_window
        item, _ = _create_item(mw, "cylinder", qapp)
        _select_item(mw, item, qapp)

        item.set_adjust1(0.25)
        item._notify_changed()
        from canvas.items import MetaCylinderItem
        if MetaCylinderItem.on_adjust1_changed:
            MetaCylinderItem.on_adjust1_changed(item, 0.25)
        qapp.processEvents()

        assert mw.props.adjust1_spin.value() == 25  # 0.25 → 25%

    def test_blockarrow_adjust1_canvas_to_panel(self, main_window, qapp):
        """Programmatic set_adjust1 + callback should update the spinbox."""
        mw = main_window
        item, _ = _create_item(mw, "blockarrow", qapp)
        _select_item(mw, item, qapp)

        item.set_adjust1(0.6)
        item._notify_changed()
        from canvas.items import MetaBlockArrowItem
        if MetaBlockArrowItem.on_adjust1_changed:
            MetaBlockArrowItem.on_adjust1_changed(item, 0.6)
        qapp.processEvents()

        assert mw.props.adjust1_spin.value() == 60  # 0.6 → 60%

    def test_blockarrow_adjust2_canvas_to_panel(self, main_window, qapp):
        """Programmatic set_adjust2 + callback should update the spinbox."""
        mw = main_window
        item, _ = _create_item(mw, "blockarrow", qapp)
        _select_item(mw, item, qapp)

        item.set_adjust2(55.0)
        item._notify_changed()
        from canvas.items import MetaBlockArrowItem
        if MetaBlockArrowItem.on_adjust2_changed:
            MetaBlockArrowItem.on_adjust2_changed(item, 55.0)
        qapp.processEvents()

        assert mw.props.adjust2_spin.value() == 55


# ---------------------------------------------------------------------------
# Tests — Full cycle: canvas → JSON → panel consistency
# ---------------------------------------------------------------------------

class TestFullCycle:
    """Verify canvas, JSON editor, and property panel all agree."""

    @pytest.mark.parametrize("kind,new_spin_val,expected_json", [
        ("roundedrect", 18, 18.0),
        ("hexagon", 40, 0.4),
        ("cylinder", 30, 0.3),
        ("blockarrow", 80, 0.8),
    ])
    def test_panel_json_canvas_agree(self, main_window, qapp, kind, new_spin_val, expected_json):
        """After changing adjust1 via panel, canvas and JSON should agree."""
        mw = main_window
        item, ann_id = _create_item(mw, kind, qapp)
        _select_item(mw, item, qapp)

        mw.props.adjust1_spin.setValue(new_spin_val)
        qapp.processEvents()

        # 1. JSON geom should match
        geom = _json_geom(mw, ann_id)
        assert geom is not None, f"{ann_id} not found in editor JSON"
        assert geom["adjust1"] == expected_json, (
            f"JSON adjust1 mismatch: expected {expected_json}, got {geom['adjust1']}"
        )

        # 2. Canvas item internal value should match
        assert item._adjust1 == expected_json, (
            f"Canvas _adjust1 mismatch: expected {expected_json}, got {item._adjust1}"
        )

        # 3. Spinbox should still show the value
        assert mw.props.adjust1_spin.value() == new_spin_val

        # 4. No duplicate IDs
        ids = _all_ids(mw)
        dupes = [x for x in ids if ids.count(x) > 1]
        assert len(dupes) == 0, f"Duplicate IDs: {dupes}"
