"""
help_dialog.py

Help system dialogs for PictoSync application.

Provides a tabbed help browser (Quick Start, Drawing Tools, Keyboard Shortcuts)
and an About dialog.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QMessageBox,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
)


class HelpDialog(QDialog):
    """Tabbed help dialog for PictoSync.

    Args:
        parent: Parent widget.
        initial_tab: Index of the tab to display on open
            (0=Quick Start, 1=Drawing Tools, 2=Keyboard Shortcuts).
    """

    def __init__(self, parent=None, initial_tab: int = 0):
        super().__init__(parent)
        self.setWindowTitle("PictoSync Help")
        self.setMinimumSize(650, 550)
        self.resize(720, 600)

        layout = QVBoxLayout(self)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_quick_start_tab(), "Quick Start")
        self.tabs.addTab(self._create_tools_tab(), "Drawing Tools")
        self.tabs.addTab(self._create_shortcuts_tab(), "Keyboard Shortcuts")
        self.tabs.setCurrentIndex(initial_tab)
        layout.addWidget(self.tabs)

        # Close button
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # ── Tab builders ──────────────────────────────────

    def _create_quick_start_tab(self) -> QTextBrowser:
        """Build the Quick Start guide tab."""
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(_QUICK_START_HTML)
        return browser

    def _create_tools_tab(self) -> QTextBrowser:
        """Build the Drawing Tools reference tab."""
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(_TOOLS_HTML)
        return browser

    def _create_shortcuts_tab(self) -> QTextBrowser:
        """Build the Keyboard Shortcuts reference tab."""
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(_SHORTCUTS_HTML)
        return browser


def show_about_dialog(parent=None):
    """Show the About PictoSync dialog.

    Args:
        parent: Parent widget for the message box.
    """
    QMessageBox.about(
        parent,
        "About PictoSync",
        "<h2>PictoSync</h2>"
        "<p><b>v1.1</b> &mdash; Diagram Annotation &amp; Sync Tool</p>"
        "<p>Create diagram overlays with manual drawing tools, "
        "Gemini AI auto-extraction, and bidirectional JSON synchronization.</p>"
        "<p>Built with PyQt6 and Google Gemini AI.</p>"
        "<hr>"
        "<p>&copy; 2025 PictoSync Contributors</p>",
    )


# ── Static HTML content ──────────────────────────────

_QUICK_START_HTML = """\
<h2>Quick Start</h2>

<h3>1. Load a Background Image</h3>
<p>Drag-and-drop a <b>PNG</b> or <b>PlantUML (.puml)</b> file onto the canvas,
or use <b>File &rarr; Open Graphic</b>.</p>
<ul>
  <li><b>PNG</b> files are loaded directly as the background.</li>
  <li><b>PUML</b> files are rendered to PNG (requires Java + plantuml.jar)
      and parsed into annotation JSON automatically.</li>
</ul>

<h3>2. Draw Annotations</h3>
<p>Click a drawing tool in the toolbar (or press its shortcut key), then
<b>click and drag</b> on the canvas to create a shape.</p>
<p><i>Tip:</i> <b>Ctrl+click</b> a tool to enable <b>sticky mode</b> &mdash;
the tool stays active so you can draw multiple shapes in a row.
Press <b>Esc</b> or right-click to exit sticky mode.</p>

<h3>3. Edit Properties</h3>
<p>Click a shape to select it. The <b>Property Panel</b> below the canvas
shows editable fields for label, tech, note, colors, and geometry.</p>

<h3>4. JSON Synchronization</h3>
<p>The <b>Draft JSON</b> editor on the right stays in sync with the canvas.
Edits in either direction are reflected immediately after you click
<b>Import &amp; Link</b>.</p>

<h3>5. AI Extraction</h3>
<p>With a PNG loaded, click <b>Auto-Extract (Gemini)</b> in the toolbar to
have the AI detect diagram elements automatically.</p>
<p><i>Requires the <code>GOOGLE_API_KEY</code> environment variable.</i></p>

<h3>6. Save &amp; Export</h3>
<ul>
  <li><b>File &rarr; Save Overlay JSON</b> &mdash; save annotations as a
      portable JSON file.</li>
  <li><b>File &rarr; Save Draft JSON Text</b> &mdash; save the raw editor
      text.</li>
  <li><b>File &rarr; Export PowerPoint</b> &mdash; export annotations to a
      <code>.pptx</code> file.</li>
</ul>
"""

_TOOLS_HTML = """\
<h2>Drawing Tools</h2>

<table cellpadding="6" cellspacing="0" border="1"
       style="border-collapse:collapse; width:100%;">
  <tr style="background:#f0f0f0;">
    <th>Tool</th><th>Key</th><th>Description</th>
  </tr>
  <tr><td><b>Select</b></td><td>S</td>
      <td>Select, move, and resize annotations. Drag handles to resize.</td></tr>
  <tr><td><b>Rectangle</b></td><td>R</td>
      <td>Draw rectangular annotation boxes.</td></tr>
  <tr><td><b>Rounded Rect</b></td><td>U</td>
      <td>Draw rounded-corner rectangles.</td></tr>
  <tr><td><b>Ellipse</b></td><td>E</td>
      <td>Draw elliptical or circular annotations.</td></tr>
  <tr><td><b>Line</b></td><td>L</td>
      <td>Draw lines and connectors. Supports arrowheads.</td></tr>
  <tr><td><b>Text</b></td><td>T</td>
      <td>Place standalone text annotations. Double-click to edit.</td></tr>
  <tr><td><b>Hexagon</b></td><td>H</td>
      <td>Draw hexagonal shapes.</td></tr>
  <tr><td><b>Cylinder</b></td><td>Y</td>
      <td>Draw cylinder shapes (databases / storage).</td></tr>
  <tr><td><b>Block Arrow</b></td><td>A</td>
      <td>Draw block arrow shapes for directional flow.</td></tr>
</table>

<h3>Other Toolbar Actions</h3>
<table cellpadding="6" cellspacing="0" border="1"
       style="border-collapse:collapse; width:100%;">
  <tr style="background:#f0f0f0;">
    <th>Action</th><th>Description</th>
  </tr>
  <tr><td><b>Open Graphic</b></td>
      <td>Load a PNG image or PlantUML file as background.</td></tr>
  <tr><td><b>Clear Overlay</b></td>
      <td>Remove all annotations from the canvas.</td></tr>
  <tr><td><b>Hide / Show PNG</b></td>
      <td>Toggle background image visibility.</td></tr>
  <tr><td><b>Align to PNG</b></td>
      <td>Snap selected shape to match the background image
          (requires opencv-python).</td></tr>
  <tr><td><b>Align Line to PNG</b></td>
      <td>Snap selected line to match the background image.</td></tr>
  <tr><td><b>Cycle Model</b></td>
      <td>Switch between available Gemini AI models.</td></tr>
  <tr><td><b>Auto-Extract (Gemini)</b></td>
      <td>Run AI extraction to detect diagram elements from the loaded
          image.</td></tr>
  <tr><td><b>Undo / Redo</b></td>
      <td>Step through the edit history.</td></tr>
  <tr><td><b>Zoom Region</b></td>
      <td>Drag a rectangle to zoom into that area.</td></tr>
  <tr><td><b>Zoom Fit</b></td>
      <td>Fit the entire scene into the view.</td></tr>
</table>
"""

_SHORTCUTS_HTML = """\
<h2>Keyboard Shortcuts</h2>

<table cellpadding="6" cellspacing="0" border="1"
       style="border-collapse:collapse; width:100%;">
  <tr style="background:#f0f0f0;">
    <th>Category</th><th>Shortcut</th><th>Action</th>
  </tr>
  <tr><td rowspan="9"><b>Drawing Tools</b></td>
      <td><code>S</code></td><td>Select mode</td></tr>
  <tr><td><code>R</code></td><td>Rectangle tool</td></tr>
  <tr><td><code>U</code></td><td>Rounded rectangle tool</td></tr>
  <tr><td><code>E</code></td><td>Ellipse tool</td></tr>
  <tr><td><code>L</code></td><td>Line tool</td></tr>
  <tr><td><code>T</code></td><td>Text tool</td></tr>
  <tr><td><code>H</code></td><td>Hexagon tool</td></tr>
  <tr><td><code>Y</code></td><td>Cylinder tool</td></tr>
  <tr><td><code>A</code></td><td>Block arrow tool</td></tr>

  <tr><td rowspan="3"><b>Editing</b></td>
      <td><code>Delete</code></td><td>Delete selected items</td></tr>
  <tr><td><code>Ctrl+Z</code></td><td>Undo</td></tr>
  <tr><td><code>Ctrl+Y</code></td><td>Redo</td></tr>

  <tr><td rowspan="5"><b>View</b></td>
      <td><code>F</code></td><td>Zoom to fit</td></tr>
  <tr><td><code>1</code></td><td>Zoom 100%</td></tr>
  <tr><td><code>Z</code></td><td>Toggle zoom-to-region mode</td></tr>
  <tr><td><code>Ctrl++</code></td><td>Zoom in</td></tr>
  <tr><td><code>Ctrl+-</code></td><td>Zoom out</td></tr>

  <tr><td><b>Help</b></td>
      <td><code>F1</code></td><td>Open this Help dialog</td></tr>
</table>

<br>
<p><b>Tip:</b> <code>Ctrl+click</code> a drawing tool to toggle
<b>sticky mode</b> &mdash; the tool stays active after each shape is drawn.
Press <b>Esc</b> or right-click to return to Select mode.</p>
"""
