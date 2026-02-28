"""
mermaid/c4_source_parser.py

Parse Mermaid C4 source text (.mmd/.mermaid) into structured shape and
relationship data, following the official JISON grammar from
``packages/mermaid/src/diagrams/c4/parser/c4Diagram.jison``.

This is **step 1** of a two-step pipeline:

    1. Source parse  → semantic data (alias, label, tech, descr, type, rels)
    2. SVG geometry  → positions matched to aliases from step 1

The parser handles C4Context, C4Container, C4Component, C4Dynamic, and
C4Deployment diagrams.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ═══════════════════════════════════════════════════════════
# Data classes
# ═══════════════════════════════════════════════════════════

@dataclass
class C4Shape:
    """A parsed C4 element (person, system, container, component, etc.).

    Attributes:
        alias: Unique identifier used in Rel() references.
        label: Human-readable name.
        c4_type: Internal type string (e.g. ``person``, ``container_db``).
        tech: Technology tag (containers/components only).
        descr: Description text.
        parent_boundary: Alias of the enclosing boundary, or ``"global"``.
    """
    alias: str = ""
    label: str = ""
    c4_type: str = ""
    tech: str = ""
    descr: str = ""
    parent_boundary: str = "global"


@dataclass
class C4Rel:
    """A parsed C4 relationship.

    Attributes:
        rel_type: Relationship direction (``rel``, ``birel``, ``rel_u``, etc.).
        from_alias: Source element alias.
        to_alias: Target element alias.
        label: Relationship label.
        tech: Technology/protocol (e.g. ``JSON/HTTPS``, ``SMTP``).
        descr: Description text.
    """
    rel_type: str = ""
    from_alias: str = ""
    to_alias: str = ""
    label: str = ""
    tech: str = ""
    descr: str = ""


@dataclass
class C4Boundary:
    """A parsed C4 boundary (enterprise, system, container, or deployment node).

    Attributes:
        alias: Unique identifier.
        label: Human-readable name.
        boundary_type: Type string (``ENTERPRISE``, ``SYSTEM``, ``CONTAINER``, etc.).
        parent_boundary: Alias of the enclosing boundary, or ``"global"``.
    """
    alias: str = ""
    label: str = ""
    boundary_type: str = ""
    parent_boundary: str = "global"


@dataclass
class C4ParseResult:
    """Complete result from parsing a C4 source file.

    Attributes:
        diagram_type: One of ``C4Context``, ``C4Container``, ``C4Component``,
            ``C4Dynamic``, ``C4Deployment``.
        title: Diagram title (if any).
        shapes: All parsed elements (persons, systems, containers, components).
        boundaries: All parsed boundaries.
        rels: All parsed relationships.
    """
    diagram_type: str = ""
    title: str = ""
    shapes: List[C4Shape] = field(default_factory=list)
    boundaries: List[C4Boundary] = field(default_factory=list)
    rels: List[C4Rel] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# Keyword → argument-signature mapping
# ═══════════════════════════════════════════════════════════

# Person/System: (alias, label, ?descr, ?sprite, ?tags, ?link)
_PERSON_SYSTEM_KEYWORDS: Dict[str, str] = {
    "Person":              "person",
    "Person_Ext":          "external_person",
    "System":              "system",
    "SystemDb":            "system_db",
    "SystemQueue":         "system_queue",
    "System_Ext":          "external_system",
    "SystemDb_Ext":        "external_system_db",
    "SystemQueue_Ext":     "external_system_queue",
}

# Container/Component: (alias, label, ?techn, ?descr, ?sprite, ?tags, ?link)
_CONTAINER_COMPONENT_KEYWORDS: Dict[str, str] = {
    "Container":             "container",
    "ContainerDb":           "container_db",
    "ContainerQueue":        "container_queue",
    "Container_Ext":         "external_container",
    "ContainerDb_Ext":       "external_container_db",
    "ContainerQueue_Ext":    "external_container_queue",
    "Component":             "component",
    "ComponentDb":           "component_db",
    "ComponentQueue":        "component_queue",
    "Component_Ext":         "external_component",
    "ComponentDb_Ext":       "external_component_db",
    "ComponentQueue_Ext":    "external_component_queue",
}

# Relationship: (from, to, label, ?techn, ?descr, ?sprite, ?tags, ?link)
_REL_KEYWORDS = {
    "Rel", "BiRel", "Rel_Up", "Rel_U", "Rel_Down", "Rel_D",
    "Rel_Left", "Rel_L", "Rel_Right", "Rel_R", "Rel_Back",
}

# Boundary: (alias, label, ?type, ?tags, ?link) — opens a { } block
_BOUNDARY_KEYWORDS: Dict[str, str] = {
    "Enterprise_Boundary":  "ENTERPRISE",
    "System_Boundary":      "SYSTEM",
    "Boundary":             "",
    "Container_Boundary":   "CONTAINER",
    "Deployment_Node":      "node",
    "Node":                 "node",
    "Node_L":               "nodeL",
    "Node_R":               "nodeR",
}

# Diagram type keywords
_DIAGRAM_TYPES = {"C4Context", "C4Container", "C4Component", "C4Dynamic", "C4Deployment"}

# Style/layout keywords — recognised and skipped
_SKIP_KEYWORDS = {"UpdateElementStyle", "UpdateRelStyle", "UpdateLayoutConfig", "RelIndex"}


# ═══════════════════════════════════════════════════════════
# Attribute extraction
# ═══════════════════════════════════════════════════════════

def _extract_attributes(paren_content: str) -> List[str]:
    """Extract comma-separated attributes from the content inside ``(...)``.

    Handles quoted strings (which may contain commas), bare identifiers,
    empty attributes (``,,``), and ``$key="value"`` pairs (skipped).

    Args:
        paren_content: The text between ``(`` and ``)``, exclusive.

    Returns:
        List of attribute strings with quotes stripped.
    """
    attrs: List[str] = []
    i = 0
    current: List[str] = []

    while i < len(paren_content):
        ch = paren_content[i]
        if ch == '"':
            # Quoted string — collect until closing quote
            i += 1
            start = i
            while i < len(paren_content) and paren_content[i] != '"':
                i += 1
            attrs.append(paren_content[start:i])
            i += 1  # skip closing quote
        elif ch == ',':
            # Separator — flush any bare token
            bare = "".join(current).strip()
            if bare:
                # Skip $key="value" style attributes
                if not bare.startswith("$"):
                    attrs.append(bare)
                current = []
            elif not attrs:
                # Leading comma → empty first attribute
                attrs.append("")
            i += 1
        elif ch == '$':
            # $key="value" — skip to next comma or end
            while i < len(paren_content) and paren_content[i] != ',':
                i += 1
            current = []
        else:
            current.append(ch)
            i += 1

    # Flush trailing bare token
    bare = "".join(current).strip()
    if bare and not bare.startswith("$"):
        attrs.append(bare)

    return attrs


def _find_paren_content(text: str, start: int) -> Optional[str]:
    """Find matching parentheses starting from ``start`` and return the content.

    Args:
        text: Full source text.
        start: Index of the opening ``(``.

    Returns:
        Content between ``(`` and ``)`` or None if unbalanced.
    """
    if start >= len(text) or text[start] != "(":
        return None
    depth = 0
    i = start
    while i < len(text):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return text[start + 1:i]
        i += 1
    return None


# ═══════════════════════════════════════════════════════════
# Main parser
# ═══════════════════════════════════════════════════════════

def parse_c4_source(text: str) -> C4ParseResult:
    """Parse Mermaid C4 source text into structured data.

    Args:
        text: Full content of a ``.mmd`` or ``.mermaid`` file.

    Returns:
        Parsed result with shapes, boundaries, and relationships.

    Raises:
        ValueError: If the text does not start with a C4 diagram keyword.
    """
    result = C4ParseResult()

    # Strip leading whitespace and detect diagram type
    stripped = text.strip()
    first_line = stripped.split("\n", 1)[0].strip()

    for dt in _DIAGRAM_TYPES:
        if first_line.startswith(dt):
            result.diagram_type = dt
            break
    if not result.diagram_type:
        raise ValueError(
            f"Not a C4 diagram. First line must start with one of: "
            f"{', '.join(sorted(_DIAGRAM_TYPES))}"
        )

    # Remove comments (%% ...)
    text = re.sub(r"%%[^\n]*", "", text)

    # Track boundary nesting
    boundary_stack: List[str] = ["global"]

    # Extract title
    title_m = re.search(r"^\s*title\s+(.+)$", text, re.MULTILINE)
    if title_m:
        result.title = title_m.group(1).strip()

    # Build combined keyword pattern (longest match first to avoid prefix collisions)
    all_keywords = sorted(
        (list(_PERSON_SYSTEM_KEYWORDS.keys())
         + list(_CONTAINER_COMPONENT_KEYWORDS.keys())
         + list(_REL_KEYWORDS)
         + list(_BOUNDARY_KEYWORDS.keys())
         + list(_SKIP_KEYWORDS)),
        key=len,
        reverse=True,
    )
    kw_pattern = re.compile(
        r"\b(" + "|".join(re.escape(k) for k in all_keywords) + r")\s*\(",
    )

    # Also handle closing braces for boundary nesting
    # Walk through the text finding keywords and braces
    pos = 0
    while pos < len(text):
        # Skip whitespace and newlines
        if text[pos] in " \t\r\n":
            pos += 1
            continue

        # Closing brace — pop boundary stack
        if text[pos] == "}":
            if len(boundary_stack) > 1:
                boundary_stack.pop()
            pos += 1
            continue

        # Opening brace (standalone, not after a keyword paren)
        if text[pos] == "{":
            pos += 1
            continue

        # Try keyword match at current position
        m = kw_pattern.match(text, pos)
        if not m:
            # Advance to next line or next interesting char
            nl = text.find("\n", pos)
            pos = nl + 1 if nl >= 0 else len(text)
            continue

        keyword = m.group(1)
        paren_start = m.end() - 1  # index of '('
        content = _find_paren_content(text, paren_start)
        if content is None:
            pos = m.end()
            continue

        attrs = _extract_attributes(content)
        # Advance past the closing paren
        pos = paren_start + len(content) + 2  # +2 for ( and )

        current_boundary = boundary_stack[-1]

        # ── Skip styling/layout keywords ──
        if keyword in _SKIP_KEYWORDS:
            continue

        # ── Person / System ──
        if keyword in _PERSON_SYSTEM_KEYWORDS:
            c4_type = _PERSON_SYSTEM_KEYWORDS[keyword]
            shape = C4Shape(
                alias=attrs[0] if len(attrs) > 0 else "",
                label=attrs[1] if len(attrs) > 1 else "",
                c4_type=c4_type,
                descr=attrs[2] if len(attrs) > 2 else "",
                parent_boundary=current_boundary,
            )
            result.shapes.append(shape)
            continue

        # ── Container / Component ──
        if keyword in _CONTAINER_COMPONENT_KEYWORDS:
            c4_type = _CONTAINER_COMPONENT_KEYWORDS[keyword]
            shape = C4Shape(
                alias=attrs[0] if len(attrs) > 0 else "",
                label=attrs[1] if len(attrs) > 1 else "",
                c4_type=c4_type,
                tech=attrs[2] if len(attrs) > 2 else "",
                descr=attrs[3] if len(attrs) > 3 else "",
                parent_boundary=current_boundary,
            )
            result.shapes.append(shape)
            continue

        # ── Relationship ──
        if keyword in _REL_KEYWORDS:
            # Normalise directional aliases to canonical form
            _REL_TYPE_MAP = {
                "Rel": "rel", "BiRel": "birel", "Rel_Back": "rel_b",
                "Rel_Up": "rel_u", "Rel_U": "rel_u",
                "Rel_Down": "rel_d", "Rel_D": "rel_d",
                "Rel_Left": "rel_l", "Rel_L": "rel_l",
                "Rel_Right": "rel_r", "Rel_R": "rel_r",
            }
            rel_type = _REL_TYPE_MAP.get(keyword, keyword.lower())
            rel = C4Rel(
                rel_type=rel_type,
                from_alias=attrs[0] if len(attrs) > 0 else "",
                to_alias=attrs[1] if len(attrs) > 1 else "",
                label=attrs[2] if len(attrs) > 2 else "",
                tech=attrs[3] if len(attrs) > 3 else "",
                descr=attrs[4] if len(attrs) > 4 else "",
            )
            result.rels.append(rel)
            continue

        # ── Boundary ──
        if keyword in _BOUNDARY_KEYWORDS:
            btype = _BOUNDARY_KEYWORDS[keyword]
            # For boundaries with explicit type in attrs[2]
            if not btype and len(attrs) > 2:
                btype = attrs[2]
            boundary = C4Boundary(
                alias=attrs[0] if len(attrs) > 0 else "",
                label=attrs[1] if len(attrs) > 1 else "",
                boundary_type=btype,
                parent_boundary=current_boundary,
            )
            result.boundaries.append(boundary)
            # Push onto boundary stack — the { will be consumed by the main loop
            boundary_stack.append(boundary.alias)
            continue

    return result


def parse_c4_source_file(path: str) -> C4ParseResult:
    """Parse a C4 source file.

    Args:
        path: Path to the ``.mmd`` or ``.mermaid`` file.

    Returns:
        Parsed result.
    """
    with open(path, "r", encoding="utf-8") as f:
        return parse_c4_source(f.read())
