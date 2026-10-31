# CODEX MASTER BUILD PROMPT
# The Thrifty Pilot | Aircraft Maintenance Logbook
## Complete Windows Desktop Application, Version 1.0

### 1. YOUR ROLE AND MISSION

You are the lead software architect, senior Windows desktop engineer, Python developer, database engineer, product designer, aviation maintenance recordkeeping specialist, security reviewer, accessibility specialist, QA engineer, and release engineer.

Your assignment is to design, develop, test, package, and document a complete, production-quality Windows desktop application called:

**The Thrifty Pilot | Aircraft Maintenance Logbook**

This is a new software project intended for publication through The Thrifty Pilot aviation software collection and eventual public distribution through GitHub.

The software must enable general aviation aircraft owners, pilots, certificated aircraft mechanics, and appropriately authorized maintenance personnel to:

- Create and maintain aircraft maintenance records.
- Prepare professional maintenance logbook entries.
- Record preventive maintenance performed by authorized pilots.
- Document maintenance performed by certificated mechanics.
- Record inspections and associated findings.
- Track aircraft discrepancies and outstanding maintenance items.
- Monitor inspection dates, aircraft operating time, and recurring maintenance.
- Maintain aircraft, engine, propeller, and component histories.
- Track Airworthiness Directive compliance status.
- Record maintenance expenses and replacement parts.
- Generate professional PDF maintenance records.
- Print correctly formatted entries for traditional paper logbooks.
- Preserve supporting maintenance documentation.
- Back up, restore, and export maintenance records.
- Maintain a traceable history of changes to finalized records.

**The primary product goal is simplicity without sacrificing record quality or integrity.**

A first-time user should be able to create an aircraft profile and prepare a printable maintenance entry within approximately three minutes, assuming the user already has the maintenance information.

Do not build a mockup, incomplete prototype, demonstration-only interface, or a website pretending to be a desktop application.

Build the actual product.

### 2. DEVELOPMENT AUTONOMY AND EXECUTION RULES

You have authorization to make ordinary software architecture, design, and implementation decisions needed to complete this application.

Do not repeatedly request confirmation for decisions that can be resolved through sound engineering judgment.

Before implementation:

1. Inspect the existing repository and relevant files.
2. Preserve existing useful code if this repository already contains an implementation.
3. Establish the product architecture and data model.
4. Identify regulatory and safety-critical functionality.
5. Create an implementation checklist with objectively verifiable acceptance criteria.
6. Begin implementation.

Continue through implementation, automated testing, bug fixing, packaging, and documentation.

Do not stop after creating a project skeleton.

Do not replace essential features with TODO comments, empty buttons, fake data, placeholder screens, or nonfunctional menu items.

Every visible control must perform its stated function or be omitted from the release.

When facing implementation constraints, investigate reasonable alternatives and continue with the best supported solution.

If the environment cannot compile or execute Windows applications, complete the source, tests, Windows build scripts, installer configuration, and Windows GitHub Actions workflow. Clearly state that Windows validation remains unverified until the Windows workflow succeeds.

Never claim to have run a test or built an installer that was not actually executed.

Produce an accurate final implementation report listing completed, verified, blocked, and deferred work.

### 3. PRODUCT IDENTITY AND DESIGN

Application name: The Thrifty Pilot | Aircraft Maintenance Logbook

Version: 1.0.0

Publisher: The Thrifty Pilot

Primary platform: Windows 11, with Windows 10 compatibility wherever supported by the pinned dependencies.

Target architecture: Windows x64.

Website: https://www.thethriftypilot.com/

Repository name: `thrifty-pilot-aircraft-maintenance`

Brand positioning:

Practical, reliable aviation tools for aircraft owners and pilots who want to maintain good records, understand ownership responsibilities, and manage maintenance without unnecessary costs.

Design a modern aviation-themed interface.

Visual requirements:

- Professional general aviation aesthetic.
- Dark navy, charcoal, muted blue, and restrained aviation accent colors.
- Optional light theme.
- Excellent text readability.
- Clear visual hierarchy.
- High-quality typography.
- Distinctive application icon.
- Attractive dashboard.
- Consistent spacing and controls.
- Clear forms and data tables.
- Practical rather than flashy animations.
- No unnecessary visual clutter.

The application should feel appropriate for an individual aircraft owner, an independent A&P mechanic, or a small maintenance shop.

Do not make the interface look like generic accounting software or a spreadsheet with buttons.

Avoid excessive dashboards that interfere with entering maintenance records.

Support high-DPI monitors, Windows display scaling, keyboard navigation, accessible labels, and usable layouts on smaller laptop screens.

Include a consistent, nonintrusive way to access The Thrifty Pilot website.

### 4. REQUIRED TECHNICAL ARCHITECTURE

Preferred technology stack:

- Python using a stable, supported version compatible with the chosen dependencies.
- PySide6 with Qt Widgets for the desktop interface.
- SQLite for local persistent storage.
- SQLAlchemy or another well-maintained database access layer.
- Alembic or an equivalent reliable database migration mechanism.
- ReportLab or another suitable PDF generation library.
- PyInstaller for executable packaging.
- Inno Setup for the Windows installer.
- Pytest for automated testing.
- GitHub Actions for build and release verification.

You may change a technology only if a documented technical reason supports the change.

Prioritize reliable offline operation, ease of maintenance, and simple distribution.

Use a maintainable project structure separating:

- User interface
- Domain models
- Database persistence
- Maintenance record services
- Scheduling and due-date logic
- Regulatory validation and reference data
- PDF and printing functionality
- File attachment management
- Backup and restore
- Import and export
- Settings and profiles
- Tests and release tooling

Never embed business logic exclusively inside UI event handlers.

Use consistent types, input validation, structured logging, and centralized error handling.

The installed program must function without requiring Python, Git, a compiler, or command-line knowledge on the user's computer.

### 5. INSTALLATION AND DISTRIBUTION

Produce a complete Windows installation package.

Expected final release artifact:

`TheThriftyPilot-AircraftMaintenanceLogbook-Setup-1.0.0.exe`

Installer requirements:

- Standard Windows installation experience.
- Visible application name and publisher information.
- User-selectable installation folder where practical.
- Start menu shortcut.
- Optional desktop shortcut.
- Programs and Features / Installed Apps uninstall entry.
- Application icon.
- Version metadata.
- Clean uninstall.
- No unnecessary Windows services.
- No automatic startup unless a user explicitly requests it.
- No administrator privileges unless genuinely necessary.
- No bundled advertisements.
- No browser extensions.
- No telemetry.
- No subscription or registration requirement.

Use PyInstaller one-folder packaging internally, with Inno Setup creating the user-facing installer.

Also create a portable ZIP distribution if practical.

Store user data outside the application installation directory.

Default data location:

`%LOCALAPPDATA%\TheThriftyPilot\AircraftMaintenanceLogbook\`

Keep the database, attachments, configuration, and application logs in appropriate subdirectories.

Do not store writable user records inside Program Files or the packaged executable directory.

Uninstallation must not silently delete maintenance records, attachments, backups, or signed documents.

Implement safe installation upgrades that preserve existing data.

Before schema changes, create a recoverable backup.

If code signing credentials are unavailable, generate an unsigned installer, document the limitation, and do not falsely imply that the file has been signed or verified by Microsoft.

Provide reproducible Windows build scripts and a GitHub Actions workflow capable of generating release artifacts.

Pin or constrain dependencies appropriately, generate a third-party license inventory, and comply with applicable Qt/PySide6 and other component licensing obligations.

### 6. AVIATION REGULATORY SCOPE

This application initially targets United States general aviation maintenance records under the applicable provisions of 14 CFR Parts 43 and 91.

The system must be designed around, at minimum:

- 14 CFR § 43.3
- 14 CFR § 43.7
- 14 CFR § 43.9
- 14 CFR § 43.11
- 14 CFR Part 43, Appendix A
- 14 CFR Part 43, Appendix B
- 14 CFR § 91.207
- 14 CFR § 91.409
- 14 CFR § 91.411
- 14 CFR § 91.413
- 14 CFR § 91.417
- 14 CFR § 65.95
- FAA AC 43-9D, Maintenance Records and FAA Form 8130-3 Return to Service
- FAA AC 43-12A, Preventive Maintenance
- FAA AC 120-78B, Electronic Signatures, Electronic Recordkeeping, and Electronic Manuals

Authoritative sources:

https://www.ecfr.gov/current/title-14

https://www.faa.gov/regulations_policies/advisory_circulars

Verify the current regulations and guidance rather than relying solely on remembered text.

Keep a documented regulatory reference matrix identifying:

1. The requirement.
2. Its controlling reference.
3. The relevant application features.
4. How the implementation supports the requirement.
5. What the software cannot independently verify.
6. Any assumptions or limitations.

The product must not falsely claim FAA certification, FAA approval, automatic legal compliance, or authority to approve an aircraft for return to service.

This is a recordkeeping and workflow application, not a replacement for qualified maintenance judgment or regulatory responsibility.

Regulatory references must be maintained separately from application code so future updates are manageable.

### 7. USER ROLES AND CREDENTIALS

The software must support at least these user profiles.

**A. Aircraft owner / pilot**

Intended for private aircraft owners and pilots performing or documenting authorized preventive maintenance.

Capabilities:

- Create and manage aircraft profiles.
- Enter maintenance discrepancies.
- Maintain inspection and maintenance schedules.
- Prepare preventive maintenance entries.
- Enter work descriptions.
- Print maintenance records.
- Maintain parts and expense histories.
- Track aircraft records.
- Attach invoices and documentation.

The interface must distinguish work an appropriately qualified pilot may perform from work generally requiring other authorized personnel.

Do not assume that ownership of an aircraft alone authorizes maintenance or approval for return to service.

Relevant authorization depends on certificate privileges, aircraft status, operating circumstances, and the nature of the work.

**B. Certificated aircraft mechanic**

Support:

- Airframe mechanic
- Powerplant mechanic
- Airframe and Powerplant mechanic
- Mechanic holding Inspection Authorization

Fields:

- Full name
- Certificate type
- Certificate number
- Ratings
- Inspection Authorization status when applicable
- Optional business name
- Contact information
- Optional certificate expiration or authorization-related dates where applicable
- Saved signature-block preferences

**C. Other appropriately authorized maintenance personnel**

Support configurable profiles for repair stations, repairmen, and other authorized persons or organizations.

Do not assume they have identical privileges.

**D. Recordkeeping-only profile**

Allow an owner or administrator to record historical maintenance performed by others without representing themselves as having performed or approved the work.

Credentials entered in the software are user-provided information.

The application does not verify FAA certificate validity.

Role selection must not be confused with legal authorization.

Where applicable, explain limitations and require the user to affirm responsibility for the actual work, approvals, and statements.

### 8. FIRST-RUN SETUP

Provide an attractive first-run setup wizard.

The setup should ask:

1. Are you primarily an aircraft owner/pilot, mechanic, or both?
2. Would you like to create an aircraft profile?
3. Would you like to configure your maintenance record identity?
4. Where should backups be stored?
5. Would you like to open an optional sample aircraft?

Do not require users to complete all setup steps before exploring the application.

Avoid asking for irrelevant information.

Support multiple aircraft from the beginning.

Provide a brief tutorial introducing:

- Dashboard
- New maintenance entry
- Maintenance tracking
- Printing
- Backup and restore

Create optional sample data using a fictional aircraft, clearly marked as demonstration material.

Do not mix sample records with real records.

The sample aircraft may be a fictional Piper PA-28-161 Warrior, but its registration, component serial numbers, dates, and maintenance records must be invented and unmistakably labeled DEMO.

### 9. AIRCRAFT PROFILE MANAGEMENT

Support complete profiles containing:

- Registration number
- Make
- Model
- Aircraft serial number
- Model year
- Aircraft category
- Airworthiness classification
- Owner/operator
- Base airport
- Registration country
- Optional aircraft photograph
- Aircraft total time
- Tachometer time
- Hobbs meter time
- Time data source
- Last recorded time update
- Last annual inspection
- Applicable inspection program
- Optional operating notes

Create separate records for major installed components.

At minimum:

- Airframe
- Engine
- Propeller
- Avionics
- Appliances
- Other user-defined components

Engine and propeller profiles should support:

- Manufacturer
- Model
- Serial number
- Installation date
- Total time since new
- Time since overhaul
- Time since installation, if relevant
- Overhaul information
- Relevant service limits or recurring requirements
- Historical removal and installation events

Do not assume the aircraft has only one engine or propeller.

Maintain component history when equipment is removed, replaced, or transferred.

Keep historical maintenance associated with the actual component rather than merely its current aircraft.

Allow aircraft profiles to be archived without destroying records.

### 10. MAINTENANCE DASHBOARD

Create a useful dashboard for each aircraft.

Display:

- Aircraft registration and description
- Aircraft operating time
- Last maintenance activity
- Open discrepancies
- Planned maintenance
- Upcoming inspections
- Overdue tracked items
- Airworthiness Directive tracking status
- Recent logbook entries
- Recent maintenance expenses
- Backup status

Use simple, understandable status indicators.

For maintenance reminders:

- Upcoming
- Due
- Past recorded due threshold
- Completed
- Not configured
- Unknown

Avoid displaying an aircraft as legally "airworthy" or "safe to fly" based only on available software records.

Provide a direct route from every dashboard item to its underlying record.

Important actions should be available within one or two clicks.

Prominently include:

**New Maintenance Entry**

**Add Discrepancy**

**Print Logbook Entry**

**View Maintenance Schedule**

### 11. MAINTENANCE LOGBOOK ENTRY SYSTEM

This is the application's most important feature.

Create a polished maintenance entry editor with a live formatted preview.

Support entry categories including:

- Preventive maintenance
- General maintenance
- Repair
- Alteration
- Annual inspection
- 100-hour inspection
- Progressive inspection
- Other inspections
- Airworthiness Directive compliance
- Component installation or removal
- Inspection/test documentation
- Historical entry
- User-defined category

Required or conditionally required fields must reflect the applicable regulation.

For general maintenance entries, support:

- Aircraft or component identification
- Date work was completed
- Relevant operating time
- Description of work performed
- Data or maintenance references
- Person performing the work
- Person approving the work for return to service, where applicable
- Certificate type
- Certificate number
- Signature area
- Notes and supporting documentation

For inspection entries, support the additional requirements of § 43.11, including inspection type, extent, applicable total time, disposition, authorized person, and required certification or discrepancy statements.

Maintain distinct entry models or validation rules when necessary rather than using a generic form that loses required inspection information.

The system must support both approval and nonapproval outcomes.

Do not automatically assume successful completion or return-to-service approval.

#### Maintenance editor behavior

- Autosave drafts safely.
- Provide a clearly labeled Save Draft button.
- Allow reopening and editing drafts.
- Allow work to be documented over multiple sessions.
- Support multiple work descriptions in one entry.
- Support parts and references.
- Allow linking to maintenance discrepancies.
- Provide spellchecking where feasible.
- Provide a live print preview.
- Warn about missing required information.
- Never invent missing maintenance facts.
- Never fabricate a certificate number or signature.

Separate "work documented" from "approved for return to service."

A draft or work-in-progress record must not be shown as a completed approval.

### 12. PILOT PREVENTIVE MAINTENANCE WORKFLOW

Create a simple mode for pilots documenting preventive maintenance they are authorized to perform.

Provide selectable reference categories drawn from the current 14 CFR Part 43 Appendix A(c).

Examples to consider, subject to actual applicability and limitations:

- Oil changes
- Tire replacement or repair
- Lubrication
- Battery servicing or replacement where permitted
- Wheel bearing servicing
- Spark plug servicing or replacement where permitted
- Other permitted preventive maintenance tasks

Do not treat this list as universally permissible for every pilot or aircraft.

The application must display appropriate contextual guidance and links to the controlling provisions.

A user selecting an item should receive help drafting a complete record based on what the user actually performed.

Example workflow:

1. Choose aircraft.
2. Select preventive maintenance.
3. Select task or choose custom.
4. Enter date and relevant time.
5. Describe actual work.
6. Record parts and references.
7. Enter authorized person's information.
8. Preview the entry.
9. Print it for the appropriate physical signature.
10. Optionally attach a scan of the signed record.

Provide editable sample wording, not fabricated statements of completed work.

For example, an oil change template can present fields for oil type, quantity, filter details, inspection observations, and relevant references.

It must not insert an assertion that a filter was inspected or a system was tested unless the user confirms that work was actually completed.

Do not provide unsafe, unsourced maintenance procedures or automatically determine that a maintenance task is permitted.

### 13. MECHANIC MAINTENANCE WORKFLOW

Create a mechanic-focused entry workflow without making the interface significantly more complicated.

Support:

- Maintenance and repair documentation
- Work descriptions
- Technical data references
- Parts installed and removed
- Component serial numbers
- Inspection results
- Discrepancy findings
- Return-to-service documentation
- Certificate information
- Supporting photographs
- Invoices or work order references
- Labor time and cost

Allow the name of the person performing the work to differ from the person approving the work.

For annual inspection entries, apply appropriate authorization checks and warnings.

Do not allow a basic mechanic profile to be treated as automatically authorized to conduct or approve an annual inspection.

Recognize Inspection Authorization privileges and other applicable regulatory authorizations without pretending that software can verify them.

Provide proper workflows for inspections that result in a discrepancy list rather than approval for return to service.

### 14. PRINTING AND PDF GENERATION

Printing quality is a critical acceptance requirement.

A user must be able to create an entry that can be printed and inserted or transferred into a traditional maintenance logbook.

Provide at least three document formats:

**Format A: Compact maintenance logbook entry**

- Minimal margins where appropriate.
- Readable font.
- Clear date and relevant aircraft time.
- Well-formatted work description.
- Appropriate certificate information.
- Physical signature area.
- Suitable for printing, cutting, and attaching to a conventional logbook page.

**Format B: Full-page maintenance record**

- US Letter format.
- Aircraft identification.
- Full maintenance details.
- Technical references.
- Parts information.
- Approval/disposition information as applicable.
- Signature block.
- Optional attached continuation pages.

**Format C: Maintenance history report**

- Selected aircraft or component.
- Configurable date range.
- Chronological records.
- Optional filters.
- Page numbers.
- Record identification.
- Consistent formatting.

Also provide professional reports for:

- Outstanding discrepancies
- Upcoming maintenance
- Inspection history
- AD tracking status
- Component history
- Maintenance expenses
- Aircraft records handover

Printing features:

- Actual printer selection through the operating system.
- Printer-independent PDF creation.
- Print preview.
- Paper size selection where supported.
- Portrait/landscape options.
- Correct page breaks.
- Long-description continuation.
- No clipped text.
- No truncated entries.
- Appropriate signature space.
- Optional compact layout.
- Configurable font size within legibility limits.

Never split a signature block from its associated certification statement in a misleading manner.

Include a document generated timestamp and stable record identifier where useful, but avoid unnecessary branding that would interfere with the official appearance of the maintenance entry.

Branding may appear discreetly on internal reports.

Do not place marketing material inside formal maintenance entries.

### 15. SIGNATURES AND FINALIZED RECORDS

Implement a safe, realistic version 1 signature process.

Support these separate states:

1. Draft
2. Ready to print
3. Printed / awaiting physical signature
4. Signed copy recorded
5. Superseded or amended
6. Historical import requiring verification

A generated document without an actual signature must not be represented as a signed maintenance approval.

For the first release:

- Generate printable signature blocks.
- Allow users to print and physically sign.
- Allow scanned signed documents to be attached.
- Allow users to mark that an externally signed copy has been recorded.
- Record who entered that status, when, and which document supports it.
- Preserve the signed document.
- Store file hashes to detect subsequent changes.
- Prevent silent changes to finalized record content.

Do not implement a simplistic electronic-signature function and claim it meets FAA requirements.

Electronic signatures require their own documented design and compliance analysis against applicable FAA guidance, including AC 120-78B.

Keep the architecture capable of adding a proper electronic-signature workflow in a future version.

For corrections:

- Never silently overwrite a finalized entry.
- Create an identifiable amendment or superseding record.
- Preserve the original.
- Preserve both timestamps.
- Show the relationship between records.
- Distinguish the time an entry was recorded from the date maintenance was performed.

Use database transactions and audit events to preserve integrity.

Be transparent that a local audit trail and hash are tamper-evidence measures, not a substitute for a legally valid electronic-signature system or independent trust infrastructure.

### 16. DISCREPANCY AND MAINTENANCE ITEM TRACKING

Build a complete maintenance tracking module.

Allow users to record:

- Squawks
- Inspection discrepancies
- Open maintenance items
- Planned maintenance
- Repeating maintenance tasks
- Parts needed
- Outstanding corrective actions
- Work awaiting inspection
- Work awaiting return-to-service approval

Each item should include:

- Aircraft
- Associated component
- Title
- Description
- Date identified
- Identified by
- Priority
- Status
- Assigned person or organization
- Relevant supporting records
- Due date or operating-time threshold
- Parts
- Notes
- Completion information
- Linked corrective maintenance entry

Suggested workflow:

Open → Planned → In Progress → Work Completed / Awaiting Approval → Closed

Also support canceled, deferred, and awaiting-parts statuses.

Do not confuse a maintenance tracking status with legal authorization to operate an aircraft.

A "deferred" item must not be represented as approved under an MEL, § 91.213, or any other applicable provision merely because the user selected Deferred.

Discrepancies from inspections that require a signed list must retain the relevant inspection linkage and documentary evidence.

Closing a discrepancy should require appropriate documentation and must not automatically constitute return-to-service approval.

### 17. RECURRING MAINTENANCE AND INSPECTION TRACKING

Provide configurable reminders for calendar-based and operating-time-based events.

Potential tracked events include:

- Annual inspections
- 100-hour inspections when applicable
- ELT inspections
- ELT battery replacement thresholds
- Altimeter/static system checks when applicable
- Transponder inspections
- Oil changes
- Engine-related intervals
- Propeller-related intervals
- Manufacturer-recommended maintenance
- Recurring AD actions
- User-defined maintenance

Do not assume every inspection applies to every aircraft or type of operation.

Specifically:

- Annual inspection timing must follow applicable calendar-month rules.
- 100-hour inspection tracking must depend on operational applicability.
- Altimeter/static requirements must account for the relevant operating circumstances.
- ELT replacement tracking must support the applicable battery-use and life limitations.
- Manufacturer recommendations must not automatically be represented as federal regulatory requirements.
- Recurring AD requirements must be configurable based on the applicable AD.

Support:

- Calendar interval
- Operating-hours interval
- Cycles interval when relevant
- Earlier-of-multiple-limits logic
- One-time events
- Recurring events
- Unknown interval
- User-configured reminder lead times

Maintain separate Hobbs, tachometer, airframe total time, and component times.

Never assume those values are interchangeable.

Track units explicitly and store operating-time quantities with sufficient decimal precision to avoid floating-point errors.

If required data is missing, show "Unknown" rather than calculating an unreliable due date.

Do not silently reset an inspection interval when an unrelated maintenance event is recorded.

Use explicitly linked qualifying events to calculate next-due values.

Provide unit tests for end-of-month, calendar-year boundaries, leap years, inspection interval calculations, and operating-time thresholds.

### 18. AIRWORTHINESS DIRECTIVES AND SERVICE BULLETINS

Create an AD tracking module that allows users to enter and manage:

- AD number
- Revision
- Issuing authority
- Affected component
- Applicability status
- Applicability rationale
- Compliance requirements
- Compliance method
- Supporting documentation
- Last compliance date
- Relevant operating time
- Recurring interval
- Next required action
- Notes
- Linked maintenance records

Supported applicability statuses:

- Applicable
- Not applicable, documented rationale
- Under review
- Unknown

Do not automatically declare an AD inapplicable solely because a component model appears different.

Provide support for recurring and one-time actions.

Create a separate service bulletin tracker.

Clearly distinguish mandatory regulatory requirements from recommendations or other manufacturer publications.

Never fabricate AD numbers, revisions, or compliance methods.

If current external information cannot be verified, require manual entry or review.

The first release does not need live FAA AD database integration.

Instead, build a reliable manual tracking system with a future integration boundary.

### 19. PARTS AND COMPONENT TRACKING

Allow maintenance entries to reference:

- Part description
- Part number
- Serial number
- Manufacturer
- Quantity
- Installed or removed
- Installation date
- Removal date
- Relevant operating time
- Cost
- Supplier
- Receipt
- Supporting airworthiness documentation
- Optional notes

Support multiple parts per maintenance event.

Support component replacement and historical identification.

Store attached FAA Form 8130-3 documents, FAA Form 337 copies, invoices, and other supporting records when provided.

Do not generate a document that impersonates an official FAA form.

Do not treat a purchased part or uploaded document as proof of installation eligibility, airworthiness, or compliance.

### 20. MAINTENANCE COST TRACKING

Include a practical expense module.

Track:

- Parts
- Labor
- Consumables
- Inspections
- Outside services
- Miscellaneous maintenance expenses

Allow costs to be linked to a specific maintenance entry or work item.

Support:

- Amount
- Currency
- Date
- Vendor
- Payment status
- Invoice reference
- Attachment
- Notes

Provide reports for:

- Annual maintenance expenses
- Expenses by category
- Expenses by aircraft
- Expenses by component
- Parts versus labor
- Selected date ranges

Do not make financial tracking mandatory for recording maintenance.

Design this module with a future one-way CSV integration or import/export interface for FlightCost, another The Thrifty Pilot aircraft ownership application.

Do not invent or assume an undocumented FlightCost database schema.

Do not modify another application's files without an explicit integration specification.

### 21. SEARCH, FILTERING, AND HISTORY

Include a fast searchable maintenance history.

Search by:

- Aircraft registration
- Entry type
- Date
- Operating time
- Work description
- Mechanic
- Certificate number
- Part number
- AD number
- Component
- Discrepancy
- Status

Provide sensible sorting and filters.

Allow individual records to be opened directly from search results.

Support exporting selected records.

Provide a timeline view of aircraft and component maintenance.

Keep the UI responsive with large datasets.

### 22. ATTACHMENTS AND DOCUMENT MANAGEMENT

Support attachments including:

- PDF
- JPEG
- PNG
- Other explicitly supported safe document formats

Typical attachments:

- Maintenance invoices
- Signed logbook entries
- Parts receipts
- Inspection reports
- Work orders
- Technical references
- AD compliance records
- Equipment documentation
- Photographs

Store managed copies inside the application data area.

Avoid relying exclusively on original file paths that may later disappear.

Use stable attachment identifiers, file hashes, and database relationships.

Prevent unsafe file path handling and filename collisions.

Support attachment viewing through appropriate system applications.

Do not execute attachments.

Provide controls for attachment deletion that respect finalized records and their retention requirements.

### 23. DATABASE INTEGRITY AND AUDITABILITY

Use SQLite with appropriate transaction handling and foreign-key enforcement.

Implement:

- Schema migrations
- Referential integrity
- Input validation
- Reasonable indexes
- Unique record identifiers
- Created and modified timestamps
- Audit events
- Backup validation
- Database integrity checks
- Safe application shutdown
- Recovery from interrupted writes

Finalized records must not be silently rewritten.

Use append-only amendment relationships for finalized content.

Maintain a clear distinction between operational tracking data that may change and finalized maintenance records that must preserve their historical meaning.

Prevent accidental cross-aircraft data association.

Test concurrent windows and repeated clicks to avoid duplicate entries.

Handle unexpected shutdowns without corrupting the database.

### 24. BACKUP, RESTORE, AND DATA PORTABILITY

Treat maintenance records as irreplaceable user data.

Provide:

- Manual backup
- Configurable automatic backups
- Backup folder selection
- Backup history
- Backup verification
- Restore workflow
- Export to PDF
- Export to CSV
- Full structured export, such as JSON with a documented schema
- Optional complete archive containing database and attachments

Use a safe SQLite backup method rather than copying an active database file unsafely.

Backup archives must include all necessary user records, metadata, and attachments.

Restore must:

1. Validate the archive.
2. Display its contents and version.
3. Warn before replacing data.
4. Offer a backup of the current state.
5. Prevent path traversal.
6. Restore transactionally where feasible.
7. Verify the restored database.
8. Report success or failure accurately.

Never overwrite current data without explicit user confirmation.

Prefer retaining all maintenance records indefinitely unless the user deliberately performs a permitted export or deletion operation.

Do not automatically purge historical maintenance records based on a simplistic one-year retention interpretation.

Maintain support for records that must accompany an aircraft or component during transfer.

Support producing an aircraft-record handover archive for ownership changes.

### 25. IMPORTING EXISTING MAINTENANCE RECORDS

Provide a manual historical entry workflow.

Many aircraft owners already have decades of paper logbooks.

Allow users to:

- Enter prior maintenance events.
- Record information from existing paper records.
- Attach scanned logbook pages.
- Identify source documents.
- Mark entries as historical imports.
- Enter original maintenance dates.
- Preserve uncertainty or missing fields.
- Avoid representing newly transcribed information as newly performed maintenance.

Support CSV import with preview and field mapping.

Do not fabricate missing information.

Do not automatically interpret an old signature image as a newly executed electronic signature.

If optical character recognition is not reliable enough for production, omit automated OCR from version 1 rather than implementing misleading extraction.

### 26. USER EXPERIENCE AND NAVIGATION

Use a simple navigation structure:

**Dashboard**

**Aircraft**

**Logbook**

**Maintenance Items**

**Schedules**

**ADs & Service Bulletins**

**Parts & Expenses**

**Reports**

**Settings & Backups**

Provide contextual actions and sensible shortcuts.

The most important feature, creating a maintenance entry, should always be easy to find.

Avoid excessive configuration before meaningful use.

Provide helpful empty states.

Use plain English.

Examples:

"Add your first aircraft"

"No open maintenance items"

"Create a new logbook entry"

"Print this entry"

"Last backup: Not yet created"

Error messages must explain the problem and what the user can do next.

Support light and dark mode.

Remember reasonable window size, sorting, filters, and selected aircraft.

### 27. SETTINGS AND DOCUMENT PREFERENCES

Include settings for:

- Default aircraft
- User identity
- Mechanic profiles
- Theme
- Date formatting
- Units
- Currency
- Backup location
- Backup schedule
- Printer preferences
- Default logbook template
- Reminder thresholds
- Application data location display
- Export preferences
- Application version

Do not expose dangerous configuration controls without an explanation of their effects.

### 28. SECURITY AND PRIVACY

The application must operate completely offline for its core functions.

Do not require:

- Internet access
- User accounts
- Online authentication
- Subscriptions
- Telemetry
- Cloud storage
- Advertising services

Do not transmit maintenance or certificate information to an external service.

If an optional future update check is implemented, it must be disabled by default or clearly opt-in and must not transmit aircraft records.

Do not log sensitive document contents or complete certificate information unnecessarily.

Avoid storing user data in temporary installer directories.

Support recoverable backups and appropriate local filesystem permissions.

No claims of enterprise-grade access control or regulatory security certification without evidence.

### 29. HELP AND DOCUMENTATION

Include an accessible help center within the application.

Provide:

- Quick-start guide
- Aircraft setup instructions
- Creating maintenance entries
- Pilot preventive maintenance workflow
- Mechanic workflow
- Printing instructions
- Recording signed copies
- Inspection tracking
- AD tracking
- Backup and restore
- Troubleshooting
- Regulatory limitations

Provide a clearly visible disclaimer explaining that users are responsible for verifying regulatory applicability, work performed, qualifications, record accuracy, and proper approval for return to service.

Help material must not represent general guidance as a substitute for applicable maintenance manuals, current regulatory text, or authorized professional judgment.

### 30. QUALITY ASSURANCE

Implement meaningful automated tests.

At minimum, test:

**Aircraft data**
- Creation and modification
- Multiple aircraft
- Duplicate registrations
- Component history
- Component removal and replacement
- Time record updates

**Maintenance entries**
- Draft creation
- Draft editing
- Required-field validation
- Inspection-specific requirements
- Record finalization
- Historical imports
- Amendments
- Correction history
- Work performer versus approving person
- Protection of finalized records

**Regulatory and workflow safeguards**
- Missing certificate details
- Pilot preventive maintenance restrictions
- Annual inspection authorization warnings
- Inspection approval and nonapproval paths
- Discrepancy-list handling
- Drafts not constituting approval
- No false electronic-signature claims

**Schedules**
- Calendar-month calculations
- Leap-year calculations
- End-of-month logic
- Hour-based intervals
- Earlier-of-two-limits rules
- Missing time values
- Nonapplicable inspection tracking
- Recurring AD calculations

**PDF and printing**
- Single entry
- Long entry
- Inspection entry
- Compact format
- Full-page format
- Multi-page report
- Signature block
- Correct page boundaries
- Embedded fonts and character handling
- No overlapping text
- No clipped information

**Data integrity**
- Backups
- Restore
- Corrupted backup
- Schema migration
- Duplicate actions
- Unexpected shutdown recovery
- Attachment preservation
- Audit event generation
- Prevention of silent finalized-record modification

**Import/export**
- CSV validation
- Data mapping
- Structured export
- Complete aircraft handover archive
- Reimport validation
- Special characters
- Empty datasets

**Windows distribution**
- Fresh installation
- First launch
- Database creation
- Normal application restart
- Upgrade preserving data
- Uninstall behavior
- Installation without Python
- PDF output in packaged build
- Optional print dialog behavior

### 31. AUTOMATED END-TO-END TESTING

Create repeatable acceptance scenarios.

**Scenario A: First-time aircraft owner**

1. Install the program.
2. Launch it without Python installed.
3. Create an aircraft.
4. Set current operating time.
5. Add an oil change as an example preventive maintenance draft.
6. Enter actual work details.
7. Preview the document.
8. Generate PDF.
9. Print or save the document.
10. Record a signed copy.
11. Confirm the historical record remains available.
12. Restart the program and verify data persistence.

**Scenario B: A&P mechanic**

1. Open an existing aircraft.
2. Create a maintenance event.
3. Enter multiple maintenance actions.
4. Record parts and technical references.
5. Identify performer and authorized approving person separately.
6. Create a printable maintenance record.
7. Verify required fields.
8. Record the physical signing status.
9. Reopen the record.
10. Confirm finalized content cannot be silently altered.

**Scenario C: Annual inspection**

1. Select annual inspection.
2. Enter inspection data.
3. Verify appropriate authorizations and warnings.
4. Record an inspection outcome.
5. Test both approval and nonapproval paths.
6. Generate a discrepancy list for a nonapproval case.
7. Print the correct documents.
8. Verify inspection-specific statements.
9. Verify that an unresolved discrepancy is not automatically cleared.

**Scenario D: Maintenance tracking**

1. Create an open discrepancy.
2. Assign a priority.
3. Link it to a planned task.
4. Record corrective maintenance.
5. Attach supporting evidence.
6. Complete any appropriate approval workflow.
7. Close the discrepancy with documented linkage.
8. Confirm its history remains available.

**Scenario E: Backup and recovery**

1. Create multiple records and attachments.
2. Generate a complete backup.
3. Verify the backup.
4. Introduce additional test records.
5. Restore the earlier backup after confirmation.
6. Verify restored content and attachments.
7. Confirm integrity checks succeed.

Use automated GUI smoke tests where feasible.

Where physical printer testing is unavailable, thoroughly test PDF generation and print layout, and explicitly document that physical printer validation remains outstanding.

### 32. PERFORMANCE AND RELIABILITY

The software should launch promptly on an ordinary Windows laptop.

It should remain responsive with thousands of entries.

Avoid blocking the GUI during large imports, exports, or backup operations.

Provide progress feedback for longer operations.

Use safe threading or background worker patterns for operations that could block the interface.

Handle disk-full, missing-file, permission, corrupted-database, and failed-PDF-generation scenarios gracefully.

Never report an operation as completed unless it actually succeeded.

### 33. RELEASE DOCUMENTATION

Create and maintain:

- README.md
- USER_GUIDE.md
- INSTALLATION.md
- BUILD_WINDOWS.md
- ARCHITECTURE.md
- DATABASE_SCHEMA.md
- REGULATORY_REFERENCES.md
- REGULATORY_LIMITATIONS.md
- TEST_PLAN.md
- TEST_RESULTS.md
- SECURITY_AND_PRIVACY.md
- RELEASE_NOTES.md
- THIRD_PARTY_LICENSES.md
- IMPLEMENTATION_LOG.md
- KNOWN_LIMITATIONS.md

Documentation should be useful rather than repetitive.

Include the exact build commands and any required Windows development dependencies.

Create an appropriate open-source project license after checking compatibility with dependencies.

Include screenshots of the actual application where available.

Do not generate fabricated screenshots.

### 34. GITHUB AND RELEASE PIPELINE

Prepare the repository for GitHub publication.

Include:

- Clear project description
- Installation instructions
- Screenshots
- Release download instructions
- Issue templates
- Versioning
- Changelog
- Windows build workflow
- Installer artifact generation
- Source release
- License information

Configure GitHub Actions to build on a Windows runner.

The workflow should:

1. Set up the required Python environment.
2. Install locked dependencies.
3. Run tests.
4. Build the Windows executable.
5. Package the installer.
6. Run feasible packaged-application smoke tests.
7. Upload build artifacts.
8. Produce a release artifact on an authorized version-tagged release.

Never assume a successful build because configuration files exist.

Do not publish a remote repository or release without the required authorization and credentials.

### 35. VISUAL DESIGN REVIEW

After implementing the application, conduct an actual UI review.

Assess:

- Dashboard readability
- Visual consistency
- Form usability
- Excessive clicks
- Layout at normal and high DPI
- Keyboard accessibility
- Dark/light theme contrast
- Error presentation
- Empty-state presentation
- PDF appearance
- Navigation consistency
- First-run experience

Fix material usability problems before release.

Prioritize usefulness and reliability over decorative elements.

### 36. SCOPE AND PRIORITY MANAGEMENT

This is intended to be a complete and usable initial release.

Prioritize the following in order:

**Priority 0: Must work**

- Windows application startup
- Aircraft profiles
- Pilot and mechanic profiles
- Maintenance entry creation
- Inspection-specific entries
- PDF generation
- Printing
- Maintenance history
- Local database persistence
- Backup and restore
- Regulatory safeguards
- Data integrity
- Windows installer

**Priority 1: Required for the intended release**

- Discrepancy tracking
- Maintenance schedules
- AD tracking
- Component history
- Parts management
- Expenses
- Search
- Reports
- Historical records
- Import/export
- Documentation

**Priority 2: Polish and extensibility**

- Advanced filtering
- Theming
- Enhanced dashboards
- Advanced report customization
- Optional integrations
- UI refinements

Do not sacrifice Priority 0 reliability to implement a Priority 2 feature.

If implementation capacity is constrained, complete the functional core and clearly identify unfinished items.

Never conceal an incomplete feature behind attractive interface design.

### 37. DEFINITION OF DONE

The application is ready for a version 1 release only when:

1. A normal user can install it on Windows.
2. It launches without requiring a development environment.
3. Users can create real aircraft profiles.
4. Maintenance records persist correctly.
5. Pilot and mechanic workflows function.
6. Inspection-specific validation functions.
7. Professional logbook entries generate correctly.
8. PDF export works from the installed application.
9. Print preview and printing functions are implemented.
10. Maintenance tracking works.
11. Data survives restarts and upgrades.
12. Backup and restore work.
13. Finalized records cannot be silently modified.
14. Regulatory limitations and signature handling are clearly documented.
15. Automated tests pass.
16. The repository includes reproducible release tooling.
17. Installation and release artifacts are actually built and validated where the environment permits.
18. No essential screen contains mock functionality.
19. The application is reasonably accessible and visually polished.
20. Known limitations are disclosed accurately.

### 38. FINAL PROJECT REVIEW AND HANDOFF

Before completing, perform a comprehensive audit comparing the implementation against every numbered section of this specification.

Create a completion matrix with:

- Requirement
- Implementation status
- Source file or relevant module
- Test coverage
- Verification evidence
- Remaining work, if any

Fix high-priority gaps and rerun relevant tests.

Do not merely report that a feature works because the source code appears to support it.

Provide an end-of-project summary containing:

1. What was built.
2. How to install and run it.
3. Location of the Windows installer.
4. Location of the portable version, if created.
5. Database and backup storage locations.
6. Test results.
7. Regulatory and electronic-signature limitations.
8. Known issues.
9. Any verification that could not be performed.
10. Recommended next enhancements.

**FINAL INSTRUCTION**

Build The Thrifty Pilot | Aircraft Maintenance Logbook as a complete, dependable, offline Windows application that real aircraft owners and appropriately authorized maintenance personnel can use to prepare, organize, preserve, and print aircraft maintenance records.

Make the common tasks exceptionally simple.

Make the underlying architecture robust.

Treat regulatory accuracy, signed record integrity, and protection of historical aircraft maintenance information as nonnegotiable priorities.

Implement, test, inspect, improve, package, and document the actual product.

Do not stop at planning.

Do not substitute simulated functionality for working software.

Do not claim regulatory approval, signature validity, successful testing, or release readiness without supporting evidence.

Deliver the strongest verifiable first-pass implementation possible.
