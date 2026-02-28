"""
mermaid/parser.py

Parse pre-rendered Mermaid SVG files into PictoSync annotation JSON.

Supports all 21 Mermaid diagram types via a dispatch table that maps
``aria-roledescription`` values to per-type parser functions.
"""

from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple

from models import resolve_kind_alias
from plantuml.parser import (
    _path_bbox,
    _parse_path_to_curve_nodes,
    _make_line_style,
    _normalize_annotations,
    _SVG_NS,
)


# XHTML namespace used inside <foreignObject> elements
_XHTML_NS = "http://www.w3.org/1999/xhtml"

# Mermaid diagram types we recognise via aria-roledescription
_SUPPORTED_DIAGRAM_TYPES = {
    "flowchart-v2", "flowchart",
    "stateDiagram", "class", "er", "requirement", "mindmap",
    "block", "sankey", "kanban", "architecture", "c4",
    "sequence", "gantt", "packet", "timeline", "pie",
    "xychart", "quadrantChart", "gitGraph", "journey", "zenuml",
}

# Fallback class-name heuristics for detection (class -> inferred type)
_CLASS_HEURISTICS: Dict[str, str] = {
    "nodes": "flowchart-v2",
    "architecture-services": "architecture",
    "pieCircle": "pie",
    "commit-bullets": "gitGraph",
    "journey-section": "journey",
    "packetBlock": "packet",
}


# ─────────────────────────────────────────────────────────
# Annotation ID counter (module-level helper)
# ─────────────────────────────────────────────────────────

def _make_id_gen() -> Any:
    """Return a callable that produces sequential IDs ``m000001, m000002, ...``."""
    counter = 0

    def _next_id() -> str:
        nonlocal counter
        counter += 1
        return f"m{counter:06d}"

    return _next_id


# ─────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────


def detect_mermaid_svg(svg_path: str) -> Optional[str]:
    """Check whether an SVG file is a Mermaid-rendered diagram.

    Args:
        svg_path: Path to the SVG file.

    Returns:
        The diagram type string (e.g. ``"flowchart-v2"``) if detected,
        or ``None`` if the SVG is not recognised as Mermaid output.
    """
    try:
        tree = ET.parse(svg_path)
    except ET.ParseError:
        return None

    root = tree.getroot()
    ns = _SVG_NS

    # Primary: aria-roledescription on root <svg>
    role = root.get("aria-roledescription", "")
    if role in _SUPPORTED_DIAGRAM_TYPES:
        return role

    # Fallback: look for Mermaid-specific class names on child groups
    for g in root.iter(f"{{{ns}}}g"):
        cls = g.get("class", "")
        for token in cls.split():
            if token in _CLASS_HEURISTICS:
                return _CLASS_HEURISTICS[token]

    # Fallback: class on rect/path elements
    for el in root.iter():
        cls = el.get("class", "")
        for token in cls.split():
            if token in _CLASS_HEURISTICS:
                return _CLASS_HEURISTICS[token]

    return None


def parse_mermaid_svg_to_annotations(svg_path: str) -> Dict[str, Any]:
    """Parse a Mermaid-rendered SVG file into PictoSync annotation JSON.

    Args:
        svg_path: Path to the ``.svg`` file.

    Returns:
        Annotation dict with ``version``, ``image``, and ``annotations`` keys.
    """
    tree = ET.parse(svg_path)
    root = tree.getroot()
    ns = _SVG_NS

    # ── Canvas dimensions from viewBox ──
    viewbox = root.get("viewBox", "").split()
    vb_x = float(viewbox[0]) if len(viewbox) >= 1 else 0.0
    vb_y = float(viewbox[1]) if len(viewbox) >= 2 else 0.0
    canvas_w = int(float(viewbox[2])) if len(viewbox) >= 3 else 800
    canvas_h = int(float(viewbox[3])) if len(viewbox) >= 4 else 600

    # ── Detect diagram type ──
    role = root.get("aria-roledescription", "")
    if role not in _SUPPORTED_DIAGRAM_TYPES:
        # Try class-based fallback
        for g in root.iter(f"{{{ns}}}g"):
            cls = g.get("class", "")
            for token in cls.split():
                if token in _CLASS_HEURISTICS:
                    role = _CLASS_HEURISTICS[token]
                    break
            if role:
                break

    # ── Dispatch to type-specific parser ──
    parser_fn = _DIAGRAM_PARSERS.get(role, _parse_flowchart)
    annotations = parser_fn(root, ns)

    # ── Apply viewBox offset so coordinates are in 0-based canvas space ──
    if vb_x != 0.0 or vb_y != 0.0:
        _apply_viewbox_offset(annotations, vb_x, vb_y)

    # ── Normalize and return ──
    _normalize_annotations(annotations)
    return {
        "version": "draft-1",
        "image": {"width": canvas_w, "height": canvas_h},
        "annotations": annotations,
    }


# ─────────────────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────────────────


def _find_group_by_class(
    root: ET.Element, ns: str, class_name: str
) -> Optional[ET.Element]:
    """Find a ``<g>`` element by its ``class`` attribute anywhere in the tree."""
    for g in root.iter(f"{{{ns}}}g"):
        if class_name in g.get("class", "").split():
            return g
    return None


def _find_groups_by_class(
    root: ET.Element, ns: str, class_name: str
) -> List[ET.Element]:
    """Find all ``<g>`` elements containing *class_name* in their class list."""
    result = []
    for g in root.iter(f"{{{ns}}}g"):
        if class_name in g.get("class", "").split():
            result.append(g)
    return result


def _strip_ns(tag: str, ns: str) -> str:
    """Remove namespace prefix from a tag."""
    prefix = f"{{{ns}}}"
    return tag[len(prefix):] if tag.startswith(prefix) else tag


def _parse_translate(transform: str) -> Tuple[float, float]:
    """Extract (tx, ty) from a ``translate(x, y)`` transform string."""
    m = re.search(r"translate\(\s*([-+]?\d*\.?\d+)[,\s]+([-+]?\d*\.?\d+)", transform or "")
    if m:
        return float(m.group(1)), float(m.group(2))
    return 0.0, 0.0


def _apply_viewbox_offset(
    annotations: List[Dict[str, Any]], vb_x: float, vb_y: float
) -> None:
    """Shift all annotation coordinates so they map to 0-based canvas space.

    When a Mermaid SVG has a non-zero viewBox origin (e.g. ``-183 -166 W H``),
    the raw SVG coordinates are offset from the canvas origin.  This subtracts
    the viewBox origin so that annotations sit correctly on the rasterised PNG.

    Args:
        annotations: List of annotation dicts (modified in-place).
        vb_x: ViewBox x origin.
        vb_y: ViewBox y origin.
    """
    for ann in annotations:
        geom = ann.get("geom")
        if not geom:
            continue
        kind = ann.get("kind", "")
        if kind == "line":
            geom["x1"] = round(geom["x1"] - vb_x, 2)
            geom["y1"] = round(geom["y1"] - vb_y, 2)
            geom["x2"] = round(geom["x2"] - vb_x, 2)
            geom["y2"] = round(geom["y2"] - vb_y, 2)
        else:
            if "x" in geom:
                geom["x"] = round(geom["x"] - vb_x, 2)
            if "y" in geom:
                geom["y"] = round(geom["y"] - vb_y, 2)


def _robust_path_bbox(d: str) -> Tuple[float, float, float, float]:
    """Compute bounding box of an SVG path handling both absolute and relative commands.

    Unlike ``_path_bbox`` from plantuml which only handles absolute M/L/C/A,
    this handles the relative commands (m, l, h, v, q, c, etc.) commonly used
    in Mermaid timeline and other diagram paths.

    Returns:
        (x, y, width, height) bounding box.
    """
    # Tokenise: split into command letters and numbers
    tokens = re.findall(r'[MmLlHhVvCcSsQqTtAaZz]|[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', d)
    if not tokens:
        return (0.0, 0.0, 0.0, 0.0)

    points: List[Tuple[float, float]] = []
    cx, cy = 0.0, 0.0  # current point
    sx, sy = 0.0, 0.0  # subpath start (for Z)
    i = 0

    def _next_float() -> float:
        nonlocal i
        i += 1
        return float(tokens[i]) if i < len(tokens) else 0.0

    while i < len(tokens):
        cmd = tokens[i]
        if cmd == 'M':
            cx, cy = _next_float(), _next_float()
            sx, sy = cx, cy
            points.append((cx, cy))
            # Subsequent coordinate pairs are implicit L
            while i + 1 < len(tokens) and tokens[i + 1][0] not in 'MmLlHhVvCcSsQqTtAaZz':
                cx, cy = _next_float(), _next_float()
                points.append((cx, cy))
        elif cmd == 'm':
            cx += _next_float()
            cy += _next_float()
            sx, sy = cx, cy
            points.append((cx, cy))
            while i + 1 < len(tokens) and tokens[i + 1][0] not in 'MmLlHhVvCcSsQqTtAaZz':
                cx += _next_float()
                cy += _next_float()
                points.append((cx, cy))
        elif cmd == 'L':
            cx, cy = _next_float(), _next_float()
            points.append((cx, cy))
        elif cmd == 'l':
            cx += _next_float()
            cy += _next_float()
            points.append((cx, cy))
        elif cmd == 'H':
            cx = _next_float()
            points.append((cx, cy))
        elif cmd == 'h':
            cx += _next_float()
            points.append((cx, cy))
        elif cmd == 'V':
            cy = _next_float()
            points.append((cx, cy))
        elif cmd == 'v':
            cy += _next_float()
            points.append((cx, cy))
        elif cmd == 'C':
            for _ in range(3):
                px, py = _next_float(), _next_float()
                points.append((px, py))
            cx, cy = points[-1]
        elif cmd == 'c':
            for _ in range(3):
                px = cx + _next_float()
                py = cy + _next_float()
                points.append((px, py))
            cx, cy = points[-1]
        elif cmd == 'Q':
            for _ in range(2):
                px, py = _next_float(), _next_float()
                points.append((px, py))
            cx, cy = points[-1]
        elif cmd == 'q':
            for _ in range(2):
                px = cx + _next_float()
                py = cy + _next_float()
                points.append((px, py))
            cx, cy = points[-1]
        elif cmd == 'S':
            for _ in range(2):
                px, py = _next_float(), _next_float()
                points.append((px, py))
            cx, cy = points[-1]
        elif cmd == 's':
            for _ in range(2):
                px = cx + _next_float()
                py = cy + _next_float()
                points.append((px, py))
            cx, cy = points[-1]
        elif cmd == 'T':
            cx, cy = _next_float(), _next_float()
            points.append((cx, cy))
        elif cmd == 't':
            cx += _next_float()
            cy += _next_float()
            points.append((cx, cy))
        elif cmd in ('A', 'a'):
            # arc: rx ry x-rotation large-arc sweep x y
            _next_float()  # rx
            _next_float()  # ry
            _next_float()  # x-rotation
            _next_float()  # large-arc-flag
            _next_float()  # sweep-flag
            if cmd == 'A':
                cx, cy = _next_float(), _next_float()
            else:
                cx += _next_float()
                cy += _next_float()
            points.append((cx, cy))
        elif cmd in ('Z', 'z'):
            cx, cy = sx, sy
        i += 1

    if not points:
        return (0.0, 0.0, 0.0, 0.0)

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    return (round(min_x, 2), round(min_y, 2),
            round(max_x - min_x, 2), round(max_y - min_y, 2))


def _extract_text(g_el: ET.Element, ns: str) -> str:
    """Extract text from a Mermaid SVG group (foreignObject or <text>).

    Handles both HTML-label mode (foreignObject with XHTML spans)
    and plain SVG text mode.
    """
    # Try foreignObject first (default Mermaid output)
    for fo in g_el.iter(f"{{{ns}}}foreignObject"):
        texts: List[str] = []
        for el in fo.iter():
            if el.text and el.text.strip():
                cls = el.get("class", "")
                if cls and "fa-" in cls and not el.text.strip():
                    continue
                texts.append(el.text.strip())
            if el.tail and el.tail.strip():
                texts.append(el.tail.strip())
        if texts:
            return " ".join(texts)

    # Also try XHTML namespace foreignObject content
    for fo in g_el.iter(f"{{{ns}}}foreignObject"):
        for el in fo.iter(f"{{{_XHTML_NS}}}span"):
            if el.text and el.text.strip():
                return el.text.strip()
        for el in fo.iter(f"{{{_XHTML_NS}}}p"):
            if el.text and el.text.strip():
                return el.text.strip()
        texts = []
        for el in fo.iter():
            if el.text and el.text.strip():
                texts.append(el.text.strip())
            if el.tail and el.tail.strip():
                texts.append(el.tail.strip())
        if texts:
            return " ".join(texts)

    # Fallback: native SVG <text>
    for t_el in g_el.iter(f"{{{ns}}}text"):
        parts = list(t_el.itertext())
        if parts:
            joined = " ".join(p.strip() for p in parts if p.strip())
            if joined:
                return joined

    return ""


def _extract_native_text(el: ET.Element, ns: str) -> str:
    """Extract text from native SVG ``<text>`` elements only (skip foreignObject)."""
    for t_el in el.iter(f"{{{ns}}}text"):
        parts = list(t_el.itertext())
        if parts:
            joined = " ".join(p.strip() for p in parts if p.strip())
            if joined:
                return joined
    return ""


def _extract_rect_geom(
    rect_el: ET.Element, tx: float = 0.0, ty: float = 0.0
) -> Tuple[float, float, float, float]:
    """Extract ``(x, y, w, h)`` from a ``<rect>`` element plus a translate offset."""
    lx = float(rect_el.get("x", "0") or "0")
    ly = float(rect_el.get("y", "0") or "0")
    w = float(rect_el.get("width", "0") or "0")
    h = float(rect_el.get("height", "0") or "0")
    return round(tx + lx, 2), round(ty + ly, 2), round(w, 2), round(h, 2)


def _make_shape_style(
    fill: str = "#ECECFF",
    stroke: str = "#9370DB",
    text_color: str = "#333333",
) -> Dict[str, Any]:
    """Return a standard shape style dict."""
    return {
        "pen": {
            "color": stroke, "width": 1, "dash": "solid",
            "dash_pattern_length": 30, "dash_solid_percent": 50,
        },
        "fill": {"color": fill},
        "text": {"color": text_color, "size_pt": 10.0},
    }


def _extract_node_id(node_g: ET.Element, prefix_re: str = r"flowchart-(.+)-\d+$") -> str:
    """Extract the Mermaid node ID from a node group's ``id`` attribute."""
    raw_id = node_g.get("id", "")
    m = re.match(prefix_re, raw_id)
    if m:
        return m.group(1)
    return raw_id


def _parse_polygon_points(points_str: str) -> List[Tuple[float, float]]:
    """Parse a ``points`` attribute into a list of (x, y) tuples."""
    pairs = re.findall(r"([-+]?\d*\.?\d+)[,\s]([-+]?\d*\.?\d+)", points_str)
    return [(float(x), float(y)) for x, y in pairs]


def _get_fill(el: ET.Element) -> Optional[str]:
    """Extract fill colour from an element's ``style`` or ``fill`` attribute."""
    style = el.get("style", "")
    m = re.search(r"fill:\s*(#[0-9a-fA-F]{3,8}|rgb[^)]+\)|hsl[^)]+\))", style)
    if m:
        return m.group(1)
    fill = el.get("fill", "")
    if fill and fill != "none":
        return fill
    return None


def _get_stroke(el: ET.Element) -> Optional[str]:
    """Extract stroke colour from an element's ``style`` or ``stroke`` attribute."""
    style = el.get("style", "")
    m = re.search(r"stroke:\s*(#[0-9a-fA-F]{3,8}|rgb[^)]+\)|hsl[^)]+\))", style)
    if m:
        return m.group(1)
    stroke = el.get("stroke", "")
    if stroke and stroke != "none":
        return stroke
    return None


def _text_from_el(t_el: ET.Element) -> str:
    """Get joined text from a single ``<text>`` element."""
    parts = list(t_el.itertext())
    return " ".join(p.strip() for p in parts if p.strip())


def _extract_path_endpoints(
    d: str,
) -> Optional[Tuple[float, float, float, float]]:
    """Extract first and last point from an SVG path as line endpoints."""
    tokens = re.findall(r"[-+]?\d*\.?\d+", d)
    if len(tokens) < 4:
        return None
    x1, y1 = float(tokens[0]), float(tokens[1])
    x2, y2 = float(tokens[-2]), float(tokens[-1])
    return x1, y1, x2, y2


def _path_bbox(d: str) -> Optional[Tuple[float, float, float, float]]:
    """Compute an approximate bounding box by walking SVG path commands.

    Handles absolute (``M``, ``L``, ``C``, ``H``, ``V``) and relative
    (``m``, ``l``, ``c``, ``h``, ``v``) commands.  Cubic bezier control
    points are included in the bbox, which slightly overestimates curves
    but is sufficient for layout purposes.

    Returns:
        ``(x, y, w, h)`` or ``None`` if the path is too short.
    """
    # Tokenise into commands + numbers
    tokens = re.findall(r"[MmLlCcHhVvSsQqTtAaZz]|[-+]?\d*\.?\d+", d)
    if not tokens:
        return None

    cx, cy = 0.0, 0.0  # current point
    xs: List[float] = []
    ys: List[float] = []
    cmd = "M"
    nums: List[float] = []

    def _flush():
        nonlocal cx, cy
        if not nums:
            return
        if cmd in ("M", "m"):
            if cmd == "M":
                cx, cy = nums[0], nums[1]
            else:
                cx += nums[0]
                cy += nums[1]
            xs.append(cx); ys.append(cy)
            # Implicit lineto pairs after initial move
            i = 2
            while i + 1 < len(nums):
                if cmd == "M":
                    cx, cy = nums[i], nums[i + 1]
                else:
                    cx += nums[i]
                    cy += nums[i + 1]
                xs.append(cx); ys.append(cy)
                i += 2
        elif cmd in ("L", "l"):
            i = 0
            while i + 1 < len(nums):
                if cmd == "L":
                    cx, cy = nums[i], nums[i + 1]
                else:
                    cx += nums[i]
                    cy += nums[i + 1]
                xs.append(cx); ys.append(cy)
                i += 2
        elif cmd in ("H", "h"):
            for n in nums:
                cx = n if cmd == "H" else cx + n
                xs.append(cx); ys.append(cy)
        elif cmd in ("V", "v"):
            for n in nums:
                cy = n if cmd == "V" else cy + n
                xs.append(cx); ys.append(cy)
        elif cmd in ("C", "c"):
            # 6 numbers per segment: cp1x,cp1y, cp2x,cp2y, x,y
            i = 0
            while i + 5 < len(nums):
                if cmd == "C":
                    for j in range(0, 6, 2):
                        xs.append(nums[i + j])
                        ys.append(nums[i + j + 1])
                    cx, cy = nums[i + 4], nums[i + 5]
                else:
                    for j in range(0, 6, 2):
                        xs.append(cx + nums[i + j])
                        ys.append(cy + nums[i + j + 1])
                    cx += nums[i + 4]
                    cy += nums[i + 5]
                i += 6
        # S, Q, T, A — fall through (rare in Mermaid C4)

    for tok in tokens:
        if tok.isalpha() and len(tok) == 1:
            _flush()
            cmd = tok
            nums = []
        else:
            try:
                nums.append(float(tok))
            except ValueError:
                pass
    _flush()

    if not xs or not ys:
        return None
    min_x, min_y = min(xs), min(ys)
    return (round(min_x, 2), round(min_y, 2),
            round(max(xs) - min_x, 2), round(max(ys) - min_y, 2))


# ─────────────────────────────────────────────────────────
# Node parsing (reused across graph-based diagrams)
# ─────────────────────────────────────────────────────────


def _parse_node(
    node_g: ET.Element, ns: str, ann_id: str
) -> Optional[Dict[str, Any]]:
    """Parse a single ``<g class="node ...">`` into an annotation dict."""
    tx, ty = _parse_translate(node_g.get("transform", ""))
    text = _extract_text(node_g, ns)

    # Try shape elements in priority order
    rect_el = node_g.find(f"{{{ns}}}rect[@class]")
    if rect_el is None:
        rect_el = node_g.find(f"{{{ns}}}rect")
    poly_el = node_g.find(f"{{{ns}}}polygon")
    circle_el = node_g.find(f"{{{ns}}}circle")
    ellipse_el = node_g.find(f"{{{ns}}}ellipse")
    path_el = None
    for g_child in node_g:
        tag = _strip_ns(g_child.tag, ns)
        if tag == "g" and "label-container" in g_child.get("class", ""):
            for p in g_child.iter(f"{{{ns}}}path"):
                d = p.get("d", "")
                if d and p.get("fill", "") != "none" and p.get("stroke-width", "") != "0":
                    path_el = p
                    break
            if path_el is None:
                paths = list(g_child.iter(f"{{{ns}}}path"))
                if paths:
                    path_el = paths[-1]
            break

    kind: str
    x: float
    y: float
    w: float
    h: float
    fill_color = "#ECECFF"
    stroke_color = "#9370DB"
    rel_points: List[List[float]] = []

    if rect_el is not None and poly_el is None:
        rx = float(rect_el.get("rx", "0") or "0")
        lx = float(rect_el.get("x", "0") or "0")
        ly = float(rect_el.get("y", "0") or "0")
        w = float(rect_el.get("width", "0") or "0")
        h = float(rect_el.get("height", "0") or "0")
        x = tx + lx
        y = ty + ly
        kind = "roundedrect" if rx > 0 else "rect"
        fill_color = _get_fill(rect_el) or fill_color
        stroke_color = _get_stroke(rect_el) or stroke_color

    elif poly_el is not None:
        points_str = poly_el.get("points", "")
        pts = _parse_polygon_points(points_str)
        poly_tx, poly_ty = _parse_translate(poly_el.get("transform", ""))
        if pts:
            xs = [p[0] + poly_tx for p in pts]
            ys = [p[1] + poly_ty for p in pts]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            w = max_x - min_x
            h = max_y - min_y
            x = tx + min_x
            y = ty + min_y
            rel_points = [
                [round((px - min_x) / w, 4) if w > 0 else 0.0,
                 round((py - min_y) / h, 4) if h > 0 else 0.0]
                for px, py in zip(xs, ys)
            ]
        else:
            x, y, w, h = tx - 40, ty - 40, 80, 80
            rel_points = [[0.5, 0.0], [1.0, 0.5], [0.5, 1.0], [0.0, 0.5]]
        kind = "polygon"
        fill_color = _get_fill(poly_el) or fill_color
        stroke_color = _get_stroke(poly_el) or stroke_color

    elif circle_el is not None:
        cx = float(circle_el.get("cx", "0"))
        cy = float(circle_el.get("cy", "0"))
        r = float(circle_el.get("r", "20"))
        x = tx + cx - r
        y = ty + cy - r
        w = h = 2 * r
        kind = "ellipse"
        fill_color = _get_fill(circle_el) or fill_color
        stroke_color = _get_stroke(circle_el) or stroke_color

    elif ellipse_el is not None:
        cx = float(ellipse_el.get("cx", "0"))
        cy = float(ellipse_el.get("cy", "0"))
        rx = float(ellipse_el.get("rx", "20"))
        ry = float(ellipse_el.get("ry", "20"))
        x = tx + cx - rx
        y = ty + cy - ry
        w = 2 * rx
        h = 2 * ry
        kind = "ellipse"
        fill_color = _get_fill(ellipse_el) or fill_color
        stroke_color = _get_stroke(ellipse_el) or stroke_color

    elif path_el is not None:
        d = path_el.get("d", "")
        bx, by, bw, bh = _robust_path_bbox(d)
        x = tx + bx
        y = ty + by
        w = bw
        h = bh
        kind = "roundedrect"
        fill_color = _get_fill(path_el) or fill_color
        stroke_color = _get_stroke(path_el) or stroke_color

    else:
        # Last resort: any <path> with a visible fill in the node group
        for p in node_g.iter(f"{{{ns}}}path"):
            d = p.get("d", "")
            pf = _get_fill(p)
            if d and pf and pf != "none":
                bx, by, bw, bh = _robust_path_bbox(d)
                if bw > 1 and bh > 1:
                    x = tx + bx
                    y = ty + by
                    w = bw
                    h = bh
                    kind = "rect"
                    fill_color = pf
                    stroke_color = _get_stroke(p) or stroke_color
                    break
        else:
            return None

    x = round(x, 2)
    y = round(y, 2)
    w = round(w, 2)
    h = round(h, 2)

    geom: Dict[str, Any] = {"x": x, "y": y, "w": w, "h": h}
    if kind == "polygon":
        geom["points"] = rel_points

    return {
        "id": ann_id,
        "kind": kind,
        "geom": geom,
        "meta": {"label": text},
        "style": _make_shape_style(fill_color, stroke_color),
    }


# ─────────────────────────────────────────────────────────
# Edge parsing (reused across graph-based diagrams)
# ─────────────────────────────────────────────────────────


def _parse_edge_path(
    path_el: ET.Element,
    ns: str,
    ann_id: str,
    edge_labels: List[Tuple[str, float, float]],
    edge_idx: int,
) -> Optional[Dict[str, Any]]:
    """Parse a single edge ``<path>`` into a curve or line annotation."""
    d = path_el.get("d", "")
    if not d:
        return None

    marker_end = path_el.get("marker-end", "")
    marker_start = path_el.get("marker-start", "")
    if marker_end and marker_start:
        arrow = "both"
    elif marker_start:
        arrow = "start"
    elif marker_end:
        arrow = "end"
    else:
        arrow = "none"

    style_attr = path_el.get("style", "")
    cls = path_el.get("class", "")
    dashed = "dashed" in style_attr or "dashed" in cls or "dotted" in cls

    label = ""
    if 0 <= edge_idx < len(edge_labels):
        label = edge_labels[edge_idx][0]

    style = _make_line_style(
        pen_color="#333333",
        pen_width=2,
        dashed=dashed,
        arrow=arrow,
    )

    nodes, bbox = _parse_path_to_curve_nodes(d)
    if nodes:
        bx, by, bw, bh = bbox
        return {
            "id": ann_id,
            "kind": "curve",
            "geom": {
                "x": round(bx, 2),
                "y": round(by, 2),
                "w": round(bw, 2),
                "h": round(bh, 2),
                "nodes": nodes,
            },
            "meta": {"label": label},
            "style": style,
        }

    endpoints = _extract_path_endpoints(d)
    if endpoints is None:
        return None

    x1, y1, x2, y2 = endpoints
    return {
        "id": ann_id,
        "kind": "line",
        "geom": {
            "x1": round(x1, 2),
            "y1": round(y1, 2),
            "x2": round(x2, 2),
            "y2": round(y2, 2),
        },
        "meta": {"label": label},
        "style": style,
    }


def _parse_cluster(
    cluster_g: ET.Element,
    ns: str,
    ann_id: str,
    all_annotations: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """Parse a ``<g class="cluster">`` into a group annotation."""
    rect_el = cluster_g.find(f"{{{ns}}}rect")
    if rect_el is None:
        return None

    x, y, w, h = _extract_rect_geom(rect_el)
    text = _extract_text(cluster_g, ns)

    return {
        "id": ann_id,
        "kind": "group",
        "geom": {"x": x, "y": y, "w": w, "h": h},
        "meta": {"label": text},
        "style": _make_shape_style("#FFFFDE", "#AAAA33"),
    }


# ─────────────────────────────────────────────────────────
# Graph-based diagram parser (shared by Tier 1 types)
# ─────────────────────────────────────────────────────────


def _parse_graph_diagram(
    root: ET.Element,
    ns: str,
    node_id_re: str = r"flowchart-(.+)-\d+$",
) -> List[Dict[str, Any]]:
    """Generic parser for diagrams that use nodes/edgePaths/edgeLabels/clusters groups."""
    nodes_g = _find_group_by_class(root, ns, "nodes")
    edge_paths_g = _find_group_by_class(root, ns, "edgePaths")
    edge_labels_g = _find_group_by_class(root, ns, "edgeLabels")
    clusters_g = _find_group_by_class(root, ns, "clusters")

    annotations: List[Dict[str, Any]] = []
    next_id = _make_id_gen()

    # ── Nodes ──
    if nodes_g is not None:
        for node_g in nodes_g:
            tag = _strip_ns(node_g.tag, ns)
            if tag != "g":
                continue
            cls = node_g.get("class", "")
            if "node" not in cls:
                continue
            ann = _parse_node(node_g, ns, next_id())
            if ann is not None:
                annotations.append(ann)

    # ── Edge labels ──
    edge_labels: List[Tuple[str, float, float]] = []
    if edge_labels_g is not None:
        for label_g in edge_labels_g:
            tag = _strip_ns(label_g.tag, ns)
            if tag != "g":
                continue
            tx, ty = _parse_translate(label_g.get("transform", ""))
            text = _extract_text(label_g, ns)
            edge_labels.append((text, tx, ty))

    # ── Edge paths ──
    if edge_paths_g is not None:
        edge_idx = 0
        for child in edge_paths_g:
            tag = _strip_ns(child.tag, ns)
            if tag == "path":
                ann = _parse_edge_path(child, ns, next_id(), edge_labels, edge_idx)
                if ann is not None:
                    annotations.append(ann)
                edge_idx += 1
            elif tag == "g":
                path_el = child.find(f"{{{ns}}}path")
                if path_el is None:
                    for p in child.iter(f"{{{ns}}}path"):
                        if p.get("d"):
                            path_el = p
                            break
                if path_el is not None:
                    ann = _parse_edge_path(path_el, ns, next_id(), edge_labels, edge_idx)
                    if ann is not None:
                        annotations.append(ann)
                edge_idx += 1

    # ── Clusters ──
    if clusters_g is not None:
        for cluster_g in clusters_g:
            tag = _strip_ns(cluster_g.tag, ns)
            if tag != "g":
                continue
            ann = _parse_cluster(cluster_g, ns, next_id(), annotations)
            if ann is not None:
                annotations.append(ann)

    return annotations


# ═══════════════════════════════════════════════════════════
# Tier 0: Flowchart
# ═══════════════════════════════════════════════════════════


def _parse_flowchart(root: ET.Element, ns: str) -> List[Dict[str, Any]]:
    """Parse a Mermaid flowchart SVG."""
    return _parse_graph_diagram(root, ns, r"flowchart-(.+)-\d+$")


# ═══════════════════════════════════════════════════════════
# Tier 1: Graph-based (same nodes/edgePaths/edgeLabels)
# ═══════════════════════════════════════════════════════════


def _parse_state(root: ET.Element, ns: str) -> List[Dict[str, Any]]:
    """Parse a Mermaid state diagram SVG."""
    return _parse_graph_diagram(root, ns, r"state-(.+)-\d+$")


def _parse_class(root: ET.Element, ns: str) -> List[Dict[str, Any]]:
    """Parse a Mermaid class diagram SVG."""
    return _parse_graph_diagram(root, ns, r"classId-(.+)-\d+$")


def _parse_er(root: ET.Element, ns: str) -> List[Dict[str, Any]]:
    """Parse a Mermaid ER diagram SVG."""
    return _parse_graph_diagram(root, ns, r"entity-(.+)-\d+$")


def _parse_requirement(root: ET.Element, ns: str) -> List[Dict[str, Any]]:
    """Parse a Mermaid requirement diagram SVG."""
    return _parse_graph_diagram(root, ns, r"(.+)")


def _parse_mindmap(root: ET.Element, ns: str) -> List[Dict[str, Any]]:
    """Parse a Mermaid mindmap SVG."""
    return _parse_graph_diagram(root, ns, r"(.+)")


# ═══════════════════════════════════════════════════════════
# Tier 2: Partial reuse
# ═══════════════════════════════════════════════════════════


def _parse_block(root: ET.Element, ns: str) -> List[Dict[str, Any]]:
    """Parse a Mermaid block diagram SVG.

    Block diagrams have a single ``<g class="block">`` containing node groups
    and ``<path>`` edge elements interleaved.
    """
    block_g = _find_group_by_class(root, ns, "block")
    if block_g is None:
        return _parse_graph_diagram(root, ns)

    annotations: List[Dict[str, Any]] = []
    next_id = _make_id_gen()

    for child in block_g:
        tag = _strip_ns(child.tag, ns)
        cls = child.get("class", "")
        if tag == "g" and "node" in cls:
            ann = _parse_node(child, ns, next_id())
            if ann is not None:
                annotations.append(ann)
        elif tag == "path" and child.get("d"):
            ann = _parse_edge_path(child, ns, next_id(), [], -1)
            if ann is not None:
                annotations.append(ann)

    return annotations


def _parse_sankey(root: ET.Element, ns: str) -> List[Dict[str, Any]]:
    """Parse a Mermaid Sankey diagram SVG.

    Structure: ``<g class="nodes">``, ``<g class="node-labels">``,
    ``<g class="links">``.
    """
    annotations: List[Dict[str, Any]] = []
    next_id = _make_id_gen()

    nodes_g = _find_group_by_class(root, ns, "nodes")
    labels_g = _find_group_by_class(root, ns, "node-labels")
    links_g = _find_group_by_class(root, ns, "links")

    # Collect labels indexed by approximate x position
    label_texts: Dict[str, str] = {}  # node-id -> text
    if labels_g is not None:
        label_idx = 0
        for t_el in labels_g.iter(f"{{{ns}}}text"):
            text = _text_from_el(t_el)
            # Split "Name\nvalue" -> just name
            name = text.split("\n")[0].strip() if text else ""
            label_texts[str(label_idx)] = name
            label_idx += 1

    # ── Nodes ──
    if nodes_g is not None:
        label_idx = 0
        for g in nodes_g:
            tag = _strip_ns(g.tag, ns)
            if tag != "g":
                continue
            cls = g.get("class", "")
            if "node" not in cls:
                continue
            node_id = g.get("id", "")
            tx, ty = _parse_translate(g.get("transform", ""))
            rect = g.find(f"{{{ns}}}rect")
            if rect is None:
                continue
            _, _, w, h = _extract_rect_geom(rect)
            x = round(tx, 2)
            y = round(ty, 2)
            fill = _get_fill(rect) or "#4e79a7"
            label = label_texts.get(str(label_idx), node_id)
            annotations.append({
                "id": next_id(),
                "kind": "rect",
                "geom": {"x": x, "y": y, "w": w, "h": h},
                "meta": {"label": label},
                "style": _make_shape_style(fill, "#333333"),
            })
            label_idx += 1

    # ── Links ──
    if links_g is not None:
        for link_g in links_g:
            tag = _strip_ns(link_g.tag, ns)
            if tag != "g":
                continue
            for path_el in link_g.iter(f"{{{ns}}}path"):
                d = path_el.get("d", "")
                if not d:
                    continue
                nodes, bbox = _parse_path_to_curve_nodes(d)
                if nodes:
                    bx, by, bw, bh = bbox
                    annotations.append({
                        "id": next_id(),
                        "kind": "curve",
                        "geom": {
                            "x": round(bx, 2), "y": round(by, 2),
                            "w": round(bw, 2), "h": round(bh, 2),
                            "nodes": nodes,
                        },
                        "meta": {"label": ""},
                        "style": _make_line_style("#999999", 2, False, "none"),
                    })
                break  # one path per link group

    return annotations


def _parse_kanban(root: ET.Element, ns: str) -> List[Dict[str, Any]]:
    """Parse a Mermaid kanban board SVG.

    Structure: ``<g class="sections">`` (columns) + ``<g class="items">`` (cards).
    """
    annotations: List[Dict[str, Any]] = []
    next_id = _make_id_gen()

    # ── Sections (columns) ──
    sections_g = _find_group_by_class(root, ns, "sections")
    if sections_g is not None:
        for g in sections_g:
            tag = _strip_ns(g.tag, ns)
            if tag != "g":
                continue
            cls = g.get("class", "")
            if "cluster" not in cls:
                continue
            rect = g.find(f"{{{ns}}}rect")
            if rect is None:
                continue
            x, y, w, h = _extract_rect_geom(rect)
            label = _extract_text(g, ns) or g.get("id", "")
            fill = _get_fill(rect) or "#FFFFDE"
            annotations.append({
                "id": next_id(),
                "kind": "group",
                "geom": {"x": x, "y": y, "w": w, "h": h},
                "meta": {"label": label},
                "style": _make_shape_style(fill, "#AAAA33"),
            })

    # ── Items (cards) ──
    items_g = _find_group_by_class(root, ns, "items")
    if items_g is not None:
        for g in items_g:
            tag = _strip_ns(g.tag, ns)
            if tag != "g":
                continue
            cls = g.get("class", "")
            if "node" not in cls:
                continue
            ann = _parse_node(g, ns, next_id())
            if ann is not None:
                annotations.append(ann)

    return annotations


def _parse_architecture(root: ET.Element, ns: str) -> List[Dict[str, Any]]:
    """Parse a Mermaid architecture diagram SVG.

    Structure: ``architecture-edges``, ``architecture-services``,
    ``architecture-groups``.
    """
    annotations: List[Dict[str, Any]] = []
    next_id = _make_id_gen()

    # ── Groups (bounding boxes) ──
    groups_g = _find_group_by_class(root, ns, "architecture-groups")
    if groups_g is not None:
        for rect_el in groups_g.iter(f"{{{ns}}}rect"):
            rect_id = rect_el.get("id", "")
            if not rect_id.startswith("group-"):
                continue
            x, y, w, h = _extract_rect_geom(rect_el)
            # Find label text near this rect
            label = rect_id.replace("group-", "")
            # Try to get text from sibling elements
            parent = groups_g
            for t_el in parent.iter(f"{{{ns}}}text"):
                txt = _text_from_el(t_el)
                if txt:
                    label = txt
                    break
            annotations.append({
                "id": next_id(),
                "kind": "group",
                "geom": {"x": x, "y": y, "w": w, "h": h},
                "meta": {"label": label},
                "style": _make_shape_style("#ECECFF", "#9370DB"),
            })

    # ── Services (icon boxes + text labels) ──
    services_g = _find_group_by_class(root, ns, "architecture-services")
    if services_g is not None:
        for g in services_g:
            tag = _strip_ns(g.tag, ns)
            if tag != "g":
                continue
            svc_id = g.get("id", "")
            if not svc_id.startswith("service-"):
                continue
            tx, ty = _parse_translate(g.get("transform", ""))
            # Services are 80x80 icon boxes
            w, h = 80.0, 80.0
            x = round(tx, 2)
            y = round(ty, 2)
            label = _extract_native_text(g, ns) or svc_id.replace("service-", "")
            annotations.append({
                "id": next_id(),
                "kind": "rect",
                "geom": {"x": x, "y": y, "w": w, "h": h},
                "meta": {"label": label},
                "style": _make_shape_style("#087EBF", "#333333", "#FFFFFF"),
            })
            # Emit a text annotation for the label below the icon.
            # The label group uses translate(40, 80) within the service.
            if label:
                annotations.append({
                    "id": next_id(),
                    "kind": "text",
                    "geom": {"x": round(tx + 40, 2), "y": round(ty + 80, 2)},
                    "meta": {"note": label},
                    "style": {"text": {"color": "#333333", "size": 14}},
                })

    # ── Edges ──
    edges_g = _find_group_by_class(root, ns, "architecture-edges")
    if edges_g is not None:
        for g in edges_g:
            for path_el in g.iter(f"{{{ns}}}path"):
                d = path_el.get("d", "")
                if not d:
                    continue
                ann = _parse_edge_path(path_el, ns, next_id(), [], -1)
                if ann is not None:
                    annotations.append(ann)
                break

    return annotations


def _parse_c4(root: ET.Element, ns: str) -> List[Dict[str, Any]]:
    """Parse a Mermaid C4 context diagram SVG.

    Structure: flat ``<g class="person-man">`` groups + connection lines/paths.
    """
    annotations: List[Dict[str, Any]] = []
    next_id = _make_id_gen()

    # ── Person/system boxes ──
    for g in _find_groups_by_class(root, ns, "person-man"):
        # Determine geometry and kind from the primary shape element.
        # Rect-based nodes → roundedrect; path-based nodes (e.g. cylinder/db) → curve.
        rect_el = g.find(f"{{{ns}}}rect")
        if rect_el is not None:
            x, y, w, h = _extract_rect_geom(rect_el)
            fill = _get_fill(rect_el) or "#08427B"
            stroke = _get_stroke(rect_el) or "#073B6F"
            kind = "roundedrect"
        else:
            # Path-based shape (cylinder, queue, etc.) — extract bbox
            # from the first filled <path> element.
            filled_path = None
            for p_el in g.iter(f"{{{ns}}}path"):
                if (p_el.get("fill") or "none").lower() != "none":
                    filled_path = p_el
                    break
            if filled_path is None:
                continue
            x, y, w, h = _robust_path_bbox(filled_path.get("d", ""))
            if w == 0 and h == 0:
                continue
            fill = _get_fill(filled_path) or "#08427B"
            stroke = _get_stroke(filled_path) or "#073B6F"
            kind = "curve"

        # Classify each text element:
        #   <<stereotype>> — C4 stereotype (used for kind mapping, not displayed)
        #   [technology]   — tech tag, strip brackets (display adds them back)
        #   first plain    — label
        #   remaining      — note
        stereotype = ""
        tech = ""
        labels: List[str] = []
        notes: List[str] = []
        for t_el in g.iter(f"{{{ns}}}text"):
            txt = _text_from_el(t_el)
            if not txt:
                continue
            if txt.startswith("<<") and txt.endswith(">>"):
                stereotype = txt[2:-2].strip()
                continue
            if txt.startswith("[") and txt.endswith("]"):
                tech = txt[1:-1].strip()
            elif not labels:
                labels.append(txt)
            else:
                notes.append(txt)

        # Refine kind from stereotype via alias map
        if stereotype:
            resolved = resolve_kind_alias(stereotype)
            if resolved:
                kind = resolved

        label = labels[0] if labels else ""
        note = " ".join(notes)
        meta: Dict[str, Any] = {"label": label}
        if tech:
            meta["tech"] = tech
        if note:
            meta["note"] = note
        annotations.append({
            "id": next_id(),
            "kind": kind,
            "geom": {"x": x, "y": y, "w": w, "h": h},
            "meta": meta,
            "style": _make_shape_style(fill, stroke, "#FFFFFF"),
        })

    # ── Connection lines and paths ──
    # Connections are direct <line> and <path> elements at SVG root or in unnamed <g>
    for el in root:
        tag = _strip_ns(el.tag, ns)
        if tag == "g":
            cls = el.get("class", "")
            if cls and cls != "":
                continue  # skip named groups
            # Unnamed group may contain lines and paths
            for child in el:
                child_tag = _strip_ns(child.tag, ns)
                if child_tag == "line":
                    _add_line_from_el(child, ns, next_id, annotations)
                elif child_tag == "path":
                    d = child.get("d", "")
                    if d and "fill" not in (child.get("style", "")):
                        ann = _parse_edge_path(child, ns, next_id(), [], -1)
                        if ann is not None:
                            annotations.append(ann)
        elif tag == "line":
            _add_line_from_el(el, ns, next_id, annotations)

    return annotations


def _add_line_from_el(
    el: ET.Element,
    ns: str,
    next_id: Any,
    annotations: List[Dict[str, Any]],
) -> None:
    """Create a line annotation from a ``<line>`` element."""
    x1 = float(el.get("x1", "0"))
    y1 = float(el.get("y1", "0"))
    x2 = float(el.get("x2", "0"))
    y2 = float(el.get("y2", "0"))
    marker = el.get("marker-end", "")
    arrow = "end" if marker else "none"
    stroke = el.get("stroke", "#444444")
    annotations.append({
        "id": next_id(),
        "kind": "line",
        "geom": {
            "x1": round(x1, 2), "y1": round(y1, 2),
            "x2": round(x2, 2), "y2": round(y2, 2),
        },
        "meta": {"label": ""},
        "style": _make_line_style(stroke, 1, False, arrow),
    })


# ═══════════════════════════════════════════════════════════
# Tier 3: Fully custom parsers
# ═══════════════════════════════════════════════════════════


def _parse_sequence(root: ET.Element, ns: str) -> List[Dict[str, Any]]:
    """Parse a Mermaid sequence diagram SVG.

    Elements are flat (no class-based grouping). Actors are ``<rect>`` with
    class ``actor``, messages are ``<line class="messageLine*">``, notes are
    ``<rect class="note">``.
    """
    annotations: List[Dict[str, Any]] = []
    next_id = _make_id_gen()

    seen_actors: Dict[str, str] = {}  # name -> ann_id (avoid top+bottom dupes)

    for el in root.iter():
        tag = _strip_ns(el.tag, ns)
        cls = el.get("class", "")

        # ── Actor boxes (top only to avoid duplicates) ──
        if tag == "rect" and "actor" in cls and "actor-top" in cls:
            name = el.get("name", "")
            x, y, w, h = _extract_rect_geom(el)
            aid = next_id()
            seen_actors[name] = aid
            annotations.append({
                "id": aid,
                "kind": "roundedrect",
                "geom": {"x": x, "y": y, "w": w, "h": h},
                "meta": {"label": name},
                "style": _make_shape_style("#EAEAEA", "#666666"),
            })

        # ── Notes ──
        if tag == "rect" and "note" in cls:
            x, y, w, h = _extract_rect_geom(el)
            annotations.append({
                "id": next_id(),
                "kind": "roundedrect",
                "geom": {"x": x, "y": y, "w": w, "h": h},
                "meta": {"label": ""},  # text collected below
                "style": _make_shape_style("#FFF5AD", "#AAAA33"),
            })

        # ── Message lines ──
        if tag == "line" and "messageLine" in cls:
            x1 = float(el.get("x1", "0"))
            y1 = float(el.get("y1", "0"))
            x2 = float(el.get("x2", "0"))
            y2 = float(el.get("y2", "0"))
            marker = el.get("marker-end", "")
            arrow = "end" if marker else "none"
            dashed = "messageLine1" in cls or "dash" in el.get("style", "")
            annotations.append({
                "id": next_id(),
                "kind": "line",
                "geom": {
                    "x1": round(x1, 2), "y1": round(y1, 2),
                    "x2": round(x2, 2), "y2": round(y2, 2),
                },
                "meta": {"label": ""},
                "style": _make_line_style("#333333", 2, dashed, arrow),
            })

        # ── Self-referencing message paths ──
        if tag == "path" and "messageLine" in cls:
            d = el.get("d", "")
            if d:
                ann = _parse_edge_path(el, ns, next_id(), [], -1)
                if ann is not None:
                    annotations.append(ann)

        # ── Loop boxes (loopLine rects implied by polygon) ──
        if tag == "polygon" and "labelBox" in cls:
            points_str = el.get("points", "")
            pts = _parse_polygon_points(points_str)
            if pts:
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                annotations.append({
                    "id": next_id(),
                    "kind": "roundedrect",
                    "geom": {
                        "x": round(min(xs), 2), "y": round(min(ys), 2),
                        "w": round(max(xs) - min(xs), 2),
                        "h": round(max(ys) - min(ys), 2),
                    },
                    "meta": {"label": "loop"},
                    "style": _make_shape_style("#ECECFF", "#9370DB"),
                })

    # ── Collect message text labels ──
    msg_idx = 0
    line_anns = [a for a in annotations if a["kind"] == "line"]
    for el in root.iter(f"{{{ns}}}text"):
        cls = el.get("class", "")
        if "messageText" in cls:
            txt = _text_from_el(el)
            if msg_idx < len(line_anns):
                line_anns[msg_idx]["meta"]["label"] = txt
            msg_idx += 1

    # ── Collect note text labels ──
    note_anns = [a for a in annotations if a["style"]["fill"]["color"] == "#FFF5AD"]
    note_idx = 0
    for el in root.iter(f"{{{ns}}}text"):
        cls = el.get("class", "")
        if "noteText" in cls:
            txt = _text_from_el(el)
            if note_idx < len(note_anns):
                note_anns[note_idx]["meta"]["label"] = txt
            note_idx += 1

    return annotations


def _parse_gantt(root: ET.Element, ns: str) -> List[Dict[str, Any]]:
    """Parse a Mermaid Gantt chart SVG.

    Task bars have IDs like ``a1``, paired with text IDs like ``a1-text``.
    Section titles use class ``sectionTitle``.
    """
    annotations: List[Dict[str, Any]] = []
    next_id = _make_id_gen()

    # Collect task texts: id -> text
    task_texts: Dict[str, str] = {}
    for t_el in root.iter(f"{{{ns}}}text"):
        tid = t_el.get("id", "")
        cls = t_el.get("class", "")
        if tid.endswith("-text") and "taskText" in cls:
            task_texts[tid.replace("-text", "")] = _text_from_el(t_el).strip()

    # ── Title ──
    for t_el in root.iter(f"{{{ns}}}text"):
        cls = t_el.get("class", "")
        if "titleText" in cls:
            txt = _text_from_el(t_el)
            x = float(t_el.get("x", "0"))
            y = float(t_el.get("y", "0"))
            annotations.append({
                "id": next_id(),
                "kind": "text",
                "geom": {"x": round(x, 2), "y": round(y - 10, 2)},
                "meta": {"note": txt},
                "style": _make_shape_style("#FFFFFF", "#333333"),
            })
            break

    # ── Section title labels ──
    for t_el in root.iter(f"{{{ns}}}text"):
        cls = t_el.get("class", "")
        if "sectionTitle" in cls:
            txt = _text_from_el(t_el)
            x = float(t_el.get("x", "0"))
            y = float(t_el.get("y", "0"))
            annotations.append({
                "id": next_id(),
                "kind": "text",
                "geom": {"x": round(x, 2), "y": round(y - 6, 2)},
                "meta": {"note": txt},
                "style": _make_shape_style("#FFFFFF", "#333333"),
            })

    # ── Task bars ──
    for rect_el in root.iter(f"{{{ns}}}rect"):
        cls = rect_el.get("class", "")
        rid = rect_el.get("id", "")
        if "task" in cls and rid and not rid.endswith("-text"):
            x, y, w, h = _extract_rect_geom(rect_el)
            if w < 1 or h < 1:
                continue
            label = task_texts.get(rid, rid)
            fill = _get_fill(rect_el) or "#8a90dd"
            annotations.append({
                "id": next_id(),
                "kind": "roundedrect",
                "geom": {"x": x, "y": y, "w": w, "h": h},
                "meta": {"label": label},
                "style": _make_shape_style(fill, "#534fbc", "#FFFFFF"),
            })

    return annotations


def _parse_packet(root: ET.Element, ns: str) -> List[Dict[str, Any]]:
    """Parse a Mermaid packet diagram SVG.

    Packet fields are ``<rect class="packetBlock">`` with matching
    ``<text class="packetLabel">`` labels.
    """
    annotations: List[Dict[str, Any]] = []
    next_id = _make_id_gen()

    # ── Title ──
    for t_el in root.iter(f"{{{ns}}}text"):
        cls = t_el.get("class", "")
        if "packetTitle" in cls:
            txt = _text_from_el(t_el)
            x = float(t_el.get("x", "0"))
            y = float(t_el.get("y", "0"))
            annotations.append({
                "id": next_id(),
                "kind": "text",
                "geom": {"x": round(x, 2), "y": round(y, 2)},
                "meta": {"note": txt},
                "style": _make_shape_style("#FFFFFF", "#333333"),
            })
            break

    # ── Packet blocks (field rectangles) ──
    blocks: List[Tuple[float, float, float, float]] = []
    for rect_el in root.iter(f"{{{ns}}}rect"):
        cls = rect_el.get("class", "")
        if "packetBlock" in cls:
            x, y, w, h = _extract_rect_geom(rect_el)
            blocks.append((x, y, w, h))
            annotations.append({
                "id": next_id(),
                "kind": "rect",
                "geom": {"x": x, "y": y, "w": w, "h": h},
                "meta": {"label": ""},
                "style": _make_shape_style("#ECECFF", "#9370DB"),
            })

    # ── Labels (match to blocks by index) ──
    label_idx = 0
    block_anns = [a for a in annotations if a["kind"] == "rect"]
    for t_el in root.iter(f"{{{ns}}}text"):
        cls = t_el.get("class", "")
        if "packetLabel" in cls:
            txt = _text_from_el(t_el)
            if label_idx < len(block_anns):
                block_anns[label_idx]["meta"]["label"] = txt
            label_idx += 1

    return annotations


def _parse_timeline(root: ET.Element, ns: str) -> List[Dict[str, Any]]:
    """Parse a Mermaid timeline diagram SVG.

    Timeline nodes have class ``timeline-node``, with nested ``<path>``
    for rounded-rect shapes and ``<text>`` for labels.  Wrapper groups
    (``taskWrapper``, ``eventWrapper``, or bare ``<g>``) carry the outer
    translate, while the ``timeline-node`` group may have its own.
    """
    annotations: List[Dict[str, Any]] = []
    next_id = _make_id_gen()

    # Build parent map so we can walk up to get wrapper transforms
    parent_map: Dict[ET.Element, ET.Element] = {}
    for parent in root.iter():
        for child in parent:
            parent_map[child] = parent

    # ── Timeline nodes (decade/period blocks) ──
    for g in root.iter(f"{{{ns}}}g"):
        cls = g.get("class", "")
        if "timeline-node" not in cls:
            continue
        # Find the first path for the shape bounding box
        for path_el in g.iter(f"{{{ns}}}path"):
            d = path_el.get("d", "")
            if not d:
                continue
            bx, by, bw, bh = _robust_path_bbox(d)
            if bw < 2 or bh < 2:
                continue
            # Accumulate transforms up the tree
            tx, ty = _parse_translate(g.get("transform", ""))
            ancestor = parent_map.get(g)
            while ancestor is not None:
                ax, ay = _parse_translate(ancestor.get("transform", ""))
                tx += ax
                ty += ay
                ancestor = parent_map.get(ancestor)
            label = _extract_native_text(g, ns)
            fill = _get_fill(path_el) or "#ECECFF"
            annotations.append({
                "id": next_id(),
                "kind": "roundedrect",
                "geom": {
                    "x": round(tx + bx, 2), "y": round(ty + by, 2),
                    "w": round(bw, 2), "h": round(bh, 2),
                },
                "meta": {"label": label},
                "style": _make_shape_style(fill, "#9370DB"),
            })
            break

    # ── Title text ──
    for t_el in root.iter(f"{{{ns}}}text"):
        txt = _text_from_el(t_el)
        if txt and float(t_el.get("font-size", "0").replace("ex", "").replace("px", "").replace("em", "") or "0") > 2:
            x = float(t_el.get("x", "0"))
            y = float(t_el.get("y", "0"))
            annotations.append({
                "id": next_id(),
                "kind": "text",
                "geom": {"x": round(x, 2), "y": round(y, 2)},
                "meta": {"note": txt},
                "style": _make_shape_style("#FFFFFF", "#333333"),
            })
            break

    return annotations


def _parse_pie(root: ET.Element, ns: str) -> List[Dict[str, Any]]:
    """Parse a Mermaid pie chart SVG.

    Slices are ``<path class="pieCircle">``, labels are ``<text class="slice">``,
    legend entries are ``<g class="legend">``.
    """
    annotations: List[Dict[str, Any]] = []
    next_id = _make_id_gen()

    # Find the centering translate group
    center_tx, center_ty = 0.0, 0.0
    for g in root.iter(f"{{{ns}}}g"):
        t = g.get("transform", "")
        if "translate" in t:
            # Check if this group contains pie elements
            has_pie = False
            for child in g:
                tag = _strip_ns(child.tag, ns)
                cls = child.get("class", "")
                if "pieCircle" in cls or "pieOuterCircle" in cls:
                    has_pie = True
                    break
            if has_pie:
                center_tx, center_ty = _parse_translate(t)
                break

    # ── Title ──
    for t_el in root.iter(f"{{{ns}}}text"):
        cls = t_el.get("class", "")
        if "pieTitleText" in cls:
            txt = _text_from_el(t_el)
            x = float(t_el.get("x", "0"))
            y = float(t_el.get("y", "0"))
            annotations.append({
                "id": next_id(),
                "kind": "text",
                "geom": {"x": round(center_tx + x, 2), "y": round(center_ty + y, 2)},
                "meta": {"note": txt},
                "style": _make_shape_style("#FFFFFF", "#333333"),
            })
            break

    # ── Outer circle as ellipse ──
    for circle_el in root.iter(f"{{{ns}}}circle"):
        cls = circle_el.get("class", "")
        if "pieOuterCircle" in cls:
            r = float(circle_el.get("r", "0"))
            cx = float(circle_el.get("cx", "0"))
            cy = float(circle_el.get("cy", "0"))
            annotations.append({
                "id": next_id(),
                "kind": "ellipse",
                "geom": {
                    "x": round(center_tx + cx - r, 2),
                    "y": round(center_ty + cy - r, 2),
                    "w": round(2 * r, 2),
                    "h": round(2 * r, 2),
                },
                "meta": {"label": ""},
                "style": _make_shape_style("#FFFFFF00", "#000000"),
            })
            break

    # ── Pie slices ──
    slice_labels: List[str] = []
    for t_el in root.iter(f"{{{ns}}}text"):
        cls = t_el.get("class", "")
        if "slice" in cls.split():
            slice_labels.append(_text_from_el(t_el))

    slice_idx = 0
    for path_el in root.iter(f"{{{ns}}}path"):
        cls = path_el.get("class", "")
        if "pieCircle" not in cls:
            continue
        d = path_el.get("d", "")
        if not d:
            continue
        bx, by, bw, bh = _path_bbox(d)
        fill = _get_fill(path_el) or "#ECECFF"
        label = slice_labels[slice_idx] if slice_idx < len(slice_labels) else ""
        annotations.append({
            "id": next_id(),
            "kind": "roundedrect",
            "geom": {
                "x": round(center_tx + bx, 2), "y": round(center_ty + by, 2),
                "w": round(bw, 2), "h": round(bh, 2),
            },
            "meta": {"label": label},
            "style": _make_shape_style(fill, "#000000"),
        })
        slice_idx += 1

    # ── Legend entries ──
    for g in _find_groups_by_class(root, ns, "legend"):
        tx, ty = _parse_translate(g.get("transform", ""))
        rect = g.find(f"{{{ns}}}rect")
        text_el = g.find(f"{{{ns}}}text")
        if rect is not None and text_el is not None:
            fill_style = rect.get("style", "")
            fill_m = re.search(r"fill:\s*([^;]+)", fill_style)
            fill = fill_m.group(1).strip() if fill_m else "#ECECFF"
            txt = _text_from_el(text_el)
            rw = float(rect.get("width", "18"))
            rh = float(rect.get("height", "18"))
            annotations.append({
                "id": next_id(),
                "kind": "rect",
                "geom": {
                    "x": round(center_tx + tx, 2),
                    "y": round(center_ty + ty, 2),
                    "w": round(rw, 2), "h": round(rh, 2),
                },
                "meta": {"label": txt},
                "style": _make_shape_style(fill, fill),
            })

    return annotations


def _parse_xychart(root: ET.Element, ns: str) -> List[Dict[str, Any]]:
    """Parse a Mermaid XY chart SVG.

    Structure: ``<g class="main">`` containing ``<g class="plot">``,
    ``<g class="bar-plot-*">``, ``<g class="line-plot-*">``,
    ``<g class="bottom-axis">``, etc.
    """
    annotations: List[Dict[str, Any]] = []
    next_id = _make_id_gen()

    main_g = _find_group_by_class(root, ns, "main")
    if main_g is None:
        return annotations

    # ── Title ──
    title_g = _find_group_by_class(main_g, ns, "chart-title")
    if title_g is not None:
        for t_el in title_g.iter(f"{{{ns}}}text"):
            txt = _text_from_el(t_el)
            if txt:
                # Parse transform for position
                tr = t_el.get("transform", "")
                tx, ty = _parse_translate(tr)
                annotations.append({
                    "id": next_id(),
                    "kind": "text",
                    "geom": {"x": round(tx, 2), "y": round(ty - 10, 2)},
                    "meta": {"note": txt},
                    "style": _make_shape_style("#FFFFFF", "#333333"),
                })
                break

    # ── Axis labels ──
    for axis_class in ("bottom-axis", "left-axis"):
        axis_g = _find_group_by_class(main_g, ns, axis_class)
        if axis_g is None:
            continue
        label_g = _find_group_by_class(axis_g, ns, "label")
        if label_g is not None:
            for t_el in label_g.iter(f"{{{ns}}}text"):
                txt = _text_from_el(t_el)
                if txt:
                    tr = t_el.get("transform", "")
                    tx, ty = _parse_translate(tr)
                    annotations.append({
                        "id": next_id(),
                        "kind": "text",
                        "geom": {"x": round(tx, 2), "y": round(ty, 2)},
                        "meta": {"note": txt},
                        "style": _make_shape_style("#FFFFFF", "#131300"),
                    })

    # ── Bar plots ──
    for g in main_g.iter(f"{{{ns}}}g"):
        cls = g.get("class", "")
        if "bar-plot" in cls:
            for rect_el in g.iter(f"{{{ns}}}rect"):
                x, y, w, h = _extract_rect_geom(rect_el)
                if w < 1 or h < 1:
                    continue
                fill = _get_fill(rect_el) or "#ECECFF"
                annotations.append({
                    "id": next_id(),
                    "kind": "rect",
                    "geom": {"x": x, "y": y, "w": w, "h": h},
                    "meta": {"label": ""},
                    "style": _make_shape_style(fill, fill),
                })

    # ── Line plots ──
    for g in main_g.iter(f"{{{ns}}}g"):
        cls = g.get("class", "")
        if "line-plot" in cls:
            for path_el in g.iter(f"{{{ns}}}path"):
                d = path_el.get("d", "")
                if not d:
                    continue
                nodes, bbox = _parse_path_to_curve_nodes(d)
                if nodes:
                    bx, by, bw, bh = bbox
                    stroke = _get_stroke(path_el) or "#8493A6"
                    annotations.append({
                        "id": next_id(),
                        "kind": "curve",
                        "geom": {
                            "x": round(bx, 2), "y": round(by, 2),
                            "w": round(bw, 2), "h": round(bh, 2),
                            "nodes": nodes,
                        },
                        "meta": {"label": ""},
                        "style": _make_line_style(stroke, 2, False, "none"),
                    })

    return annotations


def _parse_quadrant(root: ET.Element, ns: str) -> List[Dict[str, Any]]:
    """Parse a Mermaid quadrant chart SVG.

    Structure: ``<g class="main">`` with ``quadrants``, ``data-points``,
    ``labels``, ``title`` sub-groups.
    """
    annotations: List[Dict[str, Any]] = []
    next_id = _make_id_gen()

    main_g = _find_group_by_class(root, ns, "main")
    if main_g is None:
        return annotations

    # ── Title ──
    title_g = _find_group_by_class(main_g, ns, "title")
    if title_g is not None:
        for t_el in title_g.iter(f"{{{ns}}}text"):
            txt = _text_from_el(t_el)
            if txt:
                tr = t_el.get("transform", "")
                tx, ty = _parse_translate(tr)
                annotations.append({
                    "id": next_id(),
                    "kind": "text",
                    "geom": {"x": round(tx, 2), "y": round(ty, 2)},
                    "meta": {"note": txt},
                    "style": _make_shape_style("#FFFFFF", "#333333"),
                })
                break

    # ── Quadrant rectangles ──
    quadrants_g = _find_group_by_class(main_g, ns, "quadrants")
    if quadrants_g is not None:
        for qg in quadrants_g:
            tag = _strip_ns(qg.tag, ns)
            if tag != "g":
                continue
            rect = qg.find(f"{{{ns}}}rect")
            if rect is None:
                continue
            x, y, w, h = _extract_rect_geom(rect)
            fill = _get_fill(rect) or "#ECECFF"
            label = ""
            t_el = qg.find(f"{{{ns}}}text")
            if t_el is not None:
                label = _text_from_el(t_el)
            annotations.append({
                "id": next_id(),
                "kind": "rect",
                "geom": {"x": x, "y": y, "w": w, "h": h},
                "meta": {"label": label},
                "style": _make_shape_style(fill, "#C7C7F1"),
            })

    # ── Data points ──
    points_g = _find_group_by_class(main_g, ns, "data-points")
    if points_g is not None:
        for pg in points_g:
            tag = _strip_ns(pg.tag, ns)
            if tag != "g":
                continue
            circle_el = pg.find(f"{{{ns}}}circle")
            if circle_el is None:
                continue
            cx = float(circle_el.get("cx", "0"))
            cy = float(circle_el.get("cy", "0"))
            r = float(circle_el.get("r", "5"))
            label = ""
            t_el = pg.find(f"{{{ns}}}text")
            if t_el is not None:
                label = _text_from_el(t_el)
            annotations.append({
                "id": next_id(),
                "kind": "ellipse",
                "geom": {
                    "x": round(cx - r, 2), "y": round(cy - r, 2),
                    "w": round(2 * r, 2), "h": round(2 * r, 2),
                },
                "meta": {"label": label},
                "style": _make_shape_style("#6666FF", "#6666FF"),
            })

    # ── Axis labels ──
    labels_g = _find_group_by_class(main_g, ns, "labels")
    if labels_g is not None:
        for lg in labels_g:
            tag = _strip_ns(lg.tag, ns)
            if tag != "g":
                continue
            for t_el in lg.iter(f"{{{ns}}}text"):
                txt = _text_from_el(t_el)
                if txt:
                    tr = t_el.get("transform", "")
                    tx, ty = _parse_translate(tr)
                    annotations.append({
                        "id": next_id(),
                        "kind": "text",
                        "geom": {"x": round(tx, 2), "y": round(ty, 2)},
                        "meta": {"note": txt},
                        "style": _make_shape_style("#FFFFFF", "#131300"),
                    })

    return annotations


def _parse_gitgraph(root: ET.Element, ns: str) -> List[Dict[str, Any]]:
    """Parse a Mermaid git graph SVG.

    Structure: ``<g class="commit-bullets">`` (circles),
    ``<g class="commit-labels">`` (text), ``<g class="commit-arrows">`` (paths),
    plus branch lines and labels.
    """
    annotations: List[Dict[str, Any]] = []
    next_id = _make_id_gen()

    # ── Branch lines ──
    for el in root.iter(f"{{{ns}}}line"):
        cls = el.get("class", "")
        if "branch" in cls:
            x1 = float(el.get("x1", "0"))
            y1 = float(el.get("y1", "0"))
            x2 = float(el.get("x2", "0"))
            y2 = float(el.get("y2", "0"))
            annotations.append({
                "id": next_id(),
                "kind": "line",
                "geom": {
                    "x1": round(x1, 2), "y1": round(y1, 2),
                    "x2": round(x2, 2), "y2": round(y2, 2),
                },
                "meta": {"label": ""},
                "style": _make_line_style("#333333", 1, True, "none"),
            })

    # ── Branch labels ──
    for g in _find_groups_by_class(root, ns, "branchLabel"):
        txt = _extract_native_text(g, ns)
        if txt:
            tx, ty = _parse_translate(g.get("transform", ""))
            annotations.append({
                "id": next_id(),
                "kind": "text",
                "geom": {"x": round(tx, 2), "y": round(ty, 2)},
                "meta": {"note": txt},
                "style": _make_shape_style("#FFFFFF", "#333333"),
            })

    # ── Commit circles ──
    bullets_g = _find_group_by_class(root, ns, "commit-bullets")
    if bullets_g is not None:
        for circle_el in bullets_g.iter(f"{{{ns}}}circle"):
            cx = float(circle_el.get("cx", "0"))
            cy = float(circle_el.get("cy", "0"))
            r = float(circle_el.get("r", "10"))
            cls = circle_el.get("class", "")
            if "commit-merge" in cls:
                continue  # skip inner merge circles (duplicates)
            fill = _get_fill(circle_el) or "#0000EC"
            annotations.append({
                "id": next_id(),
                "kind": "ellipse",
                "geom": {
                    "x": round(cx - r, 2), "y": round(cy - r, 2),
                    "w": round(2 * r, 2), "h": round(2 * r, 2),
                },
                "meta": {"label": ""},
                "style": _make_shape_style(fill, fill),
            })

    # ── Commit labels ──
    labels_g = _find_group_by_class(root, ns, "commit-labels")
    if labels_g is not None:
        commit_anns = [a for a in annotations if a["kind"] == "ellipse"]
        label_idx = 0
        for t_el in labels_g.iter(f"{{{ns}}}text"):
            cls = t_el.get("class", "")
            if "commit-label" in cls:
                txt = _text_from_el(t_el)
                if label_idx < len(commit_anns):
                    commit_anns[label_idx]["meta"]["label"] = txt
                label_idx += 1

    # ── Commit arrows ──
    arrows_g = _find_group_by_class(root, ns, "commit-arrows")
    if arrows_g is not None:
        for path_el in arrows_g.iter(f"{{{ns}}}path"):
            d = path_el.get("d", "")
            if not d:
                continue
            nodes, bbox = _parse_path_to_curve_nodes(d)
            if nodes:
                bx, by, bw, bh = bbox
                cls = path_el.get("class", "")
                stroke = _get_stroke(path_el) or "#333333"
                annotations.append({
                    "id": next_id(),
                    "kind": "curve",
                    "geom": {
                        "x": round(bx, 2), "y": round(by, 2),
                        "w": round(bw, 2), "h": round(bh, 2),
                        "nodes": nodes,
                    },
                    "meta": {"label": ""},
                    "style": _make_line_style(stroke, 8, False, "none"),
                })
            else:
                endpoints = _extract_path_endpoints(d)
                if endpoints:
                    x1, y1, x2, y2 = endpoints
                    annotations.append({
                        "id": next_id(),
                        "kind": "line",
                        "geom": {
                            "x1": round(x1, 2), "y1": round(y1, 2),
                            "x2": round(x2, 2), "y2": round(y2, 2),
                        },
                        "meta": {"label": ""},
                        "style": _make_line_style("#333333", 8, False, "none"),
                    })

    return annotations


def _parse_journey(root: ET.Element, ns: str) -> List[Dict[str, Any]]:
    """Parse a Mermaid user journey diagram SVG.

    Flat structure: section rects, task rects, actor circles, face circles.
    """
    annotations: List[Dict[str, Any]] = []
    next_id = _make_id_gen()

    # ── Title ──
    for t_el in root.iter(f"{{{ns}}}text"):
        style = t_el.get("font-weight", "")
        fs = t_el.get("font-size", "")
        if "bold" in style or "4ex" in fs:
            txt = _text_from_el(t_el)
            if txt:
                x = float(t_el.get("x", "0"))
                y = float(t_el.get("y", "0"))
                annotations.append({
                    "id": next_id(),
                    "kind": "text",
                    "geom": {"x": round(x, 2), "y": round(y - 10, 2)},
                    "meta": {"note": txt},
                    "style": _make_shape_style("#FFFFFF", "#333333"),
                })
                break

    # ── Section headers ──
    for rect_el in root.iter(f"{{{ns}}}rect"):
        cls = rect_el.get("class", "")
        if "journey-section" in cls:
            x, y, w, h = _extract_rect_geom(rect_el)
            fill = _get_fill(rect_el) or "#191970"
            annotations.append({
                "id": next_id(),
                "kind": "group",
                "geom": {"x": x, "y": y, "w": w, "h": h},
                "meta": {"label": ""},
                "style": _make_shape_style(fill, "#666666", "#FFFFFF"),
            })

    # Collect section labels
    section_anns = [a for a in annotations if a["kind"] == "group"]
    sec_idx = 0
    for el in root.iter():
        tag = _strip_ns(el.tag, ns)
        cls = el.get("class", "")
        if tag == "text" and "journey-section" in cls:
            txt = _text_from_el(el)
            if sec_idx < len(section_anns):
                section_anns[sec_idx]["meta"]["label"] = txt
            sec_idx += 1

    # Also check foreignObject for section labels
    if sec_idx == 0:
        for el in root.iter(f"{{{ns}}}foreignObject"):
            parent = None
            # Walk up via iteration to find parent
            pass  # foreignObject text handled via _extract_text

        # Try extracting from switch/foreignObject inside <g> containing journey-section rect
        sec_idx2 = 0
        for g in root.iter(f"{{{ns}}}g"):
            has_section = False
            for r in g:
                tag = _strip_ns(r.tag, ns)
                if tag == "rect" and "journey-section" in r.get("class", ""):
                    has_section = True
                    break
            if has_section:
                txt = _extract_text(g, ns)
                if txt and sec_idx2 < len(section_anns):
                    section_anns[sec_idx2]["meta"]["label"] = txt
                sec_idx2 += 1

    # ── Task rects ──
    for el in root.iter(f"{{{ns}}}rect"):
        cls = el.get("class", "")
        if cls and "task " in cls and "journey-section" not in cls:
            x, y, w, h = _extract_rect_geom(el)
            fill = _get_fill(el) or "#191970"
            annotations.append({
                "id": next_id(),
                "kind": "roundedrect",
                "geom": {"x": x, "y": y, "w": w, "h": h},
                "meta": {"label": ""},
                "style": _make_shape_style(fill, "#666666", "#FFFFFF"),
            })

    # Collect task labels from foreignObject or text
    task_anns = [a for a in annotations if a["kind"] == "roundedrect"]
    task_idx = 0
    for g in root.iter(f"{{{ns}}}g"):
        # Check if this group has a task rect
        has_task = False
        for child in g:
            tag = _strip_ns(child.tag, ns)
            cls = child.get("class", "")
            if tag == "rect" and "task " in cls and "journey-section" not in cls:
                has_task = True
                break
        if has_task:
            txt = _extract_text(g, ns)
            if txt and task_idx < len(task_anns):
                task_anns[task_idx]["meta"]["label"] = txt
            task_idx += 1

    return annotations


def _parse_zenuml(root: ET.Element, ns: str) -> List[Dict[str, Any]]:
    """Parse a Mermaid ZenUML diagram SVG.

    ZenUML diagrams are primarily HTML/CSS inside ``<foreignObject>``,
    with minimal SVG geometry. This parser extracts what it can from
    the XHTML structure.
    """
    annotations: List[Dict[str, Any]] = []
    next_id = _make_id_gen()

    # Get canvas dimensions from viewBox as fallback for percentage values
    viewbox = root.get("viewBox", "").split()
    vb_w = float(viewbox[2]) if len(viewbox) >= 3 else 800.0
    vb_h = float(viewbox[3]) if len(viewbox) >= 4 else 600.0

    def _safe_dim(val: str, fallback: float) -> float:
        """Parse a dimension, falling back if it's a percentage or invalid."""
        if not val or val.endswith("%"):
            return fallback
        try:
            return float(val)
        except ValueError:
            return fallback

    # ZenUML wraps everything in foreignObject with HTML
    for fo in root.iter(f"{{{ns}}}foreignObject"):
        fo_x = _safe_dim(fo.get("x", "0"), 0.0)
        fo_y = _safe_dim(fo.get("y", "0"), 0.0)
        fo_w = _safe_dim(fo.get("width", ""), vb_w)
        fo_h = _safe_dim(fo.get("height", ""), vb_h)

        # Create a single bounding annotation for the whole diagram
        annotations.append({
            "id": next_id(),
            "kind": "rect",
            "geom": {"x": round(fo_x, 2), "y": round(fo_y, 2),
                     "w": round(fo_w, 2), "h": round(fo_h, 2)},
            "meta": {"label": "ZenUML Diagram"},
            "style": _make_shape_style("#FFFFFF", "#999999"),
        })

        # Try to extract participant names from XHTML
        for el in fo.iter():
            tag_local = el.tag.split("}")[-1] if "}" in el.tag else el.tag
            cls = el.get("class", "")
            if "participant" in cls and tag_local == "div":
                # Look for label text inside
                for child in el.iter():
                    child_tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                    if child_tag == "label" or child_tag == "span":
                        txt = (child.text or "").strip()
                        if txt:
                            annotations.append({
                                "id": next_id(),
                                "kind": "text",
                                "geom": {"x": round(fo_x + 10, 2),
                                         "y": round(fo_y + 10, 2)},
                                "meta": {"note": txt},
                                "style": _make_shape_style("#FFFFFF", "#333333"),
                            })
                            break

        break  # only process first foreignObject

    return annotations


# ═══════════════════════════════════════════════════════════
# Dispatch table (must be after all parser functions)
# ═══════════════════════════════════════════════════════════

_DIAGRAM_PARSERS: Dict[str, Any] = {
    "flowchart-v2": _parse_flowchart,
    "flowchart": _parse_flowchart,
    "stateDiagram": _parse_state,
    "class": _parse_class,
    "er": _parse_er,
    "requirement": _parse_requirement,
    "mindmap": _parse_mindmap,
    "block": _parse_block,
    "sankey": _parse_sankey,
    "kanban": _parse_kanban,
    "architecture": _parse_architecture,
    "c4": _parse_c4,
    "sequence": _parse_sequence,
    "gantt": _parse_gantt,
    "packet": _parse_packet,
    "timeline": _parse_timeline,
    "pie": _parse_pie,
    "xychart": _parse_xychart,
    "quadrantChart": _parse_quadrant,
    "gitGraph": _parse_gitgraph,
    "journey": _parse_journey,
    "zenuml": _parse_zenuml,
}
