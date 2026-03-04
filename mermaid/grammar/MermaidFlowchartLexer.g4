// MermaidFlowchartLexer.g4
// ANTLR4 *lexer* grammar for Mermaid Flowchart / Graph diagrams
// Reference: https://mermaid.js.org/syntax/flowchart.html  (v11.12)
//
// Token ordering rules (ANTLR4):
//   1. Keywords are declared before ID — keywords win for exact matches.
//   2. Edge tokens are declared before single-character punctuation so that
//      "-->" is one EDGE_SOLID token, not three separate tokens.
//   3. Longer patterns beat shorter patterns within the same declaration order
//      (ANTLR4 always takes the longest match).
//   4. Equal-length tie-breaks are resolved by declaration order (first wins).
//   5. CSS_TEXT pushes CSS_MODE so free-form CSS content cannot clobber
//      DIR_* tokens or keywords in the structural (DEFAULT) mode.

lexer grammar MermaidFlowchartLexer;

// ── Keywords ──────────────────────────────────────────────────────────────

KW_FLOWCHART  : 'flowchart' ;
KW_GRAPH      : 'graph' ;
KW_SUBGRAPH   : 'subgraph' ;
KW_END        : 'end' ;
KW_DIRECTION  : 'direction' ;
KW_CLASSDEF  : 'classDef' -> pushMode(CSS_READY_MODE) ;
KW_CLASS      : 'class' ;
KW_LINKSTYLE  : 'linkStyle' -> pushMode(CSS_READY_MODE) ;
KW_STYLE  : 'style' -> pushMode(CSS_READY_MODE) ;
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
    : '|' ~[|\r\n]+ '|'
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
BSLASH  : '\\' ; // parallelogram-alt: [\text\]
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


// ── Comment ───────────────────────────────────────────────────────────────

COMMENT
    : '%%' ~[\r\n]*
    ;

// ── Unquoted label text (fallback for plain node labels) ─────────────────
// Only fires inside classic shape brackets; excludes all structural chars
// so it cannot accidentally match direction tokens (TD, LR, etc.) on the
// header line.

LABEL_TEXT
    : ~[[\](){}<>/\\\r\n@|"`:;,&% ]+
    ;


// ── Whitespace ────────────────────────────────────────────────────────────

WS
    : [ \t]+ -> skip
    ;

// ── Newline ───────────────────────────────────────────────────────────────
// Handles all three line-ending conventions.
// '\r\n' is listed first so Windows CRLF is consumed as ONE token (not two).
// The + quantifier merges consecutive blank lines into a single NEWLINE token.

NEWLINE : ( '\r\n' | '\r' | '\n' ) ;



// ── Style keywords push CSS_READY_MODE ──────────────────────────────────
// KW_STYLE, KW_CLASSDEF, KW_LINKSTYLE are re-declared here as mode-pushing
// variants.  When the lexer sees 'style', 'classDef', or 'linkStyle' it
// emits the keyword token AND switches to CSS_READY_MODE, where the node/
// class/link target is consumed normally before CSS_MODE takes over for the
// free-form CSS value.
//
// NOTE: These must be declared AFTER the base keyword tokens above so that
// within DEFAULT_MODE the plain keyword tokens win (declaration order).
// These mode-pushing variants live at the bottom of DEFAULT_MODE and are
// only reachable because they are identical literals — ANTLR picks the
// FIRST matching rule, so we rely on CSS_READY_MODE being entered by the
// parser issuing a pushMode via the action, not by re-matching the keyword.
//
// Simpler approach: push CSS_READY_MODE directly from the keyword tokens.
// We redefine the three style keywords to push the mode:

// ═══════════════════════════════════════════════════════════════════════════
// CSS_READY_MODE  — entered right after a style/classDef/linkStyle keyword
// ═══════════════════════════════════════════════════════════════════════════
// In this mode we still need to lex: whitespace (skip), an ID or INT target,
// commas between targets, the KW_DEFAULT token, and then transition to
// CSS_MODE when the actual CSS value starts.

mode CSS_READY_MODE;

// Skip whitespace between keyword and target
CSS_READY_WS     : [ \t]+              -> skip ;

// Identifiers and integers for the statement target (node id, class name,
// link index).  Emit as the same token types the parser expects.
CSS_READY_ID     : [a-zA-Z_][a-zA-Z0-9_\-.]* -> type(ID)   ;
CSS_READY_INT    : [0-9]+                      -> type(INT)  ;
CSS_READY_COMMA  : ','                         -> type(COMMA) ;
CSS_READY_DEFAULT: 'default'                   -> type(KW_DEFAULT) ;

// A bare newline with no CSS value (empty style statement) — return to default.
CSS_READY_NL
    : ('\r\n' | '\r' | '\n')          -> type(NEWLINE), mode(DEFAULT_MODE)
    ;

// In CSS_READY_MODE:
CSS_VALUE_START
    : ~[\r\n;% \t]+  -> mode(CSS_MODE)
    ;

// ═══════════════════════════════════════════════════════════════════════════
// CSS LEXER MODE
// ═══════════════════════════════════════════════════════════════════════════
// Entered after the first CSS_TEXT chunk.  Remains active until a newline
// or semicolon terminates the CSS value, then returns to DEFAULT_MODE.

mode CSS_MODE;

CSS_TEXT_MORE : ~[\r\n;%]+              -> type(CSS_VALUE_START)             ;
CSS_SEMI      : ';'                       -> type(SEMI),   mode(DEFAULT_MODE) ;
CSS_NL        : ('\r\n'|'\r'|'\n')   -> type(NEWLINE), mode(DEFAULT_MODE) ;
CSS_WS        : [ \t]+                   -> skip                       ;
