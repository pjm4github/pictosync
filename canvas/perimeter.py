"""
canvas/perimeter.py

Perimeter point computation for all porteable shape types.

Uses a path-length percentage parameter *t* (0.0–1.0) to identify
positions on a shape's perimeter.  t=0 starts at the first vertex
(or 0° for ellipses) and increases clockwise around the perimeter.

Convention for vertex ordering (polygon-based shapes):
  First vertex is top-left, vertices proceed clockwise.

For ellipses, t=0 corresponds to the rightmost point (3 o'clock)
and increases clockwise.
"""

from __future__ import annotations

import math
from typing import List, Tuple

from PyQt6.QtCore import QPointF


# ── Low-level geometry helpers ──

def _seg_length(x1: float, y1: float, x2: float, y2: float) -> float:
    """Euclidean distance between two points."""
    return math.hypot(x2 - x1, y2 - y1)


def _point_at_t_on_polygon(vertices: List[Tuple[float, float]], t: float) -> QPointF:
    """Find the point at fraction *t* (0–1) of a closed polygon's perimeter.

    Args:
        vertices: Ordered polygon vertices (closed automatically).
        t: Fraction of total perimeter length (0.0–1.0).

    Returns:
        QPointF on the perimeter.
    """
    n = len(vertices)
    if n == 0:
        return QPointF(0, 0)
    if n == 1:
        return QPointF(vertices[0][0], vertices[0][1])

    # Compute cumulative edge lengths
    edge_lengths: List[float] = []
    total = 0.0
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        ln = _seg_length(x1, y1, x2, y2)
        edge_lengths.append(ln)
        total += ln

    if total < 1e-9:
        return QPointF(vertices[0][0], vertices[0][1])

    t = t % 1.0  # wrap around
    target = t * total

    cumulative = 0.0
    for i in range(n):
        seg_len = edge_lengths[i]
        if cumulative + seg_len >= target - 1e-9:
            # Point is on this edge
            remainder = target - cumulative
            frac = remainder / seg_len if seg_len > 1e-9 else 0.0
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % n]
            return QPointF(x1 + frac * (x2 - x1), y1 + frac * (y2 - y1))
        cumulative += seg_len

    # Fallback: return last vertex
    return QPointF(vertices[-1][0], vertices[-1][1])


def _t_from_point_on_polygon(vertices: List[Tuple[float, float]],
                             px: float, py: float) -> float:
    """Find the t value (0–1) of the closest perimeter point to (px, py).

    Projects the point onto each edge and returns the t corresponding
    to the nearest projection.
    """
    n = len(vertices)
    if n < 2:
        return 0.0

    # Compute cumulative edge lengths and total
    edge_lengths: List[float] = []
    total = 0.0
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        ln = _seg_length(x1, y1, x2, y2)
        edge_lengths.append(ln)
        total += ln

    if total < 1e-9:
        return 0.0

    best_dist_sq = float("inf")
    best_t = 0.0
    cumulative = 0.0

    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        seg_len = edge_lengths[i]

        if seg_len < 1e-9:
            # Zero-length edge, check vertex distance
            d = (px - x1) ** 2 + (py - y1) ** 2
            if d < best_dist_sq:
                best_dist_sq = d
                best_t = cumulative / total
            cumulative += seg_len
            continue

        # Project point onto segment
        dx, dy = x2 - x1, y2 - y1
        s = ((px - x1) * dx + (py - y1) * dy) / (seg_len * seg_len)
        s = max(0.0, min(1.0, s))

        proj_x = x1 + s * dx
        proj_y = y1 + s * dy
        d = (px - proj_x) ** 2 + (py - proj_y) ** 2

        if d < best_dist_sq:
            best_dist_sq = d
            best_t = (cumulative + s * seg_len) / total

        cumulative += seg_len

    return best_t


def _outward_angle_on_polygon(vertices: List[Tuple[float, float]], t: float) -> float:
    """Return the outward normal angle (degrees, 0=right clockwise) at position t.

    The outward normal is perpendicular to the edge, pointing away from
    the polygon interior (assumed convex, vertices clockwise).
    """
    n = len(vertices)
    if n < 2:
        return 0.0

    edge_lengths: List[float] = []
    total = 0.0
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        ln = _seg_length(x1, y1, x2, y2)
        edge_lengths.append(ln)
        total += ln

    if total < 1e-9:
        return 0.0

    target = (t % 1.0) * total
    cumulative = 0.0
    for i in range(n):
        if cumulative + edge_lengths[i] >= target - 1e-9:
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % n]
            dx, dy = x2 - x1, y2 - y1
            # Edge direction angle
            edge_angle = math.atan2(dy, dx)
            # Outward normal: rotate edge direction −90° (clockwise vertices, y-down)
            normal = edge_angle - math.pi / 2
            return math.degrees(normal) % 360
        cumulative += edge_lengths[i]

    return 0.0


# ── Ellipse helpers (sampled arc-length) ──

_ELLIPSE_SAMPLES = 128  # Number of sample points for arc-length approximation


def _ellipse_point_at_t(w: float, h: float, t: float) -> QPointF:
    """Point at fraction t (0–1) of ellipse perimeter arc length.

    t=0 is rightmost point (3 o'clock), increases clockwise.
    """
    cx, cy = w / 2, h / 2
    rx, ry = w / 2, h / 2
    if rx < 1e-6 or ry < 1e-6:
        return QPointF(cx, cy)

    # Sample arc lengths
    N = _ELLIPSE_SAMPLES
    angles = [2 * math.pi * i / N for i in range(N + 1)]
    points = [(cx + rx * math.cos(a), cy + ry * math.sin(a)) for a in angles]
    cum_lengths = [0.0]
    for i in range(1, N + 1):
        cum_lengths.append(cum_lengths[-1] + _seg_length(
            points[i - 1][0], points[i - 1][1], points[i][0], points[i][1]))

    total = cum_lengths[-1]
    target = (t % 1.0) * total

    # Binary search for the segment
    lo, hi = 0, N
    while lo < hi:
        mid = (lo + hi) // 2
        if cum_lengths[mid + 1] < target:
            lo = mid + 1
        else:
            hi = mid

    seg_start = cum_lengths[lo]
    seg_end = cum_lengths[lo + 1]
    seg_len = seg_end - seg_start
    frac = (target - seg_start) / seg_len if seg_len > 1e-9 else 0.0

    # Interpolate angle
    a1 = angles[lo]
    a2 = angles[lo + 1]
    a = a1 + frac * (a2 - a1)
    return QPointF(cx + rx * math.cos(a), cy + ry * math.sin(a))


def _ellipse_t_from_point(w: float, h: float, px: float, py: float) -> float:
    """Find t (0–1) for closest perimeter point to (px, py) on ellipse.

    Uses closest-point search over sampled perimeter points, then
    refines within the winning segment for sub-sample accuracy.
    """
    cx, cy = w / 2, h / 2
    rx, ry = w / 2, h / 2
    if rx < 1e-6 or ry < 1e-6:
        return 0.0

    N = _ELLIPSE_SAMPLES
    angles = [2 * math.pi * i / N for i in range(N + 1)]
    points = [(cx + rx * math.cos(a), cy + ry * math.sin(a)) for a in angles]
    cum_lengths = [0.0]
    for i in range(1, N + 1):
        cum_lengths.append(cum_lengths[-1] + _seg_length(
            points[i - 1][0], points[i - 1][1], points[i][0], points[i][1]))
    total = cum_lengths[-1]
    if total < 1e-9:
        return 0.0

    # Find the closest sample point
    best_i = 0
    best_d2 = float('inf')
    for i in range(N + 1):
        dx = points[i][0] - px
        dy = points[i][1] - py
        d2 = dx * dx + dy * dy
        if d2 < best_d2:
            best_d2 = d2
            best_i = i

    # Refine: check the two adjacent segments and find closest point on each
    best_t = cum_lengths[best_i] / total

    for seg_i in (best_i - 1, best_i):
        if seg_i < 0 or seg_i >= N:
            continue
        x1, y1 = points[seg_i]
        x2, y2 = points[seg_i + 1]
        # Project (px, py) onto segment [p1, p2]
        sdx, sdy = x2 - x1, y2 - y1
        seg_len2 = sdx * sdx + sdy * sdy
        if seg_len2 < 1e-12:
            continue
        frac = max(0.0, min(1.0,
            ((px - x1) * sdx + (py - y1) * sdy) / seg_len2))
        proj_x = x1 + frac * sdx
        proj_y = y1 + frac * sdy
        d2 = (proj_x - px) ** 2 + (proj_y - py) ** 2
        if d2 < best_d2:
            best_d2 = d2
            arc_at = cum_lengths[seg_i] + frac * (cum_lengths[seg_i + 1] - cum_lengths[seg_i])
            best_t = arc_at / total

    return best_t % 1.0


def _ellipse_outward_angle(w: float, h: float, t: float) -> float:
    """Outward normal angle at t on ellipse perimeter."""
    cx, cy = w / 2, h / 2
    pt = _ellipse_point_at_t(w, h, t)
    # Outward direction from center
    return math.degrees(math.atan2(pt.y() - cy, pt.x() - cx)) % 360


# ── Vertex lists for each shape kind ──

def _rect_vertices(w: float, h: float) -> List[Tuple[float, float]]:
    return [(w, 0), (w, h), (0, h), (0, 0)]


_CORNER_ARC_SAMPLES = 8  # Points per quarter-circle corner arc


def _roundedrect_vertices(w: float, h: float, radius: float) -> List[Tuple[float, float]]:
    """Rounded rectangle outline, wound clockwise in screen coords (y-down).

    Traces: top-right corner arc → right edge → bottom-right arc →
    bottom edge → bottom-left arc → left edge → top-left arc → top edge.

    Args:
        radius: Corner radius in pixels (clamped to half of min dimension).
    """
    r = min(radius, w / 2, h / 2)
    if r < 0.5:
        return _rect_vertices(w, h)

    verts: List[Tuple[float, float]] = []
    N = _CORNER_ARC_SAMPLES

    # Top-right corner: center (w-r, r), angles -π/2 → 0
    cx, cy = w - r, r
    for i in range(N + 1):
        a = -math.pi / 2 + (math.pi / 2) * i / N
        verts.append((cx + r * math.cos(a), cy + r * math.sin(a)))

    # Bottom-right corner: center (w-r, h-r), angles 0 → π/2
    cx, cy = w - r, h - r
    for i in range(N + 1):
        a = (math.pi / 2) * i / N
        verts.append((cx + r * math.cos(a), cy + r * math.sin(a)))

    # Bottom-left corner: center (r, h-r), angles π/2 → π
    cx, cy = r, h - r
    for i in range(N + 1):
        a = math.pi / 2 + (math.pi / 2) * i / N
        verts.append((cx + r * math.cos(a), cy + r * math.sin(a)))

    # Top-left corner: center (r, r), angles π → 3π/2
    cx, cy = r, r
    for i in range(N + 1):
        a = math.pi + (math.pi / 2) * i / N
        verts.append((cx + r * math.cos(a), cy + r * math.sin(a)))

    return verts


def _hexagon_vertices(w: float, h: float, indent: float) -> List[Tuple[float, float]]:
    cy = h / 2
    return [
        (indent, 0),
        (w - indent, 0),
        (w, cy),
        (w - indent, h),
        (indent, h),
        (0, cy),
    ]


def _blockarrow_vertices(w: float, h: float,
                         adjust1: float, adjust2: float) -> List[Tuple[float, float]]:
    """Block arrow vertices.

    Args:
        adjust1: Shaft height ratio (0–1). shaft_margin = h * (1 - adjust1) / 2.
        adjust2: Head length in pixels (distance from tip to head base).
    """
    shaft_margin = h * (1 - adjust1) / 2
    shaft_top = shaft_margin
    shaft_bot = h - shaft_margin
    head_x = w - adjust2
    return [
        (0, shaft_top),
        (head_x, shaft_top),
        (head_x, 0),
        (w, h / 2),
        (head_x, h),
        (head_x, shaft_bot),
        (0, shaft_bot),
    ]


def _polygon_vertices_from_rel(rel_points: List[Tuple[float, float]],
                                w: float, h: float) -> List[Tuple[float, float]]:
    return [(rx * w, ry * h) for rx, ry in rel_points]


def _ensure_cw_screen(verts: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """Ensure vertices are clockwise in screen coords (y-down).

    All shape vertex functions use CW screen winding so that the −90°
    rotation in ``_outward_angle_on_polygon`` yields outward normals.
    User-drawn polygons may have arbitrary winding; this normalises them.

    Uses the shoelace trapezoid sum ``Σ(x₁−x₀)(y₁+y₀) = −2A`` where *A*
    is the standard signed area.  Positive sum ⟹ CCW screen ⟹ reverse.
    """
    n = len(verts)
    if n < 3:
        return verts
    signed_area = 0.0
    for i in range(n):
        x0, y0 = verts[i]
        x1, y1 = verts[(i + 1) % n]
        signed_area += (x1 - x0) * (y1 + y0)
    if signed_area > 0:  # CCW in screen coords → reverse to CW
        return list(reversed(verts))
    return verts


_CYLINDER_ARC_SAMPLES = 32  # Points per half-ellipse arc


def _cylinder_vertices(w: float, h: float, cap_ratio: float) -> List[Tuple[float, float]]:
    """Outer silhouette of a cylinder, wound clockwise in screen coordinates (y-down).

    Clockwise order:
      1. Start at top-right (w, cap_h)
      2. Right side line down to (w, h−cap_h)
      3. Bottom outer arc: right → bottom → left  (angles 0 → π)
      4. Left side line up to (0, cap_h)
      5. Top outer arc: left → top → right  (angles −π → 0)
      6. Close back to (w, cap_h)

    Args:
        cap_ratio: Fraction of height used for cap (adjust1).
    """
    cap_h = h * cap_ratio
    rx = w / 2
    ry = cap_h
    cx = w / 2

    verts: List[Tuple[float, float]] = []
    N = _CYLINDER_ARC_SAMPLES

    # 1–2. Start at top-right, right side down is implicit
    #      (close segment from last point back to first handles this)

    # 3. Bottom outer arc: right(0) → bottom(π/2) → left(π)
    bot_cy = h - cap_h
    for i in range(N + 1):
        a = math.pi * i / N  # 0 → π
        verts.append((cx + rx * math.cos(a), bot_cy + ry * math.sin(a)))

    # 4. Left side line up: (0, h−cap_h) → (0, cap_h) [implicit from last point]

    # 5. Top outer arc: left(−π) → top(−π/2) → right(0)
    for i in range(N + 1):
        a = -math.pi + math.pi * i / N  # −π → 0
        verts.append((cx + rx * math.cos(a), cap_h + ry * math.sin(a)))

    # 6. Right side down: (w, cap_h) → (w, h−cap_h) [implicit close]
    return verts


def _isocube_silhouette(w: float, h: float, depth: float,
                        angle_deg: float) -> List[Tuple[float, float]]:
    """Outer silhouette (convex hull) of an isometric cube.

    Computes all 8 corner points (front + back faces) and returns
    their convex hull as clockwise-ordered vertices.

    Args:
        depth: Effective extrusion depth in pixels (adjust1, clamped).
        angle_deg: Extrusion angle in degrees (adjust2). 0=up, CW positive.
    """
    rad = math.radians(angle_deg)
    dx = -depth * math.sin(rad)
    dy = depth * math.cos(rad)
    adx, ady = abs(dx), abs(dy)
    fw = max(1, w - adx)
    fh = max(1, h - ady)
    fx = adx if dx < 0 else 0
    fy = ady if dy < 0 else 0
    fx = max(0, min(fx, w - fw))
    fy = max(0, min(fy, h - fh))

    # Front corners
    corners = [
        (fx, fy), (fx + fw, fy), (fx + fw, fy + fh), (fx, fy + fh),
    ]
    # Back corners
    corners += [
        (fx + dx, fy + dy), (fx + fw + dx, fy + dy),
        (fx + fw + dx, fy + fh + dy), (fx + dx, fy + fh + dy),
    ]

    return _convex_hull(corners)


def _convex_hull(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """Compute convex hull of 2D points, returned in CCW order (screen coords, y-down).

    Uses Andrew's monotone chain algorithm.
    """
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    # Build lower hull
    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    # Build upper hull
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    hull = lower[:-1] + upper[:-1]
    # Andrew's gives CCW in screen coords (y-down), which matches
    # the −90° outward normal convention used by all other shapes.
    return hull


# ── Public API ──

PORTEABLE_KINDS = frozenset({
    "rect", "roundedrect", "ellipse", "hexagon", "cylinder",
    "blockarrow", "isocube", "polygon", "seqblock",
})


def _get_item_dims(item) -> Tuple[float, float]:
    """Read width/height from an item, with fallback to rect()."""
    w = getattr(item, '_width', 0)
    h = getattr(item, '_height', 0)
    if (w == 0 or h == 0) and hasattr(item, 'rect') and callable(item.rect):
        r = item.rect()
        w, h = r.width(), r.height()
    return w, h


def _get_vertices_for_kind(kind: str, item) -> List[Tuple[float, float]] | None:
    """Return ordered vertices for polygon-based shapes, or None for ellipse."""
    w, h = _get_item_dims(item)

    if kind == "ellipse":
        return None  # Ellipse uses special handling

    if kind == "hexagon":
        indent_ratio = getattr(item, '_adjust1', 0.2)
        indent = w * indent_ratio
        return _hexagon_vertices(w, h, indent)

    if kind == "blockarrow":
        adjust1 = getattr(item, '_adjust1', 0.6)
        adjust2 = getattr(item, '_adjust2', w * 0.3)
        return _blockarrow_vertices(w, h, adjust1, adjust2)

    if kind == "cylinder":
        cap_ratio = getattr(item, '_adjust1', 0.15)
        return _cylinder_vertices(w, h, cap_ratio)

    if kind == "isocube":
        depth = getattr(item, '_adjust1', 0)
        angle_deg = getattr(item, '_adjust2', 0)
        if depth < 0.5:
            return _rect_vertices(w, h)
        # Use effective depth (clamped to fit bounding box)
        if hasattr(item, '_effective_depth'):
            depth = item._effective_depth()
        return _isocube_silhouette(w, h, depth, angle_deg)

    if kind == "polygon":
        pts = getattr(item, '_rel_points', [])
        if len(pts) < 3:
            return _rect_vertices(w, h)
        return _ensure_cw_screen(_polygon_vertices_from_rel(pts, w, h))

    if kind == "roundedrect":
        radius = getattr(item, '_adjust1', 10)
        return _roundedrect_vertices(w, h, radius)

    # rect, seqblock → plain rect vertices
    return _rect_vertices(w, h)


def perimeter_point(kind: str, item, t: float) -> QPointF:
    """Compute the perimeter point for a given item kind.

    Args:
        kind: The item's KIND string.
        item: The parent graphics item (used to read geometry).
        t: Position on perimeter as fraction of path length (0.0–1.0).

    Returns:
        QPointF in the parent's local coordinate space.
    """
    w, h = _get_item_dims(item)

    if kind == "ellipse":
        return _ellipse_point_at_t(w, h, t)

    verts = _get_vertices_for_kind(kind, item)
    if verts:
        return _point_at_t_on_polygon(verts, t)

    return QPointF(w / 2, h / 2)


def t_from_local_point(kind: str, item, lx: float, ly: float) -> float:
    """Find t (0.0–1.0) for the closest perimeter point to local coords (lx, ly).

    Args:
        kind: The item's KIND string.
        item: The parent graphics item.
        lx: Local x coordinate.
        ly: Local y coordinate.

    Returns:
        Fraction of perimeter path length (0.0–1.0).
    """
    w, h = _get_item_dims(item)

    if kind == "ellipse":
        return _ellipse_t_from_point(w, h, lx, ly)

    verts = _get_vertices_for_kind(kind, item)
    if verts:
        return _t_from_point_on_polygon(verts, lx, ly)

    return 0.0


def outward_normal_angle(kind: str, item, t: float) -> float:
    """Return the outward normal angle (degrees) at position t on the perimeter.

    0=right, 90=down, 180=left, 270=up (clockwise convention).
    """
    w, h = _get_item_dims(item)

    if kind == "ellipse":
        return _ellipse_outward_angle(w, h, t)

    verts = _get_vertices_for_kind(kind, item)
    if verts:
        return _outward_angle_on_polygon(verts, t)

    return 0.0
