# Keys NG User Guide

## 1. What Keys NG is

Keys NG is an OpenPGP-based password manager. Each entry is stored as a separate encrypted file, while searchable metadata and the logical folder tree are stored in encrypted metadata files. The same vault can be used through the command line, the Textual TUI, or the PySide6 GUI.

The main design goals are:

- no plaintext credential files during normal vault operation;
- public cloud storage can contain the encrypted vault;
- decryption is delegated to GnuPG and `gpg-agent`;
- individual entries can contain passwords, TOTP tokens, URLs, SSH or RDP actions;
- folders are logical and encrypted rather than visible directory names;
- credentials can be reused through UUID references;
- a third party can create an inbox item using only the vault owner's public key.

## 2. Installation

Create a virtual environment and install the desired frontends:

```bash
python -m venv ~/.venvs/keys-ng
source ~/.venvs/keys-ng/bin/activate
pip install 'keys-ng[gui,tui,qr]'
```

GnuPG must be installed separately. The GUI requires PySide6, the TUI requires Textual, and QR import requires the optional QR dependencies.

After installation, register Keys NG in the current user's application menu:

```bash
keys-ng desktop install
```

`keys-ng desktop status` checks the integration and `keys-ng desktop uninstall` removes it.

The integration is platform-specific:

- Linux: a freedesktop `.desktop` launcher plus hicolor icon;
- Windows: a Start Menu shortcut;
- macOS: a per-user `~/Applications/Keys NG.app` launcher bundle.

The GUI also attempts this registration automatically on startup.

## 3. Creating a vault

First list available OpenPGP keys:

```bash
keys-ng keys
keys-ng keys --secret
```

Create the vault using full fingerprints:

```bash
keys-ng init ~/vaults/personal \
  --recipient FULL_ENCRYPTION_FINGERPRINT \
  --signer FULL_SIGNING_FINGERPRINT \
  --catalog-privacy standard
```

The vault contains encrypted records, an encrypted catalog, an encrypted folder store, and an inbox directory.

## 4. Starting the interfaces

CLI:

```bash
keys-ng list ~/vaults/personal
```

TUI:

```bash
keys-ng-tui ~/vaults/personal
```

M1.18 gives the TUI full day-to-day editing parity with the GUI. In the tree view:

- `N` creates a new entry in the selected/current folder;
- `Ctrl+D` creates a new folder;
- `E` edits an entry or renames a folder;
- `M` moves an entry or folder;
- `Delete` deletes the selected entry or an empty folder after confirmation;
- `X` exports the selected entry as plaintext KeePass-compatible XML.
- `s` exports the selected entry as a standalone encrypted record; the guided screen selects the recipient public key, optional signing key and output path.

The entry editor supports generic, Web/URL, SSH and RDP records, UUID references in username/password, tags, notes, TOTP URI/secret, TOTP QR image files, SSH X11 forwarding and advanced SSH argv options. Fields that are not applicable to the selected entry type are ignored on save.

GUI with no vault open:

```bash
keys-ng-gui
```

The GUI can open one or more vaults with a native directory chooser. Multiple vaults are shown as vertical tabs. You can also pass vault paths at startup:

```bash
keys-ng-gui ~/vaults/personal ~/vaults/work
```

## 5. Configuration

The configuration file is normally:

```text
~/.config/keys-ng/config.toml
```

On platforms using different conventions, `platformdirs` selects the native user configuration directory.

Example:

```toml
language = "it"

[clipboard]
password_timeout = 20
totp_timeout = 10

[security]
auto_lock_timeout = 300
crypto_backend = "auto"

[ui]
tree_startup_view = "compact"

[ui.tui]
# Empty colors use Textual's theme-aware semantic colors.
clipboard_notice_background = ""
clipboard_notice_foreground = ""
clipboard_notice_seconds = 2.5
recent_vaults = []

[launchers.ssh]
terminal = "auto"
terminal_options = []

[launchers.rdp.linux]
client = "auto"
options = ["/dynamic-resolution", "+clipboard"]

[launchers.rdp.windows]
client = "mstsc"
options = []

[launchers.rdp.macos]
client = "auto"
options = []
```

`tree_startup_view` accepts `expanded` or `compact`.

## 6. Entries and folders

Entries can be organized in arbitrary folder/subfolder trees. The folder names are encrypted; the filesystem only exposes UUID-like record names.

An entry may contain:

- title;
- one or more usernames;
- password;
- TOTP configuration;
- tags and notes;
- custom fields;
- URL, SSH, RDP, or structured command actions.

The GUI entry editor offers `Generic credential`, `Web / URL`, `SSH connection`, and `RDP connection` types.

## 7. Clipboard shortcuts

In the GUI:

```text
Ctrl+U       Copy URL
Ctrl+B       Copy username
Ctrl+C       Copy password
Ctrl+T       Copy TOTP
Ctrl+O       Open the selected URL/SSH/RDP action
Ctrl+Shift+I Copy entry UUID
Ctrl+F       Search
```

Clipboard values are cleared after the configured timeout when Keys NG can verify that the clipboard still contains the value it placed there.

## 8. TOTP

TOTP may be configured by entering:

- the Base32 secret;
- an `otpauth://` URI;
- a QR code from a local image or clipboard in the GUI.

The seed remains inside the encrypted record. The generated code is calculated in memory.

## 9. SSH

SSH entries define host, port, username, X11 forwarding and optional advanced arguments.

X11 forwarding has a dedicated choice:

```text
off
-X
-Y
```

Advanced options may contain arguments such as:

```text
-J bastion.example.org -o ServerAliveInterval=30
-L 8080:localhost:80
-D 1080
```

Keys NG never invokes these through a shell. Options are parsed into an argument list and passed to the SSH client with `shell=False`.

The terminal used to host SSH is configured globally in `config.toml`. Passwords are not placed on the process command line.

## 10. RDP

RDP entries store host, port and username. The client and its command-line options are configured separately for Linux, Windows and macOS in `config.toml`.

Keys NG does not put the stored password on the RDP process command line.

## 11. Reusing credentials by UUID

Keys NG implements the KeePassXC-style UUID reference subset:

```text
username = {REF:U@I:<UUID>}
password = {REF:P@I:<UUID>}
```

Example:

```text
{REF:U@I:033054d4-45c6-48c5-9092-cc1d661b1b71}
{REF:P@I:033054d4-45c6-48c5-9092-cc1d661b1b71}
```

References are resolved when the value is used. Updating the source entry therefore updates every consuming entry immediately. Cycles and missing targets are rejected.

## 12. Search

Search is performed against the encrypted catalog. Once the vault is unlocked, catalog metadata is cached in memory so searches do not repeatedly invoke GnuPG for each record or folder.

The GUI and TUI search fields filter entries globally, independently of their current folder.

## 13. Locking

A normal lock clears Keys NG's decrypted metadata caches for the vault. A hard lock also clears the GnuPG agent authorization cache. Because `gpg-agent` is shared by the user session, hard lock is global in the multi-vault GUI.

## 14. Recent vaults

The GUI keeps the five most recently opened vault paths. They are available under `Vault → Recent` and stored in the user configuration file.

## 15. Public-key-only inbox workflow

A third party can create an encrypted entry without having the vault or your private key:

```bash
keys-ng inbox-create \
  --public-key owner-public.asc \
  --output server-entry.gpg \
  --title "New server" \
  --username admin \
  --ssh-host server.example.org
```

The resulting `.gpg` file can be copied manually into the vault's `inbox/` directory.

Public-key-only items cannot be signed by the vault owner. Therefore unsigned inbox items are rejected by default. The owner may explicitly accept them:

```bash
keys-ng import-inbox ~/vaults/personal --accept-unsigned
```

After validation, the entry is saved again using the vault's normal recipients and signer.

## 16. Importing KeePassXC

Direct KDBX import delegates decryption to `keepassxc-cli`, receiving XML through a pipe:

```bash
keys-ng import-keepassxc Passwords.kdbx ~/vaults/personal
```

An existing XML export can also be imported:

```bash
keys-ng import-keepassxc Passwords.xml ~/vaults/personal --format xml
```

The importer preserves groups as folders, entries, usernames, passwords, URL actions, TOTP, tags, notes and custom string fields. KeePassXC UUID references are preserved or remapped safely if an UUID collision exists in the destination vault.
If a command or unsupported action cannot be represented as a Keys NG action, it is preserved in the Notes field without replacing existing notes. The import report marks the entry as partially imported and lists it for manual review. This behavior is shared by KDBX and XML imports.

## 17. Exporting to KeePassXC XML

### 17.1 One entry from the CLI

```bash
keys-ng export-entry ~/vaults/personal ENTRY_UUID entry.xml
```

For a single-entry export, UUID credential references are resolved so the exported item is self-contained.

### 17.2 One entry from the TUI

Select the entry and press:

```text
E
```

The XML file is written to the current directory with a name derived from the entry title and UUID.

### 17.3 One entry from the GUI

Select the entry and choose:

```text
Entry → Export as KeePassXC XML…
```

A native save dialog selects the destination.

### 17.4 Complete vault

```bash
keys-ng export-vault ~/vaults/personal full-vault.xml
```

The full export preserves the folder hierarchy, entry UUIDs and UUID credential references so KeePassXC can reconstruct shared credentials.

> **Security warning:** KeePass XML is plaintext. It contains passwords, TOTP seeds and other secrets. Protect the file, import it promptly, and remove it securely when no longer needed.

## 18. Legacy Keys migration

The legacy Bash tree can be migrated without sourcing or executing decrypted shell records:

```bash
keys-ng migrate-legacy OLD_KEYROOT ~/vaults/personal --verify
```

Legacy directories become encrypted logical folders.

## 19. Useful maintenance commands

```bash
keys-ng reindex ~/vaults/personal
keys-ng catalog-health ~/vaults/personal
keys-ng doctor
keys-ng desktop status
```

`reindex` rebuilds the encrypted search catalog from the encrypted records. `catalog-health` checks record/catalog/folder consistency.

## 20. Security boundaries to remember

Keys NG protects data at rest and avoids normal plaintext temporary files, but an unlocked endpoint can still expose secrets through memory, clipboard history, screen capture, malware, compromised SSH/RDP clients, or a compromised GnuPG environment.

A password and its TOTP seed stored in the same vault are convenient but no longer independent factors against vault compromise. Use a separate authenticator when strict factor separation is required.


### Installed version

```bash
keys-ng version
keys-ng-tui version
```

The GUI shows the same version under **? → License**.

## M1.16: Preferences and native desktop packages

The GUI now provides **Settings → Preferences…** (`Ctrl+,`) so normal users do
not need to edit `config.toml` manually. The dialog edits the same global file
reported by `keys-ng doctor` and is divided into General, Clipboard, SSH and RDP
pages. Inline help explains every option. Launcher option fields use **one argv
item per line**; they are never interpreted by a shell. For example, Ptyxis can
open SSH sessions in a new tab by configuring the SSH terminal as `ptyxis` and
entering these two terminal options on separate lines:

```text
--tab
--
```

Some settings (language, crypto backend and initial tree layout) are safest to
apply to newly opened vaults or after restarting Keys NG; timeout changes are
used immediately by the running GUI.

Vault keyboard shortcuts shared by GUI and TUI are:

- `Ctrl+L`: lock the current vault;
- `Ctrl+Shift+L`: hard lock (clear the GnuPG agent cache; in the multi-vault GUI
  this is intentionally global);
- `Ctrl+P`: unlock the current vault.

### Recommended desktop installation formats

Keys NG now carries native packaging recipes:

- Linux: Flatpak (`packaging/flatpak/`), based on `io.qt.PySide.BaseApp`;
- Windows: Briefcase MSI;
- macOS: Briefcase `.app` packaged as a DMG;
- Python wheel: retained for developers and advanced installations.

The Flatpak intentionally delegates GnuPG, SSH and RDP commands to the host via
`flatpak-spawn --host`, preserving the user's existing GnuPG keyring/agent,
terminal emulator and remote-desktop clients. This requires the documented
`org.freedesktop.Flatpak` D-Bus permission and should be considered during the
security review.

Run:

```bash
keys-ng doctor
```

to inspect the installed version, Python, GnuPG, optional GUI/TUI/QR modules,
clipboard backend, SSH/RDP tools, application-menu integration and the active
settings path.

## Creating a new vault from the GUI or TUI (M1.19)

The GUI now provides **Vault → New vault…** (`Ctrl+Shift+N`) and a **Create new vault…** button when no vault is open. The wizard selects an empty target directory, an existing OpenPGP encryption recipient, an existing secret signing key, and catalog privacy. Full fingerprints are shown before creation. Keys NG runs an encrypt/decrypt/signature self-test before writing vault files and opens the vault immediately after successful creation.

The TUI can now be started without a vault argument:

```text
keys-ng-tui
```

A keyboard-first new-vault wizard is displayed. Keys NG does not generate OpenPGP key pairs; create/import them with GnuPG/Kleopatra first.

On Windows, M1.19 automatically searches common Gpg4win/GnuPG locations when `gpg.exe` is not on `PATH`. Explicit `gpg` and `gpgconf` paths can be configured in Preferences if needed.

## Diagnostic logging (M1.19.1)

Keys NG has opt-in rotating file diagnostics for troubleshooting GUI, TUI, CLI and GnuPG performance. It is disabled by default. Edit the per-user `config.toml` and add or change:

```toml
[diagnostics]
enabled = true
level = "DEBUG"
log_file = ""
max_bytes = 2000000
backup_count = 3
```

An empty `log_file` selects the platform-specific per-user log directory. Run `keys-ng doctor` to see whether diagnostics are enabled and which path will be used. Restart the application after changing the setting.

The diagnostic stream records application/component startup, GnuPG operation names, discovery method, subprocess duration/return code/byte counts, vault record read/decrypt/parse/binding timings, and GUI selection timing. It intentionally does **not** record passwords, usernames, URLs, TOTP seeds/codes, clipboard contents, decrypted record bodies, GnuPG argument values, fingerprints, record UUIDs or entry titles.

Logs still contain technical metadata such as timestamps, process/thread information, platform/Python version, operation types and timing. Review a log before sharing it publicly. Disable diagnostics again after collecting the required trace unless continuous logging is specifically desired.

On Windows M1.19.1 also starts GnuPG and `gpgconf` helpers with `CREATE_NO_WINDOW`. This prevents the transient console-window flash produced by console-subsystem helper executables while preserving graphical `pinentry`.

## Inbox and trusted signers (M1.19.2)

The Inbox is a write-only collaboration boundary. A colleague may encrypt a credential to the vault owner's public key and optionally sign it with their own key. When a vault is opened, the GUI and TUI count `inbox/*.gpg` without decrypting the files. If pending items exist, the GUI offers to review them immediately and the TUI shows an `Inbox: N pending` notice; the Inbox remains available later from **Vault → Inbox…** or the TUI `I` binding.

Opening the Inbox review explicitly decrypts each selected/pending item for inspection and classifies it as **VALID / TRUSTED**, **VALID SIGNATURE / SIGNER NOT AUTHORIZED**, **UNSIGNED**, **INVALID SIGNATURE**, **CANNOT DECRYPT**, or **MALFORMED ENTRY**. A valid OpenPGP signature is not sufficient by itself: its primary-key fingerprint must also be authorized in this vault's `trusted_signers` list. This per-vault authorization is intentionally independent of GnuPG/Kleopatra ownertrust.

For a valid but unauthorized signer, GUI/TUI can authorize that key for the current vault after displaying the full fingerprint. Trusted signer management is also available independently from the GUI **Trusted signers…** dialog, the TUI `F3` binding, and `keys-ng trust list/add/remove`.

Unsigned items remain rejected by default. The interactive Inbox can import an unsigned item only after an explicit warning that the sender cannot be authenticated. Invalid signatures are not bypassed by unsigned approval.

Successful import parses the external entry, checks UUID collision, writes a normal record encrypted to the vault recipients and signed by the vault signer, updates the encrypted catalog, and only then removes the Inbox source file. On failure the Inbox ciphertext remains in place. Deleting an Inbox item without importing it requires explicit confirmation.

## M1.20 interactive GUI/TUI parity

M1.20 defines an explicit parity contract for ordinary interactive workflows. GUI and TUI both provide vault create/open/close/recent-vault workflows, entry and folder maintenance, Inbox/trusted-signer review, preferences/help, single-entry KeePassXC XML export, complete-vault KeePassXC XML export, KeePassXC KDBX/XML import, note copying, and password generation. Administrative and diagnostic operations such as `doctor`, `reindex`, `catalog-health`, desktop integration and legacy migration remain CLI-oriented by design.

### Notes: copy and paste

Notes are treated as potentially sensitive data. In the GUI the read-only note viewer is selectable and **Copy notes** copies the whole note using the same timed clipboard clearing policy used for passwords/usernames. While editing a note, normal text-widget shortcuts (`Ctrl+C`, `Ctrl+X`, `Ctrl+V`) operate on the selected text instead of triggering the global copy-password action.

In the TUI, the note editor is a Textual `TextArea`; its native copy/paste bindings take precedence while it has focus. Outside the editor, `Ctrl+C` continues to copy the selected entry password. `Ctrl+N` explicitly copies the complete note with timed clipboard clearing.

### Password generator

The entry editors in both GUI and TUI now include **Generate…**. The generator uses `secrets` through the shared `services.passwords.generate_password()` implementation and supports length, uppercase, lowercase, digits, symbols and optional ambiguous characters. Generated values remain in the generator/editor until save; in the TUI, **Copy generated password** copies the candidate temporarily before applying it to the entry so it can be tested on the remote service first.

### Importing KeePassXC KDBX or XML

Both interactive frontends can import into the currently open vault. The source may be a KeePassXC `.kdbx` file or an XML export. KDBX import delegates decoding to `keepassxc-cli`; XML bytes are received through stdout and no intermediate plaintext XML file is created. For interactive KDBX import the optional database password is held only transiently in process memory and sent to `keepassxc-cli` over stdin; it is never placed in argv, environment variables or a file. This password is unrelated to the OpenPGP private-key passphrase, which Keys NG continues to delegate exclusively to GnuPG/gpg-agent/pinentry.

The import dialog/screen supports a key file, `no password` databases and YubiKey parameters, and provides a dry-run/preview summary before writing. Existing import protections remain active: unsafe XML declarations are rejected, UUID collisions are remapped, references are rewritten/validated, and a post-import validation reopens the encrypted records.

Complete-vault and single-entry XML exports contain plaintext credentials. Keys NG warns before/after export and applies restrictive permissions where the platform supports them.

### M1.20.1 TUI Preferences shortcut

In the M1.20.3 TUI, Preferences opens with `F2`. Main bindings no longer use `Ctrl+Shift+<letter>` because many terminals do not distinguish Shift when combined with Ctrl; `Ctrl+I` is also an alias of Tab. Press `?` for the inline command guide.

## M1.20.4 TUI multi-vault switcher

The TUI can keep more than one vault open in the same process. `F5` opens a vault and `F6` opens a recent vault without closing the previously active one. `Ctrl+J` opens **Open vaults**, where an already-open vault can be activated or closed. Each vault keeps its own `Vault` instance, decrypted metadata cache and locked/unlocked state. `Ctrl+L` locks only the active vault; `F9` hard-locks every open vault before clearing the shared GnuPG agent cache. `Ctrl+W` closes only the active vault and activates another remaining open vault when possible.

