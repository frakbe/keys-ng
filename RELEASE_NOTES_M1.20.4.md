# Keys NG M1.20.4 — TUI multi-vault switcher

Version: `0.1.20.dev4`

M1.20.4 completes the TUI multi-vault workflow discovered during Linux testing of M1.20.3.

## Changes

- Added `VaultSessionManager` to keep multiple `Vault` instances open in one TUI process.
- `F5` and `F6` now add/activate vaults instead of replacing the current vault by restarting the TUI.
- Added `Ctrl+J` as the terminal-portable **Open vaults / switch active vault** shortcut.
- The switcher shows every open vault and its locked/unlocked state, and can activate or close a selected vault.
- `Ctrl+W` closes only the active vault; another open vault becomes active automatically when available.
- `Ctrl+L` remains per-vault.
- `F9` now hard-locks every open vault, clearing all decrypted vault caches before clearing the shared GnuPG agent cache.
- Switching to an already locked vault does not decrypt it; the TUI shows a locked placeholder until `Ctrl+P` unlocks that vault.
- Updated EN/IT inline command help, user/developer guides and code-review manuals.

## Regression coverage

Tests cover opening/switching multiple vault sessions, preserving independent lock state, active-vault fallback after close, global lock-all semantics, and the `Ctrl+J` TUI binding.
