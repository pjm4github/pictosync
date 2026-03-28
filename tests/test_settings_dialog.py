"""Test bench for SettingsDialog.

Tests:
  - Dialog creation and tab count
  - Tab names match expected
  - Layer radio buttons present and switchable
  - General tab: theme combo, workspace path
  - Editor tab: font size spinbox
  - Canvas tab: handle size spinbox
  - Item Defaults tab: per-kind widget creation
  - OK/Cancel/Apply/Restore button existence
  - Dialog accept/reject behavior
"""
from __future__ import annotations

import pytest

from settings import SettingsManager
from settings_dialog import SettingsDialog


# ── Helpers ──────────────────────────────────────────────────────────────

@pytest.fixture
def dialog(qapp):
    """Create a SettingsDialog for testing."""
    sm = SettingsManager()
    dlg = SettingsDialog(sm)
    yield dlg
    dlg.close()


# ── Tests ────────────────────────────────────────────────────────────────

class TestDialogCreation:

    def test_dialog_creates(self, dialog):
        assert dialog is not None

    def test_dialog_is_dialog(self, dialog):
        from PyQt6.QtWidgets import QDialog
        assert isinstance(dialog, QDialog)

    def test_dialog_has_title(self, dialog):
        assert dialog.windowTitle() != ""

    def test_dialog_has_tabs(self, dialog):
        assert dialog.tabs.count() >= 5


class TestTabNames:

    def test_expected_tabs_present(self, dialog):
        tab_names = [dialog.tabs.tabText(i) for i in range(dialog.tabs.count())]
        assert "General" in tab_names
        assert "JSON Editor" in tab_names
        assert "Canvas" in tab_names
        assert "Alignment" in tab_names
        assert "Item Defaults" in tab_names

    def test_general_is_first(self, dialog):
        assert dialog.tabs.tabText(0) == "General"


class TestLayerRadioButtons:

    def test_layer_button_group_exists(self, dialog):
        assert hasattr(dialog, "_layer_btn_group")
        assert dialog._layer_btn_group is not None

    def test_default_layer_is_user(self, dialog):
        assert dialog._active_layer == "user"

    def test_builtin_radio_exists(self, dialog):
        assert hasattr(dialog, "_rb_builtin")


class TestGeneralTab:

    def test_theme_combo_exists(self, dialog):
        assert hasattr(dialog, "theme_combo")
        assert dialog.theme_combo.count() >= 1

    def test_workspace_dir_edit_exists(self, dialog):
        assert hasattr(dialog, "workspace_dir_edit")

    def test_gemini_model_list_exists(self, dialog):
        assert hasattr(dialog, "gemini_model_list")

    def test_gemini_default_combo_exists(self, dialog):
        assert hasattr(dialog, "gemini_default_combo")


class TestEditorTab:

    def test_font_size_spinbox(self, dialog):
        assert hasattr(dialog, "editor_font_size")
        assert dialog.editor_font_size.value() > 0

    def test_font_family_edit(self, dialog):
        assert hasattr(dialog, "editor_font_family")

    def test_fold_width_spinbox(self, dialog):
        assert hasattr(dialog, "editor_fold_width")


class TestCanvasTab:

    def test_handle_size_spinbox(self, dialog):
        assert hasattr(dialog, "canvas_handle_size")
        assert dialog.canvas_handle_size.value() > 0

    def test_hit_distance_spinbox(self, dialog):
        assert hasattr(dialog, "canvas_hit_distance")

    def test_dash_length_spinbox(self, dialog):
        assert hasattr(dialog, "canvas_dash_length")


class TestItemDefaultsTab:

    def test_item_kind_widgets_created(self, dialog):
        assert hasattr(dialog, "_item_kind_widgets")
        assert len(dialog._item_kind_widgets) > 0

    def test_rect_defaults_exist(self, dialog):
        assert "rect" in dialog._item_kind_widgets

    def test_line_defaults_exist(self, dialog):
        assert "line" in dialog._item_kind_widgets

    def test_kind_widget_has_pen_color(self, dialog):
        rect_widgets = dialog._item_kind_widgets.get("rect", {})
        assert "pen_color" in rect_widgets

    def test_all_standard_kinds_present(self, dialog):
        expected = {"rect", "roundedrect", "ellipse", "line", "text"}
        actual = set(dialog._item_kind_widgets.keys())
        missing = expected - actual
        assert not missing, f"Missing kind defaults: {missing}"


class TestButtonBox:

    def test_ok_button(self, dialog):
        from PyQt6.QtWidgets import QDialogButtonBox
        btns = dialog.findChild(QDialogButtonBox)
        assert btns is not None
        assert btns.button(QDialogButtonBox.StandardButton.Ok) is not None

    def test_cancel_button(self, dialog):
        from PyQt6.QtWidgets import QDialogButtonBox
        btns = dialog.findChild(QDialogButtonBox)
        assert btns.button(QDialogButtonBox.StandardButton.Cancel) is not None

    def test_apply_button(self, dialog):
        from PyQt6.QtWidgets import QDialogButtonBox
        btns = dialog.findChild(QDialogButtonBox)
        assert btns.button(QDialogButtonBox.StandardButton.Apply) is not None

    def test_restore_button(self, dialog):
        from PyQt6.QtWidgets import QDialogButtonBox
        btns = dialog.findChild(QDialogButtonBox)
        assert btns.button(QDialogButtonBox.StandardButton.RestoreDefaults) is not None


class TestDialogActions:

    def test_on_ok_accepts(self, dialog):
        dialog._on_ok()
        from PyQt6.QtWidgets import QDialog
        assert dialog.result() == QDialog.DialogCode.Accepted

    def test_on_cancel_rejects(self, dialog):
        dialog._on_cancel()
        from PyQt6.QtWidgets import QDialog
        assert dialog.result() == QDialog.DialogCode.Rejected

    def test_on_apply_no_crash(self, dialog):
        dialog._on_apply()

    def test_on_restore_defaults_no_crash(self, dialog):
        dialog._on_restore_defaults()
