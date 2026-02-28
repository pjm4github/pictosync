"""
models.py

Data models and constants for the Diagram Annotator application.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Any, Dict, Optional

from settings import get_settings


# ----------------------------
# Annotation metadata model
# ----------------------------

@dataclass
class AnnotationMeta:
    """Metadata for diagram annotations.

    Known fields are stored as typed attributes.  Any additional keys
    (e.g. C4-specific ``alias``, ``c4_type``, ``parent_boundary``,
    ``from_alias``, ``to_alias``, ``rel_type``, ``boundary_type``)
    are preserved in the ``extras`` dict so they survive the
    JSON → canvas → JSON round-trip.
    """
    label: str = ""            # semantic label (Component, Database, External, etc.)
    tech: str = ""             # optional (HTTPS/JSON, gRPC, Kafka, etc.)
    note: str = ""             # freeform note
    # Text formatting options
    label_align: str = "center"    # left | center | right
    label_size: int = 12           # font size in points
    tech_align: str = "center"
    tech_size: int = 10
    note_align: str = "center"
    note_size: int = 10
    # Text vertical alignment and spacing
    text_valign: str = "top"       # top | middle | bottom
    text_spacing: float = 0.0      # spacing between label/tech/note in lines (0, 0.5, 1, 1.5, 2)
    # Text bounding box for lines (0 = auto-size, no box)
    text_box_width: float = 0.0
    text_box_height: float = 0.0
    # Arbitrary extra keys preserved through round-trips
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AnnotationMeta":
        """Create an AnnotationMeta from a dict, preserving unknown keys in ``extras``.

        Args:
            d: Meta dict that may contain both known and unknown keys.

        Returns:
            An ``AnnotationMeta`` instance with extras populated.
        """
        if not isinstance(d, dict):
            return cls()
        known_names = {f.name for f in fields(cls) if f.name != "extras"}
        known = {}
        extras = {}
        for k, v in d.items():
            if k in known_names:
                known[k] = v
            else:
                extras[k] = v
        return cls(**known, extras=extras)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a plain dict, merging extras back in.

        Returns:
            Dict with known fields first, then any extras.
        """
        d = {f.name: getattr(self, f.name) for f in fields(self) if f.name != "extras"}
        d.update(self.extras)
        return d

    @classmethod
    def get_formatting_defaults(cls) -> Dict[str, Any]:
        """Get default values for formatting/layout meta fields only.

        Values are loaded from settings. Defaults if settings unavailable:
        - label_align: "center", label_size: 12
        - tech_align: "center", tech_size: 10
        - note_align: "center", note_size: 10
        - text_valign: "top", text_spacing: 0.0
        - text_box_width: 0.0, text_box_height: 0.0
        """
        defaults = get_settings().settings.defaults
        return {
            "label_align": defaults.label_align,
            "label_size": defaults.label_size,
            "tech_align": defaults.tech_align,
            "tech_size": defaults.tech_size,
            "note_align": defaults.note_align,
            "note_size": defaults.note_size,
            "text_valign": defaults.vertical_align,
            "text_spacing": defaults.line_spacing,
            "text_box_width": defaults.text_box_width,
            "text_box_height": defaults.text_box_height,
        }


def normalize_meta(meta_dict: Dict[str, Any], kind: str) -> Dict[str, Any]:
    """
    Normalize a meta dict by adding default values for missing formatting fields.

    Content fields (label, tech, note) come from extraction only.
    Formatting fields get defaults if not provided.

    Args:
        meta_dict: The meta dict to normalize (may be partial)
        kind: The item kind (rect, roundedrect, ellipse, line, text)

    Returns:
        A complete meta dict with formatting defaults applied
    """
    # Start with the extraction data (content fields)
    result = {}
    if meta_dict:
        result.update(meta_dict)

    # Add formatting defaults for missing fields only
    formatting_defaults = AnnotationMeta.get_formatting_defaults()
    for key, default_value in formatting_defaults.items():
        if key not in result:
            result[key] = default_value

    return result


# ----------------------------
# External type → PictoSync kind alias mapping
# ----------------------------

# Maps external type names (C4, PlantUML, etc.) to PictoSync annotation kinds.
# Each alias key maps to exactly one kind — uniqueness is guaranteed by dict
# structure.  Parsers call ``resolve_kind_alias()`` instead of ad-hoc checks.
#
# To add mappings for a new format (e.g. D2), add entries here.
KIND_ALIAS_MAP: Dict[str, str] = {
    # ── C4 Model types ──
    "person":                   "roundedrect",
    "external_person":          "roundedrect",
    "system":                   "roundedrect",
    "external_system":          "roundedrect",
    "system_db":                "cylinder",
    "external_system_db":       "cylinder",
    "system_queue":             "roundedrect",
    "external_system_queue":    "roundedrect",
    "container":                "roundedrect",
    "external_container":       "roundedrect",
    "container_db":             "cylinder",
    "external_container_db":    "cylinder",
    "container_queue":          "roundedrect",
    "external_container_queue": "roundedrect",
    "component":                "roundedrect",
    "external_component":       "roundedrect",
    "component_db":             "cylinder",
    "external_component_db":    "cylinder",
    "component_queue":          "roundedrect",
    "external_component_queue": "roundedrect",
    # ── PlantUML types ──
    "rectangle":  "rect",
    "database":   "cylinder",
    "actor":      "ellipse",
    "interface":  "ellipse",
    "cloud":      "ellipse",
    "node":       "rect",
    "folder":     "rect",
    "queue":      "rect",
    "participant": "rect",
    "class":      "rect",
    "entity":     "rect",
    "note":       "roundedrect",
    "title":      "text",
}


def resolve_kind_alias(external_type: str, fallback: Optional[str] = None) -> Optional[str]:
    """Resolve an external type name to a PictoSync annotation kind.

    Args:
        external_type: The external type name (e.g. ``'container_db'``,
            ``'database'``, ``'person'``).
        fallback: Kind to return if no alias match.  Defaults to ``None``.

    Returns:
        The PictoSync kind string, or *fallback* if no mapping exists.
    """
    return KIND_ALIAS_MAP.get(external_type, fallback)


# ----------------------------
# Drawing mode constants
# ----------------------------

class Mode:
    """Drawing mode constants for the annotator."""
    SELECT = "select"
    RECT = "rect"
    ROUNDEDRECT = "roundedrect"
    ELLIPSE = "ellipse"
    LINE = "line"
    TEXT = "text"
    HEXAGON = "hexagon"
    CYLINDER = "cylinder"
    BLOCKARROW = "blockarrow"
    POLYGON = "polygon"
    CURVE = "curve"
    ORTHOCURVE = "orthocurve"
    ISOCUBE = "isocube"


# ----------------------------
# Graphics item constants
# ----------------------------

ANN_ID_KEY = 1  # QGraphicsItem.data key for annotation id

# Resizable shape handle constants
# NOTE: These constants are kept for backwards compatibility.
# New code should use get_settings().settings.canvas.handles.size etc.
# Defaults: HANDLE_SIZE=8.0, HIT_DIST=10.0, MIN_SIZE=5.0
HANDLE_SIZE = 8.0  # Default: 8.0 pixels - use settings.canvas.handles.size instead
HIT_DIST = 10.0    # Default: 10.0 pixels - use settings.canvas.handles.hit_distance instead
MIN_SIZE = 5.0     # Default: 5.0 pixels - use settings.canvas.shapes.min_size instead
