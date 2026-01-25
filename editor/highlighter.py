"""
editor/highlighter.py

JSON syntax highlighter for the code editor.
"""

from __future__ import annotations

from typing import List, Tuple

from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor


class JsonHighlighter(QSyntaxHighlighter):
    """
    Syntax highlighter for JSON content.

    Highlights:
    - Keys (blue, bold)
    - String values (green)
    - Numbers (purple)
    - Keywords: true, false, null (orange, bold)
    - Braces and brackets (gray, bold)
    """

    def __init__(self, parent):
        super().__init__(parent)

        self.rules: List[Tuple[QRegularExpression, QTextCharFormat]] = []

        def fmt(color_hex: str, bold: bool = False) -> QTextCharFormat:
            f = QTextCharFormat()
            f.setForeground(QColor(color_hex))
            if bold:
                f.setFontWeight(700)
            return f

        # JSON keys (before colon)
        key_fmt = fmt("#2E86C1", bold=True)
        self.rules.append((QRegularExpression(r'"[^"\\]*(?:\\.[^"\\]*)*"\s*(?=:)'), key_fmt))

        # String values (not keys)
        str_fmt = fmt("#27AE60")
        self.rules.append((QRegularExpression(r'(?<!:)\s*"[^"\\]*(?:\\.[^"\\]*)*"'), str_fmt))

        # Numbers
        num_fmt = fmt("#8E44AD")
        self.rules.append((QRegularExpression(r"\b-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?\b"), num_fmt))

        # Keywords: true, false, null
        kw_fmt = fmt("#D35400", bold=True)
        self.rules.append((QRegularExpression(r"\b(true|false|null)\b"), kw_fmt))

        # Braces and brackets
        brace_fmt = fmt("#566573", bold=True)
        self.rules.append((QRegularExpression(r"[\{\}\[\]]"), brace_fmt))

    def highlightBlock(self, text: str) -> None:
        """Apply highlighting rules to a block of text."""
        for regex, f in self.rules:
            it = regex.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), f)
