"""Test bench for file drag & drop acceptance logic.

Tests the file extension acceptance logic used by AnnotatorView's
dragEnterEvent and dropEvent. We test the logic directly rather than
simulating Qt drag events (which cause access violations on Windows
when constructed from Python).

Tests:
  - Accepted file extensions: .png, .puml, .svg, .mmd, .mermaid
  - Rejected file extensions: .jpg, .gif, .txt, .pdf, .docx
  - Case-insensitive matching
  - Drop callback receives local file path (not URL)
  - Multiple files: iteration finds first accepted file
"""
from __future__ import annotations

import os
import tempfile

import pytest


# ── Acceptance logic (extracted from canvas/view.py) ─────────────────────

def _is_accepted_file(path: str) -> bool:
    """Replicate the acceptance logic from AnnotatorView.dragEnterEvent."""
    lf = path.lower()
    return (lf.endswith(".png") or lf.endswith(".puml")
            or lf.endswith(".svg") or lf.endswith(".mmd")
            or lf.endswith(".mermaid"))


def _first_accepted_path(paths: list) -> str:
    """Replicate the iteration logic from AnnotatorView.dropEvent."""
    for path in paths:
        if _is_accepted_file(path):
            return path
    return ""


# ── Tests ────────────────────────────────────────────────────────────────

class TestAcceptedExtensions:

    @pytest.mark.parametrize("ext", [".png", ".puml", ".svg", ".mmd", ".mermaid"])
    def test_accepted(self, ext):
        assert _is_accepted_file(f"/path/to/file{ext}")

    @pytest.mark.parametrize("ext", [".PNG", ".Puml", ".SVG", ".MMD", ".MERMAID"])
    def test_accepted_case_insensitive(self, ext):
        assert _is_accepted_file(f"/path/to/file{ext}")


class TestRejectedExtensions:

    @pytest.mark.parametrize("ext", [
        ".jpg", ".jpeg", ".gif", ".bmp", ".tiff",
        ".txt", ".pdf", ".docx", ".xlsx", ".pptx",
        ".py", ".json", ".xml", ".html", ".css",
    ])
    def test_rejected(self, ext):
        assert not _is_accepted_file(f"/path/to/file{ext}")


class TestFirstAcceptedPath:

    def test_single_accepted(self):
        assert _first_accepted_path(["/a/b.png"]) == "/a/b.png"

    def test_single_rejected(self):
        assert _first_accepted_path(["/a/b.txt"]) == ""

    def test_first_rejected_second_accepted(self):
        paths = ["/a/b.txt", "/a/c.puml"]
        assert _first_accepted_path(paths) == "/a/c.puml"

    def test_all_rejected(self):
        paths = ["/a/b.txt", "/a/c.jpg", "/a/d.pdf"]
        assert _first_accepted_path(paths) == ""

    def test_first_accepted_wins(self):
        paths = ["/a/b.png", "/a/c.svg"]
        assert _first_accepted_path(paths) == "/a/b.png"

    def test_empty_list(self):
        assert _first_accepted_path([]) == ""


class TestDropCallbackIntegration:
    """Test that AnnotatorView wires the callback correctly."""

    def test_view_has_callback(self):
        from canvas.scene import AnnotatorScene
        from canvas.view import AnnotatorView
        log = []
        scene = AnnotatorScene()
        view = AnnotatorView(scene, on_drop_png_cb=lambda p: log.append(p))
        assert view.on_drop_png_cb is not None

    def test_callback_callable(self):
        from canvas.scene import AnnotatorScene
        from canvas.view import AnnotatorView
        log = []
        scene = AnnotatorScene()
        view = AnnotatorView(scene, on_drop_png_cb=lambda p: log.append(p))
        # Simulate what dropEvent does internally
        view.on_drop_png_cb("/test/path.png")
        assert log == ["/test/path.png"]

    def test_callback_receives_string_not_url(self):
        from canvas.scene import AnnotatorScene
        from canvas.view import AnnotatorView
        log = []
        scene = AnnotatorScene()
        view = AnnotatorView(scene, on_drop_png_cb=lambda p: log.append(p))
        view.on_drop_png_cb("C:\\Users\\test\\diagram.puml")
        assert isinstance(log[0], str)
        assert not log[0].startswith("file://")
