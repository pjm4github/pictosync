"""
editor/draft_dock.py

Draft JSON dock widget with enhanced code editor for diagram annotation.
"""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal, QTimer
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

        # Scroll lock: when set, scroll position is pinned to this value
        self._locked_scroll: int | None = None
        self._lock_after_scroll = False

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

    def replace_json_text_keep_scroll(self, s: str, status: str = ""):
        """Replace text content while preserving the scroll position.

        Uses QTextCursor to swap content as an edit operation rather than
        setPlainText() which resets the cursor, scroll, and fold state.
        If scroll is locked, restores to the locked value.
        """
        sb = self.text.verticalScrollBar()
        target = self._locked_scroll if self._locked_scroll is not None else sb.value()

        self.text._suppress_cursor_signal = True
        cursor = QTextCursor(self.text.document())
        cursor.beginEditBlock()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.insertText(s)
        cursor.endEditBlock()

        sb.setValue(target)
        QTimer.singleShot(0, lambda: sb.setValue(target))
        self.text._suppress_cursor_signal = False
        self.status.setText(status)

    def lock_scroll(self):
        """Lock the scroll position at its current value (first call only)."""
        if self._locked_scroll is None:
            self._locked_scroll = self.text.verticalScrollBar().value()

    def unlock_scroll(self):
        """Unlock the scroll position."""
        self._locked_scroll = None
        self._lock_after_scroll = False

    def set_status(self, status: str):
        """Update the status label."""
        self.status.setText(status)

    def get_json_text(self) -> str:
        """Get the current JSON text content."""
        return self.text.toPlainText()

    def _scroll_cursor_to_top(self):
        """Scroll the editor so the current cursor position is at the viewport top.

        setTextCursor() internally queues a deferred ensureCursorVisible() via
        Qt's event loop, so this method must be called via QTimer.singleShot(0)
        to run after that deferred scroll completes.

        Strategy: scroll to the document bottom so the cursor is above the
        viewport, call ensureCursorVisible() which scrolls up to reveal it
        near the top, then fine-tune the scrollbar using the cursor's actual
        pixel position so it sits exactly at the viewport top.
        """
        # Suppress cursor signals during scroll — scrolling to the bottom
        # temporarily moves a different annotation into view, which would
        # otherwise trigger a feedback loop via cursor_annotation_changed.
        self.text._suppress_cursor_signal = True
        try:
            sb = self.text.verticalScrollBar()
            sb.setValue(sb.maximum())
            self.text.ensureCursorVisible()

            cursor_rect = self.text.cursorRect()
            if cursor_rect.top() > 1:
                line_height = self.text.blockBoundingRect(
                    self.text.firstVisibleBlock()).height()
                if line_height > 0:
                    sb.setValue(sb.value() + int(cursor_rect.top() / line_height))
            # Lock scroll after the deferred scroll completes so that
            # subsequent drag frames keep the annotation pinned in place.
            # Force-capture: overwrite any stale value from an early drag frame.
            if self._lock_after_scroll:
                self._lock_after_scroll = False
                self._locked_scroll = sb.value()
        finally:
            self.text._suppress_cursor_signal = False

    def scroll_to_id_top(self, ann_id: str, suppress_signal: bool = True) -> bool:
        """
        Scroll the editor to show the annotation at the top of the viewport.
        Finds the opening brace of the annotation object and scrolls it to the top.
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

            # Scan backward from the "id" field to find the opening brace
            # of this annotation object, so we scroll the whole object into view
            target_pos = id_pos
            brace_depth = 0
            in_string = False
            for i in range(id_pos - 1, -1, -1):
                ch = full[i]
                if ch == '"' and (i == 0 or full[i - 1] != '\\'):
                    in_string = not in_string
                    continue
                if in_string:
                    continue
                if ch == '}':
                    brace_depth += 1
                elif ch == '{':
                    if brace_depth == 0:
                        target_pos = i
                        break
                    brace_depth -= 1

            # Position cursor at the target line
            doc = self.text.document()
            cursor = QTextCursor(doc)
            cursor.setPosition(target_pos)
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)

            self.text.setTextCursor(cursor)

            # Update the tracked annotation ID
            self.text._current_annotation_id = ann_id

            # Deferred: setTextCursor() queues an internal ensureCursorVisible()
            # via Qt's event loop; our scroll must run after that completes.
            QTimer.singleShot(0, self._scroll_cursor_to_top)
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

            # Update the tracked annotation ID
            self.text._current_annotation_id = ann_id

            # Deferred: setTextCursor() queues an internal ensureCursorVisible()
            # via Qt's event loop; our scroll must run after that completes.
            QTimer.singleShot(0, self._scroll_cursor_to_top)
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
