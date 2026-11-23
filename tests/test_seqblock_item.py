"""Test bench for MetaSeqBlockItem — sequence diagram combined fragment.

Tests:
    - SeqBlock creation with block_type
    - to_record() serialization (kind, geom, adjust1/2/3, contents, style)
    - Block type defaults (alt/par get 1 divider, loop/opt get 0)
    - Adjust values serialization (only if divider_count >= N)
    - Custom adjust values round-trip
    - Block type stored in meta
    - geom x/y/w/h present and numeric
    - style.pen and style.fill present
    - No duplicate IDs
"""
from __future__ import annotations

import os
import sys

import pytest




from canvas.items import MetaSeqBlockItem, ANN_ID_KEY


# ── Helpers ──────────────────────────────────────────────────────────────

def _make_seqblock(block_type="alt", ann_id="sb1",
                   x=100, y=100, w=200, h=150):
    return MetaSeqBlockItem(x, y, w, h, block_type, ann_id, on_change=None)


# ── Tests ────────────────────────────────────────────────────────────────

class TestSeqBlockCreation:
    """SeqBlock creation and basic properties."""

    def test_kind(self):
        item = _make_seqblock()
        assert item.kind == "seqblock"

    def test_ann_id(self):
        item = _make_seqblock(ann_id="seq42")
        assert item.ann_id == "seq42"
        assert item.data(ANN_ID_KEY) == "seq42"

    def test_block_type_stored(self):
        item = _make_seqblock(block_type="loop")
        assert item._block_type == "loop"

    def test_dimensions(self):
        item = _make_seqblock(x=10, y=20, w=300, h=200)
        assert item._width == 300
        assert item._height == 200


class TestSeqBlockDividerDefaults:
    """Block type → divider count defaults."""

    @pytest.mark.parametrize("btype,expected", [
        ("alt", 1),
        ("par", 1),
        ("loop", 0),
        ("opt", 0),
        ("break", 0),
        ("critical", 0),
    ])
    def test_divider_count(self, btype, expected):
        item = _make_seqblock(block_type=btype)
        assert item._divider_count == expected

    def test_unknown_type_zero_dividers(self):
        item = _make_seqblock(block_type="custom")
        assert item._divider_count == 0


class TestSeqBlockAdjustDefaults:
    """Default adjust values."""

    def test_adjust1_default(self):
        item = _make_seqblock()
        assert item._adjust1 == 0.5

    def test_adjust2_default(self):
        item = _make_seqblock()
        assert item._adjust2 == 0.67

    def test_adjust3_default(self):
        item = _make_seqblock()
        assert item._adjust3 == 0.83


class TestSeqBlockToRecord:
    """to_record() serialization."""

    def test_kind_in_record(self):
        item = _make_seqblock()
        rec = item.to_record()
        assert rec["kind"] == "seqblock"

    def test_geom_has_xywh(self):
        item = _make_seqblock(x=10, y=20, w=300, h=200)
        rec = item.to_record()
        g = rec["geom"]
        assert g["x"] == 10
        assert g["y"] == 20
        assert g["w"] == 300
        assert g["h"] == 200

    def test_alt_has_adjust1(self):
        """alt type has 1 divider → adjust1 in geom."""
        item = _make_seqblock(block_type="alt")
        rec = item.to_record()
        assert "adjust1" in rec["geom"]
        assert abs(rec["geom"]["adjust1"] - 0.5) < 0.01

    def test_alt_no_adjust2(self):
        """alt type has 1 divider → no adjust2 in geom."""
        item = _make_seqblock(block_type="alt")
        rec = item.to_record()
        assert "adjust2" not in rec["geom"]

    def test_loop_no_adjust(self):
        """loop type has 0 dividers → no adjust in geom."""
        item = _make_seqblock(block_type="loop")
        rec = item.to_record()
        assert "adjust1" not in rec["geom"]
        assert "adjust2" not in rec["geom"]
        assert "adjust3" not in rec["geom"]

    def test_custom_adjust_values(self):
        """Custom adjust values serialize correctly."""
        item = _make_seqblock(block_type="alt")
        item._divider_count = 3
        item._adjust1 = 0.3
        item._adjust2 = 0.6
        item._adjust3 = 0.9
        rec = item.to_record()
        g = rec["geom"]
        assert abs(g["adjust1"] - 0.3) < 0.01
        assert abs(g["adjust2"] - 0.6) < 0.01
        assert abs(g["adjust3"] - 0.9) < 0.01

    def test_has_style(self):
        item = _make_seqblock()
        rec = item.to_record()
        assert "style" in rec
        assert "pen" in rec["style"]
        assert "fill" in rec["style"]

    def test_has_contents(self):
        item = _make_seqblock()
        rec = item.to_record()
        assert "contents" in rec

    def test_has_ports(self):
        item = _make_seqblock()
        rec = item.to_record()
        assert "ports" in rec


class TestSeqBlockNoDuplicateIds:
    """No duplicate IDs."""

    def test_unique_ids(self):
        s1 = _make_seqblock(ann_id="sb1")
        s2 = _make_seqblock(ann_id="sb2")
        assert s1.ann_id != s2.ann_id
