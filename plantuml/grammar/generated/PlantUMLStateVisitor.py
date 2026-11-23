# Generated from plantuml/grammar/PlantUMLState.g4 by ANTLR 4.13.0
from antlr4 import *
if "." in __name__:
    from .PlantUMLStateParser import PlantUMLStateParser
else:
    from PlantUMLStateParser import PlantUMLStateParser

# This class defines a complete generic visitor for a parse tree produced by PlantUMLStateParser.

class PlantUMLStateVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by PlantUMLStateParser#diagram.
    def visitDiagram(self, ctx:PlantUMLStateParser.DiagramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#filenameHint.
    def visitFilenameHint(self, ctx:PlantUMLStateParser.FilenameHintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#restOfLine.
    def visitRestOfLine(self, ctx:PlantUMLStateParser.RestOfLineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#statement.
    def visitStatement(self, ctx:PlantUMLStateParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#stateDecl.
    def visitStateDecl(self, ctx:PlantUMLStateParser.StateDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#stateName.
    def visitStateName(self, ctx:PlantUMLStateParser.StateNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#aliasClause.
    def visitAliasClause(self, ctx:PlantUMLStateParser.AliasClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#colorStyle.
    def visitColorStyle(self, ctx:PlantUMLStateParser.ColorStyleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#stereotypeClause.
    def visitStereotypeClause(self, ctx:PlantUMLStateParser.StereotypeClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#compositeBlock.
    def visitCompositeBlock(self, ctx:PlantUMLStateParser.CompositeBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#concurrentSep.
    def visitConcurrentSep(self, ctx:PlantUMLStateParser.ConcurrentSepContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#transitionStmt.
    def visitTransitionStmt(self, ctx:PlantUMLStateParser.TransitionStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#transitionEnd.
    def visitTransitionEnd(self, ctx:PlantUMLStateParser.TransitionEndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#descriptionStmt.
    def visitDescriptionStmt(self, ctx:PlantUMLStateParser.DescriptionStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#stateRef.
    def visitStateRef(self, ctx:PlantUMLStateParser.StateRefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#noteStmt.
    def visitNoteStmt(self, ctx:PlantUMLStateParser.NoteStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#noteBlock.
    def visitNoteBlock(self, ctx:PlantUMLStateParser.NoteBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#noteLinkBlock.
    def visitNoteLinkBlock(self, ctx:PlantUMLStateParser.NoteLinkBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#noteSide.
    def visitNoteSide(self, ctx:PlantUMLStateParser.NoteSideContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#noteBodyLine.
    def visitNoteBodyLine(self, ctx:PlantUMLStateParser.NoteBodyLineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#hideStmt.
    def visitHideStmt(self, ctx:PlantUMLStateParser.HideStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#directionStmt.
    def visitDirectionStmt(self, ctx:PlantUMLStateParser.DirectionStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#scaleStmt.
    def visitScaleStmt(self, ctx:PlantUMLStateParser.ScaleStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#titleStmt.
    def visitTitleStmt(self, ctx:PlantUMLStateParser.TitleStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#headerStmt.
    def visitHeaderStmt(self, ctx:PlantUMLStateParser.HeaderStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#footerStmt.
    def visitFooterStmt(self, ctx:PlantUMLStateParser.FooterStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#captionStmt.
    def visitCaptionStmt(self, ctx:PlantUMLStateParser.CaptionStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#skinparamStmt.
    def visitSkinparamStmt(self, ctx:PlantUMLStateParser.SkinparamStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#skinparamBlock.
    def visitSkinparamBlock(self, ctx:PlantUMLStateParser.SkinparamBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#skinparamName.
    def visitSkinparamName(self, ctx:PlantUMLStateParser.SkinparamNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#skinparamEntry.
    def visitSkinparamEntry(self, ctx:PlantUMLStateParser.SkinparamEntryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#styleBlock.
    def visitStyleBlock(self, ctx:PlantUMLStateParser.StyleBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLStateParser#pragmaStmt.
    def visitPragmaStmt(self, ctx:PlantUMLStateParser.PragmaStmtContext):
        return self.visitChildren(ctx)



del PlantUMLStateParser