# Release 0.2.2 validation

The release workflow `.github/workflows/release-0.2.2.yml` runs all regression
tests and static security checks on Python 3.11 and 3.12, builds the distribution,
installs the wheel in a clean environment and runs CLI/TUI version checks,
offscreen Qt interaction smoke and real GnuPG smoke with a disposable keyring.
Only successful matrix runs allow publication from main. Staging runs do not
publish a release. See GitHub Actions for the authoritative matrix results.

Local preparation on Linux/Python 3.12: 187 regression tests, security static
check and offscreen GUI smoke passed. The local environment cannot start
gpg-agent; real OpenPGP validation is mandatory in the workflow before release.
GUI coverage includes multi-tag selection/new tags, persistence in the list,
soft deletion, cancellation, restore, permanent deletion, empty-trash cancellation
and confirmation, references, clipboard expiry and vault locking. Storage tests
cover old-vault migration, idempotency, Trash protection, nested contents,
reopening, catalog integrity and all three catalog privacy levels.

Manual checks still required: native clipboard/Pinentry on Linux desktops,
Windows/macOS startup and packaging, HiDPI and theme changes, and an independent
security review. Automated offscreen tests do not substitute these checks.
