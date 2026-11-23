# Generated from plantuml/grammar/PlantUMLComponent.g4 by ANTLR 4.13.0
from antlr4 import *
if "." in __name__:
    from .PlantUMLComponentParser import PlantUMLComponentParser
else:
    from PlantUMLComponentParser import PlantUMLComponentParser

# This class defines a complete generic visitor for a parse tree produced by PlantUMLComponentParser.

class PlantUMLComponentVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by PlantUMLComponentParser#diagram.
    def visitDiagram(self, ctx:PlantUMLComponentParser.DiagramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#filenameHint.
    def visitFilenameHint(self, ctx:PlantUMLComponentParser.FilenameHintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#restOfLine.
    def visitRestOfLine(self, ctx:PlantUMLComponentParser.RestOfLineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#statement.
    def visitStatement(self, ctx:PlantUMLComponentParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#componentFullDecl.
    def visitComponentFullDecl(self, ctx:PlantUMLComponentParser.ComponentFullDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#componentBodyDesc.
    def visitComponentBodyDesc(self, ctx:PlantUMLComponentParser.ComponentBodyDescContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#innerStatement.
    def visitInnerStatement(self, ctx:PlantUMLComponentParser.InnerStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#portDecl.
    def visitPortDecl(self, ctx:PlantUMLComponentParser.PortDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#interfaceDecl.
    def visitInterfaceDecl(self, ctx:PlantUMLComponentParser.InterfaceDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#elementName.
    def visitElementName(self, ctx:PlantUMLComponentParser.ElementNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#aliasClause.
    def visitAliasClause(self, ctx:PlantUMLComponentParser.AliasClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#componentModifier.
    def visitComponentModifier(self, ctx:PlantUMLComponentParser.ComponentModifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#stereotypeClause.
    def visitStereotypeClause(self, ctx:PlantUMLComponentParser.StereotypeClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#stereotypeBody.
    def visitStereotypeBody(self, ctx:PlantUMLComponentParser.StereotypeBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#groupBlock.
    def visitGroupBlock(self, ctx:PlantUMLComponentParser.GroupBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#groupKeyword.
    def visitGroupKeyword(self, ctx:PlantUMLComponentParser.GroupKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#relationStmt.
    def visitRelationStmt(self, ctx:PlantUMLComponentParser.RelationStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#relationRef.
    def visitRelationRef(self, ctx:PlantUMLComponentParser.RelationRefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#noteStmt.
    def visitNoteStmt(self, ctx:PlantUMLComponentParser.NoteStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#noteBlock.
    def visitNoteBlock(self, ctx:PlantUMLComponentParser.NoteBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#noteSide.
    def visitNoteSide(self, ctx:PlantUMLComponentParser.NoteSideContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#noteBodyLine.
    def visitNoteBodyLine(self, ctx:PlantUMLComponentParser.NoteBodyLineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#spriteDecl.
    def visitSpriteDecl(self, ctx:PlantUMLComponentParser.SpriteDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#spriteDimension.
    def visitSpriteDimension(self, ctx:PlantUMLComponentParser.SpriteDimensionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#spriteRow.
    def visitSpriteRow(self, ctx:PlantUMLComponentParser.SpriteRowContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#skinparamStmt.
    def visitSkinparamStmt(self, ctx:PlantUMLComponentParser.SkinparamStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#skinparamBlock.
    def visitSkinparamBlock(self, ctx:PlantUMLComponentParser.SkinparamBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#skinparamName.
    def visitSkinparamName(self, ctx:PlantUMLComponentParser.SkinparamNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#skinparamEntry.
    def visitSkinparamEntry(self, ctx:PlantUMLComponentParser.SkinparamEntryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#visibilityStmt.
    def visitVisibilityStmt(self, ctx:PlantUMLComponentParser.VisibilityStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#visibilityKeyword.
    def visitVisibilityKeyword(self, ctx:PlantUMLComponentParser.VisibilityKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#visibilityTarget.
    def visitVisibilityTarget(self, ctx:PlantUMLComponentParser.VisibilityTargetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#directionStmt.
    def visitDirectionStmt(self, ctx:PlantUMLComponentParser.DirectionStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#allowMixingStmt.
    def visitAllowMixingStmt(self, ctx:PlantUMLComponentParser.AllowMixingStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#titleStmt.
    def visitTitleStmt(self, ctx:PlantUMLComponentParser.TitleStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#headerStmt.
    def visitHeaderStmt(self, ctx:PlantUMLComponentParser.HeaderStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#footerStmt.
    def visitFooterStmt(self, ctx:PlantUMLComponentParser.FooterStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#captionStmt.
    def visitCaptionStmt(self, ctx:PlantUMLComponentParser.CaptionStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#legendBlock.
    def visitLegendBlock(self, ctx:PlantUMLComponentParser.LegendBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#legendAlign.
    def visitLegendAlign(self, ctx:PlantUMLComponentParser.LegendAlignContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#pragmaStmt.
    def visitPragmaStmt(self, ctx:PlantUMLComponentParser.PragmaStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLComponentParser#scaleStmt.
    def visitScaleStmt(self, ctx:PlantUMLComponentParser.ScaleStmtContext):
        return self.visitChildren(ctx)



del PlantUMLComponentParser