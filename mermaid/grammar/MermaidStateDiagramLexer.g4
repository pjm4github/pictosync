// MermaidStateDiagramLexer.g4
// ANTLR4 *lexer* grammar for Mermaid State Diagrams
// Reference: https://mermaid.ai/open-source/syntax/stateDiagram.html  (v11.12)
//
// Token ordering rules (ANTLR4):
//   1. KW_STATE_DIAGRAM_V2  before KW_STATE_DIAGRAM  (longer literal wins)
//   2. START_END  '[*]'     before LBRACK  '[' (so [*] is one token)
//   3. STEREOTYPE '<<...>>' before LT '<'  (so <<choice>> is one token)
//   4. TRANSITION '-->'     before CONCURRENCY '--' before MINUS '-'
//   5. TRIPLE_COLON ':::'   before COLON ':'
//   6. KW_END_NOTE uses inline [ \t]* (WS is skip-channel, unreferenceable)
//   7. All keyword tokens   before ID
//   8. KW_CLASSDEF pushes CSS_READY_MODE so free-form CSS content cannot
//      clobber keywords or FREE_TEXT in the structural (DEFAULT) mode.

lexer grammar MermaidStateDiagramLexer;

// ── Diagram type ──────────────────────────────────────────────────────────
// v2 must be declared first — it is longer and would otherwise partially
// match KW_STATE_DIAGRAM leaving "-v2" to cause a lex error.

KW_STATE_DIAGRAM_V2 : 'stateDiagram-v2' ;
KW_STATE_DIAGRAM    : 'stateDiagram' ;

// ── Statement keywords ────────────────────────────────────────────────────

KW_STATE     : 'state' ;
KW_AS        : 'as' ;
KW_DIRECTION : 'direction' ;
KW_CLASSDEF  : 'classDef' -> mode(CSS_READY_MODE) ;
KW_CLASS     : 'class' ;
KW_NOTE      : 'note' -> mode(NOTE_HDR_MODE) ;
KW_OF        : 'of' ;
KW_RIGHT     : 'right' ;
KW_LEFT      : 'left' ;

// "end note" is two words but functions as a single terminator token.
// We inline the inter-word whitespace with [ \t]+ because WS is declared
// as -> skip and therefore cannot be referenced inside other lexer rules.
KW_END_NOTE  : 'end' [ \t]+ 'note' ;

// ── Direction values ──────────────────────────────────────────────────────

DIR_TB : 'TB' ;
DIR_TD : 'TD' ;
DIR_BT : 'BT' ;
DIR_LR : 'LR' ;
DIR_RL : 'RL' ;

// ── [*] start / end pseudo-state ─────────────────────────────────────────
// Must be declared before LBRACK so the full three-character sequence is
// consumed as a single token.

START_END : '[*]' ;

// ── Stereotype <<choice>> <<fork>> <<join>> ───────────────────────────────
// Must be declared before any single '<' token.
// Whitespace inside the angle brackets is consumed here (not by WS -> skip).

STEREOTYPE
    : '<<' [ \t]* ( 'choice' | 'fork' | 'join' ) [ \t]* '>>'
    ;

// ── Transition arrow ──────────────────────────────────────────────────────
// --> must be declared before CONCURRENCY (--) so that the full arrow is
// consumed atomically rather than as "--" followed by ">".

TRANSITION : '-->' ;

// ── Concurrency divider ───────────────────────────────────────────────────
// -- separates parallel regions inside a composite state body.
// Must be declared before any lone MINUS token (if one is ever needed).

CONCURRENCY : '--' ;

// ── Quoted string ─────────────────────────────────────────────────────────
// Used for state labels in: state "label" as id

QUOTED_STRING
    : '"' ( '\\' '"' | ~["\r\n] )* '"'
    ;

// ── Triple colon ──────────────────────────────────────────────────────────
// Class shorthand operator :::className.
// Must be declared before COLON so that ::: is one token, not three COLONs.

TRIPLE_COLON : ':::' ;

// ── Punctuation ───────────────────────────────────────────────────────────

LBRACK : '[' ;
RBRACK : ']' ;
LBRACE : '{' ;
RBRACE : '}' ;
// COLON is declared below with -> mode(FREE_TEXT_MODE)
SEMI   : ';' ;
COMMA  : ',' ;

// ── Integer ───────────────────────────────────────────────────────────────

INT : [0-9]+ ;

// ── Identifier ────────────────────────────────────────────────────────────
// State ids, class names, direction values (when not exact keywords), etc.
// Allows hyphens and dots so state ids like "my-state" or "app.idle" work.
// Declared after all keyword tokens — keywords win on exact-length match
// by declaration order.

ID
    : [a-zA-Z_] [a-zA-Z0-9_\-.]*
    ;

// ── Free-form text ────────────────────────────────────────────────────────
// FREE_TEXT must NOT live in DEFAULT_MODE — a catch-all there would swallow
// START_END, TRANSITION, keywords, and IDs before they can be matched.
//
// Instead, COLON uses mode(FREE_TEXT_MODE) — a hard switch, never pushMode —
// so the mode stack never grows. NOTE_BODY_MODE handles multi-line note bodies.
//
// In DEFAULT_MODE the COLON token hard-switches to FREE_TEXT_MODE:

COLON : ':' -> mode(FREE_TEXT_MODE) ;

// ── Comment ───────────────────────────────────────────────────────────────

COMMENT
    : '%%' ~[\r\n]*
    ;

// ── Newline ───────────────────────────────────────────────────────────────
// Handles all three line-ending conventions.
// '\r\n' is listed first so Windows CRLF is consumed as ONE token (not two).

NEWLINE : ( '\r\n' | '\r' | '\n' ) ;

// ── Whitespace ────────────────────────────────────────────────────────────

WS
    : [ \t]+ -> skip
    ;



// ═══════════════════════════════════════════════════════════════════════════
// FREE_TEXT_MODE  — entered after COLON in a state description or transition
// ═══════════════════════════════════════════════════════════════════════════
// Consumes everything to end-of-line as FREE_TEXT, then returns to DEFAULT.
// WS is NOT skipped here — spaces are part of the free-form content.

mode FREE_TEXT_MODE;

FREE_TEXT    : ~[\r\n%]+                  ;   // content token
FREE_TEXT_NL : ('\r\n' | '\r' | '\n')  -> type(NEWLINE), mode(DEFAULT_MODE) ;
FREE_TEXT_CMT: '%%' ~[\r\n]*              -> type(COMMENT), mode(DEFAULT_MODE) ;

// ═══════════════════════════════════════════════════════════════════════════
// NOTE_HDR_MODE  — entered immediately after the 'note' keyword
// ═══════════════════════════════════════════════════════════════════════════
// Lexes the note header tokens: right/left, 'of', state id, optional colon.
// A bare newline (no colon) signals a multi-line note — pushes NOTE_BODY_MODE.
// A colon pushes FREE_TEXT_MODE for the single-line note content.

mode NOTE_HDR_MODE;

NOTE_HDR_WS      : [ \t]+                         -> skip ;
NOTE_HDR_RIGHT   : 'right'                         -> type(KW_RIGHT) ;
NOTE_HDR_LEFT    : 'left'                          -> type(KW_LEFT) ;
NOTE_HDR_OF      : 'of'                            -> type(KW_OF) ;
NOTE_HDR_ID      : [a-zA-Z_][a-zA-Z0-9_\-.]*     -> type(ID) ;
// Colon → single-line note: hard switch so FREE_TEXT_NL returns to DEFAULT.
NOTE_HDR_COLON   : ':'                             -> type(COLON), mode(FREE_TEXT_MODE) ;
// Newline with no colon → multi-line note body follows.
NOTE_HDR_NL      : ('\r\n' | '\r' | '\n')     -> type(NEWLINE), mode(NOTE_BODY_MODE) ;
// Safety: comment on note header line (unusual but legal) — return to DEFAULT.
NOTE_HDR_CMT     : '%%' ~[\r\n]*                -> type(COMMENT), mode(DEFAULT_MODE) ;

// ═══════════════════════════════════════════════════════════════════════════
// NOTE_BODY_MODE  — entered after a bare note header line ends with NEWLINE
// ═══════════════════════════════════════════════════════════════════════════
// Each body line is consumed as FREE_TEXT until "end note" terminates.
// KW_END_NOTE pops back to DEFAULT_MODE.

mode NOTE_BODY_MODE;

NOTE_BODY_TEXT : ~[\r\n%]+                  -> type(FREE_TEXT)                ;
NOTE_BODY_NL   : ('\r\n' | '\r' | '\n')  -> type(NEWLINE)                  ;
NOTE_BODY_CMT  : '%%' ~[\r\n]*              -> type(COMMENT)                  ;
NOTE_BODY_END  : 'end' [ \t]+ 'note'         -> type(KW_END_NOTE), mode(DEFAULT_MODE) ;
NOTE_BODY_WS   : [ \t]+                      -> skip                           ;

// ═══════════════════════════════════════════════════════════════════════════
// CSS_READY_MODE  — entered right after a classDef keyword
// ═══════════════════════════════════════════════════════════════════════════
// In this mode we still need to lex: whitespace (skip), an ID target (class
// name), commas between multiple names, and then transition to CSS_MODE when
// the actual CSS property value starts.

mode CSS_READY_MODE;

// Skip whitespace between keyword and target
CSS_READY_WS     : [ \t]+              -> skip ;

// Identifiers for the class name list.  Emit as the same token types the
// parser expects.
CSS_READY_ID     : [a-zA-Z_][a-zA-Z0-9_\-.]* -> type(ID) ;
CSS_READY_COMMA  : ','                        -> type(COMMA) ;

// Comment on same line as classDef keyword (before CSS value) — return to default.
CSS_READY_CMT    : '%%' ~[\r\n]*              -> type(COMMENT), mode(DEFAULT_MODE) ;

// A bare newline with no CSS value (empty classDef) — return to default.
CSS_READY_NL
    : ('\r\n' | '\r' | '\n')          -> type(NEWLINE), mode(DEFAULT_MODE)
    ;

// First CSS value character — switch to CSS_MODE for the rest.
CSS_VALUE_START
    : ~[\r\n;% \t]+                   -> mode(CSS_MODE)
    ;

// ═══════════════════════════════════════════════════════════════════════════
// CSS_MODE  — lexing the free-form CSS property values
// ═══════════════════════════════════════════════════════════════════════════
// Remains active until a newline or semicolon terminates the CSS value,
// then returns to DEFAULT_MODE.

mode CSS_MODE;

CSS_TEXT_MORE : ~[\r\n;%]+              -> type(CSS_VALUE_START)             ;
CSS_SEMI      : ';'                     -> type(SEMI),   mode(DEFAULT_MODE) ;
CSS_NL        : ('\r\n'|'\r'|'\n')      -> type(NEWLINE), mode(DEFAULT_MODE) ;
CSS_WS        : [ \t]+                  -> skip                              ;
