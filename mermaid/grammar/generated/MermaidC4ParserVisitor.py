# Generated from MermaidC4Parser.g4 by ANTLR 4.13.0
from antlr4 import *
if "." in __name__:
    from .MermaidC4Parser import MermaidC4Parser
else:
    from MermaidC4Parser import MermaidC4Parser

# This class defines a complete generic visitor for a parse tree produced by MermaidC4Parser.

class MermaidC4ParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by MermaidC4Parser#diagram.
    def visitDiagram(self, ctx:MermaidC4Parser.DiagramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidC4Parser#diagramType.
    def visitDiagramType(self, ctx:MermaidC4Parser.DiagramTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidC4Parser#statement.
    def visitStatement(self, ctx:MermaidC4Parser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidC4Parser#titleStmt.
    def visitTitleStmt(self, ctx:MermaidC4Parser.TitleStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidC4Parser#titleText.
    def visitTitleText(self, ctx:MermaidC4Parser.TitleTextContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidC4Parser#elementStmt.
    def visitElementStmt(self, ctx:MermaidC4Parser.ElementStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidC4Parser#elementKw.
    def visitElementKw(self, ctx:MermaidC4Parser.ElementKwContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidC4Parser#boundaryBlock.
    def visitBoundaryBlock(self, ctx:MermaidC4Parser.BoundaryBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidC4Parser#boundaryKw.
    def visitBoundaryKw(self, ctx:MermaidC4Parser.BoundaryKwContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidC4Parser#deployNodeBlock.
    def visitDeployNodeBlock(self, ctx:MermaidC4Parser.DeployNodeBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidC4Parser#deployNodeKw.
    def visitDeployNodeKw(self, ctx:MermaidC4Parser.DeployNodeKwContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidC4Parser#relationStmt.
    def visitRelationStmt(self, ctx:MermaidC4Parser.RelationStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidC4Parser#relKw.
    def visitRelKw(self, ctx:MermaidC4Parser.RelKwContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidC4Parser#styleStmt.
    def visitStyleStmt(self, ctx:MermaidC4Parser.StyleStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidC4Parser#layoutStmt.
    def visitLayoutStmt(self, ctx:MermaidC4Parser.LayoutStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidC4Parser#addTagStmt.
    def visitAddTagStmt(self, ctx:MermaidC4Parser.AddTagStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidC4Parser#argList.
    def visitArgList(self, ctx:MermaidC4Parser.ArgListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidC4Parser#arg.
    def visitArg(self, ctx:MermaidC4Parser.ArgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidC4Parser#namedArg.
    def visitNamedArg(self, ctx:MermaidC4Parser.NamedArgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidC4Parser#positionalArg.
    def visitPositionalArg(self, ctx:MermaidC4Parser.PositionalArgContext):
        return self.visitChildren(ctx)



del MermaidC4Parser