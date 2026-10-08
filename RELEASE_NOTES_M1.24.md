# Keys NG 0.1.24 — KeePassXC import and TUI help

## Changes

- Added the standalone encrypted-entry export shortcut to the TUI command guide: s.
- KeePassXC KDBX/XML imports now preserve unsupported command-like URLs and custom command fields in Notes without replacing existing notes.
- Import reports list entries that were imported partially and require manual review.
- Added regression coverage for command preservation and partial-import reporting.
- Added complete English and Italian Linux Flatpak build guides under docs.

The Flatpak manifest continues to delegate GnuPG, SSH and RDP helpers to the host by design; review the documented permissions before distributing it.
