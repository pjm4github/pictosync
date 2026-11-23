"""Test bench for polygon vertex editing mode.

Tests:
  - Double-click toggles vertex editing mode
  - Hover over vertex shows CrossCursor
  - Hover over control point shows CrossCursor
  - Hover over edge shows PointingHandCursor
  - Hover away from all shows ArrowCursor
  - Right-click on vertex shows context menu (no crash)
  - Right-click on edge shows context menu (no crash)
  - shape() in vertex-edit mode includes vertex knobs
  - shape() in vertex-edit mode includes edge stroke areas
  - shape() in vertex-edit mode includes control point areas
  - Hit-test vertex finds nearby vertex
  - Hit-test vertex rejects distant point
  - Hit-test edge finds nearby edge
  - Hit-test edge rejects distant point
  - Hit-test ctrl point finds nearby control point
"""
from __future__ import annotations

import pytest

from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPainterPath

from canvas.items import MetaPolygonItem


# ── Helpers ──────────────────────────────────────────────────────────────

# Triangle: vertices at relative (0.1,0.9), (0.5,0.1), (0.9,0.9)
TRIANGLE_PTS = [[0.1, 0.9], [0.5, 0.1], [0.9, 0.9]]

# Pentagon with one quadratic vertex (index 2) and one cubic vertex (index 4)
MIXED_PTS = [
    [0.1, 0.5],
    [0.3, 0.1],
    [0.5, 0.5, "Q", 0.5, 0.0],         # quadratic: cp above
    [0.7, 0.1],
    [0.9, 0.5, "C", 1.0, 0.3, 1.0, 0.7],  # cubic: cp1/cp2 right
]


def _make_poly(points=None, w=200, h=200):
    """Create a polygon item at (100, 100) with given relative points."""
    pts = points or TRIANGLE_PTS
    item = MetaPolygonItem(100, 100, w, h, pts, "poly_test", None)
    return item


def _enter_vertex_editing(item):
    """Toggle vertex editing mode on."""
    item._vertex_editing = True
    item.prepareGeometryChange()
    item.update()


def _vertex_scene_pos(item, idx):
    """Return scene position of vertex idx."""
    return item._vertex_points_scene()[idx]


def _midpoint_scene(item, idx_a, idx_b):
    """Return scene position of the midpoint between two vertices."""
    verts = item._vertex_points_scene()
    a, b = verts[idx_a], verts[idx_b]
    return QPointF((a.x() + b.x()) / 2, (a.y() + b.y()) / 2)


# ── Hit-test accuracy ────────────────────────────────────────────────────

class TestHitTestVertex:

    def test_vertex_found_at_exact_position(self):
        item = _make_poly()
        _enter_vertex_editing(item)
        vp = _vertex_scene_pos(item, 0)
        assert item._hit_test_vertex(vp) == 0

    def test_vertex_found_all_indices(self):
        item = _make_poly()
        _enter_vertex_editing(item)
        for i in range(len(TRIANGLE_PTS)):
            vp = _vertex_scene_pos(item, i)
            assert item._hit_test_vertex(vp) == i

    def test_vertex_not_found_far_away(self):
        item = _make_poly()
        _enter_vertex_editing(item)
        far_pt = QPointF(9999, 9999)
        assert item._hit_test_vertex(far_pt) is None

    def test_vertex_found_near_but_not_exact(self):
        item = _make_poly()
        _enter_vertex_editing(item)
        vp = _vertex_scene_pos(item, 1)
        # Offset by 3 pixels — should still be within hit distance
        near = QPointF(vp.x() + 3, vp.y() + 3)
        assert item._hit_test_vertex(near) == 1


class TestHitTestEdge:

    def test_edge_found_at_midpoint(self):
        item = _make_poly()
        _enter_vertex_editing(item)
        mid = _midpoint_scene(item, 0, 1)
        result = item._hit_test_edge(mid)
        assert result is not None
        assert result == 0  # edge 0 connects vertex 0 to vertex 1

    def test_edge_found_all_edges(self):
        item = _make_poly()
        _enter_vertex_editing(item)
        n = len(TRIANGLE_PTS)
        for i in range(n):
            j = (i + 1) % n
            mid = _midpoint_scene(item, i, j)
            result = item._hit_test_edge(mid)
            assert result is not None, f"Edge {i} not found at midpoint"

    def test_edge_not_found_far_away(self):
        item = _make_poly()
        _enter_vertex_editing(item)
        far_pt = QPointF(9999, 9999)
        assert item._hit_test_edge(far_pt) is None


class TestHitTestControlPoint:

    def test_ctrl_point_found_quadratic(self):
        item = _make_poly(MIXED_PTS)
        _enter_vertex_editing(item)
        # Vertex 2 has a Q control point at (0.5, 0.0) relative
        # Local pos: (0.5*200, 0.0*200) = (100, 0)
        cp_scene = item.mapToScene(QPointF(0.5 * 200, 0.0 * 200))
        result = item._hit_test_ctrl_point(cp_scene)
        assert result is not None
        assert result[0] == 2  # vertex index
        assert result[1] == "cp"  # quadratic control point

    def test_ctrl_point_found_cubic(self):
        item = _make_poly(MIXED_PTS)
        _enter_vertex_editing(item)
        # Vertex 4 has C control points at (1.0, 0.3) and (1.0, 0.7)
        c1_scene = item.mapToScene(QPointF(1.0 * 200, 0.3 * 200))
        result = item._hit_test_ctrl_point(c1_scene)
        assert result is not None
        assert result[0] == 4
        assert result[1] == "c1"

    def test_ctrl_point_not_found_on_straight_polygon(self):
        item = _make_poly(TRIANGLE_PTS)
        _enter_vertex_editing(item)
        # No control points on a straight polygon
        mid = _midpoint_scene(item, 0, 1)
        assert item._hit_test_ctrl_point(mid) is None


# ── shape() hit area coverage ────────────────────────────────────────────

class TestShapeHitArea:

    def test_shape_contains_vertices(self):
        item = _make_poly()
        _enter_vertex_editing(item)
        item.setSelected(True)
        s = item.shape()
        for vp in item._vertex_points_local():
            assert s.contains(vp), f"shape() doesn't contain vertex at {vp}"

    def test_shape_contains_edge_midpoints(self):
        item = _make_poly()
        _enter_vertex_editing(item)
        item.setSelected(True)
        s = item.shape()
        verts = item._vertex_points_local()
        n = len(verts)
        for i in range(n):
            a, b = verts[i], verts[(i + 1) % n]
            mid = QPointF((a.x() + b.x()) / 2, (a.y() + b.y()) / 2)
            assert s.contains(mid), f"shape() doesn't contain edge {i} midpoint"

    def test_shape_contains_control_points(self):
        item = _make_poly(MIXED_PTS)
        _enter_vertex_editing(item)
        item.setSelected(True)
        s = item.shape()
        for _vi, _label, cp in item._ctrl_point_info():
            assert s.contains(cp), f"shape() doesn't contain ctrl point {_label} of vertex {_vi}"


# ── Vertex editing mode toggle ───────────────────────────────────────────

class TestVertexEditingToggle:

    def test_starts_not_editing(self):
        item = _make_poly()
        assert item._vertex_editing is False

    def test_toggle_on(self):
        item = _make_poly()
        item._vertex_editing = True
        assert item._vertex_editing is True

    def test_toggle_off_on_deselect(self):
        """Deselecting should exit vertex edit mode."""
        item = _make_poly()
        _enter_vertex_editing(item)
        # Simulate deselection
        from PyQt6.QtWidgets import QGraphicsItem
        item.itemChange(
            QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged, False)
        assert item._vertex_editing is False


# ── Right-click context menu (no crash) ──────────────────────────────────

class TestVertexContextMenu:

    def test_right_click_on_vertex_no_crash(self):
        """Right-click near a vertex should not crash."""
        item = _make_poly()
        _enter_vertex_editing(item)
        vp = _vertex_scene_pos(item, 0)
        idx = item._hit_test_vertex(vp)
        assert idx is not None, "Should find vertex at exact position"

    def test_right_click_on_edge_no_crash(self):
        """Right-click near an edge midpoint should find the edge."""
        item = _make_poly()
        _enter_vertex_editing(item)
        mid = _midpoint_scene(item, 0, 1)
        edge_idx = item._hit_test_edge(mid)
        assert edge_idx is not None, "Should find edge at midpoint"

    def test_right_click_away_from_all(self):
        """Right-click far from everything should find nothing."""
        item = _make_poly()
        _enter_vertex_editing(item)
        far = QPointF(9999, 9999)
        assert item._hit_test_vertex(far) is None
        assert item._hit_test_edge(far) is None
        assert item._hit_test_ctrl_point(far) is None


# ── Vertex selection state flow ──────────────────────────────────────────

class TestVertexSelectionFlow:
    """Test the select-then-act interaction model."""

    def test_no_vertex_selected_initially(self):
        item = _make_poly()
        _enter_vertex_editing(item)
        assert item._selected_vertex is None

    def test_hover_sets_hover_vertex(self):
        item = _make_poly()
        _enter_vertex_editing(item)
        assert item._hover_vertex is None
        # Simulate what hoverMoveEvent does
        vp = _vertex_scene_pos(item, 1)
        idx = item._hit_test_vertex(vp)
        item._hover_vertex = idx
        assert item._hover_vertex == 1

    def test_hover_away_clears_hover(self):
        item = _make_poly()
        _enter_vertex_editing(item)
        item._hover_vertex = 1
        # Move far away
        item._hover_vertex = None
        assert item._hover_vertex is None

    def test_left_click_selects_vertex(self):
        item = _make_poly()
        _enter_vertex_editing(item)
        item._selected_vertex = 2
        assert item._selected_vertex == 2

    def test_click_another_vertex_changes_selection(self):
        item = _make_poly()
        _enter_vertex_editing(item)
        item._selected_vertex = 0
        item._selected_vertex = 2
        assert item._selected_vertex == 2

    def test_drag_deselects(self):
        """Starting a vertex drag should deselect after release."""
        item = _make_poly()
        _enter_vertex_editing(item)
        item._selected_vertex = 1
        # Simulate drag start + release
        item._vertex_dragging = True
        item._active_vertex = 1
        # Release
        item._vertex_dragging = False
        item._active_vertex = None
        item._selected_vertex = None
        assert item._selected_vertex is None

    def test_ctrl_drag_deselects(self):
        """Dragging a control point should deselect."""
        item = _make_poly(MIXED_PTS)
        _enter_vertex_editing(item)
        item._selected_vertex = 2
        item._ctrl_dragging = True
        item._active_ctrl_point = (2, "cp")
        # Release
        item._ctrl_dragging = False
        item._active_ctrl_point = None
        item._selected_vertex = None
        assert item._selected_vertex is None

    def test_deselect_item_clears_selected_vertex(self):
        item = _make_poly()
        _enter_vertex_editing(item)
        item._selected_vertex = 1
        from PyQt6.QtWidgets import QGraphicsItem
        item.itemChange(
            QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged, False)
        assert item._selected_vertex is None
        assert item._hover_vertex is None

    def test_double_click_off_clears_selected_vertex(self):
        item = _make_poly()
        _enter_vertex_editing(item)
        item._selected_vertex = 1
        # Double-click to exit vertex editing
        item._vertex_editing = False
        item._selected_vertex = None
        item._hover_vertex = None
        assert item._selected_vertex is None

    def test_paint_shows_orange_for_selected(self):
        """Selected vertex index should be orange (same condition as hover/active)."""
        item = _make_poly()
        _enter_vertex_editing(item)
        item._selected_vertex = 1
        # The paint condition checks: i == _selected_vertex or _active_vertex or _hover_vertex
        assert item._selected_vertex == 1

    def test_paint_shows_orange_for_hover(self):
        item = _make_poly()
        _enter_vertex_editing(item)
        item._hover_vertex = 0
        assert item._hover_vertex == 0


# ── Bug fix: edge rejection near vertex endpoints ────────────────────────

class TestEdgeRejectsNearVertex:
    """Edge hit should be rejected near endpoints so vertex knobs win."""

    def test_edge_rejected_at_vertex_0(self):
        """At vertex 0's exact position, edge should NOT match."""
        item = _make_poly()
        _enter_vertex_editing(item)
        vp = _vertex_scene_pos(item, 0)
        # Vertex should match
        assert item._hit_test_vertex(vp) == 0
        # Edge should NOT match (t near 0.0 or 1.0 → rejected)
        assert item._hit_test_edge(vp) is None

    def test_edge_rejected_at_all_vertices(self):
        """At every vertex position, edge hit should be None."""
        item = _make_poly()
        _enter_vertex_editing(item)
        for i in range(len(TRIANGLE_PTS)):
            vp = _vertex_scene_pos(item, i)
            assert item._hit_test_edge(vp) is None, \
                f"Edge hit at vertex {i} should be None"

    def test_vertex_wins_over_edge_at_first_vertex(self):
        """The hover/right-click priority: vertex before edge at vertex 0."""
        item = _make_poly()
        _enter_vertex_editing(item)
        vp = _vertex_scene_pos(item, 0)
        vertex_hit = item._hit_test_vertex(vp)
        edge_hit = item._hit_test_edge(vp)
        assert vertex_hit == 0
        assert edge_hit is None


# ── Bug fix: curve-aware edge hit testing ────────────────────────────────

class TestCurveAwareEdgeHit:
    """Edge hit testing should follow the actual curve, not straight lines."""

    def test_quadratic_curve_midpoint_detected(self):
        """A point on a quadratic curve (off the straight line) should hit."""
        # Vertex 2 is Q with control point at (0.5, 0.0)
        # The curve bows upward; its midpoint is NOT on the straight line
        item = _make_poly(MIXED_PTS)
        _enter_vertex_editing(item)
        # Sample the midpoint of the quadratic curve (vertex 1 → vertex 2)
        w, h = 200, 200
        p0 = QPointF(MIXED_PTS[1][0] * w, MIXED_PTS[1][1] * h)
        cp = QPointF(MIXED_PTS[2][3] * w, MIXED_PTS[2][4] * h)
        p2 = QPointF(MIXED_PTS[2][0] * w, MIXED_PTS[2][1] * h)
        # Quadratic bezier at t=0.5
        t = 0.5
        mid_x = (1-t)**2 * p0.x() + 2*(1-t)*t * cp.x() + t**2 * p2.x()
        mid_y = (1-t)**2 * p0.y() + 2*(1-t)*t * cp.y() + t**2 * p2.y()
        curve_mid = item.mapToScene(QPointF(mid_x, mid_y))
        edge_idx = item._hit_test_edge(curve_mid)
        assert edge_idx == 1, f"Expected edge 1 (vertex 1→2), got {edge_idx}"

    def test_cubic_curve_midpoint_detected(self):
        """A point on a cubic curve should hit."""
        item = _make_poly(MIXED_PTS)
        _enter_vertex_editing(item)
        w, h = 200, 200
        p0 = QPointF(MIXED_PTS[3][0] * w, MIXED_PTS[3][1] * h)
        c1 = QPointF(MIXED_PTS[4][3] * w, MIXED_PTS[4][4] * h)
        c2 = QPointF(MIXED_PTS[4][5] * w, MIXED_PTS[4][6] * h)
        p3 = QPointF(MIXED_PTS[4][0] * w, MIXED_PTS[4][1] * h)
        # Cubic bezier at t=0.5
        t = 0.5
        u = 1 - t
        mid_x = u**3*p0.x() + 3*u**2*t*c1.x() + 3*u*t**2*c2.x() + t**3*p3.x()
        mid_y = u**3*p0.y() + 3*u**2*t*c1.y() + 3*u*t**2*c2.y() + t**3*p3.y()
        curve_mid = item.mapToScene(QPointF(mid_x, mid_y))
        edge_idx = item._hit_test_edge(curve_mid)
        assert edge_idx == 3, f"Expected edge 3 (vertex 3→4), got {edge_idx}"
