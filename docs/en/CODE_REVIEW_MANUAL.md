# Keys NG M1.20.4 — Complete Code Review Manual

Version: `0.1.20.dev4`. This document is generated from the exact Python source tree shipped with M1.20.4.

## Purpose and reading method

This manual is a reviewer-oriented map, not a substitute for reading the source. It documents every Python class and function (including nested helpers) with its signature, source range, direct calls, explicit exceptions, state writes, control-flow shape and security-relevant effects. Stable `symbol:` markers are machine-checked by the test suite so undocumented executable symbols cannot silently enter the release.

## Architecture and trust boundaries

- `models` contains validated plaintext domain objects. Plaintext exists in Python memory only while needed.
- `storage.vault` is the central policy boundary. It encrypts before persistence, verifies signatures after decryption, binds records to the signed catalog, and clears decrypted metadata caches on lock.
- `crypto` delegates private-key passphrase handling to GnuPG/gpg-agent/pinentry; Keys NG never requests that passphrase.
- Persistent credential data is per-record OpenPGP ciphertext. `catalog.gpg` and `folders.gpg` are also encrypted and signed. `vault.json` is intentionally cleartext policy metadata and must not contain credentials.
- External actions are argv-based and use `shell=False`. Advanced SSH options remain a trusted-record boundary because OpenSSH itself can execute commands through options such as ProxyCommand/LocalCommand.
- The encrypted catalog detects single-record replacement/rollback through ciphertext SHA-256 plus revision. Coordinated rollback of both record and catalog remains a documented residual risk.

## Primary execution flows

```text
CLI/TUI/GUI -> Vault -> CryptoBackend -> GnuPG -> gpg-agent/pinentry
                    |
                    +-> records/<uuid>.gpg
                    +-> catalog.gpg
                    +-> folders.gpg
public-key contributor -> inbox/<random>.gpg -> explicit import -> Vault.save_entry()
```

## Module-by-module exhaustive reference

### `keys_ng.__main__`

Source module.

**Source:** `src/keys_ng/__main__.py`  
**Executable symbols:** 0

**Direct module dependencies:** `keys_ng.gui.main`

### `keys_ng.cli.main`

Command-line parser and dispatcher for all CLI workflows.

**Source:** `src/keys_ng/cli/main.py`  
**Executable symbols:** 7

**Direct module dependencies:** `__future__`, `argparse`, `getpass`, `keys_ng`, `keys_ng.crypto.factory`, `keys_ng.crypto.gpg_process`, `keys_ng.errors`, `keys_ng.i18n`, `keys_ng.migration.keepassxc`, `keys_ng.migration.keepassxc_export`, `keys_ng.migration.migrator`, `keys_ng.models`, `keys_ng.platform.desktop_integration`, `keys_ng.services.actions`, `keys_ng.services.clipboard`, `keys_ng.services.diagnostics`, `keys_ng.services.doctor`, `keys_ng.services.passwords`, `keys_ng.services.qr`, `keys_ng.services.ssh_options`, `keys_ng.services.totp`, `keys_ng.services.trusted_signers`, `keys_ng.services.vault_init`, `keys_ng.storage.inbox`, `keys_ng.storage.settings`, `keys_ng.storage.vault`, `os`, `pathlib`, `sys`, `tempfile`, `time`

<!-- symbol:keys_ng.cli.main:_settings -->
#### `_settings`

**Kind:** function/method  
**Lines:** 40-41  
**Signature:** `def _settings() -> AppSettings`  
**Purpose:** Internal helper implementing `_settings`.

**Direct calls observed in the function body:** `AppSettings.load`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.cli.main:_crypto -->
#### `_crypto`

**Kind:** function/method  
**Lines:** 44-46  
**Signature:** `def _crypto()`  
**Purpose:** Internal helper implementing `_crypto`.

**Direct calls observed in the function body:** `_settings`, `create_crypto_backend`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.cli.main:_vault -->
#### `_vault`

**Kind:** function/method  
**Lines:** 49-50  
**Signature:** `def _vault(path: str) -> Vault`  
**Purpose:** Internal helper implementing `_vault`.

**Direct calls observed in the function body:** `Vault`, `_crypto`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.cli.main:_print_items -->
#### `_print_items`

**Kind:** function/method  
**Lines:** 53-56  
**Signature:** `def _print_items(items) -> None`  
**Purpose:** Internal helper implementing `_print_items`.

**Direct calls observed in the function body:** `join`, `print`.

**Control-flow shape:** 0 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.cli.main:build_parser -->
#### `build_parser`

**Kind:** function/method  
**Lines:** 59-238  
**Signature:** `def build_parser() -> argparse.ArgumentParser`  
**Purpose:** Builds `build_parser`.

**Direct calls observed in the function body:** `action.add_argument`, `add.add_argument`, `argparse.ArgumentParser`, `delete.add_argument`, `deposit.add_argument`, `desktop.add_subparsers`, `desktop_sub.add_parser`, `edit.add_argument`, `export_entry.add_argument`, `export_vault.add_argument`, `folder.add_subparsers`, `folder_create.add_argument`, `folder_delete.add_argument`, `folder_list.add_argument`, `folder_move.add_argument`, `folder_rename.add_argument`, `folder_sub.add_parser`, `gen.add_argument`, `health.add_argument`, `inbox.add_argument`, `init.add_argument`, `keys.add_argument`, `kp.add_argument`, `lock.add_argument`, `ls.add_argument`, `migrate.add_argument`, `move.add_argument`, `otp.add_argument`, `p.add_argument`, `p.add_subparsers`, `password.add_argument`, `reindex.add_argument`, `search.add_argument`, `show.add_argument`, `sub.add_parser`, `trust.add_subparsers`, `trust_add.add_argument`, `trust_list.add_argument`, `trust_remove.add_argument`, `trust_sub.add_parser`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.cli.main:run -->
#### `run`

**Kind:** function/method  
**Lines:** 241-530  
**Signature:** `def run(args: argparse.Namespace) -> int`  
**Purpose:** Implements the `run` operation in this module.

**Direct calls observed in the function body:** `Action`, `Entry.create`, `GPGProcessBackend`, `KeysNGError`, `Path`, `Vault`, `VaultInitRequest`, `_`, `_crypto`, `_print_items`, `_settings`, `actions.append`, `add_trusted_signer`, `args.folder.strip`, `args.parent.strip`, `collect_doctor_checks`, `copy_secret_cli`, `create_vault`, `crypto.hard_lock`, `crypto.list_keys`, `deposit_crypto.import_public_key`, `deposit_crypto.resolve_fingerprint`, `desktop_integration_status`, `dict.fromkeys`, `entry.actions.insert`, `expanduser`, `export_entry_xml`, `export_vault_xml`, `flags.append`, `format`, `generate_password`, `generate_totp`, `getpass`, `import_inbox`, `import_keepassxc`, `imported.extend`, `input`, `install_user_desktop_integration`, `join`, `launch_action`, `len`, `list`, `list_trusted_signers`, `migrate_legacy_tree`, `next`, `os.chmod`, `parse_otpauth_uri`, `parse_ssh_options`, `parse_totp_qr_file`, `print`, `read_bytes`, `remove_trusted_signer`, `strip`, `tempfile.TemporaryDirectory`, `temporary_home.cleanup`, `time.sleep`, `totp.append`, `tuple`, `uninstall_user_desktop_integration`, `vault.catalog_health`, `vault.create_folder_path`, `vault.delete_entry`, `vault.delete_folder`, `vault.folder_path`, `vault.get_entry`, `vault.list_folders`, `vault.list_items`, `vault.move_entry`, `vault.move_folder`, `vault.reindex`, `vault.rename_folder`, `vault.resolve_folder_path`, `vault.resolved_action`, `vault.resolved_password`, `vault.save_entry`, `vault.search`, `write_encrypted_entry`, `write_export`.

**Explicitly raised exceptions:** `KeysNGError`.

**Object attributes written:** `action.username`, `entry.actions`, `entry.folder_id`, `entry.revision`, `entry.title`, `entry.usernames`, `ssh_action.ssh_options`, `ssh_action.ssh_x11_forwarding`.

**Control-flow shape:** 79 conditional blocks, 11 loops, 3 try blocks, 0 context managers, 22 explicit returns.

**Security-relevant effect categories:** filesystem, cryptography/key-agent.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.cli.main:main -->
#### `main`

**Kind:** function/method  
**Lines:** 533-544  
**Signature:** `def main() -> None`  
**Purpose:** Implements the `main` operation in this module.

**Direct calls observed in the function body:** `SystemExit`, `_settings`, `build_parser`, `configure_diagnostics`, `configure_language`, `get_logger`, `info`, `parser.parse_args`, `print`, `run`.

**Explicitly raised exceptions:** `SystemExit`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.crypto.backend`

Cryptographic backend contracts and immutable result/key records.

**Source:** `src/keys_ng/crypto/backend.py`  
**Executable symbols:** 11

**Direct module dependencies:** `__future__`, `abc`, `dataclasses`

<!-- symbol:keys_ng.crypto.backend:DecryptionResult -->
#### `DecryptionResult`

**Kind:** class  
**Lines:** 8-12  
**Declared fields:** `plaintext`, `signer_fingerprint`, `signature_valid`, `primary_signer_fingerprint`  
**Responsibility:** Implements the `DecryptionResult` operation in this module.

<!-- symbol:keys_ng.crypto.backend:KeyInfo -->
#### `KeyInfo`

**Kind:** class  
**Lines:** 16-28  
**Declared fields:** `fingerprint`, `user_ids`, `can_encrypt`, `can_sign`, `secret`, `revoked`, `expired`  
**Methods:** `label`  
**Responsibility:** Implements the `KeyInfo` operation in this module.

<!-- symbol:keys_ng.crypto.backend:KeyInfo.label -->
#### `KeyInfo.label`

**Kind:** function/method  
**Lines:** 26-28  
**Signature:** `def label(self) -> str`  
**Purpose:** Implements the `label` operation in this module.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.crypto.backend:CryptoBackend -->
#### `CryptoBackend`

**Kind:** class  
**Lines:** 31-62  
**Bases:** `ABC`  
**Methods:** `encrypt`, `decrypt`, `diagnose`, `list_keys`, `resolve_fingerprint`, `import_public_key`, `hard_lock`  
**Responsibility:** Abstract interface isolating vault logic from crypto implementation.

<!-- symbol:keys_ng.crypto.backend:CryptoBackend.encrypt -->
#### `CryptoBackend.encrypt`

**Kind:** function/method  
**Lines:** 33-34  
**Signature:** `def encrypt(self, plaintext: bytes, recipients: list[str], signer: str | None=None) -> bytes`  
**Purpose:** Implements the `encrypt` operation in this module.

**Explicitly raised exceptions:** `NotImplementedError`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.crypto.backend:CryptoBackend.decrypt -->
#### `CryptoBackend.decrypt`

**Kind:** function/method  
**Lines:** 37-38  
**Signature:** `def decrypt(self, ciphertext: bytes) -> DecryptionResult`  
**Purpose:** Implements the `decrypt` operation in this module.

**Explicitly raised exceptions:** `NotImplementedError`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.crypto.backend:CryptoBackend.diagnose -->
#### `CryptoBackend.diagnose`

**Kind:** function/method  
**Lines:** 41-42  
**Signature:** `def diagnose(self) -> list[tuple[str, bool, str]]`  
**Purpose:** Implements the `diagnose` operation in this module.

**Explicitly raised exceptions:** `NotImplementedError`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.crypto.backend:CryptoBackend.list_keys -->
#### `CryptoBackend.list_keys`

**Kind:** function/method  
**Lines:** 44-45  
**Signature:** `def list_keys(self, secret: bool=False) -> list[KeyInfo]`  
**Purpose:** Returns a filtered/listed view of `list_keys`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.crypto.backend:CryptoBackend.resolve_fingerprint -->
#### `CryptoBackend.resolve_fingerprint`

**Kind:** function/method  
**Lines:** 47-51  
**Signature:** `def resolve_fingerprint(self, selector: str, secret: bool=False) -> str`  
**Purpose:** Resolves `resolve_fingerprint`.

**Direct calls observed in the function body:** `ValueError`, `k.fingerprint.upper`, `len`, `selector.upper`, `self.list_keys`.

**Explicitly raised exceptions:** `ValueError`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.crypto.backend:CryptoBackend.import_public_key -->
#### `CryptoBackend.import_public_key`

**Kind:** function/method  
**Lines:** 53-58  
**Signature:** `def import_public_key(self, key_data: bytes) -> list[str]`  
**Purpose:** Import public-key material and return available encryption fingerprints. Backends that do not support key import may raise ``NotImplementedError``.

**Direct calls observed in the function body:** `NotImplementedError`.

**Explicitly raised exceptions:** `NotImplementedError`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.crypto.backend:CryptoBackend.hard_lock -->
#### `CryptoBackend.hard_lock`

**Kind:** function/method  
**Lines:** 60-62  
**Signature:** `def hard_lock(self) -> None`  
**Purpose:** Drop any cached private-key authorization if supported by the backend.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.crypto.discovery`

Cross-platform GnuPG executable discovery, including Windows Gpg4win/GnuPG installations.

**Source:** `src/keys_ng/crypto/discovery.py`  
**Executable symbols:** 5

**Direct module dependencies:** `__future__`, `dataclasses`, `keys_ng.platform.host`, `os`, `pathlib`, `sys`

<!-- symbol:keys_ng.crypto.discovery:ExecutableDiscovery -->
#### `ExecutableDiscovery`

**Kind:** class  
**Lines:** 12-16  
**Declared fields:** `path`, `method`  
**Responsibility:** Resolved external executable and the method used to find it.

<!-- symbol:keys_ng.crypto.discovery:_candidate_is_executable -->
#### `_candidate_is_executable`

**Kind:** function/method  
**Lines:** 19-28  
**Signature:** `def _candidate_is_executable(path: str | Path | None) -> str | None`  
**Purpose:** Internal helper implementing `_candidate_is_executable`.

**Direct calls observed in the function body:** `Path`, `candidate.is_file`, `candidate.resolve`, `expanduser`, `str`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 4 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.crypto.discovery:_windows_registry_roots -->
#### `_windows_registry_roots`

**Kind:** function/method  
**Lines:** 31-62  
**Signature:** `def _windows_registry_roots() -> list[Path]`  
**Purpose:** Return GnuPG/Gpg4win installation roots advertised by the Windows registry.

**Direct calls observed in the function body:** `Path`, `isinstance`, `os.path.expandvars`, `roots.append`, `value.strip`, `winreg.OpenKey`, `winreg.QueryValueEx`.

**Control-flow shape:** 2 conditional blocks, 3 loops, 3 try blocks, 1 context managers, 3 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.crypto.discovery:_windows_standard_roots -->
#### `_windows_standard_roots`

**Kind:** function/method  
**Lines:** 65-81  
**Signature:** `def _windows_standard_roots() -> list[Path]`  
**Purpose:** Internal helper implementing `_windows_standard_roots`.

**Direct calls observed in the function body:** `Path`, `casefold`, `os.environ.get`, `result.append`, `roots.extend`, `seen.add`, `set`, `str`.

**Control-flow shape:** 3 conditional blocks, 2 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.crypto.discovery:discover_gnupg_executable -->
#### `discover_gnupg_executable`

**Kind:** function/method  
**Lines:** 84-125  
**Signature:** `def discover_gnupg_executable(name: str, configured: str='') -> ExecutableDiscovery`  
**Purpose:** Resolve a GnuPG executable without a shell. Precedence is: explicit user configuration, PATH/Flatpak host PATH, Windows registry installation roots, then conventional Windows locations.

**Direct calls observed in the function body:** `ExecutableDiscovery`, `Path`, `_candidate_is_executable`, `_windows_registry_roots`, `_windows_standard_roots`, `configured.strip`, `host_which`.

**Control-flow shape:** 9 conditional blocks, 4 loops, 0 try blocks, 0 context managers, 8 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.crypto.factory`

Selects the configured cryptographic backend.

**Source:** `src/keys_ng/crypto/factory.py`  
**Executable symbols:** 1

**Direct module dependencies:** `__future__`, `keys_ng.crypto.backend`, `keys_ng.crypto.gpg_process`

<!-- symbol:keys_ng.crypto.factory:create_crypto_backend -->
#### `create_crypto_backend`

**Kind:** function/method  
**Lines:** 7-36  
**Signature:** `def create_crypto_backend(preference: str='auto', gpg_executable: str='', gpgconf_executable: str='') -> CryptoBackend`  
**Purpose:** Return the requested backend. Explicit GnuPG executable overrides select the subprocess backend so the configured paths are honored consistently on every platform.

**Direct calls observed in the function body:** `GPGMEBackend`, `GPGProcessBackend`, `RuntimeError`, `ValueError`, `gpg_executable.strip`, `gpgconf_executable.strip`, `preference.lower`.

**Explicitly raised exceptions:** `RuntimeError`, `ValueError`.

**Control-flow shape:** 5 conditional blocks, 0 loops, 2 try blocks, 0 context managers, 4 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.crypto.gpg_process`

GnuPG subprocess backend; all data crosses pipes and no shell is used.

**Source:** `src/keys_ng/crypto/gpg_process.py`  
**Executable symbols:** 12

**Direct module dependencies:** `__future__`, `keys_ng.crypto.backend`, `keys_ng.crypto.discovery`, `keys_ng.errors`, `keys_ng.platform.host`, `keys_ng.services.diagnostics`, `os`, `subprocess`, `time`, `typing`

<!-- symbol:keys_ng.crypto.gpg_process:_windows_creationflags -->
#### `_windows_creationflags`

**Kind:** function/method  
**Lines:** 18-22  
**Signature:** `def _windows_creationflags() -> int`  
**Purpose:** Suppress transient console windows for GnuPG helpers on Windows.

**Direct calls observed in the function body:** `getattr`, `int`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.crypto.gpg_process:GPGProcessBackend -->
#### `GPGProcessBackend`

**Kind:** class  
**Lines:** 25-196  
**Bases:** `CryptoBackend`  
**Methods:** `__init__`, `_base_args`, `_run`, `encrypt`, `decrypt`, `list_keys`, `import_public_key`, `resolve_fingerprint`, `hard_lock`, `diagnose`  
**Responsibility:** GnuPG backend using argv arrays and pipes only; never invokes a shell.

<!-- symbol:keys_ng.crypto.gpg_process:GPGProcessBackend.__init__ -->
#### `GPGProcessBackend.__init__`

**Kind:** function/method  
**Lines:** 28-44  
**Signature:** `def __init__(self, executable: str | None=None, gpgconf_executable: str | None=None, homedir: str | None=None) -> None`  
**Purpose:** Internal helper implementing `__init__`.

**Direct calls observed in the function body:** `_LOG.debug`, `bool`, `discover_gnupg_executable`.

**Object attributes written:** `self.executable`, `self.executable_discovery`, `self.gpgconf_discovery`, `self.gpgconf_executable`, `self.homedir`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.crypto.gpg_process:GPGProcessBackend._base_args -->
#### `GPGProcessBackend._base_args`

**Kind:** function/method  
**Lines:** 46-47  
**Signature:** `def _base_args(self) -> list[str]`  
**Purpose:** Internal helper implementing `_base_args`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.crypto.gpg_process:GPGProcessBackend._run -->
#### `GPGProcessBackend._run`

**Kind:** function/method  
**Lines:** 49-84  
**Signature:** `def _run(self, args: Iterable[str], data: bytes=b'', *, check: bool=True) -> subprocess.CompletedProcess[bytes]`  
**Purpose:** Internal helper implementing `_run`.

**Direct calls observed in the function body:** `CryptoError`, `_LOG.debug`, `_LOG.exception`, `_windows_creationflags`, `elapsed_ms`, `host_argv`, `len`, `list`, `os.environ.copy`, `proc.stderr.decode`, `safe_operation_args`, `self._base_args`, `strip`, `subprocess.run`, `time.perf_counter`.

**Explicitly raised exceptions:** `CryptoError`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** process.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.crypto.gpg_process:GPGProcessBackend.encrypt -->
#### `GPGProcessBackend.encrypt`

**Kind:** function/method  
**Lines:** 86-95  
**Signature:** `def encrypt(self, plaintext: bytes, recipients: list[str], signer: str | None=None) -> bytes`  
**Purpose:** Implements the `encrypt` operation in this module.

**Direct calls observed in the function body:** `CryptoError`, `args.append`, `args.extend`, `self._run`.

**Explicitly raised exceptions:** `CryptoError`.

**Control-flow shape:** 2 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** process.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.crypto.gpg_process:GPGProcessBackend.decrypt -->
#### `GPGProcessBackend.decrypt`

**Kind:** function/method  
**Lines:** 97-118  
**Signature:** `def decrypt(self, ciphertext: bytes) -> DecryptionResult`  
**Purpose:** Implements the `decrypt` operation in this module.

**Direct calls observed in the function body:** `DecryptionResult`, `len`, `proc.stderr.decode`, `raw_line.startswith`, `self._run`, `splitlines`, `status.split`, `status.startswith`, `upper`.

**Control-flow shape:** 4 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** process, cryptography/key-agent.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.crypto.gpg_process:GPGProcessBackend.list_keys -->
#### `GPGProcessBackend.list_keys`

**Kind:** function/method  
**Lines:** 120-148  
**Signature:** `def list_keys(self, secret: bool=False) -> list[KeyInfo]`  
**Purpose:** Returns a filtered/listed view of `list_keys`.

**Direct calls observed in the function body:** `KeyInfo`, `caps.lower`, `current.get`, `keys.append`, `len`, `line.split`, `proc.stdout.decode`, `self._run`, `splitlines`, `upper`.

**Control-flow shape:** 5 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** process.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.crypto.gpg_process:GPGProcessBackend.import_public_key -->
#### `GPGProcessBackend.import_public_key`

**Kind:** function/method  
**Lines:** 150-152  
**Signature:** `def import_public_key(self, key_data: bytes) -> list[str]`  
**Purpose:** Imports `import_public_key`.

**Direct calls observed in the function body:** `self._run`, `self.list_keys`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** process.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.crypto.gpg_process:GPGProcessBackend.resolve_fingerprint -->
#### `GPGProcessBackend.resolve_fingerprint`

**Kind:** function/method  
**Lines:** 154-161  
**Signature:** `def resolve_fingerprint(self, selector: str, secret: bool=False) -> str`  
**Purpose:** Resolves `resolve_fingerprint`.

**Direct calls observed in the function body:** `CryptoError`, `any`, `len`, `selector.strip`, `self.list_keys`, `upper`.

**Explicitly raised exceptions:** `CryptoError`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.crypto.gpg_process:GPGProcessBackend.hard_lock -->
#### `GPGProcessBackend.hard_lock`

**Kind:** function/method  
**Lines:** 163-178  
**Signature:** `def hard_lock(self) -> None`  
**Purpose:** Implements the `hard_lock` operation in this module.

**Direct calls observed in the function body:** `CryptoError`, `_windows_creationflags`, `host_argv`, `proc.stderr.decode`, `strip`, `subprocess.run`.

**Explicitly raised exceptions:** `CryptoError`.

**Control-flow shape:** 3 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** process.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.crypto.gpg_process:GPGProcessBackend.diagnose -->
#### `GPGProcessBackend.diagnose`

**Kind:** function/method  
**Lines:** 180-196  
**Signature:** `def diagnose(self) -> list[tuple[str, bool, str]]`  
**Purpose:** Implements the `diagnose` operation in this module.

**Direct calls observed in the function body:** `bool`, `checks.append`, `len`, `proc.stdout.decode`, `self._run`, `self.list_keys`, `splitlines`, `str`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** process.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.crypto.gpgme_backend`

Reserved module for a future GPGME backend; currently contains no executable symbols.

**Source:** `src/keys_ng/crypto/gpgme_backend.py`  
**Executable symbols:** 0

**Direct module dependencies:** `__future__`

### `keys_ng.errors`

Project exception hierarchy.

**Source:** `src/keys_ng/errors.py`  
**Executable symbols:** 6

<!-- symbol:keys_ng.errors:KeysNGError -->
#### `KeysNGError`

**Kind:** class  
**Lines:** 1-2  
**Bases:** `Exception`  
**Responsibility:** Base application error.

<!-- symbol:keys_ng.errors:CryptoError -->
#### `CryptoError`

**Kind:** class  
**Lines:** 5-6  
**Bases:** `KeysNGError`  
**Responsibility:** OpenPGP operation failed.

<!-- symbol:keys_ng.errors:SignatureError -->
#### `SignatureError`

**Kind:** class  
**Lines:** 9-10  
**Bases:** `CryptoError`  
**Responsibility:** A required signature was missing or invalid.

<!-- symbol:keys_ng.errors:VaultError -->
#### `VaultError`

**Kind:** class  
**Lines:** 13-14  
**Bases:** `KeysNGError`  
**Responsibility:** Vault storage or configuration error.

<!-- symbol:keys_ng.errors:LegacyFormatError -->
#### `LegacyFormatError`

**Kind:** class  
**Lines:** 17-18  
**Bases:** `KeysNGError`  
**Responsibility:** Legacy record did not match the strict supported grammar.

<!-- symbol:keys_ng.errors:ReferenceError -->
#### `ReferenceError`

**Kind:** class  
**Lines:** 21-22  
**Bases:** `KeysNGError`  
**Responsibility:** An entry cross-reference was invalid, broken, or cyclic.

### `keys_ng.gui.main`

PySide6 desktop GUI, including dialogs, per-vault panes, menus and multi-vault orchestration.

**Source:** `src/keys_ng/gui/main.py`  
**Executable symbols:** 106

**Direct module dependencies:** `__future__`, `argparse`, `keys_ng`, `keys_ng.crypto.factory`, `keys_ng.i18n`, `keys_ng.migration.keepassxc`, `keys_ng.migration.keepassxc_export`, `keys_ng.models`, `keys_ng.platform.app_identity`, `keys_ng.platform.desktop_integration`, `keys_ng.services.actions`, `keys_ng.services.clipboard`, `keys_ng.services.diagnostics`, `keys_ng.services.entry_editor`, `keys_ng.services.passwords`, `keys_ng.services.qr`, `keys_ng.services.ssh_options`, `keys_ng.services.totp`, `keys_ng.services.trusted_signers`, `keys_ng.services.vault_init`, `keys_ng.storage.inbox`, `keys_ng.storage.settings`, `keys_ng.storage.vault`, `pathlib`, `sys`, `time`

<!-- symbol:keys_ng.gui.main:main -->
#### `main`

**Kind:** function/method  
**Lines:** 31-1635  
**Signature:** `def main() -> None`  
**Purpose:** Implements the `main` operation in this module.

**Direct calls observed in the function body:** `AppSettings.load`, `EntryDialog`, `EntryDraft`, `HelpDialog`, `InboxDialog`, `KeePassXCImportDialog`, `MainWindow`, `NewVaultWizard`, `PasswordGeneratorDialog`, `Path`, `Path.home`, `QApplication`, `QApplication.clipboard`, `QApplication.focusWidget`, `QCheckBox`, `QComboBox`, `QDialogButtonBox`, `QDoubleSpinBox`, `QFileDialog.getExistingDirectory`, `QFileDialog.getOpenFileName`, `QFileDialog.getSaveFileName`, `QFormLayout`, `QHBoxLayout`, `QIcon.fromTheme`, `QInputDialog.getItem`, `QInputDialog.getText`, `QKeySequence`, `QLabel`, `QLineEdit`, `QListWidget`, `QMessageBox.critical`, `QMessageBox.information`, `QMessageBox.question`, `QMessageBox.warning`, `QPushButton`, `QShortcut`, `QSpinBox`, `QStackedWidget`, `QTabWidget`, `QTextBrowser`, `QTextEdit`, `QTimer`, `QTreeWidgetItem`, `QVBoxLayout`, `QWidget`, `QWizardPage`, `SettingsDialog`, `SystemExit`, `TrustedSignersDialog`, `ValueError`, `Vault`, `VaultInitRequest`, `VaultPane`, `VaultTree`, `_`, `__init__`, `action.setEnabled`, `action.setToolTip`, `action.triggered.connect`, `addMenu`, `add_button.clicked.connect`, `add_trusted_signer`, `app.exec`, `apply_qt_identity`, `argparse.ArgumentParser`, `authorize_button.clicked.connect`, `available_vault_keys`, `backend.diagnose`, `bool`, `box.toggled.connect`, `browse.clicked.connect`, `browser.setMarkdown`, `browser.setOpenExternalLinks`, `build_entry_from_draft`, `build_otpauth_uri`, `buttons.accepted.connect`, `buttons.addStretch`, `buttons.addWidget`, `buttons.rejected.connect`, `ch.isalnum`, `clear`, `clipboard_form.addRow`, `close_button.clicked.connect`, `close_buttons.rejected.connect`, `configure_diagnostics`, `configure_language`, `configure_process_identity`, `copy_secret_qt`, `create_button.clicked.connect`, `create_crypto_backend`, `create_vault`, `current.data`, `current.text`, `current_language`, `data`, `delete_button.clicked.connect`, `delete_inbox_item`, `dialog.apply`, `dialog.build_entry`, `dialog.exec`, `dialog.value`, `elapsed_ms`, `eligible_signing_keys`, `empty_label.setAlignment`, `empty_layout.addStretch`, `empty_layout.addWidget`, `ensure_user_desktop_integration`, `entry_menu.addSeparator`, `event.accept`, `event.position`, `exec`, `expanduser`, `export_entry_xml`, `export_vault_xml`, `failures.append`, `files`, `float`, `focus.copy`, `focus.hasSelectedText`, `focus.textCursor`, `folder_widgets.get`, `form.addRow`, `format`, `format_import_report`, `format_ssh_options`, `general_form.addRow`, `generate_password`, `generate_totp`, `get_logger`, `getattr`, `hasSelection`, `hasattr`, `help_label`, `help_root.joinpath`, `icon.isNull`, `image`, `image.isNull`, `import_button.clicked.connect`, `import_inbox_item`, `import_keepassxc`, `import_trusted_button.clicked.connect`, `inspect_inbox`, `int`, `isinstance`, `item.data`, `item.flags`, `item.setData`, `item.setFlags`, `item.setIcon`, `join`, `joinpath`, `key_button.clicked.connect`, `key_layout.addWidget`, `key_layout.setContentsMargins`, `keys_form.addRow`, `keys_page.setSubTitle`, `keys_page.setTitle`, `label.setStyleSheet`, `label.setWordWrap`, `labels.index`, `launch_action`, `layout.addLayout`, `layout.addWidget`, `left.addLayout`, `left.addWidget`, `len`, `line.strip`, `list`, `list_trusted_signers`, `location.setSubTitle`, `location.setTitle`, `location_layout.addLayout`, `log.debug`, `log.error`, `log.info`, `mapping.get`, `max`, `menu.addAction`, `min`, `name.strip`, `next`, `open_button.clicked.connect`, `options.setSubTitle`, `options.setTitle`, `options_form.addRow`, `pane.clear_details`, `pane.deleteLater`, `pane.reload`, `pane.reset_auto_lock_timer`, `pane.vault.lock`, `parent.addChild`, `parse_totp_qimage`, `parse_totp_qr_file`, `parser.add_argument`, `parser.parse_args`, `password_layout.addWidget`, `password_layout.setContentsMargins`, `paths.get`, `pending_inbox_paths`, `preferences_action.setMenuRole`, `preview_button.clicked.connect`, `print`, `range`, `rdp_form.addRow`, `refresh.clicked.connect`, `refresh_button.clicked.connect`, `remaining.remove`, `remove_button.clicked.connect`, `remove_trusted_signer`, `resolve`, `resource.is_file`, `resource.read_text`, `right.addStretch`, `right.addWidget`, `root_layout.addLayout`, `row.addStretch`, `row.addWidget`, `s.save`, `self._entry_icon`, `self._entry_item`, `self._folder_icon`, `self._folder_item`, `self._lines`, `self._menu_action`, `self._run`, `self._status_text`, `self._sync_empty_state`, `self._theme_icon`, `self.accept`, `self.action_type_combo.addItem`, `self.action_type_combo.currentData`, `self.action_type_combo.currentIndexChanged.connect`, `self.action_type_combo.findData`, `self.action_type_combo.setCurrentIndex`, `self.active_pane`, `self.activity`, `self.addPage`, `self.ambiguous.isChecked`, `self.ambiguous.setChecked`, `self.auto_lock_spin.setRange`, `self.auto_lock_spin.setSuffix`, `self.auto_lock_spin.setValue`, `self.auto_lock_spin.value`, `self.auto_lock_timer.setSingleShot`, `self.auto_lock_timer.start`, `self.auto_lock_timer.timeout.connect`, `self.build_menus`, `self.call_active`, `self.clear_details`, `self.close_vault`, `self.copy_notes.clicked.connect`, `self.copy_otp.clicked.connect`, `self.copy_otp.setToolTip`, `self.copy_password.clicked.connect`, `self.copy_password.setToolTip`, `self.copy_url.clicked.connect`, `self.copy_url.setToolTip`, `self.copy_username.clicked.connect`, `self.copy_username.setToolTip`, `self.copy_uuid.clicked.connect`, `self.copy_uuid.setToolTip`, `self.crypto_combo.addItem`, `self.crypto_combo.currentData`, `self.crypto_combo.findData`, `self.crypto_combo.setCurrentIndex`, `self.currentIdChanged.connect`, `self.currentItem`, `self.delete_button.clicked.connect`, `self.delete_folder_button.clicked.connect`, `self.details.clear`, `self.details.setText`, `self.details.setWordWrap`, `self.digits.isChecked`, `self.digits.setChecked`, `self.edit_button.clicked.connect`, `self.entries.addTopLevelItem`, `self.entries.clear`, `self.entries.collapseAll`, `self.entries.currentItemChanged.connect`, `self.entries.expandAll`, `self.entries.itemDoubleClicked.connect`, `self.entries.setDragEnabled`, `self.folder_combo.addItem`, `self.folder_combo.currentData`, `self.folder_combo.findData`, `self.folder_combo.setCurrentIndex`, `self.gpg_path_edit.setPlaceholderText`, `self.gpg_path_edit.text`, `self.gpgconf_path_edit.setPlaceholderText`, `self.gpgconf_path_edit.text`, `self.hard_lock_button.clicked.connect`, `self.host_edit.setVisible`, `self.host_edit.text`, `self.host_label.setVisible`, `self.itemAt`, `self.key_file_edit.setText`, `self.key_file_edit.text`, `self.language_combo.addItem`, `self.language_combo.currentData`, `self.language_combo.findData`, `self.language_combo.setCurrentIndex`, `self.length.setRange`, `self.length.setValue`, `self.length.value`, `self.length.valueChanged.connect`, `self.list.addItem`, `self.list.clear`, `self.list.count`, `self.list.currentItem`, `self.list.currentRow`, `self.list.currentRowChanged.connect`, `self.list.item`, `self.list.setCurrentRow`, `self.lock`, `self.lock_button.clicked.connect`, `self.lower.isChecked`, `self.lower.setChecked`, `self.menuBar`, `self.new_button.clicked.connect`, `self.new_folder_button.clicked.connect`, `self.no_password.isChecked`, `self.notes.clear`, `self.notes.setMinimumHeight`, `self.notes.setReadOnly`, `self.notes.setText`, `self.notes.setToolTip`, `self.notes_edit.toPlainText`, `self.on_move`, `self.on_reload`, `self.open_action.clicked.connect`, `self.open_action.setToolTip`, `self.open_action_clicked`, `self.open_vault`, `self.otp.clear`, `self.otp.setText`, `self.password_edit.setEchoMode`, `self.password_edit.setText`, `self.password_edit.setToolTip`, `self.password_edit.text`, `self.password_generate.clicked.connect`, `self.password_generate.setToolTip`, `self.password_timeout_spin.setRange`, `self.password_timeout_spin.setSuffix`, `self.password_timeout_spin.setValue`, `self.password_timeout_spin.value`, `self.password_toggle.setCheckable`, `self.password_toggle.setText`, `self.password_toggle.setToolTip`, `self.password_toggle.toggled.connect`, `self.path_edit.setText`, `self.path_edit.text`, `self.path_label.clear`, `self.path_label.setText`, `self.port_edit.setPlaceholderText`, `self.port_edit.setVisible`, `self.port_edit.text`, `self.port_label.setVisible`, `self.preview.setReadOnly`, `self.preview.setText`, `self.preview.text`, `self.privacy_combo.addItem`, `self.privacy_combo.currentData`, `self.privacy_combo.setCurrentIndex`, `self.qr_button.clicked.connect`, `self.qr_clipboard_button.clicked.connect`, `self.rdp_linux_client_edit.text`, `self.rdp_linux_options_edit.setMaximumHeight`, `self.rdp_linux_options_edit.setPlainText`, `self.rdp_macos_client_edit.text`, `self.rdp_macos_options_edit.setMaximumHeight`, `self.rdp_macos_options_edit.setPlainText`, `self.rdp_windows_client_edit.text`, `self.rdp_windows_options_edit.setMaximumHeight`, `self.rdp_windows_options_edit.setPlainText`, `self.recent_menu.aboutToShow.connect`, `self.recent_menu.addAction`, `self.recent_menu.clear`, `self.recipient_combo.addItem`, `self.recipient_combo.currentData`, `self.refresh`, `self.refresh_otp`, `self.refresh_recent_menu`, `self.regenerate`, `self.reload`, `self.rename_folder_button.clicked.connect`, `self.report.setPlaceholderText`, `self.report.setPlainText`, `self.report.setReadOnly`, `self.require_signature.isChecked`, `self.require_signature.setChecked`, `self.resize`, `self.search.selectAll`, `self.search.setClearButtonEnabled`, `self.search.setFocus`, `self.search.setPlaceholderText`, `self.search.setToolTip`, `self.search.text`, `self.search.textChanged.connect`, `self.search_timer.setInterval`, `self.search_timer.setSingleShot`, `self.search_timer.start`, `self.search_timer.timeout.connect`, `self.setAcceptDrops`, `self.setCentralWidget`, `self.setDefaultDropAction`, `self.setDragDropMode`, `self.setDragEnabled`, `self.setDropIndicatorShown`, `self.setHeaderHidden`, `self.setLayout`, `self.setWindowTitle`, `self.shortcuts.append`, `self.show_help`, `self.show_inbox`, `self.signer_combo.addItem`, `self.signer_combo.currentData`, `self.source_edit.setText`, `self.source_edit.text`, `self.ssh_options_edit.setMaximumHeight`, `self.ssh_options_edit.setPlaceholderText`, `self.ssh_options_edit.setPlainText`, `self.ssh_options_edit.setText`, `self.ssh_options_edit.setVisible`, `self.ssh_options_edit.text`, `self.ssh_options_label.setVisible`, `self.ssh_terminal_edit.text`, `self.ssh_x11_combo.addItem`, `self.ssh_x11_combo.currentData`, `self.ssh_x11_combo.findData`, `self.ssh_x11_combo.setCurrentIndex`, `self.ssh_x11_combo.setVisible`, `self.ssh_x11_label.setVisible`, `self.stack.addWidget`, `self.stack.setCurrentWidget`, `self.statusBar`, `self.status_message`, `self.style`, `self.summary_label.setText`, `self.summary_label.setWordWrap`, `self.symbols.isChecked`, `self.symbols.setChecked`, `self.tabs.addTab`, `self.tabs.count`, `self.tabs.currentChanged.connect`, `self.tabs.currentIndex`, `self.tabs.currentWidget`, `self.tabs.removeTab`, `self.tabs.setCurrentIndex`, `self.tabs.setMovable`, `self.tabs.setTabPosition`, `self.tabs.setTabToolTip`, `self.tabs.setTabsClosable`, `self.tabs.tabCloseRequested.connect`, `self.tabs.widget`, `self.tags_edit.text`, `self.timer.start`, `self.timer.timeout.connect`, `self.title.clear`, `self.title.setText`, `self.title_edit.text`, `self.totp_edit.setText`, `self.totp_edit.text`, `self.totp_secret_edit.setEchoMode`, `self.totp_secret_edit.setText`, `self.totp_secret_edit.text`, `self.totp_timeout_spin.setRange`, `self.totp_timeout_spin.setSuffix`, `self.totp_timeout_spin.setValue`, `self.totp_timeout_spin.value`, `self.tree_combo.addItem`, `self.tree_combo.currentData`, `self.tree_combo.findData`, `self.tree_combo.setCurrentIndex`, `self.tui_notice_background_edit.setPlaceholderText`, `self.tui_notice_background_edit.text`, `self.tui_notice_foreground_edit.setPlaceholderText`, `self.tui_notice_foreground_edit.text`, `self.tui_notice_seconds_spin.setRange`, `self.tui_notice_seconds_spin.setSingleStep`, `self.tui_notice_seconds_spin.setSuffix`, `self.tui_notice_seconds_spin.setValue`, `self.tui_notice_seconds_spin.value`, `self.unlock_button.clicked.connect`, `self.update_action_fields`, `self.update_window_title`, `self.upper.isChecked`, `self.upper.setChecked`, `self.url_edit.setVisible`, `self.url_edit.text`, `self.url_label.setVisible`, `self.username.clear`, `self.username.setText`, `self.username_edit.setToolTip`, `self.username_edit.text`, `self.uuid_label.clear`, `self.uuid_label.setText`, `self.vault.create_folder`, `self.vault.delete_entry`, `self.vault.delete_folder`, `self.vault.folder_path`, `self.vault.folder_paths`, `self.vault.get_entry`, `self.vault.get_folder`, `self.vault.list_folders`, `self.vault.list_items`, `self.vault.lock`, `self.vault.move_entry`, `self.vault.move_folder`, `self.vault.rename_folder`, `self.vault.resolved_action`, `self.vault.resolved_password`, `self.vault.resolved_username`, `self.vault.save_entry`, `self.vault.search`, `self.vault.unlock`, `self.window`, `self.yubikey_edit.setPlaceholderText`, `self.yubikey_edit.text`, `set`, `setData`, `settings.remember_vault`, `settings.save`, `shortcut.activated.connect`, `shortcut.setContext`, `showMessage`, `source_button.clicked.connect`, `source_layout.addWidget`, `source_layout.setContentsMargins`, `splitlines`, `ssh_form.addRow`, `standardIcon`, `str`, `strip`, `summary.setSubTitle`, `summary.setTitle`, `summary_layout.addWidget`, `super`, `tabs.addTab`, `tabs.count`, `tabs.setCurrentIndex`, `target.data`, `target.parent`, `time.perf_counter`, `toPoint`, `toolbar1.addWidget`, `toolbar2.addWidget`, `type`, `vault.crypto.hard_lock`, `vault_menu.addMenu`, `vault_menu.addSeparator`, `verify_gpg.clicked.connect`, `widget.toPlainText`, `window.hard_lock_all`, `window.resize`, `window.setWindowIcon`, `window.show`, `window.statusBar`, `wizard.exec`, `wizard.request`, `write_export`.

**Explicitly raised exceptions:** `SystemExit`, `ValueError`.

**Object attributes written:** `s.auto_lock_timeout`, `s.clipboard_password_timeout`, `s.clipboard_totp_timeout`, `s.crypto_backend`, `s.gpg_executable`, `s.gpgconf_executable`, `s.language`, `s.rdp_linux_client`, `s.rdp_linux_options`, `s.rdp_macos_client`, `s.rdp_macos_options`, `s.rdp_windows_client`, `s.rdp_windows_options`, `s.ssh_terminal`, `s.ssh_terminal_options`, `s.tree_startup_view`, `s.tui_clipboard_notice_background`, `s.tui_clipboard_notice_foreground`, `s.tui_clipboard_notice_seconds`, `self._choices`, `self.action_type_combo`, `self.ambiguous`, `self.app_settings`, `self.auto_lock_spin`, `self.auto_lock_timer`, `self.copy_notes`, `self.copy_otp`, `self.copy_password`, `self.copy_url`, `self.copy_username`, `self.copy_uuid`, `self.crypto`, `self.crypto_combo`, `self.current_entry`, `self.current_folder_id`, `self.current_id`, `self.delete_button`, `self.delete_folder_button`, `self.details`, `self.digits`, `self.edit_button`, `self.empty_page`, `self.entries`, `self.entry`, `self.folder_combo`, `self.gpg_path_edit`, `self.gpgconf_path_edit`, `self.hard_lock_button`, `self.host_edit`, `self.host_label`, `self.items`, `self.key_file_edit`, `self.language_combo`, `self.length`, `self.list`, `self.lock_button`, `self.lower`, `self.new_button`, `self.new_folder_button`, `self.no_password`, `self.notes`, `self.notes_edit`, `self.on_move`, `self.on_reload`, `self.open_action`, `self.otp`, `self.password_edit`, `self.password_generate`, `self.password_timeout_spin`, `self.password_toggle`, `self.path_edit`, `self.path_label`, `self.port_edit`, `self.port_label`, `self.preview`, `self.privacy_combo`, `self.qr_button`, `self.qr_clipboard_button`, `self.rdp_linux_client_edit`, `self.rdp_linux_options_edit`, `self.rdp_macos_client_edit`, `self.rdp_macos_options_edit`, `self.rdp_windows_client_edit`, `self.rdp_windows_options_edit`, `self.recent_menu`, `self.recipient_combo`, `self.rename_folder_button`, `self.report`, `self.require_signature`, `self.search`, `self.search_timer`, `self.shortcuts`, `self.signer_combo`, `self.source_edit`, `self.ssh_options_edit`, `self.ssh_options_label`, `self.ssh_terminal_edit`, `self.ssh_x11_combo`, `self.ssh_x11_label`, `self.stack`, `self.summary_label`, `self.symbols`, `self.tabs`, `self.tags_edit`, `self.timer`, `self.title`, `self.title_edit`, `self.totp_edit`, `self.totp_secret_edit`, `self.totp_timeout_spin`, `self.tree_combo`, `self.tui_notice_background_edit`, `self.tui_notice_foreground_edit`, `self.tui_notice_seconds_spin`, `self.unlock_button`, `self.upper`, `self.url_edit`, `self.url_label`, `self.username`, `self.username_edit`, `self.uuid_label`, `self.vault`, `self.vault_path`, `self.yubikey_edit`.

**Control-flow shape:** 109 conditional blocks, 24 loops, 36 try blocks, 0 context managers, 66 explicit returns.

**Security-relevant effect categories:** process, filesystem, cryptography/key-agent, clipboard, parser/serialization.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultTree -->
#### `main.VaultTree`

**Kind:** class  
**Lines:** 83-114  
**Bases:** `QTreeWidget`  
**Methods:** `__init__`, `dropEvent`  
**Responsibility:** Implements the `VaultTree` operation in this module.

<!-- symbol:keys_ng.gui.main:main.VaultTree.__init__ -->
#### `main.VaultTree.__init__`

**Kind:** function/method  
**Lines:** 84-93  
**Signature:** `def __init__(self, on_move, on_reload, parent=None) -> None`  
**Purpose:** Internal helper implementing `__init__`.

**Direct calls observed in the function body:** `__init__`, `self.setAcceptDrops`, `self.setDefaultDropAction`, `self.setDragDropMode`, `self.setDragEnabled`, `self.setDropIndicatorShown`, `self.setHeaderHidden`, `super`.

**Object attributes written:** `self.on_move`, `self.on_reload`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultTree.dropEvent -->
#### `main.VaultTree.dropEvent`

**Kind:** function/method  
**Lines:** 95-114  
**Signature:** `def dropEvent(self, event) -> None`  
**Purpose:** Implements the `dropEvent` operation in this module.

**Direct calls observed in the function body:** `QMessageBox.critical`, `_`, `data`, `event.accept`, `event.position`, `item.data`, `self.currentItem`, `self.itemAt`, `self.on_move`, `self.on_reload`, `str`, `target.data`, `target.parent`, `toPoint`.

**Control-flow shape:** 4 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** parser/serialization.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.PasswordGeneratorDialog -->
#### `main.PasswordGeneratorDialog`

**Kind:** class  
**Lines:** 116-146  
**Bases:** `QDialog`  
**Methods:** `__init__`, `regenerate`, `value`  
**Responsibility:** Implements the `PasswordGeneratorDialog` operation in this module.

<!-- symbol:keys_ng.gui.main:main.PasswordGeneratorDialog.__init__ -->
#### `main.PasswordGeneratorDialog.__init__`

**Kind:** function/method  
**Lines:** 117-136  
**Signature:** `def __init__(self, parent=None) -> None`  
**Purpose:** Internal helper implementing `__init__`.

**Direct calls observed in the function body:** `QCheckBox`, `QDialogButtonBox`, `QFormLayout`, `QLineEdit`, `QPushButton`, `QSpinBox`, `QVBoxLayout`, `_`, `__init__`, `box.toggled.connect`, `buttons.accepted.connect`, `buttons.rejected.connect`, `form.addRow`, `layout.addLayout`, `layout.addWidget`, `refresh.clicked.connect`, `self.ambiguous.setChecked`, `self.digits.setChecked`, `self.length.setRange`, `self.length.setValue`, `self.length.valueChanged.connect`, `self.lower.setChecked`, `self.preview.setReadOnly`, `self.regenerate`, `self.setWindowTitle`, `self.symbols.setChecked`, `self.upper.setChecked`, `super`.

**Object attributes written:** `self.ambiguous`, `self.digits`, `self.length`, `self.lower`, `self.preview`, `self.symbols`, `self.upper`.

**Control-flow shape:** 0 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.PasswordGeneratorDialog.regenerate -->
#### `main.PasswordGeneratorDialog.regenerate`

**Kind:** function/method  
**Lines:** 137-144  
**Signature:** `def regenerate(self) -> None`  
**Purpose:** Implements the `regenerate` operation in this module.

**Direct calls observed in the function body:** `_`, `generate_password`, `self.ambiguous.isChecked`, `self.digits.isChecked`, `self.length.value`, `self.lower.isChecked`, `self.preview.setText`, `self.symbols.isChecked`, `self.upper.isChecked`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.PasswordGeneratorDialog.value -->
#### `main.PasswordGeneratorDialog.value`

**Kind:** function/method  
**Lines:** 145-146  
**Signature:** `def value(self) -> str`  
**Purpose:** Implements the `value` operation in this module.

**Direct calls observed in the function body:** `self.preview.text`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.EntryDialog -->
#### `main.EntryDialog`

**Kind:** class  
**Lines:** 148-330  
**Bases:** `QDialog`  
**Methods:** `__init__`, `toggle_password_visibility`, `generate_password_value`, `update_action_fields`, `import_qr`, `import_qr_clipboard`, `build_entry`  
**Responsibility:** Implements the `EntryDialog` operation in this module.

<!-- symbol:keys_ng.gui.main:main.EntryDialog.__init__ -->
#### `main.EntryDialog.__init__`

**Kind:** function/method  
**Lines:** 151-255  
**Signature:** `def __init__(self, vault_obj: Vault, parent=None, entry: Entry | None=None, default_folder_id: str | None=None) -> None`  
**Purpose:** Internal helper implementing `__init__`.

**Direct calls observed in the function body:** `QComboBox`, `QDialogButtonBox`, `QFormLayout`, `QHBoxLayout`, `QLabel`, `QLineEdit`, `QPushButton`, `QTextEdit`, `QVBoxLayout`, `QWidget`, `_`, `__init__`, `build_otpauth_uri`, `buttons.accepted.connect`, `buttons.rejected.connect`, `form.addRow`, `format_ssh_options`, `join`, `layout.addLayout`, `layout.addWidget`, `next`, `password_layout.addWidget`, `password_layout.setContentsMargins`, `self.action_type_combo.addItem`, `self.action_type_combo.currentIndexChanged.connect`, `self.action_type_combo.findData`, `self.action_type_combo.setCurrentIndex`, `self.folder_combo.addItem`, `self.folder_combo.findData`, `self.folder_combo.setCurrentIndex`, `self.password_edit.setEchoMode`, `self.password_edit.setToolTip`, `self.password_generate.clicked.connect`, `self.password_generate.setToolTip`, `self.password_toggle.setCheckable`, `self.password_toggle.setToolTip`, `self.password_toggle.toggled.connect`, `self.qr_button.clicked.connect`, `self.qr_clipboard_button.clicked.connect`, `self.setWindowTitle`, `self.ssh_options_edit.setPlaceholderText`, `self.ssh_options_edit.setText`, `self.ssh_x11_combo.addItem`, `self.ssh_x11_combo.findData`, `self.ssh_x11_combo.setCurrentIndex`, `self.totp_edit.setText`, `self.totp_secret_edit.setEchoMode`, `self.totp_secret_edit.setText`, `self.update_action_fields`, `self.username_edit.setToolTip`, `self.vault.folder_path`, `self.vault.list_folders`, `str`, `super`.

**Object attributes written:** `self.action_type_combo`, `self.entry`, `self.folder_combo`, `self.host_edit`, `self.host_label`, `self.notes_edit`, `self.password_edit`, `self.password_generate`, `self.password_toggle`, `self.port_edit`, `self.port_label`, `self.qr_button`, `self.qr_clipboard_button`, `self.ssh_options_edit`, `self.ssh_options_label`, `self.ssh_x11_combo`, `self.ssh_x11_label`, `self.tags_edit`, `self.title_edit`, `self.totp_edit`, `self.totp_secret_edit`, `self.url_edit`, `self.url_label`, `self.username_edit`, `self.vault`.

**Control-flow shape:** 5 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** clipboard.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.EntryDialog.toggle_password_visibility -->
#### `main.EntryDialog.toggle_password_visibility`

**Kind:** function/method  
**Lines:** 257-259  
**Signature:** `def toggle_password_visibility(self, visible: bool) -> None`  
**Purpose:** Implements the `toggle_password_visibility` operation in this module.

**Direct calls observed in the function body:** `_`, `self.password_edit.setEchoMode`, `self.password_toggle.setText`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.EntryDialog.generate_password_value -->
#### `main.EntryDialog.generate_password_value`

**Kind:** function/method  
**Lines:** 261-264  
**Signature:** `def generate_password_value(self) -> None`  
**Purpose:** Implements the `generate_password_value` operation in this module.

**Direct calls observed in the function body:** `PasswordGeneratorDialog`, `dialog.exec`, `dialog.value`, `self.password_edit.setText`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.EntryDialog.update_action_fields -->
#### `main.EntryDialog.update_action_fields`

**Kind:** function/method  
**Lines:** 266-286  
**Signature:** `def update_action_fields(self) -> None`  
**Purpose:** Implements the `update_action_fields` operation in this module.

**Direct calls observed in the function body:** `self.action_type_combo.currentData`, `self.host_edit.setVisible`, `self.host_label.setVisible`, `self.port_edit.setPlaceholderText`, `self.port_edit.setVisible`, `self.port_label.setVisible`, `self.ssh_options_edit.setVisible`, `self.ssh_options_label.setVisible`, `self.ssh_x11_combo.setVisible`, `self.ssh_x11_label.setVisible`, `self.url_edit.setVisible`, `self.url_label.setVisible`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.EntryDialog.import_qr -->
#### `main.EntryDialog.import_qr`

**Kind:** function/method  
**Lines:** 288-298  
**Signature:** `def import_qr(self) -> None`  
**Purpose:** Imports `import_qr`.

**Direct calls observed in the function body:** `QFileDialog.getOpenFileName`, `QMessageBox.critical`, `_`, `build_otpauth_uri`, `parse_totp_qr_file`, `self.totp_edit.setText`, `self.totp_secret_edit.setText`, `str`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.EntryDialog.import_qr_clipboard -->
#### `main.EntryDialog.import_qr_clipboard`

**Kind:** function/method  
**Lines:** 300-311  
**Signature:** `def import_qr_clipboard(self) -> None`  
**Purpose:** Imports `import_qr_clipboard`.

**Direct calls observed in the function body:** `QApplication.clipboard`, `QMessageBox.critical`, `ValueError`, `_`, `build_otpauth_uri`, `image`, `image.isNull`, `parse_totp_qimage`, `self.totp_edit.setText`, `self.totp_secret_edit.setText`, `str`.

**Explicitly raised exceptions:** `ValueError`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** clipboard.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.EntryDialog.build_entry -->
#### `main.EntryDialog.build_entry`

**Kind:** function/method  
**Lines:** 313-330  
**Signature:** `def build_entry(self) -> Entry`  
**Purpose:** Builds `build_entry`.

**Direct calls observed in the function body:** `EntryDraft`, `build_entry_from_draft`, `self.action_type_combo.currentData`, `self.folder_combo.currentData`, `self.host_edit.text`, `self.notes_edit.toPlainText`, `self.password_edit.text`, `self.port_edit.text`, `self.ssh_options_edit.text`, `self.ssh_x11_combo.currentData`, `self.tags_edit.text`, `self.title_edit.text`, `self.totp_edit.text`, `self.totp_secret_edit.text`, `self.url_edit.text`, `self.username_edit.text`, `str`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.HelpDialog -->
#### `main.HelpDialog`

**Kind:** class  
**Lines:** 332-364  
**Bases:** `QDialog`  
**Methods:** `__init__`  
**Responsibility:** Implements the `HelpDialog` operation in this module.

<!-- symbol:keys_ng.gui.main:main.HelpDialog.__init__ -->
#### `main.HelpDialog.__init__`

**Kind:** function/method  
**Lines:** 333-364  
**Signature:** `def __init__(self, parent=None, initial_tab: int=0) -> None`  
**Purpose:** Internal helper implementing `__init__`.

**Direct calls observed in the function body:** `QDialogButtonBox`, `QTabWidget`, `QTextBrowser`, `QVBoxLayout`, `_`, `__init__`, `browser.setMarkdown`, `browser.setOpenExternalLinks`, `close_buttons.rejected.connect`, `current_language`, `files`, `format`, `help_root.joinpath`, `joinpath`, `layout.addWidget`, `max`, `min`, `resource.is_file`, `resource.read_text`, `self.resize`, `self.setWindowTitle`, `super`, `tabs.addTab`, `tabs.count`, `tabs.setCurrentIndex`.

**Control-flow shape:** 2 conditional blocks, 1 loops, 1 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.KeePassXCImportDialog -->
#### `main.KeePassXCImportDialog`

**Kind:** class  
**Lines:** 366-443  
**Bases:** `QDialog`  
**Methods:** `__init__`, `browse_source`, `browse_key_file`, `_run`, `preview_import`, `perform_import`  
**Responsibility:** Preview and import a KeePassXC KDBX/XML source into an open vault.

<!-- symbol:keys_ng.gui.main:main.KeePassXCImportDialog.__init__ -->
#### `main.KeePassXCImportDialog.__init__`

**Kind:** function/method  
**Lines:** 369-405  
**Signature:** `def __init__(self, vault_obj: Vault, parent=None) -> None`  
**Purpose:** Internal helper implementing `__init__`.

**Direct calls observed in the function body:** `QCheckBox`, `QFormLayout`, `QHBoxLayout`, `QLabel`, `QLineEdit`, `QPushButton`, `QTextEdit`, `QVBoxLayout`, `QWidget`, `_`, `__init__`, `close_button.clicked.connect`, `form.addRow`, `import_button.clicked.connect`, `key_button.clicked.connect`, `key_layout.addWidget`, `key_layout.setContentsMargins`, `layout.addLayout`, `layout.addWidget`, `preview_button.clicked.connect`, `row.addStretch`, `row.addWidget`, `self.password_edit.setEchoMode`, `self.password_edit.setToolTip`, `self.report.setPlaceholderText`, `self.report.setReadOnly`, `self.resize`, `self.setWindowTitle`, `self.yubikey_edit.setPlaceholderText`, `source_button.clicked.connect`, `source_layout.addWidget`, `source_layout.setContentsMargins`, `super`.

**Object attributes written:** `self.key_file_edit`, `self.no_password`, `self.password_edit`, `self.report`, `self.source_edit`, `self.vault`, `self.yubikey_edit`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.KeePassXCImportDialog.browse_source -->
#### `main.KeePassXCImportDialog.browse_source`

**Kind:** function/method  
**Lines:** 407-409  
**Signature:** `def browse_source(self) -> None`  
**Purpose:** Implements the `browse_source` operation in this module.

**Direct calls observed in the function body:** `Path.home`, `QFileDialog.getOpenFileName`, `_`, `self.source_edit.setText`, `str`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.KeePassXCImportDialog.browse_key_file -->
#### `main.KeePassXCImportDialog.browse_key_file`

**Kind:** function/method  
**Lines:** 411-413  
**Signature:** `def browse_key_file(self) -> None`  
**Purpose:** Implements the `browse_key_file` operation in this module.

**Direct calls observed in the function body:** `Path.home`, `QFileDialog.getOpenFileName`, `_`, `self.key_file_edit.setText`, `str`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.KeePassXCImportDialog._run -->
#### `main.KeePassXCImportDialog._run`

**Kind:** function/method  
**Lines:** 415-425  
**Signature:** `def _run(self, dry_run: bool)`  
**Purpose:** Internal helper implementing `_run`.

**Direct calls observed in the function body:** `ValueError`, `_`, `import_keepassxc`, `self.key_file_edit.text`, `self.no_password.isChecked`, `self.password_edit.text`, `self.source_edit.text`, `self.yubikey_edit.text`, `strip`.

**Explicitly raised exceptions:** `ValueError`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.KeePassXCImportDialog.preview_import -->
#### `main.KeePassXCImportDialog.preview_import`

**Kind:** function/method  
**Lines:** 427-432  
**Signature:** `def preview_import(self) -> None`  
**Purpose:** Implements the `preview_import` operation in this module.

**Direct calls observed in the function body:** `QMessageBox.critical`, `_`, `format_import_report`, `self._run`, `self.report.setPlainText`, `str`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** process.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.KeePassXCImportDialog.perform_import -->
#### `main.KeePassXCImportDialog.perform_import`

**Kind:** function/method  
**Lines:** 434-443  
**Signature:** `def perform_import(self) -> None`  
**Purpose:** Implements the `perform_import` operation in this module.

**Direct calls observed in the function body:** `QMessageBox.critical`, `QMessageBox.information`, `QMessageBox.warning`, `_`, `format_import_report`, `self._run`, `self.accept`, `self.report.setPlainText`, `str`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** process.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.TrustedSignersDialog -->
#### `main.TrustedSignersDialog`

**Kind:** class  
**Lines:** 445-500  
**Bases:** `QDialog`  
**Methods:** `__init__`, `refresh`, `add_signer`, `remove_signer`  
**Responsibility:** Implements the `TrustedSignersDialog` operation in this module.

<!-- symbol:keys_ng.gui.main:main.TrustedSignersDialog.__init__ -->
#### `main.TrustedSignersDialog.__init__`

**Kind:** function/method  
**Lines:** 446-464  
**Signature:** `def __init__(self, vault: Vault, parent=None) -> None`  
**Purpose:** Internal helper implementing `__init__`.

**Direct calls observed in the function body:** `QHBoxLayout`, `QLabel`, `QListWidget`, `QPushButton`, `QVBoxLayout`, `_`, `__init__`, `add_button.clicked.connect`, `buttons.addStretch`, `buttons.addWidget`, `close_button.clicked.connect`, `layout.addLayout`, `layout.addWidget`, `remove_button.clicked.connect`, `self.refresh`, `self.resize`, `self.setWindowTitle`, `super`.

**Object attributes written:** `self.list`, `self.vault`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.TrustedSignersDialog.refresh -->
#### `main.TrustedSignersDialog.refresh`

**Kind:** function/method  
**Lines:** 466-471  
**Signature:** `def refresh(self) -> None`  
**Purpose:** Implements the `refresh` operation in this module.

**Direct calls observed in the function body:** `_`, `list_trusted_signers`, `self.list.addItem`, `self.list.clear`, `self.list.count`, `self.list.item`, `setData`.

**Control-flow shape:** 0 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.TrustedSignersDialog.add_signer -->
#### `main.TrustedSignersDialog.add_signer`

**Kind:** function/method  
**Lines:** 473-487  
**Signature:** `def add_signer(self) -> None`  
**Purpose:** Implements the `add_signer` operation in this module.

**Direct calls observed in the function body:** `QInputDialog.getItem`, `QMessageBox.information`, `QMessageBox.question`, `_`, `add_trusted_signer`, `eligible_signing_keys`, `format`, `labels.index`, `list_trusted_signers`, `self.refresh`.

**Control-flow shape:** 3 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 3 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.TrustedSignersDialog.remove_signer -->
#### `main.TrustedSignersDialog.remove_signer`

**Kind:** function/method  
**Lines:** 489-500  
**Signature:** `def remove_signer(self) -> None`  
**Purpose:** Implements the `remove_signer` operation in this module.

**Direct calls observed in the function body:** `QMessageBox.critical`, `QMessageBox.question`, `_`, `format`, `item.data`, `remove_trusted_signer`, `self.list.currentItem`, `self.refresh`, `str`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.InboxDialog -->
#### `main.InboxDialog`

**Kind:** class  
**Lines:** 503-614  
**Bases:** `QDialog`  
**Methods:** `__init__`, `_status_text`, `refresh`, `show_details`, `import_selected`, `import_all_trusted`, `authorize_selected`, `delete_selected`  
**Responsibility:** Implements the `InboxDialog` operation in this module.

<!-- symbol:keys_ng.gui.main:main.InboxDialog.__init__ -->
#### `main.InboxDialog.__init__`

**Kind:** function/method  
**Lines:** 504-534  
**Signature:** `def __init__(self, vault: Vault, parent=None) -> None`  
**Purpose:** Internal helper implementing `__init__`.

**Direct calls observed in the function body:** `QHBoxLayout`, `QLabel`, `QListWidget`, `QPushButton`, `QVBoxLayout`, `_`, `__init__`, `authorize_button.clicked.connect`, `close_button.clicked.connect`, `delete_button.clicked.connect`, `import_button.clicked.connect`, `import_trusted_button.clicked.connect`, `layout.addLayout`, `layout.addWidget`, `refresh_button.clicked.connect`, `row.addStretch`, `row.addWidget`, `self.details.setWordWrap`, `self.list.currentRowChanged.connect`, `self.refresh`, `self.resize`, `self.setWindowTitle`, `super`.

**Object attributes written:** `self.details`, `self.items`, `self.list`, `self.vault`.

**Control-flow shape:** 0 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.InboxDialog._status_text -->
#### `main.InboxDialog._status_text`

**Kind:** function/method  
**Lines:** 536-545  
**Signature:** `def _status_text(self, item) -> str`  
**Purpose:** Internal helper implementing `_status_text`.

**Direct calls observed in the function body:** `_`, `mapping.get`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.InboxDialog.refresh -->
#### `main.InboxDialog.refresh`

**Kind:** function/method  
**Lines:** 547-556  
**Signature:** `def refresh(self) -> None`  
**Purpose:** Implements the `refresh` operation in this module.

**Direct calls observed in the function body:** `_`, `inspect_inbox`, `self._status_text`, `self.details.setText`, `self.list.addItem`, `self.list.clear`, `self.list.setCurrentRow`.

**Object attributes written:** `self.items`.

**Control-flow shape:** 1 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.InboxDialog.show_details -->
#### `main.InboxDialog.show_details`

**Kind:** function/method  
**Lines:** 558-566  
**Signature:** `def show_details(self, row: int) -> None`  
**Purpose:** Implements the `show_details` operation in this module.

**Direct calls observed in the function body:** `_`, `format`, `len`, `self._status_text`, `self.details.clear`, `self.details.setText`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.InboxDialog.import_selected -->
#### `main.InboxDialog.import_selected`

**Kind:** function/method  
**Lines:** 568-581  
**Signature:** `def import_selected(self) -> None`  
**Purpose:** Imports `import_selected`.

**Direct calls observed in the function body:** `QMessageBox.critical`, `QMessageBox.warning`, `_`, `import_inbox_item`, `self.list.currentRow`, `self.refresh`, `str`.

**Control-flow shape:** 3 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.InboxDialog.import_all_trusted -->
#### `main.InboxDialog.import_all_trusted`

**Kind:** function/method  
**Lines:** 583-590  
**Signature:** `def import_all_trusted(self) -> None`  
**Purpose:** Imports `import_all_trusted`.

**Direct calls observed in the function body:** `QMessageBox.warning`, `_`, `failures.append`, `import_inbox_item`, `list`, `self.refresh`, `type`.

**Control-flow shape:** 2 conditional blocks, 1 loops, 1 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.InboxDialog.authorize_selected -->
#### `main.InboxDialog.authorize_selected`

**Kind:** function/method  
**Lines:** 592-604  
**Signature:** `def authorize_selected(self) -> None`  
**Purpose:** Implements the `authorize_selected` operation in this module.

**Direct calls observed in the function body:** `QMessageBox.critical`, `QMessageBox.information`, `QMessageBox.question`, `_`, `add_trusted_signer`, `format`, `self.list.currentRow`, `self.refresh`, `str`.

**Control-flow shape:** 3 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 3 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.InboxDialog.delete_selected -->
#### `main.InboxDialog.delete_selected`

**Kind:** function/method  
**Lines:** 606-614  
**Signature:** `def delete_selected(self) -> None`  
**Purpose:** Deletes `delete_selected`.

**Direct calls observed in the function body:** `QMessageBox.critical`, `QMessageBox.warning`, `_`, `delete_inbox_item`, `self.list.currentRow`, `self.refresh`, `str`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane -->
#### `main.VaultPane`

**Kind:** class  
**Lines:** 616-1075  
**Bases:** `QWidget`  
**Methods:** `__init__`, `display_name`, `status_message`, `focus_search`, `schedule_search`, `activity`, `_theme_icon`, `_folder_icon`, `_entry_icon`, `_folder_item`, `_entry_item`, `reload`, `select_item`, `clear_details`, `tree_move`, `request_hard_lock`, `lock`, `unlock`, `refresh_otp`, `copy_url_clicked`, `copy_uuid_clicked`, `copy_username_clicked`, `copy_password_clicked`, `copy_notes_clicked`, `copy_otp_clicked`, `open_action_clicked`, `export_entry_keepassxc`, `new_entry`, `edit_entry`, `delete_entry`, `new_folder`, `rename_folder`, `delete_folder`  
**Responsibility:** GUI state and widgets for exactly one independently locked vault tab.

<!-- symbol:keys_ng.gui.main:main.VaultPane.__init__ -->
#### `main.VaultPane.__init__`

**Kind:** function/method  
**Lines:** 617-728  
**Signature:** `def __init__(self, vault_path: str, parent=None) -> None`  
**Purpose:** Internal helper implementing `__init__`.

**Direct calls observed in the function body:** `Path`, `QHBoxLayout`, `QLabel`, `QLineEdit`, `QPushButton`, `QTextEdit`, `QTimer`, `QVBoxLayout`, `Vault`, `VaultTree`, `_`, `__init__`, `create_crypto_backend`, `expanduser`, `left.addLayout`, `left.addWidget`, `resolve`, `right.addStretch`, `right.addWidget`, `root_layout.addLayout`, `self.auto_lock_timer.setSingleShot`, `self.auto_lock_timer.start`, `self.auto_lock_timer.timeout.connect`, `self.copy_notes.clicked.connect`, `self.copy_otp.clicked.connect`, `self.copy_otp.setToolTip`, `self.copy_password.clicked.connect`, `self.copy_password.setToolTip`, `self.copy_url.clicked.connect`, `self.copy_url.setToolTip`, `self.copy_username.clicked.connect`, `self.copy_username.setToolTip`, `self.copy_uuid.clicked.connect`, `self.copy_uuid.setToolTip`, `self.delete_button.clicked.connect`, `self.delete_folder_button.clicked.connect`, `self.edit_button.clicked.connect`, `self.entries.currentItemChanged.connect`, `self.entries.itemDoubleClicked.connect`, `self.hard_lock_button.clicked.connect`, `self.lock`, `self.lock_button.clicked.connect`, `self.new_button.clicked.connect`, `self.new_folder_button.clicked.connect`, `self.notes.setMinimumHeight`, `self.notes.setReadOnly`, `self.notes.setToolTip`, `self.open_action.clicked.connect`, `self.open_action.setToolTip`, `self.open_action_clicked`, `self.reload`, `self.rename_folder_button.clicked.connect`, `self.search.setClearButtonEnabled`, `self.search.setPlaceholderText`, `self.search.setToolTip`, `self.search.textChanged.connect`, `self.search_timer.setInterval`, `self.search_timer.setSingleShot`, `self.search_timer.timeout.connect`, `self.setLayout`, `self.timer.start`, `self.timer.timeout.connect`, `self.unlock_button.clicked.connect`, `super`, `toolbar1.addWidget`, `toolbar2.addWidget`.

**Object attributes written:** `self.auto_lock_timer`, `self.copy_notes`, `self.copy_otp`, `self.copy_password`, `self.copy_url`, `self.copy_username`, `self.copy_uuid`, `self.current_entry`, `self.current_folder_id`, `self.current_id`, `self.delete_button`, `self.delete_folder_button`, `self.edit_button`, `self.entries`, `self.hard_lock_button`, `self.lock_button`, `self.new_button`, `self.new_folder_button`, `self.notes`, `self.open_action`, `self.otp`, `self.path_label`, `self.rename_folder_button`, `self.search`, `self.search_timer`, `self.timer`, `self.title`, `self.unlock_button`, `self.username`, `self.uuid_label`, `self.vault`, `self.vault_path`.

**Control-flow shape:** 1 conditional blocks, 2 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** filesystem, cryptography/key-agent.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.display_name -->
#### `main.VaultPane.display_name`

**Kind:** function/method  
**Lines:** 731-732  
**Signature:** `def display_name(self) -> str`  
**Purpose:** Implements the `display_name` operation in this module.

**Direct calls observed in the function body:** `str`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.status_message -->
#### `main.VaultPane.status_message`

**Kind:** function/method  
**Lines:** 734-737  
**Signature:** `def status_message(self, message: str, timeout: int=0) -> None`  
**Purpose:** Implements the `status_message` operation in this module.

**Direct calls observed in the function body:** `hasattr`, `self.window`, `showMessage`, `window.statusBar`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.focus_search -->
#### `main.VaultPane.focus_search`

**Kind:** function/method  
**Lines:** 739-742  
**Signature:** `def focus_search(self) -> None`  
**Purpose:** Implements the `focus_search` operation in this module.

**Direct calls observed in the function body:** `self.activity`, `self.search.selectAll`, `self.search.setFocus`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.schedule_search -->
#### `main.VaultPane.schedule_search`

**Kind:** function/method  
**Lines:** 744-746  
**Signature:** `def schedule_search(self) -> None`  
**Purpose:** Implements the `schedule_search` operation in this module.

**Direct calls observed in the function body:** `self.activity`, `self.search_timer.start`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.activity -->
#### `main.VaultPane.activity`

**Kind:** function/method  
**Lines:** 748-750  
**Signature:** `def activity(self) -> None`  
**Purpose:** Implements the `activity` operation in this module.

**Direct calls observed in the function body:** `self.auto_lock_timer.start`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane._theme_icon -->
#### `main.VaultPane._theme_icon`

**Kind:** function/method  
**Lines:** 752-757  
**Signature:** `def _theme_icon(self, names: tuple[str, ...], fallback) -> QIcon`  
**Purpose:** Internal helper implementing `_theme_icon`.

**Direct calls observed in the function body:** `QIcon.fromTheme`, `icon.isNull`, `self.style`, `standardIcon`.

**Control-flow shape:** 1 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane._folder_icon -->
#### `main.VaultPane._folder_icon`

**Kind:** function/method  
**Lines:** 759-760  
**Signature:** `def _folder_icon(self) -> QIcon`  
**Purpose:** Internal helper implementing `_folder_icon`.

**Direct calls observed in the function body:** `self._theme_icon`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane._entry_icon -->
#### `main.VaultPane._entry_icon`

**Kind:** function/method  
**Lines:** 762-772  
**Signature:** `def _entry_icon(self, catalog_item) -> QIcon`  
**Purpose:** Internal helper implementing `_entry_icon`.

**Direct calls observed in the function body:** `self._theme_icon`, `set`.

**Control-flow shape:** 4 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 5 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane._folder_item -->
#### `main.VaultPane._folder_item`

**Kind:** function/method  
**Lines:** 774-784  
**Signature:** `def _folder_item(self, folder, parent=None)`  
**Purpose:** Internal helper implementing `_folder_item`.

**Direct calls observed in the function body:** `QTreeWidgetItem`, `item.flags`, `item.setData`, `item.setFlags`, `item.setIcon`, `parent.addChild`, `self._folder_icon`, `self.entries.addTopLevelItem`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane._entry_item -->
#### `main.VaultPane._entry_item`

**Kind:** function/method  
**Lines:** 786-797  
**Signature:** `def _entry_item(self, catalog_item, parent=None, suffix='')`  
**Purpose:** Internal helper implementing `_entry_item`.

**Direct calls observed in the function body:** `QTreeWidgetItem`, `item.flags`, `item.setData`, `item.setFlags`, `item.setIcon`, `parent.addChild`, `self._entry_icon`, `self.entries.addTopLevelItem`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.reload -->
#### `main.VaultPane.reload`

**Kind:** function/method  
**Lines:** 799-833  
**Signature:** `def reload(self) -> None`  
**Purpose:** Implements the `reload` operation in this module.

**Direct calls observed in the function body:** `QMessageBox.critical`, `_`, `bool`, `folder_widgets.get`, `list`, `paths.get`, `remaining.remove`, `self._entry_item`, `self._folder_item`, `self.entries.clear`, `self.entries.collapseAll`, `self.entries.expandAll`, `self.entries.setDragEnabled`, `self.search.text`, `self.vault.folder_paths`, `self.vault.list_folders`, `self.vault.list_items`, `self.vault.search`, `str`, `strip`.

**Control-flow shape:** 5 conditional blocks, 4 loops, 1 try blocks, 0 context managers, 3 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.select_item -->
#### `main.VaultPane.select_item`

**Kind:** function/method  
**Lines:** 835-876  
**Signature:** `def select_item(self, current, _previous) -> None`  
**Purpose:** Implements the `select_item` operation in this module.

**Direct calls observed in the function body:** `QMessageBox.critical`, `_`, `current.data`, `current.text`, `elapsed_ms`, `log.debug`, `log.error`, `log.info`, `self.activity`, `self.notes.clear`, `self.notes.setText`, `self.otp.clear`, `self.path_label.setText`, `self.refresh_otp`, `self.title.setText`, `self.username.clear`, `self.username.setText`, `self.uuid_label.clear`, `self.uuid_label.setText`, `self.vault.folder_path`, `self.vault.get_entry`, `self.vault.resolved_username`, `str`, `time.perf_counter`, `type`.

**Object attributes written:** `self.current_entry`, `self.current_folder_id`, `self.current_id`.

**Control-flow shape:** 3 conditional blocks, 0 loops, 2 try blocks, 0 context managers, 3 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.clear_details -->
#### `main.VaultPane.clear_details`

**Kind:** function/method  
**Lines:** 878-883  
**Signature:** `def clear_details(self) -> None`  
**Purpose:** Implements the `clear_details` operation in this module.

**Direct calls observed in the function body:** `self.entries.clear`, `self.notes.clear`, `self.otp.clear`, `self.path_label.clear`, `self.title.clear`, `self.username.clear`, `self.uuid_label.clear`.

**Object attributes written:** `self.current_entry`, `self.current_folder_id`, `self.current_id`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.tree_move -->
#### `main.VaultPane.tree_move`

**Kind:** function/method  
**Lines:** 885-891  
**Signature:** `def tree_move(self, item_type: str, item_id: str, parent_id: str | None) -> None`  
**Purpose:** Implements the `tree_move` operation in this module.

**Direct calls observed in the function body:** `self.search.text`, `self.vault.move_entry`, `self.vault.move_folder`, `strip`.

**Control-flow shape:** 3 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.request_hard_lock -->
#### `main.VaultPane.request_hard_lock`

**Kind:** function/method  
**Lines:** 893-898  
**Signature:** `def request_hard_lock(self) -> None`  
**Purpose:** Implements the `request_hard_lock` operation in this module.

**Direct calls observed in the function body:** `hasattr`, `self.lock`, `self.window`, `window.hard_lock_all`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** cryptography/key-agent.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.lock -->
#### `main.VaultPane.lock`

**Kind:** function/method  
**Lines:** 900-907  
**Signature:** `def lock(self, hard: bool) -> None`  
**Purpose:** Implements the `lock` operation in this module.

**Direct calls observed in the function body:** `QApplication.clipboard`, `QMessageBox.critical`, `_`, `clear`, `self.clear_details`, `self.status_message`, `self.vault.lock`, `str`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** clipboard.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.unlock -->
#### `main.VaultPane.unlock`

**Kind:** function/method  
**Lines:** 909-916  
**Signature:** `def unlock(self) -> None`  
**Purpose:** Implements the `unlock` operation in this module.

**Direct calls observed in the function body:** `QMessageBox.critical`, `_`, `self.activity`, `self.reload`, `self.status_message`, `self.vault.unlock`, `str`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.refresh_otp -->
#### `main.VaultPane.refresh_otp`

**Kind:** function/method  
**Lines:** 918-923  
**Signature:** `def refresh_otp(self) -> None`  
**Purpose:** Implements the `refresh_otp` operation in this module.

**Direct calls observed in the function body:** `generate_totp`, `self.otp.setText`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.copy_url_clicked -->
#### `main.VaultPane.copy_url_clicked`

**Kind:** function/method  
**Lines:** 925-932  
**Signature:** `def copy_url_clicked(self) -> None`  
**Purpose:** Copies a value using `copy_url_clicked`.

**Direct calls observed in the function body:** `_`, `copy_secret_qt`, `next`, `self.activity`, `self.status_message`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.copy_uuid_clicked -->
#### `main.VaultPane.copy_uuid_clicked`

**Kind:** function/method  
**Lines:** 934-938  
**Signature:** `def copy_uuid_clicked(self) -> None`  
**Purpose:** Copies a value using `copy_uuid_clicked`.

**Direct calls observed in the function body:** `_`, `copy_secret_qt`, `self.activity`, `self.status_message`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.copy_username_clicked -->
#### `main.VaultPane.copy_username_clicked`

**Kind:** function/method  
**Lines:** 940-950  
**Signature:** `def copy_username_clicked(self) -> None`  
**Purpose:** Copies a value using `copy_username_clicked`.

**Direct calls observed in the function body:** `QMessageBox.critical`, `_`, `copy_secret_qt`, `self.activity`, `self.status_message`, `self.vault.resolved_username`, `str`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.copy_password_clicked -->
#### `main.VaultPane.copy_password_clicked`

**Kind:** function/method  
**Lines:** 952-961  
**Signature:** `def copy_password_clicked(self) -> None`  
**Purpose:** Copies a value using `copy_password_clicked`.

**Direct calls observed in the function body:** `QMessageBox.critical`, `_`, `copy_secret_qt`, `self.activity`, `self.vault.resolved_password`, `str`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.copy_notes_clicked -->
#### `main.VaultPane.copy_notes_clicked`

**Kind:** function/method  
**Lines:** 963-967  
**Signature:** `def copy_notes_clicked(self) -> None`  
**Purpose:** Copies a value using `copy_notes_clicked`.

**Direct calls observed in the function body:** `_`, `copy_secret_qt`, `self.activity`, `self.status_message`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.copy_otp_clicked -->
#### `main.VaultPane.copy_otp_clicked`

**Kind:** function/method  
**Lines:** 969-973  
**Signature:** `def copy_otp_clicked(self) -> None`  
**Purpose:** Copies a value using `copy_otp_clicked`.

**Direct calls observed in the function body:** `copy_secret_qt`, `generate_totp`, `self.activity`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.open_action_clicked -->
#### `main.VaultPane.open_action_clicked`

**Kind:** function/method  
**Lines:** 975-981  
**Signature:** `def open_action_clicked(self) -> None`  
**Purpose:** Implements the `open_action_clicked` operation in this module.

**Direct calls observed in the function body:** `QMessageBox.critical`, `_`, `launch_action`, `self.activity`, `self.vault.resolved_action`, `str`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.export_entry_keepassxc -->
#### `main.VaultPane.export_entry_keepassxc`

**Kind:** function/method  
**Lines:** 983-1002  
**Signature:** `def export_entry_keepassxc(self) -> None`  
**Purpose:** Exports `export_entry_keepassxc`.

**Direct calls observed in the function body:** `QFileDialog.getSaveFileName`, `QMessageBox.critical`, `QMessageBox.warning`, `_`, `ch.isalnum`, `export_entry_xml`, `join`, `self.activity`, `self.status_message`, `str`, `strip`, `write_export`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.new_entry -->
#### `main.VaultPane.new_entry`

**Kind:** function/method  
**Lines:** 1004-1014  
**Signature:** `def new_entry(self) -> None`  
**Purpose:** Implements the `new_entry` operation in this module.

**Direct calls observed in the function body:** `EntryDialog`, `QMessageBox.critical`, `_`, `dialog.build_entry`, `dialog.exec`, `self.activity`, `self.reload`, `self.vault.save_entry`, `str`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.edit_entry -->
#### `main.VaultPane.edit_entry`

**Kind:** function/method  
**Lines:** 1016-1026  
**Signature:** `def edit_entry(self) -> None`  
**Purpose:** Implements the `edit_entry` operation in this module.

**Direct calls observed in the function body:** `EntryDialog`, `QMessageBox.critical`, `_`, `dialog.build_entry`, `dialog.exec`, `self.activity`, `self.reload`, `self.vault.save_entry`, `str`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.delete_entry -->
#### `main.VaultPane.delete_entry`

**Kind:** function/method  
**Lines:** 1028-1039  
**Signature:** `def delete_entry(self) -> None`  
**Purpose:** Deletes `delete_entry`.

**Direct calls observed in the function body:** `QMessageBox.critical`, `QMessageBox.question`, `_`, `self.activity`, `self.clear_details`, `self.reload`, `self.vault.delete_entry`, `str`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.new_folder -->
#### `main.VaultPane.new_folder`

**Kind:** function/method  
**Lines:** 1041-1051  
**Signature:** `def new_folder(self) -> None`  
**Purpose:** Implements the `new_folder` operation in this module.

**Direct calls observed in the function body:** `QInputDialog.getText`, `QMessageBox.critical`, `_`, `name.strip`, `self.activity`, `self.reload`, `self.vault.create_folder`, `str`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.rename_folder -->
#### `main.VaultPane.rename_folder`

**Kind:** function/method  
**Lines:** 1053-1063  
**Signature:** `def rename_folder(self) -> None`  
**Purpose:** Implements the `rename_folder` operation in this module.

**Direct calls observed in the function body:** `QInputDialog.getText`, `QMessageBox.critical`, `_`, `name.strip`, `self.reload`, `self.vault.get_folder`, `self.vault.rename_folder`, `str`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.VaultPane.delete_folder -->
#### `main.VaultPane.delete_folder`

**Kind:** function/method  
**Lines:** 1065-1075  
**Signature:** `def delete_folder(self) -> None`  
**Purpose:** Deletes `delete_folder`.

**Direct calls observed in the function body:** `QMessageBox.critical`, `QMessageBox.question`, `_`, `self.clear_details`, `self.reload`, `self.vault.delete_folder`, `str`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.NewVaultWizard -->
#### `main.NewVaultWizard`

**Kind:** class  
**Lines:** 1078-1169  
**Bases:** `QWizard`  
**Methods:** `__init__`, `_browse`, `_update_summary`, `request`  
**Responsibility:** Guided vault creation using the same initialization service as the CLI.

<!-- symbol:keys_ng.gui.main:main.NewVaultWizard.__init__ -->
#### `main.NewVaultWizard.__init__`

**Kind:** function/method  
**Lines:** 1081-1138  
**Signature:** `def __init__(self, crypto, parent=None) -> None`  
**Purpose:** Internal helper implementing `__init__`.

**Direct calls observed in the function body:** `QCheckBox`, `QComboBox`, `QFormLayout`, `QHBoxLayout`, `QLabel`, `QLineEdit`, `QPushButton`, `QVBoxLayout`, `QWizardPage`, `_`, `__init__`, `available_vault_keys`, `browse.clicked.connect`, `keys_form.addRow`, `keys_page.setSubTitle`, `keys_page.setTitle`, `location.setSubTitle`, `location.setTitle`, `location_layout.addLayout`, `options.setSubTitle`, `options.setTitle`, `options_form.addRow`, `row.addWidget`, `self.addPage`, `self.currentIdChanged.connect`, `self.privacy_combo.addItem`, `self.privacy_combo.setCurrentIndex`, `self.recipient_combo.addItem`, `self.require_signature.setChecked`, `self.resize`, `self.setWindowTitle`, `self.signer_combo.addItem`, `self.summary_label.setWordWrap`, `summary.setSubTitle`, `summary.setTitle`, `summary_layout.addWidget`, `super`.

**Object attributes written:** `self._choices`, `self.crypto`, `self.path_edit`, `self.privacy_combo`, `self.recipient_combo`, `self.require_signature`, `self.signer_combo`, `self.summary_label`.

**Control-flow shape:** 0 conditional blocks, 2 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.NewVaultWizard._browse -->
#### `main.NewVaultWizard._browse`

**Kind:** function/method  
**Lines:** 1140-1144  
**Signature:** `def _browse(self) -> None`  
**Purpose:** Internal helper implementing `_browse`.

**Direct calls observed in the function body:** `Path.home`, `QFileDialog.getExistingDirectory`, `_`, `self.path_edit.setText`, `str`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.NewVaultWizard._update_summary -->
#### `main.NewVaultWizard._update_summary`

**Kind:** function/method  
**Lines:** 1146-1154  
**Signature:** `def _update_summary(self, _page_id: int) -> None`  
**Purpose:** Internal helper implementing `_update_summary`.

**Direct calls observed in the function body:** `_`, `self.path_edit.text`, `self.privacy_combo.currentData`, `self.recipient_combo.currentData`, `self.signer_combo.currentData`, `self.summary_label.setText`, `str`, `strip`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.NewVaultWizard.request -->
#### `main.NewVaultWizard.request`

**Kind:** function/method  
**Lines:** 1156-1169  
**Signature:** `def request(self) -> VaultInitRequest`  
**Purpose:** Implements the `request` operation in this module.

**Direct calls observed in the function body:** `ValueError`, `VaultInitRequest`, `_`, `self.path_edit.text`, `self.privacy_combo.currentData`, `self.recipient_combo.currentData`, `self.require_signature.isChecked`, `self.signer_combo.currentData`, `str`, `strip`.

**Explicitly raised exceptions:** `ValueError`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.SettingsDialog -->
#### `main.SettingsDialog`

**Kind:** class  
**Lines:** 1172-1337  
**Bases:** `QDialog`  
**Methods:** `__init__`, `_lines`, `_verify_gnupg`, `apply`  
**Responsibility:** Edit the global Keys NG config.toml without exposing TOML syntax.

<!-- symbol:keys_ng.gui.main:main.SettingsDialog.__init__ -->
#### `main.SettingsDialog.__init__`

**Kind:** function/method  
**Lines:** 1175-1298  
**Signature:** `def __init__(self, app_settings: AppSettings, parent=None) -> None`  
**Purpose:** Internal helper implementing `__init__`.

**Direct calls observed in the function body:** `QComboBox`, `QDialogButtonBox`, `QDoubleSpinBox`, `QFormLayout`, `QLabel`, `QLineEdit`, `QPushButton`, `QSpinBox`, `QTabWidget`, `QTextEdit`, `QVBoxLayout`, `QWidget`, `_`, `__init__`, `buttons.accepted.connect`, `buttons.rejected.connect`, `clipboard_form.addRow`, `general_form.addRow`, `help_label`, `join`, `label.setStyleSheet`, `label.setWordWrap`, `layout.addWidget`, `max`, `rdp_form.addRow`, `self.auto_lock_spin.setRange`, `self.auto_lock_spin.setSuffix`, `self.auto_lock_spin.setValue`, `self.crypto_combo.addItem`, `self.crypto_combo.findData`, `self.crypto_combo.setCurrentIndex`, `self.gpg_path_edit.setPlaceholderText`, `self.gpgconf_path_edit.setPlaceholderText`, `self.language_combo.addItem`, `self.language_combo.findData`, `self.language_combo.setCurrentIndex`, `self.password_timeout_spin.setRange`, `self.password_timeout_spin.setSuffix`, `self.password_timeout_spin.setValue`, `self.rdp_linux_options_edit.setMaximumHeight`, `self.rdp_linux_options_edit.setPlainText`, `self.rdp_macos_options_edit.setMaximumHeight`, `self.rdp_macos_options_edit.setPlainText`, `self.rdp_windows_options_edit.setMaximumHeight`, `self.rdp_windows_options_edit.setPlainText`, `self.resize`, `self.setWindowTitle`, `self.ssh_options_edit.setMaximumHeight`, `self.ssh_options_edit.setPlainText`, `self.totp_timeout_spin.setRange`, `self.totp_timeout_spin.setSuffix`, `self.totp_timeout_spin.setValue`, `self.tree_combo.addItem`, `self.tree_combo.findData`, `self.tree_combo.setCurrentIndex`, `self.tui_notice_background_edit.setPlaceholderText`, `self.tui_notice_foreground_edit.setPlaceholderText`, `self.tui_notice_seconds_spin.setRange`, `self.tui_notice_seconds_spin.setSingleStep`, `self.tui_notice_seconds_spin.setSuffix`, `self.tui_notice_seconds_spin.setValue`, `ssh_form.addRow`, `super`, `tabs.addTab`, `verify_gpg.clicked.connect`.

**Object attributes written:** `self.app_settings`, `self.auto_lock_spin`, `self.crypto_combo`, `self.gpg_path_edit`, `self.gpgconf_path_edit`, `self.language_combo`, `self.password_timeout_spin`, `self.rdp_linux_client_edit`, `self.rdp_linux_options_edit`, `self.rdp_macos_client_edit`, `self.rdp_macos_options_edit`, `self.rdp_windows_client_edit`, `self.rdp_windows_options_edit`, `self.ssh_options_edit`, `self.ssh_terminal_edit`, `self.totp_timeout_spin`, `self.tree_combo`, `self.tui_notice_background_edit`, `self.tui_notice_foreground_edit`, `self.tui_notice_seconds_spin`.

**Control-flow shape:** 0 conditional blocks, 2 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** clipboard.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.SettingsDialog.__init__.help_label -->
#### `main.SettingsDialog.__init__.help_label`

**Kind:** function/method  
**Lines:** 1184-1188  
**Signature:** `def help_label(text: str) -> QLabel`  
**Purpose:** Implements the `help_label` operation in this module.

**Direct calls observed in the function body:** `QLabel`, `label.setStyleSheet`, `label.setWordWrap`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.SettingsDialog._lines -->
#### `main.SettingsDialog._lines`

**Kind:** function/method  
**Lines:** 1301-1302  
**Signature:** `def _lines(widget: QTextEdit) -> list[str]`  
**Purpose:** Internal helper implementing `_lines`.

**Direct calls observed in the function body:** `line.strip`, `splitlines`, `widget.toPlainText`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** parser/serialization.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.SettingsDialog._verify_gnupg -->
#### `main.SettingsDialog._verify_gnupg`

**Kind:** function/method  
**Lines:** 1304-1314  
**Signature:** `def _verify_gnupg(self) -> None`  
**Purpose:** Internal helper implementing `_verify_gnupg`.

**Direct calls observed in the function body:** `QMessageBox.critical`, `QMessageBox.information`, `_`, `backend.diagnose`, `create_crypto_backend`, `join`, `self.gpg_path_edit.text`, `self.gpgconf_path_edit.text`, `str`, `strip`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.SettingsDialog.apply -->
#### `main.SettingsDialog.apply`

**Kind:** function/method  
**Lines:** 1316-1337  
**Signature:** `def apply(self) -> None`  
**Purpose:** Implements the `apply` operation in this module.

**Direct calls observed in the function body:** `float`, `s.save`, `self._lines`, `self.auto_lock_spin.value`, `self.crypto_combo.currentData`, `self.gpg_path_edit.text`, `self.gpgconf_path_edit.text`, `self.language_combo.currentData`, `self.password_timeout_spin.value`, `self.rdp_linux_client_edit.text`, `self.rdp_macos_client_edit.text`, `self.rdp_windows_client_edit.text`, `self.ssh_terminal_edit.text`, `self.totp_timeout_spin.value`, `self.tree_combo.currentData`, `self.tui_notice_background_edit.text`, `self.tui_notice_foreground_edit.text`, `self.tui_notice_seconds_spin.value`, `str`, `strip`.

**Object attributes written:** `s.auto_lock_timeout`, `s.clipboard_password_timeout`, `s.clipboard_totp_timeout`, `s.crypto_backend`, `s.gpg_executable`, `s.gpgconf_executable`, `s.language`, `s.rdp_linux_client`, `s.rdp_linux_options`, `s.rdp_macos_client`, `s.rdp_macos_options`, `s.rdp_windows_client`, `s.rdp_windows_options`, `s.ssh_terminal`, `s.ssh_terminal_options`, `s.tree_startup_view`, `s.tui_clipboard_notice_background`, `s.tui_clipboard_notice_foreground`, `s.tui_clipboard_notice_seconds`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.MainWindow -->
#### `main.MainWindow`

**Kind:** class  
**Lines:** 1339-1624  
**Bases:** `QMainWindow`  
**Methods:** `__init__`, `_menu_action`, `build_menus`, `copy_context_or_password`, `show_keepassxc_import`, `export_vault_keepassxc`, `show_inbox`, `show_trusted_signers`, `show_preferences`, `refresh_recent_menu`, `show_help`, `active_pane`, `call_active`, `_sync_empty_state`, `update_window_title`, `create_vault_wizard`, `open_vault_dialog`, `open_vault`, `close_current_vault`, `close_vault`, `hard_lock_all`  
**Responsibility:** Top-level GUI window coordinating multiple VaultPane instances.

<!-- symbol:keys_ng.gui.main:main.MainWindow.__init__ -->
#### `main.MainWindow.__init__`

**Kind:** function/method  
**Lines:** 1340-1395  
**Signature:** `def __init__(self, initial_vaults: list[str]) -> None`  
**Purpose:** Internal helper implementing `__init__`.

**Direct calls observed in the function body:** `QKeySequence`, `QLabel`, `QPushButton`, `QShortcut`, `QStackedWidget`, `QTabWidget`, `QVBoxLayout`, `QWidget`, `_`, `__init__`, `create_button.clicked.connect`, `empty_label.setAlignment`, `empty_layout.addStretch`, `empty_layout.addWidget`, `open_button.clicked.connect`, `self._sync_empty_state`, `self.build_menus`, `self.call_active`, `self.open_vault`, `self.setCentralWidget`, `self.setWindowTitle`, `self.shortcuts.append`, `self.stack.addWidget`, `self.tabs.currentChanged.connect`, `self.tabs.setMovable`, `self.tabs.setTabPosition`, `self.tabs.setTabsClosable`, `self.tabs.tabCloseRequested.connect`, `shortcut.activated.connect`, `shortcut.setContext`, `super`.

**Object attributes written:** `self.empty_page`, `self.shortcuts`, `self.stack`, `self.tabs`.

**Control-flow shape:** 0 conditional blocks, 2 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.MainWindow._menu_action -->
#### `main.MainWindow._menu_action`

**Kind:** function/method  
**Lines:** 1397-1401  
**Signature:** `def _menu_action(self, menu, label: str, callback, shortcut_text: str | None=None)`  
**Purpose:** Internal helper implementing `_menu_action`.

**Direct calls observed in the function body:** `action.triggered.connect`, `menu.addAction`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.MainWindow.build_menus -->
#### `main.MainWindow.build_menus`

**Kind:** function/method  
**Lines:** 1403-1450  
**Signature:** `def build_menus(self) -> None`  
**Purpose:** Builds `build_menus`.

**Direct calls observed in the function body:** `_`, `addMenu`, `entry_menu.addSeparator`, `preferences_action.setMenuRole`, `self._menu_action`, `self.call_active`, `self.menuBar`, `self.recent_menu.aboutToShow.connect`, `self.refresh_recent_menu`, `self.show_help`, `vault_menu.addMenu`, `vault_menu.addSeparator`.

**Object attributes written:** `self.recent_menu`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.MainWindow.copy_context_or_password -->
#### `main.MainWindow.copy_context_or_password`

**Kind:** function/method  
**Lines:** 1452-1458  
**Signature:** `def copy_context_or_password(self) -> None`  
**Purpose:** Copies a value using `copy_context_or_password`.

**Direct calls observed in the function body:** `QApplication.focusWidget`, `focus.copy`, `focus.hasSelectedText`, `focus.textCursor`, `hasSelection`, `isinstance`, `self.call_active`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.MainWindow.show_keepassxc_import -->
#### `main.MainWindow.show_keepassxc_import`

**Kind:** function/method  
**Lines:** 1460-1466  
**Signature:** `def show_keepassxc_import(self) -> None`  
**Purpose:** Implements the `show_keepassxc_import` operation in this module.

**Direct calls observed in the function body:** `KeePassXCImportDialog`, `_`, `dialog.exec`, `pane.reload`, `self.active_pane`, `self.statusBar`, `showMessage`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.MainWindow.export_vault_keepassxc -->
#### `main.MainWindow.export_vault_keepassxc`

**Kind:** function/method  
**Lines:** 1468-1479  
**Signature:** `def export_vault_keepassxc(self) -> None`  
**Purpose:** Exports `export_vault_keepassxc`.

**Direct calls observed in the function body:** `QFileDialog.getSaveFileName`, `QMessageBox.critical`, `QMessageBox.warning`, `_`, `export_vault_xml`, `self.active_pane`, `self.statusBar`, `showMessage`, `str`, `write_export`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.MainWindow.show_inbox -->
#### `main.MainWindow.show_inbox`

**Kind:** function/method  
**Lines:** 1481-1485  
**Signature:** `def show_inbox(self) -> None`  
**Purpose:** Implements the `show_inbox` operation in this module.

**Direct calls observed in the function body:** `InboxDialog`, `exec`, `pane.reload`, `self.active_pane`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.MainWindow.show_trusted_signers -->
#### `main.MainWindow.show_trusted_signers`

**Kind:** function/method  
**Lines:** 1487-1490  
**Signature:** `def show_trusted_signers(self) -> None`  
**Purpose:** Implements the `show_trusted_signers` operation in this module.

**Direct calls observed in the function body:** `TrustedSignersDialog`, `exec`, `self.active_pane`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.MainWindow.show_preferences -->
#### `main.MainWindow.show_preferences`

**Kind:** function/method  
**Lines:** 1492-1504  
**Signature:** `def show_preferences(self) -> None`  
**Purpose:** Implements the `show_preferences` operation in this module.

**Direct calls observed in the function body:** `QMessageBox.critical`, `SettingsDialog`, `_`, `dialog.apply`, `dialog.exec`, `isinstance`, `pane.reset_auto_lock_timer`, `range`, `self.statusBar`, `self.tabs.count`, `self.tabs.widget`, `showMessage`, `str`.

**Control-flow shape:** 2 conditional blocks, 1 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.MainWindow.refresh_recent_menu -->
#### `main.MainWindow.refresh_recent_menu`

**Kind:** function/method  
**Lines:** 1506-1518  
**Signature:** `def refresh_recent_menu(self) -> None`  
**Purpose:** Implements the `refresh_recent_menu` operation in this module.

**Direct calls observed in the function body:** `Path`, `_`, `action.setEnabled`, `action.setToolTip`, `action.triggered.connect`, `list`, `self.open_vault`, `self.recent_menu.addAction`, `self.recent_menu.clear`, `str`.

**Control-flow shape:** 1 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.MainWindow.show_help -->
#### `main.MainWindow.show_help`

**Kind:** function/method  
**Lines:** 1520-1521  
**Signature:** `def show_help(self, tab: int=0) -> None`  
**Purpose:** Implements the `show_help` operation in this module.

**Direct calls observed in the function body:** `HelpDialog`, `exec`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.MainWindow.active_pane -->
#### `main.MainWindow.active_pane`

**Kind:** function/method  
**Lines:** 1523-1525  
**Signature:** `def active_pane(self) -> VaultPane | None`  
**Purpose:** Implements the `active_pane` operation in this module.

**Direct calls observed in the function body:** `isinstance`, `self.tabs.currentWidget`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.MainWindow.call_active -->
#### `main.MainWindow.call_active`

**Kind:** function/method  
**Lines:** 1527-1531  
**Signature:** `def call_active(self, method: str, *args) -> None`  
**Purpose:** Implements the `call_active` operation in this module.

**Direct calls observed in the function body:** `getattr`, `self.active_pane`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.MainWindow._sync_empty_state -->
#### `main.MainWindow._sync_empty_state`

**Kind:** function/method  
**Lines:** 1533-1535  
**Signature:** `def _sync_empty_state(self) -> None`  
**Purpose:** Internal helper implementing `_sync_empty_state`.

**Direct calls observed in the function body:** `self.stack.setCurrentWidget`, `self.tabs.count`, `self.update_window_title`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.MainWindow.update_window_title -->
#### `main.MainWindow.update_window_title`

**Kind:** function/method  
**Lines:** 1537-1539  
**Signature:** `def update_window_title(self, _index: int | None=None) -> None`  
**Purpose:** Implements the `update_window_title` operation in this module.

**Direct calls observed in the function body:** `self.active_pane`, `self.setWindowTitle`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.MainWindow.create_vault_wizard -->
#### `main.MainWindow.create_vault_wizard`

**Kind:** function/method  
**Lines:** 1541-1553  
**Signature:** `def create_vault_wizard(self) -> None`  
**Purpose:** Creates `create_vault_wizard`.

**Direct calls observed in the function body:** `NewVaultWizard`, `QMessageBox.critical`, `_`, `create_crypto_backend`, `create_vault`, `self.open_vault`, `self.statusBar`, `showMessage`, `str`, `wizard.exec`, `wizard.request`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.MainWindow.open_vault_dialog -->
#### `main.MainWindow.open_vault_dialog`

**Kind:** function/method  
**Lines:** 1555-1558  
**Signature:** `def open_vault_dialog(self) -> None`  
**Purpose:** Implements the `open_vault_dialog` operation in this module.

**Direct calls observed in the function body:** `Path.home`, `QFileDialog.getExistingDirectory`, `_`, `self.open_vault`, `str`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.MainWindow.open_vault -->
#### `main.MainWindow.open_vault`

**Kind:** function/method  
**Lines:** 1560-1591  
**Signature:** `def open_vault(self, path: str) -> None`  
**Purpose:** Implements the `open_vault` operation in this module.

**Direct calls observed in the function body:** `Path`, `QMessageBox.critical`, `QMessageBox.information`, `VaultPane`, `_`, `expanduser`, `format`, `isinstance`, `len`, `pending_inbox_paths`, `range`, `resolve`, `self._sync_empty_state`, `self.refresh_recent_menu`, `self.show_inbox`, `self.tabs.addTab`, `self.tabs.count`, `self.tabs.setCurrentIndex`, `self.tabs.setTabToolTip`, `self.tabs.widget`, `settings.remember_vault`, `settings.save`, `str`.

**Control-flow shape:** 3 conditional blocks, 1 loops, 2 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.MainWindow.close_current_vault -->
#### `main.MainWindow.close_current_vault`

**Kind:** function/method  
**Lines:** 1593-1596  
**Signature:** `def close_current_vault(self) -> None`  
**Purpose:** Implements the `close_current_vault` operation in this module.

**Direct calls observed in the function body:** `self.close_vault`, `self.tabs.currentIndex`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.MainWindow.close_vault -->
#### `main.MainWindow.close_vault`

**Kind:** function/method  
**Lines:** 1598-1609  
**Signature:** `def close_vault(self, index: int) -> None`  
**Purpose:** Implements the `close_vault` operation in this module.

**Direct calls observed in the function body:** `isinstance`, `pane.clear_details`, `pane.deleteLater`, `pane.vault.lock`, `self._sync_empty_state`, `self.tabs.removeTab`, `self.tabs.widget`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.gui.main:main.MainWindow.hard_lock_all -->
#### `main.MainWindow.hard_lock_all`

**Kind:** function/method  
**Lines:** 1611-1624  
**Signature:** `def hard_lock_all(self) -> None`  
**Purpose:** Implements the `hard_lock_all` operation in this module.

**Direct calls observed in the function body:** `QApplication.clipboard`, `QMessageBox.critical`, `_`, `clear`, `isinstance`, `pane.clear_details`, `pane.vault.lock`, `range`, `self.statusBar`, `self.tabs.count`, `self.tabs.widget`, `showMessage`, `str`, `vault.crypto.hard_lock`.

**Control-flow shape:** 1 conditional blocks, 1 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** cryptography/key-agent, clipboard.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.i18n.manager`

gettext language discovery and translation helpers.

**Source:** `src/keys_ng/i18n/manager.py`  
**Executable symbols:** 7

**Direct module dependencies:** `__future__`, `gettext`, `locale`, `pathlib`

<!-- symbol:keys_ng.i18n.manager:_locales_dir -->
#### `_locales_dir`

**Kind:** function/method  
**Lines:** 12-23  
**Signature:** `def _locales_dir() -> Path`  
**Purpose:** Internal helper implementing `_locales_dir`.

**Direct calls observed in the function body:** `Path`, `bundled.exists`, `candidate.exists`, `resolve`.

**Control-flow shape:** 2 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 3 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.i18n.manager:_language_code -->
#### `_language_code`

**Kind:** function/method  
**Lines:** 26-29  
**Signature:** `def _language_code(value: str | None) -> str`  
**Purpose:** Internal helper implementing `_language_code`.

**Direct calls observed in the function body:** `lower`, `split`, `value.replace`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.i18n.manager:configure_language -->
#### `configure_language`

**Kind:** function/method  
**Lines:** 32-42  
**Signature:** `def configure_language(language: str | None=None) -> None`  
**Purpose:** Implements the `configure_language` operation in this module.

**Direct calls observed in the function body:** `_language_code`, `_locales_dir`, `gettext.translation`, `locale.getlocale`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.i18n.manager:current_language -->
#### `current_language`

**Kind:** function/method  
**Lines:** 45-46  
**Signature:** `def current_language() -> str`  
**Purpose:** Implements the `current_language` operation in this module.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.i18n.manager:_ -->
#### `_`

**Kind:** function/method  
**Lines:** 49-50  
**Signature:** `def _(message: str) -> str`  
**Purpose:** Internal helper implementing `_`.

**Direct calls observed in the function body:** `_translation.gettext`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.i18n.manager:ngettext -->
#### `ngettext`

**Kind:** function/method  
**Lines:** 53-54  
**Signature:** `def ngettext(singular: str, plural: str, n: int) -> str`  
**Purpose:** Implements the `ngettext` operation in this module.

**Direct calls observed in the function body:** `_translation.ngettext`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.i18n.manager:pgettext -->
#### `pgettext`

**Kind:** function/method  
**Lines:** 57-59  
**Signature:** `def pgettext(context: str, message: str) -> str`  
**Purpose:** Implements the `pgettext` operation in this module.

**Direct calls observed in the function body:** `fn`, `getattr`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.migration.keepassxc`

KeePassXC XML/KDBX import, UUID mapping and reference-safe validation.

**Source:** `src/keys_ng/migration/keepassxc.py`  
**Executable symbols:** 24

**Direct module dependencies:** `__future__`, `base64`, `binascii`, `dataclasses`, `keys_ng.errors`, `keys_ng.models`, `keys_ng.services.references`, `keys_ng.services.totp`, `keys_ng.storage.vault`, `os`, `pathlib`, `re`, `shutil`, `subprocess`, `sys`, `urllib.parse`, `uuid`, `xml.etree.ElementTree`

<!-- symbol:keys_ng.migration.keepassxc:KeePassXCImportReport -->
#### `KeePassXCImportReport`

**Kind:** class  
**Lines:** 44-56  
**Declared fields:** `entries`, `folders`, `totp_tokens`, `custom_fields`, `skipped_recycle_bin`, `uuid_preserved`, `uuid_remapped`, `uuid_generated`, `references_found`, `references_remapped`, `references_validated`, `warnings`  
**Responsibility:** Implements the `KeePassXCImportReport` operation in this module.

<!-- symbol:keys_ng.migration.keepassxc:_PendingEntry -->
#### `_PendingEntry`

**Kind:** class  
**Lines:** 60-63  
**Declared fields:** `entry`, `folder_path`, `source_uuid`  
**Responsibility:** Internal helper implementing `_PendingEntry`.

<!-- symbol:keys_ng.migration.keepassxc:_safe_xml_root -->
#### `_safe_xml_root`

**Kind:** function/method  
**Lines:** 66-75  
**Signature:** `def _safe_xml_root(raw: bytes) -> ET.Element`  
**Purpose:** Internal helper implementing `_safe_xml_root`.

**Direct calls observed in the function body:** `ET.fromstring`, `ValueError`, `len`, `upper`.

**Explicitly raised exceptions:** `ValueError`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** parser/serialization.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc:_text -->
#### `_text`

**Kind:** function/method  
**Lines:** 78-80  
**Signature:** `def _text(parent: ET.Element, path: str, default: str='') -> str`  
**Purpose:** Internal helper implementing `_text`.

**Direct calls observed in the function body:** `parent.find`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc:_strings -->
#### `_strings`

**Kind:** function/method  
**Lines:** 83-90  
**Signature:** `def _strings(entry_node: ET.Element) -> dict[str, str]`  
**Purpose:** Internal helper implementing `_strings`.

**Direct calls observed in the function body:** `_text`, `entry_node.findall`.

**Control-flow shape:** 1 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc:_decode_keepass_uuid -->
#### `_decode_keepass_uuid`

**Kind:** function/method  
**Lines:** 93-113  
**Signature:** `def _decode_keepass_uuid(value: str) -> str | None`  
**Purpose:** Convert a KeePass XML UUID to Keys NG's canonical RFC-4122 form. KDBX XML serializes UUID elements as base64Binary containing 16 UUID bytes. For robustness, canonical/32-hex UUID strings are accepted too; this is useful with hand-written exports and tests, but real KeePassXC XML normally uses Base64.

**Direct calls observed in the function body:** `ValueError`, `base64.b64decode`, `len`, `str`, `uuid.UUID`, `value.strip`.

**Explicitly raised exceptions:** `ValueError`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 2 try blocks, 0 context managers, 3 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc:_uuid_compare_key -->
#### `_uuid_compare_key`

**Kind:** function/method  
**Lines:** 116-124  
**Signature:** `def _uuid_compare_key(value: str) -> str`  
**Purpose:** Normalize UUIDs when possible, otherwise preserve opaque legacy test IDs.

**Direct calls observed in the function body:** `_decode_keepass_uuid`, `value.strip`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 3 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc:_normalize_totp_algorithm -->
#### `_normalize_totp_algorithm`

**Kind:** function/method  
**Lines:** 127-131  
**Signature:** `def _normalize_totp_algorithm(value: str) -> str`  
**Purpose:** Internal helper implementing `_normalize_totp_algorithm`.

**Direct calls observed in the function body:** `replace`, `upper`, `value.strip`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc:_parse_totp -->
#### `_parse_totp`

**Kind:** function/method  
**Lines:** 134-156  
**Signature:** `def _parse_totp(fields: dict[str, str], title: str, username: str) -> list[TotpConfig]`  
**Purpose:** Internal helper implementing `_parse_totp`.

**Direct calls observed in the function body:** `_normalize_totp_algorithm`, `fields.get`, `int`, `otp.lower`, `parse_otpauth_uri`, `startswith`, `strip`, `totp_from_secret`.

**Control-flow shape:** 3 conditional blocks, 0 loops, 3 try blocks, 0 context managers, 4 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc:_action_from_url -->
#### `_action_from_url`

**Kind:** function/method  
**Lines:** 159-171  
**Signature:** `def _action_from_url(value: str, username: str) -> tuple[list[Action], str | None]`  
**Purpose:** Internal helper implementing `_action_from_url`.

**Direct calls observed in the function body:** `Action`, `parsed.scheme.lower`, `urlparse`, `value.strip`.

**Control-flow shape:** 4 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 5 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc:_parse_tags -->
#### `_parse_tags`

**Kind:** function/method  
**Lines:** 174-179  
**Signature:** `def _parse_tags(entry_node: ET.Element) -> list[str]`  
**Purpose:** Internal helper implementing `_parse_tags`.

**Direct calls observed in the function body:** `_text`, `part.strip`, `raw.split`, `strip`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc:_entry_from_xml -->
#### `_entry_from_xml`

**Kind:** function/method  
**Lines:** 182-214  
**Signature:** `def _entry_from_xml(entry_node: ET.Element, report: KeePassXCImportReport) -> Entry`  
**Purpose:** Internal helper implementing `_entry_from_xml`.

**Direct calls observed in the function body:** `Entry.create`, `_action_from_url`, `_parse_tags`, `_parse_totp`, `_strings`, `custom.setdefault`, `fields.get`, `fields.items`, `len`, `strip`.

**Object attributes written:** `report.custom_fields`, `report.totp_tokens`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc:_new_unique_uuid -->
#### `_new_unique_uuid`

**Kind:** function/method  
**Lines:** 217-222  
**Signature:** `def _new_unique_uuid(reserved: set[str]) -> str`  
**Purpose:** Internal helper implementing `_new_unique_uuid`.

**Direct calls observed in the function body:** `reserved.add`, `str`, `uuid.uuid4`.

**Control-flow shape:** 1 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc:_rewrite_reference_text -->
#### `_rewrite_reference_text`

**Kind:** function/method  
**Lines:** 225-241  
**Signature:** `def _rewrite_reference_text(value: str | None, uuid_map: dict[str, str], report: KeePassXCImportReport) -> str | None`  
**Purpose:** Internal helper implementing `_rewrite_reference_text`.

**Direct calls observed in the function body:** `_UUID_REFERENCE_RE.sub`, `field_name.upper`, `match.group`, `match.groups`, `normalize_entry_uuid`, `uuid_map.get`, `value.upper`.

**Object attributes written:** `report.references_found`, `report.references_remapped`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 4 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc:_rewrite_reference_text.replace -->
#### `_rewrite_reference_text.replace`

**Kind:** function/method  
**Lines:** 229-239  
**Signature:** `def replace(match: re.Match[str]) -> str`  
**Purpose:** Implements the `replace` operation in this module.

**Direct calls observed in the function body:** `field_name.upper`, `match.group`, `match.groups`, `normalize_entry_uuid`, `uuid_map.get`.

**Object attributes written:** `report.references_found`, `report.references_remapped`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc:_rewrite_entry_references -->
#### `_rewrite_entry_references`

**Kind:** function/method  
**Lines:** 244-257  
**Signature:** `def _rewrite_entry_references(entry: Entry, uuid_map: dict[str, str], report: KeePassXCImportReport) -> None`  
**Purpose:** Internal helper implementing `_rewrite_entry_references`.

**Direct calls observed in the function body:** `_rewrite_reference_text`, `entry.custom_fields.items`.

**Object attributes written:** `action.argv`, `action.ssh_options`, `action.url`, `action.username`, `entry.custom_fields`, `entry.notes`, `entry.password`, `entry.title`, `entry.usernames`.

**Control-flow shape:** 0 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc:_validate_import_references -->
#### `_validate_import_references`

**Kind:** function/method  
**Lines:** 260-295  
**Signature:** `def _validate_import_references(pending: list[_PendingEntry], vault: Vault, report: KeePassXCImportReport) -> None`  
**Purpose:** Resolve every whole-field imported U/P reference before any record is saved.

**Direct calls observed in the function body:** `ValueError`, `checked.add`, `join`, `len`, `load_entry`, `parse_entry_reference`, `resolve`, `set`, `vault.get_entry`, `vault.list_items`.

**Explicitly raised exceptions:** `ValueError`.

**Object attributes written:** `report.references_validated`.

**Control-flow shape:** 6 conditional blocks, 2 loops, 0 try blocks, 0 context managers, 4 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc:_validate_import_references.load_entry -->
#### `_validate_import_references.load_entry`

**Kind:** function/method  
**Lines:** 266-271  
**Signature:** `def load_entry(entry_id: str) -> Entry`  
**Purpose:** Loads and validates `load_entry`.

**Direct calls observed in the function body:** `ValueError`, `vault.get_entry`.

**Explicitly raised exceptions:** `ValueError`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc:_validate_import_references.resolve -->
#### `_validate_import_references.resolve`

**Kind:** function/method  
**Lines:** 273-286  
**Signature:** `def resolve(value: str | None, stack: tuple[tuple[str, str], ...]=()) -> str | None`  
**Purpose:** Implements the `resolve` operation in this module.

**Direct calls observed in the function body:** `ValueError`, `checked.add`, `join`, `load_entry`, `parse_entry_reference`, `resolve`.

**Explicitly raised exceptions:** `ValueError`.

**Control-flow shape:** 3 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc:import_keepassxc_xml -->
#### `import_keepassxc_xml`

**Kind:** function/method  
**Lines:** 298-406  
**Signature:** `def import_keepassxc_xml(raw: bytes, vault: Vault, *, dry_run: bool=False) -> KeePassXCImportReport`  
**Purpose:** Import KeePassXC XML using UUID-preserving, reference-safe two-pass migration. Pass 1 collects the entire source tree and source UUIDs. Pass 2 assigns target UUIDs, rewrites all UUID references, validates whole-field U/P reference chains, and only then writes folders/entries to the destination vault.

**Direct calls observed in the function body:** `KeePassXCImportReport`, `ValueError`, `_PendingEntry`, `_decode_keepass_uuid`, `_entry_from_xml`, `_new_unique_uuid`, `_rewrite_entry_references`, `_safe_xml_root`, `_text`, `_uuid_compare_key`, `_validate_import_references`, `collect_group`, `group_node.findall`, `parse_entry_reference`, `pending.append`, `report.warnings.append`, `reserved.add`, `root.find`, `set`, `source_seen.add`, `strip`, `vault.create_folder_path`, `vault.get_entry`, `vault.list_items`, `vault.resolved_action`, `vault.resolved_password`, `vault.resolved_username`, `vault.save_entry`.

**Explicitly raised exceptions:** `ValueError`.

**Object attributes written:** `item.entry.folder_id`, `item.entry.id`, `report.entries`, `report.folders`, `report.skipped_recycle_bin`, `report.uuid_generated`, `report.uuid_preserved`, `report.uuid_remapped`.

**Control-flow shape:** 15 conditional blocks, 7 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc:import_keepassxc_xml.collect_group -->
#### `import_keepassxc_xml.collect_group`

**Kind:** function/method  
**Lines:** 318-343  
**Signature:** `def collect_group(group_node: ET.Element, parent_path: str, create_folder: bool) -> None`  
**Purpose:** Implements the `collect_group` operation in this module.

**Direct calls observed in the function body:** `ValueError`, `_PendingEntry`, `_decode_keepass_uuid`, `_entry_from_xml`, `_text`, `_uuid_compare_key`, `collect_group`, `group_node.findall`, `pending.append`, `source_seen.add`, `strip`.

**Explicitly raised exceptions:** `ValueError`.

**Object attributes written:** `report.entries`, `report.folders`, `report.skipped_recycle_bin`.

**Control-flow shape:** 4 conditional blocks, 2 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc:export_kdbx_to_xml -->
#### `export_kdbx_to_xml`

**Kind:** function/method  
**Lines:** 409-454  
**Signature:** `def export_kdbx_to_xml(database: str | Path, *, key_file: str | Path | None=None, no_password: bool=False, yubikey: str | None=None, keepassxc_cli: str | None=None, password: str | None=None) -> bytes`  
**Purpose:** Exports `export_kdbx_to_xml`.

**Direct calls observed in the function body:** `Path`, `RuntimeError`, `argv.append`, `argv.extend`, `candidates.append`, `encode`, `expanduser`, `next`, `os.environ.get`, `path.is_file`, `process.communicate`, `str`, `subprocess.Popen`, `which`.

**Explicitly raised exceptions:** `RuntimeError`.

**Control-flow shape:** 11 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** process, filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc:import_keepassxc -->
#### `import_keepassxc`

**Kind:** function/method  
**Lines:** 457-478  
**Signature:** `def import_keepassxc(source: str | Path, vault: Vault, *, source_format: str='auto', key_file: str | Path | None=None, no_password: bool=False, yubikey: str | None=None, dry_run: bool=False, password: str | None=None) -> KeePassXCImportReport`  
**Purpose:** Imports `import_keepassxc`.

**Direct calls observed in the function body:** `Path`, `ValueError`, `expanduser`, `export_kdbx_to_xml`, `import_keepassxc_xml`, `path.read_bytes`, `path.suffix.lower`, `source_format.lower`.

**Explicitly raised exceptions:** `ValueError`.

**Control-flow shape:** 3 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc:format_import_report -->
#### `format_import_report`

**Kind:** function/method  
**Lines:** 481-496  
**Signature:** `def format_import_report(report: KeePassXCImportReport) -> str`  
**Purpose:** Render a concise, frontend-neutral KeePassXC import summary.

**Direct calls observed in the function body:** `join`, `lines.append`, `lines.extend`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.migration.keepassxc_export`

KeePass-compatible XML export for one entry or an entire vault.

**Source:** `src/keys_ng/migration/keepassxc_export.py`  
**Executable symbols:** 11

**Direct module dependencies:** `__future__`, `base64`, `keys_ng.models`, `keys_ng.services.references`, `keys_ng.services.ssh_options`, `keys_ng.services.totp`, `keys_ng.storage.vault`, `pathlib`, `re`, `uuid`, `xml.etree.ElementTree`

<!-- symbol:keys_ng.migration.keepassxc_export:_keepass_uuid -->
#### `_keepass_uuid`

**Kind:** function/method  
**Lines:** 18-20  
**Signature:** `def _keepass_uuid(value: str) -> str`  
**Purpose:** Encode an RFC-4122 UUID as KeePass XML's base64Binary UUID.

**Direct calls observed in the function body:** `base64.b64encode`, `decode`, `uuid.UUID`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc_export:_reference_to_keepass -->
#### `_reference_to_keepass`

**Kind:** function/method  
**Lines:** 23-32  
**Signature:** `def _reference_to_keepass(value: str | None) -> str`  
**Purpose:** Internal helper implementing `_reference_to_keepass`.

**Direct calls observed in the function body:** `_REF_RE.sub`, `canonical.hex.upper`, `field.upper`, `match.groups`, `uuid.UUID`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 3 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc_export:_reference_to_keepass.repl -->
#### `_reference_to_keepass.repl`

**Kind:** function/method  
**Lines:** 27-30  
**Signature:** `def repl(match: re.Match[str]) -> str`  
**Purpose:** Implements the `repl` operation in this module.

**Direct calls observed in the function body:** `canonical.hex.upper`, `field.upper`, `match.groups`, `uuid.UUID`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc_export:_add_string -->
#### `_add_string`

**Kind:** function/method  
**Lines:** 35-41  
**Signature:** `def _add_string(parent: ET.Element, key: str, value: str, *, protected: bool=False) -> None`  
**Purpose:** Internal helper implementing `_add_string`.

**Direct calls observed in the function body:** `ET.SubElement`, `value_node.set`.

**Object attributes written:** `text`, `value_node.text`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** parser/serialization.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc_export:_action_url -->
#### `_action_url`

**Kind:** function/method  
**Lines:** 44-53  
**Signature:** `def _action_url(action: Action | None) -> str`  
**Purpose:** Internal helper implementing `_action_url`.

**Control-flow shape:** 3 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 4 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc_export:_entry_xml -->
#### `_entry_xml`

**Kind:** function/method  
**Lines:** 56-100  
**Signature:** `def _entry_xml(entry: Entry, vault: Vault, *, resolve_references: bool) -> ET.Element`  
**Purpose:** Internal helper implementing `_entry_xml`.

**Direct calls observed in the function body:** `ET.Element`, `ET.SubElement`, `_action_url`, `_add_string`, `_keepass_uuid`, `_reference_to_keepass`, `build_otpauth_uri`, `entry.custom_fields.items`, `format_ssh_options`, `join`, `sorted`, `vault.resolved_password`, `vault.resolved_username`.

**Object attributes written:** `text`.

**Control-flow shape:** 10 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** parser/serialization.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc_export:_new_group -->
#### `_new_group`

**Kind:** function/method  
**Lines:** 103-108  
**Signature:** `def _new_group(name: str, group_id: str | None=None) -> ET.Element`  
**Purpose:** Internal helper implementing `_new_group`.

**Direct calls observed in the function body:** `ET.Element`, `ET.SubElement`, `_keepass_uuid`, `str`, `uuid.uuid4`.

**Object attributes written:** `text`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** parser/serialization.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc_export:_document -->
#### `_document`

**Kind:** function/method  
**Lines:** 111-121  
**Signature:** `def _document(root_group: ET.Element, database_name: str) -> bytes`  
**Purpose:** Internal helper implementing `_document`.

**Direct calls observed in the function body:** `ET.Element`, `ET.SubElement`, `ET.indent`, `ET.tostring`, `root_node.append`.

**Object attributes written:** `text`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** parser/serialization.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc_export:export_entry_xml -->
#### `export_entry_xml`

**Kind:** function/method  
**Lines:** 124-133  
**Signature:** `def export_entry_xml(vault: Vault, entry_id: str) -> bytes`  
**Purpose:** Export one entry as a standalone KeePass/KeePassXC XML document. Credential references are resolved because their target entries are not part of a single-entry export.

**Direct calls observed in the function body:** `_document`, `_entry_xml`, `_new_group`, `group.append`, `vault.get_entry`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc_export:export_vault_xml -->
#### `export_vault_xml`

**Kind:** function/method  
**Lines:** 136-164  
**Signature:** `def export_vault_xml(vault: Vault) -> bytes`  
**Purpose:** Export the complete vault hierarchy as KeePass/KeePassXC XML. Entry UUIDs are preserved, so Keys NG UUID references can be translated to KeePassXC UUID-reference syntax without resolving shared credentials.

**Direct calls observed in the function body:** `ValueError`, `_document`, `_entry_xml`, `_new_group`, `group_by_id.get`, `list`, `parent.append`, `remaining.remove`, `vault.get_entry`, `vault.list_folders`, `vault.list_items`.

**Explicitly raised exceptions:** `ValueError`.

**Control-flow shape:** 2 conditional blocks, 3 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.keepassxc_export:write_export -->
#### `write_export`

**Kind:** function/method  
**Lines:** 167-176  
**Signature:** `def write_export(path: str | Path, raw: bytes) -> Path`  
**Purpose:** Write a plaintext XML export with restrictive permissions where possible.

**Direct calls observed in the function body:** `Path`, `destination.parent.mkdir`, `destination.write_bytes`, `expanduser`, `os.chmod`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.migration.legacy_parser`

Non-executing parser for legacy Bash record syntax.

**Source:** `src/keys_ng/migration/legacy_parser.py`  
**Executable symbols:** 2

**Direct module dependencies:** `__future__`, `keys_ng.errors`, `re`

<!-- symbol:keys_ng.migration.legacy_parser:_unescape_single_quoted_legacy -->
#### `_unescape_single_quoted_legacy`

**Kind:** function/method  
**Lines:** 11-25  
**Signature:** `def _unescape_single_quoted_legacy(value: str) -> str`  
**Purpose:** Internal helper implementing `_unescape_single_quoted_legacy`.

**Direct calls observed in the function body:** `LegacyFormatError`, `join`, `len`, `out.append`.

**Explicitly raised exceptions:** `LegacyFormatError`.

**Control-flow shape:** 2 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.legacy_parser:parse_legacy_record -->
#### `parse_legacy_record`

**Kind:** function/method  
**Lines:** 28-43  
**Signature:** `def parse_legacy_record(text: str) -> dict[str, str]`  
**Purpose:** Parses and validates `parse_legacy_record`.

**Direct calls observed in the function body:** `LegacyFormatError`, `_ASSIGNMENT.fullmatch`, `_unescape_single_quoted_legacy`, `enumerate`, `match.groups`, `raw.strip`, `text.splitlines`.

**Explicitly raised exceptions:** `LegacyFormatError`.

**Control-flow shape:** 4 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.migration.migrator`

Converts a legacy filesystem tree into encrypted Keys NG entries/folders.

**Source:** `src/keys_ng/migration/migrator.py`  
**Executable symbols:** 2

**Direct module dependencies:** `__future__`, `keys_ng.crypto.backend`, `keys_ng.migration.legacy_parser`, `keys_ng.models`, `keys_ng.storage.vault`, `pathlib`

<!-- symbol:keys_ng.migration.migrator:_legacy_kind -->
#### `_legacy_kind`

**Kind:** function/method  
**Lines:** 11-16  
**Signature:** `def _legacy_kind(path: Path) -> tuple[str, str]`  
**Purpose:** Internal helper implementing `_legacy_kind`.

**Direct calls observed in the function body:** `len`, `name.endswith`.

**Control-flow shape:** 1 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.migration.migrator:migrate_legacy_tree -->
#### `migrate_legacy_tree`

**Kind:** function/method  
**Lines:** 19-62  
**Signature:** `def migrate_legacy_tree(source: Path, vault: Vault, crypto: CryptoBackend, dry_run: bool=False, verify: bool=False) -> list[tuple[Path, str]]`  
**Purpose:** Implements the `migrate_legacy_tree` operation in this module.

**Direct calls observed in the function body:** `Action`, `Entry.create`, `ValueError`, `_legacy_kind`, `actions.append`, `argv.append`, `crypto.decrypt`, `entry.to_bytes`, `join`, `list`, `p.is_file`, `parse_legacy_record`, `path.read_bytes`, `path.relative_to`, `plaintext.decode`, `restored.to_bytes`, `results.append`, `sorted`, `source.rglob`, `strip`, `values.get`, `vault.create_folder_path`, `vault.get_entry`, `vault.save_entry`.

**Explicitly raised exceptions:** `ValueError`.

**Control-flow shape:** 7 conditional blocks, 1 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** filesystem, cryptography/key-agent.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.models`

Validated in-memory and JSON-serializable domain model.

**Source:** `src/keys_ng/models.py`  
**Executable symbols:** 21

**Direct module dependencies:** `__future__`, `dataclasses`, `datetime`, `json`, `typing`, `uuid`

<!-- symbol:keys_ng.models:utc_now -->
#### `utc_now`

**Kind:** function/method  
**Lines:** 12-13  
**Signature:** `def utc_now() -> str`  
**Purpose:** Implements the `utc_now` operation in this module.

**Direct calls observed in the function body:** `datetime.now`, `isoformat`, `replace`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.models:TotpConfig -->
#### `TotpConfig`

**Kind:** class  
**Lines:** 17-33  
**Declared fields:** `secret`, `issuer`, `account_name`, `algorithm`, `digits`, `period`  
**Methods:** `validate`  
**Responsibility:** Validated TOTP seed and algorithm parameters.

<!-- symbol:keys_ng.models:TotpConfig.validate -->
#### `TotpConfig.validate`

**Kind:** function/method  
**Lines:** 25-33  
**Signature:** `def validate(self) -> None`  
**Purpose:** Validates the invariants of `validate`.

**Direct calls observed in the function body:** `ValueError`, `self.algorithm.upper`, `self.secret.strip`.

**Explicitly raised exceptions:** `ValueError`.

**Control-flow shape:** 4 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** parser/serialization.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.models:Action -->
#### `Action`

**Kind:** class  
**Lines:** 37-69  
**Declared fields:** `type`, `url`, `host`, `port`, `username`, `argv`, `shell`, `ssh_x11_forwarding`, `ssh_options`  
**Methods:** `validate`  
**Responsibility:** Validated external action attached to an entry.

<!-- symbol:keys_ng.models:Action.validate -->
#### `Action.validate`

**Kind:** function/method  
**Lines:** 48-69  
**Signature:** `def validate(self) -> None`  
**Purpose:** Validates the invariants of `validate`.

**Direct calls observed in the function body:** `ValueError`, `all`, `isinstance`, `self.type.upper`, `validate_ssh_options`.

**Explicitly raised exceptions:** `ValueError`.

**Control-flow shape:** 10 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.models:Folder -->
#### `Folder`

**Kind:** class  
**Lines:** 73-93  
**Declared fields:** `id`, `name`, `parent_id`, `created_at`, `updated_at`  
**Methods:** `create`, `validate`  
**Responsibility:** Logical folder node identified by UUID.

<!-- symbol:keys_ng.models:Folder.create -->
#### `Folder.create`

**Kind:** function/method  
**Lines:** 81-82  
**Signature:** `def create(cls, name: str, parent_id: str | None=None) -> 'Folder'`  
**Purpose:** Implements the `create` operation in this module.

**Direct calls observed in the function body:** `cls`, `str`, `uuid.uuid4`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.models:Folder.validate -->
#### `Folder.validate`

**Kind:** function/method  
**Lines:** 84-93  
**Signature:** `def validate(self) -> None`  
**Purpose:** Validates the invariants of `validate`.

**Direct calls observed in the function body:** `ValueError`, `self.name.strip`, `uuid.UUID`.

**Explicitly raised exceptions:** `ValueError`.

**Control-flow shape:** 4 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.models:FolderStore -->
#### `FolderStore`

**Kind:** class  
**Lines:** 97-129  
**Declared fields:** `folders`, `schema`  
**Methods:** `validate`, `to_bytes`, `from_bytes`  
**Responsibility:** Encrypted logical folder tree.

<!-- symbol:keys_ng.models:FolderStore.validate -->
#### `FolderStore.validate`

**Kind:** function/method  
**Lines:** 101-118  
**Signature:** `def validate(self) -> None`  
**Purpose:** Validates the invariants of `validate`.

**Direct calls observed in the function body:** `ValueError`, `by_id.get`, `folder.validate`, `len`, `seen.add`, `set`.

**Explicitly raised exceptions:** `ValueError`.

**Control-flow shape:** 4 conditional blocks, 3 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.models:FolderStore.to_bytes -->
#### `FolderStore.to_bytes`

**Kind:** function/method  
**Lines:** 120-122  
**Signature:** `def to_bytes(self) -> bytes`  
**Purpose:** Serializes/converts `to_bytes`.

**Direct calls observed in the function body:** `asdict`, `encode`, `json.dumps`, `self.validate`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** parser/serialization.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.models:FolderStore.from_bytes -->
#### `FolderStore.from_bytes`

**Kind:** function/method  
**Lines:** 125-129  
**Signature:** `def from_bytes(cls, raw: bytes) -> 'FolderStore'`  
**Purpose:** Deserializes/constructs `from_bytes`.

**Direct calls observed in the function body:** `Folder`, `cls`, `data.get`, `json.loads`, `raw.decode`, `store.validate`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** parser/serialization.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.models:Entry -->
#### `Entry`

**Kind:** class  
**Lines:** 133-182  
**Declared fields:** `id`, `title`, `kind`, `usernames`, `password`, `totp`, `actions`, `tags`, `notes`, `custom_fields`, `folder_id`, `revision`, `created_at`, `updated_at`, `schema`  
**Methods:** `create`, `validate`, `to_bytes`, `from_bytes`  
**Responsibility:** Credential record persisted inside one encrypted record file.

<!-- symbol:keys_ng.models:Entry.create -->
#### `Entry.create`

**Kind:** function/method  
**Lines:** 151-152  
**Signature:** `def create(cls, title: str, **kwargs: Any) -> 'Entry'`  
**Purpose:** Implements the `create` operation in this module.

**Direct calls observed in the function body:** `cls`, `str`, `uuid.uuid4`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.models:Entry.validate -->
#### `Entry.validate`

**Kind:** function/method  
**Lines:** 154-167  
**Signature:** `def validate(self) -> None`  
**Purpose:** Validates the invariants of `validate`.

**Direct calls observed in the function body:** `ValueError`, `action.validate`, `self.title.strip`, `token.validate`, `uuid.UUID`.

**Explicitly raised exceptions:** `ValueError`.

**Control-flow shape:** 4 conditional blocks, 2 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.models:Entry.to_bytes -->
#### `Entry.to_bytes`

**Kind:** function/method  
**Lines:** 169-171  
**Signature:** `def to_bytes(self) -> bytes`  
**Purpose:** Serializes/converts `to_bytes`.

**Direct calls observed in the function body:** `asdict`, `encode`, `json.dumps`, `self.validate`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** parser/serialization.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.models:Entry.from_bytes -->
#### `Entry.from_bytes`

**Kind:** function/method  
**Lines:** 174-182  
**Signature:** `def from_bytes(cls, raw: bytes) -> 'Entry'`  
**Purpose:** Deserializes/constructs `from_bytes`.

**Direct calls observed in the function body:** `Action`, `TotpConfig`, `cls`, `data.get`, `data.setdefault`, `entry.validate`, `json.loads`, `raw.decode`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** parser/serialization.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.models:CatalogItem -->
#### `CatalogItem`

**Kind:** class  
**Lines:** 186-196  
**Declared fields:** `id`, `title`, `kind`, `usernames`, `tags`, `url_hosts`, `capabilities`, `revision`, `ciphertext_sha256`, `folder_id`  
**Responsibility:** One catalog row derived from an Entry and its ciphertext hash.

<!-- symbol:keys_ng.models:Catalog -->
#### `Catalog`

**Kind:** class  
**Lines:** 200-218  
**Declared fields:** `items`, `folders`, `schema`  
**Methods:** `to_bytes`, `from_bytes`  
**Responsibility:** Encrypted searchable metadata snapshot; rebuildable from records.

<!-- symbol:keys_ng.models:Catalog.to_bytes -->
#### `Catalog.to_bytes`

**Kind:** function/method  
**Lines:** 205-206  
**Signature:** `def to_bytes(self) -> bytes`  
**Purpose:** Serializes/converts `to_bytes`.

**Direct calls observed in the function body:** `asdict`, `encode`, `json.dumps`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** parser/serialization.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.models:Catalog.from_bytes -->
#### `Catalog.from_bytes`

**Kind:** function/method  
**Lines:** 209-218  
**Signature:** `def from_bytes(cls, raw: bytes) -> 'Catalog'`  
**Purpose:** Deserializes/constructs `from_bytes`.

**Direct calls observed in the function body:** `CatalogItem`, `Folder`, `ValueError`, `cls`, `data.get`, `item.setdefault`, `items.append`, `json.loads`, `raw.decode`.

**Explicitly raised exceptions:** `ValueError`.

**Control-flow shape:** 1 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** parser/serialization.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.platform.app_identity`

Desktop/process identity and application icon integration.

**Source:** `src/keys_ng/platform/app_identity.py`  
**Executable symbols:** 4

**Direct module dependencies:** `__future__`, `importlib.resources`, `sys`

<!-- symbol:keys_ng.platform.app_identity:icon_bytes -->
#### `icon_bytes`

**Kind:** function/method  
**Lines:** 11-13  
**Signature:** `def icon_bytes() -> bytes`  
**Purpose:** Return the bundled legacy Keys application icon as PNG bytes.

**Direct calls observed in the function body:** `files`, `joinpath`, `read_bytes`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.platform.app_identity:configure_process_identity -->
#### `configure_process_identity`

**Kind:** function/method  
**Lines:** 16-30  
**Signature:** `def configure_process_identity() -> None`  
**Purpose:** Set platform process identity before the GUI toolkit starts. On Windows this helps the taskbar group Keys NG separately from the Python interpreter when running from source. It is intentionally best-effort.

**Direct calls observed in the function body:** `ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.platform.app_identity:apply_qt_identity -->
#### `apply_qt_identity`

**Kind:** function/method  
**Lines:** 33-57  
**Signature:** `def apply_qt_identity(app) -> object | None`  
**Purpose:** Apply application name, desktop identity and bundled icon to Qt. Returns the QIcon so callers can also set it explicitly on top-level windows if desired. Importing PySide6 is deferred to keep CLI/TUI free of a GUI dependency.

**Direct calls observed in the function body:** `QIcon`, `QPixmap`, `app.setApplicationDisplayName`, `app.setApplicationName`, `app.setDesktopFileName`, `app.setOrganizationName`, `app.setWindowIcon`, `hasattr`, `icon_bytes`, `pixmap.loadFromData`.

**Control-flow shape:** 3 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 3 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.platform.app_identity:set_textual_terminal_title -->
#### `set_textual_terminal_title`

**Kind:** function/method  
**Lines:** 60-75  
**Signature:** `def set_textual_terminal_title(app) -> None`  
**Purpose:** Best-effort TUI identity. A terminal application does not own the desktop window; the terminal emulator does. We can therefore set the terminal/window title where the host supports it, but cannot portably replace the terminal emulator's graphical taskbar icon from Textual.

**Direct calls observed in the function body:** `app.console.set_window_title`.

**Object attributes written:** `app.title`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 2 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.platform.desktop_integration`

Per-user desktop launcher installation/status/removal.

**Source:** `src/keys_ng/platform/desktop_integration.py`  
**Executable symbols:** 13

**Direct module dependencies:** `__future__`, `dataclasses`, `importlib.resources`, `keys_ng.platform.app_identity`, `keys_ng.platform.host`, `os`, `pathlib`, `shutil`, `subprocess`, `sys`

<!-- symbol:keys_ng.platform.desktop_integration:DesktopIntegrationPaths -->
#### `DesktopIntegrationPaths`

**Kind:** class  
**Lines:** 21-25  
**Declared fields:** `desktop_file`, `icon_file`  
**Responsibility:** Implements the `DesktopIntegrationPaths` operation in this module.

<!-- symbol:keys_ng.platform.desktop_integration:_xdg_data_home -->
#### `_xdg_data_home`

**Kind:** function/method  
**Lines:** 28-32  
**Signature:** `def _xdg_data_home() -> Path`  
**Purpose:** Internal helper implementing `_xdg_data_home`.

**Direct calls observed in the function body:** `Path`, `Path.home`, `expanduser`, `os.environ.get`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.platform.desktop_integration:_gui_executable -->
#### `_gui_executable`

**Kind:** function/method  
**Lines:** 35-41  
**Signature:** `def _gui_executable() -> str`  
**Purpose:** Internal helper implementing `_gui_executable`.

**Direct calls observed in the function body:** `Path`, `resolve`, `shutil.which`, `str`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.platform.desktop_integration:user_paths -->
#### `user_paths`

**Kind:** function/method  
**Lines:** 44-59  
**Signature:** `def user_paths() -> DesktopIntegrationPaths`  
**Purpose:** Implements the `user_paths` operation in this module.

**Direct calls observed in the function body:** `DesktopIntegrationPaths`, `Path`, `Path.home`, `RuntimeError`, `_xdg_data_home`, `os.environ.get`, `sys.platform.startswith`.

**Explicitly raised exceptions:** `RuntimeError`.

**Control-flow shape:** 3 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 3 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.platform.desktop_integration:_resource_bytes -->
#### `_resource_bytes`

**Kind:** function/method  
**Lines:** 62-63  
**Signature:** `def _resource_bytes(name: str) -> bytes`  
**Purpose:** Internal helper implementing `_resource_bytes`.

**Direct calls observed in the function body:** `files`, `joinpath`, `read_bytes`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.platform.desktop_integration:_desktop_exec_token -->
#### `_desktop_exec_token`

**Kind:** function/method  
**Lines:** 66-69  
**Signature:** `def _desktop_exec_token(value: str) -> str`  
**Purpose:** Internal helper implementing `_desktop_exec_token`.

**Direct calls observed in the function body:** `replace`, `value.replace`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.platform.desktop_integration:_install_linux -->
#### `_install_linux`

**Kind:** function/method  
**Lines:** 72-95  
**Signature:** `def _install_linux(paths: DesktopIntegrationPaths) -> None`  
**Purpose:** Internal helper implementing `_install_linux`.

**Direct calls observed in the function body:** `Path`, `_desktop_exec_token`, `_gui_executable`, `_resource_bytes`, `decode`, `join`, `line.startswith`, `lines.append`, `name.lower`, `paths.desktop_file.chmod`, `paths.desktop_file.parent.mkdir`, `paths.desktop_file.write_text`, `paths.icon_file.chmod`, `paths.icon_file.parent.mkdir`, `paths.icon_file.write_bytes`, `startswith`, `template.splitlines`.

**Control-flow shape:** 3 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.platform.desktop_integration:_install_windows -->
#### `_install_windows`

**Kind:** function/method  
**Lines:** 98-125  
**Signature:** `def _install_windows(paths: DesktopIntegrationPaths) -> None`  
**Purpose:** Internal helper implementing `_install_windows`.

**Direct calls observed in the function body:** `Path`, `Path.home`, `RuntimeError`, `_gui_executable`, `_resource_bytes`, `arguments.replace`, `name.lower`, `paths.desktop_file.exists`, `paths.desktop_file.parent.mkdir`, `paths.icon_file.parent.mkdir`, `paths.icon_file.write_bytes`, `replace`, `shutil.which`, `startswith`, `str`, `subprocess.run`, `target.replace`.

**Explicitly raised exceptions:** `RuntimeError`.

**Control-flow shape:** 3 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** process, filesystem, parser/serialization.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.platform.desktop_integration:_install_macos -->
#### `_install_macos`

**Kind:** function/method  
**Lines:** 128-155  
**Signature:** `def _install_macos(paths: DesktopIntegrationPaths) -> None`  
**Purpose:** Internal helper implementing `_install_macos`.

**Direct calls observed in the function body:** `Path`, `_gui_executable`, `_resource_bytes`, `launcher.chmod`, `launcher.write_text`, `macos.mkdir`, `name.lower`, `paths.icon_file.write_bytes`, `resources.mkdir`, `startswith`, `write_text`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.platform.desktop_integration:install_user_desktop_integration -->
#### `install_user_desktop_integration`

**Kind:** function/method  
**Lines:** 158-169  
**Signature:** `def install_user_desktop_integration() -> DesktopIntegrationPaths`  
**Purpose:** Install a per-user application-menu launcher on Linux, Windows or macOS.

**Direct calls observed in the function body:** `RuntimeError`, `_install_linux`, `_install_macos`, `_install_windows`, `sys.platform.startswith`, `user_paths`.

**Explicitly raised exceptions:** `RuntimeError`.

**Control-flow shape:** 3 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.platform.desktop_integration:ensure_user_desktop_integration -->
#### `ensure_user_desktop_integration`

**Kind:** function/method  
**Lines:** 172-188  
**Signature:** `def ensure_user_desktop_integration() -> DesktopIntegrationPaths | None`  
**Purpose:** Best-effort per-user application-menu integration used by the GUI.

**Direct calls observed in the function body:** `desktop_integration_status`, `in_flatpak`, `install_user_desktop_integration`, `sys.platform.startswith`, `user_paths`.

**Control-flow shape:** 3 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 5 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.platform.desktop_integration:uninstall_user_desktop_integration -->
#### `uninstall_user_desktop_integration`

**Kind:** function/method  
**Lines:** 191-201  
**Signature:** `def uninstall_user_desktop_integration() -> DesktopIntegrationPaths`  
**Purpose:** Implements the `uninstall_user_desktop_integration` operation in this module.

**Direct calls observed in the function body:** `path.unlink`, `shutil.rmtree`, `user_paths`.

**Control-flow shape:** 1 conditional blocks, 1 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.platform.desktop_integration:desktop_integration_status -->
#### `desktop_integration_status`

**Kind:** function/method  
**Lines:** 204-210  
**Signature:** `def desktop_integration_status() -> tuple[bool, DesktopIntegrationPaths]`  
**Purpose:** Implements the `desktop_integration_status` operation in this module.

**Direct calls observed in the function body:** `is_file`, `paths.desktop_file.is_file`, `paths.icon_file.is_file`, `user_paths`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.platform.host`

Flatpak host-command bridge and executable resolution.

**Source:** `src/keys_ng/platform/host.py`  
**Executable symbols:** 4

**Direct module dependencies:** `__future__`, `os`, `pathlib`, `shutil`, `subprocess`

<!-- symbol:keys_ng.platform.host:in_flatpak -->
#### `in_flatpak`

**Kind:** function/method  
**Lines:** 9-10  
**Signature:** `def in_flatpak() -> bool`  
**Purpose:** Implements the `in_flatpak` operation in this module.

**Direct calls observed in the function body:** `Path`, `bool`, `exists`, `os.environ.get`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.platform.host:host_prefix -->
#### `host_prefix`

**Kind:** function/method  
**Lines:** 13-18  
**Signature:** `def host_prefix() -> list[str]`  
**Purpose:** Prefix argv so external desktop tools execute on the host from Flatpak.

**Direct calls observed in the function body:** `in_flatpak`, `shutil.which`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.platform.host:host_which -->
#### `host_which`

**Kind:** function/method  
**Lines:** 21-37  
**Signature:** `def host_which(name: str) -> str | None`  
**Purpose:** Resolve an executable on the host without invoking a shell.

**Direct calls observed in the function body:** `host_prefix`, `in_flatpak`, `os.access`, `os.path.isabs`, `os.path.isfile`, `proc.stdout.decode`, `shutil.which`, `splitlines`, `strip`, `subprocess.run`.

**Control-flow shape:** 5 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 6 explicit returns.

**Security-relevant effect categories:** process.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.platform.host:host_argv -->
#### `host_argv`

**Kind:** function/method  
**Lines:** 40-41  
**Signature:** `def host_argv(argv: list[str]) -> list[str]`  
**Purpose:** Implements the `host_argv` operation in this module.

**Direct calls observed in the function body:** `host_prefix`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.platform.paths`

Cross-platform application config/data paths.

**Source:** `src/keys_ng/platform/paths.py`  
**Executable symbols:** 2

**Direct module dependencies:** `pathlib`, `platformdirs`

<!-- symbol:keys_ng.platform.paths:config_dir -->
#### `config_dir`

**Kind:** function/method  
**Lines:** 9-10  
**Signature:** `def config_dir() -> Path`  
**Purpose:** Implements the `config_dir` operation in this module.

**Direct calls observed in the function body:** `Path`, `user_config_path`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.platform.paths:data_dir -->
#### `data_dir`

**Kind:** function/method  
**Lines:** 13-14  
**Signature:** `def data_dir() -> Path`  
**Purpose:** Implements the `data_dir` operation in this module.

**Direct calls observed in the function body:** `Path`, `user_data_path`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.services.actions`

Launches URL, SSH, RDP and argv-based command actions without a shell.

**Source:** `src/keys_ng/services/actions.py`  
**Executable symbols:** 9

**Direct module dependencies:** `__future__`, `keys_ng.models`, `keys_ng.platform.host`, `keys_ng.storage.settings`, `os`, `shutil`, `subprocess`, `sys`, `urllib.parse`, `webbrowser`

<!-- symbol:keys_ng.services.actions:ActionError -->
#### `ActionError`

**Kind:** class  
**Lines:** 15-16  
**Bases:** `RuntimeError`  
**Responsibility:** Implements the `ActionError` operation in this module.

<!-- symbol:keys_ng.services.actions:_which -->
#### `_which`

**Kind:** function/method  
**Lines:** 19-23  
**Signature:** `def _which(name: str) -> str | None`  
**Purpose:** Internal helper implementing `_which`.

**Direct calls observed in the function body:** `host_which`, `in_flatpak`, `shutil.which`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.actions:_resolve_executable -->
#### `_resolve_executable`

**Kind:** function/method  
**Lines:** 26-32  
**Signature:** `def _resolve_executable(name: str) -> str | None`  
**Purpose:** Resolve a configured executable without invoking a shell.

**Direct calls observed in the function body:** `_which`, `in_flatpak`, `os.access`, `os.path.isabs`, `os.path.isfile`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 3 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.actions:_ssh_terminal -->
#### `_ssh_terminal`

**Kind:** function/method  
**Lines:** 35-72  
**Signature:** `def _ssh_terminal(settings: AppSettings) -> tuple[str, list[str]]`  
**Purpose:** Internal helper implementing `_ssh_terminal`.

**Direct calls observed in the function body:** `ActionError`, `_resolve_executable`, `_which`, `get`, `list`, `os.path.basename`, `requested.lower`, `settings.ssh_terminal.strip`.

**Explicitly raised exceptions:** `ActionError`.

**Control-flow shape:** 4 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 3 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.actions:_launch_ssh -->
#### `_launch_ssh`

**Kind:** function/method  
**Lines:** 75-98  
**Signature:** `def _launch_ssh(action: Action, settings: AppSettings) -> None`  
**Purpose:** Internal helper implementing `_launch_ssh`.

**Direct calls observed in the function body:** `ActionError`, `_ssh_terminal`, `_which`, `host_argv`, `ssh_argv.append`, `ssh_argv.extend`, `str`, `subprocess.Popen`.

**Explicitly raised exceptions:** `ActionError`.

**Control-flow shape:** 5 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** process, filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.actions:_linux_rdp -->
#### `_linux_rdp`

**Kind:** function/method  
**Lines:** 101-117  
**Signature:** `def _linux_rdp(action: Action, settings: AppSettings) -> None`  
**Purpose:** Internal helper implementing `_linux_rdp`.

**Direct calls observed in the function body:** `ActionError`, `_resolve_executable`, `_which`, `argv.append`, `host_argv`, `next`, `requested.lower`, `settings.rdp_linux_client.strip`, `str`, `subprocess.Popen`.

**Explicitly raised exceptions:** `ActionError`.

**Control-flow shape:** 5 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** process, filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.actions:_windows_rdp -->
#### `_windows_rdp`

**Kind:** function/method  
**Lines:** 120-128  
**Signature:** `def _windows_rdp(action: Action, settings: AppSettings) -> None`  
**Purpose:** Internal helper implementing `_windows_rdp`.

**Direct calls observed in the function body:** `ActionError`, `_resolve_executable`, `host_argv`, `settings.rdp_windows_client.strip`, `str`, `subprocess.Popen`.

**Explicitly raised exceptions:** `ActionError`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** process, filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.actions:_macos_rdp -->
#### `_macos_rdp`

**Kind:** function/method  
**Lines:** 131-147  
**Signature:** `def _macos_rdp(action: Action, settings: AppSettings) -> None`  
**Purpose:** Internal helper implementing `_macos_rdp`.

**Direct calls observed in the function body:** `ActionError`, `_resolve_executable`, `attributes.append`, `host_argv`, `join`, `quote`, `requested.lower`, `settings.rdp_macos_client.strip`, `str`, `subprocess.Popen`.

**Explicitly raised exceptions:** `ActionError`.

**Control-flow shape:** 3 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** process, filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.actions:launch_action -->
#### `launch_action`

**Kind:** function/method  
**Lines:** 150-173  
**Signature:** `def launch_action(action: Action, settings: AppSettings | None=None) -> None`  
**Purpose:** Validates and launches `launch_action`.

**Direct calls observed in the function body:** `ActionError`, `AppSettings.load`, `_launch_ssh`, `_linux_rdp`, `_macos_rdp`, `_windows_rdp`, `action.validate`, `host_argv`, `subprocess.Popen`, `webbrowser.open`.

**Explicitly raised exceptions:** `ActionError`.

**Control-flow shape:** 8 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 4 explicit returns.

**Security-relevant effect categories:** process, filesystem, desktop URL launcher.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.services.clipboard`

Secret clipboard backends, ownership checking and timed clearing.

**Source:** `src/keys_ng/services/clipboard.py`  
**Executable symbols:** 9

**Direct module dependencies:** `__future__`, `queue`, `secrets`, `shutil`, `subprocess`, `sys`, `threading`

<!-- symbol:keys_ng.services.clipboard:ClipboardUnavailable -->
#### `ClipboardUnavailable`

**Kind:** class  
**Lines:** 11-12  
**Bases:** `RuntimeError`  
**Responsibility:** Implements the `ClipboardUnavailable` operation in this module.

<!-- symbol:keys_ng.services.clipboard:copy_secret_qt -->
#### `copy_secret_qt`

**Kind:** function/method  
**Lines:** 15-40  
**Signature:** `def copy_secret_qt(secret: str, timeout_ms: int=15000) -> None`  
**Purpose:** Copy a secret using Qt and clear it only if Keys NG still owns the token.

**Direct calls observed in the function body:** `ClipboardUnavailable`, `QByteArray`, `QGuiApplication.instance`, `QMimeData`, `QTimer.singleShot`, `app.clipboard`, `bytes`, `clipboard.clear`, `clipboard.mimeData`, `clipboard.setMimeData`, `current.data`, `mime.setData`, `mime.setText`, `secrets.token_bytes`.

**Explicitly raised exceptions:** `ClipboardUnavailable`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** clipboard.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.clipboard:copy_secret_qt.clear_if_owned -->
#### `copy_secret_qt.clear_if_owned`

**Kind:** function/method  
**Lines:** 35-38  
**Signature:** `def clear_if_owned() -> None`  
**Purpose:** Implements the `clear_if_owned` operation in this module.

**Direct calls observed in the function body:** `bytes`, `clipboard.clear`, `clipboard.mimeData`, `current.data`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** clipboard.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.clipboard:_run_clipboard_command -->
#### `_run_clipboard_command`

**Kind:** function/method  
**Lines:** 43-61  
**Signature:** `def _run_clipboard_command(argv: list[str], *, input_bytes: bytes | None=None, timeout: float=3.0) -> bytes`  
**Purpose:** Internal helper implementing `_run_clipboard_command`.

**Direct calls observed in the function body:** `ClipboardUnavailable`, `completed.stderr.decode`, `strip`, `subprocess.run`.

**Explicitly raised exceptions:** `ClipboardUnavailable`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** process, clipboard.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.clipboard:available_native_clipboard_backend -->
#### `available_native_clipboard_backend`

**Kind:** function/method  
**Lines:** 64-88  
**Signature:** `def available_native_clipboard_backend() -> str | None`  
**Purpose:** Return the best terminal-friendly clipboard backend for this platform.

**Direct calls observed in the function body:** `os.environ.get`, `shutil.which`.

**Control-flow shape:** 8 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 9 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.clipboard:set_native_clipboard -->
#### `set_native_clipboard`

**Kind:** function/method  
**Lines:** 91-112  
**Signature:** `def set_native_clipboard(secret: str, backend: str | None=None) -> str`  
**Purpose:** Write text to a platform clipboard without putting the secret in argv/env.

**Direct calls observed in the function body:** `ClipboardUnavailable`, `_run_clipboard_command`, `available_native_clipboard_backend`, `secret.encode`.

**Explicitly raised exceptions:** `ClipboardUnavailable`.

**Control-flow shape:** 6 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** process, clipboard, parser/serialization.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.clipboard:read_native_clipboard -->
#### `read_native_clipboard`

**Kind:** function/method  
**Lines:** 115-130  
**Signature:** `def read_native_clipboard(backend: str) -> str`  
**Purpose:** Implements the `read_native_clipboard` operation in this module.

**Direct calls observed in the function body:** `ClipboardUnavailable`, `_run_clipboard_command`, `data.decode`.

**Explicitly raised exceptions:** `ClipboardUnavailable`.

**Control-flow shape:** 5 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** process, clipboard.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.clipboard:clear_native_clipboard -->
#### `clear_native_clipboard`

**Kind:** function/method  
**Lines:** 133-155  
**Signature:** `def clear_native_clipboard(backend: str) -> None`  
**Purpose:** Implements the `clear_native_clipboard` operation in this module.

**Direct calls observed in the function body:** `ClipboardUnavailable`, `_run_clipboard_command`.

**Explicitly raised exceptions:** `ClipboardUnavailable`.

**Control-flow shape:** 5 conditional blocks, 0 loops, 2 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** process, clipboard.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.clipboard:copy_secret_cli -->
#### `copy_secret_cli`

**Kind:** function/method  
**Lines:** 158-214  
**Signature:** `def copy_secret_cli(secret: str, timeout_seconds: int=15) -> None`  
**Purpose:** Start a detached helper that owns/copies and later clears the clipboard. The helper prefers native terminal clipboard implementations. Qt is used only as a fallback, so the TUI no longer requires the GUI optional dependency.

**Direct calls observed in the function body:** `ClipboardUnavailable`, `acknowledgement.startswith`, `acknowledgements.get`, `acknowledgements.put`, `decode`, `getattr`, `isinstance`, `proc.stderr.read`, `proc.stdin.close`, `proc.stdin.write`, `proc.stdout.close`, `proc.stdout.readline`, `proc.terminate`, `queue.Queue`, `raw_ack.decode`, `secret.encode`, `start`, `str`, `strip`, `subprocess.Popen`, `threading.Thread`.

**Explicitly raised exceptions:** `ClipboardUnavailable`.

**Control-flow shape:** 5 conditional blocks, 0 loops, 4 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** process, filesystem, clipboard, parser/serialization.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.services.clipboard_helper`

Detached helper process used by terminal clipboard operations.

**Source:** `src/keys_ng/services/clipboard_helper.py`  
**Executable symbols:** 4

**Direct module dependencies:** `__future__`, `keys_ng.services.clipboard`, `sys`, `time`

<!-- symbol:keys_ng.services.clipboard_helper:_normalise -->
#### `_normalise`

**Kind:** function/method  
**Lines:** 14-16  
**Signature:** `def _normalise(value: str) -> str`  
**Purpose:** Internal helper implementing `_normalise`.

**Direct calls observed in the function body:** `value.replace`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.clipboard_helper:_native_worker -->
#### `_native_worker`

**Kind:** function/method  
**Lines:** 19-33  
**Signature:** `def _native_worker(secret: str, timeout_seconds: int) -> None`  
**Purpose:** Internal helper implementing `_native_worker`.

**Direct calls observed in the function body:** `ClipboardUnavailable`, `_normalise`, `clear_native_clipboard`, `read_native_clipboard`, `set_native_clipboard`, `sys.stdout.flush`, `sys.stdout.write`, `time.sleep`.

**Explicitly raised exceptions:** `ClipboardUnavailable`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** clipboard.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.clipboard_helper:_qt_worker -->
#### `_qt_worker`

**Kind:** function/method  
**Lines:** 36-53  
**Signature:** `def _qt_worker(secret: str, timeout_seconds: int) -> None`  
**Purpose:** Internal helper implementing `_qt_worker`.

**Direct calls observed in the function body:** `ClipboardUnavailable`, `QGuiApplication`, `QTimer.singleShot`, `app.clipboard`, `app.exec`, `app.processEvents`, `copy_secret_qt`, `sys.stdout.flush`, `sys.stdout.write`, `text`.

**Explicitly raised exceptions:** `ClipboardUnavailable`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** clipboard.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.clipboard_helper:main -->
#### `main`

**Kind:** function/method  
**Lines:** 56-68  
**Signature:** `def main() -> None`  
**Purpose:** Implements the `main` operation in this module.

**Direct calls observed in the function body:** `SystemExit`, `_native_worker`, `_qt_worker`, `decode`, `int`, `max`, `print`, `sys.stdin.buffer.read`.

**Explicitly raised exceptions:** `SystemExit`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 2 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.services.diagnostics`

Opt-in rotating diagnostic logging with privacy-preserving operation/timing summaries.

**Source:** `src/keys_ng/services/diagnostics.py`  
**Executable symbols:** 6

**Direct module dependencies:** `__future__`, `logging`, `logging.handlers`, `os`, `pathlib`, `platformdirs`, `sys`, `time`

<!-- symbol:keys_ng.services.diagnostics:default_log_path -->
#### `default_log_path`

**Kind:** function/method  
**Lines:** 17-19  
**Signature:** `def default_log_path() -> Path`  
**Purpose:** Return the per-user diagnostics log path without creating it.

**Direct calls observed in the function body:** `Path`, `user_log_dir`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.diagnostics:diagnostics_log_path -->
#### `diagnostics_log_path`

**Kind:** function/method  
**Lines:** 22-24  
**Signature:** `def diagnostics_log_path() -> Path | None`  
**Purpose:** Return the active diagnostics log path, if diagnostics are configured.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.diagnostics:configure_diagnostics -->
#### `configure_diagnostics`

**Kind:** function/method  
**Lines:** 27-73  
**Signature:** `def configure_diagnostics(settings, component: str) -> Path | None`  
**Purpose:** Configure rotating file diagnostics from AppSettings. Diagnostics are opt-in. Callers must never include credentials, decrypted record fields, TOTP seeds/codes, clipboard contents, or plaintext exports.

**Direct calls observed in the function body:** `Path`, `RotatingFileHandler`, `default_log_path`, `expanduser`, `getattr`, `handler.setFormatter`, `int`, `logger.addHandler`, `logger.handlers.clear`, `logger.info`, `logger.setLevel`, `logging.Formatter`, `logging.getLogger`, `max`, `min`, `os.chmod`, `path.parent.mkdir`, `path.resolve`, `str`, `strip`, `sys.version.split`, `upper`.

**Object attributes written:** `logger.propagate`.

**Control-flow shape:** 3 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 3 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.diagnostics:get_logger -->
#### `get_logger`

**Kind:** function/method  
**Lines:** 76-78  
**Signature:** `def get_logger(name: str) -> logging.Logger`  
**Purpose:** Return a child logger in the Keys NG diagnostics namespace.

**Direct calls observed in the function body:** `logging.getLogger`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.diagnostics:elapsed_ms -->
#### `elapsed_ms`

**Kind:** function/method  
**Lines:** 81-83  
**Signature:** `def elapsed_ms(start: float) -> float`  
**Purpose:** Convert a perf_counter start value to elapsed milliseconds.

**Direct calls observed in the function body:** `time.perf_counter`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.diagnostics:safe_operation_args -->
#### `safe_operation_args`

**Kind:** function/method  
**Lines:** 86-103  
**Signature:** `def safe_operation_args(args) -> str`  
**Purpose:** Return a non-secret summary of a GnuPG argv sequence. Only operation flags are exposed. Values following options are deliberately omitted so fingerprints, file names, UIDs, paths, and other arguments do not leak into diagnostic logs.

**Direct calls observed in the function body:** `join`, `operation_flags.items`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.services.doctor`

Runtime/environment diagnostics.

**Source:** `src/keys_ng/services/doctor.py`  
**Executable symbols:** 3

**Direct module dependencies:** `__future__`, `dataclasses`, `importlib.util`, `keys_ng`, `keys_ng.crypto.backend`, `keys_ng.platform.desktop_integration`, `keys_ng.services.clipboard`, `keys_ng.services.diagnostics`, `keys_ng.storage.settings`, `platform`, `shutil`, `sys`

<!-- symbol:keys_ng.services.doctor:DoctorCheck -->
#### `DoctorCheck`

**Kind:** class  
**Lines:** 18-22  
**Declared fields:** `name`, `ok`, `detail`, `optional`  
**Responsibility:** Implements the `DoctorCheck` operation in this module.

<!-- symbol:keys_ng.services.doctor:_module -->
#### `_module`

**Kind:** function/method  
**Lines:** 25-26  
**Signature:** `def _module(name: str) -> bool`  
**Purpose:** Internal helper implementing `_module`.

**Direct calls observed in the function body:** `importlib.util.find_spec`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.doctor:collect_doctor_checks -->
#### `collect_doctor_checks`

**Kind:** function/method  
**Lines:** 29-74  
**Signature:** `def collect_doctor_checks(crypto: CryptoBackend, settings: AppSettings | None=None) -> list[DoctorCheck]`  
**Purpose:** Implements the `collect_doctor_checks` operation in this module.

**Direct calls observed in the function body:** `AppSettings.default_path`, `AppSettings.load`, `DoctorCheck`, `_module`, `available_native_clipboard_backend`, `bool`, `checks.append`, `checks.extend`, `crypto.diagnose`, `default_log_path`, `desktop_integration_status`, `next`, `platform.python_version`, `shutil.which`, `str`, `sys.platform.startswith`.

**Control-flow shape:** 3 conditional blocks, 1 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** clipboard.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.services.entry_editor`

Frontend-neutral credential editor draft and validation shared by GUI and TUI.

**Source:** `src/keys_ng/services/entry_editor.py`  
**Executable symbols:** 3

**Direct module dependencies:** `__future__`, `dataclasses`, `keys_ng.i18n`, `keys_ng.models`, `keys_ng.services.ssh_options`, `keys_ng.services.totp`

<!-- symbol:keys_ng.services.entry_editor:EntryDraft -->
#### `EntryDraft`

**Kind:** class  
**Lines:** 12-56  
**Declared fields:** `title`, `folder_id`, `action_type`, `username`, `password`, `url`, `host`, `port`, `ssh_x11_forwarding`, `ssh_options`, `tags`, `totp_uri`, `totp_secret`, `notes`  
**Methods:** `from_entry`  
**Responsibility:** Frontend-neutral editable representation of one credential. GUI and TUI deliberately use the same conversion routine so validation and preservation rules cannot silently diverge between front ends.

<!-- symbol:keys_ng.services.entry_editor:EntryDraft.from_entry -->
#### `EntryDraft.from_entry`

**Kind:** function/method  
**Lines:** 35-56  
**Signature:** `def from_entry(cls, entry: Entry) -> 'EntryDraft'`  
**Purpose:** Deserializes/constructs `from_entry`.

**Direct calls observed in the function body:** `build_otpauth_uri`, `cls`, `format_ssh_options`, `join`, `next`, `str`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.entry_editor:build_entry_from_draft -->
#### `build_entry_from_draft`

**Kind:** function/method  
**Lines:** 59-158  
**Signature:** `def build_entry_from_draft(draft: EntryDraft, existing: Entry | None=None) -> Entry`  
**Purpose:** Validate a frontend draft and create/update the domain Entry. Imported/legacy command actions and custom fields are preserved during an edit because the desktop editor does not expose them directly.

**Direct calls observed in the function body:** `Action`, `Entry.create`, `ValueError`, `_`, `actions.insert`, `draft.action_type.strip`, `draft.host.strip`, `draft.port.strip`, `draft.tags.split`, `draft.title.strip`, `draft.totp_secret.strip`, `draft.totp_uri.strip`, `draft.url.strip`, `draft.username.strip`, `entry.validate`, `existing.validate`, `int`, `lower`, `parse_otpauth_uri`, `parse_ssh_options`, `secret.replace`, `tag.strip`, `token.secret.replace`, `totp_from_secret`, `upper`.

**Explicitly raised exceptions:** `ValueError`.

**Object attributes written:** `existing.actions`, `existing.folder_id`, `existing.kind`, `existing.notes`, `existing.password`, `existing.revision`, `existing.tags`, `existing.title`, `existing.totp`, `existing.usernames`.

**Control-flow shape:** 10 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 2 explicit returns.

**Security-relevant effect categories:** filesystem, parser/serialization.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.services.passwords`

Cryptographically secure password generation.

**Source:** `src/keys_ng/services/passwords.py`  
**Executable symbols:** 1

**Direct module dependencies:** `__future__`, `secrets`, `string`

<!-- symbol:keys_ng.services.passwords:generate_password -->
#### `generate_password`

**Kind:** function/method  
**Lines:** 9-47  
**Signature:** `def generate_password(length: int=24, *, uppercase: bool=True, lowercase: bool=True, digits: bool=True, symbols: bool=True, ambiguous: bool=False) -> str`  
**Purpose:** Implements the `generate_password` operation in this module.

**Direct calls observed in the function body:** `ValueError`, `chars.extend`, `groups.append`, `join`, `len`, `range`, `secrets.choice`, `secrets.randbelow`, `set`.

**Explicitly raised exceptions:** `ValueError`.

**Control-flow shape:** 8 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.services.qr`

QR decoding and conversion to TOTP configuration.

**Source:** `src/keys_ng/services/qr.py`  
**Executable symbols:** 4

**Direct module dependencies:** `__future__`, `keys_ng.models`, `keys_ng.services.totp`, `pathlib`

<!-- symbol:keys_ng.services.qr:QRUnavailable -->
#### `QRUnavailable`

**Kind:** class  
**Lines:** 9-10  
**Bases:** `RuntimeError`  
**Responsibility:** Implements the `QRUnavailable` operation in this module.

<!-- symbol:keys_ng.services.qr:_decode_image -->
#### `_decode_image`

**Kind:** function/method  
**Lines:** 13-24  
**Signature:** `def _decode_image(image) -> TotpConfig`  
**Purpose:** Internal helper implementing `_decode_image`.

**Direct calls observed in the function body:** `QRUnavailable`, `ValueError`, `barcode.text.strip`, `parse_otpauth_uri`, `text.startswith`, `zxingcpp.read_barcode`.

**Explicitly raised exceptions:** `QRUnavailable`, `ValueError`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.qr:parse_totp_qr_file -->
#### `parse_totp_qr_file`

**Kind:** function/method  
**Lines:** 27-33  
**Signature:** `def parse_totp_qr_file(path: str | Path) -> TotpConfig`  
**Purpose:** Parses and validates `parse_totp_qr_file`.

**Direct calls observed in the function body:** `Image.open`, `Path`, `QRUnavailable`, `_decode_image`, `image.convert`.

**Explicitly raised exceptions:** `QRUnavailable`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 1 try blocks, 1 context managers, 1 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.qr:parse_totp_qimage -->
#### `parse_totp_qimage`

**Kind:** function/method  
**Lines:** 36-37  
**Signature:** `def parse_totp_qimage(image) -> TotpConfig`  
**Purpose:** Parses and validates `parse_totp_qimage`.

**Direct calls observed in the function body:** `_decode_image`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.services.references`

KeePassXC-style UUID reference parsing and construction.

**Source:** `src/keys_ng/services/references.py`  
**Executable symbols:** 5

**Direct module dependencies:** `__future__`, `dataclasses`, `keys_ng.errors`, `re`, `uuid`

<!-- symbol:keys_ng.services.references:EntryReference -->
#### `EntryReference`

**Kind:** class  
**Lines:** 15-21  
**Declared fields:** `field`, `entry_id`  
**Methods:** `field_name`  
**Responsibility:** Implements the `EntryReference` operation in this module.

<!-- symbol:keys_ng.services.references:EntryReference.field_name -->
#### `EntryReference.field_name`

**Kind:** function/method  
**Lines:** 20-21  
**Signature:** `def field_name(self) -> str`  
**Purpose:** Implements the `field_name` operation in this module.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.references:normalize_entry_uuid -->
#### `normalize_entry_uuid`

**Kind:** function/method  
**Lines:** 24-28  
**Signature:** `def normalize_entry_uuid(value: str) -> str`  
**Purpose:** Implements the `normalize_entry_uuid` operation in this module.

**Direct calls observed in the function body:** `ReferenceError`, `str`, `uuid.UUID`, `value.strip`.

**Explicitly raised exceptions:** `ReferenceError`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.references:parse_entry_reference -->
#### `parse_entry_reference`

**Kind:** function/method  
**Lines:** 31-38  
**Signature:** `def parse_entry_reference(value: str | None) -> EntryReference | None`  
**Purpose:** Parses and validates `parse_entry_reference`.

**Direct calls observed in the function body:** `EntryReference`, `_REFERENCE_RE.fullmatch`, `match.groups`, `normalize_entry_uuid`, `value.strip`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 3 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.references:make_entry_reference -->
#### `make_entry_reference`

**Kind:** function/method  
**Lines:** 41-47  
**Signature:** `def make_entry_reference(field: str, entry_id: str, *, keepass_uuid: bool=False) -> str`  
**Purpose:** Implements the `make_entry_reference` operation in this module.

**Direct calls observed in the function body:** `ReferenceError`, `field.upper`, `hex.upper`, `normalize_entry_uuid`, `strip`, `uuid.UUID`.

**Explicitly raised exceptions:** `ReferenceError`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.services.ssh_options`

Parses and validates advanced OpenSSH argv options.

**Source:** `src/keys_ng/services/ssh_options.py`  
**Executable symbols:** 4

**Direct module dependencies:** `__future__`, `shlex`

<!-- symbol:keys_ng.services.ssh_options:SSHOptionsError -->
#### `SSHOptionsError`

**Kind:** class  
**Lines:** 6-7  
**Bases:** `ValueError`  
**Responsibility:** Implements the `SSHOptionsError` operation in this module.

<!-- symbol:keys_ng.services.ssh_options:parse_ssh_options -->
#### `parse_ssh_options`

**Kind:** function/method  
**Lines:** 10-26  
**Signature:** `def parse_ssh_options(text: str) -> list[str]`  
**Purpose:** Parse user-entered SSH options into argv without involving a shell. The destination, username, port and X11 forwarding are managed separately by Keys NG. We therefore reject options that would silently override those fields. All other OpenSSH options (including -J, -L, -R, -D and -o ...) are passed through as argv tokens.

**Direct calls observed in the function body:** `SSHOptionsError`, `shlex.split`, `text.strip`, `validate_ssh_options`.

**Explicitly raised exceptions:** `SSHOptionsError`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.ssh_options:validate_ssh_options -->
#### `validate_ssh_options`

**Kind:** function/method  
**Lines:** 29-52  
**Signature:** `def validate_ssh_options(argv: list[str]) -> None`  
**Purpose:** Validates the invariants of `validate_ssh_options`.

**Direct calls observed in the function body:** `SSHOptionsError`, `enumerate`, `isdigit`, `len`, `lower`, `option_value.split`, `strip`, `token.startswith`.

**Explicitly raised exceptions:** `SSHOptionsError`.

**Control-flow shape:** 9 conditional blocks, 2 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.ssh_options:format_ssh_options -->
#### `format_ssh_options`

**Kind:** function/method  
**Lines:** 55-57  
**Signature:** `def format_ssh_options(argv: list[str]) -> str`  
**Purpose:** Return a safely quoted, editable representation of stored argv tokens.

**Direct calls observed in the function body:** `shlex.join`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.services.totp`

RFC-style TOTP generation and otpauth URI parsing/building.

**Source:** `src/keys_ng/services/totp.py`  
**Executable symbols:** 5

**Direct module dependencies:** `__future__`, `base64`, `hashlib`, `hmac`, `keys_ng.models`, `struct`, `time`, `urllib.parse`

<!-- symbol:keys_ng.services.totp:_decode_base32 -->
#### `_decode_base32`

**Kind:** function/method  
**Lines:** 15-18  
**Signature:** `def _decode_base32(secret: str) -> bytes`  
**Purpose:** Internal helper implementing `_decode_base32`.

**Direct calls observed in the function body:** `base64.b32decode`, `join`, `len`, `secret.split`, `upper`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** parser/serialization.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.totp:totp_from_secret -->
#### `totp_from_secret`

**Kind:** function/method  
**Lines:** 22-48  
**Signature:** `def totp_from_secret(secret: str, *, issuer: str='', account_name: str='', algorithm: str='SHA1', digits: int=6, period: int=30) -> TotpConfig`  
**Purpose:** Build and validate a TOTP configuration from a raw Base32 secret.

**Direct calls observed in the function body:** `TotpConfig`, `ValueError`, `_decode_base32`, `account_name.strip`, `algorithm.upper`, `config.validate`, `issuer.strip`, `join`, `secret.split`, `upper`.

**Explicitly raised exceptions:** `ValueError`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** parser/serialization.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.totp:generate_totp -->
#### `generate_totp`

**Kind:** function/method  
**Lines:** 50-60  
**Signature:** `def generate_totp(config: TotpConfig, at_time: int | float | None=None) -> tuple[str, int]`  
**Purpose:** Implements the `generate_totp` operation in this module.

**Direct calls observed in the function body:** `_decode_base32`, `config.algorithm.upper`, `config.validate`, `digest`, `hmac.new`, `int`, `str`, `struct.pack`, `struct.unpack`, `time.time`, `zfill`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.totp:parse_otpauth_uri -->
#### `parse_otpauth_uri`

**Kind:** function/method  
**Lines:** 63-84  
**Signature:** `def parse_otpauth_uri(uri: str) -> TotpConfig`  
**Purpose:** Parses and validates `parse_otpauth_uri`.

**Direct calls observed in the function body:** `TotpConfig`, `ValueError`, `config.validate`, `int`, `label.partition`, `params.get`, `parse_qs`, `parsed.netloc.lower`, `parsed.path.lstrip`, `unquote`, `upper`, `urlparse`.

**Explicitly raised exceptions:** `ValueError`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.totp:build_otpauth_uri -->
#### `build_otpauth_uri`

**Kind:** function/method  
**Lines:** 87-98  
**Signature:** `def build_otpauth_uri(config: TotpConfig) -> str`  
**Purpose:** Builds `build_otpauth_uri`.

**Direct calls observed in the function body:** `config.algorithm.upper`, `config.validate`, `join`, `params.append`, `quote`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.services.trusted_signers`

Per-vault authorization list for cryptographically valid Inbox signers.

**Source:** `src/keys_ng/services/trusted_signers.py`  
**Executable symbols:** 7

**Direct module dependencies:** `__future__`, `dataclasses`, `keys_ng.crypto.backend`, `keys_ng.errors`, `keys_ng.storage.config`, `keys_ng.storage.vault`, `os`, `pathlib`

<!-- symbol:keys_ng.services.trusted_signers:TrustedSignerInfo -->
#### `TrustedSignerInfo`

**Kind:** class  
**Lines:** 14-21  
**Declared fields:** `fingerprint`, `label`, `present`, `revoked`, `expired`, `can_sign`, `vault_signer`  
**Responsibility:** Implements the `TrustedSignerInfo` operation in this module.

<!-- symbol:keys_ng.services.trusted_signers:_save_config -->
#### `_save_config`

**Kind:** function/method  
**Lines:** 24-28  
**Signature:** `def _save_config(vault: Vault) -> None`  
**Purpose:** Internal helper implementing `_save_config`.

**Direct calls observed in the function body:** `os.chmod`, `path.write_text`, `vault.config.to_json`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.trusted_signers:_key_by_fingerprint -->
#### `_key_by_fingerprint`

**Kind:** function/method  
**Lines:** 31-33  
**Signature:** `def _key_by_fingerprint(vault: Vault, fingerprint: str) -> KeyInfo | None`  
**Purpose:** Internal helper implementing `_key_by_fingerprint`.

**Direct calls observed in the function body:** `fingerprint.strip`, `key.fingerprint.upper`, `next`, `upper`, `vault.crypto.list_keys`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.trusted_signers:list_trusted_signers -->
#### `list_trusted_signers`

**Kind:** function/method  
**Lines:** 36-54  
**Signature:** `def list_trusted_signers(vault: Vault) -> list[TrustedSignerInfo]`  
**Purpose:** Returns a filtered/listed view of `list_trusted_signers`.

**Direct calls observed in the function body:** `TrustedSignerInfo`, `bool`, `fingerprint.upper`, `key.fingerprint.upper`, `keys.get`, `result.append`, `upper`, `vault.crypto.list_keys`.

**Control-flow shape:** 0 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.trusted_signers:eligible_signing_keys -->
#### `eligible_signing_keys`

**Kind:** function/method  
**Lines:** 57-58  
**Signature:** `def eligible_signing_keys(vault: Vault) -> list[KeyInfo]`  
**Purpose:** Implements the `eligible_signing_keys` operation in this module.

**Direct calls observed in the function body:** `vault.crypto.list_keys`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.trusted_signers:add_trusted_signer -->
#### `add_trusted_signer`

**Kind:** function/method  
**Lines:** 61-76  
**Signature:** `def add_trusted_signer(vault: Vault, fingerprint: str) -> TrustedSignerInfo`  
**Purpose:** Implements the `add_trusted_signer` operation in this module.

**Direct calls observed in the function body:** `TrustedSignerInfo`, `VaultError`, `_key_by_fingerprint`, `_save_config`, `upper`, `value.upper`, `vault.config.trusted_signers.append`, `vault.crypto.resolve_fingerprint`.

**Explicitly raised exceptions:** `VaultError`.

**Control-flow shape:** 5 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.trusted_signers:remove_trusted_signer -->
#### `remove_trusted_signer`

**Kind:** function/method  
**Lines:** 79-87  
**Signature:** `def remove_trusted_signer(vault: Vault, fingerprint: str) -> None`  
**Purpose:** Implements the `remove_trusted_signer` operation in this module.

**Direct calls observed in the function body:** `VaultError`, `_save_config`, `fingerprint.strip`, `len`, `upper`, `value.upper`.

**Explicitly raised exceptions:** `VaultError`.

**Object attributes written:** `vault.config.trusted_signers`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.services.ui_capabilities`

Declares the interactive GUI/TUI parity contract.

**Source:** `src/keys_ng/services/ui_capabilities.py`  
**Executable symbols:** 1

**Direct module dependencies:** `__future__`

<!-- symbol:keys_ng.services.ui_capabilities:missing_interactive_capabilities -->
#### `missing_interactive_capabilities`

**Kind:** function/method  
**Lines:** 22-24  
**Signature:** `def missing_interactive_capabilities(frontend: str) -> frozenset[str]`  
**Purpose:** Implements the `missing_interactive_capabilities` operation in this module.

**Direct calls observed in the function body:** `frozenset`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.services.vault_init`

Shared vault-creation validation, key selection and pre-write cryptographic self-test.

**Source:** `src/keys_ng/services/vault_init.py`  
**Executable symbols:** 7

**Direct module dependencies:** `__future__`, `dataclasses`, `keys_ng.crypto.backend`, `keys_ng.errors`, `keys_ng.storage.vault`, `pathlib`

<!-- symbol:keys_ng.services.vault_init:VaultInitRequest -->
#### `VaultInitRequest`

**Kind:** class  
**Lines:** 12-17  
**Declared fields:** `path`, `recipients`, `signer`, `require_signature`, `catalog_privacy`  
**Responsibility:** Implements the `VaultInitRequest` operation in this module.

<!-- symbol:keys_ng.services.vault_init:VaultInitChoices -->
#### `VaultInitChoices`

**Kind:** class  
**Lines:** 21-23  
**Declared fields:** `recipients`, `signers`  
**Responsibility:** Implements the `VaultInitChoices` operation in this module.

<!-- symbol:keys_ng.services.vault_init:available_vault_keys -->
#### `available_vault_keys`

**Kind:** function/method  
**Lines:** 26-36  
**Signature:** `def available_vault_keys(crypto: CryptoBackend) -> VaultInitChoices`  
**Purpose:** Return usable public encryption keys and secret signing keys.

**Direct calls observed in the function body:** `VaultInitChoices`, `crypto.list_keys`, `tuple`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.vault_init:validate_vault_target -->
#### `validate_vault_target`

**Kind:** function/method  
**Lines:** 39-54  
**Signature:** `def validate_vault_target(path: str | Path) -> Path`  
**Purpose:** Validate the target without creating or deleting user data.

**Direct calls observed in the function body:** `Path`, `VaultError`, `any`, `expanduser`, `parent.exists`, `parent.is_dir`, `resolve`, `root.exists`, `root.is_dir`, `root.iterdir`.

**Explicitly raised exceptions:** `VaultError`.

**Control-flow shape:** 4 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.vault_init:_normalize_request -->
#### `_normalize_request`

**Kind:** function/method  
**Lines:** 57-72  
**Signature:** `def _normalize_request(request: VaultInitRequest, crypto: CryptoBackend) -> VaultInitRequest`  
**Purpose:** Internal helper implementing `_normalize_request`.

**Direct calls observed in the function body:** `VaultError`, `VaultInitRequest`, `crypto.resolve_fingerprint`, `tuple`, `validate_vault_target`.

**Explicitly raised exceptions:** `VaultError`.

**Control-flow shape:** 3 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.vault_init:run_vault_crypto_self_test -->
#### `run_vault_crypto_self_test`

**Kind:** function/method  
**Lines:** 75-86  
**Signature:** `def run_vault_crypto_self_test(crypto: CryptoBackend, recipients: tuple[str, ...], signer: str | None, require_signature: bool) -> None`  
**Purpose:** Verify encrypt/decrypt/signature behavior before writing a new vault.

**Direct calls observed in the function body:** `VaultError`, `crypto.decrypt`, `crypto.encrypt`, `list`, `result.signer_fingerprint.upper`, `signer.upper`.

**Explicitly raised exceptions:** `VaultError`.

**Control-flow shape:** 4 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** cryptography/key-agent.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.vault_init:create_vault -->
#### `create_vault`

**Kind:** function/method  
**Lines:** 89-106  
**Signature:** `def create_vault(request: VaultInitRequest, crypto: CryptoBackend, *, self_test: bool=True) -> Vault`  
**Purpose:** Create a vault through the shared CLI/GUI/TUI initialization policy.

**Direct calls observed in the function body:** `Vault.init`, `_normalize_request`, `list`, `run_vault_crypto_self_test`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.services.vault_sessions`

Multi-vault session state for interactive frontends, preserving one Vault object and lock/cache state per open vault.

**Source:** `src/keys_ng/services/vault_sessions.py`  
**Executable symbols:** 14

**Direct module dependencies:** `__future__`, `collections.abc`, `keys_ng.storage.vault`, `pathlib`

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager -->
#### `VaultSessionManager`

**Kind:** class  
**Lines:** 9-82  
**Methods:** `__init__`, `_key`, `active`, `active_path`, `add`, `activate`, `contains`, `opened`, `paths`, `close`, `lock_all`, `__len__`, `__iter__`  
**Responsibility:** Track multiple open vault objects and one active vault. The manager deliberately keeps each ``Vault`` instance alive while it is open so its lock state and in-memory caches remain independent when the TUI switches between vaults.

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager.__init__ -->
#### `VaultSessionManager.__init__`

**Kind:** function/method  
**Lines:** 17-20  
**Signature:** `def __init__(self, initial: Vault) -> None`  
**Purpose:** Internal helper implementing `__init__`.

**Direct calls observed in the function body:** `self.add`.

**Object attributes written:** `self._active_path`, `self._vaults`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager._key -->
#### `VaultSessionManager._key`

**Kind:** function/method  
**Lines:** 23-24  
**Signature:** `def _key(path: str | Path) -> str`  
**Purpose:** Internal helper implementing `_key`.

**Direct calls observed in the function body:** `Path`, `expanduser`, `resolve`, `str`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager.active -->
#### `VaultSessionManager.active`

**Kind:** function/method  
**Lines:** 27-28  
**Signature:** `def active(self) -> Vault`  
**Purpose:** Implements the `active` operation in this module.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager.active_path -->
#### `VaultSessionManager.active_path`

**Kind:** function/method  
**Lines:** 31-32  
**Signature:** `def active_path(self) -> str`  
**Purpose:** Implements the `active_path` operation in this module.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager.add -->
#### `VaultSessionManager.add`

**Kind:** function/method  
**Lines:** 34-42  
**Signature:** `def add(self, vault: Vault, *, activate: bool=True) -> Vault`  
**Purpose:** Implements the `add` operation in this module.

**Direct calls observed in the function body:** `self._key`, `self._vaults.get`.

**Object attributes written:** `self._active_path`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager.activate -->
#### `VaultSessionManager.activate`

**Kind:** function/method  
**Lines:** 44-49  
**Signature:** `def activate(self, path: str | Path) -> Vault`  
**Purpose:** Implements the `activate` operation in this module.

**Direct calls observed in the function body:** `KeyError`, `self._key`.

**Explicitly raised exceptions:** `KeyError`.

**Object attributes written:** `self._active_path`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager.contains -->
#### `VaultSessionManager.contains`

**Kind:** function/method  
**Lines:** 51-52  
**Signature:** `def contains(self, path: str | Path) -> bool`  
**Purpose:** Implements the `contains` operation in this module.

**Direct calls observed in the function body:** `self._key`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager.opened -->
#### `VaultSessionManager.opened`

**Kind:** function/method  
**Lines:** 54-55  
**Signature:** `def opened(self) -> tuple[Vault, ...]`  
**Purpose:** Implements the `opened` operation in this module.

**Direct calls observed in the function body:** `self._vaults.values`, `tuple`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager.paths -->
#### `VaultSessionManager.paths`

**Kind:** function/method  
**Lines:** 57-58  
**Signature:** `def paths(self) -> tuple[str, ...]`  
**Purpose:** Implements the `paths` operation in this module.

**Direct calls observed in the function body:** `tuple`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager.close -->
#### `VaultSessionManager.close`

**Kind:** function/method  
**Lines:** 60-72  
**Signature:** `def close(self, path: str | Path | None=None) -> Vault | None`  
**Purpose:** Implements the `close` operation in this module.

**Direct calls observed in the function body:** `next`, `reversed`, `self._key`, `self._vaults.pop`, `vault.lock`.

**Object attributes written:** `self._active_path`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager.lock_all -->
#### `VaultSessionManager.lock_all`

**Kind:** function/method  
**Lines:** 74-76  
**Signature:** `def lock_all(self) -> None`  
**Purpose:** Implements the `lock_all` operation in this module.

**Direct calls observed in the function body:** `self._vaults.values`, `vault.lock`.

**Control-flow shape:** 0 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager.__len__ -->
#### `VaultSessionManager.__len__`

**Kind:** function/method  
**Lines:** 78-79  
**Signature:** `def __len__(self) -> int`  
**Purpose:** Internal helper implementing `__len__`.

**Direct calls observed in the function body:** `len`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager.__iter__ -->
#### `VaultSessionManager.__iter__`

**Kind:** function/method  
**Lines:** 81-82  
**Signature:** `def __iter__(self) -> Iterable[Vault]`  
**Purpose:** Internal helper implementing `__iter__`.

**Direct calls observed in the function body:** `iter`, `self._vaults.values`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.storage.atomic`

Crash-resistant ciphertext-only atomic file replacement and stale-temp cleanup.

**Source:** `src/keys_ng/storage/atomic.py`  
**Executable symbols:** 2

**Direct module dependencies:** `__future__`, `os`, `pathlib`, `secrets`

<!-- symbol:keys_ng.storage.atomic:atomic_write_ciphertext -->
#### `atomic_write_ciphertext`

**Kind:** function/method  
**Lines:** 8-32  
**Signature:** `def atomic_write_ciphertext(path: Path, data: bytes) -> None`  
**Purpose:** Atomically replace a ciphertext file. The temporary file contains ciphertext only.

**Direct calls observed in the function body:** `handle.fileno`, `handle.flush`, `handle.write`, `hasattr`, `os.close`, `os.fdopen`, `os.fsync`, `os.open`, `os.replace`, `path.parent.mkdir`, `path.with_name`, `secrets.token_hex`, `tmp.unlink`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 3 try blocks, 1 context managers, 0 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.atomic:remove_stale_ciphertext_temps -->
#### `remove_stale_ciphertext_temps`

**Kind:** function/method  
**Lines:** 35-46  
**Signature:** `def remove_stale_ciphertext_temps(directory: Path) -> int`  
**Purpose:** Remove abandoned atomic-write temp files. They contain ciphertext only.

**Direct calls observed in the function body:** `directory.exists`, `directory.glob`, `path.unlink`.

**Control-flow shape:** 1 conditional blocks, 1 loops, 1 try blocks, 0 context managers, 2 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.storage.config`

Cleartext vault policy/configuration file model.

**Source:** `src/keys_ng/storage/config.py`  
**Executable symbols:** 4

**Direct module dependencies:** `__future__`, `dataclasses`, `json`, `keys_ng.errors`, `pathlib`

<!-- symbol:keys_ng.storage.config:VaultConfig -->
#### `VaultConfig`

**Kind:** class  
**Lines:** 14-59  
**Declared fields:** `recipients`, `signer`, `trusted_signers`, `require_signature`, `catalog_privacy`, `schema`  
**Methods:** `validate`, `to_json`, `load`  
**Responsibility:** Implements the `VaultConfig` operation in this module.

<!-- symbol:keys_ng.storage.config:VaultConfig.validate -->
#### `VaultConfig.validate`

**Kind:** function/method  
**Lines:** 22-30  
**Signature:** `def validate(self) -> None`  
**Purpose:** Validates the invariants of `validate`.

**Direct calls observed in the function body:** `VaultError`.

**Explicitly raised exceptions:** `VaultError`.

**Control-flow shape:** 4 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.config:VaultConfig.to_json -->
#### `VaultConfig.to_json`

**Kind:** function/method  
**Lines:** 32-45  
**Signature:** `def to_json(self) -> str`  
**Purpose:** Serializes/converts `to_json`.

**Direct calls observed in the function body:** `json.dumps`, `self.validate`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** parser/serialization.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.config:VaultConfig.load -->
#### `VaultConfig.load`

**Kind:** function/method  
**Lines:** 48-59  
**Signature:** `def load(cls, vault_path: Path) -> 'VaultConfig'`  
**Purpose:** Implements the `load` operation in this module.

**Direct calls observed in the function body:** `VaultError`, `cls`, `config.validate`, `data.get`, `data.setdefault`, `json.loads`, `path.read_text`.

**Explicitly raised exceptions:** `VaultError`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** filesystem, parser/serialization.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.storage.inbox`

Public-key-only deposit and controlled inbox import.

**Source:** `src/keys_ng/storage/inbox.py`  
**Executable symbols:** 11

**Direct module dependencies:** `__future__`, `dataclasses`, `keys_ng.crypto.backend`, `keys_ng.models`, `keys_ng.services.diagnostics`, `keys_ng.storage.atomic`, `keys_ng.storage.vault`, `pathlib`, `time`, `uuid`

<!-- symbol:keys_ng.storage.inbox:InboxInspection -->
#### `InboxInspection`

**Kind:** class  
**Lines:** 18-44  
**Declared fields:** `path`, `entry`, `decryptable`, `signed`, `signature_valid`, `signer_fingerprint`, `signer_authorized`, `error`  
**Methods:** `importable`, `status`  
**Responsibility:** Implements the `InboxInspection` operation in this module.

<!-- symbol:keys_ng.storage.inbox:InboxInspection.importable -->
#### `InboxInspection.importable`

**Kind:** function/method  
**Lines:** 29-30  
**Signature:** `def importable(self) -> bool`  
**Purpose:** Implements the `importable` operation in this module.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.inbox:InboxInspection.status -->
#### `InboxInspection.status`

**Kind:** function/method  
**Lines:** 33-44  
**Signature:** `def status(self) -> str`  
**Purpose:** Implements the `status` operation in this module.

**Control-flow shape:** 5 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 6 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.inbox:write_encrypted_entry -->
#### `write_encrypted_entry`

**Kind:** function/method  
**Lines:** 47-53  
**Signature:** `def write_encrypted_entry(output_path: str | Path, entry: Entry, crypto: CryptoBackend, recipients: list[str], signer: str | None=None) -> Path`  
**Purpose:** Encrypt one standalone entry to an arbitrary ciphertext path.

**Direct calls observed in the function body:** `Path`, `atomic_write_ciphertext`, `crypto.encrypt`, `entry.to_bytes`, `entry.validate`, `expanduser`, `resolve`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** cryptography/key-agent.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.inbox:deposit_entry -->
#### `deposit_entry`

**Kind:** function/method  
**Lines:** 56-59  
**Signature:** `def deposit_entry(vault_path: str | Path, entry: Entry, crypto: CryptoBackend, recipients: list[str], signer: str | None=None) -> Path`  
**Purpose:** Write a new encrypted inbox item without requiring access to the vault catalog.

**Direct calls observed in the function body:** `Path`, `expanduser`, `resolve`, `uuid.uuid4`, `write_encrypted_entry`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** cryptography/key-agent.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.inbox:pending_inbox_paths -->
#### `pending_inbox_paths`

**Kind:** function/method  
**Lines:** 62-64  
**Signature:** `def pending_inbox_paths(vault: Vault) -> list[Path]`  
**Purpose:** Return pending ciphertexts without decrypting them.

**Direct calls observed in the function body:** `glob`, `sorted`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.inbox:inspect_inbox_item -->
#### `inspect_inbox_item`

**Kind:** function/method  
**Lines:** 67-89  
**Signature:** `def inspect_inbox_item(vault: Vault, path: Path) -> InboxInspection`  
**Purpose:** Decrypt and classify one inbox item without modifying the vault.

**Direct calls observed in the function body:** `Entry.from_bytes`, `InboxInspection`, `_LOG.debug`, `_LOG.info`, `bool`, `elapsed_ms`, `fp.upper`, `path.read_bytes`, `signer.upper`, `time.perf_counter`, `type`, `vault.crypto.decrypt`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 2 try blocks, 0 context managers, 3 explicit returns.

**Security-relevant effect categories:** filesystem, cryptography/key-agent.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.inbox:inspect_inbox -->
#### `inspect_inbox`

**Kind:** function/method  
**Lines:** 92-95  
**Signature:** `def inspect_inbox(vault: Vault) -> list[InboxInspection]`  
**Purpose:** Implements the `inspect_inbox` operation in this module.

**Direct calls observed in the function body:** `_LOG.info`, `inspect_inbox_item`, `len`, `pending_inbox_paths`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.inbox:import_inbox_item -->
#### `import_inbox_item`

**Kind:** function/method  
**Lines:** 98-118  
**Signature:** `def import_inbox_item(vault: Vault, inspection: InboxInspection, *, delete_after: bool=True, accept_unsigned: bool=False) -> str`  
**Purpose:** Import one already inspected item and re-encrypt/sign it with vault policy.

**Direct calls observed in the function body:** `ValueError`, `_LOG.debug`, `_LOG.info`, `elapsed_ms`, `inspection.path.unlink`, `target.exists`, `time.perf_counter`, `vault.save_entry`.

**Explicitly raised exceptions:** `ValueError`.

**Control-flow shape:** 7 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** filesystem, parser/serialization.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.inbox:delete_inbox_item -->
#### `delete_inbox_item`

**Kind:** function/method  
**Lines:** 121-126  
**Signature:** `def delete_inbox_item(vault: Vault, path: Path) -> None`  
**Purpose:** Deletes `delete_inbox_item`.

**Direct calls observed in the function body:** `ValueError`, `path.resolve`, `resolve`, `resolved.suffix.lower`, `resolved.unlink`.

**Explicitly raised exceptions:** `ValueError`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.inbox:import_inbox -->
#### `import_inbox`

**Kind:** function/method  
**Lines:** 129-138  
**Signature:** `def import_inbox(vault: Vault, *, delete_after: bool=True, accept_unsigned: bool=False) -> list[tuple[Path, str]]`  
**Purpose:** Import all inbox records, preserving failed source files.

**Direct calls observed in the function body:** `import_inbox_item`, `inspect_inbox`, `results.append`.

**Control-flow shape:** 0 conditional blocks, 1 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.storage.settings`

Per-user TOML application settings.

**Source:** `src/keys_ng/storage/settings.py`  
**Executable symbols:** 8

**Direct module dependencies:** `__future__`, `dataclasses`, `os`, `pathlib`, `platformdirs`, `tomllib`

<!-- symbol:keys_ng.storage.settings:_string_list -->
#### `_string_list`

**Kind:** function/method  
**Lines:** 11-16  
**Signature:** `def _string_list(value, name: str) -> list[str]`  
**Purpose:** Internal helper implementing `_string_list`.

**Direct calls observed in the function body:** `ValueError`, `all`, `isinstance`, `list`.

**Explicitly raised exceptions:** `ValueError`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.settings:_toml_string -->
#### `_toml_string`

**Kind:** function/method  
**Lines:** 19-20  
**Signature:** `def _toml_string(value: str) -> str`  
**Purpose:** Internal helper implementing `_toml_string`.

**Direct calls observed in the function body:** `replace`, `value.replace`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.settings:_toml_array -->
#### `_toml_array`

**Kind:** function/method  
**Lines:** 23-24  
**Signature:** `def _toml_array(values: list[str]) -> str`  
**Purpose:** Internal helper implementing `_toml_array`.

**Direct calls observed in the function body:** `_toml_string`, `join`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.settings:AppSettings -->
#### `AppSettings`

**Kind:** class  
**Lines:** 28-164  
**Declared fields:** `language`, `clipboard_password_timeout`, `clipboard_totp_timeout`, `auto_lock_timeout`, `crypto_backend`, `gpg_executable`, `gpgconf_executable`, `tree_startup_view`, `recent_vaults`, `tui_clipboard_notice_background`, `tui_clipboard_notice_foreground`, `tui_clipboard_notice_seconds`, `diagnostics_enabled`, `diagnostics_level`, `diagnostics_log_file`, `diagnostics_max_bytes`, `diagnostics_backup_count`, `ssh_terminal`, `ssh_terminal_options`, `rdp_linux_client`, `rdp_linux_options`, `rdp_windows_client`, `rdp_windows_options`, `rdp_macos_client`, `rdp_macos_options`  
**Methods:** `default_path`, `load`, `remember_vault`, `save`  
**Responsibility:** Validated application preferences loaded from/saved to TOML.

<!-- symbol:keys_ng.storage.settings:AppSettings.default_path -->
#### `AppSettings.default_path`

**Kind:** function/method  
**Lines:** 60-61  
**Signature:** `def default_path(cls) -> Path`  
**Purpose:** Implements the `default_path` operation in this module.

**Direct calls observed in the function body:** `Path`, `user_config_dir`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.settings:AppSettings.load -->
#### `AppSettings.load`

**Kind:** function/method  
**Lines:** 64-113  
**Signature:** `def load(cls, path: Path | None=None) -> 'AppSettings'`  
**Purpose:** Implements the `load` operation in this module.

**Direct calls observed in the function body:** `ValueError`, `_string_list`, `bool`, `clipboard.get`, `cls`, `cls.default_path`, `data.get`, `diagnostics.get`, `float`, `gnupg.get`, `int`, `launchers.get`, `lower`, `max`, `min`, `path.exists`, `path.open`, `rdp.get`, `rdp_linux.get`, `rdp_macos.get`, `rdp_windows.get`, `security.get`, `ssh.get`, `str`, `strip`, `tomllib.load`, `tui.get`, `ui.get`, `upper`.

**Explicitly raised exceptions:** `ValueError`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 0 try blocks, 1 context managers, 2 explicit returns.

**Security-relevant effect categories:** filesystem, clipboard, parser/serialization.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.settings:AppSettings.remember_vault -->
#### `AppSettings.remember_vault`

**Kind:** function/method  
**Lines:** 116-119  
**Signature:** `def remember_vault(self, path: str | Path) -> None`  
**Purpose:** Implements the `remember_vault` operation in this module.

**Direct calls observed in the function body:** `Path`, `expanduser`, `resolve`, `str`.

**Object attributes written:** `self.recent_vaults`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.settings:AppSettings.save -->
#### `AppSettings.save`

**Kind:** function/method  
**Lines:** 121-164  
**Signature:** `def save(self, path: Path | None=None) -> Path`  
**Purpose:** Validates and persists state for `save`.

**Direct calls observed in the function body:** `_toml_array`, `_toml_string`, `lower`, `os.chmod`, `path.parent.mkdir`, `path.write_text`, `self.default_path`, `str`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.storage.vault`

Central vault service: encryption, signatures, catalog, records, folders, references and integrity binding.

**Source:** `src/keys_ng/storage/vault.py`  
**Executable symbols:** 42

**Direct module dependencies:** `__future__`, `dataclasses`, `hashlib`, `keys_ng.crypto.backend`, `keys_ng.errors`, `keys_ng.models`, `keys_ng.services.diagnostics`, `keys_ng.services.references`, `keys_ng.storage.atomic`, `keys_ng.storage.config`, `os`, `pathlib`, `time`, `urllib.parse`

<!-- symbol:keys_ng.storage.vault:Vault -->
#### `Vault`

**Kind:** class  
**Lines:** 26-544  
**Methods:** `__init__`, `init`, `recover_interrupted_writes`, `locked`, `lock`, `unlock`, `_require_unlocked`, `_verify`, `_encrypt`, `_decrypt`, `_write_catalog`, `_write_folders`, `load_catalog`, `load_folders`, `_catalog_item`, `_sync_catalog_folders`, `save_entry`, `_verify_record_binding`, `get_entry`, `resolve_reference_value`, `resolved_username`, `resolved_password`, `resolved_action`, `delete_entry`, `list_items`, `_folder_paths_from`, `folder_paths`, `search`, `reindex`, `catalog_health`, `list_folders`, `get_folder`, `folder_path`, `resolve_folder_path`, `create_folder`, `create_folder_path`, `rename_folder`, `move_folder`, `delete_folder`, `move_entry`  
**Responsibility:** Owns one vault instance and enforces its storage/security policy.

<!-- symbol:keys_ng.storage.vault:Vault.__init__ -->
#### `Vault.__init__`

**Kind:** function/method  
**Lines:** 27-37  
**Signature:** `def __init__(self, path: str | Path, crypto: CryptoBackend) -> None`  
**Purpose:** Internal helper implementing `__init__`.

**Direct calls observed in the function body:** `Path`, `VaultConfig.load`, `expanduser`, `resolve`, `self.recover_interrupted_writes`.

**Object attributes written:** `self._catalog_cache`, `self._folders_cache`, `self._locked`, `self.config`, `self.crypto`, `self.path`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.init -->
#### `Vault.init`

**Kind:** function/method  
**Lines:** 40-67  
**Signature:** `def init(cls, path: str | Path, crypto: CryptoBackend, recipients: list[str], signer: str | None, require_signature: bool=True, catalog_privacy: str='standard') -> 'Vault'`  
**Purpose:** Implements the `init` operation in this module.

**Direct calls observed in the function body:** `Catalog`, `FolderStore`, `Path`, `VaultConfig`, `VaultError`, `any`, `cls`, `config.to_json`, `config_path.write_text`, `expanduser`, `mkdir`, `os.chmod`, `resolve`, `root.exists`, `root.iterdir`, `vault._write_catalog`, `vault._write_folders`.

**Explicitly raised exceptions:** `VaultError`.

**Control-flow shape:** 3 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.recover_interrupted_writes -->
#### `Vault.recover_interrupted_writes`

**Kind:** function/method  
**Lines:** 69-73  
**Signature:** `def recover_interrupted_writes(self) -> int`  
**Purpose:** Implements the `recover_interrupted_writes` operation in this module.

**Direct calls observed in the function body:** `remove_stale_ciphertext_temps`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.locked -->
#### `Vault.locked`

**Kind:** function/method  
**Lines:** 76-77  
**Signature:** `def locked(self) -> bool`  
**Purpose:** Implements the `locked` operation in this module.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.lock -->
#### `Vault.lock`

**Kind:** function/method  
**Lines:** 79-84  
**Signature:** `def lock(self, hard: bool=False) -> None`  
**Purpose:** Implements the `lock` operation in this module.

**Direct calls observed in the function body:** `self.crypto.hard_lock`.

**Object attributes written:** `self._catalog_cache`, `self._folders_cache`, `self._locked`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** cryptography/key-agent.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.unlock -->
#### `Vault.unlock`

**Kind:** function/method  
**Lines:** 86-93  
**Signature:** `def unlock(self) -> None`  
**Purpose:** Implements the `unlock` operation in this module.

**Direct calls observed in the function body:** `self.load_catalog`, `self.load_folders`.

**Object attributes written:** `self._locked`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault._require_unlocked -->
#### `Vault._require_unlocked`

**Kind:** function/method  
**Lines:** 95-97  
**Signature:** `def _require_unlocked(self) -> None`  
**Purpose:** Internal helper implementing `_require_unlocked`.

**Direct calls observed in the function body:** `VaultError`.

**Explicitly raised exceptions:** `VaultError`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault._verify -->
#### `Vault._verify`

**Kind:** function/method  
**Lines:** 99-107  
**Signature:** `def _verify(self, signer_fingerprint: str | None, signature_valid: bool, primary_signer_fingerprint: str | None=None) -> None`  
**Purpose:** Internal helper implementing `_verify`.

**Direct calls observed in the function body:** `SignatureError`, `fp.upper`, `upper`.

**Explicitly raised exceptions:** `SignatureError`.

**Control-flow shape:** 3 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault._encrypt -->
#### `Vault._encrypt`

**Kind:** function/method  
**Lines:** 109-111  
**Signature:** `def _encrypt(self, plaintext: bytes) -> bytes`  
**Purpose:** Internal helper implementing `_encrypt`.

**Direct calls observed in the function body:** `self._require_unlocked`, `self.crypto.encrypt`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** cryptography/key-agent.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault._decrypt -->
#### `Vault._decrypt`

**Kind:** function/method  
**Lines:** 113-117  
**Signature:** `def _decrypt(self, ciphertext: bytes) -> bytes`  
**Purpose:** Internal helper implementing `_decrypt`.

**Direct calls observed in the function body:** `self._require_unlocked`, `self._verify`, `self.crypto.decrypt`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** cryptography/key-agent.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault._write_catalog -->
#### `Vault._write_catalog`

**Kind:** function/method  
**Lines:** 119-122  
**Signature:** `def _write_catalog(self, catalog: Catalog) -> None`  
**Purpose:** Internal helper implementing `_write_catalog`.

**Direct calls observed in the function body:** `atomic_write_ciphertext`, `catalog.to_bytes`, `self._encrypt`.

**Object attributes written:** `self._catalog_cache`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** cryptography/key-agent.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault._write_folders -->
#### `Vault._write_folders`

**Kind:** function/method  
**Lines:** 124-127  
**Signature:** `def _write_folders(self, store: FolderStore) -> None`  
**Purpose:** Internal helper implementing `_write_folders`.

**Direct calls observed in the function body:** `atomic_write_ciphertext`, `self._encrypt`, `store.to_bytes`.

**Object attributes written:** `self._folders_cache`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** cryptography/key-agent.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.load_catalog -->
#### `Vault.load_catalog`

**Kind:** function/method  
**Lines:** 129-138  
**Signature:** `def load_catalog(self) -> Catalog`  
**Purpose:** Loads and validates `load_catalog`.

**Direct calls observed in the function body:** `Catalog`, `Catalog.from_bytes`, `path.exists`, `path.read_bytes`, `self._decrypt`, `self._require_unlocked`.

**Object attributes written:** `self._catalog_cache`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Security-relevant effect categories:** filesystem, cryptography/key-agent.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.load_folders -->
#### `Vault.load_folders`

**Kind:** function/method  
**Lines:** 140-151  
**Signature:** `def load_folders(self) -> FolderStore`  
**Purpose:** Loads and validates `load_folders`.

**Direct calls observed in the function body:** `FolderStore`, `FolderStore.from_bytes`, `list`, `path.exists`, `path.read_bytes`, `self._decrypt`, `self._require_unlocked`, `self.load_catalog`.

**Object attributes written:** `self._folders_cache`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Security-relevant effect categories:** filesystem, cryptography/key-agent.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault._catalog_item -->
#### `Vault._catalog_item`

**Kind:** function/method  
**Lines:** 153-182  
**Signature:** `def _catalog_item(self, entry: Entry, ciphertext: bytes) -> CatalogItem`  
**Purpose:** Internal helper implementing `_catalog_item`.

**Direct calls observed in the function body:** `CatalogItem`, `capabilities.append`, `capabilities.extend`, `hexdigest`, `hosts.append`, `set`, `sha256`, `sorted`, `urlparse`.

**Control-flow shape:** 6 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault._sync_catalog_folders -->
#### `Vault._sync_catalog_folders`

**Kind:** function/method  
**Lines:** 184-188  
**Signature:** `def _sync_catalog_folders(self, catalog: Catalog | None=None, store: FolderStore | None=None) -> Catalog`  
**Purpose:** Internal helper implementing `_sync_catalog_folders`.

**Direct calls observed in the function body:** `list`, `self.load_catalog`, `self.load_folders`.

**Object attributes written:** `catalog.folders`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.save_entry -->
#### `Vault.save_entry`

**Kind:** function/method  
**Lines:** 190-205  
**Signature:** `def save_entry(self, entry: Entry) -> Entry`  
**Purpose:** Validates and persists state for `save_entry`.

**Direct calls observed in the function body:** `VaultError`, `atomic_write_ciphertext`, `catalog.items.append`, `catalog.items.sort`, `entry.to_bytes`, `entry.validate`, `self._catalog_item`, `self._encrypt`, `self._require_unlocked`, `self._sync_catalog_folders`, `self._write_catalog`, `self.load_catalog`, `self.load_folders`, `utc_now`, `x.title.casefold`.

**Explicitly raised exceptions:** `VaultError`.

**Object attributes written:** `catalog.items`, `entry.updated_at`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** cryptography/key-agent.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault._verify_record_binding -->
#### `Vault._verify_record_binding`

**Kind:** function/method  
**Lines:** 207-223  
**Signature:** `def _verify_record_binding(self, entry_id: str, ciphertext: bytes, entry: Entry) -> None`  
**Purpose:** Bind a decrypted record to its signed catalog snapshot. This detects replacement or rollback of a single record while the catalog remains current. It intentionally does not claim protection against an attacker who rolls back the record and the signed catalog together.

**Direct calls observed in the function body:** `VaultError`, `hexdigest`, `next`, `self.load_catalog`, `sha256`.

**Explicitly raised exceptions:** `VaultError`.

**Control-flow shape:** 4 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.get_entry -->
#### `Vault.get_entry`

**Kind:** function/method  
**Lines:** 225-246  
**Signature:** `def get_entry(self, entry_id: str) -> Entry`  
**Purpose:** Retrieves `get_entry`.

**Direct calls observed in the function body:** `Entry.from_bytes`, `VaultError`, `_LOG.debug`, `_LOG.info`, `_LOG.warning`, `elapsed_ms`, `len`, `path.exists`, `path.read_bytes`, `self._decrypt`, `self._require_unlocked`, `self._verify_record_binding`, `time.perf_counter`.

**Explicitly raised exceptions:** `VaultError`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** filesystem, cryptography/key-agent.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.resolve_reference_value -->
#### `Vault.resolve_reference_value`

**Kind:** function/method  
**Lines:** 248-281  
**Signature:** `def resolve_reference_value(self, value: str | None, *, _stack: tuple[tuple[str, str], ...]=(), _max_depth: int=32) -> str | None`  
**Purpose:** Resolve a KeePassXC-style UUID reference stored as a whole field. Keys NG intentionally implements the UUID subset requested for reusable credentials: {REF:U@I:<UUID>} and {REF:P@I:<UUID>}. References can be chained, but cycles and excessive nesting are rejected.

**Direct calls observed in the function body:** `ReferenceError`, `join`, `len`, `parse_entry_reference`, `self.get_entry`, `self.resolve_reference_value`.

**Explicitly raised exceptions:** `ReferenceError`.

**Control-flow shape:** 5 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.resolved_username -->
#### `Vault.resolved_username`

**Kind:** function/method  
**Lines:** 283-286  
**Signature:** `def resolved_username(self, entry: Entry | str) -> str | None`  
**Purpose:** Implements the `resolved_username` operation in this module.

**Direct calls observed in the function body:** `isinstance`, `self.get_entry`, `self.resolve_reference_value`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.resolved_password -->
#### `Vault.resolved_password`

**Kind:** function/method  
**Lines:** 288-290  
**Signature:** `def resolved_password(self, entry: Entry | str) -> str | None`  
**Purpose:** Implements the `resolved_password` operation in this module.

**Direct calls observed in the function body:** `isinstance`, `self.get_entry`, `self.resolve_reference_value`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.resolved_action -->
#### `Vault.resolved_action`

**Kind:** function/method  
**Lines:** 292-298  
**Signature:** `def resolved_action(self, entry: Entry, action: Action) -> Action`  
**Purpose:** Return an action with any UUID-referenced username resolved.

**Direct calls observed in the function body:** `replace`, `self.resolve_reference_value`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.delete_entry -->
#### `Vault.delete_entry`

**Kind:** function/method  
**Lines:** 300-309  
**Signature:** `def delete_entry(self, entry_id: str) -> None`  
**Purpose:** Deletes `delete_entry`.

**Direct calls observed in the function body:** `VaultError`, `path.unlink`, `self._require_unlocked`, `self._write_catalog`, `self.load_catalog`.

**Explicitly raised exceptions:** `VaultError`.

**Object attributes written:** `catalog.items`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.list_items -->
#### `Vault.list_items`

**Kind:** function/method  
**Lines:** 311-325  
**Signature:** `def list_items(self, folder_id: str | None=None, recursive: bool=False) -> list[CatalogItem]`  
**Purpose:** Returns a filtered/listed view of `list_items`.

**Direct calls observed in the function body:** `allowed.add`, `self.load_catalog`, `self.load_folders`.

**Control-flow shape:** 3 conditional blocks, 2 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault._folder_paths_from -->
#### `Vault._folder_paths_from`

**Kind:** function/method  
**Lines:** 328-354  
**Signature:** `def _folder_paths_from(folders: list[Folder]) -> dict[str, str]`  
**Purpose:** Build all folder paths in O(n) without repeated vault decryptions.

**Direct calls observed in the function body:** `VaultError`, `by_id.get`, `resolve`, `set`, `visiting.add`, `visiting.remove`.

**Explicitly raised exceptions:** `VaultError`.

**Control-flow shape:** 4 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 3 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault._folder_paths_from.resolve -->
#### `Vault._folder_paths_from.resolve`

**Kind:** function/method  
**Lines:** 333-350  
**Signature:** `def resolve(folder_id: str, visiting: set[str] | None=None) -> str`  
**Purpose:** Implements the `resolve` operation in this module.

**Direct calls observed in the function body:** `VaultError`, `by_id.get`, `resolve`, `set`, `visiting.add`, `visiting.remove`.

**Explicitly raised exceptions:** `VaultError`.

**Control-flow shape:** 4 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.folder_paths -->
#### `Vault.folder_paths`

**Kind:** function/method  
**Lines:** 356-358  
**Signature:** `def folder_paths(self, *, catalog_snapshot: bool=False) -> dict[str, str]`  
**Purpose:** Implements the `folder_paths` operation in this module.

**Direct calls observed in the function body:** `self._folder_paths_from`, `self.load_catalog`, `self.load_folders`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.search -->
#### `Vault.search`

**Kind:** function/method  
**Lines:** 360-375  
**Signature:** `def search(self, query: str) -> list[CatalogItem]`  
**Purpose:** Implements the `search` operation in this module.

**Direct calls observed in the function body:** `casefold`, `folder_names.get`, `join`, `list`, `matches.append`, `query.casefold`, `self._folder_paths_from`, `self.load_catalog`, `strip`.

**Control-flow shape:** 2 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.reindex -->
#### `Vault.reindex`

**Kind:** function/method  
**Lines:** 377-387  
**Signature:** `def reindex(self) -> Catalog`  
**Purpose:** Implements the `reindex` operation in this module.

**Direct calls observed in the function body:** `Catalog`, `Entry.from_bytes`, `glob`, `items.append`, `list`, `path.read_bytes`, `self._catalog_item`, `self._decrypt`, `self._require_unlocked`, `self._write_catalog`, `self.load_folders`, `sorted`, `x.title.casefold`.

**Control-flow shape:** 0 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** filesystem, cryptography/key-agent.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.catalog_health -->
#### `Vault.catalog_health`

**Kind:** function/method  
**Lines:** 389-410  
**Signature:** `def catalog_health(self) -> tuple[bool, list[str]]`  
**Purpose:** Implements the `catalog_health` operation in this module.

**Direct calls observed in the function body:** `by_id.get`, `glob`, `hexdigest`, `issues.append`, `path.read_bytes`, `self.load_catalog`, `self.load_folders`, `set`, `sha256`, `sorted`.

**Control-flow shape:** 4 conditional blocks, 2 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.list_folders -->
#### `Vault.list_folders`

**Kind:** function/method  
**Lines:** 413-416  
**Signature:** `def list_folders(self) -> list[Folder]`  
**Purpose:** Returns a filtered/listed view of `list_folders`.

**Direct calls observed in the function body:** `casefold`, `list`, `self._folder_paths_from`, `self.load_folders`, `sorted`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.get_folder -->
#### `Vault.get_folder`

**Kind:** function/method  
**Lines:** 418-422  
**Signature:** `def get_folder(self, folder_id: str) -> Folder`  
**Purpose:** Retrieves `get_folder`.

**Direct calls observed in the function body:** `VaultError`, `self.load_folders`.

**Explicitly raised exceptions:** `VaultError`.

**Control-flow shape:** 1 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.folder_path -->
#### `Vault.folder_path`

**Kind:** function/method  
**Lines:** 424-430  
**Signature:** `def folder_path(self, folder_id: str | None) -> str`  
**Purpose:** Implements the `folder_path` operation in this module.

**Direct calls observed in the function body:** `VaultError`, `self.folder_paths`.

**Explicitly raised exceptions:** `VaultError`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.resolve_folder_path -->
#### `Vault.resolve_folder_path`

**Kind:** function/method  
**Lines:** 432-445  
**Signature:** `def resolve_folder_path(self, path: str) -> str | None`  
**Purpose:** Resolves `resolve_folder_path`.

**Direct calls observed in the function body:** `VaultError`, `folder.name.casefold`, `len`, `part.casefold`, `path.replace`, `path.strip`, `self.load_folders`, `split`, `strip`.

**Explicitly raised exceptions:** `VaultError`.

**Control-flow shape:** 3 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.create_folder -->
#### `Vault.create_folder`

**Kind:** function/method  
**Lines:** 447-462  
**Signature:** `def create_folder(self, name: str, parent_id: str | None=None) -> Folder`  
**Purpose:** Creates `create_folder`.

**Direct calls observed in the function body:** `Folder.create`, `VaultError`, `any`, `casefold`, `folder.name.casefold`, `folder.validate`, `name.strip`, `self._require_unlocked`, `self._sync_catalog_folders`, `self._write_catalog`, `self._write_folders`, `self.load_catalog`, `self.load_folders`, `store.folders.append`, `store.validate`.

**Explicitly raised exceptions:** `VaultError`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.create_folder_path -->
#### `Vault.create_folder_path`

**Kind:** function/method  
**Lines:** 464-478  
**Signature:** `def create_folder_path(self, path: str) -> Folder | None`  
**Purpose:** Creates `create_folder_path`.

**Direct calls observed in the function body:** `folder.name.casefold`, `next`, `normalized.replace`, `part.casefold`, `path.strip`, `self.create_folder`, `self.load_folders`, `split`, `strip`.

**Control-flow shape:** 2 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.rename_folder -->
#### `Vault.rename_folder`

**Kind:** function/method  
**Lines:** 480-496  
**Signature:** `def rename_folder(self, folder_id: str, new_name: str) -> Folder`  
**Purpose:** Implements the `rename_folder` operation in this module.

**Direct calls observed in the function body:** `FolderStore`, `VaultError`, `any`, `new_name.strip`, `next`, `normalized.casefold`, `other.name.casefold`, `replace`, `self._sync_catalog_folders`, `self._write_catalog`, `self._write_folders`, `self.load_catalog`, `self.load_folders`, `store.validate`, `utc_now`.

**Explicitly raised exceptions:** `VaultError`.

**Object attributes written:** `folder.name`, `folder.updated_at`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.move_folder -->
#### `Vault.move_folder`

**Kind:** function/method  
**Lines:** 498-521  
**Signature:** `def move_folder(self, folder_id: str, parent_id: str | None) -> Folder`  
**Purpose:** Implements the `move_folder` operation in this module.

**Direct calls observed in the function body:** `FolderStore`, `VaultError`, `any`, `by_id.get`, `folder.name.casefold`, `other.name.casefold`, `replace`, `self._sync_catalog_folders`, `self._write_catalog`, `self._write_folders`, `self.load_catalog`, `self.load_folders`, `store.validate`, `utc_now`.

**Explicitly raised exceptions:** `VaultError`.

**Object attributes written:** `folder.parent_id`, `folder.updated_at`.

**Control-flow shape:** 4 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.delete_folder -->
#### `Vault.delete_folder`

**Kind:** function/method  
**Lines:** 523-536  
**Signature:** `def delete_folder(self, folder_id: str) -> None`  
**Purpose:** Deletes `delete_folder`.

**Direct calls observed in the function body:** `VaultError`, `any`, `len`, `self._sync_catalog_folders`, `self._write_catalog`, `self._write_folders`, `self.load_catalog`, `self.load_folders`.

**Explicitly raised exceptions:** `VaultError`.

**Object attributes written:** `store.folders`.

**Control-flow shape:** 3 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.storage.vault:Vault.move_entry -->
#### `Vault.move_entry`

**Kind:** function/method  
**Lines:** 538-544  
**Signature:** `def move_entry(self, entry_id: str, folder_id: str | None) -> Entry`  
**Purpose:** Implements the `move_entry` operation in this module.

**Direct calls observed in the function body:** `VaultError`, `self.get_entry`, `self.load_folders`, `self.save_entry`.

**Explicitly raised exceptions:** `VaultError`.

**Object attributes written:** `entry.folder_id`, `entry.revision`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

### `keys_ng.tui.main`

Textual terminal UI and its actions/bindings.

**Source:** `src/keys_ng/tui/main.py`  
**Executable symbols:** 148

**Direct module dependencies:** `__future__`, `argparse`, `keys_ng`, `keys_ng.crypto.factory`, `keys_ng.i18n`, `keys_ng.migration.keepassxc`, `keys_ng.migration.keepassxc_export`, `keys_ng.platform.app_identity`, `keys_ng.services.actions`, `keys_ng.services.clipboard`, `keys_ng.services.diagnostics`, `keys_ng.services.entry_editor`, `keys_ng.services.passwords`, `keys_ng.services.qr`, `keys_ng.services.totp`, `keys_ng.services.trusted_signers`, `keys_ng.services.vault_init`, `keys_ng.services.vault_sessions`, `keys_ng.storage.inbox`, `keys_ng.storage.settings`, `keys_ng.storage.vault`, `pathlib`, `sys`

<!-- symbol:keys_ng.tui.main:main -->
#### `main`

**Kind:** function/method  
**Lines:** 32-1437  
**Signature:** `def main() -> None`  
**Purpose:** Implements the `main` operation in this module.

**Direct calls observed in the function body:** `AppSettings.load`, `Binding`, `Button`, `Checkbox`, `ChoiceScreen`, `ConfirmScreen`, `EntryDraft`, `EntryDraft.from_entry`, `EntryEditorScreen`, `ExportVaultScreen`, `Footer`, `Header`, `HelpScreen`, `Horizontal`, `InboxScreen`, `Input`, `KeePassXCImportScreen`, `KeysApp`, `Label`, `MoveScreen`, `NameScreen`, `PasswordGeneratorScreen`, `Path`, `Path.cwd`, `Path.home`, `PreferencesScreen`, `Select`, `Static`, `SystemExit`, `TextArea`, `Tree`, `TrustedSignersScreen`, `ValueError`, `Vault`, `VaultCreationApp`, `VaultInitRequest`, `VaultSessionManager`, `VaultStartApp`, `VaultSwitcherScreen`, `Vertical`, `VerticalScroll`, `_`, `__init__`, `_select_value_is_blank`, `add_trusted_signer`, `argparse.ArgumentParser`, `available_vault_keys`, `banner.add_class`, `banner.remove_class`, `banner.update`, `bool`, `build_entry_from_draft`, `build_otpauth_uri`, `ch.isalnum`, `choose_vault`, `configure_diagnostics`, `configure_language`, `copy_secret_cli`, `create_crypto_backend`, `create_vault`, `current_language`, `delete_inbox_item`, `eligible_signing_keys`, `enumerate`, `event.value.strip`, `exists`, `expanduser`, `export_entry_xml`, `export_vault_xml`, `files`, `focus`, `folder_nodes.get`, `folder_options`, `format`, `format_import_report`, `generate_password`, `generate_totp`, `get`, `get_logger`, `getattr`, `import_inbox_item`, `import_keepassxc`, `info`, `inspect_inbox`, `int`, `isinstance`, `join`, `joinpath`, `launch_action`, `len`, `list`, `list_trusted_signers`, `load_text`, `next`, `options.append`, `parent.add`, `parent.add_leaf`, `parse_totp_qr_file`, `parser.add_argument`, `parser.parse_args`, `paths.get`, `pending_inbox_paths`, `print`, `remaining.remove`, `remove_trusted_signer`, `resolve`, `resource.is_file`, `resource.read_text`, `root.joinpath`, `run`, `select.set_options`, `self._activate_opened_vault`, `self._banner_timer.stop`, `self._collect`, `self._copy`, `self._copy_generated`, `self._display_active_vault`, `self._finish_edit_entry`, `self._finish_export_entry`, `self._finish_open_vault`, `self._generate`, `self._load_qr`, `self._refresh_after_mutation`, `self._reset_selection`, `self._run`, `self._show_clipboard_banner`, `self._status`, `self._text`, `self._toggle_password_visibility`, `self._update_command_hints`, `self.action_cancel`, `self.action_close`, `self.action_reload_tree`, `self.action_save`, `self.app.copy_to_clipboard`, `self.app.push_screen`, `self.copy_to_clipboard`, `self.dismiss`, `self.exit`, `self.push_screen`, `self.query_one`, `self.rebuild_tree`, `self.refresh_inbox`, `self.refresh_signers`, `self.selected`, `self.set_timer`, `self.show_item`, `sessions.activate`, `sessions.add`, `sessions.close`, `sessions.contains`, `sessions.lock_all`, `sessions.opened`, `set_textual_terminal_title`, `settings.remember_vault`, `settings.save`, `status.update`, `str`, `strip`, `super`, `tree.clear`, `tree.root.add_leaf`, `tree.root.expand`, `tree.root.set_label`, `type`, `update`, `value.startswith`, `value.strip`, `vault.create_folder`, `vault.crypto.hard_lock`, `vault.delete_entry`, `vault.delete_folder`, `vault.folder_path`, `vault.folder_paths`, `vault.get_entry`, `vault.get_folder`, `vault.list_folders`, `vault.list_items`, `vault.lock`, `vault.move_entry`, `vault.move_folder`, `vault.rename_folder`, `vault.resolved_action`, `vault.resolved_password`, `vault.resolved_username`, `vault.save_entry`, `vault.search`, `vault.unlock`, `write_export`.

**Explicitly raised exceptions:** `SystemExit`, `ValueError`.

**Object attributes written:** `banner.styles.background`, `banner.styles.color`, `password_input.password`, `select.value`, `self._banner_timer`, `self._inbox_notice_shown`, `self.confirm_label`, `self.current_entry`, `self.current_folder_id`, `self.current_id`, `self.current_kind`, `self.destructive`, `self.dialog_title`, `self.draft`, `self.exclude_id`, `self.items`, `self.message`, `self.options`, `self.resource_name`, `self.selected`, `self.title`, `self.title_text`, `self.value`, `settings.auto_lock_timeout`, `settings.clipboard_password_timeout`, `settings.clipboard_totp_timeout`, `settings.diagnostics_enabled`, `settings.gpg_executable`, `settings.gpgconf_executable`, `settings.language`, `settings.tree_startup_view`, `toggle.label`, `value`.

**Control-flow shape:** 134 conditional blocks, 10 loops, 40 try blocks, 47 context managers, 69 explicit returns.

**Security-relevant effect categories:** process, filesystem, cryptography/key-agent, clipboard.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.VaultCreationApp -->
#### `main.VaultCreationApp`

**Kind:** class  
**Lines:** 70-133  
**Bases:** `App[str | None]`  
**Methods:** `compose`, `on_button_pressed`, `action_cancel`  
**Responsibility:** Standalone keyboard-first onboarding wizard used when no vault is supplied.

<!-- symbol:keys_ng.tui.main:main.VaultCreationApp.compose -->
#### `main.VaultCreationApp.compose`

**Kind:** function/method  
**Lines:** 84-104  
**Signature:** `def compose(self) -> ComposeResult`  
**Purpose:** Implements the `compose` operation in this module.

**Direct calls observed in the function body:** `Button`, `Checkbox`, `Horizontal`, `Input`, `Label`, `Path.home`, `Select`, `Static`, `Vertical`, `_`, `available_vault_keys`, `str`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 2 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.VaultCreationApp.on_button_pressed -->
#### `main.VaultCreationApp.on_button_pressed`

**Kind:** function/method  
**Lines:** 106-130  
**Signature:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Purpose:** Implements the `on_button_pressed` operation in this module.

**Direct calls observed in the function body:** `ValueError`, `VaultInitRequest`, `_`, `bool`, `create_vault`, `self.exit`, `self.query_one`, `str`, `update`, `value.strip`.

**Explicitly raised exceptions:** `ValueError`.

**Control-flow shape:** 4 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.VaultCreationApp.action_cancel -->
#### `main.VaultCreationApp.action_cancel`

**Kind:** function/method  
**Lines:** 132-133  
**Signature:** `def action_cancel(self) -> None`  
**Purpose:** Implements the `action_cancel` operation in this module.

**Direct calls observed in the function body:** `self.exit`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.VaultStartApp -->
#### `main.VaultStartApp`

**Kind:** class  
**Lines:** 135-160  
**Bases:** `App[str | None]`  
**Methods:** `compose`, `on_select_changed`, `on_button_pressed`  
**Responsibility:** Start screen for opening, creating, or selecting a recent vault.

<!-- symbol:keys_ng.tui.main:main.VaultStartApp.compose -->
#### `main.VaultStartApp.compose`

**Kind:** function/method  
**Lines:** 142-153  
**Signature:** `def compose(self) -> ComposeResult`  
**Purpose:** Implements the `compose` operation in this module.

**Direct calls observed in the function body:** `Button`, `Horizontal`, `Input`, `Label`, `Path`, `Path.home`, `Select`, `Static`, `Vertical`, `_`, `exists`, `str`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 2 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.VaultStartApp.on_select_changed -->
#### `main.VaultStartApp.on_select_changed`

**Kind:** function/method  
**Lines:** 154-156  
**Signature:** `def on_select_changed(self, event: Select.Changed) -> None`  
**Purpose:** Implements the `on_select_changed` operation in this module.

**Direct calls observed in the function body:** `_select_value_is_blank`, `self.query_one`, `str`.

**Object attributes written:** `value`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.VaultStartApp.on_button_pressed -->
#### `main.VaultStartApp.on_button_pressed`

**Kind:** function/method  
**Lines:** 157-160  
**Signature:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Purpose:** Implements the `on_button_pressed` operation in this module.

**Direct calls observed in the function body:** `self.exit`, `self.query_one`, `value.strip`.

**Control-flow shape:** 3 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.choose_vault -->
#### `main.choose_vault`

**Kind:** function/method  
**Lines:** 162-179  
**Signature:** `def choose_vault(path: str | None=None) -> str | None`  
**Purpose:** Implements the `choose_vault` operation in this module.

**Direct calls observed in the function body:** `Path`, `VaultCreationApp`, `VaultStartApp`, `expanduser`, `resolve`, `run`, `settings.remember_vault`, `settings.save`, `str`.

**Control-flow shape:** 5 conditional blocks, 1 loops, 1 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.folder_options -->
#### `main.folder_options`

**Kind:** function/method  
**Lines:** 187-192  
**Signature:** `def folder_options(exclude_id: str | None=None) -> list[tuple[str, str]]`  
**Purpose:** Implements the `folder_options` operation in this module.

**Direct calls observed in the function body:** `_`, `options.append`, `vault.folder_path`, `vault.list_folders`.

**Control-flow shape:** 1 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.PasswordGeneratorScreen -->
#### `main.PasswordGeneratorScreen`

**Kind:** class  
**Lines:** 194-251  
**Bases:** `ModalScreen[str | None]`  
**Methods:** `compose`, `on_mount`, `_generate`, `_copy_generated`, `on_button_pressed`, `action_cancel`  
**Responsibility:** Implements the `PasswordGeneratorScreen` operation in this module.

<!-- symbol:keys_ng.tui.main:main.PasswordGeneratorScreen.compose -->
#### `main.PasswordGeneratorScreen.compose`

**Kind:** function/method  
**Lines:** 201-216  
**Signature:** `def compose(self) -> ComposeResult`  
**Purpose:** Implements the `compose` operation in this module.

**Direct calls observed in the function body:** `Button`, `Checkbox`, `Horizontal`, `Input`, `Label`, `Static`, `Vertical`, `_`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 2 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.PasswordGeneratorScreen.on_mount -->
#### `main.PasswordGeneratorScreen.on_mount`

**Kind:** function/method  
**Lines:** 217-217  
**Signature:** `def on_mount(self) -> None`  
**Purpose:** Implements the `on_mount` operation in this module.

**Direct calls observed in the function body:** `self._generate`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.PasswordGeneratorScreen._generate -->
#### `main.PasswordGeneratorScreen._generate`

**Kind:** function/method  
**Lines:** 218-230  
**Signature:** `def _generate(self) -> None`  
**Purpose:** Internal helper implementing `_generate`.

**Direct calls observed in the function body:** `_`, `generate_password`, `int`, `self.query_one`.

**Object attributes written:** `value`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.PasswordGeneratorScreen._copy_generated -->
#### `main.PasswordGeneratorScreen._copy_generated`

**Kind:** function/method  
**Lines:** 231-244  
**Signature:** `def _copy_generated(self) -> None`  
**Purpose:** Internal helper implementing `_copy_generated`.

**Direct calls observed in the function body:** `_`, `copy_secret_cli`, `self.app.copy_to_clipboard`, `self.query_one`, `status.update`, `type`, `value.startswith`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 2 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** clipboard.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.PasswordGeneratorScreen.on_button_pressed -->
#### `main.PasswordGeneratorScreen.on_button_pressed`

**Kind:** function/method  
**Lines:** 246-250  
**Signature:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Purpose:** Implements the `on_button_pressed` operation in this module.

**Direct calls observed in the function body:** `self._copy_generated`, `self._generate`, `self.dismiss`, `self.query_one`.

**Control-flow shape:** 3 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.PasswordGeneratorScreen.action_cancel -->
#### `main.PasswordGeneratorScreen.action_cancel`

**Kind:** function/method  
**Lines:** 251-251  
**Signature:** `def action_cancel(self) -> None`  
**Purpose:** Implements the `action_cancel` operation in this module.

**Direct calls observed in the function body:** `self.dismiss`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeePassXCImportScreen -->
#### `main.KeePassXCImportScreen`

**Kind:** class  
**Lines:** 253-292  
**Bases:** `ModalScreen[bool]`  
**Methods:** `compose`, `_run`, `on_button_pressed`, `action_close`  
**Responsibility:** Implements the `KeePassXCImportScreen` operation in this module.

<!-- symbol:keys_ng.tui.main:main.KeePassXCImportScreen.compose -->
#### `main.KeePassXCImportScreen.compose`

**Kind:** function/method  
**Lines:** 261-273  
**Signature:** `def compose(self) -> ComposeResult`  
**Purpose:** Implements the `compose` operation in this module.

**Direct calls observed in the function body:** `Button`, `Checkbox`, `Horizontal`, `Input`, `Label`, `Static`, `TextArea`, `Vertical`, `_`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 2 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeePassXCImportScreen._run -->
#### `main.KeePassXCImportScreen._run`

**Kind:** function/method  
**Lines:** 274-283  
**Signature:** `def _run(self, dry_run: bool)`  
**Purpose:** Internal helper implementing `_run`.

**Direct calls observed in the function body:** `ValueError`, `_`, `import_keepassxc`, `self.query_one`, `value.strip`.

**Explicitly raised exceptions:** `ValueError`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeePassXCImportScreen.on_button_pressed -->
#### `main.KeePassXCImportScreen.on_button_pressed`

**Kind:** function/method  
**Lines:** 284-291  
**Signature:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Purpose:** Implements the `on_button_pressed` operation in this module.

**Direct calls observed in the function body:** `_`, `format_import_report`, `load_text`, `self._run`, `self.dismiss`, `self.query_one`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Security-relevant effect categories:** process.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeePassXCImportScreen.action_close -->
#### `main.KeePassXCImportScreen.action_close`

**Kind:** function/method  
**Lines:** 292-292  
**Signature:** `def action_close(self) -> None`  
**Purpose:** Implements the `action_close` operation in this module.

**Direct calls observed in the function body:** `self.dismiss`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.ExportVaultScreen -->
#### `main.ExportVaultScreen`

**Kind:** class  
**Lines:** 294-306  
**Bases:** `ModalScreen[str | None]`  
**Methods:** `compose`, `on_button_pressed`  
**Responsibility:** Implements the `ExportVaultScreen` operation in this module.

<!-- symbol:keys_ng.tui.main:main.ExportVaultScreen.compose -->
#### `main.ExportVaultScreen.compose`

**Kind:** function/method  
**Lines:** 296-304  
**Signature:** `def compose(self) -> ComposeResult`  
**Purpose:** Implements the `compose` operation in this module.

**Direct calls observed in the function body:** `Button`, `Horizontal`, `Input`, `Path.cwd`, `Static`, `Vertical`, `_`, `str`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 2 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.ExportVaultScreen.on_button_pressed -->
#### `main.ExportVaultScreen.on_button_pressed`

**Kind:** function/method  
**Lines:** 305-306  
**Signature:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Purpose:** Implements the `on_button_pressed` operation in this module.

**Direct calls observed in the function body:** `self.dismiss`, `self.query_one`, `value.strip`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.PreferencesScreen -->
#### `main.PreferencesScreen`

**Kind:** class  
**Lines:** 308-336  
**Bases:** `ModalScreen[bool]`  
**Methods:** `compose`, `on_button_pressed`  
**Responsibility:** Implements the `PreferencesScreen` operation in this module.

<!-- symbol:keys_ng.tui.main:main.PreferencesScreen.compose -->
#### `main.PreferencesScreen.compose`

**Kind:** function/method  
**Lines:** 310-323  
**Signature:** `def compose(self) -> ComposeResult`  
**Purpose:** Implements the `compose` operation in this module.

**Direct calls observed in the function body:** `Button`, `Checkbox`, `Horizontal`, `Input`, `Label`, `Select`, `Static`, `Vertical`, `VerticalScroll`, `_`, `str`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 3 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.PreferencesScreen.on_button_pressed -->
#### `main.PreferencesScreen.on_button_pressed`

**Kind:** function/method  
**Lines:** 324-336  
**Signature:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Purpose:** Implements the `on_button_pressed` operation in this module.

**Direct calls observed in the function body:** `int`, `self.dismiss`, `self.query_one`, `settings.save`, `str`, `value.strip`.

**Object attributes written:** `settings.auto_lock_timeout`, `settings.clipboard_password_timeout`, `settings.clipboard_totp_timeout`, `settings.diagnostics_enabled`, `settings.gpg_executable`, `settings.gpgconf_executable`, `settings.language`, `settings.tree_startup_view`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.HelpScreen -->
#### `main.HelpScreen`

**Kind:** class  
**Lines:** 338-356  
**Bases:** `ModalScreen[None]`  
**Methods:** `__init__`, `_text`, `compose`, `on_button_pressed`  
**Responsibility:** Implements the `HelpScreen` operation in this module.

<!-- symbol:keys_ng.tui.main:main.HelpScreen.__init__ -->
#### `main.HelpScreen.__init__`

**Kind:** function/method  
**Lines:** 340-341  
**Signature:** `def __init__(self, resource_name: str='README.md') -> None`  
**Purpose:** Internal helper implementing `__init__`.

**Direct calls observed in the function body:** `__init__`, `super`.

**Object attributes written:** `self.resource_name`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.HelpScreen._text -->
#### `main.HelpScreen._text`

**Kind:** function/method  
**Lines:** 342-351  
**Signature:** `def _text(self) -> str`  
**Purpose:** Internal helper implementing `_text`.

**Direct calls observed in the function body:** `_`, `current_language`, `files`, `joinpath`, `resource.is_file`, `resource.read_text`, `root.joinpath`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 2 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.HelpScreen.compose -->
#### `main.HelpScreen.compose`

**Kind:** function/method  
**Lines:** 352-355  
**Signature:** `def compose(self) -> ComposeResult`  
**Purpose:** Implements the `compose` operation in this module.

**Direct calls observed in the function body:** `Button`, `TextArea`, `Vertical`, `_`, `self._text`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 1 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.HelpScreen.on_button_pressed -->
#### `main.HelpScreen.on_button_pressed`

**Kind:** function/method  
**Lines:** 356-356  
**Signature:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Purpose:** Implements the `on_button_pressed` operation in this module.

**Direct calls observed in the function body:** `self.dismiss`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.EntryEditorScreen -->
#### `main.EntryEditorScreen`

**Kind:** class  
**Lines:** 358-515  
**Bases:** `ModalScreen[EntryDraft | None]`  
**Methods:** `__init__`, `compose`, `_collect`, `action_save`, `action_cancel`, `_finish_generated_password`, `_toggle_password_visibility`, `_load_qr`, `on_button_pressed`  
**Responsibility:** Keyboard-first full editor shared semantically with the GUI editor.

<!-- symbol:keys_ng.tui.main:main.EntryEditorScreen.__init__ -->
#### `main.EntryEditorScreen.__init__`

**Kind:** function/method  
**Lines:** 378-381  
**Signature:** `def __init__(self, draft: EntryDraft, title: str) -> None`  
**Purpose:** Internal helper implementing `__init__`.

**Direct calls observed in the function body:** `__init__`, `super`.

**Object attributes written:** `self.dialog_title`, `self.draft`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.EntryEditorScreen.compose -->
#### `main.EntryEditorScreen.compose`

**Kind:** function/method  
**Lines:** 383-455  
**Signature:** `def compose(self) -> ComposeResult`  
**Purpose:** Implements the `compose` operation in this module.

**Direct calls observed in the function body:** `Button`, `Horizontal`, `Input`, `Label`, `Select`, `Static`, `TextArea`, `Vertical`, `VerticalScroll`, `_`, `folder_options`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 17 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.EntryEditorScreen._collect -->
#### `main.EntryEditorScreen._collect`

**Kind:** function/method  
**Lines:** 457-474  
**Signature:** `def _collect(self) -> EntryDraft`  
**Purpose:** Internal helper implementing `_collect`.

**Direct calls observed in the function body:** `EntryDraft`, `self.query_one`, `str`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.EntryEditorScreen.action_save -->
#### `main.EntryEditorScreen.action_save`

**Kind:** function/method  
**Lines:** 476-477  
**Signature:** `def action_save(self) -> None`  
**Purpose:** Implements the `action_save` operation in this module.

**Direct calls observed in the function body:** `self._collect`, `self.dismiss`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.EntryEditorScreen.action_cancel -->
#### `main.EntryEditorScreen.action_cancel`

**Kind:** function/method  
**Lines:** 479-480  
**Signature:** `def action_cancel(self) -> None`  
**Purpose:** Implements the `action_cancel` operation in this module.

**Direct calls observed in the function body:** `self.dismiss`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.EntryEditorScreen._finish_generated_password -->
#### `main.EntryEditorScreen._finish_generated_password`

**Kind:** function/method  
**Lines:** 482-484  
**Signature:** `def _finish_generated_password(self, value: str | None) -> None`  
**Purpose:** Internal helper implementing `_finish_generated_password`.

**Direct calls observed in the function body:** `self.query_one`.

**Object attributes written:** `value`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.EntryEditorScreen._toggle_password_visibility -->
#### `main.EntryEditorScreen._toggle_password_visibility`

**Kind:** function/method  
**Lines:** 486-490  
**Signature:** `def _toggle_password_visibility(self) -> None`  
**Purpose:** Internal helper implementing `_toggle_password_visibility`.

**Direct calls observed in the function body:** `_`, `self.query_one`.

**Object attributes written:** `password_input.password`, `toggle.label`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.EntryEditorScreen._load_qr -->
#### `main.EntryEditorScreen._load_qr`

**Kind:** function/method  
**Lines:** 492-503  
**Signature:** `def _load_qr(self) -> None`  
**Purpose:** Internal helper implementing `_load_qr`.

**Direct calls observed in the function body:** `_`, `build_otpauth_uri`, `parse_totp_qr_file`, `self.query_one`, `update`, `value.strip`.

**Object attributes written:** `value`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.EntryEditorScreen.on_button_pressed -->
#### `main.EntryEditorScreen.on_button_pressed`

**Kind:** function/method  
**Lines:** 505-515  
**Signature:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Purpose:** Implements the `on_button_pressed` operation in this module.

**Direct calls observed in the function body:** `PasswordGeneratorScreen`, `self._load_qr`, `self._toggle_password_visibility`, `self.action_cancel`, `self.action_save`, `self.app.push_screen`.

**Control-flow shape:** 5 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.NameScreen -->
#### `main.NameScreen`

**Kind:** class  
**Lines:** 517-548  
**Bases:** `ModalScreen[str | None]`  
**Methods:** `__init__`, `compose`, `action_save`, `action_cancel`, `on_button_pressed`  
**Responsibility:** Small modal used for folder creation and rename.

<!-- symbol:keys_ng.tui.main:main.NameScreen.__init__ -->
#### `main.NameScreen.__init__`

**Kind:** function/method  
**Lines:** 527-530  
**Signature:** `def __init__(self, title: str, value: str='') -> None`  
**Purpose:** Internal helper implementing `__init__`.

**Direct calls observed in the function body:** `__init__`, `super`.

**Object attributes written:** `self.dialog_title`, `self.value`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.NameScreen.compose -->
#### `main.NameScreen.compose`

**Kind:** function/method  
**Lines:** 532-538  
**Signature:** `def compose(self) -> ComposeResult`  
**Purpose:** Implements the `compose` operation in this module.

**Direct calls observed in the function body:** `Button`, `Horizontal`, `Input`, `Static`, `Vertical`, `_`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 2 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.NameScreen.action_save -->
#### `main.NameScreen.action_save`

**Kind:** function/method  
**Lines:** 540-542  
**Signature:** `def action_save(self) -> None`  
**Purpose:** Implements the `action_save` operation in this module.

**Direct calls observed in the function body:** `self.dismiss`, `self.query_one`, `value.strip`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.NameScreen.action_cancel -->
#### `main.NameScreen.action_cancel`

**Kind:** function/method  
**Lines:** 544-545  
**Signature:** `def action_cancel(self) -> None`  
**Purpose:** Implements the `action_cancel` operation in this module.

**Direct calls observed in the function body:** `self.dismiss`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.NameScreen.on_button_pressed -->
#### `main.NameScreen.on_button_pressed`

**Kind:** function/method  
**Lines:** 547-548  
**Signature:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Purpose:** Implements the `on_button_pressed` operation in this module.

**Direct calls observed in the function body:** `self.action_cancel`, `self.action_save`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.MoveScreen -->
#### `main.MoveScreen`

**Kind:** class  
**Lines:** 550-582  
**Bases:** `ModalScreen[str | None | bool]`  
**Methods:** `__init__`, `compose`, `action_save`, `action_cancel`, `on_button_pressed`  
**Responsibility:** Choose a destination folder. False means cancelled; None means root.

<!-- symbol:keys_ng.tui.main:main.MoveScreen.__init__ -->
#### `main.MoveScreen.__init__`

**Kind:** function/method  
**Lines:** 560-564  
**Signature:** `def __init__(self, title: str, selected: str | None, exclude_id: str | None=None) -> None`  
**Purpose:** Internal helper implementing `__init__`.

**Direct calls observed in the function body:** `__init__`, `super`.

**Object attributes written:** `self.dialog_title`, `self.exclude_id`, `self.selected`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.MoveScreen.compose -->
#### `main.MoveScreen.compose`

**Kind:** function/method  
**Lines:** 566-572  
**Signature:** `def compose(self) -> ComposeResult`  
**Purpose:** Implements the `compose` operation in this module.

**Direct calls observed in the function body:** `Button`, `Horizontal`, `Select`, `Static`, `Vertical`, `_`, `folder_options`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 2 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.MoveScreen.action_save -->
#### `main.MoveScreen.action_save`

**Kind:** function/method  
**Lines:** 574-576  
**Signature:** `def action_save(self) -> None`  
**Purpose:** Implements the `action_save` operation in this module.

**Direct calls observed in the function body:** `self.dismiss`, `self.query_one`, `str`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.MoveScreen.action_cancel -->
#### `main.MoveScreen.action_cancel`

**Kind:** function/method  
**Lines:** 578-579  
**Signature:** `def action_cancel(self) -> None`  
**Purpose:** Implements the `action_cancel` operation in this module.

**Direct calls observed in the function body:** `self.dismiss`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.MoveScreen.on_button_pressed -->
#### `main.MoveScreen.on_button_pressed`

**Kind:** function/method  
**Lines:** 581-582  
**Signature:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Purpose:** Implements the `on_button_pressed` operation in this module.

**Direct calls observed in the function body:** `self.action_cancel`, `self.action_save`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.ConfirmScreen -->
#### `main.ConfirmScreen`

**Kind:** class  
**Lines:** 584-611  
**Bases:** `ModalScreen[bool]`  
**Methods:** `__init__`, `compose`, `action_no`, `on_button_pressed`  
**Responsibility:** Explicit confirmation screen for destructive and sensitive actions.

<!-- symbol:keys_ng.tui.main:main.ConfirmScreen.__init__ -->
#### `main.ConfirmScreen.__init__`

**Kind:** function/method  
**Lines:** 594-598  
**Signature:** `def __init__(self, message: str, confirm_label: str | None=None, *, destructive: bool=False) -> None`  
**Purpose:** Internal helper implementing `__init__`.

**Direct calls observed in the function body:** `_`, `__init__`, `super`.

**Object attributes written:** `self.confirm_label`, `self.destructive`, `self.message`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.ConfirmScreen.compose -->
#### `main.ConfirmScreen.compose`

**Kind:** function/method  
**Lines:** 600-605  
**Signature:** `def compose(self) -> ComposeResult`  
**Purpose:** Implements the `compose` operation in this module.

**Direct calls observed in the function body:** `Button`, `Horizontal`, `Static`, `Vertical`, `_`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 2 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.ConfirmScreen.action_no -->
#### `main.ConfirmScreen.action_no`

**Kind:** function/method  
**Lines:** 607-608  
**Signature:** `def action_no(self) -> None`  
**Purpose:** Implements the `action_no` operation in this module.

**Direct calls observed in the function body:** `self.dismiss`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.ConfirmScreen.on_button_pressed -->
#### `main.ConfirmScreen.on_button_pressed`

**Kind:** function/method  
**Lines:** 610-611  
**Signature:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Purpose:** Implements the `on_button_pressed` operation in this module.

**Direct calls observed in the function body:** `self.dismiss`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.TrustedSignersScreen -->
#### `main.TrustedSignersScreen`

**Kind:** class  
**Lines:** 613-680  
**Bases:** `ModalScreen[None]`  
**Methods:** `compose`, `on_mount`, `refresh_signers`, `action_close`, `on_select_changed`, `_finish_add`, `_finish_remove`, `on_button_pressed`  
**Responsibility:** Implements the `TrustedSignersScreen` operation in this module.

<!-- symbol:keys_ng.tui.main:main.TrustedSignersScreen.compose -->
#### `main.TrustedSignersScreen.compose`

**Kind:** function/method  
**Lines:** 621-630  
**Signature:** `def compose(self) -> ComposeResult`  
**Purpose:** Implements the `compose` operation in this module.

**Direct calls observed in the function body:** `Button`, `Horizontal`, `Select`, `Static`, `Vertical`, `_`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 2 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.TrustedSignersScreen.on_mount -->
#### `main.TrustedSignersScreen.on_mount`

**Kind:** function/method  
**Lines:** 632-633  
**Signature:** `def on_mount(self) -> None`  
**Purpose:** Implements the `on_mount` operation in this module.

**Direct calls observed in the function body:** `self.refresh_signers`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.TrustedSignersScreen.refresh_signers -->
#### `main.TrustedSignersScreen.refresh_signers`

**Kind:** function/method  
**Lines:** 635-643  
**Signature:** `def refresh_signers(self) -> None`  
**Purpose:** Implements the `refresh_signers` operation in this module.

**Direct calls observed in the function body:** `_`, `list_trusted_signers`, `select.set_options`, `self.query_one`, `update`.

**Object attributes written:** `select.value`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.TrustedSignersScreen.action_close -->
#### `main.TrustedSignersScreen.action_close`

**Kind:** function/method  
**Lines:** 645-646  
**Signature:** `def action_close(self) -> None`  
**Purpose:** Implements the `action_close` operation in this module.

**Direct calls observed in the function body:** `self.dismiss`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.TrustedSignersScreen.on_select_changed -->
#### `main.TrustedSignersScreen.on_select_changed`

**Kind:** function/method  
**Lines:** 648-650  
**Signature:** `def on_select_changed(self, event: Select.Changed) -> None`  
**Purpose:** Implements the `on_select_changed` operation in this module.

**Direct calls observed in the function body:** `_select_value_is_blank`, `self.query_one`, `str`, `update`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.TrustedSignersScreen._finish_add -->
#### `main.TrustedSignersScreen._finish_add`

**Kind:** function/method  
**Lines:** 652-658  
**Signature:** `def _finish_add(self, value) -> None`  
**Purpose:** Internal helper implementing `_finish_add`.

**Direct calls observed in the function body:** `_`, `add_trusted_signer`, `self.query_one`, `self.refresh_signers`, `str`, `update`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.TrustedSignersScreen._finish_remove -->
#### `main.TrustedSignersScreen._finish_remove`

**Kind:** function/method  
**Lines:** 660-667  
**Signature:** `def _finish_remove(self, confirmed: bool) -> None`  
**Purpose:** Internal helper implementing `_finish_remove`.

**Direct calls observed in the function body:** `_`, `_select_value_is_blank`, `remove_trusted_signer`, `self.query_one`, `self.refresh_signers`, `str`, `update`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.TrustedSignersScreen.on_button_pressed -->
#### `main.TrustedSignersScreen.on_button_pressed`

**Kind:** function/method  
**Lines:** 669-680  
**Signature:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Purpose:** Implements the `on_button_pressed` operation in this module.

**Direct calls observed in the function body:** `ChoiceScreen`, `ConfirmScreen`, `_`, `_select_value_is_blank`, `eligible_signing_keys`, `list_trusted_signers`, `self.action_close`, `self.app.push_screen`, `self.query_one`, `update`.

**Control-flow shape:** 5 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.ChoiceScreen -->
#### `main.ChoiceScreen`

**Kind:** class  
**Lines:** 683-700  
**Bases:** `ModalScreen[str | bool]`  
**Methods:** `__init__`, `compose`, `on_button_pressed`  
**Responsibility:** Implements the `ChoiceScreen` operation in this module.

<!-- symbol:keys_ng.tui.main:main.ChoiceScreen.__init__ -->
#### `main.ChoiceScreen.__init__`

**Kind:** function/method  
**Lines:** 689-690  
**Signature:** `def __init__(self, title: str, options) -> None`  
**Purpose:** Internal helper implementing `__init__`.

**Direct calls observed in the function body:** `__init__`, `super`.

**Object attributes written:** `self.options`, `self.title_text`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.ChoiceScreen.compose -->
#### `main.ChoiceScreen.compose`

**Kind:** function/method  
**Lines:** 691-697  
**Signature:** `def compose(self) -> ComposeResult`  
**Purpose:** Implements the `compose` operation in this module.

**Direct calls observed in the function body:** `Button`, `Horizontal`, `Select`, `Static`, `Vertical`, `_`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 2 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.ChoiceScreen.on_button_pressed -->
#### `main.ChoiceScreen.on_button_pressed`

**Kind:** function/method  
**Lines:** 698-700  
**Signature:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Purpose:** Implements the `on_button_pressed` operation in this module.

**Direct calls observed in the function body:** `self.dismiss`, `self.query_one`, `str`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.InboxScreen -->
#### `main.InboxScreen`

**Kind:** class  
**Lines:** 703-788  
**Bases:** `ModalScreen[None]`  
**Methods:** `__init__`, `compose`, `on_mount`, `action_close`, `_status`, `refresh_inbox`, `show_item`, `selected`, `on_select_changed`, `_finish_unsigned`, `_finish_delete`, `on_button_pressed`  
**Responsibility:** Implements the `InboxScreen` operation in this module.

<!-- symbol:keys_ng.tui.main:main.InboxScreen.__init__ -->
#### `main.InboxScreen.__init__`

**Kind:** function/method  
**Lines:** 711-712  
**Signature:** `def __init__(self) -> None`  
**Purpose:** Internal helper implementing `__init__`.

**Direct calls observed in the function body:** `__init__`, `super`.

**Object attributes written:** `self.items`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.InboxScreen.compose -->
#### `main.InboxScreen.compose`

**Kind:** function/method  
**Lines:** 713-724  
**Signature:** `def compose(self) -> ComposeResult`  
**Purpose:** Implements the `compose` operation in this module.

**Direct calls observed in the function body:** `Button`, `Horizontal`, `Select`, `Static`, `Vertical`, `_`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 2 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.InboxScreen.on_mount -->
#### `main.InboxScreen.on_mount`

**Kind:** function/method  
**Lines:** 725-725  
**Signature:** `def on_mount(self) -> None`  
**Purpose:** Implements the `on_mount` operation in this module.

**Direct calls observed in the function body:** `self.refresh_inbox`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.InboxScreen.action_close -->
#### `main.InboxScreen.action_close`

**Kind:** function/method  
**Lines:** 726-726  
**Signature:** `def action_close(self) -> None`  
**Purpose:** Implements the `action_close` operation in this module.

**Direct calls observed in the function body:** `self.dismiss`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.InboxScreen._status -->
#### `main.InboxScreen._status`

**Kind:** function/method  
**Lines:** 727-728  
**Signature:** `def _status(self, item) -> str`  
**Purpose:** Internal helper implementing `_status`.

**Direct calls observed in the function body:** `_`, `get`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.InboxScreen.refresh_inbox -->
#### `main.InboxScreen.refresh_inbox`

**Kind:** function/method  
**Lines:** 729-740  
**Signature:** `def refresh_inbox(self) -> None`  
**Purpose:** Implements the `refresh_inbox` operation in this module.

**Direct calls observed in the function body:** `_`, `enumerate`, `inspect_inbox`, `options.append`, `select.set_options`, `self._status`, `self.query_one`, `self.show_item`, `str`, `update`.

**Object attributes written:** `select.value`, `self.items`.

**Control-flow shape:** 1 conditional blocks, 1 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.InboxScreen.show_item -->
#### `main.InboxScreen.show_item`

**Kind:** function/method  
**Lines:** 741-746  
**Signature:** `def show_item(self, idx: int) -> None`  
**Purpose:** Implements the `show_item` operation in this module.

**Direct calls observed in the function body:** `_`, `self._status`, `self.query_one`, `update`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.InboxScreen.selected -->
#### `main.InboxScreen.selected`

**Kind:** function/method  
**Lines:** 747-750  
**Signature:** `def selected(self)`  
**Purpose:** Implements the `selected` operation in this module.

**Direct calls observed in the function body:** `_select_value_is_blank`, `int`, `len`, `self.query_one`, `str`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.InboxScreen.on_select_changed -->
#### `main.InboxScreen.on_select_changed`

**Kind:** function/method  
**Lines:** 751-752  
**Signature:** `def on_select_changed(self, event: Select.Changed) -> None`  
**Purpose:** Implements the `on_select_changed` operation in this module.

**Direct calls observed in the function body:** `_select_value_is_blank`, `int`, `self.show_item`, `str`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.InboxScreen._finish_unsigned -->
#### `main.InboxScreen._finish_unsigned`

**Kind:** function/method  
**Lines:** 753-758  
**Signature:** `def _finish_unsigned(self, confirmed: bool) -> None`  
**Purpose:** Internal helper implementing `_finish_unsigned`.

**Direct calls observed in the function body:** `_`, `import_inbox_item`, `self.query_one`, `self.refresh_inbox`, `self.selected`, `update`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.InboxScreen._finish_delete -->
#### `main.InboxScreen._finish_delete`

**Kind:** function/method  
**Lines:** 759-764  
**Signature:** `def _finish_delete(self, confirmed: bool) -> None`  
**Purpose:** Internal helper implementing `_finish_delete`.

**Direct calls observed in the function body:** `_`, `delete_inbox_item`, `self.query_one`, `self.refresh_inbox`, `self.selected`, `update`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.InboxScreen.on_button_pressed -->
#### `main.InboxScreen.on_button_pressed`

**Kind:** function/method  
**Lines:** 765-788  
**Signature:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Purpose:** Implements the `on_button_pressed` operation in this module.

**Direct calls observed in the function body:** `ConfirmScreen`, `_`, `add_trusted_signer`, `import_inbox_item`, `list`, `self.action_close`, `self.app.push_screen`, `self.query_one`, `self.refresh_inbox`, `self.selected`, `update`.

**Control-flow shape:** 10 conditional blocks, 1 loops, 3 try blocks, 0 context managers, 5 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.VaultSwitcherScreen -->
#### `main.VaultSwitcherScreen`

**Kind:** class  
**Lines:** 790-828  
**Bases:** `ModalScreen[tuple[str, str | None] | None]`  
**Methods:** `compose`, `action_cancel`, `on_button_pressed`  
**Responsibility:** Select, activate, or close one of the vaults already open in the TUI.

<!-- symbol:keys_ng.tui.main:main.VaultSwitcherScreen.compose -->
#### `main.VaultSwitcherScreen.compose`

**Kind:** function/method  
**Lines:** 800-813  
**Signature:** `def compose(self) -> ComposeResult`  
**Purpose:** Implements the `compose` operation in this module.

**Direct calls observed in the function body:** `Button`, `Horizontal`, `Select`, `Static`, `Vertical`, `_`, `options.append`, `sessions.opened`, `str`.

**Control-flow shape:** 0 conditional blocks, 1 loops, 0 try blocks, 2 context managers, 0 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.VaultSwitcherScreen.action_cancel -->
#### `main.VaultSwitcherScreen.action_cancel`

**Kind:** function/method  
**Lines:** 815-816  
**Signature:** `def action_cancel(self) -> None`  
**Purpose:** Implements the `action_cancel` operation in this module.

**Direct calls observed in the function body:** `self.dismiss`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.VaultSwitcherScreen.on_button_pressed -->
#### `main.VaultSwitcherScreen.on_button_pressed`

**Kind:** function/method  
**Lines:** 818-828  
**Signature:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Purpose:** Implements the `on_button_pressed` operation in this module.

**Direct calls observed in the function body:** `_select_value_is_blank`, `self.dismiss`, `self.query_one`, `str`.

**Control-flow shape:** 4 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp -->
#### `main.KeysApp`

**Kind:** class  
**Lines:** 830-1417  
**Bases:** `App`  
**Methods:** `__init__`, `compose`, `on_mount`, `rebuild_tree`, `_reset_selection`, `_refresh_after_mutation`, `on_input_changed`, `on_tree_node_selected`, `_status`, `_show_clipboard_banner`, `_hide_clipboard_banner`, `_update_command_hints`, `action_focus_search`, `action_reload_tree`, `action_import_keepassxc`, `action_export_vault`, `_finish_export_vault`, `_display_active_vault`, `_activate_opened_vault`, `action_open_vault`, `_finish_open_vault`, `action_recent_vault`, `_finish_recent_vault`, `action_switch_vault`, `_finish_switch_vault`, `action_close_vault`, `action_preferences`, `action_help`, `action_shortcut_help`, `_finish_help`, `action_inbox`, `action_trusted_signers`, `_copy`, `action_copy_url`, `action_copy_uuid`, `action_copy_username`, `action_copy_password`, `action_copy_notes`, `action_copy_totp`, `action_open_action`, `action_new_entry`, `_finish_new_entry`, `action_edit_selected`, `_finish_edit_entry`, `action_new_folder`, `_finish_new_folder`, `_finish_rename_folder`, `action_move_selected`, `_finish_move`, `action_delete_selected`, `_finish_delete`, `action_export_entry`, `_finish_export_entry`, `action_lock_vault`, `action_hard_lock_vault`, `action_unlock_vault`  
**Responsibility:** Top-level Textual application for one vault.

<!-- symbol:keys_ng.tui.main:main.KeysApp.__init__ -->
#### `main.KeysApp.__init__`

**Kind:** function/method  
**Lines:** 878-885  
**Signature:** `def __init__(self) -> None`  
**Purpose:** Internal helper implementing `__init__`.

**Direct calls observed in the function body:** `__init__`, `super`.

**Object attributes written:** `self._banner_timer`, `self._inbox_notice_shown`, `self.current_entry`, `self.current_folder_id`, `self.current_id`, `self.current_kind`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.compose -->
#### `main.KeysApp.compose`

**Kind:** function/method  
**Lines:** 887-897  
**Signature:** `def compose(self) -> ComposeResult`  
**Purpose:** Implements the `compose` operation in this module.

**Direct calls observed in the function body:** `Footer`, `Header`, `Horizontal`, `Input`, `Static`, `Tree`, `Vertical`, `_`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 2 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.on_mount -->
#### `main.KeysApp.on_mount`

**Kind:** function/method  
**Lines:** 899-907  
**Signature:** `def on_mount(self) -> None`  
**Purpose:** Implements the `on_mount` operation in this module.

**Direct calls observed in the function body:** `_`, `focus`, `format`, `len`, `pending_inbox_paths`, `self._status`, `self._update_command_hints`, `self.query_one`, `self.rebuild_tree`, `set_textual_terminal_title`.

**Object attributes written:** `self._inbox_notice_shown`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.rebuild_tree -->
#### `main.KeysApp.rebuild_tree`

**Kind:** function/method  
**Lines:** 909-941  
**Signature:** `def rebuild_tree(self, query: str='') -> None`  
**Purpose:** Implements the `rebuild_tree` operation in this module.

**Direct calls observed in the function body:** `_`, `folder_nodes.get`, `list`, `parent.add`, `parent.add_leaf`, `paths.get`, `remaining.remove`, `self.query_one`, `tree.clear`, `tree.root.add_leaf`, `tree.root.expand`, `tree.root.set_label`, `vault.folder_paths`, `vault.list_folders`, `vault.list_items`, `vault.search`.

**Control-flow shape:** 4 conditional blocks, 4 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp._reset_selection -->
#### `main.KeysApp._reset_selection`

**Kind:** function/method  
**Lines:** 943-949  
**Signature:** `def _reset_selection(self) -> None`  
**Purpose:** Internal helper implementing `_reset_selection`.

**Direct calls observed in the function body:** `_`, `self._update_command_hints`, `self.query_one`, `update`.

**Object attributes written:** `self.current_entry`, `self.current_folder_id`, `self.current_id`, `self.current_kind`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp._refresh_after_mutation -->
#### `main.KeysApp._refresh_after_mutation`

**Kind:** function/method  
**Lines:** 951-955  
**Signature:** `def _refresh_after_mutation(self, message: str) -> None`  
**Purpose:** Internal helper implementing `_refresh_after_mutation`.

**Direct calls observed in the function body:** `focus`, `self._reset_selection`, `self._status`, `self.query_one`, `self.rebuild_tree`, `value.strip`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.on_input_changed -->
#### `main.KeysApp.on_input_changed`

**Kind:** function/method  
**Lines:** 957-967  
**Signature:** `def on_input_changed(self, event: Input.Changed) -> None`  
**Purpose:** Implements the `on_input_changed` operation in this module.

**Direct calls observed in the function body:** `event.value.strip`, `self._reset_selection`, `self.rebuild_tree`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.on_tree_node_selected -->
#### `main.KeysApp.on_tree_node_selected`

**Kind:** function/method  
**Lines:** 969-1011  
**Signature:** `def on_tree_node_selected(self, event: Tree.NodeSelected) -> None`  
**Purpose:** Implements the `on_tree_node_selected` operation in this module.

**Direct calls observed in the function body:** `_`, `join`, `self._status`, `self._update_command_hints`, `self.query_one`, `update`, `vault.folder_path`, `vault.get_entry`, `vault.get_folder`, `vault.resolved_username`.

**Object attributes written:** `self.current_entry`, `self.current_folder_id`, `self.current_id`, `self.current_kind`.

**Control-flow shape:** 4 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp._status -->
#### `main.KeysApp._status`

**Kind:** function/method  
**Lines:** 1013-1014  
**Signature:** `def _status(self, text: str) -> None`  
**Purpose:** Internal helper implementing `_status`.

**Direct calls observed in the function body:** `self.query_one`, `update`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp._show_clipboard_banner -->
#### `main.KeysApp._show_clipboard_banner`

**Kind:** function/method  
**Lines:** 1016-1033  
**Signature:** `def _show_clipboard_banner(self, text: str, level: str='success') -> None`  
**Purpose:** Internal helper implementing `_show_clipboard_banner`.

**Direct calls observed in the function body:** `banner.add_class`, `banner.remove_class`, `banner.update`, `self._banner_timer.stop`, `self.query_one`, `self.set_timer`.

**Object attributes written:** `banner.styles.background`, `banner.styles.color`, `self._banner_timer`.

**Control-flow shape:** 3 conditional blocks, 0 loops, 2 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp._hide_clipboard_banner -->
#### `main.KeysApp._hide_clipboard_banner`

**Kind:** function/method  
**Lines:** 1035-1037  
**Signature:** `def _hide_clipboard_banner(self) -> None`  
**Purpose:** Internal helper implementing `_hide_clipboard_banner`.

**Direct calls observed in the function body:** `banner.remove_class`, `self.query_one`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp._update_command_hints -->
#### `main.KeysApp._update_command_hints`

**Kind:** function/method  
**Lines:** 1039-1047  
**Signature:** `def _update_command_hints(self) -> None`  
**Purpose:** Internal helper implementing `_update_command_hints`.

**Direct calls observed in the function body:** `_`, `self.query_one`, `update`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_focus_search -->
#### `main.KeysApp.action_focus_search`

**Kind:** function/method  
**Lines:** 1049-1050  
**Signature:** `def action_focus_search(self) -> None`  
**Purpose:** Implements the `action_focus_search` operation in this module.

**Direct calls observed in the function body:** `focus`, `self.query_one`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_reload_tree -->
#### `main.KeysApp.action_reload_tree`

**Kind:** function/method  
**Lines:** 1052-1056  
**Signature:** `def action_reload_tree(self) -> None`  
**Purpose:** Implements the `action_reload_tree` operation in this module.

**Direct calls observed in the function body:** `_`, `format`, `len`, `pending_inbox_paths`, `self._status`, `self.query_one`, `self.rebuild_tree`, `value.strip`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_import_keepassxc -->
#### `main.KeysApp.action_import_keepassxc`

**Kind:** function/method  
**Lines:** 1058-1061  
**Signature:** `def action_import_keepassxc(self) -> None`  
**Purpose:** Implements the `action_import_keepassxc` operation in this module.

**Direct calls observed in the function body:** `KeePassXCImportScreen`, `_`, `self._refresh_after_mutation`, `self._status`, `self.push_screen`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_export_vault -->
#### `main.KeysApp.action_export_vault`

**Kind:** function/method  
**Lines:** 1063-1065  
**Signature:** `def action_export_vault(self) -> None`  
**Purpose:** Implements the `action_export_vault` operation in this module.

**Direct calls observed in the function body:** `ExportVaultScreen`, `self.push_screen`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp._finish_export_vault -->
#### `main.KeysApp._finish_export_vault`

**Kind:** function/method  
**Lines:** 1067-1072  
**Signature:** `def _finish_export_vault(self, destination: str | None) -> None`  
**Purpose:** Internal helper implementing `_finish_export_vault`.

**Direct calls observed in the function body:** `_`, `export_vault_xml`, `format`, `self._status`, `write_export`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp._display_active_vault -->
#### `main.KeysApp._display_active_vault`

**Kind:** function/method  
**Lines:** 1074-1093  
**Signature:** `def _display_active_vault(self, message: str | None=None) -> None`  
**Purpose:** Refresh the main widgets after the active vault changes.

**Direct calls observed in the function body:** `_`, `focus`, `format`, `self._reset_selection`, `self._status`, `self._update_command_hints`, `self.query_one`, `self.rebuild_tree`, `tree.clear`, `tree.root.expand`, `tree.root.set_label`, `update`.

**Object attributes written:** `self.title`, `value`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp._activate_opened_vault -->
#### `main.KeysApp._activate_opened_vault`

**Kind:** function/method  
**Lines:** 1095-1101  
**Signature:** `def _activate_opened_vault(self, path: str) -> None`  
**Purpose:** Internal helper implementing `_activate_opened_vault`.

**Direct calls observed in the function body:** `_`, `format`, `self._display_active_vault`, `self._status`, `sessions.activate`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_open_vault -->
#### `main.KeysApp.action_open_vault`

**Kind:** function/method  
**Lines:** 1103-1104  
**Signature:** `def action_open_vault(self) -> None`  
**Purpose:** Implements the `action_open_vault` operation in this module.

**Direct calls observed in the function body:** `NameScreen`, `Path.home`, `_`, `self.push_screen`, `str`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp._finish_open_vault -->
#### `main.KeysApp._finish_open_vault`

**Kind:** function/method  
**Lines:** 1106-1123  
**Signature:** `def _finish_open_vault(self, path: str | None) -> None`  
**Purpose:** Internal helper implementing `_finish_open_vault`.

**Direct calls observed in the function body:** `Path`, `Vault`, `_`, `expanduser`, `format`, `resolve`, `self._display_active_vault`, `self._status`, `sessions.activate`, `sessions.add`, `sessions.contains`, `settings.remember_vault`, `settings.save`, `str`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 2 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_recent_vault -->
#### `main.KeysApp.action_recent_vault`

**Kind:** function/method  
**Lines:** 1125-1130  
**Signature:** `def action_recent_vault(self) -> None`  
**Purpose:** Implements the `action_recent_vault` operation in this module.

**Direct calls observed in the function body:** `ChoiceScreen`, `Path`, `_`, `exists`, `resolve`, `self._status`, `self.push_screen`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp._finish_recent_vault -->
#### `main.KeysApp._finish_recent_vault`

**Kind:** function/method  
**Lines:** 1132-1134  
**Signature:** `def _finish_recent_vault(self, path) -> None`  
**Purpose:** Internal helper implementing `_finish_recent_vault`.

**Direct calls observed in the function body:** `self._finish_open_vault`, `str`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_switch_vault -->
#### `main.KeysApp.action_switch_vault`

**Kind:** function/method  
**Lines:** 1136-1140  
**Signature:** `def action_switch_vault(self) -> None`  
**Purpose:** Implements the `action_switch_vault` operation in this module.

**Direct calls observed in the function body:** `VaultSwitcherScreen`, `_`, `len`, `self._status`, `self.push_screen`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp._finish_switch_vault -->
#### `main.KeysApp._finish_switch_vault`

**Kind:** function/method  
**Lines:** 1142-1165  
**Signature:** `def _finish_switch_vault(self, result: tuple[str, str | None] | None) -> None`  
**Purpose:** Internal helper implementing `_finish_switch_vault`.

**Direct calls observed in the function body:** `Path`, `_`, `expanduser`, `format`, `resolve`, `self._activate_opened_vault`, `self._display_active_vault`, `self._status`, `self.exit`, `sessions.close`, `str`.

**Control-flow shape:** 6 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 4 explicit returns.

**Security-relevant effect categories:** filesystem.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_close_vault -->
#### `main.KeysApp.action_close_vault`

**Kind:** function/method  
**Lines:** 1167-1177  
**Signature:** `def action_close_vault(self) -> None`  
**Purpose:** Implements the `action_close_vault` operation in this module.

**Direct calls observed in the function body:** `_`, `format`, `self._display_active_vault`, `self._status`, `self.exit`, `sessions.close`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_preferences -->
#### `main.KeysApp.action_preferences`

**Kind:** function/method  
**Lines:** 1179-1180  
**Signature:** `def action_preferences(self) -> None`  
**Purpose:** Implements the `action_preferences` operation in this module.

**Direct calls observed in the function body:** `PreferencesScreen`, `_`, `self._status`, `self.push_screen`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_help -->
#### `main.KeysApp.action_help`

**Kind:** function/method  
**Lines:** 1182-1183  
**Signature:** `def action_help(self) -> None`  
**Purpose:** Implements the `action_help` operation in this module.

**Direct calls observed in the function body:** `ChoiceScreen`, `_`, `self.push_screen`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_shortcut_help -->
#### `main.KeysApp.action_shortcut_help`

**Kind:** function/method  
**Lines:** 1185-1186  
**Signature:** `def action_shortcut_help(self) -> None`  
**Purpose:** Implements the `action_shortcut_help` operation in this module.

**Direct calls observed in the function body:** `HelpScreen`, `self.push_screen`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp._finish_help -->
#### `main.KeysApp._finish_help`

**Kind:** function/method  
**Lines:** 1188-1190  
**Signature:** `def _finish_help(self, resource) -> None`  
**Purpose:** Internal helper implementing `_finish_help`.

**Direct calls observed in the function body:** `HelpScreen`, `self.push_screen`, `str`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_inbox -->
#### `main.KeysApp.action_inbox`

**Kind:** function/method  
**Lines:** 1192-1195  
**Signature:** `def action_inbox(self) -> None`  
**Purpose:** Implements the `action_inbox` operation in this module.

**Direct calls observed in the function body:** `InboxScreen`, `_`, `self._status`, `self.action_reload_tree`, `self.push_screen`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_trusted_signers -->
#### `main.KeysApp.action_trusted_signers`

**Kind:** function/method  
**Lines:** 1197-1198  
**Signature:** `def action_trusted_signers(self) -> None`  
**Purpose:** Implements the `action_trusted_signers` operation in this module.

**Direct calls observed in the function body:** `TrustedSignersScreen`, `self.push_screen`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp._copy -->
#### `main.KeysApp._copy`

**Kind:** function/method  
**Lines:** 1200-1213  
**Signature:** `def _copy(self, value: str, timeout: int, success: str) -> None`  
**Purpose:** Internal helper implementing `_copy`.

**Direct calls observed in the function body:** `_`, `copy_secret_cli`, `self._show_clipboard_banner`, `self.copy_to_clipboard`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 2 try blocks, 0 context managers, 2 explicit returns.

**Security-relevant effect categories:** clipboard.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_copy_url -->
#### `main.KeysApp.action_copy_url`

**Kind:** function/method  
**Lines:** 1215-1220  
**Signature:** `def action_copy_url(self) -> None`  
**Purpose:** Implements the `action_copy_url` operation in this module.

**Direct calls observed in the function body:** `_`, `next`, `self._copy`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_copy_uuid -->
#### `main.KeysApp.action_copy_uuid`

**Kind:** function/method  
**Lines:** 1222-1224  
**Signature:** `def action_copy_uuid(self) -> None`  
**Purpose:** Implements the `action_copy_uuid` operation in this module.

**Direct calls observed in the function body:** `_`, `self._copy`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_copy_username -->
#### `main.KeysApp.action_copy_username`

**Kind:** function/method  
**Lines:** 1226-1233  
**Signature:** `def action_copy_username(self) -> None`  
**Purpose:** Implements the `action_copy_username` operation in this module.

**Direct calls observed in the function body:** `_`, `self._copy`, `self._status`, `vault.resolved_username`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_copy_password -->
#### `main.KeysApp.action_copy_password`

**Kind:** function/method  
**Lines:** 1235-1242  
**Signature:** `def action_copy_password(self) -> None`  
**Purpose:** Implements the `action_copy_password` operation in this module.

**Direct calls observed in the function body:** `_`, `self._copy`, `self._status`, `vault.resolved_password`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_copy_notes -->
#### `main.KeysApp.action_copy_notes`

**Kind:** function/method  
**Lines:** 1244-1246  
**Signature:** `def action_copy_notes(self) -> None`  
**Purpose:** Implements the `action_copy_notes` operation in this module.

**Direct calls observed in the function body:** `_`, `self._copy`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_copy_totp -->
#### `main.KeysApp.action_copy_totp`

**Kind:** function/method  
**Lines:** 1248-1251  
**Signature:** `def action_copy_totp(self) -> None`  
**Purpose:** Implements the `action_copy_totp` operation in this module.

**Direct calls observed in the function body:** `_`, `generate_totp`, `self._copy`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_open_action -->
#### `main.KeysApp.action_open_action`

**Kind:** function/method  
**Lines:** 1253-1259  
**Signature:** `def action_open_action(self) -> None`  
**Purpose:** Implements the `action_open_action` operation in this module.

**Direct calls observed in the function body:** `_`, `launch_action`, `self._status`, `vault.resolved_action`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_new_entry -->
#### `main.KeysApp.action_new_entry`

**Kind:** function/method  
**Lines:** 1261-1266  
**Signature:** `def action_new_entry(self) -> None`  
**Purpose:** Implements the `action_new_entry` operation in this module.

**Direct calls observed in the function body:** `EntryDraft`, `EntryEditorScreen`, `_`, `self._status`, `self.push_screen`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp._finish_new_entry -->
#### `main.KeysApp._finish_new_entry`

**Kind:** function/method  
**Lines:** 1268-1276  
**Signature:** `def _finish_new_entry(self, draft: EntryDraft | None) -> None`  
**Purpose:** Internal helper implementing `_finish_new_entry`.

**Direct calls observed in the function body:** `_`, `build_entry_from_draft`, `self._refresh_after_mutation`, `self._status`, `vault.save_entry`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_edit_selected -->
#### `main.KeysApp.action_edit_selected`

**Kind:** function/method  
**Lines:** 1278-1290  
**Signature:** `def action_edit_selected(self) -> None`  
**Purpose:** Implements the `action_edit_selected` operation in this module.

**Direct calls observed in the function body:** `EntryDraft.from_entry`, `EntryEditorScreen`, `NameScreen`, `_`, `self._finish_edit_entry`, `self._status`, `self.push_screen`, `vault.get_folder`.

**Control-flow shape:** 3 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp._finish_edit_entry -->
#### `main.KeysApp._finish_edit_entry`

**Kind:** function/method  
**Lines:** 1292-1303  
**Signature:** `def _finish_edit_entry(self, entry_id: str, draft: EntryDraft | None) -> None`  
**Purpose:** Internal helper implementing `_finish_edit_entry`.

**Direct calls observed in the function body:** `_`, `build_entry_from_draft`, `self._refresh_after_mutation`, `self._status`, `vault.get_entry`, `vault.save_entry`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_new_folder -->
#### `main.KeysApp.action_new_folder`

**Kind:** function/method  
**Lines:** 1305-1309  
**Signature:** `def action_new_folder(self) -> None`  
**Purpose:** Implements the `action_new_folder` operation in this module.

**Direct calls observed in the function body:** `NameScreen`, `_`, `self._status`, `self.push_screen`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp._finish_new_folder -->
#### `main.KeysApp._finish_new_folder`

**Kind:** function/method  
**Lines:** 1311-1318  
**Signature:** `def _finish_new_folder(self, name: str | None) -> None`  
**Purpose:** Internal helper implementing `_finish_new_folder`.

**Direct calls observed in the function body:** `_`, `self._refresh_after_mutation`, `self._status`, `vault.create_folder`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp._finish_rename_folder -->
#### `main.KeysApp._finish_rename_folder`

**Kind:** function/method  
**Lines:** 1320-1328  
**Signature:** `def _finish_rename_folder(self, name: str | None) -> None`  
**Purpose:** Internal helper implementing `_finish_rename_folder`.

**Direct calls observed in the function body:** `_`, `self._refresh_after_mutation`, `self._status`, `vault.rename_folder`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_move_selected -->
#### `main.KeysApp.action_move_selected`

**Kind:** function/method  
**Lines:** 1330-1335  
**Signature:** `def action_move_selected(self) -> None`  
**Purpose:** Implements the `action_move_selected` operation in this module.

**Direct calls observed in the function body:** `MoveScreen`, `_`, `self.push_screen`, `vault.get_folder`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp._finish_move -->
#### `main.KeysApp._finish_move`

**Kind:** function/method  
**Lines:** 1337-1349  
**Signature:** `def _finish_move(self, destination: str | None | bool) -> None`  
**Purpose:** Internal helper implementing `_finish_move`.

**Direct calls observed in the function body:** `_`, `self._refresh_after_mutation`, `self._status`, `vault.move_entry`, `vault.move_folder`.

**Control-flow shape:** 2 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_delete_selected -->
#### `main.KeysApp.action_delete_selected`

**Kind:** function/method  
**Lines:** 1351-1355  
**Signature:** `def action_delete_selected(self) -> None`  
**Purpose:** Implements the `action_delete_selected` operation in this module.

**Direct calls observed in the function body:** `ConfirmScreen`, `_`, `self.push_screen`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp._finish_delete -->
#### `main.KeysApp._finish_delete`

**Kind:** function/method  
**Lines:** 1357-1371  
**Signature:** `def _finish_delete(self, confirmed: bool) -> None`  
**Purpose:** Internal helper implementing `_finish_delete`.

**Direct calls observed in the function body:** `_`, `self._refresh_after_mutation`, `self._status`, `vault.delete_entry`, `vault.delete_folder`.

**Control-flow shape:** 3 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 2 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_export_entry -->
#### `main.KeysApp.action_export_entry`

**Kind:** function/method  
**Lines:** 1373-1383  
**Signature:** `def action_export_entry(self) -> None`  
**Purpose:** Implements the `action_export_entry` operation in this module.

**Direct calls observed in the function body:** `ConfirmScreen`, `_`, `self._finish_export_entry`, `self.push_screen`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp._finish_export_entry -->
#### `main.KeysApp._finish_export_entry`

**Kind:** function/method  
**Lines:** 1385-1395  
**Signature:** `def _finish_export_entry(self, confirmed: bool, entry_id: str) -> None`  
**Purpose:** Internal helper implementing `_finish_export_entry`.

**Direct calls observed in the function body:** `Path.cwd`, `_`, `ch.isalnum`, `export_entry_xml`, `format`, `join`, `self._status`, `strip`, `vault.get_entry`, `write_export`.

**Control-flow shape:** 1 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 1 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_lock_vault -->
#### `main.KeysApp.action_lock_vault`

**Kind:** function/method  
**Lines:** 1397-1401  
**Signature:** `def action_lock_vault(self) -> None`  
**Purpose:** Implements the `action_lock_vault` operation in this module.

**Direct calls observed in the function body:** `_`, `self._reset_selection`, `self._status`, `self.query_one`, `update`, `vault.lock`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_hard_lock_vault -->
#### `main.KeysApp.action_hard_lock_vault`

**Kind:** function/method  
**Lines:** 1403-1408  
**Signature:** `def action_hard_lock_vault(self) -> None`  
**Purpose:** Implements the `action_hard_lock_vault` operation in this module.

**Direct calls observed in the function body:** `_`, `self._reset_selection`, `self._status`, `self.query_one`, `sessions.lock_all`, `update`, `vault.crypto.hard_lock`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 0 try blocks, 0 context managers, 0 explicit returns.

**Security-relevant effect categories:** cryptography/key-agent.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_unlock_vault -->
#### `main.KeysApp.action_unlock_vault`

**Kind:** function/method  
**Lines:** 1410-1417  
**Signature:** `def action_unlock_vault(self) -> None`  
**Purpose:** Implements the `action_unlock_vault` operation in this module.

**Direct calls observed in the function body:** `_`, `focus`, `self._status`, `self.query_one`, `self.rebuild_tree`, `value.strip`, `vault.unlock`.

**Control-flow shape:** 0 conditional blocks, 0 loops, 1 try blocks, 0 context managers, 0 explicit returns.

**Reviewer note:** Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative.

## Coverage guarantee

This edition documents **535** class/function symbols discovered by AST traversal. `tests/test_code_review_manual_coverage.py` independently traverses the release source and requires one marker for every symbol in both language editions.

Generated fields such as direct calls and control-flow counts are descriptive static-analysis aids; they do not prove security. The reviewer must inspect the referenced source and the separate threat model/security review.
\n\n<!-- symbol:keys_ng.services.standalone_export:standalone_recipient_keys -->\n<!-- symbol:keys_ng.services.standalone_export:standalone_signing_keys -->\n<!-- symbol:keys_ng.services.standalone_export:import_standalone_public_key -->\n<!-- symbol:keys_ng.services.standalone_export:prepare_standalone_entry -->\n<!-- symbol:keys_ng.services.standalone_export:export_standalone_entry -->\n<!-- symbol:keys_ng.gui.main:StandaloneExportDialog -->\n<!-- symbol:keys_ng.gui.main:StandaloneExportDialog.__init__ -->\n<!-- symbol:keys_ng.gui.main:StandaloneExportDialog._refresh_keys -->\n<!-- symbol:keys_ng.gui.main:StandaloneExportDialog.import_public_key -->\n<!-- symbol:keys_ng.gui.main:StandaloneExportDialog.browse_output -->\n<!-- symbol:keys_ng.gui.main:StandaloneExportDialog.perform_export -->\n<!-- symbol:keys_ng.gui.main:VaultPane.export_standalone_clicked -->\n<!-- symbol:keys_ng.tui.main:StandaloneExportScreen -->\n<!-- symbol:keys_ng.tui.main:StandaloneExportScreen.__init__ -->\n<!-- symbol:keys_ng.tui.main:StandaloneExportScreen.compose -->\n<!-- symbol:keys_ng.tui.main:StandaloneExportScreen.on_mount -->\n<!-- symbol:keys_ng.tui.main:StandaloneExportScreen._refresh_keys -->\n<!-- symbol:keys_ng.tui.main:StandaloneExportScreen.on_checkbox_changed -->\n<!-- symbol:keys_ng.tui.main:StandaloneExportScreen._import_public_key -->\n<!-- symbol:keys_ng.tui.main:StandaloneExportScreen._perform_export -->\n<!-- symbol:keys_ng.tui.main:StandaloneExportScreen.on_button_pressed -->\n<!-- symbol:keys_ng.tui.main:StandaloneExportScreen.action_cancel -->\n<!-- symbol:keys_ng.tui.main:KeysApp.action_export_standalone -->\n<!-- symbol:keys_ng.tui.main:KeysApp._finish_export_standalone -->\n

<!-- symbol:keys_ng.gui.main:main.StandaloneExportDialog -->
<!-- symbol:keys_ng.gui.main:main.StandaloneExportDialog.__init__ -->
<!-- symbol:keys_ng.gui.main:main.StandaloneExportDialog._refresh_keys -->
<!-- symbol:keys_ng.gui.main:main.StandaloneExportDialog.import_public_key -->
<!-- symbol:keys_ng.gui.main:main.StandaloneExportDialog.browse_output -->
<!-- symbol:keys_ng.gui.main:main.StandaloneExportDialog.perform_export -->
<!-- symbol:keys_ng.gui.main:main.VaultPane.export_standalone_clicked -->
<!-- symbol:keys_ng.tui.main:main.StandaloneExportScreen -->
<!-- symbol:keys_ng.tui.main:main.StandaloneExportScreen.__init__ -->
<!-- symbol:keys_ng.tui.main:main.StandaloneExportScreen.compose -->
<!-- symbol:keys_ng.tui.main:main.StandaloneExportScreen.on_mount -->
<!-- symbol:keys_ng.tui.main:main.StandaloneExportScreen._refresh_keys -->
<!-- symbol:keys_ng.tui.main:main.StandaloneExportScreen.on_checkbox_changed -->
<!-- symbol:keys_ng.tui.main:main.StandaloneExportScreen._import_public_key -->
<!-- symbol:keys_ng.tui.main:main.StandaloneExportScreen._perform_export -->
<!-- symbol:keys_ng.tui.main:main.StandaloneExportScreen.on_button_pressed -->
<!-- symbol:keys_ng.tui.main:main.StandaloneExportScreen.action_cancel -->
<!-- symbol:keys_ng.tui.main:main.KeysApp.action_export_standalone -->
<!-- symbol:keys_ng.tui.main:main.KeysApp._finish_export_standalone -->
