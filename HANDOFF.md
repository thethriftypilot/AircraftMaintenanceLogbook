# Project handoff — 1.1.0-rc1

The existing native Windows application has been stabilized and packaged as an **unsigned evaluation release candidate**. It remains offline, with no accounts, telemetry or subscriptions. Public distribution is authorized by the owner's subsequent publication request; see the [GitHub prerelease](https://github.com/thethriftypilot/AircraftMaintenanceLogbook/releases/tag/v1.1.0-rc1). All 1.0.0 installer/portable/source artifacts remain unchanged.

## Deliverables
- Installer: dist/release/TheThriftyPilot-AircraftMaintenanceLogbook-Setup-1.1.0-rc1.exe
- Portable: dist/release/TheThriftyPilot-AircraftMaintenanceLogbook-Portable-1.1.0-rc1.zip
- Clean source: dist/release/TheThriftyPilot-AircraftMaintenanceLogbook-Source-1.1.0-rc1.zip
- Checksums: dist/release/SHA256SUMS.txt
- Application source: logbook/; tests: tests/; packaging/rehearsal scripts: scripts/.
- Guides: USER_GUIDE.md, INSTALLATION_AND_UPGRADE.md, REGULATORY_REFERENCES.md, REGULATORY_LIMITATIONS.md, BUILD_WINDOWS.md.
- Assessment/evidence: TEST_RESULTS.md, COMPLETION_MATRIX.md, KNOWN_LIMITATIONS.md, RELEASE_NOTES.md, IMPLEMENTATION_LOG.md, docs/rc-evidence/ and docs/upgrade-*-evidence.json.

## What changed
Durable recovery journal and explicit startup recovery prevent silent empty replacement after interrupted restore. Schema 1→2 migration retains a verified rollback archive and preserves finalized payloads. Service checks bind closure/delivery to verified evidence; finalized snapshots and amendment chains preserve history. Inspection statements require explicit preparation/review; historical PDFs have no new signature block. Compact PDFs use true page dimensions. ELT/user-confirmed schedule calculations, oil prompts, component state, selected-aircraft handover, currency-separated expense totals, timeline/paging and preferences are available.

## Verified outcome
84 tests passed. Windows installer and portable run; real 1.0.0→RC upgrade on disposable populated data preserved all six record payloads and the managed attachment hash. Restore rehearsal, restart and uninstall preservation passed. Actual GUI/PDF layouts were rendered and sampled at 125/150/200%; a PDF-preview file-lock regression was found and fixed. Updated pinned-package advisory scan reports no known advisories; native dependency review is a separate limitation.

## Release decision
This candidate is ready for independent evaluation, not a declaration that every production gate is complete. Must complete: independent aviation/legal review, physical printer acceptance, clean Windows VM without Python, distribution signing/trust decision and real hardware power-loss/recovery review. Should improve: novice/screen-reader testing, smaller-window navigation, very large report/export workloads and richer expense/component UX. Deferred: compliant e-signatures, live FAA ingestion, FlightCost direct integration and billing/conversion automation. See KNOWN_LIMITATIONS.md for precise boundaries.

Back up before upgrading. Data defaults to %LOCALAPPDATA%\TheThriftyPilot\AircraftMaintenanceLogbook. Schema 2 must not be opened by the old executable; use a separate restored schema-1 copy for rollback. Do not remove recovery journals to bypass startup safeguards. No automatic archive retention purge occurs.
