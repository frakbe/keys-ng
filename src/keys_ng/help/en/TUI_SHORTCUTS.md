# Keys NG TUI commands

This screen lists the stable keyboard shortcuts for the terminal interface.

## Main screen

- `?` — open this command guide.
- `F1` — open Help / User guide / Security / License.
- `F2` — Preferences.
- `F3` — Trusted Inbox signers.
- `F4` — copy the selected entry UUID.
- `F5` — open another vault.
- `F6` — open a recent vault.
- `Ctrl+J` — open the vault switcher and activate/close one of the vaults already open in this TUI session.
- `F7` — import a KeePassXC database or XML file.
- `F8` — export the complete vault as KeePassXC XML.
- `F9` — hard lock and clear the GnuPG agent cache.
- `Ctrl+Q` — quit.
- `Ctrl+F` — focus search.
- `N` — create a new entry.
- `Ctrl+D` — create a new folder.
- `E` — edit the selected entry or rename the selected folder.
- `M` — move the selected entry or folder.
- `Delete` — delete the selected entry or folder.
- `Ctrl+U` — copy URL.
- `Ctrl+B` — copy username.
- `Ctrl+C` — copy password when focus is outside a text editor.
- `Ctrl+T` — copy TOTP.
- `Ctrl+N` — copy the complete Notes field with timed clipboard clearing.
- `Ctrl+O` — execute/open the selected entry action.
- `X` — export the selected entry as plaintext KeePassXC XML after confirmation.
- `Ctrl+W` — close the current vault; if other vaults are open, the most recently opened remaining vault becomes active.
- `Ctrl+L` — lock the vault.
- `Ctrl+P` — unlock the vault.
- `R` — reload the vault tree.
- `I` — review the Inbox.

## Text editing

When an Input or TextArea has focus, its normal editing shortcuts take precedence where applicable. In particular `Ctrl+C`, `Ctrl+X`, and `Ctrl+V` retain their normal copy/cut/paste meaning inside editors.

## Password generator

- **Generate** creates a new candidate password.
- **Copy generated password** copies the candidate without applying it to the entry. The clipboard is cleared according to the configured secret timeout when the native clipboard helper is available.
- **Use password** applies the candidate to the entry editor.
- **Cancel** closes the generator without changing the entry.

## Lock state

The tree remains visible after locking so the user can keep orientation inside the vault. Opening an entry while locked does not decrypt it; Keys NG asks you to press `Ctrl+P` to unlock first.

## Multiple open vaults

`F5` and `F6` add vaults to the current TUI session instead of replacing the active vault. Use `Ctrl+J` to switch between them. Each vault keeps an independent locked/unlocked state. `Ctrl+L` locks only the active vault; `F9` hard-locks every open vault and clears the shared GnuPG agent cache.
