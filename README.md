<p align="center">
  <img src="assets/banner.svg" alt="PictoSync Banner" width="800"/>
</p>

# PictoSync

**v1.5** | PNG Image Canvas Tool for Object Synchronization

Diagram annotation tool with AI-powered extraction and bidirectional sync.

## Abstract

PictoSync is a PyQt6 desktop application for creating and managing diagram annotations. It combines manual drawing tools with Google Gemini AI (see note below) to automatically extract structural elements from architecture diagrams (such as C4 models). The application maintains bidirectional synchronization between a visual canvas and JSON representation, enabling a human-in-the-loop workflow where AI extracts, humans refine, and changes sync back seamlessly.

**Note**: If you don't have a Google Gemini API key, or dont want to send your picture to Google for scanning, you can still place a graphic on the picture and then use the local optimizer to match the grahpics to the PNG.

## Features
**For a comparison to other tools and their features see this file:  [Round Tripping PNG Tools](png_json_comparison.md)**

### Drawing & Annotation
- **Manual Drawing Tools**: Rectangle, rounded rectangle, ellipse, hexagon, cylinder, block arrow, polygon, curve, line, and text annotations
- **Curve Tool**: Click-click placement of SVG path-like curves with node editing; supports cubic bezier (`C`), quadratic bezier (`Q`), arc (`A`), and line (`L`) segments; right-click nodes to change type; arrowhead support (none, start, end, both)
- **Polygon Tool**: Multi-click vertex placement with right-click to close; double-click to enter vertex editing mode with draggable control knobs; right-click vertices to delete, right-click edges to add vertices
- **Text Labels**: All shapes support label, tech, and note text with customizable formatting
- **Text Alignment**: Vertical alignment (top/middle/bottom) and line spacing controls
- **Pen Styles**: Solid or dashed lines with configurable dash pattern (length, solid percent)
- **Z-Order Control**: Right-click context menu to "Bring to Front" or "Send to Back"
- **Auto-Stacking**: New shapes automatically appear on top of existing items

### Groups
- **Group/Ungroup**: Select multiple items and group them; ungroup to restore individual items
- **Group Resize**: 8 handles (4 corners + 4 sides) with proportional scaling of all children
- **Nested Hierarchy**: PlantUML cluster/entity parent-child relationships parsed into group annotations with recursive children

### Undo/Redo
- **Move**: Single and multi-select item movement
- **Resize**: All shape types including proportional group resize
- **Text Editing**: Full text edit history
- **Properties**: All property panel changes (colors, metadata, line styles, adjustments)

### Element Alignment (OpenCV)
- **Shape Alignment**: Snap rectangles, rounded rectangles, and ellipses to match PNG visuals
- **Line Detection**: Detect and align line elements including endpoints, angle, and length
- **Arrowhead Detection**: Automatically detects triangular arrowheads and extends line endpoints
- **Dashed Line Support**: Merges collinear segments to handle dashed/dotted lines
- **Text Matching**: Uses label/note text to locate lines in the image
- **Color Matching**: HSV-based color detection matches pen colors in the PNG

### PlantUML Import
- **PlantUML Rendering**: Import `.puml` files directly via drag-and-drop or File > Open
- **SVG Position Extraction**: Parses PlantUML-rendered SVG for pixel-accurate element positioning
- **Curve Connector Parsing**: SVG `<path>` elements with cubic bezier curves are parsed into curve annotations preserving actual connector geometry (instead of simple center-to-center lines)
- **Dedicated Description Diagram Parser**: Component, deployment, use-case, and architecture diagrams parsed directly from SVG structure (entities, clusters, links) for reliable extraction
- **Bracket Notation Support**: Captures `[Component Name] as alias` syntax that text-regex extraction would miss
- **Cluster/Package Support**: PlantUML packages render as polygon shapes with SVG path vertices; rect-vs-path detection correctly handles decorative tab overlays
- **Activity Diagram Support**: Parses activity diagram SVGs with partitions, activities, flow lines, and start/end nodes
- **Link Style Extraction**: Stroke colors and dash patterns from SVG applied to connectors
- **Diagram Name Validation**: Warns about Windows-illegal characters in `@startuml` names that would cause silent rendering failures

### PowerPoint Export
- **Slide Export**: Export annotations as native PowerPoint shapes via File > Export PPTX
- **Shape Support**: Rectangles, rounded rectangles, ellipses, hexagons, cylinders, block arrows, polygons, curves, lines, and text
- **Native Bezier Curves**: Curves export as OOXML `a:cubicBezTo` and `a:quadBezTo` elements preserving control points
- **Curve Labels**: Label/tech/note text placed at the parametric midpoint (t=0.5) of the actual curve path
- **Arrowheads**: Line and curve arrowheads exported via `tailEnd`/`headEnd` attributes
- **Fill & Text Colors**: Fill colors, border colors, text colors, font sizes, and alignment
- **Polygon Freeforms**: Polygon shapes exported as PowerPoint freeform shapes
- **Group Flattening**: Groups recursively flattened for export
- **Export Directory Setting**: Option to default PPTX export to the source file's directory

### AI Integration
- **AI Extraction**: Automatic diagram element detection using Google Gemini models
- **Smart Defaults**: Extracted elements automatically get formatting defaults
- **Markdown Handling**: Automatically strips markdown fences from AI responses

### Synchronization
- **Bidirectional Sync**: Real-time synchronization between canvas elements and JSON editor
- **Live Drag Updates**: Geometry values update in the JSON editor in real-time during drag without scroll jumping
- **Scroll Lock During Interaction**: Editor scroll position is frozen from mouse-down to mouse-up, then scrolls to the final position on release
- **Human-in-the-Loop**: AI extracts → Human edits → Syncs back (round-trip workflow)
- **Project Save/Load**: Save and load projects (annotations + PNG) to a configurable workspace directory

### JSON Editor
- **Syntax Highlighting**: Full JSON syntax highlighting
- **Line Numbers**: Theme-aware line number gutter with selection highlighting
- **Code Folding**: Collapse/expand JSON objects and arrays
- **Focus Mode**: Toggle to show only the selected annotation (lamp icon)
- **Smart Scrolling**: Clicking canvas items scrolls editor to the annotation's opening brace on mouse release
- **Gutter Highlight Bar**: Colored bar in gutter marks the full scope of the selected annotation
- **Consistent Precision**: Geometry values use 2 decimal places, style values use 1 decimal place

### Property Panel
- **Context-Sensitive**: Shows relevant controls based on selected item type
- **Schema-Driven Adjust Controls**: Adjust spinboxes (radius, indent, cap, shaft, head) derive labels, suffixes, and ranges from `annotation_schema.json`
- **Qt Designer UI**: Built with Qt Designer for consistent layout
- **Auto-Compile**: UI files are automatically compiled on startup if modified
- **Text Formatting**: Font size, alignment, vertical position, and spacing controls

### User Interface
- **Hide/Show PNG**: Toggle background image visibility for cleaner annotation view
- **Handle-Enclosed Selection**: Rubber band selection respects individual item handles with live preview
- **Multiple Themes**: 7 built-in themes (Foundation Dark, Bulma Light, Bauhaus, Neumorphism, Materialize, Tailwind, Bootstrap)
- **Styled Splitters**: High-contrast, theme-aware resize handles
- **Custom Icons**: Theme-matched SVG icons for all tools and actions

## Installation

```bash
# Clone the repository
git clone https://github.com/pjm4github/pictosync.git
cd pictosync

# Install dependencies
pip install -r requirements.txt
```

## Requirements

- Python 3.8+
- PyQt6
- Pillow
- google-genai
- opencv-python (for element alignment)
- python-pptx (for PowerPoint export)
- pytest (for running tests)

Set your Google API key for AI extraction:
```bash
export GOOGLE_API_KEY=your_api_key_here
```

## Usage

```bash
python main.py
```

## Testing

PictoSync includes an automated test suite under `tests/` using pytest. Tests require a GUI environment (not headless).

```bash
# Run all tests
python -m pytest tests/ -v

# Run a specific test file
python -m pytest tests/test_scroll_preservation.py -v
```

### Test Coverage

| Test Module | What It Covers |
|-------------|---------------|
| `test_adjust_roundtrip.py` | Schema-driven adjust control labels, suffixes, ranges; adjust value round-trips through panel/JSON/canvas; no duplicate IDs after adjust changes |
| `test_scroll_preservation.py` | Editor scroll stays frozen during canvas drag; JSON geometry values update live during drag; PUML import produces correct annotations with full meta fields; re-import works after drag |
| `test_ungroup_drag.py` | Ungroup preserves index integrity; no duplicate IDs after ungroup; children retain `on_change` callbacks; geometry updates during drag after ungroup; move-then-ungroup-then-drag scenario |
| `test_flow_ungroup.py` | Move-then-ungroup-then-drag on flow/activity diagrams; index integrity and duplicate ID checks; child callback and geometry verification |

### Basic Workflow
1. **Load an image**: Drag and drop a PNG/PUML file or use File > Open
2. **Draw annotations**: Select a tool (R=Rect, U=RoundedRect, E=Ellipse, L=Line, V=Curve, T=Text, H=Hexagon, Y=Cylinder, A=Block Arrow, P=Polygon, S=Select)
3. **AI extraction**: Click "Auto-Extract (Gemini)" to detect diagram elements
4. **Edit JSON**: Modify annotations in the Draft JSON panel
5. **Link**: Click "Import & Link" to enable bidirectional JSON ↔ Canvas sync
6. **Save**: Save your project via File > Save Project (Ctrl+S)
7. **Export**: Export to PowerPoint via File > Export PPTX

### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| S | Select mode |
| R | Rectangle tool |
| U | Rounded rectangle tool |
| E | Ellipse tool |
| L | Line tool |
| V | Curve tool |
| T | Text tool |
| H | Hexagon tool |
| Y | Cylinder tool |
| A | Block arrow tool |
| P | Polygon tool |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Ctrl+S | Save project |
| Ctrl+O | Open project |
| Delete | Delete selected item |

### Tips
- **Z-Order**: Right-click a selected shape for "Bring to Front" / "Send to Back"
- **Curve Editing**: Double-click a curve to enter node editing mode; right-click a node to change its type (Line, Cubic, Quadratic, Arc)
- **Focus Mode**: Click the lamp icon to collapse all annotations except the selected one
- **Hide PNG**: Toggle background visibility when annotations obscure the image
- **Themes**: Access Settings to switch between 7 visual themes
- **Text Formatting**: Use the property panel to adjust vertical alignment and spacing
- **Element Alignment**: Select a shape or line and use "Align to PNG" to snap it to the visual
- **Group Resize**: Select a group and drag corner/side handles to proportionally resize all children

## Project Structure

```
pictosync/
├── main.py              # Application entry point, MainWindow
├── models.py            # Data models, AnnotationMeta, DrawMode, normalize_meta()
├── styles.py            # Theme stylesheets, dash patterns, color configs
├── utils.py             # JSON parsing, coordinate scaling, markdown handling
├── settings.py          # Application settings (workspace, export options)
├── undo_commands.py     # Undo/redo commands for all canvas operations
├── canvas/              # Graphics layer
│   ├── items.py         # Annotation items (Rect, Ellipse, Hexagon, Cylinder, BlockArrow, Polygon, Curve, Line, Text, Group)
│   ├── mixins.py        # LinkedMixin, MetaMixin for shared behavior
│   ├── scene.py         # AnnotatorScene (drawing, context menu, z-order)
│   └── view.py          # AnnotatorView (zoom, pan, drag-drop, rubber band selection)
├── editor/              # JSON editor
│   ├── code_editor.py   # JsonCodeEditor with folding and focus mode
│   ├── draft_dock.py    # DraftDock widget with scroll-to-id and scroll lock
│   └── highlighter.py   # JSON syntax highlighting
├── properties/          # Property panel
│   ├── dock.py          # PropertyPanel controller (schema-driven adjust controls)
│   ├── properties_panel.ui   # Qt Designer UI file
│   └── properties_ui.py      # Auto-generated from .ui file
├── schemas/             # JSON schemas
│   └── annotation_schema.json  # Annotation format specification (including curve, group)
├── plantuml/            # PlantUML import
│   ├── renderer.py      # PlantUML to PNG/SVG rendering
│   └── parser.py        # PUML text parsing, SVG position/path extraction, description diagram parser
├── gemini/              # AI integration
│   └── worker.py        # Threaded Gemini API worker
├── pptx_export.py       # PowerPoint slide export (native bezier curves, arrowheads, labels)
├── alignment/           # OpenCV alignment
│   ├── optimizer.py     # Shape and line alignment algorithms
│   └── worker.py        # Threaded alignment workers
├── icons/               # Theme-aware SVG icons
│   ├── generate_icons.py    # Icon generation script
│   └── [Theme folders]      # Icons for each theme
├── tests/               # Automated test suite (pytest)
│   ├── test_adjust_roundtrip.py     # Adjust control schema validation
│   ├── test_scroll_preservation.py  # Scroll lock & live update tests
│   ├── test_ungroup_drag.py         # Ungroup + drag correctness
│   └── test_flow_ungroup.py         # Flow diagram ungroup + drag
├── test_data/           # Test fixture data
│   └── PUML/            # Anonymized PlantUML test diagrams
└── requirements.txt
```

## Schema

Annotations follow a JSON schema with support for:
- **Geometry**: rect, roundedrect, ellipse, hexagon, cylinder, blockarrow, polygon, curve, line, text, group
- **Curve Geometry**: Bounding box (`x, y, w, h`) plus `nodes` array with SVG path commands (`M`, `L`, `C`, `Q`, `A`, `Z`) and normalized 0–1 control point coordinates
- **Group**: Recursive `children` array containing nested annotations
- **Meta**: label, tech, note with alignment and sizing; `ui_label` and `ui_suffix` for schema-driven property controls
- **Style**: pen (color, width, dash), brush (fill), text (color, size), arrow (none, start, end, both)
- **Text Layout**: vertical alignment, spacing, bounding box dimensions

See `schemas/annotation_schema.json` for the full specification.

## Version History

### v1.5 (2026-02-18)
- Curve drawing tool with SVG path-like node editing (cubic bezier, quadratic bezier, arc, line segments)
- PlantUML SVG path parsing preserves actual connector geometry as curve annotations
- Dedicated description diagram parser for component, deployment, use-case, and architecture diagrams
- Native OOXML bezier export to PowerPoint (`a:cubicBezTo`, `a:quadBezTo`) with arrowheads and midpoint labels
- PPTX export-to-source-dir setting
- Cluster rect-vs-path parsing fix for decorative tab overlays
- Diagram name validation warns about illegal characters in `@startuml` names
- Comprehensive undo/redo for move, resize, text editing, and property changes
- Group resize with proportional child scaling via 8 handles
- Group kind support in schema, validation, export, and utilities
- Handle-enclosed rubber band selection with live preview
- Schema-driven adjust controls (labels, suffixes, ranges from `annotation_schema.json`)
- Fixed duplicate annotations when ungrouping a moved group
- Expanded test suite: `test_adjust_roundtrip.py`, `test_ungroup_drag.py`, `test_flow_ungroup.py`
- Renamed test data directory to `test_data/` with anonymized PUML fixtures

### v1.4 (2026-02-16)
- Standardized numeric precision: geometry values at 2 decimal places, style values at 1 decimal place
- Editor scroll position frozen during canvas drag/resize (mouse-down to mouse-up)
- Live JSON geometry updates during drag without scroll jumping
- Selection scroll deferred to mouse release for smooth click-and-drag
- Added automated test suite (`tests/`) with pytest
- Added pytest to requirements

### v1.3 (2026-02-15)
- Activity diagram SVG parser with partition groups, flow lines, ellipses, and polygons
- Nested group hierarchy from PlantUML cluster/entity parent-child relationships
- PowerPoint export: fill colors, border colors, text colors, font sizes, and alignment
- PowerPoint export: polygon freeform shapes, line labels, vertical text alignment
- Fixed PPTX color format handling (`#RRGGBBAA` instead of `#AARRGGBB`)
- Fixed PPTX text styling to reliably override PowerPoint theme defaults
- Fixed PPTX vertical alignment using `vertical_anchor` (python-pptx 1.0.2 API)
- Fixed crash when clearing grouped items from canvas

### v1.2 (2026-02-12)
- Polygon shape tool with multi-click vertex drawing and vertex editing mode
- SVG-based position extraction for PlantUML import (pixel-accurate placement)
- PlantUML packages/clusters render as polygons with SVG path vertices
- Link style extraction (stroke colors, dash patterns) from PlantUML SVG
- Fixed editor scroll-to-selection for documents with wrapped lines
- Gutter highlight bar shows full annotation scope on selection

### v1.1 (2026-01-29)
- OpenCV-based element alignment for snapping shapes to PNG visuals
- Line detection with endpoint, angle, and arrowhead detection
- Dashed line support via collinear segment merging
- Text matching to locate lines using label/note metadata

### v1.0 (2026-01-28)
- Initial stable release
- Text vertical alignment and spacing controls
- Ellipse text label support
- Dash pattern controls for pen styles
- Qt Designer property panel with auto-compile
- Focus mode scroll improvements
- AI extraction with formatting defaults
- 7 built-in themes

## License

MIT
