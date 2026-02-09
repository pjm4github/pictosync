"""
properties/dock.py

Property panel widget for editing selected item properties.
Loads UI from Qt Designer-generated properties_ui.py.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtWidgets import (
    QColorDialog,
    QGraphicsItem,
    QWidget,
)

from models import AnnotationMeta
from canvas.items import (
    MetaRectItem,
    MetaRoundedRectItem,
    MetaEllipseItem,
    MetaLineItem,
    MetaTextItem,
    MetaHexagonItem,
    MetaCylinderItem,
    MetaBlockArrowItem,
)

# Try to import the compiled UI, fall back to None if not available
try:
    from properties.properties_ui import Ui_PropertyPanel
    HAS_UI = True
except ImportError:
    HAS_UI = False
    Ui_PropertyPanel = None


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

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_item: Optional[QGraphicsItem] = None
        self._image_info: Dict[str, Any] = {}

        if HAS_UI:
            self._init_from_ui()
        else:
            self._init_fallback()

        self._connect_signals()
        self._set_enabled(False)
        self._set_color_rows_visible(False, False, False)
        self._set_extra_rows_visible(False, False, False, False, False, False)
        self._set_dash_pattern_visible(False)

    def _init_from_ui(self):
        """Initialize from Qt Designer UI file."""
        self.ui = Ui_PropertyPanel()
        self.ui.setupUi(self)

        # Create convenience references to widgets using naming convention
        # Tabs
        self.tabs = self.ui.tabs

        # Image tab widgets
        self.img_path = self.ui.lbl_img_path
        self.path_scroll = self.ui.scroll_img_path
        self.img_size = self.ui.lbl_img_size
        self.img_mode = self.ui.lbl_img_mode
        self.img_depth = self.ui.lbl_img_depth
        self.img_filesize = self.ui.lbl_img_filesize

        # Properties tab - Kind
        self.kind_label = self.ui.lbl_kind

        # Properties tab - Label row
        self.label_edit = self.ui.edit_label
        self.label_align = self.ui.combo_label_align
        self.label_size = self.ui.spin_label_size
        self.label_row = self.ui.row_label

        # Properties tab - Tech row
        self.tech_edit = self.ui.edit_tech
        self.tech_align = self.ui.combo_tech_align
        self.tech_size = self.ui.spin_tech_size
        self.tech_row = self.ui.row_tech

        # Properties tab - Note row
        self.note_edit = self.ui.edit_note
        self.note_align = self.ui.combo_note_align
        self.note_size = self.ui.spin_note_size
        self.note_row = self.ui.row_note

        # Properties tab - Color rows
        self.pen_color_btn = self.ui.btn_pen_color
        self.pen_color_preview = self.ui.lbl_pen_color_preview
        self.pen_row = self.ui.row_pen_color

        self.fill_color_btn = self.ui.btn_fill_color
        self.fill_color_preview = self.ui.lbl_fill_color_preview
        self.fill_row = self.ui.row_fill_color

        self.text_color_btn = self.ui.btn_text_color
        self.text_color_preview = self.ui.lbl_text_color_preview
        self.text_row = self.ui.row_text_color

        # Properties tab - Extra controls
        self.radius_spin = self.ui.spin_radius
        self.radius_row = self.ui.row_radius

        self.line_width_spin = self.ui.spin_line_width
        self.line_width_row = self.ui.row_line_width

        self.dash_combo = self.ui.combo_dash
        self.dash_row = self.ui.row_dash

        self.dash_length_spin = self.ui.spin_dash_length
        self.dash_solid_spin = self.ui.spin_dash_solid
        self.dash_pattern_row = self.ui.row_dash_pattern

        self.arrow_combo = self.ui.combo_arrow
        self.arrow_row = self.ui.row_arrow

        self.arrow_size_spin = self.ui.spin_arrow_size
        self.arrow_size_row = self.ui.row_arrow_size

        # Head length control (may not exist in UI file, create fallback)
        if hasattr(self.ui, 'spin_adjust2'):
            self.adjust2_spin = self.ui.spin_adjust2
            self.adjust2_row = self.ui.row_head_length
        else:
            # Create programmatically if not in UI file
            from PyQt6.QtWidgets import QSpinBox, QHBoxLayout, QWidget, QLabel, QFormLayout
            self.adjust2_row = QWidget()
            adjust2_l = QHBoxLayout(self.adjust2_row)
            adjust2_l.setContentsMargins(0, 0, 0, 0)
            self.adjust2_spin = QSpinBox()
            self.adjust2_spin.setRange(10, 500)
            self.adjust2_spin.setValue(15)
            self.adjust2_spin.setSuffix(" px")
            adjust2_l.addWidget(self.adjust2_spin)
            adjust2_l.addStretch(1)
            # Find the QFormLayout by traversing up from arrow_size_row
            parent = self.arrow_size_row.parentWidget()
            while parent:
                layout = parent.layout()
                if isinstance(layout, QFormLayout):
                    idx = layout.indexOf(self.arrow_size_row)
                    if idx >= 0:
                        row_num = layout.getWidgetPosition(self.arrow_size_row)[0]
                        layout.insertRow(row_num + 1, "Adjust 2:", self.adjust2_row)
                    break
                parent = parent.parentWidget()

        self.text_box_width_spin = self.ui.spin_text_box_width
        self.text_box_width_row = self.ui.row_text_box_width

        # Text layout controls (spacing and vertical alignment)
        self.text_spacing_combo = self.ui.combo_text_spacing
        self.text_valign_combo = self.ui.combo_text_valign

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

        # Corner radius control
        self.radius_row = QWidget()
        rad_l = QHBoxLayout(self.radius_row)
        rad_l.setContentsMargins(0, 0, 0, 0)
        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(0, 200)
        self.radius_spin.setValue(10)
        self.radius_spin.setSuffix(" px")
        rad_l.addWidget(self.radius_spin)
        rad_l.addStretch(1)

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

        # Head length control (for block arrows)
        self.adjust2_row = QWidget()
        adjust2_l = QHBoxLayout(self.adjust2_row)
        adjust2_l.setContentsMargins(0, 0, 0, 0)
        self.adjust2_spin = QSpinBox()
        self.adjust2_spin.setRange(10, 500)
        self.adjust2_spin.setValue(15)
        self.adjust2_spin.setSuffix(" px")
        self.adjust2_spin.setStyleSheet(compact_spin_with_suffix)
        adjust2_l.addWidget(self.adjust2_spin)
        adjust2_l.addStretch(1)

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
        form.addRow("Corner radius:", self.radius_row)
        form.addRow("Line width:", self.line_width_row)
        form.addRow("Line style:", self.dash_row)
        form.addRow("Dash pattern:", self.dash_pattern_row)
        form.addRow("Arrow:", self.arrow_row)
        form.addRow("Arrow size:", self.arrow_size_row)
        form.addRow("Adjust 2:", self.adjust2_row)
        form.addRow("Text box width:", self.text_box_width_row)

        props_layout.addStretch(1)
        self.tabs.addTab(props_tab, "Properties")

    def _connect_signals(self):
        """Connect all widget signals to handlers."""
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
        self.radius_spin.valueChanged.connect(self._on_radius_changed)
        self.line_width_spin.valueChanged.connect(self._on_line_width_changed)
        self.dash_combo.currentIndexChanged.connect(self._on_dash_changed)
        self.dash_length_spin.valueChanged.connect(self._on_dash_pattern_changed)
        self.dash_solid_spin.valueChanged.connect(self._on_dash_pattern_changed)
        self.arrow_combo.currentIndexChanged.connect(self._on_arrow_changed)
        self.arrow_size_spin.valueChanged.connect(self._on_arrow_size_changed)
        self.adjust2_spin.valueChanged.connect(self._on_adjust2_changed)
        self.text_box_width_spin.valueChanged.connect(self._on_text_box_width_changed)

        # Text layout controls
        self.text_spacing_combo.currentIndexChanged.connect(self._on_text_spacing_changed)
        self.text_valign_combo.currentIndexChanged.connect(self._on_text_valign_changed)

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
        self.radius_spin.setEnabled(enabled)
        self.line_width_spin.setEnabled(enabled)
        self.dash_combo.setEnabled(enabled)
        self.dash_length_spin.setEnabled(enabled)
        self.dash_solid_spin.setEnabled(enabled)
        self.arrow_combo.setEnabled(enabled)
        self.arrow_size_spin.setEnabled(enabled)
        self.adjust2_spin.setEnabled(enabled)
        self.text_box_width_spin.setEnabled(enabled)
        self.text_spacing_combo.setEnabled(enabled)
        self.text_valign_combo.setEnabled(enabled)

    def _set_extra_rows_visible(self, radius: bool, line_width: bool, dash: bool, arrow: bool, arrow_size: bool, text_box_width: bool = False, text_layout: bool = False, adjust2: bool = False):
        """Show or hide extra control rows."""
        self.radius_row.setVisible(radius)
        self.radius_spin.setVisible(radius)
        self.line_width_row.setVisible(line_width)
        # text_box_width_row contains both text_box_width spin AND text layout controls
        # Show the row if either text_box_width or text_layout is needed
        self.text_box_width_row.setVisible(text_box_width or text_layout)
        # But only show the text_box_width spin/label for line items
        self.text_box_width_spin.setVisible(text_box_width)
        if hasattr(self.ui, 'label_text_box_width_title'):
            self.ui.label_text_box_width_title.setVisible(text_box_width)
        self.line_width_spin.setVisible(line_width)
        self.dash_row.setVisible(dash)
        self.dash_combo.setVisible(dash)
        self.arrow_row.setVisible(arrow)
        self.arrow_combo.setVisible(arrow)
        self.arrow_size_row.setVisible(arrow_size)
        self.arrow_size_spin.setVisible(arrow_size)
        self.adjust2_row.setVisible(adjust2)
        self.adjust2_spin.setVisible(adjust2)

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
        """Update a color preview label."""
        r, g, b, a = color.red(), color.green(), color.blue(), color.alpha()
        rgba_str = f"rgba({r}, {g}, {b}, {a / 255.0:.2f})"
        lbl.setStyleSheet(f"background-color: {rgba_str}; border: 1px solid #444;")
        lbl.update()

    def set_item(self, item: Optional[QGraphicsItem]):
        """Set the item to display/edit in the property panel."""
        self._current_item = item
        if item is None or not hasattr(item, "meta"):
            self.kind_label.setText("-")
            self.label_edit.setText("")
            self.tech_edit.setText("")
            self.note_edit.setText("")
            self._set_enabled(False)
            self._set_text_rows_visible(True, True, True)
            self._set_color_rows_visible(False, False, False)
            self._set_extra_rows_visible(False, False, False, False, False, text_box_width=False, text_layout=False)
            self._set_dash_pattern_visible(False)
            return

        # Switch to Properties tab when an item is selected
        self.tabs.setCurrentIndex(1)

        meta: AnnotationMeta = getattr(item, "meta")
        self.kind_label.setText(meta.kind)

        # Block signals while setting values
        self._block_text_signals(True)

        self.label_edit.setText(meta.label)
        self.tech_edit.setText(meta.tech)
        self.note_edit.setText(meta.note)

        # Set alignment and font size values
        align_map = {"left": 0, "center": 1, "right": 2}
        self.label_align.setCurrentIndex(align_map.get(meta.label_align, 1))
        self.label_size.setValue(meta.label_size)
        self.tech_align.setCurrentIndex(align_map.get(meta.tech_align, 1))
        self.tech_size.setValue(meta.tech_size)
        self.note_align.setCurrentIndex(align_map.get(meta.note_align, 1))
        self.note_size.setValue(meta.note_size)

        self._block_text_signals(False)
        self._set_enabled(True)

        kind = meta.kind
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
        else:
            self._set_color_rows_visible(False, False, False)
            self._set_extra_rows_visible(False, False, False, False, False, text_box_width=False, text_layout=False)
            self._set_dash_pattern_visible(False)

    def _setup_rect_controls(self, item, pen_color):
        """Configure controls for rect items."""
        self._set_text_rows_visible(True, True, True)
        self._set_color_rows_visible(True, True, True)
        self._set_extra_rows_visible(False, True, True, False, False, text_box_width=False, text_layout=True)
        self._set_preview(self.pen_color_preview, pen_color)
        self._set_preview(self.fill_color_preview, getattr(item, "brush_color", QColor(0, 0, 0, 0)))
        self._set_preview(self.text_color_preview, getattr(item, "text_color", pen_color))
        self._setup_line_style_controls(item)
        self._setup_text_layout_controls(item)

    def _setup_ellipse_controls(self, item, pen_color):
        """Configure controls for ellipse items."""
        self._set_text_rows_visible(True, True, True)
        self._set_color_rows_visible(True, True, True)
        self._set_extra_rows_visible(False, True, True, False, False, text_box_width=False, text_layout=True)
        self._set_preview(self.pen_color_preview, pen_color)
        self._set_preview(self.fill_color_preview, getattr(item, "brush_color", QColor(0, 0, 0, 0)))
        self._set_preview(self.text_color_preview, getattr(item, "text_color", pen_color))
        self._setup_line_style_controls(item)
        self._setup_text_layout_controls(item)

    def _setup_roundedrect_controls(self, item, pen_color):
        """Configure controls for rounded rect items."""
        self._set_text_rows_visible(True, True, True)
        self._set_color_rows_visible(True, True, True)
        self._set_extra_rows_visible(True, True, True, False, False, text_box_width=False, text_layout=True)
        self._set_preview(self.pen_color_preview, pen_color)
        self._set_preview(self.fill_color_preview, getattr(item, "brush_color", QColor(0, 0, 0, 0)))
        self._set_preview(self.text_color_preview, getattr(item, "text_color", pen_color))
        self.radius_spin.blockSignals(True)
        self.radius_spin.setSuffix(" px")  # Reset suffix for rounded rect
        self.radius_spin.setRange(0, 200)  # Reset range
        self.radius_spin.setValue(int(getattr(item, "_adjust1", 10)))
        self.radius_spin.blockSignals(False)
        self._setup_line_style_controls(item)
        self._setup_text_layout_controls(item)

    def _setup_line_controls(self, item, pen_color):
        """Configure controls for line items."""
        self._set_text_rows_visible(True, True, True)
        self._set_color_rows_visible(True, False, True)
        self._set_extra_rows_visible(False, True, True, True, True, text_box_width=True, text_layout=True)
        self._set_preview(self.pen_color_preview, pen_color)
        self._set_preview(self.text_color_preview, getattr(item, "text_color", pen_color))
        self._setup_line_style_controls(item)
        self._setup_text_layout_controls(item)

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
        """Configure controls for text items."""
        self._set_text_rows_visible(False, False, True)
        self._set_color_rows_visible(False, False, True)
        self._set_extra_rows_visible(False, False, False, False, False, text_box_width=False, text_layout=False)
        self._set_dash_pattern_visible(False)
        self._set_preview(self.text_color_preview, getattr(item, "text_color", pen_color))
        if isinstance(item, MetaTextItem):
            self.note_edit.setText(item.toPlainText())

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

        self._set_dash_pattern_visible(dash_style == "dashed")
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

        # Text spacing (0, 0.5, 1, 1.5, 2)
        spacing = getattr(item.meta, "text_spacing", 0.0)
        spacing_map = {0.0: 0, 0.5: 1, 1.0: 2, 1.5: 3, 2.0: 4}
        spacing_index = spacing_map.get(spacing, 0)
        self.text_spacing_combo.blockSignals(True)
        self.text_spacing_combo.setCurrentIndex(spacing_index)
        self.text_spacing_combo.blockSignals(False)

        # Vertical alignment (top, middle, bottom)
        valign = getattr(item.meta, "text_valign", "top")
        valign_map = {"top": 0, "middle": 1, "bottom": 2}
        valign_index = valign_map.get(valign, 0)
        self.text_valign_combo.blockSignals(True)
        self.text_valign_combo.setCurrentIndex(valign_index)
        self.text_valign_combo.blockSignals(False)

    def _block_text_signals(self, block: bool):
        """Block or unblock signals from text formatting controls."""
        self.label_align.blockSignals(block)
        self.label_size.blockSignals(block)
        self.tech_align.blockSignals(block)
        self.tech_size.blockSignals(block)
        self.note_align.blockSignals(block)
        self.note_size.blockSignals(block)

    def _apply_changes(self):
        """Apply changes from the form to the current item."""
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        meta: AnnotationMeta = getattr(item, "meta")
        meta.label = self.label_edit.text().strip()
        meta.tech = self.tech_edit.text().strip()
        meta.note = self.note_edit.text().strip()

        align_values = ["left", "center", "right"]
        meta.label_align = align_values[self.label_align.currentIndex()]
        meta.label_size = self.label_size.value()
        meta.tech_align = align_values[self.tech_align.currentIndex()]
        meta.tech_size = self.tech_size.value()
        meta.note_align = align_values[self.note_align.currentIndex()]
        meta.note_size = self.note_size.value()

        setattr(item, "meta", meta)

        if isinstance(item, MetaTextItem):
            if not getattr(item, '_editing', False) and item.toPlainText() != meta.note:
                item.setPlainText(meta.note)

        if hasattr(item, "_update_label_text"):
            item._update_label_text()

        if hasattr(item, "_notify_changed"):
            item._notify_changed()

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
        initial = getattr(item, "pen_color", QColor("red"))
        c = self._pick_color(initial, "Pick Border (Pen) Color")
        if c is None:
            return
        setattr(item, "pen_color", c)
        # Use item's apply method to preserve dash style
        if isinstance(item, MetaLineItem):
            item._apply_pen()
        elif isinstance(item, (MetaRectItem, MetaEllipseItem, MetaRoundedRectItem)):
            item._apply_pen_brush()
        self._set_preview(self.pen_color_preview, c)
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

    def pick_fill_color(self):
        """Pick fill (brush) color."""
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        initial = getattr(item, "brush_color", QColor(0, 0, 0, 0))
        c = self._pick_color(initial, "Pick Fill (Brush) Color")
        if c is None:
            return
        setattr(item, "brush_color", c)
        if isinstance(item, (MetaRectItem, MetaEllipseItem, MetaRoundedRectItem)):
            item.setBrush(QBrush(c))
        self._set_preview(self.fill_color_preview, c)
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

    def pick_text_color(self):
        """Pick text color."""
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        initial = getattr(item, "text_color", QColor("yellow"))
        c = self._pick_color(initial, "Pick Text Color")
        if c is None:
            return
        setattr(item, "text_color", c)
        if isinstance(item, MetaTextItem):
            item._apply_text_style()
        if hasattr(item, "_update_label_text"):
            item._update_label_text()
        self._set_preview(self.text_color_preview, c)
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

    def _on_radius_changed(self, value: int):
        """Handle corner radius / adjust1 change."""
        item = self._current_item
        if item is None:
            return

        if isinstance(item, MetaRoundedRectItem):
            item.set_adjust1(float(value))  # Rounded rect uses pixels directly
        elif isinstance(item, MetaHexagonItem):
            item.set_adjust1(value / 100.0)  # Convert percentage to ratio
        elif isinstance(item, MetaCylinderItem):
            item.set_adjust1(value / 100.0)
        elif isinstance(item, MetaBlockArrowItem):
            item.set_adjust1(value / 100.0)
        else:
            return

        if hasattr(item, "_notify_changed"):
            item._notify_changed()

    def _on_line_width_changed(self, value: int):
        """Handle line width change."""
        item = self._current_item
        if item is None or not hasattr(item, "pen_width"):
            return
        item.pen_width = value
        if hasattr(item, "_apply_pen"):
            item._apply_pen()
        elif hasattr(item, "_apply_pen_brush"):
            item._apply_pen_brush()
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

    def _on_dash_changed(self, index: int):
        """Handle line dash style change."""
        item = self._current_item
        if item is None or not hasattr(item, "line_dash"):
            return
        dash_styles = ["solid", "dashed"]
        if 0 <= index < len(dash_styles):
            item.line_dash = dash_styles[index]
            is_dashed = dash_styles[index] == "dashed"
            self._set_dash_pattern_visible(is_dashed)
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

    def _on_dash_pattern_changed(self, value: int):
        """Handle custom dash pattern change."""
        item = self._current_item
        if item is None or not hasattr(item, "line_dash"):
            return
        item.dash_pattern_length = float(self.dash_length_spin.value())
        item.dash_solid_percent = float(self.dash_solid_spin.value())
        if hasattr(item, "_apply_pen"):
            item._apply_pen()
        elif hasattr(item, "_apply_pen_brush"):
            item._apply_pen_brush()
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

    def _on_arrow_changed(self, index: int):
        """Handle arrow mode change."""
        item = self._current_item
        if item is None or not isinstance(item, MetaLineItem):
            return
        arrow_modes = ["none", "start", "end", "both"]
        if 0 <= index < len(arrow_modes):
            item.set_arrow_mode(arrow_modes[index])
            if hasattr(item, "_notify_changed"):
                item._notify_changed()

    def _on_arrow_size_changed(self, value: int):
        """Handle arrow size change."""
        item = self._current_item
        if item is None or not isinstance(item, MetaLineItem):
            return
        item.arrow_size = float(value)
        item.update()
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

    def _on_adjust2_changed(self, value: int):
        """Handle block arrow adjust2 (head length) change."""
        item = self._current_item
        if item is None or not isinstance(item, MetaBlockArrowItem):
            return
        item.set_adjust2(float(value))
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

    def _on_text_box_width_changed(self, value: int):
        """Handle text box width change for line items."""
        item = self._current_item
        if item is None or not isinstance(item, MetaLineItem):
            return
        if not hasattr(item, "meta"):
            return
        item.meta.text_box_width = float(value)
        item.prepareGeometryChange()
        if hasattr(item, "_update_label_text"):
            item._update_label_text()
        item.update()
        if hasattr(item, "_notify_changed"):
            item._notify_changed()

    def _on_text_spacing_changed(self, index: int):
        """Handle text spacing change."""
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        # Spacing values: 0, 0.5, 1, 1.5, 2
        spacing_values = [0.0, 0.5, 1.0, 1.5, 2.0]
        if 0 <= index < len(spacing_values):
            item.meta.text_spacing = spacing_values[index]
            if hasattr(item, "_update_label_text"):
                item._update_label_text()
            if hasattr(item, "_notify_changed"):
                item._notify_changed()

    def _on_text_valign_changed(self, index: int):
        """Handle text vertical alignment change."""
        item = self._current_item
        if item is None or not hasattr(item, "meta"):
            return
        # Valign values: top, middle, bottom
        valign_values = ["top", "middle", "bottom"]
        if 0 <= index < len(valign_values):
            item.meta.text_valign = valign_values[index]
            if hasattr(item, "_update_label_position"):
                item._update_label_position()
            item.update()
            if hasattr(item, "_notify_changed"):
                item._notify_changed()

    def update_radius_display(self, item, radius: float):
        """Deprecated: Use update_adjust1_display instead."""
        # Keep for backwards compatibility
        self.update_adjust1_display(item, radius)

    def _setup_hexagon_controls(self, item, pen_color):
        """Configure controls for hexagon items."""
        self._set_text_rows_visible(True, True, True)
        self._set_color_rows_visible(True, True, True)
        # Reuse radius row for adjust1
        self._set_extra_rows_visible(True, True, True, False, False, text_box_width=False, text_layout=True)
        self._set_preview(self.pen_color_preview, pen_color)
        self._set_preview(self.fill_color_preview, getattr(item, "brush_color", QColor(0, 0, 0, 0)))
        self._set_preview(self.text_color_preview, getattr(item, "text_color", pen_color))
        # Use radius spinbox for adjust1 (show as percentage)
        adjust1 = getattr(item, "_adjust1", 0.25)
        self.radius_spin.blockSignals(True)
        self.radius_spin.setValue(int(adjust1 * 100))  # Show as percentage
        self.radius_spin.setSuffix(" %")
        self.radius_spin.setRange(0, 50)
        self.radius_spin.blockSignals(False)
        self._setup_line_style_controls(item)
        self._setup_text_layout_controls(item)

    def _setup_cylinder_controls(self, item, pen_color):
        """Configure controls for cylinder items."""
        self._set_text_rows_visible(True, True, True)
        self._set_color_rows_visible(True, True, True)
        # Reuse radius row for adjust1
        self._set_extra_rows_visible(True, True, True, False, False, text_box_width=False, text_layout=True)
        self._set_preview(self.pen_color_preview, pen_color)
        self._set_preview(self.fill_color_preview, getattr(item, "brush_color", QColor(0, 0, 0, 0)))
        self._set_preview(self.text_color_preview, getattr(item, "text_color", pen_color))
        # Use radius spinbox for adjust1 (show as percentage)
        adjust1 = getattr(item, "_adjust1", 0.15)
        self.radius_spin.blockSignals(True)
        self.radius_spin.setValue(int(adjust1 * 100))
        self.radius_spin.setSuffix(" %")
        self.radius_spin.setRange(10, 50)
        self.radius_spin.blockSignals(False)
        self._setup_line_style_controls(item)
        self._setup_text_layout_controls(item)

    def _setup_blockarrow_controls(self, item, pen_color):
        """Configure controls for block arrow items."""
        self._set_text_rows_visible(True, True, True)
        self._set_color_rows_visible(True, True, True)
        # Reuse radius row for adjust1, show adjust2 row
        self._set_extra_rows_visible(True, True, True, False, False, text_box_width=False, text_layout=True, adjust2=True)
        self._set_preview(self.pen_color_preview, pen_color)
        self._set_preview(self.fill_color_preview, getattr(item, "brush_color", QColor(0, 0, 0, 0)))
        self._set_preview(self.text_color_preview, getattr(item, "text_color", pen_color))
        # Use radius spinbox for adjust1 (show as percentage)
        adjust1 = getattr(item, "_adjust1", 0.5)
        self.radius_spin.blockSignals(True)
        self.radius_spin.setValue(int(adjust1 * 100))
        self.radius_spin.setSuffix(" %")
        self.radius_spin.setRange(20, 90)
        self.radius_spin.blockSignals(False)
        # Adjust2 control
        adjust2 = getattr(item, "_adjust2", 15)
        self.adjust2_spin.blockSignals(True)
        self.adjust2_spin.setValue(int(adjust2))
        self.adjust2_spin.blockSignals(False)
        self._setup_line_style_controls(item)
        self._setup_text_layout_controls(item)

    def update_adjust1_display(self, item, value: float):
        """Update the adjust1 spinbox display when it changes via canvas handle."""
        if self._current_item is not item:
            return
        self.radius_spin.blockSignals(True)
        if isinstance(item, MetaRoundedRectItem):
            # Rounded rect uses pixels directly
            self.radius_spin.setValue(int(value))
        elif isinstance(item, (MetaHexagonItem, MetaCylinderItem, MetaBlockArrowItem)):
            # Other shapes use percentage (0-1 ratio)
            self.radius_spin.setValue(int(value * 100))
        self.radius_spin.blockSignals(False)

    def update_adjust2_display(self, item, value: float):
        """Update the adjust2 spinbox display when it changes via canvas handle."""
        if self._current_item is item and isinstance(item, MetaBlockArrowItem):
            self.adjust2_spin.blockSignals(True)
            self.adjust2_spin.setValue(int(value))
            self.adjust2_spin.blockSignals(False)


# Backwards compatibility alias
PropertyDock = PropertyPanel
