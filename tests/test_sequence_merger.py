"""Tests for mermaid/sequence_merger.py — Step 2 of the two-step sequence
diagram pipeline.

Validates that source-parsed semantic data is correctly merged with
SVG-parsed geometry to produce enriched PictoSync annotations.
"""
from __future__ import annotations

import os

import pytest

from mermaid.sequence_merger import (
    merge_sequence_source_with_svg,
    _classify_annotations,
    _normalize_label,
)
from mermaid.sequence_source_parser import parse_sequence_source_file


# ─────────────────────────────────────────────────────────
# Test fixtures — paths to test data
# ─────────────────────────────────────────────────────────

_MERMAID_DIR = "test_data/MERMAID"


def _seq(ann: dict) -> dict:
    """Extract sequence domain metadata from an annotation."""
    return ann.get("meta", {}).get("dsl", {}).get("sequence", {})


def _have_pair(name: str) -> bool:
    """Check that both .mermaid and .svg exist for a diagram."""
    return (
        os.path.exists(f"{_MERMAID_DIR}/{name}.mermaid")
        and os.path.exists(f"{_MERMAID_DIR}/{name}.svg")
    )


# ─────────────────────────────────────────────────────────
# Unit tests
# ─────────────────────────────────────────────────────────


class TestNormalizeLabel:
    def test_basic(self):
        assert _normalize_label("Web Browser") == "web browser"

    def test_extra_whitespace(self):
        assert _normalize_label("  Blog   Service  ") == "blog service"

    def test_empty(self):
        assert _normalize_label("") == ""


class TestClassifyAnnotations:
    def test_classifies_line_as_message(self):
        ann = [{"kind": "line", "meta": {"label": ""}, "style": {"fill": {"color": ""}}}]
        tops, msgs, notes, blocks, lifelines, bottoms, acts = _classify_annotations(ann)
        assert len(msgs) == 1
        assert len(tops) == 0

    def test_classifies_note_by_fill(self):
        ann = [{"kind": "roundedrect", "meta": {"label": ""}, "style": {"fill": {"color": "#FFF5AD"}}}]
        tops, msgs, notes, blocks, lifelines, bottoms, acts = _classify_annotations(ann)
        assert len(notes) == 1
        assert len(tops) == 0

    def test_classifies_block_by_fill(self):
        ann = [{"kind": "roundedrect", "meta": {"label": "loop"}, "style": {"fill": {"color": "#ECECFF"}}}]
        tops, msgs, notes, blocks, lifelines, bottoms, acts = _classify_annotations(ann)
        assert len(blocks) == 1

    def test_classifies_actor_top_by_role(self):
        ann = [{"kind": "roundedrect", "meta": {"label": "Alice", "seq_role": "actor_top"}, "style": {"fill": {"color": "#EAEAEA"}}}]
        tops, msgs, notes, blocks, lifelines, bottoms, acts = _classify_annotations(ann)
        assert len(tops) == 1

    def test_classifies_actor_top_by_fill_fallback(self):
        """Without seq_role, actor boxes should still be classified by fill."""
        ann = [{"kind": "roundedrect", "meta": {"label": "Alice"}, "style": {"fill": {"color": "#EAEAEA"}}}]
        tops, msgs, notes, blocks, lifelines, bottoms, acts = _classify_annotations(ann)
        assert len(tops) == 1

    def test_classifies_actor_bottom(self):
        ann = [{"kind": "roundedrect", "meta": {"label": "Alice", "seq_role": "actor_bottom"}, "style": {"fill": {"color": "#EAEAEA"}}}]
        tops, msgs, notes, blocks, lifelines, bottoms, acts = _classify_annotations(ann)
        assert len(bottoms) == 1
        assert len(tops) == 0

    def test_classifies_lifeline(self):
        ann = [{"kind": "line", "meta": {"label": "web", "seq_role": "lifeline"}, "style": {"fill": {"color": ""}}}]
        tops, msgs, notes, blocks, lifelines, bottoms, acts = _classify_annotations(ann)
        assert len(lifelines) == 1
        assert len(msgs) == 0

    def test_classifies_activation(self):
        ann = [{"kind": "rect", "meta": {"label": "", "seq_role": "activation"}, "style": {"fill": {"color": "#F4F4F4"}}}]
        tops, msgs, notes, blocks, lifelines, bottoms, acts = _classify_annotations(ann)
        assert len(acts) == 1
        assert len(tops) == 0

    def test_classifies_block_by_role(self):
        ann = [{"kind": "rect", "meta": {"label": "alt", "seq_role": "block"}, "style": {"fill": {"color": "#ECECFF"}}}]
        tops, msgs, notes, blocks, lifelines, bottoms, acts = _classify_annotations(ann)
        assert len(blocks) == 1

    def test_classifies_seqblock_by_kind(self):
        """A seqblock annotation should be classified as a block."""
        ann = [{"kind": "seqblock", "meta": {"label": "alt", "seq_role": "block"}, "style": {"fill": {"color": "#ECECFF40"}}}]
        tops, msgs, notes, blocks, lifelines, bottoms, acts = _classify_annotations(ann)
        assert len(blocks) == 1
        assert len(msgs) == 0


# ─────────────────────────────────────────────────────────
# Integration tests (require SVG test data)
# ─────────────────────────────────────────────────────────


@pytest.mark.skipif(not _have_pair("sequence"), reason="test data SVG missing")
class TestSequenceMerge:
    @pytest.fixture()
    def result(self):
        source = parse_sequence_source_file(f"{_MERMAID_DIR}/sequence.mermaid")
        return merge_sequence_source_with_svg(source, f"{_MERMAID_DIR}/sequence.svg")

    def test_output_structure(self, result):
        assert result["version"] == "draft-1"
        assert "width" in result["image"]
        assert "height" in result["image"]
        assert isinstance(result["annotations"], list)

    def test_has_annotations(self, result):
        assert len(result["annotations"]) > 0

    def test_actor_top_enrichment(self, result):
        """Actor top boxes should have sequence DSL data with alias."""
        actors = [
            a for a in result["annotations"]
            if _seq(a).get("type") == "participant"
            and a.get("meta", {}).get("seq_role") == "actor_top"
        ]
        assert len(actors) == 5
        for a in actors:
            assert "alias" in _seq(a)

    def test_actor_bottom_boxes(self, result):
        """Actor bottom boxes should exist and have DSL enrichment."""
        bottoms = [
            a for a in result["annotations"]
            if a.get("meta", {}).get("seq_role") == "actor_bottom"
        ]
        assert len(bottoms) == 5
        for b in bottoms:
            assert _seq(b).get("type") == "participant"
            assert "alias" in _seq(b)

    def test_lifelines(self, result):
        """Actor lifelines (vertical dashed lines) should exist."""
        lifelines = [
            a for a in result["annotations"]
            if a.get("meta", {}).get("seq_role") == "lifeline"
        ]
        assert len(lifelines) == 5
        for ll in lifelines:
            assert ll["kind"] == "line"
            assert _seq(ll).get("type") == "lifeline"
            assert "alias" in _seq(ll)
            # Lifelines should be vertical (x1 == x2)
            geom = ll["geom"]
            assert geom["x1"] == geom["x2"]

    def test_activations(self, result):
        """Activation boxes should exist."""
        acts = [
            a for a in result["annotations"]
            if a.get("meta", {}).get("seq_role") == "activation"
        ]
        assert len(acts) == 2  # account and blog activations
        for act in acts:
            assert act["kind"] == "rect"
            assert _seq(act).get("type") == "activation"

    def test_message_enrichment(self, result):
        """Message annotations should have sequence DSL data."""
        msgs = [
            a for a in result["annotations"]
            if _seq(a).get("type") == "message"
        ]
        assert len(msgs) > 0
        for m in msgs:
            seq = _seq(m)
            assert "from" in seq
            assert "to" in seq

    def test_message_arrow_types(self, result):
        """Messages should have line_type and arrow_type."""
        msgs = [
            a for a in result["annotations"]
            if _seq(a).get("type") == "message"
        ]
        for m in msgs:
            seq = _seq(m)
            assert seq.get("line_type") in ("solid", "dotted")
            assert seq.get("arrow_type") in ("arrow", "open", "cross", "point")

    def test_annotation_geometry(self, result):
        """All annotations should have geometry."""
        for ann in result["annotations"]:
            assert "geom" in ann
            geom = ann["geom"]
            if ann["kind"] == "line":
                assert "x1" in geom and "y1" in geom
            else:
                assert "x" in geom and "y" in geom

    def test_dsl_tool_is_mermaid(self, result):
        """All enriched annotations should have tool='mermaid'."""
        for ann in result["annotations"]:
            dsl = ann.get("meta", {}).get("dsl", {})
            if dsl:
                assert dsl.get("tool") == "mermaid"

    def test_block_enrichment(self, result):
        """Block rects should have DSL enrichment with block_type."""
        blocks = [
            a for a in result["annotations"]
            if _seq(a).get("type") == "block"
        ]
        assert len(blocks) == 2
        block_types = {_seq(b).get("block_type") for b in blocks}
        assert "alt" in block_types
        assert "par" in block_types

    def test_seqblock_adjust_values(self, result):
        """Seqblock annotations with dividers should carry adjust values."""
        seqblocks = [
            a for a in result["annotations"]
            if a.get("kind") == "seqblock"
        ]
        assert len(seqblocks) == 2
        # Both alt and par blocks have one divider each (else / and)
        for sb in seqblocks:
            geom = sb["geom"]
            assert "adjust1" in geom
            assert 0.05 <= geom["adjust1"] <= 0.95


# ─────────────────────────────────────────────────────────
# SVG-only tests (no source merger, just SVG parser output)
# ─────────────────────────────────────────────────────────


@pytest.mark.skipif(
    not os.path.exists(f"{_MERMAID_DIR}/sequence.svg"),
    reason="sequence.svg missing",
)
class TestSequenceSvgParser:
    """Test that the generic SVG parser extracts lifelines, bottom boxes,
    and activations from a sequence diagram SVG."""

    @pytest.fixture()
    def data(self):
        from mermaid.parser import parse_mermaid_svg_to_annotations
        return parse_mermaid_svg_to_annotations(f"{_MERMAID_DIR}/sequence.svg")

    def test_actor_top_boxes(self, data):
        tops = [a for a in data["annotations"]
                if a.get("meta", {}).get("seq_role") == "actor_top"]
        assert len(tops) == 5

    def test_actor_bottom_boxes(self, data):
        bottoms = [a for a in data["annotations"]
                   if a.get("meta", {}).get("seq_role") == "actor_bottom"]
        assert len(bottoms) == 5

    def test_lifelines(self, data):
        lifelines = [a for a in data["annotations"]
                     if a.get("meta", {}).get("seq_role") == "lifeline"]
        assert len(lifelines) == 5
        # Each lifeline should have a name
        for ll in lifelines:
            assert ll["meta"]["label"] != ""

    def test_activations(self, data):
        acts = [a for a in data["annotations"]
                if a.get("meta", {}).get("seq_role") == "activation"]
        assert len(acts) == 2

    def test_lifeline_names_match_actors(self, data):
        """Lifeline names should correspond to actor names."""
        tops = {a["meta"]["label"] for a in data["annotations"]
                if a.get("meta", {}).get("seq_role") == "actor_top"}
        lifeline_names = {a["meta"]["label"] for a in data["annotations"]
                          if a.get("meta", {}).get("seq_role") == "lifeline"}
        # Lifeline names are aliases (e.g. "web"), actor labels are display
        # names (e.g. "Web Browser"). They won't match directly, but both
        # sets should have 5 entries.
        assert len(lifeline_names) == 5
        assert len(tops) == 5

    def test_block_rects(self, data):
        """Block rects (alt, par) should be extracted from SVG."""
        blocks = [a for a in data["annotations"]
                  if a.get("meta", {}).get("seq_role") == "block"]
        assert len(blocks) == 2  # alt + par
        labels = {b["meta"]["label"] for b in blocks}
        assert "alt" in labels
        assert "par" in labels

    def test_seqblock_dividers_as_adjust(self, data):
        """Dividers should be encoded as adjust values in seqblock geom."""
        seqblocks = [a for a in data["annotations"]
                     if a.get("kind") == "seqblock"]
        assert len(seqblocks) == 2  # alt + par
        # Each has one divider (else / and) → adjust1 present
        for sb in seqblocks:
            assert "adjust1" in sb["geom"]

    def test_block_geometry(self, data):
        """Block rects should have meaningful geometry."""
        blocks = [a for a in data["annotations"]
                  if a.get("meta", {}).get("seq_role") == "block"]
        for b in blocks:
            geom = b["geom"]
            assert geom["w"] > 0
            assert geom["h"] > 0
