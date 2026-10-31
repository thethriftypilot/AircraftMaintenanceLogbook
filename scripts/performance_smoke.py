"""Bounded, fictional dataset timing; not a hardware-independent SLA."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import json
import sys
import tempfile
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from logbook.storage import Store,uid,now,encode
from logbook.services import Service
from logbook.ui import MainWindow

root=Path(__file__).resolve().parents[1]
app=QApplication([])
with tempfile.TemporaryDirectory() as folder:
    store=Store(Path(folder));aircraft=Service(store).save_aircraft({'registration':'PERFORMANCE-DEMO'})
    with store.connect() as con:
        stamp=now()
        con.executemany('INSERT INTO records(id,kind,aircraft_id,state,data,created,modified) VALUES(?,?,?,?,?,?,?)',[(uid(),'entry',aircraft['id'],'Historical import requiring verification',encode({'category':'Historical entry','date':'2026-01-01','description':f'DEMO ONLY performance fixture {i}','source_document':'Synthetic performance fixture'}),stamp,stamp) for i in range(5000)])
    start=time.perf_counter();window=MainWindow(store,root/'resources');window.navigation.setCurrentRow(2);app.processEvents();load=time.perf_counter()-start
    start=time.perf_counter();window.search.setText('fixture 4999');app.processEvents();search=time.perf_counter()-start
    result={'records':5000,'initial_window_and_list_seconds':round(load,3),'search_seconds':round(search,3),'matching_rows':window.table.rowCount(),'mode':'offscreen synthetic data; local Windows development hardware'}
    (root/'docs'/'performance-smoke.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result));window.close()
