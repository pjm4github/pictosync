"""
canvas/items.py

Graphics items for diagram annotation: rectangles, ellipses, lines, and text.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

from PyQt6.QtCore import Qt, QPointF, QRectF, QLineF
from PyQt6.QtGui import QBrush, QPen, QColor, QPainter, QPainterPath, QPolygonF
from PyQt6.QtWidgets import (
    QGraphicsItem,
    QGraphicsItemGroup,
    QGraphicsRectItem,
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsTextItem,
    QGraphicsPathItem,
    QStyle,
    QStyleOptionGraphicsItem,
)

from models import AnnotationMeta, ANN_ID_KEY, KIND_ALIAS_MAP
from canvas.mixins import LinkedMixin, MetaMixin
from settings import get_settings
from debug_trace import trace


# =============================================================================
# Cached canvas settings - initialized once at first access to avoid
# repeated settings lookups during paint operations.
# =============================================================================

class _CachedCanvasSettings:
    """Cache for canvas settings values to avoid repeated lookups during paint."""

    _instance = None

    def __init__(self):
        self._initialized = False
        # Default values (used if settings unavailable)
        self.handle_size = 8.0
        self.hit_distance = 10.0
        self.min_size = 5.0
        self.handle_border_color = QColor("#0078D7")
        self.handle_fill_color = QColor("#FFFFFF")
        self.selection_color = QColor("#0078D7")
        self.min_gap_pixels = 2.0
        self.arrow_min_multiplier = 2
        self.default_dash_length = 30.0
        self.default_dash_solid_percent = 50.0

    def _ensure_initialized(self):
        """Load settings on first access."""
        if self._initialized:
            return
        try:
            s = get_settings().settings.canvas
            self.handle_size = s.handles.size
            self.hit_distance = s.handles.hit_distance
            self.min_size = s.shapes.min_size
            self.handle_border_color = QColor(s.handles.border_color)
            self.handle_fill_color = QColor(s.handles.fill_color)
            self.selection_color = QColor(s.selection.outline_color)
            self.min_gap_pixels = s.lines.min_gap_pixels
            self.arrow_min_multiplier = s.lines.arrow_min_multiplier
            self.default_dash_length = s.shapes.default_dash_length
            self.default_dash_solid_percent = s.shapes.default_dash_solid_percent
        except Exception:
            pass  # Use defaults
        self._initialized = True

    @classmethod
    def get(cls) -> "_CachedCanvasSettings":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        cls._instance._ensure_initialized()
        return cls._instance


# Helper functions to get cached canvas settings
def _get_handle_size() -> float:
    """Get handle size from settings. Default: 8.0 pixels."""
    return _CachedCanvasSettings.get().handle_size


def _get_hit_distance() -> float:
    """Get hit distance from settings. Default: 10.0 pixels."""
    return _CachedCanvasSettings.get().hit_distance


def _get_min_size() -> float:
    """Get minimum shape size from settings. Default: 5.0 pixels."""
    return _CachedCanvasSettings.get().min_size


def _get_handle_border_color() -> QColor:
    """Get handle border color from settings. Default: #0078D7 (blue)."""
    return _CachedCanvasSettings.get().handle_border_color


def _get_handle_fill_color() -> QColor:
    """Get handle fill color from settings. Default: #FFFFFF (white)."""
    return _CachedCanvasSettings.get().handle_fill_color


def _get_selection_color() -> QColor:
    """Get selection outline color from settings. Default: #0078D7 (blue)."""
    return _CachedCanvasSettings.get().selection_color


_crosshair_plus_cursor = None

def _get_crosshair_plus_cursor():
    """Return a cached crosshair cursor with a small '+' at lower-right."""
    global _crosshair_plus_cursor
    if _crosshair_plus_cursor is not None:
        return _crosshair_plus_cursor
    from PyQt6.QtGui import QPixmap, QCursor
    size = 24
    hot = 8  # hotspot at the crosshair center
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
    pen = QPen(QColor(0, 0, 0), 1)
    p.setPen(pen)
    # Crosshair lines (centered at hotspot)
    p.drawLine(hot, 0, hot, hot - 3)       # top
    p.drawLine(hot, hot + 3, hot, hot + 7)  # bottom
    p.drawLine(0, hot, hot - 3, hot)        # left
    p.drawLine(hot + 3, hot, hot + 7, hot)  # right
    # '+' symbol at lower-right (offset from crosshair)
    px, py = hot + 9, hot + 9
    p.drawLine(px - 3, py, px + 3, py)     # horizontal
    p.drawLine(px, py - 3, px, py + 3)     # vertical
    p.end()
    _crosshair_plus_cursor = QCursor(pix, hot, hot)
    return _crosshair_plus_cursor


_rotate_cursor = None

def _get_rotate_cursor():
    """Return a cached rotation cursor (circular arrow)."""
    global _rotate_cursor
    if _rotate_cursor is not None:
        return _rotate_cursor
    from PyQt6.QtGui import QPixmap, QCursor
    size = 24
    hot = 12
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    pen = QPen(QColor(0, 0, 0), 1.5)
    p.setPen(pen)
    # Draw a 270° arc (open circle)
    from PyQt6.QtCore import QRectF as _QRectF
    arc_rect = _QRectF(3, 3, 18, 18)
    # Qt angles: 16ths of a degree, 0=3 o'clock, positive=counter-clockwise
    p.drawArc(arc_rect, 45 * 16, 270 * 16)
    # Arrowhead at the end of the arc (pointing clockwise at ~315°/bottom-right)
    import math
    ax, ay = hot + 6.4, hot + 6.4  # end of arc at 315°
    p.drawLine(int(ax), int(ay), int(ax - 4), int(ay))
    p.drawLine(int(ax), int(ay), int(ax), int(ay - 4))
    p.end()
    _rotate_cursor = QCursor(pix, hot, hot)
    return _rotate_cursor


def _find_nearby_port(scene, scene_pt: QPointF,
                      threshold: float = 0) -> Optional['MetaPortItem']:
    """Return the nearest MetaPortItem within *threshold* pixels of *scene_pt*.

    Args:
        scene: The QGraphicsScene to scan.
        scene_pt: Point in scene coordinates.
        threshold: Snap distance in pixels (default: 1.5 * hit_distance).

    Returns:
        The nearest MetaPortItem within range, or None.
    """
    if threshold <= 0:
        threshold = _get_hit_distance() * 1.5
    best = None
    best_d = threshold
    for si in scene.items():
        if not isinstance(si, MetaPortItem):
            continue
        port_pos = si.mapToScene(QPointF(0, 0))
        d = QLineF(scene_pt, port_pos).length()
        if d < best_d:
            best_d = d
            best = si
    return best


def round1(value: float) -> float:
    """Round a value to 2 decimal place precision for geometry."""
    return round(value, 2)


def _apply_dash_style(pen: QPen, dash_style: str, pattern_length: float, solid_percent: float):
    """
    Apply dash style to a QPen.

    Args:
        pen: The QPen to modify
        dash_style: One of "solid" or "dashed"
        pattern_length: Total length of one dash+gap cycle in pixels
        solid_percent: Percentage of pattern that is solid (0-100)
    """
    if dash_style == "dashed":
        # Create custom dash pattern based on length and solid percentage
        # Qt dash patterns are specified in units of pen width
        pen_width = pen.widthF() if pen.widthF() > 0 else 1.0
        solid_percent = max(1, min(99, solid_percent))  # Clamp to 1-99%

        # Calculate dash and gap lengths in absolute pixels first
        solid_px = pattern_length * solid_percent / 100.0
        gap_px = pattern_length * (100 - solid_percent) / 100.0

        # Minimum gap from cached settings. Default: 2.0 pixels
        min_gap_px = _CachedCanvasSettings.get().min_gap_pixels
        if gap_px < min_gap_px:
            gap_px = min_gap_px
            solid_px = max(min_gap_px, pattern_length - gap_px)

        # Convert to pen-width units (Qt multiplies by pen width when rendering)
        solid_length = solid_px / pen_width
        gap_length = gap_px / pen_width

        pen.setStyle(Qt.PenStyle.CustomDashLine)
        pen.setDashPattern([solid_length, gap_length])
    else:
        pen.setStyle(Qt.PenStyle.SolidLine)


def draw_handles(painter: QPainter, handle_positions: Dict[str, QPointF], handle_size: Optional[float] = None):
    """Draw resize handles at the given positions."""
    # Handle size from settings. Default: 8.0 pixels
    if handle_size is None:
        handle_size = _get_handle_size()
    # Handle colors from settings. Defaults: border=#0078D7 (blue), fill=#FFFFFF (white)
    handle_pen = QPen(_get_handle_border_color(), 1)
    handle_brush = QBrush(_get_handle_fill_color())
    painter.setPen(handle_pen)
    painter.setBrush(handle_brush)

    half = handle_size / 2
    for pos in handle_positions.values():
        painter.drawRect(QRectF(pos.x() - half, pos.y() - half, handle_size, handle_size))


def shape_with_handles(base_shape: QPainterPath, handle_positions: Dict[str, QPointF],
                       handle_size: Optional[float] = None,
                       rotation_knob_local: Optional[QPointF] = None) -> QPainterPath:
    """Create a shape path that includes handle and rotation knob hit areas."""
    if handle_size is None:
        handle_size = _get_hit_distance()
    result = QPainterPath(base_shape)
    half = handle_size / 2
    for pos in handle_positions.values():
        result.addRect(QRectF(pos.x() - half, pos.y() - half, handle_size, handle_size))
    if rotation_knob_local is not None:
        result.addEllipse(rotation_knob_local, half, half)
    return result


class MetaRectItem(QGraphicsRectItem, MetaMixin, LinkedMixin):
    """Rectangle item with resizable corners and embedded C4 text label."""

    KIND = "rect"
    KIND_ALIASES = frozenset(k for k, v in KIND_ALIAS_MAP.items() if v == "rect")

    def __init__(self, x: float, y: float, w: float, h: float, ann_id: str, on_change=None):
        trace(f"MetaRectItem.__init__ start: id={ann_id}", "ITEM_INIT")
        QGraphicsRectItem.__init__(self, QRectF(0, 0, w, h))
        MetaMixin.__init__(self)
        LinkedMixin.__init__(self, ann_id, on_change)

        self.kind ="rect"
        self.setPos(QPointF(x, y))
        self.setData(ANN_ID_KEY, ann_id)

        self.setAcceptHoverEvents(True)

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        self._active_handle: Optional[str] = None
        self._resizing = False
        self._press_scene: Optional[QPointF] = None
        self._start_pos: Optional[QPointF] = None
        self._start_rect: Optional[QRectF] = None

        self.pen_color = QColor(Qt.GlobalColor.red)
        self.pen_width = 2
        self.brush_color = QColor(0, 0, 0, 0)
        self.text_color = QColor(self.pen_color)  # Default text color matches border
        self.line_dash = "solid"  # solid | dashed
        # Dash pattern settings from cached settings. Defaults: length=30.0, solid_percent=50.0
        trace("  Getting cached settings", "ITEM_INIT")
        cached = _CachedCanvasSettings.get()
        self.dash_pattern_length = cached.default_dash_length
        self.dash_solid_percent = cached.default_dash_solid_percent
        trace("  Applying pen/brush", "ITEM_INIT")
        self._apply_pen_brush()

        # Embedded text for C4 properties
        trace("  Creating label item", "ITEM_INIT")
        self._label_item = QGraphicsTextItem(self)
        self._label_item.setAcceptHoverEvents(False)
        self._label_item.setDefaultTextColor(self.text_color)
        self._label_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        trace("  Updating label position", "ITEM_INIT")
        self._update_label_position()
        trace(f"MetaRectItem.__init__ complete: id={ann_id}", "ITEM_INIT")

    def _apply_pen_brush(self):
        pen = QPen(self.pen_color, self.pen_width)
        _apply_dash_style(pen, self.line_dash, self.dash_pattern_length, self.dash_solid_percent)
        self.setPen(pen)
        self.setBrush(QBrush(self.brush_color))

    def _update_label_position(self):
        r = self.rect()
        self._position_label_in_rect(0, 0, r.width(), r.height())

    def _update_label_text(self):
        self._render_label_from_meta()

    def set_meta(self, meta: AnnotationMeta) -> None:
        self.meta = meta
        self._update_label_text()

    def setRect(self, r: QRectF):
        super().setRect(r)
        self._update_label_position()
        self._update_transform_origin()
        self._update_child_ports()

    def _handle_points_local(self) -> Dict[str, QPointF]:
        """Return handle positions in local coordinates for painting."""
        r = self.rect()
        cx = r.left() + r.width() / 2
        cy = r.top() + r.height() / 2
        return {
            "tl": QPointF(r.left(), r.top()),
            "tr": QPointF(r.right(), r.top()),
            "bl": QPointF(r.left(), r.bottom()),
            "br": QPointF(r.right(), r.bottom()),
            "t":  QPointF(cx, r.top()),
            "b":  QPointF(cx, r.bottom()),
            "l":  QPointF(r.left(), cy),
            "r":  QPointF(r.right(), cy),
        }

    def hoverMoveEvent(self, event):
        h = self._hit_test_handle(event.scenePos())
        if h == "rotate":
            self.setCursor(_get_rotate_cursor())
        elif h:
            self.setCursor(self._cursor_for_handle(h))
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            h = self._hit_test_handle(event.scenePos())
            if h == "rotate":
                self._begin_rotation()
                event.accept()
                return
            if h:
                self._begin_resize_tracking()
                self._active_handle = h
                self._resizing = True
                self._store_resize_anchor(h)
                self._press_scene = event.scenePos()
                self._start_pos = QPointF(self.pos())
                self._start_rect = QRectF(self.rect())
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._rotating:
            self._handle_rotation_move(event)
            return
        if self._resizing and self._active_handle and self._press_scene and self._start_pos and self._start_rect:
            cur = event.scenePos()
            dx, dy = self._scene_delta_to_local(
                cur.x() - self._press_scene.x(),
                cur.y() - self._press_scene.y())

            w0 = self._start_rect.width()
            h0 = self._start_rect.height()
            new_w, new_h, anchor_after = self._compute_resize(
                self._active_handle, dx, dy, w0, h0)
            self.setRect(QRectF(0, 0, new_w, new_h))
            self._update_transform_origin()
            self._fixup_resize_pos(anchor_after)

            self._notify_changed()
            event.accept()
            return

        super().mouseMoveEvent(event)

    def shape(self) -> QPainterPath:
        """Return shape including handle areas when selected."""
        base = super().shape()
        if self._should_paint_handles():
            return shape_with_handles(base, self._handle_points_local(),
                                      rotation_knob_local=self._rotation_knob_local() if self._is_rotatable() else None)
        return base

    def boundingRect(self) -> QRectF:
        """Expand bounding rect to include resize handles."""
        r = super().boundingRect()
        # Handle size from settings. Default: 8.0 pixels
        margin = _get_handle_size() / 2 + 1
        return r.adjusted(-margin, -margin, margin, margin)

    def paint(self, painter: QPainter, option, widget=None):
        # Remove selection state from option to suppress default selection rectangle
        my_option = QStyleOptionGraphicsItem(option)
        my_option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, my_option, widget)

        if self._should_paint_handles():
            # Draw selection outline matching the actual rect
            # Selection color from settings. Default: #0078D7 (blue)
            sel_pen = QPen(_get_selection_color(), 1, Qt.PenStyle.DashLine)
            painter.setPen(sel_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self.rect())
            # Draw resize handles
            draw_handles(painter, self._handle_points_local())
            self._draw_rotation_knob(painter)

    def mouseReleaseEvent(self, event):
        if self._rotating:
            self._end_rotation()
            event.accept()
            return
        if self._resizing:
            self._end_resize_tracking()
            self._resizing = False
            self._active_handle = None
            self._press_scene = None
            self._start_pos = None
            self._start_rect = None
            self._notify_changed()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        out = super().itemChange(change, value)
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if not self._resizing:
                self._notify_changed()
            self._update_child_port_connections()
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            # Update shape when selection changes to include/exclude handle areas
            self.prepareGeometryChange()
        return out

    def to_record(self) -> Dict[str, Any]:
        p = self.pos()
        r = self.rect()
        rec = {
            "id": self.ann_id,
            "kind": "rect",
            **self._ports_dict(),
            "geom": {
                "x": round1(p.x()),
                "y": round1(p.y()),
                "w": round1(r.width()),
                "h": round1(r.height()),
            },
            **self._meta_dict(self.meta),
            **self._style_dict(),
        }
        # Include z-index if set
        z = self.zValue()
        if z != 0:
            rec["z"] = int(z)
        self._add_angle_to_geom(rec.get("geom", {}))
        return rec


class MetaRoundedRectItem(QGraphicsPathItem, MetaMixin, LinkedMixin):
    """Rounded rectangle item with configurable corner radius (adjust1)."""

    KIND = "roundedrect"
    KIND_ALIASES = frozenset(k for k, v in KIND_ALIAS_MAP.items() if v == "roundedrect")

    # Class-level callback for adjust1 changes (set by MainWindow)
    on_adjust1_changed = None  # Called with (item, new_value) when adjust1 changes via handle drag

    def __init__(self, x: float, y: float, w: float, h: float, adjust1: float, ann_id: str, on_change=None):
        QGraphicsPathItem.__init__(self)
        MetaMixin.__init__(self)
        LinkedMixin.__init__(self, ann_id, on_change)

        self.kind ="roundedrect"
        self._width = w
        self._height = h
        self._adjust1 = adjust1
        self.setPos(QPointF(x, y))
        self.setData(ANN_ID_KEY, ann_id)
        self._update_path()

        self.setAcceptHoverEvents(True)

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        self._active_handle: Optional[str] = None
        self._resizing = False
        self._press_scene: Optional[QPointF] = None
        self._start_pos: Optional[QPointF] = None
        self._start_size: Optional[Tuple[float, float]] = None
        self._start_adjust1: Optional[float] = None

        self.pen_color = QColor(Qt.GlobalColor.magenta)
        self.pen_width = 2
        self.brush_color = QColor(0, 0, 0, 0)
        self.text_color = QColor(self.pen_color)  # Default text color matches border
        self.line_dash = "solid"  # solid | dashed
        # Dash pattern settings from cached settings. Defaults: length=30.0, solid_percent=50.0
        cached = _CachedCanvasSettings.get()
        self.dash_pattern_length = cached.default_dash_length
        self.dash_solid_percent = cached.default_dash_solid_percent
        self._apply_pen_brush()

        # Embedded text for C4 properties
        self._label_item = QGraphicsTextItem(self)
        self._label_item.setAcceptHoverEvents(False)
        self._label_item.setDefaultTextColor(self.text_color)
        self._label_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self._update_label_position()

    def _update_path(self):
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, self._width, self._height), self._adjust1, self._adjust1)
        self.setPath(path)

    def _apply_pen_brush(self):
        pen = QPen(self.pen_color, self.pen_width)
        _apply_dash_style(pen, self.line_dash, self.dash_pattern_length, self.dash_solid_percent)
        self.setPen(pen)
        self.setBrush(QBrush(self.brush_color))

    def _update_label_position(self):
        # Rounded corners push the content area inward slightly
        corner_inset = self._adjust1 * 0.3
        self._position_label_in_rect(
            corner_inset, corner_inset,
            self._width - 2 * corner_inset,
            self._height - 2 * corner_inset)

    def _update_label_text(self):
        self._render_label_from_meta()

    def set_meta(self, meta: AnnotationMeta) -> None:
        self.meta = meta
        self._update_label_text()

    def rect(self) -> QRectF:
        return QRectF(0, 0, self._width, self._height)

    def setRect(self, r: QRectF):
        self._width = r.width()
        self._height = r.height()
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()
        self._update_child_ports()

    def adjust1(self) -> float:
        return self._adjust1

    def set_adjust1(self, value: float):
        self._adjust1 = max(0, value)
        self._update_path()
        self._update_child_ports()

    def _handle_points_local(self) -> Dict[str, QPointF]:
        """Return handle positions in local coordinates for painting."""
        cx = self._width / 2
        cy = self._height / 2
        return {
            "tl": QPointF(0, 0),
            "tr": QPointF(self._width, 0),
            "bl": QPointF(0, self._height),
            "br": QPointF(self._width, self._height),
            "t":  QPointF(cx, 0),
            "b":  QPointF(cx, self._height),
            "l":  QPointF(0, cy),
            "r":  QPointF(self._width, cy),
            "adjust1": QPointF(self._adjust1, 0),  # Adjust1 (radius) control handle
        }

    def hoverMoveEvent(self, event):
        h = self._hit_test_handle(event.scenePos())
        if h == "rotate":
            self.setCursor(_get_rotate_cursor())
        elif h == "adjust1":
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif h:
            self.setCursor(self._cursor_for_handle(h))
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            h = self._hit_test_handle(event.scenePos())
            if h == "rotate":
                self._begin_rotation()
                event.accept()
                return
            if h:
                self._begin_resize_tracking()
                self._active_handle = h
                self._resizing = True
                self._store_resize_anchor(h)
                self._press_scene = event.scenePos()
                self._start_pos = QPointF(self.pos())
                self._start_size = (self._width, self._height)
                self._start_adjust1 = self._adjust1
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._rotating:
            self._handle_rotation_move(event)
            return
        if self._resizing and self._active_handle and self._press_scene and self._start_pos and self._start_size:
            cur = event.scenePos()
            dx, dy = self._scene_delta_to_local(
                cur.x() - self._press_scene.x(),
                cur.y() - self._press_scene.y())

            # Handle adjust1 (corner radius) adjustment separately
            if self._active_handle == "adjust1" and self._start_adjust1 is not None:
                new_adjust1 = self._start_adjust1 + dx
                # Clamp adjust1 between 0 and half of the smaller dimension
                max_adjust1 = min(self._width, self._height) / 2
                new_adjust1 = max(0, min(new_adjust1, max_adjust1))
                self._adjust1 = new_adjust1
                self._update_path()
                self._update_label_position()
                self._update_transform_origin()
                self._notify_changed()
                # Notify property panel of adjust1 change
                if MetaRoundedRectItem.on_adjust1_changed:
                    MetaRoundedRectItem.on_adjust1_changed(self, new_adjust1)
                event.accept()
                return

            w0, h0 = self._start_size
            new_w, new_h, anchor_after = self._compute_resize(
                self._active_handle, dx, dy, w0, h0)
            self._width = new_w
            self._height = new_h
            self._update_path()
            self._update_label_position()
            self._update_transform_origin()
            self._fixup_resize_pos(anchor_after)

            self._notify_changed()
            event.accept()
            return

        super().mouseMoveEvent(event)

    def shape(self) -> QPainterPath:
        """Return shape including handle areas when selected."""
        base = super().shape()
        if self._should_paint_handles():
            return shape_with_handles(base, self._handle_points_local(),
                                      rotation_knob_local=self._rotation_knob_local() if self._is_rotatable() else None)
        return base

    def boundingRect(self) -> QRectF:
        """Expand bounding rect to include resize handles."""
        r = super().boundingRect()
        # Handle size from settings. Default: 8.0 pixels
        margin = _get_handle_size() / 2 + 1
        return r.adjusted(-margin, -margin, margin, margin)

    def paint(self, painter: QPainter, option, widget=None):
        # Remove selection state from option to suppress default selection rectangle
        my_option = QStyleOptionGraphicsItem(option)
        my_option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, my_option, widget)

        if self._should_paint_handles():
            # Draw selection outline matching the actual rounded rect
            # Selection color from settings. Default: #0078D7 (blue)
            sel_pen = QPen(_get_selection_color(), 1, Qt.PenStyle.DashLine)
            painter.setPen(sel_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(QRectF(0, 0, self._width, self._height), self._adjust1, self._adjust1)

            # Draw resize handles (excluding adjust1 handle)
            handles = self._handle_points_local()
            adjust1_handle_pos = handles.pop("adjust1")  # Remove adjust1 handle from regular handles
            draw_handles(painter, handles)
            self._draw_rotation_knob(painter)

            # Draw adjust1 handle in yellow
            # Handle size from settings. Default: 8.0 pixels
            handle_size = _get_handle_size()
            half = handle_size / 2
            painter.setPen(QPen(QColor(204, 153, 0), 1))  # Dark yellow border
            painter.setBrush(QBrush(QColor(255, 215, 0)))  # Gold/yellow fill
            painter.drawEllipse(QRectF(adjust1_handle_pos.x() - half, adjust1_handle_pos.y() - half,
                                       handle_size, handle_size))

    def mouseReleaseEvent(self, event):
        if self._rotating:
            self._end_rotation()
            event.accept()
            return
        if self._resizing:
            self._end_resize_tracking()
            self._resizing = False
            self._active_handle = None
            self._press_scene = None
            self._start_pos = None
            self._start_size = None
            self._start_adjust1 = None
            self._notify_changed()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        out = super().itemChange(change, value)
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if not self._resizing:
                self._notify_changed()
            self._update_child_port_connections()
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.prepareGeometryChange()
        return out

    def to_record(self) -> Dict[str, Any]:
        p = self.pos()
        rec = {
            "id": self.ann_id,
            "kind": "roundedrect",
            **self._ports_dict(),
            "geom": {
                "x": round1(p.x()),
                "y": round1(p.y()),
                "w": round1(self._width),
                "h": round1(self._height),
                "adjust1": round1(self._adjust1),
            },
            **self._meta_dict(self.meta),
            **self._style_dict(),
        }
        # Include z-index if set
        z = self.zValue()
        if z != 0:
            rec["z"] = int(z)
        self._add_angle_to_geom(rec.get("geom", {}))
        return rec


class MetaEllipseItem(QGraphicsEllipseItem, MetaMixin, LinkedMixin):
    """Ellipse item with resizable corners."""

    KIND = "ellipse"
    KIND_ALIASES = frozenset(k for k, v in KIND_ALIAS_MAP.items() if v == "ellipse")

    def __init__(self, x: float, y: float, w: float, h: float, ann_id: str, on_change=None):
        QGraphicsEllipseItem.__init__(self, QRectF(0, 0, w, h))
        MetaMixin.__init__(self)
        LinkedMixin.__init__(self, ann_id, on_change)

        self.kind ="ellipse"
        self.setPos(QPointF(x, y))
        self.setData(ANN_ID_KEY, ann_id)

        self.setAcceptHoverEvents(True)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        self._active_handle: Optional[str] = None
        self._resizing = False
        self._press_scene: Optional[QPointF] = None
        self._start_pos: Optional[QPointF] = None
        self._start_rect: Optional[QRectF] = None

        self.pen_color = QColor(Qt.GlobalColor.green)
        self.pen_width = 2
        self.brush_color = QColor(0, 0, 0, 0)
        self.text_color = QColor(Qt.GlobalColor.green)
        self.line_dash = "solid"  # solid | dashed
        # Dash pattern settings from cached settings. Defaults: length=30.0, solid_percent=50.0
        cached = _CachedCanvasSettings.get()
        self.dash_pattern_length = cached.default_dash_length
        self.dash_solid_percent = cached.default_dash_solid_percent
        self._apply_pen_brush()

        # Embedded label
        self._label_item = QGraphicsTextItem(self)
        self._label_item.setAcceptHoverEvents(False)
        self._label_item.setDefaultTextColor(self.text_color)
        self._update_label_position()

    def _apply_pen_brush(self):
        pen = QPen(self.pen_color, self.pen_width)
        _apply_dash_style(pen, self.line_dash, self.dash_pattern_length, self.dash_solid_percent)
        self.setPen(pen)
        self.setBrush(QBrush(self.brush_color))

    def _update_label_position(self):
        r = self.rect()
        # Ellipse inscribes the text area — inset ~10% to stay inside the curve
        inset_x = max(4, r.width() * 0.1)
        inset_y = max(4, r.height() * 0.1)
        self._position_label_in_rect(
            inset_x, inset_y,
            r.width() - 2 * inset_x,
            r.height() - 2 * inset_y)

    def _update_label_text(self):
        self._render_label_from_meta()

    def set_meta(self, meta: AnnotationMeta) -> None:
        self.meta = meta
        self._update_label_text()

    def setRect(self, r: QRectF):
        super().setRect(r)
        self._update_label_position()
        self._update_transform_origin()
        self._update_child_ports()

    def _handle_points_local(self) -> Dict[str, QPointF]:
        """Return handle positions in local coordinates for painting."""
        r = self.rect()
        cx = r.left() + r.width() / 2
        cy = r.top() + r.height() / 2
        return {
            "tl": QPointF(r.left(), r.top()),
            "tr": QPointF(r.right(), r.top()),
            "bl": QPointF(r.left(), r.bottom()),
            "br": QPointF(r.right(), r.bottom()),
            "t":  QPointF(cx, r.top()),
            "b":  QPointF(cx, r.bottom()),
            "l":  QPointF(r.left(), cy),
            "r":  QPointF(r.right(), cy),
        }

    def hoverMoveEvent(self, event):
        h = self._hit_test_handle(event.scenePos())
        if h == "rotate":
            self.setCursor(_get_rotate_cursor())
        elif h:
            self.setCursor(self._cursor_for_handle(h))
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            h = self._hit_test_handle(event.scenePos())
            if h == "rotate":
                self._begin_rotation()
                event.accept()
                return
            if h:
                self._begin_resize_tracking()
                self._active_handle = h
                self._resizing = True
                self._store_resize_anchor(h)
                self._press_scene = event.scenePos()
                self._start_pos = QPointF(self.pos())
                self._start_rect = QRectF(self.rect())
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._rotating:
            self._handle_rotation_move(event)
            return
        if self._resizing and self._active_handle and self._press_scene and self._start_pos and self._start_rect:
            cur = event.scenePos()
            dx, dy = self._scene_delta_to_local(
                cur.x() - self._press_scene.x(),
                cur.y() - self._press_scene.y())

            w0 = self._start_rect.width()
            h0 = self._start_rect.height()
            new_w, new_h, anchor_after = self._compute_resize(
                self._active_handle, dx, dy, w0, h0)
            self.setRect(QRectF(0, 0, new_w, new_h))
            self._update_transform_origin()
            self._fixup_resize_pos(anchor_after)

            self._notify_changed()
            event.accept()
            return

        super().mouseMoveEvent(event)

    def shape(self) -> QPainterPath:
        """Return shape including handle areas when selected."""
        base = super().shape()
        if self._should_paint_handles():
            return shape_with_handles(base, self._handle_points_local(),
                                      rotation_knob_local=self._rotation_knob_local() if self._is_rotatable() else None)
        return base

    def boundingRect(self) -> QRectF:
        """Expand bounding rect to include resize handles."""
        r = super().boundingRect()
        # Handle size from settings. Default: 8.0 pixels
        margin = _get_handle_size() / 2 + 1
        return r.adjusted(-margin, -margin, margin, margin)

    def paint(self, painter: QPainter, option, widget=None):
        # Remove selection state from option to suppress default selection rectangle
        my_option = QStyleOptionGraphicsItem(option)
        my_option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, my_option, widget)

        if self._should_paint_handles():
            # Draw selection outline matching the actual ellipse
            # Selection color from settings. Default: #0078D7 (blue)
            sel_pen = QPen(_get_selection_color(), 1, Qt.PenStyle.DashLine)
            painter.setPen(sel_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(self.rect())
            # Draw resize handles
            draw_handles(painter, self._handle_points_local())
            self._draw_rotation_knob(painter)

    def mouseReleaseEvent(self, event):
        if self._rotating:
            self._end_rotation()
            event.accept()
            return
        if self._resizing:
            self._end_resize_tracking()
            self._resizing = False
            self._active_handle = None
            self._press_scene = None
            self._start_pos = None
            self._start_rect = None
            self._notify_changed()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        out = super().itemChange(change, value)
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if not self._resizing:
                self._notify_changed()
            self._update_child_port_connections()
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.prepareGeometryChange()
        return out

    def to_record(self) -> Dict[str, Any]:
        p = self.pos()
        r = self.rect()
        rec = {
            "id": self.ann_id,
            "kind": "ellipse",
            **self._ports_dict(),
            "geom": {
                "x": round1(p.x()),
                "y": round1(p.y()),
                "w": round1(r.width()),
                "h": round1(r.height()),
            },
            **self._meta_dict(self.meta),
            **self._style_dict(),
        }
        # Include z-index if set
        z = self.zValue()
        if z != 0:
            rec["z"] = int(z)
        self._add_angle_to_geom(rec.get("geom", {}))
        return rec


class MetaLineItem(QGraphicsLineItem, MetaMixin, LinkedMixin):
    """Line item with draggable endpoints and optional arrowheads."""

    KIND = "line"

    def _is_rotatable(self) -> bool:
        return False
    KIND_ALIASES = frozenset()

    ARROW_NONE = "none"
    ARROW_START = "start"
    ARROW_END = "end"
    ARROW_BOTH = "both"

    def __init__(self, x1: float, y1: float, x2: float, y2: float, ann_id: str, on_change=None):
        QGraphicsLineItem.__init__(self, QLineF(0, 0, x2 - x1, y2 - y1))
        MetaMixin.__init__(self)
        LinkedMixin.__init__(self, ann_id, on_change)

        self.kind ="line"
        self.setPos(QPointF(x1, y1))
        self.setData(ANN_ID_KEY, ann_id)

        self.setAcceptHoverEvents(True)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        self.pen_color = QColor(Qt.GlobalColor.blue)
        self.pen_width = 2
        self.brush_color = QColor(255, 255, 255)  # Text box background fill
        self.text_color = QColor(self.pen_color)  # Default text color matches border
        self.arrow_mode = self.ARROW_NONE
        self._apply_pen()

        self._drag_end: Optional[str] = None  # "p1" or "p2"
        self._drag_text_box: Optional[str] = None  # "tl", "tr", "bl", "br" for text box corners
        self._snap_port: Optional['MetaPortItem'] = None  # port being hovered during drag
        self._port_ids: List[str] = []  # connected port IDs (read-only, computed)
        self._port_endpoints: Dict[str, str] = {}  # port_id → "start"|"end"

        # Text box properties (local coordinates relative to line midpoint)
        self._text_box_rect: Optional[QRectF] = None  # Will be computed from meta

        # Embedded text labels for label, tech, and note (stacked vertically)
        self._label_item = QGraphicsTextItem(self)
        self._label_item.setAcceptHoverEvents(False)
        self._label_item.setDefaultTextColor(self.text_color)
        self._label_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self._tech_item = QGraphicsTextItem(self)
        self._tech_item.setAcceptHoverEvents(False)
        self._tech_item.setDefaultTextColor(self.text_color)
        self._tech_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self._note_item = QGraphicsTextItem(self)
        self._note_item.setAcceptHoverEvents(False)
        self._note_item.setDefaultTextColor(self.text_color)
        self._note_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self._update_label_position()

    def _apply_pen(self):
        pen = QPen(self.pen_color, self.pen_width)
        _apply_dash_style(pen, self.line_dash, self.dash_pattern_length, self.dash_solid_percent)
        self.setPen(pen)

    def _point_at_t(self, t: float) -> QPointF:
        """Return the point at parameter *t* (0-1) along the line."""
        ln = self.line()
        return QPointF(ln.x1() + t * (ln.x2() - ln.x1()),
                       ln.y1() + t * (ln.y2() - ln.y1()))

    def _anchor_box_position(self, ax: float, ay: float, bw: float, bh: float) -> tuple:
        """Compute text box (x, y) from anchor point and text_anchor / text_anchor_v.

        The UI grid is mirrored: clicking the top-right button places the
        box so its *bottom-left* corner sits at the anchor point (the box
        extends up and to the right of the anchor).
        """
        h = getattr(self.meta, "text_anchor", "center")
        v = getattr(self.meta, "text_anchor_v", "middle")
        if h == "left":
            bx = ax
        elif h == "right":
            bx = ax - bw
        else:
            bx = ax - bw / 2
        if v == "top":
            by = ay
        elif v == "bottom":
            by = ay - bh
        else:
            by = ay - bh / 2
        return bx, by

    def _update_label_position(self):
        """Position _label_item relative to the anchor point on the line.

        When ``text_box_width`` is set, a virtual text rectangle is placed
        relative to the anchor point using ``text_anchor`` (left/center/right).
        When text content exists but no explicit text_box_width, auto-sizes
        a text box from the rendered label dimensions.
        Inner text layout (margins, halign, valign, wrap) is handled by the
        shared ``_position_label_in_rect()`` — identical to shapes.
        """
        t = getattr(self.meta, "anchor_value", 50.0) / 100.0
        anchor_pt = self._point_at_t(t)
        mid_x = anchor_pt.x()
        mid_y = anchor_pt.y()

        has_text_box = (hasattr(self, "meta") and self.meta.text_box_width > 0)
        has_text = bool(self._label_item.toPlainText().strip())

        if has_text_box:
            box_w = self.meta.text_box_width

            # Estimate box height: use explicit value or auto-size from text
            ml, mr, mt, mb = self._get_text_margins()
            wrap = getattr(self.meta, "wrap", True)
            if wrap:
                self._label_item.setTextWidth(max(10, box_w - ml - mr))
            else:
                self._label_item.setTextWidth(-1)
            text_height = self._label_item.boundingRect().height()

            if self.meta.text_box_height > 0:
                box_h = self.meta.text_box_height
            else:
                box_h = text_height + mt + mb

            box_x, box_y = self._anchor_box_position(mid_x, mid_y, box_w, box_h)
            self._text_box_rect = QRectF(box_x, box_y, box_w, box_h)
            self._position_label_in_rect(box_x, box_y, box_w, box_h)
        elif has_text:
            # Auto-size text box from label content
            self._label_item.setTextWidth(-1)
            ml, mr, mt, mb = self._get_text_margins()
            text_rect = self._label_item.boundingRect()
            box_w = text_rect.width() + ml + mr
            box_h = text_rect.height() + mt + mb

            box_x, box_y = self._anchor_box_position(mid_x, mid_y, box_w, box_h)
            self._text_box_rect = QRectF(box_x, box_y, box_w, box_h)
            self._position_label_in_rect(box_x, box_y, box_w, box_h)
        else:
            self._text_box_rect = None
            self._label_item.setTextWidth(-1)

            text_w = self._label_item.boundingRect().width()
            text_h = self._label_item.boundingRect().height()
            self._label_item.setPos(mid_x - text_w / 2, mid_y - text_h / 2)

    def _update_label_text(self):
        """Render text via shared helper; hide legacy tech/note items."""
        self._render_label_from_meta()

        has_content = bool(self._label_item.toPlainText().strip())
        self._label_item.setVisible(has_content)

        # Hide legacy separate items — all text goes through _label_item
        self._tech_item.setPlainText("")
        self._tech_item.setVisible(False)
        self._note_item.setPlainText("")
        self._note_item.setVisible(False)

    def set_meta(self, meta: AnnotationMeta) -> None:
        self.meta = meta
        self._update_label_text()

    def setLine(self, line: QLineF):
        super().setLine(line)
        self._update_label_position()

    def set_arrow_mode(self, mode: str):
        if mode in (self.ARROW_NONE, self.ARROW_START, self.ARROW_END, self.ARROW_BOTH):
            self.arrow_mode = mode
            self.update()

    def _handle_points_local(self) -> Dict[str, QPointF]:
        """Return endpoint handle positions in local coordinates for painting."""
        ln = self.line()
        handles = {
            "p1": QPointF(ln.x1(), ln.y1()),
            "p2": QPointF(ln.x2(), ln.y2()),
        }
        return handles

    def _text_box_handle_points(self) -> Dict[str, QPointF]:
        """Return text box corner handle positions for resizing."""
        if self._text_box_rect is None:
            return {}
        r = self._text_box_rect
        return {
            "tb_tl": QPointF(r.left(), r.top()),
            "tb_tr": QPointF(r.right(), r.top()),
            "tb_bl": QPointF(r.left(), r.bottom()),
            "tb_br": QPointF(r.right(), r.bottom()),
        }

    def shape(self) -> QPainterPath:
        """Return shape including handle areas when selected, with 10px margin for easier selection."""
        from PyQt6.QtGui import QPainterPathStroker

        # Create a wider hit area around the line (10 pixel margin on each side = 20px total width)
        ln = self.line()
        line_path = QPainterPath()
        line_path.moveTo(ln.p1())
        line_path.lineTo(ln.p2())

        # Use QPainterPathStroker to create a wide path around the line
        stroker = QPainterPathStroker()
        stroker.setWidth(20.0)  # 10 pixels on each side
        stroker.setCapStyle(Qt.PenCapStyle.RoundCap)
        wide_path = stroker.createStroke(line_path)

        if self._should_paint_handles():
            all_handles = self._handle_points_local()
            all_handles.update(self._text_box_handle_points())
            result = shape_with_handles(wide_path, all_handles)
            # Include text box area
            if self._text_box_rect is not None:
                result.addRect(self._text_box_rect)
            return result
        # Include text box in shape even when not selected (for hit testing)
        if self._text_box_rect is not None:
            result = QPainterPath(wide_path)
            result.addRect(self._text_box_rect)
            return result
        return wide_path

    def boundingRect(self) -> QRectF:
        """Expand bounding rect to include resize handles, text box, and selection margin."""
        r = super().boundingRect()
        # Include 10px selection margin plus handle size
        # Handle size from settings. Default: 8.0 pixels
        margin = max(_get_handle_size() / 2 + 1, 12.0)  # At least 12px for the 10px selection margin
        r = r.adjusted(-margin, -margin, margin, margin)
        # Include text box in bounding rect
        if self._text_box_rect is not None:
            r = r.united(self._text_box_rect.adjusted(-margin, -margin, margin, margin))
        return r

    def paint(self, painter: QPainter, option, widget=None):
        # Remove selection state from option to suppress default selection rectangle
        my_option = QStyleOptionGraphicsItem(option)
        my_option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, my_option, widget)

        # Draw arrowheads if enabled
        if self.arrow_mode != self.ARROW_NONE:
            ln = self.line()
            # Use configurable arrow_size, with minimum based on pen width
            # Arrow min multiplier from cached settings. Default: 2x pen width
            arrow_min_mult = _CachedCanvasSettings.get().arrow_min_multiplier
            effective_arrow_size = max(self.arrow_size, self.pen_width * arrow_min_mult)

            painter.setPen(QPen(self.pen_color, self.pen_width))
            painter.setBrush(QBrush(self.pen_color))

            if self.arrow_mode in (self.ARROW_END, self.ARROW_BOTH):
                self._draw_arrowhead(painter, QPointF(ln.x1(), ln.y1()), QPointF(ln.x2(), ln.y2()), effective_arrow_size)

            if self.arrow_mode in (self.ARROW_START, self.ARROW_BOTH):
                self._draw_arrowhead(painter, QPointF(ln.x2(), ln.y2()), QPointF(ln.x1(), ln.y1()), effective_arrow_size)

        # Draw text bounding box if present
        if self._text_box_rect is not None:
            bg_hex = getattr(self.meta, "text_box_background_color", "")
            if bg_hex:
                from utils import hex_to_qcolor
                bg_c = hex_to_qcolor(bg_hex, self.brush_color)
            else:
                bg_c = QColor(self.brush_color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(bg_c))
            painter.drawRect(self._text_box_rect)

            if self._should_paint_handles():
                border_hex = getattr(self.meta, "text_box_border_color", "")
                if border_hex:
                    from utils import hex_to_qcolor as _h2q
                    border_c = _h2q(border_hex, QColor(200, 200, 200))
                else:
                    border_c = QColor(200, 200, 200)
                box_pen = QPen(border_c, 1, Qt.PenStyle.SolidLine)
                painter.setPen(box_pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRect(self._text_box_rect)

        # Draw anchor dot when selected
        if self._should_paint_handles():
            t = getattr(self.meta, "anchor_value", 50.0) / 100.0
            pt = self._point_at_t(t)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(160, 160, 160)))
            painter.drawEllipse(pt, 5, 5)

        # Draw resize handles when selected
        if self._should_paint_handles():
            draw_handles(painter, self._handle_points_local())
            # Draw text box handles in a different color
            if self._text_box_rect is not None:
                self._draw_text_box_handles(painter)

    def _draw_text_box_handles(self, painter: QPainter):
        """Draw handles for resizing the text bounding box."""
        handles = self._text_box_handle_points()
        if not handles:
            return

        # Use a different color for text box handles (orange)
        handle_pen = QPen(QColor(255, 140, 0), 1)
        handle_brush = QBrush(QColor(255, 200, 100))
        painter.setPen(handle_pen)
        painter.setBrush(handle_brush)

        # Handle size from settings. Default: 8.0 pixels
        handle_size = _get_handle_size()
        half = handle_size / 2
        for pos in handles.values():
            painter.drawRect(QRectF(pos.x() - half, pos.y() - half, handle_size, handle_size))

    def _draw_arrowhead(self, painter: QPainter, from_pt: QPointF, to_pt: QPointF, size: float):
        dx = to_pt.x() - from_pt.x()
        dy = to_pt.y() - from_pt.y()
        length = math.sqrt(dx * dx + dy * dy)
        if length < 1e-6:
            return

        ux, uy = dx / length, dy / length
        px, py = -uy, ux

        tip = to_pt
        left = QPointF(to_pt.x() - ux * size + px * size * 0.4, to_pt.y() - uy * size + py * size * 0.4)
        right = QPointF(to_pt.x() - ux * size - px * size * 0.4, to_pt.y() - uy * size - py * size * 0.4)

        arrow = QPolygonF([tip, left, right])
        painter.drawPolygon(arrow)

    def _endpoints_scene(self) -> Tuple[QPointF, QPointF]:
        p = self.pos()
        ln = self.line()
        p1 = QPointF(p.x() + ln.x1(), p.y() + ln.y1())
        p2 = QPointF(p.x() + ln.x2(), p.y() + ln.y2())
        return p1, p2

    def _hit_test_endpoint(self, scene_pt: QPointF) -> Optional[str]:
        if not self._should_paint_handles():
            return None
        p1, p2 = self._endpoints_scene()
        # Hit distance from settings. Default: 10.0 pixels
        hit_dist = _get_hit_distance()
        if QLineF(scene_pt, p1).length() <= hit_dist:
            return "p1"
        if QLineF(scene_pt, p2).length() <= hit_dist:
            return "p2"
        return None

    def _hit_test_text_box_handle(self, scene_pt: QPointF) -> Optional[str]:
        """Test if scene point hits a text box resize handle."""
        if not self._should_paint_handles():
            return None
        if self._text_box_rect is None:
            return None
        handles = self._text_box_handle_points()
        local_pt = self.mapFromScene(scene_pt)
        # Hit distance from settings. Default: 10.0 pixels
        hit_dist = _get_hit_distance()
        for name, pos in handles.items():
            if QLineF(local_pt, pos).length() <= hit_dist:
                return name
        return None

    def hoverMoveEvent(self, event):
        # Check text box handles first
        tb_h = self._hit_test_text_box_handle(event.scenePos())
        if tb_h:
            # Set appropriate resize cursor based on handle
            if tb_h in ("tb_tl", "tb_br"):
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            else:
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            super().hoverMoveEvent(event)
            return

        h = self._hit_test_endpoint(event.scenePos())
        self.setCursor(Qt.CursorShape.CrossCursor if h else Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Check text box handles first
            tb_h = self._hit_test_text_box_handle(event.scenePos())
            if tb_h:
                self._begin_resize_tracking()
                self._drag_text_box = tb_h
                event.accept()
                return

            h = self._hit_test_endpoint(event.scenePos())
            if h:
                self._begin_resize_tracking()
                self._drag_end = h
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_text_box:
            local_pt = self.mapFromScene(event.scenePos())
            self._resize_text_box(self._drag_text_box, local_pt)
            self._notify_changed()
            event.accept()
            return

        if self._drag_end:
            cur = event.scenePos()
            p1, p2 = self._endpoints_scene()

            if self._drag_end == "p1":
                new_p1 = cur
                new_p2 = p2
            else:
                new_p1 = p1
                new_p2 = cur

            self.setPos(new_p1)
            self.setLine(QLineF(0, 0, new_p2.x() - new_p1.x(), new_p2.y() - new_p1.y()))

            # Port proximity detection
            port = _find_nearby_port(self.scene(), cur)
            if port is not self._snap_port:
                if self._snap_port:
                    self._snap_port.set_snap_hover(False)
                self._snap_port = port
                if port:
                    port.set_snap_hover(True)

            self._notify_changed()
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._drag_text_box:
            self._end_resize_tracking()
            self._drag_text_box = None
            self._notify_changed()
            event.accept()
            return
        if self._drag_end:
            # Snap endpoint to port if hovering
            if self._snap_port:
                port = self._snap_port
                port.set_snap_hover(False)
                port_pos = port.mapToScene(QPointF(0, 0))
                p1, p2 = self._endpoints_scene()
                if self._drag_end == "p1":
                    self.setPos(port_pos)
                    self.setLine(QLineF(0, 0, p2.x() - port_pos.x(),
                                        p2.y() - port_pos.y()))
                else:
                    self.setPos(p1)
                    self.setLine(QLineF(0, 0, port_pos.x() - p1.x(),
                                        port_pos.y() - p1.y()))
                # Add bidirectional connection
                if self.ann_id not in port._connections:
                    port.add_connection(self.ann_id)
                if port.ann_id not in self._port_ids:
                    self._port_ids.append(port.ann_id)
                which = "start" if self._drag_end == "p1" else "end"
                self._port_endpoints[port.ann_id] = which
                port._notify_changed()
                self._snap_port = None
            else:
                # Disconnect from any port previously connected at this end
                which = "start" if self._drag_end == "p1" else "end"
                self._disconnect_end(which)
            self._end_resize_tracking()
            self._drag_end = None
            self._notify_changed()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _disconnect_end(self, which: str):
        """Remove port connection for the given endpoint ('start' or 'end')."""
        to_remove = [pid for pid, end in self._port_endpoints.items()
                     if end == which]
        if not to_remove:
            return
        scene = self.scene()
        for pid in to_remove:
            del self._port_endpoints[pid]
            if pid in self._port_ids:
                self._port_ids.remove(pid)
            # Remove from port's connections list
            if scene:
                for si in scene.items():
                    if (isinstance(si, MetaPortItem)
                            and si.ann_id == pid):
                        si.remove_connection(self.ann_id)
                        si._notify_changed()
                        break

    def _resize_text_box(self, handle: str, local_pt: QPointF):
        """Resize the text box based on handle being dragged."""
        if self._text_box_rect is None:
            return

        r = self._text_box_rect
        min_size = 30.0  # Minimum box size

        if handle == "tb_tl":
            new_left = min(local_pt.x(), r.right() - min_size)
            new_top = min(local_pt.y(), r.bottom() - min_size)
            new_width = r.right() - new_left
            new_height = r.bottom() - new_top
        elif handle == "tb_tr":
            new_left = r.left()
            new_top = min(local_pt.y(), r.bottom() - min_size)
            new_width = max(local_pt.x() - r.left(), min_size)
            new_height = r.bottom() - new_top
        elif handle == "tb_bl":
            new_left = min(local_pt.x(), r.right() - min_size)
            new_top = r.top()
            new_width = r.right() - new_left
            new_height = max(local_pt.y() - r.top(), min_size)
        elif handle == "tb_br":
            new_left = r.left()
            new_top = r.top()
            new_width = max(local_pt.x() - r.left(), min_size)
            new_height = max(local_pt.y() - r.top(), min_size)
        else:
            return

        # Update meta with new dimensions
        self.meta.text_box_width = round1(new_width)
        self.meta.text_box_height = round1(new_height)

        # Recompute box position to keep it centered on line midpoint
        self.prepareGeometryChange()
        self._update_label_position()
        self.update()

    def itemChange(self, change, value):
        out = super().itemChange(change, value)
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if not self._drag_end:
                self._notify_changed()
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.prepareGeometryChange()
        return out

    def to_record(self) -> Dict[str, Any]:
        p = self.pos()
        ln = self.line()
        style = self._style_dict()["style"]
        style["arrow"] = self.arrow_mode
        rec = {
            "id": self.ann_id,
            "kind": "line",
            **self._ports_dict(),
            "geom": {
                "x1": round1(p.x() + ln.x1()),
                "y1": round1(p.y() + ln.y1()),
                "x2": round1(p.x() + ln.x2()),
                "y2": round1(p.y() + ln.y2()),
            },
            **self._meta_dict(self.meta),
            "style": style,
        }
        # Include connected port IDs (read-only)
        if self._port_ids:
            rec["ports"] = list(self._port_ids)
        # Include z-index if set
        z = self.zValue()
        if z != 0:
            rec["z"] = int(z)
        self._add_angle_to_geom(rec.get("geom", {}))
        return rec


class MetaTextItem(QGraphicsTextItem, MetaMixin, LinkedMixin):
    """Display-only text item rendered from the overlay-2.0 content model.

    All text editing is done through the Contents tab text widget in the
    property panel.  Double-click on the scene item focuses that widget.
    The scene item is re-rendered from ``meta.blocks`` whenever the
    Contents tab changes (via ``_render_from_meta()``).

    This avoids the dual-document sync problem: the Contents tab's
    QTextEdit is the single source of truth for text content and
    formatting.  The scene item is a one-way render target.
    """

    KIND = "text"

    def _is_rotatable(self) -> bool:
        return False
    KIND_ALIASES = frozenset(k for k, v in KIND_ALIAS_MAP.items() if v == "text")

    # Class-level callback: called on double-click to focus the Contents tab
    on_request_edit = None   # Called with (item) — MainWindow focuses Contents tab
    on_text_edit_finished = None  # Called with (item, old_text, new_text) for undo

    # Class-level default text color (set by MainWindow based on theme)
    default_text_color = QColor("#1E293B")  # Default to dark (Tailwind slate-800)

    def __init__(self, x: float, y: float, text: str, ann_id: str, on_change=None):
        QGraphicsTextItem.__init__(self, text)
        MetaMixin.__init__(self)
        LinkedMixin.__init__(self, ann_id, on_change)

        self.kind = "text"
        # Build overlay-2.0 structure: one block, one plain run with default text.
        # label = block 0 plain text; tech = block 1; note = block 2.
        from models import TextBlock, TextRun
        self.meta.blocks = [TextBlock(runs=[TextRun(type="text", text=text)])]
        self.setPos(QPointF(x, y))
        self.setData(ANN_ID_KEY, ann_id)

        # Display-only — no inline text editing on the scene
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        self.text_color = QColor(MetaTextItem.default_text_color)
        self.text_size_pt = 12
        self._editing = False  # kept for compat checks in dock.py
        self._apply_text_style()

    def _apply_text_style(self):
        self.setDefaultTextColor(self.text_color)
        f = self.font()
        f.setPointSizeF(float(self.text_size_pt))
        self.setFont(f)

    def _render_from_meta(self):
        """Rebuild the QTextDocument from meta blocks (or legacy text/note).

        One-way render: reads font/colour from effective_default_format,
        then sets the document HTML from blocks.  The Contents tab text
        widget is the source of truth; this method is the display sink.
        """
        from PyQt6.QtGui import QFont as _QFont
        from models import _blocks_to_legacy_text

        meta = self.meta
        _eff_fmt = meta.effective_default_format()

        font_family = _eff_fmt.font_family
        font_size = max(6, int(_eff_fmt.font_size or 12))
        color_str = _eff_fmt.color or ""

        if color_str:
            from utils import hex_to_qcolor as _htq
            self.text_color = _htq(color_str, self.text_color)

        self.text_size_pt = font_size
        fnt = _QFont(font_family) if font_family else _QFont()
        fnt.setPointSize(font_size)
        self.setFont(fnt)
        self.setDefaultTextColor(self.text_color)

        # Block contentsChanged during external update
        self.document().blockSignals(True)

        if meta.blocks is not None:
            html_text = _blocks_to_legacy_text(meta.blocks)
            self.setHtml(html_text if html_text else "")
        elif getattr(meta, "text", ""):
            self.setHtml(meta.text)
        elif getattr(meta, "note", ""):
            self.setPlainText(meta.note)
        else:
            self.setPlainText("")

        self.document().blockSignals(False)

    def set_meta(self, meta: AnnotationMeta) -> None:
        """Set metadata and render the document from blocks/text/note."""
        self.meta = meta
        self._render_from_meta()

    def itemChange(self, change, value):
        out = super().itemChange(change, value)
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self._notify_changed()
        return out

    def mouseDoubleClickEvent(self, event):
        """Double-click → focus the Contents tab text widget for editing."""
        if event.button() == Qt.MouseButton.LeftButton:
            if MetaTextItem.on_request_edit:
                MetaTextItem.on_request_edit(self)
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def to_record(self) -> Dict[str, Any]:
        p = self.pos()
        rec = {
            "id": self.ann_id,
            "kind": "text",
            "geom": {
                "x": round1(p.x()),
                "y": round1(p.y()),
            },
            **self._meta_dict(self.meta),
            **self._style_dict(),
        }
        # Include z-index if set
        z = self.zValue()
        if z != 0:
            rec["z"] = int(z)
        self._add_angle_to_geom(rec.get("geom", {}))
        return rec


class MetaHexagonItem(QGraphicsPathItem, MetaMixin, LinkedMixin):
    """Flat-top hexagon item with configurable horizontal indent.

    adjust1 controls how far the left/right vertices extend inward
    from the edges. A value of 0.25 (default) creates a regular hexagon.
    """

    KIND = "hexagon"
    KIND_ALIASES = frozenset(k for k, v in KIND_ALIAS_MAP.items() if v == "hexagon")

    # Class-level callback for adjust1 changes (set by MainWindow)
    on_adjust1_changed = None  # Called with (item, new_value) when adjust1 changes via handle drag

    def __init__(self, x: float, y: float, w: float, h: float, adjust1: float, ann_id: str, on_change=None):
        QGraphicsPathItem.__init__(self)
        MetaMixin.__init__(self)
        LinkedMixin.__init__(self, ann_id, on_change)

        self.kind ="hexagon"
        self._width = w
        self._height = h
        self._adjust1 = max(0.0, min(0.5, adjust1))  # Clamp to 0.0-0.5
        self.setPos(QPointF(x, y))
        self.setData(ANN_ID_KEY, ann_id)
        self._update_path()

        self.setAcceptHoverEvents(True)

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        self._active_handle: Optional[str] = None
        self._resizing = False
        self._press_scene: Optional[QPointF] = None
        self._start_pos: Optional[QPointF] = None
        self._start_size: Optional[Tuple[float, float]] = None
        self._start_adjust1: Optional[float] = None

        self.pen_color = QColor(Qt.GlobalColor.darkCyan)
        self.pen_width = 2
        self.brush_color = QColor(0, 0, 0, 0)
        self.text_color = QColor(self.pen_color)
        self.line_dash = "solid"
        cached = _CachedCanvasSettings.get()
        self.dash_pattern_length = cached.default_dash_length
        self.dash_solid_percent = cached.default_dash_solid_percent
        self._apply_pen_brush()

        # Embedded text for C4 properties
        self._label_item = QGraphicsTextItem(self)
        self._label_item.setAcceptHoverEvents(False)
        self._label_item.setDefaultTextColor(self.text_color)
        self._label_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self._update_label_position()

    def _update_path(self):
        """Build hexagon path from current dimensions and indent."""
        path = QPainterPath()
        w = self._width
        h = self._height
        indent_px = w * self._adjust1

        # Flat-top hexagon vertices (clockwise from top-left)
        #   (indent, 0) ------- (w-indent, 0)      top edge
        #      /                         \
        # (0, h/2)                   (w, h/2)      left/right vertices
        #      \                         /
        #   (indent, h) ------- (w-indent, h)     bottom edge

        path.moveTo(indent_px, 0)
        path.lineTo(w - indent_px, 0)
        path.lineTo(w, h / 2)
        path.lineTo(w - indent_px, h)
        path.lineTo(indent_px, h)
        path.lineTo(0, h / 2)
        path.closeSubpath()
        self.setPath(path)

    def _apply_pen_brush(self):
        pen = QPen(self.pen_color, self.pen_width)
        _apply_dash_style(pen, self.line_dash, self.dash_pattern_length, self.dash_solid_percent)
        self.setPen(pen)
        self.setBrush(QBrush(self.brush_color))

    def _update_label_position(self):
        # Hexagon indent pushes the content area inward on left/right
        indent = self._width * self._adjust1 * 0.5
        self._position_label_in_rect(
            indent, 0, self._width - 2 * indent, self._height)

    def _update_label_text(self):
        self._render_label_from_meta()

    def set_meta(self, meta: AnnotationMeta) -> None:
        self.meta = meta
        self._update_label_text()

    def rect(self) -> QRectF:
        return QRectF(0, 0, self._width, self._height)

    def setRect(self, r: QRectF):
        self._width = r.width()
        self._height = r.height()
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()
        self._update_child_ports()

    def adjust1(self) -> float:
        return self._adjust1

    def set_adjust1(self, value: float):
        self._adjust1 = max(0.0, min(0.5, value))
        self._update_path()
        self._update_child_ports()

    def _handle_points_local(self) -> Dict[str, QPointF]:
        cx = self._width / 2
        cy = self._height / 2
        return {
            "tl": QPointF(0, 0),
            "tr": QPointF(self._width, 0),
            "bl": QPointF(0, self._height),
            "br": QPointF(self._width, self._height),
            "t":  QPointF(cx, 0),
            "b":  QPointF(cx, self._height),
            "l":  QPointF(0, cy),
            "r":  QPointF(self._width, cy),
            "adjust1": QPointF(self._width * self._adjust1, 0),  # Upper left vertex for indent control
        }

    def hoverMoveEvent(self, event):
        h = self._hit_test_handle(event.scenePos())
        if h == "rotate":
            self.setCursor(_get_rotate_cursor())
        elif h == "adjust1":
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif h:
            self.setCursor(self._cursor_for_handle(h))
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            h = self._hit_test_handle(event.scenePos())
            if h == "rotate":
                self._begin_rotation()
                event.accept()
                return
            if h:
                self._begin_resize_tracking()
                self._active_handle = h
                self._resizing = True
                self._store_resize_anchor(h)
                self._press_scene = event.scenePos()
                self._start_pos = QPointF(self.pos())
                self._start_size = (self._width, self._height)
                self._start_adjust1 = self._adjust1
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._rotating:
            self._handle_rotation_move(event)
            return
        if self._resizing and self._active_handle and self._press_scene and self._start_pos and self._start_size:
            cur = event.scenePos()
            dx, dy = self._scene_delta_to_local(
                cur.x() - self._press_scene.x(),
                cur.y() - self._press_scene.y())

            # Handle adjust1 (indent) adjustment
            if self._active_handle == "adjust1" and self._start_adjust1 is not None:
                # Dragging upper left vertex right increases adjust1 (makes top/bottom edges shorter)
                new_adjust1_px = self._width * self._start_adjust1 + dx
                new_adjust1 = new_adjust1_px / self._width if self._width > 0 else 0.25
                new_adjust1 = max(0.0, min(0.5, new_adjust1))
                self._adjust1 = new_adjust1
                self._update_path()
                self._update_label_position()
                self._update_transform_origin()
                self._notify_changed()
                if MetaHexagonItem.on_adjust1_changed:
                    MetaHexagonItem.on_adjust1_changed(self, new_adjust1)
                event.accept()
                return

            w0, h0 = self._start_size
            new_w, new_h, anchor_after = self._compute_resize(
                self._active_handle, dx, dy, w0, h0)
            self._width = new_w
            self._height = new_h
            self._update_path()
            self._update_label_position()
            self._update_transform_origin()
            self._fixup_resize_pos(anchor_after)

            self._notify_changed()
            event.accept()
            return

        super().mouseMoveEvent(event)

    def shape(self) -> QPainterPath:
        base = super().shape()
        if self._should_paint_handles():
            return shape_with_handles(base, self._handle_points_local(),
                                      rotation_knob_local=self._rotation_knob_local() if self._is_rotatable() else None)
        return base

    def boundingRect(self) -> QRectF:
        r = super().boundingRect()
        margin = _get_handle_size() / 2 + 1
        return r.adjusted(-margin, -margin, margin, margin)

    def paint(self, painter: QPainter, option, widget=None):
        my_option = QStyleOptionGraphicsItem(option)
        my_option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, my_option, widget)

        if self._should_paint_handles():
            sel_pen = QPen(_get_selection_color(), 1, Qt.PenStyle.DashLine)
            painter.setPen(sel_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(self.path())

            handles = self._handle_points_local()
            adjust1_handle_pos = handles.pop("adjust1")
            draw_handles(painter, handles)
            self._draw_rotation_knob(painter)

            # Draw adjust1 handle in yellow
            handle_size = _get_handle_size()
            half = handle_size / 2
            painter.setPen(QPen(QColor(204, 153, 0), 1))
            painter.setBrush(QBrush(QColor(255, 215, 0)))
            painter.drawEllipse(QRectF(adjust1_handle_pos.x() - half, adjust1_handle_pos.y() - half,
                                       handle_size, handle_size))

    def mouseReleaseEvent(self, event):
        if self._rotating:
            self._end_rotation()
            event.accept()
            return
        if self._resizing:
            self._end_resize_tracking()
            self._resizing = False
            self._active_handle = None
            self._press_scene = None
            self._start_pos = None
            self._start_size = None
            self._start_adjust1 = None
            self._notify_changed()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        out = super().itemChange(change, value)
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if not self._resizing:
                self._notify_changed()
            self._update_child_port_connections()
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.prepareGeometryChange()
        return out

    def to_record(self) -> Dict[str, Any]:
        p = self.pos()
        rec = {
            "id": self.ann_id,
            "kind": "hexagon",
            **self._ports_dict(),
            "geom": {
                "x": round1(p.x()),
                "y": round1(p.y()),
                "w": round1(self._width),
                "h": round1(self._height),
                "adjust1": round1(self._adjust1),
            },
            **self._meta_dict(self.meta),
            **self._style_dict(),
        }
        z = self.zValue()
        if z != 0:
            rec["z"] = int(z)
        self._add_angle_to_geom(rec.get("geom", {}))
        return rec


class MetaCylinderItem(QGraphicsPathItem, MetaMixin, LinkedMixin):
    """3D cylinder (database icon) with configurable cap ellipse ratio.

    adjust1 controls the depth/height of the elliptical cap as a
    ratio of total height. Default is 0.15 (15% of height).
    """

    KIND = "cylinder"
    KIND_ALIASES = frozenset(k for k, v in KIND_ALIAS_MAP.items() if v == "cylinder")

    # Class-level callback for adjust1 changes (set by MainWindow)
    on_adjust1_changed = None

    def __init__(self, x: float, y: float, w: float, h: float, adjust1: float, ann_id: str, on_change=None):
        QGraphicsPathItem.__init__(self)
        MetaMixin.__init__(self)
        LinkedMixin.__init__(self, ann_id, on_change)

        self.kind ="cylinder"
        self._width = w
        self._height = h
        self._adjust1 = max(0.1, min(0.5, adjust1))
        self.setPos(QPointF(x, y))
        self.setData(ANN_ID_KEY, ann_id)
        self._update_path()

        self.setAcceptHoverEvents(True)

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        self._active_handle: Optional[str] = None
        self._resizing = False
        self._press_scene: Optional[QPointF] = None
        self._start_pos: Optional[QPointF] = None
        self._start_size: Optional[Tuple[float, float]] = None
        self._start_adjust1: Optional[float] = None

        self.pen_color = QColor(Qt.GlobalColor.darkMagenta)
        self.pen_width = 2
        self.brush_color = QColor(0, 0, 0, 0)
        self.text_color = QColor(self.pen_color)
        self.line_dash = "solid"
        cached = _CachedCanvasSettings.get()
        self.dash_pattern_length = cached.default_dash_length
        self.dash_solid_percent = cached.default_dash_solid_percent
        self._apply_pen_brush()

        self._label_item = QGraphicsTextItem(self)
        self._label_item.setAcceptHoverEvents(False)
        self._label_item.setDefaultTextColor(self.text_color)
        self._label_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self._update_label_position()

    def _update_path(self):
        """Build cylinder path: top ellipse, sides, bottom arc."""
        path = QPainterPath()
        w = self._width
        h = self._height
        cap_h = h * self._adjust1

        # Top ellipse (full)
        path.addEllipse(0, 0, w, cap_h * 2)

        # Rectangular body sides
        body_top = cap_h
        body_bottom = h - cap_h

        # Left side line
        path.moveTo(0, body_top)
        path.lineTo(0, body_bottom)

        # Bottom arc (only bottom half of ellipse)
        path.arcTo(0, h - cap_h * 2, w, cap_h * 2, 180, 180)

        # Right side line
        path.lineTo(w, body_top)

        self.setPath(path)

    def _apply_pen_brush(self):
        pen = QPen(self.pen_color, self.pen_width)
        _apply_dash_style(pen, self.line_dash, self.dash_pattern_length, self.dash_solid_percent)
        self.setPen(pen)
        self.setBrush(QBrush(self.brush_color))

    def _update_label_position(self):
        # Text goes in the body area between the top and bottom caps
        cap_h = self._height * self._adjust1
        self._position_label_in_rect(
            0, cap_h, self._width, self._height - 2 * cap_h)

    def _update_label_text(self):
        self._render_label_from_meta()

    def set_meta(self, meta: AnnotationMeta) -> None:
        self.meta = meta
        self._update_label_text()

    def rect(self) -> QRectF:
        return QRectF(0, 0, self._width, self._height)

    def setRect(self, r: QRectF):
        self._width = r.width()
        self._height = r.height()
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()
        self._update_child_ports()

    def adjust1(self) -> float:
        return self._adjust1

    def set_adjust1(self, value: float):
        self._adjust1 = max(0.1, min(0.5, value))
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()

    def _handle_points_local(self) -> Dict[str, QPointF]:
        cx = self._width / 2
        cy = self._height / 2
        cap_h = self._height * self._adjust1
        return {
            "tl": QPointF(0, 0),
            "tr": QPointF(self._width, 0),
            "bl": QPointF(0, self._height),
            "br": QPointF(self._width, self._height),
            "t":  QPointF(cx, 0),
            "b":  QPointF(cx, self._height),
            "l":  QPointF(0, cy),
            "r":  QPointF(self._width, cy),
            "adjust1": QPointF(self._width, cap_h),
        }

    def hoverMoveEvent(self, event):
        h = self._hit_test_handle(event.scenePos())
        if h == "rotate":
            self.setCursor(_get_rotate_cursor())
        elif h == "adjust1":
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif h:
            self.setCursor(self._cursor_for_handle(h))
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            h = self._hit_test_handle(event.scenePos())
            if h == "rotate":
                self._begin_rotation()
                event.accept()
                return
            if h:
                self._begin_resize_tracking()
                self._active_handle = h
                self._resizing = True
                self._store_resize_anchor(h)
                self._press_scene = event.scenePos()
                self._start_pos = QPointF(self.pos())
                self._start_size = (self._width, self._height)
                self._start_adjust1 = self._adjust1
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._rotating:
            self._handle_rotation_move(event)
            return
        if self._resizing and self._active_handle and self._press_scene and self._start_pos and self._start_size:
            cur = event.scenePos()
            dx, dy = self._scene_delta_to_local(
                cur.x() - self._press_scene.x(),
                cur.y() - self._press_scene.y())

            # Handle adjust1 (cap ratio) adjustment
            if self._active_handle == "adjust1" and self._start_adjust1 is not None:
                new_cap_h = self._height * self._start_adjust1 + dy
                new_ratio = new_cap_h / self._height if self._height > 0 else 0.15
                new_ratio = max(0.1, min(0.5, new_ratio))
                self._adjust1 = new_ratio
                self._update_path()
                self._update_label_position()
                self._update_transform_origin()
                self._notify_changed()
                if MetaCylinderItem.on_adjust1_changed:
                    MetaCylinderItem.on_adjust1_changed(self, new_ratio)
                event.accept()
                return

            w0, h0 = self._start_size
            new_w, new_h, anchor_after = self._compute_resize(
                self._active_handle, dx, dy, w0, h0)
            self._width = new_w
            self._height = new_h
            self._update_path()
            self._update_label_position()
            self._update_transform_origin()
            self._fixup_resize_pos(anchor_after)

            self._notify_changed()
            event.accept()
            return

        super().mouseMoveEvent(event)

    def shape(self) -> QPainterPath:
        base = super().shape()
        if self._should_paint_handles():
            return shape_with_handles(base, self._handle_points_local(),
                                      rotation_knob_local=self._rotation_knob_local() if self._is_rotatable() else None)
        return base

    def boundingRect(self) -> QRectF:
        r = super().boundingRect()
        margin = _get_handle_size() / 2 + 1
        return r.adjusted(-margin, -margin, margin, margin)

    def paint(self, painter: QPainter, option, widget=None):
        my_option = QStyleOptionGraphicsItem(option)
        my_option.state &= ~QStyle.StateFlag.State_Selected

        # Custom paint for cylinder: fill body, then stroke all parts
        w = self._width
        h = self._height
        cap_h = h * self._adjust1

        # Fill the body (rect + bottom ellipse + top ellipse)
        if self.brush_color.alpha() > 0:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(self.brush_color))
            # Fill top ellipse
            painter.drawEllipse(QRectF(0, 0, w, cap_h * 2))
            # Fill body rectangle
            painter.drawRect(QRectF(0, cap_h, w, h - cap_h * 2))
            # Fill bottom ellipse
            painter.drawEllipse(QRectF(0, h - cap_h * 2, w, cap_h * 2))

        # Draw strokes
        pen = QPen(self.pen_color, self.pen_width)
        _apply_dash_style(pen, self.line_dash, self.dash_pattern_length, self.dash_solid_percent)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Top ellipse
        painter.drawEllipse(QRectF(0, 0, w, cap_h * 2))
        # Left side
        painter.drawLine(QPointF(0, cap_h), QPointF(0, h - cap_h))
        # Right side
        painter.drawLine(QPointF(w, cap_h), QPointF(w, h - cap_h))
        # Bottom arc (bottom half of ellipse)
        path = QPainterPath()
        path.arcMoveTo(0, h - cap_h * 2, w, cap_h * 2, 180)
        path.arcTo(0, h - cap_h * 2, w, cap_h * 2, 180, 180)
        painter.drawPath(path)

        if self._should_paint_handles():
            sel_pen = QPen(_get_selection_color(), 1, Qt.PenStyle.DashLine)
            painter.setPen(sel_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(QRectF(0, 0, w, h))

            handles = self._handle_points_local()
            adjust1_handle_pos = handles.pop("adjust1")
            draw_handles(painter, handles)
            self._draw_rotation_knob(painter)

            # Draw adjust1 handle in yellow
            handle_size = _get_handle_size()
            half = handle_size / 2
            painter.setPen(QPen(QColor(204, 153, 0), 1))
            painter.setBrush(QBrush(QColor(255, 215, 0)))
            painter.drawEllipse(QRectF(adjust1_handle_pos.x() - half, adjust1_handle_pos.y() - half,
                                       handle_size, handle_size))

    def mouseReleaseEvent(self, event):
        if self._rotating:
            self._end_rotation()
            event.accept()
            return
        if self._resizing:
            self._end_resize_tracking()
            self._resizing = False
            self._active_handle = None
            self._press_scene = None
            self._start_pos = None
            self._start_size = None
            self._start_adjust1 = None
            self._notify_changed()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        out = super().itemChange(change, value)
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if not self._resizing:
                self._notify_changed()
            self._update_child_port_connections()
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.prepareGeometryChange()
        return out

    def to_record(self) -> Dict[str, Any]:
        p = self.pos()
        rec = {
            "id": self.ann_id,
            "kind": "cylinder",
            **self._ports_dict(),
            "geom": {
                "x": round1(p.x()),
                "y": round1(p.y()),
                "w": round1(self._width),
                "h": round1(self._height),
                "adjust1": round1(self._adjust1),
            },
            **self._meta_dict(self.meta),
            **self._style_dict(),
        }
        z = self.zValue()
        if z != 0:
            rec["z"] = int(z)
        self._add_angle_to_geom(rec.get("geom", {}))
        return rec


class MetaBlockArrowItem(QGraphicsPathItem, MetaMixin, LinkedMixin):
    """Right-pointing block arrow with configurable head and shaft dimensions.

    adjust1: ratio of shaft height to total height (0.2 to 0.9)
    adjust2: horizontal distance from arrow tip to head base (in pixels)
    """

    KIND = "blockarrow"
    KIND_ALIASES = frozenset(k for k, v in KIND_ALIAS_MAP.items() if v == "blockarrow")

    # Class-level callbacks for property changes
    on_adjust1_changed = None
    on_adjust2_changed = None

    def __init__(self, x: float, y: float, w: float, h: float, adjust2: float, adjust1: float, ann_id: str, on_change=None):
        QGraphicsPathItem.__init__(self)
        MetaMixin.__init__(self)
        LinkedMixin.__init__(self, ann_id, on_change)

        self.kind ="blockarrow"
        self._width = w
        self._height = h
        self._adjust2 = max(10, min(w * 0.8, adjust2)) if w > 0 else adjust2
        self._adjust1 = max(0.2, min(0.9, adjust1))
        self.setPos(QPointF(x, y))
        self.setData(ANN_ID_KEY, ann_id)
        self._update_path()

        self.setAcceptHoverEvents(True)

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        self._active_handle: Optional[str] = None
        self._resizing = False
        self._press_scene: Optional[QPointF] = None
        self._start_pos: Optional[QPointF] = None
        self._start_size: Optional[Tuple[float, float]] = None
        self._start_adjust2: Optional[float] = None
        self._start_adjust1: Optional[float] = None

        self.pen_color = QColor(Qt.GlobalColor.darkYellow)
        self.pen_width = 2
        self.brush_color = QColor(0, 0, 0, 0)
        self.text_color = QColor(self.pen_color)
        self.line_dash = "solid"
        cached = _CachedCanvasSettings.get()
        self.dash_pattern_length = cached.default_dash_length
        self.dash_solid_percent = cached.default_dash_solid_percent
        self._apply_pen_brush()

        self._label_item = QGraphicsTextItem(self)
        self._label_item.setAcceptHoverEvents(False)
        self._label_item.setDefaultTextColor(self.text_color)
        self._label_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self._update_label_position()

    def _update_path(self):
        """Build block arrow path from current dimensions."""
        path = QPainterPath()
        w = self._width
        h = self._height
        head_x = w - self._adjust2  # X position where head starts
        shaft_margin = h * (1 - self._adjust1) / 2  # Space above/below shaft

        # Block arrow vertices (clockwise from top-left of shaft)
        # (0, shaft_top) --- (head_x, shaft_top) --- (head_x, 0)
        #                                                \
        #                                            (w, h/2)  <- arrow point
        #                                                /
        # (0, shaft_bot) --- (head_x, shaft_bot) --- (head_x, h)

        shaft_top = shaft_margin
        shaft_bot = h - shaft_margin

        path.moveTo(0, shaft_top)
        path.lineTo(head_x, shaft_top)
        path.lineTo(head_x, 0)
        path.lineTo(w, h / 2)
        path.lineTo(head_x, h)
        path.lineTo(head_x, shaft_bot)
        path.lineTo(0, shaft_bot)
        path.closeSubpath()

        self.setPath(path)

    def _apply_pen_brush(self):
        pen = QPen(self.pen_color, self.pen_width)
        _apply_dash_style(pen, self.line_dash, self.dash_pattern_length, self.dash_solid_percent)
        self.setPen(pen)
        self.setBrush(QBrush(self.brush_color))

    def _update_label_position(self):
        # Text goes in the shaft area (excluding the arrowhead)
        shaft_top = self._height * (1 - self._adjust1) / 2
        shaft_height = self._height * self._adjust1
        shaft_width = self._width - self._adjust2  # exclude head
        self._position_label_in_rect(0, shaft_top, shaft_width, shaft_height)

    def _update_label_text(self):
        self._render_label_from_meta()

    def set_meta(self, meta: AnnotationMeta) -> None:
        self.meta = meta
        self._update_label_text()

    def rect(self) -> QRectF:
        return QRectF(0, 0, self._width, self._height)

    def setRect(self, r: QRectF):
        self._width = r.width()
        self._height = r.height()
        self._adjust2 = min(self._adjust2, self._width * 0.8)
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()
        self._update_child_ports()

    def adjust2(self) -> float:
        return self._adjust2

    def set_adjust2(self, value: float):
        self._adjust2 = max(10, min(self._width * 0.8, value))
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()

    def adjust1(self) -> float:
        return self._adjust1

    def set_adjust1(self, value: float):
        self._adjust1 = max(0.2, min(0.9, value))
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()

    def _handle_points_local(self) -> Dict[str, QPointF]:
        cx = self._width / 2
        cy = self._height / 2
        head_x = self._width - self._adjust2
        shaft_margin = self._height * (1 - self._adjust1) / 2
        return {
            "tl": QPointF(0, 0),
            "tr": QPointF(self._width, 0),
            "bl": QPointF(0, self._height),
            "br": QPointF(self._width, self._height),
            "t":  QPointF(cx, 0),
            "b":  QPointF(cx, self._height),
            "l":  QPointF(0, cy),
            "r":  QPointF(self._width, cy),
            "adjust2": QPointF(head_x, shaft_margin),
            "adjust1": QPointF(0, shaft_margin),
        }

    def hoverMoveEvent(self, event):
        h = self._hit_test_handle(event.scenePos())
        if h == "rotate":
            self.setCursor(_get_rotate_cursor())
        elif h == "adjust1":
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif h == "adjust2":
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif h:
            self.setCursor(self._cursor_for_handle(h))
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            h = self._hit_test_handle(event.scenePos())
            if h == "rotate":
                self._begin_rotation()
                event.accept()
                return
            if h:
                self._begin_resize_tracking()
                self._active_handle = h
                self._resizing = True
                self._store_resize_anchor(h)
                self._press_scene = event.scenePos()
                self._start_pos = QPointF(self.pos())
                self._start_size = (self._width, self._height)
                self._start_adjust2 = self._adjust2
                self._start_adjust1 = self._adjust1
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._rotating:
            self._handle_rotation_move(event)
            return
        if self._resizing and self._active_handle and self._press_scene and self._start_pos and self._start_size:
            cur = event.scenePos()
            dx, dy = self._scene_delta_to_local(
                cur.x() - self._press_scene.x(),
                cur.y() - self._press_scene.y())

            # Handle adjust2 (head length) adjustment
            if self._active_handle == "adjust2" and self._start_adjust2 is not None:
                new_adjust2 = self._start_adjust2 - dx  # Moving left increases head length
                new_adjust2 = max(10, min(self._width * 0.8, new_adjust2))
                self._adjust2 = new_adjust2
                self._update_path()
                self._update_label_position()
                self._update_transform_origin()
                self._notify_changed()
                if MetaBlockArrowItem.on_adjust2_changed:
                    MetaBlockArrowItem.on_adjust2_changed(self, new_adjust2)
                event.accept()
                return

            # Handle adjust1 (shaft width) adjustment
            if self._active_handle == "adjust1" and self._start_adjust1 is not None:
                # Moving down decreases adjust1 (increases margin)
                old_margin = self._height * (1 - self._start_adjust1) / 2
                new_margin = old_margin + dy
                new_adjust1 = 1 - (2 * new_margin / self._height) if self._height > 0 else 0.5
                new_adjust1 = max(0.2, min(0.9, new_adjust1))
                self._adjust1 = new_adjust1
                self._update_path()
                self._update_label_position()
                self._update_transform_origin()
                self._notify_changed()
                if MetaBlockArrowItem.on_adjust1_changed:
                    MetaBlockArrowItem.on_adjust1_changed(self, new_adjust1)
                event.accept()
                return

            w0, h0 = self._start_size
            new_w, new_h, anchor_after = self._compute_resize(
                self._active_handle, dx, dy, w0, h0)
            self._width = new_w
            self._height = new_h
            self._adjust2 = min(self._adjust2, new_w * 0.8)
            self._update_path()
            self._update_label_position()
            self._update_transform_origin()
            self._fixup_resize_pos(anchor_after)

            self._notify_changed()
            event.accept()
            return

        super().mouseMoveEvent(event)

    def shape(self) -> QPainterPath:
        base = super().shape()
        if self._should_paint_handles():
            return shape_with_handles(base, self._handle_points_local(),
                                      rotation_knob_local=self._rotation_knob_local() if self._is_rotatable() else None)
        return base

    def boundingRect(self) -> QRectF:
        r = super().boundingRect()
        margin = _get_handle_size() / 2 + 1
        return r.adjusted(-margin, -margin, margin, margin)

    def paint(self, painter: QPainter, option, widget=None):
        my_option = QStyleOptionGraphicsItem(option)
        my_option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, my_option, widget)

        if self._should_paint_handles():
            sel_pen = QPen(_get_selection_color(), 1, Qt.PenStyle.DashLine)
            painter.setPen(sel_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(self.path())

            handles = self._handle_points_local()
            adjust2_handle = handles.pop("adjust2")
            adjust1_handle = handles.pop("adjust1")
            draw_handles(painter, handles)
            self._draw_rotation_knob(painter)

            # Draw custom handles in yellow
            handle_size = _get_handle_size()
            half = handle_size / 2
            painter.setPen(QPen(QColor(204, 153, 0), 1))
            painter.setBrush(QBrush(QColor(255, 215, 0)))
            painter.drawEllipse(QRectF(adjust2_handle.x() - half, adjust2_handle.y() - half,
                                       handle_size, handle_size))
            painter.drawEllipse(QRectF(adjust1_handle.x() - half, adjust1_handle.y() - half,
                                       handle_size, handle_size))

    def mouseReleaseEvent(self, event):
        if self._rotating:
            self._end_rotation()
            event.accept()
            return
        if self._resizing:
            self._end_resize_tracking()
            self._resizing = False
            self._active_handle = None
            self._press_scene = None
            self._start_pos = None
            self._start_size = None
            self._start_adjust2 = None
            self._start_adjust1 = None
            self._notify_changed()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        out = super().itemChange(change, value)
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if not self._resizing:
                self._notify_changed()
            self._update_child_port_connections()
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.prepareGeometryChange()
        return out

    def to_record(self) -> Dict[str, Any]:
        p = self.pos()
        rec = {
            "id": self.ann_id,
            "kind": "blockarrow",
            **self._ports_dict(),
            "geom": {
                "x": round1(p.x()),
                "y": round1(p.y()),
                "w": round1(self._width),
                "h": round1(self._height),
                "adjust2": round1(self._adjust2),
                "adjust1": round1(self._adjust1),
            },
            **self._meta_dict(self.meta),
            **self._style_dict(),
        }
        z = self.zValue()
        if z != 0:
            rec["z"] = int(z)
        self._add_angle_to_geom(rec.get("geom", {}))
        return rec


class MetaPolygonItem(QGraphicsPathItem, MetaMixin, LinkedMixin):
    """Arbitrary polygon item with vertex editing.

    Vertices are stored as relative coordinates (0.0–1.0) within the
    bounding box so that the shape scales proportionally on resize.
    Double-click to enter vertex-edit mode where individual vertices
    can be dragged.
    """

    KIND = "polygon"
    KIND_ALIASES = frozenset(k for k, v in KIND_ALIAS_MAP.items() if v == "polygon")

    def __init__(self, x: float, y: float, w: float, h: float,
                 points: list, ann_id: str, on_change=None):
        QGraphicsPathItem.__init__(self)
        MetaMixin.__init__(self)
        LinkedMixin.__init__(self, ann_id, on_change)

        self.kind ="polygon"
        self._width = max(w, 1.0)
        self._height = max(h, 1.0)

        # Relative points (0-1 within bounding box).
        # Preserve the extended format: [rx, ry] for straight,
        # [rx, ry, "Q", cx, cy] for quadratic, [rx, ry, "C", c1x, c1y, c2x, c2y] for cubic.
        if points and len(points) >= 3:
            self._rel_points = [list(p) for p in points]
        else:
            self._rel_points = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]

        self._in_bbox_recalc = False  # recursion guard (before first _update_path)
        self.setPos(QPointF(x, y))
        self.setData(ANN_ID_KEY, ann_id)
        self._update_path()

        self.setAcceptHoverEvents(True)

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        # Bounding-box resize state
        self._active_handle: Optional[str] = None
        self._resizing = False
        self._press_scene: Optional[QPointF] = None
        self._start_pos: Optional[QPointF] = None
        self._start_size: Optional[Tuple[float, float]] = None

        # Vertex editing state
        self._vertex_editing = False
        self._active_vertex: Optional[int] = None
        self._vertex_dragging = False
        self._active_ctrl_point: Optional[Tuple[int, str]] = None  # (vertex_idx, "cp"/"c1"/"c2")
        self._ctrl_dragging = False
        self._selected_vertex: Optional[int] = None   # left-click selected vertex
        self._hover_vertex: Optional[int] = None       # hover-highlighted vertex
        self._in_bbox_recalc = False                    # recursion guard

        self.pen_color = QColor(Qt.GlobalColor.darkCyan)
        self.pen_width = 2
        self.brush_color = QColor(0, 0, 0, 0)
        self.text_color = QColor(self.pen_color)
        self.line_dash = "solid"
        cached = _CachedCanvasSettings.get()
        self.dash_pattern_length = cached.default_dash_length
        self.dash_solid_percent = cached.default_dash_solid_percent
        self._apply_pen_brush()

        # Embedded text for C4 properties
        self._label_item = QGraphicsTextItem(self)
        self._label_item.setAcceptHoverEvents(False)
        self._label_item.setDefaultTextColor(self.text_color)
        self._label_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self._update_label_position()

    # ---- Path / geometry ----

    def _update_path(self):
        """Rebuild polygon path from relative points and current dimensions."""
        path = QPainterPath()
        if not self._rel_points:
            self.setPath(path)
            return
        w, h = self._width, self._height
        p0 = self._rel_points[0]
        path.moveTo(p0[0] * w, p0[1] * h)
        for pt in self._rel_points[1:]:
            rx, ry = pt[0], pt[1]
            if len(pt) >= 5 and pt[2] == "Q":
                cx, cy = pt[3], pt[4]
                path.quadTo(cx * w, cy * h, rx * w, ry * h)
            elif len(pt) >= 7 and pt[2] == "C":
                c1x, c1y, c2x, c2y = pt[3], pt[4], pt[5], pt[6]
                path.cubicTo(c1x * w, c1y * h, c2x * w, c2y * h, rx * w, ry * h)
            else:
                path.lineTo(rx * w, ry * h)
        # Close using vertex 0's curve data (closeSubpath is always straight)
        if len(p0) >= 5 and p0[2] == "Q":
            cx, cy = p0[3], p0[4]
            path.quadTo(cx * w, cy * h, p0[0] * w, p0[1] * h)
        elif len(p0) >= 7 and p0[2] == "C":
            c1x, c1y, c2x, c2y = p0[3], p0[4], p0[5], p0[6]
            path.cubicTo(c1x * w, c1y * h, c2x * w, c2y * h, p0[0] * w, p0[1] * h)
        else:
            path.closeSubpath()
        self.setPath(path)

        # Auto-recalculate bbox if the rendered curve extends beyond
        # the current (0, 0, _width, _height) coordinate space.
        if not self._in_bbox_recalc:
            pr = path.boundingRect()
            tol = 1.0  # pixel tolerance
            if (pr.x() < -tol or pr.y() < -tol
                    or pr.right() > self._width + tol
                    or pr.bottom() > self._height + tol):
                self._in_bbox_recalc = True
                self._recalculate_bbox()
                self._in_bbox_recalc = False

    def _recalculate_bbox(self):
        """Recalculate bounding box to tightly enclose the rendered curve.

        Uses the QPainterPath bounding rect (which accounts for bezier
        curve extent) rather than just anchor points.  Converts relative
        points back into a new bounding box with all values normalized.
        Preserves curve type tags and control points.
        """
        if not self._rel_points:
            return

        p = self.pos()
        w, h = self._width, self._height

        # Build a temporary path to get the actual curve bounding rect
        tmp = QPainterPath()
        p0 = self._rel_points[0]
        tmp.moveTo(p0[0] * w, p0[1] * h)
        for pt in self._rel_points[1:]:
            rx, ry = pt[0], pt[1]
            if len(pt) >= 5 and pt[2] == "Q":
                tmp.quadTo(pt[3] * w, pt[4] * h, rx * w, ry * h)
            elif len(pt) >= 7 and pt[2] == "C":
                tmp.cubicTo(pt[3] * w, pt[4] * h, pt[5] * w, pt[6] * h, rx * w, ry * h)
            else:
                tmp.lineTo(rx * w, ry * h)
        # Close using vertex 0's curve data
        if len(p0) >= 5 and p0[2] == "Q":
            tmp.quadTo(p0[3] * w, p0[4] * h, p0[0] * w, p0[1] * h)
        elif len(p0) >= 7 and p0[2] == "C":
            tmp.cubicTo(p0[3] * w, p0[4] * h, p0[5] * w, p0[6] * h, p0[0] * w, p0[1] * h)
        else:
            tmp.closeSubpath()

        # Use the path's bounding rect (includes curve extent)
        pr = tmp.boundingRect()
        new_x = p.x() + pr.x()
        new_y = p.y() + pr.y()
        new_w = pr.width()
        new_h = pr.height()

        # Enforce minimum size
        if new_w < 1.0:
            new_w = 1.0
        if new_h < 1.0:
            new_h = 1.0

        def _rescale(rx, ry):
            ax = p.x() + rx * w
            ay = p.y() + ry * h
            return (ax - new_x) / new_w, (ay - new_y) / new_h

        new_pts = []
        for pt in self._rel_points:
            new_rx, new_ry = _rescale(pt[0], pt[1])
            if len(pt) >= 5 and pt[2] == "Q":
                new_cx, new_cy = _rescale(pt[3], pt[4])
                new_pts.append([new_rx, new_ry, "Q", new_cx, new_cy])
            elif len(pt) >= 7 and pt[2] == "C":
                new_c1x, new_c1y = _rescale(pt[3], pt[4])
                new_c2x, new_c2y = _rescale(pt[5], pt[6])
                new_pts.append([new_rx, new_ry, "C", new_c1x, new_c1y, new_c2x, new_c2y])
            else:
                new_pts.append([new_rx, new_ry])
        self._rel_points = new_pts

        # Update position and dimensions
        self.prepareGeometryChange()
        self.setPos(QPointF(new_x, new_y))
        self._width = new_w
        self._height = new_h
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()

    def _apply_pen_brush(self):
        pen = QPen(self.pen_color, self.pen_width)
        _apply_dash_style(pen, self.line_dash, self.dash_pattern_length, self.dash_solid_percent)
        self.setPen(pen)
        self.setBrush(QBrush(self.brush_color))

    def _update_label_position(self):
        self._position_label_in_rect(0, 0, self._width, self._height)

    def _update_label_text(self):
        self._render_label_from_meta()

    def set_meta(self, meta: AnnotationMeta) -> None:
        self.meta = meta
        self._update_label_text()

    def rect(self) -> QRectF:
        return QRectF(0, 0, self._width, self._height)

    def setRect(self, r: QRectF):
        self._width = r.width()
        self._height = r.height()
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()
        self._update_child_ports()

    # ---- Bounding-box handles ----

    def _handle_points_local(self) -> Dict[str, QPointF]:
        cx = self._width / 2
        cy = self._height / 2
        return {
            "tl": QPointF(0, 0),
            "tr": QPointF(self._width, 0),
            "bl": QPointF(0, self._height),
            "br": QPointF(self._width, self._height),
            "t":  QPointF(cx, 0),
            "b":  QPointF(cx, self._height),
            "l":  QPointF(0, cy),
            "r":  QPointF(self._width, cy),
        }

    # ---- Vertex editing helpers ----

    def _vertex_points_scene(self) -> list:
        """Return absolute scene positions of all vertices (rotation-aware)."""
        return [
            self.mapToScene(QPointF(pt[0] * self._width, pt[1] * self._height))
            for pt in self._rel_points
        ]

    def _vertex_points_local(self) -> list:
        """Return local positions of all vertices."""
        return [
            QPointF(pt[0] * self._width, pt[1] * self._height)
            for pt in self._rel_points
        ]

    def _ctrl_point_info(self) -> list:
        """Return list of (vertex_idx, label, local_QPointF) for all control points."""
        result = []
        w, h = self._width, self._height
        for i, pt in enumerate(self._rel_points):
            if len(pt) >= 5 and pt[2] == "Q":
                result.append((i, "cp", QPointF(pt[3] * w, pt[4] * h)))
            elif len(pt) >= 7 and pt[2] == "C":
                result.append((i, "c1", QPointF(pt[3] * w, pt[4] * h)))
                result.append((i, "c2", QPointF(pt[5] * w, pt[6] * h)))
        return result

    def _hit_test_ctrl_point(self, scene_pt: QPointF) -> Optional[Tuple[int, str]]:
        """Return (vertex_idx, label) of control point near scene_pt, or None.

        Uses QPainterPath circle containment for consistency with shape().
        """
        hit_r = _get_hit_distance()
        local_pt = self.mapFromScene(scene_pt)
        for vi, label, lp in self._ctrl_point_info():
            circle = QPainterPath()
            circle.addEllipse(lp, hit_r, hit_r)
            if circle.contains(local_pt):
                return (vi, label)
        return None

    def _hit_test_vertex(self, scene_pt: QPointF) -> Optional[int]:
        """Return index of vertex near scene_pt, or None.

        Uses QPainterPath circle containment for consistency with shape().
        Tests in reverse order so the last-drawn vertex wins when
        vertices overlap (matching visual stacking).
        """
        hit_r = _get_hit_distance()
        local_pt = self.mapFromScene(scene_pt)
        verts = self._vertex_points_local()
        # Reverse iteration: last vertex is drawn on top, so test it first
        for i in range(len(verts) - 1, -1, -1):
            circle = QPainterPath()
            circle.addEllipse(verts[i], hit_r, hit_r)
            if circle.contains(local_pt):
                return i
        return None

    def _hit_test_edge(self, scene_pt: QPointF) -> Optional[int]:
        """Return index of edge near scene_pt, or None.

        Edge i is the segment arriving at vertex (i+1) % n from vertex i.
        For curved edges (Q/C), the actual curve path is sampled.
        Hits near vertex endpoints (t < 0.15 or t > 0.85) are rejected
        so that vertex knobs take priority over edge hits.
        """
        hit_dist = _get_hit_distance()
        n = len(self._rel_points)
        if n < 2:
            return None
        w, h = self._width, self._height
        # Pre-compute local test point once
        local_pt = self.mapFromScene(scene_pt)

        for i in range(n):
            j = (i + 1) % n
            pt_j = self._rel_points[j]
            # Build sample points along this edge in local coords
            a = QPointF(self._rel_points[i][0] * w, self._rel_points[i][1] * h)
            b = QPointF(pt_j[0] * w, pt_j[1] * h)

            if len(pt_j) >= 7 and pt_j[2] == "C":
                # Cubic bezier: sample the curve
                c1 = QPointF(pt_j[3] * w, pt_j[4] * h)
                c2 = QPointF(pt_j[5] * w, pt_j[6] * h)
                samples = self._sample_cubic(a, c1, c2, b, 20)
            elif len(pt_j) >= 5 and pt_j[2] == "Q":
                # Quadratic bezier: sample the curve
                cp = QPointF(pt_j[3] * w, pt_j[4] * h)
                samples = self._sample_quadratic(a, cp, b, 20)
            else:
                # Straight line: just use endpoints
                samples = [a, b]

            # Find closest point on this edge's sample segments
            best_dist = float("inf")
            best_t_global = 0.0
            total_segs = len(samples) - 1
            for si in range(total_segs):
                sa = samples[si]
                sb = samples[si + 1]
                seg_dx = sb.x() - sa.x()
                seg_dy = sb.y() - sa.y()
                seg_len_sq = seg_dx * seg_dx + seg_dy * seg_dy
                if seg_len_sq < 1e-12:
                    continue
                t_seg = ((local_pt.x() - sa.x()) * seg_dx +
                         (local_pt.y() - sa.y()) * seg_dy) / seg_len_sq
                t_seg = max(0.0, min(1.0, t_seg))
                proj = QPointF(sa.x() + t_seg * seg_dx, sa.y() + t_seg * seg_dy)
                d = QLineF(local_pt, proj).length()
                if d < best_dist:
                    best_dist = d
                    best_t_global = (si + t_seg) / total_segs

            if best_dist <= hit_dist and 0.15 <= best_t_global <= 0.85:
                return i
        return None

    @staticmethod
    def _sample_cubic(p0: QPointF, c1: QPointF, c2: QPointF, p3: QPointF,
                      n: int) -> list:
        """Return n+1 sample points along a cubic bezier."""
        pts = []
        for k in range(n + 1):
            t = k / n
            u = 1.0 - t
            x = (u*u*u * p0.x() + 3*u*u*t * c1.x() +
                 3*u*t*t * c2.x() + t*t*t * p3.x())
            y = (u*u*u * p0.y() + 3*u*u*t * c1.y() +
                 3*u*t*t * c2.y() + t*t*t * p3.y())
            pts.append(QPointF(x, y))
        return pts

    @staticmethod
    def _sample_quadratic(p0: QPointF, cp: QPointF, p2: QPointF,
                          n: int) -> list:
        """Return n+1 sample points along a quadratic bezier."""
        pts = []
        for k in range(n + 1):
            t = k / n
            u = 1.0 - t
            x = u*u * p0.x() + 2*u*t * cp.x() + t*t * p2.x()
            y = u*u * p0.y() + 2*u*t * cp.y() + t*t * p2.y()
            pts.append(QPointF(x, y))
        return pts

    # ---- Mouse interaction ----

    # ---- Vertex context menu / type change ----

    def _serialize_points(self) -> list:
        """Serialize _rel_points preserving curve type and control points."""
        result = []
        for pt in self._rel_points:
            if len(pt) >= 5 and pt[2] == "Q":
                result.append([round(pt[0], 4), round(pt[1], 4), "Q",
                                round(pt[3], 4), round(pt[4], 4)])
            elif len(pt) >= 7 and pt[2] == "C":
                result.append([round(pt[0], 4), round(pt[1], 4), "C",
                                round(pt[3], 4), round(pt[4], 4),
                                round(pt[5], 4), round(pt[6], 4)])
            else:
                result.append([round(pt[0], 4), round(pt[1], 4)])
        return result

    def _show_vertex_context_menu(self, screen_pos, idx: int):
        """Show context menu for a vertex: change type, add, delete."""
        from PyQt6.QtWidgets import QMenu
        menu = QMenu()
        pt = self._rel_points[idx]
        cur_type = pt[2] if len(pt) >= 3 and isinstance(pt[2], str) else "L"

        type_menu = menu.addMenu("Vertex Type")
        for label, vtype in [("Straight (L)", "L"), ("Quadratic (Q)", "Q"), ("Cubic (C)", "C")]:
            act = type_menu.addAction(label)
            act.setCheckable(True)
            act.setChecked(cur_type == vtype)
            act.triggered.connect(lambda checked, t=vtype: self._change_vertex_type(idx, t))

        menu.addSeparator()
        ins_act = menu.addAction("Add Node After")
        ins_act.triggered.connect(lambda: self._insert_vertex_after(idx))

        if len(self._rel_points) > 3:
            del_act = menu.addAction("Delete Node")
            del_act.triggered.connect(lambda: self._delete_vertex(idx))

        menu.exec(screen_pos)

    def _show_edge_context_menu(self, screen_pos, edge_idx: int, scene_pt: QPointF):
        """Show context menu for an edge: insert vertex here."""
        from PyQt6.QtWidgets import QMenu
        menu = QMenu()
        ins_act = menu.addAction("Insert Vertex Here")
        ins_act.triggered.connect(lambda: self._insert_vertex_at(edge_idx, scene_pt))
        menu.exec(screen_pos)

    def _change_vertex_type(self, idx: int, new_type: str):
        """Change a vertex's segment type, auto-generating control points."""
        pt = self._rel_points[idx]
        rx, ry = pt[0], pt[1]
        old_type = pt[2] if len(pt) >= 3 and isinstance(pt[2], str) else "L"
        if old_type == new_type:
            return
        prev_pt = self._rel_points[idx - 1] if idx > 0 else self._rel_points[-1]
        px, py = prev_pt[0], prev_pt[1]
        if new_type == "L":
            self._rel_points[idx] = [rx, ry]
        elif new_type == "Q":
            cx = (px + rx) / 2
            cy = (py + ry) / 2
            self._rel_points[idx] = [rx, ry, "Q", cx, cy]
        elif new_type == "C":
            c1x = px + (rx - px) / 3
            c1y = py + (ry - py) / 3
            c2x = px + 2 * (rx - px) / 3
            c2y = py + 2 * (ry - py) / 3
            self._rel_points[idx] = [rx, ry, "C", c1x, c1y, c2x, c2y]
        self.prepareGeometryChange()
        self._recalculate_bbox()
        self._notify_changed()

    def _insert_vertex_after(self, idx: int):
        """Insert a new straight vertex midway between vertex idx and the next."""
        next_idx = (idx + 1) % len(self._rel_points)
        pt = self._rel_points[idx]
        npt = self._rel_points[next_idx]
        rx = (pt[0] + npt[0]) / 2
        ry = (pt[1] + npt[1]) / 2
        self.prepareGeometryChange()
        self._rel_points.insert(idx + 1, [rx, ry])
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()
        self._notify_changed()

    def _insert_vertex_at(self, edge_idx: int, scene_pt: QPointF):
        """Insert a vertex at the given scene position on edge edge_idx."""
        local_pt = self.mapFromScene(scene_pt)
        rx = local_pt.x() / self._width if self._width > 0 else 0.5
        ry = local_pt.y() / self._height if self._height > 0 else 0.5
        self.prepareGeometryChange()
        self._rel_points.insert(edge_idx + 1, [rx, ry])
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()
        self._notify_changed()

    def _delete_vertex(self, idx: int):
        """Delete a vertex (minimum 3 vertices)."""
        if len(self._rel_points) <= 3:
            return
        self.prepareGeometryChange()
        del self._rel_points[idx]
        self._recalculate_bbox()
        self._notify_changed()

    # ---- Mouse interaction ----

    def hoverMoveEvent(self, event):
        if self._vertex_editing:
            scene_pt = event.scenePos()
            idx = self._hit_test_vertex(scene_pt)
            old_hover = self._hover_vertex
            if idx is not None:
                self._hover_vertex = idx
                self.setCursor(Qt.CursorShape.CrossCursor)
            else:
                self._hover_vertex = None
                if self._hit_test_ctrl_point(scene_pt) is not None:
                    self.setCursor(Qt.CursorShape.CrossCursor)
                elif self._hit_test_edge(scene_pt) is not None:
                    self.setCursor(_get_crosshair_plus_cursor())
                else:
                    self.setCursor(Qt.CursorShape.ArrowCursor)
            if old_hover != self._hover_vertex:
                self.update()  # repaint to show/hide hover highlight
        else:
            h = self._hit_test_handle(event.scenePos())
            if h == "rotate":
                self.setCursor(_get_rotate_cursor())
            elif h:
                self.setCursor(self._cursor_for_handle(h))
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._vertex_editing:
                # In edit mode: only exit if double-click is on empty space.
                scene_pt = event.scenePos()
                if (self._hit_test_vertex(scene_pt) is not None
                        or self._hit_test_ctrl_point(scene_pt) is not None
                        or self._hit_test_edge(scene_pt) is not None):
                    event.accept()
                    return
                self._vertex_editing = False
                self._selected_vertex = None
                self._hover_vertex = None
            else:
                self._vertex_editing = True
            self.prepareGeometryChange()
            self.update()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton and self._vertex_editing:
            scene_pt = event.scenePos()
            if self._selected_vertex is not None:
                idx = self._hit_test_vertex(scene_pt)
                if idx is not None and idx == self._selected_vertex:
                    self._show_vertex_context_menu(event.screenPos(), idx)
                    event.accept()
                    return
            edge_idx = self._hit_test_edge(scene_pt)
            if edge_idx is not None:
                self._show_edge_context_menu(event.screenPos(), edge_idx, scene_pt)
                event.accept()
                return
            event.accept()
            return

        if event.button() == Qt.MouseButton.LeftButton:
            if self._vertex_editing:
                scene_pt = event.scenePos()
                cp_hit = self._hit_test_ctrl_point(scene_pt)
                if cp_hit is not None:
                    self._selected_vertex = None
                    self._active_ctrl_point = cp_hit
                    self._ctrl_dragging = True
                    self.update()
                    event.accept()
                    return
                idx = self._hit_test_vertex(scene_pt)
                if idx is not None:
                    self._selected_vertex = idx
                    self._begin_resize_tracking()
                    self._active_vertex = idx
                    self._press_scene = event.scenePos()
                    self.update()
                    event.accept()
                    return
                edge_idx = self._hit_test_edge(scene_pt)
                if edge_idx is not None:
                    self._selected_vertex = None
                    self._insert_vertex_at(edge_idx, scene_pt)
                    self.update()
                    event.accept()
                    return
                self._selected_vertex = None
                self.update()
                event.accept()
                return

            h = self._hit_test_handle(event.scenePos())
            if h == "rotate":
                self._begin_rotation()
                event.accept()
                return
            if h:
                self._begin_resize_tracking()
                self._active_handle = h
                self._resizing = True
                self._store_resize_anchor(h)
                self._press_scene = event.scenePos()
                self._start_pos = QPointF(self.pos())
                self._start_size = (self._width, self._height)
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._rotating:
            self._handle_rotation_move(event)
            return
        # Control point dragging
        if self._ctrl_dragging and self._active_ctrl_point is not None:
            vi, label = self._active_ctrl_point
            local_pt = self.mapFromScene(event.scenePos())
            rx = local_pt.x() / self._width if self._width > 0 else 0.5
            ry = local_pt.y() / self._height if self._height > 0 else 0.5
            pt = self._rel_points[vi]
            if label == "cp" and len(pt) >= 5 and pt[2] == "Q":
                self._rel_points[vi] = [pt[0], pt[1], "Q", rx, ry]
            elif label == "c1" and len(pt) >= 7 and pt[2] == "C":
                self._rel_points[vi] = [pt[0], pt[1], "C", rx, ry, pt[5], pt[6]]
            elif label == "c2" and len(pt) >= 7 and pt[2] == "C":
                self._rel_points[vi] = [pt[0], pt[1], "C", pt[3], pt[4], rx, ry]
            self.prepareGeometryChange()
            self._update_path()
            self._update_label_position()
            self._update_transform_origin()
            self._notify_changed()
            event.accept()
            return
        # Promote click-to-select into drag once the mouse moves
        if (not self._vertex_dragging and self._active_vertex is not None
                and self._press_scene is not None):
            self._vertex_dragging = True
        # Vertex dragging — allow dragging outside the current bounding box
        if self._vertex_dragging and self._active_vertex is not None:
            # Map scene position to local coordinates (rotation-aware)
            local_pt = self.mapFromScene(event.scenePos())
            # Compute unclamped relative position (can exceed 0-1 range)
            rx = local_pt.x() / self._width if self._width > 0 else 0.5
            ry = local_pt.y() / self._height if self._height > 0 else 0.5
            pt = self._rel_points[self._active_vertex]
            if len(pt) >= 5 and pt[2] == "Q":
                self._rel_points[self._active_vertex] = [rx, ry, "Q", pt[3], pt[4]]
            elif len(pt) >= 7 and pt[2] == "C":
                self._rel_points[self._active_vertex] = [rx, ry, "C", pt[3], pt[4], pt[5], pt[6]]
            else:
                self._rel_points[self._active_vertex] = [rx, ry]
            self.prepareGeometryChange()
            self._update_path()
            self._update_label_position()
            self._update_transform_origin()
            self._notify_changed()
            event.accept()
            return

        # Bounding-box handle resize
        if self._resizing and self._active_handle and self._press_scene and self._start_pos and self._start_size:
            cur = event.scenePos()
            dx, dy = self._scene_delta_to_local(
                cur.x() - self._press_scene.x(),
                cur.y() - self._press_scene.y())

            w0, h0 = self._start_size
            new_w, new_h, anchor_after = self._compute_resize(
                self._active_handle, dx, dy, w0, h0)
            self._width = new_w
            self._height = new_h
            self._update_path()
            self._update_label_position()
            self._update_transform_origin()
            self._fixup_resize_pos(anchor_after)
            self._notify_changed()
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._ctrl_dragging:
            self._ctrl_dragging = False
            self._active_ctrl_point = None
            self._selected_vertex = None
            self._recalculate_bbox()
            self._notify_changed()
            self.update()
            event.accept()
            return
        if self._vertex_dragging:
            # Actual drag happened — deselect after release
            self._end_resize_tracking()
            self._vertex_dragging = False
            self._active_vertex = None
            self._selected_vertex = None
            self._recalculate_bbox()
            self._notify_changed()
            self.update()
            event.accept()
            return
        if self._active_vertex is not None:
            # Click-only (no drag) — keep vertex selected, clean up press state
            self._active_vertex = None
            self._press_scene = None
            self._end_resize_tracking()
            self.update()
            event.accept()
            return
        if self._rotating:
            self._end_rotation()
            event.accept()
            return
        if self._resizing:
            self._end_resize_tracking()
            self._resizing = False
            self._active_handle = None
            self._press_scene = None
            self._start_pos = None
            self._start_size = None
            self._notify_changed()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    # ---- Shape / bounds / paint ----

    def shape(self) -> QPainterPath:
        base = super().shape()
        if self._should_paint_handles() and not self._vertex_editing:
            return shape_with_handles(base, self._handle_points_local(),
                                      rotation_knob_local=self._rotation_knob_local() if self._is_rotatable() else None)
        if self._should_paint_handles() and self._vertex_editing:
            # Use hit_distance for knob areas so shape matches hit testing
            hit_r = _get_hit_distance()
            verts = self._vertex_points_local()
            # Add vertex knob hit areas
            for vp in verts:
                base.addEllipse(vp, hit_r, hit_r)
            # Add control point hit areas
            for _vi, _label, cp in self._ctrl_point_info():
                base.addEllipse(cp, hit_r, hit_r)
            # Add edge stroke areas using the actual polygon path (curves included)
            from PyQt6.QtGui import QPainterPathStroker
            stroker = QPainterPathStroker()
            stroker.setWidth(max(hit_r * 2, 12))
            base = base.united(stroker.createStroke(self.path()))
        return base

    def boundingRect(self) -> QRectF:
        r = super().boundingRect()
        margin = max(_get_handle_size() / 2 + 1, _get_hit_distance() + 1)
        return r.adjusted(-margin, -margin, margin, margin)

    def paint(self, painter: QPainter, option, widget=None):
        my_option = QStyleOptionGraphicsItem(option)
        my_option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, my_option, widget)

        if not self._should_paint_handles():
            return

        if self._vertex_editing:
            handle_size = _get_handle_size()
            half = handle_size / 2
            w, h = self._width, self._height
            # Draw control point handles first (behind vertex knobs)
            cp_pen = QPen(QColor(100, 100, 200), 1, Qt.PenStyle.DashLine)
            cp_brush = QBrush(QColor(100, 100, 220))
            cp_pen_solid = QPen(QColor(50, 50, 180), 1)
            for i, pt in enumerate(self._rel_points):
                if len(pt) >= 5 and pt[2] == "Q":
                    anchor = QPointF(pt[0] * w, pt[1] * h)
                    cp = QPointF(pt[3] * w, pt[4] * h)
                    painter.setPen(cp_pen)
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    painter.drawLine(anchor, cp)
                    painter.setPen(cp_pen_solid)
                    painter.setBrush(cp_brush)
                    painter.drawEllipse(QRectF(cp.x() - half, cp.y() - half, handle_size, handle_size))
                elif len(pt) >= 7 and pt[2] == "C":
                    anchor = QPointF(pt[0] * w, pt[1] * h)
                    c1 = QPointF(pt[3] * w, pt[4] * h)
                    c2 = QPointF(pt[5] * w, pt[6] * h)
                    prev_pt = self._rel_points[i - 1] if i > 0 else self._rel_points[-1]
                    prev_anchor = QPointF(prev_pt[0] * w, prev_pt[1] * h)
                    painter.setPen(cp_pen)
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    painter.drawLine(prev_anchor, c1)
                    painter.drawLine(anchor, c2)
                    painter.setPen(cp_pen_solid)
                    painter.setBrush(cp_brush)
                    painter.drawEllipse(QRectF(c1.x() - half, c1.y() - half, handle_size, handle_size))
                    painter.drawEllipse(QRectF(c2.x() - half, c2.y() - half, handle_size, handle_size))
            # Draw vertex knobs
            for i, vp in enumerate(self._vertex_points_local()):
                if i == self._selected_vertex or i == self._active_vertex:
                    # Selected / dragging: orange fill + orange outline
                    painter.setPen(QPen(QColor(204, 102, 0), 2))
                    painter.setBrush(QBrush(QColor(255, 165, 0)))
                elif i == self._hover_vertex:
                    # Hover: green fill + thick orange outline
                    painter.setPen(QPen(QColor(204, 102, 0), 2))
                    painter.setBrush(QBrush(QColor(0, 200, 0)))
                else:
                    # Normal: green fill + thin green outline
                    painter.setPen(QPen(QColor(0, 128, 0), 1))
                    painter.setBrush(QBrush(QColor(0, 200, 0)))
                painter.drawEllipse(QRectF(vp.x() - half, vp.y() - half,
                                           handle_size, handle_size))
        else:
            # Draw selection outline and bounding-box handles
            sel_pen = QPen(_get_selection_color(), 1, Qt.PenStyle.DashLine)
            painter.setPen(sel_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(self.path())

            draw_handles(painter, self._handle_points_local())
            self._draw_rotation_knob(painter)

    def itemChange(self, change, value):
        out = super().itemChange(change, value)
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if not self._resizing and not self._vertex_dragging:
                self._notify_changed()
            self._update_child_port_connections()
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            if not value:
                self._vertex_editing = False
                self._selected_vertex = None
                self._hover_vertex = None
            self.prepareGeometryChange()
        return out

    def to_record(self) -> Dict[str, Any]:
        p = self.pos()
        rec = {
            "id": self.ann_id,
            "kind": "polygon",
            **self._ports_dict(),
            "geom": {
                "x": round1(p.x()),
                "y": round1(p.y()),
                "w": round1(self._width),
                "h": round1(self._height),
                "points": self._serialize_points(),
            },
            **self._meta_dict(self.meta),
            **self._style_dict(),
        }
        z = self.zValue()
        if z != 0:
            rec["z"] = int(z)
        self._add_angle_to_geom(rec.get("geom", {}))
        return rec


class MetaCurveItem(QGraphicsPathItem, MetaMixin, LinkedMixin):
    """Arbitrary curve item with SVG path-like node editing.

    Nodes are stored as dicts with 'cmd' and relative coordinates (0.0-1.0)
    within the bounding box. The curve is stroke-only (no fill) and supports
    arrowheads. Double-click to enter node-edit mode where individual nodes
    and control points can be dragged.
    """

    KIND = "curve"
    KIND_ALIASES = frozenset(k for k, v in KIND_ALIAS_MAP.items() if v == "curve")

    ARROW_NONE = "none"
    ARROW_START = "start"
    ARROW_END = "end"
    ARROW_BOTH = "both"

    # Valid SVG path commands
    _VALID_CMDS = {"M", "L", "H", "V", "C", "S", "Q", "T", "A", "Z"}

    on_adjust1_changed = None  # Called with (item, new_value) when adjust1 changes via handle drag

    def __init__(self, x: float, y: float, w: float, h: float,
                 nodes: list, ann_id: str, on_change=None):
        QGraphicsPathItem.__init__(self)
        MetaMixin.__init__(self)
        LinkedMixin.__init__(self, ann_id, on_change)

        self.kind ="curve"
        self._width = max(w, 1.0)
        self._height = max(h, 1.0)
        self._adjust1 = 0.0  # bend radius in pixels for H/V corners
        self._start_adjust1: Optional[float] = None  # for drag tracking

        # Deep copy nodes and validate
        import copy
        self._nodes = [dict(n) for n in nodes] if nodes else [{"cmd": "M", "x": 0.0, "y": 0.0}]
        if self._nodes[0].get("cmd") != "M":
            self._nodes.insert(0, {"cmd": "M", "x": 0.0, "y": 0.0})

        self.setPos(QPointF(x, y))
        self.setData(ANN_ID_KEY, ann_id)

        self.setAcceptHoverEvents(True)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        # Bounding-box resize state
        self._active_handle: Optional[str] = None
        self._resizing = False
        self._press_scene: Optional[QPointF] = None
        self._start_pos: Optional[QPointF] = None
        self._start_size: Optional[Tuple[float, float]] = None

        # Node editing state
        self._node_editing = False
        self._active_node: Optional[int] = None
        self._active_handle_type: Optional[str] = None  # "anchor"/"c1"/"c2"/"cx"
        self._node_dragging = False
        self._snap_port: Optional['MetaPortItem'] = None  # port being hovered during drag
        self._port_ids: List[str] = []  # connected port IDs (read-only, computed)
        self._port_endpoints: Dict[str, str] = {}  # port_id → "start"|"end"

        # Arrow support
        self.arrow_mode = self.ARROW_NONE
        self.arrow_size = 12.0

        # Style
        self.pen_color = QColor(Qt.GlobalColor.darkMagenta)
        self.pen_width = 2
        self.brush_color = QColor(255, 255, 255)  # Text box background fill
        self.text_color = QColor(self.pen_color)
        self.line_dash = "solid"
        cached = _CachedCanvasSettings.get()
        self.dash_pattern_length = cached.default_dash_length
        self.dash_solid_percent = cached.default_dash_solid_percent
        self._apply_pen_brush()

        # Text box properties (local coordinates, computed from anchor_value)
        self._text_box_rect: Optional[QRectF] = None
        self._drag_text_box: Optional[str] = None

        # Embedded text for C4 properties
        self._label_item = QGraphicsTextItem(self)
        self._label_item.setAcceptHoverEvents(False)
        self._label_item.setDefaultTextColor(self.text_color)
        self._label_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self._update_path()
        self._update_label_position()
        self._update_transform_origin()

    # ---- Path / geometry ----

    def _update_path(self):
        """Rebuild QPainterPath from _nodes and current dimensions."""
        path = QPainterPath()
        if not self._nodes:
            self.setPath(path)
            return

        w, h = self._width, self._height
        prev_x, prev_y = 0.0, 0.0  # track last endpoint for H/V/S/T
        r = self._adjust1  # bend radius in pixels

        for i, node in enumerate(self._nodes):
            cmd = node.get("cmd", "L")
            nx = node.get("x", prev_x)
            ny = node.get("y", prev_y)

            if cmd == "M":
                path.moveTo(nx * w, ny * h)
                prev_x, prev_y = nx, ny
            elif cmd == "L":
                path.lineTo(nx * w, ny * h)
                prev_x, prev_y = nx, ny
            elif cmd in ("H", "V"):
                # Compute the target endpoint for this segment
                if cmd == "H":
                    target_x, target_y = nx, prev_y
                else:  # V
                    target_x, target_y = prev_x, ny

                # Check if next node forms a corner and we have a bend radius.
                # Corners: H→V, V→H, or H/V→L (final endpoint).
                next_node = self._nodes[i + 1] if i + 1 < len(self._nodes) else None
                next_cmd = next_node.get("cmd", "") if next_node else ""
                has_hv_corner = (r > 0 and next_cmd in ("H", "V")
                                 and next_cmd != cmd)
                has_endpoint_corner = (r > 0 and next_cmd == "L"
                                       and i + 1 == len(self._nodes) - 1)
                has_corner = has_hv_corner or has_endpoint_corner

                if has_corner:
                    # Compute next segment endpoint
                    if next_cmd == "H":
                        next_target_x = next_node.get("x", target_x)
                        next_target_y = target_y
                    elif next_cmd == "V":
                        next_target_x = target_x
                        next_target_y = next_node.get("y", target_y)
                    else:  # L endpoint
                        next_target_x = next_node.get("x", target_x)
                        next_target_y = next_node.get("y", target_y)

                    # Incoming segment length (in pixels)
                    in_dx = (target_x - prev_x) * w
                    in_dy = (target_y - prev_y) * h
                    in_len = math.sqrt(in_dx * in_dx + in_dy * in_dy)

                    # Outgoing segment length (in pixels)
                    out_dx = (next_target_x - target_x) * w
                    out_dy = (next_target_y - target_y) * h
                    out_len = math.sqrt(out_dx * out_dx + out_dy * out_dy)

                    effective_r = min(r, in_len / 2, out_len / 2)

                    if effective_r > 0.5:
                        # Normalize incoming and outgoing directions
                        in_ux = in_dx / in_len if in_len > 0 else 0
                        in_uy = in_dy / in_len if in_len > 0 else 0
                        out_ux = out_dx / out_len if out_len > 0 else 0
                        out_uy = out_dy / out_len if out_len > 0 else 0

                        # Stop r pixels before the corner
                        arc_start_x = target_x * w - in_ux * effective_r
                        arc_start_y = target_y * h - in_uy * effective_r
                        # Start r pixels into the outgoing segment
                        arc_end_x = target_x * w + out_ux * effective_r
                        arc_end_y = target_y * h + out_uy * effective_r

                        path.lineTo(arc_start_x, arc_start_y)
                        path.quadTo(target_x * w, target_y * h,
                                    arc_end_x, arc_end_y)

                        # Update prev to arc endpoint in relative coords
                        prev_x = arc_end_x / w if w > 0 else target_x
                        prev_y = arc_end_y / h if h > 0 else target_y
                    else:
                        # Too small for rounding, just draw straight
                        path.lineTo(target_x * w, target_y * h)
                        prev_x, prev_y = target_x, target_y
                else:
                    # No corner or no radius — straight line
                    path.lineTo(target_x * w, target_y * h)
                    prev_x, prev_y = target_x, target_y
            elif cmd == "C":
                c1x = node.get("c1x", prev_x)
                c1y = node.get("c1y", prev_y)
                c2x = node.get("c2x", nx)
                c2y = node.get("c2y", ny)
                path.cubicTo(c1x * w, c1y * h, c2x * w, c2y * h, nx * w, ny * h)
                prev_x, prev_y = nx, ny
            elif cmd == "S":
                c2x = node.get("c2x", nx)
                c2y = node.get("c2y", ny)
                c1x, c1y = self._mirror_control_point(i, "cubic")
                path.cubicTo(c1x * w, c1y * h, c2x * w, c2y * h, nx * w, ny * h)
                prev_x, prev_y = nx, ny
            elif cmd == "Q":
                cx = node.get("cx", (prev_x + nx) / 2)
                cy = node.get("cy", (prev_y + ny) / 2)
                path.quadTo(cx * w, cy * h, nx * w, ny * h)
                prev_x, prev_y = nx, ny
            elif cmd == "T":
                cx, cy = self._mirror_control_point(i, "quadratic")
                path.quadTo(cx * w, cy * h, nx * w, ny * h)
                prev_x, prev_y = nx, ny
            elif cmd == "A":
                # Convert arc to cubic beziers
                rx_a = node.get("rx", 0.1)
                ry_a = node.get("ry", 0.1)
                rotation = node.get("rotation", 0)
                large_arc = node.get("large_arc", 0)
                sweep = node.get("sweep", 1)
                cubics = self._arc_to_cubics(
                    prev_x, prev_y, rx_a, ry_a, rotation, large_arc, sweep, nx, ny
                )
                for c in cubics:
                    path.cubicTo(c[0] * w, c[1] * h, c[2] * w, c[3] * h, c[4] * w, c[5] * h)
                prev_x, prev_y = nx, ny
            elif cmd == "Z":
                path.closeSubpath()
                # prev_x, prev_y stay at the last move-to (Qt handles this)

        self.setPath(path)

    def _mirror_control_point(self, node_idx: int, kind: str) -> Tuple[float, float]:
        """Mirror a control point from the previous C/S or Q/T node.

        Args:
            node_idx: Index of the current S/T node
            kind: "cubic" (for S) or "quadratic" (for T)

        Returns:
            (cx, cy) mirrored control point in relative coords
        """
        if node_idx < 1:
            return (0.0, 0.0)

        prev = self._nodes[node_idx - 1]
        prev_cmd = prev.get("cmd", "L")
        prev_x = prev.get("x", 0.0)
        prev_y = prev.get("y", 0.0)

        if kind == "cubic" and prev_cmd in ("C", "S"):
            # Mirror the last control point (c2) across the endpoint
            if prev_cmd == "C":
                c2x = prev.get("c2x", prev_x)
                c2y = prev.get("c2y", prev_y)
            else:  # S
                c2x = prev.get("c2x", prev_x)
                c2y = prev.get("c2y", prev_y)
            return (2 * prev_x - c2x, 2 * prev_y - c2y)

        if kind == "quadratic" and prev_cmd in ("Q", "T"):
            if prev_cmd == "Q":
                cx = prev.get("cx", prev_x)
                cy = prev.get("cy", prev_y)
            else:  # T — recursively mirrored, just use endpoint
                cx = prev_x
                cy = prev_y
            return (2 * prev_x - cx, 2 * prev_y - cy)

        # No previous matching command — control point coincides with prev endpoint
        return (prev_x, prev_y)

    @staticmethod
    def _arc_to_cubics(x1, y1, rx, ry, rotation, large_arc, sweep, x2, y2):
        """Convert SVG arc parameters to cubic bezier segments.

        All coordinates are in relative (0-1) space.

        Returns:
            List of tuples: [(c1x, c1y, c2x, c2y, ex, ey), ...]
        """
        # Handle degenerate cases
        if abs(rx) < 1e-10 or abs(ry) < 1e-10:
            return [(x1, y1, x2, y2, x2, y2)]
        if abs(x2 - x1) < 1e-10 and abs(y2 - y1) < 1e-10:
            return []

        rx = abs(rx)
        ry = abs(ry)
        phi = math.radians(rotation)
        cos_phi = math.cos(phi)
        sin_phi = math.sin(phi)

        # Step 1: Compute (x1', y1')
        dx = (x1 - x2) / 2
        dy = (y1 - y2) / 2
        x1p = cos_phi * dx + sin_phi * dy
        y1p = -sin_phi * dx + cos_phi * dy

        # Step 2: Correct radii
        lam = (x1p * x1p) / (rx * rx) + (y1p * y1p) / (ry * ry)
        if lam > 1:
            lam_sqrt = math.sqrt(lam)
            rx *= lam_sqrt
            ry *= lam_sqrt

        # Step 3: Compute center point
        num = max(0, rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p)
        den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
        sq = math.sqrt(num / den) if den > 1e-20 else 0
        if large_arc == sweep:
            sq = -sq
        cxp = sq * rx * y1p / ry
        cyp = -sq * ry * x1p / rx

        # Step 4: Compute center (cx, cy)
        cx = cos_phi * cxp - sin_phi * cyp + (x1 + x2) / 2
        cy = sin_phi * cxp + cos_phi * cyp + (y1 + y2) / 2

        # Step 5: Compute angles
        def angle(ux, uy, vx, vy):
            n = math.sqrt(ux * ux + uy * uy) * math.sqrt(vx * vx + vy * vy)
            if n < 1e-20:
                return 0
            c = max(-1, min(1, (ux * vx + uy * vy) / n))
            a = math.acos(c)
            if ux * vy - uy * vx < 0:
                a = -a
            return a

        theta1 = angle(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
        dtheta = angle(
            (x1p - cxp) / rx, (y1p - cyp) / ry,
            (-x1p - cxp) / rx, (-y1p - cyp) / ry
        )

        if sweep == 0 and dtheta > 0:
            dtheta -= 2 * math.pi
        elif sweep == 1 and dtheta < 0:
            dtheta += 2 * math.pi

        # Step 6: Split into segments of at most pi/2
        n_segs = max(1, int(math.ceil(abs(dtheta) / (math.pi / 2))))
        d_per_seg = dtheta / n_segs
        alpha = 4.0 / 3.0 * math.tan(d_per_seg / 4)

        cubics = []
        theta = theta1
        for _ in range(n_segs):
            cos_t = math.cos(theta)
            sin_t = math.sin(theta)
            cos_t2 = math.cos(theta + d_per_seg)
            sin_t2 = math.sin(theta + d_per_seg)

            ep1x = rx * cos_t
            ep1y = ry * sin_t
            ep2x = rx * cos_t2
            ep2y = ry * sin_t2

            # Control points on the unit circle
            c1x = ep1x - alpha * rx * sin_t
            c1y = ep1y + alpha * ry * cos_t
            c2x = ep2x + alpha * rx * sin_t2
            c2y = ep2y - alpha * ry * cos_t2

            # Transform back from arc space
            def transform(ax, ay):
                return (
                    cos_phi * ax - sin_phi * ay + cx,
                    sin_phi * ax + cos_phi * ay + cy,
                )

            tc1 = transform(c1x, c1y)
            tc2 = transform(c2x, c2y)
            te = transform(ep2x, ep2y)

            cubics.append((tc1[0], tc1[1], tc2[0], tc2[1], te[0], te[1]))
            theta += d_per_seg

        return cubics

    def _get_node_anchor(self, idx: int) -> Tuple[float, float]:
        """Get the effective anchor (endpoint) of a node in relative coords."""
        node = self._nodes[idx]
        cmd = node.get("cmd", "L")
        if cmd == "Z":
            # Z goes back to the last M
            for j in range(idx - 1, -1, -1):
                if self._nodes[j].get("cmd") == "M":
                    return (self._nodes[j].get("x", 0), self._nodes[j].get("y", 0))
            return (0.0, 0.0)
        x = node.get("x", 0.0)
        y = node.get("y", 0.0)
        # For H, y comes from previous; for V, x comes from previous
        if cmd == "H" and idx > 0:
            y = self._get_node_anchor(idx - 1)[1]
        elif cmd == "V" and idx > 0:
            x = self._get_node_anchor(idx - 1)[0]
        return (x, y)

    def _recalculate_bbox(self):
        """Recalculate bounding box to tightly enclose all node coordinates."""
        if not self._nodes:
            return

        p = self.pos()
        all_coords = []

        for i, node in enumerate(self._nodes):
            ax, ay = self._get_node_anchor(i)
            all_coords.append((p.x() + ax * self._width, p.y() + ay * self._height))

            cmd = node.get("cmd", "L")
            if cmd == "C":
                c1x = node.get("c1x", ax)
                c1y = node.get("c1y", ay)
                c2x = node.get("c2x", ax)
                c2y = node.get("c2y", ay)
                all_coords.append((p.x() + c1x * self._width, p.y() + c1y * self._height))
                all_coords.append((p.x() + c2x * self._width, p.y() + c2y * self._height))
            elif cmd == "S":
                c2x = node.get("c2x", ax)
                c2y = node.get("c2y", ay)
                all_coords.append((p.x() + c2x * self._width, p.y() + c2y * self._height))
            elif cmd == "Q":
                cx = node.get("cx", ax)
                cy = node.get("cy", ay)
                all_coords.append((p.x() + cx * self._width, p.y() + cy * self._height))

        if not all_coords:
            return

        xs = [c[0] for c in all_coords]
        ys = [c[1] for c in all_coords]
        new_x = min(xs)
        new_y = min(ys)
        new_w = max(xs) - new_x
        new_h = max(ys) - new_y

        if new_w < 1.0:
            new_w = 1.0
        if new_h < 1.0:
            new_h = 1.0

        # Renormalize all node coordinates into new bbox
        for node in self._nodes:
            cmd = node.get("cmd", "L")
            if cmd == "Z":
                continue
            for key in ("x", "y", "c1x", "c1y", "c2x", "c2y", "cx", "cy"):
                if key not in node:
                    continue
                if key.endswith("x") or key == "x":
                    old_abs = p.x() + node[key] * self._width
                    node[key] = (old_abs - new_x) / new_w
                else:
                    old_abs = p.y() + node[key] * self._height
                    node[key] = (old_abs - new_y) / new_h

        self.prepareGeometryChange()
        self.setPos(QPointF(new_x, new_y))
        self._width = new_w
        self._height = new_h
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()

    def _apply_pen_brush(self):
        """Apply pen and brush (no fill for curves)."""
        pen = QPen(self.pen_color, self.pen_width)
        _apply_dash_style(pen, self.line_dash, self.dash_pattern_length, self.dash_solid_percent)
        self.setPen(pen)
        self.setBrush(QBrush(QColor(0, 0, 0, 0)))  # Transparent fill

    def _point_at_t(self, t: float) -> QPointF:
        """Return the point at parameter *t* (0-1) along the curve path.

        Uses ``QPainterPath.pointAtPercent()`` on the actual rendered path,
        so the result follows cubic/quadratic beziers, arcs, and bend-radius
        corners exactly as drawn.
        """
        path = self.path()
        if path.isEmpty():
            return QPointF(self._width / 2, self._height / 2)
        return path.pointAtPercent(max(0.0, min(1.0, t)))

    def _anchor_box_position(self, ax: float, ay: float, bw: float, bh: float) -> tuple:
        """Compute text box (x, y) from anchor point and text_anchor / text_anchor_v.

        The UI grid is mirrored: clicking the top-right button places the
        box so its *bottom-left* corner sits at the anchor point (the box
        extends up and to the right of the anchor).
        """
        h = getattr(self.meta, "text_anchor", "center")
        v = getattr(self.meta, "text_anchor_v", "middle")
        if h == "left":
            bx = ax
        elif h == "right":
            bx = ax - bw
        else:
            bx = ax - bw / 2
        if v == "top":
            by = ay
        elif v == "bottom":
            by = ay - bh
        else:
            by = ay - bh / 2
        return bx, by

    def _update_label_position(self):
        """Position label at anchor point along the curve path."""
        t = getattr(self.meta, "anchor_value", 50.0) / 100.0
        anchor_pt = self._point_at_t(t)

        has_text_box = (hasattr(self, "meta") and self.meta.text_box_width > 0)
        has_text = bool(self._label_item.toPlainText().strip())

        if has_text_box:
            box_w = self.meta.text_box_width
            ml, mr, mt, mb = self._get_text_margins()
            wrap = getattr(self.meta, "wrap", True)
            if wrap:
                self._label_item.setTextWidth(max(10, box_w - ml - mr))
            else:
                self._label_item.setTextWidth(-1)
            text_height = self._label_item.boundingRect().height()

            if self.meta.text_box_height > 0:
                box_h = self.meta.text_box_height
            else:
                box_h = text_height + mt + mb

            box_x, box_y = self._anchor_box_position(anchor_pt.x(), anchor_pt.y(), box_w, box_h)
            self._text_box_rect = QRectF(box_x, box_y, box_w, box_h)
            self._position_label_in_rect(box_x, box_y, box_w, box_h)
        elif has_text:
            # Auto-size text box from label content
            self._label_item.setTextWidth(-1)
            ml, mr, mt, mb = self._get_text_margins()
            text_rect = self._label_item.boundingRect()
            box_w = text_rect.width() + ml + mr
            box_h = text_rect.height() + mt + mb

            box_x, box_y = self._anchor_box_position(anchor_pt.x(), anchor_pt.y(), box_w, box_h)
            self._text_box_rect = QRectF(box_x, box_y, box_w, box_h)
            self._position_label_in_rect(box_x, box_y, box_w, box_h)
        else:
            self._text_box_rect = None
            self._position_label_in_rect(0, 0, self._width, self._height)

    def _update_label_text(self):
        self._render_label_from_meta()

    def set_meta(self, meta: AnnotationMeta) -> None:
        """Set annotation metadata and update label."""
        self.meta = meta
        self._update_label_text()

    def set_arrow_mode(self, mode: str):
        """Set arrow mode."""
        if mode in (self.ARROW_NONE, self.ARROW_START, self.ARROW_END, self.ARROW_BOTH):
            self.arrow_mode = mode
            self.update()

    def rect(self) -> QRectF:
        """Return bounding rect as QRectF."""
        return QRectF(0, 0, self._width, self._height)

    def setRect(self, r: QRectF):
        """Set bounding box dimensions (used by scene during resize)."""
        self._width = r.width()
        self._height = r.height()
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()

    @property
    def adjust1(self) -> float:
        """Bend radius for H/V corner transitions."""
        return self._adjust1

    def set_adjust1(self, value: float):
        """Set bend radius, clamping >= 0."""
        value = max(0.0, value)
        if abs(value - self._adjust1) < 0.01:
            return
        self._adjust1 = value
        self.prepareGeometryChange()
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()

    def _has_hv_corners(self) -> bool:
        """Return True if this curve has any H->V or V->H transitions."""
        for i in range(1, len(self._nodes)):
            prev_cmd = self._nodes[i - 1].get("cmd", "L")
            cur_cmd = self._nodes[i].get("cmd", "L")
            if (prev_cmd in ("H", "V") and cur_cmd in ("H", "V") and prev_cmd != cur_cmd):
                return True
            # Also detect M->H/V followed by the complement
            if prev_cmd == "M" and cur_cmd in ("H", "V") and i + 1 < len(self._nodes):
                next_cmd = self._nodes[i + 1].get("cmd", "L")
                if next_cmd in ("H", "V") and next_cmd != cur_cmd:
                    return True
        return False

    def _find_first_hv_corner(self) -> Optional[int]:
        """Find index of the second node in the first H->V or V->H pair."""
        for i in range(1, len(self._nodes) - 1):
            cur_cmd = self._nodes[i].get("cmd", "L")
            next_cmd = self._nodes[i + 1].get("cmd", "L")
            if cur_cmd in ("H", "V") and next_cmd in ("H", "V") and cur_cmd != next_cmd:
                return i + 1
        return None

    # ---- Bounding-box handles ----

    def _bend_radius_handle_local(self) -> Optional[QPointF]:
        """Compute local position of the bend radius handle at first H/V corner."""
        corner_idx = self._find_first_hv_corner()
        if corner_idx is None:
            return None
        w, h = self._width, self._height
        # The corner point is the endpoint of the node before corner_idx
        corner_x, corner_y = self._get_node_anchor(corner_idx - 1)
        # Incoming direction from the node before that
        prev_x, prev_y = self._get_node_anchor(corner_idx - 2) if corner_idx >= 2 else (corner_x, corner_y)
        in_dx = (corner_x - prev_x) * w
        in_dy = (corner_y - prev_y) * h
        in_len = math.sqrt(in_dx * in_dx + in_dy * in_dy)
        if in_len < 1e-6:
            return None
        in_ux = in_dx / in_len
        in_uy = in_dy / in_len
        # Position handle r pixels back from corner along incoming direction
        handle_x = corner_x * w - in_ux * self._adjust1
        handle_y = corner_y * h - in_uy * self._adjust1
        return QPointF(handle_x, handle_y)

    def _handle_points_local(self) -> Dict[str, QPointF]:
        cx = self._width / 2
        cy = self._height / 2
        handles = {
            "tl": QPointF(0, 0),
            "tr": QPointF(self._width, 0),
            "bl": QPointF(0, self._height),
            "br": QPointF(self._width, self._height),
            "t":  QPointF(cx, 0),
            "b":  QPointF(cx, self._height),
            "l":  QPointF(0, cy),
            "r":  QPointF(self._width, cy),
        }
        br_local = self._bend_radius_handle_local()
        if br_local is not None:
            handles["adjust1"] = br_local
        return handles

    # ---- Node editing helpers ----

    def _node_points_scene(self) -> list:
        """Return list of (scene_point, node_index, handle_type) for all hit-testable points (rotation-aware)."""
        w, h = self._width, self._height
        result = []
        for i, node in enumerate(self._nodes):
            cmd = node.get("cmd", "L")
            if cmd == "Z":
                continue
            ax, ay = self._get_node_anchor(i)
            result.append((self.mapToScene(QPointF(ax * w, ay * h)), i, "anchor"))
            if cmd == "C":
                c1x, c1y = node.get("c1x", ax), node.get("c1y", ay)
                c2x, c2y = node.get("c2x", ax), node.get("c2y", ay)
                result.append((self.mapToScene(QPointF(c1x * w, c1y * h)), i, "c1"))
                result.append((self.mapToScene(QPointF(c2x * w, c2y * h)), i, "c2"))
            elif cmd == "S":
                c2x, c2y = node.get("c2x", ax), node.get("c2y", ay)
                result.append((self.mapToScene(QPointF(c2x * w, c2y * h)), i, "c2"))
            elif cmd == "Q":
                cx, cy = node.get("cx", ax), node.get("cy", ay)
                result.append((self.mapToScene(QPointF(cx * w, cy * h)), i, "cx"))
        return result

    def _hit_test_node(self, scene_pt: QPointF) -> Optional[Tuple[int, str]]:
        """Hit-test all node points (control points first, then anchors).

        Returns (node_index, handle_type) or None.
        """
        hit_dist = _get_hit_distance()
        points = self._node_points_scene()
        # Test control points first (they overlap anchors but are smaller)
        for pt, idx, htype in points:
            if htype != "anchor" and QLineF(scene_pt, pt).length() <= hit_dist:
                return (idx, htype)
        for pt, idx, htype in points:
            if htype == "anchor" and QLineF(scene_pt, pt).length() <= hit_dist:
                return (idx, htype)
        return None

    def _hit_test_edge(self, scene_pt: QPointF) -> Optional[int]:
        """Hit-test curve segments for node insertion. Returns node index after which to insert."""
        hit_dist = _get_hit_distance()
        p = self.pos()
        w, h = self._width, self._height

        for i in range(1, len(self._nodes)):
            node = self._nodes[i]
            cmd = node.get("cmd", "L")
            if cmd == "Z":
                continue
            ax, ay = self._get_node_anchor(i)
            px_a, py_a = self._get_node_anchor(i - 1)

            # Simple line-segment check for L/H/V
            if cmd in ("L", "H", "V"):
                a = QPointF(p.x() + px_a * w, p.y() + py_a * h)
                b = QPointF(p.x() + ax * w, p.y() + ay * h)
                line = QLineF(a, b)
                length = line.length()
                if length < 1e-6:
                    continue
                ldx = b.x() - a.x()
                ldy = b.y() - a.y()
                t = ((scene_pt.x() - a.x()) * ldx + (scene_pt.y() - a.y()) * ldy) / (length * length)
                t = max(0.0, min(1.0, t))
                proj = QPointF(a.x() + t * ldx, a.y() + t * ldy)
                if QLineF(scene_pt, proj).length() <= hit_dist:
                    return i - 1
        return None

    # ---- Mouse interaction ----

    def hoverMoveEvent(self, event):
        if self._node_editing:
            hit = self._hit_test_node(event.scenePos())
            if hit is not None:
                self.setCursor(Qt.CursorShape.CrossCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            # Check text box handles first
            tb_h = self._hit_test_text_box_handle(event.scenePos())
            if tb_h:
                if tb_h in ("tb_tl", "tb_br"):
                    self.setCursor(Qt.CursorShape.SizeFDiagCursor)
                else:
                    self.setCursor(Qt.CursorShape.SizeBDiagCursor)
                super().hoverMoveEvent(event)
                return
            h = self._hit_test_handle(event.scenePos())
            if h == "adjust1":
                self.setCursor(Qt.CursorShape.CrossCursor)
            elif h:
                self.setCursor(self._cursor_for_handle(h))
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._node_editing = not self._node_editing
            self.prepareGeometryChange()
            self.update()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def _last_anchor_index(self) -> int:
        """Return the index of the last non-Z anchor node."""
        for i in range(len(self._nodes) - 1, -1, -1):
            if self._nodes[i].get("cmd") != "Z":
                return i
        return 0

    def _is_endpoint_index(self, idx: int) -> bool:
        """Return True if *idx* is the first or last anchor node."""
        return idx == 0 or idx == self._last_anchor_index()

    def _node_scene_pos(self, idx: int) -> QPointF:
        """Return the scene position of the anchor at *idx*."""
        ax, ay = self._get_node_anchor(idx)
        return QPointF(self.pos().x() + ax * self._width,
                       self.pos().y() + ay * self._height)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton and self._node_editing:
            scene_pt = event.scenePos()
            hit = self._hit_test_node(scene_pt)
            if hit is not None:
                idx, htype = hit
                if htype == "anchor":
                    self._show_node_context_menu(event.screenPos(), idx)
                    event.accept()
                    return
            # Right-click on edge: insert new L node
            edge_idx = self._hit_test_edge(scene_pt)
            if edge_idx is not None:
                local_pt = self.mapFromScene(scene_pt)
                rx = local_pt.x() / self._width if self._width > 0 else 0.5
                ry = local_pt.y() / self._height if self._height > 0 else 0.5
                self.prepareGeometryChange()
                self._nodes.insert(edge_idx + 1, {"cmd": "L", "x": rx, "y": ry})
                self._update_path()
                self._update_label_position()
                self._update_transform_origin()
                self._notify_changed()
                event.accept()
                return

        if event.button() == Qt.MouseButton.LeftButton:
            # Check text box handles first (before node editing)
            tb_h = self._hit_test_text_box_handle(event.scenePos())
            if tb_h:
                self._begin_resize_tracking()
                self._drag_text_box = tb_h
                event.accept()
                return

            if self._node_editing:
                hit = self._hit_test_node(event.scenePos())
                if hit is not None:
                    idx, htype = hit
                    self._begin_resize_tracking()
                    self._active_node = idx
                    self._active_handle_type = htype
                    self._node_dragging = True
                    self._press_scene = event.scenePos()
                    event.accept()
                    return

            # Bounding-box handle resize (or adjust1)
            h = self._hit_test_handle(event.scenePos())
            if h == "rotate":
                self._begin_rotation()
                event.accept()
                return
            if h:
                self._begin_resize_tracking()
                self._active_handle = h
                if h == "adjust1":
                    self._start_adjust1 = self._adjust1
                self._resizing = True
                self._store_resize_anchor(h)
                self._press_scene = event.scenePos()
                self._start_pos = QPointF(self.pos())
                self._start_size = (self._width, self._height)
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # Text box handle drag
        if self._drag_text_box:
            local_pt = self.mapFromScene(event.scenePos())
            self._resize_text_box(self._drag_text_box, local_pt)
            self._notify_changed()
            event.accept()
            return

        # Adjust1 (bend radius) handle drag
        if self._rotating:
            self._handle_rotation_move(event)
            return
        if self._resizing and self._active_handle == "adjust1":
            corner_idx = self._find_first_hv_corner()
            if corner_idx is not None:
                cur = event.scenePos()
                p = self.pos()
                w, h = self._width, self._height
                corner_x, corner_y = self._get_node_anchor(corner_idx - 1)
                # Distance from cursor to corner point in pixels
                dx = cur.x() - (p.x() + corner_x * w)
                dy = cur.y() - (p.y() + corner_y * h)
                dist = math.sqrt(dx * dx + dy * dy)
                new_r = max(0.0, min(200.0, dist))
                self._adjust1 = new_r
                self.prepareGeometryChange()
                self._update_path()
                self._update_label_position()
                self._update_transform_origin()
                if MetaCurveItem.on_adjust1_changed:
                    MetaCurveItem.on_adjust1_changed(self, new_r)
                self._notify_changed()
            event.accept()
            return

        # Node dragging
        if self._node_dragging and self._active_node is not None:
            # Map scene position to local coordinates (rotation-aware)
            local_pt = self.mapFromScene(event.scenePos())
            rx = local_pt.x() / self._width if self._width > 0 else 0.5
            ry = local_pt.y() / self._height if self._height > 0 else 0.5

            node = self._nodes[self._active_node]
            htype = self._active_handle_type

            if htype == "anchor":
                cmd = node.get("cmd", "L")
                if cmd == "H":
                    node["x"] = rx
                elif cmd == "V":
                    node["y"] = ry
                else:
                    node["x"] = rx
                    node["y"] = ry
                # Orthocurve: keep final edge orthogonal
                idx = self._active_node
                if isinstance(self, MetaOrthoCurveItem):
                    # Last L endpoint dragged: adjust previous H/V
                    if cmd == "L" and idx > 0:
                        prev = self._nodes[idx - 1]
                        prev_cmd = prev.get("cmd")
                        if prev_cmd == "H":
                            prev["x"] = rx
                        elif prev_cmd == "V":
                            prev["y"] = ry
                    # H/V node dragged: propagate to next L endpoint
                    if cmd in ("H", "V") and idx + 1 < len(self._nodes):
                        nxt = self._nodes[idx + 1]
                        if nxt.get("cmd") == "L":
                            if cmd == "H":
                                nxt["x"] = rx
                            elif cmd == "V":
                                nxt["y"] = ry
            elif htype == "c1":
                node["c1x"] = rx
                node["c1y"] = ry
            elif htype == "c2":
                node["c2x"] = rx
                node["c2y"] = ry
            elif htype == "cx":
                node["cx"] = rx
                node["cy"] = ry

            self.prepareGeometryChange()
            self._update_path()
            self._update_label_position()
            self._update_transform_origin()

            # Port proximity detection for endpoint anchors
            if htype == "anchor" and self._is_endpoint_index(self._active_node):
                scene_pt = self._node_scene_pos(self._active_node)
                port = _find_nearby_port(self.scene(), scene_pt)
                if port is not self._snap_port:
                    if self._snap_port:
                        self._snap_port.set_snap_hover(False)
                    self._snap_port = port
                    if port:
                        port.set_snap_hover(True)

            self._notify_changed()
            event.accept()
            return

        # Bounding-box handle resize
        if self._resizing and self._active_handle and self._press_scene and self._start_pos and self._start_size:
            cur = event.scenePos()
            dx, dy = self._scene_delta_to_local(
                cur.x() - self._press_scene.x(),
                cur.y() - self._press_scene.y())

            w0, h0 = self._start_size
            new_w, new_h, anchor_after = self._compute_resize(
                self._active_handle, dx, dy, w0, h0)
            self._width = new_w
            self._height = new_h
            self._update_path()
            self._update_label_position()
            self._update_transform_origin()
            self._fixup_resize_pos(anchor_after)
            self._notify_changed()
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._drag_text_box:
            self._end_resize_tracking()
            self._drag_text_box = None
            self._notify_changed()
            event.accept()
            return
        if self._rotating:
            self._end_rotation()
            self._reattach_port_endpoints()
            event.accept()
            return
        if self._node_dragging:
            # Snap endpoint to port if hovering
            if (self._snap_port and self._active_node is not None
                    and self._is_endpoint_index(self._active_node)):
                port = self._snap_port
                port.set_snap_hover(False)
                port_pos = port.mapToScene(QPointF(0, 0))
                w = self._width if self._width > 0 else 1.0
                h = self._height if self._height > 0 else 1.0
                rx = (port_pos.x() - self.pos().x()) / w
                ry = (port_pos.y() - self.pos().y()) / h
                idx = self._active_node
                node = self._nodes[idx]
                cmd = node.get("cmd", "L")
                if cmd == "H":
                    node["x"] = rx
                elif cmd == "V":
                    node["y"] = ry
                else:
                    node["x"] = rx
                    node["y"] = ry
                # For orthocurves, adjust the second-to-last node (end only).
                # The start (M node) moves freely; the first H/V after M is unchanged.
                if isinstance(self, MetaOrthoCurveItem) and idx != 0 and idx >= 1:
                    adj = self._nodes[idx - 1]
                    adj_cmd = adj.get("cmd", "L")
                    if cmd == "H" and adj_cmd in ("V", "M", "L"):
                        adj["y"] = ry
                    elif cmd == "V" and adj_cmd in ("H", "M", "L"):
                        adj["x"] = rx
                    elif cmd in ("M", "L"):
                        if adj_cmd == "H":
                            adj["x"] = rx
                        elif adj_cmd == "V":
                            adj["y"] = ry
                self.prepareGeometryChange()
                self._update_path()
                self._update_label_position()
                self._update_transform_origin()
                # Add bidirectional connection
                if self.ann_id not in port._connections:
                    port.add_connection(self.ann_id)
                if port.ann_id not in self._port_ids:
                    self._port_ids.append(port.ann_id)
                which = "start" if idx == 0 else "end"
                self._port_endpoints[port.ann_id] = which
                port._notify_changed()
                self._snap_port = None
            else:
                if self._snap_port:
                    self._snap_port.set_snap_hover(False)
                    self._snap_port = None
                # Disconnect from any port previously at this endpoint
                if (self._active_node is not None
                        and self._is_endpoint_index(self._active_node)):
                    which = "start" if self._active_node == 0 else "end"
                    self._disconnect_end(which)
            self._end_resize_tracking()
            self._node_dragging = False
            self._active_node = None
            self._active_handle_type = None
            self._recalculate_bbox()
            self._notify_changed()
            event.accept()
            return
        if self._resizing:
            self._end_resize_tracking()
            self._resizing = False
            self._active_handle = None
            self._press_scene = None
            self._start_pos = None
            self._start_size = None
            self._notify_changed()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    # ---- Node context menu ----

    def _show_node_context_menu(self, screen_pos, node_idx: int):
        """Show context menu for changing node type."""
        from PyQt6.QtWidgets import QMenu
        menu = QMenu()
        node = self._nodes[node_idx]
        current_cmd = node.get("cmd", "L")

        if node_idx == 0:
            # First node is always M
            act = menu.addAction("Move To (M)")
            act.setCheckable(True)
            act.setChecked(True)
            act.setEnabled(False)
        else:
            cmds = [
                ("Line To (L)", "L"),
                ("Horizontal (H)", "H"),
                ("Vertical (V)", "V"),
                ("Cubic Bezier (C)", "C"),
                ("Smooth Cubic (S)", "S"),
                ("Quadratic (Q)", "Q"),
                ("Smooth Quad (T)", "T"),
                ("Arc (A)", "A"),
            ]
            for label, cmd in cmds:
                act = menu.addAction(label)
                act.setCheckable(True)
                act.setChecked(current_cmd == cmd)
                act.triggered.connect(lambda checked, c=cmd: self._change_node_type(node_idx, c))

            # Close path option for last node
            if node_idx == len(self._nodes) - 1:
                menu.addSeparator()
                z_act = menu.addAction("Close Path (Z)")
                z_act.setCheckable(True)
                has_z = any(n.get("cmd") == "Z" for n in self._nodes)
                z_act.setChecked(has_z)
                z_act.triggered.connect(lambda checked: self._toggle_close_path())

        menu.addSeparator()

        # Delete node
        if len(self._nodes) > 2:
            del_act = menu.addAction("Delete Node")
            del_act.triggered.connect(lambda: self._delete_node(node_idx))

        # Insert node after
        ins_act = menu.addAction("Insert Node After")
        ins_act.triggered.connect(lambda: self._insert_node_after(node_idx))

        menu.exec(screen_pos)

    def _change_node_type(self, idx: int, new_cmd: str):
        """Change a node's command type, auto-generating control points."""
        node = self._nodes[idx]
        old_cmd = node.get("cmd", "L")
        if old_cmd == new_cmd:
            return

        ax, ay = self._get_node_anchor(idx)
        px, py = self._get_node_anchor(idx - 1) if idx > 0 else (ax, ay)

        # Remove old control point keys
        for key in ("c1x", "c1y", "c2x", "c2y", "cx", "cy", "rx", "ry", "rotation", "large_arc", "sweep"):
            node.pop(key, None)

        node["cmd"] = new_cmd

        # Ensure x, y are set for commands that need them
        if new_cmd not in ("Z",):
            if "x" not in node:
                node["x"] = ax
            if "y" not in node:
                node["y"] = ay

        # Auto-generate control points
        if new_cmd == "C":
            node["c1x"] = px + (ax - px) / 3
            node["c1y"] = py + (ay - py) / 3
            node["c2x"] = px + 2 * (ax - px) / 3
            node["c2y"] = py + 2 * (ay - py) / 3
        elif new_cmd == "S":
            node["c2x"] = px + 2 * (ax - px) / 3
            node["c2y"] = py + 2 * (ay - py) / 3
        elif new_cmd == "Q":
            node["cx"] = (px + ax) / 2
            node["cy"] = (py + ay) / 2
        elif new_cmd == "A":
            chord = math.sqrt((ax - px) ** 2 + (ay - py) ** 2)
            r = max(chord / 2, 0.05)
            node["rx"] = r
            node["ry"] = r
            node["rotation"] = 0
            node["large_arc"] = 0
            node["sweep"] = 1
        elif new_cmd == "H":
            node.pop("y", None)
        elif new_cmd == "V":
            node.pop("x", None)

        self.prepareGeometryChange()
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()
        self._notify_changed()

    def _toggle_close_path(self):
        """Toggle Z (close path) at end of nodes."""
        if self._nodes and self._nodes[-1].get("cmd") == "Z":
            self._nodes.pop()
        else:
            self._nodes.append({"cmd": "Z"})
        self.prepareGeometryChange()
        self._update_path()
        self._notify_changed()

    def _delete_node(self, idx: int):
        """Delete a node (minimum 2 nodes)."""
        if len(self._nodes) <= 2:
            return
        self.prepareGeometryChange()
        del self._nodes[idx]
        # Ensure first node is M
        if self._nodes and self._nodes[0].get("cmd") != "M":
            self._nodes[0]["cmd"] = "M"
        self._recalculate_bbox()
        self._notify_changed()

    def _insert_node_after(self, idx: int):
        """Insert a new L node after the given index, at midpoint to next anchor."""
        ax, ay = self._get_node_anchor(idx)
        if idx + 1 < len(self._nodes):
            nx, ny = self._get_node_anchor(idx + 1)
        else:
            nx, ny = ax + 0.1, ay
        mx, my = (ax + nx) / 2, (ay + ny) / 2
        self.prepareGeometryChange()
        self._nodes.insert(idx + 1, {"cmd": "L", "x": mx, "y": my})
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()
        self._notify_changed()

    # ---- Text box handles (same pattern as MetaLineItem) ----

    def _text_box_handle_points(self) -> Dict[str, QPointF]:
        """Return text box corner handle positions for resizing."""
        if self._text_box_rect is None:
            return {}
        r = self._text_box_rect
        return {
            "tb_tl": QPointF(r.left(), r.top()),
            "tb_tr": QPointF(r.right(), r.top()),
            "tb_bl": QPointF(r.left(), r.bottom()),
            "tb_br": QPointF(r.right(), r.bottom()),
        }

    def _draw_text_box_handles(self, painter: QPainter):
        """Draw handles for resizing the text bounding box."""
        handles = self._text_box_handle_points()
        if not handles:
            return
        handle_pen = QPen(QColor(255, 140, 0), 1)
        handle_brush = QBrush(QColor(255, 200, 100))
        painter.setPen(handle_pen)
        painter.setBrush(handle_brush)
        handle_size = _get_handle_size()
        half = handle_size / 2
        for pos in handles.values():
            painter.drawRect(QRectF(pos.x() - half, pos.y() - half, handle_size, handle_size))

    def _hit_test_text_box_handle(self, scene_pt: QPointF) -> Optional[str]:
        """Test if scene point hits a text box resize handle."""
        if not self._should_paint_handles():
            return None
        if self._text_box_rect is None:
            return None
        handles = self._text_box_handle_points()
        local_pt = self.mapFromScene(scene_pt)
        hit_dist = _get_hit_distance()
        for name, pos in handles.items():
            if QLineF(local_pt, pos).length() <= hit_dist:
                return name
        return None

    def _resize_text_box(self, handle: str, local_pt: QPointF):
        """Resize the text box based on handle being dragged."""
        if self._text_box_rect is None:
            return
        r = self._text_box_rect
        min_size = 30.0
        if handle == "tb_tl":
            new_left = min(local_pt.x(), r.right() - min_size)
            new_top = min(local_pt.y(), r.bottom() - min_size)
            new_width = r.right() - new_left
            new_height = r.bottom() - new_top
        elif handle == "tb_tr":
            new_left = r.left()
            new_top = min(local_pt.y(), r.bottom() - min_size)
            new_width = max(local_pt.x() - r.left(), min_size)
            new_height = r.bottom() - new_top
        elif handle == "tb_bl":
            new_left = min(local_pt.x(), r.right() - min_size)
            new_top = r.top()
            new_width = r.right() - new_left
            new_height = max(local_pt.y() - r.top(), min_size)
        elif handle == "tb_br":
            new_left = r.left()
            new_top = r.top()
            new_width = max(local_pt.x() - r.left(), min_size)
            new_height = max(local_pt.y() - r.top(), min_size)
        else:
            return
        self.meta.text_box_width = round1(new_width)
        self.meta.text_box_height = round1(new_height)
        self.prepareGeometryChange()
        self._update_label_position()
        self.update()

    # ---- Shape / bounds / paint ----

    def shape(self) -> QPainterPath:
        """Return shape for hit-testing with fat stroke."""
        stroker = QPainterPath()
        from PyQt6.QtGui import QPainterPathStroker
        s = QPainterPathStroker()
        s.setWidth(max(20, self.pen_width + 10))
        stroker = s.createStroke(self.path())
        if self._text_box_rect is not None:
            stroker.addRect(self._text_box_rect)
        if self._should_paint_handles() and not self._node_editing:
            all_handles = self._handle_points_local()
            all_handles.update(self._text_box_handle_points())
            return shape_with_handles(stroker, all_handles)
        if self._should_paint_handles() and self._node_editing:
            hit_r = _get_handle_size() / 2 + 1
            for pt, _, _ in self._node_points_scene():
                local_pt = self.mapFromScene(pt)
                stroker.addEllipse(local_pt, hit_r, hit_r)
        return stroker

    def boundingRect(self) -> QRectF:
        r = super().boundingRect()
        margin = _get_handle_size() / 2 + 1 + self.pen_width
        r = r.adjusted(-margin, -margin, margin, margin)
        if self._text_box_rect is not None:
            r = r.united(self._text_box_rect.adjusted(-margin, -margin, margin, margin))
        return r

    def paint(self, painter: QPainter, option, widget=None):
        my_option = QStyleOptionGraphicsItem(option)
        my_option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, my_option, widget)

        # Draw arrowheads
        if self.arrow_mode != self.ARROW_NONE:
            arrow_min_mult = _CachedCanvasSettings.get().arrow_min_multiplier
            effective_arrow_size = max(self.arrow_size, self.pen_width * arrow_min_mult)
            painter.setPen(QPen(self.pen_color, self.pen_width))
            painter.setBrush(QBrush(self.pen_color))

            path = self.path()
            if path.elementCount() >= 2:
                if self.arrow_mode in (self.ARROW_END, self.ARROW_BOTH):
                    # Arrow at end: last two distinct points
                    from_pt, to_pt = self._get_path_end_segment(path, from_end=True)
                    if from_pt is not None and to_pt is not None:
                        self._draw_arrowhead(painter, from_pt, to_pt, effective_arrow_size)

                if self.arrow_mode in (self.ARROW_START, self.ARROW_BOTH):
                    # Arrow at start: first two distinct points
                    from_pt, to_pt = self._get_path_end_segment(path, from_end=False)
                    if from_pt is not None and to_pt is not None:
                        self._draw_arrowhead(painter, from_pt, to_pt, effective_arrow_size)

        # Draw text box when present
        if self._text_box_rect is not None:
            bg_hex = getattr(self.meta, "text_box_background_color", "")
            if bg_hex:
                from utils import hex_to_qcolor
                bg_c = hex_to_qcolor(bg_hex, self.brush_color)
            else:
                bg_c = QColor(self.brush_color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(bg_c))
            painter.drawRect(self._text_box_rect)

            if self._should_paint_handles():
                border_hex = getattr(self.meta, "text_box_border_color", "")
                if border_hex:
                    from utils import hex_to_qcolor as _h2q
                    border_c = _h2q(border_hex, QColor(200, 200, 200))
                else:
                    border_c = QColor(200, 200, 200)
                box_pen = QPen(border_c, 1, Qt.PenStyle.SolidLine)
                painter.setPen(box_pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRect(self._text_box_rect)

        if not self._should_paint_handles():
            return

        # Draw anchor dot
        t = getattr(self.meta, "anchor_value", 50.0) / 100.0
        pt = self._point_at_t(t)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(160, 160, 160)))
        painter.drawEllipse(pt, 5, 5)

        # Draw text box handles
        if self._text_box_rect is not None:
            self._draw_text_box_handles(painter)

        if self._node_editing:
            self._paint_node_handles(painter)
        else:
            # Selection outline and bbox handles
            sel_pen = QPen(_get_selection_color(), 1, Qt.PenStyle.DashLine)
            painter.setPen(sel_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(self.path())

            # Draw resize handles (excluding adjust1)
            handles = self._handle_points_local()
            adjust1_handle_pos = handles.pop("adjust1", None)
            # Remove any subclass-added handles that aren't bbox handles
            for k in list(handles):
                if k.startswith("ortho_"):
                    handles.pop(k)
            draw_handles(painter, handles)
            self._draw_rotation_knob(painter)

            # Draw adjust1 handle in yellow
            if adjust1_handle_pos is not None:
                handle_size = _get_handle_size()
                half = handle_size / 2
                painter.setPen(QPen(QColor(204, 153, 0), 1))  # Dark yellow border
                painter.setBrush(QBrush(QColor(255, 215, 0)))  # Gold/yellow fill
                painter.drawEllipse(QRectF(adjust1_handle_pos.x() - half, adjust1_handle_pos.y() - half,
                                           handle_size, handle_size))

    def _paint_node_handles(self, painter: QPainter):
        """Paint node editing handles: green circles for anchors, blue diamonds for controls."""
        handle_size = _get_handle_size()
        half = handle_size / 2
        w, h = self._width, self._height

        for i, node in enumerate(self._nodes):
            cmd = node.get("cmd", "L")
            if cmd == "Z":
                continue

            ax, ay = self._get_node_anchor(i)
            anchor_local = QPointF(ax * w, ay * h)

            # Draw control point lines and handles first
            if cmd == "C":
                c1 = QPointF(node.get("c1x", ax) * w, node.get("c1y", ay) * h)
                c2 = QPointF(node.get("c2x", ax) * w, node.get("c2y", ay) * h)
                # Dashed lines from controls to anchor
                ctrl_pen = QPen(QColor(150, 150, 150), 1, Qt.PenStyle.DashLine)
                painter.setPen(ctrl_pen)
                if i > 0:
                    pax, pay = self._get_node_anchor(i - 1)
                    painter.drawLine(QPointF(pax * w, pay * h), c1)
                painter.drawLine(c2, anchor_local)
                # Blue diamond for c1
                self._draw_diamond(painter, c1, half, i, "c1")
                # Blue diamond for c2
                self._draw_diamond(painter, c2, half, i, "c2")
            elif cmd == "S":
                c2 = QPointF(node.get("c2x", ax) * w, node.get("c2y", ay) * h)
                ctrl_pen = QPen(QColor(150, 150, 150), 1, Qt.PenStyle.DashLine)
                painter.setPen(ctrl_pen)
                painter.drawLine(c2, anchor_local)
                self._draw_diamond(painter, c2, half, i, "c2")
            elif cmd == "Q":
                cp = QPointF(node.get("cx", ax) * w, node.get("cy", ay) * h)
                ctrl_pen = QPen(QColor(150, 150, 150), 1, Qt.PenStyle.DashLine)
                painter.setPen(ctrl_pen)
                if i > 0:
                    pax, pay = self._get_node_anchor(i - 1)
                    painter.drawLine(QPointF(pax * w, pay * h), cp)
                painter.drawLine(cp, anchor_local)
                self._draw_diamond(painter, cp, half, i, "cx")

            # Draw anchor circle
            is_active = (i == self._active_node and self._active_handle_type == "anchor")
            if is_active:
                painter.setPen(QPen(QColor(204, 102, 0), 1))
                painter.setBrush(QBrush(QColor(255, 165, 0)))
            else:
                painter.setPen(QPen(QColor(0, 128, 0), 1))
                painter.setBrush(QBrush(QColor(0, 200, 0)))
            painter.drawEllipse(QRectF(anchor_local.x() - half, anchor_local.y() - half,
                                       handle_size, handle_size))

    def _draw_diamond(self, painter: QPainter, center: QPointF, half: float,
                      node_idx: int, handle_type: str):
        """Draw a diamond-shaped control point handle."""
        is_active = (node_idx == self._active_node and self._active_handle_type == handle_type)
        if is_active:
            painter.setPen(QPen(QColor(204, 102, 0), 1))
            painter.setBrush(QBrush(QColor(255, 165, 0)))
        else:
            painter.setPen(QPen(QColor(0, 70, 180), 1))
            painter.setBrush(QBrush(QColor(80, 140, 255)))
        diamond = QPolygonF([
            QPointF(center.x(), center.y() - half),
            QPointF(center.x() + half, center.y()),
            QPointF(center.x(), center.y() + half),
            QPointF(center.x() - half, center.y()),
        ])
        painter.drawPolygon(diamond)

    def _draw_arrowhead(self, painter: QPainter, from_pt: QPointF, to_pt: QPointF, size: float):
        """Draw a filled arrowhead triangle."""
        dx = to_pt.x() - from_pt.x()
        dy = to_pt.y() - from_pt.y()
        length = math.sqrt(dx * dx + dy * dy)
        if length < 1e-6:
            return
        ux, uy = dx / length, dy / length
        px, py = -uy, ux
        tip = to_pt
        left = QPointF(to_pt.x() - ux * size + px * size * 0.4,
                       to_pt.y() - uy * size + py * size * 0.4)
        right = QPointF(to_pt.x() - ux * size - px * size * 0.4,
                        to_pt.y() - uy * size - py * size * 0.4)
        arrow = QPolygonF([tip, left, right])
        painter.drawPolygon(arrow)

    @staticmethod
    def _get_path_end_segment(path: QPainterPath, from_end: bool):
        """Get the last (or first) two distinct points of a QPainterPath for arrowhead direction."""
        n = path.elementCount()
        if n < 2:
            return None, None

        if from_end:
            to_pt = QPointF(path.elementAt(n - 1).x, path.elementAt(n - 1).y)
            for i in range(n - 2, -1, -1):
                e = path.elementAt(i)
                pt = QPointF(e.x, e.y)
                if QLineF(pt, to_pt).length() > 1e-3:
                    return pt, to_pt
            return None, None
        else:
            to_pt = QPointF(path.elementAt(0).x, path.elementAt(0).y)
            for i in range(1, n):
                e = path.elementAt(i)
                pt = QPointF(e.x, e.y)
                if QLineF(pt, to_pt).length() > 1e-3:
                    return pt, to_pt
            return None, None

    def itemChange(self, change, value):
        out = super().itemChange(change, value)
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if not self._resizing and not self._node_dragging:
                self._notify_changed()
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            if not value:
                self._node_editing = False
            self.prepareGeometryChange()
        return out

    def to_record(self) -> Dict[str, Any]:
        """Serialize curve to JSON record."""
        p = self.pos()
        # Build clean node list with rounded values
        clean_nodes = []
        for node in self._nodes:
            clean = {"cmd": node["cmd"]}
            for key in ("x", "y", "c1x", "c1y", "c2x", "c2y", "cx", "cy"):
                if key in node:
                    clean[key] = round(node[key], 4)
            for key in ("rx", "ry", "rotation"):
                if key in node:
                    clean[key] = round(node[key], 4)
            for key in ("large_arc", "sweep"):
                if key in node:
                    clean[key] = int(node[key])
            clean_nodes.append(clean)

        style = self._style_dict()["style"]
        style["arrow"] = self.arrow_mode
        style["arrow_size"] = round(self.arrow_size, 1)

        geom = {
            "x": round1(p.x()),
            "y": round1(p.y()),
            "w": round1(self._width),
            "h": round1(self._height),
            "nodes": clean_nodes,
        }
        if self._adjust1 > 0:
            geom["adjust1"] = round(self._adjust1, 1)

        rec = {
            "id": self.ann_id,
            "kind": "curve",
            "geom": geom,
            **self._meta_dict(self.meta),
            "style": style,
        }
        # Include connected port IDs (read-only)
        if self._port_ids:
            rec["ports"] = list(self._port_ids)
        z = self.zValue()
        if z != 0:
            rec["z"] = int(z)
        self._add_angle_to_geom(rec.get("geom", {}))
        return rec

    def _reattach_port_endpoints(self):
        """Recalculate connected endpoint positions after rotation.

        After rotation, local-to-scene mapping changes.  For each connected
        port, convert the port's scene position into the curve's (now rotated)
        local coordinate system and update the endpoint node so the curve
        still visually touches the port.
        """
        if not self._port_endpoints:
            return
        scene = self.scene()
        if not scene:
            return
        w = self._width if self._width > 0 else 1.0
        h = self._height if self._height > 0 else 1.0
        first_idx = 0
        last_idx = self._last_anchor_index()

        for port_id, which in self._port_endpoints.items():
            # Find the port in the scene
            port = None
            for si in scene.items():
                if isinstance(si, MetaPortItem) and si.ann_id == port_id:
                    port = si
                    break
            if port is None:
                continue

            port_scene = port.mapToScene(QPointF(0, 0))
            local = self.mapFromScene(port_scene)
            rx = local.x() / w
            ry = local.y() / h

            idx = first_idx if which == "start" else last_idx
            node = self._nodes[idx]
            cmd = node.get("cmd", "L")
            if cmd == "H":
                node["x"] = rx
            elif cmd == "V":
                node["y"] = ry
            else:
                node["x"] = rx
                node["y"] = ry

            # Orthocurve: also adjust adjacent node for end
            if (isinstance(self, MetaOrthoCurveItem)
                    and which == "end" and idx >= 1):
                adj = self._nodes[idx - 1]
                adj_cmd = adj.get("cmd")
                if adj_cmd == "H":
                    adj["x"] = rx
                elif adj_cmd == "V":
                    adj["y"] = ry

        self.prepareGeometryChange()
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()
        self._notify_changed()

    def _disconnect_end(self, which: str):
        """Remove port connection for the given endpoint ('start' or 'end')."""
        to_remove = [pid for pid, end in self._port_endpoints.items()
                     if end == which]
        if not to_remove:
            return
        scene = self.scene()
        for pid in to_remove:
            del self._port_endpoints[pid]
            if pid in self._port_ids:
                self._port_ids.remove(pid)
            if scene:
                for si in scene.items():
                    if (isinstance(si, MetaPortItem)
                            and si.ann_id == pid):
                        si.remove_connection(self.ann_id)
                        si._notify_changed()
                        break


class MetaOrthoCurveItem(MetaCurveItem):
    """Orthogonal curve restricted to M/H/V nodes with green handles and Ctrl+click extend.

    Inherits core curve infrastructure (path rendering, node editing, arrowheads,
    bbox resize, adjust1/bend-radius handle) from MetaCurveItem.  Adds ortho-specific
    features: green control handles at each H/V node, Ctrl+click endpoint extension,
    and linked H/V node dragging.
    """

    KIND = "orthocurve"
    KIND_ALIASES = frozenset(k for k, v in KIND_ALIAS_MAP.items() if v == "orthocurve")

    def __init__(self, x: float, y: float, w: float, h: float,
                 nodes: list, ann_id: str, on_change=None):
        super().__init__(x, y, w, h, nodes, ann_id, on_change)
        self.kind = "orthocurve"
        self._ortho_drag_idx: Optional[int] = None

    # ---- Ortho-specific helpers ----

    def _has_hv_nodes(self) -> bool:
        """Return True if this curve has any H or V command nodes."""
        return any(n.get("cmd") in ("H", "V") for n in self._nodes)

    def _last_path_index(self) -> int:
        """Return index of last non-Z node."""
        idx = len(self._nodes) - 1
        while idx > 0 and self._nodes[idx].get("cmd") == "Z":
            idx -= 1
        return idx

    def _try_extend_ortho(self, scene_pt: QPointF) -> bool:
        """Try to extend ortho curve at start or end via Ctrl+click.

        Returns True if the curve was extended.
        """
        if not self._has_hv_nodes():
            return False
        hit_dist = _get_hit_distance()
        p = self.pos()
        w, h = self._width, self._height

        first_ax, first_ay = self._get_node_anchor(0)
        first_scene = QPointF(p.x() + first_ax * w, p.y() + first_ay * h)

        last_idx = self._last_path_index()
        last_ax, last_ay = self._get_node_anchor(last_idx)
        last_scene = QPointF(p.x() + last_ax * w, p.y() + last_ay * h)

        near_end = QLineF(scene_pt, last_scene).length() <= hit_dist
        near_start = QLineF(scene_pt, first_scene).length() <= hit_dist

        if near_end:
            self._extend_ortho_end(scene_pt)
            return True
        if near_start:
            self._extend_ortho_start(scene_pt)
            return True
        return False

    def _extend_ortho_end(self, scene_pt: QPointF):
        """Append an orthogonal segment at the end of the curve.

        The previous last node (L endpoint) is converted to H/V, and the
        new endpoint becomes an L node so it can be freely dragged.
        """
        self._begin_resize_tracking()
        p = self.pos()
        rx = (scene_pt.x() - p.x()) / self._width if self._width > 0 else 0.5
        ry = (scene_pt.y() - p.y()) / self._height if self._height > 0 else 0.5

        last_idx = self._last_path_index()
        last_node = self._nodes[last_idx]
        last_cmd = last_node.get("cmd", "L")
        last_ax, last_ay = self._get_node_anchor(last_idx)

        # Determine direction for the new segment
        if last_cmd == "H":
            direction = "V"
        elif last_cmd == "V":
            direction = "H"
        elif last_cmd == "L":
            # Convert old L endpoint to H or V based on predecessor
            prev_cmd = self._nodes[last_idx - 1].get("cmd", "M") if last_idx > 0 else "M"
            if prev_cmd in ("H", "M", "L"):
                # Previous was horizontal-ish → old endpoint becomes V
                last_node["cmd"] = "V"
                last_node["y"] = last_ay
                last_node.pop("x", None)
                direction = "H"
            else:
                # Previous was V → old endpoint becomes H
                last_node["cmd"] = "H"
                last_node["x"] = last_ax
                last_node.pop("y", None)
                direction = "V"
        else:
            if abs(rx - last_ax) >= abs(ry - last_ay):
                direction = "H"
            else:
                direction = "V"

        # New endpoint is always L (freely draggable)
        new_node = {"cmd": "L", "x": rx, "y": ry}
        self._nodes.insert(last_idx + 1, new_node)
        self._recalculate_bbox()
        self._notify_changed()
        self._end_resize_tracking()

    def _extend_ortho_start(self, scene_pt: QPointF):
        """Prepend a new start point, converting old M to an orthogonal node."""
        self._begin_resize_tracking()
        p = self.pos()
        rx = (scene_pt.x() - p.x()) / self._width if self._width > 0 else 0.5
        ry = (scene_pt.y() - p.y()) / self._height if self._height > 0 else 0.5

        old_m = self._nodes[0]
        old_mx = old_m.get("x", 0.0)
        old_my = old_m.get("y", 0.0)

        if len(self._nodes) > 1:
            next_cmd = self._nodes[1].get("cmd", "L")
            if next_cmd == "H":
                old_m["cmd"] = "V"
                old_m["y"] = old_my
                old_m.pop("x", None)
            elif next_cmd == "V":
                old_m["cmd"] = "H"
                old_m["x"] = old_mx
                old_m.pop("y", None)
            else:
                old_m["cmd"] = "L"
        else:
            old_m["cmd"] = "L"

        self._nodes.insert(0, {"cmd": "M", "x": rx, "y": ry})
        self._recalculate_bbox()
        self._notify_changed()
        self._end_resize_tracking()

    # ---- Ortho control handle positions ----

    def _ortho_handle_points_local(self) -> Dict[str, QPointF]:
        """Return local positions of ortho control handles at each H/V node.

        The last L endpoint is only editable in node-editing mode (double-click),
        matching the M start point behaviour — both show as yellow handles.
        """
        handles: Dict[str, QPointF] = {}
        w, h = self._width, self._height
        for i in range(1, len(self._nodes)):
            cmd = self._nodes[i].get("cmd", "L")
            if cmd in ("H", "V"):
                ax, ay = self._get_node_anchor(i)
                handles[f"ortho_{i}"] = QPointF(ax * w, ay * h)
        return handles

    # ---- Ortho node insertion ----

    def _flip_subsequent_hv(self, start_idx: int):
        """Flip H<->V commands for all nodes from start_idx onwards."""
        for i in range(start_idx, len(self._nodes)):
            node = self._nodes[i]
            cmd = node.get("cmd")
            if cmd == "H":
                val = node.pop("x", 0)
                node["cmd"] = "V"
                node["y"] = val
            elif cmd == "V":
                val = node.pop("y", 0)
                node["cmd"] = "H"
                node["x"] = val

    def _insert_node_after(self, idx: int):
        """Insert an ortho node after idx with opposite cmd, then flip subsequent."""
        node = self._nodes[idx]
        cmd = node.get("cmd", "L")
        ax, ay = self._get_node_anchor(idx)
        if idx + 1 < len(self._nodes):
            nx, ny = self._get_node_anchor(idx + 1)
        else:
            nx, ny = ax + 0.1, ay

        if cmd == "V":
            new_node = {"cmd": "H", "x": (ax + nx) / 2}
        elif cmd in ("H", "M"):
            new_node = {"cmd": "V", "y": (ay + ny) / 2}
        else:
            new_node = {"cmd": "L", "x": (ax + nx) / 2, "y": (ay + ny) / 2}

        self.prepareGeometryChange()
        self._nodes.insert(idx + 1, new_node)
        self._flip_subsequent_hv(idx + 2)
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()
        self._notify_changed()

    def _insert_ortho_node_on_edge(self, edge_idx: int, scene_pt: QPointF):
        """Insert an ortho node on edge at click position, then flip subsequent."""
        p = self.pos()
        rx = (scene_pt.x() - p.x()) / self._width if self._width > 0 else 0.5
        ry = (scene_pt.y() - p.y()) / self._height if self._height > 0 else 0.5

        prev_node = self._nodes[edge_idx]
        prev_cmd = prev_node.get("cmd", "L")

        if prev_cmd == "V":
            new_node = {"cmd": "H", "x": rx}
        elif prev_cmd in ("H", "M"):
            new_node = {"cmd": "V", "y": ry}
        else:
            new_node = {"cmd": "L", "x": rx, "y": ry}

        self.prepareGeometryChange()
        self._nodes.insert(edge_idx + 1, new_node)
        self._flip_subsequent_hv(edge_idx + 2)

        # Keep L endpoint orthogonal to its new predecessor
        last_idx = self._last_path_index()
        last_node = self._nodes[last_idx]
        if last_node.get("cmd") == "L" and last_idx > 0:
            before_last = self._nodes[last_idx - 1]
            bl_cmd = before_last.get("cmd")
            if bl_cmd == "H":
                last_node["x"] = before_last.get("x", last_node.get("x", 0))
            elif bl_cmd == "V":
                last_node["y"] = before_last.get("y", last_node.get("y", 0))

        self._update_path()
        self._update_label_position()
        self._update_transform_origin()
        self._notify_changed()

    # ---- Handle overrides ----

    def _handle_points_local(self) -> Dict[str, QPointF]:
        handles = super()._handle_points_local()
        handles.update(self._ortho_handle_points_local())
        return handles

    # ---- Mouse interaction overrides ----

    def hoverMoveEvent(self, event):
        if not self._node_editing:
            h = self._hit_test_handle(event.scenePos())
            if h and h.startswith("ortho_"):
                self.setCursor(Qt.CursorShape.SizeAllCursor)
                QGraphicsPathItem.hoverMoveEvent(self, event)
                return
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        # Right-click on edge in node editing: insert ortho node + flip subsequent
        if event.button() == Qt.MouseButton.RightButton and self._node_editing:
            scene_pt = event.scenePos()
            hit = self._hit_test_node(scene_pt)
            if hit is None:
                edge_idx = self._hit_test_edge(scene_pt)
                if edge_idx is not None:
                    self._insert_ortho_node_on_edge(edge_idx, scene_pt)
                    event.accept()
                    return
        if event.button() == Qt.MouseButton.LeftButton:
            # Ctrl+click near start/end to extend ortho curve
            if (event.modifiers() & Qt.KeyboardModifier.ControlModifier
                    and not self._node_editing):
                if self._try_extend_ortho(event.scenePos()):
                    event.accept()
                    return
        super().mousePressEvent(event)
        # If super set _active_handle to an ortho handle, record the index
        if self._active_handle and self._active_handle.startswith("ortho_"):
            self._ortho_drag_idx = int(self._active_handle.split("_", 1)[1])

    def mouseMoveEvent(self, event):
        # Ortho control handle drag (linked H/V node movement)
        if self._resizing and self._ortho_drag_idx is not None:
            cur = event.scenePos()
            p = self.pos()
            rx = (cur.x() - p.x()) / self._width if self._width > 0 else 0.5
            ry = (cur.y() - p.y()) / self._height if self._height > 0 else 0.5
            idx = self._ortho_drag_idx
            node = self._nodes[idx]
            prev = self._nodes[idx - 1]
            cmd = node.get("cmd")
            prev_cmd = prev.get("cmd")
            # Check if next node is the L endpoint
            nxt = self._nodes[idx + 1] if idx + 1 < len(self._nodes) else None
            nxt_cmd = nxt.get("cmd") if nxt else None
            if cmd == "H":
                node["x"] = rx
                if prev_cmd == "V":
                    prev["y"] = ry
                elif prev_cmd in ("M", "L"):
                    prev["y"] = ry
                # Propagate x to next L endpoint to keep final edge orthogonal
                if nxt_cmd == "L":
                    nxt["x"] = rx
            elif cmd == "V":
                node["y"] = ry
                if prev_cmd == "H":
                    prev["x"] = rx
                elif prev_cmd in ("M", "L"):
                    prev["x"] = rx
                # Propagate y to next L endpoint to keep final edge orthogonal
                if nxt_cmd == "L":
                    nxt["y"] = ry
            elif cmd == "L":
                # Last endpoint: move freely, adjust previous H/V
                node["x"] = rx
                node["y"] = ry
                if prev_cmd == "H":
                    prev["x"] = rx
                elif prev_cmd == "V":
                    prev["y"] = ry
            self.prepareGeometryChange()
            self._update_path()
            self._update_label_position()
            self._update_transform_origin()
            self._notify_changed()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._resizing and self._ortho_drag_idx is not None:
            self._end_resize_tracking()
            self._recalculate_bbox()
            self._ortho_drag_idx = None
            self._resizing = False
            self._active_handle = None
            self._press_scene = None
            self._start_pos = None
            self._start_size = None
            self._notify_changed()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    # ---- Paint override ----

    def _paint_node_handles(self, painter: QPainter):
        """Paint ortho node handles: green circle for M node, blue squares for H/V."""
        handle_size = _get_handle_size()
        half = handle_size / 2
        w, h = self._width, self._height

        for i, node in enumerate(self._nodes):
            cmd = node.get("cmd", "L")
            if cmd == "Z":
                continue
            ax, ay = self._get_node_anchor(i)
            anchor_local = QPointF(ax * w, ay * h)

            is_active = (i == self._active_node and self._active_handle_type == "anchor")
            if is_active:
                painter.setPen(QPen(QColor(204, 102, 0), 1))
                painter.setBrush(QBrush(QColor(255, 165, 0)))
            elif i == 0:
                # First node (M): green circle — free movement
                painter.setPen(QPen(QColor(0, 128, 0), 1))
                painter.setBrush(QBrush(QColor(0, 200, 0)))
            else:
                # H/V nodes: blue square — orthogonal movement
                painter.setPen(QPen(QColor(0, 70, 180), 1))
                painter.setBrush(QBrush(QColor(80, 140, 255)))

            if i == 0 or is_active:
                # Circle for first node and active node
                painter.drawEllipse(QRectF(anchor_local.x() - half, anchor_local.y() - half,
                                           handle_size, handle_size))
            else:
                # Square for H/V nodes
                painter.drawRect(QRectF(anchor_local.x() - half, anchor_local.y() - half,
                                        handle_size, handle_size))

    def paint(self, painter: QPainter, option, widget=None):
        super().paint(painter, option, widget)
        # Paint green ortho control handles on top
        if self._should_paint_handles() and not self._node_editing:
            ortho_handles = self._ortho_handle_points_local()
            if ortho_handles:
                handle_size = _get_handle_size()
                half = handle_size / 2
                painter.setPen(QPen(QColor(0, 128, 0), 1))
                painter.setBrush(QBrush(QColor(0, 200, 0)))
                for hp in ortho_handles.values():
                    painter.drawEllipse(QRectF(hp.x() - half, hp.y() - half,
                                               handle_size, handle_size))

    # ---- Serialization ----

    def to_record(self) -> Dict[str, Any]:
        """Serialize orthocurve to JSON record."""
        rec = super().to_record()
        rec["kind"] = "orthocurve"
        self._add_angle_to_geom(rec.get("geom", {}))
        return rec


class MetaIsoCubeItem(QGraphicsPathItem, MetaMixin, LinkedMixin):
    """Isometric cube with configurable depth and extrusion angle.

    adjust1: depth of isometric extrusion in pixels (0–max(w,h), default 30)
    adjust2: angle of isometric extrusion in degrees (0–360, default 135)
    """

    KIND = "isocube"
    KIND_ALIASES = frozenset(k for k, v in KIND_ALIAS_MAP.items() if v == "isocube")

    # Class-level callbacks for property changes
    on_adjust1_changed = None
    on_adjust2_changed = None

    def __init__(self, x: float, y: float, w: float, h: float, adjust1: float, adjust2: float, ann_id: str, on_change=None):
        QGraphicsPathItem.__init__(self)
        MetaMixin.__init__(self)
        LinkedMixin.__init__(self, ann_id, on_change)

        self.kind = "isocube"
        self._width = w
        self._height = h
        self._adjust1 = max(0.0, float(adjust1))     # depth px (clamped to bbox on resize)
        self._adjust2 = max(0, min(360, adjust2))     # angle degrees
        self.setPos(QPointF(x, y))
        self.setData(ANN_ID_KEY, ann_id)
        self._update_path()

        self.setAcceptHoverEvents(True)

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        self._active_handle: Optional[str] = None
        self._resizing = False
        self._press_scene: Optional[QPointF] = None
        self._start_pos: Optional[QPointF] = None
        self._start_size: Optional[Tuple[float, float]] = None
        self._start_adjust1: Optional[float] = None
        self._start_adjust2: Optional[float] = None

        self.pen_color = QColor("#000000")
        self.pen_width = 2
        self.brush_color = QColor(200, 200, 200, 200)
        self.text_color = QColor(self.pen_color)
        self.line_dash = "solid"
        cached = _CachedCanvasSettings.get()
        self.dash_pattern_length = cached.default_dash_length
        self.dash_solid_percent = cached.default_dash_solid_percent
        self._apply_pen_brush()

        self._label_item = QGraphicsTextItem(self)
        self._label_item.setAcceptHoverEvents(False)
        self._label_item.setDefaultTextColor(self.text_color)
        self._label_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self._update_label_position()

    # ----- geometry helpers ---------------------------------------------------

    def _max_depth(self) -> float:
        """Return maximum allowed depth: the larger bounding-box dimension."""
        return max(self._width, self._height)

    def _effective_depth(self) -> float:
        """Return depth clamped so the cube fits within the bounding box.

        The offset along each axis must not exceed that axis's dimension.
        """
        depth = self._adjust1
        rad = math.radians(self._adjust2)
        abs_sin = abs(math.sin(rad))
        abs_cos = abs(math.cos(rad))
        if abs_sin > 1e-9:
            depth = min(depth, self._width / abs_sin)
        if abs_cos > 1e-9:
            depth = min(depth, self._height / abs_cos)
        return max(0.0, depth)

    def _depth_offset(self) -> Tuple[float, float]:
        """Return (dx, dy) offset from front face to back face.

        adjust2 stores the outward direction of the front face
        (0° = up, CW positive).  Extrusion goes opposite.
        Uses effective depth so the cube fits within the bounding box.
        """
        depth = self._effective_depth()
        rad = math.radians(self._adjust2)
        return -depth * math.sin(rad), depth * math.cos(rad)

    def _front_rect(self) -> Tuple[float, float, float, float]:
        """Return (fx, fy, fw, fh) for the front face, inset so the whole shape fits in (w, h)."""
        dx, dy = self._depth_offset()
        adx, ady = abs(dx), abs(dy)
        fw = max(1, self._width - adx)
        fh = max(1, self._height - ady)
        # Shift front face so depth extends outward from it
        fx = adx if dx < 0 else 0
        fy = ady if dy < 0 else 0
        # Clamp so front face stays within bounding box even at extreme depth
        fx = max(0, min(fx, self._width - fw))
        fy = max(0, min(fy, self._height - fh))
        return fx, fy, fw, fh

    def _update_path(self):
        """Build the isometric cube path from current dimensions."""
        path = QPainterPath()
        # WindingFill so overlapping face polygons are all "inside" for hit-testing.
        # Default OddEvenFill treats even-overlap regions as holes → flicker on hover.
        path.setFillRule(Qt.FillRule.WindingFill)
        if self._adjust1 < 0.5:
            fx, fy, fw, fh = self._front_rect()
            path.addRect(QRectF(fx, fy, fw, fh))
        else:
            for face in self._face_polygons():
                path.addPolygon(face)
        self.setPath(path)

    def _face_polygons(self):
        """Return the 6 cube face polygons in back-to-front paint order.

        The order depends on the angle quadrant so that faces closer
        to the viewer are painted on top of faces further away.
        Front face is always last.

        Extrusion offset is (-sin θ, cos θ) × depth, so the back face
        position relative to the front determines which side faces are
        forward (closer to viewer):
          0–90°:   back is left+below  → left & bottom forward
          90–180°: back is left+above  → left & top forward
          180–270°: back is right+above → right & top forward
          270–360°: back is right+below → right & bottom forward
        """
        dx, dy = self._depth_offset()
        fx, fy, fw, fh = self._front_rect()
        # Front corners
        f_tl = QPointF(fx, fy)
        f_tr = QPointF(fx + fw, fy)
        f_bl = QPointF(fx, fy + fh)
        f_br = QPointF(fx + fw, fy + fh)
        # Back corners
        b_tl = QPointF(fx + dx, fy + dy)
        b_tr = QPointF(fx + fw + dx, fy + dy)
        b_bl = QPointF(fx + dx, fy + fh + dy)
        b_br = QPointF(fx + fw + dx, fy + fh + dy)

        back   = QPolygonF([b_tl, b_tr, b_br, b_bl])
        left   = QPolygonF([b_tl, b_bl, f_bl, f_tl])
        bottom = QPolygonF([b_bl, b_br, f_br, f_bl])
        top    = QPolygonF([f_tl, f_tr, b_tr, b_tl])
        right  = QPolygonF([f_tr, f_br, b_br, b_tr])
        front  = QPolygonF([f_tl, f_tr, f_br, f_bl])

        angle = self._adjust2 % 360
        if angle < 90:      # back is left+below → left & bottom forward
            return [back, top, right, bottom, left, front]
        elif angle < 180:   # back is left+above → left & top forward
            return [back, bottom, right, top, left, front]
        elif angle < 270:   # back is right+above → right & top forward
            return [back, bottom, left, top, right, front]
        else:               # back is right+below → right & bottom forward
            return [back, top, left, bottom, right, front]

    # ----- visual helpers -----------------------------------------------------

    def _apply_pen_brush(self):
        """Apply pen and brush from current colors."""
        pen = QPen(self.pen_color, self.pen_width)
        _apply_dash_style(pen, self.line_dash, self.dash_pattern_length, self.dash_solid_percent)
        self.setPen(pen)
        self.setBrush(QBrush(self.brush_color))

    def _update_label_position(self):
        """Position label text inside the front face."""
        fx, fy, fw, fh = self._front_rect()
        self._position_label_in_rect(fx, fy, fw, fh)

    def _update_label_text(self):
        self._render_label_from_meta()

    def set_meta(self, meta: AnnotationMeta) -> None:
        """Set annotation metadata and update label display."""
        self.meta = meta
        self._update_label_text()

    # ----- geometry accessors -------------------------------------------------

    def rect(self) -> QRectF:
        """Return bounding rect of the item in local coords."""
        return QRectF(0, 0, self._width, self._height)

    def setRect(self, r: QRectF):
        """Resize the item to the given local rect."""
        self._width = r.width()
        self._height = r.height()
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()
        self._update_child_ports()

    def adjust1(self) -> float:
        """Return current depth (px)."""
        return self._adjust1

    def set_adjust1(self, value: float):
        """Set depth (px), clamped to 0–max_depth."""
        self._adjust1 = max(0, min(self._max_depth(), value))
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()

    def adjust2(self) -> float:
        """Return current angle (degrees)."""
        return self._adjust2

    def set_adjust2(self, value: float):
        """Set angle (degrees), clamped to 0–360."""
        self._adjust2 = max(0, min(360, value))
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()

    # ----- handles ------------------------------------------------------------

    def _handle_points_local(self) -> Dict[str, QPointF]:
        """Return handle positions in local coordinates."""
        cx = self._width / 2
        cy = self._height / 2
        fx, fy, fw, fh = self._front_rect()
        front_cx = fx + fw / 2
        front_cy = fy + fh / 2
        return {
            "tl": QPointF(0, 0),
            "tr": QPointF(self._width, 0),
            "bl": QPointF(0, self._height),
            "br": QPointF(self._width, self._height),
            "t":  QPointF(cx, 0),
            "b":  QPointF(cx, self._height),
            "l":  QPointF(0, cy),
            "r":  QPointF(self._width, cy),
            "adjust1": QPointF(front_cx, front_cy),
            # Angle handle at bbox center (stable — doesn't shift with angle/depth)
            "adjust2": QPointF(cx + 20 * math.sin(math.radians(self._adjust2)),
                               cy - 20 * math.cos(math.radians(self._adjust2))),
        }

    def hoverMoveEvent(self, event):
        """Update cursor based on handle under mouse."""
        h = self._hit_test_handle(event.scenePos())
        if h == "rotate":
            self.setCursor(_get_rotate_cursor())
        elif h in ("adjust1", "adjust2"):
            self.setCursor(Qt.CursorShape.CrossCursor)
        elif h:
            self.setCursor(self._cursor_for_handle(h))
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        """Begin resize/adjust tracking on handle press."""
        if event.button() == Qt.MouseButton.LeftButton:
            h = self._hit_test_handle(event.scenePos())
            if h == "rotate":
                self._begin_rotation()
                event.accept()
                return
            if h:
                self._begin_resize_tracking()
                self._active_handle = h
                self._resizing = True
                self._store_resize_anchor(h)
                self._press_scene = event.scenePos()
                self._start_pos = QPointF(self.pos())
                self._start_size = (self._width, self._height)
                self._start_adjust1 = self._adjust1
                self._start_adjust2 = self._adjust2
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle drag for resize and adjust handles."""
        if self._rotating:
            self._handle_rotation_move(event)
            return
        if self._resizing and self._active_handle and self._press_scene and self._start_pos and self._start_size:
            cur = event.scenePos()
            d_x, d_y = self._scene_delta_to_local(
                cur.x() - self._press_scene.x(),
                cur.y() - self._press_scene.y())

            # adjust1 (depth): drag front face away from back to increase depth
            if self._active_handle == "adjust1" and self._start_adjust1 is not None:
                fx, fy, fw, fh = self._front_rect()
                front_cx = self.pos().x() + fx + fw / 2
                front_cy = self.pos().y() + fy + fh / 2
                vec_x = cur.x() - front_cx
                vec_y = cur.y() - front_cy
                rad = math.radians(self._adjust2)
                sin_a, cos_a = math.sin(rad), math.cos(rad)
                # Extrusion dir is (-sin, cos); negate to get "pull outward = more depth"
                proj = vec_x * sin_a - vec_y * cos_a
                new_depth = max(0, min(self._max_depth(), proj))
                self._adjust1 = new_depth
                self._update_path()
                self._update_label_position()
                self._update_transform_origin()
                self._notify_changed()
                if MetaIsoCubeItem.on_adjust1_changed:
                    MetaIsoCubeItem.on_adjust1_changed(self, new_depth)
                event.accept()
                return

            # adjust2 (angle): atan2 from bbox center to cursor
            if self._active_handle == "adjust2" and self._start_adjust2 is not None:
                # Use bbox center — stable reference that doesn't shift with angle
                ref_x = self.pos().x() + self._width / 2
                ref_y = self.pos().y() + self._height / 2
                vec_x = cur.x() - ref_x
                vec_y = cur.y() - ref_y
                angle_deg = math.degrees(math.atan2(vec_x, -vec_y)) % 360
                self._adjust2 = angle_deg
                self._update_path()
                self._update_label_position()
                self._update_transform_origin()
                self._notify_changed()
                if MetaIsoCubeItem.on_adjust2_changed:
                    MetaIsoCubeItem.on_adjust2_changed(self, angle_deg)
                event.accept()
                return

            # Standard bbox resize handles
            w0, h0 = self._start_size
            new_w, new_h, anchor_after = self._compute_resize(
                self._active_handle, d_x, d_y, w0, h0)
            self._width = new_w
            self._height = new_h
            self._update_path()
            self._update_label_position()
            self._update_transform_origin()
            self._fixup_resize_pos(anchor_after)
            self._notify_changed()
            event.accept()
            return

        super().mouseMoveEvent(event)

    def shape(self) -> QPainterPath:
        """Return shape including handle hit areas when selected."""
        base = super().shape()
        if self._should_paint_handles():
            return shape_with_handles(base, self._handle_points_local(),
                                      rotation_knob_local=self._rotation_knob_local() if self._is_rotatable() else None)
        return base

    def boundingRect(self) -> QRectF:
        """Return bounding rect with handle margin."""
        r = super().boundingRect()
        margin = _get_handle_size() / 2 + 1
        return r.adjusted(-margin, -margin, margin, margin)

    def paint(self, painter: QPainter, option, widget=None):
        """Paint the cube face-by-face for proper alpha stacking, then selection handles."""
        # Custom rendering — draw each face individually so overlapping
        # semi-transparent fills create natural depth shading.
        dragging_adjust = self._resizing and self._active_handle in ("adjust1", "adjust2")

        pen = QPen(self.pen_color, self.pen_width)
        _apply_dash_style(pen, self.line_dash, self.dash_pattern_length, self.dash_solid_percent)
        painter.setPen(pen)
        painter.setBrush(QBrush(self.brush_color))

        if self._adjust1 < 0.5:
            fx, fy, fw, fh = self._front_rect()
            painter.drawRect(QRectF(fx, fy, fw, fh))
        else:
            faces = self._face_polygons()
            # Draw first 5 faces (back through right-front)
            for face in faces[:-1]:
                painter.drawPolygon(face)
            # Front face — thicker edge while dragging adjust handles
            if dragging_adjust:
                front_pen = QPen(self.pen_color, max(self.pen_width * 2.5, 4))
                _apply_dash_style(front_pen, self.line_dash, self.dash_pattern_length, self.dash_solid_percent)
                painter.setPen(front_pen)
            painter.drawPolygon(faces[-1])

        if self._should_paint_handles():
            sel_pen = QPen(_get_selection_color(), 1, Qt.PenStyle.DashLine)
            painter.setPen(sel_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(QRectF(0, 0, self._width, self._height))

            handles = self._handle_points_local()
            adjust1_handle = handles.pop("adjust1")
            adjust2_handle = handles.pop("adjust2")
            draw_handles(painter, handles)
            self._draw_rotation_knob(painter)

            # Yellow depth handle (circle)
            handle_size = _get_handle_size()
            half = handle_size / 2
            painter.setPen(QPen(QColor(204, 153, 0), 1))
            painter.setBrush(QBrush(QColor(255, 215, 0)))
            painter.drawEllipse(QRectF(adjust1_handle.x() - half, adjust1_handle.y() - half,
                                       handle_size, handle_size))

            # Angle handle — ∠ symbol with arc indicator (at bbox center)
            cx = self._width / 2
            cy = self._height / 2
            arm = 20
            arc_r = 8
            painter.setPen(QPen(QColor(255, 215, 0), 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            # Vertical reference arm (0° = up)
            painter.drawLine(QPointF(cx, cy), QPointF(cx, cy - arm))
            # Angle arm toward handle
            painter.drawLine(QPointF(cx, cy), adjust2_handle)
            # Filled arc wedge between the two arms
            angle_deg = self._adjust2
            # Qt drawPie: 0° = 3-o'clock, CCW positive, 1/16° units
            # Our 0° = up = Qt 90°; CW sweep = negative in Qt's CCW system
            start_16 = 90 * 16
            sweep_16 = int(-angle_deg * 16)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(255, 215, 0, 80)))
            painter.drawPie(QRectF(cx - arc_r, cy - arc_r, arc_r * 2, arc_r * 2),
                            start_16, sweep_16)
            # Small dot at the angle arm tip
            dot_r = 3
            painter.setPen(QPen(QColor(204, 153, 0), 1))
            painter.setBrush(QBrush(QColor(255, 215, 0)))
            painter.drawEllipse(QRectF(adjust2_handle.x() - dot_r, adjust2_handle.y() - dot_r,
                                       dot_r * 2, dot_r * 2))

    def mouseReleaseEvent(self, event):
        """End resize tracking on mouse release."""
        if self._rotating:
            self._end_rotation()
            event.accept()
            return
        if self._resizing:
            self._end_resize_tracking()
            self._resizing = False
            self._active_handle = None
            self._press_scene = None
            self._start_pos = None
            self._start_size = None
            self._start_adjust1 = None
            self._start_adjust2 = None
            self._notify_changed()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        """Notify on position/selection changes."""
        out = super().itemChange(change, value)
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if not self._resizing:
                self._notify_changed()
            self._update_child_port_connections()
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.prepareGeometryChange()
        return out

    def to_record(self) -> Dict[str, Any]:
        """Serialize isocube to JSON record."""
        p = self.pos()
        rec = {
            "id": self.ann_id,
            "kind": "isocube",
            **self._ports_dict(),
            "geom": {
                "x": round1(p.x()),
                "y": round1(p.y()),
                "w": round1(self._width),
                "h": round1(self._height),
                "adjust1": round1(self._adjust1),
                "adjust2": round1(self._adjust2),
            },
            **self._meta_dict(self.meta),
            **self._style_dict(),
        }
        z = self.zValue()
        if z != 0:
            rec["z"] = int(z)
        self._add_angle_to_geom(rec.get("geom", {}))
        return rec


class MetaGroupItem(QGraphicsItemGroup, MetaMixin, LinkedMixin):
    """Group item that contains multiple annotation items as a single unit."""

    KIND = "group"

    def _is_rotatable(self) -> bool:
        return False
    KIND_ALIASES = frozenset(k for k, v in KIND_ALIAS_MAP.items() if v == "group")

    def __init__(self, ann_id: str, on_change=None):
        QGraphicsItemGroup.__init__(self)
        MetaMixin.__init__(self)
        LinkedMixin.__init__(self, ann_id, on_change)

        self.kind ="group"
        self.setData(ANN_ID_KEY, ann_id)

        self.setFiltersChildEvents(False)

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        self.setAcceptHoverEvents(True)

        # Resize state
        self._active_handle: Optional[str] = None
        self._resizing = False
        self._press_scene: Optional[QPointF] = None
        self._start_cbr: Optional[QRectF] = None
        self._child_start_states: Dict = {}

    def add_member(self, item: QGraphicsItem):
        """Add an item to this group, removing its individual selectability."""
        item.setSelected(False)
        self.addToGroup(item)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)

    def remove_member(self, item: QGraphicsItem):
        """Remove an item from this group, restoring its selectability."""
        self.removeFromGroup(item)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)

    def member_items(self) -> list:
        """Return direct child annotation items (excluding non-annotation children)."""
        return [c for c in self.childItems() if hasattr(c, "ann_id")]

    def set_meta(self, meta: AnnotationMeta) -> None:
        """Set the annotation metadata."""
        self.meta = meta

    def _offset_geom(self, rec: dict, dx: float, dy: float) -> dict:
        """Offset geometry coordinates in a record by dx, dy (group-local to scene)."""
        out = dict(rec)
        kind = out.get("kind")
        if kind == "group":
            children = out.get("children", [])
            out["children"] = [self._offset_geom(c, dx, dy) for c in children]
        else:
            geom = dict(out.get("geom", {}))
            if kind == "line":
                geom["x1"] = round1(geom.get("x1", 0) + dx)
                geom["y1"] = round1(geom.get("y1", 0) + dy)
                geom["x2"] = round1(geom.get("x2", 0) + dx)
                geom["y2"] = round1(geom.get("y2", 0) + dy)
            else:
                geom["x"] = round1(geom.get("x", 0) + dx)
                geom["y"] = round1(geom.get("y", 0) + dy)
            out["geom"] = geom
        return out

    def to_record(self) -> Dict[str, Any]:
        """Serialize group and children with absolute scene coordinates."""
        gx = self.pos().x()
        gy = self.pos().y()
        children_recs = []
        for child in self.member_items():
            if hasattr(child, "to_record"):
                child_rec = child.to_record()
                # Child to_record returns group-local coords; offset to scene-absolute
                child_rec = self._offset_geom(child_rec, gx, gy)
                children_recs.append(child_rec)
        rec = {
            "id": self.ann_id,
            "kind": "group",
            "children": children_recs,
            **self._meta_dict(self.meta),
        }
        z = self.zValue()
        if z != 0:
            rec["z"] = int(z)
        self._add_angle_to_geom(rec.get("geom", {}))
        return rec

    # ---- Group resize helpers ----

    def _hit_test_handle(self, scene_pt: QPointF) -> Optional[str]:
        """Test if a scene point hits one of the group resize handles."""
        if not self._should_paint_handles():
            return None
        handles = self._handle_points_scene()
        hit_dist = _get_hit_distance()
        for k, hp in handles.items():
            if QLineF(scene_pt, hp).length() <= hit_dist:
                return k
        return None

    def _get_anchor(self, handle: str) -> QPointF:
        """Return the anchor point (opposite corner/edge) in group-local coords."""
        s = self._start_cbr
        anchors = {
            "tl": QPointF(s.right(), s.bottom()),
            "tr": QPointF(s.left(), s.bottom()),
            "bl": QPointF(s.right(), s.top()),
            "br": QPointF(s.left(), s.top()),
            "t":  QPointF(s.left(), s.bottom()),
            "b":  QPointF(s.left(), s.top()),
            "l":  QPointF(s.right(), s.top()),
            "r":  QPointF(s.left(), s.top()),
        }
        return anchors[handle]

    def _capture_child_states(self) -> Dict:
        """Snapshot each child's geometry for resize calculations."""
        states = {}
        for child in self.member_items():
            states[child] = self._snapshot_child(child)
        return states

    def _restore_child_states(self, states: Dict) -> None:
        """Restore each child's geometry from a snapshot dict."""
        for child, state in states.items():
            pos = state.get("pos")
            if isinstance(child, (MetaRectItem, MetaEllipseItem)):
                child.setRect(QRectF(0, 0, state["w"], state["h"]))
                if pos:
                    child.setPos(pos)
            elif isinstance(child, (MetaRoundedRectItem, MetaHexagonItem,
                                    MetaCylinderItem, MetaBlockArrowItem,
                                    MetaPolygonItem)):
                child._width = state["w"]
                child._height = state["h"]
                child._update_path()
                if hasattr(child, '_update_label_position'):
                    child._update_label_position()
                if pos:
                    child.setPos(pos)
            elif isinstance(child, MetaLineItem):
                child.setLine(QLineF(0, 0, state["dx"], state["dy"]))
                if pos:
                    child.setPos(pos)
            elif isinstance(child, MetaGroupItem):
                nested = state.get("nested", {})
                if nested:
                    child._restore_child_states(nested)
                if pos:
                    child.setPos(pos)
            else:
                if pos:
                    child.setPos(pos)

    def _snapshot_child(self, child) -> Dict:
        """Capture geometry state of a single child item."""
        pos = QPointF(child.pos())
        if isinstance(child, (MetaRectItem, MetaEllipseItem)):
            r = child.rect()
            return {"pos": pos, "w": r.width(), "h": r.height()}
        elif isinstance(child, (MetaRoundedRectItem, MetaHexagonItem,
                                MetaCylinderItem, MetaBlockArrowItem,
                                MetaPolygonItem)):
            return {"pos": pos, "w": child._width, "h": child._height}
        elif isinstance(child, MetaLineItem):
            ln = child.line()
            return {"pos": pos, "dx": ln.dx(), "dy": ln.dy()}
        elif isinstance(child, MetaGroupItem):
            nested = {}
            for gc in child.member_items():
                nested[gc] = self._snapshot_child(gc)
            cbr = QRectF(child.childrenBoundingRect())
            return {"pos": pos, "nested": nested, "cbr": cbr}
        else:
            # MetaTextItem or unknown — position only
            return {"pos": pos}

    def _apply_child_scale(self, child, state: Dict,
                           anchor: QPointF, sx: float, sy: float):
        """Scale a single child relative to anchor by (sx, sy)."""
        old_pos = state["pos"]
        new_x = anchor.x() + (old_pos.x() - anchor.x()) * sx
        new_y = anchor.y() + (old_pos.y() - anchor.y()) * sy

        if isinstance(child, (MetaRectItem, MetaEllipseItem)):
            child.setPos(QPointF(new_x, new_y))
            child.setRect(QRectF(0, 0, state["w"] * sx, state["h"] * sy))
        elif isinstance(child, (MetaRoundedRectItem, MetaHexagonItem,
                                MetaCylinderItem, MetaBlockArrowItem,
                                MetaPolygonItem)):
            child.setPos(QPointF(new_x, new_y))
            child._width = state["w"] * sx
            child._height = state["h"] * sy
            child._update_path()
            child._update_label_position()
        elif isinstance(child, MetaLineItem):
            child.setPos(QPointF(new_x, new_y))
            child.setLine(QLineF(0, 0, state["dx"] * sx, state["dy"] * sy))
        elif isinstance(child, MetaGroupItem):
            child.setPos(QPointF(new_x, new_y))
            # Recursively scale nested children relative to (0,0) within the nested group
            nested = state.get("nested", {})
            nested_cbr = state.get("cbr", QRectF())
            if not nested_cbr.isNull():
                nested_anchor = QPointF(0, 0)
                for gc, gs in nested.items():
                    self._apply_child_scale(gc, gs, nested_anchor, sx, sy)
        else:
            # MetaTextItem — position only
            child.setPos(QPointF(new_x, new_y))

    # ---- Mouse events for group resize ----

    def hoverMoveEvent(self, event):
        """Update cursor shape when hovering over resize handles."""
        h = self._hit_test_handle(event.scenePos())
        if h:
            self.setCursor(self._cursor_for_handle(h))
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        """Start group resize if a handle is clicked."""
        if event.button() == Qt.MouseButton.LeftButton:
            h = self._hit_test_handle(event.scenePos())
            if h:
                self._begin_resize_tracking()
                self._active_handle = h
                self._resizing = True
                self._store_resize_anchor(h)
                self._press_scene = event.scenePos()
                self._start_cbr = QRectF(self.childrenBoundingRect())
                self._child_start_states = self._capture_child_states()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Scale group children proportionally during handle drag."""
        if self._resizing and self._active_handle and self._press_scene and self._start_cbr:
            cur = event.scenePos()
            dx, dy = self._scene_delta_to_local(
                cur.x() - self._press_scene.x(),
                cur.y() - self._press_scene.y())

            s = self._start_cbr
            left = s.left()
            top = s.top()
            right = s.right()
            bottom = s.bottom()

            h = self._active_handle
            if h == "tl":
                left += dx; top += dy
            elif h == "tr":
                right += dx; top += dy
            elif h == "bl":
                left += dx; bottom += dy
            elif h == "br":
                right += dx; bottom += dy
            elif h == "t":
                top += dy
            elif h == "b":
                bottom += dy
            elif h == "l":
                left += dx
            elif h == "r":
                right += dx

            min_size = _get_min_size()
            if (right - left) < min_size:
                if h in ("tl", "bl", "l"):
                    left = right - min_size
                else:
                    right = left + min_size
            if (bottom - top) < min_size:
                if h in ("tl", "tr", "t"):
                    top = bottom - min_size
                else:
                    bottom = top + min_size

            new_w = right - left
            new_h = bottom - top
            sx = new_w / s.width() if s.width() > 0 else 1.0
            sy = new_h / s.height() if s.height() > 0 else 1.0

            # Side handles lock the perpendicular axis
            if h in ("l", "r"):
                sy = 1.0
            elif h in ("t", "b"):
                sx = 1.0

            anchor = self._get_anchor(h)

            self.prepareGeometryChange()
            for child, state in self._child_start_states.items():
                self._apply_child_scale(child, state, anchor, sx, sy)
            self._notify_changed()
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Finish group resize."""
        if self._resizing:
            self._end_resize_tracking()
            self._resizing = False
            self._active_handle = None
            self._press_scene = None
            self._start_cbr = None
            self._child_start_states = {}
            self._notify_changed()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _handle_points_local(self) -> Dict[str, QPointF]:
        """Return handle positions in local coordinates for the group bounding rect."""
        r = self.childrenBoundingRect()
        if r.isNull():
            return {}
        cx = r.left() + r.width() / 2
        cy = r.top() + r.height() / 2
        return {
            "tl": QPointF(r.left(), r.top()),
            "tr": QPointF(r.right(), r.top()),
            "bl": QPointF(r.left(), r.bottom()),
            "br": QPointF(r.right(), r.bottom()),
            "t":  QPointF(cx, r.top()),
            "b":  QPointF(cx, r.bottom()),
            "l":  QPointF(r.left(), cy),
            "r":  QPointF(r.right(), cy),
        }

    def _handle_points_scene(self) -> Dict[str, QPointF]:
        """Return handle positions in scene coordinates."""
        p = self.pos()
        return {
            k: QPointF(pt.x() + p.x(), pt.y() + p.y())
            for k, pt in self._handle_points_local().items()
        }

    def boundingRect(self) -> QRectF:
        """Expand bounding rect to include resize handles."""
        r = self.childrenBoundingRect()
        if r.isNull():
            return r
        margin = _get_handle_size() / 2 + 2
        return r.adjusted(-margin, -margin, margin, margin)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None):
        """Draw selection outline and control handles when selected."""
        if self._should_paint_handles():
            cr = self.childrenBoundingRect()
            if not cr.isNull():
                sel_color = _get_selection_color()
                pen = QPen(sel_color, 1, Qt.PenStyle.DashLine)
                painter.setPen(pen)
                painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
                painter.drawRect(cr)
                # Draw resize handles at corners and sides
                draw_handles(painter, self._handle_points_local())

    def itemChange(self, change, value):
        """Notify on position changes and update geometry on selection change."""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self._notify_changed()
            # Force scene to repaint the area we moved from/to
            self.update()
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.prepareGeometryChange()
        return super().itemChange(change, value)


# ═══════════════════════════════════════════════════════════
# MetaSeqBlockItem — Sequence diagram block (alt/loop/opt/…)
# ═══════════════════════════════════════════════════════════

# Divider defaults per block type
_SEQBLOCK_DEFAULTS: Dict[str, int] = {
    "alt": 1, "par": 1,
    "loop": 0, "opt": 0, "break": 0, "critical": 0,
}


class MetaSeqBlockItem(QGraphicsPathItem, MetaMixin, LinkedMixin):
    """Sequence-diagram combined fragment (alt/loop/opt/critical/break/par).

    A rectangular block with a type-tab in the top-left corner and up to
    three horizontal dashed dividers whose vertical positions are controlled
    by adjust1/adjust2/adjust3 (ratios 0.0–1.0 of total height).
    """

    KIND = "seqblock"
    KIND_ALIASES = frozenset()

    # Class-level callbacks (wired from main.py)
    on_adjust1_changed = None
    on_adjust2_changed = None
    on_adjust3_changed = None

    _TAB_HEIGHT = 20
    _TAB_PADDING = 4

    def __init__(self, x: float, y: float, w: float, h: float,
                 block_type: str, ann_id: str, on_change=None):
        QGraphicsPathItem.__init__(self)
        MetaMixin.__init__(self)
        LinkedMixin.__init__(self, ann_id, on_change)

        self.kind = "seqblock"
        self._block_type = block_type
        self._width = w
        self._height = h
        self._divider_count = _SEQBLOCK_DEFAULTS.get(block_type, 0)
        self._adjust1 = 0.5
        self._adjust2 = 0.67
        self._adjust3 = 0.83
        self.setPos(QPointF(x, y))
        self.setData(ANN_ID_KEY, ann_id)
        self._update_path()

        self.setAcceptHoverEvents(True)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        self._active_handle: Optional[str] = None
        self._resizing = False
        self._press_scene: Optional[QPointF] = None
        self._start_pos: Optional[QPointF] = None
        self._start_size: Optional[Tuple[float, float]] = None
        self._start_adjust1: Optional[float] = None
        self._start_adjust2: Optional[float] = None
        self._start_adjust3: Optional[float] = None

        self.pen_color = QColor("#9370DB")
        self.pen_width = 2
        self.brush_color = QColor("#ECECFF40")
        self.text_color = QColor("#333333")
        self.line_dash = "solid"
        cached = _CachedCanvasSettings.get()
        self.dash_pattern_length = cached.default_dash_length
        self.dash_solid_percent = cached.default_dash_solid_percent
        self._apply_pen_brush()

        # Section text items: one per region (top + up to 3 divider regions).
        # tech meta is pipe-separated; each section "[text]" is placed just
        # below its corresponding divider (first section below the tab).
        self._section_items: List[QGraphicsTextItem] = []
        for _ in range(4):
            ti = QGraphicsTextItem(self)
            ti.setAcceptHoverEvents(False)
            ti.setDefaultTextColor(self.text_color)
            ti.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
            ti.setVisible(False)
            self._section_items.append(ti)
        # Legacy compat: _label_item points to first section for shared code
        self._label_item = self._section_items[0]
        self._update_label_position()

    # ---- geometry helpers ----

    def _update_path(self):
        """Rebuild the outline path (simple rectangle)."""
        path = QPainterPath()
        path.addRect(0, 0, self._width, self._height)
        self.setPath(path)

    def _apply_pen_brush(self):
        """Apply pen and brush from current style properties."""
        pen = QPen(self.pen_color, self.pen_width)
        _apply_dash_style(pen, self.line_dash, self.dash_pattern_length, self.dash_solid_percent)
        self.setPen(pen)
        self.setBrush(QBrush(self.brush_color))

    def _update_label_position(self):
        """Position section labels: first just below tab, rest just below dividers."""
        tab_bottom = self._TAB_HEIGHT + self._TAB_PADDING
        padding = 4
        text_w = max(10, self._width - 2 * padding)

        # Region top-Y values: section 0 starts below tab,
        # section N starts below divider N.
        divider_ys = []
        if self._divider_count >= 1:
            divider_ys.append(self._adjust1 * self._height)
        if self._divider_count >= 2:
            divider_ys.append(self._adjust2 * self._height)
        if self._divider_count >= 3:
            divider_ys.append(self._adjust3 * self._height)

        for i, ti in enumerate(self._section_items):
            if not ti.isVisible():
                continue
            ti.setTextWidth(text_w)
            if i == 0:
                ti.setPos(padding, tab_bottom)
            elif i - 1 < len(divider_ys):
                ti.setPos(padding, divider_ys[i - 1] + padding)
            else:
                ti.setVisible(False)

    def _update_label_text(self):
        """Render pipe-separated tech sections as bracketed labels.

        ``meta.tech`` is split on ``|``.  Each section is displayed as
        ``[text]`` — the first just below the type tab, subsequent ones
        just below each divider line.
        """
        _eff_frame = self.meta.effective_frame()
        _eff_fmt = self.meta.effective_default_format()
        align_map = {"left": "left", "center": "center", "right": "right"}
        align = align_map.get(_eff_frame.halign or "center", "center")
        size = max(6, int(_eff_fmt.font_size or 10))

        sections: List[str] = []
        if self.meta.tech:
            sections = [s.strip() for s in self.meta.tech.split("|")]

        for i, ti in enumerate(self._section_items):
            if i < len(sections) and sections[i]:
                html = (f'<p style="text-align:{align}; font-size:{size}pt;">'
                        f'<i>[{sections[i]}]</i></p>')
                ti.setHtml(html)
                ti.setDefaultTextColor(self.text_color)
                ti.setVisible(True)
            else:
                ti.setPlainText("")
                ti.setVisible(False)

        self._update_label_position()

    def set_meta(self, meta: AnnotationMeta) -> None:
        """Assign metadata and refresh label."""
        self.meta = meta
        self._update_label_text()

    # ---- rect / adjust API ----

    def rect(self) -> QRectF:
        """Return the logical rectangle."""
        return QRectF(0, 0, self._width, self._height)

    def setRect(self, r: QRectF):
        """Set width/height and rebuild."""
        self._width = r.width()
        self._height = r.height()
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()
        self._update_child_ports()

    @property
    def block_type(self) -> str:
        return self._block_type

    def set_block_type(self, block_type: str):
        """Change the block type and reset divider count."""
        self._block_type = block_type
        self._divider_count = _SEQBLOCK_DEFAULTS.get(block_type, 0)
        self.prepareGeometryChange()
        self.update()

    def set_divider_count(self, count: int):
        """Set the number of dividers (0–3), spacing evenly if adding."""
        count = max(0, min(3, count))
        old = self._divider_count
        if count == old:
            return
        # When adding dividers, space them evenly in the available range
        if count > old:
            positions = []
            for i in range(count):
                positions.append((i + 1) / (count + 1))
            if count >= 1:
                self._adjust1 = positions[0]
            if count >= 2:
                self._adjust2 = positions[1]
            if count >= 3:
                self._adjust3 = positions[2]
        self.prepareGeometryChange()
        self._divider_count = count
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()
        self.update()

    def add_divider(self) -> bool:
        """Add one divider.  Returns True if successful."""
        if self._divider_count >= 3:
            return False
        new_count = self._divider_count + 1
        # Place the new divider evenly between the last divider and 1.0
        if new_count == 1:
            self._adjust1 = 0.5
        elif new_count == 2:
            # Place between adjust1 and bottom
            self._adjust2 = self._adjust1 + (1.0 - self._adjust1) / 2
        elif new_count == 3:
            self._adjust3 = self._adjust2 + (1.0 - self._adjust2) / 2
        self.prepareGeometryChange()
        self._divider_count = new_count
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()
        self.update()
        return True

    def remove_divider(self) -> bool:
        """Remove the last divider.  Returns True if successful."""
        if self._divider_count <= 0:
            return False
        self.prepareGeometryChange()
        self._divider_count -= 1
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()
        self.update()
        return True

    def set_adjust1(self, value: float):
        """Set first divider position (ratio 0.05–0.95)."""
        value = max(0.05, min(0.95, value))
        if self._divider_count >= 2:
            value = min(value, self._adjust2 - 0.05)
        self.prepareGeometryChange()
        self._adjust1 = value
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()
        self.update()

    def set_adjust2(self, value: float):
        """Set second divider position (ratio 0.05–0.95)."""
        value = max(0.05, min(0.95, value))
        value = max(value, self._adjust1 + 0.05)
        if self._divider_count >= 3:
            value = min(value, self._adjust3 - 0.05)
        self.prepareGeometryChange()
        self._adjust2 = value
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()
        self.update()

    def set_adjust3(self, value: float):
        """Set third divider position (ratio 0.05–0.95)."""
        value = max(0.05, min(0.95, value))
        value = max(value, self._adjust2 + 0.05)
        self.prepareGeometryChange()
        self._adjust3 = value
        self._update_path()
        self._update_label_position()
        self._update_transform_origin()
        self.update()

    # ---- handle points ----

    def _handle_points_local(self) -> Dict[str, QPointF]:
        """Standard 8 resize handles + yellow divider handles."""
        cx = self._width / 2
        cy = self._height / 2
        pts = {
            "tl": QPointF(0, 0),
            "tr": QPointF(self._width, 0),
            "bl": QPointF(0, self._height),
            "br": QPointF(self._width, self._height),
            "t":  QPointF(cx, 0),
            "b":  QPointF(cx, self._height),
            "l":  QPointF(0, cy),
            "r":  QPointF(self._width, cy),
        }
        if self._divider_count >= 1:
            pts["adjust1"] = QPointF(cx, self._adjust1 * self._height)
        if self._divider_count >= 2:
            pts["adjust2"] = QPointF(cx, self._adjust2 * self._height)
        if self._divider_count >= 3:
            pts["adjust3"] = QPointF(cx, self._adjust3 * self._height)
        return pts

    # ---- mouse events ----

    def hoverMoveEvent(self, event):
        h = self._hit_test_handle(event.scenePos())
        if h == "rotate":
            self.setCursor(_get_rotate_cursor())
        elif h in ("adjust1", "adjust2", "adjust3"):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif h:
            self.setCursor(self._cursor_for_handle(h))
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            h = self._hit_test_handle(event.scenePos())
            if h == "rotate":
                self._begin_rotation()
                event.accept()
                return
            if h:
                self._begin_resize_tracking()
                self._active_handle = h
                self._resizing = True
                self._store_resize_anchor(h)
                self._press_scene = event.scenePos()
                self._start_pos = QPointF(self.pos())
                self._start_size = (self._width, self._height)
                self._start_adjust1 = self._adjust1
                self._start_adjust2 = self._adjust2
                self._start_adjust3 = self._adjust3
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._rotating:
            self._handle_rotation_move(event)
            return
        if self._resizing and self._active_handle and self._press_scene and self._start_pos and self._start_size:
            cur = event.scenePos()
            dx, dy = self._scene_delta_to_local(
                cur.x() - self._press_scene.x(),
                cur.y() - self._press_scene.y())

            # Divider handle: vertical-only drag
            if self._active_handle == "adjust1" and self._start_adjust1 is not None:
                new_val = self._start_adjust1 + dy / self._height if self._height > 0 else 0.5
                self.set_adjust1(new_val)
                self._notify_changed()
                if MetaSeqBlockItem.on_adjust1_changed:
                    MetaSeqBlockItem.on_adjust1_changed(self, self._adjust1)
                event.accept()
                return

            if self._active_handle == "adjust2" and self._start_adjust2 is not None:
                new_val = self._start_adjust2 + dy / self._height if self._height > 0 else 0.67
                self.set_adjust2(new_val)
                self._notify_changed()
                if MetaSeqBlockItem.on_adjust2_changed:
                    MetaSeqBlockItem.on_adjust2_changed(self, self._adjust2)
                event.accept()
                return

            if self._active_handle == "adjust3" and self._start_adjust3 is not None:
                new_val = self._start_adjust3 + dy / self._height if self._height > 0 else 0.83
                self.set_adjust3(new_val)
                self._notify_changed()
                if MetaSeqBlockItem.on_adjust3_changed:
                    MetaSeqBlockItem.on_adjust3_changed(self, self._adjust3)
                event.accept()
                return

            # Standard resize handles
            w0, h0 = self._start_size
            new_w, new_h, anchor_after = self._compute_resize(
                self._active_handle, dx, dy, w0, h0)
            self._width = new_w
            self._height = new_h
            self._update_path()
            self._update_label_position()
            self._update_transform_origin()
            self._fixup_resize_pos(anchor_after)
            self._notify_changed()
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._rotating:
            self._end_rotation()
            event.accept()
            return
        if self._resizing:
            self._end_resize_tracking()
            self._resizing = False
            self._active_handle = None
            self._press_scene = None
            self._start_pos = None
            self._start_size = None
            self._start_adjust1 = None
            self._start_adjust2 = None
            self._start_adjust3 = None
            self._notify_changed()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    # ---- paint ----

    def paint(self, painter: QPainter, option, widget=None):
        """Draw the sequence block: fill, border, type tab, dividers, handles."""
        my_option = QStyleOptionGraphicsItem(option)
        my_option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, my_option, widget)

        w = self._width
        h = self._height
        if w <= 0 or h <= 0:
            return

        # --- Type tab in top-left ---
        tab_text = self._block_type.upper()
        fm = painter.fontMetrics()
        text_w = fm.horizontalAdvance(tab_text)
        tab_w = text_w + 2 * self._TAB_PADDING + 8
        tab_h = self._TAB_HEIGHT

        # Pentagon tab shape (like UML combined fragments)
        tab_path = QPainterPath()
        tab_path.moveTo(0, 0)
        tab_path.lineTo(tab_w, 0)
        tab_path.lineTo(tab_w, tab_h - 6)
        tab_path.lineTo(tab_w - 6, tab_h)
        tab_path.lineTo(0, tab_h)
        tab_path.closeSubpath()

        painter.setPen(QPen(self.pen_color, self.pen_width))
        painter.setBrush(QBrush(QColor(self.pen_color.red(), self.pen_color.green(),
                                       self.pen_color.blue(), 60)))
        painter.drawPath(tab_path)

        painter.setPen(QPen(self.text_color))
        painter.drawText(self._TAB_PADDING, int(tab_h * 0.72), tab_text)

        # --- Dashed divider lines ---
        if self._divider_count >= 1:
            div_pen = QPen(self.pen_color, 1, Qt.PenStyle.DashLine)
            painter.setPen(div_pen)
            y1 = self._adjust1 * h
            painter.drawLine(QPointF(0, y1), QPointF(w, y1))
        if self._divider_count >= 2:
            y2 = self._adjust2 * h
            painter.drawLine(QPointF(0, y2), QPointF(w, y2))
        if self._divider_count >= 3:
            y3 = self._adjust3 * h
            painter.drawLine(QPointF(0, y3), QPointF(w, y3))

        # --- Selection handles ---
        if self._should_paint_handles():
            sel_pen = QPen(_get_selection_color(), 1, Qt.PenStyle.DashLine)
            painter.setPen(sel_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(QRectF(0, 0, w, h))

            handles = self._handle_points_local()
            # Separate adjust handles for yellow drawing
            adjust_handles = {}
            for key in ("adjust1", "adjust2", "adjust3"):
                if key in handles:
                    adjust_handles[key] = handles.pop(key)
            draw_handles(painter, handles)
            self._draw_rotation_knob(painter)

            # Yellow adjust handles
            if adjust_handles:
                handle_size = _get_handle_size()
                half = handle_size / 2
                painter.setPen(QPen(QColor(204, 153, 0), 1))
                painter.setBrush(QBrush(QColor(255, 215, 0)))
                for pt in adjust_handles.values():
                    painter.drawEllipse(QRectF(pt.x() - half, pt.y() - half,
                                               handle_size, handle_size))

    def shape(self) -> QPainterPath:
        base = super().shape()
        if self._should_paint_handles():
            return shape_with_handles(base, self._handle_points_local(),
                                      rotation_knob_local=self._rotation_knob_local() if self._is_rotatable() else None)
        return base

    def boundingRect(self) -> QRectF:
        r = super().boundingRect()
        margin = _get_handle_size() / 2 + 1
        return r.adjusted(-margin, -margin, margin, margin)

    def itemChange(self, change, value):
        out = super().itemChange(change, value)
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if not self._resizing:
                self._notify_changed()
            self._update_child_port_connections()
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.prepareGeometryChange()
        return out

    # ---- serialization ----

    def to_record(self) -> Dict[str, Any]:
        """Serialize to a JSON-compatible dict."""
        p = self.pos()
        geom = {
            "x": round1(p.x()),
            "y": round1(p.y()),
            "w": round1(self._width),
            "h": round1(self._height),
        }
        if self._divider_count >= 1:
            geom["adjust1"] = round1(self._adjust1)
        if self._divider_count >= 2:
            geom["adjust2"] = round1(self._adjust2)
        if self._divider_count >= 3:
            geom["adjust3"] = round1(self._adjust3)

        rec = {
            "id": self.ann_id,
            "kind": "seqblock",
            **self._ports_dict(),
            "geom": geom,
            **self._meta_dict(self.meta),
            **self._style_dict(),
        }
        z = self.zValue()
        if z != 0:
            rec["z"] = int(z)
        self._add_angle_to_geom(rec.get("geom", {}))
        return rec


# ═══════════════════════════════════════════════════════════
# MetaPortItem — connector port on parent shape perimeter
# ═══════════════════════════════════════════════════════════

class MetaPortItem(QGraphicsEllipseItem, MetaMixin, LinkedMixin):
    """Connector port that attaches to the perimeter of a parent shape.

    Ports are child items of their parent shape and move/rotate
    automatically with the parent.  Dragging a port constrains it to
    the parent's perimeter.  Connected line/curve/orthocurve endpoints
    update to follow the port's scene position.
    """

    KIND = "port"
    KIND_ALIASES = frozenset()

    PORT_IN = "In"
    PORT_OUT = "Out"
    PORT_INOUT = "InOut"

    def __init__(self, t: float, radius: float,
                 parent_shape: QGraphicsItem, ann_id: str,
                 on_change=None):
        """Create a port at position *t* on *parent_shape*'s perimeter.

        Args:
            t: Position on parent perimeter as fraction of path length (0.0–1.0).
            radius: Circle radius in pixels.
            parent_shape: The parent graphics item (must have a KIND).
            ann_id: Annotation ID string.
            on_change: Callback when geometry changes.
        """
        QGraphicsEllipseItem.__init__(
            self, QRectF(-radius, -radius, 2 * radius, 2 * radius))
        MetaMixin.__init__(self)
        LinkedMixin.__init__(self, ann_id, on_change)

        self.kind = "port"
        self._t = t % 1.0  # fraction of perimeter path length
        self._radius = radius
        self._parent_shape = parent_shape
        self._port_type = self.PORT_INOUT
        self._protocol = ""
        self._connections: List[str] = []

        self.setParentItem(parent_shape)
        self.setData(ANN_ID_KEY, ann_id)
        self.setZValue(10000)  # Above parent's other children

        self.setAcceptHoverEvents(True)
        flags = (QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
                 | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        if parent_shape is None:
            flags |= QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        self.setFlags(flags)

        # Visual style
        self.pen_color = QColor("#0066CC")
        self.pen_width = 1.5
        self.brush_color = QColor("#CCE5FF")
        self.text_color = QColor("#333333")
        self._apply_pen_brush()

        # Drag state
        self._dragging = False
        self._press_scene: Optional[QPointF] = None

        # Error state — shown when JSON has validation issues
        self._has_error = False

        # Snap hover state — shown when a line/curve endpoint is near this port
        self._snap_hover = False

        # Place on perimeter
        self._update_position_from_t()

    # ---- visual style ----

    def _apply_pen_brush(self):
        """Apply pen and brush from current style properties."""
        pen = QPen(self.pen_color, self.pen_width)
        self.setPen(pen)
        self.setBrush(QBrush(self.brush_color))

    def set_snap_hover(self, active: bool):
        """Toggle the snap-hover glow ring shown during endpoint drag proximity."""
        if active != self._snap_hover:
            self._snap_hover = active
            self.prepareGeometryChange()
            self.update()

    def _is_rotatable(self) -> bool:
        return False

    # ---- perimeter positioning ----

    def _update_position_from_t(self):
        """Recompute local position from the current t on parent perimeter."""
        from canvas.perimeter import perimeter_point
        parent = self._parent_shape
        if parent is None:
            return
        kind = getattr(parent, 'kind', getattr(parent, 'KIND', 'rect'))
        pt = perimeter_point(kind, parent, self._t)
        self.setPos(pt)

    def _update_connected_lines(self):
        """Move connected line/curve endpoints to follow this port."""
        if not self._connections:
            return
        scene = self.scene()
        if not scene:
            return
        port_scene_pos = self.mapToScene(QPointF(0, 0))
        for item in scene.items():
            if not hasattr(item, 'ann_id') or item.ann_id not in self._connections:
                continue
            # Ensure the line/curve knows about this port connection
            if hasattr(item, '_port_ids') and self.ann_id not in item._port_ids:
                item._port_ids.append(self.ann_id)
            # Auto-detect which end if not already known
            if hasattr(item, '_port_endpoints') and self.ann_id not in item._port_endpoints:
                if isinstance(item, MetaLineItem):
                    p = item.pos()
                    ln = item.line()
                    p1 = QPointF(p.x() + ln.x1(), p.y() + ln.y1())
                    p2 = QPointF(p.x() + ln.x2(), p.y() + ln.y2())
                    d1 = (p1.x() - port_scene_pos.x()) ** 2 + (p1.y() - port_scene_pos.y()) ** 2
                    d2 = (p2.x() - port_scene_pos.x()) ** 2 + (p2.y() - port_scene_pos.y()) ** 2
                    item._port_endpoints[self.ann_id] = "start" if d1 <= d2 else "end"
                elif isinstance(item, MetaCurveItem):
                    if item._nodes:
                        p1 = item._node_scene_pos(0)
                        p2 = item._node_scene_pos(item._last_anchor_index())
                        d1 = (p1.x() - port_scene_pos.x()) ** 2 + (p1.y() - port_scene_pos.y()) ** 2
                        d2 = (p2.x() - port_scene_pos.x()) ** 2 + (p2.y() - port_scene_pos.y()) ** 2
                        item._port_endpoints[self.ann_id] = "start" if d1 <= d2 else "end"
            self._snap_endpoint(item, port_scene_pos)

    def _snap_endpoint(self, item, port_pos: QPointF):
        """Snap the connected endpoint of a line/curve/orthocurve to port_pos.

        Uses _port_endpoints mapping when available to determine which end
        is connected, falling back to nearest-distance heuristic.
        """
        # Determine which end this port is connected to
        known_end = getattr(item, '_port_endpoints', {}).get(self.ann_id)

        if isinstance(item, MetaLineItem):
            p = item.pos()
            ln = item.line()
            if known_end == "start":
                at_start = True
            elif known_end == "end":
                at_start = False
            else:
                p1 = QPointF(p.x() + ln.x1(), p.y() + ln.y1())
                p2 = QPointF(p.x() + ln.x2(), p.y() + ln.y2())
                d1 = (p1.x() - port_pos.x()) ** 2 + (p1.y() - port_pos.y()) ** 2
                d2 = (p2.x() - port_pos.x()) ** 2 + (p2.y() - port_pos.y()) ** 2
                at_start = d1 <= d2
            if at_start:
                item.setLine(QLineF(
                    port_pos.x() - p.x(), port_pos.y() - p.y(),
                    ln.x2(), ln.y2()))
            else:
                item.setLine(QLineF(
                    ln.x1(), ln.y1(),
                    port_pos.x() - p.x(), port_pos.y() - p.y()))
            if hasattr(item, '_notify_changed'):
                item._notify_changed()
        elif isinstance(item, MetaCurveItem):
            # Works for both MetaCurveItem and MetaOrthoCurveItem
            if not item._nodes:
                return
            first_idx = 0
            last_idx = item._last_anchor_index()
            if known_end == "start":
                at_start = True
            elif known_end == "end":
                at_start = False
            else:
                p1 = item._node_scene_pos(first_idx)
                p2 = item._node_scene_pos(last_idx)
                d1 = (p1.x() - port_pos.x()) ** 2 + (p1.y() - port_pos.y()) ** 2
                d2 = (p2.x() - port_pos.x()) ** 2 + (p2.y() - port_pos.y()) ** 2
                at_start = d1 <= d2
            idx = first_idx if at_start else last_idx
            w = item._width if item._width > 0 else 1.0
            h = item._height if item._height > 0 else 1.0
            # Use mapFromScene for rotation-aware coordinate conversion
            local = item.mapFromScene(port_pos)
            rx = local.x() / w
            ry = local.y() / h
            node = item._nodes[idx]
            cmd = node.get("cmd", "L")
            # Move the endpoint node
            if cmd == "H":
                node["x"] = rx
            elif cmd == "V":
                node["y"] = ry
            else:
                node["x"] = rx
                node["y"] = ry
            # For orthocurves, also adjust the adjacent node so the
            # H/V pair stays connected.  E.g. if the last two nodes
            # are ...V, H  moving H.x also needs V.y = ry so the
            # vertical segment reaches the new endpoint height.
            if isinstance(item, MetaOrthoCurveItem) and not at_start and idx >= 1:
                # Only adjust the second-to-last node for the END of the curve.
                # The start (M node) moves freely; the first H/V after M is unchanged.
                adj = item._nodes[idx - 1]
                adj_cmd = adj.get("cmd", "L")
                if cmd == "H" and adj_cmd in ("V", "M", "L"):
                    adj["y"] = ry
                elif cmd == "V" and adj_cmd in ("H", "M", "L"):
                    adj["x"] = rx
                elif cmd in ("M", "L"):
                    if adj_cmd == "H":
                        adj["x"] = rx
                    elif adj_cmd == "V":
                        adj["y"] = ry
            item._recalculate_bbox()
            if hasattr(item, '_notify_changed'):
                item._notify_changed()

    # ---- properties ----

    @property
    def parent_id(self) -> str:
        """Annotation ID of the parent shape, or empty string if parentless."""
        if self._parent_shape and hasattr(self._parent_shape, 'ann_id'):
            return self._parent_shape.ann_id
        return ""

    @property
    def port_type(self) -> str:
        return self._port_type

    def set_port_type(self, value: str):
        if value in (self.PORT_IN, self.PORT_OUT, self.PORT_INOUT):
            self._port_type = value
            self.update()

    @property
    def protocol(self) -> str:
        return self._protocol

    def set_protocol(self, value: str):
        self._protocol = value

    @property
    def connections(self) -> List[str]:
        return self._connections

    def add_connection(self, ann_id: str):
        """Add a line/curve id to the connections list."""
        if ann_id not in self._connections:
            self._connections.append(ann_id)

    def remove_connection(self, ann_id: str):
        """Remove a line/curve id from the connections list."""
        if ann_id in self._connections:
            self._connections.remove(ann_id)

    # ---- mouse events (perimeter drag) ----

    def hoverMoveEvent(self, event):
        self.setCursor(Qt.CursorShape.CrossCursor)
        super().hoverMoveEvent(event)

    def _handle_points_local(self) -> Dict[str, QPointF]:
        """Return handle positions in local coordinates (center only for ports)."""
        return {"center": QPointF(0, 0)}

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Select this port (clear others unless Ctrl held)
            scene = self.scene()
            if scene and not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
                scene.clearSelection()
            self.setSelected(True)
            if self._parent_shape is not None:
                # Parented port: start perimeter drag
                self._dragging = True
                self._press_scene = event.scenePos()
                event.accept()
                return
        # Parentless port: use default Qt movable behavior
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging and self._parent_shape:
            from canvas.perimeter import t_from_local_point
            parent = self._parent_shape
            # Convert scene pos to parent local coords
            local = parent.mapFromScene(event.scenePos())
            kind = getattr(parent, 'kind', getattr(parent, 'KIND', 'rect'))
            self._t = t_from_local_point(kind, parent, local.x(), local.y())
            self._update_position_from_t()
            self._update_connected_lines()
            self._notify_changed()
            event.accept()
            return
        # Parentless port: default Qt move
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._dragging:
            self._dragging = False
            self._press_scene = None
            self._notify_changed()
            event.accept()
            return
        # Parentless port: default Qt release
        super().mouseReleaseEvent(event)

    def _outward_normal_deg(self) -> float:
        """Return the outward normal angle (degrees) at this port's perimeter position.

        The outward normal points away from the parent's center, aligned
        perpendicular to the parent edge at the port's t position.
        """
        from canvas.perimeter import outward_normal_angle
        parent = self._parent_shape
        if parent is None:
            return 0.0
        kind = getattr(parent, 'kind', getattr(parent, 'KIND', 'rect'))
        return outward_normal_angle(kind, parent, self._t)

    # ---- paint ----

    def paint(self, painter: QPainter, option, widget=None):
        """Draw the port circle with a direction indicator rotated to the surface normal."""
        my_option = QStyleOptionGraphicsItem(option)
        my_option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, my_option, widget)

        r = self._radius
        # Rotate direction indicator to match outward normal
        normal = self._outward_normal_deg()
        painter.save()
        painter.rotate(normal)

        painter.setPen(QPen(self.pen_color, 1.5))
        if self._port_type == self.PORT_IN:
            # Arrow pointing inward (toward center = left in rotated frame)
            tip_x = -r * 0.5
            tail_x = r * 0.5
            painter.drawLine(QPointF(tail_x, 0), QPointF(tip_x, 0))
            painter.drawLine(QPointF(tip_x + r * 0.3, -r * 0.35), QPointF(tip_x, 0))
            painter.drawLine(QPointF(tip_x + r * 0.3, r * 0.35), QPointF(tip_x, 0))
        elif self._port_type == self.PORT_OUT:
            # Arrow pointing outward (away from center = right in rotated frame)
            tip_x = r * 0.5
            tail_x = -r * 0.5
            painter.drawLine(QPointF(tail_x, 0), QPointF(tip_x, 0))
            painter.drawLine(QPointF(tip_x - r * 0.3, -r * 0.35), QPointF(tip_x, 0))
            painter.drawLine(QPointF(tip_x - r * 0.3, r * 0.35), QPointF(tip_x, 0))
        else:  # InOut — dash line along the normal
            painter.drawLine(QPointF(-r * 0.5, 0), QPointF(r * 0.5, 0))

        painter.restore()

        # External direction badge on inward side — visible when lines cover the port
        if self._connections:
            painter.save()
            painter.rotate(normal)
            d = -(r + 6)  # inward side (negative = toward parent center)
            s = r * 0.8   # badge size
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(self.pen_color))
            if self._port_type == self.PORT_IN:
                # Triangle pointing inward (toward center)
                tri = QPolygonF([
                    QPointF(d, 0),
                    QPointF(d + s, -s * 0.7),
                    QPointF(d + s, s * 0.7),
                ])
                painter.drawPolygon(tri)
            elif self._port_type == self.PORT_OUT:
                # Triangle pointing outward (away from center)
                tri = QPolygonF([
                    QPointF(d + s, 0),
                    QPointF(d, -s * 0.7),
                    QPointF(d, s * 0.7),
                ])
                painter.drawPolygon(tri)
            else:  # InOut — diamond
                tri = QPolygonF([
                    QPointF(d + s, 0),
                    QPointF(d + s * 0.5, -s * 0.5),
                    QPointF(d, 0),
                    QPointF(d + s * 0.5, s * 0.5),
                ])
                painter.drawPolygon(tri)
            painter.restore()

        # Snap hover glow — bright cyan ring when a line endpoint is nearby
        if self._snap_hover:
            glow_pen = QPen(QColor(0, 200, 255, 180), 3.0)
            painter.setPen(glow_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            m = r + 5
            painter.drawEllipse(QRectF(-m, -m, 2 * m, 2 * m))

        # Error indicator — red dashed circle
        if self._has_error:
            err_pen = QPen(QColor("#FF0000"), 1.5, Qt.PenStyle.DashDotLine)
            painter.setPen(err_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            m = r + 2
            painter.drawEllipse(QRectF(-m, -m, 2 * m, 2 * m))

        # Selection highlight — dashed circle
        if self.isSelected():
            sel_pen = QPen(_get_selection_color(), 1.5, Qt.PenStyle.DashLine)
            painter.setPen(sel_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            m = r + 3
            painter.drawEllipse(QRectF(-m, -m, 2 * m, 2 * m))

    def boundingRect(self) -> QRectF:
        extra = 9 if self._snap_hover else (8 if self._connections else 4)
        m = self._radius + extra
        return QRectF(-m, -m, 2 * m, 2 * m)

    # ---- serialization ----

    def to_record(self) -> Dict[str, Any]:
        """Serialize to a JSON-compatible dict."""
        parent_id = ""
        if self._parent_shape and hasattr(self._parent_shape, 'ann_id'):
            parent_id = self._parent_shape.ann_id

        geom: Dict[str, Any] = {
            "t": round(self._t, 4),
            "radius": round1(self._radius),
            "port_type": self._port_type,
            "protocol": self._protocol,
        }
        # Parentless ports: include absolute position and size
        if not self._parent_shape:
            p = self.pos()
            geom["x"] = round1(p.x())
            geom["y"] = round1(p.y())
            geom["w"] = round1(self._radius * 2)
            geom["h"] = round1(self._radius * 2)

        rec = {
            "id": self.ann_id,
            "kind": "port",
            "parent_id": parent_id,
            "connections": list(self._connections),
            "geom": geom,
            **self._meta_dict(self.meta),
            **self._style_dict(),
        }
        z = self.zValue()
        if z != 0:
            rec["z"] = int(z)
        return rec

    def apply_style_from_record(self, rec: Dict[str, Any]):
        """Apply style properties from a JSON record."""
        style = rec.get("style", {})
        pen = style.get("pen", {})
        fill = style.get("fill", {})
        from utils import hex_to_qcolor
        if pen.get("color"):
            self.pen_color = hex_to_qcolor(pen["color"], self.pen_color)
        if pen.get("width"):
            self.pen_width = float(pen["width"])
        if fill.get("color"):
            self.brush_color = hex_to_qcolor(fill["color"], self.brush_color)
        self._apply_pen_brush()

    def update_from_record(self, rec: Dict[str, Any], scene):
        """Update this port in-place from a JSON record during scene rebuild.

        Keeps the port attached to its parent and visible even if some
        fields are temporarily invalid (e.g. mid-edit in JSON editor).
        Sets ``_has_error`` when values can't be applied cleanly.
        """
        from canvas.perimeter import PORTEABLE_KINDS
        from models import AnnotationMeta

        g = rec.get("geom", {})
        had_error = False

        # Snapshot scene position NOW, before any position updates can
        # corrupt it (e.g. _update_position_from_t with a stale parent).
        # Qt does NOT adjust pos() on setParentItem(None), so the rebuild
        # cleanup preserves scene position explicitly; mapToScene is safe
        # here because the port has no Qt parent at this point.
        in_scene = self.scene() is not None
        scene_pos = self.mapToScene(QPointF(0, 0)) if in_scene else self.pos()

        # ── parent re-attachment ──
        # Always re-resolve the parent because the parent object may have
        # been destroyed and recreated during a scene rebuild even though
        # the ann_id stays the same.
        # parent_id lives at record level; fall back to geom for legacy data
        parent_id = rec.get("parent_id", g.get("parent_id", ""))
        new_parent = None
        if parent_id:
            for si in scene.items():
                if hasattr(si, 'ann_id') and si.ann_id == parent_id:
                    new_parent = si
                    break

        if new_parent and hasattr(new_parent, 'kind') and new_parent.kind in PORTEABLE_KINDS:
            was_different_parent = (self._parent_shape is not new_parent)
            if was_different_parent:
                self._parent_shape = new_parent
                self.setParentItem(new_parent)
            # Ensure correct flags for parented port
            flags = (QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
                     | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
            self.setFlags(flags)
            if was_different_parent:
                # Newly assigned parent — find nearest perimeter point
                # from the port's previous scene position.
                from canvas.perimeter import t_from_local_point
                local = new_parent.mapFromScene(scene_pos)
                kind = getattr(new_parent, 'kind',
                               getattr(new_parent, 'KIND', 'rect'))
                self._t = t_from_local_point(
                    kind, new_parent, local.x(), local.y())
            self._update_position_from_t()
        elif not parent_id:
            # Parentless port — preserve scene position when detaching.
            # Qt does NOT adjust pos() on setParentItem(None), so we
            # must capture scene_pos before detaching and restore after.
            was_parented = self._parent_shape is not None
            has_qt_parent = self.parentItem() is not None
            if has_qt_parent:
                # Still has Qt parent — capture scene pos and detach
                scene_pos = self.mapToScene(QPointF(0, 0))
            if was_parented or has_qt_parent:
                self._parent_shape = None
                if has_qt_parent:
                    self.setParentItem(None)
                self._t = 0.0
            # Ensure the port is in the scene (setParentItem(None) may
            # have removed it if the old parent was already gone).
            still_in_scene = self.scene() is not None
            if not still_in_scene:
                scene.addItem(self)
            if was_parented or has_qt_parent:
                self.setPos(scene_pos)
            elif "x" in g and "y" in g:
                # Already parentless — apply position from geom
                try:
                    self.setPos(QPointF(float(g["x"]), float(g["y"])))
                except (ValueError, TypeError):
                    had_error = True
            # else: keep current pos (port just detached, geom not yet updated)
            flags = (QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
                     | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
                     | QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
            self.setFlags(flags)
        elif parent_id and not new_parent:
            # Parent ID specified but parent not found — keep current attachment
            had_error = True

        # ── t position (only meaningful when parented) ──
        if self._parent_shape is not None:
            try:
                if "t" in g:
                    new_t = float(g["t"]) % 1.0
                else:
                    new_t = float(g.get("angle", 0)) / 360.0
                if abs(new_t - self._t) > 1e-6:
                    self._t = new_t
                    self._update_position_from_t()
            except (ValueError, TypeError):
                had_error = True

        # ── radius ──
        try:
            new_radius = float(g.get("radius", self._radius))
            if new_radius >= 1 and abs(new_radius - self._radius) > 0.01:
                self._radius = new_radius
                self.setRect(QRectF(-new_radius, -new_radius,
                                    2 * new_radius, 2 * new_radius))
        except (ValueError, TypeError):
            had_error = True

        # ── port_type ──
        pt = g.get("port_type", self._port_type)
        if pt in (self.PORT_IN, self.PORT_OUT, self.PORT_INOUT):
            self._port_type = pt
        else:
            had_error = True  # invalid value — keep old type, flag error

        # ── protocol & connections ──
        self._protocol = str(g.get("protocol", self._protocol))
        # connections lives at record level; fall back to geom for legacy data
        conns = rec.get("connections", g.get("connections", self._connections))
        if isinstance(conns, list):
            self._connections = list(conns)

        # ── contents (was meta) ──
        meta_dict = rec.get("contents") or rec.get("meta") or {}
        if isinstance(meta_dict, dict):
            meta_dict.pop("kind", None)
            self.set_meta(AnnotationMeta.from_dict(meta_dict))

        # ── style ──
        self.apply_style_from_record(rec)

        # ── z-index ──
        z = rec.get("z", 0)
        if z:
            self.setZValue(z)

        # ── error state ──
        old_error = self._has_error
        self._has_error = had_error
        if old_error != had_error:
            self.prepareGeometryChange()
        self.update()

    def itemChange(self, change, value):
        out = super().itemChange(change, value)
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self._update_connected_lines()
            if not self._dragging:
                self._notify_changed()
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.prepareGeometryChange()
        return out


# ═══════════════════════════════════════════════════════════
# Kind alias registry — validates uniqueness at import time
# ═══════════════════════════════════════════════════════════

_ALL_META_CLASSES = [
    MetaRectItem, MetaRoundedRectItem, MetaEllipseItem, MetaLineItem,
    MetaTextItem, MetaHexagonItem, MetaCylinderItem, MetaBlockArrowItem,
    MetaPolygonItem, MetaCurveItem, MetaOrthoCurveItem, MetaIsoCubeItem,
    MetaSeqBlockItem, MetaPortItem, MetaGroupItem,
]

# Validate: no alias appears in more than one class
_seen_aliases: Dict[str, str] = {}
for _cls in _ALL_META_CLASSES:
    for _alias in _cls.KIND_ALIASES:
        if _alias in _seen_aliases:
            raise ValueError(
                f"Duplicate KIND_ALIAS '{_alias}': claimed by both "
                f"'{_seen_aliases[_alias]}' and '{_cls.KIND}'"
            )
        _seen_aliases[_alias] = _cls.KIND
del _seen_aliases, _cls, _alias  # clean up module namespace
