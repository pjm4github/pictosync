"""Test bench for polygon curve vertices round-trip.

Tests that the extended _rel_points format survives:
  - MetaPolygonItem creation with straight, Q, and C points
  - to_record() serializes the full format
  - Points loaded from JSON preserve curve type and control points
  - QPainterPath uses cubicTo/quadTo (not just lineTo)
  - _recalculate_bbox preserves curve data
  - Cloud-like polygon (many cubic curves) round-trips
  - Mixed straight + curve vertices
"""
from __future__ import annotations

import os
import sys

import pytest




from canvas.items import MetaPolygonItem


# ── Helpers ──────────────────────────────────────────────────────────────

def _make_polygon(points, ann_id="poly1", x=100, y=100, w=200, h=200):
    return MetaPolygonItem(x, y, w, h, points, ann_id, on_change=None)


# ── Test Data ────────────────────────────────────────────────────────────

STRAIGHT_TRIANGLE = [
    [0.0, 0.0],
    [1.0, 0.0],
    [0.5, 1.0],
]

QUADRATIC_CURVE = [
    [0.0, 0.5],
    [0.5, 0.0, "Q", 0.25, 0.0],
    [1.0, 0.5, "Q", 0.75, 0.0],
    [0.5, 1.0, "Q", 0.75, 1.0],
    [0.0, 0.5, "Q", 0.25, 1.0],
]

CUBIC_CURVE = [
    [0.0, 0.5],
    [0.5, 0.0, "C", 0.1, 0.1, 0.4, 0.1],
    [1.0, 0.5, "C", 0.6, 0.1, 0.9, 0.1],
    [0.5, 1.0, "C", 0.9, 0.9, 0.6, 0.9],
    [0.0, 0.5, "C", 0.4, 0.9, 0.1, 0.9],
]

MIXED_POINTS = [
    [0.0, 0.0],
    [0.5, 0.0],                                # straight
    [1.0, 0.5, "Q", 0.9, 0.0],                # quadratic
    [0.5, 1.0, "C", 1.0, 0.8, 0.8, 1.0],     # cubic
    [0.0, 0.5],                                # straight
]


# ── Tests ────────────────────────────────────────────────────────────────

class TestStraightPolygon:
    """Straight-only polygon (baseline)."""

    def test_straight_points_preserved(self):
        item = _make_polygon(STRAIGHT_TRIANGLE)
        assert len(item._rel_points) == 3
        for pt in item._rel_points:
            assert len(pt) == 2

    def test_straight_to_record(self):
        item = _make_polygon(STRAIGHT_TRIANGLE)
        rec = item.to_record()
        pts = rec["geom"]["points"]
        assert len(pts) == 3
        for pt in pts:
            assert len(pt) == 2

    def test_straight_path_uses_lineto(self):
        item = _make_polygon(STRAIGHT_TRIANGLE)
        path = item.path()
        # MoveTo + 2 LineTo + closeSubpath
        assert path.elementCount() >= 3


class TestCubicBezierPolygon:
    """Polygon with cubic bezier curves."""

    def test_cubic_points_preserved(self):
        item = _make_polygon(CUBIC_CURVE)
        assert len(item._rel_points) == 5
        # First point is straight (moveto)
        assert len(item._rel_points[0]) == 2
        # Remaining points are cubic
        for pt in item._rel_points[1:]:
            assert len(pt) == 7
            assert pt[2] == "C"

    def test_cubic_control_points_preserved(self):
        item = _make_polygon(CUBIC_CURVE)
        pt = item._rel_points[1]  # [0.5, 0.0, "C", 0.1, 0.1, 0.4, 0.1]
        assert pt[0] == 0.5
        assert pt[1] == 0.0
        assert pt[2] == "C"
        assert pt[3] == 0.1  # c1x
        assert pt[4] == 0.1  # c1y
        assert pt[5] == 0.4  # c2x
        assert pt[6] == 0.1  # c2y

    def test_cubic_to_record_preserves_format(self):
        item = _make_polygon(CUBIC_CURVE)
        rec = item.to_record()
        pts = rec["geom"]["points"]
        assert len(pts) == 5
        assert len(pts[0]) == 2  # straight moveto
        for pt in pts[1:]:
            assert len(pt) == 7
            assert pt[2] == "C"

    def test_cubic_path_uses_cubicto(self):
        item = _make_polygon(CUBIC_CURVE)
        path = item.path()
        # Should have CurveToElement entries
        has_curve = False
        for i in range(path.elementCount()):
            e = path.elementAt(i)
            if e.type.name == "CurveToElement":
                has_curve = True
                break
        assert has_curve, "Path should contain CurveToElement for cubic bezier"


class TestQuadraticBezierPolygon:
    """Polygon with quadratic bezier curves."""

    def test_quadratic_points_preserved(self):
        item = _make_polygon(QUADRATIC_CURVE)
        assert len(item._rel_points) == 5
        assert len(item._rel_points[0]) == 2  # straight moveto
        for pt in item._rel_points[1:]:
            assert len(pt) == 5
            assert pt[2] == "Q"

    def test_quadratic_to_record(self):
        item = _make_polygon(QUADRATIC_CURVE)
        rec = item.to_record()
        pts = rec["geom"]["points"]
        for pt in pts[1:]:
            assert len(pt) == 5
            assert pt[2] == "Q"


class TestMixedVertices:
    """Polygon with mixed straight + quadratic + cubic vertices."""

    def test_mixed_points_preserved(self):
        item = _make_polygon(MIXED_POINTS)
        assert len(item._rel_points) == 5
        assert len(item._rel_points[0]) == 2  # straight
        assert len(item._rel_points[1]) == 2  # straight
        assert len(item._rel_points[2]) == 5  # Q
        assert item._rel_points[2][2] == "Q"
        assert len(item._rel_points[3]) == 7  # C
        assert item._rel_points[3][2] == "C"
        assert len(item._rel_points[4]) == 2  # straight

    def test_mixed_to_record_round_trip(self):
        item = _make_polygon(MIXED_POINTS)
        rec = item.to_record()
        pts = rec["geom"]["points"]
        # Recreate from the serialized points
        item2 = _make_polygon(pts, ann_id="poly2")
        assert len(item2._rel_points) == 5
        assert len(item2._rel_points[2]) == 5
        assert item2._rel_points[2][2] == "Q"
        assert len(item2._rel_points[3]) == 7
        assert item2._rel_points[3][2] == "C"


class TestRecalculateBBox:
    """_recalculate_bbox preserves curve type and control points."""

    def test_recalculate_preserves_cubic(self):
        item = _make_polygon(CUBIC_CURVE)
        # Simulate vertex drag: move a vertex outside bbox
        item._rel_points[1] = [0.5, -0.5, "C", 0.1, -0.3, 0.4, -0.3]
        item._recalculate_bbox()
        # After recalculate, the curve type should be preserved
        found_cubic = sum(1 for pt in item._rel_points
                         if len(pt) >= 7 and pt[2] == "C")
        assert found_cubic == 4, f"Expected 4 cubic points, got {found_cubic}"

    def test_recalculate_preserves_quadratic(self):
        item = _make_polygon(QUADRATIC_CURVE)
        item._rel_points[1] = [0.5, -0.5, "Q", 0.25, -0.3]
        item._recalculate_bbox()
        found_quad = sum(1 for pt in item._rel_points
                        if len(pt) >= 5 and pt[2] == "Q")
        assert found_quad == 4, f"Expected 4 quadratic points, got {found_quad}"

    def test_recalculate_preserves_mixed(self):
        item = _make_polygon(MIXED_POINTS)
        item._recalculate_bbox()
        assert len(item._rel_points[2]) == 5
        assert item._rel_points[2][2] == "Q"
        assert len(item._rel_points[3]) == 7
        assert item._rel_points[3][2] == "C"


class TestCloudPolygon:
    """Cloud-like polygon with many cubic bezier curves."""

    def test_many_curves(self):
        """Simulate a cloud shape with 20+ cubic curves."""
        pts = [[0.0, 0.5]]  # moveto
        n = 20
        for i in range(n):
            t0 = i / n
            t1 = (i + 1) / n
            rx = round(t1, 4)
            ry = round(0.5 + 0.3 * ((-1) ** i), 4)
            c1x = round(t0 + 0.01, 4)
            c1y = round(0.3, 4)
            c2x = round(t1 - 0.01, 4)
            c2y = round(0.3, 4)
            pts.append([rx, ry, "C", c1x, c1y, c2x, c2y])
        item = _make_polygon(pts)
        assert len(item._rel_points) == n + 1
        cubic_count = sum(1 for p in item._rel_points if len(p) >= 7 and p[2] == "C")
        assert cubic_count == n

    def test_many_curves_to_record_round_trip(self):
        pts = [[0.0, 0.5]]
        for i in range(15):
            pts.append([round((i + 1) / 15, 4), 0.5, "C",
                        round(i / 15 + 0.02, 4), 0.2,
                        round((i + 1) / 15 - 0.02, 4), 0.2])
        item = _make_polygon(pts)
        rec = item.to_record()
        pts2 = rec["geom"]["points"]
        item2 = _make_polygon(pts2, ann_id="p2")
        assert len(item2._rel_points) == 16
        for orig, loaded in zip(item._rel_points, item2._rel_points):
            assert len(orig) == len(loaded)
            if len(orig) >= 7:
                assert loaded[2] == "C"
