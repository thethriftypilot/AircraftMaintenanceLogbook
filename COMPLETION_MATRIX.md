# Follow-up completion matrix — 1.1.0-rc1

| Area | Implemented and evidence | Remaining boundary |
|---|---|---|
| Established-directory safety | Marker, journal/.new detection; mode=rw connections; no empty replacement; test_recovery.py | Cannot infer erased history if every marker, archive and attachment is manually destroyed |
| Restore | Verified stage/recovery archive, durable phases, retained DB/WAL/SHM/attachments, recovery UI; 12 boundary cases | Real power loss/device faults untested |
| Migration | Additive schema 1→2, preserved record payloads, verified v1 archive, five fault boundaries, downgrade rejection | Old app must use restored v1 copy |
| Service integrity | Link checks, optimistic revisions, outer OS operation lock, attachment hashes/idempotency, closure evidence | Privileged filesystem access is outside trust boundary |
| Finalized records | SQL immutability, identity/parts snapshots, additive amendment table and chain view | No cryptographic signature |
| Backups/handover | Verified destination/time/hash, same-drive warning, restore preview, retained history, selected export test | No automatic purge; exports are not backups |
| Regulatory safeguards | Official-source recheck; reviewed outcome text, authority checks, Appendix A guidance | Qualified independent acceptance unverified |
| Discrepancy workflow | Dedicated PDF, signed evidence delivery ledger and content fingerprint; tested cross-record/tampered evidence | Actual signature, delivery and legal basis are user assertions |
| Historical records | Source/uncertainty label, no new signature block; tested | Original scan completeness is user responsibility |
| Time/ELT | Separate clocks; documented applicability/baseline; battery thresholds and 100-hour excess | No blanket applicability or extension permission |
| Printing | Actual compact size, Letter/continuations, historical/history/discrepancy output, memory-backed preview | Physical printer remains release gate |
| Editor/dashboard | Contextual inspection tab/actions, actual-work oil prompts, prominent aircraft/new-entry, backup status | Independent novice/screen-reader study outstanding |
| Components/expenses | Installation state/events/transfers; parts snapshots; separate-currency Decimal summaries | No billing engine or currency conversion |
| Navigation/preferences | Timeline, SQL paging, saved filters/global ordering, date/currency/printer/font/width preferences | ASCII search folding; page-local column sorting |
| Packaging | Versioned Windows artifacts, tests-before-build, preserved v1 artifacts, source exclusions, checksums | Unsigned; clean VM not available |
| Upgrade/recovery rehearsal | scripts/upgrade_smoke.ps1 and upgrade_fixture.py; exact payload/file comparisons and restore rehearsal | See generated evidence JSON for actual run outcome |
| CI/security/licensing | Pinned lock, Windows CI, license inventory, advisory scan; automatic publishing removed | Native dependency/legal licensing audit remains independent work |

Historical 1.0.0 matrix and test conclusions are preserved under docs/v1-evidence. This matrix supersedes first-pass completion claims. Detailed limitations are in KNOWN_LIMITATIONS.md.
