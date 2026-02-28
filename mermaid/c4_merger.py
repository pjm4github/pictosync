"""
mermaid/c4_merger.py

Step 2 of the two-step C4 pipeline: merge source-parsed semantic data
with SVG-parsed geometry to produce enriched PictoSync annotations.

Pipeline:
    1.  ``c4_source_parser.parse_c4_source()``  →  semantic data
    2.  This module scans the SVG for geometry and matches it to step 1
        by label text, producing annotations that carry **both** the rich
        source metadata (alias, c4_type, tech, descr, parent_boundary)
        *and* the pixel-accurate geometry from the rendered SVG.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple

from plantuml.parser import (
    _make_line_style,
    _normalize_annotations,
    _SVG_NS,
)

from models import resolve_kind_alias
from mermaid.c4_source_parser import C4ParseResult, C4Rel, C4Shape
from mermaid.parser import (
    _extract_rect_geom,
    _find_groups_by_class,
    _get_fill,
    _get_stroke,
    _make_id_gen,
    _make_shape_style,
    _robust_path_bbox,
    _strip_ns,
    _text_from_el,
    _apply_viewbox_offset,
)


def _make_dsl_c4(**fields: Any) -> Dict[str, Any]:
    """Build a ``meta.dsl`` dict for C4 domain annotations.

    Filters out falsy values so the output stays compact.
    """
    c4 = {k: v for k, v in fields.items() if v}
    return {"tool": "mermaid", "c4": c4}


# ═══════════════════════════════════════════════════════════
# SVG geometry extraction (shapes, boundaries, connections)
# ═══════════════════════════════════════════════════════════


def _extract_svg_shapes(
    root: ET.Element, ns: str,
) -> List[Dict[str, Any]]:
    """Extract C4 shape geometry and text from ``<g class="person-man">`` groups.

    Returns a list of dicts, each with keys:
        ``label``, ``stereotype``, ``tech``, ``note``,
        ``x``, ``y``, ``w``, ``h``, ``kind``, ``fill``, ``stroke``.
    """
    shapes: List[Dict[str, Any]] = []

    for g in _find_groups_by_class(root, ns, "person-man"):
        # ── Geometry ──
        rect_el = g.find(f"{{{ns}}}rect")
        if rect_el is not None:
            x, y, w, h = _extract_rect_geom(rect_el)
            fill = _get_fill(rect_el) or "#08427B"
            stroke = _get_stroke(rect_el) or "#073B6F"
            kind = "roundedrect"
        else:
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
            kind = "curve"  # default for path-based; refined below

        # ── Text classification ──
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
                continue
            if not labels:
                labels.append(txt)
            else:
                notes.append(txt)

        # Refine kind from stereotype via alias map
        if stereotype:
            resolved = resolve_kind_alias(stereotype)
            if resolved:
                kind = resolved

        shapes.append({
            "label": labels[0] if labels else "",
            "stereotype": stereotype,
            "tech": tech,
            "note": " ".join(notes),
            "x": x, "y": y, "w": w, "h": h,
            "kind": kind, "fill": fill, "stroke": stroke,
        })

    return shapes


def _extract_svg_boundaries(
    root: ET.Element, ns: str,
) -> List[Dict[str, Any]]:
    """Extract C4 boundary rectangles from unnamed ``<g>`` groups.

    Boundaries are unnamed groups containing a single ``<rect>`` (no lines)
    plus text elements showing ``label`` and ``[type]``.

    Returns a list of dicts with keys:
        ``label``, ``boundary_type``, ``x``, ``y``, ``w``, ``h``.
    """
    boundaries: List[Dict[str, Any]] = []

    for el in root:
        tag = _strip_ns(el.tag, ns)
        if tag != "g":
            continue
        cls = el.get("class", "")
        if cls:
            continue  # named group — skip

        rects = list(el.iter(f"{{{ns}}}rect"))
        lines = list(el.iter(f"{{{ns}}}line"))
        if not rects or lines:
            continue  # not a boundary (has lines = rels group)

        # Extract text
        label = ""
        btype = ""
        for t_el in el.iter(f"{{{ns}}}text"):
            txt = _text_from_el(t_el)
            if not txt:
                continue
            if txt.startswith("[") and txt.endswith("]"):
                btype = txt[1:-1].strip()
            elif not label:
                label = txt

        r = rects[0]
        x, y, w, h = _extract_rect_geom(r)
        boundaries.append({
            "label": label,
            "boundary_type": btype,
            "x": x, "y": y, "w": w, "h": h,
        })

    return boundaries


def _extract_svg_connections(
    root: ET.Element, ns: str,
) -> List[Dict[str, Any]]:
    """Extract C4 relationship lines/paths and their associated text labels.

    Walks direct children of unnamed ``<g>`` groups in DOM order.
    In Mermaid C4 SVGs the pattern is::

        <line .../>          ← segment 1
        <text>Uses</text>    ← label for segment 1
        <path .../>          ← segment 2
        <text>Uses</text>    ← label for segment 2
        <path .../>          ← segment 3
        <text>Sends</text>   ← label for segment 3
        <text>[SMTP]</text>  ← tech for segment 3
        ...

    Each ``<line>`` or arrow-``<path>`` starts a new connection.  The
    ``<text>`` elements that follow (before the next segment) are its
    label and optional ``[tech]``.

    Returns a list of dicts with keys:
        ``x1``, ``y1``, ``x2``, ``y2``, ``label``, ``tech``,
        ``stroke``, ``arrow``.
    """
    connections: List[Dict[str, Any]] = []

    for el in root:
        tag = _strip_ns(el.tag, ns)
        if tag != "g":
            if tag == "line":
                connections.append(_line_to_dict(el))
            continue
        cls = el.get("class", "")
        if cls:
            continue  # named group — skip

        # Check if this unnamed group is a rels group
        has_segment = False
        for child in el:
            ctag = _strip_ns(child.tag, ns)
            if ctag == "line" or (
                ctag == "path" and _is_arrow_path(child)
            ):
                has_segment = True
                break
        if not has_segment:
            continue

        # Walk children in DOM order, grouping segment + following texts
        current_conn: Optional[Dict[str, Any]] = None
        for child in el:
            ctag = _strip_ns(child.tag, ns)

            if ctag == "line":
                # Flush previous connection
                if current_conn is not None:
                    connections.append(current_conn)
                current_conn = _line_to_dict(child)

            elif ctag == "path" and _is_arrow_path(child):
                # Arrow path — new connection segment
                if current_conn is not None:
                    connections.append(current_conn)
                current_conn = _path_to_line_dict(child)
                if current_conn is not None:
                    # Detect arrow direction from markers
                    if child.get("marker-start", ""):
                        current_conn["arrow"] = "start"
                    elif child.get("marker-end", ""):
                        current_conn["arrow"] = "end"

            elif ctag == "text" and current_conn is not None:
                txt = _text_from_el(child)
                if not txt:
                    continue
                if txt.startswith("[") and txt.endswith("]"):
                    current_conn["tech"] = txt[1:-1].strip()
                elif not current_conn.get("label"):
                    current_conn["label"] = txt

        # Flush last connection
        if current_conn is not None:
            connections.append(current_conn)

    return connections


def _is_arrow_path(el: ET.Element) -> bool:
    """Check if a ``<path>`` element is a connection arrow (has any marker)."""
    return bool(el.get("marker-end", "") or el.get("marker-start", ""))


def _line_to_dict(el: ET.Element) -> Dict[str, Any]:
    """Convert a ``<line>`` SVG element to a connection dict."""
    marker = el.get("marker-end", "")
    return {
        "x1": round(float(el.get("x1", "0")), 2),
        "y1": round(float(el.get("y1", "0")), 2),
        "x2": round(float(el.get("x2", "0")), 2),
        "y2": round(float(el.get("y2", "0")), 2),
        "label": "",
        "tech": "",
        "stroke": el.get("stroke", "#444444"),
        "arrow": "end" if marker else "none",
    }


def _path_to_line_dict(el: ET.Element) -> Optional[Dict[str, Any]]:
    """Convert a ``<path>`` SVG element to a connection dict using start/end points.

    Extracts the first ``M`` point as the start and walks the path commands
    to find the final current-point as the end.
    """
    d = el.get("d", "")
    if not d:
        return None

    # Extract start and end points by walking the path
    start, end = _path_endpoints(d)
    if start is None:
        return None

    marker = el.get("marker-end", "")
    stroke = _get_stroke(el) or "#444444"
    return {
        "x1": round(start[0], 2),
        "y1": round(start[1], 2),
        "x2": round(end[0], 2),
        "y2": round(end[1], 2),
        "label": "",
        "tech": "",
        "stroke": stroke,
        "arrow": "end" if marker else "none",
    }


def _path_endpoints(
    d: str,
) -> Tuple[Optional[Tuple[float, float]], Tuple[float, float]]:
    """Extract the start and end points of an SVG path.

    Walks path commands (absolute and relative) to track the current point.

    Returns:
        ``(start_point, end_point)`` where each is ``(x, y)`` or
        ``(None, (0,0))`` if the path is empty.
    """
    import re as _re
    tokens = _re.findall(
        r'[MmLlHhVvCcSsQqTtAaZz]|[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', d,
    )
    if not tokens:
        return None, (0.0, 0.0)

    cx, cy = 0.0, 0.0
    sx, sy = 0.0, 0.0
    start: Optional[Tuple[float, float]] = None
    i = 0

    def _nf() -> float:
        nonlocal i
        i += 1
        return float(tokens[i]) if i < len(tokens) else 0.0

    while i < len(tokens):
        cmd = tokens[i]
        if cmd == 'M':
            cx, cy = _nf(), _nf()
            sx, sy = cx, cy
            if start is None:
                start = (cx, cy)
        elif cmd == 'm':
            cx += _nf(); cy += _nf()
            sx, sy = cx, cy
            if start is None:
                start = (cx, cy)
        elif cmd == 'L':
            cx, cy = _nf(), _nf()
        elif cmd == 'l':
            cx += _nf(); cy += _nf()
        elif cmd == 'H':
            cx = _nf()
        elif cmd == 'h':
            cx += _nf()
        elif cmd == 'V':
            cy = _nf()
        elif cmd == 'v':
            cy += _nf()
        elif cmd in ('C', 'S', 'Q'):
            n = 3 if cmd == 'C' else 2
            for _ in range(n):
                cx, cy = _nf(), _nf()
        elif cmd in ('c', 's', 'q'):
            n = 3 if cmd == 'c' else 2
            for _ in range(n):
                dx, dy = _nf(), _nf()
            cx += dx; cy += dy  # type: ignore[possibly-undefined]
        elif cmd == 'T':
            cx, cy = _nf(), _nf()
        elif cmd == 't':
            cx += _nf(); cy += _nf()
        elif cmd in ('A', 'a'):
            for _ in range(5):
                _nf()
            if cmd == 'A':
                cx, cy = _nf(), _nf()
            else:
                cx += _nf(); cy += _nf()
        elif cmd in ('Z', 'z'):
            cx, cy = sx, sy
        i += 1

    return start, (cx, cy)


# ═══════════════════════════════════════════════════════════
# Label-based matching
# ═══════════════════════════════════════════════════════════

def _normalize_label(label: str) -> str:
    """Normalize a label for fuzzy matching (lowercase, collapse whitespace)."""
    return " ".join(label.lower().split())


def _match_shapes(
    source_shapes: List[C4Shape],
    svg_shapes: List[Dict[str, Any]],
) -> List[Tuple[Dict[str, Any], Optional[C4Shape]]]:
    """Match SVG shapes to source shapes by label text.

    Returns a list of ``(svg_shape, source_shape_or_None)`` tuples,
    one per SVG shape.  Source shapes are matched greedily — first
    exact match wins, then normalized match.
    """
    # Build lookup: normalized_label → list of source shapes
    source_by_label: Dict[str, List[C4Shape]] = {}
    for s in source_shapes:
        key = _normalize_label(s.label)
        source_by_label.setdefault(key, []).append(s)

    results: List[Tuple[Dict[str, Any], Optional[C4Shape]]] = []
    used: set = set()

    for svg_s in svg_shapes:
        key = _normalize_label(svg_s["label"])
        match: Optional[C4Shape] = None
        candidates = source_by_label.get(key, [])
        for c in candidates:
            if id(c) not in used:
                match = c
                used.add(id(c))
                break
        results.append((svg_s, match))

    return results


def _match_rels(
    source_rels: List[C4Rel],
    svg_connections: List[Dict[str, Any]],
) -> List[Tuple[Dict[str, Any], Optional[C4Rel]]]:
    """Match SVG connections to source relationships by label text.

    Returns ``(svg_conn, source_rel_or_None)`` tuples.
    """
    source_by_label: Dict[str, List[C4Rel]] = {}
    for r in source_rels:
        key = _normalize_label(r.label)
        source_by_label.setdefault(key, []).append(r)

    results: List[Tuple[Dict[str, Any], Optional[C4Rel]]] = []
    used: set = set()

    for conn in svg_connections:
        key = _normalize_label(conn.get("label", ""))
        match: Optional[C4Rel] = None
        candidates = source_by_label.get(key, [])
        for c in candidates:
            if id(c) not in used:
                match = c
                used.add(id(c))
                break
        results.append((conn, match))

    return results


# ═══════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════


def merge_c4_source_with_svg(
    source: C4ParseResult,
    svg_path: str,
) -> Dict[str, Any]:
    """Merge C4 source-parsed data with SVG geometry into annotation JSON.

    This is the **step 2** entry point.  It:

    1. Parses the SVG for shape geometry, boundary rectangles, and
       connection lines.
    2. Matches SVG shapes to source shapes by label text.
    3. Produces enriched annotations with source metadata (alias,
       c4_type, tech, description, parent_boundary) and SVG geometry.
    4. Adds boundary annotations (dashed rectangles from the SVG).
    5. Enriches relationship annotations with source rel data.

    Args:
        source: Result from ``parse_c4_source()`` / ``parse_c4_source_file()``.
        svg_path: Path to the Mermaid-rendered SVG file.

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

    # ── Extract SVG geometry ──
    svg_shapes = _extract_svg_shapes(root, ns)
    svg_boundaries = _extract_svg_boundaries(root, ns)
    svg_connections = _extract_svg_connections(root, ns)

    # ── Match to source data ──
    shape_pairs = _match_shapes(source.shapes, svg_shapes)
    rel_pairs = _match_rels(source.rels, svg_connections)

    # ── Build annotations ──
    annotations: List[Dict[str, Any]] = []
    next_id = _make_id_gen()

    # ── Shapes ──
    for svg_s, src_s in shape_pairs:
        meta: Dict[str, Any] = {"label": svg_s["label"]}

        if src_s is not None:
            # Enrich with source data
            if src_s.tech:
                meta["tech"] = src_s.tech
            elif svg_s["tech"]:
                meta["tech"] = svg_s["tech"]
            if src_s.descr:
                meta["note"] = src_s.descr
            elif svg_s["note"]:
                meta["note"] = svg_s["note"]
            parent = (
                src_s.parent_boundary
                if src_s.parent_boundary != "global" else ""
            )
            meta["dsl"] = _make_dsl_c4(
                type=src_s.c4_type,
                alias=src_s.alias,
                parent=parent,
            )
        else:
            # Fallback to SVG-only data
            if svg_s["tech"]:
                meta["tech"] = svg_s["tech"]
            if svg_s["note"]:
                meta["note"] = svg_s["note"]
            if svg_s["stereotype"]:
                meta["dsl"] = _make_dsl_c4(type=svg_s["stereotype"])

        # Determine kind: prefer source c4_type mapping, then SVG-detected
        kind = svg_s["kind"]
        c4_type = src_s.c4_type if src_s else svg_s.get("stereotype", "")
        if c4_type:
            resolved = resolve_kind_alias(c4_type)
            if resolved:
                kind = resolved

        annotations.append({
            "id": next_id(),
            "kind": kind,
            "geom": {
                "x": svg_s["x"], "y": svg_s["y"],
                "w": svg_s["w"], "h": svg_s["h"],
            },
            "meta": meta,
            "style": _make_shape_style(
                svg_s["fill"], svg_s["stroke"], "#FFFFFF",
            ),
        })

    # ── Boundaries ──
    # Match SVG boundaries to source boundaries by label
    source_bnd_by_label: Dict[str, Any] = {}
    for b in source.boundaries:
        key = _normalize_label(b.label)
        source_bnd_by_label.setdefault(key, []).append(b)
    bnd_used: set = set()

    for svg_b in svg_boundaries:
        key = _normalize_label(svg_b["label"])
        src_b = None
        for c in source_bnd_by_label.get(key, []):
            if id(c) not in bnd_used:
                src_b = c
                bnd_used.add(id(c))
                break

        meta: Dict[str, Any] = {"label": svg_b["label"]}
        if src_b is not None:
            parent = (
                src_b.parent_boundary
                if src_b.parent_boundary != "global" else ""
            )
            meta["dsl"] = _make_dsl_c4(
                type="boundary",
                alias=src_b.alias,
                boundary_type=src_b.boundary_type,
                parent=parent,
            )
        else:
            if svg_b["boundary_type"]:
                meta["dsl"] = _make_dsl_c4(
                    type="boundary",
                    boundary_type=svg_b["boundary_type"],
                )

        annotations.append({
            "id": next_id(),
            "kind": "rect",
            "geom": {
                "x": svg_b["x"], "y": svg_b["y"],
                "w": svg_b["w"], "h": svg_b["h"],
            },
            "meta": meta,
            "style": {
                "pen": {
                    "color": "#444444", "width": 1, "dash": "dashed",
                    "dash_pattern_length": 30, "dash_solid_percent": 50,
                },
                "fill": {"color": "none"},
                "text": {"color": "#444444", "size_pt": 10.0},
            },
        })

    # ── Relationships ──
    for svg_c, src_r in rel_pairs:
        meta: Dict[str, Any] = {}
        if src_r is not None:
            meta["label"] = src_r.label
            if src_r.tech:
                meta["tech"] = src_r.tech
            elif svg_c.get("tech"):
                meta["tech"] = svg_c["tech"]
            if src_r.descr:
                meta["note"] = src_r.descr
            meta["dsl"] = _make_dsl_c4(
                rel_type=src_r.rel_type,
                **{"from": src_r.from_alias, "to": src_r.to_alias},
            )
        else:
            meta["label"] = svg_c.get("label", "")
            if svg_c.get("tech"):
                meta["tech"] = svg_c["tech"]

        stroke = svg_c.get("stroke", "#444444")
        arrow = svg_c.get("arrow", "end")
        annotations.append({
            "id": next_id(),
            "kind": "line",
            "geom": {
                "x1": svg_c["x1"], "y1": svg_c["y1"],
                "x2": svg_c["x2"], "y2": svg_c["y2"],
            },
            "meta": meta,
            "style": _make_line_style(stroke, 1, False, arrow),
        })

    # ── Apply viewBox offset ──
    if vb_x != 0.0 or vb_y != 0.0:
        _apply_viewbox_offset(annotations, vb_x, vb_y)

    # ── Normalize and return ──
    _normalize_annotations(annotations)
    return {
        "version": "draft-1",
        "image": {"width": canvas_w, "height": canvas_h},
        "annotations": annotations,
    }
