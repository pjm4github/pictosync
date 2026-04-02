# Generated from plantuml/grammar/PlantUMLActivity.g4 by ANTLR 4.13.0
from antlr4 import *
if "." in __name__:
    from .PlantUMLActivityParser import PlantUMLActivityParser
else:
    from PlantUMLActivityParser import PlantUMLActivityParser

# This class defines a complete generic visitor for a parse tree produced by PlantUMLActivityParser.

class PlantUMLActivityVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by PlantUMLActivityParser#diagram.
    def visitDiagram(self, ctx:PlantUMLActivityParser.DiagramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#filenameHint.
    def visitFilenameHint(self, ctx:PlantUMLActivityParser.FilenameHintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#restOfLine.
    def visitRestOfLine(self, ctx:PlantUMLActivityParser.RestOfLineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#parenContent.
    def visitParenContent(self, ctx:PlantUMLActivityParser.ParenContentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#statement.
    def visitStatement(self, ctx:PlantUMLActivityParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#actionStmt.
    def visitActionStmt(self, ctx:PlantUMLActivityParser.ActionStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#listActionStmt.
    def visitListActionStmt(self, ctx:PlantUMLActivityParser.ListActionStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#arrowStmt.
    def visitArrowStmt(self, ctx:PlantUMLActivityParser.ArrowStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#arrowLabel.
    def visitArrowLabel(self, ctx:PlantUMLActivityParser.ArrowLabelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#connectorStmt.
    def visitConnectorStmt(self, ctx:PlantUMLActivityParser.ConnectorStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#controlStmt.
    def visitControlStmt(self, ctx:PlantUMLActivityParser.ControlStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#swimlaneStmt.
    def visitSwimlaneStmt(self, ctx:PlantUMLActivityParser.SwimlaneStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#ifBlock.
    def visitIfBlock(self, ctx:PlantUMLActivityParser.IfBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#condExpr.
    def visitCondExpr(self, ctx:PlantUMLActivityParser.CondExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#condOp.
    def visitCondOp(self, ctx:PlantUMLActivityParser.CondOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#thenLabel.
    def visitThenLabel(self, ctx:PlantUMLActivityParser.ThenLabelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#elseifBranch.
    def visitElseifBranch(self, ctx:PlantUMLActivityParser.ElseifBranchContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#elseBranch.
    def visitElseBranch(self, ctx:PlantUMLActivityParser.ElseBranchContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#switchBlock.
    def visitSwitchBlock(self, ctx:PlantUMLActivityParser.SwitchBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#caseBranch.
    def visitCaseBranch(self, ctx:PlantUMLActivityParser.CaseBranchContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#repeatBlock.
    def visitRepeatBlock(self, ctx:PlantUMLActivityParser.RepeatBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#backwardClause.
    def visitBackwardClause(self, ctx:PlantUMLActivityParser.BackwardClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#repeatWhileLabels.
    def visitRepeatWhileLabels(self, ctx:PlantUMLActivityParser.RepeatWhileLabelsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#whileBlock.
    def visitWhileBlock(self, ctx:PlantUMLActivityParser.WhileBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#forkBlock.
    def visitForkBlock(self, ctx:PlantUMLActivityParser.ForkBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#forkAgainBranch.
    def visitForkAgainBranch(self, ctx:PlantUMLActivityParser.ForkAgainBranchContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#forkTerminator.
    def visitForkTerminator(self, ctx:PlantUMLActivityParser.ForkTerminatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#joinSpec.
    def visitJoinSpec(self, ctx:PlantUMLActivityParser.JoinSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#splitBlock.
    def visitSplitBlock(self, ctx:PlantUMLActivityParser.SplitBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#splitAgainBranch.
    def visitSplitAgainBranch(self, ctx:PlantUMLActivityParser.SplitAgainBranchContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#containerBlock.
    def visitContainerBlock(self, ctx:PlantUMLActivityParser.ContainerBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#containerKeyword.
    def visitContainerKeyword(self, ctx:PlantUMLActivityParser.ContainerKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#containerName.
    def visitContainerName(self, ctx:PlantUMLActivityParser.ContainerNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#noteStmt.
    def visitNoteStmt(self, ctx:PlantUMLActivityParser.NoteStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#noteBlock.
    def visitNoteBlock(self, ctx:PlantUMLActivityParser.NoteBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#labelStmt.
    def visitLabelStmt(self, ctx:PlantUMLActivityParser.LabelStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#gotoStmt.
    def visitGotoStmt(self, ctx:PlantUMLActivityParser.GotoStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#styleBlock.
    def visitStyleBlock(self, ctx:PlantUMLActivityParser.StyleBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#skinparamStmt.
    def visitSkinparamStmt(self, ctx:PlantUMLActivityParser.SkinparamStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#skinparamBlock.
    def visitSkinparamBlock(self, ctx:PlantUMLActivityParser.SkinparamBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#skinparamEntry.
    def visitSkinparamEntry(self, ctx:PlantUMLActivityParser.SkinparamEntryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#pragmaStmt.
    def visitPragmaStmt(self, ctx:PlantUMLActivityParser.PragmaStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#scaleStmt.
    def visitScaleStmt(self, ctx:PlantUMLActivityParser.ScaleStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#titleStmt.
    def visitTitleStmt(self, ctx:PlantUMLActivityParser.TitleStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#headerStmt.
    def visitHeaderStmt(self, ctx:PlantUMLActivityParser.HeaderStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#footerStmt.
    def visitFooterStmt(self, ctx:PlantUMLActivityParser.FooterStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLActivityParser#captionStmt.
    def visitCaptionStmt(self, ctx:PlantUMLActivityParser.CaptionStmtContext):
        return self.visitChildren(ctx)



del PlantUMLActivityParser