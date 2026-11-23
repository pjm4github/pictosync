# PictoSync Diagnostic Scripts

Manual diagnostic scripts for investigating specific behaviours that are
not suitable for automated testing (they require visual inspection, a GUI
environment, or produce verbose exploratory output).

These scripts are **not** part of the pytest test suite.  Run them
directly with Python when you need to debug or verify a specific
subsystem.

## Scripts

### `diagnose_drag_kinds.py`

**Purpose:** Check which canvas item kinds correctly update their JSON
annotation geometry when dragged on the canvas.

**When to run:**
- After modifying `_notify_changed()`, `on_change` callbacks, or
  `itemChange()` in any canvas item class
- After adding a new item kind to verify it participates in the
  bidirectional JSON sync
- When drag-based geometry updates stop working for a specific kind

**What it does:**
1. Creates a MainWindow and loads `test_data/PUML/test_seq1.puml`
2. Finds all canvas items grouped by kind
3. For each kind (`rect`, `roundedrect`, `line`, `polygon`, `text`):
   - Snapshots the JSON annotation before drag
   - Simulates a 10px drag via `setPos()`
   - Snapshots the JSON annotation after drag
   - Reports whether `geom` changed and whether `on_change` is wired

**Usage:**
```bash
.venv/Scripts/python scripts/diagnose_drag_kinds.py
```

**Requirements:** Requires a GUI environment (not headless / offscreen).
The script creates and shows a `MainWindow`.

**Example output:**
```
Item kinds: {'rect': 3, 'roundedrect': 2, 'line': 4, 'polygon': 1, 'text': 2}
rect: id=a000001 idx=0 on_change=True geom_changed=True
  before: {'x': 100.0, 'y': 200.0, 'w': 150.0, 'h': 80.0}
  after:  {'x': 110.0, 'y': 210.0, 'w': 150.0, 'h': 80.0}
line: id=a000005 idx=4 on_change=True geom_changed=True
  before: {'x1': 50.0, 'y1': 60.0, 'x2': 250.0, 'y2': 180.0}
  after:  {'x1': 60.0, 'y1': 70.0, 'x2': 260.0, 'y2': 190.0}
```
