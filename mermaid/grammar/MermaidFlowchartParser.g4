// MermaidFlowchartParser.g4
// ANTLR4 *parser* grammar for Mermaid Flowchart / Graph diagrams
// Reference: https://mermaid.js.org/syntax/flowchart.html  (v11.12)
//
// Diagram types covered
//   flowchart <dir>
//   graph     <dir>       — legacy alias, identical semantics
//
// Directions:  TB  TD  BT  LR  RL
//
// ── Classic bracket-pair node shapes (13) ────────────────────────────────
//   [text]            rectangle (default)
//   (text)            rounded rectangle
//   ([text])          stadium / pill
//   [[text]]          subroutine / framed rectangle
//   [(text)]          cylinder / database
//   ((text))          circle
//   (((text)))        double circle
//   >text]            asymmetric / flag
//   {text}            rhombus / diamond
//   {{text}}          hexagon
//   [/text/]          parallelogram lean-right
//   [\\text\\]          parallelogram lean-left
//   [/text\\]          trapezoid
//   [\\text/]          trapezoid-alt
//
// ── New @{} shape syntax (v11.3+) ────────────────────────────────────────
//   A@{ shape: rect, label: "text" }
//   A@{ icon: "fa:gear", form: circle, label: "text", pos: t, h: 60 }
//   A@{ img: "url", label: "text", pos: t, w: 60, h: 60, constraint: on }
//
// ── Class shorthand ───────────────────────────────────────────────────────
//   A:::className    (appended to nodeId or node shape, or inline in edge chain)
//
// ── Edge types ────────────────────────────────────────────────────────────
//   Line styles :  solid (-)   dotted (-.--)   thick (=)   invisible (~~)
//   Heads       :  arrow (>/<)  circle (o)  cross (x)  none (open)
//   Bidirectional arrows: <-->  o--o  x--x
//   Variable length: extra -  .  = chars extend rank span
//
// ── Edge labels ───────────────────────────────────────────────────────────
//   A -->|label| B      pipe-delimited
//   A --label--> B      embedded in shaft (dashes surround text)
//
// ── Edge ID prefix (v11+) ────────────────────────────────────────────────
//   e1@-->              assigns id "e1" to the next edge
//
// ── Edge property statement ───────────────────────────────────────────────
//   e1@{ animate: true, animation: fast, curve: stepBefore }
//
// ── Multi-target chaining ─────────────────────────────────────────────────
//   A & B --> C & D     & separates multiple source or target nodes
//
// ── Subgraphs ─────────────────────────────────────────────────────────────
//   subgraph [id ["title"]]
//       direction <dir>?
//       statement*
//   end
//
// ── Styling ───────────────────────────────────────────────────────────────
//   classDef  name[,name]  css;
//   class     nodeId[,nodeId]  className;
//   linkStyle N[,N]  css;        (N = 0-based edge index, or "default")
//   style     nodeId  css;
//
// ── Interaction ───────────────────────────────────────────────────────────
//   click nodeId  callback  ["tooltip"]
//   click nodeId  call callback()  ["tooltip"]
//   click nodeId  href "url"  ["tooltip"]  [target]
//   click nodeId  "url"  ["tooltip"]  [target]
//
// ── Comments ──────────────────────────────────────────────────────────────
//   %% anything to end of line

parser grammar MermaidFlowchartParser;

options { tokenVocab = MermaidFlowchartLexer; }

// ═══════════════════════════════════════════════════════════════════════════
// PARSER RULES
// ═══════════════════════════════════════════════════════════════════════════

diagram
    : NEWLINE* header NEWLINE+ statement* EOF
    ;

// ── Header ────────────────────────────────────────────────────────────────

header
    : ( KW_FLOWCHART | KW_GRAPH ) direction
    ;

direction
    : DIR_TB | DIR_TD | DIR_BT | DIR_LR | DIR_RL
    ;

// ── Statements ────────────────────────────────────────────────────────────
// Semicolons are optional terminators (legacy support).

statement
    : ( nodeStmt
      | edgeChainStmt
      | classDefStmt
      | classAssignStmt
      | linkStyleStmt
      | nodeStyleStmt
      | clickStmt
      | edgePropStmt
      | directionStmt
      ) SEMI? NEWLINE+
    | subgraphBlock
    | COMMENT NEWLINE+
    | NEWLINE+
    ;

directionStmt
    : KW_DIRECTION direction
    ;

// ═══════════════════════════════════════════════════════════════════════════
// NODE STATEMENT
// ═══════════════════════════════════════════════════════════════════════════
// Declares a node explicitly.  A bare nodeId creates a default-rectangle node.
// Shape and class shorthand are optional suffixes.
//
//   A                           bare id → rectangle
//   A[Process]                  rectangle with label
//   A(Rounded)                  rounded rectangle
//   A:::myClass                 bare id with class shorthand
//   A[Label]:::myClass          shape + class shorthand
//   A@{ shape: rect }           new @{} shape syntax
//   A@{ shape: hex }:::myClass  new shape + class shorthand

nodeStmt
    : nodeId classicShape? classShorthand?
    | nodeId attrBlock    classShorthand?
    ;

nodeId : ID ;

// ── Class shorthand :::className ─────────────────────────────────────────
classShorthand
    : TRIPLE_COLON ID
    ;

// ── Classic bracket-pair shapes ──────────────────────────────────────────
// Listed longest/most-specific first.  Parser alternatives are tried top-down.

// Each shape is one opening delimiter token (which pushed the lexer's label
// mode), a single nodeLabel token, and the matching closing-delimiter token.
classicShape
    : TRIPLE_LPAREN nodeLabel TRIPLE_RPAREN   // (((t)))  double-circle
    | DOUBLE_LBRACK nodeLabel DOUBLE_RBRACK   // [[t]]    subroutine
    | DOUBLE_LBRACE nodeLabel DOUBLE_RBRACE   // {{t}}    hexagon
    | LPAREN_LBRACK nodeLabel RBRACK_RPAREN   // ([t])    stadium
    | LBRACK_LPAREN nodeLabel RPAREN_RBRACK   // [(t)]    cylinder
    | DOUBLE_LPAREN nodeLabel DOUBLE_RPAREN   // ((t))    circle
    | LBRACK_FSLASH nodeLabel RBRACK          // [/t/] [/t\\]  parallelogram / trapezoid
    | LBRACK_BSLASH nodeLabel RBRACK          // [\\t\\] [\\t/] parallelogram-alt / trapezoid-alt
    | LBRACK nodeLabel RBRACK                 // [t]      rectangle
    | LPAREN nodeLabel RPAREN                 // (t)      rounded
    | RANGLE nodeLabel RBRACK                 // >t]      asymmetric
    | LBRACE nodeLabel RBRACE                 // {t}      rhombus
    ;

// ── Node label content ────────────────────────────────────────────────────
// The lexer's M_LBL mode captures the whole label as ONE token:
//   QUOTED_STRING / MARKDOWN_STRING — when the label is wrapped in the DEFAULT
//       mode before a bracket (rare), or
//   LABEL_TEXT — the common case (any inner characters, incl. spaces, <br/>,
//       slashes, unicode).  The visitor strips wrapping quotes/backticks.
// The empty alternative permits empty-label shapes such as ``A()``.

nodeLabel
    : QUOTED_STRING
    | MARKDOWN_STRING
    | LABEL_TEXT
    |
    ;

// ── @{ } attribute block ─────────────────────────────────────────────────
// Shared by new node shapes (A@{...}) and edge property statements (e1@{...}).
// '@{' is a single lexer token (AT_LBRACE) so the brace does not open a label.

attrBlock
    : AT_LBRACE attrList RBRACE
    ;

attrList
    : attr ( COMMA attr )*
    |
    ;

attr
    : attrKey COLON attrVal
    ;

attrKey : ID ;

attrVal
    : QUOTED_STRING
    | ID
    | INT
    ;

// ═══════════════════════════════════════════════════════════════════════════
// EDGE CHAIN STATEMENT
//
// One or more node groups connected by edge operators.
// A node group is one or more node references separated by &.
//
// Examples:
//   A --> B
//   A --> B --> C --> D
//   A & B --> C & D
//   A:::cls1 --> B:::cls2
//   A -->|label| B
//   A --label--> B
//   e1@--> B          (edge-id prefix on edge operator)
// ═══════════════════════════════════════════════════════════════════════════

edgeChainStmt
    : nodeGroup ( edgeOp nodeGroup )+
    ;

// One or more node refs joined by &
nodeGroup
    : nodeRef ( AMP nodeRef )*
    ;

// A node reference in an edge chain may carry a class shorthand.
// It may not carry a shape decorator (shapes are only in nodeStmt).
//nodeRef
//    : nodeId classShorthand?
//    ;
nodeRef
    : nodeId classicShape? classShorthand?
    | nodeId attrBlock    classShorthand?
    ;

// ── Edge operator ─────────────────────────────────────────────────────────
// Composed of: optional edge-id prefix, the edge token, optional pipe label.

edgeOp
    : edgeIdPrefix? edge pipeLabel?
    ;

// e1@  — edge-id prefix.  The @ immediately follows the id with no space.
edgeIdPrefix
    : ID AT
    ;

// The edge itself is one of the four EDGE_* tokens produced by the lexer.
// The visitor decodes direction, style, and minimum rank-span from the token text.
edge
    : EDGE_SOLID
    | EDGE_DOTTED
    | EDGE_THICK
    | EDGE_INVIS
    ;

// |label|  — optional pipe-delimited label after the edge operator
pipeLabel
    : PIPE_LABEL
    ;

// ═══════════════════════════════════════════════════════════════════════════
// SUBGRAPH BLOCK
//
// subgraph [id ["title"]]
//     direction <dir>?
//     statement*
// end
//
// Header forms:
//   subgraph                      anonymous, no title
//   subgraph myId                 id only
//   subgraph myId ["My Title"]    id + quoted title
//   subgraph myId [Bracket Title] id + bracket title (most common in practice)
//   subgraph "My Title"           title only (id inferred)
// ═══════════════════════════════════════════════════════════════════════════

subgraphBlock
    : KW_SUBGRAPH subgraphHeader? NEWLINE+
          statement*
      KW_END NEWLINE*
    ;

subgraphHeader
    : ID subgraphTitle?
    | QUOTED_STRING
    ;

// Title forms:
//   "Quoted Title"        — double-quoted string
//   [Bracket Title]       — bracket-delimited (most common in practice)
subgraphTitle
    : QUOTED_STRING
    | LBRACK nodeLabel RBRACK
    ;

// ═══════════════════════════════════════════════════════════════════════════
// STYLING STATEMENTS
// ═══════════════════════════════════════════════════════════════════════════

// classDef name css;
// classDef name1,name2 css;
classDefStmt
    : KW_CLASSDEF classNameList cssString
    ;

classNameList
    : ID ( COMMA ID )*
    ;

// class nodeId[,nodeId] className;
classAssignStmt
    : KW_CLASS nodeIdList ID
    ;

nodeIdList
    : ID ( COMMA ID )*
    ;

// linkStyle N[,N] css;   or   linkStyle default css;
linkStyleStmt
    : KW_LINKSTYLE linkStyleTargets cssString
    ;

linkStyleTargets
    : INT ( COMMA INT )*
    | KW_DEFAULT
    ;

// style nodeId css;
nodeStyleStmt
    : KW_STYLE ID cssString
    ;

// CSS is free-form text to the end of the line / semicolon.
// The visitor concatenates the CSS_TEXT tokens.
cssString
    : CSS_VALUE_START+
    ;

// ═══════════════════════════════════════════════════════════════════════════
// CLICK STATEMENT
//
// click nodeId callback ["tooltip"]
// click nodeId call callback() ["tooltip"]
// click nodeId href "url" ["tooltip"] [target]
// click nodeId "url" ["tooltip"] [target]
// ═══════════════════════════════════════════════════════════════════════════

clickStmt
    : KW_CLICK ID clickAction? QUOTED_STRING?
    ;

clickAction
    : KW_CALL ID LPAREN RPAREN         // call fn()
    | KW_HREF QUOTED_STRING clickTarget?
    | QUOTED_STRING clickTarget?        // bare URL
    | ID                               // plain callback name
    ;

clickTarget
    : QUOTED_STRING      // "_self" | "_blank" | "_parent" | "_top"
    ;

// ═══════════════════════════════════════════════════════════════════════════
// EDGE PROPERTY STATEMENT
//
// Assigns properties to a previously-declared edge by its ID.
//   e1@{ animate: true }
//   e1@{ animation: fast }
//   e1@{ curve: stepBefore }
// ═══════════════════════════════════════════════════════════════════════════

edgePropStmt
    : ID attrBlock
    ;
