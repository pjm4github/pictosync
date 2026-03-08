"""Mermaid grammar: detection, dispatching, and diagram type registry."""
from mermaid.grammar.detector import detect_mermaid_source_type
from mermaid.grammar.dispatcher import parse_mermaid_source, parse_mermaid_source_as
from mermaid.grammar.registry import REGISTRY, DiagramTypeEntry, SVGShapeRule

__all__ = [
    "detect_mermaid_source_type",
    "parse_mermaid_source",
    "parse_mermaid_source_as",
    "REGISTRY",
    "DiagramTypeEntry",
    "SVGShapeRule",
]
