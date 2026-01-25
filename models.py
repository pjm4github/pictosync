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
    # Text bounding box for lines (0 = auto-size, no box)
    text_box_width: float = 0.0
    text_box_height: float = 0.0


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
