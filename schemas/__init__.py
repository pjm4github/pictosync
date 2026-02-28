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


_VALUE_VALIDATORS = frozenset({
    "pattern", "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
    "enum", "type", "const", "minLength", "maxLength", "multipleOf",
    "minItems", "maxItems", "format",
})


def validate_annotation_values(annotation: Dict) -> Tuple[bool, List[str]]:
    """Validate only value constraints (pattern, range, enum, type).

    Skips structural constraints (additionalProperties, required, oneOf)
    so extra/missing fields don't block scene rebuilds.

    Args:
        annotation: A single annotation dictionary.

    Returns:
        Tuple of (is_valid, list_of_error_messages).
    """
    if not HAS_JSONSCHEMA:
        return True, []

    schema = get_annotation_schema()
    item_schema = schema.get("$defs", {}).get("annotationItem", {})

    if not item_schema:
        return False, ["Could not find annotationItem schema definition"]

    full_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$defs": schema.get("$defs", {}),
        **item_schema
    }

    try:
        validator = Draft202012Validator(full_schema)
        errors = [
            e for e in validator.iter_errors(annotation)
            if e.validator in _VALUE_VALIDATORS
        ]

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


# -------------------------------------------------------------------------
# Schema -> expected template utilities
# -------------------------------------------------------------------------

def _resolve_ref(ref: str, defs: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve ``$ref`` like ``#/$defs/penStyle`` to its definition."""
    parts = ref.split("/")
    if len(parts) == 3 and parts[0] == "#" and parts[1] == "$defs":
        return defs.get(parts[2], {})
    return {}


def _zero_for_type(prop_def: Dict[str, Any]) -> Any:
    """Return a sensible zero/empty value for a JSON-Schema type."""
    t = prop_def.get("type")
    if t == "string":
        return ""
    if t in ("number", "integer"):
        return 0
    if t == "boolean":
        return False
    if t == "array":
        return []
    if t == "object":
        return {}
    return ""


def _extract_defaults(schema_def: Dict[str, Any], defs: Dict[str, Any]) -> Dict[str, Any]:
    """Walk a schema definition and build a dict of {prop_name: default_value}.

    - If a property has both ``$ref`` and an inline ``"default"`` (sibling
      keywords, valid in JSON Schema 2020-12), the inline default wins.
    - If a property is a ``$ref`` to an object definition, recurse.
    - If a property is a ``$ref`` to a scalar (e.g. ``colorHex``), check
      the resolved definition for a ``"default"``, else use a type-appropriate
      zero.
    - Otherwise use :func:`_zero_for_type`.
    """
    result: Dict[str, Any] = {}
    for prop_name, prop_def in schema_def.get("properties", {}).items():
        if "$ref" in prop_def:
            resolved = _resolve_ref(prop_def["$ref"], defs)
            if resolved.get("type") == "object":
                result[prop_name] = _extract_defaults(resolved, defs)
            elif "default" in prop_def:
                result[prop_name] = prop_def["default"]
            elif "default" in resolved:
                result[prop_name] = resolved["default"]
            else:
                result[prop_name] = _zero_for_type(resolved)
        elif "default" in prop_def:
            result[prop_name] = prop_def["default"]
        elif prop_def.get("type") == "object":
            result[prop_name] = _extract_defaults(prop_def, defs)
        else:
            result[prop_name] = _zero_for_type(prop_def)
    return result


def _parse_kind_overrides(item_def: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Parse the ``allOf``/``if``/``then`` blocks from ``annotationItem``.

    Returns a dict mapping each kind to its ``then`` clause.
    """
    overrides: Dict[str, Dict[str, Any]] = {}
    for rule in item_def.get("allOf", []):
        if_clause = rule.get("if", {})
        then_clause = rule.get("then", {})
        kind_props = if_clause.get("properties", {}).get("kind", {})
        kind_val = kind_props.get("const")
        if kind_val and then_clause:
            overrides[kind_val] = then_clause
    return overrides


def _deep_merge(base: dict, override: dict) -> None:
    """Recursively merge *override* into *base* in-place."""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def build_expected_from_schema(kind: str) -> Dict[str, Any]:
    """Build a complete expected annotation template from the JSON schema.

    Reads ``annotationItem`` and its ``allOf``/``if``/``then`` blocks to
    resolve the correct geometry, meta, and style for the given *kind*.
    Kind-specific inline overrides in ``then`` clauses are deep-merged
    onto the base defaults.

    Args:
        kind: The annotation kind (``rect``, ``line``, etc.).

    Returns:
        A dict with all schema-declared fields populated with defaults.
    """
    schema = get_annotation_schema()
    defs = schema.get("$defs", {})
    item_def = defs.get("annotationItem", {})
    overrides = _parse_kind_overrides(item_def)

    expected: Dict[str, Any] = {"kind": kind}

    # Get the then-clause for this kind (geometry $ref, style $ref, required)
    then_clause = overrides.get(kind, {})
    then_props = then_clause.get("properties", {})

    # Geometry — use kind-specific $ref from then-clause, fall back to base
    geom_schema = then_props.get("geom", item_def.get("properties", {}).get("geom", {}))
    if "$ref" in geom_schema:
        resolved = _resolve_ref(geom_schema["$ref"], defs)
        expected["geom"] = _extract_defaults(resolved, defs)

    # Meta — base from annotationMeta
    meta_ref = item_def.get("properties", {}).get("meta", {})
    if "$ref" in meta_ref:
        resolved = _resolve_ref(meta_ref["$ref"], defs)
        expected["meta"] = _extract_defaults(resolved, defs)

    # Strip optional domain objects that should only appear when the
    # actual annotation carries them (avoids gray "missing" noise on
    # every manually-drawn item).
    expected.get("meta", {}).pop("dsl", None)

    # Merge kind-specific meta overrides from then clause
    then_meta = then_props.get("meta", {})
    if then_meta.get("type") == "object" and "properties" in then_meta:
        meta_overrides = _extract_defaults(then_meta, defs)
        _deep_merge(expected.get("meta", {}), meta_overrides)

    # Style — always start with base styleDefinition
    base_style_ref = item_def.get("properties", {}).get("style", {})
    if "$ref" in base_style_ref:
        resolved = _resolve_ref(base_style_ref["$ref"], defs)
        expected["style"] = _extract_defaults(resolved, defs)

    # Then-clause style: $ref replaces base (e.g. lineStyleDefinition),
    # inline object deep-merges overrides onto base
    then_style = then_props.get("style", {})
    if "$ref" in then_style:
        resolved = _resolve_ref(then_style["$ref"], defs)
        expected["style"] = _extract_defaults(resolved, defs)
    elif then_style.get("type") == "object" and "properties" in then_style:
        style_overrides = _extract_defaults(then_style, defs)
        _deep_merge(expected.get("style", {}), style_overrides)

    # Remaining top-level annotationItem properties (z, etc.)
    _HANDLED = {"id", "kind", "geom", "meta", "style", "children"}
    for prop_name, prop_def in item_def.get("properties", {}).items():
        if prop_name in expected or prop_name in _HANDLED:
            continue
        if "$ref" in prop_def:
            resolved = _resolve_ref(prop_def["$ref"], defs)
            if "default" in resolved:
                expected[prop_name] = resolved["default"]
            else:
                expected[prop_name] = _zero_for_type(resolved)
        elif "default" in prop_def:
            expected[prop_name] = prop_def["default"]
        elif prop_def.get("type") in ("string",):
            expected[prop_name] = ""
        elif prop_def.get("type") in ("number", "integer"):
            expected[prop_name] = 0

    return expected


def create_default_annotation(kind: str) -> Dict:
    """Create a default annotation derived from ``annotation_schema.json``.

    Args:
        kind: The annotation kind (``rect``, ``line``, ``text``, etc.).

    Returns:
        A dictionary with default values for the annotation.
    """
    return build_expected_from_schema(kind)


# Valid item kinds
VALID_KINDS = ["rect", "roundedrect", "ellipse", "line", "text", "hexagon", "cylinder", "blockarrow", "polygon", "group"]

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
    "group": [],  # No required geometry fields
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

    # Groups use children instead of geom
    if kind == "group":
        children = annotation.get("children")
        if not isinstance(children, list):
            return False, "Group annotations require a 'children' array"
        return True, ""

    geom = annotation.get("geom")
    if not isinstance(geom, dict):
        return False, "Missing or invalid 'geom' field"

    required_fields = REQUIRED_GEOM_FIELDS.get(kind, [])
    for field in required_fields:
        if field not in geom:
            return False, f"Missing required geometry field '{field}' for kind '{kind}'"
        if not isinstance(geom[field], (int, float)):
            return False, f"Geometry field '{field}' must be a number"

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
    for key in ["pen", "fill", "text"]:
        result["style"][key] = {**default_style.get(key, {}), **ann_style.get(key, {})}

    # Copy line-specific style fields
    if kind == "line":
        result["style"]["arrow"] = ann_style.get("arrow", default_style.get("arrow", "none"))
        result["style"]["arrow_size"] = ann_style.get("arrow_size", default_style.get("arrow_size", 12))

    # Backward-compat: migrate legacy "text" field
    # Lines use meta.label for text; other kinds use meta.note
    legacy_text = annotation.get("text", "")
    if legacy_text:
        if kind == "line":
            if not result["meta"].get("label"):
                result["meta"]["label"] = legacy_text
        else:
            if not result["meta"].get("note"):
                result["meta"]["note"] = legacy_text

    # Merge remaining top-level fields (z, etc.) from defaults and annotation
    _HANDLED = {"kind", "id", "geom", "meta", "style", "text"}
    for key in default:
        if key not in result and key not in _HANDLED:
            result[key] = annotation.get(key, default[key])

    return result
