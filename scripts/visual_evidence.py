"""Capture real Qt widgets and generated PDFs from isolated fictional data."""
from pathlib import Path
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from logbook.storage import Store
from logbook.__main__ import seed_demo
from logbook.ui import MainWindow,RecordDialog,SetupWizard
from logbook.documents import write_pdf

root=Path(__file__).resolve().parents[1];out=root/'docs'/'rc-evidence';out.mkdir(parents=True,exist_ok=True)
app=QApplication([]);app.setStyle('Fusion')
with tempfile.TemporaryDirectory() as folder:
    store=Store(Path(folder));seed_demo(store);main=MainWindow(store,root/'resources');main.show();app.processEvents()
    main.grab().save(str(out/'dashboard-dark.png'))
    main.theme('Light');app.processEvents();main.grab().save(str(out/'dashboard-light.png'))
    main.theme('Dark');main.resize(1000,700);app.processEvents();main.grab().save(str(out/'dashboard-small.png'))
    record=store.records('entry')[0];editor=RecordDialog(main,'entry',record);editor.show();app.processEvents();editor.grab().save(str(out/'entry-editor.png'))
    editor.close();wizard=SetupWizard(main);wizard.show();app.processEvents();wizard.grab().save(str(out/'first-run.png'));wizard.close()
    aircraft=store.aircraft()[0]
    write_pdf(out/'sample-full.pdf',[record],aircraft)
    write_pdf(out/'sample-compact.pdf',[record],aircraft,True)
    record['data']['description']='DEMO ONLY. Fictional maintenance description with accents: José, café. No actual maintenance performed.\n'*130
    write_pdf(out/'sample-long.pdf',[record],aircraft)
    record['data'].update(category='Preventive maintenance',description='DEMO ONLY: oil brand/type and quantity documented by the fictional performer. No actual maintenance performed.',performer='Fictional pilot',approver='Fictional pilot',certificate_type='Pilot',certificate_number='DEMO-NOT-VALID',date='2026-10-01',total_time='2345.6',disposition='Approval for physical signature')
    record['state']='Draft'
    write_pdf(out/'compact-work.pdf',[record],aircraft,True,compact_width=6)
    write_pdf(out/'letter-work.pdf',[record],aircraft)
    from logbook.statements import inspection_statement
    record['data'].update(category='Annual inspection',extent='Fictional annual inspection scope',disposition='Not approved',discrepancy_date='2026-10-01',discrepancies='DEMO ONLY: fictional cabin light discrepancy. No actual inspection or findings.',approver='Fictional IA',certificate_type='A&P / IA')
    record['data']['statement']=inspection_statement(record['data'])
    write_pdf(out/'nonapproval.pdf',[record],aircraft)
    write_pdf(out/'discrepancy-list.pdf',[record],aircraft,discrepancy=True)
    record['data']['disposition']='Approval for physical signature';record['data']['statement']=inspection_statement(record['data'])
    write_pdf(out/'approved-inspection.pdf',[record],aircraft)
    main.navigation.setCurrentRow(2);app.processEvents();main.grab().save(str(out/'paginated-logbook.png'))
    main.close()
