// PlantUMLActivity.g4
// ANTLR4 grammar for PlantUML Activity Diagrams (new/beta syntax)
// Reference: https://plantuml.com/activity-diagram-beta
//
// ── Diagram wrapper ───────────────────────────────────────────────────────
//   @startuml [filename]
//   ...statements...
//   @enduml
//
// ── Action statements ─────────────────────────────────────────────────────
//   :action label text;           simple action (colon...semicolon)
//   #color:action text;           action with background color prefix
//   #color:action text; <<stereo>> action with color + SDL/UML stereotype
//   :action text; <<stereo>>      action with stereotype only
//   - Action text                 list-style action (dash bullet)
//   * Action text                 list-style action (star bullet)
//   ** Sub-action                 nested star bullet (multiple levels)
//
// ── Control flow keywords ─────────────────────────────────────────────────
//   start                         initial node
//   stop                          final flow node
//   end                           final activity node (alternative to stop)
//   detach                        detach flow (removes outgoing arrow)
//   kill                          kill flow (removes outgoing arrow, cross)
//   break                         break out of repeat loop
//
// ── Connector (circle) ────────────────────────────────────────────────────
//   (A)                           named connector / circle node
//   #color:(A)                    connector with color
//
// ── Explicit arrow ────────────────────────────────────────────────────────
//   ->                            default arrow (no label)
//   -> label text;                arrow with label
//   -[#color]->                   arrow with color
//   -[#color,dashed]->            arrow with color and style
//   -[#c1;#c2]->                  multi-color arrow
//   -[hidden]->                   hidden arrow (layout hint)
//   -[#color,bold]->  -[dotted]-> etc.
//
// ── Conditional ───────────────────────────────────────────────────────────
//   if (condition) then (yes-label)
//     ...
//   else (no-label)
//     ...
//   endif
//
//   if (x) is (y) then            alternate comparison form
//   if (x) equals (y) then        alternate equality form
//   elseif (cond) then (label)    chained else-if
//
// ── Switch ────────────────────────────────────────────────────────────────
//   switch (condition)
//   case (label)
//     ...
//   case (label)
//     ...
//   endswitch
//
// ── Repeat loop ───────────────────────────────────────────────────────────
//   repeat [:startAction;]
//     ...
//     [backward :backAction;]
//   repeat while (condition) [is (yes-label)] [not (no-label)]
//   -- or --
//   repeatwhile (condition) [is (yes-label)] [not (no-label)]
//
// ── While loop ────────────────────────────────────────────────────────────
//   while (condition) [is (label)]
//     ...
//     [backward :action;]
//   endwhile [(label)]
//
// ── Fork / parallel ───────────────────────────────────────────────────────
//   fork
//     ...
//   fork again
//     ...
//   end fork [{joinspec}]         joinspec: {or} {and} etc.
//   end merge                     alternative fork terminator (merge without join)
//   endfork                       compact alias for end fork
//
// ── Split ─────────────────────────────────────────────────────────────────
//   split
//     ...
//   split again
//     ...
//   end split
//
// ── Grouping containers ───────────────────────────────────────────────────
//   partition ["title" | title] [#color] { ... }
//   group ["title" | title] { ... }
//   package ["title" | title] [#color] { ... }
//   rectangle ["title" | title] [#color] { ... }
//   card ["title" | title] [#color] { ... }
//
// ── Swimlanes ─────────────────────────────────────────────────────────────
//   |LaneName|                    switch to named swimlane
//   |#color|LaneName|             swimlane with color
//   |#color|alias| Title          swimlane with color, alias, and displayed title
//
// ── Notes ─────────────────────────────────────────────────────────────────
//   note left : text              single-line note after action
//   note right : text
//   floating note left: text      floating note (not attached to action)
//   note left                     multi-line note
//     ...
//   end note
//   note                          standalone floating note block
//     ...
//   end note
//
// ── Label / Goto ──────────────────────────────────────────────────────────
//   label labelName               define a goto target
//   goto labelName                jump to a label
//
// ── Style block ───────────────────────────────────────────────────────────
//   <style>  ...  </style>        CSS-like styling block (opaque token)
//
// ── Other directives ──────────────────────────────────────────────────────
//   skinparam key value
//   skinparam SectionName { key value }
//   !pragma key value
//   scale N [width|height]
//   title text
//   header text
//   footer text
//   caption text
//
// ── Comments ──────────────────────────────────────────────────────────────
//   ' single-line comment
//   /' multi-line comment '/
//
// ── Lexer ordering notes ──────────────────────────────────────────────────
//   1.  STARTUML / ENDUML        before ID
//   2.  ACTION ':...;'           composite colon-to-semicolon token; before COLON
//   3.  SWIMLANE '|...|'         composite pipe-to-pipe token; before PIPE
//   4.  ARROW '-[...]->','-> '   before DASH
//   5.  STYLE_BLOCK '<style>...' before LT
//   6.  STEREO '<<...>>'         before LT
//   7.  Multi-word keywords      before their component single words:
//       KW_FORK_AGAIN, KW_SPLIT_AGAIN, KW_END_FORK, KW_END_MERGE,
//       KW_END_SPLIT, KW_REPEAT_WHILE, KW_END_NOTE, KW_END_LEGEND
//       all before KW_END, KW_FORK, KW_SPLIT, KW_REPEAT
//   8.  COLOR_PREFIX '#color:'   before COLOR '#color' before HASH '#'
//   9.  BULLET_STAR '*+'         (multi-level star) before STAR
//  10.  All keyword tokens        before ID

grammar PlantUMLActivity;

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

// ── Generic rest-of-line — consumes mixed tokens until NEWLINE ────────────
restOfLine
    : ( ID | QUOTED_STRING | INT | COLOR | FREE_TEXT
      | COLON | SEMI | PIPE | BANG | HASH | DOT
      | QMARK | COMMA | SLASH | LT | GT | PLUS | TILDE | EQ
      | LPAREN | RPAREN | LBRACK | RBRACK | LBRACE | RBRACE
      | STEREO | ARROW | SWIMLANE
      | BULLET_STAR | BULLET_DASH
      | KW_START | KW_STOP | KW_END | KW_DETACH | KW_KILL | KW_BREAK
      | KW_IF | KW_THEN | KW_ELSE | KW_ELSEIF | KW_ENDIF
      | KW_IS | KW_EQUALS | KW_NOT
      | KW_SWITCH | KW_CASE | KW_ENDSWITCH
      | KW_REPEAT | KW_BACKWARD | KW_WHILE | KW_ENDWHILE
      | KW_FORK | KW_SPLIT | KW_MERGE
      | KW_FORK_AGAIN | KW_SPLIT_AGAIN
      | KW_END_FORK | KW_END_MERGE | KW_END_SPLIT
      | KW_PARTITION | KW_GROUP | KW_PACKAGE | KW_RECTANGLE | KW_CARD
      | KW_NOTE | KW_FLOATING | KW_LEFT | KW_RIGHT
      | KW_LABEL | KW_GOTO
      | KW_SKINPARAM | KW_PRAGMA | KW_SCALE | KW_TITLE
      | KW_HEADER | KW_FOOTER | KW_CAPTION
      )+
    ;

// Content inside parentheses — any tokens except RPAREN and NEWLINE
parenContent
    : ( ID | QUOTED_STRING | INT | COLOR | FREE_TEXT
      | COLON | SEMI | PIPE | BANG | HASH | DOT
      | QMARK | COMMA | SLASH | LT | GT | PLUS | TILDE | EQ
      | LPAREN | LBRACK | RBRACK | LBRACE | RBRACE
      | STEREO | ARROW
      | BULLET_STAR | BULLET_DASH
      | KW_START | KW_STOP | KW_END | KW_DETACH | KW_KILL | KW_BREAK
      | KW_IF | KW_THEN | KW_ELSE | KW_ELSEIF | KW_ENDIF
      | KW_IS | KW_EQUALS | KW_NOT
      | KW_SWITCH | KW_CASE | KW_ENDSWITCH
      | KW_REPEAT | KW_BACKWARD | KW_WHILE | KW_ENDWHILE
      | KW_FORK | KW_SPLIT | KW_MERGE
      | KW_PARTITION | KW_GROUP | KW_PACKAGE | KW_RECTANGLE | KW_CARD
      | KW_NOTE | KW_FLOATING | KW_LEFT | KW_RIGHT
      | KW_LABEL | KW_GOTO
      | KW_SKINPARAM | KW_PRAGMA | KW_SCALE | KW_TITLE
      )+
    ;

// ── Statement dispatcher ──────────────────────────────────────────────────

statement
    : actionStmt         NEWLINE+
    | listActionStmt     NEWLINE+
    | arrowStmt          NEWLINE+
    | connectorStmt      NEWLINE+
    | swimlaneStmt       NEWLINE+
    | controlStmt        NEWLINE+
    | ifBlock                        // self-terminating
    | switchBlock                    // self-terminating
    | repeatBlock                    // self-terminating
    | whileBlock                     // self-terminating
    | forkBlock                      // self-terminating
    | splitBlock                     // self-terminating
    | containerBlock                 // self-terminating
    | noteStmt           NEWLINE+
    | noteBlock                      // self-terminating
    | labelStmt          NEWLINE+
    | gotoStmt           NEWLINE+
    | styleBlock         NEWLINE+
    | skinparamStmt      NEWLINE+
    | skinparamBlock                 // self-terminating
    | pragmaStmt         NEWLINE+
    | scaleStmt          NEWLINE+
    | titleStmt          NEWLINE+
    | headerStmt         NEWLINE+
    | footerStmt         NEWLINE+
    | captionStmt        NEWLINE+
    | COMMENT_SINGLE     NEWLINE+
    | COMMENT_MULTI      NEWLINE+
    | NEWLINE+
    ;

// ═══════════════════════════════════════════════════════════════════════════
// ACTION STATEMENT
//
//   :label text;               simple action
//   #color:label text;         action with background color
//   #color:label text; <<stereo>>  action with color and SDL/UML stereotype
//   :label text; <<stereo>>    action with stereotype
//
// The ACTION token captures the entire ':...;' span (including newlines
// inside the action text).  COLOR_PREFIX captures '#color:' as one token.
// ═══════════════════════════════════════════════════════════════════════════

actionStmt
    : ACTION STEREO?
    ;

// ── List-style actions (bullet notation) ──────────────────────────────────
//   - Action text       dash bullet
//   * Action text       star bullet (one level)
//   ** Sub-Action       star bullet (two levels)
//   *** Sub-Sub-Action  etc.

listActionStmt
    : BULLET_DASH restOfLine    // - text
    | BULLET_STAR restOfLine    // * / ** / *** text
    ;

// ═══════════════════════════════════════════════════════════════════════════
// EXPLICIT ARROW STATEMENT
//
//   ->                          simple arrow (no label)
//   -> label;                   arrow with label (semicolon-terminated)
//   -[#color]->                 colored arrow
//   -[#color,dashed]-> label;
//   -[hidden]->
//
// The ARROW token (see lexer) captures the full arrow operator.
// An optional label follows, terminated by ';'.
// ═══════════════════════════════════════════════════════════════════════════

arrowStmt
    : ARROW arrowLabel?
    ;

arrowLabel
    : restOfLine SEMI?
    ;

// ═══════════════════════════════════════════════════════════════════════════
// CONNECTOR (CIRCLE) STATEMENT
//
//   (A)            named connector
//   (A)            re-use of the same connector elsewhere
//   #color:(A)     colored connector (color before the paren)
// ═══════════════════════════════════════════════════════════════════════════

connectorStmt
    : COLOR? LPAREN ID RPAREN
    ;

// ── Control flow terminals ────────────────────────────────────────────────

controlStmt
    : KW_START
    | KW_STOP
    | KW_END
    | KW_DETACH
    | KW_KILL
    | KW_BREAK
    ;

// ═══════════════════════════════════════════════════════════════════════════
// SWIMLANE STATEMENT
//
//   |LaneName|                single-pipe swimlane switch
//   |#color|LaneName|         swimlane with color
//   |#color|alias| Title      swimlane with color, alias, displayed title
//
// The SWIMLANE token captures the entire '|...|' sequence.
// ═══════════════════════════════════════════════════════════════════════════

swimlaneStmt
    : SWIMLANE
    ;

// ═══════════════════════════════════════════════════════════════════════════
// CONDITIONAL (IF) BLOCK
//
// if (cond) then (yes)
//   ...
// elseif (cond) then (label)
//   ...
// else (no)
//   ...
// endif
//
// Condition operator forms:
//   if (x) then (label)
//   if (x) is (y) then
//   if (x) equals (y) then
// ═══════════════════════════════════════════════════════════════════════════

ifBlock
    : KW_IF condExpr condOp thenLabel NEWLINE+
          statement*
      elseifBranch*
      elseBranch?
      KW_ENDIF NEWLINE+
    ;

condExpr
    : LPAREN parenContent RPAREN
    ;

condOp
    : KW_THEN thenLabel            // if (x) then (label)
    | KW_IS   LPAREN parenContent RPAREN KW_THEN   // if (x) is (y) then
    | KW_EQUALS LPAREN parenContent RPAREN KW_THEN  // if (x) equals (y) then
    ;

thenLabel
    : ( LPAREN parenContent RPAREN )?
    ;

elseifBranch
    : KW_ELSEIF condExpr condOp NEWLINE+
          statement*
    ;

elseBranch
    : KW_ELSE ( LPAREN parenContent RPAREN )? NEWLINE+
          statement*
    ;

// ═══════════════════════════════════════════════════════════════════════════
// SWITCH BLOCK
//
//   switch (condition)
//   case (A) ...
//   case (B) ...
//   endswitch
// ═══════════════════════════════════════════════════════════════════════════

switchBlock
    : KW_SWITCH condExpr NEWLINE+
      caseBranch+
      KW_ENDSWITCH NEWLINE+
    ;

caseBranch
    : KW_CASE LPAREN parenContent RPAREN NEWLINE+
          statement*
    ;

// ═══════════════════════════════════════════════════════════════════════════
// REPEAT BLOCK
//
//   repeat [:startAction;]
//     ...
//     [backward :backAction;]
//   repeat while (cond) [is (yes)] [not (no)]
//
// 'repeatwhile' (no space) is also accepted as a compact form.
// ═══════════════════════════════════════════════════════════════════════════

repeatBlock
    : KW_REPEAT ACTION? NEWLINE+
          statement*
          backwardClause?
      KW_REPEAT_WHILE condExpr repeatWhileLabels NEWLINE+
    ;

backwardClause
    : KW_BACKWARD ACTION NEWLINE+
    ;

repeatWhileLabels
    : ( KW_IS  LPAREN parenContent RPAREN )?
      ( KW_NOT LPAREN parenContent RPAREN )?
      arrowStmt?
    ;

// ═══════════════════════════════════════════════════════════════════════════
// WHILE BLOCK
//
//   while (condition) [is (label)]
//     ...
//     [backward :action;]
//   endwhile [(label)]
// ═══════════════════════════════════════════════════════════════════════════

whileBlock
    : KW_WHILE condExpr ( KW_IS LPAREN parenContent RPAREN )? NEWLINE+
          statement*
          backwardClause?
      KW_ENDWHILE ( LPAREN parenContent RPAREN )? NEWLINE+
    ;

// ═══════════════════════════════════════════════════════════════════════════
// FORK / PARALLEL BLOCK
//
//   fork
//     ...
//   fork again
//     ...
//   end fork [{joinspec}]
//   end merge
//   endfork               (compact alias)
// ═══════════════════════════════════════════════════════════════════════════

forkBlock
    : KW_FORK NEWLINE+
          statement*
      forkAgainBranch+
      forkTerminator
    ;

forkAgainBranch
    : KW_FORK_AGAIN NEWLINE+
          statement*
    ;

forkTerminator
    : KW_END_FORK joinSpec? NEWLINE+
    | KW_END_MERGE NEWLINE+
    | KW_ENDFORK NEWLINE+
    ;

// Optional joinspec: {or} {and} etc.
joinSpec
    : LBRACE ID RBRACE
    ;

// ═══════════════════════════════════════════════════════════════════════════
// SPLIT BLOCK
//
//   split
//     ...
//   split again
//     ...
//   end split
// ═══════════════════════════════════════════════════════════════════════════

splitBlock
    : KW_SPLIT NEWLINE+
          statement*
      splitAgainBranch+
      KW_END_SPLIT NEWLINE+
    ;

splitAgainBranch
    : KW_SPLIT_AGAIN NEWLINE+
          statement*
    ;

// ═══════════════════════════════════════════════════════════════════════════
// CONTAINER BLOCKS  (partition, group, package, rectangle, card)
//
//   partition ["Title" | title] [#color] { ... }
//   group ["Title" | title] { ... }
//   package ["Title" | title] [#color] { ... }
//   rectangle ["Title" | title] [#color] { ... }
//   card ["Title" | title] [#color] { ... }
// ═══════════════════════════════════════════════════════════════════════════

containerBlock
    : containerKeyword containerName? COLOR? LBRACE NEWLINE+
          statement*
      RBRACE NEWLINE+
    ;

containerKeyword
    : KW_PARTITION | KW_GROUP | KW_PACKAGE | KW_RECTANGLE | KW_CARD
    ;

containerName
    : QUOTED_STRING
    | ID             // bare unquoted name
    ;

// ═══════════════════════════════════════════════════════════════════════════
// NOTE STATEMENTS
//
// Inline single-line (immediately after an action or backward):
//   note left : text
//   note right : text
//   floating note left: text
//   floating note right: text
//
// Multi-line note block:
//   note left
//     ...
//   end note
//
//   note right
//     ...
//   end note
//
//   note                (standalone floating note block)
//     ...
//   end note
// ═══════════════════════════════════════════════════════════════════════════

noteStmt
    : NOTE_INLINE_TOKEN
    ;

noteBlock
    : NOTE_BLOCK_TOKEN NEWLINE+
    ;

// ── Label and Goto ────────────────────────────────────────────────────────

labelStmt
    : KW_LABEL ID
    ;

gotoStmt
    : KW_GOTO ID
    ;

// ═══════════════════════════════════════════════════════════════════════════
// STYLE, SKINPARAM, PRAGMA, DIRECTIVES
// ═══════════════════════════════════════════════════════════════════════════

styleBlock
    : STYLE_BLOCK
    ;

skinparamStmt
    : KW_SKINPARAM ( ID | containerKeyword ) restOfLine?
    ;

skinparamBlock
    : KW_SKINPARAM ( ID | containerKeyword ) LBRACE NEWLINE+
          skinparamEntry*
      RBRACE NEWLINE+
    ;

skinparamEntry
    : restOfLine NEWLINE+
    | NEWLINE+
    ;

pragmaStmt  : BANG KW_PRAGMA ID restOfLine?
            | BANG ID restOfLine?
            ;
scaleStmt   : KW_SCALE restOfLine ;
titleStmt   : KW_TITLE restOfLine? ;
headerStmt  : KW_HEADER restOfLine? | HEADER_BLOCK ;
footerStmt  : KW_FOOTER restOfLine? | FOOTER_BLOCK ;
captionStmt : KW_CAPTION restOfLine? ;


// ═══════════════════════════════════════════════════════════════════════════
// LEXER RULES
// ═══════════════════════════════════════════════════════════════════════════
//
// Critical ordering:
//   1.  STARTUML / ENDUML            before ID
//   2.  ACTION ':...;'               longest-match composite; before COLON
//   3.  SWIMLANE '|...|'             composite; before PIPE
//   4.  ARROW '-[...]->','->...'     composite; before DASH
//   5.  STYLE_BLOCK '<style>...'     composite; before LT
//   6.  STEREO '<<...>>'             composite; before LT
//   7.  COLOR_PREFIX '#color:'       before COLOR '#color' before HASH '#'
//   8.  CONNECTOR '(X)'              single-char-content paren; before LPAREN
//   9.  Multi-word keyword tokens:
//       KW_FORK_AGAIN, KW_SPLIT_AGAIN, KW_END_FORK, KW_END_MERGE,
//       KW_END_SPLIT, KW_REPEAT_WHILE, KW_END_NOTE
//       ALL before their single-word components (KW_END, KW_FORK, etc.)
//  10.  BULLET_STAR ('*'+)           before STAR '*'
//  11.  All keyword tokens            before ID

// ── Diagram wrappers ──────────────────────────────────────────────────────

STARTUML : '@startuml' ;
ENDUML   : '@enduml' ;

// ── Action token ──────────────────────────────────────────────────────────
// Captures the full ':...;' action including any embedded newlines.
// The content between ':' and ';' is the action text (Creole-formatted).
// Declared before COLON so ':' followed by any content up to ';' wins.

// Note composite tokens — declared BEFORE ACTION so ':' inside note/header/footer
// body text is not consumed by ACTION.

// Multi-line note block: note [left|right] [#color]\n...\nend note
// Requires 'end note' to be at start of a line (after optional whitespace)
// to avoid matching 'end note' appearing mid-line inside note body text.
NOTE_BLOCK_TOKEN
    : ('floating' [ \t]+)? 'note' ([ \t]+ ('left' | 'right'))? ([ \t]+ '#' [a-zA-Z0-9]+)? [ \t]* ('\r'? '\n')
      .*?
      ('\r'? '\n') [ \t]* 'end' [ \t]+ 'note'
    ;

// Inline note: note left|right [#color] : text
NOTE_INLINE_TOKEN
    : ('floating' [ \t]+)? 'note' [ \t]+ ('left' | 'right') ([ \t]+ '#' [a-zA-Z0-9]+)? [ \t]* ':' ~[\r\n]*
    ;

// Multi-line header/footer blocks
HEADER_BLOCK
    : 'header' [ \t]* ('\r'? '\n') .*? 'end' [ \t]+ 'header'
    ;

FOOTER_BLOCK
    : 'footer' [ \t]* ('\r'? '\n') .*? 'end' [ \t]+ 'footer'
    ;

// Action: captures ':text;' including optional '#color:' prefix
ACTION
    : '#' [a-zA-Z0-9\-|\\]+ ':' .*? ';'   // #color:text;
    | ':' .*? ';'                            // :text;
    ;

// ── Swimlane token ────────────────────────────────────────────────────────
// Captures the full '|...|' swimlane declaration including optional
// color and alias fields.
// Forms:
//   |Name|
//   |#color|Name|
//   |#color|alias| Title text (everything to end of line after last |)
// Declared before PIPE so the full swimlane wins.

SWIMLANE
    : '|' ( '#' [a-zA-Z0-9]+ '|' )? ~[|\r\n]+ '|' ~[\r\n]*
    ;

// ── Arrow token ───────────────────────────────────────────────────────────
// Covers all activity arrow variants:
//   ->                         plain arrow
//   -[#color]->                colored
//   -[#color,dashed]->         colored + style
//   -[#c1;#c2]->               multi-color
//   -[hidden]->                hidden
//   -[#blue,bold]->  -[dotted]->  etc.
// The inline style block '[...]' is optional.
// Declared before any bare DASH '-'.

ARROW
    : '-' ( '[' ~[\]\r\n]* ']' )? '-'* '>'
    ;

// ── Style block ───────────────────────────────────────────────────────────
// '<style>' is longer than '<<'; declared before STEREO so maximal-munch
// is explicit in declaration order as well as token length.

STYLE_BLOCK
    : '<style>' .*? '</style>'
    ;

// ── Stereotype token ──────────────────────────────────────────────────────
// Captures << anything >> as one token.
// Declared after STYLE_BLOCK (longer pattern) and before any bare '<'.

STEREO
    : '<<' [ \t]* ~[>\r\n]+ [ \t]* '>>'
    ;

// ── Color prefix (for colored actions and connectors) ─────────────────────
// '#color:' — the color prefix immediately before an ACTION colon.
// Must be declared before COLOR '#color' and before HASH '#'.

COLOR_PREFIX
    : '#' [a-zA-Z0-9\-|\\]+ ':'
    ;

// ── Color token (standalone, e.g. on connectors and containers) ───────────

COLOR
    : '#' [a-zA-Z0-9\-|\\]+
    ;

// Connector is now handled as a parser rule: connectorStmt → LPAREN ID RPAREN
// (Removed CONNECTOR lexer token to avoid conflict with condition labels)

// ── Bullet tokens ─────────────────────────────────────────────────────────
// BULLET_STAR matches one or more '*' at the start of a logical line
// (after whitespace skip).  Declared before STAR.

BULLET_STAR : '*'+ ;
BULLET_DASH : '-' ;

// ── Multi-word keyword tokens ─────────────────────────────────────────────
// ALL must be declared before their single-word components.

// fork again / split again — before KW_FORK / KW_SPLIT
KW_FORK_AGAIN   : 'fork' [ \t]+ 'again' ;
KW_SPLIT_AGAIN  : 'split' [ \t]+ 'again' ;

// end fork / end merge / end split / end note — before KW_END
KW_END_FORK     : 'end' [ \t]+ 'fork' ;
KW_END_MERGE    : 'end' [ \t]+ 'merge' ;
KW_END_SPLIT    : 'end' [ \t]+ 'split' ;
KW_END_NOTE     : 'end' [ \t]+ 'note' ;

// repeat while / repeatwhile — before KW_REPEAT / KW_WHILE
KW_REPEAT_WHILE : 'repeat' [ \t]* 'while' ;

// ── Single-word keyword tokens ────────────────────────────────────────────

KW_START      : 'start' ;
KW_STOP       : 'stop' ;
KW_END        : 'end' ;
KW_DETACH     : 'detach' ;
KW_KILL       : 'kill' ;
KW_BREAK      : 'break' ;

KW_IF         : 'if' ;
KW_THEN       : 'then' ;
KW_ELSE       : 'else' ;
KW_ELSEIF     : 'elseif' ;
KW_ENDIF      : 'endif' ;
KW_IS         : 'is' ;
KW_EQUALS     : 'equals' ;
KW_NOT        : 'not' ;

KW_SWITCH     : 'switch' ;
KW_CASE       : 'case' ;
KW_ENDSWITCH  : 'endswitch' ;

KW_REPEAT     : 'repeat' ;
KW_BACKWARD   : 'backward' ;
KW_WHILE      : 'while' ;
KW_ENDWHILE   : 'endwhile' ;

KW_FORK       : 'fork' ;
KW_ENDFORK    : 'endfork' ;
KW_SPLIT      : 'split' ;
KW_MERGE      : 'merge' ;

KW_PARTITION  : 'partition' ;
KW_GROUP      : 'group' ;
KW_PACKAGE    : 'package' ;
KW_RECTANGLE  : 'rectangle' ;
KW_CARD       : 'card' ;

KW_NOTE       : 'note' ;
KW_FLOATING   : 'floating' ;
KW_LEFT       : 'left' ;
KW_RIGHT      : 'right' ;

KW_LABEL      : 'label' ;
KW_GOTO       : 'goto' ;

KW_SKINPARAM  : 'skinparam' ;
KW_PRAGMA     : 'pragma' ;
KW_SCALE      : 'scale' ;
KW_TITLE      : 'title' ;
KW_HEADER     : 'header' ;
KW_FOOTER     : 'footer' ;
KW_CAPTION    : 'caption' ;

// ── Quoted string ─────────────────────────────────────────────────────────

QUOTED_STRING
    : '"' ( '\\' '"' | ~["\r\n] )* '"'
    ;

// ── Punctuation ───────────────────────────────────────────────────────────

LPAREN  : '(' ;
RPAREN  : ')' ;
LBRACE  : '{' ;
RBRACE  : '}' ;
LBRACK  : '[' ;
RBRACK  : ']' ;
COLON   : ':' ;
SEMI    : ';' ;
PIPE    : '|' ;
STAR    : '*' ;
DASH    : '-' ;
BANG    : '!' ;
HASH    : '#' ;
DOT     : '.' ;
QMARK   : '?' ;
COMMA   : ',' ;
SLASH   : '/' ;
LT      : '<' ;
GT      : '>' ;
PLUS    : '+' ;
TILDE   : '~' ;
EQ      : '=' ;

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
// Catch-all for condition text, arrow labels, container names, note body
// lines, skinparam values, etc.  Stops at newline.
// Declared last so all structural tokens have priority.

// Restricted: catch-all for characters not covered by explicit tokens.
// Single character to prevent consuming structural delimiters like ')'.
FREE_TEXT
    : [&%^\\`$@]
    | [\u0080-\uFFFF]     // Unicode chars (em-dash, accented letters, etc.)
    ;

// ── Newline ───────────────────────────────────────────────────────────────

NEWLINE
    : [\r\n]+
    ;

// ── Whitespace ────────────────────────────────────────────────────────────

WS
    : [ \t]+ -> skip
    ;
