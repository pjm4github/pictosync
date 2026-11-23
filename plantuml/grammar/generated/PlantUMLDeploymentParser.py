# Generated from plantuml/grammar/PlantUMLDeployment.g4 by ANTLR 4.13.0
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
        4,1,93,740,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,
        7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,26,7,26,
        2,27,7,27,2,28,7,28,2,29,7,29,2,30,7,30,2,31,7,31,2,32,7,32,2,33,
        7,33,2,34,7,34,2,35,7,35,2,36,7,36,2,37,7,37,2,38,7,38,2,39,7,39,
        2,40,7,40,2,41,7,41,2,42,7,42,2,43,7,43,2,44,7,44,2,45,7,45,2,46,
        7,46,2,47,7,47,2,48,7,48,1,0,5,0,100,8,0,10,0,12,0,103,9,0,1,0,1,
        0,3,0,107,8,0,1,0,4,0,110,8,0,11,0,12,0,111,1,0,5,0,115,8,0,10,0,
        12,0,118,9,0,1,0,1,0,5,0,122,8,0,10,0,12,0,125,9,0,1,0,1,0,1,1,4,
        1,130,8,1,11,1,12,1,131,1,1,1,1,4,1,136,8,1,11,1,12,1,137,5,1,140,
        8,1,10,1,12,1,143,9,1,1,1,3,1,146,8,1,1,2,1,2,4,2,150,8,2,11,2,12,
        2,151,1,2,1,2,1,2,4,2,157,8,2,11,2,12,2,158,1,2,1,2,4,2,163,8,2,
        11,2,12,2,164,1,2,1,2,1,2,1,2,1,2,4,2,172,8,2,11,2,12,2,173,1,2,
        1,2,1,2,4,2,179,8,2,11,2,12,2,180,1,2,1,2,4,2,185,8,2,11,2,12,2,
        186,1,2,1,2,4,2,191,8,2,11,2,12,2,192,1,2,1,2,4,2,197,8,2,11,2,12,
        2,198,1,2,1,2,4,2,203,8,2,11,2,12,2,204,1,2,1,2,4,2,209,8,2,11,2,
        12,2,210,1,2,1,2,4,2,215,8,2,11,2,12,2,216,1,2,1,2,1,2,4,2,222,8,
        2,11,2,12,2,223,1,2,1,2,4,2,228,8,2,11,2,12,2,229,1,2,1,2,4,2,234,
        8,2,11,2,12,2,235,1,2,1,2,4,2,240,8,2,11,2,12,2,241,1,2,4,2,245,
        8,2,11,2,12,2,246,3,2,249,8,2,1,3,1,3,3,3,253,8,3,1,3,5,3,256,8,
        3,10,3,12,3,259,9,3,1,3,1,3,3,3,263,8,3,1,3,5,3,266,8,3,10,3,12,
        3,269,9,3,1,3,1,3,1,3,3,3,274,8,3,1,3,5,3,277,8,3,10,3,12,3,280,
        9,3,1,3,1,3,3,3,284,8,3,1,3,5,3,287,8,3,10,3,12,3,290,9,3,1,3,1,
        3,1,3,3,3,295,8,3,1,3,5,3,298,8,3,10,3,12,3,301,9,3,1,3,3,3,304,
        8,3,3,3,306,8,3,1,4,1,4,1,4,1,4,1,5,1,5,3,5,314,8,5,1,5,3,5,317,
        8,5,1,5,5,5,320,8,5,10,5,12,5,323,9,5,1,5,1,5,4,5,327,8,5,11,5,12,
        5,328,1,5,5,5,332,8,5,10,5,12,5,335,9,5,1,5,1,5,4,5,339,8,5,11,5,
        12,5,340,1,6,1,6,4,6,345,8,6,11,6,12,6,346,1,6,1,6,1,6,4,6,352,8,
        6,11,6,12,6,353,1,6,1,6,4,6,358,8,6,11,6,12,6,359,1,6,1,6,4,6,364,
        8,6,11,6,12,6,365,1,6,1,6,1,6,4,6,371,8,6,11,6,12,6,372,1,6,1,6,
        4,6,377,8,6,11,6,12,6,378,1,6,4,6,382,8,6,11,6,12,6,383,3,6,386,
        8,6,1,7,1,7,1,7,1,7,1,7,1,7,3,7,394,8,7,1,8,1,8,1,8,4,8,399,8,8,
        11,8,12,8,400,1,8,5,8,404,8,8,10,8,12,8,407,9,8,1,8,1,8,4,8,411,
        8,8,11,8,12,8,412,1,9,1,9,1,10,1,10,1,11,1,11,1,11,1,12,1,12,1,12,
        3,12,425,8,12,1,13,1,13,1,14,1,14,1,14,1,14,1,15,3,15,434,8,15,1,
        15,3,15,437,8,15,1,16,1,16,1,16,1,16,1,16,1,16,1,17,1,17,1,18,1,
        18,1,19,3,19,450,8,19,1,20,1,20,1,20,1,20,1,20,1,20,1,20,1,20,1,
        20,1,20,1,20,1,20,1,20,1,20,1,20,1,20,1,20,1,20,1,20,1,20,1,20,1,
        20,1,20,1,20,1,20,1,20,1,20,1,20,1,20,1,20,1,20,1,20,1,20,1,20,4,
        20,486,8,20,11,20,12,20,487,1,21,1,21,1,21,1,21,1,21,3,21,495,8,
        21,1,22,1,22,1,23,1,23,1,24,1,24,1,24,1,24,1,24,1,24,3,24,507,8,
        24,1,24,1,24,1,24,1,24,3,24,513,8,24,1,25,1,25,1,25,1,25,1,25,4,
        25,520,8,25,11,25,12,25,521,1,25,4,25,525,8,25,11,25,12,25,526,1,
        25,1,25,4,25,531,8,25,11,25,12,25,532,1,25,1,25,1,25,1,25,4,25,539,
        8,25,11,25,12,25,540,1,25,4,25,544,8,25,11,25,12,25,545,1,25,1,25,
        4,25,550,8,25,11,25,12,25,551,3,25,554,8,25,1,26,1,26,1,27,1,27,
        4,27,560,8,27,11,27,12,27,561,1,27,4,27,565,8,27,11,27,12,27,566,
        3,27,569,8,27,1,28,1,28,1,28,3,28,574,8,28,1,28,1,28,4,28,578,8,
        28,11,28,12,28,579,1,28,4,28,583,8,28,11,28,12,28,584,1,28,1,28,
        4,28,589,8,28,11,28,12,28,590,1,29,1,29,1,29,1,29,1,29,1,29,3,29,
        599,8,29,1,29,1,29,1,30,1,30,4,30,605,8,30,11,30,12,30,606,1,30,
        4,30,610,8,30,11,30,12,30,611,3,30,614,8,30,1,31,1,31,1,31,3,31,
        619,8,31,1,32,1,32,1,32,1,32,4,32,625,8,32,11,32,12,32,626,1,32,
        5,32,630,8,32,10,32,12,32,633,9,32,1,32,1,32,4,32,637,8,32,11,32,
        12,32,638,1,33,1,33,1,33,5,33,644,8,33,10,33,12,33,647,9,33,1,34,
        1,34,3,34,651,8,34,1,35,1,35,1,35,4,35,656,8,35,11,35,12,35,657,
        1,35,4,35,661,8,35,11,35,12,35,662,3,35,665,8,35,1,36,1,36,1,36,
        1,37,1,37,1,38,1,38,1,39,1,39,1,39,1,39,1,39,1,39,1,39,1,39,3,39,
        682,8,39,1,40,1,40,1,41,1,41,3,41,688,8,41,1,42,1,42,3,42,692,8,
        42,1,43,1,43,3,43,696,8,43,1,44,1,44,3,44,700,8,44,1,45,1,45,3,45,
        704,8,45,1,45,4,45,707,8,45,11,45,12,45,708,1,45,4,45,712,8,45,11,
        45,12,45,713,1,45,1,45,4,45,718,8,45,11,45,12,45,719,1,46,1,46,1,
        47,1,47,1,47,1,47,3,47,728,8,47,1,47,1,47,1,47,3,47,733,8,47,3,47,
        735,8,47,1,48,1,48,1,48,1,48,0,0,49,0,2,4,6,8,10,12,14,16,18,20,
        22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60,62,64,
        66,68,70,72,74,76,78,80,82,84,86,88,90,92,94,96,0,9,1,0,87,88,1,
        0,10,36,2,0,73,73,88,88,2,0,88,88,91,91,3,0,4,6,73,73,88,88,1,0,
        46,49,1,0,51,53,2,0,8,9,83,83,2,0,46,47,62,62,858,0,101,1,0,0,0,
        2,145,1,0,0,0,4,248,1,0,0,0,6,305,1,0,0,0,8,307,1,0,0,0,10,311,1,
        0,0,0,12,385,1,0,0,0,14,393,1,0,0,0,16,395,1,0,0,0,18,414,1,0,0,
        0,20,416,1,0,0,0,22,418,1,0,0,0,24,424,1,0,0,0,26,426,1,0,0,0,28,
        428,1,0,0,0,30,433,1,0,0,0,32,438,1,0,0,0,34,444,1,0,0,0,36,446,
        1,0,0,0,38,449,1,0,0,0,40,485,1,0,0,0,42,489,1,0,0,0,44,496,1,0,
        0,0,46,498,1,0,0,0,48,512,1,0,0,0,50,553,1,0,0,0,52,555,1,0,0,0,
        54,568,1,0,0,0,56,570,1,0,0,0,58,592,1,0,0,0,60,613,1,0,0,0,62,615,
        1,0,0,0,64,620,1,0,0,0,66,640,1,0,0,0,68,650,1,0,0,0,70,664,1,0,
        0,0,72,666,1,0,0,0,74,669,1,0,0,0,76,671,1,0,0,0,78,681,1,0,0,0,
        80,683,1,0,0,0,82,685,1,0,0,0,84,689,1,0,0,0,86,693,1,0,0,0,88,697,
        1,0,0,0,90,701,1,0,0,0,92,721,1,0,0,0,94,734,1,0,0,0,96,736,1,0,
        0,0,98,100,5,92,0,0,99,98,1,0,0,0,100,103,1,0,0,0,101,99,1,0,0,0,
        101,102,1,0,0,0,102,104,1,0,0,0,103,101,1,0,0,0,104,106,5,2,0,0,
        105,107,3,2,1,0,106,105,1,0,0,0,106,107,1,0,0,0,107,109,1,0,0,0,
        108,110,5,92,0,0,109,108,1,0,0,0,110,111,1,0,0,0,111,109,1,0,0,0,
        111,112,1,0,0,0,112,116,1,0,0,0,113,115,3,4,2,0,114,113,1,0,0,0,
        115,118,1,0,0,0,116,114,1,0,0,0,116,117,1,0,0,0,117,119,1,0,0,0,
        118,116,1,0,0,0,119,123,5,3,0,0,120,122,5,92,0,0,121,120,1,0,0,0,
        122,125,1,0,0,0,123,121,1,0,0,0,123,124,1,0,0,0,124,126,1,0,0,0,
        125,123,1,0,0,0,126,127,5,0,0,1,127,1,1,0,0,0,128,130,7,0,0,0,129,
        128,1,0,0,0,130,131,1,0,0,0,131,129,1,0,0,0,131,132,1,0,0,0,132,
        141,1,0,0,0,133,135,5,1,0,0,134,136,7,0,0,0,135,134,1,0,0,0,136,
        137,1,0,0,0,137,135,1,0,0,0,137,138,1,0,0,0,138,140,1,0,0,0,139,
        133,1,0,0,0,140,143,1,0,0,0,141,139,1,0,0,0,141,142,1,0,0,0,142,
        146,1,0,0,0,143,141,1,0,0,0,144,146,5,73,0,0,145,129,1,0,0,0,145,
        144,1,0,0,0,146,3,1,0,0,0,147,149,3,6,3,0,148,150,5,92,0,0,149,148,
        1,0,0,0,150,151,1,0,0,0,151,149,1,0,0,0,151,152,1,0,0,0,152,249,
        1,0,0,0,153,249,3,10,5,0,154,156,3,42,21,0,155,157,5,92,0,0,156,
        155,1,0,0,0,157,158,1,0,0,0,158,156,1,0,0,0,158,159,1,0,0,0,159,
        249,1,0,0,0,160,162,3,48,24,0,161,163,5,92,0,0,162,161,1,0,0,0,163,
        164,1,0,0,0,164,162,1,0,0,0,164,165,1,0,0,0,165,249,1,0,0,0,166,
        249,3,50,25,0,167,249,3,16,8,0,168,249,3,56,28,0,169,171,3,62,31,
        0,170,172,5,92,0,0,171,170,1,0,0,0,172,173,1,0,0,0,173,171,1,0,0,
        0,173,174,1,0,0,0,174,249,1,0,0,0,175,249,3,64,32,0,176,178,3,72,
        36,0,177,179,5,92,0,0,178,177,1,0,0,0,179,180,1,0,0,0,180,178,1,
        0,0,0,180,181,1,0,0,0,181,249,1,0,0,0,182,184,3,78,39,0,183,185,
        5,92,0,0,184,183,1,0,0,0,185,186,1,0,0,0,186,184,1,0,0,0,186,187,
        1,0,0,0,187,249,1,0,0,0,188,190,3,80,40,0,189,191,5,92,0,0,190,189,
        1,0,0,0,191,192,1,0,0,0,192,190,1,0,0,0,192,193,1,0,0,0,193,249,
        1,0,0,0,194,196,3,82,41,0,195,197,5,92,0,0,196,195,1,0,0,0,197,198,
        1,0,0,0,198,196,1,0,0,0,198,199,1,0,0,0,199,249,1,0,0,0,200,202,
        3,84,42,0,201,203,5,92,0,0,202,201,1,0,0,0,203,204,1,0,0,0,204,202,
        1,0,0,0,204,205,1,0,0,0,205,249,1,0,0,0,206,208,3,86,43,0,207,209,
        5,92,0,0,208,207,1,0,0,0,209,210,1,0,0,0,210,208,1,0,0,0,210,211,
        1,0,0,0,211,249,1,0,0,0,212,214,3,88,44,0,213,215,5,92,0,0,214,213,
        1,0,0,0,215,216,1,0,0,0,216,214,1,0,0,0,216,217,1,0,0,0,217,249,
        1,0,0,0,218,249,3,90,45,0,219,221,3,94,47,0,220,222,5,92,0,0,221,
        220,1,0,0,0,222,223,1,0,0,0,223,221,1,0,0,0,223,224,1,0,0,0,224,
        249,1,0,0,0,225,227,3,96,48,0,226,228,5,92,0,0,227,226,1,0,0,0,228,
        229,1,0,0,0,229,227,1,0,0,0,229,230,1,0,0,0,230,249,1,0,0,0,231,
        233,5,89,0,0,232,234,5,92,0,0,233,232,1,0,0,0,234,235,1,0,0,0,235,
        233,1,0,0,0,235,236,1,0,0,0,236,249,1,0,0,0,237,239,5,90,0,0,238,
        240,5,92,0,0,239,238,1,0,0,0,240,241,1,0,0,0,241,239,1,0,0,0,241,
        242,1,0,0,0,242,249,1,0,0,0,243,245,5,92,0,0,244,243,1,0,0,0,245,
        246,1,0,0,0,246,244,1,0,0,0,246,247,1,0,0,0,247,249,1,0,0,0,248,
        147,1,0,0,0,248,153,1,0,0,0,248,154,1,0,0,0,248,160,1,0,0,0,248,
        166,1,0,0,0,248,167,1,0,0,0,248,168,1,0,0,0,248,169,1,0,0,0,248,
        175,1,0,0,0,248,176,1,0,0,0,248,182,1,0,0,0,248,188,1,0,0,0,248,
        194,1,0,0,0,248,200,1,0,0,0,248,206,1,0,0,0,248,212,1,0,0,0,248,
        218,1,0,0,0,248,219,1,0,0,0,248,225,1,0,0,0,248,231,1,0,0,0,248,
        237,1,0,0,0,248,244,1,0,0,0,249,5,1,0,0,0,250,252,5,4,0,0,251,253,
        3,22,11,0,252,251,1,0,0,0,252,253,1,0,0,0,253,257,1,0,0,0,254,256,
        3,24,12,0,255,254,1,0,0,0,256,259,1,0,0,0,257,255,1,0,0,0,257,258,
        1,0,0,0,258,306,1,0,0,0,259,257,1,0,0,0,260,262,5,5,0,0,261,263,
        3,22,11,0,262,261,1,0,0,0,262,263,1,0,0,0,263,267,1,0,0,0,264,266,
        3,24,12,0,265,264,1,0,0,0,266,269,1,0,0,0,267,265,1,0,0,0,267,268,
        1,0,0,0,268,306,1,0,0,0,269,267,1,0,0,0,270,271,5,7,0,0,271,273,
        3,20,10,0,272,274,3,22,11,0,273,272,1,0,0,0,273,274,1,0,0,0,274,
        278,1,0,0,0,275,277,3,24,12,0,276,275,1,0,0,0,277,280,1,0,0,0,278,
        276,1,0,0,0,278,279,1,0,0,0,279,306,1,0,0,0,280,278,1,0,0,0,281,
        283,5,6,0,0,282,284,3,22,11,0,283,282,1,0,0,0,283,284,1,0,0,0,284,
        288,1,0,0,0,285,287,3,24,12,0,286,285,1,0,0,0,287,290,1,0,0,0,288,
        286,1,0,0,0,288,289,1,0,0,0,289,306,1,0,0,0,290,288,1,0,0,0,291,
        292,3,18,9,0,292,294,3,20,10,0,293,295,3,22,11,0,294,293,1,0,0,0,
        294,295,1,0,0,0,295,299,1,0,0,0,296,298,3,24,12,0,297,296,1,0,0,
        0,298,301,1,0,0,0,299,297,1,0,0,0,299,300,1,0,0,0,300,303,1,0,0,
        0,301,299,1,0,0,0,302,304,3,8,4,0,303,302,1,0,0,0,303,304,1,0,0,
        0,304,306,1,0,0,0,305,250,1,0,0,0,305,260,1,0,0,0,305,270,1,0,0,
        0,305,281,1,0,0,0,305,291,1,0,0,0,306,7,1,0,0,0,307,308,5,76,0,0,
        308,309,3,38,19,0,309,310,5,77,0,0,310,9,1,0,0,0,311,313,3,18,9,
        0,312,314,3,20,10,0,313,312,1,0,0,0,313,314,1,0,0,0,314,316,1,0,
        0,0,315,317,3,22,11,0,316,315,1,0,0,0,316,317,1,0,0,0,317,321,1,
        0,0,0,318,320,3,24,12,0,319,318,1,0,0,0,320,323,1,0,0,0,321,319,
        1,0,0,0,321,322,1,0,0,0,322,324,1,0,0,0,323,321,1,0,0,0,324,326,
        5,78,0,0,325,327,5,92,0,0,326,325,1,0,0,0,327,328,1,0,0,0,328,326,
        1,0,0,0,328,329,1,0,0,0,329,333,1,0,0,0,330,332,3,12,6,0,331,330,
        1,0,0,0,332,335,1,0,0,0,333,331,1,0,0,0,333,334,1,0,0,0,334,336,
        1,0,0,0,335,333,1,0,0,0,336,338,5,79,0,0,337,339,5,92,0,0,338,337,
        1,0,0,0,339,340,1,0,0,0,340,338,1,0,0,0,340,341,1,0,0,0,341,11,1,
        0,0,0,342,344,3,6,3,0,343,345,5,92,0,0,344,343,1,0,0,0,345,346,1,
        0,0,0,346,344,1,0,0,0,346,347,1,0,0,0,347,386,1,0,0,0,348,386,3,
        10,5,0,349,351,3,14,7,0,350,352,5,92,0,0,351,350,1,0,0,0,352,353,
        1,0,0,0,353,351,1,0,0,0,353,354,1,0,0,0,354,386,1,0,0,0,355,357,
        3,42,21,0,356,358,5,92,0,0,357,356,1,0,0,0,358,359,1,0,0,0,359,357,
        1,0,0,0,359,360,1,0,0,0,360,386,1,0,0,0,361,363,3,48,24,0,362,364,
        5,92,0,0,363,362,1,0,0,0,364,365,1,0,0,0,365,363,1,0,0,0,365,366,
        1,0,0,0,366,386,1,0,0,0,367,386,3,50,25,0,368,370,5,89,0,0,369,371,
        5,92,0,0,370,369,1,0,0,0,371,372,1,0,0,0,372,370,1,0,0,0,372,373,
        1,0,0,0,373,386,1,0,0,0,374,376,5,90,0,0,375,377,5,92,0,0,376,375,
        1,0,0,0,377,378,1,0,0,0,378,376,1,0,0,0,378,379,1,0,0,0,379,386,
        1,0,0,0,380,382,5,92,0,0,381,380,1,0,0,0,382,383,1,0,0,0,383,381,
        1,0,0,0,383,384,1,0,0,0,384,386,1,0,0,0,385,342,1,0,0,0,385,348,
        1,0,0,0,385,349,1,0,0,0,385,355,1,0,0,0,385,361,1,0,0,0,385,367,
        1,0,0,0,385,368,1,0,0,0,385,374,1,0,0,0,385,381,1,0,0,0,386,13,1,
        0,0,0,387,388,5,37,0,0,388,394,3,20,10,0,389,390,5,38,0,0,390,394,
        3,20,10,0,391,392,5,39,0,0,392,394,3,20,10,0,393,387,1,0,0,0,393,
        389,1,0,0,0,393,391,1,0,0,0,394,15,1,0,0,0,395,396,5,41,0,0,396,
        398,5,78,0,0,397,399,5,92,0,0,398,397,1,0,0,0,399,400,1,0,0,0,400,
        398,1,0,0,0,400,401,1,0,0,0,401,405,1,0,0,0,402,404,3,4,2,0,403,
        402,1,0,0,0,404,407,1,0,0,0,405,403,1,0,0,0,405,406,1,0,0,0,406,
        408,1,0,0,0,407,405,1,0,0,0,408,410,5,79,0,0,409,411,5,92,0,0,410,
        409,1,0,0,0,411,412,1,0,0,0,412,410,1,0,0,0,412,413,1,0,0,0,413,
        17,1,0,0,0,414,415,7,1,0,0,415,19,1,0,0,0,416,417,7,2,0,0,417,21,
        1,0,0,0,418,419,5,40,0,0,419,420,3,20,10,0,420,23,1,0,0,0,421,425,
        3,28,14,0,422,425,3,26,13,0,423,425,5,8,0,0,424,421,1,0,0,0,424,
        422,1,0,0,0,424,423,1,0,0,0,425,25,1,0,0,0,426,427,5,71,0,0,427,
        27,1,0,0,0,428,429,5,68,0,0,429,430,3,30,15,0,430,431,5,69,0,0,431,
        29,1,0,0,0,432,434,3,32,16,0,433,432,1,0,0,0,433,434,1,0,0,0,434,
        436,1,0,0,0,435,437,3,36,18,0,436,435,1,0,0,0,436,437,1,0,0,0,437,
        31,1,0,0,0,438,439,5,74,0,0,439,440,3,34,17,0,440,441,5,82,0,0,441,
        442,3,26,13,0,442,443,5,75,0,0,443,33,1,0,0,0,444,445,7,0,0,0,445,
        35,1,0,0,0,446,447,7,3,0,0,447,37,1,0,0,0,448,450,3,40,20,0,449,
        448,1,0,0,0,449,450,1,0,0,0,450,39,1,0,0,0,451,486,5,88,0,0,452,
        486,5,73,0,0,453,486,5,87,0,0,454,486,5,71,0,0,455,486,5,8,0,0,456,
        486,5,91,0,0,457,486,5,81,0,0,458,486,5,82,0,0,459,486,5,83,0,0,
        460,486,5,84,0,0,461,486,5,80,0,0,462,486,5,74,0,0,463,486,5,75,
        0,0,464,486,5,76,0,0,465,486,5,77,0,0,466,486,5,85,0,0,467,486,5,
        86,0,0,468,486,5,68,0,0,469,486,5,69,0,0,470,486,5,4,0,0,471,486,
        5,5,0,0,472,486,5,6,0,0,473,486,5,70,0,0,474,486,5,40,0,0,475,486,
        5,50,0,0,476,486,5,54,0,0,477,486,5,46,0,0,478,486,5,47,0,0,479,
        486,5,48,0,0,480,486,5,49,0,0,481,486,5,62,0,0,482,486,5,67,0,0,
        483,486,5,55,0,0,484,486,3,18,9,0,485,451,1,0,0,0,485,452,1,0,0,
        0,485,453,1,0,0,0,485,454,1,0,0,0,485,455,1,0,0,0,485,456,1,0,0,
        0,485,457,1,0,0,0,485,458,1,0,0,0,485,459,1,0,0,0,485,460,1,0,0,
        0,485,461,1,0,0,0,485,462,1,0,0,0,485,463,1,0,0,0,485,464,1,0,0,
        0,485,465,1,0,0,0,485,466,1,0,0,0,485,467,1,0,0,0,485,468,1,0,0,
        0,485,469,1,0,0,0,485,470,1,0,0,0,485,471,1,0,0,0,485,472,1,0,0,
        0,485,473,1,0,0,0,485,474,1,0,0,0,485,475,1,0,0,0,485,476,1,0,0,
        0,485,477,1,0,0,0,485,478,1,0,0,0,485,479,1,0,0,0,485,480,1,0,0,
        0,485,481,1,0,0,0,485,482,1,0,0,0,485,483,1,0,0,0,485,484,1,0,0,
        0,486,487,1,0,0,0,487,485,1,0,0,0,487,488,1,0,0,0,488,41,1,0,0,0,
        489,490,3,44,22,0,490,491,5,70,0,0,491,494,3,44,22,0,492,493,5,81,
        0,0,493,495,3,46,23,0,494,492,1,0,0,0,494,495,1,0,0,0,495,43,1,0,
        0,0,496,497,7,4,0,0,497,45,1,0,0,0,498,499,3,40,20,0,499,47,1,0,
        0,0,500,501,5,45,0,0,501,502,3,52,26,0,502,503,5,50,0,0,503,506,
        3,44,22,0,504,505,5,81,0,0,505,507,3,40,20,0,506,504,1,0,0,0,506,
        507,1,0,0,0,507,513,1,0,0,0,508,509,5,45,0,0,509,510,5,73,0,0,510,
        511,5,40,0,0,511,513,3,20,10,0,512,500,1,0,0,0,512,508,1,0,0,0,513,
        49,1,0,0,0,514,515,5,45,0,0,515,516,3,52,26,0,516,517,5,50,0,0,517,
        519,3,44,22,0,518,520,5,92,0,0,519,518,1,0,0,0,520,521,1,0,0,0,521,
        519,1,0,0,0,521,522,1,0,0,0,522,524,1,0,0,0,523,525,3,54,27,0,524,
        523,1,0,0,0,525,526,1,0,0,0,526,524,1,0,0,0,526,527,1,0,0,0,527,
        528,1,0,0,0,528,530,5,42,0,0,529,531,5,92,0,0,530,529,1,0,0,0,531,
        532,1,0,0,0,532,530,1,0,0,0,532,533,1,0,0,0,533,554,1,0,0,0,534,
        535,5,45,0,0,535,536,5,40,0,0,536,538,3,20,10,0,537,539,5,92,0,0,
        538,537,1,0,0,0,539,540,1,0,0,0,540,538,1,0,0,0,540,541,1,0,0,0,
        541,543,1,0,0,0,542,544,3,54,27,0,543,542,1,0,0,0,544,545,1,0,0,
        0,545,543,1,0,0,0,545,546,1,0,0,0,546,547,1,0,0,0,547,549,5,42,0,
        0,548,550,5,92,0,0,549,548,1,0,0,0,550,551,1,0,0,0,551,549,1,0,0,
        0,551,552,1,0,0,0,552,554,1,0,0,0,553,514,1,0,0,0,553,534,1,0,0,
        0,554,51,1,0,0,0,555,556,7,5,0,0,556,53,1,0,0,0,557,559,3,40,20,
        0,558,560,5,92,0,0,559,558,1,0,0,0,560,561,1,0,0,0,561,559,1,0,0,
        0,561,562,1,0,0,0,562,569,1,0,0,0,563,565,5,92,0,0,564,563,1,0,0,
        0,565,566,1,0,0,0,566,564,1,0,0,0,566,567,1,0,0,0,567,569,1,0,0,
        0,568,557,1,0,0,0,568,564,1,0,0,0,569,55,1,0,0,0,570,571,5,66,0,
        0,571,573,5,8,0,0,572,574,3,58,29,0,573,572,1,0,0,0,573,574,1,0,
        0,0,574,575,1,0,0,0,575,577,5,78,0,0,576,578,5,92,0,0,577,576,1,
        0,0,0,578,579,1,0,0,0,579,577,1,0,0,0,579,580,1,0,0,0,580,582,1,
        0,0,0,581,583,3,60,30,0,582,581,1,0,0,0,583,584,1,0,0,0,584,582,
        1,0,0,0,584,585,1,0,0,0,585,586,1,0,0,0,586,588,5,79,0,0,587,589,
        5,92,0,0,588,587,1,0,0,0,589,590,1,0,0,0,590,588,1,0,0,0,590,591,
        1,0,0,0,591,57,1,0,0,0,592,593,5,76,0,0,593,594,5,87,0,0,594,595,
        5,67,0,0,595,598,5,87,0,0,596,597,5,80,0,0,597,599,5,87,0,0,598,
        596,1,0,0,0,598,599,1,0,0,0,599,600,1,0,0,0,600,601,5,77,0,0,601,
        59,1,0,0,0,602,604,5,72,0,0,603,605,5,92,0,0,604,603,1,0,0,0,605,
        606,1,0,0,0,606,604,1,0,0,0,606,607,1,0,0,0,607,614,1,0,0,0,608,
        610,5,92,0,0,609,608,1,0,0,0,610,611,1,0,0,0,611,609,1,0,0,0,611,
        612,1,0,0,0,612,614,1,0,0,0,613,602,1,0,0,0,613,609,1,0,0,0,614,
        61,1,0,0,0,615,616,5,63,0,0,616,618,3,66,33,0,617,619,3,40,20,0,
        618,617,1,0,0,0,618,619,1,0,0,0,619,63,1,0,0,0,620,621,5,63,0,0,
        621,622,3,66,33,0,622,624,5,78,0,0,623,625,5,92,0,0,624,623,1,0,
        0,0,625,626,1,0,0,0,626,624,1,0,0,0,626,627,1,0,0,0,627,631,1,0,
        0,0,628,630,3,70,35,0,629,628,1,0,0,0,630,633,1,0,0,0,631,629,1,
        0,0,0,631,632,1,0,0,0,632,634,1,0,0,0,633,631,1,0,0,0,634,636,5,
        79,0,0,635,637,5,92,0,0,636,635,1,0,0,0,637,638,1,0,0,0,638,636,
        1,0,0,0,638,639,1,0,0,0,639,65,1,0,0,0,640,645,3,68,34,0,641,642,
        5,1,0,0,642,644,3,68,34,0,643,641,1,0,0,0,644,647,1,0,0,0,645,643,
        1,0,0,0,645,646,1,0,0,0,646,67,1,0,0,0,647,645,1,0,0,0,648,651,5,
        88,0,0,649,651,3,18,9,0,650,648,1,0,0,0,650,649,1,0,0,0,651,69,1,
        0,0,0,652,653,3,68,34,0,653,655,3,40,20,0,654,656,5,92,0,0,655,654,
        1,0,0,0,656,657,1,0,0,0,657,655,1,0,0,0,657,658,1,0,0,0,658,665,
        1,0,0,0,659,661,5,92,0,0,660,659,1,0,0,0,661,662,1,0,0,0,662,660,
        1,0,0,0,662,663,1,0,0,0,663,665,1,0,0,0,664,652,1,0,0,0,664,660,
        1,0,0,0,665,71,1,0,0,0,666,667,3,74,37,0,667,668,3,76,38,0,668,73,
        1,0,0,0,669,670,7,6,0,0,670,75,1,0,0,0,671,672,7,7,0,0,672,77,1,
        0,0,0,673,674,5,46,0,0,674,675,5,54,0,0,675,676,5,47,0,0,676,682,
        5,55,0,0,677,678,5,48,0,0,678,679,5,54,0,0,679,680,5,49,0,0,680,
        682,5,55,0,0,681,673,1,0,0,0,681,677,1,0,0,0,682,79,1,0,0,0,683,
        684,5,56,0,0,684,81,1,0,0,0,685,687,5,57,0,0,686,688,3,40,20,0,687,
        686,1,0,0,0,687,688,1,0,0,0,688,83,1,0,0,0,689,691,5,58,0,0,690,
        692,3,40,20,0,691,690,1,0,0,0,691,692,1,0,0,0,692,85,1,0,0,0,693,
        695,5,59,0,0,694,696,3,40,20,0,695,694,1,0,0,0,695,696,1,0,0,0,696,
        87,1,0,0,0,697,699,5,60,0,0,698,700,3,40,20,0,699,698,1,0,0,0,699,
        700,1,0,0,0,700,89,1,0,0,0,701,703,5,61,0,0,702,704,3,92,46,0,703,
        702,1,0,0,0,703,704,1,0,0,0,704,706,1,0,0,0,705,707,5,92,0,0,706,
        705,1,0,0,0,707,708,1,0,0,0,708,706,1,0,0,0,708,709,1,0,0,0,709,
        711,1,0,0,0,710,712,3,54,27,0,711,710,1,0,0,0,712,713,1,0,0,0,713,
        711,1,0,0,0,713,714,1,0,0,0,714,715,1,0,0,0,715,717,5,43,0,0,716,
        718,5,92,0,0,717,716,1,0,0,0,718,719,1,0,0,0,719,717,1,0,0,0,719,
        720,1,0,0,0,720,91,1,0,0,0,721,722,7,8,0,0,722,93,1,0,0,0,723,724,
        5,84,0,0,724,725,5,64,0,0,725,727,5,88,0,0,726,728,3,40,20,0,727,
        726,1,0,0,0,727,728,1,0,0,0,728,735,1,0,0,0,729,730,5,84,0,0,730,
        732,5,88,0,0,731,733,3,40,20,0,732,731,1,0,0,0,732,733,1,0,0,0,733,
        735,1,0,0,0,734,723,1,0,0,0,734,729,1,0,0,0,735,95,1,0,0,0,736,737,
        5,65,0,0,737,738,3,40,20,0,738,97,1,0,0,0,104,101,106,111,116,123,
        131,137,141,145,151,158,164,173,180,186,192,198,204,210,216,223,
        229,235,241,246,248,252,257,262,267,273,278,283,288,294,299,303,
        305,313,316,321,328,333,340,346,353,359,365,372,378,383,385,393,
        400,405,412,424,433,436,449,485,487,494,506,512,521,526,532,540,
        545,551,553,561,566,568,573,579,584,590,598,606,611,613,618,626,
        631,638,645,650,657,662,664,681,687,691,695,699,703,708,713,719,
        727,732,734
    ]

class PlantUMLDeploymentParser ( Parser ):

    grammarFileName = "PlantUMLDeployment.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'.'", "'@startuml'", "'@enduml'", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "'()'", "<INVALID>", "'@unlinked'", 
                     "'actor'", "'agent'", "'artifact'", "'boundary'", "'card'", 
                     "'circle'", "'cloud'", "'collections'", "'component'", 
                     "'control'", "'database'", "'entity'", "'file'", "'folder'", 
                     "'frame'", "'hexagon'", "'interface'", "'label'", "'node'", 
                     "'package'", "'person'", "'process'", "'queue'", "'rectangle'", 
                     "'stack'", "'storage'", "'usecase'", "'port'", "'portin'", 
                     "'portout'", "'as'", "'together'", "<INVALID>", "<INVALID>", 
                     "'end'", "'note'", "'left'", "'right'", "'top'", "'bottom'", 
                     "'of'", "'hide'", "'remove'", "'restore'", "'to'", 
                     "'direction'", "'allowmixing'", "'title'", "'header'", 
                     "'footer'", "'caption'", "'legend'", "'center'", "'skinparam'", 
                     "'pragma'", "'scale'", "'sprite'", "'x'", "'<<'", "'>>'", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "'('", "')'", "'['", "']'", "'{'", "'}'", "'/'", "':'", 
                     "','", "'*'", "'!'", "'@'", "'$'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "STARTUML", "ENDUML", "BRACKET_COMP", 
                      "ACTOR_COLON", "USECASE_PAREN", "CIRCLE_IFACE", "TAG", 
                      "AT_UNLINKED", "KW_ACTOR", "KW_AGENT", "KW_ARTIFACT", 
                      "KW_BOUNDARY", "KW_CARD", "KW_CIRCLE", "KW_CLOUD", 
                      "KW_COLLECTIONS", "KW_COMPONENT", "KW_CONTROL", "KW_DATABASE", 
                      "KW_ENTITY", "KW_FILE", "KW_FOLDER", "KW_FRAME", "KW_HEXAGON", 
                      "KW_INTERFACE", "KW_LABEL", "KW_NODE", "KW_PACKAGE", 
                      "KW_PERSON", "KW_PROCESS", "KW_QUEUE", "KW_RECTANGLE", 
                      "KW_STACK", "KW_STORAGE", "KW_USECASE", "KW_PORT", 
                      "KW_PORTIN", "KW_PORTOUT", "KW_AS", "KW_TOGETHER", 
                      "KW_END_NOTE", "KW_END_LEGEND", "KW_END", "KW_NOTE", 
                      "KW_LEFT", "KW_RIGHT", "KW_TOP", "KW_BOTTOM", "KW_OF", 
                      "KW_HIDE", "KW_REMOVE", "KW_RESTORE", "KW_TO", "KW_DIRECTION", 
                      "KW_ALLOWMIXING", "KW_TITLE", "KW_HEADER", "KW_FOOTER", 
                      "KW_CAPTION", "KW_LEGEND", "KW_CENTER", "KW_SKINPARAM", 
                      "KW_PRAGMA", "KW_SCALE", "KW_SPRITE", "KW_X", "STEREOTYPE_OPEN", 
                      "STEREOTYPE_CLOSE", "ARROW_SPEC", "COLOR", "SPRITE_ROW", 
                      "QUOTED_STRING", "LPAREN", "RPAREN", "LBRACK", "RBRACK", 
                      "LBRACE", "RBRACE", "FSLASH", "COLON", "COMMA", "STAR", 
                      "BANG", "AT", "DOLLAR", "INT", "ID", "COMMENT_SINGLE", 
                      "COMMENT_MULTI", "FREE_TEXT", "NEWLINE", "WS" ]

    RULE_diagram = 0
    RULE_filenameHint = 1
    RULE_statement = 2
    RULE_elementDecl = 3
    RULE_descriptionBody = 4
    RULE_elementBlock = 5
    RULE_blockStatement = 6
    RULE_portDecl = 7
    RULE_togetherBlock = 8
    RULE_elementKeyword = 9
    RULE_elementName = 10
    RULE_aliasClause = 11
    RULE_elementModifier = 12
    RULE_colorSpec = 13
    RULE_stereotypeClause = 14
    RULE_stereotypeBody = 15
    RULE_spotSpec = 16
    RULE_spotChar = 17
    RULE_stereotypeText = 18
    RULE_bodyText = 19
    RULE_restOfLine = 20
    RULE_relationStmt = 21
    RULE_relationRef = 22
    RULE_labelText = 23
    RULE_noteStmt = 24
    RULE_noteBlock = 25
    RULE_noteSide = 26
    RULE_noteBodyLine = 27
    RULE_spriteDecl = 28
    RULE_spriteDimension = 29
    RULE_spriteRow = 30
    RULE_skinparamStmt = 31
    RULE_skinparamBlock = 32
    RULE_skinparamPath = 33
    RULE_skinparamWord = 34
    RULE_skinparamEntry = 35
    RULE_visibilityStmt = 36
    RULE_visibilityKeyword = 37
    RULE_visibilityTarget = 38
    RULE_directionStmt = 39
    RULE_allowMixingStmt = 40
    RULE_titleStmt = 41
    RULE_headerStmt = 42
    RULE_footerStmt = 43
    RULE_captionStmt = 44
    RULE_legendBlock = 45
    RULE_legendAlign = 46
    RULE_pragmaStmt = 47
    RULE_scaleStmt = 48

    ruleNames =  [ "diagram", "filenameHint", "statement", "elementDecl", 
                   "descriptionBody", "elementBlock", "blockStatement", 
                   "portDecl", "togetherBlock", "elementKeyword", "elementName", 
                   "aliasClause", "elementModifier", "colorSpec", "stereotypeClause", 
                   "stereotypeBody", "spotSpec", "spotChar", "stereotypeText", 
                   "bodyText", "restOfLine", "relationStmt", "relationRef", 
                   "labelText", "noteStmt", "noteBlock", "noteSide", "noteBodyLine", 
                   "spriteDecl", "spriteDimension", "spriteRow", "skinparamStmt", 
                   "skinparamBlock", "skinparamPath", "skinparamWord", "skinparamEntry", 
                   "visibilityStmt", "visibilityKeyword", "visibilityTarget", 
                   "directionStmt", "allowMixingStmt", "titleStmt", "headerStmt", 
                   "footerStmt", "captionStmt", "legendBlock", "legendAlign", 
                   "pragmaStmt", "scaleStmt" ]

    EOF = Token.EOF
    T__0=1
    STARTUML=2
    ENDUML=3
    BRACKET_COMP=4
    ACTOR_COLON=5
    USECASE_PAREN=6
    CIRCLE_IFACE=7
    TAG=8
    AT_UNLINKED=9
    KW_ACTOR=10
    KW_AGENT=11
    KW_ARTIFACT=12
    KW_BOUNDARY=13
    KW_CARD=14
    KW_CIRCLE=15
    KW_CLOUD=16
    KW_COLLECTIONS=17
    KW_COMPONENT=18
    KW_CONTROL=19
    KW_DATABASE=20
    KW_ENTITY=21
    KW_FILE=22
    KW_FOLDER=23
    KW_FRAME=24
    KW_HEXAGON=25
    KW_INTERFACE=26
    KW_LABEL=27
    KW_NODE=28
    KW_PACKAGE=29
    KW_PERSON=30
    KW_PROCESS=31
    KW_QUEUE=32
    KW_RECTANGLE=33
    KW_STACK=34
    KW_STORAGE=35
    KW_USECASE=36
    KW_PORT=37
    KW_PORTIN=38
    KW_PORTOUT=39
    KW_AS=40
    KW_TOGETHER=41
    KW_END_NOTE=42
    KW_END_LEGEND=43
    KW_END=44
    KW_NOTE=45
    KW_LEFT=46
    KW_RIGHT=47
    KW_TOP=48
    KW_BOTTOM=49
    KW_OF=50
    KW_HIDE=51
    KW_REMOVE=52
    KW_RESTORE=53
    KW_TO=54
    KW_DIRECTION=55
    KW_ALLOWMIXING=56
    KW_TITLE=57
    KW_HEADER=58
    KW_FOOTER=59
    KW_CAPTION=60
    KW_LEGEND=61
    KW_CENTER=62
    KW_SKINPARAM=63
    KW_PRAGMA=64
    KW_SCALE=65
    KW_SPRITE=66
    KW_X=67
    STEREOTYPE_OPEN=68
    STEREOTYPE_CLOSE=69
    ARROW_SPEC=70
    COLOR=71
    SPRITE_ROW=72
    QUOTED_STRING=73
    LPAREN=74
    RPAREN=75
    LBRACK=76
    RBRACK=77
    LBRACE=78
    RBRACE=79
    FSLASH=80
    COLON=81
    COMMA=82
    STAR=83
    BANG=84
    AT=85
    DOLLAR=86
    INT=87
    ID=88
    COMMENT_SINGLE=89
    COMMENT_MULTI=90
    FREE_TEXT=91
    NEWLINE=92
    WS=93

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

        def STARTUML(self):
            return self.getToken(PlantUMLDeploymentParser.STARTUML, 0)

        def ENDUML(self):
            return self.getToken(PlantUMLDeploymentParser.ENDUML, 0)

        def EOF(self):
            return self.getToken(PlantUMLDeploymentParser.EOF, 0)

        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.NEWLINE)
            else:
                return self.getToken(PlantUMLDeploymentParser.NEWLINE, i)

        def filenameHint(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.FilenameHintContext,0)


        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PlantUMLDeploymentParser.StatementContext)
            else:
                return self.getTypedRuleContext(PlantUMLDeploymentParser.StatementContext,i)


        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_diagram

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDiagram" ):
                return visitor.visitDiagram(self)
            else:
                return visitor.visitChildren(self)




    def diagram(self):

        localctx = PlantUMLDeploymentParser.DiagramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_diagram)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 101
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==92:
                self.state = 98
                self.match(PlantUMLDeploymentParser.NEWLINE)
                self.state = 103
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 104
            self.match(PlantUMLDeploymentParser.STARTUML)
            self.state = 106
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if ((((_la - 73)) & ~0x3f) == 0 and ((1 << (_la - 73)) & 49153) != 0):
                self.state = 105
                self.filenameHint()


            self.state = 109 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 108
                    self.match(PlantUMLDeploymentParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 111 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,2,self._ctx)

            self.state = 116
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & -4667591649214333712) != 0) or ((((_la - 65)) & ~0x3f) == 0 and ((1 << (_la - 65)) & 193462531) != 0):
                self.state = 113
                self.statement()
                self.state = 118
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 119
            self.match(PlantUMLDeploymentParser.ENDUML)
            self.state = 123
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==92:
                self.state = 120
                self.match(PlantUMLDeploymentParser.NEWLINE)
                self.state = 125
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 126
            self.match(PlantUMLDeploymentParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FilenameHintContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.ID)
            else:
                return self.getToken(PlantUMLDeploymentParser.ID, i)

        def INT(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.INT)
            else:
                return self.getToken(PlantUMLDeploymentParser.INT, i)

        def QUOTED_STRING(self):
            return self.getToken(PlantUMLDeploymentParser.QUOTED_STRING, 0)

        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_filenameHint

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFilenameHint" ):
                return visitor.visitFilenameHint(self)
            else:
                return visitor.visitChildren(self)




    def filenameHint(self):

        localctx = PlantUMLDeploymentParser.FilenameHintContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_filenameHint)
        self._la = 0 # Token type
        try:
            self.state = 145
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [87, 88]:
                self.enterOuterAlt(localctx, 1)
                self.state = 129 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 128
                    _la = self._input.LA(1)
                    if not(_la==87 or _la==88):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()
                    self.state = 131 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==87 or _la==88):
                        break

                self.state = 141
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==1:
                    self.state = 133
                    self.match(PlantUMLDeploymentParser.T__0)
                    self.state = 135 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    while True:
                        self.state = 134
                        _la = self._input.LA(1)
                        if not(_la==87 or _la==88):
                            self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 137 
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        if not (_la==87 or _la==88):
                            break

                    self.state = 143
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass
            elif token in [73]:
                self.enterOuterAlt(localctx, 2)
                self.state = 144
                self.match(PlantUMLDeploymentParser.QUOTED_STRING)
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


    class StatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def elementDecl(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.ElementDeclContext,0)


        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.NEWLINE)
            else:
                return self.getToken(PlantUMLDeploymentParser.NEWLINE, i)

        def elementBlock(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.ElementBlockContext,0)


        def relationStmt(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.RelationStmtContext,0)


        def noteStmt(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.NoteStmtContext,0)


        def noteBlock(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.NoteBlockContext,0)


        def togetherBlock(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.TogetherBlockContext,0)


        def spriteDecl(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.SpriteDeclContext,0)


        def skinparamStmt(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.SkinparamStmtContext,0)


        def skinparamBlock(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.SkinparamBlockContext,0)


        def visibilityStmt(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.VisibilityStmtContext,0)


        def directionStmt(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.DirectionStmtContext,0)


        def allowMixingStmt(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.AllowMixingStmtContext,0)


        def titleStmt(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.TitleStmtContext,0)


        def headerStmt(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.HeaderStmtContext,0)


        def footerStmt(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.FooterStmtContext,0)


        def captionStmt(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.CaptionStmtContext,0)


        def legendBlock(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.LegendBlockContext,0)


        def pragmaStmt(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.PragmaStmtContext,0)


        def scaleStmt(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.ScaleStmtContext,0)


        def COMMENT_SINGLE(self):
            return self.getToken(PlantUMLDeploymentParser.COMMENT_SINGLE, 0)

        def COMMENT_MULTI(self):
            return self.getToken(PlantUMLDeploymentParser.COMMENT_MULTI, 0)

        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_statement

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStatement" ):
                return visitor.visitStatement(self)
            else:
                return visitor.visitChildren(self)




    def statement(self):

        localctx = PlantUMLDeploymentParser.StatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_statement)
        try:
            self.state = 248
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,25,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 147
                self.elementDecl()
                self.state = 149 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 148
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 151 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,9,self._ctx)

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 153
                self.elementBlock()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 154
                self.relationStmt()
                self.state = 156 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 155
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 158 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,10,self._ctx)

                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 160
                self.noteStmt()
                self.state = 162 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 161
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 164 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,11,self._ctx)

                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 166
                self.noteBlock()
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 167
                self.togetherBlock()
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 168
                self.spriteDecl()
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 169
                self.skinparamStmt()
                self.state = 171 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 170
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 173 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,12,self._ctx)

                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 175
                self.skinparamBlock()
                pass

            elif la_ == 10:
                self.enterOuterAlt(localctx, 10)
                self.state = 176
                self.visibilityStmt()
                self.state = 178 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 177
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 180 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,13,self._ctx)

                pass

            elif la_ == 11:
                self.enterOuterAlt(localctx, 11)
                self.state = 182
                self.directionStmt()
                self.state = 184 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 183
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 186 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,14,self._ctx)

                pass

            elif la_ == 12:
                self.enterOuterAlt(localctx, 12)
                self.state = 188
                self.allowMixingStmt()
                self.state = 190 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 189
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 192 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,15,self._ctx)

                pass

            elif la_ == 13:
                self.enterOuterAlt(localctx, 13)
                self.state = 194
                self.titleStmt()
                self.state = 196 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 195
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 198 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,16,self._ctx)

                pass

            elif la_ == 14:
                self.enterOuterAlt(localctx, 14)
                self.state = 200
                self.headerStmt()
                self.state = 202 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 201
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 204 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,17,self._ctx)

                pass

            elif la_ == 15:
                self.enterOuterAlt(localctx, 15)
                self.state = 206
                self.footerStmt()
                self.state = 208 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 207
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 210 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,18,self._ctx)

                pass

            elif la_ == 16:
                self.enterOuterAlt(localctx, 16)
                self.state = 212
                self.captionStmt()
                self.state = 214 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 213
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 216 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,19,self._ctx)

                pass

            elif la_ == 17:
                self.enterOuterAlt(localctx, 17)
                self.state = 218
                self.legendBlock()
                pass

            elif la_ == 18:
                self.enterOuterAlt(localctx, 18)
                self.state = 219
                self.pragmaStmt()
                self.state = 221 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 220
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 223 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,20,self._ctx)

                pass

            elif la_ == 19:
                self.enterOuterAlt(localctx, 19)
                self.state = 225
                self.scaleStmt()
                self.state = 227 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 226
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 229 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,21,self._ctx)

                pass

            elif la_ == 20:
                self.enterOuterAlt(localctx, 20)
                self.state = 231
                self.match(PlantUMLDeploymentParser.COMMENT_SINGLE)
                self.state = 233 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 232
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 235 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,22,self._ctx)

                pass

            elif la_ == 21:
                self.enterOuterAlt(localctx, 21)
                self.state = 237
                self.match(PlantUMLDeploymentParser.COMMENT_MULTI)
                self.state = 239 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 238
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 241 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,23,self._ctx)

                pass

            elif la_ == 22:
                self.enterOuterAlt(localctx, 22)
                self.state = 244 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 243
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 246 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,24,self._ctx)

                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ElementDeclContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def BRACKET_COMP(self):
            return self.getToken(PlantUMLDeploymentParser.BRACKET_COMP, 0)

        def aliasClause(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.AliasClauseContext,0)


        def elementModifier(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PlantUMLDeploymentParser.ElementModifierContext)
            else:
                return self.getTypedRuleContext(PlantUMLDeploymentParser.ElementModifierContext,i)


        def ACTOR_COLON(self):
            return self.getToken(PlantUMLDeploymentParser.ACTOR_COLON, 0)

        def CIRCLE_IFACE(self):
            return self.getToken(PlantUMLDeploymentParser.CIRCLE_IFACE, 0)

        def elementName(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.ElementNameContext,0)


        def USECASE_PAREN(self):
            return self.getToken(PlantUMLDeploymentParser.USECASE_PAREN, 0)

        def elementKeyword(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.ElementKeywordContext,0)


        def descriptionBody(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.DescriptionBodyContext,0)


        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_elementDecl

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitElementDecl" ):
                return visitor.visitElementDecl(self)
            else:
                return visitor.visitChildren(self)




    def elementDecl(self):

        localctx = PlantUMLDeploymentParser.ElementDeclContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_elementDecl)
        self._la = 0 # Token type
        try:
            self.state = 305
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [4]:
                self.enterOuterAlt(localctx, 1)
                self.state = 250
                self.match(PlantUMLDeploymentParser.BRACKET_COMP)
                self.state = 252
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==40:
                    self.state = 251
                    self.aliasClause()


                self.state = 257
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while ((((_la - 8)) & ~0x3f) == 0 and ((1 << (_la - 8)) & -8070450532247928831) != 0):
                    self.state = 254
                    self.elementModifier()
                    self.state = 259
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass
            elif token in [5]:
                self.enterOuterAlt(localctx, 2)
                self.state = 260
                self.match(PlantUMLDeploymentParser.ACTOR_COLON)
                self.state = 262
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==40:
                    self.state = 261
                    self.aliasClause()


                self.state = 267
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while ((((_la - 8)) & ~0x3f) == 0 and ((1 << (_la - 8)) & -8070450532247928831) != 0):
                    self.state = 264
                    self.elementModifier()
                    self.state = 269
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass
            elif token in [7]:
                self.enterOuterAlt(localctx, 3)
                self.state = 270
                self.match(PlantUMLDeploymentParser.CIRCLE_IFACE)
                self.state = 271
                self.elementName()
                self.state = 273
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==40:
                    self.state = 272
                    self.aliasClause()


                self.state = 278
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while ((((_la - 8)) & ~0x3f) == 0 and ((1 << (_la - 8)) & -8070450532247928831) != 0):
                    self.state = 275
                    self.elementModifier()
                    self.state = 280
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass
            elif token in [6]:
                self.enterOuterAlt(localctx, 4)
                self.state = 281
                self.match(PlantUMLDeploymentParser.USECASE_PAREN)
                self.state = 283
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==40:
                    self.state = 282
                    self.aliasClause()


                self.state = 288
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while ((((_la - 8)) & ~0x3f) == 0 and ((1 << (_la - 8)) & -8070450532247928831) != 0):
                    self.state = 285
                    self.elementModifier()
                    self.state = 290
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass
            elif token in [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]:
                self.enterOuterAlt(localctx, 5)
                self.state = 291
                self.elementKeyword()
                self.state = 292
                self.elementName()
                self.state = 294
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==40:
                    self.state = 293
                    self.aliasClause()


                self.state = 299
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while ((((_la - 8)) & ~0x3f) == 0 and ((1 << (_la - 8)) & -8070450532247928831) != 0):
                    self.state = 296
                    self.elementModifier()
                    self.state = 301
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 303
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==76:
                    self.state = 302
                    self.descriptionBody()


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


    class DescriptionBodyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACK(self):
            return self.getToken(PlantUMLDeploymentParser.LBRACK, 0)

        def bodyText(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.BodyTextContext,0)


        def RBRACK(self):
            return self.getToken(PlantUMLDeploymentParser.RBRACK, 0)

        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_descriptionBody

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDescriptionBody" ):
                return visitor.visitDescriptionBody(self)
            else:
                return visitor.visitChildren(self)




    def descriptionBody(self):

        localctx = PlantUMLDeploymentParser.DescriptionBodyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_descriptionBody)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 307
            self.match(PlantUMLDeploymentParser.LBRACK)
            self.state = 308
            self.bodyText()
            self.state = 309
            self.match(PlantUMLDeploymentParser.RBRACK)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ElementBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def elementKeyword(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.ElementKeywordContext,0)


        def LBRACE(self):
            return self.getToken(PlantUMLDeploymentParser.LBRACE, 0)

        def RBRACE(self):
            return self.getToken(PlantUMLDeploymentParser.RBRACE, 0)

        def elementName(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.ElementNameContext,0)


        def aliasClause(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.AliasClauseContext,0)


        def elementModifier(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PlantUMLDeploymentParser.ElementModifierContext)
            else:
                return self.getTypedRuleContext(PlantUMLDeploymentParser.ElementModifierContext,i)


        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.NEWLINE)
            else:
                return self.getToken(PlantUMLDeploymentParser.NEWLINE, i)

        def blockStatement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PlantUMLDeploymentParser.BlockStatementContext)
            else:
                return self.getTypedRuleContext(PlantUMLDeploymentParser.BlockStatementContext,i)


        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_elementBlock

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitElementBlock" ):
                return visitor.visitElementBlock(self)
            else:
                return visitor.visitChildren(self)




    def elementBlock(self):

        localctx = PlantUMLDeploymentParser.ElementBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_elementBlock)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 311
            self.elementKeyword()
            self.state = 313
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==73 or _la==88:
                self.state = 312
                self.elementName()


            self.state = 316
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==40:
                self.state = 315
                self.aliasClause()


            self.state = 321
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while ((((_la - 8)) & ~0x3f) == 0 and ((1 << (_la - 8)) & -8070450532247928831) != 0):
                self.state = 318
                self.elementModifier()
                self.state = 323
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 324
            self.match(PlantUMLDeploymentParser.LBRACE)
            self.state = 326 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 325
                    self.match(PlantUMLDeploymentParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 328 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,41,self._ctx)

            self.state = 333
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 36283883715824) != 0) or ((((_la - 73)) & ~0x3f) == 0 and ((1 << (_la - 73)) & 753665) != 0):
                self.state = 330
                self.blockStatement()
                self.state = 335
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 336
            self.match(PlantUMLDeploymentParser.RBRACE)
            self.state = 338 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 337
                    self.match(PlantUMLDeploymentParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 340 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,43,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BlockStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def elementDecl(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.ElementDeclContext,0)


        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.NEWLINE)
            else:
                return self.getToken(PlantUMLDeploymentParser.NEWLINE, i)

        def elementBlock(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.ElementBlockContext,0)


        def portDecl(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.PortDeclContext,0)


        def relationStmt(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.RelationStmtContext,0)


        def noteStmt(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.NoteStmtContext,0)


        def noteBlock(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.NoteBlockContext,0)


        def COMMENT_SINGLE(self):
            return self.getToken(PlantUMLDeploymentParser.COMMENT_SINGLE, 0)

        def COMMENT_MULTI(self):
            return self.getToken(PlantUMLDeploymentParser.COMMENT_MULTI, 0)

        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_blockStatement

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBlockStatement" ):
                return visitor.visitBlockStatement(self)
            else:
                return visitor.visitChildren(self)




    def blockStatement(self):

        localctx = PlantUMLDeploymentParser.BlockStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_blockStatement)
        try:
            self.state = 385
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,51,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 342
                self.elementDecl()
                self.state = 344 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 343
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 346 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,44,self._ctx)

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 348
                self.elementBlock()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 349
                self.portDecl()
                self.state = 351 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 350
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 353 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,45,self._ctx)

                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 355
                self.relationStmt()
                self.state = 357 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 356
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 359 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,46,self._ctx)

                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 361
                self.noteStmt()
                self.state = 363 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 362
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 365 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,47,self._ctx)

                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 367
                self.noteBlock()
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 368
                self.match(PlantUMLDeploymentParser.COMMENT_SINGLE)
                self.state = 370 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 369
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 372 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,48,self._ctx)

                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 374
                self.match(PlantUMLDeploymentParser.COMMENT_MULTI)
                self.state = 376 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 375
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 378 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,49,self._ctx)

                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 381 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 380
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 383 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,50,self._ctx)

                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PortDeclContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KW_PORT(self):
            return self.getToken(PlantUMLDeploymentParser.KW_PORT, 0)

        def elementName(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.ElementNameContext,0)


        def KW_PORTIN(self):
            return self.getToken(PlantUMLDeploymentParser.KW_PORTIN, 0)

        def KW_PORTOUT(self):
            return self.getToken(PlantUMLDeploymentParser.KW_PORTOUT, 0)

        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_portDecl

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPortDecl" ):
                return visitor.visitPortDecl(self)
            else:
                return visitor.visitChildren(self)




    def portDecl(self):

        localctx = PlantUMLDeploymentParser.PortDeclContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_portDecl)
        try:
            self.state = 393
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [37]:
                self.enterOuterAlt(localctx, 1)
                self.state = 387
                self.match(PlantUMLDeploymentParser.KW_PORT)
                self.state = 388
                self.elementName()
                pass
            elif token in [38]:
                self.enterOuterAlt(localctx, 2)
                self.state = 389
                self.match(PlantUMLDeploymentParser.KW_PORTIN)
                self.state = 390
                self.elementName()
                pass
            elif token in [39]:
                self.enterOuterAlt(localctx, 3)
                self.state = 391
                self.match(PlantUMLDeploymentParser.KW_PORTOUT)
                self.state = 392
                self.elementName()
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


    class TogetherBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KW_TOGETHER(self):
            return self.getToken(PlantUMLDeploymentParser.KW_TOGETHER, 0)

        def LBRACE(self):
            return self.getToken(PlantUMLDeploymentParser.LBRACE, 0)

        def RBRACE(self):
            return self.getToken(PlantUMLDeploymentParser.RBRACE, 0)

        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.NEWLINE)
            else:
                return self.getToken(PlantUMLDeploymentParser.NEWLINE, i)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PlantUMLDeploymentParser.StatementContext)
            else:
                return self.getTypedRuleContext(PlantUMLDeploymentParser.StatementContext,i)


        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_togetherBlock

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTogetherBlock" ):
                return visitor.visitTogetherBlock(self)
            else:
                return visitor.visitChildren(self)




    def togetherBlock(self):

        localctx = PlantUMLDeploymentParser.TogetherBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_togetherBlock)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 395
            self.match(PlantUMLDeploymentParser.KW_TOGETHER)
            self.state = 396
            self.match(PlantUMLDeploymentParser.LBRACE)
            self.state = 398 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 397
                    self.match(PlantUMLDeploymentParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 400 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,53,self._ctx)

            self.state = 405
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & -4667591649214333712) != 0) or ((((_la - 65)) & ~0x3f) == 0 and ((1 << (_la - 65)) & 193462531) != 0):
                self.state = 402
                self.statement()
                self.state = 407
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 408
            self.match(PlantUMLDeploymentParser.RBRACE)
            self.state = 410 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 409
                    self.match(PlantUMLDeploymentParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 412 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,55,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ElementKeywordContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KW_ACTOR(self):
            return self.getToken(PlantUMLDeploymentParser.KW_ACTOR, 0)

        def KW_AGENT(self):
            return self.getToken(PlantUMLDeploymentParser.KW_AGENT, 0)

        def KW_ARTIFACT(self):
            return self.getToken(PlantUMLDeploymentParser.KW_ARTIFACT, 0)

        def KW_BOUNDARY(self):
            return self.getToken(PlantUMLDeploymentParser.KW_BOUNDARY, 0)

        def KW_CARD(self):
            return self.getToken(PlantUMLDeploymentParser.KW_CARD, 0)

        def KW_CIRCLE(self):
            return self.getToken(PlantUMLDeploymentParser.KW_CIRCLE, 0)

        def KW_CLOUD(self):
            return self.getToken(PlantUMLDeploymentParser.KW_CLOUD, 0)

        def KW_COLLECTIONS(self):
            return self.getToken(PlantUMLDeploymentParser.KW_COLLECTIONS, 0)

        def KW_COMPONENT(self):
            return self.getToken(PlantUMLDeploymentParser.KW_COMPONENT, 0)

        def KW_CONTROL(self):
            return self.getToken(PlantUMLDeploymentParser.KW_CONTROL, 0)

        def KW_DATABASE(self):
            return self.getToken(PlantUMLDeploymentParser.KW_DATABASE, 0)

        def KW_ENTITY(self):
            return self.getToken(PlantUMLDeploymentParser.KW_ENTITY, 0)

        def KW_FILE(self):
            return self.getToken(PlantUMLDeploymentParser.KW_FILE, 0)

        def KW_FOLDER(self):
            return self.getToken(PlantUMLDeploymentParser.KW_FOLDER, 0)

        def KW_FRAME(self):
            return self.getToken(PlantUMLDeploymentParser.KW_FRAME, 0)

        def KW_HEXAGON(self):
            return self.getToken(PlantUMLDeploymentParser.KW_HEXAGON, 0)

        def KW_INTERFACE(self):
            return self.getToken(PlantUMLDeploymentParser.KW_INTERFACE, 0)

        def KW_LABEL(self):
            return self.getToken(PlantUMLDeploymentParser.KW_LABEL, 0)

        def KW_NODE(self):
            return self.getToken(PlantUMLDeploymentParser.KW_NODE, 0)

        def KW_PACKAGE(self):
            return self.getToken(PlantUMLDeploymentParser.KW_PACKAGE, 0)

        def KW_PERSON(self):
            return self.getToken(PlantUMLDeploymentParser.KW_PERSON, 0)

        def KW_PROCESS(self):
            return self.getToken(PlantUMLDeploymentParser.KW_PROCESS, 0)

        def KW_QUEUE(self):
            return self.getToken(PlantUMLDeploymentParser.KW_QUEUE, 0)

        def KW_RECTANGLE(self):
            return self.getToken(PlantUMLDeploymentParser.KW_RECTANGLE, 0)

        def KW_STACK(self):
            return self.getToken(PlantUMLDeploymentParser.KW_STACK, 0)

        def KW_STORAGE(self):
            return self.getToken(PlantUMLDeploymentParser.KW_STORAGE, 0)

        def KW_USECASE(self):
            return self.getToken(PlantUMLDeploymentParser.KW_USECASE, 0)

        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_elementKeyword

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitElementKeyword" ):
                return visitor.visitElementKeyword(self)
            else:
                return visitor.visitChildren(self)




    def elementKeyword(self):

        localctx = PlantUMLDeploymentParser.ElementKeywordContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_elementKeyword)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 414
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 137438952448) != 0)):
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


    class ElementNameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def QUOTED_STRING(self):
            return self.getToken(PlantUMLDeploymentParser.QUOTED_STRING, 0)

        def ID(self):
            return self.getToken(PlantUMLDeploymentParser.ID, 0)

        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_elementName

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitElementName" ):
                return visitor.visitElementName(self)
            else:
                return visitor.visitChildren(self)




    def elementName(self):

        localctx = PlantUMLDeploymentParser.ElementNameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_elementName)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 416
            _la = self._input.LA(1)
            if not(_la==73 or _la==88):
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


    class AliasClauseContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KW_AS(self):
            return self.getToken(PlantUMLDeploymentParser.KW_AS, 0)

        def elementName(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.ElementNameContext,0)


        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_aliasClause

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAliasClause" ):
                return visitor.visitAliasClause(self)
            else:
                return visitor.visitChildren(self)




    def aliasClause(self):

        localctx = PlantUMLDeploymentParser.AliasClauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_aliasClause)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 418
            self.match(PlantUMLDeploymentParser.KW_AS)
            self.state = 419
            self.elementName()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ElementModifierContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def stereotypeClause(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.StereotypeClauseContext,0)


        def colorSpec(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.ColorSpecContext,0)


        def TAG(self):
            return self.getToken(PlantUMLDeploymentParser.TAG, 0)

        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_elementModifier

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitElementModifier" ):
                return visitor.visitElementModifier(self)
            else:
                return visitor.visitChildren(self)




    def elementModifier(self):

        localctx = PlantUMLDeploymentParser.ElementModifierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_elementModifier)
        try:
            self.state = 424
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [68]:
                self.enterOuterAlt(localctx, 1)
                self.state = 421
                self.stereotypeClause()
                pass
            elif token in [71]:
                self.enterOuterAlt(localctx, 2)
                self.state = 422
                self.colorSpec()
                pass
            elif token in [8]:
                self.enterOuterAlt(localctx, 3)
                self.state = 423
                self.match(PlantUMLDeploymentParser.TAG)
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


    class ColorSpecContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COLOR(self):
            return self.getToken(PlantUMLDeploymentParser.COLOR, 0)

        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_colorSpec

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitColorSpec" ):
                return visitor.visitColorSpec(self)
            else:
                return visitor.visitChildren(self)




    def colorSpec(self):

        localctx = PlantUMLDeploymentParser.ColorSpecContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_colorSpec)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 426
            self.match(PlantUMLDeploymentParser.COLOR)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StereotypeClauseContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STEREOTYPE_OPEN(self):
            return self.getToken(PlantUMLDeploymentParser.STEREOTYPE_OPEN, 0)

        def stereotypeBody(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.StereotypeBodyContext,0)


        def STEREOTYPE_CLOSE(self):
            return self.getToken(PlantUMLDeploymentParser.STEREOTYPE_CLOSE, 0)

        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_stereotypeClause

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStereotypeClause" ):
                return visitor.visitStereotypeClause(self)
            else:
                return visitor.visitChildren(self)




    def stereotypeClause(self):

        localctx = PlantUMLDeploymentParser.StereotypeClauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_stereotypeClause)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 428
            self.match(PlantUMLDeploymentParser.STEREOTYPE_OPEN)
            self.state = 429
            self.stereotypeBody()
            self.state = 430
            self.match(PlantUMLDeploymentParser.STEREOTYPE_CLOSE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StereotypeBodyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def spotSpec(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.SpotSpecContext,0)


        def stereotypeText(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.StereotypeTextContext,0)


        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_stereotypeBody

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStereotypeBody" ):
                return visitor.visitStereotypeBody(self)
            else:
                return visitor.visitChildren(self)




    def stereotypeBody(self):

        localctx = PlantUMLDeploymentParser.StereotypeBodyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_stereotypeBody)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 433
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==74:
                self.state = 432
                self.spotSpec()


            self.state = 436
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==88 or _la==91:
                self.state = 435
                self.stereotypeText()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SpotSpecContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LPAREN(self):
            return self.getToken(PlantUMLDeploymentParser.LPAREN, 0)

        def spotChar(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.SpotCharContext,0)


        def COMMA(self):
            return self.getToken(PlantUMLDeploymentParser.COMMA, 0)

        def colorSpec(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.ColorSpecContext,0)


        def RPAREN(self):
            return self.getToken(PlantUMLDeploymentParser.RPAREN, 0)

        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_spotSpec

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSpotSpec" ):
                return visitor.visitSpotSpec(self)
            else:
                return visitor.visitChildren(self)




    def spotSpec(self):

        localctx = PlantUMLDeploymentParser.SpotSpecContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_spotSpec)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 438
            self.match(PlantUMLDeploymentParser.LPAREN)
            self.state = 439
            self.spotChar()
            self.state = 440
            self.match(PlantUMLDeploymentParser.COMMA)
            self.state = 441
            self.colorSpec()
            self.state = 442
            self.match(PlantUMLDeploymentParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SpotCharContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(PlantUMLDeploymentParser.ID, 0)

        def INT(self):
            return self.getToken(PlantUMLDeploymentParser.INT, 0)

        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_spotChar

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSpotChar" ):
                return visitor.visitSpotChar(self)
            else:
                return visitor.visitChildren(self)




    def spotChar(self):

        localctx = PlantUMLDeploymentParser.SpotCharContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_spotChar)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 444
            _la = self._input.LA(1)
            if not(_la==87 or _la==88):
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


    class StereotypeTextContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FREE_TEXT(self):
            return self.getToken(PlantUMLDeploymentParser.FREE_TEXT, 0)

        def ID(self):
            return self.getToken(PlantUMLDeploymentParser.ID, 0)

        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_stereotypeText

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStereotypeText" ):
                return visitor.visitStereotypeText(self)
            else:
                return visitor.visitChildren(self)




    def stereotypeText(self):

        localctx = PlantUMLDeploymentParser.StereotypeTextContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_stereotypeText)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 446
            _la = self._input.LA(1)
            if not(_la==88 or _la==91):
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


    class BodyTextContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def restOfLine(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.RestOfLineContext,0)


        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_bodyText

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBodyText" ):
                return visitor.visitBodyText(self)
            else:
                return visitor.visitChildren(self)




    def bodyText(self):

        localctx = PlantUMLDeploymentParser.BodyTextContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_bodyText)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 449
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,59,self._ctx)
            if la_ == 1:
                self.state = 448
                self.restOfLine()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RestOfLineContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.ID)
            else:
                return self.getToken(PlantUMLDeploymentParser.ID, i)

        def QUOTED_STRING(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.QUOTED_STRING)
            else:
                return self.getToken(PlantUMLDeploymentParser.QUOTED_STRING, i)

        def INT(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.INT)
            else:
                return self.getToken(PlantUMLDeploymentParser.INT, i)

        def COLOR(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.COLOR)
            else:
                return self.getToken(PlantUMLDeploymentParser.COLOR, i)

        def TAG(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.TAG)
            else:
                return self.getToken(PlantUMLDeploymentParser.TAG, i)

        def FREE_TEXT(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.FREE_TEXT)
            else:
                return self.getToken(PlantUMLDeploymentParser.FREE_TEXT, i)

        def COLON(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.COLON)
            else:
                return self.getToken(PlantUMLDeploymentParser.COLON, i)

        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.COMMA)
            else:
                return self.getToken(PlantUMLDeploymentParser.COMMA, i)

        def STAR(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.STAR)
            else:
                return self.getToken(PlantUMLDeploymentParser.STAR, i)

        def BANG(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.BANG)
            else:
                return self.getToken(PlantUMLDeploymentParser.BANG, i)

        def FSLASH(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.FSLASH)
            else:
                return self.getToken(PlantUMLDeploymentParser.FSLASH, i)

        def LPAREN(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.LPAREN)
            else:
                return self.getToken(PlantUMLDeploymentParser.LPAREN, i)

        def RPAREN(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.RPAREN)
            else:
                return self.getToken(PlantUMLDeploymentParser.RPAREN, i)

        def LBRACK(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.LBRACK)
            else:
                return self.getToken(PlantUMLDeploymentParser.LBRACK, i)

        def RBRACK(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.RBRACK)
            else:
                return self.getToken(PlantUMLDeploymentParser.RBRACK, i)

        def AT(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.AT)
            else:
                return self.getToken(PlantUMLDeploymentParser.AT, i)

        def DOLLAR(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.DOLLAR)
            else:
                return self.getToken(PlantUMLDeploymentParser.DOLLAR, i)

        def STEREOTYPE_OPEN(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.STEREOTYPE_OPEN)
            else:
                return self.getToken(PlantUMLDeploymentParser.STEREOTYPE_OPEN, i)

        def STEREOTYPE_CLOSE(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.STEREOTYPE_CLOSE)
            else:
                return self.getToken(PlantUMLDeploymentParser.STEREOTYPE_CLOSE, i)

        def BRACKET_COMP(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.BRACKET_COMP)
            else:
                return self.getToken(PlantUMLDeploymentParser.BRACKET_COMP, i)

        def ACTOR_COLON(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.ACTOR_COLON)
            else:
                return self.getToken(PlantUMLDeploymentParser.ACTOR_COLON, i)

        def USECASE_PAREN(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.USECASE_PAREN)
            else:
                return self.getToken(PlantUMLDeploymentParser.USECASE_PAREN, i)

        def ARROW_SPEC(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.ARROW_SPEC)
            else:
                return self.getToken(PlantUMLDeploymentParser.ARROW_SPEC, i)

        def KW_AS(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.KW_AS)
            else:
                return self.getToken(PlantUMLDeploymentParser.KW_AS, i)

        def KW_OF(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.KW_OF)
            else:
                return self.getToken(PlantUMLDeploymentParser.KW_OF, i)

        def KW_TO(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.KW_TO)
            else:
                return self.getToken(PlantUMLDeploymentParser.KW_TO, i)

        def KW_LEFT(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.KW_LEFT)
            else:
                return self.getToken(PlantUMLDeploymentParser.KW_LEFT, i)

        def KW_RIGHT(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.KW_RIGHT)
            else:
                return self.getToken(PlantUMLDeploymentParser.KW_RIGHT, i)

        def KW_TOP(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.KW_TOP)
            else:
                return self.getToken(PlantUMLDeploymentParser.KW_TOP, i)

        def KW_BOTTOM(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.KW_BOTTOM)
            else:
                return self.getToken(PlantUMLDeploymentParser.KW_BOTTOM, i)

        def KW_CENTER(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.KW_CENTER)
            else:
                return self.getToken(PlantUMLDeploymentParser.KW_CENTER, i)

        def KW_X(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.KW_X)
            else:
                return self.getToken(PlantUMLDeploymentParser.KW_X, i)

        def KW_DIRECTION(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.KW_DIRECTION)
            else:
                return self.getToken(PlantUMLDeploymentParser.KW_DIRECTION, i)

        def elementKeyword(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PlantUMLDeploymentParser.ElementKeywordContext)
            else:
                return self.getTypedRuleContext(PlantUMLDeploymentParser.ElementKeywordContext,i)


        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_restOfLine

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRestOfLine" ):
                return visitor.visitRestOfLine(self)
            else:
                return visitor.visitChildren(self)




    def restOfLine(self):

        localctx = PlantUMLDeploymentParser.RestOfLineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_restOfLine)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 485 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 485
                    self._errHandler.sync(self)
                    token = self._input.LA(1)
                    if token in [88]:
                        self.state = 451
                        self.match(PlantUMLDeploymentParser.ID)
                        pass
                    elif token in [73]:
                        self.state = 452
                        self.match(PlantUMLDeploymentParser.QUOTED_STRING)
                        pass
                    elif token in [87]:
                        self.state = 453
                        self.match(PlantUMLDeploymentParser.INT)
                        pass
                    elif token in [71]:
                        self.state = 454
                        self.match(PlantUMLDeploymentParser.COLOR)
                        pass
                    elif token in [8]:
                        self.state = 455
                        self.match(PlantUMLDeploymentParser.TAG)
                        pass
                    elif token in [91]:
                        self.state = 456
                        self.match(PlantUMLDeploymentParser.FREE_TEXT)
                        pass
                    elif token in [81]:
                        self.state = 457
                        self.match(PlantUMLDeploymentParser.COLON)
                        pass
                    elif token in [82]:
                        self.state = 458
                        self.match(PlantUMLDeploymentParser.COMMA)
                        pass
                    elif token in [83]:
                        self.state = 459
                        self.match(PlantUMLDeploymentParser.STAR)
                        pass
                    elif token in [84]:
                        self.state = 460
                        self.match(PlantUMLDeploymentParser.BANG)
                        pass
                    elif token in [80]:
                        self.state = 461
                        self.match(PlantUMLDeploymentParser.FSLASH)
                        pass
                    elif token in [74]:
                        self.state = 462
                        self.match(PlantUMLDeploymentParser.LPAREN)
                        pass
                    elif token in [75]:
                        self.state = 463
                        self.match(PlantUMLDeploymentParser.RPAREN)
                        pass
                    elif token in [76]:
                        self.state = 464
                        self.match(PlantUMLDeploymentParser.LBRACK)
                        pass
                    elif token in [77]:
                        self.state = 465
                        self.match(PlantUMLDeploymentParser.RBRACK)
                        pass
                    elif token in [85]:
                        self.state = 466
                        self.match(PlantUMLDeploymentParser.AT)
                        pass
                    elif token in [86]:
                        self.state = 467
                        self.match(PlantUMLDeploymentParser.DOLLAR)
                        pass
                    elif token in [68]:
                        self.state = 468
                        self.match(PlantUMLDeploymentParser.STEREOTYPE_OPEN)
                        pass
                    elif token in [69]:
                        self.state = 469
                        self.match(PlantUMLDeploymentParser.STEREOTYPE_CLOSE)
                        pass
                    elif token in [4]:
                        self.state = 470
                        self.match(PlantUMLDeploymentParser.BRACKET_COMP)
                        pass
                    elif token in [5]:
                        self.state = 471
                        self.match(PlantUMLDeploymentParser.ACTOR_COLON)
                        pass
                    elif token in [6]:
                        self.state = 472
                        self.match(PlantUMLDeploymentParser.USECASE_PAREN)
                        pass
                    elif token in [70]:
                        self.state = 473
                        self.match(PlantUMLDeploymentParser.ARROW_SPEC)
                        pass
                    elif token in [40]:
                        self.state = 474
                        self.match(PlantUMLDeploymentParser.KW_AS)
                        pass
                    elif token in [50]:
                        self.state = 475
                        self.match(PlantUMLDeploymentParser.KW_OF)
                        pass
                    elif token in [54]:
                        self.state = 476
                        self.match(PlantUMLDeploymentParser.KW_TO)
                        pass
                    elif token in [46]:
                        self.state = 477
                        self.match(PlantUMLDeploymentParser.KW_LEFT)
                        pass
                    elif token in [47]:
                        self.state = 478
                        self.match(PlantUMLDeploymentParser.KW_RIGHT)
                        pass
                    elif token in [48]:
                        self.state = 479
                        self.match(PlantUMLDeploymentParser.KW_TOP)
                        pass
                    elif token in [49]:
                        self.state = 480
                        self.match(PlantUMLDeploymentParser.KW_BOTTOM)
                        pass
                    elif token in [62]:
                        self.state = 481
                        self.match(PlantUMLDeploymentParser.KW_CENTER)
                        pass
                    elif token in [67]:
                        self.state = 482
                        self.match(PlantUMLDeploymentParser.KW_X)
                        pass
                    elif token in [55]:
                        self.state = 483
                        self.match(PlantUMLDeploymentParser.KW_DIRECTION)
                        pass
                    elif token in [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]:
                        self.state = 484
                        self.elementKeyword()
                        pass
                    else:
                        raise NoViableAltException(self)


                else:
                    raise NoViableAltException(self)
                self.state = 487 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,61,self._ctx)

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

        def relationRef(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PlantUMLDeploymentParser.RelationRefContext)
            else:
                return self.getTypedRuleContext(PlantUMLDeploymentParser.RelationRefContext,i)


        def ARROW_SPEC(self):
            return self.getToken(PlantUMLDeploymentParser.ARROW_SPEC, 0)

        def COLON(self):
            return self.getToken(PlantUMLDeploymentParser.COLON, 0)

        def labelText(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.LabelTextContext,0)


        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_relationStmt

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRelationStmt" ):
                return visitor.visitRelationStmt(self)
            else:
                return visitor.visitChildren(self)




    def relationStmt(self):

        localctx = PlantUMLDeploymentParser.RelationStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_relationStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 489
            self.relationRef()
            self.state = 490
            self.match(PlantUMLDeploymentParser.ARROW_SPEC)
            self.state = 491
            self.relationRef()
            self.state = 494
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==81:
                self.state = 492
                self.match(PlantUMLDeploymentParser.COLON)
                self.state = 493
                self.labelText()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RelationRefContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def BRACKET_COMP(self):
            return self.getToken(PlantUMLDeploymentParser.BRACKET_COMP, 0)

        def ACTOR_COLON(self):
            return self.getToken(PlantUMLDeploymentParser.ACTOR_COLON, 0)

        def USECASE_PAREN(self):
            return self.getToken(PlantUMLDeploymentParser.USECASE_PAREN, 0)

        def QUOTED_STRING(self):
            return self.getToken(PlantUMLDeploymentParser.QUOTED_STRING, 0)

        def ID(self):
            return self.getToken(PlantUMLDeploymentParser.ID, 0)

        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_relationRef

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRelationRef" ):
                return visitor.visitRelationRef(self)
            else:
                return visitor.visitChildren(self)




    def relationRef(self):

        localctx = PlantUMLDeploymentParser.RelationRefContext(self, self._ctx, self.state)
        self.enterRule(localctx, 44, self.RULE_relationRef)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 496
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 112) != 0) or _la==73 or _la==88):
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


    class LabelTextContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def restOfLine(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.RestOfLineContext,0)


        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_labelText

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLabelText" ):
                return visitor.visitLabelText(self)
            else:
                return visitor.visitChildren(self)




    def labelText(self):

        localctx = PlantUMLDeploymentParser.LabelTextContext(self, self._ctx, self.state)
        self.enterRule(localctx, 46, self.RULE_labelText)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 498
            self.restOfLine()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NoteStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KW_NOTE(self):
            return self.getToken(PlantUMLDeploymentParser.KW_NOTE, 0)

        def noteSide(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.NoteSideContext,0)


        def KW_OF(self):
            return self.getToken(PlantUMLDeploymentParser.KW_OF, 0)

        def relationRef(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.RelationRefContext,0)


        def COLON(self):
            return self.getToken(PlantUMLDeploymentParser.COLON, 0)

        def restOfLine(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.RestOfLineContext,0)


        def QUOTED_STRING(self):
            return self.getToken(PlantUMLDeploymentParser.QUOTED_STRING, 0)

        def KW_AS(self):
            return self.getToken(PlantUMLDeploymentParser.KW_AS, 0)

        def elementName(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.ElementNameContext,0)


        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_noteStmt

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNoteStmt" ):
                return visitor.visitNoteStmt(self)
            else:
                return visitor.visitChildren(self)




    def noteStmt(self):

        localctx = PlantUMLDeploymentParser.NoteStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 48, self.RULE_noteStmt)
        self._la = 0 # Token type
        try:
            self.state = 512
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,64,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 500
                self.match(PlantUMLDeploymentParser.KW_NOTE)
                self.state = 501
                self.noteSide()
                self.state = 502
                self.match(PlantUMLDeploymentParser.KW_OF)
                self.state = 503
                self.relationRef()
                self.state = 506
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==81:
                    self.state = 504
                    self.match(PlantUMLDeploymentParser.COLON)
                    self.state = 505
                    self.restOfLine()


                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 508
                self.match(PlantUMLDeploymentParser.KW_NOTE)
                self.state = 509
                self.match(PlantUMLDeploymentParser.QUOTED_STRING)
                self.state = 510
                self.match(PlantUMLDeploymentParser.KW_AS)
                self.state = 511
                self.elementName()
                pass


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
            return self.getToken(PlantUMLDeploymentParser.KW_NOTE, 0)

        def noteSide(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.NoteSideContext,0)


        def KW_OF(self):
            return self.getToken(PlantUMLDeploymentParser.KW_OF, 0)

        def relationRef(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.RelationRefContext,0)


        def KW_END_NOTE(self):
            return self.getToken(PlantUMLDeploymentParser.KW_END_NOTE, 0)

        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.NEWLINE)
            else:
                return self.getToken(PlantUMLDeploymentParser.NEWLINE, i)

        def noteBodyLine(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PlantUMLDeploymentParser.NoteBodyLineContext)
            else:
                return self.getTypedRuleContext(PlantUMLDeploymentParser.NoteBodyLineContext,i)


        def KW_AS(self):
            return self.getToken(PlantUMLDeploymentParser.KW_AS, 0)

        def elementName(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.ElementNameContext,0)


        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_noteBlock

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNoteBlock" ):
                return visitor.visitNoteBlock(self)
            else:
                return visitor.visitChildren(self)




    def noteBlock(self):

        localctx = PlantUMLDeploymentParser.NoteBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 50, self.RULE_noteBlock)
        self._la = 0 # Token type
        try:
            self.state = 553
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,71,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 514
                self.match(PlantUMLDeploymentParser.KW_NOTE)
                self.state = 515
                self.noteSide()
                self.state = 516
                self.match(PlantUMLDeploymentParser.KW_OF)
                self.state = 517
                self.relationRef()
                self.state = 519 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 518
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 521 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,65,self._ctx)

                self.state = 524 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 523
                    self.noteBodyLine()
                    self.state = 526 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 4667911881975922032) != 0) or ((((_la - 67)) & ~0x3f) == 0 and ((1 << (_la - 67)) & 54519775) != 0)):
                        break

                self.state = 528
                self.match(PlantUMLDeploymentParser.KW_END_NOTE)
                self.state = 530 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 529
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 532 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,67,self._ctx)

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 534
                self.match(PlantUMLDeploymentParser.KW_NOTE)
                self.state = 535
                self.match(PlantUMLDeploymentParser.KW_AS)
                self.state = 536
                self.elementName()
                self.state = 538 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 537
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 540 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,68,self._ctx)

                self.state = 543 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 542
                    self.noteBodyLine()
                    self.state = 545 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 4667911881975922032) != 0) or ((((_la - 67)) & ~0x3f) == 0 and ((1 << (_la - 67)) & 54519775) != 0)):
                        break

                self.state = 547
                self.match(PlantUMLDeploymentParser.KW_END_NOTE)
                self.state = 549 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 548
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 551 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,70,self._ctx)

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

        def KW_LEFT(self):
            return self.getToken(PlantUMLDeploymentParser.KW_LEFT, 0)

        def KW_RIGHT(self):
            return self.getToken(PlantUMLDeploymentParser.KW_RIGHT, 0)

        def KW_TOP(self):
            return self.getToken(PlantUMLDeploymentParser.KW_TOP, 0)

        def KW_BOTTOM(self):
            return self.getToken(PlantUMLDeploymentParser.KW_BOTTOM, 0)

        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_noteSide

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNoteSide" ):
                return visitor.visitNoteSide(self)
            else:
                return visitor.visitChildren(self)




    def noteSide(self):

        localctx = PlantUMLDeploymentParser.NoteSideContext(self, self._ctx, self.state)
        self.enterRule(localctx, 52, self.RULE_noteSide)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 555
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 1055531162664960) != 0)):
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


    class NoteBodyLineContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def restOfLine(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.RestOfLineContext,0)


        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.NEWLINE)
            else:
                return self.getToken(PlantUMLDeploymentParser.NEWLINE, i)

        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_noteBodyLine

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNoteBodyLine" ):
                return visitor.visitNoteBodyLine(self)
            else:
                return visitor.visitChildren(self)




    def noteBodyLine(self):

        localctx = PlantUMLDeploymentParser.NoteBodyLineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 54, self.RULE_noteBodyLine)
        try:
            self.state = 568
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [4, 5, 6, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 40, 46, 47, 48, 49, 50, 54, 55, 62, 67, 68, 69, 70, 71, 73, 74, 75, 76, 77, 80, 81, 82, 83, 84, 85, 86, 87, 88, 91]:
                self.enterOuterAlt(localctx, 1)
                self.state = 557
                self.restOfLine()
                self.state = 559 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 558
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 561 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,72,self._ctx)

                pass
            elif token in [92]:
                self.enterOuterAlt(localctx, 2)
                self.state = 564 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 563
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 566 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,73,self._ctx)

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


    class SpriteDeclContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KW_SPRITE(self):
            return self.getToken(PlantUMLDeploymentParser.KW_SPRITE, 0)

        def TAG(self):
            return self.getToken(PlantUMLDeploymentParser.TAG, 0)

        def LBRACE(self):
            return self.getToken(PlantUMLDeploymentParser.LBRACE, 0)

        def RBRACE(self):
            return self.getToken(PlantUMLDeploymentParser.RBRACE, 0)

        def spriteDimension(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.SpriteDimensionContext,0)


        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.NEWLINE)
            else:
                return self.getToken(PlantUMLDeploymentParser.NEWLINE, i)

        def spriteRow(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PlantUMLDeploymentParser.SpriteRowContext)
            else:
                return self.getTypedRuleContext(PlantUMLDeploymentParser.SpriteRowContext,i)


        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_spriteDecl

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSpriteDecl" ):
                return visitor.visitSpriteDecl(self)
            else:
                return visitor.visitChildren(self)




    def spriteDecl(self):

        localctx = PlantUMLDeploymentParser.SpriteDeclContext(self, self._ctx, self.state)
        self.enterRule(localctx, 56, self.RULE_spriteDecl)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 570
            self.match(PlantUMLDeploymentParser.KW_SPRITE)
            self.state = 571
            self.match(PlantUMLDeploymentParser.TAG)
            self.state = 573
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==76:
                self.state = 572
                self.spriteDimension()


            self.state = 575
            self.match(PlantUMLDeploymentParser.LBRACE)
            self.state = 577 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 576
                    self.match(PlantUMLDeploymentParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 579 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,76,self._ctx)

            self.state = 582 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 581
                self.spriteRow()
                self.state = 584 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==72 or _la==92):
                    break

            self.state = 586
            self.match(PlantUMLDeploymentParser.RBRACE)
            self.state = 588 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 587
                    self.match(PlantUMLDeploymentParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 590 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,78,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SpriteDimensionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACK(self):
            return self.getToken(PlantUMLDeploymentParser.LBRACK, 0)

        def INT(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.INT)
            else:
                return self.getToken(PlantUMLDeploymentParser.INT, i)

        def KW_X(self):
            return self.getToken(PlantUMLDeploymentParser.KW_X, 0)

        def RBRACK(self):
            return self.getToken(PlantUMLDeploymentParser.RBRACK, 0)

        def FSLASH(self):
            return self.getToken(PlantUMLDeploymentParser.FSLASH, 0)

        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_spriteDimension

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSpriteDimension" ):
                return visitor.visitSpriteDimension(self)
            else:
                return visitor.visitChildren(self)




    def spriteDimension(self):

        localctx = PlantUMLDeploymentParser.SpriteDimensionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 58, self.RULE_spriteDimension)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 592
            self.match(PlantUMLDeploymentParser.LBRACK)
            self.state = 593
            self.match(PlantUMLDeploymentParser.INT)
            self.state = 594
            self.match(PlantUMLDeploymentParser.KW_X)
            self.state = 595
            self.match(PlantUMLDeploymentParser.INT)
            self.state = 598
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==80:
                self.state = 596
                self.match(PlantUMLDeploymentParser.FSLASH)
                self.state = 597
                self.match(PlantUMLDeploymentParser.INT)


            self.state = 600
            self.match(PlantUMLDeploymentParser.RBRACK)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SpriteRowContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SPRITE_ROW(self):
            return self.getToken(PlantUMLDeploymentParser.SPRITE_ROW, 0)

        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.NEWLINE)
            else:
                return self.getToken(PlantUMLDeploymentParser.NEWLINE, i)

        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_spriteRow

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSpriteRow" ):
                return visitor.visitSpriteRow(self)
            else:
                return visitor.visitChildren(self)




    def spriteRow(self):

        localctx = PlantUMLDeploymentParser.SpriteRowContext(self, self._ctx, self.state)
        self.enterRule(localctx, 60, self.RULE_spriteRow)
        try:
            self.state = 613
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [72]:
                self.enterOuterAlt(localctx, 1)
                self.state = 602
                self.match(PlantUMLDeploymentParser.SPRITE_ROW)
                self.state = 604 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 603
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 606 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,80,self._ctx)

                pass
            elif token in [92]:
                self.enterOuterAlt(localctx, 2)
                self.state = 609 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 608
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 611 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,81,self._ctx)

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


    class SkinparamStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KW_SKINPARAM(self):
            return self.getToken(PlantUMLDeploymentParser.KW_SKINPARAM, 0)

        def skinparamPath(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.SkinparamPathContext,0)


        def restOfLine(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.RestOfLineContext,0)


        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_skinparamStmt

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSkinparamStmt" ):
                return visitor.visitSkinparamStmt(self)
            else:
                return visitor.visitChildren(self)




    def skinparamStmt(self):

        localctx = PlantUMLDeploymentParser.SkinparamStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 62, self.RULE_skinparamStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 615
            self.match(PlantUMLDeploymentParser.KW_SKINPARAM)
            self.state = 616
            self.skinparamPath()
            self.state = 618
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 4667911881975922032) != 0) or ((((_la - 67)) & ~0x3f) == 0 and ((1 << (_la - 67)) & 20965343) != 0):
                self.state = 617
                self.restOfLine()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SkinparamBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KW_SKINPARAM(self):
            return self.getToken(PlantUMLDeploymentParser.KW_SKINPARAM, 0)

        def skinparamPath(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.SkinparamPathContext,0)


        def LBRACE(self):
            return self.getToken(PlantUMLDeploymentParser.LBRACE, 0)

        def RBRACE(self):
            return self.getToken(PlantUMLDeploymentParser.RBRACE, 0)

        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.NEWLINE)
            else:
                return self.getToken(PlantUMLDeploymentParser.NEWLINE, i)

        def skinparamEntry(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PlantUMLDeploymentParser.SkinparamEntryContext)
            else:
                return self.getTypedRuleContext(PlantUMLDeploymentParser.SkinparamEntryContext,i)


        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_skinparamBlock

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSkinparamBlock" ):
                return visitor.visitSkinparamBlock(self)
            else:
                return visitor.visitChildren(self)




    def skinparamBlock(self):

        localctx = PlantUMLDeploymentParser.SkinparamBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 64, self.RULE_skinparamBlock)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 620
            self.match(PlantUMLDeploymentParser.KW_SKINPARAM)
            self.state = 621
            self.skinparamPath()
            self.state = 622
            self.match(PlantUMLDeploymentParser.LBRACE)
            self.state = 624 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 623
                    self.match(PlantUMLDeploymentParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 626 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,84,self._ctx)

            self.state = 631
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 137438952448) != 0) or _la==88 or _la==92:
                self.state = 628
                self.skinparamEntry()
                self.state = 633
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 634
            self.match(PlantUMLDeploymentParser.RBRACE)
            self.state = 636 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 635
                    self.match(PlantUMLDeploymentParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 638 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,86,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SkinparamPathContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def skinparamWord(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PlantUMLDeploymentParser.SkinparamWordContext)
            else:
                return self.getTypedRuleContext(PlantUMLDeploymentParser.SkinparamWordContext,i)


        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_skinparamPath

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSkinparamPath" ):
                return visitor.visitSkinparamPath(self)
            else:
                return visitor.visitChildren(self)




    def skinparamPath(self):

        localctx = PlantUMLDeploymentParser.SkinparamPathContext(self, self._ctx, self.state)
        self.enterRule(localctx, 66, self.RULE_skinparamPath)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 640
            self.skinparamWord()
            self.state = 645
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==1:
                self.state = 641
                self.match(PlantUMLDeploymentParser.T__0)
                self.state = 642
                self.skinparamWord()
                self.state = 647
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SkinparamWordContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(PlantUMLDeploymentParser.ID, 0)

        def elementKeyword(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.ElementKeywordContext,0)


        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_skinparamWord

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSkinparamWord" ):
                return visitor.visitSkinparamWord(self)
            else:
                return visitor.visitChildren(self)




    def skinparamWord(self):

        localctx = PlantUMLDeploymentParser.SkinparamWordContext(self, self._ctx, self.state)
        self.enterRule(localctx, 68, self.RULE_skinparamWord)
        try:
            self.state = 650
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [88]:
                self.enterOuterAlt(localctx, 1)
                self.state = 648
                self.match(PlantUMLDeploymentParser.ID)
                pass
            elif token in [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]:
                self.enterOuterAlt(localctx, 2)
                self.state = 649
                self.elementKeyword()
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


    class SkinparamEntryContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def skinparamWord(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.SkinparamWordContext,0)


        def restOfLine(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.RestOfLineContext,0)


        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.NEWLINE)
            else:
                return self.getToken(PlantUMLDeploymentParser.NEWLINE, i)

        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_skinparamEntry

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSkinparamEntry" ):
                return visitor.visitSkinparamEntry(self)
            else:
                return visitor.visitChildren(self)




    def skinparamEntry(self):

        localctx = PlantUMLDeploymentParser.SkinparamEntryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 70, self.RULE_skinparamEntry)
        try:
            self.state = 664
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 88]:
                self.enterOuterAlt(localctx, 1)
                self.state = 652
                self.skinparamWord()
                self.state = 653
                self.restOfLine()
                self.state = 655 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 654
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 657 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,89,self._ctx)

                pass
            elif token in [92]:
                self.enterOuterAlt(localctx, 2)
                self.state = 660 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 659
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 662 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,90,self._ctx)

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


    class VisibilityStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def visibilityKeyword(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.VisibilityKeywordContext,0)


        def visibilityTarget(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.VisibilityTargetContext,0)


        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_visibilityStmt

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitVisibilityStmt" ):
                return visitor.visitVisibilityStmt(self)
            else:
                return visitor.visitChildren(self)




    def visibilityStmt(self):

        localctx = PlantUMLDeploymentParser.VisibilityStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 72, self.RULE_visibilityStmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 666
            self.visibilityKeyword()
            self.state = 667
            self.visibilityTarget()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class VisibilityKeywordContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KW_HIDE(self):
            return self.getToken(PlantUMLDeploymentParser.KW_HIDE, 0)

        def KW_REMOVE(self):
            return self.getToken(PlantUMLDeploymentParser.KW_REMOVE, 0)

        def KW_RESTORE(self):
            return self.getToken(PlantUMLDeploymentParser.KW_RESTORE, 0)

        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_visibilityKeyword

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitVisibilityKeyword" ):
                return visitor.visitVisibilityKeyword(self)
            else:
                return visitor.visitChildren(self)




    def visibilityKeyword(self):

        localctx = PlantUMLDeploymentParser.VisibilityKeywordContext(self, self._ctx, self.state)
        self.enterRule(localctx, 74, self.RULE_visibilityKeyword)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 669
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 15762598695796736) != 0)):
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


    class VisibilityTargetContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def AT_UNLINKED(self):
            return self.getToken(PlantUMLDeploymentParser.AT_UNLINKED, 0)

        def TAG(self):
            return self.getToken(PlantUMLDeploymentParser.TAG, 0)

        def STAR(self):
            return self.getToken(PlantUMLDeploymentParser.STAR, 0)

        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_visibilityTarget

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitVisibilityTarget" ):
                return visitor.visitVisibilityTarget(self)
            else:
                return visitor.visitChildren(self)




    def visibilityTarget(self):

        localctx = PlantUMLDeploymentParser.VisibilityTargetContext(self, self._ctx, self.state)
        self.enterRule(localctx, 76, self.RULE_visibilityTarget)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 671
            _la = self._input.LA(1)
            if not(_la==8 or _la==9 or _la==83):
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


    class DirectionStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KW_LEFT(self):
            return self.getToken(PlantUMLDeploymentParser.KW_LEFT, 0)

        def KW_TO(self):
            return self.getToken(PlantUMLDeploymentParser.KW_TO, 0)

        def KW_RIGHT(self):
            return self.getToken(PlantUMLDeploymentParser.KW_RIGHT, 0)

        def KW_DIRECTION(self):
            return self.getToken(PlantUMLDeploymentParser.KW_DIRECTION, 0)

        def KW_TOP(self):
            return self.getToken(PlantUMLDeploymentParser.KW_TOP, 0)

        def KW_BOTTOM(self):
            return self.getToken(PlantUMLDeploymentParser.KW_BOTTOM, 0)

        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_directionStmt

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDirectionStmt" ):
                return visitor.visitDirectionStmt(self)
            else:
                return visitor.visitChildren(self)




    def directionStmt(self):

        localctx = PlantUMLDeploymentParser.DirectionStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 78, self.RULE_directionStmt)
        try:
            self.state = 681
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [46]:
                self.enterOuterAlt(localctx, 1)
                self.state = 673
                self.match(PlantUMLDeploymentParser.KW_LEFT)
                self.state = 674
                self.match(PlantUMLDeploymentParser.KW_TO)
                self.state = 675
                self.match(PlantUMLDeploymentParser.KW_RIGHT)
                self.state = 676
                self.match(PlantUMLDeploymentParser.KW_DIRECTION)
                pass
            elif token in [48]:
                self.enterOuterAlt(localctx, 2)
                self.state = 677
                self.match(PlantUMLDeploymentParser.KW_TOP)
                self.state = 678
                self.match(PlantUMLDeploymentParser.KW_TO)
                self.state = 679
                self.match(PlantUMLDeploymentParser.KW_BOTTOM)
                self.state = 680
                self.match(PlantUMLDeploymentParser.KW_DIRECTION)
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


    class AllowMixingStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KW_ALLOWMIXING(self):
            return self.getToken(PlantUMLDeploymentParser.KW_ALLOWMIXING, 0)

        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_allowMixingStmt

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAllowMixingStmt" ):
                return visitor.visitAllowMixingStmt(self)
            else:
                return visitor.visitChildren(self)




    def allowMixingStmt(self):

        localctx = PlantUMLDeploymentParser.AllowMixingStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 80, self.RULE_allowMixingStmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 683
            self.match(PlantUMLDeploymentParser.KW_ALLOWMIXING)
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

        def KW_TITLE(self):
            return self.getToken(PlantUMLDeploymentParser.KW_TITLE, 0)

        def restOfLine(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.RestOfLineContext,0)


        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_titleStmt

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTitleStmt" ):
                return visitor.visitTitleStmt(self)
            else:
                return visitor.visitChildren(self)




    def titleStmt(self):

        localctx = PlantUMLDeploymentParser.TitleStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 82, self.RULE_titleStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 685
            self.match(PlantUMLDeploymentParser.KW_TITLE)
            self.state = 687
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 4667911881975922032) != 0) or ((((_la - 67)) & ~0x3f) == 0 and ((1 << (_la - 67)) & 20965343) != 0):
                self.state = 686
                self.restOfLine()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class HeaderStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KW_HEADER(self):
            return self.getToken(PlantUMLDeploymentParser.KW_HEADER, 0)

        def restOfLine(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.RestOfLineContext,0)


        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_headerStmt

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitHeaderStmt" ):
                return visitor.visitHeaderStmt(self)
            else:
                return visitor.visitChildren(self)




    def headerStmt(self):

        localctx = PlantUMLDeploymentParser.HeaderStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 84, self.RULE_headerStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 689
            self.match(PlantUMLDeploymentParser.KW_HEADER)
            self.state = 691
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 4667911881975922032) != 0) or ((((_la - 67)) & ~0x3f) == 0 and ((1 << (_la - 67)) & 20965343) != 0):
                self.state = 690
                self.restOfLine()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FooterStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KW_FOOTER(self):
            return self.getToken(PlantUMLDeploymentParser.KW_FOOTER, 0)

        def restOfLine(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.RestOfLineContext,0)


        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_footerStmt

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFooterStmt" ):
                return visitor.visitFooterStmt(self)
            else:
                return visitor.visitChildren(self)




    def footerStmt(self):

        localctx = PlantUMLDeploymentParser.FooterStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 86, self.RULE_footerStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 693
            self.match(PlantUMLDeploymentParser.KW_FOOTER)
            self.state = 695
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 4667911881975922032) != 0) or ((((_la - 67)) & ~0x3f) == 0 and ((1 << (_la - 67)) & 20965343) != 0):
                self.state = 694
                self.restOfLine()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CaptionStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KW_CAPTION(self):
            return self.getToken(PlantUMLDeploymentParser.KW_CAPTION, 0)

        def restOfLine(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.RestOfLineContext,0)


        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_captionStmt

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCaptionStmt" ):
                return visitor.visitCaptionStmt(self)
            else:
                return visitor.visitChildren(self)




    def captionStmt(self):

        localctx = PlantUMLDeploymentParser.CaptionStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 88, self.RULE_captionStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 697
            self.match(PlantUMLDeploymentParser.KW_CAPTION)
            self.state = 699
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 4667911881975922032) != 0) or ((((_la - 67)) & ~0x3f) == 0 and ((1 << (_la - 67)) & 20965343) != 0):
                self.state = 698
                self.restOfLine()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LegendBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KW_LEGEND(self):
            return self.getToken(PlantUMLDeploymentParser.KW_LEGEND, 0)

        def KW_END_LEGEND(self):
            return self.getToken(PlantUMLDeploymentParser.KW_END_LEGEND, 0)

        def legendAlign(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.LegendAlignContext,0)


        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.NEWLINE)
            else:
                return self.getToken(PlantUMLDeploymentParser.NEWLINE, i)

        def noteBodyLine(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PlantUMLDeploymentParser.NoteBodyLineContext)
            else:
                return self.getTypedRuleContext(PlantUMLDeploymentParser.NoteBodyLineContext,i)


        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_legendBlock

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLegendBlock" ):
                return visitor.visitLegendBlock(self)
            else:
                return visitor.visitChildren(self)




    def legendBlock(self):

        localctx = PlantUMLDeploymentParser.LegendBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 90, self.RULE_legendBlock)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 701
            self.match(PlantUMLDeploymentParser.KW_LEGEND)
            self.state = 703
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 4611897124659920896) != 0):
                self.state = 702
                self.legendAlign()


            self.state = 706 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 705
                    self.match(PlantUMLDeploymentParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 708 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,98,self._ctx)

            self.state = 711 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 710
                self.noteBodyLine()
                self.state = 713 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 4667911881975922032) != 0) or ((((_la - 67)) & ~0x3f) == 0 and ((1 << (_la - 67)) & 54519775) != 0)):
                    break

            self.state = 715
            self.match(PlantUMLDeploymentParser.KW_END_LEGEND)
            self.state = 717 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 716
                    self.match(PlantUMLDeploymentParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 719 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,100,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LegendAlignContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KW_LEFT(self):
            return self.getToken(PlantUMLDeploymentParser.KW_LEFT, 0)

        def KW_RIGHT(self):
            return self.getToken(PlantUMLDeploymentParser.KW_RIGHT, 0)

        def KW_CENTER(self):
            return self.getToken(PlantUMLDeploymentParser.KW_CENTER, 0)

        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_legendAlign

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLegendAlign" ):
                return visitor.visitLegendAlign(self)
            else:
                return visitor.visitChildren(self)




    def legendAlign(self):

        localctx = PlantUMLDeploymentParser.LegendAlignContext(self, self._ctx, self.state)
        self.enterRule(localctx, 92, self.RULE_legendAlign)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 721
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 4611897124659920896) != 0)):
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


    class PragmaStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def BANG(self):
            return self.getToken(PlantUMLDeploymentParser.BANG, 0)

        def KW_PRAGMA(self):
            return self.getToken(PlantUMLDeploymentParser.KW_PRAGMA, 0)

        def ID(self):
            return self.getToken(PlantUMLDeploymentParser.ID, 0)

        def restOfLine(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.RestOfLineContext,0)


        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_pragmaStmt

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPragmaStmt" ):
                return visitor.visitPragmaStmt(self)
            else:
                return visitor.visitChildren(self)




    def pragmaStmt(self):

        localctx = PlantUMLDeploymentParser.PragmaStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 94, self.RULE_pragmaStmt)
        self._la = 0 # Token type
        try:
            self.state = 734
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,103,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 723
                self.match(PlantUMLDeploymentParser.BANG)
                self.state = 724
                self.match(PlantUMLDeploymentParser.KW_PRAGMA)
                self.state = 725
                self.match(PlantUMLDeploymentParser.ID)
                self.state = 727
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & 4667911881975922032) != 0) or ((((_la - 67)) & ~0x3f) == 0 and ((1 << (_la - 67)) & 20965343) != 0):
                    self.state = 726
                    self.restOfLine()


                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 729
                self.match(PlantUMLDeploymentParser.BANG)
                self.state = 730
                self.match(PlantUMLDeploymentParser.ID)
                self.state = 732
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & 4667911881975922032) != 0) or ((((_la - 67)) & ~0x3f) == 0 and ((1 << (_la - 67)) & 20965343) != 0):
                    self.state = 731
                    self.restOfLine()


                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ScaleStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KW_SCALE(self):
            return self.getToken(PlantUMLDeploymentParser.KW_SCALE, 0)

        def restOfLine(self):
            return self.getTypedRuleContext(PlantUMLDeploymentParser.RestOfLineContext,0)


        def getRuleIndex(self):
            return PlantUMLDeploymentParser.RULE_scaleStmt

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitScaleStmt" ):
                return visitor.visitScaleStmt(self)
            else:
                return visitor.visitChildren(self)




    def scaleStmt(self):

        localctx = PlantUMLDeploymentParser.ScaleStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 96, self.RULE_scaleStmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 736
            self.match(PlantUMLDeploymentParser.KW_SCALE)
            self.state = 737
            self.restOfLine()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





