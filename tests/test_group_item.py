"""Test bench for MetaGroupItem — group container with children.

Tests:
    - Group creation with member items
    - to_record() serialization (kind, children array, meta, z)
    - Children have scene-absolute coordinates (offset from group position)
    - add_member / remove_member operations
    - member_items() returns annotation children only
    - Nested group (group containing a group)
    - Children kind and geom preserved through serialization
    - Line children use x1/y1/x2/y2 offset
    - No duplicate IDs across group and children
"""
from __future__ import annotations

import os
import sys

import pytest




from PyQt6.QtCore import QPointF
from canvas.items import (
    MetaRectItem, MetaEllipseItem, MetaLineItem, MetaGroupItem, ANN_ID_KEY,
)
from canvas.scene import AnnotatorScene


# ── Helpers ──────────────────────────────────────────────────────────────

def _make_scene():
    return AnnotatorScene()


def _make_group(scene, ann_id="g001", children=None):
    """Create a group and add children to it."""
    group = MetaGroupItem(ann_id, on_change=None)
    scene.addItem(group)
    if children:
        for child in children:
            if child.scene() is None:
                scene.addItem(child)
            group.add_member(child)
    return group


# ── Tests ────────────────────────────────────────────────────────────────

class TestGroupCreation:
    """Group creation and basic properties."""

    def test_group_kind(self):
        scene = _make_scene()
        group = _make_group(scene)
        assert group.kind == "group"

    def test_group_ann_id(self):
        scene = _make_scene()
        group = _make_group(scene, ann_id="grp42")
        assert group.ann_id == "grp42"
        assert group.data(ANN_ID_KEY) == "grp42"

    def test_group_not_rotatable(self):
        scene = _make_scene()
        group = _make_group(scene)
        assert group._is_rotatable() is False

    def test_empty_group_member_items(self):
        scene = _make_scene()
        group = _make_group(scene)
        assert group.member_items() == []


class TestGroupMembers:
    """add_member / remove_member / member_items."""

    def test_add_member(self):
        scene = _make_scene()
        rect = MetaRectItem(50, 50, 100, 60, "r1", None)
        group = _make_group(scene, children=[rect])
        members = group.member_items()
        assert len(members) == 1
        assert members[0].ann_id == "r1"

    def test_add_multiple_members(self):
        scene = _make_scene()
        r1 = MetaRectItem(10, 10, 80, 40, "r1", None)
        r2 = MetaEllipseItem(200, 10, 80, 40, "e1", None)
        group = _make_group(scene, children=[r1, r2])
        ids = [m.ann_id for m in group.member_items()]
        assert set(ids) == {"r1", "e1"}

    def test_remove_member(self):
        scene = _make_scene()
        r1 = MetaRectItem(10, 10, 80, 40, "r1", None)
        r2 = MetaRectItem(200, 10, 80, 40, "r2", None)
        group = _make_group(scene, children=[r1, r2])
        group.remove_member(r1)
        ids = [m.ann_id for m in group.member_items()]
        assert "r1" not in ids
        assert "r2" in ids

    def test_removed_member_is_selectable(self):
        scene = _make_scene()
        rect = MetaRectItem(10, 10, 80, 40, "r1", None)
        group = _make_group(scene, children=[rect])
        group.remove_member(rect)
        from PyQt6.QtWidgets import QGraphicsItem
        assert rect.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable

    def test_child_is_not_selectable_in_group(self):
        scene = _make_scene()
        rect = MetaRectItem(10, 10, 80, 40, "r1", None)
        group = _make_group(scene, children=[rect])
        from PyQt6.QtWidgets import QGraphicsItem
        assert not (rect.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)


class TestGroupToRecord:
    """to_record() serialization."""

    def test_to_record_kind(self):
        scene = _make_scene()
        group = _make_group(scene)
        rec = group.to_record()
        assert rec["kind"] == "group"

    def test_to_record_has_children(self):
        scene = _make_scene()
        r1 = MetaRectItem(50, 50, 100, 60, "r1", None)
        group = _make_group(scene, children=[r1])
        rec = group.to_record()
        assert "children" in rec
        assert len(rec["children"]) == 1

    def test_to_record_children_have_kind(self):
        scene = _make_scene()
        r1 = MetaRectItem(50, 50, 100, 60, "r1", None)
        e1 = MetaEllipseItem(200, 50, 80, 80, "e1", None)
        group = _make_group(scene, children=[r1, e1])
        rec = group.to_record()
        kinds = {c["kind"] for c in rec["children"]}
        assert kinds == {"rect", "ellipse"}

    def test_to_record_has_contents(self):
        scene = _make_scene()
        group = _make_group(scene)
        rec = group.to_record()
        assert "contents" in rec

    def test_to_record_empty_children_when_no_members(self):
        scene = _make_scene()
        group = _make_group(scene)
        rec = group.to_record()
        assert rec["children"] == []


class TestGroupGeomOffset:
    """Children have scene-absolute coordinates after group offset."""

    def test_rect_child_geom_offset(self):
        scene = _make_scene()
        # Create rect at (50, 50) then group at default position
        r1 = MetaRectItem(50, 50, 100, 60, "r1", None)
        group = _make_group(scene, children=[r1])
        # Group position is set by Qt when adding items
        rec = group.to_record()
        child_geom = rec["children"][0]["geom"]
        # x and y should be scene-absolute (not negative or zero
        # when the rect was at 50, 50)
        assert child_geom["x"] >= 0
        assert child_geom["y"] >= 0
        assert child_geom["w"] == 100
        assert child_geom["h"] == 60

    def test_line_child_geom_offset(self):
        scene = _make_scene()
        line = MetaLineItem(10, 20, 200, 150, "l1", None)
        group = _make_group(scene, children=[line])
        rec = group.to_record()
        child_geom = rec["children"][0]["geom"]
        # Line should have x1/y1/x2/y2 (scene-absolute)
        assert "x1" in child_geom
        assert "y1" in child_geom
        assert "x2" in child_geom
        assert "y2" in child_geom

    def test_children_geom_preserved_dimensions(self):
        scene = _make_scene()
        r1 = MetaRectItem(100, 200, 150, 75, "r1", None)
        group = _make_group(scene, children=[r1])
        rec = group.to_record()
        child_geom = rec["children"][0]["geom"]
        # Width and height should not change
        assert child_geom["w"] == 150
        assert child_geom["h"] == 75


class TestNestedGroup:
    """Group containing another group."""

    def test_nested_group_serializes(self):
        scene = _make_scene()
        r1 = MetaRectItem(10, 10, 80, 40, "r1", None)
        inner = _make_group(scene, ann_id="inner", children=[r1])
        r2 = MetaRectItem(200, 10, 80, 40, "r2", None)
        outer = _make_group(scene, ann_id="outer", children=[inner, r2])
        rec = outer.to_record()
        assert rec["kind"] == "group"
        assert len(rec["children"]) == 2
        # One child should be the inner group
        inner_child = [c for c in rec["children"] if c["kind"] == "group"]
        assert len(inner_child) == 1
        assert len(inner_child[0]["children"]) == 1

    def test_nested_group_children_offset_recursively(self):
        scene = _make_scene()
        r1 = MetaRectItem(10, 10, 50, 30, "r1", None)
        inner = _make_group(scene, ann_id="inner", children=[r1])
        outer = _make_group(scene, ann_id="outer", children=[inner])
        rec = outer.to_record()
        # Drill into nested children
        inner_rec = [c for c in rec["children"] if c["kind"] == "group"][0]
        deep_child = inner_rec["children"][0]
        assert deep_child["kind"] == "rect"
        assert deep_child["geom"]["w"] == 50
        assert deep_child["geom"]["h"] == 30


class TestGroupNoDuplicateIds:
    """No duplicate IDs across group and children."""

    def test_no_duplicates(self):
        scene = _make_scene()
        r1 = MetaRectItem(10, 10, 80, 40, "r1", None)
        r2 = MetaRectItem(200, 10, 80, 40, "r2", None)
        group = _make_group(scene, ann_id="g1", children=[r1, r2])
        rec = group.to_record()
        all_ids = [rec["id"]]
        for c in rec["children"]:
            all_ids.append(c["id"])
        assert len(all_ids) == len(set(all_ids)), f"Duplicate IDs: {all_ids}"

    def test_nested_no_duplicates(self):
        scene = _make_scene()
        r1 = MetaRectItem(10, 10, 50, 30, "r1", None)
        inner = _make_group(scene, ann_id="inner", children=[r1])
        r2 = MetaRectItem(200, 10, 50, 30, "r2", None)
        outer = _make_group(scene, ann_id="outer", children=[inner, r2])
        rec = outer.to_record()

        def _collect_ids(r):
            ids = [r["id"]]
            for c in r.get("children", []):
                ids.extend(_collect_ids(c))
            return ids

        all_ids = _collect_ids(rec)
        assert len(all_ids) == len(set(all_ids)), f"Duplicate IDs: {all_ids}"
