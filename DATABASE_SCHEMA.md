# Database and portable schema

SQLite schema is `PRAGMA user_version=2`. Existing version 1 migrates through logbook/migrations.py: verified schema-1 archive, WAL checkpoint, durable journal, additive transaction, full original-payload comparison, commit/flush/integrity check and retained completion journal. Migration faults leave startup blocked for explicit recovery. Newer versions are refused; no silent downgrade. Established directories missing their database are refused rather than silently initialized.

| Table | Keys and purpose |
| --- | --- |
| aircraft | UUID PK; case-insensitive unique registration; JSON data; integer revision; UTC created/modified timestamps |
| records | UUID PK; kind; aircraft FK; component/entry/amendment self-FKs; state; JSON data; revision and UTC timestamps |
| attachments | UUID PK; record FK; original filename; unique managed basename; SHA-256; created timestamp |
| audit | integer PK; entity UUID; action; actor; timestamp; JSON detail; append-only triggers |
| settings | key PK and JSON value, including preferences and last backup/restore |

Record kinds: entry, profile, component, component_event, item, schedule, ad, sb, part, expense. Field contracts are in `forms.py`; schema version changes are required if those contracts become incompatible. Decimal values are stored as strings and interpreted with Decimal. Blank is unknown, never zero. Dates are ISO YYYY-MM-DD; timestamps are UTC.

Entry state: Draft or Historical import requiring verification → Ready to print → Printed / awaiting physical signature → Signed copy recorded. A signed copy may also be recorded directly from Ready to print if it was printed externally. Finalization freezes content through service validation and database triggers. Amendments are new entries with `amends_id`; the original remains retained, and the list derives an amended marker from immutable relationships. Amendment history displays the entire original/correction chain.

JSON export schema 1: `schema`, `generated`, `aircraft[]`, `records[]`, `attachments[]`, `audit[]`. Aircraft/record `data` is an object. UUID relationship fields retain their meaning. Attachment bytes are not embedded in JSON; use a complete ZIP backup for lossless round-trip restore. JSON import is not exposed. CSV import is historical transcription only and never imports approval states.

Backup ZIP: `manifest.json`, `logbook.db`, `attachments/<uuid>.<extension>`. Manifest contains schema, application version, UTC creation and SHA-256 for each file. All members must match the manifest; extra members, duplicate names, absolute paths, parent traversal, Windows drive separators, oversized archives and corrupt databases are rejected.


Schema 2 adds amendments(original_id, amendment_id PK, reason, created) and deliveries(id PK, inspection_id, attachment_id, recipient, delivered_date, actor, created). Both are append-only; delivery references prevent evidence deletion. New triggers freeze final entry identity/entry links and component events. The delivery audit records a content fingerprint; changed inspection findings/identity require renewed acknowledgment. Finalized payloads remain byte-for-byte unchanged during migration, even if older records lack newer optional fields.

Recovery journal protocol: verify stage → verify pre-operation archive → checkpoint → durable journal → retain old WAL/SHM/database/attachments → install attachments → install DB → verify DB/files → write established-directory marker → retain completed journal. Any pending journal/.new causes fail-closed startup. Recovery reinstalls a verified archive using the same retained-file protocol. Per-directory thread/process operation locks encompass backup/restore/mutation, while QLockFile prevents a second GUI on the same directory.
