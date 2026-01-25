"""
canvas package

PyQt6 graphics items, scene, and view for diagram annotation.
"""

from canvas.mixins import LinkedMixin, MetaMixin
from canvas.items import (
    MetaRectItem,
    MetaRoundedRectItem,
    MetaEllipseItem,
    MetaLineItem,
    MetaTextItem,
)
from canvas.scene import AnnotatorScene
from canvas.view import AnnotatorView

__all__ = [
    "LinkedMixin",
    "MetaMixin",
    "MetaRectItem",
    "MetaRoundedRectItem",
    "MetaEllipseItem",
    "MetaLineItem",
    "MetaTextItem",
    "AnnotatorScene",
    "AnnotatorView",
]
