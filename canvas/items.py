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
    QGraphicsRectItem,
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsTextItem,
    QGraphicsPathItem,
    QStyle,
    QStyleOptionGraphicsItem,
)

from models import AnnotationMeta, ANN_ID_KEY, HANDLE_SIZE, HIT_DIST, MIN_SIZE
from canvas.mixins import LinkedMixin, MetaMixin


def round1(value: float) -> float:
    """Round a value to 1 decimal place precision."""
    return round(value, 1)


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

        # Ensure minimum gap of 2 pixels so it's always visible
        min_gap_px = 2.0
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


def draw_handles(painter: QPainter, handle_positions: Dict[str, QPointF], handle_size: float = HANDLE_SIZE):
    """Draw resize handles at the given positions."""
    handle_pen = QPen(QColor(0, 120, 215), 1)  # Blue border
    handle_brush = QBrush(QColor(255, 255, 255))  # White fill
    painter.setPen(handle_pen)
    painter.setBrush(handle_brush)

    half = handle_size / 2
    for pos in handle_positions.values():
        painter.drawRect(QRectF(pos.x() - half, pos.y() - half, handle_size, handle_size))


def shape_with_handles(base_shape: QPainterPath, handle_positions: Dict[str, QPointF], handle_size: float = HIT_DIST) -> QPainterPath:
    """Create a shape path that includes handle hit areas."""
    result = QPainterPath(base_shape)
    half = handle_size / 2
    for pos in handle_positions.values():
        result.addRect(QRectF(pos.x() - half, pos.y() - half, handle_size, handle_size))
    return result


class MetaRectItem(QGraphicsRectItem, MetaMixin, LinkedMixin):
    """Rectangle item with resizable corners and embedded C4 text label."""

    def __init__(self, x: float, y: float, w: float, h: float, ann_id: str, on_change=None):
        QGraphicsRectItem.__init__(self, QRectF(0, 0, w, h))
        MetaMixin.__init__(self)
        LinkedMixin.__init__(self, ann_id, on_change)

        self.meta.kind = "rect"
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
        self.dash_pattern_length = 30.0
        self.dash_solid_percent = 50.0
        self._apply_pen_brush()

        # Embedded text for C4 properties
        self._label_item = QGraphicsTextItem(self)
        self._label_item.setDefaultTextColor(self.text_color)
        self._label_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self._update_label_position()

    def _apply_pen_brush(self):
        pen = QPen(self.pen_color, self.pen_width)
        _apply_dash_style(pen, self.line_dash, self.dash_pattern_length, self.dash_solid_percent)
        self.setPen(pen)
        self.setBrush(QBrush(self.brush_color))

    def _update_label_position(self):
        r = self.rect()
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
        handles = self._handle_points_scene()
        for k, hp in handles.items():
            if QLineF(scene_pt, hp).length() <= HIT_DIST:
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

            if (right - left) < MIN_SIZE:
                if self._active_handle in ("tl", "bl", "l"):
                    left = right - MIN_SIZE
                else:
                    right = left + MIN_SIZE

            if (bottom - top) < MIN_SIZE:
                if self._active_handle in ("tl", "tr", "t"):
                    top = bottom - MIN_SIZE
                else:
                    bottom = top + MIN_SIZE

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
        if self.isSelected():
            return shape_with_handles(base, self._handle_points_local())
        return base

    def boundingRect(self) -> QRectF:
        """Expand bounding rect to include resize handles."""
        r = super().boundingRect()
        margin = HANDLE_SIZE / 2 + 1
        return r.adjusted(-margin, -margin, margin, margin)

    def paint(self, painter: QPainter, option, widget=None):
        # Remove selection state from option to suppress default selection rectangle
        my_option = QStyleOptionGraphicsItem(option)
        my_option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, my_option, widget)

        if self.isSelected():
            # Draw selection outline matching the actual rect
            sel_pen = QPen(QColor(0, 120, 215), 1, Qt.PenStyle.DashLine)
            painter.setPen(sel_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self.rect())
            # Draw resize handles
            draw_handles(painter, self._handle_points_local())

    def mouseReleaseEvent(self, event):
        if self._resizing:
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
    """Rounded rectangle item with configurable corner radius."""

    # Class-level callback for radius changes (set by MainWindow)
    on_radius_changed = None  # Called with (item, new_radius) when radius changes via handle drag

    def __init__(self, x: float, y: float, w: float, h: float, radius: float, ann_id: str, on_change=None):
        QGraphicsPathItem.__init__(self)
        MetaMixin.__init__(self)
        LinkedMixin.__init__(self, ann_id, on_change)

        self.meta.kind = "roundedrect"
        self._width = w
        self._height = h
        self._radius = radius
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
        self._start_radius: Optional[float] = None

        self.pen_color = QColor(Qt.GlobalColor.magenta)
        self.pen_width = 2
        self.brush_color = QColor(0, 0, 0, 0)
        self.text_color = QColor(self.pen_color)  # Default text color matches border
        self.line_dash = "solid"  # solid | dashed
        self.dash_pattern_length = 30.0
        self.dash_solid_percent = 50.0
        self._apply_pen_brush()

        # Embedded text for C4 properties
        self._label_item = QGraphicsTextItem(self)
        self._label_item.setDefaultTextColor(self.text_color)
        self._label_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self._update_label_position()

    def _update_path(self):
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, self._width, self._height), self._radius, self._radius)
        self.setPath(path)

    def _apply_pen_brush(self):
        pen = QPen(self.pen_color, self.pen_width)
        _apply_dash_style(pen, self.line_dash, self.dash_pattern_length, self.dash_solid_percent)
        self.setPen(pen)
        self.setBrush(QBrush(self.brush_color))

    def _update_label_position(self):
        padding = 4 + self._radius * 0.3  # Extra padding for rounded corners
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

    def corner_radius(self) -> float:
        return self._radius

    def set_corner_radius(self, r: float):
        self._radius = max(0, r)
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
            "radius": QPointF(p.x() + self._radius, p.y()),  # Radius control handle
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
            "radius": QPointF(self._radius, 0),  # Radius control handle
        }

    def _hit_test_handle(self, scene_pt: QPointF) -> Optional[str]:
        handles = self._handle_points_scene()
        for k, hp in handles.items():
            if QLineF(scene_pt, hp).length() <= HIT_DIST:
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
        elif h in ("l", "r", "radius"):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            h = self._hit_test_handle(event.scenePos())
            if h:
                self._active_handle = h
                self._resizing = True
                self._press_scene = event.scenePos()
                self._start_pos = QPointF(self.pos())
                self._start_size = (self._width, self._height)
                self._start_radius = self._radius
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resizing and self._active_handle and self._press_scene and self._start_pos and self._start_size:
            cur = event.scenePos()
            dx = cur.x() - self._press_scene.x()
            dy = cur.y() - self._press_scene.y()

            # Handle radius adjustment separately
            if self._active_handle == "radius" and self._start_radius is not None:
                new_radius = self._start_radius + dx
                # Clamp radius between 0 and half of the smaller dimension
                max_radius = min(self._width, self._height) / 2
                new_radius = max(0, min(new_radius, max_radius))
                self._radius = new_radius
                self._update_path()
                self._update_label_position()
                self._notify_changed()
                # Notify property panel of radius change
                if MetaRoundedRectItem.on_radius_changed:
                    MetaRoundedRectItem.on_radius_changed(self, new_radius)
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

            if (right - left) < MIN_SIZE:
                if self._active_handle in ("tl", "bl", "l"):
                    left = right - MIN_SIZE
                else:
                    right = left + MIN_SIZE

            if (bottom - top) < MIN_SIZE:
                if self._active_handle in ("tl", "tr", "t"):
                    top = bottom - MIN_SIZE
                else:
                    bottom = top + MIN_SIZE

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
        if self.isSelected():
            return shape_with_handles(base, self._handle_points_local())
        return base

    def boundingRect(self) -> QRectF:
        """Expand bounding rect to include resize handles."""
        r = super().boundingRect()
        margin = HANDLE_SIZE / 2 + 1
        return r.adjusted(-margin, -margin, margin, margin)

    def paint(self, painter: QPainter, option, widget=None):
        # Remove selection state from option to suppress default selection rectangle
        my_option = QStyleOptionGraphicsItem(option)
        my_option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, my_option, widget)

        if self.isSelected():
            # Draw selection outline matching the actual rounded rect
            sel_pen = QPen(QColor(0, 120, 215), 1, Qt.PenStyle.DashLine)
            painter.setPen(sel_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(QRectF(0, 0, self._width, self._height), self._radius, self._radius)

            # Draw resize handles (excluding radius handle)
            handles = self._handle_points_local()
            radius_handle_pos = handles.pop("radius")  # Remove radius handle from regular handles
            draw_handles(painter, handles)

            # Draw radius handle in yellow
            half = HANDLE_SIZE / 2
            painter.setPen(QPen(QColor(204, 153, 0), 1))  # Dark yellow border
            painter.setBrush(QBrush(QColor(255, 215, 0)))  # Gold/yellow fill
            painter.drawEllipse(QRectF(radius_handle_pos.x() - half, radius_handle_pos.y() - half,
                                       HANDLE_SIZE, HANDLE_SIZE))

    def mouseReleaseEvent(self, event):
        if self._resizing:
            self._resizing = False
            self._active_handle = None
            self._press_scene = None
            self._start_pos = None
            self._start_size = None
            self._start_radius = None
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
                "radius": round1(self._radius),
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

    def __init__(self, x: float, y: float, w: float, h: float, ann_id: str, on_change=None):
        QGraphicsEllipseItem.__init__(self, QRectF(0, 0, w, h))
        MetaMixin.__init__(self)
        LinkedMixin.__init__(self, ann_id, on_change)

        self.meta.kind = "ellipse"
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
        self.dash_pattern_length = 30.0
        self.dash_solid_percent = 50.0
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
        handles = self._handle_points_scene()
        for k, hp in handles.items():
            if QLineF(scene_pt, hp).length() <= HIT_DIST:
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

            if (right - left) < MIN_SIZE:
                if self._active_handle in ("tl", "bl", "l"):
                    left = right - MIN_SIZE
                else:
                    right = left + MIN_SIZE

            if (bottom - top) < MIN_SIZE:
                if self._active_handle in ("tl", "tr", "t"):
                    top = bottom - MIN_SIZE
                else:
                    bottom = top + MIN_SIZE

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
        if self.isSelected():
            return shape_with_handles(base, self._handle_points_local())
        return base

    def boundingRect(self) -> QRectF:
        """Expand bounding rect to include resize handles."""
        r = super().boundingRect()
        margin = HANDLE_SIZE / 2 + 1
        return r.adjusted(-margin, -margin, margin, margin)

    def paint(self, painter: QPainter, option, widget=None):
        # Remove selection state from option to suppress default selection rectangle
        my_option = QStyleOptionGraphicsItem(option)
        my_option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, my_option, widget)

        if self.isSelected():
            # Draw selection outline matching the actual ellipse
            sel_pen = QPen(QColor(0, 120, 215), 1, Qt.PenStyle.DashLine)
            painter.setPen(sel_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(self.rect())
            # Draw resize handles
            draw_handles(painter, self._handle_points_local())

    def mouseReleaseEvent(self, event):
        if self._resizing:
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

    ARROW_NONE = "none"
    ARROW_START = "start"
    ARROW_END = "end"
    ARROW_BOTH = "both"

    def __init__(self, x1: float, y1: float, x2: float, y2: float, ann_id: str, on_change=None):
        QGraphicsLineItem.__init__(self, QLineF(0, 0, x2 - x1, y2 - y1))
        MetaMixin.__init__(self)
        LinkedMixin.__init__(self, ann_id, on_change)

        self.meta.kind = "line"
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

        if self.isSelected():
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
        margin = max(HANDLE_SIZE / 2 + 1, 12.0)  # At least 12px for the 10px selection margin
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
            effective_arrow_size = max(self.arrow_size, self.pen_width * 2)

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
        if self.isSelected():
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

        half = HANDLE_SIZE / 2
        for pos in handles.values():
            painter.drawRect(QRectF(pos.x() - half, pos.y() - half, HANDLE_SIZE, HANDLE_SIZE))

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
        p1, p2 = self._endpoints_scene()
        if QLineF(scene_pt, p1).length() <= HIT_DIST:
            return "p1"
        if QLineF(scene_pt, p2).length() <= HIT_DIST:
            return "p2"
        return None

    def _hit_test_text_box_handle(self, scene_pt: QPointF) -> Optional[str]:
        """Test if scene point hits a text box resize handle."""
        if self._text_box_rect is None:
            return None
        handles = self._text_box_handle_points()
        local_pt = self.mapFromScene(scene_pt)
        for name, pos in handles.items():
            if QLineF(local_pt, pos).length() <= HIT_DIST:
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
                self._drag_text_box = tb_h
                event.accept()
                return

            h = self._hit_test_endpoint(event.scenePos())
            if h:
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
            self._drag_text_box = None
            self._notify_changed()
            event.accept()
            return
        if self._drag_end:
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

    # Class-level callbacks for focus events (set by MainWindow)
    on_editing_started = None  # Called when text editing begins
    on_editing_finished = None  # Called when text editing ends
    on_text_changed = None  # Called when text content changes during editing

    # Class-level default text color (set by MainWindow based on theme)
    default_text_color = QColor("#1E293B")  # Default to dark (Tailwind slate-800)

    def __init__(self, x: float, y: float, text: str, ann_id: str, on_change=None):
        QGraphicsTextItem.__init__(self, text)
        MetaMixin.__init__(self)
        LinkedMixin.__init__(self, ann_id, on_change)

        self.meta.kind = "text"
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
        self.meta.note = self.toPlainText()
        try:
            self.text_size_pt = float(self.font().pointSizeF())
        except Exception:
            pass
        self._notify_changed()
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
        rec = {
            "id": self.ann_id,
            "kind": "text",
            "geom": {
                "x": round1(p.x()),
                "y": round1(p.y()),
            },
            "text": self.toPlainText(),
            **self._meta_dict(self.meta),
            **self._style_dict(),
        }
        # Include z-index if set
        z = self.zValue()
        if z != 0:
            rec["z"] = int(z)
        return rec
