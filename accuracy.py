"""
accuracy.py

Measure how well an extracted PictoSync annotation set matches the original
image it was extracted from, with NO human-labelled ground truth. The source
image itself is the reference: a good extraction puts its shape outlines on the
image's real edges and gives each shape the colour that actually sits under it.

The measure is deliberately *decomposed and signed* so a future optimiser can do
gradient descent on it:

  * Four component scores -- ``rect``, ``line``, ``text``, ``color`` -- each with
    an absolute error in ``[0, 1]`` (0 = perfect) AND a *direction*: the signed
    nudge that would reduce that error. For geometry that direction is a pixel
    vector ``(dx, dy)`` (and per shape), pointing the way the shape should move
    to land on the nearest real edge; for colour it is a signed RGB delta; for
    text it is a signed count delta (negative = text is missing).
  * One ``composite`` accuracy in ``[0, 1]`` (higher = better), the
    weight-averaged complement of the component errors over whatever components
    could be measured (text is skipped if the Tesseract binary is absent).

How geometry is scored (no ground truth needed): the original image is reduced
to a Canny edge map; its distance transform ``dt`` gives, at every pixel, the
distance to the nearest real edge. Each predicted shape outline is rasterised;
the mean of ``dt`` under that outline is the shape's chamfer error (how far it
floats off real structure), and ``-grad(dt)`` averaged under the outline is the
direction to move it back onto structure. Colour is the mean original pixel
under each shape's (rotated) fill mask versus the declared fill colour.

Run standalone:
    python accuracy.py <result.json> <image.png> [--overlay out.png]
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

try:  # OpenCV is a project dependency; guard anyway for a clearer message.
    import cv2
except Exception as _exc:  # pragma: no cover - import guard
    raise ImportError(
        "accuracy.py needs OpenCV (opencv-python). pip install opencv-python"
    ) from _exc

from PIL import Image

_BOX_KINDS = {"rect", "roundedrect", "ellipse", "hexagon", "cylinder",
              "blockarrow", "polygon", "text"}

# Default component weights (renormalised over whatever is actually measured).
_DEFAULT_WEIGHTS = {"rect": 0.35, "line": 0.25, "text": 0.20, "color": 0.20}


# --------------------------------------------------------------------------- #
# Result types
# --------------------------------------------------------------------------- #
@dataclass
class ComponentScore:
    """One accuracy dimension.

    Attributes:
        name: "rect" | "line" | "text" | "color".
        error: Absolute error in [0, 1] (0 = perfect, 1 = worst).
        accuracy: ``1 - error`` for convenience.
        direction: Signed "which way to improve" hint. A ``(dx, dy)`` pixel
            vector for geometry, an ``(dr, dg, db)`` tuple for colour, a single
            signed number for text (count delta). Empty when not applicable.
        n: How many items fed this score.
        available: False when the dimension could not be measured (e.g. no OCR).
        detail: Free-form extras (per-shape nudges, counts, notes).
    """
    name: str
    error: float = 0.0
    accuracy: float = 1.0
    direction: Tuple[float, ...] = ()
    n: int = 0
    available: bool = True
    detail: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccuracyReport:
    """Full comparison of one extraction against its source image."""
    composite: float
    components: Dict[str, ComponentScore]
    image_size: Tuple[int, int]
    weights: Dict[str, float]
    notes: List[str] = field(default_factory=list)

    def summary(self) -> str:
        """Return a short human-readable multi-line summary."""
        lines = [
            f"Composite accuracy: {self.composite * 100:.1f}%  "
            f"(image {self.image_size[0]}x{self.image_size[1]})",
        ]
        for key in ("rect", "line", "text", "color"):
            c = self.components.get(key)
            if c is None:
                continue
            if not c.available:
                lines.append(f"  {key:<6} n/a  ({c.detail.get('reason', 'unavailable')})")
                continue
            dir_txt = ""
            if c.direction:
                if key == "color":
                    dr, dg, db = c.direction
                    dir_txt = f"  move fill by RGB({dr:+.0f},{dg:+.0f},{db:+.0f})"
                elif key == "text":
                    dir_txt = f"  count delta {c.direction[0]:+.0f}"
                else:
                    dx, dy = c.direction
                    dir_txt = f"  shift ({dx:+.1f},{dy:+.1f}) px"
            lines.append(
                f"  {key:<6} {c.accuracy * 100:5.1f}%  (err {c.error:.3f}, n={c.n}){dir_txt}"
            )
        for note in self.notes:
            lines.append(f"  note: {note}")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """JSON-serialisable view (for logging / the future optimiser)."""
        return {
            "composite": round(self.composite, 4),
            "image_size": list(self.image_size),
            "weights": self.weights,
            "components": {
                k: {
                    "error": round(c.error, 4),
                    "accuracy": round(c.accuracy, 4),
                    "direction": [round(float(v), 3) for v in c.direction],
                    "n": c.n,
                    "available": c.available,
                    "detail": c.detail,
                }
                for k, c in self.components.items()
            },
            "notes": self.notes,
        }


# --------------------------------------------------------------------------- #
# Geometry helpers
# --------------------------------------------------------------------------- #
def _num(v: Any) -> Optional[float]:
    try:
        if isinstance(v, bool):
            return None
        return float(v)
    except (TypeError, ValueError):
        return None


def _rotated_box_corners(x: float, y: float, w: float, h: float,
                         angle_deg: float) -> List[Tuple[float, float]]:
    """Corners of a box rotated CLOCKWISE about its centre (screen y-down).

    Matches PictoSync rendering: angle is degrees clockwise about the centre of
    the upright ``(x, y, w, h)`` box.
    """
    cx, cy = x + w / 2.0, y + h / 2.0
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    corners = []
    for px, py in ((x, y), (x + w, y), (x + w, y + h), (x, y + h)):
        ox, oy = px - cx, py - cy
        # Clockwise rotation in a y-down coordinate frame.
        rx = ox * ca - oy * sa
        ry = ox * sa + oy * ca
        corners.append((cx + rx, cy + ry))
    return corners


def _shape_polygon(ann: Dict[str, Any]) -> Optional[np.ndarray]:
    """Outline polygon (Nx2 int array) for a box-like shape, else None."""
    geom = ann.get("geom") or {}
    x, y = _num(geom.get("x")), _num(geom.get("y"))
    w, h = _num(geom.get("w")), _num(geom.get("h"))
    if None in (x, y, w, h) or w <= 0 or h <= 0:
        return None
    angle = _num(geom.get("angle")) or 0.0
    pts = _rotated_box_corners(x, y, w, h, angle)
    return np.array([[int(round(px)), int(round(py))] for px, py in pts],
                    dtype=np.int32)


def _line_points(ann: Dict[str, Any]) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
    geom = ann.get("geom") or {}
    x1, y1 = _num(geom.get("x1")), _num(geom.get("y1"))
    x2, y2 = _num(geom.get("x2")), _num(geom.get("y2"))
    if None in (x1, y1, x2, y2):
        return None
    return (int(round(x1)), int(round(y1))), (int(round(x2)), int(round(y2)))


def _parse_hex(color: Any) -> Optional[Tuple[int, int, int]]:
    """Parse ``#RRGGBB`` / ``#RRGGBBAA`` into an ``(r, g, b)`` tuple."""
    if not isinstance(color, str):
        return None
    s = color.strip().lstrip("#")
    if len(s) in (6, 8):
        try:
            return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
        except ValueError:
            return None
    return None


# --------------------------------------------------------------------------- #
# Core measurement
# --------------------------------------------------------------------------- #
def _edge_distance_field(gray: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Canny edges + distance transform and its gradient.

    Returns:
        ``(edges, dt, gx, gy)`` where ``dt[p]`` is the distance from pixel *p*
        to the nearest edge, and ``(gx, gy) = grad(dt)`` points *away* from the
        nearest edge (so ``-(gx, gy)`` points toward it).
    """
    # Auto thresholds from the median (robust across drawings/photos).
    med = float(np.median(gray))
    lo = int(max(0, 0.66 * med))
    hi = int(min(255, 1.33 * med))
    if hi <= lo:
        lo, hi = 50, 150
    edges = cv2.Canny(gray, lo, hi)
    inv = np.where(edges > 0, 0, 255).astype(np.uint8)
    dt = cv2.distanceTransform(inv, cv2.DIST_L2, 3).astype(np.float32)
    gx = cv2.Sobel(dt, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(dt, cv2.CV_32F, 0, 1, ksize=3)
    return edges, dt, gx, gy


def _score_mask(mask: np.ndarray, dt: np.ndarray, gx: np.ndarray,
                gy: np.ndarray, tol: float) -> Tuple[float, Tuple[float, float], int]:
    """Chamfer error + toward-edge nudge for the pixels set in ``mask``."""
    ys, xs = np.nonzero(mask)
    if xs.size == 0:
        return 0.0, (0.0, 0.0), 0
    d = dt[ys, xs]
    mean_d = float(d.mean())
    error = float(min(1.0, mean_d / tol)) if tol > 0 else 0.0
    # -grad(dt) points toward the nearest real edge: the direction to move.
    ndx = float(-gx[ys, xs].mean())
    ndy = float(-gy[ys, xs].mean())
    return error, (ndx, ndy), int(xs.size)


def _geometry_component(name: str, masks: List[Tuple[Any, np.ndarray]],
                        dt: np.ndarray, gx: np.ndarray, gy: np.ndarray,
                        tol: float) -> ComponentScore:
    """Build a rect/line component from per-shape outline masks."""
    if not masks:
        return ComponentScore(name=name, error=0.0, accuracy=1.0, n=0,
                              available=True,
                              detail={"reason": f"no {name} shapes to score"})
    errors: List[float] = []
    all_px = np.zeros_like(dt, dtype=bool)
    per_shape: List[Dict[str, Any]] = []
    for ident, mask in masks:
        err, nudge, npx = _score_mask(mask, dt, gx, gy, tol)
        if npx == 0:
            continue
        errors.append(err)
        all_px |= mask.astype(bool)
        per_shape.append({
            "id": ident,
            "error": round(err, 4),
            "nudge": [round(nudge[0], 2), round(nudge[1], 2)],
        })
    if not errors:
        return ComponentScore(name=name, n=0, available=True,
                              detail={"reason": f"{name} shapes had no pixels"})
    # Aggregate direction = toward-edge nudge over all outline pixels.
    _, agg_dir, _ = _score_mask(all_px, dt, gx, gy, tol)
    mean_err = float(np.mean(errors))
    return ComponentScore(
        name=name,
        error=mean_err,
        accuracy=1.0 - mean_err,
        direction=agg_dir,
        n=len(errors),
        detail={"per_shape": per_shape},
    )


def _color_component(anns: List[Dict[str, Any]], rgb: np.ndarray) -> ComponentScore:
    """Compare each shape's declared fill to the mean image pixel under it."""
    h, w = rgb.shape[:2]
    diffs: List[float] = []
    signed = np.zeros(3, dtype=np.float64)
    per_shape: List[Dict[str, Any]] = []
    counted = 0
    for ann in anns:
        if ann.get("kind") not in _BOX_KINDS or ann.get("kind") == "text":
            continue
        declared = _parse_hex(((ann.get("style") or {}).get("fill") or {}).get("color"))
        poly = _shape_polygon(ann)
        if declared is None or poly is None:
            continue
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask, [poly], 255)
        ys, xs = np.nonzero(mask)
        if xs.size == 0:
            continue
        sampled = rgb[ys, xs].mean(axis=0)  # (r, g, b) actual pixels
        decl = np.array(declared, dtype=np.float64)
        # Direction = actual - declared: how to move the declared colour to match.
        delta = sampled - decl
        dist = float(np.linalg.norm(delta)) / (255.0 * math.sqrt(3.0))
        diffs.append(dist)
        signed += delta
        counted += 1
        per_shape.append({
            "id": ann.get("id") or ann.get("meta", {}).get("label") or "",
            "declared": "#%02X%02X%02X" % declared,
            "sampled": "#%02X%02X%02X" % tuple(int(round(v)) for v in sampled),
            "error": round(dist, 4),
        })
    if counted == 0:
        return ComponentScore(name="color", n=0, available=True,
                              detail={"reason": "no filled shapes with a declared colour"})
    mean_err = float(np.mean(diffs))
    mean_signed = tuple((signed / counted).tolist())
    return ComponentScore(
        name="color",
        error=mean_err,
        accuracy=1.0 - mean_err,
        direction=mean_signed,  # (dr, dg, db) to add to declared colours
        n=counted,
        detail={"per_shape": per_shape},
    )


def _predicted_texts(anns: List[Dict[str, Any]]) -> List[str]:
    out: List[str] = []
    for ann in anns:
        for val in (ann.get("text"), (ann.get("meta") or {}).get("label")):
            if isinstance(val, str) and val.strip():
                out.append(val.strip())
    return out


def _text_component(anns: List[Dict[str, Any]], gray: np.ndarray) -> ComponentScore:
    """OCR the image and compare against predicted text (best-effort)."""
    try:
        import pytesseract
        data = pytesseract.image_to_data(
            gray, output_type=pytesseract.Output.DICT)
    except Exception as exc:  # Tesseract binary missing, etc.
        return ComponentScore(
            name="text", available=False,
            detail={"reason": f"OCR unavailable: {type(exc).__name__}: {exc}"})

    ocr_words: List[str] = []
    for txt, conf in zip(data.get("text", []), data.get("conf", [])):
        try:
            c = float(conf)
        except (TypeError, ValueError):
            c = -1.0
        if c >= 50 and isinstance(txt, str) and txt.strip():
            ocr_words.append(txt.strip())

    pred = _predicted_texts(anns)
    pred_blob = " ".join(pred).lower()
    if not ocr_words:
        return ComponentScore(
            name="text", error=0.0, accuracy=1.0, n=0, available=True,
            direction=(float(len(pred)),),
            detail={"reason": "no OCR words detected in the image",
                    "predicted_text_items": len(pred)})

    matched = sum(1 for wrd in ocr_words if wrd.lower() in pred_blob)
    recall = matched / len(ocr_words)
    error = 1.0 - recall
    # Signed count delta: negative => image has text the extraction is missing.
    count_delta = float(len(pred) - len(ocr_words))
    return ComponentScore(
        name="text",
        error=error,
        accuracy=recall,
        direction=(count_delta,),
        n=len(ocr_words),
        detail={
            "ocr_words": len(ocr_words),
            "predicted_text_items": len(pred),
            "matched_words": matched,
            "sample_missing": [w for w in ocr_words if w.lower() not in pred_blob][:12],
        },
    )


def _make_overlay(rgb: np.ndarray, edges: np.ndarray,
                  rect_masks, line_masks) -> np.ndarray:
    """Dim the image, draw real edges green and predicted outlines in colour."""
    base = (rgb.astype(np.float32) * 0.45).astype(np.uint8).copy()
    base[edges > 0] = (0, 180, 0)  # real edges: green
    for _id, m in rect_masks:
        base[m.astype(bool)] = (255, 60, 60)   # predicted rects: red
    for _id, m in line_masks:
        base[m.astype(bool)] = (60, 120, 255)  # predicted lines: blue
    return base


def _load_annotations(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, list):
        anns = data
    elif isinstance(data, dict):
        anns = data.get("annotations") or []
    else:
        anns = []
    return [a for a in anns if isinstance(a, dict)]


def measure_accuracy(data: Any, png_path: str, *,
                     weights: Optional[Dict[str, float]] = None,
                     tolerance_frac: float = 0.012,
                     overlay_path: Optional[str] = None) -> AccuracyReport:
    """Score an extraction against its source image.

    Args:
        data: The parsed extraction (``{"annotations": [...]}`` or a bare list).
            Geometry is coerced to canonical form first, so raw model output is
            accepted too.
        png_path: Path to the original image the extraction came from.
        weights: Optional per-component weights (rect/line/text/color);
            renormalised over the components that could be measured.
        tolerance_frac: Edge-distance that counts as fully wrong, as a fraction
            of the image diagonal (default ~1.2%).
        overlay_path: If set, write a diagnostic overlay PNG there.

    Returns:
        An :class:`AccuracyReport`.
    """
    # Normalise geometry (rot->angle, left/top/right/bottom->x/y/w/h, ...).
    notes: List[str] = []
    try:
        from schema_shim import coerce_annotations
        data, shim_notes = coerce_annotations(
            data if isinstance(data, dict) else {"annotations": _load_annotations(data)})
        if shim_notes:
            notes.extend(shim_notes)
    except Exception as exc:
        notes.append(f"geometry shim skipped: {exc}")

    anns = _load_annotations(data)

    img = Image.open(png_path).convert("RGB")
    rgb = np.array(img)
    h, w = rgb.shape[:2]
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    diag = math.hypot(w, h)
    tol = max(1.0, tolerance_frac * diag)

    edges, dt, gx, gy = _edge_distance_field(gray)

    # Rasterise predicted outlines per category.
    rect_masks: List[Tuple[Any, np.ndarray]] = []
    line_masks: List[Tuple[Any, np.ndarray]] = []
    for ann in anns:
        kind = ann.get("kind")
        ident = ann.get("id") or (ann.get("meta") or {}).get("label") or kind
        if kind == "line":
            lp = _line_points(ann)
            if lp is None:
                continue
            m = np.zeros((h, w), dtype=np.uint8)
            cv2.line(m, lp[0], lp[1], 255, 2)
            line_masks.append((ident, m))
        elif kind in _BOX_KINDS and kind != "text":
            poly = _shape_polygon(ann)
            if poly is None:
                continue
            m = np.zeros((h, w), dtype=np.uint8)
            cv2.polylines(m, [poly], True, 255, 2)
            rect_masks.append((ident, m))

    components: Dict[str, ComponentScore] = {
        "rect": _geometry_component("rect", rect_masks, dt, gx, gy, tol),
        "line": _geometry_component("line", line_masks, dt, gx, gy, tol),
        "color": _color_component(anns, rgb),
        "text": _text_component(anns, gray),
    }

    # Composite: weight-average complement of error over measurable components.
    wts = dict(_DEFAULT_WEIGHTS)
    if weights:
        wts.update(weights)
    usable = {k: c for k, c in components.items() if c.available and c.n > 0}
    if usable:
        total_w = sum(wts.get(k, 0.0) for k in usable) or 1.0
        composite = sum(wts.get(k, 0.0) * components[k].accuracy
                        for k in usable) / total_w
    else:
        composite = 0.0
        notes.append("no component could be measured")

    if overlay_path:
        overlay = _make_overlay(rgb, edges, rect_masks, line_masks)
        Image.fromarray(overlay).save(overlay_path)
        notes.append(f"overlay written to {overlay_path}")

    return AccuracyReport(
        composite=float(composite),
        components=components,
        image_size=(w, h),
        weights={k: wts.get(k, 0.0) for k in components},
        notes=notes,
    )


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _main(argv: Sequence[str]) -> int:
    args = list(argv)
    overlay = None
    if "--overlay" in args:
        i = args.index("--overlay")
        overlay = args[i + 1]
        del args[i:i + 2]
    if len(args) < 2:
        print("usage: python accuracy.py <result.json> <image.png> "
              "[--overlay out.png]", file=sys.stderr)
        return 2
    with open(args[0], "r", encoding="utf-8") as fh:
        data = json.load(fh)
    report = measure_accuracy(data, args[1], overlay_path=overlay)
    print(report.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
