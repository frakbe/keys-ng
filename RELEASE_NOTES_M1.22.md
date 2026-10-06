# Keys NG 0.1.22 — Guided standalone encrypted-entry export

Version: `0.1.22`

## Changes

- GUI and TUI can export the selected vault entry as a standalone encrypted `.gpg` record.
- The recipient is selected from usable encryption-capable public keys in the active GnuPG keyring.
- A public-key file can be imported explicitly into the active GnuPG keyring and then selected.
- The export can optionally be signed with a local secret signing key.
- GUI and TUI allow choosing the destination path.
- Exported entries receive a new UUID, have no source-vault folder association, and resolve local username/password UUID references.
- The export reuses the existing atomic encrypted-record writer and does not create plaintext temporary files.

The imported public key is added to the current GnuPG keyring only after explicit user confirmation. Verify the displayed full fingerprint before exporting.
