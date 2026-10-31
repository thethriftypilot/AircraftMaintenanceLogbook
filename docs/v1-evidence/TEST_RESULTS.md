# Verified results — October 30, 2026

Environment: Windows 11 build 26100, x64; CPython 3.13.7; PySide6 6.10.1; PyInstaller 6.17.0; Inno Setup 6.7.3. Dates here use America/New_York; database timestamps and some generated documents use UTC and may show October 31.

| Check | Actual result | Evidence |
| --- | --- | --- |
| Automated suite, final build | **41 passed in 4.53 seconds**, exit 0 | `docs/test-results.xml`, beginning of `docs/build-log.txt` |
| Core rules/storage | Passed aircraft/revisions/decimal/inspection/pilot/amendment/links/calendar/audit/rollback tests | `tests/test_core.py` |
| Files/portability | Passed managed evidence, corruption/traversal, verified restore, CSV/JSON and long full/compact PDFs | `tests/test_files.py` |
| GUI tests | Passed native-widget setup/navigation, autosave, locked reopen, forms and QPdfDocument preview in offscreen mode | `tests/test_gui.py` |
| Frozen identification | Later registration edit does not rewrite finalized document identity | `tests/test_snapshots.py` |
| Packaged executable | Database integrity true; PDF 22,474 bytes; verified backup 3,101 bytes | `build/packaged-smoke/result.json` |
| Windows installer build | Inno compile succeeded; final EXE 41,195,487 bytes | End of `docs/build-log.txt`; `dist/release/` |
| Portable package | ZIP generated; 57,926,015 bytes | `dist/release/` and SHA256SUMS |
| Installation | Silent per-user install to isolated workspace test folder succeeded | `docs/install-test.log`, `docs/installer-smoke.json` |
| Installed executable | Integrity true, PDF and backup generated/verified | `docs/installer-smoke.json` |
| Reinstall/restart | Reinstall did not alter external test database hash; installed executable successfully reran | `docs/installer-smoke.json` |
| Uninstall | Uninstaller ran successfully; external test database preserved | `docs/installer-smoke.json` |
| Native visual review | Actual dark/light dashboards, 1000×700 layout, entry editor, wizard, 150% scaling and installed UI inspected | `docs/screenshots/` |
| PDF visual review | Full and compact sample pages plus all seven long-sample pages rendered with Poppler and inspected | `docs/screenshots/sample-*.png`, `pdf-contact.png` |
| Bounded performance | 5,000 synthetic entries: initial window/list 0.618 s, filtered search 0.102 s, one expected match | `docs/performance-smoke.json` |

Defects found and corrected during execution: unclosed SQLite archive connections on Windows; a trailing blank PDF page; deferred toolbar widgets briefly overlaying the dashboard; light-theme link contrast; and a packaged Qt import failure caused by an unrelated Poppler ICU DLL on the environment PATH. Build tooling now isolates DLL search inputs. Final test/build passes occurred after those fixes.

A workstation GUI test run emitted a COM/accessibility exception while still passing and exiting zero. The final automated run uses offscreen Qt and completes without that diagnostic. Actual native rendering is evidenced separately; this does not substitute for screen-reader acceptance.

**Not performed / not claimed:** clean Windows VM without any Python installed, physical printer output, Windows 10, 125/200% display-scale matrix, full keyboard/screen-reader review, actual power loss/full disk, version migration from an older public release, 10,000+ record benchmark, independently reviewed aviation scenarios A–E, code signing, remote GitHub Actions or public release. Same-version reinstall preservation is not proof of a future schema migration.

The installer is unsigned. Passing these checks does not make every requirement complete or establish regulatory/legal approval. See COMPLETION_MATRIX.md and KNOWN_LIMITATIONS.md.
