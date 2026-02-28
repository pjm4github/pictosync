"""
canvas/scene.py

QGraphicsScene with drawing mode support for creating annotation items.
"""

from __future__ import annotations

from typing import Callable, List, Optional

from PyQt6.QtCore import Qt, QPointF, QRectF, QLineF
from PyQt6.QtGui import QAction, QPainterPath, QPen, QColor
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsItem, QGraphicsPathItem, QMenu

from models import Mode
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
    MetaGroupItem,
)
from settings import get_settings


def _get_z_index_base() -> int:
    """Get z-index base from settings. Default: 1000."""
    return get_settings().settings.canvas.zorder.base


def _get_z_index_step() -> int:
    """Get z-index step from settings. Default: 10."""
    return get_settings().settings.canvas.zorder.step


class AnnotatorScene(QGraphicsScene):
    """
    Graphics scene with drawing mode support.

    Supports creating shapes (rect, rounded rect, ellipse, line, text)
    by clicking and dragging in the appropriate mode.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode = Mode.SELECT
        self._drag_start: Optional[QPointF] = None
        self._temp_item: Optional[QGraphicsItem] = None
        self._make_id: Optional[Callable[[], str]] = None
        self._on_new_item: Optional[Callable[[QGraphicsItem], None]] = None
        self._on_item_changed: Optional[Callable[[QGraphicsItem], None]] = None
        self._on_right_click: Optional[Callable[[], None]] = None  # For exiting sticky mode
        self._on_escape_key: Optional[Callable[[], None]] = None  # For exiting sticky mode
        self._on_z_order_changed: Optional[Callable[[], None]] = None  # For z-order changes
        self._on_group_items: Optional[Callable[[list], None]] = None  # For grouping items
        self._on_ungroup_item: Optional[Callable] = None  # For ungrouping
        self._on_items_moved: Optional[Callable] = None  # For move undo tracking
        self._on_select_mouse_up: Optional[Callable] = None  # For scroll-on-release
        self._on_build_dsl_item: Optional[Callable] = None  # For "Build DSL Item" context menu
        self._undo_act = None  # QAction for undo (set from main.py)
        self._redo_act = None  # QAction for redo (set from main.py)
        # Move tracking state
        self._move_start_positions: dict = {}
        self._mouse_down_in_select = False
        # Polygon multi-click drawing state
        self._polygon_points: List[QPointF] = []
        self._polygon_preview: Optional[QGraphicsItem] = None
        # Curve multi-click drawing state
        self._curve_points: List[QPointF] = []
        self._curve_preview: Optional[QGraphicsItem] = None
        # Orthogonal curve direction tracking ("H" or "V")
        self._ortho_direction: Optional[str] = None

    @property
    def is_interacting(self) -> bool:
        """True while the user has the mouse down in SELECT mode."""
        if self._mouse_down_in_select:
            return True
        # Check if any selected item is being resized / endpoint-dragged
        for item in self.selectedItems():
            if getattr(item, "_resizing", False):
                return True
            if getattr(item, "_drag_end", None):
                return True
            if getattr(item, "_drag_text_box", None):
                return True
        return False

    def set_z_order_changed_callback(self, callback: Optional[Callable[[], None]]):
        """Set callback for when z-order changes (used to sync JSON)."""
        self._on_z_order_changed = callback

    def set_mode(self, mode: str) -> None:
        """Set the current drawing mode."""
        self.mode = mode

    def configure_linkage(
        self,
        make_id: Callable[[], str],
        on_new_item: Callable[[QGraphicsItem], None],
        on_item_changed: Callable[[QGraphicsItem], None],
    ):
        """
        Configure callbacks for JSON<->Scene linkage.

        Args:
            make_id: Function to generate new annotation IDs
            on_new_item: Callback when a new item is created
            on_item_changed: Callback when an item's geometry/style changes
        """
        self._make_id = make_id
        self._on_new_item = on_new_item
        self._on_item_changed = on_item_changed

    def set_right_click_callback(self, callback: Optional[Callable[[], None]]):
        """Set callback for right-click (used to exit sticky tool mode)."""
        self._on_right_click = callback

    def set_escape_key_callback(self, callback: Optional[Callable[[], None]]):
        """Set callback for Escape key (used to exit sticky tool mode)."""
        self._on_escape_key = callback

    def set_on_items_moved(self, callback):
        """Set callback for when items are moved (used for move undo)."""
        self._on_items_moved = callback

    def set_on_select_mouse_up(self, callback):
        """Set callback for mouse release in SELECT mode (scroll-on-release)."""
        self._on_select_mouse_up = callback

    def set_build_dsl_callback(self, callback):
        """Set callback for the 'Build DSL Item' context menu action."""
        self._on_build_dsl_item = callback

    def set_undo_actions(self, undo_act, redo_act):
        """Set undo/redo actions for use in context menus."""
        self._undo_act = undo_act
        self._redo_act = redo_act

    @staticmethod
    def _geometry_hash(item) -> tuple:
        """Return a hashable geometry snapshot excluding position."""
        if hasattr(item, '_capture_child_states'):
            cbr = item.childrenBoundingRect()
            return ("group", round(cbr.width(), 2), round(cbr.height(), 2))
        if hasattr(item, 'setRect') and hasattr(item, 'rect') and not hasattr(item, '_update_path'):
            r = item.rect()
            return ("rect", round(r.width(), 2), round(r.height(), 2))
        if hasattr(item, '_width') and hasattr(item, '_update_path'):
            return ("path", round(item._width, 2), round(item._height, 2))
        if hasattr(item, 'setLine') and hasattr(item, 'line'):
            ln = item.line()
            return ("line", round(ln.dx(), 2), round(ln.dy(), 2))
        return ("pos_only",)

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Escape:
            # Cancel polygon drawing on Escape
            if self.mode == Mode.POLYGON and self._polygon_points:
                self._cancel_polygon()
                event.accept()
                return
            # Cancel curve drawing on Escape
            if self.mode in (Mode.CURVE, Mode.ORTHOCURVE) and self._curve_points:
                self._cancel_curve()
                event.accept()
                return
            if self._on_escape_key:
                self._on_escape_key()
                event.accept()
                return
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        # Snapshot positions for move tracking in SELECT mode
        if event.button() == Qt.MouseButton.LeftButton and self.mode == Mode.SELECT:
            self._mouse_down_in_select = True
            self._move_start_positions = {}
            for item in self.selectedItems():
                if hasattr(item, 'ann_id'):
                    self._move_start_positions[item] = (
                        QPointF(item.pos()),
                        self._geometry_hash(item),
                    )

        # Right-click: close polygon if drawing, show context menu, or exit sticky mode
        if event.button() == Qt.MouseButton.RightButton:
            # Polygon close/cancel on right-click
            if self.mode == Mode.POLYGON and self._polygon_points:
                if len(self._polygon_points) >= 3:
                    self._finish_polygon()
                else:
                    self._cancel_polygon()
                event.accept()
                return

            # Curve finish/cancel on right-click — capture click as final point
            if self.mode in (Mode.CURVE, Mode.ORTHOCURVE) and self._curve_points:
                sp = event.scenePos()
                if self.mode == Mode.ORTHOCURVE:
                    sp = self._commit_ortho_point(sp)
                self._curve_points.append(sp)
                if len(self._curve_points) >= 2:
                    self._finish_curve()
                else:
                    self._cancel_curve()
                event.accept()
                return

            item = self.itemAt(event.scenePos(), self.views()[0].transform() if self.views() else None)
            # Walk up to top-level selectable item (may be a group)
            while item and item.parentItem() and isinstance(item.parentItem(), MetaGroupItem):
                item = item.parentItem()
            # Check if the item is one of our annotation items (not background)
            if item and self._is_annotation_item(item) and item.isSelected():
                # Let polygon handle right-click in vertex editing mode
                if isinstance(item, MetaPolygonItem) and item._vertex_editing:
                    super().mousePressEvent(event)
                    return
                # Let curve handle right-click in node editing mode
                if isinstance(item, (MetaCurveItem, MetaOrthoCurveItem)) and item._node_editing:
                    super().mousePressEvent(event)
                    return
                self._show_context_menu(event.screenPos(), item)
                event.accept()
                return
            elif self._on_right_click:
                self._on_right_click()
                event.accept()
                return

        if event.button() == Qt.MouseButton.LeftButton:
            sp = event.scenePos()

            # Polygon multi-click mode
            if self.mode == Mode.POLYGON:
                self._polygon_points.append(sp)
                self._update_polygon_preview(sp)
                event.accept()
                return

            # Curve multi-click mode
            if self.mode == Mode.CURVE:
                self._curve_points.append(sp)
                self._update_curve_preview(sp)
                event.accept()
                return

            # Orthogonal curve multi-click mode
            if self.mode == Mode.ORTHOCURVE:
                snapped = self._commit_ortho_point(sp)
                self._curve_points.append(snapped)
                self._update_curve_preview(snapped)
                event.accept()
                return

            if self.mode in (Mode.RECT, Mode.ROUNDEDRECT, Mode.ELLIPSE, Mode.LINE, Mode.HEXAGON, Mode.CYLINDER, Mode.BLOCKARROW, Mode.ISOCUBE):
                self._drag_start = sp
                ann_id = self._make_id() if self._make_id else "local"
                next_z = self._get_next_z_index()

                if self.mode == Mode.RECT:
                    self._temp_item = MetaRectItem(sp.x(), sp.y(), 0, 0, ann_id, self._on_item_changed)
                    self.addItem(self._temp_item)
                    self._temp_item.setZValue(next_z)
                elif self.mode == Mode.ROUNDEDRECT:
                    # Default rounded radius from settings. Default: 10 pixels
                    default_radius = get_settings().settings.canvas.shapes.default_rounded_radius
                    self._temp_item = MetaRoundedRectItem(sp.x(), sp.y(), 0, 0, default_radius, ann_id, self._on_item_changed)
                    self.addItem(self._temp_item)
                    self._temp_item.setZValue(next_z)
                elif self.mode == Mode.ELLIPSE:
                    self._temp_item = MetaEllipseItem(sp.x(), sp.y(), 0, 0, ann_id, self._on_item_changed)
                    self.addItem(self._temp_item)
                    self._temp_item.setZValue(next_z)
                elif self.mode == Mode.LINE:
                    self._temp_item = MetaLineItem(sp.x(), sp.y(), sp.x(), sp.y(), ann_id, self._on_item_changed)
                    self.addItem(self._temp_item)
                    self._temp_item.setZValue(next_z)
                elif self.mode == Mode.HEXAGON:
                    # Default adjust1=0.25 (indent ratio for regular hexagon proportions)
                    self._temp_item = MetaHexagonItem(sp.x(), sp.y(), 0, 0, 0.25, ann_id, self._on_item_changed)
                    self.addItem(self._temp_item)
                    self._temp_item.setZValue(next_z)
                elif self.mode == Mode.CYLINDER:
                    # Default adjust1=0.15 (cap ratio)
                    self._temp_item = MetaCylinderItem(sp.x(), sp.y(), 0, 0, 0.15, ann_id, self._on_item_changed)
                    self.addItem(self._temp_item)
                    self._temp_item.setZValue(next_z)
                elif self.mode == Mode.BLOCKARROW:
                    # adjust2 tracks 35% of width during drawing; adjust1=0.5 (shaft width ratio)
                    self._temp_item = MetaBlockArrowItem(sp.x(), sp.y(), 0, 0, 0, 0.5, ann_id, self._on_item_changed)
                    self.addItem(self._temp_item)
                    self._temp_item.setZValue(next_z)
                elif self.mode == Mode.ISOCUBE:
                    self._temp_item = MetaIsoCubeItem(sp.x(), sp.y(), 0, 0, 30, 135, ann_id, self._on_item_changed)
                    self.addItem(self._temp_item)
                    self._temp_item.setZValue(next_z)

                event.accept()
                return

            elif self.mode == Mode.TEXT:
                ann_id = self._make_id() if self._make_id else "local"
                ti = MetaTextItem(sp.x(), sp.y(), "Double-click to edit", ann_id, self._on_item_changed)
                self.addItem(ti)
                ti.setZValue(self._get_next_z_index())
                ti.setSelected(True)
                if self._on_new_item:
                    self._on_new_item(ti)
                event.accept()
                return

        # In SELECT mode, ensure clicking on a group child selects the group
        if event.button() == Qt.MouseButton.LeftButton and self.mode == Mode.SELECT:
            item = self.itemAt(event.scenePos(), self.views()[0].transform() if self.views() else None)
            if item and isinstance(item.parentItem(), MetaGroupItem):
                # Walk up to the top-level group
                group = item.parentItem()
                while isinstance(group.parentItem(), MetaGroupItem):
                    group = group.parentItem()
                # Let Qt handle default behavior first, then select the group
                super().mousePressEvent(event)
                if not event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    self.clearSelection()
                group.setSelected(True)
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # Polygon preview: dashed line from last point to cursor
        if self.mode == Mode.POLYGON and self._polygon_points:
            self._update_polygon_preview(event.scenePos())
            event.accept()
            return

        # Curve preview: dashed line from last point to cursor
        if self.mode == Mode.CURVE and self._curve_points:
            self._update_curve_preview(event.scenePos())
            event.accept()
            return

        # Ortho curve preview with snapped cursor position
        if self.mode == Mode.ORTHOCURVE and self._curve_points:
            snapped = self._peek_ortho_snap(event.scenePos())
            self._update_curve_preview(snapped)
            event.accept()
            return

        if self._drag_start is not None and self._temp_item is not None:
            cur = event.scenePos()
            sx, sy = self._drag_start.x(), self._drag_start.y()
            cx, cy = cur.x(), cur.y()

            if isinstance(self._temp_item, (MetaRectItem, MetaEllipseItem, MetaRoundedRectItem, MetaHexagonItem, MetaCylinderItem, MetaBlockArrowItem, MetaIsoCubeItem)):
                x = min(sx, cx)
                y = min(sy, cy)
                w = abs(cx - sx)
                h = abs(cy - sy)
                self._temp_item.setPos(QPointF(x, y))
                self._temp_item.setRect(QRectF(0, 0, w, h))
                # Keep arrow head at 35% of width while drawing
                if isinstance(self._temp_item, MetaBlockArrowItem):
                    self._temp_item.set_adjust2(w * 0.35)
            elif isinstance(self._temp_item, MetaLineItem):
                x1, y1 = sx, sy
                x2, y2 = cx, cy
                self._temp_item.setPos(QPointF(x1, y1))
                self._temp_item.setLine(QLineF(0, 0, x2 - x1, y2 - y1))

            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._drag_start is not None and self._temp_item is not None:
            if self._on_new_item:
                self._on_new_item(self._temp_item)

            self._drag_start = None
            self._temp_item = None
            event.accept()
            return

        super().mouseReleaseEvent(event)

        # Detect moves in SELECT mode (after super completes the drag)
        if self._move_start_positions:
            moved = {}
            for item, (old_pos, old_hash) in self._move_start_positions.items():
                if item.pos() != old_pos and self._geometry_hash(item) == old_hash:
                    moved[item] = (old_pos, QPointF(item.pos()))
            if moved and self._on_items_moved:
                self._on_items_moved(moved)
            self._move_start_positions = {}

        # Clear mouse-down flag and notify MainWindow to unlock scroll
        if self._mouse_down_in_select:
            self._mouse_down_in_select = False
            if self._on_select_mouse_up:
                self._on_select_mouse_up()

    def _is_annotation_item(self, item: QGraphicsItem) -> bool:
        """Check if an item is one of our annotation items."""
        return isinstance(item, (MetaRectItem, MetaRoundedRectItem, MetaEllipseItem, MetaLineItem, MetaTextItem, MetaHexagonItem, MetaCylinderItem, MetaBlockArrowItem, MetaPolygonItem, MetaCurveItem, MetaOrthoCurveItem, MetaIsoCubeItem, MetaGroupItem))

    def _get_annotation_items(self) -> List[QGraphicsItem]:
        """Get all annotation items in the scene (excluding background, etc.)."""
        return [item for item in self.items() if self._is_annotation_item(item)]

    def _get_next_z_index(self) -> float:
        """Get the next z-index for a new item (higher than all existing items)."""
        items = self._get_annotation_items()
        if not items:
            return _get_z_index_base()
        max_z = max(i.zValue() for i in items)
        return max_z + _get_z_index_step()

    # ---- Polygon drawing helpers ----

    def _update_polygon_preview(self, cursor_pos: QPointF):
        """Update the polygon preview path showing placed vertices and cursor position."""
        if not self._polygon_points:
            return

        path = QPainterPath()
        path.moveTo(self._polygon_points[0])
        for pt in self._polygon_points[1:]:
            path.lineTo(pt)
        # Dashed line from last point to cursor
        path.lineTo(cursor_pos)

        if self._polygon_preview is None:
            self._polygon_preview = QGraphicsPathItem()
            pen = QPen(QColor(80, 80, 255, 180), 1.5, Qt.PenStyle.DashLine)
            self._polygon_preview.setPen(pen)
            self._polygon_preview.setZValue(999999)  # On top of everything
            self.addItem(self._polygon_preview)

        self._polygon_preview.setPath(path)

    def _finish_polygon(self):
        """Create a MetaPolygonItem from the collected polygon points."""
        points = self._polygon_points

        # Compute bounding box
        xs = [p.x() for p in points]
        ys = [p.y() for p in points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        w = max_x - min_x
        h = max_y - min_y

        # Ensure minimum size
        if w < 5:
            w = 5
        if h < 5:
            h = 5

        # Convert absolute points to relative (0-1) within bounding box
        rel_points = []
        for p in points:
            rx = (p.x() - min_x) / w if w > 0 else 0.0
            ry = (p.y() - min_y) / h if h > 0 else 0.0
            rel_points.append([rx, ry])

        ann_id = self._make_id() if self._make_id else "local"
        next_z = self._get_next_z_index()

        item = MetaPolygonItem(min_x, min_y, w, h, rel_points, ann_id, self._on_item_changed)
        self.addItem(item)
        item.setZValue(next_z)

        if self._on_new_item:
            self._on_new_item(item)

        self._cleanup_polygon_preview()

    def _cancel_polygon(self):
        """Cancel the current polygon drawing operation."""
        self._cleanup_polygon_preview()

    def _cleanup_polygon_preview(self):
        """Remove the polygon preview and reset state."""
        if self._polygon_preview is not None:
            self.removeItem(self._polygon_preview)
            self._polygon_preview = None
        self._polygon_points.clear()

    # ---- Curve drawing helpers ----

    def _update_curve_preview(self, cursor_pos: QPointF):
        """Update the curve preview path showing placed points and cursor position."""
        if not self._curve_points:
            return

        path = QPainterPath()
        path.moveTo(self._curve_points[0])
        for pt in self._curve_points[1:]:
            path.lineTo(pt)
        # Dashed line from last point to cursor
        path.lineTo(cursor_pos)

        if self._curve_preview is None:
            self._curve_preview = QGraphicsPathItem()
            if self.mode == Mode.ORTHOCURVE:
                pen = QPen(QColor(80, 160, 220, 180), 1.5, Qt.PenStyle.DashLine)
            else:
                pen = QPen(QColor(160, 80, 220, 180), 1.5, Qt.PenStyle.DashLine)
            self._curve_preview.setPen(pen)
            self._curve_preview.setZValue(999999)
            self.addItem(self._curve_preview)

        self._curve_preview.setPath(path)

    def _finish_curve(self):
        """Create a MetaCurveItem from collected curve points."""
        points = self._curve_points
        is_ortho = self.mode == Mode.ORTHOCURVE

        # Compute bounding box
        xs = [p.x() for p in points]
        ys = [p.y() for p in points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        w = max_x - min_x
        h = max_y - min_y

        if w < 5:
            w = 5
        if h < 5:
            h = 5

        # Convert to nodes
        nodes = []
        for i, p in enumerate(points):
            rx = (p.x() - min_x) / w if w > 0 else 0.0
            ry = (p.y() - min_y) / h if h > 0 else 0.0
            if i == 0:
                nodes.append({"cmd": "M", "x": rx, "y": ry})
            elif is_ortho and i > 0:
                prev = points[i - 1]
                prev_rx = (prev.x() - min_x) / w if w > 0 else 0.0
                prev_ry = (prev.y() - min_y) / h if h > 0 else 0.0
                if abs(ry - prev_ry) < 1e-6:
                    # Same Y → horizontal segment
                    nodes.append({"cmd": "H", "x": rx})
                elif abs(rx - prev_rx) < 1e-6:
                    # Same X → vertical segment
                    nodes.append({"cmd": "V", "y": ry})
                else:
                    nodes.append({"cmd": "L", "x": rx, "y": ry})
            else:
                nodes.append({"cmd": "L", "x": rx, "y": ry})

        ann_id = self._make_id() if self._make_id else "local"
        next_z = self._get_next_z_index()

        if is_ortho:
            item = MetaOrthoCurveItem(min_x, min_y, w, h, nodes, ann_id, self._on_item_changed)
            item.set_adjust1(10.0)  # Default bend radius for ortho curves
        else:
            item = MetaCurveItem(min_x, min_y, w, h, nodes, ann_id, self._on_item_changed)
        self.addItem(item)
        item.setZValue(next_z)

        if self._on_new_item:
            self._on_new_item(item)

        self._cleanup_curve_preview()

    def _cancel_curve(self):
        """Cancel the current curve drawing operation."""
        self._cleanup_curve_preview()

    def _cleanup_curve_preview(self):
        """Remove the curve preview and reset state."""
        if self._curve_preview is not None:
            self.removeItem(self._curve_preview)
            self._curve_preview = None
        self._curve_points.clear()
        self._ortho_direction = None

    # ---- Orthogonal curve snap helpers ----

    def _peek_ortho_snap(self, pt: QPointF) -> QPointF:
        """Return snapped point for ortho curve WITHOUT mutating direction state."""
        if not self._curve_points:
            return pt
        last = self._curve_points[-1]
        dx = abs(pt.x() - last.x())
        dy = abs(pt.y() - last.y())

        if self._ortho_direction is None:
            # First segment: infer from cursor position
            if dx >= dy:
                return QPointF(pt.x(), last.y())  # H
            else:
                return QPointF(last.x(), pt.y())  # V
        elif self._ortho_direction == "H":
            # Last was H → next is V
            return QPointF(last.x(), pt.y())
        else:
            # Last was V → next is H
            return QPointF(pt.x(), last.y())

    def _commit_ortho_point(self, pt: QPointF) -> QPointF:
        """Return snapped point and toggle direction for next segment."""
        snapped = self._peek_ortho_snap(pt)
        if not self._curve_points:
            return snapped
        last = self._curve_points[-1]
        dx = abs(snapped.x() - last.x())
        dy = abs(snapped.y() - last.y())

        if self._ortho_direction is None:
            # First segment: determine direction
            self._ortho_direction = "H" if dx >= dy else "V"
        elif self._ortho_direction == "H":
            self._ortho_direction = "V"
        else:
            self._ortho_direction = "H"

        return snapped

    def _show_context_menu(self, screen_pos, item: QGraphicsItem):
        """Show context menu for the selected item."""
        menu = QMenu()
        selected = self.selectedItems()

        # Undo/Redo
        if self._undo_act:
            menu.addAction(self._undo_act)
        if self._redo_act:
            menu.addAction(self._redo_act)
        if self._undo_act or self._redo_act:
            menu.addSeparator()

        # Group option: multiple items selected
        if len(selected) > 1:
            group_act = QAction("Group", menu)
            group_act.triggered.connect(lambda: self._request_group(selected))
            menu.addAction(group_act)
            menu.addSeparator()

        # Ungroup option: single group selected
        if isinstance(item, MetaGroupItem):
            ungroup_act = QAction("Ungroup", menu)
            ungroup_act.triggered.connect(lambda: self._request_ungroup(item))
            menu.addAction(ungroup_act)
            menu.addSeparator()

        bring_to_front = QAction("Bring to Front", menu)
        bring_to_front.triggered.connect(lambda: self._bring_to_front(item))
        menu.addAction(bring_to_front)

        send_to_back = QAction("Send to Back", menu)
        send_to_back.triggered.connect(lambda: self._send_to_back(item))
        menu.addAction(send_to_back)

        if self._on_build_dsl_item and len(selected) == 1:
            menu.addSeparator()
            build_dsl_act = QAction("Build DSL Item", menu)
            build_dsl_act.triggered.connect(lambda: self._on_build_dsl_item(item))
            menu.addAction(build_dsl_act)

        # screenPos() returns QPoint in PyQt6
        menu.exec(screen_pos)

    def _bring_to_front(self, item: QGraphicsItem):
        """
        Bring the item to the front of all other annotation items.

        Resets all z-indices to make room and puts this item at the top.
        """
        items = self._get_annotation_items()
        if len(items) <= 1:
            return

        # Remove the target item from the list
        items = [i for i in items if i is not item]

        # Sort remaining items by current zValue (lowest first)
        items.sort(key=lambda i: i.zValue())

        # Reassign z-indices with gaps, starting from base
        for idx, i in enumerate(items):
            new_z = _get_z_index_base() + (idx * _get_z_index_step())
            i.setZValue(new_z)

        # Put target item at the front (highest z)
        front_z = _get_z_index_base() + (len(items) * _get_z_index_step())
        item.setZValue(front_z)

        # Notify that z-order changed
        if self._on_z_order_changed:
            self._on_z_order_changed()

    def _send_to_back(self, item: QGraphicsItem):
        """
        Send the item to the back of all other annotation items.

        Finds the backmost item and places this one behind it.
        If no room, resets all z-indices.
        """
        items = self._get_annotation_items()
        if len(items) <= 1:
            return

        # Find the minimum z-value among all items
        min_z = min(i.zValue() for i in items)

        # Try to place behind the backmost item
        new_z = min_z - _get_z_index_step()

        # If we would go too low, reset all z-indices
        if new_z < 0:
            # Remove the target item from the list
            other_items = [i for i in items if i is not item]

            # Sort remaining items by current zValue (lowest first)
            other_items.sort(key=lambda i: i.zValue())

            # Put target item at the back (lowest z)
            item.setZValue(_get_z_index_base())

            # Reassign z-indices for other items with gaps
            for idx, i in enumerate(other_items):
                new_z = _get_z_index_base() + ((idx + 1) * _get_z_index_step())
                i.setZValue(new_z)
        else:
            # Just set the new z-value
            item.setZValue(new_z)

        # Notify that z-order changed
        if self._on_z_order_changed:
            self._on_z_order_changed()

    def set_group_callbacks(self, on_group, on_ungroup):
        """Set callbacks for group/ungroup operations."""
        self._on_group_items = on_group
        self._on_ungroup_item = on_ungroup

    def _request_group(self, items):
        """Request grouping of items via callback."""
        if self._on_group_items:
            self._on_group_items(list(items))

    def _request_ungroup(self, group_item):
        """Request ungrouping via callback."""
        if self._on_ungroup_item:
            self._on_ungroup_item(group_item)

    def _get_top_level_annotation_items(self) -> list:
        """Get annotation items that are NOT children of a MetaGroupItem."""
        return [
            item for item in self.items()
            if self._is_annotation_item(item) and not isinstance(item.parentItem(), MetaGroupItem)
        ]
