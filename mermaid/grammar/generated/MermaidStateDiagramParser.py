# Generated from C:\Users\pmora\OneDrive\Documents\Git\GitHub\pictosync\mermaid\grammar\MermaidStateDiagramParser.g4 by ANTLR 4.13.0
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
        4,1,41,326,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,
        7,20,2,21,7,21,2,22,7,22,1,0,5,0,48,8,0,10,0,12,0,51,9,0,1,0,1,0,
        5,0,55,8,0,10,0,12,0,58,9,0,1,0,5,0,61,8,0,10,0,12,0,64,9,0,1,0,
        1,0,1,1,1,1,1,2,1,2,5,2,72,8,2,10,2,12,2,75,9,2,1,2,1,2,5,2,79,8,
        2,10,2,12,2,82,9,2,1,2,1,2,1,2,1,2,5,2,88,8,2,10,2,12,2,91,9,2,1,
        2,1,2,5,2,95,8,2,10,2,12,2,98,9,2,1,2,1,2,5,2,102,8,2,10,2,12,2,
        105,9,2,1,2,1,2,5,2,109,8,2,10,2,12,2,112,9,2,1,2,1,2,5,2,116,8,
        2,10,2,12,2,119,9,2,1,2,4,2,122,8,2,11,2,12,2,123,3,2,126,8,2,1,
        3,1,3,1,3,1,3,1,3,3,3,133,8,3,1,3,1,3,1,3,1,3,1,3,3,3,140,8,3,1,
        3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,3,3,152,8,3,3,3,154,8,3,1,
        4,1,4,1,5,4,5,159,8,5,11,5,12,5,160,1,6,1,6,1,6,1,7,1,7,1,7,1,7,
        1,7,3,7,171,8,7,1,8,1,8,3,8,175,8,8,1,8,1,8,3,8,179,8,8,3,8,181,
        8,8,1,9,4,9,184,8,9,11,9,12,9,185,1,10,1,10,1,10,1,10,1,10,1,10,
        4,10,194,8,10,11,10,12,10,195,1,10,5,10,199,8,10,10,10,12,10,202,
        9,10,1,10,1,10,4,10,206,8,10,11,10,12,10,207,1,10,1,10,1,10,1,10,
        4,10,214,8,10,11,10,12,10,215,1,10,5,10,219,8,10,10,10,12,10,222,
        9,10,1,10,1,10,4,10,226,8,10,11,10,12,10,227,3,10,230,8,10,1,11,
        1,11,1,12,1,12,1,12,1,12,1,12,1,12,1,12,5,12,241,8,12,10,12,12,12,
        244,9,12,1,12,1,12,1,12,1,12,1,12,1,12,4,12,252,8,12,11,12,12,12,
        253,1,12,1,12,5,12,258,8,12,10,12,12,12,261,9,12,3,12,263,8,12,1,
        13,1,13,1,14,4,14,268,8,14,11,14,12,14,269,1,15,4,15,273,8,15,11,
        15,12,15,274,1,15,4,15,278,8,15,11,15,12,15,279,1,15,4,15,283,8,
        15,11,15,12,15,284,3,15,287,8,15,1,16,1,16,1,16,1,17,1,17,1,18,1,
        18,1,18,1,18,1,19,1,19,1,19,5,19,301,8,19,10,19,12,19,304,9,19,1,
        20,1,20,1,20,1,20,1,21,1,21,1,21,5,21,313,8,21,10,21,12,21,316,9,
        21,1,22,4,22,319,8,22,11,22,12,22,320,1,22,3,22,324,8,22,1,22,0,
        0,23,0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,
        44,0,3,1,0,1,2,1,0,10,11,1,0,13,17,355,0,49,1,0,0,0,2,67,1,0,0,0,
        4,125,1,0,0,0,6,153,1,0,0,0,8,155,1,0,0,0,10,158,1,0,0,0,12,162,
        1,0,0,0,14,165,1,0,0,0,16,180,1,0,0,0,18,183,1,0,0,0,20,229,1,0,
        0,0,22,231,1,0,0,0,24,262,1,0,0,0,26,264,1,0,0,0,28,267,1,0,0,0,
        30,286,1,0,0,0,32,288,1,0,0,0,34,291,1,0,0,0,36,293,1,0,0,0,38,297,
        1,0,0,0,40,305,1,0,0,0,42,309,1,0,0,0,44,318,1,0,0,0,46,48,5,34,
        0,0,47,46,1,0,0,0,48,51,1,0,0,0,49,47,1,0,0,0,49,50,1,0,0,0,50,52,
        1,0,0,0,51,49,1,0,0,0,52,56,3,2,1,0,53,55,5,34,0,0,54,53,1,0,0,0,
        55,58,1,0,0,0,56,54,1,0,0,0,56,57,1,0,0,0,57,62,1,0,0,0,58,56,1,
        0,0,0,59,61,3,4,2,0,60,59,1,0,0,0,61,64,1,0,0,0,62,60,1,0,0,0,62,
        63,1,0,0,0,63,65,1,0,0,0,64,62,1,0,0,0,65,66,5,0,0,1,66,1,1,0,0,
        0,67,68,7,0,0,0,68,3,1,0,0,0,69,73,3,6,3,0,70,72,5,34,0,0,71,70,
        1,0,0,0,72,75,1,0,0,0,73,71,1,0,0,0,73,74,1,0,0,0,74,126,1,0,0,0,
        75,73,1,0,0,0,76,80,3,14,7,0,77,79,5,34,0,0,78,77,1,0,0,0,79,82,
        1,0,0,0,80,78,1,0,0,0,80,81,1,0,0,0,81,126,1,0,0,0,82,80,1,0,0,0,
        83,126,3,20,10,0,84,126,3,24,12,0,85,89,3,22,11,0,86,88,5,34,0,0,
        87,86,1,0,0,0,88,91,1,0,0,0,89,87,1,0,0,0,89,90,1,0,0,0,90,126,1,
        0,0,0,91,89,1,0,0,0,92,96,3,32,16,0,93,95,5,34,0,0,94,93,1,0,0,0,
        95,98,1,0,0,0,96,94,1,0,0,0,96,97,1,0,0,0,97,126,1,0,0,0,98,96,1,
        0,0,0,99,103,3,36,18,0,100,102,5,34,0,0,101,100,1,0,0,0,102,105,
        1,0,0,0,103,101,1,0,0,0,103,104,1,0,0,0,104,126,1,0,0,0,105,103,
        1,0,0,0,106,110,3,40,20,0,107,109,5,34,0,0,108,107,1,0,0,0,109,112,
        1,0,0,0,110,108,1,0,0,0,110,111,1,0,0,0,111,126,1,0,0,0,112,110,
        1,0,0,0,113,117,5,33,0,0,114,116,5,34,0,0,115,114,1,0,0,0,116,119,
        1,0,0,0,117,115,1,0,0,0,117,118,1,0,0,0,118,126,1,0,0,0,119,117,
        1,0,0,0,120,122,5,34,0,0,121,120,1,0,0,0,122,123,1,0,0,0,123,121,
        1,0,0,0,123,124,1,0,0,0,124,126,1,0,0,0,125,69,1,0,0,0,125,76,1,
        0,0,0,125,83,1,0,0,0,125,84,1,0,0,0,125,85,1,0,0,0,125,92,1,0,0,
        0,125,99,1,0,0,0,125,106,1,0,0,0,125,113,1,0,0,0,125,121,1,0,0,0,
        126,5,1,0,0,0,127,128,5,3,0,0,128,129,5,22,0,0,129,130,5,4,0,0,130,
        132,3,8,4,0,131,133,3,12,6,0,132,131,1,0,0,0,132,133,1,0,0,0,133,
        154,1,0,0,0,134,135,5,3,0,0,135,136,3,8,4,0,136,137,5,32,0,0,137,
        139,3,10,5,0,138,140,3,12,6,0,139,138,1,0,0,0,139,140,1,0,0,0,140,
        154,1,0,0,0,141,142,5,3,0,0,142,143,3,8,4,0,143,144,5,19,0,0,144,
        154,1,0,0,0,145,146,3,8,4,0,146,147,5,32,0,0,147,148,3,10,5,0,148,
        154,1,0,0,0,149,151,3,8,4,0,150,152,3,12,6,0,151,150,1,0,0,0,151,
        152,1,0,0,0,152,154,1,0,0,0,153,127,1,0,0,0,153,134,1,0,0,0,153,
        141,1,0,0,0,153,145,1,0,0,0,153,149,1,0,0,0,154,7,1,0,0,0,155,156,
        5,31,0,0,156,9,1,0,0,0,157,159,5,36,0,0,158,157,1,0,0,0,159,160,
        1,0,0,0,160,158,1,0,0,0,160,161,1,0,0,0,161,11,1,0,0,0,162,163,5,
        23,0,0,163,164,5,31,0,0,164,13,1,0,0,0,165,166,3,16,8,0,166,167,
        5,20,0,0,167,170,3,16,8,0,168,169,5,32,0,0,169,171,3,18,9,0,170,
        168,1,0,0,0,170,171,1,0,0,0,171,15,1,0,0,0,172,174,3,8,4,0,173,175,
        3,12,6,0,174,173,1,0,0,0,174,175,1,0,0,0,175,181,1,0,0,0,176,178,
        5,18,0,0,177,179,3,12,6,0,178,177,1,0,0,0,178,179,1,0,0,0,179,181,
        1,0,0,0,180,172,1,0,0,0,180,176,1,0,0,0,181,17,1,0,0,0,182,184,5,
        36,0,0,183,182,1,0,0,0,184,185,1,0,0,0,185,183,1,0,0,0,185,186,1,
        0,0,0,186,19,1,0,0,0,187,188,5,3,0,0,188,189,5,22,0,0,189,190,5,
        4,0,0,190,191,3,8,4,0,191,193,5,26,0,0,192,194,5,34,0,0,193,192,
        1,0,0,0,194,195,1,0,0,0,195,193,1,0,0,0,195,196,1,0,0,0,196,200,
        1,0,0,0,197,199,3,4,2,0,198,197,1,0,0,0,199,202,1,0,0,0,200,198,
        1,0,0,0,200,201,1,0,0,0,201,203,1,0,0,0,202,200,1,0,0,0,203,205,
        5,27,0,0,204,206,5,34,0,0,205,204,1,0,0,0,206,207,1,0,0,0,207,205,
        1,0,0,0,207,208,1,0,0,0,208,230,1,0,0,0,209,210,5,3,0,0,210,211,
        3,8,4,0,211,213,5,26,0,0,212,214,5,34,0,0,213,212,1,0,0,0,214,215,
        1,0,0,0,215,213,1,0,0,0,215,216,1,0,0,0,216,220,1,0,0,0,217,219,
        3,4,2,0,218,217,1,0,0,0,219,222,1,0,0,0,220,218,1,0,0,0,220,221,
        1,0,0,0,221,223,1,0,0,0,222,220,1,0,0,0,223,225,5,27,0,0,224,226,
        5,34,0,0,225,224,1,0,0,0,226,227,1,0,0,0,227,225,1,0,0,0,227,228,
        1,0,0,0,228,230,1,0,0,0,229,187,1,0,0,0,229,209,1,0,0,0,230,21,1,
        0,0,0,231,232,5,21,0,0,232,23,1,0,0,0,233,234,5,8,0,0,234,235,3,
        26,13,0,235,236,5,9,0,0,236,237,3,8,4,0,237,238,5,32,0,0,238,242,
        3,28,14,0,239,241,5,34,0,0,240,239,1,0,0,0,241,244,1,0,0,0,242,240,
        1,0,0,0,242,243,1,0,0,0,243,263,1,0,0,0,244,242,1,0,0,0,245,246,
        5,8,0,0,246,247,3,26,13,0,247,248,5,9,0,0,248,249,3,8,4,0,249,251,
        5,34,0,0,250,252,3,30,15,0,251,250,1,0,0,0,252,253,1,0,0,0,253,251,
        1,0,0,0,253,254,1,0,0,0,254,255,1,0,0,0,255,259,5,12,0,0,256,258,
        5,34,0,0,257,256,1,0,0,0,258,261,1,0,0,0,259,257,1,0,0,0,259,260,
        1,0,0,0,260,263,1,0,0,0,261,259,1,0,0,0,262,233,1,0,0,0,262,245,
        1,0,0,0,263,25,1,0,0,0,264,265,7,1,0,0,265,27,1,0,0,0,266,268,5,
        36,0,0,267,266,1,0,0,0,268,269,1,0,0,0,269,267,1,0,0,0,269,270,1,
        0,0,0,270,29,1,0,0,0,271,273,5,36,0,0,272,271,1,0,0,0,273,274,1,
        0,0,0,274,272,1,0,0,0,274,275,1,0,0,0,275,277,1,0,0,0,276,278,5,
        34,0,0,277,276,1,0,0,0,278,279,1,0,0,0,279,277,1,0,0,0,279,280,1,
        0,0,0,280,287,1,0,0,0,281,283,5,34,0,0,282,281,1,0,0,0,283,284,1,
        0,0,0,284,282,1,0,0,0,284,285,1,0,0,0,285,287,1,0,0,0,286,272,1,
        0,0,0,286,282,1,0,0,0,287,31,1,0,0,0,288,289,5,5,0,0,289,290,3,34,
        17,0,290,33,1,0,0,0,291,292,7,2,0,0,292,35,1,0,0,0,293,294,5,6,0,
        0,294,295,3,38,19,0,295,296,3,44,22,0,296,37,1,0,0,0,297,302,5,31,
        0,0,298,299,5,29,0,0,299,301,5,31,0,0,300,298,1,0,0,0,301,304,1,
        0,0,0,302,300,1,0,0,0,302,303,1,0,0,0,303,39,1,0,0,0,304,302,1,0,
        0,0,305,306,5,7,0,0,306,307,3,42,21,0,307,308,5,31,0,0,308,41,1,
        0,0,0,309,314,5,31,0,0,310,311,5,29,0,0,311,313,5,31,0,0,312,310,
        1,0,0,0,313,316,1,0,0,0,314,312,1,0,0,0,314,315,1,0,0,0,315,43,1,
        0,0,0,316,314,1,0,0,0,317,319,5,40,0,0,318,317,1,0,0,0,319,320,1,
        0,0,0,320,318,1,0,0,0,320,321,1,0,0,0,321,323,1,0,0,0,322,324,5,
        28,0,0,323,322,1,0,0,0,323,324,1,0,0,0,324,45,1,0,0,0,42,49,56,62,
        73,80,89,96,103,110,117,123,125,132,139,151,153,160,170,174,178,
        180,185,195,200,207,215,220,227,229,242,253,259,262,269,274,279,
        284,286,302,314,320,323
    ]

class MermaidStateDiagramParser ( Parser ):

    grammarFileName = "MermaidStateDiagramParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'stateDiagram-v2'", "'stateDiagram'", 
                     "'state'", "'as'", "'direction'", "'classDef'", "'class'", 
                     "'note'", "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "'TB'", "'TD'", "'BT'", "'LR'", "'RL'", "'[*]'", "<INVALID>", 
                     "'-->'", "'--'", "<INVALID>", "':::'", "'['", "']'", 
                     "'{'", "'}'", "';'", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "':'" ]

    symbolicNames = [ "<INVALID>", "KW_STATE_DIAGRAM_V2", "KW_STATE_DIAGRAM", 
                      "KW_STATE", "KW_AS", "KW_DIRECTION", "KW_CLASSDEF", 
                      "KW_CLASS", "KW_NOTE", "KW_OF", "KW_RIGHT", "KW_LEFT", 
                      "KW_END_NOTE", "DIR_TB", "DIR_TD", "DIR_BT", "DIR_LR", 
                      "DIR_RL", "START_END", "STEREOTYPE", "TRANSITION", 
                      "CONCURRENCY", "QUOTED_STRING", "TRIPLE_COLON", "LBRACK", 
                      "RBRACK", "LBRACE", "RBRACE", "SEMI", "COMMA", "INT", 
                      "ID", "COLON", "COMMENT", "NEWLINE", "WS", "FREE_TEXT", 
                      "NOTE_HDR_WS", "NOTE_BODY_WS", "CSS_READY_WS", "CSS_VALUE_START", 
                      "CSS_WS" ]

    RULE_diagram = 0
    RULE_diagramType = 1
    RULE_statement = 2
    RULE_stateDecl = 3
    RULE_stateId = 4
    RULE_descriptionText = 5
    RULE_classShorthand = 6
    RULE_transitionStmt = 7
    RULE_stateRef = 8
    RULE_transitionLabel = 9
    RULE_compositeBlock = 10
    RULE_concurrencyDiv = 11
    RULE_noteBlock = 12
    RULE_noteSide = 13
    RULE_noteLineContent = 14
    RULE_noteBodyLine = 15
    RULE_directionStmt = 16
    RULE_direction = 17
    RULE_classDefStmt = 18
    RULE_classNameList = 19
    RULE_classAssignStmt = 20
    RULE_stateIdList = 21
    RULE_cssString = 22

    ruleNames =  [ "diagram", "diagramType", "statement", "stateDecl", "stateId", 
                   "descriptionText", "classShorthand", "transitionStmt", 
                   "stateRef", "transitionLabel", "compositeBlock", "concurrencyDiv", 
                   "noteBlock", "noteSide", "noteLineContent", "noteBodyLine", 
                   "directionStmt", "direction", "classDefStmt", "classNameList", 
                   "classAssignStmt", "stateIdList", "cssString" ]

    EOF = Token.EOF
    KW_STATE_DIAGRAM_V2=1
    KW_STATE_DIAGRAM=2
    KW_STATE=3
    KW_AS=4
    KW_DIRECTION=5
    KW_CLASSDEF=6
    KW_CLASS=7
    KW_NOTE=8
    KW_OF=9
    KW_RIGHT=10
    KW_LEFT=11
    KW_END_NOTE=12
    DIR_TB=13
    DIR_TD=14
    DIR_BT=15
    DIR_LR=16
    DIR_RL=17
    START_END=18
    STEREOTYPE=19
    TRANSITION=20
    CONCURRENCY=21
    QUOTED_STRING=22
    TRIPLE_COLON=23
    LBRACK=24
    RBRACK=25
    LBRACE=26
    RBRACE=27
    SEMI=28
    COMMA=29
    INT=30
    ID=31
    COLON=32
    COMMENT=33
    NEWLINE=34
    WS=35
    FREE_TEXT=36
    NOTE_HDR_WS=37
    NOTE_BODY_WS=38
    CSS_READY_WS=39
    CSS_VALUE_START=40
    CSS_WS=41

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
            return self.getTypedRuleContext(MermaidStateDiagramParser.DiagramTypeContext,0)


        def EOF(self):
            return self.getToken(MermaidStateDiagramParser.EOF, 0)

        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidStateDiagramParser.NEWLINE)
            else:
                return self.getToken(MermaidStateDiagramParser.NEWLINE, i)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MermaidStateDiagramParser.StatementContext)
            else:
                return self.getTypedRuleContext(MermaidStateDiagramParser.StatementContext,i)


        def getRuleIndex(self):
            return MermaidStateDiagramParser.RULE_diagram

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDiagram" ):
                return visitor.visitDiagram(self)
            else:
                return visitor.visitChildren(self)




    def diagram(self):

        localctx = MermaidStateDiagramParser.DiagramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_diagram)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 49
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==34:
                self.state = 46
                self.match(MermaidStateDiagramParser.NEWLINE)
                self.state = 51
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 52
            self.diagramType()
            self.state = 56
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,1,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 53
                    self.match(MermaidStateDiagramParser.NEWLINE) 
                self.state = 58
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,1,self._ctx)

            self.state = 62
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 27919647208) != 0):
                self.state = 59
                self.statement()
                self.state = 64
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 65
            self.match(MermaidStateDiagramParser.EOF)
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

        def KW_STATE_DIAGRAM_V2(self):
            return self.getToken(MermaidStateDiagramParser.KW_STATE_DIAGRAM_V2, 0)

        def KW_STATE_DIAGRAM(self):
            return self.getToken(MermaidStateDiagramParser.KW_STATE_DIAGRAM, 0)

        def getRuleIndex(self):
            return MermaidStateDiagramParser.RULE_diagramType

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDiagramType" ):
                return visitor.visitDiagramType(self)
            else:
                return visitor.visitChildren(self)




    def diagramType(self):

        localctx = MermaidStateDiagramParser.DiagramTypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_diagramType)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 67
            _la = self._input.LA(1)
            if not(_la==1 or _la==2):
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

        def stateDecl(self):
            return self.getTypedRuleContext(MermaidStateDiagramParser.StateDeclContext,0)


        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidStateDiagramParser.NEWLINE)
            else:
                return self.getToken(MermaidStateDiagramParser.NEWLINE, i)

        def transitionStmt(self):
            return self.getTypedRuleContext(MermaidStateDiagramParser.TransitionStmtContext,0)


        def compositeBlock(self):
            return self.getTypedRuleContext(MermaidStateDiagramParser.CompositeBlockContext,0)


        def noteBlock(self):
            return self.getTypedRuleContext(MermaidStateDiagramParser.NoteBlockContext,0)


        def concurrencyDiv(self):
            return self.getTypedRuleContext(MermaidStateDiagramParser.ConcurrencyDivContext,0)


        def directionStmt(self):
            return self.getTypedRuleContext(MermaidStateDiagramParser.DirectionStmtContext,0)


        def classDefStmt(self):
            return self.getTypedRuleContext(MermaidStateDiagramParser.ClassDefStmtContext,0)


        def classAssignStmt(self):
            return self.getTypedRuleContext(MermaidStateDiagramParser.ClassAssignStmtContext,0)


        def COMMENT(self):
            return self.getToken(MermaidStateDiagramParser.COMMENT, 0)

        def getRuleIndex(self):
            return MermaidStateDiagramParser.RULE_statement

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStatement" ):
                return visitor.visitStatement(self)
            else:
                return visitor.visitChildren(self)




    def statement(self):

        localctx = MermaidStateDiagramParser.StatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_statement)
        try:
            self.state = 125
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,11,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 69
                self.stateDecl()
                self.state = 73
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,3,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 70
                        self.match(MermaidStateDiagramParser.NEWLINE) 
                    self.state = 75
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,3,self._ctx)

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 76
                self.transitionStmt()
                self.state = 80
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,4,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 77
                        self.match(MermaidStateDiagramParser.NEWLINE) 
                    self.state = 82
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,4,self._ctx)

                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 83
                self.compositeBlock()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 84
                self.noteBlock()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 85
                self.concurrencyDiv()
                self.state = 89
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,5,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 86
                        self.match(MermaidStateDiagramParser.NEWLINE) 
                    self.state = 91
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,5,self._ctx)

                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 92
                self.directionStmt()
                self.state = 96
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,6,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 93
                        self.match(MermaidStateDiagramParser.NEWLINE) 
                    self.state = 98
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,6,self._ctx)

                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 99
                self.classDefStmt()
                self.state = 103
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,7,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 100
                        self.match(MermaidStateDiagramParser.NEWLINE) 
                    self.state = 105
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,7,self._ctx)

                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 106
                self.classAssignStmt()
                self.state = 110
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,8,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 107
                        self.match(MermaidStateDiagramParser.NEWLINE) 
                    self.state = 112
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,8,self._ctx)

                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 113
                self.match(MermaidStateDiagramParser.COMMENT)
                self.state = 117
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,9,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 114
                        self.match(MermaidStateDiagramParser.NEWLINE) 
                    self.state = 119
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,9,self._ctx)

                pass

            elif la_ == 10:
                self.enterOuterAlt(localctx, 10)
                self.state = 121 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 120
                        self.match(MermaidStateDiagramParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 123 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,10,self._ctx)

                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StateDeclContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KW_STATE(self):
            return self.getToken(MermaidStateDiagramParser.KW_STATE, 0)

        def QUOTED_STRING(self):
            return self.getToken(MermaidStateDiagramParser.QUOTED_STRING, 0)

        def KW_AS(self):
            return self.getToken(MermaidStateDiagramParser.KW_AS, 0)

        def stateId(self):
            return self.getTypedRuleContext(MermaidStateDiagramParser.StateIdContext,0)


        def classShorthand(self):
            return self.getTypedRuleContext(MermaidStateDiagramParser.ClassShorthandContext,0)


        def COLON(self):
            return self.getToken(MermaidStateDiagramParser.COLON, 0)

        def descriptionText(self):
            return self.getTypedRuleContext(MermaidStateDiagramParser.DescriptionTextContext,0)


        def STEREOTYPE(self):
            return self.getToken(MermaidStateDiagramParser.STEREOTYPE, 0)

        def getRuleIndex(self):
            return MermaidStateDiagramParser.RULE_stateDecl

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStateDecl" ):
                return visitor.visitStateDecl(self)
            else:
                return visitor.visitChildren(self)




    def stateDecl(self):

        localctx = MermaidStateDiagramParser.StateDeclContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_stateDecl)
        self._la = 0 # Token type
        try:
            self.state = 153
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,15,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 127
                self.match(MermaidStateDiagramParser.KW_STATE)
                self.state = 128
                self.match(MermaidStateDiagramParser.QUOTED_STRING)
                self.state = 129
                self.match(MermaidStateDiagramParser.KW_AS)
                self.state = 130
                self.stateId()
                self.state = 132
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==23:
                    self.state = 131
                    self.classShorthand()


                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 134
                self.match(MermaidStateDiagramParser.KW_STATE)
                self.state = 135
                self.stateId()
                self.state = 136
                self.match(MermaidStateDiagramParser.COLON)
                self.state = 137
                self.descriptionText()
                self.state = 139
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==23:
                    self.state = 138
                    self.classShorthand()


                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 141
                self.match(MermaidStateDiagramParser.KW_STATE)
                self.state = 142
                self.stateId()
                self.state = 143
                self.match(MermaidStateDiagramParser.STEREOTYPE)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 145
                self.stateId()
                self.state = 146
                self.match(MermaidStateDiagramParser.COLON)
                self.state = 147
                self.descriptionText()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 149
                self.stateId()
                self.state = 151
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==23:
                    self.state = 150
                    self.classShorthand()


                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StateIdContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(MermaidStateDiagramParser.ID, 0)

        def getRuleIndex(self):
            return MermaidStateDiagramParser.RULE_stateId

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStateId" ):
                return visitor.visitStateId(self)
            else:
                return visitor.visitChildren(self)




    def stateId(self):

        localctx = MermaidStateDiagramParser.StateIdContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_stateId)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 155
            self.match(MermaidStateDiagramParser.ID)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DescriptionTextContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FREE_TEXT(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidStateDiagramParser.FREE_TEXT)
            else:
                return self.getToken(MermaidStateDiagramParser.FREE_TEXT, i)

        def getRuleIndex(self):
            return MermaidStateDiagramParser.RULE_descriptionText

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDescriptionText" ):
                return visitor.visitDescriptionText(self)
            else:
                return visitor.visitChildren(self)




    def descriptionText(self):

        localctx = MermaidStateDiagramParser.DescriptionTextContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_descriptionText)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 158 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 157
                self.match(MermaidStateDiagramParser.FREE_TEXT)
                self.state = 160 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==36):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ClassShorthandContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TRIPLE_COLON(self):
            return self.getToken(MermaidStateDiagramParser.TRIPLE_COLON, 0)

        def ID(self):
            return self.getToken(MermaidStateDiagramParser.ID, 0)

        def getRuleIndex(self):
            return MermaidStateDiagramParser.RULE_classShorthand

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitClassShorthand" ):
                return visitor.visitClassShorthand(self)
            else:
                return visitor.visitChildren(self)




    def classShorthand(self):

        localctx = MermaidStateDiagramParser.ClassShorthandContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_classShorthand)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 162
            self.match(MermaidStateDiagramParser.TRIPLE_COLON)
            self.state = 163
            self.match(MermaidStateDiagramParser.ID)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TransitionStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def stateRef(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MermaidStateDiagramParser.StateRefContext)
            else:
                return self.getTypedRuleContext(MermaidStateDiagramParser.StateRefContext,i)


        def TRANSITION(self):
            return self.getToken(MermaidStateDiagramParser.TRANSITION, 0)

        def COLON(self):
            return self.getToken(MermaidStateDiagramParser.COLON, 0)

        def transitionLabel(self):
            return self.getTypedRuleContext(MermaidStateDiagramParser.TransitionLabelContext,0)


        def getRuleIndex(self):
            return MermaidStateDiagramParser.RULE_transitionStmt

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTransitionStmt" ):
                return visitor.visitTransitionStmt(self)
            else:
                return visitor.visitChildren(self)




    def transitionStmt(self):

        localctx = MermaidStateDiagramParser.TransitionStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_transitionStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 165
            self.stateRef()
            self.state = 166
            self.match(MermaidStateDiagramParser.TRANSITION)
            self.state = 167
            self.stateRef()
            self.state = 170
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==32:
                self.state = 168
                self.match(MermaidStateDiagramParser.COLON)
                self.state = 169
                self.transitionLabel()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StateRefContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def stateId(self):
            return self.getTypedRuleContext(MermaidStateDiagramParser.StateIdContext,0)


        def classShorthand(self):
            return self.getTypedRuleContext(MermaidStateDiagramParser.ClassShorthandContext,0)


        def START_END(self):
            return self.getToken(MermaidStateDiagramParser.START_END, 0)

        def getRuleIndex(self):
            return MermaidStateDiagramParser.RULE_stateRef

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStateRef" ):
                return visitor.visitStateRef(self)
            else:
                return visitor.visitChildren(self)




    def stateRef(self):

        localctx = MermaidStateDiagramParser.StateRefContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_stateRef)
        self._la = 0 # Token type
        try:
            self.state = 180
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [31]:
                self.enterOuterAlt(localctx, 1)
                self.state = 172
                self.stateId()
                self.state = 174
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==23:
                    self.state = 173
                    self.classShorthand()


                pass
            elif token in [18]:
                self.enterOuterAlt(localctx, 2)
                self.state = 176
                self.match(MermaidStateDiagramParser.START_END)
                self.state = 178
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==23:
                    self.state = 177
                    self.classShorthand()


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


    class TransitionLabelContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FREE_TEXT(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidStateDiagramParser.FREE_TEXT)
            else:
                return self.getToken(MermaidStateDiagramParser.FREE_TEXT, i)

        def getRuleIndex(self):
            return MermaidStateDiagramParser.RULE_transitionLabel

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTransitionLabel" ):
                return visitor.visitTransitionLabel(self)
            else:
                return visitor.visitChildren(self)




    def transitionLabel(self):

        localctx = MermaidStateDiagramParser.TransitionLabelContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_transitionLabel)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 183 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 182
                self.match(MermaidStateDiagramParser.FREE_TEXT)
                self.state = 185 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==36):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CompositeBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KW_STATE(self):
            return self.getToken(MermaidStateDiagramParser.KW_STATE, 0)

        def QUOTED_STRING(self):
            return self.getToken(MermaidStateDiagramParser.QUOTED_STRING, 0)

        def KW_AS(self):
            return self.getToken(MermaidStateDiagramParser.KW_AS, 0)

        def stateId(self):
            return self.getTypedRuleContext(MermaidStateDiagramParser.StateIdContext,0)


        def LBRACE(self):
            return self.getToken(MermaidStateDiagramParser.LBRACE, 0)

        def RBRACE(self):
            return self.getToken(MermaidStateDiagramParser.RBRACE, 0)

        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidStateDiagramParser.NEWLINE)
            else:
                return self.getToken(MermaidStateDiagramParser.NEWLINE, i)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MermaidStateDiagramParser.StatementContext)
            else:
                return self.getTypedRuleContext(MermaidStateDiagramParser.StatementContext,i)


        def getRuleIndex(self):
            return MermaidStateDiagramParser.RULE_compositeBlock

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCompositeBlock" ):
                return visitor.visitCompositeBlock(self)
            else:
                return visitor.visitChildren(self)




    def compositeBlock(self):

        localctx = MermaidStateDiagramParser.CompositeBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_compositeBlock)
        self._la = 0 # Token type
        try:
            self.state = 229
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,28,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 187
                self.match(MermaidStateDiagramParser.KW_STATE)
                self.state = 188
                self.match(MermaidStateDiagramParser.QUOTED_STRING)
                self.state = 189
                self.match(MermaidStateDiagramParser.KW_AS)
                self.state = 190
                self.stateId()
                self.state = 191
                self.match(MermaidStateDiagramParser.LBRACE)
                self.state = 193 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 192
                        self.match(MermaidStateDiagramParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 195 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,22,self._ctx)

                self.state = 200
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while (((_la) & ~0x3f) == 0 and ((1 << _la) & 27919647208) != 0):
                    self.state = 197
                    self.statement()
                    self.state = 202
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 203
                self.match(MermaidStateDiagramParser.RBRACE)
                self.state = 205 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 204
                        self.match(MermaidStateDiagramParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 207 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,24,self._ctx)

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 209
                self.match(MermaidStateDiagramParser.KW_STATE)
                self.state = 210
                self.stateId()
                self.state = 211
                self.match(MermaidStateDiagramParser.LBRACE)
                self.state = 213 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 212
                        self.match(MermaidStateDiagramParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 215 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,25,self._ctx)

                self.state = 220
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while (((_la) & ~0x3f) == 0 and ((1 << _la) & 27919647208) != 0):
                    self.state = 217
                    self.statement()
                    self.state = 222
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 223
                self.match(MermaidStateDiagramParser.RBRACE)
                self.state = 225 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 224
                        self.match(MermaidStateDiagramParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 227 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,27,self._ctx)

                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConcurrencyDivContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CONCURRENCY(self):
            return self.getToken(MermaidStateDiagramParser.CONCURRENCY, 0)

        def getRuleIndex(self):
            return MermaidStateDiagramParser.RULE_concurrencyDiv

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConcurrencyDiv" ):
                return visitor.visitConcurrencyDiv(self)
            else:
                return visitor.visitChildren(self)




    def concurrencyDiv(self):

        localctx = MermaidStateDiagramParser.ConcurrencyDivContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_concurrencyDiv)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 231
            self.match(MermaidStateDiagramParser.CONCURRENCY)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NoteBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KW_NOTE(self):
            return self.getToken(MermaidStateDiagramParser.KW_NOTE, 0)

        def noteSide(self):
            return self.getTypedRuleContext(MermaidStateDiagramParser.NoteSideContext,0)


        def KW_OF(self):
            return self.getToken(MermaidStateDiagramParser.KW_OF, 0)

        def stateId(self):
            return self.getTypedRuleContext(MermaidStateDiagramParser.StateIdContext,0)


        def COLON(self):
            return self.getToken(MermaidStateDiagramParser.COLON, 0)

        def noteLineContent(self):
            return self.getTypedRuleContext(MermaidStateDiagramParser.NoteLineContentContext,0)


        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidStateDiagramParser.NEWLINE)
            else:
                return self.getToken(MermaidStateDiagramParser.NEWLINE, i)

        def KW_END_NOTE(self):
            return self.getToken(MermaidStateDiagramParser.KW_END_NOTE, 0)

        def noteBodyLine(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MermaidStateDiagramParser.NoteBodyLineContext)
            else:
                return self.getTypedRuleContext(MermaidStateDiagramParser.NoteBodyLineContext,i)


        def getRuleIndex(self):
            return MermaidStateDiagramParser.RULE_noteBlock

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNoteBlock" ):
                return visitor.visitNoteBlock(self)
            else:
                return visitor.visitChildren(self)




    def noteBlock(self):

        localctx = MermaidStateDiagramParser.NoteBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_noteBlock)
        self._la = 0 # Token type
        try:
            self.state = 262
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,32,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 233
                self.match(MermaidStateDiagramParser.KW_NOTE)
                self.state = 234
                self.noteSide()
                self.state = 235
                self.match(MermaidStateDiagramParser.KW_OF)
                self.state = 236
                self.stateId()
                self.state = 237
                self.match(MermaidStateDiagramParser.COLON)
                self.state = 238
                self.noteLineContent()
                self.state = 242
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,29,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 239
                        self.match(MermaidStateDiagramParser.NEWLINE) 
                    self.state = 244
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,29,self._ctx)

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 245
                self.match(MermaidStateDiagramParser.KW_NOTE)
                self.state = 246
                self.noteSide()
                self.state = 247
                self.match(MermaidStateDiagramParser.KW_OF)
                self.state = 248
                self.stateId()
                self.state = 249
                self.match(MermaidStateDiagramParser.NEWLINE)
                self.state = 251 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 250
                    self.noteBodyLine()
                    self.state = 253 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==34 or _la==36):
                        break

                self.state = 255
                self.match(MermaidStateDiagramParser.KW_END_NOTE)
                self.state = 259
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,31,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 256
                        self.match(MermaidStateDiagramParser.NEWLINE) 
                    self.state = 261
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,31,self._ctx)

                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NoteSideContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KW_RIGHT(self):
            return self.getToken(MermaidStateDiagramParser.KW_RIGHT, 0)

        def KW_LEFT(self):
            return self.getToken(MermaidStateDiagramParser.KW_LEFT, 0)

        def getRuleIndex(self):
            return MermaidStateDiagramParser.RULE_noteSide

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNoteSide" ):
                return visitor.visitNoteSide(self)
            else:
                return visitor.visitChildren(self)




    def noteSide(self):

        localctx = MermaidStateDiagramParser.NoteSideContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_noteSide)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 264
            _la = self._input.LA(1)
            if not(_la==10 or _la==11):
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


    class NoteLineContentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FREE_TEXT(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidStateDiagramParser.FREE_TEXT)
            else:
                return self.getToken(MermaidStateDiagramParser.FREE_TEXT, i)

        def getRuleIndex(self):
            return MermaidStateDiagramParser.RULE_noteLineContent

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNoteLineContent" ):
                return visitor.visitNoteLineContent(self)
            else:
                return visitor.visitChildren(self)




    def noteLineContent(self):

        localctx = MermaidStateDiagramParser.NoteLineContentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_noteLineContent)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 267 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 266
                self.match(MermaidStateDiagramParser.FREE_TEXT)
                self.state = 269 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==36):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NoteBodyLineContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FREE_TEXT(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidStateDiagramParser.FREE_TEXT)
            else:
                return self.getToken(MermaidStateDiagramParser.FREE_TEXT, i)

        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidStateDiagramParser.NEWLINE)
            else:
                return self.getToken(MermaidStateDiagramParser.NEWLINE, i)

        def getRuleIndex(self):
            return MermaidStateDiagramParser.RULE_noteBodyLine

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNoteBodyLine" ):
                return visitor.visitNoteBodyLine(self)
            else:
                return visitor.visitChildren(self)




    def noteBodyLine(self):

        localctx = MermaidStateDiagramParser.NoteBodyLineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_noteBodyLine)
        self._la = 0 # Token type
        try:
            self.state = 286
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [36]:
                self.enterOuterAlt(localctx, 1)
                self.state = 272 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 271
                    self.match(MermaidStateDiagramParser.FREE_TEXT)
                    self.state = 274 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==36):
                        break

                self.state = 277 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 276
                        self.match(MermaidStateDiagramParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 279 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,35,self._ctx)

                pass
            elif token in [34]:
                self.enterOuterAlt(localctx, 2)
                self.state = 282 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 281
                        self.match(MermaidStateDiagramParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 284 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,36,self._ctx)

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


    class DirectionStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KW_DIRECTION(self):
            return self.getToken(MermaidStateDiagramParser.KW_DIRECTION, 0)

        def direction(self):
            return self.getTypedRuleContext(MermaidStateDiagramParser.DirectionContext,0)


        def getRuleIndex(self):
            return MermaidStateDiagramParser.RULE_directionStmt

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDirectionStmt" ):
                return visitor.visitDirectionStmt(self)
            else:
                return visitor.visitChildren(self)




    def directionStmt(self):

        localctx = MermaidStateDiagramParser.DirectionStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_directionStmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 288
            self.match(MermaidStateDiagramParser.KW_DIRECTION)
            self.state = 289
            self.direction()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DirectionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DIR_TB(self):
            return self.getToken(MermaidStateDiagramParser.DIR_TB, 0)

        def DIR_TD(self):
            return self.getToken(MermaidStateDiagramParser.DIR_TD, 0)

        def DIR_BT(self):
            return self.getToken(MermaidStateDiagramParser.DIR_BT, 0)

        def DIR_LR(self):
            return self.getToken(MermaidStateDiagramParser.DIR_LR, 0)

        def DIR_RL(self):
            return self.getToken(MermaidStateDiagramParser.DIR_RL, 0)

        def getRuleIndex(self):
            return MermaidStateDiagramParser.RULE_direction

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDirection" ):
                return visitor.visitDirection(self)
            else:
                return visitor.visitChildren(self)




    def direction(self):

        localctx = MermaidStateDiagramParser.DirectionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_direction)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 291
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 253952) != 0)):
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


    class ClassDefStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KW_CLASSDEF(self):
            return self.getToken(MermaidStateDiagramParser.KW_CLASSDEF, 0)

        def classNameList(self):
            return self.getTypedRuleContext(MermaidStateDiagramParser.ClassNameListContext,0)


        def cssString(self):
            return self.getTypedRuleContext(MermaidStateDiagramParser.CssStringContext,0)


        def getRuleIndex(self):
            return MermaidStateDiagramParser.RULE_classDefStmt

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitClassDefStmt" ):
                return visitor.visitClassDefStmt(self)
            else:
                return visitor.visitChildren(self)




    def classDefStmt(self):

        localctx = MermaidStateDiagramParser.ClassDefStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_classDefStmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 293
            self.match(MermaidStateDiagramParser.KW_CLASSDEF)
            self.state = 294
            self.classNameList()
            self.state = 295
            self.cssString()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ClassNameListContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidStateDiagramParser.ID)
            else:
                return self.getToken(MermaidStateDiagramParser.ID, i)

        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidStateDiagramParser.COMMA)
            else:
                return self.getToken(MermaidStateDiagramParser.COMMA, i)

        def getRuleIndex(self):
            return MermaidStateDiagramParser.RULE_classNameList

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitClassNameList" ):
                return visitor.visitClassNameList(self)
            else:
                return visitor.visitChildren(self)




    def classNameList(self):

        localctx = MermaidStateDiagramParser.ClassNameListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_classNameList)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 297
            self.match(MermaidStateDiagramParser.ID)
            self.state = 302
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==29:
                self.state = 298
                self.match(MermaidStateDiagramParser.COMMA)
                self.state = 299
                self.match(MermaidStateDiagramParser.ID)
                self.state = 304
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ClassAssignStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KW_CLASS(self):
            return self.getToken(MermaidStateDiagramParser.KW_CLASS, 0)

        def stateIdList(self):
            return self.getTypedRuleContext(MermaidStateDiagramParser.StateIdListContext,0)


        def ID(self):
            return self.getToken(MermaidStateDiagramParser.ID, 0)

        def getRuleIndex(self):
            return MermaidStateDiagramParser.RULE_classAssignStmt

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitClassAssignStmt" ):
                return visitor.visitClassAssignStmt(self)
            else:
                return visitor.visitChildren(self)




    def classAssignStmt(self):

        localctx = MermaidStateDiagramParser.ClassAssignStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_classAssignStmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 305
            self.match(MermaidStateDiagramParser.KW_CLASS)
            self.state = 306
            self.stateIdList()
            self.state = 307
            self.match(MermaidStateDiagramParser.ID)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StateIdListContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidStateDiagramParser.ID)
            else:
                return self.getToken(MermaidStateDiagramParser.ID, i)

        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidStateDiagramParser.COMMA)
            else:
                return self.getToken(MermaidStateDiagramParser.COMMA, i)

        def getRuleIndex(self):
            return MermaidStateDiagramParser.RULE_stateIdList

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStateIdList" ):
                return visitor.visitStateIdList(self)
            else:
                return visitor.visitChildren(self)




    def stateIdList(self):

        localctx = MermaidStateDiagramParser.StateIdListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_stateIdList)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 309
            self.match(MermaidStateDiagramParser.ID)
            self.state = 314
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==29:
                self.state = 310
                self.match(MermaidStateDiagramParser.COMMA)
                self.state = 311
                self.match(MermaidStateDiagramParser.ID)
                self.state = 316
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CssStringContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CSS_VALUE_START(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidStateDiagramParser.CSS_VALUE_START)
            else:
                return self.getToken(MermaidStateDiagramParser.CSS_VALUE_START, i)

        def SEMI(self):
            return self.getToken(MermaidStateDiagramParser.SEMI, 0)

        def getRuleIndex(self):
            return MermaidStateDiagramParser.RULE_cssString

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCssString" ):
                return visitor.visitCssString(self)
            else:
                return visitor.visitChildren(self)




    def cssString(self):

        localctx = MermaidStateDiagramParser.CssStringContext(self, self._ctx, self.state)
        self.enterRule(localctx, 44, self.RULE_cssString)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 318 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 317
                self.match(MermaidStateDiagramParser.CSS_VALUE_START)
                self.state = 320 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==40):
                    break

            self.state = 323
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==28:
                self.state = 322
                self.match(MermaidStateDiagramParser.SEMI)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





