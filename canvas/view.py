"""
canvas/view.py

QGraphicsView with drag & drop PNG support and enhanced selection behavior.
"""

from __future__ import annotations

from typing import Callable, List, Optional

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QGraphicsView, QGraphicsItem

from canvas.scene import AnnotatorScene
from settings import get_settings


class AnnotatorView(QGraphicsView):
    """
    Graphics view with PNG drag & drop and enhanced selection behavior.

    Selection behavior:
    - Rubber-band selection selects ONLY items fully enclosed by the rubber band
    - Ctrl + Left-click toggles selection membership (add/remove) without clearing others

    Zoom modes:
    - Normal: rubber band selects items
    - Zoom region: rubber band zooms to selected area
    """

    def __init__(self, scene: AnnotatorScene, on_drop_png_cb: Callable[[str], None], parent=None):
        super().__init__(scene, parent)
        self.setAcceptDrops(True)
        self.on_drop_png_cb = on_drop_png_cb
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # Internal state to detect rubber-band usage
        self._rb_active = False
        self._rb_origin = None

        # Zoom region mode
        self._zoom_region_mode = False
        self._on_zoom_region_complete: Optional[Callable[[], None]] = None
        self._saved_drag_mode: Optional[QGraphicsView.DragMode] = None

    def wheelEvent(self, event):
        """Zoom with mouse wheel."""
        delta = event.angleDelta().y()
        # Zoom factor from settings. Default: 1.15 (15% per scroll step)
        zoom_factor = get_settings().settings.canvas.zoom.wheel_factor
        factor = zoom_factor if delta > 0 else 1 / zoom_factor
        self.scale(factor, factor)

    def dragEnterEvent(self, event):
        """Accept PNG and PlantUML file drops."""
        if event.mimeData().hasUrls():
            for u in event.mimeData().urls():
                lf = u.toLocalFile().lower()
                if lf.endswith(".png") or lf.endswith(".puml"):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        """Handle PNG or PlantUML file drop."""
        if event.mimeData().hasUrls():
            for u in event.mimeData().urls():
                path = u.toLocalFile()
                lf = path.lower()
                if lf.endswith(".png") or lf.endswith(".puml"):
                    self.on_drop_png_cb(path)
                    event.acceptProposedAction()
                    return
        event.ignore()

    def mousePressEvent(self, event):
        """Handle mouse press with Ctrl+click toggle selection."""
        # In zoom region mode, just track the rubber band start
        if self._zoom_region_mode and event.button() == Qt.MouseButton.LeftButton:
            self._rb_active = True
            self._rb_origin = event.position().toPoint()
            # Let rubber band work normally, we'll handle zoom in release
            super().mousePressEvent(event)
            return

        # Ctrl + left click toggles selection membership without clearing others
        if event.button() == Qt.MouseButton.LeftButton and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            item = self.itemAt(event.position().toPoint())
            if item is not None and (item.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable):
                # Toggle selection
                item.setSelected(not item.isSelected())
                event.accept()
                return

        # Track possible rubber-band usage
        if event.button() == Qt.MouseButton.LeftButton and self.dragMode() == QGraphicsView.DragMode.RubberBandDrag:
            self._rb_active = True
            self._rb_origin = event.position().toPoint()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release with fully-enclosed selection enforcement."""
        # Handle zoom region mode - get rubber band rect BEFORE calling super
        if self._zoom_region_mode and self._rb_active:
            rb = self.rubberBandRect()

            # Call super to complete the rubber band operation
            super().mouseReleaseEvent(event)

            self._rb_active = False

            # Clear any selection that occurred during the drag
            self.scene().clearSelection()

            if rb.isNull() or rb.width() < 2 or rb.height() < 2:
                # Too small, cancel zoom
                self._zoom_region_mode = False
                if self._saved_drag_mode is not None:
                    self.setDragMode(self._saved_drag_mode)
                    self._saved_drag_mode = None
                self.viewport().unsetCursor()
                if self._on_zoom_region_complete:
                    self._on_zoom_region_complete()
                return

            scene_rect = self.mapToScene(rb).boundingRect()

            # Perform zoom
            self._zoom_region_mode = False
            if self._saved_drag_mode is not None:
                self.setDragMode(self._saved_drag_mode)
                self._saved_drag_mode = None
            self.viewport().unsetCursor()
            self.fitInView(scene_rect, Qt.AspectRatioMode.KeepAspectRatio)
            if self._on_zoom_region_complete:
                self._on_zoom_region_complete()
            return

        super().mouseReleaseEvent(event)

        # If rubber-band was used (normal mode), enforce "fully enclosed" selection
        if self._rb_active and self.dragMode() == QGraphicsView.DragMode.RubberBandDrag:
            self._rb_active = False

            rb = self.rubberBandRect()
            if rb.isNull() or rb.width() < 2 or rb.height() < 2:
                return

            scene_rect = self.mapToScene(rb).boundingRect()

            # Gather candidates intersecting rubber rect, then filter by FULL containment
            candidates = self.scene().items(scene_rect, Qt.ItemSelectionMode.IntersectsItemBoundingRect)
            fully_contained: List[QGraphicsItem] = []
            for it in candidates:
                # Ignore non-selectable items (like background pixmap)
                if not (it.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable):
                    continue
                br = it.sceneBoundingRect()
                if scene_rect.contains(br):
                    fully_contained.append(it)

            ctrl = bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier)
            if not ctrl:
                # Replace selection
                for it in self.scene().selectedItems():
                    it.setSelected(False)

            for it in fully_contained:
                it.setSelected(True)

    def set_zoom_region_mode(self, enabled: bool, on_complete: Optional[Callable[[], None]] = None):
        """Enable or disable zoom region mode.

        When enabled, the next rubber-band drag will zoom to the selected region.
        This temporarily switches to RubberBandDrag mode if not already in it.

        Args:
            enabled: Whether to enable zoom region mode.
            on_complete: Optional callback called when zoom region completes.
        """
        self._zoom_region_mode = enabled
        self._on_zoom_region_complete = on_complete
        if enabled:
            # Save current drag mode and switch to rubber band
            self._saved_drag_mode = self.dragMode()
            if self._saved_drag_mode != QGraphicsView.DragMode.RubberBandDrag:
                self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            # Set cursor on viewport for QGraphicsView
            self.viewport().setCursor(Qt.CursorShape.CrossCursor)
        else:
            # Restore previous drag mode
            if self._saved_drag_mode is not None:
                self.setDragMode(self._saved_drag_mode)
                self._saved_drag_mode = None
            self.viewport().unsetCursor()

    def keyPressEvent(self, event):
        """Handle key press events."""
        # Escape cancels zoom region mode
        if event.key() == Qt.Key.Key_Escape and self._zoom_region_mode:
            self._zoom_region_mode = False
            if self._saved_drag_mode is not None:
                self.setDragMode(self._saved_drag_mode)
                self._saved_drag_mode = None
            self.viewport().unsetCursor()
            if self._on_zoom_region_complete:
                self._on_zoom_region_complete()
            event.accept()
            return
        super().keyPressEvent(event)

    def zoom_fit(self):
        """Zoom to fit the entire scene in the view."""
        scene_rect = self.scene().itemsBoundingRect()
        if scene_rect.isNull() or scene_rect.isEmpty():
            # If no items, try scene rect
            scene_rect = self.scene().sceneRect()
        if not scene_rect.isNull() and not scene_rect.isEmpty():
            # Add small margin
            margin = 20
            scene_rect = scene_rect.adjusted(-margin, -margin, margin, margin)
            self.fitInView(scene_rect, Qt.AspectRatioMode.KeepAspectRatio)

    def zoom_reset(self):
        """Reset zoom to 100% (1:1 scale)."""
        self.resetTransform()

    def zoom_in(self):
        """Zoom in by the configured factor."""
        zoom_factor = get_settings().settings.canvas.zoom.wheel_factor
        self.scale(zoom_factor, zoom_factor)

    def zoom_out(self):
        """Zoom out by the configured factor."""
        zoom_factor = get_settings().settings.canvas.zoom.wheel_factor
        self.scale(1 / zoom_factor, 1 / zoom_factor)
