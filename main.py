"""
main.py

Diagram Overlay Annotator - Main Application

PyQt6 application for creating diagram overlays with:
- Manual drawing tools (rect, rounded rect, ellipse, line, text)
- Gemini AI auto-extraction
- Bidirectional JSON <-> Scene synchronization
- Context-sensitive property editing

Usage:
    python main.py

Dependencies:
    pip install PyQt6 pillow google-genai

Environment:
    GOOGLE_API_KEY=... (required for AI extraction)
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional


def compile_ui_if_needed():
    """Compile Qt Designer .ui files to Python if they've been modified."""
    base_dir = Path(__file__).parent
    ui_files = [
        (base_dir / "properties" / "properties_panel.ui",
         base_dir / "properties" / "properties_ui.py"),
    ]

    for ui_file, py_file in ui_files:
        if not ui_file.exists():
            continue

        # Compile if .py doesn't exist or .ui is newer
        needs_compile = (
            not py_file.exists() or
            ui_file.stat().st_mtime > py_file.stat().st_mtime
        )

        if needs_compile:
            print(f"Compiling {ui_file.name}...")
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "PyQt6.uic.pyuic", "-o", str(py_file), str(ui_file)],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"  -> {py_file.name} updated")
            except subprocess.CalledProcessError as e:
                print(f"  Warning: Failed to compile {ui_file.name}: {e.stderr}")
            except FileNotFoundError:
                print(f"  Warning: pyuic6 not found, skipping UI compilation")


# Auto-compile UI files before importing modules that depend on them
compile_ui_if_needed()

from PIL import Image

from PyQt6.QtCore import Qt, QRectF, QFileInfo, QSize, QTimer, QThread
from PyQt6.QtGui import QAction, QBrush, QColor, QFont, QIcon, QKeySequence, QPen, QPixmap, QUndoStack
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from models import Mode, AnnotationMeta, ANN_ID_KEY, normalize_meta
from utils import parse_c4_text, _looks_normalized, _scale_record, sort_draft_data, sort_annotation_keys
from canvas import (
    AnnotatorScene,
    AnnotatorView,
    MetaRectItem,
    MetaRoundedRectItem,
    MetaEllipseItem,
    MetaLineItem,
    MetaTextItem,
    MetaHexagonItem,
    MetaCylinderItem,
    MetaBlockArrowItem,
    MetaPolygonItem,
    MetaGroupItem,
)
from editor import DraftDock
from properties import PropertyPanel
from gemini import ExtractWorker
from styles import STYLES, DEFAULT_STYLE, CANVAS_TEXT_COLORS, LINE_NUMBER_COLORS
from pptx_export import export_to_pptx
from settings import SettingsManager, get_settings
from debug_trace import trace, trace_exception, close_log

# Optional alignment import (requires opencv-python)
try:
    from alignment import AlignmentWorker, LineAlignmentWorker
    HAS_ALIGNMENT = True
except ImportError:
    AlignmentWorker = None
    LineAlignmentWorker = None
    HAS_ALIGNMENT = False


# Import comprehensive settings dialog
from settings_dialog import SettingsDialog
from help_dialog import HelpDialog, show_about_dialog
from undo_commands import (
    DeleteItemCommand, DeleteMultipleItemsCommand, AddItemCommand,
    GroupItemsCommand, UngroupItemsCommand,
    MoveItemCommand, ItemGeometryCommand, TextEditCommand,
)
from canvas.mixins import LinkedMixin


# Mapping from style display names to icon directory names
STYLE_TO_ICON_DIR = {
    "Foundation (Dark)": "Foundation",
    "Bulma (Light)": "Bulma",
    "Bauhaus": "Bauhaus",
    "Neumorphism": "Neumorphism",
    "Materialize": "Materialize",
    "Tailwind": "Tailwind",
    "Bootstrap": "Bootstrap",
}


def get_icon_path(icon_name: str, style: str, selected: bool = False) -> str:
    """Get the path to an icon for the given style."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_dir = STYLE_TO_ICON_DIR.get(style, style)  # Fallback to style name if not in mapping
    suffix = "_selected" if selected else ""
    return os.path.join(base_dir, "icons", icon_dir, f"{icon_name}{suffix}.svg")


def create_icon_with_states(icon_name: str, style: str) -> QIcon:
    """Create a QIcon with normal and selected state variants."""
    icon = QIcon()

    normal_path = get_icon_path(icon_name, style, selected=False)
    selected_path = get_icon_path(icon_name, style, selected=True)

    if os.path.exists(normal_path):
        # Normal state (Off) - for unselected buttons
        icon.addFile(normal_path, mode=QIcon.Mode.Normal, state=QIcon.State.Off)
        icon.addFile(normal_path, mode=QIcon.Mode.Active, state=QIcon.State.Off)

    if os.path.exists(selected_path):
        # Selected state (On) - for checked/selected buttons
        icon.addFile(selected_path, mode=QIcon.Mode.Normal, state=QIcon.State.On)
        icon.addFile(selected_path, mode=QIcon.Mode.Active, state=QIcon.State.On)

    return icon


class MainWindow(QMainWindow):
    """Main application window for the Diagram Overlay Annotator.

    Args:
        settings_manager: The SettingsManager instance for application settings.
    """

    def __init__(self, settings_manager: SettingsManager):
        super().__init__()
        self.settings_manager = settings_manager
        self.setWindowTitle("PictoSync - Diagram Annotation with AI Extraction")

        # Scene and view
        self.scene = AnnotatorScene()
        self.scene.setSceneRect(0, 0, 1200, 800)

        self.bg_item: Optional[QGraphicsPixmapItem] = None
        self.bg_path: Optional[str] = None

        # Hidden PNG indicator
        self._png_hidden_indicator: Optional[QGraphicsSimpleTextItem] = None

        self.view = AnnotatorView(self.scene, self._on_drop_file)

        # Property panel (in splitter below canvas)
        self.props = PropertyPanel(self)

        # Vertical splitter: canvas on top, property panel on bottom
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_splitter.addWidget(self.view)
        self.main_splitter.addWidget(self.props)
        self.main_splitter.setStretchFactor(0, 4)  # Canvas gets more space
        self.main_splitter.setStretchFactor(1, 1)  # Property panel gets less

        self.setCentralWidget(self.main_splitter)

        # Dock widget for JSON editor (right side, full height)
        self.setCorner(Qt.Corner.TopRightCorner, Qt.DockWidgetArea.RightDockWidgetArea)
        self.setCorner(Qt.Corner.BottomRightCorner, Qt.DockWidgetArea.RightDockWidgetArea)

        self.draft = DraftDock(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.draft)

        # Pre-initialize optional actions (may be set in _build_toolbar if HAS_ALIGNMENT)
        self.align_act: Optional[QAction] = None
        self.align_line_act: Optional[QAction] = None

        # Undo/Redo stack
        self.undo_stack = QUndoStack(self)
        self.undo_stack.setUndoLimit(100)  # Limit undo history

        # Build UI (menus first since toolbar references menu actions)
        self._build_menus()
        self._build_toolbar()

        # Connect signals
        self.scene.selectionChanged.connect(self.on_selection_changed)
        self.draft.import_btn.clicked.connect(self.import_draft_and_link)
        self.draft.cursor_annotation_changed.connect(self._on_editor_cursor_annotation_changed)

        # State for JSON <-> Scene linkage
        self._link_enabled = False
        self._draft_data: Optional[dict] = None
        self._id_to_index: Dict[str, int] = {}
        self._id_counter = 1

        self._syncing_from_scene = False
        self._syncing_from_json = False
        self._handling_selection = False  # Guard against re-entry during selection handling

        # Debounced JSON editing timer
        self._json_edit_timer = QTimer(self)
        self._json_edit_timer.setSingleShot(True)
        self._json_edit_timer.setInterval(250)
        self._json_edit_timer.timeout.connect(self._apply_json_text_to_scene)

        self.draft.text.textChanged.connect(self._on_draft_text_changed)

        # Configure scene linkage callbacks
        self.scene.configure_linkage(self._new_ann_id, self._on_new_scene_item, self._on_scene_item_changed)

        # Set up callbacks to exit sticky mode
        self.scene.set_right_click_callback(self._exit_sticky_mode)
        self.scene.set_escape_key_callback(self._exit_sticky_mode)

        # Set up callback for z-order changes
        self.scene.set_z_order_changed_callback(self._on_z_order_changed)

        # Set up group/ungroup callbacks
        self.scene.set_group_callbacks(self._do_group_items, self._do_ungroup_item)

        # Set up text editing callbacks to disable shortcuts during editing
        self._setup_text_editing_callbacks()

        # Set up undo callbacks for move, resize, and text edit
        self.scene.set_on_items_moved(self._on_items_moved)
        self.scene.set_on_select_mouse_up(self._on_select_mouse_up)
        LinkedMixin.on_resize_finished = self._on_item_resize_finished
        MetaTextItem.on_text_edit_finished = self._on_text_edit_finished

        # Give property panel and scene access to undo stack/actions
        self.props.undo_stack = self.undo_stack
        self.scene.set_undo_actions(self.undo_act, self.redo_act)

        self.statusBar().showMessage("Drop a PNG. Auto-Extract or edit Draft JSON. Import links JSON<->Scene.")
        self.props.set_image_info({})

        # Gemini worker thread
        self._thread: Optional[QThread] = None
        self._worker: Optional[ExtractWorker] = None

        # Alignment worker thread
        self._align_thread: Optional[QThread] = None
        self._align_worker: Optional[AlignmentWorker] = None

        # Line alignment worker thread
        self._line_align_thread: Optional[QThread] = None
        self._line_align_worker: Optional[LineAlignmentWorker] = None

    def _build_menus(self):
        """Build the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        open_graphic = QAction("Open Graphic...", self)
        open_graphic.triggered.connect(self.open_graphic_dialog)
        file_menu.addAction(open_graphic)

        file_menu.addSeparator()

        save_project = QAction("Save Project...", self)
        save_project.setShortcut(QKeySequence.StandardKey.Save)
        save_project.triggered.connect(self.save_project_dialog)
        file_menu.addAction(save_project)

        open_project = QAction("Open Project...", self)
        open_project.setShortcut(QKeySequence.StandardKey.Open)
        open_project.triggered.connect(self.open_project_dialog)
        file_menu.addAction(open_project)

        file_menu.addSeparator()

        export_pptx = QAction("Export PowerPoint...", self)
        export_pptx.triggered.connect(self.export_pptx_dialog)
        file_menu.addAction(export_pptx)

        file_menu.addSeparator()

        exit_act = QAction("E&xit", self)
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        # Undo/Redo (will be connected to undo_stack in _build_toolbar)
        self._menu_undo_act = QAction("Undo", self)
        self._menu_undo_act.setShortcut(QKeySequence.StandardKey.Undo)
        self._menu_undo_act.setEnabled(False)
        edit_menu.addAction(self._menu_undo_act)

        self._menu_redo_act = QAction("Redo", self)
        self._menu_redo_act.setShortcut(QKeySequence.StandardKey.Redo)
        self._menu_redo_act.setEnabled(False)
        edit_menu.addAction(self._menu_redo_act)

        edit_menu.addSeparator()

        delete_act = QAction("Delete Selected", self)
        delete_act.setShortcut(QKeySequence(Qt.Key.Key_Delete))
        delete_act.triggered.connect(self.delete_selected_items)
        edit_menu.addAction(delete_act)

        edit_menu.addSeparator()

        settings_act = QAction("Settings...", self)
        settings_act.triggered.connect(self.show_settings_dialog)
        edit_menu.addAction(settings_act)

        # View menu
        view_menu = menubar.addMenu("&View")

        zoom_in_act = QAction("Zoom In", self)
        zoom_in_act.setShortcut(QKeySequence.StandardKey.ZoomIn)
        zoom_in_act.triggered.connect(lambda: self.view.zoom_in())
        view_menu.addAction(zoom_in_act)

        zoom_out_act = QAction("Zoom Out", self)
        zoom_out_act.setShortcut(QKeySequence.StandardKey.ZoomOut)
        zoom_out_act.triggered.connect(lambda: self.view.zoom_out())
        view_menu.addAction(zoom_out_act)

        view_menu.addSeparator()

        zoom_fit_act = QAction("Zoom to Fit", self)
        zoom_fit_act.setShortcut("F")
        zoom_fit_act.triggered.connect(self._on_zoom_fit)
        view_menu.addAction(zoom_fit_act)

        zoom_reset_act = QAction("Zoom 100%", self)
        zoom_reset_act.setShortcut("1")
        zoom_reset_act.triggered.connect(lambda: self.view.zoom_reset())
        view_menu.addAction(zoom_reset_act)

        view_menu.addSeparator()

        self._menu_zoom_region_act = QAction("Zoom to Region", self)
        self._menu_zoom_region_act.setShortcut("Z")
        self._menu_zoom_region_act.setCheckable(True)
        view_menu.addAction(self._menu_zoom_region_act)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        help_contents_act = QAction("Help Contents", self)
        help_contents_act.setShortcut(QKeySequence(Qt.Key.Key_F1))
        help_contents_act.triggered.connect(self._show_help_dialog)
        help_menu.addAction(help_contents_act)

        shortcuts_act = QAction("Keyboard Shortcuts", self)
        shortcuts_act.triggered.connect(lambda: self._show_help_dialog(tab=2))
        help_menu.addAction(shortcuts_act)

        help_menu.addSeparator()

        about_act = QAction("About PictoSync", self)
        about_act.triggered.connect(lambda: show_about_dialog(self))
        help_menu.addAction(about_act)

    def _build_toolbar(self):
        """Build the application toolbar."""
        tb = QToolBar("Tools")
        tb.setIconSize(QSize(18, 18))  # Smaller icons for compact toolbar
        self.addToolBar(tb)

        # Track sticky mode (Ctrl+click on tool makes it stick)
        self._sticky_mode = False

        # Store actions with their icon names for theme switching
        self._icon_actions: Dict[QAction, str] = {}

        def add_mode_action(text: str, mode: str, shortcut: str, icon_name: str,
                            tooltip: str = ""):
            act = QAction(text, self)
            act.setCheckable(True)
            act.setShortcut(shortcut)
            if tooltip:
                act.setToolTip(f"{tooltip} ({shortcut})")
                act.setStatusTip(tooltip)
            # Check for Ctrl modifier when triggered
            act.triggered.connect(lambda checked, m=mode: self._on_mode_action_triggered(m))
            self._icon_actions[act] = icon_name
            tb.addAction(act)
            return act

        # Mode actions
        self.act_select = add_mode_action("Select", Mode.SELECT, "S", "select",
                                          "Select, move, and resize annotations")
        self.act_rect = add_mode_action("Rect", Mode.RECT, "R", "rect",
                                        "Draw a rectangle")
        self.act_rrect = add_mode_action("RRect", Mode.ROUNDEDRECT, "U", "rrect",
                                         "Draw a rounded rectangle")
        self.act_ellipse = add_mode_action("Ellipse", Mode.ELLIPSE, "E", "ellipse",
                                           "Draw an ellipse")
        self.act_line = add_mode_action("Line", Mode.LINE, "L", "line",
                                        "Draw a line or connector")
        self.act_text = add_mode_action("Text", Mode.TEXT, "T", "text",
                                        "Place a text annotation")
        self.act_hexagon = add_mode_action("Hexagon", Mode.HEXAGON, "H", "hexagon",
                                           "Draw a hexagon")
        self.act_cylinder = add_mode_action("Cylinder", Mode.CYLINDER, "Y", "cylinder",
                                            "Draw a cylinder (database)")
        self.act_blockarrow = add_mode_action("Block Arrow", Mode.BLOCKARROW, "A", "blockarrow",
                                              "Draw a block arrow")
        self.act_polygon = add_mode_action("Polygon", Mode.POLYGON, "P", "polygon",
                                           "Draw a polygon (click vertices, right-click to close)")
        self.mode_actions = [self.act_select, self.act_rect, self.act_rrect, self.act_ellipse, self.act_line, self.act_text, self.act_hexagon, self.act_cylinder, self.act_blockarrow, self.act_polygon]
        self.act_select.setChecked(True)

        tb.addSeparator()

        # File actions
        open_act = QAction("Open Graphic...", self)
        open_act.triggered.connect(self.open_graphic_dialog)
        open_act.setToolTip("Open a PNG or PUML file")
        open_act.setStatusTip("Open a PNG or PUML file")
        self._icon_actions[open_act] = "open"
        tb.addAction(open_act)

        clear_act = QAction("Clear Overlay", self)
        clear_act.triggered.connect(self.clear_overlay)
        clear_act.setToolTip("Remove all annotations from the canvas")
        clear_act.setStatusTip("Remove all annotations from the canvas")
        self._icon_actions[clear_act] = "clear"
        tb.addAction(clear_act)

        # Toggle PNG visibility
        self.toggle_png_act = QAction("Hide PNG", self)
        self.toggle_png_act.setCheckable(True)
        self.toggle_png_act.setEnabled(False)  # Disabled until PNG is loaded
        self.toggle_png_act.triggered.connect(self._toggle_png_visibility)
        self.toggle_png_act.setToolTip("Toggle background image visibility")
        self.toggle_png_act.setStatusTip("Toggle background image visibility")
        self._icon_actions[self.toggle_png_act] = "hide_png"
        tb.addAction(self.toggle_png_act)

        # Align element to PNG (requires opencv-python)
        if HAS_ALIGNMENT:
            self.align_act = QAction("Align to PNG", self)
            self.align_act.setEnabled(False)  # Disabled until conditions met
            self.align_act.triggered.connect(self.align_selected_to_png)
            self.align_act.setToolTip("Snap selected shape to match background")
            self.align_act.setStatusTip("Snap selected shape to match background")
            self._icon_actions[self.align_act] = "align"
            tb.addAction(self.align_act)

            # Align line to PNG
            self.align_line_act = QAction("Align Line to PNG", self)
            self.align_line_act.setEnabled(False)  # Disabled until conditions met
            self.align_line_act.triggered.connect(self.align_selected_line_to_png)
            self.align_line_act.setToolTip("Snap selected line to match background")
            self.align_line_act.setStatusTip("Snap selected line to match background")
            self._icon_actions[self.align_line_act] = "align_line"
            tb.addAction(self.align_line_act)

        tb.addSeparator()

        # AI model selection
        self.model_label = QLabel("Model: gemini-2.5-flash-image")
        tb.addWidget(self.model_label)

        self.model_name = "gemini-2.5-flash-image"
        cycle_act = QAction("Cycle Model", self)
        cycle_act.triggered.connect(self.cycle_model)
        cycle_act.setToolTip("Cycle through Gemini AI models")
        cycle_act.setStatusTip("Cycle through Gemini AI models")
        self._icon_actions[cycle_act] = "model"
        tb.addAction(cycle_act)

        self.extract_act = QAction("Auto-Extract (Gemini)", self)
        self.extract_act.triggered.connect(self.auto_extract)
        self.extract_act.setToolTip("Auto-extract elements using Gemini AI")
        self.extract_act.setStatusTip("Auto-extract elements using Gemini AI")
        self._icon_actions[self.extract_act] = "extract"
        tb.addAction(self.extract_act)

        tb.addSeparator()

        # Undo/Redo actions (shortcuts are on menu actions, not here, to avoid ambiguity)
        self.undo_act = self.undo_stack.createUndoAction(self, "Undo")
        self.undo_act.setToolTip("Undo the last action (Ctrl+Z)")
        self.undo_act.setStatusTip("Undo the last action")
        self._icon_actions[self.undo_act] = "undo"
        tb.addAction(self.undo_act)

        self.redo_act = self.undo_stack.createRedoAction(self, "Redo")
        self.redo_act.setToolTip("Redo the last undone action (Ctrl+Y)")
        self.redo_act.setStatusTip("Redo the last undone action")
        self._icon_actions[self.redo_act] = "redo"
        tb.addAction(self.redo_act)

        tb.addSeparator()

        # Zoom actions
        self.zoom_region_act = QAction("Zoom Region", self)
        self.zoom_region_act.setCheckable(True)
        # Shortcut is on menu action, synced via toggled signal
        self.zoom_region_act.triggered.connect(self._on_zoom_region_triggered)
        self.zoom_region_act.setToolTip("Drag to zoom into a region (Z)")
        self.zoom_region_act.setStatusTip("Drag to zoom into a region")
        self._icon_actions[self.zoom_region_act] = "zoom_region"
        tb.addAction(self.zoom_region_act)

        self.zoom_fit_act = QAction("Zoom Fit", self)
        self.zoom_fit_act.setShortcut("F")
        self.zoom_fit_act.triggered.connect(self._on_zoom_fit)
        self.zoom_fit_act.setToolTip("Fit entire scene in view (F)")
        self.zoom_fit_act.setStatusTip("Fit entire scene in view")
        self._icon_actions[self.zoom_fit_act] = "zoom_fit"
        tb.addAction(self.zoom_fit_act)

        # Connect menu actions to toolbar actions
        # Undo/Redo menu items trigger toolbar actions
        self._menu_undo_act.triggered.connect(self.undo_act.trigger)
        self._menu_redo_act.triggered.connect(self.redo_act.trigger)
        # Keep menu undo/redo enabled state in sync with toolbar
        self.undo_stack.canUndoChanged.connect(self._menu_undo_act.setEnabled)
        self.undo_stack.canRedoChanged.connect(self._menu_redo_act.setEnabled)
        self._menu_undo_act.setEnabled(self.undo_stack.canUndo())
        self._menu_redo_act.setEnabled(self.undo_stack.canRedo())

        # Sync zoom region menu and toolbar checkable state
        self._menu_zoom_region_act.triggered.connect(self._on_zoom_region_triggered)
        self.zoom_region_act.toggled.connect(self._menu_zoom_region_act.setChecked)
        self._menu_zoom_region_act.toggled.connect(self.zoom_region_act.setChecked)

        # Apply initial icons and editor colors
        self._update_toolbar_icons(DEFAULT_STYLE)
        self._update_editor_colors(DEFAULT_STYLE)
        self._update_draft_dock_icons(DEFAULT_STYLE)

        # Connect focus mode button toggle to update icon
        self.draft.focus_mode_btn.toggled.connect(
            lambda checked: self._update_focus_mode_icon(checked)
        )

    def cycle_model(self):
        """Cycle through available Gemini models."""
        options = ["gemini-2.5-flash-image", "gemini-3-pro-image-preview"]
        idx = options.index(self.model_name) if self.model_name in options else 0
        self.model_name = options[(idx + 1) % len(options)]
        self.model_label.setText(f"Model: {self.model_name}")

    def _update_toolbar_icons(self, style: str):
        """Update toolbar icons for the given style."""
        for action, icon_name in self._icon_actions.items():
            icon = create_icon_with_states(icon_name, style)
            action.setIcon(icon)

    def _update_editor_colors(self, style: str):
        """Update the JSON editor's line number colors for the given style."""
        colors = LINE_NUMBER_COLORS.get(style, LINE_NUMBER_COLORS.get("Tailwind", {}))
        if colors:
            self.draft.text.set_line_number_colors(colors)

    def _update_draft_dock_icons(self, style: str):
        """Update the Draft Dock button icons for the given style."""
        # Import link button
        import_icon = create_icon_with_states("import_link", style)
        self.draft.import_btn.setIcon(import_icon)

        # Focus mode button - set initial icon based on current state
        self._update_focus_mode_icon(self.draft.focus_mode_btn.isChecked(), style)

    def _update_focus_mode_icon(self, checked: bool, style: str = None):
        """Update the focus mode button icon based on its state."""
        if style is None:
            app = QApplication.instance()
            style = getattr(app, "_current_style", DEFAULT_STYLE)

        icon_name = "focus_on" if checked else "focus_off"
        icon = create_icon_with_states(icon_name, style)
        self.draft.focus_mode_btn.setIcon(icon)

    def _setup_text_editing_callbacks(self):
        """Set up callbacks to disable shortcuts during text editing."""
        def on_editing_started():
            # Disable mode shortcuts when editing text
            for action in self.mode_actions:
                action.setShortcut("")

        def on_editing_finished():
            # Re-enable mode shortcuts when done editing
            shortcuts = ["S", "R", "U", "E", "L", "T", "H", "Y", "A"]
            for action, shortcut in zip(self.mode_actions, shortcuts):
                action.setShortcut(shortcut)

        def on_text_changed(text: str):
            # Sync text changes to the Note field in properties panel
            self.props.note_edit.blockSignals(True)
            self.props.note_edit.setText(text)
            self.props.note_edit.blockSignals(False)

        MetaTextItem.on_editing_started = on_editing_started
        MetaTextItem.on_editing_finished = on_editing_finished
        MetaTextItem.on_text_changed = on_text_changed

        # Set up callbacks for shape property changes (adjust1/adjust2)
        MetaRoundedRectItem.on_adjust1_changed = self.props.update_adjust1_display
        MetaHexagonItem.on_adjust1_changed = self.props.update_adjust1_display
        MetaCylinderItem.on_adjust1_changed = self.props.update_adjust1_display
        MetaBlockArrowItem.on_adjust1_changed = self.props.update_adjust1_display
        MetaBlockArrowItem.on_adjust2_changed = self.props.update_adjust2_display

        # Set initial default text color based on current theme
        self._update_default_text_color(DEFAULT_STYLE)

    def _update_default_text_color(self, style: str):
        """Update the default text color for new text items based on theme."""
        from PyQt6.QtGui import QColor
        color_hex = CANVAS_TEXT_COLORS.get(style, "#1E293B")
        MetaTextItem.default_text_color = QColor(color_hex)

    def _on_mode_action_triggered(self, mode: str):
        """Handle mode action click - check for Ctrl modifier for sticky mode."""
        from PyQt6.QtWidgets import QApplication
        modifiers = QApplication.keyboardModifiers()

        if mode == Mode.SELECT:
            # Select tool always clears sticky mode
            self._sticky_mode = False
        else:
            # Check if Ctrl is held - makes tool sticky
            self._sticky_mode = bool(modifiers & Qt.KeyboardModifier.ControlModifier)

        self.set_mode(mode)

        if self._sticky_mode:
            self.statusBar().showMessage(f"Mode: {mode} (sticky - Ctrl+click, Esc or right-click to exit)")

    def set_mode(self, mode: str, from_item_created: bool = False):
        """Set the current drawing mode."""
        self.scene.set_mode(mode)
        mapping = {
            Mode.SELECT: self.act_select,
            Mode.RECT: self.act_rect,
            Mode.ROUNDEDRECT: self.act_rrect,
            Mode.ELLIPSE: self.act_ellipse,
            Mode.LINE: self.act_line,
            Mode.TEXT: self.act_text,
            Mode.HEXAGON: self.act_hexagon,
            Mode.CYLINDER: self.act_cylinder,
            Mode.BLOCKARROW: self.act_blockarrow,
            Mode.POLYGON: self.act_polygon,
        }
        for a in self.mode_actions:
            a.setChecked(False)
        mapping[mode].setChecked(True)

        self.view.setDragMode(
            QGraphicsView.DragMode.RubberBandDrag if mode == Mode.SELECT else QGraphicsView.DragMode.NoDrag
        )

        if not from_item_created:
            self.statusBar().showMessage(f"Mode: {mode}")

    def _on_item_created(self):
        """Called after an item is created - revert to Select if not sticky."""
        if not self._sticky_mode:
            self.set_mode(Mode.SELECT, from_item_created=True)
            self.statusBar().showMessage("Mode: select (item created)")
        else:
            self.statusBar().showMessage(f"Mode: {self.scene.mode} (sticky)")

    def _exit_sticky_mode(self):
        """Exit sticky mode and return to Select tool."""
        self._sticky_mode = False
        self.set_mode(Mode.SELECT)
        self.statusBar().showMessage("Mode: select")

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Escape:
            # Escape exits sticky mode and returns to Select
            if self._sticky_mode or self.scene.mode != Mode.SELECT:
                self._exit_sticky_mode()
                event.accept()
                return
        super().keyPressEvent(event)

    def on_selection_changed(self):
        """Handle scene selection changes."""
        # Guard against re-entry (can happen during focus mode fold operations)
        if self._handling_selection:
            return
        self._handling_selection = True
        try:
            self._do_selection_changed()
        finally:
            self._handling_selection = False

    def _do_selection_changed(self):
        """Internal handler for selection changes."""
        items = self.scene.selectedItems()
        it = items[0] if items else None
        self.props.set_item(it)

        # Update align button state based on selection
        self._update_align_button_state()

        # Skip all editor operations when syncing from JSON edits
        # (user is actively editing the editor, don't disturb their view)
        if self._syncing_from_json:
            return

        if it is None:
            self.draft.clear_highlighted_annotation()
            self.draft.set_focused_annotation("")  # Clear focus in focus mode
            return

        ann_id = it.data(ANN_ID_KEY)
        if not (isinstance(ann_id, str) and ann_id):
            self.draft.clear_highlighted_annotation()
            self.draft.set_focused_annotation("")  # Clear focus in focus mode
            return

        # Set highlight bar in JSON editor for selected annotation
        self.draft.set_highlighted_annotation(ann_id)

        # Update focus mode to show this annotation
        self.draft.set_focused_annotation(ann_id)

        # When mouse is down, scroll to the annotation once then lock so
        # subsequent drag frames don't jump.  The lock is applied after the
        # deferred _scroll_cursor_to_top completes (see DraftDock).
        if self.scene._mouse_down_in_select:
            self.draft._lock_after_scroll = True

        # When focus mode is enabled, fold operations change the document layout.
        # Defer the scroll to allow Qt to process the layout updates first.
        if self.draft.is_focus_mode_enabled():
            QTimer.singleShot(0, lambda: self._deferred_scroll_to_id(ann_id))
        else:
            self._scroll_draft_to_id_top(ann_id)

        if isinstance(it, MetaTextItem):
            if self.draft.is_focus_mode_enabled():
                QTimer.singleShot(0, lambda: self._deferred_scroll_to_text(ann_id))
            else:
                self._scroll_to_text_field(ann_id)

    def _deferred_scroll_to_id(self, ann_id: str):
        """Deferred scroll for focus mode - checks guards to prevent loops."""
        if self._handling_selection or self._syncing_from_json:
            return
        self._scroll_draft_to_id_top(ann_id)

    def _deferred_scroll_to_text(self, ann_id: str):
        """Deferred scroll to text field for focus mode - checks guards to prevent loops."""
        if self._handling_selection or self._syncing_from_json:
            return
        self._scroll_to_text_field(ann_id)

    def _scroll_draft_to_id_top(self, ann_id: str):
        """Scroll the draft editor to show the given annotation ID."""
        ok = self.draft.scroll_to_id_top(ann_id)
        if ok:
            self.draft.set_status(f"Focused id: {ann_id}")

    def _scroll_to_text_field(self, ann_id: str):
        """Scroll the draft editor to show the text field for the given annotation ID."""
        ok = self.draft.jump_to_text_field_for_id(ann_id)
        if ok:
            self.draft.set_status(f"Focused text for id: {ann_id}")

    def _on_editor_cursor_annotation_changed(self, ann_id: str):
        """Handle cursor position changes in the JSON editor."""
        # Ignore cursor changes during selection handling (prevents loops from fold operations)
        if self._handling_selection:
            return

        if not ann_id:
            # Cursor is outside any annotation
            self.draft.clear_highlighted_annotation()
            if self._link_enabled:
                self.scene.clearSelection()
                self.props.set_item(None)
            return

        # Always show highlight bar when cursor is within annotation brackets
        self.draft.set_highlighted_annotation(ann_id)

        # Only select canvas items when linking is enabled
        if not self._link_enabled:
            return

        # Find and select the canvas item with this annotation ID
        for item in self.scene.items():
            item_ann_id = item.data(ANN_ID_KEY)
            if item_ann_id == ann_id:
                self.scene.blockSignals(True)
                try:
                    self.scene.clearSelection()
                    item.setSelected(True)
                finally:
                    self.scene.blockSignals(False)

                self.props.set_item(item)
                self.draft.set_status(f"Selected from editor: {ann_id}")
                return

        # No canvas item found, but still show the highlight
        self.scene.clearSelection()
        self.props.set_item(None)
        self.draft.set_status(f"Annotation in JSON: {ann_id} (no canvas item)")

    def open_graphic_dialog(self):
        """Open a file dialog to select a PNG image or PlantUML file."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Graphic", "",
            "All Supported (*.png *.puml);;PNG Images (*.png);;PlantUML (*.puml)"
        )
        if not path:
            return
        if path.lower().endswith(".puml"):
            self._import_puml(path)
        else:
            self.load_background_png(path)

    def _on_drop_file(self, path: str):
        """Handle a file dropped onto the canvas (PNG or PUML)."""
        if path.lower().endswith(".puml"):
            self._import_puml(path)
        else:
            self.load_background_png(path)

    def _import_puml(self, puml_path: str):
        """Import a PlantUML file: render to PNG background and parse to annotations.

        Args:
            puml_path: Path to the .puml file.
        """
        from plantuml.renderer import render_puml_to_png, render_puml_to_svg
        from plantuml.parser import parse_puml_to_annotations

        # Read PUML source text
        try:
            with open(puml_path, "r", encoding="utf-8") as f:
                puml_text = f.read()
        except Exception as e:
            QMessageBox.warning(self, "Read Error", f"Could not read PUML file:\n{e}")
            return

        # Check @startuml diagram name for illegal Windows filename chars.
        # PlantUML uses this name as the output filename, so characters like
        # : * ? " < > | will silently produce a 0-byte output on Windows.
        _ILLEGAL_FNAME_CHARS = set('\\/:*?"<>|')
        for line_num, line in enumerate(puml_text.splitlines(), start=1):
            stripped = line.strip()
            if stripped.lower().startswith("@startuml"):
                diagram_name = stripped[len("@startuml"):].strip()
                bad_chars = sorted(set(ch for ch in diagram_name if ch in _ILLEGAL_FNAME_CHARS))
                if bad_chars:
                    chars_display = "  ".join(repr(c) for c in bad_chars)
                    QMessageBox.warning(
                        self,
                        "Illegal Characters in Diagram Name",
                        f"The @startuml diagram name contains characters that are "
                        f"illegal in Windows filenames. PlantUML uses this name "
                        f"for the output file, so rendering will fail.\n\n"
                        f"Line {line_num}: {stripped}\n\n"
                        f"Illegal characters: {chars_display}\n\n"
                        f"Please remove these characters from the @startuml line.",
                    )
                    return
                break  # Only need to check the first @startuml line

        # Try to render to PNG for background
        png_path = None
        try:
            png_path = render_puml_to_png(puml_path)
            self.load_background_png(png_path)
        except RuntimeError as e:
            QMessageBox.warning(
                self, "PlantUML Rendering",
                f"Could not render PNG background (Java/JAR issue).\n"
                f"Annotations will still be parsed from PUML text.\n\n{e}"
            )

        # Try to render SVG for pixel-accurate position extraction
        svg_path = None
        try:
            svg_path = render_puml_to_svg(puml_path)
        except RuntimeError:
            pass  # Fall back to auto-layout grid

        # Determine canvas dimensions
        if self.bg_item is not None:
            pm = self.bg_item.pixmap()
            canvas_w, canvas_h = pm.width(), pm.height()
        else:
            canvas_w, canvas_h = 1200, 800

        # Parse PUML to annotations (SVG positions when available)
        data = parse_puml_to_annotations(puml_text, canvas_w, canvas_h, svg_path=svg_path)
        num_annotations = len(data.get("annotations", []))

        # Place JSON in editor
        pretty = json.dumps(data, indent=2)
        self._set_draft_text_programmatically(
            pretty,
            enable_import=True,
            status=f"PUML imported: {num_annotations} annotations. Click Import to link JSON↔Scene.",
            focus_id=None,
        )

        self.statusBar().showMessage(
            f"Imported {puml_path} — {num_annotations} annotations extracted",
            8000,
        )

    def load_background_png(self, path: str):
        """Load a PNG image as the background."""
        if not os.path.exists(path):
            QMessageBox.warning(self, "File not found", f"File does not exist:\n{path}")
            return

        pm = QPixmap(path)
        if pm.isNull():
            QMessageBox.warning(self, "Invalid image", "Could not load image.")
            return

        if self.bg_item is not None:
            self.scene.removeItem(self.bg_item)
            self.bg_item = None

        self.bg_item = QGraphicsPixmapItem(pm)
        self.bg_item.setZValue(-1000)
        self.scene.addItem(self.bg_item)

        self.bg_path = path
        self.scene.setSceneRect(QRectF(pm.rect()))
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

        try:
            img = Image.open(path)
            w, h = img.size
            mode = img.mode
            mode_to_bpp = {"1": 1, "L": 8, "P": 8, "RGB": 24, "RGBA": 32, "CMYK": 32, "I": 32, "F": 32}
            bpp = mode_to_bpp.get(mode, "unknown")

            fi = QFileInfo(path)
            filesize_bytes = fi.size()
            filesize_kb = filesize_bytes / 1024.0

            self.props.set_image_info({
                "path": path,
                "size": f"{w} x {h}px",
                "mode": mode,
                "depth": f"{bpp} bpp" if bpp != "unknown" else "unknown",
                "filesize": f"{filesize_kb:.1f} KB",
            })
        except Exception:
            self.props.set_image_info({
                "path": path,
                "size": f"{pm.width()} x {pm.height()}px",
                "mode": "unknown",
                "depth": "unknown",
                "filesize": "unknown",
            })

        self.statusBar().showMessage(f"Loaded background (locked): {os.path.basename(path)}")

        # Enable and reset the PNG visibility toggle
        self.toggle_png_act.setEnabled(True)
        self.toggle_png_act.setChecked(False)
        self.toggle_png_act.setText("Hide PNG")
        self._update_png_hidden_indicator(False)

        # Update align button state (PNG is now loaded)
        self._update_align_button_state()

    def _toggle_png_visibility(self, checked: bool):
        """Toggle the visibility of the background PNG."""
        if self.bg_item is None:
            return

        # Get current style for icon update
        app = QApplication.instance()
        current_style = getattr(app, "_current_style", DEFAULT_STYLE)

        if checked:
            # Hide the PNG
            self.bg_item.setVisible(False)
            self.toggle_png_act.setText("Show PNG")
            self._icon_actions[self.toggle_png_act] = "show_png"
            self._update_png_hidden_indicator(True)
            self.statusBar().showMessage("Background PNG hidden")
        else:
            # Show the PNG
            self.bg_item.setVisible(True)
            self.toggle_png_act.setText("Hide PNG")
            self._icon_actions[self.toggle_png_act] = "hide_png"
            self._update_png_hidden_indicator(False)
            self.statusBar().showMessage("Background PNG visible")

        # Update the icon
        icon = create_icon_with_states(self._icon_actions[self.toggle_png_act], current_style)
        self.toggle_png_act.setIcon(icon)

    def _update_png_hidden_indicator(self, show: bool):
        """Show or hide the 'PNG Hidden' indicator in the corner of the canvas."""
        if show:
            if self._png_hidden_indicator is None:
                self._png_hidden_indicator = QGraphicsSimpleTextItem("[PNG Hidden]")
                self._png_hidden_indicator.setBrush(QBrush(QColor(255, 100, 100)))
                font = QFont("Arial", 12, QFont.Weight.Bold)
                self._png_hidden_indicator.setFont(font)
                self._png_hidden_indicator.setZValue(10000)  # Always on top
                self.scene.addItem(self._png_hidden_indicator)

            # Position in top-left corner of the scene
            scene_rect = self.scene.sceneRect()
            self._png_hidden_indicator.setPos(scene_rect.x() + 10, scene_rect.y() + 10)
            self._png_hidden_indicator.setVisible(True)
        else:
            if self._png_hidden_indicator is not None:
                self._png_hidden_indicator.setVisible(False)

    def clear_overlay(self):
        """Clear all overlay items from the scene."""
        self.scene.clearSelection()
        self.scene.blockSignals(True)
        try:
            for it in list(self.scene.items()):
                if it is self.bg_item or it is self._png_hidden_indicator:
                    continue
                if it.scene() is None:
                    continue  # Already removed (child of a removed group)
                if isinstance(it.parentItem(), MetaGroupItem):
                    continue  # Will be removed with its parent group
                if hasattr(it, "meta"):
                    self.scene.removeItem(it)
        finally:
            self.scene.blockSignals(False)
        self.props.set_item(None)

        if self._link_enabled and self._draft_data and isinstance(self._draft_data.get("annotations", None), list):
            self._draft_data["annotations"] = []
            self._rebuild_id_index()
            self._push_draft_data_to_editor(status="Overlay cleared; draft JSON updated.", focus_id=None)

    def delete_selected_items(self):
        """Delete selected items from the scene (with undo support)."""
        items = [it for it in self.scene.selectedItems()
                 if it is not self.bg_item and hasattr(it, "meta")]
        if not items:
            return

        # Create undo command
        def on_item_removed(item):
            """Callback when item is removed (redo/initial delete)."""
            ann_id = item.data(ANN_ID_KEY)
            if self._link_enabled and self._draft_data and isinstance(ann_id, str):
                anns = self._draft_data.get("annotations", [])
                if isinstance(anns, list):
                    self._draft_data["annotations"] = [
                        a for a in anns if not (isinstance(a, dict) and a.get("id") == ann_id)
                    ]
                    self._rebuild_id_index()

        def on_item_restored(item):
            """Callback when item is restored (undo)."""
            # Re-add to JSON
            if self._link_enabled and self._draft_data and hasattr(item, "to_record"):
                rec = item.to_record()
                anns = self._draft_data.get("annotations", [])
                if isinstance(anns, list):
                    anns.append(rec)
                    self._draft_data["annotations"] = anns
                    self._rebuild_id_index()

        # Use DeleteMultipleItemsCommand for multiple items
        if len(items) > 1:
            cmd = DeleteMultipleItemsCommand(
                self.scene, items,
                on_add_callback=on_item_restored,
                on_remove_callback=on_item_removed
            )
        else:
            cmd = DeleteItemCommand(
                self.scene, items[0],
                on_add_callback=on_item_restored,
                on_remove_callback=on_item_removed
            )

        self.undo_stack.push(cmd)
        self.props.set_item(None)

        # Update draft editor
        if self._link_enabled and self._draft_data:
            self._push_draft_data_to_editor(
                status=f"Deleted {len(items)} item(s); draft JSON updated.",
                focus_id=None
            )

        self.statusBar().showMessage(f"Deleted {len(items)} item(s).")

    # ---- Undo callbacks for move, resize, text edit ----

    def _on_items_moved(self, moved: dict):
        """Handle items moved — push MoveItemCommand(s) to undo stack."""
        if len(moved) == 1:
            item, (old_pos, new_pos) = next(iter(moved.items()))
            cmd = MoveItemCommand(item, old_pos, new_pos)
            self.undo_stack.push(cmd)
        else:
            self.undo_stack.beginMacro(f"Move {len(moved)} items")
            for item, (old_pos, new_pos) in moved.items():
                cmd = MoveItemCommand(item, old_pos, new_pos)
                self.undo_stack.push(cmd)
            self.undo_stack.endMacro()

        # Scroll is handled by _on_select_mouse_up (fired on mouse release).

    def _on_select_mouse_up(self):
        """Handle mouse release in SELECT mode — unlock scroll and scroll to selection."""
        self.draft.unlock_scroll()
        items = self.scene.selectedItems()
        if items:
            ann_id = items[0].data(ANN_ID_KEY)
            if isinstance(ann_id, str) and ann_id:
                if isinstance(items[0], MetaTextItem):
                    self.draft.jump_to_text_field_for_id(ann_id)
                else:
                    self._scroll_draft_to_id_top(ann_id)

    def _on_item_resize_finished(self, item, old_state, new_state):
        """Handle item resize finished — push ItemGeometryCommand to undo stack."""
        cmd = ItemGeometryCommand(item, old_state, new_state)
        self.undo_stack.push(cmd)

    def _on_text_edit_finished(self, item, old_text, new_text):
        """Handle text edit finished — push TextEditCommand to undo stack."""
        cmd = TextEditCommand(item, old_text, new_text)
        self.undo_stack.push(cmd)

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Delete:
            self.delete_selected_items()
            return
        super().keyPressEvent(event)

    def _on_zoom_region_triggered(self, checked: bool):
        """Handle zoom region tool activation."""
        if checked:
            # Enable zoom region mode with callback to uncheck the action
            def on_zoom_complete():
                self.zoom_region_act.setChecked(False)
                self.statusBar().showMessage("Zoomed to region.")

            self.view.set_zoom_region_mode(True, on_complete=on_zoom_complete)
            self.statusBar().showMessage("Drag to select zoom region...")
        else:
            self.view.set_zoom_region_mode(False)
            self.statusBar().clearMessage()

    def _on_zoom_fit(self):
        """Zoom to fit all content in view."""
        self.view.zoom_fit()
        self.zoom_region_act.setChecked(False)
        self.statusBar().showMessage("Zoomed to fit.")

    def _show_help_dialog(self, tab: int = 0):
        """Show the help dialog, optionally opening to a specific tab.

        Args:
            tab: Index of the tab to show (0=Quick Start, 1=Tools, 2=Shortcuts).
        """
        dialog = HelpDialog(self, initial_tab=tab)
        dialog.exec()

    def show_settings_dialog(self):
        """Show the settings dialog."""
        app = QApplication.instance()
        current_style = getattr(app, "_current_style", DEFAULT_STYLE)

        dialog = SettingsDialog(self.settings_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Settings are saved by the dialog on OK
            # Check if theme changed and apply it
            new_style = self.settings_manager.settings.theme
            if new_style != current_style and new_style in STYLES:
                app.setStyleSheet(STYLES[new_style])
                app._current_style = new_style
                self._update_toolbar_icons(new_style)
                self._update_default_text_color(new_style)
                self._update_editor_colors(new_style)
                self._update_draft_dock_icons(new_style)
                self.statusBar().showMessage(f"Theme changed to: {new_style}")
            else:
                self.statusBar().showMessage("Settings saved.")

    def save_project_dialog(self):
        """Save project (overlay JSON + PNG) to workspace directory."""
        workspace = str(self.settings_manager.get_workspace_dir())
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Project", workspace, "JSON (*.json)"
        )
        if not path:
            return

        save_dir = os.path.dirname(path)
        data = self._export_overlay_json()

        # Copy background PNG to save directory if it exists elsewhere
        bg = data.get("background_png", "")
        if bg and os.path.isfile(bg):
            bg_name = os.path.basename(bg)
            dest_png = os.path.join(save_dir, bg_name)
            if os.path.normpath(bg) != os.path.normpath(dest_png):
                try:
                    shutil.copy2(bg, dest_png)
                except Exception:
                    pass  # Keep absolute path if copy fails
                else:
                    data["background_png"] = bg_name

        try:
            os.makedirs(save_dir, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self.statusBar().showMessage(f"Saved project: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Save failed", str(e))

    def open_project_dialog(self):
        """Open a project (overlay JSON) from workspace directory."""
        workspace = str(self.settings_manager.get_workspace_dir())
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", workspace, "JSON (*.json)"
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Open failed", str(e))
            return
        self._apply_overlay_import(data, base_dir=os.path.dirname(path))
        self.statusBar().showMessage(f"Opened project: {path}")

    def export_pptx_dialog(self):
        """Export canvas to PowerPoint file."""
        initial_dir = ""
        if self.settings_manager.settings.pptx_export_to_source_dir and self.bg_path:
            initial_dir = os.path.dirname(self.bg_path)
        path, _ = QFileDialog.getSaveFileName(
            self, "Export PowerPoint", initial_dir, "PowerPoint (*.pptx)"
        )
        if not path:
            return

        # Ensure .pptx extension
        if not path.lower().endswith(".pptx"):
            path += ".pptx"

        # Collect annotations from canvas (skip group children)
        annotations = []
        for it in self.scene.items():
            if hasattr(it, "to_record") and hasattr(it, "meta"):
                if isinstance(it.parentItem(), MetaGroupItem):
                    continue
                annotations.append(it.to_record())
        annotations.reverse()  # Maintain z-order

        # Get scene rect for proper sizing
        sr = self.scene.sceneRect()
        scene_rect = {"x": sr.x(), "y": sr.y(), "w": sr.width(), "h": sr.height()}

        try:
            export_to_pptx(
                annotations=annotations,
                output_path=path,
                scene_rect=scene_rect,
                background_png=self.bg_path,
            )
            self.statusBar().showMessage(f"Exported PowerPoint: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Export failed", str(e))

    def _export_overlay_json(self) -> Dict[str, Any]:
        """Export current overlay as JSON."""
        ann: List[Dict[str, Any]] = []
        for it in self.scene.items():
            if hasattr(it, "to_record") and hasattr(it, "meta"):
                # Skip items that are children of a group (they're serialized by the group)
                if isinstance(it.parentItem(), MetaGroupItem):
                    continue
                ann.append(sort_annotation_keys(it.to_record()))
        ann.reverse()
        sr = self.scene.sceneRect()
        return {
            "version": "overlay-1.0",
            "background_png": self.bg_path or "",
            "scene_rect": {"x": sr.x(), "y": sr.y(), "w": sr.width(), "h": sr.height()},
            "annotations": ann,
        }

    def _apply_overlay_import(self, data: Dict[str, Any], base_dir: str = ""):
        """Import overlay from JSON data."""
        self.clear_overlay()

        bg = data.get("background_png", "")
        if bg:
            if not os.path.isabs(bg):
                candidate = os.path.join(base_dir, bg)
                if os.path.exists(candidate):
                    bg = candidate
            if os.path.exists(bg):
                self.load_background_png(bg)

        for rec in data.get("annotations", []):
            if isinstance(rec, dict):
                self._add_item_from_record(rec, on_change=self._on_scene_item_changed if self._link_enabled else None)

    def auto_extract(self):
        """Start Gemini AI extraction."""
        if not self.bg_path:
            QMessageBox.information(self, "No image", "Drop/open a PNG first.")
            return

        self.extract_act.setEnabled(False)
        self.statusBar().showMessage(f"Sending image to model: {self.model_name} ...")
        self._set_draft_text_programmatically("", enable_import=False, status="Calling model...", focus_id=None)

        self._thread = QThread()
        self._worker = ExtractWorker(self.bg_path, self.model_name)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.raw_text.connect(self.on_ai_raw_text)
        self._worker.finished.connect(self.on_ai_finished)
        self._worker.failed.connect(self.on_ai_failed)

        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)

        def _reenable():
            self.extract_act.setEnabled(True)

        self._thread.finished.connect(_reenable)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()

    def on_ai_raw_text(self, text: str):
        """Handle raw AI response text."""
        self._set_draft_text_programmatically(text, enable_import=False, status="Model responded (raw). Parsing...", focus_id=None)

    def on_ai_finished(self, data: dict):
        """Handle successful AI extraction."""
        # Normalize meta dicts to include all default fields
        annotations = data.get("annotations", [])
        if isinstance(annotations, list):
            for rec in annotations:
                if isinstance(rec, dict) and "kind" in rec:
                    kind = rec["kind"]
                    meta = rec.get("meta", {}) or {}
                    rec["meta"] = normalize_meta(meta, kind)

        sorted_data = sort_draft_data(data)
        pretty = json.dumps(sorted_data, indent=2)
        self._set_draft_text_programmatically(pretty, enable_import=True, status="Draft ready. Click Import to link JSON<->Scene.", focus_id=None)
        self.statusBar().showMessage("AI draft received.")

    def on_ai_failed(self, err: str):
        """Handle AI extraction failure."""
        QMessageBox.critical(self, "Auto-Extract failed", err)
        self._set_draft_text_programmatically(self.draft.get_json_text(), enable_import=False, status="Auto-Extract failed.", focus_id=None)
        self.statusBar().showMessage("Auto-Extract failed.")

    def import_draft_and_link(self):
        """Import draft JSON and enable bidirectional linking."""
        try:
            text = self.draft.get_json_text().strip()
            if not text:
                raise ValueError("Draft JSON is empty.")

            data = json.loads(text)
            if not (isinstance(data, dict) and isinstance(data.get("annotations", None), list)):
                raise ValueError("Draft JSON must contain an 'annotations' list.")

            if self.bg_item is not None:
                actual_w = float(self.bg_item.pixmap().width())
                actual_h = float(self.bg_item.pixmap().height())

                img_info = data.get("image", {}) or {}
                draft_w = float(img_info.get("width", actual_w))
                draft_h = float(img_info.get("height", actual_h))
                if draft_w <= 0 or draft_h <= 0:
                    draft_w, draft_h = actual_w, actual_h

                sx = actual_w / draft_w
                sy = actual_h / draft_h

                scaled = []
                for rec in data.get("annotations", []):
                    if not isinstance(rec, dict) or "kind" not in rec:
                        continue
                    kind = rec.get("kind", "")
                    if kind != "group" and "geom" not in rec:
                        continue
                    geom = rec.get("geom", {}) or {}

                    norm = False
                    try:
                        if kind in ("rect", "ellipse", "roundedrect", "hexagon", "cylinder", "blockarrow", "polygon") and "x" in geom and "w" in geom:
                            norm = _looks_normalized(float(geom["x"])) and _looks_normalized(float(geom["w"]))
                        elif kind == "line" and "x1" in geom and "x2" in geom:
                            norm = _looks_normalized(float(geom["x1"])) and _looks_normalized(float(geom["x2"]))
                        elif kind == "text" and "x" in geom:
                            norm = _looks_normalized(float(geom["x"]))
                    except Exception:
                        norm = False

                    rec2 = _scale_record(rec, actual_w, actual_h, normalized=True) if norm else _scale_record(rec, sx, sy, normalized=False)

                    if "id" not in rec2 or not isinstance(rec2.get("id"), str) or not rec2["id"]:
                        rec2["id"] = self._new_ann_id()

                    rec2.setdefault("style", {
                        "pen": {"color": "#FF0000", "width": 2},
                        "brush": {"color": "#00000000"},
                        "text": {"color": "#FFFF00", "size_pt": 12},
                    })
                    if isinstance(rec2["style"], dict):
                        rec2["style"].setdefault("text", {"color": "#FFFF00", "size_pt": 12})
                        if isinstance(rec2["style"].get("text"), dict):
                            rec2["style"]["text"].setdefault("size_pt", 12)

                    scaled.append(rec2)

                data["annotations"] = scaled

            self._draft_data = data
            self._link_enabled = True
            self._rebuild_id_index()
            self._rebuild_scene_from_draft()

            # Update align button state (linking is now enabled)
            self._update_align_button_state()

            self._push_draft_data_to_editor(status="Linked. Edits in JSON or scene will stay in sync.", focus_id=None)

            # Initialize highlight bar based on current cursor position in editor
            current_ann_id = self.draft.text._find_annotation_at_cursor()
            if current_ann_id:
                self._on_editor_cursor_annotation_changed(current_ann_id)

            self.draft.import_btn.setEnabled(True)
            self.statusBar().showMessage("Linked draft JSON <-> scene.")
        except Exception as e:
            QMessageBox.critical(self, "Import/Link failed", f"{e}\n\n{traceback.format_exc()}")

    def _on_draft_text_changed(self):
        """Handle draft text changes."""
        if self._syncing_from_scene:
            return

        if self._link_enabled:
            self._json_edit_timer.start()
        else:
            try:
                txt = self.draft.get_json_text()
                data = json.loads(txt)
                ok = isinstance(data, dict) and isinstance(data.get("annotations", None), list)
                self.draft.import_btn.setEnabled(ok)
                self.draft.set_status("" if ok else "Invalid schema (needs annotations list).")
            except Exception:
                self.draft.import_btn.setEnabled(False)
                self.draft.set_status("Invalid JSON.")

    def _apply_json_text_to_scene(self):
        """Apply JSON text changes to the scene (debounced)."""
        trace("_apply_json_text_to_scene called", "SYNC")
        if self._syncing_from_scene or not self._link_enabled:
            trace("_apply_json_text_to_scene skipped (syncing or not linked)", "SYNC")
            return

        txt = self.draft.get_json_text()
        try:
            trace("Parsing JSON...", "SYNC")
            data = json.loads(txt)
            if not (isinstance(data, dict) and isinstance(data.get("annotations", None), list)):
                self.draft.set_status("Invalid schema: must contain 'annotations' list.")
                return

            self._draft_data = data

            changed = False
            anns = self._draft_data.get("annotations", [])
            if isinstance(anns, list):
                for rec in anns:
                    if not isinstance(rec, dict):
                        continue
                    if "id" not in rec or not isinstance(rec.get("id"), str) or not rec["id"]:
                        rec["id"] = self._new_ann_id()
                        changed = True
                    rec.setdefault("style", {
                        "pen": {"color": "#FF0000", "width": 2},
                        "brush": {"color": "#00000000"},
                        "text": {"color": "#FFFF00", "size_pt": 12},
                    })
                    if isinstance(rec["style"], dict):
                        rec["style"].setdefault("text", {"color": "#FFFF00", "size_pt": 12})
                        if isinstance(rec["style"].get("text"), dict):
                            rec["style"]["text"].setdefault("size_pt", 12)

            trace("Rebuilding ID index...", "SYNC")
            self._rebuild_id_index()
            trace("Rebuilding scene from draft...", "SYNC")
            self._rebuild_scene_from_draft()
            trace("Scene rebuild complete", "SYNC")

            if changed:
                self._push_draft_data_to_editor(status="Added missing ids; scene updated.", focus_id=None)
            else:
                self.draft.set_status("Scene updated from JSON.")
        except Exception as e:
            self.draft.set_status(f"JSON parse error: {e}")

    def _rebuild_scene_from_draft(self):
        """Rebuild the scene from draft data."""
        trace("_rebuild_scene_from_draft called", "REBUILD")
        if not self._draft_data:
            trace("No draft data, returning", "REBUILD")
            return

        # Remember selected item ID to restore selection after rebuild
        selected_id = None
        selected_items = self.scene.selectedItems()
        if selected_items:
            selected_id = selected_items[0].data(ANN_ID_KEY)

        self._syncing_from_json = True
        try:
            # Clear property panel before removing items
            trace("Clearing property panel", "REBUILD")
            self.props.set_item(None)

            trace("Removing existing items from scene", "REBUILD")
            for it in list(self.scene.items()):
                if it is self.bg_item or it is self._png_hidden_indicator:
                    continue
                if it.scene() is None:
                    continue  # Already removed (child of a removed group)
                if isinstance(it.parentItem(), MetaGroupItem):
                    continue  # Will be removed with its parent group
                if hasattr(it, "meta"):
                    self.scene.removeItem(it)

            anns = self._draft_data.get("annotations", [])
            trace(f"Adding {len(anns) if isinstance(anns, list) else 0} items to scene", "REBUILD")
            if isinstance(anns, list):
                for idx, rec in enumerate(anns):
                    if isinstance(rec, dict):
                        trace(f"Adding item {idx+1}/{len(anns)}: {rec.get('kind', '?')} id={rec.get('id', '?')}", "REBUILD")
                        self._add_item_from_record(rec, on_change=self._on_scene_item_changed)
                        trace(f"Item {idx+1} added successfully", "REBUILD")

            # Restore selection if the item still exists
            restored_id = None
            if selected_id:
                for it in self.scene.items():
                    if hasattr(it, "meta") and it.data(ANN_ID_KEY) == selected_id:
                        it.setSelected(True)
                        self.props.set_item(it)
                        restored_id = selected_id
                        break
        finally:
            self._syncing_from_json = False

        # After syncing is done, update the editor highlight/scroll for restored selection.
        # This must happen after _syncing_from_json is False so the handlers don't bail out.
        if restored_id:
            self.draft.set_highlighted_annotation(restored_id)
            self._scroll_draft_to_id_top(restored_id)

    def _on_new_scene_item(self, item: QGraphicsItem):
        """Handle new item added to scene."""
        # Always handle tool mode change after item creation
        self._on_item_created()

        if self._syncing_from_json:
            return

        # Skip items that are children of a group (they're managed by the group)
        if isinstance(item.parentItem(), MetaGroupItem):
            return

        # Auto-enable linking and initialize draft data when items are created
        if self._draft_data is None:
            self._draft_data = {"version": "draft-1", "image": {}, "annotations": []}

        if not self._link_enabled:
            self._link_enabled = True
            self._rebuild_id_index()

        if not (hasattr(item, "to_record") and hasattr(item, "meta")):
            return

        rec = item.to_record()
        if "id" not in rec or not rec["id"]:
            rec["id"] = item.data(ANN_ID_KEY) if isinstance(item.data(ANN_ID_KEY), str) else self._new_ann_id()

        anns = self._draft_data.get("annotations", [])
        if not isinstance(anns, list):
            anns = []
            self._draft_data["annotations"] = anns

        # Guard against duplicate entries: if an annotation with this ID
        # already exists (e.g. from a _notify_changed during drawing drag),
        # update it in place instead of appending a second copy.
        ann_id_val = rec.get("id")
        existing_idx = None
        if ann_id_val:
            for i, existing in enumerate(anns):
                if isinstance(existing, dict) and existing.get("id") == ann_id_val:
                    existing_idx = i
                    break
        if existing_idx is not None:
            anns[existing_idx] = rec
        else:
            anns.append(rec)
        self._rebuild_id_index()
        self._push_draft_data_to_editor(status="Added item from scene; draft JSON updated.", focus_id=rec["id"])

        if isinstance(item, MetaTextItem):
            self.draft.jump_to_text_field_for_id(rec["id"])
        else:
            self._scroll_draft_to_id_top(rec["id"])

    def _on_scene_item_changed(self, item: QGraphicsItem):
        """Handle scene item geometry/style changes."""
        if self._syncing_from_json:
            return

        # Skip items that are children of a group (they're managed by the group)
        if isinstance(item.parentItem(), MetaGroupItem):
            return

        # Auto-enable linking when items are modified
        if self._draft_data is None:
            self._draft_data = {"version": "draft-1", "image": {}, "annotations": []}

        if not self._link_enabled:
            self._link_enabled = True
            self._rebuild_id_index()
        if not (hasattr(item, "to_record") and hasattr(item, "meta")):
            return

        ann_id = item.data(ANN_ID_KEY)
        if not isinstance(ann_id, str) or not ann_id:
            return

        idx = self._id_to_index.get(ann_id)
        if idx is None:
            self._on_new_scene_item(item)
            return

        anns = self._draft_data.get("annotations", [])
        if not isinstance(anns, list) or idx >= len(anns):
            self._rebuild_id_index()
            return

        rec = item.to_record()
        rec["id"] = ann_id

        if isinstance(anns[idx], dict):
            preserved = dict(anns[idx])
            preserved.update(rec)
            anns[idx] = preserved
        else:
            anns[idx] = rec

        # During active mouse drag/resize, update JSON text live but keep
        # the editor scroll position stable.  Scroll is deferred to
        # mouse-release (see _on_items_moved / resize finish).
        interacting = self.scene.is_interacting

        if interacting:
            # Only lock here if the deferred selection-scroll isn't pending.
            # When _lock_after_scroll is True, the deferred scroll hasn't
            # completed yet — locking now would capture the wrong position.
            if not self.draft._lock_after_scroll:
                self.draft.lock_scroll()
        else:
            self.draft.unlock_scroll()

        self._push_draft_data_to_editor(
            status="Draft JSON updated from scene change.",
            focus_id=None if interacting else ann_id,
            keep_scroll=interacting,
        )

        if not interacting:
            if isinstance(item, MetaTextItem):
                self.draft.jump_to_text_field_for_id(ann_id)
            else:
                self._scroll_draft_to_id_top(ann_id)

        if item in self.scene.selectedItems():
            self.props.set_item(item)

    def _do_group_items(self, items):
        """Group selected items into a MetaGroupItem."""
        if len(items) < 2:
            return

        ann_id = self._new_ann_id()
        # Use 'g' prefix for group IDs
        ann_id = "g" + ann_id[1:]
        group_item = MetaGroupItem(ann_id, self._on_scene_item_changed)
        group_item.meta.kind = "group"

        # Determine z-value for the group (max of children)
        max_z = max(it.zValue() for it in items)
        self.scene.addItem(group_item)
        group_item.setZValue(max_z)

        # Suppress callbacks — addToGroup() adjusts child positions,
        # triggering ItemPositionHasChanged which would create duplicates.
        self._syncing_from_json = True
        try:
            for child in items:
                group_item.add_member(child)
        finally:
            self._syncing_from_json = False

        # Update JSON: remove individual child records, add group record
        if self._link_enabled and self._draft_data:
            anns = self._draft_data.get("annotations", [])
            child_ids = {getattr(it, "ann_id", None) for it in items}
            self._draft_data["annotations"] = [
                a for a in anns if not (isinstance(a, dict) and a.get("id") in child_ids)
            ]
            rec = group_item.to_record()
            self._draft_data["annotations"].append(rec)
            self._rebuild_id_index()
            self._push_draft_data_to_editor(
                status=f"Grouped {len(items)} items.", focus_id=ann_id
            )

        def on_grouped(g, children):
            """Redo callback: re-sync JSON after grouping."""
            if self._link_enabled and self._draft_data:
                anns = self._draft_data.get("annotations", [])
                child_ids = {getattr(c, "ann_id", None) for c in children}
                self._draft_data["annotations"] = [
                    a for a in anns if not (isinstance(a, dict) and a.get("id") in child_ids)
                ]
                self._draft_data["annotations"].append(g.to_record())
                self._rebuild_id_index()
                self._push_draft_data_to_editor(status="Grouped items (redo).", focus_id=g.ann_id)

        def on_ungrouped(g, children):
            """Undo callback: re-sync JSON after ungrouping."""
            if self._link_enabled and self._draft_data:
                anns = self._draft_data.get("annotations", [])
                self._draft_data["annotations"] = [
                    a for a in anns if not (isinstance(a, dict) and a.get("id") == g.ann_id)
                ]
                for child in children:
                    if hasattr(child, "to_record"):
                        self._draft_data["annotations"].append(child.to_record())
                self._rebuild_id_index()
                self._push_draft_data_to_editor(status="Ungrouped items (undo).")

        cmd = GroupItemsCommand(
            self.scene, group_item, items,
            on_grouped_callback=on_grouped,
            on_ungrouped_callback=on_ungrouped,
        )
        self.undo_stack.push(cmd)
        group_item.setSelected(True)

    def _do_ungroup_item(self, group_item):
        """Ungroup a MetaGroupItem, restoring children as independent items."""
        if not isinstance(group_item, MetaGroupItem):
            return

        children = list(group_item.member_items())
        if not children:
            return

        # Get absolute positions from group's to_record before ungrouping
        group_rec = group_item.to_record()
        child_recs = group_rec.get("children", [])

        # Suppress callbacks — removeFromGroup() adjusts child positions
        # from group-local to scene coords, which triggers
        # ItemPositionHasChanged → _on_scene_item_changed.  Without
        # suppression that creates duplicate annotation records.
        self._syncing_from_json = True
        try:
            for child in children:
                group_item.remove_member(child)
            self.scene.removeItem(group_item)
        finally:
            self._syncing_from_json = False

        # Update JSON: remove group record, add individual child records
        if self._link_enabled and self._draft_data:
            anns = self._draft_data.get("annotations", [])
            self._draft_data["annotations"] = [
                a for a in anns if not (isinstance(a, dict) and a.get("id") == group_item.ann_id)
            ]
            for child_rec in child_recs:
                self._draft_data["annotations"].append(child_rec)
            self._rebuild_id_index()
            self._push_draft_data_to_editor(
                status=f"Ungrouped {len(children)} items."
            )

        def on_grouped(g, child_items):
            """Undo callback: re-sync JSON after re-grouping."""
            if self._link_enabled and self._draft_data:
                anns = self._draft_data.get("annotations", [])
                child_ids = {getattr(c, "ann_id", None) for c in child_items}
                self._draft_data["annotations"] = [
                    a for a in anns if not (isinstance(a, dict) and a.get("id") in child_ids)
                ]
                self._draft_data["annotations"].append(g.to_record())
                self._rebuild_id_index()
                self._push_draft_data_to_editor(status="Grouped items (undo).", focus_id=g.ann_id)

        def on_ungrouped(g, child_items):
            """Redo callback: re-sync JSON after ungrouping."""
            if self._link_enabled and self._draft_data:
                anns = self._draft_data.get("annotations", [])
                self._draft_data["annotations"] = [
                    a for a in anns if not (isinstance(a, dict) and a.get("id") == g.ann_id)
                ]
                for child in child_items:
                    if hasattr(child, "to_record"):
                        self._draft_data["annotations"].append(child.to_record())
                self._rebuild_id_index()
                self._push_draft_data_to_editor(status="Ungrouped items (redo).")

        cmd = UngroupItemsCommand(
            self.scene, group_item, children,
            on_grouped_callback=on_grouped,
            on_ungrouped_callback=on_ungrouped,
        )
        self.undo_stack.push(cmd)
        self.props.set_item(None)

    def _on_z_order_changed(self):
        """Handle z-order changes - update all items in JSON."""
        if self._syncing_from_json or self._draft_data is None:
            return

        if not self._link_enabled:
            return

        anns = self._draft_data.get("annotations", [])
        if not isinstance(anns, list):
            return

        # Update z-index for all annotation items (skip group children)
        for item in self.scene.items():
            if not (hasattr(item, "to_record") and hasattr(item, "ann_id")):
                continue
            if isinstance(item.parentItem(), MetaGroupItem):
                continue

            ann_id = item.data(ANN_ID_KEY)
            if not isinstance(ann_id, str) or not ann_id:
                continue

            idx = self._id_to_index.get(ann_id)
            if idx is None or idx >= len(anns):
                continue

            # Update z-index in the record
            z = item.zValue()
            if isinstance(anns[idx], dict):
                if z != 0:
                    anns[idx]["z"] = int(z)
                elif "z" in anns[idx]:
                    del anns[idx]["z"]  # Remove z if it's 0 (default)

        self._push_draft_data_to_editor(status="Z-order updated.")

    def _push_draft_data_to_editor(self, status: str = "", focus_id: Optional[str] = None,
                                    keep_scroll: bool = False):
        """Push draft data to the editor."""
        if self._draft_data is None:
            return
        sorted_data = sort_draft_data(self._draft_data)
        pretty = json.dumps(sorted_data, indent=2)
        self._set_draft_text_programmatically(pretty, enable_import=True, status=status,
                                              focus_id=focus_id, keep_scroll=keep_scroll)

    def _set_draft_text_programmatically(self, text: str, enable_import: bool, status: str = "",
                                         focus_id: Optional[str] = None, keep_scroll: bool = False):
        """Set draft text without triggering change handlers."""
        self._syncing_from_scene = True
        try:
            self.draft.text.blockSignals(True)
            if keep_scroll:
                # Replace content via QTextCursor edit — preserves scroll
                # position unlike setPlainText() which resets everything.
                self.draft.replace_json_text_keep_scroll(text, status=status)
            else:
                self.draft.set_json_text(text, enable_import=enable_import, status=status)
            self.draft.text.blockSignals(False)

            # blockSignals suppressed textChanged/blockCountChanged — manually
            # trigger the updates that those signals would have driven.
            self.draft.text._recompute_fold_regions()
            self.draft.text._update_margins()
        finally:
            self._syncing_from_scene = False

        if focus_id:
            self._scroll_draft_to_id_top(focus_id)

    def _rebuild_id_index(self):
        """Rebuild the annotation ID index."""
        self._id_to_index = {}
        if not self._draft_data:
            return
        anns = self._draft_data.get("annotations", [])
        if not isinstance(anns, list):
            return
        for i, rec in enumerate(anns):
            if isinstance(rec, dict) and isinstance(rec.get("id"), str):
                self._id_to_index[rec["id"]] = i

    def _new_ann_id(self) -> str:
        """Generate a new annotation ID."""
        s = f"a{self._id_counter:06d}"
        self._id_counter += 1
        return s

    def _add_item_from_record(self, rec: Dict[str, Any], on_change=None):
        """Create a canvas item from a JSON record."""
        trace(f"_add_item_from_record: kind={rec.get('kind')}, id={rec.get('id')}", "ITEM")
        kind = rec.get("kind")
        ann_id = rec.get("id")
        if not isinstance(ann_id, str) or not ann_id:
            ann_id = self._new_ann_id()

        meta_dict = rec.get("meta") or {}
        try:
            meta = AnnotationMeta(**meta_dict) if isinstance(meta_dict, dict) else AnnotationMeta(kind=kind or "unknown")
        except Exception:
            meta = AnnotationMeta(kind=kind or "unknown")

        # Strip brackets from tech field - they will be added in the view
        if meta.tech:
            meta.tech = meta.tech.strip().strip("[]").strip()

        # Parse C4-style text if meta fields are empty and text field exists
        text_content = rec.get("text", "")
        if text_content and not meta.label and not meta.tech and not meta.note:
            label, tech, note = parse_c4_text(str(text_content))
            meta.label = label
            # Strip brackets from parsed tech as well
            meta.tech = tech.strip().strip("[]").strip() if tech else ""
            meta.note = note

        # Get z-index from record (will be applied after item is created)
        z_index = rec.get("z", 0)

        it = None

        if kind == "rect":
            g = rec.get("geom", {})
            trace(f"  Creating MetaRectItem at ({g.get('x')}, {g.get('y')})", "ITEM")
            it = MetaRectItem(float(g["x"]), float(g["y"]), float(g["w"]), float(g["h"]), ann_id, on_change)
            trace("  Setting meta", "ITEM")
            it.set_meta(meta)
            it.meta.kind = "rect"
            trace("  Applying style", "ITEM")
            it.apply_style_from_record(rec)
            it._apply_pen_brush()
            trace("  Updating label text", "ITEM")
            it._update_label_text()
            trace("  Adding to scene", "ITEM")
            self.scene.addItem(it)
            if z_index:
                it.setZValue(z_index)
            trace("  Rect item complete", "ITEM")

        elif kind == "roundedrect":
            g = rec.get("geom", {})
            adjust1 = float(g.get("adjust1", g.get("radius", 10)))  # Support legacy "radius" key
            trace(f"  Creating MetaRoundedRectItem at ({g.get('x')}, {g.get('y')})", "ITEM")
            it = MetaRoundedRectItem(float(g["x"]), float(g["y"]), float(g["w"]), float(g["h"]), adjust1, ann_id, on_change)
            trace("  Setting meta", "ITEM")
            it.set_meta(meta)
            it.meta.kind = "roundedrect"
            trace("  Applying style", "ITEM")
            it.apply_style_from_record(rec)
            it._apply_pen_brush()
            trace("  Updating label text", "ITEM")
            it._update_label_text()
            trace("  Adding to scene", "ITEM")
            self.scene.addItem(it)
            if z_index:
                it.setZValue(z_index)
            trace("  RoundedRect item complete", "ITEM")

        elif kind == "ellipse":
            g = rec.get("geom", {})
            trace(f"  Creating MetaEllipseItem at ({g.get('x')}, {g.get('y')})", "ITEM")
            it = MetaEllipseItem(float(g["x"]), float(g["y"]), float(g["w"]), float(g["h"]), ann_id, on_change)
            trace("  Setting meta", "ITEM")
            it.set_meta(meta)
            it.meta.kind = "ellipse"
            trace("  Applying style", "ITEM")
            it.apply_style_from_record(rec)
            it._apply_pen_brush()
            trace("  Updating label text", "ITEM")
            it._update_label_text()
            trace("  Adding to scene", "ITEM")
            self.scene.addItem(it)
            if z_index:
                it.setZValue(z_index)
            trace("  Ellipse item complete", "ITEM")

        elif kind == "line":
            g = rec.get("geom", {})
            trace(f"  Creating MetaLineItem from ({g.get('x1')}, {g.get('y1')}) to ({g.get('x2')}, {g.get('y2')})", "ITEM")
            it = MetaLineItem(float(g["x1"]), float(g["y1"]), float(g["x2"]), float(g["y2"]), ann_id, on_change)
            trace("  Setting meta", "ITEM")
            it.set_meta(meta)
            it.meta.kind = "line"
            trace("  Applying style", "ITEM")
            it.apply_style_from_record(rec)
            it._apply_pen()
            trace("  Updating label text", "ITEM")
            it._update_label_text()
            trace("  Adding to scene", "ITEM")
            self.scene.addItem(it)
            if z_index:
                it.setZValue(z_index)
            trace("  Line item complete", "ITEM")

        elif kind == "text":
            g = rec.get("geom", {})
            text = rec.get("text", "")
            it = MetaTextItem(float(g["x"]), float(g["y"]), str(text), ann_id, on_change)
            it.set_meta(meta)
            it.meta.kind = "text"
            it.apply_style_from_record(rec)
            it._apply_text_style()
            self.scene.addItem(it)
            if z_index:
                it.setZValue(z_index)

        elif kind == "hexagon":
            g = rec.get("geom", {})
            adjust1 = float(g.get("adjust1", 0.25))
            it = MetaHexagonItem(float(g["x"]), float(g["y"]), float(g["w"]), float(g["h"]), adjust1, ann_id, on_change)
            it.set_meta(meta)
            it.meta.kind = "hexagon"
            it.apply_style_from_record(rec)
            it._apply_pen_brush()
            it._update_label_text()
            self.scene.addItem(it)
            if z_index:
                it.setZValue(z_index)

        elif kind == "cylinder":
            g = rec.get("geom", {})
            adjust1 = float(g.get("adjust1", 0.15))
            it = MetaCylinderItem(float(g["x"]), float(g["y"]), float(g["w"]), float(g["h"]), adjust1, ann_id, on_change)
            it.set_meta(meta)
            it.meta.kind = "cylinder"
            it.apply_style_from_record(rec)
            it._apply_pen_brush()
            it._update_label_text()
            self.scene.addItem(it)
            if z_index:
                it.setZValue(z_index)

        elif kind == "blockarrow":
            g = rec.get("geom", {})
            adjust2 = float(g.get("adjust2", 15))
            adjust1 = float(g.get("adjust1", 0.5))
            it = MetaBlockArrowItem(float(g["x"]), float(g["y"]), float(g["w"]), float(g["h"]), adjust2, adjust1, ann_id, on_change)
            it.set_meta(meta)
            it.meta.kind = "blockarrow"
            it.apply_style_from_record(rec)
            it._apply_pen_brush()
            it._update_label_text()
            self.scene.addItem(it)
            if z_index:
                it.setZValue(z_index)

        elif kind == "polygon":
            g = rec.get("geom", {})
            points = g.get("points", [[0, 0], [1, 0], [1, 1], [0, 1]])
            it = MetaPolygonItem(float(g["x"]), float(g["y"]), float(g["w"]), float(g["h"]),
                                 points, ann_id, on_change)
            it.set_meta(meta)
            it.meta.kind = "polygon"
            it.apply_style_from_record(rec)
            it._apply_pen_brush()
            it._update_label_text()
            self.scene.addItem(it)
            if z_index:
                it.setZValue(z_index)

        elif kind == "group":
            children_recs = rec.get("children", [])
            it = MetaGroupItem(ann_id, on_change)
            it.set_meta(meta)
            self.scene.addItem(it)
            for child_rec in children_recs:
                child_item = self._add_item_from_record(child_rec, on_change=on_change)
                if child_item:
                    it.add_member(child_item)
            if z_index:
                it.setZValue(z_index)

        return it

    # ---- Alignment methods ----

    def _update_align_button_state(self):
        """Update the align button enabled state based on current conditions."""
        if not HAS_ALIGNMENT:
            return

        # Check base conditions for all alignment operations
        base_conditions_met = (
            self.bg_path is not None and  # PNG file is loaded
            self._link_enabled  # JSON and canvas are linked
        )

        items = self.scene.selectedItems()
        has_single_selection = len(items) == 1

        # Update shape align button
        if self.align_act is not None:
            if base_conditions_met and has_single_selection and self._is_alignable_item(items[0]):
                self.align_act.setEnabled(True)
            else:
                self.align_act.setEnabled(False)

        # Update line align button
        if self.align_line_act is not None:
            if base_conditions_met and has_single_selection and isinstance(items[0], MetaLineItem):
                self.align_line_act.setEnabled(True)
            else:
                self.align_line_act.setEnabled(False)

    def _is_alignable_item(self, item) -> bool:
        """Check if an item is alignable (rect, roundedrect, ellipse, hexagon, cylinder, blockarrow)."""
        return isinstance(item, (MetaRectItem, MetaRoundedRectItem, MetaEllipseItem, MetaHexagonItem, MetaCylinderItem, MetaBlockArrowItem, MetaPolygonItem))

    def align_selected_to_png(self):
        """Start alignment of the selected item to match the PNG visual."""
        if not HAS_ALIGNMENT:
            QMessageBox.warning(self, "Align", "Alignment requires opencv-python. Run: pip install opencv-python numpy")
            return

        items = self.scene.selectedItems()
        if len(items) != 1:
            QMessageBox.warning(self, "Align", "Please select exactly one shape to align.")
            return

        item = items[0]
        if not self._is_alignable_item(item):
            QMessageBox.warning(self, "Align", "Only rect, roundedrect, and ellipse items can be aligned.")
            return

        if self.bg_path is None:
            QMessageBox.warning(self, "Align", "No PNG image loaded.")
            return

        # Extract geometry from item
        pos = item.pos()
        if isinstance(item, MetaRoundedRectItem):
            geom = {
                "x": pos.x(),
                "y": pos.y(),
                "w": item._width,
                "h": item._height,
                "adjust1": item._adjust1,
            }
            kind = "roundedrect"
        else:
            rect = item.rect()
            geom = {
                "x": pos.x(),
                "y": pos.y(),
                "w": rect.width(),
                "h": rect.height(),
            }
            kind = "rect" if isinstance(item, MetaRectItem) else "ellipse"

        # Extract pen/stroke color and width from item
        pen_color = "#000000"  # Default black
        pen_width = 2  # Default width
        if hasattr(item, "pen_color"):
            pc = item.pen_color
            # Convert QColor to hex string
            pen_color = "#{:02X}{:02X}{:02X}".format(pc.red(), pc.green(), pc.blue())
        if hasattr(item, "pen_width"):
            pen_width = int(item.pen_width)

        # Disable button during alignment
        self.align_act.setEnabled(False)
        self.statusBar().showMessage(f"Aligning {kind} to PNG (pen color: {pen_color}, width: {pen_width})...")

        # Start worker thread
        self._align_thread = QThread()
        self._align_worker = AlignmentWorker(self.bg_path, geom, kind, pen_color, pen_width)
        self._align_worker.moveToThread(self._align_thread)

        self._align_thread.started.connect(self._align_worker.run)
        self._align_worker.progress.connect(self.on_align_progress)
        self._align_worker.finished.connect(self.on_align_finished)
        self._align_worker.failed.connect(self.on_align_failed)

        self._align_worker.finished.connect(self._align_thread.quit)
        self._align_worker.failed.connect(self._align_thread.quit)

        def _reenable():
            self._update_align_button_state()

        self._align_thread.finished.connect(_reenable)
        self._align_thread.finished.connect(self._align_thread.deleteLater)

        self._align_thread.start()

    def on_align_progress(self, iteration: int, message: str):
        """Handle progress updates from alignment worker."""
        self.statusBar().showMessage(f"Alignment: {message} (iter {iteration})")

    def on_align_finished(self, result: dict):
        """Handle successful alignment completion."""
        items = self.scene.selectedItems()
        if len(items) != 1:
            self.statusBar().showMessage("Alignment complete but selection changed.")
            return

        item = items[0]
        if not self._is_alignable_item(item):
            self.statusBar().showMessage("Alignment complete but item type changed.")
            return

        # Apply new geometry to item
        from PyQt6.QtCore import QPointF, QRectF

        new_x = float(result["x"])
        new_y = float(result["y"])
        new_w = float(result["w"])
        new_h = float(result["h"])

        if isinstance(item, MetaRoundedRectItem):
            item.setPos(QPointF(new_x, new_y))
            item._width = new_w
            item._height = new_h
            if "adjust1" in result:
                item._adjust1 = float(result["adjust1"])
            item._update_path()
            item._update_label_position()
        else:
            item.setPos(QPointF(new_x, new_y))
            item.setRect(QRectF(0, 0, new_w, new_h))

        # Apply optimized pen width if returned
        if "pen_width" in result and hasattr(item, "pen_width"):
            from PyQt6.QtGui import QPen
            new_pen_width = int(result["pen_width"])
            item.pen_width = new_pen_width
            # Update the item's pen
            pen = item.pen()
            pen.setWidth(new_pen_width)
            item.setPen(pen)

        # Apply sampled pen color if returned
        if "pen_color" in result:
            from PyQt6.QtGui import QColor
            new_color_hex = result["pen_color"]
            new_color = QColor(new_color_hex)

            # Update pen color
            if hasattr(item, "pen_color"):
                item.pen_color = new_color
                pen = item.pen()
                pen.setColor(new_color)
                item.setPen(pen)

            # Update text/label color to match
            if hasattr(item, "text_color"):
                item.text_color = new_color
            # Refresh the label on the canvas
            if hasattr(item, "_update_label_text"):
                item._update_label_text()

        # Trigger JSON sync
        item._notify_changed()

        # Build status message
        msg = "Alignment complete - element adjusted to match PNG."
        extras = []
        if "pen_width" in result:
            extras.append(f"pen_width={result['pen_width']}")
        if "pen_color" in result:
            extras.append(f"pen_color={result['pen_color']}")
        if "adjust1" in result:
            extras.append(f"adjust1={result['adjust1']}")
        if extras:
            msg += f" ({', '.join(extras)})"
        self.statusBar().showMessage(msg)

    def on_align_failed(self, error: str):
        """Handle alignment failure."""
        QMessageBox.critical(self, "Alignment failed", error)
        self.statusBar().showMessage("Alignment failed.")

    # ---- Line Alignment methods ----

    def align_selected_line_to_png(self):
        """Start alignment of the selected line item to match the PNG visual."""
        if not HAS_ALIGNMENT:
            QMessageBox.warning(self, "Align Line", "Alignment requires opencv-python. Run: pip install opencv-python numpy")
            return

        items = self.scene.selectedItems()
        if len(items) != 1:
            QMessageBox.warning(self, "Align Line", "Please select exactly one line to align.")
            return

        item = items[0]
        if not isinstance(item, MetaLineItem):
            QMessageBox.warning(self, "Align Line", "Only line items can be aligned with this tool.")
            return

        if self.bg_path is None:
            QMessageBox.warning(self, "Align Line", "No PNG image loaded.")
            return

        # Extract geometry from line item
        pos = item.pos()
        line = item.line()
        geom = {
            "x1": pos.x() + line.x1(),
            "y1": pos.y() + line.y1(),
            "x2": pos.x() + line.x2(),
            "y2": pos.y() + line.y2(),
        }

        # Extract pen/stroke color and width from item
        pen_color = "#000000"  # Default black
        pen_width = 2  # Default width
        if hasattr(item, "pen_color"):
            pc = item.pen_color
            pen_color = "#{:02X}{:02X}{:02X}".format(pc.red(), pc.green(), pc.blue())
        if hasattr(item, "pen_width"):
            pen_width = int(item.pen_width)

        # Extract note and label text from meta for text matching in PNG
        note_text = ""
        label_text = ""
        if hasattr(item, "meta"):
            if hasattr(item.meta, "note"):
                note_text = item.meta.note or ""
            if hasattr(item.meta, "label"):
                label_text = item.meta.label or ""

        # Disable button during alignment
        self.align_line_act.setEnabled(False)
        status_msg = f"Aligning line to PNG (pen color: {pen_color}, width: {pen_width})"
        if label_text:
            status_msg += f", searching for label: '{label_text}'"
        if note_text:
            status_msg += f", note: '{note_text}'"
        self.statusBar().showMessage(status_msg + "...")

        # Start worker thread
        self._line_align_thread = QThread()
        self._line_align_worker = LineAlignmentWorker(
            self.bg_path, geom, pen_color, pen_width, note_text, label_text
        )
        self._line_align_worker.moveToThread(self._line_align_thread)

        self._line_align_thread.started.connect(self._line_align_worker.run)
        self._line_align_worker.progress.connect(self.on_line_align_progress)
        self._line_align_worker.finished.connect(self.on_line_align_finished)
        self._line_align_worker.failed.connect(self.on_line_align_failed)

        self._line_align_worker.finished.connect(self._line_align_thread.quit)
        self._line_align_worker.failed.connect(self._line_align_thread.quit)

        def _reenable():
            self._update_align_button_state()

        self._line_align_thread.finished.connect(_reenable)
        self._line_align_thread.finished.connect(self._line_align_thread.deleteLater)

        self._line_align_thread.start()

    def on_line_align_progress(self, iteration: int, message: str):
        """Handle progress updates from line alignment worker."""
        self.statusBar().showMessage(f"Line alignment: {message} (iter {iteration})")

    def on_line_align_finished(self, result: dict):
        """Handle successful line alignment completion."""
        items = self.scene.selectedItems()
        if len(items) != 1:
            self.statusBar().showMessage("Line alignment complete but selection changed.")
            return

        item = items[0]
        if not isinstance(item, MetaLineItem):
            self.statusBar().showMessage("Line alignment complete but item type changed.")
            return

        # Apply new geometry to line item
        from PyQt6.QtCore import QPointF, QLineF

        new_x1 = float(result["x1"])
        new_y1 = float(result["y1"])
        new_x2 = float(result["x2"])
        new_y2 = float(result["y2"])

        # Set position to the start point, line is relative from there
        item.setPos(QPointF(new_x1, new_y1))
        item.setLine(QLineF(0, 0, new_x2 - new_x1, new_y2 - new_y1))

        # Apply arrow mode and size
        if "arrow_mode" in result:
            item.arrow_mode = result["arrow_mode"]
        if "arrow_size" in result and hasattr(item, "arrow_size"):
            item.arrow_size = float(result["arrow_size"])

        # Apply pen color
        if "pen_color" in result:
            from PyQt6.QtGui import QColor
            new_color = QColor(result["pen_color"])
            item.pen_color = new_color
            item.text_color = new_color

        # Apply pen width
        if "pen_width" in result:
            item.pen_width = int(result["pen_width"])

        # Apply dash properties if line is dashed
        if "dash" in result and result["dash"] == "dashed":
            if hasattr(item, "line_dash"):
                item.line_dash = result["dash"]  # "dashed"
            if hasattr(item, "dash_pattern_length") and "dash_pattern_length" in result:
                item.dash_pattern_length = float(result["dash_pattern_length"])
            if hasattr(item, "dash_solid_percent") and "dash_solid_percent" in result:
                item.dash_solid_percent = float(result["dash_solid_percent"])

        # Update pen and visuals
        item._apply_pen()
        item._update_label_text()

        # Trigger JSON sync
        item._notify_changed()

        # Refresh property panel to show updated values
        self.props.set_item(item)

        # Build status message
        msg = "Line alignment complete - line adjusted to match PNG."
        extras = []
        if "pen_width" in result:
            extras.append(f"pen_width={result['pen_width']}")
        if "pen_color" in result:
            extras.append(f"pen_color={result['pen_color']}")
        if "arrow_mode" in result:
            extras.append(f"arrow={result['arrow_mode']}")
        if "arrow_size" in result:
            extras.append(f"arrow_size={result['arrow_size']}px")
        if "dash" in result:
            extras.append(f"dash={result['dash']}")
            if "dash_pattern_length" in result:
                extras.append(f"dash_length={result['dash_pattern_length']}px")
        if extras:
            msg += f" ({', '.join(extras)})"
        self.statusBar().showMessage(msg)

    def on_line_align_failed(self, error: str):
        """Handle line alignment failure."""
        QMessageBox.critical(self, "Line alignment failed", error)
        self.statusBar().showMessage("Line alignment failed.")


def main():
    """Application entry point."""
    trace("Application starting", "MAIN")
    app = QApplication(sys.argv)

    # Load settings (use singleton to ensure single instance)
    trace("Loading settings", "MAIN")
    settings_manager = get_settings()

    # Ensure settings file has all sections
    settings_manager.ensure_file_complete()

    # Apply saved theme (or default if not set)
    initial_style = settings_manager.settings.theme
    if initial_style not in STYLES:
        initial_style = DEFAULT_STYLE
        settings_manager.settings.theme = initial_style

    app.setStyleSheet(STYLES[initial_style])
    app._current_style = initial_style

    # Save settings on application quit
    def save_on_quit():
        trace("Saving settings on quit", "MAIN")
        settings_manager.save()
        close_log()

    app.aboutToQuit.connect(save_on_quit)

    trace("Creating MainWindow", "MAIN")
    w = MainWindow(settings_manager)
    w.resize(1550, 980)
    trace("Showing MainWindow", "MAIN")
    w.show()
    trace("Entering event loop", "MAIN")
    sys.exit(app.exec())


if __name__ == "__main__":
    # Set up global exception handler to catch crashes
    def excepthook(exc_type, exc_value, exc_tb):
        import traceback
        trace("UNCAUGHT EXCEPTION:", "CRASH")
        trace("".join(traceback.format_exception(exc_type, exc_value, exc_tb)), "CRASH")
        close_log()
        sys.__excepthook__(exc_type, exc_value, exc_tb)

    sys.excepthook = excepthook

    try:
        main()
    except Exception as e:
        trace(f"FATAL: {type(e).__name__}: {e}", "CRASH")
        trace_exception("Fatal exception")
        close_log()
        raise
