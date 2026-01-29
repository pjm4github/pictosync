"""
alignment/worker.py

Background worker for OpenCV-based element alignment.
Runs alignment optimization in a separate thread to avoid blocking the UI.
"""

from __future__ import annotations

import traceback
from typing import Dict

from PyQt6.QtCore import QObject, pyqtSignal

from alignment.optimizer import align_element


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
