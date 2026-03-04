"""
mermaid/flowchart_source_parser.py

Parse Mermaid flowchart/graph diagram source text (.mmd/.mermaid) into
structured node, edge, and subgraph data using the ANTLR4-generated parser.

This is **step 1** of a two-step pipeline:

    1. Source parse  -> semantic data (nodes, edges, subgraphs, styles)
    2. SVG geometry  -> positions matched to source data from step 1

The parser handles ``flowchart``/``graph`` sources with nodes (13 classic
shapes + @{} syntax), edges (solid/dotted/thick/invisible, all head types),
subgraphs, and styling statements (classDef, class, style, linkStyle).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from antlr4 import CommonTokenStream, InputStream

from mermaid.grammar.generated.MermaidFlowchartLexer import MermaidFlowchartLexer
from mermaid.grammar.generated.MermaidFlowchartParser import MermaidFlowchartParser
from mermaid.grammar.generated.MermaidFlowchartParserVisitor import (
    MermaidFlowchartParserVisitor,
)


# ═══════════════════════════════════════════════════════════
# Data classes
# ═══════════════════════════════════════════════════════════


@dataclass
class FlowNode:
    """A parsed flowchart node.

    Attributes:
        node_id: Internal identifier used in edges.
        label: Display label text.
        shape: Node shape (e.g. ``"rectangle"``, ``"rounded"``, ``"rhombus"``).
        css_class: Class shorthand name (if any).
        attrs: Attribute dict from ``@{}`` syntax.
    """

    node_id: str = ""
    label: str = ""
    shape: str = "rectangle"
    css_class: str = ""
    attrs: Dict[str, str] = field(default_factory=dict)


@dataclass
class FlowEdge:
    """A parsed flowchart edge.

    Attributes:
        from_id: Source node id.
        to_id: Target node id.
        label: Edge label text.
        line_style: ``"solid"``, ``"dotted"``, ``"thick"``, or ``"invisible"``.
        left_head: ``"arrow"``, ``"circle"``, ``"cross"``, or ``"none"``.
        right_head: ``"arrow"``, ``"circle"``, ``"cross"``, or ``"none"``.
        edge_id: Optional edge ID prefix (v11+).
    """

    from_id: str = ""
    to_id: str = ""
    label: str = ""
    line_style: str = "solid"
    left_head: str = "none"
    right_head: str = "arrow"
    edge_id: str = ""


@dataclass
class FlowSubgraph:
    """A parsed flowchart subgraph.

    Attributes:
        subgraph_id: Subgraph identifier.
        title: Display title.
        children: List of child node IDs contained in this subgraph.
    """

    subgraph_id: str = ""
    title: str = ""
    children: List[str] = field(default_factory=list)


@dataclass
class FlowClassDef:
    """A parsed ``classDef`` statement.

    Attributes:
        names: Class name(s).
        css: Raw CSS string.
    """

    names: List[str] = field(default_factory=list)
    css: str = ""


@dataclass
class FlowParseResult:
    """Complete result from parsing a flowchart source file.

    Attributes:
        direction: Graph direction (``"TD"``, ``"TB"``, ``"BT"``, ``"LR"``,
            ``"RL"``).
        nodes: All declared nodes.
        edges: All parsed edges.
        subgraphs: All parsed subgraphs.
        class_defs: All ``classDef`` statements.
        class_assigns: Node ID -> class name assignments.
        node_styles: Node ID -> CSS string from ``style`` statements.
    """

    direction: str = "TD"
    nodes: List[FlowNode] = field(default_factory=list)
    edges: List[FlowEdge] = field(default_factory=list)
    subgraphs: List[FlowSubgraph] = field(default_factory=list)
    class_defs: List[FlowClassDef] = field(default_factory=list)
    class_assigns: Dict[str, str] = field(default_factory=dict)
    node_styles: Dict[str, str] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════
# Shape classification
# ═══════════════════════════════════════════════════════════


def _classify_classic_shape(ctx: MermaidFlowchartParser.ClassicShapeContext) -> str:
    """Determine the shape name from a ``classicShape`` context.

    Maps the 14 ANTLR parse tree alternatives to shape names based on
    child count and delimiter tokens.
    """
    cc = ctx.getChildCount()

    if cc == 7:
        return "double_circle"  # (((t)))

    first = ctx.getChild(0).getText()

    if cc == 5:
        second = ctx.getChild(1).getText()
        if first == "[" and second == "[":
            return "subroutine"  # [[t]]
        if first == "{" and second == "{":
            return "hexagon"  # {{t}}
        if first == "(" and second == "[":
            return "stadium"  # ([t])
        if first == "[" and second == "(":
            return "cylinder"  # [(t)]
        if first == "(" and second == "(":
            return "circle"  # ((t))
        # Parallelogram variants: [/...] or [\...]
        if first == "[":
            fourth = ctx.getChild(3).getText()
            if second == "/" and fourth == "/":
                return "parallelogram"  # [/t/]
            if second == "\\" and fourth == "\\":
                return "parallelogram_alt"  # [\t\]
            if second == "/" and fourth == "\\":
                return "trapezoid"  # [/t\]
            if second == "\\" and fourth == "/":
                return "trapezoid_alt"  # [\t/]

    if cc == 3:
        if first == "[":
            return "rectangle"  # [t]
        if first == "(":
            return "rounded"  # (t)
        if first == ">":
            return "asymmetric"  # >t]
        if first == "{":
            return "rhombus"  # {t}

    return "rectangle"  # fallback


# ═══════════════════════════════════════════════════════════
# Edge decoding
# ═══════════════════════════════════════════════════════════

_HEAD_MAP = {">": "arrow", "<": "arrow", "o": "circle", "x": "cross"}


def _decode_edge_token(text: str, token_type: int) -> Tuple[str, str, str, str]:
    """Decode an edge token into semantic components.

    Args:
        text: The edge token text (e.g. ``"-->"``, ``"<-.->"``, ``"==>"``).
        token_type: The ANTLR token type.

    Returns:
        ``(line_style, left_head, right_head, embedded_label)``
    """
    # Determine line style from token type
    if token_type == MermaidFlowchartParser.EDGE_SOLID:
        line_style = "solid"
    elif token_type == MermaidFlowchartParser.EDGE_DOTTED:
        line_style = "dotted"
    elif token_type == MermaidFlowchartParser.EDGE_THICK:
        line_style = "thick"
    else:
        return "invisible", "none", "none", ""

    # Left head
    left_head = "none"
    if text and text[0] in _HEAD_MAP:
        left_head = _HEAD_MAP[text[0]]

    # Right head
    right_head = "none"
    if text and text[-1] in _HEAD_MAP:
        right_head = _HEAD_MAP[text[-1]]

    # Embedded label for solid edges: --text-->
    embedded_label = ""
    if line_style == "solid" and len(text) > 2:
        inner = text
        if left_head != "none":
            inner = inner[1:]
        if right_head != "none":
            inner = inner[:-1]
        # Match text between dashes: --label--
        m = re.match(r"^-+(.+?)-+$", inner)
        if m:
            candidate = m.group(1)
            if not all(c == "-" for c in candidate):
                embedded_label = candidate

    return line_style, left_head, right_head, embedded_label


# ═══════════════════════════════════════════════════════════
# Node label extraction
# ═══════════════════════════════════════════════════════════


def _extract_node_label(ctx: MermaidFlowchartParser.NodeLabelContext) -> str:
    """Extract the text from a ``nodeLabel`` context.

    Handles quoted strings, markdown strings, and plain text.
    """
    if ctx is None:
        return ""

    qs = ctx.QUOTED_STRING()
    if qs is not None:
        return qs.getText()[1:-1]

    ms = ctx.MARKDOWN_STRING()
    if ms is not None:
        txt = ms.getText()
        if txt.startswith('"') and txt.endswith('"'):
            txt = txt[1:-1]
        if txt.startswith("`") and txt.endswith("`"):
            txt = txt[1:-1]
        return txt

    # Plain label text — concatenate all labelText children
    parts = []
    for lt in ctx.labelText() or []:
        parts.append(lt.getText())
    return " ".join(parts)


# ═══════════════════════════════════════════════════════════
# ANTLR Visitor
# ═══════════════════════════════════════════════════════════


class _FlowchartVisitor(MermaidFlowchartParserVisitor):
    """Visitor that extracts semantic data from the ANTLR parse tree."""

    def __init__(self) -> None:
        self.result = FlowParseResult()
        self._known_nodes: Dict[str, FlowNode] = {}
        self._subgraph_stack: List[FlowSubgraph] = []

    # ── Helpers ──

    def _ensure_node(self, node_id: str) -> FlowNode:
        """Get or create a node by ID."""
        if node_id not in self._known_nodes:
            node = FlowNode(node_id=node_id, label=node_id)
            self._known_nodes[node_id] = node
            self.result.nodes.append(node)
            if self._subgraph_stack:
                self._subgraph_stack[-1].children.append(node_id)
        return self._known_nodes[node_id]

    def _process_node_ref(
        self, ctx: MermaidFlowchartParser.NodeRefContext
    ) -> List[str]:
        """Process a ``nodeRef`` context, returning the node ID(s)."""
        node_id_ctx = ctx.nodeId()
        if node_id_ctx is None:
            return []

        nid = node_id_ctx.getText()
        node = self._ensure_node(nid)

        # Classic shape
        shape_ctx = ctx.classicShape()
        if shape_ctx is not None:
            node.shape = _classify_classic_shape(shape_ctx)
            label_ctx = shape_ctx.nodeLabel()
            if label_ctx is not None:
                node.label = _extract_node_label(label_ctx)

        # @{} attributes
        attr_ctx = ctx.attrBlock()
        if attr_ctx is not None:
            attrs = self._extract_attrs(attr_ctx)
            node.attrs = attrs
            if "shape" in attrs:
                node.shape = attrs["shape"]
            if "label" in attrs:
                node.label = attrs["label"]

        # Class shorthand
        class_ctx = ctx.classShorthand()
        if class_ctx is not None:
            id_token = class_ctx.ID()
            if id_token is not None:
                node.css_class = id_token.getText()

        return [nid]

    def _extract_attrs(
        self, ctx: MermaidFlowchartParser.AttrBlockContext
    ) -> Dict[str, str]:
        """Extract key-value pairs from an ``attrBlock`` context."""
        attrs: Dict[str, str] = {}
        attr_list = ctx.attrList()
        if attr_list is None:
            return attrs
        for attr_ctx in attr_list.attr() or []:
            key_ctx = attr_ctx.attrKey()
            val_ctx = attr_ctx.attrVal()
            if key_ctx and val_ctx:
                key = key_ctx.getText()
                val = val_ctx.getText()
                if val.startswith('"') and val.endswith('"'):
                    val = val[1:-1]
                attrs[key] = val
        return attrs

    # ── Visitor methods ──

    def visitHeader(self, ctx: MermaidFlowchartParser.HeaderContext):
        """Extract graph direction from the header."""
        dir_ctx = ctx.direction()
        if dir_ctx is not None:
            self.result.direction = dir_ctx.getText()
        return self.visitChildren(ctx)

    def visitDirectionStmt(self, ctx: MermaidFlowchartParser.DirectionStmtContext):
        """Handle ``direction`` statement inside subgraphs."""
        return None  # Recognised but not stored separately

    def visitNodeStmt(self, ctx: MermaidFlowchartParser.NodeStmtContext):
        """Process an explicit node declaration."""
        node_id_ctx = ctx.nodeId()
        if node_id_ctx is None:
            return None

        nid = node_id_ctx.getText()
        node = self._ensure_node(nid)

        # Classic shape
        shape_ctx = ctx.classicShape()
        if shape_ctx is not None:
            node.shape = _classify_classic_shape(shape_ctx)
            label_ctx = shape_ctx.nodeLabel()
            if label_ctx is not None:
                node.label = _extract_node_label(label_ctx)

        # @{} attributes
        attr_ctx = ctx.attrBlock()
        if attr_ctx is not None:
            attrs = self._extract_attrs(attr_ctx)
            node.attrs = attrs
            if "shape" in attrs:
                node.shape = attrs["shape"]
            if "label" in attrs:
                node.label = attrs["label"]

        # Class shorthand
        class_ctx = ctx.classShorthand()
        if class_ctx is not None:
            id_token = class_ctx.ID()
            if id_token is not None:
                node.css_class = id_token.getText()

        return None

    def visitEdgeChainStmt(self, ctx: MermaidFlowchartParser.EdgeChainStmtContext):
        """Process ``A --> B --> C`` edge chains.

        An edge chain has N+1 node groups connected by N edge operators.
        Each node group may contain multiple node refs separated by ``&``.
        """
        node_groups = ctx.nodeGroup() or []
        edge_ops = ctx.edgeOp() or []

        # Collect node IDs from each group
        group_ids: List[List[str]] = []
        for ng in node_groups:
            ids: List[str] = []
            for nr in ng.nodeRef() or []:
                ids.extend(self._process_node_ref(nr))
            group_ids.append(ids)

        # Create edges between consecutive groups
        for i, eop in enumerate(edge_ops):
            if i + 1 >= len(group_ids):
                break

            # Decode edge operator
            edge_ctx = eop.edge()
            if edge_ctx is None or not getattr(edge_ctx, "children", None):
                continue
            edge_token = edge_ctx.getChild(0)
            if edge_token is None or not hasattr(edge_token, "symbol"):
                continue
            token_text = edge_token.getText()
            token_type = edge_token.symbol.type
            line_style, left_head, right_head, embedded_label = _decode_edge_token(
                token_text, token_type
            )

            # Pipe label
            label = embedded_label
            pipe_ctx = eop.pipeLabel()
            if pipe_ctx is not None:
                pipe_text = pipe_ctx.getText()
                if pipe_text.startswith("|") and pipe_text.endswith("|"):
                    label = pipe_text[1:-1].strip()

            # Edge ID prefix
            edge_id = ""
            eid_ctx = eop.edgeIdPrefix()
            if eid_ctx is not None:
                id_token = eid_ctx.ID()
                if id_token is not None:
                    edge_id = id_token.getText()

            # Create edges for all source x target combinations (& operator)
            source_ids = group_ids[i]
            target_ids = group_ids[i + 1]
            for src in source_ids:
                for tgt in target_ids:
                    self.result.edges.append(
                        FlowEdge(
                            from_id=src,
                            to_id=tgt,
                            label=label,
                            line_style=line_style,
                            left_head=left_head,
                            right_head=right_head,
                            edge_id=edge_id,
                        )
                    )

        return None

    def visitSubgraphBlock(self, ctx: MermaidFlowchartParser.SubgraphBlockContext):
        """Process a ``subgraph ... end`` block."""
        header = ctx.subgraphHeader()
        sg_id = ""
        title = ""

        if header is not None:
            id_token = header.ID()
            qs = header.QUOTED_STRING()

            if id_token is not None:
                sg_id = id_token.getText()

            if qs is not None:
                qt = qs.getText()[1:-1]
                if not sg_id:
                    # subgraph "Title" form — title only, derive id
                    title = qt
                    sg_id = qt.replace(" ", "_")
                else:
                    title = qt

            title_ctx = header.subgraphTitle()
            if title_ctx is not None:
                qs2 = title_ctx.QUOTED_STRING()
                if qs2 is not None:
                    title = qs2.getText()[1:-1]
                else:
                    label_ctx = title_ctx.nodeLabel()
                    if label_ctx is not None:
                        title = _extract_node_label(label_ctx)

        if not title:
            title = sg_id

        sg = FlowSubgraph(subgraph_id=sg_id, title=title)
        self.result.subgraphs.append(sg)

        # Push subgraph for child tracking
        self._subgraph_stack.append(sg)

        # Visit child statements
        for stmt in ctx.statement() or []:
            self.visit(stmt)

        self._subgraph_stack.pop()

        return None  # Prevent default visitChildren

    def visitClassDefStmt(self, ctx: MermaidFlowchartParser.ClassDefStmtContext):
        """Process a ``classDef`` statement."""
        name_list = ctx.classNameList()
        if name_list is None:
            return None
        names = [t.getText() for t in name_list.ID() or []]
        css = ""
        css_ctx = ctx.cssString()
        if css_ctx is not None:
            css_tokens = css_ctx.CSS_VALUE_START() or []
            css = " ".join(t.getText() for t in css_tokens).strip()
        self.result.class_defs.append(FlowClassDef(names=names, css=css))
        return None

    def visitClassAssignStmt(self, ctx: MermaidFlowchartParser.ClassAssignStmtContext):
        """Process a ``class nodeId[,nodeId] className`` statement."""
        node_list = ctx.nodeIdList()
        if node_list is None:
            return None
        node_ids = [t.getText() for t in node_list.ID() or []]
        class_name_token = ctx.ID()
        if class_name_token is not None:
            class_name = class_name_token.getText()
            for nid in node_ids:
                self.result.class_assigns[nid] = class_name
        return None

    def visitNodeStyleStmt(self, ctx: MermaidFlowchartParser.NodeStyleStmtContext):
        """Process a ``style nodeId css`` statement."""
        id_token = ctx.ID()
        if id_token is None:
            return None
        nid = id_token.getText()
        css = ""
        css_ctx = ctx.cssString()
        if css_ctx is not None:
            css_tokens = css_ctx.CSS_VALUE_START() or []
            css = " ".join(t.getText() for t in css_tokens).strip()
        self.result.node_styles[nid] = css
        return None

    def visitLinkStyleStmt(self, ctx: MermaidFlowchartParser.LinkStyleStmtContext):
        """Process a ``linkStyle`` statement (recognised but not stored)."""
        return None

    def visitClickStmt(self, ctx: MermaidFlowchartParser.ClickStmtContext):
        """Process a ``click`` statement (recognised but not stored)."""
        return None

    def visitEdgePropStmt(self, ctx: MermaidFlowchartParser.EdgePropStmtContext):
        """Process an edge property statement (recognised but not stored)."""
        return None


# ═══════════════════════════════════════════════════════════
# Silent error listener
# ═══════════════════════════════════════════════════════════


class _SilentErrorListener:
    """ANTLR4 error listener that suppresses console output."""

    def syntaxError(self, *args: Any, **kwargs: Any) -> None:
        pass

    def reportAmbiguity(self, *args: Any, **kwargs: Any) -> None:
        pass

    def reportAttemptingFullContext(self, *args: Any, **kwargs: Any) -> None:
        pass

    def reportContextSensitivity(self, *args: Any, **kwargs: Any) -> None:
        pass


# ═══════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════


def parse_flowchart_source(text: str) -> FlowParseResult:
    """Parse Mermaid flowchart/graph source text into structured data.

    Args:
        text: Full content of a ``.mmd`` or ``.mermaid`` file.

    Returns:
        Parsed result with nodes, edges, subgraphs, and styles.

    Raises:
        ValueError: If the text is not a flowchart/graph diagram.
    """
    # Strip YAML front matter (--- ... ---) if present
    text = re.sub(r"^---\s*\n.*?\n---\s*\n", "", text, count=1, flags=re.DOTALL)

    stripped = text.strip()
    if not stripped:
        raise ValueError("Not a flowchart diagram: empty source")

    # Find first non-comment, non-empty line
    first_keyword = None
    for line in stripped.splitlines():
        line_s = line.strip()
        if not line_s or line_s.startswith("%%"):
            continue
        first_keyword = line_s
        break

    if first_keyword is None:
        raise ValueError("Not a flowchart diagram: no content")

    if not (
        first_keyword.startswith("flowchart")
        or first_keyword.startswith("graph")
    ):
        raise ValueError(
            "Not a flowchart diagram. First line must start with "
            "'flowchart' or 'graph'."
        )

    # Parse with ANTLR4
    input_stream = InputStream(text)
    lexer = MermaidFlowchartLexer(input_stream)
    lexer.removeErrorListeners()
    lexer.addErrorListener(_SilentErrorListener())

    token_stream = CommonTokenStream(lexer)
    parser = MermaidFlowchartParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(_SilentErrorListener())

    tree = parser.diagram()

    visitor = _FlowchartVisitor()
    visitor.visit(tree)

    return visitor.result


def parse_flowchart_source_file(path: str) -> FlowParseResult:
    """Parse a flowchart source file.

    Args:
        path: Path to the ``.mmd`` or ``.mermaid`` file.

    Returns:
        Parsed result.

    Raises:
        ValueError: If the file does not contain a flowchart diagram.
    """
    with open(path, "r", encoding="utf-8") as f:
        return parse_flowchart_source(f.read())
