"""Tests for PlantUML state ANTLR source parser and round-trip.

Validates that PlantUML state diagram source (.puml) is correctly
parsed into states with names, aliases, stereotypes, descriptions,
composite flags, concurrent regions, and parent-child relationships.
Also validates the merge into annotations and JSON round-trip.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

import pytest

from plantuml.parser import (
    _merge_state_source_info,
    _normalize_annotations,
    _parse_state_source,
)


# ═══════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════

def _load(filename: str) -> Dict[str, Dict[str, Any]]:
    path = f"test_data/PUML/{filename}"
    with open(path, encoding="utf-8") as f:
        text = f.read()
    result = _parse_state_source(text)
    assert result, f"_parse_state_source returned empty for {filename}"
    return result


@pytest.fixture()
def recloser() -> Dict[str, Dict[str, Any]]:
    return _load("t_state_recloser.puml")


@pytest.fixture()
def recloser2() -> Dict[str, Dict[str, Any]]:
    return _load("t_state_recloser2.puml")


@pytest.fixture()
def circuit_breaker() -> Dict[str, Dict[str, Any]]:
    return _load("t_state_circuit_breaker_recloser.puml")


@pytest.fixture()
def der_inverter() -> Dict[str, Dict[str, Any]]:
    return _load("t_state_der_inverter_control_modes.puml")


@pytest.fixture()
def order_lifecycle() -> Dict[str, Dict[str, Any]]:
    return _load("t_state_order_lifecycle_concurrent.puml")


@pytest.fixture()
def tcp_connection() -> Dict[str, Dict[str, Any]]:
    return _load("t_state_tcp_connection_protocol.puml")


@pytest.fixture()
def stress_test() -> Dict[str, Dict[str, Any]]:
    return _load("t_state_parser_stress_test.puml")


@pytest.fixture()
def entry_exit() -> Dict[str, Dict[str, Any]]:
    return _load("t_state_entry_exit.puml")


@pytest.fixture()
def expansion() -> Dict[str, Dict[str, Any]]:
    return _load("t_state_expansion.puml")


@pytest.fixture()
def pin() -> Dict[str, Dict[str, Any]]:
    return _load("t_state_pin.puml")


@pytest.fixture()
def pseudo_states() -> Dict[str, Dict[str, Any]]:
    return _load("t_state_start_join_fork_exit_choice.puml")


# ═══════════════════════════════════════════════════════════
# Recloser (basic state machine)
# ═══════════════════════════════════════════════════════════

class TestRecloser:
    def test_state_count(self, recloser):
        assert len(recloser) >= 5

    def test_stereotypes(self, recloser):
        stereos = [v["stereotype"] for v in recloser.values()
                   if v.get("stereotype")]
        assert len(stereos) >= 3

    def test_composite_state(self, recloser):
        composites = [k for k, v in recloser.items() if v.get("is_composite")]
        assert len(composites) >= 1

    def test_descriptions(self, recloser):
        with_desc = [k for k, v in recloser.items() if v.get("descriptions")]
        assert len(with_desc) >= 3


class TestRecloser2:
    def test_state_count(self, recloser2):
        assert len(recloser2) >= 5

    def test_stereotypes(self, recloser2):
        stereos = {v["stereotype"] for v in recloser2.values()
                   if v.get("stereotype")}
        assert len(stereos) >= 3


# ═══════════════════════════════════════════════════════════
# Circuit Breaker (complex with composites)
# ═══════════════════════════════════════════════════════════

class TestCircuitBreaker:
    def test_state_count(self, circuit_breaker):
        assert len(circuit_breaker) >= 10

    def test_composites(self, circuit_breaker):
        composites = [k for k, v in circuit_breaker.items()
                      if v.get("is_composite")]
        assert len(composites) >= 3

    def test_children(self, circuit_breaker):
        with_children = [k for k, v in circuit_breaker.items()
                         if v.get("children")]
        assert len(with_children) >= 1

    def test_stereotypes(self, circuit_breaker):
        stereos = [v["stereotype"] for v in circuit_breaker.values()
                   if v.get("stereotype")]
        assert len(stereos) >= 5


# ═══════════════════════════════════════════════════════════
# DER Inverter (large with many composites)
# ═══════════════════════════════════════════════════════════

class TestDERInverter:
    def test_state_count(self, der_inverter):
        assert len(der_inverter) >= 20

    def test_composites(self, der_inverter):
        composites = [k for k, v in der_inverter.items()
                      if v.get("is_composite")]
        assert len(composites) >= 3

    def test_choice_pseudostates(self, der_inverter):
        choices = [k for k, v in der_inverter.items()
                   if "choice" in v.get("stereotype", "").lower()]
        assert len(choices) >= 1


# ═══════════════════════════════════════════════════════════
# Order Lifecycle (concurrent regions)
# ═══════════════════════════════════════════════════════════

class TestOrderLifecycle:
    def test_state_count(self, order_lifecycle):
        assert len(order_lifecycle) >= 20

    def test_composites(self, order_lifecycle):
        composites = [k for k, v in order_lifecycle.items()
                      if v.get("is_composite")]
        assert len(composites) >= 3

    def test_stereotypes(self, order_lifecycle):
        stereos = [v["stereotype"] for v in order_lifecycle.values()
                   if v.get("stereotype")]
        assert len(stereos) >= 5

    def test_descriptions(self, order_lifecycle):
        with_desc = [k for k, v in order_lifecycle.items()
                     if v.get("descriptions")]
        assert len(with_desc) >= 3


# ═══════════════════════════════════════════════════════════
# TCP Connection (composite + descriptions)
# ═══════════════════════════════════════════════════════════

class TestTCPConnection:
    def test_state_count(self, tcp_connection):
        assert len(tcp_connection) >= 15

    def test_composites(self, tcp_connection):
        composites = [k for k, v in tcp_connection.items()
                      if v.get("is_composite")]
        assert len(composites) >= 3

    def test_descriptions(self, tcp_connection):
        with_desc = [k for k, v in tcp_connection.items()
                     if v.get("descriptions")]
        assert len(with_desc) >= 3


# ═══════════════════════════════════════════════════════════
# Pseudo-states (start, choice, fork, join, end)
# ═══════════════════════════════════════════════════════════

class TestPseudoStates:
    def test_state_count(self, pseudo_states):
        assert len(pseudo_states) >= 5

    def test_start_stereotype(self, pseudo_states):
        starts = [v for v in pseudo_states.values()
                  if "start" in v.get("stereotype", "").lower()]
        assert len(starts) >= 1

    def test_choice_stereotype(self, pseudo_states):
        choices = [v for v in pseudo_states.values()
                   if "choice" in v.get("stereotype", "").lower()]
        assert len(choices) >= 1

    def test_fork_stereotype(self, pseudo_states):
        forks = [v for v in pseudo_states.values()
                 if "fork" in v.get("stereotype", "").lower()]
        assert len(forks) >= 1

    def test_join_stereotype(self, pseudo_states):
        joins = [v for v in pseudo_states.values()
                 if "join" in v.get("stereotype", "").lower()]
        assert len(joins) >= 1

    def test_end_stereotype(self, pseudo_states):
        ends = [v for v in pseudo_states.values()
                if "end" in v.get("stereotype", "").lower()]
        assert len(ends) >= 1


# ═══════════════════════════════════════════════════════════
# Entry/Exit points
# ═══════════════════════════════════════════════════════════

class TestEntryExit:
    def test_state_count(self, entry_exit):
        assert len(entry_exit) >= 3

    def test_entry_points(self, entry_exit):
        entries = [v for v in entry_exit.values()
                   if "entryPoint" in v.get("stereotype", "")]
        assert len(entries) >= 1

    def test_exit_points(self, entry_exit):
        exits = [v for v in entry_exit.values()
                 if "exitPoint" in v.get("stereotype", "")]
        assert len(exits) >= 1

    def test_composite_parent(self, entry_exit):
        composites = [k for k, v in entry_exit.items()
                      if v.get("is_composite")]
        assert len(composites) >= 1


# ═══════════════════════════════════════════════════════════
# Expansion points
# ═══════════════════════════════════════════════════════════

class TestExpansion:
    def test_expansion_input(self, expansion):
        inputs = [v for v in expansion.values()
                  if "expansionInput" in v.get("stereotype", "")]
        assert len(inputs) >= 1

    def test_expansion_output(self, expansion):
        outputs = [v for v in expansion.values()
                   if "expansionOutput" in v.get("stereotype", "")]
        assert len(outputs) >= 1


# ═══════════════════════════════════════════════════════════
# Input/Output pins
# ═══════════════════════════════════════════════════════════

class TestPin:
    def test_input_pin(self, pin):
        inputs = [v for v in pin.values()
                  if "inputPin" in v.get("stereotype", "")]
        assert len(inputs) >= 1

    def test_output_pin(self, pin):
        outputs = [v for v in pin.values()
                   if "outputPin" in v.get("stereotype", "")]
        assert len(outputs) >= 1


# ═══════════════════════════════════════════════════════════
# Stress Test (all features combined)
# ═══════════════════════════════════════════════════════════

class TestStateStressTest:
    def test_state_count(self, stress_test):
        assert len(stress_test) >= 30

    def test_composites(self, stress_test):
        composites = [k for k, v in stress_test.items()
                      if v.get("is_composite")]
        assert len(composites) >= 3

    def test_stereotypes(self, stress_test):
        stereos = [v["stereotype"] for v in stress_test.values()
                   if v.get("stereotype")]
        assert len(stereos) >= 5

    def test_descriptions(self, stress_test):
        with_desc = [k for k, v in stress_test.items()
                     if v.get("descriptions")]
        assert len(with_desc) >= 3

    def test_children(self, stress_test):
        with_children = [k for k, v in stress_test.items()
                         if v.get("children")]
        assert len(with_children) >= 3

    def test_parent_tracking(self, stress_test):
        with_parent = [k for k, v in stress_test.items()
                       if v.get("parent")]
        assert len(with_parent) >= 3


# ═══════════════════════════════════════════════════════════
# Round-trip tests
# ═══════════════════════════════════════════════════════════

def _make_mock_state_annotations(info: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build mock annotations matching SVG parser output for states."""
    annotations = []
    counter = 1
    style = {
        "pen": {"color": "#000000", "width": 1, "dash": "solid"},
        "fill": {"color": "#E8F4FD"},
        "text": {"color": "#000000", "size_pt": 11.0},
    }
    for key, state in info.items():
        ann_id = f"p{counter:06d}"
        counter += 1
        label = state.get("name", key)
        kind = "roundedrect"
        if state.get("stereotype") and any(
            ps in state["stereotype"].lower()
            for ps in ("choice", "fork", "join")
        ):
            kind = "diamond"
        annotations.append({
            "id": ann_id,
            "kind": kind,
            "geom": {"x": 100, "y": counter * 50, "w": 150, "h": 60},
            "meta": {"label": label, "tech": "", "note": label},
            "style": dict(style),
        })
    return annotations


_STATE_FILES = [
    "t_state_recloser.puml",
    "t_state_recloser2.puml",
    "t_state_circuit_breaker_recloser.puml",
    "t_state_der_inverter_control_modes.puml",
    "t_state_order_lifecycle_concurrent.puml",
    "t_state_tcp_connection_protocol.puml",
    "t_state_parser_stress_test.puml",
    "t_state_entry_exit.puml",
    "t_state_expansion.puml",
    "t_state_pin.puml",
    "t_state_start_join_fork_exit_choice.puml",
]


class TestStateRoundTrip:
    """Verify normalize → merge → JSON serialization round-trip."""

    @pytest.mark.parametrize("filename", _STATE_FILES)
    def test_parse_succeeds(self, filename):
        info = _load(filename)
        assert len(info) > 0

    @pytest.mark.parametrize("filename", _STATE_FILES)
    def test_normalize_produces_contents(self, filename):
        info = _load(filename)
        annotations = _make_mock_state_annotations(info)
        _normalize_annotations(annotations)
        for ann in annotations:
            assert "contents" in ann
            assert "meta" not in ann

    @pytest.mark.parametrize("filename", _STATE_FILES)
    def test_contents_has_blocks(self, filename):
        info = _load(filename)
        annotations = _make_mock_state_annotations(info)
        _normalize_annotations(annotations)
        for ann in annotations:
            contents = ann["contents"]
            assert "blocks" in contents
            assert "default_format" in contents
            assert "frame" in contents

    @pytest.mark.parametrize("filename", _STATE_FILES)
    def test_merge_enriches(self, filename):
        info = _load(filename)
        annotations = _make_mock_state_annotations(info)
        _normalize_annotations(annotations)
        _merge_state_source_info(annotations, info)
        dsl_count = sum(1 for a in annotations
                        if a.get("contents", {}).get("dsl"))
        assert dsl_count > 0, "No annotations enriched with DSL data"

    @pytest.mark.parametrize("filename", _STATE_FILES)
    def test_json_serialization(self, filename):
        info = _load(filename)
        annotations = _make_mock_state_annotations(info)
        _normalize_annotations(annotations)
        _merge_state_source_info(annotations, info)
        payload = {
            "version": "draft-1",
            "image": {"width": 1200, "height": 800},
            "annotations": annotations,
        }
        json_str = json.dumps(payload, indent=2, ensure_ascii=False)
        parsed_back = json.loads(json_str)
        assert len(parsed_back["annotations"]) == len(annotations)

    @pytest.mark.parametrize("filename", _STATE_FILES)
    def test_all_states_have_name(self, filename):
        info = _load(filename)
        for key, state in info.items():
            assert state.get("name"), f"State '{key}' has no name"
