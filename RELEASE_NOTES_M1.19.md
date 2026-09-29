# Keys NG M1.19 — Windows Packaging & Vault Onboarding

Version: `0.1.19.dev0`

M1.19 consolidates the Windows packaging path validated with Briefcase and adds guided vault creation to the graphical and terminal interfaces.

## Highlights

- Shared `services.vault_init` policy used by CLI, GUI and TUI vault creation.
- GUI **New Vault** wizard with directory, recipient, signer, catalog privacy, full fingerprints and pre-write OpenPGP self-test.
- TUI can now be started without a vault path and presents a keyboard-first new-vault wizard.
- GnuPG executable discovery now supports explicit configuration, PATH, Windows registry installation roots and standard Gpg4win/GnuPG locations.
- `gpg.exe` and `gpgconf.exe` paths can be overridden in global settings; GUI Preferences includes a GnuPG verification action.
- `doctor` reports the resolved paths and discovery methods through the GnuPG backend diagnostics.
- Briefcase metadata fixed for PEP 639 and real package/app alignment; GUI, CLI and TUI package definitions are present.
- Added bilingual `WINDOWS_MSI_BUILD.md`, including the verified Git for Windows prerequisite and troubleshooting from real Windows builds.

## Security notes

Keys NG still does not generate OpenPGP key pairs. Vault creation only selects existing GnuPG keys. A crypto self-test is performed before any vault files are written. Existing non-empty directories are rejected.
