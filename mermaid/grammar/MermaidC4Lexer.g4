// MermaidC4Lexer.g4
// ANTLR4 Lexer Grammar for Mermaid C4 Diagrams
//
// Split from MermaidC4.g4 (combined grammar) to allow lexer modes.
// Compile together with MermaidC4Parser.g4:
//
//   java -jar antlr-4.13.1-complete.jar -Dlanguage=Python3 ^
//        -visitor -no-listener -o generated ^
//        MermaidC4Lexer.g4 MermaidC4Parser.g4
//
// Reference: https://mermaid.ai/open-source/syntax/c4.html
//            https://github.com/mermaid-js/mermaid  (C4 source)

lexer grammar MermaidC4Lexer;

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

TITLE : 'title'  -> pushMode(TEXT_MODE) ;

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

mode TEXT_MODE;
TEXT_WS   : [ \t]+            -> skip ;
TEXT_REST : ~[\u000D\u000A]+  -> popMode ;
TEXT_NL   : [\u000D\u000A]+   -> type(NEWLINE), popMode ;