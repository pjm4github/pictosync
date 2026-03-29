"""Diagnose PlantUML deployment grammar coverage.

Compares ANTLR4 grammar parsing against regex extraction to find
elements and connections that the grammar fails to parse.

Usage:
    .venv/Scripts/python scripts/diagnose_deployment_grammar.py [puml_file]

Defaults to test_data/PUML/t_deployment_parser_stress_test.puml
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from antlr4 import CommonTokenStream, InputStream
from plantuml.grammar.generated.PlantUMLDeploymentLexer import PlantUMLDeploymentLexer
from plantuml.grammar.generated.PlantUMLDeploymentParser import PlantUMLDeploymentParser
from plantuml.grammar.generated.PlantUMLDeploymentVisitor import PlantUMLDeploymentVisitor


# ── Regex-based reference extractor ──────────────────────────────────────

# PlantUML element keywords
_KEYWORDS = (
    "actor|agent|artifact|boundary|card|circle|cloud|collections|component|"
    "control|database|entity|file|folder|frame|hexagon|interface|label|"
    "node|package|person|process|queue|rectangle|stack|storage|usecase"
)

_ELEMENT_RE = re.compile(
    rf'^\s*({_KEYWORDS})\s+'
    r'(?:"([^"]+)"|(\S+))'           # quoted or bare name
    r'(?:\s+as\s+(\S+))?'            # optional alias
    r'(?:\s+<<[^>]+>>)*'             # optional stereotypes
    r'(?:\s*#\w+)?'                   # optional color
    r'(?:\s*\{{)?',                    # optional block open
    re.MULTILINE,
)

_CONNECTION_RE = re.compile(
    r'^\s*(\S+)\s+'
    r'(<?[-~.]+(?:\[(?:hidden|bold|dashed|dotted)\])?[-~.]*>?)\s+'
    r'(\S+)'
    r'(?:\s*:\s*"?([^"\n]*)"?)?',
    re.MULTILINE,
)

_SKINPARAM_BLOCK_RE = re.compile(
    r'^\s*skinparam\s+\w+\s*\{[^}]*\}',
    re.MULTILINE | re.DOTALL,
)


def _extract_reference_elements(text: str):
    """Extract elements using regex (reference truth)."""
    elements = {}
    for m in _ELEMENT_RE.finditer(text):
        keyword = m.group(1)
        name = m.group(2) or m.group(3)
        alias = m.group(4) or ""
        key = (alias or name).lower()
        elements[key] = {
            "keyword": keyword,
            "name": name,
            "alias": alias,
            "line": text[:m.start()].count("\n") + 1,
        }
    return elements


def _extract_reference_connections(text: str):
    """Extract connections using regex (reference truth)."""
    connections = []
    for m in _CONNECTION_RE.finditer(text):
        src = m.group(1)
        arrow = m.group(2)
        dst = m.group(3)
        label = (m.group(4) or "").strip().strip('"')
        line = text[:m.start()].count("\n") + 1
        # Skip if src or dst is a keyword (skinparam, title, etc.)
        if src.lower() in ("skinparam", "title", "header", "footer", "caption",
                           "legend", "note", "hide", "remove", "scale",
                           "left", "top", "right", "bottom"):
            continue
        connections.append({
            "src": src, "dst": dst, "arrow": arrow,
            "label": label, "line": line,
        })
    return connections


# ── ANTLR-based extractor ────────────────────────────────────────────────

class _DiagVisitor(PlantUMLDeploymentVisitor):
    def __init__(self):
        self.elements = {}
        self.connections = []

    def _name(self, ctx):
        if ctx.elementName():
            return ctx.elementName().getText().strip('"')
        if ctx.BRACKET_COMP():
            return ctx.BRACKET_COMP().getText().strip("[]")
        if ctx.ACTOR_COLON():
            return ctx.ACTOR_COLON().getText().strip(":")
        if hasattr(ctx, "USECASE_PAREN") and ctx.USECASE_PAREN():
            return ctx.USECASE_PAREN().getText().strip("()")
        return ""

    def _store(self, ctx, keyword, name, alias):
        key = (alias or name).lower()
        line = ctx.start.line if ctx.start else 0
        self.elements[key] = {
            "keyword": keyword, "name": name,
            "alias": alias, "line": line,
        }

    def visitElementDecl(self, ctx):
        name = self._name(ctx)
        kw = ctx.elementKeyword().getText() if ctx.elementKeyword() else ""
        alias = ""
        if ctx.aliasClause():
            alias = ctx.aliasClause().elementName().getText().strip('"')
        self._store(ctx, kw, name, alias)
        return self.visitChildren(ctx)

    def visitElementBlock(self, ctx):
        kw = ctx.elementKeyword().getText() if ctx.elementKeyword() else ""
        name = ctx.elementName().getText().strip('"') if ctx.elementName() else ""
        alias = ""
        if ctx.aliasClause():
            alias = ctx.aliasClause().elementName().getText().strip('"')
        self._store(ctx, kw, name, alias)
        return self.visitChildren(ctx)

    def visitRelationStmt(self, ctx):
        try:
            lhs_ctx = ctx.relationRef(0)
            rhs_ctx = ctx.relationRef(1)
            if not lhs_ctx or not rhs_ctx or not ctx.ARROW_SPEC():
                return self.visitChildren(ctx)
            lhs = lhs_ctx.getText().strip('"')
            rhs = rhs_ctx.getText().strip('"')
            arrow = ctx.ARROW_SPEC().getText()
            label = ""
            if ctx.labelText():
                label = ctx.labelText().getText().strip().strip('"')
            line = ctx.start.line if ctx.start else 0
            self.connections.append({
                "src": lhs, "dst": rhs, "arrow": arrow,
                "label": label, "line": line,
            })
        except Exception:
            pass
        return self.visitChildren(ctx)


def _parse_with_antlr(text: str):
    """Parse with ANTLR and return elements, connections, error count."""
    input_stream = InputStream(text)
    lexer = PlantUMLDeploymentLexer(input_stream)
    lexer.removeErrorListeners()  # suppress stderr noise

    token_stream = CommonTokenStream(lexer)
    parser = PlantUMLDeploymentParser(token_stream)

    # Collect errors
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
    return visitor.elements, visitor.connections, errors


# ── Main diagnostic ──────────────────────────────────────────────────────

def diagnose(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    print(f"=== Deployment Grammar Diagnostic: {os.path.basename(filepath)} ===")
    print(f"Source: {len(text)} chars, {text.count(chr(10))+1} lines\n")

    # Reference extraction
    ref_elems = _extract_reference_elements(text)
    ref_conns = _extract_reference_connections(text)

    # ANTLR extraction
    antlr_elems, antlr_conns, antlr_errors = _parse_with_antlr(text)

    # ── Elements comparison ──
    print(f"{'ELEMENTS':=^72}")
    print(f"  Regex found: {len(ref_elems)}")
    print(f"  ANTLR found: {len(antlr_elems)}")

    ref_keys = set(ref_elems.keys())
    antlr_keys = set(antlr_elems.keys())

    matched = ref_keys & antlr_keys
    missing_from_antlr = ref_keys - antlr_keys
    extra_in_antlr = antlr_keys - ref_keys

    if matched:
        print(f"\n  MATCHED ({len(matched)}):")
        for k in sorted(matched):
            r = ref_elems[k]
            a = antlr_elems[k]
            kw_match = "OK" if r["keyword"] == a["keyword"] else f"MISMATCH: regex={r['keyword']} antlr={a['keyword']}"
            print(f"    {k:30s} keyword={a['keyword']:12s} {kw_match}")

    if missing_from_antlr:
        print(f"\n  MISSING from ANTLR ({len(missing_from_antlr)}):")
        for k in sorted(missing_from_antlr):
            r = ref_elems[k]
            print(f"    line {r['line']:3d}: {r['keyword']:12s} name={r['name']!r} alias={r['alias']!r}")

    if extra_in_antlr:
        print(f"\n  EXTRA in ANTLR ({len(extra_in_antlr)}):")
        for k in sorted(extra_in_antlr):
            a = antlr_elems[k]
            print(f"    line {a['line']:3d}: {a['keyword']:12s} name={a['name']!r} alias={a['alias']!r}")

    # ── Connections comparison ──
    print(f"\n{'CONNECTIONS':=^72}")
    print(f"  Regex found: {len(ref_conns)}")
    print(f"  ANTLR found: {len(antlr_conns)}")

    ref_conn_set = {(c["src"], c["dst"]) for c in ref_conns}
    antlr_conn_set = {(c["src"], c["dst"]) for c in antlr_conns}

    conn_matched = ref_conn_set & antlr_conn_set
    conn_missing = ref_conn_set - antlr_conn_set
    conn_extra = antlr_conn_set - ref_conn_set

    print(f"  Matched: {len(conn_matched)}")

    if conn_missing:
        print(f"\n  MISSING from ANTLR ({len(conn_missing)}):")
        for c in sorted(ref_conns, key=lambda x: x["line"]):
            if (c["src"], c["dst"]) in conn_missing:
                print(f"    line {c['line']:3d}: {c['src']} {c['arrow']} {c['dst']}  label={c['label']!r}")

    if conn_extra:
        print(f"\n  EXTRA in ANTLR ({len(conn_extra)}):")
        for c in sorted(antlr_conns, key=lambda x: x["line"]):
            if (c["src"], c["dst"]) in conn_extra:
                print(f"    line {c['line']:3d}: {c['src']} {c['arrow']} {c['dst']}  label={c['label']!r}")

    # ── Parse errors ──
    if antlr_errors:
        print(f"\n{'ANTLR PARSE ERRORS':=^72}")
        print(f"  {len(antlr_errors)} errors:")
        for e in antlr_errors[:30]:
            print(f"    line {e['line']:3d} col {e['col']:2d}: {e['msg']}")
        if len(antlr_errors) > 30:
            print(f"    ... and {len(antlr_errors) - 30} more")

    # ── Summary ──
    total_ref = len(ref_elems) + len(ref_conns)
    total_antlr = len(antlr_elems) + len(antlr_conns)
    total_missing = len(missing_from_antlr) + len(conn_missing)
    pct = ((total_ref - total_missing) / total_ref * 100) if total_ref > 0 else 0

    print(f"\n{'SUMMARY':=^72}")
    print(f"  Elements: {len(matched)}/{len(ref_elems)} matched ({len(missing_from_antlr)} missing)")
    print(f"  Connections: {len(conn_matched)}/{len(ref_conns)} matched ({len(conn_missing)} missing)")
    print(f"  Coverage: {pct:.0f}% ({total_ref - total_missing}/{total_ref})")
    print(f"  Parse errors: {len(antlr_errors)}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "test_data", "PUML", "t_deployment_parser_stress_test.puml",
        )
    if not os.path.exists(path):
        print(f"File not found: {path}")
        sys.exit(1)
    diagnose(path)
