"""Measured developer-driven widget walkthrough, not a novice usability study."""
from pathlib import Path
import sys,tempfile,time,json,os
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication,QPushButton
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt
from logbook.storage import Store
from logbook.ui import MainWindow,RecordDialog,PdfPreview
from logbook.documents import write_pdf
root=Path(__file__).resolve().parents[1];out=root/'docs/rc-evidence';out.mkdir(exist_ok=True)
app=QApplication([]);app.setStyle('Fusion');actions=[];start=time.perf_counter()
def click(dialog,label):
 button=next(b for b in dialog.findChildren(QPushButton) if b.text()==label)
 QTest.mouseClick(button,Qt.MouseButton.LeftButton);app.processEvents();actions.append('Click '+label)
def fill(dialog,key,value):
 c=dialog.form.controls[key]
 if hasattr(c,'setPlainText'):c.setPlainText(value)
 elif hasattr(c,'setCurrentText'):c.setCurrentText(value)
 else:c.setText(value)
 actions.append('Enter '+key);app.processEvents()
with tempfile.TemporaryDirectory() as folder:
 store=Store(Path(folder));main=MainWindow(store,root/'resources');main.show();app.processEvents()
 aircraft=RecordDialog(main,'aircraft');aircraft.show();app.processEvents();actions.append('Open + Aircraft')
 for key,value in {'registration':'WALKTHROUGH-DEMO','make':'Piper','model':'PA-28-161','serial_number':'FICTIONAL-ONLY'}.items():fill(aircraft,key,value)
 click(aircraft,'Save');click(aircraft,'Close');main.reload_aircraft()
 entry=RecordDialog(main,'entry');entry.show();app.processEvents();actions.append('Open New Maintenance Entry')
 for key,value in {'category':'Preventive maintenance','date':'2026-10-01','performer':'Fictional operator','description':'DEMO ONLY: no actual maintenance. Fictional oil-change draft for usability rehearsal.'}.items():fill(entry,key,value)
 click(entry,'Save Draft');record=entry.record
 entry.grab().save(str(out/('walkthrough-editor-'+os.environ.get('QT_SCALE_FACTOR','1')+'.png')))
 pdf=Path(folder)/'draft.pdf';write_pdf(pdf,[record],store.aircraft()[0],True);actions.append('Generate PDF through document service (dialog automation bypassed)')
 preview=PdfPreview(pdf,entry);preview.show();QTest.qWait(600);app.processEvents();actions.append('Open actual PDF preview');preview.grab().save(str(out/('walkthrough-preview-'+os.environ.get('QT_SCALE_FACTOR','1')+'.png')));preview.close();entry.close();main.close()
 reopened=Store(Path(folder));assert reopened.get(record['id'])['data']['description']==record['data']['description'];actions.append('Reopen data and verify draft')
 evidence={'method':'Developer-driven real Qt widget/service rehearsal; not an independent novice or install-time test','scale_factor':os.environ.get('QT_SCALE_FACTOR','1'),'elapsed_seconds':round(time.perf_counter()-start,3),'action_count':len(actions),'actions':actions,'errors':0,'draft_survived_reopen':True,'physical_printing':False,'file_dialog_interactions_bypassed':True}
 (out/('walkthrough-'+os.environ.get('QT_SCALE_FACTOR','1')+'.json')).write_text(json.dumps(evidence,indent=2));print(json.dumps(evidence))
