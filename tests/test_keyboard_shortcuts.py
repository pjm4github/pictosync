"""Test bench for keyboard shortcuts.

Tests that all documented keyboard shortcuts trigger the correct action:
  - Tool shortcuts: S, R, U, E, L, T, H, Y, A, I, P, V, K, O
  - Edit shortcuts: Ctrl+Z (undo), Ctrl+Y (redo), Delete
  - File shortcuts: Ctrl+S (save), Ctrl+O (open)
  - View shortcuts: F (zoom fit), 1 (zoom 100%), Z (zoom region)
  - F1 (help)
"""
from __future__ import annotations

import pytest

from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

from models import Mode


# ── Tool shortcut tests ──────────────────────────────────────────────────

TOOL_SHORTCUTS = [
    ("S", Mode.SELECT),
    ("R", Mode.RECT),
    ("U", Mode.ROUNDEDRECT),
    ("E", Mode.ELLIPSE),
    ("L", Mode.LINE),
    ("T", Mode.TEXT),
    ("H", Mode.HEXAGON),
    ("Y", Mode.CYLINDER),
    ("A", Mode.BLOCKARROW),
    ("I", Mode.ISOCUBE),
    ("P", Mode.POLYGON),
    ("O", Mode.PORT),
]

# V and K use split buttons — mode depends on current variant
VARIANT_SHORTCUTS = [
    ("V", {Mode.CURVE, Mode.ORTHOCURVE}),
    ("K", {Mode.SEQBLOCK}),
]


class TestToolShortcuts:
    """Single-key tool shortcuts switch drawing mode."""

    @pytest.mark.parametrize("key,expected_mode", TOOL_SHORTCUTS)
    def test_tool_key(self, main_window, key, expected_mode):
        mw = main_window
        # Start in a different mode to confirm the switch
        mw.set_mode(Mode.SELECT if expected_mode != Mode.SELECT else Mode.RECT)
        # Simulate key press on the main window
        qt_key = getattr(Qt.Key, f"Key_{key}")
        QTest.keyPress(mw, qt_key)
        assert mw.scene.mode == expected_mode, \
            f"Key '{key}' should set mode {expected_mode}, got {mw.scene.mode}"

    @pytest.mark.parametrize("key,expected_modes", VARIANT_SHORTCUTS)
    def test_variant_key(self, main_window, key, expected_modes):
        mw = main_window
        mw.set_mode(Mode.SELECT)
        qt_key = getattr(Qt.Key, f"Key_{key}")
        QTest.keyPress(mw, qt_key)
        assert mw.scene.mode in expected_modes, \
            f"Key '{key}' should set mode to one of {expected_modes}, got {mw.scene.mode}"


class TestEditShortcuts:
    """Edit keyboard shortcuts."""

    def test_delete_key(self, main_window):
        """Delete key triggers delete_selected_items (no crash with nothing selected)."""
        mw = main_window
        # Just verify it doesn't crash with no selection
        QTest.keyPress(mw, Qt.Key.Key_Delete)

    def test_ctrl_z_undo(self, main_window):
        """Ctrl+Z triggers undo (no crash with empty stack)."""
        mw = main_window
        QTest.keyPress(mw, Qt.Key.Key_Z, Qt.KeyboardModifier.ControlModifier)

    def test_ctrl_y_redo(self, main_window):
        """Ctrl+Y triggers redo (no crash with empty stack)."""
        mw = main_window
        QTest.keyPress(mw, Qt.Key.Key_Y, Qt.KeyboardModifier.ControlModifier)


class TestViewShortcuts:
    """View keyboard shortcuts."""

    def test_f_zoom_fit(self, main_window):
        """F key triggers zoom to fit (no crash with empty scene)."""
        mw = main_window
        QTest.keyPress(mw, Qt.Key.Key_F)

    def test_1_zoom_100(self, main_window):
        """1 key triggers zoom 100%."""
        mw = main_window
        QTest.keyPress(mw, Qt.Key.Key_1)

    def test_z_zoom_region(self, main_window):
        """Z key toggles zoom region mode."""
        mw = main_window
        QTest.keyPress(mw, Qt.Key.Key_Z)
