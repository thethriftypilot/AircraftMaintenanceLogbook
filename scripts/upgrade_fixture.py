"""Disposable populated v1 -> v2 evidence. No real-user directory access."""
from pathlib import Path
import sys,json,sqlite3,hashlib,zipfile
root=Path(__file__).resolve().parents[1]
mode,folder=sys.argv[1],Path(sys.argv[2]).resolve()
assert folder.is_relative_to(root/'build'),folder
folder.mkdir(parents=True,exist_ok=True)
def snapshot():
 with sqlite3.connect(folder/'logbook.db') as con:
  return {'schema':con.execute('PRAGMA user_version').fetchone()[0], 'records':con.execute('SELECT id,kind,aircraft_id,component_id,entry_id,amends_id,state,data FROM records ORDER BY id').fetchall(),'aircraft':con.execute('SELECT id,registration,data FROM aircraft ORDER BY id').fetchall(),'attachments':con.execute('SELECT * FROM attachments ORDER BY id').fetchall(),'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (folder/'attachments').glob('*')}}
if mode=='seed':
 source=folder.parent/'v1-source';source.mkdir(exist_ok=True)
 with zipfile.ZipFile(root/'dist/release/TheThriftyPilot-AircraftMaintenanceLogbook-Source-1.0.0.zip') as archive:
  for name in archive.namelist():
   parts=Path(name).parts
   if len(parts)>2 and parts[1]=='logbook' and name.endswith('.py'):
    target=source/Path(*parts[1:]);target.parent.mkdir(exist_ok=True,parents=True);target.write_bytes(archive.read(name))
 sys.path.insert(0,str(source))
 from logbook.storage import Store
 from logbook.services import Service
 from reportlab.pdfgen.canvas import Canvas
 store=Store(folder);service=Service(store);aircraft=service.save_aircraft({'registration':'UPGRADE-DEMO-ONLY','make':'Piper','model':'PA-28-161','total_time':'1250.5','notes':'FICTIONAL upgrade rehearsal'})
 record=service.save('entry',{'category':'Preventive maintenance','date':'2026-10-01','description':'FICTIONAL upgrade test. No actual work performed.','performer':'Fictional pilot','approver':'Fictional pilot','role':'Pilot','certificate_type':'Pilot','certificate_number':'TEST-NOT-VALID','authorization_basis':'Fictional fixture','pilot_eligible':True,'affirmed':True,'disposition':'Approval for physical signature'},aircraft['id'])
 record=service.finalize(record);pdf=folder/'fictional-evidence.pdf';canvas=Canvas(str(pdf));canvas.drawString(40,700,'FICTIONAL EVIDENCE FOR UPGRADE TEST - NOT A REAL SIGNATURE');canvas.save()
 attachment=service.attach(record['id'],pdf);service.transition(record,'Signed copy recorded','Test recorder',attachment)
 service.save('component',{'title':'Fictional engine','serial_number':'DEMO-ENGINE'},aircraft['id'])
 service.save('expense',{'date':'2026-10-01','amount':'123.45','currency':'USD'},aircraft['id'])
 before=snapshot();assert before['schema']==1
 (folder.parent/'before.json').write_text(json.dumps(before),encoding='utf-8')
elif mode=='check':
 before=json.loads((folder.parent/'before.json').read_text());after=json.loads(json.dumps(snapshot()));assert after.pop('schema')==2;before.pop('schema');assert before==after,'Record content or evidence changed on upgrade'
 sys.path.insert(0,str(root))
 from logbook.storage import Store
 from logbook.services import Service
 from logbook.backup import backup,restore
 store=Store(folder);archive=backup(store,folder/'rehearsal.zip');Service(store).save_aircraft({'registration':'TEMP-RESTORE-TEST'});restore(store,archive,True)
 restored=json.loads(json.dumps(snapshot()));restored.pop('schema');assert restored==before
 (root/'docs/upgrade-data-evidence.json').write_text(json.dumps({'legacy_schema':1,'upgraded_schema':2,'record_count':len(after['records']),'attachment_count':len(after['attachments']),'record_payloads_and_links_unchanged':True,'attachment_hashes_unchanged':True,'restore_rehearsal_passed':True,'migration_archives':[str(p) for p in (folder/'backups').glob('pre-migration*')]},indent=2),encoding='utf-8')
else:raise ValueError(mode)
