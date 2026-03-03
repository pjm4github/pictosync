"""
mermaid/sequence_merger.py

Step 2 of the two-step sequence diagram pipeline: merge source-parsed
semantic data with SVG-parsed geometry to produce enriched PictoSync
annotations.

Pipeline:
    1.  ``sequence_source_parser.parse_sequence_source()``  →  semantic data
    2.  This module calls the generic SVG parser for geometry and matches
        it to step 1 by sequential order and label text, producing
        annotations that carry **both** the rich source metadata (alias,
        actor_type, from/to, arrow_type, line_type, placement, block_type)
        *and* the pixel-accurate geometry from the rendered SVG.
"""

from __future__ import annotations

from typing import Any, Dict, List

from mermaid.parser import parse_mermaid_svg_to_annotations
from mermaid.sequence_source_parser import (
    SeqMessage,
    SeqNote,
    SeqParseResult,
    SeqParticipant,
)


def _make_dsl_sequence(**fields: Any) -> Dict[str, Any]:
    """Build a ``meta.dsl`` dict for sequence domain annotations.

    Filters out falsy values so the output stays compact.
    """
    seq = {k: v for k, v in fields.items() if v}
    return {"tool": "mermaid", "sequence": seq}


def _normalize_label(label: str) -> str:
    """Normalize a label for fuzzy matching (lowercase, collapse whitespace)."""
    return " ".join(label.lower().split())


# ═══════════════════════════════════════════════════════════
# Classification helpers
# ═══════════════════════════════════════════════════════════

def _classify_annotations(
    annotations: List[Dict[str, Any]],
) -> tuple[
    List[Dict[str, Any]],
    List[Dict[str, Any]],
    List[Dict[str, Any]],
    List[Dict[str, Any]],
    List[Dict[str, Any]],
    List[Dict[str, Any]],
    List[Dict[str, Any]],
]:
    """Classify SVG-parsed annotations into semantic categories.

    Uses the ``meta.seq_role`` tag set by the SVG parser when available,
    falling back to kind/fill heuristics otherwise.

    Returns:
        ``(actor_tops, messages, notes, blocks, lifelines,
        actor_bottoms, activations)`` where each is a list of annotation
        dicts.
    """
    actor_tops: List[Dict[str, Any]] = []
    messages: List[Dict[str, Any]] = []
    notes: List[Dict[str, Any]] = []
    blocks: List[Dict[str, Any]] = []
    lifelines: List[Dict[str, Any]] = []
    actor_bottoms: List[Dict[str, Any]] = []
    activations: List[Dict[str, Any]] = []

    for ann in annotations:
        kind = ann.get("kind", "")
        fill_color = ann.get("style", {}).get("fill", {}).get("color", "")
        seq_role = ann.get("meta", {}).get("seq_role", "")

        # ── Prefer explicit seq_role classification ──
        if seq_role == "actor_top":
            actor_tops.append(ann)
        elif seq_role == "actor_bottom":
            actor_bottoms.append(ann)
        elif seq_role == "lifeline":
            lifelines.append(ann)
        elif seq_role == "activation":
            activations.append(ann)
        elif seq_role == "block" or kind == "seqblock":
            blocks.append(ann)
        elif kind in ("line", "curve"):
            messages.append(ann)
        elif kind == "roundedrect" and fill_color == "#FFF5AD":
            notes.append(ann)
        elif kind == "roundedrect" and fill_color in ("#ECECFF", "#ececff"):
            blocks.append(ann)
        elif kind in ("roundedrect", "rect") and fill_color not in (
            "#FFF5AD", "#ECECFF", "#ececff",
        ):
            actor_tops.append(ann)

    return actor_tops, messages, notes, blocks, lifelines, actor_bottoms, activations


# ═══════════════════════════════════════════════════════════
# Matching
# ═══════════════════════════════════════════════════════════

def _match_actors(
    source_participants: List[SeqParticipant],
    svg_actors: List[Dict[str, Any]],
) -> List[tuple[Dict[str, Any], SeqParticipant | None]]:
    """Match SVG actor boxes to source participants by label or alias.

    Mermaid SVGs store the ``name`` attribute (which is the source alias)
    as the label text on actor rects.  This matcher tries both the display
    label and the alias for matching.

    Returns ``(svg_actor, source_participant_or_None)`` tuples.
    """
    # Build lookups: normalized_label → participant, alias → participant
    source_by_label: dict[str, list[SeqParticipant]] = {}
    source_by_alias: dict[str, list[SeqParticipant]] = {}
    for p in source_participants:
        key = _normalize_label(p.label)
        source_by_label.setdefault(key, []).append(p)
        alias_key = _normalize_label(p.alias)
        source_by_alias.setdefault(alias_key, []).append(p)

    results: list[tuple[Dict[str, Any], SeqParticipant | None]] = []
    used: set[int] = set()

    for svg_a in svg_actors:
        label = svg_a.get("meta", {}).get("label", "")
        key = _normalize_label(label)
        match = None
        # Try label match first, then alias match
        for lookup in (source_by_label, source_by_alias):
            for c in lookup.get(key, []):
                if id(c) not in used:
                    match = c
                    used.add(id(c))
                    break
            if match:
                break
        results.append((svg_a, match))

    return results


def _match_messages(
    source_messages: List[SeqMessage],
    svg_messages: List[Dict[str, Any]],
) -> List[tuple[Dict[str, Any], SeqMessage | None]]:
    """Match SVG message lines to source messages by sequential order.

    Sequence diagrams are inherently ordered, so message N in source
    corresponds to message N in SVG.
    """
    results: list[tuple[Dict[str, Any], SeqMessage | None]] = []
    for i, svg_m in enumerate(svg_messages):
        src = source_messages[i] if i < len(source_messages) else None
        results.append((svg_m, src))
    return results


def _match_notes(
    source_notes: List[SeqNote],
    svg_notes: List[Dict[str, Any]],
) -> List[tuple[Dict[str, Any], SeqNote | None]]:
    """Match SVG note boxes to source notes by sequential order."""
    results: list[tuple[Dict[str, Any], SeqNote | None]] = []
    for i, svg_n in enumerate(svg_notes):
        src = source_notes[i] if i < len(source_notes) else None
        results.append((svg_n, src))
    return results


# ═══════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════


def merge_sequence_source_with_svg(
    source: SeqParseResult,
    svg_path: str,
) -> Dict[str, Any]:
    """Merge sequence source-parsed data with SVG geometry into annotation JSON.

    This is the **step 2** entry point.  It:

    1. Parses the SVG via the generic Mermaid SVG parser for geometry.
    2. Classifies annotations into actors, messages, notes, blocks.
    3. Matches each category to the source-parsed data.
    4. Enriches each annotation with ``meta.dsl.sequence`` metadata.

    Args:
        source: Result from ``parse_sequence_source()`` /
            ``parse_sequence_source_file()``.
        svg_path: Path to the Mermaid-rendered SVG file.

    Returns:
        Annotation dict with ``version``, ``image``, and ``annotations`` keys.
    """
    # Get SVG geometry from the generic parser
    data = parse_mermaid_svg_to_annotations(svg_path)
    annotations = data.get("annotations", [])

    # Classify
    (svg_actor_tops, svg_messages, svg_notes, svg_blocks,
     svg_lifelines, svg_actor_bottoms, svg_activations,
     ) = _classify_annotations(annotations)

    # Build alias lookup from source participants keyed by label and alias
    _label_to_alias: dict[str, str] = {}
    for p in source.participants:
        _label_to_alias[_normalize_label(p.label)] = p.alias
        _label_to_alias[_normalize_label(p.alias)] = p.alias

    # Sort messages by Y position so sequential matching aligns with source
    # order (curves from self-referencing messages may appear out of order).
    def _msg_y(a: Dict[str, Any]) -> float:
        g = a.get("geom", {})
        return g.get("y1", g.get("y", 0.0))
    svg_messages.sort(key=_msg_y)

    # Match
    actor_pairs = _match_actors(source.participants, svg_actor_tops)
    msg_pairs = _match_messages(source.messages, svg_messages)
    note_pairs = _match_notes(source.notes, svg_notes)

    # Build alias → display label lookup (label from 'as' clause, else participantId)
    _alias_to_label: dict[str, str] = {
        p.alias: p.label for p in source.participants
    }

    # ── Enrich actor top boxes ──
    for svg_a, src_p in actor_pairs:
        if src_p is not None:
            svg_a["meta"]["label"] = src_p.label
            svg_a["meta"]["dsl"] = _make_dsl_sequence(
                type="participant",
                alias=src_p.alias,
                actor_type=src_p.actor_type,
            )

    # ── Enrich actor bottom boxes (match by label) ──
    for svg_b in svg_actor_bottoms:
        label = svg_b.get("meta", {}).get("label", "")
        alias = _label_to_alias.get(_normalize_label(label), "")
        if alias:
            svg_b["meta"]["label"] = _alias_to_label.get(alias, label)
            svg_b["meta"]["dsl"] = _make_dsl_sequence(
                type="participant",
                alias=alias,
            )

    # ── Enrich lifelines (match by label = actor name) ──
    for svg_l in svg_lifelines:
        label = svg_l.get("meta", {}).get("label", "")
        alias = _label_to_alias.get(_normalize_label(label), "")
        # Lifeline label is the alias (name attr), not the display label
        if not alias:
            # Try direct alias match (name attr stores alias, not label)
            for p in source.participants:
                if p.alias == label:
                    alias = p.alias
                    break
        if alias:
            svg_l["meta"]["label"] = _alias_to_label.get(alias, label)
            svg_l["meta"]["dsl"] = _make_dsl_sequence(
                type="lifeline",
                alias=alias,
            )

    # ── Enrich activations ──
    for svg_act in svg_activations:
        svg_act["meta"]["dsl"] = _make_dsl_sequence(type="activation")

    # ── Enrich messages ──
    # The parse tree is authoritative for message text — the SVG parser's
    # index-based text-to-line matching is fragile (block-divider lines can
    # shift the count).  Override meta.label with the source text.
    for svg_m, src_m in msg_pairs:
        if src_m is not None:
            svg_m["meta"]["label"] = src_m.text
            svg_m["meta"]["dsl"] = _make_dsl_sequence(
                type="message",
                **{
                    "from": src_m.from_alias,
                    "to": src_m.to_alias,
                },
                line_type=src_m.line_type,
                arrow_type=src_m.arrow_type,
            )

    # ── Enrich notes ──
    for svg_n, src_n in note_pairs:
        if src_n is not None:
            # Use source note text (may contain HTML like <br/>) over SVG-
            # extracted text which can be stripped or reformatted by the renderer.
            if src_n.text:
                svg_n["meta"]["note"] = src_n.text
            svg_n["meta"]["dsl"] = _make_dsl_sequence(
                type="note",
                placement=src_n.placement,
            )

    # ── Enrich blocks ──
    # Match SVG seqblock annotations to source blocks by label == block_type,
    # consuming each source block at most once (in order within type).
    # Seqblock annotations already carry adjust values from SVG divider positions.
    used_src: set[int] = set()
    for svg_b in svg_blocks:
        svg_label = _normalize_label(svg_b.get("meta", {}).get("label", ""))
        for i, src_b in enumerate(source.blocks):
            if i in used_src:
                continue
            if src_b.block_type == svg_label:
                svg_b["meta"]["dsl"] = _make_dsl_sequence(
                    type="block",
                    block_type=src_b.block_type,
                )
                # Stamp section labels from source into meta.tech
                if len(src_b.sections) > 0:
                    labels = [s[0] for s in src_b.sections if s[0]]
                    if labels:
                        svg_b["meta"]["tech"] = " | ".join(labels)
                used_src.add(i)
                break

    return data
