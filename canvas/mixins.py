"""
canvas/mixins.py

Mixin classes for graphics items providing annotation ID linking and metadata handling.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from PyQt6.QtCore import Qt
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
    """

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

    def _should_paint_handles(self) -> bool:
        """Check if this item should paint selection handles.

        Returns False when the item is a child of a group, since
        the group draws its own handles.
        """
        return self.isSelected() and not isinstance(self.parentItem(), QGraphicsItemGroup)

    def set_meta(self, meta: AnnotationMeta) -> None:
        """Set the annotation metadata."""
        self.meta = meta

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
