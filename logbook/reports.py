"""Decimal expense summaries and explicitly scoped, non-restorable handover exports."""
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
import json
import tempfile
import zipfile
from .domain import quantity
from .storage import now
from .backup import digest
from .recovery import flush_file,replace

def expense_summary(records,group='year'):
    totals=defaultdict(Decimal)
    for record in records:
        if record['kind']!='expense':continue
        d=record['data'];amount=quantity(d.get('amount'))
        if amount is None:continue
        currency=d.get('currency','').strip().upper() or 'UNKNOWN CURRENCY'
        key=d.get('date','')[:4] or 'Unknown year' if group=='year' else record.get('aircraft_id','') if group=='aircraft' else record.get('component_id') or 'Whole aircraft' if group=='component' else d.get('category') or 'Uncategorized'
        totals[(currency,key)]+=amount
    return [{'currency':currency,'group':key,'amount':str(amount)} for (currency,key),amount in sorted(totals.items())]

def labor_amount(hours,rate):
    hours=quantity(hours,'Labor hours');rate=quantity(rate,'Labor rate')
    if hours is None or rate is None:raise ValueError('Enter labor hours and rate first.')
    return str(hours*rate)

def export_aircraft(store,aircraft_id,path):
    from .documents import write_pdf
    from .services import Service
    with store.operation(),tempfile.TemporaryDirectory() as folder:
        folder=Path(folder);aircraft=store.get(aircraft_id,True);records=store.records(aircraft_id=aircraft_id);ids={r['id'] for r in records}
        component_ids={r['component_id'] for r in records if r.get('component_id')}
        related=[store.get(identity) for identity in component_ids if identity not in ids]
        with store.connect() as con:
            evidence=[dict(r) for r in con.execute('SELECT * FROM attachments') if r['record_id'] in ids]
            audit=[dict(r) for r in con.execute('SELECT * FROM audit') if r['entity_id'] in ids|component_ids|{aircraft_id}]
            deliveries=[dict(r) for r in con.execute('SELECT * FROM deliveries') if r['inspection_id'] in ids]
        for a in evidence:
            if not Service(store).verify_attachment(a):raise ValueError('Handover aborted: missing or changed evidence.')
        payload={'format':'selected-aircraft-handover','version':1,'restorable':False,'generated':now(),'aircraft':aircraft,'records':records,'related_components':related,'attachments':evidence,'audit':audit,'deliveries':deliveries,'notice':'Portable record export, not a full database restore. Related component audit may identify past aircraft. Preserve originals.'}
        (folder/'records.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
        entries=sorted([r for r in records if r['kind']=='entry'],key=lambda r:r['data'].get('date',''))
        write_pdf(folder/'maintenance-history.pdf',entries,aircraft,title='Aircraft handover — maintenance history',history=True)
        files={'records.json':folder/'records.json','maintenance-history.pdf':folder/'maintenance-history.pdf'}
        for a in evidence:files['attachments/'+a['stored_name']]=store.root/'attachments'/a['stored_name']
        manifest={'format':'selected-aircraft-handover','restorable':False,'files':{n:digest(p) for n,p in files.items()}}
        target=Path(path);temporary=target.with_name(target.name+'.tmp')
        try:
            with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED) as out:
                out.writestr('handover-manifest.json',json.dumps(manifest))
                for n,p in files.items():out.write(p,n)
            with zipfile.ZipFile(temporary) as check:
                import hashlib
                for n,h in manifest['files'].items():
                    if hashlib.sha256(check.read(n)).hexdigest()!=h:raise ValueError('Export verification failed.')
            flush_file(temporary);replace(temporary,target)
        finally:temporary.unlink(missing_ok=True)
        return manifest
