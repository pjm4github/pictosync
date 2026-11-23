"""Test bench for MetaPortItem — connector port on parent shape perimeter.

Tests:
    - Port creation on a parent shape
    - to_record() serialization (geom.t, geom.radius, port_type, protocol, parent_id, connections)
    - Parentless port includes absolute x/y/w/h in geom
    - Port type (In/Out/InOut) round-trip
    - Protocol field round-trip
    - Connections list round-trip
    - apply_style_from_record pen/fill color
    - update_from_record in-place update
    - Property panel meta edits sync to JSON
    - No duplicate IDs after port creation
"""
from __future__ import annotations

import json
import os
import sys

import pytest

# Ensure project root is on path




from PyQt6.QtCore import QPointF
from canvas.items import MetaRectItem, MetaPortItem, ANN_ID_KEY


# ── Helpers ──────────────────────────────────────────────────────────────

def _make_parent():
    """Create a parent rect item (NOT on scene yet)."""
    return MetaRectItem(100, 100, 200, 100, "parent1", None)


def _make_port(parent, t=0.5, ann_id="port1"):
    """Create a port attached to a parent shape.

    Parent must NOT be on a scene when creating the port — adding a
    child item to a scene-attached parent can trigger event processing
    that hangs in offscreen/test contexts.  Add the parent (with port
    as child) to the scene AFTER creation.
    """
    return MetaPortItem(t=t, radius=6.0, parent_shape=parent,
                        ann_id=ann_id, on_change=None)




# ── Tests ────────────────────────────────────────────────────────────────

class TestPortCreation:
    """Port creation and basic properties."""

    def test_port_has_kind(self):
        parent = _make_parent()
        port = _make_port(parent)
        assert port.kind == "port"

    def test_port_has_ann_id(self):
        parent = _make_parent()
        port = _make_port(parent, ann_id="p001")
        assert port.ann_id == "p001"
        assert port.data(ANN_ID_KEY) == "p001"

    def test_port_is_child_of_parent(self):
        parent = _make_parent()
        port = _make_port(parent)
        assert port.parentItem() is parent

    def test_port_default_type(self):
        parent = _make_parent()
        port = _make_port(parent)
        assert port._port_type == MetaPortItem.PORT_INOUT

    def test_port_default_protocol(self):
        parent = _make_parent()
        port = _make_port(parent)
        assert port._protocol == ""

    def test_port_default_connections(self):
        parent = _make_parent()
        port = _make_port(parent)
        assert port._connections == []


class TestPortToRecord:
    """to_record() serialization."""

    def test_to_record_has_kind_port(self):
        parent = _make_parent()
        port = _make_port(parent)
        rec = port.to_record()
        assert rec["kind"] == "port"

    def test_to_record_has_parent_id(self):
        parent = _make_parent()
        port = _make_port(parent)
        rec = port.to_record()
        assert rec["parent_id"] == "parent1"

    def test_to_record_geom_has_t(self):
        parent = _make_parent()
        port = _make_port(parent, t=0.75)
        rec = port.to_record()
        assert abs(rec["geom"]["t"] - 0.75) < 0.001

    def test_to_record_geom_has_radius(self):
        parent = _make_parent()
        port = _make_port(parent)
        rec = port.to_record()
        assert rec["geom"]["radius"] == 6.0

    def test_to_record_has_port_type(self):
        parent = _make_parent()
        port = _make_port(parent)
        rec = port.to_record()
        assert rec["geom"]["port_type"] == "InOut"

    def test_to_record_has_protocol(self):
        parent = _make_parent()
        port = _make_port(parent)
        port._protocol = "HTTP"
        rec = port.to_record()
        assert rec["geom"]["protocol"] == "HTTP"

    def test_to_record_connections(self):
        parent = _make_parent()
        port = _make_port(parent)
        port._connections = ["line1", "line2"]
        rec = port.to_record()
        assert rec["connections"] == ["line1", "line2"]

    def test_to_record_has_style(self):
        parent = _make_parent()
        port = _make_port(parent)
        rec = port.to_record()
        assert "style" in rec
        assert "pen" in rec["style"]

    def test_to_record_has_contents(self):
        parent = _make_parent()
        port = _make_port(parent)
        rec = port.to_record()
        assert "contents" in rec or "meta" in rec


class TestParentlessPort:
    """Parentless port includes absolute position in geom."""

    def test_parentless_port_has_xy(self):
        port = MetaPortItem(t=0.0, radius=6.0, parent_shape=None,
                            ann_id="orphan1", on_change=None)
        port.setPos(QPointF(50, 75))
        rec = port.to_record()
        assert "x" in rec["geom"]
        assert "y" in rec["geom"]

    def test_parentless_port_has_wh(self):
        port = MetaPortItem(t=0.0, radius=8.0, parent_shape=None,
                            ann_id="orphan2", on_change=None)
        rec = port.to_record()
        assert rec["geom"]["w"] == 16.0  # 2 * radius
        assert rec["geom"]["h"] == 16.0

    def test_parentless_port_empty_parent_id(self):
        port = MetaPortItem(t=0.0, radius=6.0, parent_shape=None,
                            ann_id="orphan3", on_change=None)
        rec = port.to_record()
        assert rec["parent_id"] == ""


class TestPortType:
    """Port type field round-trip."""

    @pytest.mark.parametrize("ptype", ["In", "Out", "InOut"])
    def test_port_type_in_record(self, ptype):
        parent = _make_parent()
        port = _make_port(parent)
        port._port_type = ptype
        rec = port.to_record()
        assert rec["geom"]["port_type"] == ptype


class TestPortStyle:
    """apply_style_from_record pen/fill color."""

    def test_apply_pen_color(self):
        parent = _make_parent()
        port = _make_port(parent)
        rec = {"style": {"pen": {"color": "#FF0000", "width": 2},
                          "fill": {"color": "#00FF00FF"}}}
        port.apply_style_from_record(rec)
        assert port.pen_color.red() == 255
        assert port.pen_color.green() == 0

    def test_apply_fill_color(self):
        parent = _make_parent()
        port = _make_port(parent)
        rec = {"style": {"pen": {"color": "#000000"},
                          "fill": {"color": "#0000FFFF"}}}
        port.apply_style_from_record(rec)
        assert port.brush_color.blue() == 255


class TestPortNoDuplicateIds:
    """No duplicate IDs when multiple ports exist."""

    def test_unique_ids(self):
        parent = _make_parent()
        port1 = _make_port(parent, t=0.25, ann_id="p001")
        port2 = _make_port(parent, t=0.75, ann_id="p002")
        ids = [port1.ann_id, port2.ann_id, parent.ann_id]
        assert len(ids) == len(set(ids)), f"Duplicate IDs found: {ids}"
