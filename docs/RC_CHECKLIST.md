# Stabilization checklist — 1.1.0-rc1

1. Preserve 1.0.0 artifacts and baseline evidence; rerun existing tests. **41 passed, exit 0.**
2. P0: durable restore journal; fail-closed startup; explicit recovery; bounded lock retries; WAL/SHM isolation; per-directory operation locking; fault injection.
3. P0: schema 1→2, verified pre-migration archive, preserved final content, recovery and downgrade tests.
4. P0: storage/service integrity, amendment chains, signed discrepancy-list evidence and delivery ledger.
5. P0: official-source recheck, reviewed inspection statements, separate historical output, ELT and documented schedule exceptions.
6. P0: compact/full/inspection/discrepancy/history PDFs with continuation identity; render actual fixtures.
7. P1: contextual editor/oil-change prompts, component installation state, money summaries, timeline/paging/preferences and selected-aircraft handover.
8. Release: tests, real 1.0.0→1.1.0 upgrade on disposable populated records, packaged/installed checks, source archive audit, dependency inventory/security check, hashes and accurate gates.

No remote publishing. No real user-data deletion. Physical power-loss, physical printing, independent aviation review, signing and clean-VM acceptance are separate gates, never inferred from automated tests.

Final local outcome: implemented core P0/P1 changes and built versioned RC artifacts; 84 tests, installed upgrade/recovery/uninstall and extracted portable smoke pass. Remaining gates and scoped P1 limits are documented in KNOWN_LIMITATIONS.md and TEST_RESULTS.md.
