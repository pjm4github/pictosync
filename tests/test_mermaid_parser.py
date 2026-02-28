"""
tests/test_mermaid_parser.py

Validate that the Mermaid SVG parser correctly converts all visual entities
from each of the 21 supported diagram types into PictoSync annotations.

Ground-truth counts were established by manual inspection of each test SVG
and verified against the raw SVG element inventory.
"""

from __future__ import annotations

import glob
import os
import re

import pytest

from mermaid.parser import detect_mermaid_svg, parse_mermaid_svg_to_annotations


# ─────────────────────────────────────────────────────────
# Test data directory
# ─────────────────────────────────────────────────────────

_SVG_DIR = os.path.join(os.path.dirname(__file__), "..", "test_data", "MERMAID")

# Valid annotation kinds per the PictoSync schema
_VALID_KINDS = {
    "rect", "roundedrect", "ellipse", "line", "text",
    "hexagon", "cylinder", "blockarrow", "polygon",
    "curve", "orthocurve", "isocube", "group",
}

# Required geometry keys per annotation kind
_GEOM_KEYS = {
    "rect":        {"x", "y", "w", "h"},
    "roundedrect": {"x", "y", "w", "h"},
    "ellipse":     {"x", "y", "w", "h"},
    "hexagon":     {"x", "y", "w", "h"},
    "cylinder":    {"x", "y", "w", "h"},
    "blockarrow":  {"x", "y", "w", "h"},
    "isocube":     {"x", "y", "w", "h"},
    "polygon":     {"x", "y", "w", "h", "points"},
    "curve":       {"x", "y", "w", "h", "nodes"},
    "orthocurve":  {"x", "y", "w", "h", "nodes"},
    "line":        {"x1", "y1", "x2", "y2"},
    "text":        {"x", "y"},
    "group":       set(),  # group geom is optional / via children
}


# ─────────────────────────────────────────────────────────
# Ground truth: expected parser output per test SVG
#
#   type      – aria-roledescription value detected
#   total     – total annotation count
#   kinds     – exact kind → count breakdown
#   min_w/h   – minimum expected canvas dimensions
# ─────────────────────────────────────────────────────────

GROUND_TRUTH = {
    "architecture1.svg": {
        "type": "architecture",
        "total": 9,
        "kinds": {"group": 1, "line": 2, "rect": 3, "text": 3},
        "min_w": 400, "min_h": 400,
    },
    "block1.svg": {
        "type": "block",
        "total": 9,
        "kinds": {"curve": 1, "line": 3, "polygon": 1, "rect": 4},
        "min_w": 200, "min_h": 100,
    },
    "c4context1.svg": {
        "type": "c4",
        "total": 9,
        "kinds": {"curve": 3, "line": 1, "roundedrect": 5},
        "min_w": 800, "min_h": 800,
    },
    "class1.svg": {
        "type": "class",
        "total": 7,
        "kinds": {"curve": 2, "line": 1, "roundedrect": 4},
        "min_w": 300, "min_h": 500,
    },
    "er1.svg": {
        "type": "er",
        "total": 7,
        "kinds": {"curve": 2, "line": 1, "rect": 4},
        "min_w": 400, "min_h": 700,
    },
    "flowchart1.svg": {
        "type": "flowchart-v2",
        "total": 11,
        "kinds": {"curve": 4, "line": 1, "polygon": 1, "rect": 4, "roundedrect": 1},
        "min_w": 400, "min_h": 500,
    },
    "gantt1.svg": {
        "type": "gantt",
        "total": 10,
        "kinds": {"roundedrect": 6, "text": 4},
        "min_w": 1900, "min_h": 200,
    },
    "gitgraph1.svg": {
        "type": "gitGraph",
        "total": 15,
        "kinds": {"curve": 4, "line": 8, "text": 3},
        "min_w": 400, "min_h": 200,
    },
    "journey1.svg": {
        "type": "journey",
        "total": 8,
        "kinds": {"group": 2, "roundedrect": 5, "text": 1},
        "min_w": 1200, "min_h": 500,
    },
    "kanban1.svg": {
        "type": "kanban",
        "total": 9,
        "kinds": {"group": 3, "roundedrect": 6},
        "min_w": 600, "min_h": 100,
    },
    "mindmap1.svg": {
        "type": "mindmap",
        "total": 13,
        "kinds": {"curve": 12, "ellipse": 1},
        "min_w": 600, "min_h": 400,
    },
    "packet1.svg": {
        "type": "packet",
        "total": 17,
        "kinds": {"rect": 16, "text": 1},
        "min_w": 1000, "min_h": 300,
    },
    "pie1.svg": {
        "type": "pie",
        "total": 12,
        "kinds": {"ellipse": 1, "rect": 5, "roundedrect": 5, "text": 1},
        "min_w": 600, "min_h": 400,
    },
    "quadrant1.svg": {
        "type": "quadrantChart",
        "total": 15,
        "kinds": {"ellipse": 6, "rect": 4, "text": 5},
        "min_w": 500, "min_h": 500,
    },
    "requirement1.svg": {
        "type": "requirement",
        "total": 8,
        "kinds": {"curve": 4, "roundedrect": 4},
        "min_w": 400, "min_h": 600,
    },
    "sankey1.svg": {
        "type": "sankey",
        "total": 12,
        "kinds": {"curve": 4, "rect": 8},
        "min_w": 600, "min_h": 400,
    },
    "sequence1.svg": {
        "type": "sequence",
        "total": 11,
        "kinds": {"curve": 1, "line": 5, "roundedrect": 5},
        "min_w": 600, "min_h": 600,
    },
    "state1.svg": {
        "type": "stateDiagram",
        "total": 11,
        "kinds": {"curve": 6, "ellipse": 1, "rect": 1, "roundedrect": 3},
        "min_w": 90, "min_h": 300,
    },
    "timeline1.svg": {
        "type": "timeline",
        "total": 21,
        "kinds": {"roundedrect": 20, "text": 1},
        "min_w": 1900, "min_h": 500,
    },
    "xychart1.svg": {
        "type": "xychart",
        "total": 29,
        "kinds": {"curve": 1, "rect": 6, "text": 22},
        "min_w": 700, "min_h": 500,
    },
    "zenuml1.svg": {
        "type": "zenuml",
        "total": 4,
        "kinds": {"rect": 1, "text": 3},
        "min_w": 700, "min_h": 500,
    },
}

# All SVG filenames we test (sorted for deterministic order)
ALL_SVG_FILES = sorted(GROUND_TRUTH.keys())


def _svg_path(filename: str) -> str:
    """Return the absolute path to a test SVG file."""
    return os.path.normpath(os.path.join(_SVG_DIR, filename))


# ═══════════════════════════════════════════════════════════
# Detection tests
# ═══════════════════════════════════════════════════════════


class TestDetection:
    """Verify ``detect_mermaid_svg`` identifies every test SVG's diagram type."""

    @pytest.mark.parametrize("svg_file", ALL_SVG_FILES)
    def test_detect_type(self, svg_file: str) -> None:
        """Detected type matches ground-truth for each SVG."""
        expected_type = GROUND_TRUTH[svg_file]["type"]
        detected = detect_mermaid_svg(_svg_path(svg_file))
        assert detected == expected_type, (
            f"{svg_file}: expected type '{expected_type}', got '{detected}'"
        )

    def test_unrecognised_file_returns_none(self) -> None:
        """A multi-type composite SVG should not be detected."""
        path = _svg_path("mermaid_all_types.svg")
        if os.path.exists(path):
            result = detect_mermaid_svg(path)
            assert result is None, (
                f"mermaid_all_types.svg should be undetected, got '{result}'"
            )


# ═══════════════════════════════════════════════════════════
# Parsing – annotation count and kind breakdown
# ═══════════════════════════════════════════════════════════


class TestAnnotationCounts:
    """Verify the parser extracts the exact expected number of annotations."""

    @pytest.mark.parametrize("svg_file", ALL_SVG_FILES)
    def test_total_count(self, svg_file: str) -> None:
        """Total annotation count matches ground-truth."""
        expected = GROUND_TRUTH[svg_file]["total"]
        data = parse_mermaid_svg_to_annotations(_svg_path(svg_file))
        actual = len(data["annotations"])
        assert actual == expected, (
            f"{svg_file}: expected {expected} annotations, got {actual}"
        )

    @pytest.mark.parametrize("svg_file", ALL_SVG_FILES)
    def test_kind_breakdown(self, svg_file: str) -> None:
        """Per-kind annotation counts match ground-truth exactly."""
        expected_kinds = GROUND_TRUTH[svg_file]["kinds"]
        data = parse_mermaid_svg_to_annotations(_svg_path(svg_file))
        actual_kinds: dict[str, int] = {}
        for ann in data["annotations"]:
            k = ann["kind"]
            actual_kinds[k] = actual_kinds.get(k, 0) + 1
        assert actual_kinds == expected_kinds, (
            f"{svg_file}: kind mismatch\n"
            f"  expected: {expected_kinds}\n"
            f"  actual:   {actual_kinds}"
        )


# ═══════════════════════════════════════════════════════════
# Top-level structure validation
# ═══════════════════════════════════════════════════════════


class TestOutputStructure:
    """Verify the parser output matches the PictoSync annotation schema."""

    @pytest.mark.parametrize("svg_file", ALL_SVG_FILES)
    def test_top_level_keys(self, svg_file: str) -> None:
        """Output has required top-level keys: version, image, annotations."""
        data = parse_mermaid_svg_to_annotations(_svg_path(svg_file))
        assert "version" in data
        assert "image" in data
        assert "annotations" in data
        assert data["version"] == "draft-1"

    @pytest.mark.parametrize("svg_file", ALL_SVG_FILES)
    def test_image_dimensions(self, svg_file: str) -> None:
        """Canvas dimensions are positive and meet minimum thresholds."""
        gt = GROUND_TRUTH[svg_file]
        data = parse_mermaid_svg_to_annotations(_svg_path(svg_file))
        img = data["image"]
        assert "width" in img and "height" in img
        assert isinstance(img["width"], int)
        assert isinstance(img["height"], int)
        assert img["width"] >= gt["min_w"], (
            f"{svg_file}: width {img['width']} < min {gt['min_w']}"
        )
        assert img["height"] >= gt["min_h"], (
            f"{svg_file}: height {img['height']} < min {gt['min_h']}"
        )


# ═══════════════════════════════════════════════════════════
# Per-annotation validation
# ═══════════════════════════════════════════════════════════


class TestAnnotationValidity:
    """Validate every annotation has correct fields and value types."""

    @pytest.mark.parametrize("svg_file", ALL_SVG_FILES)
    def test_valid_kind(self, svg_file: str) -> None:
        """Every annotation has a kind from the schema's allowed set."""
        data = parse_mermaid_svg_to_annotations(_svg_path(svg_file))
        for ann in data["annotations"]:
            assert "kind" in ann, f"{svg_file}: annotation missing 'kind': {ann}"
            assert ann["kind"] in _VALID_KINDS, (
                f"{svg_file}: invalid kind '{ann['kind']}' in {ann['id']}"
            )

    @pytest.mark.parametrize("svg_file", ALL_SVG_FILES)
    def test_valid_id_format(self, svg_file: str) -> None:
        """Every annotation has a string ID matching the m000NNN pattern."""
        data = parse_mermaid_svg_to_annotations(_svg_path(svg_file))
        id_pattern = re.compile(r"^m\d{6}$")
        for ann in data["annotations"]:
            assert "id" in ann, f"{svg_file}: annotation missing 'id'"
            assert id_pattern.match(ann["id"]), (
                f"{svg_file}: ID '{ann['id']}' doesn't match mNNNNNN pattern"
            )

    @pytest.mark.parametrize("svg_file", ALL_SVG_FILES)
    def test_unique_ids(self, svg_file: str) -> None:
        """All annotation IDs within a parsed file are unique."""
        data = parse_mermaid_svg_to_annotations(_svg_path(svg_file))
        ids = [ann["id"] for ann in data["annotations"]]
        dupes = [aid for aid in ids if ids.count(aid) > 1]
        assert len(dupes) == 0, (
            f"{svg_file}: duplicate IDs found: {set(dupes)}"
        )

    @pytest.mark.parametrize("svg_file", ALL_SVG_FILES)
    def test_geom_keys(self, svg_file: str) -> None:
        """Each annotation's geom contains the required keys for its kind."""
        data = parse_mermaid_svg_to_annotations(_svg_path(svg_file))
        for ann in data["annotations"]:
            kind = ann["kind"]
            required = _GEOM_KEYS.get(kind, set())
            if not required:
                continue  # group geom is optional
            assert "geom" in ann, (
                f"{svg_file}/{ann['id']}: missing 'geom' for kind '{kind}'"
            )
            geom = ann["geom"]
            missing = required - set(geom.keys())
            assert not missing, (
                f"{svg_file}/{ann['id']} ({kind}): "
                f"geom missing keys {missing}, got {set(geom.keys())}"
            )

    @pytest.mark.parametrize("svg_file", ALL_SVG_FILES)
    def test_geom_numeric_values(self, svg_file: str) -> None:
        """All scalar geom values are numeric (int or float)."""
        data = parse_mermaid_svg_to_annotations(_svg_path(svg_file))
        for ann in data["annotations"]:
            geom = ann.get("geom", {})
            for key, val in geom.items():
                if key in ("points", "nodes", "children"):
                    continue  # array fields validated separately
                assert isinstance(val, (int, float)), (
                    f"{svg_file}/{ann['id']}: geom['{key}'] = {val!r} "
                    f"is {type(val).__name__}, expected numeric"
                )

    @pytest.mark.parametrize("svg_file", ALL_SVG_FILES)
    def test_shapes_have_positive_size(self, svg_file: str) -> None:
        """Shape annotations have non-negative w,h with at least one > 0.

        Arc-derived shapes (e.g. pie slices) can have one zero dimension
        when the bounding box collapses along one axis, so we require that
        not *both* w and h are zero.
        """
        shape_kinds = {"rect", "roundedrect", "ellipse", "polygon",
                       "hexagon", "cylinder", "blockarrow", "isocube"}
        data = parse_mermaid_svg_to_annotations(_svg_path(svg_file))
        for ann in data["annotations"]:
            if ann["kind"] not in shape_kinds:
                continue
            geom = ann["geom"]
            assert geom["w"] >= 0, (
                f"{svg_file}/{ann['id']}: w={geom['w']} < 0"
            )
            assert geom["h"] >= 0, (
                f"{svg_file}/{ann['id']}: h={geom['h']} < 0"
            )
            assert geom["w"] > 0 or geom["h"] > 0, (
                f"{svg_file}/{ann['id']}: both w and h are zero"
            )

    @pytest.mark.parametrize("svg_file", ALL_SVG_FILES)
    def test_has_meta(self, svg_file: str) -> None:
        """Every annotation has a meta dict."""
        data = parse_mermaid_svg_to_annotations(_svg_path(svg_file))
        for ann in data["annotations"]:
            assert "meta" in ann, (
                f"{svg_file}/{ann['id']}: missing 'meta'"
            )
            assert isinstance(ann["meta"], dict), (
                f"{svg_file}/{ann['id']}: meta is {type(ann['meta']).__name__}, "
                f"expected dict"
            )

    @pytest.mark.parametrize("svg_file", ALL_SVG_FILES)
    def test_has_style(self, svg_file: str) -> None:
        """Every annotation has a style dict."""
        data = parse_mermaid_svg_to_annotations(_svg_path(svg_file))
        for ann in data["annotations"]:
            assert "style" in ann, (
                f"{svg_file}/{ann['id']}: missing 'style'"
            )
            assert isinstance(ann["style"], dict), (
                f"{svg_file}/{ann['id']}: style is {type(ann['style']).__name__}, "
                f"expected dict"
            )


# ═══════════════════════════════════════════════════════════
# Curve and polygon geometry validation
# ═══════════════════════════════════════════════════════════


class TestComplexGeometry:
    """Validate curves have nodes and polygons have points."""

    @pytest.mark.parametrize("svg_file", ALL_SVG_FILES)
    def test_curves_have_nodes(self, svg_file: str) -> None:
        """Curve annotations have a non-empty nodes list in geom.

        Nodes are ``{cmd, x, y}`` dicts produced by
        ``_parse_path_to_curve_nodes`` with normalised 0-1 coordinates.
        """
        data = parse_mermaid_svg_to_annotations(_svg_path(svg_file))
        for ann in data["annotations"]:
            if ann["kind"] != "curve":
                continue
            nodes = ann["geom"].get("nodes", [])
            assert isinstance(nodes, list), (
                f"{svg_file}/{ann['id']}: curve nodes is {type(nodes).__name__}"
            )
            assert len(nodes) >= 2, (
                f"{svg_file}/{ann['id']}: curve has {len(nodes)} nodes, "
                f"expected >= 2"
            )
            for i, node in enumerate(nodes):
                assert isinstance(node, dict), (
                    f"{svg_file}/{ann['id']}: curve node[{i}] = {node!r}, "
                    f"expected dict with cmd/x/y"
                )
                assert "cmd" in node and "x" in node and "y" in node, (
                    f"{svg_file}/{ann['id']}: curve node[{i}] missing "
                    f"required keys (cmd/x/y), got {sorted(node.keys())}"
                )
                assert isinstance(node["x"], (int, float)), (
                    f"{svg_file}/{ann['id']}: node[{i}].x = {node['x']!r}"
                )
                assert isinstance(node["y"], (int, float)), (
                    f"{svg_file}/{ann['id']}: node[{i}].y = {node['y']!r}"
                )

    @pytest.mark.parametrize("svg_file", ALL_SVG_FILES)
    def test_polygons_have_points(self, svg_file: str) -> None:
        """Polygon annotations have a non-empty points list with normalised coords."""
        data = parse_mermaid_svg_to_annotations(_svg_path(svg_file))
        for ann in data["annotations"]:
            if ann["kind"] != "polygon":
                continue
            points = ann["geom"].get("points", [])
            assert isinstance(points, list), (
                f"{svg_file}/{ann['id']}: polygon points is "
                f"{type(points).__name__}"
            )
            assert len(points) >= 3, (
                f"{svg_file}/{ann['id']}: polygon has {len(points)} points, "
                f"expected >= 3"
            )
            for i, pt in enumerate(points):
                assert isinstance(pt, list) and len(pt) == 2, (
                    f"{svg_file}/{ann['id']}: point[{i}] = {pt!r}, "
                    f"expected [x, y] pair"
                )
                # Normalised 0-1 range
                assert 0.0 <= pt[0] <= 1.0 + 1e-6, (
                    f"{svg_file}/{ann['id']}: point[{i}][0] = {pt[0]} "
                    f"out of [0,1] range"
                )
                assert 0.0 <= pt[1] <= 1.0 + 1e-6, (
                    f"{svg_file}/{ann['id']}: point[{i}][1] = {pt[1]} "
                    f"out of [0,1] range"
                )


# ═══════════════════════════════════════════════════════════
# Group annotation validation
# ═══════════════════════════════════════════════════════════


class TestGroupAnnotations:
    """Validate group annotations have geometry (container bounds).

    Mermaid-parsed groups use geom-based containers (x, y, w, h) to
    represent section/cluster bounds rather than explicit children lists.
    """

    @pytest.mark.parametrize("svg_file", ALL_SVG_FILES)
    def test_groups_have_geom(self, svg_file: str) -> None:
        """Group annotations have bounding-box geometry."""
        data = parse_mermaid_svg_to_annotations(_svg_path(svg_file))
        for ann in data["annotations"]:
            if ann["kind"] != "group":
                continue
            assert "geom" in ann, (
                f"{svg_file}/{ann['id']}: group missing 'geom'"
            )
            geom = ann["geom"]
            assert "w" in geom and "h" in geom, (
                f"{svg_file}/{ann['id']}: group geom missing w/h, "
                f"got {sorted(geom.keys())}"
            )
            assert geom["w"] > 0 and geom["h"] > 0, (
                f"{svg_file}/{ann['id']}: group has zero-size bounds "
                f"w={geom['w']}, h={geom['h']}"
            )


# ═══════════════════════════════════════════════════════════
# Coverage check – all 21 types are tested
# ═══════════════════════════════════════════════════════════


class TestCoverage:
    """Ensure the test suite covers all supported Mermaid diagram types."""

    def test_all_types_have_test_svg(self) -> None:
        """Every supported diagram type has at least one ground-truth SVG."""
        from mermaid.parser import _SUPPORTED_DIAGRAM_TYPES

        tested_types = {gt["type"] for gt in GROUND_TRUTH.values()}
        # flowchart-v2 covers both "flowchart-v2" and "flowchart"
        tested_types.add("flowchart")
        missing = _SUPPORTED_DIAGRAM_TYPES - tested_types
        assert not missing, (
            f"Diagram types with no test SVG: {missing}"
        )

    def test_ground_truth_files_exist(self) -> None:
        """All ground-truth SVG files actually exist on disk."""
        for svg_file in ALL_SVG_FILES:
            path = _svg_path(svg_file)
            assert os.path.isfile(path), (
                f"Ground-truth SVG missing: {path}"
            )

    def test_no_untested_svg_files(self) -> None:
        """Every SVG in test_data/MERMAID/ is covered by ground-truth
        (except the composite mermaid_all_types.svg)."""
        on_disk = {
            os.path.basename(f)
            for f in glob.glob(os.path.join(_SVG_DIR, "*.svg"))
        }
        expected_skip = {"mermaid_all_types.svg"}
        untested = on_disk - set(ALL_SVG_FILES) - expected_skip
        assert not untested, (
            f"SVG files not covered by ground-truth: {untested}"
        )
