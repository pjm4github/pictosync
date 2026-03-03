# Generated from C:\Users\pmora\OneDrive\Documents\Git\GitHub\pictosync\mermaid\grammar\MermaidSequenceParser.g4 by ANTLR 4.13.0
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
        4,1,56,547,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,
        7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,26,7,26,
        2,27,7,27,2,28,7,28,2,29,7,29,2,30,7,30,2,31,7,31,2,32,7,32,2,33,
        7,33,2,34,7,34,2,35,7,35,2,36,7,36,2,37,7,37,2,38,7,38,2,39,7,39,
        2,40,7,40,2,41,7,41,2,42,7,42,1,0,5,0,88,8,0,10,0,12,0,91,9,0,1,
        0,1,0,4,0,95,8,0,11,0,12,0,96,1,0,5,0,100,8,0,10,0,12,0,103,9,0,
        1,0,1,0,1,1,1,1,4,1,109,8,1,11,1,12,1,110,1,1,1,1,4,1,115,8,1,11,
        1,12,1,116,1,1,1,1,1,1,4,1,122,8,1,11,1,12,1,123,1,1,1,1,4,1,128,
        8,1,11,1,12,1,129,1,1,1,1,4,1,134,8,1,11,1,12,1,135,1,1,1,1,4,1,
        140,8,1,11,1,12,1,141,1,1,1,1,4,1,146,8,1,11,1,12,1,147,1,1,1,1,
        4,1,152,8,1,11,1,12,1,153,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,4,
        1,165,8,1,11,1,12,1,166,1,1,1,1,4,1,171,8,1,11,1,12,1,172,1,1,1,
        1,4,1,177,8,1,11,1,12,1,178,1,1,1,1,4,1,183,8,1,11,1,12,1,184,1,
        1,4,1,188,8,1,11,1,12,1,189,3,1,192,8,1,1,2,1,2,1,2,1,2,3,2,198,
        8,2,1,3,1,3,1,4,1,4,1,4,1,4,3,4,206,8,4,1,5,1,5,1,6,1,6,1,7,1,7,
        3,7,214,8,7,1,7,3,7,217,8,7,1,7,4,7,220,8,7,11,7,12,7,221,1,7,5,
        7,225,8,7,10,7,12,7,228,9,7,1,7,1,7,4,7,232,8,7,11,7,12,7,233,1,
        8,1,8,1,9,1,9,1,10,1,10,1,10,1,10,1,10,3,10,245,8,10,1,11,1,11,1,
        11,1,12,1,12,1,12,1,12,1,12,1,12,1,13,3,13,257,8,13,1,13,1,13,3,
        13,261,8,13,1,14,3,14,264,8,14,1,14,1,14,3,14,268,8,14,1,15,3,15,
        271,8,15,1,16,1,16,1,16,1,17,1,17,1,17,1,18,1,18,1,18,1,18,1,18,
        3,18,284,8,18,1,18,1,18,1,18,1,19,1,19,1,20,3,20,292,8,20,1,21,1,
        21,1,21,4,21,297,8,21,11,21,12,21,298,1,21,5,21,302,8,21,10,21,12,
        21,305,9,21,1,21,1,21,4,21,309,8,21,11,21,12,21,310,1,22,3,22,314,
        8,22,1,23,1,23,1,23,4,23,319,8,23,11,23,12,23,320,1,23,5,23,324,
        8,23,10,23,12,23,327,9,23,1,23,1,23,1,23,4,23,332,8,23,11,23,12,
        23,333,1,23,5,23,337,8,23,10,23,12,23,340,9,23,5,23,342,8,23,10,
        23,12,23,345,9,23,1,23,1,23,4,23,349,8,23,11,23,12,23,350,1,24,1,
        24,1,24,4,24,356,8,24,11,24,12,24,357,1,24,5,24,361,8,24,10,24,12,
        24,364,9,24,1,24,1,24,4,24,368,8,24,11,24,12,24,369,1,25,3,25,373,
        8,25,1,26,3,26,376,8,26,1,27,1,27,1,27,4,27,381,8,27,11,27,12,27,
        382,1,27,5,27,386,8,27,10,27,12,27,389,9,27,1,27,1,27,1,27,4,27,
        394,8,27,11,27,12,27,395,1,27,5,27,399,8,27,10,27,12,27,402,9,27,
        5,27,404,8,27,10,27,12,27,407,9,27,1,27,1,27,4,27,411,8,27,11,27,
        12,27,412,1,28,3,28,416,8,28,1,29,1,29,1,29,4,29,421,8,29,11,29,
        12,29,422,1,29,5,29,426,8,29,10,29,12,29,429,9,29,1,29,1,29,1,29,
        4,29,434,8,29,11,29,12,29,435,1,29,5,29,439,8,29,10,29,12,29,442,
        9,29,5,29,444,8,29,10,29,12,29,447,9,29,1,29,1,29,4,29,451,8,29,
        11,29,12,29,452,1,30,3,30,456,8,30,1,31,3,31,459,8,31,1,32,1,32,
        1,32,4,32,464,8,32,11,32,12,32,465,1,32,5,32,469,8,32,10,32,12,32,
        472,9,32,1,32,1,32,4,32,476,8,32,11,32,12,32,477,1,33,3,33,481,8,
        33,1,34,1,34,1,34,4,34,486,8,34,11,34,12,34,487,1,34,5,34,491,8,
        34,10,34,12,34,494,9,34,1,34,1,34,4,34,498,8,34,11,34,12,34,499,
        1,35,1,35,1,36,1,36,1,36,1,36,3,36,508,8,36,3,36,510,8,36,3,36,512,
        8,36,1,37,1,37,1,37,1,37,1,37,1,37,1,37,1,38,1,38,1,38,1,38,1,38,
        1,39,3,39,527,8,39,1,40,3,40,530,8,40,1,41,1,41,1,41,1,41,5,41,536,
        8,41,10,41,12,41,539,9,41,1,41,1,41,1,42,1,42,1,42,1,42,1,42,0,0,
        43,0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,
        44,46,48,50,52,54,56,58,60,62,64,66,68,70,72,74,76,78,80,82,84,0,
        5,1,0,2,9,1,0,45,46,2,0,45,45,54,54,2,0,34,34,47,49,2,0,10,11,20,
        20,597,0,89,1,0,0,0,2,191,1,0,0,0,4,193,1,0,0,0,6,199,1,0,0,0,8,
        201,1,0,0,0,10,207,1,0,0,0,12,209,1,0,0,0,14,211,1,0,0,0,16,235,
        1,0,0,0,18,237,1,0,0,0,20,239,1,0,0,0,22,246,1,0,0,0,24,249,1,0,
        0,0,26,256,1,0,0,0,28,263,1,0,0,0,30,270,1,0,0,0,32,272,1,0,0,0,
        34,275,1,0,0,0,36,278,1,0,0,0,38,288,1,0,0,0,40,291,1,0,0,0,42,293,
        1,0,0,0,44,313,1,0,0,0,46,315,1,0,0,0,48,352,1,0,0,0,50,372,1,0,
        0,0,52,375,1,0,0,0,54,377,1,0,0,0,56,415,1,0,0,0,58,417,1,0,0,0,
        60,455,1,0,0,0,62,458,1,0,0,0,64,460,1,0,0,0,66,480,1,0,0,0,68,482,
        1,0,0,0,70,501,1,0,0,0,72,503,1,0,0,0,74,513,1,0,0,0,76,520,1,0,
        0,0,78,526,1,0,0,0,80,529,1,0,0,0,82,531,1,0,0,0,84,542,1,0,0,0,
        86,88,5,51,0,0,87,86,1,0,0,0,88,91,1,0,0,0,89,87,1,0,0,0,89,90,1,
        0,0,0,90,92,1,0,0,0,91,89,1,0,0,0,92,94,5,1,0,0,93,95,5,51,0,0,94,
        93,1,0,0,0,95,96,1,0,0,0,96,94,1,0,0,0,96,97,1,0,0,0,97,101,1,0,
        0,0,98,100,3,2,1,0,99,98,1,0,0,0,100,103,1,0,0,0,101,99,1,0,0,0,
        101,102,1,0,0,0,102,104,1,0,0,0,103,101,1,0,0,0,104,105,5,0,0,1,
        105,1,1,0,0,0,106,108,3,4,2,0,107,109,5,51,0,0,108,107,1,0,0,0,109,
        110,1,0,0,0,110,108,1,0,0,0,110,111,1,0,0,0,111,192,1,0,0,0,112,
        114,3,8,4,0,113,115,5,51,0,0,114,113,1,0,0,0,115,116,1,0,0,0,116,
        114,1,0,0,0,116,117,1,0,0,0,117,192,1,0,0,0,118,192,3,14,7,0,119,
        121,3,20,10,0,120,122,5,51,0,0,121,120,1,0,0,0,122,123,1,0,0,0,123,
        121,1,0,0,0,123,124,1,0,0,0,124,192,1,0,0,0,125,127,3,22,11,0,126,
        128,5,51,0,0,127,126,1,0,0,0,128,129,1,0,0,0,129,127,1,0,0,0,129,
        130,1,0,0,0,130,192,1,0,0,0,131,133,3,24,12,0,132,134,5,51,0,0,133,
        132,1,0,0,0,134,135,1,0,0,0,135,133,1,0,0,0,135,136,1,0,0,0,136,
        192,1,0,0,0,137,139,3,32,16,0,138,140,5,51,0,0,139,138,1,0,0,0,140,
        141,1,0,0,0,141,139,1,0,0,0,141,142,1,0,0,0,142,192,1,0,0,0,143,
        145,3,34,17,0,144,146,5,51,0,0,145,144,1,0,0,0,146,147,1,0,0,0,147,
        145,1,0,0,0,147,148,1,0,0,0,148,192,1,0,0,0,149,151,3,36,18,0,150,
        152,5,51,0,0,151,150,1,0,0,0,152,153,1,0,0,0,153,151,1,0,0,0,153,
        154,1,0,0,0,154,192,1,0,0,0,155,192,3,42,21,0,156,192,3,46,23,0,
        157,192,3,48,24,0,158,192,3,54,27,0,159,192,3,58,29,0,160,192,3,
        64,32,0,161,192,3,68,34,0,162,164,3,72,36,0,163,165,5,51,0,0,164,
        163,1,0,0,0,165,166,1,0,0,0,166,164,1,0,0,0,166,167,1,0,0,0,167,
        192,1,0,0,0,168,170,3,74,37,0,169,171,5,51,0,0,170,169,1,0,0,0,171,
        172,1,0,0,0,172,170,1,0,0,0,172,173,1,0,0,0,173,192,1,0,0,0,174,
        176,3,76,38,0,175,177,5,51,0,0,176,175,1,0,0,0,177,178,1,0,0,0,178,
        176,1,0,0,0,178,179,1,0,0,0,179,192,1,0,0,0,180,182,5,50,0,0,181,
        183,5,51,0,0,182,181,1,0,0,0,183,184,1,0,0,0,184,182,1,0,0,0,184,
        185,1,0,0,0,185,192,1,0,0,0,186,188,5,51,0,0,187,186,1,0,0,0,188,
        189,1,0,0,0,189,187,1,0,0,0,189,190,1,0,0,0,190,192,1,0,0,0,191,
        106,1,0,0,0,191,112,1,0,0,0,191,118,1,0,0,0,191,119,1,0,0,0,191,
        125,1,0,0,0,191,131,1,0,0,0,191,137,1,0,0,0,191,143,1,0,0,0,191,
        149,1,0,0,0,191,155,1,0,0,0,191,156,1,0,0,0,191,157,1,0,0,0,191,
        158,1,0,0,0,191,159,1,0,0,0,191,160,1,0,0,0,191,161,1,0,0,0,191,
        162,1,0,0,0,191,168,1,0,0,0,191,174,1,0,0,0,191,180,1,0,0,0,191,
        187,1,0,0,0,192,3,1,0,0,0,193,194,3,6,3,0,194,197,3,10,5,0,195,196,
        5,12,0,0,196,198,3,12,6,0,197,195,1,0,0,0,197,198,1,0,0,0,198,5,
        1,0,0,0,199,200,7,0,0,0,200,7,1,0,0,0,201,202,5,3,0,0,202,205,3,
        10,5,0,203,204,5,12,0,0,204,206,3,12,6,0,205,203,1,0,0,0,205,206,
        1,0,0,0,206,9,1,0,0,0,207,208,7,1,0,0,208,11,1,0,0,0,209,210,7,2,
        0,0,210,13,1,0,0,0,211,213,5,13,0,0,212,214,3,16,8,0,213,212,1,0,
        0,0,213,214,1,0,0,0,214,216,1,0,0,0,215,217,3,18,9,0,216,215,1,0,
        0,0,216,217,1,0,0,0,217,219,1,0,0,0,218,220,5,51,0,0,219,218,1,0,
        0,0,220,221,1,0,0,0,221,219,1,0,0,0,221,222,1,0,0,0,222,226,1,0,
        0,0,223,225,3,2,1,0,224,223,1,0,0,0,225,228,1,0,0,0,226,224,1,0,
        0,0,226,227,1,0,0,0,227,229,1,0,0,0,228,226,1,0,0,0,229,231,5,14,
        0,0,230,232,5,51,0,0,231,230,1,0,0,0,232,233,1,0,0,0,233,231,1,0,
        0,0,233,234,1,0,0,0,234,15,1,0,0,0,235,236,7,3,0,0,236,17,1,0,0,
        0,237,238,7,2,0,0,238,19,1,0,0,0,239,240,5,15,0,0,240,241,3,6,3,
        0,241,244,3,10,5,0,242,243,5,12,0,0,243,245,3,12,6,0,244,242,1,0,
        0,0,244,245,1,0,0,0,245,21,1,0,0,0,246,247,5,16,0,0,247,248,3,10,
        5,0,248,23,1,0,0,0,249,250,3,26,13,0,250,251,5,35,0,0,251,252,3,
        28,14,0,252,253,5,36,0,0,253,254,3,30,15,0,254,25,1,0,0,0,255,257,
        5,39,0,0,256,255,1,0,0,0,256,257,1,0,0,0,257,258,1,0,0,0,258,260,
        3,10,5,0,259,261,5,40,0,0,260,259,1,0,0,0,260,261,1,0,0,0,261,27,
        1,0,0,0,262,264,5,39,0,0,263,262,1,0,0,0,263,264,1,0,0,0,264,265,
        1,0,0,0,265,267,3,10,5,0,266,268,5,40,0,0,267,266,1,0,0,0,267,268,
        1,0,0,0,268,29,1,0,0,0,269,271,5,56,0,0,270,269,1,0,0,0,270,271,
        1,0,0,0,271,31,1,0,0,0,272,273,5,17,0,0,273,274,3,10,5,0,274,33,
        1,0,0,0,275,276,5,18,0,0,276,277,3,10,5,0,277,35,1,0,0,0,278,279,
        5,19,0,0,279,280,3,38,19,0,280,283,3,10,5,0,281,282,5,37,0,0,282,
        284,3,10,5,0,283,281,1,0,0,0,283,284,1,0,0,0,284,285,1,0,0,0,285,
        286,5,36,0,0,286,287,3,40,20,0,287,37,1,0,0,0,288,289,7,4,0,0,289,
        39,1,0,0,0,290,292,5,56,0,0,291,290,1,0,0,0,291,292,1,0,0,0,292,
        41,1,0,0,0,293,294,5,21,0,0,294,296,3,44,22,0,295,297,5,51,0,0,296,
        295,1,0,0,0,297,298,1,0,0,0,298,296,1,0,0,0,298,299,1,0,0,0,299,
        303,1,0,0,0,300,302,3,2,1,0,301,300,1,0,0,0,302,305,1,0,0,0,303,
        301,1,0,0,0,303,304,1,0,0,0,304,306,1,0,0,0,305,303,1,0,0,0,306,
        308,5,14,0,0,307,309,5,51,0,0,308,307,1,0,0,0,309,310,1,0,0,0,310,
        308,1,0,0,0,310,311,1,0,0,0,311,43,1,0,0,0,312,314,5,56,0,0,313,
        312,1,0,0,0,313,314,1,0,0,0,314,45,1,0,0,0,315,316,5,22,0,0,316,
        318,3,50,25,0,317,319,5,51,0,0,318,317,1,0,0,0,319,320,1,0,0,0,320,
        318,1,0,0,0,320,321,1,0,0,0,321,325,1,0,0,0,322,324,3,2,1,0,323,
        322,1,0,0,0,324,327,1,0,0,0,325,323,1,0,0,0,325,326,1,0,0,0,326,
        343,1,0,0,0,327,325,1,0,0,0,328,329,5,23,0,0,329,331,3,50,25,0,330,
        332,5,51,0,0,331,330,1,0,0,0,332,333,1,0,0,0,333,331,1,0,0,0,333,
        334,1,0,0,0,334,338,1,0,0,0,335,337,3,2,1,0,336,335,1,0,0,0,337,
        340,1,0,0,0,338,336,1,0,0,0,338,339,1,0,0,0,339,342,1,0,0,0,340,
        338,1,0,0,0,341,328,1,0,0,0,342,345,1,0,0,0,343,341,1,0,0,0,343,
        344,1,0,0,0,344,346,1,0,0,0,345,343,1,0,0,0,346,348,5,14,0,0,347,
        349,5,51,0,0,348,347,1,0,0,0,349,350,1,0,0,0,350,348,1,0,0,0,350,
        351,1,0,0,0,351,47,1,0,0,0,352,353,5,24,0,0,353,355,3,52,26,0,354,
        356,5,51,0,0,355,354,1,0,0,0,356,357,1,0,0,0,357,355,1,0,0,0,357,
        358,1,0,0,0,358,362,1,0,0,0,359,361,3,2,1,0,360,359,1,0,0,0,361,
        364,1,0,0,0,362,360,1,0,0,0,362,363,1,0,0,0,363,365,1,0,0,0,364,
        362,1,0,0,0,365,367,5,14,0,0,366,368,5,51,0,0,367,366,1,0,0,0,368,
        369,1,0,0,0,369,367,1,0,0,0,369,370,1,0,0,0,370,49,1,0,0,0,371,373,
        5,56,0,0,372,371,1,0,0,0,372,373,1,0,0,0,373,51,1,0,0,0,374,376,
        5,56,0,0,375,374,1,0,0,0,375,376,1,0,0,0,376,53,1,0,0,0,377,378,
        5,25,0,0,378,380,3,56,28,0,379,381,5,51,0,0,380,379,1,0,0,0,381,
        382,1,0,0,0,382,380,1,0,0,0,382,383,1,0,0,0,383,387,1,0,0,0,384,
        386,3,2,1,0,385,384,1,0,0,0,386,389,1,0,0,0,387,385,1,0,0,0,387,
        388,1,0,0,0,388,405,1,0,0,0,389,387,1,0,0,0,390,391,5,26,0,0,391,
        393,3,56,28,0,392,394,5,51,0,0,393,392,1,0,0,0,394,395,1,0,0,0,395,
        393,1,0,0,0,395,396,1,0,0,0,396,400,1,0,0,0,397,399,3,2,1,0,398,
        397,1,0,0,0,399,402,1,0,0,0,400,398,1,0,0,0,400,401,1,0,0,0,401,
        404,1,0,0,0,402,400,1,0,0,0,403,390,1,0,0,0,404,407,1,0,0,0,405,
        403,1,0,0,0,405,406,1,0,0,0,406,408,1,0,0,0,407,405,1,0,0,0,408,
        410,5,14,0,0,409,411,5,51,0,0,410,409,1,0,0,0,411,412,1,0,0,0,412,
        410,1,0,0,0,412,413,1,0,0,0,413,55,1,0,0,0,414,416,5,56,0,0,415,
        414,1,0,0,0,415,416,1,0,0,0,416,57,1,0,0,0,417,418,5,27,0,0,418,
        420,3,60,30,0,419,421,5,51,0,0,420,419,1,0,0,0,421,422,1,0,0,0,422,
        420,1,0,0,0,422,423,1,0,0,0,423,427,1,0,0,0,424,426,3,2,1,0,425,
        424,1,0,0,0,426,429,1,0,0,0,427,425,1,0,0,0,427,428,1,0,0,0,428,
        445,1,0,0,0,429,427,1,0,0,0,430,431,5,28,0,0,431,433,3,62,31,0,432,
        434,5,51,0,0,433,432,1,0,0,0,434,435,1,0,0,0,435,433,1,0,0,0,435,
        436,1,0,0,0,436,440,1,0,0,0,437,439,3,2,1,0,438,437,1,0,0,0,439,
        442,1,0,0,0,440,438,1,0,0,0,440,441,1,0,0,0,441,444,1,0,0,0,442,
        440,1,0,0,0,443,430,1,0,0,0,444,447,1,0,0,0,445,443,1,0,0,0,445,
        446,1,0,0,0,446,448,1,0,0,0,447,445,1,0,0,0,448,450,5,14,0,0,449,
        451,5,51,0,0,450,449,1,0,0,0,451,452,1,0,0,0,452,450,1,0,0,0,452,
        453,1,0,0,0,453,59,1,0,0,0,454,456,5,56,0,0,455,454,1,0,0,0,455,
        456,1,0,0,0,456,61,1,0,0,0,457,459,5,56,0,0,458,457,1,0,0,0,458,
        459,1,0,0,0,459,63,1,0,0,0,460,461,5,29,0,0,461,463,3,66,33,0,462,
        464,5,51,0,0,463,462,1,0,0,0,464,465,1,0,0,0,465,463,1,0,0,0,465,
        466,1,0,0,0,466,470,1,0,0,0,467,469,3,2,1,0,468,467,1,0,0,0,469,
        472,1,0,0,0,470,468,1,0,0,0,470,471,1,0,0,0,471,473,1,0,0,0,472,
        470,1,0,0,0,473,475,5,14,0,0,474,476,5,51,0,0,475,474,1,0,0,0,476,
        477,1,0,0,0,477,475,1,0,0,0,477,478,1,0,0,0,478,65,1,0,0,0,479,481,
        5,56,0,0,480,479,1,0,0,0,480,481,1,0,0,0,481,67,1,0,0,0,482,483,
        5,30,0,0,483,485,3,70,35,0,484,486,5,51,0,0,485,484,1,0,0,0,486,
        487,1,0,0,0,487,485,1,0,0,0,487,488,1,0,0,0,488,492,1,0,0,0,489,
        491,3,2,1,0,490,489,1,0,0,0,491,494,1,0,0,0,492,490,1,0,0,0,492,
        493,1,0,0,0,493,495,1,0,0,0,494,492,1,0,0,0,495,497,5,14,0,0,496,
        498,5,51,0,0,497,496,1,0,0,0,498,499,1,0,0,0,499,497,1,0,0,0,499,
        500,1,0,0,0,500,69,1,0,0,0,501,502,7,3,0,0,502,71,1,0,0,0,503,511,
        5,31,0,0,504,509,5,43,0,0,505,507,5,43,0,0,506,508,5,43,0,0,507,
        506,1,0,0,0,507,508,1,0,0,0,508,510,1,0,0,0,509,505,1,0,0,0,509,
        510,1,0,0,0,510,512,1,0,0,0,511,504,1,0,0,0,511,512,1,0,0,0,512,
        73,1,0,0,0,513,514,5,32,0,0,514,515,3,10,5,0,515,516,5,36,0,0,516,
        517,3,78,39,0,517,518,5,38,0,0,518,519,3,80,40,0,519,75,1,0,0,0,
        520,521,5,33,0,0,521,522,3,10,5,0,522,523,5,36,0,0,523,524,3,82,
        41,0,524,77,1,0,0,0,525,527,5,56,0,0,526,525,1,0,0,0,526,527,1,0,
        0,0,527,79,1,0,0,0,528,530,5,56,0,0,529,528,1,0,0,0,529,530,1,0,
        0,0,530,81,1,0,0,0,531,532,5,41,0,0,532,537,3,84,42,0,533,534,5,
        37,0,0,534,536,3,84,42,0,535,533,1,0,0,0,536,539,1,0,0,0,537,535,
        1,0,0,0,537,538,1,0,0,0,538,540,1,0,0,0,539,537,1,0,0,0,540,541,
        5,42,0,0,541,83,1,0,0,0,542,543,5,45,0,0,543,544,5,36,0,0,544,545,
        5,45,0,0,545,85,1,0,0,0,75,89,96,101,110,116,123,129,135,141,147,
        153,166,172,178,184,189,191,197,205,213,216,221,226,233,244,256,
        260,263,267,270,283,291,298,303,310,313,320,325,333,338,343,350,
        357,362,369,372,375,382,387,395,400,405,412,415,422,427,435,440,
        445,452,455,458,465,470,477,480,487,492,499,507,509,511,526,529,
        537
    ]

class MermaidSequenceParser ( Parser ):

    grammarFileName = "MermaidSequenceParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'sequenceDiagram'", "'participant'", 
                     "'actor'", "'boundary'", "'control'", "'entity'", "'database'", 
                     "'collections'", "'queue'", "'right of'", "'left of'", 
                     "'as'", "'box'", "'end'", "'create'", "'destroy'", 
                     "'activate'", "'deactivate'", "<INVALID>", "'over'", 
                     "'loop'", "'alt'", "'else'", "'opt'", "'par'", "'and'", 
                     "'critical'", "'option'", "'break'", "'rect'", "'autonumber'", 
                     "'link'", "'links'", "'transparent'", "<INVALID>", 
                     "':'", "','", "'@'", "'('", "')'", "'{'", "'}'" ]

    symbolicNames = [ "<INVALID>", "SEQUENCE_DIAGRAM", "PARTICIPANT", "ACTOR", 
                      "BOUNDARY", "CONTROL", "ENTITY", "DATABASE", "COLLECTIONS", 
                      "QUEUE", "RIGHT_OF", "LEFT_OF", "AS", "BOX", "END", 
                      "CREATE", "DESTROY", "ACTIVATE", "DEACTIVATE", "NOTE", 
                      "OVER", "LOOP", "ALT", "ELSE", "OPT", "PAR", "AND", 
                      "CRITICAL", "OPTION", "BREAK", "RECT", "AUTONUMBER", 
                      "LINK", "LINKS", "TRANSPARENT", "ARROW", "COLON", 
                      "COMMA", "AT", "LPAREN", "RPAREN", "LBRACE", "RBRACE", 
                      "INT", "FLOAT", "QUOTED_STRING", "ID", "RGB_COLOR", 
                      "RGBA_COLOR", "COLOR_NAME", "COMMENT", "NEWLINE", 
                      "WS", "LABEL_WS", "LABEL_REST", "TEXT_WS", "TEXT_REST" ]

    RULE_diagram = 0
    RULE_statement = 1
    RULE_participantDecl = 2
    RULE_participantType = 3
    RULE_actorDecl = 4
    RULE_participantId = 5
    RULE_label = 6
    RULE_boxBlock = 7
    RULE_boxColor = 8
    RULE_boxLabel = 9
    RULE_createDirective = 10
    RULE_destroyDirective = 11
    RULE_messageStatement = 12
    RULE_sender = 13
    RULE_receiver = 14
    RULE_messageText = 15
    RULE_activateStatement = 16
    RULE_deactivateStatement = 17
    RULE_noteStatement = 18
    RULE_notePosition = 19
    RULE_noteText = 20
    RULE_loopBlock = 21
    RULE_loopLabel = 22
    RULE_altBlock = 23
    RULE_optBlock = 24
    RULE_altCondition = 25
    RULE_optCondition = 26
    RULE_parBlock = 27
    RULE_parLabel = 28
    RULE_criticalBlock = 29
    RULE_criticalAction = 30
    RULE_optionCondition = 31
    RULE_breakBlock = 32
    RULE_breakCondition = 33
    RULE_rectBlock = 34
    RULE_rectColor = 35
    RULE_autonumberStatement = 36
    RULE_linkStatement = 37
    RULE_linksStatement = 38
    RULE_linkLabel = 39
    RULE_linkUrl = 40
    RULE_jsonObject = 41
    RULE_jsonPair = 42

    ruleNames =  [ "diagram", "statement", "participantDecl", "participantType", 
                   "actorDecl", "participantId", "label", "boxBlock", "boxColor", 
                   "boxLabel", "createDirective", "destroyDirective", "messageStatement", 
                   "sender", "receiver", "messageText", "activateStatement", 
                   "deactivateStatement", "noteStatement", "notePosition", 
                   "noteText", "loopBlock", "loopLabel", "altBlock", "optBlock", 
                   "altCondition", "optCondition", "parBlock", "parLabel", 
                   "criticalBlock", "criticalAction", "optionCondition", 
                   "breakBlock", "breakCondition", "rectBlock", "rectColor", 
                   "autonumberStatement", "linkStatement", "linksStatement", 
                   "linkLabel", "linkUrl", "jsonObject", "jsonPair" ]

    EOF = Token.EOF
    SEQUENCE_DIAGRAM=1
    PARTICIPANT=2
    ACTOR=3
    BOUNDARY=4
    CONTROL=5
    ENTITY=6
    DATABASE=7
    COLLECTIONS=8
    QUEUE=9
    RIGHT_OF=10
    LEFT_OF=11
    AS=12
    BOX=13
    END=14
    CREATE=15
    DESTROY=16
    ACTIVATE=17
    DEACTIVATE=18
    NOTE=19
    OVER=20
    LOOP=21
    ALT=22
    ELSE=23
    OPT=24
    PAR=25
    AND=26
    CRITICAL=27
    OPTION=28
    BREAK=29
    RECT=30
    AUTONUMBER=31
    LINK=32
    LINKS=33
    TRANSPARENT=34
    ARROW=35
    COLON=36
    COMMA=37
    AT=38
    LPAREN=39
    RPAREN=40
    LBRACE=41
    RBRACE=42
    INT=43
    FLOAT=44
    QUOTED_STRING=45
    ID=46
    RGB_COLOR=47
    RGBA_COLOR=48
    COLOR_NAME=49
    COMMENT=50
    NEWLINE=51
    WS=52
    LABEL_WS=53
    LABEL_REST=54
    TEXT_WS=55
    TEXT_REST=56

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

        def SEQUENCE_DIAGRAM(self):
            return self.getToken(MermaidSequenceParser.SEQUENCE_DIAGRAM, 0)

        def EOF(self):
            return self.getToken(MermaidSequenceParser.EOF, 0)

        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidSequenceParser.NEWLINE)
            else:
                return self.getToken(MermaidSequenceParser.NEWLINE, i)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MermaidSequenceParser.StatementContext)
            else:
                return self.getTypedRuleContext(MermaidSequenceParser.StatementContext,i)


        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_diagram

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDiagram" ):
                return visitor.visitDiagram(self)
            else:
                return visitor.visitChildren(self)




    def diagram(self):

        localctx = MermaidSequenceParser.DiagramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_diagram)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 89
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==51:
                self.state = 86
                self.match(MermaidSequenceParser.NEWLINE)
                self.state = 91
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 92
            self.match(MermaidSequenceParser.SEQUENCE_DIAGRAM)
            self.state = 94 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 93
                    self.match(MermaidSequenceParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 96 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,1,self._ctx)

            self.state = 101
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 3483819427472380) != 0):
                self.state = 98
                self.statement()
                self.state = 103
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 104
            self.match(MermaidSequenceParser.EOF)
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

        def participantDecl(self):
            return self.getTypedRuleContext(MermaidSequenceParser.ParticipantDeclContext,0)


        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidSequenceParser.NEWLINE)
            else:
                return self.getToken(MermaidSequenceParser.NEWLINE, i)

        def actorDecl(self):
            return self.getTypedRuleContext(MermaidSequenceParser.ActorDeclContext,0)


        def boxBlock(self):
            return self.getTypedRuleContext(MermaidSequenceParser.BoxBlockContext,0)


        def createDirective(self):
            return self.getTypedRuleContext(MermaidSequenceParser.CreateDirectiveContext,0)


        def destroyDirective(self):
            return self.getTypedRuleContext(MermaidSequenceParser.DestroyDirectiveContext,0)


        def messageStatement(self):
            return self.getTypedRuleContext(MermaidSequenceParser.MessageStatementContext,0)


        def activateStatement(self):
            return self.getTypedRuleContext(MermaidSequenceParser.ActivateStatementContext,0)


        def deactivateStatement(self):
            return self.getTypedRuleContext(MermaidSequenceParser.DeactivateStatementContext,0)


        def noteStatement(self):
            return self.getTypedRuleContext(MermaidSequenceParser.NoteStatementContext,0)


        def loopBlock(self):
            return self.getTypedRuleContext(MermaidSequenceParser.LoopBlockContext,0)


        def altBlock(self):
            return self.getTypedRuleContext(MermaidSequenceParser.AltBlockContext,0)


        def optBlock(self):
            return self.getTypedRuleContext(MermaidSequenceParser.OptBlockContext,0)


        def parBlock(self):
            return self.getTypedRuleContext(MermaidSequenceParser.ParBlockContext,0)


        def criticalBlock(self):
            return self.getTypedRuleContext(MermaidSequenceParser.CriticalBlockContext,0)


        def breakBlock(self):
            return self.getTypedRuleContext(MermaidSequenceParser.BreakBlockContext,0)


        def rectBlock(self):
            return self.getTypedRuleContext(MermaidSequenceParser.RectBlockContext,0)


        def autonumberStatement(self):
            return self.getTypedRuleContext(MermaidSequenceParser.AutonumberStatementContext,0)


        def linkStatement(self):
            return self.getTypedRuleContext(MermaidSequenceParser.LinkStatementContext,0)


        def linksStatement(self):
            return self.getTypedRuleContext(MermaidSequenceParser.LinksStatementContext,0)


        def COMMENT(self):
            return self.getToken(MermaidSequenceParser.COMMENT, 0)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_statement

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStatement" ):
                return visitor.visitStatement(self)
            else:
                return visitor.visitChildren(self)




    def statement(self):

        localctx = MermaidSequenceParser.StatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_statement)
        try:
            self.state = 191
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,16,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 106
                self.participantDecl()
                self.state = 108 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 107
                        self.match(MermaidSequenceParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 110 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,3,self._ctx)

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 112
                self.actorDecl()
                self.state = 114 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 113
                        self.match(MermaidSequenceParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 116 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,4,self._ctx)

                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 118
                self.boxBlock()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 119
                self.createDirective()
                self.state = 121 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 120
                        self.match(MermaidSequenceParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 123 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,5,self._ctx)

                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 125
                self.destroyDirective()
                self.state = 127 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 126
                        self.match(MermaidSequenceParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 129 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,6,self._ctx)

                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 131
                self.messageStatement()
                self.state = 133 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 132
                        self.match(MermaidSequenceParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 135 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,7,self._ctx)

                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 137
                self.activateStatement()
                self.state = 139 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 138
                        self.match(MermaidSequenceParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 141 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,8,self._ctx)

                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 143
                self.deactivateStatement()
                self.state = 145 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 144
                        self.match(MermaidSequenceParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 147 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,9,self._ctx)

                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 149
                self.noteStatement()
                self.state = 151 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 150
                        self.match(MermaidSequenceParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 153 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,10,self._ctx)

                pass

            elif la_ == 10:
                self.enterOuterAlt(localctx, 10)
                self.state = 155
                self.loopBlock()
                pass

            elif la_ == 11:
                self.enterOuterAlt(localctx, 11)
                self.state = 156
                self.altBlock()
                pass

            elif la_ == 12:
                self.enterOuterAlt(localctx, 12)
                self.state = 157
                self.optBlock()
                pass

            elif la_ == 13:
                self.enterOuterAlt(localctx, 13)
                self.state = 158
                self.parBlock()
                pass

            elif la_ == 14:
                self.enterOuterAlt(localctx, 14)
                self.state = 159
                self.criticalBlock()
                pass

            elif la_ == 15:
                self.enterOuterAlt(localctx, 15)
                self.state = 160
                self.breakBlock()
                pass

            elif la_ == 16:
                self.enterOuterAlt(localctx, 16)
                self.state = 161
                self.rectBlock()
                pass

            elif la_ == 17:
                self.enterOuterAlt(localctx, 17)
                self.state = 162
                self.autonumberStatement()
                self.state = 164 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 163
                        self.match(MermaidSequenceParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 166 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,11,self._ctx)

                pass

            elif la_ == 18:
                self.enterOuterAlt(localctx, 18)
                self.state = 168
                self.linkStatement()
                self.state = 170 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 169
                        self.match(MermaidSequenceParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 172 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,12,self._ctx)

                pass

            elif la_ == 19:
                self.enterOuterAlt(localctx, 19)
                self.state = 174
                self.linksStatement()
                self.state = 176 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 175
                        self.match(MermaidSequenceParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 178 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,13,self._ctx)

                pass

            elif la_ == 20:
                self.enterOuterAlt(localctx, 20)
                self.state = 180
                self.match(MermaidSequenceParser.COMMENT)
                self.state = 182 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 181
                        self.match(MermaidSequenceParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 184 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,14,self._ctx)

                pass

            elif la_ == 21:
                self.enterOuterAlt(localctx, 21)
                self.state = 187 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 186
                        self.match(MermaidSequenceParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 189 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,15,self._ctx)

                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ParticipantDeclContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def participantType(self):
            return self.getTypedRuleContext(MermaidSequenceParser.ParticipantTypeContext,0)


        def participantId(self):
            return self.getTypedRuleContext(MermaidSequenceParser.ParticipantIdContext,0)


        def AS(self):
            return self.getToken(MermaidSequenceParser.AS, 0)

        def label(self):
            return self.getTypedRuleContext(MermaidSequenceParser.LabelContext,0)


        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_participantDecl

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParticipantDecl" ):
                return visitor.visitParticipantDecl(self)
            else:
                return visitor.visitChildren(self)




    def participantDecl(self):

        localctx = MermaidSequenceParser.ParticipantDeclContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_participantDecl)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 193
            self.participantType()
            self.state = 194
            self.participantId()
            self.state = 197
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==12:
                self.state = 195
                self.match(MermaidSequenceParser.AS)
                self.state = 196
                self.label()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ParticipantTypeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PARTICIPANT(self):
            return self.getToken(MermaidSequenceParser.PARTICIPANT, 0)

        def ACTOR(self):
            return self.getToken(MermaidSequenceParser.ACTOR, 0)

        def BOUNDARY(self):
            return self.getToken(MermaidSequenceParser.BOUNDARY, 0)

        def CONTROL(self):
            return self.getToken(MermaidSequenceParser.CONTROL, 0)

        def ENTITY(self):
            return self.getToken(MermaidSequenceParser.ENTITY, 0)

        def DATABASE(self):
            return self.getToken(MermaidSequenceParser.DATABASE, 0)

        def COLLECTIONS(self):
            return self.getToken(MermaidSequenceParser.COLLECTIONS, 0)

        def QUEUE(self):
            return self.getToken(MermaidSequenceParser.QUEUE, 0)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_participantType

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParticipantType" ):
                return visitor.visitParticipantType(self)
            else:
                return visitor.visitChildren(self)




    def participantType(self):

        localctx = MermaidSequenceParser.ParticipantTypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_participantType)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 199
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 1020) != 0)):
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


    class ActorDeclContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ACTOR(self):
            return self.getToken(MermaidSequenceParser.ACTOR, 0)

        def participantId(self):
            return self.getTypedRuleContext(MermaidSequenceParser.ParticipantIdContext,0)


        def AS(self):
            return self.getToken(MermaidSequenceParser.AS, 0)

        def label(self):
            return self.getTypedRuleContext(MermaidSequenceParser.LabelContext,0)


        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_actorDecl

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitActorDecl" ):
                return visitor.visitActorDecl(self)
            else:
                return visitor.visitChildren(self)




    def actorDecl(self):

        localctx = MermaidSequenceParser.ActorDeclContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_actorDecl)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 201
            self.match(MermaidSequenceParser.ACTOR)
            self.state = 202
            self.participantId()
            self.state = 205
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==12:
                self.state = 203
                self.match(MermaidSequenceParser.AS)
                self.state = 204
                self.label()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ParticipantIdContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def QUOTED_STRING(self):
            return self.getToken(MermaidSequenceParser.QUOTED_STRING, 0)

        def ID(self):
            return self.getToken(MermaidSequenceParser.ID, 0)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_participantId

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParticipantId" ):
                return visitor.visitParticipantId(self)
            else:
                return visitor.visitChildren(self)




    def participantId(self):

        localctx = MermaidSequenceParser.ParticipantIdContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_participantId)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 207
            _la = self._input.LA(1)
            if not(_la==45 or _la==46):
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


    class LabelContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def QUOTED_STRING(self):
            return self.getToken(MermaidSequenceParser.QUOTED_STRING, 0)

        def LABEL_REST(self):
            return self.getToken(MermaidSequenceParser.LABEL_REST, 0)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_label

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLabel" ):
                return visitor.visitLabel(self)
            else:
                return visitor.visitChildren(self)




    def label(self):

        localctx = MermaidSequenceParser.LabelContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_label)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 209
            _la = self._input.LA(1)
            if not(_la==45 or _la==54):
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


    class BoxBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def BOX(self):
            return self.getToken(MermaidSequenceParser.BOX, 0)

        def END(self):
            return self.getToken(MermaidSequenceParser.END, 0)

        def boxColor(self):
            return self.getTypedRuleContext(MermaidSequenceParser.BoxColorContext,0)


        def boxLabel(self):
            return self.getTypedRuleContext(MermaidSequenceParser.BoxLabelContext,0)


        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidSequenceParser.NEWLINE)
            else:
                return self.getToken(MermaidSequenceParser.NEWLINE, i)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MermaidSequenceParser.StatementContext)
            else:
                return self.getTypedRuleContext(MermaidSequenceParser.StatementContext,i)


        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_boxBlock

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBoxBlock" ):
                return visitor.visitBoxBlock(self)
            else:
                return visitor.visitChildren(self)




    def boxBlock(self):

        localctx = MermaidSequenceParser.BoxBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_boxBlock)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 211
            self.match(MermaidSequenceParser.BOX)
            self.state = 213
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 985179598356480) != 0):
                self.state = 212
                self.boxColor()


            self.state = 216
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==45 or _la==54:
                self.state = 215
                self.boxLabel()


            self.state = 219 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 218
                    self.match(MermaidSequenceParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 221 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,21,self._ctx)

            self.state = 226
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 3483819427472380) != 0):
                self.state = 223
                self.statement()
                self.state = 228
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 229
            self.match(MermaidSequenceParser.END)
            self.state = 231 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 230
                    self.match(MermaidSequenceParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 233 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,23,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BoxColorContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COLOR_NAME(self):
            return self.getToken(MermaidSequenceParser.COLOR_NAME, 0)

        def RGB_COLOR(self):
            return self.getToken(MermaidSequenceParser.RGB_COLOR, 0)

        def RGBA_COLOR(self):
            return self.getToken(MermaidSequenceParser.RGBA_COLOR, 0)

        def TRANSPARENT(self):
            return self.getToken(MermaidSequenceParser.TRANSPARENT, 0)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_boxColor

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBoxColor" ):
                return visitor.visitBoxColor(self)
            else:
                return visitor.visitChildren(self)




    def boxColor(self):

        localctx = MermaidSequenceParser.BoxColorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_boxColor)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 235
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 985179598356480) != 0)):
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


    class BoxLabelContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def QUOTED_STRING(self):
            return self.getToken(MermaidSequenceParser.QUOTED_STRING, 0)

        def LABEL_REST(self):
            return self.getToken(MermaidSequenceParser.LABEL_REST, 0)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_boxLabel

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBoxLabel" ):
                return visitor.visitBoxLabel(self)
            else:
                return visitor.visitChildren(self)




    def boxLabel(self):

        localctx = MermaidSequenceParser.BoxLabelContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_boxLabel)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 237
            _la = self._input.LA(1)
            if not(_la==45 or _la==54):
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


    class CreateDirectiveContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CREATE(self):
            return self.getToken(MermaidSequenceParser.CREATE, 0)

        def participantType(self):
            return self.getTypedRuleContext(MermaidSequenceParser.ParticipantTypeContext,0)


        def participantId(self):
            return self.getTypedRuleContext(MermaidSequenceParser.ParticipantIdContext,0)


        def AS(self):
            return self.getToken(MermaidSequenceParser.AS, 0)

        def label(self):
            return self.getTypedRuleContext(MermaidSequenceParser.LabelContext,0)


        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_createDirective

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCreateDirective" ):
                return visitor.visitCreateDirective(self)
            else:
                return visitor.visitChildren(self)




    def createDirective(self):

        localctx = MermaidSequenceParser.CreateDirectiveContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_createDirective)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 239
            self.match(MermaidSequenceParser.CREATE)
            self.state = 240
            self.participantType()
            self.state = 241
            self.participantId()
            self.state = 244
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==12:
                self.state = 242
                self.match(MermaidSequenceParser.AS)
                self.state = 243
                self.label()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DestroyDirectiveContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DESTROY(self):
            return self.getToken(MermaidSequenceParser.DESTROY, 0)

        def participantId(self):
            return self.getTypedRuleContext(MermaidSequenceParser.ParticipantIdContext,0)


        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_destroyDirective

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDestroyDirective" ):
                return visitor.visitDestroyDirective(self)
            else:
                return visitor.visitChildren(self)




    def destroyDirective(self):

        localctx = MermaidSequenceParser.DestroyDirectiveContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_destroyDirective)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 246
            self.match(MermaidSequenceParser.DESTROY)
            self.state = 247
            self.participantId()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class MessageStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def sender(self):
            return self.getTypedRuleContext(MermaidSequenceParser.SenderContext,0)


        def ARROW(self):
            return self.getToken(MermaidSequenceParser.ARROW, 0)

        def receiver(self):
            return self.getTypedRuleContext(MermaidSequenceParser.ReceiverContext,0)


        def COLON(self):
            return self.getToken(MermaidSequenceParser.COLON, 0)

        def messageText(self):
            return self.getTypedRuleContext(MermaidSequenceParser.MessageTextContext,0)


        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_messageStatement

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMessageStatement" ):
                return visitor.visitMessageStatement(self)
            else:
                return visitor.visitChildren(self)




    def messageStatement(self):

        localctx = MermaidSequenceParser.MessageStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_messageStatement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 249
            self.sender()
            self.state = 250
            self.match(MermaidSequenceParser.ARROW)
            self.state = 251
            self.receiver()
            self.state = 252
            self.match(MermaidSequenceParser.COLON)
            self.state = 253
            self.messageText()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SenderContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def participantId(self):
            return self.getTypedRuleContext(MermaidSequenceParser.ParticipantIdContext,0)


        def LPAREN(self):
            return self.getToken(MermaidSequenceParser.LPAREN, 0)

        def RPAREN(self):
            return self.getToken(MermaidSequenceParser.RPAREN, 0)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_sender

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSender" ):
                return visitor.visitSender(self)
            else:
                return visitor.visitChildren(self)




    def sender(self):

        localctx = MermaidSequenceParser.SenderContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_sender)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 256
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==39:
                self.state = 255
                self.match(MermaidSequenceParser.LPAREN)


            self.state = 258
            self.participantId()
            self.state = 260
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==40:
                self.state = 259
                self.match(MermaidSequenceParser.RPAREN)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ReceiverContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def participantId(self):
            return self.getTypedRuleContext(MermaidSequenceParser.ParticipantIdContext,0)


        def LPAREN(self):
            return self.getToken(MermaidSequenceParser.LPAREN, 0)

        def RPAREN(self):
            return self.getToken(MermaidSequenceParser.RPAREN, 0)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_receiver

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitReceiver" ):
                return visitor.visitReceiver(self)
            else:
                return visitor.visitChildren(self)




    def receiver(self):

        localctx = MermaidSequenceParser.ReceiverContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_receiver)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 263
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==39:
                self.state = 262
                self.match(MermaidSequenceParser.LPAREN)


            self.state = 265
            self.participantId()
            self.state = 267
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==40:
                self.state = 266
                self.match(MermaidSequenceParser.RPAREN)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class MessageTextContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TEXT_REST(self):
            return self.getToken(MermaidSequenceParser.TEXT_REST, 0)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_messageText

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMessageText" ):
                return visitor.visitMessageText(self)
            else:
                return visitor.visitChildren(self)




    def messageText(self):

        localctx = MermaidSequenceParser.MessageTextContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_messageText)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 270
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==56:
                self.state = 269
                self.match(MermaidSequenceParser.TEXT_REST)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ActivateStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ACTIVATE(self):
            return self.getToken(MermaidSequenceParser.ACTIVATE, 0)

        def participantId(self):
            return self.getTypedRuleContext(MermaidSequenceParser.ParticipantIdContext,0)


        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_activateStatement

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitActivateStatement" ):
                return visitor.visitActivateStatement(self)
            else:
                return visitor.visitChildren(self)




    def activateStatement(self):

        localctx = MermaidSequenceParser.ActivateStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_activateStatement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 272
            self.match(MermaidSequenceParser.ACTIVATE)
            self.state = 273
            self.participantId()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DeactivateStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DEACTIVATE(self):
            return self.getToken(MermaidSequenceParser.DEACTIVATE, 0)

        def participantId(self):
            return self.getTypedRuleContext(MermaidSequenceParser.ParticipantIdContext,0)


        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_deactivateStatement

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDeactivateStatement" ):
                return visitor.visitDeactivateStatement(self)
            else:
                return visitor.visitChildren(self)




    def deactivateStatement(self):

        localctx = MermaidSequenceParser.DeactivateStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_deactivateStatement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 275
            self.match(MermaidSequenceParser.DEACTIVATE)
            self.state = 276
            self.participantId()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NoteStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NOTE(self):
            return self.getToken(MermaidSequenceParser.NOTE, 0)

        def notePosition(self):
            return self.getTypedRuleContext(MermaidSequenceParser.NotePositionContext,0)


        def participantId(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MermaidSequenceParser.ParticipantIdContext)
            else:
                return self.getTypedRuleContext(MermaidSequenceParser.ParticipantIdContext,i)


        def COLON(self):
            return self.getToken(MermaidSequenceParser.COLON, 0)

        def noteText(self):
            return self.getTypedRuleContext(MermaidSequenceParser.NoteTextContext,0)


        def COMMA(self):
            return self.getToken(MermaidSequenceParser.COMMA, 0)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_noteStatement

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNoteStatement" ):
                return visitor.visitNoteStatement(self)
            else:
                return visitor.visitChildren(self)




    def noteStatement(self):

        localctx = MermaidSequenceParser.NoteStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_noteStatement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 278
            self.match(MermaidSequenceParser.NOTE)
            self.state = 279
            self.notePosition()
            self.state = 280
            self.participantId()
            self.state = 283
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==37:
                self.state = 281
                self.match(MermaidSequenceParser.COMMA)
                self.state = 282
                self.participantId()


            self.state = 285
            self.match(MermaidSequenceParser.COLON)
            self.state = 286
            self.noteText()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NotePositionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def RIGHT_OF(self):
            return self.getToken(MermaidSequenceParser.RIGHT_OF, 0)

        def LEFT_OF(self):
            return self.getToken(MermaidSequenceParser.LEFT_OF, 0)

        def OVER(self):
            return self.getToken(MermaidSequenceParser.OVER, 0)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_notePosition

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNotePosition" ):
                return visitor.visitNotePosition(self)
            else:
                return visitor.visitChildren(self)




    def notePosition(self):

        localctx = MermaidSequenceParser.NotePositionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_notePosition)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 288
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 1051648) != 0)):
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


    class NoteTextContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TEXT_REST(self):
            return self.getToken(MermaidSequenceParser.TEXT_REST, 0)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_noteText

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNoteText" ):
                return visitor.visitNoteText(self)
            else:
                return visitor.visitChildren(self)




    def noteText(self):

        localctx = MermaidSequenceParser.NoteTextContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_noteText)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 291
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==56:
                self.state = 290
                self.match(MermaidSequenceParser.TEXT_REST)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LoopBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LOOP(self):
            return self.getToken(MermaidSequenceParser.LOOP, 0)

        def loopLabel(self):
            return self.getTypedRuleContext(MermaidSequenceParser.LoopLabelContext,0)


        def END(self):
            return self.getToken(MermaidSequenceParser.END, 0)

        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidSequenceParser.NEWLINE)
            else:
                return self.getToken(MermaidSequenceParser.NEWLINE, i)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MermaidSequenceParser.StatementContext)
            else:
                return self.getTypedRuleContext(MermaidSequenceParser.StatementContext,i)


        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_loopBlock

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLoopBlock" ):
                return visitor.visitLoopBlock(self)
            else:
                return visitor.visitChildren(self)




    def loopBlock(self):

        localctx = MermaidSequenceParser.LoopBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_loopBlock)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 293
            self.match(MermaidSequenceParser.LOOP)
            self.state = 294
            self.loopLabel()
            self.state = 296 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 295
                    self.match(MermaidSequenceParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 298 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,32,self._ctx)

            self.state = 303
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 3483819427472380) != 0):
                self.state = 300
                self.statement()
                self.state = 305
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 306
            self.match(MermaidSequenceParser.END)
            self.state = 308 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 307
                    self.match(MermaidSequenceParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 310 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,34,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LoopLabelContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TEXT_REST(self):
            return self.getToken(MermaidSequenceParser.TEXT_REST, 0)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_loopLabel

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLoopLabel" ):
                return visitor.visitLoopLabel(self)
            else:
                return visitor.visitChildren(self)




    def loopLabel(self):

        localctx = MermaidSequenceParser.LoopLabelContext(self, self._ctx, self.state)
        self.enterRule(localctx, 44, self.RULE_loopLabel)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 313
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==56:
                self.state = 312
                self.match(MermaidSequenceParser.TEXT_REST)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AltBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ALT(self):
            return self.getToken(MermaidSequenceParser.ALT, 0)

        def altCondition(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MermaidSequenceParser.AltConditionContext)
            else:
                return self.getTypedRuleContext(MermaidSequenceParser.AltConditionContext,i)


        def END(self):
            return self.getToken(MermaidSequenceParser.END, 0)

        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidSequenceParser.NEWLINE)
            else:
                return self.getToken(MermaidSequenceParser.NEWLINE, i)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MermaidSequenceParser.StatementContext)
            else:
                return self.getTypedRuleContext(MermaidSequenceParser.StatementContext,i)


        def ELSE(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidSequenceParser.ELSE)
            else:
                return self.getToken(MermaidSequenceParser.ELSE, i)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_altBlock

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAltBlock" ):
                return visitor.visitAltBlock(self)
            else:
                return visitor.visitChildren(self)




    def altBlock(self):

        localctx = MermaidSequenceParser.AltBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 46, self.RULE_altBlock)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 315
            self.match(MermaidSequenceParser.ALT)
            self.state = 316
            self.altCondition()
            self.state = 318 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 317
                    self.match(MermaidSequenceParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 320 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,36,self._ctx)

            self.state = 325
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 3483819427472380) != 0):
                self.state = 322
                self.statement()
                self.state = 327
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 343
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==23:
                self.state = 328
                self.match(MermaidSequenceParser.ELSE)
                self.state = 329
                self.altCondition()
                self.state = 331 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 330
                        self.match(MermaidSequenceParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 333 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,38,self._ctx)

                self.state = 338
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while (((_la) & ~0x3f) == 0 and ((1 << _la) & 3483819427472380) != 0):
                    self.state = 335
                    self.statement()
                    self.state = 340
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 345
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 346
            self.match(MermaidSequenceParser.END)
            self.state = 348 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 347
                    self.match(MermaidSequenceParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 350 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,41,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OptBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def OPT(self):
            return self.getToken(MermaidSequenceParser.OPT, 0)

        def optCondition(self):
            return self.getTypedRuleContext(MermaidSequenceParser.OptConditionContext,0)


        def END(self):
            return self.getToken(MermaidSequenceParser.END, 0)

        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidSequenceParser.NEWLINE)
            else:
                return self.getToken(MermaidSequenceParser.NEWLINE, i)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MermaidSequenceParser.StatementContext)
            else:
                return self.getTypedRuleContext(MermaidSequenceParser.StatementContext,i)


        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_optBlock

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOptBlock" ):
                return visitor.visitOptBlock(self)
            else:
                return visitor.visitChildren(self)




    def optBlock(self):

        localctx = MermaidSequenceParser.OptBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 48, self.RULE_optBlock)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 352
            self.match(MermaidSequenceParser.OPT)
            self.state = 353
            self.optCondition()
            self.state = 355 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 354
                    self.match(MermaidSequenceParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 357 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,42,self._ctx)

            self.state = 362
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 3483819427472380) != 0):
                self.state = 359
                self.statement()
                self.state = 364
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 365
            self.match(MermaidSequenceParser.END)
            self.state = 367 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 366
                    self.match(MermaidSequenceParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 369 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,44,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AltConditionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TEXT_REST(self):
            return self.getToken(MermaidSequenceParser.TEXT_REST, 0)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_altCondition

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAltCondition" ):
                return visitor.visitAltCondition(self)
            else:
                return visitor.visitChildren(self)




    def altCondition(self):

        localctx = MermaidSequenceParser.AltConditionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 50, self.RULE_altCondition)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 372
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==56:
                self.state = 371
                self.match(MermaidSequenceParser.TEXT_REST)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OptConditionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TEXT_REST(self):
            return self.getToken(MermaidSequenceParser.TEXT_REST, 0)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_optCondition

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOptCondition" ):
                return visitor.visitOptCondition(self)
            else:
                return visitor.visitChildren(self)




    def optCondition(self):

        localctx = MermaidSequenceParser.OptConditionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 52, self.RULE_optCondition)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 375
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==56:
                self.state = 374
                self.match(MermaidSequenceParser.TEXT_REST)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ParBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PAR(self):
            return self.getToken(MermaidSequenceParser.PAR, 0)

        def parLabel(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MermaidSequenceParser.ParLabelContext)
            else:
                return self.getTypedRuleContext(MermaidSequenceParser.ParLabelContext,i)


        def END(self):
            return self.getToken(MermaidSequenceParser.END, 0)

        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidSequenceParser.NEWLINE)
            else:
                return self.getToken(MermaidSequenceParser.NEWLINE, i)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MermaidSequenceParser.StatementContext)
            else:
                return self.getTypedRuleContext(MermaidSequenceParser.StatementContext,i)


        def AND(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidSequenceParser.AND)
            else:
                return self.getToken(MermaidSequenceParser.AND, i)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_parBlock

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParBlock" ):
                return visitor.visitParBlock(self)
            else:
                return visitor.visitChildren(self)




    def parBlock(self):

        localctx = MermaidSequenceParser.ParBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 54, self.RULE_parBlock)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 377
            self.match(MermaidSequenceParser.PAR)
            self.state = 378
            self.parLabel()
            self.state = 380 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 379
                    self.match(MermaidSequenceParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 382 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,47,self._ctx)

            self.state = 387
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 3483819427472380) != 0):
                self.state = 384
                self.statement()
                self.state = 389
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 405
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==26:
                self.state = 390
                self.match(MermaidSequenceParser.AND)
                self.state = 391
                self.parLabel()
                self.state = 393 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 392
                        self.match(MermaidSequenceParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 395 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,49,self._ctx)

                self.state = 400
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while (((_la) & ~0x3f) == 0 and ((1 << _la) & 3483819427472380) != 0):
                    self.state = 397
                    self.statement()
                    self.state = 402
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 407
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 408
            self.match(MermaidSequenceParser.END)
            self.state = 410 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 409
                    self.match(MermaidSequenceParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 412 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,52,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ParLabelContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TEXT_REST(self):
            return self.getToken(MermaidSequenceParser.TEXT_REST, 0)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_parLabel

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParLabel" ):
                return visitor.visitParLabel(self)
            else:
                return visitor.visitChildren(self)




    def parLabel(self):

        localctx = MermaidSequenceParser.ParLabelContext(self, self._ctx, self.state)
        self.enterRule(localctx, 56, self.RULE_parLabel)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 415
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==56:
                self.state = 414
                self.match(MermaidSequenceParser.TEXT_REST)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CriticalBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CRITICAL(self):
            return self.getToken(MermaidSequenceParser.CRITICAL, 0)

        def criticalAction(self):
            return self.getTypedRuleContext(MermaidSequenceParser.CriticalActionContext,0)


        def END(self):
            return self.getToken(MermaidSequenceParser.END, 0)

        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidSequenceParser.NEWLINE)
            else:
                return self.getToken(MermaidSequenceParser.NEWLINE, i)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MermaidSequenceParser.StatementContext)
            else:
                return self.getTypedRuleContext(MermaidSequenceParser.StatementContext,i)


        def OPTION(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidSequenceParser.OPTION)
            else:
                return self.getToken(MermaidSequenceParser.OPTION, i)

        def optionCondition(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MermaidSequenceParser.OptionConditionContext)
            else:
                return self.getTypedRuleContext(MermaidSequenceParser.OptionConditionContext,i)


        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_criticalBlock

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCriticalBlock" ):
                return visitor.visitCriticalBlock(self)
            else:
                return visitor.visitChildren(self)




    def criticalBlock(self):

        localctx = MermaidSequenceParser.CriticalBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 58, self.RULE_criticalBlock)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 417
            self.match(MermaidSequenceParser.CRITICAL)
            self.state = 418
            self.criticalAction()
            self.state = 420 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 419
                    self.match(MermaidSequenceParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 422 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,54,self._ctx)

            self.state = 427
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 3483819427472380) != 0):
                self.state = 424
                self.statement()
                self.state = 429
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 445
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==28:
                self.state = 430
                self.match(MermaidSequenceParser.OPTION)
                self.state = 431
                self.optionCondition()
                self.state = 433 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 432
                        self.match(MermaidSequenceParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 435 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,56,self._ctx)

                self.state = 440
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while (((_la) & ~0x3f) == 0 and ((1 << _la) & 3483819427472380) != 0):
                    self.state = 437
                    self.statement()
                    self.state = 442
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 447
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 448
            self.match(MermaidSequenceParser.END)
            self.state = 450 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 449
                    self.match(MermaidSequenceParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 452 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,59,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CriticalActionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TEXT_REST(self):
            return self.getToken(MermaidSequenceParser.TEXT_REST, 0)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_criticalAction

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCriticalAction" ):
                return visitor.visitCriticalAction(self)
            else:
                return visitor.visitChildren(self)




    def criticalAction(self):

        localctx = MermaidSequenceParser.CriticalActionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 60, self.RULE_criticalAction)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 455
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==56:
                self.state = 454
                self.match(MermaidSequenceParser.TEXT_REST)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OptionConditionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TEXT_REST(self):
            return self.getToken(MermaidSequenceParser.TEXT_REST, 0)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_optionCondition

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOptionCondition" ):
                return visitor.visitOptionCondition(self)
            else:
                return visitor.visitChildren(self)




    def optionCondition(self):

        localctx = MermaidSequenceParser.OptionConditionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 62, self.RULE_optionCondition)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 458
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==56:
                self.state = 457
                self.match(MermaidSequenceParser.TEXT_REST)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BreakBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def BREAK(self):
            return self.getToken(MermaidSequenceParser.BREAK, 0)

        def breakCondition(self):
            return self.getTypedRuleContext(MermaidSequenceParser.BreakConditionContext,0)


        def END(self):
            return self.getToken(MermaidSequenceParser.END, 0)

        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidSequenceParser.NEWLINE)
            else:
                return self.getToken(MermaidSequenceParser.NEWLINE, i)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MermaidSequenceParser.StatementContext)
            else:
                return self.getTypedRuleContext(MermaidSequenceParser.StatementContext,i)


        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_breakBlock

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBreakBlock" ):
                return visitor.visitBreakBlock(self)
            else:
                return visitor.visitChildren(self)




    def breakBlock(self):

        localctx = MermaidSequenceParser.BreakBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 64, self.RULE_breakBlock)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 460
            self.match(MermaidSequenceParser.BREAK)
            self.state = 461
            self.breakCondition()
            self.state = 463 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 462
                    self.match(MermaidSequenceParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 465 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,62,self._ctx)

            self.state = 470
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 3483819427472380) != 0):
                self.state = 467
                self.statement()
                self.state = 472
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 473
            self.match(MermaidSequenceParser.END)
            self.state = 475 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 474
                    self.match(MermaidSequenceParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 477 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,64,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BreakConditionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TEXT_REST(self):
            return self.getToken(MermaidSequenceParser.TEXT_REST, 0)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_breakCondition

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBreakCondition" ):
                return visitor.visitBreakCondition(self)
            else:
                return visitor.visitChildren(self)




    def breakCondition(self):

        localctx = MermaidSequenceParser.BreakConditionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 66, self.RULE_breakCondition)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 480
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==56:
                self.state = 479
                self.match(MermaidSequenceParser.TEXT_REST)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RectBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def RECT(self):
            return self.getToken(MermaidSequenceParser.RECT, 0)

        def rectColor(self):
            return self.getTypedRuleContext(MermaidSequenceParser.RectColorContext,0)


        def END(self):
            return self.getToken(MermaidSequenceParser.END, 0)

        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidSequenceParser.NEWLINE)
            else:
                return self.getToken(MermaidSequenceParser.NEWLINE, i)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MermaidSequenceParser.StatementContext)
            else:
                return self.getTypedRuleContext(MermaidSequenceParser.StatementContext,i)


        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_rectBlock

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRectBlock" ):
                return visitor.visitRectBlock(self)
            else:
                return visitor.visitChildren(self)




    def rectBlock(self):

        localctx = MermaidSequenceParser.RectBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 68, self.RULE_rectBlock)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 482
            self.match(MermaidSequenceParser.RECT)
            self.state = 483
            self.rectColor()
            self.state = 485 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 484
                    self.match(MermaidSequenceParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 487 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,66,self._ctx)

            self.state = 492
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 3483819427472380) != 0):
                self.state = 489
                self.statement()
                self.state = 494
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 495
            self.match(MermaidSequenceParser.END)
            self.state = 497 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 496
                    self.match(MermaidSequenceParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 499 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,68,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RectColorContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COLOR_NAME(self):
            return self.getToken(MermaidSequenceParser.COLOR_NAME, 0)

        def RGB_COLOR(self):
            return self.getToken(MermaidSequenceParser.RGB_COLOR, 0)

        def RGBA_COLOR(self):
            return self.getToken(MermaidSequenceParser.RGBA_COLOR, 0)

        def TRANSPARENT(self):
            return self.getToken(MermaidSequenceParser.TRANSPARENT, 0)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_rectColor

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRectColor" ):
                return visitor.visitRectColor(self)
            else:
                return visitor.visitChildren(self)




    def rectColor(self):

        localctx = MermaidSequenceParser.RectColorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 70, self.RULE_rectColor)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 501
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 985179598356480) != 0)):
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


    class AutonumberStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def AUTONUMBER(self):
            return self.getToken(MermaidSequenceParser.AUTONUMBER, 0)

        def INT(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidSequenceParser.INT)
            else:
                return self.getToken(MermaidSequenceParser.INT, i)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_autonumberStatement

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAutonumberStatement" ):
                return visitor.visitAutonumberStatement(self)
            else:
                return visitor.visitChildren(self)




    def autonumberStatement(self):

        localctx = MermaidSequenceParser.AutonumberStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 72, self.RULE_autonumberStatement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 503
            self.match(MermaidSequenceParser.AUTONUMBER)
            self.state = 511
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==43:
                self.state = 504
                self.match(MermaidSequenceParser.INT)
                self.state = 509
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==43:
                    self.state = 505
                    self.match(MermaidSequenceParser.INT)
                    self.state = 507
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if _la==43:
                        self.state = 506
                        self.match(MermaidSequenceParser.INT)






        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LinkStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LINK(self):
            return self.getToken(MermaidSequenceParser.LINK, 0)

        def participantId(self):
            return self.getTypedRuleContext(MermaidSequenceParser.ParticipantIdContext,0)


        def COLON(self):
            return self.getToken(MermaidSequenceParser.COLON, 0)

        def linkLabel(self):
            return self.getTypedRuleContext(MermaidSequenceParser.LinkLabelContext,0)


        def AT(self):
            return self.getToken(MermaidSequenceParser.AT, 0)

        def linkUrl(self):
            return self.getTypedRuleContext(MermaidSequenceParser.LinkUrlContext,0)


        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_linkStatement

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLinkStatement" ):
                return visitor.visitLinkStatement(self)
            else:
                return visitor.visitChildren(self)




    def linkStatement(self):

        localctx = MermaidSequenceParser.LinkStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 74, self.RULE_linkStatement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 513
            self.match(MermaidSequenceParser.LINK)
            self.state = 514
            self.participantId()
            self.state = 515
            self.match(MermaidSequenceParser.COLON)
            self.state = 516
            self.linkLabel()
            self.state = 517
            self.match(MermaidSequenceParser.AT)
            self.state = 518
            self.linkUrl()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LinksStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LINKS(self):
            return self.getToken(MermaidSequenceParser.LINKS, 0)

        def participantId(self):
            return self.getTypedRuleContext(MermaidSequenceParser.ParticipantIdContext,0)


        def COLON(self):
            return self.getToken(MermaidSequenceParser.COLON, 0)

        def jsonObject(self):
            return self.getTypedRuleContext(MermaidSequenceParser.JsonObjectContext,0)


        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_linksStatement

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLinksStatement" ):
                return visitor.visitLinksStatement(self)
            else:
                return visitor.visitChildren(self)




    def linksStatement(self):

        localctx = MermaidSequenceParser.LinksStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 76, self.RULE_linksStatement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 520
            self.match(MermaidSequenceParser.LINKS)
            self.state = 521
            self.participantId()
            self.state = 522
            self.match(MermaidSequenceParser.COLON)
            self.state = 523
            self.jsonObject()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LinkLabelContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TEXT_REST(self):
            return self.getToken(MermaidSequenceParser.TEXT_REST, 0)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_linkLabel

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLinkLabel" ):
                return visitor.visitLinkLabel(self)
            else:
                return visitor.visitChildren(self)




    def linkLabel(self):

        localctx = MermaidSequenceParser.LinkLabelContext(self, self._ctx, self.state)
        self.enterRule(localctx, 78, self.RULE_linkLabel)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 526
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==56:
                self.state = 525
                self.match(MermaidSequenceParser.TEXT_REST)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LinkUrlContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TEXT_REST(self):
            return self.getToken(MermaidSequenceParser.TEXT_REST, 0)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_linkUrl

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLinkUrl" ):
                return visitor.visitLinkUrl(self)
            else:
                return visitor.visitChildren(self)




    def linkUrl(self):

        localctx = MermaidSequenceParser.LinkUrlContext(self, self._ctx, self.state)
        self.enterRule(localctx, 80, self.RULE_linkUrl)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 529
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==56:
                self.state = 528
                self.match(MermaidSequenceParser.TEXT_REST)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class JsonObjectContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACE(self):
            return self.getToken(MermaidSequenceParser.LBRACE, 0)

        def jsonPair(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MermaidSequenceParser.JsonPairContext)
            else:
                return self.getTypedRuleContext(MermaidSequenceParser.JsonPairContext,i)


        def RBRACE(self):
            return self.getToken(MermaidSequenceParser.RBRACE, 0)

        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidSequenceParser.COMMA)
            else:
                return self.getToken(MermaidSequenceParser.COMMA, i)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_jsonObject

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitJsonObject" ):
                return visitor.visitJsonObject(self)
            else:
                return visitor.visitChildren(self)




    def jsonObject(self):

        localctx = MermaidSequenceParser.JsonObjectContext(self, self._ctx, self.state)
        self.enterRule(localctx, 82, self.RULE_jsonObject)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 531
            self.match(MermaidSequenceParser.LBRACE)
            self.state = 532
            self.jsonPair()
            self.state = 537
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==37:
                self.state = 533
                self.match(MermaidSequenceParser.COMMA)
                self.state = 534
                self.jsonPair()
                self.state = 539
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 540
            self.match(MermaidSequenceParser.RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class JsonPairContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def QUOTED_STRING(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidSequenceParser.QUOTED_STRING)
            else:
                return self.getToken(MermaidSequenceParser.QUOTED_STRING, i)

        def COLON(self):
            return self.getToken(MermaidSequenceParser.COLON, 0)

        def getRuleIndex(self):
            return MermaidSequenceParser.RULE_jsonPair

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitJsonPair" ):
                return visitor.visitJsonPair(self)
            else:
                return visitor.visitChildren(self)




    def jsonPair(self):

        localctx = MermaidSequenceParser.JsonPairContext(self, self._ctx, self.state)
        self.enterRule(localctx, 84, self.RULE_jsonPair)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 542
            self.match(MermaidSequenceParser.QUOTED_STRING)
            self.state = 543
            self.match(MermaidSequenceParser.COLON)
            self.state = 544
            self.match(MermaidSequenceParser.QUOTED_STRING)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





