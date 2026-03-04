"""
mermaid/flowchart_merger.py

Step 2 of the two-step flowchart pipeline: merge source-parsed semantic
data with SVG-parsed geometry to produce enriched PictoSync annotations.

Pipeline:
    1.  ``flowchart_source_parser.parse_flowchart_source()``  ->  semantic data
    2.  This module calls the generic SVG parser for geometry and matches
        it to step 1 by label text, producing annotations that carry
        **both** the rich source metadata (node_id, shape, from/to,
        line_style, edge heads, subgraph membership) *and* the
        pixel-accurate geometry from the rendered SVG.
"""

from __future__ import annotations

from typing import Any, Dict, List

from mermaid.parser import parse_mermaid_svg_to_annotations
from mermaid.flowchart_source_parser import (
    FlowEdge,
    FlowNode,
    FlowParseResult,
    FlowSubgraph,
)


def _make_dsl_flowchart(**fields: Any) -> Dict[str, Any]:
    """Build a ``meta.dsl`` dict for flowchart domain annotations.

    Filters out falsy values so the output stays compact.
    """
    fc = {k: v for k, v in fields.items() if v}
    return {"tool": "mermaid", "flowchart": fc}


def _normalize_label(label: str) -> str:
    """Normalize a label for fuzzy matching (lowercase, collapse whitespace)."""
    return " ".join(label.lower().split())


# ═══════════════════════════════════════════════════════════
# Classification
# ═══════════════════════════════════════════════════════════


def _classify_annotations(
    annotations: List[Dict[str, Any]],
) -> tuple[
    List[Dict[str, Any]],
    List[Dict[str, Any]],
    List[Dict[str, Any]],
]:
    """Classify SVG-parsed annotations into nodes, edges, and clusters.

    Returns:
        ``(nodes, edges, clusters)``
    """
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    clusters: List[Dict[str, Any]] = []

    for ann in annotations:
        kind = ann.get("kind", "")
        if kind == "group":
            clusters.append(ann)
        elif kind in ("line", "curve"):
            edges.append(ann)
        else:
            # rect, roundedrect, ellipse, polygon, etc. — nodes
            nodes.append(ann)

    return nodes, edges, clusters


# ═══════════════════════════════════════════════════════════
# Matching
# ═══════════════════════════════════════════════════════════


def _match_nodes(
    source_nodes: List[FlowNode],
    svg_nodes: List[Dict[str, Any]],
) -> List[tuple[Dict[str, Any], FlowNode | None]]:
    """Match SVG nodes to source nodes.

    Priority: src_id match (exact Mermaid node ID from SVG element),
    then label match, then node_id-by-label fallback.

    Returns ``(svg_node, source_node_or_None)`` tuples.
    """
    # Build lookups
    source_by_node_id: dict[str, FlowNode] = {}
    source_by_label: dict[str, list[FlowNode]] = {}
    source_by_id_norm: dict[str, list[FlowNode]] = {}
    for n in source_nodes:
        source_by_node_id[n.node_id] = n
        key = _normalize_label(n.label)
        source_by_label.setdefault(key, []).append(n)
        id_key = _normalize_label(n.node_id)
        source_by_id_norm.setdefault(id_key, []).append(n)

    results: list[tuple[Dict[str, Any], FlowNode | None]] = []
    used: set[int] = set()

    for svg_n in svg_nodes:
        meta = svg_n.get("meta", {})
        match = None

        # 1) Try src_id match (exact Mermaid node ID from SVG)
        src_id = meta.get("src_id", "")
        if src_id and src_id in source_by_node_id:
            candidate = source_by_node_id[src_id]
            if id(candidate) not in used:
                match = candidate
                used.add(id(candidate))

        # 2) Fallback: label match, then node_id-by-label
        if match is None:
            label = meta.get("label", "")
            key = _normalize_label(label)
            for lookup in (source_by_label, source_by_id_norm):
                for c in lookup.get(key, []):
                    if id(c) not in used:
                        match = c
                        used.add(id(c))
                        break
                if match:
                    break

        results.append((svg_n, match))

    return results


def _match_edges(
    source_edges: List[FlowEdge],
    svg_edges: List[Dict[str, Any]],
) -> List[tuple[Dict[str, Any], FlowEdge | None]]:
    """Match SVG edges to source edges by sequential order.

    Flowchart edges are rendered in source order, so edge N in source
    corresponds to edge N in SVG.
    """
    results: list[tuple[Dict[str, Any], FlowEdge | None]] = []
    for i, svg_e in enumerate(svg_edges):
        src = source_edges[i] if i < len(source_edges) else None
        results.append((svg_e, src))
    return results


def _match_clusters(
    source_subgraphs: List[FlowSubgraph],
    svg_clusters: List[Dict[str, Any]],
) -> List[tuple[Dict[str, Any], FlowSubgraph | None]]:
    """Match SVG clusters to source subgraphs.

    Priority: src_id match (SVG element id == subgraph_id), then title match.

    Returns ``(svg_cluster, source_subgraph_or_None)`` tuples.
    """
    source_by_sg_id: dict[str, FlowSubgraph] = {}
    source_by_title: dict[str, list[FlowSubgraph]] = {}
    source_by_id_norm: dict[str, list[FlowSubgraph]] = {}
    for sg in source_subgraphs:
        source_by_sg_id[sg.subgraph_id] = sg
        key = _normalize_label(sg.title)
        source_by_title.setdefault(key, []).append(sg)
        id_key = _normalize_label(sg.subgraph_id)
        source_by_id_norm.setdefault(id_key, []).append(sg)

    results: list[tuple[Dict[str, Any], FlowSubgraph | None]] = []
    used: set[int] = set()

    for svg_c in svg_clusters:
        meta = svg_c.get("meta", {})
        match = None

        # 1) Try src_id match (SVG element id == subgraph_id)
        src_id = meta.get("src_id", "")
        if src_id and src_id in source_by_sg_id:
            candidate = source_by_sg_id[src_id]
            if id(candidate) not in used:
                match = candidate
                used.add(id(candidate))

        # 2) Fallback: title match, then subgraph_id-by-label
        if match is None:
            label = meta.get("label", "")
            key = _normalize_label(label)
            for lookup in (source_by_title, source_by_id_norm):
                for c in lookup.get(key, []):
                    if id(c) not in used:
                        match = c
                        used.add(id(c))
                        break
                if match:
                    break

        results.append((svg_c, match))

    return results


# ═══════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════


def merge_flowchart_source_with_svg(
    source: FlowParseResult,
    svg_path: str,
) -> Dict[str, Any]:
    """Merge flowchart source-parsed data with SVG geometry into annotation JSON.

    This is the **step 2** entry point.  It:

    1. Parses the SVG via the generic Mermaid SVG parser for geometry.
    2. Classifies annotations into nodes, edges, clusters.
    3. Matches each category to the source-parsed data.
    4. Enriches each annotation with ``meta.dsl.flowchart`` metadata.

    Args:
        source: Result from ``parse_flowchart_source()`` /
            ``parse_flowchart_source_file()``.
        svg_path: Path to the Mermaid-rendered SVG file.

    Returns:
        Annotation dict with ``version``, ``image``, and ``annotations`` keys.
    """
    # Get SVG geometry from the generic parser
    data = parse_mermaid_svg_to_annotations(svg_path)
    annotations = data.get("annotations", [])

    # Classify
    svg_nodes, svg_edges, svg_clusters = _classify_annotations(annotations)

    # Match
    node_pairs = _match_nodes(source.nodes, svg_nodes)
    edge_pairs = _match_edges(source.edges, svg_edges)
    cluster_pairs = _match_clusters(source.subgraphs, svg_clusters)

    # ── Enrich nodes ──
    for svg_n, src_n in node_pairs:
        if src_n is not None:
            svg_n["meta"]["label"] = src_n.label
            svg_n["meta"]["dsl"] = _make_dsl_flowchart(
                type="node",
                node_id=src_n.node_id,
                shape=src_n.shape,
            )

    # ── Enrich edges ──
    for svg_e, src_e in edge_pairs:
        if src_e is not None:
            if src_e.label:
                svg_e["meta"]["label"] = src_e.label
            svg_e["meta"]["dsl"] = _make_dsl_flowchart(
                type="edge",
                **{"from": src_e.from_id, "to": src_e.to_id},
                line_style=src_e.line_style,
                left_head=src_e.left_head,
                right_head=src_e.right_head,
            )

    # ── Enrich clusters — convert to visible rects ──
    for svg_c, src_sg in cluster_pairs:
        # Convert from invisible "group" to visible "rect" for canvas rendering
        svg_c["kind"] = "rect"
        # Preserve SVG-extracted fill/stroke (from _parse_cluster), add dashed border
        svg_style = svg_c.get("style", {})
        pen_color = svg_style.get("pen", {}).get("color", "#AAAA33")
        fill_color = svg_style.get("fill", {}).get("color", "#FFFFDE")
        svg_c["style"] = {
            "pen": {"color": pen_color, "width": 1.5, "dash": "dash"},
            "fill": {"color": fill_color},
            "text": {"color": "#333333"},
        }
        if src_sg is not None:
            svg_c["meta"]["label"] = src_sg.title
            svg_c["meta"]["dsl"] = _make_dsl_flowchart(
                type="subgraph",
                subgraph_id=src_sg.subgraph_id,
                children=src_sg.children if src_sg.children else None,
            )

    # ── Clean up internal src_id from all annotations ──
    for ann in annotations:
        ann.get("meta", {}).pop("src_id", None)

    return data
