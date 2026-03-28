# Generated from PlantUMLDeployment.g4 by ANTLR 4.13.0
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
        4,1,93,715,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,
        7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,26,7,26,
        2,27,7,27,2,28,7,28,2,29,7,29,2,30,7,30,2,31,7,31,2,32,7,32,2,33,
        7,33,2,34,7,34,2,35,7,35,2,36,7,36,2,37,7,37,2,38,7,38,2,39,7,39,
        2,40,7,40,2,41,7,41,2,42,7,42,2,43,7,43,2,44,7,44,2,45,7,45,2,46,
        7,46,2,47,7,47,1,0,5,0,98,8,0,10,0,12,0,101,9,0,1,0,1,0,3,0,105,
        8,0,1,0,4,0,108,8,0,11,0,12,0,109,1,0,5,0,113,8,0,10,0,12,0,116,
        9,0,1,0,1,0,5,0,120,8,0,10,0,12,0,123,9,0,1,0,1,0,1,1,1,1,1,1,5,
        1,130,8,1,10,1,12,1,133,9,1,1,1,3,1,136,8,1,1,2,1,2,4,2,140,8,2,
        11,2,12,2,141,1,2,1,2,1,2,4,2,147,8,2,11,2,12,2,148,1,2,1,2,4,2,
        153,8,2,11,2,12,2,154,1,2,1,2,1,2,1,2,1,2,4,2,162,8,2,11,2,12,2,
        163,1,2,1,2,1,2,4,2,169,8,2,11,2,12,2,170,1,2,1,2,4,2,175,8,2,11,
        2,12,2,176,1,2,1,2,4,2,181,8,2,11,2,12,2,182,1,2,1,2,4,2,187,8,2,
        11,2,12,2,188,1,2,1,2,4,2,193,8,2,11,2,12,2,194,1,2,1,2,4,2,199,
        8,2,11,2,12,2,200,1,2,1,2,4,2,205,8,2,11,2,12,2,206,1,2,1,2,1,2,
        4,2,212,8,2,11,2,12,2,213,1,2,1,2,4,2,218,8,2,11,2,12,2,219,1,2,
        1,2,4,2,224,8,2,11,2,12,2,225,1,2,1,2,4,2,230,8,2,11,2,12,2,231,
        1,2,4,2,235,8,2,11,2,12,2,236,3,2,239,8,2,1,3,1,3,3,3,243,8,3,1,
        3,5,3,246,8,3,10,3,12,3,249,9,3,1,3,1,3,3,3,253,8,3,1,3,5,3,256,
        8,3,10,3,12,3,259,9,3,1,3,1,3,1,3,3,3,264,8,3,1,3,5,3,267,8,3,10,
        3,12,3,270,9,3,1,3,1,3,3,3,274,8,3,1,3,5,3,277,8,3,10,3,12,3,280,
        9,3,1,3,1,3,1,3,3,3,285,8,3,1,3,5,3,288,8,3,10,3,12,3,291,9,3,1,
        3,3,3,294,8,3,3,3,296,8,3,1,4,1,4,1,4,1,4,1,5,1,5,3,5,304,8,5,1,
        5,3,5,307,8,5,1,5,5,5,310,8,5,10,5,12,5,313,9,5,1,5,1,5,4,5,317,
        8,5,11,5,12,5,318,1,5,5,5,322,8,5,10,5,12,5,325,9,5,1,5,1,5,4,5,
        329,8,5,11,5,12,5,330,1,6,1,6,4,6,335,8,6,11,6,12,6,336,1,6,1,6,
        1,6,4,6,342,8,6,11,6,12,6,343,1,6,1,6,4,6,348,8,6,11,6,12,6,349,
        1,6,1,6,4,6,354,8,6,11,6,12,6,355,1,6,1,6,1,6,4,6,361,8,6,11,6,12,
        6,362,1,6,1,6,4,6,367,8,6,11,6,12,6,368,1,6,4,6,372,8,6,11,6,12,
        6,373,3,6,376,8,6,1,7,1,7,1,7,1,7,1,7,1,7,3,7,384,8,7,1,8,1,8,1,
        8,4,8,389,8,8,11,8,12,8,390,1,8,5,8,394,8,8,10,8,12,8,397,9,8,1,
        8,1,8,4,8,401,8,8,11,8,12,8,402,1,9,1,9,1,10,1,10,1,11,1,11,1,11,
        1,12,1,12,1,12,3,12,415,8,12,1,13,1,13,1,14,1,14,1,14,1,14,1,15,
        3,15,424,8,15,1,15,3,15,427,8,15,1,16,1,16,1,16,1,16,1,16,1,16,1,
        17,1,17,1,18,1,18,1,19,3,19,440,8,19,1,20,1,20,1,20,1,20,1,20,1,
        20,1,20,1,20,1,20,1,20,1,20,1,20,1,20,1,20,1,20,1,20,1,20,1,20,1,
        20,1,20,1,20,1,20,1,20,1,20,1,20,1,20,1,20,1,20,1,20,1,20,4,20,472,
        8,20,11,20,12,20,473,1,21,1,21,1,21,1,21,1,21,3,21,481,8,21,1,22,
        1,22,1,23,1,23,1,24,1,24,1,24,1,24,1,24,1,24,3,24,493,8,24,1,24,
        1,24,1,24,1,24,3,24,499,8,24,1,25,1,25,1,25,1,25,1,25,4,25,506,8,
        25,11,25,12,25,507,1,25,4,25,511,8,25,11,25,12,25,512,1,25,1,25,
        4,25,517,8,25,11,25,12,25,518,1,25,1,25,1,25,1,25,4,25,525,8,25,
        11,25,12,25,526,1,25,4,25,530,8,25,11,25,12,25,531,1,25,1,25,4,25,
        536,8,25,11,25,12,25,537,3,25,540,8,25,1,26,1,26,1,27,1,27,4,27,
        546,8,27,11,27,12,27,547,1,27,4,27,551,8,27,11,27,12,27,552,3,27,
        555,8,27,1,28,1,28,1,28,3,28,560,8,28,1,28,1,28,4,28,564,8,28,11,
        28,12,28,565,1,28,4,28,569,8,28,11,28,12,28,570,1,28,1,28,4,28,575,
        8,28,11,28,12,28,576,1,29,1,29,1,29,1,29,1,29,1,29,3,29,585,8,29,
        1,29,1,29,1,30,1,30,4,30,591,8,30,11,30,12,30,592,1,30,4,30,596,
        8,30,11,30,12,30,597,3,30,600,8,30,1,31,1,31,1,31,3,31,605,8,31,
        1,32,1,32,1,32,1,32,4,32,611,8,32,11,32,12,32,612,1,32,5,32,616,
        8,32,10,32,12,32,619,9,32,1,32,1,32,4,32,623,8,32,11,32,12,32,624,
        1,33,1,33,1,33,5,33,630,8,33,10,33,12,33,633,9,33,1,34,1,34,1,34,
        4,34,638,8,34,11,34,12,34,639,1,34,4,34,643,8,34,11,34,12,34,644,
        3,34,647,8,34,1,35,1,35,1,35,1,36,1,36,1,37,1,37,1,38,1,38,1,38,
        1,38,1,38,1,38,1,38,1,38,3,38,664,8,38,1,39,1,39,1,40,1,40,3,40,
        670,8,40,1,41,1,41,3,41,674,8,41,1,42,1,42,3,42,678,8,42,1,43,1,
        43,3,43,682,8,43,1,44,1,44,3,44,686,8,44,1,44,4,44,689,8,44,11,44,
        12,44,690,1,44,4,44,694,8,44,11,44,12,44,695,1,44,1,44,4,44,700,
        8,44,11,44,12,44,701,1,45,1,45,1,46,1,46,1,46,1,46,3,46,710,8,46,
        1,47,1,47,1,47,1,47,0,0,48,0,2,4,6,8,10,12,14,16,18,20,22,24,26,
        28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60,62,64,66,68,70,
        72,74,76,78,80,82,84,86,88,90,92,94,0,9,1,0,10,36,2,0,73,73,88,88,
        1,0,87,88,2,0,88,88,91,91,3,0,4,6,73,73,88,88,1,0,46,49,1,0,51,53,
        2,0,8,9,83,83,2,0,46,47,62,62,825,0,99,1,0,0,0,2,135,1,0,0,0,4,238,
        1,0,0,0,6,295,1,0,0,0,8,297,1,0,0,0,10,301,1,0,0,0,12,375,1,0,0,
        0,14,383,1,0,0,0,16,385,1,0,0,0,18,404,1,0,0,0,20,406,1,0,0,0,22,
        408,1,0,0,0,24,414,1,0,0,0,26,416,1,0,0,0,28,418,1,0,0,0,30,423,
        1,0,0,0,32,428,1,0,0,0,34,434,1,0,0,0,36,436,1,0,0,0,38,439,1,0,
        0,0,40,471,1,0,0,0,42,475,1,0,0,0,44,482,1,0,0,0,46,484,1,0,0,0,
        48,498,1,0,0,0,50,539,1,0,0,0,52,541,1,0,0,0,54,554,1,0,0,0,56,556,
        1,0,0,0,58,578,1,0,0,0,60,599,1,0,0,0,62,601,1,0,0,0,64,606,1,0,
        0,0,66,626,1,0,0,0,68,646,1,0,0,0,70,648,1,0,0,0,72,651,1,0,0,0,
        74,653,1,0,0,0,76,663,1,0,0,0,78,665,1,0,0,0,80,667,1,0,0,0,82,671,
        1,0,0,0,84,675,1,0,0,0,86,679,1,0,0,0,88,683,1,0,0,0,90,703,1,0,
        0,0,92,705,1,0,0,0,94,711,1,0,0,0,96,98,5,92,0,0,97,96,1,0,0,0,98,
        101,1,0,0,0,99,97,1,0,0,0,99,100,1,0,0,0,100,102,1,0,0,0,101,99,
        1,0,0,0,102,104,5,2,0,0,103,105,3,2,1,0,104,103,1,0,0,0,104,105,
        1,0,0,0,105,107,1,0,0,0,106,108,5,92,0,0,107,106,1,0,0,0,108,109,
        1,0,0,0,109,107,1,0,0,0,109,110,1,0,0,0,110,114,1,0,0,0,111,113,
        3,4,2,0,112,111,1,0,0,0,113,116,1,0,0,0,114,112,1,0,0,0,114,115,
        1,0,0,0,115,117,1,0,0,0,116,114,1,0,0,0,117,121,5,3,0,0,118,120,
        5,92,0,0,119,118,1,0,0,0,120,123,1,0,0,0,121,119,1,0,0,0,121,122,
        1,0,0,0,122,124,1,0,0,0,123,121,1,0,0,0,124,125,5,0,0,1,125,1,1,
        0,0,0,126,131,5,88,0,0,127,128,5,1,0,0,128,130,5,88,0,0,129,127,
        1,0,0,0,130,133,1,0,0,0,131,129,1,0,0,0,131,132,1,0,0,0,132,136,
        1,0,0,0,133,131,1,0,0,0,134,136,5,73,0,0,135,126,1,0,0,0,135,134,
        1,0,0,0,136,3,1,0,0,0,137,139,3,6,3,0,138,140,5,92,0,0,139,138,1,
        0,0,0,140,141,1,0,0,0,141,139,1,0,0,0,141,142,1,0,0,0,142,239,1,
        0,0,0,143,239,3,10,5,0,144,146,3,42,21,0,145,147,5,92,0,0,146,145,
        1,0,0,0,147,148,1,0,0,0,148,146,1,0,0,0,148,149,1,0,0,0,149,239,
        1,0,0,0,150,152,3,48,24,0,151,153,5,92,0,0,152,151,1,0,0,0,153,154,
        1,0,0,0,154,152,1,0,0,0,154,155,1,0,0,0,155,239,1,0,0,0,156,239,
        3,50,25,0,157,239,3,16,8,0,158,239,3,56,28,0,159,161,3,62,31,0,160,
        162,5,92,0,0,161,160,1,0,0,0,162,163,1,0,0,0,163,161,1,0,0,0,163,
        164,1,0,0,0,164,239,1,0,0,0,165,239,3,64,32,0,166,168,3,70,35,0,
        167,169,5,92,0,0,168,167,1,0,0,0,169,170,1,0,0,0,170,168,1,0,0,0,
        170,171,1,0,0,0,171,239,1,0,0,0,172,174,3,76,38,0,173,175,5,92,0,
        0,174,173,1,0,0,0,175,176,1,0,0,0,176,174,1,0,0,0,176,177,1,0,0,
        0,177,239,1,0,0,0,178,180,3,78,39,0,179,181,5,92,0,0,180,179,1,0,
        0,0,181,182,1,0,0,0,182,180,1,0,0,0,182,183,1,0,0,0,183,239,1,0,
        0,0,184,186,3,80,40,0,185,187,5,92,0,0,186,185,1,0,0,0,187,188,1,
        0,0,0,188,186,1,0,0,0,188,189,1,0,0,0,189,239,1,0,0,0,190,192,3,
        82,41,0,191,193,5,92,0,0,192,191,1,0,0,0,193,194,1,0,0,0,194,192,
        1,0,0,0,194,195,1,0,0,0,195,239,1,0,0,0,196,198,3,84,42,0,197,199,
        5,92,0,0,198,197,1,0,0,0,199,200,1,0,0,0,200,198,1,0,0,0,200,201,
        1,0,0,0,201,239,1,0,0,0,202,204,3,86,43,0,203,205,5,92,0,0,204,203,
        1,0,0,0,205,206,1,0,0,0,206,204,1,0,0,0,206,207,1,0,0,0,207,239,
        1,0,0,0,208,239,3,88,44,0,209,211,3,92,46,0,210,212,5,92,0,0,211,
        210,1,0,0,0,212,213,1,0,0,0,213,211,1,0,0,0,213,214,1,0,0,0,214,
        239,1,0,0,0,215,217,3,94,47,0,216,218,5,92,0,0,217,216,1,0,0,0,218,
        219,1,0,0,0,219,217,1,0,0,0,219,220,1,0,0,0,220,239,1,0,0,0,221,
        223,5,89,0,0,222,224,5,92,0,0,223,222,1,0,0,0,224,225,1,0,0,0,225,
        223,1,0,0,0,225,226,1,0,0,0,226,239,1,0,0,0,227,229,5,90,0,0,228,
        230,5,92,0,0,229,228,1,0,0,0,230,231,1,0,0,0,231,229,1,0,0,0,231,
        232,1,0,0,0,232,239,1,0,0,0,233,235,5,92,0,0,234,233,1,0,0,0,235,
        236,1,0,0,0,236,234,1,0,0,0,236,237,1,0,0,0,237,239,1,0,0,0,238,
        137,1,0,0,0,238,143,1,0,0,0,238,144,1,0,0,0,238,150,1,0,0,0,238,
        156,1,0,0,0,238,157,1,0,0,0,238,158,1,0,0,0,238,159,1,0,0,0,238,
        165,1,0,0,0,238,166,1,0,0,0,238,172,1,0,0,0,238,178,1,0,0,0,238,
        184,1,0,0,0,238,190,1,0,0,0,238,196,1,0,0,0,238,202,1,0,0,0,238,
        208,1,0,0,0,238,209,1,0,0,0,238,215,1,0,0,0,238,221,1,0,0,0,238,
        227,1,0,0,0,238,234,1,0,0,0,239,5,1,0,0,0,240,242,5,4,0,0,241,243,
        3,22,11,0,242,241,1,0,0,0,242,243,1,0,0,0,243,247,1,0,0,0,244,246,
        3,24,12,0,245,244,1,0,0,0,246,249,1,0,0,0,247,245,1,0,0,0,247,248,
        1,0,0,0,248,296,1,0,0,0,249,247,1,0,0,0,250,252,5,5,0,0,251,253,
        3,22,11,0,252,251,1,0,0,0,252,253,1,0,0,0,253,257,1,0,0,0,254,256,
        3,24,12,0,255,254,1,0,0,0,256,259,1,0,0,0,257,255,1,0,0,0,257,258,
        1,0,0,0,258,296,1,0,0,0,259,257,1,0,0,0,260,261,5,7,0,0,261,263,
        3,20,10,0,262,264,3,22,11,0,263,262,1,0,0,0,263,264,1,0,0,0,264,
        268,1,0,0,0,265,267,3,24,12,0,266,265,1,0,0,0,267,270,1,0,0,0,268,
        266,1,0,0,0,268,269,1,0,0,0,269,296,1,0,0,0,270,268,1,0,0,0,271,
        273,5,6,0,0,272,274,3,22,11,0,273,272,1,0,0,0,273,274,1,0,0,0,274,
        278,1,0,0,0,275,277,3,24,12,0,276,275,1,0,0,0,277,280,1,0,0,0,278,
        276,1,0,0,0,278,279,1,0,0,0,279,296,1,0,0,0,280,278,1,0,0,0,281,
        282,3,18,9,0,282,284,3,20,10,0,283,285,3,22,11,0,284,283,1,0,0,0,
        284,285,1,0,0,0,285,289,1,0,0,0,286,288,3,24,12,0,287,286,1,0,0,
        0,288,291,1,0,0,0,289,287,1,0,0,0,289,290,1,0,0,0,290,293,1,0,0,
        0,291,289,1,0,0,0,292,294,3,8,4,0,293,292,1,0,0,0,293,294,1,0,0,
        0,294,296,1,0,0,0,295,240,1,0,0,0,295,250,1,0,0,0,295,260,1,0,0,
        0,295,271,1,0,0,0,295,281,1,0,0,0,296,7,1,0,0,0,297,298,5,76,0,0,
        298,299,3,38,19,0,299,300,5,77,0,0,300,9,1,0,0,0,301,303,3,18,9,
        0,302,304,3,20,10,0,303,302,1,0,0,0,303,304,1,0,0,0,304,306,1,0,
        0,0,305,307,3,22,11,0,306,305,1,0,0,0,306,307,1,0,0,0,307,311,1,
        0,0,0,308,310,3,24,12,0,309,308,1,0,0,0,310,313,1,0,0,0,311,309,
        1,0,0,0,311,312,1,0,0,0,312,314,1,0,0,0,313,311,1,0,0,0,314,316,
        5,78,0,0,315,317,5,92,0,0,316,315,1,0,0,0,317,318,1,0,0,0,318,316,
        1,0,0,0,318,319,1,0,0,0,319,323,1,0,0,0,320,322,3,12,6,0,321,320,
        1,0,0,0,322,325,1,0,0,0,323,321,1,0,0,0,323,324,1,0,0,0,324,326,
        1,0,0,0,325,323,1,0,0,0,326,328,5,79,0,0,327,329,5,92,0,0,328,327,
        1,0,0,0,329,330,1,0,0,0,330,328,1,0,0,0,330,331,1,0,0,0,331,11,1,
        0,0,0,332,334,3,6,3,0,333,335,5,92,0,0,334,333,1,0,0,0,335,336,1,
        0,0,0,336,334,1,0,0,0,336,337,1,0,0,0,337,376,1,0,0,0,338,376,3,
        10,5,0,339,341,3,14,7,0,340,342,5,92,0,0,341,340,1,0,0,0,342,343,
        1,0,0,0,343,341,1,0,0,0,343,344,1,0,0,0,344,376,1,0,0,0,345,347,
        3,42,21,0,346,348,5,92,0,0,347,346,1,0,0,0,348,349,1,0,0,0,349,347,
        1,0,0,0,349,350,1,0,0,0,350,376,1,0,0,0,351,353,3,48,24,0,352,354,
        5,92,0,0,353,352,1,0,0,0,354,355,1,0,0,0,355,353,1,0,0,0,355,356,
        1,0,0,0,356,376,1,0,0,0,357,376,3,50,25,0,358,360,5,89,0,0,359,361,
        5,92,0,0,360,359,1,0,0,0,361,362,1,0,0,0,362,360,1,0,0,0,362,363,
        1,0,0,0,363,376,1,0,0,0,364,366,5,90,0,0,365,367,5,92,0,0,366,365,
        1,0,0,0,367,368,1,0,0,0,368,366,1,0,0,0,368,369,1,0,0,0,369,376,
        1,0,0,0,370,372,5,92,0,0,371,370,1,0,0,0,372,373,1,0,0,0,373,371,
        1,0,0,0,373,374,1,0,0,0,374,376,1,0,0,0,375,332,1,0,0,0,375,338,
        1,0,0,0,375,339,1,0,0,0,375,345,1,0,0,0,375,351,1,0,0,0,375,357,
        1,0,0,0,375,358,1,0,0,0,375,364,1,0,0,0,375,371,1,0,0,0,376,13,1,
        0,0,0,377,378,5,37,0,0,378,384,3,20,10,0,379,380,5,38,0,0,380,384,
        3,20,10,0,381,382,5,39,0,0,382,384,3,20,10,0,383,377,1,0,0,0,383,
        379,1,0,0,0,383,381,1,0,0,0,384,15,1,0,0,0,385,386,5,41,0,0,386,
        388,5,78,0,0,387,389,5,92,0,0,388,387,1,0,0,0,389,390,1,0,0,0,390,
        388,1,0,0,0,390,391,1,0,0,0,391,395,1,0,0,0,392,394,3,4,2,0,393,
        392,1,0,0,0,394,397,1,0,0,0,395,393,1,0,0,0,395,396,1,0,0,0,396,
        398,1,0,0,0,397,395,1,0,0,0,398,400,5,79,0,0,399,401,5,92,0,0,400,
        399,1,0,0,0,401,402,1,0,0,0,402,400,1,0,0,0,402,403,1,0,0,0,403,
        17,1,0,0,0,404,405,7,0,0,0,405,19,1,0,0,0,406,407,7,1,0,0,407,21,
        1,0,0,0,408,409,5,40,0,0,409,410,3,20,10,0,410,23,1,0,0,0,411,415,
        3,28,14,0,412,415,3,26,13,0,413,415,5,8,0,0,414,411,1,0,0,0,414,
        412,1,0,0,0,414,413,1,0,0,0,415,25,1,0,0,0,416,417,5,71,0,0,417,
        27,1,0,0,0,418,419,5,68,0,0,419,420,3,30,15,0,420,421,5,69,0,0,421,
        29,1,0,0,0,422,424,3,32,16,0,423,422,1,0,0,0,423,424,1,0,0,0,424,
        426,1,0,0,0,425,427,3,36,18,0,426,425,1,0,0,0,426,427,1,0,0,0,427,
        31,1,0,0,0,428,429,5,74,0,0,429,430,3,34,17,0,430,431,5,82,0,0,431,
        432,3,26,13,0,432,433,5,75,0,0,433,33,1,0,0,0,434,435,7,2,0,0,435,
        35,1,0,0,0,436,437,7,3,0,0,437,37,1,0,0,0,438,440,3,40,20,0,439,
        438,1,0,0,0,439,440,1,0,0,0,440,39,1,0,0,0,441,472,5,88,0,0,442,
        472,5,73,0,0,443,472,5,87,0,0,444,472,5,71,0,0,445,472,5,8,0,0,446,
        472,5,91,0,0,447,472,5,81,0,0,448,472,5,82,0,0,449,472,5,83,0,0,
        450,472,5,84,0,0,451,472,5,80,0,0,452,472,5,74,0,0,453,472,5,75,
        0,0,454,472,5,76,0,0,455,472,5,77,0,0,456,472,5,85,0,0,457,472,5,
        86,0,0,458,472,5,68,0,0,459,472,5,69,0,0,460,472,5,40,0,0,461,472,
        5,50,0,0,462,472,5,54,0,0,463,472,5,46,0,0,464,472,5,47,0,0,465,
        472,5,48,0,0,466,472,5,49,0,0,467,472,5,62,0,0,468,472,5,67,0,0,
        469,472,5,55,0,0,470,472,3,18,9,0,471,441,1,0,0,0,471,442,1,0,0,
        0,471,443,1,0,0,0,471,444,1,0,0,0,471,445,1,0,0,0,471,446,1,0,0,
        0,471,447,1,0,0,0,471,448,1,0,0,0,471,449,1,0,0,0,471,450,1,0,0,
        0,471,451,1,0,0,0,471,452,1,0,0,0,471,453,1,0,0,0,471,454,1,0,0,
        0,471,455,1,0,0,0,471,456,1,0,0,0,471,457,1,0,0,0,471,458,1,0,0,
        0,471,459,1,0,0,0,471,460,1,0,0,0,471,461,1,0,0,0,471,462,1,0,0,
        0,471,463,1,0,0,0,471,464,1,0,0,0,471,465,1,0,0,0,471,466,1,0,0,
        0,471,467,1,0,0,0,471,468,1,0,0,0,471,469,1,0,0,0,471,470,1,0,0,
        0,472,473,1,0,0,0,473,471,1,0,0,0,473,474,1,0,0,0,474,41,1,0,0,0,
        475,476,3,44,22,0,476,477,5,70,0,0,477,480,3,44,22,0,478,479,5,81,
        0,0,479,481,3,46,23,0,480,478,1,0,0,0,480,481,1,0,0,0,481,43,1,0,
        0,0,482,483,7,4,0,0,483,45,1,0,0,0,484,485,3,40,20,0,485,47,1,0,
        0,0,486,487,5,45,0,0,487,488,3,52,26,0,488,489,5,50,0,0,489,492,
        3,44,22,0,490,491,5,81,0,0,491,493,3,40,20,0,492,490,1,0,0,0,492,
        493,1,0,0,0,493,499,1,0,0,0,494,495,5,45,0,0,495,496,5,73,0,0,496,
        497,5,40,0,0,497,499,3,20,10,0,498,486,1,0,0,0,498,494,1,0,0,0,499,
        49,1,0,0,0,500,501,5,45,0,0,501,502,3,52,26,0,502,503,5,50,0,0,503,
        505,3,44,22,0,504,506,5,92,0,0,505,504,1,0,0,0,506,507,1,0,0,0,507,
        505,1,0,0,0,507,508,1,0,0,0,508,510,1,0,0,0,509,511,3,54,27,0,510,
        509,1,0,0,0,511,512,1,0,0,0,512,510,1,0,0,0,512,513,1,0,0,0,513,
        514,1,0,0,0,514,516,5,42,0,0,515,517,5,92,0,0,516,515,1,0,0,0,517,
        518,1,0,0,0,518,516,1,0,0,0,518,519,1,0,0,0,519,540,1,0,0,0,520,
        521,5,45,0,0,521,522,5,40,0,0,522,524,3,20,10,0,523,525,5,92,0,0,
        524,523,1,0,0,0,525,526,1,0,0,0,526,524,1,0,0,0,526,527,1,0,0,0,
        527,529,1,0,0,0,528,530,3,54,27,0,529,528,1,0,0,0,530,531,1,0,0,
        0,531,529,1,0,0,0,531,532,1,0,0,0,532,533,1,0,0,0,533,535,5,42,0,
        0,534,536,5,92,0,0,535,534,1,0,0,0,536,537,1,0,0,0,537,535,1,0,0,
        0,537,538,1,0,0,0,538,540,1,0,0,0,539,500,1,0,0,0,539,520,1,0,0,
        0,540,51,1,0,0,0,541,542,7,5,0,0,542,53,1,0,0,0,543,545,3,40,20,
        0,544,546,5,92,0,0,545,544,1,0,0,0,546,547,1,0,0,0,547,545,1,0,0,
        0,547,548,1,0,0,0,548,555,1,0,0,0,549,551,5,92,0,0,550,549,1,0,0,
        0,551,552,1,0,0,0,552,550,1,0,0,0,552,553,1,0,0,0,553,555,1,0,0,
        0,554,543,1,0,0,0,554,550,1,0,0,0,555,55,1,0,0,0,556,557,5,66,0,
        0,557,559,5,8,0,0,558,560,3,58,29,0,559,558,1,0,0,0,559,560,1,0,
        0,0,560,561,1,0,0,0,561,563,5,78,0,0,562,564,5,92,0,0,563,562,1,
        0,0,0,564,565,1,0,0,0,565,563,1,0,0,0,565,566,1,0,0,0,566,568,1,
        0,0,0,567,569,3,60,30,0,568,567,1,0,0,0,569,570,1,0,0,0,570,568,
        1,0,0,0,570,571,1,0,0,0,571,572,1,0,0,0,572,574,5,79,0,0,573,575,
        5,92,0,0,574,573,1,0,0,0,575,576,1,0,0,0,576,574,1,0,0,0,576,577,
        1,0,0,0,577,57,1,0,0,0,578,579,5,76,0,0,579,580,5,87,0,0,580,581,
        5,67,0,0,581,584,5,87,0,0,582,583,5,80,0,0,583,585,5,87,0,0,584,
        582,1,0,0,0,584,585,1,0,0,0,585,586,1,0,0,0,586,587,5,77,0,0,587,
        59,1,0,0,0,588,590,5,72,0,0,589,591,5,92,0,0,590,589,1,0,0,0,591,
        592,1,0,0,0,592,590,1,0,0,0,592,593,1,0,0,0,593,600,1,0,0,0,594,
        596,5,92,0,0,595,594,1,0,0,0,596,597,1,0,0,0,597,595,1,0,0,0,597,
        598,1,0,0,0,598,600,1,0,0,0,599,588,1,0,0,0,599,595,1,0,0,0,600,
        61,1,0,0,0,601,602,5,63,0,0,602,604,3,66,33,0,603,605,3,40,20,0,
        604,603,1,0,0,0,604,605,1,0,0,0,605,63,1,0,0,0,606,607,5,63,0,0,
        607,608,3,66,33,0,608,610,5,78,0,0,609,611,5,92,0,0,610,609,1,0,
        0,0,611,612,1,0,0,0,612,610,1,0,0,0,612,613,1,0,0,0,613,617,1,0,
        0,0,614,616,3,68,34,0,615,614,1,0,0,0,616,619,1,0,0,0,617,615,1,
        0,0,0,617,618,1,0,0,0,618,620,1,0,0,0,619,617,1,0,0,0,620,622,5,
        79,0,0,621,623,5,92,0,0,622,621,1,0,0,0,623,624,1,0,0,0,624,622,
        1,0,0,0,624,625,1,0,0,0,625,65,1,0,0,0,626,631,5,88,0,0,627,628,
        5,1,0,0,628,630,5,88,0,0,629,627,1,0,0,0,630,633,1,0,0,0,631,629,
        1,0,0,0,631,632,1,0,0,0,632,67,1,0,0,0,633,631,1,0,0,0,634,635,5,
        88,0,0,635,637,3,40,20,0,636,638,5,92,0,0,637,636,1,0,0,0,638,639,
        1,0,0,0,639,637,1,0,0,0,639,640,1,0,0,0,640,647,1,0,0,0,641,643,
        5,92,0,0,642,641,1,0,0,0,643,644,1,0,0,0,644,642,1,0,0,0,644,645,
        1,0,0,0,645,647,1,0,0,0,646,634,1,0,0,0,646,642,1,0,0,0,647,69,1,
        0,0,0,648,649,3,72,36,0,649,650,3,74,37,0,650,71,1,0,0,0,651,652,
        7,6,0,0,652,73,1,0,0,0,653,654,7,7,0,0,654,75,1,0,0,0,655,656,5,
        46,0,0,656,657,5,54,0,0,657,658,5,47,0,0,658,664,5,55,0,0,659,660,
        5,48,0,0,660,661,5,54,0,0,661,662,5,49,0,0,662,664,5,55,0,0,663,
        655,1,0,0,0,663,659,1,0,0,0,664,77,1,0,0,0,665,666,5,56,0,0,666,
        79,1,0,0,0,667,669,5,57,0,0,668,670,3,40,20,0,669,668,1,0,0,0,669,
        670,1,0,0,0,670,81,1,0,0,0,671,673,5,58,0,0,672,674,3,40,20,0,673,
        672,1,0,0,0,673,674,1,0,0,0,674,83,1,0,0,0,675,677,5,59,0,0,676,
        678,3,40,20,0,677,676,1,0,0,0,677,678,1,0,0,0,678,85,1,0,0,0,679,
        681,5,60,0,0,680,682,3,40,20,0,681,680,1,0,0,0,681,682,1,0,0,0,682,
        87,1,0,0,0,683,685,5,61,0,0,684,686,3,90,45,0,685,684,1,0,0,0,685,
        686,1,0,0,0,686,688,1,0,0,0,687,689,5,92,0,0,688,687,1,0,0,0,689,
        690,1,0,0,0,690,688,1,0,0,0,690,691,1,0,0,0,691,693,1,0,0,0,692,
        694,3,54,27,0,693,692,1,0,0,0,694,695,1,0,0,0,695,693,1,0,0,0,695,
        696,1,0,0,0,696,697,1,0,0,0,697,699,5,43,0,0,698,700,5,92,0,0,699,
        698,1,0,0,0,700,701,1,0,0,0,701,699,1,0,0,0,701,702,1,0,0,0,702,
        89,1,0,0,0,703,704,7,8,0,0,704,91,1,0,0,0,705,706,5,84,0,0,706,707,
        5,64,0,0,707,709,5,88,0,0,708,710,3,40,20,0,709,708,1,0,0,0,709,
        710,1,0,0,0,710,93,1,0,0,0,711,712,5,65,0,0,712,713,3,40,20,0,713,
        95,1,0,0,0,99,99,104,109,114,121,131,135,141,148,154,163,170,176,
        182,188,194,200,206,213,219,225,231,236,238,242,247,252,257,263,
        268,273,278,284,289,293,295,303,306,311,318,323,330,336,343,349,
        355,362,368,373,375,383,390,395,402,414,423,426,439,471,473,480,
        492,498,507,512,518,526,531,537,539,547,552,554,559,565,570,576,
        584,592,597,599,604,612,617,624,631,639,644,646,663,669,673,677,
        681,685,690,695,701,709
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
    RULE_skinparamEntry = 34
    RULE_visibilityStmt = 35
    RULE_visibilityKeyword = 36
    RULE_visibilityTarget = 37
    RULE_directionStmt = 38
    RULE_allowMixingStmt = 39
    RULE_titleStmt = 40
    RULE_headerStmt = 41
    RULE_footerStmt = 42
    RULE_captionStmt = 43
    RULE_legendBlock = 44
    RULE_legendAlign = 45
    RULE_pragmaStmt = 46
    RULE_scaleStmt = 47

    ruleNames =  [ "diagram", "filenameHint", "statement", "elementDecl", 
                   "descriptionBody", "elementBlock", "blockStatement", 
                   "portDecl", "togetherBlock", "elementKeyword", "elementName", 
                   "aliasClause", "elementModifier", "colorSpec", "stereotypeClause", 
                   "stereotypeBody", "spotSpec", "spotChar", "stereotypeText", 
                   "bodyText", "restOfLine", "relationStmt", "relationRef", 
                   "labelText", "noteStmt", "noteBlock", "noteSide", "noteBodyLine", 
                   "spriteDecl", "spriteDimension", "spriteRow", "skinparamStmt", 
                   "skinparamBlock", "skinparamPath", "skinparamEntry", 
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
            self.state = 99
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==92:
                self.state = 96
                self.match(PlantUMLDeploymentParser.NEWLINE)
                self.state = 101
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 102
            self.match(PlantUMLDeploymentParser.STARTUML)
            self.state = 104
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==73 or _la==88:
                self.state = 103
                self.filenameHint()


            self.state = 107 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 106
                    self.match(PlantUMLDeploymentParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 109 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,2,self._ctx)

            self.state = 114
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & -4667591649214333712) != 0) or ((((_la - 65)) & ~0x3f) == 0 and ((1 << (_la - 65)) & 193462531) != 0):
                self.state = 111
                self.statement()
                self.state = 116
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 117
            self.match(PlantUMLDeploymentParser.ENDUML)
            self.state = 121
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==92:
                self.state = 118
                self.match(PlantUMLDeploymentParser.NEWLINE)
                self.state = 123
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 124
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
            self.state = 135
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [88]:
                self.enterOuterAlt(localctx, 1)
                self.state = 126
                self.match(PlantUMLDeploymentParser.ID)
                self.state = 131
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==1:
                    self.state = 127
                    self.match(PlantUMLDeploymentParser.T__0)
                    self.state = 128
                    self.match(PlantUMLDeploymentParser.ID)
                    self.state = 133
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass
            elif token in [73]:
                self.enterOuterAlt(localctx, 2)
                self.state = 134
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
            self.state = 238
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,23,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 137
                self.elementDecl()
                self.state = 139 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 138
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 141 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,7,self._ctx)

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 143
                self.elementBlock()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 144
                self.relationStmt()
                self.state = 146 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 145
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 148 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,8,self._ctx)

                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 150
                self.noteStmt()
                self.state = 152 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 151
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 154 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,9,self._ctx)

                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 156
                self.noteBlock()
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 157
                self.togetherBlock()
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 158
                self.spriteDecl()
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 159
                self.skinparamStmt()
                self.state = 161 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 160
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 163 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,10,self._ctx)

                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 165
                self.skinparamBlock()
                pass

            elif la_ == 10:
                self.enterOuterAlt(localctx, 10)
                self.state = 166
                self.visibilityStmt()
                self.state = 168 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 167
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 170 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,11,self._ctx)

                pass

            elif la_ == 11:
                self.enterOuterAlt(localctx, 11)
                self.state = 172
                self.directionStmt()
                self.state = 174 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 173
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 176 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,12,self._ctx)

                pass

            elif la_ == 12:
                self.enterOuterAlt(localctx, 12)
                self.state = 178
                self.allowMixingStmt()
                self.state = 180 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 179
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 182 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,13,self._ctx)

                pass

            elif la_ == 13:
                self.enterOuterAlt(localctx, 13)
                self.state = 184
                self.titleStmt()
                self.state = 186 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 185
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 188 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,14,self._ctx)

                pass

            elif la_ == 14:
                self.enterOuterAlt(localctx, 14)
                self.state = 190
                self.headerStmt()
                self.state = 192 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 191
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 194 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,15,self._ctx)

                pass

            elif la_ == 15:
                self.enterOuterAlt(localctx, 15)
                self.state = 196
                self.footerStmt()
                self.state = 198 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 197
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 200 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,16,self._ctx)

                pass

            elif la_ == 16:
                self.enterOuterAlt(localctx, 16)
                self.state = 202
                self.captionStmt()
                self.state = 204 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 203
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 206 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,17,self._ctx)

                pass

            elif la_ == 17:
                self.enterOuterAlt(localctx, 17)
                self.state = 208
                self.legendBlock()
                pass

            elif la_ == 18:
                self.enterOuterAlt(localctx, 18)
                self.state = 209
                self.pragmaStmt()
                self.state = 211 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 210
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 213 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,18,self._ctx)

                pass

            elif la_ == 19:
                self.enterOuterAlt(localctx, 19)
                self.state = 215
                self.scaleStmt()
                self.state = 217 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 216
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 219 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,19,self._ctx)

                pass

            elif la_ == 20:
                self.enterOuterAlt(localctx, 20)
                self.state = 221
                self.match(PlantUMLDeploymentParser.COMMENT_SINGLE)
                self.state = 223 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 222
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 225 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,20,self._ctx)

                pass

            elif la_ == 21:
                self.enterOuterAlt(localctx, 21)
                self.state = 227
                self.match(PlantUMLDeploymentParser.COMMENT_MULTI)
                self.state = 229 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 228
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 231 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,21,self._ctx)

                pass

            elif la_ == 22:
                self.enterOuterAlt(localctx, 22)
                self.state = 234 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 233
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 236 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,22,self._ctx)

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
            self.state = 295
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [4]:
                self.enterOuterAlt(localctx, 1)
                self.state = 240
                self.match(PlantUMLDeploymentParser.BRACKET_COMP)
                self.state = 242
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==40:
                    self.state = 241
                    self.aliasClause()


                self.state = 247
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while ((((_la - 8)) & ~0x3f) == 0 and ((1 << (_la - 8)) & -8070450532247928831) != 0):
                    self.state = 244
                    self.elementModifier()
                    self.state = 249
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass
            elif token in [5]:
                self.enterOuterAlt(localctx, 2)
                self.state = 250
                self.match(PlantUMLDeploymentParser.ACTOR_COLON)
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
            elif token in [7]:
                self.enterOuterAlt(localctx, 3)
                self.state = 260
                self.match(PlantUMLDeploymentParser.CIRCLE_IFACE)
                self.state = 261
                self.elementName()
                self.state = 263
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==40:
                    self.state = 262
                    self.aliasClause()


                self.state = 268
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while ((((_la - 8)) & ~0x3f) == 0 and ((1 << (_la - 8)) & -8070450532247928831) != 0):
                    self.state = 265
                    self.elementModifier()
                    self.state = 270
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass
            elif token in [6]:
                self.enterOuterAlt(localctx, 4)
                self.state = 271
                self.match(PlantUMLDeploymentParser.USECASE_PAREN)
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
            elif token in [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]:
                self.enterOuterAlt(localctx, 5)
                self.state = 281
                self.elementKeyword()
                self.state = 282
                self.elementName()
                self.state = 284
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==40:
                    self.state = 283
                    self.aliasClause()


                self.state = 289
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while ((((_la - 8)) & ~0x3f) == 0 and ((1 << (_la - 8)) & -8070450532247928831) != 0):
                    self.state = 286
                    self.elementModifier()
                    self.state = 291
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 293
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==76:
                    self.state = 292
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
            self.state = 297
            self.match(PlantUMLDeploymentParser.LBRACK)
            self.state = 298
            self.bodyText()
            self.state = 299
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
            self.state = 301
            self.elementKeyword()
            self.state = 303
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==73 or _la==88:
                self.state = 302
                self.elementName()


            self.state = 306
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==40:
                self.state = 305
                self.aliasClause()


            self.state = 311
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while ((((_la - 8)) & ~0x3f) == 0 and ((1 << (_la - 8)) & -8070450532247928831) != 0):
                self.state = 308
                self.elementModifier()
                self.state = 313
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 314
            self.match(PlantUMLDeploymentParser.LBRACE)
            self.state = 316 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 315
                    self.match(PlantUMLDeploymentParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 318 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,39,self._ctx)

            self.state = 323
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 36283883715824) != 0) or ((((_la - 73)) & ~0x3f) == 0 and ((1 << (_la - 73)) & 753665) != 0):
                self.state = 320
                self.blockStatement()
                self.state = 325
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 326
            self.match(PlantUMLDeploymentParser.RBRACE)
            self.state = 328 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 327
                    self.match(PlantUMLDeploymentParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 330 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,41,self._ctx)

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
            self.state = 375
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,49,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 332
                self.elementDecl()
                self.state = 334 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 333
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 336 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,42,self._ctx)

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 338
                self.elementBlock()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 339
                self.portDecl()
                self.state = 341 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 340
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 343 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,43,self._ctx)

                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 345
                self.relationStmt()
                self.state = 347 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 346
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 349 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,44,self._ctx)

                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 351
                self.noteStmt()
                self.state = 353 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 352
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 355 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,45,self._ctx)

                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 357
                self.noteBlock()
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 358
                self.match(PlantUMLDeploymentParser.COMMENT_SINGLE)
                self.state = 360 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 359
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 362 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,46,self._ctx)

                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 364
                self.match(PlantUMLDeploymentParser.COMMENT_MULTI)
                self.state = 366 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 365
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 368 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,47,self._ctx)

                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 371 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 370
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 373 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,48,self._ctx)

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
            self.state = 383
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [37]:
                self.enterOuterAlt(localctx, 1)
                self.state = 377
                self.match(PlantUMLDeploymentParser.KW_PORT)
                self.state = 378
                self.elementName()
                pass
            elif token in [38]:
                self.enterOuterAlt(localctx, 2)
                self.state = 379
                self.match(PlantUMLDeploymentParser.KW_PORTIN)
                self.state = 380
                self.elementName()
                pass
            elif token in [39]:
                self.enterOuterAlt(localctx, 3)
                self.state = 381
                self.match(PlantUMLDeploymentParser.KW_PORTOUT)
                self.state = 382
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
            self.state = 385
            self.match(PlantUMLDeploymentParser.KW_TOGETHER)
            self.state = 386
            self.match(PlantUMLDeploymentParser.LBRACE)
            self.state = 388 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 387
                    self.match(PlantUMLDeploymentParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 390 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,51,self._ctx)

            self.state = 395
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & -4667591649214333712) != 0) or ((((_la - 65)) & ~0x3f) == 0 and ((1 << (_la - 65)) & 193462531) != 0):
                self.state = 392
                self.statement()
                self.state = 397
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 398
            self.match(PlantUMLDeploymentParser.RBRACE)
            self.state = 400 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 399
                    self.match(PlantUMLDeploymentParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 402 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,53,self._ctx)

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
            self.state = 404
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
            self.state = 406
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
            self.state = 408
            self.match(PlantUMLDeploymentParser.KW_AS)
            self.state = 409
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
            self.state = 414
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [68]:
                self.enterOuterAlt(localctx, 1)
                self.state = 411
                self.stereotypeClause()
                pass
            elif token in [71]:
                self.enterOuterAlt(localctx, 2)
                self.state = 412
                self.colorSpec()
                pass
            elif token in [8]:
                self.enterOuterAlt(localctx, 3)
                self.state = 413
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
            self.state = 416
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
            self.state = 418
            self.match(PlantUMLDeploymentParser.STEREOTYPE_OPEN)
            self.state = 419
            self.stereotypeBody()
            self.state = 420
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
            self.state = 423
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==74:
                self.state = 422
                self.spotSpec()


            self.state = 426
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==88 or _la==91:
                self.state = 425
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
            self.state = 428
            self.match(PlantUMLDeploymentParser.LPAREN)
            self.state = 429
            self.spotChar()
            self.state = 430
            self.match(PlantUMLDeploymentParser.COMMA)
            self.state = 431
            self.colorSpec()
            self.state = 432
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
            self.state = 434
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
            self.state = 436
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
            self.state = 439
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,57,self._ctx)
            if la_ == 1:
                self.state = 438
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
            self.state = 471 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 471
                    self._errHandler.sync(self)
                    token = self._input.LA(1)
                    if token in [88]:
                        self.state = 441
                        self.match(PlantUMLDeploymentParser.ID)
                        pass
                    elif token in [73]:
                        self.state = 442
                        self.match(PlantUMLDeploymentParser.QUOTED_STRING)
                        pass
                    elif token in [87]:
                        self.state = 443
                        self.match(PlantUMLDeploymentParser.INT)
                        pass
                    elif token in [71]:
                        self.state = 444
                        self.match(PlantUMLDeploymentParser.COLOR)
                        pass
                    elif token in [8]:
                        self.state = 445
                        self.match(PlantUMLDeploymentParser.TAG)
                        pass
                    elif token in [91]:
                        self.state = 446
                        self.match(PlantUMLDeploymentParser.FREE_TEXT)
                        pass
                    elif token in [81]:
                        self.state = 447
                        self.match(PlantUMLDeploymentParser.COLON)
                        pass
                    elif token in [82]:
                        self.state = 448
                        self.match(PlantUMLDeploymentParser.COMMA)
                        pass
                    elif token in [83]:
                        self.state = 449
                        self.match(PlantUMLDeploymentParser.STAR)
                        pass
                    elif token in [84]:
                        self.state = 450
                        self.match(PlantUMLDeploymentParser.BANG)
                        pass
                    elif token in [80]:
                        self.state = 451
                        self.match(PlantUMLDeploymentParser.FSLASH)
                        pass
                    elif token in [74]:
                        self.state = 452
                        self.match(PlantUMLDeploymentParser.LPAREN)
                        pass
                    elif token in [75]:
                        self.state = 453
                        self.match(PlantUMLDeploymentParser.RPAREN)
                        pass
                    elif token in [76]:
                        self.state = 454
                        self.match(PlantUMLDeploymentParser.LBRACK)
                        pass
                    elif token in [77]:
                        self.state = 455
                        self.match(PlantUMLDeploymentParser.RBRACK)
                        pass
                    elif token in [85]:
                        self.state = 456
                        self.match(PlantUMLDeploymentParser.AT)
                        pass
                    elif token in [86]:
                        self.state = 457
                        self.match(PlantUMLDeploymentParser.DOLLAR)
                        pass
                    elif token in [68]:
                        self.state = 458
                        self.match(PlantUMLDeploymentParser.STEREOTYPE_OPEN)
                        pass
                    elif token in [69]:
                        self.state = 459
                        self.match(PlantUMLDeploymentParser.STEREOTYPE_CLOSE)
                        pass
                    elif token in [40]:
                        self.state = 460
                        self.match(PlantUMLDeploymentParser.KW_AS)
                        pass
                    elif token in [50]:
                        self.state = 461
                        self.match(PlantUMLDeploymentParser.KW_OF)
                        pass
                    elif token in [54]:
                        self.state = 462
                        self.match(PlantUMLDeploymentParser.KW_TO)
                        pass
                    elif token in [46]:
                        self.state = 463
                        self.match(PlantUMLDeploymentParser.KW_LEFT)
                        pass
                    elif token in [47]:
                        self.state = 464
                        self.match(PlantUMLDeploymentParser.KW_RIGHT)
                        pass
                    elif token in [48]:
                        self.state = 465
                        self.match(PlantUMLDeploymentParser.KW_TOP)
                        pass
                    elif token in [49]:
                        self.state = 466
                        self.match(PlantUMLDeploymentParser.KW_BOTTOM)
                        pass
                    elif token in [62]:
                        self.state = 467
                        self.match(PlantUMLDeploymentParser.KW_CENTER)
                        pass
                    elif token in [67]:
                        self.state = 468
                        self.match(PlantUMLDeploymentParser.KW_X)
                        pass
                    elif token in [55]:
                        self.state = 469
                        self.match(PlantUMLDeploymentParser.KW_DIRECTION)
                        pass
                    elif token in [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]:
                        self.state = 470
                        self.elementKeyword()
                        pass
                    else:
                        raise NoViableAltException(self)


                else:
                    raise NoViableAltException(self)
                self.state = 473 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,59,self._ctx)

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
            self.state = 475
            self.relationRef()
            self.state = 476
            self.match(PlantUMLDeploymentParser.ARROW_SPEC)
            self.state = 477
            self.relationRef()
            self.state = 480
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==81:
                self.state = 478
                self.match(PlantUMLDeploymentParser.COLON)
                self.state = 479
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
            self.state = 482
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
            self.state = 484
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
            self.state = 498
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,62,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 486
                self.match(PlantUMLDeploymentParser.KW_NOTE)
                self.state = 487
                self.noteSide()
                self.state = 488
                self.match(PlantUMLDeploymentParser.KW_OF)
                self.state = 489
                self.relationRef()
                self.state = 492
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==81:
                    self.state = 490
                    self.match(PlantUMLDeploymentParser.COLON)
                    self.state = 491
                    self.restOfLine()


                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 494
                self.match(PlantUMLDeploymentParser.KW_NOTE)
                self.state = 495
                self.match(PlantUMLDeploymentParser.QUOTED_STRING)
                self.state = 496
                self.match(PlantUMLDeploymentParser.KW_AS)
                self.state = 497
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
            self.state = 539
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,69,self._ctx)
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
                self.state = 505 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 504
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 507 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,63,self._ctx)

                self.state = 510 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 509
                    self.noteBodyLine()
                    self.state = 512 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 4667911881975921920) != 0) or ((((_la - 67)) & ~0x3f) == 0 and ((1 << (_la - 67)) & 54519767) != 0)):
                        break

                self.state = 514
                self.match(PlantUMLDeploymentParser.KW_END_NOTE)
                self.state = 516 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 515
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 518 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,65,self._ctx)

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 520
                self.match(PlantUMLDeploymentParser.KW_NOTE)
                self.state = 521
                self.match(PlantUMLDeploymentParser.KW_AS)
                self.state = 522
                self.elementName()
                self.state = 524 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 523
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 526 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,66,self._ctx)

                self.state = 529 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 528
                    self.noteBodyLine()
                    self.state = 531 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 4667911881975921920) != 0) or ((((_la - 67)) & ~0x3f) == 0 and ((1 << (_la - 67)) & 54519767) != 0)):
                        break

                self.state = 533
                self.match(PlantUMLDeploymentParser.KW_END_NOTE)
                self.state = 535 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 534
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 537 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,68,self._ctx)

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
            self.state = 541
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
            self.state = 554
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 40, 46, 47, 48, 49, 50, 54, 55, 62, 67, 68, 69, 71, 73, 74, 75, 76, 77, 80, 81, 82, 83, 84, 85, 86, 87, 88, 91]:
                self.enterOuterAlt(localctx, 1)
                self.state = 543
                self.restOfLine()
                self.state = 545 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 544
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 547 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,70,self._ctx)

                pass
            elif token in [92]:
                self.enterOuterAlt(localctx, 2)
                self.state = 550 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 549
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 552 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,71,self._ctx)

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
            self.state = 556
            self.match(PlantUMLDeploymentParser.KW_SPRITE)
            self.state = 557
            self.match(PlantUMLDeploymentParser.TAG)
            self.state = 559
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==76:
                self.state = 558
                self.spriteDimension()


            self.state = 561
            self.match(PlantUMLDeploymentParser.LBRACE)
            self.state = 563 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 562
                    self.match(PlantUMLDeploymentParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 565 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,74,self._ctx)

            self.state = 568 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 567
                self.spriteRow()
                self.state = 570 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==72 or _la==92):
                    break

            self.state = 572
            self.match(PlantUMLDeploymentParser.RBRACE)
            self.state = 574 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 573
                    self.match(PlantUMLDeploymentParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 576 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,76,self._ctx)

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
            self.state = 578
            self.match(PlantUMLDeploymentParser.LBRACK)
            self.state = 579
            self.match(PlantUMLDeploymentParser.INT)
            self.state = 580
            self.match(PlantUMLDeploymentParser.KW_X)
            self.state = 581
            self.match(PlantUMLDeploymentParser.INT)
            self.state = 584
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==80:
                self.state = 582
                self.match(PlantUMLDeploymentParser.FSLASH)
                self.state = 583
                self.match(PlantUMLDeploymentParser.INT)


            self.state = 586
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
            self.state = 599
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [72]:
                self.enterOuterAlt(localctx, 1)
                self.state = 588
                self.match(PlantUMLDeploymentParser.SPRITE_ROW)
                self.state = 590 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 589
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 592 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,78,self._ctx)

                pass
            elif token in [92]:
                self.enterOuterAlt(localctx, 2)
                self.state = 595 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 594
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 597 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,79,self._ctx)

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
            self.state = 601
            self.match(PlantUMLDeploymentParser.KW_SKINPARAM)
            self.state = 602
            self.skinparamPath()
            self.state = 604
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 4667911881975921920) != 0) or ((((_la - 67)) & ~0x3f) == 0 and ((1 << (_la - 67)) & 20965335) != 0):
                self.state = 603
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
            self.state = 606
            self.match(PlantUMLDeploymentParser.KW_SKINPARAM)
            self.state = 607
            self.skinparamPath()
            self.state = 608
            self.match(PlantUMLDeploymentParser.LBRACE)
            self.state = 610 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 609
                    self.match(PlantUMLDeploymentParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 612 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,82,self._ctx)

            self.state = 617
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==88 or _la==92:
                self.state = 614
                self.skinparamEntry()
                self.state = 619
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 620
            self.match(PlantUMLDeploymentParser.RBRACE)
            self.state = 622 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 621
                    self.match(PlantUMLDeploymentParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 624 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,84,self._ctx)

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

        def ID(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLDeploymentParser.ID)
            else:
                return self.getToken(PlantUMLDeploymentParser.ID, i)

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
            self.state = 626
            self.match(PlantUMLDeploymentParser.ID)
            self.state = 631
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==1:
                self.state = 627
                self.match(PlantUMLDeploymentParser.T__0)
                self.state = 628
                self.match(PlantUMLDeploymentParser.ID)
                self.state = 633
                self._errHandler.sync(self)
                _la = self._input.LA(1)

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

        def ID(self):
            return self.getToken(PlantUMLDeploymentParser.ID, 0)

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
        self.enterRule(localctx, 68, self.RULE_skinparamEntry)
        try:
            self.state = 646
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [88]:
                self.enterOuterAlt(localctx, 1)
                self.state = 634
                self.match(PlantUMLDeploymentParser.ID)
                self.state = 635
                self.restOfLine()
                self.state = 637 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 636
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 639 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,86,self._ctx)

                pass
            elif token in [92]:
                self.enterOuterAlt(localctx, 2)
                self.state = 642 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 641
                        self.match(PlantUMLDeploymentParser.NEWLINE)

                    else:
                        raise NoViableAltException(self)
                    self.state = 644 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,87,self._ctx)

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
        self.enterRule(localctx, 70, self.RULE_visibilityStmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 648
            self.visibilityKeyword()
            self.state = 649
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
        self.enterRule(localctx, 72, self.RULE_visibilityKeyword)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 651
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
        self.enterRule(localctx, 74, self.RULE_visibilityTarget)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 653
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
        self.enterRule(localctx, 76, self.RULE_directionStmt)
        try:
            self.state = 663
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [46]:
                self.enterOuterAlt(localctx, 1)
                self.state = 655
                self.match(PlantUMLDeploymentParser.KW_LEFT)
                self.state = 656
                self.match(PlantUMLDeploymentParser.KW_TO)
                self.state = 657
                self.match(PlantUMLDeploymentParser.KW_RIGHT)
                self.state = 658
                self.match(PlantUMLDeploymentParser.KW_DIRECTION)
                pass
            elif token in [48]:
                self.enterOuterAlt(localctx, 2)
                self.state = 659
                self.match(PlantUMLDeploymentParser.KW_TOP)
                self.state = 660
                self.match(PlantUMLDeploymentParser.KW_TO)
                self.state = 661
                self.match(PlantUMLDeploymentParser.KW_BOTTOM)
                self.state = 662
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
        self.enterRule(localctx, 78, self.RULE_allowMixingStmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 665
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
        self.enterRule(localctx, 80, self.RULE_titleStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 667
            self.match(PlantUMLDeploymentParser.KW_TITLE)
            self.state = 669
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 4667911881975921920) != 0) or ((((_la - 67)) & ~0x3f) == 0 and ((1 << (_la - 67)) & 20965335) != 0):
                self.state = 668
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
        self.enterRule(localctx, 82, self.RULE_headerStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 671
            self.match(PlantUMLDeploymentParser.KW_HEADER)
            self.state = 673
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 4667911881975921920) != 0) or ((((_la - 67)) & ~0x3f) == 0 and ((1 << (_la - 67)) & 20965335) != 0):
                self.state = 672
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
        self.enterRule(localctx, 84, self.RULE_footerStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 675
            self.match(PlantUMLDeploymentParser.KW_FOOTER)
            self.state = 677
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 4667911881975921920) != 0) or ((((_la - 67)) & ~0x3f) == 0 and ((1 << (_la - 67)) & 20965335) != 0):
                self.state = 676
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
        self.enterRule(localctx, 86, self.RULE_captionStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 679
            self.match(PlantUMLDeploymentParser.KW_CAPTION)
            self.state = 681
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 4667911881975921920) != 0) or ((((_la - 67)) & ~0x3f) == 0 and ((1 << (_la - 67)) & 20965335) != 0):
                self.state = 680
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
        self.enterRule(localctx, 88, self.RULE_legendBlock)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 683
            self.match(PlantUMLDeploymentParser.KW_LEGEND)
            self.state = 685
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 4611897124659920896) != 0):
                self.state = 684
                self.legendAlign()


            self.state = 688 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 687
                    self.match(PlantUMLDeploymentParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 690 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,95,self._ctx)

            self.state = 693 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 692
                self.noteBodyLine()
                self.state = 695 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 4667911881975921920) != 0) or ((((_la - 67)) & ~0x3f) == 0 and ((1 << (_la - 67)) & 54519767) != 0)):
                    break

            self.state = 697
            self.match(PlantUMLDeploymentParser.KW_END_LEGEND)
            self.state = 699 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 698
                    self.match(PlantUMLDeploymentParser.NEWLINE)

                else:
                    raise NoViableAltException(self)
                self.state = 701 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,97,self._ctx)

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
        self.enterRule(localctx, 90, self.RULE_legendAlign)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 703
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
        self.enterRule(localctx, 92, self.RULE_pragmaStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 705
            self.match(PlantUMLDeploymentParser.BANG)
            self.state = 706
            self.match(PlantUMLDeploymentParser.KW_PRAGMA)
            self.state = 707
            self.match(PlantUMLDeploymentParser.ID)
            self.state = 709
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 4667911881975921920) != 0) or ((((_la - 67)) & ~0x3f) == 0 and ((1 << (_la - 67)) & 20965335) != 0):
                self.state = 708
                self.restOfLine()


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
        self.enterRule(localctx, 94, self.RULE_scaleStmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 711
            self.match(PlantUMLDeploymentParser.KW_SCALE)
            self.state = 712
            self.restOfLine()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





