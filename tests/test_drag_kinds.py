"""Diagnostic: check which item kinds update JSON during drag."""
import sys, json, os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QPointF

app = QApplication(sys.argv)
from settings import SettingsManager
from main import MainWindow

mw = MainWindow(SettingsManager())
mw.show()
app.processEvents()

mw._import_puml(os.path.abspath('test/PUML/test_seq1.puml'))
mw.import_draft_and_link()
app.processEvents()

items = [i for i in mw.scene.items() if hasattr(i, 'ann_id')]
by_kind = {}
for it in items:
    k = it.meta.kind if hasattr(it, 'meta') else type(it).__name__
    by_kind.setdefault(k, []).append(it)
print('Item kinds:', {k: len(v) for k, v in by_kind.items()})


def find_ann(data, aid):
    for a in data.get('annotations', []):
        if a.get('id') == aid:
            return a
        for c in a.get('children', []):
            if c.get('id') == aid:
                return c
    return None


for kind_name in ['rect', 'roundedrect', 'line', 'polygon', 'text']:
    kind_items = by_kind.get(kind_name, [])
    if not kind_items:
        print(f'{kind_name}: NO ITEMS')
        continue
    it = kind_items[0]
    ann_id = it.ann_id
    idx = mw._id_to_index.get(ann_id)

    data_before = json.loads(mw.draft.get_json_text())
    ann_before = find_ann(data_before, ann_id)

    mw.scene._mouse_down_in_select = True
    old_pos = it.pos()
    it.setPos(old_pos.x() + 10, old_pos.y() + 10)
    app.processEvents()

    data_after = json.loads(mw.draft.get_json_text())
    ann_after = find_ann(data_after, ann_id)

    if ann_before and ann_after:
        geom_changed = ann_before.get('geom') != ann_after.get('geom')
    else:
        geom_changed = 'MISSING'

    has_cb = it.on_change is not None
    print(f'{kind_name}: id={ann_id} idx={idx} on_change={has_cb} geom_changed={geom_changed}')
    if ann_before:
        print(f'  before: {ann_before.get("geom", {})}')
    if ann_after:
        print(f'  after:  {ann_after.get("geom", {})}')

    mw.scene._mouse_down_in_select = False
    mw.draft.unlock_scroll()
    it.setPos(old_pos)
    app.processEvents()

app.quit()
