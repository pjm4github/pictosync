"""
plantuml/parser.py

Regex-based PlantUML text parser with SVG-based or auto-layout grid positioning.

Parses .puml text to extract diagram elements and connections,
then maps them to PictoSync's JSON annotation schema.  When an SVG
render is available, pixel-accurate positions are read from the SVG;
otherwise an auto-layout grid is used as fallback.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional, Tuple

from models import normalize_meta


def _extract_text_format(text_els, ns: str = "") -> Dict[str, Any]:
    """Extract text formatting from a list of SVG ``<text>`` elements.

    Returns dict with ``text_color``, ``text_size``, ``text_family`` from
    the first text element that has styling attributes.
    """
    result: Dict[str, Any] = {}
    for t in text_els if isinstance(text_els, list) else [text_els]:
        if t is None:
            continue
        # Color: fill attribute or style fill
        fill = t.get("fill", "")
        if not fill:
            style = t.get("style", "")
            m = re.search(r'fill:\s*(#[0-9A-Fa-f]{3,8})', style)
            if m:
                fill = m.group(1)
        if fill and fill.lower() not in ("none", ""):
            result.setdefault("text_color", fill)

        # Font size
        fs = t.get("font-size", "")
        if not fs:
            style = t.get("style", "")
            m = re.search(r'font-size:\s*(\d+(?:\.\d+)?)', style)
            if m:
                fs = m.group(1)
        if fs:
            try:
                result.setdefault("text_size", float(fs))
            except ValueError:
                pass

        # Font family
        ff = t.get("font-family", "")
        if not ff:
            style = t.get("style", "")
            m = re.search(r"font-family:\s*['\"]?([^;'\"]+)", style)
            if m:
                ff = m.group(1).strip()
        if ff:
            result.setdefault("text_family", ff)

        # Stop once we have all three
        if "text_color" in result and "text_size" in result:
            break
    return result


def _normalize_annotations(annotations: List[Dict[str, Any]]) -> None:
    """Convert flat meta dicts to overlay-2.0 contents with blocks/runs.

    Replaces the ``meta`` key with ``contents`` containing ``blocks``,
    ``frame``, and ``default_format``.  Recurses into group children.
    """
    for ann in annotations:
        if isinstance(ann, dict) and "meta" in ann:
            _meta_to_contents(ann)
        # Recurse into children (nested groups)
        _normalize_annotations(ann.get("children", []))


def _meta_to_contents(ann: Dict[str, Any]) -> None:
    """Convert a single annotation's flat meta to overlay-2.0 contents."""
    from models import (AnnotationContents, CharFormat, TextBlock,
                        TextRun, TextFrame)
    meta = ann.get("meta", {})
    kind = ann.get("kind", "")

    label = meta.get("label", "")
    tech = meta.get("tech", "")
    note = meta.get("note", "")
    dsl = meta.get("dsl")

    # Text formatting from SVG (set by parser if available)
    # Fall back to per-kind settings defaults for missing values
    from settings import get_settings
    kind_defs = get_settings().get_item_defaults(kind)
    kind_color = getattr(kind_defs.contents, "color", "")
    kind_font_family = getattr(kind_defs.contents, "font_family", "")
    kind_font_size = getattr(kind_defs.contents, "font_size", 12)

    text_color = meta.get("text_color", "") or kind_color
    text_size = meta.get("text_size", 0) or kind_font_size
    text_family = meta.get("text_family", "") or kind_font_family

    label_size = text_size or meta.get("label_size", 12)
    tech_size = meta.get("tech_size", 0) or (label_size * 0.83)
    note_size = meta.get("note_size", 0) or (label_size * 0.83)

    blocks = []
    if label:
        blocks.append(TextBlock(runs=[TextRun(
            type="text", text=label,
            format=CharFormat(bold=True, font_size=label_size,
                              color=text_color, font_family=text_family))]))
    if tech:
        blocks.append(TextBlock(runs=[TextRun(
            type="text", text=tech,
            format=CharFormat(italic=True, font_size=round(tech_size, 1),
                              color=text_color, font_family=text_family))]))
    if note and note != label:
        blocks.append(TextBlock(runs=[TextRun(
            type="text", text=note,
            format=CharFormat(font_size=round(note_size, 1),
                              color=text_color, font_family=text_family))]))

    halign = meta.get("label_align", "center")
    valign = meta.get("text_valign", "top")
    frame = TextFrame(halign=halign, valign=valign)

    # Build default_format dict with only non-empty SVG-extracted values.
    # Missing keys will be filled by normalize_meta from settings defaults.
    df_dict: Dict[str, Any] = {"font_size": label_size}
    if text_color:
        df_dict["color"] = text_color
    if text_family:
        df_dict["font_family"] = text_family

    contents: Dict[str, Any] = {
        "frame": frame.to_dict(),
        "default_format": df_dict,
        "blocks": [b.to_dict() for b in blocks],
        "wrap": meta.get("wrap", True),
    }

    # Preserve extra fields (dsl, text_box_*, anchor_*)
    for key in ("text_box_width", "text_box_height", "text_anchor",
                "text_anchor_v", "anchor_value"):
        if key in meta:
            contents[key] = meta[key]
    if dsl:
        contents["dsl"] = dsl

    # Apply formatting defaults
    contents = normalize_meta(contents, kind)

    # Replace meta with contents
    ann["contents"] = contents
    del ann["meta"]


# ───────────────────────────────────────────────
# PUML element type → PictoSync kind mapping
# ───────────────────────────────────────────────

_KIND_MAP: Dict[str, str] = {
    "rectangle": "rect",
    "component": "roundedrect",
    "package": "polygon",
    "database": "cylinder",
    "actor": "ellipse",
    "participant": "rect",
    "class": "rect",
    "note": "roundedrect",
    "title": "text",
    "entity": "rect",
    "interface": "ellipse",
    "node": "rect",
    "folder": "rect",
    "cloud": "ellipse",
    "queue": "rect",
    "storage": "cylinder",
    "collections": "rect",
    "card": "roundedrect",
    "frame": "rect",
}


def _strip_puml_markup(text: str) -> str:
    """Remove PlantUML inline markup like **bold** and <color:...>tags.</color>."""
    # Remove **bold**
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    # Remove <color:...>...</color>
    text = re.sub(r'<color:[^>]+>([^<]*)</color>', r'\1', text)
    # Remove <color:#HEX> without closing (used in arrows)
    text = re.sub(r'<color:[^>]+>', '', text)
    # Remove remaining HTML-like tags
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()


def _normalize_color(color: str) -> str:
    """Normalize a PlantUML color to #RRGGBB or #RRGGBBAA format."""
    color = color.strip()
    if not color.startswith("#"):
        color = "#" + color
    # Ensure uppercase hex
    return color.upper()


def _detect_arrow_mode(polys, path_id: str = "", link_type: str = "") -> str:
    """Determine arrow mode from SVG polygon arrowheads and path ID.

    Args:
        polys: List of ``<polygon>`` elements (arrowhead markers).
        path_id: The SVG path ``id`` attribute (e.g. ``"A-to-B"`` or ``"A-backto-B"``).
        link_type: The ``data-link-type`` attribute (e.g. ``"association"``).

    Returns:
        Arrow mode: ``"none"``, ``"start"``, ``"end"``, or ``"both"``.
    """
    if link_type == "association":
        return "none"
    n = len(polys) if polys is not None else 0
    if n == 0:
        return "none"
    if n >= 2:
        return "both"
    # Single polygon — check if it's a reverse arrow
    if "backto" in path_id.lower():
        return "start"
    return "end"


def _make_line_style(
    pen_color: str = "#555555",
    pen_width: int = 2,
    dashed: bool = False,
    arrow: str = "end",
    text_color: str | None = None,
) -> Dict[str, Any]:
    """Build a line annotation style dict matching the annotation schema.

    Args:
        pen_color: Stroke colour (hex).
        pen_width: Stroke width in pixels.
        dashed: Whether the line is dashed.
        arrow: Arrowhead mode (``"none"``, ``"start"``, ``"end"``, ``"both"``).
        text_color: Label colour; defaults to *pen_color*.

    Returns:
        Complete style dict for a ``kind: "line"`` annotation.
    """
    if text_color is None:
        text_color = pen_color
    pen: Dict[str, Any] = {
        "color": pen_color,
        "width": pen_width,
        "dash": "dashed" if dashed else "solid",
        "dash_pattern_length": 30.0,
        "dash_solid_percent": 50.0,
    }
    return {
        "pen": pen,
        "fill": {"color": "#00000000"},
        "text": {"color": text_color, "size_pt": 10.0},
        "arrow_size": 12.0,
        "arrow": arrow,
    }


def _parse_label(raw: str) -> Tuple[str, str, str]:
    """Parse a PlantUML label into (label, tech, note).

    Handles multi-line labels like "Label\\nDetail" and bracketed tech.

    Args:
        raw: The raw label string from PUML.

    Returns:
        Tuple of (label, tech, note).
    """
    # Remove surrounding quotes
    raw = raw.strip().strip('"').strip("'")
    raw = _strip_puml_markup(raw)

    # Split on literal \n
    parts = re.split(r'\\n', raw)
    parts = [p.strip() for p in parts if p.strip()]

    label = parts[0] if parts else raw
    tech = parts[1] if len(parts) > 1 else ""
    note = " ".join(parts[2:]) if len(parts) > 2 else ""

    # Extract bracketed tech from label: "Name [Tech]" or "(Tech)"
    m = re.match(r'^(.+?)\s*[\[\(](.+?)[\]\)]$', label)
    if m and not tech:
        label = m.group(1).strip()
        tech = m.group(2).strip()

    return _dedup_label_tech_note(label, tech, note)


def _dedup_label_tech_note(label: str, tech: str, note: str) -> Tuple[str, str, str]:
    """Remove duplicate text across label, tech, and note fields.

    Priority order: label > tech > note.  If tech duplicates label it is
    cleared.  If note duplicates label or tech it is cleared.  Comparison
    is case-insensitive and whitespace-normalised.

    Args:
        label: Primary display text.
        tech:  Technology / stereotype text.
        note:  Description / note text.

    Returns:
        Tuple of (label, tech, note) with duplicates removed.
    """
    def _norm(s: str) -> str:
        return " ".join(s.split()).lower().strip()

    nl = _norm(label)
    nt = _norm(tech)
    nn = _norm(note)

    if nt and nt == nl:
        tech = ""
        nt = ""
    if nn:
        if nn == nl or nn == nt:
            note = ""

    return label, tech, note


# ───────────────────────────────────────────────
# Element extraction
# ───────────────────────────────────────────────

def _extract_elements(puml_text: str) -> List[Dict[str, Any]]:
    """Extract shape elements from PUML text.

    Returns:
        List of element dicts with keys: alias, puml_type, label, tech, note, color.
    """
    elements: List[Dict[str, Any]] = []
    seen_aliases: set = set()

    # Pattern for: type "Label" as alias #COLOR {
    # Also handles: type "Label" as alias #COLOR
    # And: type alias #COLOR { ... }
    # And: type "Label" as alias <<stereotype>> #COLOR
    pattern = re.compile(
        r'^\s*'
        r'(rectangle|component|package|database|actor|participant|class|entity'
        r'|interface|node|folder|cloud|queue|storage|collections|card|frame)'
        r'\s+'
        r'(?:"([^"]*?)"\s+as\s+)?'   # optional "Label" as
        r'(\w+)'                       # alias (or label if no "as")
        r'(?:\s*<<[^>]+>>)?'           # optional <<stereotype>>
        r'(?:\s*(#[0-9A-Fa-f]{3,8}))?'  # optional #COLOR
        r'(?:\s*\{)?'                   # optional opening brace
        r'\s*$',
        re.MULTILINE
    )

    for m in pattern.finditer(puml_text):
        puml_type = m.group(1)
        raw_label = m.group(2) or m.group(3)
        alias = m.group(3)
        color = m.group(4)

        if alias in seen_aliases:
            continue
        seen_aliases.add(alias)

        label, tech, note = _parse_label(raw_label)

        elements.append({
            "alias": alias,
            "puml_type": puml_type,
            "label": label,
            "tech": tech,
            "note": note,
            "color": color,
        })

    # Also match "Label" as alias pattern without type keyword for
    # elements inside class bodies — skip these (they are fields).

    # Parse title as a text element
    title_pattern = re.compile(r'^\s*title\s+(.+)$', re.MULTILINE)
    for m in title_pattern.finditer(puml_text):
        raw = m.group(1).strip()
        label = _strip_puml_markup(raw)
        alias = "__title__"
        if alias not in seen_aliases:
            seen_aliases.add(alias)
            elements.append({
                "alias": alias,
                "puml_type": "title",
                "label": label,
                "tech": "",
                "note": "",
                "color": None,
            })

    # Parse participant declarations (sequence diagrams)
    participant_pattern = re.compile(
        r'^\s*participant\s+"([^"]+)"\s+as\s+(\w+)(?:\s*(#[0-9A-Fa-f]{3,8}))?',
        re.MULTILINE
    )
    for m in participant_pattern.finditer(puml_text):
        raw_label = m.group(1)
        alias = m.group(2)
        color = m.group(3)

        if alias in seen_aliases:
            continue
        seen_aliases.add(alias)

        label, tech, note = _parse_label(raw_label)
        elements.append({
            "alias": alias,
            "puml_type": "participant",
            "label": label,
            "tech": tech,
            "note": note,
            "color": color,
        })

    # Parse class declarations: class "Label" as alias or class "Label" {
    class_pattern = re.compile(
        r'^\s*class\s+"([^"]+)"\s+as\s+(\w+)',
        re.MULTILINE
    )
    for m in class_pattern.finditer(puml_text):
        raw_label = m.group(1)
        alias = m.group(2)
        if alias in seen_aliases:
            continue
        seen_aliases.add(alias)
        label, tech, note = _parse_label(raw_label)
        elements.append({
            "alias": alias,
            "puml_type": "class",
            "label": label,
            "tech": tech,
            "note": note,
            "color": None,
        })

    return elements


# ───────────────────────────────────────────────
# Connection extraction
# ───────────────────────────────────────────────

def _extract_connections(puml_text: str, known_aliases: set) -> List[Dict[str, Any]]:
    """Extract connections (arrows) from PUML text.

    Matches patterns like:
        alias1 --> alias2 : label
        alias1 -[#color,style]-> alias2 : label
        alias1 -down-> alias2
        alias1 -> alias2
        alias1 *-down- alias2 : label  (UML composition)
        alias1 o-- alias2              (UML aggregation)

    Args:
        puml_text: The full PUML source text.
        known_aliases: Set of known element aliases (to filter false positives).

    Returns:
        List of connection dicts with keys: src, dst, label, dashed, color.
    """
    connections: List[Dict[str, Any]] = []
    seen: set = set()

    # Broad arrow pattern that captures the full arrow token, then we parse it.
    # Matches: src <arrow-chars> [optional-multiplicity] dst [: label]
    # The arrow can contain: - . * o > < | [ ] and direction keywords
    arrow_pattern = re.compile(
        r'^\s*(\w+)\s+'                                  # src alias
        r'([*o]?[-.<>|]+(?:\[([^\]]*)\])?[-.<>|]*'       # arrow start + optional [style]
        r'(?:up|down|left|right)?'                        # optional direction
        r'[-.<>|*o]*)'                                    # arrow end
        r'\s+(?:"[^"]*"\s+)?'                             # optional multiplicity "1..*"
        r'(\w+)'                                          # dst alias
        r'(?:\s*:\s*(.+))?'                               # optional : label
        r'\s*$',
        re.MULTILINE
    )

    for m in arrow_pattern.finditer(puml_text):
        src = m.group(1)
        arrow = m.group(2)
        style_bracket = m.group(3) or ""
        dst = m.group(4)
        raw_label = m.group(5) or ""

        # Only keep connections between known elements
        if src not in known_aliases or dst not in known_aliases:
            continue

        pair = (src, dst)
        if pair in seen:
            continue
        seen.add(pair)

        label = _strip_puml_markup(raw_label).replace("\\n", " ").strip()

        # Determine if dashed: ".." in arrow, or explicit "dashed" in style
        dashed = ".." in arrow
        if "dashed" in style_bracket.lower():
            dashed = True

        # Extract color from style bracket: #RRGGBB
        color = None
        color_match = re.search(r'(#[0-9A-Fa-f]{3,8})', style_bracket)
        if color_match:
            color = color_match.group(1)

        connections.append({
            "src": src,
            "dst": dst,
            "label": label,
            "dashed": dashed,
            "color": color,
        })

    return connections


# ───────────────────────────────────────────────
# SVG position extraction
# ───────────────────────────────────────────────

_SVG_NS = "http://www.w3.org/2000/svg"


def _path_bbox(d: str) -> Tuple[float, float, float, float]:
    """Extract bounding box (x, y, w, h) from an SVG path ``d`` attribute.

    Parses M/L coordinate pairs and A-command endpoints to compute the
    axis-aligned bounding box.

    Args:
        d: The SVG path ``d`` attribute string.

    Returns:
        Tuple of (x, y, width, height).
    """
    points: List[Tuple[float, float]] = []

    # M x,y and L x,y commands
    for m in re.finditer(r'[ML]\s*([-+]?\d*\.?\d+)[,\s]([-+]?\d*\.?\d+)', d):
        points.append((float(m.group(1)), float(m.group(2))))

    # A rx,ry x-rotation large-arc sweep x,y — extract endpoint
    for m in re.finditer(
        r'A\s*[-+]?\d*\.?\d+[,\s][-+]?\d*\.?\d+\s+'
        r'[-+]?\d*\.?\d+\s+'
        r'[01]\s+[01]\s+'
        r'([-+]?\d*\.?\d+)[,\s]([-+]?\d*\.?\d+)',
        d,
    ):
        points.append((float(m.group(1)), float(m.group(2))))

    # C x1,y1 x2,y2 x,y — cubic Bezier control points and endpoint
    for m in re.finditer(
        r'C\s*([-+]?\d*\.?\d+)[,\s]([-+]?\d*\.?\d+)\s+'
        r'([-+]?\d*\.?\d+)[,\s]([-+]?\d*\.?\d+)\s+'
        r'([-+]?\d*\.?\d+)[,\s]([-+]?\d*\.?\d+)',
        d,
    ):
        points.append((float(m.group(1)), float(m.group(2))))
        points.append((float(m.group(3)), float(m.group(4))))
        points.append((float(m.group(5)), float(m.group(6))))

    if not points:
        return (0.0, 0.0, 0.0, 0.0)

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    return (round(min_x, 2), round(min_y, 2), round(max_x - min_x, 2), round(max_y - min_y, 2))


def _path_to_curve_polygon(
    d: str, bx: float, by: float, bw: float, bh: float,
) -> list:
    """Extract SVG path M/C/L commands as polygon points with curve annotations.

    Produces the extended ``_rel_points`` format used by MetaPolygonItem:
    - ``[rx, ry]`` for straight segments (M, L)
    - ``[rx, ry, "C", c1x, c1y, c2x, c2y]`` for cubic bezier (C)
    - ``[rx, ry, "Q", cx, cy]`` for quadratic bezier (Q)

    All coordinates are relative (0-1) within the bounding box.

    Args:
        d: SVG path ``d`` attribute string.
        bx, by, bw, bh: Bounding box of the path.

    Returns:
        List of point entries in the extended polygon format.
    """
    if bw < 1e-6 or bh < 1e-6:
        return []

    def _rel(x: float, y: float) -> Tuple[float, float]:
        return (round((x - bx) / bw, 4), round((y - by) / bh, 4))

    points: list = []
    # Parse M (moveto) and L (lineto) — straight segments
    for m in re.finditer(r'[ML]\s*([-+]?\d*\.?\d+)[,\s]([-+]?\d*\.?\d+)', d):
        rx, ry = _rel(float(m.group(1)), float(m.group(2)))
        points.append([rx, ry])

    # Parse C (cubic bezier) — replace the last straight point with curve
    for m in re.finditer(
        r'C\s*([-+]?\d*\.?\d+)[,\s]([-+]?\d*\.?\d+)\s+'
        r'([-+]?\d*\.?\d+)[,\s]([-+]?\d*\.?\d+)\s+'
        r'([-+]?\d*\.?\d+)[,\s]([-+]?\d*\.?\d+)',
        d,
    ):
        c1x, c1y = _rel(float(m.group(1)), float(m.group(2)))
        c2x, c2y = _rel(float(m.group(3)), float(m.group(4)))
        rx, ry = _rel(float(m.group(5)), float(m.group(6)))
        points.append([rx, ry, "C", c1x, c1y, c2x, c2y])

    # Parse Q (quadratic bezier)
    for m in re.finditer(
        r'Q\s*([-+]?\d*\.?\d+)[,\s]([-+]?\d*\.?\d+)\s+'
        r'([-+]?\d*\.?\d+)[,\s]([-+]?\d*\.?\d+)',
        d,
    ):
        cx, cy = _rel(float(m.group(1)), float(m.group(2)))
        rx, ry = _rel(float(m.group(3)), float(m.group(4)))
        points.append([rx, ry, "Q", cx, cy])

    # Re-sort by order of appearance in the path string to maintain
    # the correct vertex sequence.  Each regex match has a start position.
    # Instead, let's walk the path in order.
    # --- Redo: walk commands sequentially ---
    points = []
    pos = 0
    cmd_pat = re.compile(
        r'([MLCQZz])\s*'
        r'((?:[-+]?\d*\.?\d+[,\s]*)*)',
    )
    for cm in cmd_pat.finditer(d):
        cmd = cm.group(1)
        coords_str = cm.group(2).strip()
        nums = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+', coords_str)]

        if cmd in ('M', 'L') and len(nums) >= 2:
            rx, ry = _rel(nums[0], nums[1])
            points.append([rx, ry])
        elif cmd == 'C' and len(nums) >= 6:
            c1x, c1y = _rel(nums[0], nums[1])
            c2x, c2y = _rel(nums[2], nums[3])
            rx, ry = _rel(nums[4], nums[5])
            points.append([rx, ry, "C", c1x, c1y, c2x, c2y])
        elif cmd == 'Q' and len(nums) >= 4:
            cx, cy = _rel(nums[0], nums[1])
            rx, ry = _rel(nums[2], nums[3])
            points.append([rx, ry, "Q", cx, cy])
        # Z/z — close path, no coordinates needed

    return points


def _path_points(d: str) -> List[List[float]]:
    """Extract all path vertices as relative coordinates within the bounding box.

    Parses M/L/A commands to collect all points, then normalizes them
    to 0.0–1.0 relative to the path's bounding box.

    Args:
        d: The SVG path ``d`` attribute string.

    Returns:
        List of [rx, ry] pairs (relative 0-1 within bounding box).
    """
    points: List[Tuple[float, float]] = []

    # Walk through the path string, collecting points in command order
    for m in re.finditer(
        r'([MLA])\s*'
        r'(?:(?:[-+]?\d*\.?\d+[,\s][-+]?\d*\.?\d+\s+)?'   # A: rx,ry (skip)
        r'(?:[-+]?\d*\.?\d+\s+)?'                           # A: x-rotation (skip)
        r'(?:[01]\s+[01]\s+)?)?'                             # A: flags (skip)
        r'([-+]?\d*\.?\d+)[,\s]([-+]?\d*\.?\d+)',
        d,
    ):
        points.append((float(m.group(2)), float(m.group(3))))

    if len(points) < 3:
        return []

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    w = max_x - min_x
    h = max_y - min_y

    if w < 1e-6 or h < 1e-6:
        return []

    return [
        [round((px - min_x) / w, 4), round((py - min_y) / h, 4)]
        for px, py in points
    ]


_SVG_PATH_CMD_LETTERS = set("MmCcLlQqAaZzSsTtHhVv")


def _parse_path_to_curve_nodes(
    d: str,
) -> Tuple[List[Dict[str, Any]], Tuple[float, float, float, float]]:
    """Parse an SVG path ``d`` attribute into normalised curve node dicts.

    Handles M, C, L, Q, A, and Z commands (uppercase / absolute only —
    PlantUML always emits absolute coordinates).  All anchor and control-
    point coordinates are normalised to 0–1 relative to the path bounding
    box.

    Args:
        d: The SVG path ``d`` attribute string.

    Returns:
        ``(nodes, (x, y, w, h))`` where *nodes* is a list of node dicts
        (with ``cmd``, ``x``, ``y``, and command-specific keys) and
        the tuple gives the absolute bounding box in SVG pixels.
        Returns ``([], (0, 0, 0, 0))`` on degenerate input.
    """
    tokens = re.findall(r"[MmCcLlQqAaZzSsTtHhVv]|[-+]?\d*\.?\d+", d)

    nodes: List[Dict[str, Any]] = []
    all_points: List[Tuple[float, float]] = []
    i = 0

    def _is_cmd(idx: int) -> bool:
        return idx < len(tokens) and tokens[idx] in _SVG_PATH_CMD_LETTERS

    def _f() -> float:
        nonlocal i
        val = float(tokens[i])
        i += 1
        return val

    while i < len(tokens):
        if not _is_cmd(i):
            i += 1
            continue

        cmd = tokens[i]
        i += 1
        upper = cmd.upper()

        if upper == "Z":
            nodes.append({"cmd": "Z", "x": 0.0, "y": 0.0})
            continue

        if upper == "M":
            first = True
            while i + 1 < len(tokens) and not _is_cmd(i):
                x, y = _f(), _f()
                nodes.append({"cmd": "M" if first else "L", "x": x, "y": y})
                first = False
                all_points.append((x, y))

        elif upper == "C":
            while i + 5 < len(tokens) and not _is_cmd(i):
                c1x, c1y = _f(), _f()
                c2x, c2y = _f(), _f()
                x, y = _f(), _f()
                nodes.append({
                    "cmd": "C", "x": x, "y": y,
                    "c1x": c1x, "c1y": c1y,
                    "c2x": c2x, "c2y": c2y,
                })
                all_points.extend([(c1x, c1y), (c2x, c2y), (x, y)])

        elif upper == "L":
            while i + 1 < len(tokens) and not _is_cmd(i):
                x, y = _f(), _f()
                nodes.append({"cmd": "L", "x": x, "y": y})
                all_points.append((x, y))

        elif upper == "Q":
            while i + 3 < len(tokens) and not _is_cmd(i):
                cx, cy = _f(), _f()
                x, y = _f(), _f()
                nodes.append({
                    "cmd": "Q", "x": x, "y": y,
                    "cx": cx, "cy": cy,
                })
                all_points.extend([(cx, cy), (x, y)])

        elif upper == "A":
            while i + 6 < len(tokens) and not _is_cmd(i):
                rx, ry = _f(), _f()
                rotation = _f()
                large_arc = int(_f())
                sweep = int(_f())
                x, y = _f(), _f()
                nodes.append({
                    "cmd": "A", "x": x, "y": y,
                    "rx": rx, "ry": ry,
                    "rotation": rotation,
                    "large_arc": large_arc,
                    "sweep": sweep,
                })
                all_points.append((x, y))

    if not all_points or len(nodes) < 2:
        return [], (0.0, 0.0, 0.0, 0.0)

    xs = [p[0] for p in all_points]
    ys = [p[1] for p in all_points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    w = max_x - min_x
    h = max_y - min_y

    if w < 1e-6 or h < 1e-6:
        return [], (0.0, 0.0, 0.0, 0.0)

    # Normalise coordinates to 0–1 within the bounding box
    for node in nodes:
        if node["cmd"] == "Z":
            continue
        node["x"] = round((node["x"] - min_x) / w, 4)
        node["y"] = round((node["y"] - min_y) / h, 4)
        if "c1x" in node:
            node["c1x"] = round((node["c1x"] - min_x) / w, 4)
            node["c1y"] = round((node["c1y"] - min_y) / h, 4)
        if "c2x" in node:
            node["c2x"] = round((node["c2x"] - min_x) / w, 4)
            node["c2y"] = round((node["c2y"] - min_y) / h, 4)
        if "cx" in node:
            node["cx"] = round((node["cx"] - min_x) / w, 4)
            node["cy"] = round((node["cy"] - min_y) / h, 4)

    bbox = (round(min_x, 2), round(min_y, 2), round(w, 2), round(h, 2))
    return nodes, bbox


def _parse_svg_positions(svg_path: str) -> Dict[str, Any]:
    """Parse a PlantUML-generated SVG to extract element positions and styles.

    Extracts entity rectangles, cluster bounding boxes, title position,
    link connections, and canvas dimensions from the SVG.

    Args:
        svg_path: Path to the SVG file.

    Returns:
        Dict with keys:
            canvas_w, canvas_h: int — from viewBox
            positions: Dict[alias, {x, y, w, h}]
            elements: Dict[alias, {fill, texts}]
            links: List[{src, dst, label, style}]
            id_to_alias: Dict[entity_id, alias]
    """
    tree = ET.parse(svg_path)
    root = tree.getroot()
    ns = _SVG_NS

    # Parse viewBox for canvas dimensions
    viewbox = root.get("viewBox", "").split()
    canvas_w = int(float(viewbox[2])) if len(viewbox) >= 3 else 1200
    canvas_h = int(float(viewbox[3])) if len(viewbox) >= 4 else 800

    id_to_alias: Dict[str, str] = {}
    positions: Dict[str, Dict[str, float]] = {}
    svg_elements: Dict[str, Dict[str, Any]] = {}
    parent_map: Dict[str, str] = {}  # child_alias -> parent_alias
    title_pos: Optional[Dict[str, float]] = None

    for g in root.iter(f"{{{ns}}}g"):
        cls = g.get("class", "")

        if cls == "entity":
            qname = g.get("data-qualified-name", "")
            ent_id = g.get("id", "")
            alias = qname.rsplit(".", 1)[-1] if "." in qname else qname
            if not alias:
                continue

            if "." in qname:
                parent_alias = qname.rsplit(".", 1)[0].rsplit(".", 1)[-1]
                parent_map[alias] = parent_alias

            id_to_alias[ent_id] = alias

            rect = g.find(f"{{{ns}}}rect")
            if rect is not None:
                positions[alias] = {
                    "x": round(float(rect.get("x", 0)), 2),
                    "y": round(float(rect.get("y", 0)), 2),
                    "w": round(float(rect.get("width", 0)), 2),
                    "h": round(float(rect.get("height", 0)), 2),
                }
                fill = rect.get("fill", "")
            else:
                fill = ""

            texts = [t.text for t in g.findall(f"{{{ns}}}text") if t.text]
            svg_elements[alias] = {"texts": texts, "fill": fill}

        elif cls == "cluster":
            qname = g.get("data-qualified-name", "")
            ent_id = g.get("id", "")
            alias = qname.rsplit(".", 1)[-1] if "." in qname else qname
            if not alias:
                continue

            if "." in qname:
                parent_alias = qname.rsplit(".", 1)[0].rsplit(".", 1)[-1]
                parent_map[alias] = parent_alias

            id_to_alias[ent_id] = alias

            path_el = g.find(f"{{{ns}}}path")
            rect_el = g.find(f"{{{ns}}}rect")
            # When both rect and path exist and the path is stroke-only
            # (fill="none"), the rect is the main body and the path is a
            # decorative tab (folder/frame).  Prefer the rect for geometry.
            if (
                path_el is not None
                and rect_el is not None
                and (path_el.get("fill", "").lower() in ("none", ""))
            ):
                path_el = None  # ignore decorative tab path
            if path_el is not None:
                d = path_el.get("d", "")
                x, y, w, h = _path_bbox(d)
                pos_entry: Dict[str, Any] = {"x": x, "y": y, "w": w, "h": h}
                rel_pts = _path_points(d)
                if rel_pts:
                    pos_entry["points"] = rel_pts
                positions[alias] = pos_entry
                fill = path_el.get("fill", "")
            elif rect_el is not None:
                positions[alias] = {
                    "x": round(float(rect_el.get("x", 0)), 2),
                    "y": round(float(rect_el.get("y", 0)), 2),
                    "w": round(float(rect_el.get("width", 0)), 2),
                    "h": round(float(rect_el.get("height", 0)), 2),
                }
                fill = rect_el.get("fill", "")
            else:
                fill = ""

            texts = [t.text for t in g.findall(f"{{{ns}}}text") if t.text]
            svg_elements[alias] = {"texts": texts, "fill": fill}

        elif cls == "title":
            text_el = g.find(f"{{{ns}}}text")
            if text_el is not None:
                tx = float(text_el.get("x", 0))
                ty = float(text_el.get("y", 0))
                font_size = float(text_el.get("font-size", 14))
                text_len = float(text_el.get("textLength", 200))
                title_pos = {
                    "x": round(tx, 2),
                    "y": round(ty - font_size, 2),
                    "w": round(text_len, 2),
                    "h": round(font_size * 1.5, 2),
                }

    # Parse links
    svg_links: List[Dict[str, Any]] = []
    for g in root.iter(f"{{{ns}}}g"):
        if g.get("class") != "link":
            continue
        src_id = g.get("data-entity-1", "")
        dst_id = g.get("data-entity-2", "")
        src_alias = id_to_alias.get(src_id)
        dst_alias = id_to_alias.get(dst_id)
        if not src_alias or not dst_alias:
            continue

        texts = [t.text for t in g.findall(f"{{{ns}}}text") if t.text]
        label = " ".join(texts)

        path_el = g.find(f"{{{ns}}}path")
        style = path_el.get("style", "") if path_el is not None else ""
        d_attr = path_el.get("d", "") if path_el is not None else ""
        path_id = path_el.get("id", "") if path_el is not None else ""
        polys = g.findall(f"{{{ns}}}polygon")

        svg_links.append({
            "src": src_alias,
            "dst": dst_alias,
            "label": label,
            "style": style,
            "path_d": d_attr,
            "has_arrowhead": len(polys) > 0,
            "arrow_mode": _detect_arrow_mode(polys, path_id),
        })

    return {
        "canvas_w": canvas_w,
        "canvas_h": canvas_h,
        "positions": positions,
        "elements": svg_elements,
        "links": svg_links,
        "id_to_alias": id_to_alias,
        "title_pos": title_pos,
        "parent_map": parent_map,
    }


def _apply_svg_link_style(conn: Dict[str, Any], svg_style: str) -> None:
    """Update a connection dict with color/dashed info from an SVG path style.

    Args:
        conn: Connection dict (modified in place).
        svg_style: CSS style string from the SVG ``<path>`` element.
    """
    stroke_match = re.search(r'stroke:\s*(#[0-9A-Fa-f]{3,8})', svg_style)
    if stroke_match:
        conn["color"] = stroke_match.group(1)
    if "stroke-dasharray" in svg_style:
        conn["dashed"] = True


# ───────────────────────────────────────────────
# Activity diagram ANTLR source parser
# ───────────────────────────────────────────────


def _parse_activity_source(puml_text: str) -> Dict[str, Any]:
    """Parse PlantUML activity source with the ANTLR4 grammar.

    Returns a dict with extracted semantic information::

        {
            "title": "Diagram Title",
            "actions": [
                {"text": "Action label", "color": "#Red", "stereotype": "<<input>>",
                 "swimlane": "Customer"},
                ...
            ],
            "conditions": [
                {"type": "if", "condition": "x?", "then_label": "yes",
                 "else_label": "no", "branches": [...]},
                ...
            ],
            "loops": [
                {"type": "repeat"|"while", "condition": "done?",
                 "backward": "Retry action", ...},
                ...
            ],
            "forks": [
                {"type": "fork"|"split", "branches": 3, "join_spec": "and"},
                ...
            ],
            "containers": [
                {"type": "partition", "name": "MyPartition", "color": "#E8F5E9"},
                ...
            ],
            "swimlanes": [
                {"name": "Customer", "color": "#FFE0B2"},
                ...
            ],
            "connectors": ["A", "B", "C"],
            "labels": ["retryPoint", "jumpTarget1"],
            "notes": [
                {"side": "right", "text": "Note text", "color": ""},
                ...
            ],
            "arrows": [
                {"style": "", "label": "arrow label"},
                ...
            ],
            "controls": ["start", "stop", "end", "detach", "kill", "break"],
        }

    Returns an empty dict if the grammar is unavailable or parsing fails.
    """
    try:
        from antlr4 import CommonTokenStream, InputStream
        from plantuml.grammar.generated.PlantUMLActivityLexer import PlantUMLActivityLexer
        from plantuml.grammar.generated.PlantUMLActivityParser import PlantUMLActivityParser
        from plantuml.grammar.generated.PlantUMLActivityVisitor import PlantUMLActivityVisitor
    except ImportError:
        return {}

    class _Visitor(PlantUMLActivityVisitor):
        def __init__(self):
            self.title = ""
            self.actions: List[Dict[str, Any]] = []
            self.conditions: List[Dict[str, Any]] = []
            self.loops: List[Dict[str, Any]] = []
            self.forks: List[Dict[str, Any]] = []
            self.containers: List[Dict[str, Any]] = []
            self.swimlanes: List[Dict[str, Any]] = []
            self.connectors: List[str] = []
            self.labels: List[str] = []
            self.notes: List[Dict[str, Any]] = []
            self.arrows: List[Dict[str, Any]] = []
            self.controls: List[str] = []
            self._current_swimlane = ""

        # ── Helpers ────────────────────────────────────────

        @staticmethod
        def _parse_action_token(token_text: str) -> Dict[str, str]:
            """Parse ACTION token text like '#Red:Action text;' or ':text;'.

            Returns dict with 'text', 'color', and 'bullet' keys.
            """
            t = token_text.strip()
            color = ""
            if t.startswith("#"):
                # #color:text;  — find the first ':' after '#'
                colon_idx = t.index(":")
                color = t[: colon_idx]
                t = t[colon_idx:]
            # Strip leading ':' and trailing ';'
            if t.startswith(":"):
                t = t[1:]
            if t.endswith(";"):
                t = t[:-1]
            text = t.strip()
            # Detect embedded bullet lines
            bullet = ""
            for line in text.split("\n"):
                stripped = line.strip()
                if stripped.startswith("- ") or stripped.startswith("* ") or stripped.startswith("** "):
                    bullet = stripped[0]  # '-' or '*'
                    break
            return {"text": text, "color": color, "bullet": bullet}

        @staticmethod
        def _parse_swimlane_token(token_text: str) -> Dict[str, str]:
            """Parse SWIMLANE token '|#color|Name|' or '|Name|'.

            Returns dict with 'name' and 'color' keys.
            """
            t = token_text.strip()
            # Strip outer pipes
            if t.startswith("|"):
                t = t[1:]
            if t.endswith("|"):
                t = t[:-1]
            # Trailing text after last | (title for alias form)
            parts = t.split("|")
            color = ""
            name = ""
            if len(parts) >= 2 and parts[0].startswith("#"):
                color = parts[0]
                name = parts[1].strip()
            elif len(parts) >= 1:
                name = parts[0].strip()
            return {"name": name, "color": color}

        @staticmethod
        def _parse_arrow_token(token_text: str) -> str:
            """Extract style info from ARROW token like '-[#red,bold]->'."""
            t = token_text.strip()
            if "[" in t and "]" in t:
                return t[t.index("[") + 1: t.index("]")]
            return ""

        @staticmethod
        def _paren_text(ctx) -> str:
            """Extract text from a parenContent context."""
            if ctx is None:
                return ""
            return ctx.getText().strip()

        @staticmethod
        def _parse_note_token(token_text: str) -> Dict[str, str]:
            """Parse NOTE_INLINE_TOKEN or NOTE_BLOCK_TOKEN.

            Returns dict with 'side', 'text', 'color'.
            """
            t = token_text.strip()
            side = ""
            color = ""
            text = ""

            # Inline: note left|right [#color] : text
            if ":" in t:
                before_colon, _, text = t.partition(":")
                text = text.strip()
                before_colon = before_colon.strip()
            else:
                # Block: note [left|right] [#color]\n...\nend note
                # Find first newline — everything after is body
                nl_idx = t.find("\n")
                if nl_idx >= 0:
                    before_colon = t[:nl_idx].strip()
                    body = t[nl_idx + 1:]
                    # Strip trailing 'end note'
                    end_idx = body.rfind("end note")
                    if end_idx >= 0:
                        body = body[:end_idx]
                    text = body.strip()
                else:
                    before_colon = t
                    text = ""

            lower = before_colon.lower()
            if "right" in lower:
                side = "right"
            elif "left" in lower:
                side = "left"

            # Extract #color
            import re as _re
            cm = _re.search(r'#[a-zA-Z0-9]+', before_colon)
            if cm:
                color = cm.group(0)

            return {"side": side, "text": text, "color": color}

        # ── Visitor overrides ──────────────────────────────

        def visitTitleStmt(self, ctx):
            if ctx.restOfLine():
                self.title = ctx.restOfLine().getText().strip()
            return self.visitChildren(ctx)

        def visitActionStmt(self, ctx):
            action_tok = ctx.ACTION()
            if action_tok:
                info = self._parse_action_token(action_tok.getText())
                stereo = ctx.STEREO()
                if stereo:
                    info["stereotype"] = stereo.getText().strip()
                else:
                    info["stereotype"] = ""
                info["swimlane"] = self._current_swimlane
                self.actions.append(info)
            return self.visitChildren(ctx)

        def visitListActionStmt(self, ctx):
            bullet = ""
            if ctx.BULLET_DASH():
                bullet = "-"
            elif ctx.BULLET_STAR():
                bullet = ctx.BULLET_STAR().getText()
            text = ctx.restOfLine().getText().strip() if ctx.restOfLine() else ""
            self.actions.append({
                "text": text, "color": "", "stereotype": "",
                "swimlane": self._current_swimlane,
                "bullet": bullet,
            })
            return self.visitChildren(ctx)

        def visitControlStmt(self, ctx):
            text = ctx.getText().strip()
            self.controls.append(text)
            return self.visitChildren(ctx)

        def visitSwimlaneStmt(self, ctx):
            tok = ctx.SWIMLANE()
            if tok:
                info = self._parse_swimlane_token(tok.getText())
                self._current_swimlane = info["name"]
                # Add to swimlanes list if not already present
                if not any(s["name"] == info["name"] for s in self.swimlanes):
                    self.swimlanes.append(info)
            return self.visitChildren(ctx)

        def visitConnectorStmt(self, ctx):
            id_tok = ctx.ID()
            if id_tok:
                name = id_tok.getText()
                if name not in self.connectors:
                    self.connectors.append(name)
            return self.visitChildren(ctx)

        def visitArrowStmt(self, ctx):
            arrow_tok = ctx.ARROW()
            style = self._parse_arrow_token(arrow_tok.getText()) if arrow_tok else ""
            label = ""
            if ctx.arrowLabel():
                label = ctx.arrowLabel().getText().strip()
                if label.endswith(";"):
                    label = label[:-1].strip()
            self.arrows.append({"style": style, "label": label})
            return self.visitChildren(ctx)

        def visitIfBlock(self, ctx):
            cond = self._paren_text(ctx.condExpr().parenContent()) if ctx.condExpr() else ""
            then_label = ""
            cond_op = ctx.condOp()
            if cond_op and cond_op.thenLabel() and cond_op.thenLabel().parenContent():
                then_label = self._paren_text(cond_op.thenLabel().parenContent())

            # Count branches
            elseif_count = len(ctx.elseifBranch()) if ctx.elseifBranch() else 0
            has_else = ctx.elseBranch() is not None
            else_label = ""
            if has_else and ctx.elseBranch().parenContent():
                else_label = self._paren_text(ctx.elseBranch().parenContent())

            self.conditions.append({
                "type": "if",
                "condition": cond,
                "then_label": then_label,
                "else_label": else_label,
                "elseif_count": elseif_count,
                "has_else": has_else,
            })
            return self.visitChildren(ctx)

        def visitSwitchBlock(self, ctx):
            cond = self._paren_text(ctx.condExpr().parenContent()) if ctx.condExpr() else ""
            case_count = len(ctx.caseBranch()) if ctx.caseBranch() else 0
            case_labels = []
            for cb in (ctx.caseBranch() or []):
                if cb.parenContent():
                    case_labels.append(self._paren_text(cb.parenContent()))
            self.conditions.append({
                "type": "switch",
                "condition": cond,
                "case_count": case_count,
                "case_labels": case_labels,
            })
            return self.visitChildren(ctx)

        def visitRepeatBlock(self, ctx):
            start_action = ""
            if ctx.ACTION():
                start_action = self._parse_action_token(ctx.ACTION().getText())["text"]
            cond = ""
            rw = ctx.condExpr()
            if rw and rw.parenContent():
                cond = self._paren_text(rw.parenContent())
            backward = ""
            bc = ctx.backwardClause()
            if bc and bc.ACTION():
                backward = self._parse_action_token(bc.ACTION().getText())["text"]
            # is/not labels
            is_label = ""
            not_label = ""
            rwl = ctx.repeatWhileLabels()
            if rwl:
                for pc in (rwl.parenContent() or []):
                    text = self._paren_text(pc)
                    # First parenContent after KW_IS, second after KW_NOT
                    if not is_label and rwl.KW_IS():
                        is_label = text
                    elif not not_label:
                        not_label = text
            self.loops.append({
                "type": "repeat",
                "condition": cond,
                "start_action": start_action,
                "backward": backward,
                "is_label": is_label,
                "not_label": not_label,
            })
            return self.visitChildren(ctx)

        def visitWhileBlock(self, ctx):
            cond = ""
            if ctx.condExpr() and ctx.condExpr().parenContent():
                cond = self._paren_text(ctx.condExpr().parenContent())
            is_label = ""
            # while (cond) is (label) — parenContent after KW_IS
            pcs = ctx.parenContent()
            if pcs:
                # Could be list, get first
                if isinstance(pcs, list):
                    is_label = self._paren_text(pcs[0]) if pcs else ""
                else:
                    is_label = self._paren_text(pcs)
            backward = ""
            bc = ctx.backwardClause()
            if bc and bc.ACTION():
                backward = self._parse_action_token(bc.ACTION().getText())["text"]
            end_label = ""
            # endwhile (label) — parenContent at end
            # The endwhile label parenContent is the last one outside the is()
            # Get it from the raw children after KW_ENDWHILE
            for i, child in enumerate(ctx.children or []):
                tok_text = getattr(child, 'symbol', None)
                if tok_text and hasattr(tok_text, 'text') and tok_text.text == 'endwhile':
                    # Look for LPAREN...RPAREN after endwhile
                    for j in range(i + 1, len(ctx.children)):
                        c = ctx.children[j]
                        pc_ctx = getattr(c, 'getRuleIndex', None)
                        if pc_ctx is not None:
                            try:
                                from plantuml.grammar.generated.PlantUMLActivityParser import PlantUMLActivityParser
                                if c.getRuleIndex() == PlantUMLActivityParser.RULE_parenContent:
                                    end_label = self._paren_text(c)
                            except Exception:
                                pass
                            break
                    break
            self.loops.append({
                "type": "while",
                "condition": cond,
                "is_label": is_label,
                "backward": backward,
                "end_label": end_label,
            })
            return self.visitChildren(ctx)

        def visitForkBlock(self, ctx):
            branch_count = 1 + len(ctx.forkAgainBranch() or [])
            join_spec = ""
            term = ctx.forkTerminator()
            if term:
                if term.KW_END_MERGE():
                    join_spec = "merge"
                elif term.joinSpec():
                    join_spec = term.joinSpec().ID().getText() if term.joinSpec().ID() else ""
                elif term.KW_ENDFORK():
                    join_spec = ""
            self.forks.append({
                "type": "fork",
                "branches": branch_count,
                "join_spec": join_spec,
            })
            return self.visitChildren(ctx)

        def visitSplitBlock(self, ctx):
            branch_count = 1 + len(ctx.splitAgainBranch() or [])
            self.forks.append({
                "type": "split",
                "branches": branch_count,
                "join_spec": "",
            })
            return self.visitChildren(ctx)

        def visitContainerBlock(self, ctx):
            kw = ctx.containerKeyword().getText() if ctx.containerKeyword() else ""
            name = ""
            if ctx.containerName():
                name = ctx.containerName().getText().strip().strip('"')
            color = ctx.COLOR().getText() if ctx.COLOR() else ""
            self.containers.append({
                "type": kw,
                "name": name,
                "color": color,
            })
            return self.visitChildren(ctx)

        def visitNoteStmt(self, ctx):
            tok = ctx.NOTE_INLINE_TOKEN()
            if tok:
                info = self._parse_note_token(tok.getText())
                self.notes.append(info)
            return self.visitChildren(ctx)

        def visitNoteBlock(self, ctx):
            tok = ctx.NOTE_BLOCK_TOKEN()
            if tok:
                info = self._parse_note_token(tok.getText())
                self.notes.append(info)
            return self.visitChildren(ctx)

        def visitLabelStmt(self, ctx):
            id_tok = ctx.ID()
            if id_tok:
                name = id_tok.getText()
                if name not in self.labels:
                    self.labels.append(name)
            return self.visitChildren(ctx)

        def visitGotoStmt(self, ctx):
            # Gotos reference labels — tracked in labels
            return self.visitChildren(ctx)

    try:
        input_stream = InputStream(puml_text)
        lexer = PlantUMLActivityLexer(input_stream)
        lexer.removeErrorListeners()
        token_stream = CommonTokenStream(lexer)
        parser = PlantUMLActivityParser(token_stream)
        parser.removeErrorListeners()
        tree = parser.diagram()

        visitor = _Visitor()
        visitor.visit(tree)

        return {
            "title": visitor.title,
            "actions": visitor.actions,
            "conditions": visitor.conditions,
            "loops": visitor.loops,
            "forks": visitor.forks,
            "containers": visitor.containers,
            "swimlanes": visitor.swimlanes,
            "connectors": visitor.connectors,
            "labels": visitor.labels,
            "notes": visitor.notes,
            "arrows": visitor.arrows,
            "controls": visitor.controls,
        }
    except Exception:
        return {}


def _merge_activity_source_info(
    annotations: List[Dict[str, Any]],
    src_info: Dict[str, Any],
) -> None:
    """Merge ANTLR-parsed activity source info into SVG annotations.

    Enriches ``contents.dsl`` (or ``meta.dsl``) with activity-specific
    semantic data from the ANTLR parse: stereotypes, swimlane membership,
    condition expressions, loop types, fork join specs, container types,
    notes, connectors, labels, and arrows.

    Args:
        annotations: List of annotation dicts (mutated in-place).
        src_info: Dict returned by ``_parse_activity_source()``.
    """
    if not src_info:
        return

    actions = list(src_info.get("actions", []))
    conditions = list(src_info.get("conditions", []))
    loops = list(src_info.get("loops", []))
    forks = list(src_info.get("forks", []))
    containers = list(src_info.get("containers", []))
    swimlanes = src_info.get("swimlanes", [])
    notes_list = list(src_info.get("notes", []))
    arrows_list = list(src_info.get("arrows", []))
    controls = list(src_info.get("controls", []))
    connectors = src_info.get("connectors", [])
    labels = src_info.get("labels", [])

    # Build swimlane name→color index
    lane_colors: Dict[str, str] = {}
    for sl in swimlanes:
        if sl.get("color"):
            lane_colors[sl["name"]] = sl["color"]

    # Build action text → info index for matching
    action_index: Dict[str, Dict[str, Any]] = {}
    for a in actions:
        key = a["text"].strip().lower()
        # Use first line for matching (multi-line actions)
        first_line = key.split("\n")[0].strip()
        if first_line:
            action_index[first_line] = a
        if key != first_line and key:
            action_index[key] = a

    def _get_label(ann: Dict[str, Any]) -> str:
        """Extract label text from annotation (contents or meta)."""
        contents = ann.get("contents") or ann.get("meta") or {}
        blocks = contents.get("blocks", [])
        if blocks:
            for b in blocks:
                for r in b.get("runs", []):
                    t = r.get("text", "").strip()
                    if t:
                        return t
        return contents.get("label", "")

    def _set_dsl(ann: Dict[str, Any], dsl_data: Dict[str, Any]) -> None:
        """Set dsl data on annotation's contents or meta."""
        target = ann.get("contents") or ann.get("meta")
        if target is None:
            return
        existing_dsl = target.get("dsl", {})
        existing_dsl.update(dsl_data)
        target["dsl"] = existing_dsl

    def _enrich(ann_list: List[Dict[str, Any]]) -> None:
        for ann in ann_list:
            kind = ann.get("kind", "")
            label = _get_label(ann).lower()
            first_line = label.split("\n")[0].strip()

            # Match activities (roundedrect) to ANTLR actions
            if kind == "roundedrect" and first_line:
                match = action_index.get(first_line) or action_index.get(label)
                if match:
                    dsl: Dict[str, Any] = {"element_type": "action"}
                    if match.get("stereotype"):
                        dsl["stereotype"] = match["stereotype"]
                    if match.get("color"):
                        dsl["action_color"] = match["color"]
                    if match.get("swimlane"):
                        dsl["swimlane"] = match["swimlane"]
                        if match["swimlane"] in lane_colors:
                            dsl["swimlane_color"] = lane_colors[match["swimlane"]]
                    if match.get("bullet"):
                        dsl["bullet"] = match["bullet"]
                    _set_dsl(ann, dsl)

            # Match ellipses (start/stop/end nodes) to controls
            elif kind == "ellipse":
                if controls:
                    ctrl = controls[0]
                    if label.lower() in ("start", "end", "stop"):
                        _set_dsl(ann, {"element_type": ctrl})
                        # Don't pop — there might be multiple start/stop

            # Match diamonds (conditions) to ANTLR conditions
            elif kind == "diamond":
                if conditions:
                    cond = conditions.pop(0)
                    dsl = {"element_type": cond["type"],
                           "condition": cond.get("condition", "")}
                    if cond["type"] == "if":
                        dsl["then_label"] = cond.get("then_label", "")
                        dsl["else_label"] = cond.get("else_label", "")
                        dsl["elseif_count"] = cond.get("elseif_count", 0)
                    elif cond["type"] == "switch":
                        dsl["case_labels"] = cond.get("case_labels", [])
                    _set_dsl(ann, dsl)

            # Match partition rects to containers
            elif kind == "rect":
                for ci, cont in enumerate(containers):
                    cname = cont["name"].lower()
                    if cname and (cname == first_line or cname in label):
                        dsl = {
                            "element_type": cont["type"],
                            "container_name": cont["name"],
                        }
                        if cont.get("color"):
                            dsl["container_color"] = cont["color"]
                        _set_dsl(ann, dsl)
                        containers.pop(ci)
                        break

            # Match lines to ANTLR arrows by order
            elif kind == "line":
                if arrows_list:
                    arrow = arrows_list.pop(0)
                    dsl = {"element_type": "arrow"}
                    if arrow.get("style"):
                        dsl["arrow_style"] = arrow["style"]
                    if arrow.get("label"):
                        dsl["arrow_label"] = arrow["label"]
                    _set_dsl(ann, dsl)

            # Recurse into group children
            children = ann.get("children", [])
            if children:
                _enrich(children)

    _enrich(annotations)

    # Add diagram-level DSL metadata to first annotation or as standalone
    diagram_dsl = {}
    if src_info.get("title"):
        diagram_dsl["title"] = src_info["title"]
    if swimlanes:
        diagram_dsl["swimlanes"] = swimlanes
    if connectors:
        diagram_dsl["connectors"] = connectors
    if labels:
        diagram_dsl["labels"] = labels
    if notes_list:
        diagram_dsl["notes"] = notes_list
    if forks:
        diagram_dsl["forks"] = forks
    if loops:
        diagram_dsl["loops"] = loops
    if conditions:
        diagram_dsl["remaining_conditions"] = conditions
    if controls:
        diagram_dsl["controls"] = controls

    if diagram_dsl and annotations:
        _set_dsl(annotations[0], {"diagram": diagram_dsl})


# ───────────────────────────────────────────────
# Activity diagram SVG parser
# ───────────────────────────────────────────────


def _parse_activity_diagram_svg(
    tree: ET.ElementTree,
    puml_text: str = "",
) -> Dict[str, Any]:
    """Parse an activity diagram SVG into PictoSync annotations.

    Activity diagram SVGs use a flat structure with raw shapes rather
    than classified ``<g>`` groups.  Elements are identified by shape
    type: rounded ``<rect>`` for activities, plain ``<rect>`` for
    partition containers.

    Args:
        tree: Parsed ElementTree of the SVG file.

    Returns:
        Dict with PictoSync schema: ``{"version", "image", "annotations"}``.
    """
    root = tree.getroot()
    ns = _SVG_NS

    # Canvas dimensions from viewBox
    viewbox = root.get("viewBox", "").split()
    canvas_w = int(float(viewbox[2])) if len(viewbox) >= 3 else 1200
    canvas_h = int(float(viewbox[3])) if len(viewbox) >= 4 else 800

    empty: Dict[str, Any] = {
        "version": "draft-1",
        "image": {"width": canvas_w, "height": canvas_h},
        "annotations": [],
    }

    root_g = root.find(f"{{{ns}}}g")
    if root_g is None:
        return empty

    # ── Collect elements from the root <g> ─────────────────
    all_rects: List[ET.Element] = []
    all_texts: List[ET.Element] = []
    all_lines: List[ET.Element] = []
    all_ellipses: List[ET.Element] = []
    title_text = ""
    title_pos: Optional[Dict[str, float]] = None

    for child in root_g:
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "rect":
            all_rects.append(child)
        elif tag == "text":
            all_texts.append(child)
        elif tag == "line":
            all_lines.append(child)
        elif tag == "ellipse":
            all_ellipses.append(child)
        elif tag == "g" and child.get("class") == "title":
            text_el = child.find(f"{{{ns}}}text")
            if text_el is not None:
                tx = float(text_el.get("x", 0))
                ty = float(text_el.get("y", 0))
                fs = float(text_el.get("font-size", 14))
                tl = float(text_el.get("textLength", 200))
                title_text = text_el.text or ""
                title_pos = {
                    "x": round(tx, 2),
                    "y": round(ty - fs, 2),
                    "w": round(tl, 2),
                    "h": round(fs * 1.5, 2),
                }

    # Need at least a background rect + one shape rect
    if len(all_rects) < 2:
        return empty

    # First rect is always the background fill — skip it
    shape_rects = all_rects[1:]

    # ── Classify rects ─────────────────────────────────────
    activity_rects: List[ET.Element] = []
    partition_rects: List[ET.Element] = []

    for rect in shape_rects:
        rx = float(rect.get("rx", 0))
        if rx > 0:
            activity_rects.append(rect)
        else:
            partition_rects.append(rect)

    # ── Helpers ────────────────────────────────────────────

    def _bounds(rect_el: ET.Element) -> Tuple[float, float, float, float]:
        return (
            round(float(rect_el.get("x", 0)), 2),
            round(float(rect_el.get("y", 0)), 2),
            round(float(rect_el.get("width", 0)), 2),
            round(float(rect_el.get("height", 0)), 2),
        )

    def _texts_inside(
        rect_el: ET.Element, margin: float = 5.0,
    ) -> List[ET.Element]:
        x, y, w, h = _bounds(rect_el)
        return [
            t for t in all_texts
            if (x - margin <= float(t.get("x", 0)) <= x + w + margin
                and y - margin <= float(t.get("y", 0)) <= y + h + margin)
        ]

    def _extract_stroke(
        rect_el: ET.Element,
    ) -> Tuple[str, int]:
        style = rect_el.get("style", "")
        sm = re.search(r'stroke:\s*(#[0-9A-Fa-f]{3,8})', style)
        wm = re.search(r'stroke-width:\s*(\d+(?:\.\d+)?)', style)
        return (
            sm.group(1).upper() if sm else "#000000",
            int(float(wm.group(1))) if wm else 1,
        )

    def _safe_fill(fill: str) -> str:
        if not fill or fill.lower() == "none" or not fill.startswith("#"):
            return "#00000000"
        return _normalize_color(fill)

    def _contains(
        ox: float, oy: float, ow: float, oh: float,
        ix: float, iy: float, iw: float, ih: float,
        margin: float = 2,
    ) -> bool:
        """Return True if outer rect fully contains inner rect."""
        return (
            ox - margin <= ix
            and oy - margin <= iy
            and ix + iw <= ox + ow + margin
            and iy + ih <= oy + oh + margin
        )

    # ── Build activity annotations ─────────────────────────
    counter = 1

    # Title annotation
    title_ann: Optional[Dict[str, Any]] = None
    if title_pos and title_text:
        ann_id = f"p{counter:06d}"
        counter += 1
        title_ann = {
            "id": ann_id,
            "kind": "text",
            "geom": dict(title_pos),
            "meta": {
                "label": title_text, "tech": "",
                "note": title_text,
            },
            "style": {
                "pen": {"color": "#555555", "width": 2, "dash": "solid"},
                "fill": {"color": "#00000000"},
                "text": {"color": "#000000", "size_pt": 12.0},
            },
        }

    # Activities (rounded rects)
    act_anns: Dict[int, Dict[str, Any]] = {}  # index → annotation

    for i, rect in enumerate(activity_rects):
        texts = _texts_inside(rect)
        text_lines = [t.text for t in texts if t.text]
        label = "\n".join(text_lines) if text_lines else "Activity"
        fill = _safe_fill(rect.get("fill", ""))
        stroke_color, stroke_width = _extract_stroke(rect)
        x, y, w, h = _bounds(rect)

        ann_id = f"p{counter:06d}"
        counter += 1
        act_anns[i] = {
            "id": ann_id,
            "kind": "roundedrect",
            "geom": {"x": x, "y": y, "w": w, "h": h},
            "meta": {
                "label": label, "tech": "",
                "note": label,
            },
            "style": {
                "pen": {
                    "color": stroke_color, "width": stroke_width, "dash": "solid",
                },
                "fill": {"color": fill},
                "text": {"color": "#000000", "size_pt": 11.0},
            },
        }

    # ── Build partition data ───────────────────────────────
    part_list: List[Dict[str, Any]] = []

    for rect in partition_rects:
        texts = _texts_inside(rect)
        bold = [t for t in texts if t.get("font-weight") == "bold"]
        title = bold[0].text if bold else ""
        fill = _safe_fill(rect.get("fill", ""))
        stroke_color, stroke_width = _extract_stroke(rect)
        x, y, w, h = _bounds(rect)

        ann_id = f"p{counter:06d}"
        counter += 1
        part_list.append({
            "ann": {
                "id": ann_id,
                "kind": "rect",
                "geom": {"x": x, "y": y, "w": w, "h": h},
                "meta": {
                    "label": title, "tech": "",
                    "note": title,
                },
                "style": {
                    "pen": {
                        "color": stroke_color, "width": stroke_width,
                        "dash": "solid",
                    },
                    "fill": {"color": fill},
                    "text": {"color": "#000000", "size_pt": 11.0},
                },
            },
            "x": x, "y": y, "w": w, "h": h,
            "area": w * h,
        })

    # Sort partitions by area (smallest first) for containment lookup
    part_list.sort(key=lambda p: p["area"])

    # ── Containment mapping ────────────────────────────────
    # Activity → smallest containing partition
    act_to_part: Dict[int, int] = {}
    for ai, rect in enumerate(activity_rects):
        ax, ay, aw, ah = _bounds(rect)
        for pi, pd in enumerate(part_list):
            if _contains(pd["x"], pd["y"], pd["w"], pd["h"],
                         ax, ay, aw, ah):
                act_to_part[ai] = pi
                break

    # Partition → smallest containing parent partition
    part_to_parent: Dict[int, int] = {}
    for pi, pd in enumerate(part_list):
        for pj, pd2 in enumerate(part_list):
            if pi == pj:
                continue
            if (pd2["area"] > pd["area"]
                    and _contains(pd2["x"], pd2["y"], pd2["w"], pd2["h"],
                                  pd["x"], pd["y"], pd["w"], pd["h"])):
                part_to_parent[pi] = pj
                break

    # ── Build group annotations (bottom-up) ────────────────
    # Collect direct activity children for each partition
    part_children: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
    for ai, pi in act_to_part.items():
        part_children[pi].append(act_anns[ai])

    def _child_y(ann: Dict[str, Any]) -> float:
        if "geom" in ann:
            g = ann["geom"]
            return g.get("y", g.get("y1", 0))
        if ann.get("children"):
            return _child_y(ann["children"][0])
        return 0.0

    part_groups: Dict[int, Dict[str, Any]] = {}

    for pi, pd in enumerate(part_list):
        direct_acts = list(part_children.get(pi, []))

        # Collect nested partition groups whose parent is this partition
        nested = []
        for pj in range(len(part_list)):
            if part_to_parent.get(pj) == pi:
                nested.append(part_groups.get(pj, part_list[pj]["ann"]))

        # Interleave nested groups and direct activities by Y position
        mixed = nested + direct_acts
        mixed.sort(key=_child_y)

        # Partition rect as first child + sorted contents
        all_children = [pd["ann"]] + mixed

        if len(all_children) > 1:
            group_id = "g" + pd["ann"]["id"][1:]
            part_groups[pi] = {
                "id": group_id,
                "kind": "group",
                "children": all_children,
                "meta": {
                    "label": pd["ann"]["meta"]["label"],
                    "tech": "",
                    "note": pd["ann"]["meta"].get("note", ""),
                },
                "style": pd["ann"]["style"],
            }

    # ── Ellipse annotations (start/end nodes) ─────────────
    ellipse_anns: List[Dict[str, Any]] = []
    seen_centers: set = set()

    for ell in all_ellipses:
        cx = float(ell.get("cx", 0))
        cy = float(ell.get("cy", 0))
        center_key = (round(cx, 1), round(cy, 1))
        if center_key in seen_centers:
            continue  # Skip concentric ellipse (end-node inner circle)
        seen_centers.add(center_key)

        # Use the largest radius among concentric ellipses at this center
        max_rx = 0.0
        max_ry = 0.0
        for e in all_ellipses:
            if (round(float(e.get("cx", 0)), 1),
                    round(float(e.get("cy", 0)), 1)) == center_key:
                erx = float(e.get("rx", 0))
                ery = float(e.get("ry", 0))
                if erx > max_rx:
                    max_rx = erx
                    max_ry = ery

        fill = ell.get("fill", "#FFFFFF")
        stroke_color, stroke_width = _extract_stroke(ell)
        label = "Start" if cy < canvas_h / 2 else "End"

        ann_id = f"p{counter:06d}"
        counter += 1
        ellipse_anns.append({
            "id": ann_id,
            "kind": "ellipse",
            "geom": {
                "x": round(cx - max_rx, 2), "y": round(cy - max_ry, 2),
                "w": round(max_rx * 2, 2), "h": round(max_ry * 2, 2),
            },
            "meta": {
                "label": label, "tech": "",
                "note": label,
            },
            "style": {
                "pen": {
                    "color": stroke_color, "width": stroke_width, "dash": "solid",
                },
                "fill": {"color": _safe_fill(fill)},
                "text": {"color": "#000000", "size_pt": 11.0},
            },
        })

    # ── Line annotations (flow connectors) ─────────────────
    # Each <line> is paired with a <polygon> arrowhead in the SVG;
    # we emit a single line annotation with arrow style per connector.
    line_anns: List[Dict[str, Any]] = []

    for line_el in all_lines:
        x1 = float(line_el.get("x1", 0))
        y1_val = float(line_el.get("y1", 0))
        x2 = float(line_el.get("x2", 0))
        y2_val = float(line_el.get("y2", 0))

        stroke_color, stroke_width = _extract_stroke(line_el)

        ann_id = f"p{counter:06d}"
        counter += 1
        line_anns.append({
            "id": ann_id,
            "kind": "line",
            "geom": {"x1": round(x1, 2), "y1": round(y1_val, 2), "x2": round(x2, 2), "y2": round(y2_val, 2)},
            "meta": {"label": "", "tech": "", "note": ""},
            "style": _make_line_style(stroke_color, stroke_width),
        })

    # ── Collect top-level annotations ──────────────────────
    top_level: List[Dict[str, Any]] = []

    if title_ann:
        top_level.append(title_ann)

    # Top-level activities (not inside any partition)
    for ai, ann in act_anns.items():
        if ai not in act_to_part:
            top_level.append(ann)

    # Top-level partitions (not inside any parent partition)
    for pi in range(len(part_list)):
        if pi not in part_to_parent:
            top_level.append(part_groups.get(pi, part_list[pi]["ann"]))

    # Ellipses and lines are always top-level
    top_level.extend(ellipse_anns)
    top_level.extend(line_anns)

    # Sort everything after title by Y coordinate
    if title_ann and len(top_level) > 1:
        rest = top_level[1:]
        rest.sort(key=_child_y)
        top_level = [title_ann] + rest
    else:
        top_level.sort(key=_child_y)

    _normalize_annotations(top_level)

    # ── Enrich with ANTLR activity source semantics ──
    if puml_text:
        src_info = _parse_activity_source(puml_text)
        if src_info:
            _merge_activity_source_info(top_level, src_info)

    return {
        "version": "draft-1",
        "image": {"width": canvas_w, "height": canvas_h},
        "annotations": top_level,
    }


# ───────────────────────────────────────────────
# Sequence diagram source parser (ANTLR4)
# ───────────────────────────────────────────────


def _parse_sequence_source(puml_text: str) -> Dict[str, Any]:
    """Parse PlantUML sequence diagram source with the ANTLR4 grammar.

    Returns a dict with extracted semantic information::

        {
            "title": "Diagram Title",
            "participants": [
                {"name": "Alice", "keyword": "participant", "alias": "",
                 "stereotype": "", "color": ""},
                ...
            ],
            "messages": [
                {"source": "Alice", "target": "Bob", "label": "hello",
                 "arrow": "->"},
                ...
            ],
            "groups": [
                {"keyword": "alt", "label": "condition"},
                ...
            ],
            "notes": [
                {"text": "some note"},
                ...
            ],
            "activations": 0,
            "deactivations": 0,
            "destroys": 0,
            "returns": 0,
            "boxes": [
                {"name": "Internal", "color": "#LightBlue"},
                ...
            ],
            "dividers": 0,
            "refs": 0,
            "newpages": 0,
            "creates": 0,
        }

    Returns an empty dict if the grammar is unavailable or parsing fails.
    """
    try:
        from antlr4 import CommonTokenStream, InputStream
        from plantuml.grammar.generated.PlantUMLSequenceLexer import PlantUMLSequenceLexer
        from plantuml.grammar.generated.PlantUMLSequenceParser import PlantUMLSequenceParser
        from plantuml.grammar.generated.PlantUMLSequenceVisitor import PlantUMLSequenceVisitor
    except ImportError:
        return {}

    class _Visitor(PlantUMLSequenceVisitor):
        def __init__(self):
            self.title = ""
            self.participants: List[Dict[str, str]] = []
            self.messages: List[Dict[str, str]] = []
            self.groups: List[Dict[str, str]] = []
            self.notes: List[Dict[str, str]] = []
            self.activations = 0
            self.deactivations = 0
            self.destroys = 0
            self.returns = 0
            self.boxes: List[Dict[str, str]] = []
            self.dividers = 0
            self.refs = 0
            self.newpages = 0
            self.creates = 0

        # ── Helpers ────────────────────────────────────────

        @staticmethod
        def _strip_quotes(text: str) -> str:
            """Remove surrounding double-quotes if present."""
            if len(text) >= 2 and text.startswith('"') and text.endswith('"'):
                return text[1:-1]
            return text

        @staticmethod
        def _participant_name_text(ctx) -> str:
            """Extract cleaned name from a participantName context."""
            if ctx is None:
                return ""
            raw = ctx.getText().strip()
            if len(raw) >= 2 and raw.startswith('"') and raw.endswith('"'):
                return raw[1:-1]
            return raw

        # ── Visitor overrides ──────────────────────────────

        def visitTitleStmt(self, ctx):
            if ctx.restOfLine():
                self.title = ctx.restOfLine().getText().strip()
            return self.visitChildren(ctx)

        def visitTitleBlock(self, ctx):
            # Multi-line title — collect noteBodyLine texts
            lines = []
            for bl in (ctx.noteBodyLine() or []):
                lines.append(bl.getText().strip())
            if lines:
                self.title = "\n".join(lines)
            return self.visitChildren(ctx)

        def visitParticipantDecl(self, ctx):
            keyword = ""
            pt = ctx.participantType()
            if pt and pt.participantKeyword():
                keyword = pt.participantKeyword().getText().strip()
            name = self._participant_name_text(ctx.participantName())
            alias = ""
            ac = ctx.aliasClause()
            if ac and ac.participantName():
                alias = self._participant_name_text(ac.participantName())
            stereotype = ""
            color = ""
            for mod in (ctx.participantModifier() or []):
                sc = mod.stereotypeClause()
                if sc:
                    stereotype = sc.getText().strip()
                cs = mod.colorSpec()
                if cs:
                    color = cs.getText().strip()
            self.participants.append({
                "name": name,
                "keyword": keyword,
                "alias": alias,
                "stereotype": stereotype,
                "color": color,
            })
            return self.visitChildren(ctx)

        def visitMessageStmt(self, ctx):
            # Source
            src_ctx = ctx.messageSource()
            source = ""
            if src_ctx:
                pr = src_ctx.participantRef()
                if pr and pr.participantName():
                    source = self._participant_name_text(pr.participantName())
                elif src_ctx.LBRACK():
                    source = "["
                elif src_ctx.QMARK():
                    source = "?"

            # Target
            tgt_ctx = ctx.messageTarget()
            target = ""
            if tgt_ctx:
                pr = tgt_ctx.participantRef()
                if pr and pr.participantName():
                    target = self._participant_name_text(pr.participantName())
                elif tgt_ctx.RBRACK():
                    target = "]"
                elif tgt_ctx.QMARK():
                    target = "?"

            # Arrow
            arrow = ""
            as_ctx = ctx.arrowSpec()
            if as_ctx and as_ctx.ARROW():
                arrow = as_ctx.ARROW().getText().strip()

            # Label
            label = ""
            ml = ctx.messageLabel()
            if ml:
                label = ml.getText().strip()

            self.messages.append({
                "source": source,
                "target": target,
                "label": label,
                "arrow": arrow,
            })
            return self.visitChildren(ctx)

        def visitGroupBlock(self, ctx):
            keyword = ""
            gk = ctx.groupKeyword()
            if gk:
                keyword = gk.getText().strip()
            label = ""
            gl = ctx.groupLabel()
            if gl:
                label = gl.getText().strip()
            self.groups.append({"keyword": keyword, "label": label})
            return self.visitChildren(ctx)

        def visitNoteStmt(self, ctx):
            text = ""
            rol = ctx.restOfLine()
            if rol:
                text = rol.getText().strip()
            self.notes.append({"text": text})
            return self.visitChildren(ctx)

        def visitNoteBlock(self, ctx):
            lines = []
            for bl in (ctx.noteBodyLine() or []):
                lines.append(bl.getText().strip())
            text = "\n".join(lines) if lines else ""
            self.notes.append({"text": text})
            return self.visitChildren(ctx)

        def visitActivateStmt(self, ctx):
            self.activations += 1
            return self.visitChildren(ctx)

        def visitDeactivateStmt(self, ctx):
            self.deactivations += 1
            return self.visitChildren(ctx)

        def visitDestroyStmt(self, ctx):
            self.destroys += 1
            return self.visitChildren(ctx)

        def visitReturnStmt(self, ctx):
            self.returns += 1
            return self.visitChildren(ctx)

        def visitBoxBlock(self, ctx):
            name = ""
            qs = ctx.QUOTED_STRING()
            if qs:
                name = self._strip_quotes(qs.getText().strip())
            color = ""
            cs = ctx.colorSpec()
            if cs:
                color = cs.getText().strip()
            self.boxes.append({"name": name, "color": color})
            return self.visitChildren(ctx)

        def visitDividerStmt(self, ctx):
            self.dividers += 1
            return self.visitChildren(ctx)

        def visitRefStmt(self, ctx):
            self.refs += 1
            return self.visitChildren(ctx)

        def visitRefBlock(self, ctx):
            self.refs += 1
            return self.visitChildren(ctx)

        def visitNewpageStmt(self, ctx):
            self.newpages += 1
            return self.visitChildren(ctx)

        def visitCreateStmt(self, ctx):
            self.creates += 1
            return self.visitChildren(ctx)

    try:
        input_stream = InputStream(puml_text)
        lexer = PlantUMLSequenceLexer(input_stream)
        lexer.removeErrorListeners()
        token_stream = CommonTokenStream(lexer)
        parser = PlantUMLSequenceParser(token_stream)
        parser.removeErrorListeners()
        tree = parser.diagram()

        visitor = _Visitor()
        visitor.visit(tree)

        return {
            "title": visitor.title,
            "participants": visitor.participants,
            "messages": visitor.messages,
            "groups": visitor.groups,
            "notes": visitor.notes,
            "activations": visitor.activations,
            "deactivations": visitor.deactivations,
            "destroys": visitor.destroys,
            "returns": visitor.returns,
            "boxes": visitor.boxes,
            "dividers": visitor.dividers,
            "refs": visitor.refs,
            "newpages": visitor.newpages,
            "creates": visitor.creates,
        }
    except Exception:
        return {}


# ───────────────────────────────────────────────
# Sequence diagram SVG parser
# ───────────────────────────────────────────────


def _parse_sequence_diagram_svg(
    tree: ET.ElementTree,
) -> Dict[str, Any]:
    """Parse a sequence diagram SVG into PictoSync annotations.

    Sequence diagram SVGs use classified ``<g>`` groups for participants,
    lifelines, and messages, plus unnamed ``<g>`` elements for activation
    boxes and bare ``<text>``/``<rect>``/``<line>`` elements for phase
    separators and the diagram title.

    Args:
        tree: Parsed ElementTree of the SVG file.

    Returns:
        Dict with PictoSync schema: ``{"version", "image", "annotations"}``.
    """
    root = tree.getroot()
    ns = _SVG_NS

    # Canvas dimensions from viewBox
    viewbox = root.get("viewBox", "").split()
    canvas_w = int(float(viewbox[2])) if len(viewbox) >= 3 else 1200
    canvas_h = int(float(viewbox[3])) if len(viewbox) >= 4 else 800

    empty: Dict[str, Any] = {
        "version": "draft-1",
        "image": {"width": canvas_w, "height": canvas_h},
        "annotations": [],
    }

    root_g = root.find(f"{{{ns}}}g")
    if root_g is None:
        return empty

    # ── Classify children of root <g> in a single pass ────
    title_text_el: Optional[ET.Element] = None
    head_groups: List[ET.Element] = []
    tail_groups: List[ET.Element] = []
    lifeline_groups: List[ET.Element] = []
    activation_groups: List[ET.Element] = []
    message_groups: List[ET.Element] = []
    phase_texts: List[ET.Element] = []
    phase_label_rects: List[ET.Element] = []
    separator_lines: List[ET.Element] = []
    # Note shapes: path pairs (folded corner), bare rects (rnote), polygons (hnote)
    note_path_pairs: List[Tuple[ET.Element, ET.Element]] = []
    note_rects: List[ET.Element] = []        # rnote rectangles
    note_polygons: List[ET.Element] = []     # hnote hexagons
    _prev_note_path: Optional[ET.Element] = None

    seen_activation_keys: set = set()

    for child in root_g:
        tag = child.tag.rsplit("}", 1)[-1]
        cls = child.get("class", "")

        if tag == "text":
            fs = float(child.get("font-size", "0") or "0")
            if fs >= 20:
                title_text_el = child
            elif child.get("font-weight") == "bold":
                phase_texts.append(child)

        elif tag == "rect":
            h = float(child.get("height", 0))
            w = float(child.get("width", 0))
            style = child.get("style", "")
            rfill = child.get("fill", "none").lower()
            # rnote rectangles: note fill color, wider than activation boxes
            if rfill.startswith("#fe") and w > 30:
                note_rects.append(child)
            # Phase label rects: ~19.5px tall, black stroke border
            elif 15 < h < 25 and "stroke:#000000" in style:
                phase_label_rects.append(child)

        elif tag == "polygon":
            # hnote hexagons: polygon with note fill color
            pgfill = child.get("fill", "none").lower()
            if pgfill.startswith("#fe") or pgfill.startswith("#fb"):
                note_polygons.append(child)

        elif tag == "path":
            # Note paths: filled paths with note-like colors.
            # Notes are always pairs (body + folded corner) in sequence.
            # Note fills: #FEFFDD, #FEFFDD, #FBFB77, custom note colors
            # Group/frame fills: #F0F0F0, #E0E0E0 — skip these
            pfill = child.get("fill", "none")
            pfill_lower = pfill.lower()
            is_note_fill = (pfill_lower not in ("none", "")
                            and pfill_lower.startswith("#")
                            and pfill_lower not in ("#f0f0f0", "#e0e0e0",
                                                     "#e2e2f0", "#ffffff"))
            if is_note_fill:
                if _prev_note_path is not None:
                    # Check if same fill = pair (body + corner)
                    prev_fill = _prev_note_path.get("fill", "").lower()
                    if prev_fill == pfill_lower:
                        note_path_pairs.append((_prev_note_path, child))
                        _prev_note_path = None
                    else:
                        # Different fill — previous was orphan, start new
                        _prev_note_path = child
                else:
                    _prev_note_path = child
            # Don't reset on non-note paths — notes may be interleaved with
            # other elements (group frames, etc.)

        elif tag == "line":
            # Bare <line> elements are phase separator rules
            separator_lines.append(child)

        elif tag == "g":
            if "participant-head" in cls:
                head_groups.append(child)
            elif "participant-tail" in cls:
                tail_groups.append(child)
            elif cls == "participant-lifeline":
                lifeline_groups.append(child)
            elif cls == "message":
                message_groups.append(child)
            elif not cls:
                # Unnamed <g> with <title> + <rect> = activation box
                title_child = child.find(f"{{{ns}}}title")
                rect_child = child.find(f"{{{ns}}}rect")
                if title_child is not None and rect_child is not None:
                    w = float(rect_child.get("width", 0))
                    if abs(w - 10) < 2:
                        # Deduplicate (SVG renders each activation twice)
                        key = (rect_child.get("x"), rect_child.get("y"))
                        if key not in seen_activation_keys:
                            seen_activation_keys.add(key)
                            activation_groups.append(child)

    # ── Helpers ───────────────────────────────────────────

    def _extract_stroke(el: ET.Element) -> Tuple[str, int]:
        style = el.get("style", "")
        sm = re.search(r'stroke:\s*(#[0-9A-Fa-f]{3,8})', style)
        wm = re.search(r'stroke-width:\s*(\d+(?:\.\d+)?)', style)
        return (
            sm.group(1).upper() if sm else "#000000",
            int(float(wm.group(1))) if wm else 1,
        )

    def _safe_fill(fill: str) -> str:
        if not fill or fill.lower() == "none" or not fill.startswith("#"):
            return "#00000000"
        return _normalize_color(fill)

    # ── Build annotations ─────────────────────────────────
    annotations: List[Dict[str, Any]] = []
    counter = 1

    # 1. Title
    if title_text_el is not None:
        tx = float(title_text_el.get("x", 0))
        ty = float(title_text_el.get("y", 0))
        fs = float(title_text_el.get("font-size", 22))
        tl = float(title_text_el.get("textLength", 200))
        title_text = title_text_el.text or ""

        ann_id = f"p{counter:06d}"
        counter += 1
        annotations.append({
            "id": ann_id,
            "kind": "text",
            "geom": {
                "x": round(tx, 2), "y": round(ty - fs, 2),
                "w": round(tl, 2), "h": round(fs * 1.5, 2),
            },
            "meta": {
                "label": title_text, "tech": "",
                "note": title_text,
            },
            "style": {
                "pen": {"color": "#555555", "width": 2, "dash": "solid"},
                "fill": {"color": "#00000000"},
                "text": {"color": "#000000", "size_pt": 12.0},
            },
        })

    # 2. Participant heads (rounded rects at top)
    for g in head_groups:
        rect = g.find(f"{{{ns}}}rect")
        if rect is None:
            continue
        texts = [t.text for t in g.findall(f"{{{ns}}}text") if t.text]
        label = "\n".join(texts) if texts else ""

        x = round(float(rect.get("x", 0)), 2)
        y = round(float(rect.get("y", 0)), 2)
        w = round(float(rect.get("width", 0)), 2)
        h = round(float(rect.get("height", 0)), 2)
        fill = _safe_fill(rect.get("fill", ""))
        stroke_color, stroke_width = _extract_stroke(rect)

        ann_id = f"p{counter:06d}"
        counter += 1
        annotations.append({
            "id": ann_id,
            "kind": "roundedrect",
            "geom": {"x": x, "y": y, "w": w, "h": h},
            "meta": {
                "label": label, "tech": "",
                "note": label,
            },
            "style": {
                "pen": {
                    "color": stroke_color, "width": stroke_width, "dash": "solid",
                },
                "fill": {"color": fill},
                "text": {"color": "#000000", "size_pt": 10.0},
            },
        })

    # 3. Participant tails (rounded rects at bottom)
    for g in tail_groups:
        rect = g.find(f"{{{ns}}}rect")
        if rect is None:
            continue
        texts = [t.text for t in g.findall(f"{{{ns}}}text") if t.text]
        label = "\n".join(texts) if texts else ""

        x = round(float(rect.get("x", 0)), 2)
        y = round(float(rect.get("y", 0)), 2)
        w = round(float(rect.get("width", 0)), 2)
        h = round(float(rect.get("height", 0)), 2)
        fill = _safe_fill(rect.get("fill", ""))
        stroke_color, stroke_width = _extract_stroke(rect)

        ann_id = f"p{counter:06d}"
        counter += 1
        annotations.append({
            "id": ann_id,
            "kind": "roundedrect",
            "geom": {"x": x, "y": y, "w": w, "h": h},
            "meta": {
                "label": label, "tech": "",
                "note": label,
            },
            "style": {
                "pen": {
                    "color": stroke_color, "width": stroke_width, "dash": "solid",
                },
                "fill": {"color": fill},
                "text": {"color": "#000000", "size_pt": 10.0},
            },
        })

    # 4. Lifelines (dashed vertical lines)
    for g in lifeline_groups:
        inner_g = g.find(f"{{{ns}}}g")
        if inner_g is None:
            continue
        line = inner_g.find(f"{{{ns}}}line")
        if line is None:
            continue

        x1 = round(float(line.get("x1", 0)), 2)
        y1 = round(float(line.get("y1", 0)), 2)
        x2 = round(float(line.get("x2", 0)), 2)
        y2 = round(float(line.get("y2", 0)), 2)
        stroke_color, stroke_width = _extract_stroke(line)

        ann_id = f"p{counter:06d}"
        counter += 1
        annotations.append({
            "id": ann_id,
            "kind": "line",
            "geom": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
            "meta": {"label": "", "tech": "", "note": ""},
            "style": _make_line_style(
                stroke_color, stroke_width, dashed=True, arrow="none",
            ),
        })

    # 5. Activation boxes (narrow rects on lifelines)
    for g in activation_groups:
        rect = g.find(f"{{{ns}}}rect")
        if rect is None:
            continue

        x = round(float(rect.get("x", 0)), 2)
        y = round(float(rect.get("y", 0)), 2)
        w = round(float(rect.get("width", 0)), 2)
        h = round(float(rect.get("height", 0)), 2)
        fill = _safe_fill(rect.get("fill", ""))
        stroke_color, stroke_width = _extract_stroke(rect)

        ann_id = f"p{counter:06d}"
        counter += 1
        annotations.append({
            "id": ann_id,
            "kind": "rect",
            "geom": {"x": x, "y": y, "w": w, "h": h},
            "meta": {"label": "", "tech": "", "note": ""},
            "style": {
                "pen": {
                    "color": stroke_color, "width": stroke_width, "dash": "solid",
                },
                "fill": {"color": fill},
                "text": {"color": "#000000", "size_pt": 10.0},
            },
        })

    # 6. Messages (normal, return, self-loop)
    #    When an SVG polygon arrowhead is present the message is emitted as
    #    an orthocurve (self-loops: M→H→V→H, normal: M→H) so that the
    #    native arrow rendering places the arrowhead at the correct end.
    for g in message_groups:
        e1 = g.get("data-entity-1", "")
        e2 = g.get("data-entity-2", "")

        lines = g.findall(f"{{{ns}}}line")
        polygon = g.find(f"{{{ns}}}polygon")
        texts = [t.text for t in g.findall(f"{{{ns}}}text") if t.text]
        label = "\n".join(texts) if texts else ""

        is_self = (e1 == e2)

        if is_self:
            # Self-loop: 3 SVG lines form a U-shape → orthocurve
            if len(lines) < 3:
                continue

            # Collect all coordinates from the three line segments
            seg_pts: List[Tuple[float, float]] = []
            for ln in lines:
                seg_pts.append(
                    (float(ln.get("x1", 0)), float(ln.get("y1", 0))),
                )
                seg_pts.append(
                    (float(ln.get("x2", 0)), float(ln.get("y2", 0))),
                )

            stroke_color, stroke_width = _extract_stroke(lines[0])
            style_str = lines[0].get("style", "")
            is_dashed = "stroke-dasharray" in style_str

            # Path corners from the three segments:
            # line[0]: horizontal right  (start → right)
            # line[1]: vertical down     (right → bottom-right)
            # line[2]: horizontal left   (bottom-right → end)
            start_x = float(lines[0].get("x1", 0))
            start_y = float(lines[0].get("y1", 0))
            right_x = max(
                float(lines[0].get("x2", 0)),
                float(lines[1].get("x1", 0)),
            )
            bottom_y = float(lines[1].get("y2", 0))

            # Arrow endpoint: use polygon tip if available
            has_arrow = polygon is not None
            if has_arrow:
                pts_str = polygon.get("points", "")
                pts = re.findall(
                    r'([-+]?\d*\.?\d+),([-+]?\d*\.?\d+)', pts_str,
                )
                if pts:
                    poly_pts = [
                        (float(p[0]), float(p[1])) for p in pts
                    ]
                    # Tip = leftmost point (arrow points back to lifeline)
                    tip = min(poly_pts, key=lambda p: p[0])
                    end_x, end_y = tip
                else:
                    end_x = float(lines[2].get("x1", 0))
                    end_y = bottom_y
            else:
                end_x = float(lines[2].get("x1", 0))
                end_y = bottom_y

            # Bounding box enclosing all path points
            all_xs = [start_x, right_x, end_x]
            all_ys = [start_y, bottom_y, end_y]
            bx = min(all_xs)
            by = min(all_ys)
            bw = max(all_xs) - bx
            bh = max(all_ys) - by
            if bw < 1 or bh < 1:
                continue

            # Normalised orthocurve nodes: M → H → V → H
            nodes: List[Dict[str, Any]] = [
                {
                    "cmd": "M",
                    "x": round((start_x - bx) / bw, 4),
                    "y": round((start_y - by) / bh, 4),
                },
                {"cmd": "H", "x": round((right_x - bx) / bw, 4)},
                {"cmd": "V", "y": round((bottom_y - by) / bh, 4)},
                {"cmd": "H", "x": round((end_x - bx) / bw, 4)},
            ]

            ann_id = f"p{counter:06d}"
            counter += 1
            annotations.append({
                "id": ann_id,
                "kind": "orthocurve",
                "geom": {
                    "x": round(bx, 2), "y": round(by, 2),
                    "w": round(bw, 2), "h": round(bh, 2),
                    "nodes": nodes,
                    "adjust1": 0,
                },
                "meta": {
                    "label": label, "tech": "",
                    "note": label,
                },
                "style": _make_line_style(
                    stroke_color, stroke_width, dashed=is_dashed,
                    arrow="end" if has_arrow else "none",
                ),
            })

        elif polygon is not None:
            # Normal / return message with arrowhead → orthocurve (M→H)
            if not lines:
                continue
            line = lines[0]

            lx1 = float(line.get("x1", 0))
            ly1 = float(line.get("y1", 0))
            lx2 = float(line.get("x2", 0))
            ly2 = float(line.get("y2", 0))

            stroke_color, stroke_width = _extract_stroke(line)
            style_str = line.get("style", "")
            is_dashed = "stroke-dasharray" in style_str

            # Determine arrow direction and polygon tip
            pts_str = polygon.get("points", "")
            pts = re.findall(
                r'([-+]?\d*\.?\d+),([-+]?\d*\.?\d+)', pts_str,
            )
            if pts:
                poly_pts = [
                    (float(p[0]), float(p[1])) for p in pts
                ]
                poly_cx = sum(p[0] for p in poly_pts) / len(poly_pts)

                if abs(poly_cx - lx1) < abs(poly_cx - lx2):
                    # Arrow toward x1 → tip is leftmost polygon point
                    tip = min(poly_pts, key=lambda p: p[0])
                    start_x, start_y = lx2, ly2
                else:
                    # Arrow toward x2 → tip is rightmost polygon point
                    tip = max(poly_pts, key=lambda p: p[0])
                    start_x, start_y = lx1, ly1
                end_x, end_y = tip
            else:
                start_x, start_y = lx1, ly1
                end_x, end_y = lx2, ly2

            # Bounding box (ensure non-zero height for horizontal lines)
            min_h = 8.0
            bx = min(start_x, end_x)
            bw = abs(end_x - start_x)
            dy = abs(end_y - start_y)
            if dy < min_h:
                by = min(start_y, end_y) - (min_h - dy) / 2
                bh = min_h
            else:
                by = min(start_y, end_y)
                bh = dy
            if bw < 1:
                continue

            nodes = [
                {
                    "cmd": "M",
                    "x": round((start_x - bx) / bw, 4),
                    "y": round((start_y - by) / bh, 4),
                },
                {"cmd": "H", "x": round((end_x - bx) / bw, 4)},
            ]

            ann_id = f"p{counter:06d}"
            counter += 1
            annotations.append({
                "id": ann_id,
                "kind": "orthocurve",
                "geom": {
                    "x": round(bx, 2), "y": round(by, 2),
                    "w": round(bw, 2), "h": round(bh, 2),
                    "nodes": nodes,
                    "adjust1": 0,
                },
                "meta": {
                    "label": label, "tech": "",
                    "note": label,
                },
                "style": _make_line_style(
                    stroke_color, stroke_width, dashed=is_dashed,
                ),
            })

        else:
            # Message without polygon (no arrowhead) → plain line
            if not lines:
                continue
            line = lines[0]

            lx1 = float(line.get("x1", 0))
            ly1 = float(line.get("y1", 0))
            lx2 = float(line.get("x2", 0))
            ly2 = float(line.get("y2", 0))

            stroke_color, stroke_width = _extract_stroke(line)
            style_str = line.get("style", "")
            is_dashed = "stroke-dasharray" in style_str

            ann_id = f"p{counter:06d}"
            counter += 1
            annotations.append({
                "id": ann_id,
                "kind": "line",
                "geom": {
                    "x1": round(lx1, 2), "y1": round(ly1, 2),
                    "x2": round(lx2, 2), "y2": round(ly2, 2),
                },
                "meta": {
                    "label": label, "tech": "",
                    "note": label,
                },
                "style": _make_line_style(
                    stroke_color, stroke_width,
                    dashed=is_dashed, arrow="none",
                ),
            })

    # 7. Phase separators (bold text labels with bordered rects)
    for text_el in phase_texts:
        ty = float(text_el.get("y", 0))
        fs = float(text_el.get("font-size", 10))
        tl = float(text_el.get("textLength", 100))
        tx = float(text_el.get("x", 0))
        phase_label = text_el.text or ""

        # Find closest label rect by Y proximity
        best_rect: Optional[ET.Element] = None
        best_dist = float("inf")
        for rect in phase_label_rects:
            ry = float(rect.get("y", 0))
            rh = float(rect.get("height", 0))
            rect_cy = ry + rh / 2
            dist = abs(rect_cy - ty)
            if dist < best_dist:
                best_dist = dist
                best_rect = rect

        # Use label rect geometry if close, else fall back to text
        if best_rect is not None and best_dist < 20:
            geom: Dict[str, Any] = {
                "x": round(float(best_rect.get("x", 0)), 2),
                "y": round(float(best_rect.get("y", 0)), 2),
                "w": round(float(best_rect.get("width", 0)), 2),
                "h": round(float(best_rect.get("height", 0)), 2),
            }
        else:
            geom = {
                "x": round(tx, 2), "y": round(ty - fs, 2),
                "w": round(tl, 2), "h": round(fs * 1.5, 2),
            }

        ann_id = f"p{counter:06d}"
        counter += 1
        annotations.append({
            "id": ann_id,
            "kind": "text",
            "geom": geom,
            "meta": {
                "label": phase_label, "tech": "",
                "note": phase_label,
            },
            "style": {
                "pen": {"color": "#000000", "width": 1, "dash": "solid"},
                "fill": {"color": "#FFFFFF"},
                "text": {"color": "#000000", "size_pt": 10.0},
            },
        })

    # 8. Phase separator lines (horizontal rules spanning diagram width)
    # Lines come in pairs ~3px apart; emit one line annotation per pair
    # at the midpoint Y.
    sep_ys: List[Tuple[float, ET.Element]] = []
    for ln in separator_lines:
        ly = float(ln.get("y1", 0))
        sep_ys.append((ly, ln))
    sep_ys.sort(key=lambda t: t[0])

    used: set = set()
    for i, (y_i, ln_i) in enumerate(sep_ys):
        if i in used:
            continue
        # Find the partner line within 5px
        partner_idx: Optional[int] = None
        for j in range(i + 1, len(sep_ys)):
            if j in used:
                continue
            if abs(sep_ys[j][0] - y_i) <= 5:
                partner_idx = j
                break
        if partner_idx is not None:
            used.add(i)
            used.add(partner_idx)
            ln_j = sep_ys[partner_idx][1]
            mid_y = round((y_i + sep_ys[partner_idx][0]) / 2, 2)
        else:
            used.add(i)
            mid_y = round(y_i, 2)

        lx1 = round(float(ln_i.get("x1", 0)), 2)
        lx2 = round(float(ln_i.get("x2", 0)), 2)
        stroke_color, stroke_width = _extract_stroke(ln_i)

        ann_id = f"p{counter:06d}"
        counter += 1
        annotations.append({
            "id": ann_id,
            "kind": "line",
            "geom": {"x1": lx1, "y1": mid_y, "x2": lx2, "y2": mid_y},
            "meta": {"label": "", "tech": "", "note": ""},
            "style": _make_line_style(
                stroke_color, stroke_width, arrow="none",
            ),
        })

    # ── Notes (path pairs with note fill + nearby text) ─────
    # Collect all bare <text> elements for note text matching
    all_bare_texts = [
        c for c in root_g
        if c.tag.rsplit("}", 1)[-1] == "text"
    ]
    for body_path, corner_path in note_path_pairs:
        d = body_path.get("d", "")
        bx, by, bw, bh = _path_bbox(d)
        if bw < 1 or bh < 1:
            continue
        fill = body_path.get("fill", "#FEFFDD")
        stroke_color, stroke_width = _extract_stroke(body_path)

        # Find text elements inside the note bbox
        note_texts: List[str] = []
        for t in all_bare_texts:
            tx = float(t.get("x", 0))
            ty = float(t.get("y", 0))
            if bx <= tx <= bx + bw and by <= ty <= by + bh:
                txt = (t.text or "").strip()
                if txt:
                    note_texts.append(txt)

        if not note_texts:
            continue

        label = note_texts[0]
        note_body = "\n".join(note_texts)
        label, _tech, note_body = _dedup_label_tech_note(label, "", note_body)
        text_fmt = _extract_text_format(
            [t for t in all_bare_texts
             if bx <= float(t.get("x", 0)) <= bx + bw
             and by <= float(t.get("y", 0)) <= by + bh])

        ann_id = f"p{counter:06d}"
        counter += 1
        # TODO: Replace "rect" with a dedicated "note" item type
        note_meta: Dict[str, Any] = {
            "label": label,
            "tech": "",
            "note": note_body,
        }
        note_meta.update(text_fmt)
        annotations.append({
            "id": ann_id,
            "kind": "rect",
            "geom": {
                "x": round(bx, 2), "y": round(by, 2),
                "w": round(bw, 2), "h": round(bh, 2),
            },
            "meta": note_meta,
            "style": {
                "pen": {
                    "color": stroke_color,
                    "width": stroke_width,
                    "dash": "solid",
                },
                "fill": {"color": _safe_fill(fill)},
            },
        })

    # ── rnotes (bare <rect> with note fill) ─────────────────
    for nr in note_rects:
        rx = float(nr.get("x", 0))
        ry = float(nr.get("y", 0))
        rw = float(nr.get("width", 0))
        rh = float(nr.get("height", 0))
        if rw < 1 or rh < 1:
            continue
        fill = nr.get("fill", "#FEFFDD")
        stroke_color, stroke_width = _extract_stroke(nr)
        note_texts = []
        for t in all_bare_texts:
            tx = float(t.get("x", 0))
            ty = float(t.get("y", 0))
            if rx <= tx <= rx + rw and ry <= ty <= ry + rh:
                txt = (t.text or "").strip()
                if txt:
                    note_texts.append(txt)
        if not note_texts:
            continue
        label = note_texts[0]
        note_body = "\n".join(note_texts)
        label, _tech, note_body = _dedup_label_tech_note(label, "", note_body)
        text_fmt = _extract_text_format(
            [t for t in all_bare_texts
             if rx <= float(t.get("x", 0)) <= rx + rw
             and ry <= float(t.get("y", 0)) <= ry + rh])
        ann_id = f"p{counter:06d}"
        counter += 1
        note_meta = {"label": label, "tech": "rnote", "note": note_body}
        note_meta.update(text_fmt)
        annotations.append({
            "id": ann_id,
            "kind": "rect",
            "geom": {"x": round(rx, 2), "y": round(ry, 2),
                     "w": round(rw, 2), "h": round(rh, 2)},
            "meta": note_meta,
            "style": {"pen": {"color": stroke_color, "width": stroke_width,
                              "dash": "solid"},
                      "fill": {"color": _safe_fill(fill)}},
        })

    # ── hnotes (bare <polygon> with note fill) ────────────
    for np in note_polygons:
        pts_str = np.get("points", "")
        pts = re.findall(r'([-+]?\d*\.?\d+),([-+]?\d*\.?\d+)', pts_str)
        if len(pts) < 4:
            continue
        xs = [float(p[0]) for p in pts]
        ys = [float(p[1]) for p in pts]
        px, py = min(xs), min(ys)
        pw, ph = max(xs) - px, max(ys) - py
        if pw < 1 or ph < 1:
            continue
        fill = np.get("fill", "#FEFFDD")
        stroke_color, stroke_width = _extract_stroke(np)
        note_texts = []
        for t in all_bare_texts:
            tx = float(t.get("x", 0))
            ty = float(t.get("y", 0))
            if px <= tx <= px + pw and py <= ty <= py + ph:
                txt = (t.text or "").strip()
                if txt:
                    note_texts.append(txt)
        if not note_texts:
            continue
        label = note_texts[0]
        note_body = "\n".join(note_texts)
        label, _tech, note_body = _dedup_label_tech_note(label, "", note_body)
        text_fmt = _extract_text_format(
            [t for t in all_bare_texts
             if px <= float(t.get("x", 0)) <= px + pw
             and py <= float(t.get("y", 0)) <= py + ph])
        ann_id = f"p{counter:06d}"
        counter += 1
        note_meta = {"label": label, "tech": "hnote", "note": note_body}
        note_meta.update(text_fmt)
        annotations.append({
            "id": ann_id,
            "kind": "polygon",
            "geom": {"x": round(px, 2), "y": round(py, 2),
                     "w": round(pw, 2), "h": round(ph, 2),
                     "points": [[round((float(p[0]) - px) / pw, 4),
                                  round((float(p[1]) - py) / ph, 4)]
                                 for p in pts]},
            "meta": note_meta,
            "style": {"pen": {"color": stroke_color, "width": stroke_width,
                              "dash": "solid"},
                      "fill": {"color": _safe_fill(fill)}},
        })

    _normalize_annotations(annotations)
    return {
        "version": "draft-1",
        "image": {"width": canvas_w, "height": canvas_h},
        "annotations": annotations,
    }


# ───────────────────────────────────────────────
# Description diagram SVG parser
# ───────────────────────────────────────────────


def _is_node_box_polygon(pts: list) -> bool:
    """Detect PlantUML "node" 3D-box polygon shape.

    PlantUML renders ``node`` elements as a 7-point polygon with a diagonal
    tab in the top-left corner (the 3D extrusion effect).  The pattern is:

    ::

        p0=(x, y+tab)  p1=(x+tab, y)  p2=(x+w, y)
        p6=(x, y+h)                    p3=(x+w, y+h-tab)
                                       p4=(x+w-tab, y+h)

    Returns True when the polygon matches this 7-point rectangular-tab
    pattern within a small tolerance.
    """
    if len(pts) not in (7, 8):  # 7 unique + optional close-repeat
        return False
    xs = [p[0] for p in pts[:7]]
    ys = [p[1] for p in pts[:7]]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    w = x_max - x_min
    h = y_max - y_min
    if w < 5 or h < 5:
        return False
    # Check that the bounding box is roughly rectangular and the tab
    # size is a small fraction (5-25%) of the total dimensions.
    tab_sizes = set()
    for p in pts[:7]:
        dx = abs(p[0] - x_min) + abs(p[0] - x_max)
        dy = abs(p[1] - y_min) + abs(p[1] - y_max)
        # Points not on the bounding box edge indicate the tab
        if dx > w + 2 and dy > h + 2:
            return False  # point too far from edges
    # Count points near each edge to validate the rectangular shape
    tol = max(w, h) * 0.02 + 1
    on_left = sum(1 for p in pts[:7] if abs(p[0] - x_min) < tol)
    on_right = sum(1 for p in pts[:7] if abs(p[0] - x_max) < tol)
    on_top = sum(1 for p in pts[:7] if abs(p[1] - y_min) < tol)
    on_bottom = sum(1 for p in pts[:7] if abs(p[1] - y_max) < tol)
    # A node box: left side has 2 pts, right side has 2 pts,
    # top has 2 pts, bottom has 2 pts, with 1 diagonal tab point
    return (on_left >= 2 and on_right >= 2 and
            on_top >= 1 and on_bottom >= 1)


# ───────────────────────────────────────────────
# ANTLR4-based PlantUML deployment source parser
# ───────────────────────────────────────────────

def _parse_deployment_source(puml_text: str) -> Dict[str, Dict[str, Any]]:
    """Parse PlantUML deployment source with the ANTLR4 grammar.

    Returns a dict keyed by element name (lowercase) with values::

        {
            "keyword": "node",          # PlantUML element keyword
            "name": "WebServer",        # original name
            "alias": "ws",              # declared alias or ""
            "stereotype": "<<Docker>>", # stereotype text or ""
            "children": [...],          # child element names
        }

    Returns an empty dict if the grammar is unavailable or parsing fails.
    """
    try:
        from antlr4 import CommonTokenStream, InputStream
        from plantuml.grammar.generated.PlantUMLDeploymentLexer import PlantUMLDeploymentLexer
        from plantuml.grammar.generated.PlantUMLDeploymentParser import PlantUMLDeploymentParser
        from plantuml.grammar.generated.PlantUMLDeploymentVisitor import PlantUMLDeploymentVisitor
    except ImportError:
        return {}

    class _Visitor(PlantUMLDeploymentVisitor):
        def __init__(self):
            self.elements: Dict[str, Dict[str, Any]] = {}

        def _extract_name(self, ctx) -> str:
            if ctx.elementName():
                return ctx.elementName().getText()
            if ctx.BRACKET_COMP():
                raw = ctx.BRACKET_COMP().getText()
                return raw.strip("[]")
            if ctx.ACTOR_COLON():
                raw = ctx.ACTOR_COLON().getText()
                return raw.strip(":")
            if hasattr(ctx, "USECASE_PAREN") and ctx.USECASE_PAREN():
                raw = ctx.USECASE_PAREN().getText()
                return raw.strip("()")
            if hasattr(ctx, "CIRCLE_IFACE") and ctx.CIRCLE_IFACE():
                raw = ctx.CIRCLE_IFACE().getText()
                return raw.strip('() "')
            return ""

        def _extract_stereotype(self, ctx) -> str:
            mods = ctx.elementModifier() if hasattr(ctx, "elementModifier") else []
            for mod in mods:
                sc = mod.stereotypeClause() if hasattr(mod, "stereotypeClause") else None
                if sc:
                    return sc.getText()
            return ""

        def _store(self, name: str, keyword: str, alias: str, stereotype: str):
            if not name:
                return
            # Strip quotes from names
            clean_name = name.strip('"')
            clean_alias = alias.strip('"')
            key = (clean_alias or clean_name).lower()
            self.elements[key] = {
                "keyword": keyword,
                "name": clean_name,
                "alias": clean_alias,
                "stereotype": stereotype,
            }

        def visitElementDecl(self, ctx):
            name = self._extract_name(ctx)
            keyword = ctx.elementKeyword().getText() if ctx.elementKeyword() else ""
            alias = ""
            if ctx.aliasClause():
                alias = ctx.aliasClause().elementName().getText()
            stereotype = self._extract_stereotype(ctx)
            self._store(name, keyword, alias, stereotype)
            return self.visitChildren(ctx)

        def visitElementBlock(self, ctx):
            keyword = ctx.elementKeyword().getText() if ctx.elementKeyword() else ""
            name = ctx.elementName().getText() if ctx.elementName() else ""
            alias = ""
            if ctx.aliasClause():
                alias = ctx.aliasClause().elementName().getText()
            stereotype = self._extract_stereotype(ctx)
            self._store(name, keyword, alias, stereotype)
            return self.visitChildren(ctx)

    try:
        input_stream = InputStream(puml_text)
        lexer = PlantUMLDeploymentLexer(input_stream)
        lexer.removeErrorListeners()
        token_stream = CommonTokenStream(lexer)
        parser = PlantUMLDeploymentParser(token_stream)
        parser.removeErrorListeners()
        tree = parser.diagram()
        if parser.getNumberOfSyntaxErrors() > 0:
            return {}
        visitor = _Visitor()
        visitor.visit(tree)
        return visitor.elements
    except Exception:
        return {}


# ───────────────────────────────────────────────
# ANTLR4-based PlantUML component source parser
# ───────────────────────────────────────────────

def _parse_component_source(puml_text: str) -> Dict[str, Any]:
    """Parse PlantUML component diagram source with the ANTLR4 grammar.

    Returns a dict with semantic elements extracted from the source::

        {
            "title": str,
            "components": [{"name", "keyword", "alias", "stereotype", "color"}],
            "interfaces": [{"name", "alias"}],
            "groups": [{"keyword", "name", "color"}],
            "relations": [{"source", "target", "label"}],
            "notes": [{"text"}],
            "sprites": [str],
        }

    Returns an empty dict if the grammar is unavailable or parsing fails.
    """
    try:
        from antlr4 import CommonTokenStream, InputStream
        from plantuml.grammar.generated.PlantUMLComponentLexer import PlantUMLComponentLexer
        from plantuml.grammar.generated.PlantUMLComponentParser import PlantUMLComponentParser
        from plantuml.grammar.generated.PlantUMLComponentVisitor import PlantUMLComponentVisitor
    except ImportError:
        return {}

    def _strip_quotes(s: str) -> str:
        if s and len(s) >= 2 and s[0] == '"' and s[-1] == '"':
            return s[1:-1]
        return s

    def _ctx_original_text(ctx) -> str:
        """Recover original source text (with whitespace) from a parse-tree node."""
        if ctx is None:
            return ""
        start = ctx.start
        stop = ctx.stop
        if start is None or stop is None:
            return ctx.getText()
        stream = start.source[1]  # the InputStream
        return stream.getText(start.start, stop.stop)

    class _Visitor(PlantUMLComponentVisitor):
        def __init__(self):
            self.title: str = ""
            self.components: List[Dict[str, str]] = []
            self.interfaces: List[Dict[str, str]] = []
            self.groups: List[Dict[str, str]] = []
            self.relations: List[Dict[str, str]] = []
            self.notes: List[Dict[str, str]] = []
            self.sprites: List[str] = []

        # ── helpers ──────────────────────────────────

        def _get_alias(self, ctx) -> str:
            ac = ctx.aliasClause() if hasattr(ctx, "aliasClause") else None
            if ac and ac.elementName():
                return _strip_quotes(ac.elementName().getText())
            return ""

        def _get_stereotype(self, ctx) -> str:
            mods = ctx.componentModifier() if hasattr(ctx, "componentModifier") else []
            for mod in mods:
                sc = mod.stereotypeClause()
                if sc:
                    return sc.getText()  # e.g. <<Docker>>
            return ""

        def _get_color(self, ctx) -> str:
            mods = ctx.componentModifier() if hasattr(ctx, "componentModifier") else []
            for mod in mods:
                c = mod.COLOR()
                if c:
                    return c.getText()
            return ""

        def _relation_ref_name(self, ref_ctx) -> str:
            """Extract the name string from a relationRef context."""
            if ref_ctx.BRACKET_COMP():
                return ref_ctx.BRACKET_COMP().getText().strip("[]").strip()
            if ref_ctx.QUOTED_STRING():
                return _strip_quotes(ref_ctx.QUOTED_STRING().getText())
            if ref_ctx.CIRCLE_IFACE() and ref_ctx.elementName():
                return _strip_quotes(ref_ctx.elementName().getText())
            if ref_ctx.ID():
                return ref_ctx.ID().getText()
            # Fallback for keyword tokens used as identifiers
            txt = ref_ctx.getText()
            return _strip_quotes(txt) if txt else ""

        # ── visitor methods ──────────────────────────

        def visitComponentFullDecl(self, ctx):
            name = ""
            keyword = "component"
            if ctx.BRACKET_COMP():
                raw = ctx.BRACKET_COMP().getText()
                name = raw.strip("[]").strip()
            elif ctx.elementName():
                name = _strip_quotes(ctx.elementName().getText())
            alias = self._get_alias(ctx)
            stereotype = self._get_stereotype(ctx)
            color = self._get_color(ctx)
            if name:
                self.components.append({
                    "name": name,
                    "keyword": keyword,
                    "alias": alias,
                    "stereotype": stereotype,
                    "color": color,
                })
            return self.visitChildren(ctx)

        def visitInterfaceDecl(self, ctx):
            name = ""
            if ctx.elementName():
                name = _strip_quotes(ctx.elementName().getText())
            alias = self._get_alias(ctx)
            if name:
                self.interfaces.append({
                    "name": name,
                    "alias": alias,
                })
            return self.visitChildren(ctx)

        def visitPortDecl(self, ctx):
            # Ports are treated like components with a port keyword
            name = ""
            keyword = "port"
            if ctx.KW_PORTIN():
                keyword = "portin"
            elif ctx.KW_PORTOUT():
                keyword = "portout"
            if ctx.elementName():
                name = _strip_quotes(ctx.elementName().getText())
            alias = self._get_alias(ctx)
            if name:
                self.components.append({
                    "name": name,
                    "keyword": keyword,
                    "alias": alias,
                    "stereotype": "",
                    "color": "",
                })
            return self.visitChildren(ctx)

        def visitGroupBlock(self, ctx):
            keyword = ctx.groupKeyword().getText() if ctx.groupKeyword() else ""
            name = ""
            if ctx.elementName():
                name = _strip_quotes(ctx.elementName().getText())
            color = self._get_color(ctx)
            if name or keyword:
                self.groups.append({
                    "keyword": keyword,
                    "name": name,
                    "color": color,
                })
            return self.visitChildren(ctx)

        def visitRelationStmt(self, ctx):
            refs = ctx.relationRef()
            if len(refs) >= 2:
                source = self._relation_ref_name(refs[0])
                target = self._relation_ref_name(refs[1])
                label = ""
                if ctx.restOfLine():
                    label = _ctx_original_text(ctx.restOfLine()).strip()
                self.relations.append({
                    "source": source,
                    "target": target,
                    "label": label,
                })
            return self.visitChildren(ctx)

        def visitNoteStmt(self, ctx):
            text = ""
            if ctx.restOfLine():
                text = _ctx_original_text(ctx.restOfLine()).strip()
            if text:
                self.notes.append({"text": text})
            return self.visitChildren(ctx)

        def visitNoteBlock(self, ctx):
            lines = []
            for body_line in ctx.noteBodyLine():
                raw = _ctx_original_text(body_line).strip()
                if raw:
                    lines.append(raw)
            text = "\n".join(lines)
            if text:
                self.notes.append({"text": text})
            return self.visitChildren(ctx)

        def visitTitleStmt(self, ctx):
            if ctx.restOfLine():
                self.title = _ctx_original_text(ctx.restOfLine()).strip()
            return self.visitChildren(ctx)

        def visitSpriteDecl(self, ctx):
            tag = ctx.TAG()
            if tag:
                # TAG is $name — strip the leading $
                self.sprites.append(tag.getText().lstrip("$"))
            return self.visitChildren(ctx)

    try:
        input_stream = InputStream(puml_text)
        lexer = PlantUMLComponentLexer(input_stream)
        lexer.removeErrorListeners()
        token_stream = CommonTokenStream(lexer)
        parser = PlantUMLComponentParser(token_stream)
        parser.removeErrorListeners()
        tree = parser.diagram()
        if parser.getNumberOfSyntaxErrors() > 0:
            return {}
        visitor = _Visitor()
        visitor.visit(tree)
        return {
            "title": visitor.title,
            "components": visitor.components,
            "interfaces": visitor.interfaces,
            "groups": visitor.groups,
            "relations": visitor.relations,
            "notes": visitor.notes,
            "sprites": visitor.sprites,
        }
    except Exception:
        return {}


def _parse_description_diagram_svg(
    tree: ET.ElementTree,
    puml_text: str = "",
) -> Dict[str, Any]:
    """Parse a DESCRIPTION diagram SVG into PictoSync annotations.

    DESCRIPTION diagrams include component, deployment, use-case, and
    architecture diagrams.  They use classified ``<g>`` groups (entity,
    cluster, link) much like the default path, but this parser extracts
    everything directly from the SVG—bypassing text-regex—so that
    bracket-notation components (``[Name] as alias``) and other elements
    missed by ``_extract_elements()`` are captured reliably.

    Args:
        tree: Parsed ElementTree of the SVG file.

    Returns:
        Dict with PictoSync schema: ``{"version", "image", "annotations"}``.
    """
    root = tree.getroot()
    ns = _SVG_NS

    # ── Canvas dimensions ────────────────────────────
    viewbox = root.get("viewBox", "").split()
    canvas_w = int(float(viewbox[2])) if len(viewbox) >= 3 else 1200
    canvas_h = int(float(viewbox[3])) if len(viewbox) >= 4 else 800

    empty: Dict[str, Any] = {
        "version": "draft-1",
        "image": {"width": canvas_w, "height": canvas_h},
        "annotations": [],
    }

    # ── Helpers ──────────────────────────────────────

    def _safe_fill(fill: str) -> str:
        if not fill or fill.lower() == "none" or not fill.startswith("#"):
            return "#00000000"
        return _normalize_color(fill)

    def _extract_stroke(el: ET.Element) -> Tuple[str, int]:
        style = el.get("style", "")
        sm = re.search(r'stroke:\s*(#[0-9A-Fa-f]{3,8})', style)
        wm = re.search(r'stroke-width:\s*(\d+(?:\.\d+)?)', style)
        return (
            sm.group(1).upper() if sm else "#000000",
            int(float(wm.group(1))) if wm else 1,
        )

    def _child_y(ann: Dict[str, Any]) -> float:
        if "geom" in ann:
            g = ann["geom"]
            return g.get("y", g.get("y1", 0))
        if ann.get("children"):
            return _child_y(ann["children"][0])
        return 0.0

    # ── Pass 1: collect data from <g> elements ───────
    title_info: Optional[Dict[str, Any]] = None
    # Keyed by SVG id (ent0002, ent0003, etc.)
    cluster_info: Dict[str, Dict[str, Any]] = {}
    entity_info: Dict[str, Dict[str, Any]] = {}
    all_geom: Dict[str, Dict[str, Any]] = {}
    id_to_qname: Dict[str, str] = {}
    qname_to_id: Dict[str, str] = {}  # clusters only

    link_list: List[Dict[str, Any]] = []

    for g in root.iter(f"{{{ns}}}g"):
        cls = g.get("class", "")

        if cls == "title":
            text_el = g.find(f"{{{ns}}}text")
            if text_el is not None:
                tx = float(text_el.get("x", 0))
                ty = float(text_el.get("y", 0))
                fs = float(text_el.get("font-size", 14))
                tl = float(text_el.get("textLength", 200))
                title_info = {
                    "text": text_el.text or "",
                    "geom": {
                        "x": round(tx, 2),
                        "y": round(ty - fs, 2),
                        "w": round(tl, 2),
                        "h": round(fs * 1.5, 2),
                    },
                }

        elif cls == "cluster":
            qname = g.get("data-qualified-name", "")
            ent_id = g.get("id", "")
            if not ent_id:
                continue
            id_to_qname[ent_id] = qname
            qname_to_id[qname] = ent_id

            # Determine shape and geometry
            polygon_el = g.find(f"{{{ns}}}polygon")
            path_el = g.find(f"{{{ns}}}path")
            rect_el = g.find(f"{{{ns}}}rect")

            # When both rect and path exist and the path is stroke-only
            # (fill="none"), the rect is the main body and the path is a
            # decorative tab (folder/frame).  Prefer the rect.
            if (
                path_el is not None
                and rect_el is not None
                and (path_el.get("fill", "").lower() in ("none", ""))
            ):
                path_el = None  # ignore decorative tab path

            kind = "rect"
            geom: Dict[str, Any] = {"x": 0, "y": 0, "w": 0, "h": 0}
            fill = "#FFFFFF"
            stroke_color = "#000000"
            stroke_width = 1

            if polygon_el is not None:
                pts_str = polygon_el.get("points", "")
                pts = re.findall(
                    r'([-+]?\d*\.?\d+),([-+]?\d*\.?\d+)', pts_str,
                )
                if pts:
                    xs = [float(p[0]) for p in pts]
                    ys = [float(p[1]) for p in pts]
                    x, y = min(xs), min(ys)
                    w, h = max(xs) - x, max(ys) - y
                    geom = {
                        "x": round(x, 2), "y": round(y, 2),
                        "w": round(w, 2), "h": round(h, 2),
                    }
                    if w > 0 and h > 0:
                        geom["points"] = [
                            [round((float(px) - x) / w, 4),
                             round((float(py) - y) / h, 4)]
                            for px, py in pts
                        ]
                    # Detect PlantUML "node" 3D-box shape → isocube
                    abs_pts = [(float(p[0]), float(p[1])) for p in pts]
                    if _is_node_box_polygon(abs_pts):
                        kind = "isocube"
                        # Compute tab size (extrusion depth) from the
                        # diagonal offset between p0 and p1
                        tab_x = abs(abs_pts[1][0] - abs_pts[0][0])
                        tab_y = abs(abs_pts[1][1] - abs_pts[0][1])
                        tab = max(tab_x, tab_y)
                        geom["adjust1"] = 14
                        geom["adjust2"] = 220
                        # Remove points — isocube uses adjust params
                        geom.pop("points", None)
                    else:
                        kind = "polygon"
                fill = polygon_el.get("fill", "#FFFFFF")
                stroke_color, stroke_width = _extract_stroke(polygon_el)

            elif path_el is not None:
                d = path_el.get("d", "")
                has_curves = bool(re.search(r'[CcSsQqTt]', d))
                bx, by, bw, bh = _path_bbox(d)
                geom = {"x": bx, "y": by, "w": bw, "h": bh}
                kind = "polygon"
                if has_curves:
                    # Cloud shape — extract cubic bezier curve vertices
                    # as polygon points with "C" curve type annotations.
                    rel_pts = _path_to_curve_polygon(d, bx, by, bw, bh)
                    if rel_pts:
                        geom["points"] = rel_pts
                else:
                    # Package / frame tab — polygon with straight points
                    rel_pts = _path_points(d)
                    if rel_pts:
                        geom["points"] = rel_pts
                fill = path_el.get("fill", "#FFFFFF")
                stroke_color, stroke_width = _extract_stroke(path_el)

            elif rect_el is not None:
                geom = {
                    "x": round(float(rect_el.get("x", 0)), 2),
                    "y": round(float(rect_el.get("y", 0)), 2),
                    "w": round(float(rect_el.get("width", 0)), 2),
                    "h": round(float(rect_el.get("height", 0)), 2),
                }
                fill = rect_el.get("fill", "#FFFFFF")
                stroke_color, stroke_width = _extract_stroke(rect_el)

            # Text labels (dedup across label/tech/note)
            texts = [t.text for t in g.findall(f"{{{ns}}}text") if t.text]
            label = texts[0] if texts else (
                qname.rsplit(".", 1)[-1] if qname else ""
            )
            tech = texts[1] if len(texts) > 1 else ""
            note = " ".join(texts[2:]) if len(texts) > 2 else ""
            label, tech, note = _dedup_label_tech_note(label, tech, note)

            cluster_info[ent_id] = {
                "kind": kind,
                "geom": geom,
                "fill": fill,
                "label": label,
                "tech": tech,
                "note": note,
                "stroke_color": stroke_color,
                "stroke_width": stroke_width,
            }
            all_geom[ent_id] = {
                "x": geom["x"], "y": geom["y"],
                "w": geom["w"], "h": geom["h"],
            }

        elif cls == "entity":
            qname = g.get("data-qualified-name", "")
            ent_id = g.get("id", "")
            if not ent_id:
                continue
            id_to_qname[ent_id] = qname

            # Determine shape type
            ellipse_el = g.find(f"{{{ns}}}ellipse")
            rects = g.findall(f"{{{ns}}}rect")
            path_el = g.find(f"{{{ns}}}path")

            kind = "rect"
            geom = {"x": 0, "y": 0, "w": 0, "h": 0}
            fill = "#FFFFFF"
            stroke_color = "#000000"
            stroke_width = 1

            if ellipse_el is not None:
                cx = float(ellipse_el.get("cx", 0))
                cy = float(ellipse_el.get("cy", 0))
                rx = float(ellipse_el.get("rx", 8))
                ry = float(ellipse_el.get("ry", 8))

                if rects:
                    # Interface entity: ellipse (circle icon) + rect (name box)
                    # TODO: Replace "rect" with a dedicated "interface" item type
                    main_rect = max(
                        rects,
                        key=lambda r: (
                            float(r.get("width", 0)) * float(r.get("height", 0))
                        ),
                    )
                    r_x = float(main_rect.get("x", 0))
                    r_y = float(main_rect.get("y", 0))
                    r_w = float(main_rect.get("width", 0))
                    r_h = float(main_rect.get("height", 0))
                    # Include ellipse in bounding box
                    x = min(r_x, cx - rx)
                    y = min(r_y, cy - ry)
                    w = max(r_x + r_w, cx + rx) - x
                    h = max(r_y + r_h, cy + ry) - y
                    geom = {
                        "x": round(x, 2), "y": round(y, 2),
                        "w": round(w, 2), "h": round(h, 2),
                    }
                    kind = "rect"  # TODO: dedicated interface item type
                    fill = main_rect.get("fill", "#FFFFFF")
                    stroke_color, stroke_width = _extract_stroke(main_rect)
                else:
                    # Actor (stick figure) or use-case ellipse (no rect)
                    all_x: List[float] = [cx - rx, cx + rx]
                    all_y: List[float] = [cy - ry, cy + ry]
                    if path_el is not None:
                        d = path_el.get("d", "")
                        for pm in re.finditer(
                            r'[ML]\s*([-+]?\d*\.?\d+)[,\s]([-+]?\d*\.?\d+)',
                            d,
                        ):
                            all_x.append(float(pm.group(1)))
                            all_y.append(float(pm.group(2)))
                    x = min(all_x)
                    y = min(all_y)
                    geom = {
                        "x": round(x, 2), "y": round(y, 2),
                        "w": round(max(all_x) - x, 2),
                        "h": round(max(all_y) - y, 2),
                    }
                    kind = "ellipse"
                    fill = ellipse_el.get("fill", "#FFFFFF")
                    stroke_color, stroke_width = _extract_stroke(ellipse_el)

            elif rects:
                # Find main rect (largest by area)
                main_rect = max(
                    rects,
                    key=lambda r: (
                        float(r.get("width", 0)) * float(r.get("height", 0))
                    ),
                )
                geom = {
                    "x": round(float(main_rect.get("x", 0)), 2),
                    "y": round(float(main_rect.get("y", 0)), 2),
                    "w": round(float(main_rect.get("width", 0)), 2),
                    "h": round(float(main_rect.get("height", 0)), 2),
                }
                # Detect UML component icon (extra small rects beside
                # the main shape).  Plain rectangles have a single rect.
                has_component_icon = len(rects) > 1
                kind = "roundedrect" if has_component_icon else "rect"
                fill = main_rect.get("fill", "#FFFFFF")
                stroke_color, stroke_width = _extract_stroke(main_rect)

            elif path_el is not None:
                # Check for interface entity: has ellipse + rect + path
                # (ellipse = circle icon, rect = name box, path = decoration)
                # TODO: Replace "rect" with a dedicated "interface" item type
                ellipse_el = g.find(f"{{{ns}}}ellipse")
                rect_el2 = g.find(f"{{{ns}}}rect")
                if ellipse_el is not None and rect_el2 is not None:
                    # Interface entity — use the rect as main geometry
                    rx = float(rect_el2.get("x", 0))
                    ry = float(rect_el2.get("y", 0))
                    rw = float(rect_el2.get("width", 0))
                    rh = float(rect_el2.get("height", 0))
                    # Include the ellipse in the bounding box
                    ecx = float(ellipse_el.get("cx", 0))
                    ecy = float(ellipse_el.get("cy", 0))
                    erx = float(ellipse_el.get("rx", 9))
                    ex, ey = ecx - erx, ecy - erx
                    x = min(rx, ex)
                    y = min(ry, ey)
                    w = max(rx + rw, ex + erx * 2) - x
                    h = max(ry + rh, ey + erx * 2) - y
                    geom = {
                        "x": round(x, 2), "y": round(y, 2),
                        "w": round(w, 2), "h": round(h, 2),
                    }
                    kind = "rect"  # TODO: dedicated interface item type
                    fill = rect_el2.get("fill", "#FFFFFF")
                    stroke_color, stroke_width = _extract_stroke(rect_el2)
                else:
                    # Note shape or other path-based entity
                    d = path_el.get("d", "")
                    bx, by, bw, bh = _path_bbox(d)
                    geom = {"x": bx, "y": by, "w": bw, "h": bh}
                    kind = "roundedrect"
                    fill = path_el.get("fill", "#FFFFFF")
                    stroke_color, stroke_width = _extract_stroke(path_el)

            else:
                # Check for polygon-based entity (deployment node without
                # children is rendered as entity, not cluster)
                polygon_el = g.find(f"{{{ns}}}polygon")
                if polygon_el is not None:
                    pts_str = polygon_el.get("points", "")
                    pts = re.findall(
                        r'([-+]?\d*\.?\d+),([-+]?\d*\.?\d+)', pts_str,
                    )
                    if pts:
                        xs = [float(p[0]) for p in pts]
                        ys = [float(p[1]) for p in pts]
                        x, y = min(xs), min(ys)
                        w, h = max(xs) - x, max(ys) - y
                        geom = {
                            "x": round(x, 2), "y": round(y, 2),
                            "w": round(w, 2), "h": round(h, 2),
                        }
                        abs_pts = [(float(p[0]), float(p[1])) for p in pts]
                        if _is_node_box_polygon(abs_pts):
                            kind = "isocube"
                            tab_x = abs(abs_pts[1][0] - abs_pts[0][0])
                            tab_y = abs(abs_pts[1][1] - abs_pts[0][1])
                            geom["adjust1"] = 14
                            geom["adjust2"] = 220
                        else:
                            kind = "polygon"
                            if w > 0 and h > 0:
                                geom["points"] = [
                                    [round((float(px) - x) / w, 4),
                                     round((float(py) - y) / h, 4)]
                                    for px, py in pts
                                ]
                        fill = polygon_el.get("fill", "#FFFFFF")
                        stroke_color, stroke_width = _extract_stroke(polygon_el)
                    else:
                        continue  # No recognizable shape
                else:
                    continue  # No recognizable shape

            # Text labels (dedup across label/tech/note)
            texts = [t.text for t in g.findall(f"{{{ns}}}text") if t.text]
            label = texts[0] if texts else (
                qname.rsplit(".", 1)[-1] if qname else ""
            )
            tech = texts[1] if len(texts) > 1 else ""
            note = " ".join(texts[2:]) if len(texts) > 2 else ""
            label, tech, note = _dedup_label_tech_note(label, tech, note)

            entity_info[ent_id] = {
                "kind": kind,
                "geom": geom,
                "fill": fill,
                "label": label,
                "tech": tech,
                "note": note,
                "stroke_color": stroke_color,
                "stroke_width": stroke_width,
            }
            all_geom[ent_id] = {
                "x": geom["x"], "y": geom["y"],
                "w": geom["w"], "h": geom["h"],
            }

        elif cls == "link":
            src_id = g.get("data-entity-1", "")
            dst_id = g.get("data-entity-2", "")
            if not src_id or not dst_id:
                continue

            texts = [t.text for t in g.findall(f"{{{ns}}}text") if t.text]
            all_paths = g.findall(f"{{{ns}}}path")
            polys = g.findall(f"{{{ns}}}polygon")

            # Separate main link path (stroke, no fill) from note paths (filled)
            link_path = None
            note_paths = []
            for p in all_paths:
                pfill = p.get("fill", "none").lower()
                if pfill in ("none", ""):
                    if link_path is None:
                        link_path = p
                else:
                    note_paths.append(p)

            style_str = (
                link_path.get("style", "") if link_path is not None else ""
            )
            d_attr = (
                link_path.get("d", "") if link_path is not None else ""
            )
            path_id = (
                link_path.get("id", "") if link_path is not None else ""
            )
            arrow_mode = _detect_arrow_mode(polys, path_id)

            # If note paths exist, split texts: first text = link label,
            # remaining texts = note content
            if note_paths:
                link_label = texts[0] if texts else ""
                note_texts = texts[1:] if len(texts) > 1 else []
                # Extract note geometry from the first filled path
                note_d = note_paths[0].get("d", "")
                note_fill = note_paths[0].get("fill", "#FFFDE7")
                nbx, nby, nbw, nbh = _path_bbox(note_d)
                note_stroke_color, note_stroke_width = _extract_stroke(
                    note_paths[0])
                note_label = note_texts[0] if note_texts else ""
                note_body = "\n".join(note_texts)
                note_label, _nt, note_body = _dedup_label_tech_note(
                    note_label, "", note_body)
                text_fmt = _extract_text_format(
                    g.findall(f"{{{ns}}}text"))
                entity_info[f"__note_on_link_{len(entity_info)}"] = {
                    "kind": "roundedrect",
                    "geom": {"x": nbx, "y": nby, "w": nbw, "h": nbh},
                    "fill": note_fill,
                    "label": note_label,
                    "tech": "",
                    "note": note_body,
                    "stroke_color": note_stroke_color or "#F57F17",
                    "stroke_width": note_stroke_width or 1,
                    **text_fmt,
                }
            else:
                link_label = " ".join(texts)

            link_list.append({
                "src_id": src_id,
                "dst_id": dst_id,
                "label": link_label,
                "style": style_str,
                "path_d": d_attr,
                "arrow_mode": arrow_mode,
            })

    if not cluster_info and not entity_info:
        return empty

    # ── Build parent map using qualified-name prefixes ─
    parent_map: Dict[str, str] = {}  # child_id → parent_id
    cluster_qnames_sorted = sorted(
        qname_to_id.keys(), key=len, reverse=True,
    )
    for ent_id, qname in id_to_qname.items():
        if not qname:
            continue
        for cq in cluster_qnames_sorted:
            if qname.startswith(cq + ".") and qname_to_id[cq] != ent_id:
                parent_map[ent_id] = qname_to_id[cq]
                break

    # ── Build individual annotations ─────────────────
    counter = 1
    id_to_ann: Dict[str, Dict[str, Any]] = {}

    # Title
    title_ann: Optional[Dict[str, Any]] = None
    if title_info:
        ann_id = f"p{counter:06d}"
        counter += 1
        title_ann = {
            "id": ann_id,
            "kind": "text",
            "geom": dict(title_info["geom"]),
            "meta": {
                "label": title_info["text"],
                "tech": "", "note": title_info["text"],
            },
            "style": {
                "pen": {"color": "#555555", "width": 2, "dash": "solid"},
                "fill": {"color": "#00000000"},
                "text": {"color": "#000000", "size_pt": 12.0},
            },
        }

    # Entities
    for ent_id, data in entity_info.items():
        ann_id = f"p{counter:06d}"
        counter += 1
        text_parts = [data["label"]]
        if data["tech"]:
            text_parts.append(f"[{data['tech']}]")
        text = " ".join(text_parts)

        ann: Dict[str, Any] = {
            "id": ann_id,
            "kind": data["kind"],
            "geom": dict(data["geom"]),
            "meta": {
                "label": data["label"],
                "tech": data["tech"],
                "note": data["note"] or text,
            },
            "style": {
                "pen": {
                    "color": data["stroke_color"],
                    "width": data["stroke_width"],
                    "dash": "solid",
                },
                "fill": {"color": _safe_fill(data["fill"])},
                "text": {"color": "#000000", "size_pt": 11.0},
            },
        }
        id_to_ann[ent_id] = ann

    # Clusters (as individual shape annotations)
    for ent_id, data in cluster_info.items():
        ann_id = f"p{counter:06d}"
        counter += 1
        text_parts = [data["label"]]
        if data["tech"]:
            text_parts.append(f"[{data['tech']}]")
        text = " ".join(text_parts)

        geom_copy = dict(data["geom"])
        ann = {
            "id": ann_id,
            "kind": data["kind"],
            "geom": geom_copy,
            "meta": {
                "label": data["label"],
                "tech": data["tech"],
                "note": data["note"] or text,
            },
            "style": {
                "pen": {
                    "color": data["stroke_color"],
                    "width": data["stroke_width"],
                    "dash": "solid",
                },
                "fill": {"color": _safe_fill(data["fill"])},
                "text": {"color": "#000000", "size_pt": 11.0},
            },
        }
        id_to_ann[ent_id] = ann

    # ── Group assembly (bottom-up) ───────────────────
    children_map: Dict[str, List[str]] = defaultdict(list)
    for child_id, parent_id in parent_map.items():
        if child_id in id_to_ann and parent_id in id_to_ann:
            children_map[parent_id].append(child_id)

    def _depth(ent_id: str) -> int:
        d = 0
        cur = ent_id
        while cur in parent_map:
            d += 1
            cur = parent_map[cur]
        return d

    grouped_ids: set = set()
    group_parents = sorted(
        [eid for eid in cluster_info if eid in children_map],
        key=_depth,
        reverse=True,
    )

    for parent_id in group_parents:
        child_ids = children_map[parent_id]
        if not child_ids:
            continue

        child_anns = [id_to_ann[cid] for cid in child_ids if cid in id_to_ann]
        child_anns.sort(key=_child_y)

        parent_ann = id_to_ann[parent_id]
        group_id = "g" + parent_ann["id"][1:]
        group_ann: Dict[str, Any] = {
            "id": group_id,
            "kind": "group",
            "children": [parent_ann] + child_anns,
            "meta": {
                "label": parent_ann["meta"]["label"],
                "tech": parent_ann["meta"].get("tech", ""),
                "note": parent_ann["meta"].get("note", ""),
            },
            "style": parent_ann["style"],
        }
        id_to_ann[parent_id] = group_ann
        grouped_ids.update(child_ids)

    # ── Connector annotations (curve when path available, line fallback)
    line_anns: List[Dict[str, Any]] = []
    for link in link_list:
        # Extract pen style common to both curve and line
        pen_color = "#808080"
        dashed = False
        style_str = link["style"]
        stroke_m = re.search(r'stroke:\s*(#[0-9A-Fa-f]{3,8})', style_str)
        if stroke_m:
            pen_color = stroke_m.group(1)
        if "stroke-dasharray" in style_str:
            dashed = True
        width_m = re.search(
            r'stroke-width:\s*(\d+(?:\.\d+)?)', style_str,
        )
        pen_width = int(float(width_m.group(1))) if width_m else 2

        # Try emitting a curve from the SVG path geometry
        d_attr = link.get("path_d", "")
        has_curves = bool(re.search(r"[CcSsQqTt]", d_attr)) if d_attr else False

        if has_curves:
            curve_nodes, (bx, by, bw, bh) = _parse_path_to_curve_nodes(d_attr)
            if curve_nodes and bw > 0 and bh > 0:
                arrow = link.get("arrow_mode", "end" if link.get("has_arrowhead") else "none")
                ann_id = f"p{counter:06d}"
                counter += 1
                line_anns.append({
                    "id": ann_id,
                    "kind": "curve",
                    "geom": {
                        "x": bx, "y": by, "w": bw, "h": bh,
                        "nodes": curve_nodes,
                    },
                    "meta": {
                        "label": link["label"],
                        "tech": "", "note": link["label"],
                    },
                    "style": _make_line_style(
                        pen_color, pen_width, dashed=dashed, arrow=arrow,
                    ),
                })
                continue

        # Degenerate curve (vertical/horizontal) → extract line from path
        if d_attr:
            coords = re.findall(r'[-+]?\d*\.?\d+', d_attr)
            if len(coords) >= 4:
                all_x = [float(coords[i]) for i in range(0, len(coords), 2)]
                all_y = [float(coords[i]) for i in range(1, len(coords), 2)]
                arrow = link.get("arrow_mode", "end" if link.get("has_arrowhead") else "none")
                ann_id = f"p{counter:06d}"
                counter += 1
                line_anns.append({
                    "id": ann_id,
                    "kind": "line",
                    "geom": {
                        "x1": round(all_x[0], 2), "y1": round(all_y[0], 2),
                        "x2": round(all_x[-1], 2), "y2": round(all_y[-1], 2),
                    },
                    "meta": {
                        "label": link["label"],
                        "tech": "", "note": link["label"],
                    },
                    "style": _make_line_style(
                        pen_color, pen_width, dashed=dashed, arrow=arrow,
                    ),
                })
                continue

        # Fallback: center-to-center line
        src_geom = all_geom.get(link["src_id"])
        dst_geom = all_geom.get(link["dst_id"])
        if not src_geom or not dst_geom:
            continue

        x1 = round(src_geom["x"] + src_geom["w"] / 2, 2)
        y1 = round(src_geom["y"] + src_geom["h"] / 2, 2)
        x2 = round(dst_geom["x"] + dst_geom["w"] / 2, 2)
        y2 = round(dst_geom["y"] + dst_geom["h"] / 2, 2)

        ann_id = f"p{counter:06d}"
        counter += 1
        line_anns.append({
            "id": ann_id,
            "kind": "line",
            "geom": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
            "meta": {
                "label": link["label"],
                "tech": "", "note": link["label"],
            },
            "style": _make_line_style(pen_color, pen_width, dashed=dashed),
        })

    # ── Collect top-level annotations ────────────────
    top_level: List[Dict[str, Any]] = []
    if title_ann:
        top_level.append(title_ann)

    # Add entities/clusters not consumed as group children
    all_ids = list(cluster_info.keys()) + list(entity_info.keys())
    for ent_id in all_ids:
        if ent_id in grouped_ids:
            continue
        ann = id_to_ann.get(ent_id)
        if ann:
            top_level.append(ann)

    top_level.extend(line_anns)

    # Sort by Y coordinate (title stays first)
    if title_ann and len(top_level) > 1:
        rest = top_level[1:]
        rest.sort(key=_child_y)
        top_level = [title_ann] + rest
    else:
        top_level.sort(key=_child_y)

    _normalize_annotations(top_level)

    # ── Enrich with ANTLR deployment source semantics ──
    if puml_text:
        src_info = _parse_deployment_source(puml_text)
        if src_info:
            _merge_deployment_source_info(top_level, src_info, id_to_qname)

    return {
        "version": "draft-1",
        "image": {"width": canvas_w, "height": canvas_h},
        "annotations": top_level,
    }


def _merge_deployment_source_info(
    annotations: List[Dict[str, Any]],
    src_info: Dict[str, Dict[str, Any]],
    id_to_qname: Dict[str, str],
) -> None:
    """Merge ANTLR-parsed deployment source info into SVG annotations.

    Adds ``meta.dsl.puml_type`` (element keyword) and ``meta.dsl.stereotype``
    for each annotation whose label or qualified name matches a source element.
    Recurses into group children.
    """
    # Build a reverse index: name → info (for matching by display name)
    name_index: Dict[str, Dict[str, Any]] = {}
    for info in src_info.values():
        name_index[info["name"].lower()] = info
        if info["alias"]:
            name_index[info["alias"].lower()] = info

    def _enrich(ann: Dict[str, Any]) -> None:
        meta = ann.get("meta", {})
        label = meta.get("label", "").strip()

        # Try matching by label, alias, or name (case-insensitive)
        match = (src_info.get(label.lower())
                 or name_index.get(label.lower())
                 or name_index.get(label.strip('"').lower()))

        if match:
            dsl = meta.setdefault("dsl", {})
            if match["keyword"]:
                dsl["puml_type"] = match["keyword"]
            if match["stereotype"]:
                dsl["stereotype"] = match["stereotype"]

        # Recurse into group children
        for child in ann.get("children", []):
            _enrich(child)

    for ann in annotations:
        _enrich(ann)


# ───────────────────────────────────────────────
# ANTLR4-based PlantUML state source parser
# ───────────────────────────────────────────────

def _parse_state_source(puml_text: str) -> Dict[str, Dict[str, Any]]:
    """Parse PlantUML state source with the ANTLR4 grammar.

    Returns a dict keyed by state name/alias (lowercase) with values::

        {
            "name": "ActiveState",
            "alias": "active",
            "stereotype": "<<choice>>",
            "descriptions": ["entry / init", "do / process"],
            "is_composite": True,
            "has_concurrent": False,
        }

    Returns an empty dict if the grammar is unavailable or parsing fails.
    """
    try:
        from antlr4 import CommonTokenStream, InputStream
        from plantuml.grammar.generated.PlantUMLStateLexer import PlantUMLStateLexer
        from plantuml.grammar.generated.PlantUMLStateParser import PlantUMLStateParser
        from plantuml.grammar.generated.PlantUMLStateVisitor import PlantUMLStateVisitor
    except ImportError:
        return {}

    class _Visitor(PlantUMLStateVisitor):
        def __init__(self):
            self.elements: Dict[str, Dict[str, Any]] = {}
            self._descriptions: Dict[str, List[str]] = defaultdict(list)
            self._parent_stack: List[str] = []  # stack of composite state keys
            self.children: Dict[str, List[str]] = defaultdict(list)  # parent → [child keys]

        def _store(self, ctx, name, alias, stereotype="",
                   is_composite=False, has_concurrent=False):
            if not name:
                return
            clean_name = name.strip('"')
            clean_alias = alias.strip('"') if alias else ""
            key = (clean_alias or clean_name).lower()
            existing = self.elements.get(key)
            if existing:
                # Merge: keep richer data from earlier declaration
                if clean_name and len(clean_name) > len(existing["name"]):
                    existing["name"] = clean_name
                if clean_alias and not existing["alias"]:
                    existing["alias"] = clean_alias
                if stereotype and not existing["stereotype"]:
                    existing["stereotype"] = stereotype
                if is_composite:
                    existing["is_composite"] = True
                if has_concurrent:
                    existing["has_concurrent"] = True
            else:
                self.elements[key] = {
                    "name": clean_name,
                    "alias": clean_alias,
                    "stereotype": stereotype,
                    "descriptions": [],
                    "is_composite": is_composite,
                    "has_concurrent": has_concurrent,
                    "children": [],
                    "parent": "",
                }
            # Record parent-child relationship
            if self._parent_stack:
                parent_key = self._parent_stack[-1]
                self.elements[key].setdefault("parent", "")
                if not self.elements[key]["parent"]:
                    self.elements[key]["parent"] = parent_key
                if key not in self.children[parent_key]:
                    self.children[parent_key].append(key)

        def visitStateDecl(self, ctx):
            name = ctx.stateName().getText() if ctx.stateName() else ""
            alias = ""
            if ctx.aliasClause():
                alias = ctx.aliasClause().stateName().getText()
            stereotype = ctx.stereotypeClause().getText() if ctx.stereotypeClause() else ""
            self._store(ctx, name, alias, stereotype)
            # Inline description: state Name <<stereo>> : text
            if ctx.COLON() and ctx.restOfLine():
                clean_name = name.strip('"')
                clean_alias = alias.strip('"') if alias else ""
                key = (clean_alias or clean_name).lower()
                self._descriptions[key].append(ctx.restOfLine().getText().strip())
            return self.visitChildren(ctx)

        def visitCompositeBlock(self, ctx):
            name = ctx.stateName().getText() if ctx.stateName() else ""
            alias = ""
            if ctx.aliasClause():
                alias = ctx.aliasClause().stateName().getText()
            stereotype = ctx.stereotypeClause().getText() if ctx.stereotypeClause() else ""
            has_concurrent = False
            for stmt in (ctx.statement() or []):
                if stmt.concurrentSep():
                    has_concurrent = True
                    break
            self._store(ctx, name, alias, stereotype,
                        is_composite=True, has_concurrent=has_concurrent)
            # Push onto parent stack so child states record this as parent
            clean_alias = alias.strip('"') if alias else ""
            clean_name = name.strip('"')
            key = (clean_alias or clean_name).lower()
            self._parent_stack.append(key)
            result = self.visitChildren(ctx)
            self._parent_stack.pop()
            # Copy children list into element
            if key in self.elements:
                self.elements[key]["children"] = list(self.children.get(key, []))
            return result

        def visitDescriptionStmt(self, ctx):
            try:
                ref = ctx.stateRef().getText().strip('"')
                desc = ctx.restOfLine().getText().strip() if ctx.restOfLine() else ""
                if ref and desc:
                    self._descriptions[ref.lower()].append(desc)
            except Exception:
                pass
            return self.visitChildren(ctx)

        def finalize(self):
            """Merge collected descriptions into elements."""
            for key, descs in self._descriptions.items():
                if key in self.elements:
                    self.elements[key]["descriptions"] = descs
                else:
                    self.elements[key] = {
                        "name": key, "alias": "", "stereotype": "",
                        "descriptions": descs,
                        "is_composite": False, "has_concurrent": False,
                        "children": [], "parent": "",
                    }

    try:
        input_stream = InputStream(puml_text)
        lexer = PlantUMLStateLexer(input_stream)
        lexer.removeErrorListeners()
        token_stream = CommonTokenStream(lexer)
        parser = PlantUMLStateParser(token_stream)
        parser.removeErrorListeners()
        tree = parser.diagram()
        if parser.getNumberOfSyntaxErrors() > 0:
            # Parse with errors — still try to extract what we can
            pass
        visitor = _Visitor()
        visitor.visit(tree)
        visitor.finalize()
        return visitor.elements
    except Exception:
        return {}


def _merge_state_source_info(
    annotations: List[Dict[str, Any]],
    src_info: Dict[str, Dict[str, Any]],
) -> None:
    """Merge ANTLR-parsed state source info into SVG annotations.

    Adds ``contents.dsl.stereotype``, ``contents.dsl.descriptions``,
    ``contents.dsl.is_composite``, and ``contents.dsl.has_concurrent``
    for each annotation whose label matches a source element.
    Recurses into group children.
    """
    # Build reverse index: name/alias/full-name → info
    name_index: Dict[str, Dict[str, Any]] = {}
    for info in src_info.values():
        name_index[info["name"].lower()] = info
        if info["alias"]:
            name_index[info["alias"].lower()] = info
        # Also index with \n as literal for multiline matching
        if "\\n" in info["name"]:
            name_index[info["name"].lower()] = info

    def _enrich(ann: Dict[str, Any]) -> None:
        contents = ann.get("contents") or ann.get("meta") or {}

        # Collect all text parts from blocks (label, tech, etc.)
        blocks = contents.get("blocks", [])
        text_parts = []
        for b in blocks:
            for r in b.get("runs", []):
                t = r.get("text", "").strip()
                if t:
                    text_parts.append(t)

        label = text_parts[0] if text_parts else contents.get("label", "")
        # Build full name by joining label + tech lines (for multiline states)
        full_text = "\\n".join(text_parts[:2]) if len(text_parts) >= 2 else label

        match = (src_info.get(label.lower())
                 or name_index.get(label.lower())
                 or name_index.get(label.strip('"').lower()))

        # Try matching by full multiline name (label + tech combined)
        if not match and full_text != label:
            match = name_index.get(full_text.lower())

        # Try matching ANTLR name (with \n) against SVG combined text
        if not match:
            for info in src_info.values():
                antlr_name = info["name"].replace("\\n", "\\n")
                if antlr_name.lower() == full_text.lower():
                    match = info
                    break

        # Fallback: match by first line only (when no ambiguity)
        if not match:
            first_line_matches = []
            for info in src_info.values():
                first_line = info["name"].split("\\n")[0].strip()
                if first_line.lower() == label.lower():
                    first_line_matches.append(info)
            if len(first_line_matches) == 1:
                match = first_line_matches[0]

        # Pseudo-state matching deferred to second pass (see below)

        # Choice diamond matching: [choice] label → match by <<choice>> stereotype
        if not match and label == "[choice]":
            candidates = [
                (k, i) for k, i in src_info.items()
                if i.get("stereotype", "").lower() == "<<choice>>"
                and k not in matched_keys
            ]
            if len(candidates) == 1:
                match = candidates[0][1]
            elif len(candidates) >= 2:
                # Multiple choices — match by proximity to annotation position
                ann_y = ann.get("geom", {}).get("y", 0)
                # Not enough info to disambiguate perfectly; take first unmatched
                match = candidates[0][1]

        # Fork/join bar matching: [fork/join] label → match by stereotype
        if not match and label == "[fork/join]":
            geom = ann.get("geom", {})
            bar_y = geom.get("y", 0)
            # Find unmatched entries with <<fork>> or <<join>> stereotypes
            candidates = []
            for k, info in src_info.items():
                s = info.get("stereotype", "").lower()
                if s in ("<<fork>>", "<<join>>") and k not in matched_keys:
                    candidates.append((k, info))
            if len(candidates) == 1:
                match = candidates[0][1]
            elif len(candidates) >= 2:
                # Fork appears before join (lower y = higher up on screen)
                fork_cands = [(k, i) for k, i in candidates if "fork" in i["stereotype"].lower()]
                join_cands = [(k, i) for k, i in candidates if "join" in i["stereotype"].lower()]
                if fork_cands and not _fork_join_bars:
                    # First bar encountered → assign fork
                    match = fork_cands[0][1]
                elif join_cands:
                    match = join_cands[0][1]
            if match:
                _fork_join_bars.append(ann)

        if match:
            matched_keys.add((match.get("alias") or match["name"]).lower())
            # Get or create dsl dict in the right location
            if "contents" in ann:
                dsl = ann["contents"].setdefault("dsl", {})
            elif "meta" in ann:
                dsl = ann["meta"].setdefault("dsl", {})
            else:
                return
            if match["stereotype"]:
                dsl["stereotype"] = match["stereotype"]
            if match["descriptions"]:
                dsl["descriptions"] = match["descriptions"]
            if match["is_composite"]:
                dsl["is_composite"] = True
            if match["has_concurrent"]:
                dsl["has_concurrent"] = True
            # Update label for pseudo-state bars/diamonds/points/pins
            if label in ("[fork/join]", "[choice]", "[point]", "[pin]", "[expansion]"):
                stereo = match["stereotype"].strip("<>")
                # Use the declared name if available, else stereotype
                new_label = match.get("name", "") or f"[{stereo}]"
                if "contents" in ann:
                    blocks = ann["contents"].get("blocks", [])
                    if blocks and blocks[0].get("runs"):
                        blocks[0]["runs"][0]["text"] = new_label

        # Recurse into group children
        for child in ann.get("children", []):
            _enrich(child)

    matched_keys: set = set()
    _fork_join_bars: List[Dict[str, Any]] = []

    for ann in annotations:
        _enrich(ann)

    # ── Second pass: deferred pseudo-state matching ──
    # Collect unmatched pseudo-state annotations, sort by position,
    # then pair with ANTLR entries in declaration order.
    _PSEUDO_LABELS = ("[point]", "[pin]", "[expansion]")
    _PSEUDO_STEREO_MAP = {
        "[point]": ("<<entrypoint>>", "<<exitpoint>>",
                    "<<inputpin>>", "<<outputpin>>"),
        "[pin]": ("<<inputpin>>", "<<outputpin>>"),
        "[expansion]": ("<<expansioninput>>", "<<expansionoutput>>"),
    }

    def _collect_pseudo(anns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Collect all annotations with pseudo-state labels, recursively."""
        result = []
        for a in anns:
            c = a.get("contents") or a.get("meta") or {}
            blocks = c.get("blocks", [])
            lbl = blocks[0]["runs"][0]["text"] if blocks and blocks[0].get("runs") else ""
            if lbl in _PSEUDO_LABELS:
                result.append(a)
            result.extend(_collect_pseudo(a.get("children", [])))
        return result

    for pseudo_label in _PSEUDO_LABELS:
        target_stereos = _PSEUDO_STEREO_MAP[pseudo_label]
        # Get unmatched ANTLR entries with these stereotypes, in declaration order
        antlr_entries = [
            (k, i) for k, i in src_info.items()
            if i.get("stereotype", "").lower() in target_stereos
            and k not in matched_keys
        ]
        if not antlr_entries:
            continue
        # Get unmatched SVG annotations with this label, sorted by position (y, then x)
        pseudo_anns = [
            a for a in _collect_pseudo(annotations)
            if (a.get("contents") or a.get("meta") or {}).get("blocks", [{}])[0]
               .get("runs", [{}])[0].get("text", "") == pseudo_label
        ]
        pseudo_anns.sort(key=lambda a: (a.get("geom", {}).get("y", 0),
                                         a.get("geom", {}).get("x", 0)))
        # Pair them up: SVG sorted by position ↔ ANTLR in declaration order
        for pa, (ak, ai) in zip(pseudo_anns, antlr_entries):
            matched_keys.add(ak)
            if "contents" in pa:
                dsl = pa["contents"].setdefault("dsl", {})
            elif "meta" in pa:
                dsl = pa["meta"].setdefault("dsl", {})
            else:
                continue
            if ai["stereotype"]:
                dsl["stereotype"] = ai["stereotype"]
            # Update label to declared name
            new_label = ai.get("name", "") or ai["stereotype"].strip("<>")
            if "contents" in pa:
                blocks = pa["contents"].get("blocks", [])
                if blocks and blocks[0].get("runs"):
                    blocks[0]["runs"][0]["text"] = new_label

    # ── Create synthetic groups for missing composite states ──
    # Build ann lookup by label (lowercase) for child matching
    ann_by_label: Dict[str, Dict[str, Any]] = {}
    def _index_ann(ann: Dict[str, Any]) -> None:
        c = ann.get("contents") or ann.get("meta") or {}
        blocks = c.get("blocks", [])
        if blocks:
            for b in blocks:
                for r in b.get("runs", []):
                    t = r.get("text", "").strip()
                    if t:
                        ann_by_label[t.lower()] = ann
                        break
                break
        for child in ann.get("children", []):
            _index_ann(child)
    for ann in annotations:
        _index_ann(ann)

    def _nesting_depth(key: str) -> int:
        """Compute nesting depth from ANTLR parent chain."""
        depth = 0
        cur = key
        seen: set = set()
        while cur in src_info and src_info[cur].get("parent") and cur not in seen:
            seen.add(cur)
            cur = src_info[cur]["parent"]
            depth += 1
        return depth

    # Find composites with children that ARE in the SVG but the composite itself is NOT
    missing_composite_keys = []
    for key, info in src_info.items():
        if not info.get("is_composite") or not info.get("children"):
            continue
        if key in matched_keys:
            continue
        first_line = info["name"].split("\\n")[0].strip().lower()
        if first_line in matched_keys:
            continue
        missing_composite_keys.append(key)

    # Sort by depth (deepest first) so inner groups are created before outer
    missing_composite_keys.sort(key=lambda x: _nesting_depth(x), reverse=True)

    for key in missing_composite_keys:
        info = src_info[key]
        # Find child annotations (lookup at synthesis time so earlier synthetics are found)
        child_anns = []
        for child_key in info["children"]:
            child_info = src_info.get(child_key, {})
            child_name = child_info.get("name", child_key)
            child_alias = child_info.get("alias", "")
            ca = (ann_by_label.get(child_name.lower())
                  or ann_by_label.get(child_alias.lower())
                  or ann_by_label.get(child_key.lower())
                  or ann_by_label.get(child_name.split("\\n")[0].strip().lower()))
            if ca:
                child_anns.append(ca)
        if not child_anns:
            print(f"[STATE] ANTLR composite not found in SVG (no children matched): "
                  f"name={info['name']!r} alias={info['alias']!r}")
            continue
        # Compute bounding box from children
        min_x = min(a["geom"]["x"] for a in child_anns)
        min_y = min(a["geom"]["y"] for a in child_anns)
        max_x = max(a["geom"]["x"] + a["geom"].get("w", 0) for a in child_anns)
        max_y = max(a["geom"]["y"] + a["geom"].get("h", 0) for a in child_anns)
        pad = 20  # padding around children
        group_geom = {
            "x": round(min_x - pad, 2),
            "y": round(min_y - pad - 20, 2),  # extra top for label
            "w": round(max_x - min_x + 2 * pad, 2),
            "h": round(max_y - min_y + 2 * pad + 20, 2),
        }

        depth = _nesting_depth(key)
        # Outer composites behind inner: deeper nesting = higher z (in front)
        # depth 0 (outermost) = z=-10, depth 1 = z=-9, etc.
        max_depth = max(_nesting_depth(k) for k in missing_composite_keys) if missing_composite_keys else 0
        z_order = -(max_depth - depth) - 1

        group_id = f"g_synth_{key}"
        label = info["name"].split("\\n")[0].strip()
        stereotype = info.get("stereotype", "")

        # Build the group annotation as a roundedrect (not a PictoSync group)
        # so it renders as a visible container behind its children.
        # Use contents format directly since _normalize_annotations already ran.
        from models import CharFormat, TextBlock, TextRun, TextFrame
        tech_text = stereotype.strip("<>") if stereotype else ""
        synth_blocks = [
            TextBlock(runs=[TextRun(type="text", text=label,
                                     format=CharFormat(bold=True, font_size=11))]),
        ]
        if tech_text:
            synth_blocks.append(
                TextBlock(runs=[TextRun(type="text", text=tech_text,
                                         format=CharFormat(italic=True, font_size=9))]),
            )
        group_ann: Dict[str, Any] = {
            "id": group_id,
            "kind": "roundedrect",
            "geom": group_geom,
            "contents": {
                "frame": TextFrame(halign="center", valign="top").to_dict(),
                "default_format": CharFormat(font_size=11).to_dict(),
                "blocks": [b.to_dict() for b in synth_blocks],
                "wrap": True,
                "dsl": {
                    "is_composite": True,
                    "synthesized": True,
                },
            },
            "style": {
                "pen": {"color": "#888888", "width": 1, "dash": "dashed"},
                "fill": {"color": "#F8F8F820"},
                "text": {"color": "#555555", "size_pt": 11.0},
            },
        }
        if stereotype:
            group_ann["contents"]["dsl"]["stereotype"] = stereotype
        if z_order != 0:
            group_ann["z"] = z_order

        # Remove children from top_level and add the group
        child_set = set(id(a) for a in child_anns)
        annotations[:] = [a for a in annotations if id(a) not in child_set]
        annotations.append(group_ann)
        # Re-add children after the group (higher z = in front)
        annotations.extend(child_anns)

        # Register for further parent lookups
        ann_by_label[label.lower()] = group_ann
        matched_keys.add(key)
        print(f"[STATE] Synthesized composite: {label!r} with "
              f"{len(child_anns)} children, z={z_order}")


# ───────────────────────────────────────────────
# STATE diagram SVG parser
# ───────────────────────────────────────────────

def _parse_state_diagram_svg(
    tree: ET.ElementTree,
    puml_text: str = "",
) -> Dict[str, Any]:
    """Parse a STATE diagram SVG into PictoSync annotations.

    State diagrams use a mix of classified and unclassified ``<g>`` groups:
    clusters for composite states, unnamed ``<g>`` for regular states,
    ``<g class="entity">`` for notes, ``<g class="link">`` for transitions,
    and bare ``<ellipse>`` for initial ``[*]`` markers.

    Args:
        tree: Parsed ElementTree of the SVG file.

    Returns:
        Dict with PictoSync schema: ``{"version", "image", "annotations"}``.
    """
    root = tree.getroot()
    ns = _SVG_NS

    # ── Canvas dimensions ────────────────────────────
    viewbox = root.get("viewBox", "").split()
    canvas_w = int(float(viewbox[2])) if len(viewbox) >= 3 else 1200
    canvas_h = int(float(viewbox[3])) if len(viewbox) >= 4 else 800

    empty: Dict[str, Any] = {
        "version": "draft-1",
        "image": {"width": canvas_w, "height": canvas_h},
        "annotations": [],
    }

    # ── Helpers ──────────────────────────────────────

    def _safe_fill(fill: str) -> str:
        if not fill or fill.lower() == "none" or not fill.startswith("#"):
            return "#00000000"
        return _normalize_color(fill)

    def _extract_stroke(el: ET.Element) -> Tuple[str, int]:
        style = el.get("style", "")
        sm = re.search(r'stroke:\s*(#[0-9A-Fa-f]{3,8})', style)
        wm = re.search(r'stroke-width:\s*(\d+(?:\.\d+)?)', style)
        return (
            sm.group(1).upper() if sm else "#000000",
            int(float(wm.group(1))) if wm else 1,
        )

    def _child_y(ann: Dict[str, Any]) -> float:
        if "geom" in ann:
            g = ann["geom"]
            return g.get("y", g.get("y1", 0))
        if ann.get("children"):
            return _child_y(ann["children"][0])
        return 0.0

    # ── Pass 1: collect data from root <g> children ──
    title_info: Optional[Dict[str, Any]] = None
    cluster_info: Dict[str, Dict[str, Any]] = {}
    unnamed_states: List[Dict[str, Any]] = []  # ordered list
    note_info: Dict[str, Dict[str, Any]] = {}
    initial_ellipses: List[Dict[str, Any]] = []
    all_geom: Dict[str, Dict[str, Any]] = {}
    link_list: List[Dict[str, Any]] = []

    root_g = root.find(f"{{{ns}}}g")
    if root_g is None:
        return empty

    for child in root_g:
        tag_local = child.tag.split("}")[-1] if "}" in child.tag else child.tag

        if tag_local == "g":
            cls = child.get("class", "")

            if cls == "title":
                # Collect all text elements (multi-line title)
                text_items: List[Dict[str, Any]] = []
                for t in child.findall(f"{{{ns}}}text"):
                    txt = t.text or ""
                    if txt.strip():
                        text_items.append({
                            "text": txt.strip(),
                            "x": float(t.get("x", 0)),
                            "y": float(t.get("y", 0)),
                            "fs": float(t.get("font-size", 14)),
                            "tl": float(t.get("textLength", 200)),
                        })
                if text_items:
                    all_x = [ti["x"] for ti in text_items]
                    all_x2 = [ti["x"] + ti["tl"] for ti in text_items]
                    all_y = [ti["y"] - ti["fs"] for ti in text_items]
                    all_y2 = [ti["y"] for ti in text_items]
                    title_info = {
                        "text": " ".join(ti["text"] for ti in text_items),
                        "geom": {
                            "x": round(min(all_x), 2),
                            "y": round(min(all_y), 2),
                            "w": round(max(all_x2) - min(all_x), 2),
                            "h": round(
                                max(all_y2) - min(all_y)
                                + text_items[-1]["fs"] * 0.5,
                                2,
                            ),
                        },
                    }

            elif cls == "cluster":
                ent_id = child.get("id", "")
                if not ent_id:
                    continue

                # Outer rect (fill="none") gives border geometry
                rect_el = None
                for r in child.findall(f"{{{ns}}}rect"):
                    if r.get("fill", "").lower() == "none":
                        rect_el = r
                        break
                if rect_el is None:
                    continue

                geom: Dict[str, Any] = {
                    "x": round(float(rect_el.get("x", 0)), 2),
                    "y": round(float(rect_el.get("y", 0)), 2),
                    "w": round(float(rect_el.get("width", 0)), 2),
                    "h": round(float(rect_el.get("height", 0)), 2),
                }

                # Header path gives fill colour
                path_el = child.find(f"{{{ns}}}path")
                fill = (
                    path_el.get("fill", "#FFFFFF")
                    if path_el is not None
                    else "#FFFFFF"
                )
                stroke_color, stroke_width = _extract_stroke(rect_el)

                # First <line> divider separates name from description
                lines_el = child.findall(f"{{{ns}}}line")
                line_ys = sorted(
                    float(ln.get("y1", 0)) for ln in lines_el
                )
                first_div_y = line_ys[0] if line_ys else float("inf")

                # Texts: above divider = name, below = description
                name_parts: List[str] = []
                desc_parts: List[str] = []
                for t in child.findall(f"{{{ns}}}text"):
                    ty = float(t.get("y", 0))
                    txt = (t.text or "").strip()
                    if not txt:
                        continue
                    if ty < first_div_y:
                        name_parts.append(txt)
                    else:
                        desc_parts.append(txt)

                label = name_parts[0] if name_parts else ""
                tech = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
                note = "\n".join(desc_parts)
                label, tech, note = _dedup_label_tech_note(label, tech, note)

                text_fmt = _extract_text_format(
                    child.findall(f"{{{ns}}}text"))
                cluster_info[ent_id] = {
                    "kind": "roundedrect",
                    "geom": geom,
                    "fill": fill,
                    "label": label,
                    "tech": tech,
                    "note": note,
                    "stroke_color": stroke_color,
                    "stroke_width": stroke_width,
                    **text_fmt,
                }
                all_geom[ent_id] = {
                    "x": geom["x"], "y": geom["y"],
                    "w": geom["w"], "h": geom["h"],
                }

            elif cls == "entity":
                ent_id = child.get("id", "")
                if not ent_id:
                    continue

                path_el = child.find(f"{{{ns}}}path")
                rect_el = child.find(f"{{{ns}}}rect")

                if path_el is not None:
                    # Note shape (path-based, e.g. folded corner)
                    d = path_el.get("d", "")
                    bx, by, bw, bh = _path_bbox(d)
                    geom = {"x": bx, "y": by, "w": bw, "h": bh}
                    fill = path_el.get("fill", "#FEFFDD")
                    stroke_color, stroke_width = _extract_stroke(path_el)

                    texts: List[str] = []
                    for t in child.findall(f"{{{ns}}}text"):
                        txt = (t.text or "").replace("\xa0", "").strip()
                        if txt:
                            texts.append(txt)

                    label = texts[0] if texts else ""
                    note_text = "\n".join(texts)
                    label, _tech, note_text = _dedup_label_tech_note(label, "", note_text)
                    text_fmt = _extract_text_format(
                        child.findall(f"{{{ns}}}text"))

                    note_info[ent_id] = {
                        "kind": "roundedrect",
                        "geom": geom,
                        "fill": fill,
                        "label": label,
                        "tech": "",
                        "note": note_text,
                        "stroke_color": stroke_color,
                        "stroke_width": stroke_width,
                        **text_fmt,
                    }
                    all_geom[ent_id] = {
                        "x": geom["x"], "y": geom["y"],
                        "w": geom["w"], "h": geom["h"],
                    }

                elif rect_el is not None:
                    # Regular state (rect-based entity — same structure as
                    # unnamed states but with class="entity" and an id)
                    line_el = child.find(f"{{{ns}}}line")
                    text_els = child.findall(f"{{{ns}}}text")
                    geom = {
                        "x": round(float(rect_el.get("x", 0)), 2),
                        "y": round(float(rect_el.get("y", 0)), 2),
                        "w": round(float(rect_el.get("width", 0)), 2),
                        "h": round(float(rect_el.get("height", 0)), 2),
                    }
                    fill = rect_el.get("fill", "#F1F1F1")
                    stroke_color, stroke_width = _extract_stroke(rect_el)

                    div_y = float(line_el.get("y1", 9999)) if line_el is not None else 9999
                    name_parts = []
                    desc_parts = []
                    for t in text_els:
                        ty = float(t.get("y", 0))
                        txt = (t.text or "").strip()
                        if not txt:
                            continue
                        if ty < div_y:
                            name_parts.append(txt)
                        else:
                            desc_parts.append(txt)

                    label = name_parts[0] if name_parts else ""
                    tech = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
                    note_text = "\n".join(desc_parts)
                    label, tech, note_text = _dedup_label_tech_note(label, tech, note_text)

                    text_fmt = _extract_text_format(text_els)
                    unnamed_states.append({
                        "kind": "roundedrect",
                        "geom": geom,
                        "fill": fill,
                        "label": label,
                        "tech": tech,
                        "note": note_text,
                        "stroke_color": stroke_color,
                        "stroke_width": stroke_width,
                        "name_parts": name_parts,
                        "ent_id": ent_id,
                        **text_fmt,
                    })
                    all_geom[ent_id] = {
                        "x": geom["x"], "y": geom["y"],
                        "w": geom["w"], "h": geom["h"],
                    }

                else:
                    # Check for polygon (choice diamond <<choice>>)
                    poly_el = child.find(f"{{{ns}}}polygon")
                    if poly_el is not None:
                        pts_str = poly_el.get("points", "")
                        pts = re.findall(
                            r'([-+]?\d*\.?\d+),([-+]?\d*\.?\d+)', pts_str,
                        )
                        if len(pts) >= 4:
                            xs = [float(p[0]) for p in pts]
                            ys = [float(p[1]) for p in pts]
                            px, py = min(xs), min(ys)
                            pw, ph = max(xs) - px, max(ys) - py
                            fill = poly_el.get("fill", "#F1F1F1")
                            stroke_color, stroke_width = _extract_stroke(poly_el)
                            unnamed_states.append({
                                "kind": "polygon",
                                "geom": {
                                    "x": round(px, 2), "y": round(py, 2),
                                    "w": round(pw, 2), "h": round(ph, 2),
                                    "points": [
                                        [round((float(p[0]) - px) / pw, 4),
                                         round((float(p[1]) - py) / ph, 4)]
                                        for p in pts[:4]  # 4-point diamond
                                    ],
                                },
                                "fill": fill,
                                "label": "[choice]",
                                "tech": "",
                                "note": "",
                                "stroke_color": stroke_color,
                                "stroke_width": stroke_width,
                                "name_parts": ["[choice]"],
                                "ent_id": ent_id,
                            })
                            all_geom[ent_id] = {
                                "x": round(px, 2), "y": round(py, 2),
                                "w": round(pw, 2), "h": round(ph, 2),
                            }

            elif cls in ("start_entity", "end_entity"):
                # [*] pseudo-state wrapped in a <g class="start_entity"> or "end_entity"
                # Use a synthetic key to avoid colliding with entity IDs
                # (PlantUML reuses ent_id for both the [*] and a regular entity)
                ent_id = child.get("id", "")
                ells = child.findall(f"{{{ns}}}ellipse")
                ell = ells[0] if ells else None
                if ell is not None:
                    cx = float(ell.get("cx", 0))
                    cy = float(ell.get("cy", 0))
                    # Use outermost ellipse for geometry
                    rx = max(float(e.get("rx", 10)) for e in ells)
                    ry = max(float(e.get("ry", 10)) for e in ells)
                    is_end = cls == "end_entity"
                    prefix = "__end_" if is_end else "__start_"
                    if is_end:
                        # End state: white fill with thick black border (bullseye)
                        fill = "#FFFFFFFF"
                    else:
                        # Start state: solid dark fill
                        fill = ell.get("fill", "#222222")
                    synth_id = f"{prefix}{ent_id}" if ent_id else f"{prefix}_"
                    geom = {
                        "x": round(cx - rx, 2),
                        "y": round(cy - ry, 2),
                        "w": round(rx * 2, 2),
                        "h": round(ry * 2, 2),
                    }
                    initial_ellipses.append({
                        "kind": "ellipse",
                        "geom": geom,
                        "fill": fill,
                        "ent_id": synth_id,
                        "svg_ent_id": ent_id,
                        "is_end": is_end,
                    })
                    all_geom[synth_id] = dict(geom)

            elif cls == "link":
                src_id = child.get("data-entity-1", "")
                dst_id = child.get("data-entity-2", "")
                if not src_id or not dst_id:
                    continue

                link_type = child.get("data-link-type", "dependency")
                link_text_els = child.findall(f"{{{ns}}}text")
                texts_el = [t.text for t in link_text_els if t.text]
                label = "\n".join(texts_el)
                link_text_fmt = _extract_text_format(link_text_els)

                link_path = child.find(f"{{{ns}}}path")
                style_str = (
                    link_path.get("style", "")
                    if link_path is not None
                    else ""
                )
                d_attr = (
                    link_path.get("d", "")
                    if link_path is not None
                    else ""
                )
                path_id = (
                    link_path.get("id", "")
                    if link_path is not None
                    else ""
                )
                polys = child.findall(f"{{{ns}}}polygon")

                link_list.append({
                    "src_id": src_id,
                    "dst_id": dst_id,
                    "label": label,
                    "style": style_str,
                    "path_d": d_attr,
                    "path_id": path_id,
                    "link_type": link_type,
                    "has_arrowhead": len(polys) > 0,
                    "arrow_mode": _detect_arrow_mode(polys, path_id, link_type),
                    "text_fmt": link_text_fmt,
                })

            elif not cls:
                # Unnamed <g> — detect regular state or composite container:
                # <rect rx="12.5"> + <line> + <text>
                # Composite containers have fill="none" (transparent border)
                rect_el = child.find(f"{{{ns}}}rect")
                line_el = child.find(f"{{{ns}}}line")
                text_els = child.findall(f"{{{ns}}}text")

                if (
                    rect_el is not None
                    and line_el is not None
                    and text_els
                    and float(rect_el.get("rx", 0)) >= 10
                ):
                    fill_val = rect_el.get("fill", "#F1F1F1")
                    is_composite_rect = fill_val.lower() in ("none", "")

                    geom = {
                        "x": round(float(rect_el.get("x", 0)), 2),
                        "y": round(float(rect_el.get("y", 0)), 2),
                        "w": round(float(rect_el.get("width", 0)), 2),
                        "h": round(float(rect_el.get("height", 0)), 2),
                    }

                    if is_composite_rect:
                        # Composite state container (rendered without class="cluster")
                        stroke_color, stroke_width = _extract_stroke(rect_el)
                        div_y = float(line_el.get("y1", 0))
                        name_parts = []
                        desc_parts = []
                        for t in text_els:
                            ty = float(t.get("y", 0))
                            txt = (t.text or "").strip()
                            if not txt:
                                continue
                            if ty < div_y:
                                name_parts.append(txt)
                            else:
                                desc_parts.append(txt)
                        label = name_parts[0] if name_parts else ""
                        tech = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
                        note_text = "\n".join(desc_parts)
                        label, tech, note_text = _dedup_label_tech_note(label, tech, note_text)
                        # Use a synthetic cluster ID
                        synth_cid = f"__composite_{len(cluster_info)}"
                        cluster_info[synth_cid] = {
                            "kind": "roundedrect",
                            "geom": geom,
                            "fill": "#00000000",  # transparent
                            "label": label,
                            "tech": tech,
                            "note": note_text,
                            "stroke_color": stroke_color,
                            "stroke_width": stroke_width,
                            "adjust1": float(rect_el.get("rx", 10)),
                        }
                        all_geom[synth_cid] = {
                            "x": geom["x"], "y": geom["y"],
                            "w": geom["w"], "h": geom["h"],
                        }
                        continue

                    geom = {
                        "x": round(float(rect_el.get("x", 0)), 2),
                        "y": round(float(rect_el.get("y", 0)), 2),
                        "w": round(float(rect_el.get("width", 0)), 2),
                        "h": round(float(rect_el.get("height", 0)), 2),
                    }
                    fill = rect_el.get("fill", "#F1F1F1")
                    stroke_color, stroke_width = _extract_stroke(rect_el)

                    # Split texts by divider <line> y
                    div_y = float(line_el.get("y1", 0))
                    name_parts = []
                    desc_parts = []
                    for t in text_els:
                        ty = float(t.get("y", 0))
                        txt = (t.text or "").strip()
                        if not txt:
                            continue
                        if ty < div_y:
                            name_parts.append(txt)
                        else:
                            desc_parts.append(txt)

                    label = name_parts[0] if name_parts else ""
                    tech = (
                        " ".join(name_parts[1:])
                        if len(name_parts) > 1
                        else ""
                    )
                    note_text = "\n".join(desc_parts)

                    text_fmt = _extract_text_format(text_els)
                    unnamed_states.append({
                        "kind": "roundedrect",
                        "geom": geom,
                        "fill": fill,
                        "label": label,
                        "tech": tech,
                        "note": note_text,
                        "stroke_color": stroke_color,
                        "stroke_width": stroke_width,
                        "name_parts": name_parts,
                        **text_fmt,
                    })

        elif tag_local == "rect":
            # Bare <rect> at root level:
            #   fill="none" + rx>=10      → composite state container
            #   dark fill + rx=0 + thin   → fork/join bar pseudo-state
            #   light fill + rx=0 + small → pin or expansion pseudo-state
            fill_val = child.get("fill", "")
            rx_val = float(child.get("rx", 0))
            r_w = float(child.get("width", 0))
            r_h = float(child.get("height", 0))
            is_dark_fill = (fill_val.startswith("#") and fill_val.lower() not in (
                "#ffffff", "#f1f1f1", "#fafafa", "#none", ""))
            is_light_small = (not is_dark_fill and rx_val < 1
                              and r_h <= 15 and r_w <= 60
                              and fill_val.lower() not in ("none", ""))

            # Fork/join bar: dark fill, rx=0, very thin
            if (is_dark_fill and rx_val < 1
                    and (r_h <= 10 or r_w <= 10)):
                r_x = round(float(child.get("x", 0)), 2)
                r_y = round(float(child.get("y", 0)), 2)
                stroke_color, stroke_width = _extract_stroke(child)
                # Determine fork vs join from ANTLR (will be enriched later)
                unnamed_states.append({
                    "kind": "rect",
                    "geom": {
                        "x": r_x, "y": r_y,
                        "w": round(r_w, 2), "h": round(r_h, 2),
                    },
                    "fill": fill_val,
                    "label": "[fork/join]",
                    "tech": "",
                    "note": "",
                    "stroke_color": stroke_color or fill_val,
                    "stroke_width": stroke_width or 1,
                    "name_parts": ["[fork/join]"],
                })

            elif is_light_small:
                # Pin (12x12) or expansion (48x12) pseudo-state
                r_x = round(float(child.get("x", 0)), 2)
                r_y = round(float(child.get("y", 0)), 2)
                stroke_color, stroke_width = _extract_stroke(child)
                # Expansion: wider rectangle; Pin: square
                is_expansion = r_w > 20
                label = "[expansion]" if is_expansion else "[pin]"
                unnamed_states.append({
                    "kind": "rect",
                    "geom": {
                        "x": r_x, "y": r_y,
                        "w": round(r_w, 2), "h": round(r_h, 2),
                    },
                    "fill": fill_val,
                    "label": label,
                    "tech": "",
                    "note": "",
                    "stroke_color": stroke_color or "#222222",
                    "stroke_width": stroke_width or 1,
                    "name_parts": [label],
                })

            elif fill_val.lower() in ("none", ""):
                rx_val = float(child.get("rx", 0))
                if rx_val >= 10:
                    x = round(float(child.get("x", 0)), 2)
                    y = round(float(child.get("y", 0)), 2)
                    w = round(float(child.get("width", 0)), 2)
                    h = round(float(child.get("height", 0)), 2)
                    stroke_color, stroke_width = _extract_stroke(child)
                    # Find associated text elements (inside the rect bbox)
                    name_parts = []
                    desc_parts = []
                    # Find the divider line (first <line> inside the bbox)
                    div_y = y + 9999
                    for sib in root_g:
                        stag = sib.tag.split("}")[-1] if "}" in sib.tag else sib.tag
                        if stag == "line":
                            lx1 = float(sib.get("x1", 0))
                            ly1 = float(sib.get("y1", 0))
                            lx2 = float(sib.get("x2", 0))
                            if (abs(lx1 - x) < 2 and abs(lx2 - (x + w)) < 2
                                    and y < ly1 < y + h):
                                div_y = ly1
                                break
                    for sib in root_g:
                        stag = sib.tag.split("}")[-1] if "}" in sib.tag else sib.tag
                        if stag == "text":
                            tx = float(sib.get("x", 0))
                            ty = float(sib.get("y", 0))
                            txt = (sib.text or "").strip()
                            if txt and x <= tx <= x + w and y <= ty <= y + h:
                                if ty < div_y:
                                    name_parts.append(txt)
                                else:
                                    desc_parts.append(txt)
                    label = name_parts[0] if name_parts else ""
                    tech = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
                    note_text = "\n".join(desc_parts)
                    label, tech, note_text = _dedup_label_tech_note(label, tech, note_text)
                    # Extract text formatting from sibling <text> elements
                    sib_texts = [
                        s for s in root_g
                        if (s.tag.split("}")[-1] if "}" in s.tag else s.tag) == "text"
                        and x <= float(s.get("x", 0)) <= x + w
                        and y <= float(s.get("y", 0)) <= y + h
                    ]
                    text_fmt = _extract_text_format(sib_texts)
                    synth_cid = f"__composite_{len(cluster_info)}"
                    cluster_info[synth_cid] = {
                        "kind": "roundedrect",
                        "geom": {"x": x, "y": y, "w": w, "h": h},
                        "fill": "#00000000",
                        "label": label,
                        "tech": tech,
                        "note": note_text,
                        "stroke_color": stroke_color,
                        "stroke_width": stroke_width,
                        "adjust1": rx_val,
                        **text_fmt,
                    }
                    all_geom[synth_cid] = {"x": x, "y": y, "w": w, "h": h}

        elif tag_local == "ellipse":
            # Bare ellipse — [*] pseudo-state or entry/exit point
            # Skip if a start_entity at same position was already found
            rx = float(child.get("rx", 0))
            ry = float(child.get("ry", 0))
            if rx <= 12 and ry <= 12:
                cx = float(child.get("cx", 0))
                cy = float(child.get("cy", 0))
                dup = any(
                    abs(e["geom"]["x"] - (cx - rx)) < 1
                    and abs(e["geom"]["y"] - (cy - ry)) < 1
                    for e in initial_ellipses
                )
                if dup:
                    continue
                fill = child.get("fill", "#222222")
                is_dark = fill.lower() in ("#222222", "#000000", "#181818")
                geom = {
                    "x": round(cx - rx, 2),
                    "y": round(cy - ry, 2),
                    "w": round(rx * 2, 2),
                    "h": round(ry * 2, 2),
                }

                if is_dark and rx >= 8:
                    # Dark, large: [*] start pseudo-state
                    initial_ellipses.append({
                        "kind": "ellipse",
                        "geom": geom,
                        "fill": fill,
                    })
                elif not is_dark and rx <= 8:
                    # Light, small: <<entryPoint>> or <<exitPoint>>
                    unnamed_states.append({
                        "kind": "ellipse",
                        "geom": geom,
                        "fill": fill,
                        "label": "[point]",
                        "tech": "",
                        "note": "",
                        "stroke_color": "#222222",
                        "stroke_width": 1,
                        "name_parts": ["[point]"],
                    })
                else:
                    # Other: treat as [*]
                    initial_ellipses.append({
                        "kind": "ellipse",
                        "geom": geom,
                        "fill": fill,
                    })

    if not unnamed_states and not cluster_info and not note_info:
        return empty

    # ── Pass 2: entity-ID mapping for unnamed states ──
    # Extract ent_id → alias set from link path id attributes
    ent_id_aliases: Dict[str, set] = defaultdict(set)
    for link in link_list:
        path_id = link.get("path_id", "")
        if not path_id:
            continue
        # Strip -N suffix for duplicate links (e.g. "LOCKOUT-to-RESET-1")
        cleaned = re.sub(r"-(\d+)$", "", path_id)
        m = re.match(r"^(.+?)-to-(.+)$", cleaned)
        if m:
            ent_id_aliases[link["src_id"]].add(m.group(1))
            ent_id_aliases[link["dst_id"]].add(m.group(2))

    # Pick a preferred alias per ent_id (skip *start* and GMN* names)
    ent_id_to_alias: Dict[str, str] = {}
    for ent_id, aliases in ent_id_aliases.items():
        real = {
            a for a in aliases
            if not a.startswith("*") and not a.startswith("GMN")
        }
        if real:
            ent_id_to_alias[ent_id] = sorted(real)[0]

    alias_to_ent_id = {v: k for k, v in ent_id_to_alias.items()}

    # Match aliases to unnamed states by label
    state_to_ent_id: Dict[int, str] = {}
    matched_ent_ids: set = set()

    # Pre-populate for entity-based states that already have an ent_id
    for idx, state in enumerate(unnamed_states):
        eid = state.get("ent_id", "")
        if eid:
            state_to_ent_id[idx] = eid
            matched_ent_ids.add(eid)

    unmatched_ent_ids = (
        set(ent_id_to_alias.keys()) - set(cluster_info.keys())
        - matched_ent_ids
    )

    for idx, state in enumerate(unnamed_states):
        if idx in state_to_ent_id:
            continue  # Already mapped by ent_id
        parts = state.get("name_parts", [])
        full_name = " ".join(parts)

        # Candidate alias forms
        candidates: List[str] = []
        # Form 1: full name before '(', spaces → underscores
        candidates.append(
            full_name.split("(")[0].strip().replace(" ", "_"),
        )
        # Form 2: first word
        if parts:
            candidates.append(parts[0])

        for candidate in candidates:
            if (
                candidate in alias_to_ent_id
                and alias_to_ent_id[candidate] in unmatched_ent_ids
                and alias_to_ent_id[candidate] not in matched_ent_ids
            ):
                eid = alias_to_ent_id[candidate]
                state_to_ent_id[idx] = eid
                matched_ent_ids.add(eid)
                break

    # Elimination fallback for remaining unmatched states
    unmatched_states = [
        i for i in range(len(unnamed_states)) if i not in state_to_ent_id
    ]
    remaining_ent_ids = sorted(unmatched_ent_ids - matched_ent_ids)
    for i, sid in enumerate(unmatched_states):
        if i < len(remaining_ent_ids):
            state_to_ent_id[sid] = remaining_ent_ids[i]

    # Populate all_geom: states and clusters override notes
    for idx, ent_id in state_to_ent_id.items():
        sg = unnamed_states[idx]["geom"]
        all_geom[ent_id] = {
            "x": sg["x"], "y": sg["y"],
            "w": sg["w"], "h": sg["h"],
        }
    for ent_id, data in cluster_info.items():
        cg = data["geom"]
        all_geom[ent_id] = {
            "x": cg["x"], "y": cg["y"],
            "w": cg["w"], "h": cg["h"],
        }

    # ── Pass 3: parent map via geometric containment ──
    parent_map: Dict[str, str] = {}
    for idx, ent_id in state_to_ent_id.items():
        sg = unnamed_states[idx]["geom"]
        sx, sy = sg["x"], sg["y"]
        sx2, sy2 = sx + sg["w"], sy + sg["h"]

        for cluster_eid, cdata in cluster_info.items():
            cg = cdata["geom"]
            cx, cy = cg["x"], cg["y"]
            cx2, cy2 = cx + cg["w"], cy + cg["h"]

            if sx >= cx and sy >= cy and sx2 <= cx2 and sy2 <= cy2:
                parent_map[ent_id] = cluster_eid
                break

    # ── Build individual annotations ─────────────────
    counter = 1
    id_to_ann: Dict[str, Dict[str, Any]] = {}

    # Title
    title_ann: Optional[Dict[str, Any]] = None
    if title_info:
        ann_id = f"p{counter:06d}"
        counter += 1
        title_ann = {
            "id": ann_id,
            "kind": "text",
            "geom": dict(title_info["geom"]),
            "meta": {
                "label": title_info["text"],
                "tech": "", "note": title_info["text"],
            },
            "style": {
                "pen": {"color": "#555555", "width": 2, "dash": "solid"},
                "fill": {"color": "#00000000"},
                "text": {"color": "#000000", "size_pt": 12.0},
            },
        }

    # Initial [*] and final [*] ellipses (start_entity / end_entity)
    ellipse_anns: List[Dict[str, Any]] = []
    # Map from SVG ent_id → synthetic id for start/end entities
    start_id_remap: Dict[str, str] = {}
    for ell in initial_ellipses:
        ann_id = f"p{counter:06d}"
        counter += 1
        is_end = ell.get("is_end", False)
        ann = {
            "id": ann_id,
            "kind": "ellipse",
            "geom": dict(ell["geom"]),
            "meta": {
                "label": "[*]",
                "tech": "end" if is_end else "start",
                "note": "",
            },
            "style": {
                "pen": {
                    "color": "#222222",
                    "width": 8 if is_end else 1,
                    "dash": "solid",
                },
                "fill": {"color": _safe_fill(ell["fill"])},
                "text": {"color": "#FFFFFF", "size_pt": 8.0},
            },
        }
        ellipse_anns.append(ann)
        synth_id = ell.get("ent_id", "")
        svg_ent_id = ell.get("svg_ent_id", "")
        if synth_id:
            id_to_ann[synth_id] = ann
        # Remap links that reference the SVG ent_id to the synthetic id
        if svg_ent_id and synth_id != svg_ent_id:
            start_id_remap[svg_ent_id] = synth_id

    # Unnamed states
    orphan_anns: List[Dict[str, Any]] = []  # states without ent_id (pins, etc.)
    for idx, state in enumerate(unnamed_states):
        ann_id = f"p{counter:06d}"
        counter += 1
        ent_id = state_to_ent_id.get(idx)

        meta_dict: Dict[str, Any] = {
            "label": state["label"],
            "tech": state["tech"],
            "note": state["note"] or state["label"],
        }
        # Carry text formatting from SVG
        for fk in ("text_color", "text_size", "text_family"):
            if fk in state:
                meta_dict[fk] = state[fk]

        ann: Dict[str, Any] = {
            "id": ann_id,
            "kind": state["kind"],
            "geom": dict(state["geom"]),
            "meta": meta_dict,
            "style": {
                "pen": {
                    "color": state["stroke_color"],
                    "width": state["stroke_width"],
                    "dash": "solid",
                },
                "fill": {"color": _safe_fill(state["fill"])},
            },
        }
        if ent_id:
            id_to_ann[ent_id] = ann
        else:
            orphan_anns.append(ann)

    # Notes (separate from id_to_ann to avoid ent_id collisions)
    note_anns: List[Dict[str, Any]] = []
    for ent_id, data in note_info.items():
        ann_id = f"p{counter:06d}"
        counter += 1
        note_meta: Dict[str, Any] = {
            "label": data["label"],
            "tech": data["tech"],
            "note": data["note"] or data["label"],
        }
        for fk in ("text_color", "text_size", "text_family"):
            if fk in data:
                note_meta[fk] = data[fk]
        note_anns.append({
            "id": ann_id,
            "kind": data["kind"],
            "geom": dict(data["geom"]),
            "meta": note_meta,
            "style": {
                "pen": {
                    "color": data["stroke_color"],
                    "width": data["stroke_width"],
                    "dash": "solid",
                },
                "fill": {"color": _safe_fill(data["fill"])},
            },
        })

    # Clusters (including composite state containers)
    for ent_id, data in cluster_info.items():
        ann_id = f"p{counter:06d}"
        counter += 1
        geom_copy = dict(data["geom"])
        if "adjust1" in data:
            geom_copy["adjust1"] = data["adjust1"]
        cluster_meta: Dict[str, Any] = {
            "label": data["label"],
            "tech": data["tech"],
            "note": data["note"] or data["label"],
        }
        for fk in ("text_color", "text_size", "text_family"):
            if fk in data:
                cluster_meta[fk] = data[fk]
        ann = {
            "id": ann_id,
            "kind": data["kind"],
            "geom": geom_copy,
            "meta": cluster_meta,
            "style": {
                "pen": {
                    "color": data["stroke_color"],
                    "width": data["stroke_width"],
                    "dash": "solid",
                },
                "fill": {"color": _safe_fill(data["fill"])},
            },
        }
        id_to_ann[ent_id] = ann

    # ── Group assembly (bottom-up) ───────────────────
    children_map: Dict[str, List[str]] = defaultdict(list)
    for child_id, parent_id in parent_map.items():
        if child_id in id_to_ann and parent_id in id_to_ann:
            children_map[parent_id].append(child_id)

    def _depth(ent_id: str) -> int:
        d = 0
        cur = ent_id
        while cur in parent_map:
            d += 1
            cur = parent_map[cur]
        return d

    grouped_ids: set = set()
    group_parents = sorted(
        [eid for eid in cluster_info if eid in children_map],
        key=_depth,
        reverse=True,
    )

    for parent_id in group_parents:
        child_ids = children_map[parent_id]
        if not child_ids:
            continue

        child_anns = [
            id_to_ann[cid] for cid in child_ids if cid in id_to_ann
        ]
        child_anns.sort(key=_child_y)

        parent_ann = id_to_ann[parent_id]
        group_id = "g" + parent_ann["id"][1:]
        group_ann: Dict[str, Any] = {
            "id": group_id,
            "kind": "group",
            "children": [parent_ann] + child_anns,
            "meta": {
                "label": parent_ann["meta"]["label"],
                "tech": parent_ann["meta"].get("tech", ""),
                "note": parent_ann["meta"].get("note", ""),
            },
            "style": parent_ann["style"],
        }
        id_to_ann[parent_id] = group_ann
        grouped_ids.update(child_ids)

    # ── Connector annotations ────────────────────────
    # Remap start entity IDs in links to synthetic IDs
    for link in link_list:
        if link["src_id"] in start_id_remap:
            link["src_id"] = start_id_remap[link["src_id"]]
        if link["dst_id"] in start_id_remap:
            link["dst_id"] = start_id_remap[link["dst_id"]]

    line_anns: List[Dict[str, Any]] = []
    for link in link_list:
        pen_color = "#808080"
        dashed = False
        style_str = link["style"]
        stroke_m = re.search(r'stroke:\s*(#[0-9A-Fa-f]{3,8})', style_str)
        if stroke_m:
            pen_color = stroke_m.group(1)
        if "stroke-dasharray" in style_str:
            dashed = True
        width_m = re.search(
            r'stroke-width:\s*(\d+(?:\.\d+)?)', style_str,
        )
        pen_width = int(float(width_m.group(1))) if width_m else 2

        # Use detected arrow mode (handles reverse, bidirectional, association)
        arrow_mode = link.get("arrow_mode", "end" if link.get("has_arrowhead") else "none")
        if link.get("link_type") == "association":
            dashed = True
            arrow_mode = "none"

        # Build meta with text formatting from link's <text> elements
        link_meta: Dict[str, Any] = {
            "label": link["label"],
            "tech": "", "note": link["label"],
        }
        link_meta.update(link.get("text_fmt", {}))

        # Try emitting a curve from the SVG path geometry
        d_attr = link.get("path_d", "")
        has_curves = (
            bool(re.search(r"[CcSsQqTt]", d_attr)) if d_attr else False
        )

        if has_curves:
            curve_nodes, (bx, by, bw, bh) = _parse_path_to_curve_nodes(
                d_attr,
            )
            if curve_nodes and bw > 0 and bh > 0:
                ann_id = f"p{counter:06d}"
                counter += 1
                line_anns.append({
                    "id": ann_id,
                    "kind": "curve",
                    "geom": {
                        "x": bx, "y": by, "w": bw, "h": bh,
                        "nodes": curve_nodes,
                    },
                    "meta": link_meta,
                    "style": _make_line_style(
                        pen_color, pen_width,
                        dashed=dashed, arrow=arrow_mode,
                    ),
                })
                continue

        # Degenerate curve (vertical/horizontal line) or straight path:
        # extract endpoints directly from path d attribute
        if d_attr:
            coords = re.findall(
                r'[-+]?\d*\.?\d+', d_attr,
            )
            if len(coords) >= 4:
                all_x = [float(coords[i]) for i in range(0, len(coords), 2)]
                all_y = [float(coords[i]) for i in range(1, len(coords), 2)]
                x1 = round(all_x[0], 2)
                y1 = round(all_y[0], 2)
                x2 = round(all_x[-1], 2)
                y2 = round(all_y[-1], 2)

                ann_id = f"p{counter:06d}"
                counter += 1
                line_anns.append({
                    "id": ann_id,
                    "kind": "line",
                    "geom": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                    "meta": dict(link_meta),
                    "style": _make_line_style(
                        pen_color, pen_width,
                        dashed=dashed, arrow=arrow_mode,
                    ),
                })
                continue

        # Fallback: center-to-center line from geom lookup
        src_geom = all_geom.get(link["src_id"])
        dst_geom = all_geom.get(link["dst_id"])
        if not src_geom or not dst_geom:
            continue

        x1 = round(src_geom["x"] + src_geom["w"] / 2, 2)
        y1 = round(src_geom["y"] + src_geom["h"] / 2, 2)
        x2 = round(dst_geom["x"] + dst_geom["w"] / 2, 2)
        y2 = round(dst_geom["y"] + dst_geom["h"] / 2, 2)

        ann_id = f"p{counter:06d}"
        counter += 1
        line_anns.append({
            "id": ann_id,
            "kind": "line",
            "geom": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
            "meta": dict(link_meta),
            "style": _make_line_style(
                pen_color, pen_width,
                dashed=dashed, arrow=arrow_mode,
            ),
        })

    # ── Collect top-level annotations ────────────────
    top_level: List[Dict[str, Any]] = []
    if title_ann:
        top_level.append(title_ann)
    top_level.extend(ellipse_anns)

    # States and clusters not consumed as group children
    # (ellipses already added via ellipse_anns — skip their synthetic IDs)
    ellipse_ids = {e.get("ent_id", "") for e in initial_ellipses}
    seen_ids: set = set()
    for ent_id in id_to_ann:
        if ent_id in grouped_ids or ent_id in seen_ids or ent_id in ellipse_ids:
            continue
        seen_ids.add(ent_id)
        top_level.append(id_to_ann[ent_id])

    # Orphan states (no ent_id — pins, expansions, etc.)
    top_level.extend(orphan_anns)
    # Notes (always top-level)
    top_level.extend(note_anns)
    top_level.extend(line_anns)

    # Sort by Y coordinate (title stays first)
    if title_ann and len(top_level) > 1:
        rest = top_level[1:]
        rest.sort(key=_child_y)
        top_level = [title_ann] + rest
    else:
        top_level.sort(key=_child_y)

    _normalize_annotations(top_level)

    # ── Enrich with ANTLR state source semantics ──
    if puml_text:
        src_info = _parse_state_source(puml_text)
        if src_info:
            _merge_state_source_info(top_level, src_info)

    return {
        "version": "draft-1",
        "image": {"width": canvas_w, "height": canvas_h},
        "annotations": top_level,
    }


# ───────────────────────────────────────────────
# Auto-layout
# ───────────────────────────────────────────────

def _auto_layout(
    elements: List[Dict[str, Any]],
    connections: List[Dict[str, Any]],
    canvas_w: int,
    canvas_h: int,
) -> Dict[str, Dict[str, float]]:
    """Compute grid positions for elements using topological layering.

    Elements with no incoming connections go in column 0; each subsequent
    layer increments the column. Within a column, elements are distributed
    vertically.

    Args:
        elements: Parsed element dicts (must have "alias" key).
        connections: Parsed connection dicts (must have "src"/"dst").
        canvas_w: Canvas width in pixels.
        canvas_h: Canvas height in pixels.

    Returns:
        Dict mapping alias → {"x": float, "y": float, "w": float, "h": float}.
    """
    if not elements:
        return {}

    aliases = [e["alias"] for e in elements]
    alias_set = set(aliases)

    # Build adjacency + in-degree
    in_degree: Dict[str, int] = {a: 0 for a in aliases}
    adj: Dict[str, List[str]] = {a: [] for a in aliases}

    for c in connections:
        src, dst = c["src"], c["dst"]
        if src in alias_set and dst in alias_set:
            adj[src].append(dst)
            in_degree[dst] = in_degree.get(dst, 0) + 1

    # Topological layering (Kahn's algorithm variant)
    layers: List[List[str]] = []
    queue = deque([a for a in aliases if in_degree[a] == 0])

    # If everything has incoming edges (cycle), just start with all
    if not queue:
        queue = deque(aliases)

    visited: set = set()
    while queue:
        layer = []
        next_queue: List[str] = []
        for a in queue:
            if a in visited:
                continue
            visited.add(a)
            layer.append(a)
        if layer:
            layers.append(layer)
        for a in layer:
            for nb in adj[a]:
                if nb not in visited:
                    in_degree[nb] -= 1
                    if in_degree[nb] <= 0:
                        next_queue.append(nb)
        queue = deque(next_queue)

    # Add any remaining (disconnected) elements
    remaining = [a for a in aliases if a not in visited]
    if remaining:
        layers.append(remaining)

    # Compute positions
    shape_w = 160.0
    shape_h = 80.0
    pad_x = 40.0
    pad_y = 40.0

    num_cols = max(len(layers), 1)
    cell_w = (canvas_w - pad_x) / num_cols

    # Clamp shape size if cells are too small
    if cell_w < shape_w + pad_x:
        shape_w = max(cell_w - pad_x, 80)

    positions: Dict[str, Dict[str, float]] = {}

    for col_idx, layer in enumerate(layers):
        num_rows = len(layer)
        cell_h = (canvas_h - pad_y) / max(num_rows, 1)

        if cell_h < shape_h + pad_y:
            shape_h_local = max(cell_h - pad_y, 50)
        else:
            shape_h_local = shape_h

        for row_idx, alias in enumerate(layer):
            cx = pad_x + col_idx * cell_w + cell_w / 2
            cy = pad_y + row_idx * cell_h + cell_h / 2
            positions[alias] = {
                "x": round(cx - shape_w / 2, 2),
                "y": round(cy - shape_h_local / 2, 2),
                "w": round(shape_w, 2),
                "h": round(shape_h_local, 2),
            }

    return positions


# ───────────────────────────────────────────────
# Annotation builder
# ───────────────────────────────────────────────

def _build_element_annotation(
    elem: Dict[str, Any],
    pos: Dict[str, Any],
    ann_id: str,
) -> Dict[str, Any]:
    """Build a single shape annotation from a parsed element and position.

    Args:
        elem: Parsed element dict.
        pos: Position dict with x, y, w, h (and optional points).
        ann_id: Annotation ID string.

    Returns:
        Annotation dict.
    """
    kind = _KIND_MAP.get(elem["puml_type"], "rect")
    label = elem["label"]
    tech = elem.get("tech", "")
    note = elem.get("note", "")

    text_parts = [label]
    if tech:
        text_parts.append(f"[{tech}]")
    text = " ".join(text_parts)

    color = elem.get("color")
    style: Dict[str, Any] = {
        "pen": {"color": "#555555", "width": 2, "dash": "solid"},
        "fill": {"color": "#00000000"},
        "text": {"color": "#000000", "size_pt": 12.0},
    }
    if color:
        style["fill"]["color"] = _normalize_color(color)

    ann: Dict[str, Any] = {
        "id": ann_id,
        "kind": kind,
        "meta": dict(zip(("label", "tech", "note"),
                         _dedup_label_tech_note(label, tech, note or text))),
        "style": style,
    }

    if kind == "cylinder":
        ann["geom"] = {
            "x": pos["x"], "y": pos["y"],
            "w": pos["w"], "h": pos["h"],
            "adjust1": 0.2,
        }
    elif kind == "polygon":
        geom: Dict[str, Any] = {
            "x": pos["x"], "y": pos["y"],
            "w": pos["w"], "h": pos["h"],
        }
        if "points" in pos:
            geom["points"] = pos["points"]
        ann["geom"] = geom
    else:
        ann["geom"] = {
            "x": pos["x"], "y": pos["y"],
            "w": pos["w"], "h": pos["h"],
        }

    return ann


def _build_annotations(
    elements: List[Dict[str, Any]],
    connections: List[Dict[str, Any]],
    positions: Dict[str, Dict[str, float]],
    parent_map: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """Build PictoSync annotation records from parsed elements and connections.

    When *parent_map* is provided (from SVG parsing), clusters that contain
    children are emitted as ``kind: "group"`` annotations with nested
    ``children`` lists.

    Args:
        elements: Parsed element dicts.
        connections: Parsed connection dicts.
        positions: Layout positions from _auto_layout or SVG.
        parent_map: Optional mapping of child_alias → parent_alias from SVG.

    Returns:
        List of annotation dicts ready for PictoSync JSON.
    """
    # Phase 1: build individual annotations keyed by alias
    alias_to_ann: Dict[str, Dict[str, Any]] = {}
    alias_to_elem: Dict[str, Dict[str, Any]] = {}
    counter = 1

    for elem in elements:
        alias = elem["alias"]
        pos = positions.get(alias)
        if pos is None:
            continue

        ann_id = f"p{counter:06d}"
        counter += 1

        ann = _build_element_annotation(elem, pos, ann_id)
        alias_to_ann[alias] = ann
        alias_to_elem[alias] = elem

    # Phase 2: assemble groups if parent_map is provided
    grouped_aliases: set = set()

    if parent_map:
        # Invert: parent -> [child1, child2, ...] (only children in alias_to_ann)
        children_map: Dict[str, List[str]] = defaultdict(list)
        for child, parent in parent_map.items():
            if child in alias_to_ann and parent in alias_to_ann:
                children_map[parent].append(child)

        # Compute depth of each potential group parent for bottom-up assembly
        # depth = how many ancestor hops until root (no parent)
        def _depth(alias: str) -> int:
            d = 0
            cur = alias
            while cur in parent_map:
                d += 1
                cur = parent_map[cur]
            return d

        # Sort parents deepest-first so nested groups are built before outer
        parents_by_depth = sorted(children_map.keys(), key=_depth, reverse=True)

        for parent_alias in parents_by_depth:
            child_aliases = children_map[parent_alias]
            if not child_aliases:
                continue

            # Collect child annotations (may be sub-groups already replaced)
            child_anns = [alias_to_ann[ca] for ca in child_aliases]

            # Build group annotation from the parent cluster.
            # The cluster's own rect annotation (with geom, fill, text)
            # is kept as the first child so its visual boundary appears
            # on the canvas.
            parent_ann = alias_to_ann[parent_alias]
            group_id = "g" + parent_ann["id"][1:]
            group_ann: Dict[str, Any] = {
                "id": group_id,
                "kind": "group",
                "children": [parent_ann] + child_anns,
                "meta": {
                    "label": parent_ann["meta"]["label"],
                    "tech": parent_ann["meta"].get("tech", ""),
                    "note": parent_ann["meta"].get("note", ""),
                },
                "style": parent_ann["style"],
            }

            # Replace parent entry with the group
            alias_to_ann[parent_alias] = group_ann
            grouped_aliases.update(child_aliases)

    # Phase 3: collect top-level annotations (not consumed as children)
    annotations: List[Dict[str, Any]] = []
    for elem in elements:
        alias = elem["alias"]
        if alias in grouped_aliases:
            continue
        ann = alias_to_ann.get(alias)
        if ann:
            annotations.append(ann)

    # Build connector annotations (curve when SVG path available, line fallback)
    for conn in connections:
        label = conn.get("label", "")
        dashed = conn.get("dashed", False)
        color = conn.get("color")
        pen_color = _normalize_color(color) if color else "#808080"

        # Try emitting a curve from the SVG path geometry
        d_attr = conn.get("path_d", "")
        has_curves = bool(re.search(r"[CcSsQqTt]", d_attr)) if d_attr else False

        if has_curves:
            curve_nodes, (bx, by, bw, bh) = _parse_path_to_curve_nodes(d_attr)
            if curve_nodes and bw > 0 and bh > 0:
                arrow = conn.get("arrow_mode", "end" if conn.get("has_arrowhead") else "none")
                ann_id = f"p{counter:06d}"
                counter += 1
                annotations.append({
                    "id": ann_id,
                    "kind": "curve",
                    "geom": {
                        "x": bx, "y": by, "w": bw, "h": bh,
                        "nodes": curve_nodes,
                    },
                    "meta": {
                        "label": label,
                        "tech": "",
                        "note": label,
                    },
                    "style": _make_line_style(
                        pen_color, 2, dashed=dashed, arrow=arrow,
                    ),
                })
                continue

        # Fallback: center-to-center line
        src_pos = positions.get(conn["src"])
        dst_pos = positions.get(conn["dst"])
        if not src_pos or not dst_pos:
            continue

        ann_id = f"p{counter:06d}"
        counter += 1

        x1 = round(src_pos["x"] + src_pos["w"] / 2, 2)
        y1 = round(src_pos["y"] + src_pos["h"] / 2, 2)
        x2 = round(dst_pos["x"] + dst_pos["w"] / 2, 2)
        y2 = round(dst_pos["y"] + dst_pos["h"] / 2, 2)

        annotations.append({
            "id": ann_id,
            "kind": "line",
            "geom": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
            "meta": {
                "label": label,
                "tech": "",
                "note": label,
            },
            "style": _make_line_style(pen_color, 2, dashed=dashed),
        })

    return annotations


# ───────────────────────────────────────────────
# Public API
# ───────────────────────────────────────────────

def parse_puml_to_annotations(
    puml_text: str,
    canvas_w: int = 1200,
    canvas_h: int = 800,
    svg_path: str | None = None,
) -> Dict[str, Any]:
    """Parse PlantUML text and produce PictoSync JSON annotation data.

    When *svg_path* is provided the element positions, fill colours and
    link styles are read from the rendered SVG for pixel-accurate
    alignment with the PNG background.  When it is ``None`` the
    auto-layout grid is used as a fallback.

    Args:
        puml_text: The raw PlantUML source text.
        canvas_w: Canvas width in pixels for layout.
        canvas_h: Canvas height in pixels for layout.
        svg_path: Optional path to a PlantUML-rendered SVG file.

    Returns:
        Dict with PictoSync schema: {"version", "image", "annotations"}.
    """
    # Activity diagrams have a completely different SVG structure
    # (flat shapes, no <g class="entity/cluster"> groups).
    if svg_path:
        tree = ET.parse(svg_path)
        if tree.getroot().get("data-diagram-type") == "ACTIVITY":
            return _parse_activity_diagram_svg(tree, puml_text)
        if tree.getroot().get("data-diagram-type") == "SEQUENCE":
            return _parse_sequence_diagram_svg(tree)
        if tree.getroot().get("data-diagram-type") in ("DESCRIPTION", "CLASS"):
            return _parse_description_diagram_svg(tree, puml_text)
        if tree.getroot().get("data-diagram-type") == "STATE":
            return _parse_state_diagram_svg(tree, puml_text)

    elements = _extract_elements(puml_text)
    known_aliases = {e["alias"] for e in elements}
    connections = _extract_connections(puml_text, known_aliases)

    if svg_path:
        svg_data = _parse_svg_positions(svg_path)

        # Use SVG viewBox dimensions
        canvas_w = svg_data["canvas_w"]
        canvas_h = svg_data["canvas_h"]

        # Build positions from SVG, matched by alias
        positions: Dict[str, Dict[str, float]] = {}
        for alias, pos in svg_data["positions"].items():
            positions[alias] = pos
        if svg_data.get("title_pos"):
            positions["__title__"] = svg_data["title_pos"]

        # Override element fill colours from SVG
        for elem in elements:
            svg_elem = svg_data["elements"].get(elem["alias"])
            if svg_elem and svg_elem.get("fill"):
                elem["color"] = svg_elem["fill"]

        # Merge SVG link styles into text-parsed connections
        text_conn_keys = {(c["src"], c["dst"]) for c in connections}
        svg_link_map: Dict[Tuple[str, str], Dict[str, Any]] = {}
        for lnk in svg_data["links"]:
            svg_link_map[(lnk["src"], lnk["dst"])] = lnk

        for conn in connections:
            key = (conn["src"], conn["dst"])
            svg_link = svg_link_map.get(key)
            if svg_link:
                _apply_svg_link_style(conn, svg_link["style"])
                conn["path_d"] = svg_link.get("path_d", "")
                conn["has_arrowhead"] = svg_link.get("has_arrowhead", False)
                conn["arrow_mode"] = svg_link.get("arrow_mode", "end" if conn["has_arrowhead"] else "none")

        # Add SVG-only links not found by the text regex
        for key, svg_link in svg_link_map.items():
            if key not in text_conn_keys:
                conn: Dict[str, Any] = {
                    "src": svg_link["src"],
                    "dst": svg_link["dst"],
                    "label": svg_link.get("label", ""),
                    "dashed": False,
                    "color": None,
                    "path_d": svg_link.get("path_d", ""),
                    "has_arrowhead": svg_link.get("has_arrowhead", False),
                    "arrow_mode": svg_link.get("arrow_mode", "end"),
                }
                _apply_svg_link_style(conn, svg_link["style"])
                connections.append(conn)
    else:
        positions = _auto_layout(elements, connections, canvas_w, canvas_h)

    parent_map = svg_data.get("parent_map") if svg_path else None
    annotations = _build_annotations(elements, connections, positions, parent_map)

    _normalize_annotations(annotations)
    return {
        "version": "draft-1",
        "image": {
            "width": canvas_w,
            "height": canvas_h,
        },
        "annotations": annotations,
    }
