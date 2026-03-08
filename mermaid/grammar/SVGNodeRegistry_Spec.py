# SVGNodeRegistry — Specification v2
# Mermaid Sequence Diagram Renderer
# ============================================================
# VERSION NOTES (v2 vs v1)
# ─────────────────────────
# v1 assumed hand-written parse-tree traversal.
# v2 assumes the ANTLR4 tool-chain generates the recognizer:
#
#   antlr4 MermaidSequence.g4 -Dlanguage=Python3 -visitor -no-listener
#
# This produces:
#   MermaidSequenceLexer.py
#   MermaidSequenceParser.py          ← context classes live here
#   MermaidSequenceVisitor.py         ← abstract base with visitXxx stubs
#
# Consequences for the architecture:
#   • ASTNode gains a ctx field holding the originating parser context.
#     source_start / source_stop are read FROM ctx, not stored manually.
#   • The hand-written visitor in ast_visitor.py SUBCLASSES the generated
#     MermaidSequenceVisitor and overrides visitXxx methods to build AST nodes.
#   • The visitor is the ONLY place that touches parser context objects.
#     Everything downstream (layout, renderer, registry) works only with
#     AST node objects — no parser context leaks past the visitor boundary.
#   • The generated context class name for each rule is documented in
#     Section 2 so Claude Code knows which visitXxx method to implement.
#
# Target language : Python 3.13+
# SVG library     : xml.etree.ElementTree (stdlib)
# ANTLR4 runtime  : antlr4-python3-runtime >= 4.13
# PyQt version    : PyQt6
# Grammar file    : MermaidSequence.g4  (already written)
# ============================================================


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 1 — PIPELINE
# ──────────────────────────────────────────────────────────────────────────────
#
#  Source text  (mermaid sequenceDiagram string)
#       │
#       ▼  Stage 1 — ANTLR4 tool  [one-time build step, not runtime]
#  MermaidSequenceLexer.py          ← generated
#  MermaidSequenceParser.py         ← generated  (contains *Context classes)
#  MermaidSequenceVisitor.py        ← generated  (abstract visitXxx stubs)
#       │
#       ▼  Stage 2 — Runtime parse  (parse_diagram() in parser_runner.py)
#  antlr4.CommonTokenStream
#  antlr4.tree.ParseTree
#  MermaidSequenceParser.DiagramContext   ← root context object
#       │
#       ▼  Stage 3 — AST construction  (ASTBuildingVisitor in ast_visitor.py)
#  DiagramNode  (root of hand-written AST dataclass tree)
#       │
#       ▼  Stage 4 — Layout engine  (layout_engine.py)
#  LayoutModel  (pixel geometry)
#       │
#       ▼  Stage 5 — SVG renderer  (svg_renderer.py)
#  SVG DOM  (xml.etree.ElementTree)
#       │
#       ▼  Stage 6 — Registry population  [happens inside Stage 5]
#  SVGNodeRegistry  (bidirectional index)
#
#
# KEY BOUNDARY RULE
# ─────────────────
# Parser context objects (MermaidSequenceParser.*Context) MUST NOT cross
# the visitor boundary.  The visitor reads ctx fields, constructs AST nodes,
# and returns them.  All downstream code receives only ASTNode subclasses.
#
# The only exception is ASTNode.ctx which stores the originating context for
# error reporting and source-location queries.  It is typed as Any and must
# not be used for data extraction outside of ast_visitor.py.


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 2 — AST NODE HIERARCHY
# ──────────────────────────────────────────────────────────────────────────────
#
# FILE: ast_nodes.py
#
# Changes from v1:
#   • ASTNode gains  ctx: Any = None   (originating parser context)
#   • source_start / source_stop are PROPERTIES that read from ctx when set,
#     falling back to stored values for synthetic nodes.
#   • Each class documents the generated context class it is built from
#     and the visitXxx method name that constructs it.
#
# ANTLR4 context → AST node mapping
# ───────────────────────────────────
#  Parser rule          Generated context class              visitXxx method
#  ─────────────────    ─────────────────────────────────    ──────────────────────────
#  diagram              DiagramContext                        visitDiagram
#  participantDecl      ParticipantDeclContext                visitParticipantDecl
#  actorDecl            ActorDeclContext                      visitActorDecl
#  boxBlock             BoxBlockContext                       visitBoxBlock
#  createDirective      CreateDirectiveContext                visitCreateDirective
#  destroyDirective     DestroyDirectiveContext               visitDestroyDirective
#  messageStatement     MessageStatementContext               visitMessageStatement
#  activateStatement    ActivateStatementContext              visitActivateStatement
#  deactivateStatement  DeactivateStatementContext            visitDeactivateStatement
#  noteStatement        NoteStatementContext                  visitNoteStatement
#  autonumberStatement  AutonumberStatementContext            visitAutonumberStatement
#  loopBlock            LoopBlockContext                      visitLoopBlock
#  altBlock             AltBlockContext                       visitAltBlock
#  optBlock             OptBlockContext                       visitOptBlock
#  parBlock             ParBlockContext                       visitParBlock
#  criticalBlock        CriticalBlockContext                  visitCriticalBlock
#  breakBlock           BreakBlockContext                     visitBreakBlock
#  rectBlock            RectBlockContext                      visitRectBlock
#
# Helper sub-rule contexts (visited inline, not mapped to top-level AST nodes):
#  participantId        ParticipantIdContext      → str via .getText()
#  participantType      ParticipantTypeContext    → ParticipantKind enum
#  notePosition         NotePositionContext       → NotePosition enum
#  iconSpec / label     (inline text extraction)
#
# CONTEXT TEXT EXTRACTION PATTERN
# ────────────────────────────────
# In the generated visitor the standard pattern for reading a token value is:
#
#   ctx.participantId().getText().strip('"')   # strips quotes from QUOTED_STRING
#   ctx.ARROW().getText()                      # raw arrow string e.g. '->>'
#   ctx.messageText().getText().strip()        # free-form text after ':'
#
# The visitor helper _text(ctx) normalises quoted strings:
#   def _text(node) -> str:
#       t = node.getText()
#       return t[1:-1] if t.startswith('"') else t

"""
# ast_nodes.py
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional, List
from enum import Enum, auto


def make_id() -> str:
    return str(uuid.uuid4())


@dataclass
class ASTNode:
    node_id: str = field(default_factory=make_id)
    ctx:     Any = field(default=None, repr=False, compare=False)
    # ctx holds the originating MermaidSequenceParser.*Context object.
    # Use ONLY in ast_visitor.py.  Typed as Any to avoid importing
    # generated parser code into downstream modules.

    @property
    def source_start(self) -> int:
        if self.ctx is not None:
            return self.ctx.start.tokenIndex
        return -1

    @property
    def source_stop(self) -> int:
        if self.ctx is not None:
            return self.ctx.stop.tokenIndex
        return -1


# ── Enumerations ──────────────────────────────────────────────────────────────

class ParticipantKind(Enum):
    PARTICIPANT = auto()
    ACTOR       = auto()
    BOUNDARY    = auto()
    CONTROL     = auto()
    ENTITY      = auto()
    DATABASE    = auto()
    COLLECTIONS = auto()
    QUEUE       = auto()

class ArrowStyle(Enum):
    SOLID_OPEN   = "->"
    DOTTED_OPEN  = "-->"
    SOLID_ARROW  = "->>"
    DOTTED_ARROW = "-->>"
    SOLID_CROSS  = "-x"
    DOTTED_CROSS = "--x"
    SOLID_ASYNC  = "-)"
    DOTTED_ASYNC = "--)"

class NotePosition(Enum):
    RIGHT_OF = auto()
    LEFT_OF  = auto()
    OVER     = auto()

# ── Core nodes ────────────────────────────────────────────────────────────────
# Built by: visitParticipantDecl, visitActorDecl, visitCreateDirective

@dataclass
class ParticipantNode(ASTNode):
    # ctx type: ParticipantDeclContext | ActorDeclContext | CreateDirectiveContext
    kind:              ParticipantKind = ParticipantKind.PARTICIPANT
    name:              str = ""
    label:             str = ""
    created_at_step:   Optional[int] = None
    destroyed_at_step: Optional[int] = None

# Built by: visitBoxBlock
@dataclass
class BoxNode(ASTNode):
    # ctx type: BoxBlockContext
    color:        Optional[str]         = None
    label:        Optional[str]         = None
    participants: List[ParticipantNode] = field(default_factory=list)

# Built by: visitMessageStatement
@dataclass
class MessageNode(ASTNode):
    # ctx type: MessageStatementContext
    step:          int        = 0
    sender_name:   str        = ""
    receiver_name: str        = ""
    arrow:         ArrowStyle = ArrowStyle.SOLID_ARROW
    activate:      bool       = False
    deactivate:    bool       = False
    central_src:   bool       = False
    central_dst:   bool       = False
    text:          str        = ""

# Built by: visitActivateStatement, visitDeactivateStatement
@dataclass
class ActivationNode(ASTNode):
    # ctx type: ActivateStatementContext | DeactivateStatementContext
    step:             int  = 0
    participant_name: str  = ""
    is_activate:      bool = True

# Built by: visitNoteStatement
@dataclass
class NoteNode(ASTNode):
    # ctx type: NoteStatementContext
    step:              int          = 0
    position:          NotePosition = NotePosition.RIGHT_OF
    participant_names: List[str]    = field(default_factory=list)
    text:              str          = ""

# Built by: visitAutonumberStatement
@dataclass
class AutonumberNode(ASTNode):
    # ctx type: AutonumberStatementContext
    start: Optional[int] = None
    step:  Optional[int] = None

# Built by: visitLoopBlock
@dataclass
class LoopNode(ASTNode):
    # ctx type: LoopBlockContext
    step:  int           = 0
    label: str           = ""
    body:  List[ASTNode] = field(default_factory=list)

# Built by: visitAltBlock  (branches[0] = alt clause, [1..] = else clauses)
@dataclass
class AltBranch(ASTNode):
    # ctx type: slice of AltBlockContext
    condition: str           = ""
    body:      List[ASTNode] = field(default_factory=list)

@dataclass
class AltNode(ASTNode):
    # ctx type: AltBlockContext
    step:     int             = 0
    branches: List[AltBranch] = field(default_factory=list)

# Built by: visitOptBlock
@dataclass
class OptNode(ASTNode):
    # ctx type: OptBlockContext
    step:      int           = 0
    condition: str           = ""
    body:      List[ASTNode] = field(default_factory=list)

# Built by: visitParBlock
@dataclass
class ParBranch(ASTNode):
    # ctx type: slice of ParBlockContext
    label: str           = ""
    body:  List[ASTNode] = field(default_factory=list)

@dataclass
class ParNode(ASTNode):
    # ctx type: ParBlockContext
    step:     int             = 0
    branches: List[ParBranch] = field(default_factory=list)

# Built by: visitCriticalBlock
@dataclass
class CriticalOption(ASTNode):
    condition: str           = ""
    body:      List[ASTNode] = field(default_factory=list)

@dataclass
class CriticalNode(ASTNode):
    # ctx type: CriticalBlockContext
    step:    int                  = 0
    action:  str                  = ""
    body:    List[ASTNode]        = field(default_factory=list)
    options: List[CriticalOption] = field(default_factory=list)

# Built by: visitBreakBlock
@dataclass
class BreakNode(ASTNode):
    # ctx type: BreakBlockContext
    step:      int           = 0
    condition: str           = ""
    body:      List[ASTNode] = field(default_factory=list)

# Built by: visitRectBlock
@dataclass
class RectNode(ASTNode):
    # ctx type: RectBlockContext
    step:  int           = 0
    color: str           = ""
    body:  List[ASTNode] = field(default_factory=list)

# Root — built by: visitDiagram
@dataclass
class DiagramNode(ASTNode):
    # ctx type: DiagramContext
    participants: List[ParticipantNode]    = field(default_factory=list)
    boxes:        List[BoxNode]            = field(default_factory=list)
    statements:   List[ASTNode]            = field(default_factory=list)
    autonumber:   Optional[AutonumberNode] = None
"""


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 3 — ANTLR4 VISITOR IMPLEMENTATION CONTRACT
# ──────────────────────────────────────────────────────────────────────────────
#
# FILE: ast_visitor.py
#
# This is NEW in v2.  The visitor is the bridge between the generated
# parser context tree and the hand-written AST dataclass tree.
#
# CLASS HIERARCHY
# ───────────────
#   MermaidSequenceVisitor          ← generated (do not edit)
#       └── ASTBuildingVisitor      ← hand-written (ast_visitor.py)
#
# VISITOR RULES
# ─────────────
#  1. Every visitXxx method returns an ASTNode subclass (or a list for helpers).
#  2. Store ctx on the returned node: node.ctx = ctx
#  3. Never store ctx on nodes that are not the primary result of that visit
#     (e.g. AltBranch nodes constructed inside visitAltBlock get their own ctx
#     set to None because there is no single sub-context for a branch).
#  4. Call self.visitChildren(ctx) only for nodes whose body is a list of
#     heterogeneous statements; use the specific visitXxx for typed children.
#  5. The step counter is maintained as self._step: int, incremented once per
#     MessageNode, ActivationNode, NoteNode, and fragment-opening node.
#  6. Quote stripping: use the module-level helper _strip(text) -> str which
#     removes surrounding double-quotes if present.
#
# ENTRY POINT
# ───────────
#   def parse_diagram(source: str) -> DiagramNode:
#       input_stream  = antlr4.InputStream(source)
#       lexer         = MermaidSequenceLexer(input_stream)
#       token_stream  = antlr4.CommonTokenStream(lexer)
#       parser        = MermaidSequenceParser(token_stream)
#       tree          = parser.diagram()          # root rule
#       visitor       = ASTBuildingVisitor()
#       return visitor.visit(tree)               # returns DiagramNode

"""
# ast_visitor.py  (contract / skeleton — Claude Code fills in the bodies)

import antlr4
from MermaidSequenceLexer   import MermaidSequenceLexer
from MermaidSequenceParser  import MermaidSequenceParser
from MermaidSequenceVisitor import MermaidSequenceVisitor
from ast_nodes import (
    DiagramNode, ParticipantNode, ParticipantKind, BoxNode,
    MessageNode, ArrowStyle, ActivationNode, NoteNode, NotePosition,
    AutonumberNode, LoopNode, AltNode, AltBranch, OptNode,
    ParNode, ParBranch, CriticalNode, CriticalOption,
    BreakNode, RectNode, ASTNode,
)


def _strip(text: str) -> str:
    return text[1:-1] if len(text) >= 2 and text[0] == '"' else text


def parse_diagram(source: str) -> DiagramNode:
    input_stream = antlr4.InputStream(source)
    lexer        = MermaidSequenceLexer(input_stream)
    tokens       = antlr4.CommonTokenStream(lexer)
    parser       = MermaidSequenceParser(tokens)
    tree         = parser.diagram()
    return ASTBuildingVisitor().visit(tree)


class ASTBuildingVisitor(MermaidSequenceVisitor):

    def __init__(self):
        self._step = 0          # monotonic counter across all ordered statements

    # ── Root ─────────────────────────────────────────────────────────────────

    def visitDiagram(self, ctx: MermaidSequenceParser.DiagramContext) -> DiagramNode:
        ...  # Claude Code implements: collect participants, boxes, statements

    # ── Participants ──────────────────────────────────────────────────────────

    def visitParticipantDecl(self, ctx) -> ParticipantNode:
        ...  # read participantType → ParticipantKind, participantId, optional AS label

    def visitActorDecl(self, ctx) -> ParticipantNode:
        ...  # always kind=ACTOR

    def visitCreateDirective(self, ctx) -> ParticipantNode:
        ...  # same as participantDecl but sets created_at_step = self._step

    def visitDestroyDirective(self, ctx) -> str:
        ...  # returns the participant name string; caller sets destroyed_at_step

    # ── Box ───────────────────────────────────────────────────────────────────

    def visitBoxBlock(self, ctx) -> BoxNode:
        ...  # optional color, optional label, then visit inner participant decls

    # ── Messages ──────────────────────────────────────────────────────────────

    def visitMessageStatement(self, ctx) -> MessageNode:
        ...  # parse sender/receiver (check LPAREN for central_src/dst),
             # ARROW token → ArrowStyle + activate/deactivate bools,
             # messageText, then increment self._step

    # ── Activate / Deactivate ─────────────────────────────────────────────────

    def visitActivateStatement(self, ctx) -> ActivationNode:
        ...

    def visitDeactivateStatement(self, ctx) -> ActivationNode:
        ...  # is_activate=False

    # ── Notes ─────────────────────────────────────────────────────────────────

    def visitNoteStatement(self, ctx) -> NoteNode:
        ...  # notePosition → NotePosition enum, 1 or 2 participant names

    # ── Autonumber ────────────────────────────────────────────────────────────

    def visitAutonumberStatement(self, ctx) -> AutonumberNode:
        ...

    # ── Control structures ────────────────────────────────────────────────────

    def visitLoopBlock(self, ctx) -> LoopNode:
        ...

    def visitAltBlock(self, ctx) -> AltNode:
        ...  # build one AltBranch per alt/else clause

    def visitOptBlock(self, ctx) -> OptNode:
        ...

    def visitParBlock(self, ctx) -> ParNode:
        ...

    def visitCriticalBlock(self, ctx) -> CriticalNode:
        ...

    def visitBreakBlock(self, ctx) -> BreakNode:
        ...

    def visitRectBlock(self, ctx) -> RectNode:
        ...

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _participant_kind(self, ctx) -> ParticipantKind:
        ...  # map participantType context token to ParticipantKind enum

    def _arrow_style(self, arrow_text: str) -> tuple[ArrowStyle, bool, bool]:
        ...  # returns (ArrowStyle, activate_flag, deactivate_flag)
             # activate_flag  = arrow_text ends with '+'
             # deactivate_flag= arrow_text ends with '-'

    def _visit_body(self, ctx) -> list:
        ...  # visit each statement() child and collect returned ASTNode objects
"""


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 4 — SVG ATTRIBUTE / data- CONVENTIONS
# ──────────────────────────────────────────────────────────────────────────────
# (unchanged from v1 — reproduced here for completeness)
#
# PRIMARY <g> attributes
# ──────────────────────
#   id              "ast-{node_id}"
#   data-ast-type   see mapping table in Section 5
#   data-ast-ref    "{node_id}"    (inherited by descendants via DOM walk-up)
#   data-step       str(int)       on MessageNode and all fragment nodes
#
# SUB-ELEMENT attributes
# ──────────────────────
#   data-role       identifies the visual part within the group
#   data-branch     int string     on branch-divider / branch-label elements


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 5 — GRAMMAR ELEMENT → SVG MAPPING TABLE
# ──────────────────────────────────────────────────────────────────────────────
# (unchanged from v1)
#
# ┌─────────────────────────┬──────────────────┬─────────────────┬──────────────────────────────────────────────────────────────────┐
# │ Grammar Element         │ AST Class        │ data-ast-type   │ data-role sub-elements                                           │
# ├─────────────────────────┼──────────────────┼─────────────────┼──────────────────────────────────────────────────────────────────┤
# │ participant / actor /   │ ParticipantNode  │ participant      │ header  header-box  header-label                                 │
# │ boundary / control /    │                  │                 │ lifeline                                                         │
# │ entity / database /     │                  │                 │ footer  footer-box  footer-label                                 │
# │ collections / queue     │                  │                 │ destroy-marker  (only when destroyed_at_step set)                │
# ├─────────────────────────┼──────────────────┼─────────────────┼──────────────────────────────────────────────────────────────────┤
# │ box … end               │ BoxNode          │ box             │ background  label                                                │
# ├─────────────────────────┼──────────────────┼─────────────────┼──────────────────────────────────────────────────────────────────┤
# │ A->>B: text  (all arrow │ MessageNode      │ message         │ shaft  arrowhead  label  seqnum(conditional)                     │
# │ variants)               │                  │                 │                                                                  │
# ├─────────────────────────┼──────────────────┼─────────────────┼──────────────────────────────────────────────────────────────────┤
# │ activate / deactivate   │ ActivationNode   │ activation      │ bar                                                              │
# ├─────────────────────────┼──────────────────┼─────────────────┼──────────────────────────────────────────────────────────────────┤
# │ Note right/left/over    │ NoteNode         │ note            │ box  text                                                        │
# ├─────────────────────────┼──────────────────┼─────────────────┼──────────────────────────────────────────────────────────────────┤
# │ loop … end              │ LoopNode         │ loop            │ frame  label-box  kind-text  cond-text                           │
# ├─────────────────────────┼──────────────────┼─────────────────┼──────────────────────────────────────────────────────────────────┤
# │ alt … else … end        │ AltNode          │ alt             │ frame  label-box  kind-text  cond-text                           │
# │                         │                  │                 │ branch-divider(×N-1)  branch-label(×N-1)                        │
# ├─────────────────────────┼──────────────────┼─────────────────┼──────────────────────────────────────────────────────────────────┤
# │ opt … end               │ OptNode          │ opt             │ frame  label-box  kind-text  cond-text                           │
# ├─────────────────────────┼──────────────────┼─────────────────┼──────────────────────────────────────────────────────────────────┤
# │ par … and … end         │ ParNode          │ par             │ frame  label-box  kind-text                                      │
# │                         │                  │                 │ branch-divider(×N-1)  branch-label(×N-1)                        │
# ├─────────────────────────┼──────────────────┼─────────────────┼──────────────────────────────────────────────────────────────────┤
# │ critical … option … end │ CriticalNode     │ critical        │ frame  label-box  kind-text  cond-text                           │
# │                         │                  │                 │ branch-divider(×N)  branch-label(×N)                            │
# ├─────────────────────────┼──────────────────┼─────────────────┼──────────────────────────────────────────────────────────────────┤
# │ break … end             │ BreakNode        │ break           │ frame  label-box  kind-text  cond-text                           │
# ├─────────────────────────┼──────────────────┼─────────────────┼──────────────────────────────────────────────────────────────────┤
# │ rect color … end        │ RectNode         │ rect            │ background                                                       │
# └─────────────────────────┴──────────────────┴─────────────────┴──────────────────────────────────────────────────────────────────┘
#
# data-role vocabulary (exhaustive)
# ──────────────────────────────────
#   header           <g>     top lifeline box wrapper
#   header-box       <rect>  top box shape
#   header-label     <text>  top box text
#   lifeline         <line>  dashed vertical line
#   footer           <g>     bottom lifeline box wrapper
#   footer-box       <rect>  bottom box shape
#   footer-label     <text>  bottom box text
#   destroy-marker   <path>  X at destroyed_at_step y-coord
#   background       <rect>  box/rect block fill
#   label            <text>  box block header label; also message label text
#   shaft            <line>  horizontal message arrow line
#   arrowhead        <path>  arrowhead / cross / open-arrow glyph
#   seqnum           <g>     autonumber badge (circle + text)
#   bar              <rect>  activation box on lifeline
#   box              <rect>  note background
#   text             <text>  note text
#   frame            <rect>  fragment outer border
#   label-box        <rect>  fragment keyword badge (top-left)
#   kind-text        <text>  keyword inside label-box
#   cond-text        <text>  condition/label beside label-box
#   branch-divider   <line>  horizontal line between branches
#   branch-label     <text>  condition at start of else/and/option branch


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 6 — LAYOUT MODEL  (unchanged from v1)
# ──────────────────────────────────────────────────────────────────────────────
#
# FILE: layout_model.py

"""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ParticipantLayout:
    node_id:     str
    col:         int
    center_x:    float
    top_box_y:   float
    top_box_h:   float
    lifeline_y1: float
    lifeline_y2: float
    bot_box_y:   float
    bot_box_h:   float

@dataclass
class MessageLayout:
    node_id: str
    step:    int
    y:       float
    x1:      float
    x2:      float

@dataclass
class ActivationLayout:
    node_id:             str
    participant_node_id: str
    y_top:               float
    y_bottom:            float
    x:                   float
    width:               float = 10.0

@dataclass
class NoteLayout:
    node_id: str
    x:       float
    y:       float
    width:   float
    height:  float

@dataclass
class FragmentLayout:
    node_id:   str
    y_top:     float
    y_bottom:  float
    x_left:    float
    x_right:   float
    branch_ys: List[float] = field(default_factory=list)

@dataclass
class LayoutModel:
    participants: Dict[str, ParticipantLayout] = field(default_factory=dict)
    messages:     Dict[str, MessageLayout]     = field(default_factory=dict)
    activations:  Dict[str, ActivationLayout]  = field(default_factory=dict)
    notes:        Dict[str, NoteLayout]        = field(default_factory=dict)
    fragments:    Dict[str, FragmentLayout]    = field(default_factory=dict)
"""


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 7 — SVGNodeRegistry API CONTRACT
# ──────────────────────────────────────────────────────────────────────────────
#
# FILE: svg_node_registry.py
#
# Changes from v1:
#   • SVGNodeEntry gains  ctx_type: str  — the generated context class name
#     (e.g. "ParticipantDeclContext") stored as a plain string so downstream
#     code never imports generated parser modules.
#   • No other changes to the registry API.
#
# INTERNAL INDEXES (all O(1) lookup)
# ───────────────────────────────────
#   _by_node_id   : Dict[str, SVGNodeEntry]
#   _by_svg_id    : Dict[str, SVGNodeEntry]        keyed "ast-{node_id}"
#   _by_ast_type  : Dict[str, List[SVGNodeEntry]]  keyed data-ast-type string
#   _by_step      : Dict[int,  SVGNodeEntry]        messages + fragments only
#
# SVGNodeEntry FIELDS
# ───────────────────
#   node_id       str
#   ast_node      ASTNode
#   svg_group     Element
#   ast_type      str
#   ctx_type      str        generated context class name (informational)
#   sub_elements  Dict[str, List[Element]]   keyed by data-role

"""
# svg_node_registry.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from xml.etree.ElementTree import Element
from ast_nodes import ASTNode


@dataclass
class SVGNodeEntry:
    node_id:      str
    ast_node:     ASTNode
    svg_group:    Element
    ast_type:     str
    ctx_type:     str = ""          # e.g. "ParticipantDeclContext"
    sub_elements: Dict[str, List[Element]] = field(default_factory=dict)


class SVGNodeRegistry:

    def __init__(self):
        self._by_node_id:  Dict[str, SVGNodeEntry]       = {}
        self._by_svg_id:   Dict[str, SVGNodeEntry]       = {}
        self._by_ast_type: Dict[str, List[SVGNodeEntry]] = {}
        self._by_step:     Dict[int,  SVGNodeEntry]       = {}

    # ── Registration ──────────────────────────────────────────────────────────

    def register(self,
                 ast_node:  ASTNode,
                 svg_group: Element,
                 ast_type:  str,
                 ctx_type:  str = "") -> SVGNodeEntry:
        entry = SVGNodeEntry(
            node_id   = ast_node.node_id,
            ast_node  = ast_node,
            svg_group = svg_group,
            ast_type  = ast_type,
            ctx_type  = ctx_type or type(ast_node.ctx).__name__,
        )
        self._index_sub_elements(entry)
        self._by_node_id[ast_node.node_id]          = entry
        self._by_svg_id[f"ast-{ast_node.node_id}"]  = entry
        self._by_ast_type.setdefault(ast_type, []).append(entry)
        step = getattr(ast_node, "step", None)
        if step is not None:
            self._by_step[step] = entry
        return entry

    def invalidate(self, node_id: str) -> None:
        entry = self._by_node_id.pop(node_id, None)
        if entry is None:
            return
        self._by_svg_id.pop(f"ast-{node_id}", None)
        bucket = self._by_ast_type.get(entry.ast_type, [])
        self._by_ast_type[entry.ast_type] = [e for e in bucket
                                              if e.node_id != node_id]
        step = getattr(entry.ast_node, "step", None)
        if step is not None and self._by_step.get(step) is entry:
            self._by_step.pop(step, None)

    def update_sub_elements(self, node_id: str) -> None:
        entry = self._by_node_id.get(node_id)
        if entry:
            entry.sub_elements.clear()
            self._index_sub_elements(entry)

    def _index_sub_elements(self, entry: SVGNodeEntry) -> None:
        for elem in entry.svg_group.iter():
            role = elem.get("data-role")
            if role:
                entry.sub_elements.setdefault(role, []).append(elem)

    # ── Forward lookups (AST → SVG) ───────────────────────────────────────────

    def svg_group_for(self, node_id: str) -> Optional[Element]:
        e = self._by_node_id.get(node_id)
        return e.svg_group if e else None

    def svg_subelement(self, node_id: str, role: str) -> Optional[Element]:
        e = self._by_node_id.get(node_id)
        if e:
            elems = e.sub_elements.get(role, [])
            return elems[0] if elems else None
        return None

    def svg_subelements(self, node_id: str, role: str) -> List[Element]:
        e = self._by_node_id.get(node_id)
        return e.sub_elements.get(role, []) if e else []

    def all_of_type(self, ast_type: str) -> List[SVGNodeEntry]:
        return list(self._by_ast_type.get(ast_type, []))

    def entry_for_step(self, step: int) -> Optional[SVGNodeEntry]:
        return self._by_step.get(step)

    # ── Reverse lookups (SVG → AST) ───────────────────────────────────────────

    def ast_node_for_svg_id(self, svg_id: str) -> Optional[ASTNode]:
        e = self._by_svg_id.get(svg_id)
        return e.ast_node if e else None

    def ast_node_for_element(self, element: Element) -> Optional[ASTNode]:
        ref = element.get("data-ast-ref")
        if ref:
            e = self._by_node_id.get(ref)
            return e.ast_node if e else None
        return None
"""


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 8 — USAGE EXAMPLES
# ──────────────────────────────────────────────────────────────────────────────

# ── Parse + build AST ─────────────────────────────────────────────────────────
"""
from ast_visitor import parse_diagram

source = '''
sequenceDiagram
    participant Alice
    participant Bob
    Alice->>Bob: Hello
    Bob-->>Alice: Hi back
'''
diagram = parse_diagram(source)
# diagram.participants[0].name  → "Alice"
# diagram.participants[0].ctx   → ParticipantDeclContext object
# diagram.participants[0].source_start → token index from ctx
"""

# ── Parse error: access originating token via ctx ────────────────────────────
"""
msg_node = diagram.statements[0]          # MessageNode
if msg_node.ctx is not None:
    tok = msg_node.ctx.start              # antlr4.Token
    print(f"Line {tok.line}, col {tok.column}: {msg_node.sender_name}")
"""

# ── Render and populate registry ─────────────────────────────────────────────
"""
from layout_engine import LayoutEngine
from svg_renderer  import SequenceDiagramRenderer

layout          = LayoutEngine(diagram).compute()
svg_root, registry = SequenceDiagramRenderer(diagram, layout).render()
"""

# ── Forward: AST → SVG ───────────────────────────────────────────────────────
"""
alice    = next(p for p in diagram.participants if p.name == "Alice")
lifeline = registry.svg_subelement(alice.node_id, "lifeline")
lifeline.set("stroke", "red")
"""

# ── Reverse: SVG → AST (PyQt QWebEngineView click) ───────────────────────────
"""
def on_element_clicked(self, svg_id: str):
    node = self.registry.ast_node_for_svg_id(svg_id)
    match node:
        case MessageNode():    self.props.show_message(node)
        case ParticipantNode():self.props.show_participant(node)
        case LoopNode():       self.props.show_fragment(node)
"""

# ── ctx_type for diagnostics ─────────────────────────────────────────────────
"""
for entry in registry.all_of_type("participant"):
    print(entry.ctx_type, entry.ast_node.name)
# ParticipantDeclContext Alice
# ParticipantDeclContext Bob
"""