"""
tests/test_unsaved_guard.py

Unsaved-work guard: closing the window, opening a project, or opening a new
graphic must warn (Save / Discard / Cancel) when there are unsaved changes.
"""
from __future__ import annotations

from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QMessageBox

from canvas.items import MetaRectItem


def _add_item(mw):
    mw._draft_data = {"version": "draft-1", "image": {}, "annotations": []}
    mw._link_enabled = True
    mw._rebuild_id_index()
    r = MetaRectItem(0, 0, 100, 50, mw._new_ann_id(), mw._on_scene_item_changed)
    mw.scene.addItem(r)
    mw._on_new_scene_item(r)
    return r


def test_clean_window_has_no_unsaved_work(main_window, qapp):
    mw = main_window
    assert mw._has_unsaved_work() is False


def test_adding_item_marks_unsaved(main_window, qapp):
    mw = main_window
    _add_item(mw)
    qapp.processEvents()
    assert mw._has_unsaved_work() is True


def test_mark_saved_clears_unsaved(main_window, qapp):
    mw = main_window
    _add_item(mw)
    qapp.processEvents()
    mw._mark_saved()
    assert mw._has_unsaved_work() is False


def test_close_clean_accepts_without_prompt(main_window, qapp, monkeypatch):
    mw = main_window
    called = {"n": 0}
    monkeypatch.setattr(QMessageBox, "warning",
                        lambda *a, **k: called.__setitem__("n", called["n"] + 1))
    ev = QCloseEvent()
    mw.closeEvent(ev)
    assert called["n"] == 0       # nothing to lose → no prompt
    assert ev.isAccepted() is True


def test_close_dirty_cancel_keeps_window_open(main_window, qapp, monkeypatch):
    mw = main_window
    _add_item(mw)
    qapp.processEvents()
    monkeypatch.setattr(QMessageBox, "warning",
                        lambda *a, **k: QMessageBox.StandardButton.Cancel)
    ev = QCloseEvent()
    mw.closeEvent(ev)
    assert ev.isAccepted() is False   # cancel → don't close


def test_close_dirty_discard_closes(main_window, qapp, monkeypatch):
    mw = main_window
    _add_item(mw)
    qapp.processEvents()
    monkeypatch.setattr(QMessageBox, "warning",
                        lambda *a, **k: QMessageBox.StandardButton.Discard)
    ev = QCloseEvent()
    mw.closeEvent(ev)
    assert ev.isAccepted() is True    # discard → close


def test_close_dirty_save_then_close(main_window, qapp, monkeypatch):
    mw = main_window
    _add_item(mw)
    qapp.processEvents()
    monkeypatch.setattr(QMessageBox, "warning",
                        lambda *a, **k: QMessageBox.StandardButton.Save)
    # Save succeeds → safe to close.
    monkeypatch.setattr(mw, "save_project_dialog", lambda *a, **k: True)
    ev = QCloseEvent()
    mw.closeEvent(ev)
    assert ev.isAccepted() is True


def test_close_dirty_save_cancelled_aborts(main_window, qapp, monkeypatch):
    mw = main_window
    _add_item(mw)
    qapp.processEvents()
    monkeypatch.setattr(QMessageBox, "warning",
                        lambda *a, **k: QMessageBox.StandardButton.Save)
    # User cancelled the Save dialog → abort the close.
    monkeypatch.setattr(mw, "save_project_dialog", lambda *a, **k: False)
    ev = QCloseEvent()
    mw.closeEvent(ev)
    assert ev.isAccepted() is False
