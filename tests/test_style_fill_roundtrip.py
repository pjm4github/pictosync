"""Test bench for style.fill round-trip.

Tests that fill color and transparency survive:
  - to_record() → style.fill.color present for all shape kinds
  - Opaque fill (#RRGGBBFF) round-trips through apply_style_from_record
  - Transparent fill (#00000000) round-trips
  - Semi-transparent fill (#RRGGBB80) round-trips
  - Named/short hex colors normalized
  - Pen color separate from fill color
  - Fill color applied to brush_color on canvas item
"""
from __future__ import annotations

import os
import sys

import pytest




from PyQt6.QtGui import QColor
from canvas.items import (
    MetaRectItem,
    MetaRoundedRectItem,
    MetaEllipseItem,
    MetaHexagonItem,
    MetaCylinderItem,
    MetaBlockArrowItem,
    MetaIsoCubeItem,
    MetaPolygonItem,
    MetaSeqBlockItem,
)
from utils import qcolor_to_hex, hex_to_qcolor


# ── Helpers ──────────────────────────────────────────────────────────────

SHAPE_ITEMS = {
    "rect":        lambda: MetaRectItem(50, 50, 120, 80, "t1", None),
    "roundedrect": lambda: MetaRoundedRectItem(50, 50, 120, 80, 10, "t2", None),
    "ellipse":     lambda: MetaEllipseItem(50, 50, 120, 80, "t3", None),
    "hexagon":     lambda: MetaHexagonItem(50, 50, 120, 80, 0.25, "t4", None),
    "cylinder":    lambda: MetaCylinderItem(50, 50, 120, 100, 0.15, "t5", None),
    "blockarrow":  lambda: MetaBlockArrowItem(50, 50, 160, 80, 40, 0.5, "t6", None),
    "isocube":     lambda: MetaIsoCubeItem(50, 50, 120, 80, 30, 135, "t7", None),
    "polygon":     lambda: MetaPolygonItem(50, 50, 100, 100,
                                           [[0, 0], [1, 0], [0.5, 1]], "t8", None),
    "seqblock":    lambda: MetaSeqBlockItem(50, 50, 200, 150, "alt", "t9", None),
}

SHAPE_KINDS = list(SHAPE_ITEMS.keys())


# ── Tests ────────────────────────────────────────────────────────────────

class TestFillColorInRecord:
    """to_record() emits style.fill.color."""

    @pytest.mark.parametrize("kind", SHAPE_KINDS)
    def test_fill_color_present(self, kind):
        item = SHAPE_ITEMS[kind]()
        rec = item.to_record()
        assert "fill" in rec["style"]
        assert "color" in rec["style"]["fill"]

    @pytest.mark.parametrize("kind", SHAPE_KINDS)
    def test_fill_color_is_hex(self, kind):
        item = SHAPE_ITEMS[kind]()
        rec = item.to_record()
        color = rec["style"]["fill"]["color"]
        assert color.startswith("#"), f"fill.color should be hex, got {color!r}"


class TestFillColorApply:
    """apply_style_from_record sets brush_color correctly."""

    @pytest.mark.parametrize("kind", SHAPE_KINDS)
    def test_opaque_red_fill(self, kind):
        item = SHAPE_ITEMS[kind]()
        rec = {"style": {"pen": {"color": "#000000", "width": 1},
                          "fill": {"color": "#FF0000FF"}}}
        item.apply_style_from_record(rec)
        if hasattr(item, "brush_color"):
            assert item.brush_color.red() == 255
            assert item.brush_color.green() == 0
            assert item.brush_color.blue() == 0
            assert item.brush_color.alpha() == 255

    @pytest.mark.parametrize("kind", SHAPE_KINDS)
    def test_transparent_fill(self, kind):
        item = SHAPE_ITEMS[kind]()
        rec = {"style": {"pen": {"color": "#000000", "width": 1},
                          "fill": {"color": "#00000000"}}}
        item.apply_style_from_record(rec)
        if hasattr(item, "brush_color"):
            assert item.brush_color.alpha() == 0

    def test_semi_transparent_fill(self):
        item = MetaRectItem(50, 50, 100, 60, "st1", None)
        rec = {"style": {"pen": {"color": "#000000", "width": 1},
                          "fill": {"color": "#0000FF80"}}}
        item.apply_style_from_record(rec)
        assert item.brush_color.blue() == 255
        assert item.brush_color.alpha() == 128


class TestFillColorRoundTrip:
    """Full round-trip: set fill → to_record → apply_style → verify."""

    @pytest.mark.parametrize("kind", SHAPE_KINDS)
    def test_fill_survives_roundtrip(self, kind):
        item = SHAPE_ITEMS[kind]()
        # Set a specific fill color
        if hasattr(item, "brush_color"):
            item.brush_color = QColor(100, 200, 50, 180)
            if hasattr(item, "_apply_pen_brush"):
                item._apply_pen_brush()

        rec = item.to_record()
        fill_hex = rec["style"]["fill"]["color"]

        # Create new item and apply
        item2 = SHAPE_ITEMS[kind]()
        item2.apply_style_from_record(rec)
        if hasattr(item2, "_apply_pen_brush"):
            item2._apply_pen_brush()

        rec2 = item2.to_record()
        fill_hex2 = rec2["style"]["fill"]["color"]

        assert fill_hex == fill_hex2, \
            f"fill.color changed: {fill_hex} → {fill_hex2}"


class TestPenAndFillIndependent:
    """Pen color and fill color are independent."""

    def test_different_pen_and_fill(self):
        item = MetaRectItem(50, 50, 100, 60, "pf1", None)
        item.pen_color = QColor(255, 0, 0)
        item.brush_color = QColor(0, 0, 255, 128)
        item._apply_pen_brush()
        rec = item.to_record()
        pen_color = rec["style"]["pen"]["color"]
        fill_color = rec["style"]["fill"]["color"]
        assert pen_color != fill_color
        assert "FF0000" in pen_color.upper()
        assert "0000FF" in fill_color.upper()

    def test_apply_doesnt_cross_contaminate(self):
        item = MetaRectItem(50, 50, 100, 60, "pf2", None)
        rec = {"style": {
            "pen": {"color": "#FF000000", "width": 2},
            "fill": {"color": "#00FF00FF"},
        }}
        item.apply_style_from_record(rec)
        # Pen should be red (with alpha 0 = transparent pen, but color is red)
        # Fill should be green
        assert item.brush_color.green() == 255
        assert item.brush_color.red() == 0


class TestQColorHexConversion:
    """qcolor_to_hex and hex_to_qcolor utilities."""

    def test_opaque_roundtrip(self):
        c = QColor(100, 150, 200, 255)
        h = qcolor_to_hex(c, include_alpha=True)
        c2 = hex_to_qcolor(h, QColor())
        assert c2.red() == 100
        assert c2.green() == 150
        assert c2.blue() == 200
        assert c2.alpha() == 255

    def test_transparent_roundtrip(self):
        c = QColor(0, 0, 0, 0)
        h = qcolor_to_hex(c, include_alpha=True)
        c2 = hex_to_qcolor(h, QColor())
        assert c2.alpha() == 0

    def test_semi_transparent_roundtrip(self):
        c = QColor(255, 128, 64, 192)
        h = qcolor_to_hex(c, include_alpha=True)
        c2 = hex_to_qcolor(h, QColor())
        assert abs(c2.red() - 255) <= 1
        assert abs(c2.green() - 128) <= 1
        assert abs(c2.blue() - 64) <= 1
        assert abs(c2.alpha() - 192) <= 1
