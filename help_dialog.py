"""
help_dialog.py

Help system dialogs for PictoSync application.

Provides a tabbed help browser (Quick Start, Drawing Tools, Import & Export,
AI & Editor, Keyboard Shortcuts) and an About dialog.
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
            (0=Quick Start, 1=Drawing Tools, 2=Import & Export,
             3=AI & Editor, 4=Keyboard Shortcuts).
    """

    def __init__(self, parent=None, initial_tab: int = 0):
        super().__init__(parent)
        self.setWindowTitle("PictoSync Help")
        self.setMinimumSize(700, 600)
        self.resize(780, 660)

        layout = QVBoxLayout(self)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_quick_start_tab(), "Quick Start")
        self.tabs.addTab(self._create_tools_tab(), "Drawing Tools")
        self.tabs.addTab(self._create_import_export_tab(), "Import && Export")
        self.tabs.addTab(self._create_ai_editor_tab(), "AI && Editor")
        self.tabs.addTab(self._create_shortcuts_tab(), "Keyboard Shortcuts")
        self.tabs.setCurrentIndex(initial_tab)
        layout.addWidget(self.tabs)

        # Close button
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # -- Tab builders --------------------------------------------------

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

    def _create_import_export_tab(self) -> QTextBrowser:
        """Build the Import & Export reference tab."""
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(_IMPORT_EXPORT_HTML)
        return browser

    def _create_ai_editor_tab(self) -> QTextBrowser:
        """Build the AI & Editor reference tab."""
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(_AI_EDITOR_HTML)
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
        "<p><b>v1.7</b> &mdash; Diagram Annotation &amp; Sync Tool</p>"
        "<p>Create diagram overlays with manual drawing tools, "
        "Gemini AI auto-extraction, and bidirectional JSON synchronization.</p>"
        "<p>Supports PlantUML import, Mermaid import (SVG &amp; source), "
        "C4 pipeline, DSL plugins, and PowerPoint export.</p>"
        "<p>Built with PyQt6 and Google Gemini AI.</p>"
        "<hr>"
        '<p>Source: <a href="https://github.com/pjm4github/pictosync">'
        "github.com/pjm4github/pictosync</a></p>"
        "<p>&copy; 2026 PictoSync Contributors</p>",
    )


# -- Static HTML content ------------------------------------------------

_QUICK_START_HTML = """\
<h2>Quick Start</h2>

<h3>1. Load a Diagram</h3>
<p>Drag-and-drop a file onto the canvas, or use <b>File &rarr; Open Graphic</b>.</p>
<ul>
  <li><b>PNG</b> &mdash; loaded directly as the background image.</li>
  <li><b>PlantUML (.puml)</b> &mdash; rendered to PNG (requires Java + plantuml.jar)
      and parsed into annotation JSON automatically.</li>
  <li><b>Mermaid SVG (.svg)</b> &mdash; pre-rendered SVG loaded and parsed into
      annotations.</li>
  <li><b>Mermaid source (.mmd / .mermaid)</b> &mdash; rendered via Mermaid CLI,
      then parsed. C4 diagrams use a two-step pipeline
      (source &rarr; SVG &rarr; annotations with metadata).</li>
</ul>

<h3>2. Draw Annotations</h3>
<p>Click a drawing tool in the toolbar (or press its shortcut key), then
<b>click and drag</b> on the canvas to create a shape. All 12 primitive tools
are available: Rectangle, Rounded Rect, Ellipse, Line, Text, Hexagon, Cylinder,
Block Arrow, Iso Cube, Polygon, Curve, and Orthocurve.</p>
<p><i>Tip:</i> <b>Ctrl+click</b> a tool to enable <b>sticky mode</b> &mdash;
the tool stays active so you can draw multiple shapes in a row.
Press <b>Esc</b> or right-click to exit sticky mode.</p>

<h3>3. Edit Properties</h3>
<p>Click a shape to select it. The <b>Property Panel</b> below the canvas
shows schema-driven controls for label, tech, note, colors, geometry,
pen style, fill, and arrow settings.</p>

<h3>4. JSON Synchronization</h3>
<p>The <b>Draft JSON</b> editor on the right stays in bidirectional sync with the
canvas. Edit JSON directly, then click <b>Import &amp; Link</b> to apply changes.
The editor highlights the focused annotation and scrolls to keep it visible.</p>
<p>Use <b>Schema Check</b> to validate the JSON structure.</p>

<h3>5. AI Extraction</h3>
<p>With a PNG loaded, click <b>Auto-Extract (Gemini)</b> in the toolbar to
have the AI detect diagram elements automatically. Use <b>Cycle Model</b>
to switch Gemini models. The token counter shows API usage.</p>
<p>Use <b>Focus Align</b> to refine a single selected annotation via AI.</p>
<p><i>Requires the <code>GOOGLE_API_KEY</code> environment variable.</i></p>

<h3>6. Save &amp; Export</h3>
<ul>
  <li><b>File &rarr; Save Project</b> (<b>Ctrl+S</b>) &mdash; save the full
      project (image + annotations) for later reload.</li>
  <li><b>File &rarr; Open Project</b> (<b>Ctrl+O</b>) &mdash; reload a saved
      project.</li>
  <li><b>File &rarr; Export PowerPoint</b> &mdash; export annotations as native
      PowerPoint shapes in a <code>.pptx</code> file.</li>
  <li><b>File &rarr; Save Overlay JSON</b> / <b>Save Draft JSON Text</b>
      &mdash; save annotations as portable JSON.</li>
</ul>

<hr>
<p>Latest source &amp; documentation:
<a href="https://github.com/pjm4github/pictosync">
github.com/pjm4github/pictosync</a></p>
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
  <tr><td><b>Iso Cube</b></td><td>I</td>
      <td>Draw isometric cube shapes with adjustable top/side handles.
          Supports semi-transparent fills.</td></tr>
  <tr><td><b>Polygon</b></td><td>P</td>
      <td>Draw polygon shapes. Click to add vertices;
          double-click or press Enter to finish.</td></tr>
  <tr><td><b>Curve</b></td><td>V</td>
      <td>Draw bezier curves. Click to add control points;
          double-click or press Enter to finish. Drag handles to reshape.</td></tr>
  <tr><td><b>Orthocurve</b></td><td><i>dropdown</i></td>
      <td>Draw orthogonal (right-angle) curves via the Curve tool dropdown.
          Points snap to horizontal/vertical segments.</td></tr>
</table>

<h3>Groups</h3>
<ul>
  <li><b>Group</b> (Ctrl+G) &mdash; combine selected annotations into a group.
      Moving or resizing the group affects all members.</li>
  <li><b>Ungroup</b> (Ctrl+Shift+G) &mdash; dissolve a group back into
      individual items.</li>
  <li>Groups support nested hierarchy and resize all children proportionally.</li>
</ul>

<h3>Undo / Redo</h3>
<p>Undo (<b>Ctrl+Z</b>) and Redo (<b>Ctrl+Y</b>) track moves, resizes,
text changes, and property edits. History is maintained per session.</p>

<h3>Z-Order &amp; Auto-Stacking</h3>
<ul>
  <li><b>Bring to Front / Send to Back</b> &mdash; adjust the stacking
      order of overlapping annotations.</li>
  <li>Auto-stacking assigns z-order based on annotation area
      (larger shapes behind smaller ones).</li>
</ul>

<h3>Other Toolbar Actions</h3>
<table cellpadding="6" cellspacing="0" border="1"
       style="border-collapse:collapse; width:100%;">
  <tr style="background:#f0f0f0;">
    <th>Action</th><th>Description</th>
  </tr>
  <tr><td><b>Open Graphic</b></td>
      <td>Load a PNG, PlantUML, Mermaid SVG, or Mermaid source file.</td></tr>
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

_IMPORT_EXPORT_HTML = """\
<h2>Import &amp; Export</h2>

<h3>PlantUML Import</h3>
<ul>
  <li>Drop a <code>.puml</code> file or use <b>File &rarr; Open Graphic</b>.</li>
  <li>PictoSync renders the file to PNG via Java + plantuml.jar, then parses
      the SVG output to extract shape positions, labels, and connectors.</li>
  <li>Supports sequence, activity, state, class, component, and description
      diagrams.</li>
  <li>Curve connectors and link styles are preserved.</li>
  <li>Diagram name is validated and used for the project title.</li>
</ul>

<h3>Mermaid SVG Import</h3>
<ul>
  <li>Drop a pre-rendered <b>.svg</b> file exported from Mermaid.</li>
  <li>PictoSync parses SVG elements (rects, paths, text) into annotations.</li>
  <li>Works with flowcharts, sequence diagrams, and other Mermaid SVG output.</li>
</ul>

<h3>Mermaid Source Import</h3>
<ul>
  <li>Drop a <code>.mmd</code> or <code>.mermaid</code> source file.</li>
  <li>PictoSync renders it via the Mermaid CLI (<code>mmdc</code>), then
      parses the resulting SVG.</li>
  <li><b>Flowchart parser</b> extracts nodes, edges, and labels.</li>
  <li><b>C4 two-step pipeline:</b> source is rendered to SVG, then metadata
      (kind, label, tech, description) is extracted from both the source text
      and SVG positions. C4 layout settings control spacing and grouping.</li>
  <li>Supports C4 Context, Container, Component, and Deployment diagrams.</li>
</ul>

<h3>DSL Plugin System</h3>
<ul>
  <li>Domain-specific tools live in the <code>domains/</code> folder.</li>
  <li>Each domain has a <code>tools.json</code> defining custom shape templates,
      icons, and default properties.</li>
  <li>The <b>Domain</b> menu and left toolbar load available domain plugins.</li>
  <li>Example: <code>domains/ns3/</code> provides NS3 network simulation shapes.</li>
</ul>

<h3>OpenCV Alignment</h3>
<ul>
  <li><b>Align to PNG</b> uses OpenCV to detect shapes, lines, arrowheads,
      and dashed lines in the background image.</li>
  <li>Text and color matching refine the alignment.</li>
  <li>Requires the <code>opencv-python</code> package.</li>
</ul>

<h3>PowerPoint Export</h3>
<ul>
  <li><b>File &rarr; Export PowerPoint</b> creates a <code>.pptx</code> file
      with native PowerPoint shapes.</li>
  <li>Exports all shape types including rectangles, rounded rects, ellipses,
      hexagons, cylinders, block arrows, iso cubes, and polygons.</li>
  <li>Curves use native PowerPoint bezier freeform shapes.</li>
  <li>Arrowheads, line styles, and semi-transparent fills are preserved.</li>
  <li>Groups are flattened for maximum compatibility.</li>
  <li>Export directory defaults to the source file location.</li>
</ul>
"""

_AI_EDITOR_HTML = """\
<h2>AI &amp; Editor</h2>

<h3>AI Integration</h3>
<ul>
  <li><b>Auto-Extract (Gemini)</b> sends the loaded PNG to Google Gemini and
      receives structured annotation JSON.</li>
  <li><b>Cycle Model</b> switches between available Gemini models
      (e.g., Gemini 2.0 Flash, Gemini 1.5 Pro).</li>
  <li><b>Focus Align</b> re-extracts a single selected annotation for
      fine-tuning its position and properties.</li>
  <li>The <b>token counter</b> in the status bar shows cumulative API usage
      for the session.</li>
  <li>Requires the <code>GOOGLE_API_KEY</code> environment variable.</li>
</ul>

<h3>Bidirectional Synchronization</h3>
<ul>
  <li>The <b>Draft JSON</b> editor and canvas stay in bidirectional sync.</li>
  <li>Moving or resizing shapes on the canvas updates the JSON immediately.</li>
  <li>Editing JSON and clicking <b>Import &amp; Link</b> updates the canvas.</li>
  <li><b>Scroll lock:</b> selecting an annotation on the canvas scrolls the
      JSON editor to that annotation, and vice versa.</li>
  <li><b>Save / Open Project</b> (Ctrl+S / Ctrl+O) persists the full state
      including image, annotations, and editor text.</li>
</ul>

<h3>JSON Editor Features</h3>
<ul>
  <li><b>Syntax highlighting</b> with color-coded keys, values, and
      structure.</li>
  <li><b>Line numbers</b> and <b>code folding</b> for navigating large
      documents.</li>
  <li><b>Focus mode:</b> the editor highlights and scrolls to the currently
      selected annotation's JSON block.</li>
  <li><b>Schema check:</b> validates the JSON structure against the
      annotation schema and reports errors.</li>
  <li><b>Ghost fields:</b> shows available but unset fields in the property
      panel for easy discovery.</li>
  <li><b>Smart scrolling:</b> keeps the focused annotation visible near the
      top of the editor viewport.</li>
  <li><b>Gutter bar:</b> visual indicator showing annotation boundaries in
      the editor margin.</li>
</ul>

<h3>Property Panel</h3>
<ul>
  <li>Context-sensitive controls appear based on the selected shape type.</li>
  <li>Schema-driven: available fields adjust automatically for each annotation
      kind.</li>
  <li>Edits in the property panel auto-compile and sync to both the canvas
      and JSON editor.</li>
</ul>

<h3>User Interface</h3>
<ul>
  <li><b>Dynamic title bar</b> shows the current project name and file path.</li>
  <li><b>Themes:</b> light and dark theme support.</li>
  <li><b>Custom icons</b> for toolbar tools and domain plugins.</li>
  <li><b>Hide / Show PNG</b> toggles the background image to inspect
      annotations in isolation.</li>
</ul>
"""

_SHORTCUTS_HTML = """\
<h2>Keyboard Shortcuts</h2>

<table cellpadding="6" cellspacing="0" border="1"
       style="border-collapse:collapse; width:100%;">
  <tr style="background:#f0f0f0;">
    <th>Category</th><th>Shortcut</th><th>Action</th>
  </tr>
  <tr><td rowspan="12"><b>Drawing Tools</b></td>
      <td><code>S</code></td><td>Select mode</td></tr>
  <tr><td><code>R</code></td><td>Rectangle tool</td></tr>
  <tr><td><code>U</code></td><td>Rounded rectangle tool</td></tr>
  <tr><td><code>E</code></td><td>Ellipse tool</td></tr>
  <tr><td><code>L</code></td><td>Line tool</td></tr>
  <tr><td><code>T</code></td><td>Text tool</td></tr>
  <tr><td><code>H</code></td><td>Hexagon tool</td></tr>
  <tr><td><code>Y</code></td><td>Cylinder tool</td></tr>
  <tr><td><code>A</code></td><td>Block arrow tool</td></tr>
  <tr><td><code>I</code></td><td>Iso Cube tool</td></tr>
  <tr><td><code>P</code></td><td>Polygon tool</td></tr>
  <tr><td><code>V</code></td><td>Curve tool</td></tr>

  <tr><td rowspan="3"><b>Editing</b></td>
      <td><code>Delete</code></td><td>Delete selected items</td></tr>
  <tr><td><code>Ctrl+Z</code></td><td>Undo</td></tr>
  <tr><td><code>Ctrl+Y</code></td><td>Redo</td></tr>

  <tr><td rowspan="2"><b>Groups</b></td>
      <td><code>Ctrl+G</code></td><td>Group selected items</td></tr>
  <tr><td><code>Ctrl+Shift+G</code></td><td>Ungroup</td></tr>

  <tr><td rowspan="2"><b>File</b></td>
      <td><code>Ctrl+S</code></td><td>Save project</td></tr>
  <tr><td><code>Ctrl+O</code></td><td>Open project</td></tr>

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
