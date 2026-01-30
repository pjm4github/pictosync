"""
alignment/worker.py

Background worker for OpenCV-based element alignment.
Runs alignment optimization in a separate thread to avoid blocking the UI.
"""

from __future__ import annotations

import traceback
from typing import Dict

from PyQt6.QtCore import QObject, pyqtSignal

from alignment.optimizer import align_element, align_line_element


class AlignmentWorker(QObject):
    """
    Background worker that aligns a canvas element to match the PNG visual.

    Signals:
        progress(int, str): Emitted with iteration number and status message
        finished(dict): Emitted with optimized geometry on success
        failed(str): Emitted with error message on failure
    """

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(self, png_path: str, geom: Dict[str, float], kind: str,
                 pen_color: str = "#000000", pen_width: int = 2):
        """
        Initialize the alignment worker.

        Args:
            png_path: Path to the PNG file
            geom: Current geometry dict {x, y, w, h, radius?}
            kind: Shape type - "rect", "roundedrect", or "ellipse"
            pen_color: Hex color of the element's pen/stroke
            pen_width: Current pen/stroke width
        """
        super().__init__()
        self.png_path = png_path
        self.geom = geom
        self.kind = kind
        self.pen_color = pen_color
        self.pen_width = pen_width

    def run(self):
        """Execute the alignment optimization."""
        try:
            def on_progress(iteration: int, message: str):
                self.progress.emit(iteration, message)

            result = align_element(
                self.png_path,
                self.geom,
                self.kind,
                pen_color=self.pen_color,
                pen_width=self.pen_width,
                progress_callback=on_progress
            )

            self.finished.emit(result)

        except Exception as e:
            msg = f"{e}\n\n{traceback.format_exc()}"
            self.failed.emit(msg)


class LineAlignmentWorker(QObject):
    """
    Background worker that aligns a line element to match the PNG visual.

    Detects line endpoints, angle, length, and arrowheads.
    Supports dashed lines by merging collinear segments.
    Uses text matching from meta.note or meta.label to find the initial center.

    Signals:
        progress(int, str): Emitted with iteration number and status message
        finished(dict): Emitted with optimized geometry on success
        failed(str): Emitted with error message on failure
    """

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(self, png_path: str, geom: Dict[str, float],
                 pen_color: str = "#000000", pen_width: int = 2,
                 note_text: str = "", label_text: str = ""):
        """
        Initialize the line alignment worker.

        Args:
            png_path: Path to the PNG file
            geom: Current geometry dict {x1, y1, x2, y2}
            pen_color: Hex color of the line's pen/stroke
            pen_width: Current pen/stroke width
            note_text: Text from meta.note for text matching in PNG
            label_text: Text from meta.label for text matching in PNG
        """
        super().__init__()
        self.png_path = png_path
        self.geom = geom
        self.pen_color = pen_color
        self.pen_width = pen_width
        self.note_text = note_text
        self.label_text = label_text

    def run(self):
        """Execute the line alignment optimization."""
        try:
            def on_progress(iteration: int, message: str):
                self.progress.emit(iteration, message)

            result = align_line_element(
                self.png_path,
                self.geom,
                pen_color=self.pen_color,
                pen_width=self.pen_width,
                note_text=self.note_text,
                label_text=self.label_text,
                progress_callback=on_progress
            )

            self.finished.emit(result)

        except Exception as e:
            msg = f"{e}\n\n{traceback.format_exc()}"
            self.failed.emit(msg)
