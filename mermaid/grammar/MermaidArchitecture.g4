// MermaidArchitecture.g4
// ANTLR4 Grammar for Mermaid Architecture Diagrams (architecture-beta)
// Reference: https://mermaid.js.org/syntax/architecture
//
// Syntax coverage:
//   - architecture-beta header
//   - group declarations    (nested via 'in <parentId>')
//   - service declarations  (placed in group via 'in <parentId>')
//   - junction declarations (placed in group via 'in <parentId>')
//   - edge statements       (side specifiers L|R|T|B, arrows <--, -->, <-->,
//                            no-arrow --, {group} modifier)
//   - iconify icon names    (builtin shortnames AND namespaced pack:name form)
//   - %% line comments

grammar MermaidArchitecture;

// =============================================================================
// Parser Rules
// =============================================================================

diagram
    : NEWLINE* ARCHITECTURE_BETA NEWLINE+ statement* EOF
    ;

statement
    : groupDecl    NEWLINE+
    | serviceDecl  NEWLINE+
    | junctionDecl NEWLINE+
    | edgeStmt     NEWLINE+
    | COMMENT      NEWLINE+
    | NEWLINE+
    ;

// ---------------------------------------------------------------------------
// group {groupId}({iconName})[{label}] (in {parentId})?
// ---------------------------------------------------------------------------
groupDecl
    : GROUP nodeId iconSpec labelSpec (IN nodeId)?
    ;

// ---------------------------------------------------------------------------
// service {serviceId}({iconName})[{label}] (in {parentId})?
// ---------------------------------------------------------------------------
serviceDecl
    : SERVICE nodeId iconSpec labelSpec (IN nodeId)?
    ;

// ---------------------------------------------------------------------------
// junction {junctionId} (in {parentId})?
// Junctions have no icon or label — they are invisible routing nodes.
// ---------------------------------------------------------------------------
junctionDecl
    : JUNCTION nodeId (IN nodeId)?
    ;

// ---------------------------------------------------------------------------
// Icon spec: ({iconName})
//   iconName is either a simple name  (e.g. cloud, database, disk)
//   or a namespaced name              (e.g. logos:aws-lambda, mdi:server)
// ---------------------------------------------------------------------------
iconSpec
    : LPAREN iconName RPAREN
    ;

iconName
    : ICON_NAME           // simple or pack:name token
    ;

// ---------------------------------------------------------------------------
// Label spec: [{label text}]
//   Label text may contain spaces and most printable characters.
// ---------------------------------------------------------------------------
labelSpec
    : LBRACKET labelText RBRACKET
    ;

labelText
    : LABEL_TEXT
    ;

// ---------------------------------------------------------------------------
// Node identifier
//   Used for serviceId, groupId, junctionId, and parentId.
// ---------------------------------------------------------------------------
nodeId
    : ID
    ;

// ---------------------------------------------------------------------------
// Edge statement
//
// Full BNF:
//   edgeStmt ::= edgeEndpoint edgeConnector edgeEndpoint
//
//   edgeEndpoint ::= nodeId ('{group}')? ':' sideSpec
//
//   edgeConnector ::= '<'? '--' '>'?
//                     (the '<' and '>' are the arrowhead markers)
//
//   sideSpec ::= 'L' | 'R' | 'T' | 'B'
//
// Examples:
//   db:R -- L:server
//   db:T --> B:server
//   api{group}:L <-- R:client
//   lb:R <--> L:cache
// ---------------------------------------------------------------------------
edgeStmt
    : edgeSide edgeConnector edgeSide
    ;

edgeSide
    : nodeId groupModifier? COLON sideSpec   // nodeId{group}:L  (left of arrow)
    | sideSpec COLON nodeId groupModifier?   // R:nodeId{group}  (right of arrow)
    ;

groupModifier
    : LBRACE GROUP RBRACE       // literal {group}
    ;

edgeConnector
    : ARROW_LEFT? EDGE_LINE ARROW_RIGHT?
    ;

sideSpec
    : SIDE_L
    | SIDE_R
    | SIDE_T
    | SIDE_B
    ;

// =============================================================================
// Lexer Rules
// =============================================================================

// ---------------------------------------------------------------------------
// Keywords  (order matters — must precede general ID rule)
// ---------------------------------------------------------------------------

ARCHITECTURE_BETA : 'architecture-beta' ;
GROUP             : 'group' ;
SERVICE           : 'service' ;
JUNCTION          : 'junction' ;
IN                : 'in' ;

// Side specifiers are single uppercase letters used only in edge statements.
// Declared as tokens so they don't collide with identifiers that happen to be
// single letters in other positions.
SIDE_L : 'L' ;
SIDE_R : 'R' ;
SIDE_T : 'T' ;
SIDE_B : 'B' ;

// ---------------------------------------------------------------------------
// Edge tokens
// ---------------------------------------------------------------------------

ARROW_LEFT  : '<' ;
ARROW_RIGHT : '>' ;
EDGE_LINE   : '--' ;

// ---------------------------------------------------------------------------
// Structural punctuation
// ---------------------------------------------------------------------------

COLON   : ':' ;
LPAREN  : '(' ;
RPAREN  : ')' ;
LBRACKET : '[' ;
RBRACKET : ']' ;
LBRACE  : '{' ;
RBRACE  : '}' ;

// ---------------------------------------------------------------------------
// Icon name
//   Matches  simple names:     cloud  database  disk  internet  server
//   Matches  namespaced names: logos:aws-lambda  mdi:server  fa:home
//   The colon in namespaced icons is consumed inside this single token so
//   it does not conflict with the COLON token used in edge side-specs.
//   The token is greedy and will match the longest possible sequence of
//   valid icon-name characters.
// ---------------------------------------------------------------------------
ICON_NAME
    : ICON_PART (':' ICON_PART)?
    ;

fragment ICON_PART
    : [a-zA-Z0-9_\-]+
    ;

// ---------------------------------------------------------------------------
// Label text
//   Everything between [ and ] on a single line.
//   Captured as a single token to avoid keyword conflicts inside labels.
// ---------------------------------------------------------------------------
LABEL_TEXT
    : ~[\[\]\r\n]+
    ;

// ---------------------------------------------------------------------------
// General identifier
//   Service IDs, group IDs, junction IDs.
//   Must start with a letter or underscore; can contain letters, digits,
//   underscores, hyphens, and dots (common in real infra identifiers).
// ---------------------------------------------------------------------------
ID
    : [a-zA-Z_] [a-zA-Z0-9_\-.]*
    ;

// ---------------------------------------------------------------------------
// Comments
// ---------------------------------------------------------------------------
COMMENT
    : '%%' ~[\r\n]*
    ;

// ---------------------------------------------------------------------------
// Whitespace and newlines
// ---------------------------------------------------------------------------
NEWLINE
    : [\r\n]+
    ;

WS
    : [ \t]+ -> skip
    ;
