"""
schema_shim.py

A single place that maps the many ways vision models express geometry and
rotation onto PictoSync's canonical annotation schema, so extraction results
translate back consistently no matter which model produced them.

PictoSync canonical geometry (see schemas/annotation_schema.json):
  * Box shapes (rect, roundedrect, ellipse, hexagon, cylinder, blockarrow,
    polygon, text): ``geom = {x, y, w, h[, angle]}`` where x,y is the TOP-LEFT
    of the UNROTATED box, w/h are its side lengths, and ``angle`` is rotation
    in degrees CLOCKWISE about the box CENTRE (0 ≤ angle < 360; omitted at 0).
  * Lines: ``geom = {x1, y1, x2, y2}``.

Models vary a lot. They say ``rot`` / ``rotation`` / ``theta`` for angle,
``width`` / ``height`` for w/h, ``left/top/right/bottom`` or ``cx/cy`` for
position, sometimes nest things under ``bbox`` or put geometry at the top
level. This shim coerces all of those into the canonical form. Apply it to a
parsed extraction result BEFORE schema validation (``validate_and_fix_annotations``)
so correct shapes aren't dropped for "missing w/h".
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

_BOX_KINDS = {"rect", "roundedrect", "ellipse", "hexagon", "cylinder",
              "blockarrow", "polygon", "text"}

# Alias lists are matched case-insensitively. First match wins.
_A_ANGLE = ("angle", "rot", "rotation", "rotation_deg", "rotation_degrees",
            "angle_deg", "rotate", "orientation", "theta", "deg", "heading")
_A_ANGLE_RAD = ("theta_rad", "rotation_rad", "angle_rad", "rot_rad")
_A_W = ("w", "width", "dx", "wd")
_A_H = ("h", "height", "dy", "ht")
_A_X = ("x", "left", "x0", "xmin", "x_min", "left_x", "l")
_A_Y = ("y", "top", "y0", "ymin", "y_min", "top_y", "t")
_A_RIGHT = ("right", "xmax", "x_max", "right_x", "r")
_A_BOTTOM = ("bottom", "ymax", "y_max", "bottom_y", "b")
_A_CX = ("cx", "center_x", "centerx", "centre_x", "cen_x", "xc", "mid_x")
_A_CY = ("cy", "center_y", "centery", "centre_y", "cen_y", "yc", "mid_y")

_A_X1 = ("x1", "x_1", "start_x", "startx", "x0", "sx")
_A_Y1 = ("y1", "y_1", "start_y", "starty", "y0", "sy")
_A_X2 = ("x2", "x_2", "end_x", "endx", "ex")
_A_Y2 = ("y2", "y_2", "end_y", "endy", "ey")

# Geom keys that are NOT position/size and must be carried through untouched.
_PASS_THROUGH = ("adjust1", "adjust2", "adjust3")


def _num(v: Any) -> Optional[float]:
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v.strip())
        except ValueError:
            return None
    return None


def _ci(d: Dict[str, Any]) -> Dict[str, str]:
    """Lowercase-key -> original-key map for case-insensitive lookups."""
    return {str(k).lower(): k for k in d.keys()}


def _first(src: Dict[str, Any], ci: Dict[str, str],
           aliases: Tuple[str, ...]) -> Optional[float]:
    for a in aliases:
        if a in ci:
            val = _num(src.get(ci[a]))
            if val is not None:
                return val
    return None


def _norm_angle(deg: float) -> float:
    a = deg % 360.0
    if a < 0:
        a += 360.0
    return round(a, 2)


def _gather_source(ann: Dict[str, Any]) -> Dict[str, Any]:
    """Collect geometry-ish keys from geom, nested bbox, and the top level."""
    src: Dict[str, Any] = {}
    geom = ann.get("geom")
    if isinstance(geom, dict):
        src.update(geom)
    # Nested bounding-box dicts.
    for bk in ("bbox", "bounds", "box", "rect", "frame"):
        for container in (geom if isinstance(geom, dict) else None, ann):
            if isinstance(container, dict) and isinstance(container.get(bk), dict):
                for k, v in container[bk].items():
                    src.setdefault(k, v)
    # Top-level geometry keys (some models skip the "geom" wrapper).
    _skip = {"geom", "kind", "id", "contents", "meta", "style", "children",
             "text", "dsl", "label", "note", "tech"}
    for k, v in ann.items():
        if k not in _skip and not isinstance(v, (dict, list)):
            src.setdefault(k, v)
    return src


def _coerce_box(src: Dict[str, Any]) -> Tuple[Dict[str, float], List[str]]:
    ci = _ci(src)
    notes: List[str] = []

    w = _first(src, ci, _A_W)
    h = _first(src, ci, _A_H)
    left = _first(src, ci, _A_X)
    top = _first(src, ci, _A_Y)
    right = _first(src, ci, _A_RIGHT)
    bottom = _first(src, ci, _A_BOTTOM)
    cx = _first(src, ci, _A_CX)
    cy = _first(src, ci, _A_CY)

    # Width/height from edges if not given directly.
    if w is None and left is not None and right is not None:
        w = abs(right - left)
        notes.append("derived w from right-left")
    if h is None and top is not None and bottom is not None:
        h = abs(bottom - top)
        notes.append("derived h from bottom-top")

    # Top-left from a centre if that's all we have.
    x = left
    y = top
    if x is None and cx is not None and w is not None:
        x = cx - w / 2.0
        notes.append("derived x from centre")
    if y is None and cy is not None and h is not None:
        y = cy - h / 2.0
        notes.append("derived y from centre")

    out: Dict[str, float] = {}
    if x is not None:
        out["x"] = round(x, 2)
    if y is not None:
        out["y"] = round(y, 2)
    if w is not None:
        out["w"] = round(abs(w), 2)
    if h is not None:
        out["h"] = round(abs(h), 2)

    # Rotation: prefer explicit degrees; fall back to radians.
    ang = _first(src, ci, _A_ANGLE)
    if ang is None:
        rad = _first(src, ci, _A_ANGLE_RAD)
        if rad is not None:
            ang = math.degrees(rad)
            notes.append("converted angle from radians")
    if ang is not None:
        norm = _norm_angle(ang)
        if norm != 0:
            out["angle"] = norm
        if "rot" in ci or any(a in ci for a in _A_ANGLE if a != "angle"):
            if "angle" not in {k.lower() for k in src}:
                notes.append("mapped rotation alias -> angle")

    # Carry through shape-specific tuning params verbatim.
    for key in _PASS_THROUGH:
        if key in ci:
            v = _num(src.get(ci[key]))
            if v is not None:
                out[key] = v
    return out, notes


def _coerce_line(src: Dict[str, Any], ann: Dict[str, Any]) -> Tuple[Dict[str, float], List[str]]:
    ci = _ci(src)
    notes: List[str] = []

    x1 = _first(src, ci, _A_X1)
    y1 = _first(src, ci, _A_Y1)
    x2 = _first(src, ci, _A_X2)
    y2 = _first(src, ci, _A_Y2)

    # start/end point dicts.
    geom = ann.get("geom") if isinstance(ann.get("geom"), dict) else {}
    for d in (geom, ann):
        for sk in ("start", "p1", "from"):
            p = d.get(sk) if isinstance(d, dict) else None
            if isinstance(p, dict):
                x1 = x1 if x1 is not None else _num(p.get("x"))
                y1 = y1 if y1 is not None else _num(p.get("y"))
        for ek in ("end", "p2", "to"):
            p = d.get(ek) if isinstance(d, dict) else None
            if isinstance(p, dict):
                x2 = x2 if x2 is not None else _num(p.get("x"))
                y2 = y2 if y2 is not None else _num(p.get("y"))
        # points list: [[x,y],[x,y]] or [{x,y},{x,y}]
        for pk in ("points", "pts", "path"):
            pts = d.get(pk) if isinstance(d, dict) else None
            if isinstance(pts, list) and len(pts) >= 2:
                a, b = pts[0], pts[-1]
                def _pt(p):
                    if isinstance(p, dict):
                        return _num(p.get("x")), _num(p.get("y"))
                    if isinstance(p, (list, tuple)) and len(p) >= 2:
                        return _num(p[0]), _num(p[1])
                    return None, None
                ax, ay = _pt(a)
                bx, by = _pt(b)
                x1 = x1 if x1 is not None else ax
                y1 = y1 if y1 is not None else ay
                x2 = x2 if x2 is not None else bx
                y2 = y2 if y2 is not None else by

    out: Dict[str, float] = {}
    for k, v in (("x1", x1), ("y1", y1), ("x2", x2), ("y2", y2)):
        if v is not None:
            out[k] = round(v, 2)
    return out, notes


def coerce_annotation(ann: Dict[str, Any]) -> List[str]:
    """Rewrite one annotation's ``geom`` in place to canonical form.

    Args:
        ann: A single annotation dict (mutated in place).

    Returns:
        Human-readable notes about any non-trivial coercions applied.
    """
    if not isinstance(ann, dict):
        return []
    kind = ann.get("kind")
    if kind == "group":
        return []

    src = _gather_source(ann)
    if kind == "line":
        new_geom, notes = _coerce_line(src, ann)
    elif kind in _BOX_KINDS:
        new_geom, notes = _coerce_box(src)
    else:
        return []

    if not new_geom:
        return notes

    # Preserve genuinely unknown geom keys (future-proofing), but drop the
    # alias/structural keys we just consumed so geom isn't left with both
    # "w" and "width", or "angle" and "rot".
    existing = ann.get("geom")
    if isinstance(existing, dict):
        for k, v in existing.items():
            if k.lower() in _CONSUMED_KEYS:
                continue
            new_geom.setdefault(k, v)
    ann["geom"] = new_geom

    # Remove geometry keys/aliases that leaked to the top level so they don't
    # confuse later consumers (geometry lives only under "geom").
    _canonical = {"x", "y", "w", "h", "x1", "y1", "x2", "y2", "angle"}
    for k in list(ann.keys()):
        if k == "geom":
            continue
        if k.lower() in _CONSUMED_KEYS or k.lower() in _canonical:
            ann.pop(k, None)
    return notes


# Every key (alias or structural) the shim reads and therefore replaces with
# canonical fields; these are dropped from the output geom and top level.
_CONSUMED_KEYS = set(
    _A_ANGLE + _A_ANGLE_RAD + _A_W + _A_H + _A_X + _A_Y + _A_RIGHT
    + _A_BOTTOM + _A_CX + _A_CY + _A_X1 + _A_Y1 + _A_X2 + _A_Y2
    + ("start", "end", "p1", "p2", "from", "to", "points", "pts", "path",
       "bbox", "bounds", "box", "rect", "frame")
) - {"x", "y", "w", "h", "x1", "y1", "x2", "y2", "angle"}


def coerce_annotations(data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """Coerce every annotation's geometry/rotation in a parsed result.

    Args:
        data: The parsed extraction dict (``{"annotations": [...]}``), mutated
            in place.

    Returns:
        ``(data, notes)`` where *notes* summarizes coercions (deduplicated with
        counts) for surfacing as extraction warnings.
    """
    if not isinstance(data, dict):
        return data, []
    anns = data.get("annotations")
    if not isinstance(anns, list):
        return data, []
    tally: Dict[str, int] = {}
    for ann in anns:
        for note in coerce_annotation(ann):
            tally[note] = tally.get(note, 0) + 1
    notes = [f"geometry shim: {n} (x{c})" if c > 1 else f"geometry shim: {n}"
             for n, c in tally.items()]
    return data, notes


def snap_angles(data: Dict[str, Any],
                increment: float = 15.0) -> Tuple[Dict[str, Any], List[str]]:
    """Snap every box shape's ``angle`` to the nearest multiple of *increment*.

    Vision models rarely report a clean rotation (e.g. 14.3° where the drawing
    is clearly on a 15° grid). When the domain uses fixed angular steps, snapping
    after extraction is far more reliable than asking the model to be exact.

    Args:
        data: Parsed extraction dict (``{"annotations": [...]}``), mutated in
            place. Geometry should already be canonical (run after
            :func:`coerce_annotations`).
        increment: Degrees between allowed angles (default 15). Values <= 0 are
            a no-op.

    Returns:
        ``(data, notes)`` where *notes* reports how many angles were snapped.
    """
    if increment <= 0 or not isinstance(data, dict):
        return data, []
    anns = data.get("annotations")
    if not isinstance(anns, list):
        return data, []
    snapped = 0
    for ann in anns:
        if not isinstance(ann, dict) or ann.get("kind") not in _BOX_KINDS:
            continue
        geom = ann.get("geom")
        if not isinstance(geom, dict) or "angle" not in geom:
            continue
        ang = _num(geom.get("angle"))
        if ang is None:
            continue
        new = (round(ang / increment) * increment) % 360.0
        if abs(new - (ang % 360.0)) > 1e-6:
            snapped += 1
        if new == 0:
            geom.pop("angle", None)
        else:
            geom["angle"] = round(new, 2)
    notes = ([f"angle snap: {snapped} shape(s) snapped to {increment:g}°"]
             if snapped else [])
    return data, notes
