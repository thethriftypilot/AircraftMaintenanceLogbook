"""Durable fail-closed recovery protocol. Never infer success from missing files."""
from __future__ import annotations
import json
import os
import sqlite3
import time
import uuid
from contextlib import closing
from pathlib import Path

JOURNAL = 'recovery-journal.json'
MARKER = 'data-directory.json'

class RecoveryRequired(ValueError):
    pass

def flush_file(path):
    with open(path,'r+b') as stream:
        os.fsync(stream.fileno())

def replace(source, target):
    # Antivirus/indexer sharing violations are bounded; never delete the destination.
    for attempt in range(5):
        try:
            os.replace(source,target)
            return
        except PermissionError:
            if attempt==4: raise
            time.sleep(0.05 * (attempt+1))

def durable_json(path, data):
    path=Path(path);temporary=path.with_name(path.name+'.new')
    with open(temporary,'w',encoding='utf-8') as out:
        json.dump(data,out,sort_keys=True);out.flush();os.fsync(out.fileno())
    replace(temporary,path)
    flush_file(path)
    # Directory fsync is supported on POSIX; Windows rename durability still depends
    # on the OS/filesystem/device. The surviving marker always causes fail-closed startup.
    if os.name!='nt':
        handle=os.open(path.parent,os.O_RDONLY)
        try:os.fsync(handle)
        finally:os.close(handle)

def check_startup(root):
    root=Path(root)
    if (root/JOURNAL).exists() or (root/(JOURNAL+'.new')).exists():
        raise RecoveryRequired('An interrupted restore or migration requires recovery. No database was opened. Use the verified recovery archive; do not remove the journal to bypass this check.')
    if not (root/'logbook.db').exists():
        evidence=(root/MARKER).exists() or any(root.glob('logbook.db-*')) or any(root.glob('recovery-*'))
        evidence = evidence or any((root/name).exists() and any((root/name).iterdir()) for name in ['attachments','backups'])
        if evidence:
            raise RecoveryRequired('An established data directory is missing logbook.db. Refusing to create an empty replacement. Select a verified backup for recovery.')

def validate_database(path):
    if not Path(path).is_file():raise RecoveryRequired('Expected database is missing.')
    with closing(sqlite3.connect(Path(path).as_uri()+'?mode=rw',uri=True)) as con:
        if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or con.execute('PRAGMA foreign_key_check').fetchall():
            raise RecoveryRequired('Database integrity verification failed.')
        return con.execute('PRAGMA user_version').fetchone()[0]

def install_stage(root,stage,journal,fault=lambda boundary:None):
    """After a durable journal exists, every partial state remains blocked on restart."""
    root=Path(root);stage=Path(stage)
    for path in stage.rglob('*'):
        if path.is_file():flush_file(path)
    journal=dict(journal,attempt=str(uuid.uuid4()),phase='prepared')
    durable_json(root/JOURNAL,journal);fault('journal_written')
    retained=root/('recovery-retained-'+journal['attempt']);retained.mkdir()
    # No app connection survives this boundary. Sidecars belong to the old DB only.
    for name in ['logbook.db-wal','logbook.db-shm','logbook.db','attachments']:
        if (root/name).exists():replace(root/name,retained/name)
        journal['phase']='retained '+name;durable_json(root/JOURNAL,journal);fault('retained_'+name)
    replace(stage/'attachments',root/'attachments')
    journal['phase']='attachments installed';durable_json(root/JOURNAL,journal);fault('attachments_installed')
    replace(stage/'logbook.db',root/'logbook.db')
    journal['phase']='database installed';durable_json(root/JOURNAL,journal);fault('database_installed')
    version=validate_database(root/'logbook.db')
    from .services import verify_all_files
    verify_all_files(root)
    durable_json(root/MARKER,{'schema':version,'established':True})
    journal['phase']='verified';durable_json(root/JOURNAL,journal);fault('verified')
    # Preserve completed journals as evidence rather than deleting them.
    replace(root/JOURNAL,retained/'completed-journal.json');fault('committed')

def recover(root,archive=None,confirmed=False,fault=lambda boundary:None):
    if not confirmed:raise RecoveryRequired('Explicit recovery confirmation is required.')
    root=Path(root).resolve()
    journal_path=root/JOURNAL
    journal=json.loads(journal_path.read_text(encoding='utf-8')) if journal_path.exists() else {}
    source=Path(archive) if archive else Path(journal.get('recovery_archive',''))
    if not source.is_file():raise RecoveryRequired('Choose a verified recovery ZIP. The journal does not identify an available archive.')
    from .backup import _extract
    from .locking import operation
    with operation(root):
        stage=root/('recovery-stage-'+str(uuid.uuid4()));stage.mkdir()
        _extract(source,stage)
        # Keep the original recovery source across retries, even if its journal was incomplete.
        install_stage(root,stage,{'kind':'recovery','recovery_archive':str(source.resolve())},fault)
        pending=root/(JOURNAL+'.new')
        if pending.exists():replace(pending,root/('recovery-unused-'+str(uuid.uuid4())+'.json'))

