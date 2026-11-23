"""
editor/highlighter.py

JSON syntax highlighter for the code editor.
"""

from __future__ import annotations

from typing import List, Tuple

from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor

from settings import get_settings


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

        # Get syntax colors from settings
        # Defaults: key=#2E86C1, string=#27AE60, number=#8E44AD, keyword=#D35400, brace=#566573
        syntax = get_settings().settings.editor.syntax

        def fmt(color_hex: str, bold: bool = False) -> QTextCharFormat:
            f = QTextCharFormat()
            f.setForeground(QColor(color_hex))
            if bold:
                f.setFontWeight(700)
            return f

        # JSON keys (before colon) - Default: #2E86C1 (blue), bold
        key_fmt = fmt(syntax.key_color, bold=syntax.key_bold)
        self.rules.append((QRegularExpression(r'"[^"\\]*(?:\\.[^"\\]*)*"\s*(?=:)'), key_fmt))

        # Read-only fields — light gray italic for key + all values
        ro_fmt = QTextCharFormat()
        ro_fmt.setForeground(QColor("#777777"))
        ro_fmt.setFontItalic(True)
        self._readonly_fmt = ro_fmt
        # Set of JSON key names that are computed / read-only
        self._readonly_keys = frozenset({"ports", "label", "tech", "note"})

        # String values (not keys) - Default: #27AE60 (green)
        str_fmt = fmt(syntax.string_color)
        self.rules.append((QRegularExpression(r'(?<!:)\s*"[^"\\]*(?:\\.[^"\\]*)*"'), str_fmt))

        # Numbers - Default: #8E44AD (purple)
        num_fmt = fmt(syntax.number_color)
        self.rules.append((QRegularExpression(r"\b-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?\b"), num_fmt))

        # Keywords: true, false, null - Default: #D35400 (orange), bold
        kw_fmt = fmt(syntax.keyword_color, bold=syntax.keyword_bold)
        self.rules.append((QRegularExpression(r"\b(true|false|null)\b"), kw_fmt))

        # Braces and brackets - Default: #566573 (gray), bold
        brace_fmt = fmt(syntax.brace_color, bold=syntax.brace_bold)
        self.rules.append((QRegularExpression(r"[\{\}\[\]]"), brace_fmt))

    # Block states for read-only field tracking across lines.
    # Positive values encode the remaining bracket depth inside a
    # read-only field's value (1 = one unclosed '[').
    _STATE_NORMAL = -1

    def highlightBlock(self, text: str) -> None:
        """Apply highlighting rules to a block of text."""
        for regex, f in self.rules:
            it = regex.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), f)

        # ── Read-only field detection (key line + multi-line values) ──
        prev_state = self.previousBlockState()
        is_readonly = False
        depth = prev_state if prev_state > 0 else 0

        # Check if this line starts a new read-only field
        stripped = text.lstrip()
        if stripped.startswith('"'):
            colon = stripped.find('":')
            if colon > 0 and stripped[1:colon] in self._readonly_keys:
                is_readonly = True
                depth = 0  # will be counted below

        # If previous line was inside a read-only value, we continue
        if not is_readonly and prev_state > 0:
            is_readonly = True

        if is_readonly:
            self.setFormat(0, len(text), self._readonly_fmt)
            # Count brackets on this line to track depth
            for ch in text:
                if ch == '[':
                    depth += 1
                elif ch == ']':
                    depth -= 1
            # Positive depth means brackets still open → next line is read-only
            self.setCurrentBlockState(depth if depth > 0 else self._STATE_NORMAL)
        else:
            self.setCurrentBlockState(self._STATE_NORMAL)
