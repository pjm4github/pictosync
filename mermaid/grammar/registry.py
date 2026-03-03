"""Central registry mapping Mermaid diagram types to parsers and SVG shape rules."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class SVGShapeRule:
    """Maps one SVG element role to a PictoSync annotation kind.

    Args:
        svg_role: Role identifier from the SVG (e.g. "actor_top", "lifeline").
        pictosync_kind: PictoSync annotation kind ("rect", "line", "text", etc.).
        default_style: Optional default style hints (fill color, dashed, etc.).
    """

    svg_role: str
    pictosync_kind: str
    default_style: dict = field(default_factory=dict)


@dataclass
class DiagramTypeEntry:
    """Registry entry for one Mermaid diagram type.

    Args:
        type_key: Short key like "sequence", "flowchart".
        header_pattern: Compiled regex matching the diagram header line.
        grammar_name: ANTLR4 grammar name (e.g. "MermaidSequence").
        parse_fn: Function that takes source text and returns an ANTLR4 parse
            tree, or ``None`` if parsing is not yet implemented.
        svg_shape_rules: SVG role to PictoSync shape mappings.
    """

    type_key: str
    header_pattern: re.Pattern
    grammar_name: str
    parse_fn: Callable[[str], Any] | None = None
    svg_shape_rules: list[SVGShapeRule] = field(default_factory=list)


class MermaidDiagramRegistry:
    """Singleton-style registry of all known Mermaid diagram types."""

    def __init__(self) -> None:
        self._entries: dict[str, DiagramTypeEntry] = {}

    def register(self, entry: DiagramTypeEntry) -> None:
        """Register a diagram type entry.

        Args:
            entry: The DiagramTypeEntry to register.
        """
        self._entries[entry.type_key] = entry

    def detect(self, source: str) -> DiagramTypeEntry | None:
        """Detect diagram type from source text.

        Strips leading whitespace and tries each registered header pattern.

        Args:
            source: Raw Mermaid source text.

        Returns:
            The matching DiagramTypeEntry, or None if no match.
        """
        stripped = source.lstrip()
        for entry in self._entries.values():
            if entry.header_pattern.search(stripped):
                return entry
        return None

    def get(self, type_key: str) -> DiagramTypeEntry | None:
        """Look up a diagram type by key.

        Args:
            type_key: The diagram type key (e.g. "sequence").

        Returns:
            The DiagramTypeEntry or None.
        """
        return self._entries.get(type_key)

    def all_types(self) -> list[str]:
        """Return all registered type keys.

        Returns:
            List of type key strings.
        """
        return list(self._entries.keys())


# ---------------------------------------------------------------------------
# Parse functions for fully-wired grammars
# ---------------------------------------------------------------------------

def _parse_sequence(source: str) -> Any:
    """Parse Mermaid sequence diagram source via ANTLR4.

    Args:
        source: Raw Mermaid sequence diagram text.

    Returns:
        ANTLR4 parse tree (DiagramContext).
    """
    from antlr4 import CommonTokenStream, InputStream

    from generated.MermaidSequenceLexer import MermaidSequenceLexer
    from generated.MermaidSequenceParser import MermaidSequenceParser

    input_stream = InputStream(source)
    lexer = MermaidSequenceLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = MermaidSequenceParser(token_stream)
    return parser.diagram()


def _parse_c4(source: str) -> Any:
    """Parse Mermaid C4 diagram source via ANTLR4.

    Args:
        source: Raw Mermaid C4 diagram text.

    Returns:
        ANTLR4 parse tree (DiagramContext).
    """
    from antlr4 import CommonTokenStream, InputStream

    from generated.MermaidC4Lexer import MermaidC4Lexer
    from generated.MermaidC4Parser import MermaidC4Parser

    input_stream = InputStream(source)
    lexer = MermaidC4Lexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = MermaidC4Parser(token_stream)
    return parser.diagram()


# ---------------------------------------------------------------------------
# Sequence SVG shape rules
# ---------------------------------------------------------------------------

_SEQUENCE_SHAPE_RULES = [
    SVGShapeRule("actor_top", "rect", {"fill": "#ECECFF"}),
    SVGShapeRule("actor_bottom", "rect", {"fill": "#ECECFF"}),
    SVGShapeRule("lifeline", "line", {"dashed": True}),
    SVGShapeRule("activation", "rect", {}),
    SVGShapeRule("message", "line", {}),
    SVGShapeRule("note", "rect", {"fill": "#FFF5AD"}),
    SVGShapeRule("block", "rect", {}),
    SVGShapeRule("block_divider", "line", {}),
    SVGShapeRule("actor_person", "ellipse", {}),
]


# ---------------------------------------------------------------------------
# Module-level singleton registry with all known types pre-registered
# ---------------------------------------------------------------------------

REGISTRY = MermaidDiagramRegistry()

REGISTRY.register(DiagramTypeEntry(
    type_key="sequence",
    header_pattern=re.compile(r"sequenceDiagram\b"),
    grammar_name="MermaidSequence",
    parse_fn=_parse_sequence,
    svg_shape_rules=_SEQUENCE_SHAPE_RULES,
))

REGISTRY.register(DiagramTypeEntry(
    type_key="c4",
    header_pattern=re.compile(r"C4(Context|Container|Component|Dynamic|Deployment)\b"),
    grammar_name="MermaidC4",
    parse_fn=_parse_c4,
))

REGISTRY.register(DiagramTypeEntry(
    type_key="flowchart",
    header_pattern=re.compile(r"(flowchart|graph)\s+(TB|TD|BT|LR|RL)"),
    grammar_name="MermaidFlowchart",
))

REGISTRY.register(DiagramTypeEntry(
    type_key="block",
    header_pattern=re.compile(r"block-beta\b"),
    grammar_name="MermaidBlockDiagram",
))

REGISTRY.register(DiagramTypeEntry(
    type_key="state",
    header_pattern=re.compile(r"stateDiagram(-v2)?\b"),
    grammar_name="MermaidStateDiagram",
))

REGISTRY.register(DiagramTypeEntry(
    type_key="architecture",
    header_pattern=re.compile(r"architecture-beta\b"),
    grammar_name="MermaidArchitectureDiagram",
))
