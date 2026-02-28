"""Tests for mermaid/c4_source_parser.py — Step 1 of the two-step C4 pipeline.

Validates that C4 source text (.mmd/.mermaid) is correctly parsed into
shapes, boundaries, and relationships for all five C4 diagram types.
"""
from __future__ import annotations

import pytest
from mermaid.c4_source_parser import (
    C4Boundary,
    C4ParseResult,
    C4Rel,
    C4Shape,
    _extract_attributes,
    parse_c4_source,
    parse_c4_source_file,
)


# ═══════════════════════════════════════════════════════════
# _extract_attributes unit tests
# ═══════════════════════════════════════════════════════════

class TestExtractAttributes:
    """Unit tests for the attribute extraction helper."""

    def test_quoted_strings(self):
        assert _extract_attributes('"hello", "world"') == ["hello", "world"]

    def test_bare_identifiers(self):
        assert _extract_attributes("foo, bar") == ["foo", "bar"]

    def test_mixed_quoted_and_bare(self):
        assert _extract_attributes('alias, "Label Text"') == ["alias", "Label Text"]

    def test_dollar_attributes_skipped(self):
        attrs = _extract_attributes('"a", "b", $tags="v1.0"')
        assert attrs == ["a", "b"]

    def test_dollar_with_equals(self):
        attrs = _extract_attributes('alias, "Label", $fontColor="red", $bgColor="grey"')
        assert attrs == ["alias", "Label"]

    def test_empty_input(self):
        assert _extract_attributes("") == []

    def test_single_quoted(self):
        assert _extract_attributes('"only"') == ["only"]

    def test_commas_inside_quotes(self):
        attrs = _extract_attributes('"a, b, c", "d"')
        assert attrs == ["a, b, c", "d"]

    def test_whitespace_stripping(self):
        attrs = _extract_attributes('  alias , "Label"  ')
        assert attrs == ["alias", "Label"]


# ═══════════════════════════════════════════════════════════
# C4Context parsing
# ═══════════════════════════════════════════════════════════

class TestC4Context:
    """Test parsing of the c4context.mermaid test file."""

    @pytest.fixture()
    def result(self) -> C4ParseResult:
        return parse_c4_source_file("test_data/MERMAID/c4context.mermaid")

    def test_diagram_type(self, result):
        assert result.diagram_type == "C4Context"

    def test_title(self, result):
        assert result.title == "System Context diagram for Internet Banking System"

    def test_shape_count(self, result):
        assert len(result.shapes) == 12

    def test_boundary_count(self, result):
        assert len(result.boundaries) == 4

    def test_rel_count(self, result):
        assert len(result.rels) == 4

    def test_person_shape(self, result):
        s = next(s for s in result.shapes if s.alias == "customerA")
        assert s.label == "Banking Customer A"
        assert s.c4_type == "person"
        assert s.descr.startswith("A customer of the bank")
        assert s.parent_boundary == "b0"

    def test_external_person(self, result):
        s = next(s for s in result.shapes if s.alias == "customerC")
        assert s.c4_type == "external_person"
        assert s.descr == "desc"

    def test_system_db_ext(self, result):
        s = next(s for s in result.shapes if s.alias == "SystemE")
        assert s.c4_type == "external_system_db"
        assert s.parent_boundary == "b1"

    def test_system_queue(self, result):
        s = next(s for s in result.shapes if s.alias == "SystemF")
        assert s.c4_type == "system_queue"
        assert s.parent_boundary == "b3"

    def test_nested_boundaries(self, result):
        aliases = {b.alias: b for b in result.boundaries}
        assert aliases["b0"].parent_boundary == "global"
        assert aliases["b1"].parent_boundary == "b0"
        assert aliases["b2"].parent_boundary == "b1"
        assert aliases["b3"].parent_boundary == "b1"

    def test_boundary_types(self, result):
        aliases = {b.alias: b for b in result.boundaries}
        assert aliases["b0"].boundary_type == "ENTERPRISE"
        assert aliases["b1"].boundary_type == "ENTERPRISE"
        assert aliases["b2"].boundary_type == "SYSTEM"
        assert aliases["b3"].boundary_type == "boundary"

    def test_birel(self, result):
        birels = [r for r in result.rels if r.rel_type == "birel"]
        assert len(birels) == 2
        assert birels[0].from_alias == "customerA"
        assert birels[0].to_alias == "SystemAA"

    def test_rel_with_tech(self, result):
        r = next(r for r in result.rels if r.tech == "SMTP")
        assert r.from_alias == "SystemAA"
        assert r.to_alias == "SystemC"
        assert r.label == "Sends e-mails"


# ═══════════════════════════════════════════════════════════
# C4Container parsing
# ═══════════════════════════════════════════════════════════

class TestC4Container:
    """Test parsing of the c4container.mermaid test file."""

    @pytest.fixture()
    def result(self) -> C4ParseResult:
        return parse_c4_source_file("test_data/MERMAID/c4container.mermaid")

    def test_diagram_type(self, result):
        assert result.diagram_type == "C4Container"

    def test_shape_count(self, result):
        assert len(result.shapes) == 8

    def test_container_with_tech(self, result):
        s = next(s for s in result.shapes if s.alias == "spa")
        assert s.c4_type == "container"
        assert s.tech == "JavaScript, Angular"
        assert s.parent_boundary == "c1"

    def test_container_db(self, result):
        s = next(s for s in result.shapes if s.alias == "database")
        assert s.c4_type == "container_db"
        assert s.tech == "SQL Database"

    def test_external_container_db(self, result):
        s = next(s for s in result.shapes if s.alias == "backend_api")
        assert s.c4_type == "external_container_db"
        assert s.tech == "Java, Docker Container"

    def test_person_no_tech(self, result):
        s = next(s for s in result.shapes if s.alias == "customer")
        assert s.c4_type == "person"
        assert s.tech == ""

    def test_rel_back(self, result):
        r = next(r for r in result.rels if r.rel_type == "rel_b")
        assert r.from_alias == "database"
        assert r.to_alias == "backend_api"
        assert r.tech == "sync, JDBC"

    def test_dollar_tags_ignored(self, result):
        """Verify $tags parameters are stripped from shapes."""
        s = next(s for s in result.shapes if s.alias == "email_system")
        assert s.label == "E-Mail System"
        assert s.descr == "The internal Microsoft Exchange system"


# ═══════════════════════════════════════════════════════════
# C4Component parsing
# ═══════════════════════════════════════════════════════════

class TestC4Component:
    """Test parsing of the c4component.mermaid test file."""

    @pytest.fixture()
    def result(self) -> C4ParseResult:
        return parse_c4_source_file("test_data/MERMAID/c4component.mermaid")

    def test_diagram_type(self, result):
        assert result.diagram_type == "C4Component"

    def test_shape_count(self, result):
        assert len(result.shapes) == 8

    def test_component_with_tech(self, result):
        s = next(s for s in result.shapes if s.alias == "sign")
        assert s.c4_type == "component"
        assert s.tech == "MVC Rest Controller"
        assert s.parent_boundary == "api"

    def test_container_boundary(self, result):
        assert len(result.boundaries) == 1
        b = result.boundaries[0]
        assert b.alias == "api"
        assert b.label == "API Application"
        assert b.boundary_type == "CONTAINER"

    def test_rels_inside_boundary(self, result):
        """Rels defined inside a boundary block are still captured."""
        r = next(r for r in result.rels if r.from_alias == "sign")
        assert r.to_alias == "security"

    def test_rel_back_with_tech(self, result):
        r = next(r for r in result.rels if r.rel_type == "rel_b")
        assert r.from_alias == "spa"
        assert r.to_alias == "sign"
        assert r.tech == "JSON/HTTPS"


# ═══════════════════════════════════════════════════════════
# C4Dynamic parsing
# ═══════════════════════════════════════════════════════════

class TestC4Dynamic:
    """Test parsing of the c4dynamic.mermaid test file."""

    @pytest.fixture()
    def result(self) -> C4ParseResult:
        return parse_c4_source_file("test_data/MERMAID/c4dynamic.mermaid")

    def test_diagram_type(self, result):
        assert result.diagram_type == "C4Dynamic"

    def test_shape_count(self, result):
        assert len(result.shapes) == 4

    def test_rel_count(self, result):
        assert len(result.rels) == 3

    def test_jdbc_rel(self, result):
        r = next(r for r in result.rels if r.tech == "JDBC")
        assert r.from_alias == "c3"
        assert r.to_alias == "c4"
        assert "select * from users" in r.label


# ═══════════════════════════════════════════════════════════
# C4Deployment parsing
# ═══════════════════════════════════════════════════════════

class TestC4Deployment:
    """Test parsing of the c4deployment.mermaid test file."""

    @pytest.fixture()
    def result(self) -> C4ParseResult:
        return parse_c4_source_file("test_data/MERMAID/c4deployment.mermaid")

    def test_diagram_type(self, result):
        assert result.diagram_type == "C4Deployment"

    def test_shape_count(self, result):
        assert len(result.shapes) == 6

    def test_boundary_count(self, result):
        """12 deployment nodes as boundaries."""
        assert len(result.boundaries) == 12

    def test_deep_nesting(self, result):
        """Verify multi-level boundary nesting: plc > dn > apache > api."""
        aliases = {b.alias: b for b in result.boundaries}
        assert aliases["plc"].parent_boundary == "global"
        assert aliases["dn"].parent_boundary == "plc"
        assert aliases["apache"].parent_boundary == "dn"
        # Shape inside deepest boundary
        s = next(s for s in result.shapes if s.alias == "api")
        assert s.parent_boundary == "apache"

    def test_rel_u(self, result):
        r = next(r for r in result.rels if r.rel_type == "rel_u")
        assert r.from_alias == "web"
        assert r.to_alias == "spa"

    def test_rel_r(self, result):
        r = next(r for r in result.rels if r.rel_type == "rel_r")
        assert r.from_alias == "db"
        assert r.to_alias == "db2"

    def test_deployment_node_tech(self, result):
        """Deployment nodes store tech in the boundary label, not in shapes."""
        aliases = {b.alias: b for b in result.boundaries}
        assert aliases["oracle"].label == "Oracle - Primary"
        assert aliases["oracle"].boundary_type == "node"


# ═══════════════════════════════════════════════════════════
# Error handling
# ═══════════════════════════════════════════════════════════

class TestErrorHandling:
    """Test error cases."""

    def test_non_c4_raises(self):
        with pytest.raises(ValueError, match="Not a C4 diagram"):
            parse_c4_source("flowchart LR\n  A --> B")

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="Not a C4 diagram"):
            parse_c4_source("")


# ═══════════════════════════════════════════════════════════
# Inline source tests (no file dependency)
# ═══════════════════════════════════════════════════════════

class TestInlineParsing:
    """Test parsing from inline source strings."""

    def test_minimal_c4context(self):
        src = """C4Context
        Person(user, "User")
        System(sys, "System")
        Rel(user, sys, "Uses")
        """
        r = parse_c4_source(src)
        assert r.diagram_type == "C4Context"
        assert len(r.shapes) == 2
        assert len(r.rels) == 1

    def test_comments_stripped(self):
        src = """C4Context
        %% This is a comment
        Person(user, "User") %% inline comment
        """
        r = parse_c4_source(src)
        assert len(r.shapes) == 1
        assert r.shapes[0].alias == "user"

    def test_title_extraction(self):
        src = """C4Context
        title My Diagram Title
        Person(a, "A")
        """
        r = parse_c4_source(src)
        assert r.title == "My Diagram Title"

    def test_style_keywords_skipped(self):
        src = """C4Context
        Person(a, "A")
        UpdateElementStyle(a, $fontColor="red")
        UpdateLayoutConfig($c4ShapeInRow="3")
        """
        r = parse_c4_source(src)
        assert len(r.shapes) == 1
        assert len(r.rels) == 0

    def test_boundary_nesting_and_pop(self):
        src = """C4Context
        Enterprise_Boundary(b1, "Outer") {
            Person(p1, "Inside")
            System_Boundary(b2, "Inner") {
                System(s1, "Deep")
            }
        }
        Person(p2, "Outside")
        """
        r = parse_c4_source(src)
        assert r.shapes[0].parent_boundary == "b1"  # p1
        assert r.shapes[1].parent_boundary == "b2"  # s1
        assert r.shapes[2].parent_boundary == "global"  # p2

    def test_html_br_in_descr(self):
        src = """C4Context
        Person(u, "User", "Line 1, <br/> Line 2")
        """
        r = parse_c4_source(src)
        assert "<br/>" in r.shapes[0].descr
