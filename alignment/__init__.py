"""
alignment package

OpenCV-based element alignment for snapping canvas elements to PNG visual elements.
"""

from alignment.worker import AlignmentWorker, LineAlignmentWorker

__all__ = ["AlignmentWorker", "LineAlignmentWorker"]
