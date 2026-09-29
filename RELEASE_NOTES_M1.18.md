# Keys NG M1.18 — TUI feature parity

Version: `0.1.18.dev1`

M1.18 is a focused usability and parity release. It does not change the frozen vault schema introduced for the M1.17 review cycle.

## TUI editing and organization

The Textual interface can now create and fully edit credentials using the same frontend-neutral `EntryDraft`/`build_entry_from_draft()` conversion used by the PySide6 GUI. Supported fields include title, logical folder, generic/Web/SSH/RDP type, username/password (including UUID references), URL or remote host/port, SSH X11 and advanced options, tags, TOTP URI/secret, QR image import and notes. Existing command actions and custom fields that are not exposed by the editor are preserved during edits.

The TUI can create, rename and delete folders, and move both entries and folders. Folder moves are validated against hierarchy cycles and duplicate sibling names. Rename/move validation now operates on a cloned `FolderStore`, so a rejected operation cannot leave the decrypted in-memory cache in an invalid partially-mutated state.

## Clipboard feedback

Successful, warning and failed clipboard operations are shown in a high-visibility timed banner rather than only in the ordinary status line. The default colors use Textual's semantic theme colors, which provide a portable contrast-aware default without querying terminal-specific OSC background extensions. Users can override foreground/background and banner duration under `[ui.tui]`.

## Keyboard workflow

- `N`: new entry
- `Shift+N`: new folder (inside the selected/current folder)
- `E`: edit entry / rename folder
- `M`: move selected entry/folder
- `Delete`: delete selected entry or empty folder, after confirmation
- `X`: export selected entry as plaintext KeePass-compatible XML

Existing copy/open/search/lock shortcuts remain available. A context-sensitive command hint bar makes the relevant operations discoverable without memorizing the complete key map.

## Security notes

M1.18 deliberately centralizes editor validation instead of cloning the GUI business rules in the TUI. Password and TOTP editor widgets necessarily contain plaintext in Python/Textual memory while the modal editor is open; they are not persisted until encrypted by `Vault.save_entry()`, and Keys NG still makes no secure-zero claim for Python-managed memory.

The release remains pre-1.0 and not independently security-audited.
