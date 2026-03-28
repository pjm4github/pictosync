"""Test the PlantUMLDeployment grammar against test_deployment.puml."""
from __future__ import annotations

import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from antlr4 import CommonTokenStream, InputStream
from plantuml.grammar.generated.PlantUMLDeploymentLexer import PlantUMLDeploymentLexer
from plantuml.grammar.generated.PlantUMLDeploymentParser import PlantUMLDeploymentParser
from plantuml.grammar.generated.PlantUMLDeploymentVisitor import PlantUMLDeploymentVisitor


class DeploymentPrintVisitor(PlantUMLDeploymentVisitor):
    """Walk the parse tree and print what was found."""

    def __init__(self):
        self.indent = 0

    def _print(self, msg):
        print("  " * self.indent + msg)

    def visitElementDecl(self, ctx):
        name = ""
        if ctx.elementName():
            name = ctx.elementName().getText()
        elif ctx.BRACKET_COMP():
            name = ctx.BRACKET_COMP().getText()
        elif ctx.ACTOR_COLON():
            name = ctx.ACTOR_COLON().getText()
        keyword = ""
        if ctx.elementKeyword():
            keyword = ctx.elementKeyword().getText()
        alias = ""
        if ctx.aliasClause():
            alias = ctx.aliasClause().elementName().getText()
        self._print(f"ELEMENT: keyword={keyword!r} name={name!r} alias={alias!r}")
        return self.visitChildren(ctx)

    def visitElementBlock(self, ctx):
        keyword = ctx.elementKeyword().getText() if ctx.elementKeyword() else "?"
        name = ctx.elementName().getText() if ctx.elementName() else ""
        alias = ""
        if ctx.aliasClause():
            alias = ctx.aliasClause().elementName().getText()
        self._print(f"BLOCK: keyword={keyword!r} name={name!r} alias={alias!r} {{")
        self.indent += 1
        result = self.visitChildren(ctx)
        self.indent -= 1
        self._print("}")
        return result

    def visitRelationStmt(self, ctx):
        lhs = ctx.relationRef(0).getText()
        rhs = ctx.relationRef(1).getText()
        arrow = ctx.ARROW_SPEC().getText()
        label = ""
        if ctx.labelText():
            label = ctx.labelText().getText()
        self._print(f"RELATION: {lhs!r} {arrow} {rhs!r} label={label!r}")
        return self.visitChildren(ctx)

    def visitPortDecl(self, ctx):
        name = ctx.elementName().getText()
        kind = "port"
        if ctx.KW_PORTIN():
            kind = "portin"
        elif ctx.KW_PORTOUT():
            kind = "portout"
        self._print(f"PORT: {kind} {name!r}")
        return self.visitChildren(ctx)

    def visitNoteStmt(self, ctx):
        self._print(f"NOTE: {ctx.getText()}")
        return self.visitChildren(ctx)


def parse_file(filepath: str):
    """Parse a .puml file and print the parse tree."""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    print(f"=== Parsing: {os.path.basename(filepath)} ===")
    print(f"Input ({len(text)} chars):")
    print(text)
    print()

    input_stream = InputStream(text)
    lexer = PlantUMLDeploymentLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = PlantUMLDeploymentParser(token_stream)

    # Parse
    tree = parser.diagram()

    # Check for errors
    if parser.getNumberOfSyntaxErrors() > 0:
        print(f"PARSE ERRORS: {parser.getNumberOfSyntaxErrors()}")
    else:
        print("PARSE OK (no syntax errors)")

    print()
    print("=== Parse Tree (visitor walk) ===")
    visitor = DeploymentPrintVisitor()
    visitor.visit(tree)

    print()
    print("=== LISP-style tree ===")
    print(tree.toStringTree(recog=parser))


if __name__ == "__main__":
    test_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "test_data", "PUML", "test_deployment.puml"
    )
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        sys.exit(1)
    parse_file(test_file)
