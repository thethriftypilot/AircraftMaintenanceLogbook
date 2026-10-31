# Known limitations — first-pass evaluation build

The application is functional and packaged, but the entire master specification is **not complete** and production release readiness is not claimed. These are actual remaining gaps:

1. No independently validated FAA electronic-signature/recordkeeping compliance, certificate verification or legal eligibility engine. Inspection statements are user-authored and checked for presence, not semantic correctness. No FAA approval claim.
2. Schema initialization/version rejection exists; migration from a prior public schema and restore power-loss recovery need a separately tested implementation/recovery exercise. Multi-file restore is staged and rollback-aware but not one atomic filesystem transaction.
3. Preferences currently cover theme, selected aircraft/window size, backup folder and daily backup toggle. Date format, units, currency defaults, printer/template defaults, persisted sorts/search filters and advanced export settings are deferred.
4. Reports list complete records by type/date. Expense totals/grouping, dedicated inspection-only/component-filter reports and configurable report layout are limited. Complete handover is an all-aircraft archive, not a selected-aircraft archive.
5. Reminder basics support date/hour/cycle intervals and calendar-month rules. Dedicated ELT battery cumulative-use/life controls, automatic qualifying-event baseline population and specialized operational exception handling are deferred. Users can enter manually determined dates/hour thresholds and notes.
6. Preventive references are a selected guidance menu, not the full Appendix A(c) catalog or an eligibility determination. No automatic certification wording or maintenance procedures are invented.
7. Aircraft photographs, spelling assistance, dedicated timeline, saved advanced filters, OCR, live FAA AD lookup and external FlightCost integration are omitted.
8. Component transfers and history persist, but removed components remain associated with their last aircraft unless transferred. Component events are append-only through services; correction requires another event. A polished installation-status workflow is deferred.
9. Signed evidence is retained and originals have linked amendments, but an explicit Superseded display state and amendment-chain browser are deferred. Attachments do not capture signatures or authenticate signers.
10. List filtering loads one aircraft's records into memory. A 5,000-record synthetic timing passed on this host; larger datasets and maximum archive size (4 GB) still need sizing tests. Preview generation for individual unusually long entries is synchronous; report generation, import and backup use workers.
11. JSON export is documented but has no direct importer; full fidelity reimport uses verified ZIP restore. CSV import has no deduplication. CSV exports neutralize formula-like text with a leading apostrophe.
12. Embedded Bitstream Vera covers common Latin/Greek/Cyrillic characters, not all world scripts or emoji. Review output when using unsupported characters. Physical printer, non-Letter printer configurations, Windows 10 and full accessibility validation remain outstanding.
13. Installer is unsigned. No public GitHub repository/release or remote CI run was created. License/source distribution obligations must be reviewed before public publication. This local evaluation is not a legal license audit.

Recommended next work: independent aviation review and A–E acceptance on a clean VM; crash-safe restore journal and versioned migration tests; expense aggregation and selected-aircraft handover; specialized ELT reminders; accessibility/performance refinement and publisher code signing.
