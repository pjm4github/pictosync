// MermaidC4.g4
// ANTLR4 Grammar for Mermaid C4 Diagrams
// Reference: https://mermaid.ai/open-source/syntax/c4.html
//            https://github.com/mermaid-js/mermaid  (C4 source)
//
// Covers all five diagram types:
//   C4Context    — System Context diagram
//   C4Container  — Container diagram
//   C4Component  — Component diagram
//   C4Dynamic    — Dynamic diagram
//   C4Deployment — Deployment diagram
//
// Element families (all support optional trailing named params $key="val"):
//   Context  : Person, Person_Ext
//              System, SystemDb, SystemQueue
//              System_Ext, SystemDb_Ext, SystemQueue_Ext
//   Container: Container, ContainerDb, ContainerQueue
//              Container_Ext, ContainerDb_Ext, ContainerQueue_Ext
//   Component: Component, ComponentDb, ComponentQueue
//              Component_Ext, ComponentDb_Ext, ComponentQueue_Ext
//   Deployment: Deployment_Node, Node, Node_L, Node_R
//
// Boundary blocks (contain nested elements and boundaries):
//   Enterprise_Boundary, System_Boundary, Container_Boundary, Boundary
//
// Relationships:
//   Rel, BiRel, Rel_Back
//   Rel_U / Rel_Up, Rel_D / Rel_Down, Rel_L / Rel_Left, Rel_R / Rel_Right
//   RelIndex  (Dynamic diagram; index param accepted but ignored at runtime)
//
// Style / layout directives (appear at end of diagram):
//   UpdateElementStyle, updateElementStyle
//   UpdateRelStyle,     updateRelStyle
//   UpdateLayoutConfig
//   AddElementTag, AddRelTag
//
// Parameter conventions:
//   Positional args   : plain quoted strings in declared order
//   Named args        : $paramName="value"  (mix freely with positional)
//   Optional args     : denoted with ? in the spec; grammar accepts 0-N
//
// Comments:
//   %% single-line comment

grammar MermaidC4;

// =============================================================================
// Parser Rules
// =============================================================================

diagram
    : NEWLINE* diagramType NEWLINE+ statement* EOF
    ;

diagramType
    : C4CONTEXT
    | C4CONTAINER
    | C4COMPONENT
    | C4DYNAMIC
    | C4DEPLOYMENT
    ;

statement
    : titleStmt         NEWLINE+
    | elementStmt       NEWLINE+
    | boundaryBlock
    | deployNodeBlock
    | relationStmt      NEWLINE+
    | styleStmt         NEWLINE+
    | layoutStmt        NEWLINE+
    | addTagStmt        NEWLINE+
    | COMMENT           NEWLINE+
    | NEWLINE+
    ;

// ---------------------------------------------------------------------------
// Title
// ---------------------------------------------------------------------------

titleStmt
    : TITLE titleText
    ;

titleText
    : QUOTED_STRING
    | UNQUOTED_TEXT
    ;

// ---------------------------------------------------------------------------
// Elements
// All elements share the pattern:
//   ElementKeyword(alias, label [, techn] [, descr] [, $namedParam="val" ...])
//
// Required:  alias, label
// Optional:  techn, descr, sprite (ignored), tags (ignored), $link (ignored)
//
// Named params accepted anywhere in the arg list:
//   $bgColor, $fontColor, $borderColor, $tags, $link, $techn, $descr, $sprite
// ---------------------------------------------------------------------------

elementStmt
    : elementKw LPAREN argList RPAREN
    ;

elementKw
    // ── Context elements ────────────────────────────────────────────────────
    : PERSON
    | PERSON_EXT
    | SYSTEM
    | SYSTEM_EXT
    | SYSTEM_DB
    | SYSTEM_DB_EXT
    | SYSTEM_QUEUE
    | SYSTEM_QUEUE_EXT
    // ── Container elements ──────────────────────────────────────────────────
    | CONTAINER
    | CONTAINER_EXT
    | CONTAINER_DB
    | CONTAINER_DB_EXT
    | CONTAINER_QUEUE
    | CONTAINER_QUEUE_EXT
    // ── Component elements ──────────────────────────────────────────────────
    | COMPONENT
    | COMPONENT_EXT
    | COMPONENT_DB
    | COMPONENT_DB_EXT
    | COMPONENT_QUEUE
    | COMPONENT_QUEUE_EXT
    ;

// ---------------------------------------------------------------------------
// Boundary blocks  (contain nested statements + inner boundaries)
//
//   Enterprise_Boundary(alias, label [, ?type] [, $namedParam...]) { ... }
//   System_Boundary    (alias, label [, $namedParam...])            { ... }
//   Container_Boundary (alias, label [, $namedParam...])            { ... }
//   Boundary           (alias, label [, ?type] [, $namedParam...])  { ... }
//
// Deployment nodes are also boundary-like (see deployNodeBlock).
// ---------------------------------------------------------------------------

boundaryBlock
    : boundaryKw LPAREN argList RPAREN LBRACE NEWLINE* statement* RBRACE NEWLINE+
    ;

boundaryKw
    : ENTERPRISE_BOUNDARY
    | SYSTEM_BOUNDARY
    | CONTAINER_BOUNDARY
    | BOUNDARY
    ;

// ---------------------------------------------------------------------------
// Deployment Node block
//   Deployment_Node(alias, label [, ?type] [, ?descr] [, $namedParam...]) { ... }
//   Node / Node_L / Node_R  are short aliases for Deployment_Node
// ---------------------------------------------------------------------------

deployNodeBlock
    : deployNodeKw LPAREN argList RPAREN LBRACE NEWLINE* statement* RBRACE NEWLINE+
    ;

deployNodeKw
    : DEPLOYMENT_NODE
    | NODE
    | NODE_L
    | NODE_R
    ;

// ---------------------------------------------------------------------------
// Relationships
//
//   Rel       (from, to, label [, ?techn] [, ?descr] [, $namedParam...])
//   BiRel     (from, to, label [, ?techn] [, ?descr] [, $namedParam...])
//   Rel_Back  (from, to, label [, ?techn] [, ?descr] [, $namedParam...])
//   Rel_U/Up/D/Down/L/Left/R/Right  — same args
//   RelIndex  (index, from, to, label [, ?techn] [, $namedParam...])
//             index is a positional integer; accepted but semantically ignored
// ---------------------------------------------------------------------------

relationStmt
    : relKw LPAREN argList RPAREN
    ;

relKw
    : REL
    | REL_BACK
    | REL_U  | REL_UP
    | REL_D  | REL_DOWN
    | REL_L  | REL_LEFT
    | REL_R  | REL_RIGHT
    | BIREL
    | REL_INDEX
    ;

// ---------------------------------------------------------------------------
// Style directives
//
//   UpdateElementStyle(elementName, $bgColor="…", $fontColor="…", …)
//   updateElementStyle(elementName, $bgColor="…", …)        ← lowercase alias
//
//   UpdateRelStyle(from, to, ?textColor, ?lineColor, ?offsetX, ?offsetY)
//   updateRelStyle(from, to, $textColor="…", …)             ← lowercase alias
//
//   Named param form: $paramName="value"
//   Positional form:  "value"  (UpdateRelStyle accepts both interchangeably)
// ---------------------------------------------------------------------------

styleStmt
    : ( UPDATE_ELEMENT_STYLE | UPDATE_REL_STYLE ) LPAREN argList RPAREN
    ;

// ---------------------------------------------------------------------------
// Layout config
//   UpdateLayoutConfig(?c4ShapeInRow, ?c4BoundaryInRow)
//   UpdateLayoutConfig($c4ShapeInRow="N", $c4BoundaryInRow="N")
// ---------------------------------------------------------------------------

layoutStmt
    : UPDATE_LAYOUT_CONFIG LPAREN argList RPAREN
    ;

// ---------------------------------------------------------------------------
// Tag directives (parsed but treated as informational by most renderers)
//
//   AddElementTag(tagStereo, ?bgColor, ?fontColor, ?borderColor, ?shadowing,
//                 ?shape, ?sprite, ?techn, ?legendText, ?legendSprite)
//   AddRelTag(tagStereo, ?textColor, ?lineColor, ?lineStyle, ?sprite,
//             ?techn, ?legendText, ?legendSprite)
// ---------------------------------------------------------------------------

addTagStmt
    : ( ADD_ELEMENT_TAG | ADD_REL_TAG ) LPAREN argList RPAREN
    ;

// ---------------------------------------------------------------------------
// Argument list — shared by all parenthesised constructs.
//
// Arguments are comma-separated and come in two forms:
//   positional : QUOTED_STRING  or  plain UNQUOTED_TEXT
//   named      : $identifier = QUOTED_STRING
//
// The grammar does not enforce argument count or order;
// semantic validation happens in the visitor.
// ---------------------------------------------------------------------------

argList
    : arg ( COMMA arg )*
    |                           // empty arg list is valid (no args)
    ;

arg
    : namedArg
    | positionalArg
    ;

namedArg
    : DOLLAR ID EQUALS QUOTED_STRING
    ;

positionalArg
    : QUOTED_STRING
    | UNQUOTED_TEXT
    | INT                       // RelIndex uses a bare integer as first arg
    ;

// =============================================================================
// Lexer Rules
// =============================================================================

// ---------------------------------------------------------------------------
// Diagram type keywords  (must precede ID / UNQUOTED_TEXT)
// ---------------------------------------------------------------------------

C4CONTEXT    : 'C4Context' ;
C4CONTAINER  : 'C4Container' ;
C4COMPONENT  : 'C4Component' ;
C4DYNAMIC    : 'C4Dynamic' ;
C4DEPLOYMENT : 'C4Deployment' ;

// ---------------------------------------------------------------------------
// Element keywords
// ---------------------------------------------------------------------------

PERSON              : 'Person' ;
PERSON_EXT          : 'Person_Ext' ;

SYSTEM              : 'System' ;
SYSTEM_EXT          : 'System_Ext' ;
SYSTEM_DB           : 'SystemDb' ;
SYSTEM_DB_EXT       : 'SystemDb_Ext' ;
SYSTEM_QUEUE        : 'SystemQueue' ;
SYSTEM_QUEUE_EXT    : 'SystemQueue_Ext' ;

CONTAINER           : 'Container' ;
CONTAINER_EXT       : 'Container_Ext' ;
CONTAINER_DB        : 'ContainerDb' ;
CONTAINER_DB_EXT    : 'ContainerDb_Ext' ;
CONTAINER_QUEUE     : 'ContainerQueue' ;
CONTAINER_QUEUE_EXT : 'ContainerQueue_Ext' ;

COMPONENT           : 'Component' ;
COMPONENT_EXT       : 'Component_Ext' ;
COMPONENT_DB        : 'ComponentDb' ;
COMPONENT_DB_EXT    : 'ComponentDb_Ext' ;
COMPONENT_QUEUE     : 'ComponentQueue' ;
COMPONENT_QUEUE_EXT : 'ComponentQueue_Ext' ;

// ---------------------------------------------------------------------------
// Boundary / deployment keywords
// ---------------------------------------------------------------------------

ENTERPRISE_BOUNDARY : 'Enterprise_Boundary' ;
SYSTEM_BOUNDARY     : 'System_Boundary' ;
CONTAINER_BOUNDARY  : 'Container_Boundary' ;
BOUNDARY            : 'Boundary' ;

DEPLOYMENT_NODE     : 'Deployment_Node' ;
NODE                : 'Node' ;
NODE_L              : 'Node_L' ;
NODE_R              : 'Node_R' ;

// ---------------------------------------------------------------------------
// Relationship keywords
// ---------------------------------------------------------------------------

REL         : 'Rel' ;
BIREL       : 'BiRel' ;
REL_BACK    : 'Rel_Back' ;
REL_U       : 'Rel_U' ;
REL_UP      : 'Rel_Up' ;
REL_D       : 'Rel_D' ;
REL_DOWN    : 'Rel_Down' ;
REL_L       : 'Rel_L' ;
REL_LEFT    : 'Rel_Left' ;
REL_R       : 'Rel_R' ;
REL_RIGHT   : 'Rel_Right' ;
REL_INDEX   : 'RelIndex' ;

// ---------------------------------------------------------------------------
// Style / layout / tag keywords
// ---------------------------------------------------------------------------

UPDATE_ELEMENT_STYLE : 'UpdateElementStyle' | 'updateElementStyle' ;
UPDATE_REL_STYLE     : 'UpdateRelStyle'     | 'updateRelStyle' ;
UPDATE_LAYOUT_CONFIG : 'UpdateLayoutConfig' ;
ADD_ELEMENT_TAG      : 'AddElementTag' ;
ADD_REL_TAG          : 'AddRelTag' ;

// ---------------------------------------------------------------------------
// Other keywords
// ---------------------------------------------------------------------------

TITLE : 'title' ;

// ---------------------------------------------------------------------------
// Punctuation
// ---------------------------------------------------------------------------

LPAREN : '(' ;
RPAREN : ')' ;
LBRACE : '{' ;
RBRACE : '}' ;
COMMA  : ',' ;
EQUALS : '=' ;
DOLLAR : '$' ;

// ---------------------------------------------------------------------------
// Integer literal  (used as RelIndex first positional arg)
// ---------------------------------------------------------------------------

INT : [0-9]+ ;

// ---------------------------------------------------------------------------
// Quoted string
//   Accepts embedded HTML entities and <br/> tags common in C4 labels.
//   The closing quote ends the token; escaped \" is supported.
// ---------------------------------------------------------------------------

QUOTED_STRING
    : '"' ( '\\' '"' | ~["\u000D\u000A] )* '"'
    ;

// ---------------------------------------------------------------------------
// Identifier
//   Used for alias values (first positional arg) and $paramName names.
//   Aliases in real diagrams include digits, underscores, hyphens, dots.
// ---------------------------------------------------------------------------

ID
    : [a-zA-Z_] [a-zA-Z0-9_\-.]*
    ;

// ---------------------------------------------------------------------------
// Unquoted text
//   Positional args (alias, title text) that appear without quotes.
//   Matched AFTER keywords so keywords win in the element-keyword position,
//   but inside argList an unquoted alias like "customerA" will still match ID
//   (which is fine — positionalArg accepts both ID via UNQUOTED_TEXT and
//   QUOTED_STRING).
//
//   Covers characters commonly found in unquoted C4 aliases and title text.
//   Stops at ( ) , { } newline and $ (named-param prefix).
// ---------------------------------------------------------------------------

UNQUOTED_TEXT
    : ~[(),{}\u000D\u000A"$=\t ]+
    ;

// ---------------------------------------------------------------------------
// Comments
// ---------------------------------------------------------------------------

COMMENT
    : '%%' ~[\u000D\u000A]*
    ;

// ---------------------------------------------------------------------------
// Whitespace and newlines
// ---------------------------------------------------------------------------

NEWLINE
    : [\u000D\u000A]+
    ;

WS
    : [ \t]+ -> skip
    ;
