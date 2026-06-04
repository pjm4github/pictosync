"""
properties/mini_toolbar.py

Floating PowerPoint-style mini format toolbar for in-place canvas text editing.

Pops up on right-click over a text selection in a :class:`MetaTextItem` that
is being edited in place.  It formats the selection directly through Qt's
native ``QTextCursor`` / ``QTextCharFormat`` machinery — the same engine the
property panel uses — so changes round-trip into ``meta.blocks`` when the edit
commits.

Focus model
-----------
The widget is a ``Qt.Popup`` so it auto-closes on an outside click and grabs
keyboard input (Esc dismisses).  Its buttons are ``NoFocus`` and it is shown
without activating, so it never pulls keyboard focus off the graphics item.
The selection range is captured at popup time and re-applied on every action,
so formatting is robust even if the visible caret/selection changes.
"""

from __future__ import annotations

from typing import Optional, Tuple

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor, QFont, QTextCursor, QTextCharFormat
from PyQt6.QtWidgets import (
    QColorDialog,
    QHBoxLayout,
    QPushButton,
    QSpinBox,
    QWidget,
)


class MiniFormatToolbar(QWidget):
    """A small floating toolbar with bold/italic/underline/strike/colour/size."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(
            parent,
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setObjectName("MiniFormatToolbar")

        self._item = None  # the MetaTextItem being edited
        self._sel: Tuple[int, int] = (0, 0)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.setSpacing(2)

        self._btn_bold = self._make_toggle("B", "Bold", bold=True)
        self._btn_italic = self._make_toggle("I", "Italic", italic=True)
        self._btn_underline = self._make_toggle("U", "Underline", underline=True)
        self._btn_strike = self._make_toggle("S", "Strikethrough", strike=True)
        self._btn_bold.clicked.connect(self._toggle_bold)
        self._btn_italic.clicked.connect(self._toggle_italic)
        self._btn_underline.clicked.connect(self._toggle_underline)
        self._btn_strike.clicked.connect(self._toggle_strike)
        for b in (self._btn_bold, self._btn_italic,
                  self._btn_underline, self._btn_strike):
            lay.addWidget(b)

        self._btn_color = QPushButton("A", self)
        self._btn_color.setToolTip("Text colour")
        self._btn_color.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._btn_color.setFixedSize(26, 24)
        self._btn_color.clicked.connect(self._pick_color)
        lay.addWidget(self._btn_color)

        self._spin_size = QSpinBox(self)
        self._spin_size.setToolTip("Font size")
        self._spin_size.setRange(6, 96)
        self._spin_size.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._spin_size.setFixedWidth(48)
        self._spin_size.valueChanged.connect(self._apply_size)
        lay.addWidget(self._spin_size)

        self.setStyleSheet(
            "#MiniFormatToolbar { background: palette(window); "
            "border: 1px solid palette(mid); border-radius: 4px; }"
        )

    # ── Construction helpers ──────────────────────────────────────────

    def _make_toggle(self, text: str, tip: str, *, bold=False, italic=False,
                     underline=False, strike=False) -> QPushButton:
        btn = QPushButton(text, self)
        btn.setToolTip(tip)
        btn.setCheckable(True)
        btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn.setFixedSize(26, 24)
        f = QFont(btn.font())
        f.setBold(bold)
        f.setItalic(italic)
        f.setUnderline(underline)
        f.setStrikeOut(strike)
        btn.setFont(f)
        return btn

    # ── Public API ────────────────────────────────────────────────────

    def popup_for(self, item, global_pos: QPoint) -> None:
        """Attach to *item*'s current selection and show at *global_pos*."""
        cur = item.textCursor()
        if not cur.hasSelection():
            return
        self._item = item
        self._sel = (cur.selectionStart(), cur.selectionEnd())
        self._sync_states()
        self.adjustSize()
        self.move(global_pos)
        self.show()

    # ── Selection-targeted formatting ─────────────────────────────────

    def _cursor(self) -> QTextCursor:
        cur = QTextCursor(self._item.document())
        start, end = self._sel
        cur.setPosition(start)
        cur.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        return cur

    def _merge(self, fmt: QTextCharFormat) -> None:
        cur = self._cursor()
        cur.mergeCharFormat(fmt)
        # Re-show the selection so the formatted run stays highlighted.
        self._item.setTextCursor(cur)

    def _sel_char_format(self) -> QTextCharFormat:
        return self._cursor().charFormat()

    def _sync_states(self) -> None:
        """Reflect the selection's current format on the buttons/spin."""
        cf = self._sel_char_format()
        for b in (self._btn_bold, self._btn_italic,
                  self._btn_underline, self._btn_strike):
            b.blockSignals(True)
        self._btn_bold.setChecked(cf.fontWeight() >= QFont.Weight.Bold)
        self._btn_italic.setChecked(cf.fontItalic())
        self._btn_underline.setChecked(cf.fontUnderline())
        self._btn_strike.setChecked(cf.fontStrikeOut())
        for b in (self._btn_bold, self._btn_italic,
                  self._btn_underline, self._btn_strike):
            b.blockSignals(False)
        pt = int(round(cf.fontPointSize())) or 12
        self._spin_size.blockSignals(True)
        self._spin_size.setValue(max(6, min(96, pt)))
        self._spin_size.blockSignals(False)

    # ── Actions ───────────────────────────────────────────────────────

    def _toggle_bold(self) -> None:
        on = self._btn_bold.isChecked()
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Weight.Bold if on else QFont.Weight.Normal)
        self._merge(fmt)

    def _toggle_italic(self) -> None:
        fmt = QTextCharFormat()
        fmt.setFontItalic(self._btn_italic.isChecked())
        self._merge(fmt)

    def _toggle_underline(self) -> None:
        fmt = QTextCharFormat()
        fmt.setFontUnderline(self._btn_underline.isChecked())
        self._merge(fmt)

    def _toggle_strike(self) -> None:
        fmt = QTextCharFormat()
        fmt.setFontStrikeOut(self._btn_strike.isChecked())
        self._merge(fmt)

    def _apply_size(self, value: int) -> None:
        fmt = QTextCharFormat()
        fmt.setFontPointSize(float(value))
        self._merge(fmt)

    def _pick_color(self) -> None:
        cf = self._sel_char_format()
        initial = cf.foreground().color() if cf.foreground().style() != Qt.BrushStyle.NoBrush \
            else QColor("#000000")
        # The modal dialog may dismiss this popup; the captured selection range
        # is re-resolved in _merge, so the colour still lands on the right text.
        color = QColorDialog.getColor(
            initial, self, "Text colour",
            QColorDialog.ColorDialogOption.ShowAlphaChannel,
        )
        if not color.isValid():
            return
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        self._merge(fmt)

    # ── Lifecycle ─────────────────────────────────────────────────────

    def hideEvent(self, event):
        # Hand keyboard focus back to the edited item so the user can keep
        # typing; a later click on empty canvas then commits the edit.
        item = self._item
        super().hideEvent(event)
        if item is not None and getattr(item, "_editing", False):
            item.setFocus(Qt.FocusReason.PopupFocusReason)
