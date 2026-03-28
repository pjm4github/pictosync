"""Test bench for the menu system.

Tests:
  - Menu bar has all expected top-level menus (File, Edit, View, Help, Domain)
  - File menu: Open Graphic, Open Project, Save Project, Export PPTX, Exit
  - Edit menu: Undo, Redo, Delete Selected, Settings
  - View menu: Zoom In, Zoom Out, Zoom to Fit, Zoom 100%, Zoom to Region
  - Help menu: Help Contents, Keyboard Shortcuts, About PictoSync
  - Domain menu: Generic action present and checked
  - Undo/Redo actions initially disabled
  - Zoom to Region is checkable
"""
from __future__ import annotations

import pytest

from PyQt6.QtWidgets import QMenuBar


# ── Helpers ──────────────────────────────────────────────────────────────

def _get_menu_titles(mw):
    """Return list of top-level menu titles."""
    menubar = mw.menuBar()
    return [a.text() for a in menubar.actions() if a.menu()]


def _get_menu_by_title(mw, title_fragment: str):
    """Find a menu whose title contains the fragment (case-insensitive)."""
    menubar = mw.menuBar()
    for action in menubar.actions():
        if action.menu() and title_fragment.lower() in action.text().lower():
            return action.menu()
    return None


def _get_action_texts(menu):
    """Return list of action texts in a menu (excluding separators).

    Strips Qt accelerator markers (&) for reliable matching.
    """
    return [a.text().replace("&", "") for a in menu.actions()
            if not a.isSeparator() and a.text()]


# ── Tests ────────────────────────────────────────────────────────────────

class TestMenuBarPresence:
    """Top-level menus exist."""

    def test_has_file_menu(self, main_window):
        assert _get_menu_by_title(main_window, "file") is not None

    def test_has_edit_menu(self, main_window):
        assert _get_menu_by_title(main_window, "edit") is not None

    def test_has_view_menu(self, main_window):
        assert _get_menu_by_title(main_window, "view") is not None

    def test_has_help_menu(self, main_window):
        assert _get_menu_by_title(main_window, "help") is not None

    def test_has_domain_menu(self, main_window):
        assert _get_menu_by_title(main_window, "main") is not None  # "Do&main"

    def test_at_least_four_menus(self, main_window):
        titles = _get_menu_titles(main_window)
        assert len(titles) >= 4


class TestFileMenu:
    """File menu actions."""

    def test_has_open_graphic(self, main_window):
        menu = _get_menu_by_title(main_window, "file")
        actions = _get_action_texts(menu)
        assert any("open graphic" in a.lower() for a in actions)

    def test_has_open_project(self, main_window):
        menu = _get_menu_by_title(main_window, "file")
        actions = _get_action_texts(menu)
        assert any("open project" in a.lower() for a in actions)

    def test_has_save_project(self, main_window):
        menu = _get_menu_by_title(main_window, "file")
        actions = _get_action_texts(menu)
        assert any("save project" in a.lower() for a in actions)

    def test_has_export_pptx(self, main_window):
        menu = _get_menu_by_title(main_window, "file")
        actions = _get_action_texts(menu)
        assert any("powerpoint" in a.lower() or "pptx" in a.lower() for a in actions)

    def test_has_exit(self, main_window):
        menu = _get_menu_by_title(main_window, "file")
        actions = _get_action_texts(menu)
        assert any("exit" in a.lower() or "quit" in a.lower() for a in actions)


class TestEditMenu:
    """Edit menu actions."""

    def test_has_undo(self, main_window):
        menu = _get_menu_by_title(main_window, "edit")
        actions = _get_action_texts(menu)
        assert any("undo" in a.lower() for a in actions)

    def test_has_redo(self, main_window):
        menu = _get_menu_by_title(main_window, "edit")
        actions = _get_action_texts(menu)
        assert any("redo" in a.lower() for a in actions)

    def test_has_delete(self, main_window):
        menu = _get_menu_by_title(main_window, "edit")
        actions = _get_action_texts(menu)
        assert any("delete" in a.lower() for a in actions)

    def test_has_settings(self, main_window):
        menu = _get_menu_by_title(main_window, "edit")
        actions = _get_action_texts(menu)
        assert any("settings" in a.lower() for a in actions)

    def test_undo_initially_disabled(self, main_window):
        assert not main_window._menu_undo_act.isEnabled()

    def test_redo_initially_disabled(self, main_window):
        assert not main_window._menu_redo_act.isEnabled()


class TestViewMenu:
    """View menu actions."""

    def test_has_zoom_in(self, main_window):
        menu = _get_menu_by_title(main_window, "view")
        actions = _get_action_texts(menu)
        assert any("zoom in" in a.lower() for a in actions)

    def test_has_zoom_out(self, main_window):
        menu = _get_menu_by_title(main_window, "view")
        actions = _get_action_texts(menu)
        assert any("zoom out" in a.lower() for a in actions)

    def test_has_zoom_fit(self, main_window):
        menu = _get_menu_by_title(main_window, "view")
        actions = _get_action_texts(menu)
        assert any("fit" in a.lower() for a in actions)

    def test_has_zoom_100(self, main_window):
        menu = _get_menu_by_title(main_window, "view")
        actions = _get_action_texts(menu)
        assert any("100" in a for a in actions)

    def test_has_zoom_region(self, main_window):
        menu = _get_menu_by_title(main_window, "view")
        actions = _get_action_texts(menu)
        assert any("region" in a.lower() for a in actions)

    def test_zoom_region_is_checkable(self, main_window):
        assert main_window._menu_zoom_region_act.isCheckable()


class TestHelpMenu:
    """Help menu actions."""

    def test_has_help_contents(self, main_window):
        menu = _get_menu_by_title(main_window, "help")
        actions = _get_action_texts(menu)
        assert any("help" in a.lower() and "content" in a.lower() for a in actions)

    def test_has_keyboard_shortcuts(self, main_window):
        menu = _get_menu_by_title(main_window, "help")
        actions = _get_action_texts(menu)
        assert any("shortcut" in a.lower() or "keyboard" in a.lower() for a in actions)

    def test_has_about(self, main_window):
        menu = _get_menu_by_title(main_window, "help")
        actions = _get_action_texts(menu)
        assert any("about" in a.lower() for a in actions)


class TestDomainMenu:
    """Domain menu actions."""

    def test_has_generic(self, main_window):
        menu = _get_menu_by_title(main_window, "main")  # "Do&main"
        actions = _get_action_texts(menu)
        assert any("generic" in a.lower() for a in actions)

    def test_generic_is_checked(self, main_window):
        menu = _get_menu_by_title(main_window, "main")
        for action in menu.actions():
            if "generic" in action.text().lower():
                assert action.isChecked()
                break
