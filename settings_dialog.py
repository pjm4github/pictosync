"""
settings_dialog.py

Comprehensive settings dialog for PictoSync application.
Organizes all settings into logical tabs and groups.
"""

from __future__ import annotations

import os
import shutil
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QWidget,
    QGroupBox,
    QFormLayout,
    QLabel,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QLineEdit,
    QCheckBox,
    QPushButton,
    QDialogButtonBox,
    QColorDialog,
    QFileDialog,
    QScrollArea,
    QFrame,
    QListWidget,
    QRadioButton,
    QButtonGroup,
    QSizePolicy,
)
from PyQt6.QtGui import QColor

if TYPE_CHECKING:
    from settings import SettingsManager

from styles import STYLES

# Canvas item kinds with display names — order matches the toolbar
CANVAS_ITEM_KINDS = [
    ("rect",        "Rectangle"),
    ("roundedrect", "Rounded Rectangle"),
    ("ellipse",     "Ellipse"),
    ("line",        "Line"),
    ("curve",       "Curve"),
    ("orthocurve",  "Ortho Curve"),
    ("text",        "Text"),
    ("hexagon",     "Hexagon"),
    ("cylinder",    "Cylinder"),
    ("blockarrow",  "Block Arrow"),
    ("polygon",     "Polygon"),
    ("isocube",     "Iso Cube"),
    ("seqblock",    "Sequence Block"),
]


class ColorButton(QPushButton):
    """A button that displays and allows selection of a color."""

    def __init__(self, color: str = "#000000", parent=None):
        super().__init__(parent)
        self._color = color
        self._update_style()
        self.clicked.connect(self._pick_color)
        self.setFixedWidth(60)

    def _update_style(self):
        """Update button appearance to show current color."""
        # Determine text color based on luminance
        qc = QColor(self._color)
        luminance = 0.299 * qc.red() + 0.587 * qc.green() + 0.114 * qc.blue()
        text_color = "#000000" if luminance > 128 else "#FFFFFF"
        self.setStyleSheet(
            f"background-color: {self._color}; color: {text_color}; "
            f"border: 1px solid #888; padding: 2px 8px;"
        )
        self.setText(self._color)

    def _pick_color(self):
        """Open color picker dialog."""
        color = QColorDialog.getColor(QColor(self._color), self, "Select Color")
        if color.isValid():
            self._color = color.name()
            self._update_style()

    def color(self) -> str:
        """Get current color as hex string."""
        return self._color

    def setColor(self, color: str):
        """Set current color from hex string."""
        self._color = color
        self._update_style()


class SettingsDialog(QDialog):
    """
    Comprehensive settings dialog with tabbed organization.

    Tabs:
    - General: Theme selection
    - Editor: Font, line numbers, folding, syntax highlighting
    - Canvas: Handles, shapes, lines, selection, z-order, zoom
    - Alignment: Detection, color matching, scoring
    - Text Defaults: Default text formatting for annotations
    """

    def __init__(self, settings_manager: "SettingsManager", parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self._parent_window = parent  # Store parent for theme application
        self.setWindowTitle("PictoSync Settings")
        self.setMinimumSize(650, 520)
        self.resize(760, 620)

        # "user" | "system" | "builtin" — which layer is currently displayed
        self._active_layer: str = "user"

        # Store original settings for cancel (merged view)
        self._original_settings = self._snapshot_settings()

        self._setup_ui()
        self._load_settings()

        # Wheel must not change spin/combo values unless the widget has focus.
        from utils import install_wheel_guard
        install_wheel_guard(self)

    def _setup_ui(self):
        """Create the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # ── Layer selector banner ─────────────────────────────────────────
        layer_group = QGroupBox("Settings Layer")
        layer_outer = QVBoxLayout(layer_group)
        layer_outer.setContentsMargins(6, 4, 6, 4)
        layer_outer.setSpacing(2)

        # Radio buttons row
        radio_row = QHBoxLayout()
        radio_row.setSpacing(16)
        self._rb_builtin = QRadioButton("Built-in (read-only)")
        self._rb_system  = QRadioButton("System")
        self._rb_user    = QRadioButton("User")
        self._rb_user.setChecked(True)

        # Force Fusion style so ::indicator:checked CSS is respected on Windows
        # (QWindowsVistaStyle draws indicators via native UxTheme, ignoring CSS background-color)
        from PyQt6.QtWidgets import QStyleFactory
        _fusion = QStyleFactory.create("Fusion")
        if _fusion:
            self._rb_builtin.setStyle(_fusion)
            self._rb_system.setStyle(_fusion)
            self._rb_user.setStyle(_fusion)

        self._layer_btn_group = QButtonGroup(self)
        self._layer_btn_group.addButton(self._rb_builtin, 0)
        self._layer_btn_group.addButton(self._rb_system,  1)
        self._layer_btn_group.addButton(self._rb_user,    2)
        self._layer_btn_group.idClicked.connect(self._on_layer_changed)

        radio_row.addWidget(self._rb_builtin)
        radio_row.addWidget(self._rb_system)
        radio_row.addWidget(self._rb_user)
        radio_row.addStretch()
        layer_outer.addLayout(radio_row)

        # File path + status label
        self._layer_path_label = QLabel()
        self._layer_path_label.setStyleSheet("font-size: 8pt; color: #888;")
        self._layer_path_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self._layer_path_label.setWordWrap(True)
        layer_outer.addWidget(self._layer_path_label)

        layout.addWidget(layer_group)
        self._update_layer_path_label()

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabBar::tab { padding: 4px 10px; }")
        layout.addWidget(self.tabs)

        # Create tabs
        self.tabs.addTab(self._create_general_tab(), "General")
        self.tabs.addTab(self._create_editor_tab(), "JSON Editor")
        self.tabs.addTab(self._create_canvas_tab(), "Canvas")
        self.tabs.addTab(self._create_alignment_tab(), "Alignment")
        self.tabs.addTab(self._create_item_defaults_tab(), "Item Defaults")
        self.tabs.addTab(self._create_external_tools_tab(), "External Tools")

        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply |
            QDialogButtonBox.StandardButton.RestoreDefaults
        )
        button_box.accepted.connect(self._on_ok)
        button_box.rejected.connect(self._on_cancel)
        self._apply_btn = button_box.button(QDialogButtonBox.StandardButton.Apply)
        self._apply_btn.clicked.connect(self._on_apply)
        button_box.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self._on_restore_defaults)
        layout.addWidget(button_box)

    def _create_scrollable_tab(self, content_widget: QWidget) -> QScrollArea:
        """Wrap a widget in a scroll area for tabs with lots of content."""
        scroll = QScrollArea()
        scroll.setWidget(content_widget)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        return scroll

    # =========================================================================
    # Layer management
    # =========================================================================

    def _update_layer_path_label(self):
        """Refresh the path/status label under the layer radio buttons."""
        from pathlib import Path as _Path
        mgr = self.settings_manager
        if self._active_layer == "builtin":
            self._layer_path_label.setText("Built-in defaults (no file — Python dataclass defaults)")
        elif self._active_layer == "system":
            p = mgr.system_settings_file
            exists = "✓ exists" if _Path(p).exists() else "✗ not found"
            self._layer_path_label.setText(f"System:  {p}   [{exists}]")
        else:
            p = mgr.user_settings_file
            exists = "✓ exists" if _Path(p).exists() else "✗ not found"
            self._layer_path_label.setText(f"User:    {p}   [{exists}]")

    def _on_layer_changed(self, btn_id: int):
        """Handle layer radio-button selection change."""
        layer = {0: "builtin", 1: "system", 2: "user"}.get(btn_id, "user")
        self._active_layer = layer
        self._update_layer_path_label()


        # Reload widgets from the selected layer
        if layer == "builtin":
            from settings import AppSettings
            s = AppSettings()
        elif layer == "system":
            s = self.settings_manager.load_layer(self.settings_manager.system_settings_file)
        else:
            s = self.settings_manager.load_layer(self.settings_manager.user_settings_file)

        self._load_settings(s)

        # Built-in layer is read-only: disable Apply
        self._apply_btn.setEnabled(layer != "builtin")

    # =========================================================================
    # General Tab
    # =========================================================================

    def _create_general_tab(self) -> QWidget:
        """Create the General settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Theme group
        theme_group = QGroupBox("Appearance")
        theme_layout = QFormLayout(theme_group)
        theme_layout.setContentsMargins(6, 4, 6, 4)
        theme_layout.setSpacing(4)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(STYLES.keys()))
        theme_layout.addRow("Theme:", self.theme_combo)

        layout.addWidget(theme_group)

        # Workspace group
        workspace_group = QGroupBox("Workspace")
        workspace_layout = QFormLayout(workspace_group)
        workspace_layout.setContentsMargins(6, 4, 6, 4)
        workspace_layout.setSpacing(4)

        workspace_row = QHBoxLayout()
        self.workspace_dir_edit = QLineEdit()
        self.workspace_dir_edit.setPlaceholderText("~/Documents/PictoSync (default)")
        workspace_row.addWidget(self.workspace_dir_edit)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_workspace_dir)
        workspace_row.addWidget(browse_btn)
        workspace_layout.addRow("Project Directory:", workspace_row)

        self.pptx_source_dir_cb = QCheckBox("Export PPTX to source file directory")
        workspace_layout.addRow("", self.pptx_source_dir_cb)

        layout.addWidget(workspace_group)

        # Gemini AI group
        gemini_group = QGroupBox("Gemini AI")
        gemini_layout = QVBoxLayout(gemini_group)
        gemini_layout.setContentsMargins(6, 4, 6, 4)
        gemini_layout.setSpacing(4)

        model_label = QLabel("Available Models:")
        gemini_layout.addWidget(model_label)

        self.gemini_model_list = QListWidget()
        self.gemini_model_list.setMaximumHeight(120)
        gemini_layout.addWidget(self.gemini_model_list)

        model_btn_row = QHBoxLayout()
        self.gemini_add_btn = QPushButton("Add...")
        self.gemini_add_btn.clicked.connect(self._add_gemini_model)
        model_btn_row.addWidget(self.gemini_add_btn)

        self.gemini_remove_btn = QPushButton("Remove")
        self.gemini_remove_btn.clicked.connect(self._remove_gemini_model)
        model_btn_row.addWidget(self.gemini_remove_btn)
        model_btn_row.addStretch()
        gemini_layout.addLayout(model_btn_row)

        default_row = QFormLayout()
        self.gemini_default_combo = QComboBox()
        default_row.addRow("Default Model:", self.gemini_default_combo)
        gemini_layout.addLayout(default_row)

        layout.addWidget(gemini_group)
        layout.addStretch()

        return widget

    def _browse_workspace_dir(self):
        """Open a directory picker for the workspace directory."""
        current = self.workspace_dir_edit.text()
        if not current:
            from settings import get_settings
            current = str(get_settings().get_workspace_dir())
        directory = QFileDialog.getExistingDirectory(
            self, "Select Workspace Directory", current
        )
        if directory:
            self.workspace_dir_edit.setText(directory)

    def _add_gemini_model(self):
        """Prompt user for a new model name and add it."""
        from PyQt6.QtWidgets import QInputDialog

        name, ok = QInputDialog.getText(self, "Add Model", "Model name:")
        if ok and name.strip():
            name = name.strip()
            existing = [
                self.gemini_model_list.item(i).text()
                for i in range(self.gemini_model_list.count())
            ]
            if name not in existing:
                self.gemini_model_list.addItem(name)
                self._sync_gemini_default_combo()

    def _remove_gemini_model(self):
        """Remove the selected model from the list."""
        row = self.gemini_model_list.currentRow()
        if row >= 0:
            self.gemini_model_list.takeItem(row)
            self._sync_gemini_default_combo()

    def _sync_gemini_default_combo(self):
        """Sync the default model combo box with the model list."""
        current_default = self.gemini_default_combo.currentText()
        self.gemini_default_combo.clear()
        for i in range(self.gemini_model_list.count()):
            self.gemini_default_combo.addItem(self.gemini_model_list.item(i).text())
        idx = self.gemini_default_combo.findText(current_default)
        if idx >= 0:
            self.gemini_default_combo.setCurrentIndex(idx)

    # =========================================================================
    # Editor Tab
    # =========================================================================

    def _create_editor_tab(self) -> QWidget:
        """Create the Editor settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Font group
        font_group = QGroupBox("Font")
        font_layout = QFormLayout(font_group)

        self.editor_font_family = QLineEdit()
        font_layout.addRow("Font Family:", self.editor_font_family)

        self.editor_font_size = QSpinBox()
        self.editor_font_size.setRange(6, 72)
        font_layout.addRow("Font Size:", self.editor_font_size)

        self.editor_tab_width = QSpinBox()
        self.editor_tab_width.setRange(1, 16)
        font_layout.addRow("Tab Width:", self.editor_tab_width)

        layout.addWidget(font_group)

        # Line Numbers group
        ln_group = QGroupBox("Line Numbers")
        ln_layout = QFormLayout(ln_group)

        self.editor_ln_left_margin = QSpinBox()
        self.editor_ln_left_margin.setRange(0, 50)
        ln_layout.addRow("Left Margin:", self.editor_ln_left_margin)

        self.editor_ln_right_margin = QSpinBox()
        self.editor_ln_right_margin.setRange(0, 50)
        ln_layout.addRow("Right Margin:", self.editor_ln_right_margin)

        self.editor_ln_highlight_bar = QSpinBox()
        self.editor_ln_highlight_bar.setRange(0, 20)
        ln_layout.addRow("Highlight Bar Width:", self.editor_ln_highlight_bar)

        layout.addWidget(ln_group)

        # Folding group
        fold_group = QGroupBox("Code Folding")
        fold_layout = QFormLayout(fold_group)

        self.editor_fold_width = QSpinBox()
        self.editor_fold_width.setRange(8, 30)
        fold_layout.addRow("Fold Area Width:", self.editor_fold_width)

        layout.addWidget(fold_group)

        # Syntax Highlighting group
        syntax_group = QGroupBox("Syntax Highlighting")
        syntax_layout = QFormLayout(syntax_group)

        self.syntax_key_color = ColorButton()
        self.syntax_key_bold = QCheckBox("Bold")
        key_row = QHBoxLayout()
        key_row.addWidget(self.syntax_key_color)
        key_row.addWidget(self.syntax_key_bold)
        key_row.addStretch()
        syntax_layout.addRow("JSON Keys:", key_row)

        self.syntax_string_color = ColorButton()
        syntax_layout.addRow("Strings:", self.syntax_string_color)

        self.syntax_number_color = ColorButton()
        syntax_layout.addRow("Numbers:", self.syntax_number_color)

        self.syntax_keyword_color = ColorButton()
        self.syntax_keyword_bold = QCheckBox("Bold")
        kw_row = QHBoxLayout()
        kw_row.addWidget(self.syntax_keyword_color)
        kw_row.addWidget(self.syntax_keyword_bold)
        kw_row.addStretch()
        syntax_layout.addRow("Keywords:", kw_row)

        self.syntax_brace_color = ColorButton()
        self.syntax_brace_bold = QCheckBox("Bold")
        brace_row = QHBoxLayout()
        brace_row.addWidget(self.syntax_brace_color)
        brace_row.addWidget(self.syntax_brace_bold)
        brace_row.addStretch()
        syntax_layout.addRow("Braces:", brace_row)

        layout.addWidget(syntax_group)
        layout.addStretch()

        return self._create_scrollable_tab(widget)

    # =========================================================================
    # Canvas Tab
    # =========================================================================

    def _create_canvas_tab(self) -> QWidget:
        """Create the Canvas settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Handles group
        handles_group = QGroupBox("Resize Handles")
        handles_layout = QFormLayout(handles_group)

        self.canvas_handle_size = QDoubleSpinBox()
        self.canvas_handle_size.setRange(2.0, 20.0)
        self.canvas_handle_size.setSingleStep(0.5)
        handles_layout.addRow("Handle Size:", self.canvas_handle_size)

        self.canvas_hit_distance = QDoubleSpinBox()
        self.canvas_hit_distance.setRange(2.0, 30.0)
        self.canvas_hit_distance.setSingleStep(0.5)
        handles_layout.addRow("Hit Distance:", self.canvas_hit_distance)

        self.canvas_handle_border = ColorButton()
        handles_layout.addRow("Border Color:", self.canvas_handle_border)

        self.canvas_handle_fill = ColorButton()
        handles_layout.addRow("Fill Color:", self.canvas_handle_fill)

        layout.addWidget(handles_group)

        # Shapes group
        shapes_group = QGroupBox("Shapes")
        shapes_layout = QFormLayout(shapes_group)

        self.canvas_min_size = QDoubleSpinBox()
        self.canvas_min_size.setRange(1.0, 50.0)
        shapes_layout.addRow("Minimum Size:", self.canvas_min_size)

        self.canvas_rounded_radius = QSpinBox()
        self.canvas_rounded_radius.setRange(0, 50)
        shapes_layout.addRow("Default Rounded Radius:", self.canvas_rounded_radius)

        self.canvas_dash_length = QDoubleSpinBox()
        self.canvas_dash_length.setRange(5.0, 100.0)
        shapes_layout.addRow("Dash Pattern Length:", self.canvas_dash_length)

        self.canvas_dash_solid = QDoubleSpinBox()
        self.canvas_dash_solid.setRange(1.0, 99.0)
        self.canvas_dash_solid.setSuffix("%")
        shapes_layout.addRow("Dash Solid Percent:", self.canvas_dash_solid)

        layout.addWidget(shapes_group)

        # Lines group
        lines_group = QGroupBox("Lines")
        lines_layout = QFormLayout(lines_group)

        self.canvas_line_hit_width = QDoubleSpinBox()
        self.canvas_line_hit_width.setRange(5.0, 50.0)
        lines_layout.addRow("Hit Area Width:", self.canvas_line_hit_width)

        self.canvas_arrow_multiplier = QSpinBox()
        self.canvas_arrow_multiplier.setRange(1, 10)
        lines_layout.addRow("Arrow Min Multiplier:", self.canvas_arrow_multiplier)

        self.canvas_min_text_box = QDoubleSpinBox()
        self.canvas_min_text_box.setRange(10.0, 100.0)
        lines_layout.addRow("Min Text Box Size:", self.canvas_min_text_box)

        layout.addWidget(lines_group)

        # Selection group
        selection_group = QGroupBox("Selection")
        selection_layout = QFormLayout(selection_group)

        self.canvas_selection_color = ColorButton()
        selection_layout.addRow("Selection Outline:", self.canvas_selection_color)

        layout.addWidget(selection_group)

        # Z-Order group
        zorder_group = QGroupBox("Z-Order")
        zorder_layout = QFormLayout(zorder_group)

        self.canvas_zorder_base = QSpinBox()
        self.canvas_zorder_base.setRange(0, 10000)
        zorder_layout.addRow("Base Z-Index:", self.canvas_zorder_base)

        self.canvas_zorder_step = QSpinBox()
        self.canvas_zorder_step.setRange(1, 100)
        zorder_layout.addRow("Z-Index Step:", self.canvas_zorder_step)

        layout.addWidget(zorder_group)

        # Zoom group
        zoom_group = QGroupBox("Zoom")
        zoom_layout = QFormLayout(zoom_group)

        self.canvas_zoom_factor = QDoubleSpinBox()
        self.canvas_zoom_factor.setRange(1.01, 2.0)
        self.canvas_zoom_factor.setSingleStep(0.05)
        self.canvas_zoom_factor.setDecimals(2)
        zoom_layout.addRow("Wheel Zoom Factor:", self.canvas_zoom_factor)

        layout.addWidget(zoom_group)
        layout.addStretch()

        return self._create_scrollable_tab(widget)

    # =========================================================================
    # Alignment Tab
    # =========================================================================

    def _create_alignment_tab(self) -> QWidget:
        """Create the Alignment settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Detection group
        detection_group = QGroupBox("Shape Detection")
        detection_layout = QFormLayout(detection_group)

        self.align_min_area = QSpinBox()
        self.align_min_area.setRange(100, 5000)
        detection_layout.addRow("Min Area (px²):", self.align_min_area)

        self.align_min_width = QSpinBox()
        self.align_min_width.setRange(5, 100)
        detection_layout.addRow("Min Width:", self.align_min_width)

        self.align_min_height = QSpinBox()
        self.align_min_height.setRange(5, 100)
        detection_layout.addRow("Min Height:", self.align_min_height)

        self.align_cluster_dist = QSpinBox()
        self.align_cluster_dist.setRange(1, 50)
        detection_layout.addRow("Clustering Distance:", self.align_cluster_dist)

        self.align_ellipse_ratio_min = QDoubleSpinBox()
        self.align_ellipse_ratio_min.setRange(0.5, 1.0)
        self.align_ellipse_ratio_min.setSingleStep(0.05)
        detection_layout.addRow("Ellipse Fill Ratio Min:", self.align_ellipse_ratio_min)

        self.align_ellipse_ratio_max = QDoubleSpinBox()
        self.align_ellipse_ratio_max.setRange(0.5, 1.0)
        self.align_ellipse_ratio_max.setSingleStep(0.05)
        detection_layout.addRow("Ellipse Fill Ratio Max:", self.align_ellipse_ratio_max)

        layout.addWidget(detection_group)

        # Color Matching group
        color_group = QGroupBox("Color Matching")
        color_layout = QFormLayout(color_group)

        self.align_hue_tolerances = QLineEdit()
        self.align_hue_tolerances.setPlaceholderText("e.g., 10, 15, 20, 25, 30")
        color_layout.addRow("Hue Tolerances:", self.align_hue_tolerances)

        self.align_sat_tolerance = QSpinBox()
        self.align_sat_tolerance.setRange(0, 255)
        color_layout.addRow("Saturation Tolerance:", self.align_sat_tolerance)

        self.align_val_tolerance = QSpinBox()
        self.align_val_tolerance.setRange(0, 255)
        color_layout.addRow("Value Tolerance:", self.align_val_tolerance)

        self.align_low_sat_threshold = QSpinBox()
        self.align_low_sat_threshold.setRange(0, 100)
        color_layout.addRow("Low Saturation Threshold:", self.align_low_sat_threshold)

        self.align_bgr_multiplier = QSpinBox()
        self.align_bgr_multiplier.setRange(1, 20)
        color_layout.addRow("BGR Tolerance Multiplier:", self.align_bgr_multiplier)

        layout.addWidget(color_group)

        # Scoring group
        scoring_group = QGroupBox("Scoring")
        scoring_layout = QFormLayout(scoring_group)

        self.align_size_weight = QSpinBox()
        self.align_size_weight.setRange(0, 200)
        scoring_layout.addRow("Size Difference Weight:", self.align_size_weight)

        layout.addWidget(scoring_group)

        # Line Alignment group
        line_group = QGroupBox("Line Alignment")
        line_layout = QFormLayout(line_group)

        self.align_line_hue_tolerances = QLineEdit()
        self.align_line_hue_tolerances.setPlaceholderText("e.g., 15, 25, 35")
        line_layout.addRow("Line Hue Tolerances:", self.align_line_hue_tolerances)

        layout.addWidget(line_group)
        layout.addStretch()

        return self._create_scrollable_tab(widget)

    # =========================================================================
    # Text Defaults Tab
    # =========================================================================

    def _create_item_defaults_tab(self) -> QWidget:
        """Create the Item Defaults tab with per-kind style + contents settings."""
        self._item_kind_widgets: dict = {}  # kind -> {field_name -> widget}

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        intro = QLabel(
            "Set default Style and Contents for each canvas item kind. "
            "These override the built-in defaults when creating new items. "
            "Click a group header to expand/collapse it."
        )
        intro.setWordWrap(True)
        intro.setStyleSheet("color: #666; margin-bottom: 4px; font-size: 8pt;")
        layout.addWidget(intro)

        for kind, label in CANVAS_ITEM_KINDS:
            group = self._build_kind_group(kind, label)
            layout.addWidget(group)

        layout.addStretch()
        return self._create_scrollable_tab(widget)

    def _build_kind_group(self, kind: str, label: str) -> QGroupBox:
        """Build a collapsible QGroupBox for one canvas item kind.

        Stores widget references in ``self._item_kind_widgets[kind]``.

        Args:
            kind: Internal kind string (e.g. ``"roundedrect"``).
            label: Human-readable display name (e.g. ``"Rounded Rectangle"``).

        Returns:
            The populated, collapsed QGroupBox.
        """
        w: dict = {}
        self._item_kind_widgets[kind] = w

        outer = QGroupBox(label)
        outer.setCheckable(True)
        outer.setChecked(False)  # collapsed by default
        outer.setStyleSheet(
            "QGroupBox { font-weight: bold; } "
            "QGroupBox::indicator { width: 12px; height: 12px; }"
        )

        # Content widget — hidden when group is collapsed
        content = QWidget()
        content.setVisible(False)
        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(4, 2, 4, 4)
        outer_layout.setSpacing(4)
        outer_layout.addWidget(content)

        outer.toggled.connect(content.setVisible)

        inner = QVBoxLayout(content)
        inner.setContentsMargins(0, 0, 0, 0)
        inner.setSpacing(4)

        # ── Style ──────────────────────────────────────────────────
        style_group = QGroupBox("Style")
        style_group.setStyleSheet("QGroupBox { font-weight: normal; }")
        style_layout = QFormLayout(style_group)
        style_layout.setContentsMargins(6, 4, 6, 4)
        style_layout.setSpacing(4)

        w["pen_color"] = ColorButton()
        style_layout.addRow("Pen Color:", w["pen_color"])

        w["pen_width"] = QSpinBox()
        w["pen_width"].setRange(1, 20)
        w["pen_width"].setSuffix(" px")
        style_layout.addRow("Pen Width:", w["pen_width"])

        w["line_dash"] = QComboBox()
        w["line_dash"].addItems(["solid", "dashed", "dotted", "dot-dashed"])
        style_layout.addRow("Line Dash:", w["line_dash"])

        w["fill_color"] = ColorButton()
        style_layout.addRow("Fill Color:", w["fill_color"])

        inner.addWidget(style_group)

        # ── Contents ───────────────────────────────────────────────
        contents_group = QGroupBox("Contents")
        contents_group.setStyleSheet("QGroupBox { font-weight: normal; }")
        cont_layout = QFormLayout(contents_group)
        cont_layout.setContentsMargins(6, 4, 6, 4)
        cont_layout.setSpacing(4)

        w["halign"] = QComboBox()
        w["halign"].addItems(["left", "center", "right", "justified"])
        cont_layout.addRow("Horizontal Align:", w["halign"])

        w["valign"] = QComboBox()
        w["valign"].addItems(["top", "middle", "bottom"])
        cont_layout.addRow("Vertical Align:", w["valign"])

        w["font_size"] = QSpinBox()
        w["font_size"].setRange(6, 72)
        w["font_size"].setSuffix(" pt")
        cont_layout.addRow("Font Size:", w["font_size"])

        w["font_family"] = QLineEdit()
        w["font_family"].setPlaceholderText("(system default)")
        cont_layout.addRow("Font Family:", w["font_family"])

        w["color"] = ColorButton()
        cont_layout.addRow("Text Color:", w["color"])

        w["spacing"] = QDoubleSpinBox()
        w["spacing"].setRange(0.0, 3.0)
        w["spacing"].setSingleStep(0.1)
        w["spacing"].setSuffix(" em")
        cont_layout.addRow("Paragraph Spacing:", w["spacing"])

        w["wrap"] = QCheckBox()
        cont_layout.addRow("Word Wrap:", w["wrap"])

        # Margins row (4 compact spinboxes on one line)
        margin_row = QHBoxLayout()
        for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
            spin = QDoubleSpinBox()
            spin.setRange(0.0, 200.0)
            spin.setSuffix(" px")
            spin.setFixedWidth(80)
            w[side] = spin
            margin_row.addWidget(QLabel(side.split("_")[1].capitalize() + ":"))
            margin_row.addWidget(spin)
        margin_row.addStretch()
        cont_layout.addRow("Margins:", margin_row)

        w["flow_type"] = QComboBox()
        w["flow_type"].addItems(["none", "horizontal", "vertical"])
        cont_layout.addRow("Flow Type:", w["flow_type"])

        w["text_box_width"] = QDoubleSpinBox()
        w["text_box_width"].setRange(0.0, 2000.0)
        w["text_box_width"].setSpecialValueText("Auto")
        w["text_box_width"].setSuffix(" px")
        cont_layout.addRow("Text Box Width:", w["text_box_width"])

        w["text_box_height"] = QDoubleSpinBox()
        w["text_box_height"].setRange(0.0, 2000.0)
        w["text_box_height"].setSpecialValueText("Auto")
        w["text_box_height"].setSuffix(" px")
        cont_layout.addRow("Text Box Height:", w["text_box_height"])

        inner.addWidget(contents_group)

        return outer

    def _load_item_defaults(self, s) -> None:
        """Populate the item-kind widgets from *s.item_defaults*.

        Args:
            s: An ``AppSettings`` instance (may be merged, single-layer, or built-in).
        """
        from settings import ItemDefaults
        for kind, _label in CANVAS_ITEM_KINDS:
            if kind not in self._item_kind_widgets:
                continue
            id_obj = s.item_defaults.get(kind, ItemDefaults())
            w = self._item_kind_widgets[kind]
            # Style
            w["pen_color"].setColor(id_obj.style.pen_color)
            w["pen_width"].setValue(id_obj.style.pen_width)
            w["line_dash"].setCurrentText(id_obj.style.line_dash)
            w["fill_color"].setColor(id_obj.style.fill_color)
            # Contents
            w["halign"].setCurrentText(id_obj.contents.halign)
            w["valign"].setCurrentText(id_obj.contents.valign)
            w["font_size"].setValue(id_obj.contents.font_size)
            w["font_family"].setText(id_obj.contents.font_family)
            w["color"].setColor(id_obj.contents.color)
            w["spacing"].setValue(id_obj.contents.spacing)
            w["wrap"].setChecked(id_obj.contents.wrap)
            w["margin_left"].setValue(id_obj.contents.margin_left)
            w["margin_right"].setValue(id_obj.contents.margin_right)
            w["margin_top"].setValue(id_obj.contents.margin_top)
            w["margin_bottom"].setValue(id_obj.contents.margin_bottom)
            w["flow_type"].setCurrentText(id_obj.contents.flow_type)
            w["text_box_width"].setValue(id_obj.contents.text_box_width)
            w["text_box_height"].setValue(id_obj.contents.text_box_height)

    def _save_item_defaults(self, s) -> None:
        """Write item-kind widget values into *s.item_defaults*.

        Args:
            s: The ``AppSettings`` object to update in place.
        """
        from settings import ItemDefaults, DefaultStyleSettings, DefaultContentsSettings
        for kind, _label in CANVAS_ITEM_KINDS:
            if kind not in self._item_kind_widgets:
                continue
            w = self._item_kind_widgets[kind]
            style = DefaultStyleSettings(
                pen_color=w["pen_color"].color(),
                pen_width=w["pen_width"].value(),
                line_dash=w["line_dash"].currentText(),
                fill_color=w["fill_color"].color(),
            )
            contents = DefaultContentsSettings(
                halign=w["halign"].currentText(),
                valign=w["valign"].currentText(),
                font_size=w["font_size"].value(),
                font_family=w["font_family"].text().strip(),
                color=w["color"].color(),
                spacing=w["spacing"].value(),
                wrap=w["wrap"].isChecked(),
                margin_left=w["margin_left"].value(),
                margin_right=w["margin_right"].value(),
                margin_top=w["margin_top"].value(),
                margin_bottom=w["margin_bottom"].value(),
                flow_type=w["flow_type"].currentText(),
                text_box_width=w["text_box_width"].value(),
                text_box_height=w["text_box_height"].value(),
            )
            s.item_defaults[kind] = ItemDefaults(style=style, contents=contents)

    # =========================================================================
    # External Tools Tab
    # =========================================================================

    def _create_external_tools_tab(self) -> QWidget:
        """Create the External Tools settings tab.

        Shows auto-detected paths as read-only when found, with browse
        buttons for manual override.  Each tool group includes a
        description of what features it enables.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)

        # Intro note
        intro = QLabel(
            "PictoSync uses external CLI tools for diagram import. "
            "Auto-detected paths are shown grayed out. Use Browse to "
            "override a path manually, or Clear to revert to auto-detection."
        )
        intro.setWordWrap(True)
        intro.setStyleSheet("color: #666; margin-bottom: 4px;")
        layout.addWidget(intro)

        # ── Java ──
        java_group = QGroupBox("Java Runtime")
        java_layout = QVBoxLayout(java_group)
        java_layout.setContentsMargins(6, 4, 6, 4)
        java_layout.setSpacing(4)

        java_note = QLabel(
            "Java (JRE 8+) is required by PlantUML to render .puml diagrams. "
            "Without Java, PlantUML import is unavailable."
        )
        java_note.setWordWrap(True)
        java_note.setStyleSheet("color: #666; font-size: 11px;")
        java_layout.addWidget(java_note)

        java_row = QHBoxLayout()
        self.tools_java_edit = QLineEdit()
        self.tools_java_edit.setPlaceholderText("Auto-detect from PATH")
        java_row.addWidget(self.tools_java_edit)
        java_browse = QPushButton("Browse...")
        java_browse.setFixedWidth(80)
        java_browse.clicked.connect(lambda: self._browse_tool_exe(self.tools_java_edit, "Java Executable"))
        java_row.addWidget(java_browse)
        java_clear = QPushButton("Clear")
        java_clear.setFixedWidth(50)
        java_clear.clicked.connect(lambda: self._clear_tool_path(self.tools_java_edit))
        java_row.addWidget(java_clear)
        java_layout.addLayout(java_row)

        self.tools_java_status = QLabel()
        self.tools_java_status.setStyleSheet("font-size: 11px;")
        java_layout.addWidget(self.tools_java_status)

        layout.addWidget(java_group)

        # ── PlantUML JAR ──
        puml_group = QGroupBox("PlantUML JAR")
        puml_layout = QVBoxLayout(puml_group)
        puml_layout.setContentsMargins(6, 4, 6, 4)
        puml_layout.setSpacing(4)

        puml_note = QLabel(
            "PlantUML renders .puml source files into diagrams. "
            "Requires Java. Enables: import .puml files as annotated backgrounds. "
            "Download from: https://github.com/plantuml/plantuml/releases"
        )
        puml_note.setWordWrap(True)
        puml_note.setStyleSheet("color: #666; font-size: 11px;")
        puml_layout.addWidget(puml_note)

        puml_row = QHBoxLayout()
        self.tools_puml_jar_edit = QLineEdit()
        self.tools_puml_jar_edit.setPlaceholderText("Auto-detect (PLANTUML_JAR env, project dir, PATH)")
        puml_row.addWidget(self.tools_puml_jar_edit)
        puml_browse = QPushButton("Browse...")
        puml_browse.setFixedWidth(80)
        puml_browse.clicked.connect(lambda: self._browse_tool_file(
            self.tools_puml_jar_edit, "PlantUML JAR", "JAR Files (*.jar);;All Files (*)"
        ))
        puml_row.addWidget(puml_browse)
        puml_clear = QPushButton("Clear")
        puml_clear.setFixedWidth(50)
        puml_clear.clicked.connect(lambda: self._clear_tool_path(self.tools_puml_jar_edit))
        puml_row.addWidget(puml_clear)
        puml_layout.addLayout(puml_row)

        self.tools_puml_status = QLabel()
        self.tools_puml_status.setStyleSheet("font-size: 11px;")
        puml_layout.addWidget(self.tools_puml_status)

        layout.addWidget(puml_group)

        # ── Node.js ──
        node_group = QGroupBox("Node.js")
        node_layout = QVBoxLayout(node_group)
        node_layout.setContentsMargins(6, 4, 6, 4)
        node_layout.setSpacing(4)

        node_note = QLabel(
            "Node.js is required by the Mermaid CLI (mmdc) to render "
            ".mmd/.mermaid source files. Without Node.js, mmdc cannot run."
        )
        node_note.setWordWrap(True)
        node_note.setStyleSheet("color: #666; font-size: 11px;")
        node_layout.addWidget(node_note)

        node_row = QHBoxLayout()
        self.tools_node_edit = QLineEdit()
        self.tools_node_edit.setPlaceholderText("Auto-detect from PATH")
        node_row.addWidget(self.tools_node_edit)
        node_browse = QPushButton("Browse...")
        node_browse.setFixedWidth(80)
        node_browse.clicked.connect(lambda: self._browse_tool_exe(self.tools_node_edit, "Node.js Executable"))
        node_row.addWidget(node_browse)
        node_clear = QPushButton("Clear")
        node_clear.setFixedWidth(50)
        node_clear.clicked.connect(lambda: self._clear_tool_path(self.tools_node_edit))
        node_row.addWidget(node_clear)
        node_layout.addLayout(node_row)

        self.tools_node_status = QLabel()
        self.tools_node_status.setStyleSheet("font-size: 11px;")
        node_layout.addWidget(self.tools_node_status)

        layout.addWidget(node_group)

        # ── Mermaid CLI (mmdc) ──
        mmdc_group = QGroupBox("Mermaid CLI (mmdc)")
        mmdc_layout = QVBoxLayout(mmdc_group)
        mmdc_layout.setContentsMargins(6, 4, 6, 4)
        mmdc_layout.setSpacing(4)

        mmdc_note = QLabel(
            "mmdc renders .mmd/.mermaid source files into PNG and SVG using "
            "Puppeteer/Chromium for pixel-perfect output. Requires Node.js. "
            "Enables: import Mermaid source files as annotated backgrounds. "
            "Install with: npm install -g @mermaid-js/mermaid-cli"
        )
        mmdc_note.setWordWrap(True)
        mmdc_note.setStyleSheet("color: #666; font-size: 11px;")
        mmdc_layout.addWidget(mmdc_note)

        mmdc_row = QHBoxLayout()
        self.tools_mmdc_edit = QLineEdit()
        self.tools_mmdc_edit.setPlaceholderText("Auto-detect (MMDC_PATH env, PATH)")
        mmdc_row.addWidget(self.tools_mmdc_edit)
        mmdc_browse = QPushButton("Browse...")
        mmdc_browse.setFixedWidth(80)
        mmdc_browse.clicked.connect(lambda: self._browse_tool_exe(self.tools_mmdc_edit, "mmdc Executable"))
        mmdc_row.addWidget(mmdc_browse)
        mmdc_clear = QPushButton("Clear")
        mmdc_clear.setFixedWidth(50)
        mmdc_clear.clicked.connect(lambda: self._clear_tool_path(self.tools_mmdc_edit))
        mmdc_row.addWidget(mmdc_clear)
        mmdc_layout.addLayout(mmdc_row)

        self.tools_mmdc_status = QLabel()
        self.tools_mmdc_status.setStyleSheet("font-size: 11px;")
        mmdc_layout.addWidget(self.tools_mmdc_status)

        # PNG scale factor
        scale_row = QHBoxLayout()
        scale_label = QLabel("PNG scale factor:")
        scale_label.setToolTip(
            "CSS zoom/scale passed to mmdc via the -s flag.\n"
            "Higher values produce larger, sharper PNG backgrounds.\n"
            "1 = native size, 4 = 4\u00d7 resolution (default)."
        )
        scale_row.addWidget(scale_label)
        self.tools_mmdc_scale_spin = QSpinBox()
        self.tools_mmdc_scale_spin.setRange(1, 10)
        self.tools_mmdc_scale_spin.setValue(
            self.settings_manager.settings.external_tools.mmdc_png_scale
        )
        self.tools_mmdc_scale_spin.setSuffix("\u00d7")
        self.tools_mmdc_scale_spin.setFixedWidth(70)
        scale_row.addWidget(self.tools_mmdc_scale_spin)
        scale_row.addStretch()
        mmdc_layout.addLayout(scale_row)

        # C4 layout: shapes per row
        c4_shapes_row = QHBoxLayout()
        c4_shapes_label = QLabel("C4 shapes per row:")
        c4_shapes_label.setToolTip(
            "Maximum number of C4 shapes rendered per row inside a boundary.\n"
            "Passed to Mermaid via UpdateLayoutConfig($c4ShapeInRow).\n"
            "Lower values produce taller, narrower diagrams."
        )
        c4_shapes_row.addWidget(c4_shapes_label)
        self.tools_c4_shapes_spin = QSpinBox()
        self.tools_c4_shapes_spin.setRange(1, 10)
        self.tools_c4_shapes_spin.setValue(
            self.settings_manager.settings.external_tools.c4_shapes_per_row
        )
        self.tools_c4_shapes_spin.setFixedWidth(70)
        c4_shapes_row.addWidget(self.tools_c4_shapes_spin)
        c4_shapes_row.addStretch()
        mmdc_layout.addLayout(c4_shapes_row)

        # C4 layout: boundaries per row
        c4_bnd_row = QHBoxLayout()
        c4_bnd_label = QLabel("C4 boundaries per row:")
        c4_bnd_label.setToolTip(
            "Maximum number of C4 boundaries rendered per row.\n"
            "Passed to Mermaid via UpdateLayoutConfig($c4BoundaryInRow).\n"
            "Lower values stack boundaries vertically."
        )
        c4_bnd_row.addWidget(c4_bnd_label)
        self.tools_c4_bnd_spin = QSpinBox()
        self.tools_c4_bnd_spin.setRange(1, 10)
        self.tools_c4_bnd_spin.setValue(
            self.settings_manager.settings.external_tools.c4_boundaries_per_row
        )
        self.tools_c4_bnd_spin.setFixedWidth(70)
        c4_bnd_row.addWidget(self.tools_c4_bnd_spin)
        c4_bnd_row.addStretch()
        mmdc_layout.addLayout(c4_bnd_row)

        layout.addWidget(mmdc_group)

        layout.addStretch()

        # Run auto-detection to populate status labels
        self._detect_external_tools()

        return self._create_scrollable_tab(widget)

    def _detect_external_tools(self):
        """Auto-detect external tools and update status labels.

        For each tool, if the settings field is empty, tries to find
        the tool automatically.  Populates the line edit (grayed out)
        when auto-detected, and updates the status label.
        """
        s = self.settings_manager.settings

        # ── Java ──
        configured = s.external_tools.java_path
        if configured and os.path.isfile(configured):
            self.tools_java_edit.setText(configured)
            self.tools_java_edit.setReadOnly(False)
            self._set_tool_status(self.tools_java_status, True, "Configured manually")
        else:
            detected = shutil.which("java")
            if detected:
                self.tools_java_edit.setText(detected)
                self.tools_java_edit.setReadOnly(True)
                self._set_tool_status(self.tools_java_status, True, "Auto-detected from PATH")
            else:
                self.tools_java_edit.setText("")
                self.tools_java_edit.setReadOnly(False)
                self._set_tool_status(self.tools_java_status, False,
                                      "Not found — install JRE 8+ from https://adoptium.net/")

        # ── PlantUML JAR ──
        configured = s.external_tools.plantuml_jar_path
        if configured and os.path.isfile(configured):
            self.tools_puml_jar_edit.setText(configured)
            self.tools_puml_jar_edit.setReadOnly(False)
            self._set_tool_status(self.tools_puml_status, True, "Configured manually")
        else:
            from plantuml.renderer import find_plantuml_jar
            detected = find_plantuml_jar()
            if detected:
                self.tools_puml_jar_edit.setText(detected)
                self.tools_puml_jar_edit.setReadOnly(True)
                self._set_tool_status(self.tools_puml_status, True, "Auto-detected")
            else:
                self.tools_puml_jar_edit.setText("")
                self.tools_puml_jar_edit.setReadOnly(False)
                self._set_tool_status(self.tools_puml_status, False,
                                      "Not found — download from github.com/plantuml/plantuml/releases")

        # ── Node.js ──
        configured = s.external_tools.nodejs_path
        if configured and os.path.isfile(configured):
            self.tools_node_edit.setText(configured)
            self.tools_node_edit.setReadOnly(False)
            self._set_tool_status(self.tools_node_status, True, "Configured manually")
        else:
            detected = shutil.which("node")
            if detected:
                self.tools_node_edit.setText(detected)
                self.tools_node_edit.setReadOnly(True)
                self._set_tool_status(self.tools_node_status, True, "Auto-detected from PATH")
            else:
                self.tools_node_edit.setText("")
                self.tools_node_edit.setReadOnly(False)
                self._set_tool_status(self.tools_node_status, False,
                                      "Not found — install from https://nodejs.org/")

        # ── mmdc ──
        configured = s.external_tools.mmdc_path
        if configured and os.path.isfile(configured):
            self.tools_mmdc_edit.setText(configured)
            self.tools_mmdc_edit.setReadOnly(False)
            self._set_tool_status(self.tools_mmdc_status, True, "Configured manually")
        else:
            from mermaid.renderer import find_mmdc
            detected = find_mmdc()
            if detected:
                self.tools_mmdc_edit.setText(detected)
                self.tools_mmdc_edit.setReadOnly(True)
                self._set_tool_status(self.tools_mmdc_status, True, "Auto-detected")
            else:
                self.tools_mmdc_edit.setText("")
                self.tools_mmdc_edit.setReadOnly(False)
                self._set_tool_status(self.tools_mmdc_status, False,
                                      "Not found — install with: npm install -g @mermaid-js/mermaid-cli")

    @staticmethod
    def _set_tool_status(label: QLabel, found: bool, message: str):
        """Update a tool status label with found/not-found styling."""
        if found:
            label.setText(f"Found: {message}")
            label.setStyleSheet("color: #27AE60; font-size: 11px;")
        else:
            label.setText(f"Not found: {message}")
            label.setStyleSheet("color: #E74C3C; font-size: 11px;")

    def _browse_tool_exe(self, line_edit: QLineEdit, title: str):
        """Open file dialog to browse for an executable."""
        path, _ = QFileDialog.getOpenFileName(
            self, f"Select {title}", "",
            "Executables (*.exe *.cmd *.bat);;All Files (*)"
        )
        if path:
            line_edit.setText(path)
            line_edit.setReadOnly(False)

    def _browse_tool_file(self, line_edit: QLineEdit, title: str, file_filter: str):
        """Open file dialog to browse for a file."""
        path, _ = QFileDialog.getOpenFileName(self, f"Select {title}", "", file_filter)
        if path:
            line_edit.setText(path)
            line_edit.setReadOnly(False)

    def _clear_tool_path(self, line_edit: QLineEdit):
        """Clear a tool path and re-run auto-detection."""
        line_edit.setText("")
        line_edit.setReadOnly(False)
        # Save cleared value so detection uses auto-detect
        self._save_tool_path_from_edit(line_edit, "")
        self._detect_external_tools()

    def _save_tool_path_from_edit(self, line_edit: QLineEdit, value: str):
        """Update the matching settings field for a tool line edit."""
        s = self.settings_manager.settings
        if line_edit is self.tools_java_edit:
            s.external_tools.java_path = value
        elif line_edit is self.tools_puml_jar_edit:
            s.external_tools.plantuml_jar_path = value
        elif line_edit is self.tools_node_edit:
            s.external_tools.nodejs_path = value
        elif line_edit is self.tools_mmdc_edit:
            s.external_tools.mmdc_path = value

    # =========================================================================
    # Settings Load/Save
    # =========================================================================

    def _snapshot_settings(self) -> dict:
        """Create a snapshot of current settings for cancel/restore."""
        s = self.settings_manager.settings
        return {
            # General
            "theme": s.theme,
            "workspace_dir": s.workspace_dir,
            "pptx_export_to_source_dir": s.pptx_export_to_source_dir,
            # Editor
            "editor_font_family": s.editor.font.family,
            "editor_font_size": s.editor.font.size,
            "editor_tab_width": s.editor.font.tab_width,
            "editor_ln_left_margin": s.editor.line_numbers.left_margin,
            "editor_ln_right_margin": s.editor.line_numbers.right_margin,
            "editor_ln_highlight_bar": s.editor.line_numbers.highlight_bar_width,
            "editor_fold_width": s.editor.folding.width,
            "syntax_key_color": s.editor.syntax.key_color,
            "syntax_key_bold": s.editor.syntax.key_bold,
            "syntax_string_color": s.editor.syntax.string_color,
            "syntax_number_color": s.editor.syntax.number_color,
            "syntax_keyword_color": s.editor.syntax.keyword_color,
            "syntax_keyword_bold": s.editor.syntax.keyword_bold,
            "syntax_brace_color": s.editor.syntax.brace_color,
            "syntax_brace_bold": s.editor.syntax.brace_bold,
            # Canvas
            "canvas_handle_size": s.canvas.handles.size,
            "canvas_hit_distance": s.canvas.handles.hit_distance,
            "canvas_handle_border": s.canvas.handles.border_color,
            "canvas_handle_fill": s.canvas.handles.fill_color,
            "canvas_min_size": s.canvas.shapes.min_size,
            "canvas_rounded_radius": s.canvas.shapes.default_rounded_radius,
            "canvas_dash_length": s.canvas.shapes.default_dash_length,
            "canvas_dash_solid": s.canvas.shapes.default_dash_solid_percent,
            "canvas_line_hit_width": s.canvas.lines.hit_area_width,
            "canvas_arrow_multiplier": s.canvas.lines.arrow_min_multiplier,
            "canvas_min_text_box": s.canvas.lines.min_text_box_size,
            "canvas_selection_color": s.canvas.selection.outline_color,
            "canvas_zorder_base": s.canvas.zorder.base,
            "canvas_zorder_step": s.canvas.zorder.step,
            "canvas_zoom_factor": s.canvas.zoom.wheel_factor,
            # Alignment
            "align_min_area": s.alignment.detection.default_min_area,
            "align_min_width": s.alignment.detection.min_shape_width,
            "align_min_height": s.alignment.detection.min_shape_height,
            "align_cluster_dist": s.alignment.detection.center_clustering_distance,
            "align_ellipse_ratio_min": s.alignment.detection.ellipse_fill_ratio_min,
            "align_ellipse_ratio_max": s.alignment.detection.ellipse_fill_ratio_max,
            "align_hue_tolerances": s.alignment.color.hue_tolerances,
            "align_sat_tolerance": s.alignment.color.saturation_tolerance,
            "align_val_tolerance": s.alignment.color.value_tolerance,
            "align_low_sat_threshold": s.alignment.color.low_saturation_threshold,
            "align_bgr_multiplier": s.alignment.color.bgr_tolerance_multiplier,
            "align_size_weight": s.alignment.scoring.size_difference_weight,
            "align_line_hue_tolerances": s.alignment.line.hue_tolerances,
            # Item Defaults (snapshot as a deep copy dict keyed by kind)
            "item_defaults": {
                kind: {
                    "style": {
                        "pen_color": id_obj.style.pen_color,
                        "pen_width": id_obj.style.pen_width,
                        "line_dash": id_obj.style.line_dash,
                        "fill_color": id_obj.style.fill_color,
                    },
                    "contents": {
                        "halign": id_obj.contents.halign,
                        "valign": id_obj.contents.valign,
                        "spacing": id_obj.contents.spacing,
                        "color": id_obj.contents.color,
                        "font_family": id_obj.contents.font_family,
                        "font_size": id_obj.contents.font_size,
                        "margin_left": id_obj.contents.margin_left,
                        "margin_right": id_obj.contents.margin_right,
                        "margin_top": id_obj.contents.margin_top,
                        "margin_bottom": id_obj.contents.margin_bottom,
                        "wrap": id_obj.contents.wrap,
                        "flow_type": id_obj.contents.flow_type,
                        "text_box_width": id_obj.contents.text_box_width,
                        "text_box_height": id_obj.contents.text_box_height,
                    },
                }
                for kind, id_obj in s.item_defaults.items()
            },
            # Gemini
            "gemini_models": list(s.gemini.models),
            "gemini_default_model": s.gemini.default_model,
            # External Tools
            "tools_java_path": s.external_tools.java_path,
            "tools_puml_jar_path": s.external_tools.plantuml_jar_path,
            "tools_nodejs_path": s.external_tools.nodejs_path,
            "tools_mmdc_path": s.external_tools.mmdc_path,
            "tools_mmdc_png_scale": s.external_tools.mmdc_png_scale,
            "tools_c4_shapes_per_row": s.external_tools.c4_shapes_per_row,
            "tools_c4_boundaries_per_row": s.external_tools.c4_boundaries_per_row,
        }

    def _load_settings(self, settings=None):
        """Load *settings* (or current merged settings) into the UI widgets.

        Args:
            settings: Optional AppSettings to display. When None, uses the
                      merged settings_manager.settings (startup default).
        """
        s = settings if settings is not None else self.settings_manager.settings

        # General
        self.theme_combo.setCurrentText(s.theme)
        self.workspace_dir_edit.setText(s.workspace_dir)
        self.pptx_source_dir_cb.setChecked(s.pptx_export_to_source_dir)

        # Editor - Font
        self.editor_font_family.setText(s.editor.font.family)
        self.editor_font_size.setValue(s.editor.font.size)
        self.editor_tab_width.setValue(s.editor.font.tab_width)

        # Editor - Line Numbers
        self.editor_ln_left_margin.setValue(s.editor.line_numbers.left_margin)
        self.editor_ln_right_margin.setValue(s.editor.line_numbers.right_margin)
        self.editor_ln_highlight_bar.setValue(s.editor.line_numbers.highlight_bar_width)

        # Editor - Folding
        self.editor_fold_width.setValue(s.editor.folding.width)

        # Editor - Syntax
        self.syntax_key_color.setColor(s.editor.syntax.key_color)
        self.syntax_key_bold.setChecked(s.editor.syntax.key_bold)
        self.syntax_string_color.setColor(s.editor.syntax.string_color)
        self.syntax_number_color.setColor(s.editor.syntax.number_color)
        self.syntax_keyword_color.setColor(s.editor.syntax.keyword_color)
        self.syntax_keyword_bold.setChecked(s.editor.syntax.keyword_bold)
        self.syntax_brace_color.setColor(s.editor.syntax.brace_color)
        self.syntax_brace_bold.setChecked(s.editor.syntax.brace_bold)

        # Canvas - Handles
        self.canvas_handle_size.setValue(s.canvas.handles.size)
        self.canvas_hit_distance.setValue(s.canvas.handles.hit_distance)
        self.canvas_handle_border.setColor(s.canvas.handles.border_color)
        self.canvas_handle_fill.setColor(s.canvas.handles.fill_color)

        # Canvas - Shapes
        self.canvas_min_size.setValue(s.canvas.shapes.min_size)
        self.canvas_rounded_radius.setValue(s.canvas.shapes.default_rounded_radius)
        self.canvas_dash_length.setValue(s.canvas.shapes.default_dash_length)
        self.canvas_dash_solid.setValue(s.canvas.shapes.default_dash_solid_percent)

        # Canvas - Lines
        self.canvas_line_hit_width.setValue(s.canvas.lines.hit_area_width)
        self.canvas_arrow_multiplier.setValue(s.canvas.lines.arrow_min_multiplier)
        self.canvas_min_text_box.setValue(s.canvas.lines.min_text_box_size)

        # Canvas - Selection
        self.canvas_selection_color.setColor(s.canvas.selection.outline_color)

        # Canvas - Z-Order
        self.canvas_zorder_base.setValue(s.canvas.zorder.base)
        self.canvas_zorder_step.setValue(s.canvas.zorder.step)

        # Canvas - Zoom
        self.canvas_zoom_factor.setValue(s.canvas.zoom.wheel_factor)

        # Alignment - Detection
        self.align_min_area.setValue(s.alignment.detection.default_min_area)
        self.align_min_width.setValue(s.alignment.detection.min_shape_width)
        self.align_min_height.setValue(s.alignment.detection.min_shape_height)
        self.align_cluster_dist.setValue(s.alignment.detection.center_clustering_distance)
        self.align_ellipse_ratio_min.setValue(s.alignment.detection.ellipse_fill_ratio_min)
        self.align_ellipse_ratio_max.setValue(s.alignment.detection.ellipse_fill_ratio_max)

        # Alignment - Color
        self.align_hue_tolerances.setText(", ".join(map(str, s.alignment.color.hue_tolerances)))
        self.align_sat_tolerance.setValue(s.alignment.color.saturation_tolerance)
        self.align_val_tolerance.setValue(s.alignment.color.value_tolerance)
        self.align_low_sat_threshold.setValue(s.alignment.color.low_saturation_threshold)
        self.align_bgr_multiplier.setValue(s.alignment.color.bgr_tolerance_multiplier)

        # Alignment - Scoring
        self.align_size_weight.setValue(s.alignment.scoring.size_difference_weight)

        # Alignment - Line
        self.align_line_hue_tolerances.setText(", ".join(map(str, s.alignment.line.hue_tolerances)))

        # Item Defaults
        self._load_item_defaults(s)

        # Gemini
        self.gemini_model_list.clear()
        self.gemini_model_list.addItems(s.gemini.models)
        self.gemini_default_combo.clear()
        self.gemini_default_combo.addItems(s.gemini.models)
        self.gemini_default_combo.setCurrentText(s.gemini.default_model)

        # External Tools — re-run detection to refresh status labels
        self._detect_external_tools()

    def _save_settings(self):
        """Save UI widget values to the active layer's settings file.

        Built-in layer is read-only — calling this method does nothing in that case.
        System layer writes to the system file; User layer writes to the user file.
        The merged in-memory settings_manager.settings is also updated so that
        the running app reflects the change immediately.
        """
        if self._active_layer == "builtin":
            return  # read-only

        # Write into the merged settings object (live app)
        s = self.settings_manager.settings

        # General
        s.theme = self.theme_combo.currentText()
        s.workspace_dir = self.workspace_dir_edit.text().strip()
        s.pptx_export_to_source_dir = self.pptx_source_dir_cb.isChecked()

        # Editor - Font
        s.editor.font.family = self.editor_font_family.text()
        s.editor.font.size = self.editor_font_size.value()
        s.editor.font.tab_width = self.editor_tab_width.value()

        # Editor - Line Numbers
        s.editor.line_numbers.left_margin = self.editor_ln_left_margin.value()
        s.editor.line_numbers.right_margin = self.editor_ln_right_margin.value()
        s.editor.line_numbers.highlight_bar_width = self.editor_ln_highlight_bar.value()

        # Editor - Folding
        s.editor.folding.width = self.editor_fold_width.value()

        # Editor - Syntax
        s.editor.syntax.key_color = self.syntax_key_color.color()
        s.editor.syntax.key_bold = self.syntax_key_bold.isChecked()
        s.editor.syntax.string_color = self.syntax_string_color.color()
        s.editor.syntax.number_color = self.syntax_number_color.color()
        s.editor.syntax.keyword_color = self.syntax_keyword_color.color()
        s.editor.syntax.keyword_bold = self.syntax_keyword_bold.isChecked()
        s.editor.syntax.brace_color = self.syntax_brace_color.color()
        s.editor.syntax.brace_bold = self.syntax_brace_bold.isChecked()

        # Canvas - Handles
        s.canvas.handles.size = self.canvas_handle_size.value()
        s.canvas.handles.hit_distance = self.canvas_hit_distance.value()
        s.canvas.handles.border_color = self.canvas_handle_border.color()
        s.canvas.handles.fill_color = self.canvas_handle_fill.color()

        # Canvas - Shapes
        s.canvas.shapes.min_size = self.canvas_min_size.value()
        s.canvas.shapes.default_rounded_radius = self.canvas_rounded_radius.value()
        s.canvas.shapes.default_dash_length = self.canvas_dash_length.value()
        s.canvas.shapes.default_dash_solid_percent = self.canvas_dash_solid.value()

        # Canvas - Lines
        s.canvas.lines.hit_area_width = self.canvas_line_hit_width.value()
        s.canvas.lines.arrow_min_multiplier = self.canvas_arrow_multiplier.value()
        s.canvas.lines.min_text_box_size = self.canvas_min_text_box.value()

        # Canvas - Selection
        s.canvas.selection.outline_color = self.canvas_selection_color.color()

        # Canvas - Z-Order
        s.canvas.zorder.base = self.canvas_zorder_base.value()
        s.canvas.zorder.step = self.canvas_zorder_step.value()

        # Canvas - Zoom
        s.canvas.zoom.wheel_factor = self.canvas_zoom_factor.value()

        # Alignment - Detection
        s.alignment.detection.default_min_area = self.align_min_area.value()
        s.alignment.detection.min_shape_width = self.align_min_width.value()
        s.alignment.detection.min_shape_height = self.align_min_height.value()
        s.alignment.detection.center_clustering_distance = self.align_cluster_dist.value()
        s.alignment.detection.ellipse_fill_ratio_min = self.align_ellipse_ratio_min.value()
        s.alignment.detection.ellipse_fill_ratio_max = self.align_ellipse_ratio_max.value()

        # Alignment - Color (parse list from text)
        try:
            hue_list = [int(x.strip()) for x in self.align_hue_tolerances.text().split(",") if x.strip()]
            s.alignment.color.hue_tolerances = hue_list if hue_list else [10, 15, 20, 25, 30]
        except ValueError:
            pass  # Keep existing value

        s.alignment.color.saturation_tolerance = self.align_sat_tolerance.value()
        s.alignment.color.value_tolerance = self.align_val_tolerance.value()
        s.alignment.color.low_saturation_threshold = self.align_low_sat_threshold.value()
        s.alignment.color.bgr_tolerance_multiplier = self.align_bgr_multiplier.value()

        # Alignment - Scoring
        s.alignment.scoring.size_difference_weight = self.align_size_weight.value()

        # Alignment - Line (parse list from text)
        try:
            line_hue_list = [int(x.strip()) for x in self.align_line_hue_tolerances.text().split(",") if x.strip()]
            s.alignment.line.hue_tolerances = line_hue_list if line_hue_list else [15, 25, 35]
        except ValueError:
            pass  # Keep existing value

        # Item Defaults
        self._save_item_defaults(s)

        # Gemini
        s.gemini.models = [
            self.gemini_model_list.item(i).text()
            for i in range(self.gemini_model_list.count())
        ]
        default = self.gemini_default_combo.currentText()
        s.gemini.default_model = default if default in s.gemini.models else (
            s.gemini.models[0] if s.gemini.models else "gemini-2.5-flash-image"
        )

        # External Tools — only save non-empty manually-entered paths
        # (auto-detected read-only fields are not persisted)
        if not self.tools_java_edit.isReadOnly():
            s.external_tools.java_path = self.tools_java_edit.text().strip()
        if not self.tools_puml_jar_edit.isReadOnly():
            s.external_tools.plantuml_jar_path = self.tools_puml_jar_edit.text().strip()
        if not self.tools_node_edit.isReadOnly():
            s.external_tools.nodejs_path = self.tools_node_edit.text().strip()
        if not self.tools_mmdc_edit.isReadOnly():
            s.external_tools.mmdc_path = self.tools_mmdc_edit.text().strip()
        s.external_tools.mmdc_png_scale = self.tools_mmdc_scale_spin.value()
        s.external_tools.c4_shapes_per_row = self.tools_c4_shapes_spin.value()
        s.external_tools.c4_boundaries_per_row = self.tools_c4_bnd_spin.value()

        # Persist to the active layer's file
        if self._active_layer == "system":
            self.settings_manager.save_to(
                self.settings_manager.system_settings_file,
                self.settings_manager.settings,
            )
        else:  # user
            self.settings_manager.save()
        self._update_layer_path_label()

    def _restore_from_snapshot(self, snapshot: dict):
        """Restore settings from a snapshot."""
        s = self.settings_manager.settings

        # General
        s.theme = snapshot["theme"]
        s.workspace_dir = snapshot["workspace_dir"]
        s.pptx_export_to_source_dir = snapshot["pptx_export_to_source_dir"]

        # Editor
        s.editor.font.family = snapshot["editor_font_family"]
        s.editor.font.size = snapshot["editor_font_size"]
        s.editor.font.tab_width = snapshot["editor_tab_width"]
        s.editor.line_numbers.left_margin = snapshot["editor_ln_left_margin"]
        s.editor.line_numbers.right_margin = snapshot["editor_ln_right_margin"]
        s.editor.line_numbers.highlight_bar_width = snapshot["editor_ln_highlight_bar"]
        s.editor.folding.width = snapshot["editor_fold_width"]
        s.editor.syntax.key_color = snapshot["syntax_key_color"]
        s.editor.syntax.key_bold = snapshot["syntax_key_bold"]
        s.editor.syntax.string_color = snapshot["syntax_string_color"]
        s.editor.syntax.number_color = snapshot["syntax_number_color"]
        s.editor.syntax.keyword_color = snapshot["syntax_keyword_color"]
        s.editor.syntax.keyword_bold = snapshot["syntax_keyword_bold"]
        s.editor.syntax.brace_color = snapshot["syntax_brace_color"]
        s.editor.syntax.brace_bold = snapshot["syntax_brace_bold"]

        # Canvas
        s.canvas.handles.size = snapshot["canvas_handle_size"]
        s.canvas.handles.hit_distance = snapshot["canvas_hit_distance"]
        s.canvas.handles.border_color = snapshot["canvas_handle_border"]
        s.canvas.handles.fill_color = snapshot["canvas_handle_fill"]
        s.canvas.shapes.min_size = snapshot["canvas_min_size"]
        s.canvas.shapes.default_rounded_radius = snapshot["canvas_rounded_radius"]
        s.canvas.shapes.default_dash_length = snapshot["canvas_dash_length"]
        s.canvas.shapes.default_dash_solid_percent = snapshot["canvas_dash_solid"]
        s.canvas.lines.hit_area_width = snapshot["canvas_line_hit_width"]
        s.canvas.lines.arrow_min_multiplier = snapshot["canvas_arrow_multiplier"]
        s.canvas.lines.min_text_box_size = snapshot["canvas_min_text_box"]
        s.canvas.selection.outline_color = snapshot["canvas_selection_color"]
        s.canvas.zorder.base = snapshot["canvas_zorder_base"]
        s.canvas.zorder.step = snapshot["canvas_zorder_step"]
        s.canvas.zoom.wheel_factor = snapshot["canvas_zoom_factor"]

        # Alignment
        s.alignment.detection.default_min_area = snapshot["align_min_area"]
        s.alignment.detection.min_shape_width = snapshot["align_min_width"]
        s.alignment.detection.min_shape_height = snapshot["align_min_height"]
        s.alignment.detection.center_clustering_distance = snapshot["align_cluster_dist"]
        s.alignment.detection.ellipse_fill_ratio_min = snapshot["align_ellipse_ratio_min"]
        s.alignment.detection.ellipse_fill_ratio_max = snapshot["align_ellipse_ratio_max"]
        s.alignment.color.hue_tolerances = snapshot["align_hue_tolerances"]
        s.alignment.color.saturation_tolerance = snapshot["align_sat_tolerance"]
        s.alignment.color.value_tolerance = snapshot["align_val_tolerance"]
        s.alignment.color.low_saturation_threshold = snapshot["align_low_sat_threshold"]
        s.alignment.color.bgr_tolerance_multiplier = snapshot["align_bgr_multiplier"]
        s.alignment.scoring.size_difference_weight = snapshot["align_size_weight"]
        s.alignment.line.hue_tolerances = snapshot["align_line_hue_tolerances"]

        # Item Defaults
        from settings import ItemDefaults, DefaultStyleSettings, DefaultContentsSettings
        s.item_defaults = {}
        for kind, d in snapshot.get("item_defaults", {}).items():
            st = d.get("style", {})
            co = d.get("contents", {})
            s.item_defaults[kind] = ItemDefaults(
                style=DefaultStyleSettings(
                    pen_color=st.get("pen_color", "#FF0000FF"),
                    pen_width=st.get("pen_width", 2),
                    line_dash=st.get("line_dash", "solid"),
                    fill_color=st.get("fill_color", "#00000000"),
                ),
                contents=DefaultContentsSettings(
                    halign=co.get("halign", "left"),
                    valign=co.get("valign", "top"),
                    spacing=co.get("spacing", 0.0),
                    color=co.get("color", "#FF00FFFF"),
                    font_family=co.get("font_family", ""),
                    font_size=co.get("font_size", 12),
                    margin_left=co.get("margin_left", 0.0),
                    margin_right=co.get("margin_right", 0.0),
                    margin_top=co.get("margin_top", 0.0),
                    margin_bottom=co.get("margin_bottom", 0.0),
                    wrap=co.get("wrap", True),
                    flow_type=co.get("flow_type", "none"),
                    text_box_width=co.get("text_box_width", 0.0),
                    text_box_height=co.get("text_box_height", 0.0),
                ),
            )

        # Gemini
        s.gemini.models = snapshot["gemini_models"]
        s.gemini.default_model = snapshot["gemini_default_model"]

        # External Tools
        s.external_tools.java_path = snapshot["tools_java_path"]
        s.external_tools.plantuml_jar_path = snapshot["tools_puml_jar_path"]
        s.external_tools.nodejs_path = snapshot["tools_nodejs_path"]
        s.external_tools.mmdc_path = snapshot["tools_mmdc_path"]
        s.external_tools.mmdc_png_scale = snapshot["tools_mmdc_png_scale"]
        s.external_tools.c4_shapes_per_row = snapshot["tools_c4_shapes_per_row"]
        s.external_tools.c4_boundaries_per_row = snapshot["tools_c4_boundaries_per_row"]

    # =========================================================================
    # Button Handlers
    # =========================================================================

    def _on_ok(self):
        """Handle OK button - save and close."""
        self._save_settings()
        self.accept()

    def _on_cancel(self):
        """Handle Cancel button - restore original settings and close."""
        self._restore_from_snapshot(self._original_settings)
        self.reject()

    def _on_apply(self):
        """Handle Apply button - save and apply theme immediately."""
        self._save_settings()
        # Update snapshot so Cancel won't undo applied changes
        self._original_settings = self._snapshot_settings()
        # Apply theme immediately
        self._apply_theme_to_app()

    def _on_restore_defaults(self):
        """Handle Restore Defaults button - load built-in defaults into the UI.

        Restores the currently displayed layer's widgets to built-in defaults.
        Does not write to any file until Apply/OK is clicked.
        """
        from settings import AppSettings
        self._load_settings(AppSettings())

    def selected_style(self) -> str:
        """Get the currently selected theme for immediate application."""
        return self.theme_combo.currentText()

    def _apply_theme_to_app(self):
        """Apply the current theme to the application immediately."""
        from PyQt6.QtWidgets import QApplication
        new_style = self.theme_combo.currentText()
        app = QApplication.instance()
        current_style = getattr(app, "_current_style", None)

        if new_style != current_style and new_style in STYLES:
            app.setStyleSheet(STYLES[new_style])
            app._current_style = new_style

            # Update parent window's icons and colors if available
            if self._parent_window and hasattr(self._parent_window, "_update_toolbar_icons"):
                self._parent_window._update_toolbar_icons(new_style)
            if self._parent_window and hasattr(self._parent_window, "_update_default_text_color"):
                self._parent_window._update_default_text_color(new_style)
            if self._parent_window and hasattr(self._parent_window, "_update_editor_colors"):
                self._parent_window._update_editor_colors(new_style)
            if self._parent_window and hasattr(self._parent_window, "_update_draft_dock_icons"):
                self._parent_window._update_draft_dock_icons(new_style)
