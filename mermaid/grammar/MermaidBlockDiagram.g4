// MermaidBlockDiagram.g4
// ANTLR4 grammar for Mermaid Block Diagrams
// Reference: https://mermaid.ai/open-source/syntax/block.html  (v11.12)
//
// Key differences from flowchart:
//   • Author has FULL positional control — blocks appear in the order written.
//   • Layout is grid-based: a column count controls row wrapping.
//   • Blocks carry an optional :N width-span suffix (1 = default).
//   • Composite blocks nest other blocks inside { }.
//   • Space blocks are layout fillers, not real nodes.
//   • Block-arrow is a unique shape: id<["label"]>(direction)
//   • Edges are declared AFTER all block/composite declarations.
//
// ── Diagram header ────────────────────────────────────────────────────────
//   block-beta
//   block-beta
//     columns N
//
// ── Block declarations ────────────────────────────────────────────────────
//   id                              default rectangle, width 1
//   id:N                            default rectangle, column-span N
//   id["label"]                     rectangle with label, width 1
//   id["label"]:N                   rectangle with label, column-span N
//   id("label")                     round-edge rectangle
//   id(["label"])                   stadium / pill
//   id[["label"]]                   subroutine / framed rectangle
//   id[("label")]                   cylinder / database
//   id(("label"))                   circle
//   id(((  "label"  )))             double circle
//   id>"label"]                     asymmetric / flag
//   id{"label"}                     rhombus / diamond
//   id{{"label"}}                   hexagon
//   id[/"label"/]                   parallelogram lean-right
//   id[\"label"\]                   parallelogram lean-left
//   id[/"label"\]                   trapezoid
//   id[\"label"/]                   trapezoid-alt
//   id<["label"]>(direction)        block arrow  (direction: left|right|up|down)
//   space                           1-column empty filler
//   space:N                         N-column empty filler
//
// ── Composite block ───────────────────────────────────────────────────────
//   block:id["label"]               named composite (outer label)
//   block:id                        named composite without label
//   block                           anonymous composite
//     columns N                     optional inner column count
//     ...block declarations...
//   end
//
// ── Edge declarations ─────────────────────────────────────────────────────
//   A --> B                         arrow, no label
//   A --- B                         open line, no label
//   A -- "label" --> B              arrow with label
//   A -- "label" --- B              open line with label
//   A --> B & C                     fan-out to multiple targets
//   A & B --> C                     fan-in from multiple sources
//
// ── Styling ───────────────────────────────────────────────────────────────
//   style id  fill:#f00,stroke:#333,...
//   classDef name  fill:#f00,...
//   class id[,id] name
//
// ── Comments ──────────────────────────────────────────────────────────────
//   %% anything to end of line
//
// ── Lexer ordering notes ──────────────────────────────────────────────────
//   1. KW_BLOCK_BETA  'block-beta'  before KW_BLOCK  'block'
//   2. ARROW  '-->'  and  OPEN_EDGE  '---'  before DASH  '-'
//   3. DOUBLE_COLON  ':::'  before COLON  ':'  (classDef shorthand)
//   4. All keywords before ID

grammar MermaidBlockDiagram;

// ═══════════════════════════════════════════════════════════════════════════
// PARSER RULES
// ═══════════════════════════════════════════════════════════════════════════

diagram
    : NEWLINE* KW_BLOCK_BETA NEWLINE+
      columnDecl?
      statement*
      EOF
    ;

// Optional top-level column count.  May appear as the very first statement.
columnDecl
    : KW_COLUMNS INT NEWLINE+
    ;

// ── Statement dispatcher ──────────────────────────────────────────────────

statement
    : blockDecl     NEWLINE+
    | compositeBlock
    | edgeStmt      NEWLINE+
    | styleStmt     NEWLINE+
    | classDefStmt  NEWLINE+
    | classAssign   NEWLINE+
    | spaceDecl     NEWLINE+
    | COMMENT       NEWLINE+
    | NEWLINE+
    ;

// ═══════════════════════════════════════════════════════════════════════════
// BLOCK DECLARATIONS
//
// A block declaration is: shapeExpr optionally followed by :N (column span).
// The shapeExpr encodes both the shape type and the label.
//
// Block-arrow is a unique shape with its own rule.
// ═══════════════════════════════════════════════════════════════════════════

blockDecl
    : blockId blockArrowShape                   // block arrow — no width suffix
    | blockId classicShape widthSpec?           // classic bracket-pair shape
    | blockId widthSpec?                        // bare id (implicit rectangle)
    ;

blockId : ID ;

// Optional :N column-span suffix
widthSpec
    : COLON INT
    ;

// ── Classic bracket-pair shapes ───────────────────────────────────────────
// Same 13 shapes as flowchart grammar, but here each shape wraps a label
// that is always a QUOTED_STRING (or rarely a plain ID for very short labels).
// Listed longest-first so the parser tries the most-specific alternatives
// before the shorter ones.

classicShape
    : LPAREN LPAREN LPAREN blockLabel RPAREN RPAREN RPAREN   // (((l)))  double-circle
    | LBRACK LBRACK blockLabel RBRACK RBRACK                 // [[l]]    subroutine
    | LBRACE LBRACE blockLabel RBRACE RBRACE                 // {{l}}    hexagon
    | LPAREN LBRACK blockLabel RBRACK RPAREN                 // ([l])    stadium
    | LBRACK LPAREN blockLabel RPAREN RBRACK                 // [(l)]    cylinder
    | LPAREN LPAREN blockLabel RPAREN RPAREN                 // ((l))    circle
    | LBRACK FSLASH blockLabel FSLASH RBRACK                 // [/l/]    parallelogram
    | LBRACK BSLASH blockLabel BSLASH RBRACK                 // [\l\]    parallelogram-alt
    | LBRACK FSLASH blockLabel BSLASH RBRACK                 // [/l\]    trapezoid
    | LBRACK BSLASH blockLabel FSLASH RBRACK                 // [\l/]    trapezoid-alt
    | LBRACK blockLabel RBRACK                               // [l]      rectangle
    | LPAREN blockLabel RPAREN                               // (l)      rounded
    | RANGLE blockLabel RBRACK                               // >l]      asymmetric
    | LBRACE blockLabel RBRACE                               // {l}      rhombus
    ;

// Block labels are quoted strings, markdown strings, or bare identifiers.
blockLabel
    : QUOTED_STRING
    | MARKDOWN_STRING
    | ID
    ;

// ── Block-arrow shape ─────────────────────────────────────────────────────
// Syntax: id<["label"]>(direction)
// The < > pair wraps the label; the () suffix carries the direction keyword.
// Direction values: left | right | up | down  (validated by visitor)

blockArrowShape
    : LANGLE LBRACK blockLabel RBRACK RANGLE
      LPAREN arrowDirection RPAREN
    ;

arrowDirection
    : KW_LEFT | KW_RIGHT | KW_UP | KW_DOWN
    ;

// ── Space blocks ──────────────────────────────────────────────────────────
// space       — 1-column filler
// space:N     — N-column filler

spaceDecl
    : KW_SPACE widthSpec?
    ;

// ═══════════════════════════════════════════════════════════════════════════
// COMPOSITE BLOCK
//
// A composite block groups other blocks (and their own column layout) under
// a named or anonymous parent.  Composites may nest recursively.
//
// Forms:
//   block:id["label"]    named composite with visible label
//   block:id             named composite without label
//   block                anonymous composite
//     columns N
//     ...statements...
//   end
// ═══════════════════════════════════════════════════════════════════════════

compositeBlock
    : KW_BLOCK compositeHeader? NEWLINE+
          columnDecl?
          statement*
      KW_END NEWLINE+
    ;

compositeHeader
    : COLON blockId ( LBRACK blockLabel RBRACK )?    // :id  or  :id["label"]
    ;

// ═══════════════════════════════════════════════════════════════════════════
// EDGE STATEMENTS
//
// Block diagrams can have directional or open edges between any block ids.
// Multiple sources or targets are connected with the & operator.
//
//   A --> B
//   A --- B
//   A -- "label" --> B
//   A -- "label" --- B
//   A --> B & C         (fan-out)
//   A & B --> C         (fan-in)
// ═══════════════════════════════════════════════════════════════════════════

edgeStmt
    : edgeGroup edgeOp edgeGroup
    ;

// One or more block ids joined by &
edgeGroup
    : blockId ( AMP blockId )*
    ;

// The edge operator: optionally prefixed with a quoted label
edgeOp
    : ARROW                                 // -->
    | OPEN_EDGE                             // ---
    | DASH QUOTED_STRING ARROW              // -- "label" -->
    | DASH QUOTED_STRING OPEN_EDGE          // -- "label" ---
    ;

// ═══════════════════════════════════════════════════════════════════════════
// STYLING STATEMENTS
// ═══════════════════════════════════════════════════════════════════════════

// style id  fill:#f9f,stroke:#333,stroke-width:4px
styleStmt
    : KW_STYLE blockId cssProperties
    ;

// classDef name  fill:#f00,color:white
classDefStmt
    : KW_CLASSDEF classNameList cssProperties
    ;

classNameList
    : ID ( COMMA ID )*
    ;

// class id[,id] className
classAssign
    : KW_CLASS blockIdList ID
    ;

blockIdList
    : ID ( COMMA ID )*
    ;

// CSS properties: free-form text to end of line; semicolon is optional.
cssProperties
    : CSS_TEXT+ SEMI?
    ;


// ═══════════════════════════════════════════════════════════════════════════
// LEXER RULES
// ═══════════════════════════════════════════════════════════════════════════
//
// Declaration order rules:
//   1. KW_BLOCK_BETA  before  KW_BLOCK  (longer literal wins)
//   2. ARROW  '-->'   before  OPEN_EDGE  '---'  before  DASH  '-'
//   3. DOUBLE_COLON   before  COLON
//   4. MARKDOWN_STRING before QUOTED_STRING (same opening char "; longer wins)
//   5. All keyword tokens before ID

// ── Diagram header keyword ────────────────────────────────────────────────
// 'block-beta' contains a hyphen — must be a keyword token.
// Declared before KW_BLOCK so the longer literal wins.

KW_BLOCK_BETA : 'block-beta' ;
KW_BLOCK      : 'block' ;
KW_END        : 'end' ;
KW_COLUMNS    : 'columns' ;
KW_SPACE      : 'space' ;
KW_STYLE      : 'style' ;
KW_CLASSDEF   : 'classDef' ;
KW_CLASS      : 'class' ;

// Block-arrow direction keywords
KW_LEFT  : 'left' ;
KW_RIGHT : 'right' ;
KW_UP    : 'up' ;
KW_DOWN  : 'down' ;

// ── Edge tokens ───────────────────────────────────────────────────────────
// ARROW and OPEN_EDGE must be declared before DASH so they are not
// fragmented into individual '-' and '>' characters.

ARROW     : '-->' ;
OPEN_EDGE : '---' ;
DASH      : '--' ;      // two-dash prefix for labelled edges: -- "text" -->

// ── Strings ───────────────────────────────────────────────────────────────
// MARKDOWN_STRING must be declared before QUOTED_STRING because both open
// with '"'.  ANTLR4 tries longer match first; markdown has extra '`' chars.

MARKDOWN_STRING
    : '"' '`' ~[`]* '`' '"'
    ;

QUOTED_STRING
    : '"' ( '\\' '"' | ~["\r\n] )* '"'
    ;

// ── Double-colon (class shorthand) ────────────────────────────────────────
// Must precede COLON so ':::' is not lexed as three COLONs.

TRIPLE_COLON : ':::' ;

// ── Punctuation ───────────────────────────────────────────────────────────

LPAREN  : '(' ;
RPAREN  : ')' ;
LBRACK  : '[' ;
RBRACK  : ']' ;
LBRACE  : '{' ;
RBRACE  : '}' ;
LANGLE  : '<' ;       // block-arrow left bracket
RANGLE  : '>' ;       // asymmetric shape opening
FSLASH  : '/' ;       // parallelogram [/l/]
BSLASH  : '\\' ;      // parallelogram-alt [\l\]
COLON   : ':' ;
SEMI    : ';' ;
COMMA   : ',' ;
AMP     : '&' ;       // multi-target separator in edges

// ── Integer ───────────────────────────────────────────────────────────────

INT : [0-9]+ ;

// ── Identifier ────────────────────────────────────────────────────────────
// Block ids, class names, CSS property names.
// Allows hyphens and dots (e.g. "block-A", "node.1").
// Declared after all keyword tokens.

ID
    : [a-zA-Z_] [a-zA-Z0-9_\-.]*
    ;

// ── CSS property text ─────────────────────────────────────────────────────
// Free-form CSS to end of line, stopping at newline and semicolon.

CSS_TEXT
    : ~[\r\n;%%]+
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
