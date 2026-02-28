"""Test round-trip for all 10 item kinds: creation, JSON fields, meta editing, pen color.

For each of the 10 annotation kinds:
  1. Create the item on the canvas and register it in draft JSON.
  2. Verify JSON has correct kind, geom fields, meta, style, and pen.
  3. Select it and edit meta fields via the property panel.
  4. Verify JSON reflects the meta edits.
  5. Apply pen color changes and verify JSON style.pen.color.
  6. Verify no duplicate annotation IDs at any point.

Requires a GUI environment (not headless).  Run with:
    .venv/Scripts/python -m pytest tests/test_item_kinds.py -v
"""
from __future__ import annotations

import json
import os
import sys

import pytest
from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QApplication

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from canvas.items import (
    MetaRectItem,
    MetaRoundedRectItem,
    MetaEllipseItem,
    MetaLineItem,
    MetaTextItem,
    MetaHexagonItem,
    MetaCylinderItem,
    MetaBlockArrowItem,
    MetaPolygonItem,
    MetaCurveItem,
    MetaOrthoCurveItem,
    MetaIsoCubeItem,
)
from settings import SettingsManager

# ============================================================================
# Item config table: kind -> (ItemClass, constructor_args)
#
# Constructor args are everything BEFORE ann_id and on_change.
# ============================================================================

ALL_KINDS = [
    "rect", "roundedrect", "ellipse", "hexagon", "cylinder",
    "blockarrow", "isocube", "line", "text", "polygon", "curve", "orthocurve",
]

ITEM_CONFIG = {
    "rect":        (MetaRectItem,        (50, 50, 120, 80)),
    "roundedrect": (MetaRoundedRectItem, (50, 50, 120, 80, 10)),
    "ellipse":     (MetaEllipseItem,     (50, 50, 120, 80)),
    "hexagon":     (MetaHexagonItem,     (50, 50, 120, 80, 0.25)),
    "cylinder":    (MetaCylinderItem,    (50, 50, 120, 100, 0.15)),
    "blockarrow":  (MetaBlockArrowItem,  (50, 50, 160, 80, 40, 0.5)),
    "isocube":     (MetaIsoCubeItem,     (50, 50, 120, 80, 30, 135)),
    "line":        (MetaLineItem,        (50, 50, 200, 150)),
    "text":        (MetaTextItem,        (50, 50, "Sample")),
    "polygon":     (MetaPolygonItem,     (50, 50, 100, 100, [[0, 0], [1, 0], [0.5, 1]])),
    "curve":       (MetaCurveItem,       (50, 50, 100, 100,
                                          [{"cmd": "M", "x": 0, "y": 0},
                                           {"cmd": "L", "x": 1, "y": 1}])),
    "orthocurve":  (MetaOrthoCurveItem, (50, 50, 100, 80,
                                          [{"cmd": "M", "x": 0, "y": 0},
                                           {"cmd": "H", "x": 1},
                                           {"cmd": "V", "y": 1}])),
}

# Expected geom keys per kind (excluding nested list/dict fields like points/nodes)
GEOM_SCALAR_KEYS = {
    "rect":        {"x", "y", "w", "h"},
    "roundedrect": {"x", "y", "w", "h", "adjust1"},
    "ellipse":     {"x", "y", "w", "h"},
    "hexagon":     {"x", "y", "w", "h", "adjust1"},
    "cylinder":    {"x", "y", "w", "h", "adjust1"},
    "blockarrow":  {"x", "y", "w", "h", "adjust1", "adjust2"},
    "isocube":     {"x", "y", "w", "h", "adjust1", "adjust2"},
    "line":        {"x1", "y1", "x2", "y2"},
    "text":        {"x", "y"},
    "polygon":     {"x", "y", "w", "h"},
    "curve":       {"x", "y", "w", "h"},
    "orthocurve":  {"x", "y", "w", "h"},
}

# Geom keys that contain list/dict values (not int/float)
GEOM_COLLECTION_KEYS = {
    "polygon":    {"points"},
    "curve":      {"nodes"},
    "orthocurve": {"nodes"},
}

# Kinds that have _apply_pen_brush (shapes)
SHAPE_KINDS = {"rect", "roundedrect", "ellipse", "hexagon", "cylinder",
               "blockarrow", "isocube", "polygon", "curve", "orthocurve"}
# Kinds that have _apply_pen (line items)
LINE_KINDS = {"line"}
# Kinds with neither (text)
TEXT_KINDS = {"text"}


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
    """Create an item from the config table, register it in draft JSON.

    Returns (item, ann_id).
    """
    _ensure_linked(mw)

    ann_id = mw._new_ann_id()
    on_change = mw._on_scene_item_changed

    cls, args = ITEM_CONFIG[kind]
    item = cls(*args, ann_id, on_change)

    mw.scene.addItem(item)
    qapp.processEvents()

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


def _find_ann(data, ann_id):
    """Find annotation dict by ID in parsed data."""
    for a in data.get("annotations", []):
        if isinstance(a, dict) and a.get("id") == ann_id:
            return a
    return None


def _get_ann(mw, ann_id):
    """Parse editor JSON and return annotation dict. Asserts it exists."""
    text = mw.draft.get_json_text()
    data = json.loads(text)
    ann = _find_ann(data, ann_id)
    assert ann is not None, f"Annotation {ann_id} not found in editor JSON"
    return ann


def _all_ids(mw):
    """Return all annotation IDs from the live editor JSON."""
    text = mw.draft.get_json_text()
    data = json.loads(text)
    return [a.get("id") for a in data.get("annotations", []) if isinstance(a, dict)]


def _apply_pen_color(item, color_hex):
    """Apply a pen color to an item without opening a dialog.

    Mirrors the internal logic of pick_pen_color():
      1. Set item.pen_color
      2. Call the appropriate repaint method
      3. Call _notify_changed()
    """
    item.pen_color = QColor(color_hex)
    kind = getattr(item, "kind", "")
    if kind in SHAPE_KINDS and hasattr(item, "_apply_pen_brush"):
        item._apply_pen_brush()
    elif kind in LINE_KINDS and hasattr(item, "_apply_pen"):
        item._apply_pen()
    # Text items have _apply_text_style but pen color is not visual for them;
    # however _notify_changed still serialises pen_color in style dict.
    item._notify_changed()


# ---------------------------------------------------------------------------
# Test Class 1: Item creation and JSON field correctness
# ---------------------------------------------------------------------------

class TestItemCreationAndJSON:
    """Verify that creating each kind produces correct JSON structure."""

    @pytest.mark.parametrize("kind", ALL_KINDS)
    def test_item_kind_in_json(self, main_window, qapp, kind):
        """Annotation has the correct 'kind' value."""
        mw = main_window
        item, ann_id = _create_item(mw, kind, qapp)
        ann = _get_ann(mw, ann_id)
        assert ann["kind"] == kind

    @pytest.mark.parametrize("kind", ALL_KINDS)
    def test_geom_fields_present(self, main_window, qapp, kind):
        """Geom contains all expected keys for this kind."""
        mw = main_window
        item, ann_id = _create_item(mw, kind, qapp)
        ann = _get_ann(mw, ann_id)
        geom = ann.get("geom", {})
        expected = GEOM_SCALAR_KEYS[kind] | GEOM_COLLECTION_KEYS.get(kind, set())
        assert expected <= set(geom.keys()), (
            f"Missing geom keys for {kind}: {expected - set(geom.keys())}"
        )

    @pytest.mark.parametrize("kind", ALL_KINDS)
    def test_geom_values_numeric(self, main_window, qapp, kind):
        """Scalar geom values are int or float."""
        mw = main_window
        item, ann_id = _create_item(mw, kind, qapp)
        ann = _get_ann(mw, ann_id)
        geom = ann.get("geom", {})
        collection_keys = GEOM_COLLECTION_KEYS.get(kind, set())
        for key, val in geom.items():
            if key in collection_keys:
                assert isinstance(val, list), f"geom.{key} should be a list for {kind}"
            else:
                assert isinstance(val, (int, float)), (
                    f"geom.{key} = {val!r} is not numeric for {kind}"
                )

    @pytest.mark.parametrize("kind", ALL_KINDS)
    def test_meta_and_style_present(self, main_window, qapp, kind):
        """Annotation has 'meta' and 'style' top-level keys."""
        mw = main_window
        item, ann_id = _create_item(mw, kind, qapp)
        ann = _get_ann(mw, ann_id)
        assert "meta" in ann, f"No 'meta' key for {kind}"
        assert "style" in ann, f"No 'style' key for {kind}"

    @pytest.mark.parametrize("kind", ALL_KINDS)
    def test_style_has_pen(self, main_window, qapp, kind):
        """Style.pen has 'color' and 'width'."""
        mw = main_window
        item, ann_id = _create_item(mw, kind, qapp)
        ann = _get_ann(mw, ann_id)
        pen = ann.get("style", {}).get("pen", {})
        assert "color" in pen, f"No 'color' in style.pen for {kind}"
        assert "width" in pen, f"No 'width' in style.pen for {kind}"


# ---------------------------------------------------------------------------
# Test Class 2: Property panel meta editing
# ---------------------------------------------------------------------------

class TestPropertyPanelMeta:
    """Verify that editing meta fields via the property panel updates JSON."""

    @pytest.mark.parametrize("kind", ALL_KINDS)
    def test_label_edit(self, main_window, qapp, kind):
        """Setting label_edit text updates meta.label in JSON."""
        mw = main_window
        item, ann_id = _create_item(mw, kind, qapp)
        _select_item(mw, item, qapp)

        mw.props.label_edit.setText("TestLabel")
        mw.props._apply_changes()
        qapp.processEvents()

        ann = _get_ann(mw, ann_id)
        assert ann["meta"]["label"] == "TestLabel"

    @pytest.mark.parametrize("kind", ALL_KINDS)
    def test_tech_edit(self, main_window, qapp, kind):
        """Setting tech_edit text updates meta.tech in JSON."""
        mw = main_window
        item, ann_id = _create_item(mw, kind, qapp)
        _select_item(mw, item, qapp)

        mw.props.tech_edit.setText("gRPC")
        mw.props._apply_changes()
        qapp.processEvents()

        ann = _get_ann(mw, ann_id)
        assert ann["meta"]["tech"] == "gRPC"

    @pytest.mark.parametrize("kind", ALL_KINDS)
    def test_note_edit(self, main_window, qapp, kind):
        """Setting note_edit text updates meta.note in JSON."""
        mw = main_window
        item, ann_id = _create_item(mw, kind, qapp)
        _select_item(mw, item, qapp)

        mw.props.note_edit.setText("A useful note")
        mw.props._apply_changes()
        qapp.processEvents()

        ann = _get_ann(mw, ann_id)
        assert ann["meta"]["note"] == "A useful note"

    @pytest.mark.parametrize("kind", ALL_KINDS)
    def test_all_meta_fields_together(self, main_window, qapp, kind):
        """Setting all three meta fields at once updates JSON correctly."""
        mw = main_window
        item, ann_id = _create_item(mw, kind, qapp)
        _select_item(mw, item, qapp)

        mw.props.label_edit.setText("MyService")
        mw.props.tech_edit.setText("HTTPS/JSON")
        mw.props.note_edit.setText("Main service")
        mw.props._apply_changes()
        qapp.processEvents()

        ann = _get_ann(mw, ann_id)
        assert ann["meta"]["label"] == "MyService"
        assert ann["meta"]["tech"] == "HTTPS/JSON"
        assert ann["meta"]["note"] == "Main service"


# ---------------------------------------------------------------------------
# Test Class 3: Pen color changes
# ---------------------------------------------------------------------------

class TestPenColorChange:
    """Verify that pen color changes are reflected in JSON style.pen.color."""

    @pytest.mark.parametrize("kind", ALL_KINDS)
    def test_pen_color_green(self, main_window, qapp, kind):
        """Setting pen color to #00FF00 updates style.pen.color in JSON."""
        mw = main_window
        item, ann_id = _create_item(mw, kind, qapp)

        _apply_pen_color(item, "#00FF00")
        qapp.processEvents()

        ann = _get_ann(mw, ann_id)
        pen_color = ann["style"]["pen"]["color"].upper()
        assert pen_color == "#00FF00"

    @pytest.mark.parametrize("kind", ALL_KINDS)
    def test_pen_color_custom(self, main_window, qapp, kind):
        """Setting pen color to #AB12CD updates style.pen.color in JSON."""
        mw = main_window
        item, ann_id = _create_item(mw, kind, qapp)

        _apply_pen_color(item, "#AB12CD")
        qapp.processEvents()

        ann = _get_ann(mw, ann_id)
        pen_color = ann["style"]["pen"]["color"].upper()
        assert pen_color == "#AB12CD"


# ---------------------------------------------------------------------------
# Test Class 4: No duplicate IDs
# ---------------------------------------------------------------------------

class TestNoDuplicateIds:
    """Verify that no duplicate annotation IDs are created."""

    @pytest.mark.parametrize("kind", ALL_KINDS)
    def test_no_duplicate_ids_after_create(self, main_window, qapp, kind):
        """No duplicate IDs after creating an item."""
        mw = main_window
        item, ann_id = _create_item(mw, kind, qapp)

        ids = _all_ids(mw)
        dupes = [x for x in ids if ids.count(x) > 1]
        assert len(dupes) == 0, f"Duplicate IDs after creating {kind}: {dupes}"

    @pytest.mark.parametrize("kind", ALL_KINDS)
    def test_no_duplicate_ids_after_meta_change(self, main_window, qapp, kind):
        """No duplicate IDs after editing meta via property panel."""
        mw = main_window
        item, ann_id = _create_item(mw, kind, qapp)
        _select_item(mw, item, qapp)

        mw.props.label_edit.setText("Edited")
        mw.props._apply_changes()
        qapp.processEvents()

        ids = _all_ids(mw)
        dupes = [x for x in ids if ids.count(x) > 1]
        assert len(dupes) == 0, f"Duplicate IDs after meta change on {kind}: {dupes}"
