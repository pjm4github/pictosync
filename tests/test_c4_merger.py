"""Tests for mermaid/c4_merger.py — Step 2 of the two-step C4 pipeline.

Validates that source-parsed semantic data is correctly merged with
SVG-parsed geometry to produce enriched PictoSync annotations.
"""
from __future__ import annotations

import os

import pytest

from mermaid.c4_merger import (
    merge_c4_source_with_svg,
    _extract_svg_shapes,
    _extract_svg_boundaries,
    _extract_svg_connections,
    _normalize_label,
    _path_endpoints,
)
from mermaid.c4_source_parser import parse_c4_source_file


# ─────────────────────────────────────────────────────────
# Test fixtures — paths to test data
# ─────────────────────────────────────────────────────────

_MERMAID_DIR = "test_data/MERMAID"


def _c4(ann: dict) -> dict:
    """Extract C4 domain metadata from an annotation."""
    return ann.get("meta", {}).get("dsl", {}).get("c4", {})


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
        assert _normalize_label("Hello World") == "hello world"

    def test_extra_whitespace(self):
        assert _normalize_label("  Banking   Customer  A  ") == "banking customer a"

    def test_empty(self):
        assert _normalize_label("") == ""


class TestPathEndpoints:
    def test_simple_line(self):
        start, end = _path_endpoints("M10,20 L30,40")
        assert start == (10.0, 20.0)
        assert end == (30.0, 40.0)

    def test_relative_line(self):
        start, end = _path_endpoints("M10,20 l20,20")
        assert start == (10.0, 20.0)
        assert end == (30.0, 40.0)

    def test_cubic_bezier(self):
        start, end = _path_endpoints("M100,200 Q150,250 300,400")
        assert start == (100.0, 200.0)
        assert end == (300.0, 400.0)

    def test_empty(self):
        start, end = _path_endpoints("")
        assert start is None


# ─────────────────────────────────────────────────────────
# C4Context integration tests
# ─────────────────────────────────────────────────────────


@pytest.mark.skipif(not _have_pair("c4context"), reason="test data missing")
class TestC4ContextMerge:
    @pytest.fixture()
    def result(self):
        source = parse_c4_source_file(f"{_MERMAID_DIR}/c4context.mermaid")
        return merge_c4_source_with_svg(source, f"{_MERMAID_DIR}/c4context.svg")

    def test_output_structure(self, result):
        assert result["version"] == "draft-1"
        assert "width" in result["image"]
        assert "height" in result["image"]
        assert isinstance(result["annotations"], list)

    def test_shape_count(self, result):
        shapes = [a for a in result["annotations"] if a["kind"] not in ("line", "rect")]
        assert len(shapes) == 12

    def test_boundary_count(self, result):
        bnds = [a for a in result["annotations"] if a["kind"] == "rect"]
        assert len(bnds) == 4

    def test_rel_count(self, result):
        rels = [a for a in result["annotations"] if a["kind"] == "line"]
        assert len(rels) == 4

    def test_all_shapes_have_alias(self, result):
        shapes = [a for a in result["annotations"] if a["kind"] not in ("line", "rect")]
        for s in shapes:
            assert "alias" in _c4(s), f"Shape {s['meta']['label']} missing alias"

    def test_all_shapes_have_c4_type(self, result):
        shapes = [a for a in result["annotations"] if a["kind"] not in ("line", "rect")]
        for s in shapes:
            assert "type" in _c4(s), f"Shape {s['meta']['label']} missing c4 type"

    def test_all_shapes_have_geometry(self, result):
        shapes = [a for a in result["annotations"] if a["kind"] not in ("line", "rect")]
        for s in shapes:
            g = s["geom"]
            assert g["w"] > 0 or g["h"] > 0, (
                f"Shape {s['meta']['label']} has zero geometry"
            )

    def test_person_enrichment(self, result):
        shapes = {
            _c4(a).get("alias"): a
            for a in result["annotations"]
            if _c4(a).get("alias") and a["kind"] not in ("line", "rect")
        }
        cust = shapes["customerA"]
        assert cust["meta"]["label"] == "Banking Customer A"
        assert _c4(cust)["type"] == "person"
        assert "note" in cust["meta"]
        assert _c4(cust)["parent"] == "b0"

    def test_boundary_enrichment(self, result):
        bnds = {
            _c4(a).get("alias"): a
            for a in result["annotations"]
            if a["kind"] == "rect" and _c4(a).get("alias")
        }
        b2 = bnds["b2"]
        assert _c4(b2)["boundary_type"] == "SYSTEM"
        assert _c4(b2)["parent"] == "b1"
        # Boundary should have dashed pen style
        assert b2["style"]["pen"]["dash"] == "dashed"

    def test_rel_enrichment(self, result):
        rels = [a for a in result["annotations"] if a["kind"] == "line"]
        smtp_rel = next(
            r for r in rels if r["meta"].get("tech") == "SMTP"
        )
        assert _c4(smtp_rel)["from"] == "SystemAA"
        assert _c4(smtp_rel)["to"] == "SystemC"
        assert smtp_rel["meta"]["label"] == "Sends e-mails"

    def test_birel_matched(self, result):
        rels = [a for a in result["annotations"] if a["kind"] == "line"]
        birels = [r for r in rels if _c4(r).get("rel_type") == "birel"]
        assert len(birels) == 2


# ─────────────────────────────────────────────────────────
# C4Container integration tests
# ─────────────────────────────────────────────────────────


@pytest.mark.skipif(not _have_pair("c4container"), reason="test data missing")
class TestC4ContainerMerge:
    @pytest.fixture()
    def result(self):
        source = parse_c4_source_file(f"{_MERMAID_DIR}/c4container.mermaid")
        return merge_c4_source_with_svg(source, f"{_MERMAID_DIR}/c4container.svg")

    def test_shape_count(self, result):
        shapes = [a for a in result["annotations"] if a["kind"] not in ("line", "rect")]
        assert len(shapes) == 8

    def test_container_tech(self, result):
        shapes = {
            _c4(a).get("alias"): a
            for a in result["annotations"]
            if _c4(a).get("alias") and a["kind"] not in ("line", "rect")
        }
        spa = shapes["spa"]
        assert spa["meta"]["tech"] == "JavaScript, Angular"
        assert _c4(spa)["type"] == "container"

    def test_container_db_is_cylinder(self, result):
        shapes = {
            _c4(a).get("alias"): a
            for a in result["annotations"]
            if _c4(a).get("alias") and a["kind"] not in ("line", "rect")
        }
        db = shapes["database"]
        assert db["kind"] == "cylinder"
        assert _c4(db)["type"] == "container_db"
        assert db["meta"]["tech"] == "SQL Database"

    def test_external_container_db_is_cylinder(self, result):
        shapes = {
            _c4(a).get("alias"): a
            for a in result["annotations"]
            if _c4(a).get("alias") and a["kind"] not in ("line", "rect")
        }
        api = shapes["backend_api"]
        assert api["kind"] == "cylinder"
        assert _c4(api)["type"] == "external_container_db"

    def test_rel_back_arrow(self, result):
        rels = [a for a in result["annotations"] if a["kind"] == "line"]
        rel_b = next(r for r in rels if _c4(r).get("rel_type") == "rel_b")
        assert _c4(rel_b)["from"] == "database"
        assert _c4(rel_b)["to"] == "backend_api"
        assert rel_b["style"]["arrow"] == "start"

    def test_all_rels_matched(self, result):
        rels = [a for a in result["annotations"] if a["kind"] == "line"]
        assert len(rels) == 10
        matched = sum(1 for r in rels if "from" in _c4(r))
        assert matched == 10


# ─────────────────────────────────────────────────────────
# C4Component integration tests
# ─────────────────────────────────────────────────────────


@pytest.mark.skipif(not _have_pair("c4component"), reason="test data missing")
class TestC4ComponentMerge:
    @pytest.fixture()
    def result(self):
        source = parse_c4_source_file(f"{_MERMAID_DIR}/c4component.mermaid")
        return merge_c4_source_with_svg(source, f"{_MERMAID_DIR}/c4component.svg")

    def test_shape_count(self, result):
        shapes = [a for a in result["annotations"] if a["kind"] not in ("line", "rect")]
        assert len(shapes) == 8

    def test_component_inside_boundary(self, result):
        shapes = {
            _c4(a).get("alias"): a
            for a in result["annotations"]
            if _c4(a).get("alias") and a["kind"] not in ("line", "rect")
        }
        sign = shapes["sign"]
        assert _c4(sign)["type"] == "component"
        assert _c4(sign)["parent"] == "api"

    def test_all_rels_matched(self, result):
        rels = [a for a in result["annotations"] if a["kind"] == "line"]
        assert len(rels) == 8
        matched = sum(1 for r in rels if "from" in _c4(r))
        assert matched == 8

    def test_container_db_is_cylinder(self, result):
        """ContainerDb shapes should be imported as cylinder kind."""
        shapes = {
            _c4(a).get("alias"): a
            for a in result["annotations"]
            if _c4(a).get("alias") and a["kind"] not in ("line", "rect")
        }
        db = shapes["db"]
        assert db["kind"] == "cylinder"
        assert _c4(db)["type"] == "container_db"
        assert db["geom"]["w"] > 0
        assert db["geom"]["h"] > 0
