# Public distribution — 1.1.0-rc1

Published at the owner's explicit request on October 30, 2026 (America/New_York; October 31 UTC).

- Repository: https://github.com/thethriftypilot/AircraftMaintenanceLogbook
- Evaluation prerelease: https://github.com/thethriftypilot/AircraftMaintenanceLogbook/releases/tag/v1.1.0-rc1
- Website: https://www.thethriftypilot.com/aviation-software

The prerelease contains the verified installer, portable edition, tested source snapshot and a release-specific SHA256SUMS.txt. GitHub asset digests match local SHA-256 values. The tested source archive is preserved unchanged; subsequent repository changes document publication and repair CI compiler acquisition. The original 1.0.0 artifacts remain preserved locally.

Pilot Tools includes a native download link and a new directory card with an actual fictional-demo screenshot, feature overview, setup instructions, source and guide links, and an unsigned evaluation notice. All four existing tool entries remain present. Desktop and mobile previews were checked, publication was confirmed in Wix, and the live page's logbook links, loaded image and limitations text were verified.

Publication does not complete the independent aviation, signing, printer, clean-machine or user acceptance gates listed in KNOWN_LIMITATIONS.md and COMPLETION_MATRIX.md.

The initial GitHub workflow failed because Chocolatey did not provide the pinned Inno Setup version. The workflow now fetches that same version from the vendor's GitHub release and validates its published SHA-256 digest before installation. This affects CI setup only; published application binaries are unchanged.

The corrected [Windows workflow run](https://github.com/thethriftypilot/AircraftMaintenanceLogbook/actions/runs/41161518263) completed successfully, including tests, executable/installer packaging, source archiving and artifact uploads.
