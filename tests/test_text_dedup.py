"""Test bench for text deduplication logic.

Tests _dedup_blocks (models.py) and _dedup_label_tech_note (plantuml/parser.py):
  - Block-level dedup: clears runs from blocks whose text duplicates higher-priority blocks
  - Priority: block 0 (label) > block 1 (tech) > block 2 (note)
  - Case-insensitive, whitespace-normalised comparison
  - String-level dedup for plantuml parser output
  - Dedup applied during from_dict (both overlay-2.0 and legacy paths)
  - Unique values are preserved unchanged
"""
from __future__ import annotations

import os
import sys

import pytest


from models import (
    AnnotationContents,
    TextBlock,
    TextRun,
    CharFormat,
    _dedup_blocks,
)
from plantuml.parser import _dedup_label_tech_note


# ── _dedup_blocks tests ─────────────────────────────────────────────────

class TestDedupBlocks:
    """_dedup_blocks clears duplicate block runs."""

    def test_no_dupes_unchanged(self):
        blocks = [
            TextBlock(runs=[TextRun(type="text", text="Label")]),
            TextBlock(runs=[TextRun(type="text", text="Tech")]),
            TextBlock(runs=[TextRun(type="text", text="Note")]),
        ]
        _dedup_blocks(blocks)
        assert blocks[0].plain_text() == "Label"
        assert blocks[1].plain_text() == "Tech"
        assert blocks[2].plain_text() == "Note"

    def test_tech_dupes_label(self):
        blocks = [
            TextBlock(runs=[TextRun(type="text", text="Server")]),
            TextBlock(runs=[TextRun(type="text", text="Server")]),
            TextBlock(runs=[TextRun(type="text", text="Description")]),
        ]
        _dedup_blocks(blocks)
        assert blocks[0].plain_text() == "Server"
        assert blocks[1].runs == []  # cleared
        assert blocks[2].plain_text() == "Description"

    def test_note_dupes_label(self):
        blocks = [
            TextBlock(runs=[TextRun(type="text", text="Server")]),
            TextBlock(runs=[TextRun(type="text", text="Java")]),
            TextBlock(runs=[TextRun(type="text", text="Server")]),
        ]
        _dedup_blocks(blocks)
        assert blocks[0].plain_text() == "Server"
        assert blocks[1].plain_text() == "Java"
        assert blocks[2].runs == []  # cleared

    def test_note_dupes_tech(self):
        blocks = [
            TextBlock(runs=[TextRun(type="text", text="API")]),
            TextBlock(runs=[TextRun(type="text", text="REST")]),
            TextBlock(runs=[TextRun(type="text", text="REST")]),
        ]
        _dedup_blocks(blocks)
        assert blocks[0].plain_text() == "API"
        assert blocks[1].plain_text() == "REST"
        assert blocks[2].runs == []

    def test_all_three_same(self):
        blocks = [
            TextBlock(runs=[TextRun(type="text", text="Same")]),
            TextBlock(runs=[TextRun(type="text", text="Same")]),
            TextBlock(runs=[TextRun(type="text", text="Same")]),
        ]
        _dedup_blocks(blocks)
        assert blocks[0].plain_text() == "Same"
        assert blocks[1].runs == []
        assert blocks[2].runs == []

    def test_case_insensitive(self):
        blocks = [
            TextBlock(runs=[TextRun(type="text", text="Server")]),
            TextBlock(runs=[TextRun(type="text", text="server")]),
        ]
        _dedup_blocks(blocks)
        assert blocks[0].plain_text() == "Server"
        assert blocks[1].runs == []

    def test_whitespace_normalised(self):
        blocks = [
            TextBlock(runs=[TextRun(type="text", text="  My Server  ")]),
            TextBlock(runs=[TextRun(type="text", text="My  Server")]),
        ]
        _dedup_blocks(blocks)
        assert blocks[0].plain_text() == "  My Server  "
        assert blocks[1].runs == []

    def test_empty_blocks_ignored(self):
        blocks = [
            TextBlock(runs=[TextRun(type="text", text="Label")]),
            TextBlock(runs=[]),
            TextBlock(runs=[TextRun(type="text", text="Label")]),
        ]
        _dedup_blocks(blocks)
        assert blocks[0].plain_text() == "Label"
        assert blocks[1].runs == []  # was empty, stays empty
        assert blocks[2].runs == []  # cleared (dupes block 0)

    def test_single_block_unchanged(self):
        blocks = [TextBlock(runs=[TextRun(type="text", text="Only")])]
        _dedup_blocks(blocks)
        assert blocks[0].plain_text() == "Only"

    def test_multi_run_concatenation(self):
        """Dedup compares concatenated run text."""
        blocks = [
            TextBlock(runs=[
                TextRun(type="text", text="Hello "),
                TextRun(type="text", text="World"),
            ]),
            TextBlock(runs=[TextRun(type="text", text="Hello World")]),
        ]
        _dedup_blocks(blocks)
        assert blocks[0].plain_text() == "Hello World"
        assert blocks[1].runs == []


# ── _dedup_label_tech_note tests ─────────────────────────────────────────

class TestDedupLabelTechNote:
    """String-level dedup for plantuml parser."""

    def test_all_unique(self):
        assert _dedup_label_tech_note("A", "B", "C") == ("A", "B", "C")

    def test_tech_dupes_label(self):
        assert _dedup_label_tech_note("Server", "Server", "") == ("Server", "", "")

    def test_note_dupes_label(self):
        assert _dedup_label_tech_note("Server", "", "Server") == ("Server", "", "")

    def test_note_dupes_tech(self):
        assert _dedup_label_tech_note("X", "Java", "Java") == ("X", "Java", "")

    def test_all_same(self):
        assert _dedup_label_tech_note("S", "S", "S") == ("S", "", "")

    def test_case_insensitive(self):
        assert _dedup_label_tech_note("Server", "server", "") == ("Server", "", "")

    def test_whitespace_normalised(self):
        assert _dedup_label_tech_note("  A B  ", "A  B", "") == ("  A B  ", "", "")

    def test_empty_strings(self):
        assert _dedup_label_tech_note("", "", "") == ("", "", "")

    def test_label_only(self):
        assert _dedup_label_tech_note("Label", "", "") == ("Label", "", "")

    def test_note_dupes_label_tech_unique(self):
        assert _dedup_label_tech_note("Server", "Java", "Server") == ("Server", "Java", "")


# ── Dedup in from_dict integration ───────────────────────────────────────

class TestDedupInFromDict:
    """_dedup_blocks is called during AnnotationContents.from_dict."""

    def test_overlay20_dedup(self):
        d = {
            "frame": {},
            "blocks": [
                {"runs": [{"type": "text", "text": "MyService"}]},
                {"runs": [{"type": "text", "text": "Java"}]},
                {"runs": [{"type": "text", "text": "MyService"}]},
            ],
        }
        meta = AnnotationContents.from_dict(d)
        assert meta.label == "MyService"
        assert meta.tech == "Java"
        assert meta.note == ""  # cleared by dedup

    def test_legacy_dedup(self):
        d = {"label": "Server", "tech": "Server", "note": "Server"}
        meta = AnnotationContents.from_dict(d)
        assert meta.label == "Server"
        assert meta.tech == ""
        assert meta.note == ""

    def test_legacy_label_note_dedup(self):
        d = {"label": "DB", "tech": "PostgreSQL", "note": "DB"}
        meta = AnnotationContents.from_dict(d)
        assert meta.label == "DB"
        assert meta.tech == "PostgreSQL"
        assert meta.note == ""

    def test_unique_values_preserved(self):
        d = {"label": "Server", "tech": "Java", "note": "Main backend"}
        meta = AnnotationContents.from_dict(d)
        assert meta.label == "Server"
        assert meta.tech == "Java"
        assert meta.note == "Main backend"
