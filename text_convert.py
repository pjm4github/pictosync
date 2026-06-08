"""
text_convert.py

Shared conversion between a Qt ``QTextDocument`` and the overlay-2.0
``blocks``/``runs`` text model.

Both the property-panel Contents editor and the on-canvas in-place text
editor extract their edited document through :func:`qtextdoc_to_blocks`, so
the round-trip ``blocks → HTML → QTextDocument → edit → blocks`` is governed
by a single, shared implementation.  Keeping it here (depending only on
``models`` and ``utils``) avoids a circular import between ``canvas`` and
``properties``.
"""

from __future__ import annotations

from typing import Optional

from models import CharFormat


def qtextdoc_to_blocks(doc, doc_default_format: Optional[CharFormat] = None) -> list:
    """Convert a QTextDocument to a list of block dicts (overlay-2.0 format).

    Compares each fragment's character format against *doc_default_format*
    and emits only the fields that differ (sparse run formats).

    Args:
        doc: QTextDocument to traverse.
        doc_default_format: Document-level CharFormat defaults used to suppress
            redundant per-run format fields.

    Returns:
        List of block dicts ready to be stored in ``meta.blocks``.
    """
    from PyQt6.QtGui import QTextCharFormat
    from PyQt6.QtCore import Qt
    from utils import qcolor_to_hex

    if doc_default_format is None:
        doc_default_format = CharFormat()

    # Get the document's default alignment so we can suppress redundant
    # per-block halign when it matches the default (defer to frame).
    _doc_default_align = doc.defaultTextOption().alignment()

    blocks: list = []
    block = doc.begin()
    while block.isValid():
        block_fmt = block.blockFormat()
        alignment = block_fmt.alignment()
        halign = ""
        if alignment & Qt.AlignmentFlag.AlignHCenter:
            halign = "center"
        elif alignment & Qt.AlignmentFlag.AlignRight:
            halign = "right"
        elif alignment & Qt.AlignmentFlag.AlignJustify:
            halign = "justified"
        elif alignment & Qt.AlignmentFlag.AlignLeft:
            halign = "left"
        # Suppress block-level halign when it matches the document default
        # (the frame.halign will be used instead).
        if alignment == _doc_default_align:
            halign = ""

        runs: list = []
        it = block.begin()
        while not it.atEnd():
            fragment = it.fragment()
            if fragment.isValid():
                text = fragment.text()
                char_fmt = fragment.charFormat()

                run_fmt: dict = {}

                weight = char_fmt.fontWeight()
                if weight >= 700:
                    run_fmt["bold"] = True

                if char_fmt.fontItalic():
                    run_fmt["italic"] = True

                if char_fmt.fontUnderline():
                    run_fmt["underline"] = True

                if char_fmt.fontStrikeOut():
                    run_fmt["strikethrough"] = True

                valign_type = char_fmt.verticalAlignment()
                if valign_type == QTextCharFormat.VerticalAlignment.AlignSuperScript:
                    run_fmt["superscript"] = True
                elif valign_type == QTextCharFormat.VerticalAlignment.AlignSubScript:
                    run_fmt["subscript"] = True

                pt = char_fmt.fontPointSize()
                if pt > 0:
                    fsize = int(round(pt))
                    if fsize != doc_default_format.font_size:
                        run_fmt["font_size"] = fsize

                families = char_fmt.fontFamilies()
                family = families[0] if isinstance(families, list) and families else (
                    families if isinstance(families, str) else "")
                if family and family != doc_default_format.font_family:
                    run_fmt["font_family"] = family

                fg = char_fmt.foreground()
                if fg.style() != Qt.BrushStyle.NoBrush:
                    color_hex = qcolor_to_hex(fg.color(), include_alpha=True)
                    if color_hex != doc_default_format.color:
                        run_fmt["color"] = color_hex

                bg = char_fmt.background()
                if bg.style() != Qt.BrushStyle.NoBrush:
                    run_fmt["background_color"] = qcolor_to_hex(
                        bg.color(), include_alpha=True)

                run: dict = {"type": "text", "text": text}
                if run_fmt:
                    run["format"] = run_fmt
                runs.append(run)
            it += 1

        # Emit one block per QTextBlock — INCLUDING empty paragraphs (a blank
        # line typed as a double-return has no text fragment, so ``runs`` is
        # empty).  Skipping them here would silently drop blank lines on the
        # round-trip and shift/merge the surrounding paragraphs.
        if True:
            blk: dict = {"runs": runs}
            if halign:
                blk["halign"] = halign
            top = block_fmt.topMargin()
            bot = block_fmt.bottomMargin()
            if top:
                blk["space_before"] = top
            if bot:
                blk["space_after"] = bot
            line_h = block_fmt.lineHeight()
            line_t = block_fmt.lineHeightType()
            _qt_type_map = {0: "single", 1: "proportional", 2: "fixed",
                            3: "minimum", 4: "line_distance"}
            _type_name = _qt_type_map.get(line_t, "single")
            if _type_name != "single":
                blk["spacing_type"] = _type_name
                blk["spacing_value"] = float(line_h)
                # Legacy line_spacing compat
                if line_t == 1 and line_h and line_h != 100:
                    blk["line_spacing"] = line_h / 100.0
            blocks.append(blk)

        block = block.next()

    return blocks
