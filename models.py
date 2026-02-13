"""
models.py

Data models and constants for the Diagram Annotator application.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict

from settings import get_settings


# ----------------------------
# Annotation metadata model
# ----------------------------

@dataclass
class AnnotationMeta:
    """Metadata for diagram annotations."""
    kind: str                  # rect | ellipse | roundedrect | line | text | hexagon | cylinder | blockarrow
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

    Content fields (kind, label, tech, note) come from extraction only.
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

    # Set kind from parameter
    result["kind"] = kind

    # Add formatting defaults for missing fields only
    formatting_defaults = AnnotationMeta.get_formatting_defaults()
    for key, default_value in formatting_defaults.items():
        if key not in result:
            result[key] = default_value

    return result


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
