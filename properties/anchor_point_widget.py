"""
properties/anchor_point_widget.py

A 3x3 radio-button grid for selecting text-box anchor placement
relative to the line/curve anchor point.

Columns: left, center, right  (text_anchor)
Rows:    top, middle, bottom   (text_anchor_v)

The selected button encodes the combination, e.g. ("left", "top").
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtWidgets import (
    QButtonGroup,
    QGridLayout,
    QRadioButton,
    QSizePolicy,
    QStyleFactory,
    QWidget,
)


# Mapping: (row, col) → (text_anchor_v, text_anchor)
_POSITIONS = {
    (0, 0): ("top", "left"),
    (0, 1): ("top", "center"),
    (0, 2): ("top", "right"),
    (1, 0): ("middle", "left"),
    (1, 1): ("middle", "center"),
    (1, 2): ("middle", "right"),
    (2, 0): ("bottom", "left"),
    (2, 1): ("bottom", "center"),
    (2, 2): ("bottom", "right"),
}

# Reverse: (text_anchor_v, text_anchor) → linear id
_POS_TO_ID = {v: row * 3 + col for (row, col), v in _POSITIONS.items()}

# Stylesheet: 5×5 px indicator with 0 padding, Fusion style for CSS control.
_BTN_STYLE = """
QRadioButton {
    spacing: 0px;
    padding: 0px;
    margin: 0px;
}
QRadioButton::indicator {
    width: 5px;
    height: 5px;
    border-radius: 0px;
    border: 1px solid #888;
    background: #ccc;
}
QRadioButton::indicator:checked {
    background: #ff8800;
    border: 1px solid #cc6600;
}
QRadioButton::indicator:hover {
    border: 1px solid #555;
}
"""


class _TinyRadio(QRadioButton):
    """Radio button that reports a fixed 7×7 size hint (5px dot + 1px border each side)."""

    def sizeHint(self) -> QSize:
        return QSize(7, 7)

    def minimumSizeHint(self) -> QSize:
        return QSize(7, 7)


class AnchorPointWidget(QWidget):
    """3×3 radio-button grid for text-box anchor placement.

    Max size 70×70 px.  Each dot is 5×5 px with 3 px spacing.

    Signals:
        anchor_changed(str, str): Emitted as (text_anchor, text_anchor_v)
            when the user clicks a different cell.
    """

    anchor_changed = pyqtSignal(str, str)  # (h_anchor, v_anchor)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setMaximumSize(70, 70)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Fusion style honours ::indicator CSS; native Windows style ignores it.
        _fusion = QStyleFactory.create("Fusion")

        self._group = QButtonGroup(self)
        layout = QGridLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setHorizontalSpacing(3)
        layout.setVerticalSpacing(3)

        self._buttons: dict[int, _TinyRadio] = {}
        for (row, col), (v_anchor, h_anchor) in _POSITIONS.items():
            btn = _TinyRadio()
            btn.setToolTip(f"{v_anchor} {h_anchor}")
            btn.setStyleSheet(_BTN_STYLE)
            btn.setFixedSize(7, 7)
            if _fusion:
                btn.setStyle(_fusion)
            btn_id = row * 3 + col
            self._group.addButton(btn, btn_id)
            layout.addWidget(btn, row, col, Qt.AlignmentFlag.AlignCenter)
            self._buttons[btn_id] = btn

        # Default: middle-center (id=4)
        self._buttons[4].setChecked(True)

        self._group.idClicked.connect(self._on_clicked)

    def _on_clicked(self, btn_id: int) -> None:
        row, col = divmod(btn_id, 3)
        v_anchor, h_anchor = _POSITIONS[(row, col)]
        self.anchor_changed.emit(h_anchor, v_anchor)

    def set_anchor(self, h_anchor: str, v_anchor: str) -> None:
        """Programmatically select the cell matching the given anchors.

        Args:
            h_anchor: "left", "center", or "right".
            v_anchor: "top", "middle", or "bottom".
        """
        btn_id = _POS_TO_ID.get((v_anchor, h_anchor), 4)
        self._group.blockSignals(True)
        self._buttons[btn_id].setChecked(True)
        self._group.blockSignals(False)

    def current_anchor(self) -> tuple[str, str]:
        """Return the currently selected (text_anchor, text_anchor_v)."""
        btn_id = self._group.checkedId()
        if btn_id < 0:
            return ("center", "middle")
        row, col = divmod(btn_id, 3)
        v_anchor, h_anchor = _POSITIONS[(row, col)]
        return (h_anchor, v_anchor)
