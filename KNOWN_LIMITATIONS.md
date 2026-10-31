# Known limitations and release assessment — 1.1.0-rc1

## Must complete before public operational release
- Independent A&P/IA and applicable legal review of record wording, authority boundaries, inspection/discrepancy workflow and retention/transfer obligations. No FAA approval or legal compliance certification is claimed.
- Physical-printer acceptance: actual paper dimensions, printer nonprintable margins, 100% scale, multi-page signatures and long entries. Preview/rendering is not printer output.
- Clean Windows VM acceptance without Python/development tools, including install, migration, restart and uninstall. This workstation has Python and build tools.
- Distribution trust decision and code signing. Installer is unsigned and SmartScreen reputation is not established. Do not instruct users to bypass organization security policies.
- Real hardware sudden-power-loss/storage-failure testing and independent recovery review. Exception injection, forced process termination, flushes and Windows retry behavior are covered; device/filesystem write durability cannot be guaranteed.

## Should improve before broad adoption
- Independent novice walkthrough and screen-reader testing. Developer-driven Qt rehearsal has 16 recorded actions, file dialogs bypassed, zero final errors; it is not evidence of three-minute human onboarding.
- Responsive toolbars and large reports: record lists paginate, but dashboard aggregation, amendment-family lookup, full exports and reports still load collections in memory. Unicode search is exact-case outside SQLite's ASCII case folding. Column-header sorting is page-local; the order selector is global.
- Text checks detect selected contradictory inspection wording only. Human review is required; role/certificate fields and signed-scan claims are not authenticated. A supplied document can have a valid hash and still be substantively wrong.
- Improve component-history navigation after transfer and richer category/aircraft labels in expense summaries (some groups display stable IDs). Current events and relationships are preserved.
- Extend fonts beyond bundled Vera Latin/Greek/Cyrillic coverage. Tested accented Latin and punctuation; arbitrary world scripts/emoji are not guaranteed.
- Secure local Windows account/disk permissions separately. Database is not encrypted, audit hashes are not digital signatures, and a privileged filesystem user can tamper with local files. No network service or telemetry is added.
- Backups and recovery copies consume space indefinitely. History listing does not reverify files automatically. Same drive warning compares Windows drive identifiers, not physical-device topology.

## Deferred capabilities and explicit boundaries
- FAA/AD live ingestion, electronic signatures/certificate validation, official Form 337/8130-3 generation, cloud sync, accounts, subscriptions and telemetry.
- FlightCost direct integration: CSV/JSON manual-mapping boundary only; no undocumented schema or foreign database writes.
- Labor invoicing/tax/currency conversion and generalized unit conversions. Hours/rates and exact expense totals exist; recorded amounts are not automatic billed totals. Date editing/storage stays ISO; list display may use US dates.
- Universal automatic schedule applicability, interval resetting, inspection-program approval, extension authorization and airworthiness determination. User-confirmed sources/baselines/decisions are required.
- Selected-aircraft export cannot be restored as a complete database. Full structured JSON remains the legacy version-1 interchange projection (records/attachment metadata/audit), not schema-2 backup restoration; full verified ZIP backup is authoritative for recovery.
- Build scripts are reproducible procedures with pinned packages, not bit-for-bit reproducible binaries. Downloaded wheels, compiler/platform and timestamps matter. Python advisory audit does not cover every native Qt/OpenSSL/OS vulnerability or establish licensing approval.
