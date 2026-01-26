"""
editor/draft_dock.py

Draft JSON dock widget with enhanced code editor for diagram annotation.
"""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import (
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from editor.highlighter import JsonHighlighter
from editor.code_editor import JsonCodeEditor


class DraftDock(QDockWidget):
    """
    Draft JSON dock widget with enhanced code editor featuring:
    - Line numbers
    - Code folding for JSON objects/arrays
    - Bidirectional sync: canvas selection -> editor scroll, editor cursor -> canvas selection
    """

    # Signal emitted when cursor moves to a different annotation in the editor
    cursor_annotation_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__("Draft JSON (AI)", parent)
        w = QWidget()
        self.setWidget(w)
        layout = QVBoxLayout(w)

        # Use the enhanced JsonCodeEditor with line numbers and folding
        self.text = JsonCodeEditor()
        self.text.setPlaceholderText("AI draft JSON will appear here... (editable)")
        layout.addWidget(self.text)

        # Syntax highlighting
        self._highlighter = JsonHighlighter(self.text.document())

        # Forward the cursor annotation changed signal
        self.text.cursor_annotation_changed.connect(self.cursor_annotation_changed.emit)

        # Toolbar for focus mode
        fold_bar = QHBoxLayout()
        self.focus_mode_btn = QPushButton("Focus")
        self.focus_mode_btn.setCheckable(True)
        self.focus_mode_btn.setToolTip(
            "When enabled, only the selected annotation is expanded.\n"
            "Other annotations are collapsed for easier reading."
        )
        self.focus_mode_btn.toggled.connect(self._on_focus_mode_toggled)
        fold_bar.addWidget(self.focus_mode_btn)
        fold_bar.addStretch()
        layout.addLayout(fold_bar)

        # Focus mode state
        self._focus_mode_enabled = False
        self._focused_annotation_id = ""

        self.import_btn = QPushButton("Import && Link")
        self.import_btn.setEnabled(False)
        layout.addWidget(self.import_btn)

        self.status = QLabel("")
        layout.addWidget(self.status)

    def set_json_text(self, s: str, enable_import: bool, status: str = ""):
        """Set the JSON text content."""
        self.text.setPlainText(s)
        self.import_btn.setEnabled(enable_import)
        self.status.setText(status)

    def set_status(self, status: str):
        """Update the status label."""
        self.status.setText(status)

    def get_json_text(self) -> str:
        """Get the current JSON text content."""
        return self.text.toPlainText()

    def scroll_to_id_top(self, ann_id: str, suppress_signal: bool = True) -> bool:
        """
        Scroll the editor to show the annotation's opening bracket at the top.
        If suppress_signal is True, prevents emitting cursor_annotation_changed.
        """
        if not ann_id:
            return False

        # Suppress cursor signal to prevent circular updates when canvas selection drives scroll
        if suppress_signal:
            self.text._suppress_cursor_signal = True

        try:
            full = self.text.toPlainText()

            # Find the "id" field for this annotation
            id_needle = f'"id": "{ann_id}"'
            id_pos = full.find(id_needle)
            if id_pos < 0:
                # Try with different spacing
                id_needle = f'"id":"{ann_id}"'
                id_pos = full.find(id_needle)
            if id_pos < 0:
                return False

            # Scan backwards from id_pos to find the opening brace of this object
            brace_depth = 0
            object_start = -1
            in_string = False

            for i in range(id_pos - 1, -1, -1):
                ch = full[i]

                # Handle string detection (scanning backwards)
                if ch == '"' and (i == 0 or full[i-1] != '\\'):
                    in_string = not in_string
                    continue

                if in_string:
                    continue

                if ch == '}':
                    brace_depth += 1
                elif ch == '{':
                    if brace_depth == 0:
                        object_start = i
                        break
                    brace_depth -= 1

            if object_start < 0:
                return False

            # Position cursor at the opening bracket
            doc = self.text.document()
            cursor = QTextCursor(doc)
            cursor.setPosition(object_start)
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)

            self.text.setTextCursor(cursor)

            # Update the tracked annotation ID
            self.text._current_annotation_id = ann_id

            # Scroll so the opening bracket line is at the top of the viewport
            # First ensure it's visible, then adjust to put it at top
            self.text.ensureCursorVisible()
            rect = self.text.cursorRect(cursor)
            sb = self.text.verticalScrollBar()
            sb.setValue(sb.value() + rect.top())
            return True
        finally:
            if suppress_signal:
                self.text._suppress_cursor_signal = False

    def jump_to_text_field_for_id(self, ann_id: str, suppress_signal: bool = True) -> bool:
        """
        Jump to the "text" field of the annotation with the given ID.
        If suppress_signal is True, prevents emitting cursor_annotation_changed.
        """
        if not ann_id:
            return False

        # Suppress cursor signal to prevent circular updates
        if suppress_signal:
            self.text._suppress_cursor_signal = True

        try:
            full = self.text.toPlainText()
            id_needle = f"\"id\": \"{ann_id}\""
            id_pos = full.find(id_needle)
            if id_pos < 0:
                return False

            text_key = "\"text\":"
            text_pos = full.find(text_key, id_pos)
            if text_pos < 0:
                return self.scroll_to_id_top(ann_id, suppress_signal=False)

            value_start = text_pos + len(text_key)

            doc = self.text.document()
            cursor = QTextCursor(doc)
            cursor.setPosition(value_start)
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)

            self.text.setTextCursor(cursor)
            self.text.ensureCursorVisible()

            # Update the tracked annotation ID
            self.text._current_annotation_id = ann_id

            rect = self.text.cursorRect(cursor)
            sb = self.text.verticalScrollBar()
            sb.setValue(sb.value() + rect.top())
            return True
        finally:
            if suppress_signal:
                self.text._suppress_cursor_signal = False

    def set_highlighted_annotation(self, ann_id: str):
        """Set the annotation to highlight in the line number gutter."""
        self.text.set_highlighted_annotation(ann_id)

    def clear_highlighted_annotation(self):
        """Clear the highlighted annotation."""
        self.text.clear_highlighted_annotation()

    def _on_focus_mode_toggled(self, enabled: bool):
        """Handle focus mode toggle."""
        self._focus_mode_enabled = enabled
        if enabled:
            # Apply focus mode with current focused annotation
            self.text.focus_on_annotation(self._focused_annotation_id)
        else:
            # Disable focus mode - unfold all
            self.text.unfold_all()

    def is_focus_mode_enabled(self) -> bool:
        """Check if focus mode is enabled."""
        return self._focus_mode_enabled

    def set_focused_annotation(self, ann_id: str):
        """
        Set the annotation to focus on (expand) when in focus mode.
        If focus mode is enabled, this will fold all others and expand this one.
        """
        self._focused_annotation_id = ann_id
        if self._focus_mode_enabled:
            self.text.focus_on_annotation(ann_id)
