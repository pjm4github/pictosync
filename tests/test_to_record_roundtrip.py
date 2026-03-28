"""Test to_record → reconstruct round-trip for all item kinds.

For each kind:
  1. Create an item with known parameters
  2. Call to_record() to serialize
  3. Reconstruct a new item from the serialized record
  4. Call to_record() on the new item
  5. Verify the two records match (kind, geom fields, style structure)

This tests the full serialization/deserialization cycle without MainWindow.
"""
from __future__ import annotations

import os
import sys

import pytest




from canvas.items import (
    MetaRectItem,
    MetaRoundedRectItem,
    MetaEllipseItem,
    MetaLineItem,
    MetaTextItem,
    MetaHexagonItem,
    MetaCylinderItem,
    MetaBlockArrowItem,
    MetaPolygonItem,
    MetaCurveItem,
    MetaOrthoCurveItem,
    MetaIsoCubeItem,
    MetaSeqBlockItem,
)
from models import AnnotationMeta


# ── Item creation table ──────────────────────────────────────────────────

def _create_item(kind: str, ann_id: str = "test1"):
    """Create an item of the given kind with representative parameters."""
    factories = {
        "rect": lambda: MetaRectItem(100, 200, 150, 80, ann_id, None),
        "roundedrect": lambda: MetaRoundedRectItem(100, 200, 150, 80, 12, ann_id, None),
        "ellipse": lambda: MetaEllipseItem(100, 200, 150, 80, ann_id, None),
        "hexagon": lambda: MetaHexagonItem(100, 200, 150, 80, 0.25, ann_id, None),
        "cylinder": lambda: MetaCylinderItem(100, 200, 120, 100, 0.15, ann_id, None),
        "blockarrow": lambda: MetaBlockArrowItem(100, 200, 160, 80, 40, 0.5, ann_id, None),
        "isocube": lambda: MetaIsoCubeItem(100, 200, 120, 80, 30, 135, ann_id, None),
        "line": lambda: MetaLineItem(50, 60, 250, 180, ann_id, None),
        "text": lambda: MetaTextItem(100, 200, "Hello World", ann_id, None),
        "polygon": lambda: MetaPolygonItem(100, 200, 120, 100,
                                           [[0, 0], [1, 0], [0.5, 1]], ann_id, None),
        "curve": lambda: MetaCurveItem(100, 200, 150, 100,
                                       [{"cmd": "M", "x": 0.0, "y": 0.0},
                                        {"cmd": "C", "x": 1.0, "y": 1.0,
                                         "c1x": 0.3, "c1y": 0.0,
                                         "c2x": 0.7, "c2y": 1.0}],
                                       ann_id, None),
        "orthocurve": lambda: MetaOrthoCurveItem(100, 200, 150, 80,
                                                  [{"cmd": "M", "x": 0.0, "y": 0.0},
                                                   {"cmd": "H", "x": 1.0},
                                                   {"cmd": "V", "y": 1.0}],
                                                  ann_id, None),
        "seqblock": lambda: MetaSeqBlockItem(100, 200, 200, 150, "alt", ann_id, None),
    }
    return factories[kind]()


def _reconstruct_item(rec: dict, ann_id: str = "test2"):
    """Reconstruct an item from a to_record() dict."""
    kind = rec["kind"]
    g = rec.get("geom", {})
    meta_dict = rec.get("contents") or rec.get("meta") or {}
    meta = AnnotationMeta.from_dict(meta_dict)

    if kind == "rect":
        it = MetaRectItem(float(g["x"]), float(g["y"]),
                          float(g["w"]), float(g["h"]), ann_id, None)
    elif kind == "roundedrect":
        it = MetaRoundedRectItem(float(g["x"]), float(g["y"]),
                                  float(g["w"]), float(g["h"]),
                                  float(g.get("adjust1", 10)), ann_id, None)
    elif kind == "ellipse":
        it = MetaEllipseItem(float(g["x"]), float(g["y"]),
                              float(g["w"]), float(g["h"]), ann_id, None)
    elif kind == "hexagon":
        it = MetaHexagonItem(float(g["x"]), float(g["y"]),
                              float(g["w"]), float(g["h"]),
                              float(g.get("adjust1", 0.25)), ann_id, None)
    elif kind == "cylinder":
        it = MetaCylinderItem(float(g["x"]), float(g["y"]),
                               float(g["w"]), float(g["h"]),
                               float(g.get("adjust1", 0.15)), ann_id, None)
    elif kind == "blockarrow":
        it = MetaBlockArrowItem(float(g["x"]), float(g["y"]),
                                 float(g["w"]), float(g["h"]),
                                 float(g.get("adjust2", 15)),
                                 float(g.get("adjust1", 0.5)),
                                 ann_id, None)
    elif kind == "isocube":
        it = MetaIsoCubeItem(float(g["x"]), float(g["y"]),
                              float(g["w"]), float(g["h"]),
                              float(g.get("adjust1", 30)),
                              float(g.get("adjust2", 135)),
                              ann_id, None)
    elif kind == "line":
        it = MetaLineItem(float(g["x1"]), float(g["y1"]),
                           float(g["x2"]), float(g["y2"]), ann_id, None)
    elif kind == "text":
        text = meta.note or meta.label or ""
        it = MetaTextItem(float(g["x"]), float(g["y"]), text, ann_id, None)
    elif kind == "polygon":
        pts = g.get("points", [[0, 0], [1, 0], [1, 1], [0, 1]])
        it = MetaPolygonItem(float(g["x"]), float(g["y"]),
                              float(g["w"]), float(g["h"]),
                              pts, ann_id, None)
    elif kind == "curve":
        nodes = g.get("nodes", [{"cmd": "M", "x": 0.0, "y": 0.0},
                                 {"cmd": "L", "x": 1.0, "y": 1.0}])
        it = MetaCurveItem(float(g["x"]), float(g["y"]),
                            float(g["w"]), float(g["h"]),
                            nodes, ann_id, None)
    elif kind == "orthocurve":
        nodes = g.get("nodes", [{"cmd": "M", "x": 0.0, "y": 0.0},
                                 {"cmd": "H", "x": 1.0},
                                 {"cmd": "V", "y": 1.0}])
        it = MetaOrthoCurveItem(float(g["x"]), float(g["y"]),
                                 float(g["w"]), float(g["h"]),
                                 nodes, ann_id, None)
    elif kind == "seqblock":
        btype = meta_dict.get("block_type", "alt")
        it = MetaSeqBlockItem(float(g["x"]), float(g["y"]),
                               float(g["w"]), float(g["h"]),
                               btype, ann_id, None)
    else:
        raise ValueError(f"Unknown kind: {kind}")

    it.set_meta(meta)
    it.apply_style_from_record(rec)
    return it


# ── Parametrized kinds ───────────────────────────────────────────────────

ALL_KINDS = [
    "rect", "roundedrect", "ellipse", "hexagon", "cylinder",
    "blockarrow", "isocube", "line", "text", "polygon",
    "curve", "orthocurve", "seqblock",
]


# ── Tests ────────────────────────────────────────────────────────────────

class TestToRecordRoundTrip:
    """Full to_record → reconstruct → to_record cycle."""

    @pytest.mark.parametrize("kind", ALL_KINDS)
    def test_kind_preserved(self, kind):
        item = _create_item(kind)
        rec1 = item.to_record()
        item2 = _reconstruct_item(rec1)
        rec2 = item2.to_record()
        assert rec2["kind"] == kind

    @pytest.mark.parametrize("kind", ALL_KINDS)
    def test_geom_keys_preserved(self, kind):
        """All geom keys from first record appear in second."""
        item = _create_item(kind)
        rec1 = item.to_record()
        item2 = _reconstruct_item(rec1)
        rec2 = item2.to_record()
        g1_keys = set(rec1["geom"].keys())
        g2_keys = set(rec2["geom"].keys())
        # Geom keys should match (except angle which may be added/omitted if 0)
        missing = g1_keys - g2_keys - {"angle"}
        assert not missing, f"Missing geom keys in round-trip: {missing}"

    @pytest.mark.parametrize("kind", ALL_KINDS)
    def test_geom_scalar_values_close(self, kind):
        """Scalar geom values should be approximately equal after round-trip."""
        item = _create_item(kind)
        rec1 = item.to_record()
        item2 = _reconstruct_item(rec1)
        rec2 = item2.to_record()
        for key in rec1["geom"]:
            v1 = rec1["geom"][key]
            if isinstance(v1, (int, float)):
                v2 = rec2["geom"].get(key)
                assert v2 is not None, f"geom[{key!r}] missing in round-trip"
                assert abs(v1 - v2) < 0.1, \
                    f"geom[{key!r}] changed: {v1} → {v2}"

    @pytest.mark.parametrize("kind", ALL_KINDS)
    def test_style_pen_preserved(self, kind):
        """style.pen.color and style.pen.width preserved."""
        item = _create_item(kind)
        rec1 = item.to_record()
        item2 = _reconstruct_item(rec1)
        rec2 = item2.to_record()
        p1 = rec1.get("style", {}).get("pen", {})
        p2 = rec2.get("style", {}).get("pen", {})
        assert p1.get("color") == p2.get("color"), \
            f"pen.color changed: {p1.get('color')} → {p2.get('color')}"
        assert p1.get("width") == p2.get("width"), \
            f"pen.width changed: {p1.get('width')} → {p2.get('width')}"

    @pytest.mark.parametrize("kind", ALL_KINDS)
    def test_style_fill_preserved(self, kind):
        """style.fill.color preserved."""
        item = _create_item(kind)
        rec1 = item.to_record()
        item2 = _reconstruct_item(rec1)
        rec2 = item2.to_record()
        f1 = rec1.get("style", {}).get("fill", {}).get("color", "")
        f2 = rec2.get("style", {}).get("fill", {}).get("color", "")
        assert f1 == f2, f"fill.color changed: {f1} → {f2}"

    @pytest.mark.parametrize("kind", ALL_KINDS)
    def test_has_contents_or_meta(self, kind):
        """Record has contents or meta key after round-trip."""
        item = _create_item(kind)
        rec1 = item.to_record()
        item2 = _reconstruct_item(rec1)
        rec2 = item2.to_record()
        assert "contents" in rec2 or "meta" in rec2


class TestGeomSpecificRoundTrip:
    """Kind-specific geom field round-trips."""

    def test_line_endpoints(self):
        item = _create_item("line")
        rec1 = item.to_record()
        item2 = _reconstruct_item(rec1)
        rec2 = item2.to_record()
        for key in ("x1", "y1", "x2", "y2"):
            assert abs(rec1["geom"][key] - rec2["geom"][key]) < 0.1

    def test_polygon_points_count(self):
        item = _create_item("polygon")
        rec1 = item.to_record()
        item2 = _reconstruct_item(rec1)
        rec2 = item2.to_record()
        assert len(rec1["geom"]["points"]) == len(rec2["geom"]["points"])

    def test_polygon_points_values(self):
        item = _create_item("polygon")
        rec1 = item.to_record()
        item2 = _reconstruct_item(rec1)
        rec2 = item2.to_record()
        for p1, p2 in zip(rec1["geom"]["points"], rec2["geom"]["points"]):
            assert abs(p1[0] - p2[0]) < 0.001
            assert abs(p1[1] - p2[1]) < 0.001

    def test_curve_nodes_count(self):
        item = _create_item("curve")
        rec1 = item.to_record()
        item2 = _reconstruct_item(rec1)
        rec2 = item2.to_record()
        assert len(rec1["geom"]["nodes"]) == len(rec2["geom"]["nodes"])

    def test_curve_node_cmds(self):
        item = _create_item("curve")
        rec1 = item.to_record()
        item2 = _reconstruct_item(rec1)
        rec2 = item2.to_record()
        cmds1 = [n["cmd"] for n in rec1["geom"]["nodes"]]
        cmds2 = [n["cmd"] for n in rec2["geom"]["nodes"]]
        assert cmds1 == cmds2

    def test_orthocurve_nodes_count(self):
        item = _create_item("orthocurve")
        rec1 = item.to_record()
        item2 = _reconstruct_item(rec1)
        rec2 = item2.to_record()
        assert len(rec1["geom"]["nodes"]) == len(rec2["geom"]["nodes"])

    def test_isocube_adjust_values(self):
        item = _create_item("isocube")
        rec1 = item.to_record()
        item2 = _reconstruct_item(rec1)
        rec2 = item2.to_record()
        assert abs(rec1["geom"]["adjust1"] - rec2["geom"]["adjust1"]) < 0.1
        assert abs(rec1["geom"]["adjust2"] - rec2["geom"]["adjust2"]) < 0.1

    def test_roundedrect_adjust1(self):
        item = _create_item("roundedrect")
        rec1 = item.to_record()
        item2 = _reconstruct_item(rec1)
        rec2 = item2.to_record()
        assert abs(rec1["geom"]["adjust1"] - rec2["geom"]["adjust1"]) < 0.1

    def test_seqblock_adjust1_present(self):
        """alt seqblock has adjust1 (1 divider)."""
        item = _create_item("seqblock")
        rec1 = item.to_record()
        assert "adjust1" in rec1["geom"]


class TestPolygonCurveRoundTrip:
    """Polygon with curve vertices survives full round-trip."""

    def test_cubic_polygon_round_trip(self):
        pts = [
            [0.0, 0.5],
            [0.5, 0.0, "C", 0.1, 0.1, 0.4, 0.1],
            [1.0, 0.5, "C", 0.6, 0.1, 0.9, 0.1],
            [0.5, 1.0, "C", 0.9, 0.9, 0.6, 0.9],
            [0.0, 0.5, "C", 0.4, 0.9, 0.1, 0.9],
        ]
        item = MetaPolygonItem(100, 100, 200, 200, pts, "cpoly", None)
        rec1 = item.to_record()
        item2 = _reconstruct_item(rec1, ann_id="cpoly2")
        rec2 = item2.to_record()
        pts1 = rec1["geom"]["points"]
        pts2 = rec2["geom"]["points"]
        assert len(pts1) == len(pts2)
        for p1, p2 in zip(pts1, pts2):
            assert len(p1) == len(p2), f"Point length mismatch: {len(p1)} vs {len(p2)}"
            if len(p1) >= 7:
                assert p2[2] == "C"
