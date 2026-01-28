"""
models.py

Data models and constants for the Diagram Annotator application.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict


# ----------------------------
# Annotation metadata model
# ----------------------------

@dataclass
class AnnotationMeta:
    """Metadata for diagram annotations."""
    kind: str                  # rect | ellipse | roundedrect | line | text
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
        """Get default values for formatting/layout meta fields only."""
        return {
            "label_align": "center",
            "label_size": 12,
            "tech_align": "center",
            "tech_size": 10,
            "note_align": "center",
            "note_size": 10,
            "text_valign": "top",
            "text_spacing": 0.0,
            "text_box_width": 0.0,
            "text_box_height": 0.0,
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


# ----------------------------
# Graphics item constants
# ----------------------------

ANN_ID_KEY = 1  # QGraphicsItem.data key for annotation id

# Resizable shape handle constants
HANDLE_SIZE = 8.0
HIT_DIST = 10.0
MIN_SIZE = 5.0
