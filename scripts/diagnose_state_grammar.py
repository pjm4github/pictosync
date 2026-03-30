"""Diagnose PlantUML state grammar coverage.

Compares ANTLR4 grammar parsing against regex extraction to find
states and transitions that the grammar fails to parse.

Usage:
    .venv/Scripts/python scripts/diagnose_state_grammar.py [puml_file]

Defaults to test_data/PUML/t_state_parser_stress_test.puml
"""
from __future__ import annotations

import io
import os
import re
import sys

# Force UTF-8 stdout on Windows to handle Unicode in PUML files
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from antlr4 import CommonTokenStream, InputStream
from plantuml.grammar.generated.PlantUMLStateLexer import PlantUMLStateLexer
from plantuml.grammar.generated.PlantUMLStateParser import PlantUMLStateParser
from plantuml.grammar.generated.PlantUMLStateVisitor import PlantUMLStateVisitor


# ── Regex-based reference extractor ──────────────────────────────────────

_STATE_RE = re.compile(
    r'^\s*state\s+'
    r'(?:"([^"]+)"|(\S+))'         # quoted or bare name
    r'(?:\s+as\s+(\S+))?'          # optional alias
    r'(?:\s+<<[^>]+>>)?'           # optional stereotype
    r'(?:\s*#\S+)?'                 # optional color
    r'(?:\s*\{)?',                  # optional block open
    re.MULTILINE,
)

_TRANSITION_RE = re.compile(
    r'^\s*(\[[\*H]+\]|"[^"]+"|[a-zA-Z_][\w.]*(?:\[H\*?\])?)\s+'
    r'(-+(?:[a-z]+)?(?:\[[^\]]*\])?-*>|<-+(?:[a-z]+)?(?:\[[^\]]*\])?-*>?)\s+'
    r'(\[[\*H]+\]|"[^"]+"|[a-zA-Z_][\w.]*(?:\[H\*?\])?)'
    r'(?:\s*:\s*(.+))?',
    re.MULTILINE,
)

_DESCRIPTION_RE = re.compile(
    r'^\s*([a-zA-Z_]\w*)\s*:\s*(.+)',
    re.MULTILINE,
)


def _extract_reference_states(text: str):
    """Extract states using regex (reference truth)."""
    states = {}
    for m in _STATE_RE.finditer(text):
        name = m.group(1) or m.group(2)
        alias = m.group(3) or ""
        key = (alias or name).lower()
        line = text[:m.start()].count("\n") + 1
        states[key] = {"name": name, "alias": alias, "line": line}
    return states


def _extract_reference_transitions(text: str):
    """Extract transitions using regex."""
    transitions = []
    for m in _TRANSITION_RE.finditer(text):
        src = m.group(1).strip('"')
        arrow = m.group(2)
        dst = m.group(3).strip('"')
        label = (m.group(4) or "").strip()
        line = text[:m.start()].count("\n") + 1
        transitions.append({
            "src": src, "dst": dst, "arrow": arrow,
            "label": label, "line": line,
        })
    return transitions


def _extract_reference_descriptions(text: str):
    """Extract state descriptions (StateName : text)."""
    descs = {}
    for m in _DESCRIPTION_RE.finditer(text):
        name = m.group(1)
        desc = m.group(2).strip()
        line = text[:m.start()].count("\n") + 1
        key = name.lower()
        if key not in descs:
            descs[key] = []
        descs[key].append({"text": desc, "line": line})
    return descs


# ── ANTLR-based extractor ────────────────────────────────────────────────

class _DiagVisitor(PlantUMLStateVisitor):
    def __init__(self):
        self.states = {}
        self.transitions = []
        self.descriptions = {}
        self.composites = {}

    def _store_state(self, ctx, name, alias):
        key = (alias or name).lower()
        line = ctx.start.line if ctx.start else 0
        self.states[key] = {"name": name, "alias": alias, "line": line}

    def visitStateDecl(self, ctx):
        name = ctx.stateName().getText().strip('"') if ctx.stateName() else ""
        alias = ""
        if ctx.aliasClause():
            alias = ctx.aliasClause().stateName().getText().strip('"')
        stereotype = ctx.stereotypeClause().getText() if ctx.stereotypeClause() else ""
        self._store_state(ctx, name, alias)
        if stereotype:
            key = (alias or name).lower()
            self.states[key]["stereotype"] = stereotype
        return self.visitChildren(ctx)

    def visitCompositeBlock(self, ctx):
        name = ctx.stateName().getText().strip('"') if ctx.stateName() else ""
        alias = ""
        if ctx.aliasClause():
            alias = ctx.aliasClause().stateName().getText().strip('"')
        stereotype = ctx.stereotypeClause().getText() if ctx.stereotypeClause() else ""
        self._store_state(ctx, name, alias)
        key = (alias or name).lower()
        self.composites[key] = True
        if stereotype:
            self.states[key]["stereotype"] = stereotype
        return self.visitChildren(ctx)

    def visitTransitionStmt(self, ctx):
        try:
            ends = ctx.transitionEnd()
            if len(ends) < 2:
                return self.visitChildren(ctx)
            src = ends[0].getText().strip('"')
            dst = ends[1].getText().strip('"')
            arrow = ctx.TRANSITION_ARROW().getText() if ctx.TRANSITION_ARROW() else "??"
            label = ""
            if ctx.restOfLine():
                label = ctx.restOfLine().getText().strip()
            line = ctx.start.line if ctx.start else 0
            self.transitions.append({
                "src": src, "dst": dst, "arrow": arrow,
                "label": label, "line": line,
            })
        except Exception:
            pass
        return self.visitChildren(ctx)

    def visitDescriptionStmt(self, ctx):
        try:
            ref = ctx.stateRef().getText().strip('"')
            desc = ctx.restOfLine().getText().strip() if ctx.restOfLine() else ""
            line = ctx.start.line if ctx.start else 0
            key = ref.lower()
            if key not in self.descriptions:
                self.descriptions[key] = []
            self.descriptions[key].append({"text": desc, "line": line})
        except Exception:
            pass
        return self.visitChildren(ctx)


def _parse_with_antlr(text: str):
    """Parse with ANTLR and return states, transitions, errors."""
    input_stream = InputStream(text)
    lexer = PlantUMLStateLexer(input_stream)
    lexer.removeErrorListeners()

    token_stream = CommonTokenStream(lexer)
    parser = PlantUMLStateParser(token_stream)

    errors = []

    class _ErrorListener:
        def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
            errors.append({"line": line, "col": column, "msg": msg})
        def reportAmbiguity(self, *a): pass
        def reportAttemptingFullContext(self, *a): pass
        def reportContextSensitivity(self, *a): pass

    parser.removeErrorListeners()
    parser.addErrorListener(_ErrorListener())

    tree = parser.diagram()
    visitor = _DiagVisitor()
    visitor.visit(tree)
    return visitor.states, visitor.transitions, visitor.descriptions, visitor.composites, errors


# ── Main diagnostic ──────────────────────────────────────────────────────

def diagnose(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    print(f"=== State Grammar Diagnostic: {os.path.basename(filepath)} ===")
    print(f"Source: {len(text)} chars, {text.count(chr(10))+1} lines\n")

    ref_states = _extract_reference_states(text)
    ref_trans = _extract_reference_transitions(text)
    ref_descs = _extract_reference_descriptions(text)

    antlr_states, antlr_trans, antlr_descs, antlr_composites, antlr_errors = _parse_with_antlr(text)

    # ── States comparison ──
    print(f"{'STATES':=^72}")
    print(f"  Regex found: {len(ref_states)}")
    print(f"  ANTLR found: {len(antlr_states)} ({len(antlr_composites)} composite)")

    ref_keys = set(ref_states.keys())
    antlr_keys = set(antlr_states.keys())
    matched = ref_keys & antlr_keys
    missing = ref_keys - antlr_keys
    extra = antlr_keys - ref_keys

    if matched:
        print(f"\n  MATCHED ({len(matched)}):")
        for k in sorted(matched):
            a = antlr_states[k]
            comp = " [composite]" if k in antlr_composites else ""
            stereo = a.get("stereotype", "")
            stereo_str = f" {stereo}" if stereo else ""
            print(f"    {k:30s} name={a['name']!r}{stereo_str}{comp}")

    if missing:
        print(f"\n  MISSING from ANTLR ({len(missing)}):")
        for k in sorted(missing):
            r = ref_states[k]
            print(f"    line {r['line']:3d}: name={r['name']!r} alias={r['alias']!r}")

    if extra:
        print(f"\n  EXTRA in ANTLR ({len(extra)}):")
        for k in sorted(extra):
            a = antlr_states[k]
            print(f"    line {a['line']:3d}: name={a['name']!r} alias={a['alias']!r}")

    # ── Descriptions ──
    print(f"\n{'DESCRIPTIONS':=^72}")
    print(f"  Regex found: {sum(len(v) for v in ref_descs.values())} across {len(ref_descs)} states")
    print(f"  ANTLR found: {sum(len(v) for v in antlr_descs.values())} across {len(antlr_descs)} states")

    ref_desc_keys = set(ref_descs.keys())
    antlr_desc_keys = set(antlr_descs.keys())
    desc_missing = ref_desc_keys - antlr_desc_keys
    if desc_missing:
        print(f"\n  MISSING from ANTLR ({len(desc_missing)}):")
        for k in sorted(desc_missing):
            for d in ref_descs[k]:
                print(f"    line {d['line']:3d}: {k} : {d['text']!r}")

    # ── Transitions comparison ──
    print(f"\n{'TRANSITIONS':=^72}")
    print(f"  Regex found: {len(ref_trans)}")
    print(f"  ANTLR found: {len(antlr_trans)}")

    ref_conn_set = {(c["src"], c["dst"]) for c in ref_trans}
    antlr_conn_set = {(c["src"], c["dst"]) for c in antlr_trans}
    conn_matched = ref_conn_set & antlr_conn_set
    conn_missing = ref_conn_set - antlr_conn_set

    print(f"  Matched: {len(conn_matched)}")

    if conn_missing:
        print(f"\n  MISSING from ANTLR ({len(conn_missing)}):")
        for c in sorted(ref_trans, key=lambda x: x["line"]):
            if (c["src"], c["dst"]) in conn_missing:
                print(f"    line {c['line']:3d}: {c['src']} {c['arrow']} {c['dst']}  label={c['label']!r}")

    # ── Parse errors ──
    if antlr_errors:
        print(f"\n{'ANTLR PARSE ERRORS':=^72}")
        print(f"  {len(antlr_errors)} errors:")
        for e in antlr_errors[:30]:
            msg = e['msg'].encode('ascii', 'replace').decode('ascii')
            print(f"    line {e['line']:3d} col {e['col']:2d}: {msg}")
        if len(antlr_errors) > 30:
            print(f"    ... and {len(antlr_errors) - 30} more")

    # ── Summary ──
    total_ref = len(ref_states) + len(ref_trans)
    total_missing = len(missing) + len(conn_missing)
    pct = ((total_ref - total_missing) / total_ref * 100) if total_ref > 0 else 0

    print(f"\n{'SUMMARY':=^72}")
    print(f"  States: {len(matched)}/{len(ref_states)} matched ({len(missing)} missing)")
    print(f"  Transitions: {len(conn_matched)}/{len(ref_trans)} matched ({len(conn_missing)} missing)")
    print(f"  Descriptions: {sum(len(v) for v in antlr_descs.values())}/{sum(len(v) for v in ref_descs.values())}")
    print(f"  Coverage: {pct:.0f}% ({total_ref - total_missing}/{total_ref})")
    print(f"  Parse errors: {len(antlr_errors)}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "test_data", "PUML", "t_state_parser_stress_test.puml",
        )
    if not os.path.exists(path):
        print(f"File not found: {path}")
        sys.exit(1)
    diagnose(path)
