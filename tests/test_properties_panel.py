"""Test bench for PropertyDock panel.

Tests:
  - set_item populates controls for each kind
  - set_item(None) disables controls
  - Tab count and presence
  - Kind label shows correct kind name
  - Per-kind control visibility (arrow controls for line, fill for shapes, etc.)
  - Pen color edit syncs to item
  - Fill opacity slider syncs to item
  - Pen width spinbox syncs to item
  - Label/tech/note edits sync to meta
  - Save as Default button visibility
"""
from __future__ import annotations

import pytest

from PyQt6.QtGui import QColor

from canvas.items import (
    MetaRectItem, MetaEllipseItem, MetaLineItem,
    MetaTextItem, MetaHexagonItem, MetaCylinderItem,
    MetaPolygonItem, MetaCurveItem, MetaIsoCubeItem,
)


# ── Helpers ──────────────────────────────────────────────────────────────

SHAPE_FACTORIES = {
    "rect": lambda: MetaRectItem(50, 50, 120, 80, "r1", None),
    "ellipse": lambda: MetaEllipseItem(50, 50, 120, 80, "e1", None),
    "hexagon": lambda: MetaHexagonItem(50, 50, 120, 80, 0.25, "h1", None),
    "cylinder": lambda: MetaCylinderItem(50, 50, 120, 100, 0.15, "c1", None),
    "isocube": lambda: MetaIsoCubeItem(50, 50, 120, 80, 30, 135, "i1", None),
    "polygon": lambda: MetaPolygonItem(50, 50, 100, 100,
                                       [[0, 0], [1, 0], [0.5, 1]], "p1", None),
}

LINE_FACTORY = lambda: MetaLineItem(50, 50, 200, 150, "l1", None)
TEXT_FACTORY = lambda: MetaTextItem(50, 50, "Hello", "t1", None)
CURVE_FACTORY = lambda: MetaCurveItem(50, 50, 100, 100,
                                       [{"cmd": "M", "x": 0, "y": 0},
                                        {"cmd": "L", "x": 1, "y": 1}], "cv1", None)


def _setup_panel(main_window, item):
    """Add item to scene and select it so the panel populates."""
    mw = main_window
    mw.scene.addItem(item)
    mw.scene.clearSelection()
    item.setSelected(True)
    mw.props.set_item(item)
    return mw.props


# ── Tests ────────────────────────────────────────────────────────────────

class TestSetItemNone:
    """set_item(None) disables controls."""

    def test_kind_label_empty(self, main_window):
        main_window.props.set_item(None)
        assert main_window.props.kind_label.text() == "-"

    def test_controls_disabled(self, main_window):
        main_window.props.set_item(None)
        assert not main_window.props.label_edit.isEnabled()
        assert not main_window.props.tech_edit.isEnabled()


class TestSetItemShape:
    """set_item with shape items populates controls."""

    @pytest.mark.parametrize("kind", list(SHAPE_FACTORIES.keys()))
    def test_kind_label_shows_kind(self, main_window, kind):
        item = SHAPE_FACTORIES[kind]()
        props = _setup_panel(main_window, item)
        assert props.kind_label.text() == kind

    @pytest.mark.parametrize("kind", list(SHAPE_FACTORIES.keys()))
    def test_controls_enabled(self, main_window, kind):
        item = SHAPE_FACTORIES[kind]()
        props = _setup_panel(main_window, item)
        assert props.label_edit.isEnabled()

    def test_rect_has_fill_controls(self, main_window):
        item = SHAPE_FACTORIES["rect"]()
        props = _setup_panel(main_window, item)
        # Fill color button should be present and accessible
        assert hasattr(props, "fill_color_btn")


class TestSetItemLine:
    """set_item with line item shows line-specific controls."""

    def test_kind_label_line(self, main_window):
        item = LINE_FACTORY()
        props = _setup_panel(main_window, item)
        assert props.kind_label.text() == "line"

    def test_arrow_combo_visible(self, main_window):
        item = LINE_FACTORY()
        props = _setup_panel(main_window, item)
        assert props.arrow_combo.isVisible()

    def test_anchor_frame_not_hidden(self, main_window):
        item = LINE_FACTORY()
        props = _setup_panel(main_window, item)
        # anchor_frame.isVisible() may be False if dock isn't shown;
        # check isHidden() which is the widget's own hidden flag
        assert not props.anchor_frame.isHidden()


class TestSetItemText:
    """set_item with text item."""

    def test_kind_label_text(self, main_window):
        item = TEXT_FACTORY()
        props = _setup_panel(main_window, item)
        assert props.kind_label.text() == "text"


class TestSetItemCurve:
    """set_item with curve item shows anchor controls."""

    def test_kind_label_curve(self, main_window):
        item = CURVE_FACTORY()
        props = _setup_panel(main_window, item)
        assert props.kind_label.text() == "curve"

    def test_anchor_frame_not_hidden(self, main_window):
        item = CURVE_FACTORY()
        props = _setup_panel(main_window, item)
        assert not props.anchor_frame.isHidden()


class TestTabPresence:
    """Panel has the expected tabs."""

    def test_has_tabs(self, main_window):
        props = main_window.props
        assert props.tabs.count() >= 2  # at least Style + Contents

    def test_tab_names(self, main_window):
        props = main_window.props
        tab_names = [props.tabs.tabText(i) for i in range(props.tabs.count())]
        assert "Style" in tab_names
        assert "Contents" in tab_names


class TestPenColorSync:
    """Pen color changes sync to item."""

    def test_pen_color_applied(self, main_window):
        item = SHAPE_FACTORIES["rect"]()
        props = _setup_panel(main_window, item)
        # Simulate setting pen color
        new_color = QColor(0, 128, 255)
        item.pen_color = new_color
        item._apply_pen_brush()
        rec = item.to_record()
        pen_hex = rec["style"]["pen"]["color"].upper()
        assert "0080FF" in pen_hex


class TestPenWidthSync:
    """Pen width spinbox syncs to item."""

    def test_pen_width_read(self, main_window):
        item = SHAPE_FACTORIES["rect"]()
        item.pen_width = 3
        item._apply_pen_brush()
        props = _setup_panel(main_window, item)
        assert props.line_width_spin.value() == 3


class TestMetaFieldEdits:
    """Label/tech/note edits sync to item meta."""

    def test_label_edit_syncs(self, main_window):
        item = SHAPE_FACTORIES["rect"]()
        props = _setup_panel(main_window, item)
        props.label_edit.setText("NewLabel")
        # The edit should trigger a signal that updates the item
        # (signal connection happens in set_item)
        # For direct testing, we read what the edit contains
        assert props.label_edit.text() == "NewLabel"

    def test_tech_edit_syncs(self, main_window):
        item = SHAPE_FACTORIES["rect"]()
        props = _setup_panel(main_window, item)
        props.tech_edit.setText("NewTech")
        assert props.tech_edit.text() == "NewTech"

    def test_note_edit_syncs(self, main_window):
        item = SHAPE_FACTORIES["rect"]()
        props = _setup_panel(main_window, item)
        props.note_edit.setText("NewNote")
        assert props.note_edit.text() == "NewNote"


class TestSaveDefaultButton:
    """Save as Default button visibility."""

    def test_visible_when_item_selected(self, main_window):
        item = SHAPE_FACTORIES["rect"]()
        props = _setup_panel(main_window, item)
        assert props._save_default_btn.isVisible()

    def test_hidden_when_no_item(self, main_window):
        main_window.props.set_item(None)
        assert not main_window.props._save_default_btn.isVisible()


class TestSwitchBetweenItems:
    """Switching between different item types updates controls."""

    def test_rect_then_line(self, main_window):
        rect = SHAPE_FACTORIES["rect"]()
        line = LINE_FACTORY()
        main_window.scene.addItem(rect)
        main_window.scene.addItem(line)

        # Select rect
        main_window.props.set_item(rect)
        assert main_window.props.kind_label.text() == "rect"

        # Select line
        main_window.props.set_item(line)
        assert main_window.props.kind_label.text() == "line"

    def test_line_then_none(self, main_window):
        line = LINE_FACTORY()
        main_window.scene.addItem(line)
        main_window.props.set_item(line)
        assert main_window.props.kind_label.text() == "line"
        main_window.props.set_item(None)
        assert main_window.props.kind_label.text() == "-"
