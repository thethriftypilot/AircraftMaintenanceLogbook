# Release-candidate verification — 1.1.0-rc1

Local test date 2026-10-30 America/New_York; UTC evidence crosses into October 31. Environment: Windows 11 x64 build 26100, CPython 3.13.7, PySide6 6.10.1, ReportLab 4.4.5, PyInstaller 6.17.0, Inno Setup 6.7.3. Exact dependency pins are in requirements-lock.txt. No independent machine or aviation reviewer participated.

| Command / scenario | Result and evidence |
|---|---|
| `.venv/Scripts/python.exe -m pytest -q --junitxml=docs/baseline-1.0.0-tests.xml` before edits | 41 passed; exit 0; original implementation baseline |
| `./scripts/build.ps1` (reruns pytest before packaging) | Exit 0; **84 passed, zero failed/skipped/errors**, 12.334 seconds; docs/test-results.xml and docs/rc-build-log.txt |
| `.venv/Scripts/python.exe -m pip_audit -r requirements-lock.txt --no-deps --disable-pip --format json --output docs/dependency-audit.json` | Final exit 0; no known advisories in pinned packages. Initial exit 1: 99 advisories in test-only pypdf/pytest; fixed pins and reran. Before/after JSON retained |
| `.venv/Scripts/python.exe scripts/visual_evidence.py` plus Poppler `pdftoppm` | Exit 0; actual Qt screenshots/PDFs/rendered PNGs in docs/rc-evidence; pdf-inventory.json records sizes/pages |
| `QT_SCALE_FACTOR=1.25`, `1.5`, `2`: `.venv/Scripts/python.exe scripts/walkthrough.py` | Final each exit 0; 16 recorded developer actions, zero final errors, draft survives reopen. Actual PDF preview renders. Initial run exposed PDF file lock; fixed using QBuffer and added regression test |
| Packaged exe `--smoke-test build/packaged-smoke-rc1` | Exit 0; DB integrity, PDF and verified backup; build/packaged-smoke-rc1/result.json |
| `./scripts/upgrade_smoke.ps1` | Exit 0; real 1.0.0 installer → populated v1 data → RC installer same app folder → migration, native UI, restart, restore rehearsal, uninstall. docs/upgrade-installer-evidence.json and docs/upgrade-data-evidence.json |
| Extract final Portable ZIP; run extracted exe `--smoke-test` on disposable directory | Exit 0; docs/portable-rc-smoke.json |
| Original release SHA-256 comparison | All three 1.0.0 artifacts match docs/v1-evidence/SHA256SUMS.txt |
| Authenticode inspection | Unsigned; docs/rc-signature-status.json. No SmartScreen reputation claim |

## Coverage behind the count

- Original data workflows: multi-aircraft persistence, decimals/time sources, authority guards, finalization/amendment immutability, component transfers, signed evidence, backups, malicious/corrupt archive rejection, historical CSV and GUI autosave.
- Recovery: 12 restore boundaries, 5 migration boundaries, preserved legacy payloads, missing established DB refusal, newer-schema rejection, simulated disk-full, persistent Windows rename denial, cross-process lock and real subprocess os._exit termination after moving the original DB. Recovery uses a verified archive and integrity/hash checks. These tests do not simulate controller cache loss or physical power interruption.
- Accuracy: conflicting inspection dispositions, reviewer reset, cross-record delivery rejection, changes invalidating delivery, missing signed evidence blocking closure, historical/history no-new-signature behavior, ELT exact thresholds and conservative time/exception handling.
- Scope/math: selected-aircraft export excludes unrelated aircraft records and is rejected as a full backup; Decimal currency totals remain separate; pagination and amendment chain preserve identities.
- GUI: five tests (headless Qt to avoid workstation accessibility/COM interference), plus native widget captures and installed native launch. PDF memory-buffer test proves the temporary file can be deleted while preview is open.

## Visual evidence and usability limits

The compact work fixture is **432 × 384 pt (6 × 5⅓ in)**; historical compact is 432 × 320 pt. Letter fixtures are 612 × 792 pt. Long historical fixture has six pages. Inspected compact work, historical compact, Letter nonapproval, discrepancy list, last long page, editor/list layouts, installed dashboard and 200% actual PDF preview. Automated long-entry tests check content tail, Unicode, page count and physical signature on the final page. No physical printer was used.

The developer-driven walkthrough records five mouse-click/open actions, eight field-entry actions and three service/preview/reopen actions (16 total); file-save/format dialogs and installation timing are bypassed. Machine execution time is not human task time. A real novice three-minute test, screen-reader session, printer test, clean VM without Python and independent A&P/IA review remain unverified.

## Upgrade rehearsal details

The old executable created schema 1. Old source services added a fictional PA-28-161, finalized entry with recorded evidence, component and expense. Six records and one managed attachment were compared before/after: IDs, kind, aircraft/component/entry/amendment links, state, serialized data and attachment hashes unchanged. A full backup/restore rehearsal repeated the comparison. Uninstall left the disposable DB hash unchanged. Fixtures stay under build/upgrade-UUID; no real-user maintenance data was touched.


## Clean source archive verification
The source ZIP was inspected for .venv/build/dist/.git/cache/database/binary-archive members and generated fixture directories; none were included. Extracted source was tested with the existing pinned test interpreter, from the extracted project directory: `python -m pytest -q --junitxml=<workspace>/docs/source-archive-tests.xml`, exit 0, 84 passed. This checks source completeness, not a separate clean Python installation. docs/source-archive-audit.json records the final archive inventory.
