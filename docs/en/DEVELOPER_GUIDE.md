# Keys NG Developer Guide

**Code baseline:** `0.1.18.dev1` / M1.18.1  
**Audience:** developers who know Python fundamentals and want to maintain or extend Keys NG.  
**Method:** top-down: architecture first, then workflows, modules, classes and functions.

---

## M1.18 reviewer documentation

For an independent security/code review, this guide should be read together with `CODE_REVIEW_MANUAL.md`, which contains a source-derived entry for every Python class, method, function and nested helper, plus exact source ranges, signatures, direct-call maps and security-effect hints. `THREAT_MODEL.md`, `VAULT_FORMAT_1.0.md`, `SECURITY_REVIEW.md`, `MEMORY_REVIEW.md` and `RELEASE_SECURITY_CHECKLIST.md` define the review scope and known residual risks.


## 1. The one-sentence mental model

Keys NG is a set of three frontends around a common encrypted-vault core:

```text
CLI (argparse) ─┐
TUI (Textual) ──┼──> Vault ──> CryptoBackend ──> GnuPG / gpg-agent
GUI (PySide6) ──┘      │
                       ├── encrypted entries
                       ├── encrypted catalog
                       ├── encrypted folder tree
                       └── services (TOTP, clipboard, launchers, import/export)
```

The frontends must not implement cryptography or data persistence themselves. They collect user intent and delegate to the core.

## M1.18 frontend parity rule

GUI and TUI must not independently encode credential validation. Both construct an `EntryDraft` and call `build_entry_from_draft()` from `services/entry_editor.py`. This is the canonical transformation from editor fields to the domain `Entry`; imported command actions and custom fields that the editors do not expose are preserved on edit. Folder reorganization remains a `Vault` responsibility so cycle and duplicate-name checks are enforced regardless of frontend.

The Textual TUI uses modal screens for entry editing, folder naming, moving and destructive confirmation. Clipboard results are presented by a timed banner; empty color overrides use Textual semantic theme colors, while explicit foreground/background values come from `[ui.tui]`.

## 2. Repository map

```text
src/keys_ng/
├── cli/main.py                 argparse frontend
├── gui/main.py                 PySide6 multi-vault frontend
├── tui/main.py                 Textual frontend
├── crypto/
│   ├── backend.py              crypto interface and result types
│   ├── factory.py              backend selection
│   ├── gpg_process.py          production GnuPG subprocess backend
│   └── gpgme_backend.py        optional/future native backend
├── storage/
│   ├── vault.py                main domain/application service
│   ├── config.py               per-vault config
│   ├── settings.py             global TOML settings
│   ├── atomic.py               atomic ciphertext writes
│   └── inbox.py                write-only inbox workflow
├── services/
│   ├── actions.py              URL/SSH/RDP launchers
│   ├── entry_editor.py         shared GUI/TUI entry draft + validation
│   ├── clipboard.py            clipboard backends
│   ├── clipboard_helper.py     Qt helper process
│   ├── passwords.py            password generation
│   ├── qr.py                   QR/TOTP import
│   ├── references.py           {REF:...} parser/resolver helpers
│   ├── ssh_options.py          SSH argv parser/validator
│   └── totp.py                 RFC 6238 operations
├── migration/
│   ├── legacy_parser.py        safe parser for old Bash records
│   ├── migrator.py             legacy Keys migration
│   ├── keepassxc.py            KeePassXC import
│   └── keepassxc_export.py     KeePassXC-compatible XML export
├── platform/
│   ├── paths.py
│   ├── app_identity.py
│   └── desktop_integration.py
├── i18n/
├── help/
├── resources/
├── models.py
└── errors.py
```

## 3. Data model (`models.py`)

### 3.1 `Entry`

`Entry` is the complete decrypted representation of one credential record. Important fields:

- `id`: RFC-4122 UUID;
- `title`;
- `kind`;
- `usernames`;
- `password`;
- `totp`;
- `actions`;
- `tags`;
- `notes`;
- `custom_fields`;
- `folder_id`;
- revision/timestamps/schema.

`Entry.create()` generates a UUID and builds a new record. `Entry.validate()` enforces schema and validates child objects. `to_bytes()` and `from_bytes()` serialize the decrypted record to/from UTF-8 JSON.

The JSON is not itself the security boundary; it is passed to `CryptoBackend.encrypt()` before being persisted.

### 3.2 `Action`

`Action` describes an operation that can be launched from an entry:

```text
url      -> browser URL
ssh      -> SSH host/port/user and SSH-specific options
rdp      -> RDP host/port/user
command  -> explicit argv list, shell disabled
```

`Action.validate()` rejects shell actions and invalid combinations. SSH options are delegated to `services/ssh_options.py`.

### 3.3 `TotpConfig`

Stores the TOTP seed and parameters (`algorithm`, `digits`, `period`, issuer/account). `validate()` rejects unsupported algorithms, invalid periods and empty secrets.

### 3.4 `Folder`, `FolderStore`, `Catalog`, `CatalogItem`

Folders are logical encrypted objects, not filesystem directories. `FolderStore` validates parent relationships and detects cycles.

`CatalogItem` contains search metadata but not passwords or TOTP seeds. `Catalog` is the encrypted search/index representation cached in memory while unlocked.

## 4. Vault structure on disk

A typical vault is:

```text
vault/
├── config.json
├── catalog.gpg
├── folders.gpg
├── records/
│   ├── <uuid>.gpg
│   └── ...
└── inbox/
```

Only ciphertext record files are stored persistently. `catalog.gpg` and `folders.gpg` are also encrypted.

## 5. `storage/vault.py`: the central class

`Vault` is the most important class in the project. Most frontend operations eventually call it.

### 5.1 Construction

```python
vault = Vault(path, crypto_backend)
```

The constructor resolves the path, loads the per-vault configuration and recovers stale ciphertext temporary files. The vault starts with empty metadata caches.

### 5.2 `Vault.init()`

Creates an empty vault, writes the config, creates `records/` and `inbox/`, and writes encrypted empty folder/catalog objects.

### 5.3 Locking

`lock()` clears decrypted catalog and folder caches. `lock(hard=True)` also calls the crypto backend's hard-lock operation, which clears `gpg-agent` authorization.

`unlock()` reloads the encrypted catalog and folder store. If either fails, the vault remains locked.

### 5.4 Encryption/decryption

Private helper methods centralize:

- encryption to configured recipients;
- optional signing with the configured signer;
- signature verification;
- rejection of untrusted signers.

This is why frontends never call `gpg` directly.

### 5.5 Entry CRUD

The key public operations are conceptually:

```text
save_entry(entry)
get_entry(uuid)
delete_entry(uuid)
list_items()
search(query)
move_entry(uuid, folder_id)
```

`save_entry()` validates the entry, serializes it, encrypts it, writes ciphertext atomically and updates the encrypted catalog.

`get_entry()` decrypts only the requested record. Passwords are therefore not loaded just because a search result is visible.

### 5.6 Search cache

The decrypted catalog is cached in RAM while the vault is unlocked. Search works on that cache. This avoids the old performance failure in which folder metadata was decrypted repeatedly for each result.

The cache is invalidated when metadata changes and destroyed on lock.

### 5.7 Folder methods

Important methods include creating paths, resolving a path, renaming, moving and deleting folders. Folder deletion is only allowed when safe. Folder validation prevents cycles and invalid parents.

### 5.8 Credential references

`resolved_username()`, `resolved_password()` and `resolved_action()` resolve KeePassXC-style UUID references before returning a value to a frontend or launcher.

The supported forms are:

```text
{REF:U@I:<UUID>}
{REF:P@I:<UUID>}
```

Reference resolution follows chains and rejects cycles and missing targets.

## 6. Crypto layer

### 6.1 `CryptoBackend`

`crypto/backend.py` defines the interface used by `Vault`. A backend must implement encryption, decryption and environment/key operations without changing the domain layer.

This interface is also what makes fake crypto possible in unit tests.

### 6.2 `GPGProcessBackend`

The production backend runs GnuPG with an argv list and `shell=False`. Plaintext is exchanged through pipes rather than persistent temporary files.

The private-key passphrase is handled by GnuPG/`gpg-agent`/pinentry; Keys NG does not request or store it.

### 6.3 Fingerprints

Key selection resolves to complete fingerprints. Short IDs and ambiguous user IDs are intentionally avoided for security-sensitive configuration.

## 7. Atomic persistence

`storage/atomic.py` writes new ciphertext to a temporary ciphertext file, flushes it, then replaces the destination atomically. The temporary object contains ciphertext, not credential plaintext.

On startup, stale ciphertext temp files from interrupted operations can be removed safely.

## 8. Global and per-vault configuration

### 8.1 `storage/config.py`

This is the vault-specific configuration: recipients, signer, trusted signers, signature policy and catalog privacy.

### 8.2 `storage/settings.py`

`AppSettings` represents the user-level `config.toml` and includes:

- language;
- clipboard timeouts;
- auto-lock;
- crypto backend choice;
- initial tree mode;
- recent vault list;
- SSH terminal configuration;
- OS-specific RDP client options.

`load()` parses TOML. `save()` writes deterministic TOML and uses `0600` on Unix. `remember_vault()` implements the five-item MRU list.

## 9. TOTP service

`services/totp.py` handles:

- `otpauth://` parsing/building;
- Base32 secret normalization;
- RFC 6238 code generation;
- time remaining in the current period.

The TOTP code is derived when requested and is not persisted.

## 10. Clipboard service

`services/clipboard.py` has platform-aware backends. CLI/TUI prefer native tools where available and can fall back to Qt/terminal mechanisms. GUI uses Qt directly.

Secrets are sent through stdin where an external clipboard helper is used, rather than being included in process arguments.

Automatic clearing checks ownership/current content where possible so it does not erase a later clipboard value belonging to another application.

## 11. Action launcher service

`services/actions.py` transforms a structured `Action` plus user settings into process argv.

### SSH

SSH may be hosted in a configured terminal. Advanced SSH arguments are parsed by `ssh_options.py`, which blocks attempts to redefine dedicated host/user/port/X11 fields through conflicting options.

### RDP

RDP launchers are OS-specific. Configuration selects the client and options for Linux, Windows and macOS.

The launcher does not place stored passwords on the process command line.

## 12. GUI architecture (`gui/main.py`)

The GUI is multi-vault.

```text
QApplication
└── MainWindow
    ├── menu bar + global shortcuts
    └── vertical QTabWidget
        ├── VaultPane -> Vault A
        ├── VaultPane -> Vault B
        └── VaultPane -> Vault C
```

### 12.1 `MainWindow`

Owns application-level functions:

- open/close vault;
- recent-vault menu;
- multi-vault tabs;
- global hard-lock;
- Help dialog;
- global shortcut dispatch.

Shortcuts are dispatched only to the active `VaultPane`.

### 12.2 `VaultPane`

Owns the UI state for one vault:

- search field;
- folder/entry tree;
- selected entry;
- detail panel;
- timers;
- lock state;
- CRUD operations;
- copy/open/export operations.

### 12.3 `EntryDialog`

Builds or edits an `Entry`. The action type determines which input fields are visible. Its `build_entry()` method is the boundary where GUI widget values are converted into a validated domain object.

### 12.4 KeePassXC single-entry export

`VaultPane.export_entry_keepassxc()` opens a native save dialog, calls `export_entry_xml()` and writes the plaintext export using `write_export()`.

## 13. TUI architecture (`tui/main.py`)

The Textual `KeysApp` owns one `Vault`. The tree contains folders and entries. Search rebuilds the visual tree using the cached catalog.

Bindings call action methods such as copy username/password/TOTP, open action, lock and export.

The `E` binding exports the selected entry to the current working directory.

## 14. CLI architecture (`cli/main.py`)

`build_parser()` declares every public CLI command. `run()` dispatches the parsed namespace.

A useful modification rule is:

1. add the parser branch;
2. add the domain/service implementation outside the CLI if it is reusable;
3. add a small dispatch branch in `run()`;
4. add tests for the reusable layer and the CLI surface.

M1.15 export commands are:

```text
export-entry VAULT ENTRY_ID OUTPUT
export-vault VAULT OUTPUT
```

## 15. KeePassXC import

`migration/keepassxc.py` can read XML directly or call `keepassxc-cli export --format xml` for KDBX.

The importer is deliberately two-pass:

1. parse groups and entries and collect source UUIDs;
2. allocate destination UUIDs, remap collisions, rewrite references;
3. validate reference graphs;
4. only then write folders and encrypted entries;
5. re-read and validate runtime resolution after writing.

This prevents a half-successful import with broken UUID references.

## 16. KeePassXC export (`migration/keepassxc_export.py`)

This module is the inverse interoperability layer.

### `_keepass_uuid()`

KeePass XML represents UUID values as Base64-encoded 16-byte UUIDs. This helper converts Keys NG's RFC-4122 string representation.

### `_reference_to_keepass()`

Transforms Keys NG canonical UUID references into KeePassXC's 32-hex UUID form.

### `_entry_xml()`

Builds one KeePass `<Entry>` node, including standard strings, TOTP, tags, custom fields and selected Keys NG action metadata.

### `export_entry_xml()`

Creates a standalone XML document for one entry. References are resolved because their target entries are not exported.

### `export_vault_xml()`

Creates the folder hierarchy, preserves entry UUIDs and keeps UUID references so shared credentials remain shared after import into KeePassXC.

### `write_export()`

Writes plaintext XML and applies mode `0600` on Unix. This function exists to keep the plaintext-export warning boundary explicit.

## 17. Legacy Keys migration

The old Bash format is never executed with `source`. `legacy_parser.py` accepts only the known assignment structure and rejects shell constructs. `migrator.py` decrypts one record in memory, parses it, creates a new `Entry`, encrypts it and moves on.

## 18. Inbox workflow

`storage/inbox.py` supports two distinct roles:

- owner: imports an inbox file into a normal signed vault record;
- external contributor: creates a ciphertext using only the owner's public key.

Public-key-only files are unsigned by definition. The importer therefore rejects them unless the owner explicitly opts into `--accept-unsigned`.

## 19. Internationalization

All user-facing frontend strings should pass through gettext `_()`. Translation sources live in `.po` files and compiled `.mo` files ship with the package.

Do not translate JSON keys, command names, configuration keys or stable machine identifiers.

## 20. Application-menu integration

`platform/desktop_integration.py` installs a per-user launcher:

```text
Linux   -> XDG applications .desktop + hicolor icon
Windows -> Start Menu .lnk via PowerShell/WScript.Shell
macOS   -> ~/Applications/Keys NG.app launcher bundle
```

`ensure_user_desktop_integration()` is best effort and must never prevent the password manager from opening. Explicit CLI commands surface errors.

## 21. Security invariants when modifying code

Before merging a change, verify that it does not:

1. write decrypted credentials to persistent temporary files;
2. put passwords/TOTP seeds in argv or environment variables;
3. log secret values;
4. use `shell=True` for user-controlled action input;
5. silently accept untrusted/unsigned encrypted objects;
6. accidentally keep decrypted record objects in global caches;
7. make a plaintext XML export appear encrypted;
8. bypass UUID-reference cycle validation;
9. expose logical folder names in record filenames.

## 22. Tests

Most tests use a `FakeCrypto` implementation that prepends `ENC:`. This does not test cryptographic security; it isolates domain logic so tests can verify persistence, references, folders, imports/exports and frontend wiring quickly.

Real GnuPG smoke tests should use a temporary `GNUPGHOME`, never the developer's normal keyring.

## 23. Common modification recipes

### Add a new entry field

1. extend `Entry` in `models.py`;
2. add validation and backwards-compatible `from_bytes()` defaults;
3. update GUI/TUI/CLI input/output as needed;
4. decide whether it belongs in `CatalogItem`;
5. update KeePassXC import/export if interoperable;
6. add tests.

### Add a new action type

1. extend `Action.validate()`;
2. implement launching in `services/actions.py`;
3. add GUI editor controls;
4. add CLI arguments;
5. add TUI display/open behavior;
6. decide how to map it to KeePassXC XML;
7. add platform-specific tests.

### Add a new configuration option

1. add a field to `AppSettings`;
2. parse it in `load()`;
3. emit it in `save()`;
4. add it to `config.example.toml`;
5. consume it only in the relevant service;
6. document and test it.

### Change search behavior

Work in `Vault.search()` and catalog construction first. Do not solve search performance by decrypting all records in a frontend.

### Change cryptography

Implement or modify a `CryptoBackend`. Keep the `Vault` API stable and test compatibility separately. Never embed passphrase prompting in the GUI/CLI core.

## 24. Build and packaging

`pyproject.toml` defines:

- core dependency: `platformdirs`;
- optional GUI/TUI/QR/i18n/dev extras;
- console scripts `keys-ng`, `keys-ng-gui`, `keys-ng-tui`;
- package data for translations, help and application resources.

A wheel is the installable Python distribution artifact. Source archives are preferable for development; wheels are useful for testing the exact package delivered to users.

## 25. Final dependency direction

Keep this direction in mind:

```text
frontend
   ↓
Vault / reusable services
   ↓
models + storage + crypto abstraction
   ↓
OS / GnuPG / Qt / Textual adapters
```

Avoid dependencies in the reverse direction. In particular, `models.py` and `Vault` should not depend on GUI or TUI widgets. This is what keeps Keys NG testable, multi-platform and maintainable.

## M1.16 distribution and preferences architecture

M1.16 adds three distribution layers without changing the vault format. Native
package recipes live under `packaging/`, while the application remains a normal
Python package. Windows and macOS use Briefcase; Linux uses the Flathub
`io.qt.PySide.BaseApp` so Qt/PySide does not have to be rebuilt by the project.
The Flatpak backend is special: `keys_ng.platform.host` detects the sandbox and
prefixes external GnuPG/SSH/RDP argv with `flatpak-spawn --host`. No shell is
introduced. Desktop self-registration is disabled inside Flatpak because the
Flatpak export already owns the application desktop ID.

`keys_ng.services.doctor.collect_doctor_checks()` centralizes runtime diagnostics
and deliberately distinguishes required failures from optional capability
warnings.

The global preferences dialog lives in `keys_ng.gui.main.SettingsDialog`. It
edits the existing `AppSettings` object and calls `AppSettings.save()`, so the
GUI and manual TOML editing remain two interfaces over exactly the same model.
List-valued launcher options are edited one argv item per line and are stored as
TOML arrays. No command-line parser or shell tokenizer is involved.

GUI shortcuts are owned by `MainWindow` and dispatched only to the active `VaultPane`. TUI bindings must remain terminal-portable: `Ctrl+L` locks, `Ctrl+P` unlocks, and `F9` performs the hard lock. In the GUI, `Ctrl+Shift+L` continues to map to `MainWindow.hard_lock_all()` because `gpg-agent` is a session-wide resource.

## M1.19 Windows MSI build procedure

The end-to-end Windows/Briefcase release procedure, including Git for Windows, PEP 639 license metadata, GUI/CLI/TUI packaging, Gpg4win runtime testing, cleanup and troubleshooting, is documented in [`WINDOWS_MSI_BUILD.md`](WINDOWS_MSI_BUILD.md). Release maintainers should follow that document rather than reconstructing the commands from CI configuration.

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

## M1.19.2 Inbox authorization model

`GnuPG ownertrust` and `VaultConfig.trusted_signers` are deliberately independent. GnuPG establishes whether a signature is cryptographically valid; Keys NG then asks whether the primary signing identity is authorized to submit records to this specific vault. `services/trusted_signers.py` is the only supported mutation path for this allowlist. It validates a full fingerprint against the local public keyring, rejects revoked/expired/non-signing keys, persists `vault.json`, and prevents removal of the configured vault signer.

`storage/inbox.py` separates scanning, inspection and mutation. `pending_inbox_paths()` performs ciphertext-only counting. `inspect_inbox_item()` decrypts and classifies without changing vault state. `import_inbox_item()` accepts only a valid+authorized signature unless explicit unsigned approval is supplied; it then delegates normal storage to `Vault.save_entry()` so destination encryption/signature/catalog rules are identical to locally created records. Source deletion happens only after successful storage.

The GnuPG backend records both the signing-key fingerprint and the optional primary-key fingerprint from `VALIDSIG`. Vault authorization uses the primary fingerprint when available, allowing signing-subkey rotation without adding each subkey to the allowlist.

## Textual lifecycle rule (M1.19.3)

TUI `Screen`, `ModalScreen`, and `Widget` subclasses must not reuse framework lifecycle/API method names such as `refresh` for application-level data reloads. Textual may call `Widget.refresh()` before `compose()` children are mounted. Use explicit names such as `refresh_inbox()` or `refresh_signers()` for data/UI repopulation and invoke them from `on_mount()` or controlled event handlers.

## M1.20 interactive parity contract

`keys_ng.services.ui_capabilities` declares the ordinary user-facing capabilities that must be reachable from both GUI and TUI. The parity regression test compares the declared sets and also checks for the M1.20 workflow hooks in both frontend source files. CLI-only administrative/diagnostic commands are deliberately excluded from this contract.

The shared KeePassXC importer now accepts an optional transient `password` argument for interactive frontends. When supplied, it is encoded only for stdin to `keepassxc-cli`; it must never be copied into argv, environment variables, logs or a temporary XML file. CLI callers may continue to omit it and allow `keepassxc-cli` to own the terminal prompt. Common Windows/macOS KeePassXC installation paths are checked when `keepassxc-cli` is not on `PATH`.

GUI `Ctrl+C` is context-aware: selected text in `QLineEdit`/`QTextEdit` is copied normally; otherwise the shortcut retains the historic copy-password behavior. The TUI global copy-password binding is deliberately non-priority so a focused Textual `TextArea` may consume its native copy/paste key bindings. The explicit whole-note action uses the timed secret-clipboard service.

Password generation remains centralized in `services.passwords.generate_password()`. Frontends collect policy choices only; they must not implement their own RNG or password alphabet.

## M1.20.1 Textual binding compatibility

Textual treats comma in a `Binding` key specification as a separator between alternative keys. Do not use a literal shortcut such as `ctrl+,`: it is parsed as an empty alternate binding and may raise `InvalidBinding` while the application class is created. Keys NG uses `Ctrl+Shift+P` for TUI Preferences. Regression tests reject binding keys ending in a literal comma.

## PySide6 and gettext `_` name-shadowing rule (M1.20.2)

`keys_ng.gui.main` imports gettext as `_`. Do not use `_` as a throw-away assignment target inside any function that also calls `_()`. Python treats the assigned name as local for the entire function, so constructs such as `path, _ = QFileDialog.getOpenFileName(..., _("Title"), ...)` raise `UnboundLocalError`. Use a descriptive unused name such as `selected_filter` instead. A regression test enforces this rule.

## M1.20.4 TUI multi-vault session model

`services.vault_sessions.VaultSessionManager` owns the set of open TUI `Vault` objects and the active-path pointer. Opening a vault adds/reuses an object instead of terminating and restarting the Textual app. Switching changes the active `vault` closure reference and refreshes the tree/detail widgets. A locked vault is not decrypted merely by switching to it. Normal lock is per-vault; hard lock first locks every open vault (clearing every decrypted cache) and only then calls the shared crypto backend's `hard_lock()` once. Closing a vault locks it before removing it from the session.

