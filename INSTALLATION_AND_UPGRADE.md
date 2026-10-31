# Installation, upgrade and recovery

Use the versioned 1.1.0-rc1 Setup EXE in dist/release, or extract its Portable ZIP and run AircraftMaintenanceLogbook.exe. Python is bundled. Installer uses the current Windows user's application directory and does not need elevation. Keep the entire portable folder together. Both modes default to %LOCALAPPDATA%\TheThriftyPilot\AircraftMaintenanceLogbook; portable does not mean data is stored beside the EXE. Use --data-dir with an explicit directory for isolated evaluation.

Before upgrading, close all application instances and create a verified full backup on a separate drive. Install the RC over the existing application using the same destination. The installer does not delete the external data directory. First open migrates schema 1→2 after creating a verified pre-migration-v1-*.zip under the data directory's backups folder. Retain this ZIP and your separate-drive copy. Schema 2 is rejected by version 1.0.0; do not downgrade in place.

For rollback, preserve the complete upgraded directory first. Use the original verified schema-1 backup to recover a separate data directory, then open that directory with the old application. For interrupted migration/restore, use the RC's startup recovery prompt; do not remove journal or retained files to bypass detection. Cancel means no recovery is attempted. Full backups contain all aircraft and should be protected accordingly. Selected-aircraft handover archives and JSON exports are not accepted as full backups.

Uninstall removes program files; user data is retained. Delete user records only through a separately deliberate user-managed process, never as part of this installation. The developer upgrade rehearsal uses disposable workspace paths and verifies data after uninstall; the default real-user path was not populated with test records.

This is an unsigned evaluation candidate. Verify SHA256SUMS.txt against the delivered files. Signing and SmartScreen reputation, a clean VM without Python, physical printers and independent aviation review are not passed acceptance gates.
