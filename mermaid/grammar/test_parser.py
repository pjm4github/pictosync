# test_parse.py — put this in your project root
import sys

from antlr4 import CommonTokenStream, InputStream
from generated.MermaidSequenceLexer import MermaidSequenceLexer
from generated.MermaidSequenceParser import MermaidSequenceParser

from dispatcher import parse_mermaid_source, REGISTRY
from detector import detect_mermaid_source_type

source = """
sequenceDiagram
    participant web as Web Browser
    participant db as Storage
    web->>+db: Query
    db-->>-web: Result
"""
filename = 'C:/Users/pmora/OneDrive/Documents/Git/GitHub/pictosync/test_data/MERMAID/sequence.mermaid'
print(filename)
with open(filename, 'r') as f:
    src = f.read()

tree = parse_mermaid_source(src)

stream = InputStream(src)   # source must be a str, not bytes — this works fine
#stream = InputStream(source)
lexer  = MermaidSequenceLexer(stream)
tokens = CommonTokenStream(lexer)
parser = MermaidSequenceParser(tokens)
#tree   = parser.diagram()

print(tree.toStringTree(recog=parser))