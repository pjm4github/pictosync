"""Diagnostic: move group g000012 FIRST, then ungroup, then drag p000013."""
import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from PyQt6.QtWidgets import QApplication, QGraphicsItem
from PyQt6.QtCore import QPointF

app = QApplication(sys.argv)
from settings import SettingsManager
from main import MainWindow
from canvas.items import MetaGroupItem

mw = MainWindow(SettingsManager())
mw.show()
app.processEvents()

puml_path = os.path.abspath('test/PUML/test_flow.puml')
mw._import_puml(puml_path)
mw.import_draft_and_link()
app.processEvents()

# Find and ungroup g000012
groups = [i for i in mw.scene.items() if isinstance(i, MetaGroupItem)]
target_group = [g for g in groups if g.ann_id == 'g000012'][0]
children = list(target_group.member_items())
p13 = [c for c in children if c.ann_id == 'p000013'][0]

print(f"=== STEP 1: Move group g000012 ===")
print(f"  group pos before: ({target_group.pos().x()}, {target_group.pos().y()})")
print(f"  p000013 pos before: ({p13.pos().x()}, {p13.pos().y()})")
print(f"  p000013 scenePos: ({p13.scenePos().x()}, {p13.scenePos().y()})")

# Select and move the group
mw.scene.clearSelection()
target_group.setSelected(True)
app.processEvents()

mw.scene._mouse_down_in_select = True
old_group_pos = target_group.pos()
target_group.setPos(old_group_pos.x() + 20, old_group_pos.y() + 20)
app.processEvents()
mw.scene._mouse_down_in_select = False
mw.draft.unlock_scroll()
app.processEvents()

print(f"  group pos after move: ({target_group.pos().x()}, {target_group.pos().y()})")
print(f"  p000013 pos after group move: ({p13.pos().x()}, {p13.pos().y()})")
print(f"  p000013 scenePos after: ({p13.scenePos().x()}, {p13.scenePos().y()})")

# Check state
idx_group = mw._id_to_index.get('g000012')
print(f"  g000012 in index: {idx_group}")
print(f"  annotations count: {len(mw._draft_data['annotations'])}")

print(f"\n=== STEP 2: Ungroup g000012 ===")
target_group.setSelected(True)
app.processEvents()
mw._do_ungroup_item(target_group)
app.processEvents()

print(f"  p000013 pos after ungroup: ({p13.pos().x()}, {p13.pos().y()})")
print(f"  p000013 parentItem: {type(p13.parentItem()).__name__ if p13.parentItem() else 'None'}")
print(f"  p000013 on_change: {p13.on_change is not None}")

idx = mw._id_to_index.get('p000013')
print(f"  p000013 in index: {idx}")
print(f"  annotations count: {len(mw._draft_data['annotations'])}")

if idx is not None:
    ann = mw._draft_data['annotations'][idx]
    print(f"  annotation id at idx: {ann.get('id')}")
    print(f"  annotation geom: {ann.get('geom')}")
else:
    print(f"  p000013 NOT IN INDEX!")
    # Search all annotations
    for i, a in enumerate(mw._draft_data['annotations']):
        if isinstance(a, dict) and a.get('id') == 'p000013':
            print(f"  found p000013 at index {i}")
            print(f"  but _id_to_index says: {mw._id_to_index.get('p000013')}")

# Check for duplicates
all_ids = [a.get('id') for a in mw._draft_data['annotations'] if isinstance(a, dict)]
dup_ids = [x for x in all_ids if all_ids.count(x) > 1]
if dup_ids:
    print(f"  DUPLICATE IDs: {set(dup_ids)}")

print(f"\n=== STEP 3: Drag p000013 ===")
mw.scene.clearSelection()
p13.setSelected(True)
app.processEvents()
app.processEvents()

mw.scene._mouse_down_in_select = True
idx = mw._id_to_index.get('p000013')
if idx is not None:
    geom_before = dict(mw._draft_data['annotations'][idx].get('geom', {}))
    print(f"  geom before drag: {geom_before}")
else:
    geom_before = None
    print(f"  p000013 NOT IN INDEX - drag won't update JSON!")

old_pos = p13.pos()
for step in range(1, 6):
    p13.setPos(old_pos.x() + step, old_pos.y() + step)
    app.processEvents()

if idx is not None:
    geom_after = mw._draft_data['annotations'][idx].get('geom', {})
    print(f"  geom after drag: {geom_after}")
    print(f"  changed: {geom_before != geom_after}")
else:
    # Check if it was added as a new item
    idx_new = mw._id_to_index.get('p000013')
    if idx_new is not None:
        print(f"  p000013 appeared at index {idx_new} (was added as new)")
        print(f"  geom: {mw._draft_data['annotations'][idx_new].get('geom', {})}")
    else:
        print(f"  p000013 STILL NOT IN INDEX after drag!")

# Verify editor text
editor_text = mw.draft.get_json_text()
data = json.loads(editor_text)
ann = None
for a in data['annotations']:
    if a.get('id') == 'p000013':
        ann = a
        break
print(f"  p000013 in editor JSON: {ann is not None}")
if ann:
    print(f"  editor geom: {ann.get('geom')}")

# Full integrity check
print(f"\n=== Index integrity ===")
anns = mw._draft_data['annotations']
mismatches = 0
for aid, i in mw._id_to_index.items():
    if i >= len(anns):
        print(f"  {aid}: idx={i} OUT OF BOUNDS (len={len(anns)})")
        mismatches += 1
    elif anns[i].get('id') != aid:
        print(f"  {aid}: idx={i} → id={anns[i].get('id')}")
        mismatches += 1
if mismatches == 0:
    print(f"  All {len(mw._id_to_index)} entries OK")

mw.scene._mouse_down_in_select = False
mw.draft.unlock_scroll()
app.quit()
