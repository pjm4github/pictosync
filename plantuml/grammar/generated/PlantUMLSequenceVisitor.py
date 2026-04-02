# Generated from plantuml/grammar/PlantUMLSequence.g4 by ANTLR 4.13.0
from antlr4 import *
if "." in __name__:
    from .PlantUMLSequenceParser import PlantUMLSequenceParser
else:
    from PlantUMLSequenceParser import PlantUMLSequenceParser

# This class defines a complete generic visitor for a parse tree produced by PlantUMLSequenceParser.

class PlantUMLSequenceVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by PlantUMLSequenceParser#diagram.
    def visitDiagram(self, ctx:PlantUMLSequenceParser.DiagramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#filenameHint.
    def visitFilenameHint(self, ctx:PlantUMLSequenceParser.FilenameHintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#restOfLine.
    def visitRestOfLine(self, ctx:PlantUMLSequenceParser.RestOfLineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#participantKeyword.
    def visitParticipantKeyword(self, ctx:PlantUMLSequenceParser.ParticipantKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#statement.
    def visitStatement(self, ctx:PlantUMLSequenceParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#participantDecl.
    def visitParticipantDecl(self, ctx:PlantUMLSequenceParser.ParticipantDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#participantModifier.
    def visitParticipantModifier(self, ctx:PlantUMLSequenceParser.ParticipantModifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#participantType.
    def visitParticipantType(self, ctx:PlantUMLSequenceParser.ParticipantTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#participantName.
    def visitParticipantName(self, ctx:PlantUMLSequenceParser.ParticipantNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#aliasClause.
    def visitAliasClause(self, ctx:PlantUMLSequenceParser.AliasClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#colorSpec.
    def visitColorSpec(self, ctx:PlantUMLSequenceParser.ColorSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#orderClause.
    def visitOrderClause(self, ctx:PlantUMLSequenceParser.OrderClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#stereotypeClause.
    def visitStereotypeClause(self, ctx:PlantUMLSequenceParser.StereotypeClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#stereotypeBody.
    def visitStereotypeBody(self, ctx:PlantUMLSequenceParser.StereotypeBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#spotSpec.
    def visitSpotSpec(self, ctx:PlantUMLSequenceParser.SpotSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#spotChar.
    def visitSpotChar(self, ctx:PlantUMLSequenceParser.SpotCharContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#multiBody.
    def visitMultiBody(self, ctx:PlantUMLSequenceParser.MultiBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#multiBodyLine.
    def visitMultiBodyLine(self, ctx:PlantUMLSequenceParser.MultiBodyLineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#createStmt.
    def visitCreateStmt(self, ctx:PlantUMLSequenceParser.CreateStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#messageStmt.
    def visitMessageStmt(self, ctx:PlantUMLSequenceParser.MessageStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#messageSource.
    def visitMessageSource(self, ctx:PlantUMLSequenceParser.MessageSourceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#messageTarget.
    def visitMessageTarget(self, ctx:PlantUMLSequenceParser.MessageTargetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#participantRef.
    def visitParticipantRef(self, ctx:PlantUMLSequenceParser.ParticipantRefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#arrowSpec.
    def visitArrowSpec(self, ctx:PlantUMLSequenceParser.ArrowSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#lifelineShorthand.
    def visitLifelineShorthand(self, ctx:PlantUMLSequenceParser.LifelineShorthandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#messageLabel.
    def visitMessageLabel(self, ctx:PlantUMLSequenceParser.MessageLabelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#activateStmt.
    def visitActivateStmt(self, ctx:PlantUMLSequenceParser.ActivateStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#deactivateStmt.
    def visitDeactivateStmt(self, ctx:PlantUMLSequenceParser.DeactivateStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#destroyStmt.
    def visitDestroyStmt(self, ctx:PlantUMLSequenceParser.DestroyStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#returnStmt.
    def visitReturnStmt(self, ctx:PlantUMLSequenceParser.ReturnStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#autoactivateStmt.
    def visitAutoactivateStmt(self, ctx:PlantUMLSequenceParser.AutoactivateStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#autonumberStmt.
    def visitAutonumberStmt(self, ctx:PlantUMLSequenceParser.AutonumberStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#autonumberArgs.
    def visitAutonumberArgs(self, ctx:PlantUMLSequenceParser.AutonumberArgsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#autonumberStart.
    def visitAutonumberStart(self, ctx:PlantUMLSequenceParser.AutonumberStartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#groupBlock.
    def visitGroupBlock(self, ctx:PlantUMLSequenceParser.GroupBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#groupKeyword.
    def visitGroupKeyword(self, ctx:PlantUMLSequenceParser.GroupKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#groupLabel.
    def visitGroupLabel(self, ctx:PlantUMLSequenceParser.GroupLabelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#elseBranch.
    def visitElseBranch(self, ctx:PlantUMLSequenceParser.ElseBranchContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#partitionBlock.
    def visitPartitionBlock(self, ctx:PlantUMLSequenceParser.PartitionBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#noteStmt.
    def visitNoteStmt(self, ctx:PlantUMLSequenceParser.NoteStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#noteBlock.
    def visitNoteBlock(self, ctx:PlantUMLSequenceParser.NoteBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#noteAlign.
    def visitNoteAlign(self, ctx:PlantUMLSequenceParser.NoteAlignContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#noteKeyword.
    def visitNoteKeyword(self, ctx:PlantUMLSequenceParser.NoteKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#notePosition.
    def visitNotePosition(self, ctx:PlantUMLSequenceParser.NotePositionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#noteBodyLine.
    def visitNoteBodyLine(self, ctx:PlantUMLSequenceParser.NoteBodyLineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#noteEndKeyword.
    def visitNoteEndKeyword(self, ctx:PlantUMLSequenceParser.NoteEndKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#refStmt.
    def visitRefStmt(self, ctx:PlantUMLSequenceParser.RefStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#refBlock.
    def visitRefBlock(self, ctx:PlantUMLSequenceParser.RefBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#boxBlock.
    def visitBoxBlock(self, ctx:PlantUMLSequenceParser.BoxBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#dividerStmt.
    def visitDividerStmt(self, ctx:PlantUMLSequenceParser.DividerStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#dividerContent.
    def visitDividerContent(self, ctx:PlantUMLSequenceParser.DividerContentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#spacerStmt.
    def visitSpacerStmt(self, ctx:PlantUMLSequenceParser.SpacerStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#titleStmt.
    def visitTitleStmt(self, ctx:PlantUMLSequenceParser.TitleStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#titleBlock.
    def visitTitleBlock(self, ctx:PlantUMLSequenceParser.TitleBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#headerStmt.
    def visitHeaderStmt(self, ctx:PlantUMLSequenceParser.HeaderStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#footerStmt.
    def visitFooterStmt(self, ctx:PlantUMLSequenceParser.FooterStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#newpageStmt.
    def visitNewpageStmt(self, ctx:PlantUMLSequenceParser.NewpageStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#anchorStmt.
    def visitAnchorStmt(self, ctx:PlantUMLSequenceParser.AnchorStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#durationStmt.
    def visitDurationStmt(self, ctx:PlantUMLSequenceParser.DurationStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#pragmaStmt.
    def visitPragmaStmt(self, ctx:PlantUMLSequenceParser.PragmaStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#skinparamStmt.
    def visitSkinparamStmt(self, ctx:PlantUMLSequenceParser.SkinparamStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#skinparamBlock.
    def visitSkinparamBlock(self, ctx:PlantUMLSequenceParser.SkinparamBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#skinparamEntry.
    def visitSkinparamEntry(self, ctx:PlantUMLSequenceParser.SkinparamEntryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#hidestmt.
    def visitHidestmt(self, ctx:PlantUMLSequenceParser.HidestmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLSequenceParser#freeText.
    def visitFreeText(self, ctx:PlantUMLSequenceParser.FreeTextContext):
        return self.visitChildren(ctx)



del PlantUMLSequenceParser