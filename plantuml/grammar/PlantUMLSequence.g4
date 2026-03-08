// PlantUMLSequence.g4
// ANTLR4 grammar for PlantUML Sequence Diagrams
// Reference: https://plantuml.com/sequence-diagram
//
// ── Diagram wrapper ───────────────────────────────────────────────────────
//   @startuml [filename]
//   ...statements...
//   @enduml
//
// ── Participant declarations ──────────────────────────────────────────────
//   participant  Name [as Alias] [#color] [order N] [<<stereotype>>] [multiBody]
//   actor        Name [as Alias] [#color] [order N] [<<stereotype>>]
//   boundary     Name [as Alias] [#color] [order N] [<<stereotype>>]
//   control      Name [as Alias] [#color] [order N] [<<stereotype>>]
//   entity       Name [as Alias] [#color] [order N] [<<stereotype>>]
//   database     Name [as Alias] [#color] [order N] [<<stereotype>>]
//   collections  Name [as Alias] [#color] [order N] [<<stereotype>>]
//   queue        Name [as Alias] [#color] [order N] [<<stereotype>>]
//   create       participantType? Name
//
// ── Participant name forms ────────────────────────────────────────────────
//   Alice           bare identifier
//   "Bob()"         quoted (allows special chars)
//   "Long\nName" as Alias
//
// ── Multiline participant body (participant only) ─────────────────────────
//   participant Foo [
//     = Title
//     ----
//     ""SubTitle""
//   ]
//
// ── Stereotypes ───────────────────────────────────────────────────────────
//   << Generated >>
//   << (C,#ADD1B2) Testable >>
//
// ── Messages ─────────────────────────────────────────────────────────────
//   Alice -> Bob : label
//   Alice --> Bob : label
//   Alice <- Bob : label
//   Alice <-- Bob : label
//   (and all arrow style variants — see arrowSpec below)
//
//   Arrow shafts:    -  (solid)   --  (dotted)
//   Left heads:      <  <<  \  //  x  o
//   Right heads:     >  >>  /  \\  x  o
//   Bidirectional:   <->  <-->
//   Color modifier:  -[#color]-  between shaft chars and head
//   Lost/found:      ->x  ->o  (also with dotted)
//
//   Incoming (from left boundary):   [->  [-->  [<-  [<--
//   Outgoing (to right boundary):    ->]  -->]  <-]  <--]
//   Short (off-screen):              ?->  ?-->  ->?  -->?
//
// ── Lifeline shorthand suffixes (after target participant on message) ─────
//   ++  activate target [#color]
//   --  deactivate source
//   **  create target
//   !!  destroy target
//
// ── Lifeline control statements ───────────────────────────────────────────
//   activate   Participant [#color]
//   deactivate Participant
//   destroy    Participant
//   return     [label]
//   autoactivate on|off
//
// ── Grouping / fragment blocks ────────────────────────────────────────────
//   alt [label]
//     ...
//   else [label]
//     ...
//   end
//
//   opt [label]   ...  end
//   loop [label]  ...  end
//   par [label]   ...  end
//   break [label] ...  end
//   critical [label] ... end
//
//   group Label [secondary label in brackets]
//     ...
//   end
//
//   partition Label
//     ...
//   end
//
// ── Notes ─────────────────────────────────────────────────────────────────
//   note left : text
//   note right : text
//   note left of Participant [#color] : text
//   note right of Participant [#color] : text
//   note over Participant[, Participant] [#color] : text
//   note across : text
//   / note ...                          (aligned with previous note)
//   hnote over ...                      (hexagonal note)
//   rnote over ...                      (rectangular note)
//   Multi-line forms: end note | endnote | endrnote | endhnote
//
// ── Reference ─────────────────────────────────────────────────────────────
//   ref over Participant[, Participant] : text
//   ref over Participant
//     multi-line
//   end ref
//
// ── Dividers / spacers ────────────────────────────────────────────────────
//   == section title ==
//   ...                    (delay, no label)
//   ... text ...           (delay with label)
//   |||                    (extra vertical space, default)
//   ||N||                  (extra vertical space, N pixels)
//
// ── Autonumber ────────────────────────────────────────────────────────────
//   autonumber
//   autonumber N
//   autonumber N N
//   autonumber "format"
//   autonumber N "format"
//   autonumber N N "format"
//   autonumber stop
//   autonumber resume [N] ["format"]
//   autonumber inc A
//   autonumber inc B
//   autonumber 1.1.1       (hierarchical: dot/semicolon/comma/colon delimited)
//
// ── Title / header / footer ───────────────────────────────────────────────
//   title text
//   title
//     multi-line
//   end title
//   header text
//   footer text
//
// ── Box ───────────────────────────────────────────────────────────────────
//   box ["title"] [#color]
//     participant declarations
//   end box
//
// ── Page split ────────────────────────────────────────────────────────────
//   newpage [title]
//   ignore newpage
//
// ── Anchors and duration (teoz) ───────────────────────────────────────────
//   {anchorId}
//   {anchorId} <-> {anchorId} : label
//
// ── Pragmas and skinparam ─────────────────────────────────────────────────
//   !pragma key value
//   skinparam paramName value
//   hide footbox
//
// ── Comments ──────────────────────────────────────────────────────────────
//   ' single-line comment
//   /' multi-line comment '/
//
// ── Lexer ordering notes ──────────────────────────────────────────────────
//   1. STARTUML '@startuml' and ENDUML '@enduml' before AT '@'
//   2. Arrow tokens: bidirectional before unidirectional; dotted before solid
//      variants listed longest-first within each group.
//   3. DOUBLE_EQ '==' before EQ '='
//   4. DELAY_LINE '...' before DOT '.'
//   5. SPACER '|||' before PIPE '|'
//   6. STEREOTYPE_OPEN '<<' before LT '<'
//   7. STEREOTYPE_CLOSE '>>' before GT '>'
//   8. BLOCK_END_NOTE and variant keywords before END_KW 'end'
//   9. All keyword tokens before ID

grammar PlantUMLSequence;

// ═══════════════════════════════════════════════════════════════════════════
// PARSER RULES
// ═══════════════════════════════════════════════════════════════════════════

diagram
    : NEWLINE* STARTUML filenameHint? NEWLINE+
      statement*
      ENDUML NEWLINE*
      EOF
    ;

// Optional filename after @startuml
filenameHint
    : ID ( DOT ID )*
    | QUOTED_STRING
    ;

// ── Statement dispatcher ──────────────────────────────────────────────────

statement
    : participantDecl NEWLINE+
    | createStmt      NEWLINE+
    | messageStmt     NEWLINE+
    | activateStmt    NEWLINE+
    | deactivateStmt  NEWLINE+
    | destroyStmt     NEWLINE+
    | returnStmt      NEWLINE+
    | autoactivateStmt NEWLINE+
    | autonumberStmt  NEWLINE+
    | groupBlock
    | partitionBlock
    | noteStmt        NEWLINE+
    | noteBlock
    | refStmt         NEWLINE+
    | refBlock
    | boxBlock
    | dividerStmt     NEWLINE+
    | spacerStmt      NEWLINE+
    | titleStmt       NEWLINE+
    | titleBlock
    | headerStmt      NEWLINE+
    | footerStmt      NEWLINE+
    | newpageStmt     NEWLINE+
    | anchorStmt      NEWLINE+
    | durationStmt    NEWLINE+
    | pragmaStmt      NEWLINE+
    | skinparamStmt   NEWLINE+
    | hidestmt        NEWLINE+
    | COMMENT_SINGLE  NEWLINE+
    | COMMENT_MULTI   NEWLINE+
    | NEWLINE+
    ;

// ═══════════════════════════════════════════════════════════════════════════
// PARTICIPANT DECLARATIONS
//
// participant  Name [as Alias] [#color] [order N] [<<stereo>>] [multiBody]
// actor | boundary | control | entity | database | collections | queue
//   Name [as Alias] [#color] [order N] [<<stereo>>]
// ═══════════════════════════════════════════════════════════════════════════

participantDecl
    : participantType participantName
      aliasClause?
      colorSpec?
      orderClause?
      stereotypeClause?
      multiBody?
    ;

participantType
    : KW_PARTICIPANT
    | KW_ACTOR
    | KW_BOUNDARY
    | KW_CONTROL
    | KW_ENTITY
    | KW_DATABASE
    | KW_COLLECTIONS
    | KW_QUEUE
    ;

participantName
    : QUOTED_STRING
    | ID
    ;

aliasClause
    : KW_AS participantName
    ;

colorSpec
    : COLOR        // #red  #FF0000  #LightBlue
    ;

orderClause
    : KW_ORDER INT
    ;

stereotypeClause
    : STEREOTYPE_OPEN stereotypeBody STEREOTYPE_CLOSE
    ;

// Stereotype body: optional spot "(C,#color)" followed by optional text
stereotypeBody
    : spotSpec? freeText?
    ;

spotSpec
    : LPAREN spotChar COMMA colorSpec RPAREN
    ;

spotChar
    : ID       // single letter e.g. C
    | INT
    ;

// Multi-line participant body: [...] with free-form lines inside
multiBody
    : LBRACK NEWLINE+
          multiBodyLine+
      RBRACK
    ;

multiBodyLine
    : FREE_TEXT NEWLINE+
    | NEWLINE+
    ;

// ── create statement ──────────────────────────────────────────────────────
// create [participantType] participantName

createStmt
    : KW_CREATE participantType? participantName
    ;

// ═══════════════════════════════════════════════════════════════════════════
// MESSAGE STATEMENT
//
// Forms:
//   Alice -> Bob : label
//   [-> Alice : label              (incoming from left boundary)
//   Alice ->] : label              (outgoing to right boundary)
//   ?-> Alice : label              (short incoming)
//   Alice ->? : label              (short outgoing)
//
// After the target participant, optional lifeline shorthand suffixes:
//   ++ [#color]    activate target
//   --             deactivate source
//   **             create target
//   !!             destroy target
// These can be combined: --++ or similar.
// ═══════════════════════════════════════════════════════════════════════════

messageStmt
    : messageSource arrowSpec messageTarget lifelineShorthand* ( COLON messageLabel )?
    ;

// Source: participant, left-boundary '[', short-arrow '?', or self-message
messageSource
    : participantRef     // Alice, "Bob()", or alias
    | LBRACK             // [  incoming from left
    | QMARK              // ?  short incoming
    ;

// Target: participant, right-boundary ']', short-arrow '?'
messageTarget
    : participantRef
    | RBRACK             // ]  outgoing to right
    | QMARK              // ?  short outgoing
    ;

// Participant reference in message: quoted or bare id
participantRef
    : QUOTED_STRING
    | ID
    ;

// ── Arrow specification ───────────────────────────────────────────────────
// The arrow encodes: direction, shaft style (solid/dotted), head style,
// and optional color modifier.
//
// Rather than enumerating all combinations as separate parser alternatives
// (which would be hundreds), we use dedicated ARROW_* tokens at the lexer
// level that capture the complete arrow string.  The visitor decodes:
//   - direction (left-to-right vs right-to-left vs bidirectional)
//   - shaft style (solid single-dash vs dotted double-dash)
//   - head style (plain, double, slash, backslash, lost-x, found-o, none)
//   - color (extracted from embedded [#...] if present)

arrowSpec
    : ARROW
    ;

// ── Lifeline shorthand suffixes ───────────────────────────────────────────
// Appear directly after the target participant, before the colon/label.
// Multiple can be combined on one line (e.g. --++).

lifelineShorthand
    : LL_ACTIVATE colorSpec?     // ++  [#color]
    | LL_DEACTIVATE              // --
    | LL_CREATE                  // **
    | LL_DESTROY                 // !!
    ;

// Message label: free text to end of line
messageLabel
    : FREE_TEXT
    ;

// ═══════════════════════════════════════════════════════════════════════════
// LIFELINE CONTROL STATEMENTS
// ═══════════════════════════════════════════════════════════════════════════

activateStmt
    : KW_ACTIVATE participantRef colorSpec?
    ;

deactivateStmt
    : KW_DEACTIVATE participantRef
    ;

destroyStmt
    : KW_DESTROY participantRef
    ;

returnStmt
    : KW_RETURN FREE_TEXT?
    ;

autoactivateStmt
    : KW_AUTOACTIVATE ( KW_ON | KW_OFF )
    ;

// ═══════════════════════════════════════════════════════════════════════════
// AUTONUMBER
//
// autonumber
// autonumber N
// autonumber N N
// autonumber "format"
// autonumber N "format"
// autonumber N N "format"
// autonumber stop
// autonumber resume [N] ["format"]
// autonumber inc A | B
// autonumber 1.1.1  (hierarchical, dot/semicolon/comma/colon delimited)
// ═══════════════════════════════════════════════════════════════════════════

autonumberStmt
    : KW_AUTONUMBER autonumberArgs?
    ;

autonumberArgs
    : KW_STOP
    | KW_RESUME autonumberStart? QUOTED_STRING?
    | KW_INC ( KW_A | KW_B )
    | autonumberStart INT? QUOTED_STRING?
    ;

// Start number: plain integer or hierarchical dotted/delimited form
autonumberStart
    : HIER_NUM    // 1.1.1  or  1;2;3  or  1:2:3  etc.
    | INT
    ;

// ═══════════════════════════════════════════════════════════════════════════
// GROUP / FRAGMENT BLOCKS
//
// alt [label]   else [label]   end
// opt [label]   end
// loop [label]  end
// par [label]   end
// break [label] end
// critical [label] end
// group Label [secondary label in brackets]  end
// ═══════════════════════════════════════════════════════════════════════════

groupBlock
    : groupKeyword groupLabel? NEWLINE+
          statement*
          elseBranch*
      KW_END NEWLINE+
    ;

groupKeyword
    : KW_ALT | KW_OPT | KW_LOOP | KW_PAR
    | KW_BREAK | KW_CRITICAL | KW_GROUP
    ;

groupLabel
    : FREE_TEXT ( LBRACK FREE_TEXT RBRACK )?    // group Label [secondary]
    ;

elseBranch
    : KW_ELSE FREE_TEXT? NEWLINE+
      statement*
    ;

// ── Partition block ───────────────────────────────────────────────────────
//   partition Label
//     ...
//   end

partitionBlock
    : KW_PARTITION FREE_TEXT? NEWLINE+
          statement*
      KW_END NEWLINE+
    ;

// ═══════════════════════════════════════════════════════════════════════════
// NOTE STATEMENTS
//
// Single-line forms (inline after message or standalone):
//   note left : text
//   note right : text
//   note left of Participant [#color] : text
//   note right of Participant [#color] : text
//   note over P [, P] [#color] : text
//   note across : text
//   / note left [of P] [#color] : text   (aligned)
//
// Multi-line forms:
//   note left [of P] [#color]
//     body
//   end note
//   (also hnote / rnote with endhnote / endrnote)
// ═══════════════════════════════════════════════════════════════════════════

// Single-line note on same line
noteStmt
    : noteAlign? noteKeyword notePosition colorSpec? COLON FREE_TEXT
    ;

// Multi-line note block
noteBlock
    : noteAlign? noteKeyword notePosition colorSpec? NEWLINE+
          noteBodyLine+
      noteEndKeyword NEWLINE+
    ;

// Alignment prefix '/' aligns note horizontally with previous note
noteAlign : FSLASH ;

noteKeyword
    : KW_NOTE | KW_HNOTE | KW_RNOTE
    ;

notePosition
    : KW_LEFT                              // note left : text
    | KW_RIGHT                             // note right : text
    | KW_LEFT KW_OF participantRef         // note left of Alice
    | KW_RIGHT KW_OF participantRef        // note right of Alice
    | KW_OVER participantRef ( COMMA participantRef )*  // note over Alice, Bob
    | KW_ACROSS                            // note across
    ;

noteBodyLine
    : FREE_TEXT NEWLINE+
    | NEWLINE+
    ;

noteEndKeyword
    : KW_END_NOTE
    | KW_ENDNOTE
    | KW_ENDRNOTE
    | KW_ENDHNOTE
    ;

// ═══════════════════════════════════════════════════════════════════════════
// REFERENCE
//
//   ref over P[, P] : text
//   ref over P[, P]
//     multi-line
//   end ref
// ═══════════════════════════════════════════════════════════════════════════

refStmt
    : KW_REF KW_OVER participantRef ( COMMA participantRef )* COLON FREE_TEXT
    ;

refBlock
    : KW_REF KW_OVER participantRef ( COMMA participantRef )* NEWLINE+
          noteBodyLine+
      KW_END KW_REF NEWLINE+
    ;

// ═══════════════════════════════════════════════════════════════════════════
// BOX
//
//   box ["title"] [#color]
//     participant declarations / messages
//   end box
// ═══════════════════════════════════════════════════════════════════════════

boxBlock
    : KW_BOX QUOTED_STRING? colorSpec? NEWLINE+
          statement*
      KW_END KW_BOX NEWLINE+
    ;

// ═══════════════════════════════════════════════════════════════════════════
// DIVIDERS AND SPACERS
//
//   == section title ==
//   ...
//   ...label...
//   |||
//   ||N||
// ═══════════════════════════════════════════════════════════════════════════

dividerStmt
    : DIVIDER FREE_TEXT? DIVIDER   // == text ==  (DIVIDER is ==)
    | DELAY                        // ...  or  ...text...
    ;

spacerStmt
    : SPACER               // |||
    | SPACER_N             // ||N||
    ;

// ═══════════════════════════════════════════════════════════════════════════
// TITLE / HEADER / FOOTER
// ═══════════════════════════════════════════════════════════════════════════

titleStmt
    : KW_TITLE FREE_TEXT
    ;

titleBlock
    : KW_TITLE NEWLINE+
          noteBodyLine+
      KW_END_TITLE NEWLINE+
    ;

headerStmt
    : KW_HEADER FREE_TEXT
    ;

footerStmt
    : KW_FOOTER FREE_TEXT
    ;

// ═══════════════════════════════════════════════════════════════════════════
// NEWPAGE
//   newpage [title text]
//   ignore newpage
// ═══════════════════════════════════════════════════════════════════════════

newpageStmt
    : KW_IGNORE KW_NEWPAGE
    | KW_NEWPAGE FREE_TEXT?
    ;

// ═══════════════════════════════════════════════════════════════════════════
// ANCHORS AND DURATION (teoz mode)
//
//   {anchorId}
//   {anchorId} <-> {anchorId} : label
// ═══════════════════════════════════════════════════════════════════════════

anchorStmt
    : LBRACE ID RBRACE
    ;

durationStmt
    : LBRACE ID RBRACE BIDIR_ARROW LBRACE ID RBRACE ( COLON FREE_TEXT )?
    ;

// ═══════════════════════════════════════════════════════════════════════════
// PRAGMA AND SKINPARAM
//
//   !pragma key value
//   skinparam paramName value
//   hide footbox
// ═══════════════════════════════════════════════════════════════════════════

pragmaStmt
    : BANG KW_PRAGMA ID FREE_TEXT?
    ;

skinparamStmt
    : KW_SKINPARAM ID FREE_TEXT?
    ;

hidestmt
    : KW_HIDE FREE_TEXT?
    ;

// ── Free text (label content) ─────────────────────────────────────────────
// Placeholder rule — parser rules reference FREE_TEXT token directly.
// The visitor joins multiple FREE_TEXT tokens when they appear.

freeText
    : FREE_TEXT
    ;


// ═══════════════════════════════════════════════════════════════════════════
// LEXER RULES
// ═══════════════════════════════════════════════════════════════════════════
//
// Ordering priorities:
//   1. STARTUML / ENDUML   before AT
//   2. Compound arrow tokens (all variants) before any single '-' or '<' '>'
//   3. DIVIDER '=='        before EQ '='
//   4. DELAY '...'         before any lone '.'
//   5. SPACER_N '||N||'    before SPACER '|||' before PIPE '|'
//   6. STEREOTYPE_OPEN/CLOSE '<<' '>>'  before LT/GT
//   7. End-note keywords   before KW_END
//   8. All keyword tokens  before ID

// ── Diagram wrappers ──────────────────────────────────────────────────────

STARTUML : '@startuml' ;
ENDUML   : '@enduml' ;

// ── Declaration keywords ──────────────────────────────────────────────────

KW_PARTICIPANT  : 'participant' ;
KW_ACTOR        : 'actor' ;
KW_BOUNDARY     : 'boundary' ;
KW_CONTROL      : 'control' ;
KW_ENTITY       : 'entity' ;
KW_DATABASE     : 'database' ;
KW_COLLECTIONS  : 'collections' ;
KW_QUEUE        : 'queue' ;
KW_AS           : 'as' ;
KW_ORDER        : 'order' ;
KW_CREATE       : 'create' ;

// ── Lifeline control ──────────────────────────────────────────────────────

KW_ACTIVATE     : 'activate' ;
KW_DEACTIVATE   : 'deactivate' ;
KW_DESTROY      : 'destroy' ;
KW_RETURN       : 'return' ;
KW_AUTOACTIVATE : 'autoactivate' ;
KW_ON           : 'on' ;
KW_OFF          : 'off' ;

// ── Autonumber ────────────────────────────────────────────────────────────

KW_AUTONUMBER   : 'autonumber' ;
KW_STOP         : 'stop' ;
KW_RESUME       : 'resume' ;
KW_INC          : 'inc' ;
KW_A            : 'A' ;
KW_B            : 'B' ;

// ── Group / fragment keywords ─────────────────────────────────────────────

KW_ALT       : 'alt' ;
KW_ELSE      : 'else' ;
KW_OPT       : 'opt' ;
KW_LOOP      : 'loop' ;
KW_PAR       : 'par' ;
KW_BREAK     : 'break' ;
KW_CRITICAL  : 'critical' ;
KW_GROUP     : 'group' ;
KW_PARTITION : 'partition' ;

// ── Note end keywords ─────────────────────────────────────────────────────
// All compound "end X" forms must be declared BEFORE bare KW_END 'end'
// so the longer literal wins when the lexer sees "end note" or "endnote".

KW_END_NOTE  : 'end' [ \t]+ 'note' ;
KW_ENDNOTE   : 'endnote' ;
KW_ENDRNOTE  : 'endrnote' ;
KW_ENDHNOTE  : 'endhnote' ;

KW_NOTE      : 'note' ;
KW_HNOTE     : 'hnote' ;
KW_RNOTE     : 'rnote' ;
KW_LEFT      : 'left' ;
KW_RIGHT     : 'right' ;
KW_OF        : 'of' ;
KW_OVER      : 'over' ;
KW_ACROSS    : 'across' ;

// ── Reference ─────────────────────────────────────────────────────────────

KW_REF       : 'ref' ;

// ── Box ───────────────────────────────────────────────────────────────────

KW_BOX       : 'box' ;

// ── Title / header / footer ───────────────────────────────────────────────
// "end title" — compound; declared before KW_END so it wins.
KW_END_TITLE : 'end' [ \t]+ 'title' ;
KW_TITLE     : 'title' ;
KW_HEADER    : 'header' ;
KW_FOOTER    : 'footer' ;

// KW_END declared after ALL compound "end X" forms so that longer literals
// (KW_END_NOTE, KW_END_TITLE, etc.) win when the lexer sees those sequences.
KW_END       : 'end' ;

// ── Newpage ───────────────────────────────────────────────────────────────

KW_NEWPAGE    : 'newpage' ;
KW_IGNORE     : 'ignore' ;

// ── Pragma / skinparam / hide ─────────────────────────────────────────────

KW_PRAGMA     : 'pragma' ;
KW_SKINPARAM  : 'skinparam' ;
KW_HIDE       : 'hide' ;

// ── Arrow tokens ──────────────────────────────────────────────────────────
//
// Design rationale
// ────────────────
// PlantUML sequence arrows are the most complex token set in this grammar.
// The combinatorial space includes:
//   Shaft:       -  (solid)    --  (dotted)
//   Left-head:   <  <<  \  //  x  o  (none)
//   Right-head:  >  >>  /  \\  x  o  (none)
//   Color mod:   -[#color]-  embedded in shaft
//   Boundary:    [  (left)   ]  (right)   ?  (short)
//   Bidir:       <->  <-->
//
// Strategy: express the full arrow as one ARROW token via a catch-all
// fragment that matches any reasonable combination.  The visitor decodes
// direction, style, head symbols, and embedded color from the token text.
//
// Key fragment definitions:
//   HEAD_R: any right-pointing head character sequence  (> >> / \\ x o)
//   HEAD_L: any left-pointing head character sequence   (< << \ // x o)
//   SHAFT:  one or more '-' chars (solid) or '--' (dotted base)
//   COLOR_MOD: '[' '#' colorref ']'
//
// The ARROW token covers all forms including:
//   boundary prefixes [ ]  and short-arrow ?
//   bidir <-> <-->
//   color-embedded shafts  -[#red]->
//   lost / found x o terminators

fragment F_HEAD_R  : ( '>>' | '>' | '/' | '\\\\' | 'x' | 'o' ) ;
fragment F_HEAD_L  : ( '<<' | '<' | '\\' | '//' | 'x' | 'o' ) ;
// Shaft: solid is one or more -, dotted is --
fragment F_SHAFT_S : '-'+ ;                  // solid: - or --
fragment F_SHAFT_D : '--' ;                  // dotted base (at least --)
// Color modifier embedded in shaft: -[#colorref]-
fragment F_COLOR_MOD : '[' '#' [a-zA-Z0-9]+ ']' ;
// The shaft with optional color: either  -[#color]-  or plain -/--
fragment F_SHAFT   : F_SHAFT_S ( F_COLOR_MOD F_SHAFT_S )? ;

// Complete ARROW token — matches all PlantUML sequence diagram arrow forms.
// Uses a broad catch-all anchored between optional left and right boundary
// markers and head/tail characters.
//
// Pattern groups (in order, longest match wins):
//   1. Bidirectional with optional dotted: <->  <-->
//   2. Dotted right-to-left: <--  <<--  o--  etc.
//   3. Dotted left-to-right: -->  -->>  --o  etc.
//   4. Solid right-to-left: <-  <<-  o\-  etc.
//   5. Solid left-to-right: ->  ->>  ->o  etc.
//   6. Boundary / short variants: [->, ->], ?->, ->?
//   All with optional color modifier in shaft.

BIDIR_ARROW
    : F_HEAD_L F_SHAFT F_HEAD_R      // <->  <-->  <-[#red]->
    ;

ARROW
    : '[' F_HEAD_L? F_SHAFT F_HEAD_R?   // [->  [-->  [<-
    | F_HEAD_L? F_SHAFT F_HEAD_R? ']'   // ->]  -->]  <-]
    | '?' F_HEAD_L? F_SHAFT F_HEAD_R?   // ?->  ?-->
    | F_HEAD_L? F_SHAFT F_HEAD_R? '?'   // ->?  -->?
    | F_HEAD_L F_SHAFT F_HEAD_R?        // <-  <--  <-[#color]-  <<-  o-
    | F_HEAD_L? F_SHAFT F_HEAD_R        // ->  -->  -[#color]->  ->>  -o
    ;

// ── Lifeline shorthand tokens ─────────────────────────────────────────────
// ++ -- ** !!  — appear right after target participant on a message line.
// Must be declared before any single-char punctuation they might share.

LL_ACTIVATE   : '++' ;
LL_DEACTIVATE : '--' ;
LL_CREATE     : '**' ;
LL_DESTROY    : '!!' ;

// ── Stereotype delimiters ─────────────────────────────────────────────────
// Declared before LT '<' and GT '>' single-char tokens.

STEREOTYPE_OPEN  : '<<' ;
STEREOTYPE_CLOSE : '>>' ;

// ── Divider '==' ─────────────────────────────────────────────────────────
// Declared before single EQ '=' token.

DIVIDER : '==' ;

// ── Delay '...' ───────────────────────────────────────────────────────────
// The delay is always at least three dots; may have text inside.
// DELAY captures the whole  ...text...  as one token.
// Declared before DOT so three-dot sequence wins.

DELAY
    : '...' ( ~[.\r\n] ~[\r\n]* )? '...'   // ...text...
    | '...'                                  // plain delay
    ;

// ── Spacer tokens ─────────────────────────────────────────────────────────
// SPACER_N must be declared before SPACER so ||45|| wins over |||.

SPACER_N : '||' [0-9]+ '||' ;
SPACER   : '|||' ;

// ── Hierarchical autonumber start ─────────────────────────────────────────
// Matches patterns like 1.1.1  1;2;3  1:2:3  1,2,3  (delimited digit groups)
// Must be declared before INT to prevent partial matches.

HIER_NUM
    : [0-9]+ ( [.:;,] [0-9]+ )+
    ;

// ── Color specification ───────────────────────────────────────────────────
// #red  #FF0000  #LightBlue  #ADD1B2
// The '#' prefix is part of the token.

COLOR
    : '#' [a-zA-Z0-9]+
    ;

// ── Quoted string ─────────────────────────────────────────────────────────

QUOTED_STRING
    : '"' ( '\\' '"' | ~["\r\n] )* '"'
    ;

// ── Bang (!) for pragma ───────────────────────────────────────────────────

BANG : '!' ;

// ── Punctuation ───────────────────────────────────────────────────────────

LPAREN   : '(' ;
RPAREN   : ')' ;
LBRACK   : '[' ;
RBRACK   : ']' ;
LBRACE   : '{' ;
RBRACE   : '}' ;
FSLASH   : '/' ;    // note alignment prefix
COMMA    : ',' ;
COLON    : ':' ;
QMARK    : '?' ;
DOT      : '.' ;

// ── Integer ───────────────────────────────────────────────────────────────

INT : [0-9]+ ;

// ── Identifier ────────────────────────────────────────────────────────────
// Participant ids, parameter names, skinparam names, pragma keys.
// Declared after all keyword tokens.

ID
    : [a-zA-Z_] [a-zA-Z0-9_\-]*
    ;

// ── Comments ──────────────────────────────────────────────────────────────
// Single-line: '   — apostrophe starts a comment to end of line
// Multi-line:  /'  ...  '/
// Single-line comment: starts with apostrophe
COMMENT_SINGLE
    : ['] ~[\r\n]*      // ['] matches literal apostrophe
    ;

// Multi-line comment: delimiters are /' and '/
COMMENT_MULTI
    : '/' ['] .*? ['] '/'   // builds /'+content+'/ from parts
    ;

// ── Free text (label, title, note body, etc.) ────────────────────────────
// Catch-all for anything remaining on a line that is not a structural token.
// Stops at newlines.  Declared last so all structural tokens take priority.

FREE_TEXT
    : ~[\r\n]+
    ;

// ── Newline ───────────────────────────────────────────────────────────────

NEWLINE
    : [\r\n]+
    ;

// ── Whitespace ────────────────────────────────────────────────────────────

WS
    : [ \t]+ -> skip
    ;
