"""Native Qt Widgets interface. All writes go through application services."""
from __future__ import annotations
import functools
import json
import logging
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QUrl, QThread, Signal, QSize,QRectF,QBuffer,QIODevice
from PySide6.QtGui import QDesktopServices, QPainter, QIcon
from PySide6.QtWidgets import (QApplication,QLayout,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QFormLayout,QLabel,QPushButton,QComboBox,QLineEdit,QPlainTextEdit,QCheckBox,QTabWidget,QScrollArea,QDialog,QDialogButtonBox,QMessageBox,QTextBrowser,QSplitter,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView,QFileDialog,QInputDialog,QListWidget,QProgressDialog,QWizard,QWizardPage)
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtPrintSupport import QPrinter,QPrintDialog,QPageSetupDialog,QPrinterInfo
from .forms import FORMS
from .domain import DISCLAIMER, schedule_status
from .services import Service
from .storage import Store, now
from .documents import entry_html, write_pdf
from .backup import backup,inspect_backup,restore
from .portability import read_csv,import_csv,export_csv,export_json,CSV_FIELDS

def guarded(fn):
    @functools.wraps(fn)
    def run(self,*args,**kwargs):
        try:
            return fn(self,*args,**kwargs)
        except Exception as exc:
            logging.getLogger('logbook').warning('Operation failed: %s',type(exc).__name__)
            QMessageBox.warning(self,'Unable to complete operation',str(exc)+'\n\nCheck the values or available disk space, then retry. Existing finalized records are retained.')
            return None
    return run

def button(label,slot,layout=None,primary=False):
    item=QPushButton(label)
    if primary:
        item.setObjectName('primary')
    item.clicked.connect(slot)
    if layout is not None:
        layout.addWidget(item)
    return item

class Task(QThread):
    result=Signal(object)
    failure=Signal(str)
    def __init__(self,action,parent):
        super().__init__(parent); self.action=action
    def run(self):
        try:
            self.result.emit(self.action())
        except Exception as exc:
            self.failure.emit(str(exc))

def work(parent,title,action):
    dialog=QProgressDialog(title,None,0,0,parent)
    dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
    dialog.setMinimumDuration(0)
    dialog.setWindowFlag(Qt.WindowType.WindowCloseButtonHint,False)
    result=[]; errors=[]
    task=Task(action,dialog)
    task.result.connect(result.append); task.failure.connect(errors.append)
    task.finished.connect(dialog.accept)
    task.start(); dialog.exec(); task.wait()
    if errors:
        raise ValueError(errors[0])
    return result[0] if result else None

class Fields(QWidget):
    changed=Signal()
    def __init__(self,kind,data=None,parent=None):
        super().__init__(parent); self.controls={}
        layout=QVBoxLayout(self); tabs=QTabWidget();self.tabs=tabs; layout.addWidget(tabs)
        for tab_title,definitions in FORMS[kind]:
            page=QWidget(); form=QFormLayout(page); form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
            for key,label,typ in definitions:
                if isinstance(typ,list):
                    control=QComboBox(); control.addItems(typ); control.currentTextChanged.connect(self.changed)
                elif typ=='bool':
                    control=QCheckBox(); control.stateChanged.connect(self.changed)
                elif typ=='long':
                    control=QPlainTextEdit(); control.setMinimumHeight(95); control.textChanged.connect(self.changed)
                else:
                    control=QLineEdit(); control.textChanged.connect(self.changed)
                    if 'date' in key or key in ['last_annual','authorization_until']:
                        control.setPlaceholderText('YYYY-MM-DD or blank if unknown')
                control.setAccessibleName(label); control.setObjectName(key)
                caption=QLabel(label); caption.setWordWrap(True); caption.setMinimumWidth(160); caption.setMaximumWidth(210); caption.setBuddy(control)
                form.addRow(caption,control); self.controls[key]=control
            scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setWidget(page); tabs.addTab(scroll,tab_title)
        self.set_data(data or {})
        if kind=='entry':
            self.controls['category'].currentTextChanged.connect(self.contextual)
            self.contextual()
            for key in ['statement','category','disposition','extent','discrepancy_date','routine_scope','detailed_scope','inspection_program']:
                control=self.controls[key]
                signal=control.currentTextChanged if isinstance(control,QComboBox) else control.textChanged
                signal.connect(lambda *args:self.controls['statement_reviewed'].setChecked(False))
    def contextual(self):
        from .statements import is_inspection
        self.tabs.setTabVisible(2,is_inspection(self.data()))
    def set_data(self,data):
        for key,control in self.controls.items():
            if key not in data: continue
            value=data[key]
            if isinstance(control,QComboBox): control.setCurrentText(str(value))
            elif isinstance(control,QCheckBox): control.setChecked(bool(value))
            elif isinstance(control,QPlainTextEdit): control.setPlainText(str(value))
            else: control.setText(str(value))
    def data(self):
        return {key:(control.currentText() if isinstance(control,QComboBox) else control.isChecked() if isinstance(control,QCheckBox) else control.toPlainText() if isinstance(control,QPlainTextEdit) else control.text().strip()) for key,control in self.controls.items()}

class PdfPreview(QDialog):
    def __init__(self,path,parent):
        super().__init__(parent); self.setWindowTitle('Print preview • actual PDF pages'); self.resize(850,740)
        self.document=QPdfDocument(self)
        self.printer=QPrinter(QPrinter.PrinterMode.HighResolution)
        main=parent if hasattr(parent,'store') else getattr(parent,'main',None)
        if main and main.store.setting('printer',''):self.printer.setPrinterName(main.store.setting('printer'))
        self.pdf_buffer=QBuffer(self);self.pdf_buffer.setData(Path(path).read_bytes());self.pdf_buffer.open(QIODevice.OpenModeFlag.ReadOnly)
        self.document.load(self.pdf_buffer);error=self.document.error()
        if error!=QPdfDocument.Error.None_:
            raise ValueError('PDF could not be loaded for preview.')
        layout=QVBoxLayout(self); view=QPdfView(self); view.setDocument(self.document)
        view.setPageMode(QPdfView.PageMode.MultiPage); view.setZoomMode(QPdfView.ZoomMode.FitToWidth); layout.addWidget(view)
        self.scale=QComboBox();self.scale.addItems(['Actual size (100%)','Fit to selected paper']);layout.addWidget(self.scale)
        button('Paper / orientation…',lambda:QPageSetupDialog(self.printer,self).exec(),layout)
        button('Print…',self.print_document,layout,True)
    def done(self,result):
        self.document.close()
        super().done(result)
    def closeEvent(self,event):
        self.document.close()
        super().closeEvent(event)
    @guarded
    def print_document(self):
        printer=self.printer
        dialog=QPrintDialog(printer,self)
        dialog.setMinMax(1,self.document.pageCount())
        if dialog.exec()!=QDialog.DialogCode.Accepted: return
        printer.setFullPage(True)
        painter=QPainter()
        if not painter.begin(printer): raise ValueError('Printer could not start. Select another printer or export PDF.')
        try:
            start=max(0,printer.fromPage()-1); end=printer.toPage() or self.document.pageCount()
            for page in range(start,min(end,self.document.pageCount())):
                if page>start and not printer.newPage(): raise ValueError('Printer rejected a page.')
                size=self.document.pagePointSize(page)
                image=self.document.render(page,QSize(int(size.width()*3),int(size.height()*3)))
                rect=printer.pageLayout().fullRectPixels(printer.resolution())
                actual=QSize(round(size.width()*printer.resolution()/72),round(size.height()*printer.resolution()/72))
                if self.scale.currentIndex()==0:
                    if actual.width()>rect.width()+2 or actual.height()>rect.height()+2:raise ValueError('Document exceeds selected paper at 100%. Choose larger paper or explicitly select Fit.')
                    scaled=actual
                else:scaled=actual.scaled(rect.size(),Qt.AspectRatioMode.KeepAspectRatio)
                painter.drawImage(QRectF(0,0,scaled.width(),scaled.height()),image)
        finally: painter.end()

class RecordDialog(QDialog):
    def __init__(self,main,kind,record=None):
        super().__init__(main); self.main=main; self.service=main.service; self.kind=kind; self.record=record
        self.aircraft_id=record.get('aircraft_id') if record and kind!='aircraft' else main.aircraft_id()
        self.frozen=bool(record and kind=='entry' and record['state'] not in ['Draft','Historical import requiring verification'])
        self.setWindowTitle(('View' if self.frozen else 'Edit' if record else 'New')+' '+kind.replace('_',' ')); self.resize(1080 if kind=='entry' else 760,760)
        layout=QVBoxLayout(self)
        if kind=='entry':
            guidance=QLabel('Document actual work. Approval is a separate decision; a typed name is not a signature.\nInspection: enter the applicable § 43.11 statement. Historical: preserve source and uncertainty.')
            guidance.setWordWrap(True); layout.addWidget(guidance)
        defaults={'date':date.today().isoformat()} if kind in ['entry','expense','part','item','component_event'] else {}
        if kind=='expense':defaults['currency']=main.store.setting('currency','USD')
        self.form=Fields(kind,record['data'] if record else defaults,self)
        split=QSplitter(); split.addWidget(self.form); layout.addWidget(split,1)
        self.preview=None
        if kind=='entry':
            self.preview=QTextBrowser(); self.preview.setMinimumWidth(300); split.addWidget(self.preview); split.setSizes([620,420])
            self.form.changed.connect(self.update_preview)
        self.form.setEnabled(not self.frozen and kind!='component_event' or record is None)
        links=QHBoxLayout(); self.component=QComboBox(); self.component.addItem('Whole aircraft / no component',None)
        for item in self.service.store.records('component'):
            if item['aircraft_id']==self.aircraft_id or (record and item['id']==record.get('component_id')):
                self.component.addItem(item['data'].get('title','Component')+' | '+item['data'].get('serial_number','')+' | '+item['data'].get('installation_status','Unknown installation'),item['id'])
        self.linked_entry=QComboBox(); self.linked_entry.addItem('No linked maintenance entry',None)
        for item in self.service.store.records('entry',self.aircraft_id) if self.aircraft_id else []:
            self.linked_entry.addItem(item['data'].get('date','Unknown date')+' | '+item['data'].get('description','')[:55],item['id'])
        if kind not in ['aircraft','profile','component']:
            links.addWidget(QLabel('Component')); links.addWidget(self.component)
            if kind!='entry': links.addWidget(self.linked_entry)
            layout.addLayout(links)
        if record:
            self.component.setCurrentIndex(max(0,self.component.findData(record.get('component_id'))))
            self.linked_entry.setCurrentIndex(max(0,self.linked_entry.findData(record.get('entry_id'))))
        self.component.setEnabled(not self.frozen)
        if kind=='entry' and not self.frozen:
            helpers=QHBoxLayout(); self.identity=QComboBox(); self.identity.addItem('Use saved approving identity…',None)
            for profile in self.service.store.records('profile'):
                self.identity.addItem(profile['data'].get('name','Identity'),profile)
            self.identity.activated.connect(self.apply_identity); helpers.addWidget(self.identity)
            button('Preventive task guidance',self.task_guidance,helpers); layout.addLayout(helpers)
            extra=QHBoxLayout();layout.addLayout(extra)
            button('Oil change details…',self.oil_change,extra)
            self.prepare_inspection_button=button('Prepare inspection statement…',self.prepare_statement,extra)
        if kind=='entry':
            evidence=QHBoxLayout();layout.addLayout(evidence)
            discrepancy_button=button('Discrepancy list PDF',self.discrepancy_pdf,evidence)
            delivery_button=button('Record list delivery',self.delivery,evidence)
            def inspection_actions():
                from .statements import is_inspection
                active=is_inspection(self.form.data())
                discrepancy_button.setVisible(active);delivery_button.setVisible(active)
                if hasattr(self,'prepare_inspection_button'):self.prepare_inspection_button.setVisible(active)
            self.form.controls['category'].currentTextChanged.connect(inspection_actions);inspection_actions()
            if record:button('Amendment history',self.chain,evidence)
        self.status=QLabel(record['state'] if record and kind!='aircraft' else 'Changes are saved locally.'); self.status.setWordWrap(True); layout.addWidget(self.status)
        actions=QHBoxLayout(); layout.addLayout(actions)
        self.save_button=button('Save Draft' if kind=='entry' else 'Save',self.save,actions,True)
        self.save_button.setEnabled(not self.frozen and not (kind=='component_event' and record))
        if kind=='entry':
            if not self.frozen: button('Finalize for printing',self.finalize,actions)
            else: button('Create amendment',self.amend,actions)
            button('PDF / Print preview',self.pdf,actions)
            if self.frozen: button('Record signed copy',self.signed,actions)
        if kind!='aircraft': button('Attachments',self.attachments,actions)
        button('Close',self.close,actions)
        self.timer=QTimer(self); self.timer.setInterval(1500); self.timer.setSingleShot(True); self.timer.timeout.connect(self.autosave)
        self.dirty=False
        self.form.changed.connect(self.changed)
        self.component.currentIndexChanged.connect(self.changed)
        if kind=='entry': self.update_preview()
    def changed(self):
        self.dirty=True
        if self.kind=='entry' and not self.frozen: self.timer.start()
    def update_preview(self):
        if not self.preview or not self.aircraft_id: return
        record=self.record or {'id':'Unsaved draft','state':'Draft','kind':'entry'}
        record={**record,'data':self.form.data()}
        self.preview.setHtml(entry_html(record,self.service.store.get(self.aircraft_id,True)))
    def apply_identity(self):
        profile=self.identity.currentData()
        if profile:
            data=dict(profile['data']); data['approver']=data.get('name',''); self.form.set_data(data)
    def task_guidance(self):
        reference=json.loads((self.main.resources/'regulatory.json').read_text(encoding='utf-8'))
        task,ok=QInputDialog.getItem(self,'Preventive maintenance reference','Choose a reference category (eligibility must be verified)',list(reference['preventive_tasks']),0,False)
        if ok:
            QMessageBox.information(self,task,reference['preventive_tasks'][task]+'\n\nRecord only actual work in the Work tab: materials, quantities, part numbers, observations and references. This guide provides no maintenance procedure.\n\n'+reference['pilot_guidance'])
    def persist(self):
        if self.frozen: return self.record
        data={**(self.record['data'] if self.record else {}),**self.form.data()}
        if self.kind=='aircraft': self.record=self.service.save_aircraft(data,self.record)
        else: self.record=self.service.save(self.kind,data,None if self.kind=='profile' else self.aircraft_id,self.record,self.component.currentData(),self.linked_entry.currentData(),self.record.get('amends_id') if self.record else None)
        self.dirty=False
        if self.kind=='entry':self.update_preview()
        self.status.setText('Saved locally at '+datetime.now().strftime('%H:%M:%S')+' • '+(self.record.get('state') or 'Aircraft'))
        return self.record
    @guarded
    def save(self):
        self.persist(); self.main.refresh()
    def autosave(self):
        if not self.dirty: return
        try: self.persist()
        except Exception as exc: self.status.setText('Draft not saved: '+str(exc))
    @guarded
    def finalize(self):
        record=self.persist()
        from .domain import validate_entry
        errors=validate_entry(record['data'])
        if errors: raise ValueError('\n'.join(errors))
        if QMessageBox.question(self,'Finalize record','Lock the content for printing? Later corrections require a linked amendment. This does not sign or approve the record.')!=QMessageBox.StandardButton.Yes: return
        self.record=self.service.finalize(record); self.main.refresh(); self.accept()
    @guarded
    def amend(self):
        reason,ok=QInputDialog.getText(self,'Amendment','Why does this finalized record need correction?')
        if ok:
            amendment=self.service.amend(self.record,reason); self.accept(); RecordDialog(self.main,'entry',amendment).exec(); self.main.refresh()
    @guarded
    def pdf(self):
        record=self.persist()
        fmt,ok=QInputDialog.getItem(self,'Document format','Format',['Full page','Compact'],1 if self.main.store.setting('default_template','Full page')=='Compact' else 0,False)
        if not ok:return
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'entry.pdf'
            write_pdf(path,[record],self.service.store.get(self.aircraft_id,True),fmt=='Compact',compact_width=self.main.store.setting('compact_width',6.0),font_size=self.main.store.setting('font_size',10))
            dialog=PdfPreview(path,self)
            button('Save PDF…',lambda:self.save_pdf_copy(path),dialog.layout())
            dialog.exec()
        if record['state']=='Ready to print' and record['data'].get('category')!='Historical entry':
            if QMessageBox.question(self,'Physical print status','Did you print a physical copy for signing?')==QMessageBox.StandardButton.Yes:
                self.record=self.service.transition(record,'Printed / awaiting physical signature'); self.main.refresh(); self.accept()
    @guarded
    def save_pdf_copy(self,path):
        import shutil
        target,_=QFileDialog.getSaveFileName(self,'Save PDF','maintenance-entry.pdf','PDF (*.pdf)')
        if target: shutil.copyfile(path,target)
    @guarded
    def signed(self):
        if self.record['data'].get('category')=='Historical entry':raise ValueError('Attach the original historical source scan using Attachments. This transcription cannot be newly signed as maintenance.')
        path,_=QFileDialog.getOpenFileName(self,'Select externally signed document','','Documents (*.pdf *.png *.jpg *.jpeg)')
        if not path:return
        actor,ok=QInputDialog.getText(self,'Record signed copy','Your name (person recording this externally signed document):')
        if not ok:return
        if not actor.strip():raise ValueError('Recorder name is required.')
        if QMessageBox.question(self,'Confirm external signature','Confirm this document is the signed copy for this exact record. The application cannot authenticate its signature.')!=QMessageBox.StandardButton.Yes:return
        attachment=self.service.attach(self.record['id'],Path(path))
        self.record=self.service.transition(self.record,'Signed copy recorded',actor,attachment); self.main.refresh(); self.accept()
    @guarded
    def attachments(self):
        self.persist(); AttachmentDialog(self.main,self.record).exec()
    @guarded
    def prepare_statement(self):
        from .statements import inspection_statement
        statement=inspection_statement(self.form.data())
        if QMessageBox.question(self,'User review required',statement+'\n\nInsert this proposed wording for your review? It asserts facts and must match actual inspection, disposition and delivery. Inserting it does not approve or sign anything.')==QMessageBox.StandardButton.Yes:
            self.form.set_data({'statement':statement,'statement_reviewed':False})
    @guarded
    def oil_change(self):
        dialog=QDialog(self);dialog.setWindowTitle('Actual oil-change details');layout=QVBoxLayout(dialog)
        warning=QLabel('Verify authorization and Appendix A(c)/approved technical data. Enter only work actually performed. No inspection or test is assumed.');warning.setWordWrap(True);layout.addWidget(warning)
        form=QFormLayout();layout.addLayout(form);controls={}
        for key in ['Oil brand / type','Quantity and units','Filter part number (if replaced)','Actual observations / tests performed','Technical references']:
            control=QLineEdit();form.addRow(key,control);controls[key]=control
        affirmed=QCheckBox('I confirm these are actual work details, not proposed work');layout.addWidget(affirmed)
        button('Use reviewed details',dialog.accept,layout,True)
        if dialog.exec()!=QDialog.DialogCode.Accepted:return
        if not affirmed.isChecked():raise ValueError('Confirm the actual work before inserting a description.')
        values={k:c.text().strip() for k,c in controls.items()}
        if not values['Oil brand / type'] or not values['Quantity and units']:raise ValueError('Oil type and quantity/units are required for this drafting aid.')
        wording='Oil service performed. '+ '; '.join(k+': '+v for k,v in values.items() if v)+'.'
        self.form.set_data({'category':'Preventive maintenance','description':wording,'references':values['Technical references']})
    @guarded
    def discrepancy_pdf(self):
        record=self.persist()
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'discrepancy-list.pdf';write_pdf(path,[record],self.service.store.get(self.aircraft_id,True),discrepancy=True)
            dialog=PdfPreview(path,self);button('Save list PDF…',lambda:self.save_pdf_copy(path),dialog.layout());dialog.exec()
    @guarded
    def delivery(self):
        record=self.persist()
        path,_=QFileDialog.getOpenFileName(self,'Select signed and dated discrepancy list','','Documents (*.pdf *.png *.jpg *.jpeg)')
        if not path:return
        recipient,ok=QInputDialog.getText(self,'Actual delivery','Owner/operator recipient name:')
        if not ok:return
        when,ok=QInputDialog.getText(self,'Actual delivery','Delivery date (YYYY-MM-DD):')
        if not ok:return
        actor,ok=QInputDialog.getText(self,'Recorder','Your name (recording actual delivery):')
        if not ok:return
        evidence=self.service.attach(record['id'],Path(path))
        self.service.record_delivery(record['id'],evidence,recipient,when,actor)
        self.form.set_data({'list_delivered':True});self.status.setText('Signed list evidence and actual delivery recorded; no flight authorization implied.')
    @guarded
    def chain(self):
        from html import escape
        rows=self.service.amendment_chain(self.record['id']);dialog=QDialog(self);dialog.setWindowTitle('Chronological amendment chain — originals preserved');dialog.resize(850,650)
        layout=QVBoxLayout(dialog);view=QTextBrowser();layout.addWidget(view)
        view.setHtml(''.join('<h2>'+escape(r['created']+' • '+r['state'])+'</h2><p>Record '+escape(r['id'])+'</p><p>Amends: '+escape(r.get('amends_id') or 'Original')+'</p><p>Reason: '+escape(r['data'].get('amendment_reason','Original record'))+'</p><pre>'+escape(json.dumps(r['data'],ensure_ascii=False,indent=2))+'</pre>' for r in rows));dialog.exec()
    def closeEvent(self,event):
        self.timer.stop()
        if self.dirty and not self.frozen:
            try:self.persist()
            except Exception as exc:
                response=QMessageBox.question(self,'Unsaved changes',str(exc)+'\nDiscard unsaved changes?',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)
                if response!=QMessageBox.StandardButton.Yes:event.ignore();return
        self.main.refresh();event.accept()
    def reject(self):
        self.close()

class AttachmentDialog(QDialog):
    def __init__(self,main,record):
        super().__init__(main); self.main=main; self.record=record; self.setWindowTitle('Managed supporting documents'); self.resize(650,400)
        layout=QVBoxLayout(self); self.list=QListWidget(); layout.addWidget(self.list)
        row=QHBoxLayout();layout.addLayout(row);button('Add PDF / image',self.add,row);button('Open verified copy',self.open,row);button('Remove draft attachment',self.remove,row)
        self.refresh()
    def refresh(self):
        self.rows=self.main.service.attachments(self.record['id']);self.list.clear()
        for r in self.rows:self.list.addItem(r['filename']+' • '+r['sha256'][:12])
    def selected(self):
        if self.list.currentRow()<0:raise ValueError('Select a document first.')
        return self.rows[self.list.currentRow()]
    @guarded
    def add(self):
        path,_=QFileDialog.getOpenFileName(self,'Add supporting document','','Documents (*.pdf *.png *.jpg *.jpeg)')
        if path:self.main.service.attach(self.record['id'],Path(path));self.refresh()
    @guarded
    def open(self):
        row=self.selected()
        if not self.main.service.verify_attachment(row):raise ValueError('Attachment is missing or its hash has changed. Restore a verified backup.')
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.main.store.root/'attachments'/row['stored_name'])))
    @guarded
    def remove(self):
        row=self.selected()
        if QMessageBox.question(self,'Remove attachment','Remove this draft attachment? Finalized evidence cannot be deleted.')==QMessageBox.StandardButton.Yes:
            self.main.service.remove_attachment(row);self.refresh()

class ImportDialog(QDialog):
    def __init__(self,main,path):
        super().__init__(main);self.main=main;self.path=path;self.setWindowTitle('Preview historical CSV import');self.resize(900,650)
        headers,self.rows=read_csv(path);layout=QVBoxLayout(self);layout.addWidget(QLabel(f'{len(self.rows)} rows. Map columns below. Every imported record remains historical and unverified.'))
        form=QFormLayout();self.mapping={}
        for target in CSV_FIELDS:
            combo=QComboBox();combo.addItems(['']+headers);combo.setCurrentText(target if target in headers else '');form.addRow(target,combo);self.mapping[target]=combo
        layout.addLayout(form);preview=QTableWidget(min(10,len(self.rows)),len(headers));preview.setHorizontalHeaderLabels(headers)
        for i,row in enumerate(self.rows[:10]):
            for j,key in enumerate(headers):preview.setItem(i,j,QTableWidgetItem(row.get(key,'')))
        preview.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers);layout.addWidget(preview)
        button('Import historical records',self.import_rows,layout,True)
    @guarded
    def import_rows(self):
        mapping={k:v.currentText() for k,v in self.mapping.items()}
        count=work(self,'Validating and importing records…',lambda:import_csv(self.main.store,self.main.aircraft_id(),self.rows,mapping,Path(self.path).name))
        QMessageBox.information(self,'Import complete',f'{count} historical records imported.');self.accept();self.main.refresh()

PAGES=[('Dashboard',None),('Aircraft','aircraft'),('Logbook','entry'),('Maintenance Items','item'),('Schedules','schedule'),('ADs','ad'),('Service Bulletins','sb'),('Components','component'),('Component History','component_event'),('Parts','part'),('Expenses','expense'),('Reports','reports'),('Settings & Backups','settings'),('Timeline','timeline')]

class MainWindow(QMainWindow):
    def __init__(self,store,resources):
        super().__init__();self.store=store;self.service=Service(store);self.resources=Path(resources);self.rows=[];self.offset=0;self.current_list=None
        self.setWindowTitle('The Thrifty Pilot | Aircraft Maintenance Logbook');self.resize(*store.setting('window_size',[1220,800]));self.setMinimumSize(900,600)
        root=QWidget();self.setCentralWidget(root);outer=QHBoxLayout(root);outer.setContentsMargins(0,0,0,0)
        sidebar=QWidget();sidebar.setObjectName('sidebar');sidebar.setFixedWidth(210);nav=QVBoxLayout(sidebar);nav.setContentsMargins(16,24,16,18)
        brand=QLabel('THE THRIFTY PILOT\n\nMAINTENANCE\nLOGBOOK');brand.setObjectName('brand');nav.addWidget(brand)
        self.navigation=QListWidget();self.navigation.addItems([p[0] for p in PAGES]);self.navigation.currentRowChanged.connect(self.refresh);nav.addWidget(self.navigation)
        button('Help and references',self.help,nav);button('The Thrifty Pilot ↗',lambda:QDesktopServices.openUrl(QUrl('https://www.thethriftypilot.com/')),nav);outer.addWidget(sidebar)
        content=QWidget();body=QVBoxLayout(content);body.setContentsMargins(26,22,26,20);body.setSpacing(14);outer.addWidget(content,1)
        header=QHBoxLayout();self.aircraft_box=QComboBox();self.aircraft_box.setMinimumWidth(260);self.aircraft_box.setAccessibleName('Selected aircraft');self.aircraft_box.currentIndexChanged.connect(self.refresh);header.addWidget(self.aircraft_box)
        button('+ Aircraft',lambda:self.edit('aircraft'),header);header.addStretch();button('+ New Maintenance Entry',lambda:self.edit('entry'),header,True);body.addLayout(header)
        self.title=QLabel('Dashboard');self.title.setObjectName('title');body.addWidget(self.title)
        self.subtitle=QLabel();self.subtitle.setWordWrap(True);body.addWidget(self.subtitle)
        toolwidget=QWidget();self.tools=QHBoxLayout(toolwidget);self.tools.setContentsMargins(0,0,0,0);self.tools.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        toolscroll=QScrollArea();toolscroll.setWidgetResizable(True);toolscroll.setWidget(toolwidget);toolscroll.setFixedHeight(65);body.addWidget(toolscroll)
        self.search=QLineEdit();self.search.setPlaceholderText('Search records, dates, names, certificate numbers, parts…');self.search.setClearButtonEnabled(True);self.search.textChanged.connect(self.filter_changed);body.addWidget(self.search)
        self.table=QTableWidget();self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows);self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers);self.table.setAlternatingRowColors(True);self.table.setSortingEnabled(True);self.table.doubleClicked.connect(self.open_selected);self.table.horizontalHeader().setStretchLastSection(True);body.addWidget(self.table,1)
        self.summary=QTextBrowser();self.summary.setOpenExternalLinks(False);self.summary.anchorClicked.connect(self.dashboard_link);body.addWidget(self.summary,1)
        self.foot=QLabel('Local records • No telemetry • Status indicators do not determine airworthiness');self.foot.setObjectName('muted');body.addWidget(self.foot)
        self.navigation.setCurrentRow(0);self.reload_aircraft();self.theme(store.setting('theme','Dark'))
        self.auto_timer=QTimer(self);self.auto_timer.setInterval(60*60*1000);self.auto_timer.timeout.connect(self.automatic_backup);self.auto_timer.start()
    def aircraft_id(self):return self.aircraft_box.currentData()
    def reload_aircraft(self):
        previous=self.aircraft_id() or self.store.setting('selected_aircraft')
        self.aircraft_box.blockSignals(True);self.aircraft_box.clear()
        for record in self.store.aircraft():self.aircraft_box.addItem(record['registration']+(' • archived' if record['data'].get('archived') else ''),record['id'])
        self.aircraft_box.setCurrentIndex(max(0,self.aircraft_box.findData(previous)));self.aircraft_box.blockSignals(False);self.refresh()
    def kind(self):return PAGES[max(0,self.navigation.currentRow())][1]
    def clear_tools(self):
        while self.tools.count():
            item=self.tools.takeAt(0)
            if item.widget():
                widget=item.widget();widget.hide();widget.setParent(None);widget.deleteLater()
    def refresh(self,*args):
        if not hasattr(self,'summary'):return
        kind=self.kind();self.title.setText(PAGES[max(0,self.navigation.currentRow())][0]);self.clear_tools()
        self.summary.setVisible(kind in [None,'settings','reports']);self.table.setVisible(kind not in [None,'settings','reports']);self.search.setVisible(kind not in [None,'settings','reports'])
        if self.aircraft_id():self.store.set_setting('selected_aircraft',self.aircraft_id())
        self.subtitle.setText('Keep the record clear. Keep the history intact.')
        if kind is None:self.dashboard();return
        if kind=='settings':self.settings_page();return
        if kind=='reports':self.reports_page();return
        if self.current_list!=kind:
            self.current_list=kind;self.offset=0;self.search.blockSignals(True);self.search.setText(self.store.setting('filter_'+kind,''));self.search.blockSignals(False)
        if kind!='timeline':button('Add '+('aircraft' if kind=='aircraft' else 'record'),lambda:self.edit(kind),self.tools,True)
        button('Open selected',self.open_selected,self.tools)
        button('Previous',lambda:self.page_move(-100),self.tools);button('Next',lambda:self.page_move(100),self.tools)
        self.sort_box=QComboBox();self.sort_box.addItems(['Newest','Oldest','Work date']);self.sort_box.setCurrentText(self.store.setting('sort_'+kind,'Newest'));self.sort_box.currentTextChanged.connect(self.sort_changed);self.tools.addWidget(self.sort_box)
        button('Export visible CSV',self.csv_export,self.tools)
        if kind=='entry':button('Import historical CSV',self.csv_import,self.tools);button('Audit history',self.audit_view,self.tools)
        if kind=='component':button('Transfer component',self.transfer,self.tools)
        if kind in ['ad','schedule']:self.subtitle.setText('Thresholds use your applicability decision and explicit baselines. Missing inputs remain Unknown. No automatic interval resets.')
        if kind=='item':self.subtitle.setText('Deferred and Closed are tracking states, not authorization to operate. Closure needs linked signed corrective evidence.')
        self.populate()
    def filter_changed(self):
        self.offset=0
        if self.kind():self.store.set_setting('filter_'+self.kind(),self.search.text())
        self.populate()
    def sort_changed(self,value):
        self.store.set_setting('sort_'+self.kind(),value);self.offset=0;self.populate()
    def page_move(self,delta):
        self.offset=max(0,self.offset+delta);self.populate()
    def populate(self):
        if self.kind() in [None,'settings','reports']:return
        query=self.search.text().casefold()
        if self.kind()=='aircraft':
            rows=[r for r in self.store.aircraft() if query in json.dumps(r,ensure_ascii=False).casefold()];total=len(rows)
        elif self.aircraft_id():
            rows,total=self.store.page(None if self.kind()=='timeline' else self.kind(),self.aircraft_id(),query,self.offset,100,self.store.setting('sort_'+self.kind(),'Newest'))
            if self.offset and not rows:self.offset=max(0,((total-1)//100)*100);rows,total=self.store.page(None if self.kind()=='timeline' else self.kind(),self.aircraft_id(),query,self.offset,100,self.store.setting('sort_'+self.kind(),'Newest'))
        else:rows=[];total=0
        self.rows=rows
        with self.store.connect() as con:amended={r[0] for r in con.execute('SELECT original_id FROM amendments')}
        self.table.setSortingEnabled(False);self.table.clear();self.table.setColumnCount(5);self.table.setHorizontalHeaderLabels(['Date / registration','Description','Status','Details','Record ID']);self.table.setRowCount(len(rows))
        times=self.store.get(self.aircraft_id(),True)['data'] if self.aircraft_id() else {}
        for i,r in enumerate(rows):
            d=r['data'];status=r.get('state','Archived' if d.get('archived') else 'Active');detail=d.get('model') or d.get('number') or d.get('performer') or d.get('amount','')
            if r['id'] in amended:status+=' • amended (see chain)'
            if r.get('kind')=='component':status=d.get('installation_status','Unknown installation state')
            if self.kind() in ['schedule','ad']:
                clock=self.store.get(r['component_id'])['data'] if r.get('component_id') else times
                status,detail=schedule_status(d,clock)
            values=[d.get('date') or d.get('registration') or d.get('last_date',''),d.get('title') or d.get('description') or d.get('make',''),status,str(detail),r['id']]
            if self.store.setting('date_format','ISO')=='US' and len(values[0])==10 and values[0][4]=='-':values[0]=values[0][5:7]+'/'+values[0][8:10]+'/'+values[0][:4]
            for j,value in enumerate(values):
                cell=QTableWidgetItem(str(value).replace('\n',' ')[:200]);cell.setData(Qt.ItemDataRole.UserRole,r);cell.setToolTip(str(value));self.table.setItem(i,j,cell)
        self.table.setColumnWidth(0,135);self.table.setColumnWidth(1,300);self.table.setColumnWidth(2,220);self.table.setColumnHidden(4,True);self.table.setSortingEnabled(True)
        self.foot.setText(f'{len(rows)} displayed / {total} matching • Page {self.offset//100+1} • Column sorting applies to this page')
    def selected(self):
        row=self.table.currentRow()
        if row<0:raise ValueError('Select a record first.')
        return self.table.item(row,0).data(Qt.ItemDataRole.UserRole)
    @guarded
    def open_selected(self,*args):
        record=self.selected();self.edit(record['kind'] if self.kind()=='timeline' else self.kind(),record)
    @guarded
    def edit(self,kind,record=None):
        if kind not in ['aircraft','profile'] and not self.aircraft_id():raise ValueError('Add your first aircraft before creating maintenance records.')
        RecordDialog(self,kind,record).exec();self.reload_aircraft()
    def dashboard(self):
        button('Add Discrepancy',lambda:self.edit('item'),self.tools);button('View Maintenance Schedule',lambda:self.navigation.setCurrentRow(4),self.tools);button('Print Logbook Entry',lambda:self.navigation.setCurrentRow(2),self.tools)
        if not self.aircraft_id():
            self.summary.setHtml('<h1>Your aircraft records, in one place.</h1><p>Add your first aircraft, then create a maintenance entry. You can configure identities and backups at any time.</p><p>1. Add aircraft &nbsp; 2. Document actual work &nbsp; 3. Preview and print &nbsp; 4. Preserve a signed copy</p>');return
        from html import escape
        aircraft=self.store.get(self.aircraft_id(),True);data=aircraft['data'];records=self.store.records(aircraft_id=self.aircraft_id())
        entries=[r for r in records if r['kind']=='entry'];items=[r for r in records if r['kind']=='item' and r['data'].get('status') not in ['Closed','Canceled']]
        info=self.store.setting('last_backup',{});backup_info=(('Verified '+info.get('at','')+' • '+info.get('path','')) if info.get('verified') else 'No verified backup recorded')
        if not info.get('path') or Path(info['path']).drive.lower()==self.store.root.drive.lower():backup_info+=' • Same drive or unknown destination: keep a separate-drive copy.'
        out=f'<h1>{escape(aircraft["registration"])}</h1><p>{escape(data.get("make","")+" "+data.get("model",""))}</p><h2>{escape(data.get("total_time") or "Unknown")} airframe hours &nbsp; • &nbsp; {len(items)} open maintenance items</h2><p>Tach: {escape(data.get("tach") or "Unknown")} &nbsp; Hobbs: {escape(data.get("hobbs") or "Unknown")}</p><p>Last backup: {escape(backup_info)}</p><h2>Maintenance ahead</h2>'
        tracked=[r for r in records if r['kind'] in ['schedule','ad']]
        if not tracked:out+='<p>No reminders configured. Applicability must be reviewed for your aircraft and operation.</p>'
        for r in tracked[:20]:
            clock=self.store.get(r['component_id'])['data'] if r.get('component_id') else data
            status,detail=schedule_status(r['data'],clock)
            out+=f'<p><a href="record:{r["id"]}">{escape(r["data"].get("title") or r["data"].get("number") or "Untitled reminder")}</a> — {escape(status)}<br>{escape(detail)}</p>'
        out+='<h2>Recent records</h2>'
        if not records:out+='<p>No maintenance records yet. Create a new logbook entry to get started.</p>'
        for r in records[:10]:out+=f'<p><a href="record:{r["id"]}">{escape(r["data"].get("date", "")+" "+(r["data"].get("title") or r["data"].get("description") or r["kind"])[:100])}</a> • {escape(r["state"])}</p>'
        link_color='#68c8dd' if getattr(self,'theme_name','Dark')=='Dark' else '#005b76'
        self.summary.setHtml('<style>a {color:'+link_color+';} body {font-family:Segoe UI;}</style>'+out)
    @guarded
    def dashboard_link(self,url):
        record=self.store.get(url.toString().removeprefix('record:'));self.edit(record['kind'],record)
    @guarded
    def csv_export(self):
        path,_=QFileDialog.getSaveFileName(self,'Export visible rows','maintenance.csv','CSV (*.csv)')
        if path:export_csv([self.table.item(i,0).data(Qt.ItemDataRole.UserRole) for i in range(self.table.rowCount())],path)
    @guarded
    def csv_import(self):
        if not self.aircraft_id():raise ValueError('Select an aircraft first.')
        path,_=QFileDialog.getOpenFileName(self,'Import historical records','','CSV (*.csv)')
        if path:ImportDialog(self,path).exec()
    @guarded
    def audit_view(self):
        record=self.selected()
        with self.store.connect() as con:events=[dict(r) for r in con.execute('SELECT at,action,actor,detail FROM audit WHERE entity_id=? ORDER BY id',(record['id'],))]
        dialog=QDialog(self);dialog.setWindowTitle('Append-only record audit');dialog.resize(800,500);layout=QVBoxLayout(dialog);view=QPlainTextEdit();view.setReadOnly(True);view.setPlainText(json.dumps(events,indent=2,ensure_ascii=False));layout.addWidget(view);dialog.exec()
    @guarded
    def transfer(self):
        record=self.selected();aircraft=self.store.aircraft();names=[a['registration'] for a in aircraft]
        name,ok=QInputDialog.getItem(self,'Transfer component','Destination aircraft',names,0,False)
        if not ok:return
        when,ok=QInputDialog.getText(self,'Transfer date','Actual installation/removal date (YYYY-MM-DD)')
        if not ok:return
        notes,ok=QInputDialog.getMultiLineText(self,'Transfer details','Removal / installation details and source record:')
        if ok:self.service.transfer_component(record,aircraft[names.index(name)]['id'],when,notes);self.refresh()
    def settings_page(self):
        button('Identities',self.identities,self.tools);button('Preferences',self.preferences,self.tools);button('Back up now',self.backup_now,self.tools,True);button('Restore…',self.restore_backup,self.tools);button('Verify backup',self.verify_backup,self.tools);button('Backup history',self.backup_history,self.tools)
        from html import escape
        self.summary.setHtml('<h2>Private, offline records</h2><p>'+escape(DISCLAIMER)+'</p><h3>Data location</h3><p>'+escape(str(self.store.root))+'</p><h3>Backup location</h3><p>'+escape(self.store.setting('backup_folder',str(self.store.root/'backups')))+'</p><p>Automatic daily backup while the app is running: '+str(self.store.setting('auto_backup',True))+'</p><h3>Version 1.1.0-rc1 • Evaluation release candidate</h3><p>Keep backups on another drive. Restore retains a recovery archive. No automatic retention purge.</p>')
    @guarded
    def identities(self):
        records=self.store.records('profile');names=['Create identity']+[r['data'].get('name','Unnamed') for r in records]
        name,ok=QInputDialog.getItem(self,'Saved identities','Select or create',names,0,False)
        if ok:self.edit('profile',records[names.index(name)-1] if names.index(name)>0 else None)
    @guarded
    def preferences(self):
        dialog=QDialog(self);dialog.setWindowTitle('Preferences');layout=QFormLayout(dialog);controls={}
        options={'theme':['Dark','Light'],'default_template':['Compact','Full page'],'date_format':['ISO','US'],'currency':['USD','CAD','EUR','GBP'],'printer':['']+QPrinterInfo.availablePrinterNames()}
        defaults={'theme':'Dark','default_template':'Compact','date_format':'ISO','currency':'USD','printer':'','compact_width':'6.0','font_size':'10','backup_folder':str(self.store.root/'backups')}
        for key,default in defaults.items():
            control=QComboBox() if key in options else QLineEdit()
            if key in options:control.addItems(options[key]);control.setCurrentText(str(self.store.setting(key,default)))
            else:control.setText(str(self.store.setting(key,default)))
            controls[key]=control;layout.addRow(key.replace('_',' ').title(),control)
        automatic=QCheckBox();automatic.setChecked(self.store.setting('auto_backup',True));layout.addRow('Daily backup while running',automatic)
        layout.addRow(QLabel('Time units remain hours; cycles remain counts. No clock conversion.'))
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel);buttons.accepted.connect(dialog.accept);buttons.rejected.connect(dialog.reject);layout.addRow(buttons)
        if dialog.exec()!=QDialog.DialogCode.Accepted:return
        values={k:c.currentText() if isinstance(c,QComboBox) else c.text() for k,c in controls.items()}
        if not 4<=float(values['compact_width'])<=8.5 or not 8<=float(values['font_size'])<=14:raise ValueError('Width must be 4–8.5 inches; font must be 8–14 points.')
        for key,value in values.items():self.store.set_setting(key,value)
        self.store.set_setting('auto_backup',automatic.isChecked());self.theme(values['theme'])
    @guarded
    def backup_history(self):
        folder=Path(self.store.setting('backup_folder',str(self.store.root/'backups')))
        paths=sorted(set(folder.glob('*.zip'))|set((self.store.root/'backups').glob('*.zip')),key=lambda p:p.stat().st_mtime,reverse=True)
        dialog=QDialog(self);dialog.setWindowTitle('Retained archives — verify before use');dialog.resize(850,500);layout=QVBoxLayout(dialog);view=QTextBrowser();view.setPlainText('No automatic purge. Recovery archives are retained. Listing does not reverify contents. Use Verify backup.\n\n'+'\n'.join(str(p) for p in paths));layout.addWidget(view);dialog.exec()
    @guarded
    def backup_now(self):
        default=Path(self.store.setting('backup_folder',str(self.store.root/'backups')))/('logbook-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'.zip')
        path,_=QFileDialog.getSaveFileName(self,'Create complete verified backup',str(default),'ZIP archive (*.zip)')
        if path:
            work(self,'Creating and verifying backup…',lambda:backup(self.store,Path(path)));QMessageBox.information(self,'Backup verified','Database and all managed attachments saved.');self.refresh()
    @guarded
    def verify_backup(self):
        path,_=QFileDialog.getOpenFileName(self,'Verify backup','','ZIP archive (*.zip)')
        if path:
            result=work(self,'Verifying backup…',lambda:inspect_backup(Path(path)));QMessageBox.information(self,'Backup verified',json.dumps({k:v for k,v in result.items() if k!='files'},indent=2))
    @guarded
    def restore_backup(self):
        path,_=QFileDialog.getOpenFileName(self,'Restore complete backup','','ZIP archive (*.zip)')
        if not path:return
        info=work(self,'Inspecting archive…',lambda:inspect_backup(Path(path)))
        if QMessageBox.warning(self,'Replace current records?',f'Backup created: {info["created"]}\nSchema: {info["schema"]}\nAircraft: {info["aircraft_count"]}\nRecords: {info["record_count"]}\n\nReplace ALL current records with this archive? A recovery backup of current data will be retained.',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)!=QMessageBox.StandardButton.Yes:return
        work(self,'Saving recovery backup and restoring…',lambda:restore(self.store,Path(path),True));self.reload_aircraft();QMessageBox.information(self,'Restore complete','Restored database and attachment hashes verified. Current-state recovery backup retained in the data directory.')
    def automatic_backup(self):
        if QApplication.activeModalWidget() or not self.store.setting('auto_backup',True):return
        previous=self.store.setting('last_backup',{}).get('at','')
        if previous and (datetime.now(timezone.utc)-datetime.fromisoformat(previous)).total_seconds()<86400:return
        try:
            path=Path(self.store.setting('backup_folder',str(self.store.root/'backups')))/('automatic-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'.zip')
            work(self,'Creating daily backup…',lambda:backup(self.store,path));self.refresh()
        except Exception as exc:self.foot.setText('Automatic backup failed: '+str(exc))
    def reports_page(self):
        button('Create PDF report',self.report,self.tools,True);button('Structured JSON export',self.json_export,self.tools);button('Selected aircraft handover',self.selected_export,self.tools);button('Expense totals',self.expense_totals,self.tools)
        self.summary.setHtml('<h2>Records you can take with you</h2><p>Generate maintenance history, discrepancy, schedule, AD, component, parts or expense reports. Choose a date range; blank bounds include unknown dates.</p><p>CSV exports are available from each record list and honor its search filter. JSON includes record identities, relationships and audit metadata. Complete archives include all aircraft and attachments; review their scope before sharing.</p><p>Reports summarize recorded facts and user-entered thresholds. They do not certify compliance or airworthiness.</p>')
    @guarded
    def report(self):
        if not self.aircraft_id():raise ValueError('Select an aircraft first.')
        choices={'Maintenance history':'entry','Outstanding discrepancies':'item','Maintenance schedules':'schedule','AD tracking':'ad','Service bulletins':'sb','Components':'component','Component history':'component_event','Parts':'part','Expenses':'expense'}
        choice,ok=QInputDialog.getItem(self,'Report','Report type',list(choices),0,False)
        if not ok:return
        bounds,ok=QInputDialog.getText(self,'Date range','Optional YYYY-MM-DD,YYYY-MM-DD (leave blank for all records):')
        if not ok:return
        rows=self.store.records(choices[choice],self.aircraft_id())
        if choice=='Outstanding discrepancies':rows=[r for r in rows if r['data'].get('status') not in ['Closed','Canceled']]
        if bounds.strip():
            from .domain import iso_date
            start,end=bounds.split(',');iso_date(start);iso_date(end)
            rows=[r for r in rows if r['data'].get('date') and (not start or r['data']['date']>=start) and (not end or r['data']['date']<=end)]
        rows.sort(key=lambda r:r['data'].get('date',''))
        path,_=QFileDialog.getSaveFileName(self,'Save PDF report','maintenance-report.pdf','PDF (*.pdf)')
        if path:
            aircraft=self.store.get(self.aircraft_id(),True)
            work(self,'Generating report…',lambda:write_pdf(path,rows,aircraft,title=choice,history=True));PdfPreview(Path(path),self).exec()
    @guarded
    def selected_export(self):
        if not self.aircraft_id():raise ValueError('Select an aircraft first.')
        from .reports import export_aircraft
        path,_=QFileDialog.getSaveFileName(self,'Selected-aircraft handover (not restorable backup)','aircraft-handover.zip','ZIP (*.zip)')
        if path:work(self,'Verifying records and evidence…',lambda:export_aircraft(self.store,self.aircraft_id(),path))
    @guarded
    def expense_totals(self):
        from .reports import expense_summary
        group,ok=QInputDialog.getItem(self,'Expense totals across aircraft','Group by',['year','category','aircraft','component'],0,False)
        if not ok:return
        totals=expense_summary(self.store.records('expense'),group)
        dialog=QDialog(self);dialog.setWindowTitle('Recorded expenses — currencies kept separate');dialog.resize(700,500);layout=QVBoxLayout(dialog);view=QTextBrowser();view.setPlainText('No currency conversion. Blank amounts excluded.\n\n'+'\n'.join(f"{r['currency']}  {r['amount']}  |  {r['group']}" for r in totals));layout.addWidget(view);dialog.exec()
    @guarded
    def json_export(self):
        path,_=QFileDialog.getSaveFileName(self,'Export all aircraft and metadata','logbook.json','JSON (*.json)')
        if path:work(self,'Exporting structured records…',lambda:export_json(self.store,path))
    def help(self):
        dialog=QDialog(self);dialog.setWindowTitle('Quick start, workflows & regulatory references');dialog.resize(850,700);layout=QVBoxLayout(dialog);view=QTextBrowser();view.setOpenExternalLinks(True)
        guide=self.resources/'USER_GUIDE.md';view.setMarkdown(guide.read_text(encoding='utf-8') if guide.exists() else DISCLAIMER);layout.addWidget(view);dialog.exec()
    def theme(self,name):
        self.theme_name=name
        dark=name=='Dark';bg='#101b2b' if dark else '#eef2f6';panel='#17263a' if dark else '#ffffff';fg='#e9eff7' if dark else '#142337';border='#344b65' if dark else '#bbc8d5';alt='#1d3048' if dark else '#e9f0f7'
        self.setStyleSheet(f'''QWidget {{font-family:Segoe UI;font-size:10pt;color:{fg};background:{bg};}} QDialog,QScrollArea,QTabWidget::pane {{background:{panel};}} QLabel#title {{font-size:25pt;font-weight:600;}} QLabel#brand {{font-size:13pt;font-weight:700;color:#8cd9e2;}} QWidget#sidebar,QWidget#sidebar * {{background:#0b1422;color:#dce6f2;}} QPushButton {{background:{panel};border:1px solid {border};border-radius:5px;padding:9px 12px;}} QPushButton:hover {{border:1px solid #65cbd6;}} QPushButton#primary {{background:#2b8592;color:white;border:1px solid #61b8c3;font-weight:600;}} QPushButton:disabled {{color:#8894a3;}} QLineEdit,QComboBox,QPlainTextEdit,QTextBrowser,QListWidget,QTableWidget {{background:{panel};border:1px solid {border};border-radius:4px;padding:5px;selection-background-color:#2c657d;alternate-background-color:{alt};}} QHeaderView::section {{background:{alt};padding:8px;border:0;}} QListWidget::item {{padding:9px 3px;}} QListWidget::item:selected {{background:#24536b;}} QTabBar::tab {{padding:9px;background:{panel};border:1px solid {border};}} QTabBar::tab:selected {{border-bottom:2px solid #72cbd6;}} QLabel#muted {{color:#879aaf;font-size:9pt;}} QCheckBox::indicator {{width:18px;height:18px;}}''')
        self.refresh()
    def closeEvent(self,event):
        self.store.set_setting('window_size',[self.width(),self.height()]);event.accept()

class SetupWizard(QWizard):
    def __init__(self,main):
        super().__init__(main);self.main=main;self.setWindowTitle('Welcome to The Thrifty Pilot');self.resize(650,500)
        page=QWizardPage();page.setTitle('Your maintenance records, kept locally');layout=QVBoxLayout(page);label=QLabel(DISCLAIMER);label.setWordWrap(True);layout.addWidget(label)
        self.role=QComboBox();self.role.addItems(['Owner / pilot','Mechanic','Both','Recordkeeping only']);layout.addWidget(QLabel('How will you primarily use this logbook?'));layout.addWidget(self.role)
        self.add_aircraft=QCheckBox('Create an aircraft after setup');self.identity=QCheckBox('Configure my record identity after setup');layout.addWidget(self.add_aircraft);layout.addWidget(self.identity);self.addPage(page)
        page=QWizardPage();page.setTitle('Protect your records');layout=QVBoxLayout(page);self.folder=QLineEdit(str(main.store.root/'backups'));layout.addWidget(QLabel('Backup location (a separate drive is recommended)'));layout.addWidget(self.folder);button('Choose backup folder',self.choose,layout)
        self.demo=QCheckBox('Open a separate DEMO workspace with a fictional aircraft');layout.addWidget(self.demo);layout.addWidget(QLabel('You can cancel setup and explore now.\nDashboard → New entry → Preview / print → Attach signed copy → Back up.'));self.addPage(page)
    def choose(self):
        path=QFileDialog.getExistingDirectory(self,'Choose backup folder',self.folder.text())
        if path:self.folder.setText(path)
    def accept(self):
        self.main.store.set_setting('backup_folder',self.folder.text());self.main.store.set_setting('setup_done',True);self.main.store.set_setting('primary_role',self.role.currentText());super().accept()
        if self.add_aircraft.isChecked():self.main.edit('aircraft')
        if self.identity.isChecked():self.main.edit('profile')
        if self.demo.isChecked():
            import subprocess,sys
            command=[sys.executable,'--demo'] if getattr(sys,'frozen',False) else [sys.executable,'-m','logbook','--demo']
            subprocess.Popen(command,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
