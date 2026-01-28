# PictoSync

**v1.0** | PNG Image Canvas Tool for Object Synchronization

Diagram annotation tool with AI-powered extraction and bidirectional sync.

## Abstract

PictoSync is a PyQt6 desktop application for creating and managing diagram annotations. It combines manual drawing tools with Google Gemini AI to automatically extract structural elements from architecture diagrams (such as C4 models). The application maintains bidirectional synchronization between a visual canvas and JSON representation, enabling a human-in-the-loop workflow where AI extracts, humans refine, and changes sync back seamlessly.

## Features

### Drawing & Annotation
- **Manual Drawing Tools**: Rectangle, rounded rectangle, ellipse, line, and text annotations
- **Text Labels**: All shapes support label, tech, and note text with customizable formatting
- **Text Alignment**: Vertical alignment (top/middle/bottom) and line spacing controls
- **Pen Styles**: Solid or dashed lines with configurable dash pattern (length, solid percent)
- **Z-Order Control**: Right-click context menu to "Bring to Front" or "Send to Back"
- **Auto-Stacking**: New shapes automatically appear on top of existing items

### AI Integration
- **AI Extraction**: Automatic diagram element detection using Google Gemini models
- **Smart Defaults**: Extracted elements automatically get formatting defaults
- **Markdown Handling**: Automatically strips markdown fences from AI responses

### Synchronization
- **Bidirectional Sync**: Real-time synchronization between canvas elements and JSON editor
- **Human-in-the-Loop**: AI extracts → Human edits → Syncs back (round-trip workflow)
- **Import/Export**: Save and load overlay annotations as JSON

### JSON Editor
- **Syntax Highlighting**: Full JSON syntax highlighting
- **Line Numbers**: Theme-aware line number gutter with selection highlighting
- **Code Folding**: Collapse/expand JSON objects and arrays
- **Focus Mode**: Toggle to show only the selected annotation (lamp icon)
- **Smart Scrolling**: Clicking canvas items scrolls editor to the annotation's ID field

### Property Panel
- **Context-Sensitive**: Shows relevant controls based on selected item type
- **Qt Designer UI**: Built with Qt Designer for consistent layout
- **Auto-Compile**: UI files are automatically compiled on startup if modified
- **Text Formatting**: Font size, alignment, vertical position, and spacing controls

### User Interface
- **Hide/Show PNG**: Toggle background image visibility for cleaner annotation view
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

Set your Google API key for AI extraction:
```bash
export GOOGLE_API_KEY=your_api_key_here
```

## Usage

```bash
python main.py
```

### Basic Workflow
1. **Load an image**: Drag and drop a PNG or use File > Open PNG
2. **Draw annotations**: Select a tool (R=Rect, U=RoundedRect, E=Ellipse, L=Line, T=Text, S=Select)
3. **AI extraction**: Click "Auto-Extract (Gemini)" to detect diagram elements
4. **Edit JSON**: Modify annotations in the Draft JSON panel
5. **Link**: Click "Import & Link" to enable bidirectional JSON ↔ Canvas sync
6. **Save**: Export your annotations via File > Save Overlay JSON

### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| S | Select mode |
| R | Rectangle tool |
| U | Rounded rectangle tool |
| E | Ellipse tool |
| L | Line tool |
| T | Text tool |
| Delete | Delete selected item |

### Tips
- **Z-Order**: Right-click a selected shape for "Bring to Front" / "Send to Back"
- **Focus Mode**: Click the lamp icon to collapse all annotations except the selected one
- **Hide PNG**: Toggle background visibility when annotations obscure the image
- **Themes**: Access Settings to switch between 7 visual themes
- **Text Formatting**: Use the property panel to adjust vertical alignment and spacing

## Project Structure

```
pictosync/
├── main.py              # Application entry point, MainWindow
├── models.py            # Data models, AnnotationMeta, normalize_meta()
├── styles.py            # Theme stylesheets, dash patterns, color configs
├── utils.py             # JSON parsing, coordinate scaling, markdown handling
├── canvas/              # Graphics layer
│   ├── items.py         # Annotation items (Rect, Ellipse, Line, Text) with labels
│   ├── mixins.py        # LinkedMixin, MetaMixin for shared behavior
│   ├── scene.py         # AnnotatorScene (drawing, context menu, z-order)
│   └── view.py          # AnnotatorView (zoom, pan, drag-drop)
├── editor/              # JSON editor
│   ├── code_editor.py   # JsonCodeEditor with folding and focus mode
│   ├── draft_dock.py    # DraftDock widget with scroll-to-id
│   └── highlighter.py   # JSON syntax highlighting
├── properties/          # Property panel
│   ├── dock.py          # PropertyPanel controller
│   ├── properties_panel.ui   # Qt Designer UI file
│   └── properties_ui.py      # Auto-generated from .ui file
├── schemas/             # JSON schemas
│   └── annotation_schema.json  # Annotation format specification
├── gemini/              # AI integration
│   └── worker.py        # Threaded Gemini API worker
├── icons/               # Theme-aware SVG icons
│   ├── generate_icons.py    # Icon generation script
│   └── [Theme folders]      # Icons for each theme
└── requirements.txt
```

## Schema

Annotations follow a JSON schema with support for:
- **Geometry**: rect, roundedrect, ellipse, line, text
- **Meta**: label, tech, note with alignment and sizing
- **Style**: pen (color, width, dash), brush (fill), text (color, size)
- **Text Layout**: vertical alignment, spacing, bounding box dimensions

See `schemas/annotation_schema.json` for the full specification.

## Version History

### v1.0 (2025-01-28)
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
