# Windows installation

Target: Windows 11 x64. Windows 10 compatibility has not been exercised. Installer:
`dist/release/TheThriftyPilot-AircraftMaintenanceLogbook-Setup-1.1.0-rc1.exe`.

Run the installer as your normal user. It installs under `%LOCALAPPDATA%\Programs\TheThriftyPilot\AircraftMaintenanceLogbook` by default, creates a Start menu shortcut, offers an optional desktop shortcut and registers an uninstall entry. No service, startup task, browser extension, network account or telemetry is installed. No administrator access is required for the default location. Choose another writable application folder if needed.

The executable bundles its Python runtime, Qt and supporting libraries. Python and Git are not needed on an end-user machine. A clean machine without Python remains a separate acceptance test even when packaged smoke tests pass on the development machine.

Portable use: extract the ZIP, retaining the entire folder and `_internal` files, then run the executable. Portable refers to distribution; user data still uses the per-user data folder by default.

Data lives at `%LOCALAPPDATA%\TheThriftyPilot\AircraftMaintenanceLogbook`:
- `logbook.db` and transient SQLite WAL files: records, settings and audit metadata.
- `attachments/`: managed supporting PDFs and images.
- `backups/`: default backup location and pre-restore recovery archives.
- `application.log`: rotating non-content error log. `logs/` is reserved.
- `demo-workspace/`: separate optional fictional demo database.

Back up before installing an upgrade. Close the application before replacement. The installer leaves the separate user-data directory in place. Uninstall removes application files/shortcuts, not maintenance data. No automatic user-data purge is configured.

The build is unsigned; Windows may display an unknown-publisher prompt. A file hash can identify the artifact but does not prove trustworthiness. Signing is deferred until the publisher supplies credentials.


Schema 1→2 and recovery procedure: see [Installation and upgrade](INSTALLATION_AND_UPGRADE.md).
