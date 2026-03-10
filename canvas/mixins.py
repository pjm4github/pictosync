"""
canvas/mixins.py

Mixin classes for graphics items providing annotation ID linking and metadata handling.
"""

from __future__ import annotations

import math
from typing import Any, Callable, Dict, List, Optional

from PyQt6.QtCore import Qt, QPointF, QLineF
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsItemGroup

from models import AnnotationMeta, ANN_ID_KEY
from utils import qcolor_to_hex, hex_to_qcolor


class LinkedMixin:
    """
    Mixin that provides annotation ID linking for graphics items.
    Enables bidirectional sync between JSON and scene.
    """

    # Class-level callback for resize/geometry changes (set by MainWindow)
    on_resize_finished = None  # Called with (item, old_state, new_state)

    def __init__(self, ann_id: str, on_change: Optional[Callable[[QGraphicsItem], None]]):
        self.ann_id = ann_id
        self.on_change = on_change
        self._geometry_before_resize = None

    def _notify_changed(self):
        """Notify that this item has changed."""
        if self.on_change:
            self.on_change(self)

    def set_ann_id(self, ann_id: str):
        """Set the annotation ID for this item."""
        self.ann_id = ann_id
        self.setData(ANN_ID_KEY, ann_id)

    def _begin_resize_tracking(self):
        """Snapshot geometry before a resize/endpoint-drag operation."""
        from undo_commands import capture_geometry
        self._geometry_before_resize = capture_geometry(self)

    def _end_resize_tracking(self):
        """Fire resize callback with before/after geometry if changed."""
        if self._geometry_before_resize is not None:
            from undo_commands import capture_geometry
            new_geo = capture_geometry(self)
            if LinkedMixin.on_resize_finished:
                LinkedMixin.on_resize_finished(self, self._geometry_before_resize, new_geo)
            self._geometry_before_resize = None


class MetaMixin:
    """
    Mixin that adds metadata and styling support to graphics items.

    Provides:
      - meta (AnnotationMeta)
      - style properties (pen, brush, text colors)
      - text size support via style.text.size_pt
      - rotation via set_rotation_angle / _update_transform_origin
      - default _handle_points_scene (rotation-aware via mapToScene)
      - default _hit_test_handle (with rotation knob support)
      - rotation drag helpers (_begin_rotation, _handle_rotation_move, _end_rotation)
    """

    # Class-level callback for rotation changes (set by MainWindow)
    on_rotation_changed = None  # Called with (item, new_angle)

    # Rotation knob constants
    _ROTATION_KNOB_INSET = 12   # distance below top edge in local coords
    _ROTATION_KNOB_RADIUS = 6   # radius of the knob circle

    def __init__(self):
        self.kind = "unknown"
        self.meta = AnnotationMeta()
        self.pen_color = QColor(Qt.GlobalColor.red)
        self.pen_width = 2
        self.brush_color = QColor(0, 0, 0, 0)  # transparent
        self.text_color = QColor(Qt.GlobalColor.yellow)
        self.text_size_pt = 12  # font size in points
        self.line_dash = "solid"  # solid | dashed
        self.dash_pattern_length = 30.0  # total length of one dash+gap cycle in pixels
        self.dash_solid_percent = 50.0  # percentage of pattern that is solid (0-100)
        self.arrow_size = 12.0  # arrow head size in pixels
        # Rotation state
        self._rotating = False
        self._rotation_start_angle = 0.0

    def _should_paint_handles(self) -> bool:
        """Check if this item should paint selection handles.

        Returns False when the item is a child of a group, since
        the group draws its own handles.
        """
        return self.isSelected() and not isinstance(self.parentItem(), QGraphicsItemGroup)

    def set_meta(self, meta: AnnotationMeta) -> None:
        """Set the annotation metadata."""
        self.meta = meta

    @property
    def ports(self) -> List[str]:
        """Annotation IDs of child port items attached to this shape."""
        if not hasattr(self, 'childItems'):
            return []
        return [child.ann_id for child in self.childItems()
                if hasattr(child, 'kind') and child.kind == 'port'
                and hasattr(child, 'ann_id')]

    def _ports_dict(self) -> Dict[str, Any]:
        """Return ``{"ports": [...]}`` for JSON serialization."""
        return {"ports": self.ports}

    @staticmethod
    def _meta_dict(meta: AnnotationMeta) -> Dict[str, Any]:
        """Convert metadata to dict for JSON serialization.

        Uses ``AnnotationMeta.to_dict()`` which merges any extra keys
        (e.g. C4 fields like ``alias``, ``c4_type``) back into the dict.
        """
        return {"meta": meta.to_dict()}

    def _style_dict(self) -> Dict[str, Any]:
        """Get style as dict for JSON serialization."""
        pen_style = {
            "color": qcolor_to_hex(self.pen_color),
            "width": int(self.pen_width),
            "dash": self.line_dash,
            "dash_pattern_length": round(self.dash_pattern_length, 1),
            "dash_solid_percent": round(self.dash_solid_percent, 1),
        }

        # Text style only contains visual properties (color, size)
        # Layout properties (valign, spacing) are stored in meta
        text_style = {
            "color": qcolor_to_hex(self.text_color),
            "size_pt": round(self.text_size_pt, 1),
        }

        style = {
            "pen": pen_style,
            "fill": {"color": qcolor_to_hex(self.brush_color, include_alpha=True)},
            "text": text_style,
        }
        # Only include arrow_size for line items
        if hasattr(self, "arrow_mode"):
            style["arrow_size"] = round(self.arrow_size, 1)
        return {"style": style}

    def apply_style_from_record(self, rec: Dict[str, Any]):
        """Apply style from a JSON record dict."""
        style = rec.get("style") or {}
        if not isinstance(style, dict):
            return
        pen = style.get("pen") or {}
        fill = style.get("fill") or {}
        txt = style.get("text") or {}

        if isinstance(pen, dict):
            self.pen_color = hex_to_qcolor(pen.get("color", ""), self.pen_color)
            try:
                self.pen_width = int(pen.get("width", self.pen_width))
            except Exception:
                pass
            dash = pen.get("dash", "solid")
            if dash in ("solid", "dashed"):
                self.line_dash = dash
            # Read dash pattern settings
            try:
                if "dash_pattern_length" in pen:
                    self.dash_pattern_length = float(pen["dash_pattern_length"])
                if "dash_solid_percent" in pen:
                    self.dash_solid_percent = float(pen["dash_solid_percent"])
            except Exception:
                pass

        if isinstance(fill, dict):
            self.brush_color = hex_to_qcolor(fill.get("color", ""), self.brush_color)

        if isinstance(txt, dict):
            self.text_color = hex_to_qcolor(txt.get("color", ""), self.text_color)
            try:
                if "size_pt" in txt and txt["size_pt"] is not None:
                    self.text_size_pt = float(txt["size_pt"])
            except Exception:
                pass
            # Note: text layout options (valign, spacing) are stored in meta, not style

        arrow = style.get("arrow", "none")
        if hasattr(self, "arrow_mode") and isinstance(arrow, str):
            self.arrow_mode = arrow

        try:
            arrow_size = style.get("arrow_size")
            if arrow_size is not None:
                self.arrow_size = float(arrow_size)
        except Exception:
            pass

        try:
            if "font_size" in rec and rec["font_size"] is not None:
                self.text_size_pt = float(rec["font_size"])
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Rotation support
    # ------------------------------------------------------------------

    def _update_transform_origin(self):
        """Set the transform origin to the center of this item's local bbox.

        Must be called after any geometry change (resize, setRect, _update_path)
        so that rotation stays centered.
        """
        if hasattr(self, '_width') and hasattr(self, '_height'):
            cx, cy = self._width / 2, self._height / 2
        elif hasattr(self, 'rect') and callable(self.rect):
            sr = self.rect()
            cx, cy = sr.center().x(), sr.center().y()
        else:
            r = self.boundingRect()
            cx, cy = r.center().x(), r.center().y()
        self.setTransformOriginPoint(QPointF(cx, cy))
        self._update_child_ports()

    def _update_child_ports(self):
        """Reposition all child MetaPortItem instances after a geometry change."""
        # Import here to avoid circular dependency
        from canvas.items import MetaPortItem
        for child in self.childItems():
            if isinstance(child, MetaPortItem):
                child._update_position_from_t()
                child._update_connected_lines()

    def _update_child_port_connections(self):
        """Update connected lines on child ports after a position change.

        Unlike ``_update_child_ports``, this does NOT recompute port
        positions (t hasn't changed on a move), only snaps connected
        line/curve endpoints to follow the ports' new scene positions.
        """
        from canvas.items import MetaPortItem
        for child in self.childItems():
            if isinstance(child, MetaPortItem) and child._connections:
                child._update_connected_lines()

    def set_rotation_angle(self, angle: float):
        """Set the rotation angle (degrees, clockwise) and update the transform origin."""
        angle = angle % 360
        self._update_transform_origin()
        self.setRotation(angle)
        if MetaMixin.on_rotation_changed:
            MetaMixin.on_rotation_changed(self, angle)
        self._notify_changed()

    # ------------------------------------------------------------------
    # Rotation-aware coordinate helpers
    # ------------------------------------------------------------------

    def _scene_delta_to_local(self, dx_scene: float, dy_scene: float):
        """Convert a scene-space delta (dx, dy) into local-space delta.

        When the item is rotated, mouse movement in scene space must be
        projected onto the item's local axes for resize to follow the
        rotated edges.  Returns (dx_local, dy_local).
        """
        angle = self.rotation()
        if angle == 0:
            return dx_scene, dy_scene
        rad = math.radians(-angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        dx_local = dx_scene * cos_a - dy_scene * sin_a
        dy_local = dx_scene * sin_a + dy_scene * cos_a
        return dx_local, dy_local

    _RESIZE_ANCHOR_MAP = {
        "tl": "br", "tr": "bl", "bl": "tr", "br": "tl",
        "t": "b", "b": "t", "l": "r", "r": "l",
    }

    def _resize_anchor_local(self, handle: str) -> QPointF:
        """Return the fixed anchor point in current local coords for a resize handle."""
        if hasattr(self, '_width') and hasattr(self, '_height'):
            w, h = self._width, self._height
        elif hasattr(self, 'rect') and callable(self.rect):
            r = self.rect()
            w, h = r.width(), r.height()
        else:
            return QPointF(0, 0)
        pts = {
            "tl": QPointF(w, h),   "tr": QPointF(0, h),
            "bl": QPointF(w, 0),   "br": QPointF(0, 0),
            "t":  QPointF(w / 2, h), "b": QPointF(w / 2, 0),
            "l":  QPointF(w, h / 2), "r": QPointF(0, h / 2),
        }
        return pts.get(handle, QPointF(0, 0))

    def _store_resize_anchor(self, handle: str):
        """Snapshot the scene position of the fixed anchor at drag start."""
        self._resize_anchor_scene = self.mapToScene(
            self._resize_anchor_local(handle))

    def _compute_resize(self, handle: str, dx_local: float, dy_local: float,
                        w0: float, h0: float):
        """Compute new size and anchor-after point for a rotation-aware resize.

        Args:
            handle: Which handle is being dragged (tl/t/tr/r/br/b/bl/l).
            dx_local, dy_local: Mouse delta in item-local coordinates.
            w0, h0: Original width and height before the drag started.

        Returns:
            (new_w, new_h, anchor_after) where anchor_after is the fixed
            point expressed in the new local coords (rect 0,0,new_w,new_h).
        """
        from canvas.items import _get_min_size
        new_w, new_h = w0, h0

        if handle in ("tl", "l", "bl"):
            new_w = w0 - dx_local
        elif handle in ("tr", "r", "br"):
            new_w = w0 + dx_local

        if handle in ("tl", "t", "tr"):
            new_h = h0 - dy_local
        elif handle in ("bl", "b", "br"):
            new_h = h0 + dy_local

        min_size = _get_min_size()
        new_w = max(new_w, min_size)
        new_h = max(new_h, min_size)

        # Anchor-after = the fixed point in new local coords (rect 0,0,new_w,new_h).
        _anchor_after = {
            "tl": QPointF(new_w, new_h), "tr": QPointF(0, new_h),
            "bl": QPointF(new_w, 0),     "br": QPointF(0, 0),
            "t":  QPointF(w0 / 2, new_h),  "b": QPointF(w0 / 2, 0),
            "l":  QPointF(new_w, h0 / 2),  "r": QPointF(0, h0 / 2),
        }
        return new_w, new_h, _anchor_after[handle]

    def _fixup_resize_pos(self, anchor_after: QPointF):
        """Adjust item position so the anchor point stays fixed after resize.

        Call AFTER updating the item's rect/path and transform origin.
        Uses ``_resize_anchor_scene`` stored at drag start.

        Args:
            anchor_after: Local-space position of the anchor in the NEW geometry.
        """
        anchor_now = self.mapToScene(anchor_after)
        self.setPos(self.pos() + self._resize_anchor_scene - anchor_now)

    def _cursor_for_handle(self, handle: str):
        """Return the appropriate resize cursor for a handle, accounting for rotation.

        The double-arrow cursor rotates to match the item's orientation.
        """
        base_angles = {
            "r": 0, "l": 0,
            "br": 45, "tl": 45,
            "b": 90, "t": 90,
            "bl": 135, "tr": 135,
        }
        if handle not in base_angles:
            return Qt.CursorShape.ArrowCursor
        effective = (base_angles[handle] + self.rotation()) % 180
        if effective < 22.5 or effective >= 157.5:
            return Qt.CursorShape.SizeHorCursor
        elif effective < 67.5:
            return Qt.CursorShape.SizeFDiagCursor
        elif effective < 112.5:
            return Qt.CursorShape.SizeVerCursor
        else:
            return Qt.CursorShape.SizeBDiagCursor

    # ------------------------------------------------------------------
    # Default handle-points and hit-testing (rotation-aware)
    # ------------------------------------------------------------------

    def _handle_points_scene(self) -> Dict[str, QPointF]:
        """Return handle positions in scene coordinates (rotation-aware).

        Default implementation maps local handle points through the item's
        transform (including rotation). Subclasses only need to override
        _handle_points_local().
        """
        local = self._handle_points_local()
        return {k: self.mapToScene(v) for k, v in local.items()}

    def _hit_test_handle(self, scene_pt: QPointF) -> Optional[str]:
        """Hit-test against all handles including the rotation knob.

        Returns the handle key string or 'rotate', or None.
        Override in subclasses that need custom hit-test logic.
        """
        if not self._should_paint_handles():
            return None
        # Test rotation knob first (only for rotatable items)
        if self._is_rotatable() and self._hit_test_rotation_knob(scene_pt):
            return "rotate"
        handles = self._handle_points_scene()
        from canvas.items import _get_hit_distance
        hit_dist = _get_hit_distance()
        for k, hp in handles.items():
            if QLineF(scene_pt, hp).length() <= hit_dist:
                return k
        return None

    def _is_rotatable(self) -> bool:
        """Return True if this item supports rotation.

        Override to return False for items that don't rotate (line, text, group).
        """
        return True

    # ------------------------------------------------------------------
    # Rotation knob geometry and interaction
    # ------------------------------------------------------------------

    def _rotation_knob_local(self) -> QPointF:
        """Return rotation knob position in local coordinates (inside top-center)."""
        inset = self._ROTATION_KNOB_INSET
        if hasattr(self, '_width') and hasattr(self, '_height'):
            return QPointF(self._width / 2, inset)
        elif hasattr(self, 'rect') and callable(self.rect):
            r = self.rect()
            return QPointF(r.left() + r.width() / 2, r.top() + inset)
        return QPointF(0, inset)

    def _hit_test_rotation_knob(self, scene_pt: QPointF) -> bool:
        """Test if a scene point hits the rotation knob."""
        knob_scene = self.mapToScene(self._rotation_knob_local())
        from canvas.items import _get_hit_distance
        return QLineF(scene_pt, knob_scene).length() <= _get_hit_distance()

    def _draw_rotation_knob(self, painter):
        """Draw the rotation knob (green circle inside top-center).

        Call from paint() when _should_paint_handles() is True.
        Only draws for rotatable items.
        """
        if not self._is_rotatable():
            return
        from PyQt6.QtGui import QPen, QBrush
        from PyQt6.QtCore import QRectF

        knob_pt = self._rotation_knob_local()
        r = self._ROTATION_KNOB_RADIUS

        # Green filled circle — distinct from blue resize handles
        painter.setPen(QPen(QColor("#00AA00"), 1.5))
        painter.setBrush(QBrush(QColor("#CCFFCC")))
        painter.drawEllipse(knob_pt, r, r)

        # Small arc arrow icon inside the knob
        painter.setPen(QPen(QColor("#00AA00"), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        icon_r = r - 2
        arc_rect = QRectF(knob_pt.x() - icon_r, knob_pt.y() - icon_r, icon_r * 2, icon_r * 2)
        painter.drawArc(arc_rect, 30 * 16, 270 * 16)

    def _begin_rotation(self):
        """Start a rotation drag operation."""
        self._begin_resize_tracking()
        self._rotating = True
        self._rotation_start_angle = self.rotation()

    def _handle_rotation_move(self, event):
        """Handle mouse move during rotation drag.

        Hold Shift to snap to 15° increments.
        """
        center = self.mapToScene(self.transformOriginPoint())
        cur = event.scenePos()
        angle = math.degrees(math.atan2(
            cur.x() - center.x(), -(cur.y() - center.y())
        )) % 360
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            angle = round(angle / 15) * 15 % 360
        self.set_rotation_angle(angle)
        event.accept()

    def _end_rotation(self):
        """End a rotation drag operation."""
        self._end_resize_tracking()
        self._rotating = False
        self._notify_changed()

    def _add_angle_to_geom(self, geom: dict) -> dict:
        """Add angle to geom dict if non-zero. Call from to_record().

        No-op for non-rotatable items.
        """
        if not self._is_rotatable():
            return geom
        angle = self.rotation()
        if angle != 0:
            geom["angle"] = round(angle, 2)
        return geom
