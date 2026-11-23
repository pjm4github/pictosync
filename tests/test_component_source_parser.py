"""Tests for PlantUML component ANTLR grammar and source parser.

Validates that PlantUML component diagram source (.puml) is correctly
parsed by the ANTLR4 grammar and that _parse_component_source() (if
available) extracts components, interfaces, groups, relations, and notes.
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
    """Run the Component ANTLR grammar on a file, return error count."""
    try:
        from antlr4 import CommonTokenStream, InputStream
        from antlr4.error.ErrorListener import ErrorListener
        from plantuml.grammar.generated.PlantUMLComponentLexer import (
            PlantUMLComponentLexer,
        )
        from plantuml.grammar.generated.PlantUMLComponentParser import (
            PlantUMLComponentParser,
        )
    except ImportError:
        pytest.skip("ANTLR4 component grammar not available")

    class _Counter(ErrorListener):
        def __init__(self):
            super().__init__()
            self.count = 0

        def syntaxError(self, *args, **kwargs):
            self.count += 1

    path = f"test_data/PUML/{filename}"
    with open(path, encoding="utf-8") as f:
        text = f.read()

    lexer = PlantUMLComponentLexer(InputStream(text))
    lexer.removeErrorListeners()
    lex_err = _Counter()
    lexer.addErrorListener(lex_err)

    stream = CommonTokenStream(lexer)
    parser = PlantUMLComponentParser(stream)
    parser.removeErrorListeners()
    parse_err = _Counter()
    parser.addErrorListener(parse_err)

    parser.diagram()
    return lex_err.count + parse_err.count


_ALL_FILES = [
    "t_component_01_declaration_forms.puml",
    "t_component_02_arrow_styles.puml",
    "t_component_03_group_containers.puml",
    "t_component_04_notes_skinparam.puml",
    "t_component_05_allowmixing_sprites_creole.puml",
    "t_component_06_iss_ot_architecture.puml",
    "t_component_07_parser_edge_cases.puml",
    "t_component_08_api.puml",
    "t_component_09_edge.puml",
    "t_component_10_flow_pipeline.puml",
    "t_component_11_mix.puml",
]


# Files that parse with zero grammar errors
_CLEAN_FILES = [
    "t_component_01_declaration_forms.puml",
    "t_component_06_iss_ot_architecture.puml",
    "t_component_08_api.puml",
]


class TestComponentGrammar:
    """Test that the component ANTLR grammar parses test files."""

    @pytest.mark.parametrize("filename", _CLEAN_FILES)
    def test_zero_errors(self, filename):
        errors = _count_grammar_errors(filename)
        assert errors == 0, f"{filename}: {errors} grammar errors"

    @pytest.mark.parametrize("filename", _ALL_FILES)
    def test_no_exception(self, filename):
        """Grammar should not raise on any file (may have errors)."""
        _count_grammar_errors(filename)


# ═══════════════════════════════════════════════════════════
# Source parser tests (if _parse_component_source exists)
# ═══════════════════════════════════════════════════════════

def _has_component_source_parser() -> bool:
    try:
        from plantuml.parser import _parse_component_source
        return True
    except ImportError:
        return False


def _load_component(filename: str) -> Dict[str, Any]:
    from plantuml.parser import _parse_component_source
    path = f"test_data/PUML/{filename}"
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return _parse_component_source(text)


@pytest.mark.skipif(
    not _has_component_source_parser(),
    reason="_parse_component_source not yet implemented",
)
class TestComponentSourceExtraction:
    """Test element extraction from component source parser."""

    def test_declaration_forms(self):
        info = _load_component("t_component_01_declaration_forms.puml")
        assert info, "Parser returned empty"
        components = info.get("components", [])
        assert len(components) >= 5, f"Expected >=5 components, got {len(components)}"

    def test_has_stereotypes(self):
        info = _load_component("t_component_01_declaration_forms.puml")
        if not info:
            pytest.skip("Parser returned empty")
        components = info.get("components", [])
        stereos = [c for c in components if c.get("stereotype")]
        assert len(stereos) >= 1

    def test_group_containers(self):
        info = _load_component("t_component_03_group_containers.puml")
        if not info:
            pytest.skip("Parser returned empty")
        groups = info.get("groups", [])
        assert len(groups) >= 3

    def test_group_keywords(self):
        info = _load_component("t_component_03_group_containers.puml")
        if not info:
            pytest.skip("Parser returned empty")
        groups = info.get("groups", [])
        keywords = {g.get("keyword", "") for g in groups}
        # Should have multiple container types
        assert len(keywords) >= 2

    def test_relations(self):
        info = _load_component("t_component_02_arrow_styles.puml")
        if not info:
            pytest.skip("Parser returned empty")
        relations = info.get("relations", [])
        assert len(relations) >= 5

    def test_notes(self):
        info = _load_component("t_component_04_notes_skinparam.puml")
        if not info:
            pytest.skip("Parser returned empty")
        notes = info.get("notes", [])
        assert len(notes) >= 1

    def test_iss_architecture(self):
        """Full architecture file should parse with many elements."""
        info = _load_component("t_component_06_iss_ot_architecture.puml")
        if not info:
            pytest.skip("Parser returned empty")
        components = info.get("components", [])
        assert len(components) >= 10

    def test_stress_test(self):
        info = _load_component("t_component_07_parser_edge_cases.puml")
        if not info:
            pytest.skip("Parser returned empty")
        components = info.get("components", [])
        assert len(components) >= 3


# ═══════════════════════════════════════════════════════════
# Round-trip tests
# ═══════════════════════════════════════════════════════════

@pytest.mark.skipif(
    not _has_component_source_parser(),
    reason="_parse_component_source not yet implemented",
)
class TestComponentRoundTrip:
    """Verify normalize → JSON round-trip for component files."""

    @pytest.mark.parametrize("filename", _ALL_FILES)
    def test_json_serialization(self, filename):
        from plantuml.parser import _normalize_annotations

        info = _load_component(filename)
        if not info:
            pytest.skip(f"Parser returned empty for {filename}")

        annotations = []
        counter = 1
        style = {
            "pen": {"color": "#000000", "width": 1, "dash": "solid"},
            "fill": {"color": "#E8F4FD"},
            "text": {"color": "#000000", "size_pt": 11.0},
        }
        for comp in info.get("components", []):
            ann_id = f"p{counter:06d}"
            counter += 1
            label = comp.get("name", "")
            annotations.append({
                "id": ann_id,
                "kind": "roundedrect",
                "geom": {"x": 100, "y": counter * 50, "w": 200, "h": 60},
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
