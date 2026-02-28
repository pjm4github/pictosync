"""
canvas/items.py

Graphics items for diagram annotation: rectangles, ellipses, lines, and text.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Optional, Tuple

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


def shape_with_handles(base_shape: QPainterPath, handle_positions: Dict[str, QPointF], handle_size: Optional[float] = None) -> QPainterPath:
    """Create a shape path that includes handle hit areas."""
    # Hit distance from settings. Default: 10.0 pixels
    if handle_size is None:
        handle_size = _get_hit_distance()
    result = QPainterPath(base_shape)
    half = handle_size / 2
    for pos in handle_positions.values():
        result.addRect(QRectF(pos.x() - half, pos.y() - half, handle_size, handle_size))
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
        # Text padding - using hardcoded default. Default: 4 pixels
        padding = 4
        self._label_item.setTextWidth(max(10, r.width() - 2 * padding))

        # Calculate text height after setting width (so wrapping is applied)
        text_height = self._label_item.boundingRect().height()
        available_height = r.height() - 2 * padding

        # Get vertical alignment from meta
        valign = getattr(self.meta, "text_valign", "top") if hasattr(self, "meta") else "top"

        if valign == "middle":
            y_pos = padding + (available_height - text_height) / 2
        elif valign == "bottom":
            y_pos = r.height() - padding - text_height
        else:  # top (default)
            y_pos = padding

        self._label_item.setPos(padding, max(padding, y_pos))

    def _update_label_text(self):
        lines = []
        align_map = {"left": "left", "center": "center", "right": "right"}

        # Get text spacing in em units (lines * 1em)
        spacing = getattr(self.meta, "text_spacing", 0.0) if hasattr(self, "meta") else 0.0
        margin_style = f"margin-bottom:{spacing}em;" if spacing > 0 else ""

        if self.meta.label:
            align = align_map.get(self.meta.label_align, "center")
            size = self.meta.label_size
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt; {margin_style}"><b>{self.meta.label}</b></p>')
        if self.meta.tech:
            align = align_map.get(self.meta.tech_align, "center")
            size = self.meta.tech_size
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt; {margin_style}"><i>[{self.meta.tech}]</i></p>')
        if self.meta.note:
            align = align_map.get(self.meta.note_align, "center")
            size = self.meta.note_size
            # No bottom margin on the last element
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt;">{self.meta.note}</p>')

        self._label_item.setHtml("".join(lines) if lines else "")
        self._label_item.setDefaultTextColor(self.text_color)
        # Update position after text changes (valign may need recalculation)
        self._update_label_position()

    def set_meta(self, meta: AnnotationMeta) -> None:
        self.meta = meta
        self._update_label_text()

    def setRect(self, r: QRectF):
        super().setRect(r)
        self._update_label_position()

    def _handle_points_scene(self) -> Dict[str, QPointF]:
        """Return handle positions in scene coordinates (corners and sides)."""
        r = self.rect()
        p = self.pos()
        cx = p.x() + r.left() + r.width() / 2
        cy = p.y() + r.top() + r.height() / 2
        return {
            "tl": QPointF(p.x() + r.left(),  p.y() + r.top()),
            "tr": QPointF(p.x() + r.right(), p.y() + r.top()),
            "bl": QPointF(p.x() + r.left(),  p.y() + r.bottom()),
            "br": QPointF(p.x() + r.right(), p.y() + r.bottom()),
            "t":  QPointF(cx, p.y() + r.top()),
            "b":  QPointF(cx, p.y() + r.bottom()),
            "l":  QPointF(p.x() + r.left(), cy),
            "r":  QPointF(p.x() + r.right(), cy),
        }

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

    def _hit_test_handle(self, scene_pt: QPointF) -> Optional[str]:
        if not self._should_paint_handles():
            return None
        handles = self._handle_points_scene()
        # Hit distance from settings. Default: 10.0 pixels
        hit_dist = _get_hit_distance()
        for k, hp in handles.items():
            if QLineF(scene_pt, hp).length() <= hit_dist:
                return k
        return None

    def hoverMoveEvent(self, event):
        h = self._hit_test_handle(event.scenePos())
        if h in ("tl", "br"):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif h in ("tr", "bl"):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif h in ("t", "b"):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif h in ("l", "r"):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            h = self._hit_test_handle(event.scenePos())
            if h:
                self._begin_resize_tracking()
                self._active_handle = h
                self._resizing = True
                self._press_scene = event.scenePos()
                self._start_pos = QPointF(self.pos())
                self._start_rect = QRectF(self.rect())
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resizing and self._active_handle and self._press_scene and self._start_pos and self._start_rect:
            cur = event.scenePos()
            dx = cur.x() - self._press_scene.x()
            dy = cur.y() - self._press_scene.y()

            x0 = self._start_pos.x()
            y0 = self._start_pos.y()
            w0 = self._start_rect.width()
            h0 = self._start_rect.height()

            left = x0
            top = y0
            right = x0 + w0
            bottom = y0 + h0

            if self._active_handle == "tl":
                left += dx
                top += dy
            elif self._active_handle == "tr":
                right += dx
                top += dy
            elif self._active_handle == "bl":
                left += dx
                bottom += dy
            elif self._active_handle == "br":
                right += dx
                bottom += dy
            elif self._active_handle == "t":
                top += dy
            elif self._active_handle == "b":
                bottom += dy
            elif self._active_handle == "l":
                left += dx
            elif self._active_handle == "r":
                right += dx

            # Minimum size from settings. Default: 5.0 pixels
            min_size = _get_min_size()
            if (right - left) < min_size:
                if self._active_handle in ("tl", "bl", "l"):
                    left = right - min_size
                else:
                    right = left + min_size

            if (bottom - top) < min_size:
                if self._active_handle in ("tl", "tr", "t"):
                    top = bottom - min_size
                else:
                    bottom = top + min_size

            new_w = right - left
            new_h = bottom - top

            self.setPos(QPointF(left, top))
            self.setRect(QRectF(0, 0, new_w, new_h))

            self._notify_changed()
            event.accept()
            return

        super().mouseMoveEvent(event)

    def shape(self) -> QPainterPath:
        """Return shape including handle areas when selected."""
        base = super().shape()
        if self._should_paint_handles():
            return shape_with_handles(base, self._handle_points_local())
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

    def mouseReleaseEvent(self, event):
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
        padding = 4 + self._adjust1 * 0.3  # Extra padding for rounded corners
        self._label_item.setTextWidth(max(10, self._width - 2 * padding))

        # Calculate text height after setting width (so wrapping is applied)
        text_height = self._label_item.boundingRect().height()
        available_height = self._height - 2 * padding

        # Get vertical alignment from meta
        valign = getattr(self.meta, "text_valign", "top") if hasattr(self, "meta") else "top"

        if valign == "middle":
            y_pos = padding + (available_height - text_height) / 2
        elif valign == "bottom":
            y_pos = self._height - padding - text_height
        else:  # top (default)
            y_pos = padding

        self._label_item.setPos(padding, max(padding, y_pos))

    def _update_label_text(self):
        lines = []
        align_map = {"left": "left", "center": "center", "right": "right"}

        # Get text spacing in em units (lines * 1em)
        spacing = getattr(self.meta, "text_spacing", 0.0) if hasattr(self, "meta") else 0.0
        margin_style = f"margin-bottom:{spacing}em;" if spacing > 0 else ""

        if self.meta.label:
            align = align_map.get(self.meta.label_align, "center")
            size = self.meta.label_size
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt; {margin_style}"><b>{self.meta.label}</b></p>')
        if self.meta.tech:
            align = align_map.get(self.meta.tech_align, "center")
            size = self.meta.tech_size
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt; {margin_style}"><i>[{self.meta.tech}]</i></p>')
        if self.meta.note:
            align = align_map.get(self.meta.note_align, "center")
            size = self.meta.note_size
            # No bottom margin on the last element
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt;">{self.meta.note}</p>')

        self._label_item.setHtml("".join(lines) if lines else "")
        self._label_item.setDefaultTextColor(self.text_color)
        # Update position after text changes (valign may need recalculation)
        self._update_label_position()

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

    def adjust1(self) -> float:
        return self._adjust1

    def set_adjust1(self, value: float):
        self._adjust1 = max(0, value)
        self._update_path()

    def _handle_points_scene(self) -> Dict[str, QPointF]:
        """Return handle positions in scene coordinates (corners and sides)."""
        p = self.pos()
        cx = p.x() + self._width / 2
        cy = p.y() + self._height / 2
        return {
            "tl": QPointF(p.x(), p.y()),
            "tr": QPointF(p.x() + self._width, p.y()),
            "bl": QPointF(p.x(), p.y() + self._height),
            "br": QPointF(p.x() + self._width, p.y() + self._height),
            "t":  QPointF(cx, p.y()),
            "b":  QPointF(cx, p.y() + self._height),
            "l":  QPointF(p.x(), cy),
            "r":  QPointF(p.x() + self._width, cy),
            "adjust1": QPointF(p.x() + self._adjust1, p.y()),  # Adjust1 (radius) control handle
        }

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

    def _hit_test_handle(self, scene_pt: QPointF) -> Optional[str]:
        if not self._should_paint_handles():
            return None
        handles = self._handle_points_scene()
        # Hit distance from settings. Default: 10.0 pixels
        hit_dist = _get_hit_distance()
        for k, hp in handles.items():
            if QLineF(scene_pt, hp).length() <= hit_dist:
                return k
        return None

    def hoverMoveEvent(self, event):
        h = self._hit_test_handle(event.scenePos())
        if h in ("tl", "br"):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif h in ("tr", "bl"):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif h in ("t", "b"):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif h in ("l", "r", "adjust1"):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            h = self._hit_test_handle(event.scenePos())
            if h:
                self._begin_resize_tracking()
                self._active_handle = h
                self._resizing = True
                self._press_scene = event.scenePos()
                self._start_pos = QPointF(self.pos())
                self._start_size = (self._width, self._height)
                self._start_adjust1 = self._adjust1
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resizing and self._active_handle and self._press_scene and self._start_pos and self._start_size:
            cur = event.scenePos()
            dx = cur.x() - self._press_scene.x()
            dy = cur.y() - self._press_scene.y()

            # Handle adjust1 (corner radius) adjustment separately
            if self._active_handle == "adjust1" and self._start_adjust1 is not None:
                new_adjust1 = self._start_adjust1 + dx
                # Clamp adjust1 between 0 and half of the smaller dimension
                max_adjust1 = min(self._width, self._height) / 2
                new_adjust1 = max(0, min(new_adjust1, max_adjust1))
                self._adjust1 = new_adjust1
                self._update_path()
                self._update_label_position()
                self._notify_changed()
                # Notify property panel of adjust1 change
                if MetaRoundedRectItem.on_adjust1_changed:
                    MetaRoundedRectItem.on_adjust1_changed(self, new_adjust1)
                event.accept()
                return

            x0 = self._start_pos.x()
            y0 = self._start_pos.y()
            w0, h0 = self._start_size

            left = x0
            top = y0
            right = x0 + w0
            bottom = y0 + h0

            if self._active_handle == "tl":
                left += dx
                top += dy
            elif self._active_handle == "tr":
                right += dx
                top += dy
            elif self._active_handle == "bl":
                left += dx
                bottom += dy
            elif self._active_handle == "br":
                right += dx
                bottom += dy
            elif self._active_handle == "t":
                top += dy
            elif self._active_handle == "b":
                bottom += dy
            elif self._active_handle == "l":
                left += dx
            elif self._active_handle == "r":
                right += dx

            # Minimum size from settings. Default: 5.0 pixels
            min_size = _get_min_size()
            if (right - left) < min_size:
                if self._active_handle in ("tl", "bl", "l"):
                    left = right - min_size
                else:
                    right = left + min_size

            if (bottom - top) < min_size:
                if self._active_handle in ("tl", "tr", "t"):
                    top = bottom - min_size
                else:
                    bottom = top + min_size

            new_w = right - left
            new_h = bottom - top

            self.setPos(QPointF(left, top))
            self._width = new_w
            self._height = new_h
            self._update_path()
            self._update_label_position()

            self._notify_changed()
            event.accept()
            return

        super().mouseMoveEvent(event)

    def shape(self) -> QPainterPath:
        """Return shape including handle areas when selected."""
        base = super().shape()
        if self._should_paint_handles():
            return shape_with_handles(base, self._handle_points_local())
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

            # Draw adjust1 handle in yellow
            # Handle size from settings. Default: 8.0 pixels
            handle_size = _get_handle_size()
            half = handle_size / 2
            painter.setPen(QPen(QColor(204, 153, 0), 1))  # Dark yellow border
            painter.setBrush(QBrush(QColor(255, 215, 0)))  # Gold/yellow fill
            painter.drawEllipse(QRectF(adjust1_handle_pos.x() - half, adjust1_handle_pos.y() - half,
                                       handle_size, handle_size))

    def mouseReleaseEvent(self, event):
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
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.prepareGeometryChange()
        return out

    def to_record(self) -> Dict[str, Any]:
        p = self.pos()
        rec = {
            "id": self.ann_id,
            "kind": "roundedrect",
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
        self._label_item.setDefaultTextColor(self.text_color)
        self._update_label_position()

    def _apply_pen_brush(self):
        pen = QPen(self.pen_color, self.pen_width)
        _apply_dash_style(pen, self.line_dash, self.dash_pattern_length, self.dash_solid_percent)
        self.setPen(pen)
        self.setBrush(QBrush(self.brush_color))

    def _update_label_position(self):
        r = self.rect()
        # Ellipse needs more padding to keep text inside the curved shape
        padding = max(8, r.width() * 0.1, r.height() * 0.1)
        self._label_item.setTextWidth(max(10, r.width() - 2 * padding))

        # Calculate text height after setting width (so wrapping is applied)
        text_height = self._label_item.boundingRect().height()
        available_height = r.height() - 2 * padding

        # Get vertical alignment from meta
        valign = getattr(self.meta, "text_valign", "top") if hasattr(self, "meta") else "top"

        if valign == "middle":
            y_pos = padding + (available_height - text_height) / 2
        elif valign == "bottom":
            y_pos = r.height() - padding - text_height
        else:  # top (default)
            y_pos = padding

        self._label_item.setPos(padding, max(padding, y_pos))

    def _update_label_text(self):
        lines = []
        align_map = {"left": "left", "center": "center", "right": "right"}

        # Get text spacing in em units (lines * 1em)
        spacing = getattr(self.meta, "text_spacing", 0.0) if hasattr(self, "meta") else 0.0
        margin_style = f"margin-bottom:{spacing}em;" if spacing > 0 else ""

        if self.meta.label:
            align = align_map.get(self.meta.label_align, "center")
            size = self.meta.label_size
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt; {margin_style}"><b>{self.meta.label}</b></p>')
        if self.meta.tech:
            align = align_map.get(self.meta.tech_align, "center")
            size = self.meta.tech_size
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt; {margin_style}"><i>[{self.meta.tech}]</i></p>')
        if self.meta.note:
            align = align_map.get(self.meta.note_align, "center")
            size = self.meta.note_size
            # No bottom margin on the last element
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt;">{self.meta.note}</p>')

        self._label_item.setHtml("".join(lines) if lines else "")
        self._label_item.setDefaultTextColor(self.text_color)
        # Update position after text changes (valign may need recalculation)
        self._update_label_position()

    def set_meta(self, meta: AnnotationMeta) -> None:
        self.meta = meta
        self._update_label_text()

    def setRect(self, r: QRectF):
        super().setRect(r)
        self._update_label_position()

    def _handle_points_scene(self) -> Dict[str, QPointF]:
        """Return handle positions in scene coordinates (corners and sides)."""
        r = self.rect()
        p = self.pos()
        cx = p.x() + r.left() + r.width() / 2
        cy = p.y() + r.top() + r.height() / 2
        return {
            "tl": QPointF(p.x() + r.left(),  p.y() + r.top()),
            "tr": QPointF(p.x() + r.right(), p.y() + r.top()),
            "bl": QPointF(p.x() + r.left(),  p.y() + r.bottom()),
            "br": QPointF(p.x() + r.right(), p.y() + r.bottom()),
            "t":  QPointF(cx, p.y() + r.top()),
            "b":  QPointF(cx, p.y() + r.bottom()),
            "l":  QPointF(p.x() + r.left(), cy),
            "r":  QPointF(p.x() + r.right(), cy),
        }

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

    def _hit_test_handle(self, scene_pt: QPointF) -> Optional[str]:
        if not self._should_paint_handles():
            return None
        handles = self._handle_points_scene()
        # Hit distance from settings. Default: 10.0 pixels
        hit_dist = _get_hit_distance()
        for k, hp in handles.items():
            if QLineF(scene_pt, hp).length() <= hit_dist:
                return k
        return None

    def hoverMoveEvent(self, event):
        h = self._hit_test_handle(event.scenePos())
        if h in ("tl", "br"):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif h in ("tr", "bl"):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif h in ("t", "b"):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif h in ("l", "r"):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            h = self._hit_test_handle(event.scenePos())
            if h:
                self._begin_resize_tracking()
                self._active_handle = h
                self._resizing = True
                self._press_scene = event.scenePos()
                self._start_pos = QPointF(self.pos())
                self._start_rect = QRectF(self.rect())
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resizing and self._active_handle and self._press_scene and self._start_pos and self._start_rect:
            cur = event.scenePos()
            dx = cur.x() - self._press_scene.x()
            dy = cur.y() - self._press_scene.y()

            x0 = self._start_pos.x()
            y0 = self._start_pos.y()
            w0 = self._start_rect.width()
            h0 = self._start_rect.height()

            left = x0
            top = y0
            right = x0 + w0
            bottom = y0 + h0

            if self._active_handle == "tl":
                left += dx
                top += dy
            elif self._active_handle == "tr":
                right += dx
                top += dy
            elif self._active_handle == "bl":
                left += dx
                bottom += dy
            elif self._active_handle == "br":
                right += dx
                bottom += dy
            elif self._active_handle == "t":
                top += dy
            elif self._active_handle == "b":
                bottom += dy
            elif self._active_handle == "l":
                left += dx
            elif self._active_handle == "r":
                right += dx

            # Minimum size from settings. Default: 5.0 pixels
            min_size = _get_min_size()
            if (right - left) < min_size:
                if self._active_handle in ("tl", "bl", "l"):
                    left = right - min_size
                else:
                    right = left + min_size

            if (bottom - top) < min_size:
                if self._active_handle in ("tl", "tr", "t"):
                    top = bottom - min_size
                else:
                    bottom = top + min_size

            new_w = right - left
            new_h = bottom - top

            self.setPos(QPointF(left, top))
            self.setRect(QRectF(0, 0, new_w, new_h))

            self._notify_changed()
            event.accept()
            return

        super().mouseMoveEvent(event)

    def shape(self) -> QPainterPath:
        """Return shape including handle areas when selected."""
        base = super().shape()
        if self._should_paint_handles():
            return shape_with_handles(base, self._handle_points_local())
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

    def mouseReleaseEvent(self, event):
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
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.prepareGeometryChange()
        return out

    def to_record(self) -> Dict[str, Any]:
        p = self.pos()
        r = self.rect()
        rec = {
            "id": self.ann_id,
            "kind": "ellipse",
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
        return rec


class MetaLineItem(QGraphicsLineItem, MetaMixin, LinkedMixin):
    """Line item with draggable endpoints and optional arrowheads."""

    KIND = "line"
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
        self.text_color = QColor(self.pen_color)  # Default text color matches border
        self.arrow_mode = self.ARROW_NONE
        self._apply_pen()

        self._drag_end: Optional[str] = None  # "p1" or "p2"
        self._drag_text_box: Optional[str] = None  # "tl", "tr", "bl", "br" for text box corners

        # Text box properties (local coordinates relative to line midpoint)
        self._text_box_rect: Optional[QRectF] = None  # Will be computed from meta

        # Embedded text labels for label, tech, and note (stacked vertically)
        self._label_item = QGraphicsTextItem(self)
        self._label_item.setDefaultTextColor(self.text_color)
        self._label_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self._tech_item = QGraphicsTextItem(self)
        self._tech_item.setDefaultTextColor(self.text_color)
        self._tech_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self._note_item = QGraphicsTextItem(self)
        self._note_item.setDefaultTextColor(self.text_color)
        self._note_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self._update_label_position()

    def _apply_pen(self):
        pen = QPen(self.pen_color, self.pen_width)
        _apply_dash_style(pen, self.line_dash, self.dash_pattern_length, self.dash_solid_percent)
        self.setPen(pen)

    def _update_label_position(self):
        ln = self.line()
        mid_x = (ln.x1() + ln.x2()) / 2
        mid_y = (ln.y1() + ln.y2()) / 2

        # Check if we have a text bounding box width (height is optional)
        has_text_box = (hasattr(self, "meta") and self.meta.text_box_width > 0)

        if has_text_box:
            # Use the text box width for wrapping
            box_w = self.meta.text_box_width
            padding = 4

            # Set text width for wrapping - this is the key for text wrapping
            text_width = box_w - 2 * padding
            self._label_item.setTextWidth(text_width)
            self._tech_item.setTextWidth(text_width)
            self._note_item.setTextWidth(text_width)

            # Calculate total height of visible text items
            total_height = 0
            if hasattr(self, "meta"):
                if self.meta.label and self._label_item.isVisible():
                    total_height += self._label_item.boundingRect().height()
                if self.meta.tech and self._tech_item.isVisible():
                    total_height += self._tech_item.boundingRect().height()
                if self.meta.note and self._note_item.isVisible():
                    total_height += self._note_item.boundingRect().height()

            # Use text_box_height if set, otherwise use actual content height
            if self.meta.text_box_height > 0:
                box_h = self.meta.text_box_height
            else:
                box_h = total_height + 2 * padding

            # Determine text block alignment relative to line midpoint
            # Get the dominant alignment (use label_align as primary)
            block_align = "center"
            if hasattr(self, "meta"):
                block_align = self.meta.label_align

            # Position the text box based on block alignment
            # All alignments are vertically centered on the line midpoint (middle-left, middle-center, middle-right)
            box_y = mid_y - box_h / 2  # Vertically centered on midpoint

            if block_align == "left":
                # Text block is to the LEFT of the line center (right edge at midpoint)
                box_x = mid_x - box_w
            elif block_align == "right":
                # Text block is to the RIGHT of the line center (left edge at midpoint)
                box_x = mid_x
            else:  # center
                # Text block is centered on line horizontally
                box_x = mid_x - box_w / 2

            self._text_box_rect = QRectF(box_x, box_y, box_w, box_h)

            # Position text items inside the box
            current_y = box_y + padding

            if hasattr(self, "meta"):
                if self.meta.label and self._label_item.isVisible():
                    self._label_item.setPos(box_x + padding, current_y)
                    current_y += self._label_item.boundingRect().height()

                if self.meta.tech and self._tech_item.isVisible():
                    self._tech_item.setPos(box_x + padding, current_y)
                    current_y += self._tech_item.boundingRect().height()

                if self.meta.note and self._note_item.isVisible():
                    self._note_item.setPos(box_x + padding, current_y)
        else:
            # No text box - use original positioning logic
            self._text_box_rect = None

            # Remove text width constraint
            self._label_item.setTextWidth(-1)
            self._tech_item.setTextWidth(-1)
            self._note_item.setTextWidth(-1)

            # Gather visible items (those with text) and calculate total height
            visible_items = []
            if hasattr(self, "meta"):
                if self.meta.label:
                    visible_items.append((self._label_item, self.meta.label_align))
                if self.meta.tech:
                    visible_items.append((self._tech_item, self.meta.tech_align))
                if self.meta.note:
                    visible_items.append((self._note_item, self.meta.note_align))

            if not visible_items:
                return

            # Calculate total height of all visible text items
            total_height = sum(item.boundingRect().height() for item, _ in visible_items)

            # Vertically center on the line midpoint
            current_y = mid_y - total_height / 2

            for item, align in visible_items:
                item_width = item.boundingRect().width()
                item_height = item.boundingRect().height()

                # Position based on alignment relative to line center (middle-left, middle-center, middle-right)
                if align == "left":
                    # Text ends at center point
                    pos_x = mid_x - item_width
                elif align == "right":
                    # Text starts at center point
                    pos_x = mid_x
                else:  # center
                    # Text centered on center point
                    pos_x = mid_x - item_width / 2

                item.setPos(pos_x, current_y)
                current_y += item_height

    def _update_label_text(self):
        # Check if we have a text box - this affects text justification
        has_text_box = self.meta.text_box_width > 0

        # Determine text justification within the box based on block alignment
        # - "left" block alignment = text right-justified within box
        # - "right" block alignment = text left-justified within box
        # - "center" block alignment = text centered within box
        def get_text_align(block_align: str) -> str:
            if has_text_box:
                if block_align == "left":
                    return "right"  # Text right-justified when box is left of line
                elif block_align == "right":
                    return "left"   # Text left-justified when box is right of line
                else:
                    return "center"
            else:
                return "center"  # Default for no text box

        # Get hex color for HTML
        text_hex = "#{:02X}{:02X}{:02X}".format(
            self.text_color.red(), self.text_color.green(), self.text_color.blue()
        )

        # Update label text item
        if self.meta.label:
            text_align = get_text_align(self.meta.label_align)
            size = self.meta.label_size
            html = f'<p style="text-align:{text_align}; font-size:{size}pt; color:{text_hex}; margin:0;"><b>{self.meta.label}</b></p>'
            self._label_item.setHtml(html)
            self._label_item.setVisible(True)
        else:
            self._label_item.setPlainText("")
            self._label_item.setVisible(False)

        # Update tech text item
        if self.meta.tech:
            text_align = get_text_align(self.meta.tech_align)
            size = self.meta.tech_size
            html = f'<p style="text-align:{text_align}; font-size:{size}pt; color:{text_hex}; margin:0;"><i>[{self.meta.tech}]</i></p>'
            self._tech_item.setHtml(html)
            self._tech_item.setVisible(True)
        else:
            self._tech_item.setPlainText("")
            self._tech_item.setVisible(False)

        # Update note text item
        if self.meta.note:
            text_align = get_text_align(self.meta.note_align)
            size = self.meta.note_size
            html = f'<p style="text-align:{text_align}; font-size:{size}pt; color:{text_hex}; margin:0;">{self.meta.note}</p>'
            self._note_item.setHtml(html)
            self._note_item.setVisible(True)
        else:
            self._note_item.setPlainText("")
            self._note_item.setVisible(False)

        # Update position after text changes (alignment may have changed)
        self._update_label_position()

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

        # Draw text bounding box if present - with opaque fill to obscure the line
        if self._text_box_rect is not None:
            # Draw opaque white background to cover the line underneath
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 255)))  # Opaque white fill
            painter.drawRect(self._text_box_rect)
            # Draw subtle border
            box_pen = QPen(QColor(200, 200, 200), 1, Qt.PenStyle.SolidLine)
            painter.setPen(box_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self._text_box_rect)

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
            self._end_resize_tracking()
            self._drag_end = None
            self._notify_changed()
            event.accept()
            return
        super().mouseReleaseEvent(event)

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
            "geom": {
                "x1": round1(p.x() + ln.x1()),
                "y1": round1(p.y() + ln.y1()),
                "x2": round1(p.x() + ln.x2()),
                "y2": round1(p.y() + ln.y2()),
            },
            **self._meta_dict(self.meta),
            "style": style,
        }
        # Include z-index if set
        z = self.zValue()
        if z != 0:
            rec["z"] = int(z)
        return rec


class MetaTextItem(QGraphicsTextItem, MetaMixin, LinkedMixin):
    """Text item with inline editing and configurable font."""

    KIND = "text"
    KIND_ALIASES = frozenset(k for k, v in KIND_ALIAS_MAP.items() if v == "text")

    # Class-level callbacks for focus events (set by MainWindow)
    on_editing_started = None  # Called when text editing begins
    on_editing_finished = None  # Called when text editing ends
    on_text_changed = None  # Called when text content changes during editing
    on_text_edit_finished = None  # Called with (item, old_text, new_text) for undo

    # Class-level default text color (set by MainWindow based on theme)
    default_text_color = QColor("#1E293B")  # Default to dark (Tailwind slate-800)

    def __init__(self, x: float, y: float, text: str, ann_id: str, on_change=None):
        QGraphicsTextItem.__init__(self, text)
        MetaMixin.__init__(self)
        LinkedMixin.__init__(self, ann_id, on_change)

        self.kind ="text"
        # Store initial text in meta.note
        self.meta.note = text
        self.setPos(QPointF(x, y))
        self.setData(ANN_ID_KEY, ann_id)

        # Start with no text interaction - only select/move
        # Double-click will enable editing
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        # Use class-level default text color (contrasts with canvas background)
        self.text_color = QColor(MetaTextItem.default_text_color)
        self.text_size_pt = 12  # default
        self._editing = False
        self._apply_text_style()

        # Connect document changes to sync with properties
        self.document().contentsChanged.connect(self._on_contents_changed)

    def _apply_text_style(self):
        self.setDefaultTextColor(self.text_color)
        f = self.font()
        f.setPointSizeF(float(self.text_size_pt))
        self.setFont(f)

    def _on_contents_changed(self):
        """Called when text content changes during editing."""
        if self._editing:
            self.meta.note = self.toPlainText()
            if MetaTextItem.on_text_changed:
                MetaTextItem.on_text_changed(self.toPlainText())

    def set_meta(self, meta: AnnotationMeta) -> None:
        """Set metadata and update displayed text from meta.note."""
        self.meta = meta
        if meta.note and meta.note != self.toPlainText():
            # Block contentsChanged signal during external update
            self.document().blockSignals(True)
            self.setPlainText(meta.note)
            self.document().blockSignals(False)

    def itemChange(self, change, value):
        out = super().itemChange(change, value)
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self._notify_changed()
        return out

    def mouseDoubleClickEvent(self, event):
        """Double-click to enter edit mode."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._start_editing()
            # Position cursor at click location
            super().mouseDoubleClickEvent(event)
        else:
            super().mouseDoubleClickEvent(event)

    def _start_editing(self):
        """Enter text editing mode."""
        if self._editing:
            return
        self._editing = True
        self._text_before_edit = self.toPlainText()
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        # Select all text for easy replacement
        cursor = self.textCursor()
        cursor.select(cursor.SelectionType.Document)
        self.setTextCursor(cursor)
        if MetaTextItem.on_editing_started:
            MetaTextItem.on_editing_started()

    def _stop_editing(self):
        """Exit text editing mode."""
        if not self._editing:
            return
        self._editing = False
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        # Clear selection
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)
        # Sync the displayed text to meta.note
        new_text = self.toPlainText()
        self.meta.note = new_text
        try:
            self.text_size_pt = float(self.font().pointSizeF())
        except Exception:
            pass
        self._notify_changed()
        # Fire text edit undo callback if text changed
        old_text = getattr(self, '_text_before_edit', None)
        if old_text is not None and old_text != new_text:
            if MetaTextItem.on_text_edit_finished:
                MetaTextItem.on_text_edit_finished(self, old_text, new_text)
        self._text_before_edit = None
        if MetaTextItem.on_editing_finished:
            MetaTextItem.on_editing_finished()

    def focusOutEvent(self, event):
        """Handle focus out - exit edit mode."""
        super().focusOutEvent(event)
        self._stop_editing()

    def to_record(self) -> Dict[str, Any]:
        try:
            self.text_size_pt = float(self.font().pointSizeF())
        except Exception:
            pass

        p = self.pos()
        # Sync displayed text content into meta.note before serializing
        self.meta.note = self.toPlainText()
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
        padding = 4 + self._width * self._adjust1 * 0.5
        self._label_item.setTextWidth(max(10, self._width - 2 * padding))

        text_height = self._label_item.boundingRect().height()
        available_height = self._height - 2 * padding

        valign = getattr(self.meta, "text_valign", "top") if hasattr(self, "meta") else "top"

        if valign == "middle":
            y_pos = padding + (available_height - text_height) / 2
        elif valign == "bottom":
            y_pos = self._height - padding - text_height
        else:
            y_pos = padding

        self._label_item.setPos(padding, max(padding, y_pos))

    def _update_label_text(self):
        lines = []
        align_map = {"left": "left", "center": "center", "right": "right"}

        spacing = getattr(self.meta, "text_spacing", 0.0) if hasattr(self, "meta") else 0.0
        margin_style = f"margin-bottom:{spacing}em;" if spacing > 0 else ""

        if self.meta.label:
            align = align_map.get(self.meta.label_align, "center")
            size = self.meta.label_size
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt; {margin_style}"><b>{self.meta.label}</b></p>')
        if self.meta.tech:
            align = align_map.get(self.meta.tech_align, "center")
            size = self.meta.tech_size
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt; {margin_style}"><i>[{self.meta.tech}]</i></p>')
        if self.meta.note:
            align = align_map.get(self.meta.note_align, "center")
            size = self.meta.note_size
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt;">{self.meta.note}</p>')

        self._label_item.setHtml("".join(lines) if lines else "")
        self._label_item.setDefaultTextColor(self.text_color)
        self._update_label_position()

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

    def adjust1(self) -> float:
        return self._adjust1

    def set_adjust1(self, value: float):
        self._adjust1 = max(0.0, min(0.5, value))
        self._update_path()

    def _handle_points_scene(self) -> Dict[str, QPointF]:
        p = self.pos()
        cx = p.x() + self._width / 2
        cy = p.y() + self._height / 2
        return {
            "tl": QPointF(p.x(), p.y()),
            "tr": QPointF(p.x() + self._width, p.y()),
            "bl": QPointF(p.x(), p.y() + self._height),
            "br": QPointF(p.x() + self._width, p.y() + self._height),
            "t":  QPointF(cx, p.y()),
            "b":  QPointF(cx, p.y() + self._height),
            "l":  QPointF(p.x(), cy),
            "r":  QPointF(p.x() + self._width, cy),
            "adjust1": QPointF(p.x() + self._width * self._adjust1, p.y()),  # Upper left vertex
        }

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

    def _hit_test_handle(self, scene_pt: QPointF) -> Optional[str]:
        if not self._should_paint_handles():
            return None
        handles = self._handle_points_scene()
        hit_dist = _get_hit_distance()
        for k, hp in handles.items():
            if QLineF(scene_pt, hp).length() <= hit_dist:
                return k
        return None

    def hoverMoveEvent(self, event):
        h = self._hit_test_handle(event.scenePos())
        if h in ("tl", "br"):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif h in ("tr", "bl"):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif h in ("t", "b"):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif h in ("l", "r", "adjust1"):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            h = self._hit_test_handle(event.scenePos())
            if h:
                self._begin_resize_tracking()
                self._active_handle = h
                self._resizing = True
                self._press_scene = event.scenePos()
                self._start_pos = QPointF(self.pos())
                self._start_size = (self._width, self._height)
                self._start_adjust1 = self._adjust1
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resizing and self._active_handle and self._press_scene and self._start_pos and self._start_size:
            cur = event.scenePos()
            dx = cur.x() - self._press_scene.x()
            dy = cur.y() - self._press_scene.y()

            # Handle adjust1 (indent) adjustment
            if self._active_handle == "adjust1" and self._start_adjust1 is not None:
                # Dragging upper left vertex right increases adjust1 (makes top/bottom edges shorter)
                new_adjust1_px = self._width * self._start_adjust1 + dx
                new_adjust1 = new_adjust1_px / self._width if self._width > 0 else 0.25
                new_adjust1 = max(0.0, min(0.5, new_adjust1))
                self._adjust1 = new_adjust1
                self._update_path()
                self._update_label_position()
                self._notify_changed()
                if MetaHexagonItem.on_adjust1_changed:
                    MetaHexagonItem.on_adjust1_changed(self, new_adjust1)
                event.accept()
                return

            x0 = self._start_pos.x()
            y0 = self._start_pos.y()
            w0, h0 = self._start_size

            left = x0
            top = y0
            right = x0 + w0
            bottom = y0 + h0

            if self._active_handle == "tl":
                left += dx
                top += dy
            elif self._active_handle == "tr":
                right += dx
                top += dy
            elif self._active_handle == "bl":
                left += dx
                bottom += dy
            elif self._active_handle == "br":
                right += dx
                bottom += dy
            elif self._active_handle == "t":
                top += dy
            elif self._active_handle == "b":
                bottom += dy
            elif self._active_handle == "l":
                left += dx
            elif self._active_handle == "r":
                right += dx

            min_size = _get_min_size()
            if (right - left) < min_size:
                if self._active_handle in ("tl", "bl", "l"):
                    left = right - min_size
                else:
                    right = left + min_size

            if (bottom - top) < min_size:
                if self._active_handle in ("tl", "tr", "t"):
                    top = bottom - min_size
                else:
                    bottom = top + min_size

            new_w = right - left
            new_h = bottom - top

            self.setPos(QPointF(left, top))
            self._width = new_w
            self._height = new_h
            self._update_path()
            self._update_label_position()

            self._notify_changed()
            event.accept()
            return

        super().mouseMoveEvent(event)

    def shape(self) -> QPainterPath:
        base = super().shape()
        if self._should_paint_handles():
            return shape_with_handles(base, self._handle_points_local())
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

            # Draw adjust1 handle in yellow
            handle_size = _get_handle_size()
            half = handle_size / 2
            painter.setPen(QPen(QColor(204, 153, 0), 1))
            painter.setBrush(QBrush(QColor(255, 215, 0)))
            painter.drawEllipse(QRectF(adjust1_handle_pos.x() - half, adjust1_handle_pos.y() - half,
                                       handle_size, handle_size))

    def mouseReleaseEvent(self, event):
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
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.prepareGeometryChange()
        return out

    def to_record(self) -> Dict[str, Any]:
        p = self.pos()
        rec = {
            "id": self.ann_id,
            "kind": "hexagon",
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
        cap_h = self._height * self._adjust1
        padding = 4
        self._label_item.setTextWidth(max(10, self._width - 2 * padding))

        text_height = self._label_item.boundingRect().height()
        # Text goes in body area, below top cap
        available_height = self._height - cap_h * 2 - 2 * padding

        valign = getattr(self.meta, "text_valign", "top") if hasattr(self, "meta") else "top"

        if valign == "middle":
            y_pos = cap_h + padding + (available_height - text_height) / 2
        elif valign == "bottom":
            y_pos = self._height - cap_h - padding - text_height
        else:
            y_pos = cap_h + padding

        self._label_item.setPos(padding, max(cap_h + padding, y_pos))

    def _update_label_text(self):
        lines = []
        align_map = {"left": "left", "center": "center", "right": "right"}

        spacing = getattr(self.meta, "text_spacing", 0.0) if hasattr(self, "meta") else 0.0
        margin_style = f"margin-bottom:{spacing}em;" if spacing > 0 else ""

        if self.meta.label:
            align = align_map.get(self.meta.label_align, "center")
            size = self.meta.label_size
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt; {margin_style}"><b>{self.meta.label}</b></p>')
        if self.meta.tech:
            align = align_map.get(self.meta.tech_align, "center")
            size = self.meta.tech_size
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt; {margin_style}"><i>[{self.meta.tech}]</i></p>')
        if self.meta.note:
            align = align_map.get(self.meta.note_align, "center")
            size = self.meta.note_size
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt;">{self.meta.note}</p>')

        self._label_item.setHtml("".join(lines) if lines else "")
        self._label_item.setDefaultTextColor(self.text_color)
        self._update_label_position()

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

    def adjust1(self) -> float:
        return self._adjust1

    def set_adjust1(self, value: float):
        self._adjust1 = max(0.1, min(0.5, value))
        self._update_path()
        self._update_label_position()

    def _handle_points_scene(self) -> Dict[str, QPointF]:
        p = self.pos()
        cx = p.x() + self._width / 2
        cy = p.y() + self._height / 2
        cap_h = self._height * self._adjust1
        return {
            "tl": QPointF(p.x(), p.y()),
            "tr": QPointF(p.x() + self._width, p.y()),
            "bl": QPointF(p.x(), p.y() + self._height),
            "br": QPointF(p.x() + self._width, p.y() + self._height),
            "t":  QPointF(cx, p.y()),
            "b":  QPointF(cx, p.y() + self._height),
            "l":  QPointF(p.x(), cy),
            "r":  QPointF(p.x() + self._width, cy),
            "adjust1": QPointF(p.x() + self._width, p.y() + cap_h),  # Right side of top ellipse
        }

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

    def _hit_test_handle(self, scene_pt: QPointF) -> Optional[str]:
        if not self._should_paint_handles():
            return None
        handles = self._handle_points_scene()
        hit_dist = _get_hit_distance()
        for k, hp in handles.items():
            if QLineF(scene_pt, hp).length() <= hit_dist:
                return k
        return None

    def hoverMoveEvent(self, event):
        h = self._hit_test_handle(event.scenePos())
        if h in ("tl", "br"):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif h in ("tr", "bl"):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif h in ("t", "b", "adjust1"):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif h in ("l", "r"):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            h = self._hit_test_handle(event.scenePos())
            if h:
                self._begin_resize_tracking()
                self._active_handle = h
                self._resizing = True
                self._press_scene = event.scenePos()
                self._start_pos = QPointF(self.pos())
                self._start_size = (self._width, self._height)
                self._start_adjust1 = self._adjust1
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resizing and self._active_handle and self._press_scene and self._start_pos and self._start_size:
            cur = event.scenePos()
            dx = cur.x() - self._press_scene.x()
            dy = cur.y() - self._press_scene.y()

            # Handle adjust1 (cap ratio) adjustment
            if self._active_handle == "adjust1" and self._start_adjust1 is not None:
                new_cap_h = self._height * self._start_adjust1 + dy
                new_ratio = new_cap_h / self._height if self._height > 0 else 0.15
                new_ratio = max(0.1, min(0.5, new_ratio))
                self._adjust1 = new_ratio
                self._update_path()
                self._update_label_position()
                self._notify_changed()
                if MetaCylinderItem.on_adjust1_changed:
                    MetaCylinderItem.on_adjust1_changed(self, new_ratio)
                event.accept()
                return

            x0 = self._start_pos.x()
            y0 = self._start_pos.y()
            w0, h0 = self._start_size

            left = x0
            top = y0
            right = x0 + w0
            bottom = y0 + h0

            if self._active_handle == "tl":
                left += dx
                top += dy
            elif self._active_handle == "tr":
                right += dx
                top += dy
            elif self._active_handle == "bl":
                left += dx
                bottom += dy
            elif self._active_handle == "br":
                right += dx
                bottom += dy
            elif self._active_handle == "t":
                top += dy
            elif self._active_handle == "b":
                bottom += dy
            elif self._active_handle == "l":
                left += dx
            elif self._active_handle == "r":
                right += dx

            min_size = _get_min_size()
            if (right - left) < min_size:
                if self._active_handle in ("tl", "bl", "l"):
                    left = right - min_size
                else:
                    right = left + min_size

            if (bottom - top) < min_size:
                if self._active_handle in ("tl", "tr", "t"):
                    top = bottom - min_size
                else:
                    bottom = top + min_size

            new_w = right - left
            new_h = bottom - top

            self.setPos(QPointF(left, top))
            self._width = new_w
            self._height = new_h
            self._update_path()
            self._update_label_position()

            self._notify_changed()
            event.accept()
            return

        super().mouseMoveEvent(event)

    def shape(self) -> QPainterPath:
        base = super().shape()
        if self._should_paint_handles():
            return shape_with_handles(base, self._handle_points_local())
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

            # Draw adjust1 handle in yellow
            handle_size = _get_handle_size()
            half = handle_size / 2
            painter.setPen(QPen(QColor(204, 153, 0), 1))
            painter.setBrush(QBrush(QColor(255, 215, 0)))
            painter.drawEllipse(QRectF(adjust1_handle_pos.x() - half, adjust1_handle_pos.y() - half,
                                       handle_size, handle_size))

    def mouseReleaseEvent(self, event):
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
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.prepareGeometryChange()
        return out

    def to_record(self) -> Dict[str, Any]:
        p = self.pos()
        rec = {
            "id": self.ann_id,
            "kind": "cylinder",
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
        shaft_margin = self._height * (1 - self._adjust1) / 2
        head_x = self._width - self._adjust2
        padding = 4
        # Text goes in the shaft area
        self._label_item.setTextWidth(max(10, head_x - 2 * padding))

        text_height = self._label_item.boundingRect().height()
        shaft_height = self._height * self._adjust1

        valign = getattr(self.meta, "text_valign", "top") if hasattr(self, "meta") else "top"

        if valign == "middle":
            y_pos = shaft_margin + (shaft_height - text_height) / 2
        elif valign == "bottom":
            y_pos = self._height - shaft_margin - padding - text_height
        else:
            y_pos = shaft_margin + padding

        self._label_item.setPos(padding, max(shaft_margin + padding, y_pos))

    def _update_label_text(self):
        lines = []
        align_map = {"left": "left", "center": "center", "right": "right"}

        spacing = getattr(self.meta, "text_spacing", 0.0) if hasattr(self, "meta") else 0.0
        margin_style = f"margin-bottom:{spacing}em;" if spacing > 0 else ""

        if self.meta.label:
            align = align_map.get(self.meta.label_align, "center")
            size = self.meta.label_size
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt; {margin_style}"><b>{self.meta.label}</b></p>')
        if self.meta.tech:
            align = align_map.get(self.meta.tech_align, "center")
            size = self.meta.tech_size
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt; {margin_style}"><i>[{self.meta.tech}]</i></p>')
        if self.meta.note:
            align = align_map.get(self.meta.note_align, "center")
            size = self.meta.note_size
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt;">{self.meta.note}</p>')

        self._label_item.setHtml("".join(lines) if lines else "")
        self._label_item.setDefaultTextColor(self.text_color)
        self._update_label_position()

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

    def adjust2(self) -> float:
        return self._adjust2

    def set_adjust2(self, value: float):
        self._adjust2 = max(10, min(self._width * 0.8, value))
        self._update_path()
        self._update_label_position()

    def adjust1(self) -> float:
        return self._adjust1

    def set_adjust1(self, value: float):
        self._adjust1 = max(0.2, min(0.9, value))
        self._update_path()
        self._update_label_position()

    def _handle_points_scene(self) -> Dict[str, QPointF]:
        p = self.pos()
        cx = p.x() + self._width / 2
        cy = p.y() + self._height / 2
        head_x = self._width - self._adjust2
        shaft_margin = self._height * (1 - self._adjust1) / 2
        return {
            "tl": QPointF(p.x(), p.y()),
            "tr": QPointF(p.x() + self._width, p.y()),
            "bl": QPointF(p.x(), p.y() + self._height),
            "br": QPointF(p.x() + self._width, p.y() + self._height),
            "t":  QPointF(cx, p.y()),
            "b":  QPointF(cx, p.y() + self._height),
            "l":  QPointF(p.x(), cy),
            "r":  QPointF(p.x() + self._width, cy),
            "adjust2": QPointF(p.x() + head_x, p.y() + shaft_margin),  # Junction of head and shaft
            "adjust1": QPointF(p.x(), p.y() + shaft_margin),  # Left edge at shaft top
        }

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

    def _hit_test_handle(self, scene_pt: QPointF) -> Optional[str]:
        if not self._should_paint_handles():
            return None
        handles = self._handle_points_scene()
        hit_dist = _get_hit_distance()
        for k, hp in handles.items():
            if QLineF(scene_pt, hp).length() <= hit_dist:
                return k
        return None

    def hoverMoveEvent(self, event):
        h = self._hit_test_handle(event.scenePos())
        if h in ("tl", "br"):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif h in ("tr", "bl"):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif h in ("t", "b", "adjust1"):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif h in ("l", "r", "adjust2"):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            h = self._hit_test_handle(event.scenePos())
            if h:
                self._begin_resize_tracking()
                self._active_handle = h
                self._resizing = True
                self._press_scene = event.scenePos()
                self._start_pos = QPointF(self.pos())
                self._start_size = (self._width, self._height)
                self._start_adjust2 = self._adjust2
                self._start_adjust1 = self._adjust1
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resizing and self._active_handle and self._press_scene and self._start_pos and self._start_size:
            cur = event.scenePos()
            dx = cur.x() - self._press_scene.x()
            dy = cur.y() - self._press_scene.y()

            # Handle adjust2 (head length) adjustment
            if self._active_handle == "adjust2" and self._start_adjust2 is not None:
                new_adjust2 = self._start_adjust2 - dx  # Moving left increases head length
                new_adjust2 = max(10, min(self._width * 0.8, new_adjust2))
                self._adjust2 = new_adjust2
                self._update_path()
                self._update_label_position()
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
                self._notify_changed()
                if MetaBlockArrowItem.on_adjust1_changed:
                    MetaBlockArrowItem.on_adjust1_changed(self, new_adjust1)
                event.accept()
                return

            x0 = self._start_pos.x()
            y0 = self._start_pos.y()
            w0, h0 = self._start_size

            left = x0
            top = y0
            right = x0 + w0
            bottom = y0 + h0

            if self._active_handle == "tl":
                left += dx
                top += dy
            elif self._active_handle == "tr":
                right += dx
                top += dy
            elif self._active_handle == "bl":
                left += dx
                bottom += dy
            elif self._active_handle == "br":
                right += dx
                bottom += dy
            elif self._active_handle == "t":
                top += dy
            elif self._active_handle == "b":
                bottom += dy
            elif self._active_handle == "l":
                left += dx
            elif self._active_handle == "r":
                right += dx

            min_size = _get_min_size()
            if (right - left) < min_size:
                if self._active_handle in ("tl", "bl", "l"):
                    left = right - min_size
                else:
                    right = left + min_size

            if (bottom - top) < min_size:
                if self._active_handle in ("tl", "tr", "t"):
                    top = bottom - min_size
                else:
                    bottom = top + min_size

            new_w = right - left
            new_h = bottom - top

            self.setPos(QPointF(left, top))
            self._width = new_w
            self._height = new_h
            self._adjust2 = min(self._adjust2, new_w * 0.8)
            self._update_path()
            self._update_label_position()

            self._notify_changed()
            event.accept()
            return

        super().mouseMoveEvent(event)

    def shape(self) -> QPainterPath:
        base = super().shape()
        if self._should_paint_handles():
            return shape_with_handles(base, self._handle_points_local())
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
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.prepareGeometryChange()
        return out

    def to_record(self) -> Dict[str, Any]:
        p = self.pos()
        rec = {
            "id": self.ann_id,
            "kind": "blockarrow",
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

        # Relative points (0-1 within bounding box)
        if points and len(points) >= 3:
            self._rel_points = [[float(p[0]), float(p[1])] for p in points]
        else:
            self._rel_points = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]

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
        for rx, ry in self._rel_points[1:]:
            path.lineTo(rx * w, ry * h)
        path.closeSubpath()
        self.setPath(path)

    def _recalculate_bbox(self):
        """Recalculate bounding box to tightly enclose all vertices.

        Converts relative points that may be outside 0-1 range back into
        a new bounding box with all relative points normalized to 0-1.
        """
        if not self._rel_points:
            return

        # Convert current relative points to absolute scene coordinates
        p = self.pos()
        abs_pts = [
            (p.x() + rx * self._width, p.y() + ry * self._height)
            for rx, ry in self._rel_points
        ]

        # Compute new bounding box
        xs = [pt[0] for pt in abs_pts]
        ys = [pt[1] for pt in abs_pts]
        new_x = min(xs)
        new_y = min(ys)
        new_w = max(xs) - new_x
        new_h = max(ys) - new_y

        # Enforce minimum size
        if new_w < 1.0:
            new_w = 1.0
        if new_h < 1.0:
            new_h = 1.0

        # Recompute relative points within new bounding box
        self._rel_points = [
            [(ax - new_x) / new_w, (ay - new_y) / new_h]
            for ax, ay in abs_pts
        ]

        # Update position and dimensions
        self.prepareGeometryChange()
        self.setPos(QPointF(new_x, new_y))
        self._width = new_w
        self._height = new_h
        self._update_path()
        self._update_label_position()

    def _apply_pen_brush(self):
        pen = QPen(self.pen_color, self.pen_width)
        _apply_dash_style(pen, self.line_dash, self.dash_pattern_length, self.dash_solid_percent)
        self.setPen(pen)
        self.setBrush(QBrush(self.brush_color))

    def _update_label_position(self):
        padding = 8
        self._label_item.setTextWidth(max(10, self._width - 2 * padding))

        text_height = self._label_item.boundingRect().height()
        available_height = self._height - 2 * padding

        valign = getattr(self.meta, "text_valign", "top") if hasattr(self, "meta") else "top"

        if valign == "middle":
            y_pos = padding + (available_height - text_height) / 2
        elif valign == "bottom":
            y_pos = self._height - padding - text_height
        else:
            y_pos = padding

        self._label_item.setPos(padding, max(padding, y_pos))

    def _update_label_text(self):
        lines = []
        align_map = {"left": "left", "center": "center", "right": "right"}

        spacing = getattr(self.meta, "text_spacing", 0.0) if hasattr(self, "meta") else 0.0
        margin_style = f"margin-bottom:{spacing}em;" if spacing > 0 else ""

        if self.meta.label:
            align = align_map.get(self.meta.label_align, "center")
            size = self.meta.label_size
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt; {margin_style}"><b>{self.meta.label}</b></p>')
        if self.meta.tech:
            align = align_map.get(self.meta.tech_align, "center")
            size = self.meta.tech_size
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt; {margin_style}"><i>[{self.meta.tech}]</i></p>')
        if self.meta.note:
            align = align_map.get(self.meta.note_align, "center")
            size = self.meta.note_size
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt;">{self.meta.note}</p>')

        self._label_item.setHtml("".join(lines) if lines else "")
        self._label_item.setDefaultTextColor(self.text_color)
        self._update_label_position()

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

    # ---- Bounding-box handles ----

    def _handle_points_scene(self) -> Dict[str, QPointF]:
        p = self.pos()
        cx = p.x() + self._width / 2
        cy = p.y() + self._height / 2
        return {
            "tl": QPointF(p.x(), p.y()),
            "tr": QPointF(p.x() + self._width, p.y()),
            "bl": QPointF(p.x(), p.y() + self._height),
            "br": QPointF(p.x() + self._width, p.y() + self._height),
            "t":  QPointF(cx, p.y()),
            "b":  QPointF(cx, p.y() + self._height),
            "l":  QPointF(p.x(), cy),
            "r":  QPointF(p.x() + self._width, cy),
        }

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

    def _hit_test_handle(self, scene_pt: QPointF) -> Optional[str]:
        if not self._should_paint_handles():
            return None
        handles = self._handle_points_scene()
        hit_dist = _get_hit_distance()
        for k, hp in handles.items():
            if QLineF(scene_pt, hp).length() <= hit_dist:
                return k
        return None

    # ---- Vertex editing helpers ----

    def _vertex_points_scene(self) -> list:
        """Return absolute scene positions of all vertices."""
        p = self.pos()
        return [
            QPointF(p.x() + rx * self._width, p.y() + ry * self._height)
            for rx, ry in self._rel_points
        ]

    def _vertex_points_local(self) -> list:
        """Return local positions of all vertices."""
        return [
            QPointF(rx * self._width, ry * self._height)
            for rx, ry in self._rel_points
        ]

    def _hit_test_vertex(self, scene_pt: QPointF) -> Optional[int]:
        """Return index of vertex near scene_pt, or None."""
        hit_dist = _get_hit_distance()
        for i, vp in enumerate(self._vertex_points_scene()):
            if QLineF(scene_pt, vp).length() <= hit_dist:
                return i
        return None

    def _hit_test_edge(self, scene_pt: QPointF) -> Optional[int]:
        """Return index of edge near scene_pt, or None.

        Edge i connects vertex i to vertex (i+1) % n.
        Returns the edge index where a new vertex should be inserted after.
        """
        hit_dist = _get_hit_distance()
        verts = self._vertex_points_scene()
        n = len(verts)
        for i in range(n):
            a = verts[i]
            b = verts[(i + 1) % n]
            # Distance from point to line segment
            line = QLineF(a, b)
            length = line.length()
            if length < 1e-6:
                continue
            # Project scene_pt onto line segment
            dx = b.x() - a.x()
            dy = b.y() - a.y()
            t = ((scene_pt.x() - a.x()) * dx + (scene_pt.y() - a.y()) * dy) / (length * length)
            t = max(0.0, min(1.0, t))
            proj = QPointF(a.x() + t * dx, a.y() + t * dy)
            if QLineF(scene_pt, proj).length() <= hit_dist:
                return i
        return None

    # ---- Mouse interaction ----

    def hoverMoveEvent(self, event):
        if self._vertex_editing:
            idx = self._hit_test_vertex(event.scenePos())
            if idx is not None:
                self.setCursor(Qt.CursorShape.CrossCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            h = self._hit_test_handle(event.scenePos())
            if h in ("tl", "br"):
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            elif h in ("tr", "bl"):
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            elif h in ("t", "b"):
                self.setCursor(Qt.CursorShape.SizeVerCursor)
            elif h in ("l", "r"):
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._vertex_editing = not self._vertex_editing
            self.prepareGeometryChange()
            self.update()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton and self._vertex_editing:
            scene_pt = event.scenePos()
            # Right-click on vertex: delete it (min 3 vertices)
            idx = self._hit_test_vertex(scene_pt)
            if idx is not None:
                if len(self._rel_points) > 3:
                    self.prepareGeometryChange()
                    del self._rel_points[idx]
                    self._recalculate_bbox()
                    self._notify_changed()
                event.accept()
                return
            # Right-click on edge: insert a new vertex
            edge_idx = self._hit_test_edge(scene_pt)
            if edge_idx is not None:
                p = self.pos()
                rx = (scene_pt.x() - p.x()) / self._width if self._width > 0 else 0.5
                ry = (scene_pt.y() - p.y()) / self._height if self._height > 0 else 0.5
                self.prepareGeometryChange()
                self._rel_points.insert(edge_idx + 1, [rx, ry])
                self._update_path()
                self._update_label_position()
                self._notify_changed()
                event.accept()
                return

        if event.button() == Qt.MouseButton.LeftButton:
            # Vertex editing takes priority
            if self._vertex_editing:
                idx = self._hit_test_vertex(event.scenePos())
                if idx is not None:
                    self._begin_resize_tracking()
                    self._active_vertex = idx
                    self._vertex_dragging = True
                    self._press_scene = event.scenePos()
                    event.accept()
                    return

            # Bounding-box handle resize
            h = self._hit_test_handle(event.scenePos())
            if h:
                self._begin_resize_tracking()
                self._active_handle = h
                self._resizing = True
                self._press_scene = event.scenePos()
                self._start_pos = QPointF(self.pos())
                self._start_size = (self._width, self._height)
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # Vertex dragging — allow dragging outside the current bounding box
        if self._vertex_dragging and self._active_vertex is not None:
            cur = event.scenePos()
            p = self.pos()
            # Compute unclamped relative position (can exceed 0-1 range)
            rx = (cur.x() - p.x()) / self._width if self._width > 0 else 0.5
            ry = (cur.y() - p.y()) / self._height if self._height > 0 else 0.5
            self._rel_points[self._active_vertex] = [rx, ry]
            self.prepareGeometryChange()
            self._update_path()
            self._update_label_position()
            self._notify_changed()
            event.accept()
            return

        # Bounding-box handle resize
        if self._resizing and self._active_handle and self._press_scene and self._start_pos and self._start_size:
            cur = event.scenePos()
            dx = cur.x() - self._press_scene.x()
            dy = cur.y() - self._press_scene.y()

            x0 = self._start_pos.x()
            y0 = self._start_pos.y()
            w0, h0 = self._start_size

            left = x0
            top = y0
            right = x0 + w0
            bottom = y0 + h0

            if self._active_handle == "tl":
                left += dx; top += dy
            elif self._active_handle == "tr":
                right += dx; top += dy
            elif self._active_handle == "bl":
                left += dx; bottom += dy
            elif self._active_handle == "br":
                right += dx; bottom += dy
            elif self._active_handle == "t":
                top += dy
            elif self._active_handle == "b":
                bottom += dy
            elif self._active_handle == "l":
                left += dx
            elif self._active_handle == "r":
                right += dx

            min_size = _get_min_size()
            if (right - left) < min_size:
                if self._active_handle in ("tl", "bl", "l"):
                    left = right - min_size
                else:
                    right = left + min_size
            if (bottom - top) < min_size:
                if self._active_handle in ("tl", "tr", "t"):
                    top = bottom - min_size
                else:
                    bottom = top + min_size

            self.setPos(QPointF(left, top))
            self._width = right - left
            self._height = bottom - top
            self._update_path()
            self._update_label_position()
            self._notify_changed()
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._vertex_dragging:
            self._end_resize_tracking()
            self._vertex_dragging = False
            self._active_vertex = None
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

    # ---- Shape / bounds / paint ----

    def shape(self) -> QPainterPath:
        base = super().shape()
        if self._should_paint_handles() and not self._vertex_editing:
            return shape_with_handles(base, self._handle_points_local())
        if self._should_paint_handles() and self._vertex_editing:
            # Add vertex hit areas
            hit_r = _get_handle_size() / 2 + 1
            for vp in self._vertex_points_local():
                base.addEllipse(vp, hit_r, hit_r)
        return base

    def boundingRect(self) -> QRectF:
        r = super().boundingRect()
        margin = _get_handle_size() / 2 + 1
        return r.adjusted(-margin, -margin, margin, margin)

    def paint(self, painter: QPainter, option, widget=None):
        my_option = QStyleOptionGraphicsItem(option)
        my_option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, my_option, widget)

        if not self._should_paint_handles():
            return

        if self._vertex_editing:
            # Draw vertex knobs
            handle_size = _get_handle_size()
            half = handle_size / 2
            for i, vp in enumerate(self._vertex_points_local()):
                if i == self._active_vertex:
                    painter.setPen(QPen(QColor(204, 102, 0), 1))
                    painter.setBrush(QBrush(QColor(255, 165, 0)))  # Orange for active
                else:
                    painter.setPen(QPen(QColor(0, 128, 0), 1))
                    painter.setBrush(QBrush(QColor(0, 200, 0)))  # Green
                painter.drawEllipse(QRectF(vp.x() - half, vp.y() - half,
                                           handle_size, handle_size))
        else:
            # Draw selection outline and bounding-box handles
            sel_pen = QPen(_get_selection_color(), 1, Qt.PenStyle.DashLine)
            painter.setPen(sel_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(self.path())

            draw_handles(painter, self._handle_points_local())

    def itemChange(self, change, value):
        out = super().itemChange(change, value)
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if not self._resizing and not self._vertex_dragging:
                self._notify_changed()
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            if not value:
                self._vertex_editing = False
            self.prepareGeometryChange()
        return out

    def to_record(self) -> Dict[str, Any]:
        p = self.pos()
        rec = {
            "id": self.ann_id,
            "kind": "polygon",
            "geom": {
                "x": round1(p.x()),
                "y": round1(p.y()),
                "w": round1(self._width),
                "h": round1(self._height),
                "points": [[round(rx, 4), round(ry, 4)] for rx, ry in self._rel_points],
            },
            **self._meta_dict(self.meta),
            **self._style_dict(),
        }
        z = self.zValue()
        if z != 0:
            rec["z"] = int(z)
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

        # Arrow support
        self.arrow_mode = self.ARROW_NONE
        self.arrow_size = 12.0

        # Style
        self.pen_color = QColor(Qt.GlobalColor.darkMagenta)
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
        self._label_item.setDefaultTextColor(self.text_color)
        self._label_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self._update_path()
        self._update_label_position()

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

                # Check if next node forms an H/V corner and we have a bend radius
                next_node = self._nodes[i + 1] if i + 1 < len(self._nodes) else None
                next_cmd = next_node.get("cmd", "") if next_node else ""
                has_corner = (r > 0 and cmd in ("H", "V") and next_cmd in ("H", "V")
                              and next_cmd != cmd)

                if has_corner:
                    # Compute next segment endpoint
                    if next_cmd == "H":
                        next_target_x = next_node.get("x", target_x)
                        next_target_y = target_y
                    else:  # V
                        next_target_x = target_x
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

    def _apply_pen_brush(self):
        """Apply pen and brush (no fill for curves)."""
        pen = QPen(self.pen_color, self.pen_width)
        _apply_dash_style(pen, self.line_dash, self.dash_pattern_length, self.dash_solid_percent)
        self.setPen(pen)
        self.setBrush(QBrush(QColor(0, 0, 0, 0)))  # Transparent fill

    def _update_label_position(self):
        """Position label at center of bounding box."""
        padding = 8
        self._label_item.setTextWidth(max(10, self._width - 2 * padding))
        text_height = self._label_item.boundingRect().height()
        y_pos = (self._height - text_height) / 2
        self._label_item.setPos(padding, max(padding, y_pos))

    def _update_label_text(self):
        """Update embedded label HTML from meta fields."""
        lines = []
        align_map = {"left": "left", "center": "center", "right": "right"}
        spacing = getattr(self.meta, "text_spacing", 0.0)
        margin_style = f"margin-bottom:{spacing}em;" if spacing > 0 else ""

        if self.meta.label:
            align = align_map.get(self.meta.label_align, "center")
            size = self.meta.label_size
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt; {margin_style}"><b>{self.meta.label}</b></p>')
        if self.meta.tech:
            align = align_map.get(self.meta.tech_align, "center")
            size = self.meta.tech_size
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt; {margin_style}"><i>[{self.meta.tech}]</i></p>')
        if self.meta.note:
            align = align_map.get(self.meta.note_align, "center")
            size = self.meta.note_size
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt;">{self.meta.note}</p>')

        self._label_item.setHtml("".join(lines) if lines else "")
        self._label_item.setDefaultTextColor(self.text_color)
        self._update_label_position()

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

    def _handle_points_scene(self) -> Dict[str, QPointF]:
        p = self.pos()
        cx = p.x() + self._width / 2
        cy = p.y() + self._height / 2
        handles = {
            "tl": QPointF(p.x(), p.y()),
            "tr": QPointF(p.x() + self._width, p.y()),
            "bl": QPointF(p.x(), p.y() + self._height),
            "br": QPointF(p.x() + self._width, p.y() + self._height),
            "t":  QPointF(cx, p.y()),
            "b":  QPointF(cx, p.y() + self._height),
            "l":  QPointF(p.x(), cy),
            "r":  QPointF(p.x() + self._width, cy),
        }
        br_local = self._bend_radius_handle_local()
        if br_local is not None:
            handles["adjust1"] = QPointF(p.x() + br_local.x(), p.y() + br_local.y())
        return handles

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

    def _hit_test_handle(self, scene_pt: QPointF) -> Optional[str]:
        if not self._should_paint_handles():
            return None
        handles = self._handle_points_scene()
        hit_dist = _get_hit_distance()
        # Test adjust1 first (it may overlap with other handles)
        if "adjust1" in handles:
            if QLineF(scene_pt, handles["adjust1"]).length() <= hit_dist:
                return "adjust1"
        for k, hp in handles.items():
            if k == "adjust1":
                continue
            if QLineF(scene_pt, hp).length() <= hit_dist:
                return k
        return None

    # ---- Node editing helpers ----

    def _node_points_scene(self) -> list:
        """Return list of (scene_point, node_index, handle_type) for all hit-testable points."""
        p = self.pos()
        w, h = self._width, self._height
        result = []
        for i, node in enumerate(self._nodes):
            cmd = node.get("cmd", "L")
            if cmd == "Z":
                continue
            ax, ay = self._get_node_anchor(i)
            result.append((QPointF(p.x() + ax * w, p.y() + ay * h), i, "anchor"))
            if cmd == "C":
                c1x, c1y = node.get("c1x", ax), node.get("c1y", ay)
                c2x, c2y = node.get("c2x", ax), node.get("c2y", ay)
                result.append((QPointF(p.x() + c1x * w, p.y() + c1y * h), i, "c1"))
                result.append((QPointF(p.x() + c2x * w, p.y() + c2y * h), i, "c2"))
            elif cmd == "S":
                c2x, c2y = node.get("c2x", ax), node.get("c2y", ay)
                result.append((QPointF(p.x() + c2x * w, p.y() + c2y * h), i, "c2"))
            elif cmd == "Q":
                cx, cy = node.get("cx", ax), node.get("cy", ay)
                result.append((QPointF(p.x() + cx * w, p.y() + cy * h), i, "cx"))
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
            h = self._hit_test_handle(event.scenePos())
            if h == "adjust1":
                self.setCursor(Qt.CursorShape.CrossCursor)
            elif h in ("tl", "br"):
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            elif h in ("tr", "bl"):
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            elif h in ("t", "b"):
                self.setCursor(Qt.CursorShape.SizeVerCursor)
            elif h in ("l", "r"):
                self.setCursor(Qt.CursorShape.SizeHorCursor)
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
                p = self.pos()
                rx = (scene_pt.x() - p.x()) / self._width if self._width > 0 else 0.5
                ry = (scene_pt.y() - p.y()) / self._height if self._height > 0 else 0.5
                self.prepareGeometryChange()
                self._nodes.insert(edge_idx + 1, {"cmd": "L", "x": rx, "y": ry})
                self._update_path()
                self._update_label_position()
                self._notify_changed()
                event.accept()
                return

        if event.button() == Qt.MouseButton.LeftButton:
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
            if h:
                self._begin_resize_tracking()
                self._active_handle = h
                if h == "adjust1":
                    self._start_adjust1 = self._adjust1
                self._resizing = True
                self._press_scene = event.scenePos()
                self._start_pos = QPointF(self.pos())
                self._start_size = (self._width, self._height)
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # Adjust1 (bend radius) handle drag
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
                if MetaCurveItem.on_adjust1_changed:
                    MetaCurveItem.on_adjust1_changed(self, new_r)
                self._notify_changed()
            event.accept()
            return

        # Node dragging
        if self._node_dragging and self._active_node is not None:
            cur = event.scenePos()
            p = self.pos()
            rx = (cur.x() - p.x()) / self._width if self._width > 0 else 0.5
            ry = (cur.y() - p.y()) / self._height if self._height > 0 else 0.5

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
            self._notify_changed()
            event.accept()
            return

        # Bounding-box handle resize
        if self._resizing and self._active_handle and self._press_scene and self._start_pos and self._start_size:
            cur = event.scenePos()
            dx = cur.x() - self._press_scene.x()
            dy = cur.y() - self._press_scene.y()

            x0 = self._start_pos.x()
            y0 = self._start_pos.y()
            w0, h0 = self._start_size

            left = x0
            top = y0
            right = x0 + w0
            bottom = y0 + h0

            if self._active_handle == "tl":
                left += dx; top += dy
            elif self._active_handle == "tr":
                right += dx; top += dy
            elif self._active_handle == "bl":
                left += dx; bottom += dy
            elif self._active_handle == "br":
                right += dx; bottom += dy
            elif self._active_handle == "t":
                top += dy
            elif self._active_handle == "b":
                bottom += dy
            elif self._active_handle == "l":
                left += dx
            elif self._active_handle == "r":
                right += dx

            min_size = _get_min_size()
            if (right - left) < min_size:
                if self._active_handle in ("tl", "bl", "l"):
                    left = right - min_size
                else:
                    right = left + min_size
            if (bottom - top) < min_size:
                if self._active_handle in ("tl", "tr", "t"):
                    top = bottom - min_size
                else:
                    bottom = top + min_size

            self.setPos(QPointF(left, top))
            self._width = right - left
            self._height = bottom - top
            self._update_path()
            self._update_label_position()
            self._notify_changed()
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._node_dragging:
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
        self._notify_changed()

    # ---- Shape / bounds / paint ----

    def shape(self) -> QPainterPath:
        """Return shape for hit-testing with fat stroke."""
        stroker = QPainterPath()
        from PyQt6.QtGui import QPainterPathStroker
        s = QPainterPathStroker()
        s.setWidth(max(20, self.pen_width + 10))
        stroker = s.createStroke(self.path())
        if self._should_paint_handles() and not self._node_editing:
            return shape_with_handles(stroker, self._handle_points_local())
        if self._should_paint_handles() and self._node_editing:
            hit_r = _get_handle_size() / 2 + 1
            for pt, _, _ in self._node_points_scene():
                local_pt = self.mapFromScene(pt)
                stroker.addEllipse(local_pt, hit_r, hit_r)
        return stroker

    def boundingRect(self) -> QRectF:
        r = super().boundingRect()
        margin = _get_handle_size() / 2 + 1 + self.pen_width
        return r.adjusted(-margin, -margin, margin, margin)

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

        if not self._should_paint_handles():
            return

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
        z = self.zValue()
        if z != 0:
            rec["z"] = int(z)
        return rec


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
        """Append an orthogonal segment at the end of the curve."""
        self._begin_resize_tracking()
        p = self.pos()
        rx = (scene_pt.x() - p.x()) / self._width if self._width > 0 else 0.5
        ry = (scene_pt.y() - p.y()) / self._height if self._height > 0 else 0.5

        last_idx = self._last_path_index()
        last_cmd = self._nodes[last_idx].get("cmd", "L")

        if last_cmd == "H":
            new_node = {"cmd": "V", "y": ry}
        elif last_cmd == "V":
            new_node = {"cmd": "H", "x": rx}
        else:
            last_ax, last_ay = self._get_node_anchor(last_idx)
            if abs(rx - last_ax) >= abs(ry - last_ay):
                new_node = {"cmd": "H", "x": rx}
            else:
                new_node = {"cmd": "V", "y": ry}

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
        """Return local positions of ortho control handles at each H/V node."""
        handles: Dict[str, QPointF] = {}
        w, h = self._width, self._height
        for i in range(1, len(self._nodes)):
            cmd = self._nodes[i].get("cmd", "L")
            if cmd not in ("H", "V"):
                continue
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
        self._update_path()
        self._update_label_position()
        self._notify_changed()

    # ---- Handle overrides ----

    def _handle_points_scene(self) -> Dict[str, QPointF]:
        handles = super()._handle_points_scene()
        p = self.pos()
        for k, lp in self._ortho_handle_points_local().items():
            handles[k] = QPointF(p.x() + lp.x(), p.y() + lp.y())
        return handles

    def _handle_points_local(self) -> Dict[str, QPointF]:
        handles = super()._handle_points_local()
        handles.update(self._ortho_handle_points_local())
        return handles

    def _hit_test_handle(self, scene_pt: QPointF) -> Optional[str]:
        if not self._should_paint_handles():
            return None
        handles = self._handle_points_scene()
        hit_dist = _get_hit_distance()
        # Test adjust1 first (it may overlap with other handles)
        if "adjust1" in handles:
            if QLineF(scene_pt, handles["adjust1"]).length() <= hit_dist:
                return "adjust1"
        # Test ortho handles next (priority over bbox handles)
        for k, hp in handles.items():
            if k.startswith("ortho_") and QLineF(scene_pt, hp).length() <= hit_dist:
                return k
        for k, hp in handles.items():
            if k == "adjust1" or k.startswith("ortho_"):
                continue
            if QLineF(scene_pt, hp).length() <= hit_dist:
                return k
        return None

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
            if cmd == "H":
                node["x"] = rx
                if prev_cmd == "V":
                    prev["y"] = ry
                elif prev_cmd in ("M", "L"):
                    prev["y"] = ry
            elif cmd == "V":
                node["y"] = ry
                if prev_cmd == "H":
                    prev["x"] = rx
                elif prev_cmd in ("M", "L"):
                    prev["x"] = rx
            self.prepareGeometryChange()
            self._update_path()
            self._update_label_position()
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
        padding = 4
        self._label_item.setTextWidth(max(10, fw - 2 * padding))

        text_height = self._label_item.boundingRect().height()
        valign = getattr(self.meta, "text_valign", "top") if hasattr(self, "meta") else "top"

        if valign == "middle":
            y_pos = fy + (fh - text_height) / 2
        elif valign == "bottom":
            y_pos = fy + fh - padding - text_height
        else:
            y_pos = fy + padding

        self._label_item.setPos(fx + padding, max(fy + padding, y_pos))

    def _update_label_text(self):
        """Rebuild label HTML from meta fields."""
        lines = []
        align_map = {"left": "left", "center": "center", "right": "right"}

        spacing = getattr(self.meta, "text_spacing", 0.0) if hasattr(self, "meta") else 0.0
        margin_style = f"margin-bottom:{spacing}em;" if spacing > 0 else ""

        if self.meta.label:
            align = align_map.get(self.meta.label_align, "center")
            size = self.meta.label_size
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt; {margin_style}"><b>{self.meta.label}</b></p>')
        if self.meta.tech:
            align = align_map.get(self.meta.tech_align, "center")
            size = self.meta.tech_size
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt; {margin_style}"><i>[{self.meta.tech}]</i></p>')
        if self.meta.note:
            align = align_map.get(self.meta.note_align, "center")
            size = self.meta.note_size
            lines.append(f'<p style="text-align:{align}; font-size:{size}pt;">{self.meta.note}</p>')

        self._label_item.setHtml("".join(lines) if lines else "")
        self._label_item.setDefaultTextColor(self.text_color)
        self._update_label_position()

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

    def adjust1(self) -> float:
        """Return current depth (px)."""
        return self._adjust1

    def set_adjust1(self, value: float):
        """Set depth (px), clamped to 0–max_depth."""
        self._adjust1 = max(0, min(self._max_depth(), value))
        self._update_path()
        self._update_label_position()

    def adjust2(self) -> float:
        """Return current angle (degrees)."""
        return self._adjust2

    def set_adjust2(self, value: float):
        """Set angle (degrees), clamped to 0–360."""
        self._adjust2 = max(0, min(360, value))
        self._update_path()
        self._update_label_position()

    # ----- handles ------------------------------------------------------------

    def _handle_points_scene(self) -> Dict[str, QPointF]:
        """Return handle positions in scene coordinates."""
        p = self.pos()
        cx = p.x() + self._width / 2
        cy = p.y() + self._height / 2
        fx, fy, fw, fh = self._front_rect()
        # Depth handle on the front face center (drag away from back to increase depth)
        front_cx = fx + fw / 2
        front_cy = fy + fh / 2
        return {
            "tl": QPointF(p.x(), p.y()),
            "tr": QPointF(p.x() + self._width, p.y()),
            "bl": QPointF(p.x(), p.y() + self._height),
            "br": QPointF(p.x() + self._width, p.y() + self._height),
            "t":  QPointF(cx, p.y()),
            "b":  QPointF(cx, p.y() + self._height),
            "l":  QPointF(p.x(), cy),
            "r":  QPointF(p.x() + self._width, cy),
            "adjust1": QPointF(p.x() + front_cx, p.y() + front_cy),
            # Angle handle at bbox center (stable — doesn't shift with angle/depth)
            "adjust2": QPointF(cx + 20 * math.sin(math.radians(self._adjust2)),
                               cy - 20 * math.cos(math.radians(self._adjust2))),
        }

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

    def _hit_test_handle(self, scene_pt: QPointF) -> Optional[str]:
        """Hit-test against all handles."""
        if not self._should_paint_handles():
            return None
        handles = self._handle_points_scene()
        hit_dist = _get_hit_distance()
        for k, hp in handles.items():
            if QLineF(scene_pt, hp).length() <= hit_dist:
                return k
        return None

    def hoverMoveEvent(self, event):
        """Update cursor based on handle under mouse."""
        h = self._hit_test_handle(event.scenePos())
        if h in ("tl", "br"):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif h in ("tr", "bl"):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif h in ("t", "b"):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif h in ("l", "r"):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif h in ("adjust1", "adjust2"):
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        """Begin resize/adjust tracking on handle press."""
        if event.button() == Qt.MouseButton.LeftButton:
            h = self._hit_test_handle(event.scenePos())
            if h:
                self._begin_resize_tracking()
                self._active_handle = h
                self._resizing = True
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
        if self._resizing and self._active_handle and self._press_scene and self._start_pos and self._start_size:
            cur = event.scenePos()
            d_x = cur.x() - self._press_scene.x()
            d_y = cur.y() - self._press_scene.y()

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
                self._notify_changed()
                if MetaIsoCubeItem.on_adjust2_changed:
                    MetaIsoCubeItem.on_adjust2_changed(self, angle_deg)
                event.accept()
                return

            # Standard bbox resize handles
            x0 = self._start_pos.x()
            y0 = self._start_pos.y()
            w0, h0 = self._start_size

            left = x0
            top = y0
            right = x0 + w0
            bottom = y0 + h0

            if self._active_handle == "tl":
                left += d_x; top += d_y
            elif self._active_handle == "tr":
                right += d_x; top += d_y
            elif self._active_handle == "bl":
                left += d_x; bottom += d_y
            elif self._active_handle == "br":
                right += d_x; bottom += d_y
            elif self._active_handle == "t":
                top += d_y
            elif self._active_handle == "b":
                bottom += d_y
            elif self._active_handle == "l":
                left += d_x
            elif self._active_handle == "r":
                right += d_x

            min_size = _get_min_size()
            if (right - left) < min_size:
                if self._active_handle in ("tl", "bl", "l"):
                    left = right - min_size
                else:
                    right = left + min_size
            if (bottom - top) < min_size:
                if self._active_handle in ("tl", "tr", "t"):
                    top = bottom - min_size
                else:
                    bottom = top + min_size

            new_w = right - left
            new_h = bottom - top
            self.setPos(QPointF(left, top))
            self._width = new_w
            self._height = new_h
            self._update_path()
            self._update_label_position()
            self._notify_changed()
            event.accept()
            return

        super().mouseMoveEvent(event)

    def shape(self) -> QPainterPath:
        """Return shape including handle hit areas when selected."""
        base = super().shape()
        if self._should_paint_handles():
            return shape_with_handles(base, self._handle_points_local())
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
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.prepareGeometryChange()
        return out

    def to_record(self) -> Dict[str, Any]:
        """Serialize isocube to JSON record."""
        p = self.pos()
        rec = {
            "id": self.ann_id,
            "kind": "isocube",
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
        return rec


class MetaGroupItem(QGraphicsItemGroup, MetaMixin, LinkedMixin):
    """Group item that contains multiple annotation items as a single unit."""

    KIND = "group"
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
        if h in ("tl", "br"):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif h in ("tr", "bl"):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif h in ("t", "b"):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif h in ("l", "r"):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
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
            dx = cur.x() - self._press_scene.x()
            dy = cur.y() - self._press_scene.y()

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
# Kind alias registry — validates uniqueness at import time
# ═══════════════════════════════════════════════════════════

_ALL_META_CLASSES = [
    MetaRectItem, MetaRoundedRectItem, MetaEllipseItem, MetaLineItem,
    MetaTextItem, MetaHexagonItem, MetaCylinderItem, MetaBlockArrowItem,
    MetaPolygonItem, MetaCurveItem, MetaOrthoCurveItem, MetaIsoCubeItem,
    MetaGroupItem,
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
