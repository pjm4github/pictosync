"""Test bench for contents.blocks/runs formatting round-trip.

Tests that the overlay-2.0 block/run/format structure survives:
  - AnnotationContents from_dict → to_dict for blocks, runs, formats
  - Block-level: halign, spacing_type, spacing_value, space_before, space_after
  - Run-level: bold, italic, underline, strikethrough, color, font_family, font_size
  - default_format: font_family, font_size, color, spacing_type, spacing_value
  - frame: halign, valign, margins
  - CharFormat sparse serialization (only non-default fields emitted)
  - Multi-block, multi-run documents
  - Legacy format (label/tech/note) → blocks migration
  - Overlay-2.0 with label/tech/note convenience keys → blocks authoritative
"""
from __future__ import annotations

import os
import sys

import pytest


from models import (
    AnnotationContents,
    TextFrame,
    CharFormat,
    TextBlock,
    TextRun,
)


# ── Tests ────────────────────────────────────────────────────────────────

class TestCharFormatRoundTrip:
    """CharFormat to_dict / from_dict."""

    def test_empty_format(self):
        cf = CharFormat()
        d = cf.to_dict(sparse=True)
        assert d == {}

    def test_bold_only(self):
        cf = CharFormat(bold=True)
        d = cf.to_dict(sparse=True)
        assert d == {"bold": True}
        cf2 = CharFormat.from_dict(d)
        assert cf2.bold is True
        assert cf2.italic is False

    def test_full_format(self):
        cf = CharFormat(
            font_family="Arial", font_size=16, bold=True, italic=True,
            underline=True, strikethrough=True, color="#FF0000FF",
            background_color="#00FF00FF", superscript=False, subscript=True,
            spacing_type="proportional", spacing_value=150.0,
        )
        d = cf.to_dict(sparse=True)
        cf2 = CharFormat.from_dict(d)
        assert cf2.font_family == "Arial"
        assert cf2.font_size == 16
        assert cf2.bold is True
        assert cf2.italic is True
        assert cf2.underline is True
        assert cf2.strikethrough is True
        assert cf2.color == "#FF0000FF"
        assert cf2.background_color == "#00FF00FF"
        assert cf2.subscript is True
        assert cf2.spacing_type == "proportional"
        assert cf2.spacing_value == 150.0

    def test_sparse_omits_defaults(self):
        cf = CharFormat(font_size=12, bold=False, color="")
        d = cf.to_dict(sparse=True)
        # All default values → empty dict
        assert d == {}

    def test_non_sparse_includes_all(self):
        cf = CharFormat()
        d = cf.to_dict(sparse=False)
        assert "font_family" in d
        assert "font_size" in d
        assert "bold" in d
        assert "spacing_type" in d


class TestTextRunRoundTrip:
    """TextRun to_dict / from_dict."""

    def test_plain_run(self):
        r = TextRun(type="text", text="hello")
        d = r.to_dict()
        assert d["type"] == "text"
        assert d["text"] == "hello"
        assert "format" not in d  # no format → not serialized

    def test_formatted_run(self):
        r = TextRun(type="text", text="bold text",
                    format=CharFormat(bold=True, color="#0000FFFF"))
        d = r.to_dict()
        assert d["format"]["bold"] is True
        assert d["format"]["color"] == "#0000FFFF"
        r2 = TextRun.from_dict(d)
        assert r2.text == "bold text"
        assert r2.format.bold is True
        assert r2.format.color == "#0000FFFF"

    def test_empty_format_not_serialized(self):
        r = TextRun(type="text", text="plain", format=CharFormat())
        d = r.to_dict()
        assert "format" not in d  # all defaults → omitted


class TestTextBlockRoundTrip:
    """TextBlock to_dict / from_dict."""

    def test_simple_block(self):
        b = TextBlock(runs=[TextRun(type="text", text="hello")])
        d = b.to_dict()
        assert len(d["runs"]) == 1
        assert d["runs"][0]["text"] == "hello"
        b2 = TextBlock.from_dict(d)
        assert b2.runs[0].text == "hello"

    def test_block_halign(self):
        b = TextBlock(halign="right", runs=[TextRun(type="text", text="x")])
        d = b.to_dict()
        assert d["halign"] == "right"
        b2 = TextBlock.from_dict(d)
        assert b2.halign == "right"

    def test_block_halign_empty_not_serialized(self):
        b = TextBlock(halign="", runs=[TextRun(type="text", text="x")])
        d = b.to_dict()
        assert "halign" not in d

    def test_block_spacing(self):
        b = TextBlock(
            spacing_type="fixed", spacing_value=20.0,
            space_before=5.0, space_after=3.0,
            runs=[TextRun(type="text", text="x")],
        )
        d = b.to_dict()
        assert d["spacing_type"] == "fixed"
        assert d["spacing_value"] == 20.0
        assert d["space_before"] == 5.0
        assert d["space_after"] == 3.0
        b2 = TextBlock.from_dict(d)
        assert b2.spacing_type == "fixed"
        assert b2.spacing_value == 20.0
        assert b2.space_before == 5.0
        assert b2.space_after == 3.0

    def test_block_default_spacing_not_serialized(self):
        b = TextBlock(runs=[TextRun(type="text", text="x")])
        d = b.to_dict()
        assert "spacing_type" not in d
        assert "spacing_value" not in d
        assert "space_before" not in d
        assert "space_after" not in d

    def test_multi_run_block(self):
        b = TextBlock(runs=[
            TextRun(type="text", text="normal "),
            TextRun(type="text", text="bold", format=CharFormat(bold=True)),
            TextRun(type="text", text=" end"),
        ])
        d = b.to_dict()
        assert len(d["runs"]) == 3
        assert d["runs"][1]["format"]["bold"] is True
        b2 = TextBlock.from_dict(d)
        assert b2.runs[1].format.bold is True
        assert b2.plain_text() == "normal bold end"


class TestFrameRoundTrip:
    """TextFrame to_dict / from_dict."""

    def test_default_frame(self):
        f = TextFrame()
        d = f.to_dict()
        assert d["halign"] == "center"
        assert d["valign"] == "top"
        f2 = TextFrame.from_dict(d)
        assert f2.halign == "center"

    def test_custom_frame(self):
        f = TextFrame(halign="left", valign="bottom",
                      margin_left=8, margin_right=8,
                      margin_top=2, margin_bottom=2)
        d = f.to_dict()
        f2 = TextFrame.from_dict(d)
        assert f2.halign == "left"
        assert f2.valign == "bottom"
        assert f2.margin_left == 8
        assert f2.margin_bottom == 2


class TestAnnotationContentsOverlay20:
    """AnnotationContents from_dict / to_dict for overlay-2.0 format."""

    def test_simple_blocks(self):
        d = {
            "frame": {"halign": "center", "valign": "top"},
            "default_format": {"font_size": 14, "color": "#333333FF"},
            "blocks": [
                {"runs": [{"type": "text", "text": "Title",
                           "format": {"bold": True}}]},
                {"runs": [{"type": "text", "text": "Subtitle"}]},
            ],
        }
        meta = AnnotationContents.from_dict(d)
        assert len(meta.blocks) == 2
        assert meta.blocks[0].runs[0].text == "Title"
        assert meta.blocks[0].runs[0].format.bold is True
        assert meta.blocks[1].runs[0].text == "Subtitle"
        assert meta.default_format.font_size == 14
        assert meta.frame.halign == "center"

    def test_to_dict_round_trip(self):
        d = {
            "frame": {"halign": "left", "valign": "middle"},
            "default_format": {"font_size": 16, "font_family": "Arial",
                               "color": "#000000FF"},
            "blocks": [
                {"runs": [{"type": "text", "text": "Hello",
                           "format": {"bold": True, "color": "#FF0000FF"}}]},
                {"runs": [{"type": "text", "text": "World",
                           "format": {"italic": True}}]},
            ],
        }
        meta = AnnotationContents.from_dict(d)
        d2 = meta.to_dict()
        meta2 = AnnotationContents.from_dict(d2)
        assert len(meta2.blocks) == 2
        assert meta2.blocks[0].runs[0].text == "Hello"
        assert meta2.blocks[0].runs[0].format.bold is True
        assert meta2.blocks[0].runs[0].format.color == "#FF0000FF"
        assert meta2.blocks[1].runs[0].format.italic is True
        assert meta2.default_format.font_size == 16
        assert meta2.frame.halign == "left"
        assert meta2.frame.valign == "middle"

    def test_label_tech_note_derived(self):
        d = {
            "blocks": [
                {"runs": [{"type": "text", "text": "MyService"}]},
                {"runs": [{"type": "text", "text": "Java"}]},
                {"runs": [{"type": "text", "text": "Backend"}]},
            ],
            "frame": {},
        }
        meta = AnnotationContents.from_dict(d)
        assert meta.label == "MyService"
        assert meta.tech == "Java"
        assert meta.note == "Backend"

    def test_blocks_with_spacing(self):
        d = {
            "frame": {},
            "default_format": {"spacing_type": "proportional",
                               "spacing_value": 150.0},
            "blocks": [
                {"runs": [{"type": "text", "text": "Line 1"}],
                 "spacing_type": "fixed", "spacing_value": 20.0,
                 "space_before": 4.0, "space_after": 2.0},
                {"runs": [{"type": "text", "text": "Line 2"}]},
            ],
        }
        meta = AnnotationContents.from_dict(d)
        assert meta.blocks[0].spacing_type == "fixed"
        assert meta.blocks[0].spacing_value == 20.0
        assert meta.blocks[0].space_before == 4.0
        assert meta.blocks[1].spacing_type == ""  # inherits from default
        assert meta.default_format.spacing_type == "proportional"

    def test_overlay20_with_label_key(self):
        """Overlay-2.0 with both blocks AND label key → blocks win."""
        d = {
            "frame": {},
            "blocks": [
                {"runs": [{"type": "text", "text": "From Blocks"}]},
            ],
            "label": "From Label Key",
        }
        meta = AnnotationContents.from_dict(d)
        # blocks should be authoritative
        assert meta.blocks[0].runs[0].text == "From Blocks"
        assert meta.label == "From Blocks"


class TestLegacyFormatMigration:
    """Legacy label/tech/note → blocks migration."""

    def test_legacy_creates_three_blocks(self):
        d = {"label": "Server", "tech": "Java", "note": "Backend"}
        meta = AnnotationContents.from_dict(d)
        assert len(meta.blocks) == 3
        assert meta.label == "Server"
        assert meta.tech == "Java"
        assert meta.note == "Backend"

    def test_legacy_label_bold(self):
        d = {"label": "Server"}
        meta = AnnotationContents.from_dict(d)
        assert meta.blocks[0].runs[0].format.bold is True

    def test_legacy_tech_italic(self):
        d = {"label": "X", "tech": "TypeScript"}
        meta = AnnotationContents.from_dict(d)
        assert meta.blocks[1].runs[0].format.italic is True

    def test_legacy_empty_fields(self):
        d = {"label": "", "tech": "", "note": ""}
        meta = AnnotationContents.from_dict(d)
        # Blocks are created but empty text
        assert len(meta.blocks) == 3


class TestMultiRunMultiBlock:
    """Complex multi-block, multi-run documents."""

    def test_three_blocks_with_mixed_runs(self):
        d = {
            "frame": {"halign": "center"},
            "default_format": {"font_size": 12},
            "blocks": [
                {"runs": [
                    {"type": "text", "text": "Normal "},
                    {"type": "text", "text": "Bold",
                     "format": {"bold": True}},
                    {"type": "text", "text": " and "},
                    {"type": "text", "text": "Red",
                     "format": {"color": "#FF0000FF"}},
                ]},
                {"runs": [
                    {"type": "text", "text": "Second paragraph",
                     "format": {"italic": True, "font_size": 10}},
                ], "halign": "left"},
                {"runs": [
                    {"type": "text", "text": "Third with "},
                    {"type": "text", "text": "underline",
                     "format": {"underline": True}},
                ], "space_before": 6.0},
            ],
        }
        meta = AnnotationContents.from_dict(d)
        d2 = meta.to_dict()
        meta2 = AnnotationContents.from_dict(d2)

        # Block 0: 4 runs
        assert len(meta2.blocks[0].runs) == 4
        assert meta2.blocks[0].runs[1].format.bold is True
        assert meta2.blocks[0].runs[3].format.color == "#FF0000FF"

        # Block 1: italic, left aligned
        assert meta2.blocks[1].runs[0].format.italic is True
        assert meta2.blocks[1].runs[0].format.font_size == 10
        assert meta2.blocks[1].halign == "left"

        # Block 2: underline run, space_before
        assert meta2.blocks[2].runs[1].format.underline is True
        assert meta2.blocks[2].space_before == 6.0

        # label = block 0 plain text
        assert meta2.label == "Normal Bold and Red"
