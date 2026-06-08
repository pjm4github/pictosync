"""
tests/test_clear_overlay_confirm.py

The toolbar "Clear Overlay" (delete) action is destructive — it removes all
annotations and empties the draft JSON — so it must confirm first.
"""
from __future__ import annotations

import json

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


def _ann_count(mw):
    return len(json.loads(mw.draft.get_json_text()).get("annotations", []))


def test_clear_overlay_cancelled_keeps_everything(main_window, qapp, monkeypatch):
    mw = main_window
    _add_item(mw)
    qapp.processEvents()
    assert _ann_count(mw) == 1
    monkeypatch.setattr(QMessageBox, "question",
                        lambda *a, **k: QMessageBox.StandardButton.No)
    mw.clear_overlay()
    qapp.processEvents()
    assert _ann_count(mw) == 1  # nothing deleted


def test_clear_overlay_confirmed_clears(main_window, qapp, monkeypatch):
    mw = main_window
    _add_item(mw)
    qapp.processEvents()
    monkeypatch.setattr(QMessageBox, "question",
                        lambda *a, **k: QMessageBox.StandardButton.Yes)
    mw.clear_overlay()
    qapp.processEvents()
    assert _ann_count(mw) == 0  # cleared


def test_clear_overlay_empty_does_not_prompt(main_window, qapp, monkeypatch):
    mw = main_window
    mw._draft_data = {"version": "draft-1", "image": {}, "annotations": []}
    mw._link_enabled = True
    mw._rebuild_id_index()
    calls = {"n": 0}

    def _q(*a, **k):
        calls["n"] += 1
        return QMessageBox.StandardButton.Yes

    monkeypatch.setattr(QMessageBox, "question", _q)
    mw.clear_overlay()
    qapp.processEvents()
    assert calls["n"] == 0  # nothing to clear → no confirmation shown
