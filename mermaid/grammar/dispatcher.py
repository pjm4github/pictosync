"""Dispatch Mermaid source to the correct ANTLR4 parser."""
from __future__ import annotations

from typing import Any

from mermaid.grammar.detector import detect_mermaid_source_type
from mermaid.grammar.registry import REGISTRY


def parse_mermaid_source(source: str) -> Any:
    """Detect diagram type and dispatch to the ANTLR4 parser.

    Args:
        source: Raw Mermaid source text.

    Returns:
        ANTLR4 parse tree root node.

    Raises:
        ValueError: If the diagram type cannot be detected.
        NotImplementedError: If the detected type has no parser wired yet.
    """
    type_key = detect_mermaid_source_type(source)
    if type_key is None:
        raise ValueError("Could not detect Mermaid diagram type from source")
    return parse_mermaid_source_as(type_key, source)


def parse_mermaid_source_as(type_key: str, source: str) -> Any:
    """Parse source using the specified diagram type (skip detection).

    Args:
        type_key: Diagram type key (e.g. ``"sequence"``).
        source: Raw Mermaid source text.

    Returns:
        ANTLR4 parse tree root node.

    Raises:
        ValueError: If the type_key is not registered.
        NotImplementedError: If the type has no parser wired yet.
    """
    entry = REGISTRY.get(type_key)
    if entry is None:
        raise ValueError(f"Unknown Mermaid diagram type: {type_key!r}")
    if entry.parse_fn is None:
        raise NotImplementedError(
            f"Parser for Mermaid diagram type {type_key!r} "
            f"(grammar {entry.grammar_name!r}) is not yet implemented"
        )
    return entry.parse_fn(source)
