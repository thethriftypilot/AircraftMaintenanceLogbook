from __future__ import annotations
import argparse
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import sys
import tempfile
from PySide6.QtCore import QLockFile, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication,QMessageBox,QFileDialog
from .storage import Store
from .services import Service

def resource_path():
    return Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent.parent))/'resources'

def seed_demo(store):
    if store.aircraft():return
    service=Service(store)
    aircraft=service.save_aircraft({'registration':'DEMO-ONLY','make':'Piper','model':'PA-28-161 Warrior (fictional)','serial_number':'DEMO-AIRFRAME-001','total_time':'2345.6','tach':'1850.2','hobbs':'2601.8','time_source':'Fictional demonstration','notes':'DEMO ONLY. Not an actual aircraft or maintenance record.'})
    service.save('entry',{'date':'2026-09-15','category':'Historical entry','description':'DEMO ONLY: fictional oil-change record for exploring this application. No maintenance was performed.','source_document':'Fictional sample; not an actual maintenance document.','performer':'DEMO PERSON'},aircraft['id'])
    service.save('item',{'title':'DEMO: inspect cabin light discrepancy','description':'Fictional example. No operational meaning.','status':'Open','priority':'Normal','date':'2026-10-01'},aircraft['id'])
    service.save('schedule',{'title':'DEMO annual reminder','applicability':'Applicable','last_date':'2026-09-15','months':'12','calendar_month':True,'notes':'Demonstration only; applicability not established.'},aircraft['id'])
    store.set_setting('setup_done',True)

def smoke(root):
    from .documents import write_pdf
    from .backup import backup,inspect_backup
    store=Store(root);seed_demo(store)
    aircraft=store.aircraft()[0]
    write_pdf(root/'smoke.pdf',store.records('entry',aircraft['id']),aircraft)
    path=backup(store,root/'smoke.zip');inspect_backup(path)
    return {'database_integrity':store.integrity(),'pdf_bytes':(root/'smoke.pdf').stat().st_size,'backup_bytes':path.stat().st_size}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--data-dir',type=Path);parser.add_argument('--demo',action='store_true');parser.add_argument('--smoke-test',type=Path);parser.add_argument('--screenshot',type=Path);args=parser.parse_args()
    app=QApplication(sys.argv);app.setOrganizationName('TheThriftyPilot');app.setApplicationName('AircraftMaintenanceLogbook');app.setStyle('Fusion')
    if args.smoke_test:
        args.smoke_test.mkdir(parents=True,exist_ok=True)
        try:
            result=smoke(args.smoke_test);(args.smoke_test/'result.json').write_text(json.dumps(result));return 0
        except Exception as exc:
            (args.smoke_test/'error.txt').write_text(str(exc));return 1
    root=args.data_dir or Path(os.environ.get('LOCALAPPDATA',Path.home()))/'TheThriftyPilot'/'AircraftMaintenanceLogbook'
    if args.demo:root=root/'demo-workspace'
    root.mkdir(parents=True,exist_ok=True)
    lock=QLockFile(str(root/'application.lock'));lock.setStaleLockTime(0)
    if not lock.tryLock(100):
        QMessageBox.warning(None,'Logbook already open','This data directory is open in another application instance. Close it first.');return 1
    handler=RotatingFileHandler(root/'application.log',maxBytes=1_000_000,backupCount=3,encoding='utf-8');logging.basicConfig(handlers=[handler],level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
    try:
        from .recovery import RecoveryRequired,recover,check_startup
        try:check_startup(root)
        except RecoveryRequired as exc:
            choice=QMessageBox.warning(None,'Recovery required — records not opened',str(exc)+'\n\nRecover the verified pre-operation archive? Choose No to select another verified ZIP, or Cancel to leave all files untouched.',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No|QMessageBox.StandardButton.Cancel,QMessageBox.StandardButton.Cancel)
            if choice==QMessageBox.StandardButton.Cancel:return 1
            archive=None
            if choice==QMessageBox.StandardButton.No:
                archive,_=QFileDialog.getOpenFileName(None,'Choose verified recovery archive',str(root/'backups'),'ZIP (*.zip)')
                if not archive:return 1
            recover(root,archive,confirmed=True)
        store=Store(root)
        if args.demo:seed_demo(store)
        from .ui import MainWindow,SetupWizard
        window=MainWindow(store,resource_path());window.setWindowIcon(QIcon(str(resource_path()/'app.ico')));window.show()
        if args.screenshot:
            def capture():
                args.screenshot.parent.mkdir(parents=True,exist_ok=True);window.grab().save(str(args.screenshot));app.quit()
            QTimer.singleShot(700,capture)
        elif not store.setting('setup_done',False):
            QTimer.singleShot(100,lambda:SetupWizard(window).exec())
        else:QTimer.singleShot(1500,window.automatic_backup)
        return app.exec()
    except Exception as exc:
        QMessageBox.critical(None,'Unable to start logbook',str(exc)+'\nYour data has not been intentionally deleted. Restore a verified backup if needed.');return 1
    finally:lock.unlock()

if __name__=='__main__':sys.exit(main())
