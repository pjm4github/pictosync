// PlantUMLArchimate.g4
// ANTLR4 grammar for PlantUML ArchiMate Diagrams
// Reference: https://plantuml.com/archimate-diagram
//
// ── Diagram wrappers ──────────────────────────────────────────────────────
//   @startuml [filename]
//   ...statements...
//   @enduml
//
//   @startuml
//   listsprite
//   @enduml
//
// ── ArchiMate element declaration ────────────────────────────────────────
//   archimate #Color "Label" as alias <<stereotype>>
//   archimate #Color "Label" <<stereotype>>
//   archimate #Color elementId
//   archimate "Label" as alias
//   archimate elementId
//
//   Color may be a named ArchiMate layer keyword or any #rrggbb / #name:
//     Business | Application | Motivation | Strategy
//     Technology | Physical | Implementation
//     #lightgreen  #red  #orange  etc.
//
//   Stereotype examples:
//     <<technology-device>>
//     <<$bProcess>>
//     <<behavior>>
//     <<$archimate/application-service>>
//     <<$aComponent>><<behavior>>     (multiple stereotypes on one element)
//
// ── Rectangle element (used in ArchiMate context) ────────────────────────
//   rectangle "Label" as alias <<stereo>> #Color
//   rectangle Id <<stereo>><<stereo>> #Color
//   rectangle Id #Color
//   rectangle Id { ... }             grouped rectangle
//
// ── Circle element (junction) ─────────────────────────────────────────────
//   circle #black
//   circle #whitesmoke
//   circle Id #color
//   () Id                            interface-circle notation (from component)
//
// ── Sprite declaration ────────────────────────────────────────────────────
//   sprite $name jar:archimate/icon-name
//   sprite $name jar:archimate/icon-name-with-dashes
//
// ── Preprocessor directives ───────────────────────────────────────────────
//   !define MacroName circle #color
//   !define MacroName keyword [args]
//   !include <archimate/Archimate>
//   !include "localfile.iuml"
//   !pragma key value
//
// ── Macro invocations (from !include <archimate/Archimate>) ──────────────
//   Category_ElementName(id, "description")
//   Rel_RelationType(from, to, "label")
//   Rel_RelationType_Direction(from, to, "label")
//
//   Categories: Motivation Business Application Technology
//               Strategy Physical Implementation
//   ElementNames: Stakeholder Driver Assessment Goal Outcome
//                 Principle Requirement Constraint Meaning Value
//                 Resource Capability CourseOfAction ValueStream
//                 BusinessActor BusinessRole BusinessCollaboration
//                 BusinessInterface BusinessProcess BusinessFunction
//                 BusinessInteraction BusinessEvent BusinessService
//                 BusinessObject Contract Representation Product
//                 ApplicationComponent ApplicationCollaboration
//                 ApplicationInterface ApplicationFunction
//                 ApplicationInteraction ApplicationProcess
//                 ApplicationEvent ApplicationService DataObject
//                 TechnologyFunction TechnologyProcess TechnologyInteraction
//                 TechnologyEvent TechnologyService TechnologyObject
//                 Node Equipment Facility DistributionNetwork
//                 Material SystemSoftware ... (open-ended)
//
//   RelationTypes: Access Aggregation Assignment Association
//                  Composition Flow Influence Realization
//                  Serving Specialization Triggering
//                  (also: Access_r Access_w Access_rw Association_dir)
//   Directions: Up Down Left Right
//
// ── Relations / arrows (native PlantUML syntax) ──────────────────────────
//   A --> B                         solid arrow
//   A -> B                          short solid arrow
//   A -up-> B  -down->  -left->  -right->   direction hint
//   A *-down- B                     composition
//   A -right->> B                   realization-style
//   A .up.|> B                      dotted with open arrowhead
//   A -- B                          association line
//   A .. B                          dotted line
//   All with optional ': label'
//
// ── Legend block ──────────────────────────────────────────────────────────
//   legend [left|right|center]
//     ...
//   endlegend
//
// ── Other directives ──────────────────────────────────────────────────────
//   skinparam key value
//   skinparam ElementName<<stereo>> { key value }
//   skinparam rectangle<<behavior>> { roundCorner 25 }
//   left to right direction
//   top to bottom direction
//   title text
//   header text
//   footer text
//   scale N
//
// ── Comments ──────────────────────────────────────────────────────────────
//   ' single-line comment
//   /' multi-line comment '/
//
// ── Lexer ordering notes ──────────────────────────────────────────────────
//   1.  STARTUML / ENDUML           before ID
//   2.  STEREO_MULTI '<<...>><<>>'  before STEREO_SINGLE '<<...>>'
//   3.  STEREO_SINGLE '<<...>>'     before LT '<'
//   4.  ARROW_SPEC                  composite; covers all arrow variants
//   5.  JAR_REF 'jar:...'           before COLON
//   6.  ARCHIMATE_COLOR layer names — keyword tokens before ID
//   7.  COLOR '#...'                before HASH '#'
//   8.  MACRO_CALL 'X_Y(z,...)'     before ID (uses ID-like prefix)
//   9.  PREPROCESSOR '!define' etc. before BANG '!'
//  10.  All keyword tokens           before ID

grammar PlantUMLArchimate;

// ═══════════════════════════════════════════════════════════════════════════
// PARSER RULES
// ═══════════════════════════════════════════════════════════════════════════

diagram
    : NEWLINE* STARTUML filenameHint? NEWLINE+
      ( KW_LISTSPRITE NEWLINE+ | statement* )
      ENDUML NEWLINE*
      EOF
    ;

filenameHint
    : ID
    | QUOTED_STRING
    ;

// ── Statement dispatcher ──────────────────────────────────────────────────

statement
    : archimateDecl     NEWLINE+
    | rectangleDecl     NEWLINE+
    | rectangleBlock               // self-terminating
    | circleDecl        NEWLINE+
    | interfaceDecl     NEWLINE+
    | spriteDecl        NEWLINE+
    | macroCall         NEWLINE+
    | relationStmt      NEWLINE+
    | preprocessorStmt  NEWLINE+
    | legendBlock                  // self-terminating
    | skinparamStmt     NEWLINE+
    | skinparamBlock               // self-terminating
    | directionStmt     NEWLINE+
    | titleStmt         NEWLINE+
    | headerStmt        NEWLINE+
    | footerStmt        NEWLINE+
    | scaleStmt         NEWLINE+
    | COMMENT_SINGLE    NEWLINE+
    | COMMENT_MULTI     NEWLINE+
    | NEWLINE+
    ;

// ═══════════════════════════════════════════════════════════════════════════
// ARCHIMATE ELEMENT DECLARATION
//
//   archimate #Color "Label" as alias <<stereo>><<stereo>>
//   archimate #Color elementId <<stereo>>
//   archimate "Label" as alias
//   archimate elementId
//
// The color field may be a named ArchiMate layer keyword (Business,
// Application, etc.) or any #color token.
// Multiple stereotypes may follow the element name.
// ═══════════════════════════════════════════════════════════════════════════

archimateDecl
    : KW_ARCHIMATE archimateColor? elementName aliasClause? stereoList?
    ;

// ArchiMate layer color — either a named keyword or generic #color
archimateColor
    : KW_BUSINESS
    | KW_APPLICATION
    | KW_MOTIVATION
    | KW_STRATEGY
    | KW_TECHNOLOGY
    | KW_PHYSICAL
    | KW_IMPLEMENTATION
    | COLOR                          // #rrggbb or #name
    ;

// Element name: quoted string or bare identifier
elementName
    : QUOTED_STRING
    | ID
    ;

// Alias clause
aliasClause
    : KW_AS elementName
    ;

// One or more stereotype annotations
stereoList
    : stereo+
    ;

stereo
    : STEREO_SINGLE
    ;

// ═══════════════════════════════════════════════════════════════════════════
// RECTANGLE ELEMENT
//
//   rectangle "Label" as alias <<stereo>><<stereo>> #Color
//   rectangle Id <<stereo>> #Color
//   rectangle Id #Color { ... }    grouped rectangle
// ═══════════════════════════════════════════════════════════════════════════

rectangleDecl
    : KW_RECTANGLE elementName aliasClause? stereoList? COLOR?
    ;

rectangleBlock
    : KW_RECTANGLE elementName aliasClause? stereoList? COLOR?
      LBRACE NEWLINE+
          statement*
      RBRACE NEWLINE+
    ;

// ═══════════════════════════════════════════════════════════════════════════
// CIRCLE ELEMENT (junction)
//
//   circle #black
//   circle #whitesmoke
//   circle Id #color
// ═══════════════════════════════════════════════════════════════════════════

circleDecl
    : KW_CIRCLE elementName? COLOR?
    ;

// ── Interface circle notation '() Name' ───────────────────────────────────
//   () JunctionAnd
//   () JunctionOr

interfaceDecl
    : CIRCLE_IFACE elementName
    ;

// ═══════════════════════════════════════════════════════════════════════════
// SPRITE DECLARATION
//
//   sprite $name jar:archimate/icon-name
//
// The JAR_REF token captures 'jar:archimate/...' as one token.
// ═══════════════════════════════════════════════════════════════════════════

spriteDecl
    : KW_SPRITE TAG JAR_REF
    ;

// ═══════════════════════════════════════════════════════════════════════════
// MACRO INVOCATIONS
//
// ArchiMate stdlib macros follow the pattern:
//   Category_ElementName(id, "description")
//   Rel_RelationType(from, to, "label")
//   Rel_RelationType_Direction(from, to, "label")
//   MacroName(arg, ...)             any macro call
//
// The MACRO_CALL token captures the macro name (Category_Element form).
// Arguments are parsed as a comma-separated list inside parentheses.
// ═══════════════════════════════════════════════════════════════════════════

macroCall
    : MACRO_CALL LPAREN macroArgList RPAREN
    ;

macroArgList
    : macroArg ( COMMA macroArg )*
    ;

macroArg
    : QUOTED_STRING
    | ID
    | FREE_TEXT_ARG    // unquoted text argument (e.g. plain label)
    ;

// ═══════════════════════════════════════════════════════════════════════════
// RELATION / ARROW STATEMENTS
//
//   A --> B
//   A -up-> B
//   A *-down- B
//   A .up.|> B
//   A -- B : label
//   (All standard PlantUML component-style arrows)
// ═══════════════════════════════════════════════════════════════════════════

relationStmt
    : relationRef ARROW_SPEC relationRef ( COLON FREE_TEXT )?
    ;

relationRef
    : QUOTED_STRING
    | ID
    ;

// ═══════════════════════════════════════════════════════════════════════════
// PREPROCESSOR DIRECTIVES
//
//   !define MacroName circle #color
//   !define MacroName keyword
//   !include <archimate/Archimate>
//   !include "file.iuml"
//   !pragma key value
// ═══════════════════════════════════════════════════════════════════════════

preprocessorStmt
    : PREPROCESSOR FREE_TEXT?
    ;

// ═══════════════════════════════════════════════════════════════════════════
// LEGEND BLOCK
//
//   legend [left|right|center]
//     ...
//   endlegend
// ═══════════════════════════════════════════════════════════════════════════

legendBlock
    : KW_LEGEND legendAlign? NEWLINE+
          legendLine*
      KW_ENDLEGEND NEWLINE+
    ;

legendAlign
    : KW_LEFT | KW_RIGHT | KW_CENTER
    ;

legendLine
    : FREE_TEXT NEWLINE+
    | NEWLINE+
    ;

// ═══════════════════════════════════════════════════════════════════════════
// SKINPARAM
//
//   skinparam key value
//   skinparam rectangle<<stereo>> { key value }
//   skinparam nodesep 4
// ═══════════════════════════════════════════════════════════════════════════

skinparamStmt
    : KW_SKINPARAM skinparamTarget FREE_TEXT?
    ;

skinparamBlock
    : KW_SKINPARAM skinparamTarget LBRACE NEWLINE+
          skinparamEntry*
      RBRACE NEWLINE+
    ;

// Target: plain id, id with stereotype qualifier
skinparamTarget
    : ID STEREO_SINGLE?
    ;

skinparamEntry
    : ID FREE_TEXT NEWLINE+
    | NEWLINE+
    ;

// ── Direction, title, header, footer, scale ───────────────────────────────

directionStmt
    : KW_LEFT KW_TO KW_RIGHT KW_DIRECTION
    | KW_TOP  KW_TO KW_BOTTOM KW_DIRECTION
    ;

titleStmt   : KW_TITLE   FREE_TEXT? ;
headerStmt  : KW_HEADER  FREE_TEXT? ;
footerStmt  : KW_FOOTER  FREE_TEXT? ;
scaleStmt   : KW_SCALE   FREE_TEXT ;


// ═══════════════════════════════════════════════════════════════════════════
// LEXER RULES
// ═══════════════════════════════════════════════════════════════════════════
//
// Critical ordering:
//   1.  STARTUML / ENDUML         before ID
//   2.  STEREO_SINGLE '<<...>>'   before any bare '<'
//   3.  ARROW_SPEC                composite; covers all arrow variants
//   4.  JAR_REF 'jar:...'         before COLON (starts with 'jar:')
//   5.  MACRO_CALL 'Cat_Elem'     before ID (has underscore pattern Cat_Elem)
//   6.  PREPROCESSOR '!define'    composite; before BANG '!'
//   7.  CIRCLE_IFACE '()'         before LPAREN
//   8.  COLOR '#...'              before HASH '#'
//   9.  TAG '$name'               before DOLLAR '$'
//  10.  ArchiMate layer keywords  before ID
//  11.  COMMENT_SINGLE / MULTI    before FREE_TEXT

// ── Diagram wrappers ──────────────────────────────────────────────────────

STARTUML : '@startuml' ;
ENDUML   : '@enduml' ;

// ── Stereotype token ──────────────────────────────────────────────────────
// Captures '<<...>>' as one token; handles dashes, slashes, dollar signs,
// and asterisks inside (e.g. <<technology-device>>, <<$bProcess>>,
// <<$archimate/application-service>>, <<behavior>>).
// Declared before any bare '<' to ensure longest match wins.

STEREO_SINGLE
    : '<<' ~[>\r\n]+ '>>'
    ;

// ── Arrow specification ───────────────────────────────────────────────────
// Covers all PlantUML component/archimate arrow forms:
//   -->  ->  <--  <-
//   -up->  -down->  -left->  -right->  (and abbreviated -u-> etc.)
//   *-down-  *--  (composition prefix)
//   .up.|>  ..>  ..  (dotted forms)
//   --  (plain association line)
// Uses fragments for direction words and shaft variants.

fragment F_DIR
    : 'up' | 'down' | 'left' | 'right'
    | 'u' | 'd' | 'l' | 'r'
    ;

// Solid shaft with optional direction and optional composition prefix '*'
fragment F_SOLID_SHAFT
    : '*'? '-' F_DIR? '-'* '>'?
    | '*'? '-' F_DIR? '-'*
    | '--'
    | '-'
    ;

// Dotted shaft with optional direction and arrowhead
fragment F_DOTTED_SHAFT
    : '.' '.'+ F_DIR? '.' * '|'? '>'?
    | '.' F_DIR? '.'+ '|'? '>'?
    ;

ARROW_SPEC
    : '<'? F_SOLID_SHAFT '>'?    // solid arrows and lines
    | '<'? F_DOTTED_SHAFT '>'?   // dotted arrows and lines
    ;

// ── Jar reference (sprite source) ────────────────────────────────────────
// Captures 'jar:archimate/icon-name' as one token.
// Must be declared before COLON so 'jar:' is not split.

JAR_REF
    : 'jar:' [a-zA-Z0-9/\-]+
    ;

// ── Preprocessor directives ───────────────────────────────────────────────
// Captures the entire '!define ...' / '!include ...' / '!pragma ...' line
// as one composite token starting with '!'.
// Declared before BANG '!' so the full directive wins.

PREPROCESSOR
    : '!' ( 'define' | 'include' | 'pragma' | 'undefine' | 'ifdef' | 'ifndef'
           | 'else' | 'endif' | 'import' ) ~[\r\n]*
    ;

// ── Interface circle notation ─────────────────────────────────────────────
// '()' used for junction circles (from component diagram style).
// Declared before LPAREN.

CIRCLE_IFACE : '()' ;

// ── Tag token '$name' ─────────────────────────────────────────────────────
// Sprite names are prefixed with '$'.
// Declared before DOLLAR.

TAG
    : '$' [a-zA-Z_][a-zA-Z0-9_/\-]*
    ;

// ── Color token ───────────────────────────────────────────────────────────

COLOR
    : '#' [a-zA-Z0-9\-]+
    ;

// ── Macro call token ──────────────────────────────────────────────────────
// Matches macro names of the form:
//   Category_ElementName       e.g. Motivation_Stakeholder
//   Rel_RelationType            e.g. Rel_Composition
//   Rel_RelationType_Direction  e.g. Rel_Composition_Down
// Pattern: starts with uppercase, contains underscore(s).
// Declared before ID so the Category_Element pattern wins.

MACRO_CALL
    : [A-Z] [a-zA-Z0-9]* ( '_' [a-zA-Z0-9]+ )+
    ;

// ── ArchiMate layer color keywords ───────────────────────────────────────
// These appear immediately after the 'archimate' keyword as color names.
// Declared before ID so they are recognised as keywords.

KW_BUSINESS        : 'Business' ;
KW_APPLICATION     : 'Application' ;
KW_MOTIVATION      : 'Motivation' ;
KW_STRATEGY        : 'Strategy' ;
KW_TECHNOLOGY      : 'Technology' ;
KW_PHYSICAL        : 'Physical' ;
KW_IMPLEMENTATION  : 'Implementation' ;

// ── Element / directive keywords ──────────────────────────────────────────

KW_ARCHIMATE  : 'archimate' ;
KW_RECTANGLE  : 'rectangle' ;
KW_CIRCLE     : 'circle' ;
KW_SPRITE     : 'sprite' ;
KW_LISTSPRITE : 'listsprite' ;
KW_AS         : 'as' ;

// ── Legend keywords ───────────────────────────────────────────────────────

KW_LEGEND    : 'legend' ;
KW_ENDLEGEND : 'endlegend' ;
KW_LEFT      : 'left' ;
KW_RIGHT     : 'right' ;
KW_CENTER    : 'center' ;

// ── Direction statement keywords ──────────────────────────────────────────

KW_TOP       : 'top' ;
KW_BOTTOM    : 'bottom' ;
KW_TO        : 'to' ;
KW_DIRECTION : 'direction' ;

// ── Other directive keywords ──────────────────────────────────────────────

KW_SKINPARAM  : 'skinparam' ;
KW_TITLE      : 'title' ;
KW_HEADER     : 'header' ;
KW_FOOTER     : 'footer' ;
KW_SCALE      : 'scale' ;

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
COMMA   : ',' ;
BANG    : '!' ;
HASH    : '#' ;
DOLLAR  : '$' ;

// ── Integer ───────────────────────────────────────────────────────────────

INT : [0-9]+ ;

// ── Identifier ────────────────────────────────────────────────────────────
// Plain identifiers: element ids, alias names, skinparam keys.
// Declared after all keyword tokens and after MACRO_CALL.

ID
    : [a-zA-Z_][a-zA-Z0-9_]*
    ;

// ── Free-text argument (inside macro call parens) ─────────────────────────
// Unquoted text inside macro argument lists (before closing ')' or ',').
// Restricted to avoid consuming structural punctuation.

FREE_TEXT_ARG
    : ~[,)\r\n"]+
    ;

// ── Comments ──────────────────────────────────────────────────────────────

COMMENT_SINGLE
    : ['] ~[\r\n]*
    ;

COMMENT_MULTI
    : '/' ['] .*? ['] '/'
    ;

// ── Free text ─────────────────────────────────────────────────────────────
// Catch-all for relation labels, skinparam values, legend lines, etc.
// Declared last.

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
