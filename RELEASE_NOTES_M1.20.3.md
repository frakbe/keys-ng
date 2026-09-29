# Keys NG M1.20.3 — TUI keyboard, lock-safety and password-generator hotfix

Version: `0.1.20.dev3`

M1.20.3 follows real Linux TUI testing of M1.20.2 and focuses on terminal-portable keyboard behavior and lock-state safety.

## TUI shortcut redesign

The main TUI no longer relies on `Ctrl+Shift+<letter>` combinations. Many terminal protocols do not preserve Shift independently when Ctrl is pressed, so these combinations may arrive as the corresponding `Ctrl+<letter>` sequence. `Ctrl+I` is also commonly an alias of Tab.

The stable TUI shortcuts are now:

- `F2` Preferences
- `F3` Trusted signers
- `F4` Copy UUID
- `F5` Open vault
- `F6` Recent vault
- `F7` Import KeePassXC KDBX/XML
- `F8` Export complete vault XML
- `F9` Hard lock / clear gpg-agent
- `Ctrl+N` Copy Notes
- `Ctrl+D` New folder
- `?` Inline TUI command guide

Existing portable shortcuts such as `Ctrl+L` lock, `Ctrl+P` unlock, `Ctrl+C` password, `Ctrl+B` username, `Ctrl+T` TOTP, `Ctrl+U` URL, `Ctrl+O` action, `I` Inbox and `X` single-entry export are retained.

## Locked-vault selection crash

The tree intentionally remains visible while locked, but selecting a node must not attempt record or folder decryption. `on_tree_node_selected()` now checks the lock state before any `vault.get_entry()` or `vault.get_folder()` operation and displays an unlock instruction instead.

## Safer single-entry export

`X` now displays an explicit confirmation before creating a plaintext KeePassXC XML file. The confirmation states that decrypted credential data will be written. The generic TUI confirmation dialog now supports operation-specific labels instead of always showing a destructive `Delete` button.

## Password generator workflow

The TUI generator now includes **Copy generated password**. This copies the candidate using the timed secret clipboard mechanism without applying it to the entry. The user can therefore update/test the password on the target service first and select **Use password** only after successful verification.

## Help

Press `?` to open the new packaged `TUI_SHORTCUTS.md` command guide. `F1` retains the broader documentation chooser and includes the shortcut guide as its first item.

## Regression coverage

New tests verify that:

- the main `KeysApp` bindings contain no `Ctrl+Shift+<letter>` shortcuts;
- `Ctrl+I` is not used for trusted signers;
- `?` opens the command guide;
- locked tree selection is guarded before vault reads;
- single-entry export requires confirmation;
- the password generator provides a copy-before-use path.
