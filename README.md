<p align="center">
  <img src="assets/banner.svg" alt="PictoSync Banner" width="800"/>
</p>

# PictoSync

**v2.1** | Diagram Normalization & Agentic Specification IDE

---

## Why PictoSync Exists

Enterprise architecture artifacts live in dozens of formats: PlantUML component diagrams, Mermaid flowcharts, C4 models, state machines, hand-drawn whiteboard photos exported as PNGs, Visio exports, and ad-hoc PowerPoint slides. These diagrams encode critical knowledge — component boundaries, data flows, interface contracts, deployment topology — but that knowledge is locked inside tool-specific rendering formats that no downstream system can reason about programmatically.

**The original goal of PictoSync was to bring legacy architecture components forward into an agentic-readable format by normalizing various diagram-as-code artifacts.** A PlantUML deployment diagram, a Mermaid C4 container view, and a hand-annotated PNG screenshot of a whiteboard all describe the same kind of thing — interconnected components with contracts and constraints — but they do it in mutually incompatible syntaxes. PictoSync unifies them into a single structured JSON annotation format that preserves spatial layout, semantic metadata, and inter-element relationships, making the architecture machine-readable regardless of its original source.

This normalization layer is what makes everything else possible: bidirectional sync, AI-assisted extraction, PowerPoint export, and — in the V2 vision — agentic specification authoring.

---

## PictoSync V2 Vision

<p align="center">
  <img src="pictosync_v2_architecture_map.svg" alt="Pictosync v2 Architecture Map" width="800"/>
</p>

### From annotation tool to agentic specification IDE

PictoSync v1 built a robust parsing and rendering foundation: ANTLR4 grammars for Flowchart, State, Sequence, and C4 diagram types; an `SVGNodeRegistry` creating a bidirectional index between AST nodes and rendered SVG elements; a PyQt6 `QGraphicsScene`-based canvas for interactive display; and the `mmdc` non-headless pipeline for Mermaid-to-SVG conversion. This infrastructure is not legacy — it becomes the rendering and inspection engine for v2.

PictoSync v2 is a **goal-oriented agentic specification IDE** — a workbench for directing software agents that use architecture diagramming as their primary design language for producing top-level interconnection specifications. The output is not code. It is a human-reviewed, versioned architectural specification that defines how components connect, what contracts they hold, and what constraints they operate under.

The core insight is that architecture diagrams — particularly the C4, sequence, and flowchart types already supported in v1 — are a precise enough language to serve as machine-readable specifications, not just documentation. An agent can read a Mermaid diagram, reason about it against a goal hierarchy, propose a modification or extension, and emit a new diagram. The human's role is editorial: to monitor, redirect, approve, or reject each agent-generated revision. The IDE structures that loop.

### Long-Term Goals

**G1 — Goal-directed agent orchestration.** A structured goal editor where engineers define an objective hierarchy: top-level system intent, sub-goals, acceptance criteria, and architectural constraints. Agents receive this hierarchy as context and use it to drive spec generation, ensuring every diagram revision is traceable to a stated goal rather than unconstrained exploration.

**G2 — Diagram-as-specification semantics.** Every diagram produced in v2 carries formal semantic weight beyond visual rendering. Component names, relationship labels, and boundary annotations are treated as specification statements that can be validated, diffed, and exported to downstream tooling. The v1 `SVGNodeRegistry` and AST infrastructure provide the structural index needed to make individual diagram elements addressable as specification artifacts.

**G3 — Human-in-the-loop as a first-class design constraint.** Agent proposals are never silently accepted. The review gate is a primary UI surface, not a confirmation dialog. Engineers see what the agent proposed, why it proposed it (traceable to the goal hierarchy), what changed from the prior version, and what downstream implications the change carries. Review actions — approve, reject, annotate, redirect — are logged and become part of the decision lineage.

**G4 — Versioned specification lineage.** The spec artifact store maintains a full history of diagram revisions with diffs, authorship (human vs agent), and the goal context that motivated each change. This supports audit, rollback, and collaborative review workflows appropriate to high-consequence systems (OT, power grid, IEC 61850 environments where specification traceability is a compliance concern).

**G5 — Exportable interconnection specifications.** Approved specs must be consumable by downstream systems without manual transcription. Export targets include Mermaid source (for further tooling), structured JSON schema (for programmatic integration), and domain-specific formats relevant to the target environment — IEC 61850 SCD topology, SCADA integration descriptors, or API contract stubs.

### V2 IDE layout (target)

```mermaid
C4Component
    title PictoSync v2 IDE Layout

    
        Container_Boundary(top, "Upper Panels") {
            Component(canvas, "Diagram Canvas", "Live spec render via v1 SVGNodeRegistry + PyQt6 QGraphicsScene")
            Component(review, "Human Review Gate", "Approve / Reject / Annotate / Redirect, Decision log")
            Component(goal, "Goal Editor", "Objective hierarchy, acceptance criteria, constraints")
        }
 
    Container_Boundary(bottom, "Lower Panels") {
        Component(agent, "Agent Workspace", "Goal decomposition, spec generation loop")
        Component(store, "Spec Artifact Store", "Versioned diagrams, diff, lineage view")
        Component(export, "Export / Handoff", "IEC 61850, SCADA, JSON schema, Mermaid source")
    }

    Rel_D(canvas, review, "Surfaces changes")
    Rel_D(agent, store, "Persists versions")
    Rel_D(store, export, "Exports specs")
    Rel_U(goal, canvas, "Informs design")
    Rel_U(goal, store, "Track Goals")
    Rel_D(review, agent, "Approve / Redirect")
    Rel_L(agent, review, "Proposes revisions")
    Rel_R(review, goal, "Review criteria")
```

### Relationship to v1

V2 is an application layer built on top of the v1 rendering and parsing foundation, not a replacement.

| v1 component | Role in v2 |
|---|---|
| ANTLR4 grammars | Parsing engine for all agent-emitted and human-edited diagrams |
| `SVGNodeRegistry` | Element-level diff, annotation, and review highlight bridge |
| PyQt6 canvas | Diagram canvas panel embedded in the v2 `QSplitter` IDE layout |
| `mmdc` pipeline | Rendering of agent-generated and revised diagrams |

### Primary user

The primary user is a senior engineer or architect working on systems where interconnection specifications have formal significance — not casual documentation. They are directing agents, not hand-drawing diagrams. Their value-add is judgment: knowing when an agent-proposed topology is architecturally sound, whether it respects unstated constraints the goal hierarchy doesn't yet capture, and when to redirect versus approve. The IDE is built to support that judgment, not to automate it away.

---

## Current Features (v2.0)

**For a comparison to other tools and their features see: [Round Tripping PNG Tools](png_json_comparison.md)**

### Diagram Import & Normalization

PictoSync's core capability is ingesting diagrams from multiple source formats and normalizing them into a unified JSON annotation model.

| Source Format | Import Method | What Gets Extracted |
|---|---|---|
| **PNG images** | Drag-and-drop, File > Open | Background canvas; AI extraction of shapes, lines, text |
| **PlantUML** (`.puml`) | Drag-and-drop, File > Open | Component, deployment, use-case, architecture, activity, sequence, state, class diagrams |
| **Mermaid SVG** | Drag-and-drop, File > Open | Flowcharts, state diagrams with full `classDef` styling |
| **Mermaid source** (`.mmd`) | Drag-and-drop, File > Open | Rendered via mmdc CLI; PNG background + SVG annotation parsing |
| **Mermaid C4** | Source + SVG two-step pipeline | Context, Container, Component, Dynamic, Deployment with full C4 semantics |

All sources converge to the same JSON annotation schema — shapes, lines, curves, text, ports, groups — with geometry, metadata, and style preserved.

### Drawing & Annotation
- **Manual Drawing Tools**: Rectangle, rounded rectangle, ellipse, hexagon, cylinder, block arrow, isometric cube, polygon, curve, orthogonal curve, line, text, and port annotations
- **Isometric Cube**: Container shape with configurable extrusion depth and angle (0-360); drag control handles to adjust depth and direction interactively
- **Curve Tool**: Click-click placement of SVG path-like curves with node editing; supports cubic bezier (`C`), quadratic bezier (`Q`), arc (`A`), and line (`L`) segments; right-click nodes to change type; arrowhead support (none, start, end, both)
- **Orthogonal Curve**: Curve variant restricted to horizontal/vertical segments (M/H/V nodes) with optional corner bend radius; Ctrl+click to extend; arrowhead support; last endpoint is an L node (freely draggable in both axes); bend radius applies to the final corner
- **Polygon Tool**: Multi-click vertex placement with right-click to close; double-click to enter vertex editing mode with draggable control knobs; right-click vertices to delete, right-click edges to add vertices
- **Text Labels**: All shapes support label, tech, and note text with customizable formatting
- **Text Alignment**: Vertical alignment (top/middle/bottom) and line spacing controls
- **Rotation**: All shapes support rotation via drag handle (green knob) or property panel angle spinner (0-359); rotation-aware resize handles follow the rotated axis
- **Port Connections**: Attach port connectors to any shape's perimeter; ports track a parametric position (t) and move with their parent; snap-to-port with cyan glow visual feedback; Alt+click/drag to select ports underneath overlapping lines
- **Pen Styles**: Solid or dashed lines with configurable dash pattern
- **Z-Order Control**: Right-click context menu to "Bring to Front" or "Send to Back"

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

### AI Integration
- **AI Extraction**: Automatic diagram element detection using Google Gemini models
- **Model Selection**: Configurable model list and default model in settings; dropdown menu in toolbar
- **Focus Align**: Refine a selected element via Gemini AI on a cropped region around it
- **Token Counter**: Live Gemini token usage counter displayed on the toolbar
- **Note**: If you don't have a Google Gemini API key, or don't want to send your picture to Google for scanning, you can still place graphics on the picture and use the local optimizer to match them to the PNG

### Synchronization
- **Bidirectional Sync**: Real-time synchronization between canvas elements and JSON editor
- **Live Drag Updates**: Geometry values update in the JSON editor in real-time during drag without scroll jumping
- **Scroll Lock During Interaction**: Editor scroll position is frozen from mouse-down to mouse-up, then scrolls to the final position on release
- **Human-in-the-Loop**: AI extracts, human edits, changes sync back (round-trip workflow)
- **Project Save/Load**: Save and load projects (annotations + PNG) to a configurable workspace directory

### JSON Editor
- **Syntax Highlighting**: Full JSON syntax highlighting with line numbers
- **Code Folding**: Collapse/expand JSON objects and arrays
- **Focus Mode**: Toggle to show only the selected annotation (lamp icon)
- **Schema Check**: Toggle checkbox compares the focused annotation against `annotation_schema.json` — missing fields appear as gray ghost text, extra fields are highlighted in red
- **Accept Ghost Fields**: Right-click a gray ghost field to make it permanent
- **Smart Scrolling**: Clicking canvas items scrolls editor to the annotation's opening brace
- **Gutter Highlight Bar**: Colored bar marks the full scope of the selected annotation

### Property Panel
- **Context-Sensitive**: Shows relevant controls based on selected item type
- **Schema-Driven Adjust Controls**: Labels, suffixes, and ranges derived from `annotation_schema.json`
- **Contents Tab**: Rich-text editor with run-level font family, font size, bold/italic/underline, text color, subscript/superscript, and alignment controls
- **Text Selection Persistence**: Selection stays highlighted when focus moves to panel controls

### PowerPoint Export
- **Slide Export**: Export annotations as native PowerPoint shapes via File > Export PPTX
- **Shape Support**: All 13 annotation kinds including native bezier curves, arrowheads, rotation, and transparency
- **Group Flattening**: Groups recursively flattened for export

### User Interface
- **Multiple Themes**: 7 built-in themes (Foundation Dark, Bulma Light, Bauhaus, Neumorphism, Materialize, Tailwind, Bootstrap)
- **Custom Icons**: Theme-matched SVG icons for all tools and actions
- **Dynamic Title Bar**: Window title shows the currently loaded file
- **Wheel Guard**: Mouse wheel does not change spinner/combo values unless the widget has keyboard focus

### Domain-Specific Language (DSL)
- **Domain Plugin System**: Extensible `domains/` folder; each domain provides a `tools.json` defining drawing tools
- **DSL Toolbar**: Second toolbar row appears when a domain is activated
- **Schema-Documented DSL Metadata**: `meta.dsl` structure defined in `annotation_schema.json`; extensible to PlantUML, D2, SysML, ArchiMate
- **NS3 Example Domain**: Reference implementation under `domains/ns3/`

---

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

### Basic Workflow
1. **Load a diagram**: Drag and drop a PNG, PUML, SVG, or MMD file, or use File > Open
2. **Draw annotations**: Select a tool (R=Rect, U=RoundedRect, E=Ellipse, L=Line, V=Curve, T=Text, H=Hexagon, Y=Cylinder, A=Block Arrow, I=Iso Cube, P=Polygon, O=Port, S=Select)
3. **AI extraction**: Click "Auto-Extract (Gemini)" to detect diagram elements
4. **Edit JSON**: Modify annotations in the Draft JSON panel
5. **Link**: Click "Import & Link" to enable bidirectional JSON-Canvas sync
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
| I | Iso Cube tool |
| P | Polygon tool |
| O | Port tool |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Ctrl+S | Save project |
| Ctrl+O | Open project |
| Alt+Click | Select port underneath overlapping lines |
| Delete | Delete selected item |

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
| `test_item_kinds.py` | All 13 item kinds end-to-end: creation/JSON field correctness, property panel meta editing, pen color changes, and no duplicate IDs |
| `test_adjust_roundtrip.py` | Schema-driven adjust control labels, suffixes, ranges; adjust value round-trips through panel/JSON/canvas |
| `test_scroll_preservation.py` | Editor scroll stays frozen during canvas drag; JSON geometry values update live during drag; PUML import produces correct annotations |
| `test_ungroup_drag.py` | Ungroup preserves index integrity; no duplicate IDs after ungroup; children retain callbacks; geometry updates during drag |
| `test_flow_ungroup.py` | Move-then-ungroup-then-drag on flow/activity diagrams; index integrity and duplicate ID checks |

## Project Structure

```
pictosync/
├── main.py              # Application entry point, MainWindow
├── models.py            # Data models, AnnotationMeta, DrawMode, normalize_meta()
├── styles.py            # Theme stylesheets, dash patterns, color configs
├── utils.py             # JSON parsing, coordinate scaling, markdown handling
├── settings.py          # Application settings (workspace, export, Gemini models)
├── settings_dialog.py   # Settings dialog UI (general, themes, Gemini model list)
├── undo_commands.py     # Undo/redo commands for all canvas operations
├── canvas/              # Graphics layer
│   ├── items.py         # Annotation items (all 13 kinds + Group)
│   ├── perimeter.py     # Perimeter geometry for port attachment
│   ├── mixins.py        # LinkedMixin, MetaMixin for shared behavior
│   ├── scene.py         # AnnotatorScene (drawing, context menu, z-order)
│   └── view.py          # AnnotatorView (zoom, pan, drag-drop, rubber band)
├── editor/              # JSON editor
│   ├── code_editor.py   # JsonCodeEditor with folding, focus mode, ghost fields
│   ├── draft_dock.py    # DraftDock widget with scroll-to-id, scroll lock
│   ├── schema_checker.py # Schema diff engine
│   └── highlighter.py   # JSON syntax highlighting
├── properties/          # Property panel
│   ├── dock.py          # PropertyPanel controller (schema-driven)
│   ├── properties_panel.ui   # Qt Designer UI file
│   └── properties_ui.py      # Auto-generated from .ui file
├── schemas/             # JSON schemas and schema utilities
│   ├── __init__.py      # Schema-driven defaults, validation, template builder
│   └── annotation_schema.json  # Annotation format specification
├── plantuml/            # PlantUML import
│   ├── renderer.py      # PlantUML to PNG/SVG rendering
│   └── parser.py        # PUML text parsing, SVG position extraction
├── mermaid/             # Mermaid import (SVG + source)
│   ├── parser.py        # Mermaid SVG detection and parsing
│   ├── renderer.py      # SVG-to-PNG rendering
│   ├── c4_source_parser.py  # C4 source text parsing
│   └── c4_merger.py     # Merges C4 source semantics with SVG geometry
├── gemini/              # AI integration
│   └── worker.py        # Threaded Gemini API worker
├── pptx_export.py       # PowerPoint slide export
├── alignment/           # OpenCV alignment
│   ├── optimizer.py     # Shape and line alignment algorithms
│   └── worker.py        # Threaded alignment workers
├── domains/             # Domain-specific DSL plugins (e.g. ns3/)
├── icons/               # Theme-aware SVG icons
├── tests/               # Automated test suite (pytest)
├── test_data/           # Test fixture data (PUML, Mermaid SVG)
└── requirements.txt
```

## Schema

Annotations follow a JSON schema with support for:
- **Geometry**: rect, roundedrect, ellipse, hexagon, cylinder, blockarrow, isocube, polygon, curve, orthocurve, line, text, port, group
- **Curve Geometry**: Bounding box plus `nodes` array with SVG path commands (`M`, `L`, `C`, `Q`, `A`, `Z`) and normalized 0-1 control point coordinates
- **Group**: Recursive `children` array containing nested annotations
- **Meta**: label, tech, note with alignment and sizing; `meta.dsl` for tool-specific semantics (Mermaid, PlantUML, D2)
- **Style**: pen (color, width, dash), fill (color with alpha), text (color, size), arrow (none, start, end, both)

See `schemas/annotation_schema.json` for the full specification.

## Diagram Import Coverage

### PlantUML

| Diagram Type | Parse | Render | Notes |
|-------------|:-----:|:------:|-------|
| Component | Y | Y | Description diagram parser (entities, clusters, links) |
| Deployment | Y | Y | Description diagram parser |
| Use Case | Y | Y | Description diagram parser |
| Architecture | Y | Y | Description diagram parser |
| Activity | Y | Y | Dedicated parser (partitions, flow lines, start/end nodes) |
| Sequence | Y | Y | Dedicated parser (participants, messages, lifelines) |
| State | Y | Y | Dedicated parser (states, transitions, start/end) |
| Class | Y | Y | Falls through to generic SVG position extraction |

### Mermaid

| Diagram Type | Parse | Render | Notes |
|-------------|:-----:|:------:|-------|
| Flowchart | Y | Y | `nodes`/`edgePaths`/`edgeLabels` groups |
| State Diagram | Y | Y | Composite/concurrent states, `classDef` styles, notes, fork/join |
| C4 (all 5 types) | Y | Y | Two-step pipeline: source semantics + SVG geometry |

Additional Mermaid diagram types (Sequence, Class, ER, Gantt, Mindmap, etc.) have test data collected; parsers not yet implemented.

## Version History

### v2.0 (2026-03-14)
- **Contents tab**: Rich-text editor in the property panel with run-level font family, font size, bold/italic/underline, text color, subscript/superscript, alignment, wrap toggle, and text flow type
- **Text selection persistence**: Selected text stays highlighted when focus moves to panel controls
- **Theme radio button indicators**: All themes display correctly styled radio/checkbox indicators; Fusion style bypass for Windows native rendering
- **Gutter bar continuous sync**: JSON editor gutter highlight bar stays synchronized during typing, folding/unfolding
- **Wheel guard**: Prevents accidental value changes from scrolling past spinners and combo boxes

### v1.11 (2026-03-10)
- Snap-to-port, port disconnect, Alt+click/drag ports, port direction badge
- Connected lines follow movement; rotation-aware port connections
- Orthocurve L endpoint and bend radius on final corner
- PPTX dual arrow fix

### v1.10 (2026-03-08)
- Port connector tool with perimeter attachment and parametric tracking
- Port direction indicators, protocol labels, connections list
- Perimeter geometry engine for all shape kinds
- Port unparenting/reparenting via JSON editor

### v1.9 (2026-03-07)
- Shape rotation via drag handle or property panel
- Rotation-aware resize and editing
- PPTX rotation export; seqblock compound export
- DSL toolbar row

### v1.8 (2026-03-07)
- Mermaid state diagram import with composite states, classDef styling
- Pixel-perfect PNG alignment via viewBox matching
- SVG z-order; CSS color support; edge styling; two-path fill extraction

### v1.7 (2026-02-27)
- Dynamic title bar; wait cursor during imports; wider JSON editor; compact settings

### v1.6 (2026-02-22)
- Gemini model selection and Focus Align tool
- Schema-driven defaults; value-only validation; accept ghost fields
- Isometric Cube and Orthogonal Curve tools
- PPTX transparency export

### v1.5 (2026-02-18)
- Curve drawing tool with bezier/arc/line node editing
- PlantUML SVG path parsing; description diagram parser
- Native OOXML bezier export; undo/redo; group resize
- Schema-driven adjust controls

### v1.4 (2026-02-16)
- Standardized numeric precision; scroll lock during drag; live JSON updates
- Automated test suite

### v1.3 (2026-02-15)
- Activity diagram parser; nested group hierarchy
- PPTX fill/text colors, polygon freeforms

### v1.2 (2026-02-12)
- Polygon tool; SVG-based PlantUML position extraction
- Gutter highlight bar

### v1.1 (2026-01-29)
- OpenCV element alignment; line/arrowhead detection

### v1.0 (2026-01-28)
- Initial stable release

## License

MIT
