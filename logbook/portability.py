"""Explicit historical CSV imports and documented portable exports."""
import csv
import json
import os
from pathlib import Path
from .storage import encode, uid, now
from .domain import iso_date, quantity

CSV_FIELDS = ['date','description','total_time','performer','approver','certificate_type','certificate_number','references','source_document','notes']

def read_csv(path):
    with open(path,encoding='utf-8-sig',newline='') as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError('CSV requires unique column headers.')
        rows = list(reader)
        if len(rows)>50000:
            raise ValueError('Import at most 50,000 rows per file.')
        return reader.fieldnames,rows

def import_csv(store, aircraft_id, rows, mapping, source_name):
    staged = []
    for index,row in enumerate(rows,2):
        d = {target:row.get(source,'') or '' for target,source in mapping.items() if source}
        d.update(category='Historical entry',source_document=d.get('source_document') or source_name,disposition='Work documented only')
        try:
            iso_date(d.get('date','')); quantity(d.get('total_time'))
            if not d.get('description','').strip():
                raise ValueError('Description is required.')
        except ValueError as exc:
            raise ValueError(f'CSV row {index}: {exc}') from exc
        staged.append(d)
    with store.connect() as con:
        con.execute('BEGIN IMMEDIATE')
        for d in staged:
            identity,stamp=uid(),now()
            con.execute('INSERT INTO records(id,kind,aircraft_id,state,data,created,modified) VALUES(?,?,?,?,?,?,?)',(identity,'entry',aircraft_id,'Historical import requiring verification',encode(d),stamp,stamp))
            store.audit(con,identity,'historical CSV imported',detail={'source':source_name})
    return len(staged)

def export_json(store,path,aircraft_id=None):
    with store.connect() as con:
        con.execute('BEGIN')
        aircraft=[dict(r) for r in con.execute('SELECT * FROM aircraft'+(' WHERE id=?' if aircraft_id else ''),(aircraft_id,) if aircraft_id else ())]
        records=[dict(r) for r in con.execute('SELECT * FROM records'+(' WHERE aircraft_id=?' if aircraft_id else ''),(aircraft_id,) if aircraft_id else ())]
        ids={r['id'] for r in records}
        data={'schema':1,'generated':now(),'aircraft':aircraft,'records':records,'attachments':[dict(r) for r in con.execute('SELECT * FROM attachments') if r['record_id'] in ids],'audit':[dict(r) for r in con.execute('SELECT * FROM audit') if not aircraft_id or r['entity_id'] in ids|{aircraft_id}]}
    for r in data['aircraft']+data['records']:
        r['data']=json.loads(r['data'])
    temporary=Path(str(path)+'.tmp')
    temporary.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    os.replace(temporary,path)

def export_csv(records,path):
    keys=sorted({key for r in records for key in r['data']})
    def safe(value):
        value=str(value)
        return "'"+value if value.startswith(('=','+','-','@','\t','\r')) else value
    with open(path,'w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.writer(stream)
        writer.writerow(['id','kind','state']+keys)
        for record in records:
            writer.writerow([record['id'],record['kind'],record['state']]+[safe(record['data'].get(k,'')) for k in keys])
