"""
canvas/view.py

QGraphicsView with drag & drop PNG support and enhanced selection behavior.
"""

from __future__ import annotations

from typing import Callable, List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QGraphicsView, QGraphicsItem

from canvas.scene import AnnotatorScene


class AnnotatorView(QGraphicsView):
    """
    Graphics view with PNG drag & drop and enhanced selection behavior.

    Selection behavior:
    - Rubber-band selection selects ONLY items fully enclosed by the rubber band
    - Ctrl + Left-click toggles selection membership (add/remove) without clearing others
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

    def wheelEvent(self, event):
        """Zoom with mouse wheel."""
        delta = event.angleDelta().y()
        factor = 1.15 if delta > 0 else 1 / 1.15
        self.scale(factor, factor)

    def dragEnterEvent(self, event):
        """Accept PNG file drops."""
        if event.mimeData().hasUrls():
            for u in event.mimeData().urls():
                if u.toLocalFile().lower().endswith(".png"):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        """Handle PNG file drop."""
        if event.mimeData().hasUrls():
            for u in event.mimeData().urls():
                path = u.toLocalFile()
                if path.lower().endswith(".png"):
                    self.on_drop_png_cb(path)
                    event.acceptProposedAction()
                    return
        event.ignore()

    def mousePressEvent(self, event):
        """Handle mouse press with Ctrl+click toggle selection."""
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
        super().mouseReleaseEvent(event)

        # If rubber-band was used, enforce "fully enclosed" selection
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
