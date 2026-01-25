"""
editor package

JSON code editor with syntax highlighting, line numbers, code folding,
and annotation tracking for bidirectional sync with the canvas.
"""

from editor.highlighter import JsonHighlighter
from editor.code_editor import LineNumberArea, FoldingArea, JsonCodeEditor
from editor.draft_dock import DraftDock

__all__ = [
    "JsonHighlighter",
    "LineNumberArea",
    "FoldingArea",
    "JsonCodeEditor",
    "DraftDock",
]
