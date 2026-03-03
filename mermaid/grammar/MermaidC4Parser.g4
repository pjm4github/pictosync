// MermaidC4Parser.g4
// ANTLR4 Parser Grammar for Mermaid C4 Diagrams
//
// Token vocabulary supplied by MermaidC4Lexer.g4.
// Compile together:
//
//   java -jar antlr-4.13.1-complete.jar -Dlanguage=Python3 ^
//        -visitor -no-listener -o generated ^
//        MermaidC4Lexer.g4 MermaidC4Parser.g4
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

parser grammar MermaidC4Parser;

options { tokenVocab = MermaidC4Lexer; }

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
    | TEXT_REST
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
    | ID          // ← add this
    | INT                       // RelIndex uses a bare integer as first arg
    ;
