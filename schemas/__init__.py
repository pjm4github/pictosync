"""
schemas/__init__.py

JSON Schema definitions and validation utilities for NanoBANANA annotation items.
Provides validation for canvas, property panel, and JSON file interchange.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple

# Try to import jsonschema for validation
try:
    import jsonschema
    from jsonschema import Draft202012Validator, ValidationError
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    ValidationError = Exception  # Fallback type

# Schema file paths
SCHEMA_DIR = os.path.dirname(os.path.abspath(__file__))
ANNOTATION_SCHEMA_PATH = os.path.join(SCHEMA_DIR, "annotation_schema.json")
GEMINI_SCHEMA_PATH = os.path.join(SCHEMA_DIR, "gemini_extraction_schema.json")

# Cached schemas
_annotation_schema: Optional[Dict] = None
_gemini_schema: Optional[Dict] = None


def get_annotation_schema() -> Dict:
    """Load and return the main annotation schema."""
    global _annotation_schema
    if _annotation_schema is None:
        with open(ANNOTATION_SCHEMA_PATH, "r", encoding="utf-8") as f:
            _annotation_schema = json.load(f)
    return _annotation_schema


def get_gemini_schema() -> Dict:
    """Load and return the Gemini extraction schema."""
    global _gemini_schema
    if _gemini_schema is None:
        with open(GEMINI_SCHEMA_PATH, "r", encoding="utf-8") as f:
            _gemini_schema = json.load(f)
    return _gemini_schema


def validate_document(data: Dict, use_gemini_schema: bool = False) -> Tuple[bool, List[str]]:
    """
    Validate a document against the appropriate schema.

    Args:
        data: The JSON data to validate
        use_gemini_schema: If True, use the Gemini extraction schema

    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    if not HAS_JSONSCHEMA:
        return True, ["jsonschema not installed, skipping validation"]

    schema = get_gemini_schema() if use_gemini_schema else get_annotation_schema()

    try:
        validator = Draft202012Validator(schema)
        errors = list(validator.iter_errors(data))

        if not errors:
            return True, []

        error_messages = []
        for error in errors:
            path = " -> ".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"
            error_messages.append(f"{path}: {error.message}")

        return False, error_messages
    except Exception as e:
        return False, [f"Validation error: {str(e)}"]


def validate_annotation(annotation: Dict) -> Tuple[bool, List[str]]:
    """
    Validate a single annotation item against the schema.

    Args:
        annotation: A single annotation dictionary

    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    if not HAS_JSONSCHEMA:
        return True, ["jsonschema not installed, skipping validation"]

    schema = get_annotation_schema()
    item_schema = schema.get("$defs", {}).get("annotationItem", {})

    if not item_schema:
        return False, ["Could not find annotationItem schema definition"]

    # Build a complete schema with definitions
    full_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$defs": schema.get("$defs", {}),
        **item_schema
    }

    try:
        validator = Draft202012Validator(full_schema)
        errors = list(validator.iter_errors(annotation))

        if not errors:
            return True, []

        error_messages = []
        for error in errors:
            path = " -> ".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"
            error_messages.append(f"{path}: {error.message}")

        return False, error_messages
    except Exception as e:
        return False, [f"Validation error: {str(e)}"]


def get_schema_for_kind(kind: str) -> Optional[Dict]:
    """
    Get the geometry schema definition for a specific item kind.

    Args:
        kind: One of 'rect', 'roundedrect', 'ellipse', 'line', 'text'

    Returns:
        The geometry schema definition or None if not found
    """
    schema = get_annotation_schema()
    defs = schema.get("$defs", {})

    kind_to_geom = {
        "rect": "rectGeometry",
        "ellipse": "rectGeometry",
        "roundedrect": "roundedRectGeometry",
        "line": "lineGeometry",
        "text": "pointGeometry",
        "hexagon": "rectGeometry",  # Uses same base geometry as rect
        "cylinder": "rectGeometry",
        "blockarrow": "rectGeometry",
    }

    geom_name = kind_to_geom.get(kind)
    if geom_name:
        return defs.get(geom_name)
    return None


def create_default_annotation(kind: str) -> Dict:
    """
    Create a default annotation of the specified kind with required fields.

    Args:
        kind: One of 'rect', 'roundedrect', 'ellipse', 'line', 'text'

    Returns:
        A dictionary with default values for the annotation
    """
    defaults = {
        "rect": {
            "kind": "rect",
            "geom": {"x": 0, "y": 0, "w": 100, "h": 50},
            "meta": {"label": "", "tech": "", "note": ""},
            "style": {
                "pen": {"color": "#FF0000", "width": 2},
                "brush": {"color": "#00000000"},
                "text": {"color": "#FFFF00", "size_pt": 12}
            }
        },
        "roundedrect": {
            "kind": "roundedrect",
            "geom": {"x": 0, "y": 0, "w": 100, "h": 50, "adjust1": 10},
            "meta": {"label": "", "tech": "", "note": ""},
            "style": {
                "pen": {"color": "#FF0000", "width": 2},
                "brush": {"color": "#00000000"},
                "text": {"color": "#FFFF00", "size_pt": 12}
            }
        },
        "ellipse": {
            "kind": "ellipse",
            "geom": {"x": 0, "y": 0, "w": 100, "h": 100},
            "meta": {"label": "", "tech": "", "note": ""},
            "style": {
                "pen": {"color": "#FF0000", "width": 2},
                "brush": {"color": "#00000000"},
                "text": {"color": "#FFFF00", "size_pt": 12}
            }
        },
        "line": {
            "kind": "line",
            "geom": {"x1": 0, "y1": 0, "x2": 100, "y2": 0},
            "meta": {"label": "", "tech": "", "note": ""},
            "style": {
                "pen": {"color": "#FF0000", "width": 2},
                "brush": {"color": "#00000000"},
                "text": {"color": "#FFFF00", "size_pt": 12},
                "arrow": "end"
            }
        },
        "text": {
            "kind": "text",
            "geom": {"x": 0, "y": 0},
            "text": "Text",
            "meta": {"label": "", "tech": "", "note": ""},
            "style": {
                "pen": {"color": "#000000", "width": 1},
                "brush": {"color": "#00000000"},
                "text": {"color": "#000000", "size_pt": 12}
            }
        },
        "hexagon": {
            "kind": "hexagon",
            "geom": {"x": 0, "y": 0, "w": 100, "h": 80, "adjust1": 0.25},
            "meta": {"label": "", "tech": "", "note": ""},
            "style": {
                "pen": {"color": "#008B8B", "width": 2},
                "brush": {"color": "#00000000"},
                "text": {"color": "#008B8B", "size_pt": 12}
            }
        },
        "cylinder": {
            "kind": "cylinder",
            "geom": {"x": 0, "y": 0, "w": 80, "h": 120, "adjust1": 0.15},
            "meta": {"label": "", "tech": "", "note": ""},
            "style": {
                "pen": {"color": "#8B008B", "width": 2},
                "brush": {"color": "#00000000"},
                "text": {"color": "#8B008B", "size_pt": 12}
            }
        },
        "blockarrow": {
            "kind": "blockarrow",
            "geom": {"x": 0, "y": 0, "w": 150, "h": 60, "adjust2": 15, "adjust1": 0.5},
            "meta": {"label": "", "tech": "", "note": ""},
            "style": {
                "pen": {"color": "#B8860B", "width": 2},
                "brush": {"color": "#00000000"},
                "text": {"color": "#B8860B", "size_pt": 12}
            }
        }
    }

    return defaults.get(kind, defaults["rect"]).copy()


# Valid item kinds
VALID_KINDS = ["rect", "roundedrect", "ellipse", "line", "text", "hexagon", "cylinder", "blockarrow", "polygon"]

# Required geometry fields per kind
REQUIRED_GEOM_FIELDS = {
    "rect": ["x", "y", "w", "h"],
    "roundedrect": ["x", "y", "w", "h"],  # adjust1 is optional with default
    "ellipse": ["x", "y", "w", "h"],
    "line": ["x1", "y1", "x2", "y2"],
    "text": ["x", "y"],
    "hexagon": ["x", "y", "w", "h"],  # adjust1 is optional with default
    "cylinder": ["x", "y", "w", "h"],  # adjust1 is optional with default
    "blockarrow": ["x", "y", "w", "h"],  # adjust1 and adjust2 are optional with defaults
    "polygon": ["x", "y", "w", "h"],  # points is optional with default
}


def quick_validate_annotation(annotation: Dict) -> Tuple[bool, str]:
    """
    Perform quick validation without full JSON Schema validation.
    Useful when jsonschema is not installed or for performance.

    Args:
        annotation: A single annotation dictionary

    Returns:
        Tuple of (is_valid, error_message or empty string)
    """
    if not isinstance(annotation, dict):
        return False, "Annotation must be a dictionary"

    kind = annotation.get("kind")
    if kind not in VALID_KINDS:
        return False, f"Invalid kind '{kind}'. Must be one of: {VALID_KINDS}"

    geom = annotation.get("geom")
    if not isinstance(geom, dict):
        return False, "Missing or invalid 'geom' field"

    required_fields = REQUIRED_GEOM_FIELDS.get(kind, [])
    for field in required_fields:
        if field not in geom:
            return False, f"Missing required geometry field '{field}' for kind '{kind}'"
        if not isinstance(geom[field], (int, float)):
            return False, f"Geometry field '{field}' must be a number"

    if kind == "text" and "text" not in annotation:
        return False, "Text items require a 'text' field"

    return True, ""


def normalize_annotation(annotation: Dict) -> Dict:
    """
    Normalize an annotation by adding missing optional fields with defaults.
    Does not modify the original dictionary.

    Args:
        annotation: A single annotation dictionary

    Returns:
        A new dictionary with normalized fields
    """
    kind = annotation.get("kind", "rect")
    default = create_default_annotation(kind)

    result = {}
    result["kind"] = kind

    # Copy ID if present
    if "id" in annotation:
        result["id"] = annotation["id"]

    # Merge geometry
    result["geom"] = {**default["geom"], **annotation.get("geom", {})}

    # Merge meta
    default_meta = default.get("meta", {})
    result["meta"] = {**default_meta, **annotation.get("meta", {})}

    # Merge style (deep merge)
    default_style = default.get("style", {})
    ann_style = annotation.get("style", {})
    result["style"] = {}
    for key in ["pen", "brush", "text"]:
        result["style"][key] = {**default_style.get(key, {}), **ann_style.get(key, {})}

    # Copy arrow for lines
    if kind == "line":
        result["style"]["arrow"] = ann_style.get("arrow", default_style.get("arrow", "none"))

    # Copy text field
    if "text" in annotation:
        result["text"] = annotation["text"]
    elif kind == "text":
        result["text"] = default.get("text", "")

    return result
