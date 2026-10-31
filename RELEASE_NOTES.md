# 1.1.0-rc1 — stabilization evaluation candidate

Native offline Windows architecture retained. No release has been published.

- Add durable fail-closed recovery journals, retained originals, verified recovery ZIPs, explicit startup recovery, bounded Windows rename retries and process-wide operation locking.
- Add schema 1→2 migration with a pre-migration archive, rollback/recovery, finalized-payload comparison, immutable amendment and delivery relationships, and newer-schema rejection.
- Enforce verified evidence for finalization, signed discrepancy delivery and squawk closure; record content changes invalidate prior delivery acknowledgment. Preserve finalized identity/parts snapshots and show chronological amendments.
- Separate reviewed inspection outcomes, historical transcriptions and discrepancy-list printing. Historical/history PDFs omit new signature lines. Compact PDF pages have configurable true width and content-sized height; Letter documents have continuation identity and restrained administrative metadata.
- Add oil-change description prompts, explicit component installation state, ELT battery controls, documented applicability/time bases/exceptions, selected-aircraft handover, Decimal expense totals, timeline/paging/persistent filters and print/display preferences.
- Fix Windows PDF preview file locking by loading generated PDFs into an owned memory buffer; verify 125/150/200% widget layouts.
- Update test dependencies pypdf 6.3.0→6.21.4 and pytest 8.4.2→9.0.3 after advisory audit. Runtime dependency versions remain pinned.

Existing 1.0.0 artifacts are retained. Schema 2 is not backward-compatible with the old executable: recover a separate schema 1 copy from the retained pre-migration archive for rollback. No automated purge of archives or retained recovery files occurs.

This is an unsigned evaluation candidate. Independent aviation review, physical-printer output, real power-loss testing, clean-Windows-without-Python acceptance, code signing/SmartScreen reputation and independent novice/screen-reader testing are unverified.
