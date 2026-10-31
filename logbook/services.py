"""Application services shared by UI, imports, tests and packaged smoke checks."""
from __future__ import annotations
import hashlib
import json
import shutil
import sqlite3
import os
import functools
from pathlib import Path
from .storage import Store, uid, now, encode
from .domain import iso_date, quantity, validate_entry

KINDS = {'entry', 'profile', 'component', 'component_event', 'item', 'schedule', 'ad', 'sb', 'part', 'expense'}
DECIMALS = {'total_time','tach','hobbs','cycles','since_overhaul','since_installation','amount','quantity','unit_cost','labor_hours','labor_rate','interval_hours','last_hours','due_hours','interval_cycles','last_cycles','due_cycles','lead_hours','lead_cycles','battery_used','battery_life_percent','excess_hours'}
DATES = {'date','last_date','due_date','installation_date','removal_date','last_annual','authorization_until','discrepancy_date','delivered_date','battery_expiration'}

def verify_all_files(root):
    from contextlib import closing
    root=Path(root)
    with closing(sqlite3.connect((root/'logbook.db').as_uri()+'?mode=rw',uri=True)) as con:
        for name,expected in con.execute('SELECT stored_name,sha256 FROM attachments'):
            if Path(name).name!=name or '/' in name or '\\' in name:raise ValueError('Unsafe attachment name.')
            path=root/'attachments'/name
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('Missing or changed supporting document: '+name)

def delivery_fingerprint(data):
    keys=['category','date','extent','total_time','discrepancies','discrepancy_date','approver','certificate_type','certificate_number','disposition']
    return hashlib.sha256(encode({key:data.get(key) for key in keys}).encode()).hexdigest()

def exclusive(fn):
    @functools.wraps(fn)
    def locked(self,*args,**kwargs):
        with self.store.operation():return fn(self,*args,**kwargs)
    return locked

class Service:
    def __init__(self, store: Store):
        self.store = store

    def validate_values(self, data):
        for key, value in data.items():
            if key in DECIMALS:
                quantity(value, key.replace('_', ' '))
            if key in DATES:
                iso_date(value, key.replace('_', ' '))
            if key in {'months','lead_days'} and value != '':
                if not str(value).isdigit() or (key == 'months' and int(value) < 1):
                    raise ValueError(f'{key} must be a positive whole number (lead days may be zero).')

    def save_aircraft(self, data, record=None):
        data = dict(data)
        registration = data.get('registration', '').strip().upper()
        if not registration:
            raise ValueError('Registration or clearly marked DEMO identifier is required.')
        data['registration'] = registration
        self.validate_values(data)
        identity, stamp = record['id'] if record else uid(), now()
        with self.store.connect() as con:
            if record:
                result = con.execute('UPDATE aircraft SET registration=?,data=?,revision=revision+1,modified=? WHERE id=? AND revision=?', (registration,encode(data),stamp,identity,record['revision']))
                if result.rowcount != 1:
                    raise ValueError('Aircraft changed in another window. Reopen it before saving.')
            else:
                con.execute('INSERT INTO aircraft(id,registration,data,created,modified) VALUES(?,?,?,?,?)', (identity,registration,encode(data),stamp,stamp))
            self.store.audit(con, identity, 'aircraft updated' if record else 'aircraft created', detail={'data': data})
        return self.store.get(identity, True)

    def _links(self, con, aircraft_id, component_id, entry_id, amends_id):
        for identity, expected in [(component_id, 'component'), (entry_id, 'entry'), (amends_id, 'entry')]:
            if identity:
                linked = con.execute('SELECT * FROM records WHERE id=?', (identity,)).fetchone()
                if not linked or linked['kind'] != expected:
                    raise ValueError(f'Invalid linked {expected}.')
                if linked['aircraft_id'] != aircraft_id:
                    # Component transfers preserve existing historical relationships.
                    if expected != 'component':
                        raise ValueError('Linked records must belong to the same aircraft.')
                    history = con.execute("SELECT 1 FROM records WHERE kind='component_event' AND component_id=? AND aircraft_id=?", (identity, aircraft_id)).fetchone()
                    if not history:
                        raise ValueError('Component has no installation history on this aircraft.')

    def save(self, kind, data, aircraft_id=None, record=None, component_id=None, entry_id=None, amends_id=None,request_id=None):
        if kind not in KINDS:
            raise ValueError('Unsupported record type.')
        if kind != 'profile' and not aircraft_id:
            raise ValueError('Select an aircraft first.')
        data = dict(data)
        self.validate_values(data)
        if kind=='expense' and data.get('amount'):
            currency=data.get('currency','').strip().upper()
            if len(currency)!=3 or not currency.isalpha():raise ValueError('Expenses with amounts require a three-letter currency code; currencies are never combined or converted.')
            data['currency']=currency
        if kind == 'entry' and data.get('category') == 'Historical entry':
            state = 'Historical import requiring verification'
        else:
            state = 'Draft' if kind == 'entry' else data.get('status', 'Active')
        identity, stamp = record['id'] if record else (request_id or uid()), now()
        with self.store.connect() as con:
            con.execute('BEGIN IMMEDIATE')
            self._links(con, aircraft_id, component_id, entry_id, amends_id)
            if request_id and not record:
                existing=con.execute('SELECT * FROM records WHERE id=?',(request_id,)).fetchone()
                if existing:
                    old=self.store.unpack(existing)
                    if old['data']==data and old['aircraft_id']==aircraft_id and old['kind']==kind and old['component_id']==component_id and old['entry_id']==entry_id and old['amends_id']==amends_id:return old
                    raise ValueError('Duplicate action identifier has different content.')
            if amends_id:
                original=con.execute('SELECT state FROM records WHERE id=?',(amends_id,)).fetchone()
                if kind!='entry' or original['state'] in ['Draft','Historical import requiring verification'] or not data.get('amendment_reason','').strip():
                    raise ValueError('An amendment needs a finalized original and a reason.')
            if kind == 'item' and data.get('status') == 'Closed':
                if not entry_id or not data.get('completion_notes'):
                    raise ValueError('Closing requires a corrective maintenance entry and completion notes.')
                linked = con.execute('SELECT state FROM records WHERE id=?', (entry_id,)).fetchone()[0]
                if linked != 'Signed copy recorded':
                    raise ValueError('Record signed corrective evidence before closing the item. This does not determine airworthiness.')
                self._verify_signed_evidence(con,entry_id)
            if kind=='item' and data.get('status')=='Deferred' and not data.get('completion_notes','').strip():
                raise ValueError('Deferral requires an independently determined legal basis and limitations in completion notes. No flight authorization is implied.')
            if kind == 'ad' and data.get('applicability') == 'Not applicable' and not data.get('rationale'):
                raise ValueError('An inapplicable AD requires a documented rationale.')
            if record:
                old = self.store.unpack(con.execute('SELECT * FROM records WHERE id=?', (identity,)).fetchone())
                if old['kind'] != kind or old['aircraft_id'] != aircraft_id:
                    raise ValueError('Record identity/aircraft cannot be changed here.')
                if kind == 'entry' and old['state'] not in ['Draft','Historical import requiring verification']:
                    raise ValueError('This entry is finalized. Create an amendment to correct it.')
                if kind == 'component_event':
                    raise ValueError('Component events are append-only. Add a correcting event.')
                result = con.execute('UPDATE records SET data=?,state=?,component_id=?,entry_id=?,revision=revision+1,modified=? WHERE id=? AND revision=?', (encode(data),state,component_id,entry_id,stamp,identity,record['revision']))
                if result.rowcount != 1:
                    raise ValueError('Record changed in another window. Reopen it before saving.')
            else:
                con.execute('INSERT INTO records(id,kind,aircraft_id,component_id,entry_id,amends_id,state,data,created,modified) VALUES(?,?,?,?,?,?,?,?,?,?)', (identity,kind,aircraft_id,component_id,entry_id,amends_id,state,encode(data),stamp,stamp))
                if amends_id:con.execute('INSERT INTO amendments VALUES(?,?,?,?)',(amends_id,identity,data['amendment_reason'],stamp))
            if kind=='component_event':
                if not component_id or not data.get('date') or not data.get('notes','').strip():raise ValueError('Component events require a component, date and details.')
                if data.get('action') in ['Installed','Removed']:
                    linked=self.store.unpack(con.execute('SELECT * FROM records WHERE id=?',(component_id,)).fetchone())
                    if linked['aircraft_id']!=aircraft_id:raise ValueError('Use Transfer component to install on another aircraft.')
                    component_data={**linked['data'],'installation_status':data['action'],'installation_date' if data['action']=='Installed' else 'removal_date':data['date']}
                    con.execute('UPDATE records SET data=?,revision=revision+1,modified=? WHERE id=?',(encode(component_data),stamp,component_id))
            self.store.audit(con, identity, f'{kind} saved', detail={'revision': (record['revision']+1) if record else 1})
        return self.store.get(identity)

    def finalize(self, record):
        errors = validate_entry(record['data'])
        if errors:
            raise ValueError('\n'.join(errors))
        return self.transition(record, 'Ready to print')

    def transition(self, record, state, actor='Local user', attachment_id=None):
        allowed = {'Draft': ['Ready to print'], 'Historical import requiring verification': ['Ready to print'], 'Ready to print': ['Printed / awaiting physical signature','Signed copy recorded'], 'Printed / awaiting physical signature': ['Signed copy recorded']}
        with self.store.connect() as con:
            con.execute('BEGIN IMMEDIATE')
            old = self.store.unpack(con.execute('SELECT * FROM records WHERE id=?', (record['id'],)).fetchone())
            if old['kind'] != 'entry' or state not in allowed.get(old['state'], []):
                raise ValueError('Invalid record state transition.')
            if state == 'Ready to print':
                errors = validate_entry(old['data'])
                if errors:
                    raise ValueError('\n'.join(errors))
                if old['data'].get('disposition')=='Not approved':
                    deliveries=con.execute('SELECT a.* FROM deliveries d JOIN attachments a ON a.id=d.attachment_id WHERE d.inspection_id=?',(old['id'],)).fetchall()
                    if not deliveries or not all(self.verify_attachment(dict(a)) for a in deliveries):raise ValueError('Nonapproval requires verified signed discrepancy-list evidence and recorded delivery before finalization.')
                    acknowledged=con.execute("SELECT detail FROM audit WHERE entity_id=? AND action='signed discrepancy list delivery recorded' ORDER BY id DESC LIMIT 1",(old['id'],)).fetchone()
                    if not acknowledged or json.loads(acknowledged[0]).get('content_sha256')!=delivery_fingerprint(old['data']):raise ValueError('Inspection findings or identity changed after delivery. Record delivery of the corrected signed list.')
                for attachment in con.execute('SELECT * FROM attachments WHERE record_id=?',(old['id'],)):
                    if not self.verify_attachment(dict(attachment)):raise ValueError('Supporting evidence is missing or changed. Restore it before finalizing.')
                # Freeze identification as it appeared when content was finalized.
                aircraft = self.store.unpack(con.execute('SELECT * FROM aircraft WHERE id=?', (old['aircraft_id'],)).fetchone())
                snapshot = dict(old['data'])
                snapshot['aircraft_snapshot'] = aircraft
                snapshot['linked_parts_snapshot']=[json.loads(r[0]) for r in con.execute("SELECT data FROM records WHERE kind='part' AND entry_id=?",(old['id'],))]
                if old['component_id']:
                    snapshot['component_snapshot'] = self.store.unpack(con.execute('SELECT * FROM records WHERE id=?', (old['component_id'],)).fetchone())
                con.execute('UPDATE records SET data=? WHERE id=?', (encode(snapshot),old['id']))
            if state == 'Signed copy recorded':
                if old['data'].get('category')=='Historical entry':raise ValueError('Historical transcription cannot receive a new maintenance signature. Attach the original source scan instead.')
                if old['data'].get('disposition')=='Not approved' and not con.execute('SELECT 1 FROM deliveries WHERE inspection_id=?',(old['id'],)).fetchone():
                    raise ValueError('Record signed discrepancy-list evidence and delivery acknowledgment first.')
                if not actor.strip():
                    raise ValueError('Identify who recorded the externally signed copy.')
                attachment = con.execute('SELECT * FROM attachments WHERE id=? AND record_id=?', (attachment_id,record['id'])).fetchone()
                if not attachment or not self.verify_attachment(dict(attachment)):
                    raise ValueError('A verified managed copy of the signed document is required.')
            result = con.execute('UPDATE records SET state=?,revision=revision+1,modified=? WHERE id=? AND revision=?', (state,now(),record['id'],record['revision']))
            if result.rowcount != 1:
                raise ValueError('Record changed. Reopen it before continuing.')
            self.store.audit(con, record['id'], state, actor, {'attachment_id':attachment_id})
        return self.store.get(record['id'])

    def amend(self, record, reason):
        record=self.store.get(record['id'])
        if record['state'] in ['Draft','Historical import requiring verification'] or not reason.strip():
            raise ValueError('Amendments require a finalized original and a correction reason.')
        data = dict(record['data'])
        data.pop('aircraft_snapshot',None)
        data.pop('component_snapshot',None)
        data.update(amendment_reason=reason, affirmed=False, list_delivered=False,statement_reviewed=False)
        return self.save('entry', data, record['aircraft_id'], component_id=record['component_id'], amends_id=record['id'])

    def transfer_component(self, component, target_id, event_date, notes):
        iso_date(event_date)
        if not event_date or not notes.strip():
            raise ValueError('Transfer requires date and installation/removal details.')
        with self.store.connect() as con:
            con.execute('BEGIN IMMEDIATE')
            if not con.execute('SELECT 1 FROM aircraft WHERE id=?', (target_id,)).fetchone():
                raise ValueError('Select a valid destination aircraft.')
            for aircraft, action in [(component['aircraft_id'], 'Removed'), (target_id, 'Installed')]:
                identity, stamp = uid(), now()
                con.execute('INSERT INTO records(id,kind,aircraft_id,component_id,state,data,created,modified) VALUES(?,?,?,?,?,?,?,?)', (identity,'component_event',aircraft,component['id'],'Recorded',encode({'date':event_date,'action':action,'notes':notes}),stamp,stamp))
            result = con.execute('UPDATE records SET aircraft_id=?,revision=revision+1,modified=? WHERE id=? AND revision=?', (target_id,now(),component['id'],component['revision']))
            if result.rowcount != 1:
                raise ValueError('Component changed. Reopen it.')
            self.store.audit(con,component['id'],'component transfer',detail={'from':component['aircraft_id'],'to':target_id,'date':event_date})
            updated={**component['data'],'installation_status':'Installed','installation_date':event_date,'removal_date':''}
            con.execute('UPDATE records SET data=? WHERE id=?',(encode(updated),component['id']))

    def attach(self, record_id, source: Path):
        source = Path(source)
        extension = source.suffix.lower()
        if extension not in {'.pdf','.jpg','.jpeg','.png'}:
            raise ValueError('Supported attachments are PDF, JPEG and PNG only.')
        if source.stat().st_size > 100 * 1024 * 1024:
            raise ValueError('Attachment exceeds 100 MB. Split it into smaller documents.')
        with open(source,'rb') as stream:header=stream.read(8)
        valid = header.startswith(b'%PDF-') if extension == '.pdf' else header.startswith(b'\x89PNG\r\n\x1a\n') if extension == '.png' else header.startswith(b'\xff\xd8\xff')
        if not valid:
            raise ValueError('File content does not match its document extension.')
        self.store.get(record_id)
        digest=hashlib.sha256(source.read_bytes()).hexdigest()
        for existing in self.attachments(record_id):
            if existing['sha256']==digest and self.verify_attachment(existing):return existing['id']
        identity = uid()
        stored = identity + extension
        target = self.store.root / 'attachments' / stored
        try:
            with open(source,'rb') as src,open(target,'xb') as dst:
                shutil.copyfileobj(src,dst);dst.flush();os.fsync(dst.fileno())
            if hashlib.sha256(target.read_bytes()).hexdigest()!=digest:raise ValueError('Source changed while copying. Retry attachment.')
            with self.store.connect() as con:
                con.execute('INSERT INTO attachments VALUES(?,?,?,?,?,?)', (identity,record_id,source.name,stored,digest,now()))
                self.store.audit(con, record_id, 'attachment added', detail={'id':identity,'sha256':digest})
        except Exception:
            target.unlink(missing_ok=True)
            raise
        return identity

    def attachments(self, record_id):
        with self.store.connect() as con:
            return [dict(r) for r in con.execute('SELECT * FROM attachments WHERE record_id=? ORDER BY created', (record_id,))]

    def verify_attachment(self, attachment):
        name = attachment['stored_name']
        if Path(name).name != name or '/' in name or '\\' in name:
            return False
        path = self.store.root / 'attachments' / name
        return path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == attachment['sha256']

    def remove_attachment(self, attachment):
        with self.store.connect() as con:
            row=con.execute('SELECT * FROM attachments WHERE id=?',(attachment['id'],)).fetchone()
            if not row:raise ValueError('Attachment does not exist.')
            attachment=dict(row)
        with self.store.connect() as con:
            con.execute('DELETE FROM attachments WHERE id=?', (attachment['id'],))
            self.store.audit(con,attachment['record_id'],'draft attachment removed',detail={'id':attachment['id']})
        (self.store.root / 'attachments' / attachment['stored_name']).unlink(missing_ok=True)

    def _verify_signed_evidence(self,con,entry_id):
        audit=con.execute("SELECT detail FROM audit WHERE entity_id=? AND action='Signed copy recorded' ORDER BY id DESC LIMIT 1",(entry_id,)).fetchone()
        identity=json.loads(audit[0]).get('attachment_id') if audit else None
        evidence=con.execute('SELECT * FROM attachments WHERE id=? AND record_id=?',(identity,entry_id)).fetchone()
        if not evidence or not self.verify_attachment(dict(evidence)):raise ValueError('The linked signed evidence is missing or changed.')

    def record_delivery(self,inspection_id,attachment_id,recipient,delivered_date,actor):
        if not recipient.strip() or not actor.strip() or not delivered_date:raise ValueError('Recipient, delivery date and recorder are required.')
        iso_date(delivered_date)
        with self.store.connect() as con:
            inspection=self.store.unpack(con.execute('SELECT * FROM records WHERE id=?',(inspection_id,)).fetchone())
            if inspection['kind']!='entry' or inspection['data'].get('disposition')!='Not approved' or 'inspection' not in inspection['data'].get('category','').lower():raise ValueError('Delivery must link to a nonapproved inspection.')
            evidence=con.execute('SELECT * FROM attachments WHERE id=? AND record_id=?',(attachment_id,inspection_id)).fetchone()
            if not evidence or not self.verify_attachment(dict(evidence)):raise ValueError('Verified signed discrepancy-list evidence must belong to this inspection.')
            existing=con.execute('SELECT id FROM deliveries WHERE inspection_id=? AND attachment_id=? AND recipient=? AND delivered_date=?',(inspection_id,attachment_id,recipient,delivered_date)).fetchone()
            if existing:
                self.store.audit(con,inspection_id,'signed discrepancy list delivery recorded',actor,{'delivery_id':existing[0],'attachment_id':attachment_id,'content_sha256':delivery_fingerprint(inspection['data'])})
                return existing[0]
            identity=uid();con.execute('INSERT INTO deliveries VALUES(?,?,?,?,?,?,?)',(identity,inspection_id,attachment_id,recipient,delivered_date,actor,now()))
            self.store.audit(con,inspection_id,'signed discrepancy list delivery recorded',actor,{'delivery_id':identity,'attachment_id':attachment_id,'content_sha256':delivery_fingerprint(inspection['data'])})
            return identity

    def amendment_chain(self,record_id):
        with self.store.connect() as con:
            rows=[self.store.unpack(r) for r in con.execute("SELECT * FROM records WHERE kind='entry'")]
        by_id={r['id']:r for r in rows};current=by_id[record_id];seen=set()
        while current.get('amends_id') and current['amends_id'] in by_id:
            if current['id'] in seen:raise ValueError('Invalid cyclic amendment history.')
            seen.add(current['id']);current=by_id[current['amends_id']]
        family={current['id']}
        while True:
            added={r['id'] for r in rows if r.get('amends_id') in family}-family
            if not added:break
            family.update(added)
        return sorted([r for r in rows if r['id'] in family],key=lambda r:r['created'])

for _name in ['save_aircraft','save','finalize','transition','amend','transfer_component','attach','remove_attachment','record_delivery']:
    setattr(Service,_name,exclusive(getattr(Service,_name)))
