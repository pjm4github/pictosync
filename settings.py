"""
settings.py

Persistent settings management for PictoSync.

Handles cross-platform settings storage using TOML format with platformdirs
for proper user config directory detection.

Settings file locations:
    System (built-in defaults):
        - Windows: %LOCALAPPDATA%/pictosync/settings.toml
        - Linux:   ~/.local/share/pictosync/settings.toml
        - macOS:   ~/Library/Application Support/pictosync/settings.toml
    User (per-user overrides):
        - All platforms: ~/Documents/pictosync/settings.toml

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


def get_documents_folder() -> Path:
    """Return the shell Documents folder, resolving OneDrive redirection on Windows.

    On Windows, ``~/Documents`` may point to an OneDrive-redirected path rather
    than the true shell Documents folder.  ``SHGetFolderPathW`` asks the shell
    directly, so it always returns the canonical location regardless of
    OneDrive sync settings.

    On macOS / Linux the function simply returns ``~/Documents``.

    Returns:
        Path to the user's Documents folder.
    """
    if sys.platform == "win32":
        import ctypes
        buf = ctypes.create_unicode_buffer(260)
        # CSIDL 0x0005 = CSIDL_PERSONAL = "My Documents"
        ctypes.windll.shell32.SHGetFolderPathW(0, 0x0005, 0, 0, buf)
        resolved = buf.value
        if resolved:
            return Path(resolved)
    return Path.home() / "Documents"

# Console debug logging — toggle via settings dialog (future)
DEBUG_LOG: bool = False

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
class DefaultContentsSettings:
    """Default values for annotationContents fields.

    These map 1-to-1 to the annotationContents JSON schema fields and are
    applied when creating new annotations or when a field is absent from a
    loaded file.

    Defaults:
        halign: "center"
        valign: "top"
        spacing: 0.0
        color: "#FFFF00FF"
        font_family: ""
        font_size: 12
        margin_left: 0.0
        margin_right: 0.0
        margin_top: 0.0
        margin_bottom: 0.0
        wrap: True
        flow_type: "none"
        text_box_width: 0.0
        text_box_height: 0.0
        image_url: ""
        image_anchor: 0
    """
    halign: str = "left"              # Default: "left"
    valign: str = "top"               # Default: "top"
    spacing: float = 0.0              # Default: 0.0 em
    color: str = "#FF00FFFF"          # Default: magenta (opaque)
    font_family: str = ""             # Default: "" (system sans-serif)
    font_size: int = 12               # Default: 12 points
    margin_left: float = 0.0          # Default: 0.0 px
    margin_right: float = 0.0         # Default: 0.0 px
    margin_top: float = 0.0           # Default: 0.0 px
    margin_bottom: float = 0.0        # Default: 0.0 px
    wrap: bool = True                 # Default: True
    flow_type: str = "none"           # Default: "none"
    text_box_width: float = 0.0       # Default: 0.0 (auto)
    text_box_height: float = 0.0      # Default: 0.0 (auto)
    image_url: str = ""               # Default: "" (none)
    image_anchor: int = 0             # Default: 0 (none)
    # overlay-2.0 rich-text defaults (None = not set / use built-in defaults)
    frame: Optional[Dict[str, Any]] = None           # TextFrame fields
    default_format: Optional[Dict[str, Any]] = None  # CharFormat fields


# Backwards-compatibility alias — remove once settings_dialog.py is migrated
DefaultTextSettings = DefaultContentsSettings


# =============================================================================
# Default Style Settings
# =============================================================================

@dataclass
class DefaultStyleSettings:
    """Default style values saved from the Format (Style) tab.

    Defaults:
        pen_color: "#FF0000FF"
        pen_width: 2
        line_dash: "solid"
        fill_color: "#00000000"
    """
    pen_color: str = "#FF0000FF"      # Default: red opaque
    pen_width: int = 2                # Default: 2 pixels
    line_dash: str = "solid"          # Default: "solid"
    fill_color: str = "#00000000"     # Default: transparent


# =============================================================================
# Per-Kind Item Defaults
# =============================================================================

@dataclass
class ItemDefaults:
    """Bundled style + contents defaults for one canvas item kind.

    Stored under ``[item_defaults.<kind>]`` in the user settings file.
    """
    style: DefaultStyleSettings = field(default_factory=DefaultStyleSettings)
    contents: DefaultContentsSettings = field(default_factory=DefaultContentsSettings)


# =============================================================================
# Gemini AI Settings
# =============================================================================

@dataclass
class GeminiSettings:
    """Gemini AI model settings.

    Defaults:
        models: ["gemini-2.5-flash-image", "gemini-3-pro-image-preview"]
        default_model: "gemini-2.5-flash-image"
    """
    models: List[str] = field(default_factory=lambda: [
        "gemini-2.5-flash-image",
        "gemini-3-pro-image-preview",
    ])
    default_model: str = "gemini-2.5-flash-image"


# =============================================================================
# External Tools Settings
# =============================================================================

@dataclass
class ExternalToolsSettings:
    """Paths to external CLI tools used for diagram import.

    Empty strings mean "auto-detect" (environment variable, then system PATH).
    When a path is set here, it takes priority over auto-detection.

    Defaults:
        java_path: ""
        plantuml_jar_path: ""
        nodejs_path: ""
        mmdc_path: ""
        mmdc_png_scale: 4
        c4_shapes_per_row: 4
        c4_boundaries_per_row: 2
    """
    java_path: str = ""              # Default: "" (auto-detect)
    plantuml_jar_path: str = ""      # Default: "" (auto-detect)
    nodejs_path: str = ""            # Default: "" (auto-detect)
    mmdc_path: str = ""              # Default: "" (auto-detect)
    mmdc_png_scale: int = 4          # Default: 4 (CSS scale factor for PNG output)
    c4_shapes_per_row: int = 4       # Default: 4 (Mermaid C4 c4ShapeInRow)
    c4_boundaries_per_row: int = 2   # Default: 2 (Mermaid C4 c4BoundaryInRow)


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
    defaults: DefaultContentsSettings = field(default_factory=DefaultContentsSettings)
    style: DefaultStyleSettings = field(default_factory=DefaultStyleSettings)
    item_defaults: Dict[str, ItemDefaults] = field(default_factory=dict)
    gemini: GeminiSettings = field(default_factory=GeminiSettings)
    external_tools: ExternalToolsSettings = field(default_factory=ExternalToolsSettings)


# =============================================================================
# Settings Manager
# =============================================================================

def _build_item_defaults_toml(id_obj: "ItemDefaults") -> Dict[str, Any]:
    """Serialize one ItemDefaults to a TOML-compatible dict.

    Includes overlay-2.0 ``frame`` and ``default_format`` sub-tables when
    they have been saved (i.e. are not None).
    """
    contents: Dict[str, Any] = {
        "halign":           id_obj.contents.halign,
        "valign":           id_obj.contents.valign,
        "spacing":          id_obj.contents.spacing,
        "color":            id_obj.contents.color,
        "font_family":      id_obj.contents.font_family,
        "font_size":        id_obj.contents.font_size,
        "margin_left":      id_obj.contents.margin_left,
        "margin_right":     id_obj.contents.margin_right,
        "margin_top":       id_obj.contents.margin_top,
        "margin_bottom":    id_obj.contents.margin_bottom,
        "wrap":             id_obj.contents.wrap,
        "flow_type":        id_obj.contents.flow_type,
        "text_box_width":   id_obj.contents.text_box_width,
        "text_box_height":  id_obj.contents.text_box_height,
        "image_anchor":     id_obj.contents.image_anchor,
    }
    if id_obj.contents.frame is not None:
        contents["frame"] = id_obj.contents.frame
    if id_obj.contents.default_format is not None:
        contents["default_format"] = id_obj.contents.default_format
    return {
        "style": {
            "pen_color":  id_obj.style.pen_color,
            "pen_width":  id_obj.style.pen_width,
            "line_dash":  id_obj.style.line_dash,
            "fill_color": id_obj.style.fill_color,
        },
        "contents": contents,
    }


class SettingsManager:
    """Manages loading, saving, and accessing application settings.

    Two-tier file layout
    --------------------
    system_settings_file  — machine-level defaults (AppData\\Local\\pictosync on Windows)
    user_settings_file    — per-user overrides   (~/Documents/pictosync on all platforms)

    Load order: built-in Python defaults → system file → user file.
    "Save as Default" writes only to the user file (targeted merge).

    Args:
        app_name: Application name used for the config directory.
    """

    def __init__(self, app_name: str = APP_NAME):
        # ── System settings: AppData\Local\pictosync (Windows)
        #                     ~/.local/share/pictosync  (Linux)
        #                     ~/Library/Application Support/pictosync (macOS)
        self.system_settings_dir = Path(
            platformdirs.user_data_dir(app_name, appauthor=False)
        )
        self.system_settings_file = self.system_settings_dir / "settings.toml"

        # ── User settings: <Documents>/pictosync/settings.toml (all platforms)
        #    Uses SHGetFolderPathW on Windows so OneDrive redirection is resolved.
        self.user_settings_dir = get_documents_folder() / app_name
        self.user_settings_file = self.user_settings_dir / "settings.toml"

        # Backward-compat aliases used by the rest of the codebase
        self.settings_dir = self.user_settings_dir
        self.settings_file = self.user_settings_file

        self.settings = self.load()
        self._needs_save = not self.user_settings_file.exists()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ensure_file_complete(self) -> None:
        """Ensure both settings files exist. Call once at startup."""
        if not self.system_settings_file.exists():
            self.save_system()
        if self._needs_save or not self.user_settings_file.exists():
            self.save()
            self._needs_save = False

    def save_system(self) -> None:
        """Save built-in defaults to the system settings file."""
        self.system_settings_dir.mkdir(parents=True, exist_ok=True)
        with open(self.system_settings_file, "wb") as f:
            tomli_w.dump(self._to_toml_dict(AppSettings()), f)

    def load_layer(self, path: "Path") -> "AppSettings":
        """Load a single settings file in isolation (no cascade).

        Returns AppSettings populated only from that file's values,
        falling back to built-in defaults for anything not present.

        Args:
            path: Path to the TOML file to load.

        Returns:
            AppSettings populated from the file.
        """
        settings = AppSettings()
        if path.exists():
            try:
                with open(path, "rb") as f:
                    self._apply_toml(settings, tomllib.load(f))
            except Exception:
                pass
        return settings

    def save_to(self, path: Path, settings: "AppSettings") -> None:
        """Save *settings* to an arbitrary path.

        Args:
            path: Destination TOML file path.
            settings: AppSettings to serialise.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            tomli_w.dump(self._to_toml_dict(settings), f)

    def load(self) -> AppSettings:
        """Load settings using three-layer cascade.

        Layers (each overrides the previous):
          1. Built-in Python defaults (AppSettings())
          2. System settings file
          3. User settings file

        Returns:
            Merged AppSettings instance.
        """
        settings = AppSettings()
        for path in (self.system_settings_file, self.user_settings_file):
            if path.exists():
                try:
                    with open(path, "rb") as f:
                        self._apply_toml(settings, tomllib.load(f))
                except Exception:
                    pass  # Corrupted file — keep what we have
        return settings

    def save(self) -> None:
        """Save *all* current settings to the user settings file."""
        self.user_settings_dir.mkdir(parents=True, exist_ok=True)
        with open(self.user_settings_file, "wb") as f:
            tomli_w.dump(self._to_toml_dict(), f)

    def save_user_item_defaults(
        self,
        kind: str,
        style: Dict[str, Any],
        contents: Dict[str, Any],
    ) -> None:
        """Merge item defaults for *kind* into the user settings file.

        Only the ``[item_defaults.<kind>]`` section is written; all other
        settings already in the user file are preserved unchanged.

        Args:
            kind: Canvas item kind string (e.g. "rect", "roundedrect").
            style: Dict of DefaultStyleSettings field values.
            contents: Dict of DefaultContentsSettings field values (no image_url).
        """
        # Load raw existing user TOML (preserve all other settings)
        raw: Dict[str, Any] = {}
        if self.user_settings_file.exists():
            try:
                with open(self.user_settings_file, "rb") as f:
                    raw = tomllib.load(f)
            except Exception:
                raw = {}

        # Update only the target kind sub-table
        item_defaults = raw.setdefault("item_defaults", {})
        item_defaults[kind] = {"style": style, "contents": contents}

        self.user_settings_dir.mkdir(parents=True, exist_ok=True)
        with open(self.user_settings_file, "wb") as f:
            tomli_w.dump(raw, f)

        # Reload in-memory settings so callers see the change immediately
        self.settings = self.load()

    def get_item_defaults(self, kind: str) -> "ItemDefaults":
        """Return defaults for *kind*, falling back to global defaults.

        Args:
            kind: Canvas item kind string.

        Returns:
            ItemDefaults with style + contents for this kind.
        """
        if kind in self.settings.item_defaults:
            return self.settings.item_defaults[kind]
        return ItemDefaults(
            style=self.settings.style,
            contents=self.settings.defaults,
        )

    def has_user_item_defaults(self, kind: str) -> bool:
        """Return True if the user settings file already has defaults for *kind*."""
        if not self.user_settings_file.exists():
            return False
        try:
            with open(self.user_settings_file, "rb") as f:
                raw = tomllib.load(f)
            return kind in raw.get("item_defaults", {})
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _apply_toml(self, settings: AppSettings, data: Dict[str, Any]) -> None:
        """Apply *data* (parsed TOML dict) onto *settings* in place.

        Called once per file in the load cascade so each layer overrides
        the previous without resetting unrelated fields.
        """
        # General section
        general = data.get("general", {})
        settings.theme = general.get("theme", settings.theme)
        settings.workspace_dir = general.get("workspace_dir", settings.workspace_dir)
        settings.pptx_export_to_source_dir = general.get(
            "pptx_export_to_source_dir", settings.pptx_export_to_source_dir
        )

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

        # Defaults section — reads [defaults.contents]; falls back to legacy [defaults.text]
        defaults = data.get("defaults", {})
        c = defaults.get("contents") or defaults.get("text") or {}
        if c:
            settings.defaults.halign = c.get("halign", c.get("label_align", settings.defaults.halign))
            settings.defaults.valign = c.get("valign", c.get("vertical_align", settings.defaults.valign))
            settings.defaults.spacing = c.get("spacing", c.get("line_spacing", settings.defaults.spacing))
            settings.defaults.color = c.get("color", settings.defaults.color)
            settings.defaults.font_family = c.get("font_family", settings.defaults.font_family)
            settings.defaults.font_size = c.get("font_size", c.get("label_size", settings.defaults.font_size))
            settings.defaults.margin_left = c.get("margin_left", settings.defaults.margin_left)
            settings.defaults.margin_right = c.get("margin_right", settings.defaults.margin_right)
            settings.defaults.margin_top = c.get("margin_top", settings.defaults.margin_top)
            settings.defaults.margin_bottom = c.get("margin_bottom", settings.defaults.margin_bottom)
            settings.defaults.wrap = c.get("wrap", settings.defaults.wrap)
            settings.defaults.flow_type = c.get("flow_type", settings.defaults.flow_type)
            settings.defaults.text_box_width = c.get("text_box_width", settings.defaults.text_box_width)
            settings.defaults.text_box_height = c.get("text_box_height", settings.defaults.text_box_height)
            settings.defaults.image_url = c.get("image_url", settings.defaults.image_url)
            settings.defaults.image_anchor = c.get("image_anchor", settings.defaults.image_anchor)

        st = defaults.get("style", {})
        if st:
            settings.style.pen_color = st.get("pen_color", settings.style.pen_color)
            settings.style.pen_width = int(st.get("pen_width", settings.style.pen_width))
            settings.style.line_dash = st.get("line_dash", settings.style.line_dash)
            settings.style.fill_color = st.get("fill_color", settings.style.fill_color)

        # Per-kind item defaults
        for kind, kind_data in data.get("item_defaults", {}).items():
            if not isinstance(kind_data, dict):
                continue
            id_obj = settings.item_defaults.setdefault(kind, ItemDefaults())
            _st = kind_data.get("style", {})
            if _st:
                id_obj.style.pen_color = _st.get("pen_color", id_obj.style.pen_color)
                id_obj.style.pen_width = int(_st.get("pen_width", id_obj.style.pen_width))
                id_obj.style.line_dash = _st.get("line_dash", id_obj.style.line_dash)
                id_obj.style.fill_color = _st.get("fill_color", id_obj.style.fill_color)
            _c = kind_data.get("contents", {})
            if _c:
                id_obj.contents.halign = _c.get("halign", id_obj.contents.halign)
                id_obj.contents.valign = _c.get("valign", id_obj.contents.valign)
                id_obj.contents.spacing = _c.get("spacing", id_obj.contents.spacing)
                id_obj.contents.color = _c.get("color", id_obj.contents.color)
                id_obj.contents.font_family = _c.get("font_family", id_obj.contents.font_family)
                id_obj.contents.font_size = int(_c.get("font_size", id_obj.contents.font_size))
                id_obj.contents.margin_left = _c.get("margin_left", id_obj.contents.margin_left)
                id_obj.contents.margin_right = _c.get("margin_right", id_obj.contents.margin_right)
                id_obj.contents.margin_top = _c.get("margin_top", id_obj.contents.margin_top)
                id_obj.contents.margin_bottom = _c.get("margin_bottom", id_obj.contents.margin_bottom)
                id_obj.contents.wrap = _c.get("wrap", id_obj.contents.wrap)
                id_obj.contents.flow_type = _c.get("flow_type", id_obj.contents.flow_type)
                id_obj.contents.text_box_width = _c.get("text_box_width", id_obj.contents.text_box_width)
                id_obj.contents.text_box_height = _c.get("text_box_height", id_obj.contents.text_box_height)
                id_obj.contents.image_anchor = int(_c.get("image_anchor", id_obj.contents.image_anchor))
                if "frame" in _c and isinstance(_c["frame"], dict):
                    id_obj.contents.frame = _c["frame"]
                if "default_format" in _c and isinstance(_c["default_format"], dict):
                    id_obj.contents.default_format = _c["default_format"]

        # Gemini section
        gemini = data.get("gemini", {})
        if "models" in gemini:
            settings.gemini.models = gemini["models"]
        settings.gemini.default_model = gemini.get("default_model", settings.gemini.default_model)
        if settings.gemini.default_model not in settings.gemini.models:
            if settings.gemini.models:
                settings.gemini.default_model = settings.gemini.models[0]

        # External tools section
        ext = data.get("external_tools", {})
        settings.external_tools.java_path = ext.get("java_path", settings.external_tools.java_path)
        settings.external_tools.plantuml_jar_path = ext.get("plantuml_jar_path", settings.external_tools.plantuml_jar_path)
        settings.external_tools.nodejs_path = ext.get("nodejs_path", settings.external_tools.nodejs_path)
        settings.external_tools.mmdc_path = ext.get("mmdc_path", settings.external_tools.mmdc_path)
        settings.external_tools.mmdc_png_scale = int(ext.get("mmdc_png_scale", settings.external_tools.mmdc_png_scale))
        settings.external_tools.c4_shapes_per_row = int(ext.get("c4_shapes_per_row", settings.external_tools.c4_shapes_per_row))
        settings.external_tools.c4_boundaries_per_row = int(ext.get("c4_boundaries_per_row", settings.external_tools.c4_boundaries_per_row))

    def _to_toml_dict(self, settings: "Optional[AppSettings]" = None) -> Dict[str, Any]:
        """Serialize *settings* (or current merged settings) to a TOML-compatible dictionary."""
        s = settings if settings is not None else self.settings
        d: Dict[str, Any] = {
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
                "folding": {"width": s.editor.folding.width},
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
                "selection": {"outline_color": s.canvas.selection.outline_color},
                "zorder": {"base": s.canvas.zorder.base, "step": s.canvas.zorder.step},
                "zoom": {"wheel_factor": s.canvas.zoom.wheel_factor},
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
                "scoring": {"size_difference_weight": s.alignment.scoring.size_difference_weight},
                "line": {"hue_tolerances": s.alignment.line.hue_tolerances},
            },
            "defaults": {
                "contents": {
                    "halign": s.defaults.halign,
                    "valign": s.defaults.valign,
                    "spacing": s.defaults.spacing,
                    "color": s.defaults.color,
                    "font_family": s.defaults.font_family,
                    "font_size": s.defaults.font_size,
                    "margin_left": s.defaults.margin_left,
                    "margin_right": s.defaults.margin_right,
                    "margin_top": s.defaults.margin_top,
                    "margin_bottom": s.defaults.margin_bottom,
                    "wrap": s.defaults.wrap,
                    "flow_type": s.defaults.flow_type,
                    "text_box_width": s.defaults.text_box_width,
                    "text_box_height": s.defaults.text_box_height,
                    "image_url": s.defaults.image_url,
                    "image_anchor": s.defaults.image_anchor,
                },
                "style": {
                    "pen_color": s.style.pen_color,
                    "pen_width": s.style.pen_width,
                    "line_dash": s.style.line_dash,
                    "fill_color": s.style.fill_color,
                },
            },
            "item_defaults": {
                kind: _build_item_defaults_toml(id_obj)
                for kind, id_obj in s.item_defaults.items()
            },
            "gemini": {
                "models": s.gemini.models,
                "default_model": s.gemini.default_model,
            },
            "external_tools": {
                "java_path": s.external_tools.java_path,
                "plantuml_jar_path": s.external_tools.plantuml_jar_path,
                "nodejs_path": s.external_tools.nodejs_path,
                "mmdc_path": s.external_tools.mmdc_path,
                "mmdc_png_scale": s.external_tools.mmdc_png_scale,
                "c4_shapes_per_row": s.external_tools.c4_shapes_per_row,
                "c4_boundaries_per_row": s.external_tools.c4_boundaries_per_row,
            },
        }
        return d

    def to_toml(self) -> str:
        """Convert current settings to a TOML-formatted string."""
        return tomli_w.dumps(self._to_toml_dict())

    def get_workspace_dir(self) -> Path:
        """Return resolved workspace directory, falling back to ~/Documents/PictoSync."""
        if self.settings.workspace_dir:
            return Path(self.settings.workspace_dir)
        return Path.home() / "Documents" / "PictoSync"

    def get_settings_path(self) -> Path:
        """Return path to the user settings file (backward-compat)."""
        return self.user_settings_file
