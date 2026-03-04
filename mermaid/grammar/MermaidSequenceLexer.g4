// MermaidSequenceLexer.g4
// ANTLR4 Lexer Grammar for Mermaid Sequence Diagrams
//
// Split from MermaidSequence.g4 (combined grammar) to allow lexer modes.
// Compile together with MermaidSequenceParser.g4:
//
//   java -jar antlr-4.13.1-complete.jar -Dlanguage=Python3 ^
//        -visitor -no-listener -o generated ^
//        MermaidSequenceLexer.g4 MermaidSequenceParser.g4
//
// Fixes applied vs the combined grammar:
//   1. ARROW + fragments moved here from the parser section
//   2. UNQUOTED_LABEL / FREE_TEXT replaced with LABEL_MODE and TEXT_MODE
//      — eliminates the maximal-munch line-swallowing bug
//   3. ID hyphen/dot removed — prevents 'web-' consuming the '-' before '->>'
//   4. NEWLINE handles \r\n, \r, \n  (all platforms, CRLF listed first)
//   5. linkLabel replaced by TEXT_REST consumed in TEXT_MODE after COLON
//   6. NEWLINE declared AFTER all keywords (ties broken by declaration order)
//   7. Duplicate '--x' removed from ARROW alternatives

lexer grammar MermaidSequenceLexer;

// =============================================================================
// DEFAULT MODE
// =============================================================================

// ---- Diagram type -----------------------------------------------------------

SEQUENCE_DIAGRAM : 'sequenceDiagram' ;

// ---- Participant type keywords ----------------------------------------------

PARTICIPANT  : 'participant' ;
ACTOR        : 'actor' ;
BOUNDARY     : 'boundary' ;
CONTROL      : 'control' ;
ENTITY       : 'entity' ;
DATABASE     : 'database' ;
COLLECTIONS  : 'collections' ;
QUEUE        : 'queue' ;

// ---- Multi-word keywords (must precede their component words) ---------------

RIGHT_OF : 'right of' ;
LEFT_OF  : 'left of' ;

// ---- Single-word keywords ---------------------------------------------------

// AS pushes LABEL_MODE so the rest of the line is consumed as one LABEL_REST
// token.  This prevents keywords inside alias text (e.g. "Web Browser") from
// being re-tokenised as ACTOR, END, etc.
AS         : 'as' -> pushMode(LABEL_MODE) ;

BOX        : 'box' ;
END        : 'end' ;
CREATE     : 'create' ;
DESTROY    : 'destroy' ;
ACTIVATE   : 'activate' ;
DEACTIVATE : 'deactivate' ;
NOTE       : 'Note' | 'note' ;
OVER       : 'over' ;
LOOP       : 'loop'     -> pushMode(TEXT_MODE) ;
ALT        : 'alt'      -> pushMode(TEXT_MODE) ;
ELSE       : 'else'     -> pushMode(TEXT_MODE) ;
OPT        : 'opt'      -> pushMode(TEXT_MODE) ;
PAR        : 'par'      -> pushMode(TEXT_MODE) ;
AND        : 'and'      -> pushMode(TEXT_MODE) ;
CRITICAL   : 'critical' -> pushMode(TEXT_MODE) ;
OPTION     : 'option'   -> pushMode(TEXT_MODE) ;
BREAK      : 'break'    -> pushMode(TEXT_MODE) ;
RECT       : 'rect'     -> pushMode(TEXT_MODE) ;
AUTONUMBER : 'autonumber' ;
LINK       : 'link' ;
LINKS      : 'links' ;
TRANSPARENT: 'transparent' ;

// ---- Arrow tokens ----------------------------------------------------------
// Rules:
//   a) Longer alternatives must appear before shorter ones that share a prefix.
//      '--x' before '-x', '-->>' before '-->', etc.
//   b) Activation suffix (+/-) is part of the arrow token so that
//      'web->>+account' → ID ARROW('->>+') ID
//      rather than       ID ARROW('->>') UNKNOWN('+') ID.
//   c) ARROW_BASE + ACTIVATE_SUFFIX? as final catch-all handles any
//      combination not listed explicitly.

ARROW
    : '--x'
    | '-x'
    | '-->>+' | '-->>-' | '-->>'
    | '--)+' | '--)-' | '--)'
    | '-->+' | '-->-' | '-->'
    | '--'
    | '->>+' | '->>-' | '->>'
    | '->+' | '->-' | '->'
    | '-)+'  | '-)-'  | '-)'
    | ARROW_BASE ACTIVATE_SUFFIX?
    ;

fragment ARROW_BASE      : '-' '-'? ( '>>' | '>' | 'x' | ')' ) ;
fragment ACTIVATE_SUFFIX : [+\-] ;

// ---- Symbols ----------------------------------------------------------------

// COLON pushes TEXT_MODE so message text, note text, condition labels and link
// URLs are all consumed as a single TEXT_REST token without re-tokenisation.
COLON  : ':' -> pushMode(TEXT_MODE) ;

COMMA  : ',' ;
AT     : '@' ;
LPAREN : '(' ;
RPAREN : ')' ;
LBRACE : '{' ;
RBRACE : '}' ;



// ---- Numbers ----------------------------------------------------------------

INT   : [0-9]+ ;
FLOAT : [0-9]+ '.' [0-9]* | '.' [0-9]+ ;

// ---- Strings and identifiers ------------------------------------------------

QUOTED_STRING : '"' ( ~["\\\r\n] | '\\"' )* '"' ;

// ID does NOT include hyphen or dot.
// If ID matched [a-zA-Z0-9_\-.]* then 'web-' would be consumed as one token
// (maximal munch), leaving '>>+account' with no matching ARROW rule.
// Participant names with hyphens must be written as QUOTED_STRING.
ID : [a-zA-Z_] [a-zA-Z0-9_]* ;

// ---- Color literals ---------------------------------------------------------

RGB_COLOR  : 'rgb('  INT ',' SPACES? INT ',' SPACES? INT ')' ;
RGBA_COLOR : 'rgba(' INT ',' SPACES? INT ',' SPACES? INT ',' SPACES? FLOAT ')' ;
// COLOR_NAME is declared after all keyword tokens so that keywords ('end',
// 'alt', 'par', etc.) are not shadowed.
COLOR_NAME : [a-zA-Z]+ ;

// ---- Comments ---------------------------------------------------------------

COMMENT : '%%' ~[\r\n]* ;

// ---- Whitespace and newlines ------------------------------------------------

// NEWLINE handles all three line-ending conventions.
// '\r\n' is listed first so Windows CRLF is consumed as ONE token (not two).
// The + quantifier merges consecutive blank lines into a single NEWLINE token.
NEWLINE : ( '\r\n' | '\r' | '\n' )+ ;

WS : [ \t]+ -> skip ;

// ---- Fragments --------------------------------------------------------------

fragment SPACES : [ \t]+ ;

// =============================================================================
// LABEL_MODE — entered after 'as'
// =============================================================================
// Captures the rest of the line as LABEL_REST so multi-word aliases like
// "Web Browser" are a single token.
//
// Example:  participant web as Web Browser\n
//   DEFAULT → PARTICIPANT  ID('web')  AS  →pushMode(LABEL_MODE)
//   LABEL   → LABEL_WS skips the space
//             LABEL_REST('Web Browser')   →popMode
//   DEFAULT → NEWLINE

mode LABEL_MODE;

LABEL_WS   : [ \t]+             -> skip ;
LABEL_REST : ~[\r\n]+           -> popMode ;
LABEL_NL   : ( '\r\n' | '\r' | '\n' )+ -> type(NEWLINE), popMode ;

// =============================================================================
// TEXT_MODE — entered after ':'
// =============================================================================
// Captures the rest of the line as TEXT_REST.
// Used for: message text, note text, loop/alt/par/break condition labels,
//           link labels, link URLs.
//
// Example:  web->>+db: Query results\n
//   DEFAULT → ID('web') ARROW('->>+') ID('db') COLON →pushMode(TEXT_MODE)
//   TEXT    → TEXT_WS skips the space
//             TEXT_REST('Query results')              →popMode
//   DEFAULT → NEWLINE

mode TEXT_MODE;

TEXT_WS   : [ \t]+             -> skip ;
TEXT_REST : ~[\r\n]+           -> popMode ;
TEXT_NL   : ( '\r\n' | '\r' | '\n' )+ -> type(NEWLINE), popMode ;
