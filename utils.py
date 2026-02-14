"""
utils.py

Utility functions for the Diagram Annotator application.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional, Tuple

from PyQt6.QtGui import QColor


def strip_markdown_fences(s: str) -> str:
    """
    Strip markdown code fences from a string.

    Handles formats like:
    - ```json ... ```
    - ``` ... ```
    - ```javascript ... ```

    Args:
        s: The string potentially wrapped in markdown fences

    Returns:
        The string with markdown fences removed
    """
    ss = (s or "").strip()

    # Pattern matches: ```<optional language>\n<content>\n```
    # Handles both ```json and ``` variants
    pattern = r'^```(?:\w+)?\s*\n?(.*?)\n?```\s*$'
    match = re.match(pattern, ss, re.DOTALL)
    if match:
        return match.group(1).strip()

    return ss


def extract_first_json_object(s: str) -> Optional[dict]:
    """
    Extract the first JSON object from a string.
    Handles markdown code blocks and raw JSON.
    """
    # First, strip any markdown fences
    ss = strip_markdown_fences(s)
    ss = ss.strip()

    if ss.startswith("{") and ss.endswith("}"):
        try:
            return json.loads(ss)
        except Exception:
            pass

    start = ss.find("{")
    if start < 0:
        return None

    depth = 0
    for i in range(start, len(ss)):
        if ss[i] == "{":
            depth += 1
        elif ss[i] == "}":
            depth -= 1
            if depth == 0:
                candidate = ss[start:i + 1]
                try:
                    return json.loads(candidate)
                except Exception:
                    return None
    return None


def _looks_normalized(v: float) -> bool:
    """Check if a value looks like a normalized coordinate (0-1 range)."""
    return 0.0 <= v <= 1.5  # forgiving


def _scale_record(rec: dict, a: float, b: float, normalized: bool) -> dict:
    """
    Scale annotation coordinates by factors a (width) and b (height).

    Args:
        rec: The annotation record dict
        a: Width scale factor
        b: Height scale factor
        normalized: Whether coordinates are normalized (0-1)

    Returns:
        New dict with scaled coordinates
    """
    out = dict(rec)
    kind = out.get("kind")

    # Groups have no geom, only recurse into children
    if kind == "group":
        children = out.get("children", [])
        out["children"] = [_scale_record(c, a, b, normalized) for c in children]
        return out

    geom = dict(out.get("geom", {}) or {})

    def fx(v): return float(v) * a
    def fy(v): return float(v) * b

    # Shapes with x, y, w, h bounding box geometry
    bbox_kinds = ("rect", "ellipse", "roundedrect", "hexagon", "cylinder", "blockarrow", "polygon")

    if normalized:
        if kind in bbox_kinds:
            geom["x"] = fx(geom.get("x", 0))
            geom["y"] = fy(geom.get("y", 0))
            geom["w"] = fx(geom.get("w", 0))
            geom["h"] = fy(geom.get("h", 0))
        elif kind == "line":
            geom["x1"] = fx(geom.get("x1", 0))
            geom["y1"] = fy(geom.get("y1", 0))
            geom["x2"] = fx(geom.get("x2", 0))
            geom["y2"] = fy(geom.get("y2", 0))
        elif kind == "text":
            geom["x"] = fx(geom.get("x", 0))
            geom["y"] = fy(geom.get("y", 0))
    else:
        if kind in bbox_kinds:
            geom["x"] = fx(geom.get("x", 0))
            geom["y"] = fy(geom.get("y", 0))
            geom["w"] = fx(geom.get("w", 0))
            geom["h"] = fy(geom.get("h", 0))
        elif kind == "line":
            geom["x1"] = fx(geom.get("x1", 0))
            geom["y1"] = fy(geom.get("y1", 0))
            geom["x2"] = fx(geom.get("x2", 0))
            geom["y2"] = fy(geom.get("y2", 0))
        elif kind == "text":
            geom["x"] = fx(geom.get("x", 0))
            geom["y"] = fy(geom.get("y", 0))

    out["geom"] = geom
    return out


def qcolor_to_hex(c: QColor, include_alpha: bool = False) -> str:
    """
    Convert a QColor to a hex string.

    Args:
        c: The QColor to convert
        include_alpha: If True, include alpha channel as 4th byte

    Returns:
        Hex string like "#RRGGBB" or "#RRGGBBAA"
    """
    if include_alpha:
        return "#{:02X}{:02X}{:02X}{:02X}".format(c.red(), c.green(), c.blue(), c.alpha())
    return "#{:02X}{:02X}{:02X}".format(c.red(), c.green(), c.blue())


def hex_to_qcolor(s: str, fallback: QColor) -> QColor:
    """
    Parse a hex string to a QColor.

    Args:
        s: Hex string like "#RRGGBB" or "#RRGGBBAA"
        fallback: Color to return if parsing fails

    Returns:
        Parsed QColor or fallback
    """
    try:
        if not s:
            return QColor(fallback)
        s = s.strip()
        if s.startswith("#"):
            s = s[1:]
        if len(s) == 6:
            r = int(s[0:2], 16)
            g = int(s[2:4], 16)
            b = int(s[4:6], 16)
            return QColor(r, g, b)
        if len(s) == 8:
            r = int(s[0:2], 16)
            g = int(s[2:4], 16)
            b = int(s[4:6], 16)
            a = int(s[6:8], 16)
            return QColor(r, g, b, a)
    except Exception:
        pass
    return QColor(fallback)


# Canonical key order for annotation records
ANNOTATION_KEY_ORDER = ["id", "kind", "children", "geom", "meta", "style", "text"]


def sort_annotation_keys(rec: dict) -> dict:
    """
    Sort annotation record keys in canonical order.

    Order: id, kind, children, geom, meta, style, text
    Any keys not in this list are appended at the end in their original order.

    Args:
        rec: The annotation record dict

    Returns:
        New dict with keys sorted in canonical order
    """
    result = {}
    # Add keys in canonical order first
    for key in ANNOTATION_KEY_ORDER:
        if key in rec:
            if key == "children" and isinstance(rec[key], list):
                result[key] = [
                    sort_annotation_keys(c) if isinstance(c, dict) else c
                    for c in rec[key]
                ]
            else:
                result[key] = rec[key]
    # Add any remaining keys not in the canonical order
    for key in rec:
        if key not in result:
            result[key] = rec[key]
    return result


def sort_draft_data(data: dict) -> dict:
    """
    Sort a draft data dict, applying key ordering to all annotations.

    Args:
        data: The draft data dict with "annotations" list

    Returns:
        New dict with sorted annotation keys
    """
    result = dict(data)
    anns = result.get("annotations", [])
    if isinstance(anns, list):
        result["annotations"] = [
            sort_annotation_keys(rec) if isinstance(rec, dict) else rec
            for rec in anns
        ]
    return result


def parse_c4_text(text: str) -> Tuple[str, str, str]:
    """
    Parse C4-style text into Label, Tech, and Note components.

    Format: "Label [Tech] Note"
    - Label = everything from start up to (but not including) "["
    - Tech = content between "[" and "]" (brackets stripped - they are added in the view)
    - Note = everything after "]" to end

    Returns: (label, tech, note) tuple
    """
    if not text:
        return ("", "", "")

    label = ""
    tech = ""
    note = ""

    bracket_start = text.find("[")
    bracket_end = text.find("]")

    if bracket_start != -1 and bracket_end != -1 and bracket_end > bracket_start:
        # Has valid brackets - extract content without brackets
        label = text[:bracket_start].strip()
        tech = text[bracket_start + 1:bracket_end].strip()  # Content between brackets (no brackets)
        note = text[bracket_end + 1:].strip()
    elif bracket_start != -1:
        # Has "[" but no "]" - strip leading bracket
        label = text[:bracket_start].strip()
        tech = text[bracket_start + 1:].strip()  # Strip the leading bracket
    else:
        # No brackets - treat entire text as label
        label = text.strip()

    return (label, tech, note)
