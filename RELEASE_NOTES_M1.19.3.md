# Keys NG M1.19.3 — TUI Inbox hotfix

Version: `0.1.19.dev3`

M1.19.3 is a focused hotfix for the TUI Inbox and Trusted Signers modal screens introduced in M1.19.2.

## Fixed

- Fixed a TUI crash when pressing `I` to review pending Inbox entries.
- Fixed the same latent lifecycle collision in the Trusted Signers modal.
- Renamed application-specific `refresh()` methods to `refresh_inbox()` and `refresh_signers()`.
- Added a regression test preventing these Textual modal screens from overriding `Widget.refresh()` again.

## Cause

Textual invokes its inherited `Widget.refresh()` during screen registration and stylesheet processing, before the screen's composed child widgets have mounted. M1.19.2 accidentally overrode that framework method in `InboxScreen` and `TrustedSignersScreen`. The custom method then queried `#inbox-select` / `#trusted-select` too early and could raise `NoMatches`.

This bug is framework-lifecycle related and is not Windows-specific, although it was first reproduced on Windows.
