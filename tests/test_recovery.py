import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path
from contextlib import closing
import pytest
from logbook.storage import Store,DDL,encode,now
from logbook.services import Service
from logbook.backup import backup,restore,inspect_backup
from logbook.recovery import RecoveryRequired,recover,JOURNAL

class Interruption(BaseException):pass

BOUNDARIES=['stage_verified','recovery_backup_verified','checkpointed','journal_written','retained_logbook.db-wal','retained_logbook.db-shm','retained_logbook.db','retained_attachments','attachments_installed','database_installed','verified','committed']

@pytest.mark.parametrize('boundary',BOUNDARIES)
def test_every_restore_boundary(store,service,aircraft,tmp_path,boundary):
    archive=backup(store,tmp_path/'target.zip')
    service.save_aircraft({'registration':'AFTER'})
    def fault(step):
        if step==boundary:raise Interruption(step)
    with pytest.raises(Interruption):restore(store,archive,True,fault)
    if (store.root/JOURNAL).exists():
        with pytest.raises(RecoveryRequired):Store(store.root)
        with pytest.raises(RecoveryRequired):store.aircraft()
        with pytest.raises(RecoveryRequired):recover(store.root)
        recover(store.root,confirmed=True)
        assert len(Store(store.root).aircraft())==2
    else:
        assert len(Store(store.root).aircraft())==(1 if boundary=='committed' else 2)

def legacy(root):
    root.mkdir();(root/'attachments').mkdir()
    with closing(sqlite3.connect(root/'logbook.db')) as con:
        con.executescript(DDL+'PRAGMA user_version=1;')
        con.execute('INSERT INTO aircraft VALUES(?,?,?,?,?,?)',('a','LEGACY',encode({'registration':'LEGACY'}),1,now(),now()))
        con.execute('INSERT INTO records(id,kind,aircraft_id,state,data,created,modified) VALUES(?,?,?,?,?,?,?)',('entry','entry','a','Ready to print',encode({'description':'Original finalized meaning','category':'Historical entry','source_document':'TEST ONLY'}),now(),now()))
        con.commit()
    return root

def test_migration_preserves_bytes_and_is_idempotent(tmp_path):
    root=legacy(tmp_path/'legacy')
    with closing(sqlite3.connect(root/'logbook.db')) as con:before=con.execute('SELECT * FROM records').fetchall()
    store=Store(root)
    with store.connect() as con:
        assert con.execute('PRAGMA user_version').fetchone()[0]==2
        assert [tuple(r) for r in con.execute('SELECT * FROM records')]==before
    backups=list((root/'backups').glob('pre-migration*.zip'));assert len(backups)==1
    assert inspect_backup(backups[0])['schema']==1
    Store(root);assert len(list((root/'backups').glob('pre-migration*.zip')))==1
    with store.connect() as con:con.execute('PRAGMA user_version=3')
    with pytest.raises(ValueError,match='newer'):Store(root)

@pytest.mark.parametrize('boundary',['migration_backup_verified','migration_journal_written','migration_ddl_applied','migration_committed','migration_verified'])
def test_migration_interruption(tmp_path,boundary):
    root=legacy(tmp_path/'legacy')
    def fault(step):
        if step==boundary:raise Interruption(step)
    with pytest.raises(Interruption):Store(root,fault=fault)
    if (root/JOURNAL).exists():
        with pytest.raises(RecoveryRequired):Store(root)
        recover(root,confirmed=True)
    store=Store(root);assert store.get('entry')['data']['description']=='Original finalized meaning'
    assert store.integrity()

def test_missing_established_database_never_initializes(store):
    os.replace(store.path,store.root/'saved.db')
    with pytest.raises(RecoveryRequired):Store(store.root)
    assert not store.path.exists()

def test_legacy_missing_db_with_attachments_is_blocked(tmp_path):
    root=tmp_path/'legacy';(root/'attachments').mkdir(parents=True);(root/'attachments'/'old.pdf').write_bytes(b'%PDF-1.4')
    with pytest.raises(RecoveryRequired):Store(root)

def test_real_process_termination_and_recovery(store,service,aircraft,tmp_path):
    archive=backup(store,tmp_path/'target.zip');service.save_aircraft({'registration':'PRESERVE'})
    code="from pathlib import Path; import os,sys; from logbook.storage import Store; from logbook.backup import restore; restore(Store(Path(sys.argv[1])),Path(sys.argv[2]),True,lambda step:os._exit(77) if step=='retained_logbook.db' else None)"
    result=subprocess.run([sys.executable,'-c',code,str(store.root),str(archive)],timeout=30)
    assert result.returncode==77
    assert not store.path.exists()
    with pytest.raises(RecoveryRequired):Store(store.root)
    recover(store.root,confirmed=True);assert len(Store(store.root).aircraft())==2

def test_disk_full_before_swap_keeps_data(store,service,aircraft,tmp_path,monkeypatch):
    archive=backup(store,tmp_path/'good.zip')
    import logbook.backup as module
    def fail(*args,**kwargs):raise OSError(28,'Injected disk full')
    monkeypatch.setattr(module,'backup',fail)
    with pytest.raises(OSError):restore(store,archive,True)
    assert store.get(aircraft['id'],True)['registration']=='TEST-ONLY'

def test_windows_lock_failure_stays_recoverable(store,service,aircraft,tmp_path,monkeypatch):
    archive=backup(store,tmp_path/'good.zip')
    import logbook.recovery as module
    real=module.replace
    def fail(source,target):
        if Path(source)==store.path:raise PermissionError('Injected persistent antivirus lock')
        return real(source,target)
    monkeypatch.setattr(module,'replace',fail)
    with pytest.raises(PermissionError):restore(store,archive,True)
    with pytest.raises(RecoveryRequired):Store(store.root)
    monkeypatch.setattr(module,'replace',real);recover(store.root,confirmed=True)
    assert Store(store.root).integrity()

def test_cross_process_lock(store):
    code="import sys; from pathlib import Path; from logbook.storage import Store; Store(Path(sys.argv[1]))"
    with store.operation():
        result=subprocess.run([sys.executable,'-c',code,str(store.root)],capture_output=True,timeout=15)
    assert result.returncode!=0 and b'busy' in result.stderr

def test_duplicate_action_is_idempotent(service,aircraft,entry_data):
    first=service.save('entry',entry_data,aircraft['id'],request_id='same-action')
    second=service.save('entry',entry_data,aircraft['id'],request_id='same-action')
    assert first==second
    with pytest.raises(ValueError):service.save('entry',{**entry_data,'description':'different'},aircraft['id'],request_id='same-action')
