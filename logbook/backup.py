"""Verified archives and staged restore. Callers must exclude concurrent application writes."""
from __future__ import annotations
import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
import zipfile
import functools
from contextlib import closing
from pathlib import Path, PurePosixPath
from .storage import SCHEMA, Store, now, uid
from .recovery import flush_file,replace,install_stage

def exclusive(fn):
    @functools.wraps(fn)
    def locked(store,*args,**kwargs):
        with store.operation():return fn(store,*args,**kwargs)
    return locked

def digest(path):
    with open(path, 'rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

@exclusive
def backup(store: Store, destination: Path) -> Path:
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as folder:
        stage = Path(folder)
        db = stage / 'logbook.db'
        with store.connect() as source, closing(sqlite3.connect(db)) as target:
            source.backup(target)
        with closing(sqlite3.connect(db)) as con:
            names = [r[0] for r in con.execute('SELECT stored_name FROM attachments')]
            version=con.execute('PRAGMA user_version').fetchone()[0]
        files = {'logbook.db':db}
        for name in names:
            if Path(name).name != name or '/' in name or '\\' in name:
                raise ValueError('Unsafe attachment path in database.')
            files['attachments/'+name] = store.root / 'attachments' / name
        manifest = {'schema':version,'application':'1.1.0-rc1','created':now(),'files':{name:digest(path) for name,path in files.items()}}
        temporary = destination.with_name(destination.name + '.' + uid() + '.tmp')
        try:
            with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED) as archive:
                archive.writestr('manifest.json',json.dumps(manifest))
                for name,path in files.items():
                    archive.write(path,name)
            inspect_backup(temporary)
            flush_file(temporary);replace(temporary,destination);flush_file(destination)
        finally:
            temporary.unlink(missing_ok=True)
    store.set_setting('last_backup', {'path':str(destination.resolve()),'at':now(),'verified':True,'sha256':digest(destination)})
    return destination

def _extract(archive_path: Path, stage: Path):
    with zipfile.ZipFile(archive_path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or len(names) > 100000:
            raise ValueError('Duplicate or excessive archive members.')
        if sum(i.file_size for i in infos) > 4 * 1024**3:
            raise ValueError('Archive exceeds the 4 GB safety limit.')
        for name in names:
            path = PurePosixPath(name)
            if path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name:
                raise ValueError('Unsafe archive path.')
        if 'manifest.json' not in names or archive.getinfo('manifest.json').file_size > 16*1024*1024:
            raise ValueError('Missing or oversized manifest.')
        manifest = json.loads(archive.read('manifest.json'))
        if manifest.get('schema') not in (1,SCHEMA):
            raise ValueError('Unsupported backup schema version.')
        files = manifest.get('files', {})
        if set(names) != set(files) | {'manifest.json'} or 'logbook.db' not in files:
            raise ValueError('Archive and manifest disagree.')
        for name, expected in files.items():
            if name != 'logbook.db' and not (name.startswith('attachments/') and len(PurePosixPath(name).parts)==2):
                raise ValueError('Unexpected archive member.')
            target = stage / name
            target.parent.mkdir(parents=True,exist_ok=True)
            with archive.open(name) as source, open(target,'wb') as out:
                shutil.copyfileobj(source,out)
            if digest(target) != expected:
                raise ValueError('Backup checksum mismatch: ' + name)
        with closing(sqlite3.connect(stage / 'logbook.db')) as con:
            if con.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or con.execute('PRAGMA foreign_key_check').fetchall():
                raise ValueError('Backup database failed integrity verification.')
            if con.execute('PRAGMA user_version').fetchone()[0] != manifest['schema']:
                raise ValueError('Database schema does not match manifest.')
            for name, expected in con.execute('SELECT stored_name,sha256 FROM attachments'):
                if 'attachments/'+name not in files or files['attachments/'+name] != expected:
                    raise ValueError('Missing or changed attachment in backup.')
            manifest['aircraft_count'] = con.execute('SELECT count(*) FROM aircraft').fetchone()[0]
            manifest['record_count'] = con.execute('SELECT count(*) FROM records').fetchone()[0]
        (stage / 'attachments').mkdir(exist_ok=True)
        return manifest

def inspect_backup(path: Path):
    with tempfile.TemporaryDirectory() as folder:
        return _extract(path,Path(folder))

@exclusive
def restore(store: Store, archive: Path, confirmed=False,fault=lambda boundary:None):
    if not confirmed:
        raise ValueError('Explicit confirmation is required before replacing current data.')
    stage=store.root/('recovery-stage-'+uid());stage.mkdir()
    manifest=_extract(archive,stage);fault('stage_verified')
    recovery=store.root/'backups'/('pre-restore-'+uid()+'.zip')
    backup(store,recovery);fault('recovery_backup_verified')
    with store.connect() as con:
        result=con.execute('PRAGMA wal_checkpoint(TRUNCATE)').fetchone()
        if result[0]:raise ValueError('Database busy. Restore was not started.')
    fault('checkpointed')
    install_stage(store.root,stage,{'kind':'restore','recovery_archive':str(recovery),'source_archive':str(Path(archive).resolve())},fault)
    # Legacy archives are upgraded only after a complete recoverable installation.
    Store(store.root)
    store.set_setting('last_restore',{'at':now(),'recovery':str(recovery)})
    return manifest
