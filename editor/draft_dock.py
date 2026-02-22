"""
editor/draft_dock.py

Draft JSON dock widget with enhanced code editor for diagram annotation.
"""

from __future__ import annotations

import json
import logging
from typing import Optional

from PyQt6.QtCore import pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QTextCharFormat, QTextCursor
from PyQt6.QtWidgets import (
    QCheckBox,
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from editor.highlighter import JsonHighlighter
from editor.code_editor import JsonCodeEditor
from editor.schema_checker import FieldDiff, build_merged_annotation, find_key_ranges_in_json

log = logging.getLogger(__name__)


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

        self.schema_check_btn = QCheckBox("Schema")
        self.schema_check_btn.setToolTip(
            "Compare focused annotation against schema.\n"
            "Missing fields shown in gray, extra fields in red."
        )
        self.schema_check_btn.toggled.connect(self._on_schema_check_toggled)
        fold_bar.addWidget(self.schema_check_btn)

        fold_bar.addStretch()
        layout.addLayout(fold_bar)

        # Focus mode state
        self._focus_mode_enabled = False
        self._focused_annotation_id = ""

        # Schema check state
        self._schema_check_enabled = False
        self._schema_check_inserting = False
        self._schema_original_ann_text: str = ""
        self._schema_original_start: int = -1
        self._schema_original_end: int = -1
        self._schema_diff: Optional[FieldDiff] = None
        self._missing_field_ranges: list[tuple[int, int, str]] = []

        # Wire up ghost-field checker and accept signal
        self.text._ghost_field_checker = self.get_ghost_field_at_pos
        self.text.accept_ghost_field.connect(self._on_accept_ghost_field)

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

    def jump_to_note_field_for_id(self, ann_id: str, suppress_signal: bool = True) -> bool:
        """
        Jump to the "note" field inside "meta" for the annotation with the given ID.
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

            # Find "meta" after the id, then "note" inside meta
            meta_key = "\"meta\":"
            meta_pos = full.find(meta_key, id_pos)
            if meta_pos < 0:
                return self.scroll_to_id_top(ann_id, suppress_signal=False)

            note_key = "\"note\":"
            note_pos = full.find(note_key, meta_pos)
            if note_pos < 0:
                return self.scroll_to_id_top(ann_id, suppress_signal=False)

            value_start = note_pos + len(note_key)

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
        """Set the annotation to focus on (expand) when in focus mode.

        If schema check is active and the annotation is changing, the old
        annotation is restored first, then the check is re-applied to the
        new one (deferred so focus-mode layout completes first).
        """
        old_id = self._focused_annotation_id

        # If schema check active and annotation changing, restore old first
        if self._schema_check_enabled and old_id and old_id != ann_id:
            self.remove_schema_check()

        self._focused_annotation_id = ann_id
        if self._focus_mode_enabled:
            self.text.focus_on_annotation(ann_id)

        # Apply schema check to new annotation (deferred for focus mode layout)
        if self._schema_check_enabled and ann_id:
            QTimer.singleShot(0, self.apply_schema_check)

    # -----------------------------------------------------------------
    # Schema check
    # -----------------------------------------------------------------

    def _on_schema_check_toggled(self, enabled: bool):
        """Handle Schema checkbox toggle."""
        self._schema_check_enabled = enabled
        if enabled:
            self.apply_schema_check()
        else:
            self.remove_schema_check()

    def is_schema_check_enabled(self) -> bool:
        """Return whether the schema check overlay is active."""
        return self._schema_check_enabled

    def apply_schema_check(self):
        """Compute field diff for the focused annotation and apply overlays.

        1. Locate the annotation in the editor text.
        2. Build merged annotation (actual + missing defaults).
        3. Replace the annotation block in the editor with the merged text.
        4. Color missing fields gray, extra fields red via extra selections.
        """
        ann_id = self._focused_annotation_id
        if not ann_id:
            self.text.setExtraSelections([])
            return

        start, end = self.text._find_annotation_char_range(ann_id)
        if start < 0:
            self.text.setExtraSelections([])
            return

        full_text = self.text.toPlainText()
        ann_text = full_text[start:end + 1]

        try:
            ann_dict = json.loads(ann_text)
        except json.JSONDecodeError:
            self.text.setExtraSelections([])
            return

        kind = ann_dict.get("kind")
        if not kind:
            self.text.setExtraSelections([])
            return

        # Save original text so we can restore later
        self._schema_original_ann_text = ann_text
        self._schema_original_start = start
        self._schema_original_end = end

        merged, diff = build_merged_annotation(ann_dict, kind)
        self._schema_diff = diff

        if not diff.missing_paths and not diff.extra_paths:
            # Nothing to show — just clear any previous overlays
            self.text.setExtraSelections([])
            return

        # Serialize merged annotation
        merged_text = json.dumps(merged, indent=2)

        # Detect base indentation from the original text
        base_indent = self._detect_indent(full_text, start)

        # Apply base indent to the merged text (skip first line — it's the opening brace)
        if base_indent:
            lines = merged_text.split("\n")
            indented_lines = [lines[0]]
            for line in lines[1:]:
                indented_lines.append(base_indent + line)
            merged_text = "\n".join(indented_lines)

        # Replace the annotation block in the editor
        self._schema_check_inserting = True
        self.text.blockSignals(True)
        try:
            doc = self.text.document()
            cursor = QTextCursor(doc)
            cursor.setPosition(start)
            cursor.setPosition(end + 1, QTextCursor.MoveMode.KeepAnchor)
            cursor.insertText(merged_text)
        finally:
            self.text.blockSignals(False)
            self._schema_check_inserting = False

        # Recompute fold regions since text changed with signals blocked
        self.text._recompute_fold_regions()
        self.text._update_margins()

        # Recompute char range after replacement (text may have shifted)
        new_start, new_end = self.text._find_annotation_char_range(ann_id)
        if new_start < 0:
            return

        # Build extra selections for colored overlays
        full_text = self.text.toPlainText()  # re-read after replacement
        selections: list[QTextEdit.ExtraSelection] = []

        self._missing_field_ranges = []
        if diff.missing_paths:
            fmt_missing = QTextCharFormat()
            fmt_missing.setForeground(QColor("#888888"))
            missing_ranges = find_key_ranges_in_json(
                full_text, new_start, new_end, diff.missing_paths
            )
            # Build per-path range mapping for context-menu detection
            for path in diff.missing_paths:
                path_ranges = find_key_ranges_in_json(
                    full_text, new_start, new_end, {path}
                )
                for rs, re_ in path_ranges:
                    self._missing_field_ranges.append((rs, re_, path))
            for rng_start, rng_end in missing_ranges:
                sel = QTextEdit.ExtraSelection()
                sel.format = fmt_missing  # type: ignore[assignment]
                cur = QTextCursor(self.text.document())
                cur.setPosition(rng_start)
                cur.setPosition(rng_end, QTextCursor.MoveMode.KeepAnchor)
                sel.cursor = cur  # type: ignore[assignment]
                selections.append(sel)

        if diff.extra_paths:
            fmt_extra = QTextCharFormat()
            fmt_extra.setForeground(QColor("#CC4444"))
            extra_ranges = find_key_ranges_in_json(
                full_text, new_start, new_end, diff.extra_paths
            )
            for rng_start, rng_end in extra_ranges:
                sel = QTextEdit.ExtraSelection()
                sel.format = fmt_extra  # type: ignore[assignment]
                cur = QTextCursor(self.text.document())
                cur.setPosition(rng_start)
                cur.setPosition(rng_end, QTextCursor.MoveMode.KeepAnchor)
                sel.cursor = cur  # type: ignore[assignment]
                selections.append(sel)

        self.text.setExtraSelections(selections)

    def remove_schema_check(self):
        """Remove schema overlays and restore original annotation text.

        Ghost fields that still have their default value are removed;
        fields the user has edited are kept.
        """
        self.text.setExtraSelections([])

        if not self._schema_original_ann_text or not self._schema_diff:
            self._clear_schema_state()
            return

        ann_id = self._focused_annotation_id
        if not ann_id:
            self._clear_schema_state()
            return

        # Find current annotation in the (possibly modified) editor text
        start, end = self.text._find_annotation_char_range(ann_id)
        if start < 0:
            self._clear_schema_state()
            return

        full_text = self.text.toPlainText()
        current_text = full_text[start:end + 1]

        try:
            current_dict = json.loads(current_text)
        except json.JSONDecodeError:
            self._clear_schema_state()
            return

        try:
            original_dict = json.loads(self._schema_original_ann_text)
        except json.JSONDecodeError:
            self._clear_schema_state()
            return

        # Smart cleanup: for each missing field that was inserted,
        # remove it if its value still matches the default
        kind = current_dict.get("kind", "")
        cleaned = self._smart_cleanup(current_dict, original_dict, kind)

        # Serialize and replace
        cleaned_text = json.dumps(cleaned, indent=2)
        base_indent = self._detect_indent(full_text, start)
        if base_indent:
            lines = cleaned_text.split("\n")
            indented_lines = [lines[0]]
            for line in lines[1:]:
                indented_lines.append(base_indent + line)
            cleaned_text = "\n".join(indented_lines)

        self._schema_check_inserting = True
        self.text.blockSignals(True)
        try:
            doc = self.text.document()
            cursor = QTextCursor(doc)
            cursor.setPosition(start)
            cursor.setPosition(end + 1, QTextCursor.MoveMode.KeepAnchor)
            cursor.insertText(cleaned_text)
        finally:
            self.text.blockSignals(False)
            self._schema_check_inserting = False

        self.text._recompute_fold_regions()
        self.text._update_margins()
        self._clear_schema_state()

    def refresh_schema_check(self):
        """Re-apply schema check after external text changes.

        Called by main.py after ``_set_draft_text_programmatically`` replaces
        the editor content (which does not contain ghost fields).
        """
        if self._schema_check_enabled and self._focused_annotation_id:
            # Reset saved state (text was replaced externally)
            self._schema_original_ann_text = ""
            self._schema_diff = None
            self.apply_schema_check()

    def update_schema_overlays(self):
        """Refresh schema overlay positions without modifying editor text.

        Re-finds the annotation's character range (which may have shifted
        after an edit/rebuild), re-computes the character ranges for
        missing and extra paths, and re-applies extra selections.
        """
        ann_id = self._focused_annotation_id
        diff = self._schema_diff
        if not ann_id or not diff:
            return
        if not diff.missing_paths and not diff.extra_paths:
            self.text.setExtraSelections([])
            self._missing_field_ranges = []
            return

        start, end = self.text._find_annotation_char_range(ann_id)
        if start < 0:
            return

        full_text = self.text.toPlainText()
        selections: list[QTextEdit.ExtraSelection] = []

        self._missing_field_ranges = []
        if diff.missing_paths:
            fmt_missing = QTextCharFormat()
            fmt_missing.setForeground(QColor("#888888"))
            missing_ranges = find_key_ranges_in_json(
                full_text, start, end, diff.missing_paths
            )
            for path in diff.missing_paths:
                path_ranges = find_key_ranges_in_json(
                    full_text, start, end, {path}
                )
                for rs, re_ in path_ranges:
                    self._missing_field_ranges.append((rs, re_, path))
            for rng_start, rng_end in missing_ranges:
                sel = QTextEdit.ExtraSelection()
                sel.format = fmt_missing  # type: ignore[assignment]
                cur = QTextCursor(self.text.document())
                cur.setPosition(rng_start)
                cur.setPosition(rng_end, QTextCursor.MoveMode.KeepAnchor)
                sel.cursor = cur  # type: ignore[assignment]
                selections.append(sel)

        if diff.extra_paths:
            fmt_extra = QTextCharFormat()
            fmt_extra.setForeground(QColor("#CC4444"))
            extra_ranges = find_key_ranges_in_json(
                full_text, start, end, diff.extra_paths
            )
            for rng_start, rng_end in extra_ranges:
                sel = QTextEdit.ExtraSelection()
                sel.format = fmt_extra  # type: ignore[assignment]
                cur = QTextCursor(self.text.document())
                cur.setPosition(rng_start)
                cur.setPosition(rng_end, QTextCursor.MoveMode.KeepAnchor)
                sel.cursor = cur  # type: ignore[assignment]
                selections.append(sel)

        self.text.setExtraSelections(selections)

    def get_ghost_field_at_pos(self, cursor_pos: int) -> str | None:
        """Return the dot-path of the ghost field at *cursor_pos*, or ``None``."""
        for rng_start, rng_end, path in self._missing_field_ranges:
            if rng_start <= cursor_pos <= rng_end:
                return path
        return None

    def _on_accept_ghost_field(self, path: str):
        """Accept a ghost field so it becomes a real field.

        Removes *path* from the diff's missing set and updates the saved
        original annotation text so ``_smart_cleanup`` treats the field
        as pre-existing (won't remove it on schema-check removal).
        """
        diff = self._schema_diff
        if not diff or path not in diff.missing_paths:
            return

        diff.missing_paths.discard(path)

        # Update _schema_original_ann_text so _smart_cleanup keeps the field
        if self._schema_original_ann_text:
            ann_id = self._focused_annotation_id
            if not ann_id:
                return
            start, end = self.text._find_annotation_char_range(ann_id)
            if start < 0:
                return
            full_text = self.text.toPlainText()
            current_text = full_text[start:end + 1]
            try:
                current_dict = json.loads(current_text)
            except json.JSONDecodeError:
                return
            # Deep-set the accepted field's value into the original dict
            try:
                original_dict = json.loads(self._schema_original_ann_text)
            except json.JSONDecodeError:
                return
            self._deep_set_path(original_dict, path, current_dict)
            self._schema_original_ann_text = json.dumps(original_dict, indent=2)

        self.update_schema_overlays()

    @staticmethod
    def _deep_set_path(target: dict, dot_path: str, source: dict):
        """Copy the value at *dot_path* from *source* into *target*.

        Creates intermediate dicts in *target* as needed.
        """
        parts = dot_path.split(".")
        src = source
        dst = target
        for part in parts[:-1]:
            src = src.get(part, {}) if isinstance(src, dict) else {}
            if part not in dst or not isinstance(dst.get(part), dict):
                dst[part] = {}
            dst = dst[part]
        leaf = parts[-1]
        if isinstance(src, dict) and leaf in src:
            dst[leaf] = src[leaf]

    def _clear_schema_state(self):
        """Reset all internal schema-check bookkeeping."""
        self._schema_original_ann_text = ""
        self._schema_original_start = -1
        self._schema_original_end = -1
        self._schema_diff = None
        self._missing_field_ranges = []

    @staticmethod
    def _detect_indent(text: str, obj_start: int) -> str:
        """Detect the leading whitespace of the line containing *obj_start*."""
        line_start = text.rfind("\n", 0, obj_start)
        if line_start < 0:
            line_start = 0
        else:
            line_start += 1  # skip the newline itself
        indent = ""
        for ch in text[line_start:obj_start]:
            if ch in (" ", "\t"):
                indent += ch
            else:
                break
        return indent

    @staticmethod
    def _smart_cleanup(
        current: dict,
        original: dict,
        kind: str,
    ) -> dict:
        """Remove ghost fields whose values are still default.

        For each key that was absent in *original* (i.e. it was inserted as
        a ghost field), check whether the user modified it.  If the value is
        still the schema default, drop it so the annotation returns to its
        pre-schema-check state.  If the user changed it, keep it.
        """
        from editor.schema_checker import build_expected_from_schema

        defaults = build_expected_from_schema(kind)
        if not defaults:
            return dict(current)
        result: dict = {}

        for key, value in current.items():
            if key in original:
                # Key existed before — always keep it, recursing into dicts
                if isinstance(value, dict) and isinstance(original.get(key), dict):
                    result[key] = DraftDock._smart_cleanup_dict(
                        value, original[key], defaults.get(key, {})
                    )
                else:
                    result[key] = value
            else:
                # Ghost field — keep only if user changed it from default
                default_val = defaults.get(key)
                if isinstance(value, dict) and isinstance(default_val, dict):
                    cleaned = DraftDock._smart_cleanup_dict(value, {}, default_val)
                    if cleaned:
                        result[key] = cleaned
                elif value != default_val:
                    result[key] = value
                # else: still default → drop it

        return result

    @staticmethod
    def _smart_cleanup_dict(
        current: dict,
        original: dict,
        defaults: dict,
    ) -> dict:
        """Recursive helper for :meth:`_smart_cleanup`."""
        result: dict = {}
        for key, value in current.items():
            if key in original:
                if isinstance(value, dict) and isinstance(original.get(key), dict):
                    result[key] = DraftDock._smart_cleanup_dict(
                        value, original[key], defaults.get(key, {}) if isinstance(defaults.get(key), dict) else {}
                    )
                else:
                    result[key] = value
            else:
                default_val = defaults.get(key) if isinstance(defaults, dict) else None
                if isinstance(value, dict) and isinstance(default_val, dict):
                    cleaned = DraftDock._smart_cleanup_dict(value, {}, default_val)
                    if cleaned:
                        result[key] = cleaned
                elif value != default_val:
                    result[key] = value
        return result
