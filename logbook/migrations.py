"""Versioned, additive migration preserving every original record payload."""
import sqlite3
from contextlib import closing
from .storage import V2_DDL,uid
from .recovery import durable_json,JOURNAL,replace,flush_file,validate_database

def migrate_v1(store,fault=lambda boundary:None):
    from .backup import backup
    archive=store.root/'backups'/('pre-migration-v1-'+uid()+'.zip')
    backup(store,archive)
    fault('migration_backup_verified')
    with store.connect() as con:
        result=con.execute('PRAGMA wal_checkpoint(TRUNCATE)').fetchone()
        if result[0]:raise ValueError('Database is busy; migration postponed without changing its schema.')
    durable_json(store.root/JOURNAL,{'kind':'migration','from':1,'to':2,'recovery_archive':str(archive)})
    fault('migration_journal_written')
    with closing(sqlite3.connect(store.path)) as con:
        con.execute('PRAGMA foreign_keys=ON');con.execute('PRAGMA synchronous=FULL')
        before=con.execute('SELECT id,data,state,aircraft_id,component_id,amends_id FROM records ORDER BY id').fetchall()
        # executescript begins explicitly; statements are a fixed reviewed migration.
        try:
            con.executescript('BEGIN IMMEDIATE;'+V2_DDL)
            fault('migration_ddl_applied')
            after=con.execute('SELECT id,data,state,aircraft_id,component_id,amends_id FROM records ORDER BY id').fetchall()
            if before!=after:raise ValueError('Migration changed record meaning; refusing commit.')
            con.execute('PRAGMA user_version=2');con.commit()
        except BaseException:
            con.rollback();raise
        fault('migration_committed')
        con.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    flush_file(store.path);validate_database(store.path)
    fault('migration_verified')
    replace(store.root/JOURNAL,store.root/('recovery-migration-completed-'+uid()+'.json'))
