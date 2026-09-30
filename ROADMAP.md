# Keys NG roadmap

> **Current implementation status (0.1.21):** M1.21 is implemented and released. The project remains in M1 (hardened usable alpha); M2 beta work is limited to packaging/validation and has not yet been completed.

## M0 - Foundation (complete)

- [x] Python package layout
- [x] versioned JSON entry model
- [x] independent encrypted records
- [x] encrypted rebuildable catalog
- [x] GnuPG process backend using pipes
- [x] optional signing and trusted signer verification
- [x] password generator
- [x] RFC 6238 TOTP generator and `otpauth://` import
- [x] basic CLI
- [x] basic PySide6 GUI
- [x] gettext `.po/.mo` structure
- [x] strict Keys 1.0.1 legacy parser/migrator
- [x] unit tests and real-GPG smoke test

## M1 - Hardened usable alpha (in progress)

- [ ] GPGME backend with safe fallback to `gpg` (factory/fallback complete; native GPGME adapter deliberately gated until cross-platform packaging is validated)
- [x] key discovery/selection by full fingerprint
- [x] explicit vault lock / hard lock semantics
- [x] verified native clipboard backends for CLI/TUI (Wayland/X11/macOS/Windows) with Qt and Textual terminal fallbacks
- [x] clipboard sensitive-data hint where supported (KDE hint; further platform-specific hints remain for M2 testing)
- [x] create/edit/delete flows in GUI
- [x] TOTP QR import from local image/clipboard (optional ZXing-C++ backend)
- [x] configurable catalog privacy levels (`minimal`, `standard`, `full`)
- [x] structured URL/SSH/RDP actions
- [x] safe write-only inbox import workflow
- [x] catalog consistency checks and interrupted ciphertext-write cleanup tests
- [x] migration verification mode
- [x] TOML application settings and platformdirs integration
- [x] encrypted logical folder/subfolder model with independent `folders.gpg` primary store
- [x] folder-aware search and CLI folder management
- [x] GUI tree view with drag-and-drop moves, folder CRUD, and type-specific icons for folder/web/SSH/RDP/command entries
- [x] optional Textual TUI with tree navigation, cached search and priority secret-copy shortcuts
- [x] legacy directory hierarchy migration into logical folders
- [x] KeePassXC import bridge: native KDBX via `keepassxc-cli` XML stdout, plus direct XML export import
- [x] KeePassXC two-pass UUID preservation/remapping and cross-reference validation
- [x] unlocked-session catalog/folder RAM cache eliminating repeated GPG decryptions during search
- [x] GUI `Ctrl+F` search, `Ctrl+O` Open shortcut, application menus, and localized offline README/security/license help
- [x] clipboard helper read-back verification before CLI/TUI copy success acknowledgement
- [ ] cross-platform manual/CI validation of GUI, clipboard, QR and native launchers

## M2 - Cross-platform beta

- [ ] native packaging for Linux
- [ ] signed Windows installer
- [ ] signed/notarized macOS app
- [ ] CI integration tests on Linux/Windows/macOS
- [ ] smartcard/YubiKey test matrix
- [ ] cloud conflict detection/reconciliation
- [ ] rollback detection design
- [ ] localization QA / pseudo-locale / RTL layout tests

## M3 - Stable security release

- [ ] threat model review
- [ ] external security audit
- [ ] fuzzing of JSON, catalog, URI and legacy parsers
- [ ] reproducible release procedure
- [ ] migration guide from classic Keys
- [x] complete user/admin documentation

## M1.8.1 — GNOME/Wayland desktop identity fix (complete)

- [x] Match Qt `desktopFileName` to `org.keysng.KeysNG.desktop`.
- [x] Install per-user freedesktop desktop entry and hicolor icon.
- [x] Add `keys-ng desktop install|status|uninstall`.
- [x] Preserve bundled legacy icon as the single source asset.

## M1.9 - GUI remote entry types and launchers

- [x] GUI selector for Generic/Web/SSH/RDP entries
- [x] Dynamic URL vs Host/Port fields
- [x] Configurable SSH terminal and argv options
- [x] Per-OS RDP client and argv options
- [x] Launcher tests with `shell=False`


## M1.10 - Per-entry advanced SSH

- [x] Per-entry X11 forwarding selector (`off`, `-X`, `-Y`)
- [x] Free-form advanced SSH argv field with safe tokenization
- [x] JumpHost (`-J`) and tunnel options (`-L`, `-R`, `-D`) support
- [x] Dedicated-field protection for username, port and X11 forwarding
- [x] CLI flags `--ssh-x11` and `--ssh-options`


## M1.11 - Multi-vault GUI

- [x] GUI can start with no vault path
- [x] Native directory chooser for opening vaults
- [x] Multiple simultaneously open vaults in vertical tabs
- [x] Per-tab vault/search/tree/selection/TOTP/auto-lock state
- [x] Active-tab dispatch for GUI menus and keyboard shortcuts
- [x] Duplicate-open detection and full-path tab tooltips
- [x] Per-tab normal lock and global hard-lock semantics for shared `gpg-agent`

## M1.12 - Reusable credentials by UUID

- [x] KeePassXC-compatible `{REF:U@I:<UUID>}` username references
- [x] KeePassXC-compatible `{REF:P@I:<UUID>}` password references
- [x] Canonical and 32-hex UUID parsing
- [x] Recursive resolution with cycle and missing-target detection
- [x] Runtime resolution for clipboard and SSH/RDP launchers
- [x] UUID display/copy in GUI and TUI
- [x] Italian gettext/help updates and reference documentation

## M1.14 - Recent vaults and public-key-only inbox workflow (complete)

- [x] GUI `Vault > Recent` with the five most recently opened vaults.
- [x] Persistent recent-vault paths in `[ui].recent_vaults`.
- [x] Standalone `keys-ng inbox-create` command requiring no vault access.
- [x] `--public-key FILE` isolated temporary GnuPG keyring mode.
- [x] Explicit `import-inbox --accept-unsigned` approval for public-key-only deposits.
- [x] Inbox records are re-encrypted/signed under normal vault policy after approval.

## M1.15 - Application menu, consolidated documentation, KeePassXC XML export (complete)

- [x] Per-user application-menu launcher on Linux, Windows and macOS.
- [x] Documentation consolidated into user/developer guides under `docs/en` and `docs/it`.
- [x] KeePassXC-compatible single-entry XML export in CLI/TUI/GUI.
- [x] KeePassXC-compatible complete-vault XML export in CLI, preserving folder hierarchy, UUIDs and UUID references.


## M1.15.1 — launcher/version maintenance (complete)

- [x] Linux `.desktop` launchers no longer contain `TryExec`, improving GNOME/GIO compatibility.
- [x] `keys-ng version` and `keys-ng-tui version` expose the installed package version.
- [x] GUI License help shows the installed Keys NG version dynamically.

## M1.16 — Distribution and GUI preferences

- [x] GUI editor for global `config.toml` with inline tips
- [x] GUI/TUI `Ctrl+L`, `Ctrl+Shift+L`, `Ctrl+P`
- [x] expanded `keys-ng doctor`
- [x] Linux Flatpak manifest using `io.qt.PySide.BaseApp`
- [x] Flatpak host delegation for GnuPG/SSH/RDP
- [x] Briefcase Windows MSI recipe
- [x] Briefcase macOS `.app` / DMG recipe
- [x] cross-platform distribution CI workflow
- [ ] sign/notarize production Windows/macOS artifacts with release certificates
- [ ] run final Flatpak/Windows/macOS packages on clean target machines

## M1.17 — Security consolidation and reviewer documentation

- [x] vault format 1.0 frozen/documented for the review cycle
- [x] bilingual formal threat model
- [x] internal security review with explicit fixed findings/residual risks
- [x] single-record rollback/replacement detection bound to signed catalog hash/revision
- [x] fail-closed payload UUID / filename UUID binding
- [x] private POSIX vault directory permissions (`0700`)
- [x] signature-policy consistency checks
- [x] strict 40/64-hex full fingerprint syntax in the GnuPG process backend
- [x] atomic-write fault-injection regression test
- [x] deterministic malformed-input parser stress tests
- [x] dependency-free AST security check
- [x] memory/secret-lifetime review
- [x] exhaustive bilingual code-review manual covering every Python class/function
- [x] automatic test preventing undocumented Python symbols
- [ ] independent external code/security audit
- [ ] connected-environment Ruff/Bandit/Semgrep/pip-audit execution
- [ ] hardware-token and clean Windows/macOS package validation

## M1.18 — TUI feature parity and usability

- [x] frontend-neutral entry draft/build service shared by GUI and TUI
- [x] full TUI entry creation and editing for generic, URL, SSH and RDP credentials
- [x] TUI username/password UUID references, tags, notes, TOTP URI/secret and QR-file import
- [x] TUI SSH X11 forwarding and advanced argv options
- [x] TUI folder create/rename/delete
- [x] TUI entry/folder move workflow with cycle-safe validation
- [x] rejected folder moves/renames no longer mutate the in-memory folder cache
- [x] duplicate sibling-folder names rejected during move
- [x] high-visibility timed clipboard result banner with success/warning/error states
- [x] user-configurable TUI clipboard banner foreground/background/duration with theme-based automatic defaults
- [x] context-sensitive command hint bar
- [x] bilingual documentation and regenerated exhaustive code-review manuals
- [x] regression tests for shared editor behavior, folder reorganization and TUI parity

## M1.20 — Interactive UI Parity & KeePassXC Import (complete)

- [x] GUI/TUI interactive capability parity.
- [x] KeePassXC KDBX/XML import from both interactive frontends.
- [x] Full-vault and single-entry XML export.
- [x] Note copy/paste improvements and integrated password generator.
- [x] TUI vault/open/recent/preferences/help workflows.

### M1.20.1 — TUI Preferences binding hotfix (complete)

- [x] Replaced the invalid Textual `ctrl+,` Preferences binding with `Ctrl+Shift+P`.
- [x] Added regression coverage for literal-comma binding keys.

### M1.20.2 — TUI terminal-portable shortcuts (complete)

- [x] Replaced terminal-fragile `Ctrl+Shift+<letter>` main commands with F-key bindings.
- [x] Added `F2` Preferences, `F3` Trusted signers, `F5` Open vault, `F6` Recent vault, `F7` KeePassXC import, `F8` complete-vault XML export and `F9` hard lock.
- [x] Added `Ctrl+N` Notes copy, `Ctrl+D` folder creation and `?` inline command guide.

### M1.20.3 — TUI keyboard and lock semantics (complete)

- [x] Completed terminal-portable shortcut and lock behavior regression coverage.

### M1.20.4 — TUI multi-vault switching (complete)

- [x] Multiple vaults remain open in one TUI session.
- [x] `Ctrl+J` opens the vault switcher; `Ctrl+W` closes only the active vault.
- [x] `Ctrl+L` locks only the active vault; `F9` hard-locks all vaults and the shared GnuPG agent.
- [x] Vault switching uses the temporary notification banner.

### M1.21 — RDP credentials and TUI notification fixes (complete, released as 0.1.21)

- [x] Linux RDP passes the password through stdin using `/from-stdin:force`; passwords are not placed in process arguments.
- [x] RDP entries expose an optional domain field in GUI and TUI.
- [x] Linux RDP options remain separate argv items and are configurable per item.
- [x] Vault-switch notifications use the temporary banner instead of permanent status text.
- [x] TUI clipboard notifications are acknowledged immediately after a successful clipboard write.
- [x] Release workflow builds and smoke-tests the wheel; release `v0.1.21` is published.
