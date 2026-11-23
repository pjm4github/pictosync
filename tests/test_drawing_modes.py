"""Test bench for drawing mode switching.

Tests:
  - All 15 modes can be set via set_mode
  - Mode sets the correct action as checked
  - Only one action is checked at a time
  - Scene receives the mode change
  - SELECT mode enables RubberBandDrag, others disable it
  - Mode revert after item creation (non-sticky)
  - Sticky mode stays in current tool
  - Exit sticky via _exit_sticky_mode
  - Curve/orthocurve variant switching
  - Seqblock type switching
  - set_mode(from_item_created=True) preserves selection
"""
from __future__ import annotations

import pytest

from models import Mode


# ── Tests ────────────────────────────────────────────────────────────────

ALL_MODES = [
    Mode.SELECT, Mode.RECT, Mode.ROUNDEDRECT, Mode.ELLIPSE,
    Mode.LINE, Mode.TEXT, Mode.HEXAGON, Mode.CYLINDER,
    Mode.BLOCKARROW, Mode.ISOCUBE, Mode.POLYGON,
    Mode.CURVE, Mode.ORTHOCURVE, Mode.SEQBLOCK, Mode.PORT,
]

DRAWING_MODES = [m for m in ALL_MODES if m != Mode.SELECT]


class TestSetMode:
    """set_mode changes the active mode."""

    @pytest.mark.parametrize("mode", ALL_MODES)
    def test_scene_receives_mode(self, main_window, mode):
        mw = main_window
        mw.set_mode(mode)
        assert mw.scene.mode == mode

    @pytest.mark.parametrize("mode", ALL_MODES)
    def test_exactly_one_action_checked(self, main_window, mode):
        mw = main_window
        mw.set_mode(mode)
        checked = [a for a in mw.mode_actions if a.isChecked()]
        assert len(checked) == 1, \
            f"Expected 1 checked action for mode {mode}, got {len(checked)}"

    @pytest.mark.parametrize("mode", ALL_MODES)
    def test_correct_action_checked(self, main_window, mode):
        mw = main_window
        mw.set_mode(mode)
        mapping = {
            Mode.SELECT: mw.act_select,
            Mode.RECT: mw.act_rect,
            Mode.ROUNDEDRECT: mw.act_rrect,
            Mode.ELLIPSE: mw.act_ellipse,
            Mode.LINE: mw.act_line,
            Mode.TEXT: mw.act_text,
            Mode.HEXAGON: mw.act_hexagon,
            Mode.CYLINDER: mw.act_cylinder,
            Mode.BLOCKARROW: mw.act_blockarrow,
            Mode.ISOCUBE: mw.act_isocube,
            Mode.POLYGON: mw.act_polygon,
            Mode.CURVE: mw.act_curve,
            Mode.ORTHOCURVE: mw.act_curve,  # shares action
            Mode.SEQBLOCK: mw.act_seqblock,
            Mode.PORT: mw.act_port,
        }
        assert mapping[mode].isChecked()


class TestSelectModeDrag:
    """SELECT mode enables rubber-band drag, others don't."""

    def test_select_enables_rubberband(self, main_window):
        from PyQt6.QtWidgets import QGraphicsView
        mw = main_window
        mw.set_mode(Mode.SELECT)
        assert mw.view.dragMode() == QGraphicsView.DragMode.RubberBandDrag

    @pytest.mark.parametrize("mode", DRAWING_MODES)
    def test_drawing_mode_disables_rubberband(self, main_window, mode):
        from PyQt6.QtWidgets import QGraphicsView
        mw = main_window
        mw.set_mode(mode)
        assert mw.view.dragMode() == QGraphicsView.DragMode.NoDrag


class TestModeRevertAfterCreation:
    """After item creation, mode reverts to SELECT (non-sticky)."""

    def test_revert_to_select(self, main_window):
        mw = main_window
        mw._sticky_mode = False
        mw.set_mode(Mode.RECT)
        assert mw.scene.mode == Mode.RECT
        mw._on_item_created()
        assert mw.scene.mode == Mode.SELECT
        assert mw.act_select.isChecked()

    def test_revert_preserves_selection_flag(self, main_window):
        """from_item_created=True should not call clearSelection."""
        from canvas.items import MetaRectItem
        mw = main_window
        item = MetaRectItem(50, 50, 100, 60, "sel_test", None)
        mw.scene.addItem(item)
        item.setSelected(True)
        mw.set_mode(Mode.SELECT, from_item_created=True)
        # Item should still be selected
        assert item.isSelected()


class TestStickyMode:
    """Sticky mode keeps the drawing tool active."""

    def test_sticky_prevents_revert(self, main_window):
        mw = main_window
        mw._sticky_mode = True
        mw.set_mode(Mode.ELLIPSE)
        mw._on_item_created()
        # Should stay in ELLIPSE mode
        assert mw.scene.mode == Mode.ELLIPSE

    def test_exit_sticky_returns_to_select(self, main_window):
        mw = main_window
        mw._sticky_mode = True
        mw.set_mode(Mode.LINE)
        mw._exit_sticky_mode()
        assert mw._sticky_mode is False
        assert mw.scene.mode == Mode.SELECT

    def test_select_clears_sticky(self, main_window):
        mw = main_window
        mw._sticky_mode = True
        mw._on_mode_action_triggered(Mode.SELECT)
        assert mw._sticky_mode is False


class TestCurveVariant:
    """Curve/orthocurve split button switching."""

    def test_set_curve_variant(self, main_window):
        mw = main_window
        mw._set_curve_variant(Mode.CURVE)
        assert mw._curve_variant == Mode.CURVE
        assert mw.scene.mode == Mode.CURVE

    def test_set_ortho_variant(self, main_window):
        mw = main_window
        mw._set_curve_variant(Mode.ORTHOCURVE)
        assert mw._curve_variant == Mode.ORTHOCURVE
        assert mw.scene.mode == Mode.ORTHOCURVE

    def test_curve_action_checked(self, main_window):
        mw = main_window
        mw._set_curve_variant(Mode.CURVE)
        assert mw.act_curve.isChecked()

    def test_variant_menu_checked(self, main_window):
        mw = main_window
        mw._set_curve_variant(Mode.CURVE)
        assert mw._act_curve_free.isChecked()
        assert not mw._act_curve_ortho.isChecked()
        mw._set_curve_variant(Mode.ORTHOCURVE)
        assert not mw._act_curve_free.isChecked()
        assert mw._act_curve_ortho.isChecked()


class TestSeqBlockType:
    """Seqblock type split button switching."""

    @pytest.mark.parametrize("btype", ["alt", "loop", "opt", "critical", "break", "par"])
    def test_set_seqblock_type(self, main_window, btype):
        mw = main_window
        mw._set_seqblock_type(btype)
        assert mw._seqblock_type == btype
        assert mw.scene._seqblock_type == btype
        assert mw.scene.mode == Mode.SEQBLOCK

    def test_seqblock_menu_checked(self, main_window):
        mw = main_window
        mw._set_seqblock_type("loop")
        for bt, act in mw._seqblock_menu_actions.items():
            if bt == "loop":
                assert act.isChecked()
            else:
                assert not act.isChecked()


class TestModeTransitions:
    """Switching between modes works correctly."""

    def test_rect_then_select(self, main_window):
        mw = main_window
        mw.set_mode(Mode.RECT)
        assert mw.scene.mode == Mode.RECT
        mw.set_mode(Mode.SELECT)
        assert mw.scene.mode == Mode.SELECT

    def test_multiple_mode_switches(self, main_window):
        mw = main_window
        for mode in [Mode.RECT, Mode.ELLIPSE, Mode.LINE, Mode.TEXT, Mode.SELECT]:
            mw.set_mode(mode)
            assert mw.scene.mode == mode

    def test_drawing_to_drawing(self, main_window):
        mw = main_window
        mw.set_mode(Mode.RECT)
        mw.set_mode(Mode.HEXAGON)
        assert mw.scene.mode == Mode.HEXAGON
        assert mw.act_hexagon.isChecked()
        assert not mw.act_rect.isChecked()
