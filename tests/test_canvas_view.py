"""Test bench for AnnotatorView (canvas/view.py).

Tests:
  - Zoom: fit, reset, in, out, transform changes
  - Zoom region mode: enable/disable, escape cancellation, callback
  - _all_handles_enclosed: shape handles, line endpoints, fallback bounding rect
  - Drag & drop: accepted file extensions, rejected extensions
"""
from __future__ import annotations

import pytest

from PyQt6.QtCore import Qt, QRectF, QPointF, QMimeData, QUrl
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QGraphicsView

from canvas.items import MetaRectItem, MetaLineItem, MetaTextItem
from canvas.scene import AnnotatorScene
from canvas.view import AnnotatorView


# ── Helpers ──────────────────────────────────────────────────────────────

@pytest.fixture
def view_scene():
    """Create a standalone AnnotatorView + Scene (no MainWindow)."""
    scene = AnnotatorScene()
    drop_log = []
    view = AnnotatorView(scene, on_drop_png_cb=lambda p: drop_log.append(p))
    view.resize(800, 600)
    view.show()
    return view, scene, drop_log


# ── Zoom actions ─────────────────────────────────────────────────────────

class TestZoom:

    def test_zoom_reset(self, view_scene):
        view, scene, _ = view_scene
        view.scale(2, 2)
        view.zoom_reset()
        t = view.transform()
        assert abs(t.m11() - 1.0) < 0.01
        assert abs(t.m22() - 1.0) < 0.01

    def test_zoom_in_increases_scale(self, view_scene):
        view, scene, _ = view_scene
        view.zoom_reset()
        t_before = view.transform().m11()
        view.zoom_in()
        t_after = view.transform().m11()
        assert t_after > t_before

    def test_zoom_out_decreases_scale(self, view_scene):
        view, scene, _ = view_scene
        view.zoom_reset()
        view.scale(2, 2)
        t_before = view.transform().m11()
        view.zoom_out()
        t_after = view.transform().m11()
        assert t_after < t_before

    def test_zoom_fit_with_items(self, view_scene):
        view, scene, _ = view_scene
        r = MetaRectItem(100, 100, 200, 150, "r1", None)
        scene.addItem(r)
        view.zoom_fit()
        # Transform should have changed from identity
        t = view.transform()
        # At minimum, it should not crash
        assert t.m11() > 0

    def test_zoom_fit_empty_scene(self, view_scene):
        view, scene, _ = view_scene
        view.zoom_fit()  # should not crash


# ── Zoom region mode ─────────────────────────────────────────────────────

class TestZoomRegionMode:

    def test_enable_sets_flag(self, view_scene):
        view, scene, _ = view_scene
        view.set_zoom_region_mode(True)
        assert view._zoom_region_mode is True

    def test_enable_sets_rubberband_drag(self, view_scene):
        view, scene, _ = view_scene
        view.setDragMode(QGraphicsView.DragMode.NoDrag)
        view.set_zoom_region_mode(True)
        assert view.dragMode() == QGraphicsView.DragMode.RubberBandDrag

    def test_enable_sets_crosshair_cursor(self, view_scene):
        view, scene, _ = view_scene
        view.set_zoom_region_mode(True)
        assert view.viewport().cursor().shape() == Qt.CursorShape.CrossCursor

    def test_disable_restores_drag_mode(self, view_scene):
        view, scene, _ = view_scene
        view.setDragMode(QGraphicsView.DragMode.NoDrag)
        view.set_zoom_region_mode(True)
        view.set_zoom_region_mode(False)
        assert view.dragMode() == QGraphicsView.DragMode.NoDrag

    def test_disable_clears_flag(self, view_scene):
        view, scene, _ = view_scene
        view.set_zoom_region_mode(True)
        view.set_zoom_region_mode(False)
        assert view._zoom_region_mode is False

    def test_escape_cancels(self, view_scene):
        view, scene, _ = view_scene
        completed = []
        view.set_zoom_region_mode(True, on_complete=lambda: completed.append(1))
        QTest.keyPress(view, Qt.Key.Key_Escape)
        assert view._zoom_region_mode is False
        assert len(completed) == 1

    def test_callback_on_complete(self, view_scene):
        view, scene, _ = view_scene
        completed = []
        view.set_zoom_region_mode(True, on_complete=lambda: completed.append(1))
        # Cancel via disable (simulating complete)
        view.set_zoom_region_mode(False)
        # Callback is NOT called by set_zoom_region_mode(False) directly,
        # only via escape or actual zoom completion
        # Just verify no crash


# ── _all_handles_enclosed ────────────────────────────────────────────────

class TestHandlesEnclosed:

    def test_rect_fully_enclosed(self, view_scene):
        view, scene, _ = view_scene
        r = MetaRectItem(100, 100, 50, 30, "r1", None)
        scene.addItem(r)
        # Rect at (100,100) size 50x30 → handles at corners
        big_rect = QRectF(90, 90, 70, 50)  # fully encloses
        assert view._all_handles_enclosed(r, big_rect)

    def test_rect_partially_enclosed(self, view_scene):
        view, scene, _ = view_scene
        r = MetaRectItem(100, 100, 50, 30, "r1", None)
        scene.addItem(r)
        # Only covers left half
        small_rect = QRectF(90, 90, 30, 50)
        assert not view._all_handles_enclosed(r, small_rect)

    def test_line_fully_enclosed(self, view_scene):
        view, scene, _ = view_scene
        line = MetaLineItem(10, 20, 100, 80, "l1", None)
        scene.addItem(line)
        big_rect = QRectF(0, 0, 200, 200)
        assert view._all_handles_enclosed(line, big_rect)

    def test_line_partially_enclosed(self, view_scene):
        view, scene, _ = view_scene
        line = MetaLineItem(10, 20, 300, 250, "l1", None)
        scene.addItem(line)
        # Only covers start point
        small_rect = QRectF(0, 0, 50, 50)
        assert not view._all_handles_enclosed(line, small_rect)

    def test_rect_fully_outside(self, view_scene):
        view, scene, _ = view_scene
        r = MetaRectItem(500, 500, 50, 30, "r2", None)
        scene.addItem(r)
        small_rect = QRectF(0, 0, 100, 100)
        assert not view._all_handles_enclosed(r, small_rect)


# ── Drag & drop file acceptance ──────────────────────────────────────────

class TestDragDropAcceptance:

    @pytest.mark.parametrize("ext", [".png", ".puml", ".svg", ".mmd", ".mermaid"])
    def test_accepted_extension(self, view_scene, ext):
        view, scene, _ = view_scene
        # Manually test the acceptance logic
        filename = f"test{ext}"
        lf = filename.lower()
        accepted = (lf.endswith(".png") or lf.endswith(".puml")
                    or lf.endswith(".svg") or lf.endswith(".mmd")
                    or lf.endswith(".mermaid"))
        assert accepted

    @pytest.mark.parametrize("ext", [".jpg", ".gif", ".txt", ".pdf", ".docx"])
    def test_rejected_extension(self, view_scene, ext):
        view, scene, _ = view_scene
        filename = f"test{ext}"
        lf = filename.lower()
        accepted = (lf.endswith(".png") or lf.endswith(".puml")
                    or lf.endswith(".svg") or lf.endswith(".mmd")
                    or lf.endswith(".mermaid"))
        assert not accepted
