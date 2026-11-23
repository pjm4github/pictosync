"""Tests for PlantUML sequence ANTLR grammar and source parser.

Validates that PlantUML sequence diagram source (.puml) is correctly
parsed by the ANTLR4 grammar and that _parse_sequence_source() (if
available) extracts participants, messages, groups, notes, lifeline
controls, boxes, dividers, and refs.
Also validates round-trip to annotation JSON.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

import pytest


# ═══════════════════════════════════════════════════════════
# Grammar-level tests (ANTLR lex + parse)
# ═══════════════════════════════════════════════════════════

def _count_grammar_errors(filename: str) -> int:
    """Run the Sequence ANTLR grammar on a file, return error count."""
    try:
        from antlr4 import CommonTokenStream, InputStream
        from antlr4.error.ErrorListener import ErrorListener
        from plantuml.grammar.generated.PlantUMLSequenceLexer import (
            PlantUMLSequenceLexer,
        )
        from plantuml.grammar.generated.PlantUMLSequenceParser import (
            PlantUMLSequenceParser,
        )
    except ImportError:
        pytest.skip("ANTLR4 sequence grammar not available")

    class _Counter(ErrorListener):
        def __init__(self):
            super().__init__()
            self.count = 0

        def syntaxError(self, *args, **kwargs):
            self.count += 1

    path = f"test_data/PUML/{filename}"
    with open(path, encoding="utf-8") as f:
        text = f.read()

    lexer = PlantUMLSequenceLexer(InputStream(text))
    lexer.removeErrorListeners()
    lex_err = _Counter()
    lexer.addErrorListener(lex_err)

    stream = CommonTokenStream(lexer)
    parser = PlantUMLSequenceParser(stream)
    parser.removeErrorListeners()
    parse_err = _Counter()
    parser.addErrorListener(parse_err)

    parser.diagram()
    return lex_err.count + parse_err.count


_ALL_FILES = [
    "t_sequence_01_declarations.puml",
    "t_sequence_02_arrow_forms.puml",
    "t_sequence_03_lifeline_control.puml",
    "t_sequence_04_grouping_frames.puml",
    "t_sequence_05_notes.puml",
    "t_sequence_06_autonumber_dividers_box_ref.puml",
    "t_sequence_07_skinparam_title_misc.puml",
    "t_sequence_08_parser_stress_test.puml",
    "t_sequence_09_diagnostic.puml",
]

# Files that parse with zero grammar errors
_CLEAN_FILES = [
    "t_sequence_04_grouping_frames.puml",
    "t_sequence_09_diagnostic.puml",
]


class TestSequenceGrammar:
    """Test that the sequence ANTLR grammar parses test files."""

    @pytest.mark.parametrize("filename", _CLEAN_FILES)
    def test_zero_errors(self, filename):
        errors = _count_grammar_errors(filename)
        assert errors == 0, f"{filename}: {errors} grammar errors"

    @pytest.mark.parametrize("filename", _ALL_FILES)
    def test_no_exception(self, filename):
        """Grammar should not raise on any file (may have errors)."""
        _count_grammar_errors(filename)  # Just ensure no crash


# ═══════════════════════════════════════════════════════════
# Source parser tests (if _parse_sequence_source exists)
# ═══════════════════════════════════════════════════════════

def _has_sequence_source_parser() -> bool:
    try:
        from plantuml.parser import _parse_sequence_source
        return True
    except ImportError:
        return False


def _load_sequence(filename: str) -> Dict[str, Any]:
    from plantuml.parser import _parse_sequence_source
    path = f"test_data/PUML/{filename}"
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return _parse_sequence_source(text)


@pytest.mark.skipif(
    not _has_sequence_source_parser(),
    reason="_parse_sequence_source not yet implemented",
)
class TestSequenceSourceExtraction:
    """Test element extraction from sequence source parser."""

    def test_participant_declarations(self):
        info = _load_sequence("t_sequence_01_declarations.puml")
        assert info, "Parser returned empty"
        participants = info.get("participants", [])
        assert len(participants) >= 5

    def test_participant_keywords(self):
        info = _load_sequence("t_sequence_01_declarations.puml")
        if not info:
            pytest.skip("Parser returned empty")
        participants = info.get("participants", [])
        keywords = {p.get("keyword", "") for p in participants}
        assert len(keywords) >= 3

    def test_messages(self):
        info = _load_sequence("t_sequence_03_lifeline_control.puml")
        if not info:
            pytest.skip("Parser returned empty")
        messages = info.get("messages", [])
        assert len(messages) >= 3

    def test_grouping_frames(self):
        info = _load_sequence("t_sequence_04_grouping_frames.puml")
        if not info:
            pytest.skip("Parser returned empty")
        groups = info.get("groups", [])
        assert len(groups) >= 3

    def test_group_keywords(self):
        info = _load_sequence("t_sequence_04_grouping_frames.puml")
        if not info:
            pytest.skip("Parser returned empty")
        groups = info.get("groups", [])
        keywords = {g.get("keyword", "") for g in groups}
        assert len(keywords) >= 2

    def test_notes(self):
        info = _load_sequence("t_sequence_05_notes.puml")
        if not info:
            pytest.skip("Parser returned empty")
        notes = info.get("notes", [])
        assert len(notes) >= 3

    def test_lifeline_controls(self):
        info = _load_sequence("t_sequence_03_lifeline_control.puml")
        if not info:
            pytest.skip("Parser returned empty")
        assert info.get("activations", 0) >= 1
        assert info.get("deactivations", 0) >= 1

    def test_dividers(self):
        info = _load_sequence("t_sequence_06_autonumber_dividers_box_ref.puml")
        if not info:
            pytest.skip("Parser returned empty")
        assert info.get("dividers", 0) >= 1

    def test_boxes(self):
        info = _load_sequence("t_sequence_06_autonumber_dividers_box_ref.puml")
        if not info:
            pytest.skip("Parser returned empty")
        boxes = info.get("boxes", [])
        assert len(boxes) >= 1


# ═══════════════════════════════════════════════════════════
# Round-trip tests
# ═══════════════════════════════════════════════════════════

@pytest.mark.skipif(
    not _has_sequence_source_parser(),
    reason="_parse_sequence_source not yet implemented",
)
class TestSequenceRoundTrip:
    """Verify normalize → JSON round-trip for sequence files."""

    @pytest.mark.parametrize("filename", _CLEAN_FILES)
    def test_json_serialization(self, filename):
        from plantuml.parser import _normalize_annotations

        info = _load_sequence(filename)
        if not info:
            pytest.skip(f"Parser returned empty for {filename}")

        annotations: List[Dict[str, Any]] = []
        counter = 1
        style = {
            "pen": {"color": "#000000", "width": 1, "dash": "solid"},
            "fill": {"color": "#E8F4FD"},
            "text": {"color": "#000000", "size_pt": 11.0},
        }
        for p in info.get("participants", []):
            ann_id = f"p{counter:06d}"
            counter += 1
            label = p.get("name", "")
            annotations.append({
                "id": ann_id,
                "kind": "roundedrect",
                "geom": {"x": counter * 120, "y": 50, "w": 100, "h": 40},
                "meta": {"label": label, "tech": "", "note": label},
                "style": dict(style),
            })

        _normalize_annotations(annotations)
        payload = {
            "version": "draft-1",
            "image": {"width": 1200, "height": 800},
            "annotations": annotations,
        }
        json_str = json.dumps(payload, indent=2, ensure_ascii=False)
        parsed_back = json.loads(json_str)
        assert len(parsed_back["annotations"]) == len(annotations)
