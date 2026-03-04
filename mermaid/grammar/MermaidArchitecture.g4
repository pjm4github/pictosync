// MermaidArchitectureDiagram.g4
// ANTLR4 grammar for Mermaid Architecture Diagrams (v11.1.0+)
// Reference: https://mermaid.ai/open-source/syntax/architecture.html
//
// ── Diagram header ────────────────────────────────────────────────────────
//   architecture-beta
//
// ── Building blocks ───────────────────────────────────────────────────────
//   group   {id}({icon})[{label}] (in {parentId})?
//   service {id}({icon})[{label}] (in {parentId})?
//   junction {id}              (in {parentId})?
//   {lhsSvc}{group}?:{side} {<}?--{>}? {side}:{rhsSvc}{group}?
//
// ── Icon syntax ───────────────────────────────────────────────────────────
//   (cloud)                   built-in icon by bare name
//   (disk)                    built-in: cloud database disk internet server
//   (aws:Lambda)              icon pack: "packName:icon-name"
//   (azure:FunctionApp)
//
// ── Label syntax ──────────────────────────────────────────────────────────
//   [My Database]             free-text label in square brackets
//   [Public API]
//
// ── Group membership ──────────────────────────────────────────────────────
//   in parentId               optional suffix on group / service / junction
//
// ── Edge syntax (full form) ───────────────────────────────────────────────
//   db:R -- L:server                   open line, right-of-db  to left-of-server
//   db:T -- L:server                   90-degree bend
//   subnet:R --> L:gateway             arrow into gateway
//   subnet:R <-- L:gateway             arrow into subnet
//   subnet:R <--> L:gateway            bidirectional arrows
//   server{group}:B --> T:subnet{group} edge exits the parent group boundary
//
// ── Edge sides ────────────────────────────────────────────────────────────
//   L  left    R  right    T  top    B  bottom
//
// ── Junction ──────────────────────────────────────────────────────────────
//   junction jId
//   junction jId in groupId
//   (junctions are 4-way edge split points)
//
// ── Comments ──────────────────────────────────────────────────────────────
//   %% anything to end of line
//
// ── Lexer ordering notes ──────────────────────────────────────────────────
//   1. KW_ARCH_BETA 'architecture-beta' before any ID (hyphen in name)
//   2. EDGE_BIDIR  '<-->'  before EDGE_LEFT  '<--'  before EDGE_OPEN  '--'
//   3. EDGE_RIGHT  '-->'   before EDGE_OPEN  '--'
//   4. LBRACE_GROUP '{group}' literal before LBRACE '{'
//   5. SIDE token  (L|R|T|B) declared as alternatives inside a parser rule,
//      backed by individual keyword tokens, all before ID
//   6. ICON_REF  handles both bare-name and pack:name inside parentheses
//      via a dedicated lexer token to avoid COLON ambiguity
//   7. All multi-char keyword tokens before ID

grammar MermaidArchitectureDiagram;

// ═══════════════════════════════════════════════════════════════════════════
// PARSER RULES
// ═══════════════════════════════════════════════════════════════════════════

diagram
    : NEWLINE* KW_ARCH_BETA NEWLINE+
      statement*
      EOF
    ;

// ── Statement dispatcher ──────────────────────────────────────────────────

statement
    : groupDecl   NEWLINE+
    | serviceDecl NEWLINE+
    | junctionDecl NEWLINE+
    | edgeStmt    NEWLINE+
    | COMMENT     NEWLINE+
    | NEWLINE+
    ;

// ═══════════════════════════════════════════════════════════════════════════
// GROUP DECLARATION
//
//   group {id}({icon})[{label}] (in {parentId})?
//
// Examples:
//   group public_api(cloud)[Public API]
//   group private_api(cloud)[Private API] in public_api
//   group db_cluster(database)[DB Cluster] in private_api
// ═══════════════════════════════════════════════════════════════════════════

groupDecl
    : KW_GROUP nodeId iconRef labelRef groupMembership?
    ;

// ═══════════════════════════════════════════════════════════════════════════
// SERVICE DECLARATION
//
//   service {id}({icon})[{label}] (in {parentId})?
//
// Examples:
//   service database1(database)[My Database]
//   service database1(database)[My Database] in private_api
//   service lambda1(aws:Lambda)[Lambda] in compute_group
// ═══════════════════════════════════════════════════════════════════════════

serviceDecl
    : KW_SERVICE nodeId iconRef labelRef groupMembership?
    ;

// ═══════════════════════════════════════════════════════════════════════════
// JUNCTION DECLARATION
//
//   junction {id}
//   junction {id} in {parentId}
//
// A junction is a 4-way edge-split point with no icon or label.
// ═══════════════════════════════════════════════════════════════════════════

junctionDecl
    : KW_JUNCTION nodeId groupMembership?
    ;

// ── Node identifier ───────────────────────────────────────────────────────
// Identifiers for groups, services, and junctions.  Allows hyphens and
// underscores as commonly seen in cloud resource names.

nodeId : ID ;

// ── Icon reference ────────────────────────────────────────────────────────
// Wrapped in parentheses.  Two forms:
//   (cloud)           — bare built-in icon name
//   (aws:Lambda)      — pack:iconName  (colon is INSIDE the parens)
//
// Design: ICON_REF is a single lexer token that consumes the entire
// '(' content ')' sequence.  This sidesteps the COLON ambiguity that would
// arise if we tried to tokenize pack:name with the shared COLON token.
// The visitor strips the surrounding parens and splits on ':' if present.

iconRef
    : ICON_REF
    ;

// ── Label reference ───────────────────────────────────────────────────────
// Free-text label wrapped in square brackets.
// LABEL_REF is a single lexer token: '[' ~[\]\r\n]* ']'
// The visitor strips the surrounding brackets.

labelRef
    : LABEL_REF
    ;

// ── Group membership ──────────────────────────────────────────────────────
// Optional suffix: "in parentId"

groupMembership
    : KW_IN nodeId
    ;

// ═══════════════════════════════════════════════════════════════════════════
// EDGE STATEMENT
//
// Full BNF:
//   {lhsSvc}{group}?:{side} {<}?--{>}? {side}:{rhsSvc}{group}?
//
// Where:
//   {group}  is the literal token  {group}  (braces included)
//   {side}   is one of  L  R  T  B
//   <        signals an arrowhead pointing INTO the left service
//   >        signals an arrowhead pointing INTO the right service
//
// Examples:
//   db:R -- L:server
//   subnet:R --> L:gateway
//   subnet:R <-- L:gateway
//   subnet:R <--> L:gateway
//   server{group}:B --> T:subnet{group}
// ═══════════════════════════════════════════════════════════════════════════

edgeStmt
    : lhsEndpoint edgeLine rhsEndpoint
    ;

// ── Left-hand endpoint ────────────────────────────────────────────────────
// Format: nodeId {group}? : side

lhsEndpoint
    : nodeId GROUP_MOD? COLON side
    ;

// ── Right-hand endpoint ───────────────────────────────────────────────────
// Format: side : nodeId {group}?

rhsEndpoint
    : side COLON nodeId GROUP_MOD?
    ;

// ── Edge line (the connecting shaft with optional arrowheads) ─────────────
// Four variants, in declaration-order priority:
//   <-->   bidirectional
//   -->    right arrow only
//   <--    left arrow only
//   --     open (no arrows)
//
// These are emitted as four dedicated tokens so the parser rule is simple.

edgeLineToken
    : EDGE_BIDIR
    | EDGE_RIGHT
    | EDGE_LEFT
    | EDGE_OPEN
    ;

// edgeLine wraps the token for a cleaner visitor API
edgeLine
    : edgeLineToken
    ;

// ── Side specifier ────────────────────────────────────────────────────────
// L=left  R=right  T=top  B=bottom
// Each is a keyword token so they win over ID for single-letter matches.

side
    : KW_L | KW_R | KW_T | KW_B
    ;


// ═══════════════════════════════════════════════════════════════════════════
// LEXER RULES
// ═══════════════════════════════════════════════════════════════════════════
//
// Critical ordering:
//   1.  KW_ARCH_BETA   — 'architecture-beta' hyphenated, before ID
//   2.  EDGE_BIDIR     — '<-->' longest, before EDGE_LEFT '<--'
//   3.  EDGE_RIGHT     — '-->'  before EDGE_OPEN '--'
//   4.  EDGE_LEFT      — '<--'  before EDGE_OPEN '--'
//   5.  GROUP_MOD      — literal '{group}' before LBRACE '{'
//   6.  ICON_REF       — '(' ... ')' composite token; before LPAREN
//   7.  LABEL_REF      — '[' ... ']' composite token; before LBRACK
//   8.  Side keywords KW_L KW_R KW_T KW_B — before ID
//   9.  All other keywords — before ID

// ── Diagram type ──────────────────────────────────────────────────────────

KW_ARCH_BETA : 'architecture-beta' ;

// ── Declaration keywords ──────────────────────────────────────────────────

KW_GROUP    : 'group' ;
KW_SERVICE  : 'service' ;
KW_JUNCTION : 'junction' ;
KW_IN       : 'in' ;

// ── Side keywords (single uppercase letters) ──────────────────────────────
// These must be declared before ID so that bare L / R / T / B in an
// edge statement tokenise as side keywords rather than identifiers.
// Using single-char tokens means "LR" or "TB" still tokenise as ID
// (longer match wins), which is correct since those are valid node ids.

KW_L : 'L' ;
KW_R : 'R' ;
KW_T : 'T' ;
KW_B : 'B' ;

// ── Edge shaft tokens ─────────────────────────────────────────────────────
// Declared longest-first.  ANTLR4 longest-match rule resolves ties.

EDGE_BIDIR  : '<-->' ;    // bidirectional arrow
EDGE_RIGHT  : '-->'  ;    // right-pointing arrow
EDGE_LEFT   : '<--'  ;    // left-pointing arrow
EDGE_OPEN   : '--'   ;    // open line (no arrowheads)

// ── Group modifier ────────────────────────────────────────────────────────
// The literal string '{group}' (including braces) used as a modifier on
// edge endpoint service ids.  Must be declared before LBRACE so the
// full literal wins over a bare '{'.

GROUP_MOD : '{group}' ;

// ── Icon reference token ──────────────────────────────────────────────────
// Consumes:  '(' iconContent ')'
// iconContent is: packName ':' iconName  or  bare iconName
// Using a composite token avoids COLON ambiguity inside parens.
// The character class ~[)\r\n] excludes the closing paren and newlines.

ICON_REF
    : '(' ~[)\r\n]+ ')'
    ;

// ── Label reference token ─────────────────────────────────────────────────
// Consumes:  '[' labelContent ']'
// labelContent is free text (spaces allowed), excluding newlines.

LABEL_REF
    : '[' ~[\]\r\n]* ']'
    ;

// ── Punctuation ───────────────────────────────────────────────────────────

LBRACE  : '{' ;
RBRACE  : '}' ;
LPAREN  : '(' ;    // kept for potential future use / error recovery
RPAREN  : ')' ;
LBRACK  : '[' ;
RBRACK  : ']' ;
COLON   : ':' ;    // used between nodeId and side in edge endpoints

// ── Integer ───────────────────────────────────────────────────────────────

INT : [0-9]+ ;

// ── Identifier ────────────────────────────────────────────────────────────
// Node ids, group ids, icon pack names (inside ICON_REF handled above).
// Allows hyphens, underscores, dots — common in cloud resource naming
// (e.g. "private-api", "db_cluster", "lambda.v2").
// Declared after all keyword tokens.

ID
    : [a-zA-Z_] [a-zA-Z0-9_\-.]*
    ;

// ── Comment ───────────────────────────────────────────────────────────────

COMMENT
    : '%%' ~[\r\n]*
    ;

// ── Newline ───────────────────────────────────────────────────────────────

NEWLINE
    : [\r\n]+
    ;

// ── Whitespace ────────────────────────────────────────────────────────────

WS
    : [ \t]+ -> skip
    ;
