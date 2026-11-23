"""Test bench for rotation angle round-trip.

Tests that geom.angle persists through:
  - set_rotation_angle → to_record → geom.angle present
  - Reconstruct from record → rotation restored
  - Zero rotation → no angle key in geom
  - Non-rotatable items (group) don't emit angle
  - Various angle values (0, 45, 90, 180, 270, 359)
"""
from __future__ import annotations

import os
import sys

import pytest




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
    MetaSeqBlockItem,
    MetaGroupItem,
)


# ── Helpers ──────────────────────────────────────────────────────────────

ROTATABLE_ITEMS = {
    "rect":        lambda: MetaRectItem(50, 50, 120, 80, "r1", None),
    "roundedrect": lambda: MetaRoundedRectItem(50, 50, 120, 80, 10, "r2", None),
    "ellipse":     lambda: MetaEllipseItem(50, 50, 120, 80, "r3", None),
    "hexagon":     lambda: MetaHexagonItem(50, 50, 120, 80, 0.25, "r4", None),
    "cylinder":    lambda: MetaCylinderItem(50, 50, 120, 100, 0.15, "r5", None),
    "blockarrow":  lambda: MetaBlockArrowItem(50, 50, 160, 80, 40, 0.5, "r6", None),
    "isocube":     lambda: MetaIsoCubeItem(50, 50, 120, 80, 30, 135, "r7", None),
    "polygon":     lambda: MetaPolygonItem(50, 50, 100, 100,
                                           [[0, 0], [1, 0], [0.5, 1]], "r8", None),
    "seqblock":    lambda: MetaSeqBlockItem(50, 50, 200, 150, "alt", "r9", None),
    "curve":       lambda: MetaCurveItem(50, 50, 100, 100,
                                         [{"cmd": "M", "x": 0, "y": 0},
                                          {"cmd": "L", "x": 1, "y": 1}], "r11", None),
    "orthocurve":  lambda: MetaOrthoCurveItem(50, 50, 100, 80,
                                               [{"cmd": "M", "x": 0, "y": 0},
                                                {"cmd": "H", "x": 1},
                                                {"cmd": "V", "y": 1}], "r12", None),
}

# Items that are NOT rotatable (endpoints define direction, no angle field)
NON_ROTATABLE_ITEMS = {
    "line":  lambda: MetaLineItem(50, 50, 200, 150, "nr1", None),
    "group": None,  # tested separately
}

ROTATABLE_KINDS = list(ROTATABLE_ITEMS.keys())


# ── Tests ────────────────────────────────────────────────────────────────

class TestZeroRotation:
    """Zero rotation should NOT include angle in geom."""

    @pytest.mark.parametrize("kind", ROTATABLE_KINDS)
    def test_no_angle_at_zero(self, kind):
        item = ROTATABLE_ITEMS[kind]()
        rec = item.to_record()
        assert "angle" not in rec.get("geom", {}), \
            f"{kind}: geom should not have 'angle' when rotation is 0"


class TestSetRotation:
    """Setting rotation → angle appears in to_record."""

    @pytest.mark.parametrize("kind", ROTATABLE_KINDS)
    def test_angle_45(self, kind):
        item = ROTATABLE_ITEMS[kind]()
        if hasattr(item, "set_rotation_angle"):
            item.set_rotation_angle(45)
        else:
            item.setRotation(45)
        rec = item.to_record()
        g = rec.get("geom", {})
        assert "angle" in g, f"{kind}: geom missing 'angle' after set_rotation_angle(45)"
        assert abs(g["angle"] - 45) < 0.1, f"{kind}: angle={g['angle']}, expected 45"


class TestAngleValues:
    """Various angle values serialize correctly."""

    @pytest.mark.parametrize("angle", [0, 30, 45, 90, 135, 180, 270, 359])
    def test_rect_angles(self, angle):
        item = MetaRectItem(50, 50, 120, 80, "test", None)
        if angle > 0:
            if hasattr(item, "set_rotation_angle"):
                item.set_rotation_angle(angle)
            else:
                item.setRotation(angle)
        rec = item.to_record()
        g = rec.get("geom", {})
        if angle == 0:
            assert "angle" not in g
        else:
            assert abs(g["angle"] - angle) < 0.1


class TestRotationRoundTrip:
    """Full round-trip: set angle → to_record → reconstruct → verify rotation."""

    @pytest.mark.parametrize("kind", ROTATABLE_KINDS)
    def test_angle_survives_roundtrip(self, kind):
        item = ROTATABLE_ITEMS[kind]()
        if hasattr(item, "set_rotation_angle"):
            item.set_rotation_angle(60)
        else:
            item.setRotation(60)
        rec = item.to_record()

        # Verify angle in record
        assert abs(rec["geom"].get("angle", 0) - 60) < 0.1

        # Reconstruct: create new item and apply rotation from geom
        item2 = ROTATABLE_ITEMS[kind]()
        angle_from_rec = rec["geom"].get("angle", 0)
        if hasattr(item2, "set_rotation_angle"):
            item2.set_rotation_angle(angle_from_rec)
        else:
            item2.setRotation(angle_from_rec)

        # Verify rotation on reconstructed item
        assert abs(item2.rotation() - 60) < 0.1

        # Verify second to_record also has angle
        rec2 = item2.to_record()
        assert abs(rec2["geom"].get("angle", 0) - 60) < 0.1


class TestNonRotatable:
    """Non-rotatable items (group, line) don't emit angle."""

    def test_group_no_angle(self):
        from canvas.scene import AnnotatorScene
        scene = AnnotatorScene()
        group = MetaGroupItem("g1", None)
        scene.addItem(group)
        assert group._is_rotatable() is False
        rec = group.to_record()
        assert "angle" not in rec.get("geom", {})

    def test_line_not_rotatable(self):
        item = MetaLineItem(50, 50, 200, 150, "l1", None)
        assert item._is_rotatable() is False

    def test_line_no_angle_in_record(self):
        item = MetaLineItem(50, 50, 200, 150, "l1", None)
        rec = item.to_record()
        assert "angle" not in rec.get("geom", {})
