# test_parse.py — put this in your project root
import sys

from antlr4 import CommonTokenStream, InputStream
from MermaidSequenceLexer import MermaidSequenceLexer
from MermaidSequenceParser import MermaidSequenceParser

from ..dispatcher import parse_mermaid_source, REGISTRY
from ..detector import detect_mermaid_source_type

source = """
sequenceDiagram
    participant web as Web Browser
    participant db as Storage
    web->>+db: Query
    db-->>-web: Result
"""

with open('../../../test_data/MERMAID/sequence.mermaid', 'r') as f:
    src = f.read()

tree = parse_mermaid_source(src)

stream = InputStream(source)   # source must be a str, not bytes — this works fine
#stream = InputStream(source)
lexer  = MermaidSequenceLexer(stream)
tokens = CommonTokenStream(lexer)
parser = MermaidSequenceParser(tokens)
tree   = parser.diagram()

print(tree.toStringTree(recog=parser))