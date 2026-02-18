"""
settings.py

Persistent settings management for PictoSync.

Handles cross-platform settings storage using TOML format with platformdirs
for proper user config directory detection.

Settings file location:
    - Windows: %APPDATA%/pictosync/settings.toml
    - macOS: ~/Library/Application Support/pictosync/settings.toml
    - Linux: ~/.config/pictosync/settings.toml

Default values are documented in comments throughout this file.
If settings.toml is corrupted, these defaults will be used.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import platformdirs

# TOML reading - use tomllib for Python 3.11+, tomli for earlier versions
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import tomli_w

APP_NAME = "pictosync"

# Global settings manager instance (singleton)
_settings_manager: Optional["SettingsManager"] = None


def get_settings() -> "SettingsManager":
    """Get the global settings manager instance.

    Returns:
        The singleton SettingsManager instance.
    """
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager


# =============================================================================
# Editor Settings
# =============================================================================

@dataclass
class EditorFontSettings:
    """Editor font settings.

    Defaults:
        family: "Consolas"
        size: 10
        tab_width: 4
    """
    family: str = "Consolas"  # Default: "Consolas"
    size: int = 10            # Default: 10 points
    tab_width: int = 4        # Default: 4 characters


@dataclass
class EditorLineNumberSettings:
    """Line number gutter settings.

    Defaults:
        left_margin: 8
        right_margin: 4
        highlight_bar_width: 4
    """
    left_margin: int = 8           # Default: 8 pixels
    right_margin: int = 4          # Default: 4 pixels
    highlight_bar_width: int = 4   # Default: 4 pixels


@dataclass
class EditorFoldingSettings:
    """Code folding settings.

    Defaults:
        width: 14
    """
    width: int = 14  # Default: 14 pixels


@dataclass
class EditorSyntaxSettings:
    """JSON syntax highlighting colors.

    Defaults:
        key_color: "#2E86C1"
        key_bold: True
        string_color: "#27AE60"
        number_color: "#8E44AD"
        keyword_color: "#D35400"
        keyword_bold: True
        brace_color: "#566573"
        brace_bold: True
    """
    key_color: str = "#2E86C1"       # Default: blue
    key_bold: bool = True            # Default: True
    string_color: str = "#27AE60"    # Default: green
    number_color: str = "#8E44AD"    # Default: purple
    keyword_color: str = "#D35400"   # Default: orange
    keyword_bold: bool = True        # Default: True
    brace_color: str = "#566573"     # Default: gray
    brace_bold: bool = True          # Default: True


@dataclass
class EditorSettings:
    """All editor-related settings.

    Contains nested settings for font, line numbers, folding, and syntax.
    """
    font: EditorFontSettings = field(default_factory=EditorFontSettings)
    line_numbers: EditorLineNumberSettings = field(default_factory=EditorLineNumberSettings)
    folding: EditorFoldingSettings = field(default_factory=EditorFoldingSettings)
    syntax: EditorSyntaxSettings = field(default_factory=EditorSyntaxSettings)


# =============================================================================
# Canvas Settings
# =============================================================================

@dataclass
class CanvasHandleSettings:
    """Resize handle settings.

    Defaults:
        size: 8.0
        hit_distance: 10.0
        border_color: "#0078D7"
        fill_color: "#FFFFFF"
    """
    size: float = 8.0                 # Default: 8.0 pixels
    hit_distance: float = 10.0        # Default: 10.0 pixels
    border_color: str = "#0078D7"     # Default: blue
    fill_color: str = "#FFFFFF"       # Default: white


@dataclass
class CanvasShapeSettings:
    """Shape drawing settings.

    Defaults:
        min_size: 5.0
        default_dash_length: 30.0
        default_dash_solid_percent: 50.0
        rect_text_padding: 4
        roundedrect_text_padding_factor: 0.3
        ellipse_text_padding_base: 8
        ellipse_text_padding_ratio: 0.1
        default_rounded_radius: 10
    """
    min_size: float = 5.0                        # Default: 5.0 pixels
    default_dash_length: float = 30.0            # Default: 30.0 pixels
    default_dash_solid_percent: float = 50.0     # Default: 50.0%
    rect_text_padding: int = 4                   # Default: 4 pixels
    roundedrect_text_padding_factor: float = 0.3 # Default: 0.3
    ellipse_text_padding_base: int = 8           # Default: 8 pixels
    ellipse_text_padding_ratio: float = 0.1      # Default: 0.1
    default_rounded_radius: int = 10             # Default: 10 pixels


@dataclass
class CanvasLineSettings:
    """Line drawing settings.

    Defaults:
        dash_length: 30.0
        dash_solid_percent: 50.0
        text_box_padding: 4
        hit_area_width: 20.0
        arrow_min_multiplier: 2
        min_text_box_size: 30.0
        min_gap_pixels: 2.0
    """
    dash_length: float = 30.0          # Default: 30.0 pixels
    dash_solid_percent: float = 50.0   # Default: 50.0%
    text_box_padding: int = 4          # Default: 4 pixels
    hit_area_width: float = 20.0       # Default: 20.0 pixels
    arrow_min_multiplier: int = 2      # Default: 2x pen width
    min_text_box_size: float = 30.0    # Default: 30.0 pixels
    min_gap_pixels: float = 2.0        # Default: 2.0 pixels


@dataclass
class CanvasSelectionSettings:
    """Selection appearance settings.

    Defaults:
        outline_color: "#0078D7"
    """
    outline_color: str = "#0078D7"  # Default: blue


@dataclass
class CanvasZOrderSettings:
    """Z-order layering settings.

    Defaults:
        base: 1000
        step: 10
    """
    base: int = 1000  # Default: 1000
    step: int = 10    # Default: 10


@dataclass
class CanvasZoomSettings:
    """Zoom behavior settings.

    Defaults:
        wheel_factor: 1.15
    """
    wheel_factor: float = 1.15  # Default: 1.15 (15% per scroll step)


@dataclass
class CanvasSettings:
    """All canvas-related settings."""
    handles: CanvasHandleSettings = field(default_factory=CanvasHandleSettings)
    shapes: CanvasShapeSettings = field(default_factory=CanvasShapeSettings)
    lines: CanvasLineSettings = field(default_factory=CanvasLineSettings)
    selection: CanvasSelectionSettings = field(default_factory=CanvasSelectionSettings)
    zorder: CanvasZOrderSettings = field(default_factory=CanvasZOrderSettings)
    zoom: CanvasZoomSettings = field(default_factory=CanvasZoomSettings)


# =============================================================================
# Alignment Settings
# =============================================================================

@dataclass
class AlignmentDetectionSettings:
    """Shape detection settings for alignment.

    Defaults:
        default_min_area: 500
        min_shape_width: 15
        min_shape_height: 15
        center_clustering_distance: 10
        ellipse_fill_ratio_min: 0.75
        ellipse_fill_ratio_max: 0.85
    """
    default_min_area: int = 500               # Default: 500 square pixels
    min_shape_width: int = 15                 # Default: 15 pixels
    min_shape_height: int = 15                # Default: 15 pixels
    center_clustering_distance: int = 10      # Default: 10 pixels
    ellipse_fill_ratio_min: float = 0.75      # Default: 0.75
    ellipse_fill_ratio_max: float = 0.85      # Default: 0.85


@dataclass
class AlignmentColorSettings:
    """Color matching settings for alignment.

    Defaults:
        hue_tolerances: [10, 15, 20, 25, 30]
        saturation_tolerance: 80
        value_tolerance: 80
        low_saturation_threshold: 30
        bgr_tolerance_multiplier: 4
    """
    hue_tolerances: List[int] = field(default_factory=lambda: [10, 15, 20, 25, 30])  # Default: [10, 15, 20, 25, 30]
    saturation_tolerance: int = 80            # Default: 80
    value_tolerance: int = 80                 # Default: 80
    low_saturation_threshold: int = 30        # Default: 30
    bgr_tolerance_multiplier: int = 4         # Default: 4


@dataclass
class AlignmentScoringSettings:
    """Scoring weights for alignment matching.

    Defaults:
        size_difference_weight: 50
    """
    size_difference_weight: int = 50  # Default: 50


@dataclass
class AlignmentLineSettings:
    """Line alignment settings.

    Defaults:
        hue_tolerances: [15, 25, 35]
    """
    hue_tolerances: List[int] = field(default_factory=lambda: [15, 25, 35])  # Default: [15, 25, 35]


@dataclass
class AlignmentSettings:
    """All alignment-related settings."""
    detection: AlignmentDetectionSettings = field(default_factory=AlignmentDetectionSettings)
    color: AlignmentColorSettings = field(default_factory=AlignmentColorSettings)
    scoring: AlignmentScoringSettings = field(default_factory=AlignmentScoringSettings)
    line: AlignmentLineSettings = field(default_factory=AlignmentLineSettings)


# =============================================================================
# Default Text Settings
# =============================================================================

@dataclass
class DefaultTextSettings:
    """Default text formatting settings for annotations.

    Defaults:
        label_align: "center"
        label_size: 12
        tech_align: "center"
        tech_size: 10
        note_align: "center"
        note_size: 10
        vertical_align: "top"
        line_spacing: 0.0
        text_box_width: 0.0
        text_box_height: 0.0
    """
    label_align: str = "center"       # Default: "center"
    label_size: int = 12              # Default: 12 points
    tech_align: str = "center"        # Default: "center"
    tech_size: int = 10               # Default: 10 points
    note_align: str = "center"        # Default: "center"
    note_size: int = 10               # Default: 10 points
    vertical_align: str = "top"       # Default: "top"
    line_spacing: float = 0.0         # Default: 0.0 em
    text_box_width: float = 0.0       # Default: 0.0 (auto)
    text_box_height: float = 0.0      # Default: 0.0 (auto)


# =============================================================================
# Main App Settings
# =============================================================================

@dataclass
class AppSettings:
    """Application settings with default values.

    Attributes:
        theme: The UI theme name (must match a key in styles.STYLES).
        workspace_dir: Default directory for saving/loading projects.
        editor: Editor-related settings.
        canvas: Canvas-related settings.
        alignment: Alignment-related settings.
        defaults: Default text formatting settings.
    """
    # UI Settings
    theme: str = "Tailwind"  # Default: "Tailwind"

    # Workspace directory for project save/load (empty = ~/Documents/PictoSync)
    workspace_dir: str = ""

    # PPTX export defaults to source file directory when True
    pptx_export_to_source_dir: bool = True

    # Nested settings categories
    editor: EditorSettings = field(default_factory=EditorSettings)
    canvas: CanvasSettings = field(default_factory=CanvasSettings)
    alignment: AlignmentSettings = field(default_factory=AlignmentSettings)
    defaults: DefaultTextSettings = field(default_factory=DefaultTextSettings)


# =============================================================================
# Settings Manager
# =============================================================================

class SettingsManager:
    """Manages loading, saving, and accessing application settings.

    Settings are stored in a TOML file at the platform-appropriate location.
    If the settings file doesn't exist, defaults are used and the file is
    created on first save.

    Args:
        app_name: Application name used for the config directory.
    """

    def __init__(self, app_name: str = APP_NAME):
        self.settings_dir = Path(platformdirs.user_config_dir(app_name))
        self.settings_file = self.settings_dir / "settings.toml"
        self.settings = self.load()
        self._needs_save = not self.settings_file.exists()  # Save if file didn't exist

    def ensure_file_complete(self) -> None:
        """Ensure settings file exists with all sections. Call once at startup."""
        if self._needs_save or not self.settings_file.exists():
            self.save()
            self._needs_save = False

    def load(self) -> AppSettings:
        """Load settings from the TOML file.

        Returns:
            AppSettings instance with values from file or defaults if file
            doesn't exist or is invalid.
        """
        if not self.settings_file.exists():
            return AppSettings()

        try:
            with open(self.settings_file, "rb") as f:
                data = tomllib.load(f)

            return self._parse_toml(data)
        except Exception:
            # If file is corrupted or invalid, return defaults
            return AppSettings()

    def _parse_toml(self, data: Dict[str, Any]) -> AppSettings:
        """Parse TOML data into AppSettings.

        Args:
            data: Parsed TOML dictionary.

        Returns:
            AppSettings instance populated from TOML data.
        """
        settings = AppSettings()

        # General section
        general = data.get("general", {})
        settings.theme = general.get("theme", settings.theme)
        settings.workspace_dir = general.get("workspace_dir", settings.workspace_dir)
        settings.pptx_export_to_source_dir = general.get("pptx_export_to_source_dir", settings.pptx_export_to_source_dir)

        # Editor section
        editor = data.get("editor", {})
        if "font" in editor:
            font = editor["font"]
            settings.editor.font.family = font.get("family", settings.editor.font.family)
            settings.editor.font.size = font.get("size", settings.editor.font.size)
            settings.editor.font.tab_width = font.get("tab_width", settings.editor.font.tab_width)
        if "line_numbers" in editor:
            ln = editor["line_numbers"]
            settings.editor.line_numbers.left_margin = ln.get("left_margin", settings.editor.line_numbers.left_margin)
            settings.editor.line_numbers.right_margin = ln.get("right_margin", settings.editor.line_numbers.right_margin)
            settings.editor.line_numbers.highlight_bar_width = ln.get("highlight_bar_width", settings.editor.line_numbers.highlight_bar_width)
        if "folding" in editor:
            fold = editor["folding"]
            settings.editor.folding.width = fold.get("width", settings.editor.folding.width)
        if "syntax" in editor:
            syn = editor["syntax"]
            settings.editor.syntax.key_color = syn.get("key_color", settings.editor.syntax.key_color)
            settings.editor.syntax.key_bold = syn.get("key_bold", settings.editor.syntax.key_bold)
            settings.editor.syntax.string_color = syn.get("string_color", settings.editor.syntax.string_color)
            settings.editor.syntax.number_color = syn.get("number_color", settings.editor.syntax.number_color)
            settings.editor.syntax.keyword_color = syn.get("keyword_color", settings.editor.syntax.keyword_color)
            settings.editor.syntax.keyword_bold = syn.get("keyword_bold", settings.editor.syntax.keyword_bold)
            settings.editor.syntax.brace_color = syn.get("brace_color", settings.editor.syntax.brace_color)
            settings.editor.syntax.brace_bold = syn.get("brace_bold", settings.editor.syntax.brace_bold)

        # Canvas section
        canvas = data.get("canvas", {})
        if "handles" in canvas:
            h = canvas["handles"]
            settings.canvas.handles.size = h.get("size", settings.canvas.handles.size)
            settings.canvas.handles.hit_distance = h.get("hit_distance", settings.canvas.handles.hit_distance)
            settings.canvas.handles.border_color = h.get("border_color", settings.canvas.handles.border_color)
            settings.canvas.handles.fill_color = h.get("fill_color", settings.canvas.handles.fill_color)
        if "shapes" in canvas:
            s = canvas["shapes"]
            settings.canvas.shapes.min_size = s.get("min_size", settings.canvas.shapes.min_size)
            settings.canvas.shapes.default_dash_length = s.get("default_dash_length", settings.canvas.shapes.default_dash_length)
            settings.canvas.shapes.default_dash_solid_percent = s.get("default_dash_solid_percent", settings.canvas.shapes.default_dash_solid_percent)
            settings.canvas.shapes.rect_text_padding = s.get("rect_text_padding", settings.canvas.shapes.rect_text_padding)
            settings.canvas.shapes.roundedrect_text_padding_factor = s.get("roundedrect_text_padding_factor", settings.canvas.shapes.roundedrect_text_padding_factor)
            settings.canvas.shapes.ellipse_text_padding_base = s.get("ellipse_text_padding_base", settings.canvas.shapes.ellipse_text_padding_base)
            settings.canvas.shapes.ellipse_text_padding_ratio = s.get("ellipse_text_padding_ratio", settings.canvas.shapes.ellipse_text_padding_ratio)
            settings.canvas.shapes.default_rounded_radius = s.get("default_rounded_radius", settings.canvas.shapes.default_rounded_radius)
        if "lines" in canvas:
            li = canvas["lines"]
            settings.canvas.lines.dash_length = li.get("dash_length", settings.canvas.lines.dash_length)
            settings.canvas.lines.dash_solid_percent = li.get("dash_solid_percent", settings.canvas.lines.dash_solid_percent)
            settings.canvas.lines.text_box_padding = li.get("text_box_padding", settings.canvas.lines.text_box_padding)
            settings.canvas.lines.hit_area_width = li.get("hit_area_width", settings.canvas.lines.hit_area_width)
            settings.canvas.lines.arrow_min_multiplier = li.get("arrow_min_multiplier", settings.canvas.lines.arrow_min_multiplier)
            settings.canvas.lines.min_text_box_size = li.get("min_text_box_size", settings.canvas.lines.min_text_box_size)
            settings.canvas.lines.min_gap_pixels = li.get("min_gap_pixels", settings.canvas.lines.min_gap_pixels)
        if "selection" in canvas:
            sel = canvas["selection"]
            settings.canvas.selection.outline_color = sel.get("outline_color", settings.canvas.selection.outline_color)
        if "zorder" in canvas:
            z = canvas["zorder"]
            settings.canvas.zorder.base = z.get("base", settings.canvas.zorder.base)
            settings.canvas.zorder.step = z.get("step", settings.canvas.zorder.step)
        if "zoom" in canvas:
            zm = canvas["zoom"]
            settings.canvas.zoom.wheel_factor = zm.get("wheel_factor", settings.canvas.zoom.wheel_factor)

        # Alignment section
        alignment = data.get("alignment", {})
        if "detection" in alignment:
            d = alignment["detection"]
            settings.alignment.detection.default_min_area = d.get("default_min_area", settings.alignment.detection.default_min_area)
            settings.alignment.detection.min_shape_width = d.get("min_shape_width", settings.alignment.detection.min_shape_width)
            settings.alignment.detection.min_shape_height = d.get("min_shape_height", settings.alignment.detection.min_shape_height)
            settings.alignment.detection.center_clustering_distance = d.get("center_clustering_distance", settings.alignment.detection.center_clustering_distance)
            settings.alignment.detection.ellipse_fill_ratio_min = d.get("ellipse_fill_ratio_min", settings.alignment.detection.ellipse_fill_ratio_min)
            settings.alignment.detection.ellipse_fill_ratio_max = d.get("ellipse_fill_ratio_max", settings.alignment.detection.ellipse_fill_ratio_max)
        if "color" in alignment:
            c = alignment["color"]
            settings.alignment.color.hue_tolerances = c.get("hue_tolerances", settings.alignment.color.hue_tolerances)
            settings.alignment.color.saturation_tolerance = c.get("saturation_tolerance", settings.alignment.color.saturation_tolerance)
            settings.alignment.color.value_tolerance = c.get("value_tolerance", settings.alignment.color.value_tolerance)
            settings.alignment.color.low_saturation_threshold = c.get("low_saturation_threshold", settings.alignment.color.low_saturation_threshold)
            settings.alignment.color.bgr_tolerance_multiplier = c.get("bgr_tolerance_multiplier", settings.alignment.color.bgr_tolerance_multiplier)
        if "scoring" in alignment:
            sc = alignment["scoring"]
            settings.alignment.scoring.size_difference_weight = sc.get("size_difference_weight", settings.alignment.scoring.size_difference_weight)
        if "line" in alignment:
            ln = alignment["line"]
            settings.alignment.line.hue_tolerances = ln.get("hue_tolerances", settings.alignment.line.hue_tolerances)

        # Defaults section
        defaults = data.get("defaults", {})
        if "text" in defaults:
            t = defaults["text"]
            settings.defaults.label_align = t.get("label_align", settings.defaults.label_align)
            settings.defaults.label_size = t.get("label_size", settings.defaults.label_size)
            settings.defaults.tech_align = t.get("tech_align", settings.defaults.tech_align)
            settings.defaults.tech_size = t.get("tech_size", settings.defaults.tech_size)
            settings.defaults.note_align = t.get("note_align", settings.defaults.note_align)
            settings.defaults.note_size = t.get("note_size", settings.defaults.note_size)
            settings.defaults.vertical_align = t.get("vertical_align", settings.defaults.vertical_align)
            settings.defaults.line_spacing = t.get("line_spacing", settings.defaults.line_spacing)
            settings.defaults.text_box_width = t.get("text_box_width", settings.defaults.text_box_width)
            settings.defaults.text_box_height = t.get("text_box_height", settings.defaults.text_box_height)

        return settings

    def save(self) -> None:
        """Save current settings to the TOML file.

        Creates the settings directory if it doesn't exist.
        """
        # Ensure directory exists
        self.settings_dir.mkdir(parents=True, exist_ok=True)

        # Convert settings to TOML structure
        data = self._to_toml_dict()

        with open(self.settings_file, "wb") as f:
            tomli_w.dump(data, f)

    def _to_toml_dict(self) -> Dict[str, Any]:
        """Convert settings to a TOML-compatible dictionary structure.

        Returns:
            Dictionary organized by TOML sections.
        """
        s = self.settings
        return {
            "general": {
                "theme": s.theme,
                "workspace_dir": s.workspace_dir,
                "pptx_export_to_source_dir": s.pptx_export_to_source_dir,
            },
            "editor": {
                "font": {
                    "family": s.editor.font.family,
                    "size": s.editor.font.size,
                    "tab_width": s.editor.font.tab_width,
                },
                "line_numbers": {
                    "left_margin": s.editor.line_numbers.left_margin,
                    "right_margin": s.editor.line_numbers.right_margin,
                    "highlight_bar_width": s.editor.line_numbers.highlight_bar_width,
                },
                "folding": {
                    "width": s.editor.folding.width,
                },
                "syntax": {
                    "key_color": s.editor.syntax.key_color,
                    "key_bold": s.editor.syntax.key_bold,
                    "string_color": s.editor.syntax.string_color,
                    "number_color": s.editor.syntax.number_color,
                    "keyword_color": s.editor.syntax.keyword_color,
                    "keyword_bold": s.editor.syntax.keyword_bold,
                    "brace_color": s.editor.syntax.brace_color,
                    "brace_bold": s.editor.syntax.brace_bold,
                },
            },
            "canvas": {
                "handles": {
                    "size": s.canvas.handles.size,
                    "hit_distance": s.canvas.handles.hit_distance,
                    "border_color": s.canvas.handles.border_color,
                    "fill_color": s.canvas.handles.fill_color,
                },
                "shapes": {
                    "min_size": s.canvas.shapes.min_size,
                    "default_dash_length": s.canvas.shapes.default_dash_length,
                    "default_dash_solid_percent": s.canvas.shapes.default_dash_solid_percent,
                    "rect_text_padding": s.canvas.shapes.rect_text_padding,
                    "roundedrect_text_padding_factor": s.canvas.shapes.roundedrect_text_padding_factor,
                    "ellipse_text_padding_base": s.canvas.shapes.ellipse_text_padding_base,
                    "ellipse_text_padding_ratio": s.canvas.shapes.ellipse_text_padding_ratio,
                    "default_rounded_radius": s.canvas.shapes.default_rounded_radius,
                },
                "lines": {
                    "dash_length": s.canvas.lines.dash_length,
                    "dash_solid_percent": s.canvas.lines.dash_solid_percent,
                    "text_box_padding": s.canvas.lines.text_box_padding,
                    "hit_area_width": s.canvas.lines.hit_area_width,
                    "arrow_min_multiplier": s.canvas.lines.arrow_min_multiplier,
                    "min_text_box_size": s.canvas.lines.min_text_box_size,
                    "min_gap_pixels": s.canvas.lines.min_gap_pixels,
                },
                "selection": {
                    "outline_color": s.canvas.selection.outline_color,
                },
                "zorder": {
                    "base": s.canvas.zorder.base,
                    "step": s.canvas.zorder.step,
                },
                "zoom": {
                    "wheel_factor": s.canvas.zoom.wheel_factor,
                },
            },
            "alignment": {
                "detection": {
                    "default_min_area": s.alignment.detection.default_min_area,
                    "min_shape_width": s.alignment.detection.min_shape_width,
                    "min_shape_height": s.alignment.detection.min_shape_height,
                    "center_clustering_distance": s.alignment.detection.center_clustering_distance,
                    "ellipse_fill_ratio_min": s.alignment.detection.ellipse_fill_ratio_min,
                    "ellipse_fill_ratio_max": s.alignment.detection.ellipse_fill_ratio_max,
                },
                "color": {
                    "hue_tolerances": s.alignment.color.hue_tolerances,
                    "saturation_tolerance": s.alignment.color.saturation_tolerance,
                    "value_tolerance": s.alignment.color.value_tolerance,
                    "low_saturation_threshold": s.alignment.color.low_saturation_threshold,
                    "bgr_tolerance_multiplier": s.alignment.color.bgr_tolerance_multiplier,
                },
                "scoring": {
                    "size_difference_weight": s.alignment.scoring.size_difference_weight,
                },
                "line": {
                    "hue_tolerances": s.alignment.line.hue_tolerances,
                },
            },
            "defaults": {
                "text": {
                    "label_align": s.defaults.label_align,
                    "label_size": s.defaults.label_size,
                    "tech_align": s.defaults.tech_align,
                    "tech_size": s.defaults.tech_size,
                    "note_align": s.defaults.note_align,
                    "note_size": s.defaults.note_size,
                    "vertical_align": s.defaults.vertical_align,
                    "line_spacing": s.defaults.line_spacing,
                    "text_box_width": s.defaults.text_box_width,
                    "text_box_height": s.defaults.text_box_height,
                },
            },
        }

    def to_toml(self) -> str:
        """Convert current settings to a TOML-formatted string.

        Returns:
            TOML representation of the current settings.
        """
        data = self._to_toml_dict()
        return tomli_w.dumps(data)

    def get_workspace_dir(self) -> Path:
        """Get the resolved workspace directory path.

        Returns:
            Path to workspace directory. Falls back to ~/Documents/PictoSync
            if workspace_dir setting is empty.
        """
        if self.settings.workspace_dir:
            return Path(self.settings.workspace_dir)
        return Path.home() / "Documents" / "PictoSync"

    def get_settings_path(self) -> Path:
        """Get the path to the settings file.

        Returns:
            Path object pointing to the settings file location.
        """
        return self.settings_file
