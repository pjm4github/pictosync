# Generated from C:\Users\pmora\OneDrive\Documents\Git\GitHub\pictosync\mermaid\grammar\MermaidStateDiagramParser.g4 by ANTLR 4.13.0
from antlr4 import *
if "." in __name__:
    from .MermaidStateDiagramParser import MermaidStateDiagramParser
else:
    from MermaidStateDiagramParser import MermaidStateDiagramParser

# This class defines a complete generic visitor for a parse tree produced by MermaidStateDiagramParser.

class MermaidStateDiagramParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by MermaidStateDiagramParser#diagram.
    def visitDiagram(self, ctx:MermaidStateDiagramParser.DiagramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidStateDiagramParser#diagramType.
    def visitDiagramType(self, ctx:MermaidStateDiagramParser.DiagramTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidStateDiagramParser#statement.
    def visitStatement(self, ctx:MermaidStateDiagramParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidStateDiagramParser#stateDecl.
    def visitStateDecl(self, ctx:MermaidStateDiagramParser.StateDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidStateDiagramParser#stateId.
    def visitStateId(self, ctx:MermaidStateDiagramParser.StateIdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidStateDiagramParser#descriptionText.
    def visitDescriptionText(self, ctx:MermaidStateDiagramParser.DescriptionTextContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidStateDiagramParser#classShorthand.
    def visitClassShorthand(self, ctx:MermaidStateDiagramParser.ClassShorthandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidStateDiagramParser#transitionStmt.
    def visitTransitionStmt(self, ctx:MermaidStateDiagramParser.TransitionStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidStateDiagramParser#stateRef.
    def visitStateRef(self, ctx:MermaidStateDiagramParser.StateRefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidStateDiagramParser#transitionLabel.
    def visitTransitionLabel(self, ctx:MermaidStateDiagramParser.TransitionLabelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidStateDiagramParser#compositeBlock.
    def visitCompositeBlock(self, ctx:MermaidStateDiagramParser.CompositeBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidStateDiagramParser#concurrencyDiv.
    def visitConcurrencyDiv(self, ctx:MermaidStateDiagramParser.ConcurrencyDivContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidStateDiagramParser#noteBlock.
    def visitNoteBlock(self, ctx:MermaidStateDiagramParser.NoteBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidStateDiagramParser#noteSide.
    def visitNoteSide(self, ctx:MermaidStateDiagramParser.NoteSideContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidStateDiagramParser#noteLineContent.
    def visitNoteLineContent(self, ctx:MermaidStateDiagramParser.NoteLineContentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidStateDiagramParser#noteBodyLine.
    def visitNoteBodyLine(self, ctx:MermaidStateDiagramParser.NoteBodyLineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidStateDiagramParser#directionStmt.
    def visitDirectionStmt(self, ctx:MermaidStateDiagramParser.DirectionStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidStateDiagramParser#direction.
    def visitDirection(self, ctx:MermaidStateDiagramParser.DirectionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidStateDiagramParser#classDefStmt.
    def visitClassDefStmt(self, ctx:MermaidStateDiagramParser.ClassDefStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidStateDiagramParser#classNameList.
    def visitClassNameList(self, ctx:MermaidStateDiagramParser.ClassNameListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidStateDiagramParser#classAssignStmt.
    def visitClassAssignStmt(self, ctx:MermaidStateDiagramParser.ClassAssignStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidStateDiagramParser#stateIdList.
    def visitStateIdList(self, ctx:MermaidStateDiagramParser.StateIdListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidStateDiagramParser#cssString.
    def visitCssString(self, ctx:MermaidStateDiagramParser.CssStringContext):
        return self.visitChildren(ctx)



del MermaidStateDiagramParser