// MermaidSequenceParser.g4
// ANTLR4 Parser Grammar for Mermaid Sequence Diagrams
//
// Token vocabulary supplied by MermaidSequenceLexer.g4.
// Compile together:
//
//   java -jar antlr-4.13.1-complete.jar -Dlanguage=Python3 ^
//        -visitor -no-listener -o generated ^
//        MermaidSequenceLexer.g4 MermaidSequenceParser.g4
//
// Changes vs the combined grammar:
//   - ARROW, fragment ARROW_BASE, fragment ACTIVATE_SUFFIX removed (now in lexer)
//   - UNQUOTED_LABEL references remain in label/boxLabel rules; the token is
//     now produced by LABEL_MODE in the lexer (renamed from the old greedy rule)
//   - FREE_TEXT references replaced by TEXT_REST (produced by TEXT_MODE)
//   - linkLabel replaced by TEXT_REST (no string literals allowed in parser rules
//     of a split grammar)

parser grammar MermaidSequenceParser;

options { tokenVocab = MermaidSequenceLexer; }

// =============================================================================
// Parser Rules
// =============================================================================

diagram
    : NEWLINE* SEQUENCE_DIAGRAM NEWLINE+ statement* EOF
    ;

statement
    : participantDecl NEWLINE+
    | actorDecl NEWLINE+
    | boxBlock
    | createDirective NEWLINE+
    | destroyDirective NEWLINE+
    | messageStatement NEWLINE+
    | activateStatement NEWLINE+
    | deactivateStatement NEWLINE+
    | noteStatement NEWLINE+
    | loopBlock
    | altBlock
    | optBlock
    | parBlock
    | criticalBlock
    | breakBlock
    | rectBlock
    | autonumberStatement NEWLINE+
    | linkStatement NEWLINE+
    | linksStatement NEWLINE+
    | COMMENT NEWLINE+
    | NEWLINE+
    ;

// ---- Participant Declarations -----------------------------------------------

participantDecl
    : participantType participantId (AS label)?
    ;

participantType
    : PARTICIPANT
    | ACTOR
    | BOUNDARY
    | CONTROL
    | ENTITY
    | DATABASE
    | COLLECTIONS
    | QUEUE
    ;

actorDecl
    : ACTOR participantId (AS label)?
    ;

participantId
    : QUOTED_STRING
    | ID
    ;

// label uses LABEL_REST which is produced by LABEL_MODE (entered after AS).
// LABEL_REST captures the entire rest of the line as one token, so multi-word
// aliases like "Web Browser" work without quoting.
label
    : QUOTED_STRING
    | LABEL_REST
    ;

// ---- Box Block --------------------------------------------------------------

boxBlock
    : BOX boxColor? boxLabel? NEWLINE+ statement* END NEWLINE+
    ;

boxColor
    : COLOR_NAME
    | RGB_COLOR
    | RGBA_COLOR
    | TRANSPARENT
    ;

boxLabel
    : QUOTED_STRING
    | LABEL_REST
    ;

// ---- Create / Destroy -------------------------------------------------------

createDirective
    : CREATE participantType participantId (AS label)?
    ;

destroyDirective
    : DESTROY participantId
    ;

// ---- Message Statements -----------------------------------------------------

messageStatement
    : sender ARROW receiver COLON messageText
    ;

sender
    : LPAREN? participantId RPAREN?
    ;

receiver
    : LPAREN? participantId RPAREN?
    ;

// messageText is the text after ':' — captured as TEXT_REST by TEXT_MODE.
messageText
    : TEXT_REST?
    ;

// ---- Activate / Deactivate --------------------------------------------------

activateStatement
    : ACTIVATE participantId
    ;

deactivateStatement
    : DEACTIVATE participantId
    ;

// ---- Note Statements --------------------------------------------------------

noteStatement
    : NOTE notePosition participantId (COMMA participantId)? COLON noteText
    ;

notePosition
    : RIGHT_OF
    | LEFT_OF
    | OVER
    ;

noteText
    : TEXT_REST?
    ;

// ---- Loop Block -------------------------------------------------------------

loopBlock
    : LOOP loopLabel NEWLINE+ statement* END NEWLINE+
    ;

// loopLabel is text after 'loop' on the same line.
// Because LOOP does not push TEXT_MODE, the label tokens are still in DEFAULT
// mode.  In practice loop labels are simple identifiers or short phrases that
// don't contain ':', so ID / COLOR_NAME tokens cover them.
// If you need arbitrary text here, add a LOOP_LABEL_MODE triggered by LOOP.
loopLabel
    : TEXT_REST?
    ;

// ---- Alt / Else / Opt Blocks ------------------------------------------------

altBlock
    : ALT altCondition NEWLINE+ statement*
      (ELSE altCondition NEWLINE+ statement*)*
      END NEWLINE+
    ;

optBlock
    : OPT optCondition NEWLINE+ statement* END NEWLINE+
    ;

altCondition
    : TEXT_REST?
    ;

optCondition
    : TEXT_REST?
    ;

// ---- Par / And Block --------------------------------------------------------

parBlock
    : PAR parLabel NEWLINE+ statement*
      (AND parLabel NEWLINE+ statement*)*
      END NEWLINE+
    ;

parLabel
    : TEXT_REST?
    ;

// ---- Critical / Option Block ------------------------------------------------

criticalBlock
    : CRITICAL criticalAction NEWLINE+ statement*
      (OPTION optionCondition NEWLINE+ statement*)*
      END NEWLINE+
    ;

criticalAction
    : TEXT_REST?
    ;

optionCondition
    : TEXT_REST?
    ;

// ---- Break Block ------------------------------------------------------------

breakBlock
    : BREAK breakCondition NEWLINE+ statement* END NEWLINE+
    ;

breakCondition
    : TEXT_REST?
    ;

// ---- Rect Block -------------------------------------------------------------

rectBlock
    : RECT rectColor NEWLINE+ statement* END NEWLINE+
    ;

rectColor
    : COLOR_NAME
    | RGB_COLOR
    | RGBA_COLOR
    | TRANSPARENT
    ;

// ---- Autonumber -------------------------------------------------------------

autonumberStatement
    : AUTONUMBER (INT (INT INT?)?)?
    ;

// ---- Link / Links -----------------------------------------------------------

linkStatement
    : LINK participantId COLON linkLabel AT linkUrl
    ;

linksStatement
    : LINKS participantId COLON jsonObject
    ;

// linkLabel and linkUrl are both captured by TEXT_MODE after COLON.
// The original grammar used ~('@'|'\n'|'\r')+ for linkLabel which is not
// legal in a split parser grammar (no string literals in parser rules).
// TEXT_REST covers the entire post-colon text; the visitor/listener can
// split on '@' to separate label from URL if needed.
linkLabel
    : TEXT_REST?
    ;

linkUrl
    : TEXT_REST?
    ;

// Minimal JSON object (for links directive)
jsonObject
    : LBRACE jsonPair (COMMA jsonPair)* RBRACE
    ;

jsonPair
    : QUOTED_STRING COLON QUOTED_STRING
    ;
