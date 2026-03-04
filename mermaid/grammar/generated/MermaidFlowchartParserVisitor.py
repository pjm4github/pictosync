# Generated from C:\Users\pmora\OneDrive\Documents\Git\GitHub\pictosync\mermaid\grammar\MermaidFlowchartParser.g4 by ANTLR 4.13.0
from antlr4 import *
if "." in __name__:
    from .MermaidFlowchartParser import MermaidFlowchartParser
else:
    from MermaidFlowchartParser import MermaidFlowchartParser

# This class defines a complete generic visitor for a parse tree produced by MermaidFlowchartParser.

class MermaidFlowchartParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by MermaidFlowchartParser#diagram.
    def visitDiagram(self, ctx:MermaidFlowchartParser.DiagramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#header.
    def visitHeader(self, ctx:MermaidFlowchartParser.HeaderContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#direction.
    def visitDirection(self, ctx:MermaidFlowchartParser.DirectionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#statement.
    def visitStatement(self, ctx:MermaidFlowchartParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#directionStmt.
    def visitDirectionStmt(self, ctx:MermaidFlowchartParser.DirectionStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#nodeStmt.
    def visitNodeStmt(self, ctx:MermaidFlowchartParser.NodeStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#nodeId.
    def visitNodeId(self, ctx:MermaidFlowchartParser.NodeIdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#classShorthand.
    def visitClassShorthand(self, ctx:MermaidFlowchartParser.ClassShorthandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#classicShape.
    def visitClassicShape(self, ctx:MermaidFlowchartParser.ClassicShapeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#nodeLabel.
    def visitNodeLabel(self, ctx:MermaidFlowchartParser.NodeLabelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#labelText.
    def visitLabelText(self, ctx:MermaidFlowchartParser.LabelTextContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#attrBlock.
    def visitAttrBlock(self, ctx:MermaidFlowchartParser.AttrBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#attrList.
    def visitAttrList(self, ctx:MermaidFlowchartParser.AttrListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#attr.
    def visitAttr(self, ctx:MermaidFlowchartParser.AttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#attrKey.
    def visitAttrKey(self, ctx:MermaidFlowchartParser.AttrKeyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#attrVal.
    def visitAttrVal(self, ctx:MermaidFlowchartParser.AttrValContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#edgeChainStmt.
    def visitEdgeChainStmt(self, ctx:MermaidFlowchartParser.EdgeChainStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#nodeGroup.
    def visitNodeGroup(self, ctx:MermaidFlowchartParser.NodeGroupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#nodeRef.
    def visitNodeRef(self, ctx:MermaidFlowchartParser.NodeRefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#edgeOp.
    def visitEdgeOp(self, ctx:MermaidFlowchartParser.EdgeOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#edgeIdPrefix.
    def visitEdgeIdPrefix(self, ctx:MermaidFlowchartParser.EdgeIdPrefixContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#edge.
    def visitEdge(self, ctx:MermaidFlowchartParser.EdgeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#pipeLabel.
    def visitPipeLabel(self, ctx:MermaidFlowchartParser.PipeLabelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#subgraphBlock.
    def visitSubgraphBlock(self, ctx:MermaidFlowchartParser.SubgraphBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#subgraphHeader.
    def visitSubgraphHeader(self, ctx:MermaidFlowchartParser.SubgraphHeaderContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#subgraphTitle.
    def visitSubgraphTitle(self, ctx:MermaidFlowchartParser.SubgraphTitleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#classDefStmt.
    def visitClassDefStmt(self, ctx:MermaidFlowchartParser.ClassDefStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#classNameList.
    def visitClassNameList(self, ctx:MermaidFlowchartParser.ClassNameListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#classAssignStmt.
    def visitClassAssignStmt(self, ctx:MermaidFlowchartParser.ClassAssignStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#nodeIdList.
    def visitNodeIdList(self, ctx:MermaidFlowchartParser.NodeIdListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#linkStyleStmt.
    def visitLinkStyleStmt(self, ctx:MermaidFlowchartParser.LinkStyleStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#linkStyleTargets.
    def visitLinkStyleTargets(self, ctx:MermaidFlowchartParser.LinkStyleTargetsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#nodeStyleStmt.
    def visitNodeStyleStmt(self, ctx:MermaidFlowchartParser.NodeStyleStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#cssString.
    def visitCssString(self, ctx:MermaidFlowchartParser.CssStringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#clickStmt.
    def visitClickStmt(self, ctx:MermaidFlowchartParser.ClickStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#clickAction.
    def visitClickAction(self, ctx:MermaidFlowchartParser.ClickActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#clickTarget.
    def visitClickTarget(self, ctx:MermaidFlowchartParser.ClickTargetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidFlowchartParser#edgePropStmt.
    def visitEdgePropStmt(self, ctx:MermaidFlowchartParser.EdgePropStmtContext):
        return self.visitChildren(ctx)



del MermaidFlowchartParser