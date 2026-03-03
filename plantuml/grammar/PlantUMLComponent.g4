// PlantUMLComponent.g4
// ANTLR4 grammar for PlantUML Component Diagrams
// Reference: https://plantuml.com/component-diagram
//
// ── Diagram wrapper ───────────────────────────────────────────────────────
//   @startuml [filename]
//   ...statements...
//   @enduml
//
// ── Component declarations ────────────────────────────────────────────────
//   [Name]                           bracket form (always treated as component)
//   [Name] as Alias                  bracket form with alias
//   component Name                   keyword form (no brackets needed for simple ids)
//   component "Long Name" as Alias   keyword form with quoted name and alias
//   component Name <<stereotype>>    with stereotype
//   component Name $tag1 $tag2       with one or more tags
//   component Name #color            with background color
//   component Name [                 keyword form with multi-line description body
//     line one
//     line two
//   ]
//
// ── Interface declarations ────────────────────────────────────────────────
//   () "Name"                        circle-paren form
//   () "Name" as Alias               circle-paren form with alias
//   interface Name                   keyword form
//   interface "Long Name" as Alias   keyword form with alias
//
// ── Group containers (recursive nesting) ──────────────────────────────────
//   package  "Title" [#color] [<<stereotype>>] { statements }
//   node     "Title" [#color] [<<stereotype>>] { statements }
//   folder   "Title" [#color] [<<stereotype>>] { statements }
//   frame    "Title" [#color] [<<stereotype>>] { statements }
//   cloud    ["Title"] [#color] [<<stereotype>>] { statements }
//   database "Title" [#color] [<<stereotype>>] { statements }
//   rectangle "Title" [#color] [<<stereotype>>] { statements }
//
// ── Port declarations (inside component body only) ────────────────────────
//   port    portId
//   portin  portId
//   portout portId
//
// ── Relation / link statements ────────────────────────────────────────────
//   A -- B                           solid line (vertical)
//   A - B                            solid line (horizontal)
//   A --> B                          solid arrow
//   A -> B                           solid arrow (horizontal)
//   A .. B                           dotted line
//   A ..> B                          dotted arrow
//   A -left-> B                      directional hint: left|right|up|down
//   A -l-> B                         abbreviated direction: l|r|u|d
//   A -left- B                       directional open line
//   A -- B : label                   relation with label
//   A --> B : label
//   [Comp] ..> HTTP : use            component to bare-id
//
// ── Note statements ───────────────────────────────────────────────────────
//   note left of X : text            single-line positional note
//   note right of X : text
//   note top of X : text
//   note bottom of X : text
//   note left of X                   multi-line positional note
//     ...
//   end note
//   note as N                        floating note with alias
//     ...
//   end note
//   note "text" as N                 single-line floating note
//
// ── Sprite declaration ────────────────────────────────────────────────────
//   sprite $spriteName [WxH/depth] {
//     HEXROW
//     HEXROW
//   }
//
// ── Skinparam ─────────────────────────────────────────────────────────────
//   skinparam paramName value
//   skinparam paramName {
//     key value
//     key value
//   }
//   skinparam component { ... }
//   skinparam interface { ... }
//   skinparam node { ... }
//
// ── Visibility control ────────────────────────────────────────────────────
//   hide @unlinked
//   hide $tagName
//   remove @unlinked
//   remove $tagName
//   remove *
//   restore $tagName
//
// ── Other directives ──────────────────────────────────────────────────────
//   left to right direction
//   top to bottom direction
//   allowmixing
//   title text
//   header text
//   footer text
//   caption text
//   legend [left|right|center]  ...  end legend
//   !pragma key value
//   scale N
//
// ── Comments ──────────────────────────────────────────────────────────────
//   ' single-line comment
//   /' multi-line comment '/
//
// ── Lexer ordering notes ──────────────────────────────────────────────────
//   1. STARTUML / ENDUML before AT '@'
//   2. ARROW tokens (longest first) before DASH '-' and DOT '.'
//   3. DOTTED_LINE '..' before DOT '.'
//   4. STEREOTYPE_OPEN '<<' before any LT; STEREOTYPE_CLOSE '>>' before GT
//   5. CIRCLE_IFACE '()' before LPAREN '('
//   6. All keyword tokens before ID
//   7. TAG '$id' token ($ prefix) declared before DOLLAR '$'

grammar PlantUMLComponent;

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
    : ID ( '.' ID )*
    | QUOTED_STRING
    ;

// ── Top-level statement dispatcher ────────────────────────────────────────

statement
    : componentDecl     NEWLINE+
    | interfaceDecl     NEWLINE+
    | groupBlock                     // self-terminating with '}'
    | relationStmt      NEWLINE+
    | noteStmt          NEWLINE+
    | noteBlock                      // self-terminating with 'end note'
    | spriteDecl                     // self-terminating with '}'
    | skinparamStmt     NEWLINE+
    | skinparamBlock                 // self-terminating with '}'
    | visibilityStmt    NEWLINE+
    | directionStmt     NEWLINE+
    | allowMixingStmt   NEWLINE+
    | titleStmt         NEWLINE+
    | headerStmt        NEWLINE+
    | footerStmt        NEWLINE+
    | captionStmt       NEWLINE+
    | legendBlock                    // self-terminating with 'end legend'
    | pragmaStmt        NEWLINE+
    | scaleStmt         NEWLINE+
    | COMMENT_SINGLE    NEWLINE+
    | COMMENT_MULTI     NEWLINE+
    | NEWLINE+
    ;

// ═══════════════════════════════════════════════════════════════════════════
// COMPONENT DECLARATIONS
//
// Form 1:  [Name]                      bracket notation
// Form 2:  [Name] as Alias             bracket notation with alias
// Form 3:  component Name              keyword, simple id
// Form 4:  component "Long Name"       keyword, quoted
// Form 5:  component Name as Alias     keyword with alias
// Form 6:  component Name <<stereo>>   keyword with stereotype
// Form 7:  component Name $tag         keyword with one or more tags
// Form 8:  component Name #color       keyword with color
// Form 9:  component Name [ body ]     keyword with multi-line description body
//
// Modifiers (color, stereotype, tags) may appear in any order after the name.
// ═══════════════════════════════════════════════════════════════════════════

componentDecl
    : BRACKET_COMP aliasClause? componentModifier*   // [Name] as Alias #color
    | KW_COMPONENT elementName aliasClause?
      componentModifier*
      componentBody?
    ;

// The body of a component declared with 'component' keyword:
// either a single-line description in [ ] on the same line,
// or a nested block { ... } containing port/component declarations.
componentBody
    : LBRACK bodyText RBRACK              // component Foo [ description ]
    | LBRACE NEWLINE+ innerStatement* RBRACE NEWLINE+  // component Foo { ports... }
    ;

// Statements allowed inside a component body block { }
innerStatement
    : portDecl       NEWLINE+
    | componentDecl  NEWLINE+
    | COMMENT_SINGLE NEWLINE+
    | COMMENT_MULTI  NEWLINE+
    | NEWLINE+
    ;

// Port declarations — only valid inside a component body
portDecl
    : KW_PORT    elementName
    | KW_PORTIN  elementName
    | KW_PORTOUT elementName
    ;

// ═══════════════════════════════════════════════════════════════════════════
// INTERFACE DECLARATIONS
//
// Form 1:  () "Name"           circle-paren notation
// Form 2:  () "Name" as Alias  circle-paren with alias
// Form 3:  interface Name      keyword, simple id
// Form 4:  interface "Name" as Alias
// ═══════════════════════════════════════════════════════════════════════════

interfaceDecl
    : CIRCLE_IFACE elementName aliasClause? componentModifier*
    | KW_INTERFACE elementName aliasClause? componentModifier*
    ;

// ── Element name ──────────────────────────────────────────────────────────
// A component or interface name is either a quoted string or a bare ID.

elementName
    : QUOTED_STRING
    | ID
    ;

// ── Alias ─────────────────────────────────────────────────────────────────

aliasClause
    : KW_AS elementName
    ;

// ── Component modifiers ───────────────────────────────────────────────────
// Appear after the element name / alias in any order.

componentModifier
    : stereotypeClause    // <<Name>>  or  <<$sprite>>
    | colorSpec           // #color
    | TAG                 // $tagName
    ;

colorSpec
    : COLOR
    ;

stereotypeClause
    : STEREOTYPE_OPEN stereotypeBody STEREOTYPE_CLOSE
    ;

stereotypeBody
    : spotSpec? stereotypeText?
    ;

// Optional (C,#color) spot inside stereotype
spotSpec
    : LPAREN spotChar COMMA colorSpec RPAREN
    ;

spotChar : ID | INT ;

// Stereotype text after optional spot
stereotypeText
    : FREE_TEXT
    | ID
    ;

// Body text inside [ ] for multi-line component description
bodyText
    : FREE_TEXT?
    ;

// ═══════════════════════════════════════════════════════════════════════════
// GROUP CONTAINERS
//
// package | node | folder | frame | cloud | database | rectangle
//   ["Title"] [#color] [<<stereotype>>] {
//       statements*
//   }
//
// Containers nest recursively — they appear as statements inside other
// containers.
// ═══════════════════════════════════════════════════════════════════════════

groupBlock
    : groupKeyword elementName? colorSpec? stereotypeClause? LBRACE NEWLINE+
          statement*
      RBRACE NEWLINE+
    ;

groupKeyword
    : KW_PACKAGE
    | KW_NODE
    | KW_FOLDER
    | KW_FRAME
    | KW_CLOUD
    | KW_DATABASE
    | KW_RECTANGLE
    ;

// ═══════════════════════════════════════════════════════════════════════════
// RELATION STATEMENTS
//
// Format:  lhsRef  arrowSpec  rhsRef  [: label]
//
// lhsRef and rhsRef can be:
//   [Name]    — bracket notation (component reference)
//   ()Name    — circle paren (interface reference, rare in relation context)
//   Name      — bare identifier (component or interface alias)
//   "Name"    — quoted name
//
// arrowSpec covers all combinations of:
//   Shaft:     -   --   ..   ...   (solid or dotted, one or two)
//   Direction: -left-  -right-  -up-  -down-  (or abbrev -l- -r- -u- -d-)
//   Heads:     >  <  (on either end, or neither for open lines)
//   Dotted arrow: ..>  <..  <..>
// ═══════════════════════════════════════════════════════════════════════════

relationStmt
    : relationRef ARROW_SPEC relationRef ( COLON labelText )?
    ;

// A relation endpoint: bracket-comp, bare id, or quoted string
relationRef
    : BRACKET_COMP    // [Name]
    | QUOTED_STRING
    | ID
    ;

// Arrow spec — a single composite ARROW_SPEC token (decoded by visitor)
// All legal arrow string patterns are captured by the lexer.
// See ARROW_SPEC token definition below.

// Label text after ':'
labelText
    : FREE_TEXT
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
// Positional multi-line:
//   note left of X
//     ...
//   end note
//
// Floating with alias:
//   note as N
//     ...
//   end note
//
// Floating single-line (inline):
//   note "text" as N
//
// Connection to floating note via relation:
//   C .. N
// ═══════════════════════════════════════════════════════════════════════════

noteStmt
    : KW_NOTE noteSide KW_OF relationRef ( COLON FREE_TEXT )?
    | KW_NOTE QUOTED_STRING KW_AS elementName
    ;

noteBlock
    : KW_NOTE noteSide KW_OF relationRef NEWLINE+
          noteBodyLine+
      KW_END_NOTE NEWLINE+
    | KW_NOTE KW_AS elementName NEWLINE+
          noteBodyLine+
      KW_END_NOTE NEWLINE+
    ;

noteSide
    : KW_LEFT | KW_RIGHT | KW_TOP | KW_BOTTOM
    ;

noteBodyLine
    : FREE_TEXT NEWLINE+
    | NEWLINE+
    ;

// ═══════════════════════════════════════════════════════════════════════════
// SPRITE DECLARATION
//
//   sprite $spriteName [WxH/depth] {
//     FFFFFFFFFFFFFFFF
//     ...
//   }
// ═══════════════════════════════════════════════════════════════════════════

spriteDecl
    : KW_SPRITE TAG spriteDimension? LBRACE NEWLINE+
          spriteRow+
      RBRACE NEWLINE+
    ;

// [WxH/depth] — e.g. [16x16/16]
spriteDimension
    : LBRACK INT KW_X INT ( FSLASH INT )? RBRACK
    ;

// Hex data rows inside sprite body
spriteRow
    : SPRITE_ROW NEWLINE+
    | NEWLINE+
    ;

// ═══════════════════════════════════════════════════════════════════════════
// SKINPARAM STATEMENTS
//
// Inline:  skinparam paramName value
// Block:   skinparam paramName {
//            key value
//          }
// ═══════════════════════════════════════════════════════════════════════════

skinparamStmt
    : KW_SKINPARAM skinparamPath FREE_TEXT?
    ;

skinparamBlock
    : KW_SKINPARAM skinparamPath LBRACE NEWLINE+
          skinparamEntry*
      RBRACE NEWLINE+
    ;

// skinparam path: paramName  or  elementType  (e.g. "component", "interface")
skinparamPath
    : ID ( '.' ID )*
    ;

skinparamEntry
    : ID FREE_TEXT NEWLINE+
    | NEWLINE+
    ;

// ═══════════════════════════════════════════════════════════════════════════
// VISIBILITY CONTROL STATEMENTS
//
//   hide @unlinked
//   hide $tagName
//   remove @unlinked
//   remove $tagName
//   remove *
//   restore $tagName
// ═══════════════════════════════════════════════════════════════════════════

visibilityStmt
    : visibilityKeyword visibilityTarget
    ;

visibilityKeyword
    : KW_HIDE | KW_REMOVE | KW_RESTORE
    ;

visibilityTarget
    : AT_UNLINKED     // @unlinked
    | TAG             // $tagName
    | STAR            // *  (wildcard — remove all)
    ;

// ═══════════════════════════════════════════════════════════════════════════
// DIRECTION, MIXING, TITLE, HEADER, FOOTER, CAPTION
// ═══════════════════════════════════════════════════════════════════════════

directionStmt
    : KW_LEFT KW_TO KW_RIGHT KW_DIRECTION
    | KW_TOP  KW_TO KW_BOTTOM KW_DIRECTION
    ;

allowMixingStmt
    : KW_ALLOWMIXING
    ;

titleStmt   : KW_TITLE   FREE_TEXT? ;
headerStmt  : KW_HEADER  FREE_TEXT? ;
footerStmt  : KW_FOOTER  FREE_TEXT? ;
captionStmt : KW_CAPTION FREE_TEXT? ;

legendBlock
    : KW_LEGEND legendAlign? NEWLINE+
          noteBodyLine+
      KW_END_LEGEND NEWLINE+
    ;

legendAlign : KW_LEFT | KW_RIGHT | KW_CENTER ;

// ── Pragma ────────────────────────────────────────────────────────────────

pragmaStmt
    : BANG KW_PRAGMA ID FREE_TEXT?
    ;

// ── Scale ─────────────────────────────────────────────────────────────────

scaleStmt
    : KW_SCALE FREE_TEXT
    ;


// ═══════════════════════════════════════════════════════════════════════════
// LEXER RULES
// ═══════════════════════════════════════════════════════════════════════════
//
// Critical ordering:
//   1.  STARTUML / ENDUML     before ID (they contain '@')
//   2.  ARROW_SPEC tokens     before DASH and DOT
//   3.  DOTTED_LINE '..'      before DOT '.'
//   4.  STEREOTYPE_OPEN '<<'  before any LT-like token
//   5.  CIRCLE_IFACE '()'     before LPAREN '('
//   6.  BRACKET_COMP '[..]'   captures the full [name] as one token
//   7.  TAG '$name'           before DOLLAR '$'
//   8.  AT_UNLINKED '@unlinked' before AT '@'
//   9.  KW_END_NOTE 'end note' before KW_END 'end' (compound form first)
//  10.  All keyword tokens    before ID

// ── Diagram wrappers ──────────────────────────────────────────────────────

STARTUML : '@startuml' ;
ENDUML   : '@enduml' ;

// ── Component bracket notation ────────────────────────────────────────────
// Captures the entire [Name] as one token, including any internal spaces.
// Declared before LBRACK so the full bracketed name wins.
// The visitor strips the surrounding brackets.

BRACKET_COMP
    : '[' ~[\]\r\n]+ ']'
    ;

// ── Interface circle-paren notation ──────────────────────────────────────
// '()' is the interface symbol.  Declared before LPAREN.

CIRCLE_IFACE : '()' ;

// ── Tag token  $tagName ───────────────────────────────────────────────────
// A tag is '$' followed immediately by an identifier (no space).
// Must be declared before DOLLAR so the full $name is one token.

TAG
    : '$' [a-zA-Z_] [a-zA-Z0-9_]*
    ;

// ── @unlinked special target ──────────────────────────────────────────────
// Declared before generic AT '@' token.

AT_UNLINKED : '@unlinked' ;

// ── Declaration keywords ──────────────────────────────────────────────────

KW_COMPONENT  : 'component' ;
KW_INTERFACE  : 'interface' ;
KW_AS         : 'as' ;
KW_PORT       : 'port' ;
KW_PORTIN     : 'portin' ;
KW_PORTOUT    : 'portout' ;

// ── Group container keywords ──────────────────────────────────────────────

KW_PACKAGE    : 'package' ;
KW_NODE       : 'node' ;
KW_FOLDER     : 'folder' ;
KW_FRAME      : 'frame' ;
KW_CLOUD      : 'cloud' ;
KW_DATABASE   : 'database' ;
KW_RECTANGLE  : 'rectangle' ;

// ── Note keywords ─────────────────────────────────────────────────────────
// KW_END_NOTE must be declared before KW_END.

KW_END_NOTE   : 'end' [ \t]+ 'note' ;
KW_END_LEGEND : 'end' [ \t]+ 'legend' ;
KW_END        : 'end' ;
KW_NOTE       : 'note' ;
KW_LEFT       : 'left' ;
KW_RIGHT      : 'right' ;
KW_TOP        : 'top' ;
KW_BOTTOM     : 'bottom' ;
KW_OF         : 'of' ;

// ── Visibility control keywords ───────────────────────────────────────────

KW_HIDE       : 'hide' ;
KW_REMOVE     : 'remove' ;
KW_RESTORE    : 'restore' ;

// ── Direction keywords ────────────────────────────────────────────────────
// KW_LEFT, KW_RIGHT, KW_TOP, KW_BOTTOM already declared above (note sides).
// They are reused in directionStmt without re-declaration.

KW_TO        : 'to' ;
KW_DIRECTION : 'direction' ;

// ── Other directive keywords ──────────────────────────────────────────────

KW_ALLOWMIXING : 'allowmixing' ;
KW_TITLE       : 'title' ;
KW_HEADER      : 'header' ;
KW_FOOTER      : 'footer' ;
KW_CAPTION     : 'caption' ;
KW_LEGEND      : 'legend' ;
KW_CENTER      : 'center' ;
KW_SKINPARAM   : 'skinparam' ;
KW_PRAGMA      : 'pragma' ;
KW_SCALE       : 'scale' ;
KW_SPRITE      : 'sprite' ;
KW_X           : 'x' ;      // used in sprite dimension: 16x16

// ── Stereotype delimiters ─────────────────────────────────────────────────

STEREOTYPE_OPEN  : '<<' ;
STEREOTYPE_CLOSE : '>>' ;

// ── Arrow specification token ─────────────────────────────────────────────
// Captures all PlantUML component diagram arrow/line forms as one token.
// The visitor decodes direction, shaft style (solid/dotted), and arrowheads.
//
// Shaft families:
//   Solid:   -   --   (one or two dashes)
//   Dotted:  ..  ...  (two or three dots)
//
// Direction hints embedded in shaft:
//   -left-   -right-   -up-   -down-
//   -l-      -r-       -u-    -d-
//   -le-     -ri-      -do-   (two-char abbreviations)
//   Also without closing dash for one-sided: -left>  -up>
//
// Heads (either end):   >   <   (arrow)   none (open)
//
// Strategy: one ARROW_SPEC token with fragment helpers.
// Order within alternations: longest patterns first.

fragment F_SOLID  : '-' '-'? ;               // - or --
fragment F_DOTTED : '.' '.' '.'? ;           // .. or ...

// Direction hint inside shaft
fragment F_DIR_WORD
    : 'left' | 'right' | 'up' | 'down'
    | 'le' | 'ri' | 'do'
    | 'l' | 'r' | 'u' | 'd'
    ;

// Full shaft with optional embedded direction hint
fragment F_SHAFT_SOLID
    : '-' F_DIR_WORD '-'    // -left-  -right-  -l-
    | '-' F_DIR_WORD        // -left>  (no closing dash; head follows)
    | '--'                   // plain double-dash
    | '-'                    // plain single-dash
    ;

fragment F_SHAFT_DOTTED
    : '..' '.'?             // .. or ...
    ;

// Complete arrow spec token — covers all legal combinations
ARROW_SPEC
    : '<'? F_SHAFT_SOLID '>'?     // solid line with optional heads
    | '<'? F_SHAFT_DOTTED '>'?    // dotted line with optional heads
    ;

// ── Color specification ───────────────────────────────────────────────────
// #colorName  or  #RRGGBB

COLOR
    : '#' [a-zA-Z0-9]+
    ;

// ── Sprite row data ───────────────────────────────────────────────────────
// Inside a sprite body: lines of hex digits (0-9 A-F).

SPRITE_ROW
    : [0-9A-F]+
    ;

// ── Quoted string ─────────────────────────────────────────────────────────

QUOTED_STRING
    : '"' ( '\\' '"' | ~["\r\n] )* '"'
    ;

// ── Punctuation ───────────────────────────────────────────────────────────

LPAREN   : '(' ;
RPAREN   : ')' ;
LBRACK   : '[' ;
RBRACK   : ']' ;
LBRACE   : '{' ;
RBRACE   : '}' ;
FSLASH   : '/' ;
COLON    : ':' ;
COMMA    : ',' ;
STAR     : '*' ;
BANG     : '!' ;
AT       : '@' ;
DOLLAR   : '$' ;
INT      : [0-9]+ ;

// ── Identifier ────────────────────────────────────────────────────────────
// Component ids, aliases, skinparam names.
// Declared after all keyword tokens.

ID
    : [a-zA-Z_] [a-zA-Z0-9_.\-]*
    ;

// ── Comments ──────────────────────────────────────────────────────────────

COMMENT_SINGLE
    : ['] ~[\r\n]*
    ;

COMMENT_MULTI
    : '/' ['] .*? ['] '/'
    ;

// ── Free text ─────────────────────────────────────────────────────────────
// Catch-all for label content, skinparam values, note body lines, etc.
// Declared last — all structural tokens have priority.

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
