# Keys NG M1.20 — Interactive UI Parity & KeePassXC Import

Version: `0.1.20.dev0`

## Highlights

- Explicit GUI/TUI interactive capability parity contract with regression tests.
- KeePassXC `.kdbx` and XML import added to GUI and TUI, including dry-run preview, optional key file, no-password mode, YubiKey parameter and transient in-memory database password support.
- Full-vault KeePassXC XML export added to GUI and TUI; single-entry export remains available in both.
- Password generator integrated into both entry editors using the shared cryptographically secure generator.
- Notes are selectable/copyable in the GUI detail view, have an explicit timed **Copy notes** action in GUI/TUI, and normal copy/cut/paste behavior is preserved while editing.
- TUI can start with an Open/Create/Recent vault screen, open another vault, close the current vault, choose recent vaults, edit core preferences and read Help/Security/License.
- KeePassXC CLI discovery now checks common Windows/macOS installation paths in addition to `PATH`.
- The OpenPGP private-key passphrase boundary is unchanged: Keys NG never asks for it; GnuPG/gpg-agent/pinentry own it.

## Security notes

Interactive KDBX passwords are never written to files, argv or environment variables. They are transient Python strings sent to `keepassxc-cli` over stdin. This is distinct from the GnuPG private-key passphrase and is documented as an in-memory exposure during import.

KeePassXC XML export is plaintext and must be protected/deleted after use. Import continues to reject DOCTYPE/entities, performs reference-safe UUID mapping and validates the encrypted destination records after import.
