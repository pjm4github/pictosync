# SVGNodeRegistry — Specification
# Mermaid Sequence Diagram Renderer
# ============================================================
# This file is the single source of truth consumed by the
# SVGNodeRegistry implementation.  It defines:
#
#   1. The AST node class hierarchy (Python dataclasses)
#   2. The SVG attribute / data- conventions
#   3. The complete grammar-element → SVG group mapping
#   4. The SVGNodeRegistry API contract
#   5. The LayoutModel contract
#   6. Worked usage examples
#
# Target language : Python 3.11+
# SVG library     : xml.etree.ElementTree (stdlib)
# ANTLR4 runtime  : antlr4-python3-runtime
# PyQt version    : PyQt6
# ============================================================


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 1 — PIPELINE OVERVIEW
# ──────────────────────────────────────────────────────────────────────────────
#
#  Source text  (mermaid sequenceDiagram string)
#       │
#       ▼  Stage 1 — ANTLR4 parse
#  Parse Tree   (MermaidSequenceParser context objects)
#       │
#       ▼  Stage 2 — Visitor → AST construction
#  AST          (Python dataclasses defined in Section 2)
#       │
#       ▼  Stage 3 — Layout engine
#  LayoutModel  (pixel geometry, defined in Section 4)
#       │
#       ▼  Stage 4 — SVG renderer
#  SVG DOM      (xml.etree.ElementTree; groups carry data- attributes)
#       │
#       ▼  Stage 5 — Registry population (happens during Stage 4)
#  SVGNodeRegistry  (bidirectional index, defined in Section 5)


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 2 — AST NODE HIERARCHY
# ──────────────────────────────────────────────────────────────────────────────
#
# FILE: ast_nodes.py
#
# Rules:
#   • Every node inherits ASTNode.
#   • node_id is a UUID string assigned at construction and NEVER changed.
#   • source_start / source_stop are the ANTLR4 token interval indices
#     (set by the visitor; default -1 means "synthetic / not from source").
#   • All list fields default to empty list via field(default_factory=list).

"""
import uuid
from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum, auto


def make_id() -> str:
    return str(uuid.uuid4())


@dataclass
class ASTNode:
    node_id:      str = field(default_factory=make_id)
    source_start: int = -1
    source_stop:  int = -1


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
    SOLID_OPEN   = "->"    # solid line, no arrowhead
    DOTTED_OPEN  = "-->"   # dotted line, no arrowhead
    SOLID_ARROW  = "->>"   # solid line, filled arrowhead
    DOTTED_ARROW = "-->>"  # dotted line, filled arrowhead
    SOLID_CROSS  = "-x"    # solid line, cross terminus
    DOTTED_CROSS = "--x"   # dotted line, cross terminus
    SOLID_ASYNC  = "-)"    # solid line, open async arrow
    DOTTED_ASYNC = "--)"   # dotted line, open async arrow

class NotePosition(Enum):
    RIGHT_OF = auto()
    LEFT_OF  = auto()
    OVER     = auto()

# ── Core leaf nodes ───────────────────────────────────────────────────────────

@dataclass
class ParticipantNode(ASTNode):
    kind:              ParticipantKind = ParticipantKind.PARTICIPANT
    name:              str = ""          # internal identifier (used in message refs)
    label:             str = ""          # display label / alias
    created_at_step:   Optional[int] = None   # set when 'create' directive precedes first message
    destroyed_at_step: Optional[int] = None   # set when 'destroy' directive fires

@dataclass
class BoxNode(ASTNode):
    color:        Optional[str]         = None
    label:        Optional[str]         = None
    participants: List[ParticipantNode] = field(default_factory=list)

@dataclass
class MessageNode(ASTNode):
    step:          int        = 0
    sender_name:   str        = ""
    receiver_name: str        = ""
    arrow:         ArrowStyle = ArrowStyle.SOLID_ARROW
    activate:      bool       = False   # '+' suffix activates receiver
    deactivate:    bool       = False   # '-' suffix deactivates receiver
    central_src:   bool       = False   # sender uses () central-connection syntax
    central_dst:   bool       = False   # receiver uses () central-connection syntax
    text:          str        = ""

@dataclass
class ActivationNode(ASTNode):
    step:             int  = 0
    participant_name: str  = ""
    is_activate:      bool = True   # False → deactivate statement

@dataclass
class NoteNode(ASTNode):
    step:              int          = 0
    position:          NotePosition = NotePosition.RIGHT_OF
    participant_names: List[str]    = field(default_factory=list)   # 1 or 2 names
    text:              str          = ""

@dataclass
class AutonumberNode(ASTNode):
    start: Optional[int] = None
    step:  Optional[int] = None

# ── Control-structure nodes (all have a body list of child statements) ─────────

@dataclass
class LoopNode(ASTNode):
    step:  int           = 0
    label: str           = ""
    body:  List[ASTNode] = field(default_factory=list)

@dataclass
class AltBranch(ASTNode):
    """One branch of an alt/else block."""
    condition: str           = ""
    body:      List[ASTNode] = field(default_factory=list)

@dataclass
class AltNode(ASTNode):
    step:     int             = 0
    branches: List[AltBranch] = field(default_factory=list)  # [0]=alt, [1..]=else

@dataclass
class OptNode(ASTNode):
    step:      int           = 0
    condition: str           = ""
    body:      List[ASTNode] = field(default_factory=list)

@dataclass
class ParBranch(ASTNode):
    """One branch of a par/and block."""
    label: str           = ""
    body:  List[ASTNode] = field(default_factory=list)

@dataclass
class ParNode(ASTNode):
    step:     int             = 0
    branches: List[ParBranch] = field(default_factory=list)

@dataclass
class CriticalOption(ASTNode):
    condition: str           = ""
    body:      List[ASTNode] = field(default_factory=list)

@dataclass
class CriticalNode(ASTNode):
    step:    int                  = 0
    action:  str                  = ""
    body:    List[ASTNode]        = field(default_factory=list)
    options: List[CriticalOption] = field(default_factory=list)

@dataclass
class BreakNode(ASTNode):
    step:      int           = 0
    condition: str           = ""
    body:      List[ASTNode] = field(default_factory=list)

@dataclass
class RectNode(ASTNode):
    step:  int           = 0
    color: str           = ""
    body:  List[ASTNode] = field(default_factory=list)

# ── Root ─────────────────────────────────────────────────────────────────────

@dataclass
class DiagramNode(ASTNode):
    participants: List[ParticipantNode]    = field(default_factory=list)
    boxes:        List[BoxNode]            = field(default_factory=list)
    statements:   List[ASTNode]            = field(default_factory=list)
    autonumber:   Optional[AutonumberNode] = None
"""


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 3 — SVG ATTRIBUTE CONVENTIONS
# ──────────────────────────────────────────────────────────────────────────────
#
# Every logical AST node is rendered as a PRIMARY <g> element.
# Child SVG primitives live inside that group.
#
# PRIMARY <g> attributes
# ──────────────────────
#   id              "ast-{node_id}"          CSS/JS/PyQt addressable primary key
#   data-ast-type   string (see table below) node kind for type-based queries
#   data-ast-ref    "{node_id}"              back-pointer to AST; inherited by
#                                            all descendants via DOM walk-up
#   data-step       integer string           sequence order (messages, fragments)
#
# SUB-ELEMENT attributes (on children inside the primary <g>)
# ───────────────────────────────────────────────────────────
#   data-role       string  identifies the visual part within the group
#                           (see mapping table in Section 4)
#   data-branch     integer branch index within alt / par / critical groups
#
# SVG TREE SHAPE
# ──────────────
# Fragment body children (loop body, alt branches, etc.) are rendered as
# nested <g> elements INSIDE the fragment's primary <g>.  This mirrors
# the AST containment and gives correct z-ordering automatically.
#
# EXAMPLE — participant
# ─────────────────────
#   <g id="ast-{node_id}"
#      data-ast-type="participant"
#      data-ast-ref="{node_id}"
#      data-participant-name="Alice">
#
#     <g data-role="header">
#       <rect  data-role="header-box"   x=… y=… width=… height=… rx="6"/>
#       <text  data-role="header-label" x=… y=…>Alice</text>
#     </g>
#
#     <line  data-role="lifeline"
#            x1="{cx}" y1="{y1}" x2="{cx}" y2="{y2}"
#            stroke-dasharray="6,3"/>
#
#     <g data-role="footer">
#       <rect  data-role="footer-box"   x=… y=… width=… height=… rx="6"/>
#       <text  data-role="footer-label" x=… y=…>Alice</text>
#     </g>
#   </g>
#
# EXAMPLE — message
# ─────────────────
#   <g id="ast-{node_id}"
#      data-ast-type="message"
#      data-ast-ref="{node_id}"
#      data-step="3"
#      data-sender="Alice"
#      data-receiver="Bob">
#
#     <line  data-role="shaft"     x1=… y1=… x2=… y2=…/>
#     <path  data-role="arrowhead" marker-end="url(#arrow-solid-filled)"/>
#     <text  data-role="label"     x=… y=…>Login request</text>
#     <g     data-role="seqnum">        <!-- only when autonumber active -->
#       <circle cx=… cy=… r="10"/>
#       <text   x=… y=…>3</text>
#     </g>
#   </g>
#
# EXAMPLE — loop fragment
# ───────────────────────
#   <g id="ast-{node_id}"
#      data-ast-type="loop"
#      data-ast-ref="{node_id}"
#      data-step="5">
#
#     <rect  data-role="frame"     x=… y=… width=… height=…/>
#     <rect  data-role="label-box" x=… y=… width="40" height="18"/>
#     <text  data-role="kind-text" x=… y=…>loop</text>
#     <text  data-role="cond-text" x=… y=…>Retry up to 3 times</text>
#
#     <!-- body children nested here -->
#     <g id="ast-{child_id}" data-ast-type="message" …> … </g>
#   </g>
#
# EXAMPLE — alt fragment
# ──────────────────────
#   <g id="ast-{node_id}" data-ast-type="alt" …>
#     <rect  data-role="frame"     …/>
#     <rect  data-role="label-box" …/>
#     <text  data-role="kind-text" …>alt</text>
#     <text  data-role="cond-text" …>is sick</text>
#     <!-- branch-0 body children -->
#     <line  data-role="branch-divider" data-branch="1" …/>
#     <text  data-role="branch-label"   data-branch="1" …>else is well</text>
#     <!-- branch-1 body children -->
#   </g>


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 4 — GRAMMAR ELEMENT → SVG MAPPING TABLE
# ──────────────────────────────────────────────────────────────────────────────
#
# This is the authoritative lookup table used when building and querying the
# SVGNodeRegistry.  Every row maps one grammar construct to its AST class,
# its data-ast-type string, and the exhaustive set of data-role sub-elements
# the renderer will emit inside the primary <g>.
#
# ┌─────────────────────────┬──────────────────┬─────────────────┬────────────────────────────────────────────────────────────────────────────────────────┐
# │ Grammar Element         │ AST Class        │ data-ast-type   │ data-role sub-elements (in emission order)                                             │
# ├─────────────────────────┼──────────────────┼─────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
# │ participant / actor /   │ ParticipantNode  │ participant      │ header  header-box  header-label                                                       │
# │ boundary / control /    │                  │                 │ lifeline                                                                               │
# │ entity / database /     │                  │                 │ footer  footer-box  footer-label                                                       │
# │ collections / queue     │                  │                 │ destroy-marker  (only when destroyed_at_step is set)                                   │
# ├─────────────────────────┼──────────────────┼─────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
# │ box … end               │ BoxNode          │ box             │ background  label                                                                      │
# ├─────────────────────────┼──────────────────┼─────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
# │ A -> B: text            │ MessageNode      │ message         │ shaft  arrowhead  label                                                                │
# │ A --> B: text           │                  │                 │ seqnum  (only when autonumber active)                                                  │
# │ A ->> B: text           │                  │                 │                                                                                        │
# │ A -->> B: text          │                  │                 │                                                                                        │
# │ A -x B: text            │                  │                 │                                                                                        │
# │ A --x B: text           │                  │                 │                                                                                        │
# │ A -) B: text            │                  │                 │                                                                                        │
# │ A --) B: text           │                  │                 │                                                                                        │
# ├─────────────────────────┼──────────────────┼─────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
# │ activate A              │ ActivationNode   │ activation      │ bar                                                                                    │
# │ deactivate A            │ (is_activate=F)  │                 │                                                                                        │
# │ A->>+B: text  (+suffix) │                  │                 │                                                                                        │
# │ A->>-B: text  (-suffix) │                  │                 │                                                                                        │
# ├─────────────────────────┼──────────────────┼─────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
# │ Note right of A: txt    │ NoteNode         │ note            │ box  text                                                                              │
# │ Note left of A: txt     │                  │                 │                                                                                        │
# │ Note over A,B: txt      │                  │                 │                                                                                        │
# ├─────────────────────────┼──────────────────┼─────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
# │ loop label … end        │ LoopNode         │ loop            │ frame  label-box  kind-text  cond-text                                                 │
# ├─────────────────────────┼──────────────────┼─────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
# │ alt cond … else … end   │ AltNode          │ alt             │ frame  label-box  kind-text  cond-text                                                 │
# │                         │ → AltBranch[]    │                 │ branch-divider(×N-1)  branch-label(×N-1)                                              │
# ├─────────────────────────┼──────────────────┼─────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
# │ opt cond … end          │ OptNode          │ opt             │ frame  label-box  kind-text  cond-text                                                 │
# ├─────────────────────────┼──────────────────┼─────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
# │ par label … and … end   │ ParNode          │ par             │ frame  label-box  kind-text                                                            │
# │                         │ → ParBranch[]    │                 │ branch-divider(×N-1)  branch-label(×N-1)                                              │
# ├─────────────────────────┼──────────────────┼─────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
# │ critical act …          │ CriticalNode     │ critical        │ frame  label-box  kind-text  cond-text                                                 │
# │   option cond … end     │ → CriticalOption │                 │ branch-divider(×N options)  branch-label(×N options)                                  │
# ├─────────────────────────┼──────────────────┼─────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
# │ break cond … end        │ BreakNode        │ break           │ frame  label-box  kind-text  cond-text                                                 │
# ├─────────────────────────┼──────────────────┼─────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
# │ rect color … end        │ RectNode         │ rect            │ background                                                                             │
# ├─────────────────────────┼──────────────────┼─────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
# │ create participant A    │ ParticipantNode  │ participant      │ same as participant row above; created_at_step is non-None                             │
# ├─────────────────────────┼──────────────────┼─────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
# │ destroy A               │ ParticipantNode  │ participant      │ same as participant row above; destroy-marker role element added at destroyed_at_step  │
# └─────────────────────────┴──────────────────┴─────────────────┴────────────────────────────────────────────────────────────────────────────────────────┘
#
# data-role vocabulary (exhaustive list)
# ──────────────────────────────────────
#   header           <g>    wrapper group for top lifeline box
#   header-box       <rect> top box shape
#   header-label     <text> text inside top box
#   lifeline         <line> dashed vertical line
#   footer           <g>    wrapper group for bottom lifeline box
#   footer-box       <rect> bottom box shape (mirror of header)
#   footer-label     <text> text inside bottom box
#   destroy-marker   <path> X marker drawn at destroyed_at_step y-coord
#   background       <rect> filled rectangle for box or rect blocks
#   label            <text> display label for box block header; also message label
#   shaft            <line> horizontal line of a message arrow
#   arrowhead        <path> arrowhead / cross / open-arrow glyph
#   seqnum           <g>    sequence number badge (circle + text)
#   bar              <rect> activation box on a lifeline
#   box              <rect> note background rectangle
#   text             <text> note text content
#   frame            <rect> outer border of a fragment (loop/alt/par/etc.)
#   label-box        <rect> small filled rectangle in top-left of frame
#   kind-text        <text> keyword inside label-box (loop / alt / par / etc.)
#   cond-text        <text> condition/label text beside label-box
#   branch-divider   <line> horizontal dividing line between branches
#   branch-label     <text> condition text at start of an else/and/option branch


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 5 — LAYOUT MODEL CONTRACT
# ──────────────────────────────────────────────────────────────────────────────
#
# FILE: layout_model.py
#
# The layout engine populates a LayoutModel before rendering.
# Every entry is keyed by the AST node's node_id.

"""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ParticipantLayout:
    node_id:     str
    col:         int     # 0-based column index
    center_x:    float   # SVG x of the lifeline centerline
    top_box_y:   float   # top edge of header box
    top_box_h:   float   # height of header box
    lifeline_y1: float   # top of lifeline segment
    lifeline_y2: float   # bottom of lifeline segment (grows with diagram)
    bot_box_y:   float   # top edge of footer box
    bot_box_h:   float   # height of footer box


@dataclass
class MessageLayout:
    node_id: str
    step:    int
    y:       float   # vertical midpoint of the arrow
    x1:      float   # x at sender lifeline
    x2:      float   # x at receiver lifeline


@dataclass
class ActivationLayout:
    node_id:             str
    participant_node_id: str
    y_top:               float
    y_bottom:            float
    x:                   float   # left edge of bar
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
    \"\"\"Covers loop, alt, opt, par, critical, break, rect.\"\"\"
    node_id:   str
    y_top:     float
    y_bottom:  float
    x_left:    float
    x_right:   float
    branch_ys: List[float] = field(default_factory=list)
    # branch_ys[i] is the y of the dividing line before branch i+1


@dataclass
class LayoutModel:
    participants: Dict[str, ParticipantLayout] = field(default_factory=dict)
    messages:     Dict[str, MessageLayout]     = field(default_factory=dict)
    activations:  Dict[str, ActivationLayout]  = field(default_factory=dict)
    notes:        Dict[str, NoteLayout]        = field(default_factory=dict)
    fragments:    Dict[str, FragmentLayout]    = field(default_factory=dict)
"""


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 6 — SVGNodeRegistry API CONTRACT
# ──────────────────────────────────────────────────────────────────────────────
#
# FILE: svg_node_registry.py
#
# The registry is populated incrementally by the renderer as each primary <g>
# is emitted.  It maintains four O(1) indexes.
#
# INTERNAL INDEXES
# ────────────────
#   _by_node_id   : Dict[str, SVGNodeEntry]        keyed by node_id (UUID)
#   _by_svg_id    : Dict[str, SVGNodeEntry]         keyed by "ast-{node_id}"
#   _by_ast_type  : Dict[str, List[SVGNodeEntry]]   keyed by data-ast-type string
#   _by_step      : Dict[int, SVGNodeEntry]         keyed by step int (messages only)
#
# SVGNodeEntry FIELDS
# ───────────────────
#   node_id       str                    mirrors ast_node.node_id
#   ast_node      ASTNode                live reference to the AST node object
#   svg_group     Element                live reference to the primary <g>
#   ast_type      str                    data-ast-type value
#   sub_elements  Dict[str, List[Element]]  keyed by data-role value
#
# REGISTRATION
# ────────────
#   register(ast_node, svg_group, ast_type) -> SVGNodeEntry
#     Called by the renderer immediately after creating each primary <g>.
#     Scans all descendants of svg_group for data-role attributes and
#     populates sub_elements automatically.
#     Adds the entry to all four indexes.
#
# FORWARD LOOKUPS  (AST → SVG)
# ─────────────────────────────
#   svg_group_for(node_id)              -> Optional[Element]
#   svg_subelement(node_id, role)       -> Optional[Element]   first match
#   svg_subelements(node_id, role)      -> List[Element]        all matches
#   all_of_type(ast_type)              -> List[SVGNodeEntry]
#   entry_for_step(step)               -> Optional[SVGNodeEntry]
#
# REVERSE LOOKUPS  (SVG → AST)
# ─────────────────────────────
#   ast_node_for_svg_id(svg_id)        -> Optional[ASTNode]
#     svg_id is the element's 'id' attribute, e.g. "ast-<uuid>"
#
#   ast_node_for_element(element)      -> Optional[ASTNode]
#     Reads data-ast-ref from any SVG element (not necessarily the group)
#     and resolves it to an AST node.  Use this in click-event handlers
#     after calling element.closest('[data-ast-ref]') in JS.
#
# MUTATION HELPERS
# ────────────────
#   invalidate(node_id)
#     Removes an entry from all indexes.  Call before re-registering a node
#     after an incremental re-render of its <g>.
#
#   update_sub_elements(node_id)
#     Re-scans the existing svg_group's descendants and refreshes
#     sub_elements.  Call after modifying the group's children in-place
#     (e.g. adding a seqnum badge when autonumber is toggled on).

"""
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
                 ast_type:  str) -> SVGNodeEntry:
        entry = SVGNodeEntry(
            node_id  = ast_node.node_id,
            ast_node = ast_node,
            svg_group = svg_group,
            ast_type  = ast_type,
        )
        self._index_sub_elements(entry)
        svg_id = f'ast-{ast_node.node_id}'
        self._by_node_id[ast_node.node_id] = entry
        self._by_svg_id[svg_id]            = entry
        self._by_ast_type.setdefault(ast_type, []).append(entry)
        # index step for messages
        step = getattr(ast_node, 'step', None)
        if step is not None:
            self._by_step[step] = entry
        return entry

    def invalidate(self, node_id: str) -> None:
        entry = self._by_node_id.pop(node_id, None)
        if entry is None:
            return
        self._by_svg_id.pop(f'ast-{node_id}', None)
        bucket = self._by_ast_type.get(entry.ast_type, [])
        self._by_ast_type[entry.ast_type] = [e for e in bucket if e.node_id != node_id]
        step = getattr(entry.ast_node, 'step', None)
        if step is not None and self._by_step.get(step) is entry:
            self._by_step.pop(step, None)

    def update_sub_elements(self, node_id: str) -> None:
        entry = self._by_node_id.get(node_id)
        if entry:
            entry.sub_elements.clear()
            self._index_sub_elements(entry)

    def _index_sub_elements(self, entry: SVGNodeEntry) -> None:
        for elem in entry.svg_group.iter():
            role = elem.get('data-role')
            if role:
                entry.sub_elements.setdefault(role, []).append(elem)

    # ── Forward lookups ───────────────────────────────────────────────────────

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

    def entry_for_step(self, step: int) -> Optional['SVGNodeEntry']:
        return self._by_step.get(step)

    # ── Reverse lookups ───────────────────────────────────────────────────────

    def ast_node_for_svg_id(self, svg_id: str) -> Optional[ASTNode]:
        e = self._by_svg_id.get(svg_id)
        return e.ast_node if e else None

    def ast_node_for_element(self, element: Element) -> Optional[ASTNode]:
        ref = element.get('data-ast-ref')
        if ref:
            e = self._by_node_id.get(ref)
            return e.ast_node if e else None
        return None
"""


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 7 — USAGE EXAMPLES
# ──────────────────────────────────────────────────────────────────────────────

# ── Forward: AST → SVG — highlight Alice's lifeline ──────────────────────────
"""
diagram_ast, layout = build_ast_and_layout(source_text)
svg_root, registry  = SequenceDiagramRenderer(diagram_ast, layout).render()

alice    = next(p for p in diagram_ast.participants if p.name == 'Alice')
lifeline = registry.svg_subelement(alice.node_id, 'lifeline')
lifeline.set('stroke', 'red')
lifeline.set('stroke-width', '3')
"""

# ── Reverse: SVG → AST — PyQt QWebEngineView click handler ───────────────────
#
# JavaScript injected into the WebView:
#   document.addEventListener('click', e => {
#       const g = e.target.closest('[data-ast-ref]');
#       if (g) bridge.elementClicked(g.id);
#   });
"""
def on_element_clicked(self, svg_id: str):
    node = self.registry.ast_node_for_svg_id(svg_id)
    if isinstance(node, MessageNode):
        self.property_panel.show_message(node)
    elif isinstance(node, ParticipantNode):
        self.property_panel.show_participant(node)
    elif isinstance(node, LoopNode):
        self.property_panel.show_fragment(node)
"""

# ── All messages in step order ────────────────────────────────────────────────
"""
entries = registry.all_of_type('message')
for entry in sorted(entries, key=lambda e: e.ast_node.step):
    msg = entry.ast_node
    print(f"[{msg.step}] {msg.sender_name} --{msg.arrow.value}--> "
          f"{msg.receiver_name}: {msg.text}")
"""

# ── Incremental label update (no full re-render) ──────────────────────────────
"""
alice.label = 'Alice (Client)'
for role in ('header-label', 'footer-label'):
    elem = registry.svg_subelement(alice.node_id, role)
    if elem is not None:
        elem.text = alice.label
# serialize / push updated SVG to QWebEngineView
"""

# ── Toggle autonumber badges on / off ─────────────────────────────────────────
"""
def toggle_seqnum(registry: SVGNodeRegistry, show: bool):
    for entry in registry.all_of_type('message'):
        badges = registry.svg_subelements(entry.node_id, 'seqnum')
        for badge in badges:
            badge.set('visibility', 'visible' if show else 'hidden')
"""

# ── Find all activation bars for a given participant ──────────────────────────
"""
def activation_bars_for(registry: SVGNodeRegistry,
                         participant_name: str) -> list:
    bars = []
    for entry in registry.all_of_type('activation'):
        node = entry.ast_node          # ActivationNode
        if node.participant_name == participant_name:
            bar = registry.svg_subelement(node.node_id, 'bar')
            if bar is not None:
                bars.append(bar)
    return bars
"""
