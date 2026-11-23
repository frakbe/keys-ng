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

## Post-release preferences fix (2026-11-23, main)

Saving Preferences called a missing `VaultPane.reset_auto_lock_timer` method after
writing settings. The shared reset method now applies timeout changes to every
open vault, stops the old timer when timeout is zero, and keeps locked vaults
stopped. Startup, activity, unlock, normal lock, hard lock and close use the same
timer policy. Cancel leaves settings and timer intervals unchanged.

The expanded GUI smoke reproduced the original AttributeError before the fix,
then passed with two vaults, including disabled/enabled timers, a locked vault,
cancel, real timer expiry, unlock and hard lock. All 188 regression tests and
static security checks passed locally on Linux/Python 3.12. The original v0.2.2
release artifacts do not include this post-release fix; rebuild from updated main.
