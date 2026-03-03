# Generated from MermaidC4Parser.g4 by ANTLR 4.13.0
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,67,220,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,1,0,
        5,0,42,8,0,10,0,12,0,45,9,0,1,0,1,0,4,0,49,8,0,11,0,12,0,50,1,0,
        5,0,54,8,0,10,0,12,0,57,9,0,1,0,1,0,1,1,1,1,1,2,1,2,4,2,65,8,2,11,
        2,12,2,66,1,2,1,2,4,2,71,8,2,11,2,12,2,72,1,2,1,2,1,2,1,2,4,2,79,
        8,2,11,2,12,2,80,1,2,1,2,4,2,85,8,2,11,2,12,2,86,1,2,1,2,4,2,91,
        8,2,11,2,12,2,92,1,2,1,2,4,2,97,8,2,11,2,12,2,98,1,2,1,2,4,2,103,
        8,2,11,2,12,2,104,1,2,4,2,108,8,2,11,2,12,2,109,3,2,112,8,2,1,3,
        1,3,1,3,1,4,1,4,1,5,1,5,1,5,1,5,1,5,1,6,1,6,1,7,1,7,1,7,1,7,1,7,
        1,7,5,7,132,8,7,10,7,12,7,135,9,7,1,7,5,7,138,8,7,10,7,12,7,141,
        9,7,1,7,1,7,4,7,145,8,7,11,7,12,7,146,1,8,1,8,1,9,1,9,1,9,1,9,1,
        9,1,9,5,9,157,8,9,10,9,12,9,160,9,9,1,9,5,9,163,8,9,10,9,12,9,166,
        9,9,1,9,1,9,4,9,170,8,9,11,9,12,9,171,1,10,1,10,1,11,1,11,1,11,1,
        11,1,11,1,12,1,12,1,13,1,13,1,13,1,13,1,13,1,14,1,14,1,14,1,14,1,
        14,1,15,1,15,1,15,1,15,1,15,1,16,1,16,1,16,5,16,201,8,16,10,16,12,
        16,204,9,16,1,16,3,16,207,8,16,1,17,1,17,3,17,211,8,17,1,18,1,18,
        1,18,1,18,1,18,1,19,1,19,1,19,0,0,20,0,2,4,6,8,10,12,14,16,18,20,
        22,24,26,28,30,32,34,36,38,0,9,1,0,1,5,2,0,60,60,67,67,1,0,6,25,
        1,0,26,29,1,0,30,33,1,0,34,45,1,0,46,47,1,0,49,50,1,0,59,62,228,
        0,43,1,0,0,0,2,60,1,0,0,0,4,111,1,0,0,0,6,113,1,0,0,0,8,116,1,0,
        0,0,10,118,1,0,0,0,12,123,1,0,0,0,14,125,1,0,0,0,16,148,1,0,0,0,
        18,150,1,0,0,0,20,173,1,0,0,0,22,175,1,0,0,0,24,180,1,0,0,0,26,182,
        1,0,0,0,28,187,1,0,0,0,30,192,1,0,0,0,32,206,1,0,0,0,34,210,1,0,
        0,0,36,212,1,0,0,0,38,217,1,0,0,0,40,42,5,64,0,0,41,40,1,0,0,0,42,
        45,1,0,0,0,43,41,1,0,0,0,43,44,1,0,0,0,44,46,1,0,0,0,45,43,1,0,0,
        0,46,48,3,2,1,0,47,49,5,64,0,0,48,47,1,0,0,0,49,50,1,0,0,0,50,48,
        1,0,0,0,50,51,1,0,0,0,51,55,1,0,0,0,52,54,3,4,2,0,53,52,1,0,0,0,
        54,57,1,0,0,0,55,53,1,0,0,0,55,56,1,0,0,0,56,58,1,0,0,0,57,55,1,
        0,0,0,58,59,5,0,0,1,59,1,1,0,0,0,60,61,7,0,0,0,61,3,1,0,0,0,62,64,
        3,6,3,0,63,65,5,64,0,0,64,63,1,0,0,0,65,66,1,0,0,0,66,64,1,0,0,0,
        66,67,1,0,0,0,67,112,1,0,0,0,68,70,3,10,5,0,69,71,5,64,0,0,70,69,
        1,0,0,0,71,72,1,0,0,0,72,70,1,0,0,0,72,73,1,0,0,0,73,112,1,0,0,0,
        74,112,3,14,7,0,75,112,3,18,9,0,76,78,3,22,11,0,77,79,5,64,0,0,78,
        77,1,0,0,0,79,80,1,0,0,0,80,78,1,0,0,0,80,81,1,0,0,0,81,112,1,0,
        0,0,82,84,3,26,13,0,83,85,5,64,0,0,84,83,1,0,0,0,85,86,1,0,0,0,86,
        84,1,0,0,0,86,87,1,0,0,0,87,112,1,0,0,0,88,90,3,28,14,0,89,91,5,
        64,0,0,90,89,1,0,0,0,91,92,1,0,0,0,92,90,1,0,0,0,92,93,1,0,0,0,93,
        112,1,0,0,0,94,96,3,30,15,0,95,97,5,64,0,0,96,95,1,0,0,0,97,98,1,
        0,0,0,98,96,1,0,0,0,98,99,1,0,0,0,99,112,1,0,0,0,100,102,5,63,0,
        0,101,103,5,64,0,0,102,101,1,0,0,0,103,104,1,0,0,0,104,102,1,0,0,
        0,104,105,1,0,0,0,105,112,1,0,0,0,106,108,5,64,0,0,107,106,1,0,0,
        0,108,109,1,0,0,0,109,107,1,0,0,0,109,110,1,0,0,0,110,112,1,0,0,
        0,111,62,1,0,0,0,111,68,1,0,0,0,111,74,1,0,0,0,111,75,1,0,0,0,111,
        76,1,0,0,0,111,82,1,0,0,0,111,88,1,0,0,0,111,94,1,0,0,0,111,100,
        1,0,0,0,111,107,1,0,0,0,112,5,1,0,0,0,113,114,5,51,0,0,114,115,3,
        8,4,0,115,7,1,0,0,0,116,117,7,1,0,0,117,9,1,0,0,0,118,119,3,12,6,
        0,119,120,5,52,0,0,120,121,3,32,16,0,121,122,5,53,0,0,122,11,1,0,
        0,0,123,124,7,2,0,0,124,13,1,0,0,0,125,126,3,16,8,0,126,127,5,52,
        0,0,127,128,3,32,16,0,128,129,5,53,0,0,129,133,5,54,0,0,130,132,
        5,64,0,0,131,130,1,0,0,0,132,135,1,0,0,0,133,131,1,0,0,0,133,134,
        1,0,0,0,134,139,1,0,0,0,135,133,1,0,0,0,136,138,3,4,2,0,137,136,
        1,0,0,0,138,141,1,0,0,0,139,137,1,0,0,0,139,140,1,0,0,0,140,142,
        1,0,0,0,141,139,1,0,0,0,142,144,5,55,0,0,143,145,5,64,0,0,144,143,
        1,0,0,0,145,146,1,0,0,0,146,144,1,0,0,0,146,147,1,0,0,0,147,15,1,
        0,0,0,148,149,7,3,0,0,149,17,1,0,0,0,150,151,3,20,10,0,151,152,5,
        52,0,0,152,153,3,32,16,0,153,154,5,53,0,0,154,158,5,54,0,0,155,157,
        5,64,0,0,156,155,1,0,0,0,157,160,1,0,0,0,158,156,1,0,0,0,158,159,
        1,0,0,0,159,164,1,0,0,0,160,158,1,0,0,0,161,163,3,4,2,0,162,161,
        1,0,0,0,163,166,1,0,0,0,164,162,1,0,0,0,164,165,1,0,0,0,165,167,
        1,0,0,0,166,164,1,0,0,0,167,169,5,55,0,0,168,170,5,64,0,0,169,168,
        1,0,0,0,170,171,1,0,0,0,171,169,1,0,0,0,171,172,1,0,0,0,172,19,1,
        0,0,0,173,174,7,4,0,0,174,21,1,0,0,0,175,176,3,24,12,0,176,177,5,
        52,0,0,177,178,3,32,16,0,178,179,5,53,0,0,179,23,1,0,0,0,180,181,
        7,5,0,0,181,25,1,0,0,0,182,183,7,6,0,0,183,184,5,52,0,0,184,185,
        3,32,16,0,185,186,5,53,0,0,186,27,1,0,0,0,187,188,5,48,0,0,188,189,
        5,52,0,0,189,190,3,32,16,0,190,191,5,53,0,0,191,29,1,0,0,0,192,193,
        7,7,0,0,193,194,5,52,0,0,194,195,3,32,16,0,195,196,5,53,0,0,196,
        31,1,0,0,0,197,202,3,34,17,0,198,199,5,56,0,0,199,201,3,34,17,0,
        200,198,1,0,0,0,201,204,1,0,0,0,202,200,1,0,0,0,202,203,1,0,0,0,
        203,207,1,0,0,0,204,202,1,0,0,0,205,207,1,0,0,0,206,197,1,0,0,0,
        206,205,1,0,0,0,207,33,1,0,0,0,208,211,3,36,18,0,209,211,3,38,19,
        0,210,208,1,0,0,0,210,209,1,0,0,0,211,35,1,0,0,0,212,213,5,58,0,
        0,213,214,5,61,0,0,214,215,5,57,0,0,215,216,5,60,0,0,216,37,1,0,
        0,0,217,218,7,8,0,0,218,39,1,0,0,0,21,43,50,55,66,72,80,86,92,98,
        104,109,111,133,139,146,158,164,171,202,206,210
    ]

class MermaidC4Parser ( Parser ):

    grammarFileName = "MermaidC4Parser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'C4Context'", "'C4Container'", "'C4Component'", 
                     "'C4Dynamic'", "'C4Deployment'", "'Person'", "'Person_Ext'", 
                     "'System'", "'System_Ext'", "'SystemDb'", "'SystemDb_Ext'", 
                     "'SystemQueue'", "'SystemQueue_Ext'", "'Container'", 
                     "'Container_Ext'", "'ContainerDb'", "'ContainerDb_Ext'", 
                     "'ContainerQueue'", "'ContainerQueue_Ext'", "'Component'", 
                     "'Component_Ext'", "'ComponentDb'", "'ComponentDb_Ext'", 
                     "'ComponentQueue'", "'ComponentQueue_Ext'", "'Enterprise_Boundary'", 
                     "'System_Boundary'", "'Container_Boundary'", "'Boundary'", 
                     "'Deployment_Node'", "'Node'", "'Node_L'", "'Node_R'", 
                     "'Rel'", "'BiRel'", "'Rel_Back'", "'Rel_U'", "'Rel_Up'", 
                     "'Rel_D'", "'Rel_Down'", "'Rel_L'", "'Rel_Left'", "'Rel_R'", 
                     "'Rel_Right'", "'RelIndex'", "<INVALID>", "<INVALID>", 
                     "'UpdateLayoutConfig'", "'AddElementTag'", "'AddRelTag'", 
                     "'title'", "'('", "')'", "'{'", "'}'", "','", "'='", 
                     "'$'" ]

    symbolicNames = [ "<INVALID>", "C4CONTEXT", "C4CONTAINER", "C4COMPONENT", 
                      "C4DYNAMIC", "C4DEPLOYMENT", "PERSON", "PERSON_EXT", 
                      "SYSTEM", "SYSTEM_EXT", "SYSTEM_DB", "SYSTEM_DB_EXT", 
                      "SYSTEM_QUEUE", "SYSTEM_QUEUE_EXT", "CONTAINER", "CONTAINER_EXT", 
                      "CONTAINER_DB", "CONTAINER_DB_EXT", "CONTAINER_QUEUE", 
                      "CONTAINER_QUEUE_EXT", "COMPONENT", "COMPONENT_EXT", 
                      "COMPONENT_DB", "COMPONENT_DB_EXT", "COMPONENT_QUEUE", 
                      "COMPONENT_QUEUE_EXT", "ENTERPRISE_BOUNDARY", "SYSTEM_BOUNDARY", 
                      "CONTAINER_BOUNDARY", "BOUNDARY", "DEPLOYMENT_NODE", 
                      "NODE", "NODE_L", "NODE_R", "REL", "BIREL", "REL_BACK", 
                      "REL_U", "REL_UP", "REL_D", "REL_DOWN", "REL_L", "REL_LEFT", 
                      "REL_R", "REL_RIGHT", "REL_INDEX", "UPDATE_ELEMENT_STYLE", 
                      "UPDATE_REL_STYLE", "UPDATE_LAYOUT_CONFIG", "ADD_ELEMENT_TAG", 
                      "ADD_REL_TAG", "TITLE", "LPAREN", "RPAREN", "LBRACE", 
                      "RBRACE", "COMMA", "EQUALS", "DOLLAR", "INT", "QUOTED_STRING", 
                      "ID", "UNQUOTED_TEXT", "COMMENT", "NEWLINE", "WS", 
                      "TEXT_WS", "TEXT_REST" ]

    RULE_diagram = 0
    RULE_diagramType = 1
    RULE_statement = 2
    RULE_titleStmt = 3
    RULE_titleText = 4
    RULE_elementStmt = 5
    RULE_elementKw = 6
    RULE_boundaryBlock = 7
    RULE_boundaryKw = 8
    RULE_deployNodeBlock = 9
    RULE_deployNodeKw = 10
    RULE_relationStmt = 11
    RULE_relKw = 12
    RULE_styleStmt = 13
    RULE_layoutStmt = 14
    RULE_addTagStmt = 15
    RULE_argList = 16
    RULE_arg = 17
    RULE_namedArg = 18
    RULE_positionalArg = 19

    ruleNames =  [ "diagram", "diagramType", "statement", "titleStmt", "titleText", 
                   "elementStmt", "elementKw", "boundaryBlock", "boundaryKw", 
                   "deployNodeBlock", "deployNodeKw", "relationStmt", "relKw", 
                   "styleStmt", "layoutStmt", "addTagStmt", "argList", "arg", 
                   "namedArg", "positionalArg" ]

    EOF = Token.EOF
    C4CONTEXT=1
    C4CONTAINER=2
    C4COMPONENT=3
    C4DYNAMIC=4
    C4DEPLOYMENT=5
    PERSON=6
    PERSON_EXT=7
    SYSTEM=8
    SYSTEM_EXT=9
    SYSTEM_DB=10
    SYSTEM_DB_EXT=11
    SYSTEM_QUEUE=12
    SYSTEM_QUEUE_EXT=13
    CONTAINER=14
    CONTAINER_EXT=15
    CONTAINER_DB=16
    CONTAINER_DB_EXT=17
    CONTAINER_QUEUE=18
    CONTAINER_QUEUE_EXT=19
    COMPONENT=20
    COMPONENT_EXT=21
    COMPONENT_DB=22
    COMPONENT_DB_EXT=23
    COMPONENT_QUEUE=24
    COMPONENT_QUEUE_EXT=25
    ENTERPRISE_BOUNDARY=26
    SYSTEM_BOUNDARY=27
    CONTAINER_BOUNDARY=28
    BOUNDARY=29
    DEPLOYMENT_NODE=30
    NODE=31
    NODE_L=32
    NODE_R=33
    REL=34
    BIREL=35
    REL_BACK=36
    REL_U=37
    REL_UP=38
    REL_D=39
    REL_DOWN=40
    REL_L=41
    REL_LEFT=42
    REL_R=43
    REL_RIGHT=44
    REL_INDEX=45
    UPDATE_ELEMENT_STYLE=46
    UPDATE_REL_STYLE=47
    UPDATE_LAYOUT_CONFIG=48
    ADD_ELEMENT_TAG=49
    ADD_REL_TAG=50
    TITLE=51
    LPAREN=52
    RPAREN=53
    LBRACE=54
    RBRACE=55
    COMMA=56
    EQUALS=57
    DOLLAR=58
    INT=59
    QUOTED_STRING=60
    ID=61
    UNQUOTED_TEXT=62
    COMMENT=63
    NEWLINE=64
    WS=65
    TEXT_WS=66
    TEXT_REST=67

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.0")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class DiagramContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def diagramType(self):
            return self.getTypedRuleContext(MermaidC4Parser.DiagramTypeContext,0)


        def EOF(self):
            return self.getToken(MermaidC4Parser.EOF, 0)

        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidC4Parser.NEWLINE)
            else:
                return self.getToken(MermaidC4Parser.NEWLINE, i)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MermaidC4Parser.StatementContext)
            else:
                return self.getTypedRuleContext(MermaidC4Parser.StatementContext,i)


        def getRuleIndex(self):
            return MermaidC4Parser.RULE_diagram

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDiagram" ):
                return visitor.visitDiagram(self)
            else:
                return visitor.visitChildren(self)




    def diagram(self):

        localctx = MermaidC4Parser.DiagramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_diagram)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 43
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==64:
                self.state = 40
                self.match(MermaidC4Parser.NEWLINE)
                self.state = 45
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 46
            self.diagramType()
            self.state = 48 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 47
                    self.match(MermaidC4Parser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 50 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,1,self._ctx)

            self.state = 55
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while ((((_la - 6)) & ~0x3f) == 0 and ((1 << (_la - 6)) & 432415932971745279) != 0):
                self.state = 52
                self.statement()
                self.state = 57
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 58
            self.match(MermaidC4Parser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DiagramTypeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def C4CONTEXT(self):
            return self.getToken(MermaidC4Parser.C4CONTEXT, 0)

        def C4CONTAINER(self):
            return self.getToken(MermaidC4Parser.C4CONTAINER, 0)

        def C4COMPONENT(self):
            return self.getToken(MermaidC4Parser.C4COMPONENT, 0)

        def C4DYNAMIC(self):
            return self.getToken(MermaidC4Parser.C4DYNAMIC, 0)

        def C4DEPLOYMENT(self):
            return self.getToken(MermaidC4Parser.C4DEPLOYMENT, 0)

        def getRuleIndex(self):
            return MermaidC4Parser.RULE_diagramType

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDiagramType" ):
                return visitor.visitDiagramType(self)
            else:
                return visitor.visitChildren(self)




    def diagramType(self):

        localctx = MermaidC4Parser.DiagramTypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_diagramType)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 60
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 62) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def titleStmt(self):
            return self.getTypedRuleContext(MermaidC4Parser.TitleStmtContext,0)


        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidC4Parser.NEWLINE)
            else:
                return self.getToken(MermaidC4Parser.NEWLINE, i)

        def elementStmt(self):
            return self.getTypedRuleContext(MermaidC4Parser.ElementStmtContext,0)


        def boundaryBlock(self):
            return self.getTypedRuleContext(MermaidC4Parser.BoundaryBlockContext,0)


        def deployNodeBlock(self):
            return self.getTypedRuleContext(MermaidC4Parser.DeployNodeBlockContext,0)


        def relationStmt(self):
            return self.getTypedRuleContext(MermaidC4Parser.RelationStmtContext,0)


        def styleStmt(self):
            return self.getTypedRuleContext(MermaidC4Parser.StyleStmtContext,0)


        def layoutStmt(self):
            return self.getTypedRuleContext(MermaidC4Parser.LayoutStmtContext,0)


        def addTagStmt(self):
            return self.getTypedRuleContext(MermaidC4Parser.AddTagStmtContext,0)


        def COMMENT(self):
            return self.getToken(MermaidC4Parser.COMMENT, 0)

        def getRuleIndex(self):
            return MermaidC4Parser.RULE_statement

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStatement" ):
                return visitor.visitStatement(self)
            else:
                return visitor.visitChildren(self)




    def statement(self):

        localctx = MermaidC4Parser.StatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_statement)
        try:
            self.state = 111
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [51]:
                self.enterOuterAlt(localctx, 1)
                self.state = 62
                self.titleStmt()
                self.state = 64 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 63
                        self.match(MermaidC4Parser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 66 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,3,self._ctx)

                pass
            elif token in [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]:
                self.enterOuterAlt(localctx, 2)
                self.state = 68
                self.elementStmt()
                self.state = 70 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 69
                        self.match(MermaidC4Parser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 72 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,4,self._ctx)

                pass
            elif token in [26, 27, 28, 29]:
                self.enterOuterAlt(localctx, 3)
                self.state = 74
                self.boundaryBlock()
                pass
            elif token in [30, 31, 32, 33]:
                self.enterOuterAlt(localctx, 4)
                self.state = 75
                self.deployNodeBlock()
                pass
            elif token in [34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45]:
                self.enterOuterAlt(localctx, 5)
                self.state = 76
                self.relationStmt()
                self.state = 78 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 77
                        self.match(MermaidC4Parser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 80 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,5,self._ctx)

                pass
            elif token in [46, 47]:
                self.enterOuterAlt(localctx, 6)
                self.state = 82
                self.styleStmt()
                self.state = 84 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 83
                        self.match(MermaidC4Parser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 86 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,6,self._ctx)

                pass
            elif token in [48]:
                self.enterOuterAlt(localctx, 7)
                self.state = 88
                self.layoutStmt()
                self.state = 90 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 89
                        self.match(MermaidC4Parser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 92 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,7,self._ctx)

                pass
            elif token in [49, 50]:
                self.enterOuterAlt(localctx, 8)
                self.state = 94
                self.addTagStmt()
                self.state = 96 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 95
                        self.match(MermaidC4Parser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 98 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,8,self._ctx)

                pass
            elif token in [63]:
                self.enterOuterAlt(localctx, 9)
                self.state = 100
                self.match(MermaidC4Parser.COMMENT)
                self.state = 102 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 101
                        self.match(MermaidC4Parser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 104 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,9,self._ctx)

                pass
            elif token in [64]:
                self.enterOuterAlt(localctx, 10)
                self.state = 107 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 106
                        self.match(MermaidC4Parser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 109 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,10,self._ctx)

                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TitleStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TITLE(self):
            return self.getToken(MermaidC4Parser.TITLE, 0)

        def titleText(self):
            return self.getTypedRuleContext(MermaidC4Parser.TitleTextContext,0)


        def getRuleIndex(self):
            return MermaidC4Parser.RULE_titleStmt

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTitleStmt" ):
                return visitor.visitTitleStmt(self)
            else:
                return visitor.visitChildren(self)




    def titleStmt(self):

        localctx = MermaidC4Parser.TitleStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_titleStmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 113
            self.match(MermaidC4Parser.TITLE)
            self.state = 114
            self.titleText()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TitleTextContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def QUOTED_STRING(self):
            return self.getToken(MermaidC4Parser.QUOTED_STRING, 0)

        def TEXT_REST(self):
            return self.getToken(MermaidC4Parser.TEXT_REST, 0)

        def getRuleIndex(self):
            return MermaidC4Parser.RULE_titleText

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTitleText" ):
                return visitor.visitTitleText(self)
            else:
                return visitor.visitChildren(self)




    def titleText(self):

        localctx = MermaidC4Parser.TitleTextContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_titleText)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 116
            _la = self._input.LA(1)
            if not(_la==60 or _la==67):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ElementStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def elementKw(self):
            return self.getTypedRuleContext(MermaidC4Parser.ElementKwContext,0)


        def LPAREN(self):
            return self.getToken(MermaidC4Parser.LPAREN, 0)

        def argList(self):
            return self.getTypedRuleContext(MermaidC4Parser.ArgListContext,0)


        def RPAREN(self):
            return self.getToken(MermaidC4Parser.RPAREN, 0)

        def getRuleIndex(self):
            return MermaidC4Parser.RULE_elementStmt

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitElementStmt" ):
                return visitor.visitElementStmt(self)
            else:
                return visitor.visitChildren(self)




    def elementStmt(self):

        localctx = MermaidC4Parser.ElementStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_elementStmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 118
            self.elementKw()
            self.state = 119
            self.match(MermaidC4Parser.LPAREN)
            self.state = 120
            self.argList()
            self.state = 121
            self.match(MermaidC4Parser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ElementKwContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PERSON(self):
            return self.getToken(MermaidC4Parser.PERSON, 0)

        def PERSON_EXT(self):
            return self.getToken(MermaidC4Parser.PERSON_EXT, 0)

        def SYSTEM(self):
            return self.getToken(MermaidC4Parser.SYSTEM, 0)

        def SYSTEM_EXT(self):
            return self.getToken(MermaidC4Parser.SYSTEM_EXT, 0)

        def SYSTEM_DB(self):
            return self.getToken(MermaidC4Parser.SYSTEM_DB, 0)

        def SYSTEM_DB_EXT(self):
            return self.getToken(MermaidC4Parser.SYSTEM_DB_EXT, 0)

        def SYSTEM_QUEUE(self):
            return self.getToken(MermaidC4Parser.SYSTEM_QUEUE, 0)

        def SYSTEM_QUEUE_EXT(self):
            return self.getToken(MermaidC4Parser.SYSTEM_QUEUE_EXT, 0)

        def CONTAINER(self):
            return self.getToken(MermaidC4Parser.CONTAINER, 0)

        def CONTAINER_EXT(self):
            return self.getToken(MermaidC4Parser.CONTAINER_EXT, 0)

        def CONTAINER_DB(self):
            return self.getToken(MermaidC4Parser.CONTAINER_DB, 0)

        def CONTAINER_DB_EXT(self):
            return self.getToken(MermaidC4Parser.CONTAINER_DB_EXT, 0)

        def CONTAINER_QUEUE(self):
            return self.getToken(MermaidC4Parser.CONTAINER_QUEUE, 0)

        def CONTAINER_QUEUE_EXT(self):
            return self.getToken(MermaidC4Parser.CONTAINER_QUEUE_EXT, 0)

        def COMPONENT(self):
            return self.getToken(MermaidC4Parser.COMPONENT, 0)

        def COMPONENT_EXT(self):
            return self.getToken(MermaidC4Parser.COMPONENT_EXT, 0)

        def COMPONENT_DB(self):
            return self.getToken(MermaidC4Parser.COMPONENT_DB, 0)

        def COMPONENT_DB_EXT(self):
            return self.getToken(MermaidC4Parser.COMPONENT_DB_EXT, 0)

        def COMPONENT_QUEUE(self):
            return self.getToken(MermaidC4Parser.COMPONENT_QUEUE, 0)

        def COMPONENT_QUEUE_EXT(self):
            return self.getToken(MermaidC4Parser.COMPONENT_QUEUE_EXT, 0)

        def getRuleIndex(self):
            return MermaidC4Parser.RULE_elementKw

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitElementKw" ):
                return visitor.visitElementKw(self)
            else:
                return visitor.visitChildren(self)




    def elementKw(self):

        localctx = MermaidC4Parser.ElementKwContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_elementKw)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 123
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 67108800) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BoundaryBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def boundaryKw(self):
            return self.getTypedRuleContext(MermaidC4Parser.BoundaryKwContext,0)


        def LPAREN(self):
            return self.getToken(MermaidC4Parser.LPAREN, 0)

        def argList(self):
            return self.getTypedRuleContext(MermaidC4Parser.ArgListContext,0)


        def RPAREN(self):
            return self.getToken(MermaidC4Parser.RPAREN, 0)

        def LBRACE(self):
            return self.getToken(MermaidC4Parser.LBRACE, 0)

        def RBRACE(self):
            return self.getToken(MermaidC4Parser.RBRACE, 0)

        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidC4Parser.NEWLINE)
            else:
                return self.getToken(MermaidC4Parser.NEWLINE, i)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MermaidC4Parser.StatementContext)
            else:
                return self.getTypedRuleContext(MermaidC4Parser.StatementContext,i)


        def getRuleIndex(self):
            return MermaidC4Parser.RULE_boundaryBlock

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBoundaryBlock" ):
                return visitor.visitBoundaryBlock(self)
            else:
                return visitor.visitChildren(self)




    def boundaryBlock(self):

        localctx = MermaidC4Parser.BoundaryBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_boundaryBlock)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 125
            self.boundaryKw()
            self.state = 126
            self.match(MermaidC4Parser.LPAREN)
            self.state = 127
            self.argList()
            self.state = 128
            self.match(MermaidC4Parser.RPAREN)
            self.state = 129
            self.match(MermaidC4Parser.LBRACE)
            self.state = 133
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,12,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 130
                    self.match(MermaidC4Parser.NEWLINE) 
                self.state = 135
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,12,self._ctx)

            self.state = 139
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while ((((_la - 6)) & ~0x3f) == 0 and ((1 << (_la - 6)) & 432415932971745279) != 0):
                self.state = 136
                self.statement()
                self.state = 141
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 142
            self.match(MermaidC4Parser.RBRACE)
            self.state = 144 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 143
                    self.match(MermaidC4Parser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 146 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,14,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BoundaryKwContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ENTERPRISE_BOUNDARY(self):
            return self.getToken(MermaidC4Parser.ENTERPRISE_BOUNDARY, 0)

        def SYSTEM_BOUNDARY(self):
            return self.getToken(MermaidC4Parser.SYSTEM_BOUNDARY, 0)

        def CONTAINER_BOUNDARY(self):
            return self.getToken(MermaidC4Parser.CONTAINER_BOUNDARY, 0)

        def BOUNDARY(self):
            return self.getToken(MermaidC4Parser.BOUNDARY, 0)

        def getRuleIndex(self):
            return MermaidC4Parser.RULE_boundaryKw

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBoundaryKw" ):
                return visitor.visitBoundaryKw(self)
            else:
                return visitor.visitChildren(self)




    def boundaryKw(self):

        localctx = MermaidC4Parser.BoundaryKwContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_boundaryKw)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 148
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 1006632960) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DeployNodeBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def deployNodeKw(self):
            return self.getTypedRuleContext(MermaidC4Parser.DeployNodeKwContext,0)


        def LPAREN(self):
            return self.getToken(MermaidC4Parser.LPAREN, 0)

        def argList(self):
            return self.getTypedRuleContext(MermaidC4Parser.ArgListContext,0)


        def RPAREN(self):
            return self.getToken(MermaidC4Parser.RPAREN, 0)

        def LBRACE(self):
            return self.getToken(MermaidC4Parser.LBRACE, 0)

        def RBRACE(self):
            return self.getToken(MermaidC4Parser.RBRACE, 0)

        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidC4Parser.NEWLINE)
            else:
                return self.getToken(MermaidC4Parser.NEWLINE, i)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MermaidC4Parser.StatementContext)
            else:
                return self.getTypedRuleContext(MermaidC4Parser.StatementContext,i)


        def getRuleIndex(self):
            return MermaidC4Parser.RULE_deployNodeBlock

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDeployNodeBlock" ):
                return visitor.visitDeployNodeBlock(self)
            else:
                return visitor.visitChildren(self)




    def deployNodeBlock(self):

        localctx = MermaidC4Parser.DeployNodeBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_deployNodeBlock)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 150
            self.deployNodeKw()
            self.state = 151
            self.match(MermaidC4Parser.LPAREN)
            self.state = 152
            self.argList()
            self.state = 153
            self.match(MermaidC4Parser.RPAREN)
            self.state = 154
            self.match(MermaidC4Parser.LBRACE)
            self.state = 158
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,15,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 155
                    self.match(MermaidC4Parser.NEWLINE) 
                self.state = 160
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,15,self._ctx)

            self.state = 164
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while ((((_la - 6)) & ~0x3f) == 0 and ((1 << (_la - 6)) & 432415932971745279) != 0):
                self.state = 161
                self.statement()
                self.state = 166
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 167
            self.match(MermaidC4Parser.RBRACE)
            self.state = 169 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 168
                    self.match(MermaidC4Parser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 171 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,17,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DeployNodeKwContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DEPLOYMENT_NODE(self):
            return self.getToken(MermaidC4Parser.DEPLOYMENT_NODE, 0)

        def NODE(self):
            return self.getToken(MermaidC4Parser.NODE, 0)

        def NODE_L(self):
            return self.getToken(MermaidC4Parser.NODE_L, 0)

        def NODE_R(self):
            return self.getToken(MermaidC4Parser.NODE_R, 0)

        def getRuleIndex(self):
            return MermaidC4Parser.RULE_deployNodeKw

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDeployNodeKw" ):
                return visitor.visitDeployNodeKw(self)
            else:
                return visitor.visitChildren(self)




    def deployNodeKw(self):

        localctx = MermaidC4Parser.DeployNodeKwContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_deployNodeKw)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 173
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 16106127360) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RelationStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def relKw(self):
            return self.getTypedRuleContext(MermaidC4Parser.RelKwContext,0)


        def LPAREN(self):
            return self.getToken(MermaidC4Parser.LPAREN, 0)

        def argList(self):
            return self.getTypedRuleContext(MermaidC4Parser.ArgListContext,0)


        def RPAREN(self):
            return self.getToken(MermaidC4Parser.RPAREN, 0)

        def getRuleIndex(self):
            return MermaidC4Parser.RULE_relationStmt

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRelationStmt" ):
                return visitor.visitRelationStmt(self)
            else:
                return visitor.visitChildren(self)




    def relationStmt(self):

        localctx = MermaidC4Parser.RelationStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_relationStmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 175
            self.relKw()
            self.state = 176
            self.match(MermaidC4Parser.LPAREN)
            self.state = 177
            self.argList()
            self.state = 178
            self.match(MermaidC4Parser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RelKwContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def REL(self):
            return self.getToken(MermaidC4Parser.REL, 0)

        def REL_BACK(self):
            return self.getToken(MermaidC4Parser.REL_BACK, 0)

        def REL_U(self):
            return self.getToken(MermaidC4Parser.REL_U, 0)

        def REL_UP(self):
            return self.getToken(MermaidC4Parser.REL_UP, 0)

        def REL_D(self):
            return self.getToken(MermaidC4Parser.REL_D, 0)

        def REL_DOWN(self):
            return self.getToken(MermaidC4Parser.REL_DOWN, 0)

        def REL_L(self):
            return self.getToken(MermaidC4Parser.REL_L, 0)

        def REL_LEFT(self):
            return self.getToken(MermaidC4Parser.REL_LEFT, 0)

        def REL_R(self):
            return self.getToken(MermaidC4Parser.REL_R, 0)

        def REL_RIGHT(self):
            return self.getToken(MermaidC4Parser.REL_RIGHT, 0)

        def BIREL(self):
            return self.getToken(MermaidC4Parser.BIREL, 0)

        def REL_INDEX(self):
            return self.getToken(MermaidC4Parser.REL_INDEX, 0)

        def getRuleIndex(self):
            return MermaidC4Parser.RULE_relKw

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRelKw" ):
                return visitor.visitRelKw(self)
            else:
                return visitor.visitChildren(self)




    def relKw(self):

        localctx = MermaidC4Parser.RelKwContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_relKw)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 180
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 70351564308480) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StyleStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LPAREN(self):
            return self.getToken(MermaidC4Parser.LPAREN, 0)

        def argList(self):
            return self.getTypedRuleContext(MermaidC4Parser.ArgListContext,0)


        def RPAREN(self):
            return self.getToken(MermaidC4Parser.RPAREN, 0)

        def UPDATE_ELEMENT_STYLE(self):
            return self.getToken(MermaidC4Parser.UPDATE_ELEMENT_STYLE, 0)

        def UPDATE_REL_STYLE(self):
            return self.getToken(MermaidC4Parser.UPDATE_REL_STYLE, 0)

        def getRuleIndex(self):
            return MermaidC4Parser.RULE_styleStmt

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStyleStmt" ):
                return visitor.visitStyleStmt(self)
            else:
                return visitor.visitChildren(self)




    def styleStmt(self):

        localctx = MermaidC4Parser.StyleStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_styleStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 182
            _la = self._input.LA(1)
            if not(_la==46 or _la==47):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 183
            self.match(MermaidC4Parser.LPAREN)
            self.state = 184
            self.argList()
            self.state = 185
            self.match(MermaidC4Parser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LayoutStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def UPDATE_LAYOUT_CONFIG(self):
            return self.getToken(MermaidC4Parser.UPDATE_LAYOUT_CONFIG, 0)

        def LPAREN(self):
            return self.getToken(MermaidC4Parser.LPAREN, 0)

        def argList(self):
            return self.getTypedRuleContext(MermaidC4Parser.ArgListContext,0)


        def RPAREN(self):
            return self.getToken(MermaidC4Parser.RPAREN, 0)

        def getRuleIndex(self):
            return MermaidC4Parser.RULE_layoutStmt

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLayoutStmt" ):
                return visitor.visitLayoutStmt(self)
            else:
                return visitor.visitChildren(self)




    def layoutStmt(self):

        localctx = MermaidC4Parser.LayoutStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_layoutStmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 187
            self.match(MermaidC4Parser.UPDATE_LAYOUT_CONFIG)
            self.state = 188
            self.match(MermaidC4Parser.LPAREN)
            self.state = 189
            self.argList()
            self.state = 190
            self.match(MermaidC4Parser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AddTagStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LPAREN(self):
            return self.getToken(MermaidC4Parser.LPAREN, 0)

        def argList(self):
            return self.getTypedRuleContext(MermaidC4Parser.ArgListContext,0)


        def RPAREN(self):
            return self.getToken(MermaidC4Parser.RPAREN, 0)

        def ADD_ELEMENT_TAG(self):
            return self.getToken(MermaidC4Parser.ADD_ELEMENT_TAG, 0)

        def ADD_REL_TAG(self):
            return self.getToken(MermaidC4Parser.ADD_REL_TAG, 0)

        def getRuleIndex(self):
            return MermaidC4Parser.RULE_addTagStmt

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAddTagStmt" ):
                return visitor.visitAddTagStmt(self)
            else:
                return visitor.visitChildren(self)




    def addTagStmt(self):

        localctx = MermaidC4Parser.AddTagStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_addTagStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 192
            _la = self._input.LA(1)
            if not(_la==49 or _la==50):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 193
            self.match(MermaidC4Parser.LPAREN)
            self.state = 194
            self.argList()
            self.state = 195
            self.match(MermaidC4Parser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ArgListContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def arg(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MermaidC4Parser.ArgContext)
            else:
                return self.getTypedRuleContext(MermaidC4Parser.ArgContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidC4Parser.COMMA)
            else:
                return self.getToken(MermaidC4Parser.COMMA, i)

        def getRuleIndex(self):
            return MermaidC4Parser.RULE_argList

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitArgList" ):
                return visitor.visitArgList(self)
            else:
                return visitor.visitChildren(self)




    def argList(self):

        localctx = MermaidC4Parser.ArgListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_argList)
        self._la = 0 # Token type
        try:
            self.state = 206
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [58, 59, 60, 61, 62]:
                self.enterOuterAlt(localctx, 1)
                self.state = 197
                self.arg()
                self.state = 202
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==56:
                    self.state = 198
                    self.match(MermaidC4Parser.COMMA)
                    self.state = 199
                    self.arg()
                    self.state = 204
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass
            elif token in [53]:
                self.enterOuterAlt(localctx, 2)

                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ArgContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def namedArg(self):
            return self.getTypedRuleContext(MermaidC4Parser.NamedArgContext,0)


        def positionalArg(self):
            return self.getTypedRuleContext(MermaidC4Parser.PositionalArgContext,0)


        def getRuleIndex(self):
            return MermaidC4Parser.RULE_arg

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitArg" ):
                return visitor.visitArg(self)
            else:
                return visitor.visitChildren(self)




    def arg(self):

        localctx = MermaidC4Parser.ArgContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_arg)
        try:
            self.state = 210
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [58]:
                self.enterOuterAlt(localctx, 1)
                self.state = 208
                self.namedArg()
                pass
            elif token in [59, 60, 61, 62]:
                self.enterOuterAlt(localctx, 2)
                self.state = 209
                self.positionalArg()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NamedArgContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DOLLAR(self):
            return self.getToken(MermaidC4Parser.DOLLAR, 0)

        def ID(self):
            return self.getToken(MermaidC4Parser.ID, 0)

        def EQUALS(self):
            return self.getToken(MermaidC4Parser.EQUALS, 0)

        def QUOTED_STRING(self):
            return self.getToken(MermaidC4Parser.QUOTED_STRING, 0)

        def getRuleIndex(self):
            return MermaidC4Parser.RULE_namedArg

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNamedArg" ):
                return visitor.visitNamedArg(self)
            else:
                return visitor.visitChildren(self)




    def namedArg(self):

        localctx = MermaidC4Parser.NamedArgContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_namedArg)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 212
            self.match(MermaidC4Parser.DOLLAR)
            self.state = 213
            self.match(MermaidC4Parser.ID)
            self.state = 214
            self.match(MermaidC4Parser.EQUALS)
            self.state = 215
            self.match(MermaidC4Parser.QUOTED_STRING)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PositionalArgContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def QUOTED_STRING(self):
            return self.getToken(MermaidC4Parser.QUOTED_STRING, 0)

        def UNQUOTED_TEXT(self):
            return self.getToken(MermaidC4Parser.UNQUOTED_TEXT, 0)

        def ID(self):
            return self.getToken(MermaidC4Parser.ID, 0)

        def INT(self):
            return self.getToken(MermaidC4Parser.INT, 0)

        def getRuleIndex(self):
            return MermaidC4Parser.RULE_positionalArg

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPositionalArg" ):
                return visitor.visitPositionalArg(self)
            else:
                return visitor.visitChildren(self)




    def positionalArg(self):

        localctx = MermaidC4Parser.PositionalArgContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_positionalArg)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 217
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 8646911284551352320) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





