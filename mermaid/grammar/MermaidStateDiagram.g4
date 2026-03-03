// MermaidStateDiagram.g4
// ANTLR4 grammar for Mermaid State Diagrams
// Reference: https://mermaid.ai/open-source/syntax/stateDiagram.html  (v11.12)
//
// Diagram types:
//   stateDiagram       — v1 renderer (legacy)
//   stateDiagram-v2    — v2 renderer (current default)
//
// ── State declarations ────────────────────────────────────────────────────
//   StateId                            bare id (implicit rectangle state)
//   state "label" as StateId           explicit label, separate id
//   state StateId : description        inline colon-description
//   state StateId <<choice>>           choice pseudostate
//   state StateId <<fork>>             fork pseudostate
//   state StateId <<join>>             join pseudostate
//   StateId:::className                class shorthand on bare declaration
//
// ── Special pseudo-states ─────────────────────────────────────────────────
//   [*]                                start or end state
//                                      (direction inferred from transition)
//
// ── Transitions ───────────────────────────────────────────────────────────
//   StateA --> StateB
//   StateA --> StateB : label
//   [*]    --> StateA
//   StateA --> [*]
//   StateA:::cls --> StateB:::cls : label
//
// ── Composite states ──────────────────────────────────────────────────────
//   state "label" as StateId {
//       statement*
//   }
//   state StateId {
//       statement*
//   }
//   Concurrent regions inside composites are separated by:
//   --
//
// ── Stereotypes ───────────────────────────────────────────────────────────
//   state StateId <<choice>>
//   state StateId <<fork>>
//   state StateId <<join>>
//
// ── Notes ─────────────────────────────────────────────────────────────────
//   note right of StateId : single-line text
//   note left of StateId  : single-line text
//   note right of StateId
//       multi-line
//       text
//   end note
//
// ── Direction ─────────────────────────────────────────────────────────────
//   direction TB | TD | BT | LR | RL
//
// ── Styling ───────────────────────────────────────────────────────────────
//   classDef name  fill:#f00,color:white,...
//   classDef name1,name2  font-style:italic
//   class StateId className
//   class StateA,StateB className
//
// ── Comments ──────────────────────────────────────────────────────────────
//   %% anything to end of line
//
// ── Key lexer ordering notes ──────────────────────────────────────────────
//   1. KW_STATE_DIAGRAM_V2  before KW_STATE_DIAGRAM  (longer literal wins)
//   2. START_END  '[*]'     before LBRACK  '[' (so [*] is one token)
//   3. STEREOTYPE '<<...>>' before LT '<'  (so <<choice>> is one token)
//   4. TRANSITION '-->'     before CONCURRENCY '--' before MINUS '-'
//   5. TRIPLE_COLON ':::'   before COLON ':'
//   6. KW_END_NOTE uses inline [ \t]* fragment (WS is skip-channel, unreferenceable)
//   7. All keyword tokens   before ID

grammar MermaidStateDiagram;

// ═══════════════════════════════════════════════════════════════════════════
// PARSER RULES
// ═══════════════════════════════════════════════════════════════════════════

diagram
    : NEWLINE* diagramType NEWLINE+
      statement*
      EOF
    ;

diagramType
    : KW_STATE_DIAGRAM_V2
    | KW_STATE_DIAGRAM
    ;

// ── Top-level statement dispatcher ────────────────────────────────────────

statement
    : stateDecl       NEWLINE+
    | transitionStmt  NEWLINE+
    | compositeBlock           // self-terminating (ends with '}' NEWLINE)
    | noteBlock                // self-terminating (ends with 'end note' NEWLINE)
    | concurrencyDiv  NEWLINE+ // -- divider between parallel regions
    | directionStmt   NEWLINE+
    | classDefStmt    NEWLINE+
    | classAssignStmt NEWLINE+
    | COMMENT         NEWLINE+
    | NEWLINE+
    ;

// ─────────────────────────────────────────────────────────────────────────
// STATE DECLARATIONS
//
// Form 1:  StateId                         bare id (implicit state)
// Form 2:  state "label" as StateId        label as id
// Form 3:  state StateId : description     id : description
// Form 4:  state StateId <<stereo>>        stereotype declaration
//
// Class shorthand (:::name) is valid on forms 1–3.
// ─────────────────────────────────────────────────────────────────────────

stateDecl
    // Form 2 — most specific, check first (has both QUOTED_STRING and KW_AS)
    : KW_STATE QUOTED_STRING KW_AS stateId classShorthand?
    // Form 3 — id followed by colon and description
    | KW_STATE stateId COLON descriptionText classShorthand?
    // Form 4 — stereotype (choice / fork / join)
    | KW_STATE stateId STEREOTYPE
    // Form 1 — bare id (with optional class shorthand)
    | stateId classShorthand?
    ;

// A state id is a plain identifier.
// [*] is not a stateId in a declaration (only in transitions).
stateId
    : ID
    ;

// ── Description text ──────────────────────────────────────────────────────
// Free-form text after "state id :" — runs to end of line.
// Represented as one or more FREE_TEXT tokens so the visitor can join them.

descriptionText
    : FREE_TEXT+
    ;

// ── Class shorthand :::className ─────────────────────────────────────────

classShorthand
    : TRIPLE_COLON ID
    ;

// ─────────────────────────────────────────────────────────────────────────
// TRANSITION STATEMENT
//
//   StateA --> StateB
//   StateA --> StateB : label
//   [*]    --> StateA
//   StateA --> [*]
//   StateA:::cls --> StateB:::cls : label
//
// Both endpoints may be the start/end pseudo-state [*] or a normal stateId.
// ─────────────────────────────────────────────────────────────────────────

transitionStmt
    : stateRef TRANSITION stateRef ( COLON transitionLabel )?
    ;

// A state reference in a transition: stateId or [*], each optionally with
// a class shorthand.
stateRef
    : stateId classShorthand?
    | START_END classShorthand?
    ;

// Transition label: free-form text to end of line.
transitionLabel
    : FREE_TEXT+
    ;

// ─────────────────────────────────────────────────────────────────────────
// COMPOSITE STATE BLOCK
//
//   state "label" as StateId {
//       compositeBody
//   }
//   state StateId {
//       compositeBody
//   }
//
// The body contains zero or more statements, which may include nested
// composites (arbitrary nesting depth).  Concurrent regions inside the body
// are separated by concurrencyDiv statements (the -- token).
// ─────────────────────────────────────────────────────────────────────────

compositeBlock
    : KW_STATE QUOTED_STRING KW_AS stateId LBRACE NEWLINE+
          statement*
      RBRACE NEWLINE+
    | KW_STATE stateId LBRACE NEWLINE+
          statement*
      RBRACE NEWLINE+
    ;

// Concurrency divider -- between parallel regions inside a composite.
concurrencyDiv
    : CONCURRENCY
    ;

// ─────────────────────────────────────────────────────────────────────────
// NOTE BLOCK
//
// Single-line form:
//   note right of StateId : text to end of line
//   note left of StateId  : text to end of line
//
// Multi-line form:
//   note right of StateId
//       line one
//       line two
//   end note
//
// The noteSide keyword (right / left) is followed by the keyword "of".
// ─────────────────────────────────────────────────────────────────────────

noteBlock
    // Single-line: colon separates header from text content
    : KW_NOTE noteSide KW_OF stateId COLON noteLineContent NEWLINE+
    // Multi-line: header on its own line, body lines, terminated by "end note"
    | KW_NOTE noteSide KW_OF stateId NEWLINE+
          noteBodyLine+
      KW_END_NOTE NEWLINE+
    ;

noteSide
    : KW_RIGHT
    | KW_LEFT
    ;

// Content on the same line as the note colon.
noteLineContent
    : FREE_TEXT+
    ;

// One line of multi-line note body.  FREE_TEXT catches all content including
// spaces; each body line ends with NEWLINE.
noteBodyLine
    : FREE_TEXT+ NEWLINE+
    | NEWLINE+               // blank lines inside multi-line note are valid
    ;

// ─────────────────────────────────────────────────────────────────────────
// DIRECTION STATEMENT
//   direction TB | TD | BT | LR | RL
// ─────────────────────────────────────────────────────────────────────────

directionStmt
    : KW_DIRECTION direction
    ;

direction
    : DIR_TB | DIR_TD | DIR_BT | DIR_LR | DIR_RL
    ;

// ─────────────────────────────────────────────────────────────────────────
// STYLING STATEMENTS
//
//   classDef name  fill:#f00,color:white,stroke:yellow
//   classDef name1,name2  font-style:italic
//   class StateId  className
//   class StateA,StateB  className
// ─────────────────────────────────────────────────────────────────────────

classDefStmt
    : KW_CLASSDEF classNameList cssString
    ;

classNameList
    : ID ( COMMA ID )*
    ;

classAssignStmt
    : KW_CLASS stateIdList ID
    ;

stateIdList
    : ID ( COMMA ID )*
    ;

// CSS string: free-form to end of line, optional trailing semicolon.
cssString
    : CSS_TEXT+ SEMI?
    ;


// ═══════════════════════════════════════════════════════════════════════════
// LEXER RULES
// ═══════════════════════════════════════════════════════════════════════════
//
// Ordering:
//   1.  KW_STATE_DIAGRAM_V2  before KW_STATE_DIAGRAM  (longer literal wins)
//   2.  START_END  '[*]'     before LBRACK '['
//   3.  STEREOTYPE '<<...>>' before any single-char token
//   4.  TRANSITION '-->'     before CONCURRENCY '--'
//   5.  TRIPLE_COLON ':::'   before COLON ':'
//   6.  All keyword tokens   before ID

// ── Diagram type ──────────────────────────────────────────────────────────
// v2 must be declared first — it is longer and would otherwise partially
// match KW_STATE_DIAGRAM leaving "-v2" to cause a lex error.

KW_STATE_DIAGRAM_V2 : 'stateDiagram-v2' ;
KW_STATE_DIAGRAM    : 'stateDiagram' ;

// ── Statement keywords ────────────────────────────────────────────────────

KW_STATE     : 'state' ;
KW_AS        : 'as' ;
KW_DIRECTION : 'direction' ;
KW_CLASSDEF  : 'classDef' ;
KW_CLASS     : 'class' ;
KW_NOTE      : 'note' ;
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
COLON  : ':' ;
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

// ── CSS text ──────────────────────────────────────────────────────────────
// Content of classDef statements.  Same stop conditions as FREE_TEXT but
// also stops at semicolon (which is an explicit terminator for CSS lists).
// Because both CSS_TEXT and FREE_TEXT match the same character class, and
// ANTLR picks the first-declared rule on a tie, CSS_TEXT must be declared
// BEFORE FREE_TEXT.

CSS_TEXT
    : ~[\r\n;%%]+
    ;

// ── Free-form text ────────────────────────────────────────────────────────
// Used for: state descriptions (after id :), transition labels (after -->:),
// and note content (single-line and multi-line body).
//
// Design: rather than three separate identically-patterned tokens (which would
// all match the same input and make ANTLR pick the first-declared one
// regardless of context), we use a single FREE_TEXT token.  The parser rules
// (descriptionText, transitionLabel, noteLineContent, noteBodyLine) all
// reference FREE_TEXT, relying on the same token type in each context.
// The visitor knows from the rule context what kind of text it is reading.
//
// FREE_TEXT matches any sequence of non-newline, non-comment-start characters
// that is not solely whitespace (WS -> skip handles whitespace between tokens,
// but FREE_TEXT starts after a non-whitespace character is found).
//
// Note: FREE_TEXT is intentionally broad.  It may match things like "end" or
// "note" when they appear in the middle of a note body.  This is correct
// because keyword tokens (KW_END_NOTE, etc.) are declared first and will
// consume those sequences when they appear at the start of a line.
//
// Stops at: end-of-line (\r \n) and comment-start (%%).

FREE_TEXT
    : ~[\r\n%%]+
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
