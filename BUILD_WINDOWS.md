# Reproducible Windows build procedure

Locally exercised toolchain: CPython **3.13.7 x64**, PyInstaller 6.17.0, PySide6 6.10.1, ReportLab 4.4.5, Inno Setup 6.7.3 on Windows 11 build 26100. Dependencies, including transitive build/test dependencies, are pinned in `requirements-lock.txt`. This is a repeatable build procedure, not a claim of bit-identical output; generated timestamps and package tooling can change binary bytes.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
winget install --id JRSoftware.InnoSetup --exact --scope user
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build.ps1
```

The script tests, generates the icon and license inventory, packages the executable, runs a packaged smoke scenario, compiles Inno Setup and creates the portable ZIP with SHA-256 listings. Pass `-Iscc 'C:\path\ISCC.exe'` if needed. Artifacts are under `dist/release/`; intermediate executable under `dist/AircraftMaintenanceLogbook/`.

Useful development checks:
```powershell
.\.venv\Scripts\python.exe -m pytest -q --junitxml=docs\test-results.xml
.\.venv\Scripts\python.exe scripts\visual_evidence.py
.\.venv\Scripts\python.exe -m logbook --smoke-test build\source-smoke
```

The Windows workflow builds pull requests, main commits and version tags. No automatic publication job is present. Publishing requires separate explicit authorization. No remote workflow execution is claimed merely because this file exists. Maintain actions/toolchain pins and review dependencies before public distribution.

Qt/PySide6 are dynamically bundled in the one-folder layout under LGPLv3-compatible distribution terms. Keep license texts, notices, source acquisition information and the ability to replace compatible library files. Do not prohibit reverse engineering for debugging modifications to LGPL libraries. This original MIT code does not relicense Qt. Review third-party terms and publish corresponding library source availability with a public release. No static Qt linking or DRM is used.


RC verification after build:
```powershell
./scripts/upgrade_smoke.ps1
.\.venv\Scripts\python.exe scripts/source_archive.py
```
The upgrade rehearsal requires the retained 1.0.0 installer/source ZIP and creates only disposable build/upgrade-UUID data. Exact evidence is emitted to docs/upgrade-*-evidence.json. Source packaging excludes environments, build products, archives, database files and generated fixture/screenshot directories. Evidence remains separately available in the workspace.

The pinned-package advisory scan used pip-audit 2.10.1 (audit-only tool, not a runtime dependency): `python -m pip_audit -r requirements-lock.txt --no-deps --disable-pip --format json --output docs/dependency-audit.json`. Licenses are inventoried for pinned packages only; the audit tool's own environment is not bundled as an application feature. Check native Qt and OS security separately.
