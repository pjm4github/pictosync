"""
canvas/text_edit.py

Shared PowerPoint-style in-place text editing for canvas items.

Two text-bearing cases share one lifecycle:

* :class:`MetaTextItem` — the item *is* the ``QGraphicsTextItem``.
* Shape labels — the text lives in a child ``QGraphicsTextItem``; here that
  child is an :class:`EditableLabelItem` and the parent shape mixes in
  :class:`LabelEditableMixin` to route a double-click to it.

:class:`InPlaceTextEditMixin` holds the lifecycle (enter / commit / focus
guard / mini-toolbar / ``blocks`` round-trip) and defers the model-specific
bits to small hooks so both cases reuse the same code path.
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsTextItem


class InPlaceTextEditMixin:
    """In-place editing lifecycle for a ``QGraphicsTextItem`` subclass.

    Concrete classes override the ``_inplace_*`` hooks to point the shared
    machinery at the right ``AnnotationContents`` (their own ``meta`` or an
    owner shape's) and re-render target.
    """

    # ── Setup ─────────────────────────────────────────────────────────

    def _init_inplace(self) -> None:
        self._editing = False
        self._edit_old_blocks: Optional[list] = None
        self._mini_toolbar = None

    # ── Hooks (override in concrete classes) ──────────────────────────

    def _inplace_meta(self):
        """Return the ``AnnotationContents`` whose ``blocks`` are edited."""
        raise NotImplementedError

    def _inplace_notify(self) -> None:
        """Notify the sync layer that the owning annotation changed."""

    def _inplace_render(self) -> None:
        """Re-render the display from ``meta`` (after commit / undo)."""

    def _inplace_reflow(self) -> None:
        """Re-layout the text as it changes during typing (no re-render)."""

    def _inplace_request_edit(self) -> None:
        """Surface the property panel's Contents tab (optional)."""

    def _inplace_finish(self, old_blocks: list, new_blocks: list) -> None:
        """Push an undo command for a committed edit (optional)."""

    def _inplace_on_enter(self) -> None:
        """Per-target setup when entering edit (visibility, freeze move…)."""

    def _inplace_on_exit(self) -> None:
        """Per-target teardown when leaving edit."""

    # ── Lifecycle ─────────────────────────────────────────────────────

    def _blocks_snapshot(self) -> list:
        meta = self._inplace_meta()
        return [b.to_dict() for b in (meta.blocks or [])]

    def _enter_edit_mode(self) -> None:
        if self._editing:
            return
        self._editing = True
        self._edit_old_blocks = self._blocks_snapshot()
        self._inplace_request_edit()
        self._inplace_on_enter()
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self._seed_default_format()
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        try:
            self.document().contentsChanged.connect(self._on_inplace_contents_changed)
        except (TypeError, RuntimeError):
            pass

    def _seed_default_format(self) -> None:
        """Apply the item's effective default format to the document/typing
        cursor so the *first* characters typed into an empty box inherit the
        configured font, size, and colour — instead of Qt's bare defaults
        (which only got corrected on focus-out re-render before).
        """
        from PyQt6.QtGui import QFont, QTextCharFormat
        from utils import hex_to_qcolor
        eff = self._inplace_meta().effective_default_format()
        fam = eff.font_family
        size = max(6, int(eff.font_size or 12))

        fnt = QFont(fam) if fam else QFont()
        fnt.setPointSize(size)
        if eff.bold:
            fnt.setBold(True)
        if eff.italic:
            fnt.setItalic(True)
        if eff.underline:
            fnt.setUnderline(True)
        if eff.strikethrough:
            fnt.setStrikeOut(True)
        self.document().setDefaultFont(fnt)
        if eff.color:
            self.setDefaultTextColor(hex_to_qcolor(eff.color, self.defaultTextColor()))

        # Seed the document's default alignment from the frame so the caret /
        # new paragraphs pick up the configured horizontal alignment instead
        # of Qt's hard-coded AlignLeft.
        from PyQt6.QtGui import QTextBlockFormat
        halign = (self._inplace_meta().effective_frame().halign or "center")
        flag = {
            "left": Qt.AlignmentFlag.AlignLeft,
            "center": Qt.AlignmentFlag.AlignHCenter,
            "right": Qt.AlignmentFlag.AlignRight,
            "justified": Qt.AlignmentFlag.AlignJustify,
        }.get(halign, Qt.AlignmentFlag.AlignHCenter)
        opt = self.document().defaultTextOption()
        opt.setAlignment(flag)
        self.document().setDefaultTextOption(opt)

        # Seed the typing format only when the box is empty, so existing runs
        # keep their own formatting.
        if self.toPlainText():
            return
        bf = QTextBlockFormat()
        bf.setAlignment(flag)
        tcf = QTextCharFormat()
        if fam:
            tcf.setFontFamilies([fam])
        tcf.setFontPointSize(float(size))
        if eff.bold:
            tcf.setFontWeight(QFont.Weight.Bold)
        if eff.italic:
            tcf.setFontItalic(True)
        if eff.underline:
            tcf.setFontUnderline(True)
        if eff.strikethrough:
            tcf.setFontStrikeOut(True)
        if eff.color:
            tcf.setForeground(hex_to_qcolor(eff.color, self.defaultTextColor()))
        cur = self.textCursor()
        cur.setBlockFormat(bf)
        cur.setCharFormat(tcf)
        self.setTextCursor(cur)

    def _on_inplace_contents_changed(self) -> None:
        if self._editing:
            self._inplace_reflow()

    def focusOutEvent(self, event):
        """Commit on losing focus — unless focus moved to a formatting surface.

        Interacting with the floating mini-toolbar, opening a combo/colour
        popup, or clicking a property-panel format control must NOT end the
        edit: those handlers act on (and must preserve) the live selection.
        The edit commits only when focus truly leaves (empty canvas, another
        item, etc.).  The model/JSON stay current regardless because each
        format change re-extracts the document to ``meta.blocks``.
        """
        if self._editing and not self._keep_editing_on_focus_out(event):
            self._commit_edit()
        super().focusOutEvent(event)

    def _keep_editing_on_focus_out(self, event) -> bool:
        tb = self._mini_toolbar
        if tb is not None and tb.isVisible():
            return True
        # A popup / dialog opened (combo dropdown, colour dialog).
        if event.reason() in (Qt.FocusReason.PopupFocusReason,
                              Qt.FocusReason.ActiveWindowFocusReason):
            return True
        # Focus moved into the property panel's format controls.
        from PyQt6.QtWidgets import QApplication
        w = QApplication.focusWidget()
        while w is not None:
            if type(w).__name__ in ("PropertyPanel", "PropertyDock"):
                return True
            w = w.parentWidget()
        return False

    def keyPressEvent(self, event):
        """Escape commits the edit and selects the enclosing shape.

        All other keys (arrows, typing, Home/End, …) fall through to
        ``QGraphicsTextItem`` so the document's caret/selection responds
        natively.  The text only loses focus on Escape or a click outside.
        """
        if self._editing and event.key() == Qt.Key.Key_Escape:
            self._commit_edit()
            shape = getattr(self, "_owner", None) or self
            sc = self.scene()
            if sc is not None:
                sc.clearSelection()
            shape.setSelected(True)
            event.accept()
            return
        super().keyPressEvent(event)

    def contextMenuEvent(self, event):
        """Right-click over a selection while editing → mini format toolbar."""
        if self._editing:
            cur = self.textCursor()
            if cur.hasSelection():
                self._show_mini_toolbar(event.screenPos())
                event.accept()
                return
        super().contextMenuEvent(event)

    def _show_mini_toolbar(self, global_pos) -> None:
        from properties.mini_toolbar import MiniFormatToolbar
        if self._mini_toolbar is None:
            self._mini_toolbar = MiniFormatToolbar()
        self._mini_toolbar.popup_for(self, global_pos)

    def _commit_edit(self) -> None:
        from text_convert import qtextdoc_to_blocks
        from models import TextBlock, _blocks_to_legacy_text

        self._editing = False
        if self._mini_toolbar is not None and self._mini_toolbar.isVisible():
            self._mini_toolbar.hide()
        try:
            self.document().contentsChanged.disconnect(
                self._on_inplace_contents_changed)
        except (TypeError, RuntimeError):
            pass
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        cur = self.textCursor()
        cur.clearSelection()
        self.setTextCursor(cur)

        meta = self._inplace_meta()
        default_fmt = meta.effective_default_format()
        raw = qtextdoc_to_blocks(self.document(), default_fmt)
        new_blocks = [TextBlock.from_dict(b) for b in raw]
        meta.blocks = new_blocks
        meta.text = _blocks_to_legacy_text(new_blocks)
        self._inplace_on_exit()
        self._inplace_render()
        self._inplace_notify()

        old_blocks = self._edit_old_blocks
        new_snapshot = [b.to_dict() for b in new_blocks]
        if old_blocks is not None and old_blocks != new_snapshot:
            self._inplace_finish(old_blocks, new_snapshot)
        self._edit_old_blocks = None


class EditableLabelItem(InPlaceTextEditMixin, QGraphicsTextItem):
    """Child text item for a shape's label, editable in place.

    The edited text is committed back to the *owner* shape's
    ``meta.blocks`` so the shape, property panel, and JSON editor stay in
    sync through the one shared model.
    """

    # Class-level callbacks, wired by MainWindow.  Called with the *owner*.
    on_request_edit = None           # (owner) -> None
    on_text_edit_finished = None     # (owner, old_blocks, new_blocks) -> None

    def __init__(self, owner: QGraphicsItem):
        QGraphicsTextItem.__init__(self, owner)
        self._owner = owner
        self._init_inplace()
        self._saved_owner_movable = None
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

    # ── Begin editing from the parent shape's double-click ────────────

    def _begin_edit_at(self, owner_pos) -> None:
        """Enter edit mode and place the caret nearest *owner_pos*."""
        self._enter_edit_mode()
        local = self.mapFromParent(owner_pos)
        cur = self.textCursor()
        pos = -1
        try:
            pos = self.document().documentLayout().hitTest(
                local, Qt.HitTestAccuracy.FuzzyHit)
        except (TypeError, RuntimeError):
            pos = -1
        if pos >= 0:
            cur.setPosition(pos)
        else:
            cur.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cur)

    # ── Hooks ─────────────────────────────────────────────────────────

    def _inplace_meta(self):
        return self._owner.meta

    def _inplace_notify(self) -> None:
        if hasattr(self._owner, "_notify_changed"):
            self._owner._notify_changed()

    def _inplace_render(self) -> None:
        if hasattr(self._owner, "_update_label_text"):
            self._owner._update_label_text()

    def _inplace_reflow(self) -> None:
        if hasattr(self._owner, "_update_label_position"):
            self._owner._update_label_position()
        # Keep an empty/short label visible while it is being edited
        # (``_update_label_position`` hides labels with no content).
        self.setVisible(True)

    def _inplace_request_edit(self) -> None:
        if EditableLabelItem.on_request_edit:
            EditableLabelItem.on_request_edit(self._owner)

    def _inplace_finish(self, old_blocks: list, new_blocks: list) -> None:
        if EditableLabelItem.on_text_edit_finished:
            EditableLabelItem.on_text_edit_finished(
                self._owner, old_blocks, new_blocks)

    def _inplace_on_enter(self) -> None:
        # Make sure the (possibly empty) label is visible and positioned, and
        # freeze the owner so a text drag-select doesn't move the shape.
        self.setVisible(True)
        if hasattr(self._owner, "_update_label_position"):
            self._owner._update_label_position()
        self.setVisible(True)
        flags = self._owner.flags()
        self._saved_owner_movable = bool(
            flags & QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self._owner.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)

    def _inplace_on_exit(self) -> None:
        if self._saved_owner_movable is not None:
            self._owner.setFlag(
                QGraphicsItem.GraphicsItemFlag.ItemIsMovable,
                self._saved_owner_movable)
            self._saved_owner_movable = None


class EditableSectionItem(QGraphicsTextItem):
    """Plain-text in-place editor for one ``MetaSeqBlockItem`` region.

    A sequence-block region's text lives as a ``|``-separated segment of the
    owner's ``meta.tech`` and is displayed as italic ``[text]`` — there is no
    per-run formatting in that model, so this is a deliberately lightweight
    plain-text editor (no rich blocks, no mini-toolbar).  Double-clicking a
    region shows its raw text for editing and commits the edited segment back
    on focus-out.
    """

    # Wired by MainWindow.  Called with the owner seqblock item.
    on_request_edit = None  # (owner) -> None

    def __init__(self, owner: QGraphicsItem, index: int):
        QGraphicsTextItem.__init__(self, owner)
        self._owner = owner
        self._index = index
        self._editing = False
        self._saved_owner_movable = None
        self.setAcceptHoverEvents(False)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

    def begin_edit(self, raw_text: str) -> None:
        """Show *raw_text* (un-bracketed) and start editing this region."""
        if self._editing:
            return
        self._editing = True
        self.setPlainText(raw_text)
        self.setVisible(True)
        if hasattr(self._owner, "_update_label_position"):
            self._owner._update_label_position()
            self.setVisible(True)
        if EditableSectionItem.on_request_edit:
            EditableSectionItem.on_request_edit(self._owner)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        # Freeze owner movement so a text drag-select doesn't move the block.
        flags = self._owner.flags()
        self._saved_owner_movable = bool(
            flags & QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self._owner.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        cur = self.textCursor()
        cur.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cur)

    def focusOutEvent(self, event):
        if self._editing:
            self._commit()
        super().focusOutEvent(event)

    def _commit(self) -> None:
        self._editing = False
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        if self._saved_owner_movable is not None:
            self._owner.setFlag(
                QGraphicsItem.GraphicsItemFlag.ItemIsMovable,
                self._saved_owner_movable)
            self._saved_owner_movable = None
        text = self.toPlainText().strip()
        if hasattr(self._owner, "_set_section_text"):
            self._owner._set_section_text(self._index, text)


def label_hit_at(label_item, parent_pos, pad_w: float = 20.0,
                 pad_h: float = 12.0) -> bool:
    """Whether *parent_pos* (in the owner's local coords) hits the label.

    Used by items whose double-click is already bound to another action
    (curve node editing, polygon vertex editing) to decide between editing
    the label and toggling that mode.  For an empty/short label the hit
    region falls back to a padded box around the label's anchor so a click
    near the midpoint still starts a new edge label.
    """
    from PyQt6.QtCore import QRectF
    if not isinstance(label_item, EditableLabelItem):
        return False
    br = label_item.boundingRect()
    if br.width() > 2 and br.height() > 2:
        rect = label_item.mapToParent(br).boundingRect()
    else:
        rect = QRectF()
    if rect.width() < 2 * pad_w or rect.height() < pad_h:
        p = label_item.pos()
        rect = QRectF(p.x() - pad_w, p.y() - pad_h, 2 * pad_w, 2 * pad_h)
    return rect.contains(parent_pos)


class LabelEditableMixin:
    """Routes a shape's double-click into its child :class:`EditableLabelItem`.

    Placed FIRST in a shape's base list so this ``mouseDoubleClickEvent`` wins
    over the Qt base class's, then chains via ``super()``.
    """

    def mouseDoubleClickEvent(self, event):
        label = getattr(self, "_label_item", None)
        if (event.button() == Qt.MouseButton.LeftButton
                and isinstance(label, EditableLabelItem)):
            label._begin_edit_at(event.pos())
            event.accept()
            return
        super().mouseDoubleClickEvent(event)
