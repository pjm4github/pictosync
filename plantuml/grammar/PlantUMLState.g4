// PlantUMLState.g4
// ANTLR4 grammar for PlantUML State Diagrams
// Reference: https://plantuml.com/state-diagram
//
// ── Diagram wrapper ───────────────────────────────────────────────────────
//   @startuml [filename]
//   ...statements...
//   @enduml
//
// ── State declarations ────────────────────────────────────────────────────
//   state Name                          simple state (implicit)
//   state "Long Name"                   quoted name
//   state "Long Name" as alias          quoted name with alias
//   state alias as "Long Name"          alias first, then quoted name
//   state Name <<stereotype>>           with stereotype
//   state Name #color                   with background color
//   state Name ##[style]color           with border style/color
//   state Name #bg ##[style]border      both bg and border specs
//   state Name #color;line:color;line.bold;text:color   semicolon style syntax
//   state A.B                           dotted composite reference
//
// ── Composite state ───────────────────────────────────────────────────────
//   state Name {
//     ...statements...
//     --                               horizontal concurrent region separator
//     ||                               vertical concurrent region separator
//   }
//   state Name #color {  }             composite with inline color
//
// ── State description (label) ─────────────────────────────────────────────
//   StateName : description text       label line for a state
//
// ── Pseudo-states ─────────────────────────────────────────────────────────
//   [*]       start or end (direction from arrow)
//   [H]       shallow history
//   [H*]      deep history
//
// ── Stereotypes ───────────────────────────────────────────────────────────
//   <<start>>  <<end>>  <<choice>>  <<fork>>  <<join>>
//   <<history>>  <<history*>>  <<sdlreceive>>
//   <<entryPoint>>  <<exitPoint>>
//   <<inputPin>>  <<outputPin>>
//   <<expansionInput>>  <<expansionOutput>>
//   <<anyCustomName>>    (open-ended)
//
// ── Transition statements ─────────────────────────────────────────────────
//   A --> B                            default (vertical) arrow
//   A -> B                             horizontal arrow
//   A --> B : label                    with label
//   A -up-> B                          direction hint
//   A -down-> B  A -left-> B  A -right-> B
//   A -u-> B  -d-> -l-> -r->           single-char abbreviated direction
//   A -do-> B  -le-> -ri->             two-char abbreviated direction
//   A -[#color]-> B                    inline color
//   A -[#color,dashed]-> B             inline color and style
//   A -[dashed]-> B                    inline style only
//   A -up[#color]-> B                  direction + color
//   A -[hidden]-> B                    hidden/invisible arrow (layout hint)
//   [*] --> A   A --> [*]              to/from pseudo-states
//   A --> State3[H*]: label            deep history target
//
// ── Note statements ───────────────────────────────────────────────────────
//   note left of X : text              single-line positional note
//   note right of X : text
//   note top of X : text
//   note bottom of X : text
//   note left of X                     multi-line positional note
//     ...body...
//   end note
//   note "text" as N                   inline floating note
//   note on link                       note on the most recent transition
//     ...body...
//   end note
//
// ── Global directives ─────────────────────────────────────────────────────
//   hide empty description
//   left to right direction
//   top to bottom direction
//   scale N [width|height]
//   title text
//   header text
//   footer text
//   caption text
//   skinparam key value
//   skinparam SectionName { key value }
//   !pragma key value
//
// ── Style block ───────────────────────────────────────────────────────────
//   <style>
//     ...CSS-like content...
//   </style>
//
// ── Comments ──────────────────────────────────────────────────────────────
//   ' single-line comment
//   /' multi-line comment '/
//
// ── Lexer ordering notes ──────────────────────────────────────────────────
//   1. STARTUML / ENDUML before any other token
//   2. DEEP_HISTORY '[H*]' before HISTORY '[H]' before PSEUDO_STATE '[*]'
//      All three before LBRACK '['
//   3. STEREO_OPEN '<<'  before LT '<'
//   4. CONCURRENT_H '--'  and CONCURRENT_V '||' declared in context;
//      TRANSITION_ARROW token covers all --> / -> / -dir-> variants
//   5. STYLE_BLOCK '<style>' ... '</style>' as one composite token
//   6. INLINE_STYLE '#...##...' or '#...;...' captured as COLOR_STYLE token
//   7. KW_END_NOTE / KW_END_LEGEND before KW_END
//   8. All keyword tokens before ID

grammar PlantUMLState;

// ═══════════════════════════════════════════════════════════════════════════
// PARSER RULES
// ═══════════════════════════════════════════════════════════════════════════

diagram
    : NEWLINE* STARTUML filenameHint? NEWLINE+
      statement*
      ENDUML NEWLINE*
      EOF
    ;

filenameHint
    : ( ID | INT )+ ( '.' ( ID | INT )+ )*
    | QUOTED_STRING
    ;

// ── Generic rest-of-line — consumes mixed tokens until NEWLINE ───────────
// Used for label text, descriptions, skinparam values, note bodies, etc.

restOfLine
    : ( ID | QUOTED_STRING | INT | COLOR_STYLE | FREE_TEXT
      | COLON | BANG | LBRACK | RBRACK
      | PSEUDO_STATE | HISTORY | DEEP_HISTORY | STEREO
      | TRANSITION_ARROW | CONCURRENT_H | CONCURRENT_V
      | DOTTED_ID
      | KW_STATE | KW_AS | KW_NOTE | KW_ON | KW_LINK
      | KW_LEFT | KW_RIGHT | KW_TOP | KW_BOTTOM | KW_OF
      | KW_HIDE | KW_SHOW | KW_TO | KW_DIRECTION
      | KW_SCALE | KW_TITLE | KW_HEADER | KW_FOOTER | KW_CAPTION
      | KW_SKINPARAM | KW_PRAGMA | KW_END
      )+
    ;

// ── Statement dispatcher ──────────────────────────────────────────────────

statement
    : stateDecl        NEWLINE+
    | compositeBlock               // self-terminating with '}'
    | transitionStmt   NEWLINE+
    | descriptionStmt  NEWLINE+    // StateName : description
    | concurrentSep    NEWLINE+    // -- or || inside composite body
    | noteStmt         NEWLINE+
    | noteBlock                    // multi-line note, self-terminating
    | noteLinkBlock                // note on link ... end note
    | hideStmt         NEWLINE+
    | directionStmt    NEWLINE+
    | scaleStmt        NEWLINE+
    | titleStmt        NEWLINE+
    | headerStmt       NEWLINE+
    | footerStmt       NEWLINE+
    | captionStmt      NEWLINE+
    | skinparamStmt    NEWLINE+
    | skinparamBlock               // self-terminating with '}'
    | styleBlock                   // <style>...</style>
    | pragmaStmt       NEWLINE+
    | COMMENT_SINGLE   NEWLINE+
    | COMMENT_MULTI    NEWLINE+
    | NEWLINE+
    ;

// ═══════════════════════════════════════════════════════════════════════════
// STATE DECLARATIONS
//
// Form 1:  state Name                simple (implicit) state
// Form 2:  state "Long Name"         quoted name, no alias
// Form 3:  state "Long Name" as id   quoted name with alias
// Form 4:  state id as "Long Name"   alias first, then quoted name
// Form 5:  state Name <<stereo>>     any stereotype
// Form 6:  state Name #color ...     inline color/style
// Form 7:  state A.B                 dotted composite reference
//
// All forms may carry colorStyle and/or stereotype modifiers.
// ═══════════════════════════════════════════════════════════════════════════

stateDecl
    : KW_STATE stateName aliasClause? colorStyle? stereotypeClause? ( COLON restOfLine )?
    ;

stateName
    : QUOTED_STRING
    | DOTTED_ID       // A.B  composite reference
    | ID
    ;

aliasClause
    : KW_AS stateName
    ;

// ── Inline color and style specification ──────────────────────────────────
// PlantUML state supports two inline style syntaxes:
//
//   Syntax A:  #bg  ##[style]border
//     #red-green         gradient bg
//     #red|green         split bg
//     #pink              solid bg
//     ##[dashed]blue     border style + color
//     ##[dotted]blue
//     ##[bold]
//     ##00FFFF           border color only
//
//   Syntax B:  #bg;line:color;line.bold;text:color
//     #pink;line:red;line.bold;text:red
//
// Both forms are captured as a single COLOR_STYLE token by the lexer,
// which starts with '#'.  The visitor parses the token content.

colorStyle
    : COLOR_STYLE
    ;

// ── Stereotype clause ─────────────────────────────────────────────────────
// <<name>>  where name is any identifier (including 'history*' with asterisk)
// The STEREO token captures the full <<...>> including the delimiters.

stereotypeClause
    : STEREO
    ;

// ═══════════════════════════════════════════════════════════════════════════
// COMPOSITE STATE BLOCK
//
//   state Name [colorStyle] [<<stereo>>] {
//       statements*
//   }
// ═══════════════════════════════════════════════════════════════════════════

compositeBlock
    : KW_STATE stateName aliasClause? colorStyle? stereotypeClause?
      LBRACE NEWLINE+
          statement*
      RBRACE NEWLINE+
    ;

// ── Concurrent region separators (inside composite body) ──────────────────
// '--' separates horizontal concurrent regions
// '||' separates vertical concurrent regions

concurrentSep
    : CONCURRENT_H
    | CONCURRENT_V
    ;

// ═══════════════════════════════════════════════════════════════════════════
// TRANSITION STATEMENTS
//
//   source arrowSpec target [: label]
//
// source and target can be:
//   StateId          — bare or dotted identifier
//   "Quoted"         — quoted name
//   [*]              — start/end pseudo-state
//   [H]              — shallow history
//   [H*]             — deep history
//   StateId[H*]      — history target appended to state id (no space)
//
// arrowSpec: captured as a single TRANSITION_ARROW token (see below).
// ═══════════════════════════════════════════════════════════════════════════

transitionStmt
    : transitionEnd TRANSITION_ARROW transitionEnd ( COLON restOfLine )?
    ;

transitionEnd
    : PSEUDO_STATE          // [*]
    | HISTORY               // [H]
    | DEEP_HISTORY          // [H*]
    | ID DEEP_HISTORY       // StateId[H*]
    | ID HISTORY            // StateId[H]
    | DOTTED_ID             // A.B
    | QUOTED_STRING
    | ID
    ;

// ═══════════════════════════════════════════════════════════════════════════
// STATE DESCRIPTION STATEMENT
//
//   StateName : description text
//   "QuotedName" : description
//   alias : description
//
// Adds a label line to an existing state (standalone, not inside a block).
// ═══════════════════════════════════════════════════════════════════════════

descriptionStmt
    : stateRef COLON restOfLine
    ;

stateRef
    : DOTTED_ID
    | QUOTED_STRING
    | ID
    ;

// ═══════════════════════════════════════════════════════════════════════════
// NOTE STATEMENTS
//
// Positional single-line:
//   note left of X : text
//   note right of X : text
//   note top of X : text
//   note bottom of X : text
//
// Inline floating:
//   note "text" as N
//
// Positional multi-line (noteBlock):
//   note left of X
//     ...
//   end note
//
// Note on link (noteLinkBlock):
//   note on link
//     ...
//   end note
// ═══════════════════════════════════════════════════════════════════════════

noteStmt
    : KW_NOTE noteSide KW_OF stateRef ( COLON restOfLine )?
    | KW_NOTE QUOTED_STRING KW_AS ID
    ;

noteBlock
    : KW_NOTE noteSide KW_OF stateRef NEWLINE+
          noteBodyLine+
      KW_END_NOTE NEWLINE+
    ;

noteLinkBlock
    : KW_NOTE KW_ON KW_LINK NEWLINE+
          noteBodyLine+
      KW_END_NOTE NEWLINE+
    ;

noteSide
    : KW_LEFT | KW_RIGHT | KW_TOP | KW_BOTTOM
    ;

noteBodyLine
    : restOfLine NEWLINE+
    | NEWLINE+
    ;

// ═══════════════════════════════════════════════════════════════════════════
// HIDE / SHOW DIRECTIVES
//
//   hide empty description
//   hide <<stereotype>>
//   show <<stereotype>>
// ═══════════════════════════════════════════════════════════════════════════

hideStmt
    : ( KW_HIDE | KW_SHOW ) restOfLine
    ;

// ═══════════════════════════════════════════════════════════════════════════
// DIRECTION, SCALE, TITLE, HEADER, FOOTER, CAPTION
// ═══════════════════════════════════════════════════════════════════════════

directionStmt
    : KW_LEFT  KW_TO KW_RIGHT KW_DIRECTION
    | KW_TOP   KW_TO KW_BOTTOM KW_DIRECTION
    ;

scaleStmt
    : KW_SCALE restOfLine
    ;

titleStmt   : KW_TITLE   restOfLine? ;
headerStmt  : KW_HEADER  restOfLine? ;
footerStmt  : KW_FOOTER  restOfLine? ;
captionStmt : KW_CAPTION restOfLine? ;

// ═══════════════════════════════════════════════════════════════════════════
// SKINPARAM
//
//   skinparam paramName value
//   skinparam SectionName { key value ... }
// ═══════════════════════════════════════════════════════════════════════════

skinparamStmt
    : KW_SKINPARAM skinparamName restOfLine?
    ;

skinparamBlock
    : KW_SKINPARAM skinparamName LBRACE NEWLINE+
          skinparamEntry*
      RBRACE NEWLINE+
    ;

// Skinparam name — can be ID or a keyword like 'state', 'note', etc.
skinparamName
    : ID
    | KW_STATE | KW_NOTE
    ;

skinparamEntry
    : skinparamName restOfLine NEWLINE+
    | NEWLINE+
    ;

// ═══════════════════════════════════════════════════════════════════════════
// STYLE BLOCK
//
//   <style>
//     stateDiagram { ... }
//     diamond { ... }
//   </style>
//
// The entire block from <style> to </style> is captured as STYLE_BLOCK.
// ═══════════════════════════════════════════════════════════════════════════

styleBlock
    : STYLE_BLOCK NEWLINE+
    ;

// ── Pragma ────────────────────────────────────────────────────────────────

pragmaStmt
    : BANG KW_PRAGMA ID restOfLine?
    | BANG ID restOfLine?
    ;


// ═══════════════════════════════════════════════════════════════════════════
// LEXER RULES
// ═══════════════════════════════════════════════════════════════════════════
//
// Critical ordering:
//   1.  STARTUML / ENDUML        — longest first, before ID
//   2.  DEEP_HISTORY '[H*]'      — before HISTORY '[H]'
//   3.  HISTORY '[H]'            — before PSEUDO_STATE '[*]'
//   4.  PSEUDO_STATE '[*]'       — before LBRACK '['
//   5.  STEREO '<<...>>'         — before any '<' token
//   6.  TRANSITION_ARROW         — composite token, covers all arrow variants
//   7.  CONCURRENT_H '--'        — before DASH '-'
//   8.  CONCURRENT_V '||'        — before PIPE '|'
//   9.  COLOR_STYLE '#...'       — before HASH '#' (if standalone)
//  10.  DOTTED_ID 'A.B'          — before ID (only matches name.name pattern)
//  11.  KW_END_NOTE 'end note'   — before KW_END 'end'
//  12.  STYLE_BLOCK '<style>...</style>' — composite token, before LT '<'
//  13.  All keyword tokens        — before ID

// ── Diagram wrappers ──────────────────────────────────────────────────────

STARTUML : '@startuml' ;
ENDUML   : '@enduml' ;

// ── Pseudo-state tokens ───────────────────────────────────────────────────
// Declared longest-first; all before LBRACK.

DEEP_HISTORY : '[H*]' ;
HISTORY      : '[H]' ;
PSEUDO_STATE : '[*]' ;

// ── Stereotype token ──────────────────────────────────────────────────────
// Captures << anything >> as one token, including 'history*' with asterisk.
// Must be before any standalone '<' character token.

STEREO
    : '<<' [ \t]* ~[>\r\n]+ [ \t]* '>>'
    ;

// ── Style block token ─────────────────────────────────────────────────────
// Captures the entire <style>...</style> block as one opaque token.
// Must be before any standalone '<' token.

STYLE_BLOCK
    : '<style>' .*? '</style>'
    ;

// ── Transition arrow token ────────────────────────────────────────────────
// Covers all PlantUML state diagram transition arrow variants:
//
//   -->          default vertical solid arrow
//   ->           horizontal solid arrow
//   -up->        direction hint: up | down | left | right
//   -u->         single-char: u | d | l | r
//   -do->        two-char: do | le | ri
//   -[#color]->  inline color
//   -[#c,style]->  inline color + style (dashed, dotted, bold, hidden)
//   -[style]->   inline style only
//   -up[#color]->  direction + color
//   All of the above with reversed head (<-- variants)
//
// Fragment helpers:

fragment F_DIR
    : 'up' | 'down' | 'left' | 'right'
    | 'do' | 'le' | 'ri'
    | 'u' | 'd' | 'l' | 'r'
    ;

// Inline style modifier: [#color] [#color,dashed] [dashed] [hidden] etc.
fragment F_INLINE_STYLE
    : '[' ~[\]\r\n]* ']'
    ;

// Complete transition arrow — captures all combinations.
// Left-head variants first (longer patterns before shorter).
TRANSITION_ARROW
    : '<' '-' F_DIR? F_INLINE_STYLE? '-'? '>'?   // <- <-up-> etc.
    | '-' F_DIR? F_INLINE_STYLE? '-'? '>'         // -> -up-> -[#red]->
    | '-' F_DIR? F_INLINE_STYLE? '--' '>'?         // --> -up-->
    | '<' '--' F_DIR? F_INLINE_STYLE? '-'? '>'?   // <-- <--up->
    ;

// ── Concurrent region separators ─────────────────────────────────────────
// Must be declared before DASH '-' and PIPE '|'.

CONCURRENT_H : '--' ;
CONCURRENT_V : '||' ;

// ── Color style token ─────────────────────────────────────────────────────
// Captures inline state color/style specifications starting with '#':
//   #pink
//   #red-green          gradient
//   #red|green          split
//   #pink;line:red;line.bold;text:red   semicolon form
//   #pink ##[dashed]blue   bg + border (two # groups on same declaration)
// Declared before a standalone HASH '#' so the full color spec wins.

COLOR_STYLE
    : '#' [a-zA-Z0-9\-|;:.#[\]]*
    ;

// ── Declaration keywords ──────────────────────────────────────────────────

KW_STATE     : 'state' ;
KW_AS        : 'as' ;

// ── Note keywords ─────────────────────────────────────────────────────────
// Compound 'end note' / 'end legend' before bare 'end'.

KW_END_NOTE  : 'end' [ \t]+ 'note' ;
KW_END       : 'end' ;
KW_NOTE      : 'note' ;
KW_ON        : 'on' ;
KW_LINK      : 'link' ;
KW_LEFT      : 'left' ;
KW_RIGHT     : 'right' ;
KW_TOP       : 'top' ;
KW_BOTTOM    : 'bottom' ;
KW_OF        : 'of' ;

// ── Visibility ────────────────────────────────────────────────────────────

KW_HIDE      : 'hide' ;
KW_SHOW      : 'show' ;

// ── Direction statement ───────────────────────────────────────────────────

KW_TO        : 'to' ;
KW_DIRECTION : 'direction' ;

// ── Other directives ──────────────────────────────────────────────────────

KW_SCALE     : 'scale' ;
KW_TITLE     : 'title' ;
KW_HEADER    : 'header' ;
KW_FOOTER    : 'footer' ;
KW_CAPTION   : 'caption' ;
KW_SKINPARAM : 'skinparam' ;
KW_PRAGMA    : 'pragma' ;

// ── Dotted composite state reference ─────────────────────────────────────
// Matches A.B or A.B.C patterns — declared before ID so dotted form wins.

DOTTED_ID
    : [a-zA-Z_][a-zA-Z0-9_]* ( '.' [a-zA-Z_][a-zA-Z0-9_]* )+
    ;

// ── Quoted string ─────────────────────────────────────────────────────────

QUOTED_STRING
    : '"' ( '\\' '"' | ~["\r\n] )* '"'
    ;

// ── Punctuation ───────────────────────────────────────────────────────────

LBRACE  : '{' ;
RBRACE  : '}' ;
LBRACK  : '[' ;
RBRACK  : ']' ;
COLON   : ':' ;
BANG    : '!' ;

// ── Integer ───────────────────────────────────────────────────────────────

INT : [0-9]+ ;

// ── Identifier ────────────────────────────────────────────────────────────
// Declared after all keyword tokens.

ID
    : [a-zA-Z_] [a-zA-Z0-9_]*
    ;

// ── Comments ──────────────────────────────────────────────────────────────

COMMENT_SINGLE
    : ['] ~[\r\n]*
    ;

COMMENT_MULTI
    : '/' ['] .*? ['] '/'
    ;

// ── Free text ─────────────────────────────────────────────────────────────
// Catch-all for transition labels, description text, skinparam values, etc.
// Declared last so all structural tokens have priority.

// Free text — must NOT start with a character that could begin a structural
// token (letter, digit, quote, bracket, paren, #, <, @, !, {, }, :, ').
// This prevents FREE_TEXT from consuming keyword-led lines.
FREE_TEXT
    : ~[a-zA-Z0-9_"'()[\]{}<>#$@!:,*/~=\-.\r\n \t|] ~[\r\n]*
    | [&%^;?\\`+] ~[\r\n]*
    ;

// ── Newline ───────────────────────────────────────────────────────────────

NEWLINE
    : [\r\n]+
    ;

// ── Whitespace ────────────────────────────────────────────────────────────

WS
    : [ \t]+ -> skip
    ;
