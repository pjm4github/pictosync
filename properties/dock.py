"""
properties/dock.py

Property panel widget for editing selected item properties.
Loads UI from Qt Designer-generated properties_ui.py.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from PyQt6.QtCore import Qt, QEvent, QObject, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtWidgets import (
    QColorDialog,
    QGraphicsItem,
    QWidget,
)

import json
import os

from models import AnnotationContents, TextFrame, CharFormat, TextBlock, TextRun, hex_to_css_color
from undo_commands import ChangeStyleCommand, ChangeMetaCommand
from canvas.items import (
    MetaRectItem,
    MetaRoundedRectItem,
    MetaEllipseItem,
    MetaLineItem,
    MetaTextItem,
    MetaHexagonItem,
    MetaCylinderItem,
    MetaBlockArrowItem,
    MetaPolygonItem,
    MetaCurveItem,
    MetaOrthoCurveItem,
    MetaIsoCubeItem,
    MetaSeqBlockItem,
    MetaGroupItem,
)



def _qtextdoc_to_blocks(doc, doc_default_format: Optional[CharFormat] = None) -> list:
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

        if runs:
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


def _format_dsl_label(dsl: dict) -> str:
    """Return a compact display string for the ``dsl`` extras dict.

    Examples::

        {} → "Generic"
        {"ns3": {"tool": "node", "label": "Node"}} → "ns3 / Node"
        {"sequence": {"block_type": "alt"}} → "sequence / alt"
        {"mermaid": {"tool": "c4", "c4": {"type": "container"}}} → "mermaid / c4"
    """
    if not dsl:
        return "Generic"
    parts = []
    for domain, data in dsl.items():
        if isinstance(data, dict):
            detail = (data.get("label") or data.get("tool")
                      or data.get("block_type") or data.get("type") or "")
            parts.append(f"{domain} / {detail}" if detail else domain)
        else:
            parts.append(str(domain))
    return "  |  ".join(parts) if parts else "Generic"


def _blocks_to_html(
    blocks: list,
    default_format: Optional[CharFormat] = None,
    frame_halign: str = "center",
) -> str:
    """Convert overlay-2.0 blocks to an HTML body fragment for QTextEdit.

    Produces ``<p>`` elements with inline ``style`` attributes derived from
    run format overrides.  The *default_format* is used to suppress redundant
    inline styles (run fields that match the document default are omitted).

    Args:
        blocks: List of block dicts or TextBlock objects.
        default_format: Document-level CharFormat used to suppress redundant styles.
        frame_halign: Fallback alignment for blocks without an explicit ``halign``.

    Returns:
        HTML body fragment string (no ``<html>/<head>/<body>`` wrapper).
    """
    import html as _html
    parts: list = []

    for blk in blocks:
        if isinstance(blk, TextBlock):
            blk_halign = blk.halign or frame_halign
            run_list = blk.runs
        else:
            blk_halign = blk.get("halign") or frame_halign
            run_list = [
                TextRun.from_dict(r) if isinstance(r, dict) else r
                for r in blk.get("runs", [])
            ]

        align_css = {
            "left": "left", "center": "center",
            "right": "right", "justified": "justify",
        }.get(blk_halign, "center")

        runs_html = ""
        for run in run_list:
            if isinstance(run, dict):
                run = TextRun.from_dict(run)
            if run.type != "text":
                continue
            span = _html.escape(run.text)
            fmt = run.format
            if fmt:
                if fmt.bold:
                    span = f"<b>{span}</b>"
                if fmt.italic:
                    span = f"<i>{span}</i>"
                if fmt.underline:
                    span = f"<u>{span}</u>"
                if fmt.strikethrough:
                    span = f"<s>{span}</s>"
                if fmt.superscript:
                    span = f"<sup>{span}</sup>"
                if fmt.subscript:
                    span = f"<sub>{span}</sub>"
                styles: list = []
                if fmt.color and fmt.color != (default_format.color if default_format else ""):
                    styles.append(f"color:{hex_to_css_color(fmt.color)}")
                if fmt.background_color:
                    styles.append(f"background-color:{hex_to_css_color(fmt.background_color)}")
                def_size = default_format.font_size if default_format else 0
                if fmt.font_size and fmt.font_size != def_size:
                    styles.append(f"font-size:{fmt.font_size}pt")
                def_family = default_format.font_family if default_format else ""
                if fmt.font_family and fmt.font_family != def_family:
                    styles.append(f"font-family:{fmt.font_family}")
                if styles:
                    span = f"<span style='{';'.join(styles)}'>{span}</span>"
            runs_html += span

        parts.append(f"<p style='margin:0;text-align:{align_css};white-space:pre-wrap;'>{runs_html}</p>")

    return "\n".join(parts)


def _build_adjust_config_from_schema() -> dict:
    """Build ADJUST_CONFIG from annotation_schema.json.

    Scans the schema's ``allOf`` rules to map annotation ``kind`` values to
    geometry definitions, then extracts adjust1/adjust2 properties that carry
    ``ui_label``, ``ui_suffix``, ``ui_min``, and ``ui_max`` metadata.

    Returns:
        Dict keyed by annotation kind (e.g. "roundedrect") with nested dicts
        for "adjust1" and optionally "adjust2".
    """
    schema_path = os.path.join(
        os.path.dirname(__file__), "..", "schemas", "annotation_schema.json"
    )
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    defs = schema.get("$defs", {})

    # Build kind → geometry def name from annotationItem.allOf
    kind_to_geom_def: dict[str, str] = {}
    ann_item = defs.get("annotationItem", {})
    for rule in ann_item.get("allOf", []):
        if_block = rule.get("if", {}).get("properties", {}).get("kind", {})
        kind_val = if_block.get("const")
        if not kind_val:
            continue
        then_geom = rule.get("then", {}).get("properties", {}).get("geom", {})
        ref = then_geom.get("$ref", "")
        if ref.startswith("#/$defs/"):
            kind_to_geom_def[kind_val] = ref.split("/")[-1]

    config: dict = {}
    for kind_val, geom_def_name in kind_to_geom_def.items():
        geom_def = defs.get(geom_def_name, {})
        props = geom_def.get("properties", {})
        adjusts: dict = {}
        for key in ("adjust1", "adjust2", "adjust3"):
            adj = props.get(key)
            if adj and "ui_label" in adj:
                suffix = adj["ui_suffix"]
                scale = 100 if suffix == " %" else 1
                adjusts[key] = {
                    "label": adj["ui_label"],
                    "suffix": suffix,
                    "min": int(round(adj.get("minimum", 0) * scale)),
                    "max": int(round(adj.get("maximum", 0) * scale)),
                }
        if adjusts:
            config[kind_val] = adjusts

    return config


# Single source of truth: built from annotation_schema.json at import time.
ADJUST_CONFIG = _build_adjust_config_from_schema()

# Try to import the compiled UI, fall back to None if not available
try:
    from properties.properties_ui import Ui_PropertyPanel
    HAS_UI = True
except ImportError:
    HAS_UI = False
    Ui_PropertyPanel = None


class _TightItemDelegate(QObject):
    """QStyledItemDelegate replacement that pins row height to font height + 4px.

    Inherits QObject so it can be parented; acts as a delegate via duck-typing
    by subclassing QStyledItemDelegate through a local import.
    """

    @staticmethod
    def install(list_widget):
        """Install a tight delegate on *list_widget* and return it."""
        from PyQt6.QtWidgets import QStyledItemDelegate
        from PyQt6.QtCore import QSize

        class _Delegate(QStyledItemDelegate):
            def sizeHint(self, option, index):
                fm = option.fontMetrics
                return QSize(super().sizeHint(option, index).width(),
                             fm.height() + 4)

        delegate = _Delegate(list_widget)
        list_widget.setItemDelegate(delegate)
        return delegate


class _FocusOutFilter(QObject):
    """Event filter that calls a callback when the watched widget loses focus."""

    def __init__(self, callback, parent=None):
        super().__init__(parent)
        self._callback = callback

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.FocusOut:
            self._callback()
        return False


def _install_persistent_selection_highlight(text_edit) -> None:
    """Make a QTextEdit's selection stay visible when it loses focus.

    Sets the Inactive palette Highlight/HighlightedText colors to match
    the Active ones.  This keeps the Qt-native selection rendering intact
    (character-level formatting remains visible through the highlight) while
    the selection highlight itself doesn't vanish when focus moves to a panel
    control.

    Unlike an ExtraSelection overlay this approach does NOT override
    per-character foreground colors, so font/color changes applied to the
    selection while the widget lacks focus are immediately visible.
    """
    from PyQt6.QtGui import QPalette
    pal = text_edit.palette()
    for role in (QPalette.ColorRole.Highlight, QPalette.ColorRole.HighlightedText):
        active_color = pal.color(QPalette.ColorGroup.Active, role)
        pal.setColor(QPalette.ColorGroup.Inactive, role, active_color)
    text_edit.setPalette(pal)


class PropertyPanel(QWidget):
    """
    Property panel widget for editing selected item properties.

    Loads layout from Qt Designer-generated properties_ui.py.

    Displays two tabs:
    - Image tab: Image info (path, size, mode, depth, file size)
    - Properties tab: Selected item properties (kind, label, tech, note),
      context-sensitive color pickers, and extra controls

    Changes are auto-applied when fields lose focus or change.
    """

    # Emitted when a port ID in the ports list is clicked; carries the ann_id
    port_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_item: Optional[QGraphicsItem] = None
        self._image_info: Dict[str, Any] = {}
        self.undo_stack = None  # Set from main.py after construction
        self._text_contents_is_authoritative = False  # True while QTextEdit drives updates
        self._text_content_just_changed = False       # True during textChanged processing
        self._suppress_cursor_sync = False            # True during set_item to block deferred cursor signals

        if HAS_UI:
            self._init_from_ui()
        else:
            self._init_fallback()

        self._connect_signals()
        self._set_enabled(False)
        if not HAS_UI:
            self._set_color_rows_visible(False, False, False)
            self._set_extra_rows_visible(False, False, False, False, False, False)
            self._set_dash_pattern_visible(False)

    def _apply_compact_style(self):
        """Tighten margins and spacing so the panel fits a narrow dock."""
        from PyQt6.QtWidgets import QGroupBox, QLayout

        # Compact margins on the outer widget layout
        top = self.layout()
        if top:
            top.setContentsMargins(2, 2, 2, 2)
            top.setSpacing(2)

        # Tighten each tab's top-level layout
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if tab and tab.layout():
                tab.layout().setContentsMargins(2, 2, 2, 2)
                tab.layout().setSpacing(2)

        # Tighten every QGroupBox: smaller title padding, compact layout
        for gb in self.findChildren(QGroupBox):
            gb.setStyleSheet(
                "QGroupBox { margin-top: 8px; padding-top: 8px; font-size: 8pt; }"
                "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 4px; }"
            )
            lay = gb.layout()
            if lay:
                lay.setContentsMargins(3, 3, 3, 3)
                lay.setSpacing(2)

        # Tighten any remaining nested layouts that still have default 9px margins
        for lay in self.findChildren(QLayout):
            m = lay.contentsMargins()
            if m.left() > 4:
                lay.setContentsMargins(2, 2, 2, 2)
            if lay.spacing() > 4:
                lay.setSpacing(2)

    def _init_from_ui(self):
        """Initialize from Qt Designer UI file (new two-tab Style/Contents panel)."""
        from PyQt6.QtWidgets import (
            QComboBox as _QComboBox,
            QLabel as _QLabel,
            QLineEdit as _QLineEdit,
            QSpinBox as _QSpinBox,
            QWidget as _QWidget,
        )

        self.ui = Ui_PropertyPanel()
        self.ui.setupUi(self)

        # ── Direct schema-matched widget references ──────────────────
        # Widget names in the .ui file now mirror the annotation schema
        # so most are accessed as self.ui.<schema_field>.

        self.tabs = self.ui.tabs

        # -- Image tab stubs (image info not in this panel) --
        self.img_path = _QLabel("-")
        self.path_scroll = _QWidget()
        self.img_size = _QLabel("-")
        self.img_mode = _QLabel("-")
        self.img_depth = _QLabel("-")
        self.img_filesize = _QLabel("-")

        # -- annotationItem top-level --
        #   schema: id, kind, parent_id, z, dsl
        self.edit_id = self.ui.id               # QLineEdit (read-only)
        self.kind_label = self.ui.kind           # QLineEdit (read-only)
        self.dsl_label = self.ui.dsl             # QLabel for DSL type summary
        self.edit_parent_id = self.ui.parent_id  # QLineEdit
        self.spin_z = self.ui.z                  # QSpinBox

        # -- geom (rect) --
        #   schema: x, y, w, h, adjust1, adjust2, adjust3, angle
        self.spin_x = self.ui.x
        self.spin_y = self.ui.y
        self.spin_w = self.ui.w
        self.spin_h = self.ui.h
        self.adjust1_spin = self.ui.adjust1
        self.adjust2_spin = self.ui.adjust2
        self.adjust3_spin = self.ui.adjust3
        self.adjust1_label = self.ui.label_adjust1
        self.adjust2_label = self.ui.label_adjust2
        self.adjust3_label = self.ui.label_adjust3
        self.angle_spin = self.ui.angle
        self.radius_spin = self.adjust1_spin     # compat alias

        # ── Fix label max-width and font so text isn't cut off ───────
        from PyQt6.QtGui import QFont as _QFont
        from PyQt6.QtCore import QSize as _QSize
        _small_font = _QFont()
        _small_font.setPointSize(7)
        for lbl in (self.adjust1_label, self.adjust2_label, self.adjust3_label):
            lbl.setMaximumSize(_QSize(16777215, 16777215))  # remove width cap
            lbl.setFont(_small_font)
            lbl.setMinimumWidth(0)

        # ── Match spinbox decimal precision to JSON (round1 = 2 dp) ──
        for spin in (self.adjust1_spin, self.adjust2_spin, self.adjust3_spin):
            spin.setDecimals(2)
        self.angle_spin.setDecimals(2)

        # -- geom (line) --
        #   schema: x1, y1, x2, y2
        self.spin_x1 = self.ui.x1
        self.spin_y1 = self.ui.y1
        self.spin_x2 = self.ui.x2
        self.spin_y2 = self.ui.y2

        # ── Pixel spinboxes: 0 decimal places ────────────────────────
        for spin in (self.spin_x, self.spin_y, self.spin_w, self.spin_h,
                     self.spin_x1, self.spin_y1, self.spin_x2, self.spin_y2):
            spin.setDecimals(0)

        self.geom_group = self.ui.group_geom_shape
        self.frame_xywh = self.ui.xywh     # QFrame for rect-like geom
        self.frame_xy12 = self.ui.xy12     # QFrame for line-like geom

        # -- style.pen --
        #   schema: pen.color, pen.width, pen.dash, pen.dash_pattern_length,
        #           pen.dash_solid_percent
        self.pen_color_btn = self.ui.btn_pen_color
        self.pen_color_btn.setText("Pen")
        self.pen_hex_edit = self.ui.hex_pen_color     # QLineEdit
        self.pen_opacity = self.ui.pen_opacity         # QSlider (0-255)
        self.pen_alpha_edit = self.ui.pen_alpha        # QLineEdit (hex alpha)
        self.line_width_spin = self.ui.line_width      # QDoubleSpinBox
        self.dash_combo = self.ui.dash                 # QComboBox
        self.dash_length_spin = self.ui.dash_pattern_length  # QDoubleSpinBox
        self.dash_solid_spin = self.ui.dash_solid_percent    # QSpinBox

        # -- style.fill --
        #   schema: fill.color
        self.fill_color_btn = self.ui.btn_fill_color
        self.fill_color_btn.setText("Fill")
        self.fill_hex_edit = self.ui.hex_fill_color   # QLineEdit
        self.fill_opacity = self.ui.fill_opacity       # QSlider (0-255)
        self.fill_alpha_edit = self.ui.fill_alpha      # QLineEdit (hex alpha)

        # -- style arrow --
        #   schema: arrow (mode), arrow_size (begin/end)
        self.arrow_combo = self.ui.arrows              # QComboBox
        self.arrow_begin_spin = self.ui.arrow_begin_size  # QDoubleSpinBox
        self.arrow_end_spin = self.ui.arrow_end_size      # QDoubleSpinBox
        self.arrow_size_spin = self.arrow_end_spin     # compat alias

        # -- contents (Contents tab) --
        #   schema: text, halign, valign, color, font_family, font_size,
        #           margin_*, wrap, flow_type, image_url, image_anchor
        self.text_contents = self.ui.text             # QTextEdit
        self.ui.contents_splitter.setStretchFactor(0, 4)  # text edit: ~80%
        self.ui.contents_splitter.setStretchFactor(1, 1)  # graphic panel: ~20%
        # Keep text selection visible while the user interacts with panel controls.
        _install_persistent_selection_highlight(self.text_contents)
        self.chk_wrap = self.ui.wrap                  # QCheckBox
        self.text_color_btn = self.ui.btn_text_color
        self.text_color_btn.setText("Text")
        self.text_hex_edit = self.ui.hex_text_color   # QLineEdit
        self.text_opacity = self.ui.text_opacity      # QSlider (0-255)
        self.text_alpha_edit = self.ui.text_alpha     # QLineEdit (hex alpha)
        self.text_halign_combo = self.ui.halign
        self.text_valign_combo = self.ui.valign
        self.combo_font = self.ui.font_family
        self.spin_text_size = self.ui.font_size
        self.spin_margin_left = self.ui.margin_left
        self.spin_margin_right = self.ui.margin_right
        self.spin_margin_top = self.ui.margin_top
        self.spin_margin_bottom = self.ui.margin_bottom
        self.flow_type_combo = self.ui.flow_type
        self.spacing_type_combo = self.ui.spacing_type
        self.spin_spacing_value = self.ui.spacing_value
        self.spin_space_before = self.ui.space_before
        self.spin_space_after = self.ui.space_after
        self.edit_graphic_url = self.ui.image_url
        self.btn_graphic_browse = self.ui.graphic_browse
        self.spin_graphic_anchor = self.ui.image_anchor
        self.chk_bold = self.ui.bold                     # QCheckBox
        self.chk_italic = self.ui.italic                 # QCheckBox
        self.chk_underline = self.ui.underline           # QCheckBox
        self.chk_strikethrough = self.ui.strikethrough   # QCheckBox (UI typo)

        # -- text box dimensions --
        self.spin_text_box_width = self.ui.text_box_width    # QSpinBox
        self.spin_text_box_height = self.ui.text_box_height  # QSpinBox
        self.spin_text_box_width.setRange(0, 2000)
        self.spin_text_box_height.setRange(0, 2000)
        self.spin_text_box_width.setSpecialValueText("Auto")
        self.spin_text_box_height.setSpecialValueText("Auto")
        self.group_text_box_dims = self.ui.group_text_margins_2  # parent group

        # -- text box appearance (background fill + border) --
        self.btn_background_color = self.ui.background_color  # QPushButton
        self.btn_border_color = self.ui.border_color          # QPushButton
        self.chk_border = self.ui.border                      # QCheckBox

        # -- anchor point grid (3x3 text box placement) --
        from properties.anchor_point_widget import AnchorPointWidget
        self.anchor_pt_group = self.ui.anchor_pt_group  # QGroupBox
        self.anchor_pt_widget = AnchorPointWidget(self.anchor_pt_group)
        _grp_lay = self.anchor_pt_group.layout()
        if _grp_lay is None:
            from PyQt6.QtWidgets import QVBoxLayout as _QVL
            _grp_lay = _QVL(self.anchor_pt_group)
            _grp_lay.setContentsMargins(2, 2, 2, 2)
        _grp_lay.addWidget(self.anchor_pt_widget)
        self.anchor_pt_group.setVisible(False)  # hidden by default

        # -- anchor (line/curve text box position along path) --
        self.anchor_frame = self.ui.anchor_frame
        self.anchor_slider = self.ui.anchor          # QSlider
        self.anchor_value_edit = self.ui.anchor_value # QLineEdit
        self.anchor_slider.setRange(0, 100)
        self.anchor_slider.setValue(50)
        self.anchor_value_edit.setText("50")
        self.anchor_frame.setVisible(False)  # hidden by default

        # -- ports / connections --
        self.list_ports = self.ui.ports
        self.list_connections = self.ui.list_connections
        self.group_ports = self.ui.group_ports
        self.group_connections = self.ui.group_connections

        # Tight row height — delegate pins each row to font height + 4px,
        # overriding Qt default item padding and any theme stylesheet inflation.
        self.list_ports.setMinimumHeight(0)
        self.list_ports.setStyleSheet(
            "QListWidget { padding: 0px; }"
            "QListWidget::item { padding: 0px 2px; margin: 0px; border: none; }"
        )
        _TightItemDelegate.install(self.list_ports)
        # Restore parent item highlight when ports list loses focus
        self._ports_focus_filter = _FocusOutFilter(self._on_ports_focus_lost, self)
        self.list_ports.installEventFilter(self._ports_focus_filter)

        # ── Group-box aliases for visibility control ─────────────────
        self.pen_row = self.ui.groupBox_2        # "Line" group
        self.fill_row = self.ui.group_fill       # "Colors" group
        self.text_row = self.ui.group_text_font  # "Font" group
        self.adjust_row = self.ui.groupBox        # "Flow" group box
        self.angle_row = self.angle_spin          # visibility on the spin itself
        self.line_width_row = self.ui.groupBox_2
        self.dash_row = self.dash_combo
        self.dash_pattern_row = self.dash_length_spin
        self.arrow_row = self.arrow_combo
        self.arrow_size_row = self.arrow_size_spin

        # ── Color preview labels (stubs — hex edits serve this role) ─
        self.pen_color_preview = _QLabel()
        self.pen_color_preview.setFixedSize(24, 24)
        self.pen_color_preview.setAutoFillBackground(True)
        self.fill_color_preview = _QLabel()
        self.fill_color_preview.setFixedSize(24, 24)
        self.fill_color_preview.setAutoFillBackground(True)
        self.text_color_preview = _QLabel()
        self.text_color_preview.setFixedSize(24, 24)
        self.text_color_preview.setAutoFillBackground(True)

        # ── Legacy stubs (invisible, keep downstream code alive) ─────
        self.label_edit = _QLineEdit(); self.label_edit.setVisible(False)
        self.tech_edit = _QLineEdit(); self.tech_edit.setVisible(False)
        self.note_edit = _QLineEdit(); self.note_edit.setVisible(False)
        self.label_align = _QComboBox(); self.label_align.addItems(["Left","Center","Right"]); self.label_align.setVisible(False)
        self.tech_align = _QComboBox(); self.tech_align.addItems(["Left","Center","Right"]); self.tech_align.setVisible(False)
        self.note_align = _QComboBox(); self.note_align.addItems(["Left","Center","Right"]); self.note_align.setVisible(False)
        self.label_size = _QSpinBox(); self.label_size.setRange(6,72); self.label_size.setValue(12); self.label_size.setVisible(False)
        self.tech_size = _QSpinBox(); self.tech_size.setRange(6,72); self.tech_size.setValue(10); self.tech_size.setVisible(False)
        self.note_size = _QSpinBox(); self.note_size.setRange(6,72); self.note_size.setValue(10); self.note_size.setVisible(False)
        self.label_row = _QWidget(); self.label_row.setVisible(False)
        self.tech_row = _QWidget(); self.tech_row.setVisible(False)
        self.note_row = _QWidget(); self.note_row.setVisible(False)
        self.text_box_width_spin = _QSpinBox(); self.text_box_width_spin.setRange(0,500); self.text_box_width_spin.setVisible(False)
        self.text_box_width_row = _QWidget(); self.text_box_width_row.setVisible(False)
        self.text_spacing_combo = _QComboBox(); self.text_spacing_combo.addItems(["0","0.5","1","1.5","2"]); self.text_spacing_combo.setVisible(False)

        # Divider count (created dynamically, not in .ui)
        self.divider_count_label = _QLabel("Dividers")
        self.divider_count_spin = _QSpinBox()
        self.divider_count_spin.setRange(0, 3)
        self.divider_count_spin.setValue(0)
        self.divider_count_label.setVisible(False)
        self.divider_count_spin.setVisible(False)
        flow_layout = self.adjust_row.layout()
        if flow_layout:
            flow_layout.insertWidget(0, self.divider_count_label)
            flow_layout.insertWidget(1, self.divider_count_spin)

        # ── "Save as Default" corner button on the tab widget ────────────────
        from PyQt6.QtWidgets import QPushButton as _QPushButton
        self._save_default_btn = _QPushButton("Save as Default")
        self._save_default_btn.setToolTip(
            "Save current Format and Contents settings as new item defaults"
        )
        self._save_default_btn.setVisible(False)
        self._save_default_btn.clicked.connect(self._save_as_default)
        self.tabs.setCornerWidget(
            self._save_default_btn, Qt.Corner.TopRightCorner
        )

        # Apply compact margins after all widgets are wired up.
        # Must run before the font pass below so its QGroupBox stylesheets
        # (which cascade to children) are in place before we override them.
        self._apply_compact_style()

        # ── Fix radio button indicators in the contents-format panel ─────────
        # QWindowsVistaStyle draws ::indicator via native UxTheme, ignoring
        # CSS background-color for :checked.  Fusion uses Qt software rendering
        # which fully honours ::indicator:checked { background-color: ... }.
        from PyQt6.QtWidgets import QStyleFactory as _QSF
        _fusion = _QSF.create("Fusion")
        if _fusion:
            for _rb in (self.ui.no_effect, self.ui.subscript, self.ui.superscript):
                _rb.setStyle(_fusion)

        # ── Lock all widgets in the contents-format scroll area to 8pt ───────
        # Apply an explicit widget-level stylesheet that overrides the inherited
        # theme font-size for every widget type inside the scroll area, then
        # also call setFont() on every child widget so native-painted controls
        # (spin boxes, combo boxes, buttons) are not left at a larger size.
        from PyQt6.QtGui import QFont as _QFont2
        from PyQt6.QtWidgets import QWidget as _QWidgetChild
        _lbl_font = _QFont2()
        _lbl_font.setPointSize(8)
        _sa = self.ui.scrollAreaWidgetContents_2
        _sa.setStyleSheet(
            "QLabel, QCheckBox, QRadioButton, QGroupBox { font-size: 8pt; }"
        )
        for _w in _sa.findChildren(_QWidgetChild):
            _w.setFont(_lbl_font)

        # Wheel events must not change values unless the widget is focused.
        from utils import install_wheel_guard
        install_wheel_guard(_sa)

    def _init_fallback(self):
        """Fallback initialization when UI file is not available."""
        from PyQt6.QtWidgets import (
            QComboBox,
            QFormLayout,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QPushButton,
            QScrollArea,
            QSpinBox,
            QTabWidget,
            QVBoxLayout,
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # === Image Tab ===
        image_tab = QWidget()
        image_layout = QVBoxLayout(image_tab)

        self.img_path = QLabel("-")
        self.img_path.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.img_path.setWordWrap(False)

        self.path_scroll = QScrollArea()
        self.path_scroll.setWidget(self.img_path)
        self.path_scroll.setWidgetResizable(True)
        self.path_scroll.setMinimumWidth(200)
        self.path_scroll.setMaximumHeight(40)
        self.path_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.path_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.path_scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        self.img_size = QLabel("-")
        self.img_mode = QLabel("-")
        self.img_depth = QLabel("-")
        self.img_filesize = QLabel("-")

        img_form = QFormLayout()
        img_form.addRow("Path:", self.path_scroll)
        img_form.addRow("Size:", self.img_size)
        img_form.addRow("Mode:", self.img_mode)
        img_form.addRow("Color depth:", self.img_depth)
        img_form.addRow("File size:", self.img_filesize)
        image_layout.addLayout(img_form)
        image_layout.addStretch(1)

        self.tabs.addTab(image_tab, "Image")

        # === Properties Tab ===
        props_tab = QWidget()
        props_layout = QVBoxLayout(props_tab)

        form = QFormLayout()
        props_layout.addLayout(form)

        self.kind_label = QLabel("-")

        # Compact styling
        compact_edit_style = "padding: 4px 6px; border: 1px solid #ccc; border-radius: 3px;"
        compact_btn_style = "padding: 2px 6px; font-size: 10px; min-width: 40px;"
        compact_spin_style = "padding: 2px; max-width: 50px;"
        compact_combo_style = "padding: 2px; max-width: 60px; font-size: 10px;"

        # Label row with alignment and font size
        self.label_edit = QLineEdit()
        self.label_edit.setStyleSheet(compact_edit_style)
        self.label_align = QComboBox()
        self.label_align.addItems(["Left", "Center", "Right"])
        self.label_align.setCurrentIndex(1)
        self.label_align.setStyleSheet(compact_combo_style)
        self.label_size = QSpinBox()
        self.label_size.setRange(6, 72)
        self.label_size.setValue(12)
        self.label_size.setStyleSheet(compact_spin_style)

        self.label_row = QWidget()
        label_layout = QHBoxLayout(self.label_row)
        label_layout.setContentsMargins(0, 0, 0, 0)
        label_layout.setSpacing(4)
        label_layout.addWidget(self.label_edit, 1)
        label_layout.addWidget(self.label_align)
        label_layout.addWidget(self.label_size)

        # Tech row
        self.tech_edit = QLineEdit()
        self.tech_edit.setStyleSheet(compact_edit_style)
        self.tech_align = QComboBox()
        self.tech_align.addItems(["Left", "Center", "Right"])
        self.tech_align.setCurrentIndex(1)
        self.tech_align.setStyleSheet(compact_combo_style)
        self.tech_size = QSpinBox()
        self.tech_size.setRange(6, 72)
        self.tech_size.setValue(10)
        self.tech_size.setStyleSheet(compact_spin_style)

        self.tech_row = QWidget()
        tech_layout = QHBoxLayout(self.tech_row)
        tech_layout.setContentsMargins(0, 0, 0, 0)
        tech_layout.setSpacing(4)
        tech_layout.addWidget(self.tech_edit, 1)
        tech_layout.addWidget(self.tech_align)
        tech_layout.addWidget(self.tech_size)

        # Note row
        self.note_edit = QLineEdit()
        self.note_edit.setStyleSheet(compact_edit_style)
        self.note_align = QComboBox()
        self.note_align.addItems(["Left", "Center", "Right"])
        self.note_align.setCurrentIndex(1)
        self.note_align.setStyleSheet(compact_combo_style)
        self.note_size = QSpinBox()
        self.note_size.setRange(6, 72)
        self.note_size.setValue(10)
        self.note_size.setStyleSheet(compact_spin_style)

        self.note_row = QWidget()
        note_layout = QHBoxLayout(self.note_row)
        note_layout.setContentsMargins(0, 0, 0, 0)
        note_layout.setSpacing(4)
        note_layout.addWidget(self.note_edit, 1)
        note_layout.addWidget(self.note_align)
        note_layout.addWidget(self.note_size)

        form.addRow("Kind:", self.kind_label)
        form.addRow("Label:", self.label_row)
        form.addRow("Tech:", self.tech_row)
        form.addRow("Note:", self.note_row)

        # Color picker buttons and previews
        self.pen_color_btn = QPushButton("Pick")
        self.fill_color_btn = QPushButton("Pick")
        self.text_color_btn = QPushButton("Pick")
        self.pen_color_btn.setStyleSheet(compact_btn_style)
        self.fill_color_btn.setStyleSheet(compact_btn_style)
        self.text_color_btn.setStyleSheet(compact_btn_style)

        self.pen_color_preview = QLabel()
        self.pen_color_preview.setFixedSize(24, 24)
        self.pen_color_preview.setAutoFillBackground(True)
        self.fill_color_preview = QLabel()
        self.fill_color_preview.setFixedSize(24, 24)
        self.fill_color_preview.setAutoFillBackground(True)
        self.text_color_preview = QLabel()
        self.text_color_preview.setFixedSize(24, 24)
        self.text_color_preview.setAutoFillBackground(True)

        self.pen_row = QWidget()
        pr_l = QHBoxLayout(self.pen_row)
        pr_l.setContentsMargins(0, 0, 0, 0)
        pr_l.addWidget(self.pen_color_btn)
        pr_l.addWidget(self.pen_color_preview)
        pr_l.addStretch(1)

        self.fill_row = QWidget()
        fr_l = QHBoxLayout(self.fill_row)
        fr_l.setContentsMargins(0, 0, 0, 0)
        fr_l.addWidget(self.fill_color_btn)
        fr_l.addWidget(self.fill_color_preview)
        fr_l.addStretch(1)

        self.text_row = QWidget()
        tr_l = QHBoxLayout(self.text_row)
        tr_l.setContentsMargins(0, 0, 0, 0)
        tr_l.addWidget(self.text_color_btn)
        tr_l.addWidget(self.text_color_preview)
        tr_l.addStretch(1)

        # Unified adjust controls row (adjust1 + adjust2 + adjust3 in one row)
        self.adjust_row = QWidget()
        adjust_l = QHBoxLayout(self.adjust_row)
        adjust_l.setContentsMargins(0, 0, 0, 0)
        self.divider_count_label = QLabel("Dividers")
        self.divider_count_spin = QSpinBox()
        self.divider_count_spin.setRange(0, 3)
        self.divider_count_spin.setValue(0)
        self.adjust1_label = QLabel("Adjust1")
        self.adjust1_spin = QSpinBox()
        self.adjust1_spin.setRange(0, 200)
        self.adjust1_spin.setValue(10)
        self.adjust1_spin.setSuffix(" px")
        self.adjust2_label = QLabel("Adjust2")
        self.adjust2_spin = QSpinBox()
        self.adjust2_spin.setRange(10, 500)
        self.adjust2_spin.setValue(15)
        self.adjust2_spin.setSuffix(" px")
        self.adjust3_label = QLabel("Divider 3")
        self.adjust3_spin = QSpinBox()
        self.adjust3_spin.setRange(0, 100)
        self.adjust3_spin.setValue(83)
        self.adjust3_spin.setSuffix(" %")
        adjust_l.addWidget(self.divider_count_label)
        adjust_l.addWidget(self.divider_count_spin)
        adjust_l.addWidget(self.adjust1_label)
        adjust_l.addWidget(self.adjust1_spin)
        adjust_l.addWidget(self.adjust2_label)
        adjust_l.addWidget(self.adjust2_spin)
        adjust_l.addWidget(self.adjust3_label)
        adjust_l.addWidget(self.adjust3_spin)
        adjust_l.addStretch(1)
        self.radius_spin = self.adjust1_spin  # compat alias

        # Rotation angle control
        self.angle_row = QWidget()
        angle_l = QHBoxLayout(self.angle_row)
        angle_l.setContentsMargins(0, 0, 0, 0)
        angle_l.addWidget(QLabel("Angle:"))
        self.angle_spin = QSpinBox()
        self.angle_spin.setRange(0, 359)
        self.angle_spin.setValue(0)
        self.angle_spin.setSuffix("°")
        self.angle_spin.setWrapping(True)
        angle_l.addWidget(self.angle_spin)
        angle_l.addStretch(1)

        # Line width control with text spacing and valign
        self.line_width_row = QWidget()
        line_width_l = QHBoxLayout(self.line_width_row)
        line_width_l.setContentsMargins(0, 0, 0, 0)
        self.line_width_spin = QSpinBox()
        self.line_width_spin.setRange(1, 20)
        self.line_width_spin.setValue(2)
        self.line_width_spin.setSuffix(" px")
        self.line_width_spin.setStyleSheet("padding: 1px 2px; min-width: 60px; max-height: 20px;")
        line_width_l.addWidget(self.line_width_spin)
        line_width_l.addWidget(QLabel("Spacing:"))
        self.text_spacing_combo = QComboBox()
        self.text_spacing_combo.addItems(["0", "0.5", "1", "1.5", "2"])
        self.text_spacing_combo.setStyleSheet(compact_combo_style)
        line_width_l.addWidget(self.text_spacing_combo)
        line_width_l.addWidget(QLabel("VAlign:"))
        self.text_valign_combo = QComboBox()
        self.text_valign_combo.addItems(["Top", "Middle", "Bottom"])
        self.text_valign_combo.setStyleSheet(compact_combo_style)
        line_width_l.addWidget(self.text_valign_combo)
        line_width_l.addStretch(1)

        # Line dash style control
        self.dash_row = QWidget()
        dash_l = QHBoxLayout(self.dash_row)
        dash_l.setContentsMargins(0, 0, 0, 0)
        self.dash_combo = QComboBox()
        self.dash_combo.addItems(["Solid", "Dashed"])
        self.dash_combo.setStyleSheet(compact_combo_style)
        dash_l.addWidget(self.dash_combo)
        dash_l.addStretch(1)

        # Dash pattern controls
        self.dash_pattern_row = QWidget()
        dash_pattern_l = QHBoxLayout(self.dash_pattern_row)
        dash_pattern_l.setContentsMargins(0, 0, 0, 0)
        dash_pattern_l.setSpacing(2)
        compact_spin_with_suffix = "padding: 1px 2px; min-width: 60px; max-height: 20px;"
        self.dash_length_spin = QSpinBox()
        self.dash_length_spin.setRange(4, 100)
        self.dash_length_spin.setValue(30)
        self.dash_length_spin.setSuffix(" px")
        self.dash_length_spin.setStyleSheet(compact_spin_with_suffix)
        self.dash_solid_spin = QSpinBox()
        self.dash_solid_spin.setRange(1, 99)
        self.dash_solid_spin.setValue(50)
        self.dash_solid_spin.setSuffix(" %")
        self.dash_solid_spin.setStyleSheet(compact_spin_with_suffix)
        dash_pattern_l.addWidget(QLabel("Length:"))
        dash_pattern_l.addWidget(self.dash_length_spin)
        dash_pattern_l.addWidget(QLabel("Solid:"))
        dash_pattern_l.addWidget(self.dash_solid_spin)
        dash_pattern_l.addStretch(1)

        # Arrow mode control
        self.arrow_row = QWidget()
        arr_l = QHBoxLayout(self.arrow_row)
        arr_l.setContentsMargins(0, 0, 0, 0)
        self.arrow_combo = QComboBox()
        self.arrow_combo.addItems(["None", "Start (\u2190)", "End (\u2192)", "Both (\u2194)"])
        self.arrow_combo.setStyleSheet(compact_combo_style)
        arr_l.addWidget(self.arrow_combo)
        arr_l.addStretch(1)

        # Arrow size control
        self.arrow_size_row = QWidget()
        arrow_size_l = QHBoxLayout(self.arrow_size_row)
        arrow_size_l.setContentsMargins(0, 0, 0, 0)
        self.arrow_size_spin = QSpinBox()
        self.arrow_size_spin.setRange(4, 50)
        self.arrow_size_spin.setValue(12)
        self.arrow_size_spin.setSuffix(" px")
        self.arrow_size_spin.setStyleSheet(compact_spin_with_suffix)
        arrow_size_l.addWidget(self.arrow_size_spin)
        arrow_size_l.addStretch(1)

        # Text box width control
        self.text_box_width_row = QWidget()
        text_box_width_l = QHBoxLayout(self.text_box_width_row)
        text_box_width_l.setContentsMargins(0, 0, 0, 0)
        self.text_box_width_spin = QSpinBox()
        self.text_box_width_spin.setRange(0, 500)
        self.text_box_width_spin.setValue(0)
        self.text_box_width_spin.setSuffix(" px")
        self.text_box_width_spin.setStyleSheet(compact_spin_with_suffix)
        self.text_box_width_spin.setSpecialValueText("Auto")
        text_box_width_l.addWidget(self.text_box_width_spin)
        text_box_width_l.addStretch(1)

        form.addRow("Border color:", self.pen_row)
        form.addRow("Fill color:", self.fill_row)
        form.addRow("Text color:", self.text_row)
        form.addRow("Adjust:", self.adjust_row)
        form.addRow("Rotation:", self.angle_row)
        form.addRow("Line width:", self.line_width_row)
        form.addRow("Line style:", self.dash_row)
        form.addRow("Dash pattern:", self.dash_pattern_row)
        form.addRow("Arrow:", self.arrow_row)
        form.addRow("Arrow size:", self.arrow_size_row)
        form.addRow("Text box width:", self.text_box_width_row)

        props_layout.addStretch(1)
        self.tabs.addTab(props_tab, "Properties")

    def _connect_signals(self):
        """Connect all widget signals to handlers."""
        # Ports list — clicking a port ID emits port_selected
        if HAS_UI:
            self.list_ports.currentTextChanged.connect(self._on_port_selected)

        # Text field changes
        self.label_edit.editingFinished.connect(self._apply_changes)
        self.tech_edit.editingFinished.connect(self._apply_changes)
        self.note_edit.editingFinished.connect(self._apply_changes)

        # Alignment and size changes
        self.label_align.currentIndexChanged.connect(self._apply_changes)
        self.label_size.valueChanged.connect(self._apply_changes)
        self.tech_align.currentIndexChanged.connect(self._apply_changes)
        self.tech_size.valueChanged.connect(self._apply_changes)
        self.note_align.currentIndexChanged.connect(self._apply_changes)
        self.note_size.valueChanged.connect(self._apply_changes)

        # Color pickers
        self.pen_color_btn.clicked.connect(self.pick_pen_color)
        self.fill_color_btn.clicked.connect(self.pick_fill_color)
        self.text_color_btn.clicked.connect(self.pick_text_color)

        # Extra controls
        self.adjust1_spin.valueChanged.connect(self._on_adjust1_changed)
        self.line_width_spin.valueChanged.connect(self._on_line_width_changed)
        self.dash_combo.currentIndexChanged.connect(self._on_dash_changed)
        self.dash_length_spin.valueChanged.connect(self._on_dash_pattern_changed)
        self.dash_solid_spin.valueChanged.connect(self._on_dash_pattern_changed)
        self.arrow_combo.currentIndexChanged.connect(self._on_arrow_changed)
        self.arrow_size_spin.valueChanged.connect(self._on_arrow_size_changed)
        self.adjust2_spin.valueChanged.connect(self._on_adjust2_changed)
        self.adjust3_spin.valueChanged.connect(self._on_adjust3_changed)
        self.divider_count_spin.valueChanged.connect(self._on_divider_count_changed)
        self.text_box_width_spin.valueChanged.connect(self._on_text_box_width_changed)
        self.angle_spin.valueChanged.connect(self._on_angle_changed)

        # Opacity sliders and alpha hex edits
        self.pen_opacity.valueChanged.connect(self._on_pen_opacity_changed)
        self.fill_opacity.valueChanged.connect(self._on_fill_opacity_changed)
        self.pen_alpha_edit.editingFinished.connect(self._on_pen_alpha_edited)
        self.fill_alpha_edit.editingFinished.connect(self._on_fill_alpha_edited)
        self.text_alpha_edit.editingFinished.connect(self._on_text_alpha_edited)
        self.pen_hex_edit.editingFinished.connect(self._on_pen_hex_edited)
        self.fill_hex_edit.editingFinished.connect(self._on_fill_hex_edited)
        self.text_hex_edit.editingFinished.connect(self._on_text_hex_edited)
        self.text_opacity.valueChanged.connect(self._on_text_opacity_changed)

        # Text layout controls
        self.text_spacing_combo.currentIndexChanged.connect(self._on_text_spacing_changed)
        self.text_valign_combo.currentIndexChanged.connect(self._on_text_valign_changed)

        # Contents tab signals
        self.text_contents.textChanged.connect(self._on_text_contents_changed)
        self.text_contents.cursorPositionChanged.connect(self._on_text_cursor_changed)
        self.text_contents.selectionChanged.connect(self._on_text_cursor_changed)
        self.text_halign_combo.currentIndexChanged.connect(self._on_halign_changed)
        self.spin_text_size.valueChanged.connect(self._on_font_size_changed)
        self.combo_font.currentFontChanged.connect(self._on_font_changed)
        self.chk_wrap.toggled.connect(self._on_wrap_changed)
        self.flow_type_combo.currentIndexChanged.connect(self._on_flow_type_changed)
        self.spacing_type_combo.currentIndexChanged.connect(self._on_spacing_type_changed)
        self.spin_spacing_value.valueChanged.connect(self._on_spacing_value_changed)
        self.spin_space_before.valueChanged.connect(self._on_space_before_after_changed)
        self.spin_space_after.valueChanged.connect(self._on_space_before_after_changed)
        self.spin_margin_left.valueChanged.connect(self._on_margins_changed)
        self.spin_margin_right.valueChanged.connect(self._on_margins_changed)
        self.spin_margin_top.valueChanged.connect(self._on_margins_changed)
        self.spin_margin_bottom.valueChanged.connect(self._on_margins_changed)
        self.edit_graphic_url.editingFinished.connect(self._on_graphic_url_changed)
        self.spin_graphic_anchor.valueChanged.connect(self._on_graphic_anchor_changed)
        self.chk_bold.toggled.connect(self._on_bold_changed)
        self.chk_italic.toggled.connect(self._on_italic_changed)
        self.chk_underline.toggled.connect(self._on_underline_changed)
        self.chk_strikethrough.toggled.connect(self._on_strikethrough_changed)

        # Text box appearance (background + border) and anchor point grid
        if HAS_UI:
            self.btn_background_color.clicked.connect(self._pick_text_box_background_color)
            self.btn_border_color.clicked.connect(self._pick_text_box_border_color)
            self.chk_border.toggled.connect(self._on_text_box_border_toggled)
            self.anchor_pt_widget.anchor_changed.connect(self._on_anchor_point_changed)
            self.spin_text_box_width.valueChanged.connect(self._on_text_box_dims_changed)
            self.spin_text_box_height.valueChanged.connect(self._on_text_box_dims_changed)

        # Anchor slider/edit for line/curve
        if HAS_UI:
            self.anchor_slider.valueChanged.connect(self._on_anchor_slider_changed)
            self.anchor_value_edit.editingFinished.connect(self._on_anchor_edit_finished)

    def set_image_info(self, info: Dict[str, Any]):
        """Update the image info display."""
        self._image_info = info or {}
        path = str(self._image_info.get("path", "-"))
        self.img_path.setText(path)
        self.img_path.setToolTip(path)
        self.img_size.setText(str(self._image_info.get("size", "-")))
        self.img_mode.setText(str(self._image_info.get("mode", "-")))
        self.img_depth.setText(str(self._image_info.get("depth", "-")))
        self.img_filesize.setText(str(self._image_info.get("filesize", "-")))

    def _set_enabled(self, enabled: bool):
        """Enable or disable item editing controls."""
        self.label_edit.setEnabled(enabled)
        self.tech_edit.setEnabled(enabled)
        self.note_edit.setEnabled(enabled)

        self.label_align.setEnabled(enabled)
        self.label_size.setEnabled(enabled)
        self.tech_align.setEnabled(enabled)
        self.tech_size.setEnabled(enabled)
        self.note_align.setEnabled(enabled)
        self.note_size.setEnabled(enabled)

        self.pen_color_btn.setEnabled(enabled)
        self.fill_color_btn.setEnabled(enabled)
        self.text_color_btn.setEnabled(enabled)
        self.adjust1_spin.setEnabled(enabled)
        self.adjust2_spin.setEnabled(enabled)
        self.adjust3_spin.setEnabled(enabled)
        self.divider_count_spin.setEnabled(enabled)
        self.line_width_spin.setEnabled(enabled)
        self.dash_combo.setEnabled(enabled)
        self.dash_length_spin.setEnabled(enabled)
        self.dash_solid_spin.setEnabled(enabled)
        self.arrow_combo.setEnabled(enabled)
        self.arrow_size_spin.setEnabled(enabled)
        self.text_box_width_spin.setEnabled(enabled)
        self.text_spacing_combo.setEnabled(enabled)
        self.text_valign_combo.setEnabled(enabled)
        self.angle_spin.setEnabled(enabled)

    def _set_extra_rows_visible(self, adjust: bool, line_width: bool, dash: bool, arrow: bool, arrow_size: bool, text_box_width: bool = False, text_layout: bool = False, adjust2: bool = False, adjust3: bool = False, divider_count: bool = False):
        """Show or hide extra control rows."""
        self.adjust_row.setVisible(adjust or divider_count)
        self.adjust1_spin.setVisible(adjust)
        self.adjust1_label.setVisible(adjust)
        # Show/hide adjust2 within the same row
        self.adjust2_label.setVisible(adjust and adjust2)
        self.adjust2_spin.setVisible(adjust and adjust2)
        # Show/hide adjust3 within the same row
        self.adjust3_label.setVisible(adjust and adjust3)
        self.adjust3_spin.setVisible(adjust and adjust3)
        # Show/hide divider count
        self.divider_count_label.setVisible(divider_count)
        self.divider_count_spin.setVisible(divider_count)
        self.line_width_row.setVisible(line_width)
        # text_box_width_row contains both text_box_width spin AND text layout controls
        # Show the row if either text_box_width or text_layout is needed
        self.text_box_width_row.setVisible(text_box_width or text_layout)
        # But only show the text_box_width spin/label for line items
        self.text_box_width_spin.setVisible(text_box_width)
        if HAS_UI and hasattr(self.ui, 'label_text_box_width_title'):
            self.ui.label_text_box_width_title.setVisible(text_box_width)
        self.line_width_spin.setVisible(line_width)
        self.dash_row.setVisible(dash)
        self.dash_combo.setVisible(dash)
        self.arrow_row.setVisible(arrow)
        self.arrow_combo.setVisible(arrow)
        self.arrow_size_row.setVisible(arrow_size)
        self.arrow_size_spin.setVisible(arrow_size)

    def _configure_adjust_controls(self, kind: str):
        """Configure adjust1/adjust2 labels, suffixes, and ranges from ADJUST_CONFIG."""
        cfg = ADJUST_CONFIG.get(kind)
        if not cfg:
            return
        a1 = cfg.get("adjust1")
        if a1:
            self.adjust1_label.setText(a1["label"])
            self.adjust1_spin.blockSignals(True)
            self.adjust1_spin.setSuffix(a1["suffix"])
            self.adjust1_spin.setRange(a1["min"], a1["max"])
            self.adjust1_spin.blockSignals(False)
        a2 = cfg.get("adjust2")
        if a2:
            self.adjust2_label.setText(a2["label"])
            self.adjust2_spin.blockSignals(True)
            self.adjust2_spin.setSuffix(a2["suffix"])
            self.adjust2_spin.setRange(a2["min"], a2["max"])
            self.adjust2_spin.blockSignals(False)
        a3 = cfg.get("adjust3")
        if a3:
            self.adjust3_label.setText(a3["label"])
            self.adjust3_spin.blockSignals(True)
            self.adjust3_spin.setSuffix(a3["suffix"])
            self.adjust3_spin.setRange(a3["min"], a3["max"])
            self.adjust3_spin.blockSignals(False)

    def _set_dash_pattern_visible(self, visible: bool):
        """Show or hide the custom dash pattern controls."""
        self.dash_pattern_row.setVisible(visible)

    def _set_text_rows_visible(self, label: bool, tech: bool, note: bool):
        """Show or hide label/tech/note rows."""
        self.label_row.setVisible(label)
        self.tech_row.setVisible(tech)
        self.note_row.setVisible(note)

    def _set_color_rows_visible(self, pen: bool, fill: bool, text: bool):
        """Show or hide color picker rows."""
        self.pen_row.setVisible(pen)
        self.fill_row.setVisible(fill)
        self.text_row.setVisible(text)

    def _set_preview(self, lbl, color: QColor):
        """Update a color preview label and the matching color button foreground."""
        r, g, b, a = color.red(), color.green(), color.blue(), color.alpha()
        rgba_str = f"rgba({r}, {g}, {b}, {a / 255.0:.2f})"
        lbl.setStyleSheet(f"background-color: {rgba_str}; border: 1px solid #444;")
        lbl.update()
        # Mirror the color onto the corresponding button foreground
        if lbl is self.pen_color_preview:
            self._set_button_fg(self.pen_color_btn, color)
        elif lbl is self.fill_color_preview:
            self._set_button_fg(self.fill_color_btn, color)
        elif lbl is self.text_color_preview:
            self._set_button_fg(self.text_color_btn, color)

    def _set_button_fg(self, btn, color: QColor):
        """Set a button's background color and a contrasting text color."""
        from PyQt6.QtGui import QPalette
        r, g, b, a = color.red(), color.green(), color.blue(), color.alpha()
        af = a / 255.0
        # Blend with the parent's background to get the visible color
        parent = btn.parentWidget() or btn
        dock_bg = parent.palette().color(QPalette.ColorRole.Window)
        br, bg_g, bb = dock_bg.red(), dock_bg.green(), dock_bg.blue()
        vis_r = int(r * af + br * (1 - af))
        vis_g = int(g * af + bg_g * (1 - af))
        vis_b = int(b * af + bb * (1 - af))
        # Perceived luminance (ITU-R BT.601)
        lum = 0.299 * vis_r + 0.587 * vis_g + 0.114 * vis_b
        fg = "#000000" if lum > 140 else "#ffffff"
        bg = f"rgba({r}, {g}, {b}, {af:.2f})"
        name = btn.objectName()
        btn.setStyleSheet(
            f"#{name} {{ background-color: {bg}; color: {fg}; border: 1px solid #444; }}"
            f"#{name}:hover {{ border: 1px solid #888; }}"
        )

    def _set_color_widgets(self, which: str, color: QColor):
        """Update hex edit, opacity slider, alpha edit, and button for pen or fill.

        Args:
            which: "pen" or "fill"
            color: The QColor to display
        """
        r, g, b, a = color.red(), color.green(), color.blue(), color.alpha()
        hex_rgba = "#{:02X}{:02X}{:02X}{:02X}".format(r, g, b, a)
        alpha_hex = "{:02X}".format(a)
        if which == "pen":
            self.pen_hex_edit.setText(hex_rgba)
            self.pen_opacity.setValue(a)
            self.pen_alpha_edit.setText(alpha_hex)
            self._set_preview(self.pen_color_preview, color)
        elif which == "fill":
            self.fill_hex_edit.setText(hex_rgba)
            self.fill_opacity.setValue(a)
            self.fill_alpha_edit.setText(alpha_hex)
            self._set_preview(self.fill_color_preview, color)
        elif which == "text":
            self.text_hex_edit.setText(hex_rgba)
            self.text_opacity.setValue(a)
            self.text_alpha_edit.setText(alpha_hex)
            self._set_button_fg(self.text_color_btn, color)

    def _on_pen_opacity_changed(self, value: int):
        """Handle pen opacity slider change."""
        item = self._current_item
        if item is None or not hasattr(item, "pen_color"):
            return
        old_color = QColor(item.pen_color)
        item.pen_color.setAlpha(value)
        self.pen_alpha_edit.setText("{:02X}".format(value))
        r, g, b = item.pen_color.red(), item.pen_color.green(), item.pen_color.blue()
        self.pen_hex_edit.setText("#{:02X}{:02X}{:02X}{:02X}".format(r, g, b, value))
        self._set_preview(self.pen_color_preview, item.pen_color)
        if isinstance(item, MetaLineItem):
            item._apply_pen()
        elif hasattr(item, "_apply_pen_brush"):
            item._apply_pen_brush()
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

    def _on_fill_opacity_changed(self, value: int):
        """Handle fill opacity slider change."""
        item = self._current_item
        if item is None or not hasattr(item, "brush_color"):
            return
        item.brush_color.setAlpha(value)
        self.fill_alpha_edit.setText("{:02X}".format(value))
        r, g, b = item.brush_color.red(), item.brush_color.green(), item.brush_color.blue()
        self.fill_hex_edit.setText("#{:02X}{:02X}{:02X}{:02X}".format(r, g, b, value))
        self._set_preview(self.fill_color_preview, item.brush_color)
        if hasattr(item, "_apply_pen_brush"):
            item._apply_pen_brush()
        item.update()
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

    def _parse_alpha_hex(self, text: str) -> int:
        """Parse a hex alpha string, returning 0-255 or -1 on invalid input."""
        t = text.strip()
        if len(t) == 0:
            return -1
        try:
            v = int(t, 16)
            if 0 <= v <= 255:
                return v
        except ValueError:
            pass
        return -1

    def _on_pen_alpha_edited(self):
        """Handle pen alpha hex LineEdit editing finished."""
        item = self._current_item
        if item is None or not hasattr(item, "pen_color"):
            return
        v = self._parse_alpha_hex(self.pen_alpha_edit.text())
        if v < 0:
            # Revert to current alpha
            self.pen_alpha_edit.setText("{:02X}".format(item.pen_color.alpha()))
            return
        item.pen_color.setAlpha(v)
        self.pen_opacity.blockSignals(True)
        self.pen_opacity.setValue(v)
        self.pen_opacity.blockSignals(False)
        r, g, b = item.pen_color.red(), item.pen_color.green(), item.pen_color.blue()
        self.pen_hex_edit.setText("#{:02X}{:02X}{:02X}{:02X}".format(r, g, b, v))
        self.pen_alpha_edit.setText("{:02X}".format(v))
        self._set_preview(self.pen_color_preview, item.pen_color)
        if isinstance(item, MetaLineItem):
            item._apply_pen()
        elif hasattr(item, "_apply_pen_brush"):
            item._apply_pen_brush()
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

    def _on_fill_alpha_edited(self):
        """Handle fill alpha hex LineEdit editing finished."""
        item = self._current_item
        if item is None or not hasattr(item, "brush_color"):
            return
        v = self._parse_alpha_hex(self.fill_alpha_edit.text())
        if v < 0:
            # Revert to current alpha
            self.fill_alpha_edit.setText("{:02X}".format(item.brush_color.alpha()))
            return
        item.brush_color.setAlpha(v)
        self.fill_opacity.blockSignals(True)
        self.fill_opacity.setValue(v)
        self.fill_opacity.blockSignals(False)
        r, g, b = item.brush_color.red(), item.brush_color.green(), item.brush_color.blue()
        self.fill_hex_edit.setText("#{:02X}{:02X}{:02X}{:02X}".format(r, g, b, v))
        self.fill_alpha_edit.setText("{:02X}".format(v))
        self._set_preview(self.fill_color_preview, item.brush_color)
        if hasattr(item, "_apply_pen_brush"):
            item._apply_pen_brush()
        item.update()
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

    def _on_pen_hex_edited(self):
        """Handle pen hex color LineEdit editing finished (#RRGGBB or #RRGGBBAA)."""
        item = self._current_item
        if item is None or not hasattr(item, "pen_color"):
            return
        from utils import hex_to_qcolor
        c = hex_to_qcolor(self.pen_hex_edit.text().strip(), item.pen_color)
        if not c.isValid():
            self.pen_hex_edit.setText(
                "#{:02X}{:02X}{:02X}{:02X}".format(*[getattr(item.pen_color, ch)() for ch in ("red","green","blue","alpha")])
            )
            return
        item.pen_color = c
        self.pen_opacity.blockSignals(True)
        self.pen_opacity.setValue(c.alpha())
        self.pen_opacity.blockSignals(False)
        self.pen_alpha_edit.setText("{:02X}".format(c.alpha()))
        self.pen_hex_edit.setText("#{:02X}{:02X}{:02X}{:02X}".format(c.red(), c.green(), c.blue(), c.alpha()))
        self._set_preview(self.pen_color_preview, c)
        if isinstance(item, MetaLineItem):
            item._apply_pen()
        elif hasattr(item, "_apply_pen_brush"):
            item._apply_pen_brush()
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

    def _on_fill_hex_edited(self):
        """Handle fill hex color LineEdit editing finished (#RRGGBB or #RRGGBBAA)."""
        item = self._current_item
        if item is None or not hasattr(item, "brush_color"):
            return
        from utils import hex_to_qcolor
        c = hex_to_qcolor(self.fill_hex_edit.text().strip(), item.brush_color)
        if not c.isValid():
            self.fill_hex_edit.setText(
                "#{:02X}{:02X}{:02X}{:02X}".format(*[getattr(item.brush_color, ch)() for ch in ("red","green","blue","alpha")])
            )
            return
        item.brush_color = c
        self.fill_opacity.blockSignals(True)
        self.fill_opacity.setValue(c.alpha())
        self.fill_opacity.blockSignals(False)
        self.fill_alpha_edit.setText("{:02X}".format(c.alpha()))
        self.fill_hex_edit.setText("#{:02X}{:02X}{:02X}{:02X}".format(c.red(), c.green(), c.blue(), c.alpha()))
        self._set_preview(self.fill_color_preview, c)
        if hasattr(item, "_apply_pen_brush"):
            item._apply_pen_brush()
        item.update()
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

    def _on_text_opacity_changed(self, value: int):
        """Handle text opacity slider change."""
        item = self._current_item
        if item is None or not hasattr(item, "text_color"):
            return
        c = QColor(item.text_color)
        c.setAlpha(value)
        # Sync sibling widgets
        self.text_alpha_edit.blockSignals(True)
        self.text_alpha_edit.setText("{:02X}".format(value))
        self.text_alpha_edit.blockSignals(False)
        self.text_hex_edit.blockSignals(True)
        self.text_hex_edit.setText("#{:02X}{:02X}{:02X}{:02X}".format(
            c.red(), c.green(), c.blue(), value))
        self.text_hex_edit.blockSignals(False)
        self._apply_run_color(item, c)

    def _on_text_alpha_edited(self):
        """Handle text alpha hex LineEdit edit (2-char hex alpha)."""
        item = self._current_item
        if item is None or not hasattr(item, "text_color"):
            return
        a = self._parse_alpha_hex(self.text_alpha_edit.text().strip())
        if a < 0:
            self.text_alpha_edit.setText("{:02X}".format(item.text_color.alpha()))
            return
        c = QColor(item.text_color)
        c.setAlpha(a)
        self.text_opacity.blockSignals(True)
        self.text_opacity.setValue(a)
        self.text_opacity.blockSignals(False)
        self.text_hex_edit.blockSignals(True)
        self.text_hex_edit.setText("#{:02X}{:02X}{:02X}{:02X}".format(
            c.red(), c.green(), c.blue(), a))
        self.text_hex_edit.blockSignals(False)
        self._apply_run_color(item, c)

    def _on_text_hex_edited(self):
        """Handle text hex color LineEdit editing finished (#RRGGBB or #RRGGBBAA)."""
        from utils import hex_to_qcolor
        item = self._current_item
        if item is None or not hasattr(item, "text_color"):
            return
        c = hex_to_qcolor(self.text_hex_edit.text().strip(), item.text_color)
        if not c.isValid():
            self.text_hex_edit.setText(
                "#{:02X}{:02X}{:02X}{:02X}".format(
                    item.text_color.red(), item.text_color.green(),
                    item.text_color.blue(), item.text_color.alpha())
            )
            return
        self.text_opacity.blockSignals(True)
        self.text_opacity.setValue(c.alpha())
        self.text_opacity.blockSignals(False)
        self.text_alpha_edit.blockSignals(True)
        self.text_alpha_edit.setText("{:02X}".format(c.alpha()))
        self.text_alpha_edit.blockSignals(False)
        self._apply_run_color(item, c)

    def _set_meta_text_color(self, item, color_hex: str):
        """Write text color to both flat ``meta.color`` and nested ``default_format.color``."""
        if not hasattr(item, "meta"):
            return
        item.meta.color = color_hex
        if item.meta.default_format is None:
            item.meta.default_format = item.meta.effective_default_format()
        item.meta.default_format.color = color_hex

    def _safe_attr(self, obj, attr: str, default=None, context: str = ""):
        """Read an attribute, printing a console warning if missing."""
        if hasattr(obj, attr):
            return getattr(obj, attr)
        print(f"[PropPanel] MISMATCH: {context or type(obj).__name__} has no '{attr}' — using default {default!r}")
        return default

    def _block_format_signals(self, block: bool):
        """Block/unblock signals on run/block format widgets only.

        Used by ``_on_text_cursor_changed`` to update the format controls
        without triggering the format-change handlers that would apply the
        values back to the document.
        """
        for w in (self.text_halign_combo, self.spin_text_size, self.combo_font,
                  self.text_opacity, self.text_alpha_edit, self.text_hex_edit,
                  self.chk_bold, self.chk_italic, self.chk_underline,
                  self.chk_strikethrough,
                  self.spacing_type_combo, self.spin_spacing_value,
                  self.spin_space_before, self.spin_space_after):
            w.blockSignals(block)

    def _block_all_signals(self, block: bool):
        """Block/unblock signals on all editable widgets to prevent feedback."""
        from PyQt6.QtWidgets import QAbstractSpinBox, QComboBox as _QCB
        extra = [self.anchor_slider, self.spin_text_box_width, self.spin_text_box_height] if HAS_UI else []
        for w in (self.spin_x, self.spin_y, self.spin_w, self.spin_h,
                  self.spin_x1, self.spin_y1, self.spin_x2, self.spin_y2,
                  self.spin_z, self.adjust1_spin, self.adjust2_spin,
                  self.adjust3_spin, self.angle_spin,
                  self.line_width_spin, self.dash_length_spin,
                  self.dash_solid_spin, self.arrow_begin_spin,
                  self.arrow_end_spin, self.dash_combo, self.arrow_combo,
                  self.text_halign_combo, self.text_valign_combo,
                  self.spin_text_size, self.chk_wrap, self.text_contents,
                  self.spin_margin_left, self.spin_margin_right,
                  self.spin_margin_top, self.spin_margin_bottom,
                  self.flow_type_combo, self.spacing_type_combo,
                  self.spin_spacing_value, self.spin_space_before,
                  self.spin_space_after, self.edit_graphic_url,
                  self.spin_graphic_anchor, self.fill_opacity,
                  self.pen_opacity, self.text_opacity,
                  self.divider_count_spin, self.combo_font,
                  self.chk_bold, self.chk_italic, self.chk_underline,
                  self.chk_strikethrough, *extra):
            w.blockSignals(block)

    def _save_as_default(self):
        """Save current Format and Contents properties as per-kind user defaults.

        All values are read directly from the UI widgets so they always reflect
        what the user sees, regardless of whether the underlying model field was
        updated (e.g. font color / size / family are applied to runs but do not
        mutate meta.default_format until this button is clicked).

        Excludes text content and image_url.  Writes to
        ``[item_defaults.<kind>]`` in the user settings file via a targeted
        merge that leaves all other settings untouched, then writes the same
        values back to the live item so the JSON editor updates immediately.
        """
        from PyQt6.QtWidgets import QMessageBox as _QMessageBox
        from settings import get_settings

        item = self._current_item
        if item is None:
            return

        kind = getattr(item, "kind", "unknown")
        mgr = get_settings()

        # ── Merge / overwrite prompt ────────────────────────────────────
        if mgr.has_user_item_defaults(kind):
            reply = _QMessageBox.question(
                self,
                "Merge Item Defaults?",
                f"User defaults for '{kind}' already exist in:\n"
                f"{mgr.user_settings_file}\n\n"
                f"Merge (overwrite) the defaults for '{kind}'?",
                _QMessageBox.StandardButton.Yes | _QMessageBox.StandardButton.No,
                _QMessageBox.StandardButton.No,
            )
            if reply != _QMessageBox.StandardButton.Yes:
                return

        # ── Helper: map combo index → value list ───────────────────────
        def _combo_val(combo, values, fallback):
            idx = combo.currentIndex()
            return values[idx] if 0 <= idx < len(values) else fallback

        # ── Style: read entirely from widgets ──────────────────────────
        es = mgr.get_item_defaults(kind).style
        style_dict = {
            "pen_color":  self.pen_hex_edit.text().strip() or es.pen_color,
            "pen_width":  int(self.line_width_spin.value()),
            "line_dash":  _combo_val(self.dash_combo, ["solid", "dashed"], es.line_dash),
            "fill_color": self.fill_hex_edit.text().strip() or es.fill_color,
        }

        # ── Contents: read entirely from widgets ───────────────────────
        meta = getattr(item, "meta", None)
        ec = mgr.get_item_defaults(kind).contents

        halign    = _combo_val(self.text_halign_combo,
                               ["left", "center", "justified", "right"], ec.halign)
        valign    = _combo_val(self.text_valign_combo,
                               ["top", "middle", "bottom"], ec.valign)
        flow_type = _combo_val(self.flow_type_combo,
                               ["none", "horizontal", "vertical", "none"], ec.flow_type)
        font_family  = self.combo_font.currentFont().family()
        font_size    = int(self.spin_text_size.value())
        color        = self.text_hex_edit.text().strip() or ec.color
        margin_left  = float(self.spin_margin_left.value())
        margin_right = float(self.spin_margin_right.value())
        margin_top   = float(self.spin_margin_top.value())
        margin_bottom= float(self.spin_margin_bottom.value())
        wrap         = self.chk_wrap.isChecked()
        image_anchor = int(self.spin_graphic_anchor.value())
        # No active UI widgets for spacing / text_box_width / text_box_height;
        # fall back to meta if available, else existing defaults.
        spacing         = float(getattr(meta, "spacing",         ec.spacing))
        text_box_width  = float(getattr(meta, "text_box_width",  ec.text_box_width))
        text_box_height = float(getattr(meta, "text_box_height", ec.text_box_height))

        contents_dict: dict = {
            "halign":          halign,
            "valign":          valign,
            "spacing":         spacing,
            "color":           color,
            "font_family":     font_family,
            "font_size":       font_size,
            "margin_left":     margin_left,
            "margin_right":    margin_right,
            "margin_top":      margin_top,
            "margin_bottom":   margin_bottom,
            "wrap":            wrap,
            "flow_type":       flow_type,
            "text_box_width":  text_box_width,
            "text_box_height": text_box_height,
            "image_anchor":    image_anchor,
            # image_url intentionally excluded
        }

        # ── overlay-2.0 default_format ─────────────────────────────────
        # font_family / font_size / color come from widgets (authoritative).
        # bold/italic/underline/etc. have no dedicated panel controls — keep
        # whatever the item's current default_format already stores; they are
        # only changed via inline text-editor formatting.
        existing_cf = (
            meta.default_format
            if (meta is not None and meta.default_format is not None)
            else CharFormat()
        )
        df = existing_cf.to_dict()      # full (non-sparse) — preserves b/i/u/etc.
        df["font_family"] = font_family
        df["font_size"]   = font_size
        df["color"]       = color
        contents_dict["default_format"] = df

        # ── overlay-2.0 frame ──────────────────────────────────────────
        contents_dict["frame"] = {
            "halign":        halign,
            "valign":        valign,
            "margin_left":   margin_left,
            "margin_right":  margin_right,
            "margin_top":    margin_top,
            "margin_bottom": margin_bottom,
        }

        # ── Write back to the live item so the JSON editor updates ─────
        # Update BOTH meta.* fields AND the item-level rendering attributes.
        # set_item() reloads the panel by reading item.pen_color / text_color /
        # etc. (not meta.*), so those must be in sync or the UI will revert.
        from utils import hex_to_qcolor as _hq
        from PyQt6.QtGui import QColor as _QColor

        if meta is not None:
            meta.color       = color
            meta.halign      = halign
            meta.valign      = valign
            meta.font_family = font_family
            meta.font_size   = font_size
            meta.margin_left   = margin_left
            meta.margin_right  = margin_right
            meta.margin_top    = margin_top
            meta.margin_bottom = margin_bottom
            meta.wrap        = wrap
            meta.flow_type   = flow_type
            meta.image_anchor = image_anchor
            new_default_fmt = CharFormat.from_dict(df)
            meta.default_format = new_default_fmt
            meta.frame          = TextFrame.from_dict(contents_dict["frame"])

            # Renormalize blocks by re-extracting from the live QTextDocument.
            # _qtextdoc_to_blocks compares each run's actual character format
            # against new_default_fmt and emits only the fields that differ,
            # so overrides are correctly sparse relative to the new default.
            if meta.blocks is not None:
                from models import TextBlock as _TB
                new_blocks_raw = _qtextdoc_to_blocks(
                    self.text_contents.document(), new_default_fmt
                )
                meta.blocks = [_TB.from_dict(b) for b in new_blocks_raw]

        # Style rendering attributes (read by set_item via item.pen_color etc.)
        _transparent = _QColor(0, 0, 0, 0)
        _red         = _QColor(Qt.GlobalColor.red)
        _yellow      = _QColor(Qt.GlobalColor.yellow)
        if hasattr(item, "pen_color"):
            item.pen_color = _hq(style_dict["pen_color"], _red)
        if hasattr(item, "pen_width"):
            item.pen_width = style_dict["pen_width"]
        if hasattr(item, "line_dash"):
            item.line_dash = style_dict["line_dash"]
        if hasattr(item, "brush_color"):
            item.brush_color = _hq(style_dict["fill_color"], _transparent)
        if hasattr(item, "_apply_pen_brush"):
            item._apply_pen_brush()
        elif hasattr(item, "_apply_pen"):
            item._apply_pen()

        # Contents rendering attributes (read by set_item via item.text_color etc.)
        _color_qc = _hq(color, _yellow)
        if hasattr(item, "text_color"):
            item.text_color = _color_qc
        if hasattr(item, "text_size_pt"):
            item.text_size_pt = font_size

        if hasattr(item, "_update_label_text"):
            item._update_label_text()
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

        # ── Persist (targeted merge into user settings file) ───────────
        mgr.save_user_item_defaults(kind, style_dict, contents_dict)

        _QMessageBox.information(
            self,
            "Saved",
            f"Default settings for '{kind}' saved to:\n{mgr.user_settings_file}",
        )

    def set_active_domain(self, domain_name: str):
        """Update the DSL label (and item ann_dsl) when the domain menu changes.

        Args:
            domain_name: The selected domain name, or "" for Generic (no domain).
        """
        item = self._current_item
        if item is None or not hasattr(item, "ann_dsl"):
            return
        if domain_name:
            # Stamp domain key — preserve existing sub-keys from this domain
            existing = item.ann_dsl.get(domain_name, {})
            item.ann_dsl = {domain_name: existing}
        else:
            item.ann_dsl = {}
        self.dsl_label.setText(_format_dsl_label(item.ann_dsl))
        # Propagate change to JSON editor
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

    def set_item(self, item: Optional[QGraphicsItem]):
        """Set the item to display/edit in the property panel."""
        # Suppress _on_text_cursor_changed during population — setting
        # HTML/text on the QTextEdit fires deferred cursor signals that
        # would overwrite the freshly-set color widgets with a wrong value
        # read from Qt's CSS-rendered charFormat.
        self._suppress_cursor_sync = True
        is_new_item = item is not self._current_item
        # Clear the authoritative flag when the selected item changes
        if is_new_item:
            self._text_contents_is_authoritative = False
        self._current_item = item
        if item is None or not hasattr(item, "meta"):
            self._text_contents_is_authoritative = False
            self.kind_label.setText("-")
            self.dsl_label.setText("Generic")
            self.edit_id.setText("")
            self.text_contents.setPlainText("")
            self._set_enabled(False)
            if HAS_UI and hasattr(self, "_save_default_btn"):
                self._save_default_btn.setVisible(False)
            self._suppress_cursor_sync = False
            return

        if HAS_UI and hasattr(self, "_save_default_btn"):
            self._save_default_btn.setVisible(True)

        # Switch to Style tab only when the selected item changes, not on refresh
        if is_new_item:
            self.tabs.setCurrentIndex(0)
        self._block_all_signals(True)

        meta: AnnotationContents = getattr(item, "meta")
        kind = getattr(item, "kind", "")

        # ── geom frame visibility (xywh vs xy12) ────────────────────
        is_line_like = kind in ("line",)
        if HAS_UI:
            self.frame_xywh.setVisible(not is_line_like)
            self.frame_xy12.setVisible(is_line_like)

        # ── annotationItem top-level ─────────────────────────────────
        self.edit_id.setText(getattr(item, "ann_id", ""))
        self.kind_label.setText(kind)
        _dsl_dict = getattr(item, "ann_dsl", {})
        self.dsl_label.setText(_format_dsl_label(_dsl_dict))
        self.spin_z.setValue(int(item.zValue()))
        self.edit_parent_id.setText(getattr(item, "parent_id", ""))

        # ── geom (rect shapes) ──────────────────────────────────────
        pos = item.pos()
        self.spin_x.setValue(pos.x())
        self.spin_y.setValue(pos.y())
        if hasattr(item, "_width"):
            self.spin_w.setValue(item._width)
            self.spin_h.setValue(item._height)

        # ── geom (line shapes: x1,y1,x2,y2) ─────────────────────────
        if hasattr(item, "line"):
            ln = item.line()
            self.spin_x1.setValue(ln.x1() + pos.x())
            self.spin_y1.setValue(ln.y1() + pos.y())
            self.spin_x2.setValue(ln.x2() + pos.x())
            self.spin_y2.setValue(ln.y2() + pos.y())

        # ── geom adjusts ────────────────────────────────────────────
        if hasattr(item, "_adjust1"):
            self.adjust1_spin.setValue(float(item._adjust1))
        if hasattr(item, "_adjust2"):
            self.adjust2_spin.setValue(float(item._adjust2))
        if hasattr(item, "_adjust3"):
            self.adjust3_spin.setValue(float(item._adjust3))

        # ── geom angle ──────────────────────────────────────────────
        self.angle_spin.setValue(item.rotation() % 360)

        # ── style.pen ───────────────────────────────────────────────
        pen_color = getattr(item, "pen_color", QColor("red"))
        self._set_color_widgets("pen", pen_color)
        self.line_width_spin.setValue(float(getattr(item, "pen_width", 2)))

        dash_style = getattr(item, "line_dash", "solid")
        dash_map = {"solid": 0, "dashed": 1}
        self.dash_combo.setCurrentIndex(dash_map.get(dash_style, 0))
        self.dash_length_spin.setValue(float(getattr(item, "dash_pattern_length", 30)))
        self.dash_solid_spin.setValue(int(getattr(item, "dash_solid_percent", 50)))

        # ── style.fill ──────────────────────────────────────────────
        fill_color = getattr(item, "brush_color", QColor(0, 0, 0, 0))
        self._set_color_widgets("fill", fill_color)

        # ── style arrow ─────────────────────────────────────────────
        arrow_mode = getattr(item, "arrow_mode", "none")
        arrow_map = {"none": 0, "start": 1, "end": 2, "both": 3}
        self.arrow_combo.setCurrentIndex(arrow_map.get(arrow_mode, 0))
        arrow_size = getattr(item, "arrow_size", 12.0)
        self.arrow_begin_spin.setValue(arrow_size)
        self.arrow_end_spin.setValue(arrow_size)

        # ── text color ──────────────────────────────────────────────
        if not self._text_contents_is_authoritative:
            text_color = getattr(item, "text_color", pen_color)
            self._set_color_widgets("text", text_color)

        # ── contents — resolve effective frame and default_format ─────
        _eff_frame = meta.effective_frame()
        _eff_fmt = meta.effective_default_format()

        font_family = _eff_fmt.font_family
        font_size = max(6, int(_eff_fmt.font_size or 12))
        halign = _eff_frame.halign
        valign = _eff_frame.valign

        from PyQt6.QtGui import QFont as _QFont, QTextCharFormat as _TCF
        from models import hex_to_css_color
        from utils import hex_to_qcolor

        _te_fnt = _QFont(font_family) if font_family else _QFont()
        _te_fnt.setPointSize(font_size)
        self.text_contents.document().setDefaultFont(_te_fnt)

        # Apply default text color as document CSS so that runs without an
        # explicit color render in the item's configured default color.
        # Must be set BEFORE setHtml() so Qt picks it up when building the doc.
        _def_color_hex = _eff_fmt.color or getattr(meta, "color", "")
        if _def_color_hex:
            _css_col = hex_to_css_color(_def_color_hex)
            self.text_contents.document().setDefaultStyleSheet(
                f"body, p {{ color: {_css_col}; }}"
            )

        # Capture whether this is a brand-new item that needs one-time format
        # initialization (default_format absent).  Must be captured BEFORE the
        # stamping block below sets meta.default_format, because the deferred
        # _init_text_format_sync check at the end of set_item() needs to
        # distinguish "truly new item" from "existing item re-selected".
        _needs_format_init = (
            is_new_item
            and meta.default_format is None
            and not getattr(meta, "text", "").strip()
        )

        # For newly created items snapshot default_format and frame immediately
        # so they appear in the JSON editor right away.
        # Triggers when default_format is None and no legacy flat text is set
        # — covers both new shapes (blocks=None) and new text items (blocks set
        # in __init__ but default_format not yet resolved from UI settings).
        # Uses the actual resolved font family from the QFont we just installed
        # (empty font_family → OS default → e.g. "Segoe UI").
        if _needs_format_init:
            _actual_family = _te_fnt.family()
            meta.default_format = CharFormat(
                font_family=_actual_family if _actual_family else font_family,
                font_size=font_size,
                color=getattr(meta, "color", "") or "",
            )
            if meta.frame is None:
                meta.frame = _eff_frame
            if meta.blocks is None:
                meta.blocks = []
            if hasattr(item, "_notify_changed"):
                item._notify_changed()

        if not self.text_contents.hasFocus() and not self._text_contents_is_authoritative:
            # Block signals to prevent _on_text_contents_changed from
            # overwriting meta.blocks with the lossy HTML→QTextDoc round-trip.
            # The QTextEdit is a DISPLAY of blocks here, not the source of truth.
            self.text_contents.blockSignals(True)
            try:
                if meta.blocks is not None:
                    html = _blocks_to_html(meta.blocks, _eff_fmt, halign)
                    if html:
                        self.text_contents.setHtml(html)
                    else:
                        self.text_contents.clear()
                else:
                    text = getattr(meta, "text", "")
                    if text:
                        self.text_contents.setHtml(text)
                    else:
                        self.text_contents.clear()
            finally:
                self.text_contents.blockSignals(False)

        if self._text_contents_is_authoritative:
            # The QTextEdit owns the state — do NOT touch format controls.
            # They were set by the format handler (color picker, bold, etc.)
            # or by _on_text_cursor_changed when the user moves the cursor.
            pass
        else:
            halign_map = {"left": 0, "center": 1, "justified": 2, "right": 3}
            valign_map = {"top": 0, "middle": 1, "bottom": 2}
            self.text_halign_combo.setCurrentIndex(halign_map.get(halign, 1))
            self.text_valign_combo.setCurrentIndex(valign_map.get(valign, 0))
            self._apply_align_to_textedit(halign)
            self._apply_default_spacing_to_textedit(_eff_fmt)

            self.spin_text_size.setValue(font_size)
            _actual_family = _te_fnt.family()
            if _actual_family:
                self.combo_font.setCurrentFont(_QFont(_actual_family))

            # Set the typing-format so new characters inherit the item's defaults
            _tf = _TCF()
            if _actual_family:
                _tf.setFontFamilies([_actual_family])
            _tf.setFontPointSize(float(font_size))
            if _def_color_hex:
                _tc = hex_to_qcolor(_def_color_hex, QColor())
                if _tc.isValid():
                    _tf.setForeground(_tc)
            self.text_contents.setCurrentCharFormat(_tf)

        self.chk_wrap.setChecked(getattr(meta, "wrap", True))

        self.spin_margin_left.setValue(int(_eff_frame.margin_left))
        self.spin_margin_right.setValue(int(_eff_frame.margin_right))
        self.spin_margin_top.setValue(int(_eff_frame.margin_top))
        self.spin_margin_bottom.setValue(int(_eff_frame.margin_bottom))

        # ── contents.color → text color (already set via item.text_color above)

        # ── contents.flow_type ──────────────────────────────────────
        flow_type = getattr(meta, "flow_type", "none")
        flow_map = {"none": 0, "horizontal": 1, "vertical": 2}
        self.flow_type_combo.setCurrentIndex(flow_map.get(flow_type, 0))

        # ── line height + paragraph spacing ─────────────────────────
        # Skip when authoritative (user is actively editing spacing via
        # the controls — don't overwrite their values from meta).
        if not self._text_contents_is_authoritative:
            _lh_type = "single"
            _lh_value = 0.0
            if meta.blocks and meta.blocks[0].spacing_type:
                _lh_type = meta.blocks[0].spacing_type
                _lh_value = meta.blocks[0].spacing_value
            elif _eff_fmt.spacing_type and _eff_fmt.spacing_type != "single":
                _lh_type = _eff_fmt.spacing_type
                _lh_value = _eff_fmt.spacing_value
            _lh_type_map = {"single": 0, "proportional": 1, "fixed": 2,
                            "minimum": 3, "line_distance": 4}
            _lh_idx = _lh_type_map.get(_lh_type, 0)
            self.spacing_type_combo.setCurrentIndex(_lh_idx)
            is_single = (_lh_idx == 0)
            is_proportional = (_lh_idx == 1)
            self.spin_spacing_value.setEnabled(not is_single)
            self.spin_spacing_value.setSuffix(" %" if is_proportional else " pt")
            if is_proportional:
                self.spin_spacing_value.setRange(25, 500)
            else:
                self.spin_spacing_value.setRange(1, 200)
            if is_single:
                doc_font = self.text_contents.document().defaultFont()
                pt = doc_font.pointSize()
                self.spin_spacing_value.setValue(max(6, pt if pt > 0 else 12))
            elif _lh_value > 0:
                self.spin_spacing_value.setValue(int(_lh_value))
            elif is_proportional:
                self.spin_spacing_value.setValue(100)

            # ── space_before / space_after (paragraph spacing) ──────
            _sb = 0.0
            _sa = 0.0
            if meta.blocks:
                _sb = getattr(meta.blocks[0], "space_before", 0.0)
                _sa = getattr(meta.blocks[0], "space_after", 0.0)
            self.spin_space_before.setValue(int(_sb))
            self.spin_space_after.setValue(int(_sa))

        # ── contents.image_url / image_anchor ───────────────────────
        self.edit_graphic_url.setText(getattr(meta, "image_url", ""))
        self.spin_graphic_anchor.setValue(int(getattr(meta, "image_anchor", 0)))

        # spacing / text_box_width / text_box_height: no UI widget yet (deferred)

        # ── label / tech / note convenience edits ──────────────────────
        self.label_edit.setText(meta.label)
        self.tech_edit.setText(meta.tech)
        self.note_edit.setText(meta.note)

        self._block_all_signals(False)

        # ── ports list ───────────────────────────────────────────────
        if HAS_UI:
            self.list_ports.blockSignals(True)
            self.list_ports.clear()
            port_ids = getattr(item, "ports", [])
            for pid in port_ids:
                self.list_ports.addItem(pid)
            self.group_ports.setVisible(bool(port_ids))
            if port_ids:
                row_h = self.list_ports.sizeHintForRow(0)
                frame = self.list_ports.frameWidth() * 2
                self.list_ports.setFixedHeight(row_h * len(port_ids) + frame)
            self.list_ports.blockSignals(False)

        self._set_enabled(True)

        # ── Kind-specific control setup (visibility, dash pattern etc) ──
        # Hide anchor/text-box controls by default; line/curve _setup methods show them
        if HAS_UI:
            self.anchor_frame.setVisible(False)
            self.anchor_pt_group.setVisible(False)
        pen_color = getattr(item, "pen_color", QColor("red"))

        if kind == "rect":
            self._setup_rect_controls(item, pen_color)
        elif kind == "ellipse":
            self._setup_ellipse_controls(item, pen_color)
        elif kind == "roundedrect":
            self._setup_roundedrect_controls(item, pen_color)
        elif kind == "line":
            self._setup_line_controls(item, pen_color)
        elif kind == "text":
            self._setup_text_controls(item, pen_color)
        elif kind == "hexagon":
            self._setup_hexagon_controls(item, pen_color)
        elif kind == "cylinder":
            self._setup_cylinder_controls(item, pen_color)
        elif kind == "blockarrow":
            self._setup_blockarrow_controls(item, pen_color)
        elif kind == "isocube":
            self._setup_isocube_controls(item, pen_color)
        elif kind == "polygon":
            self._setup_polygon_controls(item, pen_color)
        elif kind == "curve":
            self._setup_curve_controls(item, pen_color)
        elif kind == "orthocurve":
            self._setup_curve_controls(item, pen_color)
        elif kind == "seqblock":
            self._setup_seqblock_controls(item, pen_color)
        elif kind == "group":
            self._setup_group_controls(item, pen_color)
        else:
            pass
        # Clear the suppress flag after deferred Qt signals have been processed.
        # QTimer.singleShot(0) runs after the current event batch completes,
        # so cursor signals queued by setHtml/setTextCursor during set_item
        # are still blocked.
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, self._clear_suppress_cursor_sync)

        # One-time initialization sync for NEWLY CREATED MetaTextItems only
        # (_needs_format_init = default_format was absent when set_item() entered).
        # After the QTextEdit is fully laid out, read back the OS-resolved font
        # family/size and push to meta.default_format + re-render the canvas item.
        # NOT triggered for existing items re-selected from the JSON editor —
        # those already have default_format set and must not have their cursor
        # position disrupted by the _notify_changed() call here.
        if _needs_format_init and isinstance(item, MetaTextItem) and hasattr(item, "_render_from_meta"):
            _item_ref = item

            def _init_text_format_sync():
                if self._current_item is not _item_ref:
                    return
                doc = self.text_contents.document()
                doc_font = doc.defaultFont()
                fam = doc_font.family()
                pt = doc_font.pointSize()
                meta = _item_ref.meta
                # Rebuild default_format from the fully resolved document state
                # so font family is the actual OS-resolved name (not empty string).
                meta.default_format = CharFormat(
                    font_family=fam if fam else getattr(meta, "font_family", ""),
                    font_size=pt if pt > 0 else max(6, getattr(meta, "font_size", 12)),
                    color=(meta.default_format.color if meta.default_format else "")
                          or getattr(meta, "color", "") or "",
                )
                _item_ref._render_from_meta()
                if hasattr(_item_ref, "_notify_changed"):
                    _item_ref._notify_changed()

            QTimer.singleShot(0, _init_text_format_sync)

    def _clear_suppress_cursor_sync(self):
        self._suppress_cursor_sync = False

    def _setup_rect_controls(self, item, pen_color):
        """Configure controls for rect items."""
        self._set_preview(self.pen_color_preview, pen_color)
        self._set_preview(self.fill_color_preview, getattr(item, "brush_color", QColor(0, 0, 0, 0)))
        self._set_preview(self.text_color_preview, getattr(item, "text_color", pen_color))
        self._setup_line_style_controls(item)
        self._setup_text_layout_controls(item)

    def _setup_ellipse_controls(self, item, pen_color):
        """Configure controls for ellipse items."""
        self._set_preview(self.pen_color_preview, pen_color)
        self._set_preview(self.fill_color_preview, getattr(item, "brush_color", QColor(0, 0, 0, 0)))
        self._set_preview(self.text_color_preview, getattr(item, "text_color", pen_color))
        self._setup_line_style_controls(item)
        self._setup_text_layout_controls(item)

    def _setup_roundedrect_controls(self, item, pen_color):
        """Configure controls for rounded rect items."""
        self._set_preview(self.pen_color_preview, pen_color)
        self._set_preview(self.fill_color_preview, getattr(item, "brush_color", QColor(0, 0, 0, 0)))
        self._set_preview(self.text_color_preview, getattr(item, "text_color", pen_color))
        self._configure_adjust_controls("roundedrect")
        self.adjust1_spin.blockSignals(True)
        self.adjust1_spin.setValue(int(getattr(item, "_adjust1", 10)))
        self.adjust1_spin.blockSignals(False)
        self._setup_line_style_controls(item)
        self._setup_text_layout_controls(item)

    def _setup_line_controls(self, item, pen_color):
        """Configure controls for line items."""
        self._set_preview(self.pen_color_preview, pen_color)
        self._set_preview(self.text_color_preview, getattr(item, "text_color", pen_color))
        self._setup_line_style_controls(item)
        self._setup_text_layout_controls(item)
        self._setup_anchor_controls(item)
        self._setup_text_box_dims(item)
        self._setup_text_box_appearance(item)

        # Arrow mode
        arrow_mode = getattr(item, "arrow_mode", "none")
        arrow_map = {"none": 0, "start": 1, "end": 2, "both": 3}
        self.arrow_combo.blockSignals(True)
        self.arrow_combo.setCurrentIndex(arrow_map.get(arrow_mode, 0))
        self.arrow_combo.blockSignals(False)

        # Arrow size
        arrow_size = getattr(item, "arrow_size", 12.0)
        self.arrow_size_spin.blockSignals(True)
        self.arrow_size_spin.setValue(int(arrow_size))
        self.arrow_size_spin.blockSignals(False)

        # Text box width
        text_box_width = getattr(item.meta, "text_box_width", 0.0) if hasattr(item, "meta") else 0.0
        self.text_box_width_spin.blockSignals(True)
        self.text_box_width_spin.setValue(int(text_box_width))
        self.text_box_width_spin.blockSignals(False)

    def _setup_text_controls(self, item, pen_color):
        """Configure controls for text items (same contents tab flow as shapes)."""
        if not self._text_contents_is_authoritative:
            self._set_preview(self.text_color_preview, getattr(item, "text_color", pen_color))
        self._setup_text_layout_controls(item)

    def _setup_line_style_controls(self, item):
        """Configure line width and dash style controls."""
        self.line_width_spin.blockSignals(True)
        self.line_width_spin.setValue(int(getattr(item, "pen_width", 2)))
        self.line_width_spin.blockSignals(False)

        dash_style = getattr(item, "line_dash", "solid")
        dash_map = {"solid": 0, "dashed": 1}
        self.dash_combo.blockSignals(True)
        self.dash_combo.setCurrentIndex(dash_map.get(dash_style, 0))
        self.dash_combo.blockSignals(False)

        self.dash_length_spin.blockSignals(True)
        self.dash_length_spin.setValue(int(getattr(item, "dash_pattern_length", 30)))
        self.dash_length_spin.blockSignals(False)
        self.dash_solid_spin.blockSignals(True)
        self.dash_solid_spin.setValue(int(getattr(item, "dash_solid_percent", 50)))
        self.dash_solid_spin.blockSignals(False)

    def _setup_text_layout_controls(self, item):
        """Configure text spacing and vertical alignment controls."""
        if not hasattr(item, "meta"):
            return

        meta = item.meta
        # Text spacing — new field "spacing", fallback to "text_spacing"
        spacing = self._safe_attr(meta, "spacing", None, "meta.spacing")
        if spacing is None:
            spacing = self._safe_attr(meta, "text_spacing", 0.0, "meta.text_spacing")
        spacing_map = {0.0: 0, 0.5: 1, 1.0: 2, 1.5: 3, 2.0: 4}
        spacing_index = spacing_map.get(float(spacing), 0)
        self.text_spacing_combo.blockSignals(True)
        self.text_spacing_combo.setCurrentIndex(spacing_index)
        self.text_spacing_combo.blockSignals(False)

        # Vertical alignment — new field "valign", fallback to "text_valign"
        valign = self._safe_attr(meta, "valign", None, "meta.valign")
        if valign is None:
            valign = self._safe_attr(meta, "text_valign", "top", "meta.text_valign")
        valign_map = {"top": 0, "middle": 1, "bottom": 2}
        valign_index = valign_map.get(valign, 0)
        self.text_valign_combo.blockSignals(True)
        self.text_valign_combo.setCurrentIndex(valign_index)
        self.text_valign_combo.blockSignals(False)

    def _setup_text_box_dims(self, item):
        """Populate text box width/height spinboxes for line/curve items."""
        if not HAS_UI:
            return
        meta = getattr(item, "meta", None)
        if meta is None:
            return
        self.spin_text_box_width.blockSignals(True)
        self.spin_text_box_width.setValue(int(getattr(meta, "text_box_width", 0)))
        self.spin_text_box_width.blockSignals(False)
        self.spin_text_box_height.blockSignals(True)
        self.spin_text_box_height.setValue(int(getattr(meta, "text_box_height", 0)))
        self.spin_text_box_height.blockSignals(False)

    def _on_text_box_dims_changed(self, _value: int):
        """Handle text box width or height spinbox change."""
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        item.meta.text_box_width = float(self.spin_text_box_width.value())
        item.meta.text_box_height = float(self.spin_text_box_height.value())
        item.prepareGeometryChange()
        if hasattr(item, "_update_label_position"):
            item._update_label_position()
        item.update()
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

    def _setup_text_box_appearance(self, item):
        """Configure text box background/border controls for line/curve items."""
        if not HAS_UI:
            return
        meta = getattr(item, "meta", None)
        if meta is None:
            return

        # Border checkbox
        self.chk_border.blockSignals(True)
        self.chk_border.setChecked(getattr(meta, "text_box_border", True))
        self.chk_border.blockSignals(False)

        # Border color button
        from utils import hex_to_qcolor
        border_hex = getattr(meta, "text_box_border_color", "")
        border_c = hex_to_qcolor(border_hex, QColor(200, 200, 200)) if border_hex else QColor(200, 200, 200)
        self._set_button_fg(self.btn_border_color, border_c)

        # Background color button
        bg_hex = getattr(meta, "text_box_background_color", "")
        bg_c = hex_to_qcolor(bg_hex, QColor(255, 255, 255)) if bg_hex else QColor(255, 255, 255)
        self._set_button_fg(self.btn_background_color, bg_c)

    def _pick_text_box_background_color(self):
        """Pick text box background fill color."""
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        from utils import hex_to_qcolor, qcolor_to_hex
        cur_hex = getattr(item.meta, "text_box_background_color", "")
        old_c = hex_to_qcolor(cur_hex, QColor(255, 255, 255)) if cur_hex else QColor(255, 255, 255)
        c = self._pick_color(old_c, "Pick Text Box Background")
        if c is None:
            return
        item.meta.text_box_background_color = qcolor_to_hex(c, include_alpha=True)
        self._set_button_fg(self.btn_background_color, c)
        item.update()
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

    def _pick_text_box_border_color(self):
        """Pick text box border stroke color."""
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        from utils import hex_to_qcolor, qcolor_to_hex
        cur_hex = getattr(item.meta, "text_box_border_color", "")
        old_c = hex_to_qcolor(cur_hex, QColor(200, 200, 200)) if cur_hex else QColor(200, 200, 200)
        c = self._pick_color(old_c, "Pick Text Box Border Color")
        if c is None:
            return
        item.meta.text_box_border_color = qcolor_to_hex(c, include_alpha=True)
        self._set_button_fg(self.btn_border_color, c)
        item.update()
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

    def _on_anchor_point_changed(self, h_anchor: str, v_anchor: str):
        """Handle anchor point grid selection change."""
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        item.meta.text_anchor = h_anchor
        item.meta.text_anchor_v = v_anchor
        if hasattr(item, "_update_label_position"):
            item.prepareGeometryChange()
            item._update_label_position()
            item.update()
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

    def _on_text_box_border_toggled(self, checked: bool):
        """Handle text box border checkbox toggle."""
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        item.meta.text_box_border = checked
        item.update()
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

    def _setup_anchor_controls(self, item):
        """Configure anchor slider/edit and anchor point grid for line/curve items."""
        if not HAS_UI:
            return
        self.anchor_frame.setVisible(True)
        anchor_val = 50
        if hasattr(item, "meta"):
            anchor_val = int(getattr(item.meta, "anchor_value", 50.0))
        self.anchor_slider.blockSignals(True)
        self.anchor_slider.setValue(anchor_val)
        self.anchor_slider.blockSignals(False)
        self.anchor_value_edit.setText(str(anchor_val))

        # Anchor point grid (3x3)
        self.anchor_pt_group.setVisible(True)
        if hasattr(item, "meta"):
            h_a = getattr(item.meta, "text_anchor", "center")
            v_a = getattr(item.meta, "text_anchor_v", "middle")
            self.anchor_pt_widget.set_anchor(h_a, v_a)

    def _on_anchor_slider_changed(self, value: int):
        """Handle anchor slider value change."""
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        self.anchor_value_edit.setText(str(value))
        item.meta.anchor_value = float(value)
        if hasattr(item, "_update_label_position"):
            item.prepareGeometryChange()
            item._update_label_position()
            item.update()
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

    def _on_anchor_edit_finished(self):
        """Handle anchor value line-edit editing finished."""
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        try:
            val = int(self.anchor_value_edit.text())
        except ValueError:
            val = 50
        val = max(0, min(100, val))
        self.anchor_value_edit.setText(str(val))
        self.anchor_slider.blockSignals(True)
        self.anchor_slider.setValue(val)
        self.anchor_slider.blockSignals(False)
        item.meta.anchor_value = float(val)
        if hasattr(item, "_update_label_position"):
            item.prepareGeometryChange()
            item._update_label_position()
            item.update()
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

    def _block_text_signals(self, block: bool):
        """Block or unblock signals from text formatting controls."""
        self.label_align.blockSignals(block)
        self.label_size.blockSignals(block)
        self.tech_align.blockSignals(block)
        self.tech_size.blockSignals(block)
        self.note_align.blockSignals(block)
        self.note_size.blockSignals(block)

    def _apply_changes(self):
        """Apply changes from the form to the current item.

        Uses new AnnotationContents fields (text, halign, valign, font_size,
        spacing) when available, with fallback reads for old attributes.
        Also syncs label/tech/note edits via property setters.
        """
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        meta: AnnotationContents = getattr(item, "meta")

        # Capture old values for undo
        contents_fields = ["text", "halign", "valign", "font_size", "spacing"]
        old_meta = {}
        for f in contents_fields:
            old_meta[f] = getattr(meta, f, None)
        old_meta["label"] = meta.label
        old_meta["tech"] = meta.tech
        old_meta["note"] = meta.note

        # -- Write label/tech/note from the convenience edits --
        new_label = self.label_edit.text()
        new_tech = self.tech_edit.text()
        new_note = self.note_edit.text()
        if new_label != meta.label:
            meta.label = new_label
        if new_tech != meta.tech:
            meta.tech = new_tech
        if new_note != meta.note:
            meta.note = new_note

        # -- Write contents fields from the Contents tab UI --
        if HAS_UI:
            halign_values = ["left", "center", "justified", "right"]
            meta.halign = halign_values[self.text_halign_combo.currentIndex()]
            valign_values = ["top", "middle", "bottom"]
            meta.valign = valign_values[self.text_valign_combo.currentIndex()]
            meta.font_size = self.spin_text_size.value()
            meta.wrap = self.chk_wrap.isChecked()
            # Sync text_contents QTextEdit → meta.text only if labels
            # didn't change (label/tech/note setters already update text)
            if (new_label == old_meta["label"] and new_tech == old_meta["tech"]
                    and new_note == old_meta["note"]):
                meta.text = self.text_contents.toHtml()

        new_meta = {}
        for f in contents_fields:
            new_meta[f] = getattr(meta, f, None)
        new_meta["label"] = meta.label
        new_meta["tech"] = meta.tech
        new_meta["note"] = meta.note

        # Skip if nothing changed
        if old_meta == new_meta:
            return

        setattr(item, "meta", meta)

        if isinstance(item, MetaTextItem):
            text_val = meta.note
            if not getattr(item, '_editing', False) and item.toPlainText() != text_val:
                item.setPlainText(text_val)

        if hasattr(item, "_update_label_text"):
            item._update_label_text()

        if hasattr(item, "_notify_changed"):
            item._notify_changed()

        # Sync text_contents QTextEdit with updated blocks (block signals
        # to avoid feedback loop)
        if HAS_UI and (new_label != old_meta["label"] or new_tech != old_meta["tech"]
                       or new_note != old_meta["note"]):
            self.text_contents.blockSignals(True)
            if meta.blocks is not None:
                from models import _blocks_to_legacy_text
                html = _blocks_to_legacy_text(meta.blocks)
                self.text_contents.setHtml(html if html else "")
            elif meta.text:
                self.text_contents.setHtml(meta.text)
            self.text_contents.blockSignals(False)

        if self.undo_stack:
            def update_func():
                if isinstance(item, MetaTextItem):
                    if not getattr(item, '_editing', False):
                        text_val = item.meta.note
                        item.setPlainText(text_val)
                if hasattr(item, "_update_label_text"):
                    item._update_label_text()
            cmd = ChangeMetaCommand(item, old_meta, new_meta, update_func)
            self.undo_stack.push(cmd)

    def _pick_color(self, initial: QColor, title: str, show_alpha: bool = True) -> Optional[QColor]:
        """Show color picker dialog."""
        options = QColorDialog.ColorDialogOption.ShowAlphaChannel if show_alpha else QColorDialog.ColorDialogOption(0)
        c = QColorDialog.getColor(initial, self, title, options)
        if not c.isValid():
            return None
        return c

    def pick_pen_color(self):
        """Pick border (pen) color."""
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        old_color = QColor(getattr(item, "pen_color", QColor("red")))
        c = self._pick_color(old_color, "Pick Border (Pen) Color")
        if c is None:
            return
        setattr(item, "pen_color", c)
        if isinstance(item, MetaLineItem):
            item._apply_pen()
        elif hasattr(item, "_apply_pen_brush"):
            item._apply_pen_brush()
        self._set_color_widgets("pen", c)
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

        if self.undo_stack:
            def apply():
                if isinstance(item, MetaLineItem):
                    item._apply_pen()
                elif hasattr(item, "_apply_pen_brush"):
                    item._apply_pen_brush()
                self._set_color_widgets("pen", item.pen_color)
            cmd = ChangeStyleCommand(item, "pen_color", old_color, c, apply)
            self.undo_stack.push(cmd)

    def pick_fill_color(self):
        """Pick fill (brush) color."""
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        old_color = QColor(getattr(item, "brush_color", QColor(0, 0, 0, 0)))
        # Present dialog with opaque initial if fill is fully transparent,
        # so clicking a standard/map color gives a visible result. The
        # native Windows dialog preserves alpha from the initial color when
        # only RGB is changed (e.g. clicking a palette swatch).
        dialog_initial = QColor(old_color)
        if dialog_initial.alpha() == 0:
            dialog_initial.setAlpha(255)
        c = self._pick_color(dialog_initial, "Pick Fill (Brush) Color")
        if c is None:
            return
        setattr(item, "brush_color", c)
        if hasattr(item, "_apply_pen_brush"):
            item._apply_pen_brush()
        item.update()
        self._set_color_widgets("fill", c)
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

        if self.undo_stack:
            def apply():
                if hasattr(item, "_apply_pen_brush"):
                    item._apply_pen_brush()
                self._set_color_widgets("fill", item.brush_color)
            cmd = ChangeStyleCommand(item, "brush_color", old_color, c, apply)
            self.undo_stack.push(cmd)

    def _apply_run_color(self, item, color: QColor, saved_cursor=None):
        """Apply *color* to the selected text run (or typing format)."""
        from PyQt6.QtGui import QTextCharFormat as _TCF

        r, g, b, a = color.red(), color.green(), color.blue(), color.alpha()

        fmt = _TCF()
        fmt.setForeground(color)

        cursor = saved_cursor if saved_cursor is not None else self.text_contents.textCursor()

        if cursor is not None:
            if cursor.hasSelection():
                self.text_contents.setTextCursor(cursor)
                cursor.mergeCharFormat(fmt)
                self.text_contents.setTextCursor(cursor)
            else:
                cursor.mergeCharFormat(fmt)
                self.text_contents.setTextCursor(cursor)


        # Always reflect the chosen color in the color-picker widgets.
        self._set_color_widgets("text", color)
        self._refocus_text_contents()

    def pick_text_color(self):
        """Pick text color via color dialog, applying to the current selection."""
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        old_color = QColor(getattr(item, "text_color", QColor("yellow")))
        # Capture cursor/selection BEFORE the dialog steals focus.
        saved_cursor = self.text_contents.textCursor()
        c = self._pick_color(old_color, "Pick Text Color")
        if c is None:
            return
        # The QTextDocument's own undo stack handles undo for char-format changes.
        self._apply_run_color(item, c, saved_cursor=saved_cursor)

    def _on_angle_changed(self, value: int):
        """Handle rotation angle change from spinner."""
        item = self._current_item
        if item is None or not hasattr(item, 'set_rotation_angle'):
            return
        if not item._is_rotatable():
            return
        item.set_rotation_angle(float(value))

    def _on_adjust1_changed(self, value: int):
        """Handle adjust1 change (radius, indent, cap, shaft, bend radius depending on kind)."""
        item = self._current_item
        if item is None:
            return

        old_val = getattr(item, "_adjust1", None)
        if old_val is None:
            return

        if isinstance(item, MetaRoundedRectItem):
            item.set_adjust1(float(value))
        elif isinstance(item, MetaHexagonItem):
            item.set_adjust1(value / 100.0)
        elif isinstance(item, MetaCylinderItem):
            item.set_adjust1(value / 100.0)
        elif isinstance(item, MetaBlockArrowItem):
            item.set_adjust1(value / 100.0)
        elif isinstance(item, (MetaCurveItem, MetaOrthoCurveItem)):
            item.set_adjust1(float(value))
        elif isinstance(item, MetaIsoCubeItem):
            item.set_adjust1(float(value))
        elif isinstance(item, MetaSeqBlockItem):
            item.set_adjust1(value / 100.0)
        else:
            return

        if hasattr(item, "_notify_changed"):
            item._notify_changed()

        if self.undo_stack:
            new_val = item._adjust1
            def apply():
                item._update_path()
                if hasattr(item, "_update_label_position"):
                    item._update_label_position()
            cmd = ChangeStyleCommand(item, "_adjust1", old_val, new_val, apply)
            self.undo_stack.push(cmd)

    def _on_line_width_changed(self, value: int):
        """Handle line width change."""
        item = self._current_item
        if item is None or not hasattr(item, "pen_width"):
            return
        old_val = item.pen_width
        item.pen_width = value
        if hasattr(item, "_apply_pen"):
            item._apply_pen()
        elif hasattr(item, "_apply_pen_brush"):
            item._apply_pen_brush()
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

        if self.undo_stack:
            def apply():
                if hasattr(item, "_apply_pen"):
                    item._apply_pen()
                elif hasattr(item, "_apply_pen_brush"):
                    item._apply_pen_brush()
            cmd = ChangeStyleCommand(item, "pen_width", old_val, value, apply)
            self.undo_stack.push(cmd)

    def _on_dash_changed(self, index: int):
        """Handle line dash style change."""
        item = self._current_item
        if item is None or not hasattr(item, "line_dash"):
            return
        dash_styles = ["solid", "dashed"]
        if 0 <= index < len(dash_styles):
            old_dash = item.line_dash
            item.line_dash = dash_styles[index]
            is_dashed = dash_styles[index] == "dashed"
            if is_dashed:
                self.dash_length_spin.blockSignals(True)
                self.dash_length_spin.setValue(30)
                self.dash_length_spin.blockSignals(False)
                self.dash_solid_spin.blockSignals(True)
                self.dash_solid_spin.setValue(50)
                self.dash_solid_spin.blockSignals(False)
                item.dash_pattern_length = 30.0
                item.dash_solid_percent = 50.0
            if hasattr(item, "_apply_pen"):
                item._apply_pen()
            elif hasattr(item, "_apply_pen_brush"):
                item._apply_pen_brush()
            if hasattr(item, "_notify_changed"):
                item._notify_changed()

            if self.undo_stack:
                def apply():
                    if hasattr(item, "_apply_pen"):
                        item._apply_pen()
                    elif hasattr(item, "_apply_pen_brush"):
                        item._apply_pen_brush()
                cmd = ChangeStyleCommand(item, "line_dash", old_dash, dash_styles[index], apply)
                self.undo_stack.push(cmd)

    def _on_dash_pattern_changed(self, value: int):
        """Handle custom dash pattern change."""
        item = self._current_item
        if item is None or not hasattr(item, "line_dash"):
            return
        old_length = item.dash_pattern_length
        old_solid = item.dash_solid_percent
        item.dash_pattern_length = float(self.dash_length_spin.value())
        item.dash_solid_percent = float(self.dash_solid_spin.value())
        if hasattr(item, "_apply_pen"):
            item._apply_pen()
        elif hasattr(item, "_apply_pen_brush"):
            item._apply_pen_brush()
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

        if self.undo_stack:
            new_length = item.dash_pattern_length
            new_solid = item.dash_solid_percent
            def apply():
                if hasattr(item, "_apply_pen"):
                    item._apply_pen()
                elif hasattr(item, "_apply_pen_brush"):
                    item._apply_pen_brush()
            # Use dash_pattern_length as primary property, store solid as tuple
            cmd = ChangeStyleCommand(
                item, "dash_pattern_length", old_length, new_length, apply)
            self.undo_stack.push(cmd)

    def _on_arrow_changed(self, index: int):
        """Handle arrow mode change."""
        item = self._current_item
        if item is None or not isinstance(item, (MetaLineItem, MetaCurveItem, MetaOrthoCurveItem)):
            return
        arrow_modes = ["none", "start", "end", "both"]
        if 0 <= index < len(arrow_modes):
            old_mode = item.arrow_mode
            item.set_arrow_mode(arrow_modes[index])
            if hasattr(item, "_notify_changed"):
                item._notify_changed()

            if self.undo_stack:
                def apply():
                    item.update()
                cmd = ChangeStyleCommand(item, "arrow_mode", old_mode, arrow_modes[index], apply)
                self.undo_stack.push(cmd)

    def _on_arrow_size_changed(self, value: int):
        """Handle arrow size change."""
        item = self._current_item
        if item is None or not isinstance(item, (MetaLineItem, MetaCurveItem, MetaOrthoCurveItem)):
            return
        old_val = item.arrow_size
        item.arrow_size = float(value)
        item.update()
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

        if self.undo_stack:
            def apply():
                item.update()
            cmd = ChangeStyleCommand(item, "arrow_size", old_val, float(value), apply)
            self.undo_stack.push(cmd)

    def _on_adjust2_changed(self, value: int):
        """Handle adjust2 change (head length for blockarrow, angle for isocube, divider for seqblock)."""
        item = self._current_item
        if item is None or not isinstance(item, (MetaBlockArrowItem, MetaIsoCubeItem, MetaSeqBlockItem)):
            return
        old_val = item._adjust2
        if isinstance(item, MetaSeqBlockItem):
            item.set_adjust2(value / 100.0)
        else:
            item.set_adjust2(float(value))
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

        if self.undo_stack:
            new_val = item._adjust2
            def apply():
                item._update_path()
                if hasattr(item, "_update_label_position"):
                    item._update_label_position()
            cmd = ChangeStyleCommand(item, "_adjust2", old_val, new_val, apply)
            self.undo_stack.push(cmd)

    def _on_text_box_width_changed(self, value: int):
        """Handle text box width change for line items."""
        item = self._current_item
        if item is None or not isinstance(item, MetaLineItem):
            return
        if not hasattr(item, "meta"):
            return
        old_val = item.meta.text_box_width
        item.meta.text_box_width = float(value)
        item.prepareGeometryChange()
        if hasattr(item, "_update_label_text"):
            item._update_label_text()
        item.update()
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

        if self.undo_stack:
            def update_func():
                item.prepareGeometryChange()
                if hasattr(item, "_update_label_text"):
                    item._update_label_text()
                item.update()
            cmd = ChangeMetaCommand(
                item, {"text_box_width": old_val}, {"text_box_width": float(value)}, update_func)
            self.undo_stack.push(cmd)

    def _on_text_spacing_changed(self, index: int):
        """Handle text spacing change."""
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        spacing_values = [0.0, 0.5, 1.0, 1.5, 2.0]
        if 0 <= index < len(spacing_values):
            old_val = getattr(item.meta, "spacing", getattr(item.meta, "text_spacing", 0.0))
            item.meta.spacing = spacing_values[index]
            if hasattr(item, "_update_label_text"):
                item._update_label_text()
            if hasattr(item, "_notify_changed"):
                item._notify_changed()

            if self.undo_stack:
                def update_func():
                    if hasattr(item, "_update_label_text"):
                        item._update_label_text()
                cmd = ChangeMetaCommand(
                    item, {"spacing": old_val}, {"spacing": spacing_values[index]}, update_func)
                self.undo_stack.push(cmd)

    def _on_text_valign_changed(self, index: int):
        """Handle text vertical alignment change."""
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        valign_values = ["top", "middle", "bottom"]
        if 0 <= index < len(valign_values):
            old_val = getattr(item.meta, "valign", getattr(item.meta, "text_valign", "top"))
            new_val = valign_values[index]
            # Write to both flat field and nested frame
            item.meta.valign = new_val
            if item.meta.frame is None:
                item.meta.frame = item.meta.effective_frame()
            item.meta.frame.valign = new_val
            if hasattr(item, "_update_label_position"):
                item._update_label_position()
            item.update()
            if hasattr(item, "_notify_changed"):
                item._notify_changed()

            if self.undo_stack:
                def update_func():
                    if hasattr(item, "_update_label_position"):
                        item._update_label_position()
                    item.update()
                cmd = ChangeMetaCommand(
                    item, {"valign": old_val}, {"valign": new_val}, update_func)
                self.undo_stack.push(cmd)

    def _on_text_contents_changed(self):
        """Handle text content edit (live update, no undo batching).

        Extracts overlay-2.0 blocks from the QTextDocument and stores them in
        ``meta.blocks``.  Also updates the legacy ``meta.text`` HTML fallback
        so canvas items that haven't been migrated to blocks rendering still
        display correctly.

        Ensures ``meta.frame`` and ``meta.default_format`` are initialised from
        the current UI controls so the three sub-objects stay in sync.
        """
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        # Skip when _apply_spacing_to_textedit_and_meta is driving
        if getattr(self, "_suppress_spacing_feedback", False):
            return

        meta = item.meta

        # Ensure nested objects exist (initialise from current state if first edit)
        if meta.frame is None:
            meta.frame = TextFrame(
                halign=getattr(meta, "halign", "center"),
                valign=getattr(meta, "valign", "top"),
                margin_left=getattr(meta, "margin_left", 4.0),
                margin_right=getattr(meta, "margin_right", 4.0),
                margin_top=getattr(meta, "margin_top", 4.0),
                margin_bottom=getattr(meta, "margin_bottom", 4.0),
            )
        if meta.default_format is None:
            # Snapshot the document's ACTUAL default font — set_item() already
            # installed the correct font from settings/effective_default_format.
            # Using the physical family here ensures _qtextdoc_to_blocks only
            # emits font_family deltas for runs that were EXPLICITLY changed;
            # runs using the document default won't carry a redundant font_family.
            _doc_font = self.text_contents.document().defaultFont()
            _fam = _doc_font.family()
            _pt = _doc_font.pointSize()
            meta.default_format = CharFormat(
                font_family=_fam if _fam else getattr(meta, "font_family", ""),
                font_size=_pt if _pt > 0 else max(6, getattr(meta, "font_size", 12)),
                color=getattr(meta, "color", "") or "",
            )

        # Extract blocks from the QTextDocument
        doc = self.text_contents.document()
        raw_blocks = _qtextdoc_to_blocks(doc, meta.default_format)
        meta.blocks = [TextBlock.from_dict(b) for b in raw_blocks]

        # Update legacy text fallback (for canvas items rendering via HTML)
        import re
        html = self.text_contents.toHtml()
        m = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL | re.IGNORECASE)
        meta.text = m.group(1).strip() if m else self.text_contents.toPlainText()


        # The QTextEdit is authoritative for the lifetime of this editing session.
        if isinstance(item, MetaTextItem):
            self._text_contents_is_authoritative = True

        # Suppress _on_text_cursor_changed from re-reading format controls
        # during the textChanged→notify→set_item round-trip.  The cursor
        # position change that accompanies typing should NOT reset the picker.
        self._text_content_just_changed = True
        try:
            if isinstance(item, MetaTextItem):
                item._render_from_meta()
            elif hasattr(item, "_update_label_text"):
                item._update_label_text()
            if hasattr(item, "_notify_changed"):
                item._notify_changed()
        finally:
            self._text_content_just_changed = False


    def _sync_format_controls_from_cursor(self):
        """Read the QTextEdit cursor's char/block format and update all
        format controls (font, size, color, bold, italic, alignment, etc.).

        Called when the QTextEdit is authoritative (during MetaTextItem
        editing) so the UI always reflects the cursor's actual state.
        """
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return

        from PyQt6.QtGui import QFont as _QFont
        from PyQt6.QtCore import Qt as _Qt

        _eff_fmt = item.meta.effective_default_format()

        cursor = self.text_contents.textCursor()
        char_fmt = cursor.charFormat()
        block_fmt = cursor.blockFormat()

        self._block_format_signals(True)
        try:
            # ── font family ───────────────────────────────────────────
            families = char_fmt.fontFamilies()
            family = (families[0] if isinstance(families, list) and families
                      else families if isinstance(families, str) else "")
            if not family:
                family = self.text_contents.document().defaultFont().family()
            if not family:
                family = _eff_fmt.font_family
            if family:
                self.combo_font.setCurrentFont(_QFont(family))

            # ── font size ─────────────────────────────────────────────
            pt = char_fmt.fontPointSize()
            if pt <= 0:
                pt = self.text_contents.document().defaultFont().pointSize()
            if pt <= 0:
                pt = _eff_fmt.font_size or 12
            self.spin_text_size.setValue(int(round(pt)))

            # ── text color ────────────────────────────────────────────
            # NEVER read color from charFormat().foreground().color() — Qt
            # mangles 8-digit hex (#RRGGBBAA ↔ #AARRGGBB) when colors are
            # inherited via CSS.  Always use the item's text_color attribute
            # which was set correctly via hex_to_qcolor in _render_from_meta.
            _item_tc = getattr(item, "text_color", None)
            if _item_tc is not None and _item_tc.isValid():
                self._set_color_widgets("text", _item_tc)
            elif _eff_fmt.color:
                from utils import hex_to_qcolor
                _text_c = hex_to_qcolor(_eff_fmt.color, QColor())
                if _text_c.isValid():
                    self._set_color_widgets("text", _text_c)

            # ── bold / italic / underline / strikethrough ─────────────
            self.chk_bold.setChecked(char_fmt.fontWeight() >= 700)
            self.chk_italic.setChecked(char_fmt.fontItalic())
            self.chk_underline.setChecked(char_fmt.fontUnderline())
            self.chk_strikethrough.setChecked(char_fmt.fontStrikeOut())

            # ── block alignment → halign combo ────────────────────────
            alignment = block_fmt.alignment()
            if alignment & _Qt.AlignmentFlag.AlignHCenter:
                halign = "center"
            elif alignment & _Qt.AlignmentFlag.AlignRight:
                halign = "right"
            elif alignment & _Qt.AlignmentFlag.AlignJustify:
                halign = "justified"
            elif alignment & _Qt.AlignmentFlag.AlignLeft:
                halign = "left"
            else:
                halign = item.meta.effective_frame().halign or ""
            if halign:
                halign_map = {"left": 0, "center": 1, "justified": 2, "right": 3}
                self.text_halign_combo.setCurrentIndex(halign_map.get(halign, 0))

            # ── block line height → spacing controls ──────────────────
            _qt_type_map = {0: "single", 1: "proportional", 2: "fixed",
                            3: "minimum", 4: "line_distance"}
            _lh_t = block_fmt.lineHeightType()
            _lh_v = block_fmt.lineHeight()
            _type_name = _qt_type_map.get(_lh_t, "single")
            _type_idx_map = {"single": 0, "proportional": 1, "fixed": 2,
                             "minimum": 3, "line_distance": 4}
            _idx = _type_idx_map.get(_type_name, 0)
            self.spacing_type_combo.setCurrentIndex(_idx)
            _is_single = (_idx == 0)
            _is_proportional = (_idx == 1)
            self.spin_spacing_value.setEnabled(not _is_single)
            self.spin_spacing_value.setSuffix(" %" if _is_proportional else " pt")
            if _is_single:
                doc_font = self.text_contents.document().defaultFont()
                _pt = doc_font.pointSize()
                self.spin_spacing_value.setValue(max(6, _pt if _pt > 0 else 12))
            elif _lh_v > 0:
                self.spin_spacing_value.setValue(int(_lh_v))

            # ── block paragraph spacing → space before/after ──────────
            self.spin_space_before.setValue(int(block_fmt.topMargin()))
            self.spin_space_after.setValue(int(block_fmt.bottomMargin()))
        finally:
            self._block_format_signals(False)

    def _on_text_cursor_changed(self):
        """Reflect the current run's format in the UI controls.

        Reads the ``QTextCharFormat`` at the cursor (or of the selection) and
        the ``QTextBlockFormat`` of the current paragraph, then updates the
        font, size, color, and alignment controls — without triggering the
        format-change handlers that would write back to the document.
        """
        if not self.text_contents.hasFocus():
            return
        if self._text_contents_is_authoritative:
            return
        if self._suppress_cursor_sync:
            return
        self._sync_format_controls_from_cursor()

    def _apply_font_to_textedit(self):
        """Sync QTextEdit default font from current font_family/font_size widgets."""
        from PyQt6.QtGui import QFont as _QFont
        family = self.combo_font.currentFont().family()
        size = max(6, int(self.spin_text_size.value()))
        fnt = _QFont(family) if family else _QFont()
        fnt.setPointSize(size)
        self.text_contents.document().setDefaultFont(fnt)

    def _apply_align_to_textedit(self, halign: str):
        """Set QTextEdit alignment at all three levels.

        1. **Document default** (``defaultTextOption``) — used for rendering
           and as the baseline for new documents.
        2. **All existing blocks** that don't carry an explicit per-block
           override — so blocks loaded from ``_blocks_to_html`` without an
           inline ``text-align`` inherit the frame default rather than Qt's
           hard-coded ``AlignLeft``.
        3. **Cursor block format** — inherited by new paragraphs created
           when the user types.  Qt uses the cursor's block format, *not*
           ``defaultTextOption``, for new-paragraph creation.
        """
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QTextOption, QTextBlockFormat, QTextCursor
        flag_map = {
            "left":      Qt.AlignmentFlag.AlignLeft,
            "center":    Qt.AlignmentFlag.AlignHCenter,
            "right":     Qt.AlignmentFlag.AlignRight,
            "justified": Qt.AlignmentFlag.AlignJustify,
        }
        flag = flag_map.get(halign, Qt.AlignmentFlag.AlignHCenter)

        # 1. Document default
        opt = self.text_contents.document().defaultTextOption()
        opt.setAlignment(flag)
        self.text_contents.document().setDefaultTextOption(opt)

        # 2. Apply to all existing blocks and set cursor block format
        #    for new paragraphs.  Block signals to prevent textChanged
        #    from firing during the format update.
        self.text_contents.blockSignals(True)
        try:
            cursor = self.text_contents.textCursor()
            pos = cursor.position()  # remember cursor position
            # Apply to all existing blocks
            cursor.select(QTextCursor.SelectionType.Document)
            bf = QTextBlockFormat()
            bf.setAlignment(flag)
            cursor.mergeBlockFormat(bf)
            # Restore cursor position and set block format for new paragraphs
            cursor.clearSelection()
            cursor.setPosition(pos)
            cursor.setBlockFormat(bf)
            self.text_contents.setTextCursor(cursor)
        finally:
            self.text_contents.blockSignals(False)

    def _apply_default_spacing_to_textedit(self, eff_fmt):
        """Apply spacing from effective default_format to all QTextEdit blocks
        and set the cursor block format so new paragraphs inherit the spacing.

        Called from set_item() to initialise the QTextEdit with the item's
        default line spacing.
        """
        from PyQt6.QtGui import QTextCursor as _TC
        _spacing_type_map = {
            "single": 0, "proportional": 1, "fixed": 2,
            "minimum": 3, "line_distance": 4,
        }
        sp_type = getattr(eff_fmt, "spacing_type", "single") or "single"
        sp_val = getattr(eff_fmt, "spacing_value", 0.0)
        qt_type = _spacing_type_map.get(sp_type, 0)
        qt_value = 0.0 if qt_type == 0 else float(sp_val)

        self.text_contents.blockSignals(True)
        try:
            doc = self.text_contents.document()
            # Apply to all existing blocks
            blk = doc.begin()
            while blk.isValid():
                c = _TC(doc)
                c.setPosition(blk.position())
                bf = c.blockFormat()
                bf.setLineHeight(qt_value, qt_type)
                c.setBlockFormat(bf)
                blk = blk.next()
            # Set cursor block format for new paragraphs
            cursor = self.text_contents.textCursor()
            bf = cursor.blockFormat()
            bf.setLineHeight(qt_value, qt_type)
            cursor.setBlockFormat(bf)
            self.text_contents.setTextCursor(cursor)
        finally:
            self.text_contents.blockSignals(False)

    def _on_halign_changed(self, index: int):
        """Handle horizontal text alignment change.

        When the text editor has focus, applies the alignment to the current
        paragraph (block-level format).  Always updates ``meta.frame.halign``
        as the document-level default.
        """
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        halign_values = ["left", "center", "justified", "right"]
        if 0 <= index < len(halign_values):
            old_val = getattr(item.meta, "halign", "center")
            new_val = halign_values[index]

            # Apply to current paragraph — no hasFocus() check needed (combo
            # steals focus but cursor position/selection is preserved).
            from PyQt6.QtGui import QTextBlockFormat as _TBF
            from PyQt6.QtCore import Qt as _Qt
            _flag_map = {
                "left":      _Qt.AlignmentFlag.AlignLeft,
                "center":    _Qt.AlignmentFlag.AlignHCenter,
                "right":     _Qt.AlignmentFlag.AlignRight,
                "justified": _Qt.AlignmentFlag.AlignJustify,
            }
            blk_fmt = _TBF()
            blk_fmt.setAlignment(_flag_map.get(new_val, _Qt.AlignmentFlag.AlignLeft))
            cursor = self.text_contents.textCursor()
            cursor.mergeBlockFormat(blk_fmt)
            self.text_contents.setTextCursor(cursor)
            self._apply_align_to_textedit(new_val)

            # Write to flat field and nested frame (document-level default)
            item.meta.halign = new_val
            if item.meta.frame is None:
                item.meta.frame = item.meta.effective_frame()
            item.meta.frame.halign = new_val

            if isinstance(item, MetaTextItem):
                item._render_from_meta()
            elif hasattr(item, "_update_label_text"):
                item._update_label_text()
            if hasattr(item, "_notify_changed"):
                item._notify_changed()
            self._refocus_text_contents()
            if self.undo_stack:
                def update_func():
                    if hasattr(item, "_update_label_text"):
                        item._update_label_text()
                cmd = ChangeMetaCommand(item, {"halign": old_val}, {"halign": new_val}, update_func)
                self.undo_stack.push(cmd)

    def _on_font_size_changed(self, value: int):
        """Handle font size change for the selected run."""
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return


        from PyQt6.QtGui import QTextCharFormat as _TCF
        fmt = _TCF()
        fmt.setFontPointSize(float(value))

        cursor = self.text_contents.textCursor()
        if cursor.hasSelection():
            self.text_contents.setTextCursor(cursor)
            cursor.mergeCharFormat(fmt)
            self.text_contents.setTextCursor(cursor)
            self._refocus_text_contents()
            return
        cursor.mergeCharFormat(fmt)
        self.text_contents.setTextCursor(cursor)
        if not self._text_contents_is_authoritative:
            self._apply_font_to_textedit()
        self._refocus_text_contents()

    def _on_font_changed(self, font):
        """Handle font family change for the selected run."""
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        new_val = font.family()


        from PyQt6.QtGui import QTextCharFormat as _TCF
        fmt = _TCF()
        fmt.setFontFamilies([new_val])

        cursor = self.text_contents.textCursor()
        if cursor.hasSelection():
            self.text_contents.setTextCursor(cursor)
            cursor.mergeCharFormat(fmt)
            self.text_contents.setTextCursor(cursor)
            self._refocus_text_contents()
            return
        cursor.mergeCharFormat(fmt)
        self.text_contents.setTextCursor(cursor)
        if not self._text_contents_is_authoritative:
            self._apply_font_to_textedit()
        self._refocus_text_contents()

    def _refocus_text_contents(self):
        """Return focus to the Contents tab text widget if editing a MetaTextItem.

        Called after every format-change handler so keystrokes continue
        going to the text editor instead of triggering toolbar shortcuts.
        Also ensures the authoritative flag stays set for the session.
        """
        if isinstance(self._current_item, MetaTextItem):
            self._text_contents_is_authoritative = True
            self.text_contents.setFocus()

    # ── bold / italic / underline / strikethrough handlers ──────────

    def _apply_char_format_toggle(self, setter_name: str, value: bool):
        """Apply a boolean char-format toggle to the selection or typing format."""
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return


        from PyQt6.QtGui import QTextCharFormat as _TCF, QFont as _QFont
        fmt = _TCF()
        if setter_name == "setFontWeight":
            fmt.setFontWeight(_QFont.Weight.Bold if value else _QFont.Weight.Normal)
        else:
            getattr(fmt, setter_name)(value)

        cursor = self.text_contents.textCursor()
        if cursor.hasSelection():
            self.text_contents.setTextCursor(cursor)
            cursor.mergeCharFormat(fmt)
            self.text_contents.setTextCursor(cursor)
            self._refocus_text_contents()
            return
        # No selection: set typing format for subsequent input.
        cursor.mergeCharFormat(fmt)
        self.text_contents.setTextCursor(cursor)
        self._refocus_text_contents()

    def _on_bold_changed(self, checked: bool):
        """Toggle bold on selected text or typing format."""
        self._apply_char_format_toggle("setFontWeight", checked)

    def _on_italic_changed(self, checked: bool):
        """Toggle italic on selected text or typing format."""
        self._apply_char_format_toggle("setFontItalic", checked)

    def _on_underline_changed(self, checked: bool):
        """Toggle underline on selected text or typing format."""
        self._apply_char_format_toggle("setFontUnderline", checked)

    def _on_strikethrough_changed(self, checked: bool):
        """Toggle strikethrough on selected text or typing format."""
        self._apply_char_format_toggle("setFontStrikeOut", checked)

    def _on_wrap_changed(self, checked: bool):
        """Handle text wrap toggle."""
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        old_val = getattr(item.meta, "wrap", True)
        item.meta.wrap = checked
        if hasattr(item, "_update_label_text"):
            item._update_label_text()
        if hasattr(item, "_notify_changed"):
            item._notify_changed()
        self._refocus_text_contents()
        if self.undo_stack:
            def update_func():
                if hasattr(item, "_update_label_text"):
                    item._update_label_text()
            cmd = ChangeMetaCommand(item, {"wrap": old_val}, {"wrap": checked}, update_func)
            self.undo_stack.push(cmd)

    def _on_flow_type_changed(self, index: int):
        """Handle flow type change."""
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        flow_values = ["none", "horizontal", "vertical", "none"]
        old_val = getattr(item.meta, "flow_type", "none")
        item.meta.flow_type = flow_values[index] if 0 <= index < len(flow_values) else "none"
        if hasattr(item, "_notify_changed"):
            item._notify_changed()
        self._refocus_text_contents()
        if self.undo_stack:
            cmd = ChangeMetaCommand(item, {"flow_type": old_val}, {"flow_type": item.meta.flow_type}, lambda: None)
            self.undo_stack.push(cmd)

    # ── Line height (spacing) controls ────────────────────────────

    # Combo indices → QTextBlockFormat.LineHeightTypes enum values
    _LINE_HEIGHT_TYPES = [0, 1, 2, 3, 4]  # Single, Proportional, Fixed, Minimum, LineDistance
    _LINE_HEIGHT_NAMES = ["single", "proportional", "fixed", "minimum", "line_distance"]

    def _on_spacing_type_changed(self, index: int):
        """Handle spacing type combo change.

        Updates the spinbox UI (suffix, enabled, default value) then
        applies the spacing to the QTextEdit and stores in meta.
        Blocks the spinbox signal during setup to prevent intermediate
        _on_spacing_value_changed callbacks from cascading.
        """
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return

        is_single = (index == 0)
        is_proportional = (index == 1)

        # Block spinbox signal during range/value adjustment
        self.spin_spacing_value.blockSignals(True)
        try:
            self.spin_spacing_value.setEnabled(not is_single)
            if is_proportional:
                self.spin_spacing_value.setSuffix(" %")
                self.spin_spacing_value.setRange(25, 500)
                if self.spin_spacing_value.value() < 50:
                    self.spin_spacing_value.setValue(100)
            else:
                self.spin_spacing_value.setSuffix(" pt")
                self.spin_spacing_value.setRange(1, 200)
            if is_single:
                doc_font = self.text_contents.document().defaultFont()
                pt = doc_font.pointSize()
                self.spin_spacing_value.setValue(max(6, pt if pt > 0 else 12))
        finally:
            self.spin_spacing_value.blockSignals(False)

        # Apply once with the final settled values
        self._apply_spacing_to_textedit_and_meta()

    def _on_spacing_value_changed(self, value: int):
        """Handle spacing value spinbox change."""
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        self._apply_spacing_to_textedit_and_meta()

    def _affected_block_indices(self) -> list:
        """Return the list of meta.blocks indices affected by the current
        QTextEdit cursor/selection.  If there's a selection, returns all
        block indices that overlap it; otherwise returns [current_block].
        """
        cursor = self.text_contents.textCursor()
        doc = self.text_contents.document()
        if cursor.hasSelection():
            sel_start = cursor.selectionStart()
            sel_end = cursor.selectionEnd()
            indices = []
            blk = doc.begin()
            idx = 0
            while blk.isValid():
                blk_start = blk.position()
                blk_end = blk_start + blk.length() - 1
                if blk_end >= sel_start and blk_start <= sel_end:
                    indices.append(idx)
                blk = blk.next()
                idx += 1
            return indices
        return [cursor.block().blockNumber()]

    def _on_space_before_after_changed(self, _value: int):
        """Handle space_before / space_after spinbox change.

        Applies to the selected/current blocks (per-block override).
        """
        from PyQt6.QtGui import QTextCursor as _TC

        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return

        sb = float(self.spin_space_before.value())
        sa = float(self.spin_space_after.value())
        affected = self._affected_block_indices()

        # 1. Apply to affected QTextEdit blocks
        self._suppress_spacing_feedback = True
        try:
            doc = self.text_contents.document()
            blk = doc.begin()
            idx = 0
            while blk.isValid():
                if idx in affected:
                    c = _TC(doc)
                    c.setPosition(blk.position())
                    bf = c.blockFormat()
                    bf.setTopMargin(sb)
                    bf.setBottomMargin(sa)
                    c.setBlockFormat(bf)
                blk = blk.next()
                idx += 1
        finally:
            self._suppress_spacing_feedback = False

        # 2. Store per-block in meta.blocks
        meta = item.meta
        if meta.blocks:
            for i in affected:
                if i < len(meta.blocks):
                    meta.blocks[i].space_before = sb
                    meta.blocks[i].space_after = sa

        # 3. Render canvas and notify JSON
        self._notify_spacing_change(item)

    def _apply_spacing_to_textedit_and_meta(self):
        """Apply spacing controls to the selected/current blocks in the
        QTextEdit and store as per-block overrides in meta.blocks.

        The ``default_format`` is NOT modified — only "Save as Default" does
        that.  Blocks that match the default will emit no ``spacing_type``
        in the JSON; blocks that differ will carry their own override.
        """
        from PyQt6.QtGui import QTextCursor as _TC

        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return

        index = self.spacing_type_combo.currentIndex()
        value = self.spin_spacing_value.value()
        qt_type = self._LINE_HEIGHT_TYPES[index] if 0 <= index < 5 else 0
        type_name = self._LINE_HEIGHT_NAMES[index] if 0 <= index < 5 else "single"
        qt_value = 0.0 if qt_type == 0 else float(value)

        cursor = self.text_contents.textCursor()
        has_sel = cursor.hasSelection()
        sel_start = cursor.selectionStart() if has_sel else cursor.position()
        sel_end = cursor.selectionEnd() if has_sel else cursor.position()
        affected = self._affected_block_indices()


        # 1. Apply to affected QTextEdit blocks
        self._suppress_spacing_feedback = True
        try:
            doc = self.text_contents.document()
            blk = doc.begin()
            idx = 0
            while blk.isValid():
                if idx in affected:
                    c = _TC(doc)
                    c.setPosition(blk.position())
                    bf = c.blockFormat()
                    bf.setLineHeight(qt_value, qt_type)
                    c.setBlockFormat(bf)
                blk = blk.next()
                idx += 1
        finally:
            self._suppress_spacing_feedback = False


        # 2. Store per-block in meta.blocks (delta from default_format)
        meta = item.meta
        _def_type = ""
        if meta.default_format:
            _def_type = meta.default_format.spacing_type or "single"
        if meta.blocks:
            for i in affected:
                if i < len(meta.blocks):
                    if type_name == _def_type and (type_name == "single" or
                            float(value) == getattr(meta.default_format, "spacing_value", 0.0)):
                        meta.blocks[i].spacing_type = ""
                        meta.blocks[i].spacing_value = 0.0
                    else:
                        meta.blocks[i].spacing_type = type_name
                        meta.blocks[i].spacing_value = float(value)


        # 3. Render canvas and notify JSON
        self._notify_spacing_change(item)

        # 4. Restore text selection (without stealing focus from the spinbox)
        if has_sel:
            self.text_contents.blockSignals(True)
            try:
                c = self.text_contents.textCursor()
                c.setPosition(sel_start)
                c.setPosition(sel_end, _TC.MoveMode.KeepAnchor)
                self.text_contents.setTextCursor(c)
            finally:
                self.text_contents.blockSignals(False)

    def _notify_spacing_change(self, item):
        """Render canvas label and notify JSON after a spacing change.

        Sets authoritative flag so set_item() won't repopulate the QTextEdit.
        Saves and restores the focus widget so the spinbox doesn't lose focus
        during intermediate value ticks.
        """
        from PyQt6.QtWidgets import QApplication
        _focus_widget = QApplication.focusWidget()
        was_auth = self._text_contents_is_authoritative
        self._text_contents_is_authoritative = True
        try:
            if isinstance(item, MetaTextItem):
                item._render_from_meta()
            elif hasattr(item, "_update_label_text"):
                item._update_label_text()
            if hasattr(item, "_notify_changed"):
                item._notify_changed()
        finally:
            self._text_contents_is_authoritative = was_auth
        # Restore focus to the widget that had it before notify
        if _focus_widget is not None and _focus_widget.isVisible():
            _focus_widget.setFocus()


    def _on_margins_changed(self, _value: int):
        """Handle any margin spinbox change — reads all four margins."""
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        old_vals = {
            "margin_left": getattr(item.meta, "margin_left", 0.0),
            "margin_right": getattr(item.meta, "margin_right", 0.0),
            "margin_top": getattr(item.meta, "margin_top", 0.0),
            "margin_bottom": getattr(item.meta, "margin_bottom", 0.0),
        }
        item.meta.margin_left = float(self.spin_margin_left.value())
        item.meta.margin_right = float(self.spin_margin_right.value())
        item.meta.margin_top = float(self.spin_margin_top.value())
        item.meta.margin_bottom = float(self.spin_margin_bottom.value())
        # Mirror to nested frame
        if item.meta.frame is None:
            item.meta.frame = item.meta.effective_frame()
        item.meta.frame.margin_left = item.meta.margin_left
        item.meta.frame.margin_right = item.meta.margin_right
        item.meta.frame.margin_top = item.meta.margin_top
        item.meta.frame.margin_bottom = item.meta.margin_bottom
        new_vals = {
            "margin_left": item.meta.margin_left,
            "margin_right": item.meta.margin_right,
            "margin_top": item.meta.margin_top,
            "margin_bottom": item.meta.margin_bottom,
        }
        if hasattr(item, "_update_label_text"):
            item._update_label_text()
        if hasattr(item, "_notify_changed"):
            item._notify_changed()
        self._refocus_text_contents()
        if self.undo_stack and old_vals != new_vals:
            def update_func():
                if hasattr(item, "_update_label_text"):
                    item._update_label_text()
            cmd = ChangeMetaCommand(item, old_vals, new_vals, update_func)
            self.undo_stack.push(cmd)

    def _on_graphic_url_changed(self):
        """Handle image URL edit."""
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        old_val = getattr(item.meta, "image_url", "")
        item.meta.image_url = self.edit_graphic_url.text()
        if hasattr(item, "_notify_changed"):
            item._notify_changed()
        if self.undo_stack and old_val != item.meta.image_url:
            cmd = ChangeMetaCommand(item, {"image_url": old_val}, {"image_url": item.meta.image_url}, lambda: None)
            self.undo_stack.push(cmd)

    def _on_graphic_anchor_changed(self, value: int):
        """Handle image anchor spinbox change."""
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        old_val = getattr(item.meta, "image_anchor", 0)
        item.meta.image_anchor = value
        if hasattr(item, "_notify_changed"):
            item._notify_changed()
        if self.undo_stack and old_val != value:
            cmd = ChangeMetaCommand(item, {"image_anchor": old_val}, {"image_anchor": value}, lambda: None)
            self.undo_stack.push(cmd)

    def _on_port_selected(self, ann_id: str):
        """Handle port ID clicked in the ports list — emit port_selected signal."""
        if ann_id:
            self.port_selected.emit(ann_id)

    def _on_ports_focus_lost(self):
        """Restore JSON editor focus to the parent item when ports list is left."""
        item = self._current_item
        if item and hasattr(item, "ann_id") and item.ann_id:
            self.port_selected.emit(item.ann_id)

    def update_radius_display(self, item, radius: float):
        """Deprecated: Use update_adjust1_display instead."""
        # Keep for backwards compatibility
        self.update_adjust1_display(item, radius)

    def _setup_hexagon_controls(self, item, pen_color):
        """Configure controls for hexagon items."""
        self._set_preview(self.pen_color_preview, pen_color)
        self._set_preview(self.fill_color_preview, getattr(item, "brush_color", QColor(0, 0, 0, 0)))
        self._set_preview(self.text_color_preview, getattr(item, "text_color", pen_color))
        self._configure_adjust_controls("hexagon")
        adjust1 = getattr(item, "_adjust1", 0.25)
        self.adjust1_spin.blockSignals(True)
        self.adjust1_spin.setValue(int(adjust1 * 100))
        self.adjust1_spin.blockSignals(False)
        self._setup_line_style_controls(item)
        self._setup_text_layout_controls(item)

    def _setup_cylinder_controls(self, item, pen_color):
        """Configure controls for cylinder items."""
        self._set_preview(self.pen_color_preview, pen_color)
        self._set_preview(self.fill_color_preview, getattr(item, "brush_color", QColor(0, 0, 0, 0)))
        self._set_preview(self.text_color_preview, getattr(item, "text_color", pen_color))
        self._configure_adjust_controls("cylinder")
        adjust1 = getattr(item, "_adjust1", 0.15)
        self.adjust1_spin.blockSignals(True)
        self.adjust1_spin.setValue(int(adjust1 * 100))
        self.adjust1_spin.blockSignals(False)
        self._setup_line_style_controls(item)
        self._setup_text_layout_controls(item)

    def _setup_blockarrow_controls(self, item, pen_color):
        """Configure controls for block arrow items."""
        self._set_preview(self.pen_color_preview, pen_color)
        self._set_preview(self.fill_color_preview, getattr(item, "brush_color", QColor(0, 0, 0, 0)))
        self._set_preview(self.text_color_preview, getattr(item, "text_color", pen_color))
        self._configure_adjust_controls("blockarrow")
        adjust1 = getattr(item, "_adjust1", 0.5)
        self.adjust1_spin.blockSignals(True)
        self.adjust1_spin.setValue(int(adjust1 * 100))
        self.adjust1_spin.blockSignals(False)
        adjust2 = getattr(item, "_adjust2", 15)
        self.adjust2_spin.blockSignals(True)
        self.adjust2_spin.setValue(int(adjust2))
        self.adjust2_spin.blockSignals(False)
        self._setup_line_style_controls(item)
        self._setup_text_layout_controls(item)

    def _setup_seqblock_controls(self, item, pen_color):
        """Configure controls for sequence block items."""
        dc = getattr(item, "_divider_count", 0)
        # Divider count spinner
        self.divider_count_spin.blockSignals(True)
        self.divider_count_spin.setValue(dc)
        self.divider_count_spin.blockSignals(False)
        self._set_preview(self.pen_color_preview, pen_color)
        self._set_preview(self.fill_color_preview, getattr(item, "brush_color", QColor(0, 0, 0, 0)))
        self._set_preview(self.text_color_preview, getattr(item, "text_color", pen_color))
        self._configure_adjust_controls("seqblock")
        if hasattr(self, "adjust1_spin"):
            self.adjust1_spin.blockSignals(True)
            self.adjust1_spin.setValue(int(getattr(item, "_adjust1", 0.5) * 100))
            self.adjust1_spin.blockSignals(False)
            self.adjust1_spin.setEnabled(dc >= 1)
            self.adjust1_label.setEnabled(dc >= 1)
        if hasattr(self, "adjust2_spin"):
            self.adjust2_spin.blockSignals(True)
            self.adjust2_spin.setValue(int(getattr(item, "_adjust2", 0.67) * 100))
            self.adjust2_spin.blockSignals(False)
            self.adjust2_spin.setEnabled(dc >= 2)
            self.adjust2_label.setEnabled(dc >= 2)
        if hasattr(self, "adjust3_spin"):
            self.adjust3_spin.blockSignals(True)
            self.adjust3_spin.setValue(int(getattr(item, "_adjust3", 0.83) * 100))
            self.adjust3_spin.blockSignals(False)
            self.adjust3_spin.setEnabled(dc >= 3)
            self.adjust3_label.setEnabled(dc >= 3)
        self._setup_line_style_controls(item)
        self._setup_text_layout_controls(item)

    def _setup_isocube_controls(self, item, pen_color):
        """Configure controls for isometric cube items."""
        self._set_preview(self.pen_color_preview, pen_color)
        self._set_preview(self.fill_color_preview, getattr(item, "brush_color", QColor(0, 0, 0, 0)))
        self._set_preview(self.text_color_preview, getattr(item, "text_color", pen_color))
        self._configure_adjust_controls("isocube")
        adjust1 = getattr(item, "_adjust1", 30)
        max_depth = getattr(item, "_max_depth", lambda: 200)()
        self.adjust1_spin.blockSignals(True)
        self.adjust1_spin.setMaximum(int(max_depth))
        self.adjust1_spin.setValue(int(adjust1))
        self.adjust1_spin.blockSignals(False)
        adjust2 = getattr(item, "_adjust2", 135)
        self.adjust2_spin.blockSignals(True)
        self.adjust2_spin.setValue(int(adjust2))
        self.adjust2_spin.blockSignals(False)
        self._setup_line_style_controls(item)
        self._setup_text_layout_controls(item)

    def _setup_polygon_controls(self, item, pen_color):
        """Configure controls for polygon items."""
        self._set_preview(self.pen_color_preview, pen_color)
        self._set_preview(self.fill_color_preview, getattr(item, "brush_color", QColor(0, 0, 0, 0)))
        self._set_preview(self.text_color_preview, getattr(item, "text_color", pen_color))
        self._setup_line_style_controls(item)
        self._setup_text_layout_controls(item)

    def _setup_curve_controls(self, item, pen_color):
        """Configure controls for curve items (pen, dash, arrow, optional adjust1 for ortho)."""
        has_hv = hasattr(item, "_has_hv_corners") and item._has_hv_corners()
        if has_hv:
            self._configure_adjust_controls("curve")
            adjust1 = getattr(item, "_adjust1", 0)
            self.adjust1_spin.blockSignals(True)
            self.adjust1_spin.setValue(int(adjust1))
            self.adjust1_spin.blockSignals(False)
        self._set_preview(self.pen_color_preview, pen_color)
        self._set_preview(self.text_color_preview, getattr(item, "text_color", pen_color))
        self._setup_line_style_controls(item)
        self._setup_anchor_controls(item)
        self._setup_text_box_dims(item)
        self._setup_text_box_appearance(item)

        # Arrow mode
        arrow_mode = getattr(item, "arrow_mode", "none")
        arrow_map = {"none": 0, "start": 1, "end": 2, "both": 3}
        self.arrow_combo.blockSignals(True)
        self.arrow_combo.setCurrentIndex(arrow_map.get(arrow_mode, 0))
        self.arrow_combo.blockSignals(False)

        # Arrow size
        arrow_size = getattr(item, "arrow_size", 12.0)
        self.arrow_size_spin.blockSignals(True)
        self.arrow_size_spin.setValue(int(arrow_size))
        self.arrow_size_spin.blockSignals(False)

    def _setup_group_controls(self, item, pen_color):
        """Configure controls for group items."""
        pass

    def update_angle_display(self, item, angle: float):
        """Update the angle spinbox display when rotation changes via canvas knob."""
        if self._current_item is not item:
            return
        self.angle_spin.blockSignals(True)
        self.angle_spin.setValue(int(angle) % 360)
        self.angle_spin.blockSignals(False)

    def update_adjust1_display(self, item, value: float):
        """Update the adjust1 spinbox display when it changes via canvas handle."""
        if self._current_item is not item:
            return
        self.adjust1_spin.blockSignals(True)
        if isinstance(item, (MetaRoundedRectItem, MetaCurveItem, MetaOrthoCurveItem, MetaIsoCubeItem)):
            self.adjust1_spin.setValue(int(value))
        elif isinstance(item, (MetaHexagonItem, MetaCylinderItem, MetaBlockArrowItem, MetaSeqBlockItem)):
            self.adjust1_spin.setValue(int(value * 100))
        self.adjust1_spin.blockSignals(False)

    def update_adjust2_display(self, item, value: float):
        """Update the adjust2 spinbox display when it changes via canvas handle."""
        if self._current_item is not item:
            return
        if isinstance(item, (MetaBlockArrowItem, MetaIsoCubeItem)):
            self.adjust2_spin.blockSignals(True)
            self.adjust2_spin.setValue(int(value))
            self.adjust2_spin.blockSignals(False)
        elif isinstance(item, MetaSeqBlockItem):
            self.adjust2_spin.blockSignals(True)
            self.adjust2_spin.setValue(int(value * 100))
            self.adjust2_spin.blockSignals(False)

    def update_adjust3_display(self, item, value: float):
        """Update the adjust3 spinbox display when it changes via canvas handle."""
        if self._current_item is not item:
            return
        if isinstance(item, MetaSeqBlockItem):
            self.adjust3_spin.blockSignals(True)
            self.adjust3_spin.setValue(int(value * 100))
            self.adjust3_spin.blockSignals(False)

    def _on_adjust3_changed(self, value: int):
        """Handle adjust3 change (third divider for seqblock)."""
        item = self._current_item
        if item is None or not isinstance(item, MetaSeqBlockItem):
            return
        old_val = item._adjust3
        item.set_adjust3(value / 100.0)
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

        if self.undo_stack:
            new_val = item._adjust3
            def apply():
                item._update_path()
                if hasattr(item, "_update_label_position"):
                    item._update_label_position()
            cmd = ChangeStyleCommand(item, "_adjust3", old_val, new_val, apply)
            self.undo_stack.push(cmd)

    def _on_divider_count_changed(self, value: int):
        """Handle divider count change for seqblock items."""
        item = self._current_item
        if item is None or not isinstance(item, MetaSeqBlockItem):
            return
        old_count = item._divider_count
        if value == old_count:
            return
        item.set_divider_count(value)
        item._notify_changed()
        # Refresh the property panel to show/hide adjust spinners
        pen_color = getattr(item, "pen_color", QColor("red"))
        self._setup_seqblock_controls(item, pen_color)


# Backwards compatibility alias
PropertyDock = PropertyPanel
