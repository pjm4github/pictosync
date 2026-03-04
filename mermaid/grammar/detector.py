"""Detect the Mermaid diagram type from source text."""
from __future__ import annotations

from mermaid.grammar.registry import REGISTRY


def detect_mermaid_source_type(source: str) -> str | None:
    """Return the diagram type key for the given Mermaid source, or None.

    Strips leading whitespace and ``%%`` comment lines before matching
    against registered header patterns.

    Args:
        source: Raw Mermaid source text.

    Returns:
        A type key string (e.g. ``"sequence"``, ``"flowchart"``) or ``None``
        if the source does not match any known diagram type.
    """
    # Strip leading blank lines and %% comment lines
    lines = source.splitlines()
    cleaned_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == "" or stripped.startswith("%%"):
            continue
        cleaned_lines.append(line)
        break  # only need the first non-comment line for detection
    if not cleaned_lines:
        return None

    cleaned = "\n".join(cleaned_lines)
    entry = REGISTRY.detect(cleaned)
    return entry.type_key if entry else None
