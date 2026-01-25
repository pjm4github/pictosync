# PictoSync

PyQt6 diagram annotation tool with Gemini AI extraction and bidirectional sync.

## Commands

- Run: `python main.py`
- Install deps: `pip install -r requirements.txt`
- Requires `GOOGLE_API_KEY` environment variable for AI features

## Architecture

- **Entry point**: `main.py` (MainWindow class)
- **MVC-like pattern**: Scene (model) + View + Controller (MainWindow)
- **Threading**: QThread for background AI operations (gemini/worker.py)

### Module Structure

| Module | Purpose |
|--------|---------|
| `canvas/` | Graphics items, scene, view (drawing layer) |
| `editor/` | JSON code editor with syntax highlighting |
| `properties/` | Property panel dock widget |
| `gemini/` | Threaded Gemini API worker |
| `models.py` | Data models, constants, drawing modes |
| `utils.py` | JSON extraction, coordinate scaling |

## Code Style

- Use `from __future__ import annotations` for type hints
- Docstrings for all classes and public methods (Args/Returns format)
- PascalCase for classes, snake_case for functions
- Private methods prefixed with `_`
- Use mixins for shared behavior (see `canvas/mixins.py`)
- PyQt6 signals for event communication

## Key Patterns

- Graphics items inherit from Qt items + mixins (LinkedMixin, MetaMixin)
- Bidirectional sync between JSON editor and canvas scene and PropertyDock for selected item in the canvas scene
- Dock widgets for panels (PropertyDock, DraftDock)
- Dataclasses for structured data (AnnotationMeta)
