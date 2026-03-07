// MermaidStateDiagramParser.g4
// ANTLR4 *parser* grammar for Mermaid State Diagrams
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

parser grammar MermaidStateDiagramParser;

options { tokenVocab = MermaidStateDiagramLexer; }

// ═══════════════════════════════════════════════════════════════════════════
// PARSER RULES
// ═══════════════════════════════════════════════════════════════════════════

diagram
    : NEWLINE* diagramType NEWLINE*
      statement*
      EOF
    ;

diagramType
    : KW_STATE_DIAGRAM_V2
    | KW_STATE_DIAGRAM
    ;

// ── Top-level statement dispatcher ────────────────────────────────────────

statement
    : stateDecl       NEWLINE*
    | transitionStmt  NEWLINE*
    | compositeBlock           // self-terminating (ends with '}' NEWLINE)
    | noteBlock                // self-terminating (ends with 'end note' NEWLINE)
    | concurrencyDiv  NEWLINE* // -- divider between parallel regions
    | directionStmt   NEWLINE*
    | classDefStmt    NEWLINE*
    | classAssignStmt NEWLINE*
    | COMMENT         NEWLINE*
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
    // Form 3 — id followed by colon and description (with 'state' keyword)
    | KW_STATE stateId COLON descriptionText classShorthand?
    // Form 4 — stereotype (choice / fork / join)
    | KW_STATE stateId STEREOTYPE
    // Form 5 — bare id with inline colon description, no 'state' keyword
    //   NamedComposite: Another Composite
    //   namedSimple: Another simple
    | stateId COLON descriptionText
    // Form 1 — bare id (with optional class shorthand), must be last
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
    // Single-line: KW_NOTE pushes NOTE_HDR_MODE; COLON inside NOTE_HDR_MODE
    // pushes FREE_TEXT_MODE; FREE_TEXT_NL popModes back through both.
    : KW_NOTE noteSide KW_OF stateId COLON noteLineContent NEWLINE*
    // Multi-line: KW_NOTE pushes NOTE_HDR_MODE; NOTE_HDR_NL inside that mode
    // transitions to NOTE_BODY_MODE. Body lines arrive as FREE_TEXT + NEWLINE
    // until KW_END_NOTE returns to DEFAULT_MODE.
    | KW_NOTE noteSide KW_OF stateId NEWLINE
          noteBodyLine+
      KW_END_NOTE NEWLINE*
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
// CSS_VALUE_START tokens are produced by the CSS lexer mode.
cssString
    : CSS_VALUE_START+ SEMI?
    ;
