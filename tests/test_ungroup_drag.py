"""Test that ungrouping items and then dragging works correctly.

Requires a GUI environment (not headless).  Run with:
    .venv/Scripts/python -m pytest tests/test_ungroup_drag.py -v
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
def linked_scene_with_groups(main_window, qapp):
    """Import a PUML file that has groups, returning (main_window, groups)."""
    puml_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "test", "PUML", "figure1.puml")
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
# Tests
# ---------------------------------------------------------------------------

class TestUngroupThenDrag:
    """After ungrouping, items should still update JSON correctly when dragged."""

    def test_ungroup_preserves_index_integrity(self, linked_scene_with_groups, qapp):
        """Ungrouping should maintain consistent _id_to_index mapping."""
        mw, groups = linked_scene_with_groups
        group = groups[0]
        children = list(group.member_items())

        count_before = len(mw._draft_data["annotations"])

        group.setSelected(True)
        qapp.processEvents()
        mw._do_ungroup_item(group)
        qapp.processEvents()

        count_after = len(mw._draft_data["annotations"])
        # Removed 1 group, added N children
        assert count_after == count_before - 1 + len(children)

        # Index integrity: every entry should point to the correct record
        anns = mw._draft_data["annotations"]
        for aid, idx in mw._id_to_index.items():
            assert idx < len(anns), f"{aid}: idx={idx} out of bounds"
            assert anns[idx].get("id") == aid, (
                f"{aid}: idx={idx} points to {anns[idx].get('id')}"
            )

    def test_no_duplicate_ids_after_ungroup(self, linked_scene_with_groups, qapp):
        """Ungrouping should not create duplicate annotation IDs."""
        mw, groups = linked_scene_with_groups

        # Ungroup all groups
        for g in groups:
            g.setSelected(True)
            qapp.processEvents()
            mw._do_ungroup_item(g)
            qapp.processEvents()
            g.setSelected(False)

        all_ids = [
            a.get("id") for a in mw._draft_data["annotations"]
            if isinstance(a, dict)
        ]
        assert len(all_ids) == len(set(all_ids)), (
            f"Duplicate IDs found: "
            f"{[x for x in all_ids if all_ids.count(x) > 1]}"
        )

    def test_child_has_on_change_after_ungroup(self, linked_scene_with_groups, qapp):
        """Ungrouped children should retain their on_change callback."""
        mw, groups = linked_scene_with_groups
        group = groups[0]
        children = list(group.member_items())

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

    def test_geom_updates_during_drag_after_ungroup(self, linked_scene_with_groups, qapp):
        """Dragging an ungrouped child should update its geom in the JSON."""
        from canvas.items import MetaRectItem

        mw, groups = linked_scene_with_groups
        group = groups[0]
        children = list(group.member_items())

        group.setSelected(True)
        qapp.processEvents()
        mw._do_ungroup_item(group)
        qapp.processEvents()

        # Find a rect child to drag
        rects = [c for c in children if isinstance(c, MetaRectItem)]
        assert len(rects) > 0, "No rect children in group"

        target = rects[0]
        ann_id = target.ann_id
        idx = mw._id_to_index.get(ann_id)
        assert idx is not None, f"{ann_id} not in _id_to_index"

        # Read geom before drag
        geom_before = dict(mw._draft_data["annotations"][idx].get("geom", {}))

        # Select and drag
        mw.scene.clearSelection()
        target.setSelected(True)
        qapp.processEvents()
        mw.scene._mouse_down_in_select = True

        old_pos = target.pos()
        target.setPos(old_pos.x() + 5, old_pos.y() + 5)
        qapp.processEvents()

        # Read geom after drag
        geom_after = mw._draft_data["annotations"][idx].get("geom", {})
        assert geom_after != geom_before, (
            f"Geom should have changed: {geom_before} -> {geom_after}"
        )

        # Clean up
        mw.scene._mouse_down_in_select = False
        mw.draft.unlock_scroll()

    def test_no_duplicates_after_move_then_ungroup(self, linked_scene_with_groups, qapp):
        """Moving a group before ungrouping should not create duplicate IDs.

        This is the exact scenario that triggered the original bug:
        removeFromGroup() adjusts child positions when the group has been
        moved, firing ItemPositionHasChanged which — without the
        _syncing_from_json guard — created duplicate annotation records.
        """
        from canvas.items import MetaRectItem

        mw, groups = linked_scene_with_groups
        group = groups[0]
        children = list(group.member_items())

        # Step 1: Move the group (non-zero offset is critical)
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

        # No duplicate IDs
        all_ids = [
            a.get("id") for a in mw._draft_data["annotations"]
            if isinstance(a, dict)
        ]
        assert len(all_ids) == len(set(all_ids)), (
            f"Duplicate IDs after move+ungroup: "
            f"{[x for x in all_ids if all_ids.count(x) > 1]}"
        )

        # Index integrity
        anns = mw._draft_data["annotations"]
        for aid, idx in mw._id_to_index.items():
            assert idx < len(anns), f"{aid}: idx={idx} out of bounds"
            assert anns[idx].get("id") == aid, (
                f"{aid}: idx={idx} points to {anns[idx].get('id')}"
            )

        # Step 3: Drag a child — geom should update
        rects = [c for c in children if isinstance(c, MetaRectItem)]
        if rects:
            target = rects[0]
            ann_id = target.ann_id
            idx = mw._id_to_index.get(ann_id)
            assert idx is not None, f"{ann_id} not in _id_to_index"

            geom_before = dict(mw._draft_data["annotations"][idx].get("geom", {}))
            mw.scene.clearSelection()
            target.setSelected(True)
            qapp.processEvents()
            mw.scene._mouse_down_in_select = True
            old_pos = target.pos()
            target.setPos(old_pos.x() + 5, old_pos.y() + 5)
            qapp.processEvents()

            geom_after = mw._draft_data["annotations"][idx].get("geom", {})
            assert geom_after != geom_before, (
                f"Geom should have changed: {geom_before} -> {geom_after}"
            )

            # Editor should also reflect the change
            editor_data = json.loads(mw.draft.get_json_text())
            editor_ann = next(
                (a for a in editor_data["annotations"] if a.get("id") == ann_id),
                None,
            )
            assert editor_ann is not None, f"{ann_id} missing from editor JSON"
            assert editor_ann.get("geom") == geom_after, (
                f"Editor geom mismatch: {editor_ann.get('geom')} vs {geom_after}"
            )

            mw.scene._mouse_down_in_select = False
            mw.draft.unlock_scroll()

    def test_json_valid_after_ungroup_and_drag(self, linked_scene_with_groups, qapp):
        """JSON in the editor should remain valid after ungroup + drag."""
        from canvas.items import MetaRectItem

        mw, groups = linked_scene_with_groups

        # Ungroup all groups
        for g in groups:
            g.setSelected(True)
            qapp.processEvents()
            mw._do_ungroup_item(g)
            qapp.processEvents()
            g.setSelected(False)

        # Find all rects and drag each one
        all_rects = [i for i in mw.scene.items() if isinstance(i, MetaRectItem)]
        assert len(all_rects) > 0

        for rect in all_rects:
            mw.scene.clearSelection()
            rect.setSelected(True)
            qapp.processEvents()
            mw.scene._mouse_down_in_select = True
            old_pos = rect.pos()
            rect.setPos(old_pos.x() + 3, old_pos.y() + 3)
            qapp.processEvents()
            mw.scene._mouse_down_in_select = False
            mw.draft.unlock_scroll()

        # Verify JSON is valid
        text = mw.draft.get_json_text()
        data = json.loads(text)  # Will raise if invalid
        assert len(data["annotations"]) > 0

        # Verify all rects are in the JSON
        json_ids = {a.get("id") for a in data["annotations"]}
        for rect in all_rects:
            assert rect.ann_id in json_ids, (
                f"{rect.ann_id} missing from JSON after drag"
            )
