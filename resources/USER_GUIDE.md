# The Thrifty Pilot — Aircraft Maintenance Logbook

## Quick start
1. Choose **+ Aircraft**. Enter registration (or an unmistakable DEMO label), make, model and serial number. Operating-time fields are optional when unknown. Save and close.
2. Choose **+ New Maintenance Entry**. Select the category and enter the actual completion date, work and performer. Never fill gaps with assumptions.
3. Open **Approval** if an authorized person will approve or disapprove the work. Enter their actual identity, certificate information and authorization basis. The performer may be different.
4. For inspections, complete **Inspection**: extent, total time, program if applicable, and the statement appropriate to the actual outcome. For nonapproval, record discrepancies and confirm delivery of a signed, dated list to the owner/operator.
5. Drafts autosave after a short pause; **Save Draft** saves immediately. **Finalize for printing** validates and locks the content. Finalization does not sign anything.
6. **PDF / Print preview** shows actual PDF pages. Save the PDF or choose an operating-system printer. Use a physical signature. Only confirm printing if a physical copy was actually printed.
7. Reopen the finalized entry and choose **Record signed copy**. Select a scan, identify who is recording it and confirm it belongs to the exact entry. The scan is copied into managed storage and hashed.
8. Use **Settings & Backups → Back up now**. Keep a verified copy on another drive.

Setup is optional. The demonstration workspace is separate from real data and all demo facts are fictional. Use `--demo` when launching from source to reopen it.

## Aircraft and components
Use Aircraft to edit profiles or archive them without deleting history. Airframe time, tach and Hobbs are independent decimal quantities. Record source and last-update date; unknown values should remain blank. No automatic meter conversion occurs.

Components supports multiple engines, propellers and other installed equipment. Record manufacturer, model, serial, installation/removal dates, overhaul details and independent hours. Add Component History events to document removals, installations and corrections. **Transfer component** appends removal and installation events and changes the current aircraft while preserving prior entry links. Do not overwrite a component's serial number to represent a different physical component: create a new component.

## Pilot workflow
Select Preventive maintenance and use **Preventive task guidance** for reference categories. Verify the actual Appendix A(c) item, aircraft configuration, complexity, pilot privileges and operating restrictions. Ownership alone does not grant maintenance or approval authority. Under the pilot approval workflow, performer and approving pilot must match. The ordinary pilot provisions exclude aircraft used under Parts 121, 129 or 135; light-sport privileges and exceptions require their own applicability review. No maintenance procedures are supplied.

## Mechanic and inspection workflow
Saved identities are under Settings & Backups. Identity data is user supplied and is copied into an entry when selected; credentials are never verified. A basic mechanic role cannot finalize an annual/progressive inspection as though it held IA. Confirm current IA privileges or document a recognized alternate authorization. Rating, currency, scope, tools, technical data and legal applicability remain the user's responsibility.

Enter a certification statement appropriate to the actual outcome under [14 CFR 43.11](https://www.ecfr.gov/current/title-14/section-43.11). The application deliberately does not invent or automatically assert an airworthy finding. Progressive/program inspections need the applicable program, scope, routine/detailed portions and required statement. A signed discrepancy list must be prepared, delivered and retained where required; attach its scan to the entry. Finalizing an inspection never closes open maintenance items automatically.

## Signatures and corrections
States are Draft, Historical import requiring verification, Ready to print, Printed / awaiting physical signature and Signed copy recorded. A historical record remains explicitly historical by category and source even after finalization. A generated PDF is always an unsigned generated copy. The signed scan is the supporting external document; a typed name, uploaded image, audit entry or file hash is not a new electronic signature.

Finalized work content is locked. **Create amendment** makes a linked draft with a correction reason, preserving the original and both timestamps. The amendment must be reviewed, finalized and signed separately as appropriate. Original records are retained; their amendment relationships appear on generated documents and in structured exports.

## Maintenance items and reminders
Use Maintenance Items for discrepancies, planned work, parts waits and corrective actions. Deferred is a tracking choice, not an MEL or regulatory deferral. Closing requires completion notes and a linked entry with a recorded signed copy; even this does not determine legal authority to fly.

Schedules and ADs use explicit applicability, baseline dates/hours/cycles, intervals and optional absolute due thresholds. For calendar months, choose the end-of-calendar-month option. For an applicable annual reminder, a last inspection in September 2026 with 12 calendar months produces September 30, 2027. Applicability and inspection-program exceptions must be checked independently. No automatic 100-hour extension is added.

Select the exact hour source. A linked component uses its own values; otherwise the aircraft's values are used. Missing current time or baseline yields Unknown unless another known limit is already due or past its threshold. Earlier-of-date/hour/cycle limits are evaluated. Upcoming does not mean every legal requirement is satisfied. Reset baselines only when an explicitly linked qualifying event justifies doing so. AD intervals and methods must be entered from the applicable directive; the app does not search for ADs or determine completeness. Service bulletins have a separate list and require a stated basis before treating them as mandatory.

## Parts, costs, search and reports
Parts and expenses are optional. Link them to the appropriate entry/component. Multiple parts are separate rows; include the actual parts in the entry's work/parts text before finalization so the printed record is complete. A purchased part or uploaded 8130-3 does not establish installation eligibility.

Search filters each list across its recorded fields. Double-click to reopen. CSV export uses the visible rows and protects formula-like values for spreadsheet use. Reports provide chronological PDFs by record type with optional date bounds. JSON exports contain all aircraft, records, links, attachment metadata and audit events. Full ZIP archives include the database and actual attachments for reimport through Restore. These complete archives contain **all aircraft**; review sharing scope.

## Historical import
CSV needs unique headers and UTF-8 text. Map each relevant column, inspect the first ten preview rows and import. All rows are validated before a transactional insert. Dates use YYYY-MM-DD; blank dates/time preserve uncertainty. Imported entries are historical and unverified, never new approvals. Record the source page/document and attach scans. No OCR or automated signature recognition is performed. Repeatedly importing the same file creates additional records; review before importing again.

## Backups and recovery
Manual backups and automatic daily backups while the app is running use SQLite's backup API and include all managed attachments. Preferences chooses the folder and enables/disables automatic backups. A backup on the same disk is not protection from disk loss.

Verify backup checks manifest hashes, attachment hashes, database integrity, foreign keys and schema version. Restore previews counts/version and requires explicit replacement confirmation. It stages and verifies files, creates a recovery ZIP of current data, then replaces the database and attachments. Recovery files are retained. Do not kill the application or remove the drive during restore. If interrupted, preserve the entire data directory and its `pre-restore-*.zip` archives before attempting recovery. A machine power-loss test of the replacement sequence remains outstanding.

## Privacy and troubleshooting
Core functionality is offline with no accounts, telemetry or cloud uploads. Website/help links open only when selected. Use OS access controls and disk encryption as appropriate; the database itself is not encrypted. Do not share archives containing private certificate or contact information unintentionally.

An error dialog means the operation did not complete. Check required fields, date format, free disk space and folder permissions. A conflicting revision means another window changed the record: reopen it. A hash mismatch means a supporting copy changed or disappeared; restore verified evidence. Only one process may open a data directory at a time. The application data directory is displayed in Settings.

## Regulatory limitations and references
This application is not FAA approved or certified. Users remain responsible for current applicability, qualifications, actual work, record accuracy, required forms and return-to-service decisions. Local audit events and hashes provide limited tamper evidence, not independent trust or a compliant electronic-signature system.

Reference review: October 30, 2026. Review current controlling text before relying on a workflow:

- [14 CFR 43.3](https://www.ecfr.gov/current/title-14/section-43.3), [43.7](https://www.ecfr.gov/current/title-14/section-43.7), [43.9](https://www.ecfr.gov/current/title-14/section-43.9), [43.11](https://www.ecfr.gov/current/title-14/section-43.11)
- [14 CFR Part 43 Appendices A and B](https://www.ecfr.gov/current/title-14/chapter-I/subchapter-C/part-43)
- [14 CFR 91.207](https://www.ecfr.gov/current/title-14/section-91.207), [91.409](https://www.ecfr.gov/current/title-14/section-91.409), [91.411](https://www.ecfr.gov/current/title-14/section-91.411), [91.413](https://www.ecfr.gov/current/title-14/section-91.413), [91.417](https://www.ecfr.gov/current/title-14/section-91.417)
- [14 CFR 65.95](https://www.ecfr.gov/current/title-14/section-65.95)
- [FAA AC 43-9D](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43-9D.pdf), [AC 43-12A](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43-12A.pdf), [AC 120-78B](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_120-78B_FAA_Web.pdf)

Current regulations take precedence over older circular language. No official FAA forms are generated. Attach actual Form 337, 8130-3 and other supporting documents when required and available.


## Version 1.1.0-rc1: recovery and migration
Opening a version 1 database creates and verifies a pre-migration ZIP before schema 2 is installed. Original record payloads remain unchanged. Keep that archive: version 1 cannot open schema 2. To revert, recover a copy from the version 1 archive; never point an older app at the upgraded database.

An interrupted restore or migration blocks ordinary startup. The recovery dialog offers the verified pre-operation archive, a separately selected backup, or Cancel. Cancel leaves recovery pending. Do not remove recovery-journal.json, its .new companion, or retained files to bypass this protection. Recovery preserves old files and archives; no automatic cleanup is performed. Keep adequate free disk space for a full archive, staging copy and retained original. Windows flushes and rename retries are implemented; actual sudden power loss has not been tested.

## Reviewed inspections and discrepancy delivery
Choose the actual outcome and inspection fields, then explicitly request Prepare inspection statement. Review and edit the wording against the actual inspection and controlling requirements, enter the reviewer, and affirm review. Editing outcome, statement, scope or program clears that affirmation. Text checks catch obvious contradictions; they cannot establish regulatory sufficiency or actual authority.

For nonapproval, create the Discrepancy list PDF, physically sign/date it, give it to the owner/operator, and use Record list delivery to retain the signed scan, recipient, date and recorder. Changes to findings/identity after recorded delivery require renewed acknowledgment of the corrected signed list before finalization. The app verifies hashes and associations, not the authenticity or substantive contents of a signature. Closed/deferred squawks do not authorize flight.

Historical transcriptions have no new signature block. Attach the original signed source. Maintenance history PDFs preserve recorded statements and credentials without presenting new approval signature spaces.

## Print and display preferences
Settings → Preferences stores dark/light appearance, compact/full-page default, compact width (4–8.5 inches), font size, preferred printer, backup location, date display and default expense currency. Stored dates and editing stay ISO YYYY-MM-DD. Time units remain explicit hours and cycles; no conversion between tach, Hobbs and TIS occurs. Compact PDFs use their actual paper width, not a narrow column on Letter. Print at 100% for paste-in dimensions; choose paper/orientation in preview. Fit to paper is an explicit alternative. Validate margins and scale on the intended physical printer before operational use.

## Finding, summarizing and handing over records
Timeline searches all selected-aircraft record types. Lists show 100 records per page; filters and global Newest/Oldest/Work date order persist per list. Clicking column headers sorts the current page only. CSV exports the displayed page. Search uses SQLite case folding (ASCII case-insensitive; Unicode text remains searchable with exact case).

Reports → Expense totals groups recorded amounts by year/category/aircraft/component, across aircraft. Currency codes remain separate, with exact decimal arithmetic and no conversion; amounts are recorded costs, not automatically calculated invoices. Labor hours and rate are recorded separately. Reports → Selected aircraft handover creates records.json, chronological maintenance-history.pdf, associated evidence and an integrity manifest. Related transferred-component audit may identify past aircraft. This ZIP is explicitly non-restorable; use full verified backups for recovery. Full JSON and full backups contain all aircraft.

Component installation state is explicit (Installed, Removed or Unknown). Removal events preserve the component's historical aircraft association; transfer appends both removal and installation events. Follow Component History to see past events. An amendment chain shows each original and correction without overwriting content.

ELT and regulatory schedules require a documented applicability decision, controlling source and baseline. ELT battery thresholds track cumulative use greater than one hour and 50% useful-life expiry, with manufacturer replacement dates and a documented storage-life exception. 100-hour excess reduces the next interval; it does not authorize use of the extension. Exceptions remain user-reviewed. Unknown facts must remain Unknown.

Backup history lists retained ZIPs but does not imply they were just verified. Verify before use; the dashboard identifies the last successfully verified backup and warns about same-drive storage. Recovery archives are never automatically purged. FlightCost integration is limited to documented CSV/JSON exports for manual mapping; no undocumented import schema or other app database is used.
