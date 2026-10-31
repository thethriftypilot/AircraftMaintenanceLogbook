# Security and privacy

No telemetry, advertisements, online login, subscriptions, automatic update calls or cloud transmission. Core code has no application HTTP client. Optional website/reference links use the OS browser only after user action. Maintenance descriptions and full certificate numbers are not written to the rotating error log; some user-entered data necessarily appears in the database, exports and PDFs.

Data is unencrypted local SQLite and files. Windows account security, disk encryption and backup media access are the user's responsibility. No enterprise access-control claims. A single-instance lock and optimistic revisions address accidental concurrent edits, not hostile local users.

SQL statements parameterize user data. Record kinds are allowlisted. Attachment names are generated UUIDs, content prefixes and extensions are checked, and only PDF/JPEG/PNG are accepted up to 100 MB. Files are opened through system document viewers after hash verification. The app does not execute uploaded binaries. PDF viewers can have their own risks: keep them updated. There is no embedded malware scanner.

Backup verification checks exact archive membership, path confinement, total extraction size (4 GB), SHA-256, SQLite integrity, foreign keys, schema and each attachment's hash. Restore requires explicit confirmation and retains current-state recovery. Zip archives are not encrypted. Do not restore untrusted archives as a substitute for provenance review.

Finalized records are protected from normal API/UI rewrites and ordinary SQL data updates by triggers. Audit events are append-only in normal operation. These controls do not protect against an administrator replacing a database or executable. This is not a cryptographic ledger.

Report a reproducible issue using the repository issue template after publication. Never include real certificate numbers, private records or signed scans in a public issue.
