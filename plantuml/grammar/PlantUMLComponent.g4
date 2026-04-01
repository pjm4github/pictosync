// PlantUMLComponent.g4
// ANTLR4 grammar for PlantUML Component Diagrams
// Reference: https://plantuml.com/component-diagram

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
    : ( ID | INT )+ ( DOT ( ID | INT )+ )*
    | QUOTED_STRING
    ;

// Generic rest-of-line — consumes mixed tokens until NEWLINE.
restOfLine
    : ( ID | QUOTED_STRING | INT | COLOR | TAG | FREE_TEXT
      | COLON | COMMA | STAR | BANG | FSLASH | LPAREN | RPAREN
      | LBRACK | RBRACK | AT | DOLLAR | DOT | DASH
      | STEREOTYPE_OPEN | STEREOTYPE_CLOSE
      | BRACKET_COMP | CIRCLE_IFACE
      | ARROW_SPEC | LOLLIPOP
      | KW_AS | KW_OF | KW_TO | KW_LEFT | KW_RIGHT | KW_TOP | KW_BOTTOM
      | KW_CENTER | KW_X | KW_DIRECTION
      | KW_COMPONENT | KW_INTERFACE | KW_PORT | KW_PORTIN | KW_PORTOUT
      | KW_PACKAGE | KW_NODE | KW_FOLDER | KW_FRAME | KW_CLOUD
      | KW_DATABASE | KW_RECTANGLE | KW_ACTOR | KW_USECASE
      | KW_HIDE | KW_REMOVE | KW_RESTORE
      | KW_SKINPARAM | KW_SPRITE | KW_PRAGMA
      | KW_SCALE | KW_TITLE | KW_HEADER | KW_FOOTER | KW_CAPTION
      | KW_NOTE | KW_ON | KW_LINK | KW_LEGEND | KW_END | KW_ALLOWMIXING
      | AT_UNLINKED
      )+
    ;

// ── Top-level statement dispatcher ────────────────────────────────────────

statement
    : groupBlock                     // group or standalone (self-terminating)
    | componentFullDecl              // component (decl, block, or body)
    | interfaceDecl     NEWLINE+
    | relationStmt      NEWLINE+
    | noteStmt          NEWLINE+
    | noteBlock                      // self-terminating with 'end note'
    | spriteDecl                     // self-terminating with '}'
    | skinparamBlock                 // self-terminating with '}'
    | skinparamStmt     NEWLINE+
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
// ═══════════════════════════════════════════════════════════════════════════

// Combined component declaration: bracket form, keyword+modifiers, keyword+body, keyword+block
componentFullDecl
    : BRACKET_COMP componentModifier* aliasClause? componentModifier* NEWLINE+
    | KW_COMPONENT elementName aliasClause? componentModifier*
      ( componentBodyDesc NEWLINE+              // component Foo [ body ]
      | LBRACE NEWLINE+ innerStatement* RBRACE NEWLINE+  // component Foo { ports }
      | NEWLINE+                                 // component Foo
      )
    ;

// component Foo [ multi-line description ]
componentBodyDesc
    : LBRACK restOfLine? ( NEWLINE+ restOfLine? )* RBRACK
    ;

innerStatement
    : portDecl       NEWLINE+
    | componentFullDecl
    | interfaceDecl  NEWLINE+
    | COMMENT_SINGLE NEWLINE+
    | COMMENT_MULTI  NEWLINE+
    | NEWLINE+
    ;

portDecl
    : KW_PORT    elementName aliasClause?
    | KW_PORTIN  elementName aliasClause?
    | KW_PORTOUT elementName aliasClause?
    ;

// ═══════════════════════════════════════════════════════════════════════════
// INTERFACE DECLARATIONS
// ═══════════════════════════════════════════════════════════════════════════

interfaceDecl
    : CIRCLE_IFACE elementName aliasClause? componentModifier*
    | KW_INTERFACE elementName aliasClause? componentModifier*
    ;

// ── Element name ──────────────────────────────────────────────────────────

elementName
    : QUOTED_STRING
    | ID
    // Allow keywords used as element names or aliases
    | KW_LEFT | KW_RIGHT | KW_TOP | KW_BOTTOM
    | KW_AS | KW_OF | KW_TO | KW_ON | KW_LINK
    | KW_NOTE | KW_END | KW_CENTER
    ;

aliasClause
    : KW_AS elementName
    ;

// ── Component modifiers ───────────────────────────────────────────────────

componentModifier
    : stereotypeClause
    | COLOR
    | TAG
    ;

stereotypeClause
    : STEREOTYPE_OPEN stereotypeBody STEREOTYPE_CLOSE
    ;

stereotypeBody
    : ( ID | TAG | FREE_TEXT | KW_X
      | KW_COMPONENT | KW_INTERFACE | KW_NODE | KW_DATABASE
      | KW_CLOUD | KW_FRAME | KW_FOLDER | KW_PACKAGE | KW_RECTANGLE
      | KW_ACTOR | KW_USECASE
      | KW_PORT | KW_PORTIN | KW_PORTOUT
      | KW_LEFT | KW_RIGHT | KW_TOP | KW_BOTTOM
      | KW_NOTE | KW_LINK | KW_ON | KW_END
      )*
    ;

// ═══════════════════════════════════════════════════════════════════════════
// GROUP CONTAINERS — recursive nesting
// ═══════════════════════════════════════════════════════════════════════════

groupBlock
    : groupKeyword elementName? aliasClause? componentModifier*
      ( LBRACE NEWLINE+ statement* RBRACE NEWLINE+    // block form
      | NEWLINE+                                       // standalone (no block)
      )
    ;

groupKeyword
    : KW_PACKAGE
    | KW_NODE
    | KW_FOLDER
    | KW_FRAME
    | KW_CLOUD
    | KW_DATABASE
    | KW_RECTANGLE
    | KW_ACTOR
    | KW_USECASE
    ;

// ═══════════════════════════════════════════════════════════════════════════
// RELATION STATEMENTS
// ═══════════════════════════════════════════════════════════════════════════

relationStmt
    : relationRef ( ARROW_SPEC | LOLLIPOP ) relationRef ( COLON restOfLine )?
    ;

relationRef
    : BRACKET_COMP
    | CIRCLE_IFACE elementName
    | QUOTED_STRING
    | ID
    | KW_LEFT | KW_RIGHT | KW_TOP | KW_BOTTOM  // keywords used as aliases
    | KW_NOTE | KW_ON | KW_LINK | KW_END
    ;

// ═══════════════════════════════════════════════════════════════════════════
// NOTE STATEMENTS
// ═══════════════════════════════════════════════════════════════════════════

noteStmt
    : KW_NOTE noteSide KW_OF relationRef ( COLON restOfLine )?
    | KW_NOTE QUOTED_STRING KW_AS elementName
    | KW_NOTE KW_ON KW_LINK COLON restOfLine     // note on link : text
    ;

noteBlock
    : KW_NOTE noteSide KW_OF relationRef COLOR? NEWLINE+
          noteBodyLine+
      KW_END_NOTE NEWLINE+
    | KW_NOTE KW_AS elementName COLOR? NEWLINE+
          noteBodyLine+
      KW_END_NOTE NEWLINE+
    | KW_NOTE KW_ON KW_LINK COLOR? NEWLINE+        // note on link [#color]
          noteBodyLine+
      KW_END_NOTE NEWLINE+
    ;

noteSide
    : KW_LEFT | KW_RIGHT | KW_TOP | KW_BOTTOM
    ;

noteBodyLine
    : ( restOfLine | LBRACE | RBRACE )+ NEWLINE+
    | NEWLINE+
    ;

// ═══════════════════════════════════════════════════════════════════════════
// SPRITE DECLARATION
// ═══════════════════════════════════════════════════════════════════════════

spriteDecl
    : KW_SPRITE TAG spriteDimension? LBRACE NEWLINE+
          spriteRow+
      RBRACE NEWLINE+
    ;

// [WxH/depth] — e.g. [16x16/16]
// Note: '16x16' lexes as INT ID (x16 is an identifier), so we accept that
spriteDimension
    : LBRACK INT ( KW_X | ID ) ( FSLASH INT )? RBRACK
    ;

spriteRow
    : SPRITE_ROW NEWLINE+
    | INT NEWLINE+             // pure-digit rows (e.g. 0000000000)
    | NEWLINE+
    ;

// ═══════════════════════════════════════════════════════════════════════════
// SKINPARAM STATEMENTS
// ═══════════════════════════════════════════════════════════════════════════

skinparamStmt
    : KW_SKINPARAM ( skinparamName | ID ) stereotypeClause? restOfLine?
    ;

skinparamBlock
    : KW_SKINPARAM skinparamName stereotypeClause? LBRACE NEWLINE+
          skinparamEntry*
      RBRACE NEWLINE+
    ;

skinparamName
    : ID ( DOT ID )*
    | groupKeyword
    | KW_COMPONENT
    | KW_INTERFACE
    | KW_NOTE
    | KW_LEGEND
    ;

skinparamEntry
    : restOfLine NEWLINE+
    | NEWLINE+
    ;

// ═══════════════════════════════════════════════════════════════════════════
// VISIBILITY CONTROL STATEMENTS
// ═══════════════════════════════════════════════════════════════════════════

visibilityStmt
    : visibilityKeyword visibilityTarget
    ;

visibilityKeyword
    : KW_HIDE | KW_REMOVE | KW_RESTORE
    ;

visibilityTarget
    : AT_UNLINKED
    | TAG
    | STAR
    | restOfLine
    ;

// ═══════════════════════════════════════════════════════════════════════════
// DIRECTIVES
// ═══════════════════════════════════════════════════════════════════════════

directionStmt
    : KW_LEFT KW_TO KW_RIGHT KW_DIRECTION
    | KW_TOP  KW_TO KW_BOTTOM KW_DIRECTION
    ;

allowMixingStmt
    : KW_ALLOWMIXING
    ;

titleStmt   : KW_TITLE   restOfLine? ;
headerStmt  : KW_HEADER  restOfLine? ;
footerStmt  : KW_FOOTER  restOfLine? ;
captionStmt : KW_CAPTION restOfLine? ;

legendBlock
    : KW_LEGEND legendAlign? NEWLINE+
          noteBodyLine+
      KW_END_LEGEND NEWLINE+
    ;

legendAlign : KW_LEFT | KW_RIGHT | KW_CENTER ;

pragmaStmt
    : BANG KW_PRAGMA ID restOfLine?
    | BANG ID restOfLine?
    ;

scaleStmt
    : KW_SCALE restOfLine
    ;


// ═══════════════════════════════════════════════════════════════════════════
// LEXER RULES
// ═══════════════════════════════════════════════════════════════════════════

// ── Diagram wrappers ──────────────────────────────────────────────────────

STARTUML : '@startuml' ;
ENDUML   : '@enduml' ;

// ── Component bracket notation ────────────────────────────────────────────
// [Name] as one token.  Must NOT match bracket body [ multi\nline ] which
// spans multiple lines — that is handled by componentBodyDesc parser rule.

// Bracket component: [Name] — content must start with a letter or space
// (excludes [16x16/16] sprite dimensions which start with digit)
BRACKET_COMP
    : '[' [ \t]* [a-zA-Z] ~[\]\r\n]* ']'
    ;

// ── Interface circle-paren notation ──────────────────────────────────────

CIRCLE_IFACE : '()' ;

// ── Tag token  $tagName ──────────────────────────────────────────────────

TAG
    : '$' [a-zA-Z_] [a-zA-Z0-9_]*
    ;

// ── @unlinked special target ─────────────────────────────────────────────

AT_UNLINKED : '@unlinked' ;

// ── Declaration keywords ─────────────────────────────────────────────────

KW_COMPONENT  : 'component' ;
KW_INTERFACE  : 'interface' ;
KW_AS         : 'as' ;
KW_PORT       : 'port' ;
KW_PORTIN     : 'portin' ;
KW_PORTOUT    : 'portout' ;

// ── Group container keywords ─────────────────────────────────────────────

KW_PACKAGE    : 'package' ;
KW_NODE       : 'node' ;
KW_FOLDER     : 'folder' ;
KW_FRAME      : 'frame' ;
KW_CLOUD      : 'cloud' ;
KW_DATABASE   : 'database' ;
KW_RECTANGLE  : 'rectangle' ;
KW_ACTOR      : 'actor' ;
KW_USECASE    : 'usecase' ;

// ── Note keywords ────────────────────────────────────────────────────────

KW_END_NOTE   : 'end' [ \t]+ 'note' ;
KW_END_LEGEND : 'end' [ \t]+ 'legend' ;
KW_END        : 'end' ;
KW_NOTE       : 'note' ;
KW_ON         : 'on' ;
KW_LINK       : 'link' ;
KW_LEFT       : 'left' ;
KW_RIGHT      : 'right' ;
KW_TOP        : 'top' ;
KW_BOTTOM     : 'bottom' ;
KW_OF         : 'of' ;

// ── Visibility control keywords ──────────────────────────────────────────

KW_HIDE       : 'hide' ;
KW_REMOVE     : 'remove' ;
KW_RESTORE    : 'restore' ;

// ── Direction / directive keywords ───────────────────────────────────────

KW_TO        : 'to' ;
KW_DIRECTION : 'direction' ;

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
KW_X           : 'x' ;

// ── Stereotype delimiters ────────────────────────────────────────────────

STEREOTYPE_OPEN  : '<<' ;
STEREOTYPE_CLOSE : '>>' ;

// ── Arrow specification token ────────────────────────────────────────────

fragment F_DIR_WORD
    : 'left' | 'right' | 'up' | 'down'
    | 'le' | 'ri' | 'do'
    | 'l' | 'r' | 'u' | 'd'
    ;

fragment F_INLINE_STYLE
    : '[' ~[\]\r\n]* ']'
    ;

ARROW_SPEC
    : '<' '-' F_DIR_WORD? F_INLINE_STYLE? '-'? '>'?
    | '-' F_DIR_WORD? F_INLINE_STYLE? '-'? '>'
    | '-' F_DIR_WORD? F_INLINE_STYLE? '-'
    | '<' '-' '-' F_DIR_WORD? F_INLINE_STYLE? '-'? '>'?
    | '-' '-' F_DIR_WORD? F_INLINE_STYLE? '-'? '>'?
    | '<' '.' '.' F_DIR_WORD? '.'? '>'?
    | '.' '.' F_DIR_WORD? '.'? '>'?
    | '-' F_DIR_WORD? F_INLINE_STYLE? '.' '>'    // mixed: -left.> -r.>
    | '.' '>'
    ;

// ── Lollipop (required interface) ────────────────────────────────────────
// --( is the lollipop connector for required interface

LOLLIPOP
    : '-' '-' '('
    ;

// ── Color specification ──────────────────────────────────────────────────

COLOR
    : '#' [a-zA-Z0-9]+
    ;

// ── Sprite row data ──────────────────────────────────────────────────────
// Sprite hex rows: at least 8 hex chars to avoid matching short names like FF, DB1
// Smallest practical sprite row is 8 chars (4x4 at 2-bit depth)

SPRITE_ROW
    : [0-9A-F] [0-9A-F] [0-9A-F] [0-9A-F] [0-9A-F] [0-9A-F] [0-9A-F] [0-9A-F]+
    ;

// ── Quoted string ────────────────────────────────────────────────────────

// Quoted string: handles \" escape and "" (PlantUML monospace delimiter)
QUOTED_STRING
    : '"' ( '\\' '"' | '""' | ~["\r\n] )* '"'
    ;

// ── Punctuation ──────────────────────────────────────────────────────────

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
DOT      : '.' ;
DASH     : '-' ;
INT      : [0-9]+ ;

// ── Identifier ───────────────────────────────────────────────────────────

ID
    : [a-zA-Z_] [a-zA-Z0-9_.\-]*
    ;

// ── Comments ─────────────────────────────────────────────────────────────

COMMENT_SINGLE
    : ['] ~[\r\n]*
    ;

COMMENT_MULTI
    : '/' ['] .*? ['] '/'
    ;

// ── Free text ────────────────────────────────────────────────────────────
// Restricted: must NOT start with chars that begin structural tokens.

FREE_TEXT
    : ~[a-zA-Z0-9_"'()[\]{}<>#$@!:,*/~=\-.\r\n \t|] ~[\r\n]*
    | [&%^;?\\`+] ~[\r\n]*
    ;

// ── Newline ──────────────────────────────────────────────────────────────

NEWLINE
    : [\r\n]+
    ;

// ── Whitespace ───────────────────────────────────────────────────────────

WS
    : [ \t]+ -> skip
    ;
