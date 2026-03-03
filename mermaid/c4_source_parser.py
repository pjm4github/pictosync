"""
mermaid/c4_source_parser.py

Parse Mermaid C4 source text (.mmd/.mermaid) into structured shape and
relationship data using an ANTLR4 grammar (MermaidC4Lexer + MermaidC4Parser).

This is **step 1** of a two-step pipeline:

    1. Source parse  → semantic data (alias, label, tech, descr, type, rels)
    2. SVG geometry  → positions matched to aliases from step 1

The parser handles C4Context, C4Container, C4Component, C4Dynamic, and
C4Deployment diagrams.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from antlr4 import CommonTokenStream, InputStream

# Ensure the generated/ package is importable
_grammar_dir = str(Path(__file__).resolve().parent / "grammar")
_generated_dir = str(Path(__file__).resolve().parent / "grammar" / "generated")
if _grammar_dir not in sys.path:
    sys.path.insert(0, _grammar_dir)
if _generated_dir not in sys.path:
    sys.path.insert(0, _generated_dir)

from MermaidC4Lexer import MermaidC4Lexer          # noqa: E402
from MermaidC4Parser import MermaidC4Parser         # noqa: E402
from MermaidC4ParserVisitor import MermaidC4ParserVisitor  # noqa: E402


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
# Token → type mapping dicts
# ═══════════════════════════════════════════════════════════

P = MermaidC4Parser

_ELEMENT_TOKEN_TO_C4TYPE = {
    P.PERSON: "person",               P.PERSON_EXT: "external_person",
    P.SYSTEM: "system",               P.SYSTEM_EXT: "external_system",
    P.SYSTEM_DB: "system_db",         P.SYSTEM_DB_EXT: "external_system_db",
    P.SYSTEM_QUEUE: "system_queue",   P.SYSTEM_QUEUE_EXT: "external_system_queue",
    P.CONTAINER: "container",         P.CONTAINER_EXT: "external_container",
    P.CONTAINER_DB: "container_db",   P.CONTAINER_DB_EXT: "external_container_db",
    P.CONTAINER_QUEUE: "container_queue",
    P.CONTAINER_QUEUE_EXT: "external_container_queue",
    P.COMPONENT: "component",         P.COMPONENT_EXT: "external_component",
    P.COMPONENT_DB: "component_db",   P.COMPONENT_DB_EXT: "external_component_db",
    P.COMPONENT_QUEUE: "component_queue",
    P.COMPONENT_QUEUE_EXT: "external_component_queue",
}

# Person/System keywords use 2-arg signature: (alias, label, ?descr)
_PERSON_SYSTEM_TOKENS = {
    P.PERSON, P.PERSON_EXT,
    P.SYSTEM, P.SYSTEM_EXT,
    P.SYSTEM_DB, P.SYSTEM_DB_EXT,
    P.SYSTEM_QUEUE, P.SYSTEM_QUEUE_EXT,
}

_REL_TOKEN_TO_TYPE = {
    P.REL: "rel", P.BIREL: "birel", P.REL_BACK: "rel_b",
    P.REL_U: "rel_u", P.REL_UP: "rel_u",
    P.REL_D: "rel_d", P.REL_DOWN: "rel_d",
    P.REL_L: "rel_l", P.REL_LEFT: "rel_l",
    P.REL_R: "rel_r", P.REL_RIGHT: "rel_r",
    P.REL_INDEX: "rel",
}

_BOUNDARY_TOKEN_TO_TYPE = {
    P.ENTERPRISE_BOUNDARY: "ENTERPRISE",
    P.SYSTEM_BOUNDARY: "SYSTEM",
    P.CONTAINER_BOUNDARY: "CONTAINER",
    P.BOUNDARY: "",
}

_DEPLOY_TOKEN_TO_TYPE = {
    P.DEPLOYMENT_NODE: "node",
    P.NODE: "node",
    P.NODE_L: "nodeL",
    P.NODE_R: "nodeR",
}

_DIAGRAM_TYPE_TOKENS = {
    P.C4CONTEXT: "C4Context",
    P.C4CONTAINER: "C4Container",
    P.C4COMPONENT: "C4Component",
    P.C4DYNAMIC: "C4Dynamic",
    P.C4DEPLOYMENT: "C4Deployment",
}

_C4_HEADER_KEYWORDS = set(_DIAGRAM_TYPE_TOKENS.values())


# ═══════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════

def _strip_quotes(text: str) -> str:
    """Remove surrounding double quotes from a string."""
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        return text[1:-1]
    return text


def _extract_positional_args(arg_list_ctx: MermaidC4Parser.ArgListContext) -> List[str]:
    """Extract positional arguments from an argList context.

    Skips named arguments (``$key="value"``).  Strips surrounding quotes
    from ``QUOTED_STRING`` tokens.

    Args:
        arg_list_ctx: ANTLR4 argList context node.

    Returns:
        List of positional argument strings.
    """
    if arg_list_ctx is None:
        return []
    args: List[str] = []
    for arg_ctx in arg_list_ctx.arg():
        # Skip named args ($key="value")
        if arg_ctx.namedArg() is not None:
            continue
        pos_ctx = arg_ctx.positionalArg()
        if pos_ctx is None:
            continue
        # QUOTED_STRING includes the surrounding quotes
        qs = pos_ctx.QUOTED_STRING()
        if qs is not None:
            args.append(_strip_quotes(qs.getText()))
        else:
            # ID, UNQUOTED_TEXT, or INT — raw text
            args.append(pos_ctx.getText())
    return args


# ═══════════════════════════════════════════════════════════
# ANTLR4 Visitor
# ═══════════════════════════════════════════════════════════

class _C4Visitor(MermaidC4ParserVisitor):
    """Walk the ANTLR4 parse tree and populate a ``C4ParseResult``."""

    def __init__(self) -> None:
        self.result = C4ParseResult()
        self._boundary_stack: List[str] = ["global"]

    # ── Diagram ──────────────────────────────────────────

    def visitDiagram(self, ctx: MermaidC4Parser.DiagramContext):
        dt_ctx = ctx.diagramType()
        token_type = dt_ctx.start.type
        self.result.diagram_type = _DIAGRAM_TYPE_TOKENS.get(token_type, "")
        return self.visitChildren(ctx)

    # ── Title ────────────────────────────────────────────

    def visitTitleStmt(self, ctx: MermaidC4Parser.TitleStmtContext):
        tt_ctx = ctx.titleText()
        if tt_ctx is None:
            return None
        qs = tt_ctx.QUOTED_STRING()
        if qs is not None:
            self.result.title = _strip_quotes(qs.getText())
        else:
            tr = tt_ctx.TEXT_REST()
            if tr is not None:
                self.result.title = tr.getText().strip()
        return None

    # ── Element ──────────────────────────────────────────

    def visitElementStmt(self, ctx: MermaidC4Parser.ElementStmtContext):
        kw_ctx = ctx.elementKw()
        token_type = kw_ctx.start.type
        c4_type = _ELEMENT_TOKEN_TO_C4TYPE.get(token_type, "")

        args = _extract_positional_args(ctx.argList())
        current_boundary = self._boundary_stack[-1]

        if token_type in _PERSON_SYSTEM_TOKENS:
            # Person/System: (alias, label, ?descr)
            shape = C4Shape(
                alias=args[0] if len(args) > 0 else "",
                label=args[1] if len(args) > 1 else "",
                c4_type=c4_type,
                descr=args[2] if len(args) > 2 else "",
                parent_boundary=current_boundary,
            )
        else:
            # Container/Component: (alias, label, ?tech, ?descr)
            shape = C4Shape(
                alias=args[0] if len(args) > 0 else "",
                label=args[1] if len(args) > 1 else "",
                c4_type=c4_type,
                tech=args[2] if len(args) > 2 else "",
                descr=args[3] if len(args) > 3 else "",
                parent_boundary=current_boundary,
            )
        self.result.shapes.append(shape)
        return None

    # ── Boundary ─────────────────────────────────────────

    def visitBoundaryBlock(self, ctx: MermaidC4Parser.BoundaryBlockContext):
        kw_ctx = ctx.boundaryKw()
        token_type = kw_ctx.start.type
        btype = _BOUNDARY_TOKEN_TO_TYPE.get(token_type, "")

        args = _extract_positional_args(ctx.argList())

        # For generic Boundary(), the type comes from the third positional arg
        if not btype and len(args) > 2:
            btype = args[2]

        current_boundary = self._boundary_stack[-1]
        boundary = C4Boundary(
            alias=args[0] if len(args) > 0 else "",
            label=args[1] if len(args) > 1 else "",
            boundary_type=btype,
            parent_boundary=current_boundary,
        )
        self.result.boundaries.append(boundary)

        # Push boundary onto stack and visit nested statements
        self._boundary_stack.append(boundary.alias)
        self.visitChildren(ctx)
        self._boundary_stack.pop()
        return None

    # ── Deployment Node ──────────────────────────────────

    def visitDeployNodeBlock(self, ctx: MermaidC4Parser.DeployNodeBlockContext):
        kw_ctx = ctx.deployNodeKw()
        token_type = kw_ctx.start.type
        btype = _DEPLOY_TOKEN_TO_TYPE.get(token_type, "node")

        args = _extract_positional_args(ctx.argList())
        current_boundary = self._boundary_stack[-1]

        boundary = C4Boundary(
            alias=args[0] if len(args) > 0 else "",
            label=args[1] if len(args) > 1 else "",
            boundary_type=btype,
            parent_boundary=current_boundary,
        )
        self.result.boundaries.append(boundary)

        # Push boundary onto stack and visit nested statements
        self._boundary_stack.append(boundary.alias)
        self.visitChildren(ctx)
        self._boundary_stack.pop()
        return None

    # ── Relationship ─────────────────────────────────────

    def visitRelationStmt(self, ctx: MermaidC4Parser.RelationStmtContext):
        kw_ctx = ctx.relKw()
        token_type = kw_ctx.start.type
        rel_type = _REL_TOKEN_TO_TYPE.get(token_type, "rel")

        args = _extract_positional_args(ctx.argList())

        # RelIndex has an extra leading integer index — skip it
        if token_type == P.REL_INDEX and args and args[0].isdigit():
            args = args[1:]

        rel = C4Rel(
            rel_type=rel_type,
            from_alias=args[0] if len(args) > 0 else "",
            to_alias=args[1] if len(args) > 1 else "",
            label=args[2] if len(args) > 2 else "",
            tech=args[3] if len(args) > 3 else "",
            descr=args[4] if len(args) > 4 else "",
        )
        self.result.rels.append(rel)
        return None

    # ── Style/layout/tags — skip ─────────────────────────

    def visitStyleStmt(self, ctx):
        return None

    def visitLayoutStmt(self, ctx):
        return None

    def visitAddTagStmt(self, ctx):
        return None


# ═══════════════════════════════════════════════════════════
# Public API
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
    # Quick validation — first non-blank line must start with a C4 keyword
    stripped = text.strip()
    first_line = stripped.split("\n", 1)[0].strip()
    if not any(first_line.startswith(kw) for kw in _C4_HEADER_KEYWORDS):
        raise ValueError(
            f"Not a C4 diagram. First line must start with one of: "
            f"{', '.join(sorted(_C4_HEADER_KEYWORDS))}"
        )

    # Pre-strip %% comments (inline comments confuse the grammar's
    # statement → NEWLINE+ expectation)
    text = re.sub(r"%%[^\n]*", "", text)

    # Ensure trailing newline (grammar expects NEWLINE+ after statements)
    if not text.endswith("\n"):
        text += "\n"

    # ANTLR4 pipeline
    input_stream = InputStream(text)
    lexer = MermaidC4Lexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = MermaidC4Parser(token_stream)
    tree = parser.diagram()

    # Walk with visitor
    visitor = _C4Visitor()
    visitor.visit(tree)
    return visitor.result


def parse_c4_source_file(path: str) -> C4ParseResult:
    """Parse a C4 source file.

    Args:
        path: Path to the ``.mmd`` or ``.mermaid`` file.

    Returns:
        Parsed result.
    """
    with open(path, "r", encoding="utf-8") as f:
        return parse_c4_source(f.read())
