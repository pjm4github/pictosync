"""Test move-then-ungroup-then-drag on a flow/activity diagram (test_flow.puml).

Requires a GUI environment (not headless).  Run with:
    .venv/Scripts/python -m pytest tests/test_flow_ungroup.py -v
"""
from __future__ import annotations

import json
import os
import sys

import pytest
from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QApplication

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from settings import SettingsManager


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def qapp():
    """Provide a single QApplication for the entire test session."""
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


@pytest.fixture()
def main_window(qapp):
    """Create a fresh MainWindow for each test."""
    from main import MainWindow
    sm = SettingsManager()
    mw = MainWindow(sm)
    mw.show()
    qapp.processEvents()
    yield mw
    mw.close()


@pytest.fixture()
def linked_flow(main_window, qapp):
    """Import test_flow.puml and link items, returning (main_window, groups)."""
    puml_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "test_data", "PUML", "test_flow.puml")
    )
    if not os.path.exists(puml_path):
        pytest.skip(f"Test fixture not found: {puml_path}")

    main_window._import_puml(puml_path)
    main_window.import_draft_and_link()
    qapp.processEvents()

    from canvas.items import MetaGroupItem
    groups = [i for i in main_window.scene.items() if isinstance(i, MetaGroupItem)]
    assert len(groups) > 0, "No groups found after import"
    return main_window, groups


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_index_integrity(mw):
    """Assert every _id_to_index entry points to the correct annotation."""
    anns = mw._draft_data["annotations"]
    for aid, idx in mw._id_to_index.items():
        assert idx < len(anns), f"{aid}: idx={idx} out of bounds (len={len(anns)})"
        assert anns[idx].get("id") == aid, (
            f"{aid}: idx={idx} points to {anns[idx].get('id')}"
        )


def _check_no_duplicate_ids(mw):
    """Assert no duplicate annotation IDs exist."""
    all_ids = [
        a.get("id") for a in mw._draft_data["annotations"]
        if isinstance(a, dict)
    ]
    assert len(all_ids) == len(set(all_ids)), (
        f"Duplicate IDs: {[x for x in all_ids if all_ids.count(x) > 1]}"
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestFlowMoveUngroupDrag:
    """Move a group, ungroup it, then drag a child — on a flow diagram."""

    def test_move_group_updates_geom(self, linked_flow, qapp):
        """Moving a group should update its geom in the JSON."""
        mw, groups = linked_flow
        group = groups[0]
        group_id = group.ann_id

        idx = mw._id_to_index.get(group_id)
        assert idx is not None, f"{group_id} not in _id_to_index"

        mw.scene.clearSelection()
        group.setSelected(True)
        qapp.processEvents()

        mw.scene._mouse_down_in_select = True
        old_pos = group.pos()
        group.setPos(old_pos.x() + 20, old_pos.y() + 20)
        qapp.processEvents()
        mw.scene._mouse_down_in_select = False
        mw.draft.unlock_scroll()
        qapp.processEvents()

        _check_index_integrity(mw)

    def test_move_then_ungroup_no_duplicates(self, linked_flow, qapp):
        """Moving a group then ungrouping should not create duplicate IDs."""
        mw, groups = linked_flow
        group = groups[0]

        # Step 1: Move the group
        mw.scene.clearSelection()
        group.setSelected(True)
        qapp.processEvents()
        mw.scene._mouse_down_in_select = True
        old_pos = group.pos()
        group.setPos(old_pos.x() + 20, old_pos.y() + 20)
        qapp.processEvents()
        mw.scene._mouse_down_in_select = False
        mw.draft.unlock_scroll()
        qapp.processEvents()

        # Step 2: Ungroup
        group.setSelected(True)
        qapp.processEvents()
        mw._do_ungroup_item(group)
        qapp.processEvents()

        _check_no_duplicate_ids(mw)
        _check_index_integrity(mw)

    def test_child_on_change_after_move_ungroup(self, linked_flow, qapp):
        """Children should retain on_change and have no parent after ungroup."""
        mw, groups = linked_flow
        group = groups[0]
        children = list(group.member_items())

        # Move then ungroup
        mw.scene.clearSelection()
        group.setSelected(True)
        qapp.processEvents()
        mw.scene._mouse_down_in_select = True
        old_pos = group.pos()
        group.setPos(old_pos.x() + 20, old_pos.y() + 20)
        qapp.processEvents()
        mw.scene._mouse_down_in_select = False
        mw.draft.unlock_scroll()
        qapp.processEvents()

        group.setSelected(True)
        qapp.processEvents()
        mw._do_ungroup_item(group)
        qapp.processEvents()

        for child in children:
            assert child.on_change is not None, (
                f"{child.ann_id}: on_change is None after ungroup"
            )
            assert child.parentItem() is None, (
                f"{child.ann_id}: still has a parent after ungroup"
            )

    def test_drag_child_after_move_ungroup(self, linked_flow, qapp):
        """Dragging an ungrouped child should update its geom in JSON."""
        from canvas.items import MetaRectItem

        mw, groups = linked_flow
        group = groups[0]
        children = list(group.member_items())

        # Move then ungroup
        mw.scene.clearSelection()
        group.setSelected(True)
        qapp.processEvents()
        mw.scene._mouse_down_in_select = True
        old_pos = group.pos()
        group.setPos(old_pos.x() + 20, old_pos.y() + 20)
        qapp.processEvents()
        mw.scene._mouse_down_in_select = False
        mw.draft.unlock_scroll()
        qapp.processEvents()

        group.setSelected(True)
        qapp.processEvents()
        mw._do_ungroup_item(group)
        qapp.processEvents()

        # Find a rect child to drag
        rects = [c for c in children if isinstance(c, MetaRectItem)]
        assert len(rects) > 0, "No rect children in group"

        target = rects[0]
        child_id = target.ann_id
        idx = mw._id_to_index.get(child_id)
        assert idx is not None, f"{child_id} not in _id_to_index"

        geom_before = dict(mw._draft_data["annotations"][idx].get("geom", {}))

        # Select and drag child
        mw.scene.clearSelection()
        target.setSelected(True)
        qapp.processEvents()
        mw.scene._mouse_down_in_select = True

        old_pos = target.pos()
        for step in range(1, 6):
            target.setPos(old_pos.x() + step, old_pos.y() + step)
            qapp.processEvents()

        geom_after = mw._draft_data["annotations"][idx].get("geom", {})
        assert geom_after != geom_before, (
            f"Geom should have changed: {geom_before} -> {geom_after}"
        )

        # Editor JSON should agree
        editor_data = json.loads(mw.draft.get_json_text())
        editor_ann = next(
            (a for a in editor_data["annotations"] if a.get("id") == child_id),
            None,
        )
        assert editor_ann is not None, f"{child_id} missing from editor JSON"
        assert editor_ann.get("geom") == geom_after, (
            f"Editor geom mismatch: {editor_ann.get('geom')} vs {geom_after}"
        )

        # Clean up
        mw.scene._mouse_down_in_select = False
        mw.draft.unlock_scroll()

        _check_no_duplicate_ids(mw)
        _check_index_integrity(mw)
