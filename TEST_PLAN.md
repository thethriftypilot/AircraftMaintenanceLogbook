# Acceptance and regression plan

Automated tests in `tests/` exercise aircraft persistence/duplicates/revisions; independent decimal times; draft edits/finalization/amendments; historical uncertainty; performer/approver separation; annual IA/nonapproval/pilot guards; cross-aircraft relationships; component transfers; month-end/leap/earlier-of/hour/cycle/unknown reminders; audit protection; attachment type/hash/retention; backup restore/corruption/traversal; CSV transactionality/Unicode; PDF continuation/signature blocks; GUI setup/navigation/autosave/read-only reopen/PDF viewer.

Run `python -m pytest -q --junitxml=docs/test-results.xml`. The packaged `--smoke-test` creates an isolated fictional database, generates an embedded-font PDF, creates/verifies a backup and writes result JSON. It does not simulate a physical signature or print job.

Manual acceptance scenarios from the original specification:
- A: install in clean Windows without Python, create aircraft, enter actual oil-change details, preview/print, record signed copy, restart and inspect history.
- B: mechanic workflow with distinct performer/approver, multiple actions/parts/references, signature status and locked reopen.
- C: annual inspection approved and nonapproved cases; independently review exact statement, IA/alternate authorization, signed discrepancy list and unchanged open items.
- D: discrepancy to corrective entry/evidence to documented closure; deferred status never implies authorization.
- E: backup multiple records/scans, add later records, restore confirmed earlier backup and verify retained current-state recovery.

Release gates still requiring independent/manual validation: physical printer margins and scale, non-Python clean VM, Windows 10, screen reader and keyboard-only full workflow, 125/150/200% DPI, 10,000+ record latency, disk-full and power-loss during restore, production migration across a released version, independent aviation statement review and timed first-user three-minute task. Never mark these passed from code inspection alone.


## RC acceptance mapping
Scenarios A/B: test_core.py, test_files.py and test_snapshots.py cover pilot/mechanic drafts, authority guards, identity snapshots, externally recorded evidence, restart, immutable original and amendment. C: test_rc_workflows.py covers outcome contradictions, signed-list delivery and changed findings; generated approved/nonapproved/discrepancy fixtures are in docs/rc-evidence. D: closure rechecks on-disk signed evidence; schedules/ELT and separate-currency totals are tested. E: test_recovery.py covers all named journal boundaries, schema evolution, forced termination and fail-closed recovery. F: long-PDF and historical/compact tests plus actual rendered fixtures and scaled Qt previews; physical printing remains outstanding. G: scripts/upgrade_smoke.ps1 installs both actual versions and compares preserved records/evidence, then tests restore/restart/uninstall; extracted portable/source checks are documented in TEST_RESULTS.md. No independent acceptance is inferred from these developer-run checks.
