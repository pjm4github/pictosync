"""Test bench for context menu actions and z-order management.

Tests:
  - Bring to front: target item gets highest z-value
  - Send to back: target item gets lowest z-value
  - Z-order reset when send-to-back would go negative
  - Z-order callback fires
  - Group request via callback
  - Ungroup request via callback
  - SeqBlock add/remove divider
  - Multiple items maintain relative order after bring/send
"""
from __future__ import annotations

import pytest

from canvas.items import (
    MetaRectItem, MetaEllipseItem, MetaGroupItem, MetaSeqBlockItem,
)
from canvas.scene import AnnotatorScene


# ── Helpers ──────────────────────────────────────────────────────────────

def _scene_with_items(n=3):
    """Create a scene with n rect items at increasing z-values."""
    scene = AnnotatorScene()
    items = []
    for i in range(n):
        it = MetaRectItem(i * 100, 0, 80, 50, f"r{i}", None)
        scene.addItem(it)
        it.setZValue(1000 + i * 10)
        items.append(it)
    return scene, items


# ── Bring to Front ───────────────────────────────────────────────────────

class TestBringToFront:

    def test_target_gets_highest_z(self):
        scene, items = _scene_with_items(3)
        lowest = items[0]  # z=1000
        scene._bring_to_front(lowest)
        for other in items[1:]:
            assert lowest.zValue() > other.zValue()

    def test_other_items_retain_order(self):
        scene, items = _scene_with_items(4)
        scene._bring_to_front(items[0])
        # items[1], items[2], items[3] should still be in relative order
        z1 = items[1].zValue()
        z2 = items[2].zValue()
        z3 = items[3].zValue()
        assert z1 < z2 < z3

    def test_already_front_is_noop(self):
        scene, items = _scene_with_items(3)
        top = items[-1]
        old_z = top.zValue()
        scene._bring_to_front(top)
        assert top.zValue() >= old_z

    def test_single_item_no_crash(self):
        scene = AnnotatorScene()
        it = MetaRectItem(0, 0, 80, 50, "r1", None)
        scene.addItem(it)
        it.setZValue(100)
        scene._bring_to_front(it)  # should not crash
        assert it.zValue() == 100

    def test_z_order_callback_fires(self):
        calls = []
        scene, items = _scene_with_items(3)
        scene.set_z_order_changed_callback(lambda: calls.append(1))
        scene._bring_to_front(items[0])
        assert len(calls) == 1


# ── Send to Back ─────────────────────────────────────────────────────────

class TestSendToBack:

    def test_target_gets_lowest_z(self):
        scene, items = _scene_with_items(3)
        highest = items[-1]  # z=1020
        scene._send_to_back(highest)
        for other in items[:-1]:
            assert highest.zValue() < other.zValue()

    def test_other_items_retain_order(self):
        scene, items = _scene_with_items(4)
        scene._send_to_back(items[3])
        z0 = items[0].zValue()
        z1 = items[1].zValue()
        z2 = items[2].zValue()
        assert z0 < z1 < z2

    def test_reset_when_negative(self):
        """If send-to-back would go below 0, z-indices are reset."""
        scene, items = _scene_with_items(3)
        # Set items at very low z so next send-back would go negative
        for i, it in enumerate(items):
            it.setZValue(5 + i)
        scene._send_to_back(items[1])
        # All z-values should be positive
        for it in items:
            assert it.zValue() >= 0

    def test_z_order_callback_fires(self):
        calls = []
        scene, items = _scene_with_items(3)
        scene.set_z_order_changed_callback(lambda: calls.append(1))
        scene._send_to_back(items[-1])
        assert len(calls) == 1


# ── Group/Ungroup Requests ───────────────────────────────────────────────

class TestGroupRequest:

    def test_group_callback_fires(self):
        grouped = []
        scene, items = _scene_with_items(2)
        scene.set_group_callbacks(
            on_group=lambda sel: grouped.append(sel),
            on_ungroup=lambda g: None,
        )
        scene._request_group(items)
        assert len(grouped) == 1
        assert len(grouped[0]) == 2

    def test_group_callback_receives_items(self):
        grouped = []
        scene, items = _scene_with_items(3)
        scene.set_group_callbacks(
            on_group=lambda sel: grouped.extend(sel),
            on_ungroup=lambda g: None,
        )
        scene._request_group(items)
        ids = {getattr(it, "ann_id", None) for it in grouped}
        assert ids == {"r0", "r1", "r2"}


class TestUngroupRequest:

    def test_ungroup_callback_fires(self):
        ungrouped = []
        scene = AnnotatorScene()
        group = MetaGroupItem("g1", None)
        scene.addItem(group)
        scene.set_group_callbacks(
            on_group=lambda sel: None,
            on_ungroup=lambda g: ungrouped.append(g),
        )
        scene._request_ungroup(group)
        assert len(ungrouped) == 1
        assert ungrouped[0] is group

    def test_no_callback_no_crash(self):
        scene = AnnotatorScene()
        group = MetaGroupItem("g1", None)
        scene.addItem(group)
        # No callbacks set — should not crash
        scene._request_ungroup(group)


# ── SeqBlock Divider ─────────────────────────────────────────────────────

class TestSeqBlockDivider:

    def test_add_divider(self):
        scene = AnnotatorScene()
        item = MetaSeqBlockItem(0, 0, 200, 150, "loop", "sb1", None)
        scene.addItem(item)
        assert item._divider_count == 0
        scene._seqblock_add_divider(item)
        assert item._divider_count == 1

    def test_add_divider_up_to_three(self):
        scene = AnnotatorScene()
        item = MetaSeqBlockItem(0, 0, 200, 150, "loop", "sb1", None)
        scene.addItem(item)
        scene._seqblock_add_divider(item)
        scene._seqblock_add_divider(item)
        scene._seqblock_add_divider(item)
        assert item._divider_count == 3
        # Fourth add should be blocked
        scene._seqblock_add_divider(item)
        assert item._divider_count == 3

    def test_remove_divider(self):
        scene = AnnotatorScene()
        item = MetaSeqBlockItem(0, 0, 200, 150, "alt", "sb1", None)
        scene.addItem(item)
        assert item._divider_count == 1
        scene._seqblock_remove_divider(item)
        assert item._divider_count == 0

    def test_remove_below_zero_blocked(self):
        scene = AnnotatorScene()
        item = MetaSeqBlockItem(0, 0, 200, 150, "loop", "sb1", None)
        scene.addItem(item)
        assert item._divider_count == 0
        scene._seqblock_remove_divider(item)
        assert item._divider_count == 0


# ── Z-Order Relative Ordering ────────────────────────────────────────────

class TestZOrderRelative:

    def test_front_back_cycle(self):
        """Bring to front then send to back returns to lowest."""
        scene, items = _scene_with_items(3)
        mid = items[1]
        scene._bring_to_front(mid)
        assert mid.zValue() > items[0].zValue()
        assert mid.zValue() > items[2].zValue()
        scene._send_to_back(mid)
        assert mid.zValue() < items[0].zValue()
        assert mid.zValue() < items[2].zValue()

    def test_all_z_values_unique(self):
        scene, items = _scene_with_items(5)
        scene._bring_to_front(items[2])
        z_vals = [it.zValue() for it in items]
        assert len(z_vals) == len(set(z_vals)), f"Duplicate z-values: {z_vals}"

    def test_all_z_values_positive(self):
        scene, items = _scene_with_items(5)
        for _ in range(5):
            scene._send_to_back(items[0])
        for it in items:
            assert it.zValue() >= 0
