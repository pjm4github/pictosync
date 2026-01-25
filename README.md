# PictoSync

**PNG Image Canvas Tool for Object Synchronization**

Diagram annotation tool with AI-powered extraction and bidirectional sync.

## Abstract

PictoSync is a PyQt6 desktop application for creating and managing diagram annotations. It combines manual drawing tools with Google Gemini AI to automatically extract structural elements from architecture diagrams (such as C4 models). The application maintains bidirectional synchronization between a visual canvas and JSON representation, enabling a human-in-the-loop workflow where AI extracts, humans refine, and changes sync back seamlessly.

## Features

- **Manual Drawing Tools**: Rectangle, rounded rectangle, ellipse, line, and text annotations
- **AI Extraction**: Automatic diagram element detection using Google Gemini models
- **Bidirectional Sync**: Real-time synchronization between canvas elements and JSON editor
- **Human-in-the-Loop**: AI extracts → Human edits → Syncs back (round-trip workflow)
- **Property Editing**: Context-sensitive property panel for selected elements
- **JSON Editor**: Syntax-highlighted editor with line numbers and code folding
- **Import/Export**: Save and load overlay annotations as JSON

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/pictosync.git
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

1. **Load an image**: Drag and drop a PNG or use File > Open PNG
2. **Draw annotations**: Select a tool (R=Rect, U=RoundedRect, E=Ellipse, L=Line, T=Text, S=Select)
3. **AI extraction**: Click "Auto-Extract (Gemini)" to detect diagram elements
4. **Edit JSON**: Modify annotations in the Draft JSON panel
5. **Link**: Click "Import" to enable bidirectional JSON ↔ Canvas sync
6. **Save**: Export your annotations via File > Save Overlay JSON

## Project Structure

```
pictosync/
├── main.py              # Application entry point, MainWindow
├── models.py            # Data models, constants, drawing modes
├── utils.py             # JSON parsing, coordinate scaling
├── canvas/              # Graphics layer
│   ├── items.py         # Annotation items (Rect, Ellipse, Line, Text)
│   ├── mixins.py        # LinkedMixin, MetaMixin for shared behavior
│   ├── scene.py         # AnnotatorScene (drawing mode management)
│   └── view.py          # AnnotatorView (zoom, pan, drag-drop)
├── editor/              # JSON editor
│   ├── code_editor.py   # JsonCodeEditor with syntax features
│   ├── draft_dock.py    # DraftDock widget
│   └── highlighter.py   # JSON syntax highlighting
├── properties/          # Property panel
│   └── dock.py          # PropertyDock for editing selected items
├── gemini/              # AI integration
│   └── worker.py        # Threaded Gemini API worker
└── requirements.txt
```

## License

MIT
