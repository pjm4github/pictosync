# Claude Code Prompt — Mermaid Sequence Diagram Renderer
# =========================================================
# Paste this entire file as your opening message in a Claude Code session.
# All referenced files must be present in the working directory.
#
# Required files already on disk:
#   MermaidSequenceParser.g4         — ANTLR4 grammar parser (already written)
#   MermaidSequenceLexer.g4          — ANTLR4 grammar lexer (already written)
#   SVGNodeRegistry_Spec.py  — authoritative specification (already written)
#
# =========================================================

You are building a Mermaid sequence diagram renderer in Python 3.13 / PyQt6.
The project uses the ANTLR4 tool-chain to generate the recognizer from a
grammar file, and xml.etree.ElementTree for SVG output.

The file SVGNodeRegistry_Spec.py is the authoritative specification.
Read it completely before writing any code.  It defines (by section):

  Section 1  — the full pipeline from source text to SVGNodeRegistry
  Section 2  — all AST node dataclasses AND the mapping table from each
                parser rule to its generated context class and visitXxx method
  Section 3  — the ASTBuildingVisitor contract (skeleton + rules)
  Section 4  — SVG <g> attribute and data-role conventions
  Section 5  — the grammar-element → data-ast-type → data-role mapping table
  Section 6  — the LayoutModel dataclasses
  Section 7  — SVGNodeRegistry with the complete API including ctx_type field
  Section 8  — worked usage examples

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 0 — GENERATE THE ANTLR4 RECOGNIZER  (one-time build step)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Run this shell command to produce the generated Python files:

    antlr4 MermaidSequence.g4 -Dlanguage=Python3 -visitor -no-listener -o generated/

This produces in generated/:
    MermaidSequenceLexer.py
    MermaidSequenceParser.py
    MermaidSequenceVisitor.py

Do NOT edit the generated files.  Add generated/ to sys.path before importing.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1 — IMPLEMENT THESE FILES IN ORDER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Implement the files below strictly as specified.  Each file's contract is
quoted in the spec.  Do not add extra dependencies beyond:
    antlr4-python3-runtime >= 4.13
    Python 3.13 stdlib only (uuid, dataclasses, xml.etree.ElementTree, enum)

1. ast_nodes.py
   — All dataclasses from Section 2.
   — ASTNode must have: node_id (UUID str), ctx (Any, default None),
     source_start property, source_stop property.
   — Every subclass has a comment naming its originating context class.

2. layout_model.py
   — All dataclasses from Section 6 exactly.

3. svg_node_registry.py
   — SVGNodeEntry dataclass with ctx_type field (Section 7).
   — SVGNodeRegistry with all methods: register(), invalidate(),
     update_sub_elements(), svg_group_for(), svg_subelement(),
     svg_subelements(), all_of_type(), entry_for_step(),
     ast_node_for_svg_id(), ast_node_for_element().
   — _index_sub_elements() scans ALL descendants of svg_group, not just
     direct children.

4. ast_visitor.py
   — Imports from generated/ (adjust sys.path at top of file).
   — parse_diagram(source: str) -> DiagramNode  entry point function.
   — ASTBuildingVisitor(MermaidSequenceVisitor) with every visitXxx method
     listed in the Section 2 mapping table fully implemented.
   — The _step counter is an instance variable incremented for every
     MessageNode, ActivationNode, NoteNode, and the opening of every
     fragment node (LoopNode, AltNode, OptNode, ParNode, CriticalNode,
     BreakNode, RectNode).
   — Quote stripping: _strip(text) removes surrounding double-quotes.
   — _arrow_style(arrow_text) maps raw ANTLR token text to
     (ArrowStyle, activate: bool, deactivate: bool).
   — destroyDirective: the visitor returns the participant name string;
     the visitDiagram method then locates the matching ParticipantNode
     in diagram.participants and sets its destroyed_at_step.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 2 — IMPLEMENT TESTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. test_ast_visitor.py  (pytest)
   Test parse_diagram() against these source strings.  For each, assert
   the exact AST structure produced:

   CASE A — simple two-participant message:
     sequenceDiagram
       participant Alice
       participant Bob
       Alice->>Bob: Hello

   Assert: len(participants)==2, statements[0] is MessageNode,
           sender_name=="Alice", receiver_name=="Bob",
           arrow==ArrowStyle.SOLID_ARROW, text=="Hello", step==0.

   CASE B — autonumber + activation + note:
     sequenceDiagram
       autonumber
       participant A
       participant B
       A->>+B: call
       Note right of B: processing
       B-->>-A: reply

   Assert: autonumber is not None, step sequence is 0,1,2,
           activation on B embedded in message (activate==True),
           NoteNode.position==NotePosition.RIGHT_OF.

   CASE C — alt/else block:
     sequenceDiagram
       participant X
       participant Y
       alt condition one
         X->>Y: msg1
       else condition two
         Y->>X: msg2
       end

   Assert: AltNode with len(branches)==2,
           branches[0].condition=="condition one",
           branches[1].condition=="condition two".

   CASE D — nested loop inside par:
     sequenceDiagram
       participant P
       participant Q
       par thread A
         loop retry
           P->>Q: ping
         end
       and thread B
         Q->>P: pong
       end

   Assert: ParNode with 2 branches; branches[0].body[0] is LoopNode;
           LoopNode.body[0] is MessageNode.

   CASE E — create and destroy:
     sequenceDiagram
       participant A
       create participant B
       A->>B: init
       destroy B
       B->>A: bye

   Assert: B.created_at_step is not None, B.destroyed_at_step is not None.

6. test_registry.py  (pytest)
   Test SVGNodeRegistry in isolation using manually constructed ASTNode
   objects and hand-built xml.etree.ElementTree Element objects.
   Do NOT call parse_diagram() or the renderer in this test file.

   Required test cases:
   R1  register() adds entry to all four internal indexes.
   R2  svg_subelement() returns the first Element with matching data-role.
   R3  svg_subelements() returns ALL Elements with matching data-role.
   R4  ast_node_for_svg_id() round-trips: register then look up by svg_id.
   R5  ast_node_for_element() resolves a child Element via data-ast-ref.
   R6  invalidate() removes entry from all four indexes; subsequent
       lookups return None / empty list.
   R7  update_sub_elements() picks up a new child added after registration.
   R8  all_of_type() filters correctly across mixed-type registrations.
   R9  entry_for_step() returns the correct entry for a MessageNode at step 3.
   R10 register() correctly reads ctx_type from type(ast_node.ctx).__name__
       when ctx_type arg is omitted.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 3 — AUDIT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

After generating all six files, produce a short audit table with two columns:
  data-role value (from Section 5 of the spec)
  covered by test  (yes / no)

Flag any data-role values that have no test coverage and suggest the
minimal additional test case needed to cover each gap.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONSTRAINTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Never import MermaidSequenceParser, MermaidSequenceLexer, or
  MermaidSequenceVisitor outside of ast_visitor.py.
• Never store parser context objects outside of ASTNode.ctx.
• Use Python 3.10+ structural pattern matching (match/case) where it
  improves clarity (e.g. in _arrow_style(), _participant_kind()).
• All dataclass fields with mutable defaults use field(default_factory=...).
• Type annotations on every function signature.
• No third-party libraries beyond antlr4-python3-runtime.
