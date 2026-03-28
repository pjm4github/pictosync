"""Shared test fixtures for PictoSync test suite.

Centralises QApplication creation, QT_QPA_PLATFORM, sys.path, and
common fixtures so individual test files don't duplicate boilerplate.
"""
from __future__ import annotations

import os
import sys

import pytest

# ── Environment ──────────────────────────────────────────────────────────
# Set offscreen platform BEFORE any Qt imports.  This must happen at
# conftest load time (before any test file imports QApplication).
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Ensure the project root is on sys.path so `from canvas.items import ...`
# works regardless of how pytest is invoked.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


# ── QApplication fixture ─────────────────────────────────────────────────

# Create QApplication at import time (before any test file loads Qt widgets).
# This is necessary because some tests create Qt objects at module level
# (e.g., in helper functions) rather than inside fixtures.
from PyQt6.QtWidgets import QApplication as _QApp
_qapp_instance = _QApp.instance() or _QApp(sys.argv)


@pytest.fixture(scope="session")
def qapp():
    """Provide a single QApplication for the entire test session.

    Session-scoped so all tests share one instance (Qt only allows one).
    The app is already created at conftest import time above.
    """
    yield _qapp_instance


# ── MainWindow fixture ───────────────────────────────────────────────────

@pytest.fixture()
def main_window(qapp):
    """Create a fresh MainWindow for each test.

    The window is shown and events are processed so that Qt completes
    layout and signal wiring before the test body runs.
    """
    from main import MainWindow
    from settings import SettingsManager
    sm = SettingsManager()
    mw = MainWindow(sm)
    mw.show()
    qapp.processEvents()
    yield mw
    mw.close()


# ── Scene fixture ────────────────────────────────────────────────────────

@pytest.fixture()
def scene():
    """Create a standalone AnnotatorScene (no MainWindow)."""
    from canvas.scene import AnnotatorScene
    return AnnotatorScene()
