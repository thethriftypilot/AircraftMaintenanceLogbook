# Architecture

The entry point is `logbook/__main__.py`, wrapped by `launch.py` for PyInstaller. One `QLockFile` per data directory prevents duplicate GUI instances. A reentrant thread lock plus OS file lock serializes whole service/backup/restore operations across processes. SQLite connections are short-lived and always closed; each write is transactional with foreign keys and FULL synchronous WAL mode. UI windows use optimistic revisions to reject stale writes.

Modules:
- `domain.py`: decimal/time/date rules, inspection and pilot validation; no Qt dependency.
- `storage.py`: schema initialization, transactions, queries, audit and settings. SQLite's maintained standard-library driver is the explicit persistence layer rather than an ORM.
- `services.py`: aircraft/record commands, link checks, immutable finalization, snapshots, transitions, amendments, attachments and component transfers.
- `backup.py`: live SQLite backup API, manifest/hash verification, safe extraction and staged replacement with retained recovery.
- `documents.py`: shared record content for formatted preview and ReportLab PDFs; physical signatures only.
- `portability.py`: historical CSV mapping/import, CSV and schema-versioned JSON export.
- `forms.py`: declarative field metadata and accessible native controls.
- `ui.py`: native Qt forms, lists, navigation, QPdfView preview, QPrintDialog, modal background tasks, wizard and help.
- `resources/regulatory.json`: separately maintained references and guidance, bundled offline.

The GUI never creates legal authorization. Roles and affirmations are user input. Immutable content includes aircraft/component identification snapshots; later profile changes do not rewrite finalized PDF identity. State transitions are audited. Signed scans are immutable copies linked to actor/time and SHA-256, not cryptographic signatures.

Restore stages on the same volume, verifies before mutation, closes connections, checkpoints WAL and saves a current-state recovery archive. Individual renames are atomic; the multi-file sequence is not crash-atomic as a whole. Recovery artifacts are deliberately retained. A power-loss recovery drill remains required.

Reports/import/backups use a QThread while a modal progress dialog prevents conflicting UI writes. Lists use bounded SQLite paging and persistent filters/order; dashboard aggregation, reports and exports still load collections into memory. No background network activity or cloud integration is present.


RC modules: locking.py owns directory operation locks; recovery.py owns durable journal/retained-file installation and startup refusal; migrations.py owns version-1→2 preservation; statements.py supplies explicit user-requested draft wording and limited contradiction checks; reports.py supplies Decimal summaries and scoped, non-restorable handover archives. QPdfDocument reads an owned QBuffer, so preview does not retain a Windows file handle to generated temporary PDFs.
