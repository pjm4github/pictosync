"""
editor/code_editor.py

Enhanced JSON code editor with line numbers, code folding, and annotation tracking.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QTextCursor
from PyQt6.QtWidgets import QPlainTextEdit, QWidget

from settings import get_settings


# =============================================================================
# Cached editor settings - initialized once to avoid repeated lookups during paint
# =============================================================================

class _CachedEditorSettings:
    """Cache for editor settings values to avoid repeated lookups during paint."""

    _instance = None

    def __init__(self):
        self._initialized = False
        # Default values (used if settings unavailable)
        self.fold_width = 14
        self.left_margin = 8
        self.right_margin = 4
        self.highlight_bar_width = 4
        self.font_family = "Consolas"
        self.font_size = 10
        self.tab_width = 4

    def _ensure_initialized(self):
        """Load settings on first access."""
        if self._initialized:
            return
        try:
            s = get_settings().settings.editor
            self.fold_width = s.folding.width
            self.left_margin = s.line_numbers.left_margin
            self.right_margin = s.line_numbers.right_margin
            self.highlight_bar_width = s.line_numbers.highlight_bar_width
            self.font_family = s.font.family
            self.font_size = s.font.size
            self.tab_width = s.font.tab_width
        except Exception:
            pass  # Use defaults
        self._initialized = True

    @classmethod
    def get(cls) -> "_CachedEditorSettings":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        cls._instance._ensure_initialized()
        return cls._instance


class LineNumberArea(QWidget):
    """Widget that displays line numbers alongside the code editor."""

    def __init__(self, editor: "JsonCodeEditor"):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return self.editor.line_number_area_size_hint()

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)

    def mousePressEvent(self, event):
        self.editor.line_number_area_mouse_press(event)


class FoldingArea(QWidget):
    """Widget that displays folding markers alongside the code editor."""

    def __init__(self, editor: "JsonCodeEditor"):
        super().__init__(editor)
        self.editor = editor
        self.setMouseTracking(True)
        self._hover_line = -1

    @property
    def fold_width(self) -> int:
        """Get fold width from settings. Default: 14 pixels."""
        return _CachedEditorSettings.get().fold_width

    def sizeHint(self):
        return QSize(self.fold_width, 0)

    def paintEvent(self, event):
        self.editor.folding_area_paint_event(event)

    def mousePressEvent(self, event):
        self.editor.folding_area_mouse_press(event)

    def mouseMoveEvent(self, event):
        block = self.editor.firstVisibleBlock()
        top = int(self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top())

        while block.isValid():
            if block.isVisible():
                block_top = top
                block_bottom = top + int(self.editor.blockBoundingRect(block).height())
                if block_top <= event.pos().y() < block_bottom:
                    old_hover = self._hover_line
                    self._hover_line = block.blockNumber()
                    if old_hover != self._hover_line:
                        self.update()
                    break
            top += int(self.editor.blockBoundingRect(block).height())
            block = block.next()

    def leaveEvent(self, event):
        self._hover_line = -1
        self.update()


class JsonCodeEditor(QPlainTextEdit):
    """
    Enhanced JSON code editor with:
    - Line numbers
    - Code folding for objects and arrays
    - Annotation ID tracking (emits signal when cursor enters an annotation block)
    """

    # Signal emitted when the cursor moves into a different annotation's JSON block
    # Emits the annotation ID (e.g., "a000001") or empty string if not in an annotation
    cursor_annotation_changed = pyqtSignal(str)

    # Default line number colors (Foundation Dark theme)
    DEFAULT_LINE_COLORS = {
        "background": "#1a1a1a",
        "text": "#606060",
        "text_active": "#ffffff",
        "highlight_bg": "#2A3A4A",
        "highlight_bar": "#0078D4",
        "current_line_bg": "#2d2d2d",
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        # Line number area
        self.line_number_area = LineNumberArea(self)

        # Folding area
        self.folding_area = FoldingArea(self)

        # Track folded blocks: set of block numbers that are fold headers with content hidden
        self._folded_blocks: set = set()

        # Track fold regions: dict mapping fold header block number to (start_pos, end_pos)
        self._fold_regions: Dict[int, Tuple[int, int]] = {}

        # Current annotation ID the cursor is in
        self._current_annotation_id: str = ""

        # Highlighted annotation ID (from canvas selection)
        self._highlighted_annotation_id: str = ""
        self._highlighted_line_range: Tuple[int, int] = (-1, -1)  # (start_line, end_line) inclusive

        # Flag to prevent circular updates
        self._suppress_cursor_signal = False

        # Line number area colors (theme-aware)
        self._line_colors = dict(self.DEFAULT_LINE_COLORS)

        # Connect signals
        self.blockCountChanged.connect(self._update_margins)
        self.updateRequest.connect(self._update_line_number_area)
        self.cursorPositionChanged.connect(self._on_cursor_position_changed)
        self.textChanged.connect(self._recompute_fold_regions)

        # Initial setup
        self._update_margins()
        self._recompute_fold_regions()

        # Set monospace font from settings. Defaults: "Consolas", 10pt
        cached = _CachedEditorSettings.get()
        font = QFont(cached.font_family, cached.font_size)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)

        # Tab width from settings. Default: 4 characters
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * cached.tab_width)

    def set_line_number_colors(self, colors: Dict[str, str]):
        """
        Set the line number area colors.

        Args:
            colors: Dict with keys: background, text, text_active, highlight_bg,
                   highlight_bar, current_line_bg
        """
        self._line_colors = dict(self.DEFAULT_LINE_COLORS)
        self._line_colors.update(colors)
        self.line_number_area.update()
        self.folding_area.update()

    def line_number_area_width(self) -> int:
        """Calculate the width needed for line numbers."""
        digits = len(str(max(1, self.blockCount())))
        # Left margin from settings. Default: 8 pixels
        left_margin = _CachedEditorSettings.get().left_margin
        space = left_margin + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def line_number_area_size_hint(self):
        return QSize(self.line_number_area_width(), 0)

    def _update_margins(self):
        """Update the viewport margins to make room for line numbers and folding."""
        # Fold width from settings. Default: 14 pixels
        left_margin = self.line_number_area_width() + self.folding_area.fold_width
        self.setViewportMargins(left_margin, 0, 0, 0)

    def _update_line_number_area(self, rect, dy):
        """Update line number area when scrolling or content changes."""
        if dy:
            self.line_number_area.scroll(0, dy)
            self.folding_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
            self.folding_area.update(0, rect.y(), self.folding_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self._update_margins()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        ln_width = self.line_number_area_width()
        # Fold width from settings. Default: 14 pixels
        fold_width = self.folding_area.fold_width

        self.line_number_area.setGeometry(cr.left(), cr.top(), ln_width, cr.height())
        self.folding_area.setGeometry(cr.left() + ln_width, cr.top(), fold_width, cr.height())

    def line_number_area_paint_event(self, event):
        """Paint the line numbers with selection highlight bar."""
        painter = QPainter(self.line_number_area)

        # Get colors from theme configuration
        colors = self._line_colors

        # Background for the gutter (slightly different from editor)
        painter.fillRect(event.rect(), QColor(colors["background"]))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        # Current line highlighting
        current_block = self.textCursor().block().blockNumber()

        # Get cached settings for paint loop. Defaults: highlight_bar=4px, right_margin=4px
        cached = _CachedEditorSettings.get()
        highlight_bar_width = cached.highlight_bar_width
        right_margin = cached.right_margin
        highlight_start, highlight_end = self._highlighted_line_range

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                block_height = int(self.blockBoundingRect(block).height())

                # Check if this line is in the highlighted annotation range
                in_highlight_range = highlight_start <= block_number <= highlight_end

                # Draw highlight bar for selected annotation
                if in_highlight_range:
                    painter.fillRect(0, top, highlight_bar_width, block_height,
                                    QColor(colors["highlight_bar"]))

                if block_number == current_block:
                    # Current cursor line - slightly different background
                    painter.fillRect(highlight_bar_width, top,
                                    self.line_number_area.width() - highlight_bar_width,
                                    block_height, QColor(colors["current_line_bg"]))
                    painter.setPen(QColor(colors["text_active"]))
                elif in_highlight_range:
                    # Lines in highlighted range - highlight background
                    painter.fillRect(highlight_bar_width, top,
                                    self.line_number_area.width() - highlight_bar_width,
                                    block_height, QColor(colors["highlight_bg"]))
                    painter.setPen(QColor(colors["text_active"]))
                else:
                    # Normal lines - dimmed text color
                    painter.setPen(QColor(colors["text"]))

                # Use cached right_margin from above
                painter.drawText(highlight_bar_width, top,
                                self.line_number_area.width() - highlight_bar_width - right_margin,
                                block_height,
                                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

        painter.end()

    def line_number_area_mouse_press(self, event):
        """Handle click on line number to select entire line."""
        block = self.firstVisibleBlock()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())

        while block.isValid():
            if block.isVisible():
                block_top = top
                block_bottom = top + int(self.blockBoundingRect(block).height())
                if block_top <= event.pos().y() < block_bottom:
                    cursor = QTextCursor(block)
                    cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                    cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
                    self.setTextCursor(cursor)
                    break
            top += int(self.blockBoundingRect(block).height())
            block = block.next()

    def folding_area_paint_event(self, event):
        """Paint the folding markers."""
        painter = QPainter(self.folding_area)

        # Get colors from theme configuration
        colors = self._line_colors

        # Folding area background matches line number area
        painter.fillRect(event.rect(), QColor(colors["background"]))

        block = self.firstVisibleBlock()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible():
                block_number = block.blockNumber()
                block_height = int(self.blockBoundingRect(block).height())

                if block_number in self._fold_regions:
                    # This block can be folded
                    is_folded = block_number in self._folded_blocks
                    is_hover = self.folding_area._hover_line == block_number

                    # Draw fold indicator
                    # Fold width from settings. Default: 14 pixels
                    fold_width = self.folding_area.fold_width
                    rect_size = 9
                    x = (fold_width - rect_size) // 2
                    y = top + (block_height - rect_size) // 2

                    if is_hover:
                        painter.fillRect(x - 1, y - 1, rect_size + 2, rect_size + 2,
                                        QColor(colors["current_line_bg"]))

                    painter.setPen(QPen(QColor(colors["text"]), 1))
                    painter.drawRect(x, y, rect_size, rect_size)

                    # Draw minus or plus
                    painter.setPen(QPen(QColor(colors["text_active"]), 1))
                    mid_y = y + rect_size // 2
                    painter.drawLine(x + 2, mid_y, x + rect_size - 2, mid_y)  # Horizontal line

                    if is_folded:
                        # Draw vertical line for plus sign
                        mid_x = x + rect_size // 2
                        painter.drawLine(mid_x, y + 2, mid_x, y + rect_size - 2)

            top += int(self.blockBoundingRect(block).height())
            block = block.next()

        painter.end()

    def folding_area_mouse_press(self, event):
        """Handle click on folding area to toggle fold."""
        block = self.firstVisibleBlock()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())

        while block.isValid():
            if block.isVisible():
                block_number = block.blockNumber()
                block_top = top
                block_bottom = top + int(self.blockBoundingRect(block).height())

                if block_top <= event.pos().y() < block_bottom:
                    if block_number in self._fold_regions:
                        self.toggle_fold(block_number)
                    break

            top += int(self.blockBoundingRect(block).height())
            block = block.next()

    def _recompute_fold_regions(self):
        """Recompute foldable regions based on JSON structure."""
        self._fold_regions.clear()
        text = self.toPlainText()

        if not text.strip():
            self.folding_area.update()
            return

        # Track brace/bracket positions and their line numbers
        stack: List[Tuple[int, int, str]] = []  # (position, block_number, char)

        doc = self.document()

        in_string = False
        escape_next = False

        for i, ch in enumerate(text):
            if escape_next:
                escape_next = False
                continue

            if ch == '\\' and in_string:
                escape_next = True
                continue

            if ch == '"':
                in_string = not in_string
                continue

            if in_string:
                continue

            if ch in '{[':
                block = doc.findBlock(i)
                if block.isValid():
                    stack.append((i, block.blockNumber(), ch))
            elif ch in '}]':
                if stack:
                    open_pos, open_block, open_char = stack.pop()
                    close_block = doc.findBlock(i).blockNumber()

                    # Only create fold region if spans multiple lines
                    if close_block > open_block:
                        self._fold_regions[open_block] = (open_pos, i)

        self.folding_area.update()

    def toggle_fold(self, block_number: int):
        """Toggle folding for a given block."""
        if block_number not in self._fold_regions:
            return

        if block_number in self._folded_blocks:
            self._unfold(block_number)
        else:
            self._fold(block_number)

    def _fold(self, block_number: int):
        """Fold the content of a block."""
        if block_number not in self._fold_regions:
            return

        start_pos, end_pos = self._fold_regions[block_number]
        doc = self.document()

        start_block = doc.findBlock(start_pos)
        end_block = doc.findBlock(end_pos)

        # Hide blocks between start and end (exclusive of start block)
        block = start_block.next()
        while block.isValid() and block.blockNumber() < end_block.blockNumber():
            block.setVisible(False)
            block = block.next()

        self._folded_blocks.add(block_number)
        self.viewport().update()
        self.folding_area.update()
        self._update_margins()

    def _unfold(self, block_number: int):
        """Unfold the content of a block."""
        if block_number not in self._fold_regions:
            return

        start_pos, end_pos = self._fold_regions[block_number]
        doc = self.document()

        start_block = doc.findBlock(start_pos)
        end_block = doc.findBlock(end_pos)

        # Show all blocks between start and end
        block = start_block.next()
        while block.isValid() and block.blockNumber() < end_block.blockNumber():
            block.setVisible(True)
            block = block.next()

        self._folded_blocks.discard(block_number)
        self.viewport().update()
        self.folding_area.update()
        self._update_margins()

    def unfold_all(self):
        """Unfold all folded regions."""
        doc = self.document()
        block = doc.begin()
        while block.isValid():
            block.setVisible(True)
            block = block.next()
        self._folded_blocks.clear()
        self.viewport().update()
        self.folding_area.update()

    def fold_all(self):
        """Fold all foldable regions."""
        for block_number in sorted(self._fold_regions.keys(), reverse=True):
            self._fold(block_number)

    def fold_all_annotations(self):
        """Fold only top-level annotation objects (items in the annotations array)."""
        text = self.toPlainText()
        # Find fold regions that correspond to annotation objects
        # These are objects that contain an "id" field at their level
        for block_number in sorted(self._fold_regions.keys(), reverse=True):
            if self._is_annotation_fold_region(block_number, text):
                self._fold(block_number)

    def _is_annotation_fold_region(self, block_number: int, text: str) -> bool:
        """Check if a fold region corresponds to a top-level annotation object."""
        if block_number not in self._fold_regions:
            return False

        start_pos, end_pos = self._fold_regions[block_number]

        # Get the text of this fold region
        region_text = text[start_pos:end_pos + 1]

        # Check if this object has an "id" field at its top level
        # Simple heuristic: look for "id": near the start of the object
        id_pattern = r'^\s*\{\s*"id"\s*:'
        return bool(re.match(id_pattern, region_text))

    def _find_annotation_block_number(self, ann_id: str) -> int:
        """Find the block number for the fold region containing the given annotation ID."""
        if not ann_id:
            return -1

        text = self.toPlainText()

        # Find the "id" field for this annotation
        id_patterns = [f'"id": "{ann_id}"', f'"id":"{ann_id}"']
        id_pos = -1
        for pattern in id_patterns:
            id_pos = text.find(pattern)
            if id_pos >= 0:
                break

        if id_pos < 0:
            return -1

        # Scan backwards to find the opening brace of this annotation object
        brace_depth = 0
        object_start = -1
        in_string = False

        for i in range(id_pos - 1, -1, -1):
            ch = text[i]

            if ch == '"' and (i == 0 or text[i-1] != '\\'):
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
            return -1

        # Find which block this position is in
        doc = self.document()
        block = doc.begin()
        pos = 0

        while block.isValid():
            block_length = block.length()
            if pos <= object_start < pos + block_length:
                return block.blockNumber()
            pos += block_length
            block = block.next()

        return -1

    def focus_on_annotation(self, ann_id: str):
        """
        Focus mode: fold all annotations except the one with the given ID.
        If ann_id is empty, fold all annotations.
        """
        # First unfold all to reset state
        self.unfold_all()

        # Recompute fold regions after unfold
        self._recompute_fold_regions()

        text = self.toPlainText()

        # Find the block number of the annotation to keep open
        keep_open_block = self._find_annotation_block_number(ann_id) if ann_id else -1

        # Fold all annotation regions except the one to keep open
        for block_number in sorted(self._fold_regions.keys(), reverse=True):
            if self._is_annotation_fold_region(block_number, text):
                if block_number != keep_open_block:
                    self._fold(block_number)

    def _on_cursor_position_changed(self):
        """Handle cursor position changes to track which annotation we're in."""
        if self._suppress_cursor_signal:
            return

        # Update line number area to highlight current line
        self.line_number_area.update()

        # Find the annotation ID at the current cursor position
        ann_id = self._find_annotation_at_cursor()

        if ann_id != self._current_annotation_id:
            self._current_annotation_id = ann_id
            self.cursor_annotation_changed.emit(ann_id)

    def _find_annotation_at_cursor(self) -> str:
        """
        Find the annotation ID that contains the current cursor position.
        Searches outward through nested objects until finding one with an "id" field.
        Returns empty string if not within an annotation block.
        """
        cursor_pos = self.textCursor().position()
        text = self.toPlainText()

        if not text.strip():
            return ""

        # Scan from the beginning to properly track string state and brace nesting
        # Build a stack of object start positions as we go
        object_stack = []  # Stack of opening brace positions
        in_string = False
        i = 0

        while i < len(text) and i < cursor_pos:
            ch = text[i]

            # Handle escape sequences in strings
            if ch == '\\' and in_string and i + 1 < len(text):
                i += 2
                continue

            if ch == '"':
                in_string = not in_string
                i += 1
                continue

            if in_string:
                i += 1
                continue

            if ch == '{':
                object_stack.append(i)
            elif ch == '}':
                if object_stack:
                    object_stack.pop()

            i += 1

        # Now object_stack contains positions of all unclosed '{' before cursor
        # Search from innermost to outermost for an object with an "id" field
        while object_stack:
            object_start = object_stack.pop()

            # Find the closing brace of this object
            brace_depth = 1
            object_end = -1
            in_string = False
            i = object_start + 1

            while i < len(text):
                ch = text[i]

                if ch == '\\' and in_string and i + 1 < len(text):
                    i += 2
                    continue

                if ch == '"':
                    in_string = not in_string
                    i += 1
                    continue

                if in_string:
                    i += 1
                    continue

                if ch == '{':
                    brace_depth += 1
                elif ch == '}':
                    brace_depth -= 1
                    if brace_depth == 0:
                        object_end = i
                        break

                i += 1

            # Make sure cursor is within this object
            if object_end < 0 or cursor_pos > object_end + 1:
                continue

            # Extract the object text and look for an "id" field at THIS level
            obj_text = text[object_start:object_end + 1]

            # Look for "id" field that is a direct child of this object
            id_match = self._find_direct_id_field(obj_text)

            if id_match:
                return id_match

        return ""

    def _find_direct_id_field(self, obj_text: str) -> str:
        """
        Find the "id" field that is a direct child of this object (not nested).
        Returns the ID value or empty string if not found.
        """
        # Use regex to find "id": "value" pattern, but verify it's at depth 1
        # First, let's find all potential "id" matches
        import re
        for match in re.finditer(r'"id"\s*:\s*"([^"]*)"', obj_text):
            # Check if this match is at depth 1 (direct child of the object)
            pos = match.start()
            depth = 0
            in_string = False

            for i in range(pos):
                ch = obj_text[i]

                if ch == '\\' and in_string and i + 1 < len(obj_text):
                    continue

                if ch == '"':
                    # Check if escaped
                    if i > 0 and obj_text[i-1] == '\\':
                        continue
                    in_string = not in_string
                    continue

                if in_string:
                    continue

                if ch == '{' or ch == '[':
                    depth += 1
                elif ch == '}' or ch == ']':
                    depth -= 1

            # "id" should be at depth 1 (inside the top-level object)
            if depth == 1:
                return match.group(1)

        return ""

    def set_current_annotation(self, ann_id: str):
        """
        Scroll to and highlight the annotation with the given ID.
        Suppresses the cursor signal to prevent circular updates.
        """
        self._suppress_cursor_signal = True
        try:
            self._current_annotation_id = ann_id
            # The actual scrolling is done by scroll_to_id_top in DraftDock
        finally:
            self._suppress_cursor_signal = False

    def get_current_annotation(self) -> str:
        """Return the current annotation ID the cursor is in."""
        return self._current_annotation_id

    def set_highlighted_annotation(self, ann_id: str):
        """
        Set the annotation to highlight in the line number area.
        Finds the line range for the annotation and triggers a repaint.
        """
        if ann_id == self._highlighted_annotation_id:
            return

        self._highlighted_annotation_id = ann_id

        if not ann_id:
            self._highlighted_line_range = (-1, -1)
        else:
            self._highlighted_line_range = self._find_annotation_line_range(ann_id)

        # Trigger repaint of line number area
        self.line_number_area.update()

    def clear_highlighted_annotation(self):
        """Clear the highlighted annotation."""
        self.set_highlighted_annotation("")

    def _find_annotation_line_range(self, ann_id: str) -> Tuple[int, int]:
        """
        Find the start and end line numbers for an annotation with the given ID.
        Returns (-1, -1) if not found.
        """
        text = self.toPlainText()
        if not text.strip():
            return (-1, -1)

        # Find the "id" field with this annotation ID
        import re
        id_pattern = rf'"id"\s*:\s*"{re.escape(ann_id)}"'
        id_match = re.search(id_pattern, text)

        if not id_match:
            return (-1, -1)

        id_pos = id_match.start()

        # Scan backwards from id_pos to find the opening brace of this object
        brace_depth = 0
        object_start = -1
        in_string = False

        for i in range(id_pos - 1, -1, -1):
            ch = text[i]

            # Handle string detection (scanning backwards)
            if ch == '"' and (i == 0 or text[i-1] != '\\'):
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
            return (-1, -1)

        # Now find the closing brace of this object
        brace_depth = 1
        object_end = -1
        in_string = False

        for i in range(object_start + 1, len(text)):
            ch = text[i]

            if ch == '"' and text[i-1] != '\\':
                in_string = not in_string
                continue

            if in_string:
                continue

            if ch == '{':
                brace_depth += 1
            elif ch == '}':
                brace_depth -= 1
                if brace_depth == 0:
                    object_end = i
                    break

        if object_end < 0:
            return (-1, -1)

        # Convert positions to line numbers
        doc = self.document()
        start_block = doc.findBlock(object_start)
        end_block = doc.findBlock(object_end)

        if start_block.isValid() and end_block.isValid():
            return (start_block.blockNumber(), end_block.blockNumber())

        return (-1, -1)
