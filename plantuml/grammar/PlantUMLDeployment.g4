// PlantUMLDeployment.g4
// ANTLR4 grammar for PlantUML Deployment Diagrams
// Reference: https://plantuml.com/deployment-diagram
//
// ── Diagram wrapper ───────────────────────────────────────────────────────
//   @startuml [filename]
//   ...statements...
//   @enduml
//
// ── Element declarations ────────────────────────────────────────────────
//   Deployment diagrams support a large set of element types:
//
//   Container elements (can nest children with { }):
//     actor, agent, artifact, boundary, card, circle, cloud, collections,
//     component, control, database, entity, file, folder, frame, hexagon,
//     interface, label, node, package, person, queue, rectangle, stack,
//     storage, usecase
//
//   Shorthand forms:
//     [Name]           component bracket notation
//     :Name:           actor colon notation
//     () "Name"        interface circle-paren notation
//     (Name)           usecase paren notation
//
//   General keyword form:
//     keyword "Display Name" as alias <<stereotype>> #color $tag
//     keyword name [ multi-line description body ]
//     keyword name { nested children }
//
// ── Port declarations (inside element body only) ────────────────────────
//   port    portId
//   portin  portId
//   portout portId
//
// ── Relation / link statements ──────────────────────────────────────────
//   A -- B                  solid line
//   A --> B                 solid arrow
//   A ..> B                 dotted arrow
//   A -left-> B             directional hint
//   A --> B : label          with label
//   A -[#red]-> B           styled link (color/bold/dashed)
//   A --0 B                 lollipop connector
//
// ── Note statements ─────────────────────────────────────────────────────
//   note left of X : text
//   note right of X
//     ...
//   end note
//   note as N
//     ...
//   end note
//
// ── Other directives ────────────────────────────────────────────────────
//   left to right direction
//   top to bottom direction
//   title text
//   skinparam paramName value
//   !pragma key value
//   allowmixing
//   together { ... }
//
// ── Lexer ordering notes ────────────────────────────────────────────────
//   1. STARTUML / ENDUML before AT '@'
//   2. ARROW_SPEC tokens (longest first) before DASH '-' and DOT '.'
//   3. STEREOTYPE_OPEN '<<' before any LT; STEREOTYPE_CLOSE '>>' before GT
//   4. CIRCLE_IFACE '()' before LPAREN '('
//   5. BRACKET_COMP '[..]' captures the full [name] as one token
//   6. ACTOR_COLON ':name:' captures actor shorthand as one token
//   7. TAG '$id' token ($ prefix) declared before DOLLAR '$'
//   8. AT_UNLINKED '@unlinked' before AT '@'
//   9. KW_END_NOTE 'end note' before KW_END 'end' (compound form first)
//  10. All keyword tokens before ID

grammar PlantUMLDeployment;

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

// ── Top-level statement dispatcher ──────────────────────────────────────

statement
    : elementDecl       NEWLINE+
    | elementBlock                   // self-terminating with '}'
    | relationStmt      NEWLINE+
    | noteStmt          NEWLINE+
    | noteBlock                      // self-terminating with 'end note'
    | togetherBlock                  // self-terminating with '}'
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
// ELEMENT DECLARATIONS (non-nesting, single-line)
//
// Deployment diagrams accept all element keywords.  The general form is:
//
//   keyword elementName [as alias] [<<stereotype>>] [#color] [$tag]...
//   [Name]              bracket component shorthand
//   :Name:              actor colon shorthand
//   () "Name"           interface circle-paren shorthand
//   (Name)              usecase paren shorthand
//
// Modifiers (stereotype, color, tag) may appear in any order.
// ═══════════════════════════════════════════════════════════════════════════

elementDecl
    : BRACKET_COMP aliasClause? elementModifier*
    | ACTOR_COLON aliasClause? elementModifier*
    | CIRCLE_IFACE elementName aliasClause? elementModifier*
    | USECASE_PAREN aliasClause? elementModifier*
    | elementKeyword elementName aliasClause?
      elementModifier*
      descriptionBody?
    ;

// Description body: [ multi-line text ]
descriptionBody
    : LBRACK bodyText RBRACK
    ;

// ═══════════════════════════════════════════════════════════════════════════
// ELEMENT BLOCKS (nesting with { })
//
// Any element keyword can contain nested children:
//   keyword "Name" [#color] [<<stereotype>>] {
//       statement*
//   }
//
// The "together" grouping is a special non-keyword block.
// ═══════════════════════════════════════════════════════════════════════════

elementBlock
    : elementKeyword elementName? aliasClause? elementModifier*
      LBRACE NEWLINE+
          blockStatement*
      RBRACE NEWLINE+
    ;

// Statements allowed inside an element block (recursive nesting)
blockStatement
    : elementDecl       NEWLINE+
    | elementBlock                   // nested container
    | portDecl          NEWLINE+
    | relationStmt      NEWLINE+
    | noteStmt          NEWLINE+
    | noteBlock
    | COMMENT_SINGLE    NEWLINE+
    | COMMENT_MULTI     NEWLINE+
    | NEWLINE+
    ;

// Port declarations — valid inside element body
portDecl
    : KW_PORT    elementName
    | KW_PORTIN  elementName
    | KW_PORTOUT elementName
    ;

// Together grouping — layout hint, not a container keyword
togetherBlock
    : KW_TOGETHER LBRACE NEWLINE+
          statement*
      RBRACE NEWLINE+
    ;

// ═══════════════════════════════════════════════════════════════════════════
// ALL ELEMENT KEYWORDS
//
// Deployment diagrams accept a very large set of element types.
// ═══════════════════════════════════════════════════════════════════════════

elementKeyword
    : KW_ACTOR
    | KW_AGENT
    | KW_ARTIFACT
    | KW_BOUNDARY
    | KW_CARD
    | KW_CIRCLE
    | KW_CLOUD
    | KW_COLLECTIONS
    | KW_COMPONENT
    | KW_CONTROL
    | KW_DATABASE
    | KW_ENTITY
    | KW_FILE
    | KW_FOLDER
    | KW_FRAME
    | KW_HEXAGON
    | KW_INTERFACE
    | KW_LABEL
    | KW_NODE
    | KW_PACKAGE
    | KW_PERSON
    | KW_PROCESS
    | KW_QUEUE
    | KW_RECTANGLE
    | KW_STACK
    | KW_STORAGE
    | KW_USECASE
    ;

// ── Element name ────────────────────────────────────────────────────────

elementName
    : QUOTED_STRING
    | ID
    ;

// ── Alias ───────────────────────────────────────────────────────────────

aliasClause
    : KW_AS elementName
    ;

// ── Element modifiers ───────────────────────────────────────────────────

elementModifier
    : stereotypeClause
    | colorSpec
    | TAG
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

spotSpec
    : LPAREN spotChar COMMA colorSpec RPAREN
    ;

spotChar : ID | INT ;

stereotypeText
    : FREE_TEXT
    | ID
    ;

bodyText
    : restOfLine?
    ;

// Generic "rest of line" — consumes any tokens until NEWLINE.
// Used for label text, skinparam values, note bodies, title text, etc.
restOfLine
    : ( ID | QUOTED_STRING | INT | COLOR | TAG | FREE_TEXT
      | COLON | COMMA | STAR | BANG | FSLASH | LPAREN | RPAREN
      | LBRACK | RBRACK | AT | DOLLAR
      | STEREOTYPE_OPEN | STEREOTYPE_CLOSE
      | BRACKET_COMP | ACTOR_COLON | USECASE_PAREN
      | ARROW_SPEC
      | KW_AS | KW_OF | KW_TO | KW_LEFT | KW_RIGHT | KW_TOP | KW_BOTTOM
      | KW_CENTER | KW_X | KW_DIRECTION
      | elementKeyword
      )+
    ;

// ═══════════════════════════════════════════════════════════════════════════
// RELATION STATEMENTS
//
// Format:  lhsRef  arrowSpec  rhsRef  [: label]
//
// Endpoints can be:
//   [Name]    bracket component reference
//   :Name:    actor colon reference
//   ()Name    circle paren interface reference
//   (Name)    usecase paren reference
//   Name      bare identifier
//   "Name"    quoted name
// ═══════════════════════════════════════════════════════════════════════════

relationStmt
    : relationRef ARROW_SPEC relationRef ( COLON labelText )?
    ;

relationRef
    : BRACKET_COMP
    | ACTOR_COLON
    | USECASE_PAREN
    | QUOTED_STRING
    | ID
    ;

labelText
    : restOfLine
    ;

// ═══════════════════════════════════════════════════════════════════════════
// NOTE STATEMENTS
// ═══════════════════════════════════════════════════════════════════════════

noteStmt
    : KW_NOTE noteSide KW_OF relationRef ( COLON restOfLine )?
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
    : restOfLine NEWLINE+
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

spriteDimension
    : LBRACK INT KW_X INT ( FSLASH INT )? RBRACK
    ;

spriteRow
    : SPRITE_ROW NEWLINE+
    | NEWLINE+
    ;

// ═══════════════════════════════════════════════════════════════════════════
// SKINPARAM STATEMENTS
// ═══════════════════════════════════════════════════════════════════════════

skinparamStmt
    : KW_SKINPARAM skinparamPath restOfLine?
    ;

skinparamBlock
    : KW_SKINPARAM skinparamPath LBRACE NEWLINE+
          skinparamEntry*
      RBRACE NEWLINE+
    ;

skinparamPath
    : skinparamWord ( '.' skinparamWord )*
    ;

// A skinparam path segment — can be an ID or an element keyword
// (e.g., `skinparam actor { ... }`, `skinparam node.BackgroundColor #FFF`)
skinparamWord
    : ID
    | elementKeyword
    ;

skinparamEntry
    : skinparamWord restOfLine NEWLINE+
    | NEWLINE+
    ;

// ═══════════════════════════════════════════════════════════════════════════
// VISIBILITY CONTROL
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
    | BANG ID restOfLine?           // !define, !include, !ifdef, etc.
    ;

scaleStmt
    : KW_SCALE restOfLine
    ;


// ═══════════════════════════════════════════════════════════════════════════
// LEXER RULES
// ═══════════════════════════════════════════════════════════════════════════

// ── Diagram wrappers ────────────────────────────────────────────────────

STARTUML : '@startuml' ;
ENDUML   : '@enduml' ;

// ── Component bracket notation [Name] ───────────────────────────────────

BRACKET_COMP
    : '[' ~[\]\r\n]+ ']'
    ;

// ── Actor colon notation :Name: ─────────────────────────────────────────

ACTOR_COLON
    : ':' ~[:\r\n"]+ ':'
    ;

// ── Usecase paren notation (Name) ───────────────────────────────────────
// Declared after CIRCLE_IFACE to avoid ambiguity with '()'.

USECASE_PAREN
    : '(' ~[)\r\n]+ ')'
    ;

// ── Interface circle-paren notation () ──────────────────────────────────

CIRCLE_IFACE : '()' ;

// ── Tag token $tagName ──────────────────────────────────────────────────

TAG
    : '$' [a-zA-Z_] [a-zA-Z0-9_]*
    ;

// ── @unlinked special target ────────────────────────────────────────────

AT_UNLINKED : '@unlinked' ;

// ── Element keywords ────────────────────────────────────────────────────

KW_ACTOR       : 'actor' ;
KW_AGENT       : 'agent' ;
KW_ARTIFACT    : 'artifact' ;
KW_BOUNDARY    : 'boundary' ;
KW_CARD        : 'card' ;
KW_CIRCLE      : 'circle' ;
KW_CLOUD       : 'cloud' ;
KW_COLLECTIONS : 'collections' ;
KW_COMPONENT   : 'component' ;
KW_CONTROL     : 'control' ;
KW_DATABASE    : 'database' ;
KW_ENTITY      : 'entity' ;
KW_FILE        : 'file' ;
KW_FOLDER      : 'folder' ;
KW_FRAME       : 'frame' ;
KW_HEXAGON     : 'hexagon' ;
KW_INTERFACE   : 'interface' ;
KW_LABEL       : 'label' ;
KW_NODE        : 'node' ;
KW_PACKAGE     : 'package' ;
KW_PERSON      : 'person' ;
KW_PROCESS     : 'process' ;
KW_QUEUE       : 'queue' ;
KW_RECTANGLE   : 'rectangle' ;
KW_STACK       : 'stack' ;
KW_STORAGE     : 'storage' ;
KW_USECASE     : 'usecase' ;

// ── Port keywords ───────────────────────────────────────────────────────

KW_PORT    : 'port' ;
KW_PORTIN  : 'portin' ;
KW_PORTOUT : 'portout' ;

// ── Common keywords ─────────────────────────────────────────────────────

KW_AS         : 'as' ;
KW_TOGETHER   : 'together' ;

// ── Note keywords ───────────────────────────────────────────────────────

KW_END_NOTE   : 'end' [ \t]+ 'note' ;
KW_END_LEGEND : 'end' [ \t]+ 'legend' ;
KW_END        : 'end' ;
KW_NOTE       : 'note' ;
KW_LEFT       : 'left' ;
KW_RIGHT      : 'right' ;
KW_TOP        : 'top' ;
KW_BOTTOM     : 'bottom' ;
KW_OF         : 'of' ;

// ── Visibility keywords ─────────────────────────────────────────────────

KW_HIDE    : 'hide' ;
KW_REMOVE  : 'remove' ;
KW_RESTORE : 'restore' ;

// ── Direction keywords ──────────────────────────────────────────────────

KW_TO        : 'to' ;
KW_DIRECTION : 'direction' ;

// ── Directive keywords ──────────────────────────────────────────────────

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

// ── Stereotype delimiters ───────────────────────────────────────────────

STEREOTYPE_OPEN  : '<<' ;
STEREOTYPE_CLOSE : '>>' ;

// ── Arrow specification token ───────────────────────────────────────────
// Captures all PlantUML deployment diagram arrow/line forms as one token.
// The visitor decodes direction, shaft style (solid/dotted), and arrowheads.
//
// Shaft families:
//   Solid:   -   --   (one or two dashes)
//   Dotted:  ..  ...  (two or three dots)
//   Bold:    ==        (double equals)
//   Wavy:    ~~        (double tilde)
//
// Direction hints: -left- -right- -up- -down- (or abbreviations -l- -r- -u- -d-)
//
// Heads: > < (arrow), none (open line)
// Special heads: 0 (lollipop), * (filled diamond), o (open diamond),
//                + (plus), # (hash), >> (double arrow)

fragment F_DIR_WORD
    : 'left' | 'right' | 'up' | 'down'
    | 'le' | 'ri' | 'do'
    | 'l' | 'r' | 'u' | 'd'
    ;

fragment F_SHAFT_SOLID
    : '-' F_DIR_WORD '-'
    | '-' F_DIR_WORD
    | '--'
    | '-'
    ;

fragment F_SHAFT_DOTTED
    : '..' '.'?
    ;

fragment F_SHAFT_BOLD
    : '=='
    ;

fragment F_SHAFT_WAVY
    : '~~'
    ;

// Styled shaft: -[#color]-> or -[bold]-> etc.
fragment F_SHAFT_STYLED
    : '-' '[' ~[\]\r\n]* ']' '-'?
    ;

ARROW_SPEC
    : '<'? F_SHAFT_SOLID '>'?
    | '<'? F_SHAFT_DOTTED '>'?
    | '<'? F_SHAFT_BOLD '>'?
    | '<'? F_SHAFT_WAVY '>'?
    | '<'? F_SHAFT_STYLED '>'?
    ;

// ── Color specification ─────────────────────────────────────────────────

COLOR
    : '#' [a-zA-Z0-9]+
    | '#' [a-zA-Z0-9]+ ';' ~[\r\n{]* // Extended style: #pink;line:red;line.bold
    ;

// ── Sprite row data ─────────────────────────────────────────────────────

SPRITE_ROW
    : [0-9A-F]+
    ;

// ── Quoted string ───────────────────────────────────────────────────────

QUOTED_STRING
    : '"' ( '\\' '"' | ~["\r\n] )* '"'
    ;

// ── Punctuation ─────────────────────────────────────────────────────────

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

// ── Identifier ──────────────────────────────────────────────────────────

ID
    : [a-zA-Z_] [a-zA-Z0-9_.\-]*
    ;

// ── Comments ────────────────────────────────────────────────────────────

COMMENT_SINGLE
    : ['] ~[\r\n]*
    ;

COMMENT_MULTI
    : '/' ['] .*? ['] '/'
    ;

// ── Rest-of-line token ──────────────────────────────────────────────────
// Captures text that doesn't start with a letter, digit, quote, bracket,
// paren, or other structural character.  This prevents FREE_TEXT from
// consuming keyword-led lines.  Parser rules use 'restOfLine' to gather
// label text, skinparam values, etc. as a sequence of mixed tokens.

FREE_TEXT
    : ~[a-zA-Z0-9_"'()[\]{}<>#$@!:,*/~=\-.\r\n \t] ~[\r\n]*
    | [&%^;?\\|`+] ~[\r\n]*
    ;

// ── Newline ─────────────────────────────────────────────────────────────

NEWLINE
    : [\r\n]+
    ;

// ── Whitespace ──────────────────────────────────────────────────────────

WS
    : [ \t]+ -> skip
    ;
