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

    if not points:
        return (0.0, 0.0, 0.0, 0.0)

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    return (min_x, min_y, max_x - min_x, max_y - min_y)


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
    title_pos: Optional[Dict[str, float]] = None

    for g in root.iter(f"{{{ns}}}g"):
        cls = g.get("class", "")

        if cls == "entity":
            qname = g.get("data-qualified-name", "")
            ent_id = g.get("id", "")
            alias = qname.rsplit(".", 1)[-1] if "." in qname else qname
            if not alias:
                continue

            id_to_alias[ent_id] = alias

            rect = g.find(f"{{{ns}}}rect")
            if rect is not None:
                positions[alias] = {
                    "x": float(rect.get("x", 0)),
                    "y": float(rect.get("y", 0)),
                    "w": float(rect.get("width", 0)),
                    "h": float(rect.get("height", 0)),
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

            id_to_alias[ent_id] = alias

            path_el = g.find(f"{{{ns}}}path")
            if path_el is not None:
                d = path_el.get("d", "")
                x, y, w, h = _path_bbox(d)
                pos_entry: Dict[str, Any] = {"x": x, "y": y, "w": w, "h": h}
                rel_pts = _path_points(d)
                if rel_pts:
                    pos_entry["points"] = rel_pts
                positions[alias] = pos_entry
                fill = path_el.get("fill", "")
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
                    "x": tx,
                    "y": round(ty - font_size, 1),
                    "w": round(text_len, 1),
                    "h": round(font_size * 1.5, 1),
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

        svg_links.append({
            "src": src_alias,
            "dst": dst_alias,
            "label": label,
            "style": style,
        })

    return {
        "canvas_w": canvas_w,
        "canvas_h": canvas_h,
        "positions": positions,
        "elements": svg_elements,
        "links": svg_links,
        "id_to_alias": id_to_alias,
        "title_pos": title_pos,
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
                "x": round(cx - shape_w / 2, 1),
                "y": round(cy - shape_h_local / 2, 1),
                "w": round(shape_w, 1),
                "h": round(shape_h_local, 1),
            }

    return positions


# ───────────────────────────────────────────────
# Annotation builder
# ───────────────────────────────────────────────

def _build_annotations(
    elements: List[Dict[str, Any]],
    connections: List[Dict[str, Any]],
    positions: Dict[str, Dict[str, float]],
) -> List[Dict[str, Any]]:
    """Build PictoSync annotation records from parsed elements and connections.

    Args:
        elements: Parsed element dicts.
        connections: Parsed connection dicts.
        positions: Layout positions from _auto_layout or SVG.

    Returns:
        List of annotation dicts ready for PictoSync JSON.
    """
    annotations: List[Dict[str, Any]] = []
    counter = 1

    for elem in elements:
        alias = elem["alias"]
        pos = positions.get(alias)
        if pos is None:
            continue

        kind = _KIND_MAP.get(elem["puml_type"], "rect")
        ann_id = f"p{counter:06d}"
        counter += 1

        label = elem["label"]
        tech = elem.get("tech", "")
        note = elem.get("note", "")

        # Build display text
        text_parts = [label]
        if tech:
            text_parts.append(f"[{tech}]")
        text = " ".join(text_parts)

        # Build style from color
        color = elem.get("color")
        style: Dict[str, Any] = {
            "pen": {"color": "#555555", "width": 2, "dash": "solid"},
            "fill": {"color": "#00000000"},
            "text": {"color": "#000000", "size_pt": 12.0},
        }
        if color:
            normalized = _normalize_color(color)
            style["fill"]["color"] = normalized

        ann: Dict[str, Any] = {
            "id": ann_id,
            "kind": kind,
            "meta": {
                "kind": kind,
                "label": label,
                "tech": tech,
                "note": note,
            },
            "style": style,
            "text": text,
        }

        if kind == "text":
            ann["geom"] = {
                "x": pos["x"],
                "y": pos["y"],
                "w": pos["w"],
                "h": pos["h"],
            }
        elif kind == "cylinder":
            ann["geom"] = {
                "x": pos["x"],
                "y": pos["y"],
                "w": pos["w"],
                "h": pos["h"],
                "adjust1": 0.2,
            }
        elif kind == "polygon":
            geom: Dict[str, Any] = {
                "x": pos["x"],
                "y": pos["y"],
                "w": pos["w"],
                "h": pos["h"],
            }
            if "points" in pos:
                geom["points"] = pos["points"]
            ann["geom"] = geom
        else:
            ann["geom"] = {
                "x": pos["x"],
                "y": pos["y"],
                "w": pos["w"],
                "h": pos["h"],
            }

        annotations.append(ann)

    # Build line annotations from connections
    alias_to_pos = positions

    for conn in connections:
        src_pos = alias_to_pos.get(conn["src"])
        dst_pos = alias_to_pos.get(conn["dst"])
        if not src_pos or not dst_pos:
            continue

        ann_id = f"p{counter:06d}"
        counter += 1

        # Compute line endpoints from shape centers
        x1 = round(src_pos["x"] + src_pos["w"] / 2, 1)
        y1 = round(src_pos["y"] + src_pos["h"] / 2, 1)
        x2 = round(dst_pos["x"] + dst_pos["w"] / 2, 1)
        y2 = round(dst_pos["y"] + dst_pos["h"] / 2, 1)

        label = conn.get("label", "")
        dashed = conn.get("dashed", False)
        color = conn.get("color")

        pen_color = _normalize_color(color) if color else "#808080"
        dash = "dash" if dashed else "solid"

        style: Dict[str, Any] = {
            "pen": {"color": pen_color, "width": 2, "dash": dash},
            "arrow": "end",
            "text": {"color": pen_color, "size_pt": 10},
        }

        ann: Dict[str, Any] = {
            "id": ann_id,
            "kind": "line",
            "geom": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
            "meta": {
                "kind": "line",
                "label": label,
                "tech": "",
                "note": label,
            },
            "style": style,
            "text": label,
        }

        annotations.append(ann)

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

        # Add SVG-only links not found by the text regex
        for key, svg_link in svg_link_map.items():
            if key not in text_conn_keys:
                conn: Dict[str, Any] = {
                    "src": svg_link["src"],
                    "dst": svg_link["dst"],
                    "label": svg_link.get("label", ""),
                    "dashed": False,
                    "color": None,
                }
                _apply_svg_link_style(conn, svg_link["style"])
                connections.append(conn)
    else:
        positions = _auto_layout(elements, connections, canvas_w, canvas_h)

    annotations = _build_annotations(elements, connections, positions)

    return {
        "version": "draft-1",
        "image": {
            "width": canvas_w,
            "height": canvas_h,
        },
        "annotations": annotations,
    }
