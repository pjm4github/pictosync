# Generated from PlantUMLDeployment.g4 by ANTLR 4.13.0
from antlr4 import *
if "." in __name__:
    from .PlantUMLDeploymentParser import PlantUMLDeploymentParser
else:
    from PlantUMLDeploymentParser import PlantUMLDeploymentParser

# This class defines a complete generic visitor for a parse tree produced by PlantUMLDeploymentParser.

class PlantUMLDeploymentVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by PlantUMLDeploymentParser#diagram.
    def visitDiagram(self, ctx:PlantUMLDeploymentParser.DiagramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#filenameHint.
    def visitFilenameHint(self, ctx:PlantUMLDeploymentParser.FilenameHintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#statement.
    def visitStatement(self, ctx:PlantUMLDeploymentParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#elementDecl.
    def visitElementDecl(self, ctx:PlantUMLDeploymentParser.ElementDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#descriptionBody.
    def visitDescriptionBody(self, ctx:PlantUMLDeploymentParser.DescriptionBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#elementBlock.
    def visitElementBlock(self, ctx:PlantUMLDeploymentParser.ElementBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#blockStatement.
    def visitBlockStatement(self, ctx:PlantUMLDeploymentParser.BlockStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#portDecl.
    def visitPortDecl(self, ctx:PlantUMLDeploymentParser.PortDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#togetherBlock.
    def visitTogetherBlock(self, ctx:PlantUMLDeploymentParser.TogetherBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#elementKeyword.
    def visitElementKeyword(self, ctx:PlantUMLDeploymentParser.ElementKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#elementName.
    def visitElementName(self, ctx:PlantUMLDeploymentParser.ElementNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#aliasClause.
    def visitAliasClause(self, ctx:PlantUMLDeploymentParser.AliasClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#elementModifier.
    def visitElementModifier(self, ctx:PlantUMLDeploymentParser.ElementModifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#colorSpec.
    def visitColorSpec(self, ctx:PlantUMLDeploymentParser.ColorSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#stereotypeClause.
    def visitStereotypeClause(self, ctx:PlantUMLDeploymentParser.StereotypeClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#stereotypeBody.
    def visitStereotypeBody(self, ctx:PlantUMLDeploymentParser.StereotypeBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#spotSpec.
    def visitSpotSpec(self, ctx:PlantUMLDeploymentParser.SpotSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#spotChar.
    def visitSpotChar(self, ctx:PlantUMLDeploymentParser.SpotCharContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#stereotypeText.
    def visitStereotypeText(self, ctx:PlantUMLDeploymentParser.StereotypeTextContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#bodyText.
    def visitBodyText(self, ctx:PlantUMLDeploymentParser.BodyTextContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#restOfLine.
    def visitRestOfLine(self, ctx:PlantUMLDeploymentParser.RestOfLineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#relationStmt.
    def visitRelationStmt(self, ctx:PlantUMLDeploymentParser.RelationStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#relationRef.
    def visitRelationRef(self, ctx:PlantUMLDeploymentParser.RelationRefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#labelText.
    def visitLabelText(self, ctx:PlantUMLDeploymentParser.LabelTextContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#noteStmt.
    def visitNoteStmt(self, ctx:PlantUMLDeploymentParser.NoteStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#noteBlock.
    def visitNoteBlock(self, ctx:PlantUMLDeploymentParser.NoteBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#noteSide.
    def visitNoteSide(self, ctx:PlantUMLDeploymentParser.NoteSideContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#noteBodyLine.
    def visitNoteBodyLine(self, ctx:PlantUMLDeploymentParser.NoteBodyLineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#spriteDecl.
    def visitSpriteDecl(self, ctx:PlantUMLDeploymentParser.SpriteDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#spriteDimension.
    def visitSpriteDimension(self, ctx:PlantUMLDeploymentParser.SpriteDimensionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#spriteRow.
    def visitSpriteRow(self, ctx:PlantUMLDeploymentParser.SpriteRowContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#skinparamStmt.
    def visitSkinparamStmt(self, ctx:PlantUMLDeploymentParser.SkinparamStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#skinparamBlock.
    def visitSkinparamBlock(self, ctx:PlantUMLDeploymentParser.SkinparamBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#skinparamPath.
    def visitSkinparamPath(self, ctx:PlantUMLDeploymentParser.SkinparamPathContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#skinparamEntry.
    def visitSkinparamEntry(self, ctx:PlantUMLDeploymentParser.SkinparamEntryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#visibilityStmt.
    def visitVisibilityStmt(self, ctx:PlantUMLDeploymentParser.VisibilityStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#visibilityKeyword.
    def visitVisibilityKeyword(self, ctx:PlantUMLDeploymentParser.VisibilityKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#visibilityTarget.
    def visitVisibilityTarget(self, ctx:PlantUMLDeploymentParser.VisibilityTargetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#directionStmt.
    def visitDirectionStmt(self, ctx:PlantUMLDeploymentParser.DirectionStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#allowMixingStmt.
    def visitAllowMixingStmt(self, ctx:PlantUMLDeploymentParser.AllowMixingStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#titleStmt.
    def visitTitleStmt(self, ctx:PlantUMLDeploymentParser.TitleStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#headerStmt.
    def visitHeaderStmt(self, ctx:PlantUMLDeploymentParser.HeaderStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#footerStmt.
    def visitFooterStmt(self, ctx:PlantUMLDeploymentParser.FooterStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#captionStmt.
    def visitCaptionStmt(self, ctx:PlantUMLDeploymentParser.CaptionStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#legendBlock.
    def visitLegendBlock(self, ctx:PlantUMLDeploymentParser.LegendBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#legendAlign.
    def visitLegendAlign(self, ctx:PlantUMLDeploymentParser.LegendAlignContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#pragmaStmt.
    def visitPragmaStmt(self, ctx:PlantUMLDeploymentParser.PragmaStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLDeploymentParser#scaleStmt.
    def visitScaleStmt(self, ctx:PlantUMLDeploymentParser.ScaleStmtContext):
        return self.visitChildren(ctx)



del PlantUMLDeploymentParser