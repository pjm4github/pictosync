"""Tests for plantuml activity ANTLR source parser and round-trip.

Validates that PlantUML activity diagram source (.puml) is correctly
parsed into actions, conditions, loops, forks, containers, swimlanes,
notes, arrows, connectors, labels, and control nodes.  Also validates
the merge into annotations and JSON round-trip.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

import pytest

from plantuml.parser import (
    _merge_activity_source_info,
    _normalize_annotations,
    _parse_activity_source,
)


# ═══════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════

def _load(filename: str) -> Dict[str, Any]:
    path = f"test_data/PUML/{filename}"
    with open(path, encoding="utf-8") as f:
        text = f.read()
    result = _parse_activity_source(text)
    assert result, f"_parse_activity_source returned empty for {filename}"
    return result


@pytest.fixture()
def actions_arrows() -> Dict[str, Any]:
    return _load("t_activity_01_actions_arrows.puml")


@pytest.fixture()
def conditionals() -> Dict[str, Any]:
    return _load("t_activity_02_conditionals.puml")


@pytest.fixture()
def loops_flow() -> Dict[str, Any]:
    return _load("t_activity_03_loops_flow_control.puml")


@pytest.fixture()
def fork_split() -> Dict[str, Any]:
    return _load("t_activity_04_fork_split_parallel.puml")


@pytest.fixture()
def swimlanes() -> Dict[str, Any]:
    return _load("t_activity_05_swimlanes.puml")


@pytest.fixture()
def containers() -> Dict[str, Any]:
    return _load("t_activity_06_partitions_containers.puml")


@pytest.fixture()
def notes_skinparam() -> Dict[str, Any]:
    return _load("t_activity_07_notes_skinparam.puml")


@pytest.fixture()
def stress_test() -> Dict[str, Any]:
    return _load("t_activity_08_parser_stress_test.puml")


# ═══════════════════════════════════════════════════════════
# 01 — Actions & Arrows
# ═══════════════════════════════════════════════════════════

class TestActionsArrows:
    """Test parsing of t_activity_01_actions_arrows.puml."""

    def test_action_count(self, actions_arrows):
        assert len(actions_arrows["actions"]) >= 40

    def test_title_extracted(self, actions_arrows):
        assert "Actions" in actions_arrows["title"]

    def test_colored_actions(self, actions_arrows):
        colors = [a["color"] for a in actions_arrows["actions"] if a.get("color")]
        assert len(colors) >= 5
        assert "#Red" in colors
        assert "#Green" in colors
        assert "#Blue" in colors

    def test_stereotypes(self, actions_arrows):
        stereos = [a["stereotype"] for a in actions_arrows["actions"]
                   if a.get("stereotype")]
        assert len(stereos) >= 7
        stereo_set = set(stereos)
        assert "<<input>>" in stereo_set
        assert "<<output>>" in stereo_set
        assert "<<procedure>>" in stereo_set
        assert "<<load>>" in stereo_set
        assert "<<save>>" in stereo_set
        assert "<<continuous>>" in stereo_set
        assert "<<task>>" in stereo_set

    def test_bullet_actions(self, actions_arrows):
        bullets = [a for a in actions_arrows["actions"] if a.get("bullet")]
        assert len(bullets) >= 1

    def test_explicit_arrows(self, actions_arrows):
        assert len(actions_arrows["arrows"]) >= 8

    def test_arrow_styles(self, actions_arrows):
        styles = [a["style"] for a in actions_arrows["arrows"] if a.get("style")]
        assert len(styles) >= 4  # colored, dashed, bold, dotted, hidden

    def test_arrow_labels(self, actions_arrows):
        labeled = [a for a in actions_arrows["arrows"] if a.get("label")]
        assert len(labeled) >= 3

    def test_controls(self, actions_arrows):
        assert "start" in actions_arrows["controls"]
        assert "stop" in actions_arrows["controls"]

    def test_notes(self, actions_arrows):
        assert len(actions_arrows["notes"]) >= 1


# ═══════════════════════════════════════════════════════════
# 02 — Conditionals
# ═══════════════════════════════════════════════════════════

class TestConditionals:
    """Test parsing of t_activity_02_conditionals.puml."""

    def test_condition_count(self, conditionals):
        assert len(conditionals["conditions"]) >= 15

    def test_if_blocks(self, conditionals):
        ifs = [c for c in conditionals["conditions"] if c["type"] == "if"]
        assert len(ifs) >= 10

    def test_switch_blocks(self, conditionals):
        switches = [c for c in conditionals["conditions"]
                    if c["type"] == "switch"]
        assert len(switches) >= 2

    def test_condition_text(self, conditionals):
        first_if = next(c for c in conditionals["conditions"]
                        if c["type"] == "if")
        assert first_if["condition"]  # non-empty

    def test_then_label(self, conditionals):
        labeled = [c for c in conditionals["conditions"]
                   if c["type"] == "if" and c.get("then_label")]
        assert len(labeled) >= 5

    def test_else_label(self, conditionals):
        labeled = [c for c in conditionals["conditions"]
                   if c["type"] == "if" and c.get("else_label")]
        assert len(labeled) >= 3

    def test_elseif_branches(self, conditionals):
        with_elseif = [c for c in conditionals["conditions"]
                       if c.get("elseif_count", 0) > 0]
        assert len(with_elseif) >= 1

    def test_switch_case_labels(self, conditionals):
        sw = next(c for c in conditionals["conditions"]
                  if c["type"] == "switch")
        assert len(sw["case_labels"]) >= 2

    def test_colored_actions_in_branches(self, conditionals):
        colors = [a["color"] for a in conditionals["actions"] if a.get("color")]
        assert len(colors) >= 2


# ═══════════════════════════════════════════════════════════
# 03 — Loops & Flow Control
# ═══════════════════════════════════════════════════════════

class TestLoopsFlowControl:
    """Test parsing of t_activity_03_loops_flow_control.puml."""

    def test_loop_count(self, loops_flow):
        assert len(loops_flow["loops"]) >= 8

    def test_repeat_loops(self, loops_flow):
        repeats = [lp for lp in loops_flow["loops"] if lp["type"] == "repeat"]
        assert len(repeats) >= 4

    def test_while_loops(self, loops_flow):
        whiles = [lp for lp in loops_flow["loops"] if lp["type"] == "while"]
        assert len(whiles) >= 4

    def test_repeat_condition(self, loops_flow):
        first_repeat = next(lp for lp in loops_flow["loops"]
                            if lp["type"] == "repeat")
        assert first_repeat["condition"]  # non-empty

    def test_backward_clause(self, loops_flow):
        with_backward = [lp for lp in loops_flow["loops"]
                         if lp.get("backward")]
        assert len(with_backward) >= 2

    def test_break_control(self, loops_flow):
        assert "break" in loops_flow["controls"]

    def test_detach_control(self, loops_flow):
        assert "detach" in loops_flow["controls"]

    def test_kill_control(self, loops_flow):
        assert "kill" in loops_flow["controls"]

    def test_stop_and_end_controls(self, loops_flow):
        assert "stop" in loops_flow["controls"]
        assert "end" in loops_flow["controls"]

    def test_label_goto(self, loops_flow):
        assert len(loops_flow["labels"]) >= 1
        assert "retryPoint" in loops_flow["labels"]


# ═══════════════════════════════════════════════════════════
# 04 — Fork, Split & Parallel
# ═══════════════════════════════════════════════════════════

class TestForkSplit:
    """Test parsing of t_activity_04_fork_split_parallel.puml."""

    def test_fork_count(self, fork_split):
        forks = [f for f in fork_split["forks"] if f["type"] == "fork"]
        assert len(forks) >= 6

    def test_split_count(self, fork_split):
        splits = [f for f in fork_split["forks"] if f["type"] == "split"]
        assert len(splits) >= 1

    def test_branch_counts(self, fork_split):
        multi = [f for f in fork_split["forks"] if f["branches"] >= 3]
        assert len(multi) >= 2

    def test_join_spec_or(self, fork_split):
        or_forks = [f for f in fork_split["forks"]
                    if f.get("join_spec") == "or"]
        assert len(or_forks) >= 1

    def test_join_spec_merge(self, fork_split):
        merge_forks = [f for f in fork_split["forks"]
                       if f.get("join_spec") == "merge"]
        assert len(merge_forks) >= 1

    def test_notes_in_forks(self, fork_split):
        assert len(fork_split["notes"]) >= 2


# ═══════════════════════════════════════════════════════════
# 05 — Swimlanes
# ═══════════════════════════════════════════════════════════

class TestSwimlanes:
    """Test parsing of t_activity_05_swimlanes.puml."""

    def test_swimlane_count(self, swimlanes):
        assert len(swimlanes["swimlanes"]) >= 10

    def test_colored_lanes(self, swimlanes):
        colored = [sl for sl in swimlanes["swimlanes"] if sl.get("color")]
        assert len(colored) >= 5

    def test_lane_names(self, swimlanes):
        names = {sl["name"] for sl in swimlanes["swimlanes"]}
        assert "Customer" in names
        assert "Warehouse" in names

    def test_actions_have_swimlane(self, swimlanes):
        with_lane = [a for a in swimlanes["actions"] if a.get("swimlane")]
        assert len(with_lane) >= 20

    def test_multiple_lanes_referenced(self, swimlanes):
        lanes = set(a["swimlane"] for a in swimlanes["actions"]
                    if a.get("swimlane"))
        assert len(lanes) >= 5


# ═══════════════════════════════════════════════════════════
# 06 — Partitions & Containers
# ═══════════════════════════════════════════════════════════

class TestContainers:
    """Test parsing of t_activity_06_partitions_containers.puml."""

    def test_container_count(self, containers):
        assert len(containers["containers"]) >= 15

    def test_partition_type(self, containers):
        parts = [c for c in containers["containers"]
                 if c["type"] == "partition"]
        assert len(parts) >= 5

    def test_group_type(self, containers):
        groups = [c for c in containers["containers"]
                  if c["type"] == "group"]
        assert len(groups) >= 2

    def test_package_type(self, containers):
        pkgs = [c for c in containers["containers"]
                if c["type"] == "package"]
        assert len(pkgs) >= 2

    def test_rectangle_type(self, containers):
        rects = [c for c in containers["containers"]
                 if c["type"] == "rectangle"]
        assert len(rects) >= 2

    def test_card_type(self, containers):
        cards = [c for c in containers["containers"]
                 if c["type"] == "card"]
        assert len(cards) >= 2

    def test_container_names(self, containers):
        names = [c["name"] for c in containers["containers"]]
        assert any("Initialization" in n for n in names)
        assert any("Authentication" in n for n in names)

    def test_container_colors(self, containers):
        colored = [c for c in containers["containers"] if c.get("color")]
        assert len(colored) >= 5


# ═══════════════════════════════════════════════════════════
# 07 — Notes & Skinparam
# ═══════════════════════════════════════════════════════════

class TestNotesSkinparam:
    """Test parsing of t_activity_07_notes_skinparam.puml."""

    def test_note_count(self, notes_skinparam):
        assert len(notes_skinparam["notes"]) >= 10

    def test_right_notes(self, notes_skinparam):
        rights = [n for n in notes_skinparam["notes"] if n["side"] == "right"]
        assert len(rights) >= 4

    def test_left_notes(self, notes_skinparam):
        lefts = [n for n in notes_skinparam["notes"] if n["side"] == "left"]
        assert len(lefts) >= 3

    def test_colored_notes(self, notes_skinparam):
        colored = [n for n in notes_skinparam["notes"] if n.get("color")]
        assert len(colored) >= 2

    def test_multiline_note_content(self, notes_skinparam):
        multiline = [n for n in notes_skinparam["notes"]
                     if "\n" in n.get("text", "")]
        assert len(multiline) >= 3

    def test_floating_note(self, notes_skinparam):
        # Floating notes have no side
        floating = [n for n in notes_skinparam["notes"]
                    if not n.get("side")]
        assert len(floating) >= 1

    def test_title(self, notes_skinparam):
        assert "Notes" in notes_skinparam["title"]


# ═══════════════════════════════════════════════════════════
# 08 — Parser Stress Test
# ═══════════════════════════════════════════════════════════

class TestStressTest:
    """Test parsing of t_activity_08_parser_stress_test.puml."""

    def test_action_count(self, stress_test):
        assert len(stress_test["actions"]) >= 50

    def test_condition_count(self, stress_test):
        assert len(stress_test["conditions"]) >= 5

    def test_loop_count(self, stress_test):
        assert len(stress_test["loops"]) >= 3

    def test_fork_count(self, stress_test):
        assert len(stress_test["forks"]) >= 3

    def test_note_count(self, stress_test):
        assert len(stress_test["notes"]) >= 3

    def test_arrow_count(self, stress_test):
        assert len(stress_test["arrows"]) >= 3

    def test_connectors(self, stress_test):
        assert len(stress_test["connectors"]) >= 2
        assert "A" in stress_test["connectors"]

    def test_labels(self, stress_test):
        assert len(stress_test["labels"]) >= 2
        assert "jumpTarget1" in stress_test["labels"]

    def test_stereotypes(self, stress_test):
        stereos = [a["stereotype"] for a in stress_test["actions"]
                   if a.get("stereotype")]
        assert len(stereos) >= 10

    def test_deep_nesting(self, stress_test):
        """5-level nested conditionals should parse without error."""
        ifs = [c for c in stress_test["conditions"] if c["type"] == "if"]
        assert len(ifs) >= 5


# ═══════════════════════════════════════════════════════════
# Round-trip tests
# ═══════════════════════════════════════════════════════════

def _make_mock_annotations(info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Build minimal mock annotations to test merge + normalize."""
    annotations: List[Dict[str, Any]] = []
    counter = 1
    style = {
        "pen": {"color": "#000000", "width": 1, "dash": "solid"},
        "fill": {"color": "#E8F4FD"},
        "text": {"color": "#000000", "size_pt": 11.0},
    }

    for action in info.get("actions", []):
        ann_id = f"p{counter:06d}"
        counter += 1
        label = action.get("text", "Action")
        annotations.append({
            "id": ann_id,
            "kind": "roundedrect",
            "geom": {"x": 100, "y": counter * 40, "w": 200, "h": 40},
            "meta": {"label": label, "tech": "", "note": label},
            "style": dict(style),
        })

    for cond in info.get("conditions", []):
        ann_id = f"p{counter:06d}"
        counter += 1
        label = cond.get("condition", "?")
        annotations.append({
            "id": ann_id,
            "kind": "diamond",
            "geom": {"x": 150, "y": counter * 40, "w": 100, "h": 60},
            "meta": {"label": label, "tech": "", "note": label},
            "style": dict(style),
        })

    for _arrow in info.get("arrows", []):
        ann_id = f"p{counter:06d}"
        counter += 1
        annotations.append({
            "id": ann_id,
            "kind": "line",
            "geom": {"x1": 200, "y1": counter * 40,
                     "x2": 200, "y2": counter * 40 + 30},
            "meta": {"label": "", "tech": "", "note": ""},
            "style": {
                "pen": {"color": "#444444", "width": 1, "dash": "solid"},
                "fill": {"color": "#00000000"},
                "text": {"color": "#000000", "size_pt": 11.0},
                "arrow": {"start": "none", "end": "filled"},
            },
        })

    for cont in info.get("containers", []):
        ann_id = f"p{counter:06d}"
        counter += 1
        name = cont.get("name", "Container")
        annotations.append({
            "id": ann_id,
            "kind": "rect",
            "geom": {"x": 50, "y": counter * 40, "w": 300, "h": 200},
            "meta": {"label": name, "tech": "", "note": name},
            "style": dict(style),
        })

    for ctrl in info.get("controls", []):
        if ctrl in ("start", "stop", "end"):
            ann_id = f"p{counter:06d}"
            counter += 1
            annotations.append({
                "id": ann_id,
                "kind": "ellipse",
                "geom": {"x": 200, "y": counter * 40, "w": 20, "h": 20},
                "meta": {"label": ctrl.capitalize(), "tech": "",
                         "note": ctrl},
                "style": dict(style),
            })

    return annotations


_ALL_FILES = [
    "t_activity_01_actions_arrows.puml",
    "t_activity_02_conditionals.puml",
    "t_activity_03_loops_flow_control.puml",
    "t_activity_04_fork_split_parallel.puml",
    "t_activity_05_swimlanes.puml",
    "t_activity_06_partitions_containers.puml",
    "t_activity_07_notes_skinparam.puml",
    "t_activity_08_parser_stress_test.puml",
]


class TestRoundTrip:
    """Verify normalize → merge → JSON serialization round-trip."""

    @pytest.mark.parametrize("filename", _ALL_FILES)
    def test_normalize_produces_contents(self, filename):
        info = _load(filename)
        annotations = _make_mock_annotations(info)
        _normalize_annotations(annotations)
        for ann in annotations:
            assert "contents" in ann, f"{ann['id']}: meta not converted"
            assert "meta" not in ann, f"{ann['id']}: meta still present"

    @pytest.mark.parametrize("filename", _ALL_FILES)
    def test_contents_has_blocks(self, filename):
        info = _load(filename)
        annotations = _make_mock_annotations(info)
        _normalize_annotations(annotations)
        for ann in annotations:
            contents = ann["contents"]
            assert "blocks" in contents
            assert "default_format" in contents
            assert "frame" in contents

    @pytest.mark.parametrize("filename", _ALL_FILES)
    def test_merge_adds_dsl(self, filename):
        info = _load(filename)
        annotations = _make_mock_annotations(info)
        _normalize_annotations(annotations)
        _merge_activity_source_info(annotations, info)
        dsl_count = sum(1 for a in annotations
                        if a.get("contents", {}).get("dsl"))
        assert dsl_count > 0, "No annotations enriched with DSL data"

    @pytest.mark.parametrize("filename", _ALL_FILES)
    def test_json_serialization(self, filename):
        info = _load(filename)
        annotations = _make_mock_annotations(info)
        _normalize_annotations(annotations)
        _merge_activity_source_info(annotations, info)

        payload = {
            "version": "draft-1",
            "image": {"width": 1200, "height": 800},
            "annotations": annotations,
        }
        json_str = json.dumps(payload, indent=2, ensure_ascii=False)
        parsed_back = json.loads(json_str)
        assert len(parsed_back["annotations"]) == len(annotations)

    @pytest.mark.parametrize("filename", _ALL_FILES)
    def test_blocks_have_valid_runs(self, filename):
        info = _load(filename)
        annotations = _make_mock_annotations(info)
        _normalize_annotations(annotations)
        for ann in annotations:
            for bi, block in enumerate(ann["contents"].get("blocks", [])):
                assert "runs" in block, f"{ann['id']}: block[{bi}] no runs"
                for ri, run in enumerate(block["runs"]):
                    assert "type" in run, (
                        f"{ann['id']}: block[{bi}].run[{ri}] no type")
                    assert "text" in run, (
                        f"{ann['id']}: block[{bi}].run[{ri}] no text")
