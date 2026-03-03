// MermaidFlowchart.g4
// ANTLR4 grammar for Mermaid Flowchart / Graph diagrams
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
//   [\text\]          parallelogram lean-left
//   [/text\]          trapezoid
//   [\text/]          trapezoid-alt
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

grammar MermaidFlowchart;

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

classicShape
    : LPAREN LPAREN LPAREN nodeLabel RPAREN RPAREN RPAREN   // (((t)))  double-circle
    | LBRACK LBRACK nodeLabel RBRACK RBRACK                 // [[t]]    subroutine
    | LBRACE LBRACE nodeLabel RBRACE RBRACE                 // {{t}}    hexagon
    | LPAREN LBRACK nodeLabel RBRACK RPAREN                 // ([t])    stadium
    | LBRACK LPAREN nodeLabel RPAREN RBRACK                 // [(t)]    cylinder
    | LPAREN LPAREN nodeLabel RPAREN RPAREN                 // ((t))    circle
    | LBRACK FSLASH nodeLabel FSLASH RBRACK                 // [/t/]    parallelogram
    | LBRACK BSLASH nodeLabel BSLASH RBRACK                 // [\t\]    parallelogram-alt
    | LBRACK FSLASH nodeLabel BSLASH RBRACK                 // [/t\]    trapezoid
    | LBRACK BSLASH nodeLabel FSLASH RBRACK                 // [\t/]    trapezoid-alt
    | LBRACK nodeLabel RBRACK                               // [t]      rectangle
    | LPAREN nodeLabel RPAREN                               // (t)      rounded
    | RANGLE nodeLabel RBRACK                               // >t]      asymmetric
    | LBRACE nodeLabel RBRACE                               // {t}      rhombus
    ;

// ── Node label content ────────────────────────────────────────────────────
// Three surface forms:
//   "quoted"      — most common, handles unicode / HTML / entity refs
//   "`markdown`"  — bold, italic, auto-wrap
//   plain text    — unquoted, rarely used, multi-token

nodeLabel
    : QUOTED_STRING
    | MARKDOWN_STRING
    | labelText+
    ;

labelText
    : LABEL_TEXT
    | ID
    | INT
    ;

// ── @{ } attribute block ─────────────────────────────────────────────────
// Shared by new node shapes (A@{...}) and edge property statements (e1@{...}).

attrBlock
    : AT LBRACE attrList RBRACE
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
nodeRef
    : nodeId classShorthand?
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
//   subgraph "My Title"           title only (id inferred)
// ═══════════════════════════════════════════════════════════════════════════

subgraphBlock
    : KW_SUBGRAPH subgraphHeader? NEWLINE+
          statement*
      KW_END NEWLINE+
    ;

subgraphHeader
    : ID QUOTED_STRING?
    | QUOTED_STRING
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
    : CSS_TEXT+
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


// ═══════════════════════════════════════════════════════════════════════════
// LEXER RULES
// ═══════════════════════════════════════════════════════════════════════════
//
// Token ordering rules (ANTLR4):
//   1. Keywords are declared before ID — keywords win for exact matches.
//   2. Edge tokens are declared before single-character punctuation so that
//      "-->" is one EDGE_SOLID token, not three separate tokens.
//   3. Longer patterns beat shorter patterns within the same declaration order
//      (ANTLR4 always takes the longest match).
//   4. Equal-length tie-breaks are resolved by declaration order (first wins).

// ── Keywords ──────────────────────────────────────────────────────────────

KW_FLOWCHART  : 'flowchart' ;
KW_GRAPH      : 'graph' ;
KW_SUBGRAPH   : 'subgraph' ;
KW_END        : 'end' ;
KW_DIRECTION  : 'direction' ;
KW_CLASSDEF   : 'classDef' ;
KW_CLASS      : 'class' ;
KW_LINKSTYLE  : 'linkStyle' ;
KW_STYLE      : 'style' ;
KW_CLICK      : 'click' ;
KW_CALL       : 'call' ;
KW_HREF       : 'href' ;
KW_DEFAULT    : 'default' ;

// ── Direction tokens ──────────────────────────────────────────────────────

DIR_TB : 'TB' ;
DIR_TD : 'TD' ;
DIR_BT : 'BT' ;
DIR_LR : 'LR' ;
DIR_RL : 'RL' ;

// ── Edge operator tokens ──────────────────────────────────────────────────
//
// Design rationale
// ────────────────
// Mermaid's edge syntax has four line-style families (solid, dotted, thick,
// invisible) each with optional left/right terminators (arrow, circle, cross)
// and an optional embedded text label.  The number of repeated characters
// sets the minimum rank span.  All of this is most cleanly handled at the
// lexer level — one token per edge string — rather than at the parser level.
//
// Fragment helpers
// ────────────────

// Shaft fragments — the repeating core of each line style
fragment F_DASH   : '-' '-'+ ;                 // --  ---  ---- ...
fragment F_DOT    : '-' '.'+ '-'? ;            // -.-  -..-  -...- ...
fragment F_EQ     : '=' '='+ ;                 // ==  ===  ==== ...
fragment F_TILDE  : '~' '~'+ ;                 // ~~  ~~~  ...

// Terminal fragments — head characters at either end of the shaft
fragment F_LARROW : '<' ;
fragment F_RARROW : '>' ;
fragment F_CIRC   : 'o' ;
fragment F_CROSS  : 'x' ;

fragment F_LEFT  : F_LARROW | F_CIRC | F_CROSS ;
fragment F_RIGHT : F_RARROW | F_CIRC | F_CROSS ;

// Embedded label fragment — text between dashes: --label-->
// Matches any sequence of non-dash, non-newline characters surrounded by dashes.
// The leading '-' is part of the shaft; label chars then the shaft continues.
fragment F_EMBEDDED_LABEL : '-' ~[\-\r\n|>ox]+ ;

// ── EDGE_SOLID ─────────────────────────────────────────────────────────────
// Matches:  --   -->  <--  <-->  o--o  x--x  o-->  x-->  etc.
// Also matches embedded-label forms: --label-->
//
// Pattern: optional-left-head  shaft  optional-embedded-label  optional-right-head
// The embedded label is part of the shaft segment so it is expressed inside.

EDGE_SOLID
    : F_LEFT? F_DASH F_EMBEDDED_LABEL? F_RIGHT?
    ;

// ── EDGE_DOTTED ────────────────────────────────────────────────────────────
// Matches:  -.-   -.->   <-.-  <-.->  o-.-o  etc.

EDGE_DOTTED
    : F_LEFT? F_DOT F_RIGHT?
    ;

// ── EDGE_THICK ─────────────────────────────────────────────────────────────
// Matches:  ==   ==>  <==  <==>  etc.

EDGE_THICK
    : F_LEFT? F_EQ F_RIGHT?
    ;

// ── EDGE_INVIS ─────────────────────────────────────────────────────────────
// Invisible links have no head characters.

EDGE_INVIS
    : F_TILDE
    ;

// ── Pipe-delimited edge label ─────────────────────────────────────────────
// |text|  — appears after the edge operator, before the target node.
// Captured as one token; the visitor strips the surrounding pipes.

PIPE_LABEL
    : '|' ~['|' '\r' '\n']+ '|'
    ;

// ── Quoted and markdown strings ───────────────────────────────────────────

QUOTED_STRING
    : '"' ( '\\' '"' | ~["\r\n] )* '"'
    ;

// "`markdown`" — double-quote wrapping around backtick-fenced content
MARKDOWN_STRING
    : '"' '`' ~[`]* '`' '"'
    ;

// ── Triple colon — class shorthand operator ───────────────────────────────
// Must be declared before COLON so that ::: is not lexed as three COLONs.

TRIPLE_COLON : ':::' ;

// ── AT sign ───────────────────────────────────────────────────────────────
// Used for @{} attribute blocks on both nodes and edge IDs.

AT : '@' ;

// ── Punctuation ───────────────────────────────────────────────────────────

LPAREN  : '(' ;
RPAREN  : ')' ;
LBRACK  : '[' ;
RBRACK  : ']' ;
LBRACE  : '{' ;
RBRACE  : '}' ;
RANGLE  : '>' ;    // asymmetric shape:  >text]
FSLASH  : '/' ;    // parallelogram:     [/text/]
BSLASH  : '\\' ;   // parallelogram-alt: [\text\]
COLON   : ':' ;
SEMI    : ';' ;
COMMA   : ',' ;
AMP     : '&' ;    // multi-target node separator

// ── Integer ───────────────────────────────────────────────────────────────

INT : [0-9]+ ;

// ── Identifier ────────────────────────────────────────────────────────────
// Node ids, class names, attribute keys, callback names, shape names.
// Declared AFTER all keyword tokens so keywords win for exact matches.
// Allows hyphens and dots (common in real-world node ids: "my-node", "api.v2").

ID
    : [a-zA-Z_] [a-zA-Z0-9_\-.]*
    ;

// ── CSS property string ───────────────────────────────────────────────────
// Free-form CSS content inside classDef / linkStyle / style statements.
// Captured as raw text up to the end of line or semicolon.
// WS -> skip fires first, so CSS_TEXT will not start with whitespace.

CSS_TEXT
    : ~[\r\n;%%]+
    ;

// ── Unquoted label text (fallback for plain node labels) ─────────────────
// Matches inside classic shape brackets when neither QUOTED_STRING nor
// MARKDOWN_STRING applied.  Stops at closing bracket characters and newlines.

LABEL_TEXT
    : ~[\[\](){}<>/\\\r\n@|"`:;,&%%]+
    ;

// ── Comment ───────────────────────────────────────────────────────────────

COMMENT
    : '%%' ~[\r\n]*
    ;

// ── Newline ───────────────────────────────────────────────────────────────

NEWLINE
    : [\r\n]+
    ;

// ── Whitespace ────────────────────────────────────────────────────────────

WS
    : [ \t]+ -> skip
    ;
