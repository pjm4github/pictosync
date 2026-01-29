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
from PyQt6.QtGui import QAction, QBrush, QColor, QFont, QIcon, QKeySequence, QPen, QPixmap
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
)
from editor import DraftDock
from properties import PropertyPanel
from gemini import ExtractWorker
from styles import STYLES, DEFAULT_STYLE, CANVAS_TEXT_COLORS, LINE_NUMBER_COLORS

# Optional alignment import (requires opencv-python)
try:
    from alignment import AlignmentWorker
    HAS_ALIGNMENT = True
except ImportError:
    AlignmentWorker = None
    HAS_ALIGNMENT = False


class SettingsDialog(QDialog):
    """Settings dialog for application preferences."""

    def __init__(self, current_style: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)

        # Form layout for settings
        form = QFormLayout()
        layout.addLayout(form)

        # Style picker
        self.style_combo = QComboBox()
        self.style_combo.addItems(list(STYLES.keys()))
        if current_style in STYLES:
            self.style_combo.setCurrentText(current_style)
        form.addRow("Theme:", self.style_combo)

        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def selected_style(self) -> str:
        """Return the selected style name."""
        return self.style_combo.currentText()


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
    """Main application window for the Diagram Overlay Annotator."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PictoSync - Diagram Annotation with AI Extraction")

        # Scene and view
        self.scene = AnnotatorScene()
        self.scene.setSceneRect(0, 0, 1200, 800)

        self.bg_item: Optional[QGraphicsPixmapItem] = None
        self.bg_path: Optional[str] = None

        # Hidden PNG indicator
        self._png_hidden_indicator: Optional[QGraphicsSimpleTextItem] = None

        self.view = AnnotatorView(self.scene, self.load_background_png)

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

        # Pre-initialize optional action (may be set in _build_toolbar if HAS_ALIGNMENT)
        self.align_act: Optional[QAction] = None

        # Build UI
        self._build_toolbar()
        self._build_menus()

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

        # Set up text editing callbacks to disable shortcuts during editing
        self._setup_text_editing_callbacks()

        self.statusBar().showMessage("Drop a PNG. Auto-Extract or edit Draft JSON. Import links JSON<->Scene.")
        self.props.set_image_info({})

        # Gemini worker thread
        self._thread: Optional[QThread] = None
        self._worker: Optional[ExtractWorker] = None

        # Alignment worker thread
        self._align_thread: Optional[QThread] = None
        self._align_worker: Optional[AlignmentWorker] = None

    def _build_menus(self):
        """Build the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        open_png = QAction("Open PNG...", self)
        open_png.triggered.connect(self.open_png_dialog)
        file_menu.addAction(open_png)

        file_menu.addSeparator()

        save_overlay = QAction("Save Overlay JSON...", self)
        save_overlay.triggered.connect(self.save_overlay_json_dialog)
        file_menu.addAction(save_overlay)

        load_overlay = QAction("Load Overlay JSON...", self)
        load_overlay.triggered.connect(self.load_overlay_json_dialog)
        file_menu.addAction(load_overlay)

        file_menu.addSeparator()

        save_draft = QAction("Save Draft JSON Text...", self)
        save_draft.triggered.connect(self.save_draft_text_dialog)
        file_menu.addAction(save_draft)

        load_draft = QAction("Load Draft JSON Text...", self)
        load_draft.triggered.connect(self.load_draft_text_dialog)
        file_menu.addAction(load_draft)

        file_menu.addSeparator()

        exit_act = QAction("E&xit", self)
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        delete_act = QAction("Delete Selected", self)
        delete_act.setShortcut(QKeySequence(Qt.Key.Key_Delete))
        delete_act.triggered.connect(self.delete_selected_items)
        edit_menu.addAction(delete_act)

        edit_menu.addSeparator()

        settings_act = QAction("Settings...", self)
        settings_act.triggered.connect(self.show_settings_dialog)
        edit_menu.addAction(settings_act)

    def _build_toolbar(self):
        """Build the application toolbar."""
        tb = QToolBar("Tools")
        tb.setIconSize(QSize(18, 18))  # Smaller icons for compact toolbar
        self.addToolBar(tb)

        # Track sticky mode (Ctrl+click on tool makes it stick)
        self._sticky_mode = False

        # Store actions with their icon names for theme switching
        self._icon_actions: Dict[QAction, str] = {}

        def add_mode_action(text: str, mode: str, shortcut: str, icon_name: str):
            act = QAction(text, self)
            act.setCheckable(True)
            act.setShortcut(shortcut)
            # Check for Ctrl modifier when triggered
            act.triggered.connect(lambda checked, m=mode: self._on_mode_action_triggered(m))
            self._icon_actions[act] = icon_name
            tb.addAction(act)
            return act

        # Mode actions
        self.act_select = add_mode_action("Select", Mode.SELECT, "S", "select")
        self.act_rect = add_mode_action("Rect", Mode.RECT, "R", "rect")
        self.act_rrect = add_mode_action("RRect", Mode.ROUNDEDRECT, "U", "rrect")
        self.act_ellipse = add_mode_action("Ellipse", Mode.ELLIPSE, "E", "ellipse")
        self.act_line = add_mode_action("Line", Mode.LINE, "L", "line")
        self.act_text = add_mode_action("Text", Mode.TEXT, "T", "text")
        self.mode_actions = [self.act_select, self.act_rect, self.act_rrect, self.act_ellipse, self.act_line, self.act_text]
        self.act_select.setChecked(True)

        tb.addSeparator()

        # File actions
        open_act = QAction("Open PNG...", self)
        open_act.triggered.connect(self.open_png_dialog)
        self._icon_actions[open_act] = "open"
        tb.addAction(open_act)

        clear_act = QAction("Clear Overlay", self)
        clear_act.triggered.connect(self.clear_overlay)
        self._icon_actions[clear_act] = "clear"
        tb.addAction(clear_act)

        # Toggle PNG visibility
        self.toggle_png_act = QAction("Hide PNG", self)
        self.toggle_png_act.setCheckable(True)
        self.toggle_png_act.setEnabled(False)  # Disabled until PNG is loaded
        self.toggle_png_act.triggered.connect(self._toggle_png_visibility)
        self._icon_actions[self.toggle_png_act] = "hide_png"
        tb.addAction(self.toggle_png_act)

        # Align element to PNG (requires opencv-python)
        if HAS_ALIGNMENT:
            self.align_act = QAction("Align to PNG", self)
            self.align_act.setEnabled(False)  # Disabled until conditions met
            self.align_act.triggered.connect(self.align_selected_to_png)
            self._icon_actions[self.align_act] = "align"
            tb.addAction(self.align_act)

        tb.addSeparator()

        # AI model selection
        self.model_label = QLabel("Model: gemini-2.5-flash-image")
        tb.addWidget(self.model_label)

        self.model_name = "gemini-2.5-flash-image"
        cycle_act = QAction("Cycle Model", self)
        cycle_act.triggered.connect(self.cycle_model)
        self._icon_actions[cycle_act] = "model"
        tb.addAction(cycle_act)

        self.extract_act = QAction("Auto-Extract (Gemini)", self)
        self.extract_act.triggered.connect(self.auto_extract)
        self._icon_actions[self.extract_act] = "extract"
        tb.addAction(self.extract_act)

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
            shortcuts = ["S", "R", "U", "E", "L", "T"]
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

        # Set up callback for rounded rect radius changes
        MetaRoundedRectItem.on_radius_changed = self.props.update_radius_display

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

    def open_png_dialog(self):
        """Open a file dialog to select a PNG image."""
        path, _ = QFileDialog.getOpenFileName(self, "Open PNG", "", "PNG Images (*.png)")
        if path:
            self.load_background_png(path)

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
        for it in list(self.scene.items()):
            if it is self.bg_item or it is self._png_hidden_indicator:
                continue
            if hasattr(it, "meta"):
                self.scene.removeItem(it)
        self.props.set_item(None)

        if self._link_enabled and self._draft_data and isinstance(self._draft_data.get("annotations", None), list):
            self._draft_data["annotations"] = []
            self._rebuild_id_index()
            self._push_draft_data_to_editor(status="Overlay cleared; draft JSON updated.", focus_id=None)

    def delete_selected_items(self):
        """Delete selected items from the scene."""
        items = list(self.scene.selectedItems())
        if not items:
            return

        deleted_ids: List[str] = []
        for it in items:
            if it is self.bg_item:
                continue
            if hasattr(it, "meta"):
                ann_id = it.data(ANN_ID_KEY)
                if isinstance(ann_id, str):
                    deleted_ids.append(ann_id)
                self.scene.removeItem(it)

        self.props.set_item(None)

        if self._link_enabled and deleted_ids and self._draft_data:
            anns = self._draft_data.get("annotations", [])
            if isinstance(anns, list):
                anns = [a for a in anns if not (isinstance(a, dict) and a.get("id") in deleted_ids)]
                self._draft_data["annotations"] = anns
                self._rebuild_id_index()
                self._push_draft_data_to_editor(status=f"Deleted {len(deleted_ids)} item(s); draft JSON updated.", focus_id=None)

        self.statusBar().showMessage("Deleted selected items.")

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Delete:
            self.delete_selected_items()
            return
        super().keyPressEvent(event)

    def show_settings_dialog(self):
        """Show the settings dialog."""
        app = QApplication.instance()
        current_style = getattr(app, "_current_style", DEFAULT_STYLE)

        dialog = SettingsDialog(current_style, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_style = dialog.selected_style()
            if new_style != current_style and new_style in STYLES:
                app.setStyleSheet(STYLES[new_style])
                app._current_style = new_style
                self._update_toolbar_icons(new_style)
                self._update_default_text_color(new_style)
                self._update_editor_colors(new_style)
                self._update_draft_dock_icons(new_style)
                self.statusBar().showMessage(f"Theme changed to: {new_style}")

    def save_draft_text_dialog(self):
        """Save draft JSON text to a file."""
        path, _ = QFileDialog.getSaveFileName(self, "Save Draft JSON Text", "", "JSON (*.json);;Text (*.txt)")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.draft.get_json_text())
            self.statusBar().showMessage(f"Saved draft text: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Save failed", str(e))

    def load_draft_text_dialog(self):
        """Load draft JSON text from a file."""
        path, _ = QFileDialog.getOpenFileName(self, "Load Draft JSON Text", "", "JSON (*.json);;Text (*.txt)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()

            enable = False
            status = ""
            try:
                data = json.loads(text)
                enable = isinstance(data, dict) and isinstance(data.get("annotations", None), list)
                status = "Loaded; click Import to link JSON<->Scene." if enable else "Loaded (not valid draft schema)."
            except Exception:
                enable = False
                status = "Loaded (invalid JSON)."

            self._set_draft_text_programmatically(text, enable_import=enable, status=status, focus_id=None)
            self.statusBar().showMessage(f"Loaded draft text: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Load failed", str(e))

    def save_overlay_json_dialog(self):
        """Save overlay JSON to a file."""
        path, _ = QFileDialog.getSaveFileName(self, "Save Overlay JSON", "", "JSON (*.json)")
        if not path:
            return
        data = self._export_overlay_json()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self.statusBar().showMessage(f"Saved overlay: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Save failed", str(e))

    def load_overlay_json_dialog(self):
        """Load overlay JSON from a file."""
        path, _ = QFileDialog.getOpenFileName(self, "Load Overlay JSON", "", "JSON (*.json)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Load failed", str(e))
            return
        self._apply_overlay_import(data, base_dir=os.path.dirname(path))
        self.statusBar().showMessage(f"Loaded overlay: {path}")

    def _export_overlay_json(self) -> Dict[str, Any]:
        """Export current overlay as JSON."""
        ann: List[Dict[str, Any]] = []
        for it in self.scene.items():
            if hasattr(it, "to_record") and hasattr(it, "meta"):
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
                    if not (isinstance(rec, dict) and "kind" in rec and "geom" in rec):
                        continue
                    geom = rec.get("geom", {}) or {}
                    kind = rec.get("kind", "")

                    norm = False
                    try:
                        if kind in ("rect", "ellipse", "roundedrect") and "x" in geom and "w" in geom:
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
        if self._syncing_from_scene or not self._link_enabled:
            return

        txt = self.draft.get_json_text()
        try:
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

            self._rebuild_id_index()
            self._rebuild_scene_from_draft()

            if changed:
                self._push_draft_data_to_editor(status="Added missing ids; scene updated.", focus_id=None)
            else:
                self.draft.set_status("Scene updated from JSON.")
        except Exception as e:
            self.draft.set_status(f"JSON parse error: {e}")

    def _rebuild_scene_from_draft(self):
        """Rebuild the scene from draft data."""
        if not self._draft_data:
            return

        # Remember selected item ID to restore selection after rebuild
        selected_id = None
        selected_items = self.scene.selectedItems()
        if selected_items:
            selected_id = selected_items[0].data(ANN_ID_KEY)

        self._syncing_from_json = True
        try:
            # Clear property panel before removing items
            self.props.set_item(None)

            for it in list(self.scene.items()):
                if it is self.bg_item or it is self._png_hidden_indicator:
                    continue
                if hasattr(it, "meta"):
                    self.scene.removeItem(it)

            anns = self._draft_data.get("annotations", [])
            if isinstance(anns, list):
                for rec in anns:
                    if isinstance(rec, dict):
                        self._add_item_from_record(rec, on_change=self._on_scene_item_changed)

            # Restore selection if the item still exists
            if selected_id:
                for it in self.scene.items():
                    if hasattr(it, "meta") and it.data(ANN_ID_KEY) == selected_id:
                        it.setSelected(True)
                        self.props.set_item(it)
                        break
        finally:
            self._syncing_from_json = False

    def _on_new_scene_item(self, item: QGraphicsItem):
        """Handle new item added to scene."""
        # Always handle tool mode change after item creation
        self._on_item_created()

        if self._syncing_from_json:
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

        self._push_draft_data_to_editor(status="Draft JSON updated from scene change.", focus_id=ann_id)

        if isinstance(item, MetaTextItem):
            self.draft.jump_to_text_field_for_id(ann_id)
        else:
            self._scroll_draft_to_id_top(ann_id)

        if item in self.scene.selectedItems():
            self.props.set_item(item)

    def _on_z_order_changed(self):
        """Handle z-order changes - update all items in JSON."""
        if self._syncing_from_json or self._draft_data is None:
            return

        if not self._link_enabled:
            return

        anns = self._draft_data.get("annotations", [])
        if not isinstance(anns, list):
            return

        # Update z-index for all annotation items
        for item in self.scene.items():
            if not (hasattr(item, "to_record") and hasattr(item, "ann_id")):
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

    def _push_draft_data_to_editor(self, status: str = "", focus_id: Optional[str] = None):
        """Push draft data to the editor."""
        if self._draft_data is None:
            return
        sorted_data = sort_draft_data(self._draft_data)
        pretty = json.dumps(sorted_data, indent=2)
        self._set_draft_text_programmatically(pretty, enable_import=True, status=status, focus_id=focus_id)

    def _set_draft_text_programmatically(self, text: str, enable_import: bool, status: str = "", focus_id: Optional[str] = None):
        """Set draft text without triggering change handlers."""
        self._syncing_from_scene = True
        try:
            self.draft.text.blockSignals(True)
            self.draft.set_json_text(text, enable_import=enable_import, status=status)
            self.draft.text.blockSignals(False)
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

        if kind == "rect":
            g = rec.get("geom", {})
            it = MetaRectItem(float(g["x"]), float(g["y"]), float(g["w"]), float(g["h"]), ann_id, on_change)
            it.set_meta(meta)
            it.meta.kind = "rect"
            it.apply_style_from_record(rec)
            it._apply_pen_brush()  # Apply pen with dash pattern
            it._update_label_text()
            self.scene.addItem(it)
            if z_index:
                it.setZValue(z_index)

        elif kind == "roundedrect":
            g = rec.get("geom", {})
            radius = float(g.get("radius", 10))
            it = MetaRoundedRectItem(float(g["x"]), float(g["y"]), float(g["w"]), float(g["h"]), radius, ann_id, on_change)
            it.set_meta(meta)
            it.meta.kind = "roundedrect"
            it.apply_style_from_record(rec)
            it._apply_pen_brush()  # Apply pen with dash pattern
            it._update_label_text()
            self.scene.addItem(it)
            if z_index:
                it.setZValue(z_index)

        elif kind == "ellipse":
            g = rec.get("geom", {})
            it = MetaEllipseItem(float(g["x"]), float(g["y"]), float(g["w"]), float(g["h"]), ann_id, on_change)
            it.set_meta(meta)
            it.meta.kind = "ellipse"
            it.apply_style_from_record(rec)
            it._apply_pen_brush()  # Apply pen with dash pattern
            it._update_label_text()
            self.scene.addItem(it)
            if z_index:
                it.setZValue(z_index)

        elif kind == "line":
            g = rec.get("geom", {})
            it = MetaLineItem(float(g["x1"]), float(g["y1"]), float(g["x2"]), float(g["y2"]), ann_id, on_change)
            it.set_meta(meta)
            it.meta.kind = "line"
            it.apply_style_from_record(rec)
            it._apply_pen()  # Apply pen with dash pattern
            it._update_label_text()
            self.scene.addItem(it)
            if z_index:
                it.setZValue(z_index)

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

    # ---- Alignment methods ----

    def _update_align_button_state(self):
        """Update the align button enabled state based on current conditions."""
        if not HAS_ALIGNMENT or self.align_act is None:
            return

        # Condition 1: PNG file is loaded
        if self.bg_path is None:
            self.align_act.setEnabled(False)
            return

        # Condition 2: JSON and canvas are linked
        if not self._link_enabled:
            self.align_act.setEnabled(False)
            return

        # Condition 3: Exactly one alignable item is selected
        items = self.scene.selectedItems()
        if len(items) != 1:
            self.align_act.setEnabled(False)
            return

        if not self._is_alignable_item(items[0]):
            self.align_act.setEnabled(False)
            return

        # All conditions met
        self.align_act.setEnabled(True)

    def _is_alignable_item(self, item) -> bool:
        """Check if an item is alignable (rect, roundedrect, or ellipse)."""
        return isinstance(item, (MetaRectItem, MetaRoundedRectItem, MetaEllipseItem))

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
                "radius": item._radius,
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
            if "radius" in result:
                item._radius = float(result["radius"])
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
        if "radius" in result:
            extras.append(f"radius={result['radius']}")
        if extras:
            msg += f" ({', '.join(extras)})"
        self.statusBar().showMessage(msg)

    def on_align_failed(self, error: str):
        """Handle alignment failure."""
        QMessageBox.critical(self, "Alignment failed", error)
        self.statusBar().showMessage("Alignment failed.")


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLES[DEFAULT_STYLE])
    app._current_style = DEFAULT_STYLE
    w = MainWindow()
    w.resize(1550, 980)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
