"""Transactional SQLite repository. No business data is written in the install folder."""
from __future__ import annotations
import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = 2
def now() -> str:
    return datetime.now(timezone.utc).isoformat()
def uid() -> str:
    return str(uuid.uuid4())
def encode(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

DDL = '''
CREATE TABLE aircraft(id TEXT PRIMARY KEY, registration TEXT NOT NULL UNIQUE COLLATE NOCASE, data TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 1, created TEXT NOT NULL, modified TEXT NOT NULL);
CREATE TABLE records(id TEXT PRIMARY KEY, kind TEXT NOT NULL, aircraft_id TEXT REFERENCES aircraft(id), component_id TEXT REFERENCES records(id), entry_id TEXT REFERENCES records(id), amends_id TEXT REFERENCES records(id), state TEXT NOT NULL, data TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 1, created TEXT NOT NULL, modified TEXT NOT NULL);
CREATE INDEX records_aircraft_kind ON records(aircraft_id,kind,created);
CREATE INDEX records_component ON records(component_id);
CREATE TABLE attachments(id TEXT PRIMARY KEY, record_id TEXT NOT NULL REFERENCES records(id), filename TEXT NOT NULL, stored_name TEXT NOT NULL UNIQUE, sha256 TEXT NOT NULL, created TEXT NOT NULL);
CREATE TABLE audit(id INTEGER PRIMARY KEY, entity_id TEXT NOT NULL, action TEXT NOT NULL, actor TEXT NOT NULL, at TEXT NOT NULL, detail TEXT NOT NULL);
CREATE TABLE settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TRIGGER frozen_entry BEFORE UPDATE ON records WHEN OLD.kind='entry' AND OLD.state NOT IN ('Draft','Historical import requiring verification') AND (NEW.data<>OLD.data OR NEW.aircraft_id IS NOT OLD.aircraft_id OR NEW.component_id IS NOT OLD.component_id OR NEW.amends_id IS NOT OLD.amends_id OR NEW.kind<>OLD.kind OR NEW.created<>OLD.created OR NEW.state IN ('Draft','Historical import requiring verification')) BEGIN SELECT RAISE(ABORT,'Finalized content is immutable; create an amendment.'); END;
CREATE TRIGGER no_entry_delete BEFORE DELETE ON records WHEN OLD.kind='entry' BEGIN SELECT RAISE(ABORT,'Maintenance records cannot be deleted.'); END;
CREATE TRIGGER no_audit_update BEFORE UPDATE ON audit BEGIN SELECT RAISE(ABORT,'Audit events are append-only.'); END;
CREATE TRIGGER no_audit_delete BEFORE DELETE ON audit BEGIN SELECT RAISE(ABORT,'Audit events are append-only.'); END;
CREATE TRIGGER no_attachment_update BEFORE UPDATE ON attachments BEGIN SELECT RAISE(ABORT,'Attachments are immutable.'); END;
CREATE TRIGGER no_final_attachment_delete BEFORE DELETE ON attachments WHEN (SELECT state FROM records WHERE id=OLD.record_id) NOT IN ('Draft','Historical import requiring verification') BEGIN SELECT RAISE(ABORT,'Finalized evidence must be retained.'); END;
'''

V2_DDL = '''
CREATE TABLE amendments(original_id TEXT NOT NULL REFERENCES records(id), amendment_id TEXT PRIMARY KEY REFERENCES records(id), reason TEXT NOT NULL, created TEXT NOT NULL);
INSERT INTO amendments SELECT amends_id,id,COALESCE(json_extract(data,'$.amendment_reason'),'Legacy amendment'),created FROM records WHERE amends_id IS NOT NULL;
CREATE TABLE deliveries(id TEXT PRIMARY KEY, inspection_id TEXT NOT NULL REFERENCES records(id), attachment_id TEXT NOT NULL REFERENCES attachments(id), recipient TEXT NOT NULL, delivered_date TEXT NOT NULL, actor TEXT NOT NULL, created TEXT NOT NULL, UNIQUE(inspection_id,attachment_id,recipient,delivered_date));
CREATE INDEX attachments_record ON attachments(record_id);
CREATE INDEX records_timeline ON records(aircraft_id,json_extract(data,'$.date'),created);
CREATE TRIGGER frozen_entry_links BEFORE UPDATE ON records WHEN OLD.kind='entry' AND OLD.state NOT IN ('Draft','Historical import requiring verification') AND (NEW.id<>OLD.id OR NEW.entry_id IS NOT OLD.entry_id) BEGIN SELECT RAISE(ABORT,'Finalized links are immutable.'); END;
CREATE TRIGGER immutable_component_event BEFORE UPDATE ON records WHEN OLD.kind='component_event' BEGIN SELECT RAISE(ABORT,'Component history is append-only.'); END;
CREATE TRIGGER no_component_event_delete BEFORE DELETE ON records WHEN OLD.kind='component_event' BEGIN SELECT RAISE(ABORT,'Component history is append-only.'); END;
CREATE TRIGGER no_amendment_update BEFORE UPDATE ON amendments BEGIN SELECT RAISE(ABORT,'Amendment history is append-only.'); END;
CREATE TRIGGER no_amendment_delete BEFORE DELETE ON amendments BEGIN SELECT RAISE(ABORT,'Amendment history is append-only.'); END;
CREATE TRIGGER no_delivery_update BEFORE UPDATE ON deliveries BEGIN SELECT RAISE(ABORT,'Delivery evidence is append-only.'); END;
CREATE TRIGGER no_delivery_delete BEFORE DELETE ON deliveries BEGIN SELECT RAISE(ABORT,'Delivery evidence is append-only.'); END;
'''

class Store:
    def __init__(self, root: Path, fault=lambda boundary:None):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        from .recovery import check_startup,durable_json,MARKER
        from .locking import operation
        self.operation=lambda:operation(self.root)
        check_startup(self.root)
        for name in ['attachments', 'backups', 'logs']:
            (self.root / name).mkdir(exist_ok=True)
        self.path = self.root / 'logbook.db'
        with self.operation():
            self._initialize(fault)
        durable_json(self.root/MARKER,{'schema':SCHEMA,'established':True})

    def _initialize(self,fault):
        from .recovery import check_startup
        check_startup(self.root)
        new=not self.path.exists()
        with self.connect(create=new) as con:
            version = con.execute('PRAGMA user_version').fetchone()[0]
            if version > SCHEMA:
                raise ValueError('This database requires a newer application. No changes were made.')
            if version == 0:
                if con.execute("SELECT count(*) FROM sqlite_master WHERE type='table'").fetchone()[0]:
                    raise ValueError('Unrecognized database. Restore a verified backup.')
                if not new:
                    raise ValueError('Existing database has no recognized version. No empty replacement was created.')
                con.executescript('BEGIN IMMEDIATE;\n' + DDL + V2_DDL + '\nPRAGMA user_version=2; COMMIT;')
            con.execute('PRAGMA journal_mode=WAL')
        if version==1:
            from .migrations import migrate_v1
            migrate_v1(self,fault)

    @contextmanager
    def connect(self,create=False):
        from .recovery import check_startup
        with self.operation():
            check_startup(self.root)
            con = sqlite3.connect(self.path if create else self.path.as_uri()+'?mode=rw',uri=not create,timeout=15)
            con.row_factory = sqlite3.Row
            con.execute('PRAGMA foreign_keys=ON')
            con.execute('PRAGMA synchronous=FULL')
            try:
                with con:yield con
            finally:con.close()

    def audit(self, con, entity: str, action: str, actor='Local user', detail=None):
        con.execute('INSERT INTO audit(entity_id,action,actor,at,detail) VALUES(?,?,?,?,?)', (entity, action, actor, now(), encode(detail or {})))

    @staticmethod
    def unpack(row):
        if row is None:
            raise ValueError('Record no longer exists. Refresh the view.')
        result = dict(row)
        if 'data' in result:
            result['data'] = json.loads(result['data'])
        return result

    def get(self, record_id, aircraft=False):
        with self.connect() as con:
            return self.unpack(con.execute('SELECT * FROM ' + ('aircraft' if aircraft else 'records') + ' WHERE id=?', (record_id,)).fetchone())

    def aircraft(self):
        with self.connect() as con:
            return [self.unpack(r) for r in con.execute('SELECT * FROM aircraft ORDER BY registration')]

    def records(self, kind=None, aircraft_id=None):
        clauses, args = [], []
        if kind:
            clauses.append('kind=?'); args.append(kind)
        if aircraft_id:
            clauses.append('aircraft_id=?'); args.append(aircraft_id)
        with self.connect() as con:
            return [self.unpack(r) for r in con.execute('SELECT * FROM records' + (' WHERE ' + ' AND '.join(clauses) if clauses else '') + ' ORDER BY created DESC', args)]

    def page(self,kind=None,aircraft_id=None,query='',offset=0,limit=100,sort='Newest'):
        clauses=[];args=[]
        if kind:clauses.append('kind=?');args.append(kind)
        if aircraft_id:clauses.append('aircraft_id=?');args.append(aircraft_id)
        if query:clauses.append("instr(lower(data || state || id),lower(?))>0");args.append(query)
        where=' WHERE '+' AND '.join(clauses) if clauses else ''
        order={ 'Newest':'created DESC,id', 'Oldest':'created ASC,id', 'Work date':"json_extract(data,'$.date') DESC,created DESC,id"}.get(sort,'created DESC,id')
        with self.connect() as con:
            count=con.execute('SELECT count(*) FROM records'+where,args).fetchone()[0]
            rows=[self.unpack(r) for r in con.execute('SELECT * FROM records'+where+' ORDER BY '+order+' LIMIT ? OFFSET ?',args+[min(500,max(1,limit)),max(0,offset)])]
        return rows,count

    def setting(self, key, default=None):
        with self.connect() as con:
            row = con.execute('SELECT value FROM settings WHERE key=?', (key,)).fetchone()
            return json.loads(row[0]) if row else default

    def set_setting(self, key, value):
        with self.connect() as con:
            con.execute('INSERT INTO settings VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value', (key, encode(value)))

    def integrity(self):
        with self.connect() as con:
            return con.execute('PRAGMA integrity_check').fetchone()[0] == 'ok' and not con.execute('PRAGMA foreign_key_check').fetchall()
