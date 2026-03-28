# PictoSync Test Suite

Automated test suite for the PictoSync diagram annotation tool.
All tests use **pytest** and run against the project in the repository root.

## Quick Start

```bash
# Run all tests
.venv/Scripts/python -m pytest tests/ -v

# Run all tests (short output)
.venv/Scripts/python -m pytest tests/ -q
```

## Directory Structure

```
tests/
├── conftest.py                      # Shared fixtures (QApp, MainWindow, Scene)
├── README.md                        # This file
│
│   ── Canvas Item Tests ──
├── test_item_kinds.py               # All 12 drawn kinds: creation, JSON fields, meta editing, pen color
├── test_port_item.py                # MetaPortItem: creation, to_record, parent attachment, port type
├── test_group_item.py               # MetaGroupItem: children, nesting, geom offset, to_record
├── test_seqblock_item.py            # MetaSeqBlockItem: block type, divider count, adjust1/2/3
│
│   ── Round-Trip Tests ──
├── test_to_record_roundtrip.py      # to_record → reconstruct → to_record for all 13 kinds
├── test_polygon_curve_vertices.py   # Polygon Q/C extended vertex format survives round-trip
├── test_rotation_roundtrip.py       # geom.angle persistence for all rotatable shapes
├── test_blocks_runs_roundtrip.py    # contents.blocks/runs formatting (bold, italic, color, spacing)
├── test_style_fill_roundtrip.py     # style.fill.color and transparency round-trip
├── test_adjust_roundtrip.py         # Schema-driven adjust controls (spinbox ↔ JSON ↔ canvas)
│
│   ── Data Model Tests ──
├── test_text_dedup.py               # _dedup_blocks and _dedup_label_tech_note
├── test_kind_alias.py               # KIND_ALIAS_MAP resolution
│
│   ── Integration Tests ──
├── test_scroll_preservation.py      # Editor scroll during canvas drag; PUML import annotations
├── test_ungroup_drag.py             # Ungroup + drag: index integrity, duplicate IDs, callbacks
├── test_flow_ungroup.py             # Flow diagram: move → ungroup → drag sequence
│
│   ── Parser Tests ──
├── test_mermaid_parser.py           # Mermaid SVG → annotations (flowchart, state, C4)
├── test_c4_source_parser.py         # Mermaid C4 source text parsing
├── test_c4_merger.py                # C4 source + SVG geometry merger
├── test_sequence_source_parser.py   # Mermaid sequence source text parsing
├── test_sequence_merger.py          # Sequence source + SVG merger
│
│   ── UI Framework Tests ──
├── test_undo_redo.py                # All 11 QUndoCommand classes: move, resize, text, properties
├── test_drawing_modes.py            # Mode switching, sticky mode, split-button variants
├── test_context_menu_zorder.py      # Z-order, group/ungroup requests, dividers
├── test_json_editor.py              # Code folding, annotation tracking, gutter, read-only fields
├── test_properties_panel.py         # Per-kind controls, pen/fill sync, tabs
├── test_keyboard_shortcuts.py       # All tool/edit/view keyboard shortcuts
├── test_canvas_view.py              # Zoom, zoom region, handles enclosed, drag acceptance
├── test_drag_drop.py                # File extension acceptance logic, drop callback
├── test_settings_dialog.py          # Dialog tabs, controls, buttons, actions
├── test_menu_system.py              # All 5 menus, action presence, initial states
│
│   ── Export Tests ──
└── test_pptx_export.py              # PowerPoint export: blocks/runs text, shapes, lines, formatting
```

## Shared Fixtures (`conftest.py`)

All test boilerplate is centralised in `conftest.py`. Individual test files
should **not** create their own `QApplication`, set `QT_QPA_PLATFORM`, or
insert `sys.path`. The conftest provides:

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `qapp` | session | Single `QApplication` instance (created at import time) |
| `main_window` | function | Fresh `MainWindow` per test (shown + events processed) |
| `scene` | function | Standalone `AnnotatorScene` (no MainWindow) |

### Using fixtures

```python
# Test that needs MainWindow (GUI integration)
class TestSomething:
    def test_foo(self, main_window):
        mw = main_window
        mw.scene.addItem(item)
        ...

# Test that needs a scene but not MainWindow
class TestOther:
    def test_bar(self, scene):
        scene.addItem(item)
        ...

# Test that needs Qt but not a window (uses module-level QApp from conftest)
def test_baz():
    from canvas.items import MetaRectItem
    item = MetaRectItem(0, 0, 100, 50, "id1", None)
    rec = item.to_record()
    assert rec["kind"] == "rect"

# Pure unit test (no Qt needed — conftest QApp is harmless)
def test_model():
    from models import CharFormat
    cf = CharFormat(bold=True)
    assert cf.to_dict(sparse=True) == {"bold": True}
```

## Test Design Patterns

### 1. Test organisation

Use **test classes** to group related assertions. Name classes `TestFoo`
and methods `test_bar`:

```python
class TestRectCreation:
    def test_kind(self):
        ...
    def test_geom_fields(self):
        ...
```

### 2. Parametrize over item kinds

When a property applies to all (or most) item kinds, use `@pytest.mark.parametrize`:

```python
ALL_KINDS = ["rect", "roundedrect", "ellipse", ...]

@pytest.mark.parametrize("kind", ALL_KINDS)
def test_fill_color_present(self, kind):
    item = FACTORIES[kind]()
    rec = item.to_record()
    assert "fill" in rec["style"]
```

### 3. Factory helpers

Define module-level factory functions or dicts for creating items:

```python
SHAPE_ITEMS = {
    "rect": lambda: MetaRectItem(50, 50, 120, 80, "t1", None),
    "ellipse": lambda: MetaEllipseItem(50, 50, 120, 80, "t2", None),
}

def _make_polygon(points, ann_id="poly1"):
    return MetaPolygonItem(100, 100, 200, 200, points, ann_id, on_change=None)
```

### 4. Round-trip tests

The standard round-trip pattern:

```python
def test_survives_roundtrip(self):
    item = create_item()          # 1. Create
    rec1 = item.to_record()       # 2. Serialize
    item2 = reconstruct(rec1)     # 3. Reconstruct from JSON
    rec2 = item2.to_record()      # 4. Serialize again
    assert rec1["geom"] == rec2["geom"]  # 5. Compare
```

### 5. Assertions

Use plain `assert` with descriptive failure messages for non-obvious checks:

```python
assert rec["kind"] == "polygon"
assert abs(rec["geom"]["x"] - 100) < 0.1, f"x drifted: {rec['geom']['x']}"
assert "angle" not in rec["geom"], "Zero rotation should not emit angle"
```

### 6. No scene for item-only tests

Most item tests do **not** need a scene or MainWindow. Create items
directly with their constructor. Only use `scene` or `main_window`
fixtures when testing drag, selection, or JSON editor sync.

## Running Tests

### Run everything

```bash
.venv/Scripts/python -m pytest tests/ -v
```

### Run a single file

```bash
.venv/Scripts/python -m pytest tests/test_port_item.py -v
```

### Run a single test class

```bash
.venv/Scripts/python -m pytest tests/test_rotation_roundtrip.py::TestSetRotation -v
```

### Run a single test method

```bash
.venv/Scripts/python -m pytest tests/test_rotation_roundtrip.py::TestSetRotation::test_angle_45 -v
```

### Run by keyword (name matching)

```bash
# All tests with "polygon" in the name
.venv/Scripts/python -m pytest tests/ -k "polygon" -v

# All tests except seqblock-related
.venv/Scripts/python -m pytest tests/ -k "not seqblock" -v

# Combine keywords
.venv/Scripts/python -m pytest tests/ -k "roundtrip and not rotation" -v
```

### Run by marker or parametrize value

```bash
# Only the "rect" parametrize variant
.venv/Scripts/python -m pytest tests/test_to_record_roundtrip.py -k "rect" -v
```

### Stop on first failure

```bash
.venv/Scripts/python -m pytest tests/ -x
```

### Show local variables on failure

```bash
.venv/Scripts/python -m pytest tests/ -l --tb=short
```

## Coverage

### Install coverage tools

```bash
pip install pytest-cov
```

### Run with coverage

```bash
# Coverage for the whole project
.venv/Scripts/python -m pytest tests/ --cov=. --cov-report=term-missing

# Coverage for specific modules
.venv/Scripts/python -m pytest tests/ --cov=canvas --cov=models --cov=pptx_export --cov-report=term-missing

# Coverage for a single test file against a single module
.venv/Scripts/python -m pytest tests/test_pptx_export.py --cov=pptx_export --cov-report=term-missing
```

### Generate HTML coverage report

```bash
.venv/Scripts/python -m pytest tests/ --cov=. --cov-report=html
# Open htmlcov/index.html in a browser
```

### Generate XML coverage report (for CI)

```bash
.venv/Scripts/python -m pytest tests/ --cov=. --cov-report=xml
# Produces coverage.xml in the project root
```

## Test Reports

### Install reporting tools

```bash
pip install pytest-html
```

### Generate HTML test report

```bash
.venv/Scripts/python -m pytest tests/ -v --html=test_report.html --self-contained-html
```

### JUnit XML report (for CI integration)

```bash
.venv/Scripts/python -m pytest tests/ --junitxml=test_results.xml
```

### Combined: coverage + HTML report

```bash
.venv/Scripts/python -m pytest tests/ -v \
    --cov=. --cov-report=html --cov-report=term-missing \
    --html=test_report.html --self-contained-html
```

## Adding a New Test File

1. Create `tests/test_<feature>.py`
2. Add a module docstring describing what is tested
3. Import what you need — `conftest.py` handles QApp, sys.path, and
   QT_QPA_PLATFORM automatically
4. Use fixtures from conftest (`qapp`, `main_window`, `scene`) as needed
5. **Do not** add `sys.path.insert`, `QT_QPA_PLATFORM`, `QApplication`
   creation, or `main_window` fixture definitions — they are all in conftest
6. Follow the patterns above (classes, parametrize, factories, round-trip)

### Template

```python
"""Test bench for <feature>.

Tests:
    - <what is tested>
    - <what is tested>
"""
from __future__ import annotations

import pytest

from canvas.items import MetaRectItem  # or whatever you need


class TestFeature:
    def test_basic(self):
        item = MetaRectItem(0, 0, 100, 50, "id1", None)
        rec = item.to_record()
        assert rec["kind"] == "rect"
```
