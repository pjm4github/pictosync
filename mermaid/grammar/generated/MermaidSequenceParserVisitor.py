# Generated from C:\Users\pmora\OneDrive\Documents\Git\GitHub\pictosync\mermaid\grammar\MermaidSequenceParser.g4 by ANTLR 4.13.0
from antlr4 import *
if "." in __name__:
    from .MermaidSequenceParser import MermaidSequenceParser
else:
    from MermaidSequenceParser import MermaidSequenceParser

# This class defines a complete generic visitor for a parse tree produced by MermaidSequenceParser.

class MermaidSequenceParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by MermaidSequenceParser#diagram.
    def visitDiagram(self, ctx:MermaidSequenceParser.DiagramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#statement.
    def visitStatement(self, ctx:MermaidSequenceParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#participantDecl.
    def visitParticipantDecl(self, ctx:MermaidSequenceParser.ParticipantDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#participantType.
    def visitParticipantType(self, ctx:MermaidSequenceParser.ParticipantTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#actorDecl.
    def visitActorDecl(self, ctx:MermaidSequenceParser.ActorDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#participantId.
    def visitParticipantId(self, ctx:MermaidSequenceParser.ParticipantIdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#label.
    def visitLabel(self, ctx:MermaidSequenceParser.LabelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#boxBlock.
    def visitBoxBlock(self, ctx:MermaidSequenceParser.BoxBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#boxColor.
    def visitBoxColor(self, ctx:MermaidSequenceParser.BoxColorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#boxLabel.
    def visitBoxLabel(self, ctx:MermaidSequenceParser.BoxLabelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#createDirective.
    def visitCreateDirective(self, ctx:MermaidSequenceParser.CreateDirectiveContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#destroyDirective.
    def visitDestroyDirective(self, ctx:MermaidSequenceParser.DestroyDirectiveContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#messageStatement.
    def visitMessageStatement(self, ctx:MermaidSequenceParser.MessageStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#sender.
    def visitSender(self, ctx:MermaidSequenceParser.SenderContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#receiver.
    def visitReceiver(self, ctx:MermaidSequenceParser.ReceiverContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#messageText.
    def visitMessageText(self, ctx:MermaidSequenceParser.MessageTextContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#activateStatement.
    def visitActivateStatement(self, ctx:MermaidSequenceParser.ActivateStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#deactivateStatement.
    def visitDeactivateStatement(self, ctx:MermaidSequenceParser.DeactivateStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#noteStatement.
    def visitNoteStatement(self, ctx:MermaidSequenceParser.NoteStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#notePosition.
    def visitNotePosition(self, ctx:MermaidSequenceParser.NotePositionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#noteText.
    def visitNoteText(self, ctx:MermaidSequenceParser.NoteTextContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#loopBlock.
    def visitLoopBlock(self, ctx:MermaidSequenceParser.LoopBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#loopLabel.
    def visitLoopLabel(self, ctx:MermaidSequenceParser.LoopLabelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#altBlock.
    def visitAltBlock(self, ctx:MermaidSequenceParser.AltBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#optBlock.
    def visitOptBlock(self, ctx:MermaidSequenceParser.OptBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#altCondition.
    def visitAltCondition(self, ctx:MermaidSequenceParser.AltConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#optCondition.
    def visitOptCondition(self, ctx:MermaidSequenceParser.OptConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#parBlock.
    def visitParBlock(self, ctx:MermaidSequenceParser.ParBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#parLabel.
    def visitParLabel(self, ctx:MermaidSequenceParser.ParLabelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#criticalBlock.
    def visitCriticalBlock(self, ctx:MermaidSequenceParser.CriticalBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#criticalAction.
    def visitCriticalAction(self, ctx:MermaidSequenceParser.CriticalActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#optionCondition.
    def visitOptionCondition(self, ctx:MermaidSequenceParser.OptionConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#breakBlock.
    def visitBreakBlock(self, ctx:MermaidSequenceParser.BreakBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#breakCondition.
    def visitBreakCondition(self, ctx:MermaidSequenceParser.BreakConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#rectBlock.
    def visitRectBlock(self, ctx:MermaidSequenceParser.RectBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#rectColor.
    def visitRectColor(self, ctx:MermaidSequenceParser.RectColorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#autonumberStatement.
    def visitAutonumberStatement(self, ctx:MermaidSequenceParser.AutonumberStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#linkStatement.
    def visitLinkStatement(self, ctx:MermaidSequenceParser.LinkStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#linksStatement.
    def visitLinksStatement(self, ctx:MermaidSequenceParser.LinksStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#linkLabel.
    def visitLinkLabel(self, ctx:MermaidSequenceParser.LinkLabelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#linkUrl.
    def visitLinkUrl(self, ctx:MermaidSequenceParser.LinkUrlContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#jsonObject.
    def visitJsonObject(self, ctx:MermaidSequenceParser.JsonObjectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidSequenceParser#jsonPair.
    def visitJsonPair(self, ctx:MermaidSequenceParser.JsonPairContext):
        return self.visitChildren(ctx)



del MermaidSequenceParser